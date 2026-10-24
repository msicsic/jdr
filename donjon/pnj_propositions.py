"""Offres du planificateur : moyens propres, valeur crue et coût de la parole donnée.

L'estimation ne consulte ni les relations, ni les besoins, ni les engagements privés
de l'auditeur. L'accord réel appartient exclusivement à echanges.proposer.
"""
from . import agendas, relations
from .deliberation import _lieu_cru, salle_crue

# Un seul devis récent par couple, sous les entrées complètes de la recherche.
_DEVIS = {}


def conditions(v, autre):
    """Services suggérés par les biens connus de l'autre, sans lire son agenda."""
    for o in v.connus:
        if v.proprietaire[o] != autre and not (
                v.proprietaire[o] is None and salle_crue(v.monde, v.id, o) == salle_crue(v.monde, v.id, autre)):
            continue
        x = v.objets[o]
        if "allume" in x:
            yield {"objet": o, "allume": True}
        if "verrouillee" in x and (v.cru(o, "verrouillee") is False or (v.cru(o, "etat") or {}).get("ouverte")):
            yield {"objet": o, "verrouillee": True}


def _taches(v, autre):
    from .echanges import _devis_proposition
    def calculer():
        from . import planification as p
        cle = v._memo(("entrees_propositions",), lambda: p._entrees(v, {}, p.PROFONDEUR, p.NOEUDS))
        precedent = _DEVIS.get((v.id, autre))
        if precedent is not None and precedent[0] == cle and not p.VERIFIER:
            return precedent[1]
        offres = []
        for condition in conditions(v, autre):
            if agendas.en_cours(v.monde, v.id, condition=condition, personne=autre, actifs=True):
                continue
            devis = _devis_proposition(v.monde, v.id, condition, autre)
            if devis and devis[1]:
                offres.append(({"type": "tache", "condition": condition}, devis[0]))
        if p.VERIFIER and precedent is not None and precedent[0] == cle:
            assert precedent[1] == offres, "Devis de proposition périmé"
        _DEVIS[v.id, autre] = cle, offres
        return offres
    return v._memo(("offres_taches", autre), calculer)


def offres(v, e, autre):
    from .caractere import prix_faute
    from .echanges import valeur_proposition
    # Les pièces s'offrent au prix connu du bien demandé ; le montant est ajouté par gestes.
    for o in sorted(e.portes):
        x = v.objets[o]
        if v.proprietaire.get(o) != v.id or not x.get("mobile") or e.fait("offert", o):
            continue
        if x["type"] in ("personnage", "depouille"):
            continue
        part = v.besoin[o] is not None
        terme = {"type": "part" if part else "objet", "objet": o}
        if part and not v.disponible(o):
            continue
        cout = valeur_proposition(v.monde, v.id, terme, autre)
        from .deliberation import parts
        garde = part and parts(x) > 1
        yield terme, cout, e.portes if garde else e.portes - {o}, [(("offert", o), True),
              *([] if garde else [(("lieu", o), autre)])], 0
    # Un devis porte sur les moyens présents, pas sur des acquisitions encore hypothétiques.
    if e.portes != frozenset(o for o in v.connus if _lieu_cru(v.monde, v.id, o) == v.id):
        return
    faute = prix_faute(v.monde, v.id, v.motif)
    for terme, cout in _taches(v, autre):
        condition = terme["condition"]
        if e.fait("promesse_offerte", condition["objet"]):
            continue
        faits = [(("promesse_offerte", condition["objet"]), True)]
        yield terme, cout, e.portes, faits, 0
        # Deux voies dans le même graphe : le prix de faute peut varier sans changer les gestes.
        if faute is not None:
            yield terme, 0, e.portes, faits + [(("faute", autre, "honnetete"), True)], int(not e.fait("faute", autre, "honnetete"))


