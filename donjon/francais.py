"""Articles et accords du vocabulaire du scénario, sans modifier les noms des objets."""
import re

VOYELLES = "aàâäeéèêëiîïoôöuùûüyœæh"


def groupe_nominal(nom, preposition="", debut=False):
    """Insère une désignation déjà déterminée, ou un nom propre sans article.

    Seul le déterminant perd sa capitale en milieu de phrase ; le nom propre
    conserve la sienne. Le h suit la convention historique d'élision des noms ;
    pour un objet, son article porte déjà sa propriété explicite ``elision``.
    """
    article = re.match(r"(?:le |la |les |l['’]|un |une |des )", nom, re.I)
    if article:
        nom = nom[:1].lower() + nom[1:]
    if preposition == "de":
        if nom.startswith("le "):
            texte = "du " + nom[3:]
        elif nom.startswith("les "):
            texte = "des " + nom[4:]
        elif nom.startswith("des "):
            texte = de(nom[4:])
        else:
            texte = ("d'" if not nom.startswith(("la ", "l'", "l’"))
                     and nom[:1].lower() in VOYELLES else "de ") + nom
    elif preposition == "à":
        texte = ("au " + nom[3:] if nom.startswith("le ") else
                 "aux " + nom[4:] if nom.startswith("les ") else "à " + nom)
    elif preposition == "defini":
        # Un article déjà présent dans la phrase ne se double pas devant la désignation.
        texte = nom
    else:
        texte = (preposition + " " if preposition else "") + nom
    return texte[:1].upper() + texte[1:] if debut else texte


def inserer_designation(texte, motif, nom):
    """Remplace une référence nominale avec sa liaison, hors citations protégées.

    Le motif désigne seulement la référence ; la préposition ou l'article de
    la phrase appartient au groupe remplacé, jamais au nom de substitution.
    """
    forme = re.compile(r"(?<!\w)(?P<liaison>de\s+(?:(?:le|la|les)\s+|l['’])?|d['’]|du\s+|des\s+|"
                       r"à\s+(?:(?:le|la|les)\s+|l['’])?|au\s+|aux\s+|"
                       r"le\s+|la\s+|les\s+|l['’])?(?:" + motif.pattern + ")", re.I)

    def remplacer(m):
        liaison = (m.group("liaison") or "").strip().lower()
        preposition = ("de" if liaison in ("de", "d'", "d’", "du", "des") or liaison.startswith("de ") else
                       "à" if liaison in ("à", "au", "aux") or liaison.startswith("à ") else "defini" if liaison else "")
        avant = texte[:m.start()].rstrip(" \t«\"“(")
        debut = not avant or avant[-1] in ".!?\n"
        return groupe_nominal(nom, preposition, debut)

    return forme.sub(remplacer, texte)

# Compatibilité avec les sauvegardes existantes. Un nouvel objet, une nouvelle salle peuvent
# préciser genre, pluriel, nom_propre et elision dans leurs propriétés.
FEMININS = {"porte", "gravure", "serrure", "clé", "cle", "trousse", "lanterne", "torche", "empreinte",
            # Salles des scénarios, pour les parties sauvées avant qu'elles déclarent leur genre.
            "galerie", "salle", "conduite", "cuisine", "étable", "chambre", "réserve", "crypte", "echoppe",
            "échoppe", "pièce", "part", "cour", "terrasse", "antichambre"}


def feminin(objet):
    return objet.get("genre", "f" if objet["nom"].split()[0].lower() in FEMININS else "m") == "f"


# Noms singuliers dont la finale ressemble à une marque du pluriel.
SINGULIERS_INVARIABLES = frozenset("""accès amas bras bois corps cours dos fonds frais
gaz grès héros jus laps lilas mois nez os pays poids pois prix puits repas
repos secours sens souris tapis tas temps velours vis choix croix noix voix""".split())


def quantite(nombre, nom, pluriel_nom=None, determinant=""):
    """Quantité d'un nom singulier ; 0 et 1 restent singuliers en français.

    Les formes irrégulières se déclarent par pluriel_nom, les finales s/x/z
    sont invariantes. Le nom d'un objet pluriel passe plutôt par designer.
    """
    mots = nom.split(" ", 1)
    tete = mots[0]
    plur = pluriel_nom or (tete if tete.endswith(("s", "x", "z")) else tete + "s")
    forme = nom if not pluriel({"nom": nom}, nombre) else plur + (" " + mots[1] if len(mots) > 1 and not pluriel_nom else "")
    if determinant:
        determinants = {"defini": ("la" if feminin({"nom": nom}) else "le", "les"),
                        "possessif": ("ta" if feminin({"nom": nom}) else "ton", "tes")}
        singulier, multiple = determinants[determinant]
        forme = (multiple if pluriel({"nom": nom}, nombre) else singulier) + " " + f"{nombre} {forme}"
        return forme
    return f"{nombre} {forme}"


def pluriel(objet, nombre=None):
    """Nombre déclaré, sinon tête du nom ; une quantité désigne son propre nombre."""
    if nombre is not None:
        return abs(nombre) >= 2
    if "pluriel" in objet:
        return objet["pluriel"]
    if objet.get("nom_propre", objet.get("type") == "personnage"):
        return False
    tete = re.split(r"[\s’'-]", objet.get("nom", "").lower())[0]
    # Les finales s/x/z peuvent être singulières : le lexique grammatical
    # couvre les formes invariantes ; une donnée explicite lève toute ambiguïté.
    return tete.endswith(("s", "x")) and tete not in SINGULIERS_INVARIABLES


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
    """Complément d'un nom propre ou d'une désignation déjà déterminée."""
    return groupe_nominal(nom, "de")


def complement_de(objet):
    """Forme le complément nominal avec les contractions françaises usuelles."""
    return de(designer(objet))


def accorder(objet, masculin, feminin_irregulier=None):
    mot = (feminin_irregulier or masculin + "e") if feminin(objet) else masculin
    return mot + "s" if pluriel(objet) and not mot.endswith(("s", "x")) else mot


def relation_physique(objet, support, relation):
    """Formule l'emplacement déclaré sans déduire une relation depuis le nom."""
    nom_support = designer(support)
    if relation == "pose":
        return accorder(objet, "posé") + " sur " + nom_support
    if relation == "contenu":
        return "dans " + nom_support
    return accorder(objet, "fixé") + " " + groupe_nominal(nom_support, "à")


def enumerer(elements):
    elements = list(elements)
    return ", ".join(elements[:-1]) + " et " + elements[-1] if len(elements) > 1 else "".join(elements)
