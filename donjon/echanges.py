"""Échanges typés entre personnages : affirmer, demander un objet, l'acheter, confier une
tâche, remettre.

Les mêmes règles valent pour le joueur et pour les PNJ. Une affirmation démentie par ce que
l'auditeur a vu récemment est rejetée et le locuteur perd sa confiance ; sinon un jet de CHA
du locuteur, contre un DD que la confiance de l'auditeur abaisse ou relève, décide s'il la
croit. Un objet n'est remis que par celui qui le porte, s'il fait confiance au demandeur et
n'en a pas besoin ; son altruisme rend le partage plus facile, sa volonté (``jet_persuasion``)
le rend plus dur à convaincre, et ce que vaut pour lui le prix qu'on ne lui paie pas aussi
(``biens.reticence``). Ce qu'il accorde dépend de qui il croit entendre (``voix``) : à une voix
qu'il ne sait à qui prêter, la confiance d'un étranger ; prudent, il lui demande d'abord « Qui va
là ? » (issue « qui_va_la »), même pour un achat ou pour lui rendre son bien. Payé son prix
(``biens.prix``), il vend sans se faire prier, s'il ne le garde pas et ne se méfie pas de
l'acheteur. Remis par son propriétaire, un objet qui dure est prêté (``biens.preter`` :
l'emprunteur en use sans faute et le rendra), ce qui se consomme est donné ; son propriétaire
qui le redemande le récupère, sauf s'il sert encore. Une tâche confiée devient un engagement
que le planificateur du moteur exécute quand rien de plus urgent ne presse ; sur un bien de celui
qui la confie, elle en confie la garde (``biens.gardes``). Tout est déterministe hors des jets du
moteur.
"""
from .caractere import penchant
from .esprits import RECENT, constater, croire, esprit, lire, memoriser, percevoir
from .paroles import _phrase, _stats_pnj, dementi, jet_persuasion

ENGAGEMENT_MAX = 240   # minutes avant qu'un engagement non tenu soit abandonné
PARTAGE = 12           # DD d'une demande (une part, un objet prêté), que l'altruisme de celui qui donne abaisse
TACHE = 12             # DD d'une tâche confiée


def clarte(monde, auditeur):
    """Un auditeur d'INT faible retient moins sûrement ce qu'on lui dit."""
    return 0.5 if _stats_pnj(monde, auditeur)["INT"] <= 8 else 1.0


def affirmer(monde, locuteur, auditeur, sujet, attribut, valeur):
    """« dementi », « doute », « crue » ou « decouvert » (crue puis démentie sous ses yeux)."""
    e = esprit(monde, auditeur)
    actuelle = e["croyances"].get(sujet, {}).get(attribut)
    if (actuelle and actuelle["valeur"] == valeur and actuelle["source"] in ("vu", "essai")
            and monde.data["minutes"] - actuelle["minute"] <= RECENT):
        return "crue"  # Il vient de le voir lui-même : la parole le confirme sans rien lui apprendre.
    from .voix import identifie, se_mefier, source_dite
    if dementi(monde, auditeur, sujet, attribut, valeur):
        # Il se méfie de qui lui ment : de lui s'il sait qui c'est, sinon de cette voix.
        if identifie(monde, auditeur, locuteur):
            memoriser(monde, auditeur, {"type": "mensonge_dementi", "locuteur": locuteur,
                                        "sujet": sujet, "attribut": attribut})
        se_mefier(monde, auditeur, locuteur, "vu")
        return "dementi"
    if not jet_persuasion(monde, auditeur, locuteur, 10)[0]:
        memoriser(monde, auditeur, {"type": "parole_doutee", "locuteur": locuteur,
                                    "sujet": sujet, "attribut": attribut})
        return "doute"
    lieu = {"salle": valeur if valeur in monde.data["salles"] else None, "case": None} if attribut == "lieu" else {}
    croire(monde, auditeur, sujet, attribut, valeur, source_dite(monde, auditeur, locuteur),
           round(0.7 * clarte(monde, auditeur), 2), **lieu)
    memoriser(monde, auditeur, {"type": "parole_crue", "locuteur": locuteur, "sujet": sujet, "attribut": attribut})
    # Ce qu'il a sous les yeux peut le démentir aussitôt.
    percevoir(monde, auditeur)
    if any(s["type"] == "mensonge_decouvert" and s.get("sujet") == sujet for s in e["memoire"][-3:]):
        return "decouvert"
    return "crue"


def necessaire(monde, auditeur, objet):
    """Un objet qui sert son plan en cours ou une de ses pulsions (l'objet, sa clé) n'est pas
    prêté, ni la source qui l'éclaire quand il a besoin d'y voir (``deliberation.lumiere_utile``).
    Le plan qui le rend à son propriétaire ne compte pas : ce n'est pas s'en servir."""
    intention = lire(monde, auditeur)["intention"]
    if (intention and "rendre" not in intention["but"]
            and any(objet in (e["cible"], e["outil"]) for e in intention["plan"])):
        return True
    if "allume" in monde.objets[objet] and monde.objets[auditeur].get("profil"):
        from .deliberation import lumiere_utile
        if lumiere_utile(monde, auditeur):
            return True
    profil = monde.objets[auditeur].get("profil")
    for pulsion in (profil or {}).get("pulsions", []):
        cible = pulsion["condition"].get("objet")
        if cible and (objet == cible or cible in monde.objets[objet].get("ouvre", [])):
            return True
    return False


def demande_de_part(monde, demandeur, auditeur, objet):
    """On peut demander une part d'une ressource comptée qui appartient à l'autre, même rangée
    ailleurs, si elle répond à un de ses besoins : des vivres pour la faim, du bois pour le froid ou
    pour un feu qu'on entretient (le donneur entretient lui-même ce feu, ``demander``)."""
    from .deliberation import besoin_de_part
    from .social import _proprietaire
    from .spatial import porte_par
    from .corps import valeurs
    o = monde.objets.get(objet)
    besoins = valeurs(monde, demandeur) if demandeur == "joueur" else lire(monde, demandeur)["besoins"]
    return bool(o and besoin_de_part(o) in besoins and not porte_par(monde, objet, auditeur)
                and _proprietaire(monde, {"objet": objet}) == auditeur)


