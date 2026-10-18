"""Échanges typés entre personnages : affirmer, demander un objet, confier une tâche, remettre.

Les mêmes règles valent pour le joueur et pour les PNJ. Une affirmation démentie par ce que
l'auditeur a vu récemment est rejetée et le locuteur perd sa confiance ; sinon un jet de CHA
du locuteur, contre un DD que la confiance de l'auditeur abaisse ou relève, décide s'il la
croit. Un objet n'est remis que par celui qui le porte, s'il fait confiance au demandeur et
n'en a pas besoin. Une tâche confiée devient un engagement que le planificateur du moteur
exécute quand rien de plus urgent ne presse. Tout est déterministe hors des jets du moteur.
"""
from .esprits import croire, esprit, lire, memoriser, percevoir
from .paroles import _phrase, _stats_pnj, dementi, jet_persuasion

ENGAGEMENT_MAX = 240   # minutes avant qu'un engagement non tenu soit abandonné


def clarte(monde, auditeur):
    """Un auditeur d'INT faible retient moins sûrement ce qu'on lui dit."""
    return 0.5 if _stats_pnj(monde, auditeur)["INT"] <= 8 else 1.0


def affirmer(monde, locuteur, auditeur, sujet, attribut, valeur):
    """« dementi », « doute », « crue » ou « decouvert » (crue puis démentie sous ses yeux)."""
    e = esprit(monde, auditeur)
    if dementi(monde, auditeur, sujet, attribut, valeur):
        croire(monde, auditeur, locuteur, "fiable", False, "vu")
        memoriser(monde, auditeur, {"type": "mensonge_dementi", "locuteur": locuteur,
                                    "sujet": sujet, "attribut": attribut})
        return "dementi"
    if not jet_persuasion(monde, auditeur, locuteur, 10)[0]:
        memoriser(monde, auditeur, {"type": "parole_doutee", "locuteur": locuteur,
                                    "sujet": sujet, "attribut": attribut})
        return "doute"
    lieu = {"salle": valeur if valeur in monde.data["salles"] else None, "case": None} if attribut == "lieu" else {}
    croire(monde, auditeur, sujet, attribut, valeur, "dit:" + locuteur, round(0.7 * clarte(monde, auditeur), 2), **lieu)
    memoriser(monde, auditeur, {"type": "parole_crue", "locuteur": locuteur, "sujet": sujet, "attribut": attribut})
    # Ce qu'il a sous les yeux peut le démentir aussitôt.
    percevoir(monde, auditeur)
    if any(s["type"] == "mensonge_decouvert" and s.get("sujet") == sujet for s in e["memoire"][-3:]):
        return "decouvert"
    return "crue"


def necessaire(monde, auditeur, objet):
    """Un objet qui sert son plan en cours ou une de ses pulsions (l'objet, sa clé) n'est pas prêté."""
    intention = lire(monde, auditeur)["intention"]
    if intention and any(objet in (e["cible"], e["outil"]) for e in intention["plan"]):
        return True
    profil = monde.objets[auditeur].get("profil")
    for pulsion in (profil or {}).get("pulsions", []):
        cible = pulsion["condition"].get("objet")
        if cible and (objet == cible or cible in monde.objets[objet].get("ouvre", [])):
            return True
    return False


def demande_de_part(monde, demandeur, auditeur, objet):
    """Un affamé peut demander une part d'une nourriture qui appartient à l'autre, même rangée ailleurs."""
    from .social import _proprietaire
    from .spatial import porte_par
    o = monde.objets.get(objet)
    besoins = lire(monde, demandeur)["besoins"] if demandeur != "joueur" else {}
    return bool(o and o["type"] == "nourriture" and "faim" in besoins and not porte_par(monde, objet, auditeur)
                and _proprietaire(monde, {"objet": objet}) == auditeur)


