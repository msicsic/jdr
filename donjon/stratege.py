"""Stratège : Luna propose ce que fait un PNJ, à partir de son seul esprit ; le moteur valide.

Le planificateur du moteur reste la règle. Le stratège n'est consulté que rarement, pour un
PNJ dont un besoin urgent n'a aucun plan, dont le seul plan est illicite (voler ou non
dépend de son caractère), ou qui reste désœuvré une heure. Il reçoit les traits en prose,
les besoins, les croyances, les souvenirs récents et les gestes possibles du PNJ ; jamais la
vérité du monde. Il renvoie un plan typé, « suivre » le plan du moteur, ou « attendre ».

Le moteur valide chaque geste : identifiants connus du PNJ, limites (``ne_vole_pas``,
``ne_ment_pas``) et capacités ; un écart est renvoyé une fois au stratège. Une étape qui
échoue à l'exécution abandonne la stratégie. Le budget est plafonné par PNJ et par heure
de jeu. Rien de ce qu'écrit Luna n'est montré au joueur, qui ne perçoit que les gestes.
"""
from .deliberation import (BESOINS, DESESPOIR, SOCIALES, _connus, _cru, _lieu_cru, autorise, confie_a_autrui,
                           illicite, profil, salle_crue)
from .echanges import demande_de_part
from .esprits import esprit, lire, memoriser, percoit, pnjs
from .monde import ErreurMonde

ATTENTE = 60            # minutes entre deux consultations pour un même PNJ
BUDGET_HEURE = 2        # consultations par heure de jeu pour tout le scénario
OISIVETE = 60           # minutes désœuvré avant de chercher un but dans sa personnalité
ETAPES_MAX = 6
REDEMANDE = 120         # minutes avant de redemander la même chose à qui vient de refuser
DECLENCHEURS = {
    "besoin_sans_plan": "un besoin urgent sans plan connu",
    "plan_illicite": "le seul plan trouvé touche au bien d'autrui (plan_moteur)",
    "desoeuvre": "désœuvré depuis une heure, sans besoin urgent",
}
GESTES = ("aller", "inspecter", "prendre", "poser", "ouvrir", "fermer", "deverrouiller", "verrouiller",
          "crocheter", "manger", "reposer", "servir", *SOCIALES)
APPELANT = None         # (instructions, entree, intention, fonction, schema) -> dict ; posé par le jeu ou le banc

INSTRUCTIONS = """Tu es le stratège d'un personnage non joueur d'un jeu de rôle. Le dossier est
tout ce qu'il sait : ses croyances peuvent être fausses ou périmées, et tu ne sais rien de
plus. Décide ce qu'il entreprend maintenant, d'après sa personnalité (traits), ses besoins et
le déclencheur. Réponds en appelant proposer_strategie une seule fois.

decision : « plan » (1 à 6 gestes), « suivre » (adopter plan_moteur tel quel, seulement s'il
est fourni) ou « attendre » (ne rien entreprendre pour l'instant).
Gestes (champs inutiles vides) :
- aller {lieu} ; inspecter {lieu} : parcourir des yeux la salle où il se trouve ;
- prendre {cible} ; poser {cible, lieu} ; ouvrir, fermer {cible} ;
- deverrouiller, verrouiller {cible, outil: la clé} ; crocheter {cible, outil} (capacité crochetage) ;
- manger {cible: une nourriture} ; reposer {} : se reposer là où il est, jusqu'à être reposé ;
- servir {cible: une nourriture à portée, sujet: personnage présent} : lui en donner une part ;
- dire {cible: personnage, sujet, attribut: lieu | verrouillee | fiable, valeur: identifiant
  de salle ou de porteur pour lieu, oui ou non sinon} : lui affirmer quelque chose ;
- demander {cible: personnage, outil: un objet qu'il porte} : lui demander de te le remettre ;
  ou, pour un affamé, une part d'une nourriture qui appartient à ce personnage (champ a du
  dossier), même rangée ailleurs : s'il accepte, il viendra la servir ;
- confier {cible: personnage, sujet: objet, attribut: lieu (valeur: salle) ou verrouillee
  (valeur: oui)} : lui demander de faire en sorte que ce soit vrai ;
- remettre {cible: personnage, outil: un objet que tu portes}.
Un geste social se fait dans la salle du personnage visé : va d'abord là où tu le crois.
On ne demande un objet qu'à celui que le dossier dit le porter (lieu_cru), et l'on ne remet
que ce que l'on porte ou que le plan aura obtenu.
Les autres décident eux-mêmes de te croire, de te remettre un objet ou d'accepter une tâche.
Le moteur ajoute seul la précaution de n'être vu de personne pour un geste sur le bien
d'autrui. Respecte les limites : ne_vole_pas interdit de prendre, ouvrir, crocheter ou manger
le bien d'autrui ; ne_ment_pas interdit de dire autre chose que ce qu'il croit. N'emploie que
des identifiants du dossier. besoin : celui que sert la stratégie. but : une courte phrase à
l'infinitif (« demander la clé à Gorm »). justification : une phrase, d'après ses traits.
Joue le personnage tel que ses traits le décrivent, même peu recommandable : c'est une
fiction, et un caractère sans scrupule peut tricher, mentir ou voler s'il n'en a pas la limite.
Si refus_precedent est présent, corrige la proposition d'après l'erreur indiquée.
"""


