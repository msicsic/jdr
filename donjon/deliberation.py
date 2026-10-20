"""Besoins, pulsions et délibération des PNJ ; planificateur borné sur leurs croyances.

Le profil d'auteur (``objet["profil"]``) déclare caractéristiques, traits, valeurs
(``caractere``), capacités, besoins et pulsions. Le moteur fait évoluer les besoins minute par minute ;
une pulsion qui cesse d'être satisfaite aux yeux du PNJ relance son besoin. Chaque minute,
le PNJ retient le but le plus urgent pour lequel il trouve un plan, cherché sur ce qu'il
croit, jamais sur la vérité du monde. Les étapes sont ensuite revalidées sur l'état réel
par ``pnj.py``. Tout est déterministe ; Luna n'intervient pas.
"""
from .caractere import STATS, interdit, verifier_valeurs
from .corps import CORPS, SATIETE  # noqa: F401  (SATIETE : un repas, pour les gestes des PNJ)
from .esprits import RECENT, esprit, lire, memoriser
from .spatial import porte_par

BESOINS = ("devoir", "biens", "securite", "faim", "repos", "chaleur")
CAPACITES = ("crochetage",)
OPERATIONS = ("aller", "prendre", "poser", "ouvrir", "fermer", "deverrouiller", "verrouiller",
              "crocheter", "manger", "inspecter", "reposer", "chauffer", "abriter", "alimenter", "allumer", "eteindre",
              "servir",
              "dire", "demander", "confier", "remettre")
PROGRESSIFS = ("aller", "reposer", "chauffer", "abriter")
EFFORTS = ("aller", "prendre", "poser", "crocheter", "alimenter", "servir", "inspecter")  # gestes qui creusent  # gestes qui durent : une minute sans les finir n'est pas un échec
SOCIALES = ("dire", "demander", "confier", "remettre")
PROFONDEUR = 4
PATIENCE = 30          # minutes d'attente d'une occasion avant de renoncer
REPIT = 60             # minutes avant de reprendre un but abandonné
ATTEINTE = 30          # une pulsion qui cesse d'être satisfaite relance son besoin
VOL = 60               # un vol vu par sa victime
REPOS_FIN = 20         # reposé : il se relève
CHALEUR_FIN = 20       # réchauffé : il s'écarte du feu
SECURITE_FIN = 30      # rassuré : il quitte l'abri
# Ce qui inquiète (+) ou rassure (−) la sécurité, valeurs par défaut que chaque profil nuance
# (donnée ``securite``) : par minute pour ce qui dure, d'un coup pour un événement.
SECURITE = {"noir": 0.5, "mefiance": 0.3, "bruit": 15, "illicite": 20,      # inquiète
            "eau": 2, "menace": 1, "crue": 10,     # par minute : 50 cm d'eau, l'eau attendue bientôt ;
                                                   # d'un coup : la voir gagner un lieu
            "lumiere": 0.2, "compagnie": 0.5, "ronde": 20}                 # rassure
REDEMANDE = 120        # minutes avant de redemander la même chose à qui vient de refuser
ATTENTE_PART = 60      # minutes pendant lesquelles on attend la part promise avant de redemander
REVOIR_FEU = 30        # un feu vu vif doit être revu avant que ce qui lui restait ne s'épuise
DESESPOIR = 95         # au-delà, le besoin l'emporte sur la crainte d'être vu ; sans abri, on appelle
APPEL_REPIT = 10       # minutes entre deux appels à l'aide
INERTIE = 5            # points au-delà du seuil avant qu'un besoin interrompe un plan en cours


def profil(monde, id):
    return monde.objets[id].get("profil")


def seuils(monde, id):
    """Seuil d'urgence de chaque besoin : ceux du corps, communs ; ceux de l'esprit, du profil."""
    p = profil(monde, id)
    return {**{nom: regle["urgence"] for nom, regle in CORPS.items()},
            **{nom: b["urgence"] for nom, b in (p or {}).get("besoins", {}).items()}}


def reserve(monde, id):
    """Parts qu'un personnage garde pour lui de chaque ressource comptée qu'il possède."""
    return (profil(monde, id) or {}).get("reserve", 1)