def valeur_crue(v, autre, terme, cout=0):
    """Valeur espérée pour l'autre, avec les seuls prix publics et signes perçus."""
    from .biens import prix
    from .echanges import PRIX_SANS_PRIX
    if terme["type"] == "pieces":
        return terme["montant"]
    if terme["type"] == "tache":
        c = terme["condition"]
        # La promesse dite est la même, qu'il compte la tenir ou la trahir.
        cout = next(prix for t, prix in _taches(v, autre) if t == terme)
        etat = v.cru(c["objet"], "etat") or {}
        utile = ("allume" in c and (not etat.get("allume", True) or etat.get("faible"))
                 or "verrouillee" in c and v.cru(c["objet"], "verrouillee") is False
                 or "lieu" in c and _lieu_cru(v.monde, v.id, c["objet"]) != c["lieu"])
        return cout / 5 if utile else 0
    o = terme["objet"]
    besoin = v.besoin[o]
    etat = v.cru(autre, "etat") or {}
    return (prix(v.monde, o, terme["type"] == "part") or PRIX_SANS_PRIX) * (
        2 if besoin and etat.get(besoin) else 1)


def gestes(v, e, vises, but):
    from . import planification as p
    from .biens import prix
    demandes = []
    objets, utiles = v.agissables(vises)
    for o in objets:
        autre = v.proprietaire[o]
        if autre in (None, v.id, "joueur") or autre not in v.chances_demandes or v.salle(e, autre) != e.salle:
            continue
        if o in e.portes or e.fait("offert", o) or v.retenu(autre, ("proposer",), o):
            continue
        if v.besoin[o] and v.disponible(o):
            final = e.apres(faits=[(("part", o), autre)])
            # La part alimentaire est remise puis mangée réellement au plan suivant.
            if but and but(v, final):
                demandes.append((autre, {"type": "part", "objet": o}, final, 1))
            elif "combustible" in v.objets[o].get("usages", ()) and (vises.get("entretenir") or v.emploie_lumiere):
                demandes.append((autre, {"type": "part", "objet": o}, None, 0))
        elif o in utiles and v.lieu(e, o) == autre:
            final = e.apres(portes=e.portes | {o}, faits=[(("acquis", o), True), (("permis", o), True)])
            demandes.append((autre, {"type": "objet", "objet": o}, final, 0))
    for condition in vises.get("confier", ()):
        for autre in v.personnes():
            if v.salle(e, autre) == e.salle and not v.retenu(autre, ("proposer",), condition["objet"]):
                demandes.append((autre, {"type": "tache", "condition": dict(condition)},
                                 e.apres(faits=p.effets_tache(condition)), p.peine_tache(v, e, condition) or p.TACHE))
    for autre, demande, final, suite in demandes:
        o = demande.get("objet") or demande["condition"]["objet"]
        contreparties = list(offres(v, e, autre))
        montant = (prix(v.monde, o, demande["type"] == "part") or 1) if demande["type"] != "tache" else p.prix_tache(suite)
        if v.piece and v.richesse - (e.fait("depense") or 0) >= montant:
            contreparties.append(({"type": "pieces", "montant": montant}, v.depense(montant), e.portes,
                                   [(("depense",), (e.fait("depense") or 0) + montant)], 0))
        for terme, cout, portes, faits, fautes in contreparties:
            if terme.get("objet") == o or terme.get("condition") == demande.get("condition") and terme["type"] == "tache":
                continue
            gain = valeur_crue(v, autre, terme, cout)
            chance = relations.chance_proposition(v.chances_demandes[autre], gain)
            contenu = {"demande": demande, "contrepartie": terme}
            etape = {**p._etape("proposer", autre, outil=o if demande["type"] != "tache" else "", contenu=contenu),
                     "suppose": True}
            minutes = (1 + p.DEMANDE + cout) / chance + suite
            if final is None:
                # Même devis de remise que les demandes de combustible : aucune source
                # n'est réputée rechargée avant la remise et les gestes réels suivants.
                depuis = e.apres(portes=portes, faits=faits)
                mesure = p._mesurer(v, e, [etape], depuis, 1)
                if mesure is None:
                    continue
                duree, pression, depuis = mesure
                from .part_estimee import suites
                v._estime_part = True
                try:
                    estimations = suites(v, depuis, o, vises, but)
                finally:
                    v._estime_part = False
                for mal, cout_suite, fin, abime in estimations:
                    yield (fautes + mal, minutes + duree - 1 + pression + cout_suite,
                           [etape], fin.apres(faits=[(("estimation",), True)]), 0, abime)
                continue
            # On ne peut réutiliser comme outil ou comme paiement un bien déjà cédé.
            suivant = final.apres(portes=(final.portes - (e.portes - portes)), faits=faits)
            yield fautes, minutes, [etape], suivant, 1
