"""Mesure 92 c sans appliquer de certificat au moteur ni modifier ses graphes."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import empreintes_nuits as empreintes
from completion_preuves import prouver


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--depot", default="artifacts/versions92c/base", help="moteur de base 9810f4a")
    args = ap.parse_args()
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    empreintes._preparer(args.depot, False, 0)
    from donjon import banc_pnj, planification as p
    banc_pnj.ceder()
    chercher, sans_plan, explorer = p.chercher, p._sans_plan, p._explorer
    pile, lignes, essais, certifies, tous_essais = [], [], {}, {}, []
    numero = [0]
    heure = [0]

    def cle(base):
        return hashlib.sha256(repr(base).encode()).hexdigest()

    def explorer_observe(*a, **k):
        r = explorer(*a, **k)
        if pile:
            pile[-1]["borne"] = r[1] >= a[5]
        return r

    def sans_plan_observe(v, depart, but, profondeur, faute, tenir, graphe, voir):
        r = sans_plan(v, depart, but, profondeur, faute, tenir, graphe, voir)
        courant = pile[-1]
        if r[2] != "lacune" or courant.get("borne"):
            return r
        place = (v.id, json.dumps(courant["memo"], ensure_ascii=False))
        base = p._GRAPHES[place][0]
        identifiant = cle((place, base, faute is None))
        if identifiant in essais:
            return r
        debut = time.process_time()
        trouve, issue, stats, _ = prouver(p, v, depart, but, courant["vises"], profondeur,
                                         faute, tenir, graphe, voir)
        mesure = {"index": courant["index"], "minute": courant["minute"], "pnj": v.id,
                  "but": courant["but"], "memo": courant["memo"], "signature": cle(base),
                  "sans_faute": faute is None, "prouve": trouve,
                  "issue": issue, "stats": stats, "ancien_parcours": r[1],
                  "cpu": time.process_time() - debut}
        essais[identifiant] = mesure
        tous_essais.append(mesure)
        with sortie.with_suffix(".essais.jsonl").open("a", encoding="utf8") as flux:
            flux.write(json.dumps(mesure, ensure_ascii=False) + "\n")
        if trouve:
            certifies[(place, cle(base), faute is None)] = courant["index"]
        return r

    def observer(monde, qui, *a, **k):
        courant = {"index": numero[0], "minute": monde.data["minutes"], "pnj": qui,
                   "but": k.get("nom", ""), "memo": k.get("memo"),
                   "vises": k.get("vises", a[1] if len(a) > 1 else None)}
        numero[0] += 1
        pile.append(courant)
        avant = len(p.DIAGNOSTIC or [])
        try:
            r = chercher(monde, qui, *a, **k)
        finally:
            pile.pop()
        if not pile and 480 <= courant["minute"] < 720:
            if p.DIAGNOSTIC is not None and len(p.DIAGNOSTIC) > avant:
                courant["diagnostic"] = p.DIAGNOSTIC[-1]
            lignes.append(courant)
        if int(monde.data["minutes"] // 60) > heure[0]:
            heure[0] = int(monde.data["minutes"] // 60)
            print(f"auberge {heure[0]} h", flush=True)
        return r

    p.chercher, p._sans_plan, p._explorer = observer, sans_plan_observe, explorer_observe
    resume = empreintes.nuit(args.depot, "auberge", 1985, 12, "tire")
    reference = Path("artifacts/aller-utile-92b")
    causes = json.loads((reference / "causes.json").read_text(encoding="utf8"))
    faits = json.loads((reference / "auberge-faits.json").read_text(encoding="utf8"))
    for nom in ("empreintes", "trace_recherches", "recherches_logiques", "noeuds"):
        assert resume[nom] == causes["resume"][nom], nom
    assert len(lignes) == len(causes["recherches"]) == len(faits["recherches"])
    precedents, sauves = {}, []
    for r, c, f in zip(lignes, causes["recherches"], faits["recherches"]):
        assert all(r[k] == c[k] == f[k] for k in ("pnj", "but", "minute"))
        place = r["pnj"], r["but"]
        ancien = precedents.get(place)
        signature = c.get("signature_complete")
        prix_seuls = ancien is not None and signature == ancien.get("signature_complete") and c["prix"] != ancien["prix"]
        memo = (r["pnj"], json.dumps(r["memo"], ensure_ascii=False))
        certificat = certifies.get((memo, signature, c["prix"][0] is None))
        if prix_seuls and f["expansions"] and certificat is not None and certificat < r["index"]:
            assert c["diagnostic"]["issue"] != "plan"
            sauves.append({"pnj": r["pnj"], "but": r["but"], "minute": r["minute"], "expansions": f["expansions"]})
        precedents[place] = c
    cout = sum(x["stats"]["enrichis"] for x in tous_essais)
    economie = sum(x["expansions"] for x in sauves)
    bilan = {"expansions_reference": sum(x["expansions"] for x in faits["recherches"]),
             "expansions_evitables_prix_seuls": economie, "cout_etats_enrichis_toute_nuit": cout,
             "gain_net": economie - cout, "relances_evitables": len(sauves),
             "essais": tous_essais, "relances": sauves, "recherches": lignes, "resume": resume}
    bilan["gain_net_part"] = bilan["gain_net"] / bilan["expansions_reference"]
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(bilan, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({k: v for k, v in bilan.items() if k not in ("essais", "relances", "resume")}), flush=True)


if __name__ == "__main__":
    main()
