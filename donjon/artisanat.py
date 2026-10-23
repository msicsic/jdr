"""Assemblages improvisés : propositions du MJ, contraintes et effets du jeu.

Premier profil : deux montants, des traverses liées, un accès vertical installé.
Les charges et difficultés sont des conventions de JDR, pas un calcul de structure.
"""
import copy
import hashlib
import json
import math

from .monde import ErreurMonde, objet
from .francais import designer
from .geometrie import placer
from .perception import eclairage
from .vol import proprietaire
from .refus import inaccessible, liste


def fabrication(montants, traverses, lien, outil, longueur_cm=300, largeur_cm=35,
                difficulte=12, justification="Préparer deux montants et lier les traverses.", rythme="normal"):
    return dict(action="fabriquer", profil="barreaux", montants=montants, traverses=traverses,
                lien=lien, outil=outil, longueur_cm=longueur_cm, largeur_cm=largeur_cm,
                difficulte=difficulte, justification=justification, rythme=rythme)


SCHEMA_FABRICATION = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": ["fabriquer"]},
        "profil": {"type": "string", "enum": ["barreaux"]},
        "montants": {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "string"}},
        "traverses": {"type": "string"}, "lien": {"type": "string"}, "outil": {"type": "string"},
        "longueur_cm": {"type": "integer", "minimum": 100, "maximum": 500},
        "largeur_cm": {"type": "integer", "minimum": 25, "maximum": 60},
        "difficulte": {"type": "integer", "minimum": 0, "maximum": 18},
        "rythme": {"type": "string", "enum": ["normal", "soigne"]},
        "justification": {"type": "string"},
    }, "required": list(fabrication([], "", "", "")),
}

# Usages modélisés d'un assemblage : le moteur ne simule que ceux-là. Une autre construction
# reste un objet ordinaire (voir docs/plan-fabrication.md).
USAGES = ("echelle",)
SCHEMA_ASSEMBLAGE = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": ["assembler"]},
        "usage": {"type": "string", "enum": list(USAGES)},
        "pieces": {"type": "object", "additionalProperties": False,
                   "properties": {"montants": {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "string"}},
                                  "barreaux": {"type": "string"}},
                   "required": ["montants", "barreaux"]},
        "lien": {"type": "string"}, "outil": {"type": "string"},
        "longueur_cm": {"type": "integer", "minimum": 100, "maximum": 500},
        "largeur_cm": {"type": "integer", "minimum": 25, "maximum": 60},
        "difficulte": {"type": "integer", "minimum": 0, "maximum": 18},
        "rythme": {"type": "string", "enum": ["normal", "soigne"]},
        "justification": {"type": "string"},
    },
    "required": ["action", "usage", "pieces", "lien", "outil", "longueur_cm", "largeur_cm", "difficulte",
                 "rythme", "justification"],
}
SCHEMA_DECOUPE = {
    "type": "object", "additionalProperties": False,
    "properties": {"action": {"type": "string", "enum": ["decouper"]}, "cible": {"type": "string"},
                   "outil": {"type": "string"}, "longueur_cm": {"type": "integer", "minimum": 5},
                   "justification": {"type": "string"}},
    "required": ["action", "cible", "outil", "longueur_cm", "justification"],
}


def normaliser(p):
    """Une proposition assembler (usage, pièces par rôle) ramenée à la forme de calcul de l'échelle."""
    if not isinstance(p, dict) or p.get("action") != "assembler":
        return p
    if set(p) != set(SCHEMA_ASSEMBLAGE["required"]):
        raise ErreurMonde("Proposition d'assemblage invalide.",
                          f"assembler a exactement les champs {', '.join(SCHEMA_ASSEMBLAGE['required'])} ; reçu : {sorted(p)}.")
    if p["usage"] not in USAGES:
        raise ErreurMonde("Cet usage n'est pas modélisé.", f"usage parmi {', '.join(USAGES)} (reçu « {p['usage']} »).")
    pieces = p["pieces"]
    if not isinstance(pieces, dict) or set(pieces) != {"montants", "barreaux"}:
        raise ErreurMonde("Pièces mal désignées.", "pieces : montants (deux identifiants) et barreaux (un identifiant).")
    return dict(action="fabriquer", profil="barreaux", montants=pieces["montants"], traverses=pieces["barreaux"],
                lien=p["lien"], outil=p["outil"], longueur_cm=p["longueur_cm"], largeur_cm=p["largeur_cm"],
                difficulte=p["difficulte"], justification=p["justification"], rythme=p["rythme"])


