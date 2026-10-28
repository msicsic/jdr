"""Détecteur générique des changements d'avis et allers-retours de décision des PNJ.

Observe ``deliberation.choisir``, ``deliberation.menager_flamme`` et ``pnj.agir``
sans modifier aucun état du monde, aucun tirage aléatoire ni aucune mémoire du
planificateur. Pour chaque transition, conserve les entrées du choix et les preuves observées :
palier du candidat essayé, étape exécutée et condition de fin devenue vraie.
Les règles sont ordonnées : cycle accompli, préemption stricte, satisfaction ou
démenti pendant l'action d'un tiers, progression, moyen évitant le geste manqué,
rendez-vous intermédiaire clos, entrée publiée utilisée par le plan repris,
répétition, entrée à expliquer.
Les dérives ouvertes et les pertes d'état payé sont des observations séparées.
Aucune durée de maintien n'est inventée pour les services instantanés.
Les pertes sont attribuées aux gestes exécutés ou aux transitions physiques
sondés, avec la présence crue avant le geste et les clôtures publiées auparavant ;
ailleurs la cause reste inconnue.

La couverture demeure partielle (horizon, prédicats de fin et candidats sans
palier publié) : une entrée changée ne constitue pas un certificat causal.
"""
import argparse
from collections import Counter
from contextlib import contextmanager, ExitStack
from unittest.mock import patch
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from donjon import agendas, appel, banc_pnj, biens, corps, defense, deliberation, eau, planification, pnj, relations  # noqa: E402
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
CLASSES_SERVICES = ("prestataire_beneficiaire_present", "prestataire_beneficiaire_parti",
                    "beneficiaire_ou_tiers", "cessation_physique", "cause_non_observee",
                    "service_clos_avant_perte")

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
        "plan": copy.deepcopy(plan),
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
        return any(a["id"] == aid and a.get("etat") == "atteint" for a in agendas.projets(monde, id))
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
        "charges": [[x["pour"], x["condition"], bool(x.get("annule"))] for x in agendas.en_cours(monde, id)],
        "engagements_tenus": [copy.deepcopy(s) for s in e["memoire"]
                              if s["type"] == "engagement_tenu" and "pour" in s],
        "agendas": [[a["id"], a.get("etat"), a.get("raison_sommeil")] for a in agendas.projets(monde, id)],
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
        "possedes": sorted(k for k in v.connus if v.proprietaire[k] == id),
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


def _references_plan(valeur):
    """Identifiants des étapes, y compris les conditions des offres imbriquées.

    Les noms d'opération, types d'offre et textes ne sont pas des références.
    On ne déduit aucune dépendance à partir du nom du but ou d'un personnage.
    """
    if isinstance(valeur, list):
        return set().union(*(_references_plan(x) for x in valeur))
    if not isinstance(valeur, dict):
        return set()
    refs = {v for k, v in valeur.items()
            if k in ("cible", "outil", "objet", "qui", "de", "pour", "lieu", "destination")
            and isinstance(v, str) and v}
    for v in valeur.values():
        if isinstance(v, (dict, list)):
            refs.update(_references_plan(v))
    return refs


