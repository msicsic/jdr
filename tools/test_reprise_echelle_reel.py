"""Reproduction des trois échecs, Luna seul ; aucune sauvegarde utilisateur lue/écrite."""
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.artisanat import fabrication
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
    moteur = Moteur(m)
    p = fabrication(["perche_1", "perche_2"], "perche_3", "ficelle", "hache")
    for jet in (5, 8, 5):
        with patch.object(Monde, "d20", return_value=jet):
            texte = moteur.executer(moteur.preparer(p))
        m.memoriser("je retente de faire l'échelle", texte, "resultat_moteur")
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    mj.observateur = JournalMJ(Path(__file__).resolve().parents[1] / "artifacts/mj/test-reel")
    r = mj.echanger(m, "je retente")
    assert r["mode"] == "action" and r["proposition"]["action"] == "fabriquer", r
    assert r["proposition"].get("rythme", "normal") == "normal", r
    print("Je retente : fabrication reconnue, méthode conservée.", flush=True)
    r = mj.echanger(m, "Je prends mon temps pour fabriquer soigneusement l'échelle, sans me presser.")
    assert r["mode"] == "action" and r["proposition"].get("rythme") == "soigne", r
    plan = moteur.preparer(r["proposition"], "MJ")
    assert not plan.stat and plan.minutes == 52
    with patch.object(Monde, "d20", side_effect=AssertionError("Pas de jet")):
        print(moteur.executer(plan), flush=True)
    assert m.objets["ficelle"]["longueur_cm"] == 680
    assert m.objets[m.trouver("echelle")]["lieu"] == "cour"
    print("Échelle créée sans jet après trois échecs, avec 6,8 m de ficelle restants. Trace : " + str(mj.observateur.chemin))


if __name__ == "__main__":
    main()