REGLES = """
FABRICATION ET INSTALLATION (conventions de jeu, pas conseils de construction réelle) :
Le dossier atelier sépare ressources connues, inconnues et assemblages possibles.
Pour une volonté de fabriquer une échelle, ou une question sur sa faisabilité (le moteur prépare
alors l'assemblage sans rien fabriquer et dit ce qui manque), propose action assembler, usage
echelle (voir Assembler et découper) : deux montants distincts, une barre pour les barreaux, un
lien, un outil, longueur_cm, largeur_cm, difficulte 10..18, justification courte (méthode et risque).
Choisis aussi rythme : normal = 26 min et jet pour l'échelle de 3 m ; soigne = deux fois
plus de temps, sans jet, si le dossier l'autorise (difficulte=0). « Je prends mon temps »,
« soigneusement », « sans me presser » demandent soigne. Sans urgence ni préférence du joueur,
préfère soigne : une fabrication ordinaire au calme ne doit pas devenir une loterie répétée.
Une reprise explicite « je retente » reprend cependant le rythme de la dernière tentative,
sauf demande de changement. Le rythme soigne ne contourne ni manque de matière ni outil absent.
Le moteur calcule barreaux, consommation, durée et charge ; ne les invente pas. Reprends
une suggestion du dossier si elle convient à l'intention. Fabrication et installation
sont séparées : construire ne garantit pas d'atteindre un mur donné. N'invente ni matériaux
ni résistance manquante, ni passage ou point d'appui. Une impossibilité locale n'interdit
pas toutes les fabrications ; explique la ressource ou la dimension à corriger.
Après fabrication : action installer, cible assemblage, outil appui_vertical présent ;
action franchir, cible assemblage installé, outil vide (monte OU descend selon ta position) ;
action desinstaller, cible assemblage installé, outil vide, depuis le pied ou le sommet
si une prise et un sol stable permettent de le remonter. Installer est également possible
depuis le sommet : on abaisse l'échelle vers le sol voisin. Composer permet de combiner
soulever, appuyer et franchir, sans imposer de commandes séparées au joueur.
Le dossier manoeuvres donne les appuis et passages déjà validés depuis la position actuelle.
Placer une échelle contre un appui utilise installer (ou appuyer dans composer), pas deplacer
vers la pièce. Pour monter avec une échelle encore libre, composer appuyer puis franchir
si l'appui figure dans installer_puis_franchir ; une seule confirmation couvre les deux gestes.
Ces trois actions utilisent methode simple, difficulte 0 et une justification courte.
La résistance est un arbitrage de jeu persisté, pas une certitude d'ingénierie.
"""


def ressources_libres(m, nature):
    return sorted(i for i, o in m.objets.items()
                  if o.get("ressource") == nature and m.designable(i) and not o.get("incorpore")
                  and not o.get("attache") and o["mobile"] and o["integrite"] >= o["maximum"]
                  and proprietaire(m, o) in (None, "joueur"))


def ressource(m, id, nature):
    o = m.objets.get(id)
    if not o or not m.accessible(id):
        raise inaccessible(m, id, champ=nature, filtre=lambda x: x.get("ressource") == nature)
    from .proximite import exiger
    exiger(m, id)
    libres = f"{nature} libres ici : {liste(ressources_libres(m, nature))}."
    if o.get("incorpore"):
        raise ErreurMonde(f"{designer(o, debut=True)} fait déjà partie d'un assemblage.", f"{id} est incorporé ; {libres}")
    if o.get("attache"):
        raise ErreurMonde(f"{designer(o, debut=True)} est encore attaché.", f"detacher {id} d'abord, ou choisis parmi les {libres}")
    if not o["mobile"]:
        raise ErreurMonde(f"Tu ne disposes pas librement de {designer(o)}.", f"{id} est fixe ; {libres}")
    if proprietaire(m, o) not in (None, "joueur"):
        raise ErreurMonde(f"Tu ne disposes pas librement de {designer(o)}.",
                          f"{id} appartient à {proprietaire(m, o)} : obtiens-le d'abord, ou choisis parmi les {libres}")
    if "physique" not in o and not o.get("ressource"):
        raise ErreurMonde(f"{designer(o, debut=True)} n'est pas encore décrit.",
                          f"décris d'abord {id} (etablir_faits, qualification avec physique : forme, matiere, "
                          f"dimensions, pieces), puis re-propose ; {libres}")
    if o.get("physique", {}).get("pieces", 1) > 1:
        raise ErreurMonde(f"{designer(o, debut=True)} forme un lot de plusieurs pièces.",
                          f"prélève d'abord une pièce de {id} (étape prelever), puis emploie-la ; {libres}")
    if o.get("ressource") != nature or o["integrite"] < o["maximum"]:
        raise ErreurMonde(f"{designer(o, debut=True)} ne convient pas comme {nature} intact.",
                          f"{id} n'est pas un {nature} intact ; {libres}")
    for champ in ("longueur_cm", "charge_jeu_kg"):
        if not isinstance(o.get(champ), (int, float)) or isinstance(o.get(champ), bool) or not math.isfinite(o[champ]) or o[champ] <= 0:
            raise ErreurMonde(f"Il manque une mesure ou une estimation établie : {id}.{champ}.",
                              f"décris d'abord {id} (etablir_faits, qualification avec physique : forme, matiere, "
                              "dimensions, pieces), puis re-propose la fabrication.")
    return o


