"""Détecteur générique des changements d'avis et allers-retours de décision des PNJ.

Observe ``deliberation.choisir``, ``deliberation.menager_flamme`` et ``pnj.agir``
sans modifier aucun état du monde, aucun tirage aléatoire ni aucune mémoire du
planificateur. Pour chaque transition de décision d'un PNJ, photographie les
entrées réellement lues par le choix (croyances, paliers de besoins, pulsions
dues, bruits/alarmes/dangers, refus/promesses/engagements/agendas, inventaire et
droits, position propre) et distingue :
- les cycles accomplis (but achevé puis redevenu dû plus tard) ;
- les allers-retours justifiés par une entrée externe nouvelle (bruit, refus,
  feu revu faible, franchissement de seuil d'urgence, etc.) ;
- les allers-retours non justifiés, où le PNJ revient à une décision qu'il vient
  de quitter sans l'avoir accomplie alors qu'aucune entrée externe n'a changé
  (ou qu'elle a été abandonnée sans entrée nouvelle).
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from donjon import agendas, banc_pnj, corps, defense, deliberation, eau, planification, pnj, relations  # noqa: E402
from donjon.esprits import RECENT, lire, pnjs  # noqa: E402
from donjon.temps import MINUTE, instant  # noqa: E402

SCENARIOS_DEFAUT = ("relais", "mine", "auberge", "crue", "crue_hameau")
SALLES_JOUEUR = {
    "relais": "chambre_cloche",
    "mine": "galerie",
    "auberge": "dortoir",
    "crue": "chambre_cloche",
    "crue_hameau": "chambre_cloche",
}
GRAINES_DEFAUT = (1985, 7, 42, 2024)

CATEGORIES_EXTERNES = (
    "croyances_valeurs",
    "besoins_paliers",
    "pulsions_dues",
    "alarmes_et_dangers",
    "social_et_engagements",
    "inventaire_et_droits",
)

SEUILS_FIN = {
    "repos": deliberation.REPOS_FIN,
    "chaleur": deliberation.CHALEUR_FIN,
    "securite": deliberation.SECURITE_FIN,
    "faim": 0,
}


def _canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def _cle_decision(intention):
    """Identité canonique du but d'une intention (None si aucune intention)."""
    if not intention or not intention.get("but"):
        return None
    but = intention["but"]
    if but.get("type") == "agenda":
        return _canon({
            "type": "agenda",
            "agenda": but.get("agenda"),
            "sorte": but.get("sorte"),
            "destination": but.get("destination"),
        })
    return _canon(but)


def _resume_decision(intention):
    if not intention or not intention.get("but"):
        return {"motif": None, "but": None, "cle": None, "tete_plan": None, "nb_etapes": 0}
    plan = intention.get("plan") or []
    tete = None
    if plan:
        e0 = plan[0]
        tete = {k: e0.get(k) for k in ("operation", "cible", "outil", "lieu") if e0.get(k)}
    return {
        "motif": intention.get("motif"),
        "but": copy.deepcopy(intention["but"]),
        "cle": _cle_decision(intention),
        "tete_plan": tete,
        "nb_etapes": len(plan),
    }


