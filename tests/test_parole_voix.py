"""Nommer qui l'on connaît, se faire attendre de qui l'on hèle, héler soi-même (branche ``parole-voix``).

- Le joueur nomme un personnage d'après ce qu'il sait de lui (vu, voix connue, nom qu'une voix
  s'est donné), jamais d'après une place connue : cas réel du banc Luna, un personnage vu de loin
  dont la place connue s'est vidée n'était plus reconnu par son nom.
Chaque cas vérifie l'état après rechargement et ce que lit le joueur."""
import unittest

from donjon import lexique
from donjon.commandes import analyser as commande
from donjon.monde import ErreurMonde
from donjon.paroles import _connu_du_joueur, analyser
from donjon.voix import connaitre, entendues
from tests.support import calme
from tests.test_repli_et_appel import jouer
from tests.test_tensions import placer, recharger, relais
from tests.test_temps_etat import faire


def cite(monde, id):
    """Le nom d'``id`` figure-t-il dans ce que le MJ et le joueur ont lu récemment ?"""
    corpus = lexique.corpus(monde.contexte(), monde.data.get("conversation", []))
    return id in lexique.entites_citees(monde, corpus)


def place_videe():
    """Corvus voit Ilse de loin (trois cases, jamais de près) ; elle part à l'échoppe, il regarde sa
    place vide, puis le temps passe : rien de récent ne la nomme plus."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    m.joueur.update(salle="antichambre", position=[2, 2], orientation="sud")
    placer(m, "ilse", "antichambre", (2, 5))
    placer(m, "aubin", "crypte", (2, 3))
    placer(m, "brune", "crypte", (3, 3))
    m = recharger(m)
    faire(m, "attendre")
    placer(m, "ilse", "echoppe", (2, 1))
    for _ in range(7):
        faire(m, "attendre")
    return recharger(m)


class NommerTests(unittest.TestCase):
    def test_cas_reel_la_place_videe_ne_fait_pas_oublier_qui_elle_est(self):
        m = place_videe()
        # Ce qui la faisait connaître jusqu'ici a disparu : souvenir de place, portrait, mention récente.
        self.assertNotIn("ilse", m.data.get("souvenirs_visuels", {}))
        self.assertNotIn("ilse", m.data["souvenirs_personnages"])
        self.assertFalse(cite(m, "ilse"))
        self.assertIn("ilse", m.data["personnages_vus"])
        self.assertTrue(_connu_du_joueur(m, "ilse"))
        self.assertEqual(analyser(m, "je dis à Ilse : viens m'aider")["nomme"], "ilse")
        reprise, sortie, appels = jouer(m, "je dis à Ilse : viens m'aider", [], [])
        self.assertEqual(appels, [])
        self.assertIn("Tu ne vois pas Ilse d'ici : approche-toi pour lui parler.", sortie)
        self.assertEqual(reprise.data.get("paroles_joueur", []), [])

    def test_donner_a_qui_n_est_plus_la_le_moteur_dit_qu_il_n_est_pas_la(self):
        m = place_videe()
        m.objets["cloche"]["lieu"] = "joueur"
        m = recharger(m)
        p = commande(m, "je donne la cloche à Ilse")
        self.assertEqual((p["action"], p["cible"], p["outil"]), ("remettre", "cloche", "ilse"))
        reprise, sortie, appels = jouer(m, "je donne la cloche à Ilse", [], [])
        self.assertEqual(appels, [])
        self.assertIn("n'est pas là pour le recevoir", sortie)
        self.assertEqual(reprise.objets["cloche"]["lieu"], "joueur")

    def test_une_voix_connue_ou_un_nom_donne_suffisent_jamais_une_place(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[2, 2], orientation="sud")
        for id in ("brune", "aubin", "ilse"):
            placer(m, id, "crypte", (2 + ("brune", "aubin", "ilse").index(id), 3))
        # Jamais vue : Brune n'est qu'une voix connue ; Aubin, une voix inconnue qui s'est dite Aubin.
        for id in ("brune", "aubin", "ilse"):
            m.data["souvenirs_visuels"].pop(id, None)
        connaitre(m, "joueur", "brune")
        entendues(m, "joueur", ecrire=True)["ilse"] = {"minute": 0, "se_dit": "aubin", "mefiance": False, "n": 1}
        m = recharger(m)
        self.assertNotIn("brune", m.data.get("personnages_vus", []))
        for nom, id in (("Brune", "brune"), ("Aubin", "aubin")):
            self.assertTrue(_connu_du_joueur(m, id), id)
            reprise, sortie, appels = jouer(m, f"je dis à {nom} : approche", [], [])
            self.assertEqual(appels, [])
            self.assertIn(f"Tu ne vois pas {nom} d'ici : approche-toi pour lui parler.", sortie)
        # Ilse, ni vue ni entendue, ni nommée : il ne la connaît pas.
        self.assertFalse(_connu_du_joueur(m, "ilse"))
        with self.assertRaises(ErreurMonde):
            commande(m, "je donne la cloche à Ilse")


if __name__ == "__main__":
    unittest.main()
