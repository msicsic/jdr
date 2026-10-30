"""Porte des insertions et évictions d'épisodes, au format historique.

S1a conserve la liste sauvegardée, son plafond et les crochets réentrants.
Les lectures et les modifications du contenu des épisodes seront portées
séparément ; ce module ne renvoie pas le stock mutable aux consommateurs.
"""
import copy

MEMOIRE_MAX = 40


def retenir_episode(monde, id, evenement):
    """Copie, date et retient l'occurrence avant ses conséquences métier."""
    from .esprits import esprit, _date_indices_soupcon, GESTES_SOUPCON_MAX
    if evenement["type"] == "dit" and "valeur" in evenement:
        from .social import retenir_dit
        retenir_dit(monde, id, evenement["a"], {"type": "affirmation", **{
            k: evenement[k] for k in ("sujet", "attribut", "valeur")}})
    memoire = esprit(monde, id)["memoire"]
    souvenir = copy.deepcopy({"minute": monde.data["minutes"], **evenement})
    from .relations import identifier
    from .temps import instant
    if id != "joueur" and souvenir["type"] in ("vu_agir", "entendu_agir", "vu_porter", "vol_surpris"):
        # Même indice et même identité de preuve qu'avant la porte S1a.
        gestes = esprit(monde, id)["indices_soupcon"]["gestes"]
        gestes.append({"objet": souvenir["objet"], "instant": _date_indices_soupcon(monde)})
        del gestes[:-GESTES_SOUPCON_MAX]
    identifier(souvenir, instant(monde))
    memoire.append(souvenir)
    del memoire[:-MEMOIRE_MAX]
    from .relations import souvenir as eprouver_souvenir
    eprouver_souvenir(monde, id, souvenir)
    from .defense import retenir as retenir_violence
    retenir_violence(monde, id, souvenir)


def evincer_episodes(monde, id, retirer):
    """Filtre en place, dans l'ordre, sans crochet ni copie des survivants.

    Le prédicat porte la décision du consommateur ; il ne doit pas modifier
    le stock. L'identité de la liste et des épisodes conservés reste intacte.
    """
    from .esprits import esprit
    memoire = esprit(monde, id)["memoire"]
    memoire[:] = [s for s in memoire if not retirer(s)]
