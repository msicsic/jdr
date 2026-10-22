"""Tension d'une nuit du Relais : observation seule, sans changer le moteur ni le scénario.

Joue des nuits comme le banc (``banc_pnj.executer`` : pas de 5 minutes, joueur passif à la
galerie), en notant chaque jet (minute, auteur, fonction, valeur) et un échantillon de l'état
toutes les 5 minutes (salle, but et besoins de chaque PNJ ; vivres, bois, planches, brasero,
réserve, crochets). Le résumé mesure la divergence entre graines (nuits encore identiques à la
minute t, écart de salle entre paires de nuits), les jets, les issues et la tension.

Les variantes sont des données seules, appliquées à une copie de ``scenario_relais.json`` ;
``tirage`` simule un manque du moteur (états de départ tirés de la graine) pour le mesurer.
Détail et résultats dans ``docs/analyse-relais.md``.

    python tools/tension_relais.py jouer base.json --graines 1-32
    python tools/tension_relais.py jouer froid.json --graines 1-32 --variante froid+faims
    python tools/tension_relais.py resumer base.json froid.json
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import hashlib
import inspect
from itertools import combinations
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# --- Variantes de données -------------------------------------------------------------------

def _o(d, k):
    return d["objets"][k]


def faims(d, g):
    """Faims décalées : les crises s'étalent dans la nuit au lieu d'arriver toutes après 4 h."""
    _o(d, "ilse")["corps"]["repas"] = 660      # faim 66 : presse vers 40 min
    _o(d, "aubin")["corps"]["repas"] = 560     # 56 : vers 140 min
    _o(d, "marchand")["corps"]["repas"] = 480  # 48 : vers 220 min


def vivres3(d, g):
    """Une part de moins que de bouches."""
    _o(d, "vivres")["portions"] = 3


def froid(d, g):
    """Le brasero ne tient qu'en le nourrissant : le bois se dispute tôt, quand on est encore trempé."""
    _o(d, "brasero")["combustible"] = 45
    _o(d, "bois")["charges"] = 1


def pain_ilse(d, g):
    """Une seconde réserve, à une évacuée, sans serrure."""
    pain = dict(_o(d, "vivres"))
    pain.update(id="pain_ilse", nom="miche d'Ilse", aliases=["miche", "miche d'Ilse"], genre="f", pluriel=False,
                lieu="antichambre", position=[4, 5], position_salle="antichambre", portions=2, proprietaire="ilse",
                masse=1, materiau="pain")
    d["objets"]["pain_ilse"] = pain
    d["esprits"]["ilse"]["croyances"]["pain_ilse"] = {"lieu": {"valeur": "antichambre", "source": "savoir", "minute": 0,
                                                               "confiance": 0.9, "salle": "antichambre", "case": [4, 5]}}


def aubin_tente(d, g):
    """Aubin n'est plus au-dessus de tout soupçon (honnêteté 45)."""
    _o(d, "aubin")["profil"]["valeurs"]["honnetete"] = 45
    _o(d, "aubin")["profil"]["traits"] = _o(d, "aubin")["profil"]["traits"].replace(" et honnête", "")


def reserve_vannes(d, g):
    """La réserve dans la salle des vannes, que seules les rondes visitent."""
    _o(d, "reserve").update(lieu="crypte", position=[2, 4], position_salle="crypte")
    for e in d["esprits"].values():
        for k in ("vivres", "reserve"):
            lieu = e["croyances"].get(k, {}).get("lieu")
            if lieu:
                lieu.update(salle="crypte", case=[2, 4])
                if k == "reserve":
                    lieu["valeur"] = "crypte"


def tirage(d, g):
    """Simulation d'un manque du moteur : états de départ tirés de la graine dans des bornes (±25 %
    des minutes déclarées, ±10 sur les besoins de l'esprit), par un tirage à part, comme l'eau."""
    r = random.Random(f"{g}:depart")
    for k in ("marchand", "brune", "ilse", "aubin"):
        c = _o(d, k)["corps"]
        for e in ("repas", "veille", "trempe"):
            c[e] = max(0, round(c[e] * r.uniform(0.75, 1.25)))
        for b in _o(d, k)["profil"]["besoins"].values():
            b["depart"] = max(0, min(100, b["depart"] + r.randint(-10, 10)))


