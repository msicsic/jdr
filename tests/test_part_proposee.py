"""Une part proposée reste un bien ; console, livraison et rendu après recharge."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas
from donjon.biens import bourse, compte, livraisons_dues
from donjon.echanges import contre_offre, evaluer_proposition
from donjon.esprits import croire
from donjon.matiere import id_piece
from donjon.propositions import prestation
from donjon.rendu import fiche
from donjon.spatial import porte_par
from tests.support import presentes
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_comptes_issue import audit
from tests.test_parts_achetees import antichambre_du_banc
from tests.test_propositions import scene
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger, vivre


def marche(m, lot, prix=3, demande=None, texte="J'accepte cet échange.", comptes=()):
    saisie = ("je paie Aubin trois pièces pour une de ses planches" if lot == "planches" else
              "Aubin, je te propose trois pièces contre cette part.")
    p = parole(saisie, personnage="aubin")
    p["proposition"]["contenu"] = [{"type": "proposition",
        "demande": demande or {"type": "part", "objet": lot},
        "contrepartie": {"type": "pieces", "montant": prix}}]
    revue = audit(texte, comptes, "aubin") if comptes else rapport(ligne("parole", sources=["conversation_validee"],
        locuteur="aubin", citation=texte))
    return jouer(m, saisie, [p, dialogue(f"« {texte} »")], [revue])


class PartProposeeTests(unittest.TestCase):
    def test_planches_reelles_et_autre_ressource_portees_ou_a_portee(self):
        for lot in ("planches", "huile_test"):
            for porte in (True, False):
                with self.subTest(lot=lot, porte=porte):
                    m = presentes(antichambre_du_banc(), "aubin")
                    if lot != "planches":
                        o = copy.deepcopy(m.objets["planches"])
                        o.update(id=lot, nom="réserve d'huile", aliases=["huile"], charges=4)
                        o.pop("physique", None)
                        m.objets[lot] = o
                    if porte:
                        m.objets[lot]["lieu"] = "aubin"
                    m.data["connus"].append(lot)
                    m = recharger(m)
                    terme = {"type": "part", "objet": lot}
                    self.assertIsNone(prestation(m, "aubin", "joueur", terme))
                    avant = copy.deepcopy(m.data)
                    bilan = evaluer_proposition(m, "joueur", "aubin", terme, {"type": "pieces", "montant": 3})
                    self.assertIsNone(bilan["cause"])
                    self.assertEqual(m.data, avant)
                    piece = id_piece(m, lot)
                    or_avant, bourse_avant = m.joueur["or"], bourse(m, "aubin")
                    r, sortie, _ = marche(m, lot, comptes=[compte("joueur", "aubin", montant=3, etat="rendu"),
                        compte("aubin", "joueur", piece, 1, "rendu" if porte else "du")])
                    self.assertIn("J'accepte cet échange.", sortie)
                    self.assertNotIn("ne voit pas comment faire la tâche", sortie)
                    self.assertEqual((r.joueur["or"], bourse(r, "aubin")), (or_avant - 3, bourse_avant + 3))
                    self.assertEqual(r.objets[lot]["charges"], m.objets[lot]["charges"] - 1)
                    r, _ = vivre(r, 3)
                    r = recharger(r)
                    self.assertTrue(porte_par(r, piece, "joueur"))
                    self.assertEqual(r.objets[piece]["proprietaire"], "joueur")
                    self.assertEqual(r.objets[lot]["proprietaire"], "aubin")
                    self.assertFalse(livraisons_dues(r))
                    self.assertIn(r.objets[piece]["nom"], fiche(r))

    def test_reserve_gardee_refuse_sans_payer_et_contre_offre_partage_la_livraison(self):
        for lot in ("planches", "vivres"):
            base = presentes(antichambre_du_banc(), "aubin") if lot == "planches" else scene("aubin")
            base.data["connus"].append(lot)
            terme = {"type": "part", "objet": lot}
            self.assertIsNotNone(contre_offre(base, "joueur", "aubin", lot, "refus"))
            for raison in ("garde", "valeur"):
                with self.subTest(lot=lot, raison=raison):
                    m = recharger(copy.deepcopy(base))
                    if raison == "garde":
                        m.objets[lot]["charges" if lot == "planches" else "portions"] = 1
                    else:
                        m.objets[lot]["prix_part"] = 1000
                    bilan = evaluer_proposition(m, "joueur", "aubin", terme,
                        {"type": "pieces", "montant": 3})
                    self.assertEqual(bilan["cause"], "garde" if raison == "garde" else None)
                    if raison == "valeur":
                        self.assertGreater(bilan["P"], bilan["G"])
                    r, sortie, _ = marche(m, lot, texte="Je refuse cet échange.")
                    self.assertEqual(r.joueur["or"], m.joueur["or"])
                    self.assertIn("Je refuse cet échange.", sortie)
                    self.assertNotIn("ne voit pas comment faire la tâche", sortie)
                    self.assertFalse(porte_par(recharger(r), id_piece(m, lot), "joueur"))

    def test_soupe_a_servir_reste_tache_avec_devis_et_engagement(self):
        m = scene("aubin")
        m.objets["vivres"].update(nom="soupe", aliases=["soupe"])
        condition = {"objet": "vivres", "servir": "joueur"}
        terme = {"type": "tache", "condition": condition}
        self.assertEqual(prestation(m, "aubin", "joueur", terme), condition)
        # Le devis est réel ; seul son appel est observé.
        from donjon.echanges import _devis_proposition
        with patch("donjon.echanges._devis_proposition", wraps=_devis_proposition) as devis:
            r, sortie, _ = marche(m, "vivres", demande=terme,
                comptes=[compte("joueur", "aubin", montant=3, etat="rendu"),
                         compte("aubin", "joueur", "vivres", 1)])
        self.assertTrue(devis.called)
        self.assertTrue(agendas.en_cours(r, "aubin", condition=condition))
        self.assertIn("J'accepte cet échange.", sortie)
        self.assertIn("servir", str(livraisons_dues(r)) + fiche(recharger(r)))
        self.assertEqual(r.objets["vivres"]["portions"], m.objets["vivres"]["portions"])

    def test_part_ailleurs_devis_sur_piece_et_non_sur_lot(self):
        m = presentes(antichambre_du_banc(), "aubin")
        m.objets["planches"].update(lieu="echoppe", position=[4, 2], position_salle="echoppe")
        croire(m, "aubin", "planches", "lieu", "echoppe", "savoir", salle="echoppe", case=[4, 2])
        m.data["connus"].append("planches")
        terme = {"type": "part", "objet": "planches"}
        self.assertEqual(prestation(m, "aubin", "joueur", terme), {"objet": "planches", "remettre": "joueur"})
        from donjon.planification import devis_pulsion
        with patch("donjon.planification.devis_pulsion", wraps=devis_pulsion) as devis:
            r, sortie, _ = marche(m, "planches", comptes=[
                compte("joueur", "aubin", montant=3, etat="rendu"), compte("aubin", "joueur", "planches_1", 1)])
        self.assertTrue(any(a.args[2] == {"objet": "planches_1", "remettre": "joueur"} for a in devis.call_args_list))
        self.assertFalse(any(a.args[2] == {"objet": "planches", "remettre": "joueur"} for a in devis.call_args_list))
        self.assertIn("J'accepte cet échange.", sortie)
        self.assertTrue(livraisons_dues(recharger(r)))
        r, _ = vivre(r, 5)
        r = recharger(r)
        self.assertTrue(porte_par(r, "planches_1", "joueur"))
        self.assertIn(r.objets["planches_1"]["nom"], fiche(r))
