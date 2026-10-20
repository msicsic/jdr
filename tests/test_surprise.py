"""La surprise : arriver dans le dos de quelqu'un à pas feutrés, lui prendre son bien sans qu'il le
voie ; un PNJ qui prépare un geste sans témoin marche lui aussi à pas feutrés."""
import unittest

from tests.support import calme, regarder
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.esprits import croire, lire, percoit
from donjon.geometrie import placer
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.ouie import retentir
from donjon.pnj import _marcher
from donjon.spatial import installer
from donjon.temps import PAS_FEUTRE


def scene():
    """Gorm, au refuge, regarde vers l'est ; son marteau est posé derrière lui ; le joueur arrive
    de l'ouest."""
    m = nouveau_defi()
    installer(m)
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    m.objets["marchand"]["lieu"] = "antichambre"
    placer(m.objets["marchand"], "antichambre", [5, 5])
    regarder(m, "marchand", [8, 5])
    m.objets["marteau"].update(proprietaire="marchand", lieu="antichambre", position=[3, 5],
                               position_salle="antichambre")
    m.joueur.update(salle="antichambre", position=[1, 5], orientation="est")
    m.objets["lanterne"]["allume"] = False
    # Les autres sont à la salle des vannes, et Gorm le sait : seuls Gorm et le joueur sont au refuge.
    for n, id in enumerate(("brune", "ilse", "aubin")):
        m.objets[id]["lieu"] = "crypte"
        placer(m.objets[id], "crypte", [2 + n, 3])
        croire(m, "marchand", id, "lieu", "crypte", "vu", salle="crypte", case=[2 + n, 3])
    return m


def faire(m, commande):
    moteur = Moteur(m)
    return moteur.executer(moteur.preparer(analyser(m, commande)))


class SurpriseTests(unittest.TestCase):
    def test_des_pas_ordinaires_le_font_se_retourner(self):
        m = scene()
        faire(m, "pas est")
        self.assertEqual(m.objets["marchand"]["orientation"], "ouest")
        self.assertTrue(percoit(m, "marchand", "joueur"))

    def test_a_pas_feutres_on_lui_prend_son_bien_dans_le_dos(self):
        m = scene()
        self.assertIn("Tu avances à pas feutrés.", faire(m, "faufiler est"))
        self.assertEqual(m.objets["marchand"]["orientation"], "est")
        self.assertFalse(percoit(m, "marchand", "joueur"))
        moteur = Moteur(m)
        plan = moteur.preparer(sequence(etape("deplacer", "marteau", "joueur", methode="discret")))
        self.assertFalse(plan.stat)  # Personne ne le voit : pas de jet.
        moteur.executer(plan)
        self.assertEqual(m.objets["marteau"]["lieu"], "joueur")
        self.assertNotIn("vol_surpris", [s["type"] for s in lire(m, "marchand")["memoire"]])

    def test_le_meme_vol_sous_ses_yeux_demande_un_jet(self):
        m = scene()
        faire(m, "pas est")  # Il l'a entendu, il s'est retourné.
        plan = Moteur(m).preparer(sequence(etape("deplacer", "marteau", "joueur", methode="discret")))
        self.assertEqual(plan.stat, "DEX")


class PasFeutresTests(unittest.TestCase):
    def test_qui_prepare_un_geste_sans_temoin_marche_a_pas_feutres(self):
        m = scene()
        m.objets["brune"]["lieu"] = "antichambre"
        placer(m.objets["brune"], "antichambre", [1, 5])
        regarder(m, "brune", [8, 5])
        lire(m, "brune")["intention"] = {"but": {"type": "manger", "objet": "vivres"}, "motif": "faim",
                                          "depuis": 0, "attente": 0, "plan": [
            {"operation": "crocheter", "cible": "reserve", "outil": "crochets", "lieu": "", "condition": "sans_temoin"}]}
        lire(m, "marchand")["croyances"].pop("brune")  # Il ne la sait pas là.
        duree = _marcher(m, "brune", lambda salle, case: salle == "antichambre" and case == (2, 5), [])
        self.assertEqual(duree, PAS_FEUTRE)
        self.assertEqual(m.objets["marchand"]["orientation"], "est")  # Trois cases : il n'entend rien.
        retentir(m, "brune", "aller")  # Le même pas, ordinaire : il se retourne.
        self.assertEqual(m.objets["marchand"]["orientation"], "ouest")


if __name__ == "__main__":
    unittest.main()
