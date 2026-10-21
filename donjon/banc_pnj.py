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
``--rejeu page.html`` écrit en plus la page où rejouer la nuit ; avec ``--graines``, une page par
graine (``page_<graine>.html``, ou ``rejeu_<graine>.html`` dans le dossier donné).
"""
import argparse
from collections import Counter
import json

from .esprits import lire, pnjs
from .pnj import CONTRAINTES
from .moteur import Moteur, proposition

PAS = 5


def creer(scenario, graine=1985, depart="tire"):
    """Le monde d'un scénario ; ``depart`` : tiré de la graine (``depart.py``) ou ``"fixe"``, le
    départ déclaré."""
    if scenario in ("relais", "crue"):
        from .crue import nouvelle_crue
        from .defi import nouveau_defi
        from .spatial import installer
        m = (nouveau_defi if scenario == "relais" else nouvelle_crue)(graine, depart)
        installer(m)
        return m
    if scenario in ("mine", "auberge"):
        from .auberge import nouveau_auberge
        from .mine import nouveau_mine
        from .spatial import installer
        m = (nouveau_mine if scenario == "mine" else nouveau_auberge)(graine, depart)
        installer(m)
        return m
    from .monde import nouveau_monde
    return nouveau_monde(graine)


def _oisifs_urgents(monde):
    """PNJ qu'un besoin urgent presse et qui n'ont rien entrepris ; ceux d'entre eux pour qui ce
    besoin a vraiment quelque chose à faire eux-mêmes (une pulsion rompue qui n'est confiée à
    personne, ou aucune pulsion) et un plan possible, qu'ils n'ont pas entrepris (sans recours) ;
    ceux pour qui il n'en existe aucun sur ce qu'ils croient (en attente, ``deliberation.attentes``) ;
    enfin ceux qui n'attendent que ce qu'ils ont confié à un autre qu'ils croient fiable (Gorm et la
    cloche confiée au joueur, qui reste passif au banc). Chaque PNJ oisif compte dans une seule de
    ces catégories, dans cet ordre."""
    from .deliberation import _delegue, attentes, satisfaite, urgents
    oisifs = bloques = attente = confies = 0
    for id in pnjs(monde):
        p = monde.objets[id].get("profil")
        if not p or lire(monde, id)["intention"] is not None or not urgents(monde, id):
            continue
        oisifs += 1
        rompues = {b: [x for x in p["pulsions"] if x["besoin"] == b and not satisfaite(monde, id, x["condition"])]
                   for b in urgents(monde, id)}
        a_faire = [b for b, r in rompues.items()
                   if any(not _delegue(monde, id, x) for x in r) or not any(x["besoin"] == b for x in p["pulsions"])]
        sans_plan = attentes(monde, id)
        if any(b not in sans_plan for b in a_faire):
            bloques += 1
        elif a_faire:
            attente += 1
        elif any(rompues.values()):
            confies += 1
    return oisifs, bloques, attente, confies


# Les minutes où l'on prend l'empreinte de la nuit (``empreinte``) pour compter les nuits distinctes.
REPERES = (5, 60, 120, 240, 480)


def empreinte(monde):
    """L'état physique du monde à cet instant : places, regards, ce que chacun porte, portes,
    feux, portions, horloges et eau. Sans les valeurs internes des PNJ (besoins, corps, croyances,
    profil), que le tirage du départ fait différer dès la minute 0 : deux nuits de même empreinte
    en sont au même point."""
    import hashlib
    etat = {"objets": {id: {k: v for k, v in o.items() if k not in ("corps", "profil")}
                       for id, o in sorted(monde.objets.items())},
            "joueur": [monde.joueur["salle"], monde.joueur.get("position"), monde.joueur.get("orientation")],
            "horloges": monde.data.get("horloges_declenchees", []),
            "eau": (monde.data.get("crue") or {}).get("etats")}
    return hashlib.sha1(json.dumps(etat, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def issue(monde, chronique):
    """Ce que la nuit laisse : où finit chaque objet déplaçable (ou qui le tient), ce qui reste
    ouvert, verrouillé, allumé, ce qu'il reste à manger, dans quelle salle finit chacun, et les
    vols vus (auteur, objet). Plus grossière que l'empreinte : la case et le regard n'y sont pas."""
    import hashlib
    objets = {id: [o["lieu"] if o.get("mobile") or o["type"] == "personnage" else None,
                   *(o.get(k) for k in ("ouverte", "verrouillee", "allume", "portions"))]
              for id, o in sorted(monde.objets.items())}
    vols = sorted({(s["auteur"], s["objet"]) for id in pnjs(monde) for s in lire(monde, id)["memoire"]
                   if s["type"] == "vu_agir" and s["operation"] not in CONTRAINTES})
    texte = json.dumps({"objets": objets, "vols": vols}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(texte.encode()).hexdigest()[:12]


def _attente(c):
    """Une entrée de la chronique qui clôt l'attente d'être rejoint (``deliberation.attendre``)."""
    return c.get("nature") == "reponse" and (" retrouve " in c["texte"] or " cesse d'attendre " in c["texte"])


def _usurpations(monde):
    """PNJ qui portent l'objet d'une tâche confiée à quelqu'un qu'ils croient encore fiable."""
    from .deliberation import _delegue
    from .spatial import porte_par
    return sum(1 for id in pnjs(monde) for x in (monde.objets[id].get("profil") or {}).get("pulsions", [])
               if x.get("delegue_a") and _delegue(monde, id, x) and porte_par(monde, x["condition"]["objet"], id))


def _nouvelles(avant, apres):
    """Ce qui s'est ajouté à la chronique bornée : ``apres`` reprend la fin d'``avant`` (moins ce
    que la borne a fait tomber), puis les entrées nouvelles. Les dater ne suffit pas : les gestes
    de la première minute d'un pas portent la minute où il commence."""
    for commun in range(min(len(avant), len(apres)), 0, -1):
        if apres[:commun] == avant[len(avant) - commun:]:
            return apres[commun:]
    return list(apres)


