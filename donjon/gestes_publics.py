"""Catalogue des premiers gestes de carte, sur la seule projection publique.

Ce sont des offres d'interface, pas une promesse de faisabilité. Le moteur
revalide chaque descripteur, y compris une référence devenue périmée.
"""
import re
from dataclasses import dataclass

from .commandes import DescripteurPublic


# Conditions sur les seuls champs déjà envoyés à la page. Même table en Python
# et dans les données du pont web, sans lire de précondition privée du moteur.
OBJETS = (
    ("examiner", "Examiner", {}),
    ("observer", "Observer son attitude", {"type": "personnage"}),
    ("parler", "Lui parler", {"type": "personnage"}),
    ("lire", "Lire", {"type": "motif"}),
    ("eteindre", "Éteindre", {"type": "luminaire", "allume": True}),
    ("allumer", "Allumer", {"type": "luminaire", "allume": False}),
    ("manger", "Manger", {"type": "nourriture"}),
    ("ouvrir", "Ouvrir", {"type": "contenant"}),
    ("fermer", "Fermer", {"type": "contenant"}),
    ("prendre", "Prendre", {"mobile": True}),
)
PORTES = (
    ("examiner", "Examiner", {}),
    ("ouvrir", "Ouvrir", {"etat": "fermee"}),
    ("fermer", "Fermer", {"etat": "ouverte"}),
    ("deverrouiller", "Déverrouiller", {"etat": "verrouillee"}),
    ("crocheter", "Crocheter", {"etat": "verrouillee"}),
)


def offres(cible, porte=False):
    if porte and cible.get("souvenir"):
        return []
    return [(geste, libelle) for geste, libelle, conditions in (PORTES if porte else OBJETS)
            if all(cible.get(k, False) == v for k, v in conditions.items())
            and not (not porte and cible.get("type") == "personnage" and geste == "prendre")]


@dataclass(frozen=True)
class ChoixPublic:
    libelle: str
    descripteur: DescripteurPublic


def liste_gestes(scene):
    """Fige les références du menu affiché ; jamais les souvenirs ou l'inventaire."""
    liste, vus = [], set()
    for niveau in (scene or {}).get("niveaux", []):
        cibles = [(o, False, o["salle"], o["globale"]) for o in niveau["objets"]]
        cibles += [(s["porte"], True, s["salle"], s["globale"])
                   for s in niveau["sorties"] if s.get("visible") and s.get("porte")]
        for cible, porte, salle, case in cibles:
            for geste, libelle in offres(cible, porte):
                if geste == "parler":  # La conversation libre reste hors de ce premier lot.
                    continue
                cle = (geste, cible["id"])
                if cle in vus:
                    continue
                vus.add(cle)
                # La référence publique distingue aussi les homonymes à la même case.
                repere = f'{cible["nom"]} [{cible["id"]}] · {salle}, carte ({case[0]}, {case[1]})'
                liste.append(ChoixPublic(f"{libelle} — {repere}",
                                        DescripteurPublic({"geste": geste, "cible": cible["id"]})))
    return tuple(liste)


def rendre_liste(liste):
    lignes = ["Gestes de la scène — numéro puis Entrée ; saisie libre disponible."]
    lignes.extend(f"{i}. {choix.libelle}" for i, choix in enumerate(liste, 1))
    if not liste:
        lignes.append("Aucun geste de carte visible.")
    return "\n".join(lignes)


def choisir_numero(texte, liste):
    """Un numéro exact, sans abréviation ni choix implicite parmi plusieurs.

    None laisse la saisie libre suivre sa voie actuelle ; ValueError reste local.
    """
    texte = texte.strip()
    if re.fullmatch(r"[0-9]+", texte):
        # Comparer les chaînes évite aussi les entiers arbitrairement longs.
        numero = texte.lstrip("0") or "0"
        for i, choix in enumerate(liste, 1):
            if numero == str(i):
                return choix.descripteur
        raise ValueError("Numéro inconnu dans la liste affichée.")
    if re.fullmatch(r"[0-9\s,;/+\-]+", texte) and any(c.isdigit() for c in texte):
        raise ValueError("Choix ambigu : saisis un seul numéro de la liste affichée.")
    return None


def catalogue_public():
    """Données JSON du catalogue commun, indépendantes de toute partie.

    Une copie des conditions empêche un consommateur de modifier les offres
    Python ; la sérialisation appartient au transport habituel du serveur.
    """
    return {famille: [[geste, libelle, dict(conditions)] for geste, libelle, conditions in table]
            for famille, table in (("objets", OBJETS), ("portes", PORTES))}
