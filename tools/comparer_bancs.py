"""Compare deux versions au banc sans joueur, référence puis branche.

    python tools/comparer_bancs.py --reference main --branche HEAD --empreintes
    python tools/comparer_bancs.py --scenarios relais mine --processus 2 --sortie artifacts/ab.json

La branche omise désigne les fichiers du worktree courant, modifications comprises.
Les mesures de temps incluent les relevés d'audit en mode normal ; le mode identité
n'observe que chronique, mesures et état complet. Une divergence déclenche un rejeu
instrumenté pour la dater, exclu des temps comparés.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack, contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
RACINE = SCRIPT.parents[1]
# Le moteur est toujours celui du cwd du processus, même quand le script vient
# d'une autre branche. audit_nuits reste celui livré avec cet outil.
for chemin in (RACINE, Path.cwd()):
    if str(chemin) in sys.path:
        sys.path.remove(str(chemin))
    sys.path.insert(0, str(chemin))
import audit_nuits as audit  # noqa: E402

JOUEURS = audit.JOUEURS
PROCESSUS = max(1, (os.cpu_count() or 2) // 2)


def git(racine, *arguments):
    return subprocess.run(["git", "-C", str(racine), *arguments], check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


@contextmanager
def worktree_temporaire(racine, reference):
    """Worktree détaché possédé par cet appel ; nettoyage même après une erreur."""
    revision = git(racine, "rev-parse", "--verify", reference + "^{commit}")
    # Dans le dépôt : compatible avec les règles de travail et les permissions locales.
    parent = Path(racine) / ".worktrees"
    parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ref-", dir=parent) as dossier:
        chemin = Path(dossier) / "arbre"
        try:
            git(racine, "worktree", "add", "--detach", str(chemin), revision)
            yield chemin
        finally:
            # Un échec partiel de worktree add peut lui aussi laisser un enregistrement.
            if chemin.exists():
                git(racine, "worktree", "remove", "--force", str(chemin))


def empreinte(valeur):
    return hashlib.sha256(json.dumps(valeur, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def jouer_nuit(tache):
    """Réutilise nuit(), avec capture de data, temps CPU et relevés d'audit."""
    from donjon import banc_pnj as banc, planification, pnj
    scenario, graine, config = tache
    banc.ceder()
    planification.VERIFIER = config["verifier"]
    capture, releves, minutes = {}, [], {}
    creer, oisifs, percevoir = banc.creer, banc._oisifs_urgents, pnj.percevoir_tous

    def creer_capture(*a, **k):
        monde = creer(*a, **k)
        capture["monde"] = monde
        if config.get("localiser"):
            minutes[str(monde.data["minutes"])] = empreinte(monde.data)
        return monde

    def relever(monde):
        releves.append(audit._releve(monde))
        return oisifs(monde)

    def observer(monde):
        resultat = percevoir(monde)
        # Dernier état perçu de chaque minute, sans changer l'horloge ni le pas.
        minutes[str(monde.data["minutes"])] = empreinte(monde.data)
        return resultat

    resultat = {"scenario": scenario, "graine": graine, "heures": config["heures"],
                "plantage": None}
    with ExitStack() as pile:
        pile.enter_context(patch.object(banc, "creer", creer_capture))
        if not config["empreintes"]:
            pile.enter_context(patch.object(banc, "_oisifs_urgents", relever))
        if config.get("localiser"):
            pile.enter_context(patch.object(pnj, "percevoir_tous", observer))
        debut, cpu = time.perf_counter(), time.process_time()
        try:
            _, _, donnees = banc.nuit(scenario, graine, config["heures"],
                                     config["joueurs"][scenario], depart=config["depart"])
            resultat["donnees"] = donnees
        except Exception as erreur:
            monde = capture.get("monde")
            resultat.update(donnees=None, plantage={"type": type(erreur).__name__,
                "message": str(erreur), "trace": traceback.format_exc(),
                "minute": monde.data["minutes"] if monde else None})
        resultat.update(secondes=time.perf_counter() - debut,
                        secondes_cpu=time.process_time() - cpu)
    monde = capture.get("monde")
    if monde is not None:
        resultat["etat_final"] = empreinte(monde.data)
    if config.get("localiser"):
        if monde is not None:
            minutes[str(monde.data["minutes"])] = empreinte(monde.data)
        resultat["minutes"] = minutes
    if not config["empreintes"]:
        resultat["releves"] = releves
        if monde is not None:
            resultat["final"] = audit._final(monde)
        resultat["boucles"] = audit.boucles(resultat)
        resultat["constats"] = audit.analyser_nuit(resultat)
    return resultat


