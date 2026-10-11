"""Luna seul, phrase réelle et ancienne réponse en mémoire ; aucune partie modifiée."""
import copy
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
    phrase = "je prend une perche, et je tente un sait a la perche pour franchir le mur"
    m.memoriser(phrase, "Tu demandes un saut à la perche plutôt que de fabriquer l'accès prévu ; ce franchissement n'est pas pris en charge.")
    avant = copy.deepcopy(m.data)
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    mj.observateur = JournalMJ(Path(__file__).resolve().parents[1] / "artifacts/mj/test-reel")
    r = mj.echanger(m, phrase)
    assert r["mode"] == "action" and r["proposition"]["action"] == "composer", r
    p = r["proposition"]
    assert [e["operation"] for e in p["etapes"]] == ["deplacer", "franchir_obstacle"], p
    assert m.data == avant
    print(Moteur(m).preparer(p, "MJ").resume(m), flush=True)
    for jet in (20, 1):
        copie = m.copier()
        moteur = Moteur(copie)
        with patch.object(Monde, "d20", return_value=jet):
            print(moteur.executer(moteur.preparer(p, "MJ")), flush=True)
        assert copie.joueur["salle"] == ("terrasse" if jet == 20 else "cour")
    print("Phrase comprise par Luna ; réussite et échec vérifiés sur copies. Trace : " + str(mj.observateur.chemin))


if __name__ == "__main__":
    main()
