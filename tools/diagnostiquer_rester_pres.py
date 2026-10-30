"""Captures des interruptions/reprises du 266 ; observation seule, sans nouvelle référence."""
import argparse
import copy
import json
from pathlib import Path
import sys
from concurrent.futures import ProcessPoolExecutor
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.append(str(RACINE / 'tools'))
from priorite import ceder


def jouer(tache):
    from donjon import banc_pnj, deliberation as d, signes
    from donjon.memoire import episodes
    from donjon.esprits import lire
    from donjon.temps import instant
    ceder()
    scenario, graine, heures, fenetres, dossier = tache
    dossier = Path(dossier) / f'{scenario}-{graine}'
    dossier.mkdir(parents=True, exist_ok=True)
    choisir = d.choisir
    fil, numero = [], 0

    def resume(m, id):
        e = lire(m, id)
        i = e['intention']
        contrat = d.agendas.contrat_intention(m, id) or {}
        demande = contrat.get('demande')
        return copy.deepcopy({'instant': instant(m), 'minute': m.data['minutes'], 'acteur': id,
            'position': {k:m.objets[id].get(k) for k in ('lieu','position','orientation')},
            'intention': i, 'contrat': contrat, 'dernier_contrat': e.get('contrat_intention'),
            'fin': d._fin_demande(m,id,demande) if demande else None,
            'detresses': sorted(d.detresses_percues(m,id)), 'calme': d.calme_pour_secourir(m,id),
            'signes': signes.percus(m,id), 'lectures': signes.actives(m,id),
            'besoins': e['besoins'], 'urgents': d.urgents(m,id), 'manque': e['manque'],
            'memoire_recente': episodes(m, id)[-10:]})

    def observer(m, id, minute):
        nonlocal numero
        actif = id in fenetres and fenetres[id][0] <= instant(m)/600 <= fenetres[id][1]
        if not actif:
            return choisir(m,id,minute)
        avant = resume(m,id)
        data = copy.deepcopy(m.data)
        resultat = choisir(m,id,minute)
        apres = resume(m,id)
        entree = {'avant': avant, 'apres': apres}
        if (avant['intention'] or {}).get('but') != (apres['intention'] or {}).get('but'):
            nom = f'{numero:04d}-{id}-{instant(m)}'
            entree['capture'] = nom
            (dossier / f'{nom}-avant.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            (dossier / f'{nom}-apres.json').write_text(json.dumps(m.data,ensure_ascii=False),encoding='utf-8')
            numero += 1
        fil.append(entree)
        return resultat

    with patch.object(d, 'choisir', observer):
        _, _, donnees = banc_pnj.nuit(scenario,graine,heures,'chambre_cloche',depart='tire')
    (dossier / 'fil.json').write_text(json.dumps(fil,ensure_ascii=False,indent=2),encoding='utf-8')
    (dossier / 'donnees.json').write_text(json.dumps(donnees,ensure_ascii=False),encoding='utf-8')
    return {'scenario':scenario,'graine':graine,'choix':len(fil),'transitions':numero}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sortie',type=Path,required=True)
    args=ap.parse_args()
    ceder()
    args.sortie.mkdir(parents=True,exist_ok=True)
    taches=[('crue',1985,85/60,{'brune':(78,84)},str(args.sortie)),
            ('crue_hameau',7,4,{'aubin':(37,41),'mael':(37,62),'marchand':(80,240)},str(args.sortie)),
            ('crue_hameau',2024,205/60,{'mael':(197,204)},str(args.sortie))]
    with ProcessPoolExecutor(max_workers=2) as pool:
        resultat=list(pool.map(jouer,taches))
    (args.sortie/'fin.json').write_text(json.dumps(resultat,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(resultat,ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
