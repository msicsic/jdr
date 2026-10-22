"""Suite unittest par fichiers isolés, les plus longs en premier, à priorité réduite.

    python tools/tests.py --processus 4
    python tools/tests.py tests/test_web.py tests/test_tui.py
    python tools/tests.py --motif 'test_*banc*.py'

Les durées, non versionnées, sont gardées dans artifacts/durees_tests.json.
Les processus exécutent la découverte unittest réelle ; ni les méthodes ni les
subtests ne sont comptés artificiellement. Aucun appel au modèle n'est ajouté.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import fnmatch
import importlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

RACINE = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
# Le nom du lanceur ne doit pas masquer le paquet namespace tests/ quand
# Python ajoute tools/ au chemin d'import d'un script exécuté directement.
sys.path[:] = [p for p in sys.path if Path(p or os.curdir).resolve() != SCRIPT.parent]
if str(RACINE) in sys.path:
    sys.path.remove(str(RACINE))
sys.path.insert(0, str(RACINE))
# Charger le namespace du dépôt avant de rendre ses outils importables (les
# tests du comparateur démarrent eux-mêmes des processus multiprocessing).
importlib.import_module("tests")
sys.path.append(str(SCRIPT.parent))

from donjon.banc_pnj import PROCESSUS  # noqa: E402
from priorite import ceder  # noqa: E402


def executer_fichier(fichier):
    """Dans un interpréteur neuf : la même découverte que unittest discover."""
    ceder()
    fichier = Path(fichier).resolve()
    debut = time.perf_counter()
    suite = unittest.TestLoader().discover(str(fichier.parent), pattern=fichier.name)
    flux = io.StringIO()
    resultat = unittest.TextTestRunner(stream=flux, verbosity=0).run(suite)
    return {"fichier": str(fichier), "secondes": time.perf_counter() - debut,
            "tests": resultat.testsRun, "succes": resultat.wasSuccessful(),
            **{cle: [(str(test), trace) for test, trace in getattr(resultat, cle)]
               for cle in ("failures", "errors", "skipped", "expectedFailures")},
            "unexpectedSuccesses": [str(test) for test in resultat.unexpectedSuccesses]}


def lancer_fichier(fichier, dossier):
    """Le JSON est distinct de stdout : les impressions d'un test ne cassent rien."""
    sortie = Path(dossier) / (uuid.uuid4().hex + ".json")
    debut = time.perf_counter()
    commande = [sys.executable, str(SCRIPT), "--_worker", str(fichier), str(sortie)]
    p = subprocess.run(commande, cwd=RACINE, capture_output=True,
                       encoding="utf-8", errors="replace",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    try:
        resultat = json.loads(sortie.read_text(encoding="utf-8"))
        if p.returncode not in (0, 1) or bool(p.returncode) == resultat["succes"]:
            raise ValueError(f"code du processus incohérent : {p.returncode}")
    except (OSError, ValueError, KeyError) as erreur:
        resultat = {"fichier": str(fichier), "tests": 1, "succes": False,
                    "failures": [], "skipped": [], "expectedFailures": [], "unexpectedSuccesses": [],
                    "errors": [(str(fichier), f"Processus de test interrompu : {erreur}\n"
                                f"Code de retour : {p.returncode}\n{p.stdout}\n{p.stderr}")]}
    # Le cache estime le coût total, y compris l'import et le démarrage du processus.
    resultat["secondes"] = time.perf_counter() - debut
    resultat["stdout"], resultat["stderr"] = p.stdout, p.stderr
    return resultat


def charger_durees(chemin):
    try:
        valeurs = json.loads(Path(chemin).read_text(encoding="utf-8"))
        return {k: float(v) for k, v in valeurs.items()
                if isinstance(v, (int, float)) and math.isfinite(v) and v >= 0}
    except (OSError, ValueError, AttributeError):
        return {}


def cle_fichier(fichier):
    try:
        return fichier.relative_to(RACINE).as_posix()
    except ValueError:
        return fichier.as_posix()


def ordonner(fichiers, durees):
    # Sans historique, les fichiers les plus gros sont une estimation de départ.
    return sorted(fichiers, key=lambda f: (-durees.get(cle_fichier(f), 0), -f.stat().st_size, str(f)))


class TestNomme:
    def __init__(self, nom):
        self.nom = nom

    def __str__(self):
        return self.nom

    def shortDescription(self):
        return None


class SuiteParallele:
    """Adaptateur de résultats pour conserver le rendu officiel TextTestRunner."""
    def __init__(self, fichiers, processus, durees, resultats):
        self.fichiers, self.processus = fichiers, processus
        self.durees, self.resultats = durees, resultats

    def __call__(self, resultat):
        with tempfile.TemporaryDirectory(prefix="tests-paralleles-") as dossier:
            with ThreadPoolExecutor(max_workers=min(self.processus, len(self.fichiers))) as pool:
                futurs = {pool.submit(lancer_fichier, f, dossier): f for f in self.fichiers}
                for futur in as_completed(futurs):
                    r = futur.result()
                    self.resultats.append(r)
                    self.durees[cle_fichier(futurs[futur])] = r["secondes"]
                    resultat.testsRun += r["tests"]
                    for cle in ("failures", "errors", "skipped", "expectedFailures"):
                        getattr(resultat, cle).extend((TestNomme(nom), trace) for nom, trace in r[cle])
                    resultat.unexpectedSuccesses.extend(TestNomme(nom) for nom in r["unexpectedSuccesses"])
                    if not r["succes"]:
                        for flux in (r["stdout"], r["stderr"]):
                            if flux:
                                resultat.stream.write(flux)
                                if not flux.endswith("\n"):
                                    resultat.stream.write("\n")
        return resultat


def selectionner(dossier, fichiers, motif):
    if not fichiers:
        return sorted(f.resolve() for f in dossier.glob(motif) if f.is_file() and f.suffix == ".py")
    resultat = set()
    for texte in fichiers:
        chemin = Path(texte)
        candidats = [chemin] if chemin.is_file() else list(Path.cwd().glob(texte))
        if not candidats and not chemin.is_absolute():
            candidats = list(dossier.glob(texte))
        candidats = [p.resolve() for p in candidats if p.is_file() and p.suffix == ".py"
                     and fnmatch.fnmatch(p.name, motif)]
        if not candidats:
            raise ValueError(f"Aucun fichier de test ne correspond à {texte}")
        resultat.update(candidats)
    return sorted(resultat)


def main(argv=None):
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("fichiers", nargs="*", help="fichiers ou motifs, relatifs au cwd ou au dossier des tests")
    parser.add_argument("--motif", default="test_*.py")
    parser.add_argument("--dossier", type=Path, default=RACINE / "tests")
    parser.add_argument("--processus", type=int, default=PROCESSUS,
                        help=f"défaut : {PROCESSUS}, moitié des cœurs ; 1 pour une série isolée par fichier")
    parser.add_argument("--durees", type=Path, default=RACINE / "artifacts" / "durees_tests.json")
    parser.add_argument("--sortie", type=Path, help="résultats détaillés JSON, traces et temps par fichier")
    args = parser.parse_args(argv)
    if args.processus < 1:
        parser.error("--processus doit être strictement positif")
    try:
        fichiers = selectionner(args.dossier.resolve(), args.fichiers, args.motif)
    except ValueError as erreur:
        parser.error(str(erreur))
    if not fichiers:
        parser.error("aucun fichier de test sélectionné")
    ceder()
    durees, resultats = charger_durees(args.durees), []
    fichiers = ordonner(fichiers, durees)
    print(f"{len(fichiers)} fichiers, {min(args.processus, len(fichiers))} processus, priorité réduite",
          file=sys.stderr, flush=True)
    debut = time.perf_counter()
    resultat = unittest.TextTestRunner(verbosity=0).run(SuiteParallele(fichiers, args.processus, durees, resultats))
    secondes = time.perf_counter() - debut
    args.durees.parent.mkdir(parents=True, exist_ok=True)
    # Remplacement atomique ; un cache lu pendant son écriture reste valide.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.durees.parent,
                                     prefix="durees-", suffix=".tmp", delete=False) as f:
        temporaire = Path(f.name)
        json.dump(durees, f, ensure_ascii=False, indent=2)
    try:
        temporaire.replace(args.durees)
    finally:
        temporaire.unlink(missing_ok=True)
    if args.sortie:
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        rapport = {"tests": resultat.testsRun, "succes": resultat.wasSuccessful(),
                   "secondes": secondes, "processus": args.processus,
                   "fichiers": sorted(resultats, key=lambda r: r["fichier"]),
                   **{cle: len(getattr(resultat, cle)) for cle in
                      ("failures", "errors", "skipped", "expectedFailures", "unexpectedSuccesses")}}
        args.sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    return int(not resultat.wasSuccessful())


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--_worker":
        r = executer_fichier(sys.argv[2])
        Path(sys.argv[3]).write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        raise SystemExit(int(not r["succes"]))
    raise SystemExit(main())
