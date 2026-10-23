"""Prix d'une suite après remise, sans développer ses états dans la recherche.

La prévision reste dans les croyances du demandeur. Elle n'est jamais exécutée :
le moteur attend la vraie part puis refait un plan. Le reste du but est approché
par un trajet et un geste conclusif ; les autres préparatifs restent dans le
préfixe détaillé de la recherche.
"""
import heapq

from .perception import recharge


def suites(v, e, lot, vises, but):
    from . import planification as p
    # La scène du devis est celle du départ ; seuls les moyens déjà acquis et
    # le budget engagé par le préfixe y sont reportés. Cela partage le devis
    # entre les préparatifs qui ont les mêmes moyens, sans multiplier les suites.
    droits = [(cle, valeur) for cle, valeur in e.faits.items()
              if cle[0] in ("permis", "acquis", "achete", "depense", "faute", "degat")]
    e = (v._depart_estimation or e).apres(salle=e.salle, portes=e.portes, faits=droits)
    cle = (e, lot, v.emploie_lumiere)
    if cle in v._estimations_parts:
        return v._estimations_parts[cle]
    resultats = []

    def aller(etat, salle):
        if salle is None or v.descente(etat.salle, salle):
            return None
        route = v.route(etat, salle)
        if route is None:
            return None
        suivant = etat.apres(salle=salle)
        return suivant, len(route) * (1 + v.pression(suivant))

    def faute(etat, objet):
        lese = v.proprietaire[objet] if v.illicite[objet] and not etat.fait("permis", objet) else None
        mal = int(bool(lese) and not etat.fait("faute", lese, "honnetete"))
        return (etat.apres(faits=[(("faute", lese, "honnetete"), True)]) if lese else etat), mal

    def obtenir(etat, objet):
        if objet in etat.portes:
            yield etat, 0, 0
            return
        if v.contrarie(objet) or not v.disponible(objet):
            return
        if v.a_portee(etat, objet) and v.autorise[objet]:
            pris, mal = faute(etat, objet)
            yield pris.apres(portes=pris.portes | {objet}), 1 + v.pression(pris), mal
        porteur = v.lieu(etat, objet)
        if (porteur not in [*v.personnes(), "joueur"] or v.salle(etat, porteur) != etat.salle
                or v.proprietaire[objet] not in (None, v.id, porteur)
                or v.seul and porteur != v.seul):
            return
        permis = etat.apres(portes=etat.portes | {objet}, faits=[(("permis", objet), True)])
        if not v.refuse(porteur, objet):
            yield permis, 1 + p.DEMANDE / v.chances_demandes[porteur] + v.pression(permis), 0
        prix = v.objets[objet].get("prix")
        if (prix and v.piece and v.proprietaire[objet] == porteur and not v.refuse_achat(porteur, objet)
                and v.richesse - (etat.fait("depense") or 0) >= prix):
            achete = permis.apres(faits=[(("achete", objet), True),
                                       (("depense",), (etat.fait("depense") or 0) + prix)])
            yield achete, 1 + p.DEMANDE + v.depense(prix) + v.pression(achete), 0

    # Les flammes déjà en main, celles posées, et les outils accessibles. Une
    # demande de feu au porteur garde son refus et son prix social habituels.
    for source in v.rechargeables:
        x = v.objets[source]
        if (not recharge(x, v.objets[lot]) or v.contrarie(source) or v.feu(e, source)[1]):
            continue
        if source not in vises.get("entretenir", ()) and not v.emploie_lumiere:
            continue
        lieu = v.salle(e, source)
        trajet = aller(e, lieu)
        if trajet is None:
            continue
        sur_place, cout_trajet_source = trajet
        if x.get("mobile"):
            prises = list(obtenir(sur_place, source))
        elif v.a_portee(sur_place, source) and v.autorise[source]:
            touche, mal = faute(sur_place, source)
            prises = [(touche, 0, mal)]
        else:
            prises = []
        for sur_place, cout_prise, fautes_source in prises:
            resultats.extend(_preparer(v, e, source, sur_place, lieu, obtenir, aller,
                                       cout_trajet_source + cout_prise, fautes_source, vises, but))
    # Même état conclusif : seuls les termes indépendants du prix d'une faute
    # peuvent se départager ici, pour garder les graphes repris exacts.
    meilleurs = {}
    for fautes, cout, final, abime in resultats:
        cle_final = (fautes, final, abime)
        if cle_final not in meilleurs or cout < meilleurs[cle_final]:
            meilleurs[cle_final] = cout
    resultat = [(f, c, final, a) for (f, final, a), c in meilleurs.items()]
    v._estimations_parts[cle] = resultat
    return resultat


