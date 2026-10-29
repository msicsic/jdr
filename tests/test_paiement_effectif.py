"""Couverture des opérations demandées : console, transaction et rendu rechargés."""
from donjon.emissions import joueur as emissions_joueur
import copy
import unittest

from donjon.biens import compte, livraisons_dues
from donjon.echanges import enqueter
from donjon.matiere import id_piece
from donjon.rendu import fiche
from donjon.spatial import porte_par
from tests.support import presentes
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_comptes_issue import audit
from tests.test_parts_achetees import antichambre_du_banc
from tests.test_propositions import scene
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger, vivre


def revue(*operations):
    # Un verdict favorable ne doit pas annuler l'analyse de la saisie.
    return {"contenu_conforme": True, "motif": "Les mots sont identiques.",
            "operations_demandees": list(operations)}


class PaiementEffectifTests(unittest.TestCase):
    def test_achat_reel_et_offre_autrement_formulee(self):
        bois = presentes(antichambre_du_banc(), "aubin")
        enqueter(bois, "joueur", "aubin", "bois")
        soupe = scene("aubin")
        soupe.objets["vivres"].update(nom="soupe", aliases=["soupe"], prix_part=2)
        for m, lot, prix, saisie, marche in [
            (bois, "planches", 3, "je paie Aubin trois pièces pour une de ses planches", False),
            (soupe, "vivres", 2, "je t'offre deux pièces pour une part de soupe", True),
            (bois, "planches", 3, "Aubin, je te paie trois pièces pour une planche", False),
            (soupe, "vivres", 2, '« Je t’offre deux pièces pour une part de soupe. »', True),
        ]:
            with self.subTest(saisie=saisie):
                m = recharger(copy.deepcopy(m))
                avant = m.joueur["or"]
                piece = id_piece(m, lot)
                faux = parole(saisie, ("propos", "", "", ""), personnage="aubin")
                faux["proposition"]["operations_demandees"].update(demande=True, proposition=True)
                bon = parole(saisie, ("demande", lot, "", str(prix)), personnage="aubin")
                if marche:
                    bon["proposition"]["contenu"] = [{"type": "proposition",
                        "demande": {"type": "part", "objet": lot},
                        "contrepartie": {"type": "pieces", "montant": prix}}]
                texte = "Entendu."
                # Une remise immédiate ou engagée dépend de la position réelle du bien.
                comptes = [compte("joueur", "aubin", montant=prix, etat="rendu"),
                           compte("aubin", "joueur", piece, 1,
                                  etat="rendu" if marche else "du")]
                r, sortie, appels = jouer(m, saisie, [faux, bon, dialogue(f"« {texte} »")],
                    [audit(texte, comptes, "aubin")],
                    revues=[revue("demande", "proposition"), revue("demande", "proposition")])
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
                self.assertEqual(r.joueur["or"], avant - prix)
                retours = [e["faits"]["retour_moteur"] for _, e in appels
                           if "retour_moteur" in e.get("faits", {})]
                self.assertIn("proposition.contenu", retours[0]["attendu"])
                self.assertIn("contrepartie", retours[0]["attendu"])
                self.assertNotIn(retours[0]["attendu"], sortie)
                self.assertEqual(len(emissions_joueur(r)), 1)
                self.assertIn(texte, sortie)
                self.assertIn(texte, str(r.data["conversation"]))
                r, _ = vivre(r, 3)
                r = recharger(r)
                self.assertTrue(porte_par(r, piece, "joueur"))
                self.assertEqual(r.objets[piece]["proprietaire"], "joueur")
                quantite = "portions" if lot == "vivres" else "charges"
                self.assertEqual(r.objets[lot][quantite], m.objets[lot][quantite] - 1)
                self.assertIn(r.objets[piece]["nom"], fiche(r))
                self.assertFalse(livraisons_dues(r))

    def test_offre_sans_montant_executable_ne_couvre_pas_l_achat(self):
        for valeur in ("trois", "0"):
            with self.subTest(valeur=valeur):
                m = scene("aubin")
                saisie = "je t'offre deux pièces pour une part de soupe"
                m.objets["vivres"].update(nom="soupe", aliases=["soupe"], prix_part=2)
                piece = id_piece(m, "vivres")
                texte = "Entendu."
                bon = parole(saisie, personnage="aubin")
                bon["proposition"]["contenu"] = [{"type": "proposition",
                    "demande": {"type": "part", "objet": "vivres"},
                    "contrepartie": {"type": "pieces", "montant": 2}}]
                r, sortie, _ = jouer(m, saisie, [
                    parole(saisie, ("demande", "vivres", "", valeur), personnage="aubin"),
                    bon,
                    dialogue(f"« {texte} »")], [audit(texte, [
                        compte("joueur", "aubin", montant=2, etat="rendu"),
                        compte("aubin", "joueur", piece, 1, etat="rendu")], "aubin")],
                    revues=[revue("proposition"), revue("proposition")])
                self.assertEqual(r.joueur["or"], m.joueur["or"] - 2)
                self.assertEqual(r.objets["vivres"]["portions"], m.objets["vivres"]["portions"] - 1)
                self.assertTrue(porte_par(r, piece, "joueur"))
                self.assertEqual(len(emissions_joueur(r)), 1)
                self.assertIn(texte, sortie)
                self.assertIn(r.objets[piece]["nom"], fiche(recharger(r)))

    def test_repli_litteral_ne_peut_pas_perdre_l_operation(self):
        m = presentes(antichambre_du_banc(), "aubin")
        avant = copy.deepcopy(m.data)
        saisie = '« Je te paie trois pièces pour une planche. »'
        faux = parole(saisie, ("propos", "", "", ""), personnage="aubin")
        faux["proposition"]["operations_demandees"]["proposition"] = True
        correction = parole(saisie, personnage="aubin")
        # L'omission déclarée empêche la correction de contourner la revue.
        r, sortie, appels = jouer(m, saisie, [faux, correction], [],
                                 revues=[revue("proposition"), revue(), revue()])
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
        self.assertEqual(r.joueur["or"], avant["joueur"]["or"])
        self.assertFalse(emissions_joueur(r))
        self.assertIn("Tu n'as encore rien dit", sortie)
        self.assertNotIn("Tu dis", sortie)

    def test_parole_ordinaire_et_autre_operation(self):
        m = presentes(antichambre_du_banc(), "aubin")
        r, sortie, _ = jouer(m, "Aubin, bonsoir", [
            parole("Bonsoir", ("propos", "", "", ""), personnage="aubin"),
            dialogue("Ta salutation est entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))], revues=[revue()])
        self.assertIn("Tu dis", sortie)
        self.assertEqual(r.joueur["or"], m.joueur["or"])
        self.assertTrue(emissions_joueur(r))
        # La même couverture protège aussi une réclamation, sans lexique de verbes.
        from tests.test_parole_corrections import banc
        m = banc("soir-appel")
        saisie = "Aubin, rends-moi les deux pièces dues."
        bon = "Entendu."
        faux = parole(saisie, personnage="aubin")
        faux["proposition"]["operations_demandees"]["reclamer"] = True
        r, sortie, _ = jouer(m, saisie, [faux,
            parole(saisie, ("reclamer", "", "", ""), personnage="aubin"), dialogue(f"« {bon} »")],
            [audit(bon, [compte("aubin", "joueur", montant=2, etat="rendu")], "aubin")],
            revues=[revue("reclamer"), revue("reclamer")])
        self.assertEqual(r.joueur["or"], m.joueur["or"] + 2)
        self.assertIn(bon, sortie)
        self.assertIn(bon, str(r.data["conversation"]))

    def test_revue_illisible_ne_valide_pas_une_parole_sans_operation(self):
        m = presentes(antichambre_du_banc(), "aubin")
        saisie = "Aubin, as-tu du bois ?"
        faux = parole(saisie, ("ressource", "bois", "", ""), personnage="aubin")
        r, sortie, appels = jouer(m, saisie, [faux, faux], [], revues=[{}] * 6)
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 6)
        self.assertEqual(r.joueur["or"], m.joueur["or"])
        self.assertFalse(emissions_joueur(recharger(r)))
        self.assertNotIn("Tu dis", sortie)
        self.assertIn("Tu n'as encore rien dit", sortie)
        self.assertNotIn("operations_demandees", sortie)
