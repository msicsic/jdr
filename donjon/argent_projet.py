"""Recours d'acquisition monétaire, devisés sur les connaissances du porteur.

Les marchés restent hors du graphe : la marche et la parole sont cherchées,
le travail et le bien cédé sont chiffrés par leurs devis communs. Aucun accord
ni richesse adverse n'est supposé acquis.
"""
import json

from .esprits import lire


def _borne_marche(valeur_but, valeur_gain, peine=0):
    from .planification import DEMANDE
    return (1 + DEMANDE + peine) * valeur_but / valeur_gain if valeur_gain else float("inf")


def obtenir(monde, id, montant, budget):
    from .biens import richesse, prix, proprietaire
    from .caractere import ARGENT, valeur_pieces
    from .deliberation import _connus, besoin_de_part, parts
    from .echanges import (garde, valeur_proposition, offre_sensee,
                           _devis_proposition, PRIX_SANS_PRIX, PAS_PROPOSITION)
    from .planification import (devis_enrichissement, chercher, _etape,
                                prix_tache, DEMANDE, SALAIRE, _couper)
    from .pnj_propositions import offre_refusee
    from .propositions import taches_crues
    from .relations import chance_demande, chance_proposition
    from .spatial import porte_par
    manque = montant - richesse(monde, id)
    if manque <= 0:
        return None
    valeur_but = valeur_pieces(monde, id, manque)
    candidats = []

    def ajouter(cout, gain, etapes, cle):
        # Minutes attendues par fraction du manque couvert. Un bien cédé et
        # une tâche ne sont pas gratuits ; un gain partiel n'est pas le but entier.
        valeur_gain = valeur_pieces(monde, id, min(manque, gain))
        if valeur_gain > 0 and cout < budget:
            candidats.append((cout * valeur_but / valeur_gain, cle, etapes))

    def peut_battre(gain, peine=0):
        if not candidats:
            return True
        valeur_gain = valeur_pieces(monde, id, min(manque, gain))
        # Une parole prend une minute ; sa chance n'excède jamais 1.
        return _borne_marche(valeur_but, valeur_gain, peine) <= min(c[0] for c in candidats)

    prise = devis_enrichissement(monde, id)
    if prise:
        cout, but, etapes = prise
        connu = lire(monde, id)["croyances"].get(but["objet"], {}).get("pieces", {})
        ajouter(cout, connu.get("valeur", 0), etapes, ("prise", but["objet"]))

    biens = []
    for objet, o in sorted(monde.objets.items()):
        if (porte_par(monde, objet, id) and proprietaire(monde, objet) == id
                and o.get("mobile") and o["type"] not in ("personnage", "depouille")
                and not garde(monde, id, o) and "pieces" not in o):
            part = besoin_de_part(o) is not None
            if not part or parts(o) > 0:
                biens.append(({"type": "part" if part else "objet", "objet": objet},
                              prix(monde, objet, part) or PRIX_SANS_PRIX))
    connus = _connus(monde, id)
    for autre in sorted(connus):
        if autre == id or not monde.objets.get(autre, {}).get("profil"):
            continue
        devis, offres = {}, []
        termes = [(t, n) for t, n in biens if peut_battre(n)]
        # prix_tache(c)=ceil(c/SALAIRE) : gagner n pièces par travail
        # exige au moins (n-1)*SALAIRE minutes. Cette borne optimiste ne
        # supprime aucun meilleur moyen, même avant d'en connaître la tâche.
        if any(peut_battre(n, (n - 1) * SALAIRE)
               for n in range(1, min(manque, prix_tache(budget)) + 1)):
            for terme in taches_crues(monde, id, autre):
                travail = _devis_proposition(monde, id, terme["condition"], autre, devis)
                if travail:
                    termes.append((terme, prix_tache(travail[0])))
        for terme, prix_ in termes:
            demande = {"type": "pieces", "montant": min(manque, prix_)}
            if offre_refusee(monde, id, autre, autre, terme):
                continue
            if not offre_sensee(monde, id, autre, demande, terme, devis=devis):
                continue
            cout = valeur_proposition(monde, id, terme, autre, devis=devis)
            if cout is None:
                continue
            chance = chance_proposition(chance_demande(monde, id, autre), cout / PAS_PROPOSITION)
            # La valeur du bien cédé est compensée par le prix reçu, déjà
            # vérifié par offre_sensee. Ne pas la compter une seconde fois
            # comme temps de travail. Une tâche garde son effort devisé.
            peine = cout if terme["type"] == "tache" else max(
                0, cout - valeur_pieces(monde, id, demande["montant"]))
            offres.append((peine + DEMANDE / chance, demande, terme))
        if not offres:
            continue
        parole = _etape("proposer", autre)
        route = chercher(monde, id, lambda v, e: bool(e.fait("parle", autre)),
                         {"parole": [parole]}, nom="marche_pieces:" + autre,
                         memo=["marche_pieces", autre], emplois=(), motif=ARGENT,
                         endurer=budget)
        if not route:
            continue
        for cout, demande, terme in offres:
            etapes = route[1][:-1] + [_etape("proposer", autre, contenu={
                "demande": demande, "contrepartie": terme})]
            ajouter(route[0] + cout, demande["montant"], etapes,
                    ("marche", autre, json.dumps(terme, sort_keys=True)))
    if not candidats:
        return None
    # Les annotations de projection (suppose, part_estimee...) appartiennent
    # au devis. Comme tout recours, ne publier que son préfixe exécutable.
    return _couper(min(candidats, key=lambda c: (c[0], c[1]))[2])
