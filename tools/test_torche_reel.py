"""La phrase exacte du joueur avec les deux modèles ; aucun accès à sa sauvegarde."""
import copy
from pathlib import Path
import sys
from threading import Event

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.comparaison import Comparateur
from donjon.config import charger_env
from donjon.mj import MJOpenAI
from donjon.monde import nouveau_monde
from donjon.moteur import Moteur


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    m = nouveau_monde()
    m.memoriser("je prend la torche et l'allume", "Le moteur ne permet pas de combiner un déplacement et un allumage.")
    avant = copy.deepcopy(m.data)
    fini = Event()
    c = Comparateur(MJOpenAI("gpt-6.1-sol", connexion="chatgpt"), MJOpenAI("gpt-6-luna", connexion="chatgpt"),
                    publier=lambda f: fini.set() if f["secondaire"]["statut"] in ("Terminé", "Erreur") else None,
                    dossier=Path(__file__).resolve().parents[1] / "artifacts/comparaisons/test-reel")
    try:
        c.echanger(m, "je prend la torche et l'allume")
        assert fini.wait(50)
        with c.verrou:
            fiche = copy.deepcopy(c.fiches[1])
        for role in ("principal", "secondaire"):
            r = fiche[role]
            assert r["statut"] == "Terminé", r
            p = r["reponse"]["proposition"]
            assert p["action"] == "composer", p
            assert [(e["operation"], e["cible"]) for e in p["etapes"]] == [("deplacer", "torche"), ("allumer", "torche")], p
            copie = m.copier()
            moteur = Moteur(copie)
            plan = moteur.preparer(p)
            assert not plan.stat and not plan.echec_critique
            print(r["modele"] + " :\n" + moteur.executer(plan), flush=True)
            assert copie.objets["torche"]["lieu"] == "joueur" and copie.objets["torche"]["allume"]
            assert copie.data["minutes"] == 2 and copie.data["jets"] == 0
        assert m.data == avant
        print("Prise et allumage compris par les deux modèles, sans jet ni confirmation supplémentaire. Aucune partie utilisateur modifiée.")
    finally:
        c.fermer()


if __name__ == "__main__":
    main()
