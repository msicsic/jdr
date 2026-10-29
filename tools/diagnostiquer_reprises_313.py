"""Rejouer les seules nuits nécessaires, capturer et relire les contacts interrompus."""
import argparse
import copy
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RACINE), str(RACINE / 'tools')]


def ecrire(chemin, valeur):
    chemin.write_text(json.dumps(valeur, ensure_ascii=False, indent=2), encoding='utf8')


def travail(arguments):
    from priorite import ceder
    ceder()
    import comparer_bancs as c
    from donjon import banc_pnj as banc, deliberation as d, pnj, social
    from donjon.esprits import lire, percus
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    from donjon.temps import instant

    scenario, graine, dossier, archive = arguments
    dossier = Path(dossier)
    nom = f'{scenario}-{graine}'
    attendus = {(x['pnj'], x['instant']) for x in archive['approches_impossibles']}
    acteurs = {qui for qui, t in attendus}
    bornes = {t // 3000 * 5 for qui, t in attendus}
    debut = min(bornes, default=240)
    dernier_choix, filet, traces, avertissements, erreurs = {}, [False], [], [], []
    dites, sauvegardes = set(), []
    approcher, choisir, deliberer = pnj._approcher, d.choisir, d.deliberer
    relever, creer = banc._oisifs_urgents, banc.creer
    chroniquer = pnj._chroniquer
    capture, monde_joue = {}, []

    def recharger(m):
        with tempfile.TemporaryDirectory(dir=dossier) as tmp:
            chemin = Path(tmp) / 'partie.json'
            m.sauver(chemin)
            return Monde.charger(chemin)

    def etat(m, qui, g=None):
        e, o = lire(m, qui), m.objets[qui]
        return {'instant': instant(m), 'pnj': qui, 'etape': copy.deepcopy(g),
                'lieu': o['lieu'], 'case': copy.deepcopy(o.get('position')),
                'orientation': o.get('orientation'), 'dernier_choix': copy.deepcopy(dernier_choix.get(qui)),
                'croyances': {s: {a: copy.deepcopy(v['valeur']) for a, v in attrs.items()}
                              for s, attrs in e['croyances'].items()},
                'perception': copy.deepcopy(percus(m, qui)[0]),
                'contacts': {x: {'salle': d.salle_crue(m, qui, x),
                                 'case': pnj._case_crue(m, qui, x, d.salle_crue(m, qui, x))}
                             for x in pnj._a_toucher(m, qui, g)} if g else {},
                'renoncements': copy.deepcopy(e['renoncements']),
                'intention': copy.deepcopy(e['intention']), 'manque': copy.deepcopy(e['manque']),
                'eveil': e['eveil'], 'libre': e['libre']}

    def sauver(m, suffixe):
        chemin = dossier / f'{nom}-{suffixe}.json.gz'
        data = copy.deepcopy(m.data)
        chemin.write_bytes(gzip.compress(json.dumps(data, ensure_ascii=False).encode('utf8'), mtime=0))
        copie = Monde(copy.deepcopy(data))
        recharge = recharger(copie)
        preuves = {'monde': copie.data == recharge.data,
                   'rendu': regarder(copie) == regarder(recharge),
                   'scene': scene_percue(copie) == scene_percue(recharge)}
        sauvegardes.append({'chemin': str(chemin), 'instant': instant(m), **preuves})
        return data

    def approche(m, qui, g, *args, **kwargs):
        observer = qui in acteurs and m.data['minutes'] >= debut
        avant = etat(m, qui, g) if observer else None
        if (qui, instant(m)) in attendus:
            sauver(m, f'avant-{qui}-{instant(m)}')
        resultat = approcher(m, qui, g, *args, **kwargs)
        if observer:
            traces.append({'avant': avant, 'resultat': resultat, 'apres': etat(m, qui, g)})
        return resultat

    def choix(m, qui, minute):
        dernier_choix[qui] = {'instant': instant(m), 'filet_minute': filet[0],
                             'eveil': lire(m, qui)['eveil']}
        return choisir(m, qui, minute)

    def deliberation(*args, **kwargs):
        ancien, filet[0] = filet[0], True
        try:
            return deliberer(*args, **kwargs)
        finally:
            filet[0] = ancien

    def releve(m):
        if m.data['minutes'] in bornes:
            capture['data'] = sauver(m, f"borne-{m.data['minutes']}")
            capture['borne'] = m.data['minutes']
        return relever(m)

    def nouveau(*args, **kwargs):
        m = creer(*args, **kwargs)
        monde_joue.append(m)
        return m

    def chronique(m, qui, texte, nature='geste'):
        if nature == 'social' and ' dit à ' in texte and ' que ' in texte:
            cle = (qui, texte)
            if cle in dites:
                avertissements.append({'instant': instant(m), 'pnj': qui, 'texte': texte,
                                        'etat': etat(m, qui)})
                sauver(m, f'avertissement-{qui}-{instant(m)}')
            dites.add(cle)
        return chroniquer(m, qui, texte, nature)

    config = {'heures': 4, 'depart': 'tire', 'verifier': False, 'empreintes': False,
              'joueurs': c.JOUEURS, 'processus': 1}
    with ExitStack() as pile:
        for objet, attr, fonction in [(pnj, '_approcher', approche), (d, 'choisir', choix),
                                     (d, 'deliberer', deliberation), (banc, '_oisifs_urgents', releve),
                                     (banc, 'creer', nouveau), (pnj, '_chroniquer', chronique)]:
            pile.enter_context(patch.object(objet, attr, fonction))
        if hasattr(social, '_chroniquer'):
            pile.enter_context(patch.object(social, '_chroniquer', chronique))
        resultat = c.jouer_nuit((scenario, graine, config))
    comparaisons = {k: resultat['donnees'][k] == archive['donnees'][k]
                    for k in ('chronique', 'recit', 'mesures', 'souvenirs')}
    comparaisons['etat_final'] = resultat['etat_final'] == archive['etat_final']
    ecrire(dossier / f'{nom}-trace.json', {'comparaisons_archives': comparaisons,
           'approches': traces, 'avertissements': avertissements, 'sauvegardes': sauvegardes})
    reprise = None
    if 'data' in capture:
        # Une borne propre du moteur, avant la première interruption ; la reprise
        # joue effectivement la sauvegarde rechargée jusqu'à la fin de la nuit.
        m = recharger(Monde(capture['data']))
        traces.clear()
        dernier_choix.clear()
        with ExitStack() as pile:
            for objet, attr, fonction in [(pnj, '_approcher', approche), (d, 'choisir', choix),
                                         (d, 'deliberer', deliberation)]:
                pile.enter_context(patch.object(objet, attr, fonction))
            banc.executer(m, 240)
        recharge = recharger(m)
        borne = capture['borne']
        reprise = {'borne': borne, 'avant_premiere_interruption': any(borne * 600 < t < (borne + 5) * 600 for q, t in attendus),
                   'etat_final_identique': c.empreinte(m.data) == archive['etat_final'],
                   'monde_recharge': m.data == recharge.data,
                   'rendu_recharge': regarder(m) == regarder(recharge),
                   'scene_recharge': scene_percue(m) == scene_percue(recharge), 'approches': traces}
        ecrire(dossier / f'{nom}-reprise.json', reprise)
    return {'nuit': nom, 'archives': comparaisons, 'sauvegardes': sauvegardes,
            'reprise': {k: v for k, v in reprise.items() if k != 'approches'} if reprise else None,
            'interruptions': len(resultat['approches_impossibles']),
            'avertissements_redits': len(avertissements)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sortie', type=Path, required=True)
    args = parser.parse_args()
    dossier = args.sortie.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = {'ok': False, 'debut': time.time()}
    try:
        from priorite import ceder
        ceder()
        source = dossier.parent / 'comparaison.json'
        archive = json.loads(source.read_text(encoding='utf8'))
        avant = {(n['scenario'], n['graine']): n for n in archive['reference']['nuits']}
        nuits = [n for n in archive['branche']['nuits'] if n['approches_impossibles']
                 or n['boucles']['avertissements_redits'] > avant[(n['scenario'], n['graine'])]['boucles']['avertissements_redits']]
        print(f'Diagnostic 313 : {len(nuits)} nuits de branche, deux travailleurs réduits', flush=True)
        with ProcessPoolExecutor(max_workers=2, max_tasks_per_child=1) as pool:
            bilan['nuits'] = list(pool.map(travail, [(n['scenario'], n['graine'], str(dossier), n) for n in nuits]))
        bilan['ok'] = all(all(n['archives'].values()) and all(all(s[k] for k in ('monde', 'rendu', 'scene'))
                              for s in n['sauvegardes']) and (not n['reprise'] or all(
                              n['reprise'][k] for k in ('avant_premiere_interruption', 'etat_final_identique',
                                                     'monde_recharge', 'rendu_recharge', 'scene_recharge')))
                          for n in bilan['nuits'])
    except BaseException:
        bilan['erreur'] = traceback.format_exc()
        print(bilan['erreur'], file=sys.stderr, flush=True)
    finally:
        bilan['fin'] = time.time()
        ecrire(dossier / 'fin.json', bilan)
    return int(not bilan['ok'])


if __name__ == '__main__':
    raise SystemExit(main())
