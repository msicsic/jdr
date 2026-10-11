"""Six échanges réels : lire aussi la prose, les assertions ne prouvent pas sa fidélité."""
import argparse
import copy
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.commandes import analyser
from donjon.config import charger_env
from donjon.mj import MJOpenAI
from donjon.monde import nouveau_monde
from donjon.moteur import Moteur


def main():
    charger_env()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--connexion", choices=["api", "chatgpt"], default="chatgpt")
    args = parser.parse_args()
    m = nouveau_monde()
    moteur = Moteur(m)
    mj = MJOpenAI(connexion=args.connexion)
    en_attente = None
    questions = [
        ("comment je me suis retrouvé ici ?", "dialogue"),
        ("pourquoi il ne va pas le chercher lui-même ?", "dialogue"),
        ("comment je peux voir s'il n'y a pas de fenetres ?", "dialogue"),
        ("Je glisse mon couteau sous la tête de l'axe supérieur et je fais levier pour le retirer.", "action"),
        ("Donc je l'ai retiré et la porte est ouverte ?", "dialogue"),
        ("Et maintenant, j'y vois toujours aussi bien ?", "dialogue"),
    ]
    for i, (message, mode) in enumerate(questions):
        if i == 5:
            en_attente = None
            resultat = moteur.executer(moteur.preparer(analyser(m, "éteindre lanterne")))
            m.memoriser("éteindre lanterne", resultat, "resultat_moteur")
        avant = copy.deepcopy(m.data)
        debut = time.monotonic()
        reponse = mj.echanger(m, message, en_attente)
        print(json.dumps({"joueur": message, "mj": reponse,
                          "secondes": round(time.monotonic() - debut, 2)}, ensure_ascii=False, indent=2), flush=True)
        assert reponse["mode"] == mode
        assert m.data == avant, "Un échange ne doit pas modifier le monde"
        if mode == "action":
            p = reponse["proposition"]
            assert p["action"] == "detacher" and p["cible"] == "axe_haut" and p["outil"] == "couteau"
            plan = moteur.preparer(p, "LLM")
            en_attente = p
            assert 17 <= plan.dd <= 22
            m.memoriser(message, plan.resume(m), "proposition_non_executee")
        else:
            m.memoriser(message, reponse["texte"])
    assert m.objets["axe_haut"]["attache"] and not m.objets["porte"]["ouverte"]
    print("Six échanges terminés. Prose à relire ; aucune sauvegarde utilisateur modifiée.")


if __name__ == "__main__":
    main()