def _entrees_utilisees(ep_depart, intermediaires, ep_retour):
    """Preuves publiées depuis la sortie, reliées au plan réellement repris.

    Une simple différence d'empreinte, une perte de possession, une position
    oubliée ou une annulation d'engagement ne sont jamais des preuves.
    Les archives dépourvues de ces relevés restent sans certificat.
    """
    plan = ep_retour["decision"].get("plan")
    if not plan or not ep_retour.get("moyen_admissible"):
        return []
    refs = _references_plan(plan)
    avant = (ep_depart.get("quitte_entrees") or ep_depart["debut_entrees"])["_details"]
    apres = ep_retour["debut_entrees"]["_details"]
    preuves = []
    for champ, preuve in (("portes", "possession_nouvelle"), ("possedes", "propriete_nouvelle")):
        inv1, inv2 = avant.get("inventaire", {}), apres.get("inventaire", {})
        if champ not in inv1 or champ not in inv2:
            continue
        for objet in sorted((set(inv2[champ]) - set(inv1[champ])) & refs):
            preuves.append({"preuve": preuve, "objet": objet})
    for cible in sorted(refs):
        cle = cible + ".lieu"
        v1, v2 = avant["croyances"].get(cle), apres["croyances"].get(cle)
        # Les valeurs sont canoniques ; null et la chaîne vide ne localisent rien.
        if v2 is not None and v2 not in ("null", '""') and v1 != v2:
            preuves.append({"preuve": "lieu_cru_change", "cible": cible, "avant": v1, "apres": v2})
    social1, social2 = avant.get("social", {}), apres.get("social", {})
    # Le moteur publie engagement_tenu ; la seule disparition du stock ne suffit
    # pas. Exiger aussi la charge observée active puis retirée et son objet utilisé.
    releves = [avant, *(entrees["_details"] for e in intermediaires
                        for entrees in (e["debut_entrees"], e.get("quitte_entrees")) if entrees)]
    charges = [x for details in releves for x in details.get("social", {}).get("charges", ())]
    for recu in social2.get("engagements_tenus", ()):
        charge = [recu["pour"], recu["condition"], False]
        if (recu not in social1.get("engagements_tenus", ())
                and charge in charges
                and not any(x[:2] == charge[:2] for x in social2.get("charges", ()))
                and recu["condition"].get("objet") in refs
                and ep_depart["quitte_minute"] <= recu["minute"] <= ep_retour["debut_minute"]):
            preuves.append({"preuve": "engagement_accompli_publie", "recu": recu})
    return preuves


