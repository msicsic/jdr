"""Deux appels réels au forfait ; aucune sauvegarde utilisateur modifiée."""
import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.config import charger_env
from donjon.mj import MJOpenAI
from donjon.monde import nouveau_monde


def main():
    charger_env()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    monde = nouveau_monde()
    monde.memoriser("il est comment Gorm ?", "Tu n'as pas de précisions sur son apparence ; je ne peux donc pas le décrire.")
    mj = MJOpenAI(connexion="chatgpt")
    for question in ("il est comment Gorm ?", "Il a l'air inquiet en ce moment ?"):
        avant = copy.deepcopy(monde.data)
        reponse = mj.echanger(monde, question)
        print("Corvus > " + question, flush=True)
        print(reponse["texte"] + "\n", flush=True)
        assert reponse["mode"] == "dialogue" and reponse["proposition"] is None
        assert monde.data == avant
        monde.memoriser(question, reponse["texte"])
    print("Deux échanges terminés. Prose à relire ; aucune partie enregistrée.")


if __name__ == "__main__":
    main()