def foyer_de(monde, auditeur, demandeur, foyer=None):
    """Le feu qu'une part de combustible entretient : celui que vise le demandeur, sinon un foyer
    que l'auditeur connaît dans la salle d'où il l'entend demander (le joueur compris : qu'il le voie
    ou n'entende qu'une voix, il sait d'où elle vient), sinon le premier qu'il connaît."""
    from .deliberation import _connus, salle_crue
    from .ouie import _place
    if foyer in monde.objets and monde.objets[foyer].get("foyer"):
        return foyer
    foyers = [f for f in _connus(monde, auditeur) if monde.objets[f].get("foyer")]
    salle = _place(monde, demandeur)[0]
    return next((f for f in foyers if salle_crue(monde, auditeur, f) == salle), foyers[0] if foyers else None)


def garde(monde, id, o):
    """Ce qu'il garde d'une ressource comptée qui est à lui : sa réserve (``reserve``), et ce dont
    il a lui-même besoin."""
    from .deliberation import besoin_de_part, parts, reserve, urgents
    from .vol import proprietaire
    return (besoin_de_part(o) is not None and proprietaire(monde, o) == id
            and (parts(o) <= reserve(monde, id) or besoin_de_part(o) in urgents(monde, id)))


def accueil(monde, demandeur, auditeur):
    """Ce qui arrête une demande avant qu'il la pèse : « mefiance » envers qui il croit entendre
    (``voix.fiabilite``), « qui_va_la » si c'est une voix inconnue et qu'il est prudent ; None."""
    from .voix import fiabilite, qui_va_la
    confiance = fiabilite(monde, auditeur, demandeur)
    if confiance and not confiance["valeur"]:
        return "mefiance"
    return "qui_va_la" if qui_va_la(monde, auditeur, demandeur) else None


def demander(monde, demandeur, auditeur, objet, foyer=None, prix=0):
    """« absent », « mefiance », « qui_va_la », « necessaire », « impossible », « pauvre »,
    « refus », « remis », « rendu », « promis » ou « vendu ».

    ``prix`` : les pièces offertes. Au moins le prix (``biens.prix``) au propriétaire, c'est un
    achat : accepté sans se faire prier, payé aussitôt. Moins, c'est une demande, que le prix non
    payé rend plus dure à qui une pièce compte (``biens.reticence``). Une voix qu'il ne sait à qui
    prêter s'entend d'abord demander qui va là, qu'elle offre de payer ou réclame son bien."""
    from .biens import prix as prix_de, reticence, richesse
    from .deliberation import _plan_pulsion, besoin_de_part
    from .spatial import porte_par
    from .vol import proprietaire
    part = demande_de_part(monde, demandeur, auditeur, objet)
    if objet not in monde.objets or not (part or porte_par(monde, objet, auditeur)
                                         or differee(monde, auditeur, objet, prix)):
        return "absent"
    arret = accueil(monde, demandeur, auditeur)
    if arret == "qui_va_la":
        return arret
    o = monde.objets[objet]
    if not part and proprietaire(monde, o) == demandeur:
        # Son propriétaire le redemande : il le lui rend, sauf s'il s'en sert encore. Garder un prêt
        # échu qu'on lui réclame lui coûte la confiance du prêteur (``biens.pret_garde``).
        if necessaire(monde, auditeur, objet):
            from .biens import echu, pret_garde
            if demandeur != "joueur" and echu(monde, objet):
                pret_garde(monde, demandeur, auditeur, objet, [])
            return "necessaire"
        remettre(monde, auditeur, demandeur, objet)
        return "rendu"
    if arret:
        return arret
    if prix and richesse(monde, demandeur) < prix:
        return "pauvre"
    prix_ = prix_de(monde, objet, part)
    vente = bool(prix_) and prix >= prix_ and proprietaire(monde, o) == auditeur
    # Ce qu'il perd à donner sans être payé : ce qui se consomme. Un objet qui dure, il le prête, et
    # le récupérera.
    perdu = part or besoin_de_part(o) is not None
    dd = PARTAGE - penchant(monde, auditeur, "altruisme") + (reticence(monde, auditeur, prix_, prix) if perdu else 0)
    if part:
        if garde(monde, auditeur, o):
            return "necessaire"
        if besoin_de_part(o) == "faim":
            condition = {"objet": objet, "servir": demandeur}
        elif vente and foyer is None:
            # Achetée sans qu'aucun feu soit nommé, une part de combustible est un bien qu'on achète :
            # il en détache une et la remet à l'acheteur. Seule une part demandée pour un feu va au feu.
            return _vendre_part(monde, auditeur, demandeur, objet, prix)
        else:
            # Une part de bois se donne au feu : il l'entretient lui-même pour celui qui a froid.
            foyer = foyer_de(monde, auditeur, demandeur, foyer)
            if foyer is None:
                return "impossible"
            condition = {"objet": foyer, "allume": True}
        engagements = esprit(monde, auditeur)["engagements"]
        paye = False
        if not any(x["condition"] == condition for x in engagements):
            if _plan_pulsion(monde, auditeur, condition) is None:
                return "impossible"
            if not vente and not jet_persuasion(monde, auditeur, demandeur, dd)[0]:
                return "refus"
            # Payée d'avance, la part est due : non servie à l'échéance, le prix est rendu ou dû
            # (``engagements_echus``).
            engagements.append({"condition": condition, "pour": demandeur, "minute": monde.data["minutes"],
                                **({"paye": {"objet": objet, "prix": prix, "quoi": "part"}} if vente else {})})
            memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": condition})
            if vente:
                _vendre(monde, auditeur, demandeur, objet, prix)
                paye = True
        if demandeur != "joueur":
            memoriser(monde, demandeur, {"type": "promis", "de": auditeur, "objet": objet,
                                         **({"foyer": condition["objet"]} if "allume" in condition else {})})
        return "vendu" if paye else "promis"
    if not porte_par(monde, objet, auditeur):
        # Un objet à lui qu'il ne porte pas, acheté à son prix : il s'engage à l'aller chercher et à le
        # remettre ; payé d'avance, non remis à l'échéance, le prix est dû (``engagements_echus``).
        if necessaire(monde, auditeur, objet) or garde(monde, auditeur, o):
            return "necessaire"
        condition = {"objet": objet, "remettre": demandeur}
        engagements = esprit(monde, auditeur)["engagements"]
        if any(x["condition"] == condition for x in engagements):
            return "promis"
        engagement = {"condition": condition, "pour": demandeur, "minute": monde.data["minutes"],
                      "paye": {"objet": objet, "prix": prix, "quoi": "objet"}}
        engagements.append(engagement)
        if _plan_pulsion(monde, auditeur, condition) is None:
            engagements.remove(engagement)
            return "impossible"
        memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": condition})
        _vendre(monde, auditeur, demandeur, objet, prix)
        return "vendu"
    # Prêter ce qui se consomme, c'est en donner les parts : il n'en prête pas ce qu'il garde.
    if necessaire(monde, auditeur, objet) or garde(monde, auditeur, o):
        return "necessaire"
    if not vente and not jet_persuasion(monde, auditeur, demandeur, dd)[0]:
        return "refus"
    if vente:
        from .biens import donner
        _vendre(monde, auditeur, demandeur, objet, prix)
        donner(monde, objet, demandeur)
    remettre(monde, auditeur, demandeur, objet)
    return "vendu" if vente else "remis"


