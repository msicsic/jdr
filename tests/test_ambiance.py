"""La preuve du moteur ne devient pas la voix du récit, même après un audit permissif."""
import copy
import unittest

from donjon.monde import ErreurMonde
from donjon.narration import consigner, controler, voix_auteur
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_commune import scene
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger


class AmbianceTests(unittest.TestCase):
    def test_reserve_de_preuve_revisee_avant_affichage_et_recharge(self):
        cas = (
            ("Tu entends le calme de la conduite ; les données ne précisent aucun autre son.",
             "Tu entends le calme de la conduite.", "calme", "les données"),
            ("Une odeur de terre humide flotte ici ; les faits ne précisent pas son origine.",
             "Une odeur de terre humide flotte ici.", "odeur de terre", "les faits"),
        )
        for mauvais, admis, entite, recu in cas:
            with self.subTest(mauvais=mauvais):
                m = scene()
                objets, joueur = copy.deepcopy(m.objets), copy.deepcopy(m.joueur)
                r, sortie, appels = jouer(m, "décris l'atmosphère", [dialogue(mauvais), dialogue(admis)],
                    [rapport(ligne("ambiance", entites=[entite]))] * 2)
                self.assertNotIn(mauvais, sortie)
                self.assertIn(admis, sortie)
                corrections = [e for f, e in appels if f == "repondre_au_joueur"]
                self.assertEqual(len(corrections), 2)
                refus = corrections[-1]["controle_narratif"]
                self.assertEqual(len(refus), 1)
                self.assertIn(f"reçu « {recu} »", refus[0]["attendu"])
                self.assertIn("sans parler du jeu", refus[0]["attendu"])
                self.assertNotIn(refus[0]["attendu"], sortie)
                self.assertEqual(r.data["ambiances"][m.joueur["salle"]][-1]["texte"], admis)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], admis)
                self.assertEqual(r.objets, objets)
                self.assertEqual(r.joueur, joueur)
                self.assertEqual(r.data["minutes"], m.data["minutes"])

                # L'écriture refait le garde, même si les métadonnées de l'audit ont été altérées.
                audit = controler(mauvais, rapport(ligne("ambiance", entites=[entite])), {})
                audit.update(texte_initial=mauvais, faits={}, fondement="")
                avant = copy.deepcopy(r.data)
                with self.assertRaises(ErreurMonde):
                    consigner(r, {"texte": mauvais, "_audit": audit})
                self.assertEqual(recharger(r).data, avant)

    def test_inconnue_mecanique_dite_en_perception_persiste(self):
        m = scene()
        texte = "Tu ne vois pas la personne d'ici."
        avant = copy.deepcopy(m.objets)
        r, sortie, appels = jouer(m, "que vois-tu au loin ?", [dialogue(texte)],
                                  [rapport(ligne("mecanique", sources=["perception"]))])
        self.assertIn(texte, sortie)
        self.assertEqual(r.data["narrations_mj"][-1]["texte"], texte)
        self.assertFalse(r.data.get("ambiances"))
        self.assertEqual(r.objets, avant)
        self.assertEqual([f for f, _ in appels].count("repondre_au_joueur"), 1)

    def test_retour_d_invention_preserve_l_ambiance_sans_inviter_une_reserve(self):
        m = scene()
        objets = copy.deepcopy(m.objets)
        mauvais = "Une odeur de terre flotte ici, près d'une ouverture nouvelle dans le mur."
        admis = "Une odeur de terre flotte ici."
        r, sortie, appels = jouer(m, "décris l'atmosphère", [dialogue(mauvais), dialogue(admis)], [
            rapport(ligne("invention_protegee", motif="Une ouverture utilisable est inventée.")),
            rapport(ligne("ambiance", entites=["odeur de terre"]))])
        correction = [e for f, e in appels if f == "repondre_au_joueur"][-1]
        attendu = correction["controle_narratif"][0]["attendu"]
        self.assertIn("l'ambiance compatible reste libre", attendu)
        self.assertNotIn("dis qu'il l'ignore", attendu)
        self.assertNotIn(mauvais, sortie)
        self.assertIn(admis, sortie)
        self.assertEqual(r.data["ambiances"][m.joueur["salle"]][-1]["texte"], admis)
        self.assertEqual(r.data["narrations_mj"][-1]["texte"], admis)
        self.assertEqual(r.objets, objets)

    def test_vocabulaire_commun_et_limites_de_fiction(self):
        for texte in ("Ce passage n'est pas établi.", "Aucune présence n'est attestée.",
                      "Rien ne confirme cette position.", "Tu ne peux préciser faute d'indication.",
                      "Son origine n'est pas indiquée."):
            with self.subTest(texte=texte):
                self.assertFalse(voix_auteur(texte, "justification"))
        for texte in ("Tu ignores d'où vient cette odeur.", "La flèche indique le nord.",
                      "Tu ne le vois pas d'ici.", "« Rien n'est établi », dit la voix."):
            with self.subTest(texte=texte):
                self.assertFalse(voix_auteur(texte))


if __name__ == "__main__":
    unittest.main()
