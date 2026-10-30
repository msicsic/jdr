"""Trace publique des mouvements accomplis, indépendante de leurs lignes de récit."""
import copy
from math import hypot


class Ligne(str):
    """Point d'insertion typé ; son contenu n'est jamais analysé."""


def place(monde):
    return monde.joueur['salle'], tuple(monde.joueur.get('position', ()))


def ouvrir(monde):
    monde._mouvements = []
    monde._reste_deplacements = 0


def noter(monde, avant, lignes=None, *, operation, debut=None, fin=None):
    """Appelé seulement après une mutation physique réussie du joueur."""
    apres = place(monde)
    if avant == apres or '_mouvements' not in monde.__dict__:
        return
    from .temps import instant
    salle, case = avant
    arrivee, position = apres
    plans = monde.data['salles']
    if (case and position and all('plan' in plans[s] for s in (salle, arrivee))
            and plans[salle].get('niveau', 0) == plans[arrivee].get('niveau', 0)):
        ox, oy = plans[salle]['plan']['origine']
        ax, ay = plans[arrivee]['plan']['origine']
        dx, dy = ax + position[0] - ox - case[0], ay + position[1] - oy - case[1]
        direction = '-'.join(d for n, d in ((dy, 'nord' if dy < 0 else 'sud'),
                                            (dx, 'ouest' if dx < 0 else 'est')) if n)
        unite, quantite = ('pas', 1) if operation == 'marcher' else ('mètre', round(hypot(dx, dy), 3))
    else:
        # Une traversée sans métrique ne s'invente ni distance ni pas.
        direction = next((d for d, s in plans[salle]['sorties'].items() if s.get('vers') == arrivee), '')
        unite, quantite = 'passage', 1
    maintenant = instant(monde)
    evenement = dict(acteur='joueur', operation=operation, unite=unite, quantite=quantite,
                     direction=direction, debut=maintenant if debut is None else debut,
                     fin=fin)
    monde._mouvements.append(evenement)
    if lignes is not None:
        lignes.append(Ligne(''))


def achever(monde, fin):
    for mouvement in monde.__dict__.get('_mouvements', ()):
        if mouvement['fin'] is None:
            mouvement['fin'] = fin


def cumuler(mouvements):
    groupes = []
    for m in mouvements:
        cle = ('acteur', 'operation', 'unite', 'direction')
        if groupes and all(groupes[-1][k] == m[k] for k in cle):
            groupes[-1]['quantite'] += m['quantite']
            groupes[-1]['fin'] = m['fin']
        else:
            groupes.append(copy.deepcopy(m))
    return groupes


def phrases(resultat):
    """La même formulation pour l'affichage et les preuves exactes du lot 95."""
    from .temps import dire_duree
    textes = []
    blocs = []
    for g in resultat.get('cumul', ()):
        if blocs and all(blocs[-1][-1][k] == g[k] for k in ('acteur', 'operation', 'unite')):
            blocs[-1].append(g)
        else:
            blocs.append([g])
    for bloc in blocs:
        g = bloc[0]
        total = sum(x['quantite'] for x in bloc)
        nombre = f"{total:g}".replace('.', ',')
        unite = g['unite'] + ('s' if total != 1 and g['unite'] != 'pas' else '')
        if len(bloc) == 1:
            direction = (' vers ' + g['direction']) if g['direction'] else ''
        else:
            direction = ' (' + ', puis '.join(f"{x['quantite']:g} vers {x['direction']}" for x in bloc) + ')'
        textes.append(f"Tu as avancé de {nombre} {unite}{direction} en {dire_duree(bloc[-1]['fin'] - g['debut'])}.")
    reste = resultat.get('reste', 0)
    if textes and reste:
        textes[-1] += f" Il reste {reste} étape{'s' if reste != 1 else ''} de déplacement non exécutée{'s' if reste != 1 else ''}."
    return textes


def clore(monde, lignes, plan):
    from .temps import instant
    achever(monde, instant(monde))
    mouvements = copy.deepcopy(monde.__dict__.get('_mouvements', []))
    total = mouvements
    parcours = plan.proposition.get('parcours')
    reste = monde.__dict__.get('_reste_deplacements', 0)
    if parcours:
        reste = len(parcours['pas']) - len(mouvements)
        precedent = (monde.data['journal'][-1].get('deplacements', {}) if monde.data['journal'] else {})
        ancien = precedent.get('parcours', {})
        if (ancien.get('id') == parcours['id'] and ancien.get('pas', [])[1:] == parcours['pas']
                and precedent.get('mouvements') and mouvements
                and precedent['mouvements'][-1]['fin'] == mouvements[0]['debut']):
            total = precedent['total'] + mouvements
    resultat = dict(mouvements=mouvements, total=total, cumul=cumuler(total), reste=reste)
    if parcours:
        resultat['parcours'] = copy.deepcopy(parcours)
    rendus = phrases(resultat)
    # Les sons et autres événements gardent leur ordre et leur multiplicité.
    sortie = []
    for ligne in lignes:
        if not isinstance(ligne, Ligne):
            sortie.append(ligne)
            continue
        sortie.extend(rendus)
        rendus = []
    # Les gestes différés (traîner) sont achevés par l'horloge, sans liste de lignes.
    sortie.extend(rendus)
    return sortie, resultat
