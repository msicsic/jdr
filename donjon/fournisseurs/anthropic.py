"""Anthropic Messages : outil strict, réflexion et transcription des réponses texte."""
import json

from ..monde import ErreurMonde
from .contrat import Fournisseur, Reponse

BORNES = ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
          "minLength", "maxLength", "maxItems")
SORTIE_MAX = 16000


def schema_strict(schema):
    """Le mode strict d'Anthropic n'accepte pas les bornes : elles passent dans la description.

    Le modèle les lit encore ; le moteur continue de vérifier la proposition comme avant.
    """
    if isinstance(schema, list):
        return [schema_strict(s) for s in schema]
    if not isinstance(schema, dict):
        return schema
    retirees = {k: schema[k] for k in BORNES if k in schema}
    if schema.get("minItems", 0) > 1:
        retirees["minItems"] = schema["minItems"]
    copie = {k: schema_strict(v) for k, v in schema.items() if k not in retirees}
    if retirees:
        note = "Contraintes : " + ", ".join(f"{k} {v}" for k, v in retirees.items()) + "."
        copie["description"] = (copie["description"] + " " + note) if copie.get("description") else note
    return copie


def _accepte_texte(schema):
    if not isinstance(schema, dict):
        return True
    if "anyOf" in schema:
        return any(_accepte_texte(s) for s in schema["anyOf"])
    types = schema.get("type")
    return types is None or "string" in (types if isinstance(types, list) else [types])


def decoder_imbrique(valeur, schema):
    """Hors mode strict, un objet peut revenir sous forme de texte JSON : seul ce codage est défait,
    là où le schéma n'accepte pas de texte ; le contrôle du moteur ne change pas."""
    if isinstance(valeur, str) and not _accepte_texte(schema) and valeur.lstrip()[:1] in ("{", "["):
        try:
            valeur = json.loads(valeur)
        except ValueError:
            return valeur
    if isinstance(schema, dict) and "anyOf" in schema:
        for option in schema["anyOf"]:
            if (option.get("type") == "object") == isinstance(valeur, dict):
                return decoder_imbrique(valeur, option)
        return valeur
    if isinstance(valeur, dict) and isinstance(schema, dict):
        proprietes = schema.get("properties", {})
        return {k: decoder_imbrique(v, proprietes.get(k)) for k, v in valeur.items()}
    if isinstance(valeur, list) and isinstance(schema, dict):
        return [decoder_imbrique(v, schema.get("items")) for v in valeur]
    return valeur


