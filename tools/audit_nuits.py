"""Audit des nuits sans joueur : jouer beaucoup de nuits avec les contrôles, puis chercher les défauts.

    python tools/audit_nuits.py jouer --scenarios relais mine auberge crue --graines 1 2 3 --heures 12 \
        --dossier artifacts/audit-nuits --processus 10 --verifier --verification 0.2 [--rejeu]
    python tools/audit_nuits.py analyser --dossier artifacts/audit-nuits [--sortie rapport.json]

``jouer`` joue chaque nuit par ``banc_pnj.nuit`` (le moteur réel, ``Monde.verifier`` à chaque pas),
avec ``planification.VERIFIER`` et ``spatial.VERIFICATION`` posés dans chaque processus ; une nuit
qui plante est consignée (trace, minute, fin de la chronique) sans arrêter les autres. Toutes les cinq
minutes, un relevé par PNJ : salle, case, but, besoins qui pressent, noir, eau, et les croyances de
lieu ou d'ouverture fausses sur ce qu'il perçoit en ce moment. Une nuit = un fichier
``<scenario>_<graine>.json.gz`` (données du banc, relevés, état final des dettes, prêts et
engagements, gestes illicites du rejeu).

``analyser`` relit ces fichiers et cherche : plantages, gestes ou demandes répétés en boucle,
va-et-vient entre deux salles ou deux buts, PNJ figés avec un besoin qui presse, croyances fausses sur
ce qu'on voit, appels sans réponse, gestes illicites jamais vus, minutes dans le noir ou l'eau, dettes
et engagements non soldés. Observation seule : les relevés ne changent pas la nuit (empreintes).
"""
import argparse
import gzip
import json
import os
import re
import sys
import traceback
from collections import Counter, defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

JOUEURS = {"relais": "chambre_cloche", "mine": "galerie", "auberge": "dortoir", "crue": "chambre_cloche"}

# --------------------------------------------------------------------------------------------
# Jouer


def _releve(monde):
    """Un relevé de chaque PNJ vivant à cet instant (lecture seule)."""
    from donjon.deliberation import autour, peur_du_noir, seuils, urgents
    from donjon.eau import active, profondeur
    from donjon.esprits import lire, percus, pnjs
    from donjon.recit_pnj import but_en_mots
    pnj_releves = {}
    for id in pnjs(monde):
        o = monde.objets[id]
        if not o.get("profil"):
            continue
        e = lire(monde, id)
        i = e["intention"]
        faux = []
        if o["lieu"] in monde.data["salles"]:
            vus, _ = percus(monde, id)
            for sujet in vus:
                c = e["croyances"].get(sujet, {})
                reel = monde.objets.get(sujet)
                if reel is None:
                    continue
                cl = c.get("lieu")
                if cl is not None and reel.get("lieu") is not None and cl["valeur"] != reel["lieu"]:
                    faux.append([sujet, "lieu", cl["valeur"], reel["lieu"], cl["source"], cl["minute"]])
                ce = c.get("etat")
                if ce is not None and "ouverte" in ce["valeur"] and "ouverte" in reel \
                        and bool(ce["valeur"]["ouverte"]) != bool(reel["ouverte"]):
                    faux.append([sujet, "ouverte", ce["valeur"]["ouverte"], reel["ouverte"], ce["source"], ce["minute"]])
        s = seuils(monde, id)
        pnj_releves[id] = {
            "s": o["lieu"], "p": o.get("position"),
            "b": but_en_mots(monde, i["but"]) if i else None, "bt": i["but"]["type"] if i else None,
            "mo": i["motif"] if i else None, "pl": len(i["plan"]) if i else 0,
            "u": urgents(monde, id), "bes": {k: round(v) for k, v in e["besoins"].items() if k in s and v >= s[k] - 5},
            "noir": bool(peur_du_noir(monde, id) and o["lieu"] in monde.data["salles"] and not autour(monde, id)["lumiere"]),
            "eau": profondeur(monde, o["lieu"]) if active(monde) and o["lieu"] in monde.data["salles"] else 0,
            "corps": {k: v for k, v in (o.get("corps") or {}).items() if isinstance(v, (int, float, bool))},
            "faux": faux, "eng": len(e["engagements"]), "rej": e["rejoint"]["qui"] if e["rejoint"] else None,
        }
    return {"m": monde.data["minutes"], "pnj": pnj_releves,
            "dettes": len(monde.data.get("dettes", []) or []),
            "gestes": len(monde.data.get("gestes_en_cours", []) or [])}