def _est_accompli(monde, id, decision, minute, cause_sortie=None):
    """Vrai si la décision ``decision`` a atteint sa condition de fin à cet instant."""
    if not decision or not decision.get("but"):
        return False
    but = decision["but"]
    genre = but.get("type")
    e = lire(monde, id)
    ici = monde.objets[id]["lieu"]
    if genre == "pulsion":
        cond = {k: v for k, v in but.items() if k != "type"}
        return bool(deliberation.satisfaite(monde, id, cond))
    if genre == "voir":
        if cause_sortie and cause_sortie.startswith("fin:"):
            return True
        from donjon.ouie import resolu
        salle = but.get("lieu")
        return not any(
            s["type"] == "bruit" and s.get("salle") == salle and not resolu(monde, id, s)
            for s in e["memoire"]
        )
    if genre in ("manger", "part"):
        return "faim" not in e.get("pressants", ())
    if genre == "chaleur":
        return "chaleur" not in e.get("pressants", ()) and e["besoins"].get("chaleur", 0) <= deliberation.CHALEUR_FIN
    if genre == "repos":
        return "repos" not in e.get("pressants", ()) and e["besoins"].get("repos", 0) <= deliberation.REPOS_FIN
    if genre == "abri":
        cible = but.get("lieu")
        return (
            (cible is None or ici == cible)
            and not eau.en_peril(monde, id)
            and "securite" not in e.get("pressants", ())
            and e["besoins"].get("securite", 0) <= deliberation.SECURITE_FIN
        )
    if genre == "lumiere":
        return "securite" not in e.get("pressants", ()) and e["besoins"].get("securite", 0) <= deliberation.SECURITE_FIN
    if genre == "agenda":
        aid = but.get("agenda")
        return any(a["id"] == aid and a.get("etat") == "atteint" for a in e.get("agendas", ()))
    if genre == "interposer":
        r = defense.interposition(monde, id)
        return r is None or not r[1]
    if genre in ("fuir", "riposter", "proteger", "degager"):
        return (
            not defense.dangers(monde, id)
            and not defense.protection(monde, id)
            and not corps.corps(monde, id).get("tenu_par")
        )
    if genre == "ranimer":
        qui = but.get("qui")
        etat = e["croyances"].get(qui, {}).get("etat", {}).get("valeur", {})
        return etat.get("conscient") is not False
    if genre == "prevenir":
        qui, de = but.get("qui"), but.get("de")
        if de:
            return not any(
                s["type"] == "a_prevenir"
                and s.get("victime") == qui
                and s.get("auteur") == de
                and deliberation._a_dire(monde, id, s["victime"], s["auteur"])
                for s in e["memoire"]
            )
        return True
    if genre == "enquete":
        besoin, qui = but.get("besoin"), but.get("qui")
        if besoin not in e.get("pressants", ()):
            return True
        v = planification.Vue(monde, id)
        return any(
            s["operation"] == "enqueter"
            and s.get("de") == qui
            and s.get("besoin") == besoin
            and deliberation.tient(monde, id, s, v.connus)
            for s in e.get("refus", ())
        ) or any(
            v.proprietaire[o] == qui and deliberation.part_pour(monde, id, o, besoin, v.connus)
            for o in v.connus
        )
    return False


