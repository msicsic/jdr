"""Jouer dans le navigateur : une vraie partie hors ligne pilotée par le serveur local, comme la page."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

import jeu
from donjon.monde import Monde
from donjon.web.pont import PontWeb
from donjon.web.serveur import Serveur


class Flux:
    """Lit les événements que reçoit la page."""

    def __init__(self, port):
        self.connexion = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
        self.connexion.request("GET", "/flux")
        self.reponse = self.connexion.getresponse()

    def suivant(self):
        while True:
            ligne = self.reponse.fp.readline().decode("utf-8")
            if ligne.startswith("data: "):
                return json.loads(ligne[6:])

    def jusqu_a_pret(self):
        vus = []
        while True:
            e = self.suivant()
            vus.append(e)
            if e["type"] == "pret":
                return vus


def commande(port, texte, hote="127.0.0.1"):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    c.request("POST", "/commande", json.dumps({"texte": texte}), {"Content-Type": "application/json", "Host": hote})
    r = c.getresponse()
    return r.status, r.read()


class PartieWebTests(unittest.TestCase):
    def test_une_partie_se_joue_et_se_sauve_par_la_page(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            sauvegarde = Path(dossier) / "defi.json"
            pont = PontWeb()
            serveur = Serveur(pont, 0)
            port = serveur.server_address[1]
            threading.Thread(target=serveur.serve_forever, daemon=True).start()
            partie = threading.Thread(target=jeu.main, args=(["--defi", "--offline", "--save", str(sauvegarde)],),
                                      kwargs={"interface": pont}, daemon=True)
            partie.start()
            try:
                flux = Flux(port)
                debut = flux.jusqu_a_pret()
                etat = next(e for e in debut if e["type"] == "etat")
                self.assertEqual(etat["salle"], "Refuge du relais")
                self.assertTrue(etat["scene"]["niveaux"])
                self.assertTrue(any("cloche" in e.get("texte", "") for e in debut if e["type"] == "ligne"))
                self.assertEqual(commande(port, "tourner ouest")[0], 200)
                suite = flux.jusqu_a_pret()
                lignes = [e["texte"] for e in suite if e["type"] == "ligne"]
                self.assertIn("Corvus > tourner ouest", lignes)
                self.assertIn("Tu te tournes vers l'ouest.", lignes)
                self.assertEqual(next(e for e in suite if e["type"] == "etat")["scene"]["joueur"]["orientation"], "ouest")
                self.assertEqual(commande(port, "quitter")[0], 200)
                partie.join(20)
                self.assertFalse(partie.is_alive())
                self.assertEqual(Monde.charger(sauvegarde).joueur["orientation"], "ouest")
            finally:
                pont.termine = True
                serveur.arreter()

    def test_une_commande_a_la_fois_et_d_ici_seulement(self):
        pont = PontWeb()
        self.assertFalse(pont.soumettre("pas est"))  # La boucle n'attend pas encore de commande.
        serveur = Serveur(pont, 0)
        port = serveur.server_address[1]
        threading.Thread(target=serveur.serve_forever, daemon=True).start()
        try:
            self.assertEqual(commande(port, "pas est", hote="exemple.com")[0], 403)
            self.assertEqual(commande(port, "pas est")[0], 409)
        finally:
            serveur.arreter()


if __name__ == "__main__":
    unittest.main()
