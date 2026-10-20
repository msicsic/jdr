"""L'horloge à la seconde : les pas du joueur font passer les minutes, après rechargement compris."""
import copy
from pathlib import Path
import tempfile
import unittest

from donjon.defi import nouveau_defi
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.spatial import installer


def relais():
    m = nouveau_defi()
    installer(m)
    m.joueur.update(salle="crypte", position=[4, 0])
    return m


def recharger(m):
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
        chemin = Path(dossier) / "partie.json"
        m.sauver(chemin)
        return Monde.charger(chemin)


class HorlogeTests(unittest.TestCase):
    def test_les_pas_font_passer_les_secondes_meme_rechargee_entre_deux(self):
        m = relais()
        m.joueur["orientation"] = "sud"
        depart = m.data["minutes"]
        for direction in ["sud"] * 4:
            Moteur(m).executer(Moteur(m).preparer(proposition("marcher", direction)))
        self.assertEqual((m.data["minutes"], m.data["dixiemes"]), (depart, 60))
        m = recharger(m)
        # Se tourner vers l'ouest (un quart de tour, 1 s), puis quatre pas.
        for direction in ["ouest"] * 4:
            Moteur(m).executer(Moteur(m).preparer(proposition("marcher", direction)))
        self.assertEqual((m.data["minutes"], m.data["dixiemes"]), (depart, 60 + 10 + 60))

    def test_une_attente_garde_les_secondes_deja_passees(self):
        m = relais()
        m.joueur["orientation"] = "sud"
        depart = m.data["minutes"]
        for direction in ["sud"] * 3:
            Moteur(m).executer(Moteur(m).preparer(proposition("marcher", direction)))
        Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        self.assertEqual((m.data["minutes"], m.data["dixiemes"]), (depart + 5, 45))

    def test_une_ancienne_partie_compte_ses_pas_en_secondes(self):
        data = copy.deepcopy(relais().data)
        data.pop("dixiemes")
        data["pas_depuis_minute"] = 7
        m = Monde(data)
        self.assertEqual(m.data["dixiemes"], 420)  # Sept pas de l'ancien temps, à 6 s chacun.
        self.assertNotIn("pas_depuis_minute", m.data)


if __name__ == "__main__":
    unittest.main()
