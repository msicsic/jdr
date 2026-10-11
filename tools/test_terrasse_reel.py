"""Rejoue les intentions de la terrasse avec Luna, sur un monde de test en mémoire."""
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.config import charger_env
from donjon.harnais import JournalMJ
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.espace import preparer
from tests.test_espace import terrasse


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    m, id = terrasse()
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    mj.observateur = JournalMJ(Path(__file__).resolve().parents[1]/"artifacts/mj/test-reel")
    r = mj.echanger(m, "il y a d'autres issues ?")
    assert "_espace" in r, r
    m = preparer(m, r["_espace"]["proposition"], r["_espace"]["revision"])
    assert r["mode"] == "dialogue", r
    print("ISSUES :", r["texte"], flush=True)
    origine = m.copier()
    question = "j'attrape mon echelle pour la remonter sur la terrasse, puis je la mets de l'autre coté de la terrasse pour en descendre"
    r = mj.echanger(m, question)
    assert r["mode"] == "action" and r["proposition"]["action"] == "composer", r
    moteur = Moteur(m)
    plan = moteur.preparer(r["proposition"])
    print("ÉCHELLE :", plan.resume(m), flush=True)
    with patch.object(Monde, "d20", return_value=20): print(moteur.executer(plan), flush=True)
    assert m.joueur["salle"] == "abord_terrasse_nord"
    r = mj.echanger(origine, "je cours et je saute dans le vide, du coté opposé a l'echelle")
    assert r["mode"] == "action" and r["proposition"]["action"] == "composer", r
    moteur = Moteur(origine)
    plan = moteur.preparer(r["proposition"])
    print("SAUT :", plan.resume(origine), flush=True)
    with patch.object(Monde, "d20", return_value=1): print(moteur.executer(plan), flush=True)
    assert origine.joueur["salle"] == "abord_terrasse_nord" and origine.joueur["pv"] == 13
    print("Vérification Luna réussie. Trace :", mj.observateur.chemin)


if __name__ == "__main__":
    main()
