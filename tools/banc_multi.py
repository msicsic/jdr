"""Bancs en parallèle : plusieurs variantes du code, plusieurs passes chacune, un tableau comparatif.

  python tools/banc_multi.py --variante avant=main --variante apres=instructions-mj \\
      --repetitions 3 --paralleles 6 --connexion anthropic

Chaque variante est une référence git, jouée dans son propre worktree ; « nom=. » joue le dépôt
courant tel quel. L'outil de banc est celui du dépôt courant (SEUIL_CODE désigne le code mesuré) :
une variante doit descendre d'un main qui connaît les options qu'il passe au jeu (--reflexion). Une passe joue les scripts de banc du dépôt courant (relais, crypte, atelier
par défaut) avec tools/banc_parties.py --fil. Les worktrees partagent la connexion ChatGPT du
dépôt (SEUIL_AUTH) et sa clé .env. Le résumé donne, par variante, la moyenne et l'étendue de
chaque indicateur sur les passes : une seule passe ne distingue pas une amélioration du hasard.

Une variante résolue en commit réemploie les parties déjà jouées (tools/references.py) :
`artifacts/references/<commit>/banc_multi/<script>-<options>-<empreinte>/partie-<n>.json`, la clé
(`cle.json`) portant le contenu du script et de banc_parties.py, la connexion, l'effort, la
réflexion, le budget d'appels et --offline. La passe i d'un script prend sa i-ième partie rangée ;
seuls les scripts manquants se jouent, puis se rangent (sauf budget épuisé ou erreur technique).
« nom=. » n'est jamais mis en cache ; --sans-cache rejoue tout. Le résumé dit combien de passes
viennent du cache, dont les secondes ont été mesurées dans d'autres conditions de charge.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import references  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
SCRIPTS = [BASE / "tests" / "data" / "bancs" / f"{nom}.json" for nom in ("relais", "crypte", "atelier")]
PRIX_HAIKU = {"entree": 0.10, "sortie": 0.50, "ecriture": 0.125, "lecture": 0.01}  # $ / MTok


def mesurer(fichiers):
    """Indicateurs d'une passe, sur l'ensemble de ses parties (fichiers JSON du banc)."""
    m = dict(tours_mj=0, appels=0, secondes=0.0, replis=0, tours_refus=0, obstacles=0, relances=0, refus=0,
             dollars=0.0, appels_traces=0, avec_reflexion=0)
    durees_tours, fonctions = [], {}
    for f in fichiers:
        for t in json.loads(Path(f).read_text(encoding="utf-8"))["tours"]:
            if t["saisie"] == "quitter":
                continue
            if t["appels"]:
                m["tours_mj"] += 1
                m["secondes"] += t["secondes"]
                durees_tours.append(t["secondes"])
            m["appels"] += t["appels"]
            m["replis"] += bool(t["replis"])
            m["tours_refus"] += bool(t["refus"])
            for e in t.get("fil", []):
                if e.get("etape") == "contrôle narratif":
                    m["obstacles"] += len(e.get("obstacles", []))
                    # Une réponse refusée par le contrôle narratif est redemandée, sauf la troisième (repli)
                    # et une explication qui cède au refus du monde (``sans_relance``).
                    m["relances"] += e.get("tentative", 0) < 3 and not e.get("sans_relance")
                if e.get("etape") == "validation":
                    m["refus"] += 1
                if e.get("etape") != "appel":
                    continue
                m["appels_traces"] += 1
                fonction = e.get("fonction", "inconnue")
                if fonction == "auditer_action":
                    fonction = ("fidelite" if "contenu_conforme" in (e.get("schema") or {}).get("properties", {})
                                else "contre_revue")
                if fonction == "repondre_au_joueur":
                    entree = e.get("entree") or {}
                    if "controle_narratif" in entree:
                        fonction = "revision"
                    else:
                        # L'interprétation expose plusieurs modes ; un récit n'en admet qu'un.
                        modes = ((e.get("schema") or {}).get("properties", {}).get("mode", {}).get("enum", []))
                        fonction = "interpretation" if len(modes) > 1 else "recit"
                mesure = fonctions.setdefault(fonction, {"appels": 0, "secondes": 0.,
                    "premiers_jetons": [], "entree": 0, "cache": 0, "sortie": 0, "reflexion": 0})
                mesure["appels"] += 1
                mesure["secondes"] += e.get("secondes", 0.)
                if e.get("premier_jeton") is not None:
                    mesure["premiers_jetons"].append(e["premier_jeton"])
                brut, u = e.get("brut") or {}, e.get("usage") or {}
                mesure["entree"] += u.get("input_tokens", 0)
                mesure["cache"] += (u.get("input_tokens_details") or {}).get("cached_tokens", 0)
                mesure["sortie"] += u.get("output_tokens", 0)
                mesure["reflexion"] += (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
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
            "mediane_secondes_par_tour": statistics.median(durees_tours) if durees_tours else 0.,
            "fonctions": fonctions,
            "replis": m["replis"], "tours_refus": m["tours_refus"], "obstacles": m["obstacles"],
            "relances": m["relances"], "refus": m["refus"],
            "cout": m["dollars"], "reflexion": m["avec_reflexion"] / (m["appels_traces"] or 1),
            "tours_mj": m["tours_mj"]}


INDICATEURS = [("appels_par_tour", "Appels par tour MJ", "{:.2f}"),
               ("secondes_par_tour", "Secondes par tour MJ", "{:.1f}"),
               ("mediane_secondes_par_tour", "Médiane des secondes par tour MJ", "{:.1f}"),
               ("replis", "Tours en repli", "{:.1f}"),
               ("tours_refus", "Tours avec refus", "{:.1f}"),
               ("obstacles", "Obstacles narratifs", "{:.1f}"),
               ("relances", "Relances narratives", "{:.1f}"),
               ("refus", "Refus (moteur, contre-revue)", "{:.1f}"),
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
            valeurs = [m.get(cle, 0) for v, m in passes if v == nom]  # une mesure plus ancienne en manque
            moyenne = statistics.mean(valeurs)
            etendue = (f" ({forme.format(min(valeurs))} – {forme.format(max(valeurs))})"
                       if len(valeurs) > 1 else "")
            cellules.append(forme.format(moyenne) + etendue)
        lignes.append(f"| {libelle} | " + " | ".join(cellules) + " |")
    lignes += ["", "| Variante / fonction | Appels | s/tour | Part de l'attente modèle | Premier delta moyen (s) | Jetons entrée / cache / sortie / réflexion |",
               "|---|---:|---:|---:|---:|---|"]
    for nom in noms:
        mesures = [m for v, m in passes if v == nom]
        tours = sum(m["tours_mj"] for m in mesures) or 1
        total = sum(f["secondes"] for m in mesures for f in m.get("fonctions", {}).values()) or 1
        for fonction in sorted({f for m in mesures for f in m.get("fonctions", {})}):
            fs = [m["fonctions"][fonction] for m in mesures if fonction in m.get("fonctions", {})]
            secondes = sum(f["secondes"] for f in fs)
            premiers = [p for f in fs for p in f["premiers_jetons"]]
            jetons = " / ".join(str(sum(f[k] for f in fs)) for k in ("entree", "cache", "sortie", "reflexion"))
            premier = f"{statistics.mean(premiers):.2f}" if premiers else "non mesuré"
            lignes.append(f"| {nom} / {fonction} | {sum(f['appels'] for f in fs)} | {secondes/tours:.2f} | {secondes/total:.1%} | {premier} | {jetons} |")
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


FORMAT_PARTIE = 1


def cle_partie(script, args):
    """Tout ce qui change une partie, sauf le commit (le dossier) : le script et l'outil de banc du
    lanceur (leur contenu), la connexion et ses options, le budget d'appels."""
    return {"outil": "banc_multi", "format_partie": FORMAT_PARTIE, "script": Path(script).stem,
            "script_contenu": references.empreinte_fichiers(script),
            "banc_parties": references.empreinte_fichiers(BASE / "tools" / "banc_parties.py"),
            "connexion": args.connexion, "effort": args.effort, "reflexion": args.reflexion,
            "max_appels": args.max_appels, "offline": bool(args.offline)}


