"""Le MJ peut répondre par un appel Python à l'API du moteur, lu sans jamais être exécuté.

L'API est la fonction demandée par le moteur (repondre_au_joueur, auditer_narration…),
présentée comme une signature Python dérivée de son schéma. Le script est analysé par
`ast` : un seul appel à cette fonction, des arguments nommés et des littéraux ; tout le
reste est refusé. La valeur obtenue est vérifiée contre le schéma, et chaque écart est
décrit par son chemin pour que le modèle puisse corriger.
"""
from __future__ import annotations

import ast
import json

FONCTION = "ecrire_script"
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {"script": {"type": "string",
                              "description": "Script Python : un seul appel à la fonction de l'API du moteur."}},
    "required": ["script"],
}
TYPES_PY = {"string": "str", "integer": "int", "number": "float", "boolean": "bool", "null": "None"}
BORNES = {"minItems": "au moins {} éléments", "maxItems": "au plus {} éléments",
          "minLength": "au moins {} caractères", "maxLength": "au plus {} caractères",
          "minimum": "au moins {}", "maximum": "au plus {}"}


class ErreurScript(ValueError):
    pass


class Instance(dict):
    """Objet écrit par un constructeur nommé : sa forme est désignée par le modèle."""

    def __init__(self, classe, champs):
        super().__init__(champs)
        self.classe = classe


def _camel(nom):
    return "".join(p[:1].upper() + p[1:] for p in str(nom).replace("-", "_").split("_") if p)


class _Classes:
    """Nomme chaque objet du schéma d'après le champ qui le porte, dans un ordre stable."""

    def __init__(self):
        self.noms, self.definitions = {}, []

    def nommer(self, schema, base, alternative):
        if id(schema) in self.noms:
            return self.noms[id(schema)]
        pris = {nom for nom, _ in self.definitions}
        candidats = [_camel(base) or "Objet"]
        if alternative:
            # Une forme parmi d'autres : sa valeur fixe (action="composer") ou ses premiers champs.
            fixes = [s["enum"][0] for s in schema.get("properties", {}).values()
                     if isinstance(s, dict) and len(s.get("enum", [])) == 1 and s["enum"][0]]
            champs = list(schema.get("properties", {}))
            candidats = ([candidats[0] + _camel(fixes[0])] if fixes else []) + [
                candidats[0] + "".join(_camel(c) for c in champs[:n]) for n in range(1, len(champs) + 1)]
        nom = next((c for c in candidats if c not in pris), None)
        n = 2
        while nom is None or nom in pris:
            nom, n = f"{candidats[0]}{n}", n + 1
        self.noms[id(schema)] = nom
        self.definitions.append((nom, schema))
        return nom


def _type(schema, base, classes, alternative=False):
    if not isinstance(schema, dict):
        return "object"
    if "anyOf" in schema:
        return " | ".join(_type(o, base, classes, True) for o in schema["anyOf"])
    if "enum" in schema:
        return "Literal[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in schema["enum"]) + "]"
    types = schema.get("type")
    if isinstance(types, list):
        return " | ".join(_type({**schema, "type": t}, base, classes) for t in types)
    if types == "array":
        return "list[" + _type(schema.get("items", {}), base[:-1] if base.endswith("s") else base, classes) + "]"
    if types == "object":
        return classes.nommer(schema, base, alternative) if schema.get("properties") else "dict"
    return TYPES_PY.get(types, "object")


def _note(schema, optionnel):
    morceaux = ["optionnel"] if optionnel else []
    if isinstance(schema, dict):
        morceaux += [schema["description"]] if schema.get("description") else []
        morceaux += [texte.format(schema[k]) for k, texte in BORNES.items() if k in schema]
    return ("  # " + " ; ".join(morceaux)) if morceaux else ""


def _champs(schema, classes, retrait, separateur=""):
    requis = set(schema.get("required", []))
    return [f"{retrait}{nom}: {_type(sous, nom, classes)}{separateur}{_note(sous, nom not in requis)}"
            for nom, sous in schema.get("properties", {}).items()]


def _rendu(fonction, schema):
    """Signature de la fonction, puis une classe par objet qu'elle reçoit."""
    classes = _Classes()
    lignes = [f"def {fonction}(*,"] + _champs(schema, classes, "    ", ",") + ["    ) -> None: ..."]
    faits = 0
    while faits < len(classes.definitions):
        nom, sous = classes.definitions[faits]
        faits += 1
        lignes += ["", f"class {nom}(TypedDict):"] + (_champs(sous, classes, "    ") or ["    pass"])
    return "\n".join(lignes), dict(classes.definitions)


