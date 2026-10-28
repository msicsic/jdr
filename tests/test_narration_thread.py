"""La narration d'ambiance en thread : elle ne corrompt pas la conversation, se consigne avec son lieu avant
d'être montrée, et le bandeau est toujours libéré."""
import io
import itertools
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import jeu
from donjon.auberge import nouveau_auberge
from donjon.fournisseurs.contrat import ErreurFournisseur, Reponse
from donjon.mj import MJ
from donjon.monde import Monde
from donjon.web.pont import PontWeb

_ROMAIN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV")
_FOIS = ("première", "seconde", "troisième", "quatrième")


class PontEspion(PontWeb):
    """Un pont qui garde le monde de la partie et l'état des ambiances au moment où le bandeau les montre."""

    def __init__(self):
        super().__init__()
        self.monde = None
        self.montrees = []

    def rafraichir(self, monde, pending, mj):
        self.monde = monde
        super().rafraichir(monde, pending, mj)

    def ambiance(self, statut="pret", texte="", duree=None):
        if statut == "pret" and texte:
            self.montrees.append({"texte": texte, "consignees": {salle: [dict(a) for a in liste]
                                                                 for salle, liste in self.monde.data["ambiances"].items()}})
        super().ambiance(statut, texte, duree)


def attendre(condition, delai=15):
    fin = time.time() + delai
    while time.time() < fin:
        if condition():
            return True
        time.sleep(0.02)
    return False


