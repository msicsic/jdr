"""OpenAI Responses : clé API HTTP ou forfait ChatGPT WebSocket."""
import json
import os
import urllib.error
import urllib.request

from ..connexion import jeton, modeles
from ..monde import ErreurMonde
from ..transport_openai import WebSocketResponses, ErreurTransport
from .contrat import Fournisseur, Reponse


class OpenAI(Fournisseur):
    def __init__(self, *, chatgpt=False):
        super().__init__()
        self.chatgpt = chatgpt
        self.catalogue_verifie = False
        self._websocket = WebSocketResponses() if chatgpt else None

    def fermer(self):
        if self._websocket is not None:
            self._websocket.fermer()

    def _appeler(self, demande):
        instructions, entree = demande.instructions, demande.entree
        fonction, schema = demande.fonction, demande.schema
        if self.erreur_auth:
            raise ErreurMonde(self.erreur_auth)
        if self.chatgpt and not self.catalogue_verifie:
            disponibles = modeles()
            if demande.modele not in [m["slug"] for m in disponibles]:
                raise ErreurMonde("Ce modèle n'est pas disponible sur ce forfait. Lancez python connexion.py modeles, puis choisissez avec --model.")
            self.catalogue_verifie = True
        cle = jeton() if self.chatgpt else os.environ.get("OPENAI_API_KEY")
        if not cle:
            raise ErreurMonde("OPENAI_API_KEY absente. Les commandes hors ligne restent disponibles (aide).")
        payload = {
            "model": demande.modele,
            "instructions": instructions,
            "input": [{"role": "user", "content": json.dumps(entree, ensure_ascii=False)}],
            "tools": [{"type": "function", "name": fonction,
                       "description": "Répond au joueur ou soumet une manœuvre au moteur, sans modifier le monde.",
                       "parameters": schema, "strict": True}],
            "tool_choice": {"type": "function", "name": fonction},
            "parallel_tool_calls": False,
            "reasoning": {"effort": demande.effort},
            "max_output_tokens": 3000,
            "store": False,
        }
        if demande.cle_cache:
            payload["prompt_cache_key"] = demande.cle_cache
        if self.chatgpt:
            outil = payload["tools"][0]
            payload["tools"] = [{"type": "namespace", "name": "donjon",
                                 "description": "Proposer une action ou une observation au moteur.",
                                 "tools": [outil]}]
            payload["tool_choice"] = "required"
            payload["stream"] = True
            payload.pop("max_output_tokens")  # non accepté par le contrat Sign in with ChatGPT
        requete = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + cle, "Content-Type": "application/json",
                     **({"session_id": demande.cle_cache} if demande.cle_cache else {})},
            method="POST",
        )
        try:
            if self.chatgpt:
                resultat = self._websocket.appeler(payload, cle, demande.cle_cache, demande.timeout)
            else:
                with urllib.request.urlopen(requete, timeout=demande.timeout) as reponse:
                    resultat = json.load(reponse)
        except ErreurTransport as exc:
            if exc.statut == 401:
                self.erreur_auth = ("MJ déconnecté : Reconnectez le forfait : python connexion.py connecter, puis relancez le jeu."
                                    " Aucun nouvel appel ne sera tenté dans cette session.")
                raise ErreurMonde(self.erreur_auth) from None
            if exc.statut:
                raise ErreurMonde(f"MJ indisponible : HTTP {exc.statut}. Aucune action appliquée.") from None
            raise ErreurMonde("Le MJ n'a pas répondu correctement (réseau ou délai). "
                              "Aucune action appliquée. Réessayez ou utilisez les commandes locales.") from None
        except urllib.error.HTTPError as exc:
            # Ne jamais afficher les en-têtes ou une clé dans le journal.
            try:
                code = json.loads(exc.read()).get("error", {}).get("code", "erreur_api")
            except (ValueError, AttributeError):
                code = "erreur_api"
            status = exc.code
            exc.close()
            if status == 401:
                conseil = ("Reconnectez le forfait : python connexion.py connecter, puis relancez le jeu."
                           if self.chatgpt else
                           "La clé API est refusée. Remplacez-la localement, ou utilisez python connexion.py connecter pour le forfait ChatGPT.")
                self.erreur_auth = "MJ déconnecté : " + conseil + " Aucun nouvel appel ne sera tenté dans cette session."
                raise ErreurMonde(self.erreur_auth) from None
            raise ErreurMonde(f"MJ indisponible : HTTP {status} ({code}). "
                              "Monde inchangé ; utilisez contexte, lumière, regarder ou journal.") from None
        except ErreurMonde:
            raise
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise ErreurMonde("Le MJ n'a pas répondu correctement (réseau ou délai). "
                              "Aucune action appliquée. Réessayez ou utilisez les commandes locales.") from None
        if not isinstance(resultat, dict) or not isinstance(resultat.get("output"), list):
            raise ErreurMonde("Réponse du MJ mal formée. Aucune action appliquée.")
        self.dernier_brut = resultat["output"]
        self.derniere_utilisation = resultat.get("usage")
        if resultat.get("status") != "completed":
            raise ErreurMonde("Réponse du MJ incomplète. Aucune action appliquée.")
        self.derniere_sortie = [{k: item.get(k) for k in ("type", "name", "namespace", "status")}
                               for item in resultat["output"] if isinstance(item, dict)]
        if not self.derniere_sortie:
            self.derniere_sortie = [{"types_evenements": resultat.get("_types_evenements", [])}]
        appels = [item for item in resultat["output"] if isinstance(item, dict) and item.get("type") == "function_call"]
        if len(appels) != 1 or appels[0].get("name") != fonction:
            raise ErreurMonde("Le MJ n'a pas fourni une proposition unique. Aucune action appliquée.")
        try:
            p = json.loads(appels[0]["arguments"])
            if not isinstance(p, dict):
                raise ValueError("La proposition doit être un objet")
            return Reponse(p, resultat["output"], self.derniere_utilisation, self.derniere_sortie)
        except (ValueError, KeyError, TypeError):
            raise ErreurMonde("Proposition du MJ illisible. Aucune action appliquée.") from None
