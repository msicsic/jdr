"""Une question à Luna sur un défi temporaire, sans toucher aux sauvegardes du joueur."""

import contextlib
import io
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

import jeu
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.spatial import position_cible


def main():
    sortie = io.StringIO()
    rapports = []
    propositions = []
    appeler_brut = MJOpenAI._appeler_brut

    def tracer(self, instructions, entree, intention, fonction, schema):
        resultat = appeler_brut(self, instructions, entree, intention, fonction, schema)
        if fonction == "repondre_au_joueur":
            propositions.append({"mode": resultat.get("mode"),
                                 "types": [a.get("type") for a in
                                           (resultat.get("proposition") or {}).get("ajouts", [])]})
        if fonction in ("auditer_narration", "auditer_portee"):
            rapports.append({"texte": entree.get("segments", entree.get("descriptions")),
                             "rapport": resultat})
        return resultat

    dialogue = "--dialogue" in sys.argv[1:]
    detail = "--detail" in sys.argv[1:]
    fixe = "--fixe" in sys.argv[1:]
    objet = "--objet" in sys.argv[1:] or fixe
    with tempfile.TemporaryDirectory(dir=RACINE) as dossier:
        chemin = Path(dossier) / "partie.json"
        if dialogue:
            monde = nouveau_monde()
            monde.joueur["salle"] = "echoppe"
            monde.sauver(chemin)
        phrase = ("mj Gorm, que peux-tu me dire sur ton échoppe ?" if dialogue else
                  "mj Décris un petit objet décoratif fixé aux murs près de moi, mais amovible à la main, sans lien avec la mission."
                  if fixe else
                  "mj Décris un petit objet libre, sans lien avec la mission, posé sur le sol près de moi."
                  if objet else
                  "mj Ajoute un détail décoratif visible sur les murs de cette pièce et décris-le." if detail else
                  "mj Que vois-je ?")
        with patch.object(MJOpenAI, "_appeler_brut", tracer), \
             patch("builtins.input", side_effect=[phrase, "quitter"]), \
             contextlib.redirect_stdout(sortie):
            arguments = ["--console", "--save", str(chemin), "--connexion", "auto"]
            code = jeu.main((["--defi"] if not dialogue else []) + arguments)
        monde = Monde.charger(chemin)
        narrations = monde.data.get("narrations_mj", [])
        print("Code :", code, "| narrations enregistrées :", len(narrations))
        details = [(o["nom"], o.get("description_visuelle")) for o in monde.objets.values()
                   if o.get("detail_local")]
        objets = [(o["id"], o["nom"], o["masse"], o["mobile"], o.get("relation_support"))
                  for o in monde.objets.values() if o.get("origine_description") == "MJ"
                  and o["type"] == "accessoire"]
        if detail:
            print("Détails créés :", details)
        if objet:
            print("Objets créés :", objets)
            print("Propositions :", propositions)
            print("Contrôles de portée :", [r["rapport"] for r in rapports
                                               if isinstance(r.get("rapport"), dict)
                                               and "descriptions" in r["rapport"]])
            if objets:
                id, nom, _, _, relation = objets[0]
                position_initiale = position_cible(monde, id)
                deplace = monde.copier()
                deplace.joueur["position"][0] += 1
                print("Position stable après déplacement :",
                      position_cible(deplace, id) == position_initiale)
                commandes = (["prendre " + nom, "détacher " + nom, "prendre " + nom, "quitter"]
                             if fixe else ["prendre " + nom, "quitter"])
                with patch("builtins.input", side_effect=commandes), \
                     contextlib.redirect_stdout(io.StringIO()) as sortie_actions:
                    code_prise = jeu.main(["--defi", "--console", "--offline", "--save", str(chemin)])
                reprise = Monde.charger(chemin)
                pris = code_prise == 0 and reprise.objets[id]["lieu"] == "joueur"
                bloque = not fixe or (relation == "fixe" and
                    "doit d'abord être détaché" in sortie_actions.getvalue())
                print("Prise initiale bloquée si fixé :", bloque)
                print("Ramassé et rechargé après détachement :", pris)
                if not (position_cible(deplace, id) == position_initiale and pris and bloque):
                    return 1
        if narrations:
            print("Dernière réponse :", narrations[-1]["texte"])
        else:
            texte = sortie.getvalue()
            reponse = texte.rsplit("Le MJ réfléchit…", 1)[-1]
            reponse = reponse.split("Partie sauvegardée.", 1)[0].strip()
            print("Réponse affichée :", reponse[:1000])
            if rapports:
                print("Dernier audit :", str(rapports[-1])[:1200])
        return 0 if code == 0 and (objets if objet else details if detail else narrations or (reponse and not dialogue)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
