"""L'ancien son fondu dans l'ouïe commune, vérifié après rechargement : les sons du joueur et des
objets retentissent par la même règle que les gestes (distance en cases, portes) ; le réflexe
déclaré devient un seuil d'alerte du profil, et la décision d'aller voir passe par la délibération ;
le protecteur reconnaît la voix de son protégé ; un seul souvenir de ce qu'on entend ; l'appelé se
tourne vers la voix ; la réponse au joueur vient à la fin de son cri."""
import unittest

from donjon.banc_pnj import creer
from donjon.commandes import analyser
from donjon.deliberation import alarme, bruit_a_voir
from donjon.esprits import dernier_son, lire, percoit, percevoir_tous
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.sons import HELER
from donjon.temps import instant
from tests.support import calme, regarder
from tests.test_protection import seule_et_a_bout
from tests.test_temps_etat import decouper, etat_pnj
from tests.test_tensions import chronique, placer, recharger, relais, vivre


def faire(m, commande):
    moteur = Moteur(m)
    return moteur.executer(moteur.preparer(analyser(m, commande) if isinstance(commande, str) else commande))


def bruit(m, id, salle):
    return next((s for s in lire(m, id)["memoire"] if s["type"] == "bruit" and s["salle"] == salle), None)


class PorteFermeeTests(unittest.TestCase):
    """L'appel à l'aide du joueur derrière la porte étanche fermée : l'ouïe commune compte la porte
    et la distance ; l'ancienne portée donnait le même niveau à toute la salle voisine."""

    def scene(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="beffroi", position=[0, 3])
        placer(m, "marchand", "crypte", (8, 3))   # contre la porte
        placer(m, "aubin", "crypte", (1, 3))      # à l'autre bout des vannes
        placer(m, "ilse", "antichambre", (4, 1))
        placer(m, "brune", "antichambre", (6, 5))
        regarder(m, "marchand", (4, 3))
        percevoir_tous(m)
        return recharger(m)

    def test_proche_puis_loin(self):
        m = self.scene()
        texte = faire(m, "je crie a l'aide")
        m = recharger(m)
        self.assertIn("Tu cries à l'aide.", texte)
        self.assertEqual(sorted(m.data["sons"][-1]["auditeurs"]), ["aubin", "brune", "ilse", "marchand"])
        self.assertEqual(m.data["sons"][-1]["bruit"], "appel")
        # Contre la porte, 6 crans ; au fond de la salle, 3 : la distance compte, la porte aussi.
        self.assertEqual({k: bruit(m, "marchand", "beffroi")[k] for k in ("nature", "niveau")},
                         {"nature": "appel", "niveau": 6})
        self.assertEqual(bruit(m, "aubin", "beffroi")["niveau"], 3)
        # Personne ne passe « inquiet » d'office : l'inquiétude vient de ce qu'il entend.
        self.assertEqual(m.objets["marchand"]["humeur"], relais().objets["marchand"]["humeur"])
        self.assertGreater(lire(m, "marchand")["besoins"]["securite"], 0)

    def test_au_seuil_d_alerte_le_proche_accourt_le_lointain_non(self):
        # Autre cas de même nature que le gardien de l'auberge : un seuil d'alerte de 5 crans.
        m = self.scene()
        for id in ("marchand", "aubin"):
            m.objets[id]["profil"]["alerte"] = 5
        faire(m, "je crie a l'aide")
        m = recharger(m)
        self.assertEqual(alarme(m, "marchand"), ("beffroi", "devoir"))
        self.assertIsNone(alarme(m, "aubin"))

    def test_d_un_bloc_ou_par_morceaux_le_monde_est_le_meme(self):
        # Gorm, alerté, va chercher la clé du relais pour ouvrir la porte et voir d'où venait l'appel :
        # attendu d'un bloc ou découpé en rotations rechargées, le même monde.
        def scene():
            m = self.scene()
            m.objets["marchand"]["profil"]["alerte"] = 5
            m.joueur["orientation"] = "nord"
            faire(m, "je crie a l'aide")
            return m
        d_un_bloc, morcele = decouper(scene, 6)
        self.assertIn("Gorm, gardien du relais prend la clé du relais.", chronique(morcele))
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))


class CloceTests(unittest.TestCase):
    def test_la_cloche_du_relais_sonne_comme_un_appel(self):
        # Le son d'un objet retentit par l'ouïe commune, selon sa sonorité (``ouie.SONS``) : la cloche
        # d'alarme (3) porte comme un appel, de la galerie jusqu'au refuge, par l'escalier.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="chambre_cloche", position=[3, 3])
        placer(m, "marchand", "antichambre", (4, 1))
        percevoir_tous(m)
        texte = faire(m, "sonner cloche")
        m = recharger(m)
        self.assertIn("Tu produis un son avec la cloche d'alarme.", texte)
        self.assertEqual((m.data["sons"][-1]["objet"], m.data["sons"][-1]["bruit"]), ("cloche", "appel"))
        self.assertIn("marchand", m.data["sons"][-1]["auditeurs"])
        self.assertIn(("chambre_cloche", "appel"),
                      [(s["salle"], s["nature"]) for s in lire(m, "marchand")["memoire"] if s["type"] == "bruit"])
        # Il y va : la cloche est sous sa garde (une pulsion de son devoir), et il a du courage. Il est
        # parti dès le son, pendant que le joueur sonnait (``deliberation-evenements``).
        self.assertEqual(bruit_a_voir(m, "marchand"), ("chambre_cloche", "devoir"))
        self.assertEqual(lire(m, "marchand")["intention"]["but"], {"type": "voir", "lieu": "chambre_cloche"})
        self.assertNotEqual(m.objets["marchand"]["lieu"], "antichambre")


