"""Banc 266 : référence commune en cache et branche observée une seule fois, deux processus.

Les minutes comptées sont des minutes de sécurité urgente effectivement en baisse
pendant une compagnie de secours. Ce n'est pas une estimation causale du gain
par rapport à une nuit différente. L'observation ne modifie aucune donnée du jeu.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / 'tools'))
sys.path.insert(0, str(RACINE))
import comparer_bancs as comparateur
import references
from priorite import ceder


def jouer(tache):
    from donjon import corps, deliberation as d, vecu
    from donjon.esprits import lire, pnjs
    from donjon.pnj import de_pres
    from donjon.temps import MINUTE
    ceder()
    compte = {'secours_peur_commences': 0, 'minutes_securite_urgente_apaisees_avec_secours': 0.0}
    episodes, notes = [], {}
    choisir, solder, noter, minute = d.choisir, vecu.solder, vecu.noter, vecu.minute

    def cible(m, id):
        i = lire(m, id)['intention']
        contrat = d.agendas.contrat_intention(m, id) or {}
        raison = (contrat.get('demande') or {}).get('raison') or {}
        return raison.get('qui') if i and i['motif'] == 'empathie' and raison.get('besoin') == 'peur' else None

    def choix(m, id, t):
        avant = cible(m, id)
        resultat = choisir(m, id, t)
        apres = cible(m, id)
        if apres and apres != avant:
            compte['secours_peur_commences'] += 1
            episodes.append({'auteur': id, 'pour': apres, 'minute': t})
        return resultat

    def photographier(m, id, t):
        if id == 'joueur':
            return
        v = corps.corps(m, id).get('vecu')
        if not v or v['depuis'] != t:
            return
        detresses = d.detresses_percues(m, id)
        aides = [x for x in pnjs(m) if x != id and cible(m, x) == id
                 and x not in detresses and de_pres(m, id, x)]
        notes[id] = aides

    def integrer(m, id, t, lignes=None):
        v = corps.corps(m, id).get('vecu')
        if id != 'joueur' and v and t > v['depuis'] and notes.get(id):
            pente = v['securite']
            besoin = lire(m, id)['besoins'].get('securite', 0)
            seuil = d.seuils(m, id).get('securite', 100)
            if pente is not None and pente < 0 and besoin > seuil:
                duree = min((t - v['depuis']) / MINUTE, (besoin - seuil) / -pente)
                compte['minutes_securite_urgente_apaisees_avec_secours'] += duree
        return solder(m, id, t, lignes)

    def noter_sonde(m, id, t, activite):
        resultat = noter(m, id, t, activite)
        photographier(m, id, t)
        return resultat

    def minute_sonde(m, id, t, lignes=None):
        resultat = minute(m, id, t, lignes)
        photographier(m, id, t)
        return resultat

    with patch.object(d, 'choisir', choix), patch.object(vecu, 'solder', integrer), \
         patch.object(vecu, 'noter', noter_sonde), patch.object(vecu, 'minute', minute_sonde):
        resultat = comparateur.jouer_nuit(tache)
    resultat['secours_peur'] = {**compte, 'episodes': episodes}
    return resultat


def bilan(nuit):
    avis = nuit.get('avis') or {}
    return {'scenario': nuit['scenario'], 'graine': nuit['graine'], 'plantage': nuit['plantage'],
            'suspects_219': avis.get('total_non_justifies', 0),
            'cycles_219': avis.get('total_cycles_accomplis', 0),
            'a_expliquer_219': avis.get('total_a_expliquer', 0),
            'boucles': nuit.get('boucles'), 'secours_peur': nuit.get('secours_peur'),
            'cache': nuit.get('cache')}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--reference', required=True)
    ap.add_argument('--arbre-reference', type=Path, required=True)
    ap.add_argument('--sortie', type=Path, required=True)
    args = ap.parse_args()
    ceder()
    args.sortie.mkdir(parents=True, exist_ok=True)
    debut, code = time.perf_counter(), 1
    config = {'scenarios': ['relais', 'mine', 'auberge', 'crue', 'crue_hameau'],
              'graines': [1985, 7, 42, 2024], 'heures': 4, 'depart': 'tire',
              'processus': 2, 'verifier': False, 'empreintes': False,
              'joueurs': dict(comparateur.JOUEURS)}
    try:
        commit = references.resoudre(RACINE, args.reference)
        if not commit or comparateur.git(args.arbre_reference, 'rev-parse', 'HEAD') != commit:
            raise ValueError('Arbre de référence différent du commit demandé')
        with tempfile.TemporaryDirectory(prefix='rester-266-') as temporaire:
            avant = comparateur.nuits_du_cote(lambda: args.arbre_reference, commit, config,
                                              temporaire, 'reference', references.dossier(RACINE))
        (args.sortie / 'reference.json').write_text(json.dumps(avant, ensure_ascii=False), encoding='utf-8')
        print('Référence terminée, lancement branche : 20 nuits, deux processus réduits.', flush=True)
        taches = [(s, g, config) for s, g in comparateur.taches_du_lot(config)]
        with ProcessPoolExecutor(max_workers=2, max_tasks_per_child=1) as pool:
            apres = []
            for nuit in pool.map(jouer, taches):
                apres.append(nuit)
                nom = f"{nuit['scenario']}-{nuit['graine']}.json"
                (args.sortie / nom).write_text(json.dumps(nuit, ensure_ascii=False), encoding='utf-8')
                print(json.dumps(bilan(nuit), ensure_ascii=False), flush=True)
        rapport = {'config': config, 'reference': commit,
                   'branche': comparateur.git(RACINE, 'rev-parse', 'HEAD'),
                   'nuits': [{'reference': bilan(a), 'branche': bilan(b)} for a, b in zip(avant, apres)]}
        (args.sortie / 'bilan.json').write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding='utf-8')
        code = int(any(n['plantage'] for n in avant + apres))
    except Exception:
        (args.sortie / 'erreur.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        # Dernier fichier écrit : le superviseur peut reprendre le lot.
        (args.sortie / 'fin.json').write_text(json.dumps({'code': code, 'secondes': time.perf_counter() - debut}),
                                           encoding='utf-8')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
