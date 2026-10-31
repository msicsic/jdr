"""Captures et attribution des vérifications du lot 374, sans modifier le monde.

Lancer depuis le worktree à diagnostiquer ; les modules du jeu viennent du cwd.
Une tâche par nuit : --scenario auberge --graine 42 --sortie <dossier>.
"""
import argparse
import copy
import gzip
import importlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
RACINE = Path.cwd().resolve()
sys.path[:] = [str(RACINE), *[p for p in sys.path if Path(p or '.').resolve() not in (RACINE, SCRIPT.parent)]]
importlib.import_module('tests')
sys.path.append(str(RACINE / 'tools'))
from priorite import ceder


def ecrire(chemin, valeur):
    chemin.write_text(json.dumps(valeur, ensure_ascii=False, indent=2), encoding='utf8')


def capturer(scenario, graine, dossier, checkpoints_extra=()):
    from donjon import banc_pnj, deliberation, esprits, pnj, echanges, ouie
    from donjon.temps import instant
    from tools.audit_nuits import JOUEURS
    dossier.mkdir(parents=True, exist_ok=True)
    nom = f'{scenario}-{graine}'
    fin = dossier / (nom + '-fin.json')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RACINE, text=True).strip()
    if fin.exists() and json.loads(fin.read_text(encoding='utf8')).get('revision') == revision:
        return
    monde_actif = None
    positives, generations, consommees = {}, {}, {}
    evenements, appels, captures, en_cours = [], [], [], {}
    bruit_attribue = set()
    checkpoints = {
        ('mine', 1985): {'lucien': (61200, 64800)},
        ('crue', 1985): {'brune': (114000, 114100, 123000, 123100)},
        ('crue', 2024): {'brune': (137384, 137391)},
        ('crue', 42): {'aubin': (10800, 11400, 12000)},
    }.get((scenario, graine), {})
    for repere in checkpoints_extra:
        acteur, t = repere.split('=')
        checkpoints[acteur] = (*checkpoints.get(acteur, ()), int(t))
    deja = set()

    def photo(m, etiquette):
        fichier = f'{nom}-{etiquette}.json.gz'
        (dossier / fichier).write_bytes(gzip.compress(json.dumps(m.data, ensure_ascii=False).encode('utf8')))
        return fichier

    creer = banc_pnj.creer
    def creer_observe(*a, **kw):
        nonlocal monde_actif
        m = creer(*a, **kw)
        monde_actif = m
        for acteur, e in m.data['esprits'].items():
            for sujet, attributs in e['croyances'].items():
                c = attributs.get('lieu')
                if c and c['valeur'] is not None:
                    positives[acteur, sujet] = copy.deepcopy(c)
                    generations[acteur, sujet] = 0
        return m

    avancer = pnj._avancer
    def avancer_observe(m, *a, **kw):
        # Moteur exécute chaque attente sur une copie transactionnelle.
        nonlocal monde_actif
        monde_actif = m
        return avancer(m, *a, **kw)

    croire = esprits.croire
    def croire_observe(m, acteur, sujet, attribut, valeur, source, *a, **kw):
        r = croire(m, acteur, sujet, attribut, valeur, source, *a, **kw)
        if m is monde_actif and attribut == 'lieu' and valeur is not None:
            cle = acteur, sujet
            c = esprits.lire(m, acteur)['croyances'][sujet]['lieu']
            date = min(c['minute'], c.get('origine', {}).get('minute', c['minute']))
            directe = source in ('vu', 'entendu', 'essai', 'se_dit') and 'origine' not in kw
            verification_propre = cle in en_cours and valeur == (positives.get(cle) or {}).get('valeur')
            if cle not in bruit_attribue and not verification_propre and (
                    directe or date > consommees.get(cle, {}).get('minute', -10**9)):
                generations[cle] = generations.get(cle, 0) + 1
            if cle not in bruit_attribue:
                # Sur l'ancien moteur, l'attribution d'un bruit rajeunit la
                # croyance brute. Ce rajeunissement n'est pas une preuve reçue.
                positives[cle] = copy.deepcopy(c)
        return r

    attribuer = ouie._attribuer
    def attribuer_observe(m, acteur, crus, *a, **kw):
        cles = {(acteur, s) for s in crus}
        bruit_attribue.update(cles)
        try:
            return attribuer(m, acteur, crus, *a, **kw)
        finally:
            bruit_attribue.difference_update(cles)

    def ouvrir(m, acteur, sujet, moyen):
        if m is not monde_actif or not sujet:
            return None
        e = esprits.lire(m, acteur)
        preuve = next((g.get('contenu', {}).get('verification') for g in (e['intention'] or {}).get('plan', [])
                       if g.get('contenu', {}).get('cherche') == sujet), None)
        c = e['croyances'].get(sujet, {}).get('lieu') or {}
        positive = positives.get((acteur, sujet)) or {}
        age = m.data['minutes'] - min(positive.get('minute', m.data['minutes']),
                                    positive.get('origine', {}).get('minute', m.data['minutes']))
        regle = m.data['positions_hypotheses']
        perimee = (positive and esprits.personne_autre(m, acteur, sujet)
                   and positive['confiance'] * 2 ** (-age / regle['demi_vies'][positive.get('mobilite', 'mobile')])
                   <= regle['seuil'])
        if not preuve and not esprits.position_a_verifier(m, acteur, sujet) and not perimee:
            return None
        cle = acteur, sujet
        ancienne = consommees.get(cle)
        generation = generations.get(cle, 0)
        expiree = bool(perimee or esprits.position_a_verifier(m, acteur, sujet))
        event = {'instant': instant(m), 'minute': m.data['minutes'], 'acteur': acteur, 'sujet': sujet,
                 'salle': m.objets[acteur]['lieu'], 'moyen': moyen, 'generation': generation,
                 'croyance': copy.deepcopy(c), 'positive': copy.deepcopy(positives.get(cle)),
                 'verification_expiree': expiree,
                 'repetition_sans_preuve': bool(expiree and ancienne and generation <= ancienne['generation']),
                 'exclusions': copy.deepcopy(e['recherches'].get(sujet, {}))}
        event['capture'] = photo(m, f'verification-{len(evenements)}')
        evenements.append(event)
        # Une cible revue en chemin est une preuve neuve déjà fraîche quand
        # l'ancien préfixe se termine. Cette inspection ne consomme pas une
        # hypothèse expirée qui n'a pas encore existé pour cette nouvelle vue.
        if expiree:
            consommees[cle] = {'generation': generation, 'minute': m.data['minutes']}
        return len(evenements) - 1

    inspecter = pnj._inspecter
    def inspecter_observe(m, acteur, cherche=None, *a, **kw):
        cle = acteur, cherche
        index = ouvrir(m, acteur, cherche, 'inspection')
        en_cours[cle] = index
        try:
            resultat = inspecter(m, acteur, cherche, *a, **kw)
            if index is not None:
                evenements[index]['apres'] = photo(m, f'verification-{index}-apres')
            return resultat
        finally:
            en_cours.pop(cle, None)

    heler = pnj.heler
    def heler_observe(m, acteur, sujet, *a, **kw):
        from donjon.corps import conscient
        if m is not monde_actif or not conscient(m, acteur):
            return heler(m, acteur, sujet, *a, **kw)
        index = en_cours.get((acteur, sujet))
        if (acteur, sujet) not in en_cours:
            index = ouvrir(m, acteur, sujet, 'appel')
        appels.append({'instant': instant(m), 'acteur': acteur, 'sujet': sujet,
                       'salle': m.objets[acteur]['lieu'], 'verification': index,
                       'generation': generations.get((acteur, sujet), 0),
                       'croyance': copy.deepcopy(esprits.lire(m, acteur)['croyances'].get(sujet, {}).get('lieu')),
                       'intention': copy.deepcopy(esprits.lire(m, acteur)['intention']),
                       'capture': photo(m, f'appel-{len(appels)}')})
        return heler(m, acteur, sujet, *a, **kw)

    enqueter = echanges.enqueter
    def enqueter_observe(m, acteur, auditeur, *a, **kw):
        index = ouvrir(m, acteur, kw.get('sujet'), 'question')
        r = enqueter(m, acteur, auditeur, *a, **kw)
        if index is not None:
            evenements[index]['issue'] = r[0]
            evenements[index]['auditeur'] = auditeur
        return r

    choisir = deliberation.choisir
    def choisir_observe(m, acteur, minute):
        t = instant(m)
        cle = acteur, t
        capture = m is monde_actif and acteur in checkpoints and t in checkpoints[acteur] and cle not in deja
        if capture:
            deja.add(cle)
            entree = {'acteur': acteur, 'instant': t, 'avant': photo(m, f'{acteur}-{t}-avant')}
            captures.append(entree)
        r = choisir(m, acteur, minute)
        if capture:
            entree['apres'] = photo(m, f'{acteur}-{t}-apres')
        return r

    from contextlib import ExitStack
    with ExitStack() as pile:
        for module in list(sys.modules.values()):
            if module and getattr(module, '__name__', '').startswith('donjon'):
                for nom_cle, valeur in list(vars(module).items()):
                    if valeur is croire:
                        pile.enter_context(patch.object(module, nom_cle, croire_observe))
        for obj, attribut, fn in ((banc_pnj, 'creer', creer_observe), (pnj, '_inspecter', inspecter_observe),
                                  (pnj, '_avancer', avancer_observe),
                                  (ouie, '_attribuer', attribuer_observe),
                                  (pnj, 'heler', heler_observe), (echanges, 'enqueter', enqueter_observe),
                                  (deliberation, 'choisir', choisir_observe)):
            pile.enter_context(patch.object(obj, attribut, fn))
        _, _, donnees = banc_pnj.nuit(scenario, graine, 4, JOUEURS[scenario], depart='tire')
    resultat = {'revision': revision, 'scenario': scenario, 'graine': graine, 'verifications': evenements,
                'appels': appels, 'captures_decisions': captures, 'donnees': donnees}
    ecrire(dossier / (nom + '.json'), resultat)
    ecrire(fin, {'revision': revision, 'verifications': len(evenements), 'appels': len(appels),
                'repetitions': sum(e['repetition_sans_preuve'] for e in evenements), 'captures': len(captures)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', required=True)
    parser.add_argument('--graine', required=True, type=int)
    parser.add_argument('--sortie', required=True, type=Path)
    parser.add_argument('--checkpoint', action='append', default=[], metavar='ACTEUR=INSTANT')
    args = parser.parse_args()
    ceder()
    capturer(args.scenario, args.graine, args.sortie.resolve(), args.checkpoint)


if __name__ == '__main__':
    main()