class SondeAvis:
    """Enregistre les épisodes de décision par PNJ sans perturber la simulation."""

    def __init__(self):
        self.episodes = {}          # id -> list[dict]
        self.intentions_agir = {}   # id -> str
        self.dans_deliberer = False
        self.gestes_contraires = []
        self.candidats = {}
        self.services = {}
        self.monde_services = None

    def cloturer_services(self, monde, avant):
        """Ne retient que les retraits effectivement publiés par le choix complet."""
        for trace in avant:
            if trace in monde.data.get("services_rendus", ()):
                continue
            for service in self.services.values():
                if (service["prestataire"] == trace["de"] and service["payeur"] == trace["pour"]
                        and service["condition"] == trace["condition"]
                        and service["reussite_t"] is not None and service["perte_t"] is None
                        and "cloture" not in service):
                    service["cloture"] = {
                        "t": instant(monde), "preuve": "retrait_publie_services_rendus",
                        "trace": copy.deepcopy(trace),
                        "presence": self.presence_service(monde, service, trace),
                        "croyances": copy.deepcopy(lire(monde, trace["de"])["croyances"]),
                    }

    def accomplissements(self, monde):
        resultat = {}
        for qui, eps in self.episodes.items():
            vus = set()
            for ep in reversed(eps):
                cle = ep["decision"]["cle"]
                if cle is None or cle in vus:
                    continue
                vus.add(cle)
                if instant(monde) - ep["debut_t"] > 60 * MINUTE:
                    continue
                resultat[qui, cle] = _est_accompli(monde, qui, ep["decision"], monde.data["minutes"])
        return resultat

    def constater(self, monde, acteur, avant):
        for (qui, cle), accompli in self.accomplissements(monde).items():
            if avant.get((qui, cle)) is False and accompli:
                self.episodes[qui][-1].setdefault("faits", []).append({
                    "t": instant(monde), "cle": cle, "autrui": acteur != qui,
                    "acteur": acteur, "preuve": "condition_de_fin_devenue_vraie"})

    def presence_service(self, monde, service, trace=None):
        """Lecture pure du même critère de départ cru que biens.services_proteges."""
        id, pour = service["prestataire"], service["payeur"]
        objet = service["condition"]["objet"]
        lieu = deliberation.salle_crue(monde, id, objet)
        beneficiaire = deliberation.salle_crue(monde, id, pour)
        porteur = deliberation._lieu_cru(monde, id, objet)
        from donjon.monde import mobile_par_nature
        if trace is None:
            trace = next((s for s in monde.data.get("services_rendus", ())
                          if s["de"] == id and s["pour"] == pour
                          and s["condition"] == service["condition"]), {})
        reference = trace.get("lieu_beneficiaire",
                              None if mobile_par_nature(monde.objets.get(objet, {})) else lieu)
        parti = (porteur != pour and reference is not None and lieu is not None
                 and beneficiaire is not None and reference != beneficiaire and lieu != beneficiaire)
        return {"parti": parti, "lieu_objet_cru": lieu, "lieu_beneficiaire_cru": beneficiaire,
                "porteur_cru": porteur, "lieu_reference": reference}

    def presences_services(self, monde):
        return {id(s): self.presence_service(monde, s) for s in self.services.values()
                if s["perte_t"] is None and s["reussite_t"] is not None}

    def relever_services(self, monde, acteur=None, cause=None, presences=None):
        self.monde_services = monde
        # Conditions d'état, lues dans la réalité ; les conditions de gestes
        # (servir/remettre) n'impliquent aucun état durable de l'objet.
        for qui in self.episodes:
            for souvenir in lire(monde, qui)["memoire"]:
                if souvenir.get("type") != "tache_payee":
                    continue
                condition = souvenir["condition"]
                objet = condition.get("objet")
                if objet not in monde.objets or not set(condition) <= {"objet", "allume", "verrouillee", "lieu"}:
                    continue
                cle = _canon([qui, souvenir])
                self.services.setdefault(cle, {
                    "payeur": qui, "prestataire": souvenir["a"], "condition": copy.deepcopy(condition),
                    "minute_paiement": souvenir["minute"], "reussite_t": None, "perte_t": None,
                    "classe": "etat_paye_perdu_apres_reussite_duree_non_specifiee",
                    "violation": False, "duree_specifiee": False})
        # Le souvenir peut sortir de la mémoire bornée du personnage ; l'audit
        # conserve son observation et continue à suivre l'état payé.
        for service in self.services.values():
            condition = service["condition"]
            objet = monde.objets.get(condition["objet"], {})
            vrai = all(objet.get(k) == v for k, v in condition.items() if k != "objet")
            if vrai and service["reussite_t"] is None:
                service["reussite_t"] = instant(monde)
            if not vrai and service["reussite_t"] is not None and service["perte_t"] is None:
                service["perte_t"] = instant(monde)
                presence = (presences or {}).get(id(service))
                classe = "cause_non_observee"
                if cause == "physique":
                    classe = "cessation_physique"
                elif acteur is not None:
                    if acteur != service["prestataire"]:
                        classe = "beneficiaire_ou_tiers"
                    elif presence is not None:
                        classe = ("prestataire_beneficiaire_parti" if presence["parti"]
                                  else "prestataire_beneficiaire_present")
                service.update(classe=classe, acteur=acteur, cause=cause, presence_avant=presence,
                               violation=classe == "prestataire_beneficiaire_present")
                if "cloture" in service and service["cloture"]["t"] <= instant(monde):
                    service.update(classe="service_clos_avant_perte", violation=False)

    def analyser(self):
        analyse = analyser_episodes(self.episodes)
        analyse["services_etat_perdu"] = [s for s in self.services.values() if s["perte_t"] is not None]
        analyse["total_services_etat_perdu"] = len(analyse["services_etat_perdu"])
        analyse["services_par_classe"] = {c: sum(s["classe"] == c for s in analyse["services_etat_perdu"])
                                          for c in CLASSES_SERVICES}
        return analyse

    def enregistrer_choix(self, monde, id, minute, cause, manque=None):
        dec = _resume_decision(lire(monde, id)["intention"])
        t = instant(monde)
        eps = self.episodes.setdefault(id, [])
        if eps and eps[-1]["decision"]["cle"] == dec["cle"]:
            eps[-1]["fin_t"] = t
            eps[-1]["fin_minute"] = minute
            eps[-1]["nb_choix"] += 1
            if dec["cle"] in self.candidats.get(id, {}):
                eps[-1]["palier"] = self.candidats[id][dec["cle"]]
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
            if manque and cause.startswith("manque:"):
                precedent.setdefault("faits", []).append({
                    "t": t, "cle": precedent["decision"]["cle"],
                    "preuve": "etape_manquee", "etape": copy.deepcopy(manque["etape"])})
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
            "palier": self.candidats.get(id, {}).get(dec["cle"]),
            "faits": [],
            "moyen_admissible": not any(
                deliberation.renoncement_tient(monde, id, r,
                                               (dec["but"], dec.get("plan", [])))
                for retenus in lire(monde, id).get("renoncements", {}).values()
                if isinstance(retenus, list) for r in retenus) if dec["cle"] else False,
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

            if ep_depart["accompli_au_depart"]:
                classe = "cycle_accompli"
            elif est_garde and intermediaires_reels and all(m["accompli_au_depart"] for m in intermediaires_reels):
                classe = "garde_interruption_accomplie"
            elif not diff_quitte_retour and meme_lieu_quitte_retour:
                classe = "non_justifie_strict_complet"
            elif not diff_debut_retour and meme_lieu_debut_retour:
                classe = "non_justifie_retour_etat_initial_exact"
            elif not diff_quitte_retour or not diff_debut_retour:
                classe = "non_justifie_externe_fixe_seul_deplacement"
            elif not diff_debut_quitte:
                classe = "non_justifie_abandon_sans_entree_externe"
            else:
                classe = "entree_nouvelle_a_expliquer"

            # Les preuves instrumentées priment sur les anciennes ressemblances
            # d'entrées. Un palier est celui d'un candidat réellement exécuté,
            # jamais déduit du nom du but ou du personnage.
            ancienne_classe = classe
            preuves = []
            palier = ep_depart.get("palier")
            suivant = intermediaires[0] if intermediaires else {}
            palier_suivant = suivant.get("palier")
            faits = [f for e in [ep_depart, *intermediaires] for f in e.get("faits", ())
                     if (ep_depart["quitte_t"] or ep_depart["fin_t"]) <= f["t"] <= ep_retour["debut_t"]]
            plan_retour = ep_retour["decision"].get("plan")
            echecs_evites = [f for f in ep_depart.get("faits", ())
                             if f.get("preuve") == "etape_manquee"
                             and f["t"] == ep_depart["quitte_t"]
                             and plan_retour and ep_retour.get("moyen_admissible")
                             and not any(all(p.get(k) == f["etape"].get(k)
                                             for k in ("operation", "cible", "lieu"))
                                         for p in plan_retour)]
            rendez_vous = [f for m in intermediaires for f in m.get("faits", ())
                          if f.get("preuve") == "rendez_vous_clos_par_retrouves"
                          and f.get("cle") == m["decision"]["cle"]
                          and m["debut_t"] <= f["t"] <= ep_retour["debut_t"]
                          and plan_retour and any(p.get("cible") == f["qui"] for p in plan_retour)]
            entrees_utilisees = _entrees_utilisees(ep_depart, intermediaires, ep_retour)
            if ep_depart["accompli_au_depart"]:
                classe = "cycle_accompli"
            elif palier is not None and palier_suivant is not None and palier_suivant < palier:
                classe = "preemption_palier_superieur"
                preuves = [{"depart": palier, "interruption": palier_suivant}]
            elif any(f.get("cle") == cle and f.get("autrui") for f in faits):
                classe = "satisfaction_ou_dementi_autrui"
                preuves = [f for f in faits if f.get("cle") == cle and f.get("autrui")]
            elif any(f.get("cle") == cle and f.get("progression") for f in faits):
                classe = "progression_reelle"
                preuves = [f for f in faits if f.get("cle") == cle and f.get("progression")]
            elif echecs_evites:
                classe = "changement_moyen_admissible"
                preuves = echecs_evites + [{"preuve": "plan_retour_admissible", "plan": plan_retour}]
            elif rendez_vous:
                classe = "rendez_vous_intermediaire_accompli"
                preuves = rendez_vous
            elif entrees_utilisees:
                classe = "entree_publiee_utilisee"
                preuves = entrees_utilisees + [{"preuve": "plan_retour_admissible", "plan": plan_retour}]
            elif intermediaires_reels and all(m["accompli_au_depart"] for m in intermediaires_reels):
                # Un résultat intermédiaire demande une explication causale ;
                # cette prudence vaut pour tous les buts, sans exception de garde.
                classe = "entree_nouvelle_a_expliquer"
            elif classe.startswith("non_justifie_"):
                classe = "repetition_sans_entree_nouvelle"
            else:
                classe = "entree_nouvelle_a_expliquer"

            comptes[classe] += 1
            non_justifie = classe == "repetition_sans_entree_nouvelle"
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
                "classe_199": ancienne_classe,
                "preuves": preuves,
                "non_justifie": non_justifie,
                "accompli_au_depart": ep_depart["accompli_au_depart"],
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

    derives = []
    for id, eps in sorted(episodes_par_pnj.items()):
        for i in range(len(eps) - 2):
            trois = eps[i:i + 3]
            cles = [e["decision"]["cle"] for e in trois]
            if None in cles or len(set(cles)) != 3:
                continue
            if any(e["decision"]["cle"] == cles[0] for e in eps[i + 3:]
                   if horizon_minutes is None or (e["debut_t"] - trois[0]["debut_t"]) / MINUTE <= horizon_minutes):
                continue
            if horizon_minutes is not None and (trois[-1]["debut_t"] - trois[0]["debut_t"]) / MINUTE > horizon_minutes:
                continue
            derives.append({"id": id, "debut_t": trois[0]["debut_t"],
                            "decisions": [e["decision"] for e in trois],
                            "accomplis": [e["accompli_au_depart"] for e in trois[:2]],
                            "suspect_certifie": False})
    return {
        "comptes": dict(comptes),
        "total_non_justifies": comptes.get("repetition_sans_entree_nouvelle", 0),
        "total_justifies": sum(comptes.get(k, 0) for k in (
            "preemption_palier_superieur", "progression_reelle", "satisfaction_ou_dementi_autrui",
            "changement_moyen_admissible", "rendez_vous_intermediaire_accompli", "entree_publiee_utilisee")),
        "derives_ouvertes": derives,
        "total_derives_ouvertes": len(derives),
        "total_a_expliquer": comptes.get("entree_nouvelle_a_expliquer", 0),
        "certification_complete": False,
        "horizon_minutes": horizon_minutes,
        "par_pnj": {id: dict(Counter(r["classe"] for r in allers_retours if r["id"] == id))
                    for id in sorted(episodes_par_pnj)},
        "total_cycles_accomplis": (
            comptes.get("cycle_accompli", 0) + comptes.get("garde_interruption_accomplie", 0)
        ),
        "par_famille_non_justifiee": dict(par_famille.most_common()),
        "allers_retours": allers_retours,
    }


