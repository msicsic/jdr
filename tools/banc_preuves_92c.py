"""CPU 92 c : deux versions lancées ensemble, deux processus de calcul au plus.

Les archives 42bb9c0 et 9810f4a sont dans artifacts/versions92c. Aucun cache
de temps n'est utilisé. Deux cohortes : ancien/branche puis base/branche.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference", choices=("ancien", "base"), required=True)
    ap.add_argument("--nuits", nargs="+", default=["auberge-tire", "auberge-fixe", "mine-tire", "mine-fixe"])
    ap.add_argument("--dossier", required=True)
    args = ap.parse_args()
    racine = Path(__file__).resolve().parents[1]
    dossier = Path(args.dossier).resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    depots = {args.reference: racine / "artifacts/versions92c" / args.reference, "branche": racine}
    for depot in depots.values():
        assert (depot / "donjon/planification.py").is_file(), depot
    conditions = {"debut": time.time(), "reference": args.reference, "processus_max": 2,
                  "cpu_count": os.cpu_count(), "cache": False, "nuits": args.nuits,
                  "planification_sha256": {nom: hashlib.sha256((depot / "donjon/planification.py").read_bytes()).hexdigest()
                                           for nom, depot in depots.items()}}
    (dossier / f"conditions-{time.time_ns()}.json").write_text(json.dumps(conditions, indent=2), encoding="utf8")
    if not (dossier / "conditions.json").exists():
        (dossier / "conditions.json").write_text(json.dumps(conditions, indent=2), encoding="utf8")
    agregats = {nom: [] for nom in depots}
    for nom in agregats:
        fichier = dossier / f"{nom}-comparer.json"
        if fichier.exists():
            agregats[nom] = json.loads(fichier.read_text(encoding="utf8"))
    for nuit in args.nuits:
        scenario, depart = nuit.split("-")
        assert scenario in ("auberge", "mine") and depart in ("fixe", "tire")
        ouvriers, flux = {}, []
        for nom, depot in depots.items():
            log = (dossier / f"{nom}-{nuit}.log").open("w", encoding="utf8")
            flux.append(log)
            commande = [sys.executable, str(racine / "tools/mesurer_attente_bornee.py"),
                        "--cout", "--depot", str(depot), "--scenario", scenario,
                        "--depart", depart, "--graine", "1985", "--heures", "12",
                        "--sortie", str(dossier / f"{nom}-{nuit}.json")]
            ouvriers[nom] = subprocess.Popen(commande, cwd=racine, stdout=log, stderr=subprocess.STDOUT,
                                            creationflags=0x4000 if os.name == "nt" else 0,
                                            env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        codes = {nom: ouvrier.wait() for nom, ouvrier in ouvriers.items()}
        for f in flux:
            f.close()
        if any(codes.values()):
            for nom, code in codes.items():
                if code:
                    print((dossier / f"{nom}-{nuit}.log").read_text(encoding="utf8")[-6000:])
            return 1
        for nom in depots:
            r = json.loads((dossier / f"{nom}-{nuit}.json").read_text(encoding="utf8"))
            assert all(r["recharge"].values()), r["recharge"]
            agregats[nom] = [x for x in agregats[nom] if (x["scenario"], x["depart"]) != (scenario, depart)]
            agregats[nom].append(r["resume"])
            (dossier / f"{nom}-comparer.json").write_text(json.dumps(agregats[nom], ensure_ascii=False, indent=2), encoding="utf8")
        print(nuit, {nom: agregats[nom][-1]["secondes"] for nom in depots}, flush=True)
        if args.reference == "base":
            a, b = (agregats[nom][-1] for nom in ("base", "branche"))
            for champ in ("chronique", "mesures", "recit", "souvenirs", "etat", "banc"):
                assert a["empreintes"][champ] == b["empreintes"][champ], (nuit, champ)
            for champ in ("recherches_logiques", "trace_recherches"):
                assert a[champ] == b[champ], (nuit, champ)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