def executer(monde, minutes, recit=None, empreintes=None):
    """Avance le monde ; renvoie la chronique produite et les mesures du banc. Un ``recit``
    observe chaque PNJ au passage. Un dictionnaire ``empreintes`` reçoit l'empreinte de l'état à
    chaque minute de ``REPERES`` atteinte, et l'``issue`` de la nuit."""
    if recit is not None:
        with recit.observer():
            resultat = executer(monde, minutes, empreintes=empreintes)
        recit.clore(monde)
        return resultat
    from .eau import active, lieu, profondeur
    vivants = [id for id in pnjs(monde) if monde.objets[id].get("profil")]
    chronique, oisivete, blocage, attente, confiance, usurpations, mouilles = [], 0, 0, 0, 0, 0, 0
    attendre_rejoint = 0
    releves = {}
    vue = list(monde.data.get("chronique", []))
    debut = monde.data["minutes"]
    while monde.data["minutes"] < minutes:
        Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre")))
        monde.verifier()
        courante = monde.data.get("chronique", [])
        chronique += _nouvelles(vue, courante)
        vue = list(courante)
        for repere in REPERES:
            if repere not in releves and monde.data["minutes"] >= repere:
                releves[repere] = empreinte(monde)
        oisifs, bloques, attendent, confies = _oisifs_urgents(monde)
        oisivete, blocage = oisivete + PAS * oisifs, blocage + PAS * bloques
        attente, confiance = attente + PAS * attendent, confiance + PAS * confies
        usurpations += _usurpations(monde)
        attendre_rejoint += PAS * sum(1 for id in vivants if (lire(monde, id)["intention"] or {}).get("but", {}).get("type") == "attendre")
        mouilles += PAS * sum(1 for id in vivants if profondeur(monde, lieu(monde, id)))
    memoire = Counter(s["type"] for id in pnjs(monde) for s in lire(monde, id)["memoire"])
    natures = Counter(c.get("nature", "geste") for c in chronique)
    mefiances = sum(1 for id in pnjs(monde) for c in lire(monde, id)["croyances"].values()
                    if c.get("fiable", {}).get("valeur") is False)
    bilan = monde.data.get("stratege", {}).get("bilan", {})
    temoins = [(id, s) for id in pnjs(monde) for s in lire(monde, id)["memoire"]
               if s["type"] == "vu_agir" and s["operation"] not in CONTRAINTES]
    mesures = {"gestes": sum(c.get("nature") != "ouie" for c in chronique),
               "evenements_distincts": len({(c["pnj"], c["texte"]) for c in chronique
                                            if c.get("nature", "geste") in ("geste", "social", "reponse")}),
               # Les échanges entre PNJ, sans les appels de qui cherche quelqu'un ni leurs réponses
               # (comptés à part, ``appels`` et ``reponses``).
               "echanges": natures["social"] + natures["reponse"] - sum(
                   " appelle : « " in c["texte"] or " répond : « " in c["texte"] or _attente(c) for c in chronique),
               "decisions": natures["decision"],
               "minutes_urgentes_oisives": oisivete,
               # Mesure d'information ajoutée après le premier banc E, hors critère de décision. Une
               # pulsion confiée à un autre que l'on croit fiable n'en est pas : elle attend (à part).
               "minutes_urgentes_sans_recours": blocage,
               # Pressé, sans rien entreprendre, faute d'aucun plan sur ce qu'il croit (``attentes``).
               "minutes_urgentes_en_attente": attente,
               "minutes_urgentes_confiees": confiance,
               # Le hasard de la nuit : jets de d20 par heure.
               "jets_par_heure": round(monde.data["jets"] * 60 / max(1, monde.data["minutes"] - debut), 2),
               "usurpations": usurpations,
               "renoncements": memoire["renoncement"],
               # Un vol vu se compte une fois (un auteur, un objet), quels que soient ses gestes d'une
               # minute ; ses témoins à part.
               "vols_vus": len({(s["auteur"], s["objet"]) for _, s in temoins}),
               "temoins_vols": len({(s["auteur"], s["objet"], id) for id, s in temoins}),
               "absences": memoire["absence"],
               "confidences": sum(" dit à " in c["texte"] for c in chronique),
               "rumeurs_crues": memoire["rumeur"], "rumeurs_doutees": memoire["parole_doutee"],
               "mefiances": mefiances, "jets": monde.data["jets"],
               # Laisser passer (``passage``) : pas de côté, demandes de passage, poussées.
               "ecarts": sum("s'écarte pour laisser passer" in c["texte"] for c in chronique),
               "passages_demandes": sum(" demande à " in c["texte"] and "laisser passer" in c["texte"]
                                        for c in chronique),
               "poussees": sum(" pousse " in c["texte"] for c in chronique),
               # L'ouïe : se retourner au bruit, retenir un bruit inconnu, aller le voir.
               "retournements": sum(c["texte"].endswith("se retourne au bruit.") for c in chronique),
               "bruits_inconnus": sum(" entend un bruit : " in c["texte"] for c in chronique),
               "alles_voir": sum(" va voir d'où venait le bruit : " in c["texte"] for c in chronique),
               # Les paroles entendues sans en être le destinataire (``social.retenir_parole``).
               "paroles_surprises": sum(" surprend les mots " in c["texte"] for c in chronique),
               # Chercher quelqu'un sans le voir : l'appeler, et qui répond (``pnj.appeler``).
               "appels": sum(" appelle : « " in c["texte"] for c in chronique),
               "reponses": sum(" répond : « " in c["texte"] for c in chronique),
               # Qui a répondu attend d'être rejoint (``deliberation.attendre``) : rejoint, ou en vain.
               "retrouvailles": sum(c.get("nature") == "reponse" and " retrouve " in c["texte"] for c in chronique),
               "attentes_vaines": sum(c.get("nature") == "reponse" and " cesse d'attendre " in c["texte"]
                                      for c in chronique),
               "minutes_a_attendre": attendre_rejoint,
               # L'argent et les prêts (``biens``) : achats conclus, refus de vendre, pièces payées,
               # prêts et objets rendus, bourses prises par un autre que leur propriétaire.
               "achats": sum(" achète " in c["texte"] and c["texte"].endswith("(vendu).") for c in chronique),
               "refus_de_vente": sum(" achète " in c["texte"] and not c["texte"].endswith("(vendu).")
                                     for c in chronique),
               "pieces_payees": sum(s["prix"] for id in pnjs(monde) for s in lire(monde, id)["memoire"]
                                    if s["type"] == "vente"),
               "prets": memoire["pret"], "rendus": sum(c["texte"].endswith("(rendu).") for c in chronique),
               "vols_de_bourse": _vols_de_bourse(monde, chronique),
               **{"stratege_" + k: v for k, v in sorted(bilan.items())}}
    if active(monde):
        # La crue : minutes passées dans l'eau (PNJ × minutes), feux noyés, état de chacun à la fin.
        mesures.update(minutes_dans_l_eau=mouilles,
                       feux_noyes=sum("eteint" in h for h in monde.data["crue"]["historique"]),
                       trempes_fin=sum(1 for id in vivants if monde.objets[id]["corps"]["trempe"]),
                       au_sec_fin=sum(1 for id in vivants if not profondeur(monde, lieu(monde, id))))
    if empreintes is not None:
        empreintes.update({str(k): v for k, v in sorted(releves.items())}, issue=issue(monde, chronique))
    return chronique, mesures