def calculer(m, p):
    champs = set(fabrication([], "", "", ""))
    if (not isinstance(p, dict) or set(p) not in (champs, champs - {"rythme"})
            or p["action"] != "fabriquer" or p["profil"] != "barreaux"):
        recus = sorted(p) if isinstance(p, dict) else type(p).__name__
        raise ErreurMonde("Proposition d'assemblage invalide.",
                          f"fabriquer a les champs {', '.join(sorted(champs))} (rythme facultatif), action fabriquer, "
                          f"profil barreaux ; reçu : {recus}.")
    if (not isinstance(p["montants"], list) or len(p["montants"]) != 2
            or any(not isinstance(i, str) for i in p["montants"])
            or any(not isinstance(p[k], str) for k in ("traverses", "lien", "outil", "justification"))
            or len(p["justification"]) > 1000):
        raise ErreurMonde("Précise deux montants, les traverses, le lien et l'outil.",
                          "montants : liste de deux identifiants ; traverses, lien, outil : un identifiant chacun ; "
                          f"justification ≤ 1000 caractères ; perches libres : {liste(ressources_libres(m, 'perche'))} ; "
                          f"liens libres : {liste(ressources_libres(m, 'lien'))}.")
    ids = [*p["montants"], p["traverses"], p["lien"], p["outil"]]
    # Un rôle laissé vide : ce qui manque, dans l'ordre de l'assemblage, une cause par refus. C'est aussi
    # la réponse à « puis-je fabriquer une échelle ? » quand rien ne peut tenir ce rôle ici.
    for vides, nature, besoin in ((sum(not i.strip() for i in p["montants"]), "perche",
                                   "deux montants, deux barres libres d'une seule pièce"),
                                  (not p["traverses"].strip(), "perche", "une barre libre où tailler les barreaux"),
                                  (not p["lien"].strip(), "lien", "un lien pour attacher les barreaux")):
        if vides:
            libres = [i for i in ressources_libres(m, nature) if i not in ids]
            besoin = "un second montant, une barre libre d'une seule pièce" if vides == 1 and nature == "perche" \
                and besoin.startswith("deux") else besoin
            raise ErreurMonde(f"Pour une échelle, il te manque {besoin}"
                              + ("." if libres else " : rien de tel n'est à ta disposition ici."),
                              f"désigne {besoin.split(',')[0]} parmi {liste(libres)} ; un objet qui pourrait servir "
                              "mais n'est pas encore décrit se décrit d'abord (etablir_faits, qualification avec physique).")
    if len(set(ids)) != 5:
        raise ErreurMonde("Chaque rôle exige une ressource distincte ; on ne peut pas compter deux fois une perche.",
                          f"cinq identifiants distincts (2 montants, traverses, lien, outil) ; reçu {', '.join(ids)} ; "
                          f"perches libres : {liste(ressources_libres(m, 'perche'))}.")
    rythme = p.get("rythme", "normal")  # Compatibilité avec les propositions déjà sauvegardées.
    if rythme not in ("normal", "soigne"):
        raise ErreurMonde("Choisis une fabrication normale ou soignée.", f"rythme : normal ou soigne (reçu « {rythme} »).")
    for cle, bas, haut in (("longueur_cm", 100, 500), ("largeur_cm", 25, 60), ("difficulte", 0 if rythme == "soigne" else 10, 18)):
        if type(p[cle]) is not int or not bas <= p[cle] <= haut:
            raise ErreurMonde(f"{cle} doit être un entier entre {bas} et {haut}.",
                              f"{cle} : entier de {bas} à {haut} (reçu {p[cle]!r})"
                              + (" ; le rythme soigne accepte difficulte 0" if cle == "difficulte" and rythme == "normal" else "") + ".")
    bois = [ressource(m, id, "perche") for id in ids[:3]]
    lien = ressource(m, p["lien"], "lien")
    t = m.objets.get(p["outil"], {})
    if (not m.accessible(p["outil"]) or not m.est_porte(p["outil"])
            or not t.get("integrite") or "couper_bois" not in t.get("usages", [])):
        haches = sorted(i for i, x in m.objets.items() if m.est_porte(i) and x.get("integrite")
                        and "couper_bois" in x.get("usages", []))
        raise ErreurMonde("Il faut tenir un outil utilisable pour couper du bois, par exemple une hache.",
                          f"outil : un objet porté d'usage couper_bois, parmi {liste(haches)}"
                          + ("" if haches else " ; prends-en un d'abord") + ".")
    longueur, largeur = p["longueur_cm"], p["largeur_cm"]
    if any(o["longueur_cm"] < longueur for o in bois[:2]):
        plus_court = min(o["longueur_cm"] for o in bois[:2])
        raise ErreurMonde("Les montants disponibles sont trop courts pour cette longueur.",
                          f"longueur_cm au plus {plus_court} avec ces montants, ou des montants plus longs.")
    # Espacement maximal conventionnel de 35 cm, perte de coupe de 1 cm par barreau.
    barreaux = math.ceil(longueur / 35) - 1
    coupe = barreaux * (largeur + 1)
    liens = barreaux * 2 * 60
    if bois[2]["longueur_cm"] < coupe:
        raise ErreurMonde(f"Il faut {coupe} cm pour {barreaux} barreaux (pertes comprises), mais cette perche n'a que {bois[2]['longueur_cm']} cm. Réduis largeur ou longueur.",
                          f"barreaux = ceil(longueur_cm / 35) - 1 ; coupe = barreaux × (largeur_cm + 1) ≤ {bois[2]['longueur_cm']} : "
                          "réduis largeur_cm ou longueur_cm, ou une traverse plus longue.")
    if lien["longueur_cm"] < liens:
        raise ErreurMonde(f"Il faut {liens} cm de lien pour les attaches ; il n'en reste que {lien['longueur_cm']} cm.",
                          f"lien nécessaire = barreaux × 120 cm ≤ {lien['longueur_cm']} : réduis longueur_cm, ou un lien plus long.")
    consommes = dict(zip(ids[:4], [longueur, longueur, coupe, liens]))
    charge = min(o["charge_jeu_kg"] for o in [*bois, lien]) * .8
    signature = {"version": 1, "profil": p["profil"], "longueur": longueur, "largeur": largeur,
                 "materiaux": [{k: o.get(k) for k in ("ressource", "materiau", "diametre_cm", "charge_jeu_kg")}
                               for o in [*bois, lien]], "outil": t.get("usages", [])}
    cle = "assemblage:" + hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    precedent = m.data["arbitrages"].get(cle)
    dd = precedent["dd"] if precedent else p["difficulte"]
    minutes = (10 + barreaux * 2) * (2 if rythme == "soigne" else 1)
    if rythme == "soigne":
        raison = obstacle_soin(m, minutes)
        if raison:
            raise ErreurMonde(raison, "rythme normal (avec un jet), ou réunis d'abord la condition manquante.")
        dd = 0
    return dict(consommes=consommes, barreaux=barreaux, charge_jeu_kg=charge,
                longueur_cm=longueur, largeur_cm=largeur, dd=dd, cle=cle,
                minutes=minutes, memorise=bool(precedent) and rythme == "normal", rythme=rythme)


