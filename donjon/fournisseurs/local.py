"""Fournisseur LLM local : API native Ollama (/api/chat) et serveurs compatibles OpenAI (/v1/chat/completions).

- Pour le compilateur et le narrateur découplés sur Ollama (port 11434 par défaut), utilise ``/api/chat``
  avec ``format`` (grammaire JSON), ``think`` et ``options.num_ctx = 32768``.
- Pour ``llama-server`` / vLLM / SGLang (``/v1/chat/completions``) et la voie complète, passe
  ``response_format``, ``cache_prompt``, ``id_slot`` et ``prompt_cache_key``.
"""
import json
import os
import re
import urllib.error
import urllib.request

from ..config import MODELE_LOCAL, URL_LOCAL_DEFAUT, URL_OLLAMA_DEFAUT
from ..monde import ErreurMonde
from ..sources import slot_cache, voie_cache
from .contrat import ErreurFournisseur, Fournisseur, Reponse
from .schema import mutualiser

CONTEXTE_DEFAUT = 32768
FONCTIONS_DECOUPLEES = ("compiler_intention", "etablir_faits", "narrer_ambiance", "repondre_dialogue")


def normaliser_url(url=None):
    """Accepte une URL de base (http://127.0.0.1:8080, .../v1) ou l'URL complète chat/completions."""
    base = (url or os.environ.get("LOCAL_LLM_URL") or URL_LOCAL_DEFAUT).strip().rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def extraire_json(texte):
    """Extrait l'objet JSON d'une réponse texte (après retrait d'un éventuel bloc <think>...</think>)."""
    if not isinstance(texte, str):
        raise ValueError("Contenu non textuel")
    nettoye = re.sub(r"^\s*<think>.*?</think>\s*", "", texte, flags=re.DOTALL).strip()
    if nettoye.startswith("```"):
        nettoye = re.sub(r"^```(?:json)?\s*|\s*```$", "", nettoye).strip()
    objet = json.loads(nettoye)
    if not isinstance(objet, dict):
        raise ValueError("La réponse JSON doit être un objet")
    return objet


def enrichir_usage(resultat):
    """Unifie les compteurs de cache KV (OpenAI ``cached_tokens`` et llama.cpp ``timings.cache_n``)."""
    usage = dict(resultat.get("usage") or {})
    timings = resultat.get("timings")
    if isinstance(timings, dict):
        usage.setdefault("timings", timings)
        cache_n = timings.get("cache_n")
        if isinstance(cache_n, int):
            details = dict(usage.get("prompt_tokens_details") or {})
            details.setdefault("cached_tokens", cache_n)
            usage["prompt_tokens_details"] = details
            if "prompt_tokens" in usage and "prompt_n" in timings:
                usage.setdefault("prompt_eval_tokens", timings["prompt_n"])
    return usage or None