def _vols_de_bourse(monde, chronique):
    """Les fois qu'un PNJ prend un objet à pièces (une bourse, une paie) qui n'est pas à lui."""
    from .francais import designer
    from .vol import proprietaire
    bourses = {k: (designer(o, debut=False), proprietaire(monde, o)) for k, o in monde.objets.items() if "pieces" in o}
    return sum(1 for c in chronique for nom, a in bourses.values()
               if c["pnj"] != a and c["texte"].endswith(" prend " + nom + "."))


def appelant(connexion="chatgpt", modele=None, effort="medium"):
    """Luna en stratège, par la même connexion que le MJ du jeu."""
    from .config import charger_env
    from .mj import MJOpenAI
    charger_env()
    return MJOpenAI(modele, effort, timeout=90, connexion=connexion)._appeler_brut


def resume_diagnostic(recherches):
    """Les recherches du planificateur regroupées par PNJ et par but, les plus coûteuses d'abord :
    nombre, issues (plan, borne de nœuds atteinte, espace épuisé, plan trouvé mais il endure plutôt
    que d'y aller), résultats repris de la mémoire sans chercher, nœuds, profondeur, durée."""
    groupes = {}
    for r in recherches:
        g = groupes.setdefault((r["pnj"], r["but"]), {"pnj": r["pnj"], "but": r["but"], "recherches": 0, "plan": 0,
                                                      "borne": 0, "epuise": 0, "endure": 0, "memoire": 0, "noeuds": 0, "noeuds_max": 0,
                                                      "profondeur_max": 0, "duree": 0.0})
        g["recherches"] += 1
        g[r["issue"]] += 1
        g["memoire"] += bool(r.get("memoire"))
        g["noeuds"] += r["noeuds"]
        g["noeuds_max"] = max(g["noeuds_max"], r["noeuds"])
        g["profondeur_max"] = max(g["profondeur_max"], r["profondeur"])
        g["duree"] += r["duree"]
    lignes = sorted(groupes.values(), key=lambda g: (-g["duree"], g["pnj"], g["but"]))
    for g in lignes:
        g["duree"] = round(g["duree"], 3)
    return lignes


