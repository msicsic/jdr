"""Lot 337 : tests ciblés puis vingt nuits 4 h, deux travailleurs réduits.

Ni Luna ni suite complète. Les nuits de référence présentes sont relues du
cache commun ; seules les absentes sont jouées et rangées. fin.json est la
dernière écriture, même sur exception ou échec des tests.
"""
from contextlib import ExitStack
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
import comparer_bancs as banc
from priorite import ceder

TESTS = ("garde_ouidire", "agendas_fins", "agendas_transferts", "agendas_garder",
         "agendas_evenement", "agendas_naissance", "esprits", "social",
         "constats_partages", "deja_dit", "parole_commune", "constater_rumeurs", "planification",
         "echanges_argent", "echanges_suite")


def ecrire(chemin, valeur):
    chemin.write_text(json.dumps(valeur, ensure_ascii=False, indent=2), encoding="utf-8")


def comparer(sortie, revision):
    config = dict(scenarios=["relais", "mine", "auberge", "crue", "crue_hameau"],
                  graines=[1985, 7, 42, 2024], heures=4., depart="tire", processus=2,
                  verifier=False, empreintes=False, joueurs=dict(banc.JOUEURS))
    cache = banc.references.dossier(RACINE)
    with ExitStack() as pile:
        arbre_ref = None
        def arbre():
            nonlocal arbre_ref
            if arbre_ref is None:
                arbre_ref = pile.enter_context(banc.worktree_temporaire(RACINE, revision))
            return arbre_ref
        avant = banc.nuits_du_cote(arbre, revision, config, sortie, "reference", cache)
        ecrire(sortie / "reference.json", avant)
    apres = banc.nuits_du_cote(lambda: RACINE, None, config, sortie, "branche", None)
    ecrire(sortie / "banc.json", dict(config=config, reference=revision,
                                    nuits_reference=avant, nuits_branche=apres))
    lignes = []
    for a, b in zip(avant, apres):
        sa, sb = [n.get("avis", {}).get("total_non_justifies") for n in (a, b)]
        mesures = (b.get("donnees") or {}).get("mesures", {})
        lignes.append(dict(scenario=b["scenario"], graine=b["graine"],
            suspects_reference=sa, suspects_branche=sb,
            plantage_reference=a["plantage"], plantage_branche=b["plantage"],
            usurpations=mesures.get("usurpations"),
            constats_reference=(a.get("donnees") or {}).get("mesures", {}).get("constats_confies"),
            constats_branche=mesures.get("constats_confies"),
            ok=sa is not None and sb is not None and sb <= sa and not a["plantage"]
               and not b["plantage"] and mesures.get("usurpations") == 0))
    ok = all(l["ok"] for l in lignes)
    ecrire(sortie / "bilan.json", dict(ok=ok, nuits=lignes,
        references_cache=sum("cache" in n for n in avant),
        mesures=banc.resumer(avant, apres),
        limite="Banc passif borné : aucune garantie universelle contre les boucles. Temps du cache non comparables."))
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, required=True)
    parser.add_argument("--reference", default="9bef3f6")
    parser.add_argument("--tests", nargs="+", choices=TESTS, default=TESTS)
    parser.add_argument("--sans-banc", action="store_true")
    parser.add_argument("--tests-valides", type=Path,
                        help="réutiliser les tests verts de ce dossier, après contrôle des empreintes")
    args = parser.parse_args()
    ceder()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    debut = time.monotonic()
    fin = dict(ok=False, pid=os.getpid())
    try:
        revision = banc.git(RACINE, "rev-parse", args.reference)
        fin["reference"] = revision
        fichiers = [*sorted((RACINE / "donjon").glob("*.py")),
                    RACINE / "tests/support.py", Path(__file__).resolve(),
                    *[RACINE / f"tests/test_{nom}.py" for nom in args.tests]]
        empreintes = {str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in fichiers}
        ecrire(sortie / "debut.json", dict(pid=os.getpid(), cwd=str(RACINE), reference=revision,
            commit=banc.git(RACINE, "rev-parse", "HEAD"),
            empreintes=empreintes))
        if args.tests_valides:
            precedent = args.tests_valides.resolve()
            acquises = json.loads((precedent / "debut.json").read_text(encoding="utf-8"))["empreintes"]
            tests = json.loads((precedent / "tests.json").read_text(encoding="utf-8"))
            if not tests["succes"] or any(acquises.get(k) != v for k, v in empreintes.items()):
                raise ValueError("Tests non verts ou code/tests différents de ceux qui ont été vérifiés")
            ecrire(sortie / "tests.json", tests)
            fin.update(tests_code=0, tests_repris=str(precedent))
        else:
            commande = [sys.executable, "tools/tests.py", "--processus", "2", "--sortie",
                        str(sortie / "tests.json"), *[f"tests/test_{n}.py" for n in args.tests]]
            with (sortie / "tests.log").open("w", encoding="utf-8") as flux:
                fin["tests_code"] = subprocess.run(commande, cwd=RACINE, stdout=flux,
                                                   stderr=subprocess.STDOUT, check=False).returncode
        if fin["tests_code"]:
            return 1
        fin["banc_ok"] = None if args.sans_banc else comparer(sortie, revision)
        fin["ok"] = args.sans_banc or fin["banc_ok"]
        return int(not fin["ok"])
    except BaseException:
        fin["erreur"] = traceback.format_exc()
        return 1
    finally:
        fin["secondes"] = time.monotonic() - debut
        ecrire(sortie / "fin.json", fin)


if __name__ == "__main__":
    raise SystemExit(main())
