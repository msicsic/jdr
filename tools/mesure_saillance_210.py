"""Expérience opt-in de saillance, sans modification du moteur. Calcul séquentiel.

--campagne lance les trois nuits de 12 h et les vingt nuits de 4 h,
chacune témoin puis variante. Les choix entiers du témoin sont appariés
à la variante et à REFERENCE sur copies de la même entrée.
"""
import argparse
import copy
import gzip
import inspect
import json
from collections import Counter
from contextlib import contextmanager, ExitStack
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj as b, planification as p, deliberation as d
from donjon.memoire import episodes
from donjon.esprits import lire, RECENT
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from priorite import ceder
from mesure_reflexion_190 import richesse
from mesure_cout import Compteurs
from empreintes_nuits import _h
import audit_nuits as audit

AGISSABLES, ENTREES, CHERCHER = p.Vue.agissables, p._entrees, p.chercher
SIGNATURE = inspect.signature(CHERCHER)
MODE = 'complete'
JOUEURS = dict(relais='chambre_cloche', mine='galerie', auberge='dortoir',
               crue='chambre_cloche', crue_hameau='chambre_cloche')


def noms(valeur):
    """Identifiants structurés, jamais extraction du texte du récit."""
    if isinstance(valeur, str):
        return {valeur}
    if isinstance(valeur, dict):
        return set(valeur).union(*(noms(x) for x in valeur.values()))
    if isinstance(valeur, (list, tuple)):
        return set().union(*(noms(x) for x in valeur))
    return set()


def esprit_saillant(v, vises):
    """Récent, local, porté, ou souvenir associant moyen et but explicite.

    L'utilité reste celle des gestes communs (agissables/pertinent/besoin).
    Pas de rayon ajouté, pas de limite en nombre d'objets ou de nœuds.
    """
    cle = (frozenset(noms(vises)), v.motif)
    cache = getattr(v, '_saillance_210', None)
    if cache is not None and cle in cache:
        return cache[cle]
    e = lire(v.monde, v.id)
    maintenant = v.monde.data['minutes']
    cibles = noms(vises) | {v.motif}
    depart = p.depart(v.monde, v.id, v)
    local = {o for o in v.connus if v.salle(depart, o) == depart.salle}
    recent = {o for o, attributs in e['croyances'].items()
              if any(c.get('source') in ('vu', 'entendu', 'essai')
                     and 0 <= maintenant - c.get('minute', -1e9) <= RECENT
                     for c in attributs.values())}
    lies = set().union(*(noms(s) for s in episodes(v.monde, v.id) if noms(s) & cibles))
    # Une clé connue pour la cible est un lien explicite, pas une proximité.
    lies.update(o for o in v.connus if noms(v.objets[o].get('ouvre')) & cibles)
    resultat = frozenset((local | recent | lies | set(depart.portes) | cibles) & set(v.connus))
    # Vue est une photographie : ce cache privé ne survit pas à la recherche.
    if cache is None:
        v._saillance_210 = cache = {}
    cache[cle] = resultat
    return resultat


def agissables(v, vises):
    objets, porter = AGISSABLES(v, vises)
    if MODE != 'saillant':
        return objets, porter
    saillants = esprit_saillant(v, vises)
    # La pertinence peut s'élargir après découverte d'un préparatif lumière.
    utiles = {o for o in objets if v.pertinent(o, noms(vises)) or v.besoin[o]
              or o in noms(vises)}
    retenus = saillants & utiles
    return [o for o in objets if o in retenus], porter & retenus


def entrees(v, vises, profondeur, noeuds):
    base = ENTREES(v, vises, profondeur, noeuds)
    if MODE != 'saillant':
        return base
    return base, 'saillance-210-v1', tuple(sorted(esprit_saillant(v, vises)))


@contextmanager
def variante(mode):
    global MODE
    avant, MODE = MODE, mode
    try:
        yield
    finally:
        MODE = avant


def plan(r):
    return None if r is None else dict(cout=r[0], etapes=r[1])


def sauver(path, contenu):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump(contenu, f, ensure_ascii=False)


