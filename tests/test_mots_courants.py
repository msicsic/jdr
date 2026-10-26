"""Les constructions techniques, et non les mots isolés, déclenchent le garde."""
import copy
import unittest
from donjon.narration import voix_auteur, unites_moteur
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_commune import scene
from tests.test_repli_et_appel import dialogue


class MotsCourantsTests(unittest.TestCase):
    def test_emplois_ordinaires(self):
        for texte in (
            "Les planches ne t'ont pas encore été données.",
            "Les faits de ton compagnon parlent pour lui.",
            "Le moteur du moulin tourne.", "Tu imagines un scénario de fuite.",
            "La lettre est attestée par le sceau.", "Le prix n'est pas établi.",
            "Tu regardes les cases du hameau.", "Tu lis ses coordonnées bancaires.",
            "Son refus de ta proposition tient toujours.",
        ):
            with self.subTest(texte=texte):
                self.assertFalse(voix_auteur(texte))

    def test_admission_persiste_dans_la_vraie_boucle(self):
        for texte in ("Les planches ne t'ont pas encore été données.",
                      "Les faits de ton compagnon parlent pour lui."):
            with self.subTest(texte=texte):
                m = scene()
                avant = copy.deepcopy(m.data)
                r, sortie, appels = jouer(m, "que vois-tu ?", [dialogue(texte)],
                                          [rapport(ligne("neutre"))])
                self.assertIn(texte, sortie)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], texte)
                self.assertEqual(r.objets, avant["objets"])
                self.assertEqual(r.joueur, avant["joueur"])
                self.assertEqual(r.data["minutes"], avant["minutes"])
                self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 1)

    def test_technique_refuse_et_corrige_avant_recharge(self):
        for texte in ("Les données du jeu sont incomplètes.", "Le moteur a refusé.",
                      "Tu regardes poutre_conduite."):
            with self.subTest(texte=texte):
                self.assertTrue(voix_auteur(texte)[0]["attendu"])
                m = scene()
                admis = "Tu ne sais pas encore."
                r, sortie, appels = jouer(m, "que vois-tu ?", [dialogue(texte), dialogue(admis)],
                                          [rapport(ligne("neutre"))] * 2)
                self.assertNotIn(texte, sortie)
                self.assertIn(admis, sortie)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], admis)
                correction = [e for f, e in appels if f == "repondre_au_joueur"][-1]
                self.assertTrue(correction["controle_narratif"][0]["attendu"])

    def test_constructions_spatiales_techniques(self):
        for texte in ("Il est à deux cases vers le sud.", "Il est aux coordonnées (5, 11)."):
            self.assertTrue(unites_moteur(texte)[0]["attendu"])