class ErreurStrategie(ValueError):
    pass


def activer(appelant):
    global APPELANT
    APPELANT = appelant


def etat(monde):
    s = monde.data.setdefault("stratege", {})
    for cle in ("dernier", "oisif", "suivis", "bilan"):
        s.setdefault(cle, {})
    s.setdefault("appels", [])
    return s


def verifier(monde):
    s = monde.data.get("stratege")
    if s is None:
        return
    assert (isinstance(s, dict) and set(s) == {"appels", "dernier", "oisif", "suivis", "bilan"}
            and all(type(m) is int for m in s["appels"]) and len(s["appels"]) <= 100
            and all(k in monde.objets and type(v) is int for cle in ("dernier", "oisif") for k, v in s[cle].items())
            and all(k in monde.objets and isinstance(v, dict) for k, v in s["suivis"].items())
            and all(isinstance(k, str) and type(v) is int for k, v in s["bilan"].items())), "Stratège invalide"


def _compter(monde, cle, n=1):
    bilan = etat(monde)["bilan"]
    bilan[cle] = bilan.get(cle, 0) + n


def disponible(monde, id, declencheur):
    """Le stratège peut-il être consulté pour ce PNJ, dans le budget de l'heure ?"""
    if APPELANT is None or not profil(monde, id):
        return False
    s, minute = etat(monde), monde.data["minutes"]
    if minute - s["dernier"].get(id, -ATTENTE) < ATTENTE:
        return False
    recents = sum(1 for m in s["appels"] if minute - m < 60)
    # Un PNJ désœuvré laisse toujours une place aux besoins urgents.
    return recents < BUDGET_HEURE - (declencheur == "desoeuvre")


# --- Dossier : l'esprit du PNJ, jamais la vérité ----------------------------------------

def _nom(monde, x):
    if x == "joueur":
        return monde.joueur["nom"]
    if x in monde.data["salles"]:
        return monde.data["salles"][x]["nom"]
    return monde.objets[x]["nom"] if x in monde.objets else x


def _personnages(monde, id):
    croyances = lire(monde, id)["croyances"]
    autres = [p for p in pnjs(monde) if p != id and (p in croyances or percoit(monde, id, p))]
    return sorted(autres) + (["joueur"] if "joueur" in croyances else [])


def _pulsion(monde, x):
    c = x["condition"]
    if "periode" in c:
        texte = f"inspecter {_nom(monde, c['lieu'])} au moins toutes les {c['periode']} minutes"
    elif "lieu" in c:
        texte = f"{_nom(monde, c['objet'])} doit être dans {_nom(monde, c['lieu'])}"
    else:
        texte = f"{_nom(monde, c['objet'])} doit rester verrouillé"
    return texte + f" ({x['besoin']})" + (", tâche confiée au joueur" if x.get("delegue_a") else "")


