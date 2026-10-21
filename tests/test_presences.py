"""Le bilan des présences : à la fin d'une action du joueur, on dit qui il voit désormais, qui il ne
voit plus, qui il n'a fait qu'apercevoir, sans le va-et-vient des pas. Entrer dans la pièce ou la
quitter ne se dit que s'il a vu le passage ; sinon, seul son regard a changé. Vérifié sur ce que
le joueur voit et ce que reçoit le récit, après rechargement."""
from pathlib import Path
import tempfile
import unittest

from tests.support import calme
from donjon.defi import nouveau_defi
from donjon.esprits import esprit, pnjs
from donjon.francais import designer, sujet
from donjon.geometrie import placer
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.narration import rendre_resultat
from donjon.operations import etape, sequence
from donjon.pnj import _etape, avancer
from donjon.spatial import installer

FORMES = ("entre dans la pièce.", "quitte la pièce.", "Tu aperçois", "Tu ne vois plus")


def recharger(m):
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
        chemin = Path(dossier) / "partie.json"
        m.sauver(chemin)
        return Monde.charger(chemin)


def faire(m, p):
    moteur = Moteur(m)
    texte = moteur.executer(moteur.preparer(p))
    return recharger(m), texte


def scene(salle, case, regard, depart, position, vers):
    """Placement d'auteur : seul Gorm est dans les parages, les autres sont à la galerie de ronde ;
    Gorm part pour ``vers``, de son pas, depuis ``depart``. Le joueur regarde vers ``regard``."""
    m = nouveau_defi(depart="fixe")
    installer(m)
    calme(m, "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("brune", "ilse", "aubin")):
        m.objets[id]["lieu"] = "chambre_cloche"
        placer(m.objets[id], "chambre_cloche", [1 + n, 12])
    m.objets["marchand"]["lieu"] = depart
    placer(m.objets["marchand"], depart, position)
    esprit(m, "marchand")["intention"] = {"but": {"type": "rejoindre", "lieu": vers}, "motif": "alerte",
                                          "plan": [_etape("aller", lieu=vers)], "depuis": 0, "attente": 0}
    m.joueur.update(salle=salle, position=list(case), orientation=regard)
    return m


class BilanTests(unittest.TestCase):
    def presences(self, avant, texte, apres):
        """Le bilan affiché s'accorde avec ce que le joueur voyait avant l'action et voit après
        rechargement : une ligne au plus par personnage, et jamais un aller-retour."""
        lignes = texte.splitlines()
        self.assertFalse([l for l in lignes if l.endswith((" arrive.", " s'éloigne."))])
        bilan = {}
        for id in pnjs(apres):
            o = apres.objets[id]
            miennes = [l for l in lignes if designer(o) in l and any(f in l for f in FORMES)]
            self.assertLessEqual(len(miennes), 1, miennes)
            v0, v1 = avant.visible(id), apres.visible(id)
            ligne = miennes[0] if miennes else None
            if v1 and not v0:
                self.assertIn(ligne, (sujet(o) + " entre dans la pièce.", "Tu aperçois " + designer(o) + ".",
                                      "Tu aperçois au-delà du passage " + designer(o) + "."))
            elif v0 and not v1:
                self.assertIn(ligne, (sujet(o) + " quitte la pièce.", "Tu ne vois plus " + designer(o) + "."))
            elif not v0 and not v1:
                self.assertIn(ligne, (None, "Tu aperçois un instant " + designer(o) + "."))
            bilan[id] = ligne
        # Le récit reçoit ces mêmes lignes, et le journal les garde après rechargement.
        self.assertEqual(rendre_resultat(texte).splitlines(), [l for l in lignes if not l.startswith("1d20(")])
        self.assertEqual(apres.data["journal"][-1]["faits"], lignes)
        return bilan

    def test_cas_reel_prendre_la_torche_et_l_allumer(self):
        # La partie réelle : au refuge, en [1, 3], « je prends la torche et je l'allume avec mon
        # briquet » ; les PNJ vont et viennent pendant ces deux minutes.
        m = nouveau_defi(depart="fixe")
        installer(m)
        avant = m.copier()
        reprise, texte = faire(m, sequence(etape("deplacer", "torche", "joueur"),
                                           etape("allumer", "torche", outil="briquet")))
        self.assertTrue(reprise.objets["torche"]["allume"])
        self.assertEqual(reprise.objets["torche"]["lieu"], "joueur")
        bilan = self.presences(avant, texte, reprise)
        # Ceux qu'il n'a fait qu'entrevoir sont aperçus un instant, sans arrivée ni départ.
        self.assertTrue(any(l and "un instant" in l for l in bilan.values()), texte)
        # Le bilan suit l'action entière : aucune ligne de présence avant le dernier geste.
        self.assertGreater(texte.index("Tu aperçois"), texte.index("La torche s'allume."))

    def test_traverser_son_regard_pendant_une_attente(self):
        # Gorm passe du refuge à la salle des vannes par la conduite, sous les yeux du joueur.
        m = scene("echoppe", [1, 5], "est", "antichambre", [6, 1], "crypte")
        avant = m.copier()
        reprise, texte = faire(m, proposition("attendre"))
        self.assertEqual(reprise.objets["marchand"]["lieu"], "crypte")
        self.assertEqual(self.presences(avant, texte, reprise)["marchand"],
                         "Tu aperçois un instant Gorm, gardien du relais.")

    def test_entrer_dans_la_piece_et_y_rester(self):
        m = scene("antichambre", [2, 3], "ouest", "echoppe", [1, 1], "antichambre")
        avant = m.copier()
        reprise, texte = faire(m, proposition("attendre"))
        self.assertEqual(reprise.objets["marchand"]["lieu"], "antichambre")
        self.assertEqual(self.presences(avant, texte, reprise)["marchand"],
                         "Gorm, gardien du relais, entre dans la pièce.")
        # Son humeur se remarque une fois qu'on le voit, pas avant.
        lignes = texte.splitlines()
        if "Gorm, gardien du relais, semble calme." in lignes:
            self.assertGreater(lignes.index("Gorm, gardien du relais, semble calme."),
                               lignes.index("Gorm, gardien du relais, entre dans la pièce."))

    def test_quitter_la_piece_sous_ses_yeux(self):
        m = scene("antichambre", [2, 3], "ouest", "antichambre", [0, 4], "crypte")
        avant = m.copier()
        self.assertTrue(avant.visible("marchand"))
        reprise, texte = faire(m, proposition("attendre"))
        self.assertEqual(self.presences(avant, texte, reprise)["marchand"], "Gorm, gardien du relais, quitte la pièce.")

    def test_un_regard_qui_change_n_est_ni_une_arrivee_ni_un_depart(self):
        m = scene("antichambre", [2, 3], "est", "crypte", [4, 3], "crypte")
        m.objets["ilse"]["lieu"] = "antichambre"
        placer(m.objets["ilse"], "antichambre", [0, 4])
        avant = m.copier()
        m, texte = faire(m, proposition("tourner", "ouest"))
        self.assertEqual(self.presences(avant, texte, m)["ilse"], "Tu aperçois Ilse, meunière évacuée.")
        avant = m.copier()
        m, texte = faire(m, proposition("tourner", "est"))
        self.assertEqual(self.presences(avant, texte, m)["ilse"], "Tu ne vois plus Ilse, meunière évacuée.")
        self.assertEqual(m.objets["ilse"]["lieu"], "antichambre")

    def test_la_vie_des_pnj_seule_fait_son_propre_bilan(self):
        m = scene("echoppe", [1, 5], "est", "antichambre", [6, 1], "crypte")
        lignes = []
        m.data["minutes"] += 5
        apparus = avancer(m, 5, lignes)
        # Aperçu en chemin : il compte parmi ceux qui sont apparus, et le bilan le dit.
        self.assertEqual(apparus, ["marchand"])
        self.assertEqual(lignes, ["Tu aperçois un instant Gorm, gardien du relais."])


if __name__ == "__main__":
    unittest.main()
