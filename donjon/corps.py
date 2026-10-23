"""Le corps, commun à tous les personnages, joueur compris : faim, froid, fatigue.

Rythmes et seuils sont ceux du moteur, les mêmes pour tous. Le scénario ne déclare que des
états (``corps`` du personnage : minutes depuis le dernier repas, minutes de veille, minutes
passées trempé ; se tenir dans l'eau d'une crue en ajoute, ``eau.py``), dont découlent les
valeurs de départ ; le profil d'un PNJ ne garde que son
caractère. Le corps vit au temps réellement passé dans chaque état (``vecu.py``) : l'effort ou
le repos du geste fait, le chaud d'un feu, l'eau où l'on se tient. Les valeurs vivent dans ``esprit["besoins"]`` pour un PNJ, dans
``joueur["besoins"]`` pour le joueur, sous les noms ``faim``, ``chaleur`` (le froid) et
``repos`` (la fatigue). Un état qui presse coûte aux jets des caractéristiques qu'il touche,
comme la volonté brisée à ceux de VOL (``malus``, lu par ``caractere``).
"""
from .esprits import esprit, lire, pnjs

# Par heure : faim et fatigue montent avec le temps, plus vite à l'effort ; le froid monte loin
# d'un feu, plus vite trempé. Un besoin presse à partir de son seuil.
CORPS = {"faim": {"heure": 6, "urgence": 70},
         "repos": {"heure": 3, "urgence": 80},
         "chaleur": {"heure": 4, "trempe": 10, "urgence": 70}}   # froid sec : 4 par heure (décision du 2026-10-22)
NOMS = {"faim": "faim", "chaleur": "froid", "repos": "fatigue"}
EFFORT = 1.5           # l'effort fait monter faim et fatigue moitié plus vite
FEU_MINUTE = 3         # froid perdu par minute dans la salle d'un foyer allumé
SECHAGE = 30           # minutes au chaud pour sécher
REPOS_MINUTE = 2       # fatigue perdue par minute de repos
SATIETE = 50           # un repas
EXTREME = 95           # au-delà, la faim et le froid épuisent le joueur
MALUS = 2              # par état qui presse, aux jets des caractéristiques qu'il touche
# Ce que chaque état qui presse touche : la faim et le froid affaiblissent et rendent maladroit ;
# la fatigue aussi, et rend confus et moins attentif. Les mêmes pour tous, joueur compris.
TOUCHE = {"faim": ("FOR", "DEX"), "chaleur": ("FOR", "DEX"), "repos": ("FOR", "DEX", "INT", "PER")}
BRISURE_MAX = 5        # points de jet de VOL qu'une volonté brisée peut perdre
PV_BASE = 6
TOUCHE_BLESSURE = (("FOR", "DEX"), ("FOR", "DEX", "INT", "PER", "VOL"))
FAITS = {"repas": 180, "veille": 480, "trempe": 0}    # joueur ou PNJ sans état déclaré
CALMES = ("attendre", "observer", "examiner", "lire", "parler", "toucher", "copier", "tourner")  # sans effort


def corps(monde, id):
    """Les états déclarés et leur suite : dernier repas, veille, minutes trempé, séchage."""
    o = monde.joueur if id == "joueur" else monde.objets[id]
    return o.setdefault("corps", dict(FAITS))


def valeurs(monde, id):
    return monde.joueur.setdefault("besoins", {}) if id == "joueur" else esprit(monde, id)["besoins"]


def depart(faits):
    """Ce que le corps éprouve d'après les états déclarés."""
    trempe = faits.get("trempe", 0)
    return {"faim": min(100.0, faits.get("repas", 0) / 60 * CORPS["faim"]["heure"]),
            "repos": min(100.0, faits.get("veille", 0) / 60 * CORPS["repos"]["heure"]),
            "chaleur": min(100.0, trempe / 60 * CORPS["chaleur"]["trempe"])}


def personnages(monde):
    return ["joueur", *pnjs(monde)]


