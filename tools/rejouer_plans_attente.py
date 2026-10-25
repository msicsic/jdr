"""Chaque plan de référence après une borne reste trouvable avec l'attente retenue."""
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj, planification as p
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue


def chercher(monde, id, nom):
    with p.vues_du_choix(monde, id):
        return _chercher(monde, id, nom)


def _chercher(monde, id, nom):
    if nom in ("faim", "chaleur"):
        return p.planifier(monde, id, nom)
    if nom.startswith("garder:"):
        return p.garder(monde, id, nom.split(":", 1)[1])
    raise ValueError(f"But non couvert par le rejeu : {nom}")


def recharger(monde, fichier):
    monde.sauver(fichier)
    r = Monde.charger(fichier)
    assert monde.data == r.data
    assert regarder(monde) == regarder(r)
    assert scene_percue(monde) == scene_percue(r)
    return r


if __name__ == "__main__":
    banc_pnj.ceder()
    root = Path("artifacts/attente-bornee")
    resultats = []
    for fichier in root.glob("cout-base-*.json"):
        if ".monde" in fichier.stem or "-plan-" in fichier.stem or "-borne-" in fichier.stem:
            continue
        d = json.loads(fichier.read_text(encoding="utf-8"))
        for plan in d.get("plans_apres_bornees", []):
            initial = plan["premiere_borne"]
            if not isinstance(initial, dict):
                diagnostic = json.loads((root / f'diagnostic-{d["resume"]["depart"]}.json').read_text(encoding="utf-8"))
                temoins = [r for r in diagnostic["recherches"] if r["pnj"] == plan["pnj"]
                           and r["but"] == plan["but"] and r["minute"] == initial and "capture" in r]
                if len(temoins) != 1:
                    raise ValueError(f"Capture de borne absente : {plan}")
                initial = {"capture": temoins[0]["capture"], "minute": initial}
            a = Monde(json.loads(Path(initial["capture"]).read_text(encoding="utf-8")))
            b = Monde(json.loads(Path(plan["capture"]).read_text(encoding="utf-8")))
            id, nom = plan["pnj"], plan["but"]
            p._MEMOIRE.clear()
            p._GRAPHES.clear()
            p._IMPOSSIBLES.clear()
            with p.diagnostics() as recherches:
                chercher(a, id, nom)
                assert recherches[-1]["issue"] == "borne", recherches[-1]
                b.data["esprits"][id]["attentes_bornees"] = copy.deepcopy(a.data["esprits"][id]["attentes_bornees"])
                b = recharger(b, root / "rejeu-avant.json")
                r = chercher(b, id, nom)
                assert r is not None, (plan, recherches[-1])
                assert recherches[-1]["issue"] != "attente"
                recharger(b, root / "rejeu-apres.json")
                resultats.append({**plan, "issue": recherches[-1]["issue"], "recharge": True})
    (root / "rejeux-plans.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(resultats)} plans conservés après recharge")