def besoin_de_part(o):
    """Le besoin qu'une part de cette ressource apaise : la faim des vivres, le froid du combustible."""
    if o["type"] == "nourriture":
        return "faim"
    return "chaleur" if "combustible" in o.get("usages", []) else None


def parts(o):
    return o.get("portions", o.get("charges", 0))


def verifier_profil(monde, id, p):
    assert (isinstance(p, dict) and {"caracteristiques", "traits", "valeurs", "capacites", "besoins", "pulsions"}
            <= set(p) <= {"caracteristiques", "traits", "valeurs", "capacites", "besoins", "pulsions",
                          "reserve", "securite", "protege"}), "Profil de PNJ mal formé"
    assert (isinstance(p.get("protege", []), list) and all(
        x in monde.objets and monde.objets[x]["type"] == "personnage" and x != id
        for x in p.get("protege", []))), "Protégés de PNJ invalides"
    assert type(p.get("reserve", 1)) is int and 0 <= p.get("reserve", 1) <= 10, "Réserve de PNJ invalide"
    assert (isinstance(p.get("securite", {}), dict) and set(p.get("securite", {})) <= set(SECURITE)
            and all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in p.get("securite", {}).values())),         "Sécurité de PNJ invalide"
    assert set(p["caracteristiques"]) == set(STATS) and all(
        type(v) is int and 1 <= v <= 20 for v in p["caracteristiques"].values()), "Caractéristiques de PNJ invalides"
    assert isinstance(p["traits"], str) and len(p["traits"]) <= 600, "Traits de PNJ invalides"
    verifier_valeurs(p["valeurs"])
    assert set(p["capacites"]) <= set(CAPACITES), "Capacité inconnue"
    for nom, b in p["besoins"].items():
        # Faim, froid et fatigue relèvent du corps, commun à tous : le profil ne les règle pas.
        assert (nom in BESOINS and nom not in CORPS and set(b) == {"depart", "derive_heure", "urgence"}
                and all(isinstance(b[k], (int, float)) for k in b)
                and 0 <= b["depart"] <= 100 and 0 < b["urgence"] <= 100), "Besoin de PNJ invalide"
    for pulsion in p["pulsions"]:
        assert (set(pulsion) <= {"besoin", "condition", "delegue_a"} and pulsion.get("besoin") in seuils(monde, id)
                and condition_valide(monde, pulsion.get("condition"))
                and pulsion.get("delegue_a", "joueur") == "joueur"), "Pulsion de PNJ invalide"


def condition_valide(monde, c):
    """Vocabulaire commun des buts : un objet en un lieu, un objet verrouillé, une ronde,
    une part de nourriture servie à quelqu'un, un feu entretenu."""
    return isinstance(c, dict) and (
        (set(c) == {"objet", "lieu"} and c["objet"] in monde.objets and c["lieu"] in monde.data["salles"])
        or (set(c) == {"objet", "servir"} and c["objet"] in monde.objets
            and monde.objets[c["objet"]]["type"] == "nourriture"
            and (c["servir"] == "joueur" or c["servir"] in monde.objets
                 and monde.objets[c["servir"]]["type"] == "personnage"))
        or (set(c) == {"objet", "verrouillee"} and c["objet"] in monde.objets and c["verrouillee"] is True)
        or (set(c) == {"objet", "allume"} and c["objet"] in monde.objets and "allume" in monde.objets[c["objet"]]
            and c["allume"] is True)
        or (set(c) == {"lieu", "periode"} and c["lieu"] in monde.data["salles"]
            and type(c["periode"]) is int and c["periode"] > 0))


def installer(monde, id):
    """Valeurs initiales des besoins et état des pulsions, à la première rencontre du profil."""
    p, e = profil(monde, id), esprit(monde, id)
    if not p:
        return
    for nom, b in p["besoins"].items():
        e["besoins"].setdefault(nom, float(b["depart"]))
    if len(e["pulsions"]) != len(p["pulsions"]):
        e["pulsions"] = [satisfaite(monde, id, x["condition"]) for x in p["pulsions"]]


def relancer(monde, id, besoin, montant):
    """Un événement (vol, atteinte à une pulsion) accroît un besoin déclaré ; un apaisement le réduit."""
    e = esprit(monde, id)
    if besoin in e["besoins"]:
        e["besoins"][besoin] = max(0.0, min(100.0, e["besoins"][besoin] + montant))