def _final(monde):
    """Ce qui reste dû à la fin : dettes, prêts, engagements, attentes, renoncements."""
    from donjon.esprits import lire, pnjs
    return {"minute": monde.data["minutes"],
            "dettes": monde.data.get("dettes"), "permissions": monde.data.get("permissions"),
            "engagements": {id: lire(monde, id)["engagements"] for id in pnjs(monde) if lire(monde, id)["engagements"]},
            "rejoint": {id: lire(monde, id)["rejoint"] for id in pnjs(monde) if lire(monde, id)["rejoint"]},
            "renoncements": {id: lire(monde, id)["renoncements"] for id in pnjs(monde) if lire(monde, id)["renoncements"]},
            "urgences": {id: lire(monde, id)["urgences"] for id in pnjs(monde)},
            "pulsions": {id: lire(monde, id)["pulsions"] for id in pnjs(monde)},
            "noms": {id: monde.objets[id]["nom"] for id in pnjs(monde)}}


def _initialiser(verifier, verification):
    from donjon import planification, spatial
    planification.VERIFIER = verifier
    spatial.VERIFICATION = verification


# Écarts de ``planification.VERIFIER`` relevés sans arrêter la nuit (``--verifier-continu``).
ECARTS = []
# Nœuds de la recherche de référence quand celle du contrôle a atteint sa borne.
GRANDE_BORNE = 60000
ECARTS_EVALUES = 25


def _verifier_continu():
    """``planification.VERIFIER`` reste vrai ; un écart (AssertionError) est noté avec ce que la
    recherche de contrôle avait examiné (a-t-elle atteint la borne de nœuds ?) et, pour les premiers,
    l'optimum d'une recherche complète à grande borne. Puis la même recherche est rejouée sans le
    contrôle : la mémoire du planificateur rend le résultat déjà gardé, la nuit continue telle quelle."""
    from donjon import planification as P
    chercher, explorer = P.chercher, P._explorer
    dernier = {}

    def _explorer(v, depart_, but, vises, profondeur, noeuds, faute, tenir=False, graphe=None):
        r = explorer(v, depart_, but, vises, profondeur, noeuds, faute, tenir, graphe)
        dernier.update(args=(v, depart_, but, vises, profondeur, noeuds, faute, tenir), r=r)
        return r

    def _chercher(monde, id, but, *a, **k):
        dernier.clear()
        try:
            return chercher(monde, id, but, *a, **k)
        except AssertionError as erreur:
            if not str(erreur).startswith("Recherche de "):
                raise
            v, depart_, but_, vises, profondeur, noeuds, faute, tenir = dernier["args"]
            examines = dernier["r"][1]
            ecart = {"minute": monde.data["minutes"], "pnj": id, "message": str(erreur)[:600],
                     "borne_atteinte": examines >= noeuds, "examines": examines, "noeuds": noeuds}
            if len(ECARTS) < ECARTS_EVALUES:
                complet = explorer(v, depart_, but_, vises, profondeur, GRANDE_BORNE, faute, tenir)
                ecart.update(optimum=None if complet[0] is None else complet[0][0], optimum_examines=complet[1],
                             optimum_etapes=None if complet[0] is None else [
                                 f'{e["operation"]} {e["cible"] or e["lieu"]} {e["outil"]}'.strip() for e in complet[0][1]])
            ECARTS.append(ecart)
            P.VERIFIER = False
            try:
                trouve = chercher(monde, id, but, *a, **k)
            finally:
                P.VERIFIER = True
            ecart["retenu"] = None if trouve is None else trouve[0]
            ecart["retenu_etapes"] = None if trouve is None else [
                f'{e["operation"]} {e["cible"] or e["lieu"]} {e["outil"]}'.strip() for e in trouve[1]]
            return trouve
    P.chercher, P._explorer = _chercher, _explorer