def texte_diagnostic(resume):
    cles = ("recherches", "plan", "borne", "epuise", "endure", "memoire", "noeuds", "noeuds_max", "profondeur_max", "duree")
    lignes = ["Planificateur : pnj but " + " ".join(cles)]
    lignes += [f'{g["pnj"]} {g["but"] or "-"} ' + " ".join(str(g[k]) for k in cles) for g in resume]
    total = {k: sum(g[k] for g in resume) for k in cles if k not in ("noeuds_max", "profondeur_max")}
    lignes.append("total " + " ".join(f"{k} {round(v, 3)}" for k, v in total.items()))
    return "\n".join(lignes)


def page_rejeu(rejeu, graine, plusieurs):
    """Où écrire la page d'une nuit : le fichier donné ; pour plusieurs graines, un fichier par graine
    (``page.html`` donne ``page_<graine>.html``, un dossier donne ``rejeu_<graine>.html``)."""
    from pathlib import Path
    if not plusieurs:
        return rejeu
    chemin = Path(rejeu)
    if chemin.suffix == ".html":
        return str(chemin.with_name(f"{chemin.stem}_{graine}.html"))
    chemin.mkdir(parents=True, exist_ok=True)
    return str(chemin / f"rejeu_{graine}.html")


def ecrire_rejeu(chemin, enregistreur, monde, chronique, titre):
    from .rejeu import page
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(page(enregistreur.donnees(monde, chronique, titre)))


