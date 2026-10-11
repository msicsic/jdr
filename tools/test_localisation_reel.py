"""Deux régressions avec Luna seul ; scènes en mémoire, aucune sauvegarde touchée."""
import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.config import charger_env
from donjon.defi import nouveau_defi
from donjon.harnais import JournalMJ
from donjon.mj import MJOpenAI
from donjon.moteur import Moteur
from donjon.spatial import installer


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    m = nouveau_defi()
    installer(m)
    m.joueur.update(salle="echoppe", position=[5, 4])
    m.memoriser("c'est quoi cet obstacle ?", "Tu ne perçois aucun obstacle dans la Conduite basse. Le pilier était dans l'échoppe.")
    m.memoriser("je prend le pied de biche", "Il est dans l'échoppe : retourne dans cette pièce.")
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    mj.observateur = JournalMJ(Path(__file__).resolve().parents[1] / "artifacts/mj/test-reel")
    avant = copy.deepcopy(m.data)
    r = mj.echanger(m, "juste au nord de ma position il y a un obstacle solide, c'est quoi ?")
    print("OBSTACLE :", r, flush=True)
    assert m.data == avant
    assert r["mode"] == "dialogue" and "poutre" in r["texte"].lower(), r
    m.joueur["position"] = [6, 5]
    avant = copy.deepcopy(m.data)
    r = mj.echanger(m, "je prend le pied de biche")
    print("PRISE :", r, flush=True)
    assert m.data == avant
    assert r["mode"] == "action", r
    simulation = m.copier()
    moteur = Moteur(simulation)
    moteur.executer(moteur.preparer(r["proposition"]))
    assert simulation.objets["pied_de_biche"]["lieu"] == "joueur"
    assert m.data == avant
    print("Deux régressions vérifiées avec Luna ; aucun changement de partie.")


if __name__ == "__main__":
    main()
