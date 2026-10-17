"""Banc de parties scriptées : mesure ce que le joueur lit et ce que coûte chaque tour.

Chaque script rejoue une suite de saisies sur une sauvegarde temporaire, par la même
boucle que la console. Les mesures portent sur les appels au modèle, la durée, les
replis du contrôle narratif et les mentions d'entités sans fondement.

  python tools/banc_parties.py tests/data/bancs/relais.json --max-appels 200
  python tools/banc_parties.py tests/data/bancs/*.json --offline
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import time

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import jeu  # noqa: E402
from donjon import lexique  # noqa: E402
from donjon.mj import MJOpenAI  # noqa: E402
from donjon.monde import Monde  # noqa: E402

# Formules de repli produites par le contrôle ou la boucle de jeu, pas par Luna.
REPLIS = ("Je ne peux pas encore", "C'est une possibilité, pas un fait établi",
          "Je n'ai pas pu déterminer une manœuvre", "Corvus n'a rien tenté",
          "Réponse du MJ invalide", "Le contrôle narratif n'a pas abouti",
          "n'a pas terminé", "Aucune action appliquée", "Aucun changement enregistré",
          "Aucun ajout enregistré", "Aucun engagement enregistré")
LANCEMENT = {"relais": ["--defi"], "atelier": ["--atelier", "--cases"], "crypte": ["--cases"]}


class BudgetEpuise(RuntimeError):
    pass


class Compteur:
    def __init__(self, maximum):
        self.maximum, self.total, self.appels, self.traces = maximum, 0, [], []

    def installer(self):
        compteur, origine_brut, origine_init = self, MJOpenAI._appeler_brut, MJOpenAI.__init__

        def appeler_brut(mj, instructions, entree, intention, fonction, schema):
            if compteur.total >= compteur.maximum:
                raise BudgetEpuise(f"Budget du banc atteint ({compteur.maximum} appels).")
            compteur.total += 1
            debut = time.monotonic()
            try:
                return origine_brut(mj, instructions, entree, intention, fonction, schema)
            finally:
                usage = mj.derniere_utilisation or {}
                compteur.appels.append({"fonction": fonction,
                                        "secondes": round(time.monotonic() - debut, 2),
                                        "tokens": usage.get("total_tokens", 0)})

        def init(mj, *a, **k):
            origine_init(mj, *a, **k)
            mj.observateur = compteur.traces.append

        MJOpenAI._appeler_brut, MJOpenAI.__init__ = appeler_brut, init


class Interface:
    """Fournit les saisies du script et découpe la sortie en tours."""

    def __init__(self, saisies, sauvegarde, compteur):
        self.saisies, self.sauvegarde, self.compteur = list(saisies), sauvegarde, compteur
        self.tours, self.courant, self.affiches = [], None, []

    def _etat(self):
        return Monde.charger(self.sauvegarde) if self.sauvegarde.exists() else None

    def _clore(self):
        if self.courant is None:
            return
        tour, self.courant = self.courant, None
        appels = self.compteur.appels[tour.pop("_appels"):]
        traces = self.compteur.traces[tour.pop("_traces"):]
        texte = "\n".join(s for s in tour["sorties"]
                          if s.strip() and s != "Le MJ réfléchit…" and not s.startswith("[vue "))
        avant, apres = tour.pop("_avant"), self._etat()
        mentions = []
        if avant is not None and apres is not None:
            fondement = lexique.corpus(avant.contexte(), apres.contexte(), self.affiches)
            mentions = lexique.mentions_sans_fondement(apres, texte, fondement)
        tour.update(texte=texte, appels=len(appels),
                    fonctions=[a["fonction"] for a in appels],
                    secondes=round(sum(a["secondes"] for a in appels), 2),
                    tokens=sum(a["tokens"] for a in appels),
                    replis=[r for r in REPLIS if r in texte],
                    refus=[t.get("obstacle", "") for t in traces if t.get("etape") == "validation"],
                    erreurs=[t["erreur"] for t in traces if t.get("erreur")],
                    controle=[o.get("motif", "") + " | " + o.get("texte", "")[:160]
                              for t in traces if t.get("etape") == "contrôle narratif"
                              for o in t["obstacles"]],
                    mentions_sans_fondement=mentions,
                    propositions=[t["reponse"]["proposition"] for t in traces
                                  if isinstance(t.get("reponse"), dict) and t["reponse"].get("proposition")])
        self.affiches.append(texte)
        self.tours.append(tour)

    def lire(self, _invite=""):
        self._clore()
        if not self.saisies:
            return "quitter"
        saisie = self.saisies.pop(0)
        self.courant = {"saisie": saisie, "sorties": [], "_appels": len(self.compteur.appels),
                        "_traces": len(self.compteur.traces), "_avant": self._etat()}
        return saisie

    def ecrire(self, *valeurs, **_options):
        texte = " ".join(str(v) for v in valeurs)
        if self.courant is not None:
            self.courant["sorties"].append(texte)

    def montrer(self, vue):
        if self.courant is not None:
            self.courant["sorties"].append(f"[vue {vue}]")

    def rafraichir(self, *_):
        pass

    def comparaison(self, *_):
        pass


def preparer(donnees, sauvegarde):
    """État de départ d'un script : caractéristiques, place du joueur, besoins des PNJ."""
    from donjon.esprits import esprit
    seed, prep = donnees.get("seed", 1985), donnees["preparation"]
    if donnees["scenario"] == "relais":
        from donjon.defi import nouveau_defi
        m = nouveau_defi(seed)
    else:
        from donjon.monde import nouveau_monde
        m = nouveau_monde(seed)
    if "--cases" in LANCEMENT[donnees["scenario"]] or donnees["scenario"] == "relais":
        from donjon.spatial import installer
        installer(m)
    m.joueur["stats"].update(prep.get("stats", {}))
    for cle in ("salle", "position"):
        if cle in prep:
            m.joueur[cle] = prep[cle]
    m.data["connus"].extend(prep.get("connus", []))
    for id, besoins in prep.get("besoins", {}).items():
        esprit(m, id)["besoins"].update(besoins)
    m.verifier()
    m.sauver(sauvegarde)