def detacher_part(monde, lot):
    """Une part d'une réserve comptée devient un objet, à sa place : une pièce du lot s'il la décrit
    (``matiere.prelever_piece``), sinon une réserve d'une charge, du même nom ; la réserve diminue
    d'autant. Renvoie son identifiant."""
    import copy
    from .matiere import id_piece, prelever_piece
    o = monde.objets[lot]
    piece = id_piece(monde, lot)
    if o.get("physique"):
        prelever_piece(monde, lot, piece)
        return piece
    part = copy.deepcopy(o)
    part.update(id=piece, charges=1, masse=round(o["masse"] / max(1, o["charges"]), 3))
    o["charges"] -= 1
    o["masse"] = round(o["masse"] - part["masse"], 3)
    monde.objets[piece] = part
    return piece


def _vendre_part(monde, vendeur, acheteur, lot, prix):
    """« vendu » ou « impossible » : l'acheteur paie une part de la réserve ``lot`` ; le vendeur la
    détache et la lui remet, aussitôt s'il la porte, sinon il s'engage à l'aller chercher (comme un
    objet vendu d'avance, ``differee``) : non remise à l'échéance, le prix est dû."""
    from .biens import donner
    from .deliberation import _plan_pulsion
    from .spatial import porte_par
    import copy
    avant = copy.deepcopy(monde.objets[lot])
    piece = detacher_part(monde, lot)
    o = monde.objets[piece]
    # Il sait où il la met de côté.
    salle = o["lieu"] if o["lieu"] in monde.data["salles"] else None
    croire(monde, vendeur, piece, "lieu", o["lieu"], "vu", salle=salle,
           case=list(o["position"]) if salle and o.get("position") else None)
    if porte_par(monde, piece, vendeur):
        _vendre(monde, vendeur, acheteur, piece, prix)
        donner(monde, piece, acheteur)
        remettre(monde, vendeur, acheteur, piece)
        return "vendu"
    condition = {"objet": piece, "remettre": acheteur}
    engagement = {"condition": condition, "pour": acheteur, "minute": monde.data["minutes"],
                  "paye": {"objet": piece, "prix": prix, "quoi": "objet"}}
    engagements = esprit(monde, vendeur)["engagements"]
    engagements.append(engagement)
    if _plan_pulsion(monde, vendeur, condition) is None:
        engagements.remove(engagement)
        del monde.objets[piece]
        del esprit(monde, vendeur)["croyances"][piece]
        monde.objets[lot] = avant
        return "impossible"
    memoriser(monde, vendeur, {"type": "engagement_pris", "pour": acheteur, "condition": condition})
    _vendre(monde, vendeur, acheteur, piece, prix)
    return "vendu"


def differee(monde, auditeur, objet, prix):
    """Un objet à lui, qu'il ne porte pas, qu'on lui offre d'acheter à son prix (``biens.prix``) : il
    peut le vendre et aller le chercher pour le remettre. Ce qui se consomme se vend par parts."""
    from .biens import prix as prix_de
    from .deliberation import besoin_de_part
    from .vol import proprietaire
    o = monde.objets.get(objet)
    return bool(o and o.get("mobile") and besoin_de_part(o) is None and proprietaire(monde, o) == auditeur
                and prix_de(monde, objet) and prix >= prix_de(monde, objet))


# Les tâches qu'on peut payer quelqu'un de faire : ce que vise une pulsion qu'on rétablit soi-même
# d'ordinaire, et que le planificateur sait faire faire (``planification._engager``).
TACHES = ("allume", "verrouillee", "lieu")


def tache(condition):
    """La sorte de tâche qu'est cette condition, si on peut la payer (``TACHES``) ; None sinon."""
    return None if "periode" in condition else next((k for k in TACHES if k in condition), None)