def demander(monde, demandeur, auditeur, objet):
    """« absent », « mefiance », « necessaire », « impossible », « refus », « remis » ou « promis »."""
    from .deliberation import _plan_pulsion, urgents
    from .deplacement_objet import deplacer
    from .spatial import porte_par
    part = demande_de_part(monde, demandeur, auditeur, objet)
    if objet not in monde.objets or not (part or porte_par(monde, objet, auditeur)):
        return "absent"
    confiance = lire(monde, auditeur)["croyances"].get(demandeur, {}).get("fiable")
    if confiance and not confiance["valeur"]:
        return "mefiance"
    if part:
        # Il garde la dernière part, et ne donne pas ce dont il a lui-même besoin.
        if monde.objets[objet].get("portions", 0) < 2 or "faim" in urgents(monde, auditeur):
            return "necessaire"
        condition = {"objet": objet, "servir": demandeur}
        engagements = esprit(monde, auditeur)["engagements"]
        if not any(x["condition"] == condition for x in engagements):
            if _plan_pulsion(monde, auditeur, condition) is None:
                return "impossible"
            if not jet_persuasion(monde, auditeur, demandeur, 12)[0]:
                return "refus"
            engagements.append({"condition": condition, "pour": demandeur, "minute": monde.data["minutes"]})
            memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": condition})
        if demandeur != "joueur":
            memoriser(monde, demandeur, {"type": "promis", "de": auditeur, "objet": objet})
        return "promis"
    if necessaire(monde, auditeur, objet):
        return "necessaire"
    if not jet_persuasion(monde, auditeur, demandeur, 12)[0]:
        return "refus"
    deplacer(monde, objet, demandeur)
    memoriser(monde, auditeur, {"type": "pret", "objet": objet, "a": demandeur})
    if demandeur != "joueur":
        memoriser(monde, demandeur, {"type": "recu", "objet": objet, "de": auditeur})
    return "remis"


def confier(monde, demandeur, auditeur, condition):
    """« mefiance », « deja », « impossible », « refus » ou « accepte »."""
    from .deliberation import _plan_pulsion, satisfaite
    confiance = lire(monde, auditeur)["croyances"].get(demandeur, {}).get("fiable")
    if confiance and not confiance["valeur"]:
        return "mefiance"
    if satisfaite(monde, auditeur, condition):
        return "deja"
    if _plan_pulsion(monde, auditeur, condition) is None:
        return "impossible"  # Il ne voit pas comment s'y prendre avec ce qu'il sait.
    if not jet_persuasion(monde, auditeur, demandeur, 12)[0]:
        return "refus"
    esprit(monde, auditeur)["engagements"].append(
        {"condition": dict(condition), "pour": demandeur, "minute": monde.data["minutes"]})
    memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": dict(condition)})
    return "accepte"


def remettre(monde, donneur, receveur, objet):
    from .deplacement_objet import deplacer
    from .vol import proprietaire
    if proprietaire(monde, monde.objets[objet]) == donneur:
        memoriser(monde, donneur, {"type": "pret", "objet": objet, "a": receveur})
    deplacer(monde, objet, receveur)
    if receveur != "joueur":
        memoriser(monde, receveur, {"type": "recu", "objet": objet, "de": donneur})


def servir(monde, id, nourriture, pour, lignes):
    """Donner une part à quelqu'un de la même salle, qu'on appelle s'il est hors de vue : il la
    mange, et sait gré de l'avoir reçue."""
    from .deliberation import SATIETE
    from .esprits import percoit
    from .francais import complement_de
    from .pnj import _chroniquer
    from .social import _qui, faire_entendre
    o, autre = monde.objets[nourriture], monde.objets.get(pour)
    if (o.get("portions", 0) <= 0 or not autre or autre["type"] != "personnage"
            or autre["lieu"] != monde.objets[id]["lieu"]):
        return False
    appel = "" if percoit(monde, id, pour) and percoit(monde, pour, id) else f"appelle {_qui(monde, pour)} et lui "
    o["portions"] -= 1
    besoins = esprit(monde, pour)["besoins"]
    if "faim" in besoins:
        besoins["faim"] = max(0.0, besoins["faim"] - SATIETE)
    memoriser(monde, pour, {"type": "nourri", "de": id, "objet": nourriture})
    croire(monde, pour, id, "fiable", True, "vu")
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


