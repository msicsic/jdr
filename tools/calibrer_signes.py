"""Corpus de nuits réelles puis grille commune des paramètres de lecture.

Les jets enregistrés sont rejugés sans rejouer les décisions : c'est une mesure
conditionnelle au corpus. ``jouer`` confirme ensuite une configuration en nuits
libres. Aucun accès aux sauvegardes de partie et aucun appel à un modèle.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import itertools
import hashlib
import json
from pathlib import Path
import sys

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from tools.priorite import ceder

JOUEURS = {"relais": "chambre_cloche", "mine": "galerie", "auberge": "dortoir", "crue": "chambre_cloche"}


def nuit(tache):
    from donjon import banc_pnj, signes
    scenario, graine, lecteur, psy, parametres = tache
    source = hashlib.sha256(Path(signes.__file__).read_bytes()).hexdigest()
    code = hashlib.sha256(b"".join(p.read_bytes() for p in sorted((RACINE / "donjon").glob("*.py")))).hexdigest()
    ceder()
    signes.PENOMBRE, signes.DISSIMULATION, signes.BANDE_RIEN = parametres
    preuves = []
    calcul = signes.interpreter

    def interpreter(s, jet, bonus, dd):
        resultat = calcul(s, jet, bonus, dd)
        preuves.append({"signe": s, "jet": jet, "bonus": bonus, "dd": dd,
                        "lecture": resultat[0], "marge": resultat[1]})
        return resultat

    # L'observateur et sa PSY sont établis au seul moment où le dé est demandé.
    jet = signes._jet
    courant = {}

    def tirer(m, observateur="joueur"):
        from donjon.caractere import caracteristique
        courant.update(observateur=observateur, psy=caracteristique(m, observateur, "PSY"), minute=m.data["minutes"])
        return jet(m, observateur)

    def enregistrer(s, j, bonus, dd):
        resultat = interpreter(s, j, bonus, dd)
        preuves[-1].update(courant)
        return resultat

    signes.interpreter, signes._jet = enregistrer, tirer
    try:
        _, mesures, donnees = banc_pnj.nuit(scenario, graine, 8, JOUEURS[scenario],
                                           reglages=[f"{lecteur}.PSY={psy}"] if lecteur else ())
    finally:
        signes.interpreter, signes._jet = calcul, jet
    return {"scenario": scenario, "graine": graine, "lecteur": lecteur, "psy": psy,
            "code_signes": source,
            "code_moteur": code,
            "parametres": parametres, "mesures": mesures, "preuves": preuves,
            "chronique": donnees["chronique"]}


def bilan(preuves):
    groupes = defaultdict(Counter)
    groupes["total"]
    for p in preuves:
        sorte = p["signe"]["sorte"] if "sorte" in p["signe"] else None
        if sorte is None:
            from donjon.signes import SIGNES
            sorte = SIGNES[p["signe"]["signe"]][0]
        tranche = "basse" if p["psy"] <= 9 else "haute" if p["psy"] >= 13 else "moyenne"
        for cle in ("total", tranche, "sorte:" + sorte, tranche + ":" + sorte):
            c = groupes[cle]
            c["essais"] += 1
            c["rien"] += p["lecture"] is None
            c["justes"] += p["marge"] >= 0
            c["meprises"] += p["lecture"] is not None and p["marge"] < 0
    resultat = {}
    for k, c in groupes.items():
        n = c["justes"] + c["meprises"]
        resultat[k] = {**{x: c[x] for x in ("essais", "rien", "justes", "meprises")},
                       "lectures": n, "justesse": c["justes"] / n if n else None,
                       "part_meprises": c["meprises"] / n if n else None,
                       "abstention": c["rien"] / c["essais"] if c["essais"] else None}
    return resultat


def grille(nuits):
    from donjon.signes import SIGNES
    resultats = []
    for penombre, dissimulation, bande in itertools.product((4, 3, 2), (5, 4, 3), range(5, 12)):
        groupes = defaultdict(list)
        for n in nuits:
            origine_p, origine_d, _ = n["parametres"]
            for p in n["preuves"]:
                s = p["signe"]
                marge = (p["marge"] + (origine_p - penombre if s["niveau"] == 1 else 0)
                         + (origine_d - dissimulation if s["dissimule"] else 0))
                sens = (s["vrai"] if marge >= 0 else None if marge >= -bande else "fatigue"
                        if s["dissimule"] else next(x for x in SIGNES[s["signe"]][5] if x != s["vrai"]))
                preuve = {**p, "marge": marge, "lecture": sens}
                if n["lecteur"]:
                    if p["observateur"] == n["lecteur"]:
                        groupes[f'{n["scenario"]}:{n["psy"]}'].append(preuve)
                        groupes["regles"].append(preuve)
                else:
                    groupes["defaut"].append(preuve)
        resultats.append({"parametres": [penombre, dissimulation, bande],
                          "groupes": {k: bilan(v) for k, v in groupes.items()}})
    return resultats


def groupes_nuits(nuits):
    groupes = defaultdict(list)
    for n in nuits:
        if n["lecteur"]:
            preuves = [p for p in n["preuves"] if p["observateur"] == n["lecteur"]]
            groupes[f'{n["scenario"]}:{n["psy"]}'].extend(preuves)
            groupes["regles"].extend(preuves)
        else:
            groupes["defaut"].extend(n["preuves"])
            groupes["defaut:" + n["scenario"]].extend(n["preuves"])
    return {k: bilan(v) for k, v in groupes.items()}


def jouer_configuration(parametres, processus, sortie):
    taches = [(s, g, None, None, parametres) for s in JOUEURS for g in (1985, 7, 42, 2024)]
    taches += [(s, g, l, psy, parametres) for s, l in (("relais", "marchand"), ("auberge", "hugues"))
               for psy in (8, 11, 14, 16) for g in (1985, 7, 42, 2024)]
    def cle(n):
        return n["scenario"], n["graine"], n["lecteur"], n["psy"]
    anciens = json.loads(sortie.read_text(encoding="utf-8")) if sortie.exists() else []
    assert all(tuple(n["parametres"]) == tuple(parametres) for n in anciens), "Reprise d'un autre réglage"
    gardes = {cle(n): n for n in anciens}
    manquantes = [t for t in taches if t[:4] not in gardes]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=max(1, min(3, processus)), max_tasks_per_child=1) as pool:
        for r in pool.map(nuit, manquantes):
            gardes[cle(r)] = r
            resultat = [gardes[t[:4]] for t in taches if t[:4] in gardes]
            sortie.write_text(json.dumps(resultat, ensure_ascii=False), encoding="utf-8")
            print(parametres, r["scenario"], r["graine"], r["lecteur"], r["psy"],
                  f'{len(gardes)}/48', flush=True)
    return [gardes[t[:4]] for t in taches]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("jouer", "grille", "balayer"))
    p.add_argument("--sortie", type=Path, required=True)
    p.add_argument("--corpus", type=Path)
    p.add_argument("--parametres", type=int, nargs=3, default=(4, 5, 5))
    p.add_argument("--processus", type=int, default=3)
    args = p.parse_args()
    if args.mode == "grille":
        resultat = grille(json.loads(args.corpus.read_text(encoding="utf-8")))
    elif args.mode == "balayer":
        resultat = []
        for parametres in itertools.product((4, 3, 2), (5, 4, 3), (5, 8)):
            fichier = args.sortie.parent / "nuits-grille" / ("-".join(map(str, parametres)) + ".json")
            nuits = jouer_configuration(parametres, args.processus, fichier)
            resultat.append({"parametres": parametres, "groupes": groupes_nuits(nuits)})
            args.sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")
            print("CONFIGURATION TERMINEE", parametres, flush=True)
    else:
        resultat = jouer_configuration(args.parametres, args.processus, args.sortie)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
