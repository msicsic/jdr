"""Savoir d'auteur, invention et rappel après rechargement avec Luna ; partie temporaire."""
import copy
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.config import charger_env
from donjon.connaissances import preparer_savoirs
from donjon.dialogues import preparer_conversation
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    m = nouveau_monde()
    m.joueur["salle"] = "echoppe"
    m.memoriser("Comment ouvrir la porte ?", "Gorm : « Je ne sais pas comment l'ouvrir. »")
    mj = MJOpenAI("gpt-6-luna", connexion="chatgpt")
    journal = Path(__file__).resolve().parents[1] / "artifacts/tests/savoirs-luna.jsonl"
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open("w", encoding="utf-8") as traces, tempfile.TemporaryDirectory() as tmp:
        def tracer(trace):
            traces.write(json.dumps(trace, ensure_ascii=False) + "\n")
            traces.flush()
        mj.observateur = tracer
        for numero, message in enumerate((
            "Gorm, comment ouvrir la porte verrouillée au nord de l'antichambre ?",
            "Gorm, pourquoi tiens-tu personnellement à retrouver cet anneau ?",
            "Gorm, rappelle-moi pourquoi tu tiens personnellement à retrouver cet anneau.",
        )):
            avant = copy.deepcopy(m.data)
            r = mj.echanger(m, message)
            assert m.data == avant
            assert r["mode"] == "dialogue" and r["texte"].strip(), r
            if numero == 0:
                assert "crochet" in r["texte"].lower() or "gond" in r["texte"].lower(), r
            elif numero == 1:
                assert "_savoirs" in r, r
                p = r["_savoirs"]
                m = preparer_savoirs(m, p["proposition"], p["revision"])
                savoirs = copy.deepcopy(m.data["savoirs_pnj"])
                print("Savoir enregistré : " + json.dumps(p["proposition"], ensure_ascii=False), flush=True)
                path = Path(tmp) / "partie.json"
                m.sauver(path)
                m = Monde.charger(path)
                m.data["conversation"] = []
            else:
                assert "_savoirs" not in r, r
                assert m.data["savoirs_pnj"] == savoirs
            if "_conversation_pnj" in r:
                p = r["_conversation_pnj"]
                m, _ = preparer_conversation(m, p["proposition"], p["revision"])
            print(message + "\n" + r["texte"] + "\n", flush=True)
    print("Connaissance d'auteur, ajout du MJ et rappel sans historique vérifiés. Aucune partie utilisateur modifiée.")


if __name__ == "__main__":
    main()
