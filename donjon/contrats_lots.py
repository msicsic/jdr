"""Quantité des transferts : un contrat commun, sans interprétation du français."""

TRANSFERTS = {
    "deplacer": {
        "sens": "Déplacer l'objet cible entier, avec toutes ses pièces s'il forme un lot. "
                "Ne représente pas le prélèvement d'une pièce de ce lot. "
                "Destination joueur pour prendre, sol pour poser à ses pieds, contenant ouvert pour ranger. "
                "Vers un consommateur en combustion, le moteur prépare alimenter (une charge consommée), "
                "pas un déplacement de l'objet. "
                "Un article en vente s'achète (acheter). methode discret pour un bien d'autrui : "
                "le moteur en déduit le vol, les témoins et leurs soupçons ; pour ses propres affaires, "
                "discret n'accuse personne.",
        "unite": "objet",
    },
    "prelever": {
        "sens": "Dans composer, séparer exactement une pièce du lot cible décrit (physique.pieces et nom_piece), "
                "puis la déplacer vers destination (joueur par défaut). Le lot reste en place et diminue "
                "d'une pièce. Les règles de possession, portée et discrétion sont celles de deplacer. "
                "Une quantité de plusieurs pièces exige plusieurs étapes ; la dernière pièce seule "
                "se déplace avec deplacer. Une description manquante doit être qualifiée avant le geste.",
        "unite": "part",
    },
}


def description():
    return " ".join(f"{op} : {c['sens']}" for op, c in TRANSFERTS.items())


def sens_propose(parametres):
    op = parametres.get("operation", parametres.get("action"))
    if op in ("prendre", "poser", "voler", "remettre"):
        op = "deplacer"
    return TRANSFERTS.get(op, {}).get("sens", "")


def quantite_proposee(parametres, monde):
    """Données publiques de la cible, distinctes de la quantité voulue par le joueur."""
    op = parametres.get("operation", parametres.get("action"))
    if op in ("prendre", "poser", "voler", "remettre"):
        op = "deplacer"
    cible = parametres.get("cible")
    if op not in TRANSFERTS or monde is None or not monde.designable(cible):
        return None
    objet = monde.objets.get(cible)
    if objet is None:
        return None
    physique = objet.get("physique") or {}
    pieces = physique.get("pieces")
    return {"objet": cible, "nom_lot": objet["nom"], "nom_piece": physique.get("nom_piece", ""),
            "quantite": 1, "unite": TRANSFERTS[op]["unite"],
            "pieces_transferees": 1 if op == "prelever" else pieces,
            "pieces_restantes": pieces - 1 if op == "prelever" and pieces is not None else 0}


def precision_publique(quantite):
    if quantite is None or quantite["pieces_transferees"] is None:
        return ""
    n = quantite["pieces_transferees"]
    if quantite["unite"] == "objet":
        if n <= 1:
            return ""
        return f"Objet entier : {n} pièce{'s' if n > 1 else ''}."
    reste = quantite["pieces_restantes"]
    return f"Quantité visée : une pièce ; reste du lot après réussite : {reste} pièce{'s' if reste > 1 else ''}."
