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
from donjon.commandes import DescripteurPublic, analyser
from donjon.defi import nouveau_defi
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.scene import scene_percue
from donjon.spatial import installer, memoriser
from tests.support import calme, regarder
from donjon.web.pont import PontWeb
from donjon.web.serveur import Serveur
from donjon.gestes_publics import catalogue_public


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


class InterfaceParDefautTests(unittest.TestCase):
    """Dans un terminal, on joue dans le navigateur ; --tui et --console restent au choix."""

    @staticmethod
    def terminal(oui):
        from unittest import mock
        return mock.patch("sys.stdin.isatty", return_value=oui), mock.patch("sys.stdout.isatty", return_value=oui)

    def test_le_navigateur_par_defaut_dans_un_terminal(self):
        from unittest import mock
        with mock.patch.object(jeu, "lancer_web", return_value="web"), \
                mock.patch.object(jeu, "lancer_tui", return_value="tui"):
            for oui, argv, attendu in ((True, [], "web"), (True, ["--tui"], "tui"), (False, ["--web"], "web")):
                entree, sortie = self.terminal(oui)
                with entree, sortie:
                    self.assertEqual(jeu.main(["--defi", "--offline", *argv]), attendu, argv)

    def test_sans_terminal_ou_en_console_la_boucle_ligne_par_ligne(self):
        from unittest import mock
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier, \
                mock.patch.object(jeu, "lancer_web") as web, mock.patch.object(jeu, "lancer_tui") as tui, \
                mock.patch("builtins.print"):
            for oui, argv in ((False, []), (True, ["--console"])):
                entree, sortie = self.terminal(oui)
                with entree, sortie, mock.patch("builtins.input", side_effect=["quitter"]):
                    jeu.main(["--defi", "--offline", "--save", str(Path(dossier) / "defi.json"), *argv])
            web.assert_not_called()
            tui.assert_not_called()


def jouer(monde, commandes):
    for texte in commandes:
        moteur = Moteur(monde)
        moteur.executer(moteur.preparer(DescripteurPublic(texte) if isinstance(texte, dict) else analyser(monde, texte)))


@unittest.skipUnless(shutil.which("node"), "node absent : le script de la page ne peut pas tourner")
class ClicTests(unittest.TestCase):
    """Le clic transmet un geste exact au moteur, après approche si nécessaire."""

    def setUp(self):
        m = nouveau_defi(depart="fixe")
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
                "proposition": "", "scene": scene_percue(m), "catalogue_gestes": catalogue_public()}
        page = Path(jeu.__file__).with_name("donjon") / "web" / "page.html"
        sonde = Path(__file__).with_name("clic_page.js")
        sortie = subprocess.run(["node", str(sonde), str(page)], input=json.dumps(etat), capture_output=True,
                                text=True, encoding="utf-8", check=True).stdout
        self.clic = json.loads(sortie)

    def test_chaque_geste_propose_est_compris_et_a_portee(self):
        gestes = [c for cmds in self.clic["choix"].values() for c in cmds if c != "aller"]
        self.assertTrue(any(isinstance(c, dict) and c["geste"] == "prendre" for c in gestes))
        self.assertTrue(any(isinstance(c, dict) and c["geste"] == "tourner" for c in gestes))
        for texte in gestes:
            essai = Monde(copy.deepcopy(self.monde.data))
            if isinstance(texte, dict):
                verbe, id = texte["geste"], texte["cible"]
            else:  # « Lui parler » reste une saisie de dialogue.
                self.assertIsNotNone(analyser(essai, texte), texte)
                verbe, _, id = texte.partition(" ")
            approche = [] if verbe in ("examiner", "lire", "parler", "tourner") else self.clic["approches"][id]
            self.assertIsNotNone(approche, texte)
            try:
                jouer(essai, ["pas " + d for d in approche] + [texte])
            except ErreurMonde as e:
                self.assertNotIn("Approche-toi", str(e), texte)  # Refusé pour une autre raison, pas la distance.

    def test_le_callback_envoie_le_descripteur_exact_sauf_la_parole_libre(self):
        for clic in self.clic["envoisClic"]:
            self.assertEqual(clic["envoye"], clic["choix"])
            if isinstance(clic["choix"], str):
                self.assertTrue(clic["choix"].startswith("parler "))
            else:
                self.assertEqual(set(clic["choix"]), {"geste", "cible"})

    def test_les_fleches_suivent_le_regard(self):
        from donjon.spatial import VECTEURS
        f = self.clic["fleches"]
        self.assertEqual(f["nord"]["gauche"], "tourner nord-ouest")
        self.assertEqual(f["nord-ouest"]["droite"], "tourner nord")
        self.assertEqual(f["est"]["haut"], "pas est")
        self.assertEqual(f["est"]["alt_haut"], "faufiler est")
        self.assertEqual(f["sud-est"]["bas"], "chasse nord-ouest")
        self.assertEqual(f["nord"]["maj_droite"], "chasse est")
        self.assertEqual(f["nord-est"]["maj_gauche"], "chasse nord-ouest")
        # Au refuge, face à l'est sur une case dégagée : ↑ avance d'un pas devant soi, ↓ recule en
        # gardant le regard, Maj+→ fait un pas de côté, ← tourne d'un huitième ; après rechargement.
        m = self.monde
        m.joueur.update(position=[6, 4], orientation="est")
        for touche, decalage, regard in (("haut", (1, 0), "est"), ("bas", (-1, 0), "est"),
                                         ("maj_droite", (0, 1), "est"), ("gauche", (0, 0), "nord-est")):
            essai = Monde(copy.deepcopy(m.data))
            jouer(essai, [f["est"][touche]])
            with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
                essai.sauver(Path(dossier) / "f.json")
                essai = Monde.charger(Path(dossier) / "f.json")
            self.assertEqual(essai.joueur["position"], [6 + decalage[0], 4 + decalage[1]], touche)
            self.assertEqual(essai.joueur["orientation"], regard, touche)

    def test_espace_attend_un_instant_si_la_saisie_est_vide(self):
        e = self.clic["espace"]
        # Saisie vide ou carte : la commande d'un instant d'attente, sans espace écrite.
        for focus in ("saisie_vide", "carte"):
            self.assertEqual(e[focus], {"envoi": "attendre 1,5 s", "empeche": True}, focus)
        # Saisie commencée, ou un bouton : Espace garde son rôle.
        for focus in ("saisie_ecrite", "bouton"):
            self.assertEqual(e[focus], {"envoi": None, "empeche": False}, focus)
        # La commande envoyée fait passer le temps d'un pas, et le monde rechargé le garde.
        from donjon.temps import instant
        essai = Monde(copy.deepcopy(self.monde.data))
        debut = instant(essai)
        jouer(essai, [e["carte"]["envoi"]])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            essai.sauver(Path(dossier) / "f.json")
            essai = Monde.charger(Path(dossier) / "f.json")
        self.assertEqual(instant(essai) - debut, 15)

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
