"""Écouter à une porte, avec Luna : la console réelle, puis ce que le joueur lit.

Relais neuf sur une sauvegarde temporaire : le joueur sur le palier des vannes, collé à la
porte fermée ; derrière, Aubin parle à Gorm pendant la minute qui suit. Aucune partie du
joueur n'est touchée. Les appels passent par la connexion ChatGPT, l'un après l'autre.
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
from donjon.ecoute import bruit
from donjon.esprits import lire
from donjon.spatial import installer

PHRASES = [
    "j'écoute à la porte pour savoir s'il y a quelque chose derrière",
    "je colle mon oreille contre la porte",
]


def relais():
    m = nouveau_defi()
    installer(m)
    for id in ("marchand", "brune", "ilse", "aubin"):
        besoins = lire(m, id)["besoins"]
        for b in besoins:
            besoins[b] = 0.0
    m.joueur.update(salle="beffroi", position=[0, 3])
    for id, case in (("aubin", [4, 1]), ("marchand", [5, 1])):
        m.objets[id].update(lieu="crypte", position=case, position_salle="crypte")
    # Placement d'auteur : Aubin parle à Gorm pendant la minute qui suit.
    m.data["minutes"] += 1
    bruit(m, "aubin", "voix", "Aubin dit à Gorm que l'eau monte aux vannes.", ["marchand"])
    m.data["minutes"] -= 1
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
        texte = sortie.getvalue().split("Le MJ réfléchit…", 1)[-1].split("Partie sauvegardée.", 1)[0].strip()
        ok = "Tu entends une voix à l'ouest." in texte or "voix" in texte
        echecs += not ok
        print(f"« {phrase} »\n  " + texte.replace("\n", "\n  ") + "\n  " + ("OK" if ok else "ÉCHEC") + "\n", flush=True)
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