# --- Croyances utiles au plan -------------------------------------------------------------

def _lieu_cru(monde, id, sujet):
    c = lire(monde, id)["croyances"].get(sujet, {}).get("lieu")
    if c:
        return c["valeur"]
    o = monde.objets.get(sujet)
    # Les objets fixes font partie des lieux : on sait où ils sont sans les avoir revus.
    return o["lieu"] if o and not o.get("mobile") else None


def salle_crue(monde, id, sujet, profondeur=0):
    if sujet in monde.objets and porte_par(monde, sujet, id):
        return monde.objets[id]["lieu"]
    lieu = _lieu_cru(monde, id, sujet)
    if lieu is None or profondeur > PROFONDEUR:
        return None
    if lieu in monde.data["salles"]:
        return lieu
    if lieu == "joueur":
        return _lieu_cru(monde, id, "joueur")
    return salle_crue(monde, id, lieu, profondeur + 1)


def _cru(monde, id, sujet, attribut):
    c = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    return None if c is None else c["valeur"]


def _ouvert_cru(monde, id, sujet):
    etat = _cru(monde, id, sujet, "etat")
    return bool(etat and etat.get("ouverte"))


def _connus(monde, id):
    """Objets dont le PNJ a une croyance ou qu'il porte, dans un ordre stable."""
    croyances = lire(monde, id)["croyances"]
    return sorted(s for s in monde.objets if s in croyances or porte_par(monde, s, id))


def periodique(condition):
    """Une ronde : avoir inspecté un lieu depuis moins de ``periode`` minutes."""
    return "periode" in condition


def s_use(condition):
    """Une ronde expire, un feu baisse : d'eux-mêmes, sans que personne y ait porté atteinte."""
    return periodique(condition) or "allume" in condition


def _disponible_cru(monde, id, objet):
    """Une nourriture ou une réserve qu'il a vue épuisée ne lui sert plus."""
    etat = _cru(monde, id, objet, "etat")
    return not etat or etat.get("disponible", True)


def refuse_recemment(monde, id, autre, operation, objet=None):
    """Le dernier refus de cet échange, s'il date de moins de ``REDEMANDE`` minutes."""
    return next((s for s in reversed(lire(monde, id)["memoire"])
                 if s["type"] == "refus" and s["de"] == autre and s["operation"] == operation
                 and s.get("objet", objet) == objet and monde.data["minutes"] - s["minute"] < REDEMANDE), None)


def promesse_en_cours(monde, id, objet):
    """Une part promise et pas encore servie, dans le délai où il l'attend."""
    for s in reversed(lire(monde, id)["memoire"]):
        if s["type"] == "nourri" and s.get("objet") == objet:
            return None
        if s["type"] == "promis" and s["objet"] == objet:
            return s["de"] if monde.data["minutes"] - s["minute"] < ATTENTE_PART else None
    return None


def satisfaite(monde, id, condition):
    if "servir" in condition:
        return False  # Une part servie solde l'engagement au moment du geste.
    if periodique(condition):
        vu = lire(monde, id)["visites"].get(condition["lieu"])
        return vu is not None and monde.data["minutes"] - vu < condition["periode"]
    if "allume" in condition:
        # Un feu qui baisse n'est plus entretenu ; un feu vu vif il y a longtemps n'est plus sûr :
        # il faut aller le voir, et le recharger tant qu'il reste le temps d'aller chercher du bois.
        c = lire(monde, id)["croyances"].get(condition["objet"], {}).get("etat")
        return bool(c and c["valeur"].get("allume") and not c["valeur"].get("faible")
                    and monde.data["minutes"] - c["minute"] < REVOIR_FEU)
    if "lieu" in condition:
        # Le tenir soi-même ne suffit pas : l'objet doit être déposé (ou tenu par un autre) sur place.
        return (not porte_par(monde, condition["objet"], id)
                and salle_crue(monde, id, condition["objet"]) == condition["lieu"])
    return _cru(monde, id, condition["objet"], "verrouillee") is True and not _ouvert_cru(monde, id, condition["objet"])


def illicite(monde, id, objet):
    from .vol import proprietaire
    return proprietaire(monde, monde.objets[objet]) not in (None, id)


