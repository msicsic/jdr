"""Captures exactes du lot 118, CPU nu, Ã©tat et rendu rechargÃ©s.

Chaque version s'exÃ©cute dans son interprÃ©teur : --depot ARCHIVE --sortie JSON.
Les diffÃ©rences de travail (graphes/preuves) restent sÃ©parÃ©es des rÃ©sultats.
"""
import argparse
from contextlib import ExitStack
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--depot', default='.')
    ap.add_argument('--sortie', required=True)
    args = ap.parse_args()
    racine = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(Path(args.depot).resolve()))
    from donjon import banc_pnj, planification as p
    from donjon.monde import Monde
    from donjon.moteur import Moteur, proposition
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    from tools.comparer_gestes_noeud import captures
    banc_pnj.ceder()
    sortie = Path(args.sortie).resolve()
    sortie.parent.mkdir(parents=True, exist_ok=True)
    donnees = {'captures': captures(p, racine / 'tests/data/cout-12h'), 'tours': {}}
    def empreinte(x):
        return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    debut = time.process_time()
    for scenario, minute in (('mine', 480), ('auberge', 480), ('auberge', 600)):
        fichier = racine / f'tests/data/cout-12h/{scenario}-1985-{minute}.json.gz'
        m = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
        recherches = []
        chercher = p.chercher
        def suivre(*a, **k):
            r = chercher(*a, **k)
            if r is None:
                recherches.append([a[1], k.get('nom'), None])
            else:
                cout, etapes, e = r
                recherches.append([a[1], k.get('nom'), [float(cout).hex(), etapes,
                    e.salle, sorted(e.portes), sorted([(list(k), v) for k, v in e.faits.items()], key=repr), e.allure]])
            return r
        with ExitStack() as pile:
            for nom in ('_MEMOIRE', '_GRAPHES', '_IMPOSSIBLES'):
                pile.enter_context(patch.object(p, nom, {}))
            pile.enter_context(patch.object(p, 'chercher', suivre))
            moteur = Moteur(m)
            lignes = moteur.executer(moteur.preparer(proposition('attendre')))
        sauvegarde = sortie.with_name(f'{sortie.stem}-{scenario}-{minute}.monde.json')
        m.sauver(sauvegarde)
        recharge = Monde.charger(sauvegarde)
        assert recharge.data == m.data
        assert regarder(recharge) == regarder(m)
        assert scene_percue(recharge) == scene_percue(m)
        donnees['tours'][f'{scenario}-{minute}'] = {
            'recherches': empreinte(recherches), 'monde': empreinte(recharge.data),
            'lignes': empreinte(lignes), 'regarder': empreinte(regarder(recharge)),
            'scene': empreinte(scene_percue(recharge))}
    donnees['cpu_tours'] = time.process_time() - debut
    sortie.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding='utf8')
    print(args.sortie, 'CPU tours', donnees['cpu_tours'], flush=True)


if __name__ == '__main__':
    main()
