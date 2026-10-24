"""Inventaires développés sur les captures, avant le lot 52 (sans appel au modèle)."""
import collections
import gzip
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import planification as p, pnj
from donjon.monde import Monde
from tools.priorite import ceder
from tools.verifier_capacites import anciennes


def categories(o):
    r = set(o.get("usages", ())) & set(p.USAGES)
    if "allume" in o:
        r.add("lumiere")
    if o.get("ouvre"):
        r.add("cle")
    if o["type"] in ("nourriture", "contenant"):
        r.add(o["type"])
    if "pieces" in o:
        r.add("monnaie")
    return r or {"autre"}


def mesurer(scenario):
    m = Monde(json.loads(gzip.decompress((Path("tests/data/cout-12h") /
                                        f"{scenario}-1985-480.json.gz").read_bytes())))
    comptes, objets, nombres = collections.Counter(), collections.Counter(), collections.Counter()
    original = p.gestes

    def observer(v, e, *a, **k):
        nombres["etats"] += 1
        initial = p.depart(m, v.id, v).portes
        if e.portes - initial:
            nombres["preparatifs"] += 1
        comptes.update(set(c for o in e.portes for c in categories(m.objets[o])))
        objets.update(e.portes - initial)
        yield from original(v, e, *a, **k)

    with patch.multiple(p.Vue, **anciennes()), patch.object(p, "gestes", observer), p.diagnostics() as recherches:
        pnj.avancer(m, 1, [])
    return {"scenario": scenario, **nombres, "categories": dict(comptes),
            "objets_acquis": dict(objets.most_common()), "recherches": recherches}


if __name__ == "__main__":
    ceder()
    Path("artifacts/capacite-52").mkdir(parents=True, exist_ok=True)
    for scenario in ("mine", "auberge"):
        r = mesurer(scenario)
        Path(f"artifacts/capacite-52/inventaires-{scenario}.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in r.items() if k != "recherches"}, ensure_ascii=False), flush=True)
