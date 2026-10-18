"""Banc A/B du jalon E : le moteur seul (D) contre le moteur conseillé par Luna (E).

    python tools/banc_stratege.py --graines 1985 7 42 2024 --heures 8

Chaque graine est jouée sans joueur actif, sans puis avec le stratège. Chroniques et
mesures sont écrites dans artifacts/bancs_pnj/. Le critère de décision a été fixé avant
toute mesure : aucune violation d'état, au moins +50 % d'événements distincts hors routine,
au moins -30 % de minutes de besoin urgent sans intention, au plus 2 appels par heure de jeu.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from donjon import stratege  # noqa: E402
from donjon.banc_pnj import appelant, creer, executer  # noqa: E402
from donjon.esprits import lire, pnjs  # noqa: E402
from donjon.geometrie import position_entree  # noqa: E402

SEUILS = {"evenements_distincts": 0.5, "minutes_urgentes_oisives": -0.3}
APPELS_PAR_HEURE = 2


def partie(graine, heures, avec_stratege, connexion):
    stratege.activer(appelant(connexion) if avec_stratege else None)
    debut = time.monotonic()
    try:
        monde = creer("relais", graine)
        monde.joueur.update(salle="chambre_cloche", position=list(position_entree(monde, "chambre_cloche")))
        chronique, mesures = executer(monde, int(heures * 60))
        violation = None
    except AssertionError as exc:
        chronique, mesures, violation = [], {}, str(exc)
    finally:
        stratege.activer(None)
    return {"graine": graine, "heures": heures, "stratege": avec_stratege, "violation": violation,
            "secondes": round(time.monotonic() - debut, 1), "mesures": mesures, "chronique": chronique,
            "souvenirs": {id: lire(monde, id)["memoire"] for id in pnjs(monde)} if not violation else {}}


def moyenne(parties, cle):
    return sum(p["mesures"].get(cle, 0) for p in parties) / max(1, len(parties))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--graines", type=int, nargs="+", default=[1985, 7, 42, 2024])
    p.add_argument("--heures", type=float, default=8)
    p.add_argument("--connexion", choices=("chatgpt", "api"), default="chatgpt")
    p.add_argument("--etiquette", default="ab")
    args = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    dossier = BASE / "artifacts" / "bancs_pnj"
    dossier.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
    resultats = {"D": [], "E": []}
    for graine in args.graines:
        for nom, actif in (("D", False), ("E", True)):
            r = partie(graine, args.heures, actif, args.connexion)
            resultats[nom].append(r)
            chemin = dossier / f"{horodatage}-{args.etiquette}-{nom}-{graine}.json"
            chemin.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
            m = r["mesures"]
            print(f"{nom} graine {graine} : {r['secondes']} s, violation {r['violation']}, "
                  f"événements {m.get('evenements_distincts')}, oisiveté urgente {m.get('minutes_urgentes_oisives')}, "
                  f"échanges {m.get('echanges')}, appels {m.get('stratege_appels', 0)}", flush=True)
    d, e = resultats["D"], resultats["E"]
    verdict = {"violations": sum(bool(r["violation"]) for r in d + e)}
    for cle, seuil in SEUILS.items():
        a, b = moyenne(d, cle), moyenne(e, cle)
        ecart = (b - a) / a if a else 0.0
        verdict[cle] = {"D": a, "E": b, "ecart": round(ecart, 3),
                        "atteint": ecart >= seuil if seuil > 0 else ecart <= seuil}
    appels = moyenne(e, "stratege_appels") / args.heures
    verdict["appels_par_heure"] = {"E": round(appels, 2), "atteint": appels <= APPELS_PAR_HEURE}
    verdict["garde"] = (verdict["violations"] == 0 and appels <= APPELS_PAR_HEURE
                        and all(verdict[c]["atteint"] for c in SEUILS))
    (dossier / f"{horodatage}-{args.etiquette}-verdict.json").write_text(
        json.dumps(verdict, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(verdict, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