def _preparer(v, e, source, sur_place, lieu, obtenir, aller, cout_source, fautes_source, vises, but):
    from . import planification as p
    x = v.objets[source]
    # Charger n'éclaire pas. L'accord n'a pas cet effet dans le monde.
    charge = sur_place.apres(faits=[(("charge", source), True)])
    cout_source += 1 + v.pression(charge)
    allumages = []
    if v.feu(e, source)[0]:
        allumages.append((charge, 0, fautes_source))
    else:
        for flamme in v.flammes_portables:
            if flamme == source or not ("allumage" in v.objets[flamme].get("usages", ())
                                       or v.feu(e, flamme)[0]):
                continue
            if v.flamme(charge, flamme):
                allumages.append((charge, 0, fautes_source))
                continue
            depart_fl = aller(charge, v.salle(charge, flamme))
            if depart_fl is None:
                continue
            pres_fl, cout_fl = depart_fl
            for avec_fl, prix_prise, fautes_fl in obtenir(pres_fl, flamme):
                retour = (avec_fl, 0) if x.get("mobile") else aller(avec_fl, lieu)
                if retour is not None:
                    allumages.append((retour[0], cout_fl + prix_prise + retour[1], fautes_source + fautes_fl))
            porteur = v.lieu(pres_fl, flamme)
            if (x.get("mobile") and not v.seul and porteur in v.personnes()
                    and not v.refuse_feu(porteur, source)):
                allumages.append((pres_fl, cout_fl + p.DEMANDE, fautes_source))
        if x.get("mobile"):
            for fixe in v.connus:
                if (fixe == source or "allume" not in v.objets[fixe]
                        or v.objets[fixe].get("mobile") or not v.feu(e, fixe)[0]):
                    continue
                pres_fl = aller(charge, v.salle(charge, fixe))
                if pres_fl is not None:
                    allumages.append((*pres_fl, fautes_source))
    for pret, cout_flamme, fautes_prep in allumages:
        allume = pret.apres(faits=[(("allume", source), True)])
        cout = cout_source + cout_flamme
        if not v.feu(e, source)[0]:
            cout += 1 + v.pression(allume)
        combustion = p.FLAMME_EN_MAIN if source in allume.portes else 0
        for final, cout_trajet in _trajets(v, allume, combustion):
            cout_reste = cout + cout_trajet
            if but(v, final):
                yield fautes_prep, cout_reste, final, False
                continue
            # Un seul geste conclusif, jamais un graphe de suites hypothétiques.
            for fautes, minutes, _, suivant, duree, abime, pression in p._suites(v, final, vises, but, conclure=True):
                yield (fautes_prep + fautes, cout_reste + minutes * (1 + combustion)
                       + duree * pression, suivant, abime)


def _trajets(v, depart, combustion):
    """Les prix entre salles, sans développer de geste ni changer les faits.

    Les étapes intermédiaires comptent leur propre pression, comme dans la file
    principale ; un détour peut ainsi coûter moins qu'un trajet payé entièrement
    au prix du lieu d'arrivée. Seuls les lieux changent, pas l'inventaire.
    """
    prix = {depart.salle: 0}
    file = [(0, depart.salle)]
    ouvertes = v.ouvertes(depart)
    while file:
        cout, salle = heapq.heappop(file)
        if cout != prix[salle]:
            continue
        e = depart.apres(salle=salle)
        yield e, cout
        for vers, longueur in v.allers(e, ouvertes):
            total = cout + longueur * (1 + combustion + v.pression(e.apres(salle=vers)))
            if total < prix.get(vers, float("inf")):
                prix[vers] = total
                heapq.heappush(file, (total, vers))
