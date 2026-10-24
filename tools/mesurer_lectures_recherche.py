"""Diagnostic du lot 63, jamais une clé de cache du moteur.

  python tools/mesurer_lectures_recherche.py --scenario mine --depart tire --sortie artifacts/lectures/mine.json
  python tools/mesurer_lectures_recherche.py --scenario auberge --depart fixe --sortie artifacts/lectures/auberge.json

Observe les recherches neuves d'un PNJ/but après --depuis (480 par défaut).
Les dictionnaires lus pendant _explorer sont enveloppés sans modifier les données.
Les listes/ensembles sont relevés en entier : sur-approximation volontaire.
Les caches préparés avant _explorer, ses arguments scalaires (dont faute), les
lectures natives de dict et les alias empêchent une preuve de couverture.
Aucune reprise n'est autorisée
par cet outil ; « inchangé observé » ne signifie PAS « recherche réutilisable ».
Les CPU incluent l'instrumentation et ne mesurent aucun gain.
"""
import argparse
import ast
from collections import Counter
from collections.abc import ItemsView, KeysView, ValuesView
from contextlib import contextmanager
import copy
import inspect
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj, planification as p
from donjon.monde import Monde


def figer(x):
    """Valeur détachée, ordre des dictionnaires conservé (départage des plans)."""
    if isinstance(x, dict):
        return ("dict", tuple((figer(k), figer(v)) for k, v in dict.items(x)))
    if isinstance(x, (tuple, list)):
        return (type(x).__name__, tuple(figer(v) for v in x))
    if isinstance(x, (set, frozenset)):
        return ("ensemble", tuple(sorted((figer(v) for v in x), key=repr)))
    return x


class DictionnaireLu(dict):
    """Vue de diagnostic ; les écritures sont refusées au lieu d'être perdues."""
    def __init__(self, source, trace, chemin):
        dict.__init__(self, source)
        self.trace, self.chemin = trace, chemin

    def __getitem__(self, cle):
        present = dict.__contains__(self, cle)
        self.trace.noter("present", self.chemin, present, cle)
        valeur = dict.__getitem__(self, cle)
        return self.trace.envelopper(valeur, (*self.chemin, cle))

    def get(self, cle, defaut=None):
        return self[cle] if cle in self else defaut

    def __contains__(self, cle):
        present = dict.__contains__(self, cle)
        self.trace.noter("present", self.chemin, present, cle)
        return present

    def __iter__(self):
        self.trace.noter("cles", self.chemin, tuple(dict.keys(self)))
        return dict.__iter__(self)

    def __len__(self):
        n = dict.__len__(self)
        self.trace.noter("longueur", self.chemin, n)
        return n

    def keys(self):
        return KeysView(self)

    def items(self):
        return ItemsView(self)

    def values(self):
        return ValuesView(self)

    def copy(self):
        self.trace.noter("valeur", self.chemin, self)
        return dict.copy(self)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        # Une table du moteur peut retenir une lecture, puis être copiée avec
        # le monde. Ne jamais copier l'observateur ou réinstaller ses proxies.
        self.trace.noter("valeur", self.chemin, self)
        return copy.deepcopy(dict.copy(self), memo)

    def __eq__(self, autre):
        self.trace.noter("valeur", self.chemin, self)
        return dict.__eq__(self, autre)

    def __ne__(self, autre):
        return not self == autre

    def __repr__(self):
        self.trace.noter("valeur", self.chemin, self)
        return dict.__repr__(self)

    def _interdire(self, *a, **k):
        raise RuntimeError("Écriture pendant la trace de lecture : " + repr(self.chemin))

    __setitem__ = __delitem__ = update = pop = popitem = clear = setdefault = __ior__ = _interdire


