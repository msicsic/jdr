"""Interprétation du vol par Sol et Luna ; conséquences sur des copies sans sauvegarde."""
import copy
from pathlib import Path
import sys
from threading import Event
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.comparaison import Comparateur
from donjon.config import charger_env
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--connexion", default="local")
    parser.add_argument("--modele", default=None)
    args = parser.parse_args()
    monde = nouveau_monde()
    monde.joueur["salle"] = "echoppe"
    monde.memoriser("Puis-je voler des crochets ?", "Le vol n'est pas pris en charge par le moteur.")
    avant = copy.deepcopy(monde.data)
    message = "j'attens que Gorm ait le dos tourné pour discretement prendre la trousse de crochets"

    if args.connexion != "chatgpt" or args.modele:
        mj = MJOpenAI(args.modele, connexion=args.connexion)
        reponse = mj.echanger(monde, message)
        assert reponse["mode"] == "action", reponse
        p = reponse["proposition"]
        assert p["action"] == "composer", p
        assert [e["operation"] for e in p["etapes"]] == ["patienter", "deplacer"], p
        assert p["etapes"][1]["cible"] == "crochets" and p["etapes"][1]["methode"] == "discret", p
        print(f"Modèle ({args.connexion}) : " + Moteur(monde).preparer(p).resume(monde), flush=True)
        for jet in (20, 1):
            copie = monde.copier()
            moteur = Moteur(copie)
            with patch.object(Monde, "d20", return_value=jet):
                resultat = moteur.executer(moteur.preparer(p))
            assert copie.objets["crochets"]["lieu"] == ("joueur" if jet == 20 else "echoppe")
            assert copie.data["relations_pnj"]["marchand"]["vols_surpris"] == (0 if jet == 20 else 1)
            print(resultat, flush=True)
        assert monde.data == avant
        print("Intention comprise par le modèle ; réussite et échec vérifiés avec dés imposés sur des copies. Aucune sauvegarde utilisateur modifiée.")
        return

    fini = Event()
    c = Comparateur(MJOpenAI("gpt-6.1-sol", connexion="chatgpt"), MJOpenAI("gpt-6-luna", connexion="chatgpt"),
                    publier=lambda f: fini.set() if f["secondaire"]["statut"] in ("Terminé", "Erreur") else None,
                    dossier=Path(__file__).resolve().parents[1] / "artifacts/comparaisons/test-reel")
    message = "j'attens que Gorm ait le dos tourné pour discretement prendre la trousse de crochets"
    try:
        c.echanger(monde, message)
        assert fini.wait(50), "Délai du secondaire"
        with c.verrou:
            fiche = copy.deepcopy(c.fiches[1])
        for role in ("principal", "secondaire"):
            r = fiche[role]
            assert r["statut"] == "Terminé", r
            reponse = r["reponse"]
            assert reponse["mode"] == "action", reponse
            p = reponse["proposition"]
            assert p["action"] == "composer", p
            assert [e["operation"] for e in p["etapes"]] == ["patienter", "deplacer"], p
            assert p["etapes"][1]["cible"] == "crochets" and p["etapes"][1]["methode"] == "discret", p
            print(r["modele"] + " : " + Moteur(monde).preparer(p).resume(monde), flush=True)
            for jet in (20, 1):
                copie = monde.copier()
                moteur = Moteur(copie)
                with patch.object(Monde, "d20", return_value=jet):
                    resultat = moteur.executer(moteur.preparer(p))
                assert copie.objets["crochets"]["lieu"] == ("joueur" if jet == 20 else "echoppe")
                assert copie.data["relations_pnj"]["marchand"]["vols_surpris"] == (0 if jet == 20 else 1)
                print(resultat, flush=True)
        assert monde.data == avant
        print("Intention comprise par les deux modèles ; réussite et échec vérifiés avec dés imposés sur des copies. Aucune sauvegarde utilisateur modifiée.")
    finally:
        c.fermer()


if __name__ == "__main__":
    main()
