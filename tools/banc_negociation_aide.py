"""Une passe K2 sur copies : alternatives nouvelles face à K0, appels et verdict.

python tools/banc_negociation_aide.py --sortie artifacts/k2-assistance-434/luna
Les scènes sont celles des preuves K0/K1/K2 ; aucun accès à sauvegardes/.
"""
import argparse
import copy
import json
from pathlib import Path
import sys
import time

BASE = Path(__file__).resolve().parents[1]
# Ne pas confondre le namespace tests/ avec le lanceur tools/tests.py.
sys.path[:] = [p for p in sys.path if Path(p or '.').resolve() != BASE / 'tools']
sys.path.insert(0, str(BASE))
import tests
sys.path.append(str(BASE / 'tools'))
from priorite import ceder
from donjon.accords_publics import accords_publics, AccordTerminal, termes_parametres
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from tests.test_negociation_aide import situations
from tests.test_editeur_marche import vues
from tests import test_information_publique as support_web


def cle(initial):
    if 'demande' in initial:
        termes = (initial['demande'], initial['contrepartie'])
    else:
        termes = termes_parametres({'prestation': initial['prestation'], 'prix': initial['prix']})
    return json.dumps([initial['destinataire'], *termes], sort_keys=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--connexion', default='chatgpt', choices=('chatgpt', 'api'))
    args = p.parse_args()
    ceder()
    args.sortie.mkdir(parents=True, exist_ok=True)
    scenes = list(situations())
    demandes = [
        'Aide-moi à négocier avec Aubin une part de ses planches sans payer de pièces ; propose un échange ou un travail ponctuel que je pourrais lui promettre.',
        'Aide-moi à négocier une part d’huile avec Odile sans payer de pièces. Je pourrais céder ma lanterne ou promettre un travail ponctuel.',
        'Aide-moi à négocier avec Aubin : je le paierai seulement s’il ramène Brune avant la crue.',
    ]
    bilan = []
    for i, saisie in enumerate(demandes):
        m = scenes[i % 2][0].copier()
        avant = copy.deepcopy(m.data)
        m.sauver(args.sortie / f'{i}-avant.json')
        k0 = accords_publics(m)['suggestions']
        trace = []
        mj = MJOpenAI('gpt-6-luna', connexion=args.connexion)
        mj.journal_complet = True
        mj.observateur = lambda evenement: trace.append(copy.deepcopy(evenement))
        mesure = {'saisie': saisie, 'reference_k0': k0}
        debut = time.monotonic()
        try:
            r = mj._echanger_prepare(m, saisie)
            mesure['reponse'] = r
            mesure['monde_inchange_avant_selection'] = m.data == avant
            b = r.get('_formulaire_accord')
            suggestions = b['public'].get('suggestions', []) if b and not b['initial'] else []
            hors_k0 = [s for s in suggestions if cle(s['initial']) not in {cle(x['initial']) for x in k0}]
            mesure['alternatives_admises'] = len(suggestions)
            mesure['alternatives_hors_k0'] = len(hors_k0)
            if suggestions:
                f = AccordTerminal(b['public'], b['initial'])
                f.saisir('suggestion 1')
                d = f.saisir('valider')
                n, lignes, _ = support_web.InformationPubliqueTests().boucle(m, [d, 'tenter'])
                mesure['soumission'] = d.contenu
                mesure['verdict'] = '\n'.join(lignes)
                n.sauver(args.sortie / f'{i}-apres.json')
                recharge = Monde.charger(args.sortie / f'{i}-apres.json')
                mesure['recharge_et_vues_identiques'] = n.data == recharge.data and vues(n) == vues(recharge)
        except Exception as exc:
            mesure['erreur'] = f'{type(exc).__name__}: {exc}'
        mesure['secondes'] = round(time.monotonic() - debut, 3)
        mesure['appels'] = sum(e.get('etape') == 'appel' for e in trace)
        mesure['appels_jusqua_alternative_hors_k0'] = mesure['appels'] if mesure.get('alternatives_hors_k0') else None
        (args.sortie / f'{i}-fil.json').write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding='utf-8')
        bilan.append(mesure)
        (args.sortie / 'bilan.json').write_text(json.dumps(bilan, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in mesure.items() if k not in ('reference_k0', 'reponse', 'verdict')}, ensure_ascii=False), flush=True)
    (args.sortie / 'fin.json').write_text(json.dumps({'termine': True, 'scenes': len(bilan),
        'erreurs': sum('erreur' in m for m in bilan)}), encoding='utf-8')


if __name__ == '__main__':
    main()
