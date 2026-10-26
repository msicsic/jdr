"""Preuves des services spontanés : effet réel, utilité crue et témoin identifié."""
from . import agendas
from .esprits import lire, memoriser, percoit


def conditions_manquantes(monde, beneficiaire, objet):
    """Les mêmes buts crus non satisfaits pour un geste ou une remise."""
    from .deliberation import satisfaite
    profil = monde.objets.get(beneficiaire, {}).get('profil') or {}
    buts = [p['condition'] for p in profil.get('pulsions', [])]
    buts += [p['condition'] for p in agendas.en_cours(monde, beneficiaire, actifs=True)]
    return [c for c in buts if c.get('objet') == objet
            and not any(k in c for k in ('servir', 'rendre', 'remettre', 'periode'))
            and not satisfaite(monde, beneficiaire, c)]


def don_utile(monde, beneficiaire, objet):
    """Capturer le manque AVANT la remise ou le repas, sans changer le monde.

    Le corps est éprouvé directement. Pour un but, la remise doit réellement
    le satisfaire ; la seule mention de l'objet dans un projet ne suffit pas.
    """
    from .corps import CORPS
    from .deliberation import besoin_de_part, part_pour, parts, satisfaite
    from .esprits import croire, constater as voir
    if not monde.objets.get(beneficiaire, {}).get('profil'):
        return False
    besoin = besoin_de_part(monde.objets[objet])
    if (besoin in CORPS
            and parts(monde.objets[objet]) > 0
            and lire(monde, beneficiaire)['besoins'].get(besoin, 0) >= CORPS[besoin]['urgence']
            and part_pour(monde, beneficiaire, objet, besoin)):
        return True
    conditions = conditions_manquantes(monde, beneficiaire, objet)
    if not conditions:
        return False
    copie = monde.copier()
    copie.objets[objet]['lieu'] = beneficiaire
    croire(copie, beneficiaire, objet, 'lieu', beneficiaire, 'vu', salle=None, case=None)
    voir(copie, beneficiaire, objet, 'vu')
    return any(satisfaite(copie, beneficiaire, c) for c in conditions)


def preparer(monde, auteur, objet, operation):
    """Capturer avant le geste les manques de ceux qui peuvent le constater."""
    if not isinstance(objet, str):
        return []
    o = monde.objets.get(objet)
    if not o or o['type'] == 'personnage':
        return []
    from .deliberation import illicite
    if illicite(monde, auteur, objet, operation):
        return []
    # Une tâche convenue reçoit déjà son épreuve d'engagement, jamais deux.
    if agendas.en_cours(monde, auteur, objet=objet, actifs=True):
        return []
    temoins = []
    for autre, x in monde.objets.items():
        if autre == auteur or not x.get('profil'):
            continue
        conditions = conditions_manquantes(monde, autre, objet)
        if conditions and percoit(monde, autre, auteur) and percoit(monde, autre, objet):
            temoins.append((autre, conditions, {k: o.get(k) for k in
                            {'combustible', *(k for c in conditions for k in c if k != 'objet')}}))
    return temoins


def constater(monde, auteur, objet, avant):
    """La perception du geste et de son résultat établit son auteur, sans annonce à distance."""
    if not avant:
        return
    from .deliberation import satisfaite
    from .esprits import constater as voir
    o = monde.objets.get(objet, {})
    for autre, conditions, ancien in avant:
        if not percoit(monde, autre, auteur) or not percoit(monde, autre, objet):
            continue
        change = any(o.get(k) != v for k, v in ancien.items() if k != 'combustible') or (
            o.get('combustible', 0) > (ancien.get('combustible') or 0))
        if not change:
            continue
        voir(monde, autre, objet, 'vu')
        # Voir un état ne révèle pas sa serrure ; voir le geste qui vient de
        # le changer établit en revanche cet effet précis, comme pour l'auteur.
        from .esprits import croire
        for attribut, valeur in ancien.items():
            if attribut != 'combustible' and o.get(attribut) != valeur:
                croire(monde, autre, objet, attribut, o.get(attribut), 'vu')
        if any(satisfaite(monde, autre, c) for c in conditions):
            memoriser(monde, autre, {'type': 'service_rendu', 'de': auteur, 'objet': objet})


def lever_refus(monde, beneficiaire, auteur, preuve):
    """Le service du demandeur, effectivement constaté, constitue un moyen nouveau."""
    if auteur == 'joueur' or not monde.objets.get(auteur, {}).get('profil'):
        return
    e = lire(monde, auteur)
    e['refus'][:] = [s for s in e['refus'] if not (
        s['de'] == beneficiaire and s['raison'] in ('mefiance', 'rancune'))]
    memoriser(monde, auteur, {'type': 'service_constate', 'a': beneficiaire, 'preuve': preuve})
