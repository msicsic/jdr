"""Recette numérotée commune aux terminaux, sur une projection publique figée."""
from copy import deepcopy
import re

from .commandes import DescripteurPublic
from .gestes_publics import catalogue_public
from .inventaire_public import ressources_publiques


def fabrication_publique(monde):
    return {"formulaires": catalogue_public()["fabrication"],
            "ressources": ressources_publiques(monde, decrire_physique=True)}


class RecetteTerminal:
    def __init__(self, public):
        self.public = deepcopy(public)
        self.offre = None
        self.valeurs = []
        self.terminee = False

    @property
    def champ(self):
        return self.offre["champs"][len(self.valeurs)] if self.offre else None

    def choix(self):
        if self.offre is None:
            return [(f, f["libelle"]) for f in self.public["formulaires"]]
        if self.champ["type"] == "ressource":
            return [(r["id"], r["nom"] + " [" + r["id"] + "] — " + r["description_physique"])
                    for r in self.public["ressources"]]
        return [(v, v) for v in self.champ.get("choix", ())]

    def rendre(self):
        lignes = ["Fabrication — numéro puis Entrée ; annuler pour fermer.",
                  "Le moteur vérifie les pièces et les droits ; aucune forme inconnue n'est complétée.",
                  "Entrée sur le dernier champ exécute ce choix."]
        if self.offre:
            lignes.append(self.offre["libelle"])
            for champ, (valeur, libelle) in zip(self.offre["champs"], self.valeurs):
                lignes.append(champ["libelle"] + " : " + libelle)
            c = self.champ
            lignes.append(c["libelle"] + (f" : entier de {c['minimum']} à {c.get('maximum', 9007199254740991)}"
                                         if c["type"] == "nombre" else " :"))
        lignes.extend(f"{i}. {libelle}" for i, (_, libelle) in enumerate(self.choix(), 1))
        if (not self.offre or self.champ["type"] != "nombre") and not self.choix():
            lignes.append("Aucun choix connu à portée. Annule pour revenir au jeu.")
        return "\n".join(lignes)

    def saisir(self, texte):
        texte = texte.strip()
        if texte.casefold() == "annuler":
            self.terminee = True
            return None
        if self.terminee:
            raise ValueError("Cette recette est fermée.")
        if self.offre and self.champ["type"] == "nombre":
            c = self.champ
            chiffres = texte.lstrip("0") or "0"
            if not re.fullmatch(r"[0-9]+", texte) or len(chiffres) > 16:
                raise ValueError("Saisis une dimension entière dans les limites indiquées.")
            valeur = int(chiffres)
            if not c["minimum"] <= valeur <= min(c.get("maximum", 9007199254740991), 9007199254740991):
                raise ValueError("Saisis une dimension entière dans les limites indiquées.")
            libelle = str(valeur)
        else:
            selection = next(((v, l) for i, (v, l) in enumerate(self.choix(), 1)
                              if texte.lstrip("0") == str(i)), None)
            if selection is None:
                raise ValueError("Choisis un seul numéro de la recette affichée.")
            valeur, libelle = selection
        if self.offre is None:
            self.offre = valeur
            return None
        self.valeurs.append((valeur, libelle))
        if len(self.valeurs) != len(self.offre["champs"]):
            return None
        d = {"geste": self.offre["geste"], "parametres": {}}
        if "cible" in self.offre:
            d["cible"] = self.offre["cible"]
        for c, (valeur, _) in zip(self.offre["champs"], self.valeurs):
            chemin = c["chemin"]
            if chemin == ["cible"]:
                d["cible"] = valeur
                continue
            parent = d["parametres"]
            for i, cle in enumerate(chemin[:-1]):
                if cle not in parent:
                    parent[cle] = [] if isinstance(chemin[i + 1], int) else {}
                parent = parent[cle]
            if isinstance(parent, list):
                while len(parent) <= chemin[-1]:
                    parent.append(None)
            parent[chemin[-1]] = valeur
        self.terminee = True
        return DescripteurPublic(d)
