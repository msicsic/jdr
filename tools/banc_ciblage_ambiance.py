"""Une passe G14 sur copies : deux détails publiés, puis une sensation diffuse.

    python tools/banc_ciblage_ambiance.py --sortie artifacts/g14-luna

Les ambiances de départ sont des données d'auteur admises par le contrat
commun. Luna choisit librement ses propositions dans la vraie boucle de jeu.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parent))

from tools import banc_parties
from donjon.faits_locaux import catalogue
from donjon.monde import Monde
from donjon.narration import consigner, controler


def main():
    from tools.priorite import ceder
    ceder()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=True)
    scripts = []
    for scenario, salle, position, orientation, support, nom, article in (
            ("relais", "antichambre", [1, 3], "est", "antichambre_sol", "pierre mouillée", "Une"),
            ("atelier", "cour", [2, 3], "nord", "cour_sol", "éclat de bois", "Un")):
        sauvegarde = args.sortie.resolve() / f"scene-{scenario}.json"
        banc_parties.preparer({"scenario": scenario, "seed": 1985,
                               "preparation": {"salle": salle, "position": position,
                                               "orientation": orientation}}, sauvegarde)
        m = Monde.charger(sauvegarde)
        # La position initiale propre au scénario garde le support à portée.
        if support not in catalogue(m)["supports"]:
            raise RuntimeError(f"Support de banc hors de portée : {support}")
        texte = f"{article} {nom} baigne dans une atmosphère feutrée, où flotte une odeur de terre."
        elements = [dict(id="detail", libelle=nom, ancrage=support, manipulable=True),
                    dict(id="sensation", libelle="odeur de terre", ancrage="", manipulable=False)]
        contexte = m.contexte()
        contexte["faits_narratifs_proposables"] = catalogue(m)
        audit = controler(texte, {"segments": {"0": {
            "verdict": "ambiance", "portee_mecanique": "aucune", "sources": [],
            "entites": elements}}}, contexte)
        audit.update(texte_initial=texte, faits=contexte, fondement="")
        avant = set(m.objets)
        consigner(m, {"texte": texte, "_audit": audit})
        assert set(m.objets) == avant
        m.sauver(sauvegarde)
        script = args.sortie.resolve() / f"g14-{scenario}.json"
        script.write_text(json.dumps({"scenario": scenario, "sauvegarde": str(sauvegarde),
            "seed": 1985, "tours": [f"mj je ramasse {nom}", "tenter",
                f"mj j'examine {nom}", "mj je ramasse cette odeur de terre", "quitter"]},
            ensure_ascii=False, indent=2), encoding="utf-8")
        scripts.append(str(script))
    return banc_parties.main([*scripts, "tests/data/bancs/luna-restes-ambiance.json",
                             "--connexion", "chatgpt", "--max-appels", "80", "--fil",
                             "--sortie", str(args.sortie / "luna")])


if __name__ == "__main__":
    raise SystemExit(main())
