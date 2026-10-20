"""Compare les méthodes de plan écrites et le planificateur par recherche, sans rien changer.

    python tools/comparer_planificateurs.py --graines 1985 7 42 2024
    python tools/comparer_planificateurs.py --suite

Au banc sans joueur, à chaque délibération d'un PNJ pressé par la faim ou le froid, les deux
calculent un plan sur le même état ; avec ``--suite``, la comparaison se fait à chaque appel
d'une méthode pendant la suite de tests. Les méthodes décident toujours ; seuls les désaccords
et les temps de calcul sont rapportés.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time
import traceback
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from donjon import deliberation  # noqa: E402
from donjon.planification import planifier  # noqa: E402

METHODES = {"faim": "_plan_manger", "chaleur": "_plan_chauffer"}


def resume(resultat):
    if not resultat:
        return None
    but, etapes = resultat
    return json.dumps(but, sort_keys=True), [
        (x["operation"], x["cible"], x["outil"], x["lieu"], x["condition"], json.dumps(x.get("contenu"), sort_keys=True))
        for x in etapes]


class Comparaison:
    def __init__(self):
        self.accords, self.ecarts, self.temps = Counter(), {}, Counter()

    def comparer(self, monde, id, besoin, methode, origine):
        t = time.perf_counter()
        a = resume(methode(monde, id))
        self.temps["méthodes"] += time.perf_counter() - t
        t = time.perf_counter()
        b = resume(planifier(monde, id, besoin))
        self.temps["planificateur"] += time.perf_counter() - t
        self.accords[besoin, a == b] += 1
        if a != b:
            self.ecarts.setdefault((besoin, str(a), str(b)), (id, origine))

    def rapport(self):
        lignes = [", ".join(f"{b} {'accord' if ok else 'écart'} {n}" for (b, ok), n in sorted(self.accords.items())),
                  ", ".join(f"{k} {v:.2f} s" for k, v in self.temps.items())]
        for (besoin, a, b), (id, origine) in self.ecarts.items():
            lignes += [f"--- {besoin}, {id}, {origine}", f"  méthode : {a}", f"  planif. : {b}"]
        return "\n".join(lignes)


def au_banc(graine, heures, c):
    from donjon.banc_pnj import creer, executer
    from donjon.geometrie import position_entree
    monde = creer("relais", graine)
    monde.joueur.update(salle="chambre_cloche", position=list(position_entree(monde, "chambre_cloche")))
    originale = deliberation.deliberer

    def deliberer(m, id, minute):
        for besoin, nom in METHODES.items():
            if besoin in deliberation.urgents(m, id):
                c.comparer(m, id, besoin, getattr(deliberation, nom), f"graine {graine}, minute {minute}")
        return originale(m, id, minute)
    with patch.object(deliberation, "deliberer", deliberer):
        executer(monde, int(heures * 60))


def dans_la_suite(c):
    originales = {b: getattr(deliberation, nom) for b, nom in METHODES.items()}

    def envelopper(besoin):
        def methode(monde, id):
            test = next((ligne.strip().splitlines()[0] for ligne in traceback.format_stack() if "test_" in ligne), "?")
            c.comparer(monde, id, besoin, originales[besoin], test)
            return originales[besoin](monde, id)
        return methode
    remplacees = {b: envelopper(b) for b in METHODES}
    progres = dict(deliberation.PROGRES, chaleur=(remplacees["chaleur"], deliberation.PROGRES["chaleur"][1]))
    with patch.object(deliberation, "_plan_manger", remplacees["faim"]), \
            patch.object(deliberation, "_plan_chauffer", remplacees["chaleur"]), \
            patch.object(deliberation, "PROGRES", progres):
        racine = Path(__file__).resolve().parents[1]
        suite = unittest.defaultTestLoader.discover(str(racine / "tests"))
        with open(racine / "artifacts" / "comparaison_suite.log", "w", encoding="utf-8") as sortie:
            unittest.TextTestRunner(stream=sortie, verbosity=0).run(suite)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--graines", type=int, nargs="*", default=[])
    parser.add_argument("--heures", type=float, default=8)
    parser.add_argument("--suite", action="store_true", help="comparer pendant la suite de tests")
    args = parser.parse_args(argv)
    c = Comparaison()
    for graine in args.graines:
        au_banc(graine, args.heures, c)
    if args.suite:
        (Path(__file__).resolve().parents[1] / "artifacts").mkdir(exist_ok=True)
        dans_la_suite(c)
    print(c.rapport())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