def obstacle_soin(m, minutes):
    salle = m.data["salles"][m.joueur["salle"]]
    if salle.get("travail_calme") is not True:
        return "Ce lieu ne permet pas de travailler au calme assez longtemps pour une fabrication soignée."
    if salle.get("urgence_minutes") is not None and salle["urgence_minutes"] < minutes:
        return "Le temps disponible avant l'urgence ne suffit pas pour travailler soigneusement."
    from .perception import avancer_combustion
    projection = m.copier()
    avancer_combustion(projection, minutes, [])
    if eclairage(m)["niveau"] < 2 or eclairage(projection)["niveau"] < 2:
        return "Il faut une lumière suffisante pendant toute la durée du travail soigné."
    return None


def installer(m):
    """Autorisation d'auteur, additive et limitée à la cour de l'atelier."""
    if m.data.get("artisanat_soigne_version") or "cour" not in m.data["salles"]:
        return
    if m.data["salles"]["cour"].get("nom") != "Cour de l'atelier":
        return
    m.data["salles"]["cour"].setdefault("travail_calme", True)
    m.data["artisanat_soigne_version"] = 1


def preparer(m, p, origine):
    from .moteur import Plan
    if eclairage(m)["niveau"] < 2:
        raise ErreurMonde("Il faut assez de lumière pour préparer et assembler les pièces.",
                          "fabriquer exige une lumière franche : allume d'abord une source.")
    proposee, p = p, normaliser(p)
    bilan = calculer(m, p)
    plan = Plan(copy.deepcopy(proposee), m.data["revision"],
                f"Fabriquer une échelle de {bilan['longueur_cm'] / 100:g} m avec {bilan['barreaux']} barreaux.",
                origine="arbitrage mémorisé" if bilan["memorise"] else origine)
    plan.stat, plan.dd, plan.minutes, plan.bruit = "DEX", bilan["dd"], bilan["minutes"], 2
    plan.cle_arbitrage = bilan["cle"]
    plan.effets = [("assembler", "", {"proposition": copy.deepcopy(p), "bilan": bilan})]
    plan.echec = [("perdre_lien", p["lien"], min(120, bilan["consommes"][p["lien"]]))]
    plan.risque = "En cas d'échec, les perches restent disponibles, mais deux mètres de lien et le temps de travail sont perdus."
    if bilan["rythme"] == "soigne":
        plan.titre = plan.titre.replace("Fabriquer ", "Fabriquer soigneusement ", 1)
        plan.stat, plan.dd, plan.cle_arbitrage = "", 0, ""
        plan.echec, plan.risque = [], ""
    return plan


