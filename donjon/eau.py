"""Le niveau d'eau : une quantité du monde, comparée à l'altitude de chaque salle.

Le scénario déclare une crue (``data["crue"]``) : le niveau de départ, puis la montée par heure,
l'heure du pic et sa hauteur, chacune entre deux bornes ; la baisse par heure, facultative, vaut
sinon la montée. Les valeurs sont tirées une fois, au départ, de la graine, par un tirage qui
lui est propre (``random.Random(f"{seed}:crue")``) : les jets de la partie (``Monde.d20``) ne
les décalent pas. Le niveau se déduit ensuite de la minute : parti du niveau de départ, il
monte jusqu'à l'heure du pic sans en dépasser la hauteur (il s'y tient), puis baisse, sans
redescendre sous son départ.

Une salle sous ce niveau est mouillée ; à partir de ``NOYEE_CM`` d'eau, elle est noyée : on n'y
entre plus (chemins, pas, trajets) et aucun feu posé n'y brûle. Se tenir dans l'eau trempe,
joueur et PNJ (``corps``). On sent l'eau de la salle où l'on se tient, on voit celle des salles
voisines par un passage ouvert : pour un PNJ, une croyance ``eau`` (en cm) sur la salle. Revue
après ``REPERE`` minutes, l'eau donne sa vitesse : il l'attend là où elle arrivera avant
``HORIZON`` minutes (``menacee``), à tort si le pic est proche.
"""
import random

from .monde import ErreurMonde

NOYEE_CM = 100         # d'eau : la salle ne se traverse plus
REPERE = 15            # minutes entre deux vues de l'eau pour en juger la vitesse
HORIZON = 60           # minutes : l'eau attendue d'ici là menace déjà un lieu
ETATS = ("seche", "mouillee", "noyee")
BORNES = ("montee_cm_heure", "heure_pic", "hauteur_pic_cm")
HISTORIQUE_MAX = 200
ANNONCES = {"mouillee": "L'eau gagne le sol où tu te tiens.",
            "noyee": "L'eau monte encore : la salle est noyée, il faut en sortir.",
            "seche": "L'eau se retire du sol où tu te tiens."}


def active(monde):
    return "crue" in monde.data


def installer(monde):
    """Tire les valeurs de la crue à la première installation ; note l'état de départ des salles."""
    crue = monde.data.get("crue")
    if crue is None:
        return
    if "tirage" not in crue:
        b = crue["bornes"]
        r = random.Random(f'{monde.data["seed"]}:crue')
        montee = r.randint(*b["montee_cm_heure"])
        crue["tirage"] = {"montee_cm_heure": montee,
                          "minute_pic": r.randint(b["heure_pic"][0] * 60, b["heure_pic"][1] * 60),
                          "hauteur_pic_cm": r.randint(*b["hauteur_pic_cm"]),
                          "baisse_cm_heure": r.randint(*b["baisse_cm_heure"]) if "baisse_cm_heure" in b else montee}
    if "etats" not in crue:
        crue["etats"] = {s: etat(monde, s) for s in sorted(monde.data["salles"])}
        crue["historique"] = [{"minute": monde.data["minutes"], "salle": s, "etat": e}
                              for s, e in crue["etats"].items() if e != "seche"]