def jouer(script, compteur, offline, connexion="chatgpt"):
    donnees = json.loads(Path(script).read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as dossier:
        sauvegarde = Path(dossier) / "banc.json"
        interface = Interface(donnees["tours"], sauvegarde, compteur)
        argv = [*LANCEMENT[donnees["scenario"]], "--new", "--save", str(sauvegarde),
                "--seed", str(donnees.get("seed", 1985))]
        if donnees.get("preparation"):
            preparer(donnees, sauvegarde)
            argv.remove("--new")
        if offline:
            argv.append("--offline")
        else:
            argv += ["--connexion", connexion]
        arret = None
        try:
            jeu.main(argv, interface=interface)
        except BudgetEpuise as exc:
            arret = str(exc)
        interface._clore()
        rechargement = None
        try:
            Monde.charger(sauvegarde)
        except Exception as exc:  # le banc rapporte l'échec au lieu de l'interrompre
            rechargement = str(exc)
        return {"script": Path(script).stem, "tours": interface.tours, "arret": arret,
                "erreur_rechargement": rechargement}


def resumer(partie):
    tours = [t for t in partie["tours"] if t["saisie"] != "quitter"]
    mj = [t for t in tours if t["appels"]]
    return {
        "script": partie["script"], "tours": len(tours), "tours_mj": len(mj),
        "appels": sum(t["appels"] for t in tours),
        "appels_par_tour_mj": round(sum(t["appels"] for t in mj) / len(mj), 2) if mj else 0,
        "secondes_par_tour_mj": round(sum(t["secondes"] for t in mj) / len(mj), 1) if mj else 0,
        "tours_avec_repli": sum(bool(t["replis"]) for t in tours),
        "tours_avec_refus": sum(bool(t["refus"]) for t in tours),
        "tours_avec_erreur": sum(bool(t["erreurs"]) for t in tours),
        "mentions_sans_fondement": sum(len(t["mentions_sans_fondement"]) for t in tours),
        "arret": partie["arret"], "erreur_rechargement": partie["erreur_rechargement"],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("scripts", nargs="+")
    p.add_argument("--offline", action="store_true", help="aucun appel au modèle")
    p.add_argument("--max-appels", type=int, default=150)
    p.add_argument("--etiquette", default="")
    p.add_argument("--connexion", choices=("chatgpt", "api", "mimo"), default="chatgpt",
                   help="fournisseur du MJ ; mimo pour un essai comparatif")
    args = p.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    compteur = Compteur(args.max_appels)
    compteur.installer()
    sortie = BASE / "artifacts" / "bancs"
    sortie.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
    resumes = []
    for script in args.scripts:
        partie = jouer(script, compteur, args.offline, args.connexion)
        nom = f"{horodatage}-{args.etiquette + '-' if args.etiquette else ''}{partie['script']}.json"
        (sortie / nom).write_text(json.dumps(partie, ensure_ascii=False, indent=1), encoding="utf-8")
        resumes.append(resumer(partie))
        print(json.dumps(resumes[-1], ensure_ascii=False))
        if partie["arret"]:
            break
    print(f"Appels utilisés : {compteur.total}. Détails : {sortie}")


if __name__ == "__main__":
    main()
