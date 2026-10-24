"""Contrat des termes d'un marché ; aucune interprétation de mots du scénario."""
from .monde import ErreurMonde


def _forme(proprietes):
    return {"type": "object", "additionalProperties": False,
            "properties": proprietes, "required": list(proprietes)}


def schema_terme(contrepartie=False):
    formes = [_forme({"type": {"type": "string", "enum": [t]}, "objet": {"type": "string"}})
              for t in ("objet", "part")]
    conditions = [_forme({"objet": {"type": "string"}, cle: valeur}) for cle, valeur in (
        ("allume", {"type": "boolean", "enum": [True]}),
        ("verrouillee", {"type": "boolean", "enum": [True]}),
        ("lieu", {"type": "string"}))]
    formes.append(_forme({"type": {"type": "string", "enum": ["tache"]},
                          "condition": {"anyOf": conditions}}))
    if contrepartie:
        formes.extend([_forme({"type": {"type": "string", "enum": ["pieces"]},
                               "montant": {"type": "integer", "minimum": 1}}),
                       _forme({"type": {"type": "string", "enum": ["rien"]}})])
    return {"anyOf": formes}


SCHEMA = _forme({"type": {"type": "string", "enum": ["proposition"]},
                 "demande": schema_terme(), "contrepartie": schema_terme(True)})


def verifier(monde, c, champ="contenu"):
    """Une forme refusée désigne toujours son champ, sa valeur et les valeurs acceptées."""
    def refuser(champ, recu, accepte):
        raise ErreurMonde("Les termes de cet échange doivent être précisés.",
                          f"{champ} : reçu {recu!r} ; attendu {accepte}.")

    if set(c) != {"type", "demande", "contrepartie"}:
        refuser(champ, sorted(c), "type, demande, contrepartie")
    for nom in ("demande", "contrepartie"):
        terme = c[nom]
        chemin = f"{champ}.{nom}"
        types = ("objet", "part", "tache") + (("pieces", "rien") if nom == "contrepartie" else ())
        if not isinstance(terme, dict) or terme.get("type") not in types:
            refuser(chemin, terme, types)
        t = terme["type"]
        champs = {"type", *({"objet"} if t in ("objet", "part") else
                            {"condition"} if t == "tache" else {"montant"} if t == "pieces" else set())}
        if set(terme) != champs:
            refuser(chemin, sorted(terme), sorted(champs))
        if t in ("objet", "part"):
            from .paroles import resoudre
            from .deliberation import besoin_de_part
            objet = terme["objet"]
            if not isinstance(objet, str) or objet not in monde.objets or resoudre(monde, objet) != objet:
                from .refus import liste
                connus = [i for i, o in monde.objets.items() if o.get("mobile")
                          and o["type"] not in ("personnage", "depouille") and resoudre(monde, i) == i]
                refuser(chemin + ".objet", objet, "identifiant parmi " + liste(connus))
            o = monde.objets[objet]
            if not o.get("mobile") or o["type"] in ("personnage", "depouille"):
                refuser(chemin + ".objet", objet, "objet mobile, hors personnage")
            if t == "part" and besoin_de_part(o) is None:
                refuser(chemin + ".objet", objet, "ressource comptée")
        elif t == "tache":
            from .deliberation import condition_valide
            from .paroles import resoudre
            condition = terme["condition"]
            if (not isinstance(condition, dict) or not isinstance(condition.get("objet"), str)
                    or any(not isinstance(v, (str, bool)) for v in condition.values())
                    or not condition_valide(monde, condition) or set(condition) not in
                    ({"objet", "allume"}, {"objet", "verrouillee"}, {"objet", "lieu"})):
                refuser(chemin + ".condition", condition, "{objet, allume:true | verrouillee:true | lieu:salle}")
            for cle, valeur in condition.items():
                if cle in ("objet", "lieu") and resoudre(monde, valeur) != valeur:
                    refuser(chemin + ".condition." + cle, valeur, "identifiant connu de Corvus")
        elif t == "pieces" and (type(terme["montant"]) is not int or terme["montant"] <= 0):
            refuser(chemin + ".montant", terme["montant"], "entier strictement positif")
