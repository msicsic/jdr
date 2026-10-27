"""Relire les bruts du lot 190, sans rejouer de nuit ni appeler un modèle."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from empreintes_nuits import _h
from priorite import ceder


def lire(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def bilan(dossier):
    lignes, paires, identites, libres = [], [], [], []
    for path in sorted(dossier.glob('*.json.gz')):
        if path.name.startswith('fumee'):
            continue
        n = lire(path)
        # Le cycle JSON est le même format d'état que les sauvegardes.
        m = Monde(n['etat'])
        rendu = (regarder(m), scene_percue(m))
        re = Monde(json.loads(json.dumps(m.data, ensure_ascii=False)))
        assert m.data == re.data
        assert rendu == (regarder(re), scene_percue(re))
        lignes.append(dict(fichier=path.name, scenario=n['scenario'], variante=n['variante'],
                           cpu=n['cpu'], recherches=sum(x['recherches'] for x in n['compteurs']),
                           neuves=sum(x['neuves'] for x in n['compteurs']),
                           noeuds=sum(x.get('noeuds', 0) for x in n['compteurs']),
                           certificats=sum(x['certificats'] for x in n['compteurs']),
                           graphes=sum(x['graphes'] for x in n['compteurs']),
                           odon_argent=[x for x in n['compteurs'] if x['pnj'] == 'odon' and x['but'] == 'argent'],
                           richesse=n['richesse'], audit=dict(Counter(x['code'] for x in n['audit'])),
                           mesures=n['donnees']['mesures'], recharge=True,
                           rendu_sha256=_h(rendu)))
        if '-apparie' in path.name:
            temoin = lire(dossier / (n['scenario'] + '-complete.json.gz'))
            identites.append(dict(scenario=n['scenario'], etat=n['etat'] == temoin['etat'],
                                  donnees={k: n['donnees'][k] == temoin['donnees'][k]
                                           for k in ('chronique', 'recit', 'souvenirs', 'mesures', 'empreintes')}))
            for variante in ('int', 'enjeu'):
                rr = [r for r in n['paires'] if r['variante'] == variante]
                perdus = [r for r in rr if r['complete'] is not None and r['limite'] is None]
                doubles = [r for r in rr if r['complete'] is not None and r['limite'] is not None]
                deltas = [r['limite']['cout'] - r['complete']['cout'] for r in doubles]
                paires.append(dict(scenario=n['scenario'], variante=variante, n=len(rr),
                                   changes=sum(r['complete'] != r['limite'] for r in rr),
                                   profondeur_inchangee_changes=sum(r['profondeur'] == 8 and r['complete'] != r['limite'] for r in rr),
                                   premier_geste_change=sum((r['complete'] or {}).get('etapes', [])[:1] !=
                                                            (r['limite'] or {}).get('etapes', [])[:1] for r in rr),
                                   perdus=len(perdus), reference_bornee=sum(r['reference_bornee'] for r in rr),
                                   communs=len(doubles), delta_somme=sum(deltas), delta_max=max(deltas, default=0),
                                   nouveaux=sum(r['complete'] is None and r['limite'] is not None for r in rr),
                                   raisons=dict(Counter('chaine_plus_longue' if len(r['complete']['etapes']) > r['profondeur']
                                                        else 'recherche_ou_devis_a_expliquer' for r in perdus)),
                                   exemples_perdus=perdus[:6],
                                   trouvailles=[r for r in rr if r['complete'] and
                                                any(e['operation'] == 'crocheter' for e in r['complete']['etapes']) and
                                                any(e['operation'] == 'allumer' for e in r['complete']['etapes'])]))
    for scenario in ('mine', 'auberge', 'crue_hameau'):
        temoin = lire(dossier / (scenario + '-complete.json.gz'))
        for variante in ('int', 'enjeu'):
            n = lire(dossier / (scenario + '-' + variante + '.json.gz'))
            a, c = temoin['donnees']['chronique'], n['donnees']['chronique']
            premier = next((dict(complete=x, variante=y) for x, y in zip(a, c) if x != y), None)
            libres.append(dict(scenario=scenario, variante=variante, etat=temoin['etat'] == n['etat'],
                               identites={k: temoin['donnees'][k] == n['donnees'][k] for k in
                                          ('chronique', 'recit', 'souvenirs', 'mesures', 'empreintes')},
                               premier_ecart= premier, longueurs_chroniques=[len(a), len(c)]))
    return dict(nuits=lignes, appariements=paires, identites=identites, libres=libres)


if __name__ == '__main__':
    ceder()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=Path)
    args = ap.parse_args()
    resultat = bilan(args.dossier)
    (args.dossier / 'bilan.json').write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(nuits=len(resultat['nuits']), identites=resultat['identites']), ensure_ascii=False))
