"""Sondes du lot 371, sans changement des règles ni appel au modèle.

Les bruts sont écrits dans --sortie. « Occasion » signifie prestation ponctuelle
effectivement promise : cela ne prouve pas qu'une limite améliorerait son issue.
"""
import argparse
import copy
import gzip
import json
from pathlib import Path
import sys
import time
import traceback
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path[:] = [x for x in sys.path if Path(x or '.').resolve() != BASE / 'tools']
sys.path.insert(0, str(BASE))
from tools.priorite import ceder


def ecrire(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if path.suffix == '.gz':
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            f.write(texte)
    else:
        path.write_text(texte, encoding='utf-8')


def scene(nom):
    from tests.test_accords_publics import situation
    from tests.test_parts_achetees import antichambre_du_banc
    from tests.support import regarder
    from donjon.commandes import DescripteurPublic
    if nom == 'auberge':
        m, d = situation()
        # La lumière permet la rencontre mais s'épuise avant la fin du parcours.
        # La livraison n'est pas la recharge : celle-ci restera un geste distinct.
        m.objets['lanterne_etable']['combustible'] = 2
        return m, d
    m = antichambre_du_banc()
    regarder(m, 'joueur', 'planches')
    m.joueur['or'] = 50
    return m, DescripteurPublic({'geste': 'accord', 'cible': 'aubin',
        'parametres': {'prestation': {'type': 'part', 'objet': 'planches'},
                       'prix': 3, 'limite': 6000}})


def instantane(m, path):
    from donjon.monde import Monde
    from donjon.rendu import fiche, regarder, decrire_comptes
    from donjon.scene import scene_percue
    from donjon.emissions import pnj
    def vues(n):
        return {'fiche': fiche(n), 'regard': regarder(n), 'comptes': decrire_comptes(n),
                'scene': scene_percue(n), 'paroles': pnj(n)}
    avant = copy.deepcopy(m.data)
    v = vues(m)
    m.sauver(path)
    n = Monde.charger(path)
    vr = vues(n)
    resultat = {'etat_identique': n.data == avant, 'rendu_identique': v == vr,
                'vues': vr}
    ecrire(path.with_name(path.stem + '-rendu.json'), resultat)
    assert resultat['etat_identique'] and resultat['rendu_identique'], path
    return n, resultat


def preparer(sortie):
    from donjon.accords_publics import accords_publics
    scripts = []
    for nom in ('auberge', 'relais'):
        m, d = scene(nom)
        source = sortie / f'{nom}-source.json'
        m.sauver(source)
        phrase = ('Odile, je te paie trois pièces maintenant si tu me livres une part d’huile dans dix minutes'
                  if nom == 'auberge' else
                  'Aubin, je te paie trois pièces maintenant si tu me livres une part de tes planches dans dix minutes')
        catalogue = accords_publics(m)
        numero = str(next(i for i, p in enumerate(catalogue['prestations'], 1)
                          if p['terme'] == d.contenu['parametres']['prestation']))
        # Séparer la fidélité du préremplissage de la récupération par le joueur.
        cas = {'sans-correction': [phrase, 'valider', 'tenter'],
               'correction-explicite': [phrase, 'corriger prestation', numero,
                   'corriger prix', '3', 'corriger delai', '10', 'valider', 'tenter'],
               'annuler': [phrase, 'annuler'],
               'demain': [phrase.replace('dans dix minutes', 'demain'), 'annuler'],
               'paiement-futur': [phrase.replace('maintenant', 'demain')],
               'maintien': [phrase + ' et tu maintiens ma lanterne allumée jusqu’à mon retour']}
        for cas_nom, tours in cas.items():
            fichier = sortie / f'luna-{nom}-{cas_nom}.json'
            ecrire(fichier, {'scenario': nom, 'seed': 1985, 'sauvegarde': str(source.resolve()), 'tours': tours})
            scripts.append(fichier.resolve())
    commande = ("$env:SEUIL_AUTH='C:\\Users\\msics\\donjon\\.seuil-auth'\n"
        "& 'C:\\Users\\msics\\donjon\\.venv\\Scripts\\python.exe' "
        + "'" + str(BASE / 'tools/banc_parties.py') + "' "
        + ' '.join("'" + str(p) + "'" for p in scripts)
        + " --connexion chatgpt --max-appels 80 --etiquette evaluation-echeance-371 --fil --sortie '"
        + str(sortie / 'luna') + "'\n")
    (sortie / 'luna-a-jouer.ps1').write_text(commande, encoding='utf-8')


def jouer(sortie):
    from donjon import agendas
    from donjon.biens import bourse, solder
    from donjon.esprits import lire
    from donjon.pnj import avancer
    from donjon.temps import ecouler, instant
    from donjon.accords_publics import accords_publics
    from tests.test_accords_publics import parcours, AccordsPublicsTests
    from tests.test_gestes_terminal import ConsoleTests, sans_saisie
    from tests.test_audits_attendu import jouer as libre
    from tests.test_accord_libre_date import interpretation
    from tests.test_tensions import vivre
    bilans = []
    for nom in ('auberge', 'relais'):
        dossier = sortie / nom
        dossier.mkdir(parents=True, exist_ok=True)
        m, d = scene(nom)
        m, _ = instantane(m, dossier / 'depart.json')
        catalogue = accords_publics(m)
        ecrire(dossier / 'catalogue.json', catalogue)
        cmd = [*parcours(m, d), 'tenter']
        debut = time.perf_counter()
        n, lignes, menus = ConsoleTests().jouer_console(m.copier(), cmd)
        secondes = time.perf_counter() - debut
        (dossier / 'terminal.txt').write_text('\n'.join(lignes), encoding='utf-8')
        n, relecture = instantane(n, dossier / 'accord.json')
        cible = d.contenu['cible']
        engagements = copy.deepcopy(agendas.en_cours(n, cible))
        clic = AccordsPublicsTests().clic(m, d)
        ecrire(dossier / 'menu-web.json', clic)
        phrase = ('Odile, je te paie trois pièces maintenant si tu me livres une part d’huile dans dix minutes'
                  if nom == 'auberge' else
                  'Aubin, je te paie trois pièces maintenant si tu me livres une part de tes planches dans dix minutes')
        f, texte, appels = libre(m.copier(), phrase, [interpretation(m, d)], [], suite=('valider', 'tenter'))
        (dossier / 'libre-fournisseur-simule.txt').write_text(texte, encoding='utf-8')
        f, _ = instantane(f, dossier / 'libre-fournisseur-simule.json')
        bilan = {'scenario': nom, 'preparation': 'scène contrôlée issue des supports de tests, jet accord fixé à 20',
            'commandes': cmd, 'saisies_terminal': len(cmd), 'clics_web_confirmation_comprise': clic['clics'] + 1,
            'appels_direct': 0, 'secondes_terminal_harnais': secondes,
            'catalogue_prestations': len(catalogue['prestations']), 'engagements': engagements,
            'paiement': 50 - n.joueur['or'], 'recharge': relecture,
            'libre_simule': {'appels': len(appels), 'fonctions': [a[0] for a in appels],
                'saisies': 3, 'parite_direct': sans_saisie(f.data) == sans_saisie(n.data)}, 'issues': {}}
        # Livraison autonome : même état et mêmes mots en bloc et après recharge à chaque minute.
        a, la = vivre(n.copier(), 3)
        z, lz = n.copier(), []
        for _ in range(3):
            z, lignes = vivre(z, 1)
            lz.extend(lignes)
            z, _ = instantane(z, dossier / f'decoupe-{z.data["minutes"]}.json')
        a, _ = instantane(a, dossier / 'livraison-naturelle.json')
        bilan['issues']['naturelle'] = {'etat_bloc_decoupe': a.data == z.data,
            'mots_bloc_decoupe': la == lz, 'lignes': la, 'lignes_decoupees': lz,
            'issues': agendas.issues_temporelles(a), 'or': a.joueur['or'],
            'engagements': agendas.en_cours(a, cible)}
        if nom == 'auberge':
            from donjon.moteur import Moteur
            from donjon.operations import sequence, etape
            lampe_avant = copy.deepcopy(a.objets['lanterne_etable'])
            part = engagements[0]['condition']['objet']
            moteur = Moteur(a)
            rendu = moteur.executer(moteur.preparer(sequence(
                etape('alimenter', 'lanterne_etable', outil=part),
                etape('allumer', 'lanterne_etable', outil='briquet'))))
            a, _ = instantane(a, dossier / 'lanterne-rechargee.json')
            bilan['issues']['recharge_lanterne'] = {'avant': lampe_avant,
                'apres': a.objets['lanterne_etable'], 'part': a.objets[part], 'rendu': rendu}
        # Interruption contrôlée, aucun geste de livraison forcé avant expiration.
        r = n.copier()
        for e in r.data['esprits'].values():
            e['libre'], e['eveil'], e['veille'] = 100000, None, None
        def retarder(pas, suffixe):
            x, mots = r.copier(), []
            for dt in pas:
                ecouler(x, dt)
                avancer(x, 0, mots, dixiemes=dt)
                x, _ = instantane(x, dossier / f'retard-{suffixe}-{instant(x)}.json')
            return x, mots
        dt = 6002 - instant(r)
        ra, ma = retarder([dt], 'bloc')
        rz, mz = retarder([dt-3, 1, 1, 1], 'decoupe')
        comptes = []
        for _ in range(2):
            agendas.echoir(ra, cible)
            solder(ra, comptes)
        ra, _ = instantane(ra, dossier / 'retard-solde.json')
        part = engagements[0]['condition']['objet'] if engagements else None
        bilan['issues']['retard'] = {'etat_bloc_decoupe': sans_saisie(rz.data) == sans_saisie(retarder([dt], 'temoin')[0].data),
            'mots_bloc_decoupe': ma == mz, 'lignes': ma, 'comptes': comptes,
            'issues': agendas.issues_temporelles(ra), 'or': ra.joueur['or'],
            'bourse_prestataire': bourse(ra, cible), 'dettes': ra.data.get('dettes'),
            'lieu_part': ra.objets.get(part, {}).get('lieu')}
        from tests.test_realisation_datee import geste
        historique = copy.deepcopy(agendas.issues_temporelles(ra))
        gestes = [geste(ra, cible, 'prendre', part), geste(ra, cible, 'remettre', 'joueur', part)]
        ra, _ = instantane(ra, dossier / 'remise-volontaire-tardive.json')
        bilan['issues']['remise_volontaire_tardive'] = {'gestes': gestes,
            'historique_identique': agendas.issues_temporelles(ra) == historique,
            'or': ra.joueur['or'], 'lieu_part': ra.objets[part]['lieu']}
        bilans.append(bilan)
        ecrire(sortie / 'jeu.json', bilans)
    return bilans


def nuit(arguments):
    scenario, graine, sortie = arguments
    ceder()
    from donjon import banc_pnj, echanges, agendas
    from donjon.temps import instant
    from donjon.esprits import pnjs
    from donjon.monde import Monde
    evenements, references, capture = [], set(), {}
    creer, demander, proposer, engager = banc_pnj.creer, echanges.demander, echanges.proposer, echanges.engager
    def creer_capture(*a, **k):
        m = creer(*a, **k)
        capture['monde'] = m
        return m
    def trace(m, appel, args, resultat):
        # L'enregistrement suit la réponse d'une opération réelle, jamais les devis.
        candidats = []
        for q in pnjs(m):
            for e in agendas.en_cours(m, q):
                c = e['condition']
                # Premier périmètre : exclure prêt, maintien et mandat durable.
                if not any(k in c for k in ('remettre', 'allume', 'verrouillee', 'lieu', 'servir')) or c.get('proteger'):
                    continue
                cle = json.dumps([q, e], sort_keys=True)
                if cle in references:
                    continue
                references.add(cle)
                candidats.append({'titulaire': q, 'engagement': copy.deepcopy(e)})
        ev = {'instant': instant(m), 'appel': appel, 'arguments': args,
              'resultat': copy.deepcopy(resultat), 'nouvelles_prestations': candidats}
        evenements.append(ev)
        if candidats:
            ecrire(sortie / f'{scenario}-{graine}-occasion-{len(evenements)}.json.gz', m.data)
    def demander_sonde(m, *a, **k):
        r = demander(m, *a, **k)
        trace(m, 'demander', {'positionnels': a, 'nommes': k}, r)
        return r
    def proposer_sonde(m, *a, **k):
        r = proposer(m, *a, **k)
        trace(m, 'proposer', {'positionnels': a, 'nommes': k}, r)
        return r
    def engager_sonde(m, *a, **k):
        r = engager(m, *a, **k)
        trace(m, 'engager', {'positionnels': a, 'nommes': k}, r)
        return r
    debut = time.perf_counter()
    try:
        with patch.object(banc_pnj, 'creer', creer_capture), patch.object(echanges, 'demander', demander_sonde), patch.object(echanges, 'proposer', proposer_sonde), patch.object(echanges, 'engager', engager_sonde):
            texte, mesures, donnees = banc_pnj.nuit(scenario, graine, 4,
                {'auberge': 'dortoir', 'relais': 'chambre_cloche', 'mine': 'galerie'}[scenario])
        m = capture['monde']
        relecture = Monde(json.loads(json.dumps(m.data)))
        donnees.update(scenario=scenario, evenements=evenements, recharge_etat=relecture.data == m.data)
        ecrire(sortie / f'{scenario}-{graine}-etat.json.gz', m.data)
        ecrire(sortie / f'{scenario}-{graine}.json.gz', donnees)
        (sortie / f'{scenario}-{graine}.txt').write_text(texte, encoding='utf-8')
        resultat = {'scenario': scenario, 'graine': graine, 'ok': True,
            'secondes': time.perf_counter()-debut, 'appels_echanges': len(evenements),
            'prestations_ponctuelles': sum(len(e['nouvelles_prestations']) for e in evenements),
            'mesures': mesures}
    except Exception:
        resultat = {'scenario': scenario, 'graine': graine, 'ok': False,
                    'traceback': traceback.format_exc()}
    ecrire(sortie / f'{scenario}-{graine}-fin.json', resultat)
    return resultat


def banc(sortie, processus=2):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    taches = [(s, g, sortie) for s in ('auberge', 'relais', 'mine') for g in (1985, 7, 42, 2024)]
    resultats = []
    with ProcessPoolExecutor(max_workers=processus) as pool:
        for f in as_completed([pool.submit(nuit, t) for t in taches]):
            r = f.result()
            resultats.append(r)
            print(json.dumps(r, ensure_ascii=False), flush=True)
            ecrire(sortie / 'banc-progression.json', resultats)
    ecrire(sortie / 'fin-banc.json', {'ok': all(r['ok'] for r in resultats), 'nuits': resultats})


def analyser(sortie):
    from collections import Counter
    from donjon import agendas, echanges
    from donjon.monde import Monde
    from donjon.temps import instant
    bilan = {'methode': 'prestations observées après opérations réelles ; devis E3 sur copies seulement',
             'nuits': [], 'occasions': [], 'retours_echanges': Counter()}
    for scenario in ('auberge', 'relais', 'mine'):
        for graine in (1985, 7, 42, 2024):
            with gzip.open(sortie / f'{scenario}-{graine}.json.gz', 'rt', encoding='utf-8') as f:
                brut = json.load(f)
            compte = Counter()
            for numero, ev in enumerate(brut['evenements'], 1):
                r = ev['resultat']
                cause = r.get('cause') or 'accepte' if isinstance(r, dict) else r
                bilan['retours_echanges'][ev['appel'] + ':' + str(cause)] += 1
                for candidat in ev['nouvelles_prestations']:
                    with gzip.open(sortie / f'{scenario}-{graine}-occasion-{numero}.json.gz', 'rt', encoding='utf-8') as f:
                        m = Monde(json.load(f))
                    engagement = candidat['engagement']
                    q = candidat['titulaire']
                    c = engagement['condition']
                    avant = copy.deepcopy(m.data)
                    try:
                        devis = echanges.juger_delai(m, q, c, engagement['pour'], instant(m) + 6000)
                    except Exception as exc:
                        devis = {'verdict': 'non_admis', 'exception': str(exc)}
                    assert m.data == avant, 'La sonde de devis a modifié sa source'
                    payee = engagement.get('paye', {}).get('prix', 0) > 0
                    compte['prestations'] += 1
                    compte['payees' if payee else 'non_payees'] += 1
                    compte[devis['verdict']] += 1
                    e = m.data['esprits'].get(engagement['pour'], {})
                    bilan['occasions'].append({'scenario': scenario, 'graine': graine,
                        'instant': ev['instant'], 'appel': ev['appel'], 'numero_evenement': numero,
                        **candidat, 'payee': payee, 'devis_dix_minutes': devis,
                        'besoins_beneficiaire': e.get('besoins'),
                        'intention_beneficiaire': e.get('intention'),
                        'compte_technique': 'lecture analyste privée, non présentée au joueur ni au MJ'})
            bilan['nuits'].append({'scenario': scenario, 'graine': graine,
                **compte, 'appels_echanges': len(brut['evenements']),
                'mesures': {k: brut['mesures'].get(k) for k in ('propositions', 'acceptees', 'achats',
                    'pieces_payees', 'remboursements', 'dettes', 'usurpations', 'minutes_dans_le_noir')},
                'recharge_etat': brut['recharge_etat']})
    bilan['retours_echanges'] = dict(bilan['retours_echanges'])
    ecrire(sortie / 'analyse-banc.json', bilan)
    ecrire(sortie / 'fin-analyse.json', {'ok': True, 'nuits': len(bilan['nuits']),
        'occasions': len(bilan['occasions'])})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('preparer', 'jeu', 'banc', 'analyser'))
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--processus', type=int, choices=(1, 2), default=2)
    args = p.parse_args()
    args.sortie = args.sortie.resolve()
    args.sortie.mkdir(parents=True, exist_ok=True)
    ceder()
    if args.mode == 'banc':
        banc(args.sortie, args.processus)
    else:
        {'preparer': preparer, 'jeu': jouer, 'analyser': analyser}[args.mode](args.sortie)