def api(fonction, schema):
    """Signature Python de la fonction et des objets qu'elle reçoit."""
    return _rendu(fonction, schema)[0]


def consigne(fonction, schema):
    return f"""

LANGAGE DE RÉPONSE : tu ne remplis pas de formulaire JSON. Tu réponds en appelant l'outil
{FONCTION}, dont le champ script contient un script Python d'une seule instruction :
un appel à {fonction}(...) avec des arguments nommés. Le moteur lit ce script sans
l'exécuter : seuls des littéraux sont permis (textes, nombres, True, False, None, listes,
dictionnaires) et les constructeurs des classes ci-dessous, appelés avec des arguments
nommés, par exemple Classe(champ="valeur"). Pas de variable, d'import, de boucle ni
d'autre fonction. Les règles qui précèdent parlent des champs de {fonction} : elles
s'appliquent telles quelles à ses arguments. Si le moteur refuse ton script, la raison
exacte t'est renvoyée dans erreur_script pour une seule correction.

API du moteur :

```python
{api(fonction, schema)}
```
"""


def _litteral(noeud, classes):
    if isinstance(noeud, ast.Constant) and (noeud.value is None or isinstance(noeud.value, (str, int, float, bool))):
        return noeud.value
    if (isinstance(noeud, ast.UnaryOp) and isinstance(noeud.op, ast.USub)
            and isinstance(noeud.operand, ast.Constant) and type(noeud.operand.value) in (int, float)):
        return -noeud.operand.value
    if isinstance(noeud, (ast.List, ast.Tuple)):
        return [_litteral(e, classes) for e in noeud.elts]
    if isinstance(noeud, ast.Dict):
        resultat = {}
        for cle, valeur in zip(noeud.keys, noeud.values):
            if not (isinstance(cle, ast.Constant) and isinstance(cle.value, str)):
                raise ErreurScript(f"ligne {noeud.lineno} : les clés d'un dictionnaire sont des textes littéraux.")
            resultat[cle.value] = _litteral(valeur, classes)
        return resultat
    if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Name) and noeud.func.id in classes:
        return Instance(noeud.func.id, _arguments(noeud, classes))
    trouve = (noeud.func.id if isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Name)
              else noeud.id if isinstance(noeud, ast.Name) else type(noeud).__name__)
    raise ErreurScript(f"ligne {getattr(noeud, 'lineno', '?')} : « {trouve} » n'est pas permis ; "
                       "seuls des littéraux et les constructeurs de l'API le sont.")


def _arguments(appel, classes):
    if appel.args or any(k.arg is None for k in appel.keywords):
        raise ErreurScript(f"ligne {appel.lineno} : {getattr(appel.func, 'id', '?')} attend uniquement "
                           "des arguments nommés.")
    noms = [k.arg for k in appel.keywords]
    doubles = sorted({n for n in noms if noms.count(n) > 1})
    if doubles:
        raise ErreurScript(f"ligne {appel.lineno} : argument répété : {', '.join(doubles)}.")
    return {k.arg: _litteral(k.value, classes) for k in appel.keywords}


def _sans_cloture(source):
    lignes = source.strip().splitlines()
    if lignes and lignes[0].startswith("```"):
        lignes = lignes[1:]
        if lignes and lignes[-1].strip() == "```":
            lignes = lignes[:-1]
    return "\n".join(lignes)


