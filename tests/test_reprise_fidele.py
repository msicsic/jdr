"""A5 : contrat de reprise, refus bornés, sauvegarde et rendu réel après recharge."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.comprehension import invariants_reprise, verifier_reprise, champs_types_revue
from donjon.couverture_action import verifier, schema
from donjon.improvisation import effet, issue, proposition as improviser
from donjon.mj import MJ
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from tests.test_comprehension import PontScript
from tests.test_paroles import relais
from tests.revue_support import porter, rapport as rapport_complet


def revue(conforme=True, perimetre="sens", ecarts=(), motif=""):
    return dict(conforme=conforme, motif=motif, perimetre=perimetre, ecarts_types=list(ecarts))


def son(methode):
    return sequence(etape("emettre_son", "joueur", methode=methode))


class RepriseFideleTests(unittest.TestCase):
    def lots(self):
        from tests.test_matiere import relais_avec_planches, planches, qualifier
        from tests.test_piece_de_lot import auberge
        m, _, _ = qualifier(relais_avec_planches(), "planches", planches())
        autre = auberge()
        # Même portée manuelle que dans le cas du Relais, sans déplacement à compiler.
        from tests.test_tensions import placer
        placer(autre, "fagots_etable", "etable", (5, 2))
        return ((m, "planches", "je prends discrètement une planche du tas"),
                (autre, "fagots_etable", "je prends discrètement une bûche de chauffage de la réserve"))

    def test_quantite_contestee_libere_operation_seule_et_preleve_une_piece(self):
        from donjon.rendu import decrire
        for m, lot, saisie in self.lots():
            with self.subTest(lot=lot):
                # La possession reste régie par le moteur ; le geste discret et sa
                # cible restent identiques lors de la correction de quantité.
                nombre = m.objets[lot]["physique"]["pieces"]
                charges = m.objets[lot]["charges"]
                lieu = m.objets[lot]["lieu"]
                mauvais = sequence(etape("deplacer", lot, "joueur", methode="discret"))
                bon = sequence(etape("prelever", lot, "joueur", methode="discret"))
                substitution = copy.deepcopy(bon)
                substitution["etapes"][0]["methode"] = "simple"
                r = revue(False, "contrat_type", [{"champ": "etapes.0.operation", "demande": "prelever"}],
                          "Une seule pièce est demandée, pas le lot entier.")
                charge, retours, appels = self.jouer(m, saisie, [mauvais, substitution, bon], [r, revue()])
                self.assertEqual(retours[0]["champs_corrigeables"], ["etapes.0.operation"])
                conserves = retours[0]["parametres_a_conserver"]
                self.assertNotIn("etapes.0.operation", conserves)
                self.assertEqual(conserves["etapes.0.cible"], lot)
                self.assertEqual(conserves["etapes.0.destination"], "joueur")
                self.assertEqual(conserves["etapes.0.methode"], "discret")
                self.assertIn("proposition.etapes.0.methode", retours[1]["attendu"])
                self.assertEqual(charge.objets[lot]["lieu"], lieu)
                self.assertEqual(charge.objets[lot]["physique"]["pieces"], nombre - 1)
                self.assertEqual(charge.objets[lot]["charges"], charges - 1)
                piece = charge.objets[lot + "_1"]
                self.assertEqual((piece["lieu"], piece["physique"]["pieces"], piece["charges"]), ("joueur", 1, 1))
                self.assertAlmostEqual(charge.objets[lot]["masse"] + piece["masse"], m.objets[lot]["masse"], places=3)
                compris = charge.data["conversation"][-1]["compris"]
                self.assertIn("Prélever", compris)
                self.assertIn(piece["nom"], compris)
                self.assertIn(f"reste du lot après réussite : {nombre - 1}", compris)
                self.assertIn(piece["nom"], fiche(charge))
                self.assertIn(str(nombre - 1), decrire(charge, lot, detail=True))
                revues = [d for f, d in appels if f == "auditer_action"]
                self.assertEqual(len(revues), 2)
                for d, op, q in zip(revues, ("deplacer", "prelever"), (nombre, 1)):
                    sens = d["plan"]["etapes"][0]["sens_propose"]
                    self.assertEqual(sens["quantite_transfert"]["pieces_transferees"], q)
                    self.assertEqual(sens["operation"], op)

    def test_lot_entier_demande_reste_entier_apres_recharge(self):
        for m, lot, _ in self.lots():
            with self.subTest(lot=lot):
                nombre = m.objets[lot]["physique"]["pieces"]
                charge, retours, _ = self.jouer(m, "je prends discrètement la totalité de " + m.objets[lot]["nom"],
                    [sequence(etape("deplacer", lot, "joueur", methode="discret"))], [revue()])
                self.assertFalse(retours)
                self.assertEqual(charge.objets[lot]["lieu"], "joueur")
                self.assertEqual(charge.objets[lot]["physique"]["pieces"], nombre)
                self.assertNotIn(lot + "_1", charge.objets)
                self.assertIn(charge.objets[lot]["nom"], fiche(charge))

    def test_plusieurs_pieces_gardent_les_quantites_de_chaque_etape(self):
        from tests.test_piece_de_lot import auberge
        m = auberge()
        lot = "fagots_etable"
        from tests.test_tensions import placer
        placer(m, lot, "etable", (5, 2))
        p = sequence(*(etape("prelever", lot, "joueur", methode="discret") for _ in range(2)))
        charge, retours, appels = self.jouer(m, "je prends discrètement deux bûches de la réserve", [p], [revue()])
        self.assertFalse(retours)
        self.assertEqual(charge.objets[lot]["physique"]["pieces"], 1)
        for i in (1, 2):
            self.assertEqual(charge.objets[f"{lot}_{i}"]["lieu"], "joueur")
            self.assertEqual(charge.objets[f"{lot}_{i}"]["charges"], 1)
        dossier = next(d for f, d in appels if f == "auditer_action")
        self.assertEqual([e["sens_propose"]["quantite_transfert"]["pieces_restantes"]
                          for e in dossier["plan"]["etapes"]], [2, 1])
        self.assertIn("reste du lot après réussite : 2", charge.data["conversation"][-1]["compris"])
        self.assertIn("reste du lot après réussite : 1", charge.data["conversation"][-1]["compris"])

    def test_derniere_piece_refusee_libere_seulement_operation_de_cette_etape(self):
        m, lot, _ = self.lots()[0]
        mauvais = sequence(*(etape("prelever", lot, "joueur", methode="discret") for _ in range(2)))
        bon = copy.deepcopy(mauvais)
        bon["etapes"][1]["operation"] = "deplacer"
        charge, retours, _ = self.jouer(m, "je prends discrètement les deux pièces du tas", [mauvais, bon], [revue()])
        self.assertEqual(retours[0]["champs_corrigeables"], ["etapes.1.operation"])
        self.assertEqual(retours[0]["parametres_a_conserver"]["etapes.0.operation"], "prelever")
        self.assertEqual(retours[0]["parametres_a_conserver"]["etapes.1.methode"], "discret")
        self.assertIn("physique.pieces=1", retours[0]["attendu"])
        for id in (lot, lot + "_1"):
            self.assertEqual((charge.objets[id]["lieu"], charge.objets[id]["physique"]["pieces"],
                              charge.objets[id]["charges"]), ("joueur", 1, 1))
            self.assertIn(charge.objets[id]["nom"], fiche(charge))

    def jouer(self, m, saisie, propositions, revues):
        propositions, revues = iter(propositions), iter(revues)
        appels, retours = [], []
        mj = MJ(connexion="chatgpt")
        def appel(instructions, dossier, intention, fonction, contrat):
            appels.append((fonction, copy.deepcopy(dossier)))
            if fonction == "auditer_action":
                r = next(revues)
                return r if "champs_types" in r else porter(r, dossier)
            self.assertEqual(fonction, "repondre_au_joueur")
            if "retour_moteur" in dossier["faits"]:
                retours.append(copy.deepcopy(dossier["faits"]["retour_moteur"]))
            elif "retour_forme" in dossier:
                retours.append(copy.deepcopy(dossier["retour_forme"]))
            return dict(mode="action", texte="", faits=[], proposition=next(propositions))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "copie.json"
            m.sauver(chemin)
            pont = PontScript(["mj " + saisie, "tenter", "quitter"], chemin)
            with patch.object(jeu, "MJ", return_value=mj), patch.object(mj, "_appeler_brut", side_effect=appel), \
                 patch("sys.stdout", io.StringIO()), patch.object(Monde, "d20", return_value=20):
                self.assertEqual(jeu.main(["--console", "--connexion", "chatgpt", "--save", str(chemin)], interface=pont), 0)
            charge = Monde.charger(chemin)
            copie = copy.deepcopy(charge.data)
            reprise = PontScript(["quitter"], chemin)
            with patch("sys.stdout", io.StringIO()):
                jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise)
            apres = Monde.charger(chemin)
            self.assertEqual(apres.data, copie)
            self.assertEqual((regarder(apres), fiche(apres), scene_percue(apres)),
                             (regarder(charge), fiche(charge), scene_percue(charge)))
            reponse = charge.data["conversation"][-1]["reponse"]
            self.assertIn(reponse, "\n".join(pont.historique))
            if charge.data["conversation"][-1].get("compris"):
                self.assertIn(reponse, "\n".join(reprise.historique))
        return charge, retours, appels

    def test_methode_comparee_au_plan_et_nuance_hors_verdict(self):
        for methode, saisie in (("sifflement", "je siffle un air joyeux"), ("cri", "je crie de colère")):
            with self.subTest(methode=methode):
                m = relais()
                p = son(methode)
                plan = Moteur(m).preparer(p)
                avant = copy.deepcopy(m.data)
                # Même un verdict faux ne peut invalider une égalité typée.
                r = revue(False, "contrat_type", [{"champ": "etapes.0.methode", "demande": methode}], "nuance absente")
                verifier(porter(r, {"champs_types": champs_types_revue(plan.proposition)}), plan)
                verifier(rapport_complet(plan, False, "émotion absente", "nuance_cosmetique"), plan)
                self.assertEqual(m.data, avant)
                charge, retours, appels = self.jouer(m, saisie, [p], [r])
                self.assertFalse(retours)
                self.assertEqual(len(charge.data["sons"]), 1)
                self.assertEqual(charge.data["sons"][0]["nature"], methode)
                self.assertIn("Siffler." if methode == "sifflement" else "Pousser un cri.",
                              charge.data["conversation"][-1]["compris"])

    def test_substitution_refusee_puis_reprise_du_candidat_non_admis(self):
        for methode, saisie in (("sifflement", "je siffle un air joyeux"), ("cri", "je crie de colère")):
            with self.subTest(methode=methode):
                p = son(methode)
                autre = improviser("Brouillon", issue("Brouillon", [effet("son", "joueur", texte="voix_melodique", valeur=1)]))
                charge, retours, appels = self.jouer(relais(), saisie, [p, autre, p],
                    [revue(False, motif="Une clause manque."), revue()])
                self.assertEqual(len(retours), 2)
                self.assertTrue(all(r["statut_candidat"] == "non_admis" and r["saisie_entiere"] == saisie for r in retours))
                self.assertEqual(retours[1]["parametres_a_conserver"]["etapes.0.methode"], methode)
                self.assertIn("proposition.action", retours[1]["attendu"])
                self.assertEqual(len(charge.data["sons"]), 1)
                self.assertEqual(charge.data["sons"][0]["nature"], methode)
                self.assertNotIn("Brouillon", charge.data["conversation"][-1]["reponse"])

    def test_refus_de_forme_libere_uniquement_le_champ_fautif(self):
        p = son("sifflement")
        p["etapes"][0]["outil"] = "couteau"
        charge, retours, _ = self.jouer(relais(), "je siffle", [p, son("sifflement")], [revue()])
        self.assertEqual(retours[0]["champs_corrigeables"], ["etapes.0.outil"])
        self.assertNotIn("etapes.0.outil", retours[0]["parametres_a_conserver"])
        self.assertEqual(retours[0]["parametres_a_conserver"]["etapes.0.methode"], "sifflement")
        self.assertEqual(len(charge.data["sons"]), 1)

    def test_cible_absente_ne_devient_pas_une_autre_reference(self):
        for cible in ("cle", "crochets"):
            with self.subTest(cible=cible):
                m = nouveau_monde()
                m.objets[cible]["lieu"] = "echoppe"
                autre = proposition("prendre", "couteau")
                charge, retours, _ = self.jouer(m, "je prends " + cible,
                    [proposition("prendre", cible), autre, proposition("prendre", cible)], [])
                self.assertEqual(retours[1]["parametres_a_conserver"]["cible"], cible)
                self.assertIn("proposition.cible", retours[1]["attendu"])
                self.assertEqual(charge.objets[cible]["lieu"], "echoppe")
                self.assertEqual(charge.objets["couteau"]["lieu"], m.objets["couteau"]["lieu"])
                self.assertFalse(charge.data["journal"])

    def test_refus_grammaire_ne_libere_pas_la_methode_voisine(self):
        p = son("sifflement")
        p["etapes"][0]["outil"] = "couteau"
        charge, retours, appels = self.jouer(relais(), "je siffle", [p, son("cri")], [])
        self.assertEqual(retours[0]["parametres_a_conserver"]["etapes.0.methode"], "sifflement")
        self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 2)
        self.assertFalse(charge.data.get("sons"))
        self.assertFalse(charge.data["journal"])

    def test_fausse_impossibilite_ne_fige_pas_une_action_absente(self):
        # L'avis initial n'a ni opération ni manière admise à préserver.
        p = proposition("impossible")
        charge, retours, _ = self.jouer(relais(), "je siffle", [p, son("sifflement")], [revue()])
        self.assertEqual(retours[0]["parametres_a_conserver"], {})
        self.assertEqual(len(charge.data["sons"]), 1)

    def test_formes_acoustiques_et_clauses_gelees_sans_lire_attendu(self):
        p = improviser("Texte sans autorité", issue("Récit", [effet("son", "joueur", texte="corps_rythmique", valeur=1)]))
        exc = ErreurMonde("Refus", "methode outil texte action : changer tout")
        invariant = invariants_reprise(p, exc)
        autre = copy.deepcopy(p)
        autre["reussite"]["effets"][0]["texte"] = "voix_melodique"
        with self.assertRaises(ErreurMonde) as refus:
            verifier_reprise(autre, invariant)
        self.assertIn("reussite.effets.0.texte", refus.exception.attendu)
        plan = Moteur(nouveau_monde()).preparer(son("sifflement"))
        with self.assertRaises(ErreurMonde) as refus:
            verifier(rapport_complet(plan, True, perimetre="contrat_type", ecarts=[{"champ": "etapes.0.methode", "demande": "cri"}]), plan)
        self.assertEqual(refus.exception.champs_corrigeables, ("etapes.0.methode",))
        self.assertIn("champs_types", schema(plan)["required"])
        original = son("sifflement")
        with self.assertRaises(ErreurMonde) as refus:
            verifier_reprise(son("cri"), invariants_reprise(original, ErreurMonde("Une autre clause manque.")))
        self.assertIn("etapes.0.methode", refus.exception.attendu)
        # Un booléen mal formé ne devient pas valide par son périmètre.
        from donjon.couverture_action import RapportInvalide
        with self.assertRaises(RapportInvalide):
            verifier({**rapport_complet(plan, False, perimetre="nuance_cosmetique"), "conforme": "non"}, plan)


if __name__ == "__main__":
    unittest.main()
