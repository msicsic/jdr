"""Franchissement improvisé avec appui mobile : arbitrage de JDR borné.

Le MJ choisit la méthode et estime le DD ; le moteur vérifie l'obstacle et les
ressources, mémorise l'arbitrage et applique des conséquences limitées.
"""
import hashlib
import json
import math

from .monde import ErreurMonde
from .francais import designer
from .perception import eclairage
from .vol import proprietaire
from .refus import liste


REGLES = """
INITIATIVES DE FRANCHISSEMENT : l'objectif indique un but, jamais une solution imposée.
Une suggestion d'échelle est facultative. Examine la méthode du joueur, même improvisée.
Opération composée franchir_obstacle : cible=obstacle connu, destination=palier relié,
outil=objet servant d'appui mobile, methode=appui_mobile, difficulte estimée entre 16 et 22.
Le dossier franchissements expose les conditions vérifiées, obstacles et inconnues.
Une perche peut servir à tenter un saut pour franchir le mur : ce n'est ni fabriquer,
ni installer une échelle. Si elle est au sol, compose deplacer(perche,joueur) puis
franchir_obstacle(mur,palier,perche,appui_mobile,DD). Une seule confirmation pour l'ensemble.
La prise reste acquise si le saut échoue. Le moteur gère coût, chute et dommage à l'outil.
Sur réussite, le personnage atteint le palier et lâche l'appui à son pied : aucun passage
permanent ni retour garanti. Ne remplace pas cette intention par l'échelle ou une simple prise.
Explique brièvement méthode et risque dans justification. Une question sur la faisabilité
propose le même franchissement : le moteur le prépare sans l'exécuter.
L'absence de compétence spécialisée n'est pas une interdiction ; la DEX et le DD servent
à cet arbitrage. Le dossier ne garantit pas la réussite : les limites sont des règles de JDR.
"""


def installer(m):
    """Complément d'auteur des anciennes sauvegardes de la seule scène d'atelier."""
    if m.data.get("franchissements_version"):
        return
    a = m.objets.get("mur_atelier", {}).get("appui_vertical", {})
    if a.get("bas") != "cour" or a.get("haut") != "terrasse":
        return
    # Les valeurs déjà établies, même fausses ou nulles, restent prioritaires.
    a.setdefault("elan_cm", 400)
    a.setdefault("reception_stable", True)
    if m.data["scenario"].get("objectif") == "Fabriquer un accès à la terrasse, y monter puis redescendre.":
        m.data["scenario"]["objectif"] = "Atteindre la terrasse puis revenir, par les moyens de ton choix."
    m.data["franchissements_version"] = 1


def conditions(m, cible, outil, destination, tenu=True):
    o, t = m.objets.get(cible, {}), m.objets.get(outil, {})
    a = o.get("appui_vertical", {})
    def perches():
        return liste(sorted(i for i, x in m.objets.items() if m.accessible(i) and x.get("mobile")
                            and (x.get("ressource") == "perche" or "appui_mobile" in x.get("usages", []))
                            and not x.get("attache") and not x.get("installation") and not x.get("incorpore")))
    if not m.accessible(cible) or not o.get("integrite") or not a:
        obstacles = sorted(i for i, x in m.objets.items() if x.get("appui_vertical") and m.accessible(i))
        raise ErreurMonde("L'obstacle et son palier doivent être accessibles et établis.",
                          f"cible : un obstacle établi, parmi {liste(obstacles)} (reçu « {cible} ») ; un obstacle "
                          "inconnu s'établit d'abord par espace.")
    if m.joueur["salle"] != a.get("bas") or destination != a.get("haut") or destination not in m.data["salles"]:
        raise ErreurMonde("Ce mouvement part du pied de l'obstacle et mène uniquement à son palier établi.",
                          f"depuis {a.get('bas')} (le joueur est en {m.joueur['salle']}), destination = {a.get('haut')} "
                          f"(reçu « {destination} »).")
    if eclairage(m)["niveau"] < 2:
        raise ErreurMonde("Tu ne vois pas assez bien l'obstacle pour tenter ce mouvement.",
                          "ce franchissement exige une lumière franche : allume d'abord une source.")
    if not m.accessible(outil) or (tenu and not m.est_porte(outil)):
        raise ErreurMonde("Il faut d'abord prendre l'objet qui servira d'appui.",
                          f"outil : une perche portée ; étape deplacer {outil or '<perche>'} vers joueur avant, dans le "
                          f"même composer ; perches à portée : {perches()}.")
    if (not t.get("mobile") or t.get("attache") or t.get("installation") or t.get("incorpore")
            or t.get("integrite", 0) < t.get("maximum", 1)):
        raise ErreurMonde("L'appui mobile doit être libre et intact.", f"{outil} est fixé, installé ou abîmé ; perches libres : {perches()}.")
    if t.get("ressource") != "perche" and "appui_mobile" not in t.get("usages", []):
        raise ErreurMonde("Cet objet ne peut pas servir d'appui mobile long dans cet arbitrage.",
                          f"outil : une perche ou un objet d'usage appui_mobile, parmi {perches()}.")
    if proprietaire(m, t) not in (None, "joueur"):
        raise ErreurMonde("Cet objet appartient à autrui ; tu ne peux pas l'employer librement.",
                          f"{outil} appartient à {proprietaire(m, t)} : obtiens-le d'abord.")
    valeurs = {}
    for nom, source, champ in (("hauteur", a, "hauteur_cm"), ("elan", a, "elan_cm"),
                               ("longueur", t, "longueur_cm"), ("charge", t, "charge_jeu_kg"),
                               ("poids", m.joueur, "masse_kg")):
        x = source.get(champ)
        if type(x) not in (int, float) or not math.isfinite(x) or x <= 0:
            porteur = "joueur" if source is m.joueur else (outil if source is t else cible)
            raise ErreurMonde(f"Il manque une donnée établie pour apprécier la tentative : {champ}.",
                              f"établis d'abord {porteur}.{champ} ("
                              + ("mode enrichir_joueur" if porteur == "joueur" else "mode etablir_faits") + "), puis re-propose.")
        valeurs[nom] = x
    if a.get("sol_stable") is not True or a.get("reception_stable") is not True:
        raise ErreurMonde("Il faut un sol d'élan et une zone de réception établis comme stables.",
                          f"{cible} n'offre pas d'élan ou de réception stables : un autre moyen (échelle, autre obstacle).")
    if valeurs["elan"] < 300:
        raise ErreurMonde("L'espace d'élan disponible est trop court pour cette tentative.",
                          f"élan {valeurs['elan']:g} cm < 300 cm : un autre moyen (échelle, autre obstacle).")
    if valeurs["hauteur"] > 300 or valeurs["longueur"] < valeurs["hauteur"] + 30:
        raise ErreurMonde("L'obstacle est trop haut ou l'appui trop court pour cette méthode.",
                          f"hauteur {valeurs['hauteur']:g} cm (300 au plus) ; appui d'au moins hauteur + 30 = "
                          f"{valeurs['hauteur'] + 30:g} cm ({outil} : {valeurs['longueur']:g}).")
    charge = m.charge() + (0 if m.est_porte(outil) else t["masse"])
    if charge > m.joueur["capacite"]:
        raise ErreurMonde("Tu ne peux pas porter cet appui avec ton équipement actuel.",
                          f"charge {charge} > capacité {m.joueur['capacite']} : pose d'abord des affaires.")
    if (valeurs["poids"] + charge) * 1.25 > valeurs["charge"]:
        raise ErreurMonde("L'appui est trop faible pour la charge dynamique retenue dans cet arbitrage.",
                          f"(poids {valeurs['poids']:g} + charge {charge}) × 1,25 > {valeurs['charge']:g} kg admis par {outil} : "
                          "allège-toi ou un appui plus solide.")
    valeurs["charge_portee"] = charge
    return a, valeurs