class Trace:
    def __init__(self, vue):
        self.vue = vue
        self.monde = object.__getattribute__(vue, "monde")
        self.spatial = object.__getattribute__(vue, "_cru_spatial")
        # Les attributs privés sont des mémoires calculées, pas des entrées.
        # Leurs dépendances antérieures restent une lacune explicite du diagnostic.
        self.champs = {k for k, v in vars(vue).items()
                       if not k.startswith("_") and k not in ("monde", "refus_routes") and not callable(v)}
        self.racines = {"vue": {k: object.__getattribute__(vue, k) for k in self.champs},
                        "monde": object.__getattribute__(self.monde, "data")}
        if self.spatial is not None:
            self.racines["spatial"] = object.__getattribute__(self.spatial, "data")
        self.lectures, self.proxies = {}, {}
        self.active = True

    def noter(self, sorte, chemin, valeur, cle=None):
        if not self.active:
            return
        identifiant = (sorte, chemin, cle)
        if identifiant not in self.lectures:
            self.lectures[identifiant] = figer(valeur)

    def envelopper(self, valeur, chemin):
        if isinstance(valeur, dict):
            if chemin not in self.proxies:
                self.proxies[chemin] = DictionnaireLu(valeur, self, chemin)
            return self.proxies[chemin]
        # Rien n'est substitué aux listes/tuples/ensembles, pour garder notamment
        # isinstance, concaténation et consommation par les fonctions natives.
        self.noter("valeur", chemin, valeur)
        return valeur

    def changements(self, precedente):
        changements = []
        for (sorte, chemin, cle), avant in precedente.lectures.items():
            try:
                x = self.racines
                for k in chemin:
                    x = x[k]
                apres = (cle in x if sorte == "present" else tuple(x) if sorte == "cles"
                         else len(x) if sorte == "longueur" else x)
                different = figer(apres) != avant
            except (KeyError, TypeError, IndexError):
                different = True
            if different:
                changements.append({"operation": sorte, "chemin": list(chemin), "cle": cle})
        return changements


@contextmanager
def tracer(trace):
    """Portée limitée à une exploration ; aucune installation durable dans Monde."""
    lire_vue, lire_monde = p.Vue.__getattribute__, Monde.__getattribute__

    def vue(self, nom):
        valeur = lire_vue(self, nom)
        if self is trace.vue and nom in trace.champs:
            # objets/salles sont aussi lus directement par les helpers du monde.
            chemin = (("monde", "objets") if nom == "objets" else
                      ("monde", "salles") if nom == "salles" else ("vue", nom))
            return trace.envelopper(valeur, chemin)
        return valeur

    def monde(self, nom):
        valeur = lire_monde(self, nom)
        racine = "monde" if self is trace.monde else "spatial" if self is trace.spatial else None
        if racine and nom in ("data", "objets", "joueur"):
            return trace.envelopper(valeur, (racine,) if nom == "data" else (racine, nom))
        return valeur

    with patch.object(p.Vue, "__getattribute__", vue), patch.object(Monde, "__getattribute__", monde):
        try:
            yield trace
        finally:
            trace.active = False


def composants_entrees():
    """Libellés extraits de l'expression réelle, pas une seconde liste de dépendances."""
    source = inspect.getsource(p._entrees)
    retour = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Return))
    return [" ".join(ast.get_source_segment(source, n).split()) for n in retour.value.args[0].elts]


def ecarts_entrees(avant, apres):
    if len(avant) != len(apres):
        raise RuntimeError("Structure de _entrees modifiée")
    return [i for i, (a, b) in enumerate(zip(avant, apres)) if a != b]