class Local(Fournisseur):
    # ``format`` (Ollama) et ``response_format`` (llama.cpp) sont des grammaires :
    # le modèle ne lit pas les descriptions du schéma.
    schema_lu = False

    def __init__(self, url=None, cle=None, contexte=None):
        super().__init__()
        self.url = url
        self.cle = cle
        self.contexte = contexte or int(os.environ.get("LOCAL_LLM_CTX") or CONTEXTE_DEFAUT)

    def _est_ollama_natif(self, demande):
        url_cfg = (self.url or os.environ.get("LOCAL_LLM_URL") or "").strip().rstrip("/")
        if url_cfg.endswith("/api/chat"):
            return True
        if "/v1" in url_cfg or ":8080" in url_cfg:
            return False
        return demande.fonction in FONCTIONS_DECOUPLEES or ":11434" in url_cfg

    def _appeler_ollama(self, demande):
        base = (self.url or os.environ.get("LOCAL_LLM_URL") or URL_OLLAMA_DEFAUT).strip().rstrip("/")
        url = base if base.endswith("/api/chat") else base + "/api/chat"
        payload = {
            "model": demande.modele or os.environ.get("LOCAL_LLM_MODEL") or MODELE_LOCAL,
            "messages": [{"role": "system", "content": demande.instructions},
                         {"role": "user", "content": json.dumps(demande.entree, ensure_ascii=False)}],
            "format": mutualiser(demande.schema),
            "stream": False,
            "think": demande.effort != "none",
            "options": {"temperature": 0.2, "repeat_penalty": 1.15, "num_ctx": self.contexte, "num_predict": 4096},
            "keep_alive": "10m",
        }
        requete = urllib.request.Request(url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(requete, timeout=demande.timeout) as flux:
                resultat = json.load(flux)
        except urllib.error.HTTPError as exc:
            statut = exc.code
            detail = exc.read().decode("utf-8", "replace")[:300]
            exc.close()
            raise ErreurMonde(f"MJ local indisponible : HTTP {statut} {detail}. Aucune action appliquée.") from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise ErreurMonde("Le serveur LLM local n'a pas répondu (Ollama lancé ? LOCAL_LLM_URL). "
                              "Aucune action appliquée.") from None
        message = resultat.get("message") if isinstance(resultat, dict) else None
        if not isinstance(message, dict):
            raise ErreurMonde("Réponse du LLM local mal formée. Aucune action appliquée.")
        entree, sortie_n = resultat.get("prompt_eval_count") or 0, resultat.get("eval_count") or 0
        usage = {"input_tokens": entree, "output_tokens": sortie_n, "total_tokens": entree + sortie_n,
                 "duree_totale_s": round((resultat.get("total_duration") or 0) / 1e9, 2),
                 "reflexion": message.get("thinking") or None}
        brut = [{"finish_reason": resultat.get("done_reason"), "message": message}]
        if resultat.get("done_reason") == "length":
            raise ErreurFournisseur("Réponse du LLM local incomplète (num_predict atteint). Aucune action appliquée.",
                                    brut=brut, utilisation=usage)
        try:
            arguments = extraire_json(message.get("content") or "")
        except (ValueError, TypeError) as exc:
            raise ErreurFournisseur("Proposition du LLM local illisible. Aucune action appliquée.",
                                    brut=brut, utilisation=usage) from exc
        return Reponse(arguments, brut, usage, [{"type": "message", "role": "assistant"}])

    def _appeler(self, demande):
        if self.erreur_auth:
            raise ErreurMonde(self.erreur_auth)
        if self._est_ollama_natif(demande):
            return self._appeler_ollama(demande)
        url = normaliser_url(self.url)
        cle = self.cle or os.environ.get("LOCAL_LLM_KEY") or "local"
        modele = demande.modele or os.environ.get("LOCAL_LLM_MODEL") or MODELE_LOCAL
        voie = voie_cache(demande.fonction, demande.entree,
            demande.schema.get("properties", {}).get("mode", {}).get("enum") != ["dialogue"])
        slot = slot_cache(voie)
        cle_cache = f"{demande.cle_cache}:{voie}" if demande.cle_cache else voie
        schema_compact = mutualiser(demande.schema)
        payload = {
            "model": modele,
            "messages": [
                {"role": "system", "content": demande.instructions},
                {"role": "user", "content": json.dumps(demande.entree, ensure_ascii=False)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": demande.fonction,
                    "strict": True,
                    "schema": schema_compact,
                },
            },
            "temperature": 0.2,
            "max_tokens": 2048,
            "stream": False,
            "cache_prompt": True,
            "id_slot": slot,
            "prompt_cache_key": cle_cache,
        }
        if demande.effort == "none":
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        requete = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {cle}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(requete, timeout=demande.timeout) as reponse:
                resultat = json.load(reponse)
        except urllib.error.HTTPError as exc:
            status = exc.code
            exc.close()
            if status == 401:
                self.erreur_auth = "MJ local déconnecté : clé LOCAL_LLM_KEY refusée (HTTP 401)."
                raise ErreurMonde(self.erreur_auth) from None
            raise ErreurMonde(f"MJ local indisponible : HTTP {status}. Aucune action appliquée.") from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise ErreurMonde("Le serveur LLM local n'a pas répondu (vérifiez LOCAL_LLM_URL ou lancez llama-server). "
                              "Aucune action appliquée.") from None
        if not isinstance(resultat, dict) or not isinstance(resultat.get("choices"), list) or not resultat["choices"]:
            raise ErreurMonde("Réponse du LLM local mal formée. Aucune action appliquée.")
        usage = enrichir_usage(resultat)
        choix = resultat["choices"][0] if isinstance(resultat["choices"][0], dict) else {}
        message = choix.get("message") if isinstance(choix.get("message"), dict) else {}
        brut = [choix]
        raison = choix.get("finish_reason")
        if raison == "length":
            raise ErreurFournisseur("Réponse du LLM local incomplète (max_tokens atteint). Aucune action appliquée.",
                                    brut=brut, utilisation=usage)
        contenu = message.get("content")
        if not contenu and isinstance(message.get("tool_calls"), list) and message["tool_calls"]:
            appel = message["tool_calls"][0]
            contenu = (appel.get("function") or {}).get("arguments", "")
        try:
            arguments = extraire_json(contenu)
        except (ValueError, TypeError) as exc:
            raise ErreurFournisseur("Proposition du LLM local illisible. Aucune action appliquée.",
                                    brut=brut, utilisation=usage) from exc
        sortie = [{"type": "message", "role": "assistant", "finish_reason": raison, "slot": slot, "voie": voie}]
        return Reponse(arguments, brut, usage, sortie)
