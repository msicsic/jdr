"""Résume les changements entre recherches et les différences des nuits du lot 87."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def diagnostic(fichier):
    d = json.loads(fichier.read_text(encoding="utf-8"))
    precedents, bornes, plans = {}, Counter(), []
    paires = memes = prix_seuls = 0
    changements = Counter()
    for r in d["recherches"]:
        cle = (r["pnj"], r["but"])
        ancien = precedents.get(cle)
        if r["issue"] == "borne":
            bornes[cle] += 1
            if ancien and ancien["issue"] == "borne":
                paires += 1
                memes += not r.get("changements")
                prix_seuls += not r.get("changements") and bool(r.get("prix_change"))
                changements.update(r.get("changements", []))
        if r.get("apres_bornees"):
            plans.append({k: v for k, v in r.items() if k not in ("entrees", "prix", "besoin")})
        precedents[cle] = r
    return {"bornees_logiques": [[*k, n] for k, n in bornes.items()], "paires": paires,
            "memes_entrees_communes": memes, "prix_seuls": prix_seuls,
            "changements_composantes": dict(changements), "issues_apres_bornees": plans,
            "series_finales": d["series_finales"]}


def bilan(root):
    from donjon import banc_pnj
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    banc_pnj.ceder()
    resultat = {"diagnostic": {}, "cout": {}, "decisions": {}}
    for fichier in root.glob("diagnostic-*.json"):
        resultat["diagnostic"][fichier.stem] = diagnostic(fichier)
    nuits = defaultdict(dict)
    for fichier in root.glob("cout-*.json"):
        if fichier.stem.endswith(".monde") or "-plan-" in fichier.stem or "-borne-" in fichier.stem:
            continue
        d = json.loads(fichier.read_text(encoding="utf-8"))
        version = fichier.stem.split("-")[1]
        r = d["resume"]
        cle = f'{r["scenario"]}-{r["depart"]}'
        resultat["cout"].setdefault(cle, {})[version] = {k: r[k] for k in (
            "secondes", "bornees", "noeuds", "cpu_cumule_4h", "mesures")}
        resultat["cout"][cle][version]["attentes"] = sum(x["issue"] == "attente" for x in d["recherches"])
        nuits[cle][version] = d
    for cle, variantes in nuits.items():
        if not {"base", "branche"} <= variantes.keys():
            continue
        a, b = (variantes[n]["resume"]["mesures"] for n in ("base", "branche"))
        resultat["decisions"][cle] = {
            "mesures_changees": {k: [v, b.get(k)] for k, v in a.items() if b.get(k) != v},
            "plans_base": variantes["base"].get("plans_apres_bornees", []),
            "plans_branche": variantes["branche"].get("plans_apres_bornees", [])}
        mondes = []
        for version in ("base", "branche"):
            m = json.loads((root / f"cout-{version}-{cle}.monde.json").read_text(encoding="utf-8"))
            for e in m["esprits"].values():
                e.pop("attentes_bornees", None)
            mondes.append(m)
        resultat["decisions"][cle]["monde_hors_attentes_identique"] = mondes[0] == mondes[1]
        a, b = [Monde.charger(root / f"cout-{version}-{cle}.monde.json") for version in ("base", "branche")]
        resultat["decisions"][cle]["regarder_identique"] = regarder(a) == regarder(b)
        resultat["decisions"][cle]["scene_identique"] = scene_percue(a) == scene_percue(b)
        for champ in ("chronique", "recit"):
            resultat["decisions"][cle][champ + "_identique"] = variantes["base"][champ] == variantes["branche"][champ]
        for champ in ("trace_recherches", "recherches_logiques"):
            resultat["decisions"][cle][champ + "_identique"] = (
                variantes["base"]["resume"][champ] == variantes["branche"]["resume"][champ])
    return resultat


if __name__ == "__main__":
    root = Path("artifacts/attente-bornee")
    (root / "bilan.json").write_text(json.dumps(bilan(root), ensure_ascii=False, indent=2), encoding="utf-8")