def appui(m, support):
    o = m.objets.get(support, {})
    a = o.get("appui_vertical", {})
    if (not a or not o.get("integrite") or a.get("bas") not in m.data["salles"]
            or a.get("haut") not in m.data["salles"] or a["bas"] == a["haut"]):
        appuis = sorted(i for i, x in m.objets.items() if x.get("appui_vertical") and m.accessible(i))
        raise ErreurMonde("Il faut un appui établi reliant un sol et un palier accessible en hauteur.",
                          f"outil : un appui vertical établi, parmi {liste(appuis)} (reçu « {support} ») ; "
                          "un appui inconnu s'établit d'abord par espace.")
    if not a.get("sol_stable") or not a.get("sommet_stable"):
        raise ErreurMonde("Le pied et le sommet doivent offrir des appuis stables.",
                          f"{support} n'offre pas d'appui stable : choisis un autre appui.")
    for k in ("hauteur_cm", "recul_cm"):
        if type(a.get(k)) is not int or a[k] <= 0:
            raise ErreurMonde("La hauteur et le recul disponibles doivent être établis.",
                              f"établis d'abord {support}.{k} (espace), puis re-propose ce geste.")
    return a


def preparer_usage(m, p, origine):
    from .moteur import Plan
    id, action = p["cible"], p["action"]
    o = m.objets.get(id, {})
    if not o.get("assemblage"):
        from .refus import RefusDeForme
        raise RefusDeForme("Cette opération ne s'applique pas à cette cible.",
                          f"{action}.cible = {id} : attendu un assemblage d'usage échelle ; "
                          "installer, franchir et desinstaller installent, parcourent ou retirent cet assemblage. "
                          "Pour un autre mouvement, propose l'action qui réalise ce mouvement, ou improviser ; "
                          "cette erreur de type ne dit rien de sa possibilité physique.")
    if not m.accessible(id) or not o["integrite"]:
        echelles = sorted(i for i, x in m.objets.items() if x.get("assemblage") and x.get("integrite") and m.accessible(i))
        raise ErreurMonde("Il faut une échelle accessible et en état de servir.",
                          f"cible : un assemblage accessible et intact, parmi {liste(echelles)} (reçu « {id} »).")
    from .proximite import exiger
    exiger(m, id)
    if p["methode"] != "simple" or p["difficulte"] != 0:
        raise ErreurMonde("L'installation et le passage utilisent la méthode simple et une difficulté fixée par les appuis.",
                          f"{action} : methode simple, difficulte 0.")
    plan = Plan(copy.deepcopy(p), m.data["revision"], "", origine=origine)
    if action == "installer":
        if o.get("installation"):
            raise ErreurMonde("Cette échelle est déjà installée ; retire-la d'abord.",
                              f"{id} est déjà contre {o['installation'].get('support')} : franchir pour passer, ou "
                              "desinstaller (soulever) avant de la déplacer.")
        a = appui(m, p["outil"])
        exiger(m, p["outil"])
        if not m.accessible(p["outil"]) or m.joueur["salle"] not in (a["bas"], a["haut"]):
            raise ErreurMonde("Il faut atteindre le pied ou le sommet de cet appui.",
                              f"installer contre {p['outil']} depuis {a['bas']} ou {a['haut']} ; le joueur est en {m.joueur['salle']}.")
        if m.joueur["salle"] == a["haut"] and not a.get("prise_sommet"):
            raise ErreurMonde("Il manque une prise au sommet pour abaisser cet assemblage.",
                              f"installer contre {p['outil']} depuis le pied ({a['bas']}).")
        from .biens import a_autrui
        if a_autrui(m, id) is not None:  # Prêtée ou confiée à sa garde, elle s'emploie librement.
            raise ErreurMonde("Cette échelle appartient à autrui.", f"{id} appartient à {proprietaire(m, o)} : obtiens-la d'abord.")
        if o["masse"] > m.joueur["capacite"]:
            raise ErreurMonde("Cette structure est trop lourde pour que tu l'installes seul.",
                              f"masse {o['masse']} > capacité {m.joueur['capacite']} : impossible seul.")
        if o["longueur_cm"] ** 2 < a["hauteur_cm"] ** 2 + a["recul_cm"] ** 2:
            raise ErreurMonde("Cette échelle est trop courte pour atteindre le palier avec ce recul.",
                              f"il faut longueur_cm ≥ √(hauteur² + recul²) = {math.ceil(math.hypot(a['hauteur_cm'], a['recul_cm']))} ; "
                              f"{id} mesure {o['longueur_cm']} : une échelle plus longue, ou un autre appui.")
        plan.titre, plan.minutes = "Installer " + designer(o) + " contre " + designer(m.objets[p["outil"]]) + ".", 2
        plan.effets = [("installer_assemblage", id, p["outil"])]
        return plan
    if p["outil"]:
        raise ErreurMonde("Cette action ne demande aucun outil supplémentaire.", f"{action} : outil vide.")
    support = o.get("installation", {}).get("support")
    a = appui(m, support)
    if o["lieu"] != a["bas"] or m.joueur["salle"] not in (a["bas"], a["haut"]):
        raise ErreurMonde("Cette installation n'est pas accessible depuis ici.",
                          f"{id} se rejoint depuis {a['bas']} ou {a['haut']} ; le joueur est en {m.joueur['salle']}.")
    if action == "desinstaller":
        from .biens import a_autrui
        if a_autrui(m, id) is not None or o.get("attache"):
            raise ErreurMonde("Cette structure n'est pas libre de ses attaches ou ne t'appartient pas.",
                              f"{id} est attachée ou à autrui : rien à desinstaller.")
        if o["masse"] > m.joueur["capacite"]:
            raise ErreurMonde("Cette structure est trop lourde pour être soulevée seul.",
                              f"masse {o['masse']} > capacité {m.joueur['capacite']} : impossible seul.")
        if m.joueur["salle"] == a["haut"] and not a.get("prise_sommet"):
            raise ErreurMonde("Le sommet n'offre pas de prise pour remonter cette structure.",
                              f"desinstaller {id} depuis le pied ({a['bas']}).")
        plan.titre = "Retirer " + designer(o) + " de son appui et la laisser au sol."
        if m.joueur["salle"] == a["haut"]:
            plan.titre = "Soulever " + designer(o) + " et la remonter sur le palier."
        plan.effets = [("retirer_assemblage", id, None)]
    else:
        if o["integrite"] < o["maximum"]:
            raise ErreurMonde("L'assemblage est endommagé ; ses appuis ne permettent plus ce passage.",
                              f"{id} est endommagée : plus de franchissement possible avec elle.")
        if o["longueur_cm"] ** 2 < a["hauteur_cm"] ** 2 + a["recul_cm"] ** 2:
            raise ErreurMonde("L'échelle n'atteint plus le palier.", f"{id} est trop courte pour {support}.")
        poids = m.joueur.get("masse_kg")
        if not isinstance(poids, (int, float)) or isinstance(poids, bool) or not math.isfinite(poids) or poids <= 0:
            raise ErreurMonde("Le poids du personnage doit être établi avant d'évaluer la charge.",
                              "établis d'abord joueur.masse_kg (mode enrichir_joueur), puis re-propose franchir.")
        if poids + m.charge() > o["charge_jeu_kg"]:
            raise ErreurMonde("Ton poids et ton équipement dépassent la charge retenue pour cet assemblage.",
                              f"poids {poids} + charge {m.charge()} > {o['charge_jeu_kg']:g} kg : pose d'abord des affaires.")
        destination = a["haut"] if m.joueur["salle"] == a["bas"] else a["bas"]
        plan.titre = ("Monter par " if destination == a["haut"] else "Redescendre par ") + designer(o) + "."
        plan.stat, plan.dd = "DEX", 10
        plan.risque = "En cas d'échec, tu renonces au passage et restes de ton côté, sans chute simulée."
        arrivee = None
        if m.data.get("mode_cases"):
            from .spatial import destination_appui
            arrivee = destination_appui(m, support, destination)
        plan.effets = [("voyager", destination, arrivee)]
    return plan


