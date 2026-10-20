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
    def test_dix_pas_font_une_minute_meme_rechargee_entre_deux(self):
        m = relais()
        depart = m.data["minutes"]
        for direction in ["sud"] * 4:
            Moteur(m).executer(Moteur(m).preparer(proposition("marcher", direction)))
        self.assertEqual((m.data["minutes"], m.data["dixiemes"]), (depart, 240))
        m = recharger(m)
        for direction in ["sud", "ouest", "ouest", "ouest", "ouest", "est"]:
            Moteur(m).executer(Moteur(m).preparer(proposition("marcher", direction)))
        self.assertEqual((m.data["minutes"], m.data["dixiemes"]), (depart + 1, 0))

    def test_une_attente_garde_les_secondes_deja_passees(self):
        m = relais()
        depart = m.data["minutes"]
        for direction in ["sud"] * 3:
            Moteur(m).executer(Moteur(m).preparer(proposition("marcher", direction)))
        Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        self.assertEqual((m.data["minutes"], m.data["dixiemes"]), (depart + 5, 180))

    def test_une_ancienne_partie_compte_ses_pas_en_secondes(self):
        data = copy.deepcopy(relais().data)
        data.pop("dixiemes")
        data["pas_depuis_minute"] = 7
        m = Monde(data)
        self.assertEqual(m.data["dixiemes"], 420)
        self.assertNotIn("pas_depuis_minute", m.data)


if __name__ == "__main__":
    unittest.main()
