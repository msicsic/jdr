"""Catalogue des gestes de carte et de besace, sur la seule projection publique.

Ce sont des offres d'interface, pas une promesse de faisabilité. Le moteur
revalide chaque descripteur, y compris une référence devenue périmée.
"""
import re
from dataclasses import dataclass

from .commandes import DescripteurPublic


# Le quatrième champ, optionnel, décrit un choix explicite encore à compléter.
# Les interfaces complètent ce champ avec une référence publique explicite.
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

    Une entrée paramétrée n'est soumise qu'après sélection de sa ressource.
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


def liste_gestes(scene, inventaire=(), destinataires=(), ressources=()):
    """Fige les choix des seules projections publiques, sans lire le monde."""
    liste, materiels, vus = [], [], set()
    for niveau in (scene or {}).get("niveaux", []):
        cibles = [(o, False, o["salle"], o["globale"]) for o in niveau["objets"]]
        cibles += [(s["porte"], True, s["salle"], s["globale"])
                   for s in niveau["sorties"] if s.get("visible") and s.get("porte")]
        for cible, porte, salle, case in cibles:
            repere = f'{cible["nom"]} [{cible["id"]}] · {salle}, carte ({case[0]}, {case[1]})'
            materiels.extend(gestes_materiels(cible, ressources, repere, porte))
            for geste, libelle in offres(cible, porte):
                if geste == "parler":  # La conversation libre reste hors de ce premier lot.
                    continue
                cle = (geste, cible["id"])
                if cle in vus:
                    continue
                vus.add(cle)
                # La référence publique distingue aussi les homonymes à la même case.
                liste.append(ChoixPublic(f"{libelle} — {repere}",
                                        DescripteurPublic({"geste": geste, "cible": cible["id"]})))
    liste.extend(gestes_inventaire(inventaire, destinataires))
    for bien in inventaire:
        repere = f'{bien["nom"]} [{bien["id"]}] · besace'
        materiels.extend(gestes_materiels({**bien, "mobile": True}, ressources, repere))
    # Une porte peut figurer sur plusieurs sorties. Figer une seule fois chaque
    # choix complet, sans modifier les numéros des gestes simples précédents.
    vus_materiels = set()
    for choix in materiels:
        d = choix.descripteur.contenu
        cle = (d["geste"], d["cible"], tuple(d["parametres"].items()))
        if cle not in vus_materiels:
            vus_materiels.add(cle)
            liste.append(choix)
    return tuple(liste)


def gestes_materiels(cible, ressources, repere, porte=False):
    """Même formulaire que la page ; aucune capacité ni réussite présumée.

    Chaque ligne fige le second choix avec sa référence, y compris pour deux
    ressources homonymes. Aucun formulaire incomplet ne quitte cette projection.
    """
    liste = []
    for geste, libelle, formulaire in offres(cible, porte, parametrees=True):
        for ressource in ressources:
            if ressource["id"] == cible["id"] or not correspond(ressource, formulaire["ressources"]):
                continue
            d = {"geste": geste, "cible": cible["id"],
                 "parametres": {formulaire["champ"]: ressource["id"]}}
            nom = f'{ressource["nom"]} [{ressource["id"]}]'
            liste.append(ChoixPublic(f"{libelle} {nom} — {repere}", DescripteurPublic(d)))
    return tuple(liste)


def gestes_inventaire(inventaire, destinataires):
    """Un numéro par choix complet : bien, quantité admise et destinataire.

    Comme le menu de la page, seules les quantités déjà proposées par le
    moteur sont offertes : lot entier pour poser/remettre, une portion/pièce.
    L'absence d'état lumineux perçu laisse les deux gestes à la revalidation.
    """
    liste = []
    for bien in inventaire:
        lot = bien.get("pieces", 0) > 1
        repere = f'{bien["nom"]} [{bien["id"]}] · besace'

        def ajouter(geste, libelle, parametres=None):
            d = {"geste": geste, "cible": bien["id"]}
            if parametres is not None:
                d["parametres"] = parametres
            liste.append(ChoixPublic(f"{libelle} — {repere}", DescripteurPublic(d)))

        ajouter("poser", "Poser le lot entier" if lot else "Poser")
        for personne in destinataires:
            libelle = "Remettre le lot entier à" if lot else "Remettre à"
            ajouter("remettre", f'{libelle} {personne["nom"]} [{personne["id"]}]',
                    {"destinataire": personne["id"]})
        if bien["type"] == "nourriture":
            ajouter("manger", "Manger une portion", {"quantite": 1})
        if bien["type"] == "luminaire":
            if bien.get("allume") is not True:
                ajouter("allumer", "Allumer")
            if bien.get("allume") is not False:
                ajouter("eteindre", "Éteindre")
        if lot:
            ajouter("prelever", f'Prélever une pièce du lot ({bien["pieces"]})', {"quantite": 1})
    return tuple(liste)


def gestes_du_monde(monde):
    """Adaptateur commun aux terminaux ; le catalogue ne reçoit que du public."""
    from .inventaire_public import inventaire_public, destinataires_publics, ressources_publiques
    from .scene import scene_percue
    scene = scene_percue(monde) if monde.data.get("mode_cases") else None
    return liste_gestes(scene, inventaire_public(monde), destinataires_publics(monde),
                        ressources_publiques(monde))


def rendre_liste(liste):
    lignes = ["Gestes de la scène et de la besace — numéro puis Entrée ; saisie libre disponible."]
    lignes.extend(f"{i}. {choix.libelle}" for i, choix in enumerate(liste, 1))
    if not liste:
        lignes.append("Aucun geste disponible dans cette vue.")
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