def autorise(monde, id, objet):
    """Le bien d'autrui est interdit à qui a l'honnêteté à son comble ; pour les autres, c'est
    une faute dont le planificateur pèse le prix (``caractere.prix_faute``)."""
    return not (illicite(monde, id, objet) and interdit(monde, id, "honnetete"))


# --- Plans ---------------------------------------------------------------------------------
# Les plans viennent de la recherche (``planification``) ; ce module choisit le but.


def _plan_pulsion(monde, id, condition):
    """Rétablir une pulsion ou tenir une parole donnée : la recherche (``planification``)."""
    from .planification import planifier_pulsion
    return planifier_pulsion(monde, id, condition)


# --- Sécurité ----------------------------------------------------------------------------

def taux(monde, id, cause):
    return (profil(monde, id) or {}).get("securite", {}).get(cause, SECURITE[cause])


def autour(monde, id):
    """Ce qui, dans sa salle, l'inquiète ou le rassure : la lumière sur sa case, ceux qu'il y voit
    ou y entend tout près et croit fiables, ceux qu'il y voit ou entend et ne croit pas fiables."""
    from .esprits import pnjs
    from .perception import eclairage
    o = monde.objets[id]
    niveau = eclairage(monde, o["lieu"], o.get("position") if monde.data.get("mode_cases") else None)["niveau"]
    presents = [x for x in [*pnjs(monde), "joueur"] if x != id
                and (monde.joueur["salle"] if x == "joueur" else monde.objets[x]["lieu"]) == o["lieu"]]
    if monde.data.get("mode_cases"):
        from .pnj import de_pres
        from .spatial import acteurs_vus
        vus = acteurs_vus(monde, id, presents)
        # Ceux qu'il voit, et ceux qu'il entend tout près, même dans son dos.
        autres = [x for x in presents if x in vus or de_pres(monde, id, x)]
    else:
        autres = presents if niveau else []
    return {"lumiere": niveau > 0,
            "fiables": sorted(x for x in autres if _cru(monde, id, x, "fiable") is True),
            "mefiants": sorted(x for x in autres if _cru(monde, id, x, "fiable") is False)}


def ressentir(monde, id):
    """Une minute de sécurité perçue : le noir, la méfiance et l'eau où l'on se tient inquiètent,
    la lumière et la compagnie de qui l'on croit fiable rassurent."""
    if "securite" not in esprit(monde, id)["besoins"] or monde.objets[id]["lieu"] not in monde.data["salles"]:
        return
    a = autour(monde, id)
    ecart = (-taux(monde, id, "lumiere") if a["lumiere"] else taux(monde, id, "noir"))
    ecart += taux(monde, id, "mefiance") if a["mefiants"] else 0
    ecart -= taux(monde, id, "compagnie") if a["fiables"] else 0
    # L'eau où il se tient, d'autant plus qu'elle est haute ; sinon l'eau qu'il y attend bientôt.
    from .eau import NOYEE_CM, menacee, profondeur
    ici = monde.objets[id]["lieu"]
    p = profondeur(monde, ici)
    if p:
        ecart += 2 * taux(monde, id, "eau") * min(p, NOYEE_CM) / NOYEE_CM
    elif menacee(monde, id, ici):
        ecart += taux(monde, id, "menace")
    relancer(monde, id, "securite", ecart)


def inquieter(monde, id, cause, signe=1):
    """Un événement inquiète (un bruit sans cause vue, un geste illicite) ou rassure (une ronde)."""
    if monde.objets.get(id, {}).get("profil"):
        relancer(monde, id, "securite", signe * taux(monde, id, cause))


def protecteurs(monde, protege):
    """Ceux dont le profil déclare protéger ce personnage."""
    return [x for x, o in monde.objets.items() if protege in (o.get("profil") or {}).get("protege", [])]


def appeler_a_l_aide(monde, id, minute):
    """À bout d'inquiétude et sans abri, il appelle : un son fort, que d'autres entendent."""
    e = esprit(monde, id)
    if (e["besoins"].get("securite", 0) < DESESPOIR
            or e["intention"] and e["intention"]["but"]["type"] == "abri"
            or any(s["type"] == "appel" and minute - s["minute"] < APPEL_REPIT for s in e["memoire"])):
        return
    memoriser(monde, id, {"type": "appel"})
    from .ecoute import appel
    appel(monde, id)


