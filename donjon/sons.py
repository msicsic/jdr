"""Émissions vocales et audition discrète sur les connexions réellement établies."""
import heapq

from .monde import ErreurMonde
from .francais import designer
from .pnj import reagir


VOIX = {
    "appel": ("Appeler à l'aide.", "Tu cries à l'aide.", 3),
    "cri": ("Pousser un cri.", "Tu pousses un cri.", 3),
    "sifflement": ("Siffler pour se signaler.", "Tu émets un sifflement.", 2),
}

REGLES = """
SONS : crier, appeler à l'aide, siffler et faire sonner un objet sonore sont possibles, sans jet.
Compose emettre_son avec cible joueur, destination et outil vides, difficulte 0 ;
methode appel pour appeler à l'aide/au secours, cri pour un cri, sifflement pour siffler.
Pour un objet ayant une sonorite dans les faits, cible = son identifiant, methode simple,
destination et outil vides. Le moteur vérifie la proximité, l'intégrité et l'audition.
« Je crie à l'aide » = une étape emettre_son(joueur,appel). Ce n'est pas une conversation
avec un PNJ absent ni une impossibilité. Le moteur produit le son, détermine qui peut
l'entendre et conserve ce souvenir. Une réponse, une arrivée ou un déplacement de PNJ n'est
affirmé que si les faits l'établissent. L'absence de PNJ visible n'empêche pas
d'appeler ; n'affirme pas non plus que personne n'existe aux alentours. Une question sur
ce qui se passerait reste un dialogue. Ces opérations se combinent aux autres gestes.
"""


def portee(m, source, intensite):
    """Une ouverture coûte 1, une porte fermée 2 ; pas de son entre lieux non reliés."""
    liens = {id: [] for id in m.data["salles"]}
    for id, salle in m.data["salles"].items():
        for sortie in salle["sorties"].values():
            porte = m.objets.get(sortie.get("porte"), {})
            cout = 2 if porte and not porte.get("ouverte") else 1
            destination = sortie["vers"]
            liens[id].append((destination, cout))
            liens[destination].append((id, cout))
    # Un appui vertical donne aussi sur son palier, même sans échelle installée.
    for o in m.objets.values():
        a = o.get("appui_vertical", {})
        bas, haut = a.get("bas"), a.get("haut")
        if bas in liens and haut in liens:
            liens[bas].append((haut, 1))
            liens[haut].append((bas, 1))
    distances, file = {source: 0}, [(0, source)]
    while file:
        cout, lieu = heapq.heappop(file)
        if cout != distances[lieu]:
            continue
        for destination, perte in liens[lieu]:
            suivant = cout + perte
            if suivant < intensite and suivant < distances.get(destination, intensite):
                distances[destination] = suivant
                heapq.heappush(file, (suivant, destination))
    return {id: intensite - cout for id, cout in distances.items()}


def auditeurs(m, source, intensite):
    niveaux = portee(m, source, intensite)
    return [o["id"] for o in m.objets.values()
            if o["type"] == "personnage" and o["lieu"] in niveaux and o.get("entend", True)]


def compiler(m, e, justification, origine):
    from .moteur import Plan
    if e["cible"] in m.objets and e["methode"] == "simple":
        if e["destination"] or e["outil"] or e["difficulte"]:
            raise ErreurMonde("Un son d'objet ne demande ni destination ni outil imposé.")
        id = e["cible"]
        o = m.objets[id]
        from .proximite import exiger
        if not m.accessible(id):
            raise ErreurMonde("Cet objet est inaccessible depuis ici.")
        exiger(m, id)
        if o["integrite"] <= 0:
            raise ErreurMonde("Cet objet ne peut pas produire ce son.")
        from .capacites_objet import statut as statut_capacite, absence as absence_capacite
        etat = statut_capacite(o, "son")
        if etat == "inconnue":
            from .moteur import QualificationRequise
            raise QualificationRequise(id, "son")
        if etat == "ecartee":
            raise ErreurMonde(absence_capacite(o, "son") + ".")
        p = Plan({"action": "composer", "justification": justification}, m.data["revision"],
                 "Produire un son avec " + designer(o) + ".", origine=origine)
        p.minutes, p.bruit = 1, o["sonorite"]
        p.effets = [("emettre_son", id, "objet")]
        return p
    if (e["cible"] not in ("", "joueur") or e["destination"] or e["outil"]
            or e["methode"] not in VOIX or e["difficulte"]):
        raise ErreurMonde("Une émission vocale vient du joueur, sans outil ni destination imposée : appel, cri ou sifflement.")
    if m.joueur.get("peut_parler") is False or m.joueur["pv"] <= 0:
        raise ErreurMonde("Tu n'es pas en état d'émettre cet appel.")
    titre, _, intensite = VOIX[e["methode"]]
    p = Plan({"action": "composer", "justification": justification}, m.data["revision"], titre, origine=origine)
    p.minutes, p.bruit = 1, intensite
    p.effets = [("emettre_son", "joueur", e["methode"])]
    return p


def appliquer(m, emetteur, mode, lignes):
    if emetteur == "joueur":
        _, texte, intensite = VOIX[mode]
    else:
        o = m.objets[emetteur]
        intensite = o["sonorite"]
        texte = "Tu produis un son avec " + designer(o) + "."
    if emetteur == "joueur":
        source = m.joueur["salle"]
    else:
        from .perception import salle_source
        source = salle_source(m, o)
    niveaux = portee(m, source, intensite)
    entendants = auditeurs(m, source, intensite)
    evenement = {"tour": m.data["revision"] + 1, "minute": m.data["minutes"],
                 "origine": source, "nature": mode, "intensite": intensite, "auditeurs": entendants}
    if emetteur != "joueur":
        evenement["objet"] = emetteur
    # Historique borné ; chaque PNJ conserve son dernier souvenir même après éviction.
    m.data.setdefault("sons", []).append(evenement)
    m.data["sons"] = m.data["sons"][-40:]
    lignes.append(texte)
    for id in entendants:
        pnj = m.objets[id]
        pnj["dernier_son_entendu"] = {k: v for k, v in evenement.items() if k != "auditeurs"}
        pnj["humeur"] = "méfiant" if m.data["relations_pnj"].get(id, {}).get("soupcon") else "inquiet"
        reagir(m, id, source, niveaux[pnj["lieu"]])
        if m.visible(id):
            entendu = ("le son de " + designer(m.objets[emetteur]) + "." if emetteur != "joueur" else
                       "ton " + ("appel à l'aide." if mode == "appel" else "cri." if mode == "cri" else "sifflement."))
            lignes.append(designer(pnj, debut=True) + " entend " + entendu)
    # Les déplacements déclarés et l'absence de réponse sont résolus après l'avancée du temps.
