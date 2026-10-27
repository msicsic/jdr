"""Attendre une durée (« attendre 30 s », « attendre 10 min », la touche Espace) : par tranches, le
même monde qu'un bloc ; le joueur cesse d'attendre quand il voit paraître quelqu'un, même un instant,
ou entend un appel, un cri, un fracas, des paroles dont il saisit les mots. Vérifié sur l'état et
sur ce que le joueur lit, après rechargement."""
import re
import unittest
from unittest.mock import patch

from donjon.commandes import analyser
from donjon.esprits import croire, lire, pnjs
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.temps import instant
from tests.test_presences import faire, scene
from tests.test_tensions import relais


def attendre(m, commande):
    """Joue la commande ; renvoie le monde rechargé, le texte lu et la durée écoulée (dixièmes)."""
    debut = instant(m)
    reprise, texte = faire(m, analyser(m, commande))
    return reprise, texte, instant(reprise) - debut


def annonce(texte):
    """La durée que le joueur lit, en dixièmes : « Tu attends … » ou « Au bout de …, tu cesses… »."""
    premiere = texte.splitlines()[0]
    total = 0
    for nombre, unite in re.findall(r"(\d+(?:,\d+)?) (heure|minute|seconde)", premiere):
        total += round(float(nombre.replace(",", ".")) * {"heure": 36000, "minute": 600, "seconde": 10}[unite])
    return total


class CommandeTests(unittest.TestCase):
    def test_les_durees_ecrites(self):
        m = relais()
        cibles = {t: (analyser(m, t) or {}).get("cible") for t in (
            "attendre", "attendre 30 s", "Attendre 10 min", "attendre 1,5 s", "attendre 1 h 30",
            "attendre 2 min 30", "attendre 10")}
        self.assertEqual(cibles, {"attendre": "300", "attendre 30 s": "30", "Attendre 10 min": "600",
                                  "attendre 1,5 s": "1.5", "attendre 1 h 30": "5400",
                                  "attendre 2 min 30": "150", "attendre 10": "600"})
        # Ce que l'analyse ne lit pas sûrement va au MJ, sans durée devinée.
        self.assertIsNone(analyser(m, "attendre que la porte s'ouvre"))
        # Un nom connu mais non perçu est refusé avant l'interprétation de la durée.
        with self.assertRaises(ErreurMonde) as refus:
            analyser(m, "attendre que Gorm revienne")
        self.assertIn("Tu ne vois pas Gorm d'ici", str(refus.exception))
        self.assertIsNone(analyser(m, "attendre 5 min puis sortir"))

    def test_une_duree_refusee_dit_ce_qui_est_attendu(self):
        m = relais()
        for cible in ("bientot", "0", str(13 * 3600)):
            with self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(proposition("attendre", cible))
            self.assertIn("cible vide", refus.exception.attendu)
            self.assertIn(cible, refus.exception.attendu)

    def test_la_proposition_sans_duree_reste_un_bloc_de_cinq_minutes(self):
        # Le MJ, le banc et les scènes de test gardent l'attente d'un bloc, sans interruption.
        m = scene("antichambre", [2, 3], "ouest", "echoppe", [1, 1], "antichambre")
        debut = instant(m)
        reprise, texte = faire(m, proposition("attendre"))
        self.assertEqual(instant(reprise) - debut, 3000)
        self.assertIn("Cinq minutes passent.", texte)


class AttenteTests(unittest.TestCase):
    @patch("donjon.agendas._naissances", return_value=None)
    def test_sans_rien_qui_l_interrompe_le_meme_monde_qu_un_bloc(self, _naissance):
        # Le joueur, seul à la galerie, n'entend que des pas en dessous : rien ne l'interrompt.
        en_bloc, _ = faire(relais(), proposition("attendre"))
        par_tranches, texte, duree = attendre(relais(), "attendre 5 min")
        self.assertEqual(duree, 3000)
        self.assertEqual(texte.splitlines()[0], "Tu attends 5 minutes.")
        self.assertNotIn("cesses d'attendre", texte)
        sans_journal = lambda m: {k: v for k, v in m.data.items() if k not in ("journal", "revision")}
        self.assertEqual(sans_journal(par_tranches), sans_journal(en_bloc))

    def test_quelqu_un_entre_dans_la_piece(self):
        # Cas réel : Gorm vient du refuge par la porte que le joueur regarde.
        m = scene("antichambre", [2, 3], "ouest", "echoppe", [1, 1], "antichambre")
        self.assertFalse(m.visible("marchand"))
        reprise, texte, duree = attendre(m, "attendre 10 min")
        self.assertLess(duree, 6000)
        self.assertEqual(annonce(texte), duree)
        self.assertIn("tu cesses d'attendre", texte.splitlines()[0])
        self.assertIn("Gorm, gardien du relais, entre dans la pièce.", texte)
        self.assertTrue(reprise.visible("marchand"))

    def test_quelqu_un_apercu_un_instant(self):
        # Même nature : Aubin passe dans le champ du joueur assis au refuge, puis en ressort.
        m = relais()
        m.joueur.update(salle="echoppe", position=[1, 5], orientation="est")
        vus = {id for id in pnjs(m) if m.visible(id)}
        reprise, texte, duree = attendre(m, "attendre 1 h")
        self.assertLess(duree, 36000)
        self.assertEqual(annonce(texte), duree)
        lignes = texte.splitlines()
        self.assertTrue(any(l.startswith("Tu aperçois") or l.endswith("entre dans la pièce.") for l in lignes), texte)
        self.assertTrue(any(id not in vus for id in pnjs(reprise) if reprise.visible(id))
                        or any("un instant" in l for l in lignes), texte)

    @patch("donjon.agendas._naissances", return_value=None)
    def test_un_appel_entendu(self, _naissance):
        # Seul à la galerie : des pas en dessous ne l'interrompent pas, l'appel d'un nom si (ou un fracas).
        # La nuit libre n'a plus d'appel en douze heures depuis la part estimée (Gorm, qui achète les
        # planches d'Aubin pour le brasero, reçoit la part et recharge lui-même au lieu d'attendre le
        # service puis de chercher Aubin en l'appelant) : placement d'auteur, Aubin ne sait plus où est
        # Gorm et sa faim montera ; il le cherchera en l'appelant, en dessous, au bout d'une heure et demie.
        m = relais()
        # Aucun secours à Brune ne doit produire un appel avant celui d'Aubin.
        from tests.support import sans_souci
        sans_souci(m)
        croire(m, "aubin", "marchand", "lieu", None, "essai", salle=None, case=None)
        lire(m, "aubin")["besoins"]["faim"] = 60.0
        reprise, texte, duree = attendre(m, "attendre 12 h")
        self.assertLess(duree, 12 * 36000)
        self.assertGreater(duree, 3000)
        self.assertEqual(annonce(texte), duree)
        self.assertTrue(re.search(r"appeler|un appel|grand bruit|: « ", texte), texte)
        self.assertFalse([id for id in pnjs(reprise) if reprise.visible(id)])

    def test_un_instant_le_temps_d_un_pas(self):
        # La touche Espace, saisie vide : 1,5 s, ce que dure un pas.
        reprise, texte, duree = attendre(relais(), "attendre 1,5 s")
        self.assertEqual(duree, 15)
        self.assertEqual(texte.splitlines()[0], "Tu attends 1,5 seconde.")


if __name__ == "__main__":
    unittest.main()