def nuit(scenario, graine, heures, joueur, chronique=False, diagnostic=False, rejeu=None, depart="tire"):
    """Une nuit sans joueur : (texte imprimable, mesures, données pour --sortie). Avec ``rejeu``
    (un chemin), la page de rejeu y est écrite. Les données portent les empreintes de la nuit
    (``executer``) et sa durée de calcul."""
    from contextlib import nullcontext
    import time
    from .planification import diagnostics
    debut = time.perf_counter()
    monde = creer(scenario, graine, depart)
    if joueur:
        from .geometrie import position_entree
        monde.joueur.update(salle=joueur, position=list(position_entree(monde, joueur)))
    from .recit_pnj import Recit
    recit = Recit(monde)
    if rejeu:
        from .rejeu import Enregistreur
        enregistreur = Enregistreur(monde)
    with diagnostics() as recherches, enregistreur.observer() if rejeu else nullcontext():
        empreintes = {}
        pas, mesures = executer(monde, int(heures * 60), recit, empreintes)
    secondes = round(time.perf_counter() - debut, 2)
    if rejeu:
        ecrire_rejeu(rejeu, enregistreur, monde, pas, f"Rejeu : {scenario}, graine {graine}, {heures:g} h")
    lignes = [f'[{c["minute"]:>4} min] {c["texte"]}' for c in pas] + [""] if chronique else []
    lignes += [recit.texte(monde, pas), ""]
    for id in pnjs(monde):
        e = lire(monde, id)
        besoins = ", ".join(f"{k} {v:.0f}" for k, v in e["besoins"].items())
        but = e["intention"]["but"] if e["intention"] else None
        lignes.append(f'{monde.objets[id]["nom"]} : {besoins or "sans profil"} ; intention : {but}')
    lignes.append("Mesures : " + ", ".join(f"{k} {v}" for k, v in mesures.items()))
    donnees = {"graine": graine, "heures": heures, "depart": depart, "empreintes": empreintes, "secondes": secondes,
               "chronique": pas, "mesures": mesures,
               "recit": recit.donnees(monde, pas), "souvenirs": {id: lire(monde, id)["memoire"] for id in pnjs(monde)}}
    if diagnostic:
        resume = resume_diagnostic(recherches)
        lignes.append(texte_diagnostic(resume))
        donnees["diagnostic"] = {"resume": resume, "recherches": recherches}
    return "\n".join(lignes), mesures, donnees


def _nuit(arguments):
    return nuit(*arguments)


def nuits(scenario, graines, heures, joueur, chronique=False, diagnostic=False, rejeu=None, depart="tire"):
    """Plusieurs nuits en parallèle, une par processus ; les résultats dans l'ordre des graines.
    Avec ``rejeu``, une page par graine (``page_rejeu``)."""
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=min(len(graines), 16)) as pool:
        return list(pool.map(_nuit, [(scenario, g, heures, joueur, chronique, diagnostic,
                                      page_rejeu(rejeu, g, True) if rejeu else None, depart) for g in graines]))


