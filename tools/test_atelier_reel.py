"""Cinq intentions avec Luna seul ; monde en mémoire, aucune sauvegarde utilisateur."""
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.atelier import nouveau_atelier
from donjon.config import charger_env
from donjon.harnais import JournalMJ
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from donjon.moteur import Moteur


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    m = nouveau_atelier()
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    mj.observateur = JournalMJ(Path(__file__).resolve().parents[1] / "artifacts/mj/test-reel")
    for texte, attendu in (
        ("Avec ces trois perches, la ficelle et ma hache, est-ce que je peux fabriquer une échelle pour monter sur la terrasse ?", None),
        ("Alors je fabrique cette échelle.", "fabriquer"),
        ("Je la pose contre le mur pour atteindre la terrasse.", "installer"),
        ("Je monte à l'échelle.", "franchir"),
        ("Je redescends par l'échelle.", "franchir"),
    ):
        print("> " + texte, flush=True)
        r = mj.echanger(m, texte)
        if attendu is None:
            assert r["mode"] == "dialogue" and m.data["revision"] == 0, r
            print(r["texte"], flush=True)
            m.memoriser(texte, r["texte"])
        else:
            assert r["mode"] == "action" and r["proposition"]["action"] == attendu, r
            moteur = Moteur(m)
            p = moteur.preparer(r["proposition"], "MJ")
            with patch.object(Monde, "d20", return_value=20):
                resultat = moteur.executer(p)
            print(resultat, flush=True)
            m.memoriser(texte, resultat, "resultat_moteur")
    assert m.joueur["salle"] == "cour"
    print("Parcours complet validé avec Luna seul. Jets fixés pour exercer toutes les étapes. Trace : " + str(mj.observateur.chemin), flush=True)


if __name__ == "__main__":
    main()
