"""Suit les séries bornées, leurs entrées et les plans qui les terminent (sans Luna)."""
import argparse
import copy
import json
from pathlib import Path
import sys

import empreintes_nuits as empreintes


def mesurer(args):
    empreintes._preparer(args.depot, False, 0)
    from donjon import banc_pnj, planification as p
    from donjon.caractere import prix_faute
    from donjon.esprits import lire
    banc_pnj.ceder()
    if args.cout:
        return mesurer_cout(args)
    chercher, entrees = p.chercher, p._entrees
    pile, lignes, precedents, series = [], [], {}, {}
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)

    def relever(v, *a):
        r = entrees(v, *a)
        if pile:
            pile[-1]["entrees"] = [json.loads(x) for x in r]
        return r

    def observer(monde, id, *a, **k):
        courant = {"minute": monde.data["minutes"], "pnj": id, "but": k.get("nom", ""),
                   "prix": [prix_faute(monde, id, k.get("motif"), n) for n in ("honnetete", "douceur")],
                   "besoin": lire(monde, id)["besoins"].get(k.get("motif")), "entrees": None}
        pile.append(courant)
        avant = len(p.DIAGNOSTIC or [])
        try:
            r = chercher(monde, id, *a, **k)
        finally:
            pile.pop()
        if pile or p.DIAGNOSTIC is None or len(p.DIAGNOSTIC) == avant:
            return r
        courant["issue"] = p.DIAGNOSTIC[-1]["issue"]
        courant["memoire"] = p.DIAGNOSTIC[-1]["memoire"]
        cle = (id, courant["but"])
        precedent = precedents.get(cle)
        if precedent:
            courant["changements"] = [i for i, (x, y) in enumerate(zip(
                (precedent["entrees"] or [[], []])[0], (courant["entrees"] or [[], []])[0])) if x != y]
            courant["prix_change"] = precedent["prix"] != courant["prix"]
        if courant["issue"] == "borne":
            serie = series.setdefault(cle, [])
            serie.append(courant["minute"])
            if len(serie) == 1 and args.captures:
                fichier = sortie.parent / f"capture-{args.depart}-{id}-{len(lignes)}.json"
                fichier.write_text(json.dumps(monde.data, ensure_ascii=False), encoding="utf-8")
                courant["capture"] = str(fichier)
        elif cle in series:
            courant["apres_bornees"] = series.pop(cle)
        lignes.append(courant)
        precedents[cle] = courant
        return r

    p.chercher, p._entrees = observer, relever
    try:
        resume = empreintes.nuit(args.depot, args.scenario, args.graine, args.heures, args.depart)
    finally:
        p.chercher, p._entrees = chercher, entrees
    sortie.write_text(json.dumps({"resume": resume, "recherches": lignes,
        "series_finales": [[*k, v] for k, v in series.items()]}, ensure_ascii=False), encoding="utf-8")


def mesurer_cout(args):
    from donjon import banc_pnj, planification as p
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    capture = {}
    creer, nuit, chercher = banc_pnj.creer, banc_pnj.nuit, p.chercher
    bornes, plans = {}, []
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    def chercher_observe(monde, id, *a, **k):
        avant = len(p.DIAGNOSTIC or [])
        r = chercher(monde, id, *a, **k)
        if p.DIAGNOSTIC is not None and len(p.DIAGNOSTIC) > avant:
            diagnostic = p.DIAGNOSTIC[-1]
            cle = (id, k.get("nom", ""))
            if diagnostic["issue"] == "borne":
                if cle not in bornes:
                    fichier = sortie.with_name(sortie.stem + f"-borne-{len(plans)}-{len(bornes)}.json")
                    fichier.write_text(json.dumps(monde.data, ensure_ascii=False), encoding="utf-8")
                    bornes[cle] = {"minute": monde.data["minutes"], "capture": str(fichier)}
            elif r is not None and cle in bornes:
                fichier = sortie.with_name(sortie.stem + f"-plan-{len(plans)}.json")
                fichier.write_text(json.dumps(monde.data, ensure_ascii=False), encoding="utf-8")
                plans.append({"pnj": id, "but": cle[1], "premiere_borne": bornes.pop(cle),
                              "minute": monde.data["minutes"], "capture": str(fichier)})
        return r
    def creer_observe(*a, **k):
        capture["monde"] = creer(*a, **k)
        return capture["monde"]
    def nuit_observee(*a, **k):
        r = nuit(*a, **k)
        capture["donnees"] = r[2]
        return r
    banc_pnj.creer, banc_pnj.nuit, p.chercher = creer_observe, nuit_observee, chercher_observe
    try:
        resume = empreintes.nuit(args.depot, args.scenario, args.graine, args.heures, args.depart,
                                 args.verifier, args.verification)
    finally:
        banc_pnj.creer, banc_pnj.nuit, p.chercher = creer, nuit, chercher
    monde = capture["monde"]
    fichier = sortie.with_suffix(".monde.json")
    monde.sauver(fichier)
    recharge = Monde.charger(fichier)
    controle = {"monde": monde.data == recharge.data, "regarder": regarder(monde) == regarder(recharge),
                "scene": scene_percue(monde) == scene_percue(recharge)}
    assert all(controle.values()), controle
    sortie.write_text(json.dumps({"resume": resume, "recharge": controle,
        "recherches": capture["donnees"]["diagnostic"]["recherches"],
        "chronique": capture["donnees"]["chronique"], "recit": capture["donnees"]["recit"],
        "plans_apres_bornees": plans},
        ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--depot", default=".")
    a.add_argument("--sortie", required=True)
    a.add_argument("--scenario", default="auberge")
    a.add_argument("--depart", choices=("fixe", "tire"), default="fixe")
    a.add_argument("--heures", type=float, default=12)
    a.add_argument("--captures", action="store_true")
    a.add_argument("--cout", action="store_true")
    a.add_argument("--graine", type=int, default=1985)
    a.add_argument("--verifier", action="store_true")
    a.add_argument("--verification", type=float, default=0)
    mesurer(a.parse_args())
