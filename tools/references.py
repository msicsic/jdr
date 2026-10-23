"""Résultats de référence calculés une fois par commit (`artifacts/references/<commit>/`).

    python tools/references.py lister
    python tools/references.py purger --garder 20 [--simulation]

Le cache est celui du dépôt principal, partagé par ses worktrees (`SEUIL_REFERENCES` le déplace).
Seul un commit résolu y entre : jamais un worktree ni une référence qui bouge, qui sont résolus en
commit avant toute lecture. Chaque outil range ses résultats sous `<commit>/<outil>/`, avec une clé
explicite (format, paramètres qui changent le résultat) relue et comparée avant tout réemploi.
`comparer_bancs.py` et `banc_multi.py` s'en servent ; `--sans-cache` les fait tout rejouer.

`purger` retire les commits qui ne sont plus des ancêtres de `main` et, avec `--garder N`, ceux qui
ont plus de N commits de retard sur `main`. Un dossier qui ne se résout pas en commit est signalé,
jamais retiré.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

FORMAT = 1


def git(racine, *arguments, verifier=True):
    resultat = subprocess.run(["git", "-C", str(racine), *arguments], capture_output=True, text=True,
                              encoding="utf-8")
    if verifier and resultat.returncode:
        raise RuntimeError(f"git {' '.join(arguments)} : {resultat.stderr.strip()}")
    return resultat.stdout.strip() if not resultat.returncode else None


def depot_principal(chemin) -> Path:
    """Racine du dépôt principal, même depuis un worktree (le cache y est partagé)."""
    commun = Path(git(chemin, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    return commun.parent if commun.name == ".git" else commun


def dossier(chemin=".") -> Path:
    return Path(os.environ.get("SEUIL_REFERENCES") or depot_principal(chemin) / "artifacts" / "references")


def resoudre(racine, reference):
    """Le commit que désigne `reference`, ou None pour le worktree courant ou une référence inconnue
    (jamais mis en cache)."""
    if reference in (None, "", "."):
        return None
    return git(racine, "rev-parse", "--verify", "--quiet", f"{reference}^{{commit}}", verifier=False) or None


def empreinte(*textes) -> str:
    """Empreinte courte de sources, fins de ligne normalisées (identique d'un worktree à l'autre)."""
    h = hashlib.sha256()
    for texte in textes:
        h.update(texte.replace("\r\n", "\n").encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()[:10]


def empreinte_fichiers(*chemins) -> str:
    return empreinte(*(Path(c).read_text(encoding="utf-8") for c in chemins))


def lire(chemin, cle):
    """Le contenu rangé sous `chemin` si sa clé est exactement `cle`, sinon None."""
    try:
        enveloppe = json.loads(Path(chemin).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if enveloppe.get("format") != FORMAT or enveloppe.get("cle") != cle:
        return None
    return enveloppe


def ecrire(chemin, cle, contenu):
    """Écriture atomique : un lecteur concurrent voit l'ancien fichier ou le nouveau, jamais un morceau."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    provisoire = chemin.with_name(f"{chemin.name}.{os.getpid()}.tmp")
    provisoire.write_text(json.dumps({"format": FORMAT, "cle": cle, "cree": datetime.now().isoformat(timespec="seconds"),
                                      "contenu": contenu}, ensure_ascii=False), encoding="utf-8")
    os.replace(provisoire, chemin)


def taille(chemin) -> int:
    return sum(f.stat().st_size for f in Path(chemin).rglob("*") if f.is_file())


def inventaire(racine, cache):
    """Un élément par dossier de commit : commit résolu (ou None), sujet, contenu par outil."""
    elements = []
    for d in sorted(p for p in Path(cache).iterdir() if p.is_dir()) if Path(cache).exists() else []:
        commit = resoudre(racine, d.name)
        sujet = git(racine, "log", "-1", "--format=%cs %s", commit, verifier=False) if commit else None
        contenu = {o.name: sum(1 for f in o.rglob("*") if f.is_file() and f.name != "cle.json")
                   for o in sorted(d.iterdir()) if o.is_dir()}
        contenu.update({f.name: 1 for f in d.iterdir() if f.is_file()})
        elements.append({"dossier": d, "commit": commit, "sujet": sujet, "contenu": contenu, "octets": taille(d)})
    return elements


def a_purger(racine, element, branche, garder):
    """La raison de retirer ce commit, ou None pour le garder."""
    commit = element["commit"]
    if commit is None:
        return None
    if git(racine, "merge-base", "--is-ancestor", commit, branche, verifier=False) is None:
        return f"pas un ancêtre de {branche}"
    if garder is not None:
        retard = int(git(racine, "rev-list", "--count", f"{commit}..{branche}"))
        if retard > garder:
            return f"{retard} commits de retard sur {branche}"
    return None


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sous = p.add_subparsers(dest="commande", required=True)
    sous.add_parser("lister", help="commits en cache et leur contenu")
    purge = sous.add_parser("purger", help="retire les commits qui ne sont plus utiles")
    purge.add_argument("--branche", default="main")
    purge.add_argument("--garder", type=int, metavar="N", help="retire aussi ce qui a plus de N commits de retard")
    purge.add_argument("--simulation", action="store_true", help="dit ce qui serait retiré, sans rien retirer")
    args = p.parse_args(argv)
    racine = Path(git(Path.cwd(), "rev-parse", "--show-toplevel"))
    cache = dossier(racine)
    elements = inventaire(racine, cache)
    print(f"Cache : {cache}")
    if args.commande == "lister":
        if not elements:
            print("vide")
        for e in elements:
            nom = e["commit"][:10] if e["commit"] else f"{e['dossier'].name} (commit inconnu)"
            contenu = ", ".join(f"{k} {v}" for k, v in e["contenu"].items()) or "vide"
            print(f"{nom}  {e['sujet'] or ''}\n    {contenu} ; {e['octets'] / 1e6:.1f} Mo")
        return 0
    retires = 0
    for e in elements:
        if e["commit"] is None:
            print(f"gardé, commit inconnu : {e['dossier'].name}")
            continue
        raison = a_purger(racine, e, args.branche, args.garder)
        if raison:
            print(f"{'à retirer' if args.simulation else 'retiré'} : {e['commit'][:10]} ({raison})")
            if not args.simulation:
                shutil.rmtree(e["dossier"])
            retires += 1
    print(f"{retires} commit(s) {'à retirer' if args.simulation else 'retiré(s)'} sur {len(elements)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
