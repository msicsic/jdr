"""A5 : contrat de reprise, refus bornés, sauvegarde et rendu réel après recharge."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.comprehension import invariants_reprise, verifier_reprise
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


def revue(conforme=True, perimetre="sens", ecarts=(), motif=""):
    return dict(conforme=conforme, motif=motif, perimetre=perimetre, ecarts_types=list(ecarts))


def son(methode):
    return sequence(etape("emettre_son", "joueur", methode=methode))


class RepriseFideleTests(unittest.TestCase):
    def jouer(self, m, saisie, propositions, revues):
        propositions, revues = iter(propositions), iter(revues)
        appels, retours = [], []
        mj = MJ(connexion="chatgpt")
        def appel(instructions, dossier, intention, fonction, contrat):
            appels.append((fonction, copy.deepcopy(dossier)))
            if fonction == "auditer_action":
                return next(revues)
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
                verifier(r, plan)
                verifier(revue(False, "nuance_cosmetique", motif="émotion absente"), plan)
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
            verifier(revue(True, "contrat_type", [{"champ": "etapes.0.methode", "demande": "cri"}]), plan)
        self.assertEqual(refus.exception.champs_corrigeables, ("etapes.0.methode",))
        self.assertIn("ecarts_types", schema(plan)["required"])
        original = son("sifflement")
        with self.assertRaises(ErreurMonde) as refus:
            verifier_reprise(son("cri"), invariants_reprise(original, ErreurMonde("Une autre clause manque.")))
        self.assertIn("etapes.0.methode", refus.exception.attendu)
        # Un booléen mal formé ne devient pas valide par son périmètre.
        from donjon.couverture_action import RapportInvalide
        with self.assertRaises(RapportInvalide):
            verifier({**revue(False, "nuance_cosmetique"), "conforme": "non"}, plan)


if __name__ == "__main__":
    unittest.main()
