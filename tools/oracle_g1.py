"""Oracle fermé G1 : relire des preuves annotées, jamais lancer le jeu ou Luna.

Les jugements de sens sont humains et versionnés, liés à toute l'observation
(charges, refus, texte publié, état rechargé). Une preuve nouvelle reste inconnue.
Les contrats typés obligatoires sont en outre vérifiés par un petit langage de
prédicats, sans branche par scénario dans le classificateur.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics

BASE = Path(__file__).resolve().parents[1]
ORACLE = BASE / "tests/data/oracle_g1.json"


def lire(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def empreinte(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def compilations(tour):
    """Une reprise après conversation est de la narration, pas une compilation."""
    result = []
    for event in tour.get("fil", []):
        if event.get("etape") != "appel" or event.get("fonction") != "repondre_au_joueur":
            continue
        faits = event.get("entree", {}).get("faits", {})
        if "conversation_validee" in faits:
            continue
        charges = [json.loads(x["arguments"]) for x in event.get("brut", [])
                   if x.get("type") == "function_call" and x.get("name") == "repondre_au_joueur"]
        if len(charges) != 1:
            raise ValueError("Compilation sans charge unique : preuve incomplète")
        result.append(charges[0])
    return result


def observation(tour):
    """Pas les temps/jetons : le sceau porte sur le sens ET les suites visibles."""
    return {"saisie": tour["saisie"], "candidats": compilations(tour),
            "propositions": tour.get("propositions", []),
            "validations": [e for e in tour.get("fil", []) if e.get("etape") == "validation"],
            "revues": [e.get("rapport") for e in tour.get("fil", [])
                       if e.get("etape") == "couverture de l'action"],
            "refus": tour.get("refus", []), "texte": tour.get("texte", ""),
            "etat_recharge": tour.get("etat")}


ABSENT = object()


def satisfait(value, regle):
    """DSL de données : all/any/not, chemins, égalité, inclusion et ordre exact."""
    if "all" in regle:
        return all(satisfait(value, r) for r in regle["all"])
    if "any" in regle:
        return any(satisfait(value, r) for r in regle["any"])
    if "not" in regle:
        return not satisfait(value, regle["not"])
    for key in regle.get("path", []):
        try:
            value = value[key]
        except (KeyError, IndexError, TypeError):
            value = ABSENT
            break
    if "eq" in regle:
        return value is not ABSENT and value == regle["eq"]
    if "contains" in regle:
        return isinstance(value, (list, str, dict)) and regle["contains"] in value
    if "test" in regle:
        return value is not ABSENT and satisfait(value, regle["test"])
    if "items" in regle:
        return (isinstance(value, list) and len(value) == len(regle["items"])
                and all(satisfait(v, r) for v, r in zip(value, regle["items"])))
    raise ValueError(f"Prédicat inconnu : {regle}")


def classer(tour, cas):
    if tour["saisie"] != cas["saisie"]:
        raise ValueError(f"Saisie déplacée : {cas['id']}")
    obs = observation(tour)
    sceau = empreinte(obs)
    preuve = cas["preuves"].get(sceau)
    # Ne pas prendre le verdict de la revue Luna pour l'oracle de fidélité.
    verdict = preuve.copy() if preuve else {
        "proposition_fidele": "non_evalue", "intention_servie": "non_evalue",
        "admission_moteur": "non_evalue", "execution": "non_evalue",
        "consentement": "non_evalue", "abandon": None}
    cs = obs["candidats"]
    verdict.update(id=cas["id"], famille=cas["famille"], preuve_connue=bool(preuve),
                   admission_premier_coup=len(cs) == 1 and not obs["refus"],
                   admission=verdict["admission_moteur"],
                   texte_vu=obs["texte"], etat_recharge=obs["etat_recharge"],
                   candidats=cs, refus=obs["refus"], sceau=sceau)
    return verdict


def seuils(mesures, familles, reference, obligatoires, inconnus):
    """Aucun axe incomplet n'est vert. Les bornes sont celles de la conception."""
    pertes = [f for f, n in reference.items() if familles.get(f, 0) < n]
    return {
        "I": {"admissions_22": mesures["admissions"] >= 22,
              "fideles_premier_23": mesures["fideles_premier"] >= 23,
              "fideles_finales_27": mesures["fideles_finales"] >= 27,
              "abandons_max_1": mesures["abandons"] <= 1,
              "aucune_famille_perdue": not pertes, "familles_perdues": pertes,
              "zero_substitution_obligatoire": all(obligatoires.values()),
              "aucune_preuve_inconnue": inconnus == 0,
              "nouveaux_refus_avec_contre_epreuve": None},
        "V": {"appels_par_tour_max_3_30": mesures["appels_par_tour"] <= 3.30,
              "un_appel_nominal": mesures["tours_sans_compilation"] == 0,
              "latence_saisie_rendu_mediane_p95": None,
              "latence_confirmation_effet_mediane_p95": None,
              "gain_par_abandon": mesures["abandons"] > 1,
              "objectif_jetons_avant_I": False},
        "F": {"zero_demande_admise_supprimee": None,
              "detail_autre_support_recharges": None,
              "qualification_compatible_incompatible": None,
              "recherche_non_substituee_creation": None,
              "corpus_complementaire": ["atelier", "assemblage", "materiaux", "invention ciblée"]},
        "P": {"cas_obligatoires": obligatoires,
              "contre_offre_acceptation_distinctes": None,
              "mots_ressources_engagements_recharges": None},
        "validation_complete": False,
    }


