"""Continuation des demandes : fournitures reçues et sommeil sans délai."""
import copy
import hashlib
import json


def fourniture(esprit, fait):
    """Le reçu public lie le résultat concret à ses sources, hors mémoire bornée."""
    if fait.get('type') not in ('recu', 'restitution') or not fait.get('lot') or not fait.get('objet'):
        return
    source, resultat = fait['lot'], fait['objet']
    if source == resultat:
        return
    stock = esprit.setdefault('fournitures', {})
    stock[resultat] = sorted(set(stock.get(resultat, ())) | {source} | set(stock.get(source, ())))


def conditions(monde, id, demande):
    """Les conditions de fourniture peuvent suivre une part, jamais une identité stricte.

    Ce sont les mêmes rôles de condition que l'affectation des fournitures
    promises. Une localisation, une garde ou une restitution d'objet précis
    ne deviennent pas satisfaites par un autre objet de même utilité.
    """
    from .esprits import lire
    c = demande['condition']
    if 'servir' in c or 'remettre' in c:
        for resultat, sources in sorted(lire(monde, id)['fournitures'].items()):
            if c['objet'] in sources and resultat in monde.objets:
                yield {**c, 'objet': resultat}
    yield c


def cle(motif, demande):
    return json.dumps([motif, demande], sort_keys=True, ensure_ascii=False)


def entrees(monde, id):
    """Croyances et moyens, pas l'âge d'un refus ni la date d'un regard."""
    from .esprits import lire
    from .spatial import porte_par

    def contenu(x):
        if isinstance(x, dict):
            return {k: contenu(v) for k, v in x.items()
                    if k not in ('minute', 'depuis', 'instant', 'preuve')}
        if isinstance(x, list):
            return [contenu(v) for v in x]
        return x

    e = lire(monde, id)
    portes = {k: {a: o[a] for a in ('portions', 'charges', 'pieces', 'allume', 'combustible') if a in o}
              for k, o in monde.objets.items() if porte_par(monde, k, id)}
    x = [contenu(e['croyances']), contenu(e['refus']), contenu(e['relations']),
         e['fournitures'], portes, monde.objets[id]['lieu'], monde.objets[id].get('position')]
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def endormir(monde, id, intention, contrat):
    from .esprits import esprit
    demande = contrat['demande']
    if 'agenda' in demande:
        return  # Son stock et son sommeil sont déjà tenus par agendas.
    esprit(monde, id)['demandes_suspendues'][cle(intention['motif'], demande)] = {
        'demande': copy.deepcopy(demande), 'but': copy.deepcopy(intention['but']),
        'motif': intention['motif'], 'depuis': intention['depuis'],
        'palier': contrat['palier'], 'valeur': contrat['valeur'], 'entrees': entrees(monde, id)}


def suspendue(monde, id, motif, demande):
    from .esprits import lire
    return demande is not None and cle(motif, demande) in lire(monde, id)['demandes_suspendues']


def dort(monde, id, motif, demande):
    from .esprits import lire
    s = lire(monde, id)['demandes_suspendues'].get(cle(motif, demande)) if demande else None
    return s is not None and s['entrees'] == entrees(monde, id)


def reveillables(monde, id):
    from .esprits import esprit
    from .deliberation import _fin_demande
    stock = esprit(monde, id)['demandes_suspendues']
    for k, s in list(stock.items()):
        if _fin_demande(monde, id, s['demande']):
            del stock[k]
        elif s['entrees'] != entrees(monde, id):
            yield s


def reprendre(monde, id, s):
    from .deliberation import _reprendre_demande
    proposition = _reprendre_demande(monde, id, s['demande'])
    if proposition is None:
        s['entrees'] = entrees(monde, id)
        return None
    return s['but'], proposition[1]


def retirer(monde, id, motif, demande):
    from .esprits import esprit
    if demande:
        esprit(monde, id)['demandes_suspendues'].pop(cle(motif, demande), None)


def verifier(monde, e):
    from .deliberation import Palier
    assert isinstance(e['fournitures'], dict) and all(
        isinstance(k, str) and isinstance(v, list) and all(isinstance(s, str) for s in v)
        and len(v) == len(set(v)) for k, v in e['fournitures'].items()), 'Provenances de fournitures invalides'
    assert isinstance(e['demandes_suspendues'], dict), 'Demandes en sommeil invalides'
    for k, s in e['demandes_suspendues'].items():
        assert (isinstance(s, dict) and set(s) == {'demande', 'but', 'motif', 'depuis', 'palier', 'valeur', 'entrees'}
                and isinstance(s['demande'], dict) and 'condition' in s['demande']
                and isinstance(s['but'], dict) and isinstance(s['motif'], str)
                and k == cle(s['motif'], s['demande']) and type(s['depuis']) is int
                and type(s['palier']) is int and s['palier'] in list(Palier)
                and isinstance(s['valeur'], (int, float)) and isinstance(s['entrees'], str)), 'Demande en sommeil invalide'