def prelever(m, id, longueur):
    o = m.objets[id]
    avant = o["longueur_cm"]
    if not 0 < longueur <= avant:
        raise ErreurMonde("La quantité disponible a changé.")
    masse = o["masse"] * longueur / avant
    from .matiere import fixer_longueur
    fixer_longueur(o, avant - longueur)
    o["masse"] = max(0, o["masse"] - masse)
    if not o["longueur_cm"]:
        o["incorpore"] = True
        o["mobile"] = False
    return masse


def appliquer(m, effet, lignes):
    op, cible, valeur = effet
    if op == "assembler":
        p, b = valeur["proposition"], valeur["bilan"]
        id = "assemblage_" + str(m.data["revision"] + 1)
        if id in m.objets:
            raise ErreurMonde("Un assemblage porte déjà cet identifiant.")
        masse = 0
        entiers = []
        for source, longueur in b["consommes"].items():
            masse += prelever(m, source, longueur)
            if m.objets[source].get("incorpore"):
                entiers.append(source)
        montant, lien = m.objets[p["montants"][0]], m.objets[p["lien"]]
        matiere = montant.get("physique", {}).get("matiere") or montant.get("materiau") or "bois"
        materiaux = " et ".join(dict.fromkeys(x for x in (matiere, lien.get("materiau")) if x))
        o = objet(id, "échelle", "assemblage", m.joueur["salle"],
                  aliases=["echelle", "échelle", "assemblage"], genre="f", mobile=True,
                  proprietaire="joueur", masse=round(masse, 6), materiau=materiaux,
                  assemblage="barreaux", longueur_cm=b["longueur_cm"], largeur_cm=b["largeur_cm"],
                  barreaux=b["barreaux"], charge_jeu_kg=b["charge_jeu_kg"],
                  composants=copy.deepcopy(b["consommes"]), arbitrage=b["cle"])
        placer(o, m.joueur["salle"], m.joueur["position"])
        m.objets[id] = o
        from .deplacement_objet import deplacer
        for source in entiers:
            deplacer(m, source, id)
        lignes.append(f"Tu fabriques une échelle de {b['longueur_cm'] / 100:g} m et {b['barreaux']} barreaux, puis la poses au sol. Les matériaux employés ont été prélevés.")
        if b.get("rythme") == "soigne":
            lignes.append(f"Tu y consacres {b['minutes']} minutes de travail soigné, sans jet de dés.")
    elif op == "decouper":
        decouper(m, cible, valeur["longueur"], valeur["morceau"])
        lignes.append(f"Tu coupes {designer(m.objets[cible])} : un morceau de {valeur['longueur']} cm s'en détache.")
    elif op == "perdre_lien":
        prelever(m, cible, valeur)
        lignes.append("Deux mètres de lien sont perdus dans les essais d'assemblage ; aucune échelle n'est créée.")
    elif op == "installer_assemblage":
        o = m.objets[cible]
        o["installation"] = {"support": valeur}
        from .geometrie import position_entree
        destination = m.objets[valeur]["appui_vertical"]["bas"]
        if m.data.get("mode_cases"):
            from .spatial import destination_appui
            position = destination_appui(m, valeur, o["lieu"])
        else:
            position = position_entree(m, destination)
        from .deplacement_objet import deplacer
        deplacer(m, cible, destination, position)
        lignes.append("Tu appuies " + designer(o) + " contre " + designer(m.objets[valeur]) + ". Le palier est désormais atteignable par cet assemblage.")
    elif op == "retirer_assemblage":
        o = m.objets[cible]
        o.pop("installation", None)
        from .deplacement_objet import deplacer
        deplacer(m, cible, m.joueur["salle"])
        lignes.append("Tu retires l'échelle de son appui et la poses au sol. Le passage vertical disparaît.")


