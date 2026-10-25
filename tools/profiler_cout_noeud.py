"""Même recherche Joss/faim depuis la capture de 8 h, dans un dépôt donné.

Le profil et le témoin sans profileur utilisent deux processus distincts.
"""
import argparse
import cProfile
import gzip
import json
from pathlib import Path
import pstats
import sys
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--depot", required=True)
    p.add_argument("--sortie", required=True)
    p.add_argument("--profil", action="store_true")
    p.add_argument("--repetitions", type=int, default=20)
    p.add_argument("--capture", default="tests/data/cout-12h/auberge-1985-480.json.gz")
    p.add_argument("--lignes", action="store_true", help="Temps inclusif par ligne de gestes (passe séparée)")
    args = p.parse_args()
    sys.path.insert(0, str(Path(args.depot).resolve()))
    from donjon import banc_pnj, planification as plan
    from donjon.monde import Monde
    banc_pnj.ceder()
    capture = Path(args.capture).resolve()
    monde = Monde(json.loads(gzip.decompress(capture.read_bytes())))
    profileur = cProfile.Profile() if args.profil else None
    lignes, precedent = {}, [None, None]
    def tracer(frame, event, arg):
        if frame.f_code is not plan.gestes.__code__:
            return None
        maintenant = time.perf_counter()
        if event == "call":
            precedent[:] = [None, maintenant]
        else:
            ligne, instant = precedent
            if ligne is not None:
                lignes[ligne] = lignes.get(ligne, 0) + maintenant - instant
            precedent[:] = [frame.f_lineno if event == "line" else None, maintenant]
        return tracer
    debut = time.process_time()
    with plan.diagnostics() as diagnostics:
        if profileur:
            profileur.enable()
        if args.lignes:
            sys.settrace(tracer)
        for _ in range(args.repetitions):
            resultat = plan.chercher(monde, "joss", plan.a_mange, nom="faim", emplois=("manger",), motif="faim")
        if profileur:
            profileur.disable()
        sys.settrace(None)
    duree = time.process_time() - debut
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    noeuds = sum(r["noeuds"] for r in diagnostics)
    donnees = {"cpu": duree, "repetitions": args.repetitions, "noeuds": noeuds,
               "microsecondes_par_noeud": duree * 1e6 / noeuds,
               "diagnostics": diagnostics, "resultat": repr(resultat)}
    if args.lignes:
        import linecache
        donnees["lignes"] = [{"ligne": n, "microsecondes_par_noeud": t * 1e6 / noeuds,
                              "code": linecache.getline(plan.__file__, n).strip()}
                             for n, t in sorted(lignes.items())]
    if profileur:
        profileur.dump_stats(str(sortie.with_suffix(".prof")))
        stats = pstats.Stats(profileur)
        donnees["fonctions"] = sorted([
            {"fichier": f, "ligne": l, "nom": n, "appels": nc, "propre": tt, "cumule": ct}
            for (f, l, n), (cc, nc, tt, ct, callers) in stats.stats.items()],
            key=lambda x: -x["cumule"])
    sortie.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in donnees.items()
                      if k not in ("fonctions", "diagnostics", "resultat", "lignes")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
