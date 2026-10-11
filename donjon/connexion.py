"""Sign in with ChatGPT pour une application locale ; aucun secret dans les sauvegardes.

JWT vérifié avec PyJWT[crypto]. Jetons protégés par DPAPI sous Windows et fichier
0600 dans un répertoire 0700 sur Unix. Le coffre sérialise login, refresh et logout.
"""
from __future__ import annotations

import base64
from contextlib import contextmanager
import ctypes
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import secrets
from threading import Lock
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import webbrowser

from .monde import ErreurMonde

ISSUER = "https://auth.openai.com"
AUTHORIZE = ISSUER + "/api/accounts/authorize"
TOKEN = ISSUER + "/api/accounts/oauth/token"
RESOURCE = "https://api.openai.com/v1"
SCOPES = "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct"
DOSSIER = Path(__file__).resolve().parents[1] / ".seuil-auth"
_ACCES_JETON = Lock()


def appeler_json(url, formulaire=None, bearer=None):
    headers = {"Accept": "application/json"}
    if bearer:
        headers["Authorization"] = "Bearer " + bearer
    data = None
    if formulaire is not None:
        data = urllib.parse.urlencode(formulaire).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=30) as r:
            contenu = r.read()
            return json.loads(contenu) if contenu else {}
    except urllib.error.HTTPError as exc:
        status = exc.code
        exc.close()
        raise ErreurMonde(f"Connexion ChatGPT refusée (HTTP {status}). Réessayez la connexion ou vérifiez l'accès de votre compte.") from None
    except (OSError, ValueError):
        raise ErreurMonde("Connexion ChatGPT impossible : réseau, délai ou réponse invalide.") from None


def _dpapi(contenu, proteger):
    from ctypes import wintypes
    class Blob(ctypes.Structure):
        _fields_ = [("taille", wintypes.DWORD), ("octets", ctypes.POINTER(ctypes.c_ubyte))]
    buf = (ctypes.c_ubyte * len(contenu)).from_buffer_copy(contenu)
    entree = Blob(len(contenu), ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)))
    sortie = Blob()
    crypto = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    fonction = crypto.CryptProtectData if proteger else crypto.CryptUnprotectData
    fonction.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob),
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    fonction.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if not fonction(ctypes.byref(entree), None, None, None, None, 1, ctypes.byref(sortie)):
        raise ErreurMonde("Le coffre ChatGPT n'est pas accessible à ce compte Windows.")
    try:
        return ctypes.string_at(sortie.octets, sortie.taille)
    finally:
        kernel.LocalFree(sortie.octets)


