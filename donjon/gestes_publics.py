"""Catalogue des premiers gestes de carte, sur la seule projection publique.

Ce sont des offres d'interface, pas une promesse de faisabilité. Le moteur
revalide chaque descripteur, y compris une référence devenue périmée.
"""
import re
from dataclasses import dataclass

from .commandes import DescripteurPublic


# Le quatrième champ, optionnel, décrit un choix explicite encore à compléter.
# Le terminal « premier geste » ne soumet que les entrées sans ce champ.
OUTIL = {"champ": "outil", "ressources": {}}
DESTINATION = {"champ": "destination", "ressources": [
    {"type": "contenant"}, {"type": "luminaire"}, {"foyer": True}]}
CORPS = ("personnage", "depouille", "partie_corps")


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
    ("deverrouiller", "Déverrouiller avec…", {"type": "contenant"}, OUTIL),
    ("crocheter", "Crocheter avec…", [{"type": "contenant"}, {"type": "serrure"}], OUTIL),
    ("frapper", "Forcer / frapper avec…", {}, OUTIL),
    ("alimenter", "Alimenter avec…", [{"type": "luminaire"}, {"foyer": True}], OUTIL),
    ("mettre", "Mettre dans…", {"mobile": True}, DESTINATION),
)
PORTES = (
    ("examiner", "Examiner", {}),
    ("ouvrir", "Ouvrir", {"etat": "fermee"}),
    ("fermer", "Fermer", {"etat": "ouverte"}),
    ("deverrouiller", "Déverrouiller", {"etat": "verrouillee"}),
    ("crocheter", "Crocheter", {"etat": "verrouillee"}),
    ("deverrouiller", "Déverrouiller avec…", {}, OUTIL),
    ("crocheter", "Crocheter avec…", {}, OUTIL),
    ("frapper", "Forcer / frapper avec…", {}, OUTIL),
)


def correspond(cible, conditions):
    """Conditions publiques : champs conjoints, ou alternatives de tels groupes."""
    if isinstance(conditions, list):
        return any(correspond(cible, groupe) for groupe in conditions)
    return all(cible.get(k, False) == v for k, v in conditions.items())


def offres(cible, porte=False, parametrees=False):
    """Le même catalogue ; les offres paramétrées exposent aussi leur formulaire.

    Une entrée paramétrée n'est jamais transformée en descripteur incomplet par
    la liste terminal. Son interface de choix des ressources relève d'U-T outils.
    """
    if porte and cible.get("souvenir"):
        return []
    resultat = []
    for geste, libelle, conditions, *formulaire in (PORTES if porte else OBJETS):
        if bool(formulaire) != parametrees or not correspond(cible, conditions):
            continue
        if formulaire and cible.get("type") in CORPS:
            continue
        if not porte and cible.get("type") == "personnage" and geste == "prendre":
            continue
        resultat.append((geste, libelle, formulaire[0]) if formulaire else (geste, libelle))
    return resultat


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
    from copy import deepcopy
    return {famille: [deepcopy(list(entree)) for entree in table]
            for famille, table in (("objets", OBJETS), ("portes", PORTES))}
