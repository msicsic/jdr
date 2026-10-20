"""Jouer dans le navigateur : une vraie partie hors ligne pilotée par le serveur local, comme la page."""
import copy
import http.client
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

import jeu
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.scene import scene_percue
from donjon.spatial import installer, memoriser
from tests.support import calme, regarder
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
                self.assertTrue(any(l.startswith("Tu te tournes vers l'ouest.") for l in lignes), lignes)
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


def jouer(monde, commandes):
    for texte in commandes:
        moteur = Moteur(monde)
        moteur.executer(moteur.preparer(analyser(monde, texte)))


@unittest.skipUnless(shutil.which("node"), "node absent : le script de la page ne peut pas tourner")
class ClicTests(unittest.TestCase):
    """Ce que propose un clic sur la carte est une commande que le moteur comprend, à portée."""

    def setUp(self):
        m = nouveau_defi()
        installer(m)
        calme(m, "marchand", "brune", "ilse", "aubin")
        for id, salle, case in (("marchand", "antichambre", [6, 2]), ("ilse", "antichambre", [7, 5]),
                                ("aubin", "echoppe", [1, 1])):
            m.objets[id]["lieu"] = salle
            placer(m.objets[id], salle, case)
        m.joueur.update(salle="antichambre", position=[1, 3], orientation="ouest")
        memoriser(m)
        m.joueur["orientation"] = "est"
        regarder(m, "marchand", "joueur")
        self.monde = m
        etat = {"type": "etat", "salle": "", "pv": 1, "or": 0, "minutes": 0, "connexion": "", "fiche": "",
                "proposition": "", "scene": scene_percue(m)}
        page = Path(jeu.__file__).with_name("donjon") / "web" / "page.html"
        sonde = Path(__file__).with_name("clic_page.js")
        sortie = subprocess.run(["node", str(sonde), str(page)], input=json.dumps(etat), capture_output=True,
                                text=True, encoding="utf-8", check=True).stdout
        self.clic = json.loads(sortie)

    def test_chaque_geste_propose_est_compris_et_a_portee(self):
        gestes = {c for cmds in self.clic["choix"].values() for c in cmds if c != "aller"}
        self.assertTrue(any(c.startswith("prendre ") for c in gestes))
        self.assertTrue(any(c.startswith("tourner ") for c in gestes))
        for texte in sorted(gestes):
            essai = Monde(copy.deepcopy(self.monde.data))
            self.assertIsNotNone(analyser(essai, texte), texte)
            verbe, _, id = texte.partition(" ")
            approche = [] if verbe in ("examiner", "lire", "parler", "tourner") else self.clic["approches"][id]
            self.assertIsNotNone(approche, texte)
            try:
                jouer(essai, ["pas " + d for d in approche] + [texte])
            except ErreurMonde as e:
                self.assertNotIn("Approche-toi", str(e), texte)  # Refusé pour une autre raison, pas la distance.

    def test_la_marche_par_clic_arrive_et_se_recharge(self):
        m = self.monde
        self.assertNotEqual(self.clic["chemin"], [])
        jouer(m, ["pas " + d for d in self.clic["chemin"]])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            m.sauver(Path(dossier) / "clic.json")
            recharge = Monde.charger(Path(dossier) / "clic.json")
        ox, oy = recharge.data["salles"][recharge.joueur["salle"]]["plan"]["origine"]
        x, y = recharge.joueur["position"]
        self.assertEqual([ox + x, oy + y], self.clic["cible"])


if __name__ == "__main__":
    unittest.main()
