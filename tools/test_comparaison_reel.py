"""Une question aux deux modèles (deux à quatre appels). Aucune partie modifiée."""
import copy
from pathlib import Path
import sys
from threading import Event

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.comparaison import Comparateur, texte_comparaison
from donjon.config import charger_env
from donjon.mj import MJOpenAI
from donjon.monde import nouveau_monde


def main():
    charger_env()
    sys.stdout.reconfigure(encoding="utf-8")
    fini = Event()
    def recevoir(fiche):
        if fiche["secondaire"]["statut"] in ("Terminé", "Erreur"):
            fini.set()
    c = Comparateur(MJOpenAI("gpt-6.1-sol", connexion="chatgpt"),
                   MJOpenAI("gpt-6-luna", connexion="chatgpt"), recevoir,
                   Path(__file__).resolve().parents[1] / "artifacts/comparaisons/test-reel")
    m = nouveau_monde()
    avant = copy.deepcopy(m.data)
    try:
        reponse = c.echanger(m, "De quelle couleur sont les yeux de Gorm ?")
        print("Principal terminé ; attente du résultat secondaire…", flush=True)
        assert fini.wait(55), "Le second modèle n'a pas terminé dans le délai du test."
        with c.verrou:
            fiche = copy.deepcopy(c.fiches[1])
        print(texte_comparaison(fiche), flush=True)
        assert m.data == avant, "La comparaison seule ne doit pas modifier le monde."
        assert fiche["secondaire"]["statut"] == "Terminé"
        assert fiche["principal"]["appels"][0]["empreinte_requete"] == fiche["secondaire"]["appels"][0]["empreinte_requete"]
        assert reponse["mode"] == "dialogue"
        print("Deux modèles vérifiés sur la même entrée. Aucune sauvegarde utilisateur modifiée.")
        print("Journal : " + str(c.chemin))
    finally:
        c.fermer()


if __name__ == "__main__":
    main()