class ProtegeTests(unittest.TestCase):
    def test_le_protecteur_reconnait_la_voix_de_son_protege(self):
        # Cas réel (``test_protection``) : Ilse, à bout, appelle ; Gorm connaît sa voix.
        m, _ = vivre(seule_et_a_bout(relais()), 1)
        self.assertEqual(dernier_son(m, "marchand")["qui"], "ilse")
        self.assertEqual(lire(m, "marchand")["croyances"]["ilse"]["lieu"]["source"], "entendu")
        self.assertEqual(alarme(m, "marchand"), ("echoppe", "devoir"))

    def test_sans_connaitre_sa_voix_ce_n_est_qu_un_appel(self):
        # Même appel, mais Gorm ne connaît pas la voix d'Ilse : il ne sait pas que c'est elle.
        m = seule_et_a_bout(relais())
        lire(m, "marchand")["voix"].remove("ilse")
        m, _ = vivre(m, 1)
        self.assertNotIn("qui", dernier_son(m, "marchand"))
        self.assertIsNone(alarme(m, "marchand"))


class GardienTests(unittest.TestCase):
    def scene(self):
        """Auberge : le joueur, dans le couloir de l'étage, appelle à l'aide ; Hugues, l'ancien soldat
        (seuil d'alerte 3), et Odile sont dans la salle commune, en bas de l'escalier."""
        m = creer("auberge", 1985, "fixe")
        calme(m, "odile", "mireille", "tilo", "joss", "anselme", "hugues", "mathurine", "lucien")
        m.joueur.update(salle="couloir", position=[4, 1])
        percevoir_tous(m)
        return recharger(m)

    def test_le_gardien_au_seuil_d_alerte_bas_accourt(self):
        # Cas réel : le réflexe déclaré d'Hugues (``reaction_son`` seuil 2) devenu le seuil d'alerte.
        m = self.scene()
        self.assertEqual(m.objets["hugues"]["profil"]["alerte"], 3)
        from tests.test_deliberation_evenements import Choix
        with Choix("hugues", "odile") as choix:
            faire(m, "je crie a l'aide")
        m = recharger(m)
        # L'alarme l'envoie voir aussitôt, pendant le cri même (``deliberation-evenements``), au titre
        # de son devoir : il a parcouru le couloir des yeux, le bruit est vu.
        self.assertEqual([b for t, x, b in choix.choix if x == "hugues"][0], {"type": "voir", "lieu": "couloir"})
        self.assertEqual([s for s in lire(m, "hugues")["memoire"] if s["type"] == "bruit"], [])
        self.assertIn("Hugues, ancien soldat passe dans : Couloir de l'étage.", chronique(m))
        self.assertIn("Hugues va voir d'où venait le bruit : Couloir de l'étage.", chronique(m))
        # Odile, aussi courageuse et sans seuil d'alerte, n'a pas d'alarme : elle y va par courage, un
        # cri étant inhabituel (``bruit_a_voir``), et non en alarme.
        self.assertIsNone(alarme(m, "odile"))


class HelerTests(unittest.TestCase):
    def test_l_appele_se_tourne_vers_la_voix_et_voit_l_appelant(self):
        # Gorm, au refuge, tourne le dos au joueur qui l'appelle par son nom : il se tourne vers la
        # voix, le voit, et lui répond.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[1, 1])
        placer(m, "marchand", "antichambre", (6, 1))
        m.objets["marchand"]["orientation"] = "est"
        percevoir_tous(m)
        self.assertFalse(percoit(m, "marchand", "joueur"))
        texte = faire(m, "je crie gorm")
        m = recharger(m)
        textes = chronique(m)
        tourne = textes.index("Gorm, gardien du relais se tourne vers la voix qui l'appelle.")
        self.assertLess(tourne, textes.index("Gorm répond : « Ici ! »"))
        self.assertEqual(m.objets["marchand"]["orientation"], "ouest")
        self.assertEqual(lire(m, "marchand")["croyances"]["joueur"]["lieu"]["source"], "vu")
        self.assertNotIn("Aucune réponse ne te parvient.", texte)

    def test_appele_d_une_autre_salle_il_se_tourne_vers_le_seuil(self):
        # Autre cas de même nature : Gorm, dans la conduite, est appelé depuis le refuge ; il se
        # tourne vers le passage par où vient la voix.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[1, 3])
        placer(m, "marchand", "echoppe", (5, 3))
        m.objets["marchand"]["orientation"] = "ouest"
        percevoir_tous(m)
        faire(m, "je crie gorm")
        m = recharger(m)
        self.assertIn("Gorm, gardien du relais se tourne vers la voix qui l'appelle.", chronique(m))
        self.assertEqual(m.objets["marchand"]["orientation"], "est")

    def test_la_reponse_vient_a_la_fin_des_trois_secondes(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[1, 3])
        placer(m, "marchand", "echoppe", (5, 3))
        percevoir_tous(m)
        debut = instant(m)
        faire(m, sequence(etape("emettre_son", "marchand", methode="heler"), justification=""))
        m = recharger(m)
        reponse = next(b for b in m.data["bruits"] if b["auteur"] == "marchand" and "Ici" in b["texte"])
        self.assertEqual(reponse["instant"], debut + HELER)


if __name__ == "__main__":
    unittest.main()