def installer(monde):
    """Valeurs de départ ; anciennes parties : les besoins du corps quittent le profil."""
    for id in personnages(monde):
        faits, v = corps(monde, id), valeurs(monde, id)
        o = monde.joueur if id == "joueur" else monde.objets[id]
        from .caractere import base
        o.setdefault("pv_max", PV_BASE + base(monde, id, "FOR"))
        o.setdefault("pv", o["pv_max"])
        faits.setdefault("inconscient", 0)
        faits.setdefault("soin", 0)
        if id != "joueur" and o.get("profil"):
            for nom in CORPS:
                ancien = monde.objets[id]["profil"]["besoins"].pop(nom, None)
                if ancien is not None and nom not in v:
                    v[nom] = float(ancien["depart"])
        for nom, valeur in depart(faits).items():
            v.setdefault(nom, round(valeur, 3))
        faits.setdefault("seche", 0)
        faits.setdefault("volonte_brisee", 0)
        if id == "joueur":
            faits.setdefault("peine", 0)


def au_chaud(monde, id):
    """Dans la salle d'un foyer allumé."""
    from .perception import allumee
    salle = monde.joueur["salle"] if id == "joueur" else monde.objets[id]["lieu"]
    return any(o.get("foyer") and allumee(o) and monde.present_physique(o["id"], salle=salle)
               for o in monde.objets.values())


def dans_l_eau(monde, id):
    """Debout dans l'eau d'une crue."""
    from .eau import lieu, profondeur
    return profondeur(monde, lieu(monde, id)) > 0


def vivre(monde, id, minutes=1, effort=False, repos=False, chaud=None, eau=None):
    """Le corps change avec le temps : faim, fatigue, froid ; repos, chaleur d'un feu, séchage.
    ``minutes`` peut être une fraction : le temps passé dans un même état (``vecu.solder``), dont
    ``chaud`` et ``eau`` disent les conditions (lues à l'instant sinon)."""
    faits, v = corps(monde, id), valeurs(monde, id)
    facteur = EFFORT if effort else 1
    v["faim"] += CORPS["faim"]["heure"] / 60 * facteur * minutes
    v["repos"] += (-REPOS_MINUTE if repos else CORPS["repos"]["heure"] / 60 * facteur) * minutes
    # Debout dans l'eau, on se trempe et l'on ne sèche pas, même près d'un feu.
    mouille = dans_l_eau(monde, id) if eau is None else eau
    if mouille:
        faits["trempe"] = _minutes(faits["trempe"] + minutes)
        faits["seche"] = 0
    if au_chaud(monde, id) if chaud is None else chaud:
        v["chaleur"] -= FEU_MINUTE * minutes
        if not mouille:
            faits["seche"] = _minutes(faits["seche"] + minutes)
        if faits["trempe"] and faits["seche"] >= SECHAGE:
            faits["trempe"] = 0
    else:
        faits["seche"] = 0
        v["chaleur"] += CORPS["chaleur"]["trempe" if faits["trempe"] else "heure"] / 60 * minutes
    for nom in CORPS:
        v[nom] = round(min(100.0, max(0.0, v[nom])), 3)
    # Le cumul exact en dixièmes évite de perdre des fractions à chaque changement d'activité.
    o = monde.joueur if id == "joueur" else monde.objets[id]
    if repos and o["pv"] < o["pv_max"] and conscient(monde, id):
        from .temps import MINUTE
        soin = round(faits["soin"] * MINUTE) + round(minutes * MINUTE)
        gain, reste = divmod(soin, 60 * MINUTE)
        o["pv"] = min(o["pv_max"], o["pv"] + gain)
        faits["soin"] = reste / MINUTE if o["pv"] < o["pv_max"] else 0


def _minutes(x):
    """Une durée d'état en minutes, entière quand elle l'est (les états déclarés), sinon au millième."""
    x = round(x, 3)
    return int(x) if x == int(x) else x


def pressants(monde, id):
    v = valeurs(monde, id)
    return [nom for nom, regle in CORPS.items() if v.get(nom, 0) >= regle["urgence"]]


def malus(monde, stat, id="joueur"):
    """Ce que les états coûtent aux jets d'une caractéristique, pour tout personnage : chaque
    état qui presse et la touche, et la volonté brisée (en points de jet)."""
    v = monde.joueur.get("besoins", {}) if id == "joueur" else lire(monde, id)["besoins"]
    presse = sum(stat in TOUCHE[nom] for nom, regle in CORPS.items() if v.get(nom, 0) >= regle["urgence"])
    faits = (monde.joueur if id == "joueur" else monde.objets[id]).get("corps", {})
    blessure_ = blessure(monde, id)
    return (-MALUS * presse - MALUS * sum(stat in touche for touche in TOUCHE_BLESSURE[:blessure_])
            - (faits.get("volonte_brisee", 0) if stat == "VOL" else 0))


