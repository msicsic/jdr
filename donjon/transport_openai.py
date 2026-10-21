"""Responses : une connexion réutilisée, le contexte complet à chaque demande."""
from __future__ import annotations

import hashlib
import json
from threading import Lock
import time

from .monde import ErreurMonde

LIMITE_REPONSE = 4_000_000
DUREE_CONNEXION = 55 * 60


def raison_interruption(evenement):
    reponse = evenement.get("response") or {}
    erreur = reponse.get("error") or evenement.get("error") or {}
    incomplete = reponse.get("incomplete_details") or {}
    if isinstance(erreur, dict) and (erreur.get("code") or erreur.get("message")):
        raison = " : ".join(str(x) for x in (erreur.get("code"), erreur.get("message")) if x)
    elif incomplete.get("reason"):
        raison = "incomplète : " + str(incomplete["reason"])
    elif evenement.get("message") or evenement.get("code"):
        raison = " : ".join(str(x) for x in (evenement.get("code"), evenement.get("message")) if x)
    else:
        raison = "raison non précisée par l'API, peut-être une limite d'usage"
    if any(mot in raison.lower() for mot in ("rate", "quota", "limit", "usage")):
        raison += " ; vérifiez les limites du forfait dans ChatGPT > Paramètres > Utilisation"
    return raison[:300]


def lire_evenements(evenements):
    """Un terminal completed est requis ; les deltas seuls ne produisent aucun résultat."""
    elements, types, taille = {}, set(), 0
    for e in evenements:
        if not isinstance(e, dict):
            raise ErreurMonde("Événement du MJ mal formé. Aucune action appliquée.")
        taille += len(json.dumps(e, ensure_ascii=False).encode("utf-8"))
        if taille > LIMITE_REPONSE:
            raise ErreurMonde("Réponse du MJ trop volumineuse. Aucune action appliquée.")
        type_e = e.get("type", "inconnu")
        types.add(type_e)
        if type_e == "response.output_item.done":
            elements[e["output_index"]] = e["item"]
        if type_e == "response.completed":
            r = e["response"]
            if not isinstance(r, dict) or r.get("status") != "completed":
                raise ErreurMonde("Réponse du MJ incomplète. Aucune action appliquée.")
            if not r.get("output") and elements:
                r["output"] = [elements[i] for i in sorted(elements)]
            r["_types_evenements"] = sorted(types)
            return r
        if type_e in ("response.failed", "response.incomplete", "error"):
            raise ErreurMonde("Le MJ ChatGPT n'a pas terminé la réponse (" + raison_interruption(e) + ").")
    raise ErreurMonde("Flux du MJ interrompu avant la fin. Aucune action appliquée.")


class ErreurTransport(RuntimeError):
    def __init__(self, statut=None):
        self.statut = statut
        super().__init__("transport_openai")


def ouvrir_websocket(cle, session, timeout):
    try:
        from websockets.sync.client import connect
    except ImportError:
        raise ErreurMonde("Installez la connexion ChatGPT : python -m pip install -r requirements-chatgpt.txt") from None
    entetes = {"Authorization": "Bearer " + cle, "Content-Type": "application/json"}
    if session:
        entetes["session_id"] = session
    try:
        return connect("wss://api.openai.com/v1/responses", additional_headers=entetes,
                       open_timeout=timeout, close_timeout=2, max_size=LIMITE_REPONSE)
    except Exception as exc:
        # Les exceptions du client peuvent contenir les en-têtes d'authentification.
        statut = getattr(getattr(exc, "response", None), "status_code", None)
        raise ErreurTransport(statut) from None


class WebSocketResponses:
    """Une connexion par MJ ; ses appels et ses audits séquentiels la partagent."""
    def __init__(self):
        self._connexion = None
        self._identite = None
        self._ouverture = 0
        self._verrou = Lock()

    def _fermer(self):
        connexion, self._connexion = self._connexion, None
        self._identite = None
        if connexion is not None:
            try:
                connexion.close()
            except Exception:
                pass

    def fermer(self):
        with self._verrou:
            self._fermer()

    def appeler(self, payload, cle, session, timeout):
        if any(k in payload for k in ("previous_response_id", "conversation", "stream_id")):
            raise ErreurMonde("Le MJ doit envoyer le contexte complet de cet appel.")
        p = {k: v for k, v in payload.items() if k not in ("stream", "background")}
        identite = (hashlib.sha256(cle.encode()).digest(), session)
        with self._verrou:
            limite = time.monotonic() + timeout
            try:
                if self._connexion is not None and (
                        self._identite != identite or time.monotonic() - self._ouverture >= DUREE_CONNEXION
                        or self._connexion.close_code is not None):
                    self._fermer()
                if self._connexion is None:
                    self._connexion = ouvrir_websocket(cle, session, timeout)
                    self._identite, self._ouverture = identite, time.monotonic()
                self._connexion.send(json.dumps({"type": "response.create", **p}, ensure_ascii=False))

                def evenements():
                    reponse_id = None
                    while True:
                        restant = limite - time.monotonic()
                        if restant <= 0:
                            raise TimeoutError()
                        e = json.loads(self._connexion.recv(timeout=restant))
                        if not isinstance(e, dict):
                            raise ValueError()
                        type_e = e.get("type")
                        if type_e == "error" and e.get("status") == 401:
                            raise ErreurTransport(401)
                        if type_e == "response.created":
                            if reponse_id is not None:
                                raise ValueError()
                            reponse_id = e["response"]["id"]
                            if not isinstance(reponse_id, str) or not reponse_id:
                                raise ValueError()
                        if type_e and type_e.startswith("response.output") and reponse_id is None:
                            raise ValueError()
                        if e.get("response_id") is not None and e["response_id"] != reponse_id:
                            raise ValueError()
                        if type_e in ("response.in_progress", "response.completed") and (
                                reponse_id is None or e["response"]["id"] != reponse_id):
                            raise ValueError()
                        yield e

                return lire_evenements(evenements())
            except (ErreurMonde, ErreurTransport):
                self._fermer()
                raise
            except Exception:
                # Une demande éventuellement déjà consommée n'est jamais rejouée ici.
                self._fermer()
                raise ErreurTransport() from None