def dossier(monde, id, declencheur, besoin=None, plan_moteur=None):
    from .social import _proprietaire
    p, e, minute = profil(monde, id), lire(monde, id), monde.data["minutes"]
    croyances = sorted(((sujet, attribut, c) for sujet, attributs in e["croyances"].items()
                        for attribut, c in attributs.items()), key=lambda x: -x[2]["minute"])[:40]
    objets = [{"id": o, "nom": monde.objets[o]["nom"], "type": monde.objets[o]["type"],
               "lieu_cru": _lieu_cru(monde, id, o) or "", "salle_crue": salle_crue(monde, id, o),
               "a": _proprietaire(monde, {"objet": o}) or "",
               "usages": monde.objets[o].get("usages", []), "ouvre": monde.objets[o].get("ouvre", [])}
              for o in _connus(monde, id) if monde.objets[o]["type"] != "personnage"]
    return {
        "personnage": {"id": id, "nom": monde.objets[id]["nom"], "traits": p["traits"],
                       "caracteristiques": p["caracteristiques"], "limites": p["limites"],
                       "capacites": p["capacites"], "salle": monde.objets[id]["lieu"]},
        "minute": minute,
        "declencheur": {"nature": declencheur, "sens": DECLENCHEURS[declencheur], "besoin": besoin or ""},
        "besoins": {b: {"valeur": round(e["besoins"].get(b, 0)), "urgence": v["urgence"]}
                    for b, v in p["besoins"].items()},
        "pulsions": [_pulsion(monde, x) for x in p["pulsions"]],
        "engagements": [{"pour": x["pour"], "condition": x["condition"]} for x in e["engagements"]],
        "croyances": [{"sujet": s, "attribut": a, "valeur": c["valeur"], "source": c["source"],
                       "il_y_a_minutes": minute - c["minute"]} for s, a, c in croyances],
        "objets_connus": objets,
        "personnages_connus": [{"id": x, "nom": _nom(monde, x), "present": percoit(monde, id, x),
                                "salle_crue": salle_crue(monde, id, x) if x != "joueur" else
                                (_cru(monde, id, "joueur", "lieu") or "")} for x in _personnages(monde, id)],
        "salles": [{"id": s, "nom": v["nom"]} for s, v in monde.data["salles"].items()],
        "souvenirs_recents": e["memoire"][-12:],
        "plan_moteur": plan_moteur or [],
    }


def schema(monde, id):
    connus = sorted({*_connus(monde, id), *_personnages(monde, id)} - {id})
    salles = list(monde.data["salles"])
    besoins = [b for b in BESOINS if b in profil(monde, id)["besoins"]]
    if lire(monde, id)["engagements"]:
        besoins.append("engagement")
    chaine = lambda valeurs: {"type": "string", "enum": ["", *valeurs]}
    return {
        "type": "object", "additionalProperties": False,
        "properties": {
            "decision": {"type": "string", "enum": ["plan", "suivre", "attendre"]},
            "besoin": {"type": "string", "enum": besoins},
            "but": {"type": "string"},
            "etapes": {"type": "array", "maxItems": ETAPES_MAX, "items": {
                "type": "object", "additionalProperties": False,
                "properties": {"operation": {"type": "string", "enum": list(GESTES)},
                               "cible": chaine(connus), "outil": chaine(connus), "lieu": chaine(salles),
                               "sujet": chaine(connus),
                               "attribut": {"type": "string", "enum": ["", "lieu", "verrouillee", "fiable"]},
                               "valeur": chaine([*salles, *connus, "oui", "non"])},
                "required": ["operation", "cible", "outil", "lieu", "sujet", "attribut", "valeur"]}},
            "justification": {"type": "string"},
        },
        "required": ["decision", "besoin", "but", "etapes", "justification"],
    }


# --- Validation : le moteur garde l'autorité ---------------------------------------------

