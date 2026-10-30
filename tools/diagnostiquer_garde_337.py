"""Rejeu unique crue/7 : captures des choix et clôtures autour du suspect 219.

Observation seule ; nuit brute, épisodes et mondes conservés. Fin écrite en
dernier, succès ou échec. Aucun banc de référence ni appel au modèle.
"""
from pathlib import Path
from unittest.mock import patch
import argparse
import copy
import gzip
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
from donjon import appel, deliberation
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import instant


def ecrire(chemin, valeur):
    chemin.write_text(json.dumps(valeur, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    sortie = args.sortie.resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    ceder()
    debut = time.monotonic()
    fin = dict(ok=False, pid=os.getpid())
    try:
        fichiers = [*sorted((RACINE / "donjon").glob("*.py")),
                    RACINE / "tools/detecter_changements_avis.py", Path(__file__).resolve()]
        ecrire(sortie / "debut.json", dict(pid=os.getpid(), commit=banc.git(RACINE, "rev-parse", "HEAD"),
            empreintes={str(p.relative_to(RACINE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers}))
        detecteur = banc.audit.detecteur_avis()
        choisir, retrouves, analyser = deliberation.choisir, appel.retrouves, detecteur.SondeAvis.analyser
        captures, evenements, episodes = [], [], {}

        def capturer(m, nature, **details):
            if 69000 <= instant(m) <= 71000:
                nom = f"{len(captures):03d}-{instant(m)}-{nature}"
                captures.append((nom, m.copier()))
                evenements.append(dict(capture=nom, t=instant(m), nature=nature, **copy.deepcopy(details)))

        def choix(m, id, minute):
            if id == "marchand":
                capturer(m, "choix-avant", intention=lire(m, id)["intention"])
            retour = choisir(m, id, minute)
            if id == "marchand":
                capturer(m, "choix-apres", intention=lire(m, id)["intention"])
            return retour

        def cloture(m, id, qui):
            def etat():
                return {x: {k: copy.deepcopy(lire(m, x).get(k))
                            for k in ("rejoint", "rejoindre", "intention")}
                        for x in (id, qui) if x != "joueur"}
            avant = etat()
            capturer(m, "retrouves-avant", id=id, qui=qui, etat=avant)
            retour = retrouves(m, id, qui)
            capturer(m, "retrouves-apres", id=id, qui=qui, etat=etat(), avant=avant)
            return retour

        def analyse(sonde):
            episodes.update(copy.deepcopy(sonde.episodes))
            return analyser(sonde)

        config = dict(heures=4., depart="tire", verifier=False, empreintes=False, joueurs=dict(banc.JOUEURS))
        with patch.object(deliberation, "choisir", choix), patch.object(appel, "retrouves", cloture), \
                patch.object(detecteur.SondeAvis, "analyser", analyse):
            nuit = banc.jouer_nuit(("crue", 7, config))
        ecrire(sortie / "nuit.json", nuit)
        with gzip.open(sortie / "episodes.json.gz", "wt", encoding="utf-8") as flux:
            json.dump(episodes, flux, ensure_ascii=False)
        controles = []
        for nom, m in captures:
            chemin = sortie / (nom + ".json")
            avant = copy.deepcopy(m.data)
            vue = regarder(m), scene_percue(m)
            m.sauver(chemin)
            recharge = Monde.charger(chemin)
            controles.append(dict(capture=nom, monde=avant == recharge.data,
                                   rendu=vue[0] == regarder(recharge), scene=vue[1] == scene_percue(recharge)))
        ecrire(sortie / "evenements.json", evenements)
        ecrire(sortie / "recharges.json", controles)
        ancienne = json.loads((sortie.parent / "banc-final/banc.json").read_text(encoding="utf-8"))
        originale = next(n for n in ancienne["nuits_branche"] if n["scenario"] == "crue" and n["graine"] == 7)
        identites = {k: nuit["donnees"][k] == originale["donnees"][k]
                     for k in ("chronique", "recit", "souvenirs")}
        ecrire(sortie / "comparaison-historique.json", identites)
        fin.update(plantage=nuit["plantage"], suspects=nuit["avis"]["total_non_justifies"],
                   captures=len(captures), recharges_ok=all(all(c[k] for k in ("monde", "rendu", "scene")) for c in controles),
                   trajectoire_historique=identites)
        fin["ok"] = nuit["plantage"] is None and fin["recharges_ok"] and bool(captures)
        return int(not fin["ok"])
    except BaseException:
        fin["erreur"] = traceback.format_exc()
        return 1
    finally:
        fin["secondes"] = time.monotonic() - debut
        ecrire(sortie / "fin.json", fin)


if __name__ == "__main__":
    raise SystemExit(main())
