"""Borne prudente des relances certifiables : même but et minute ultérieure."""
from collections import Counter
import json
from pathlib import Path


def main():
    racine = Path(__file__).resolve().parents[1]
    dossier = racine / "artifacts/preuves-92c"
    mesure = json.loads((dossier / "mesure.json").read_text(encoding="utf8"))
    causes = json.loads((racine / "artifacts/aller-utile-92b/causes.json").read_text(encoding="utf8"))["recherches"]
    faits = json.loads((racine / "artifacts/aller-utile-92b/auberge-faits.json").read_text(encoding="utf8"))["recherches"]
    certificats = {}
    for essai in mesure["essais"]:
        if not essai["prouve"]:
            continue
        cle = essai["pnj"], essai["but"], essai["signature"]
        permissions = {r["prix"][0] is None for r in causes if
                       (r["pnj"], r["but"], r.get("signature_complete")) == cle and r["minute"] == essai["minute"]}
        if len(permissions) != 1:
            continue
        cle = (*cle, permissions.pop())
        certificats[cle] = min(essai["minute"], certificats.get(cle, float("inf")))
    anciens, relances = {}, []
    for c, f in zip(causes, faits):
        place = c["pnj"], c["but"]
        ancien = anciens.get(place)
        cle = (*place, c.get("signature_complete"), c["prix"][0] is None)
        if (ancien and c.get("signature_complete") == ancien.get("signature_complete")
                and c["prix"] != ancien["prix"] and (c["prix"][0] is None) == (ancien["prix"][0] is None)
                and f["expansions"] and c["minute"] > certificats.get(cle, float("inf"))):
            relances.append({"pnj": c["pnj"], "but": c["but"], "expansions": f["expansions"]})
        anciens[place] = c
    couts = {k: sum(x["stats"][k] for x in mesure["essais"]) for k in ("ajoutes", "completes", "enrichis", "visites")}
    primaire = [r for r in relances if r["but"] == "faim" and r["pnj"] in ("tilo", "joss")]
    net = sum(r["expansions"] for r in primaire) - couts["enrichis"]
    r = {"couts_toute_nuit": couts, "relances_prudentes": len(relances),
         "expansions_prudentes": sum(r["expansions"] for r in relances),
         "faim_tilo_joss": {"relances": len(primaire), "expansions": sum(r["expansions"] for r in primaire),
                            "net": net, "part_nette": net / mesure["expansions_reference"]},
         "certificats_faim": dict(Counter(x["pnj"] for x in mesure["essais"] if x["prouve"] and x["but"] == "faim")),
         "cpu_completion": sum(x["cpu"] for x in mesure["essais"])}
    (dossier / "bilan-mesure.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
