"""Détails personnels encore libres, établis une fois sans changer les capacités."""
import copy

from .monde import ErreurMonde


CHAMPS = {"taille_cm": (140, 210), "age_ans": (18, 90)}
TRAITS = {"couleur_yeux": ("bruns", "noisette", "bleus", "gris", "verts"),
          "couleur_cheveux": ("noirs", "bruns", "châtains", "blonds", "roux", "gris", "blancs"),
          "corpulence": ("mince", "moyenne", "robuste")}
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"profil_joueur": {"type": "array", "minItems": 1, "maxItems": 5,
              "items": {"type": "object", "additionalProperties": False,
                        "properties": {"champ": {"type": "string", "enum": [*CHAMPS, *TRAITS]},
                                       "valeur": {"anyOf": [{"type": "integer"}, {"type": "string", "enum": sorted(set(v for valeurs in TRAITS.values() for v in valeurs))}]}},
                        "required": ["champ", "valeur"]}}}, "required": ["profil_joueur"]}

REGLES = """
PERSONNAGE JOUEUR : interprète les pronoms avant d'utiliser le contexte spatial.
joueur.espece et joueur.stade_vie sont le socle d'identité établi par le jeu. Corvus est
un humain adulte. Appuie les compléments sur cette identité, sa masse, son âge et les traits
déjà connus : une anatomie humaine ordinaire, sans particularité fantastique improvisée.
« Je mesure combien ? », « je fais combien de haut, moi ? » demandent la taille corporelle
du joueur, jamais l'altitude de la terrasse ni la longueur d'un objet voisin. « Je pèse
combien ? » demande joueur.masse_kg ; « j'ai quel âge ? » demande joueur.age_ans.
La conversation aide à lever une ambiguïté, mais une correction du joueur prime dessus.
Si la valeur personnelle existe dans joueur, réponds naturellement à partir de cette valeur.
Si elle manque ET figure dans profil_joueur_a_completer, établis-la en mode enrichir_joueur,
texte vide, proposition={"profil_joueur":[{"champ":"taille_cm","valeur":178}]} par exemple.
Choisis un détail plausible pour cet humain adulte, dans les bornes autorisées, compatible
avec son physique connu. Si le joueur fournit une valeur cohérente, reprends-la.
Complète seulement le champ demandé : n'invente pas son âge lorsqu'il demande sa taille.
La couleur des yeux, celle des cheveux et la corpulence peuvent aussi être établies avec
les valeurs proposées dans profil_joueur_a_completer. Pour « à quoi je ressemble ? », complète
ces trois traits visuels manquants ; ne remplis pas automatiquement l'âge et la taille.
Ils restent descriptifs : une corpulence robuste ne donne pas de bonus de Force.
Il ne s'agit pas d'une transformation ni d'une action ; le moteur mémorise le détail et
formule immédiatement la réponse. N'affirme pas qu'une valeur manque si tu peux ainsi l'établir.
N'invente aucune enfance, cicatrice, motivation, famille ou compétence pour l'expliquer.
Les valeurs déjà établies ne se réécrivent pas via ce mécanisme. N'utilise pas l'altitude
comme taille ni les caractéristiques de jeu comme mesures corporelles.
"""


def installer(m):
    """Socle d'auteur pour Corvus ; respecte toute identité déjà définie."""
    if m.joueur.get("nom") == "Corvus":
        m.joueur.setdefault("espece", "humain")
        if m.joueur["espece"] == "humain":
            m.joueur.setdefault("stade_vie", "adulte")


def catalogue(m):
    if m.joueur.get("espece") != "humain" or m.joueur.get("stade_vie") != "adulte":
        return {}
    return {**{champ: {"minimum": bornes[0], "maximum": bornes[1]}
               for champ, bornes in CHAMPS.items() if champ not in m.joueur},
            **{champ: {"valeurs": list(valeurs)} for champ, valeurs in TRAITS.items() if champ not in m.joueur}}


def preparer(m, p, revision=None):
    if revision is not None and revision != m.data["revision"]:
        raise ErreurMonde("Le personnage a changé avant l'enregistrement de ce détail.")
    if not isinstance(p, dict) or set(p) != {"profil_joueur"}:
        raise ErreurMonde("Complément de personnage mal formé.")
    ajouts = p["profil_joueur"]
    if not isinstance(ajouts, list) or not 1 <= len(ajouts) <= len(CHAMPS)+len(TRAITS):
        raise ErreurMonde("Nombre de détails personnels invalide.")
    travail, libres, vus = m.copier(), catalogue(m), set()
    for a in ajouts:
        if (not isinstance(a, dict) or set(a) != {"champ", "valeur"}
                or not isinstance(a["champ"], str) or a["champ"] not in libres
                or a["champ"] in vus):
            raise ErreurMonde("Ce détail personnel est déjà établi ou n'est pas disponible.")
        champ, valeur = a["champ"], a["valeur"]
        if champ in CHAMPS:
            bas, haut = CHAMPS[champ]
            if type(valeur) is not int or not bas <= valeur <= haut:
                raise ErreurMonde("Cette valeur ne correspond pas au cadre du personnage.")
        elif not isinstance(valeur, str) or valeur not in TRAITS[champ]:
            raise ErreurMonde("Ce trait ne correspond pas au cadre humain du personnage.")
        vus.add(champ)
        travail.joueur[champ] = valeur
    travail.data["revision"] += 1
    travail.data.setdefault("enrichissements", []).append({"revision": travail.data["revision"],
        "origine": "profil joueur", "ajouts": copy.deepcopy(ajouts)})
    travail.verifier()
    return travail


def reponse(m, p):
    phrases = []
    for a in p["profil_joueur"]:
        if a["champ"] == "taille_cm":
            cm = m.joueur["taille_cm"]
            phrases.append(f"Tu mesures {cm//100} m {cm%100:02d}.")
        elif a["champ"] == "age_ans":
            phrases.append(f"Tu as {m.joueur['age_ans']} ans.")
        elif a["champ"] == "couleur_yeux":
            phrases.append(f"Tu as les yeux {m.joueur['couleur_yeux']}.")
        elif a["champ"] == "couleur_cheveux":
            phrases.append(f"Tes cheveux sont {m.joueur['couleur_cheveux']}.")
        elif a["champ"] == "corpulence":
            phrases.append(f"Tu es de corpulence {m.joueur['corpulence']}.")
    return " ".join(phrases)