@contextmanager
def observer(qui, but, depuis, releves):
    chercher, entrees, explorer = p.chercher, p._entrees, p._explorer
    pile, derniere = [], None

    def appeler(*a, **k):
        nonlocal derniere
        cible = not pile and a[1] == qui and k.get("nom") == but and a[0].data["minutes"] >= depuis
        contexte = {"cible": cible}
        pile.append(contexte)
        try:
            resultat = chercher(*a, **k)
            if cible and "trace" in contexte:
                t = contexte["trace"]
                d = p.DIAGNOSTIC[-1]
                r = {"minute": a[0].data["minutes"], "noeuds": d["noeuds"], "issue": d["issue"],
                     "graphe": d["graphe"], "lectures": len(t.lectures),
                     "reutilisable_prouve": False,
                     "comparaison": None}
                if derniere is not None:
                    ancien, ancienne_cle, ancien_resultat = derniere
                    changements = t.changements(ancien)
                    r["comparaison"] = {"meme_resultat": resultat == ancien_resultat,
                                         "entrees_changees": ecarts_entrees(ancienne_cle, contexte["entrees"]),
                                         "lectures_changees": changements,
                                         "inchange_observe": not changements}
                r["chemins_lus"] = [{"operation": op, "chemin": list(ch), "cle": cle}
                                    for op, ch, cle in t.lectures]
                releves.append(r)
                derniere = (t, contexte["entrees"], resultat)
            return resultat
        finally:
            pile.pop()

    def cle(*a, **k):
        valeur = entrees(*a, **k)
        if pile and pile[-1]["cible"]:
            pile[-1]["entrees"] = json.loads(valeur)
        return valeur

    def exploration(v, *a, **k):
        if not pile or not pile[-1]["cible"]:
            return explorer(v, *a, **k)
        t = Trace(v)
        pile[-1]["trace"] = t
        with tracer(t):
            return explorer(v, *a, **k)

    with patch.object(p, "chercher", appeler), patch.object(p, "_entrees", cle), \
            patch.object(p, "_explorer", exploration):
        yield


def resumer(releves):
    comparables = [r for r in releves if r["comparaison"] is not None]
    identiques = [r for r in comparables if r["comparaison"]["meme_resultat"]]
    inchangees = [r for r in identiques if r["comparaison"]["inchange_observe"]]
    composantes, chemins = Counter(), Counter()
    for r in identiques:
        composantes.update(r["comparaison"]["entrees_changees"])
        chemins.update("/".join(map(str, c["chemin"])) for c in r["comparaison"]["lectures_changees"])
    return {"neuves_observees": len(releves), "paires": len(comparables), "meme_resultat": len(identiques),
            "issues": dict(Counter(r["issue"] for r in releves)), "noeuds": sum(r["noeuds"] for r in releves),
            "sans_changement_observe": len(inchangees),
            "fraction_sans_changement_observe": len(inchangees) / len(identiques) if identiques else None,
            "epuisees_sans_changement_observe": sum(r["issue"] == "epuise" for r in inchangees),
            "bornees_sans_changement_observe": sum(r["issue"] == "borne" for r in inchangees),
            "reprises_sures_hors_cle_actuelle": 0,
            "composantes_changees": dict(composantes), "lectures_changees": dict(chemins.most_common())}


def mesurer(args):
    releves = []
    qui = args.pnj or ("remy" if args.scenario == "mine" else "joss")
    debut = time.process_time()
    with observer(qui, args.but, args.depuis, releves):
        _, mesures, donnees = banc_pnj.nuit(args.scenario, args.graine, args.heures,
                                           "galerie" if args.scenario == "mine" else "dortoir",
                                           diagnostic=True, depart=args.depart)
    resultat = {"scenario": args.scenario, "graine": args.graine, "depart": args.depart,
                "heures": args.heures, "depuis": args.depuis, "pnj": qui, "but": args.but,
                "couverture_complete": False,
                "limites": ["caches de Vue préparés avant exploration", "arguments scalaires dont faute",
                            "lectures natives de dict",
                            "alias et caches partagés hors enveloppe", "listes et ensembles relevés en entier"],
                "cpu_instrumente": time.process_time() - debut, "composantes": composants_entrees(),
                "mesures": mesures, "recherches": donnees["diagnostic"]["recherches"],
                "releves": releves, "resume": resumer(releves)}
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resultat["resume"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("mine", "auberge"), required=True)
    parser.add_argument("--depart", choices=("tire", "fixe"), required=True)
    parser.add_argument("--graine", type=int, default=1985)
    parser.add_argument("--heures", type=float, default=12)
    parser.add_argument("--depuis", type=int, default=480)
    parser.add_argument("--pnj")
    parser.add_argument("--but", default="faim")
    parser.add_argument("--sortie", required=True)
    from tools.priorite import ceder
    ceder()
    mesurer(parser.parse_args())
