"""Contrat des termes d'un marché ; aucune interprétation de mots du scénario."""
from .monde import ErreurMonde


def _forme(proprietes):
    return {"type": "object", "additionalProperties": False,
            "properties": proprietes, "required": list(proprietes)}


def schema_terme(contrepartie=False, service=False):
    formes = [_forme({"type": {"type": "string", "enum": [t]}, "objet": {"type": "string"}})
              for t in ("objet", "part")]
    conditions = [_forme({"objet": {"type": "string"}, cle: valeur}) for cle, valeur in (
        ("allume", {"type": "boolean", "enum": [True]}),
        ("verrouillee", {"type": "boolean", "enum": [True]}),
        ("lieu", {"type": "string"}))]
    if service:
        conditions.append(_forme({"objet": {"type": "string"}, "servir": {"type": "string"}}))
    formes.append(_forme({"type": {"type": "string", "enum": ["tache"]},
                          "condition": {"anyOf": conditions}}))
    if contrepartie:
        formes.extend([_forme({"type": {"type": "string", "enum": ["pieces"]},
                               "montant": {"type": "integer", "minimum": 1}}),
                       _forme({"type": {"type": "string", "enum": ["rien"]}})])
    return {"anyOf": formes}


SCHEMA = _forme({"type": {"type": "string", "enum": ["proposition"]},
                 "demande": schema_terme(), "contrepartie": schema_terme(True)})


SCHEMA_OFFRE = _forme({"etat": {"type": "string", "enum": ["offre"]},
    "debiteur": {"type": "string"}, "creancier": {"type": "string"},
    "condition": schema_terme(True, service=True), "contrepartie": schema_terme(True)})


def offre(debiteur, creancier, condition, contrepartie):
    """Contrepartie promise par le débiteur contre la prestation du créancier.

    Ces termes conditionnels ne sont ni une dette exigible ni une remise accomplie.
    Mission et marché utilisent les mêmes termes, sans interpréter leur prose.
    """
    import copy
    return {"etat": "offre", "debiteur": debiteur, "creancier": creancier,
            "condition": copy.deepcopy(condition), "contrepartie": copy.deepcopy(contrepartie)}


def offre_en_mots(monde, o):
    from .voix import personne_pour_joueur
    def qui(id):
        return "toi" if id == "joueur" else personne_pour_joueur(monde, id, court=True)[0]
    return (f"Offre de {qui(o['debiteur'])} à {qui(o['creancier'])} : "
            f"{en_mots(monde, o['contrepartie'])} contre {en_mots(monde, o['condition'])}. "
            "Cette offre conditionnelle n'est pas une dette exigible ni un paiement.")


def cites_terme(terme):
    c = terme.get("condition", {})
    return [x for x in (terme.get("objet"), c.get("objet"), c.get("lieu")) if x]


def en_mots(monde, terme):
    from .francais import designer, complement_de
    from .echanges import phrase_condition
    t = terme["type"]
    if t == "tache":
        return "la promesse que " + phrase_condition(monde, terme["condition"])
    if t == "pieces":
        return f"{terme['montant']} pièces"
    if t == "rien":
        return "rien"
    o = monde.objets[terme["objet"]]
    return "une part " + complement_de(o) if t == "part" else designer(o)


def verifier(monde, c, champ="contenu", proposant="joueur"):
    """Une forme refusée désigne toujours son champ, sa valeur et les valeurs acceptées."""
    def refuser(champ, recu, accepte):
        raise ErreurMonde("Les termes de cet échange doivent être précisés.",
                          f"{champ} : reçu {recu!r} ; attendu {accepte}.")

    if set(c) != {"type", "demande", "contrepartie"}:
        refuser(champ, sorted(c), "type, demande, contrepartie")
    from .deliberation import _connus
    from .paroles import resoudre
    connus_pnj = set(_connus(monde, proposant)) if proposant != "joueur" else set()
    def connu(x):
        return resoudre(monde, x) == x if proposant == "joueur" else x in connus_pnj
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
            if not isinstance(objet, str) or objet not in monde.objets or not connu(objet):
                from .refus import cibles
                connus = [i for i, o in monde.objets.items() if o.get("mobile")
                          and o["type"] not in ("personnage", "depouille") and connu(i)]
                refuser(chemin + ".objet", objet, "identifiant parmi " + cibles(monde, connus))
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
                if cle in ("objet", "lieu") and not (connu(valeur) or proposant != "joueur" and cle == "lieu" and valeur in monde.data["salles"]):
                    refuser(chemin + ".condition." + cle, valeur, "identifiant connu de Corvus")
        elif t == "pieces" and (type(terme["montant"]) is not int or terme["montant"] <= 0):
            refuser(chemin + ".montant", terme["montant"], "entier strictement positif")
