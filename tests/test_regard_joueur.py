"""Le joueur sur l'horloge commune : se tourner prend du temps, un pas chassé garde le regard, on
se tourne vers ce qu'on manipule, on sait où sont les sorties qu'on a vues, et ses pas s'entendent."""
from pathlib import Path
import tempfile
import unittest

from tests.support import calme, regarder
from donjon.carte import carte
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.esprits import lire, percoit
from donjon.geometrie import placer
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.spatial import installer


def relais():
    m = nouveau_defi()
    installer(m)
    return calme(m, "marchand", "brune", "ilse", "aubin")


def faire(m, commande):
    moteur = Moteur(m)
    return moteur.executer(moteur.preparer(analyser(m, commande)))


def instant(m):
    return m.data["minutes"] * 600 + m.data["dixiemes"]


class RegardTests(unittest.TestCase):
    def test_se_tourner_prend_du_temps_et_se_recharge(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[5, 5], orientation="est")
        avant = instant(m)
        self.assertIn("Tu te tournes vers l'ouest.", faire(m, "tourner ouest"))
        self.assertEqual(instant(m) - avant, 20)  # Un demi-tour : 2 s.
        faire(m, "demi-tour")
        self.assertEqual(m.joueur["orientation"], "est")
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)
            self.assertEqual(Monde.charger(chemin).joueur["orientation"], "est")

    def test_un_pas_chasse_garde_le_regard_et_prend_le_double(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[5, 5], orientation="est")
        avant = instant(m)
        faire(m, "chasse ouest")
        self.assertEqual((m.joueur["position"], m.joueur["orientation"]), ([4, 5], "est"))
        self.assertEqual(instant(m) - avant, 30)
        faire(m, "pas ouest")  # Se tourner (2 s), puis avancer (1,5 s).
        self.assertEqual((m.joueur["position"], m.joueur["orientation"]), ([3, 5], "ouest"))
        self.assertEqual(instant(m) - avant, 30 + 20 + 15)

    def test_la_carte_montre_le_regard(self):
        m = relais()
        m.joueur.update(salle="antichambre", position=[5, 5], orientation="nord-est")
        self.assertIn("@↗", carte(m))

    def test_un_geste_sur_ce_qu_il_a_dans_le_dos_le_tourne_d_abord(self):
        m = relais()
        m.objets["torche"].update(position=[4, 5], position_salle="antichambre", lieu="antichambre")
        m.joueur.update(salle="antichambre", position=[5, 5], orientation="est")
        self.assertFalse(m.visible("torche"))
        texte = faire(m, "prendre torche")
        self.assertIn("Tu te tournes vers l'ouest.", texte)
        self.assertEqual((m.objets["torche"]["lieu"], m.joueur["orientation"]), ("joueur", "ouest"))

    def test_une_sortie_deja_franchie_reste_connue_dans_son_dos(self):
        m = relais()
        m.joueur.update(salle="echoppe", position=[8, 3], orientation="est")
        faire(m, "pas est")  # Il entre au refuge, face à l'est : la sortie ouest est dans son dos.
        self.assertEqual(m.joueur["salle"], "antichambre")
        self.assertIn("ouest", m.contexte()["salle"]["sorties"])

    def test_ses_pas_font_se_retourner_qui_les_entend_de_pres(self):
        m = relais()
        m.objets["marchand"]["lieu"] = "antichambre"
        placer(m.objets["marchand"], "antichambre", [6, 5])
        regarder(m, "marchand", [8, 5])
        m.joueur.update(salle="antichambre", position=[3, 5], orientation="est")
        self.assertFalse(percoit(m, "marchand", "joueur"))
        faire(m, "pas est")
        self.assertEqual(m.objets["marchand"]["orientation"], "ouest")
        self.assertTrue(percoit(m, "marchand", "joueur"))
        self.assertEqual(lire(m, "marchand")["croyances"]["joueur"]["lieu"]["valeur"], "antichambre")


if __name__ == "__main__":
    unittest.main()