def engager(monde, payeur, autre, condition, prix):
    """« mefiance », « qui_va_la », « deja », « pauvre », « impossible », « necessaire », « cher » ou
    « accepte ».

    ``payeur`` offre ``prix`` pièces pour qu'``autre`` fasse en sorte que ``condition`` soit vraie
    (un feu entretenu, un bien sous clé, un objet remis en place). Il accepte si ces pièces valent pour
    lui (``caractere.valeur_pieces``) au moins ce que la tâche lui coûte (son plan, comme s'il l'avait
    prise : ``planification.devis_pulsion``), sans jet, s'il n'y emploie pas ce qu'il garde (``garde``) : c'est un marché. Acceptée, elle devient son
    engagement, payé d'avance ; sur un bien du payeur, elle lui en confie la garde (``biens.gardes``).
    Non faite à l'échéance, le prix est dû (``engagements_echus``, ``biens.rembourser``)."""
    from .biens import payer, richesse
    from .caractere import valeur_pieces
    from .deliberation import illicite
    from .planification import devis_pulsion
    if payeur != "joueur" and condition["objet"] in monde.objets and illicite(monde, payeur, condition["objet"]):
        return "impossible"   # On ne fait pas faire à un autre ce qui serait, pour soi, une faute.
    arret = accueil(monde, payeur, autre)
    if arret:
        return arret
    # Celui qui le paie sait la tâche à faire : seul ce qu'il voit à l'instant la lui dit faite.
    if tenu(monde, autre, condition, monde.data["minutes"]):
        return "deja"
    if prix <= 0 or richesse(monde, payeur) < prix:
        return "pauvre"
    engagements = esprit(monde, autre)["engagements"]
    if any(x["condition"] == condition for x in engagements):
        return "deja"
    engagement = {"condition": dict(condition), "pour": payeur, "minute": monde.data["minutes"],
                  "paye": {"objet": condition.get("objet") or condition["lieu"], "prix": prix, "quoi": "tache"}}
    engagements.append(engagement)
    devis = devis_pulsion(monde, autre, condition, payeur)
    if devis is None:
        engagements.remove(engagement)
        return "impossible"  # Il ne voit pas comment s'y prendre avec ce qu'il sait.
    cout, etapes = devis
    # Ce qu'il garde (sa dernière part, ce dont il a besoin), il ne le donne pas, payé ou non.
    if any(monde.objets.get(x) and garde(monde, autre, monde.objets[x])
           for e in etapes if e["operation"] in ("alimenter", "manger", "servir") for x in (e["cible"], e["outil"])):
        engagements.remove(engagement)
        return "necessaire"
    if valeur_pieces(monde, autre, prix) < cout:
        engagements.remove(engagement)
        return "cher"
    payer(monde, payeur, autre, prix)
    memoriser(monde, autre, {"type": "engagement_pris", "pour": payeur, "condition": dict(condition), "prix": prix})
    if payeur != "joueur":
        memoriser(monde, payeur, {"type": "tache_payee", "a": autre, "condition": dict(condition), "prix": prix})
    return "accepte"


def siens_a_portee(monde, id):
    """Il sait ce qu'il porte et ce qui est à lui à portée de main (dans sa salle, hors de tout contenant
    fermé), même sans l'avoir regardé : il le constate (lieu et état). Renvoie ces objets."""
    from .spatial import porte_par
    from .vol import proprietaire
    salle = monde.objets[id]["lieu"]
    siens = []
    for k, o in monde.objets.items():
        if o["type"] == "personnage" or proprietaire(monde, o) != id:
            continue
        lieu, vus = o["lieu"], set()
        while lieu in monde.objets and lieu not in vus and monde.objets[lieu]["type"] == "contenant"                 and monde.objets[lieu].get("ouverte", True) is not False:
            vus.add(lieu)
            lieu = monde.objets[lieu]["lieu"]
        if not (porte_par(monde, k, id) or lieu == salle):
            continue
        ici = o["lieu"] in monde.data["salles"]
        croire(monde, id, k, "lieu", o["lieu"], "vu", salle=o["lieu"] if ici else None,
               case=list(o["position"]) if ici and o.get("position") else None)
        constater(monde, id, k, "vu")
        siens.append(k)
    return siens


def enqueter(monde, demandeur, auditeur, besoin):
    """(« mefiance », « qui_va_la », « rien » ou « dit », ce qui a été dit) : ``demandeur`` demande à
    ``auditeur`` s'il a de quoi apaiser ``besoin`` (« As-tu des vivres ? », « du bois ? ») sans rien
    connaître de ce qu'il a. Il répond par ce qu'il a vraiment : ses ressources comptées pour ce
    besoin (``deliberation.besoin_de_part``) qu'il croit avoir encore, et où il les croit ; ce qu'il
    porte et ce qui est à lui à portée de main, il le sait (``siens_a_portee``). Le
    demandeur l'apprend, par ouï-dire, et rien de plus : [(objet, lieu cru)]."""
    from .deliberation import _connus, _disponible_cru, _lieu_cru, besoin_de_part, parts
    from .spatial import porte_par
    from .vol import proprietaire
    from .deliberation import oublier_refus, retenir_refus
    arret = accueil(monde, demandeur, auditeur)
    if not arret:
        siens_a_portee(monde, auditeur)
    if arret:
        if demandeur != "joueur" and arret != "qui_va_la":
            # Refusé, il ne lui redemande pas de sitôt (``planification.s_enquerir``) ; à « Qui va
            # là ? », il se nomme et redemande.
            memoriser(monde, demandeur, {"type": "enquete", "de": auditeur, "besoin": besoin, "objets": []})
            retenir_refus(monde, demandeur, auditeur, "enqueter", arret, besoin=besoin, souvenir=False)
        return arret, []
    dit = [(k, auditeur if porte_par(monde, k, auditeur) else _lieu_cru(monde, auditeur, k))
           for k in _connus(monde, auditeur) if k in monde.objets and besoin_de_part(monde.objets[k]) == besoin
           and proprietaire(monde, monde.objets[k]) == auditeur and parts(monde.objets[k]) > 0
           and _disponible_cru(monde, auditeur, k)]
    dit = [(k, lieu) for k, lieu in dit if lieu is not None]
    if demandeur != "joueur":
        from .voix import source_dite
        source = source_dite(monde, demandeur, auditeur)
        for k, lieu in dit:
            salle = lieu if lieu in monde.data["salles"] else None
            croire(monde, demandeur, k, "lieu", lieu, source, round(0.7 * clarte(monde, demandeur), 2),
                   salle=salle, case=None)
        memoriser(monde, demandeur, {"type": "enquete", "de": auditeur, "besoin": besoin,
                                     "objets": [k for k, _ in dit]})
        # « Je n'en ai pas » se retient tant que rien de ce qu'il croit de ces ressources n'a changé ;
        # ce qu'il a dit avoir, il le sait désormais.
        if dit:
            oublier_refus(monde, demandeur, auditeur, "enqueter", besoin=besoin)
        else:
            retenir_refus(monde, demandeur, auditeur, "enqueter", "rien", besoin=besoin, souvenir=False)
    return ("dit" if dit else "rien"), dit


