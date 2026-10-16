"""Petit corpus reproductible de contre revue avec Luna réel, sans sauvegarde joueur."""

import argparse
import json
from pathlib import Path
import sys

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from donjon.atelier import nouveau_atelier
from donjon.connexion import Coffre
from donjon.defi import nouveau_defi
from donjon.faits_locaux import catalogue
from donjon.mj import MJOpenAI
from donjon.narration import attestations
from donjon.portee_narrative import SCHEMA, INSTRUCTIONS, controler, descriptions
from donjon.spatial import installer


def objet(nom, texte, materiau, masse, capacites):
    return {"type": "objet", "ancrage": "cour_sol", "nom": nom,
            "genre": "m", "texte": texte, "materiau": materiau, "masse": masse,
            "mobile": True, "relation": "pose", "capacites": capacites}


def corpus():
    return [
        ("son_et_lumiere", nouveau_atelier(), True, [
            objet("grelot de cuivre", "Le cuivre vibre et produit un tintement quand on le secoue.",
                  "cuivre", 0.2, [{"nature": "son", "intensite": 2}]),
            objet("lampe à huile", "Une mèche traverse son réservoir d'huile et peut être allumée.",
                  "cuivre et verre", 0.4,
                  [{"nature": "lumiere", "niveau": 2, "combustible": 20}]),
        ]),
        ("outils", nouveau_atelier(), True, [
            objet("barre à tranchant", "Une arête d'acier tranche le bois ; son corps rigide fait levier.",
                  "acier", 1.2, [{"nature": "outil", "usages": ["couper", "levier"],
                                   "puissance": 2}]),
            objet("percuteur à silex", "Le silex produit des étincelles pour allumer une mèche.",
                  "silex", 0.2, [{"nature": "outil", "usages": ["allumage"],
                                 "puissance": 0}]),
        ]),
        ("objet_tranchable", nouveau_atelier(), True, [
            objet("cordelette de chanvre", "Ses fibres souples peuvent être tranchées par une lame.",
                  "chanvre", 0.1, [{"nature": "tranchable", "seuil": 1,
                                    "tenacite": 2}]),
        ]),
        ("objectif_de_quete", nouveau_defi(), False, [{
            **objet("seconde cloche", "Sa surface de bronze est ternie.", "bronze", 1.2, []),
            "ancrage": "antichambre_sol", "genre": "f"}]),
    ]


def evaluer(mj, nom, monde, ajouts, attendu):
    if nom == "objectif_de_quete":
        installer(monde)
    entrees = descriptions({"mode": "etablir_faits", "proposition": {"ajouts": ajouts}})
    contexte = monde.contexte()
    preuves = attestations(monde, contexte)
    entree = {"descriptions": [{"sujet": e["sujet"], "texte": e["texte"]}
                              for e in entrees],
              "monde": {"salle": contexte["salle"], "scenario": contexte["scenario"],
                        "faits_narratifs_proposables": catalogue(monde)},
              "attestations": preuves}
    rapport = mj._appeler_brut(INSTRUCTIONS, entree, "Contrôler la portée des objets proposés",
                              "auditer_portee", SCHEMA)
    obstacles = controler(entrees, rapport, preuves)
    accepte = not obstacles
    return {"cas": nom, "attendu": "accepter" if attendu else "refuser",
            "decision": "accepter" if accepte else "refuser", "conforme": accepte == attendu,
            "classements": [{"texte": e["texte"], "capacites": r["capacites"],
                             "impact_scenario": r["impact_scenario"]}
                            for e, r in zip(entrees, rapport["descriptions"])],
            "obstacles": obstacles}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--cas", choices=[nom for nom, *_ in corpus()])
    args = parser.parse_args()
    if not 1 <= args.repetitions <= 10:
        parser.error("Les répétitions doivent être entre 1 et 10.")
    connexion = "chatgpt" if Coffre().compte() else "api"
    mj = MJOpenAI(connexion=connexion)
    resultats = []
    for essai in range(1, args.repetitions + 1):
        for nom, monde, attendu, ajouts in corpus():
            if args.cas and nom != args.cas:
                continue
            resultat = evaluer(mj, nom, monde, ajouts, attendu)
            resultat["essai"] = essai
            resultats.append(resultat)
            print(f'{essai} {nom}: {resultat["decision"]} '
                  f'({"conforme" if resultat["conforme"] else "écart"})')
            for obstacle in resultat["obstacles"]:
                print("  ", obstacle.get("texte", ""), "—", obstacle["motif"])
    chemin = RACINE / "artifacts" / "evaluations" / "capacites_objet.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Rapport :", chemin)
    return 0 if all(r["conforme"] for r in resultats) else 1


if __name__ == "__main__":
    raise SystemExit(main())