def divergence(donnees):
    """Combien de nuits distinctes sur ce lot de graines : empreintes différentes à chaque minute
    repère atteinte, issues différentes ; puis le temps de calcul moyen d'une nuit."""
    reperes = [k for k in donnees[0]["empreintes"] if k != "issue"]
    lignes = [f"Nuits distinctes sur {len(donnees)} graines : " + ", ".join(
        f"{k} min {len({d['empreintes'][k] for d in donnees if k in d['empreintes']})}" for k in reperes)
        + f", issues {len({d['empreintes']['issue'] for d in donnees})}"]
    lignes.append(f"Temps de calcul : {sum(d['secondes'] for d in donnees) / len(donnees):.1f} s par nuit en moyenne")
    return "\n".join(lignes)


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
    parser.add_argument("--scenario", choices=("relais", "crue", "crypte", "mine", "auberge"), default="relais")
    parser.add_argument("--heures", type=float, default=3)
    parser.add_argument("--joueur", help="salle où le joueur reste passif")
    parser.add_argument("--graine", type=int, default=1985)
    parser.add_argument("--graines", type=int, nargs="+", help="plusieurs nuits en parallèle, sans stratège")
    parser.add_argument("--stratege", action="store_true", help="Luna conseille les PNJ (appels plafonnés)")
    parser.add_argument("--connexion", choices=("chatgpt", "api"), default="chatgpt")
    parser.add_argument("--sortie", help="fichier JSON où écrire chronique, récit et mesures")
    parser.add_argument("--chronique", action="store_true", help="imprime aussi chaque pas")
    parser.add_argument("--rejeu", help="page HTML où rejouer la nuit (positions, regards, lumière, bruits, buts, croyances) ; "
                                        "avec --graines, une page par graine (page_<graine>.html, ou un dossier)")
    parser.add_argument("--depart", choices=("tire", "fixe"), default="tire",
                        help="départ tiré de la graine dans les bornes du scénario (défaut), ou départ déclaré")
    parser.add_argument("--diagnostic", action="store_true",
                        help="mesure chaque recherche du planificateur (nœuds, durée, issue), par PNJ et par but")
    args = parser.parse_args(argv)
    if args.graines:
        if args.stratege:
            parser.error("le stratège suit une nuit à la fois : --graine, pas --graines")
        resultats = nuits(args.scenario, args.graines, args.heures, args.joueur, args.chronique, args.diagnostic,
                          args.rejeu, args.depart)
        for g, (texte, _, _) in zip(args.graines, resultats):
            print(f"######## graine {g}\n{texte}\n")
            if args.rejeu:
                print("Rejeu :", page_rejeu(args.rejeu, g, True))
        print(tableau(args.graines, [m for _, m, _ in resultats]))
        print(divergence([d for _, _, d in resultats]))
        if args.sortie:
            with open(args.sortie, "w", encoding="utf-8") as f:
                json.dump([d for _, _, d in resultats], f, ensure_ascii=False, indent=1)
        return 0
    from . import stratege
    from .planification import diagnostics
    stratege.activer(appelant(args.connexion) if args.stratege else None)
    try:
        monde = creer(args.scenario, args.graine, args.depart)
        if args.joueur:
            from .geometrie import position_entree
            monde.joueur.update(salle=args.joueur, position=list(position_entree(monde, args.joueur)))
        from .recit_pnj import Recit
        recit = Recit(monde)
        from contextlib import nullcontext
        from .rejeu import Enregistreur
        enregistreur = Enregistreur(monde) if args.rejeu else None
        with diagnostics() as recherches, enregistreur.observer() if enregistreur else nullcontext():
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
        ecrire_rejeu(args.rejeu, enregistreur, monde, chronique,
                     f"Rejeu : {args.scenario}, graine {args.graine}, {args.heures:g} h")
        print("Rejeu :", args.rejeu)
    diagnostic = None
    if args.diagnostic:
        diagnostic = {"resume": resume_diagnostic(recherches), "recherches": recherches}
        print(texte_diagnostic(diagnostic["resume"]))
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8") as f:
            json.dump({"graine": args.graine, "heures": args.heures, "stratege": args.stratege,
                       "chronique": chronique, "mesures": mesures, "recit": recit.donnees(monde, chronique),
                       "souvenirs": {id: lire(monde, id)["memoire"] for id in pnjs(monde)},
                       **({"diagnostic": diagnostic} if diagnostic else {})},
                      f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
