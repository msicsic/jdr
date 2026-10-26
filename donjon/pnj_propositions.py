"""Un recours après le choix ordinaire ; aucune lecture depuis la recherche.

Contreparties portées puis service autonome, sans geste de marché dans la
recherche. L'auditeur évalue le marché réel par le contrat du joueur.
"""
from . import relations
from .esprits import lire, memoriser


def verifier(e):
    def cible(x):
        return isinstance(x, dict) and all(isinstance(x.get(k), str) for k in ("de", "besoin", "objet"))
    assert e["demande_refusee"] is None or cible(e["demande_refusee"]), "Déclencheur de recours invalide"
    assert isinstance(e["recours_propositions"], list) and all(
        cible(x) and isinstance(x.get("cause"), list) and isinstance(x.get("lien"), dict)
        and type(x.get("pieces")) is int and x["pieces"] >= 0 and isinstance(x.get("biens"), dict)
        and all(isinstance(o, str) and type(n) is int and n >= 0 for o, n in x["biens"].items())
        for x in e["recours_propositions"]), "Tentatives de proposition invalides"


def _demande(monde, objet):
    from .deliberation import besoin_de_part
    o = monde.objets.get(objet, {})
    if not o.get("mobile") or o.get("type") in ("personnage", "depouille"):
        return None
    return {"type": "part" if besoin_de_part(o) else "objet", "objet": objet}


def _contreparties(monde, id, autre, demande):
    from .biens import prix, richesse, proprietaire
    from .deliberation import besoin_de_part, parts
    from .echanges import valeur_proposition, PRIX_SANS_PRIX, offre_sensee
    from .spatial import porte_par
    from .propositions import demande_financee
    for o, x in sorted(monde.objets.items()):
        if (o == demande["objet"] or not porte_par(monde, o, id)
                or proprietaire(monde, o) != id or not x.get("mobile")
                or x["type"] in ("personnage", "depouille")):
            continue
        part = besoin_de_part(x)
        if part and parts(x) <= 0:
            continue
        terme = {"type": "part" if part else "objet", "objet": o}
        if not offre_sensee(monde, id, autre, demande_financee(monde, id, demande, terme), terme):
            continue
        cout = valeur_proposition(monde, id, terme, autre)
        etat = lire(monde, id)["croyances"].get(autre, {}).get("etat", {}).get("valeur", {})
        gain = (prix(monde, o, bool(part)) or PRIX_SANS_PRIX) * (2 if part and etat.get(part) else 1)
        yield terme, cout, gain
    montant = (0 if demande["type"] == "pieces" else min(richesse(monde, id),
               prix(monde, demande["objet"], demande["type"] == "part") or PRIX_SANS_PRIX))
    if montant and offre_sensee(monde, id, autre, demande, {"type": "pieces", "montant": montant}):
        terme = {"type": "pieces", "montant": montant}
        yield terme, valeur_proposition(monde, id, terme, autre), montant


def _entrees(monde, id, autre, besoin, demande):
    from .deliberation import moyens_crus, parts
    from .biens import proprietaire, richesse
    from .spatial import porte_par
    causes = moyens_crus(monde, id, {"de": autre, "operation": "proposer", "objet": demande["objet"]})
    return {"de": autre, "besoin": besoin, "objet": demande["objet"],
            "cause": causes, "lien": dict(relations.axes(monde, id, autre)),
            "pieces": richesse(monde, id),
            "biens": {o: parts(x) for o, x in monde.objets.items()
                      if porte_par(monde, o, id) and proprietaire(monde, o) == id}}


def _tient(avant, apres):
    # Comme moyens_crus/tient : perdre un moyen ou revoir le même ne relance pas.
    return (all(f in avant["cause"] for f in apres["cause"])
            and all(apres["lien"][k] <= avant["lien"][k] for k in ("confiance", "affection", "dette"))
            and all(apres["lien"][k] >= avant["lien"][k] for k in ("rancune", "peur"))
            and apres["pieces"] <= avant["pieces"]
            and all(o in avant["biens"] and n <= avant["biens"][o] for o, n in apres["biens"].items()))


def entrees_refus(monde, id, autre, objet, terme):
    """Les moyens de cette demande et la force réellement offerte, pas la fortune disponible."""
    from .biens import prix, proprietaire
    from .deliberation import moyens_crus
    from .echanges import PRIX_SANS_PRIX
    from .spatial import porte_par
    if terme["type"] == "tache":
        from .echanges import valeur_proposition, PAS_PROPOSITION
        gain = (valeur_proposition(monde, id, terme, autre) or 0) / PAS_PROPOSITION
    else:
        gain = (terme["montant"] if terme["type"] == "pieces" else
                prix(monde, terme["objet"], terme["type"] == "part") or PRIX_SANS_PRIX)
    cause = moyens_crus(monde, id, {"de": autre, "operation": "proposer", "objet": objet})
    cause += [["porte", o, id, None] for o in sorted(monde.objets)
              if porte_par(monde, o, id) and proprietaire(monde, o) == id]
    cause.append(["inventaire", id, None, None])
    return {"cause": cause,
            "gain": gain}