def _etape(monde, id, n, x, obtenus):
    """Un geste typé, cohérent avec ce que le PNJ croit ; ``obtenus`` : ce que le plan lui aura mis en main."""
    from .spatial import porte_par
    p = profil(monde, id)
    op = x.get("operation")
    connus = set(_connus(monde, id)) | set(_personnages(monde, id))
    faute = lambda texte: ErreurStrategie(f"étape {n} ({op}) : {texte}")
    if op not in GESTES:
        raise faute("geste inconnu")
    etape = {"operation": op, "cible": "", "outil": "", "lieu": "", "condition": ""}

    def connu(cle, types=None):
        valeur = x.get(cle) or ""
        if valeur not in connus or valeur == id:
            raise faute(f"{cle} « {valeur} » n'est pas un identifiant qu'il connaît")
        if types and (valeur == "joueur" or monde.objets[valeur]["type"] not in types):
            raise faute(f"{cle} « {valeur} » doit être : {', '.join(types)}")
        return valeur

    def salle(cle="lieu"):
        if x.get(cle) not in monde.data["salles"]:
            raise faute(f"{cle} doit être une salle")
        return x[cle]

    if op in ("aller", "inspecter"):
        etape["lieu"] = salle()
    elif op == "reposer":
        if "repos" not in p["besoins"]:
            raise faute("ce personnage n'a pas besoin de repos")
    elif op in SOCIALES:
        etape["cible"] = connu("cible", ("personnage",))
        if not monde.objets[etape["cible"]].get("profil"):
            raise faute("ce personnage ne prend part à aucun échange")
        refus = [s for s in lire(monde, id)["memoire"] if s["type"] == "refus" and s["de"] == etape["cible"]
                 and s["operation"] == op and monde.data["minutes"] - s["minute"] < REDEMANDE]
        if refus and op != "dire":
            raise faute(f"ce personnage a refusé il y a {monde.data['minutes'] - refus[-1]['minute']} minutes "
                        f"({refus[-1]['raison']}) : ne lui redemande pas déjà la même chose")
        if op in ("demander", "remettre"):
            etape["outil"] = connu("outil")
            if (op == "demander" and _lieu_cru(monde, id, etape["outil"]) != etape["cible"]
                    and not demande_de_part(monde, id, etape["cible"], etape["outil"])):
                raise faute("il ne croit pas que ce personnage porte cet objet (voir lieu_cru), et ce n'est pas"
                            " une part d'une nourriture qui lui appartient")
            if op == "demander":
                obtenus.add(etape["outil"])
            elif not (porte_par(monde, etape["outil"], id) or etape["outil"] in obtenus):
                raise faute("il ne porte pas cet objet et le plan ne le lui fait pas obtenir")
        elif op == "dire":
            sujet, attribut, valeur = connu("sujet"), x.get("attribut"), x.get("valeur")
            if attribut == "lieu":
                if valeur not in monde.data["salles"] and valeur not in connus:
                    raise faute("la valeur d'un lieu est une salle ou un porteur")
            elif attribut in ("verrouillee", "fiable") and valeur in ("oui", "non"):
                valeur = valeur == "oui"
            else:
                raise faute("attribut lieu, verrouillee ou fiable, avec une valeur qui lui convient")
            if "ne_ment_pas" in p["limites"] and _cru(monde, id, sujet, attribut) != valeur:
                raise faute("il ne ment pas : il ne peut dire que ce qu'il croit, et il ne croit pas cela")
            etape["contenu"] = {"sujet": sujet, "attribut": attribut, "valeur": valeur}
        else:
            objet = connu("sujet")
            if x.get("attribut") == "lieu" and x.get("valeur") in monde.data["salles"]:
                etape["contenu"] = {"objet": objet, "lieu": x["valeur"]}
            elif x.get("attribut") == "verrouillee" and x.get("valeur") == "oui":
                etape["contenu"] = {"objet": objet, "verrouillee": True}
            else:
                raise faute("une tâche est un objet dans une salle (lieu) ou un objet verrouillé (verrouillee oui)")
    else:
        cible = connu("cible")
        o = monde.objets[cible]
        etape["cible"] = cible
        if op in ("manger", "servir") and o["type"] != "nourriture":
            raise faute("on ne mange ou ne sert qu'une nourriture")
        if op == "servir":
            pour = connu("sujet", ("personnage",))
            etape["contenu"] = {"pour": pour}
        if op in ("ouvrir", "fermer", "deverrouiller", "verrouiller", "crocheter") and o["type"] not in ("porte", "contenant"):
            raise faute("on n'ouvre ou ne verrouille qu'une porte ou un contenant")
        if op in ("prendre", "poser") and not o.get("mobile"):
            raise faute("cet objet ne se déplace pas")
        if op == "poser":
            etape["lieu"] = salle()
        if op in ("deverrouiller", "verrouiller", "crocheter"):
            etape["outil"] = connu("outil")
            if op == "crocheter" and "crochetage" not in p["capacites"]:
                raise faute("il ne sait pas crocheter")
        if op == "prendre":
            obtenus.add(cible)
        if op in ("prendre", "ouvrir", "crocheter", "manger", "servir") and illicite(monde, id, cible):
            if not autorise(monde, id, cible) or op != "prendre" and "ne_vole_pas" in p["limites"]:
                raise faute("il ne vole pas : ce bien est à un autre")
            etape["condition"] = "sans_temoin"
    return etape


