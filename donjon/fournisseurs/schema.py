"""Retirer les répétitions d'un schéma sans changer son contrat de validation."""
from collections import Counter
import json


def mutualiser(schema):
    """Partager les sous-schémas identiques ; les valeurs enum/const restent littérales.

    Les schémas qui possèdent déjà une identité ou des références sont conservés :
    déplacer leur cible pourrait changer la résolution d'un pointeur relatif.
    Aucune simplification de règle ou de champ n'est effectuée.
    """
    def references(valeur):
        if isinstance(valeur, dict):
            return (any(k in valeur for k in ("$id", "$ref", "$defs", "definitions", "$anchor", "$dynamicRef"))
                    or any(references(v) for v in valeur.values()))
        return isinstance(valeur, list) and any(references(v) for v in valeur)

    if references(schema):
        return schema
    cartes = {"properties", "patternProperties", "dependentSchemas"}
    listes = {"anyOf", "allOf", "oneOf", "prefixItems"}
    uniques = {"items", "contains", "additionalProperties", "unevaluatedProperties",
               "unevaluatedItems", "propertyNames", "not", "if", "then", "else"}

    def enfants(noeud, transformer):
        resultat = dict(noeud)
        for cle, valeur in noeud.items():
            if cle in cartes:
                resultat[cle] = {k: transformer(v) for k, v in valeur.items()}
            elif cle in listes:
                resultat[cle] = [transformer(v) for v in valeur]
            elif cle in uniques:
                resultat[cle] = transformer(valeur)
        return resultat

    def signature(noeud):
        return json.dumps(noeud, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    comptes = Counter()

    def compter(noeud):
        if isinstance(noeud, dict):
            cle = signature(noeud)
            if len(cle) >= 512:
                comptes[cle] += 1
            enfants(noeud, compter)
        return noeud

    compter(schema)
    definitions, noms = {}, {}

    def partager(noeud, racine=False):
        if not isinstance(noeud, dict):
            return noeud
        cle = signature(noeud)
        if not racine and comptes[cle] > 1:
            if cle not in noms:
                nom = noms[cle] = f"commun_{len(noms)}"
                definitions[nom] = enfants(noeud, partager)
            return {"$ref": "#/$defs/" + noms[cle]}
        return enfants(noeud, partager)

    resultat = partager(schema, racine=True)
    if definitions:
        resultat["$defs"] = definitions
    return resultat if len(signature(resultat)) < len(signature(schema)) else schema