def nuit(scenario, graine, heures, mode, dossier, apparier=False):
    compte, pile, capture, releves, paires = Compteurs(), [], {}, [], []
    creer, choisir, oisifs, explorer = b.creer, d.choisir, b._oisifs_urgents, p._explorer_etats
    caches_ombres = {m: [{}, {}, {}] for m in ('saillant', 'reference')}
    recherches_ombre = []
    ombre = False
    echantillon = set()
    cpu_ombres = 0

    def creation(*a, **k):
        capture['monde'] = creer(*a, **k)
        return capture['monde']

    def recherche(*a, **k):
        x = SIGNATURE.bind(*a, **k)
        x.apply_defaults()
        x = dict(x.arguments)
        if MODE == 'reference':
            x.update(noeuds=p.REFERENCE, emplois=None)
        cle = (x['monde'].data['minutes'], x['id'], x['nom'])
        avant = len(p.DIAGNOSTIC)
        pile.append(cle)
        try:
            r = CHERCHER(**x)
        finally:
            pile.pop()
        diag = p.DIAGNOSTIC[avant:]
        if ombre:
            recherches_ombre.append(dict(but=x['nom'], plan=plan(r),
                                         borne=diag[-1]['issue'] == 'borne' or diag[-1]['noeuds'] >= x['noeuds']))
        else:
            z = diag[-1]
            compte.ajouter(*cle, recherches=1, neuves=int(not z['memoire']),
                          reprises=int(z['memoire']), graphes=int(z['graphe']),
                          noeuds_certificats=z.get('preuve_noeuds', 0))
        return r

    def exploration(*a, **k):
        r = explorer(*a, **k)
        if not ombre:
            compte.ajouter(*pile[-1], passes=1, noeuds=r[1])
        return r

    def choix(monde, ident, minute):
        nonlocal ombre, recherches_ombre, cpu_ombres
        cle_echantillon = (int(monde.data['minutes'] // 60), ident)
        selectionne = apparier and cle_echantillon not in echantillon
        if selectionne:
            echantillon.add(cle_echantillon)
            debut_ombre = time.process_time()
            resultats = {}
            entree = copy.deepcopy(monde.data)
            for m in ('saillant', 'reference'):
                copie = Monde(copy.deepcopy(entree))
                recherches_ombre = []
                ombre = True
                try:
                    with ExitStack() as stack:
                        for nom, cache in zip(('_MEMOIRE', '_GRAPHES', '_IMPOSSIBLES'), caches_ombres[m]):
                            stack.enter_context(patch.object(p, nom, cache))
                        stack.enter_context(patch.object(p, 'DIAGNOSTIC', []))
                        stack.enter_context(patch.object(d, 'COMPTES', Counter()))
                        stack.enter_context(variante(m))
                        choisir(copie, ident, minute)
                    resultats[m] = dict(intention=copy.deepcopy(lire(copie, ident)['intention']),
                                        recherches=recherches_ombre)
                finally:
                    ombre = False
            paires.append(dict(minute=minute, pnj=ident, **resultats))
            if resultats['saillant'] != resultats['reference']:
                sauver(dossier / 'choix' / f'{scenario}-{graine}-{heures:g}h-{len(paires)}.json.gz',
                       dict(etat=entree, pnj=ident, minute=minute, **resultats))
            assert monde.data == entree
            cpu_ombres += time.process_time() - debut_ombre
        compte.ajouter(monde.data['minutes'], ident, '__choix__', choix=1)
        return choisir(monde, ident, minute)

    def observation(monde):
        releves.append(audit._releve(monde))
        return oisifs(monde)

    detecteur = audit.detecteur_avis()
    with ExitStack() as stack:
        for obj, nom, f in [(b, 'creer', creation), (b, '_oisifs_urgents', observation),
                            (p, 'chercher', recherche), (p, '_explorer_etats', exploration),
                            (d, 'choisir', choix), (p.Vue, 'agissables', agissables),
                            (p, '_entrees', entrees)]:
            stack.enter_context(patch.object(obj, nom, f))
        stack.enter_context(variante(mode))
        sonde = stack.enter_context(detecteur.observer_avis())
        debut = time.process_time()
        _, mesures, donnees = b.nuit(scenario, graine, heures, JOUEURS[scenario], False, True, None, 'fixe')
        cpu = time.process_time() - debut
    monde = capture['monde']
    recharge = Monde(json.loads(json.dumps(monde.data)))
    rendu = (regarder(monde), scene_percue(monde))
    assert monde.data == recharge.data
    assert rendu == (regarder(recharge), scene_percue(recharge))
    n = dict(scenario=scenario, graine=graine, heures=heures, depart='fixe', variante=mode,
             cpu=cpu-cpu_ombres, cpu_ombres=cpu_ombres, compteurs=compte.resultat(heures), donnees=donnees, releves=releves,
             final=audit._final(monde), plantage=None, etat=monde.data, paires=paires,
             richesse=richesse(donnees['chronique'], audit._final(monde)['noms']),
             recharge=True, rendu=_h(rendu))
    audit.ajouter_avis(n, detecteur.analyser_episodes(sonde.episodes))
    n['audit'] = audit.analyser_nuit(n)
    path = dossier / f'{scenario}-{graine}-{heures:g}h-{mode}.json.gz'
    sauver(path, n)
    print(json.dumps(dict(fichier=path.name, cpu=cpu, compteurs=n['compteurs']['total'],
                          choix_apparies=len(paires)), ensure_ascii=False), flush=True)
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dossier', type=Path, required=True)
    ap.add_argument('--campagne', action='store_true')
    ap.add_argument('--scenario', choices=JOUEURS, default='mine')
    ap.add_argument('--graine', type=int, default=1985)
    ap.add_argument('--heures', type=float, default=0.1)
    ap.add_argument('--apparier', action='store_true')
    args = ap.parse_args()
    ceder()
    configs = ([(s, 1985, 12) for s in ('mine', 'auberge', 'crue_hameau')] +
               [(s, g, 4) for s in JOUEURS for g in (1985, 7, 42, 2024)] if args.campagne else
               [(args.scenario, args.graine, args.heures)])
    for s, g, h in configs:
        for mode in ('complete', 'saillant'):
            path = args.dossier / f'{s}-{g}-{h:g}h-{mode}.json.gz'
            if path.exists():
                continue
            nuit(s, g, h, mode, args.dossier, args.apparier and mode == 'complete')


if __name__ == '__main__':
    main()
