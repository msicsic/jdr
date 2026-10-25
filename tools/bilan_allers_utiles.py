"""Compare le témoin et le comptage P3 ; CPU du témoin uniquement."""
from collections import Counter, defaultdict
import json
from pathlib import Path


def bilan(racine):
    temoin, compte = [json.loads((racine / f"{nom}.json").read_text(encoding="utf8"))
                      for nom in ("temoin", "comptage-structure")]
    a, b = temoin["resume"], compte["resume"]
    for nom, resume in (("temoin", a), ("comptage-structure", b)):
        (racine / f"{nom}-comparer.json").write_text(
            json.dumps([resume], ensure_ascii=False), encoding="utf8")
    champs = ("empreintes", "trace_recherches", "recherches_logiques", "noeuds", "neuves")
    identite = {k: a[k] == b[k] for k in champs}
    assert all(identite.values()), identite
    assert len(temoin["recherches"]) == len(compte["recherches"])
    groupes = defaultdict(lambda: {"cpu": 0, "appels": 0, "noeuds_diagnostic": 0,
                                   "etats": 0, "classes": 0, "sans_geste_ni_but": 0,
                                   "suites": Counter(), "gestes": Counter(), "issues": Counter(),
                                   "vides_apres_aller": 0, "vides_structurels": 0,
                                   "vides_structurels_apres_aller": 0,
                                   "candidats_sans_obstacle_preuve": 0,
                                   "structure_tous_etats": 0, "candidats_majorants_tous_etats": 0,
                                   "retenus_preuve": Counter(), "retenus_tous_etats": Counter()})
    comptes = ("etats", "classes", "sans_geste_ni_but", "vides_apres_aller", "vides_structurels",
               "vides_structurels_apres_aller", "candidats_sans_obstacle_preuve",
               "structure_tous_etats", "candidats_majorants_tous_etats")
    tables = ("suites", "gestes", "retenus_preuve", "retenus_tous_etats")
    for x, y in zip(temoin["recherches"], compte["recherches"]):
        assert all(x[k] == y[k] for k in ("minute", "pnj", "but"))
        dx, dy = x.get("diagnostic", {}), y.get("diagnostic", {})
        assert {k: v for k, v in dx.items() if k != "duree"} == {
            k: v for k, v in dy.items() if k != "duree"}
        g = groupes[x["pnj"] + "/" + x["but"]]
        g["appels"] += 1
        g["cpu"] += x["cpu"]
        g["noeuds_diagnostic"] += dx.get("noeuds", 0)
        g["issues"][dx.get("issue", "inconnue")] += 1
        for k in comptes:
            g[k] += y[k]
        for k in tables:
            g[k].update(y[k])
    total = {k: sum(g[k] for g in groupes.values()) for k in
             ("cpu", "appels", "noeuds_diagnostic", *comptes)}
    for k in tables:
        total[k] = dict(sum((g[k] for g in groupes.values()), Counter()))
    total["non_classes"] = total["etats"] - total["classes"]
    total["part_sans_geste"] = total["sans_geste_ni_but"] / total["etats"]
    total["part_majorante_avec_non_classes"] = (
        total["sans_geste_ni_but"] + total["non_classes"]) / total["etats"]
    total["microsecondes_par_etat"] = total["cpu"] * 1e6 / total["etats"]
    total["part_aller_successeurs"] = total["suites"].get("aller", 0) / sum(total["suites"].values())
    total["part_candidats_majorants"] = total["candidats_majorants_tous_etats"] / total["etats"]
    resultat = {"identite": identite, "total": total,
                "par_but": dict(sorted(groupes.items(), key=lambda x: -x[1]["cpu"]))}
    (racine / "bilan.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({"identite": identite, "total": total,
                      "buts_cpu": {k: {n: v[n] for n in ("cpu", "etats", "sans_geste_ni_but",
                                   "structure_tous_etats", "candidats_majorants_tous_etats")}
                                   for k, v in list(resultat["par_but"].items())[:12]}},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import sys
    bilan(Path(sys.argv[1]))
