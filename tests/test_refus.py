"""Des refus qui guident : chaque refus dit au MJ, en champs et identifiants, ce qui serait accepté."""
import unittest
from unittest.mock import patch

from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence


def refus(m, p):
    try:
        Moteur(m).preparer(p)
    except ErreurMonde as exc:
        return exc
    raise AssertionError("refus attendu")


class AttenduTests(unittest.TestCase):
    def test_observer_un_objet_oriente_vers_examiner(self):
        exc = refus(nouveau_monde(), proposition("observer", "antichambre_sol"))
        self.assertIn("reçu « antichambre_sol »", exc.attendu)
        self.assertIn("examiner", exc.attendu)

    def test_identifiant_inconnu_liste_les_cibles_valables(self):
        exc = refus(nouveau_monde(), proposition("examiner", "sol"))
        self.assertIn("« sol » n'est pas un identifiant connu", exc.attendu)
        self.assertIn("antichambre_sol", exc.attendu)

    def test_objet_d_une_autre_salle_est_dit_absent(self):
        exc = refus(nouveau_monde(), proposition("examiner", "marteau"))
        self.assertIn("n'est pas ici", str(exc))
        self.assertIn("marteau n'est pas dans la salle du joueur", exc.attendu)

    def test_objet_dans_un_contenant_ferme_demande_de_l_ouvrir(self):
        m = nouveau_monde()
        m.joueur["salle"] = "crypte"
        exc = refus(m, proposition("examiner", "anneau"))
        self.assertIn("ouvre d'abord coffre", exc.attendu)

    def test_sortie_inconnue_liste_les_sorties(self):
        exc = refus(nouveau_monde(), proposition("aller", "sud"))
        self.assertIn("nord, ouest", exc.attendu)

    def test_porte_fermee_nomme_la_porte_a_ouvrir(self):
        exc = refus(nouveau_monde(), proposition("aller", "nord"))
        self.assertIn("ouvre d'abord porte", exc.attendu)

    def test_outil_absent_distingue_inconnu_et_non_porte(self):
        m = nouveau_monde()
        inconnu = refus(m, proposition("frapper", "porte", "massue"))
        self.assertIn("objets portés", inconnu.attendu)
        self.assertIn("couteau", inconnu.attendu)
        ailleurs = refus(m, proposition("crocheter", "porte", "crochets"))
        self.assertIn("crochets n'est pas à portée", ailleurs.attendu)
        m.objets["crochets"]["lieu"] = "antichambre"
        ici = refus(m, proposition("crocheter", "porte", "crochets"))
        self.assertIn("prends d'abord crochets", ici.attendu)

    def test_outil_inadapte_liste_les_outils_qui_conviennent(self):
        exc = refus(nouveau_monde(), proposition("crocheter", "porte", "couteau"))
        self.assertIn("usage crochetage", exc.attendu)

    def test_action_inconnue_liste_les_actions(self):
        exc = refus(nouveau_monde(), proposition("fouiller", "antichambre_sol"))
        self.assertIn("examiner", exc.attendu)
        self.assertNotIn("clarifier", exc.attendu)

    def test_l_etape_fautive_est_numerotee(self):
        exc = refus(nouveau_monde(), sequence(etape("deplacer", "cle", "joueur"),
                                              etape("allumer", "cle")))
        self.assertTrue(exc.attendu.startswith("étape 2 (allumer)"))

    def test_patienter_dit_ses_champs(self):
        exc = refus(nouveau_monde(), sequence(etape("patienter", "marchand")))
        self.assertIn("cible, destination et outil vides", exc.attendu)


class TransmissionTests(unittest.TestCase):
    def test_le_mj_recoit_attendu_dans_le_retour_moteur(self):
        m = nouveau_monde()
        mauvaise = {"mode": "action", "texte": "", "faits": [],
                    "proposition": proposition("observer", "antichambre_sol")}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler", side_effect=[mauvaise, ErreurMonde("indisponible")]) as appel:
            try:
                mj._echanger_prepare(m, "j'observe le sol")
            except ErreurMonde:
                pass
        retour = appel.call_args_list[1].args[1]["faits"]["retour_moteur"]
        self.assertIn("examiner", retour["attendu"])
        self.assertNotIn("examiner", retour["obstacle"])


if __name__ == "__main__":
    unittest.main()
