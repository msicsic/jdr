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
    if objet not in monde.objets or not (part or porte_par(monde, objet, auditeur)):
        return "absent"
    arret = accueil(monde, demandeur, auditeur)
    if arret == "qui_va_la":
        return arret
    o = monde.objets[objet]
    if not part and proprietaire(monde, o) == demandeur:
        # Son propriétaire le redemande : il le lui rend, sauf s'il s'en sert encore.
        if necessaire(monde, auditeur, objet):
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
                                **({"paye": {"objet": objet, "prix": prix}} if vente else {})})
            memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": condition})
            if vente:
                _vendre(monde, auditeur, demandeur, objet, prix)
                paye = True
        if demandeur != "joueur":
            memoriser(monde, demandeur, {"type": "promis", "de": auditeur, "objet": objet,
                                         **({"foyer": condition["objet"]} if "allume" in condition else {})})
        return "vendu" if paye else "promis"
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
    if "servir" in condition or not satisfaite(monde, id, condition):
        return False
    nouvelles = lire(monde, id)["croyances"].get(condition.get("objet"), {}).values()
    return depuis is None or any(c["minute"] >= depuis for c in nouvelles)


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
    if proprietaire(monde, o) == donneur:
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
    """Une part payée qu'il ne peut plus donner : ce qu'il vendait n'existe plus, n'est plus à lui,
    ou n'en a plus une part (``deliberation.parts``)."""
    from .deliberation import parts
    from .vol import proprietaire
    paye = engagement.get("paye")
    if not paye:
        return False
    o = monde.objets.get(paye["objet"])
    return o is None or proprietaire(monde, o) != id or parts(o) <= 0


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
        elif monde.data["minutes"] - engagement["minute"] > ENGAGEMENT_MAX or empeche(monde, id, engagement):
            memoriser(monde, id, {"type": "engagement_abandonne", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
            finis.append(engagement)
            if engagement.get("paye"):
                rembourser(monde, id, engagement["pour"], engagement["paye"]["prix"], engagement["paye"]["objet"])
        else:
            restants.append(engagement)
    e["engagements"] = restants
    for engagement in finis:
        o, de = engagement["condition"].get("objet"), engagement["pour"]
        if "rendre" in engagement["condition"] or o not in monde.objets or proprietaire(monde, monde.objets[o]) != de:
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
    if not reussi:
        vise = objet["id"] if objet else contenu.get("objet")
        memoriser(monde, id, {"type": "refus", "de": autre, "operation": op, "raison": issue,
                              **({"objet": vise} if vise else {})})
    return reussi
