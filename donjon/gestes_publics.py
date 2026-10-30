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
    {"type": "contenant"}, {"type": "luminaire"}, {"foyer": True}], "aptitude": "depot"}
CORPS = ("personnage", "depouille", "partie_corps")

# Famille portée par U-M corps seulement ; U-T gardera son interface actuelle.
# Ces choix ne calculent aucune aptitude : toute ressource connue peut être
# choisie, puis le moteur tranche. La surprise est une défense calculée, pas
# une méthode que le joueur pourrait imposer.
GESTES_CORPS = frozenset(("frapper", "saisir", "ligoter", "delier", "liberer",
                         "trainer", "pousser", "ranimer", "tuer", "fuir",
                         "riposter", "se_rendre", "degager"))
REACTIONS = frozenset(("fuir", "riposter", "se_rendre", "degager"))


def formulaires_corps():
    from .spatial import VECTEURS
    outil = {"champ": "outil", "libelle": "Moyen", "type": "ressource",
             "vide": "Mains nues"}
    direction = {"champ": "direction", "libelle": "Direction", "type": "choix",
                 "choix": list(VECTEURS)}
    return [
        {"geste": "frapper", "libelle": "Frapper / assommer…", "champs": [
            {"champ": "methode", "libelle": "Méthode", "type": "choix",
             "choix": ["simple", "assommer"]}, outil]},
        {"geste": "saisir", "libelle": "Saisir", "champs": []},
        {"geste": "ligoter", "libelle": "Ligoter avec…", "champs": [
            {"champ": "outil", "libelle": "Lien", "type": "ressource"}]},
        {"geste": "delier", "libelle": "Délier…", "champs": [outil]},
        {"geste": "liberer", "libelle": "Défaire mes liens", "champs": []},
        {"geste": "trainer", "libelle": "Traîner vers…", "champs": [direction]},
        {"geste": "pousser", "libelle": "Pousser vers…", "champs": [
            {**direction, "choix": ["", *direction["choix"]]}]},
        {"geste": "ranimer", "libelle": "Ranimer", "champs": []},
        {"geste": "tuer", "libelle": "Tuer…", "champs": [outil]},
        {"geste": "fuir", "libelle": "Fuir par la sortie connue la plus proche", "danger": True, "champs": []},
        {"geste": "riposter", "libelle": "Riposter avec…", "danger": True, "champs": [outil]},
        {"geste": "se_rendre", "libelle": "Me rendre à cette personne", "danger": True, "champs": []},
        {"geste": "degager", "libelle": "Me dégager", "danger": True, "champs": []},
    ]


def dangers_publics(monde):
    """Références des dangers vus et encore perçus, sans faits privés."""
    from .defense import dangers_vus
    from .noms import reference
    return [reference(monde, d["auteur"]) for d in dangers_vus(monde)
            if d["auteur"] in monde.objets and monde.visible(d["auteur"])]