@contextmanager
def observer_avis():
    """Sonde commune aux bancs ; restaure aussi les fonctions après une exception."""
    sonde = SondeAvis()
    vrai_choisir = deliberation.choisir
    vrai_deliberer = deliberation.deliberer
    vrai_agir = pnj.agir
    vrai_menager = deliberation.menager_flamme
    vrais_candidats = deliberation._candidats
    vraies_clotures = biens.clotures_services_du_choix
    vrais_retrouves = appel.retrouves

    @contextmanager
    def clotures_sondees(m):
        observe = m is sonde.monde_services
        avant = copy.deepcopy(m.data.get("services_rendus", []))
        if observe:
            sonde.relever_services(m)
        with vraies_clotures(m):
            yield
        if observe:
            sonde.cloturer_services(m, avant)

    def retrouves_sondes(m, id, qui):
        observe = m is sonde.monde_services
        attentes = [(x, y) for x, y in ((id, qui), (qui, id))
                    if x != "joueur" and (lire(m, x).get("rejoint") or {}).get("qui") == y]
        resultat = vrais_retrouves(m, id, qui)
        if not observe:
            return resultat
        for x, y in attentes:
            if lire(m, x).get("rejoint") is not None or not sonde.episodes.get(x):
                continue
            ep = sonde.episodes[x][-1]
            if ep["decision"]["but"] == {"type": "attendre", "qui": y}:
                ep.setdefault("faits", []).append({
                    "t": instant(m), "cle": ep["decision"]["cle"], "qui": y,
                    "preuve": "rendez_vous_clos_par_retrouves"})
        return resultat

    def transition(original, physique=False):
        def observer(monde, *args, **kwargs):
            m = monde
            sonde.relever_services(m)
            presences = sonde.presences_services(m)
            resultat = original(m, *args, **kwargs)
            sonde.relever_services(m, acteur=None if physique else (args[0] if args else kwargs["id"]),
                                  cause="physique" if physique else "geste", presences=presences)
            return resultat
        return observer

    def candidats_sondes(m, id):
        for candidat in vrais_candidats(m, id):
            def methode(m, id, original=candidat.methode, palier=int(candidat.urgence.palier)):
                resultat = original(m, id)
                if resultat:
                    cle = _cle_decision({"but": resultat[0]})
                    sonde.candidats.setdefault(id, {})[cle] = palier
                return resultat
            yield candidat._replace(methode=methode)

    def deliberer_sonde(m, id, minute):
        sonde.dans_deliberer = True
        try:
            return vrai_deliberer(m, id, minute)
        finally:
            sonde.dans_deliberer = False

    def choisir_sonde(m, id, minute):
        sonde.relever_services(m)
        cause = "minute" if sonde.dans_deliberer else sonde.intentions_agir.pop(id, "eveil")
        manque = copy.deepcopy(lire(m, id).get("manque"))
        sonde.candidats[id] = {}
        res = vrai_choisir(m, id, minute)
        sonde.enregistrer_choix(m, id, minute, cause, manque)
        sonde.relever_services(m)
        return res

    def agir_sonde(m, id, t, lignes, gestes=None, compter=True):
        sonde.relever_services(m)
        presences = sonde.presences_services(m)
        avant = sonde.accomplissements(m)
        intention = copy.deepcopy(lire(m, id)["intention"])
        res = vrai_agir(m, id, t, lignes, gestes, compter)
        sonde.constater(m, id, avant)
        apres = lire(m, id)["intention"]
        if (intention and intention.get("plan") and apres
                and _cle_decision(intention) == _cle_decision(apres)
                and len(apres["plan"]) < len(intention["plan"])
                and res[1] in (pnj.GESTE, pnj.FIN) and sonde.episodes.get(id)):
            sonde.episodes[id][-1]["faits"].append({
                "t": instant(m), "cle": _cle_decision(intention), "progression": True,
                "preuve": "etape_executee", "etape": intention["plan"][0]})
        sonde.relever_services(m, acteur=id, cause="geste", presences=presences)
        _, issue, rate = res
        if issue in (pnj.FIN, pnj.MANQUE):
            sonde.intentions_agir[id] = f"{issue}:{rate.get('operation') if rate else ''}"
        return res

    def menager_sonde(m, id, minute):
        avant = {k: m.objets[k].get("allume") for k in m.objets if "allume" in m.objets[k]}
        res = vrai_menager(m, id, minute)
        sonde.relever_services(m)
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

    from donjon import perception
    with ExitStack() as pile, patch.object(deliberation, "choisir", choisir_sonde), \
         patch.object(deliberation, "deliberer", deliberer_sonde), \
         patch.object(pnj, "agir", agir_sonde), \
         patch.object(biens, "clotures_services_du_choix", clotures_sondees), \
         patch.object(appel, "retrouves", retrouves_sondes), \
         patch.object(deliberation, "_candidats", candidats_sondes), \
         patch.object(deliberation, "menager_flamme", menager_sonde):
        for module, nom, physique in ((pnj, "_executer", False),
                                     (perception, "avancer_combustion", True),
                                     (eau, "inonder", True)):
            pile.enter_context(patch.object(module, nom, transition(getattr(module, nom), physique)))
        yield sonde


