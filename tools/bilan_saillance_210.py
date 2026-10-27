"""Bilan des nuits et des choix appariés, sans rejouer le moteur."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from priorite import ceder


def lire(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def premier(plan):
    return None if plan is None else plan['etapes'][:1]


def indexer(recherches):
    occurrences = Counter()
    resultat = {}
    for r in recherches:
        cle = (r['but'], occurrences[r['but']])
        occurrences[r['but']] += 1
        resultat[cle] = r
    return resultat


def bilan(dossier):
    lignes, apparies, comparaisons = [], [], []
    nuits = {}
    for path in sorted(dossier.glob('*.json.gz')):
        n = lire(path)
        cle = (n['scenario'], n['graine'], n['heures'])
        nuits[(*cle, n['variante'])] = n
        r = n['richesse']
        lignes.append(dict(scenario=cle[0], graine=cle[1], heures=cle[2], variante=n['variante'],
                           compteurs=n['compteurs']['total'], cpu=n['cpu'],
                           S=r['S'], F=r['F'], D=sum(r['D'].values()) / max(1, len(r['D'])),
                           mesures=n['donnees']['mesures'], avis=n['avis'],
                           audit=dict(Counter(x['code'] for x in n['audit'])), recharge=n['recharge']))
        stats = Counter()
        exemples = []
        for paire in n['paires']:
            stats['choix'] += 1
            a, b = paire['saillant'], paire['reference']
            ia, ib = a['intention'], b['intention']
            stats['choix_changes'] += ia != ib
            stats['premier_geste_choix_change'] += (ia or {}).get('plan', [])[:1] != (ib or {}).get('plan', [])[:1]
            stats['but_change'] += (ia or {}).get('but') != (ib or {}).get('but')
            ar, br = indexer(a['recherches']), indexer(b['recherches'])
            stats['recherches_non_appariees'] += len(ar.keys() ^ br.keys())
            for k in ar.keys() & br.keys():
                x, y = ar[k], br[k]
                xp, yp = x['plan'], y['plan']
                stats['recherches_appariees'] += 1
                stats['plans_changes'] += xp != yp
                stats['premier_geste_recherche_change'] += premier(xp) != premier(yp)
                stats['plans_perdus'] += yp is not None and xp is None
                stats['plans_nouveaux'] += yp is None and xp is not None
                stats['references_bornees'] += y['borne']
                if xp is not None and yp is not None:
                    delta = xp['cout'] - yp['cout']
                    stats['surcout_somme'] += max(0, delta)
                    stats['surcout_max'] = max(stats['surcout_max'], delta)
                    stats['gains_somme'] += min(0, delta)
                if xp != yp and len(exemples) < 12:
                    exemples.append(dict(minute=paire['minute'], pnj=paire['pnj'], but=k,
                                          saillant=x, reference=y))
        if n['paires']:
            apparies.append(dict(scenario=cle[0], graine=cle[1], heures=cle[2], **stats, exemples=exemples))
    for (s, g, h, v), a in nuits.items():
        if v != 'complete' or (s, g, h, 'saillant') not in nuits:
            continue
        b = nuits[(s, g, h, 'saillant')]
        ac, bc = a['donnees']['chronique'], b['donnees']['chronique']
        ecart = next((dict(complete=x, saillant=y) for x, y in zip(ac, bc) if x != y), None)
        comparaisons.append(dict(scenario=s, graine=g, heures=h, etat_identique=a['etat'] == b['etat'],
                                 premier_ecart=ecart, longueurs=[len(ac), len(bc)]))
    return dict(nuits=lignes, appariements=apparies, libres=comparaisons)


if __name__ == '__main__':
    ceder()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=Path)
    args = ap.parse_args()
    resultat = bilan(args.dossier)
    (args.dossier.parent / 'bilan.json').write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf-8')
    # Agrégats seulement, les exemples détaillés restent dans le bilan.
    for groupe in (12, 4):
        print('HEURES', groupe)
        for scenario in ('relais', 'mine', 'auberge', 'crue', 'crue_hameau'):
            for mode in ('complete', 'saillant'):
                rr = [r for r in resultat['nuits'] if r['heures'] == groupe and r['scenario'] == scenario and r['variante'] == mode]
                if not rr:
                    continue
                total = Counter()
                for r in rr:
                    total.update(r['compteurs'])
                print(json.dumps(dict(scenario=scenario, variante=mode, n=len(rr),
                                      compteurs=total, cpu=sum(r['cpu'] for r in rr),
                                      S=sum(r['S'] for r in rr)/len(rr),
                                      F=sum(r['F'] for r in rr)/len(rr), D=sum(r['D'] for r in rr)/len(rr),
                                      suspects=sum(r['avis']['total_non_justifies'] for r in rr),
                                      mesures={k: sum(r['mesures'].get(k, 0) for r in rr) for k in
                                               ('minutes_urgentes_sans_recours',
                                                'minutes_urgentes_en_attente')}), ensure_ascii=False))
    print(json.dumps([dict((k, v) for k, v in a.items() if k != 'exemples')
                      for a in resultat['appariements']], ensure_ascii=False))
