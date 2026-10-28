"""Banc de parties scriptées : mesure ce que le joueur lit et ce que coûte chaque tour.

Chaque script rejoue une suite de saisies sur une sauvegarde temporaire, par la même
boucle que la console. Les mesures portent sur les appels au modèle, la durée, les
replis du contrôle narratif et les mentions d'entités sans fondement.

  python tools/banc_parties.py tests/data/bancs/relais.json --max-appels 200
  python tools/banc_parties.py tests/data/bancs/*.json --offline
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import time

BASE = Path(__file__).resolve().parents[1]
# SEUIL_CODE : le code du jeu à mesurer (un worktree), joué par l'outil de banc de ce dépôt.
sys.path.insert(0, os.environ.get("SEUIL_CODE") or str(BASE))

import jeu  # noqa: E402
from donjon import lexique  # noqa: E402
from donjon.mj import MJOpenAI  # noqa: E402
from donjon.monde import Monde  # noqa: E402

# Formules de repli produites par le contrôle ou la boucle de jeu, pas par Luna.
REPLIS = ("Je ne peux pas encore", "Rien de ce que tu perçois ou sais ne permet",
          "n'en disent pas davantage", "sans te répondre.", "C'est une possibilité, pas un fait établi",
          "Je n'ai pas pu déterminer une manœuvre", "Corvus n'a rien tenté",
          "Je n'ai pas pu déterminer le geste à examiner",
          "Réponse du MJ invalide", "Le contrôle narratif n'a pas abouti",
          "n'a pas terminé", "Aucune action appliquée", "Aucun changement enregistré",
          "Aucun ajout enregistré", "Aucun engagement enregistré")
LANCEMENT = {"relais": ["--defi"], "atelier": ["--atelier", "--cases"], "crypte": ["--cases"],
             "mine": ["--mine"], "auberge": ["--auberge"], "crue": ["--crue"], "rixe": ["--rixe"]}


class BudgetEpuise(RuntimeError):
    pass


class Compteur:
    def __init__(self, maximum, fil=False, reflexion="libre", effort="medium"):
        self.maximum, self.total, self.appels, self.traces = maximum, 0, [], []
        self.fil, self.reflexion, self.effort = fil, reflexion, effort

    def installer(self):
        compteur, origine_brut, origine_init = self, MJOpenAI._appeler_brut, MJOpenAI.__init__
        # Instrumentation du lanceur : identique aussi pour un ancien SEUIL_CODE.
        from donjon import transport_openai
        lire = transport_openai.lire_evenements
        compteur.mesure = None

        def lire_mesure(evenements):
            def suivre():
                for evenement in evenements:
                    if (compteur.mesure is not None and evenement.get("delta")
                            and evenement.get("type", "").endswith(".delta")):
                        compteur.mesure.setdefault("premier_jeton", round(
                            time.monotonic() - compteur.mesure["_debut"], 4))
                    yield evenement
            return lire(suivre())

        transport_openai.lire_evenements = lire_mesure

        def observer(trace):
            if trace.get("etape") == "appel" and compteur.mesure is not None:
                trace.update({k: v for k, v in compteur.mesure.items() if not k.startswith("_")})
            compteur.traces.append(trace)

        def appeler_brut(mj, instructions, entree, intention, fonction, schema):
            if compteur.total >= compteur.maximum:
                raise BudgetEpuise(f"Budget du banc atteint ({compteur.maximum} appels).")
            compteur.total += 1
            debut = time.monotonic()
            compteur.mesure = {"_debut": debut, "debut": debut,
                               "premier_jeton": None}
            # setdefault doit pouvoir enregistrer le premier delta.
            del compteur.mesure["premier_jeton"]
            try:
                return origine_brut(mj, instructions, entree, intention, fonction, schema)
            finally:
                usage = mj.derniere_utilisation or {}
                compteur.appels.append({**{k: v for k, v in compteur.mesure.items() if not k.startswith("_")},
                                        "fin": time.monotonic(), "fonction": fonction,
                                        "secondes": round(time.monotonic() - debut, 2),
                                        "usage": usage,
                                        "tokens": usage.get("total_tokens", 0)})
                compteur.mesure = None

        def init(mj, *a, **k):
            origine_init(mj, *a, **k)
            mj.observateur = observer
            mj.journal_complet, mj.reflexion = compteur.fil, compteur.reflexion

        MJOpenAI._appeler_brut, MJOpenAI.__init__ = appeler_brut, init


def resume_etat(m):
    """Ce que la sauvegarde rechargée établit après le tour : place et temps du joueur, ce qu'il
    porte, les personnages et les formes de passage décrites dans sa salle (relecture des bancs)."""
    from donjon.esprits import pnjs
    from donjon import agendas
    from donjon.spatial import porte_par
    from donjon.temps import instant
    salle = m.joueur["salle"]
    return {"salle": salle, "position": m.joueur.get("position"), "orientation": m.joueur.get("orientation"),
            "dixiemes": instant(m), "jets": m.data.get("jets"),
            "porte": sorted(i for i in m.objets if porte_par(m, i, "joueur")),
            "promesses_joueur": agendas.en_cours(m, "joueur"),
            "personnages": {i: [m.objets[i]["lieu"], m.objets[i].get("position")] for i in pnjs(m)},
            "passages": {i: o["passage"] for i, o in m.objets.items() if o.get("lieu") == salle and "passage" in o},
            "bloquants": sorted(i for i, o in m.objets.items()
                                if o.get("lieu") == salle and o.get("bloque_passage"))}


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
                    chemin_critique=appels,
                    fonctions=[a["fonction"] for a in appels],
                    secondes=round(sum(a["secondes"] for a in appels), 2),
                    tokens=sum(a["tokens"] for a in appels),
                    # Un repli du contrôle narratif se lit dans sa trace, quelle qu'en soit la voie (ce
                    # que le moteur a établi, les phrases admises d'une réponse, ou son propre texte).
                    replis=[r for r in REPLIS if r in texte]
                    + ["contrôle narratif : " + t["voie"] for t in traces
                       if t.get("etape") == "repli du contrôle narratif"],
                    refus=[t.get("obstacle", "") for t in traces if t.get("etape") == "validation"],
                    erreurs=[t["erreur"] for t in traces if t.get("erreur")],
                    controle=[o.get("motif", "") + " | " + o.get("texte", "")[:160]
                              for t in traces if t.get("etape") == "contrôle narratif"
                              for o in t["obstacles"]],
                    mentions_sans_fondement=mentions,
                    propositions=[t["reponse"]["proposition"] for t in traces
                                  if isinstance(t.get("reponse"), dict) and t["reponse"].get("proposition")])
        if self.compteur.fil:
            # Le fil entier du tour : chaque appel (prompt, réponse) et chaque verdict, dans l'ordre.
            tour["fil"] = [t for t in traces if t.get("etape") in ("appel", "validation", "contrôle narratif",
                                                                   "couverture de l'action",
                                                                   "repli du contrôle narratif") or t.get("erreur")]
        if apres is not None:
            tour["etat"] = resume_etat(apres)
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
    elif donnees["scenario"] == "atelier":
        from donjon.atelier import nouveau_atelier
        m = nouveau_atelier()
    elif donnees["scenario"] in ("mine", "auberge", "crue", "rixe"):
        from donjon.banc_pnj import creer
        m = creer(donnees["scenario"], seed, "fixe")
    else:
        from donjon.monde import nouveau_monde
        m = nouveau_monde(seed)
    if "--cases" in LANCEMENT[donnees["scenario"]] or donnees["scenario"] == "relais":
        from donjon.spatial import installer
        installer(m)
    m.joueur["stats"].update(prep.get("stats", {}))
    for cle in ("salle", "position", "orientation"):
        if cle in prep:
            m.joueur[cle] = prep[cle]
    for id, place in prep.get("personnages", {}).items():
        # Placement d'auteur : un personnage à une case, tourné vers une direction.
        m.objets[id].update(lieu=place["salle"], position=list(place["position"]), position_salle=place["salle"])
        if "orientation" in place:
            m.objets[id]["orientation"] = place["orientation"]
    for id in prep.get("calmes", []):
        # Placement d'auteur : aucun besoin pressant, rondes faites ; le personnage reste où il est.
        besoins = esprit(m, id)["besoins"]
        for b in besoins:
            besoins[b] = 0.0
        for x in m.objets[id]["profil"]["pulsions"]:
            if "periode" in x["condition"]:
                esprit(m, id)["visites"][x["condition"]["lieu"]] = m.data["minutes"]
    m.data["connus"].extend(prep.get("connus", []))
    for salle, cases in prep.get("exploration", {}).items():
        m.data.setdefault("exploration", {}).setdefault(salle, []).extend(cases)
    # Une scène de banc peut déclarer les présentations déjà entendues, séparément de la vue.
    if prep.get("noms_connus"):
        from donjon.noms import apprendre
        for id in prep["noms_connus"]:
            apprendre(m, "joueur", id)
    for id, lieu in prep.get("lieux", {}).items():
        # Placement d'auteur : un objet déjà en main ou ailleurs, pour cibler une scène.
        m.objets[id]["lieu"] = lieu
    for id, proprietes in prep.get("proprietes_objets", {}).items():
        # Données d'auteur du banc, contrôlées à la sauvegarde ; null retire une
        # propriété pour éprouver aussi le contrat d'une donnée inconnue.
        for cle, valeur in proprietes.items():
            if valeur is None:
                m.objets[id].pop(cle, None)
            else:
                m.objets[id][cle] = valeur
    for id, besoins in prep.get("besoins", {}).items():
        esprit(m, id)["besoins"].update(besoins)
    for id, valeurs in prep.get("valeurs", {}).items():
        m.objets[id]["profil"]["valeurs"].update(valeurs)   # Placement d'auteur : un caractère retouché.
    for id, liens in prep.get("relations", {}).items():
        from donjon.relations import _nouvelle
        for autre, axes in liens.items():
            esprit(m, id)["relations"][autre] = _nouvelle(axes, m.data["minutes"])
    from donjon.biens import rembourser
    for d in prep.get("dettes", []):
        # Placement d'auteur : une contrepartie payée et jamais livrée, comme l'échéance la fait naître.
        rembourser(m, d["de"], d["a"], d["montant"], d["objet"], d.get("quoi", "part"))
    # États du corps d'abord (blessé, inconscient, mort) : la scène existe avant les noms et les appels.
    from donjon.banc_pnj import appliquer_etats
    appliquer_etats(m, prep.get("etats", []))
    for qui, noms in prep.get("noms_connus_par", {}).items():
        from donjon.noms import apprendre
        for nom in noms:
            apprendre(m, qui, nom)
    for qui in prep.get("appels", []):
        from donjon.pnj import appeler
        appeler(m, qui, "joueur", [])
    # Épreuve de force : seules les règles communes établissent le coup, ses témoins et son issue.
    for coup in prep.get("coups", []):
        from donjon.combat import frapper
        from donjon.esprits import percevoir_tous
        percevoir_tous(m)
        frapper(m, coup["auteur"], coup["cible"], coup.get("outil", ""), coup.get("methode", "simple"))
    m.verifier()
    m.sauver(sauvegarde)


def jouer(script, compteur, offline, connexion="chatgpt"):
    donnees = json.loads(Path(script).read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as dossier:
        sauvegarde = Path(dossier) / "banc.json"
        interface = Interface(donnees["tours"], sauvegarde, compteur)
        argv = [*LANCEMENT[donnees["scenario"]], "--new", "--save", str(sauvegarde),
                "--seed", str(donnees.get("seed", 1985))]
        if donnees.get("sauvegarde"):
            # Une scène enregistrée (``tests/data/scenes``), jouée sur une copie : jamais sur l'original.
            source = BASE / donnees["sauvegarde"]
            brut = source.read_bytes()
            sauvegarde.write_bytes(gzip.decompress(brut) if source.suffix == ".gz" else brut)
            if donnees.get("noms_connus"):
                # Présentations déjà entendues, déclarées par le banc comme pour une préparation.
                from donjon.noms import apprendre
                m = Monde.charger(sauvegarde)
                for id in donnees["noms_connus"]:
                    apprendre(m, "joueur", id)
                m.verifier()
                m.sauver(sauvegarde)
            argv.remove("--new")
        elif donnees.get("preparation"):
            preparer(donnees, sauvegarde)
            argv.remove("--new")
        if offline:
            argv.append("--offline")
        else:
            argv += ["--connexion", connexion, "--effort", compteur.effort, "--reflexion", compteur.reflexion]
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
    p.add_argument("--connexion", choices=("chatgpt", "anthropic", "mimo", "local"), default="chatgpt",
                   help="anthropic : essai de Claude (ANTHROPIC_API_KEY), jamais choisi par défaut")
    p.add_argument("--effort", choices=("none", "low", "medium", "high"), default=None)
    p.add_argument("--reflexion", choices=("libre", "imposee"), default="libre",
                   help="Claude : réflexion adaptative et outil libre (défaut), ou outil imposé sans réflexion")
    p.add_argument("--sortie", type=Path, default=BASE / "artifacts" / "bancs",
                   help="dossier des résultats (par défaut artifacts/bancs du dépôt)")
    p.add_argument("--fil", action="store_true",
                   help="garde le prompt et la réponse de chaque appel, et écrit un rapport HTML du fil")
    args = p.parse_args(argv)
    if args.effort is None:
        args.effort = "none" if args.connexion == "mimo" else "medium"
    sys.stdout.reconfigure(encoding="utf-8")
    compteur = Compteur(args.max_appels, args.fil, args.reflexion, args.effort)
    compteur.installer()
    sortie = args.sortie
    sortie.mkdir(parents=True, exist_ok=True)
    # Le numéro de processus distingue des bancs lancés à la même seconde.
    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}"
    resumes = []
    for script in args.scripts:
        partie = jouer(script, compteur, args.offline, args.connexion)
        nom = f"{horodatage}-{args.etiquette + '-' if args.etiquette else ''}{partie['script']}.json"
        (sortie / nom).write_text(json.dumps(partie, ensure_ascii=False, indent=1), encoding="utf-8")
        if args.fil:
            from rapport_fil import ecrire
            ecrire(sortie / nom)
        resumes.append(resumer(partie))
        print(json.dumps(resumes[-1], ensure_ascii=False))
        if partie["arret"]:
            break
    print(f"Appels utilisés : {compteur.total}. Détails : {sortie}")


if __name__ == "__main__":
    main()