def de_garde(monde, id, salle):
    """Le lieu relève de son devoir de garde : il y fait une ronde, y garde un bien ou y entretient
    quelque chose (une pulsion du devoir ou des biens), ou un protégé s'y trouve, à ce qu'il croit."""
    p = profil(monde, id) or {}
    for x in p.get("pulsions", []):
        c = x["condition"]
        if x["besoin"] in ("devoir", "biens") and (
                c.get("lieu") == salle or "objet" in c and salle_crue(monde, id, c["objet"]) == salle):
            return True
    return any(salle_crue(monde, id, x) == salle for x in p.get("protege", []))


def bruit_a_voir(monde, id):
    """(lieu, motif) du plus récent bruit inconnu, venu d'un autre lieu, qu'il ira voir : son devoir
    de garde l'y envoie ; un bruit inhabituel (un fracas, un appel), son courage aussi, s'il en a
    plus que la moyenne. None s'il n'ira pas (``ouie``)."""
    from .caractere import NEUTRE, valeur
    from .ouie import HABITUDE, HABITUELS, resolu
    courageux = valeur(monde, id, "courage") > NEUTRE
    e = lire(monde, id)
    ici, minute = monde.objets[id]["lieu"], monde.data["minutes"]
    # Celui qu'il est en train d'aller voir passe d'abord : il ne court pas d'un bruit à l'autre.
    en_cours = e["intention"]["but"].get("lieu") if e["intention"] and e["intention"]["but"]["type"] == "voir" else None
    a_voir = []
    for s in reversed(e["memoire"]):
        if s["type"] != "bruit" or s["salle"] == ici or resolu(monde, id, s):
            continue
        inhabituel = s["nature"] not in HABITUELS
        if not inhabituel and minute - e["visites"].get(s["salle"], -HABITUDE - 1) <= HABITUDE:
            continue  # Il en revient : un pas de plus ne l'y renvoie pas.
        if de_garde(monde, id, s["salle"]):
            a_voir.append((s["salle"], "devoir"))
        elif courageux and inhabituel:
            a_voir.append((s["salle"], "securite"))
    return next((x for x in a_voir if x[0] == en_cours), a_voir[0] if a_voir else None)


def _plan_prevenir(monde, id):
    """Un geste illicite vu contre un protégé : aller le lui dire."""
    e = esprit(monde, id)
    for s in reversed(e["memoire"]):
        if s["type"] != "a_prevenir":
            continue
        dit = any(x["type"] == "dit" and x["a"] == s["victime"] and x["sujet"] == s["auteur"]
                  and x["minute"] >= s["minute"] for x in e["memoire"])
        if dit or s["victime"] not in monde.objets:
            continue
        from .planification import _etape, rejoindre
        chemin = rejoindre(monde, id, s["victime"])
        if chemin is None:
            continue
        etapes, trouve = chemin
        if trouve:
            etapes.append(_etape("dire", s["victime"],
                                 contenu={"sujet": s["auteur"], "attribut": "fiable", "valeur": False}))
        return {"type": "prevenir", "qui": s["victime"]}, etapes
    return None


def _eclairee_crue(monde, id, salle):
    """Éclairée quand il y était, ou par une source qu'il y croit allumée."""
    vue = _cru(monde, id, salle, "etat")
    if vue is not None:
        return vue.get("eclairee", False)
    if monde.data["salles"][salle].get("lumiere_naturelle"):
        return True
    return any("allume" in monde.objets[k] and (_cru(monde, id, k, "etat") or {}).get("allume")
               and salle_crue(monde, id, k) == salle for k in _connus(monde, id))


