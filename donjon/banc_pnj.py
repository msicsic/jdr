"""Banc sans joueur : fait vivre les PNJ d'un scénario et imprime leur chronique.

    python -m donjon.banc_pnj --heures 3 --joueur chambre_cloche
    python -m donjon.banc_pnj --heures 8 --joueur chambre_cloche --stratege --graine 7
    python -m donjon.banc_pnj --heures 8 --joueur chambre_cloche --graines 1985 7 42 2024

Le joueur reste passif dans la salle choisie (par défaut, celle du départ) ; le temps
avance par le moteur réel, cinq minutes à la fois, et l'état est vérifié à chaque pas. Sans
``--stratege``, aucun appel à Luna. Le banc imprime le récit (``recit_pnj``) : buts, gestes,
besoins de chaque PNJ, échanges entre eux. ``--chronique`` ajoute chaque pas : gestes,
échanges et leur issue, décisions du stratège. ``--graines`` joue plusieurs nuits en
parallèle (une par processus, sans stratège) et termine par leurs mesures et leur moyenne.
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
    """PNJ qu'un besoin urgent presse et qui n'ont rien entrepris ; puis ceux d'entre eux pour
    qui ce besoin a vraiment quelque chose à faire (une pulsion rompue, ou aucune pulsion)."""
    from .deliberation import satisfaite, urgents
    oisifs = bloques = 0
    for id in pnjs(monde):
        p = monde.objets[id].get("profil")
        if not p or lire(monde, id)["intention"] is not None or not urgents(monde, id):
            continue
        oisifs += 1
        bloques += any(not all(satisfaite(monde, id, x["condition"]) for x in p["pulsions"] if x["besoin"] == b)
                       or not any(x["besoin"] == b for x in p["pulsions"]) for b in urgents(monde, id))
    return oisifs, bloques


def _usurpations(monde):
    """PNJ qui portent l'objet d'une tâche confiée à quelqu'un qu'ils croient encore fiable."""
    from .deliberation import _delegue
    from .spatial import porte_par
    return sum(1 for id in pnjs(monde) for x in (monde.objets[id].get("profil") or {}).get("pulsions", [])
               if x.get("delegue_a") and _delegue(monde, id, x) and porte_par(monde, x["condition"]["objet"], id))


def executer(monde, minutes, recit=None):
    """Avance le monde ; renvoie la chronique produite et les mesures du banc. Un ``recit``
    observe chaque PNJ au passage."""
    if recit is not None:
        with recit.observer():
            resultat = executer(monde, minutes)
        recit.clore(monde)
        return resultat
    chronique, vue, oisivete, blocage, usurpations = [], monde.data["minutes"], 0, 0, 0
    while monde.data["minutes"] < minutes:
        Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre")))
        monde.verifier()
        # La chronique est bornée : on recueille à chaque pas ce qui vient de s'y ajouter.
        chronique += [c for c in monde.data.get("chronique", []) if c["minute"] > vue]
        vue = monde.data["minutes"]
        oisifs, bloques = _oisifs_urgents(monde)
        oisivete, blocage = oisivete + PAS * oisifs, blocage + PAS * bloques
        usurpations += _usurpations(monde)
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
               # Mesure d'information ajoutée après le premier banc E, hors critère de décision.
               "minutes_urgentes_sans_recours": blocage,
               "usurpations": usurpations,
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


def nuit(scenario, graine, heures, joueur, chronique=False):
    """Une nuit sans joueur : (texte imprimable, mesures, données pour --sortie)."""
    monde = creer(scenario, graine)
    if joueur:
        from .geometrie import position_entree
        monde.joueur.update(salle=joueur, position=list(position_entree(monde, joueur)))
    from .recit_pnj import Recit
    recit = Recit(monde)
    pas, mesures = executer(monde, int(heures * 60), recit)
    lignes = [f'[{c["minute"]:>4} min] {c["texte"]}' for c in pas] + [""] if chronique else []
    lignes += [recit.texte(monde, pas), ""]
    for id in pnjs(monde):
        e = lire(monde, id)
        besoins = ", ".join(f"{k} {v:.0f}" for k, v in e["besoins"].items())
        but = e["intention"]["but"] if e["intention"] else None
        lignes.append(f'{monde.objets[id]["nom"]} : {besoins or "sans profil"} ; intention : {but}')
    lignes.append("Mesures : " + ", ".join(f"{k} {v}" for k, v in mesures.items()))
    donnees = {"graine": graine, "heures": heures, "chronique": pas, "mesures": mesures,
               "recit": recit.donnees(monde, pas), "souvenirs": {id: lire(monde, id)["memoire"] for id in pnjs(monde)}}
    return "\n".join(lignes), mesures, donnees


def _nuit(arguments):
    return nuit(*arguments)


def nuits(scenario, graines, heures, joueur, chronique=False):
    """Plusieurs nuits en parallèle, une par processus ; les résultats dans l'ordre des graines."""
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=min(len(graines), 16)) as pool:
        return list(pool.map(_nuit, [(scenario, g, heures, joueur, chronique) for g in graines]))