def refus_tient(monde, id, refus, terme):
    apres = entrees_refus(monde, id, refus["de"], refus["objet"], terme)
    avant = refus["offre"]
    # Le temps, le retour d'un bien déjà proposé et l'argent non offert ne sont
    # pas un meilleur marché. La perte d'un moyen ne lève pas non plus le refus.
    if apres["gain"] > avant["gain"]:
        return False
    # Seul le bien effectivement offert peut être un nouveau moyen porté.
    # Les captures anciennes, sans inventaire, restent conservatrices.
    portes = [f for f in avant["cause"] if f[0] == "porte"]
    nouveau = ["porte", terme.get("objet"), id, None]
    if ["inventaire", id, None, None] in avant["cause"] and nouveau in apres["cause"] and nouveau not in portes:
        return False
    # Les abords d'une salle ne changent ni la garde ni la nécessité d'un bien,
    # ni le jugement du marché. Ils ne concernent que son exécution matérielle.
    if refus["raison"] in ("impossible", "absent", "portee", "epuise", "propriete"):
        from .deliberation import _lieu_cru
        # Le contenant de la demande conditionne sa remise ; les autres portes
        # de sa salle ne sont pas des moyens nouveaux pour ce marché.
        contenants, lieu = set(), _lieu_cru(monde, id, refus["objet"])
        while lieu in monde.objets and lieu not in contenants and monde.objets[lieu]["type"] == "contenant":
            contenants.add(lieu)
            lieu = _lieu_cru(monde, id, lieu)
        def pertinent(f):
            return (f[0] == "moyen" or f[0] == "ouvert" and f[1] in contenants
                    or f[0] == "cle" and any(o in monde.objets[f[1]].get("ouvre", []) for o in contenants))
        return all(f in avant["cause"] for f in apres["cause"] if pertinent(f))
    return all(f in avant["cause"] for f in apres["cause"]
               if f[0] == "moyen" and f[2] == refus["de"])


def offre_refusee(monde, id, autre, objet, terme):
    """Même contrat au choix du recours et à l'exécution d'un marché sauvegardé."""
    return any(s["de"] == autre and s.get("objet") == objet
               and s["operation"] in ("acheter", "proposer") and "offre" in s
               and refus_tient(monde, id, s, terme) for s in lire(monde, id)["refus"])


def plan_recours(monde, id, besoin, etapes):
    """La condition entendue est un moyen, après les moyens ordinaires seulement.

    Aucune comparaison de marchés dans la recherche : le service utilise son
    planificateur existant, puis le demandeur revient réclamer la contrepartie.
    """
    from .biens import richesse
    from .echanges import condition_remplie
    from .planification import planifier_pulsion, rejoindre
    e = lire(monde, id)
    refusee = e["demande_refusee"]
    if refusee and refusee["besoin"] == besoin:
        for s in reversed(e["refus"]):
            if s["de"] != refusee["de"] or s.get("objet") != refusee["objet"] or "contre_offre" not in s:
                continue
            if etapes and not any(g["condition"] == "sans_temoin" for g in etapes):
                return None  # Les moyens ordinaires sans faute gardent la priorité.
            offre = s["contre_offre"]
            terme = offre["condition"]
            autre, objet = s["de"], s["objet"]
            prix = terme.get("montant", 0)
            demande = {"operation": "acheter" if prix else "demander", "cible": autre,
                       "outil": objet, "lieu": "", "condition": "",
                       "contenu": {"prix": prix} if prix else {}}
            if prix or condition_remplie(monde, id, s):
                if prix > richesse(monde, id):
                    return None
                route = rejoindre(monde, id, autre)
                return [*route[0], demande] if route and route[1] else None
            trouve = planifier_pulsion(monde, id, terme["condition"])
            if not trouve or any(g["condition"] == "sans_temoin" for g in trouve[1]):
                return None
            # Le refus reste le but à poursuivre après le service, même rechargé.
            return trouve[1]
    geste = recours(monde, id, besoin, etapes)
    return [geste] if geste else None


