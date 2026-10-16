"""Rejoue la question restée sans réponse, trois fois, sans toucher aux sauvegardes."""
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.config import charger_env
from donjon.mj import MJOpenAI
from donjon.monde import nouveau_monde
from donjon.transactions import du_type


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    monde = nouveau_monde()
    monde.joueur["salle"] = "echoppe"
    monde.objets["cle"]["lieu"] = "joueur"
    monde.memoriser("je demande a Gorm s'il peut m'ouvrir la porte de l'antichambre",
                    "Gorm : « La porte de l’antichambre ? Elle n’a pas besoin de moi : "
                    "tu peux la franchir pour retourner à l’antichambre. »", "conversation_pnj")
    question = "mais je lui demande s'il peut au moins me dire comment ouvrir la porte verouillée qui se trouve au nord de l'antichambre"
    avant = copy.deepcopy(monde.data)
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    destination = Path(__file__).resolve().parents[1] / "artifacts" / "tests" / "luna-dialogue.jsonl"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as journal:
        for essai in range(1, 4):
            def tracer(trace):
                journal.write(json.dumps({"essai": essai, **trace}, ensure_ascii=False) + "\n")
                journal.flush()
            mj.observateur = tracer
            resultat = mj.echanger(monde, question)
            assert resultat["mode"] == "dialogue" and resultat["texte"].strip(), resultat
            assert du_type(resultat, "conversation_pnj")["proposition"]["operation"] == "discuter", resultat
            assert monde.data == avant, "Le test ne doit pas modifier le monde."
            print(f"Essai {essai} : {resultat['texte']}", flush=True)
    print("Trois réponses non vides ; aucune sauvegarde utilisateur chargée ni modifiée.")


if __name__ == "__main__":
    main()
