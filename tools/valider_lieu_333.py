"""Banc borné 333 : référence en cache seulement, un travailleur réduit, fin même en échec."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time
import traceback

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
import comparer_bancs as banc
from priorite import ceder


def ecrire(chemin, contenu):
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2), encoding="utf-8")


def comparer(sortie, reference):
    config = dict(scenarios=["relais", "mine", "auberge", "crue", "crue_hameau"],
                  graines=[1985, 7, 42, 2024], heures=4., depart="tire", processus=1,
                  verifier=False, empreintes=False, joueurs=dict(banc.JOUEURS))
    revision = banc.git(RACINE, "rev-parse", reference)
    # f08ef58 est un ancêtre de la base du lot ; seuls docs/tests ont changé.
    banc.git(RACINE, "diff", "--exit-code", revision, "4a54090", "--", "donjon", "tools")
    def absent():
        raise RuntimeError("Référence absente du cache : aucune nuit de référence relancée.")
    avant = banc.nuits_du_cote(absent, revision, config, sortie, "reference", banc.references.dossier(RACINE))
    ecrire(sortie / "reference.json", avant)
    apres = []
    taches = [(s, g, config) for s, g in banc.taches_du_lot(config)]
    with ProcessPoolExecutor(max_workers=1, max_tasks_per_child=1) as pool:
        for nuit in pool.map(banc.jouer_nuit, taches):
            apres.append(nuit)
            ecrire(sortie / f"branche-{nuit['scenario']}-{nuit['graine']}.json", nuit)
    ecrire(sortie / "banc.json", dict(config=config, reference=revision,
                                     nuits_reference=avant, nuits_branche=apres))
    lignes = []
    for a, b in zip(avant, apres):
        m = (b.get("donnees") or {}).get("mesures", {})
        sa, sb = [n.get("avis", {}).get("total_non_justifies") for n in (a, b)]
        lignes.append(dict(scenario=b["scenario"], graine=b["graine"],
            suspects_reference=sa, suspects_branche=sb,
            plantage_reference=a["plantage"], plantage_branche=b["plantage"],
            usurpations=m.get("usurpations"), coups=m.get("coups_portes", 0),
            poussees=m.get("poussees"), secondes_cpu=b["secondes_cpu"],
            avertissements=sum("s'interpose" in c["texte"] for c in (b.get("donnees") or {}).get("chronique", [])),
            ok=sa is not None and sb is not None and sb <= sa and not a["plantage"]
               and not b["plantage"] and m.get("usurpations") == 0 and m.get("coups_portes", 0) == 0))
    ok = all(l["ok"] for l in lignes)
    ecrire(sortie / "bilan.json", dict(nuits=lignes, ok=ok,
        references_cache=sum("cache" in n for n in avant),
        limite="Scénarios historiques inchangés ; les charges de lieu sont exercées par les tests ciblés."))
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, required=True)
    parser.add_argument("--reference", default="f08ef58")
    args = parser.parse_args()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    debut = time.monotonic()
    fin = dict(ok=False, pid=os.getpid(), reference=args.reference)
    try:
        ceder()
        fichiers = [*sorted((RACINE / "donjon").glob("*.py")),
                    RACINE / "tests/test_interposition_lieu.py", Path(__file__).resolve()]
        ecrire(sortie / "debut.json", dict(pid=os.getpid(), cwd=str(RACINE),
            commit=banc.git(RACINE, "rev-parse", "HEAD"),
            empreintes={str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers}))
        fin["ok"] = comparer(sortie, args.reference)
        return int(not fin["ok"])
    except BaseException:
        fin["erreur"] = traceback.format_exc()
        return 1
    finally:
        fin["secondes"] = time.monotonic() - debut
        ecrire(sortie / "fin.json", fin)  # Dernière écriture, succès comme échec.


if __name__ == "__main__":
    raise SystemExit(main())
