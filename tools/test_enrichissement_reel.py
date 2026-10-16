"""Trois questions, au plus six appels réels ; partie temporaire uniquement."""
import copy
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.config import charger_env
from donjon.enrichissement import preparer_complements
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire
from donjon.transactions import du_type


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    mj = MJOpenAI(connexion="chatgpt")
    m = nouveau_monde()
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        def echanger(question, attendu):
            nonlocal m
            avant = copy.deepcopy(m.data)
            reponse = mj.echanger(m, question)
            assert m.data == avant
            assert reponse["mode"] == "dialogue"
            assert (du_type(reponse, "complements") is not None) == attendu, reponse
            if attendu:
                ajout = du_type(reponse, "complements")
                m = preparer_complements(m, ajout["proposition"], ajout["revision"])
                print("Ajouts validés : " + str(ajout["proposition"]), flush=True)
            m.memoriser(question, reponse["texte"])
            m.sauver(chemin)
            m = Monde.charger(chemin)
            print("Corvus > " + question + "\n" + reponse["texte"] + "\n", flush=True)

        echanger("De quelle couleur sont les yeux de Gorm ?", True)
        yeux = copy.deepcopy(m.objets["detail_marchand_yeux"])
        echanger("Rappelle-moi la couleur de ses yeux.", False)
        assert m.objets["detail_marchand_yeux"] == yeux
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition("aller", "ouest")))
        print("Examen local après rechargement : " + decrire(m, "detail_marchand_yeux", detail=True), flush=True)
        m.objets["mira"] = objet("mira", "Mira", "personnage", "echoppe", aliases=["mira"])
        echanger("Elle est comment, Mira ? Décris-moi son apparence.", True)
        print("Examen local : " + decrire(m, "mira", detail=True), flush=True)
        assert m.objets["mira"].get("facettes")
    print("Trois échanges vérifiés ; aucune sauvegarde utilisateur modifiée.")


if __name__ == "__main__":
    main()