def tableau(graines, mesures):
    """Les mesures de chaque graine, puis leur moyenne."""
    cles = list(mesures[0])
    lignes = ["graine " + " ".join(cles)]
    for g, m in zip(graines, mesures):
        lignes.append(f"{g} " + " ".join(str(m[k]) for k in cles))
    lignes.append("moyenne " + " ".join(f"{sum(m[k] for m in mesures) / len(mesures):g}" for k in cles))
    return "\n".join(lignes)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", choices=("relais", "crypte"), default="relais")
    parser.add_argument("--heures", type=float, default=3)
    parser.add_argument("--joueur", help="salle où le joueur reste passif")
    parser.add_argument("--graine", type=int, default=1985)
    parser.add_argument("--graines", type=int, nargs="+", help="plusieurs nuits en parallèle, sans stratège")
    parser.add_argument("--stratege", action="store_true", help="Luna conseille les PNJ (appels plafonnés)")
    parser.add_argument("--connexion", choices=("chatgpt", "api"), default="chatgpt")
    parser.add_argument("--sortie", help="fichier JSON où écrire chronique, récit et mesures")
    parser.add_argument("--chronique", action="store_true", help="imprime aussi chaque pas")
    parser.add_argument("--rejeu", help="page HTML où rejouer la nuit (positions, regards, buts, croyances)")
    args = parser.parse_args(argv)
    if args.graines:
        if args.stratege or args.rejeu:
            parser.error("le stratège et le rejeu suivent une nuit à la fois : --graine, pas --graines")
        resultats = nuits(args.scenario, args.graines, args.heures, args.joueur, args.chronique)
        for g, (texte, _, _) in zip(args.graines, resultats):
            print(f"######## graine {g}\n{texte}\n")
        print(tableau(args.graines, [m for _, m, _ in resultats]))
        if args.sortie:
            with open(args.sortie, "w", encoding="utf-8") as f:
                json.dump([d for _, _, d in resultats], f, ensure_ascii=False, indent=1)
        return 0
    from . import stratege
    stratege.activer(appelant(args.connexion) if args.stratege else None)
    try:
        monde = creer(args.scenario, args.graine)
        if args.joueur:
            from .geometrie import position_entree
            monde.joueur.update(salle=args.joueur, position=list(position_entree(monde, args.joueur)))
        from .recit_pnj import Recit
        recit = Recit(monde)
        from contextlib import nullcontext
        from .rejeu import Enregistreur
        enregistreur = Enregistreur(monde) if args.rejeu else None
        with enregistreur.observer() if enregistreur else nullcontext():
            chronique, mesures = executer(monde, int(args.heures * 60), recit)
    finally:
        stratege.activer(None)
    if args.chronique:
        for c in chronique:
            print(f'[{c["minute"]:>4} min] {c["texte"]}')
        print()
    print(recit.texte(monde, chronique))
    print()
    for id in pnjs(monde):
        e = lire(monde, id)
        besoins = ", ".join(f"{k} {v:.0f}" for k, v in e["besoins"].items())
        but = e["intention"]["but"] if e["intention"] else None
        print(f'{monde.objets[id]["nom"]} : {besoins or "sans profil"} ; intention : {but}')
    print("Mesures :", ", ".join(f"{k} {v}" for k, v in mesures.items()))
    if args.rejeu:
        from .rejeu import page
        titre = f"Rejeu : {args.scenario}, graine {args.graine}, {args.heures:g} h"
        with open(args.rejeu, "w", encoding="utf-8") as f:
            f.write(page(enregistreur.donnees(monde, chronique, titre)))
        print("Rejeu :", args.rejeu)
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8") as f:
            json.dump({"graine": args.graine, "heures": args.heures, "stratege": args.stratege,
                       "chronique": chronique, "mesures": mesures, "recit": recit.donnees(monde, chronique),
                       "souvenirs": {id: lire(monde, id)["memoire"] for id in pnjs(monde)}},
                      f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
