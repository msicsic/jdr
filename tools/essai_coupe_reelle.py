"""Essai isolé du parcours console avec Luna réel, sans toucher aux parties du joueur.

Lancer depuis la racine : python tools/essai_coupe_reelle.py
Les échanges et résumés d'état sont enregistrés sous artifacts/evaluations.
"""

import json
from pathlib import Path
import sys
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

import jeu
from donjon.atelier import nouveau_atelier
from donjon.mj import MJOpenAI
from donjon.monde import Monde, objet
from donjon.rendu import decrire


DOSSIER = RACINE / "artifacts" / "evaluations" / "essai_coupe_reelle"


class Interface:
    def __init__(self, commandes):
        self.commandes = iter(commandes)
        self.sortie = []

    def lire(self, _invite):
        return next(self.commandes, "quitter")

    def ecrire(self, *valeurs, **_options):
        self.sortie.append(" ".join(map(str, valeurs)))

    def montrer(self, _vue):
        pass

    def rafraichir(self, _monde, _pending, _mj):
        pass


def etat(chemin, cible, outil):
    monde = Monde.charger(chemin)
    o = monde.objets[cible]
    return {"revision": monde.data["revision"],
            "integrite": o["integrite"], "seuil_coupe": o.get("seuil_coupe"),
            "constats": [{"capacite": c["capacite"], "moyen": c["moyen_nom"],
                          "puissance_observee": c["puissance_observee"]}
                         for c in o.get("constats_capacites", [])],
            "outil": outil, "description": decrire(monde, cible, detail=True),
            "actions_executees": [e["action"]["action"] for e in monde.data["journal"]]}


def jouer(chemin, commandes, cible, outil):
    interface = Interface(commandes)
    appels = []
    original = MJOpenAI._appeler_brut

    def tracer(self, instructions, entree, intention, fonction, schema):
        reponse = original(self, instructions, entree, intention, fonction, schema)
        appels.append({"fonction": fonction, "mode": reponse.get("mode"),
                       "proposition": reponse.get("proposition")})
        return reponse

    with patch.object(MJOpenAI, "_appeler_brut", tracer):
        code = jeu.main(["--console", "--atelier", "--save", str(chemin),
                         "--connexion", "auto", "--model", "gpt-6-luna"],
                        interface=interface)
    return {"code": code, "commandes": commandes, "sortie": interface.sortie,
            "appels": appels, "etat": etat(chemin, cible, outil)}


def preparer(cible, nom, materiau, masse, description, outils):
    monde = nouveau_atelier()
    monde.objets[cible] = objet(cible, nom, "materiau", "cour", genre="f",
                                materiau=materiau, masse=masse, mobile=False,
                                description_visuelle=description)
    monde.objets[cible]["position"] = list(monde.joueur["position"])
    for identifiant, nom_outil, puissance in outils:
        monde.objets[identifiant] = objet(
            identifiant, nom_outil, "outil", "joueur", genre="f",
            materiau="acier", masse=2, usages=["couper"], puissance=puissance,
            description_visuelle=("Sa lame fine est adaptée au sciage de l'acier doux."
                                  if identifiant == "scie" else ""))
    monde.verifier()
    return monde


def main():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    resultat = {}
    granite = DOSSIER / "granite.json"
    preparer("dalle", "dalle de granit", "granit", 52,
             "Une dalle de granit massif de 8 cm d'épaisseur et de 60 sur 40 cm, fixée au sol.",
             []).sauver(granite)
    resultat["granit_hache"] = jouer(granite, [
        "je coupe la dalle de granit avec la hache", "examiner la dalle de granit",
        "quitter"], "dalle", "hache")
    if any("clé API est refusée" in ligne or "HTTP 401" in ligne
           for ligne in resultat["granit_hache"]["sortie"]):
        rapport = DOSSIER / "rapport.json"
        rapport.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Appel Luna refusé ; rapport :", rapport)
        return 2
    plaque = DOSSIER / "plaque.json"
    preparer("plaque", "plaque d'acier", "acier doux", 12.6,
             "Une plaque homogène d'acier doux de 2 mm d'épaisseur et de 100 sur 80 cm, fixée au sol.", [
        ("scie", "scie à métaux", 5)]).sauver(plaque)
    resultat["acier_hache"] = jouer(plaque, [
        "je coupe la plaque d'acier avec la hache", "quitter"], "plaque", "hache")
    resultat["acier_scie"] = jouer(plaque, [
        "je coupe la plaque d'acier avec la scie à métaux", "tenter",
        "examiner la plaque d'acier", "quitter"], "plaque", "scie")
    rapport = DOSSIER / "rapport.json"
    rapport.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf-8")
    for nom, cas in resultat.items():
        print(nom, "| appels", len(cas["appels"]), "| état", cas["etat"]["seuil_coupe"],
              cas["etat"]["integrite"], "| constats", len(cas["etat"]["constats"]))
        for ligne in cas["sortie"]:
            print(" ", ligne)
    print("Rapport :", rapport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