def relever_entrees(monde, id, minute):
    """Photographie sans effet de bord des entrées lues par ``choisir`` et ``_entrees``."""
    v = planification.Vue(monde, id)
    e = lire(monde, id)
    croyances = e["croyances"]
    ici = monde.objets[id]["lieu"]
    p = deliberation.profil(monde, id) or {"pulsions": []}
    pressants = e.get("pressants", ())

    croyances_dict = {
        f"{s}.{a}": _canon(c["valeur"])
        for s, d in sorted(croyances.items())
        for a, c in sorted(d.items())
        if a != "fin"
    }
    croyances_dict["__eau__"] = _canon([sorted(v.menacees), sorted(v.noyees), bool(v.monte), sorted(v.eau.items())])
    croyances_dict["__apport__"] = _canon([
        [o, v.apport(o)] for o in sorted(v.connus) if "lumiere" in croyances.get(o, ())
    ])

    besoins_dict = {
        "pressants": sorted(pressants),
        "paliers": {
            b: {
                "presse": b in pressants,
                "desespoir": val >= deliberation.DESESPOIR,
                "urgence": val >= p.get("besoins", {}).get(b, {}).get("urgence", 60),
                "au_dessus_fin": val > SEUILS_FIN.get(b, 0),
            }
            for b, val in sorted(e["besoins"].items())
        },
        "eau_peril_salle": bool(
            eau.active(monde)
            and ici in monde.data["salles"]
            and (eau.eau_crue(monde, id, ici) > 0 or eau.noyee_attendue(monde, id, ici))
        ),
    }

    pulsions_list = [
        x["condition"]
        for x in p.get("pulsions", ())
        if not deliberation.satisfaite(monde, id, x["condition"])
    ]

    interpos = defense.interposition(monde, id)
    alarmes_dict = {
        "dangers": defense.dangers(monde, id),
        "actifs": defense.actifs(monde, id),
        "protection": defense.protection(monde, id),
        "tenu_par": bool(corps.corps(monde, id).get("tenu_par")),
        "reddition": corps.corps(monde, id).get("reddition"),
        "interposition": interpos[0] if interpos else None,
        "alarme": deliberation.alarme(monde, id),
        "bruits_a_voir": deliberation.bruit_a_voir(monde, id),
        "examens": [
            [s.get("salle"), s.get("nature"), s.get("qui"), s.get("case")]
            for s in e["memoire"]
            if s["type"] == "examen" and minute - s["minute"] <= RECENT
        ],
        "a_ranimer": [
            prot for prot in deliberation.proteges(monde, id)
            if e["croyances"].get(prot, {}).get("etat", {}).get("valeur", {}).get("conscient") is False
            and not e["croyances"][prot]["etat"]["valeur"].get("mort")
        ],
    }

    social_dict = {
        "refus_tenus": [
            [
                {k: s[k] for k in sorted(s) if k != "minute"},
                bool(tenu),
                minute - s["minute"] < deliberation.REDEMANDE,
                minute == s["minute"],
            ]
            for s, tenu in v.refus_tenus()
        ],
        "refus_enquete": [
            [{k: s[k] for k in sorted(s) if k != "minute"}, bool(deliberation.tient(monde, id, s, v.connus))]
            for s in e.get("refus", ())
            if s.get("operation") == "enqueter"
        ],
        "promesses": [
            [
                {k: s[k] for k in sorted(s) if k != "minute"},
                minute - s["minute"] < planification.ATTENTE_PART,
                croyances.get(s.get("foyer"), {}).get("etat", {}).get("minute", -1) >= s["minute"],
            ]
            for s in e["memoire"]
            if s["type"] in ("promis", "nourri", "recu", "promesse_annulee", "creance")
        ],
        "creances_vaines": sorted({
            s["de"] for s in e["memoire"]
            if s["type"] == "creance_vaine" and minute - s["minute"] < deliberation.REDEMANDE
        }),
        "recherches": [[q, sorted(deliberation.appels_vains(monde, id, q))] for q in sorted(e.get("recherches", ()))],
        "engagements": [[x["pour"], x["condition"], bool(x.get("annule"))] for x in agendas.en_cours(monde, id)],
        "agendas": [[a["id"], a.get("etat"), a.get("raison_sommeil")] for a in e.get("agendas", ())],
        "a_prevenir": [
            [s.get("victime"), s.get("auteur")]
            for s in e["memoire"]
            if s["type"] == "a_prevenir" and deliberation._a_dire(monde, id, s["victime"], s["auteur"])
        ],
        "rejoint": e.get("rejoint"),
        "aides": v.aides,
    }

    inventaire_dict = {
        "portes": sorted(k for k in v.connus if planification.porte_par(monde, k, id)),
        "richesse": [v.richesse, v.piece],
        "illicites": [
            sorted(o for o in v.connus if v.illicite[o]),
            sorted(o for o in v.connus if v.consomme_illicite[o]),
            sorted(o for o in v.connus if v.brise_illicite[o]),
        ],
        "gardes": [v.gardes, sorted(v.prix_gardes.items())],
        "relations": [
            [x, {a: r[a] for a in (*relations.AXES, "bandes")}]
            for x in sorted(relations.connus(monde, id))
            for r in [relations.axes(monde, id, x)]
        ],
    }

    manque = e.get("manque")
    position_dict = {
        "lieu": ici,
        "ordre_visites": planification._ordre_visites(v.salles, e["visites"]),
        "manque": manque if manque and manque.get("minute") == minute else None,
    }

    return {
        "croyances_valeurs": _canon(croyances_dict),
        "besoins_paliers": _canon(besoins_dict),
        "pulsions_dues": _canon(pulsions_list),
        "alarmes_et_dangers": _canon(alarmes_dict),
        "social_et_engagements": _canon(social_dict),
        "inventaire_et_droits": _canon(inventaire_dict),
        "position_et_progres": _canon(position_dict),
        "_details": {
            "croyances": croyances_dict,
            "besoins": besoins_dict,
            "pulsions": pulsions_list,
            "alarmes": alarmes_dict,
            "social": social_dict,
            "inventaire": inventaire_dict,
        },
        "lieu": ici,
        "besoins_continus": {b: round(val, 1) for b, val in sorted(e["besoins"].items())},
    }


