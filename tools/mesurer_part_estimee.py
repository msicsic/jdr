"""Campagnes moteur et contre-épreuve de la part estimée, hors du jeu.

Deux variantes partagent au plus --processus calculs, lancés ensemble. --justesse
rejoue chaque recherche qui envisage une estimation avec l'ancienne chaîne,
avec sa mémoire séparée et sans changer le monde. Ces temps instrumentés ne mesurent pas
la vitesse du moteur. La référence est un worktree explicite, jamais une sauvegarde.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

RACINE = Path(__file__).resolve().parents[1]


def worker(args):
    sys.path.insert(0, str(Path(args.depot).resolve()))
    sys.path.insert(1, str(RACINE / "tools"))
    import comparer_bancs as c
    from donjon import banc_pnj as b, echanges as ex, planification as p, pnj, spatial
    # comparer_bancs privilégie le cwd : les sous-processus y sont lancés.
    spatial.VERIFICATION = args.verification
    ressources = dict(demandes_combustible=0, achats_combustible=0, parts_livrees=0,
                      recharges_lampes=0, recharges_foyers=0, foyers_allumes=0)
    demander, remettre, agir, nuit = ex.demander, ex.remettre, pnj._executer, b.nuit
    relever = c.audit._releve

    def releve(m):
        from donjon.deliberation import _delegue, attentes, satisfaite
        from donjon.esprits import lire
        r = relever(m)
        for qui, d in r["pnj"].items():
            d["sans_recours"] = []
            if d["u"] and lire(m, qui)["intention"] is None:
                pulsions = m.objets[qui]["profil"]["pulsions"]
                a_faire = [besoin for besoin in d["u"] if
                    not any(x["besoin"] == besoin for x in pulsions) or any(
                        x["besoin"] == besoin and not satisfaite(m, qui, x["condition"])
                        and not _delegue(m, qui, x) for x in pulsions)]
                d["sans_recours"] = [b for b in a_faire if b not in attentes(m, qui)]
        return r

    def demande(m, demandeur, donneur, objet, *a, **k):
        combustible = "combustible" in m.objets.get(objet, {}).get("usages", ())
        issue = demander(m, demandeur, donneur, objet, *a, **k)
        if combustible:
            ressources["demandes_combustible"] += 1
            ressources["achats_combustible"] += issue == "vendu"
        return issue

    def remise(m, donneur, receveur, objet, *a, **k):
        avant = m.objets[objet].get("lieu")
        r = remettre(m, donneur, receveur, objet, *a, **k)
        if (avant != receveur and m.objets[objet].get("lieu") == receveur
                and "combustible" in m.objets[objet].get("usages", ())):
            ressources["parts_livrees"] += 1
        return r

    def action(m, qui, etape, *a, **k):
        r = agir(m, qui, etape, *a, **k)
        source = m.objets.get(etape.get("cible"), {})
        if r and etape["operation"] == "alimenter":
            ressources["recharges_foyers" if source.get("foyer") else "recharges_lampes"] += 1
        if r and etape["operation"] == "allumer" and source.get("foyer"):
            ressources["foyers_allumes"] += 1
        return r

    def avec_diagnostic(*a, **k):
        k["diagnostic"] = True
        return nuit(*a, **k)

    comparaisons, pile_recherches = [], []
    chercher = p.chercher
    if args.justesse:
        memoire_detail, graphes_detail, impossibles_detail, envisages = {}, {}, {}, {}
        arbre = ast.parse((Path(args.reference) / "donjon/planification.py").read_text(encoding="utf-8"))
        fonction = next(n for n in arbre.body if isinstance(n, ast.FunctionDef) and n.name == "_parts_remises")
        namespace = dict(vars(p))
        exec(compile(ast.Module(body=[fonction], type_ignores=[]), "ancienne_part", "exec"), namespace)
        ancienne = namespace["_parts_remises"]
        def detaillee(v, e, o, dans, vises, but=None):
            yield from ancienne(v, e, o, dans, vises)
        import donjon.part_estimee as estimation
        suites = estimation.suites
        def observer_estimation(*a, **k):
            if pile_recherches:
                pile_recherches[-1] = True
            return suites(*a, **k)

        def premier(r):
            if r is None:
                return None
            etapes = p._couper(r[1])
            return etapes[0] if etapes else {}

        def objectif(r):
            if r is None:
                return None
            e = r[2]
            return [e.salle, sorted([list(cle) for cle, valeur in e.faits.items()
                                     if cle[0] in p.TERMINAUX and valeur], key=str)]

        def observer(*a, **k):
            pile_recherches.append(False)
            try:
                r = chercher(*a, **k)
                envisage = pile_recherches[-1]
            finally:
                pile_recherches.pop()
            place = (a[1], json.dumps(k.get("memo"), ensure_ascii=False))
            garde = p._MEMOIRE.get(place) if k.get("memo") is not None else None
            if garde is not None:
                signature = garde[0]
                if envisage:
                    envisages[place] = signature
                elif envisages.get(place) == signature:
                    envisage = True
            if envisage:
                with patch.object(p, "_parts_remises", detaillee), patch.object(p, "_MEMOIRE", memoire_detail), \
                        patch.object(p, "_GRAPHES", graphes_detail), patch.object(p, "_IMPOSSIBLES", impossibles_detail), \
                        patch.object(p, "VERIFIER", False), patch.object(p, "DIAGNOSTIC", None):
                    ref = chercher(*a, **k)
                entree = {"minute": a[0].data["minutes"], "pnj": a[1], "but": k.get("nom"),
                          "choix": premier(r), "detail": premier(ref),
                          "objectif": objectif(r), "objectif_detail": objectif(ref),
                          "cout": r[0] if r else None, "cout_detail": ref[0] if ref else None}
                garde_detail = memoire_detail.get(place)
                if garde_detail is not None:
                    entree["issue_detail"] = garde_detail[2]
                    entree["borne_detail"] = garde_detail[3]
                entree["estimation_choisie"] = bool(r and any(x.get("part_estimee") for x in r[1]))
                entree["identique"] = (entree["choix"] == entree["detail"]
                                        and entree["objectif"] == entree["objectif_detail"])
                if not entree["identique"]:
                    entree["plans"] = [x[1] if x else None for x in (r, ref)]
                comparaisons.append(entree)
                with args.sortie.with_suffix(".jsonl").open("a", encoding="utf-8") as f:
                    f.write(json.dumps(entree, ensure_ascii=False) + "\n")
            return r

    config = dict(verifier=args.verifier, empreintes=False, heures=args.heures,
                  joueurs=c.JOUEURS, depart="tire")
    with ExitStack() as pile:
        for objet, nom, valeur in ((ex, "demander", demande), (ex, "remettre", remise),
                                    (pnj, "_executer", action), (b, "nuit", avec_diagnostic),
                                    (c.audit, "_releve", releve)):
            pile.enter_context(patch.object(objet, nom, valeur))
        if args.justesse:
            pile.enter_context(patch.object(estimation, "suites", observer_estimation))
            pile.enter_context(patch.object(p, "chercher", observer))
        resultat = c.jouer_nuit((args.scenario, args.graine, config))
    resultat["ressources"] = ressources
    resultat["justesse"] = comparaisons
    resultat["bornes_verification"] = p.BORNES
    with gzip.open(args.sortie, "wt", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False)
    return int(resultat["plantage"] is not None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--depot", type=Path, default=RACINE)
    parser.add_argument("--dossier", type=Path, default=RACINE / "artifacts/part-estimee/campagne")
    parser.add_argument("--scenarios", nargs="+", default=["relais", "mine", "auberge", "crue"])
    parser.add_argument("--graines", nargs="+", type=int, default=[1985, 7, 42, 2024])
    parser.add_argument("--heures", type=float, default=8)
    parser.add_argument("--processus", type=int, choices=range(1, 5), default=4)
    parser.add_argument("--justesse", action="store_true")
    parser.add_argument("--verifier", action="store_true")
    parser.add_argument("--verification", type=float, default=0)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--scenario")
    parser.add_argument("--graine", type=int)
    parser.add_argument("--sortie", type=Path)
    args = parser.parse_args()
    if args.worker:
        return worker(args)
    args.dossier.mkdir(parents=True, exist_ok=True)
    variantes = [("branche", args.depot)] if args.justesse or args.verifier else [
        ("reference", args.reference), ("branche", args.depot)]
    taches = [(s, g, nom, depot) for s in args.scenarios for g in args.graines for nom, depot in variantes]
    def lancer(tache):
        s, g, nom, depot = tache
        sortie = (args.dossier / f"{nom}-{s}_{g}.json.gz").resolve()
        commande = [sys.executable, str(Path(__file__).resolve()), "--worker", "--reference",
                    str(args.reference.resolve()), "--depot", str(depot.resolve()), "--scenario", s,
                    "--graine", str(g), "--heures", str(args.heures), "--sortie", str(sortie),
                    "--verification", str(args.verification)]
        for option in ("justesse", "verifier"):
            if getattr(args, option):
                commande.append("--" + option)
        r = subprocess.run(commande, cwd=depot.resolve(), capture_output=True, text=True, encoding="utf-8",
                           creationflags=0x4000 if os.name == "nt" else 0)
        print(nom, s, g, r.returncode, r.stderr[-2500:], flush=True)
        return r.returncode
    with ThreadPoolExecutor(max_workers=args.processus) as pool:
        return int(any(list(pool.map(lancer, taches))))


if __name__ == "__main__":
    raise SystemExit(main())
