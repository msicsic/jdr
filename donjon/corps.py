"""Le corps, commun à tous les personnages, joueur compris : faim, froid, fatigue.

Rythmes et seuils sont ceux du moteur, les mêmes pour tous. Le scénario ne déclare que des
états (``corps`` du personnage : minutes depuis le dernier repas, minutes de veille, minutes
passées trempé), dont découlent les valeurs de départ ; le profil d'un PNJ ne garde que son
caractère. Les valeurs vivent dans ``esprit["besoins"]`` pour un PNJ, dans
``joueur["besoins"]`` pour le joueur, sous les noms ``faim``, ``chaleur`` (le froid) et
``repos`` (la fatigue).
"""
from .esprits import esprit, pnjs

# Par heure : faim et fatigue montent avec le temps, plus vite à l'effort ; le froid monte loin
# d'un feu, plus vite trempé. Un besoin presse à partir de son seuil.
CORPS = {"faim": {"heure": 6, "urgence": 70},
         "repos": {"heure": 3, "urgence": 80},
         "chaleur": {"heure": 2, "trempe": 10, "urgence": 70}}
NOMS = {"faim": "faim", "chaleur": "froid", "repos": "fatigue"}
EFFORT = 1.5           # l'effort fait monter faim et fatigue moitié plus vite
FEU_MINUTE = 3         # froid perdu par minute dans la salle d'un foyer allumé
SECHAGE = 30           # minutes au chaud pour sécher
REPOS_MINUTE = 2       # fatigue perdue par minute de repos
SATIETE = 50           # un repas
EXTREME = 95           # au-delà, la faim et le froid épuisent le joueur
MALUS = 2              # par état qui presse, aux jets de FOR et de DEX
FAITS = {"repas": 180, "veille": 480, "trempe": 0}    # joueur ou PNJ sans état déclaré
CALMES = ("attendre", "observer", "examiner", "lire", "parler", "toucher", "copier")  # sans effort


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
    return ["joueur", *(id for id in pnjs(monde) if monde.objets[id].get("profil"))]


def installer(monde):
    """Valeurs de départ ; anciennes parties : les besoins du corps quittent le profil."""
    for id in personnages(monde):
        faits, v = corps(monde, id), valeurs(monde, id)
        if id != "joueur":
            for nom in CORPS:
                ancien = monde.objets[id]["profil"]["besoins"].pop(nom, None)
                if ancien is not None and nom not in v:
                    v[nom] = float(ancien["depart"])
        for nom, valeur in depart(faits).items():
            v.setdefault(nom, round(valeur, 3))
        faits.setdefault("seche", 0)
        if id == "joueur":
            faits.setdefault("peine", 0)


def au_chaud(monde, id):
    """Dans la salle d'un foyer allumé."""
    from .perception import allumee
    salle = monde.joueur["salle"] if id == "joueur" else monde.objets[id]["lieu"]
    return any(o.get("foyer") and allumee(o) and monde.present_physique(o["id"], salle=salle)
               for o in monde.objets.values())


def vivre(monde, id, minutes=1, effort=False, repos=False):
    """Le corps change avec le temps : faim, fatigue, froid ; repos, chaleur d'un feu, séchage."""
    faits, v = corps(monde, id), valeurs(monde, id)
    facteur = EFFORT if effort else 1
    v["faim"] += CORPS["faim"]["heure"] / 60 * facteur * minutes
    v["repos"] += (-REPOS_MINUTE if repos else CORPS["repos"]["heure"] / 60 * facteur) * minutes
    if au_chaud(monde, id):
        v["chaleur"] -= FEU_MINUTE * minutes
        faits["seche"] += minutes
        if faits["trempe"] and faits["seche"] >= SECHAGE:
            faits["trempe"] = 0
    else:
        faits["seche"] = 0
        v["chaleur"] += CORPS["chaleur"]["trempe" if faits["trempe"] else "heure"] / 60 * minutes
    for nom in CORPS:
        v[nom] = round(min(100.0, max(0.0, v[nom])), 3)


def pressants(monde, id):
    v = valeurs(monde, id)
    return [nom for nom, regle in CORPS.items() if v.get(nom, 0) >= regle["urgence"]]


def malus(monde, stat):
    """Un état qui presse coûte aux gestes physiques du joueur."""
    return -MALUS * len(pressants(monde, "joueur")) if stat in ("FOR", "DEX") else 0


def vivre_joueur(monde, minutes, effort=False, repos=False, lignes=None):
    """Le temps passé par le joueur ; à l'extrême, la faim et le froid l'épuisent (1 PV par heure,
    jamais en deçà de 1)."""
    if minutes <= 0:
        return
    avant = set(pressants(monde, "joueur"))
    vivre(monde, "joueur", minutes, effort, repos)
    v, faits, j = valeurs(monde, "joueur"), corps(monde, "joueur"), monde.joueur
    if v["faim"] >= EXTREME or v["chaleur"] >= EXTREME:
        faits["peine"] += minutes
        perte = min(faits["peine"] // 60, j["pv"] - 1)
        faits["peine"] %= 60
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
    return {NOMS[nom]: niveau(nom, regle) for nom, regle in CORPS.items()}


def verifier(monde):
    for id in personnages(monde):
        faits, v = corps(monde, id), valeurs(monde, id)
        assert set(CORPS) <= set(v) and all(0 <= v[nom] <= 100 for nom in CORPS), "Corps invalide"
        assert (all(type(faits.get(k)) is int and faits[k] >= 0 for k in (*FAITS, "seche"))
                and (id != "joueur" or type(faits.get("peine")) is int)), "États du corps invalides"
