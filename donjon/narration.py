"""Contrôle commun des assertions du MJ avant leur affichage.

Le contrôle s'applique à la prose finale du MJ. Les effets d'une action sont
racontés par le moteur après résolution. Les phrases factuelles du MJ doivent
reprendre une attestation produite à partir de l'état courant.
"""

import copy

from .monde import ErreurMonde


VERDICTS = ("etabli", "hypothese", "neutre", "parole", "nouveau", "contradictoire")


def attestations(monde, contexte):
    """Phrases produites par l'état courant, que le MJ peut reprendre telles quelles.

    Une référence à un objet entier ne prouve pas une phrase libre à son sujet. Le
    catalogue reste volontairement distinct des données utiles pour décider d'agir.
    """
    from .rendu import decrire, regarder, decrire_perception, decrire_contexte

    scene = " ".join(ligne.strip() for ligne in regarder(monde).splitlines()
                     if ligne.strip() and not ligne.startswith("=="))
    textes = [scene, decrire_perception(monde), decrire_contexte(monde)]
    for objet in contexte["objets_perceptibles"]:
        if objet["visible"]:
            textes.append(decrire(monde, objet["id"], technique=False))
    return list(dict.fromkeys(p for texte in textes for p in segments(texte) if p))


def rendre_resultat(resultat):
    """Affiche les conséquences rédigées par le moteur, sans la ligne de calcul du jet."""
    lignes = [ligne for ligne in resultat.splitlines() if not ligne.startswith("1d20(")]
    return "\n".join(lignes).strip() or "Action accomplie."
SCHEMA_AUDIT = {
    "type": "object", "additionalProperties": False,
    "properties": {"segments": {"type": "array", "maxItems": 24,
        "items": {"type": "object", "additionalProperties": False,
            "properties": {
                "indice": {"type": "integer"},
                "verdict": {"type": "string", "enum": list(VERDICTS)},
                "sources": {"type": "array", "items": {"type": "string"}},
                "locuteur": {"type": "string"},
                "citation": {"type": "string"},
                "motif": {"type": "string"},
            },
            "required": ["indice", "verdict", "sources", "locuteur", "citation", "motif"]}},
    },
    "required": ["segments"],
}

INSTRUCTIONS_AUDIT = """Tu contrôles une réponse du maître du jeu avant qu'un joueur la voie.
Les attestations sont les seules phrases factuelles que le moteur autorise à reprendre.
Pour etabli, le segment doit reproduire exactement une attestation et citer attestations.
Les autres faits servent à choisir une action, mais ne prouvent pas une phrase libre.
L'historique,
une proposition non exécutée et une parole de personnage ne prouvent pas leur contenu.
Examine CHAQUE segment fourni, y compris les implications contenues dans une proposition.
Classe-le en entier :
- etabli : segment identique à une attestation du moteur ;
- hypothese : possibilité explicitement présentée comme incertaine ;
- neutre : formule sans affirmation sur le monde ;
- parole : propos nouveau d'un personnage présent, attribué explicitement ; son contenu
  peut être faux. Donne son identifiant exact et la citation littérale présente dans le segment ;
- nouveau : au moins un fait sur le monde sans source, même décoratif ou plausible ;
- contradictoire : au moins une affirmation contraire à l'état ou aux effets prévus.
Si un segment mêle plusieurs catégories, choisis le verdict le plus contraignant :
contradictoire, puis nouveau, puis parole, puis etabli, puis hypothese, puis neutre.
Une source vaguement liée au sujet ne suffit pas : elle doit soutenir l'affirmation précise.
Rends un contrôle pour chaque indice, dans l'ordre, sans réécrire les segments.
"""

INSTRUCTIONS_REVISION = """\nLe contrôle de la réponse précédente a relevé des affirmations
non établies ou hors de la portée de leur sujet. Réponds de nouveau à l'intention
initiale, à partir de l'état actuel.
Tu peux proposer un ajout persistant par le protocole déjà disponible si l'état et
la demande le permettent. Sinon, reformule sans présenter l'ajout comme un fait.
Ne reproduis aucune phrase refusée. Appelle la fonction demandée une fois.
"""


def segments(texte):
    """Découpage de couverture ; une assertion mixte condamne son segment entier."""
    passages, debut, citation = [], 0, 0
    texte = texte.strip()
    for i, caractere in enumerate(texte):
        if caractere == "«":
            citation += 1
        elif caractere == "»":
            citation = max(0, citation - 1)
        fin_phrase = (caractere in ".!?" and citation == 0
                      and (i + 1 == len(texte) or texte[i + 1].isspace()))
        if fin_phrase or caractere == "\n":
            passage = texte[debut:i + 1].strip()
            if passage:
                passages.append(passage)
            debut = i + 1
    dernier = texte[debut:].strip()
    if dernier:
        passages.append(dernier)
    return passages


