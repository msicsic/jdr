"""Empreintes et coût des nuits du banc : jouer deux versions du moteur, puis comparer nuit par nuit.

    python tools/empreintes_nuits.py jouer --depot . --sortie a.json --scenarios relais mine auberge crue \
        --graines 1985 7 42 2024 --departs tire fixe --heures 8 --processus 4 [--verifier] [--verification 0.2]
    python tools/empreintes_nuits.py comparer main.json branche.json [--calcul]
    python tools/empreintes_nuits.py profil --depot . --scenario mine --graine 7 --sortie mine.prof

``jouer`` joue chaque nuit par ``banc_pnj.nuit`` du dépôt donné (``--depot`` : un worktree ; le
même outil sert aux deux côtés), chacune dans son propre processus en priorité réduite, et garde :
l'empreinte de la chronique, des mesures, du récit, des souvenirs, de l'état final complet
(``monde.data``), les empreintes du banc (minutes repères et issue), recherches et nœuds du
planificateur ; puis le temps de la nuit au processeur (``process_time``) et le pic de mémoire du
processus. ``comparer`` dit, nuit par nuit, ce qui diffère (rien ne doit différer) et le temps
moyen de chaque côté. ``profil`` écrit le profil ``cProfile`` d'une nuit (au processeur).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

JOUEURS = {"relais": "chambre_cloche", "mine": "galerie", "auberge": "dortoir", "crue": "chambre_cloche",
           "rixe": "chambre_cloche"}
BELOW_NORMAL = 0x4000


def _pic_memoire():
    """Le pic de mémoire du processus, en Mo (Windows : PeakWorkingSetSize ; ailleurs ru_maxrss)."""
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class Compteurs(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
            c = Compteurs()
            c.cb = ctypes.sizeof(c)
            psapi = ctypes.WinDLL("psapi")
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Compteurs), wintypes.DWORD]
            noyau = ctypes.WinDLL("kernel32")
            noyau.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo(noyau.GetCurrentProcess(), ctypes.byref(c), c.cb)
            return round(c.PeakWorkingSetSize / 2 ** 20, 1)
        import resource
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    except Exception:
        return None


def _h(objet):
    import hashlib
    return hashlib.sha1(json.dumps(objet, sort_keys=True, ensure_ascii=False, default=repr).encode()).hexdigest()[:16]


def _preparer(depot, verifier, verification):
    sys.path.insert(0, os.path.abspath(depot))
    from donjon import planification, spatial
    planification.VERIFIER = verifier
    spatial.VERIFICATION = verification


def nuit(depot, scenario, graine, heures, depart, verifier=False, verification=0.0):
    """Une nuit dans ce processus : ses empreintes et son coût."""
    _preparer(depot, verifier, verification)
    from donjon import banc_pnj, deliberation, planification
    import hashlib
    trace, profondeur, appels = hashlib.sha1(), 0, 0
    chercher = planification.chercher

    def observer(*a, **k):
        nonlocal profondeur, appels
        exterieur = profondeur == 0
        profondeur += 1
        try:
            r = chercher(*a, **k)
        finally:
            profondeur -= 1
        if exterieur:
            resultat = None if r is None else [r[0], r[1], r[2].salle,
                sorted(r[2].portes), sorted([(list(c), v) for c, v in r[2].faits.items()], key=repr)]
            entree = [a[1], k.get("nom", ""), k.get("memo"), resultat]
            trace.update(json.dumps(entree, sort_keys=True, ensure_ascii=False).encode() + b"\n")
            appels += 1
        return r

    planification.chercher = observer
    capture, tranches = {}, []
    creer = banc_pnj.creer
    relever = banc_pnj._oisifs_urgents

    def _creer(*a, **k):
        capture["monde"] = creer(*a, **k)
        return capture["monde"]
    banc_pnj.creer = _creer
    debut = time.process_time()
    def _relever(monde):
        if monde.data["minutes"] >= 240 * (len(tranches) + 1):
            tranches.append(round(time.process_time() - debut, 4))
        return relever(monde)
    banc_pnj._oisifs_urgents = _relever
    try:
        _, mesures, donnees = banc_pnj.nuit(scenario, graine, heures, JOUEURS.get(scenario), False, True, None, depart)
    finally:
        banc_pnj.creer, banc_pnj._oisifs_urgents = creer, relever
    secondes = time.process_time() - debut
    monde = capture["monde"]
    recherches = donnees["diagnostic"]["recherches"]
    # Le mode strict conserve aussi les comptes de calcul. Quand la mémoire change, --calcul
    # compare à leur place tous les résultats des appels logiques (y compris les absences).
    neuves = [[r["pnj"], r["but"], r["noeuds"], r["issue"]] for r in recherches if not r.get("memoire")]
    # Les mesures sans les comptes de recherches et de choix (ce que le coût change, pas la nuit).
    nuit_seule = {k: v for k, v in mesures.items()
                  if k not in ("recherches", "recherches_neuves", "choix_minute", "choix_evenement")}
    return {"scenario": scenario, "graine": graine, "depart": depart, "heures": heures,
            "empreintes": {"chronique": _h(donnees["chronique"]), "mesures": _h(nuit_seule), "recit": _h(donnees["recit"]),
                           "souvenirs": _h(donnees["souvenirs"]), "etat": _h(monde.data),
                           "banc": _h(donnees["empreintes"]), "recherches_neuves": _h(neuves)},
            "mesures": mesures, "recherches": len(recherches), "neuves": len(neuves),
            "noeuds": sum(r["noeuds"] for r in recherches),
            "devis_differes": sum(r.get("devis_differes", 0) for r in recherches),
            "devis_developpes": sum(r.get("devis_developpes", 0) for r in recherches),
            "planificateur": round(sum(r.get("duree", 0.0) for r in recherches), 2),
            "choix": dict(deliberation.COMPTES), "secondes": round(secondes, 2), "memoire_mo": _pic_memoire(),
            "cpu_cumule_4h": tranches,
            "recherches_logiques": appels, "trace_recherches": trace.hexdigest()[:16],
            "impossibilites_reprises": sum(bool(r.get("impossible")) for r in recherches),
            "reprises_memoire": sum(bool(r.get("memoire")) for r in recherches),
            "reprises_graphe": sum(bool(r.get("graphe")) for r in recherches),
            "bornees": sum(r["issue"] == "borne" and not r.get("memoire") for r in recherches),
            "bornes_verifier": list(planification.BORNES),
            "epuisees": sum(r["issue"] == "epuise" and not r.get("memoire") for r in recherches),
            "preuves": sum(r.get("preuve_issue") is not None for r in recherches),
            "preuves_bornees": sum(r.get("preuve_issue") == "borne" for r in recherches),
            "noeuds_preuves": sum(r.get("preuve_noeuds", 0) for r in recherches)}


def _lancer(outil, depot, cle, heures, verifier, verification, python):
    scenario, graine, depart = cle
    commande = [python, outil, "_nuit", "--depot", depot, "--scenario", scenario, "--graine", str(graine),
                "--heures", str(heures), "--depart", depart, "--verification", str(verification)]
    if verifier:
        commande.append("--verifier")
    options = {"creationflags": BELOW_NORMAL} if os.name == "nt" else {"preexec_fn": lambda: os.nice(5)}
    sortie = subprocess.run(commande, capture_output=True, text=True, encoding="utf-8", **options)
    if sortie.returncode:
        return {"scenario": scenario, "graine": graine, "depart": depart, "erreur": sortie.stderr[-4000:]}
    return json.loads(sortie.stdout.strip().splitlines()[-1])


def jouer(args):
    cles = [(s, g, d) for d in args.departs for s in args.scenarios for g in args.graines]
    outil = os.path.abspath(__file__)
    python = args.python or sys.executable
    resultats = []
    with ThreadPoolExecutor(max_workers=args.processus) as pool:
        for r in pool.map(lambda c: _lancer(outil, args.depot, c, args.heures, args.verifier, args.verification, python), cles):
            etiquette = f'{r["scenario"]} {r["graine"]} {r["depart"]}'
            print(etiquette, "ERREUR" if "erreur" in r else f'{r["secondes"]} s, {r["memoire_mo"]} Mo', flush=True)
            if "erreur" in r:
                print(r["erreur"], flush=True)
            resultats.append(r)
    with open(args.sortie, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=1)
    return 1 if any("erreur" in r for r in resultats) else 0


def comparer(args):
    from pathlib import Path
    a, b = (json.loads(Path(x).read_text(encoding="utf-8")) for x in (args.a, args.b))
    cle = lambda r: (r["scenario"], r["graine"], r["depart"])
    da, db = {cle(r): r for r in a}, {cle(r): r for r in b}
    differences = 0
    temps = {}
    for k in sorted(set(da) & set(db), key=str):
        x, y = da[k], db[k]
        if "erreur" in x or "erreur" in y:
            print(k, "erreur d'un côté")
            differences += 1
            continue
        calcul = getattr(args, "calcul", False)
        champs = set(x["empreintes"]) | set(y["empreintes"])
        if calcul:
            champs |= {"chronique", "mesures", "recit", "souvenirs", "etat", "banc"}
            champs.discard("recherches_neuves")
        ecarts = [n for n in sorted(champs) if n not in x["empreintes"] or n not in y["empreintes"]
                  or x["empreintes"][n] != y["empreintes"][n]]
        if x.get("heures") != y.get("heures"):
            ecarts.append("heures")
        ecarts += [n for n in (("recherches_logiques", "trace_recherches") if calcul else ("neuves", "noeuds"))
                   if x.get(n) != y.get(n) or calcul and (n not in x or n not in y)]
        if ecarts:
            differences += 1
            print(k, "DIFFÈRE :", ", ".join(ecarts))
        t = temps.setdefault((k[0], k[2]), [[], [], [], [], [], []])
        for i, v in enumerate((x["secondes"], y["secondes"], x["planificateur"], y["planificateur"],
                               x["memoire_mo"] or 0, y["memoire_mo"] or 0)):
            t[i].append(v)
    manquent = set(da) ^ set(db)
    print(f"{len(set(da) & set(db))} nuits comparées, {differences} différentes"
          + (f" ({len(manquent)} d'un seul côté, non comparées)" if manquent else ""))
    moy = lambda v: sum(v) / len(v)
    print("scénario départ : temps A → B (planificateur A → B), pic mémoire A → B, rapport")
    for (s, d), t in sorted(temps.items()):
        print(f"{s} {d} : {moy(t[0]):.1f} → {moy(t[1]):.1f} s ({moy(t[2]):.1f} → {moy(t[3]):.1f}), "
              f"{max(t[4]):.0f} → {max(t[5]):.0f} Mo, × {moy(t[0]) / moy(t[1]):.2f}")
    return 1 if differences or manquent else 0


def profil(args):
    import cProfile
    _preparer(args.depot, False, 0.0)
    from donjon import banc_pnj
    banc_pnj.ceder()
    p = cProfile.Profile(time.process_time)
    p.enable()
    banc_pnj.nuit(args.scenario, args.graine, args.heures, JOUEURS.get(args.scenario), False, False, None, args.depart)
    p.disable()
    p.dump_stats(args.sortie)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sous = parser.add_subparsers(dest="commande", required=True)
    j = sous.add_parser("jouer")
    j.add_argument("--depot", default=".")
    j.add_argument("--sortie", required=True)
    j.add_argument("--scenarios", nargs="+", default=["relais", "mine", "auberge", "crue"])
    j.add_argument("--graines", type=int, nargs="+", default=[1985, 7, 42, 2024])
    j.add_argument("--departs", nargs="+", default=["tire", "fixe"])
    j.add_argument("--heures", type=float, default=8)
    j.add_argument("--processus", type=int, default=4)
    j.add_argument("--verifier", action="store_true")
    j.add_argument("--verification", type=float, default=0.0)
    j.add_argument("--python", help="interpréteur des nuits (défaut : celui-ci)")
    c = sous.add_parser("comparer")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--calcul", action="store_true", help="compare tous les résultats des recherches, coûts et plans ; "
                   "les comptes de calcul peuvent différer")
    p = sous.add_parser("profil")
    p.add_argument("--depot", default=".")
    p.add_argument("--scenario", required=True)
    p.add_argument("--graine", type=int, default=1985)
    p.add_argument("--heures", type=float, default=8)
    p.add_argument("--depart", default="tire")
    p.add_argument("--sortie", required=True)
    n = sous.add_parser("_nuit")
    n.add_argument("--depot", required=True)
    n.add_argument("--scenario", required=True)
    n.add_argument("--graine", type=int, required=True)
    n.add_argument("--heures", type=float, required=True)
    n.add_argument("--depart", required=True)
    n.add_argument("--verifier", action="store_true")
    n.add_argument("--verification", type=float, default=0.0)
    args = parser.parse_args(argv)
    if args.commande == "_nuit":
        r = nuit(args.depot, args.scenario, args.graine, args.heures, args.depart, args.verifier, args.verification)
        print(json.dumps(r, ensure_ascii=False))
        return 0
    return {"jouer": jouer, "comparer": comparer, "profil": profil}[args.commande](args)


if __name__ == "__main__":
    raise SystemExit(main())