def dossier_parties(cache, commit, cle):
    nom = (f'{cle["script"]}-{cle["connexion"]}-{cle["effort"]}-{cle["reflexion"]}-m{cle["max_appels"]}'
           f'{"-offline" if cle["offline"] else ""}-{references.empreinte(json.dumps(cle, sort_keys=True))}')
    return Path(cache) / commit / "banc_multi" / nom


def parties_en_cache(dossier, cle):
    """Les parties déjà jouées pour cette clé, dans l'ordre où elles ont été rangées."""
    if not references.lire(dossier / "cle.json", cle):
        return []
    return sorted(dossier.glob("partie-*.json"), key=lambda f: int(f.stem.split("-")[1]))


def rangeable(fichier):
    """Une partie arrêtée par le budget ou touchée par une erreur technique (réseau, délai) ne dit
    rien de la variante : elle n'est pas rangée."""
    partie = json.loads(Path(fichier).read_text(encoding="utf-8"))
    return not partie.get("arret") and not any(t.get("erreurs") for t in partie["tours"])


def ranger_partie(dossier, cle, fichier):
    if not references.lire(dossier / "cle.json", cle):
        references.ecrire(dossier / "cle.json", cle, None)
    contenu = Path(fichier).read_bytes()
    n = len(list(dossier.glob("partie-*.json"))) + 1
    while True:
        try:
            # Création exclusive : deux bancs simultanés ne rangent jamais sous le même numéro.
            with open(dossier / f"partie-{n}.json", "xb") as f:
                f.write(contenu)
            return
        except FileExistsError:
            n += 1