def rapport(parties, oracle):
    attendus = {c["id"]: c for c in oracle["cas"]}
    tours = {}
    for partie in parties:
        for i, tour in enumerate(partie["tours"]):
            if tour["saisie"] == "quitter":
                continue
            cle = f"{partie['script']}/{i}"
            if cle in tours:
                raise ValueError(f"Position dupliquée : {cle}")
            tours[cle] = tour
    if tours.keys() != attendus.keys():
        raise ValueError(f"Corpus différent : absents={sorted(attendus.keys()-tours.keys())}, "
                         f"inattendus={sorted(tours.keys()-attendus.keys())}")
    lignes = [classer(tours[k], cas) for k, cas in attendus.items()]
    mj = [x for x in lignes if attendus[x["id"]]["modele"]]
    familles = Counter(x["famille"] for x in mj if x["intention_servie"] is True)
    familles_premier = Counter(x["famille"] for x in mj if x["intention_servie"] is True
        and len(x["candidats"]) == 1 and (not x["refus"] or x.get("refus_public_fidele", False)))
    fonctions = Counter(e["fonction"] for t in tours.values() for e in t.get("fil", [])
                        if e.get("etape") == "appel")
    comp_events = []
    for t in tours.values():
        for e in t.get("fil", []):
            if (e.get("etape") == "appel" and e.get("fonction") == "repondre_au_joueur"
                    and not {"conversation_validee"}.intersection(
                        e.get("entree", {}).get("faits", {}))):
                comp_events.append(e)
    nb = len(mj)
    mesures = {"positions": len(lignes), "tours_mj": nb,
               "sans_modele": sum(not t.get("appels") for t in tours.values()),
               "admissions": sum(x["admission_premier_coup"] for x in mj),
               "fideles_premier": sum(x["intention_servie"] is True and
                   len(x["candidats"]) == 1 and (not x["refus"] or
                   x.get("refus_public_fidele", False)) for x in mj),
               "fideles_finales": sum(x["intention_servie"] is True for x in mj),
               "abandons": sum(x["abandon"] is True for x in mj),
               "appels": sum(t.get("appels", 0) for t in tours.values()),
               "appels_par_fonction": dict(fonctions),
               "compilations": len(comp_events),
               "corrections": sum(max(0, len(x["candidats"])-1) for x in mj),
               "tours_sans_compilation": sum(not x["candidats"] for x in mj)}
    mesures["appels_par_tour"] = mesures["appels"] / nb
    for nom, extract in [("jetons_entree", lambda u: u.get("input_tokens", 0)),
                         ("jetons_prefixe", lambda u: u.get("input_tokens_details", {}).get("cached_tokens", 0))]:
        valeurs = [extract(e.get("usage", {})) for e in comp_events]
        mesures[nom + "_moyenne_compilation"] = statistics.mean(valeurs) if valeurs else None
    obligations = {c["nom"]: all(
        next(x for x in lignes if x["id"] == k)["intention_servie"] is True
        and satisfait(observation(tours[k]), c["contrats"][k]) for k in c["positions"])
                   for c in oracle["obligatoires"] if c["positions"]}
    # Les preuves complémentaires ne changent jamais le dénominateur des 30.
    obligations.update({c["nom"]: None for c in oracle["obligatoires"] if not c["positions"]})
    inconnus = sum(not x["preuve_connue"] for x in lignes)
    return {"mesures": mesures, "familles": dict(familles),
            "familles_premier": dict(familles_premier), "inconnus": inconnus,
            "issues": {k: dict(Counter(str(x[k]) for x in lignes))
                       for k in ("proposition_fidele", "admission", "execution", "consentement")},
            "axes": seuils(mesures, familles, oracle["familles_reference"], obligations, inconnus),
            "tours": lignes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--archives", type=Path, help="Racine artifacts des fils figés")
    group.add_argument("--campagne", nargs="+", type=Path, help="Six fichiers d'une nouvelle campagne")
    parser.add_argument("--oracle", type=Path, default=ORACLE)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    oracle = lire(args.oracle)
    result = {"oracle_sha256": hashlib.sha256(args.oracle.read_bytes()).hexdigest(),
              "reference_318": "230e7b3", "reference_demandee": "c9459ce",
              "rejeu_moteur": False, "appel_modele": False, "campagnes": {}}
    if args.campagne:
        result["campagnes"]["nouvelle"] = rapport([lire(p) for p in args.campagne], oracle)
    elif args.archives:
        groupes = defaultdict(list)
        for source in oracle["sources"]:
            path = args.archives / source["path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
                raise ValueError(f"Archive modifiée : {path}")
            groupes[source["campagne"]].append(lire(path))
        for nom, parties in groupes.items():
            result["campagnes"][nom] = rapport(parties, oracle)
        result["complements"] = []
        for source in oracle.get("complements", []):
            path = args.archives / source["path"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
                raise ValueError(f"Archive complémentaire modifiée : {path}")
            tour = lire(path)["tours"][source["tour"]]
            if empreinte(observation(tour)) != source["observation_sha256"]:
                raise ValueError(f"Preuve complémentaire modifiée : {source['id']}")
            contrat = next(c["contrat"] for c in oracle["obligatoires"]
                           if c["nom"] == source["obligation"])
            result["complements"].append({**source,
                "contrat_satisfait": satisfait(compilations(tour)[-1], contrat),
                "texte_vu": tour["texte"], "etat_recharge": tour.get("etat")})
    else:
        parser.error("Choisir --archives ou --campagne")
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: {"mesures": v["mesures"], "inconnus": v["inconnus"]}
                      for k, v in result["campagnes"].items()}, ensure_ascii=False, indent=2))
    return int(any(v["inconnus"] for v in result["campagnes"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
