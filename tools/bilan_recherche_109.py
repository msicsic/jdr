"""Agrège les recherches et leurs générations réelles, sans relancer les nuits."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path


def resumer(lignes):
    n = len(lignes)
    noeuds = sum(x.get('diagnostic', {}).get('noeuds', 0) for x in lignes)
    generations = sum(x['generations'] for x in lignes)
    successeurs = sum(x['successeurs'] for x in lignes)
    cpu = sum(x['cpu'] for x in lignes)
    developpes = sum(x.get('developpes', 0) for x in lignes)
    normalisations = sum(x.get('normalisations', 0) for x in lignes)
    suites = sum(x.get('suites', 0) for x in lignes)
    familles = Counter()
    explorations = defaultdict(lambda: dict(passes=0, noeuds=0, generations=0, cpu=0))
    for x in lignes:
        familles.update(x['familles'])
        for e in x.get('explorations', []):
            cle = ('furtif' if e['furtif'] else 'ordinaire') + ('/decouverte' if e['decouvrir'] else '/complete')
            groupe = explorations[cle]
            groupe['passes'] += 1
            for champ in ('noeuds', 'generations', 'cpu'):
                groupe[champ] += e[champ]
    def quantiles(valeurs):
        valeurs = sorted(valeurs)
        return {str(q): valeurs[max(0, math.ceil(q*len(valeurs))-1)] if valeurs else 0
                for q in (.5, .9, .99, 1)}
    return dict(nombre=n, noeuds=noeuds, noeuds_par_recherche=noeuds/n if n else 0,
        etats=sum(x.get('diagnostic', {}).get('etats', 0) for x in lignes),
        preuve_noeuds=sum(x.get('diagnostic', {}).get('preuve_noeuds', 0) for x in lignes),
        cpu=cpu, ms_par_recherche=cpu*1000/n if n else 0,
        us_par_noeud=cpu*1e6/noeuds if noeuds else None,
        generations=generations, successeurs=successeurs, developpes=developpes,
        developpes_par_recherche=developpes/n if n else 0,
        us_par_developpe=cpu*1e6/developpes if developpes else None,
        normalisations=normalisations, suites=suites,
        suites_par_normalisation=suites/normalisations if normalisations else None,
        quantiles_noeuds=quantiles([x.get('diagnostic', {}).get('noeuds', 0) for x in lignes]),
        quantiles_generations=quantiles([x['generations'] for x in lignes]),
        quantiles_ms=quantiles([x['cpu']*1000 for x in lignes]),
        explorations=dict(explorations),
        successeurs_par_generation=successeurs/generations if generations else 0,
        issues=dict(Counter(x.get('diagnostic', {}).get('issue', 'absent') for x in lignes)),
        familles=dict(familles))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=Path)
    args = ap.parse_args()
    resultat, donnees = {}, {}
    for fichier in args.dossier.glob('*.json'):
        if fichier.stem.endswith(('.480', '.720')) or fichier.stem == 'bilan':
            continue
        d = json.loads(fichier.read_text(encoding='utf8'))
        if not isinstance(d.get('recherches'), list):
            continue
        donnees[fichier.stem] = d
        groupes = defaultdict(list)
        for r in d['recherches']:
            groupes[r['pnj']+'/'+r['but']].append(r)
        f = sorted(d.get('fonctions', []), key=lambda x:-x['propre'])
        resultat[fichier.stem] = dict(total=resumer(d['recherches']),
            groupes={k:resumer(v) for k,v in groupes.items()},
            fonctions=f[:35], cpu_total=d['cpu_total'], cpu_tranche=d['cpu_tranche'],
            recharge=d['recharge'])
        print(fichier.stem, json.dumps(resultat[fichier.stem]['total'], ensure_ascii=False))
        for k,v in sorted(resultat[fichier.stem]['groupes'].items(), key=lambda x:-x[1]['cpu'])[:12]:
            print(k, json.dumps(v, ensure_ascii=False))
    controles = {}
    for nom, temoin in donnees.items():
        if not nom.startswith('detail-'):
            continue
        base = nom.removeprefix('detail-')
        if base not in donnees:
            continue
        reference = donnees[base]
        def trace(d):
            return [dict(pnj=r['pnj'], but=r['but'], minute=r['minute'],
                generations=r['generations'], successeurs=r['successeurs'], familles=r['familles'],
                diagnostic={k:v for k,v in r['diagnostic'].items() if k != 'duree'})
                for r in d['recherches']]
        assert trace(temoin) == trace(reference), nom
        for minute in (480, 720):
            etats = [json.loads((args.dossier/f'{n}.{minute}.json').read_text(encoding='utf8'))
                     for n in (nom, base)]
            assert etats[0] == etats[1], (nom, minute)
        controles[nom] = dict(traces=True, monde_480=True, monde_720=True)
    resultat['controles'] = controles
    (args.dossier/'bilan.json').write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf8')


if __name__ == '__main__':
    main()