def jouer_nuit(arguments):
    """Une nuit, instrumentée ; renvoie (scenario, graine, chemin, résumé)."""
    scenario, graine, heures, dossier, rejeu, releves_actifs, depart, continu = arguments
    from donjon import banc_pnj
    import time
    if continu:
        from donjon import planification
        if planification.chercher.__name__ != "_chercher":
            _verifier_continu()
        ECARTS.clear()
    capture = {}
    creer, oisifs, ecrire = banc_pnj.creer, banc_pnj._oisifs_urgents, banc_pnj.ecrire_rejeu
    releves = []

    def _creer(*a, **k):
        capture["monde"] = creer(*a, **k)
        return capture["monde"]

    def _oisifs(monde):
        if releves_actifs:
            releves.append(_releve(monde))
        return oisifs(monde)

    def _ecrire(chemin, enregistreur, monde, chronique, titre):
        capture["gestes"] = enregistreur.gestes
        if rejeu:
            ecrire(chemin, enregistreur, monde, chronique, titre)

    banc_pnj.creer, banc_pnj._oisifs_urgents, banc_pnj.ecrire_rejeu = _creer, _oisifs, _ecrire
    page = str(Path(dossier) / f"rejeu_{scenario}_{graine}.html")
    debut = time.perf_counter()
    resultat = {"scenario": scenario, "graine": graine, "heures": heures, "depart": depart}
    try:
        _, mesures, donnees = banc_pnj.nuit(scenario, graine, heures, JOUEURS[scenario], False, False, page, depart)
        resultat.update(donnees=donnees, plantage=None)
    except Exception as erreur:  # une nuit qui plante est consignée, les autres continuent
        monde = capture.get("monde")
        resultat.update(donnees=None, plantage={
            "type": type(erreur).__name__, "message": str(erreur)[:2000], "trace": traceback.format_exc()[-6000:],
            "minute": monde.data["minutes"] if monde else None,
            "dixiemes": monde.data.get("dixiemes") if monde else None,
            "chronique": (monde.data.get("chronique", [])[-60:] if monde else [])})
    finally:
        banc_pnj.creer, banc_pnj._oisifs_urgents, banc_pnj.ecrire_rejeu = creer, oisifs, ecrire
    monde = capture.get("monde")
    resultat["secondes"] = round(time.perf_counter() - debut, 1)
    resultat["releves"] = releves
    resultat["gestes"] = capture.get("gestes")
    resultat["ecarts_verifier"] = list(ECARTS)
    if monde is not None:
        try:
            resultat["final"] = _final(monde)
        except Exception:
            resultat["final"] = {"erreur": traceback.format_exc()[-2000:]}
    chemin = Path(dossier) / f"{scenario}_{graine}.json.gz"
    with gzip.open(chemin, "wt", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False)
    p = resultat["plantage"]
    return scenario, graine, str(chemin), resultat["secondes"], (p["type"] + ": " + p["message"][:200] if p else None)


def jouer(args):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from donjon.banc_pnj import ceder
    ceder()
    Path(args.dossier).mkdir(parents=True, exist_ok=True)
    if args.verifier_continu:
        args.verifier = True
    taches = [(s, g, args.heures, args.dossier, args.rejeu, not args.sans_releves, args.depart, args.verifier_continu)
              for s in args.scenarios for g in args.graines
              if args.refaire or not (Path(args.dossier) / f"{s}_{g}.json.gz").exists()]
    print(f"{len(taches)} nuits à jouer", flush=True)
    with ProcessPoolExecutor(max_workers=args.processus, initializer=_initialiser,
                             initargs=(args.verifier, args.verification)) as pool:
        futurs = [pool.submit(jouer_nuit, t) for t in taches]
        for f in as_completed(futurs):
            scenario, graine, chemin, secondes, plantage = f.result()
            print(f"{scenario} {graine} {secondes} s" + (f" PLANTAGE {plantage}" if plantage else ""), flush=True)
    return 0


# --------------------------------------------------------------------------------------------
# Analyser

