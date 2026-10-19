"""Bancs en parallèle : plusieurs variantes du code, plusieurs passes chacune, un tableau comparatif.

  python tools/banc_multi.py --variante avant=main --variante apres=instructions-mj \\
      --repetitions 3 --paralleles 6 --connexion anthropic

Chaque variante est une référence git, jouée dans son propre worktree ; « nom=. » joue le dépôt
courant tel quel. L'outil de banc est celui du dépôt courant (SEUIL_CODE désigne le code mesuré) :
une variante doit descendre d'un main qui connaît les options qu'il passe au jeu (--reflexion). Une passe joue les scripts de banc du dépôt courant (relais, crypte, atelier
par défaut) avec tools/banc_parties.py --fil. Les worktrees partagent la connexion ChatGPT du
dépôt (SEUIL_AUTH) et sa clé .env. Le résumé donne, par variante, la moyenne et l'étendue de
chaque indicateur sur les passes : une seule passe ne distingue pas une amélioration du hasard.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parents[1]
SCRIPTS = [BASE / "tests" / "data" / "bancs" / f"{nom}.json" for nom in ("relais", "crypte", "atelier")]
PRIX_HAIKU = {"entree": 0.10, "sortie": 0.50, "ecriture": 0.125, "lecture": 0.01}  # $ / MTok


def mesurer(fichiers):
    """Indicateurs d'une passe, sur l'ensemble de ses parties (fichiers JSON du banc)."""
    m = dict(tours_mj=0, appels=0, secondes=0.0, replis=0, tours_refus=0, obstacles=0,
             dollars=0.0, appels_traces=0, avec_reflexion=0)
    for f in fichiers:
        for t in json.loads(Path(f).read_text(encoding="utf-8"))["tours"]:
            if t["saisie"] == "quitter":
                continue
            if t["appels"]:
                m["tours_mj"] += 1
                m["secondes"] += t["secondes"]
            m["appels"] += t["appels"]
            m["replis"] += bool(t["replis"])
            m["tours_refus"] += bool(t["refus"])
            for e in t.get("fil", []):
                if e.get("etape") == "contrôle narratif":
                    m["obstacles"] += len(e.get("obstacles", []))
                if e.get("etape") != "appel":
                    continue
                m["appels_traces"] += 1
                brut, u = e.get("brut") or {}, e.get("usage") or {}
                blocs = [b.get("type") for b in (brut.get("contenu", []) if isinstance(brut, dict) else brut)
                         if isinstance(b, dict)]
                if {"thinking", "reasoning"} & set(blocs) or (u.get("output_tokens_details") or {}).get("reasoning_tokens"):
                    m["avec_reflexion"] += 1
                if "cache_creation_input_tokens" in u:  # Anthropic : coût estimé
                    m["dollars"] += (u["input_tokens"] * PRIX_HAIKU["entree"] + u["output_tokens"] * PRIX_HAIKU["sortie"]
                                     + u.get("cache_creation_input_tokens", 0) * PRIX_HAIKU["ecriture"]
                                     + u.get("cache_read_input_tokens", 0) * PRIX_HAIKU["lecture"]) / 1e6
    tours = m["tours_mj"] or 1
    return {"appels_par_tour": m["appels"] / tours, "secondes_par_tour": m["secondes"] / tours,
            "replis": m["replis"], "tours_refus": m["tours_refus"], "obstacles": m["obstacles"],
            "cout": m["dollars"], "reflexion": m["avec_reflexion"] / (m["appels_traces"] or 1),
            "tours_mj": m["tours_mj"]}


INDICATEURS = [("appels_par_tour", "Appels par tour MJ", "{:.2f}"),
               ("secondes_par_tour", "Secondes par tour MJ", "{:.1f}"),
               ("replis", "Tours en repli", "{:.1f}"),
               ("tours_refus", "Tours avec refus", "{:.1f}"),
               ("obstacles", "Obstacles narratifs", "{:.1f}"),
               ("reflexion", "Part d'appels avec réflexion", "{:.0%}"),
               ("cout", "Coût API par passe ($)", "{:.3f}")]


def resumer(passes):
    """Par variante : moyenne et étendue de chaque indicateur sur ses passes."""
    lignes = []
    noms = list(dict.fromkeys(nom for nom, _ in passes))
    entete = "| Indicateur | " + " | ".join(f"{n} ({sum(1 for v, _ in passes if v == n)} passes)" for n in noms) + " |"
    lignes += [entete, "|" + "---|" * (len(noms) + 1)]
    for cle, libelle, forme in INDICATEURS:
        cellules = []
        for nom in noms:
            valeurs = [m[cle] for v, m in passes if v == nom]
            moyenne = statistics.mean(valeurs)
            etendue = (f" ({forme.format(min(valeurs))} – {forme.format(max(valeurs))})"
                       if len(valeurs) > 1 else "")
            cellules.append(forme.format(moyenne) + etendue)
        lignes.append(f"| {libelle} | " + " | ".join(cellules) + " |")
    return "\n".join(lignes)


def preparer_variante(nom, ref, racine):
    if ref == ".":
        return BASE
    dossier = racine / nom
    if dossier.exists():
        subprocess.run(["git", "-C", str(BASE), "worktree", "remove", "--force", str(dossier)],
                       capture_output=True)
        shutil.rmtree(dossier, ignore_errors=True)
    subprocess.run(["git", "-C", str(BASE), "worktree", "prune"], check=True)
    subprocess.run(["git", "-C", str(BASE), "worktree", "add", "--detach", str(dossier), ref],
                   check=True, capture_output=True)
    if (BASE / ".env").exists():
        shutil.copy2(BASE / ".env", dossier / ".env")
    return dossier


def jouer_passe(nom, i, depot, sortie, args):
    dossier = sortie / f"{nom}-r{i}"
    dossier.mkdir(parents=True, exist_ok=True)
    # L'outil de banc est celui de ce dépôt ; SEUIL_CODE lui fait charger le code de la variante.
    commande = [sys.executable, str(BASE / "tools" / "banc_parties.py"), *map(str, args.scripts),
                "--fil", "--sortie", str(dossier), "--etiquette", f"{nom}-r{i}",
                "--max-appels", str(args.max_appels), "--connexion", args.connexion,
                "--effort", args.effort, "--reflexion", args.reflexion] + (["--offline"] if args.offline else [])
    env = {**os.environ, "SEUIL_AUTH": os.environ.get("SEUIL_AUTH") or str(BASE / ".seuil-auth"), "SEUIL_CODE": str(depot),
           "PYTHONIOENCODING": "utf-8"}
    with open(dossier / "journal.txt", "w", encoding="utf-8") as journal:
        code = subprocess.run(commande, cwd=depot, env=env, stdout=journal, stderr=subprocess.STDOUT).returncode
    fichiers = sorted(dossier.glob("*.json"))
    if code or not fichiers:
        raise RuntimeError(f"{nom}-r{i} : échec (code {code}), voir {dossier / 'journal.txt'}")
    return nom, mesurer(fichiers)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--variante", action="append", required=True, metavar="NOM=REF",
                   help="référence git à jouer (répétable) ; NOM=. joue le dépôt courant")
    p.add_argument("--repetitions", type=int, default=3)
    p.add_argument("--paralleles", type=int, default=3, help="passes simultanées au plus")
    p.add_argument("--connexion", choices=("chatgpt", "anthropic"), default="anthropic")
    p.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    p.add_argument("--reflexion", choices=("libre", "imposee"), default="libre")
    p.add_argument("--max-appels", type=int, default=500)
    p.add_argument("--garder", action="store_true", help="garde les worktrees après le banc")
    p.add_argument("--offline", action="store_true", help="aucun appel au modèle (vérifier le lanceur)")
    p.add_argument("scripts", nargs="*", type=Path, default=SCRIPTS)
    args = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    variantes = {}
    for v in args.variante:
        nom, _, ref = v.partition("=")
        variantes[nom] = ref or nom
    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Un dossier de worktrees par lancement : deux bancs simultanés ne se marchent pas dessus.
    racine = Path(tempfile.gettempdir()) / "seuil-bancs" / f"{horodatage}-{os.getpid()}"
    sortie = BASE / "artifacts" / "bancs-multi" / f"{horodatage}-{os.getpid()}"
    depots = {nom: preparer_variante(nom, ref, racine) for nom, ref in variantes.items()}
    # Les passes s'entrelacent : la première de chaque variante part d'abord.
    travaux = [(nom, i) for i in range(1, args.repetitions + 1) for nom in variantes]
    passes = []
    try:
        with ThreadPoolExecutor(max_workers=args.paralleles) as pool:
            futurs = {pool.submit(jouer_passe, nom, i, depots[nom], sortie, args): (nom, i) for nom, i in travaux}
            for futur in as_completed(futurs):
                nom, i = futurs[futur]
                try:
                    passes.append(futur.result())
                    print(f"{nom}-r{i} terminé ({len(passes)}/{len(travaux)})", flush=True)
                except RuntimeError as exc:
                    print(exc, flush=True)
    finally:
        if not args.garder:
            for nom, depot in depots.items():
                if depot != BASE:
                    subprocess.run(["git", "-C", str(BASE), "worktree", "remove", "--force", str(depot)],
                                   capture_output=True)
    if not passes:
        print("Aucune passe n'a abouti.")
        return 1
    tableau = resumer(sorted(passes, key=lambda p: list(variantes).index(p[0])))
    entete = (f"Banc multiple du {datetime.now():%Y-%m-%d %H:%M} — {args.connexion}, effort {args.effort}, "
              f"réflexion {args.reflexion}\nVariantes : " + ", ".join(f"{n}={r}" for n, r in variantes.items())
              + "\nMoyenne par passe des trois parties (étendue entre parenthèses).\n\n")
    (sortie / "resume.md").write_text(entete + tableau + "\n", encoding="utf-8")
    (sortie / "resume.json").write_text(json.dumps(passes, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n" + entete + tableau + f"\n\nDétails : {sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
