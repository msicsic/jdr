"""Allumer sa lanterne à une autre flamme, avec Luna : la console réelle, puis l'état après rechargement.

Chaque phrase part d'un Relais neuf sur une sauvegarde temporaire, le briquet laissé au
refuge ; aucune partie du joueur n'est touchée. Les appels passent par la connexion ChatGPT,
l'un après l'autre.
"""
import io
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jeu
from donjon.config import charger_env
from donjon.defi import nouveau_defi
from donjon.monde import Monde
from donjon.spatial import installer

PHRASES = [
    "j'allume ma lanterne au brasero",
    "je rallume la lanterne avec le feu",
]


def relais():
    m = nouveau_defi()
    installer(m)
    m.joueur.update(salle="echoppe", position=[3, 5])
    # Placement d'auteur : le briquet est resté au refuge, la lanterne s'est éteinte.
    m.objets["briquet"].update(lieu="antichambre", position=[2, 2], position_salle="antichambre")
    m.objets["lanterne"]["allume"] = False
    m.verifier()
    return m


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    echecs = 0
    for phrase in PHRASES:
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "defi.json"
            relais().sauver(chemin)
            with (patch("builtins.input", side_effect=[phrase, "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                jeu.main(["--console", "--defi", "--save", str(chemin), "--connexion", "chatgpt"])
            reprise = Monde.charger(chemin)
        # La réponse du tour seule : après l'annonce du MJ, avant la sortie de la partie.
        texte = sortie.getvalue().split("Le MJ réfléchit…", 1)[-1].split("Partie sauvegardée.", 1)[0].strip()
        allumee = reprise.objets["lanterne"]["allume"] and reprise.objets["briquet"]["lieu"] == "antichambre"
        echecs += not allumee
        print(f"« {phrase} »")
        print("  " + texte.replace("\n", "\n  "))
        print("  " + ("ALLUMÉE" if allumee else "NON ALLUMÉE") + "\n", flush=True)
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
