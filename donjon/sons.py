"""Émissions vocales et audition discrète sur les connexions réellement établies."""
import heapq

from .monde import ErreurMonde
from .francais import designer
from .esprits import entendre


VOIX = {
    "appel": ("Appeler à l'aide.", "Tu cries à l'aide.", 3),
    "cri": ("Pousser un cri.", "Tu pousses un cri.", 3),
    "sifflement": ("Siffler.", "Tu émets un sifflement.", 2),
}



def liens(m):
    """Passages du son entre salles : une ouverture coûte 1, une porte fermée 2."""
    resultat = {id: [] for id in m.data["salles"]}
    for id, salle in m.data["salles"].items():
        for sortie in salle["sorties"].values():
            porte = m.objets.get(sortie.get("porte"), {})
            cout = 2 if porte and not porte.get("ouverte") else 1
            destination = sortie["vers"]
            resultat[id].append((destination, cout))
            resultat[destination].append((id, cout))
    # Un appui vertical donne aussi sur son palier, même sans échelle installée.
    for o in m.objets.values():
        a = o.get("appui_vertical", {})
        bas, haut = a.get("bas"), a.get("haut")
        if bas in resultat and haut in resultat:
            resultat[bas].append((haut, 1))
            resultat[haut].append((bas, 1))
    return resultat


def portee(m, source, intensite):
    """Une ouverture coûte 1, une porte fermée 2 ; pas de son entre lieux non reliés."""
    liens_salles = liens(m)
    distances, file = {source: 0}, [(0, source)]
    while file:
        cout, lieu = heapq.heappop(file)
        if cout != distances[lieu]:
            continue
        for destination, perte in liens_salles[lieu]:
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
            raise ErreurMonde("Un son d'objet ne demande ni destination ni outil imposé.",
                              "emettre_son avec un objet : destination et outil vides, methode simple, difficulte 0.")
        id = e["cible"]
        o = m.objets[id]
        from .proximite import exiger
        if not m.accessible(id):
            from .refus import inaccessible
            raise inaccessible(m, id)
        exiger(m, id)
        if o["integrite"] <= 0:
            raise ErreurMonde("Cet objet ne peut pas produire ce son.", f"{id} est brisé.")
        from .capacites_objet import statut as statut_capacite, absence as absence_capacite
        etat = statut_capacite(o, "son")
        if etat == "inconnue":
            from .moteur import QualificationRequise
            raise QualificationRequise(id, "son")
        if etat == "ecartee":
            raise ErreurMonde(absence_capacite(o, "son") + ".",
                              f"{id} ne produit pas de son (qualification établie) : ne re-propose pas ce son.")
        p = Plan({"action": "composer", "justification": justification}, m.data["revision"],
                 "Produire un son avec " + designer(o) + ".", origine=origine)
        p.minutes, p.bruit = 1, o["sonorite"]
        p.effets = [("emettre_son", id, "objet")]
        return p
    if e["methode"] == "heler":
        return _compiler_heler(m, e, justification, origine)
    if (e["cible"] not in ("", "joueur") or e["destination"] or e["outil"]
            or e["methode"] not in VOIX or e["difficulte"]):
        raise ErreurMonde("Une émission vocale vient du joueur, sans outil ni destination imposée : appel, cri ou sifflement.",
                          f"emettre_son vocal : cible vide ou joueur, destination et outil vides, difficulte 0, methode parmi "
                          f"{', '.join(VOIX)} (reçu cible « {e['cible']} », methode « {e['methode']} ») ; pour un objet : "
                          "cible = son identifiant, methode simple.")
    if m.joueur.get("peut_parler") is False or m.joueur["pv"] <= 0:
        raise ErreurMonde("Tu n'es pas en état d'émettre cet appel.",
                          "le joueur ne peut pas émettre de son vocal : improviser un son corporel (corps_bref, corps_rythmique).")
    titre, _, intensite = VOIX[e["methode"]]
    p = Plan({"action": "composer", "justification": justification}, m.data["revision"], titre, origine=origine)
    p.minutes, p.bruit = 1, intensite
    p.effets = [("emettre_son", "joueur", e["methode"])]
    return p


HELER = 30   # dixièmes de seconde : crier un nom


def _compiler_heler(m, e, justification, origine):
    """Héler quelqu'un par son nom (``pnj.heler``) : un cri qui porte comme un appel, par la même
    règle que pour un PNJ ; qui en saisit les mots y répond (``pnj.repondre``). On ne hèle que
    quelqu'un que Corvus connaît (``paroles._connu_du_joueur``), présent ou non."""
    from .moteur import Plan
    from .paroles import _connu_du_joueur
    from .refus import liste
    qui = e["cible"]
    if e["destination"] or e["outil"] or e["difficulte"]:
        raise ErreurMonde("On hèle quelqu'un de sa voix, sans rien d'autre.",
                          "emettre_son heler : cible = l'identifiant du personnage hélé ; destination et outil vides, "
                          "difficulte 0.")
    connus = sorted(i for i, o in m.objets.items() if o["type"] == "personnage" and _connu_du_joueur(m, i))
    if qui in ("", "joueur"):
        raise ErreurMonde("Dis qui tu appelles par son nom.",
                          f"emettre_son heler : cible = l'identifiant du personnage hélé, pas joueur ; parmi "
                          f"{liste(connus)} (reçu « {qui} »).")
    if qui not in m.objets or m.objets[qui]["type"] != "personnage" or not _connu_du_joueur(m, qui):
        raise ErreurMonde("Tu ne connais personne de ce nom à appeler.",
                          f"emettre_son heler : cible = un personnage que Corvus connaît, parmi {liste(connus)} "
                          f"(reçu « {qui} »).")
    if m.joueur.get("peut_parler") is False or m.joueur["pv"] <= 0:
        raise ErreurMonde("Tu n'es pas en état d'appeler qui que ce soit.",
                          "le joueur ne peut pas émettre de son vocal : improviser un son corporel (corps_bref, "
                          "corps_rythmique).")
    p = Plan({"action": "composer", "justification": justification}, m.data["revision"],
             "Appeler " + designer(m.objets[qui]) + " par son nom.", origine=origine)
    p.minutes, p.dixiemes, p.effort = 0, HELER, False
    p.effets = [("heler", "joueur", qui)]
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
    # Historique borné ; chaque PNJ garde aussi le son dans sa propre mémoire.
    m.data.setdefault("sons", []).append(evenement)
    m.data["sons"] = m.data["sons"][-40:]
    lignes.append(texte)
    for id in entendants:
        pnj = m.objets[id]
        pnj["humeur"] = "méfiant" if m.data["relations_pnj"].get(id, {}).get("soupcon") else "inquiet"
        entendre(m, id, evenement, niveaux[pnj["lieu"]])
        if m.visible(id):
            entendu = ("le son de " + designer(m.objets[emetteur]) + "." if emetteur != "joueur" else
                       "ton " + ("appel à l'aide." if mode == "appel" else "cri." if mode == "cri" else "sifflement."))
            lignes.append(designer(pnj, debut=True) + " entend " + entendu)
    # Les déplacements déclarés et l'absence de réponse sont résolus après l'avancée du temps.
