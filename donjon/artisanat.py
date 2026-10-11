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

REGLES = """
FABRICATION ET INSTALLATION (conventions de jeu, pas conseils de construction réelle) :
Le dossier atelier sépare ressources connues, inconnues et assemblages possibles.
Pour une question de faisabilité, réponds en dialogue sans rien fabriquer. Explique ce qui
manque réellement. Pour une volonté de fabriquer une échelle, propose action fabriquer,
profil barreaux, deux identifiants montants distincts, un troisième dans traverses, lien,
outil, longueur_cm, largeur_cm, difficulte 10..18, justification courte (méthode et risque).
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


def ressource(m, id, nature):
    o = m.objets.get(id)
    if not o or not m.accessible(id):
        raise ErreurMonde(f"Le matériau {id} est absent ou inaccessible.")
    from .proximite import exiger
    exiger(m, id)
    if (o.get("incorpore") or o.get("attache") or not o["mobile"]
            or proprietaire(m, o) not in (None, "joueur")):
        raise ErreurMonde(f"Tu ne disposes pas librement de {designer(o)}.")
    if o.get("ressource") != nature or o["integrite"] < o["maximum"]:
        raise ErreurMonde(f"{designer(o, debut=True)} ne convient pas comme {nature} intact.")
    for champ in ("longueur_cm", "charge_jeu_kg"):
        if not isinstance(o.get(champ), (int, float)) or isinstance(o.get(champ), bool) or not math.isfinite(o[champ]) or o[champ] <= 0:
            raise ErreurMonde(f"Il manque une mesure ou une estimation établie : {id}.{champ}.")
    return o


def calculer(m, p):
    champs = set(fabrication([], "", "", ""))
    if (not isinstance(p, dict) or set(p) not in (champs, champs - {"rythme"})
            or p["action"] != "fabriquer" or p["profil"] != "barreaux"):
        raise ErreurMonde("Proposition d'assemblage invalide.")
    if (not isinstance(p["montants"], list) or len(p["montants"]) != 2
            or any(not isinstance(i, str) for i in p["montants"])
            or any(not isinstance(p[k], str) for k in ("traverses", "lien", "outil", "justification"))
            or len(p["justification"]) > 1000):
        raise ErreurMonde("Précise deux montants, les traverses, le lien et l'outil.")
    ids = [*p["montants"], p["traverses"], p["lien"], p["outil"]]
    if len(set(ids)) != 5:
        raise ErreurMonde("Chaque rôle exige une ressource distincte ; on ne peut pas compter deux fois une perche.")
    rythme = p.get("rythme", "normal")  # Compatibilité avec les propositions déjà sauvegardées.
    if rythme not in ("normal", "soigne"):
        raise ErreurMonde("Choisis une fabrication normale ou soignée.")
    for cle, bas, haut in (("longueur_cm", 100, 500), ("largeur_cm", 25, 60), ("difficulte", 0 if rythme == "soigne" else 10, 18)):
        if type(p[cle]) is not int or not bas <= p[cle] <= haut:
            raise ErreurMonde(f"{cle} doit être un entier entre {bas} et {haut}.")
    bois = [ressource(m, id, "perche") for id in ids[:3]]
    lien = ressource(m, p["lien"], "lien")
    t = m.objets.get(p["outil"], {})
    if (not m.accessible(p["outil"]) or not m.est_porte(p["outil"])
            or not t.get("integrite") or "couper_bois" not in t.get("usages", [])):
        raise ErreurMonde("Il faut tenir un outil utilisable pour couper du bois, par exemple une hache.")
    longueur, largeur = p["longueur_cm"], p["largeur_cm"]
    if any(o["longueur_cm"] < longueur for o in bois[:2]):
        raise ErreurMonde("Les montants disponibles sont trop courts pour cette longueur.")
    # Espacement maximal conventionnel de 35 cm, perte de coupe de 1 cm par barreau.
    barreaux = math.ceil(longueur / 35) - 1
    coupe = barreaux * (largeur + 1)
    liens = barreaux * 2 * 60
    if bois[2]["longueur_cm"] < coupe:
        raise ErreurMonde(f"Il faut {coupe} cm pour {barreaux} barreaux (pertes comprises), mais cette perche n'a que {bois[2]['longueur_cm']} cm. Réduis largeur ou longueur.")
    if lien["longueur_cm"] < liens:
        raise ErreurMonde(f"Il faut {liens} cm de lien pour les attaches ; il n'en reste que {lien['longueur_cm']} cm.")
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
            raise ErreurMonde(raison)
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
        raise ErreurMonde("Il faut assez de lumière pour préparer et assembler les pièces.")
    bilan = calculer(m, p)
    plan = Plan(copy.deepcopy(p), m.data["revision"],
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
        raise ErreurMonde("Il faut un appui établi reliant un sol et un palier accessible en hauteur.")
    if not a.get("sol_stable") or not a.get("sommet_stable"):
        raise ErreurMonde("Le pied et le sommet doivent offrir des appuis stables.")
    for k in ("hauteur_cm", "recul_cm"):
        if type(a.get(k)) is not int or a[k] <= 0:
            raise ErreurMonde("La hauteur et le recul disponibles doivent être établis.")
    return a


def preparer_usage(m, p, origine):
    from .moteur import Plan
    id, action = p["cible"], p["action"]
    o = m.objets.get(id, {})
    if not m.accessible(id) or not o.get("assemblage") or not o["integrite"]:
        raise ErreurMonde("Il faut une échelle accessible et en état de servir.")
    from .proximite import exiger
    exiger(m, id)
    if p["methode"] != "simple" or p["difficulte"] != 0:
        raise ErreurMonde("L'installation et le passage utilisent la méthode simple et une difficulté fixée par les appuis.")
    plan = Plan(copy.deepcopy(p), m.data["revision"], "", origine=origine)
    if action == "installer":
        if o.get("installation"):
            raise ErreurMonde("Cette échelle est déjà installée ; retire-la d'abord.")
        a = appui(m, p["outil"])
        exiger(m, p["outil"])
        if not m.accessible(p["outil"]) or m.joueur["salle"] not in (a["bas"], a["haut"]):
            raise ErreurMonde("Il faut atteindre le pied ou le sommet de cet appui.")
        if m.joueur["salle"] == a["haut"] and not a.get("prise_sommet"):
            raise ErreurMonde("Il manque une prise au sommet pour abaisser cet assemblage.")
        if proprietaire(m, o) not in (None, "joueur"):
            raise ErreurMonde("Cette échelle appartient à autrui.")
        if o["masse"] > m.joueur["capacite"]:
            raise ErreurMonde("Cette structure est trop lourde pour que tu l'installes seul.")
        if o["longueur_cm"] ** 2 < a["hauteur_cm"] ** 2 + a["recul_cm"] ** 2:
            raise ErreurMonde("Cette échelle est trop courte pour atteindre le palier avec ce recul.")
        plan.titre, plan.minutes = "Installer " + designer(o) + " contre " + designer(m.objets[p["outil"]]) + ".", 2
        plan.effets = [("installer_assemblage", id, p["outil"])]
        return plan
    if p["outil"]:
        raise ErreurMonde("Cette action ne demande aucun outil supplémentaire.")
    support = o.get("installation", {}).get("support")
    a = appui(m, support)
    if o["lieu"] != a["bas"] or m.joueur["salle"] not in (a["bas"], a["haut"]):
        raise ErreurMonde("Cette installation n'est pas accessible depuis ici.")
    if action == "desinstaller":
        if proprietaire(m, o) not in (None, "joueur") or o.get("attache"):
            raise ErreurMonde("Cette structure n'est pas libre de ses attaches ou ne t'appartient pas.")
        if o["masse"] > m.joueur["capacite"]:
            raise ErreurMonde("Cette structure est trop lourde pour être soulevée seul.")
        if m.joueur["salle"] == a["haut"] and not a.get("prise_sommet"):
            raise ErreurMonde("Le sommet n'offre pas de prise pour remonter cette structure.")
        plan.titre = "Retirer " + designer(o) + " de son appui et la laisser au sol."
        if m.joueur["salle"] == a["haut"]:
            plan.titre = "Soulever " + designer(o) + " et la remonter sur le palier."
        plan.effets = [("retirer_assemblage", id, None)]
    else:
        if o["integrite"] < o["maximum"]:
            raise ErreurMonde("L'assemblage est endommagé ; ses appuis ne permettent plus ce passage.")
        if o["longueur_cm"] ** 2 < a["hauteur_cm"] ** 2 + a["recul_cm"] ** 2:
            raise ErreurMonde("L'échelle n'atteint plus le palier.")
        poids = m.joueur.get("masse_kg")
        if not isinstance(poids, (int, float)) or isinstance(poids, bool) or not math.isfinite(poids) or poids <= 0:
            raise ErreurMonde("Le poids du personnage doit être établi avant d'évaluer la charge.")
        if poids + m.charge() > o["charge_jeu_kg"]:
            raise ErreurMonde("Ton poids et ton équipement dépassent la charge retenue pour cet assemblage.")
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


def prelever(m, id, longueur, incorporer=None):
    o = m.objets[id]
    avant = o["longueur_cm"]
    if not 0 < longueur <= avant:
        raise ErreurMonde("La quantité disponible a changé.")
    masse = o["masse"] * longueur / avant
    o["longueur_cm"] -= longueur
    o["masse"] = max(0, o["masse"] - masse)
    if not o["longueur_cm"]:
        o["incorpore"] = True
        o["mobile"] = False
        if incorporer:
            o["lieu"] = incorporer
    return masse


def appliquer(m, effet, lignes):
    op, cible, valeur = effet
    if op == "assembler":
        p, b = valeur["proposition"], valeur["bilan"]
        id = "assemblage_" + str(m.data["revision"] + 1)
        if id in m.objets:
            raise ErreurMonde("Un assemblage porte déjà cet identifiant.")
        masse = sum(prelever(m, source, longueur, id) for source, longueur in b["consommes"].items())
        o = objet(id, "échelle de branches", "assemblage", m.joueur["salle"],
                  aliases=["echelle", "échelle", "assemblage"], genre="f", mobile=True,
                  proprietaire="joueur", masse=round(masse, 6), materiau="bois et ficelle",
                  assemblage="barreaux", longueur_cm=b["longueur_cm"], largeur_cm=b["largeur_cm"],
                  barreaux=b["barreaux"], charge_jeu_kg=b["charge_jeu_kg"],
                  composants=copy.deepcopy(b["consommes"]), arbitrage=b["cle"])
        placer(o, m.joueur["salle"], m.joueur["position"])
        m.objets[id] = o
        lignes.append(f"Tu fabriques une échelle de {b['longueur_cm'] / 100:g} m et {b['barreaux']} barreaux, puis la poses au sol. Les matériaux employés ont été prélevés.")
        if b.get("rythme") == "soigne":
            lignes.append(f"Tu y consacres {b['minutes']} minutes de travail soigné, sans jet de dés.")
    elif op == "perdre_lien":
        prelever(m, cible, valeur)
        lignes.append("Deux mètres de lien sont perdus dans les essais d'assemblage ; aucune échelle n'est créée.")
    elif op == "installer_assemblage":
        o = m.objets[cible]
        o["installation"] = {"support": valeur}
        from .geometrie import position_entree
        o["lieu"] = m.objets[valeur]["appui_vertical"]["bas"]
        if m.data.get("mode_cases"):
            from .spatial import destination_appui
            position = destination_appui(m, valeur, o["lieu"])
        else:
            position = position_entree(m, o["lieu"])
        placer(o, o["lieu"], position)
        lignes.append("Tu appuies " + designer(o) + " contre " + designer(m.objets[valeur]) + ". Le palier est désormais atteignable par cet assemblage.")
    elif op == "retirer_assemblage":
        o = m.objets[cible]
        o.pop("installation", None)
        o["lieu"] = m.joueur["salle"]
        placer(o, o["lieu"], m.joueur["position"])
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
