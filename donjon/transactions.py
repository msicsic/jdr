"""Transactions validées sur copie par le MJ, puis réappliquées par la boucle de jeu.

Le MJ ne modifie jamais la partie : il renvoie la liste ordonnée des propositions
qu'il a fait valider, chacune avec la révision du monde sur lequel elle a été
préparée. La boucle de jeu les réapplique dans l'ordre, sauvegarde, puis affiche.
"""
from .monde import ErreurMonde


def _preparateurs():
    from .connaissances import preparer_savoirs
    from .dialogues import preparer_conversation
    from .enrichissement import preparer_complements
    from .espace import preparer as preparer_espace
    from .faits_locaux import preparer_faits
    from .profil_joueur import preparer as preparer_profil
    return {
        "espace": lambda m, p, r: (preparer_espace(m, p, r), None),
        "conversation_pnj": preparer_conversation,
        "complements": lambda m, p, r: (preparer_complements(m, p, r), None),
        "savoirs": lambda m, p, r: (preparer_savoirs(m, p, r), None),
        "profil_joueur": lambda m, p, r: (preparer_profil(m, p, r), None),
        "faits": lambda m, p, r: (preparer_faits(m, p, r)[0], None),
    }


TYPES = ("espace", "conversation_pnj", "complements", "savoirs", "profil_joueur", "faits")


def ajouter(reponse, nature, revision, proposition, rapport=None, debut=False):
    if nature not in TYPES:
        raise ErreurMonde("Type de transaction inconnu.")
    t = {"type": nature, "revision": revision, "proposition": proposition}
    if rapport is not None:
        t["rapport"] = rapport
    liste = reponse.setdefault("_transactions", [])
    liste.insert(0, t) if debut else liste.append(t)
    return reponse


def du_type(reponse, nature):
    return next((t for t in reponse.get("_transactions", []) if t["type"] == nature), None)


def preparer(monde, transaction):
    """Valide et applique une transaction sur une copie ; renvoie (copie, rapport)."""
    if not isinstance(transaction, dict) or transaction.get("type") not in TYPES:
        raise ErreurMonde("Transaction du MJ mal formée.")
    return _preparateurs()[transaction["type"]](monde, transaction["proposition"],
                                                transaction["revision"])


def appliquer(monde, transactions):
    """Applique la liste dans l'ordre ; aucune ne touche la partie avant la dernière."""
    travail, rapports = monde, []
    for t in transactions:
        travail, rapport = preparer(travail, t)
        rapports.append(rapport)
    return (travail if transactions else monde.copier()), rapports
