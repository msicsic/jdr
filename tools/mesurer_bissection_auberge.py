"""Détails d'une nuit historique, avec le lanceur commun empreintes_nuits.

    python tools/mesurer_bissection_auberge.py --depot WORKTREE --sortie RESULTAT.json

Un processus neuf par invocation, priorité réduite ; aucun appel au modèle.
Les durées diagnostiques sont ici CPU (l'horloge du diagnostic seule est remplacée).
La sérialisation des bruts et le contrôle de recharge sont hors du chronométrage.
"""
import argparse
import ctypes
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

import empreintes_nuits as empreintes


def mesurer(depot, heures=12, scenario="auberge"):
    empreintes._preparer(depot, False, 0.0)
    from donjon import banc_pnj, planification
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue

    banc_pnj.ceder()
    capture = {}
    creer, nuit = banc_pnj.creer, banc_pnj.nuit
    horloge = planification.perf_counter

    def creer_observe(*a, **k):
        capture["monde"] = creer(*a, **k)
        return capture["monde"]

    def nuit_observee(*a, **k):
        resultat = nuit(*a, **k)
        capture["donnees"] = resultat[2]
        return resultat

    banc_pnj.creer, banc_pnj.nuit = creer_observe, nuit_observee
    planification.perf_counter = time.process_time
    try:
        resume = empreintes.nuit(depot, scenario, 1985, heures, "fixe")
    finally:
        banc_pnj.creer, banc_pnj.nuit = creer, nuit
        planification.perf_counter = horloge

    monde = capture["monde"]
    vue, scene = regarder(monde), scene_percue(monde)
    temporaires = Path(__file__).resolve().parents[1] / "artifacts/bissection-auberge"
    temporaires.mkdir(parents=True, exist_ok=True)
    tmp = temporaires / ("recharge-" + uuid.uuid4().hex)
    tmp.mkdir()
    fichier = tmp / "partie.json"
    try:
        monde.sauver(fichier)
        recharge = Monde.charger(fichier)
    finally:
        fichier.unlink(missing_ok=True)
        fichier.with_suffix(".json.tmp").unlink(missing_ok=True)
        tmp.rmdir()
    controle = {"monde": monde.data == recharge.data,
                "regarder": vue == regarder(recharge),
                "scene": scene == scene_percue(recharge)}
    if not all(controle.values()):
        raise AssertionError(controle)
    recherches = capture["donnees"]["diagnostic"]["recherches"]
    groupes = {}
    for r in recherches:
        g = groupes.setdefault((r["pnj"], r["but"]), {
            "pnj": r["pnj"], "but": r["but"], "recherches": 0, "neuves": 0,
            "noeuds": 0, "preuves_noeuds": 0, "bornees": 0, "cpu": 0.0,
            "cpu_neuves": 0.0, "issues": {}})
        g["recherches"] += 1
        g["neuves"] += not r.get("memoire")
        g["noeuds"] += r["noeuds"]
        g["preuves_noeuds"] += r.get("preuve_noeuds", 0)
        g["bornees"] += r["issue"] == "borne" and not r.get("memoire")
        g["cpu"] += r["duree"]
        g["cpu_neuves"] += r["duree"] if not r.get("memoire") else 0
        g["issues"][r["issue"]] = g["issues"].get(r["issue"], 0) + 1
    return {"commit": subprocess.check_output(
                ["git", "-C", str(depot), "rev-parse", "HEAD"], text=True).strip(),
            "resume": resume, "groupes": sorted(groupes.values(), key=lambda g: -g["cpu"]),
            "recharge": controle, "rendu": {"regarder": vue, "scene": scene},
            "monde": monde.data, "donnees": capture["donnees"],
            "horloge_diagnostic": "process_time"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--depot", required=True)
    p.add_argument("--sortie", required=True)
    p.add_argument("--heures", type=float, default=12)
    p.add_argument("--scenario", default="auberge")
    p.add_argument("--affinite", type=lambda x: int(x, 0),
                   help="masque CPU Windows, par exemple 0x11 ; à fixer pareil pour les deux versions")
    args = p.parse_args()
    if args.affinite is not None:
        if os.name != "nt":
            p.error("--affinite est réservé à Windows")
        noyau = ctypes.WinDLL("kernel32", use_last_error=True)
        noyau.GetCurrentProcess.restype = ctypes.c_void_p
        noyau.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        if not noyau.SetProcessAffinityMask(noyau.GetCurrentProcess(), args.affinite):
            raise ctypes.WinError(ctypes.get_last_error())
    r = mesurer(str(Path(args.depot).resolve()), args.heures, args.scenario)
    r["affinite_demandee"] = args.affinite
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"commit": r["commit"][:7], **r["resume"], "recharge": r["recharge"]},
                     ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
