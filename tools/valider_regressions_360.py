"""Vérifications bornées du lot 360 ; deux travailleurs, priorité réduite, fin écrite en dernier."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from priorite import ceder

TESTS = ("amener_flamme", "appel_negocie", "appeler_donneur", "boucles_pnj",
         "deliberation_evenements", "dynamique_besoins", "entretenir", "etapes_chainees",
         "gardien_detresse", "intermediaires", "ouie", "ouie_temoins", "recours_prioritaire",
         "soi_meme", "tenir", "voix", "nouvelles_initiales", "garde_ouidire", "constats_partages",
         "agendas_fins", "agendas_socle", "constater_rumeurs", "defense", "detecter_changements_avis",
         "propositions_redites", "refus_retenus", "social", "tache_promise_recours",
         "deja_dit", "parole_commune", "esprits")


def ecrire(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding="utf-8")


def empreintes():
    fichiers = [*sorted((RACINE / "donjon").rglob("*.py")),
                RACINE / "tests/support.py",
                *[RACINE / f"tests/test_{t}.py" for t in (*TESTS, "passage")]]
    return {str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sortie", type=Path, required=True)
    p.add_argument("--reference", default="origin/main")
    args = p.parse_args()
    ceder()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    debut = time.monotonic()
    fin = {"ok": False, "pid": os.getpid()}
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    def executer(nom, commande):
        with (sortie / (nom + ".log")).open("w", encoding="utf-8") as f:
            return subprocess.run([sys.executable, *commande], cwd=RACINE,
                                  stdout=f, stderr=subprocess.STDOUT, env=env).returncode
    try:
        avant = empreintes()
        ecrire(sortie / "debut.json", {"pid": os.getpid(), "sources": avant,
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RACINE, text=True).strip(),
            "reference": args.reference})
        fin["tests_code"] = executer("tests", ["tools/tests.py", "--processus", "2", "--sortie",
            str(sortie / "tests.json"), *[f"tests/test_{t}.py" for t in TESTS]])
        # Le fichier de passage appartient aussi au 361 : seuls les témoins
        # du passage spontané sont rejoués ici, aucun portage du dialogue.
        fin["passage_code"] = executer("passage", ["-m", "unittest",
            "tests.test_passage.LaisserPasserJoueurTests", "-v"])
        fin["empreintes_code"] = executer("empreintes", ["tools/comparer_bancs.py", "--reference",
            args.reference, "--empreintes", "--heures", "2", "--processus", "2", "--scenarios",
            "relais", "mine", "auberge", "crue", "crue_hameau", "--graines", "1985", "7", "42", "2024",
            "--sortie", str(sortie / "empreintes.json")])
        if (sortie / "empreintes.json").exists():
            banc = json.loads((sortie / "empreintes.json").read_text(encoding="utf-8"))
            mesures = []
            for a, b in zip(banc["reference"]["nuits"], banc["branche"]["nuits"]):
                def constats(n):
                    return ((n.get("donnees") or {}).get("mesures") or {}).get("constats_confies")
                mesures.append({"scenario": b["scenario"], "graine": b["graine"],
                    "constats_reference": constats(a), "constats_branche": constats(b),
                    "plantage_reference": a["plantage"], "plantage_branche": b["plantage"]})
            ecrire(sortie / "constats-confies.json", mesures)
            fin["banc_sans_plantage"] = all(not n["plantage_reference"] and not n["plantage_branche"] for n in mesures)
            fin["divergence"] = banc["divergence"]
        fin["sources_stables"] = avant == empreintes()
        fin["ok"] = (fin["tests_code"] == fin["passage_code"] == 0
                     and fin.get("banc_sans_plantage", False) and fin["sources_stables"])
    except BaseException:
        fin["erreur"] = traceback.format_exc()
    finally:
        fin["secondes"] = time.monotonic() - debut
        ecrire(sortie / "fin.json", fin)
    return int(not fin["ok"])


if __name__ == "__main__":
    raise SystemExit(main())
