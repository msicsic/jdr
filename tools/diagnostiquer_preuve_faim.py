"""Rejoue des captures de faim pour expliquer les lacunes du certificat d'absence."""
import argparse
import gzip
import inspect
import json
from pathlib import Path
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("captures", nargs="+")
    ap.add_argument("--sortie", required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from donjon import banc_pnj, planification as p
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    banc_pnj.ceder()
    lacunes, resultat, profondeurs = [], {}, {}

    def echec(examines, lue, e, n, noeud):
        cause = "etat_absent" if noeud is None else "successeurs_absents" if noeud[3] is None else "differe_non_developpe"
        lacunes.append({"cause": cause, "profondeur_preuve": n, "examines": examines,
                        "profondeur_recherche": profondeurs.get(e),
                        "salle": e.salle, "portes": sorted(e.portes),
                        "faits": sorted([(list(k), v) for k, v in e.faits.items()], key=repr)})
        return False, examines, "lacune", lue

    source = inspect.getsource(p._parcours)
    ancien = 'return False, examines, "lacune", lue'
    assert source.count(ancien) == 3
    source = source.replace(ancien, 'return _p2_echec_lacune(examines, lue, e, n, noeud)')
    p.__dict__["_p2_echec_lacune"] = echec
    exec(compile(source, "<diagnostic-preuve>", "exec"), p.__dict__)
    source = inspect.getsource(p._explorer_etats)
    point = "        examines += 1\n"
    assert source.count(point) == 1
    source = source.replace(point, point + "        _p2_profondeurs[e] = min(n, _p2_profondeurs.get(e, n))\n")
    p.__dict__["_p2_profondeurs"] = profondeurs
    exec(compile(source, "<diagnostic-profondeur>", "exec"), p.__dict__)
    for chemin in args.captures:
        fichier = Path(chemin)
        monde = Monde(json.loads(gzip.decompress(fichier.read_bytes())))
        qui = "tilo" if "tilo" in fichier.name else "joss"
        avant = json.dumps(monde.data, sort_keys=True, ensure_ascii=False)
        vues = regarder(monde), scene_percue(monde)
        lacunes.clear()
        p._MEMOIRE.clear()
        p._GRAPHES.clear()
        p._IMPOSSIBLES.clear()
        with p.diagnostics() as ds:
            rendus = []
            for _ in range(3):
                # Forcer le calcul en conservant uniquement le graphe de la
                # même photographie ; les prix du monde ne sont pas modifiés.
                p._MEMOIRE.clear()
                profondeurs.clear()
                r = p.chercher(monde, qui, p.a_mange, nom="faim", memo=["besoin", "faim"],
                               emplois=("manger",), motif="faim")
                rendus.append(repr(r))
        assert len(set(rendus)) == 1
        assert avant == json.dumps(monde.data, sort_keys=True, ensure_ascii=False)
        recharge = Monde(json.loads(json.dumps(monde.data)))
        assert vues == (regarder(recharge), scene_percue(recharge))
        resultat[fichier.name] = {"diagnostics": ds, "lacunes": list(lacunes),
                                 "resultat": rendus[0], "monde_et_vues_conserves": True}
    Path(args.sortie).write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