def _plan_abri(monde, id):
    """Se mettre à l'abri : rejoindre un lieu qu'il croit éclairé où se tient quelqu'un qu'il croit
    fiable, et y rester ; là où il est d'abord, s'il l'est déjà. Un lieu où il croit l'eau, ou l'y
    attend bientôt (``eau.menacee``), n'est pas un abri. Tant qu'il voit l'eau monter, l'abri est
    le plus haut lieu éclairé qu'elle ne menace pas, avec ou sans compagnie : elle monte par le bas."""
    from .eau import altitude, menacee, monte
    from .esprits import pnjs
    ici = monde.objets[id]["lieu"]
    if menacee(monde, id, ici) or monte(monde, id):
        salles = sorted((s for s in monde.data["salles"] if not menacee(monde, id, s)
                         and _eclairee_crue(monde, id, s)), key=lambda s: (-altitude(monde, s), s != ici, s))
    else:
        salles = []
        for x in [*pnjs(monde), "joueur"]:
            if x == id or _cru(monde, id, x, "fiable") is not True:
                continue
            salle = salle_crue(monde, id, x)
            if (salle in monde.data["salles"] and salle not in salles and _eclairee_crue(monde, id, salle)
                    and not menacee(monde, id, salle)):
                salles.append(salle)
        salles.sort(key=lambda s: s != ici)
    from .planification import _etape, aller
    for salle in salles:
        etapes = aller(monde, id, salle)
        if etapes is None:
            continue
        return {"type": "abri", "lieu": salle}, etapes + [_etape("abriter", lieu=salle)]
    return None


def _plan_reposer(monde, id):
    """Se reposer là où l'on est."""
    from .planification import _etape
    return {"type": "repos"}, [_etape("reposer")]


def ouvert_par_soi(monde, id, objet, depuis):
    """A-t-il lui-même ouvert ou déverrouillé cet objet dans les ``depuis`` dernières minutes ?"""
    return any(s["type"] == "ouvert_par_soi" and s["objet"] == objet and monde.data["minutes"] - s["minute"] <= depuis
               for s in lire(monde, id)["memoire"])


def garde_sous_cle(monde, id, objet):
    p = profil(monde, id)
    return bool(p) and any(x["condition"] == {"objet": objet, "verrouillee": True} for x in p["pulsions"])


def de_son_fait(monde, id, condition):
    """On ne s'alarme pas de ce qu'on vient de défaire soi-même : sa clé, sa main."""
    if condition.get("verrouillee"):
        return ouvert_par_soi(monde, id, condition["objet"], 2)
    return "lieu" in condition and "objet" in condition and porte_par(monde, condition["objet"], id)


def _plan_garder(monde, id, condition):
    from .planification import aller
    salle = salle_crue(monde, id, condition["objet"])
    etapes = None if salle is None else aller(monde, id, salle)
    return None if etapes is None else ({"type": "garder", "lieu": salle}, etapes)


def _delegue(monde, id, pulsion):
    """Une pulsion confiée au joueur attend tant que le PNJ le croit fiable."""
    return pulsion.get("delegue_a") and _cru(monde, id, pulsion["delegue_a"], "fiable") is not False


def urgents(monde, id):
    """Besoins au-delà de leur seuil, du plus pressant au moins pressant."""
    s, e = seuils(monde, id), esprit(monde, id)
    return sorted((b for b in s if e["besoins"].get(b, 0) >= s[b]),
                  key=lambda b: (s[b] - e["besoins"][b], BESOINS.index(b)))


def confie_a_autrui(monde, id, objet):
    """Ce qu'il a confié à quelqu'un qu'il croit fiable, il ne le fait pas à sa place."""
    p = profil(monde, id)
    return bool(p) and any(x["condition"].get("objet") == objet and _delegue(monde, id, x) for x in p["pulsions"])


def _plan_faim(monde, id):
    """Apaiser la faim : le plan le moins coûteux trouvé par la recherche (``planification``)."""
    from .planification import planifier
    return planifier(monde, id, "faim")


def _plan_froid(monde, id):
    """Se réchauffer : le plan le moins coûteux trouvé par la recherche (``planification``)."""
    from .planification import planifier
    return planifier(monde, id, "chaleur")


# Besoins qu'un geste qui dure apaise : la méthode, et le seuil où il s'achève.
PROGRES = {"repos": (_plan_reposer, REPOS_FIN), "chaleur": (_plan_froid, CHALEUR_FIN),
           "securite": (_plan_abri, SECURITE_FIN)}
GESTE_PROGRES = {"repos": "reposer", "chaleur": "chauffer", "securite": "abriter"}


