"""Articles et accords du vocabulaire du scénario, sans modifier les noms des objets."""

# Compatibilité avec les sauvegardes existantes. Un nouvel objet peut préciser
# genre, pluriel, nom_propre et elision dans ses propriétés.
FEMININS = {"porte", "gravure", "serrure", "clé", "cle", "trousse", "lanterne", "torche", "empreinte"}


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


def accorder(objet, masculin, feminin_irregulier=None):
    mot = (feminin_irregulier or masculin + "e") if feminin(objet) else masculin
    return mot + "s" if pluriel(objet) else mot


def enumerer(elements):
    elements = list(elements)
    return ", ".join(elements[:-1]) + " et " + elements[-1] if len(elements) > 1 else "".join(elements)
