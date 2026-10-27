"""Témoin sans sonde contre témoin apparié ; état et sorties visibles."""
import argparse
import json
from unittest.mock import patch

import mesure_saillance_210 as s


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=s.Path)
    args = ap.parse_args()
    s.ceder()
    creer = s.b.creer
    capture = {}
    def creation(*a, **k):
        capture['monde'] = creer(*a, **k)
        return capture['monde']
    controles = []
    for scenario in ('mine', 'auberge'):
        for cache in (s.p._MEMOIRE, s.p._GRAPHES, s.p._IMPOSSIBLES):
            cache.clear()
        with patch.object(s.b, 'creer', creation):
            _, mesures, donnees = s.b.nuit(scenario, 1985, .1, s.JOUEURS[scenario], False, True, None, 'fixe')
        monde = capture['monde']
        s.sauver(args.dossier / (scenario + '-sans-sonde.json.gz'),
                 dict(etat=monde.data, donnees=donnees))
        for cache in (s.p._MEMOIRE, s.p._GRAPHES, s.p._IMPOSSIBLES):
            cache.clear()
        n = s.nuit(scenario, 1985, .1, 'complete', args.dossier, apparier=True)
        comparees = dict(n['donnees'])
        # Seules les trois annotations de l'observateur 199 sont ajoutées
        # au bilan du banc ; elles ne sont pas produites sans cet observateur.
        annotations = {'avis_non_justifies', 'avis_a_expliquer', 'avis_cycles_accomplis'}
        comparees['mesures'] = {k: v for k, v in comparees['mesures'].items() if k not in annotations}
        controles.append(dict(scenario=scenario, etat=n['etat'] == monde.data,
                              donnees={k: comparees[k] == donnees[k] for k in
                                       ('chronique', 'recit', 'souvenirs', 'mesures', 'empreintes')}))
    (args.dossier / 'controles.json').write_text(json.dumps(controles, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(controles, ensure_ascii=False))
    assert all(c['etat'] and all(c['donnees'].values()) for c in controles)


if __name__ == '__main__':
    main()