def valider(monde, id, proposition, plan_moteur=None):
    if not isinstance(proposition, dict):
        raise ErreurStrategie("proposition illisible")
    decision, besoin = proposition.get("decision"), proposition.get("besoin")
    p = profil(monde, id)
    if besoin not in p["besoins"] and not (besoin == "engagement" and lire(monde, id)["engagements"]):
        raise ErreurStrategie(f"besoin « {besoin} » inconnu de ce personnage")
    but = " ".join(str(proposition.get("but") or "").split())[:120]
    if decision == "suivre":
        if not plan_moteur:
            raise ErreurStrategie("suivre n'a de sens que si plan_moteur est fourni")
        return {"decision": "suivre", "besoin": besoin, "but": but}
    if decision == "attendre":
        return {"decision": "attendre", "besoin": besoin, "but": but}
    if decision != "plan":
        raise ErreurStrategie("decision : plan, suivre ou attendre")
    etapes = proposition.get("etapes")
    if not isinstance(etapes, list) or not 1 <= len(etapes) <= ETAPES_MAX or not but:
        raise ErreurStrategie(f"un plan a un but et de 1 à {ETAPES_MAX} gestes")
    obtenus = set()
    gestes = [_etape(monde, id, n + 1, x, obtenus) for n, x in enumerate(etapes)]
    for n, etape in enumerate(gestes, 1):
        vise = {etape["cible"], etape["outil"], etape.get("contenu", {}).get("objet")} - {""}
        if etape["operation"] not in ("aller", "inspecter", "reposer", "dire") and any(
                confie_a_autrui(monde, id, o) for o in vise):
            raise ErreurStrategie(f"étape {n} ({etape['operation']}) : il a confié cette tâche à quelqu'un qu'il croit "
                                  "fiable, il ne la fait pas à sa place et ne la confie pas à un autre")
    return {"decision": "plan", "besoin": besoin, "but": but, "etapes": completer(monde, id, gestes)}


def completer(monde, id, gestes):
    """Le stratège dit quoi, le moteur dit comment : chaque geste reçoit ce qu'il suppose.

    Le planificateur du moteur, sur les croyances du PNJ, ajoute les déplacements, ouvre ou
    déverrouille le contenant d'un objet visé, va chercher la clé ou l'outil. Un geste qu'il ne
    sait pas rendre possible est refusé avec sa raison.
    """
    from .deliberation import Echec, Plan
    p = Plan(monde, id)
    for n, etape in enumerate(gestes, 1):
        op, cible = etape["operation"], etape["cible"]
        try:
            if op == "aller":
                p.aller(etape["lieu"])
                continue
            if op == "prendre":
                if cible not in p.portes:
                    p.obtenir(cible)
                continue
            if op in ("inspecter", "poser"):
                p.aller(etape["lieu"])
            elif op in ("manger", "servir") and cible not in p.portes:
                lieu = _lieu_cru(monde, id, cible)
                if lieu in monde.data["salles"]:
                    p.aller(lieu)
                elif lieu in monde.objets and monde.objets[lieu]["type"] == "contenant":
                    p.acceder(lieu)
                else:
                    raise Echec
            elif cible and op != "reposer":
                salle = salle_crue(monde, id, cible)
                if salle is None:
                    raise Echec
                if etape["outil"] and etape["outil"] not in p.portes and op in ("deverrouiller", "verrouiller", "crocheter"):
                    p.obtenir(etape["outil"])
                p.aller(salle)
        except Echec:
            raise ErreurStrategie(f"étape {n} ({op}) : il ne voit pas comment y parvenir d'après ce qu'il croit "
                                  "(chemin, contenant fermé sans clé ni outil, objet introuvable)") from None
        p.etapes.append(etape)
        if op == "ouvrir":
            p.ouverts.add(cible)
        elif op in ("deverrouiller", "crocheter"):
            p.deverrouilles.add(cible)
        elif op == "demander":
            p.portes.add(etape["outil"])
        elif op == "remettre":
            p.portes.discard(etape["outil"])
    if len(p.etapes) > 3 * ETAPES_MAX:
        raise ErreurStrategie("plan trop long une fois complété : vise un but plus proche")
    return p.etapes


# --- Consultation et adoption -------------------------------------------------------------

