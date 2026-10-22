"""Émissions du joueur : appel à l'aide, cri, sifflement, son d'un objet, héler, répondre.

Elles retentissent par l'ouïe commune (``ouie.retentir``, depuis ``moteur``) : leur nature y est
déclarée une fois (``ouie.NATURES`` pour la voix, ``ouie.SONS`` selon la ``sonorite`` d'un objet).
Qui l'entend l'interprète comme tout bruit (se retourner, retenir un bruit vers ce lieu, aller voir
selon son devoir, son courage ou son seuil d'alerte). ``data["sons"]`` garde l'historique de ce qui
a été émis et de qui l'a entendu.
"""
from .monde import ErreurMonde
from .refus import RefusDeForme
from .francais import designer


VOIX = {
    "appel": ("Appeler à l'aide.", "Tu cries à l'aide.", 3),
    "cri": ("Pousser un cri.", "Tu pousses un cri.", 3),
    "sifflement": ("Siffler.", "Tu émets un sifflement.", 2),
}



def entendants(m, n):
    """Les personnages qui entendraient maintenant un bruit de nature ``n`` (``ouie``) venu du joueur :
    l'ouïe commune, la même pour tous (distance réelle, passages, portes, seuil de chacun)."""
    from .esprits import pnjs
    from .ouie import entend
    return [id for id in pnjs(m) if entend(m, "joueur", id, force=n) is not None]


def nature_emise(m, effets):
    """La nature du bruit qu'émettent ces effets, selon l'ouïe commune (``ouie.NATURES``, ``ouie.SONS``) ;
    None s'ils n'émettent rien de déclaré."""
    from .ouie import SONS, nature
    for op, cible, valeur in effets:
        if op == "emettre_son":
            return SONS[m.objets[cible]["sonorite"]] if cible in m.objets else nature(valeur)
        if op == "son_improvise":
            return SONS[valeur["intensite"]]
    return None


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
    from .appel import METHODES as REPONSES
    if e["methode"] in REPONSES:
        return _compiler_repondre(m, e, justification, origine)
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
        raise RefusDeForme("On hèle quelqu'un de sa voix, sans rien d'autre.",
                          "emettre_son heler : cible = l'identifiant du personnage hélé ; destination et outil vides, "
                          "difficulte 0.")
    connus = sorted(i for i, o in m.objets.items() if o["type"] == "personnage" and _connu_du_joueur(m, i))
    if qui in ("", "joueur"):
        raise RefusDeForme("Dis qui tu appelles par son nom.",
                          f"emettre_son heler : cible = l'identifiant du personnage hélé, pas joueur ; parmi "
                          f"{liste(connus)} (reçu « {qui} ») ; sans nom à appeler, des mots lancés à qui les entend "
                          "sont une parole (parole_joueur, personnage = parole_prevue.personnage), un cri sans mots "
                          "emettre_son methode cri.")
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


def _compiler_repondre(m, e, justification, origine):
    """Répondre à qui vient de héler Corvus par son nom, ou de lui demander ce qu'il veut, ou de lui dire
    ce qu'il veut (``appel.en_attente``) : « Ici, viens ! » (methode repondre), « J'arrive ! » (arriver),
    « Qu'est-ce que tu veux ? » (demander_raison), par la règle des PNJ (``appel``) ; un cri. À son nom,
    il se nomme : l'appelant qui l'entend le croit là. La cible est l'appelant, sous le nom que Corvus
    lui connaît (une voix inconnue : voix_<n>)."""
    from .appel import METHODES as REPONSES, en_attente, permises
    from .moteur import Plan
    from .refus import liste
    from .voix import designation, reel
    attendent = dict(en_attente(m))
    appelants = list(attendent)
    valables = [designation(m, x) for x in appelants]
    methode = e["methode"]
    if e["destination"] or e["outil"] or e["difficulte"]:
        raise ErreurMonde("On répond de sa voix, sans rien d'autre.",
                          f"emettre_son {methode} : cible = qui vient d'appeler Corvus par son nom ; destination et "
                          "outil vides, difficulte 0.")
    if not appelants:
        raise ErreurMonde("Personne ne vient de t'appeler par ton nom.",
                          f"emettre_son {methode} : seulement juste après un appel de Corvus par son nom ; aucun appel "
                          f"de ce genre ne vient de lui parvenir (reçu cible « {e['cible']} »).")
    qui = reel(m, e["cible"])
    if qui not in appelants:
        raise ErreurMonde("Ce n'est pas cette voix qui vient de t'appeler.",
                          f"emettre_son {methode} : cible = qui vient d'appeler Corvus, parmi {liste(valables)} "
                          f"(reçu « {e['cible']} »).")
    if REPONSES[methode] not in permises(attendent[qui]):
        raise ErreurMonde("Tu sais déjà ce qu'on te veut : dis si tu viens ou s'il doit venir.",
                          f"emettre_son {methode} : après « Qu'est-ce que tu veux ? » ou ce que l'appelant veut, "
                          "methode arriver (Corvus vient) ou repondre (l'autre vient) ; demander_raison seulement à un "
                          "appel par son nom.")
    if m.joueur.get("peut_parler") is False or m.joueur["pv"] <= 0:
        raise ErreurMonde("Tu n'es pas en état de répondre.",
                          "le joueur ne peut pas émettre de son vocal : improviser un son corporel (corps_bref, "
                          "corps_rythmique).")
    from .voix import nom_pour_joueur
    p = Plan({"action": "composer", "justification": justification}, m.data["revision"],
             "Répondre à " + nom_pour_joueur(m, qui) + ".", origine=origine)
    p.minutes, p.dixiemes, p.effort = 0, HELER, False
    p.effets = [(methode, "joueur", qui)]
    return p


def appliquer(m, emetteur, mode, lignes):
    """Le joueur émet un son, de sa voix ou avec un objet : on l'inscrit avec ceux qui l'entendent
    (``entendants``), et le joueur voit qui, sous ses yeux, l'a entendu. Il retentit par l'ouïe
    commune à la fin du geste (``moteur``), où chacun l'interprète."""
    if emetteur == "joueur":
        _, texte, intensite = VOIX[mode]
    else:
        o = m.objets[emetteur]
        intensite = o["sonorite"]
        texte = "Tu produis un son avec " + designer(o) + "."
    n = nature_emise(m, [("emettre_son", emetteur, mode)])
    ecoutants = entendants(m, n)
    evenement = {"tour": m.data["revision"] + 1, "minute": m.data["minutes"], "origine": m.joueur["salle"],
                 "nature": mode, "intensite": intensite, "bruit": n, "auditeurs": ecoutants}
    if emetteur != "joueur":
        evenement["objet"] = emetteur
    m.data.setdefault("sons", []).append(evenement)
    m.data["sons"] = m.data["sons"][-40:]
    lignes.append(texte)
    for id in ecoutants:
        if m.visible(id):
            entendu = ("le son de " + designer(m.objets[emetteur]) + "." if emetteur != "joueur" else
                       "ton " + ("appel à l'aide." if mode == "appel" else "cri." if mode == "cri" else "sifflement."))
            lignes.append(designer(m.objets[id], debut=True) + " entend " + entendu)
