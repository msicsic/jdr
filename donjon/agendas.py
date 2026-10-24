"""Accès unique aux engagements et aux agendas ; stockage historique inchangé en A1.

Au premier lot qui en a besoin, chaque engagement deviendra un agenda d'origine
« contrat » s'il est payé, « parole » sinon, en conservant condition, bénéficiaire et minute.
Les lectures renvoient des copies : toute mutation passe par une opération nommée.
"""
import copy

CHAMPS = {"engagements": list}


def en_cours(monde, id, *, condition=None, objet=None, personne=None, actifs=False):
    """Dans l'ordre enregistré, annulations à annoncer comprises sauf ``actifs``.
    ``personne`` vise le bénéficiaire ou une personne de la condition.
    """
    from .esprits import lire
    stock = monde.data.get("promesses_joueur", []) if id == "joueur" else lire(monde, id)["engagements"]
    return [copy.deepcopy(x) for x in stock
            if (condition is None or x["condition"] == condition)
            and (objet is None or x["condition"].get("objet") == objet)
            and (personne is None or x["pour"] == personne
                 or any(x["condition"].get(k) == personne for k in ("servir", "rendre", "remettre")))
            and (not actifs or not x.get("annule"))]


def prendre(monde, id, engagement):
    """Inscrire aussi la proposition provisoire, retirée si le devis ou le jet refuse."""
    from .esprits import esprit
    stock = monde.data.setdefault("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    stock.append(copy.deepcopy(engagement))


def retirer_proposition(monde, id, engagement):
    from .esprits import esprit
    stock = monde.data.get("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    stock.remove(engagement)


def tenir(monde, id, engagement):
    """Retirer une parole exécutée ; l'appelant inscrit son souvenir au même instant."""
    retirer_proposition(monde, id, engagement)


def annoncer_abandon(monde, id, engagement):
    """Retirer une annulation désormais annoncée à son destinataire."""
    retirer_proposition(monde, id, engagement)


def oublier_personne(monde, personne):
    """Une mort libère tous les engagements visant cette personne."""
    for e in monde.data["esprits"].values():
        e["engagements"] = [x for x in e["engagements"] if x.get("pour") != personne
                            and not any(x["condition"].get(k) == personne for k in ("servir", "rendre", "remettre"))]
    if "promesses_joueur" in monde.data:
        monde.data["promesses_joueur"] = [x for x in monde.data["promesses_joueur"] if x["pour"] != personne]


def depart(monde, id):
    """Données déclarées par le scénario, sans activation ni écriture dans ``data``."""
    return copy.deepcopy((monde.objets[id].get("profil") or {}).get("agendas", []))


def contrats(monde):
    """Accords de mission historiques, distincts des paroles de service des PNJ."""
    return copy.deepcopy(monde.data.get("engagements", {}))


def installer_contrats(monde):
    monde.data.setdefault("engagements", {})


def proposer_contrat(monde, mission, montant):
    monde.data["engagements"][mission] = {"statut": "propose", "montant": montant}


def repondre_contrat(monde, mission, accepter):
    monde.data["engagements"][mission]["statut"] = "accepte" if accepter else "refuse"


def payer_contrat(monde, mission):
    accord = monde.data["engagements"][mission]
    accord["statut"] = "paye"
    accord["paye_revision"] = monde.data["revision"] + 1


def declares(rapport):
    """Champ public rendu ou sauvegardé, jamais un esprit de PNJ du monde."""
    return copy.deepcopy(rapport.get("engagements"))


def verifier(monde, id):
    for engagement in en_cours(monde, id):
        from .deliberation import condition_valide
        # ``paye`` : une contrepartie payée d'avance (une part, un objet, une tâche), le bien et le prix
        # reçu (``echanges.engagements_echus``).
        from .biens import QUOI
        paye = engagement.get("paye")
        assert (isinstance(engagement, dict) and set(engagement) - {"paye", "lot", "objet", "annule", "marche"}
                - {"realisee"} == {"condition", "pour", "minute"}
                and ("realisee" not in engagement or engagement["realisee"] is True)
                and ("marche" not in engagement or engagement["marche"] is True)
                and ("objet" not in engagement or isinstance(engagement["objet"], str))
                and ("annule" not in engagement or engagement["annule"] in ("impossible", "refus"))
                and condition_valide(monde, engagement["condition"]) and "periode" not in engagement["condition"]
                and (engagement["pour"] == "joueur" or engagement["pour"] in monde.objets)
                and type(engagement["minute"]) is int
                and ("lot" not in engagement or isinstance(engagement["lot"], str) and engagement["lot"] in monde.objets
                     and "remettre" in engagement["condition"])
                and (paye is None or isinstance(paye, dict) and set(paye) == {"objet", "prix", "quoi"}
                     and paye["quoi"] in QUOI
                     and isinstance(paye["objet"], str) and type(paye["prix"]) is int and paye["prix"] > 0)
                ), "Engagement de PNJ invalide"


def echoir(monde, id):
    """Retire les engagements tenus, trop anciens ou qu'il ne peut plus tenir ; les souvenirs gardent
    la trace. Une part payée d'avance et non servie à l'échéance est rendue, ou due
    (``biens.rembourser``). Une garde finie, ce qu'il en porte encore (le bien, ses clés) lui reste
    prêté : il le rendra."""
    from .echanges import ENGAGEMENT_MAX, tenu, empeche, retenir_abandon, phrase_condition
    from .esprits import esprit, memoriser
    from .biens import _cles, preter, rembourser
    from .spatial import porte_par
    from .vol import proprietaire
    e = esprit(monde, id)
    restants, finis = [], []
    for engagement in e["engagements"]:
        if engagement.get("annule"):
            restants.append(engagement)  # Il doit encore prévenir, sans savoir magiquement l'autre informé.
        elif (not engagement.get("marche") or engagement.get("realisee")) and tenu(monde, id, engagement["condition"], engagement["minute"]):
            memoriser(monde, id, {"type": "engagement_tenu", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
            finis.append(engagement)
            if engagement.get("marche"):
                _raconter_marche(monde, id, engagement, True)
            if (engagement.get("paye") or {}).get("quoi") == "tache":
                from .pnj import _chroniquer
                from .social import _qui
                _chroniquer(monde, id, f"{_qui(monde, id)} a fait le travail que {_qui(monde, engagement['pour'])} "
                                       f"lui avait payé pour que {phrase_condition(monde, engagement['condition'])}.", "compte")
        elif monde.data["minutes"] - engagement["minute"] > ENGAGEMENT_MAX or empeche(monde, id, engagement) or renonce(monde, id, engagement):
            raison = "impossible" if empeche(monde, id, engagement) else "refus"
            memoriser(monde, id, {"type": "engagement_abandonne", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
            finis.append(engagement)
            if engagement.get("marche"):
                _raconter_marche(monde, id, engagement, False)
            if engagement.get("paye"):
                paye = engagement["paye"]
                rembourser(monde, id, engagement["pour"], paye["prix"], paye["objet"], paye["quoi"])
                retenir_abandon(monde, id, engagement, raison)  # Le prix rendu ne rend pas le service possible.
            else:
                engagement["annule"] = raison
                restants.append(engagement)
        else:
            restants.append(engagement)
    e["engagements"] = restants
    for engagement in finis:
        o, de = engagement["condition"].get("objet"), engagement["pour"]
        if ("rendre" in engagement["condition"] or "remettre" in engagement["condition"] or o not in monde.objets
                or proprietaire(monde, monde.objets[o]) != de):
            continue
        for k in sorted(_cles(monde, o, de)):
            if porte_par(monde, k, id) and not any(p["objet"] == k for p in monde.data.get("permissions", ())):
                preter(monde, k, id)


def renonce(monde, id, engagement):
    """Une parole de marché peut être trahie au prix commun de léser son bénéficiaire."""
    if not engagement.get("marche"):
        return False
    from .caractere import prix_faute
    from .esprits import lire
    from .planification import devis_pulsion
    besoins = lire(monde, id)["besoins"]
    motif = max(besoins, key=besoins.get, default=None)
    faute = prix_faute(monde, id, motif)
    if faute is None:
        return False
    devis = devis_pulsion(monde, id, engagement["condition"], engagement["pour"])
    return devis is not None and faute < devis[0]


def _raconter_marche(monde, id, engagement, tenu):
    from .pnj import _chroniquer
    from .social import _qui
    from .echanges import phrase_condition
    _chroniquer(monde, id, f"{_qui(monde, id)} {'tient' if tenu else 'abandonne'} la contrepartie promise à "
                f"{_qui(monde, engagement['pour'])} : {phrase_condition(monde, engagement['condition'])}.",
                "contrepartie_tenue" if tenu else "trahison")


def observer_promesses(monde, lignes):
    """Le bénéficiaire juge une promesse du joueur sur ses observations, jamais à distance."""
    from .echanges import ENGAGEMENT_MAX, tenu, phrase_condition
    from .esprits import memoriser
    from .pnj import se_parler
    from .voix import nom_pour_joueur
    for engagement in en_cours(monde, "joueur"):
        a, c = engagement["pour"], engagement["condition"]
        faite = engagement.get("realisee", False) and tenu(monde, a, c, engagement["minute"])
        echue = monde.data["minutes"] - engagement["minute"] > ENGAGEMENT_MAX
        if not faite and not (echue and se_parler(monde, a, "joueur")):
            continue
        tenir(monde, "joueur", engagement)
        memoriser(monde, a, {"type": "engagement_tenu" if faite else "engagement_abandonne",
                            "de": "joueur", "condition": c})
        texte = ("Tu as tenu ta promesse envers " if faite else "Tu as abandonné ta promesse envers ")
        texte += nom_pour_joueur(monde, a) + " : " + phrase_condition(monde, c) + "."
        monde.data.setdefault("journal_promesses", []).append(texte)
        lignes.append(texte)


def etat_promis(monde, id="joueur"):
    """Les seuls attributs qu'un effet doit changer pour réaliser les paroles du joueur."""
    etats = {}
    for engagement in en_cours(monde, id):
        if id != "joueur" and not engagement.get("marche"):
            continue
        c = engagement["condition"]
        o = monde.objets.get(c["objet"], {})
        cles = set(c) - {"objet"}
        if "allume" in c:
            cles.add("combustible")  # Entretenir une flamme déjà allumée produit aussi un résultat.
        etats.setdefault(c["objet"], {}).update({k: o.get(k) for k in cles})
    return etats


def constater_geste_joueur(monde, avant, id="joueur"):
    """Une modification effective réalise la condition ; déplacer une flamme n'est pas l'allumer.

    La preuve du moteur persiste ; le bénéficiaire l'apprend seulement par sa perception.
    """
    from .esprits import esprit
    stock = monde.data.get("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    for engagement in stock:
        if id != "joueur" and not engagement.get("marche"):
            continue
        c = engagement["condition"]
        o = monde.objets.get(c["objet"], {})
        cles = set(c) - {"objet"}
        if "allume" in c:
            cles.add("combustible")
        ancien = avant.get(c["objet"], {})
        change = (o.get("allume") != ancien.get("allume") or
                  o.get("combustible", 0) > (ancien.get("combustible") or 0)) if "allume" in c else any(
                      o.get(k) != ancien.get(k) for k in cles)
        if (change
                and all(o.get(k) == v for k, v in c.items() if k != "objet")):
            engagement["realisee"] = True


def promesses_visibles(monde):
    from .echanges import phrase_condition
    from .voix import nom_pour_joueur
    return ["Tu as promis à " + nom_pour_joueur(monde, x["pour"]) + " que "
            + phrase_condition(monde, x["condition"]) + "." for x in en_cours(monde, "joueur")]