def recours(monde, id, besoin, etapes):
    """Une seule offre avant la faute retenue, ou après la demande refusée."""
    from .biens import proprietaire
    from .deliberation import _connus, salle_crue, refus_retenu
    e, candidats = lire(monde, id), []
    # Les demandes ordinaires du préfixe gardent leur chance avant tout recours.
    for n, geste in enumerate(etapes):
        if geste["operation"] in ("demander", "acheter", "confier", "engager", "proposer"):
            break
        if geste["condition"] != "sans_temoin":
            continue
        cible = geste["cible"]
        autre = proprietaire(monde, cible) if cible in monde.objets else None
        if autre and autre not in (id, "joueur"):
            # Le bien visé après le contenant forcé, plutôt que la cession du contenant.
            for suite in etapes[n:]:
                o = suite["cible"]
                demande = _demande(monde, o)
                if demande and proprietaire(monde, o) == autre:
                    candidats.append((autre, demande))
                    break
        break
    refusee = e["demande_refusee"]
    if refusee and refusee["besoin"] == besoin:
        autre, o = refusee["de"], refusee["objet"]
        if refus_retenu(monde, id, autre, ("demander", "acheter"), objet=o):
            demande = _demande(monde, o)
            if demande:
                candidats.append((autre, demande))
    for autre, demande in candidats:
        from .propositions import demande_utile
        demande = demande_utile(monde, id, demande)
        if demande is None:
            continue
        if (autre not in _connus(monde, id) or not monde.objets.get(autre, {}).get("profil")
                or salle_crue(monde, id, autre) != monde.objets[id]["lieu"]):
            continue
        # Il sait où le trouver ; la marche sociale normale le rejoint au contact.
        entrees = _entrees(monde, id, autre, besoin, demande)
        avant = next((x for x in e["recours_propositions"] if x["de"] == autre and x["besoin"] == besoin), None)
        refus = [s for s in e["refus"] if s["de"] == autre and s.get("objet") == demande["objet"]
                 and s["operation"] in ("acheter", "proposer") and "offre" in s]
        if not refus and avant and _tient(avant, entrees):
            continue
        chance = relations.chance_demande(monde, id, autre)
        offres = [(relations.chance_proposition(chance, gain), -cout, t)
                  for t, cout, gain in _contreparties(monde, id, autre, demande)
                  if not any(refus_tient(monde, id, s, t) for s in refus)]
        offres = [o for o in offres if o[0] > chance]
        if not (avant and _tient(avant, entrees)):
            from .propositions import taches_crues
            from .echanges import offre_sensee, valeur_proposition, PAS_PROPOSITION
            # Un seul service devisé par recours, après les biens et pièces.
            terme = next(taches_crues(monde, id, autre), None)
            devis = {}
            if terme and offre_sensee(monde, id, autre, demande, terme, devis=devis):
                cout = valeur_proposition(monde, id, terme, autre, devis=devis)
                if cout is not None and cout > 0 and not any(refus_tient(monde, id, s, terme) for s in refus):
                    offres.append((relations.chance_proposition(chance, cout / PAS_PROPOSITION), -cout, terme))
        if not offres:
            continue
        # Prix propre de l'essai par chance d'accord, puis chance pour les ex aequo.
        _, _, terme = min(offres, key=lambda x: (-x[1] / x[0], -x[0]))
        from .propositions import demande_financee
        demande = demande_financee(monde, id, demande, terme)
        return {"operation": "proposer", "cible": autre, "outil": demande["objet"], "lieu": "",
                "condition": "", "contenu": {"demande": demande, "contrepartie": terme}}
    return None


def executer(monde, id, autre, contenu, lignes):
    from .echanges import proposer, offre_sensee
    from .deliberation import retenir_refus
    from .propositions import en_mots, cites_terme
    from .pnj import _chroniquer
    from .social import _qui, faire_entendre
    demande, terme = contenu["demande"], contenu["contrepartie"]
    if offre_refusee(monde, id, autre, demande["objet"], terme):
        return False
    if not offre_sensee(monde, id, autre, demande, terme):
        return False
    e = lire(monde, id)
    besoin = e["intention"]["motif"]
    entrees = _entrees(monde, id, autre, besoin, demande)
    bilan = proposer(monde, id, autre, demande, terme)
    e = lire(monde, id)
    e["recours_propositions"][:] = [x for x in e["recours_propositions"]
                                      if (x["de"], x["besoin"]) != (autre, besoin)]
    e["recours_propositions"].append(entrees)
    e["demande_refusee"] = None
    issue = bilan["cause"] or "accepte"
    memoriser(monde, id, {"type": "proposition", "a": autre, "demande": demande,
                          "contrepartie": terme, "issue": issue})
    if bilan["cause"]:
        retenir_refus(monde, id, autre, "proposer", issue, objet=demande["objet"], besoin=besoin,
                      offre=entrees_refus(monde, id, autre, demande["objet"], terme))
    recit = f"{_qui(monde, id)} propose à {_qui(monde, autre)} {en_mots(monde, terme)} contre {en_mots(monde, demande)}"
    _chroniquer(monde, id, f"{recit} ({issue}).", "social")
    reponse = (f"{_qui(monde, autre)} accepte l'échange."
               + (" La remise est promise." if bilan.get("livraison_differee") else " Les biens convenus sont remis.")
               if not bilan["cause"] else f"{_qui(monde, autre)} refuse l'échange.")
    faire_entendre(monde, id, autre, recit + ".", cites_terme(demande) + cites_terme(terme), lignes,
                   reponse=reponse)
    return True  # L'offre est achevée même refusée : la suite sera délibérée de nouveau.
