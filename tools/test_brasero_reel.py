"""Mettre du bois dans le brasero, avec Luna : la console réelle, puis l'état après rechargement.

Chaque phrase part d'un Relais neuf sur une sauvegarde temporaire ; aucune partie du joueur
n'est touchée. Les appels passent par la connexion ChatGPT, l'un après l'autre.
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
from donjon.deplacement_objet import deplacer
from donjon.monde import Monde
from donjon.spatial import installer

CAS = [
    ("je ramasse les fagots et j'en mets une brassée dans le feu du brasero", "sol"),
    ("je jette une brassée de fagots dans le brasero", "sol"),
    ("je mets du bois dans le feu", "porte"),
]


def relais(fagots):
    m = nouveau_defi()
    installer(m)
    m.joueur.update(salle="echoppe", position=[3, 5])
    # Placement d'auteur : Gorm a donné ses fagots au joueur.
    m.objets["bois"]["proprietaire"] = "joueur"
    if fagots == "sol":
        m.objets["bois"].update(lieu="echoppe", position=[4, 5], position_salle="echoppe")
    else:
        deplacer(m, "bois", "joueur")
    m.verifier()
    return m


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    echecs = 0
    for phrase, fagots in CAS:
        m = relais(fagots)
        avant = m.objets["brasero"]["combustible"], m.objets["bois"]["charges"]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "defi.json"
            m.sauver(chemin)
            with (patch("builtins.input", side_effect=[phrase, "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                jeu.main(["--console", "--defi", "--save", str(chemin), "--connexion", "chatgpt"])
            reprise = Monde.charger(chemin)
        # La réponse du tour seule : après l'annonce du MJ, avant la sortie de la partie.
        texte = sortie.getvalue().split("Le MJ réfléchit…", 1)[-1].split("Partie sauvegardée.", 1)[0].strip()
        apres = reprise.objets["brasero"]["combustible"], reprise.objets["bois"]["charges"]
        recharge = apres[1] == avant[1] - 1 and apres[0] > avant[0]
        echecs += not recharge
        print(f"« {phrase} » (fagots {'au sol' if fagots == 'sol' else 'portés'})")
        print(f"  combustible {avant[0]} → {apres[0]}, charges {avant[1]} → {apres[1]}, "
              f"fagots : {reprise.objets['bois']['lieu']}")
        print("  " + texte.replace("\n", "\n  "))
        print("  " + ("RECHARGÉ" if recharge else "NON RECHARGÉ") + "\n", flush=True)
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
