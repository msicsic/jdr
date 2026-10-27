"""Rejouer les trouvailles enregistrées, sur copies, avec les variantes du lot 190."""
import argparse
import gzip
import inspect
import json
from pathlib import Path
import sys
import types
from unittest.mock import patch

from mesure_reflexion_190 import profondeur, ceder, b, p
from donjon.esprits import croire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.recit_pnj import Recit
# tools/tests.py masque sinon le dossier de fixtures, qui est sans __init__.
fixtures = types.ModuleType('tests')
fixtures.__path__ = [str(Path(__file__).resolve().parents[1] / 'tests')]
sys.modules['tests'] = fixtures
from tests.test_planification import relais


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=Path)
    args = ap.parse_args()
    ceder()
    m = relais()
    m.objets['torche'].update(allume=False, combustible=30)
    croire(m, 'brune', 'torche', 'lieu', 'antichambre', 'vu', salle='antichambre', case=None)
    croire(m, 'brune', 'torche', 'etat', {'allume': False, 'charge': True}, 'vu')
    croire(m, 'brune', 'brasero', 'etat', {'allume': True, 'charge': True}, 'vu')
    croire(m, 'brune', 'antichambre', 'etat', {'eclairee': False}, 'vu')
    source = Path(__file__).resolve().parents[1] / 'tests/data/taches_relais42_avant_part.json.gz'
    gorm = Monde(json.loads(gzip.decompress(source.read_bytes())))
    cas = [('lumiere_avant_crochetage', m, 'brune', 'faim'),
           ('relais42_151_avant_part', gorm, 'marchand', 'brasero')]
    lignes = []
    chercher = p.chercher
    sig = inspect.signature(chercher)
    for nom, base, ident, but in cas:
        entree = args.dossier / (nom + '-entree.json')
        base.sauver(entree)
        for variante in ('complete', 'int', 'enjeu'):
            monde = Monde.charger(entree)
            for cache in (p._MEMOIRE, p._GRAPHES, p._IMPOSSIBLES):
                cache.clear()
            def recherche(*a, **k):
                lie = sig.bind(*a, **k)
                lie.apply_defaults()
                x = lie.arguments
                x['profondeur'] = profondeur(x['monde'], x['id'], x['motif'], variante, x['profondeur'])
                return chercher(**x)
            with patch.object(p, 'chercher', recherche):
                plan = (p.planifier(monde, ident, but) if but == 'faim' else
                        p.planifier_pulsion(monde, ident, {'objet': but, 'allume': True}))
                # Dix minutes par la même chaîne d'exécution que les nuits libres.
                recit = Recit(monde)
                chronique, mesures = b.executer(monde, monde.data['minutes'] + 10, recit)
                decoupe = Monde.charger(entree)
                for _ in range(2):
                    for cache in (p._MEMOIRE, p._GRAPHES, p._IMPOSSIBLES):
                        cache.clear()
                    b.executer(decoupe, decoupe.data['minutes'] + 5, Recit(decoupe))
                    reprise = args.dossier / (nom + '-' + variante + '-reprise.json')
                    decoupe.sauver(reprise)
                    decoupe = Monde.charger(reprise)
            sortie = args.dossier / (nom + '-' + variante + '-final.json')
            monde.sauver(sortie)
            rendu = (regarder(monde), scene_percue(monde))
            recharge = Monde.charger(sortie)
            assert monde.data == recharge.data
            assert rendu == (regarder(recharge), scene_percue(recharge))
            lignes.append(dict(cas=nom, variante=variante, plan=plan, chronique=chronique,
                               mesures=mesures, recharge=True, rendu=rendu,
                               decoupe_identique=monde.data == decoupe.data,
                               rendu_decoupe_identique=rendu == (regarder(decoupe), scene_percue(decoupe))))
    (args.dossier / 'scenes.json').write_text(json.dumps(lignes, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps([dict(cas=r['cas'], variante=r['variante'], plan=r['plan']) for r in lignes], ensure_ascii=False))


if __name__ == '__main__':
    main()