def jouer_nuit_sondee(scenario, graine, heures=4.0, depart="tire", verifier_empreinte=False):
    """Joue une nuit avec la sonde sans modifier aucun comportement du moteur."""
    t0 = time.perf_counter()
    # Le banc remet les résultats et graphes à froid, mais conserve les preuves
    # d'impossibilité entre nuits. Les deux côtés de cette mesure partent à froid.
    planification._IMPOSSIBLES.clear()
    joueur = SALLES_JOUEUR.get(scenario, "chambre_cloche")
    capture = {}
    creer = banc_pnj.creer
    def capturer(*a, **k):
        capture["monde"] = creer(*a, **k)
        return capture["monde"]
    with observer_avis() as sonde, patch.object(banc_pnj, "creer", capturer):
        _, mesures, donnees = banc_pnj.nuit(scenario, graine, heures, joueur, depart=depart)
    monde = capture["monde"]
    empreintes, pas = donnees["empreintes"], donnees["chronique"]

    secondes_sonde = time.perf_counter() - t0
    secondes_reference = None
    sha_etat = hashlib.sha256(_canon(monde.data).encode("utf-8")).hexdigest()
    if verifier_empreinte:
        capture = {}
        creer = banc_pnj.creer
        def capturer(*a, **k):
            capture["monde"] = creer(*a, **k)
            return capture["monde"]
        planification._IMPOSSIBLES.clear()
        debut_ref = time.perf_counter()
        with patch.object(banc_pnj, "creer", capturer):
            _, _, ref = banc_pnj.nuit(scenario, graine, heures, joueur, depart=depart)
        secondes_reference = time.perf_counter() - debut_ref
        assert sha_etat == hashlib.sha256(_canon(capture["monde"].data).encode("utf-8")).hexdigest(), "État modifié"
        assert mesures == ref["mesures"], {k: [mesures.get(k), ref["mesures"].get(k)]
            for k in mesures.keys() | ref["mesures"].keys() if mesures.get(k) != ref["mesures"].get(k)}
        assert empreintes == ref["empreintes"], f"Empreintes modifiées sur {scenario} {graine}"
        assert donnees["recit"] == ref["recit"], "Récit modifié"
        assert donnees["souvenirs"] == ref["souvenirs"], "Souvenirs modifiés"
        assert pas == ref["chronique"], f"Chronique modifiée sur {scenario} {graine}"

    analyse = sonde.analyser()
    duree = round(time.perf_counter() - t0, 2)
    return {
        "scenario": scenario,
        "graine": graine,
        "heures": heures,
        "secondes": duree,
        "secondes_sonde": secondes_sonde,
        "secondes_reference": secondes_reference,
        "empreintes": empreintes,
        "sha256_data": sha_etat,
        "mesures": mesures,
        "chronique": pas,
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
                        help="vérifie sur chaque nuit que la sonde ne change ni empreintes ni chronique")
    parser.add_argument("--sortie", required=True, help="fichier JSON où enregistrer le rapport complet")
    args = parser.parse_args(argv)

    banc_pnj.ceder()
    resultats = []
    totaux = Counter()
    familles = Counter()
    par_scenario = {}

    for scenario in args.scenarios:
        c_scen = Counter()
        for graine in args.graines:
            r = jouer_nuit_sondee(
                scenario,
                graine,
                heures=args.heures,
                verifier_empreinte=args.verifier_empreinte,
            )
            resultats.append(r)
            chemin = Path(args.sortie)
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(json.dumps({"provisoire": True, "nuits": resultats}, ensure_ascii=False), encoding="utf-8")
            a = r["analyse"]
            for k, v in a["comptes"].items():
                totaux[k] += v
                c_scen[k] += v
            for k, v in a["par_famille_non_justifiee"].items():
                familles[f"{scenario}:{k}"] += v
            print(
                f"[{scenario} {graine}] {r['secondes']:.1f}s | "
                f"non_justifiés={a['total_non_justifies']} "
                f"classes={a['comptes']} | "
                f"à_expliquer={a['total_a_expliquer']} | cycles_accomplis={a['total_cycles_accomplis']}",
                flush=True,
            )
        par_scenario[scenario] = {
            "services_par_classe": dict(sum((Counter(r["analyse"]["services_par_classe"])
                                             for r in resultats if r["scenario"] == scenario), Counter())),
            "comptes": dict(c_scen),
            "total_derives_ouvertes": sum(r["analyse"]["total_derives_ouvertes"]
                                          for r in resultats if r["scenario"] == scenario),
            "total_services_etat_perdu": sum(r["analyse"]["total_services_etat_perdu"]
                                             for r in resultats if r["scenario"] == scenario),
            "total_non_justifies": c_scen.get("repetition_sans_entree_nouvelle", 0),
            "total_a_expliquer": c_scen.get("entree_nouvelle_a_expliquer", 0),
            "total_cycles_accomplis": (
                c_scen.get("cycle_accompli", 0) + c_scen.get("garde_interruption_accomplie", 0)
            ),
        }

    synthese = {
        "services_par_classe": dict(sum((Counter(r["analyse"]["services_par_classe"])
                                         for r in resultats), Counter())),
        "parametres": {
            "scenarios": args.scenarios,
            "graines": args.graines,
            "heures": args.heures,
            "nb_nuits": len(resultats),
        },
        "totaux_comptes": dict(totaux),
        "total_derives_ouvertes": sum(r["analyse"]["total_derives_ouvertes"] for r in resultats),
        "total_services_etat_perdu": sum(r["analyse"]["total_services_etat_perdu"] for r in resultats),
        "total_non_justifies": totaux.get("repetition_sans_entree_nouvelle", 0),
        "total_a_expliquer": totaux.get("entree_nouvelle_a_expliquer", 0),
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
        f"à_expliquer={synthese['total_a_expliquer']} | cycles_accomplis={synthese['total_cycles_accomplis']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