def retabli_par_son_plan(monde, id, condition):
    """Ce qu'il défait lui-même pour un plan qui le rétablit n'est pas à réparer d'abord, tant
    que le motif de ce plan presse encore (un besoin urgent, une parole à tenir)."""
    e = lire(monde, id)
    i = e["intention"]
    if not (condition.get("verrouillee") and i and any(
            x["operation"] == "verrouiller" and x["cible"] == condition["objet"] for x in i["plan"])):
        return False
    but = {k: v for k, v in i["but"].items() if k != "type"}
    return i["motif"] in urgents(monde, id) or i["motif"] == "engagement" and any(
        x["condition"] == but for x in e["engagements"])


def candidats(monde, id):
    """Buts envisageables, du besoin le plus pressant au moins pressant ; la routine (rondes,
    surveillance) passe après ce qui presse vraiment et après une tâche acceptée.

    Un besoin qui vient à peine de franchir son seuil laisse finir le plan en cours d'un autre
    motif : on achève le geste entamé avant de céder à la fatigue ou à la faim naissantes."""
    p, e = profil(monde, id), esprit(monde, id)
    buts = []
    en_cours = e["intention"]["motif"] if e["intention"] and e["intention"]["plan"] else None
    pressants = urgents(monde, id)
    for besoin in pressants:
        if (en_cours and besoin != en_cours
                and e["besoins"][besoin] < seuils(monde, id)[besoin] + INERTIE):
            continue
        if besoin == "faim":
            buts.append((besoin, _plan_faim, False))
            continue
        if besoin in PROGRES:
            # Le geste qui apaise d'abord ; les pulsions du même besoin (les rondes) restent des recours.
            buts.append((besoin, PROGRES[besoin][0], False))
        pulsions = [x for x in p["pulsions"] if x["besoin"] == besoin]
        for x in pulsions:
            if (not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)
                    and not retabli_par_son_plan(monde, id, x["condition"])):
                # Une ronde peut attendre qu'il ait tenu parole ; un feu à voir ou à recharger, non.
                buts.append((besoin, lambda m, i, c=x["condition"]: _plan_pulsion(m, i, c),
                             periodique(x["condition"])))
        if besoin == "biens":
            for x in pulsions:
                if periodique(x["condition"]):
                    continue
                buts.append((besoin, lambda m, i, c=x["condition"]: _plan_garder(m, i, c), True))
    buts += [("engagement", lambda m, i, c=x["condition"]: _plan_pulsion(m, i, c), False) for x in e["engagements"]]
    # Un protégé atteint sous ses yeux : il va le prévenir, comme une parole due.
    if any(s["type"] == "a_prevenir" for s in e["memoire"]):
        buts.append(("devoir", _plan_prevenir, False))
    # Un bruit inconnu qu'il doit, ou ose, aller voir : après ce qui presse, avant la routine.
    a_voir = bruit_a_voir(monde, id)
    if a_voir:
        from .planification import voir
        buts.append((a_voir[1], lambda m, i, s=a_voir[0]: voir(m, i, s), False))
    # Ce qu'il garde sous clé et a lui-même ouvert, il le referme sans attendre l'urgence.
    for x in p["pulsions"]:
        c = x["condition"]
        if (c.get("verrouillee") and ouvert_par_soi(monde, id, c["objet"], RECENT) and not satisfaite(monde, id, c)
                and not retabli_par_son_plan(monde, id, c)):
            buts.append((x["besoin"], lambda m, i, c=c: _plan_pulsion(m, i, c), False))
    # Assis pour se reposer, ou près du feu, il ne s'en va qu'une fois remis, ou pour plus pressant.
    # Seulement si son plan comporte bien ce geste : une ronde a le même motif que l'abri.
    for besoin, (methode, fin) in PROGRES.items():
        if (e["intention"] and e["intention"]["motif"] == besoin and e["besoins"].get(besoin, 0) > fin
                and any(x["operation"] == GESTE_PROGRES[besoin] for x in e["intention"]["plan"])):
            buts.append((besoin, methode, False))
    # La routine : ses rondes, même quand le besoin qu'elles servent ne presse pas.
    for x in p["pulsions"]:
        if (periodique(x["condition"]) and x["besoin"] not in pressants
                and not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)):
            buts.append((x["besoin"], lambda m, i, c=x["condition"]: _plan_pulsion(m, i, c), True))
    # Ce qui presse vraiment, la parole donnée et ce qu'on finit, puis la routine, par urgence.
    for besoin, methode, _ in sorted(buts, key=lambda x: x[2]):
        yield besoin, methode