def _diff_categories(e1, e2, categories=CATEGORIES_EXTERNES):
    return [c for c in categories if e1[c] != e2[c]]


def _diff_croyances(e1, e2):
    c1, c2 = e1["_details"]["croyances"], e2["_details"]["croyances"]
    cles = sorted(set(c1) | set(c2))
    return {k: [c1.get(k), c2.get(k)] for k in cles if c1.get(k) != c2.get(k)}


class SondeAvis:
    """Enregistre les épisodes de décision par PNJ sans perturber la simulation."""

    def __init__(self):
        self.episodes = {}          # id -> list[dict]
        self.intentions_agir = {}   # id -> str
        self.dans_deliberer = False
        self.gestes_contraires = []

    def enregistrer_choix(self, monde, id, minute, cause):
        dec = _resume_decision(lire(monde, id)["intention"])
        t = instant(monde)
        eps = self.episodes.setdefault(id, [])
        if eps and eps[-1]["decision"]["cle"] == dec["cle"]:
            eps[-1]["fin_t"] = t
            eps[-1]["fin_minute"] = minute
            eps[-1]["nb_choix"] += 1
            return
        entrees = relever_entrees(monde, id, minute)
        if eps:
            precedent = eps[-1]
            precedent["quitte_t"] = t
            precedent["quitte_minute"] = minute
            precedent["quitte_cause"] = cause
            precedent["quitte_entrees"] = entrees
            precedent["accompli_au_depart"] = _est_accompli(
                monde, id, precedent["decision"], minute, cause_sortie=cause
            )
        eps.append({
            "id": id,
            "debut_t": t,
            "debut_minute": minute,
            "fin_t": t,
            "fin_minute": minute,
            "cause_entree": cause,
            "decision": dec,
            "debut_entrees": entrees,
            "nb_choix": 1,
            "quitte_t": None,
            "quitte_minute": None,
            "quitte_cause": None,
            "quitte_entrees": None,
            "accompli_au_depart": False,
        })


