"""Essais Luna de l'arbitrage sommaire ; mondes en mémoire, aucune partie utilisateur."""
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.atelier import nouveau_atelier
from donjon.config import charger_env
from donjon.harnais import JournalMJ
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur, proposition


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    mj.observateur = JournalMJ(Path(__file__).resolve().parents[1]/"artifacts/mj/test-reel")
    m = nouveau_atelier()
    for phrase in ("je m'étire pour me dégourdir les épaules", "je fredonne une chanson pour me donner du courage",
                   "avec mon couteau je grave une flèche sur la perche 1 pour repérer le nord"):
        r = mj.echanger(m, phrase)
        assert r["mode"] == "action" and r["proposition"]["action"] == "improviser", r
        moteur = Moteur(m)
        plan = moteur.preparer(r["proposition"], "MJ")
        if "grave" not in phrase:
            assert not plan.stat, r
        print("INTENTION :", phrase, flush=True)
        with patch.object(Monde, "d20", return_value=20):
            print(moteur.executer(plan), flush=True)
        assert m.joueur["pv"] == 18
    assert any(o.get("origine_description") == "geste du joueur" for o in m.objets.values())
    assert m.data["sons"]
    n = nouveau_monde()
    moteur = Moteur(n)
    moteur.executer(moteur.preparer(proposition("prendre", "cle")))
    r = mj.echanger(n, "je jongle avec la clé")
    assert r["mode"] == "action" and r["proposition"]["action"] == "improviser", r
    plan = moteur.preparer(r["proposition"], "MJ")
    print("JONGLAGE :", plan.resume(n), flush=True)
    with patch.object(Monde, "d20", return_value=1): print(moteur.executer(plan), flush=True)
    # La narration ne doit pas annoncer une chute sans déplacement réel de la clé.
    recit = r["proposition"]["echec"]["recit"].lower()
    if "tombe" in recit or "sol" in recit:
        assert n.objets["cle"]["lieu"] == "antichambre", r
    print("Essais réussis. Trace :", mj.observateur.chemin)


if __name__ == "__main__":
    main()
