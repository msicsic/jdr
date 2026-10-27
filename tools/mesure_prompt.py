"""Mesure hors réseau des fils MJ archivés, après mutualisation OpenAI.

Exemple : python tools/mesure_prompt.py --corpus CHEMIN --sortie DOSSIER
Les références sont celles du manifeste cache-avant.json du corpus uniquement.
Estimation de jetons indépendante du modèle : caractères / 4 (non un tokenizer).
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.fournisseurs.schema import mutualiser
from donjon.sources import voie_cache


def serialiser(value):
    # Même ensure_ascii et séparateurs par défaut que le fournisseur OpenAI.
    return json.dumps(value, ensure_ascii=False)


def voie(e):
    fn = e['fonction']
    props = e['schema'].get('properties', {})
    if fn == 'auditer_action':
        return 'fidelite' if 'contenu_conforme' in props else 'contre_revue'
    if fn == 'repondre_au_joueur':
        if 'controle_narratif' in e['entree']:
            return 'revision'
        return 'interpretation' if len(props.get('mode', {}).get('enum', [])) > 1 else 'recit'
    return fn


def payload(e):
    """Ordre exact du message ChatGPT OpenAI après transport WebSocket.

    La clé, constante pendant une partie mais non archivée, est un UUID factice.
    Ce JSON n'est pas un ordre de tokens KV interne au fournisseur.
    """
    return {'type': 'response.create', 'model': e['modele'], 'instructions': e['instructions'],
            'input': [{'role': 'user', 'content': serialiser(e['entree'])}],
            'tools': [{'type': 'namespace', 'name': 'donjon',
                       'description': 'Proposer une action ou une observation au moteur.',
                       'tools': [{'type': 'function', 'name': e['fonction'],
                                  'description': 'Répond au joueur ou soumet une manœuvre au moteur, sans modifier le monde.',
                                  'parameters': mutualiser(e['schema']), 'strict': True}]}],
            'tool_choice': 'required', 'parallel_tool_calls': False,
            'reasoning': {'effort': e.get('effort', 'medium')}, 'store': False,
            'prompt_cache_key': '00000000-0000-0000-0000-000000000000:' + voie_cache(
                e['fonction'], e['entree'],
                e['schema'].get('properties', {}).get('mode', {}).get('enum') != ['dialogue'])}


def prefixe(a, b):
    return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))


def difference(a, b, chemin=''):
    if type(a) != type(b):
        return chemin
    if isinstance(a, dict):
        if list(a) != list(b):
            return chemin + '/cles'
        for k in a:
            if a[k] != b[k]:
                return difference(a[k], b[k], chemin + '/' + k)
    elif isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                return difference(x, y, chemin + '/' + str(i))
        if len(a) != len(b):
            return chemin + '/longueur'
    return chemin


def references_objets(dossier, objets):
    if isinstance(dossier, str):
        return {dossier} if dossier in objets else set()
    if isinstance(dossier, dict):
        return set().union(*(references_objets(v, objets) for v in dossier.values()), set())
    if isinstance(dossier, list):
        return set().union(*(references_objets(v, objets) for v in dossier), set())
    return set()


def dossiers_portee(faits):
    objets = {k[6:]: v for k, v in faits.items() if k.startswith('objet:')}
    resultat = {}
    for nom in ('atelier', 'franchissements', 'passages_obstacles'):
        if not faits.get(nom):
            continue
        dossier = faits[nom]
        if nom == 'atelier':
            ids = set().union(*(set(dossier.get(k, [])) for k in ('ressources', 'assemblages', 'appuis')))
        elif nom == 'franchissements':
            ids = {p[k] for p in dossier.get('possibilites', []) for k in ('obstacle', 'outil') if p.get(k)}
        else:
            ids = {p['cible'] for p in dossier if p.get('cible')}
        ids |= references_objets(dossier, objets)
        flags = [objets.get(i, {}).get('a_portee_de_main') for i in ids]
        resultat[nom] = {'references': sorted(ids), 'statut':
                         'proche' if True in flags else 'aucun_proche' if flags and all(f is False for f in flags) else 'inconnu'}
    return resultat


def mesurer(fichiers, ordonner=None):
    lignes, tours, empreintes = [], [], {}
    for groupe, fichier in fichiers:
        raw = fichier.read_bytes()
        empreintes[str(fichier)] = hashlib.sha256(raw).hexdigest()
        partie = json.loads(raw)
        precedents = {}
        for numero, tour in enumerate(partie['tours']):
            appels = [e for e in tour.get('fil', []) if e.get('etape') == 'appel']
            validations = [e for e in tour.get('fil', []) if e.get('etape') == 'validation']
            # Signature du contrat de proximite.exiger, sans inférer la classe d'un texte MJ.
            hors = [e for e in validations if 'hors de portée de main' in e.get('attendu', '')]
            if hors:
                fil = tour['fil']
                dernier = max(i for i, e in enumerate(fil) if e in hors)
                suivants = [e for e in fil[dernier + 1:] if e.get('etape') == 'appel']
                tours.append({'groupe': groupe, 'fichier': str(fichier), 'tour': numero,
                              'appels': len(appels), 'dernier_refus_hors_portee': validations[-1] in hors,
                              'appels_apres_refus': len(suivants),
                              'jetons_entree_apres_refus': sum((e.get('usage') or {}).get('input_tokens', 0) for e in suivants),
                              'texte': tour.get('texte'), 'secondes': tour.get('secondes'),
                              'obstacles': [e['obstacle'] for e in hors]})
            for index, e in enumerate(appels):
                v = voie(e)
                p = payload(e)
                s = serialiser(p)
                faits = e['entree'].get('faits') or {}
                blocs = {k: len(serialiser(val)) for k, val in faits.items()}
                objets = {k: val for k, val in faits.items() if k.startswith('objet:')}
                surfaces = {k: val for k, val in objets.items() if k.endswith(('_murs', '_sol', '_plafond'))}
                usage = e.get('usage') or {}
                row = {'groupe': groupe, 'fichier': str(fichier), 'script': partie['script'],
                       'tour': numero, 'appel': index, 'voie': v,
                       'instructions': len(e['instructions']), 'schema': len(serialiser(p['tools'])),
                       'schema_parametres': len(serialiser(p['tools'][0]['tools'][0]['parameters'])),
                       'entree': len(serialiser(e['entree'])), 'requete': len(s), 'blocs': blocs,
                       'objets': sum(len(serialiser(o)) for o in objets.values()),
                       'surfaces': sum(len(serialiser(o)) for o in surfaces.values()),
                       'portee': dossiers_portee(faits), 'usage': usage,
                       'jetons_entree': usage.get('input_tokens', 0),
                       'jetons_caches': (usage.get('input_tokens_details') or {}).get('cached_tokens', 0)}
                attribution = usage.get('attribution')
                row['attribution_presente'] = isinstance(attribution, dict)
                row['cache_attribue'] = {}
                if attribution:
                    for k, val in attribution.get('request_fields', {}).items():
                        row['cache_attribue'][k] = val.get('cached_tokens', 0)
                    items = attribution.get('items', {})
                    row['cache_attribue']['items.msg'] = sum(val.get('cached_tokens', 0) for k, val in items.items() if k.startswith('msg_'))
                outils = serialiser(p['tools'])
                entree = serialiser(e['entree'])
                ordonnee = serialiser(ordonner(e['entree'])) if ordonner else entree
                flux = {'luna': outils + '\n' + e['instructions'] + '\n' + entree,
                        'local': e['instructions'] + '\n' + entree,
                        'local_ordonnee': e['instructions'] + '\n' + ordonnee,
                        'entree': entree, 'entree_ordonnee': ordonnee}
                row['estimations_jetons'] = {k: row[k] / 4 for k in ('instructions', 'schema', 'entree', 'requete', 'objets', 'surfaces')}
                row['estimations_blocs_jetons'] = {k: n / 4 for k, n in blocs.items()}
                if v in precedents:
                    avant, ancien, ancien_flux = precedents[v]
                    ap, ep = avant['schema'].get('properties', {}), e['schema'].get('properties', {})
                    row.update(prefixe=prefixe(ancien, s),
                               instructions_changees=avant['instructions'] != e['instructions'],
                               schema_change=avant['schema'] != e['schema'],
                               premiere_divergence=difference(payload(avant), p),
                               divergence_schema=difference(avant['schema'], e['schema']) if avant['schema'] != e['schema'] else None,
                               variations_schema=[k for k in ('mode', 'proposition', 'faits') if ap.get(k) != ep.get(k)],
                               prefixe_consignes=prefixe(avant['instructions'], e['instructions']))
                    row['prefixes_flux'] = {k: prefixe(ancien_flux[k], val) for k, val in flux.items()}
                    row['cause_luna'] = 'outils' if payload(avant)['tools'] != p['tools'] else 'consignes' if avant['instructions'] != e['instructions'] else 'entree' if avant['entree'] != e['entree'] else 'identique'
                precedents[v] = e, s, flux
                lignes.append(row)
    groupes = {}
    for groupe, _ in fichiers:
        if groupe in groupes:
            continue
        synthese = {}
        for v in sorted({r['voie'] for r in lignes if r['groupe'] == groupe}):
            rs = [r for r in lignes if r['groupe'] == groupe and r['voie'] == v]
            paires = [r for r in rs if 'prefixe' in r]
            synthese[v] = {'appels': len(rs), 'paires': len(paires),
                          **{k: round(statistics.mean(r[k] for r in rs), 2) for k in ('instructions', 'schema', 'entree', 'requete', 'objets', 'surfaces')},
                          'prefixe_moyen': round(statistics.mean(r['prefixe'] for r in paires), 2) if paires else None,
                          'prefixe_mediane': statistics.median(r['prefixe'] for r in paires) if paires else None,
                          'instructions_changees': sum(r['instructions_changees'] for r in paires),
                          'schema_change': sum(r['schema_change'] for r in paires),
                          'causes': dict(Counter(r['premiere_divergence'] or 'identique' for r in paires)),
                          'causes_schema': dict(Counter(r['divergence_schema'] for r in paires if r['schema_change'])),
                          'variations_schema': dict(Counter(k for r in paires for k in r['variations_schema'])),
                          'causes_luna': dict(Counter(r['cause_luna'] for r in paires)),
                          'prefixes_flux_moyens': {k: round(statistics.mean(r['prefixes_flux'][k] for r in paires), 2) for k in ('luna', 'local', 'local_ordonnee', 'entree', 'entree_ordonnee')} if paires else {},
                          'attributions_presentes': sum(r['attribution_presente'] for r in rs),
                          'cache_attribue': dict(sum((Counter(r['cache_attribue']) for r in rs), Counter())),
                          'jetons_entree': sum(r['jetons_entree'] for r in rs),
                          'jetons_caches': sum(r['jetons_caches'] for r in rs),
                          'blocs': {k: round(sum(r['blocs'].get(k, 0) for r in rs) / len(rs), 2) for k in sorted(set().union(*(r['blocs'] for r in rs)))},
                          'portee': {nom: dict(Counter(r['portee'][nom]['statut'] for r in rs if nom in r['portee'])) for nom in ('atelier', 'franchissements', 'passages_obstacles')}}
        groupes[groupe] = synthese
    if any(hashlib.sha256(Path(p).read_bytes()).hexdigest() != h for p, h in empreintes.items()):
        raise ValueError('Une archive source a changé pendant la mesure')
    return {'groupes': groupes, 'appels': lignes, 'hors_portee': tours, 'sha256_sources': empreintes,
            'estimation_jetons': 'caracteres / 4 ; approximation, pas une tokenisation du modèle'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--sortie', type=Path, required=True)
    parser.add_argument('--argon', help='Référence git du module sources.py à mesurer, sans fusion')
    parser.add_argument('--trace-argon', type=Path)
    args = parser.parse_args()
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        kernel.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        if not kernel.SetPriorityClass(kernel.GetCurrentProcess(), 0x4000):
            raise OSError('Impossible de réduire la priorité')
    fichiers = [('141', p) for p in sorted(args.corpus.glob('*-p[12]/*.json'))]
    manifeste = json.loads((args.corpus / 'cache-avant.json').read_text(encoding='utf-8'))
    for nom, empreinte in manifeste.items():
        p = Path(nom)
        if not p.name.startswith('partie-'):
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != empreinte:
            raise ValueError('Référence modifiée : ' + nom)
        fichiers.append((p.parents[2].name[:7], p))
    ordonner = None
    source = None
    if args.argon:
        source = subprocess.check_output(['git', 'show', args.argon + ':donjon/sources.py'], cwd=Path(__file__).resolve().parents[1]).decode('utf-8')
        module = types.ModuleType('sources_argon_mesure')
        exec(compile(source, args.argon + ':donjon/sources.py', 'exec'), module.__dict__)
        ordonner = module.ordonner_entree
    if args.trace_argon:
        fichiers += [('9d53229', p) for p in sorted(args.trace_argon.rglob('*.json')) if p.name != 'resume.json']
    resultat = mesurer(fichiers, ordonner)
    resultat['argon'] = args.argon
    args.sortie.mkdir(parents=True, exist_ok=True)
    (args.sortie / 'mesures.json').write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding='utf-8')
    if source:
        (args.sortie / 'sources-argon.py').write_text(source, encoding='utf-8')
    print(len(fichiers), 'parties ;', len(resultat['appels']), 'appels ; aucun réseau')


if __name__ == '__main__':
    main()