def demander_feu(monde, demandeur, auditeur, flamme, source):
    """« absent », « mefiance », « qui_va_la », « eteinte », « impossible » ou « allume ». Le
    demandeur tend sa source ; l'auditeur l'allume à la flamme qu'il porte. Cela ne lui ôte rien,
    ni prêt ni part : il le fait sans se faire prier, sauf s'il se méfie de lui ou ne sait qui
    lui parle (``accueil``)."""
    from .eau import sous_l_eau
    from .perception import flamme as donne_feu
    from .spatial import porte_par
    if flamme not in monde.objets or not porte_par(monde, flamme, auditeur):
        return "absent"
    arret = accueil(monde, demandeur, auditeur)
    if arret:
        return arret
    if not donne_feu(monde.objets[flamme]):
        return "eteinte"
    s = monde.objets.get(source)
    if (s is None or not porte_par(monde, source, demandeur) or s.get("allume") is not False
            or s.get("integrite", 1) == 0 or s.get("combustible", 0) <= 0 or sous_l_eau(monde, s)):
        return "impossible"
    s["allume"] = True
    return "allume"


def _vendre(monde, vendeur, acheteur, objet, prix):
    """L'acheteur paie ; chacun se souvient de la vente."""
    from .biens import payer
    payer(monde, acheteur, vendeur, prix)
    memoriser(monde, vendeur, {"type": "vente", "objet": objet, "a": acheteur, "prix": prix})
    if acheteur != "joueur":
        memoriser(monde, acheteur, {"type": "achat", "objet": objet, "de": vendeur, "prix": prix})


def tenu(monde, id, condition, depuis=None):
    """Ce qu'une parole demande est-il fait, à ses yeux ? Une parole donnée à la minute ``depuis``
    n'est tenue que sur ce qu'il a constaté depuis : un feu vu vif avant qu'on lui demande d'y
    mettre du bois n'est pas un feu entretenu. Une part à servir ne l'est qu'au geste qui la sert
    (``servir`` solde l'engagement), quoi qu'il croie de la faim de l'autre."""
    from .deliberation import satisfaite
    if "rendre" in condition:
        return satisfaite(monde, id, condition)  # Le prêt est clos : il le sait de sa main.
    if "servir" in condition or "remettre" in condition or not satisfaite(monde, id, condition):
        return False
    # Les croyances sont datées à la minute : dans la minute même de la parole, rien ne dit qu'il a vu
    # après l'avoir donnée (il choisit désormais entre deux minutes, ``deliberation.choisir``).
    nouvelles = lire(monde, id)["croyances"].get(condition.get("objet"), {}).values()
    return depuis is None or any(c["minute"] > depuis for c in nouvelles)


def confier(monde, demandeur, auditeur, condition):
    """« mefiance », « qui_va_la », « deja », « impossible », « refus » ou « accepte »."""
    from .deliberation import _plan_pulsion
    arret = accueil(monde, demandeur, auditeur)
    if arret:
        return arret
    if tenu(monde, auditeur, condition):
        return "deja"
    # Une tâche sur un bien de celui qui la confie en confie la garde (``biens.gardes``) : il juge
    # s'il peut s'y prendre avec ce que la garde lui permet.
    engagements = esprit(monde, auditeur)["engagements"]
    engagement = {"condition": dict(condition), "pour": demandeur, "minute": monde.data["minutes"]}
    engagements.append(engagement)
    if _plan_pulsion(monde, auditeur, condition) is None:
        engagements.remove(engagement)
        return "impossible"  # Il ne voit pas comment s'y prendre avec ce qu'il sait.
    if not jet_persuasion(monde, auditeur, demandeur, TACHE)[0]:
        engagements.remove(engagement)
        return "refus"
    memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": dict(condition)})
    return "accepte"


def remettre(monde, donneur, receveur, objet):
    """Remis par son propriétaire, un objet qui dure est prêté, ce qui se consomme est donné ;
    remis à son propriétaire, il lui est rendu (``deplacer`` clôt le prêt) ; remis par un autre,
    il change seulement de mains."""
    from .biens import donner, preter
    from .deliberation import besoin_de_part
    from .deplacement_objet import deplacer
    from .vol import proprietaire
    o = monde.objets[objet]
    e = esprit(monde, donneur) if (monde.objets.get(donneur) or {}).get("profil") else None
    livre = [x for x in (e["engagements"] if e else []) if x["condition"] == {"objet": objet, "remettre": receveur}]
    if livre and proprietaire(monde, o) == donneur:
        # Ce qu'il a vendu et vient remettre : l'objet passe à l'acheteur, la parole est tenue.
        donner(monde, objet, receveur)
        for x in livre:
            e["engagements"].remove(x)
            memoriser(monde, donneur, {"type": "engagement_tenu", "pour": receveur, "condition": x["condition"]})
    elif proprietaire(monde, o) == donneur:
        if besoin_de_part(o):
            donner(monde, objet, receveur)
            memoriser(monde, donneur, {"type": "don", "objet": objet, "a": receveur})
        else:
            # Un bien sans propriétaire déclaré est à qui le porte : prêté, il reste au prêteur.
            o["proprietaire"] = donneur
            preter(monde, objet, receveur)
            memoriser(monde, donneur, {"type": "pret", "objet": objet, "a": receveur})
    deplacer(monde, objet, receveur)
    if receveur != "joueur":
        memoriser(monde, receveur, {"type": "recu", "objet": objet, "de": donneur})