def niveau(monde, minute=None):
    """Altitude de l'eau, en cm, à la minute donnée (par défaut, maintenant)."""
    crue = monde.data["crue"]
    x, depart = crue["tirage"], crue["depart_cm"]
    t = monde.data["minutes"] if minute is None else minute
    if t <= x["minute_pic"]:
        return min(x["hauteur_pic_cm"], depart + x["montee_cm_heure"] * t // 60)
    return max(depart, niveau(monde, x["minute_pic"]) - x["baisse_cm_heure"] * (t - x["minute_pic"]) // 60)


def altitude(monde, salle):
    from .spatial import altitude as sol
    return sol(monde, salle)


def profondeur(monde, salle):
    """Hauteur d'eau sur le sol de la salle, en cm ; 0 sans crue ou au sec."""
    if not active(monde) or salle not in monde.data["salles"]:
        return 0
    return max(0, niveau(monde) - altitude(monde, salle))


def etat(monde, salle):
    p = profondeur(monde, salle)
    return "noyee" if p >= NOYEE_CM else "mouillee" if p > 0 else "seche"


def noyee(monde, salle):
    return profondeur(monde, salle) >= NOYEE_CM


def sous_l_eau(monde, o):
    """Un objet posé, que personne ne porte, dans une salle noyée : aucune flamme n'y tient."""
    from .esprits import _porteur
    from .perception import salle_source
    return _porteur(monde, o) is None and noyee(monde, salle_source(monde, o))


def hauteur(cm):
    """Où l'eau arrive sur quelqu'un debout."""
    return ("aux chevilles" if cm < 15 else "aux genoux" if cm < 50 else "à la taille" if cm < 90
            else "à la poitrine")


def lieu(monde, id):
    return monde.joueur["salle"] if id == "joueur" else monde.objets[id]["lieu"]


def refuser_entree(monde, salle):
    """On n'entre pas dans une salle noyée : le refus dit au MJ ce qui passerait."""
    if noyee(monde, salle):
        nom = monde.data["salles"][salle]["nom"]
        raise ErreurMonde(f"L'eau a noyé : {nom}. Elle est trop haute pour y passer.",
                          f"salle {salle} noyée ({profondeur(monde, salle)} cm d'eau, {NOYEE_CM} au plus pour "
                          "passer) : choisis une autre direction ou attends que l'eau baisse.")


def tremper(monde, id, lignes=None):
    """Qui se tient dans l'eau est trempé ; le joueur l'apprend en y entrant."""
    p = profondeur(monde, lieu(monde, id))
    if not p:
        return
    from .corps import corps
    faits = corps(monde, id)
    if not faits["trempe"] and id == "joueur" and lignes is not None:
        lignes.append(f"L'eau t'arrive {hauteur(p)} : te voilà trempé.")
    faits["trempe"] = max(1, faits["trempe"])
    faits["seche"] = 0


def voisines(monde, salle):
    """Salles voisines par un passage ouvert : on voit, on entend l'eau qui y monte."""
    vues = []
    for sortie in monde.data["salles"][salle]["sorties"].values():
        porte = monde.objets.get(sortie.get("porte") or "")
        if sortie["vers"] in monde.data["salles"] and not (porte and not porte.get("ouverte")):
            vues.append(sortie["vers"])
    return vues


def eau_crue(monde, id, salle):
    """Ce que le PNJ croit de l'eau dans une salle, en cm ; 0 s'il n'en sait rien."""
    from .esprits import lire
    c = lire(monde, id)["croyances"].get(salle, {}).get("eau")
    return c["valeur"] if c else 0


def noyee_crue(monde, id, salle):
    return eau_crue(monde, id, salle) >= NOYEE_CM


def estimation(monde, id):
    """(minute, niveau, montée en cm/h) : dernier niveau vu et dernière vitesse
    mesurée entre deux repères ; None sans mesure de vitesse."""
    from .esprits import lire
    vues = [c for a in lire(monde, id)["croyances"].values()
            if (c := a.get("eau")) and c.get("niveau") is not None]
    # Revoir une salle rafraîchit son niveau, pas la date de sa vitesse :
    # celle-ci n'est remesurée qu'au renouvellement du repère. Sinon, passer
    # devant deux salles promeut tour à tour deux anciennes pentes opposées.
    # Le niveau est commun à la crue : la dernière vue l'ancre, le dernier
    # repère mesuré donne la pente, même quand on ne voit plus cette salle.
    vitesses = [(c["repere"][0], c["montee"]) for c in vues
                if c.get("repere") is not None and c.get("montee") is not None]
    if not vitesses:
        return None
    minute, niveau_vu = max((c["minute"], c["niveau"]) for c in vues)
    return minute, niveau_vu, max(vitesses)[1]


def monte(monde, id):
    """Il a vu l'eau monter, la dernière fois qu'il en a jugé."""
    e = estimation(monde, id)
    return e is not None and e[2] > 0


def menacee(monde, id, salle, horizon=None):
    """Il croit l'eau dans la salle, ou l'y attend avant ``HORIZON`` minutes à la vitesse où il l'a
    vue monter."""
    return attendue(monde, id, salle, horizon) > 0


def attendue(monde, id, salle, horizon=None, *, projection=False):
    """La hauteur d'eau, en cm, qu'il attend dans la salle d'ici ``HORIZON`` minutes : celle qu'il y
    croit, ou plus selon sa prévision retenue (``menacee`` : plus de 0).

    ``projection`` fournit aux routes (hauteur crue, droite au présent, pente en cm/min),
    sans borner la droite au sol avant de la projeter. Les mesures restent intactes.
    """
    from .esprits import prevision
    cru = eau_crue(monde, id, salle)
    c = prevision(monde, id, salle)
    e = c["valeur"] if c else None
    if type(e) is bool:
        # Une conclusion qualitative n'invente ni profondeur ni vitesse.
        # Le minimum positif porte la menace, jamais une noyade ; la mesure
        # propre d'eau présente reste prioritaire même face à un avis négatif.
        attendu = max(cru, int(e))
        return (attendu, 0, 0) if projection else attendu
    if projection:
        # Photographie affine pour les routes : garder la droite sous le sol.
        vitesse = max(0, e[2]) / 60 if e else 0
        niveau = (e[1] + vitesse * (monde.data["minutes"] + monde.data.get("dixiemes", 0) / 600 - e[0])
                  if vitesse else None)
        return cru, niveau - altitude(monde, salle) if niveau is not None else 0, vitesse
    if e is None or e[2] <= 0:
        return cru
    minute, niveau_vu, montee = e
    niveau_attendu = niveau_vu + montee * (monde.data["minutes"] + (HORIZON if horizon is None else horizon) - minute) / 60
    return max(cru, niveau_attendu - altitude(monde, salle))


def noyee_attendue(monde, id, salle):
    """Il croit la salle noyée, ou l'attend noyée avant ``HORIZON`` minutes."""
    return attendue(monde, id, salle) >= NOYEE_CM


def en_peril(monde, id):
    """Quitter l'eau crue présente, ou la noyade attendue, sans interrompre une traversée sûre."""
    ici = lieu(monde, id)
    if not (active(monde) and ici in monde.data["salles"]
            and (eau_crue(monde, id, ici) > 0 or noyee_attendue(monde, id, ici))):
        return False
    # Une traversée en cours ne devient pas un séjour à la minute ronde.
    # Elle garde la main seulement si la même admissibilité prouve encore
    # le départ avant la noyade, jusqu'au but sûr ; sinon, évacuation prioritaire.
    from .esprits import lire
    esprit = lire(monde, id)
    intention = esprit["intention"]
    plan = intention["plan"] if intention else []
    # Même préfixe déjà accompli que dans pnj.agir : une perception à
    # l'arrivée peut faire choisir avant que l'exécution retire ces étapes.
    debut = 0
    while debut < len(plan) and plan[debut]["operation"] == "aller" and plan[debut]["lieu"] == ici:
        debut += 1
    plan = plan[debut:]
    if plan and plan[0]["operation"] == "aller" and plan[0]["lieu"] != ici:
        from .planification import Vue, depart
        from .route_admissible import refus
        v = Vue(monde, id)
        e = depart(monde, id, v)
        cible = plan[0]["lieu"]
        route = v.route(e, cible)
        if route is not None and refus(v, e, route, cible, depart_compris=True) is None:
            return False
    # Un geste fini qui peut encore aboutir n'est pas un séjour : l'interrompre
    # devant sa cible le ferait reprendre au retour (inspection, livraison,
    # repas…). L'attente d'une occasion, elle, ne garantit aucun achèvement.
    from .pnj import DUREES
    from .temps import MINUTE
    if plan and esprit["patience"] is None and not noyee_attendue(monde, id, ici):
        duree = DUREES.get(plan[0]["operation"])
        if duree is not None and attendue(monde, id, ici, horizon=duree / MINUTE) < NOYEE_CM:
            return False
    return True


def _rang(cm):
    return 2 if cm >= NOYEE_CM else 1 if cm > 0 else 0


def percevoir(monde, id):
    """L'eau de sa salle et des salles voisines ouvertes devient croyance ; la voir gagner un
    lieu inquiète. Revue au moins ``REPERE`` minutes plus tard, elle donne sa vitesse."""
    ici = monde.joueur["salle"] if id == "joueur" else monde.objets[id]["lieu"]
    if not active(monde) or ici not in monde.data["salles"]:
        return
    for salle in [ici, *voisines(monde, ici)]:
        observer(monde, id, salle)


def observer(monde, id, salle, source="vu"):
    """Ce qu'il voit de l'eau d'une salle devient croyance : sa hauteur, le niveau, et la vitesse
    depuis son repère ; la voir gagner la salle inquiète."""
    from .esprits import croire, lire
    t, vue = monde.data["minutes"], profondeur(monde, salle)
    avant = lire(monde, id)["croyances"].get(salle, {}).get("eau") or {}
    if id != "joueur" and _rang(vue) > _rang(avant.get("valeur", 0)):
        from .deliberation import inquieter
        inquieter(monde, id, "crue")
    # Sous le sol, le niveau ne se voit pas : seule l'eau présente donne un repère.
    niveau_vu = altitude(monde, salle) + vue if vue else None
    repere, montee = avant.get("repere"), avant.get("montee")
    if niveau_vu is None:
        repere, montee = None, None
    elif repere is None or t < repere[0]:
        # Le moteur fait voir la fin d'un geste avant d'en dérouler les minutes : un repère
        # postérieur est repris à cette vue.
        repere = [t, niveau_vu]
        montee = None
    elif t - repere[0] >= REPERE:
        montee = round((niveau_vu - repere[1]) * 60 / (t - repere[0]))
        repere = [t, niveau_vu]
    croire(monde, id, salle, "eau", vue, source, niveau=niveau_vu, repere=repere, montee=montee)


def inonder(monde, lignes):
    """Une minute de crue : les salles changent d'état, les feux posés dans une salle noyée
    s'éteignent. Appelé à chaque minute franchie (``pnj.avancer``)."""
    crue = monde.data.get("crue")
    if crue is None:
        return
    historique = crue["historique"]
    for salle in sorted(monde.data["salles"]):
        e = etat(monde, salle)
        if e != crue["etats"].get(salle):
            crue["etats"][salle] = e
            historique.append({"minute": monde.data["minutes"], "salle": salle, "etat": e})
            if salle == monde.joueur["salle"]:
                lignes.append(ANNONCES[e])
    from .francais import designer
    from .perception import salle_source
    for o in monde.objets.values():
        if o.get("allume") and sous_l_eau(monde, o):
            o["allume"] = False
            historique.append({"minute": monde.data["minutes"], "eteint": o["id"], "salle": salle_source(monde, o)})
            if monde.present_physique(o["id"]):
                lignes.append(designer(o, debut=True) + " s'éteint sous l'eau.")
    del historique[:-HISTORIQUE_MAX]


def decrire(monde, salle):
    """Pour le MJ et la scène : l'eau d'une salle, en mots et en cm ; None au sec."""
    p = profondeur(monde, salle)
    if not p:
        return None
    return {"etat": etat(monde, salle), "profondeur_cm": p, "hauteur": hauteur(p)}


def verifier(monde):
    crue = monde.data.get("crue")
    if crue is None:
        return
    assert (isinstance(crue, dict) and set(crue) == {"depart_cm", "bornes", "tirage", "etats", "historique"}
            and type(crue["depart_cm"]) is int), "Crue mal formée"
    b = crue["bornes"]
    assert (isinstance(b, dict) and set(BORNES) <= set(b) <= {*BORNES, "baisse_cm_heure"}
            and all(isinstance(v, list) and len(v) == 2 and all(type(x) is int for x in v) and v[0] <= v[1]
                    for v in b.values())
            and b["montee_cm_heure"][0] > 0 and b.get("baisse_cm_heure", [1])[0] > 0
            and b["heure_pic"][0] >= 0), "Bornes de crue invalides"
    x = crue["tirage"]
    assert (set(x) == {"montee_cm_heure", "minute_pic", "hauteur_pic_cm", "baisse_cm_heure"}
            and all(type(v) is int for v in x.values()) and x["montee_cm_heure"] > 0
            and x["baisse_cm_heure"] > 0 and x["minute_pic"] >= 0), "Tirage de crue invalide"
    assert (set(crue["etats"]) == set(monde.data["salles"])
            and all(e in ETATS for e in crue["etats"].values())), "États de crue invalides"
    assert (isinstance(crue["historique"], list) and len(crue["historique"]) <= HISTORIQUE_MAX
            and all(isinstance(h, dict) and type(h.get("minute")) is int and h.get("salle") in monde.data["salles"]
                    and (set(h) == {"minute", "salle", "etat"} and h["etat"] in ETATS
                         or set(h) == {"minute", "salle", "eteint"} and isinstance(h["eteint"], str))
                    for h in crue["historique"])), "Historique de crue invalide"