def deliberer(monde, id, minute):
    """Une minute de vie intérieure : besoins, pulsions, choix du but et du plan."""
    p = profil(monde, id)
    e = esprit(monde, id)
    if not p:
        return
    installer(monde, id)
    for nom, b in p["besoins"].items():
        e["besoins"][nom] = round(min(100.0, max(0.0, e["besoins"][nom] + b["derive_heure"] / 60)), 3)
    # Le corps suit le geste en cours : l'effort creuse, le repos délasse.
    from .corps import vivre
    geste = e["intention"]["plan"][0]["operation"] if e["intention"] and e["intention"]["plan"] else None
    vivre(monde, id, 1, effort=geste in EFFORTS, repos=geste == "reposer")
    ressentir(monde, id)
    for i, x in enumerate(p["pulsions"]):
        etat = satisfaite(monde, id, x["condition"])
        # Une ronde expire, un feu baisse d'eux-mêmes : ce n'est pas une atteinte.
        if (e["pulsions"][i] and not etat and not s_use(x["condition"])
                and not de_son_fait(monde, id, x["condition"])):
            # Ses biens forcés ou déplacés : un vol découvert, même sans coupable.
            relancer(monde, id, x["besoin"], VOL if x["besoin"] == "biens" else ATTEINTE)
            memoriser(monde, id, {"type": "atteinte", "condition": dict(x["condition"])})
        e["pulsions"][i] = etat
    from .echanges import engagements_echus
    from . import stratege
    engagements_echus(monde, id)
    intention = e["intention"]
    if intention and intention["motif"] == "alerte":
        from .pnj import chemin
        if chemin(monde, id, monde.objets[id]["lieu"], intention["but"]["lieu"]) is not None:
            return  # Le réflexe déclaré garde la priorité jusqu'à son terme.
        e["intention"] = None  # Plus aucun passage qu'il croie ouvert : il ne peut accourir.
    if intention and intention["but"]["type"] == "strategie" and intention["plan"]:
        return  # Une stratégie choisie va à son terme, ou tombe au premier geste manqué.
    for besoin, methode in candidats(monde, id):
        if e["renoncements"].get(besoin, -REPIT) + REPIT > minute:
            continue
        resultat = methode(monde, id)
        if not resultat:
            continue
        but, etapes = resultat
        if stratege.plan_illicite(monde, id, besoin, but, etapes, minute):
            return
        intention = e["intention"]
        meme = bool(intention) and intention["but"] == but
        e["intention"] = {"but": but, "motif": besoin, "plan": etapes,
                          "depuis": intention["depuis"] if meme else minute,
                          "attente": intention["attente"] if meme else 0}
        stratege.occupe(monde, id)
        return
    e["intention"] = None
    stratege.desoeuvre(monde, id, minute, urgents(monde, id))


def menager_flamme(monde, id, minute):
    """Une flamme portable qu'il a allumée ou employée pour allumer, et que son plan n'emploie
    plus, se consume pour rien : il l'éteint d'abord, et la garde pour plus tard. Une lanterne
    portée pour y voir n'est pas concernée."""
    from .perception import allumee
    e = esprit(monde, id)
    plan = e["intention"]["plan"] if e["intention"] else []
    vises = {x["cible"] for x in plan} | {x["outil"] for x in plan}
    allumees = {s["objet"] for s in e["memoire"] if s["type"] == "flamme_employee"}
    flamme = next((k for k in sorted(allumees) if k in monde.objets and k not in vises
                   and porte_par(monde, k, id) and allumee(monde.objets[k])), None)
    if flamme is None:
        return
    geste = {"operation": "eteindre", "cible": flamme, "outil": "", "lieu": "", "condition": ""}
    if e["intention"]:
        plan.insert(0, geste)
    else:
        e["intention"] = {"but": {"type": "menager", "objet": flamme}, "motif": "menager", "plan": [geste],
                          "depuis": minute, "attente": 0}


def renoncer(monde, id, minute):
    e = esprit(monde, id)
    intention = e["intention"]
    e["renoncements"][intention["motif"]] = minute
    memoriser(monde, id, {"type": "renoncement", "but": dict(intention["but"])})
    e["intention"] = None