def servir(monde, id, nourriture, pour, lignes):
    """Donner une part à quelqu'un de la même salle, qu'on appelle s'il est hors de vue : il la
    mange, et sait gré de l'avoir reçue. Il faut pouvoir se parler (``pnj.peuvent_se_parler`` :
    s'entendre et savoir qui parle), comme pour tout échange."""
    from .deliberation import SATIETE
    from .esprits import percoit
    from .francais import complement_de
    from .pnj import _chroniquer, peuvent_se_parler
    from .social import _qui, faire_entendre
    o, autre = monde.objets[nourriture], monde.objets.get(pour)
    if pour == "joueur":
        return _servir_joueur(monde, id, nourriture, lignes)
    if (o.get("portions", 0) <= 0 or not autre or autre["type"] != "personnage"
            or autre["lieu"] != monde.objets[id]["lieu"] or not peuvent_se_parler(monde, id, pour)):
        return False
    appel = "" if percoit(monde, id, pour) and percoit(monde, pour, id) else f"appelle {_qui(monde, pour)} et lui "
    o["portions"] -= 1
    besoins = esprit(monde, pour)["besoins"]
    if "faim" in besoins:
        besoins["faim"] = max(0.0, besoins["faim"] - SATIETE)
    memoriser(monde, pour, {"type": "nourri", "de": id, "objet": nourriture})
    from .voix import identifie
    if identifie(monde, pour, id):
        croire(monde, pour, id, "fiable", True, "vu")  # Il sait gré à qui il sait l'avoir servi.
    constater(monde, id, pour, "vu")  # Il le voit manger : il sait sa faim apaisée, même dans le noir.
    e = esprit(monde, id)
    tenus = [x for x in e["engagements"] if x["condition"] == {"objet": nourriture, "servir": pour}]
    for x in tenus:
        e["engagements"].remove(x)
        memoriser(monde, id, {"type": "engagement_tenu", "pour": pour, "condition": x["condition"]})
    texte = (f"{_qui(monde, id)} {appel}donne une part {complement_de(o)}"
             + ("." if appel else f" à {_qui(monde, pour)}."))
    _chroniquer(monde, id, texte, "social")
    faire_entendre(monde, id, pour, texte, [nourriture], lignes)
    return True


def _servir_joueur(monde, id, nourriture, lignes):
    """La part promise au joueur : servie quand il est là, dans la salle des vivres, et qu'ils
    peuvent se parler (``pnj.peuvent_se_parler``) ; sinon on l'attend."""
    from .corps import SATIETE, valeurs
    from .francais import complement_de
    from .pnj import _chroniquer, peuvent_se_parler
    from .social import _qui
    o = monde.objets[nourriture]
    if (o.get("portions", 0) <= 0 or monde.joueur["salle"] != monde.objets[id]["lieu"]
            or not peuvent_se_parler(monde, id, "joueur")):
        return False
    o["portions"] -= 1
    v = valeurs(monde, "joueur")
    v["faim"] = max(0.0, v["faim"] - SATIETE)
    constater(monde, id, "joueur", "vu")
    e = esprit(monde, id)
    for x in [x for x in e["engagements"] if x["condition"] == {"objet": nourriture, "servir": "joueur"}]:
        e["engagements"].remove(x)
        memoriser(monde, id, {"type": "engagement_tenu", "pour": "joueur", "condition": x["condition"]})
    _chroniquer(monde, id, f"{_qui(monde, id)} donne une part {complement_de(o)} au joueur.", "social")
    from .voix import personne_pour_joueur
    lignes.append(f"{personne_pour_joueur(monde, id, court=True)[0]} te sert une part {complement_de(o)} ; tu manges.")
    return True


RESSOURCES = {"faim": "de quoi manger", "chaleur": "du bois"}   # ce qu'on demande sans le connaître


def _il(o):
    return "elle" if o.get("genre") == "f" else "il"


def _si_il(o):
    return "si elle" if o.get("genre") == "f" else "s'il"


def _ou_dit(monde, lieu):
    """Où il dit avoir sa ressource : « dans la réserve », « sur lui »."""
    from .francais import designer, lieu as designer_lieu
    if lieu in monde.data["salles"]:
        return " dans " + designer_lieu(monde.data["salles"][lieu])
    if lieu in monde.objets and monde.objets[lieu]["type"] == "personnage":
        return " sur lui"
    return " dans " + designer(monde.objets[lieu]) if lieu in monde.objets else ""


def _avec_joueur(monde, id, etape, lignes):
    """Un geste social d'un PNJ vers le joueur : lui remettre un objet (vendu, prêté, rendu), ou lui
    redemander ce qu'il lui a prêté. Il faut le savoir là et pouvoir se parler, comme avec un PNJ.
    Le joueur n'a pas d'esprit : redemandé, il rend l'objet ou le garde à son gré ; le PNJ s'en
    souvient (``pret_reclame``), et un prêt échu qu'il ne lui rend pas lui coûte sa confiance
    (``biens.prets_reclames``). Renvoie True si le PNJ a obtenu ce qu'il visait."""
    from .biens import echu, pret
    from .francais import accorder, designer
    from .ouie import retentir
    from .pnj import _chroniquer, _rate, se_parler
    from .social import _qui
    from .spatial import porte_par
    from .voix import personne_pour_joueur
    op = etape["operation"]
    objet = monde.objets.get(etape["outil"])
    if objet is None or op not in ("remettre", "demander"):
        return False
    if monde.joueur["salle"] != monde.objets[id]["lieu"]:
        return _rate(monde, id, "joueur")   # Il ne le trouve pas là où il le croyait.
    if not se_parler(monde, id, "joueur"):
        return False
    nom = personne_pour_joueur(monde, id, court=True)[0]
    if op == "remettre":
        if not porte_par(monde, objet["id"], id):
            return False
        vendu = any(x["condition"] == {"objet": objet["id"], "remettre": "joueur"}
                    for x in esprit(monde, id)["engagements"])
        remettre(monde, id, "joueur", objet["id"])
        _chroniquer(monde, id, f"{_qui(monde, id)} remet {designer(objet)} au joueur.", "social")
        lignes.append(f"{nom} te remet {designer(objet)}" + (" : tu l'avais payé." if vendu else "."))
        retentir(monde, id, "dire", texte=f"{_qui(monde, id)} remet {designer(objet)} à {monde.joueur['nom']}.",
                 cites=["joueur", objet["id"]], vers=["joueur"])
        return True
    p = pret(monde, objet["id"])
    if not p or p["de"] != id or p["a"] != "joueur" or not porte_par(monde, objet["id"], "joueur"):
        return False
    texte = f"{_qui(monde, id)} demande à {monde.joueur['nom']} de lui rendre {designer(objet)}."
    _chroniquer(monde, id, texte, "social")
    lignes.append(f"{nom} te demande de lui rendre {designer(objet)}"
                  + (f" : {_il(monde.objets[id])} te l'a {accorder(objet, 'prêté')} il y a longtemps."
                     if echu(monde, objet["id"]) else "."))
    retentir(monde, id, "dire", texte=texte, cites=["joueur", objet["id"]], vers=["joueur"])
    memoriser(monde, id, {"type": "pret_reclame", "objet": objet["id"], "a": "joueur", "pret": p["minute"],
                          "echu": echu(monde, objet["id"])})
    # La réponse est au joueur : il ne le redemande pas de sitôt (``deliberation.tient``).
    from .deliberation import retenir_refus
    retenir_refus(monde, id, "joueur", "demander", "attente", objet=objet["id"])
    return False


