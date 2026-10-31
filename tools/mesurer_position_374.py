"""Banc borné du lot 374, références en cache, puis VERIFIER sur une heure.

    python tools/mesurer_position_374.py --sortie C:/Users/msics/donjon/artifacts/position-hypothese-374

Deux travailleurs au plus, priorité réduite. Le lanceur détaché écrit le fichier
de fin après ce programme ; aucune sauvegarde de joueur n'est ouverte.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import time

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from priorite import ceder


def ecrire(chemin, contenu):
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2), encoding="utf-8")


def analyser(rapport):
    """Relevés comparables et nouveaux constats à lire, sans certificat automatique de non-boucle."""
    nuits = {}
    for cote in ("reference", "branche"):
        for n in rapport[cote]["nuits"]:
            cle = (n["scenario"], n["graine"])
            appels = Counter((c["pnj"], c["texte"]) for c in (n.get("donnees") or {}).get("chronique", [])
                             if " appelle : « " in c["texte"])
            nuits.setdefault(cle, {})[cote] = {
                "plantage": n["plantage"], "boucles": n.get("boucles"),
                "classes_retours": (n.get("avis") or {}).get("comptes"),
                "non_justifies": (n.get("avis") or {}).get("total_non_justifies"),
                "appels": [{"pnj": a, "texte": t, "nombre": nombre}
                           for (a, t), nombre in sorted(appels.items())],
                "constats": n.get("constats"),
                "mesures": (n.get("donnees") or {}).get("mesures"),
            }
    return {"limite": "Les nouveaux constats et appels répétés demandent une lecture des chroniques du banc.",
            "nuits": [{"scenario": s, "graine": g, **cotes} for (s, g), cotes in nuits.items()]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", required=True, type=Path)
    parser.add_argument("--revision", default="HEAD", help="commit de branche figé au lancement")
    parser.add_argument("--reference", default="origin/main", help="main distant, le main local de ce poste est ancien")
    parser.add_argument("--base", default="b83f5a5933850907a6a1d7388cf1966944c665f0")
    parser.add_argument("--historique", type=Path, help="rapport ancien : réutiliser sa référence sans la rejouer")
    args = parser.parse_args()
    dossier = args.sortie.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    ceder()
    from donjon import banc_pnj, planification
    planification.VERIFIER = True
    debut = time.perf_counter()
    _, _, donnees = banc_pnj.nuit("relais", 7, 1, "chambre_cloche", depart="tire")
    ecrire(dossier / "verifier-1h.json", {"scenario": "relais", "graine": 7, "heures": 1,
                                         "succes": True, "secondes": time.perf_counter() - debut,
                                         "donnees": donnees})
    # main local est ancien et incompatible avec l'audit courant. La base exacte isole le lot ; les
    # mêmes nuits de branche sont relues du cache, jamais jouées deux fois.
    for nom, reference in (("banc-reference", args.reference), ("banc-base", args.base)):
        if nom == "banc-base" and args.historique:
            ancien = json.loads(args.historique.read_text(encoding="utf8"))
            courant = json.loads((dossier / "banc-reference.json").read_text(encoding="utf8"))
            rapport = {"config": courant["config"], "reference": ancien["reference"],
                       "branche": courant["branche"], "provenance_reference": str(args.historique),
                       "limite": "Référence historique relue sans rejeu ; instrumentation et intégration ont évolué. "
                                 "Le comparatif isolant le lot est banc-reference.json. Aucun temps comparé."}
            ecrire(dossier / (nom + ".json"), rapport)
            ecrire(dossier / ("analyse-" + nom + ".json"), analyser(rapport))
            continue
        commande = [sys.executable, str(RACINE / "tools/comparer_bancs.py"),
                    "--reference", reference, "--branche", args.revision, "--heures", "4",
                    "--scenarios", "relais", "auberge", "mine", "crue",
                    "--graines", "1985", "7", "42", "2024", "--processus", "2",
                    "--sortie", str(dossier / (nom + ".json"))]
        with (dossier / (nom + ".stdout.txt")).open("w", encoding="utf-8") as sortie, \
                (dossier / (nom + ".stderr.txt")).open("w", encoding="utf-8") as erreurs:
            resultat = subprocess.run(commande, cwd=RACINE, stdout=sortie, stderr=erreurs)
        if (dossier / (nom + ".json")).exists():
            rapport = json.loads((dossier / (nom + ".json")).read_text(encoding="utf-8"))
            ecrire(dossier / ("analyse-" + nom + ".json"), analyser(rapport))
        if resultat.returncode:
            return resultat.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
