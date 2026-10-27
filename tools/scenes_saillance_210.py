"""Captures rechargeables des trouvailles du lot 210, sur copies uniquement."""
import argparse
import copy
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
import sys
import types
from unittest.mock import patch

import mesure_saillance_210 as s
from donjon.esprits import croire, lire
from donjon.recit_pnj import Recit

fixtures = types.ModuleType('tests')
fixtures.__path__ = [str(Path(__file__).resolve().parents[1] / 'tests')]
sys.modules['tests'] = fixtures
from tests.test_planification import relais
from tests.test_petits_correctifs import BoisDeGormTests
from tests.test_entretenir import sans


def scenes():
    m = relais()
    m.objets['torche'].update(allume=False, combustible=30)
    croire(m, 'brune', 'torche', 'lieu', 'antichambre', 'vu', salle='antichambre', case=None)
    croire(m, 'brune', 'torche', 'etat', {'allume': False, 'charge': True}, 'vu')
    croire(m, 'brune', 'brasero', 'etat', {'allume': True, 'charge': True}, 'vu')
    croire(m, 'brune', 'antichambre', 'etat', {'eclairee': False}, 'vu')
    source = Path(__file__).resolve().parents[1] / 'tests/data/taches_relais42_avant_part.json.gz'
    reel = s.Monde(json.loads(gzip.decompress(source.read_bytes())))
    auteur = BoisDeGormTests().gorm_devant_le_brasero()
    # Contre-épreuve de ressource : seules les planches peuvent fournir du bois.
    # Donnée de scène explicitée, jamais une règle de la sonde.
    sans(auteur, 'bois')
    croire(auteur, 'marchand', 'planches', 'lieu', 'antichambre', 'vu', salle='antichambre', case=None)
    return [('lumiere_avant_crochetage', m, 'brune', 'faim'),
            ('gorm_capture_reelle_151', reel, 'marchand', 'brasero'),
            ('gorm_planches_seules_scene_auteur', auteur, 'marchand', 'brasero')]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dossier', type=Path)
    args = ap.parse_args()
    args.dossier.mkdir(parents=True, exist_ok=True)
    s.ceder()
    lignes = []
    for nom, base, ident, but in scenes():
        entree = args.dossier / (nom + '-entree.json')
        base.sauver(entree)
        for mode in ('complete', 'saillant', 'reference'):
            for c in (s.p._MEMOIRE, s.p._GRAPHES, s.p._IMPOSSIBLES):
                c.clear()
            def recherche(*a, **k):
                x = s.SIGNATURE.bind(*a, **k)
                x.apply_defaults()
                x = dict(x.arguments)
                if mode == 'reference':
                    x.update(noeuds=s.p.REFERENCE, emplois=None)
                return s.CHERCHER(**x)
            with ExitStack() as stack:
                stack.enter_context(s.variante(mode))
                for obj, cle, val in [(s.p.Vue, 'agissables', s.agissables),
                                      (s.p, '_entrees', s.entrees), (s.p, 'chercher', recherche)]:
                    stack.enter_context(patch.object(obj, cle, val))
                monde = s.Monde.charger(entree)
                plan = (s.p.planifier(monde, ident, but) if but == 'faim' else
                        s.p.planifier_pulsion(monde, ident, {'objet': but, 'allume': True}))
                s.d.choisir(monde, ident, monde.data['minutes'])
                choix = copy.deepcopy(lire(monde, ident)['intention'])
                avec_plan = copy.deepcopy(monde.data)
                chronique, mesures = s.b.executer(monde, monde.data['minutes'] + 10, Recit(monde))
                decoupe = s.Monde(copy.deepcopy(avec_plan))
                for _ in range(2):
                    for c in (s.p._MEMOIRE, s.p._GRAPHES, s.p._IMPOSSIBLES):
                        c.clear()
                    s.b.executer(decoupe, decoupe.data['minutes'] + 5, Recit(decoupe))
                    reprise = args.dossier / (nom + '-' + mode + '-reprise.json')
                    decoupe.sauver(reprise)
                    decoupe = s.Monde.charger(reprise)
            sortie = args.dossier / (nom + '-' + mode + '-final.json')
            monde.sauver(sortie)
            recharge = s.Monde.charger(sortie)
            rendu = (s.regarder(monde), s.scene_percue(monde))
            assert monde.data == recharge.data
            assert rendu == (s.regarder(recharge), s.scene_percue(recharge))
            lignes.append(dict(cas=nom, variante=mode, plan=plan, choix=choix,
                               chronique=chronique, mesures=mesures, recharge=True, rendu=rendu,
                               decoupe_identique=monde.data == decoupe.data,
                               rendu_decoupe_identique=rendu == (s.regarder(decoupe), s.scene_percue(decoupe))))
    (args.dossier / 'scenes.json').write_text(json.dumps(lignes, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps([dict(cas=r['cas'], variante=r['variante'], plan=r['plan'],
                           decoupe=r['decoupe_identique']) for r in lignes], ensure_ascii=False))


if __name__ == '__main__':
    main()