def controler(texte, rapport, faits):
    """Valide le rapport de l'auditeur et renvoie ses obstacles, jamais sa seule assurance."""
    passages = segments(texte)
    lignes = rapport.get("segments") if isinstance(rapport, dict) else None
    if (not passages or len(passages) > 24 or not isinstance(lignes, list)
            or len(lignes) != len(passages)):
        raise ErreurMonde("Contrôle narratif incomplet.")
    obstacles = []
    paroles = []
    rendus = []
    lignes_validees = []
    preuves = faits.get("attestations", [])
    if not isinstance(preuves, list) or any(not isinstance(p, str) for p in preuves):
        preuves = []
    for indice, (passage, ligne) in enumerate(zip(passages, lignes)):
        if (not isinstance(ligne, dict)
                or set(ligne) != {"indice", "verdict", "sources", "locuteur", "citation", "motif"}
                or type(ligne["indice"]) is not int or ligne["indice"] != indice
                or ligne["verdict"] not in VERDICTS
                or not isinstance(ligne["sources"], list)
                or any(not isinstance(s, str) or s not in faits for s in ligne["sources"])
                or any(not isinstance(ligne[k], str) for k in ("locuteur", "citation", "motif"))):
            raise ErreurMonde("Contrôle narratif mal formé ou fondé sur une source inconnue.")
        verdict = ligne["verdict"]
        if verdict != "parole":
            # Ces deux champs ne portent aucun sens hors d'une parole attribuée.
            # Les vider évite qu'une erreur de format de l'auditeur rejette une
            # réponse dont le segment sera contrôlé par son verdict réel.
            ligne = {**ligne, "locuteur": "", "citation": ""}
        lignes_validees.append(ligne)
        if verdict == "etabli":
            if "attestations" not in ligne["sources"] or passage not in preuves:
                obstacles.append({"segment": indice, "texte": passage,
                                   "motif": "Cette phrase n'est pas attestée par le moteur."})
            rendus.append(passage)
        if verdict == "parole":
            locuteur, citation = ligne["locuteur"], ligne["citation"]
            if (locuteur not in faits.get("interlocuteurs", {}) or not citation
                    or not 3 <= len(citation) <= 240
                    or any(ord(c) < 32 for c in citation)
                    or f"« {citation} »" not in passage):
                raise ErreurMonde("Une parole du MJ n'a pas de locuteur présent ou de citation exacte.")
            paroles.append({"locuteur": locuteur, "texte": citation})
            nom = faits["interlocuteurs"][locuteur]["nom"]
            rendus.append(nom + " dit : « " + citation + " ».")
        if verdict == "hypothese":
            rendus.append("C'est une possibilité, pas un fait établi : « " + passage + " »")
        elif verdict == "neutre":
            rendus.append("Je ne peux pas encore l'établir.")
        if verdict in ("nouveau", "contradictoire"):
            obstacles.append({"segment": indice, "texte": passage,
                               "motif": ligne["motif"] or "Affirmation non établie."})
    return {"segments": copy.deepcopy(lignes_validees), "paroles": paroles,
            "obstacles": obstacles, "texte_controle": " ".join(rendus)}


def consigner(monde, reponse):
    """Enregistre une réponse contrôlée et ses paroles sur l'état à sauvegarder."""
    audit = reponse.get("_audit")
    if not audit:
        if reponse.get("_texte_moteur") is not True:
            raise ErreurMonde("Réponse du MJ sans contrôle narratif.")
        monde.data.setdefault("narrations_mj", []).append({
            "texte": reponse["texte"], "revision": monde.data["revision"],
            "sources": ["moteur"]})
        monde.data["narrations_mj"] = monde.data["narrations_mj"][-60:]
        return
    texte = reponse["texte"]
    rapport = controler(audit["texte_initial"], {"segments": audit["segments"]}, audit["faits"])
    if rapport["obstacles"] or rapport["texte_controle"] != texte:
        raise ErreurMonde("Une narration refusée ne peut pas être enregistrée.")
    paroles = []
    if rapport["paroles"]:
        from .sons import auditeurs
        for parole in rapport["paroles"]:
            locuteur = monde.objets[parole["locuteur"]]
            if not monde.present_physique(locuteur["id"]):
                raise ErreurMonde("Le locuteur n'est plus présent pour cette parole.")
            salle = monde.joueur["salle"]
            entendants = auditeurs(monde, salle, 2)
            if "joueur" not in entendants:
                entendants.append("joueur")
            paroles.append({
                "locuteur": locuteur["id"], "texte": parole["texte"], "salle": salle,
                "minute": monde.data["minutes"], "auditeurs": entendants,
                "revision": monde.data["revision"],
            })
    monde.data.setdefault("narrations_mj", []).append({
        "texte": texte, "revision": monde.data["revision"],
        "sources": sorted({source for ligne in rapport["segments"] for source in ligne["sources"]}),
    })
    monde.data["narrations_mj"] = monde.data["narrations_mj"][-60:]
    monde.data.setdefault("paroles_pnj", []).extend(paroles)


def verifier(monde):
    for e in monde.data.get("narrations_mj", []):
        assert (isinstance(e, dict) and set(e) == {"texte", "revision", "sources"}
                and isinstance(e["texte"], str) and bool(e["texte"].strip())
                and type(e["revision"]) is int and 0 <= e["revision"] <= monde.data["revision"]
                and isinstance(e["sources"], list)
                and all(isinstance(s, str) for s in e["sources"])), "Narration du MJ invalide"