def dossier(m):
    ressources, assemblages, appuis, inconnues = [], [], [], []
    for o in m.objets.values():
        if not m.accessible(o["id"]):
            continue
        if o.get("ressource"):
            ressources.append(o["id"])
            inconnues.extend(f"{o['id']}.{k}" for k in ("longueur_cm", "charge_jeu_kg") if k not in o)
        if o.get("assemblage"):
            assemblages.append(o["id"])
        if o.get("appui_vertical"):
            appuis.append(o["id"])
    if not (ressources or assemblages or appuis):
        return None
    from .moteur import Moteur, proposition
    from .operations import etape, sequence

    manoeuvres = []
    for id in assemblages:
        o = m.objets[id]
        support = (o.get("installation") or {}).get("support")
        installables, enchainables = [], []
        passage = False
        if support:
            try:
                preparer_usage(m, proposition("franchir", id), "dossier")
                passage = True
            except ErreurMonde:
                pass
        else:
            for appui_id in appuis:
                try:
                    preparer_usage(m, proposition("installer", id, appui_id), "dossier")
                except ErreurMonde:
                    continue
                installables.append(appui_id)
                enchainement = sequence(etape("appuyer", id, outil=appui_id),
                                        etape("franchir", id))
                try:
                    Moteur(m).preparer(enchainement, "dossier")
                    enchainables.append(appui_id)
                except ErreurMonde:
                    pass
        manoeuvres.append({"echelle": id, "installation": support,
                           "installer_sur": installables,
                           "installer_puis_franchir": enchainables,
                           "franchir_maintenant": passage})
    suggestion = None
    perches = [i for i in ressources if m.objets[i].get("ressource") == "perche"]
    liens = [i for i in ressources if m.objets[i].get("ressource") == "lien"]
    outils = [o["id"] for o in m.objets.values() if m.accessible(o["id"]) and m.est_porte(o["id"]) and "couper_bois" in o.get("usages", [])]
    if len(perches) >= 3 and liens and outils:
        p = fabrication(perches[:2], perches[2], liens[0], outils[0],
                        min(300, *(int(m.objets[i].get("longueur_cm", 0)) for i in perches[:2])))
        try:
            b = calculer(m, p)
            suggestion = {"proposition": p, "barreaux": b["barreaux"], "minutes": b["minutes"],
                          "charge_jeu_kg": b["charge_jeu_kg"], "consommation_cm": b["consommes"],
                          "lien_disponible_cm": m.objets[p["lien"]]["longueur_cm"],
                          "lien_restant_apres_fabrication_cm": m.objets[p["lien"]]["longueur_cm"] - b["consommes"][p["lien"]],
                          "arbitrage_memorise": b["memorise"]}
            soin = {**p, "rythme": "soigne", "difficulte": 0}
            raison = obstacle_soin(m, b["minutes"] * 2)
            suggestion["travail_soigne"] = {"obstacle": raison} if raison else {
                "proposition": soin, "minutes": b["minutes"] * 2, "jet": False,
                "consommation_cm": b["consommes"],
                "raison": "Du temps supplémentaire remplace le jet ; les contraintes matérielles restent identiques."}
        except ErreurMonde as exc:
            suggestion = {"obstacle": str(exc)}
    return {"ressources": ressources, "assemblages": assemblages, "appuis": appuis,
            "manoeuvres": manoeuvres,
            "inconnues": inconnues, "suggestion": suggestion,
            "regle": "Charges et difficultés : conventions de jeu. Aucun objet créé avant résolution. Ne complète pas silencieusement une mesure inconnue."}


