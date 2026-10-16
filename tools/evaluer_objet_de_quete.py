"""Sonde la contre revue réelle d'un objet autonome lié à l'objectif du Relais."""

from pathlib import Path
import sys

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from donjon.connexion import Coffre
from donjon.defi import nouveau_defi
from donjon.faits_locaux import catalogue
from donjon.mj import MJOpenAI
from donjon.narration import attestations
from donjon.portee_narrative import SCHEMA, INSTRUCTIONS, controler, descriptions
from donjon.spatial import installer


def main():
    monde = nouveau_defi()
    installer(monde)
    proposition = {"mode": "etablir_faits", "proposition": {"ajouts": [{
        "type": "objet", "ancrage": "antichambre_sol", "nom": "seconde cloche",
        "genre": "f", "texte": "Sa surface de bronze est ternie.",
        "materiau": "bronze", "masse": 1.2, "mobile": True, "relation": "pose", "capacites": []}]}}
    entrees = descriptions(proposition)
    contexte = monde.contexte()
    preuves = attestations(monde, contexte)
    entree = {"descriptions": [{"sujet": e["sujet"], "texte": e["texte"]} for e in entrees],
              "monde": {"salle": contexte["salle"], "scenario": contexte["scenario"],
                        "faits_narratifs_proposables": catalogue(monde)},
              "attestations": preuves}
    connexion = "chatgpt" if Coffre().compte() else "api"
    rapport = MJOpenAI(connexion=connexion)._appeler_brut(
        INSTRUCTIONS, entree, "Contrôler la portée de l'objet proposé",
        "auditer_portee", SCHEMA)
    obstacles = controler(entrees, rapport, preuves)
    print("Classements :", [r["impact_scenario"] for r in rapport["descriptions"]])
    print("Décision :", "refuser" if obstacles else "accepter")
    return 0 if obstacles else 1


if __name__ == "__main__":
    raise SystemExit(main())
