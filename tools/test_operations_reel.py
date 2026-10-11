"""Nouvelle combinaison avec les deux MJ, puis récit d'un échec partiel réel du moteur."""
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
    monde = nouveau_monde()
    avant = copy.deepcopy(monde.data)
    fini = Event()
    c = Comparateur(MJOpenAI("gpt-6.1-sol", connexion="chatgpt"), MJOpenAI("gpt-6-luna", connexion="chatgpt"),
                    publier=lambda f: fini.set() if f["secondaire"]["statut"] in ("Terminé", "Erreur") else None,
                    dossier=Path(__file__).resolve().parents[1] / "artifacts/comparaisons/test-reel")
    try:
        r = c.echanger(monde, "J'utilise mon couteau pour retirer successivement l'axe du haut puis celui du bas, en les laissant au sol.")
        assert fini.wait(50)
        with c.verrou:
            fiche = copy.deepcopy(c.fiches[1])
        for role in ("principal", "secondaire"):
            resultat = fiche[role]
            assert resultat["statut"] == "Terminé", resultat
            p = resultat["reponse"]["proposition"]
            assert p["action"] == "composer", p
            assert [(e["operation"], e["cible"]) for e in p["etapes"]] == [("detacher", "axe_haut"), ("detacher", "axe_bas")], p
            print(resultat["modele"] + "\n" + Moteur(monde).preparer(p).resume(monde), flush=True)
        assert monde.data == avant
        travail = monde.copier()
        moteur = Moteur(travail)
        with patch.object(Monde, "d20", side_effect=[20, 1]):
            print(moteur.executer(moteur.preparer(r["proposition"])), flush=True)
        assert not travail.objets["axe_haut"]["attache"] and travail.objets["axe_bas"]["attache"]
        assert not travail.objets["porte"]["ouverte"]
        fini.clear()
        apres = copy.deepcopy(travail.data)
        c.raconter_resultat(travail, travail.data["journal"][-1])
        assert fini.wait(50)
        with c.verrou:
            fiche = copy.deepcopy(c.fiches[2])
        for role in ("principal", "secondaire"):
            resultat = fiche[role]
            assert resultat["statut"] == "Terminé", resultat
            print(resultat["modele"] + " — récit : " + resultat["reponse"]["texte"], flush=True)
        assert travail.data == apres and monde.data == avant
        print("Combinaison nouvelle et narration de l'échec partiel vérifiées. Aucune sauvegarde utilisateur modifiée.")
    finally:
        c.fermer()


if __name__ == "__main__":
    main()