def verifier(m):
    for id, o in m.objets.items():
        if o.get("ressource"):
            assert type(o.get("longueur_cm", 0)) in (int, float) and o.get("longueur_cm", 0) >= 0, "Longueur de matériau invalide"
        if o.get("assemblage"):
            assert o["assemblage"] == "barreaux", "Profil d'assemblage inconnu"
            assert 100 <= o["longueur_cm"] <= 500 and 25 <= o["largeur_cm"] <= 60, "Dimensions d'assemblage invalides"
            assert o["barreaux"] > 0 and o["charge_jeu_kg"] > 0 and o["masse"] > 0, "Structure invalide"
            assert all(i in m.objets and n > 0 for i, n in o["composants"].items()), "Origine des matériaux inconnue"
        if o.get("installation"):
            assert o.get("assemblage"), "Installation sans structure"
            a = m.objets[o["installation"]["support"]]["appui_vertical"]
            assert o["lieu"] == a["bas"], "Installation déplacée sans retrait préalable"
            assert a["haut"] in m.data["salles"], "Palier inconnu"


def preparer_decoupe(m, p, origine):
    """Couper une pièce à une longueur : un morceau à part, le reste raccourci."""
    from .moteur import Plan
    from .proximite import exiger
    from .refus import inaccessible, portes_avec_usage
    if not isinstance(p, dict) or set(p) != set(SCHEMA_DECOUPE["required"]):
        raise ErreurMonde("Découpe mal formée.", f"decouper a exactement les champs {', '.join(SCHEMA_DECOUPE['required'])}.")
    cible, outil, longueur = p["cible"], p["outil"], p["longueur_cm"]
    if not m.accessible(cible):
        raise inaccessible(m, cible)
    exiger(m, cible)
    o = m.objets[cible]
    physique = o.get("physique")
    if not physique:
        raise ErreurMonde(designer(o, debut=True) + " n'est pas encore décrit.",
                          f"décris d'abord {cible} (etablir_faits, qualification avec physique), puis decouper.")
    if physique["forme"] not in ("barre", "lien"):
        raise ErreurMonde("Seule une barre ou un lien se coupe à longueur.", f"{cible} est une {physique['forme']}.")
    if physique["pieces"] > 1:
        raise ErreurMonde(designer(o, debut=True) + " forme un lot.", f"prélève d'abord une pièce de {cible} (prelever).")
    if o.get("attache") or o.get("incorpore") or proprietaire(m, o) not in (None, "joueur"):
        raise ErreurMonde("Tu ne disposes pas librement de " + designer(o) + ".",
                          f"{cible} est attaché, incorporé ou à autrui : obtiens-le ou détache-le d'abord.")
    total = physique["dimensions"]["longueur_cm"]
    if type(longueur) is not int or not 5 <= longueur <= total - 5:
        raise ErreurMonde("Cette longueur ne se coupe pas dans cette pièce.",
                          f"longueur_cm de 5 à {total - 5} : {cible} mesure {total} cm.")
    usages = {"couper_bois"} if physique["forme"] == "barre" else {"couper", "couper_bois"}
    t = m.objets.get(outil)
    if not t or t["lieu"] != "joueur" or not t.get("integrite") or not usages & set(t.get("usages", [])):
        tranchants = sorted(set().union(*(portes_avec_usage(m, u) for u in usages)))
        raise ErreurMonde("Il faut un outil adapté pour couper " + designer(o) + ".",
                          f"outil : un objet en main d'usage {' ou '.join(sorted(usages))}, parmi {', '.join(tranchants) or 'aucun'}.")
    if eclairage(m)["niveau"] < 2:
        raise ErreurMonde("Il faut assez de lumière pour couper à la bonne longueur.",
                          "decouper exige une lumière franche : allume d'abord une source.")
    from .matiere import id_piece
    plan = Plan(copy.deepcopy(p), m.data["revision"],
                f"Couper {designer(o)} à {longueur} cm avec {designer(t)}.", origine=origine)
    plan.minutes, plan.bruit = (5 if physique["forme"] == "barre" else 1), 2
    plan.effets = [("decouper", cible, {"longueur": longueur, "morceau": id_piece(m, cible)})]
    return plan


def decouper(m, cible, longueur, morceau_id):
    """Le morceau coupé devient un objet décrit ; la pièce d'origine garde le reste."""
    from .matiere import deduire, fixer_longueur
    o = m.objets[cible]
    total = o["physique"]["dimensions"]["longueur_cm"]
    masse = round(o["masse"] * longueur / total, 3)
    morceau = objet(morceau_id, "morceau de " + o["nom"], o["type"], o["lieu"], aliases=["morceau"],
                    genre="m", materiau=o["materiau"], masse=masse, mobile=True,
                    physique={**o["physique"], "dimensions": {**o["physique"]["dimensions"], "longueur_cm": longueur}})
    for cle in ("usages", "proprietaire", "position", "position_salle", "seuil_coupe", "duree_combustion"):
        if cle in o:
            morceau[cle] = list(o[cle]) if isinstance(o[cle], list) else o[cle]
    deduire(morceau)
    m.objets[morceau_id] = morceau
    o["masse"] = round(o["masse"] - masse, 3)
    fixer_longueur(o, total - longueur)
    return morceau