def valeurs(d, g):
    """Des valeurs moins uniformes : Gorm reste l'honnête gardien ; les évacués ont des scrupules
    gradués (honnêteté) et une douceur qui n'est plus entière."""
    for k, v in {"brune": {"douceur": 75},
                 "ilse": {"honnetete": 80, "douceur": 90},
                 "aubin": {"honnetete": 65, "douceur": 80, "fierte": 70}}.items():
        _o(d, k)["profil"]["valeurs"].update(v)


VARIANTES = {f.__name__: f for f in (faims, vivres3, froid, pain_ilse, aubin_tente, reserve_vannes, tirage, valeurs)}


# --- Une nuit observée ----------------------------------------------------------------------

def creer(graine, variante):
    from donjon import defi
    from donjon.monde import Monde
    from donjon.spatial import installer
    data = json.loads(defi.ETAT_INITIAL.read_text(encoding="utf-8"))
    for nom in filter(None, (variante or "").split("+")):
        VARIANTES[nom](data, graine)
    data["seed"] = graine
    m = Monde(data)
    installer(m)
    return m


def echantillon(m):
    from donjon.esprits import lire, pnjs
    o = m.objets
    s = {"t": m.data["minutes"]}
    for id in pnjs(m):
        if o[id].get("profil"):
            it = lire(m, id)["intention"]
            s[id] = {"lieu": o[id]["lieu"],
                     "but": (it["but"].get("type"), it["but"].get("objet") or it["but"].get("lieu")) if it else None,
                     "b": {k: round(v) for k, v in lire(m, id)["besoins"].items()}}
    for k in ("vivres", "bois", "planches"):
        if k in o:
            s[k] = (o[k]["lieu"], o[k].get("portions", o[k].get("charges")))
    for k, x in o.items():
        if x.get("foyer"):
            s[k] = (bool(x.get("allume")), round(x.get("combustible", 0)))
    s["reserve"] = (o["reserve"].get("verrouillee"), o["reserve"].get("ouverte"))
    s["crochets"] = o["crochets"]["lieu"]
    return s


def nuit(args):
    graine, heures, variante = args
    from donjon import banc_pnj
    from donjon.geometrie import position_entree
    from donjon.monde import Monde
    from donjon.recit_pnj import Recit
    m = creer(graine, variante)
    m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
    jets, ech = [], [echantillon(m)]
    d20, verifier = Monde.d20, Monde.verifier

    def jet(self):
        v = d20(self)
        pile = inspect.stack()[1:6]
        acteur = next((f.frame.f_locals[n] for f in pile for n in ("locuteur", "demandeur", "id", "auteur")
                       if isinstance(f.frame.f_locals.get(n), str)), None)
        jets.append({"t": self.data["minutes"], "v": v, "fonction": pile[0].function, "acteur": acteur})
        return v

    def verifier_et_noter(self, *a, **k):
        r = verifier(self, *a, **k)
        if self is m:
            ech.append(echantillon(self))
        return r
    Monde.d20, Monde.verifier = jet, verifier_et_noter
    try:
        recit = Recit(m)
        chronique, mesures = banc_pnj.executer(m, int(heures * 60), recit)
    finally:
        Monde.d20, Monde.verifier = d20, verifier
    return {"graine": graine, "jets": jets, "echantillons": ech, "chronique": chronique, "mesures": mesures,
            "recit": recit.donnees(m, chronique)}


# --- Résumé -----------------------------------------------------------------------------------

def _h(o):
    return hashlib.md5(repr(o).encode()).hexdigest()


def _illicites(x):
    """Réserve crochetée, ou planches d'Aubin aux mains d'un autre que lui."""
    planches = {s["planches"][0] for s in x["echantillons"] if s.get("planches")} - {"antichambre", "aubin"}
    return (sum("crochète la serrure" in c["texte"] for c in x["chronique"])
            + len(planches & {k for k, v in x["echantillons"][0].items() if isinstance(v, dict)}))


