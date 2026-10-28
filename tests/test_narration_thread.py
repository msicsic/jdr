"""La narration d'ambiance en thread : elle ne corrompt pas la conversation, se consigne avec son lieu avant
d'être montrée, et le bandeau est toujours libéré."""
import itertools
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import jeu
from donjon.auberge import nouveau_auberge
from donjon.fournisseurs.contrat import Reponse
from donjon.mj import MJ
from donjon.monde import Monde
from donjon.web.pont import PontWeb


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
        index, l'échange de cette action et l'écrasait. L'ambiance est maintenant consignée à part."""
        porte = threading.Event()
        bloquer = []

        def ambiance(numero):
            if bloquer:
                porte.wait(timeout=10)
            return f"Ambiance {numero}."

        self._partie(ambiance)
        for _ in range(12):
            self._jouer("ecouter")
        self.assertTrue(attendre(lambda: len(self.pont.montrees) == 12))
        self.assertEqual(len(self.pont.monde.data["conversation"]), 12)
        bloquer.append(True)
        self._jouer("ecouter")   # sa narration attend
        self._jouer("ecouter")   # l'action suivante est déjà consignée quand la première narration finit
        porte.set()
        # La plus ancienne narration finit la dernière : elle est consignée, mais seule la plus récente parle au bandeau.
        self.assertTrue(attendre(lambda: len(self.pont.monde.data["ambiances"]["salle_commune"]) == 14))
        self.assertEqual(len(self.pont.montrees), 13)
        conversation = self.pont.monde.data["conversation"]
        self.assertEqual(len(conversation), 12)
        for echange in conversation:
            self.assertNotIn("Ambiance", echange["reponse"])
            self.assertTrue(echange["reponse"].strip())
        reprise = self._quitter()
        self.assertEqual([a["texte"] for a in reprise.data["ambiances"]["salle_commune"]][-2:],
                         ["Ambiance 13.", "Ambiance 14."])
        self.assertFalse(any("Ambiance" in e["reponse"] for e in reprise.data["conversation"]))

    def test_ambiance_consignee_avec_son_lieu_avant_d_etre_montree(self):
        self._partie(lambda n: f"Une odeur de cendre, la {n}e fois.")
        self._jouer("ecouter")
        self._jouer("ecouter")
        self.assertTrue(attendre(lambda: len(self.pont.montrees) == 2))
        for vue in self.pont.montrees:
            # Au moment où le bandeau la montre, elle est déjà dans l'état, avec son lieu.
            self.assertIn(vue["texte"], [a["texte"] for a in vue["consignees"]["salle_commune"]])
        reprise = self._quitter()
        self.assertEqual([a["texte"] for a in reprise.data["ambiances"]["salle_commune"]],
                         ["Une odeur de cendre, la 1e fois.", "Une odeur de cendre, la 2e fois."])
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

    def test_une_erreur_inattendue_libere_le_bandeau_sans_etre_masquee(self):
        erreurs = []
        self._partie(lambda n: "inutilisé")
        with patch.object(MJ, "raconter_resultat", side_effect=RuntimeError("défaut")), \
             patch.object(threading, "excepthook", lambda args: erreurs.append(args.exc_value)):
            self._jouer("ecouter")
            self.assertTrue(attendre(lambda: erreurs), "l'erreur doit remonter, pas être avalée")
            self.assertTrue(attendre(lambda: self.pont.derniere_ambiance["statut"] == "pret"))
        self.assertIsInstance(erreurs[0], RuntimeError)
        self.assertTrue(all(not liste for liste in self.pont.monde.data.get("ambiances", {}).values()))
        self._quitter()


if __name__ == "__main__":
    unittest.main()
