"""Banc sans joueur : fait vivre les PNJ d'un scénario et imprime leur chronique.

    python -m donjon.banc_pnj --heures 3 --joueur chambre_cloche
    python -m donjon.banc_pnj --heures 8 --joueur chambre_cloche --stratege --graine 7

Le joueur reste passif dans la salle choisie (par défaut, celle du départ) ; le temps
avance par le moteur réel, cinq minutes à la fois, et l'état est vérifié à chaque pas. Sans
``--stratege``, aucun appel à Luna. La chronique montre gestes, échanges entre PNJ et leur
issue, décisions du stratège.
"""
import argparse
from collections import Counter
import json

from .esprits import lire, pnjs
from .moteur import Moteur, proposition

PAS = 5


def creer(scenario, graine=1985):
    if scenario == "relais":
        from .defi import nouveau_defi
        from .spatial import installer
        m = nouveau_defi(graine)
        installer(m)
        return m
    from .monde import nouveau_monde
    return nouveau_monde(graine)


def _oisifs_urgents(monde):
    """PNJ qu'un besoin urgent presse et qui n'ont rien entrepris."""
    from .deliberation import urgents
    return sum(1 for id in pnjs(monde) if monde.objets[id].get("profil")
               and lire(monde, id)["intention"] is None and urgents(monde, id))


def executer(monde, minutes):
    """Avance le monde ; renvoie la chronique produite et les mesures du banc."""
    chronique, vue, oisivete = [], monde.data["minutes"], 0
    while monde.data["minutes"] < minutes:
        Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre")))
        monde.verifier()
        # La chronique est bornée : on recueille à chaque pas ce qui vient de s'y ajouter.
        chronique += [c for c in monde.data.get("chronique", []) if c["minute"] > vue]
        vue = monde.data["minutes"]
        oisivete += PAS * _oisifs_urgents(monde)
    memoire = Counter(s["type"] for id in pnjs(monde) for s in lire(monde, id)["memoire"])
    natures = Counter(c.get("nature", "geste") for c in chronique)
    mefiances = sum(1 for id in pnjs(monde) for c in lire(monde, id)["croyances"].values()
                    if c.get("fiable", {}).get("valeur") is False)
    bilan = monde.data.get("stratege", {}).get("bilan", {})
    mesures = {"gestes": len(chronique),
               "evenements_distincts": len({(c["pnj"], c["texte"]) for c in chronique
                                            if c.get("nature", "geste") in ("geste", "social")}),
               "echanges": natures["social"], "decisions": natures["decision"],
               "minutes_urgentes_oisives": oisivete,
               "renoncements": memoire["renoncement"],
               "vols_vus": memoire["vu_agir"], "absences": memoire["absence"],
               "confidences": sum(" dit à " in c["texte"] for c in chronique),
               "rumeurs_crues": memoire["rumeur"], "rumeurs_doutees": memoire["parole_doutee"],
               "mefiances": mefiances, "jets": monde.data["jets"],
               **{"stratege_" + k: v for k, v in sorted(bilan.items())}}
    return chronique, mesures


def appelant(connexion="chatgpt", modele=None, effort="medium"):
    """Luna en stratège, par la même connexion que le MJ du jeu."""
    from .config import charger_env
    from .mj import MJOpenAI
    charger_env()
    return MJOpenAI(modele, effort, timeout=90, connexion=connexion)._appeler_brut


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", choices=("relais", "crypte"), default="relais")
    parser.add_argument("--heures", type=float, default=3)
    parser.add_argument("--joueur", help="salle où le joueur reste passif")
    parser.add_argument("--graine", type=int, default=1985)
    parser.add_argument("--stratege", action="store_true", help="Luna conseille les PNJ (appels plafonnés)")
    parser.add_argument("--connexion", choices=("chatgpt", "api"), default="chatgpt")
    parser.add_argument("--sortie", help="fichier JSON où écrire chronique et mesures")
    args = parser.parse_args(argv)
    from . import stratege
    stratege.activer(appelant(args.connexion) if args.stratege else None)
    try:
        monde = creer(args.scenario, args.graine)
        if args.joueur:
            from .geometrie import position_entree
            monde.joueur.update(salle=args.joueur, position=list(position_entree(monde, args.joueur)))
        chronique, mesures = executer(monde, int(args.heures * 60))
    finally:
        stratege.activer(None)
    for c in chronique:
        print(f'[{c["minute"]:>4} min] {c["texte"]}')
    print()
    for id in pnjs(monde):
        e = lire(monde, id)
        besoins = ", ".join(f"{k} {v:.0f}" for k, v in e["besoins"].items())
        but = e["intention"]["but"] if e["intention"] else None
        print(f'{monde.objets[id]["nom"]} : {besoins or "sans profil"} ; intention : {but}')
    print("Mesures :", ", ".join(f"{k} {v}" for k, v in mesures.items()))
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8") as f:
            json.dump({"graine": args.graine, "heures": args.heures, "stratege": args.stratege,
                       "chronique": chronique, "mesures": mesures,
                       "souvenirs": {id: lire(monde, id)["memoire"] for id in pnjs(monde)}},
                      f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