def ressource_connue(monde, id, exiger_portee=True):
    """Frontière commune des choix matériels : portée et perception actuelles."""
    from .noms import PERSONNES
    from .spatial import proche
    o = monde.objets.get(id)
    if not o or o["type"] in (*PERSONNES, "partie_corps"):
        return False
    parent, vus = o, set()
    while parent["lieu"] in monde.objets and parent["lieu"] not in vus:
        vus.add(parent["lieu"])
        parent = monde.objets[parent["lieu"]]
        if parent["type"] in PERSONNES:
            return False
    return ((o["lieu"] == "joueur" and monde.present_physique(id)) or
            (monde.visible(id) and (not exiger_portee or not monde.data.get("mode_cases") or proche(monde, id))))


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
    ("deverrouiller", "Déverrouiller avec…", {"type": "contenant"}, {**OUTIL, "aptitude": "cle"}),
    ("crocheter", "Crocheter avec…", [{"type": "contenant"}, {"type": "serrure"}], {**OUTIL, "aptitude": "crochetage"}),
    ("frapper", "Forcer / frapper avec…", {}, {**OUTIL, "aptitude": "impact"}),
    ("alimenter", "Alimenter avec…", [{"type": "luminaire"}, {"foyer": True}], {**OUTIL, "aptitude": "recharge"}),
    ("mettre", "Mettre dans…", {"mobile": True}, DESTINATION),
)
PORTES = (
    ("examiner", "Examiner", {}),
    ("ouvrir", "Ouvrir", {"etat": "fermee"}),
    ("fermer", "Fermer", {"etat": "ouverte"}),
    ("deverrouiller", "Déverrouiller", {"etat": "verrouillee"}),
    ("crocheter", "Crocheter", {"etat": "verrouillee"}),
    ("deverrouiller", "Déverrouiller avec…", {}, {**OUTIL, "aptitude": "cle"}),
    ("crocheter", "Crocheter avec…", {}, {**OUTIL, "aptitude": "crochetage"}),
    ("frapper", "Forcer / frapper avec…", {}, {**OUTIL, "aptitude": "impact"}),
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


def noms_des_choix(*groupes):
    """Désignations publiques ; un rang visible distingue les homonymes.

    Les références de transport restent dans les descripteurs, jamais dans
    les libellés. Le numéro de ligne suffit pour choisir l'entité exacte.
    """
    entites = {o["id"]: o["nom"] for groupe in groupes for o in groupe}
    return {id: nom + (f" ({ids.index(id) + 1}/{len(ids)})" if len(ids) > 1 else "")
            for id, nom in entites.items()
            for ids in [sorted(i for i, n in entites.items() if n == nom)]}


def ressource_admise(cible, ressource, formulaire):
    return (ressource["id"] != cible["id"]
            and correspond(ressource, formulaire["ressources"])
            and cible["id"] in ressource.get("aptitudes", {}).get(formulaire["aptitude"], ()))


def liste_gestes(scene, inventaire=(), destinataires=(), ressources=()):
    """Fige les choix des seules projections publiques, sans lire le monde."""
    liste, materiels, vus = [], [], set()
    entites = [o for n in (scene or {}).get("niveaux", []) for o in n["objets"]]
    entites += [s["porte"] for n in (scene or {}).get("niveaux", [])
                for s in n["sorties"] if s.get("visible") and s.get("porte")]
    noms = noms_des_choix(entites, inventaire, destinataires, ressources)
    for niveau in (scene or {}).get("niveaux", []):
        cibles = [(o, False, o["salle"], o["globale"]) for o in niveau["objets"]]
        cibles += [(s["porte"], True, s["salle"], s["globale"])
                   for s in niveau["sorties"] if s.get("visible") and s.get("porte")]
        for cible, porte, salle, case in cibles:
            repere = noms[cible["id"]] + " · scène"
            materiels.extend(gestes_materiels(cible, ressources, repere, porte, noms))
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
    liste.extend(gestes_inventaire(inventaire, destinataires, noms))
    for bien in inventaire:
        repere = noms[bien["id"]] + " · besace"
        materiels.extend(gestes_materiels({**bien, "mobile": True}, ressources, repere, noms=noms))
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


def gestes_materiels(cible, ressources, repere, porte=False, noms=None):
    """Même formulaire que la page ; aucune capacité ni réussite présumée.

    Chaque ligne fige le second choix avec sa référence, y compris pour deux
    ressources homonymes. Aucun formulaire incomplet ne quitte cette projection.
    """
    liste = []
    noms = noms if noms is not None else noms_des_choix(ressources)
    for geste, libelle, formulaire in offres(cible, porte, parametrees=True):
        for ressource in ressources:
            if not ressource_admise(cible, ressource, formulaire):
                continue
            d = {"geste": geste, "cible": cible["id"],
                 "parametres": {formulaire["champ"]: ressource["id"]}}
            nom = noms[ressource["id"]]
            liste.append(ChoixPublic(f"{libelle} {nom} — {repere}", DescripteurPublic(d)))
    return tuple(liste)


def gestes_inventaire(inventaire, destinataires, noms=None):
    """Un numéro par choix complet : bien, quantité admise et destinataire.

    Comme le menu de la page, seules les quantités déjà proposées par le
    moteur sont offertes : lot entier pour poser/remettre, une portion/pièce.
    L'absence d'état lumineux perçu laisse les deux gestes à la revalidation.
    """
    liste = []
    noms = noms if noms is not None else noms_des_choix(inventaire, destinataires)
    for bien in inventaire:
        lot = bien.get("pieces", 0) > 1
        repere = noms[bien["id"]] + " · besace"

        def ajouter(geste, libelle, parametres=None):
            d = {"geste": geste, "cible": bien["id"]}
            if parametres is not None:
                d["parametres"] = parametres
            liste.append(ChoixPublic(f"{libelle} — {repere}", DescripteurPublic(d)))

        ajouter("poser", "Poser le lot entier" if lot else "Poser")
        for personne in destinataires:
            libelle = "Remettre le lot entier à" if lot else "Remettre à"
            ajouter("remettre", f'{libelle} {noms[personne["id"]]}',
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
    lignes.append("0. Fabrication — choisir une recette et ses paramètres.")
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
    catalogue = {famille: [deepcopy(list(entree)) for entree in table]
                 for famille, table in (("objets", OBJETS), ("portes", PORTES))}
    catalogue["fabrication"] = formulaires_fabrication()
    catalogue["corps"] = formulaires_corps()
    return catalogue


def formulaires_fabrication():
    """Les usages et rôles du moteur, sans prédire l'aptitude d'une ressource."""
    from .artisanat import SCHEMA_ASSEMBLAGE, SCHEMA_DECOUPE, USAGES

    def champ(nom, schema, chemin=None):
        return {"chemin": chemin or [nom], "libelle": nom.replace("_cm", " (cm)").replace("_", " ").capitalize(),
                **({"type": "nombre", **{k: schema[k] for k in ("minimum", "maximum") if k in schema}}
                   if schema["type"] == "integer" else
                   {"type": "choix", "choix": list(schema["enum"])} if "enum" in schema else
                   {"type": "ressource"})}

    p = SCHEMA_ASSEMBLAGE["properties"]
    roles = []
    for nom, schema in p["pieces"]["properties"].items():
        if schema["type"] == "array":
            for i in range(schema["minItems"]):
                c = champ(nom, schema["items"], ["pieces", nom, i])
                c["libelle"] += f" {i + 1}"
                roles.append(c)
        else:
            roles.append(champ(nom, schema, ["pieces", nom]))
    return [
        {"geste": "assembler", "cible": usage, "libelle": "Assembler : " + usage,
         "champs": roles + [champ(nom, p[nom]) for nom in
                            ("lien", "outil", "longueur_cm", "largeur_cm", "rythme")]}
        for usage in USAGES
    ] + [{"geste": "decouper", "libelle": "Découper à longueur",
          "champs": [champ(nom, SCHEMA_DECOUPE["properties"][nom]) for nom in
                     ("cible", "outil", "longueur_cm")]}]
