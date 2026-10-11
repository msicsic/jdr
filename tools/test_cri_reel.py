"""Vérification d'un cri avec Luna seul, sans lire/écrire une partie utilisateur."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.atelier import nouveau_atelier
from donjon.config import charger_env
from donjon.harnais import JournalMJ
from donjon.mj import MJOpenAI
from donjon.moteur import Moteur


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    m = nouveau_atelier()
    m.memoriser("je crie a l'aide", "Crier n'est pas pris en charge par les actions du moteur.")
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    mj.observateur = JournalMJ(Path(__file__).resolve().parents[1] / "artifacts/mj/test-reel")
    r = mj.echanger(m, "je crie a l'aide")
    assert r["mode"] == "action" and r["proposition"]["action"] == "composer", r
    etapes = r["proposition"]["etapes"]
    assert len(etapes) == 1 and etapes[0]["operation"] == "emettre_son" and etapes[0]["methode"] == "appel", r
    moteur = Moteur(m)
    p = moteur.preparer(r["proposition"], "MJ")
    assert not p.stat and not p.echec_critique
    print(moteur.executer(p))
    assert not m.data["sons"][-1]["auditeurs"] and m.data["jets"] == 0
    print("Luna reconnaît l'appel, sans inventer de secours. Trace : " + str(mj.observateur.chemin))


if __name__ == "__main__":
    main()