def executer_lot(config):
    taches = [(s, g, config) for s in config["scenarios"] for g in config["graines"]]
    with ProcessPoolExecutor(max_workers=min(config["processus"], len(taches)), max_tasks_per_child=1) as pool:
        return list(pool.map(jouer_nuit, taches))


def lancer(racine, config, dossier, nom):
    entree, sortie = Path(dossier) / f"{nom}-entree.json", Path(dossier) / f"{nom}.json"
    entree.write_text(json.dumps(config), encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    subprocess.run([sys.executable, str(SCRIPT), "--_worker", str(entree), str(sortie)],
                   cwd=racine, env=env, check=True)
    return json.loads(sortie.read_text(encoding="utf-8"))


def comparer_identite(avant, apres):
    """L'ordre du lot définit la première nuit ; aucun temps n'entre dans l'identité."""
    if len(avant) != len(apres):
        raise ValueError("Les lots n'ont pas le même nombre de nuits")
    for a, b in zip(avant, apres):
        if (a["scenario"], a["graine"]) != (b["scenario"], b["graine"]):
            raise ValueError("Les nuits ne sont pas appariées")
        if a["plantage"] or b["plantage"]:
            return {"scenario": a["scenario"], "graine": a["graine"], "parties": ["plantage"],
                    "minute": (a["plantage"] or b["plantage"])["minute"]}
        parties = [k for k in ("chronique", "mesures") if a["donnees"][k] != b["donnees"][k]]
        if a["etat_final"] != b["etat_final"]:
            parties.append("etat_final")
        if parties:
            dates = []
            ca, cb = a["donnees"]["chronique"], b["donnees"]["chronique"]
            for i in range(max(len(ca), len(cb))):
                x, y = ca[i] if i < len(ca) else None, cb[i] if i < len(cb) else None
                if x != y:
                    dates.extend(c["minute"] for c in (x, y) if c is not None)
                    break
            # Un état interne peut diverger avant le premier geste raconté.
            for m in sorted(set(a.get("minutes", {})) | set(b.get("minutes", {})), key=int):
                if a.get("minutes", {}).get(m) != b.get("minutes", {}).get(m):
                    dates.append(int(m))
                    break
            return {"scenario": a["scenario"], "graine": a["graine"], "parties": parties,
                    "minute": min(dates) if dates else None}
    return None


def statistiques(valeurs):
    return {"moyenne": sum(valeurs) / len(valeurs), "min": min(valeurs), "max": max(valeurs)}


def resumer(avant, apres):
    tableaux = {}
    for scenario in dict.fromkeys(n["scenario"] for n in avant):
        lots = [[n for n in lot if n["scenario"] == scenario] for lot in (avant, apres)]
        lignes = []
        def mesures(n):
            return {**(n.get("donnees") or {}).get("mesures", {}),
                    **{"boucles_" + k: v for k, v in n.get("boucles", {}).items()},
                    "violations": int(n["plantage"] is not None),
                    "secondes": n["secondes"], "secondes_cpu": n["secondes_cpu"]}
        valeurs = [[mesures(n) for n in lot] for lot in lots]
        cles = sorted({k for lot in valeurs for n in lot for k in n})
        for cle in cles:
            stats = [statistiques([n[cle] for n in lot if cle in n])
                     if any(cle in n for n in lot) else None for lot in valeurs]
            delta = stats[1]["moyenne"] - stats[0]["moyenne"] if all(stats) else None
            relatif = (delta / abs(stats[0]["moyenne"]) if stats[0]["moyenne"] else None) if all(stats) else None
            lignes.append({"mesure": cle, "reference": stats[0], "branche": stats[1],
                           "ecart": delta, "relatif": relatif,
                           "notable": delta != 0 and (relatif is None or abs(relatif) >= .1)})
        tableaux[scenario] = sorted(lignes, key=lambda x: (not x["notable"], x["mesure"]))
    return tableaux


def afficher(rapport):
    def texte(s):
        return "absent" if s is None else f'{s["moyenne"]:.3g} [{s["min"]:.3g}–{s["max"]:.3g}]'
    if rapport["config"]["empreintes"]:
        d = rapport["divergence"]
        if d is None:
            print("identique : chronique, mesures et état final complet, nuit par nuit")
        else:
            minute = f'minute {d["minute"]}' if d["minute"] is not None else "minute indéterminée"
            print(f'Première divergence : {d["scenario"]}, graine {d["graine"]}, {minute} ({", ".join(d["parties"])}).')
        return
    from donjon.banc_pnj import divergence
    print("Moyenne [min–max] ; * écart ≥ 10 % ou apparition/disparition d'une mesure")
    for scenario, lignes in rapport["tableaux"].items():
        print(f"\n{scenario} : référence → branche")
        for l in lignes:
            print(f'{"*" if l["notable"] else " "} {l["mesure"]:36} {texte(l["reference"]):24} → {texte(l["branche"])}')
        for cote in ("reference", "branche"):
            nuits = [n for n in rapport[cote]["nuits"] if n["scenario"] == scenario]
            bonnes = [n["donnees"] for n in nuits if n["donnees"]]
            print(cote + ": " + (divergence(bonnes) if bonnes else "aucune nuit achevée"))
            for n in nuits:
                if n["plantage"]:
                    p = n["plantage"]
                    print(f'  VIOLATION/PLANTAGE graine {n["graine"]}, minute {p["minute"]} : {p["type"]}: {p["message"]}')
            codes = {}
            for n in nuits:
                for c in n.get("constats", []):
                    codes[c["code"]] = codes.get(c["code"], 0) + 1
            print("  Constats de l'audit : " + json.dumps(codes, ensure_ascii=False))


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reference", default="main")
    parser.add_argument("--branche", help="référence git ; omise : worktree courant")
    parser.add_argument("--scenarios", "--scenario", nargs="+", choices=tuple(JOUEURS), default=["relais"])
    parser.add_argument("--joueur", action="append", default=[], metavar="SCENARIO=SALLE")
    parser.add_argument("--graines", nargs="+", type=int, default=[1985, 7, 42, 2024])
    parser.add_argument("--heures", type=float)
    parser.add_argument("--depart", choices=("tire", "fixe"), default="tire")
    parser.add_argument("--processus", type=int, default=PROCESSUS)
    parser.add_argument("--verifier", action="store_true")
    parser.add_argument("--empreintes", action="store_true")
    parser.add_argument("--sortie", type=Path)
    args = parser.parse_args(argv)
    heures = args.heures if args.heures is not None else (2 if args.empreintes else 4)
    if args.processus < 1 or not math.isfinite(heures) or heures <= 0:
        parser.error("--processus et --heures doivent être strictement positifs et finis")
    joueurs = dict(JOUEURS)
    for valeur in args.joueur:
        scenario, sep, salle = valeur.partition("=")
        if scenario not in joueurs or not sep or not salle:
            parser.error("--joueur attend SCENARIO=SALLE")
        joueurs[scenario] = salle
    config = {"scenarios": list(dict.fromkeys(args.scenarios)), "graines": list(dict.fromkeys(args.graines)),
              "heures": heures, "depart": args.depart, "processus": args.processus,
              "verifier": args.verifier, "empreintes": args.empreintes, "joueurs": joueurs}
    racine = Path(git(Path.cwd(), "rev-parse", "--show-toplevel"))
    with ExitStack() as pile:
        reference = pile.enter_context(worktree_temporaire(racine, args.reference))
        branche = pile.enter_context(worktree_temporaire(racine, args.branche)) if args.branche else racine
        dossier = pile.enter_context(tempfile.TemporaryDirectory(prefix="comparaison-"))
        rapport = {"config": config}
        for cote, arbre, nom in (("reference", reference, args.reference), ("branche", branche, args.branche or "worktree")):
            print(f"{cote} : {nom}, {len(config['scenarios']) * len(config['graines'])} nuits", flush=True)
            rapport[cote] = {"nom": nom, "commit": git(arbre, "rev-parse", "HEAD"),
                            "modifications": git(arbre, "status", "--porcelain"),
                            "nuits": lancer(arbre, config, dossier, cote)}
        avant, apres = rapport["reference"]["nuits"], rapport["branche"]["nuits"]
        rapport["divergence"] = comparer_identite(avant, apres) if args.empreintes else None
        d = rapport["divergence"]
        if d and "plantage" not in d["parties"]:
            localisation = {**config, "scenarios": [d["scenario"]], "graines": [d["graine"]], "localiser": True}
            a = lancer(reference, localisation, dossier, "localisation-reference")
            b = lancer(branche, localisation, dossier, "localisation-branche")
            rapport["divergence"] = comparer_identite(a, b)
        rapport["tableaux"] = {} if args.empreintes else resumer(avant, apres)
    if args.sortie:
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        args.sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    afficher(rapport)
    return int(bool(rapport["divergence"]) or any(n["plantage"] for n in avant + apres))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--_worker":
        configuration = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        Path(sys.argv[3]).write_text(json.dumps(executer_lot(configuration), ensure_ascii=False), encoding="utf-8")
    else:
        raise SystemExit(main())
