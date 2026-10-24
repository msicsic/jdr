"""Un recours après le choix ordinaire ; aucune lecture depuis la recherche.

Contreparties portées et chance reprises du lot 36, sans gestes projetés ni devis
de tâches. L'auditeur seul évalue le marché réel, par le contrat du joueur.
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
    from .echanges import valeur_proposition, PRIX_SANS_PRIX
    from .spatial import porte_par
    for o, x in sorted(monde.objets.items()):
        if (o == demande["objet"] or not porte_par(monde, o, id)
                or proprietaire(monde, o) != id or not x.get("mobile")
                or x["type"] in ("personnage", "depouille")):
            continue
        part = besoin_de_part(x)
        if part and parts(x) <= 0:
            continue
        terme = {"type": "part" if part else "objet", "objet": o}
        cout = valeur_proposition(monde, id, terme, autre)
        etat = lire(monde, id)["croyances"].get(autre, {}).get("etat", {}).get("valeur", {})
        gain = (prix(monde, o, bool(part)) or PRIX_SANS_PRIX) * (2 if part and etat.get(part) else 1)
        yield terme, cout, gain
    montant = min(richesse(monde, id), prix(monde, demande["objet"], demande["type"] == "part") or PRIX_SANS_PRIX)
    if montant:
        terme = {"type": "pieces", "montant": montant}
        yield terme, valeur_proposition(monde, id, terme, autre), montant


def _entrees(monde, id, autre, besoin, demande):
    from .deliberation import moyens_crus, _connus, parts
    from .biens import proprietaire, richesse
    from .spatial import porte_par
    causes = []
    for o in _connus(monde, id):
        if proprietaire(monde, o) == autre:
            for f in moyens_crus(monde, id, {"de": autre, "operation": "proposer", "objet": o}):
                if f not in causes:
                    causes.append(f)
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
        if (autre not in _connus(monde, id) or not monde.objets.get(autre, {}).get("profil")
                or salle_crue(monde, id, autre) != monde.objets[id]["lieu"]):
            continue
        # Il sait où le trouver ; la marche sociale normale le rejoint au contact.
        entrees = _entrees(monde, id, autre, besoin, demande)
        avant = next((x for x in e["recours_propositions"] if x["de"] == autre and x["besoin"] == besoin), None)
        if avant and _tient(avant, entrees):
            continue
        chance = relations.chance_demande(monde, id, autre)
        offres = [(relations.chance_proposition(chance, gain), -cout, t)
                  for t, cout, gain in _contreparties(monde, id, autre, demande)]
        offres = [o for o in offres if o[0] > chance]
        if not offres:
            continue
        # Prix propre de l'essai par chance d'accord, puis chance pour les ex aequo.
        _, _, terme = min(offres, key=lambda x: (-x[1] / x[0], -x[0]))
        return {"operation": "proposer", "cible": autre, "outil": demande["objet"], "lieu": "",
                "condition": "", "contenu": {"demande": demande, "contrepartie": terme}}
    return None


def executer(monde, id, autre, contenu, lignes):
    from .echanges import proposer
    from .deliberation import retenir_refus
    from .propositions import en_mots, cites_terme
    from .pnj import _chroniquer
    from .social import _qui, faire_entendre
    demande, terme = contenu["demande"], contenu["contrepartie"]
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
        retenir_refus(monde, id, autre, "proposer", issue, objet=demande["objet"], besoin=besoin)
    recit = f"{_qui(monde, id)} propose à {_qui(monde, autre)} {en_mots(monde, terme)} contre {en_mots(monde, demande)}"
    _chroniquer(monde, id, f"{recit} ({issue}).", "social")
    reponse = (f"{_qui(monde, autre)} accepte l'échange."
               + (" La remise est promise." if bilan.get("livraison_differee") else " Les biens convenus sont remis.")
               if not bilan["cause"] else f"{_qui(monde, autre)} refuse l'échange.")
    faire_entendre(monde, id, autre, recit + ".", cites_terme(demande) + cites_terme(terme), lignes,
                   reponse=reponse)
    return True  # L'offre est achevée même refusée : la suite sera délibérée de nouveau.
