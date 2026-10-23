"""Ablation des lectures : mêmes signes physiques, avec/sans leurs interprétations.

Observe le registre réel des gestes et les rotations, pas seulement les souvenirs
encore en mémoire en fin de nuit. Les deux lots tournent successivement.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from priorite import ceder


def nuit(tache):
    depot, graine, lectures, sans = tache
    sys.path.insert(0, depot)
    from donjon import banc_pnj, pnj, signes
    from donjon.temps import instant
    ceder()
    evenements, rotations, gardes = [], [], set()
    commencer, temoins, regarder, lire = pnj.commencer_geste, pnj._temoins, signes.regarder, signes.lire
    place, surveiller, eprouver = signes.place, signes.surveiller, signes.eprouver

    def contexte(m):
        return {id: {"lieu": o["lieu"], "position": copy.deepcopy(o.get("position")),
                     "orientation": o.get("orientation"),
                     "guets_lus": copy.deepcopy(signes.intentions_lues(m, id))}
                for id, o in m.objets.items() if o["type"] == "personnage"}

    def commencer_geste(m, auteur, operation, objet, *a, **k):
        if not pnj.est_contrainte(m, operation, objet):
            evenements.append({"instant": instant(m), "type": "tentative", "auteur": auteur,
                               "operation": operation, "objet": objet, "contexte": contexte(m)})
        return commencer(m, auteur, operation, objet, *a, **k)

    def voir(m, geste, *a, **k):
        resultat = temoins(m, geste, *a, **k)
        cle = (geste["auteur"], geste["objet"], geste["operation"], geste["fin"], tuple(sorted(geste["temoins"])))
        if cle not in gardes and not pnj.est_contrainte(m, geste["operation"], geste["objet"]):
            gardes.add(cle)
            evenements.append({"instant": instant(m), "type": "temoins", "auteur": geste["auteur"],
                               "operation": geste["operation"], "objet": geste["objet"],
                               "fin": geste["fin"],
                               "temoins": sorted(geste["temoins"]), "contexte": contexte(m)})
        return resultat

    def tourner(m, id, i, cible, signe, sens, **k):
        avant = m.objets[id].get("orientation")
        resultat = regarder(m, id, i, cible, signe, sens, **k)
        if avant != m.objets[id].get("orientation"):
            rotations.append({"instant": instant(m), "pnj": id, "cible": cible, "signe": signe,
                              "avant": avant, "apres": m.objets[id].get("orientation"),
                              "guets_lus": copy.deepcopy(signes.intentions_lues(m, id))})
        return resultat

    pnj.commencer_geste, pnj._temoins, signes.regarder = commencer_geste, voir, tourner
    if not lectures:
        signes.lire = lambda *a, **k: None
        if sans == "signes":
            signes.place = lambda *a, **k: None
            signes.surveiller = lambda *a, **k: 0
            signes.regarder = lambda *a, **k: 0
            signes.eprouver = lambda *a, **k: None
    try:
        _, mesures, donnees = banc_pnj.nuit("mine", graine, 8, "galerie")
    finally:
        pnj.commencer_geste, pnj._temoins, signes.regarder, signes.lire = commencer, temoins, regarder, lire
        signes.place, signes.surveiller, signes.eprouver = place, surveiller, eprouver
    return {"graine": graine, "lectures": lectures, "mesures": mesures, "evenements": evenements,
            "mode": "complet" if lectures else "sans_" + sans,
            "code_moteur": hashlib.sha256(b"".join(p.read_bytes() for p in sorted(Path(signes.__file__).parent.glob("*.py")))).hexdigest(),
            "rotations": rotations, "chronique": donnees["chronique"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--depot", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--graines", type=int, nargs="+", default=[1985, 7, 42, 2024, 3, 11, 99, 500])
    p.add_argument("--processus", type=int, default=3)
    p.add_argument("--sans", choices=("lectures", "signes"), default="lectures",
                   help="lectures seules, ou lectures et choix physiques de place/regard de 3c")
    p.add_argument("--sortie", type=Path, required=True)
    args = p.parse_args()
    resultats = []
    for lectures in (True, False):
        with ProcessPoolExecutor(max_workers=max(1, min(3, args.processus)), max_tasks_per_child=1) as pool:
            for r in pool.map(nuit, [(str(Path(args.depot).resolve()), g, lectures, args.sans) for g in args.graines]):
                resultats.append(r)
                args.sortie.parent.mkdir(parents=True, exist_ok=True)
                args.sortie.write_text(json.dumps(resultats, ensure_ascii=False, indent=1), encoding="utf-8")
                print(r["graine"], lectures, len(r["evenements"]), flush=True)


if __name__ == "__main__":
    main()