class Coffre:
    def __init__(self, dossier=DOSSIER):
        self.dossier = Path(dossier)
        self.fichier = self.dossier / "comptes.bin"

    @contextmanager
    def verrou(self):
        self.dossier.mkdir(mode=0o700, parents=True, exist_ok=True)
        verrou = self.dossier / "connexion.lock"
        try:
            fd = os.open(verrou, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise ErreurMonde("Une connexion ChatGPT est déjà en cours. Fermez-la avant de réessayer.") from None
        try:
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            yield
        finally:
            verrou.unlink(missing_ok=True)

    def lire(self):
        if not self.fichier.exists():
            return {"host": "urn:uuid:" + str(uuid.uuid4()), "actif": None, "comptes": {}}
        try:
            brut = self.fichier.read_bytes()
            if os.name == "nt":
                brut = _dpapi(brut, False)
            return json.loads(brut)
        except (OSError, ValueError):
            raise ErreurMonde("Coffre ChatGPT illisible ; aucune clé API ne sera utilisée à sa place.") from None

    def ecrire(self, data):
        self.dossier.mkdir(mode=0o700, parents=True, exist_ok=True)
        brut = json.dumps(data).encode()
        if os.name == "nt":
            brut = _dpapi(brut, True)
        tmp = self.dossier / (str(uuid.uuid4()) + ".tmp")
        fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(brut)
            os.replace(tmp, self.fichier)
        finally:
            tmp.unlink(missing_ok=True)

    def compte(self):
        data = self.lire()
        return data["comptes"].get(data["actif"])


def verifier_identite(token, client_id, nonce, jwks):
    try:
        import jwt
    except ImportError:
        raise ErreurMonde("Installez la dépendance de connexion : python -m pip install -r requirements-chatgpt.txt") from None
    try:
        entete = jwt.get_unverified_header(token)
        if entete.get("alg") not in ("RS256", "ES256"):
            raise ValueError("Algorithme non accepté")
        cle = next(k for k in jwks["keys"] if k.get("kid") == entete.get("kid"))
        identite = jwt.decode(token, jwt.PyJWK.from_dict(cle).key,
            algorithms=[entete["alg"]], issuer=ISSUER, audience=client_id, leeway=5,
            options={"require": ["sub", "exp", "iat", "nonce", "iss", "aud"]})
        if not isinstance(identite["sub"], str) or not identite["sub"] or not secrets.compare_digest(identite["nonce"], nonce):
            raise ValueError("Identité invalide")
        return identite
    except (jwt.PyJWTError, KeyError, TypeError, ValueError, StopIteration):
        raise ErreurMonde("L'identité ChatGPT n'a pas pu être vérifiée. Aucune session activée.") from None


def lire_callback(parametres, state, client_id):
    def unique(nom):
        valeurs = parametres.get(nom, [])
        return valeurs[0] if len(valeurs) == 1 else ""
    if not secrets.compare_digest(unique("state"), state):
        raise ErreurMonde("Retour de connexion non vérifié (state).")
    if "error" in parametres:
        raise ErreurMonde("Connexion ou utilisation du forfait refusée. Aucun compte n'a été activé.")
    recu = unique("client_id")
    if client_id == "dynamic_agent_client":
        if not recu.startswith("oaiapp_"):
            raise ErreurMonde("Inscription ChatGPT incomplète : identifiant du client absent.")
        client_id = recu
    elif recu and recu != client_id:
        raise ErreurMonde("Le retour désigne un autre compte ; connexion rejetée.")
    code = unique("code")
    if not code:
        raise ErreurMonde("Code de connexion absent.")
    return client_id, code


def _fusionner_jetons(compte, tokens):
    scopes = tokens.get("scope", " ".join(compte.get("scopes", []))).split()
    if not {"resource.invoke", "chatgpt.tokens.use.direct"}.issubset(scopes):
        raise ErreurMonde("L'autorisation d'utiliser le forfait ChatGPT n'a pas été accordée.")
    if not isinstance(tokens.get("access_token"), str) or not tokens["access_token"]:
        raise ErreurMonde("Jeton d'accès absent.")
    if tokens.get("token_type", "").lower() != "bearer":
        raise ErreurMonde("Type de jeton inattendu.")
    try:
        expires = int(tokens["expires_in"])
        if expires <= 0:
            raise ValueError()
    except (KeyError, ValueError, TypeError):
        raise ErreurMonde("Expiration du jeton absente ou invalide.") from None
    nouveau = dict(compte)
    for cle in ("access_token", "refresh_token", "id_token"):
        if cle in tokens:
            nouveau[cle] = tokens[cle]
    nouveau.update(scopes=scopes, expires_at=time.time() + expires)
    return nouveau


def connecter(coffre=None, nouveau=False, compte_id=None, timeout=300, afficher=print):
    coffre = coffre or Coffre()
    # Tester la dépendance avant d'ouvrir une session navigateur.
    try:
        import jwt  # noqa: F401
    except ImportError:
        raise ErreurMonde("Installez : python -m pip install -r requirements-chatgpt.txt") from None
    with coffre.verrou():
        data = coffre.lire()
        selection = compte_id or data["actif"]
        if compte_id and compte_id not in data["comptes"]:
            raise ErreurMonde("Inscription inconnue. Consultez python connexion.py statut.")
        if not nouveau and not selection and data["comptes"]:
            if len(data["comptes"]) != 1:
                raise ErreurMonde("Choisissez une inscription avec --compte (liste : python connexion.py statut).")
            selection = next(iter(data["comptes"]))
        ancien = None if nouveau else data["comptes"].get(selection)
        client_id = ancien["client_id"] if ancien else "dynamic_agent_client"
        coffre.ecrire(data)  # identité de l'installation persistée AVANT la connexion
        state, nonce, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(32), secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
        retour = {}
        class Callback(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass  # l'URL contient un code OAuth, ne jamais la journaliser
            def do_GET(self):
                url = urllib.parse.urlsplit(self.path)
                if url.path != "/auth/callback":
                    self.send_error(404)
                    return
                params = urllib.parse.parse_qs(url.query)
                if params.get("state") != [state]:
                    self.send_error(400, "Connexion non verifiee")
                    return
                retour.update(params)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write("Retour reçu. Revenez au terminal pour le résultat de la vérification.".encode())
        with HTTPServer(("127.0.0.1", 0), Callback) as serveur:
            redirect = f"http://127.0.0.1:{serveur.server_port}/auth/callback"
            params = dict(client_id=client_id, ext_agent_host_id=data["host"], response_type="code",
                          redirect_uri=redirect, scope=SCOPES, resource=RESOURCE, state=state,
                          nonce=nonce, code_challenge_method="S256", code_challenge=challenge)
            if ancien:
                if ancien.get("id_token"):
                    params["id_token_hint"] = ancien["id_token"]
            else:
                params["agent_name_hint"] = "Le Seuil"
            afficher("Continue with ChatGPT — autorisez Le Seuil dans le navigateur. Aucun forfait n'est acheté.", flush=True)
            if not webbrowser.open(AUTHORIZE + "?" + urllib.parse.urlencode(params)):
                raise ErreurMonde("Impossible d'ouvrir le navigateur par défaut.")
            serveur.timeout = 1
            fin = time.monotonic() + timeout
            while not retour and time.monotonic() < fin:
                serveur.handle_request()
        if not retour:
            raise ErreurMonde("Connexion expirée ; relancez connecter.")
        client_id, code = lire_callback(retour, state, client_id)
        base = ancien or {"client_id": client_id, "subject": None}
        data["comptes"].setdefault(client_id, base)
        coffre.ecrire(data)  # conserver l'inscription pour reprendre un échange interrompu
        tokens = appeler_json(TOKEN, dict(grant_type="authorization_code", client_id=client_id,
            code=code, code_verifier=verifier, redirect_uri=redirect, resource=RESOURCE))
        identite = verifier_identite(tokens.get("id_token", ""), client_id, nonce,
                                     appeler_json(ISSUER + "/.well-known/jwks.json"))
        if ancien and ancien.get("subject") and identite["sub"] != ancien["subject"]:
            raise ErreurMonde("L'identité a changé : choisissez une nouvelle inscription.")
        if "scope" not in tokens:
            raise ErreurMonde("Les autorisations accordées ne sont pas présentes dans la réponse de connexion.")
        compte = _fusionner_jetons(base, tokens)
        compte.update(subject=identite["sub"], issuer=identite["iss"], email=identite.get("email", "compte ChatGPT"))
        data["comptes"][client_id] = compte
        data["actif"] = client_id
        coffre.ecrire(data)
        afficher("Connexion vérifiée. Le Seuil utilisera votre forfait ChatGPT, selon ses limites.")


def jeton(coffre=None):
    coffre = coffre or Coffre()
    # Les deux MJ partagent le coffre : sérialiser lecture/refresh dans ce processus,
    # puis libérer le verrou avant les requêtes d'inférence parallèles.
    with _ACCES_JETON, coffre.verrou():
        data = coffre.lire()
        compte = data["comptes"].get(data["actif"])
        if not compte or not compte.get("access_token"):
            raise ErreurMonde("Connectez le jeu : python connexion.py connecter")
        if compte["expires_at"] <= time.time() + 60:
            if not compte.get("refresh_token"):
                raise ErreurMonde("Session ChatGPT expirée : python connexion.py connecter")
            tokens = appeler_json(TOKEN, dict(grant_type="refresh_token", client_id=compte["client_id"],
                refresh_token=compte["refresh_token"], resource=RESOURCE))
            compte = _fusionner_jetons(compte, tokens)
            data["comptes"][data["actif"]] = compte
            coffre.ecrire(data)
        return compte["access_token"]


def modeles(coffre=None):
    resultat = appeler_json(RESOURCE + "/models", bearer=jeton(coffre))
    return [m for m in resultat.get("models", []) if m.get("visibility") == "list"]


def deconnecter(coffre=None):
    coffre = coffre or Coffre()
    confirme = True
    with coffre.verrou():
        data = coffre.lire()
        compte = data["comptes"].get(data["actif"])
        if not compte:
            return
        if compte.get("refresh_token"):
            try:
                discovery = appeler_json(ISSUER + "/.well-known/openid-configuration")
                endpoint = discovery["revocation_endpoint"]
                if not endpoint.startswith(ISSUER + "/"):
                    raise ErreurMonde("Endpoint de révocation inattendu.")
                appeler_json(endpoint, dict(token=compte["refresh_token"], token_type_hint="refresh_token", client_id=compte["client_id"]))
            except (ErreurMonde, KeyError):
                confirme = False
        for cle in ("access_token", "refresh_token", "id_token", "expires_at"):
            compte.pop(cle, None)
        coffre.ecrire(data)
    print("Session locale fermée." + ("" if confirme else " Révocation distante non confirmée ; déconnectez Le Seuil dans les paramètres ChatGPT."))