def analyser_episodes(episodes_par_pnj, horizon_minutes=60):
    """Détecte et classe tous les allers-retours D1 -> D2 ... -> D1."""
    allers_retours = []
    comptes = Counter()
    par_famille = Counter()

    for id, eps in sorted(episodes_par_pnj.items()):
        for k, ep_retour in enumerate(eps):
            cle = ep_retour["decision"]["cle"]
            if cle is None:
                continue
            i = None
            for j in range(k - 1, -1, -1):
                if eps[j]["decision"]["cle"] == cle:
                    i = j
                    break
            if i is None or i == k - 1:
                continue
            ep_depart = eps[i]
            duree_ecart = (ep_retour["debut_t"] - (ep_depart["quitte_t"] or ep_depart["fin_t"])) / MINUTE
            if horizon_minutes is not None and duree_ecart > horizon_minutes:
                continue

            intermediaires = eps[i + 1:k]
            intermediaires_reels = [m for m in intermediaires if m["decision"]["cle"] is not None]
            but_d1 = ep_depart["decision"]["but"]
            est_garde = but_d1.get("type") == "garder"

            if ep_depart["accompli_au_depart"]:
                classe = "cycle_accompli"
                comptes[classe] += 1
                continue
            if est_garde and intermediaires_reels and all(m["accompli_au_depart"] for m in intermediaires_reels):
                classe = "garde_interruption_accomplie"
                comptes[classe] += 1
                continue

            e_debut = ep_depart["debut_entrees"]
            e_quitte = ep_depart["quitte_entrees"] or ep_depart["debut_entrees"]
            e_retour = ep_retour["debut_entrees"]

            diff_quitte_retour = _diff_categories(e_quitte, e_retour)
            diff_debut_retour = _diff_categories(e_debut, e_retour)
            diff_debut_quitte = _diff_categories(e_debut, e_quitte)
            meme_lieu_quitte_retour = e_quitte["lieu"] == e_retour["lieu"]
            meme_lieu_debut_retour = e_debut["lieu"] == e_retour["lieu"]

            # Vérifier si la seule différence de croyances est l'état d'un tiers (orientation/activité)
            # ou un objet hors des cibles de D1 et des décisions intermédiaires.
            croyances_qr = _diff_croyances(e_quitte, e_retour)
            croyances_dr = _diff_croyances(e_debut, e_retour)
            croyances_dq = _diff_croyances(e_debut, e_quitte)

            if not diff_quitte_retour and meme_lieu_quitte_retour:
                classe = "non_justifie_strict_complet"
            elif not diff_debut_retour and meme_lieu_debut_retour:
                classe = "non_justifie_retour_etat_initial_exact"
            elif not diff_quitte_retour or not diff_debut_retour:
                classe = "non_justifie_externe_fixe_seul_deplacement"
            elif not diff_debut_quitte:
                classe = "non_justifie_abandon_sans_entree_externe"
            else:
                classe = "justifie_par_entree_nouvelle"

            comptes[classe] += 1
            non_justifie = classe.startswith("non_justifie_")
            signature = (
                id,
                ep_depart["decision"]["motif"],
                but_d1.get("type"),
                "->".join(str((m["decision"]["but"] or {}).get("type") or "attente") for m in intermediaires),
            )
            if non_justifie:
                par_famille[" | ".join(str(x) for x in signature)] += 1

            allers_retours.append({
                "id": id,
                "classe": classe,
                "non_justifie": non_justifie,
                "d1_motif": ep_depart["decision"]["motif"],
                "d1_but": but_d1,
                "d1_tete_plan": ep_depart["decision"]["tete_plan"],
                "intermediaires": [
                    {
                        "motif": m["decision"]["motif"],
                        "but": m["decision"]["but"],
                        "tete_plan": m["decision"]["tete_plan"],
                        "debut_t": m["debut_t"],
                        "debut_minute": m["debut_minute"],
                        "cause_entree": m["cause_entree"],
                        "quitte_cause": m["quitte_cause"],
                        "accompli_au_depart": m["accompli_au_depart"],
                        "lieu": m["debut_entrees"]["lieu"],
                    }
                    for m in intermediaires
                ],
                "debut_t": ep_depart["debut_t"],
                "debut_minute": ep_depart["debut_minute"],
                "quitte_t": ep_depart["quitte_t"],
                "quitte_minute": ep_depart["quitte_minute"],
                "quitte_cause": ep_depart["quitte_cause"],
                "retour_t": ep_retour["debut_t"],
                "retour_minute": ep_retour["debut_minute"],
                "retour_cause": ep_retour["cause_entree"],
                "duree_ecart_min": round(duree_ecart, 2),
                "lieu_debut": e_debut["lieu"],
                "lieu_quitte": e_quitte["lieu"],
                "lieu_retour": e_retour["lieu"],
                "diff_debut_quitte": diff_debut_quitte,
                "diff_quitte_retour": diff_quitte_retour,
                "diff_debut_retour": diff_debut_retour,
                "croyances_diff_dq": croyances_dq,
                "croyances_diff_qr": croyances_qr,
                "croyances_diff_dr": croyances_dr,
                "besoins_debut": e_debut["besoins_continus"],
                "besoins_quitte": e_quitte["besoins_continus"],
                "besoins_retour": e_retour["besoins_continus"],
            })

    return {
        "comptes": dict(comptes),
        "total_non_justifies": sum(v for k, v in comptes.items() if k.startswith("non_justifie_")),
        "total_justifies": comptes.get("justifie_par_entree_nouvelle", 0),
        "total_cycles_accomplis": (
            comptes.get("cycle_accompli", 0) + comptes.get("garde_interruption_accomplie", 0)
        ),
        "par_famille_non_justifiee": dict(par_famille.most_common()),
        "allers_retours": allers_retours,
    }


