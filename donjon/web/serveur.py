"""Le serveur local de la page de jeu : n'écoute que sur 127.0.0.1.

    GET  /          la page
    GET  /flux      les événements de la partie (Server-Sent Events) : lignes du récit, état, prêt/occupé
    POST /commande  {"descripteur": {"geste": "...", "cible": "..."}} ou {"texte": "..."}
                    409 si la précédente n'est pas finie

Une requête dont l'en-tête Host n'est pas local est refusée (une page d'un autre site ne peut
pas piloter la partie).
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

PAGE = Path(__file__).with_name("page.html")
HOTES = ("127.0.0.1", "localhost")


class Gestionnaire(BaseHTTPRequestHandler):
    server_version = "LeSeuil"

    def log_message(self, *args):
        pass  # Le journal du serveur ne pollue pas la console de jeu.

    def _local(self):
        hote = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        if hote not in HOTES:
            self.send_error(403, "Accès local seulement")
            return False
        return True

    def _repondre(self, code, contenu, type_contenu):
        corps = contenu.encode("utf-8") if isinstance(contenu, str) else contenu
        self.send_response(code)
        self.send_header("Content-Type", type_contenu)
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corps)

    def do_GET(self):
        if not self._local():
            return
        if self.path in ("/", "/index.html"):
            self._repondre(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/flux":
            self._flux()
        else:
            self.send_error(404)

    def do_POST(self):
        if not self._local():
            return
        if self.path != "/commande":
            self.send_error(404)
            return
        try:
            longueur = int(self.headers.get("Content-Length", 0))
            entree = json.loads(self.rfile.read(longueur) or b"{}")
            if not isinstance(entree, dict) or set(entree) not in ({"texte"}, {"descripteur"}):
                raise ValueError("Une seule entrée")
            if "descripteur" in entree:
                from ..commandes import DescripteurPublic
                texte = DescripteurPublic(entree["descripteur"])
            else:
                texte = entree["texte"] if isinstance(entree["texte"], str) else ""
        except (ValueError, AttributeError):
            self._repondre(400, json.dumps({"accepte": False}), "application/json")
            return
        accepte = self.server.pont.soumettre(texte)
        self._repondre(200 if accepte else 409, json.dumps({"accepte": accepte}), "application/json")

    def _flux(self):
        pont = self.server.pont
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        file = pont.abonner()
        try:
            while not self.server.arrete:
                evenement = pont.evenement(file, attente=5)
                donnees = ": signe de vie\n\n" if evenement is None else \
                    "data: " + json.dumps(evenement, ensure_ascii=False) + "\n\n"
                self.wfile.write(donnees.encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        finally:
            pont.desabonner(file)


class Serveur(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, pont, port=0):
        super().__init__(("127.0.0.1", port), Gestionnaire)
        self.pont, self.arrete = pont, False

    @property
    def adresse(self):
        return f"http://127.0.0.1:{self.server_address[1]}/"

    def arreter(self):
        self.arrete = True
        self.shutdown()
        self.server_close()