def jouer_passe(nom, i, depot, sortie, args, scripts):
    """Joue les scripts d'une passe et rend ses parties (un fichier JSON par script)."""
    dossier = sortie / f"{nom}-r{i}"
    dossier.mkdir(parents=True, exist_ok=True)
    # L'outil de banc est celui de ce dépôt ; SEUIL_CODE lui fait charger le code de la variante.
    commande = [sys.executable, str(BASE / "tools" / "banc_parties.py"), *map(str, scripts),
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
    return fichiers


def planifier(variantes, commits, args, cache):
    """Pour chaque passe (variante, numéro) : les parties lues dans le cache, par script, et les
    scripts qui restent à jouer. La passe i d'un script réemploie sa i-ième partie rangée."""
    plan = {}
    for nom in variantes:
        rangees = {}
        if cache and commits[nom]:
            for script in args.scripts:
                cle = cle_partie(script, args)
                rangees[script] = parties_en_cache(dossier_parties(cache, commits[nom], cle), cle)
        for i in range(1, args.repetitions + 1):
            lues = {s: rangees[s][i - 1] for s in args.scripts if len(rangees.get(s, [])) >= i}
            plan[(nom, i)] = (lues, [s for s in args.scripts if s not in lues])
    return plan


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
    p.add_argument("--sortie", type=Path, help="dossier des bruts (défaut : artifacts/bancs-multi/horodatage)")
    p.add_argument("--offline", action="store_true", help="aucun appel au modèle (vérifier le lanceur)")
    p.add_argument("--sans-cache", action="store_true",
                   help="rejoue toutes les passes, sans lire ni ranger de partie dans artifacts/references/<commit>/")
    p.add_argument("scripts", nargs="*", type=Path, default=SCRIPTS)
    args = p.parse_args(argv)
    # Les scripts viennent du dépôt du lanceur, même quand la variante jouée
    # précède leur création et possède un autre répertoire courant.
    args.scripts = list(dict.fromkeys(script.resolve() for script in args.scripts))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    variantes = {}
    for v in args.variante:
        nom, _, ref = v.partition("=")
        variantes[nom] = ref or nom
    # Seule une variante résolue en commit entre dans le cache ; « . » (le dépôt courant) jamais.
    commits = {nom: references.resoudre(BASE, ref) for nom, ref in variantes.items()}
    cache = None if args.sans_cache else references.dossier(BASE)
    plan = planifier(variantes, commits, args, cache)
    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Un dossier de worktrees par lancement : deux bancs simultanés ne se marchent pas dessus.
    racine = Path(tempfile.gettempdir()) / "seuil-bancs" / f"{horodatage}-{os.getpid()}"
    sortie = args.sortie or BASE / "artifacts" / "bancs-multi" / f"{horodatage}-{os.getpid()}"
    sortie.mkdir(parents=True, exist_ok=True)
    # Un worktree seulement pour une variante qui a encore une partie à jouer.
    depots = {nom: preparer_variante(nom, commits[nom] or ref, racine) for nom, ref in variantes.items()
              if any(plan[(nom, i)][1] for i in range(1, args.repetitions + 1))}
    # Les passes s'entrelacent : la première de chaque variante part d'abord.
    travaux = [(nom, i) for i in range(1, args.repetitions + 1) for nom in variantes]
    jouees = {}
    try:
        with ThreadPoolExecutor(max_workers=args.paralleles) as pool:
            futurs = {pool.submit(jouer_passe, nom, i, depots[nom], sortie, args, plan[(nom, i)][1]): (nom, i)
                      for nom, i in travaux if plan[(nom, i)][1]}
            for futur in as_completed(futurs):
                nom, i = futurs[futur]
                try:
                    jouees[(nom, i)] = futur.result()
                    print(f"{nom}-r{i} terminé ({len(jouees)}/{len(futurs)})", flush=True)
                except RuntimeError as exc:
                    print(exc, flush=True)
    finally:
        if not args.garder:
            for nom, depot in depots.items():
                if depot != BASE:
                    subprocess.run(["git", "-C", str(BASE), "worktree", "remove", "--force", str(depot)],
                                   capture_output=True)
    passes, provenance = [], {nom: {"cache": 0, "partielles": 0, "jouees": 0} for nom in variantes}
    for nom, i in travaux:
        lues, a_jouer = plan[(nom, i)]
        if a_jouer and (nom, i) not in jouees:
            continue  # passe en échec : ni mesurée ni rangée
        fichiers = list(lues.values()) + jouees.get((nom, i), [])
        if cache and commits[nom]:
            for f in jouees.get((nom, i), []):
                stem = json.loads(f.read_text(encoding="utf-8"))["script"]
                script = next((s for s in a_jouer if s.stem == stem), None)
                if script is not None and rangeable(f):
                    cle = cle_partie(script, args)
                    ranger_partie(dossier_parties(cache, commits[nom], cle), cle, f)
        provenance[nom]["cache" if not a_jouer else "partielles" if lues else "jouees"] += 1
        passes.append((nom, mesurer(fichiers)))
    if not passes:
        print("Aucune passe n'a abouti.")
        return 1
    tableau = resumer(passes)
    lignes_cache = []
    for nom in variantes:
        n = provenance[nom]
        if not commits[nom] or not cache:
            lignes_cache.append(f"- {nom} : {'dépôt courant' if not commits[nom] else 'sans cache'}, "
                                f"{n['jouees']} passes jouées, non mises en cache")
        else:
            lignes_cache.append(f"- {nom} ({commits[nom][:10]}) : {n['cache']} passes du cache, "
                                f"{n['partielles']} en partie du cache, {n['jouees']} jouées ici")
    entete = (f"Banc multiple du {datetime.now():%Y-%m-%d %H:%M} — {args.connexion}, effort {args.effort}, "
              f"réflexion {args.reflexion}\nVariantes : " + ", ".join(f"{n}={r}" for n, r in variantes.items())
              + "\nMoyenne par passe des parties (étendue entre parenthèses).\n"
              + f"Cache ({cache or 'désactivé'}) ; les secondes d'une partie du cache ont été mesurées "
              "lors de son jeu, dans d'autres conditions de charge :\n" + "\n".join(lignes_cache) + "\n\n")
    (sortie / "resume.md").write_text(entete + tableau + "\n", encoding="utf-8")
    (sortie / "resume.json").write_text(json.dumps({"passes": passes, "provenance": provenance},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n" + entete + tableau + f"\n\nDétails : {sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
