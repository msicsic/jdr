"""Contrats de plans et de rendu, avant/après, sur captures réelles rechargées."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--depot", required=True)
    a.add_argument("--sortie", required=True)
    a.add_argument("--oracle-etapes", action="store_true", help="actualiser seulement les empreintes de calcul après contrôle du jeu")
    args = a.parse_args()
    outils = Path(__file__).resolve().parent
    sys.path[:] = [x for x in sys.path if Path(x or ".").resolve() != outils]
    sys.path.insert(0, str(Path(args.depot).resolve()))
    from donjon import banc_pnj, planification as p
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    banc_pnj.ceder()
    racine = Path(__file__).resolve().parents[1]
    if args.oracle_etapes:
        from tests.test_etapes_chainees import observer_capture
        historique = json.loads((racine / "tests/data/cout-12h/etapes-attendues.json").read_text(encoding="utf8"))
        calcul = {"visites", "n_visites", "diagnostics"}
        nouveau = {"reference_historique": historique["reference"], "changement": "complétion des certificats, lot 92 c"}
        for scenario in ("mine", "auberge"):
            observe = observer_capture(scenario)
            assert {k: v for k, v in observe.items() if k not in calcul} == {
                k: v for k, v in historique[scenario].items() if k not in calcul}, scenario
            nouveau[scenario] = {k: observe[k] for k in sorted(calcul) if observe[k] != historique[scenario][k]}
        Path(args.sortie).write_text(json.dumps(nouveau, ensure_ascii=False, indent=2), encoding="utf8")
        print(json.dumps(nouveau, ensure_ascii=False))
        return
    cas = [("joss-622-epuise", "joss", "profondeurs-preuve/joss-622-epuise.json.gz"),
           ("tilo-566-epuise", "tilo", "profondeurs-preuve/tilo-566-epuise.json.gz"),
           ("joss-622-plan", "joss", "profondeurs-preuve/joss-622-plan.json.gz"),
           ("mine-480", "remy", "cout-12h/mine-1985-480.json.gz")]
    def h(x):
        return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, default=repr).encode()).hexdigest()
    def encoder(r):
        if r is None:
            return None
        return json.loads(json.dumps({"cout_hex": r[0].hex(), "etapes": r[1], "salle": r[2].salle,
                                      "portes": sorted(r[2].portes), "allure": r[2].allure,
                                      "faits": sorted([(list(k), v) for k, v in r[2].faits.items()], key=repr)}))
    resultats = {}
    for nom, qui, chemin in cas:
        m = Monde(json.loads(gzip.decompress((racine / "tests/data" / chemin).read_bytes())))
        p._MEMOIRE.clear()
        p._GRAPHES.clear()
        p._IMPOSSIBLES.clear()
        avant, vues = h(m.data), (regarder(m), scene_percue(m))
        rendus = []
        with p.diagnostics() as ds:
            for _ in range(3):
                p._MEMOIRE.clear()
                r = p.chercher(m, qui, p.a_mange, nom="faim", memo=["besoin", "faim"],
                               emplois=("manger",), motif="faim")
                rendus.append(encoder(r))
        recharge = Monde(json.loads(json.dumps(m.data)))
        assert h(m.data) == avant == h(recharge.data)
        assert vues == (regarder(recharge), scene_percue(recharge))
        assert all(x == rendus[0] for x in rendus)
        resultats[nom] = {"resultat": rendus[0], "monde": avant, "rendu": h(vues),
                          "diagnostics": ds, "recharge": True}
    Path(args.sortie).write_text(json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf8")
    print({k: {"resultat": repr(v["resultat"])[:180], "noeuds": [d["noeuds"] for d in v["diagnostics"]]} for k,v in resultats.items()})


if __name__ == "__main__":
    main()