# Textes de la chronique qui ne sont pas des décisions (perception, marche) : écartés des boucles.
_BRUIT = re.compile(r"se retourne au bruit|entend un bruit|passe dans :|se tourne vers la voix|surprend les mots"
                    r"|s'acharne sur la serrure|reste près d'|se chauffe près|s'écarte pour laisser passer")


def _norme(texte):
    return re.sub(r"\d+", "#", texte)


def charger(dossier):
    for chemin in sorted(Path(dossier).glob("*.json.gz")):
        with gzip.open(chemin, "rt", encoding="utf-8") as f:
            yield json.load(f)


def _plages(minutes, pas=5):
    """Plages contiguës d'une suite croissante de minutes : [(début, fin)]."""
    plages = []
    for m in minutes:
        if plages and m - plages[-1][1] <= pas:
            plages[-1][1] = m
        else:
            plages.append([m, m])
    return plages


def analyser_nuit(n):
    """Les constats d'une nuit : une liste de {code, pnj, minute, detail, poids}."""
    constats = []
    cle = f'{n["scenario"]} {n["graine"]}'

    def noter(code, pnj, minute, detail, poids=1):
        constats.append({"code": code, "nuit": cle, "scenario": n["scenario"], "graine": n["graine"],
                         "pnj": pnj, "minute": minute, "detail": detail, "poids": poids})
    if n.get("plantage"):
        p = n["plantage"]
        noter("plantage", None, p.get("minute"), f'{p["type"]}: {p["message"][:300]}')
    d = n.get("donnees") or {}
    chronique = d.get("chronique", [])
    noms = (n.get("final") or {}).get("noms", {})
    heures = n["heures"]

    # 1. Répétitions : même texte de décision (hors perception), par PNJ.
    repetes = Counter((c["pnj"], _norme(c["texte"])) for c in chronique
                      if c.get("nature") != "ouie" and not _BRUIT.search(c["texte"]))
    for (pnj, texte), k in repetes.items():
        if k >= max(8, 2 * heures):
            premiere = next(c["minute"] for c in chronique if c["pnj"] == pnj and _norme(c["texte"]) == texte)
            noter("repetition", pnj, premiere, f"{k}× « {texte} »", k)
    # Échanges sociaux qui échouent en boucle : même demandeur, même texte hors issue.
    def _issue(texte):
        trouve = re.search(r"\(([^)]*)\)\.$", texte)
        return trouve.group(1) if trouve else None
    sociaux = Counter((c["pnj"], _norme(re.sub(r"\s*\([^)]*\)\.$", "", c["texte"])), _issue(c["texte"]))
                      for c in chronique if c.get("nature") == "social")
    for (pnj, texte, issue), k in sociaux.items():
        if k >= 6 and issue is not None and issue not in ("accepte", "promis", "vendu", "rendu", "donne"):
            noter("demande_en_boucle", pnj, None, f"{k}× « {texte} » ({issue})", k)

    # 2. Appels : appels d'un PNJ, réponses.
    appels = defaultdict(list)
    for c in chronique:
        if " appelle : « " in c["texte"]:
            appels[c["pnj"]].append(c["minute"])
    for pnj, ms in appels.items():
        if len(ms) >= 10:
            noter("appels_nombreux", pnj, ms[0], f"{len(ms)} appels ({ms[:6]}…)", len(ms))
    aides = Counter(c["pnj"] for c in chronique if c["texte"].endswith(" appelle à l'aide."))
    for pnj, k in aides.items():
        if k >= 10:
            noter("appels_a_l_aide", pnj, None, f"{k} appels à l'aide", k)

    # 3. Relevés : va-et-vient, figé avec un besoin qui presse, noir, eau, croyances fausses.
    releves = n.get("releves") or []
    par_pnj = defaultdict(list)
    for r in releves:
        for pnj, x in r["pnj"].items():
            par_pnj[pnj].append((r["m"], x))
    for pnj, suite in par_pnj.items():
        salles = [x["s"] for _, x in suite]
        # Va-et-vient : A B A B… sur des relevés successifs, la plus longue série.
        meilleur, courant, debut_m, ou = 0, 0, None, None
        for k in range(2, len(salles)):
            if salles[k] == salles[k - 2] and salles[k] != salles[k - 1]:
                courant += 1
                if courant > meilleur:
                    meilleur, debut_m, ou = courant, suite[k - courant - 1][0], (salles[k - 1], salles[k])
            else:
                courant = 0
        if meilleur >= 6:
            noter("va_et_vient", pnj, debut_m, f"{meilleur + 2} relevés alternés {ou[0]} ↔ {ou[1]}", meilleur)
        # Changements de salle par heure.
        changements = sum(1 for k in range(1, len(salles)) if salles[k] != salles[k - 1])
        # Buts alternés : A B A B sur les buts (en mots) successifs distincts.
        buts = []
        for m, x in suite:
            if x["b"] and (not buts or buts[-1][1] != x["b"]):
                buts.append((m, x["b"]))
        alternances = sum(1 for k in range(2, len(buts)) if buts[k][1] == buts[k - 2][1])
        if alternances >= 10:
            paires = Counter(tuple(sorted((buts[k][1], buts[k - 1][1]))) for k in range(2, len(buts)) if buts[k][1] == buts[k - 2][1])
            noter("buts_alternes", pnj, buts[0][0], f"{alternances} alternances, surtout {paires.most_common(1)[0]}", alternances)
        # Figé : sans intention, un besoin qui presse, longtemps.
        fige = [m for m, x in suite if x["u"] and x["b"] is None]
        for a, b in _plages(fige):
            if b - a >= 120:
                besoins = Counter(u for m, x in suite if a <= m <= b for u in x["u"])
                noter("fige_presse", pnj, a, f"{b - a + 5} min sans but, pressé par {dict(besoins)}", (b - a) // 60)
        # Même but et même case longtemps alors qu'un autre besoin presse (le but ne le sert pas).
        immobile = []
        for m, x in suite:
            if x["b"] and x["u"] and x["mo"] not in x["u"]:
                immobile.append(m)
        for a, b in _plages(immobile):
            if b - a >= 180:
                exemple = next(x for m, x in suite if m == a)
                noter("but_hors_besoin", pnj, a, f"{b - a + 5} min à « {exemple['b']} » ({exemple['mo']}) "
                                                 f"alors que presse {exemple['u']}", (b - a) // 60)
        # Noir craint, eau.
        noir = [m for m, x in suite if x["noir"]]
        for a, b in _plages(noir):
            if b - a >= 90:
                ex = next(x for m, x in suite if m == a)
                noter("noir_long", pnj, a, f"{b - a + 5} min dans le noir qu'il craint ({ex['s']}, but {ex['b']})", (b - a) // 60)
        eau = [m for m, x in suite if x["eau"]]
        for a, b in _plages(eau):
            if b - a >= 60:
                ex = next(x for m, x in suite if m == a)
                noter("eau_longue", pnj, a, f"{b - a + 5} min dans l'eau ({ex['s']}, {ex['eau']} cm, but {ex['b']})", (b - a) // 60)
        # Croyances fausses sur ce qu'il perçoit, persistantes (deux relevés de suite au moins).
        faux = defaultdict(list)
        for m, x in suite:
            for f in x["faux"]:
                faux[(f[0], f[1], str(f[2]), str(f[3]))].append(m)
        for (sujet, attribut, cru, reel), ms in faux.items():
            for a, b in _plages(ms):
                if b > a:
                    noter("croyance_fausse_vue", pnj, a, f"{sujet}.{attribut} cru {cru}, réel {reel}, perçu {b - a + 5} min", 1)
        n_changements = changements
        if heures and n_changements / heures >= 12:
            noter("agitation", pnj, None, f"{n_changements} changements de salle ({n_changements / heures:.1f}/h)", n_changements)

    # 4. Gestes illicites : jamais vus de personne (registre du rejeu), et vols vus sans suite.
    for g in n.get("gestes") or []:
        if not g["temoins"] and g["dans_la_salle"]:
            noter("illicite_sans_temoin_avec_present", g["a"], g["t"] // 600 if isinstance(g["t"], int) else None,
                  f'{g["op"]} {g["objet"]} dans {g["salle"]}, présents {g["dans_la_salle"]}', 1)

    # 5. Fin de nuit : dettes, engagements anciens, prêts.
    f = n.get("final") or {}
    for dette in f.get("dettes") or []:
        noter("dette_fin", None, None, json.dumps(dette, ensure_ascii=False)[:200], 1)
    for pnj, engagements in (f.get("engagements") or {}).items():
        for e in engagements:
            if f["minute"] - e["minute"] >= 240:
                noter("engagement_ancien", pnj, e["minute"], json.dumps(e, ensure_ascii=False)[:200], 1)
    return constats


def analyser(args):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    tous, nuits, plantages = [], [], []
    for n in charger(args.dossier):
        nuits.append((n["scenario"], n["graine"], n.get("secondes"), (n.get("donnees") or {}).get("mesures")))
        if n.get("plantage"):
            plantages.append(n)
        tous += analyser_nuit(n)
    total = Counter(s for s, *_ in nuits)
    print(f"Nuits : {len(nuits)} ({dict(total)}) ; plantages : {len(plantages)}")
    for p in plantages:
        print(f'  PLANTAGE {p["scenario"]} {p["graine"]} min {p["plantage"]["minute"]} : '
              f'{p["plantage"]["type"]} {p["plantage"]["message"][:300]}')
    par_code = defaultdict(list)
    for c in tous:
        par_code[c["code"]].append(c)
    for code, liste in sorted(par_code.items(), key=lambda kv: -len({c["nuit"] for c in kv[1]})):
        touchees = Counter(c["scenario"] for c in {c["nuit"]: c for c in liste}.values())
        print(f"\n== {code} : {len(liste)} constats, nuits touchées {dict(touchees)}")
        for c in sorted(liste, key=lambda c: -c["poids"])[:args.exemples]:
            print(f'  [{c["nuit"]}] {c["pnj"]} min {c["minute"]} : {c["detail"]}')
    # Mesures moyennes par scénario.
    print()
    for s in total:
        mesures = [m for sc, _, _, m in nuits if sc == s and m]
        if not mesures:
            continue
        cles = [k for k in mesures[0] if isinstance(mesures[0][k], (int, float))]
        print(s, ", ".join(f"{k} {sum(m.get(k, 0) for m in mesures) / len(mesures):g}" for k in cles))
        print(s, "secondes", round(sum(sec or 0 for sc, _, sec, _ in nuits if sc == s) / total[s], 1))
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8") as f:
            json.dump(tous, f, ensure_ascii=False, indent=1)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sous = parser.add_subparsers(dest="commande", required=True)
    j = sous.add_parser("jouer")
    j.add_argument("--scenarios", nargs="+", default=list(JOUEURS), choices=list(JOUEURS))
    j.add_argument("--graines", type=int, nargs="+", required=True)
    j.add_argument("--heures", type=float, default=12)
    j.add_argument("--dossier", default="artifacts/audit-nuits")
    j.add_argument("--processus", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    j.add_argument("--verifier", action="store_true", help="planification.VERIFIER")
    j.add_argument("--verifier-continu", action="store_true",
                   help="VERIFIER, mais un écart est noté (borne atteinte ou non, optimum complet) sans arrêter la nuit")
    j.add_argument("--verification", type=float, default=0.0, help="spatial.VERIFICATION (part des lectures recomparées)")
    j.add_argument("--rejeu", action="store_true", help="écrit aussi la page de rejeu de chaque nuit")
    j.add_argument("--sans-releves", action="store_true")
    j.add_argument("--refaire", action="store_true", help="rejoue les nuits déjà présentes")
    j.add_argument("--depart", choices=("tire", "fixe"), default="tire")
    a = sous.add_parser("analyser")
    a.add_argument("--dossier", default="artifacts/audit-nuits")
    a.add_argument("--exemples", type=int, default=8)
    a.add_argument("--sortie")
    args = parser.parse_args(argv)
    return jouer(args) if args.commande == "jouer" else analyser(args)


if __name__ == "__main__":
    raise SystemExit(main())
