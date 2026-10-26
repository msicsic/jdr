"""Prototype isolé du lot 92 c : compléter un graphe d'absence en largeur."""
import copy
import json
from collections import deque


def prouver(p, original, depart, but, vises, profondeur, faute, tenir, graphes, voir):
    stats = {"ajoutes": 0, "completes": 0, "enrichis": 0, "visites": 0}
    prives = {}

    def parcours(nom, sombre):
        v = p.Vue(original.monde, original.id)
        for a in ("degat", "seul", "emplois", "eclairer", "motif", "desespere"):
            setattr(v, a, getattr(original, a))
        # Tables pures de la même photographie ; les découvertes et gestes restent privés.
        for a in ("_contextes_routes", "_contextes_pressions", "_parcours", "_routes", "_allers",
                  "_approches", "_contacts", "_locaux", "_moyennes", "_effets_routes",
                  "_tarifs_routes", "_mesures_allers"):
            setattr(v, a, getattr(original, a))
        v._depart_estimation = depart
        v._contexte_parts = (but, json.dumps(vises, sort_keys=True, ensure_ascii=False))
        v._explore_furtif = original._explore_furtif
        v._decouvrir_discretion = True
        v._lumiere_lue = not sombre
        v.agissables(vises or {})
        g = {}
        for e, noeud in graphes.get(nom, {}).items():
            n = list(noeud)
            if n[3] is not None:
                n[3] = [copy.copy(s) if isinstance(s, p.SuiteDifferee) else s for s in n[3]]
            g[e] = n
        prives[nom] = g
        departs = p._departs(v, depart)
        file, vus, lue = deque((e, 0) for e in departs), set(departs), False
        while file:
            if stats["visites"] >= p.PREUVE_MAX:
                return False, "borne", lue
            e, profondeur_e = file.popleft()
            stats["visites"] += 1
            v._lumiere_lue = not sombre
            v._discretion_lue = v._explore_furtif
            noeud = g.get(e)
            neuf = noeud is None
            if neuf:
                noeud = [but(v, e) and (e.allure == 15 or e.fait("furtif")), None, None, None, False]
                if sombre and v._lumiere_lue:
                    noeud[4] = "but"
                g[e] = noeud
                stats["ajoutes"] += 1
                stats["enrichis"] += 1
            if v._discretion_lue and not v._explore_furtif:
                return False, "discretion", lue
            if noeud[4] == "but":
                lue = True
                continue
            if noeud[0] and not (tenir and e.salle in v.menacees):
                return False, "but", lue
            if profondeur_e >= profondeur:
                continue
            if noeud[4] == "gestes":
                lue = True
                continue
            if noeud[3] is None:
                noeud[2] = sum(1 for k in e.portes if e.fait("allume", k))
                noeud[3] = p._suites(v, e, vises, but)
                stats["completes"] += 1
                stats["enrichis"] += not neuf
            suites = []
            for s in noeud[3]:
                suites.extend(s.developper(v) if isinstance(s, p.SuiteDifferee) else [s])
            if v._discretion_lue and not v._explore_furtif:
                return False, "discretion", lue
            if sombre and v._lumiere_lue:
                noeud[4] = "gestes"
                lue = True
                continue
            for fautes, _, _, suivant, *_ in suites:
                if fautes and faute is None:
                    continue
                if suivant.fait("estimation"):
                    if ((suivant.allure == 15 or suivant.fait("furtif"))
                            and not (tenir and suivant.salle in v.menacees)):
                        return False, "but", lue
                    continue
                if suivant in vus:
                    continue
                vus.add(suivant)
                file.append((suivant, profondeur_e + 1))
        return True, "epuise", lue

    if voir:
        prouve, issue, _ = parcours("lumiere", False)
    else:
        prouve, issue, lue = parcours("sombre", True)
        if prouve and lue:
            prouve, issue, _ = parcours("lumiere", False)
    return prouve, issue, stats, prives
