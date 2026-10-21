"""Articles et accords du vocabulaire du scénario, sans modifier les noms des objets."""

# Compatibilité avec les sauvegardes existantes. Un nouvel objet, une nouvelle salle peuvent
# préciser genre, pluriel, nom_propre et elision dans leurs propriétés.
FEMININS = {"porte", "gravure", "serrure", "clé", "cle", "trousse", "lanterne", "torche", "empreinte",
            # Salles des scénarios, pour les parties sauvées avant qu'elles déclarent leur genre.
            "galerie", "salle", "conduite", "cuisine", "étable", "chambre", "réserve", "crypte", "echoppe",
            "échoppe", "cour", "terrasse", "antichambre"}


def feminin(objet):
    return objet.get("genre", "f" if objet["nom"].split()[0].lower() in FEMININS else "m") == "f"


def pluriel(objet):
    return objet.get("pluriel", objet["nom"].lower() == "murs")


def designer(objet, article="defini", debut=False):
    nom = objet["nom"]
    if objet.get("nom_propre", objet.get("type") == "personnage"):
        texte = nom
    else:
        elision = objet.get("elision", nom[0].lower() in "aàâäeéèêëiîïoôöuùûüyœæ")
        if pluriel(objet):
            determinant = {"defini": "les ", "indefini": "des ", "possessif": "tes "}[article]
        elif article == "indefini":
            determinant = "une " if feminin(objet) else "un "
        elif article == "possessif":
            determinant = "ta " if feminin(objet) and not elision else "ton "
        else:
            determinant = "l'" if elision else "la " if feminin(objet) else "le "
        texte = determinant + nom
    return texte[:1].upper() + texte[1:] if debut else texte


def lieu(salle, debut=False):
    """Une salle avec son article, comme un objet : « l'étable », « la salle commune », « le
    couloir de l'étage ». Son nom, écrit avec une capitale dans le scénario, est un nom commun,
    sauf ``nom_propre``."""
    nom = salle["nom"]
    if not salle.get("nom_propre"):
        nom = nom[:1].lower() + nom[1:]
    return designer({**salle, "nom": nom, "nom_propre": False}, debut=debut)


def sujet(objet):
    """En tête de phrase, devant son verbe : une apposition (« Gorm, gardien du relais ») se
    referme par une virgule."""
    texte = designer(objet, debut=True)
    return texte + "," if "," in texte else texte


def de(nom):
    """« de Gorm », « d'Aubin » : la préposition devant un nom sans article."""
    return ("d'" if nom[:1].lower() in "aàâäeéèêëiîïoôöuùûüyœæh" else "de ") + nom


def complement_de(objet):
    """Forme le complément nominal avec les contractions françaises usuelles."""
    nom = designer(objet)
    if nom.startswith("le "):
        return "du " + nom[3:]
    if nom.startswith("les "):
        return "des " + nom[4:]
    return "d'" + nom[2:] if nom.startswith("l'") else "de " + nom


def accorder(objet, masculin, feminin_irregulier=None):
    mot = (feminin_irregulier or masculin + "e") if feminin(objet) else masculin
    return mot + "s" if pluriel(objet) else mot


def relation_physique(objet, support, relation):
    """Formule l'emplacement déclaré sans déduire une relation depuis le nom."""
    nom_support = designer(support)
    if relation == "pose":
        return accorder(objet, "posé") + " sur " + nom_support
    if relation == "contenu":
        return "dans " + nom_support
    if nom_support.startswith("le "):
        nom_support = "au " + nom_support[3:]
    elif nom_support.startswith("les "):
        nom_support = "aux " + nom_support[4:]
    else:
        nom_support = "à " + nom_support
    return accorder(objet, "fixé") + " " + nom_support


def enumerer(elements):
    elements = list(elements)
    return ", ".join(elements[:-1]) + " et " + elements[-1] if len(elements) > 1 else "".join(elements)
