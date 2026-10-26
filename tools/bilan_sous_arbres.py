"""Synthèse des sous-arbres P2 et des réveils, avec conservation contre le lot 92."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics
import sys


def main(racine, temoin):
    d = json.loads((racine / "auberge-faits.json").read_text(encoding="utf8"))
    t = json.loads(temoin.read_text(encoding="utf8"))
    causes = json.loads((racine / "causes.json").read_text(encoding="utf8"))
    champs = ("empreintes", "trace_recherches", "recherches_logiques", "noeuds", "neuves")
    conservation = {k: d["resume"][k] == t["resume"][k] for k in champs}
    assert all(conservation.values()), conservation
    assert all(causes["resume"][k] == t["resume"][k] for k in champs)
    temoins = [r for r in t["recherches"] if 480 <= r["minute"] < 720]
    assert len(d["recherches"]) == len(temoins)
    assert len(d["recherches"]) == len(causes["recherches"])
    groupes = defaultdict(list)
    for r, ref, cause in zip(d["recherches"], temoins, causes["recherches"]):
        assert all(r[k] == ref[k] for k in ("pnj", "but", "minute"))
        assert {k: v for k, v in r.get("diagnostic", {}).items() if k != "duree"} == {
            k: v for k, v in ref.get("diagnostic", {}).items() if k != "duree"}
        assert all(r[k] == cause[k] for k in ("pnj", "but", "minute", "prix"))
        assert {k: v for k, v in r.get("diagnostic", {}).items() if k != "duree"} == {
            k: v for k, v in cause.get("diagnostic", {}).items() if k != "duree"}
        r["signature_complete"] = cause.get("signature_complete")
        groupes[r["pnj"] + "/" + r["but"]].append(r)
    total = {k: sum(r[k] for r in d["recherches"]) for k in
             ("expansions", "union_preparatifs", "union_sans_rapport")}
    for k in ("descendants", "descendants_sans_rapport", "profondeurs"):
        total[k] = dict(sum((Counter(r[k]) for r in d["recherches"]), Counter()).most_common())
    total["part_sans_rapport"] = total["union_sans_rapport"] / total["expansions"]
    total["part_preparatifs"] = total["union_preparatifs"] / total["expansions"]
    details = {}
    for cle, lignes in groupes.items():
        neuves = [r for r in lignes if r["expansions"]]
        precedents, causes_reprises, expansions_causes, champs_changes, croyances = None, Counter(), Counter(), Counter(), Counter()
        for r in lignes:
            if r["expansions"]:
                if precedents is None:
                    cause = "premier_appel_observe"
                elif r.get("entrees") != precedents.get("entrees"):
                    cause = "entrees_changees"
                elif precedents.get("diagnostic", {}).get("issue") == "impossible":
                    # Le chemin certificat peut laisser l'ancienne case mémoire
                    # en place : ne pas lui attribuer une signature actuelle.
                    cause = "reprise_apres_impossibilite_a_attribuer"
                elif r.get("signature_complete") is None or precedents.get("signature_complete") is None:
                    cause = "signature_non_disponible"
                elif r["signature_complete"] != precedents["signature_complete"]:
                    cause = "parametres_complementaires"
                elif r["prix"] != precedents["prix"]:
                    cause = "prix_seuls"
                else:
                    cause = "memes_entrees_et_prix"
                causes_reprises[cause] += 1
                expansions_causes[cause] += r["expansions"]
                if cause != "premier_appel_observe":
                    champs_changes.update(str(x) for x in r.get("changements", ()))
                    croyances.update("/".join(x) for x in r.get("croyances_changees", ()))
            precedents = r
        def distribution(valeurs):
            return {"min": min(valeurs, default=0), "mediane": statistics.median(valeurs) if valeurs else 0,
                    "max": max(valeurs, default=0), "somme": sum(valeurs)}
        details[cle] = {
            "appels": len(lignes), "recherches_avec_expansion": len(neuves),
            "issues_appels": dict(Counter(r.get("diagnostic", {}).get("issue") for r in lignes)),
            "issues_expansions": dict(Counter(r.get("diagnostic", {}).get("issue") for r in neuves)),
            "memoire": sum(bool(r.get("diagnostic", {}).get("memoire")) for r in lignes),
            "graphes_repris": sum(bool(r.get("diagnostic", {}).get("graphe")) for r in neuves),
            "preuves": dict(Counter(str(r["diagnostic"].get("preuve_issue")) for r in neuves)),
            "noeuds_preuves": sum(r["diagnostic"].get("preuve_noeuds", 0) for r in neuves),
            "clotures": dict(Counter("opaque_ou_metrique" if "but_opaque_ou_passage" in r.get("dependances", {}).values()
                                     else "lumiere" if "lumiere_flamme_pression" in r.get("dependances", {}).values()
                                     else "sans_lumiere" for r in neuves)),
            "expansions": distribution([r["expansions"] for r in neuves]),
            "etats_distincts_developpes": distribution([r["distincts"] for r in neuves]),
            "etats_distincts_decouverts": distribution([r["diagnostic"]["etats"] for r in neuves]),
            "union_preparatifs": sum(r["union_preparatifs"] for r in lignes),
            "union_sans_rapport": sum(r["union_sans_rapport"] for r in lignes),
            "descendants": dict(sum((Counter(r["descendants"]) for r in lignes), Counter()).most_common()),
            "descendants_sans_rapport": dict(sum((Counter(r["descendants_sans_rapport"]) for r in lignes), Counter()).most_common()),
            "causes_recherches": dict(causes_reprises), "expansions_par_cause": dict(expansions_causes),
            "champs_changes": dict(champs_changes.most_common()),
            "croyances_changees": dict(croyances.most_common()),
            "par_recherche": [{k: r[k] for k in ("minute", "expansions", "distincts", "union_preparatifs",
                                               "union_sans_rapport", "diagnostic")} for r in neuves]}
    resultat = {"conservation": conservation, "recharge": d["recharge"], "total": total, "par_but": details}
    (racine / "bilan.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf8")
    for nom, nuit in (("auberge", d), ("temoin", t)):
        (racine / f"{nom}-comparer.json").write_text(json.dumps([nuit["resume"]], ensure_ascii=False), encoding="utf8")
    print(json.dumps({"conservation": conservation, "total": total,
                     "faim": {k: {n: v for n, v in details[k].items() if n not in ("par_recherche",)}
                              for k in ("tilo/faim", "joss/faim")}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