def phrase_condition(monde, condition):
    from .francais import designer, lieu
    o = designer(monde.objets[condition["objet"]])
    if "lieu" in condition:
        return f"{o} soit dans {lieu(monde.data['salles'][condition['lieu']])}"
    x = monde.objets[condition["objet"]]
    pluriel = x.get("pluriel")
    return (f"{o} {'soient' if pluriel else 'soit'} {'allumé' if 'allume' in condition else 'verrouillé'}"
            + ("e" if x.get("genre") == "f" else "") + ("s" if pluriel else ""))


def phrase_affirmee(monde, sujet, attribut, valeur, pour_joueur):
    """Ce qui est affirmé, vu du joueur (« tu es ») ou de la chronique (« Corvus est »)."""
    texte = _phrase(monde, sujet, attribut, valeur)
    if sujet == "joueur" and texte.startswith("toi est"):
        texte = ("tu es" if pour_joueur else monde.joueur["nom"] + " est") + texte[len("toi est"):]
    if not pour_joueur:
        texte = texte.replace("porté par toi", "porté par " + monde.joueur["nom"])
    return texte


def empeche(monde, id, engagement):
    """Une contrepartie payée qu'il ne peut plus livrer : la part ou l'objet qu'il vendait n'existe
    plus, n'est plus à lui, ou n'en a plus une part (``deliberation.parts``) ; une tâche payée qu'il ne
    voit plus comment faire (aucun plan, sur ce qu'il croit : le bois qu'il comptait employer a été vu
    épuisé, ce qu'il comptait demander lui a été refusé, et ce refus tient). Il le sait : le prix est
    rendu ou dû dès maintenant (``engagements_echus``).

    Une tâche se juge ici par le même devis qui l'a fait accepter (``planification.devis_pulsion`` :
    ses seuls moyens, ceux que lui donne ou prêterait celui qui le paie) : rien ne la dit impossible
    tant que ce qu'il croit n'a pas changé depuis qu'il l'a acceptée."""
    from .deliberation import parts
    from .planification import devis_pulsion
    from .vol import proprietaire
    paye = engagement.get("paye")
    if not paye:
        return False
    if paye["quoi"] == "tache":
        return devis_pulsion(monde, id, engagement["condition"], engagement["pour"]) is None
    o = monde.objets.get(paye["objet"])
    return o is None or proprietaire(monde, o) != id or paye["quoi"] == "part" and parts(o) <= 0


