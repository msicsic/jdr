"""Demander une part et manger, avec Luna : la console réelle, puis l'état après rechargement.

Chaque phrase part d'un Relais neuf sur une sauvegarde temporaire, le joueur près de Gorm ;
aucune partie du joueur n'est touchée. Les appels passent par la connexion ChatGPT, l'un
après l'autre. Le jet de persuasion reste aléatoire : un refus motivé est une issue valable,
« n'a pas cet objet sur lui » ne l'est plus.
"""
import io
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jeu
from donjon.config import charger_env
from donjon.corps import valeurs
from donjon.defi import nouveau_defi
from donjon.deplacement_objet import deplacer
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.spatial import installer

CAS = [
    ("Gorm, tu peux me donner une part de vivres ? Je n'ai rien mangé depuis ce matin.", "faim", "vivres"),
    ("Gorm, tu me donnerais un peu de bois pour le feu ? Je suis gelé.", "chaleur", "bois"),
    ("je mange une part des vivres", "faim", "manger"),
]


def relais(besoin, cas):
    m = nouveau_defi()
    installer(m)
    m.joueur.update(salle="echoppe", position=[1, 2])
    valeurs(m, "joueur")[besoin] = 80.0
    if cas == "manger":
        # Placement d'auteur : Gorm a donné au joueur les vivres, qu'il porte.
        m.objets["vivres"]["proprietaire"] = "joueur"
        deplacer(m, "vivres", "joueur")
    m.verifier()
    return m


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    echecs = 0
    for phrase, besoin, cas in CAS:
        m = relais(besoin, cas)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "defi.json"
            m.sauver(chemin)
            with (patch("builtins.input", side_effect=[phrase, "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                jeu.main(["--console", "--defi", "--save", str(chemin), "--connexion", "chatgpt"])
            reprise = Monde.charger(chemin)
        texte = sortie.getvalue().split("Le MJ réfléchit…", 1)[-1].split("Partie sauvegardée.", 1)[0].strip()
        engagements = [x["condition"] for x in lire(reprise, "marchand")["engagements"]]
        if cas == "manger":
            ok = reprise.objets["vivres"]["portions"] == 3 and valeurs(reprise, "joueur")["faim"] < 80 - 40
            bilan = f"portions {reprise.objets['vivres']['portions']}, faim {valeurs(reprise, 'joueur')['faim']:.0f}"
        else:
            accepte = bool(engagements)
            refus_motive = any(mot in texte for mot in ("refuse", "pas convaincu", "garde", "confiance"))
            ok = (accepte or refus_motive) and "n'a pas cet objet sur lui" not in texte
            bilan = f"engagements {engagements or 'aucun'}"
        echecs += not ok
        print(f"« {phrase} »\n  {bilan}\n  " + texte.replace("\n", "\n  ") + "\n  " + ("OK" if ok else "ÉCHEC") + "\n", flush=True)
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
