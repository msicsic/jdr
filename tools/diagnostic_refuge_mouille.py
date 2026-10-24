"""Vérifie le contrat commun plan/marche sur les captures du lot 39.

    python tools/diagnostic_refuge_mouille.py

Deux captures rechargées, puis vingt minutes en un bloc et minute par minute.
Le PNJ doit rejoindre le sec ; monde complet et rendu restent identiques après
rechargement, en un bloc ou minute par minute.
"""
import copy
import gzip
import json
from pathlib import Path
import sys
import tempfile

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from tools.priorite import ceder
from donjon import deliberation, eau, planification, pnj
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.obstacles import cout_route
from donjon.rendu import regarder


def recharger(monde, dossier):
    chemin = Path(dossier) / 'partie.json'
    monde.sauver(chemin)
    return Monde.charger(chemin)


def vivre(monde, minutes, dossier):
    monde.data['minutes'] += minutes
    pnj.avancer(monde, minutes, [])
    return recharger(monde, dossier)


def diagnostiquer(nom, qui, dossier):
    source = RACINE / 'tests/data/scenes' / f'refuge-mouille-{nom}.json.gz'
    monde = recharger(Monde(json.loads(gzip.decompress(source.read_bytes()))), dossier)
    debut = monde.data['minutes']
    vue = planification.Vue(monde, qui)
    depart = planification.depart(monde, qui, vue)
    route = vue.route(depart, 'chambre_cloche')
    assert route is not None
    plan = planification.planifier(monde, qui, 'chaleur')
    assert plan is not None and plan[0] == {'type': 'chaleur', 'objet': 'poele_guet'}
    avant = copy.deepcopy(monde.data)
    duree = pnj._marcher(monde, qui, lambda s, p: s == 'chambre_cloche', [])
    assert duree is not None, 'La recherche acceptait pourtant la route.'
    monde = recharger(monde, dossier)
    assert monde.objets[qui]['lieu'] == avant['objets'][qui]['lieu']  # premier pas local
    # Le sondage du départ ne consomme pas l'horloge ; le rejeu complet repart
    # donc de la capture, et laisse l'ordonnanceur accomplir tous les pas.
    monde = recharger(Monde(avant), dossier)
    risques = [{
        'salle': s, 'reelle_cm': eau.profondeur(monde, s),
        'crue_cm': eau.eau_crue(monde, qui, s),
        'attendue_cm': eau.attendue(monde, qui, s),
        'descente_interdite': vue.descente(depart.salle, s),
    } for s in [depart.salle, *(sortie['vers'] for sortie in route)]]
    bloc = vivre(recharger(monde, dossier), 20, dossier)
    coupe = recharger(monde, dossier)
    for _ in range(20):
        coupe = vivre(coupe, 1, dossier)
    assert bloc.data == coupe.data
    assert regarder(bloc) == regarder(coupe)
    assert bloc.objets[qui]['lieu'] == 'chambre_cloche'
    assert eau.profondeur(bloc, 'chambre_cloche') == 0
    return {
        'scene': nom, 'minute': debut, 'pnj': qui, 'plan': plan,
        'cout_route_minutes': cout_route(route, depart.orientation),
        'marche': duree, 'eau': risques,
        'renoncements': lire(monde, qui)['renoncements'],
        'refus': lire(monde, qui)['refus'],
        'apres_20_minutes': {
            'salle': bloc.objets[qui]['lieu'],
            'besoins': lire(bloc, qui)['besoins'],
            'attentes': deliberation.attentes(bloc, qui),
            'rendu_joueur': regarder(bloc),
            'monde_et_rendu_identiques_decoupes': True,
        },
    }


def main():
    ceder()
    sortie = RACINE / 'artifacts/codex-41'
    sortie.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=sortie) as dossier:
        resultat = [diagnostiquer('crue500-160', 'brune', dossier),
                    diagnostiquer('auteur-100', 'ilse', dossier)]
    chemin = sortie / 'reproduction.json'
    chemin.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Départ et arrivée au sec sur deux scènes ; monde et rendu identiques après recharge et découpage : {chemin}')


if __name__ == '__main__':
    main()