def engagements_echus(monde, id):
    """Retire les engagements tenus, trop anciens ou qu'il ne peut plus tenir ; les souvenirs gardent
    la trace. Une part payée d'avance et non servie à l'échéance est rendue, ou due
    (``biens.rembourser``). Une garde finie, ce qu'il en porte encore (le bien, ses clés) lui reste
    prêté : il le rendra."""
    from .biens import _cles, preter, rembourser
    from .spatial import porte_par
    from .vol import proprietaire
    e = esprit(monde, id)
    restants, finis = [], []
    for engagement in e["engagements"]:
        if tenu(monde, id, engagement["condition"], engagement["minute"]):
            memoriser(monde, id, {"type": "engagement_tenu", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
            finis.append(engagement)
            if (engagement.get("paye") or {}).get("quoi") == "tache":
                from .pnj import _chroniquer
                from .social import _qui
                _chroniquer(monde, id, f"{_qui(monde, id)} a fait le travail que {_qui(monde, engagement['pour'])} "
                                       f"lui avait payé pour que {phrase_condition(monde, engagement['condition'])}.", "compte")
        elif monde.data["minutes"] - engagement["minute"] > ENGAGEMENT_MAX or empeche(monde, id, engagement):
            memoriser(monde, id, {"type": "engagement_abandonne", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
            finis.append(engagement)
            if engagement.get("paye"):
                paye = engagement["paye"]
                rembourser(monde, id, engagement["pour"], paye["prix"], paye["objet"], paye["quoi"])
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


def executer(monde, id, etape, lignes):
    """Un geste social d'une minute ; renvoie True s'il a obtenu ce qu'il visait."""
    from .francais import complement_de, designer
    from .pnj import _chroniquer
    from .esprits import percoit
    from .social import _qui, faire_entendre
    from .spatial import porte_par
    autre, op = etape["cible"], etape["operation"]
    o = monde.objets.get(autre)
    from .pnj import _rate, se_parler
    if autre == "joueur":
        return _avec_joueur(monde, id, etape, lignes)
    if not o or o["type"] != "personnage" or not o.get("profil"):
        return False
    if o["lieu"] != monde.objets[id]["lieu"]:
        # Personne ne lui répond là où il le croyait : il l'apprend, comme tout geste manqué.
        return _rate(monde, id, autre)
    if not se_parler(monde, id, autre):
        return False  # Ils ne peuvent ni se voir ni s'entendre : rien ne se dit.
    a, b, contenu = _qui(monde, id), _qui(monde, autre), etape.get("contenu", {})
    objet = monde.objets.get(etape["outil"])
    transmis = []  # Ce que la parole transmet à qui l'entend sans en être le destinataire.
    reponse, dite = "", True  # Ce que l'autre y répond, et s'il le dit de sa voix.
    if op == "dire":
        issue = affirmer(monde, id, autre, contenu["sujet"], contenu["attribut"], contenu["valeur"])
        recit = f"{a} dit à {b} que {phrase_affirmee(monde, contenu['sujet'], contenu['attribut'], contenu['valeur'], False)}"
        clair = f"{a} dit à {b} que {phrase_affirmee(monde, contenu['sujet'], contenu['attribut'], contenu['valeur'], True)}."
        cites, reussi = [contenu["sujet"], contenu["valeur"] if isinstance(contenu["valeur"], str) else None], True
        transmis = [{"type": "affirmation", **{k: contenu[k] for k in ("sujet", "attribut", "valeur")}}]
        memoriser(monde, id, {"type": "dit", "a": autre, "sujet": contenu["sujet"], "attribut": contenu["attribut"]})
    elif op == "demander" and "ressource" in contenu:
        # « As-tu du bois ? » : il répond par ce qu'il a vraiment, et l'autre l'apprend.
        issue, dit = enqueter(monde, id, autre, contenu["ressource"])
        recit = f"{a} demande à {b} {_si_il(o)} a {RESSOURCES[contenu['ressource']]}"
        clair = recit + "."
        reponse = (f"{b} dit avoir " + " et ".join(designer(monde.objets[k]) + _ou_dit(monde, lieu) for k, lieu in dit)
                   + "." if dit else f"{b} dit n'en avoir pas." if issue == "rien" else f"{b} refuse de répondre.")
        cites = [k for k, _ in dit] + [lieu for _, lieu in dit]
        reussi = issue == "dit"
    elif op == "engager":
        condition, prix = contenu["condition"], contenu["prix"]
        issue = engager(monde, id, autre, condition, prix)
        recit = (f"{a} offre {prix} pièce{'s' if prix > 1 else ''} à {b} pour qu'{_il(o)} fasse en sorte que "
                 f"{phrase_condition(monde, condition)}")
        clair = recit + "."
        reponse = f"{b} accepte et prend l'argent." if issue == "accepte" else f"{b} refuse."
        cites = [condition["objet"], condition.get("lieu")]
        reussi = issue == "accepte"
    elif op in ("demander", "acheter"):
        if objet is None:
            return False
        # La nature de la demande se juge avant l'échange : après un prêt, le demandeur porte l'objet.
        part = demande_de_part(monde, id, autre, objet["id"])
        prix = contenu.get("prix", 0) if op == "acheter" else 0
        issue = demander(monde, id, autre, objet["id"], contenu.get("foyer"), prix)
        quoi = "une part " + complement_de(objet) if part else designer(objet)
        recit = (f"{a} achète {quoi} à {b} pour {prix} pièce{'s' if prix > 1 else ''}" if op == "acheter"
                 else f"{a} demande {quoi} à {b}")
        clair = recit + "."
        reponse = {"remis": f"{b} lui remet {designer(objet)}.", "rendu": f"{b} lui rend {designer(objet)}.",
                   "vendu": f"{b} accepte et prend l'argent.",
                   "promis": f"{b} accepte de lui en donner."}.get(issue, f"{b} refuse.")
        dite = issue not in ("remis", "rendu")  # Remettre l'objet est un geste, pas une parole.
        cites, reussi = [objet["id"]], issue in ("remis", "rendu", "promis", "vendu")
    elif op == "demander_feu":
        source = monde.objets.get(contenu.get("allumer"))
        if objet is None or source is None:
            return False
        issue = demander_feu(monde, id, autre, objet["id"], source["id"])
        recit = f"{a} demande du feu à {b} pour {designer(source)}"
        clair = recit + "." + (f" {b} l'allume à {designer(objet)}." if issue == "allume" else f" {b} refuse.")
        cites, reussi = [objet["id"], source["id"]], issue == "allume"
        if reussi:
            # Allumée dans sa main : il la ménagera quand elle ne lui servira plus (``menager_flamme``).
            memoriser(monde, id, {"type": "flamme_employee", "objet": source["id"]})
        elif issue == "absent":
            from .pnj import _rate
            _rate(monde, id, objet["id"])   # Il ne la porte pas : il l'apprend.
        if issue in ("allume", "eteinte", "impossible"):
            constater(monde, id, source["id"], "essai")
            if objet["id"] in monde.objets:
                constater(monde, id, objet["id"], "vu")
    elif op == "confier":
        issue = confier(monde, id, autre, contenu)
        recit = f"{a} demande à {b} de faire en sorte que {phrase_condition(monde, contenu)}"
        clair = recit + "."
        reponse = f"{b} accepte." if issue in ("accepte", "deja") else f"{b} refuse."
        cites = [contenu["objet"], contenu.get("lieu")]
        reussi = issue in ("accepte", "deja")
    else:
        if objet is None or not porte_par(monde, objet["id"], id):
            return False
        from .vol import proprietaire
        rendu = proprietaire(monde, objet) == autre
        remettre(monde, id, autre, objet["id"])
        issue, recit = ("rendu", f"{a} rend {designer(objet)} à {b}") if rendu else (
            "remis", f"{a} remet {designer(objet)} à {b}")
        clair, cites, reussi = recit + ".", [objet["id"]], True
    _chroniquer(monde, id, f"{recit} ({issue}).", "social")
    nommes = [x for x in cites if x and (x in monde.objets or x in monde.data["salles"] or x == "joueur")]
    if issue == "qui_va_la":
        # Il ne sait à qui est cette voix : « Qui va là ? » ; l'autre se nomme (``voix.se_nommer``),
        # et redemandera.
        from .social import qui_va_la
        faire_entendre(monde, id, autre, clair, nommes, lignes, transmis)
        qui_va_la(monde, id, autre, lignes)
    else:
        faire_entendre(monde, id, autre, clair, nommes, lignes, transmis, reponse, dite)
    if "ressource" not in contenu:   # « As-tu… ? » retient sa réponse (``enqueter``).
        # Un feu refusé l'est pour cette source ; un objet demandé, pour cet objet ; une tâche, pour ce
        # qu'elle vise. Le refus se retient selon sa cause (``deliberation.retenir_refus``) ; accordée,
        # la demande n'a plus de refus qui tienne.
        from .deliberation import oublier_refus, retenir_refus
        vise = (contenu.get("allumer") if op == "demander_feu" else objet["id"] if objet
                else contenu["condition"]["objet"] if op == "engager" else contenu.get("objet"))
        if reussi:
            for x in (("demander", "acheter") if op in ("demander", "acheter") else (op,)):
                oublier_refus(monde, id, autre, x, vise)
        else:
            condition = contenu["condition"] if op == "engager" else contenu if op == "confier" else None
            retenir_refus(monde, id, autre, op, issue, objet=vise,
                          prix=contenu["prix"] if op == "engager" else None,
                          tache=tache(condition) if condition else None,
                          flamme=objet["id"] if op == "demander_feu" and objet else None)
    return reussi
