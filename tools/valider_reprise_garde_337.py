"""Reprise 337 après fusion : ciblés 336/337 et preuve du retour 219 capturé.

Aucune nuit relancée : la clôture est rejouée sur les captures du rejeu
unique crue/7, puis ses faits sont lus par le classificateur commun.
Deux travailleurs réduits au plus ; fin.json écrite en dernier sur tout échec.
"""
from pathlib import Path
import copy
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
import argparse

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from priorite import ceder
import comparer_bancs as banc
from valider_garde_337 import TESTS as TESTS_337
from valider_occasion_336 import TESTS as TESTS_336
from donjon import appel
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue

TESTS = tuple(dict.fromkeys((*TESTS_337, *TESTS_336, "detecter_changements_avis")))


def ecrire(chemin, valeur):
    chemin.write_text(json.dumps(valeur, ensure_ascii=False, indent=2), encoding="utf-8")


def classer(sortie, source):
    detecteur = banc.audit.detecteur_avis()
    with gzip.open(source / "episodes.json.gz", "rt", encoding="utf-8") as flux:
        episodes = json.load(flux)
    brut = detecteur.analyser_episodes(copy.deepcopy(episodes))
    evenements = json.loads((source / "evenements.json").read_text(encoding="utf-8"))
    preuves, controles = [], []
    for index, event in enumerate(evenements):
        if event["nature"] != "retrouves-avant":
            continue
        apres = next(e for e in evenements[index + 1:] if e["nature"] == "retrouves-apres"
                     and all(e[k] == event[k] for k in ("t", "id", "qui")))
        m = Monde.charger(source / (event["capture"] + ".json"))
        attendu = Monde.charger(source / (apres["capture"] + ".json"))
        prefixes, indices = {}, {}
        for id, eps in episodes.items():
            cle = detecteur._cle_decision(lire(m, id)["intention"])
            candidats = [i for i, ep in enumerate(eps) if ep["debut_t"] <= event["t"]
                         and ep["decision"]["cle"] == cle
                         and (ep.get("quitte_t") is None or ep["quitte_t"] >= event["t"])]
            if candidats:
                indices[id] = i = candidats[-1]
                prefixes[id] = copy.deepcopy(eps[:i + 1])
        avant = {id: copy.deepcopy(eps[-1].get("faits", [])) for id, eps in prefixes.items()}
        with detecteur.observer_avis() as sonde:
            sonde.episodes = prefixes
            sonde.relever_services(m)
            appel.retrouves(m, event["id"], event["qui"])
        for id, eps in prefixes.items():
            nouveaux = [f for f in eps[-1].get("faits", []) if f not in avant[id]]
            for f in nouveaux:
                episodes[id][indices[id]].setdefault("faits", []).append(copy.deepcopy(f))
                preuves.append(dict(id=id, episode_debut=eps[-1]["debut_t"], fait=f,
                                    avant=event["capture"], apres=apres["capture"]))
        controle = dict(capture=event["capture"], monde=m.data == attendu.data,
                        rendu=regarder(m) == regarder(attendu), scene=scene_percue(m) == scene_percue(attendu))
        controles.append(controle)
    corrige = detecteur.analyser_episodes(episodes)
    ecrire(sortie / "audit-corrige.json", corrige)
    with gzip.open(sortie / "episodes-certifies.json.gz", "wt", encoding="utf-8") as flux:
        json.dump(episodes, flux, ensure_ascii=False)
    cible = [e for e in corrige["allers_retours"] if e["debut_t"] == 69945 and e["retour_t"] == 70426]
    resultat = dict(suspects_bruts=brut["total_non_justifies"], suspects_certifies=corrige["total_non_justifies"],
                    cible=cible, preuves=preuves, controles=controles,
                    qualification="reprise légitime après clôture publiée du contact préparatoire, consommé par le plan repris")
    resultat["ok"] = bool(cible) and not cible[0]["non_justifie"] and bool(preuves) and bool(controles) \
        and all(all(c[k] for k in ("monde", "rendu", "scene")) for c in controles)
    ecrire(sortie / "classification.json", resultat)
    return resultat["ok"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, required=True)
    parser.add_argument("--captures", type=Path, required=True)
    args = parser.parse_args()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    ceder()
    debut = time.monotonic()
    fin = dict(ok=False, pid=os.getpid())
    try:
        fichiers = [*sorted((RACINE / "donjon").glob("*.py")), RACINE / "tests/support.py",
                    RACINE / "tools/detecter_changements_avis.py", Path(__file__).resolve(),
                    *[RACINE / f"tests/test_{nom}.py" for nom in TESTS]]
        ecrire(sortie / "debut.json", dict(pid=os.getpid(), commit=banc.git(RACINE, "rev-parse", "HEAD"),
            integration=banc.git(RACINE, "rev-parse", "8ddef70^2"), tests=TESTS,
            empreintes={str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers}))
        fin["classification_ok"] = classer(sortie, args.captures.resolve())
        commande = [sys.executable, "tools/tests.py", "--processus", "2", "--sortie", str(sortie / "tests.json"),
                    *[f"tests/test_{nom}.py" for nom in TESTS]]
        with (sortie / "tests.log").open("w", encoding="utf-8") as flux:
            fin["tests_code"] = subprocess.run(commande, cwd=RACINE, stdout=flux,
                                               stderr=subprocess.STDOUT, check=False).returncode
        fin["ok"] = fin["classification_ok"] and fin["tests_code"] == 0
        return int(not fin["ok"])
    except BaseException:
        fin["erreur"] = traceback.format_exc()
        return 1
    finally:
        fin["secondes"] = time.monotonic() - debut
        ecrire(sortie / "fin.json", fin)


if __name__ == "__main__":
    raise SystemExit(main())