def jouer_nuit_sondee(scenario, graine, heures=4.0, depart="tire", verifier_empreinte=False):
    """Joue une nuit avec la sonde sans modifier aucun comportement du moteur."""
    t0 = time.perf_counter()
    planification._MEMOIRE.clear()
    planification._GRAPHES.clear()
    deliberation.COMPTES.clear()

    joueur = SALLES_JOUEUR.get(scenario, "chambre_cloche")
    monde = banc_pnj.creer(scenario, graine, depart)
    if joueur:
        from donjon.geometrie import position_entree
        monde.joueur.update(salle=joueur, position=list(position_entree(monde, joueur)))

    sonde = SondeAvis()
    vrai_choisir = deliberation.choisir
    vrai_deliberer = deliberation.deliberer
    vrai_agir = pnj.agir
    vrai_menager = deliberation.menager_flamme

    def deliberer_sonde(m, id, minute):
        sonde.dans_deliberer = True
        try:
            return vrai_deliberer(m, id, minute)
        finally:
            sonde.dans_deliberer = False

    def choisir_sonde(m, id, minute):
        cause = "minute" if sonde.dans_deliberer else sonde.intentions_agir.pop(id, "eveil")
        res = vrai_choisir(m, id, minute)
        sonde.enregistrer_choix(m, id, minute, cause)
        return res

    def agir_sonde(m, id, t, lignes, gestes=None, compter=True):
        res = vrai_agir(m, id, t, lignes, gestes, compter)
        _, issue, rate = res
        if issue in (pnj.FIN, pnj.MANQUE):
            sonde.intentions_agir[id] = f"{issue}:{rate.get('operation') if rate else ''}"
        return res

    def menager_sonde(m, id, minute):
        avant = {k: m.objets[k].get("allume") for k in m.objets if "allume" in m.objets[k]}
        res = vrai_menager(m, id, minute)
        for k, v_avant in avant.items():
            if v_avant and not m.objets[k].get("allume"):
                sonde.gestes_contraires.append({
                    "id": id,
                    "minute": minute,
                    "instant": instant(m),
                    "operation": "eteindre_menager",
                    "objet": k,
                    "intention": _resume_decision(lire(m, id)["intention"]),
                })
        return res

    deliberation.choisir = choisir_sonde
    deliberation.deliberer = deliberer_sonde
    pnj.agir = agir_sonde
    deliberation.menager_flamme = menager_sonde
    try:
        from donjon.recit_pnj import Recit
        recit = Recit(monde)
        empreintes = {}
        pas, mesures = banc_pnj.executer(monde, int(heures * 60), recit, empreintes)
    finally:
        deliberation.choisir = vrai_choisir
        deliberation.deliberer = vrai_deliberer
        pnj.agir = vrai_agir
        deliberation.menager_flamme = vrai_menager

    sha_etat = hashlib.sha256(_canon(monde.data).encode("utf-8")).hexdigest()
    if verifier_empreinte:
        _, _, ref = banc_pnj.nuit(scenario, graine, heures, joueur, depart=depart)
        assert empreintes == ref["empreintes"], f"Empreintes modifiées sur {scenario} {graine}"
        assert pas == ref["chronique"], f"Chronique modifiée sur {scenario} {graine}"

    analyse = analyser_episodes(sonde.episodes)
    duree = round(time.perf_counter() - t0, 2)
    return {
        "scenario": scenario,
        "graine": graine,
        "heures": heures,
        "secondes": duree,
        "empreintes": empreintes,
        "sha256_data": sha_etat,
        "mesures": mesures,
        "gestes_menager_flamme": sonde.gestes_contraires,
        "nb_episodes_par_pnj": {id: len(eps) for id, eps in sorted(sonde.episodes.items())},
        "analyse": analyse,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenarios", nargs="+", default=list(SCENARIOS_DEFAUT))
    parser.add_argument("--graines", type=int, nargs="+", default=list(GRAINES_DEFAUT))
    parser.add_argument("--heures", type=float, default=4.0)
    parser.add_argument("--verifier-empreinte", action="store_true",
                        help="vérifie sur la première nuit que la sonde ne change ni empreintes ni chronique")
    parser.add_argument("--sortie", required=True, help="fichier JSON où enregistrer le rapport complet")
    args = parser.parse_args(argv)

    banc_pnj.ceder()
    resultats = []
    totaux = Counter()
    familles = Counter()
    par_scenario = {}

    premiere = True
    for scenario in args.scenarios:
        c_scen = Counter()
        for graine in args.graines:
            r = jouer_nuit_sondee(
                scenario,
                graine,
                heures=args.heures,
                verifier_empreinte=args.verifier_empreinte and premiere,
            )
            premiere = False
            resultats.append(r)
            a = r["analyse"]
            for k, v in a["comptes"].items():
                totaux[k] += v
                c_scen[k] += v
            for k, v in a["par_famille_non_justifiee"].items():
                familles[f"{scenario}:{k}"] += v
            print(
                f"[{scenario} {graine}] {r['secondes']:.1f}s | "
                f"non_justifiés={a['total_non_justifies']} "
                f"(strict={a['comptes'].get('non_justifie_strict_complet', 0)}, "
                f"retour_init={a['comptes'].get('non_justifie_retour_etat_initial_exact', 0)}, "
                f"depl_seul={a['comptes'].get('non_justifie_externe_fixe_seul_deplacement', 0)}, "
                f"abandon_sans_entree={a['comptes'].get('non_justifie_abandon_sans_entree_externe', 0)}) | "
                f"justifiés={a['total_justifies']} | cycles_accomplis={a['total_cycles_accomplis']}",
                flush=True,
            )
        par_scenario[scenario] = {
            "comptes": dict(c_scen),
            "total_non_justifies": sum(v for k, v in c_scen.items() if k.startswith("non_justifie_")),
            "total_justifies": c_scen.get("justifie_par_entree_nouvelle", 0),
            "total_cycles_accomplis": (
                c_scen.get("cycle_accompli", 0) + c_scen.get("garde_interruption_accomplie", 0)
            ),
        }

    synthese = {
        "parametres": {
            "scenarios": args.scenarios,
            "graines": args.graines,
            "heures": args.heures,
            "nb_nuits": len(resultats),
        },
        "totaux_comptes": dict(totaux),
        "total_non_justifies": sum(v for k, v in totaux.items() if k.startswith("non_justifie_")),
        "total_justifies": totaux.get("justifie_par_entree_nouvelle", 0),
        "total_cycles_accomplis": (
            totaux.get("cycle_accompli", 0) + totaux.get("garde_interruption_accomplie", 0)
        ),
        "par_scenario": par_scenario,
        "par_famille_non_justifiee": dict(familles.most_common(40)),
        "nuits": resultats,
    }
    chemin = Path(args.sortie)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(synthese, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"\nTOTAL ({len(resultats)} nuits) : non_justifiés={synthese['total_non_justifies']} | "
        f"justifiés={synthese['total_justifies']} | cycles_accomplis={synthese['total_cycles_accomplis']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
