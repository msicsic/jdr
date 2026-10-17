"""Banc sans joueur : fait vivre les PNJ d'un scénario et imprime leur chronique.

    python -m donjon.banc_pnj --heures 3 --joueur chambre_cloche

Le joueur reste passif dans la salle choisie (par défaut, celle du départ) ; le temps
avance par le moteur réel, cinq minutes à la fois. Aucun appel à Luna. La chronique
montre gestes, confidences entre PNJ et leur issue (crue, doute, démenti).
"""
import argparse
from collections import Counter

from .esprits import lire, pnjs
from .moteur import Moteur, proposition


def creer(scenario):
    if scenario == "relais":
        from .defi import nouveau_defi
        from .spatial import installer
        m = nouveau_defi()
        installer(m)
        return m
    from .monde import nouveau_monde
    return nouveau_monde()


def executer(monde, minutes):
    """Avance le monde ; renvoie la chronique produite et quelques mesures."""
    depart = len(monde.data.get("chronique", []))
    while monde.data["minutes"] < minutes:
        Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre")))
    chronique = monde.data.get("chronique", [])[depart:]
    memoire = Counter(s["type"] for id in pnjs(monde) for s in lire(monde, id)["memoire"])
    mefiances = sum(1 for id in pnjs(monde) for c in lire(monde, id)["croyances"].values()
                    if c.get("fiable", {}).get("valeur") is False)
    mesures = {"gestes": len(chronique), "renoncements": memoire["renoncement"],
               "vols_vus": memoire["vu_agir"], "absences": memoire["absence"],
               "confidences": sum(" dit à " in c["texte"] for c in chronique),
               "rumeurs_crues": memoire["rumeur"], "rumeurs_doutees": memoire["parole_doutee"],
               "mefiances": mefiances, "jets": monde.data["jets"]}
    return chronique, mesures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", choices=("relais", "crypte"), default="relais")
    parser.add_argument("--heures", type=float, default=3)
    parser.add_argument("--joueur", help="salle où le joueur reste passif")
    args = parser.parse_args(argv)
    monde = creer(args.scenario)
    if args.joueur:
        from .geometrie import position_entree
        monde.joueur.update(salle=args.joueur, position=list(position_entree(monde, args.joueur)))
    chronique, mesures = executer(monde, int(args.heures * 60))
    for c in chronique:
        print(f'[{c["minute"]:>4} min] {c["texte"]}')
    print()
    for id in pnjs(monde):
        e = lire(monde, id)
        besoins = ", ".join(f"{k} {v:.0f}" for k, v in e["besoins"].items())
        but = e["intention"]["but"] if e["intention"] else None
        print(f'{monde.objets[id]["nom"]} : {besoins or "sans profil"} ; intention : {but}')
    print("Mesures :", ", ".join(f"{k} {v}" for k, v in mesures.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