def compiler(m, e, justification, origine):
    from .moteur import Plan
    if e["methode"] != "appui_mobile" or not 16 <= e["difficulte"] <= 22:
        raise ErreurMonde("Un franchissement avec appui mobile exige une difficulté entre 16 et 22.",
                          f"franchir_obstacle : methode appui_mobile, difficulte 16 à 22 (reçu « {e['methode']} », {e['difficulte']}).")
    a, valeurs = conditions(m, e["cible"], e["outil"], e["destination"])
    from .proximite import exiger
    exiger(m, e["cible"])
    p = Plan({"action": "composer", "justification": justification}, m.data["revision"],
             "Tenter de franchir " + designer(m.objets[e["cible"]]) + " en prenant appui sur " + designer(m.objets[e["outil"]]) + ".", origine=origine)
    signature = {"version": 1, "methode": e["methode"], "obstacle": e["cible"],
                 "destination": e["destination"], "valeurs": valeurs,
                 "matiere": m.objets[e["outil"]]["materiau"], "appuis": a}
    p.cle_arbitrage = "franchissement:" + hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    precedent = m.data["arbitrages"].get(p.cle_arbitrage)
    p.stat, p.dd = "DEX", precedent["dd"] if precedent else e["difficulte"]
    if precedent:
        p.origine = "arbitrage mémorisé"
        p.proposition["justification"] = precedent["justification"]
    p.minutes, p.bruit = 1, 2
    degats = max(1, math.ceil(valeurs["hauteur"] / 100))
    p.risque = (f"En cas d'échec, tu restes au pied du mur et perds {degats} PV. "
                "Sur un 1 naturel, l'appui subit aussi un dommage. "
                "Réussite ou échec : tu lâches l'appui au pied du mur. Aucun passage de retour n'est créé.")
    arrivee = None
    if m.data.get("mode_cases"):
        from .spatial import destination_appui
        arrivee = destination_appui(m, e["cible"], e["destination"])
    p.effets = [("transferer", e["outil"], a["bas"]), ("voyager", e["destination"], arrivee)]
    p.echec = [("transferer", e["outil"], a["bas"]), ("blessure_franchissement", "joueur", degats)]
    p.echec_critique = [("endommager", e["outil"], 1)]
    return p


def dossier(m):
    obstacles = [o for o in m.objets.values() if m.accessible(o["id"]) and o.get("appui_vertical")]
    outils = [o for o in m.objets.values() if m.accessible(o["id"]) and
              (o.get("ressource") == "perche" or "appui_mobile" in o.get("usages", []))]
    if not obstacles:
        return None
    candidats = []
    for o in obstacles[:3]:
        for t in outils[:4]:
            entree = {"obstacle": o["id"], "outil": t["id"], "destination": o["appui_vertical"].get("haut"),
                      "methode": "appui_mobile", "prendre_avant": not m.est_porte(t["id"])}
            try:
                _, valeurs = conditions(m, o["id"], t["id"], entree["destination"], tenu=False)
                entree.update(conditions_verifiees=valeurs, difficulte="DEX 16..22 à estimer ; pas de réussite garantie")
            except ErreurMonde as exc:
                entree["obstacle_physique_ou_inconnue"] = str(exc)
            candidats.append(entree)
    return {"possibilites": candidats, "but": "Atteindre un lieu existant, sans imposer de fabrication.",
            "cadre": "Arbitrage de JDR : élan minimal 3 m, hauteur maximale 3 m, appui dépassant la hauteur de 30 cm, marge de charge dynamique 25 %. Le MJ estime la difficulté dans ce cadre."}
