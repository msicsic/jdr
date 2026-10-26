"""Tables exclusives et repères inclusifs des profils du lot 98."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


def famille(f):
    module = Path(f['fichier']).stem
    nom = f['nom']
    if module == 'planification':
        if nom in ('_entrees', '_entrees_communes'):
            return 'Empreintes recherche'
        if nom in ('_sans_plan', '_parcours', '_preparer_graphe_preuve'):
            return 'Graphes et certificats'
        if nom in ('vue', 'vues_du_choix', '__init__'):
            return 'Preparation Vue'
        return 'Recherche hors Vue/cle/preuve'
    if module == 'deliberation':
        return 'Choix hors recherches'
    if module in ('obstacles', 'geometrie', 'chemins', 'trajet_estime'):
        return 'Routes et geometrie'
    if module == 'part_estimee':
        return 'Devis des remises'
    if module in ('esprits', 'spatial', 'signes', 'perception', 'vue'):
        return 'Perception/esprits/spatial/signes'
    if module in ('ouie', 'voix'):
        return 'Ouie/voix'
    if module in ('pnj', 'moteur', 'marche', 'actions'):
        return 'Execution/marche'
    if module == 'banc_pnj':
        return 'Banc et empreintes monde'
    if module in ('encoder', 'decoder', 'copy', 'json'):
        return 'JSON/copies (tous appelants)'
    if f['fichier'] == '~':
        return 'Primitives (tous appelants)'
    return 'Autres'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=Path)
    args = ap.parse_args()
    bilan = {}
    for depart in ('fixe', 'tire'):
        versions = {}
        for version in ('ancien', 'actuel'):
            d = json.loads((args.dossier / f'{version}-{depart}.json').read_text(encoding='utf8'))
            temoin_path = args.dossier / f'temoin-{version}-{depart}.json'
            controle = None
            if temoin_path.exists():
                temoin = json.loads(temoin_path.read_text(encoding='utf8'))
                assert all(temoin['recharge'].values())
                assert all(d['recharge'].values())
                for champ in ('choix', 'recherches', 'mesures'):
                    assert d[champ] == temoin[champ], (depart, version, champ)
                empreintes = {}
                for minute in (480, 720):
                    etats = [json.loads((args.dossier / f'{prefix}{version}-{depart}.{minute}.json')
                                       .read_text(encoding='utf8')) for prefix in ('', 'temoin-')]
                    assert etats[0] == etats[1], (depart, version, minute)
                    empreintes[minute] = hashlib.sha256(json.dumps(etats[0], sort_keys=True,
                        ensure_ascii=False).encode()).hexdigest()
                controle = dict(cpu_total=temoin['cpu_total'], cpu_tranche=temoin['cpu_tranche'],
                                identite=True, empreintes=empreintes)
            groupes, fonctions = defaultdict(float), defaultdict(lambda: [0, 0, 0])
            for f in d['fonctions']:
                groupes[famille(f)] += f['propre']
                cle = Path(f['fichier']).stem + ':' + f['nom']
                for i, champ in enumerate(('propre', 'cumule', 'appels')):
                    fonctions[cle][i] += f[champ]
            versions[version] = dict(cpu=d['cpu_tranche'], familles=groupes, fonctions=fonctions,
                choix=d['choix'], recherches=d['recherches'], recharge=d['recharge'], temoin=controle)
        a, b = (versions[k] for k in ('ancien', 'actuel'))
        ecarts = sorted(((k, b['fonctions'].get(k, [0]*3)[0]-a['fonctions'].get(k, [0]*3)[0])
                         for k in set(a['fonctions']) | set(b['fonctions'])), key=lambda x:-x[1])
        bilan[depart] = dict(versions=versions, dix_ecarts_propres=ecarts[:10])
    (args.dossier / 'bilan.json').write_text(json.dumps(bilan, ensure_ascii=False, indent=2), encoding='utf8')
    for depart, d in bilan.items():
        print(depart)
        for v, x in d['versions'].items():
            print(v, 'CPU', x['cpu'], 'choix', x['choix'], 'recherches', x['recherches'])
            print('familles', dict(x['familles']))
            print('inclusifs', sorted(x['fonctions'].items(), key=lambda x:-x[1][1])[:25])
        print('ecarts propres', d['dix_ecarts_propres'])


if __name__ == '__main__':
    main()