def _ordinaire(valeur):
    if isinstance(valeur, dict):
        return {k: _ordinaire(v) for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [_ordinaire(v) for v in valeur]
    return valeur


def lire(source, fonction, schema):
    """Valeur conforme au schéma décrite par le script, ou ErreurScript avec chaque écart."""
    if not isinstance(source, str) or not source.strip():
        raise ErreurScript("Le script est vide.")
    try:
        arbre = ast.parse(_sans_cloture(source))
    except SyntaxError as exc:
        raise ErreurScript(f"ligne {exc.lineno} : syntaxe Python invalide ({exc.msg}).") from None
    corps = arbre.body
    if (len(corps) != 1 or not isinstance(corps[0], ast.Expr) or not isinstance(corps[0].value, ast.Call)
            or not isinstance(corps[0].value.func, ast.Name) or corps[0].value.func.id != fonction):
        raise ErreurScript(f"Le script doit contenir une seule instruction : un appel à {fonction}(...).")
    classes = _rendu(fonction, schema)[1]  # les noms donnés dans la consigne
    valeur = _arguments(corps[0].value, classes)
    fautes = erreurs(valeur, schema, classes)
    if fautes:
        raise ErreurScript(refus(fautes))
    return _ordinaire(valeur)


def refus(fautes):
    return "Valeur refusée par l'API :\n- " + "\n- ".join(fautes[:12])


def _type_correct(valeur, attendu):
    return {"string": isinstance(valeur, str),
            "integer": isinstance(valeur, int) and not isinstance(valeur, bool),
            "number": isinstance(valeur, (int, float)) and not isinstance(valeur, bool),
            "boolean": isinstance(valeur, bool), "null": valeur is None,
            "array": isinstance(valeur, list), "object": isinstance(valeur, dict)}.get(attendu, True)


def _court(valeur):
    texte = json.dumps(_ordinaire(valeur), ensure_ascii=False)
    return texte if len(texte) <= 60 else texte[:57] + "…"


def erreurs(valeur, schema, classes=None, chemin=""):
    """Écarts entre une valeur et le sous-ensemble de JSON Schema utilisé par le moteur."""
    classes = classes or {}
    ici = chemin or "la réponse"
    if not isinstance(schema, dict):
        return []
    if "anyOf" in schema:
        options = schema["anyOf"]
        if isinstance(valeur, Instance):
            choisie = classes.get(valeur.classe)
            if not any(o is choisie for o in options):
                return [f"{ici} : {valeur.classe} n'est pas une forme acceptée ici."]
            return erreurs(valeur, choisie, classes, chemin)
        essais = [erreurs(valeur, o, classes, chemin) for o in options]
        if any(not e for e in essais):
            return []
        # Rapporte les écarts de la forme la plus proche : même type, le plus de champs en commun.
        def proximite(paire):
            option, fautes = paire
            communs = len(set(valeur) & set(option.get("properties", {}))) if isinstance(valeur, dict) else 0
            return (not _type_correct(valeur, option.get("type")), -communs, len(fautes))
        return min(zip(options, essais), key=proximite)[1]
    if "enum" in schema and valeur not in schema["enum"]:
        permis = ", ".join(_court(v) for v in schema["enum"][:40])
        return [f"{ici} : {_court(valeur)} n'est pas permis ; valeurs possibles : {permis}."]
    types = schema.get("type")
    if types is not None:
        attendus = types if isinstance(types, list) else [types]
        if not any(_type_correct(valeur, t) for t in attendus):
            return [f"{ici} : attendu {' ou '.join(TYPES_PY.get(t, t) for t in attendus)}, reçu {_court(valeur)}."]
    fautes = []
    if isinstance(valeur, str):
        if len(valeur) < schema.get("minLength", 0):
            fautes.append(f"{ici} : texte trop court (au moins {schema['minLength']} caractères).")
        if "maxLength" in schema and len(valeur) > schema["maxLength"]:
            fautes.append(f"{ici} : texte trop long (au plus {schema['maxLength']} caractères).")
    if isinstance(valeur, (int, float)) and not isinstance(valeur, bool):
        if "minimum" in schema and valeur < schema["minimum"]:
            fautes.append(f"{ici} : {valeur} est inférieur au minimum {schema['minimum']}.")
        if "maximum" in schema and valeur > schema["maximum"]:
            fautes.append(f"{ici} : {valeur} dépasse le maximum {schema['maximum']}.")
    if isinstance(valeur, list):
        if len(valeur) < schema.get("minItems", 0):
            fautes.append(f"{ici} : au moins {schema['minItems']} éléments attendus.")
        if "maxItems" in schema and len(valeur) > schema["maxItems"]:
            fautes.append(f"{ici} : au plus {schema['maxItems']} éléments attendus.")
        for i, element in enumerate(valeur):
            fautes += erreurs(element, schema.get("items"), classes, f"{chemin}[{i}]")
    if isinstance(valeur, dict) and (schema.get("type") == "object" or "properties" in schema):
        if isinstance(valeur, Instance) and classes.get(valeur.classe) is not schema:
            return [f"{ici} : {valeur.classe} n'est pas la forme attendue ici."]
        proprietes = schema.get("properties", {})
        for nom in schema.get("required", []):
            if nom not in valeur:
                fautes.append(f"{ici} : champ manquant « {nom} ».")
        for nom, sous in valeur.items():
            if nom in proprietes:
                fautes += erreurs(sous, proprietes[nom], classes, f"{chemin}.{nom}" if chemin else nom)
            elif schema.get("additionalProperties") is False:
                fautes.append(f"{ici} : champ inconnu « {nom} » ; champs permis : {', '.join(proprietes)}.")
    return fautes


def ecrire(fonction, valeur):
    """Script équivalent à une valeur, avec des dictionnaires littéraux (tests, exemples)."""
    return f"{fonction}(\n" + "".join(f"    {k}={v!r},\n" for k, v in valeur.items()) + ")"