def phrase_condition(monde, condition):
    from .francais import designer
    o = designer(monde.objets[condition["objet"]])
    if "lieu" in condition:
        return f"{o} soit dans {monde.data['salles'][condition['lieu']]['nom']}"
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


def engagements_echus(monde, id):
    """Retire les engagements tenus ou trop anciens ; les souvenirs gardent la trace."""
    from .deliberation import satisfaite
    e = esprit(monde, id)
    restants = []
    for engagement in e["engagements"]:
        if satisfaite(monde, id, engagement["condition"]):
            memoriser(monde, id, {"type": "engagement_tenu", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
        elif monde.data["minutes"] - engagement["minute"] > ENGAGEMENT_MAX:
            memoriser(monde, id, {"type": "engagement_abandonne", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
        else:
            restants.append(engagement)
    e["engagements"] = restants


def executer(monde, id, etape, lignes):
    """Un geste social d'une minute ; renvoie True s'il a obtenu ce qu'il visait."""
    from .francais import complement_de, designer
    from .pnj import _chroniquer
    from .esprits import percoit
    from .social import _qui, faire_entendre
    from .spatial import porte_par
    autre, op = etape["cible"], etape["operation"]
    o = monde.objets.get(autre)
    if (not o or o["type"] != "personnage" or not o.get("profil") or o["lieu"] != monde.objets[id]["lieu"]
            or not percoit(monde, id, autre) or not percoit(monde, autre, id)):
        return False  # Il n'est pas là, ou ils ne se voient pas : rien ne se dit.
    a, b, contenu = _qui(monde, id), _qui(monde, autre), etape.get("contenu", {})
    objet = monde.objets.get(etape["outil"])
    if op == "dire":
        issue = affirmer(monde, id, autre, contenu["sujet"], contenu["attribut"], contenu["valeur"])
        recit = f"{a} dit à {b} que {phrase_affirmee(monde, contenu['sujet'], contenu['attribut'], contenu['valeur'], False)}"
        clair = f"{a} dit à {b} que {phrase_affirmee(monde, contenu['sujet'], contenu['attribut'], contenu['valeur'], True)}."
        cites, reussi = [contenu["sujet"], contenu["valeur"] if isinstance(contenu["valeur"], str) else None], True
    elif op == "demander":
        if objet is None:
            return False
        issue = demander(monde, id, autre, objet["id"])
        part = demande_de_part(monde, id, autre, objet["id"])
        recit = f"{a} demande {'une part ' + complement_de(objet) if part else designer(objet)} à {b}"
        clair = recit + "." + {"remis": f" {b} lui remet {designer(objet)}.",
                               "promis": f" {b} accepte de lui en donner."}.get(issue, f" {b} refuse.")
        cites, reussi = [objet["id"]], issue in ("remis", "promis")
    elif op == "confier":
        issue = confier(monde, id, autre, contenu)
        recit = f"{a} demande à {b} de faire en sorte que {phrase_condition(monde, contenu)}"
        clair = recit + "." + (f" {b} accepte." if issue in ("accepte", "deja") else f" {b} refuse.")
        cites = [contenu["objet"], contenu.get("lieu")]
        reussi = issue in ("accepte", "deja")
    else:
        if objet is None or not porte_par(monde, objet["id"], id):
            return False
        remettre(monde, id, autre, objet["id"])
        issue, recit = "remis", f"{a} remet {designer(objet)} à {b}"
        clair, cites, reussi = recit + ".", [objet["id"]], True
    _chroniquer(monde, id, f"{recit} ({issue}).", "social")
    faire_entendre(monde, id, autre, clair, [x for x in cites if x and (x in monde.objets or x == "joueur")], lignes)
    if not reussi:
        vise = objet["id"] if objet else contenu.get("objet")
        memoriser(monde, id, {"type": "refus", "de": autre, "operation": op, "raison": issue,
                              **({"objet": vise} if vise else {})})
    return reussi