class Anthropic(Fournisseur):
    def __init__(self):
        super().__init__()
        self.sans_strict = set()
        self.client = None

    def fermer(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def _client(self, timeout):
        if self.client is None:
            import anthropic
            self.client = anthropic.Anthropic(timeout=max(60.0, float(timeout)), max_retries=2)
        return self.client

    def _memoriser(self, reponse, contenu, usages, strict):
        entree_t = sum(u.input_tokens for u in usages)
        sortie_t = sum(u.output_tokens for u in usages)
        lu = sum(u.cache_read_input_tokens or 0 for u in usages)
        ecrit = sum(u.cache_creation_input_tokens or 0 for u in usages)
        self.derniere_utilisation = {
            "input_tokens": entree_t, "output_tokens": sortie_t,
            "cache_read_input_tokens": lu, "cache_creation_input_tokens": ecrit,
            "total_tokens": entree_t + lu + ecrit + sortie_t}
        brut = {"stop_reason": reponse.stop_reason, "strict": strict, "contenu": contenu}
        self.dernier_brut = brut  # gardé pour la trace, même si la réponse est refusée ci-dessous
        return brut

    def _appeler(self, demande):
        instructions, entree = demande.instructions, demande.entree
        fonction, schema = demande.fonction, demande.schema
        import anthropic
        strict = fonction not in self.sans_strict
        outil = {"name": fonction,
                 "description": "Répond au joueur ou soumet une manœuvre au moteur, sans modifier le monde.",
                 "input_schema": schema_strict(schema) if strict else schema, "strict": strict}
        requete = {"model": demande.modele, "max_tokens": SORTIE_MAX,
                   "system": [{"type": "text", "text": instructions, "cache_control": {"type": "ephemeral"}}],
                   "messages": [{"role": "user", "content": json.dumps(entree, ensure_ascii=False)}],
                   "tools": [outil], "output_config": {"effort": demande.effort}}
        if demande.reflexion == "libre":
            requete.update(thinking={"type": "adaptive", "display": "summarized"},
                           tool_choice={"type": "auto", "disable_parallel_tool_use": True})
        else:
            requete["tool_choice"] = {"type": "tool", "name": fonction, "disable_parallel_tool_use": True}
        try:
            reponse = self._client(demande.timeout).messages.create(**requete)
        except anthropic.AuthenticationError:
            self.erreur_auth = ("MJ déconnecté : la clé ANTHROPIC_API_KEY est refusée. Aucun nouvel appel ne "
                              "sera tenté dans cette session.")
            raise ErreurMonde(self.erreur_auth) from None
        except anthropic.BadRequestError as exc:
            if strict and "grammar" in str(exc.message).lower():
                # Schéma trop riche pour la grammaire stricte : même requête, sans garantie de format.
                self.sans_strict.add(fonction)
                return self._appeler(demande)
            raise ErreurMonde(f"MJ indisponible : requête refusée ({str(exc.message)[:200]}).") from None
        except anthropic.APIStatusError as exc:
            raise ErreurMonde(f"MJ indisponible : HTTP {exc.status_code}. Monde inchangé.") from None
        except anthropic.APIConnectionError:
            raise ErreurMonde("Le MJ n'a pas répondu (réseau ou délai). Aucune action appliquée.") from None
        contenu = [b.model_dump(mode="json", exclude_none=True) for b in reponse.content]
        usages = [reponse.usage]
        self._memoriser(reponse, contenu, usages, strict)
        if (demande.reflexion == "libre" and reponse.stop_reason == "end_turn"
                and not any(b.type == "tool_use" for b in reponse.content)):
            # Réflexion faite, mais réponse rendue en texte : le modèle la transcrit en appel imposé,
            # avec sa propre réflexion sous les yeux. Le sens reste le sien ; seul le format change.
            suite = {**requete, "tool_choice": {"type": "tool", "name": fonction, "disable_parallel_tool_use": True},
                     "messages": [*requete["messages"], {"role": "assistant", "content": contenu},
                                  {"role": "user", "content": f"Transcris exactement cette réponse en appelant {fonction} "
                                                              "une fois, sans en changer le sens."}]}
            try:
                reponse = self._client(demande.timeout).messages.create(**suite)
            except anthropic.APIError as exc:
                raise ErreurMonde("Le MJ n'a pas fourni une proposition unique. Aucune action appliquée.") from exc
            usages.append(reponse.usage)
            contenu = contenu + [{"type": "transcription"}] + [
                b.model_dump(mode="json", exclude_none=True) for b in reponse.content]
        brut = self._memoriser(reponse, contenu, usages, strict)
        if reponse.stop_reason == "refusal":
            raise ErreurMonde("Le MJ a décliné la demande. Aucune action appliquée.")
        if reponse.stop_reason == "max_tokens":
            raise ErreurMonde("Réponse du MJ tronquée. Aucune action appliquée.")
        appels = [b for b in reponse.content if b.type == "tool_use"]
        if len(appels) != 1 or appels[0].name != fonction or not isinstance(appels[0].input, dict):
            raise ErreurMonde("Le MJ n'a pas fourni une proposition unique. Aucune action appliquée.")
        return Reponse(decoder_imbrique(appels[0].input, schema), brut, self.derniere_utilisation)
