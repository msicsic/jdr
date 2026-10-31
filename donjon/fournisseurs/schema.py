"""Grammaire commune : validation, projection et partage sans perte de contraintes."""
from collections import Counter
import json
import math
import re

from ..refus import RefusDeForme


def restreint(fort, faible):
    """Preuve structurelle suffisante d'inclusion, avant mutualisation.

    Un cas non démontré retourne faux ; il ne permet jamais de retirer une
    contrainte. Les annotations de prose n'affectent pas le langage accepté.
    """
    if fort is faible or (fort == faible and
            json.dumps(fort, sort_keys=True) == json.dumps(faible, sort_keys=True)):
        return True
    faible = {k: v for k, v in faible.items() if k != 'description'}
    if not faible:
        return True
    if 'anyOf' in fort:
        return all(restreint(option, faible) for option in fort['anyOf'])
    if 'anyOf' in faible:
        commun = {k: v for k, v in faible.items() if k != 'anyOf'}
        return restreint(fort, commun) and any(restreint(fort, option) for option in faible['anyOf'])
    for cle, valeur in faible.items():
        recu = fort.get(cle)
        if cle == 'type':
            if recu != valeur and (recu, valeur) != ('integer', 'number'):
                return False
        elif cle == 'enum':
            if recu is None or any(not any(type(v) is type(w) and v == w for w in valeur) for v in recu):
                return False
        elif cle == 'required':
            if not set(valeur) <= set(recu or []):
                return False
        elif cle == 'additionalProperties':
            if type(valeur) is not bool:
                return False
            if valeur is False and (recu is not False or
                    not set(fort.get('properties', {})) <= set(faible.get('properties', {}))):
                return False
        elif cle == 'properties':
            for champ, contrainte in valeur.items():
                if champ in fort.get('properties', {}):
                    if not restreint(fort['properties'][champ], contrainte):
                        return False
                elif fort.get('additionalProperties') is not False:
                    return False
        elif cle == 'items':
            if recu is None or not restreint(recu, valeur):
                return False
        elif cle in ('minItems', 'minLength', 'minimum'):
            if recu is None or recu < valeur:
                return False
        elif cle in ('maxItems', 'maxLength', 'maximum'):
            if recu is None or recu > valeur:
                return False
        elif cle == 'pattern':
            if recu != valeur:
                return False
        else:
            return False
    return True


def union_seule(schema):
    """Retirer une conjonction seulement si chaque branche l'implique déjà.

    Le décodeur cloud échoue avant tout jeton sur l'objet combinant propriétés
    communes et anyOf lié. Une union seule conserve exactement le même langage
    lorsque toutes ses branches portent déjà ces contraintes communes.
    """
    commun = {k: v for k, v in schema.items() if k != 'anyOf'}
    if not all(restreint(branche, commun) for branche in schema['anyOf']):
        raise ValueError('La grammaire liée ne prouve pas les contraintes communes de chaque branche.')
    return {'anyOf': schema['anyOf']}


def verifier(valeur, schema, chemin='reponse'):
    """Valider le sous-ensemble utilisé par les contrats du compilateur.

    Le contrôle porte sur la grammaire canonique avant mutualisation ; les
    contraintes du monde restent aux préparateurs. Aucun choix selon la saisie.
    """
    connus = {'type', 'enum', 'anyOf', 'properties', 'required', 'additionalProperties',
              'items', 'minItems', 'maxItems', 'minLength', 'maxLength', 'pattern',
              'minimum', 'maximum', 'description'}
    if set(schema) - connus:
        raise ValueError(f"Contraintes de grammaire non prises en charge : {sorted(set(schema) - connus)}")

    def refuser(accepte, recu=valeur, champ=chemin):
        raise RefusDeForme('La proposition ne respecte pas son contrat de forme.',
                          f'{champ} : reçu {recu!r} ; accepté : {accepte}.')

    if 'anyOf' in schema:
        options = schema['anyOf']
        preferes = []
        # Choisir seulement pour le diagnostic, jamais pour admettre une branche
        # différente : enum et types sont ensuite contrôlés intégralement.
        if isinstance(valeur, dict):
            for cle in ('mode', 'action', 'operation', 'type'):
                correspondantes = [s for s in options if valeur.get(cle) in
                                  s.get('properties', {}).get(cle, {}).get('enum', [])]
                if correspondantes:
                    preferes = correspondantes
                    options = correspondantes + [s for s in options if s not in correspondantes]
                    break
        erreurs = []
        erreurs_preferees = []
        for option in options:
            try:
                verifier(valeur, option, chemin)
                break
            except RefusDeForme as exc:
                erreurs.append(exc)
                if option in preferes:
                    erreurs_preferees.append(exc)
        else:
            # Un objet à la place de null doit montrer sa charge fautive.
            raise max(erreurs_preferees or erreurs,
                      key=lambda e: e.attendu.count('.') + e.attendu.count('['))
    types = {'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
             'string': lambda v: isinstance(v, str), 'integer': lambda v: type(v) is int,
             'number': lambda v: type(v) is int or (type(v) is float and math.isfinite(v)),
             'boolean': lambda v: type(v) is bool, 'null': lambda v: v is None}
    if 'type' in schema and not types[schema['type']](valeur):
        refuser(schema['type'])
    if 'enum' in schema and not any(valeur == v and (type(valeur) is type(v) or
            (type(valeur) in (int, float) and type(v) in (int, float))) for v in schema['enum']):
        refuser(repr(schema['enum']))
    if isinstance(valeur, dict):
        proprietes = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            for cle in valeur:
                if cle not in proprietes:
                    refuser('champ absent', valeur[cle], chemin + '.' + cle)
        # Une charge voisine interdite se diagnostique avant le contenu libre
        # qu'elle tentait de remplacer (même règle que les contrats de famille).
        for cle, s in proprietes.items():
            if cle in valeur and 'enum' in s:
                verifier(valeur[cle], s, chemin + '.' + cle)
        for cle in schema.get('required', []):
            if cle not in valeur:
                refuser('champ requis', '<absent>', chemin + '.' + cle)
        for cle, s in proprietes.items():
            if cle in valeur and 'enum' not in s:
                verifier(valeur[cle], s, chemin + '.' + cle)
    if isinstance(valeur, list):
        for cle, test in (('minItems', len(valeur) >= schema.get('minItems', 0)),
                          ('maxItems', len(valeur) <= schema.get('maxItems', math.inf))):
            if not test:
                refuser(f'{cle} {schema[cle]}')
        if 'items' in schema:
            for i, v in enumerate(valeur):
                verifier(v, schema['items'], f'{chemin}[{i}]')
    if isinstance(valeur, str):
        if len(valeur) < schema.get('minLength', 0) or len(valeur) > schema.get('maxLength', math.inf):
            refuser(f"longueur {schema.get('minLength', 0)} à {schema.get('maxLength', 'sans borne')}")
        if 'pattern' in schema and not re.search(schema['pattern'], valeur):
            refuser('pattern ' + schema['pattern'])
    if type(valeur) in (int, float):
        if (type(valeur) is float and not math.isfinite(valeur)) or valeur < schema.get('minimum', -math.inf) or valeur > schema.get('maximum', math.inf):
            refuser(f"nombre fini entre {schema.get('minimum', '-inf')} et {schema.get('maximum', '+inf')}")


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