def briser(monde, id, points):
    """Une contrainte entame la volonté (points de jet de VOL perdus) ; le répit la rend (points
    négatifs). Aucune contrainte ne la brise encore : la donnée et son effet sont prêts."""
    faits = corps(monde, id)
    faits["volonte_brisee"] = max(0, min(BRISURE_MAX, faits.get("volonte_brisee", 0) + points))


def vivre_joueur(monde, dixiemes, effort=False, repos=False, chaud=None, eau=None, lignes=None):
    """Le temps passé par le joueur (en dixièmes de seconde, dans un même état : ``vecu.solder``) ;
    à l'extrême, la faim et le froid l'épuisent (1 PV par heure, jamais en deçà de 1)."""
    from .temps import MINUTE
    if dixiemes <= 0:
        return
    avant = set(pressants(monde, "joueur"))
    vivre(monde, "joueur", dixiemes / MINUTE, effort, repos, chaud, eau)
    v, faits, j = valeurs(monde, "joueur"), corps(monde, "joueur"), monde.joueur
    if v["faim"] >= EXTREME or v["chaleur"] >= EXTREME:
        # La peine se compte en dixièmes de seconde : une heure à l'extrême coûte un PV.
        faits["peine"] += dixiemes
        perte = min(faits["peine"] // (60 * MINUTE), j["pv"] - 1)
        faits["peine"] %= 60 * MINUTE
        if perte > 0:
            j["pv"] -= perte
            if lignes is not None:
                lignes.append("La " + ("faim" if v["faim"] >= EXTREME else "froidure") + " t'affaiblit.")
    else:
        faits["peine"] = 0
    if lignes is not None:
        for nom in sorted(set(pressants(monde, "joueur")) - avant):
            lignes.append({"faim": "Tu as faim.", "chaleur": "Tu as froid.", "repos": "La fatigue te gagne."}[nom])


def etat(monde, id="joueur"):
    """Lecture qualitative pour la fiche et le MJ : ce qui presse, et ce qui est extrême."""
    v = valeurs(monde, id)
    feminin = {"faim": True, "chaleur": False, "repos": True}       # la faim, le froid, la fatigue
    def niveau(nom, regle):
        if v[nom] >= EXTREME:
            return "extrême"
        if v[nom] >= regle["urgence"]:
            return "pressante" if feminin[nom] else "pressant"
        if v[nom] >= regle["urgence"] / 2:
            return "supportable"
        return "légère" if feminin[nom] else "léger"
    resultat = {NOMS[nom]: niveau(nom, regle) for nom, regle in CORPS.items()}
    if blessure(monde, id):
        resultat["blessure"] = "grave" if blessure(monde, id) == 2 else "blessé"
    if not conscient(monde, id):
        resultat["conscience"] = "sans connaissance"
    return resultat


def verifier(monde):
    for id in personnages(monde):
        faits, v = corps(monde, id), valeurs(monde, id)
        o = monde.joueur if id == "joueur" else monde.objets[id]
        assert (type(o.get("pv")) is int and type(o.get("pv_max")) is int
                and 0 <= o["pv"] <= o["pv_max"] and o["pv_max"] > 0), "PV invalides"
        assert type(faits.get("inconscient")) is int and faits["inconscient"] >= 0, "Inconscience invalide"
        assert o["pv"] > 0 or faits["inconscient"] or (id == "joueur" and monde.data.get("fin")), "PV nuls sans inconscience"
        assert isinstance(faits.get("soin"), (int, float)) and 0 <= faits["soin"] < 60, "Soin invalide"
        if faits["inconscient"]:
            from .temps import instant
            assert (type(faits.get("inconscient_depuis")) is int
                    and 0 <= faits["inconscient_depuis"] <= instant(monde)), "Début d'inconscience invalide"
            assert not any(g["auteur"] == id for g in monde.data.get("gestes_en_cours", [])), "Inconscient en action"
            if id != "joueur":
                e = lire(monde, id)
                assert e["libre"] == faits["inconscient"] and e["veille"] is None and e["eveil"] is None, "Réveil incohérent"
        assert set(CORPS) <= set(v) and all(0 <= v[nom] <= 100 for nom in CORPS), "Corps invalide"
        assert (all(type(faits.get(k)) is int and faits[k] >= 0 for k in ("repas", "veille"))
                and all(type(faits.get(k)) in (int, float) and faits[k] >= 0 for k in ("trempe", "seche"))
                and type(faits.get("volonte_brisee", 0)) is int and 0 <= faits.get("volonte_brisee", 0) <= BRISURE_MAX
                and (id != "joueur" or type(faits.get("peine")) is int)), "États du corps invalides"
        from .vecu import verifier as verifier_vecu
        verifier_vecu(faits.get("vecu"))
    for id, d in monde.data.get("defunts", {}).items():
        assert id in monde.objets and monde.objets[id]["type"] == "depouille" and id not in monde.data["esprits"], "Dépouille avec esprit"
        assert "profil" not in monde.objets[id] and "orientation" not in monde.objets[id], "Dépouille vivante"
        assert d["salle"] in monde.data["salles"] and type(d["instant"]) is int, "Défunt invalide"


def pv(monde, id="joueur"):
    return (monde.joueur if id == "joueur" else monde.objets[id])["pv"]


def vivant(monde, id):
    return not monde.data.get("fin") if id == "joueur" else monde.objets.get(id, {}).get("type") == "personnage"


def conscient(monde, id="joueur"):
    o = monde.joueur if id == "joueur" else monde.objets.get(id, {})
    return (not monde.data.get("fin") if id == "joueur" else o.get("type") == "personnage") and not o.get("corps", {}).get("inconscient", 0)


def sans_defense(monde, id):
    return not conscient(monde, id) or bool(corps(monde, id).get("lie"))


def blessure(monde, id="joueur"):
    o = monde.joueur if id == "joueur" else monde.objets[id]
    return 2 if 3 * o.get("pv", 1) <= o.get("pv_max", 1) else 1 if 3 * o.get("pv", 1) <= 2 * o.get("pv_max", 1) else 0


def visible(monde, id):
    return {"blessure": blessure(monde, id), "conscient": conscient(monde, id)}


def perdre(monde, id, points):
    """Une blessure ne tue jamais. Le tirage du réveil appartient au monde sauvegardé."""
    o = monde.joueur if id == "joueur" else monde.objets[id]
    avant = o["pv"]
    o["pv"] = max(0, o["pv"] - points)
    if avant != o["pv"]:
        evenement(monde, "blessure", id, pv_perdus=avant - o["pv"])
    if o["pv"] == 0 and conscient(monde, id):
        endormir(monde, id, hors_combat=True)


def endormir(monde, id, hors_combat=False):
    from .temps import instant, MINUTE
    from .vecu import noter
    t = instant(monde)
    if not conscient(monde, id):
        return
    noter(monde, id, t, None)
    faits = corps(monde, id)
    faits["inconscient_depuis"] = t
    faits["inconscient"] = t + ((30 if hors_combat else 5) + monde.d20()) * MINUTE
    evenement(monde, "inconscience", id)
    monde.data["gestes_en_cours"] = [g for g in monde.data.get("gestes_en_cours", []) if g["auteur"] != id]
    if id != "joueur":
        e = esprit(monde, id)
        e.update(libre=faits["inconscient"], veille=None, eveil=None, intention=None, patience=None)
    noter(monde, id, t, None)


def reveiller(monde, id):
    from .temps import instant
    from .vecu import solder, noter
    t, faits = instant(monde), corps(monde, id)
    if not vivant(monde, id) or not faits["inconscient"]:
        return False
    solder(monde, id, t)
    depuis = faits.pop("inconscient_depuis")
    faits["inconscient"] = 0
    evenement(monde, "reveil", id, depuis=depuis)
    o = monde.joueur if id == "joueur" else monde.objets[id]
    o["pv"] = max(1, o["pv"])
    if id != "joueur":
        from .deliberation import inquieter
        from .esprits import percevoir
        e = esprit(monde, id)
        e.update(libre=t, veille=None, eveil=None)
        memoriser_reveil = {"type": "reveil", "depuis": depuis}
        from .esprits import memoriser
        memoriser(monde, id, memoriser_reveil)
        inquieter(monde, id, "coup")
        percevoir(monde, id)
    noter(monde, id, t, None)
    return True


def ranimer(monde, auteur, id):
    from .temps import instant, MINUTE
    from .passage import au_contact
    from .monde import ErreurMonde
    if not conscient(monde, auteur):
        from .refus import liste
        acceptes = [x for x in personnages(monde) if conscient(monde, x)]
        raise ErreurMonde("Tu ne peux agir sans connaissance.", f"auteur={auteur} : auteur conscient parmi {liste(acceptes)}.")
    if not vivant(monde, id) or conscient(monde, id):
        from .refus import liste
        acceptes = [x for x in personnages(monde) if not conscient(monde, x)]
        raise ErreurMonde("Cette personne n'est pas inconsciente.", f"cible={id} : cible inconsciente parmi {liste(acceptes)}.")
    if instant(monde) - corps(monde, id)["inconscient_depuis"] < MINUTE:
        minimum = corps(monde, id)["inconscient_depuis"] + MINUTE
        raise ErreurMonde("Il est trop tôt pour la ranimer.",
                          f"cible={id}, instant={instant(monde)} : ranimer accepte instant >= {minimum} (dixièmes).")
    if not au_contact(monde, auteur, id):
        raise ErreurMonde("Cette personne est hors de portée.", f"cible={id} : ranimer exige le contact.")
    resultat = reveiller(monde, id)
    if resultat:
        evenement(monde, "ranime", id, auteur=auteur)
    return resultat


def mourir(monde, id, auteur=None, cause="mort"):
    """Transition de mort, sans action de violence : appelée seulement par le moteur ou une épreuve."""
    from .temps import instant
    from .vecu import solder
    from .monde import copie
    if not vivant(monde, id):
        return
    t = instant(monde)
    solder(monde, id, t)
    evenement(monde, "mort", id, auteur=auteur)
    monde.data["gestes_en_cours"] = [g for g in monde.data.get("gestes_en_cours", []) if g["auteur"] != id]
    if id == "joueur":
        monde.data["fin"] = {"cause": cause, "minute": monde.data["minutes"], "instant": t, "auteur": auteur}
        return
    o = monde.objets[id]
    monde.data.setdefault("defunts", {})[id] = {"nom": o["nom"], "genre": o.get("genre", "m"), "profil": copie(o.get("profil")),
        "minute": monde.data["minutes"], "instant": t, "auteur": auteur, "cause": cause, "salle": o["lieu"]}
    o.update(type="depouille", nom="corps de " + o["nom"].split(",")[0], nom_propre=False, genre="m", mobile=True,
             masse_kg=o.get("masse_kg", 70), masse=o.get("masse_kg", 70), aliases=[*o.get("aliases", []), "corps"])
    o.pop("profil", None)
    o.pop("orientation", None)
    o.pop("humeur", None)
    monde.data["esprits"].pop(id, None)
    for bien in monde.objets.values():
        if bien["lieu"] == id:
            bien["proprietaire"] = id
    for e in monde.data["esprits"].values():
        e["engagements"] = [x for x in e["engagements"] if x.get("pour") != id
                            and not any(x["condition"].get(k) == id for k in ("servir", "rendre", "remettre"))]
    # Les fonds et les missions restent traçables ; leurs invariants acceptent un défunt.
    for g in monde.data.get("gestes_en_cours", []):
        for k in ("temoins", "entendus", "se_sait_vu", "exclus"):
            g[k] = [x for x in g[k] if x != id]


def evenement(monde, type, id, **detail):
    """Journal physique persistant, indépendant des souvenirs bornés et réservé aux mesures."""
    from .temps import instant
    monde.data.setdefault("historique_corps", []).append({"type": type, "id": id, "instant": instant(monde), **detail})


def mesures(monde):
    from .temps import instant, MINUTE
    histoire = monde.data.get("historique_corps", [])
    debuts, duree = {}, 0
    for e in histoire:
        if e["type"] == "inconscience":
            debuts[e["id"]] = e["instant"]
        elif e["type"] in ("reveil", "mort") and e["id"] in debuts:
            duree += e["instant"] - debuts.pop(e["id"])
    duree += sum(instant(monde) - t for t in debuts.values())
    return {"minutes_inconscient": duree / MINUTE,
            "ranimes": sum(e["type"] == "ranime" for e in histoire),
            "morts": sum(e["type"] == "mort" for e in histoire),
            "decouvertes": sum(e["type"] == "mort_vue" for e in histoire),
            "pv_perdus": sum(e.get("pv_perdus", 0) for e in histoire),
            **({"coups_portes": sum(e["type"] == "coup" for e in histoire),
                "coups_touches": sum(e["type"] == "coup" and e["touche"] for e in histoire),
                "assommes": sum(e["type"] == "coup" and e["assomme"] for e in histoire),
                "temoins_violence": sum(e["type"] == "violence_vue" for e in histoire),
                "violences_entendues": sum(e["type"] == "violence_entendue" for e in histoire)}
               if any(e["type"] == "coup" for e in histoire) else {})}