def consulter(monde, id, declencheur, besoin=None, plan_moteur=None):
    """Décision validée du stratège, ou None (indisponible, injoignable ou deux refus)."""
    s, minute = etat(monde), monde.data["minutes"]
    s["dernier"][id] = minute
    entree = {"dossier": dossier(monde, id, declencheur, besoin, plan_moteur)}
    for tentative in range(2):
        if tentative and sum(1 for m in s["appels"] if minute - m < 60) >= BUDGET_HEURE:
            return None  # La correction aussi se paie sur le budget de l'heure.
        s["appels"] = (s["appels"] + [minute])[-100:]
        _compter(monde, "appels")
        try:
            proposition = APPELANT(INSTRUCTIONS, entree, "Stratégie de " + monde.objets[id]["nom"],
                                   "proposer_strategie", schema(monde, id))
        except ErreurMonde:
            _compter(monde, "injoignable")
            return None
        try:
            decision = valider(monde, id, proposition, plan_moteur)
        except ErreurStrategie as exc:
            _compter(monde, "refus")
            entree = {**entree, "refus_precedent": {"proposition": proposition, "erreur": str(exc)}}
            continue
        _compter(monde, decision["decision"])
        return decision
    return None


def adopter(monde, id, decision, minute):
    """Une stratégie devient l'intention du PNJ ; « attendre » le laisse désœuvré."""
    from .pnj import _chroniquer
    from .social import _qui
    e = esprit(monde, id)
    if decision["decision"] != "plan":
        e["intention"] = None
        return
    e["intention"] = {"but": {"type": "strategie", "resume": decision["but"]}, "motif": decision["besoin"],
                      "plan": decision["etapes"], "depuis": minute, "attente": 0}
    memoriser(monde, id, {"type": "strategie", "but": decision["but"]})
    de = "d'" if decision["but"][:1].lower() in "aeiouyhéèêàâîôû" else "de "
    _chroniquer(monde, id, f"{_qui(monde, id)} décide {de}{decision['but']}.", "decision")


def terminer(monde, id, reussie, etape=None):
    """Fin d'une stratégie : menée à son terme, ou abandonnée au premier geste manqué."""
    from .pnj import _chroniquer
    from .social import _qui
    e = esprit(monde, id)
    but = e["intention"]["but"]["resume"]
    memoriser(monde, id, {"type": "strategie_aboutie" if reussie else "strategie_echouee", "but": but,
                          **({"etape": etape["operation"], "cible": etape["cible"] or etape["lieu"]} if etape else {})})
    _compter(monde, "abouties" if reussie else "echouees")
    if not reussie:
        _chroniquer(monde, id, f"{_qui(monde, id)} renonce à {but}.", "decision")
    e["intention"] = None


def plan_illicite(monde, id, besoin, but, etapes, minute):
    """Le seul plan trouvé touche au bien d'autrui : son caractère en décide. True si tranché."""
    if APPELANT is None or esprit(monde, id)["besoins"].get(besoin, 0) >= DESESPOIR:
        return False  # À bout, le besoin l'emporte sur les scrupules comme sur la crainte d'être vu.
    s = etat(monde)
    if (not any(x["condition"] == "sans_temoin" for x in etapes) or s["suivis"].get(id) == but
            or not disponible(monde, id, "plan_illicite")):
        return False
    decision = consulter(monde, id, "plan_illicite", besoin, etapes)
    if not decision or decision["decision"] == "suivre":
        s["suivis"][id] = dict(but)
        return False
    if decision["decision"] == "attendre":
        # Il s'en abstient pour l'instant : le moteur ne le lui reproposera qu'après le répit.
        esprit(monde, id)["renoncements"][besoin] = minute
    # Une autre voie : si elle échoue, le plan du moteur revient, sans nouvelle consultation avant l'heure.
    adopter(monde, id, decision, minute)
    return True


def occupe(monde, id):
    if APPELANT is not None:
        etat(monde)["oisif"].pop(id, None)


def desoeuvre(monde, id, minute, urgents):
    """Sans plan du moteur : un besoin urgent, ou une heure d'oisiveté, appellent le stratège."""
    if APPELANT is None:
        return
    s = etat(monde)
    s["suivis"].pop(id, None)
    depuis = s["oisif"].setdefault(id, minute)
    if urgents:
        declencheur, besoin = "besoin_sans_plan", urgents[0]
    elif minute - depuis >= OISIVETE:
        declencheur, besoin = "desoeuvre", None
    else:
        return
    if not disponible(monde, id, declencheur):
        return
    decision = consulter(monde, id, declencheur, besoin)
    if decision:
        adopter(monde, id, decision, minute)
        if decision["decision"] == "plan":
            s["oisif"].pop(id, None)
    if declencheur == "desoeuvre":
        s["oisif"][id] = minute  # La prochaine heure d'oisiveté se compte de nouveau.