class NarrationThreadTests(unittest.TestCase):
    def _partie(self, ambiance):
        """Lance une partie réelle (jeu.main) dont le narrateur est ``ambiance(numero) -> texte``."""
        self.dossier = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.dossier.cleanup)
        self.sauvegarde = Path(self.dossier.name) / "auberge.json"
        m = nouveau_auberge()
        m.joueur.update(salle="salle_commune", position=[4, 5], orientation="nord")
        m.sauver(self.sauvegarde)
        numeros = itertools.count(1)

        def faux_appeler(demande):
            self.assertEqual(demande.fonction, "narrer_ambiance")
            return Reponse(arguments={"texte": ambiance(next(numeros))}, brut={}, utilisation={})

        self.pont = PontEspion()
        patcher = patch("donjon.fournisseurs.contrat.Fournisseur.appeler", side_effect=faux_appeler)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.partie = threading.Thread(
            target=jeu.main, args=(["--auberge", "--connexion", "local", "--save", str(self.sauvegarde)],),
            kwargs={"interface": self.pont}, daemon=True)
        self.partie.start()
        self.addCleanup(lambda: setattr(self.pont, "termine", True))

    def _jouer(self, texte):
        self.assertTrue(attendre(lambda: not self.pont.occupe), "la boucle n'attend pas de commande")
        self.assertTrue(self.pont.soumettre(texte))
        self.assertTrue(attendre(lambda: not self.pont.occupe), f"« {texte} » ne se termine pas")

    def _quitter(self):
        self.assertTrue(attendre(lambda: not self.pont.occupe), "la boucle n'attend pas de commande")
        self.assertTrue(self.pont.soumettre("quitter"))
        self.partie.join(20)
        self.assertFalse(self.partie.is_alive())
        return Monde.charger(self.sauvegarde)

    def test_narration_tardive_n_ecrase_pas_la_conversation_pleine(self):
        """La mémoire garde 12 échanges : une narration qui finit après l'action suivante visait, par son
        index, l'échange de cette action et l'écrasait. L'ambiance est maintenant consignée à part, et une
        ambiance périmée (non montrée) n'est jamais consignée."""
        porte = threading.Event()
        bloque_13 = threading.Event()

        def ambiance(numero):
            if numero == 13:
                bloque_13.set()
                porte.wait(timeout=10)
            return f"Ambiance {_ROMAIN[numero - 1]}."

        self._partie(ambiance)
        for _ in range(12):
            self._jouer("ecouter")
        self.assertTrue(attendre(lambda: len(self.pont.montrees) == 12))
        self.assertEqual(len(self.pont.monde.data["conversation"]), 12)
        self._jouer("ecouter")   # sa narration (n° 13) attend sur porte
        self.assertTrue(bloque_13.wait(timeout=5))
        self._jouer("ecouter")   # l'action suivante (n° 14) est lancée et finit avant la 13
        self.assertTrue(attendre(lambda: len(self.pont.montrees) == 13))
        porte.set()
        # La narration 13 (périmée) se termine sans écraser la conversation ni être consignée dans ambiances.
        time.sleep(0.1)
        self.assertEqual(len(self.pont.monde.data["ambiances"]["salle_commune"]), 13)
        self.assertEqual(len(self.pont.montrees), 13)
        conversation = self.pont.monde.data["conversation"]
        self.assertEqual(len(conversation), 12)
        for echange in conversation:
            self.assertNotIn("Ambiance", echange["reponse"])
            self.assertTrue(echange["reponse"].strip())
        reprise = self._quitter()
        self.assertEqual([a["texte"] for a in reprise.data["ambiances"]["salle_commune"]][-2:],
                         ["Ambiance XII.", "Ambiance XIV."])
        self.assertFalse(any("Ambiance" in e["reponse"] for e in reprise.data["conversation"]))

    def test_ambiance_consignee_avec_son_lieu_avant_d_etre_montree(self):
        self._partie(lambda n: f"Une odeur de cendre, la {_FOIS[n - 1]} fois.")
        self._jouer("ecouter")
        self._jouer("ecouter")
        self.assertTrue(attendre(lambda: len(self.pont.montrees) == 2))
        for vue in self.pont.montrees:
            # Au moment où le bandeau la montre, elle est déjà dans l'état, avec son lieu.
            self.assertIn(vue["texte"], [a["texte"] for a in vue["consignees"]["salle_commune"]])
        reprise = self._quitter()
        self.assertEqual([a["texte"] for a in reprise.data["ambiances"]["salle_commune"]],
                         ["Une odeur de cendre, la première fois.", "Une odeur de cendre, la seconde fois."])
        # Les autres lieux n'ont rien reçu.
        self.assertTrue(all(not liste for salle, liste in reprise.data["ambiances"].items() if salle != "salle_commune"))

    def test_narration_vide_ne_montre_ni_ne_consigne_rien(self):
        """Pas de repli : la réplique d'un PNJ ou le résultat du moteur ne sont jamais recopiés en « ambiance »."""
        self._partie(lambda n: "")
        self._jouer("ecouter")
        self.assertTrue(attendre(lambda: self.pont.derniere_ambiance["statut"] == "pret"))
        self.assertEqual(self.pont.derniere_ambiance["texte"], "")
        self.assertTrue(all(not liste for liste in self.pont.monde.data.get("ambiances", {}).values()))
        self.assertTrue(all(not liste for liste in self._quitter().data.get("ambiances", {}).values()))

    def test_panne_fournisseur_libere_le_bandeau_et_trace_sans_masquer_resultat(self):
        """Une panne réseau/401 du fournisseur de narration est tracée sur stderr, libère le bandeau,
        ne consigne aucune ambiance et laisse le résultat mécanique affiché dans la conversation."""
        def en_panne(_numero):
            raise ErreurFournisseur("HTTP 401 : jeton expiré")

        stderr_capture = io.StringIO()
        self._partie(en_panne)
        with patch("sys.stderr", stderr_capture):
            self._jouer("ecouter")
            self.assertTrue(attendre(lambda: self.pont.derniere_ambiance["statut"] == "pret"))
            self.assertTrue(attendre(lambda: "401" in stderr_capture.getvalue()))
        self.assertEqual(self.pont.derniere_ambiance["texte"], "")
        self.assertIn("[narrateur]", stderr_capture.getvalue())
        self.assertTrue(all(not liste for liste in self.pont.monde.data.get("ambiances", {}).values()))
        reprise = self._quitter()
        self.assertEqual(len(reprise.data["conversation"]), 1)
        self.assertTrue(reprise.data["conversation"][0]["reponse"].strip())

    def test_une_erreur_inattendue_libere_le_bandeau_sans_etre_masquee(self):
        """Un bug de programmation (AttributeError) dans le narrateur remonte jusqu'au thread sans être avalé
        par narrer, tout en libérant le bandeau dans finally."""
        erreurs = []

        def bogue(_numero):
            raise AttributeError("champ manquant simulé")

        self._partie(bogue)
        with patch.object(threading, "excepthook", lambda args: erreurs.append(args.exc_value)):
            self._jouer("ecouter")
            self.assertTrue(attendre(lambda: erreurs), "l'erreur de programmation doit remonter jusqu'au thread")
            self.assertTrue(attendre(lambda: self.pont.derniere_ambiance["statut"] == "pret"))
        self.assertIsInstance(erreurs[0], AttributeError)
        self.assertTrue(all(not liste for liste in self.pont.monde.data.get("ambiances", {}).values()))
        self._quitter()

    def test_narration_plus_recente_montree_abandonne_la_precedente(self):
        """Deux actions : la 1re narration est bloquée, la 2e finit et s'affiche, puis la 1re est libérée.
        La 1re n'écrase pas la 2e, le bandeau garde la plus récente et seule la 2e est consignée."""
        porte = threading.Event()
        bloque_1 = threading.Event()

        def ambiance(numero):
            if numero == 1:
                bloque_1.set()
                porte.wait(timeout=10)
            return f"Ambiance {_ROMAIN[numero - 1]}."

        self._partie(ambiance)
        self._jouer("ecouter")
        self.assertTrue(bloque_1.wait(timeout=5))
        self._jouer("ecouter")
        self.assertTrue(attendre(lambda: len(self.pont.montrees) == 1))
        self.assertEqual(self.pont.derniere_ambiance["texte"], "Ambiance II.")
        porte.set()
        time.sleep(0.1)
        self.assertEqual([v["texte"] for v in self.pont.montrees], ["Ambiance II."])
        self.assertEqual(self.pont.derniere_ambiance["texte"], "Ambiance II.")
        self.assertEqual([a["texte"] for a in self.pont.monde.data["ambiances"]["salle_commune"]], ["Ambiance II."])
        reprise = self._quitter()
        self.assertEqual([a["texte"] for a in reprise.data["ambiances"]["salle_commune"]], ["Ambiance II."])

    def test_premiere_ambiance_seule_disponible_n_est_pas_perdue(self):
        """Deux actions : la 1re narration est bloquée, la 2e revient vide avant que la 1re ne se termine.
        Puisque la 2e n'a rien montré (derniere_montree reste 0), la 1re est montrée et consignée à sa fin."""
        porte = threading.Event()
        bloque_1 = threading.Event()
        fin_2 = threading.Event()

        def ambiance(numero):
            if numero == 1:
                bloque_1.set()
                porte.wait(timeout=10)
                return "Ambiance I."
            fin_2.set()
            return ""

        self._partie(ambiance)
        self._jouer("ecouter")
        self.assertTrue(bloque_1.wait(timeout=5))
        self._jouer("ecouter")
        self.assertTrue(fin_2.wait(timeout=5))
        self.assertTrue(attendre(lambda: self.pont.derniere_ambiance["statut"] == "pret"))
        porte.set()
        self.assertTrue(attendre(lambda: len(self.pont.montrees) == 1))
        self.assertEqual([v["texte"] for v in self.pont.montrees], ["Ambiance I."])
        self.assertEqual(self.pont.derniere_ambiance["texte"], "Ambiance I.")
        self.assertEqual([a["texte"] for a in self.pont.monde.data["ambiances"]["salle_commune"]], ["Ambiance I."])
        reprise = self._quitter()
        self.assertEqual([a["texte"] for a in reprise.data["ambiances"]["salle_commune"]], ["Ambiance I."])


if __name__ == "__main__":
    unittest.main()