def _repas(x):
    c = Counter()
    for e in x["chronique"]:
        t = e["texte"]
        if "mange " in t and "part" in t:
            c[t.split(",")[0].split(" ")[0]] += 1
        if "lui donne une part" in t:
            c[t.split("appelle ")[1].split(" ")[0]] += 1
    return tuple(sorted(c.items()))


def resume(d):
    n = len(d)
    pnj = [k for k, v in d[0]["echantillons"][0].items() if isinstance(v, dict)]
    out = {"nuits": n}
    for t in (60, 120, 240, 480):
        out[f"distinctes@{t}"] = len({_h([(c["minute"], c["texte"]) for c in x["chronique"] if c["minute"] <= t])
                                      for x in d})
    ech = [{s["t"]: s for s in x["echantillons"]} for x in d]
    paires = list(combinations(range(n), 2))
    for t in (120, 240, 360, 480):
        out[f"salle_diff@{t}"] = round(sum(sum(ech[a][t][p]["lieu"] != ech[b][t][p]["lieu"] for p in pnj) / len(pnj)
                                       for a, b in paires) / len(paires), 2)
    out["jets"] = round(sum(len(x["jets"]) for x in d) / n, 1)
    out["jets<120"] = round(sum(sum(j["t"] < 120 for j in x["jets"]) for x in d) / n, 1)
    out["issues"] = len({(_repas(x), _illicites(x) > 0) for x in d})
    out["nuits_illicites"] = round(sum(_illicites(x) > 0 for x in d) / n, 2)
    moy = lambda k: round(sum(x["mesures"].get(k, 0) for x in d) / n, 2)
    out["mefiances"] = moy("mefiances")
    out["demandes"] = round(sum(sum(" demande " in c["texte"] and c.get("nature") == "social" for c in x["chronique"])
                                for x in d) / n, 2)
    out["rumeurs"] = moy("rumeurs_crues")
    out["evenements"] = moy("evenements_distincts")
    out["sans_recours"] = moy("minutes_urgentes_sans_recours")
    out["sans_recours_hors_gorm"] = round(sum(sum(v for k, v in x["recit"]["sans_recours"].items() if k != "marchand")
                                              for x in d) / n)
    out["faim>=95_min"] = round(sum(5 for x in d for s in x["echantillons"] for p in pnj if s[p]["b"].get("faim", 0) >= 95) / n)
    out["froid>=70_min"] = round(sum(5 for x in d for s in x["echantillons"] for p in pnj if s[p]["b"].get("chaleur", 0) >= 70) / n)
    out["feu_eteint_min"] = round(sum(5 for x in d for s in x["echantillons"][1:] if not s["brasero"][0]) / n)
    return out


def graines(textes):
    res = []
    for t in textes:
        a, _, b = t.partition("-")
        res += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return res


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sous = p.add_subparsers(dest="commande", required=True)
    j = sous.add_parser("jouer")
    j.add_argument("sortie")
    j.add_argument("--graines", nargs="+", default=["1-32"])
    j.add_argument("--heures", type=float, default=8)
    j.add_argument("--variante", default="", help="noms joints par + : " + ", ".join(VARIANTES))
    r = sous.add_parser("resumer")
    r.add_argument("fichiers", nargs="+")
    a = p.parse_args(argv)
    if a.commande == "jouer":
        liste = graines(a.graines)
        with ProcessPoolExecutor(max_workers=min(len(liste), 12)) as pool:
            res = list(pool.map(nuit, [(g, a.heures, a.variante) for g in liste]))
        Path(a.sortie).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(resume(res), ensure_ascii=False))
        return 0
    lignes = [resume(json.loads(Path(f).read_text(encoding="utf-8"))) for f in a.fichiers]
    print(f'{"":24}' + "".join(f"{Path(f).stem[:14]:>15}" for f in a.fichiers))
    for k in lignes[0]:
        print(f"{k:24}" + "".join(f"{str(x[k]):>15}" for x in lignes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
