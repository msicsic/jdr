"""Frontière entre marchés parlés et recherche autonome, jusque dans la console."""
import unittest
from unittest.mock import patch

from donjon import agendas
from donjon.echanges import devis_service
from donjon.esprits import lire, percevoir_tous
from donjon.paroles import OPERATIONS, operations_contenu
from donjon.spatial import installer, porte_par
from tests.support import regarder
from tests.test_paroles import jouer, reponse_pnj
from tests.test_propositions import scene


def situation(crypte):
    if crypte:
        from donjon.scenario_crypte import nouveau_monde
        m = nouveau_monde()
        installer(m)
        m.joueur.update(salle="echoppe", position=[1, 2], orientation="nord")
        objet = "crochets"
        m.objets[objet]["proprietaire"] = "marchand"
    else:
        m = scene()
        m.objets["marchand"].pop("profil")
        lire(m, "marchand")["pulsions"] = []
        lire(m, "marchand")["besoins"] = {k: v for k, v in lire(m, "marchand")["besoins"].items()
                                           if k in ("faim", "repos", "chaleur")}
        objet = "cloche"
        m.objets[objet].update(lieu="antichambre", proprietaire="marchand", position=[2, 3])
    regarder(m, "marchand", "joueur")
    if objet not in m.data["connus"]:
        m.data["connus"].append(objet)
    percevoir_tous(m)
    return m, objet


class PromesseSansProfilTests(unittest.TestCase):
    def test_gardes_des_entrees_du_planificateur(self):
        from donjon.planification import chercher, devis_pulsion
        m, objet = situation(True)
        for acteur in ("joueur", "marchand", "inexistant"):
            with self.subTest(acteur=acteur):
                with self.assertRaisesRegex(ValueError, "chercher.*sans profil.*" + acteur):
                    chercher(m, acteur, lambda v, e: True)
                with self.assertRaisesRegex(ValueError, "devis_pulsion.*sans profil.*" + acteur):
                    devis_pulsion(m, acteur, {"objet": objet, "remettre": "joueur"}, "marchand")

    def test_remise_du_joueur_et_du_pnj_sans_profil(self):
        from tests.test_propositions import parler
        from tests.test_tensions import recharger
        for crypte in (True, False):
            for porte in (True, False):
                with self.subTest(crypte=crypte, porte=porte):
                    m, objet = situation(crypte)
                    m.objets[objet]["lieu"] = "marchand"
                    offre = "couteau" if crypte else "cire"
                    m.objets[offre].update(lieu="joueur" if porte else m.joueur["salle"],
                                           proprietaire="joueur")
                    if offre not in m.data["connus"]:
                        m.data["connus"].append(offre)
                    percevoir_tous(m)
                    with patch("donjon.planification.chercher", side_effect=AssertionError("recherche interdite")), \
                         patch("donjon.planification.devis_pulsion", side_effect=AssertionError("recherche interdite")), \
                         patch.object(type(m), "d20", return_value=20):
                        m, rapport = parler(m, demande={"type": "objet", "objet": objet},
                                           contrepartie={"type": "objet", "objet": offre})
                    m = recharger(m)
                    self.assertEqual(porte_par(m, objet, "joueur"), porte)
                    self.assertEqual(porte_par(m, offre, "marchand"), porte)
                    self.assertEqual(agendas.en_cours(m, "joueur"), [])
                    self.assertIn("accepte" if porte else "pas", " ".join(rapport["faits"]))

    def test_console_proposition_sans_profil_recharge(self):
        for crypte in (True, False):
            with self.subTest(crypte=crypte):
                m, objet = situation(crypte)
                saisie = "Gorm, donne-moi cet objet sans contrepartie."
                contenu = [{"type": "proposition", "demande": {"type": "objet", "objet": objet},
                            "contrepartie": {"type": "rien"}}]
                codes = operations_contenu(contenu)
                reponse = {"mode": "parole_joueur", "texte": "", "faits": ["interlocuteurs"],
                           "proposition": {"personnage": "marchand", "replique": saisie,
                               "contenu": contenu, "operations_demandees": {t: t in codes for t in OPERATIONS}}}
                texte = "Je refuse cet échange."
                avant = m.objets[objet]["lieu"]
                m, sortie, _ = jouer(m, saisie, [reponse, reponse_pnj(texte)])
                self.assertEqual(m.objets[objet]["lieu"], avant)
                self.assertFalse(porte_par(m, objet, "joueur"))
                self.assertEqual(agendas.en_cours(m, "marchand"), [])
                self.assertIn(texte, sortie)
                self.assertTrue(any(texte in x["reponse"] for x in m.data["conversation"]))

    def test_devis_sans_profil_ne_lance_aucune_recherche(self):
        m, objet = situation(True)
        for acteur in ("joueur", "marchand"):
            with patch("donjon.planification.devis_pulsion", side_effect=AssertionError("recherche interdite")):
                self.assertIsNone(devis_service(m, acteur, {"objet": objet, "remettre": "joueur"}, "marchand"))

