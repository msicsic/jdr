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
    e = (v._depart_estimation or e).apres(salle=e.salle, case=e.case, orientation=e.orientation,
                                        portes=e.portes, faits=droits, allure=e.allure)
    # Le lot ne sert qu'à choisir les sources qu'il recharge ; deux lots de
    # même compatibilité ont exactement le même devis. Tous les autres moyens,
    # droits et dépenses restent dans l'état normalisé complet, le but et ses
    # visées dans le contexte de l'exploration, les lectures du monde dans v.
    sources = v.sources_du_lot[lot]
    cle = (v._contexte_parts, e, sources, v.emploie_lumiere)
    if cle in v._estimations_parts:
        return v._estimations_parts[cle]
    resultats = []

    def aller(etat, salle):
        if salle is None or v.descente(etat.salle, salle):
            return None
        route = v.route(etat, salle)
        if route is None:
            return None
        suivant = v.arrivee(etat, salle, route)
        # Le même coût de route que la recherche (``obstacles.cout_route`` : passages compris).
        from .obstacles import cout_route
        return suivant, cout_route(route, etat.orientation) + v.prix_route(etat, route)

    def mesurer(etat, etape, suivant, preference=0):
        mesure = p._mesurer(v, etat, [etape], suivant, 1)
        if mesure is None:
            return None
        temps, pression, fin = mesure
        return fin, temps + pression + preference

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
            mesure = mesurer(etat, p._etape("prendre", objet), pris.apres(portes=pris.portes | {objet}))
            if mesure is not None:
                yield *mesure, mal
        porteur = v.lieu(etat, objet)
        if (porteur not in [*v.personnes(), "joueur"] or v.salle(etat, porteur) != etat.salle
                or v.proprietaire[objet] not in (None, v.id, porteur)
                or v.seul and porteur != v.seul):
            return
        permis = etat.apres(portes=etat.portes | {objet}, faits=[(("permis", objet), True)])
        if not v.refuse(porteur, objet):
            mesure = mesurer(etat, p._etape("demander", porteur, outil=objet), permis,
                              p.DEMANDE / v.chances_demandes[porteur])
            if mesure is not None:
                yield *mesure, 0
        prix = v.objets[objet].get("prix")
        if (prix and v.piece and v.proprietaire[objet] == porteur and not v.refuse_achat(porteur, objet)
                and v.richesse - (etat.fait("depense") or 0) >= prix):
            achete = permis.apres(faits=[(("achete", objet), True),
                                       (("depense",), (etat.fait("depense") or 0) + prix)])
            mesure = mesurer(etat, p._etape("acheter", porteur, outil=objet), achete,
                              p.DEMANDE + v.depense(prix))
            if mesure is not None:
                yield *mesure, 0

    # Les flammes déjà en main, celles posées, et les outils accessibles. Une
    # demande de feu au porteur garde son refus et son prix social habituels.
    for source in v.rechargeables:
        x = v.objets[source]
        if (source not in sources or v.contrarie(source) or v.feu(e, source)[1]):
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
    mesure = p._mesurer(v, sur_place, [p._etape("alimenter", source)],
                        sur_place.apres(faits=[(("charge", source), True)]), 1)
    if mesure is None:
        return
    temps, pression, charge = mesure
    cout_source += temps + pression
    allumages = []
    if v.feu(e, source)[0]:
        allumages.append((charge, 0, fautes_source, ""))
    else:
        for flamme in v.flammes_portables:
            if flamme == source or not ("allumage" in v.objets[flamme].get("usages", ())
                                       or v.feu(e, flamme)[0]):
                continue
            if v.flamme(charge, flamme):
                allumages.append((charge, 0, fautes_source, flamme))
                continue
            depart_fl = aller(charge, v.salle(charge, flamme))
            if depart_fl is None:
                continue
            pres_fl, cout_fl = depart_fl
            for avec_fl, prix_prise, fautes_fl in obtenir(pres_fl, flamme):
                retour = (avec_fl, 0) if x.get("mobile") else aller(avec_fl, lieu)
                if retour is not None:
                    allumages.append((retour[0], cout_fl + prix_prise + retour[1], fautes_source + fautes_fl, flamme))
            porteur = v.lieu(pres_fl, flamme)
            if (x.get("mobile") and not v.seul and porteur in v.personnes()
                    and not v.refuse_feu(porteur, source)):
                allumages.append((pres_fl, cout_fl + p.DEMANDE, fautes_source, flamme))
        if x.get("mobile"):
            for fixe in v.connus:
                if (fixe == source or "allume" not in v.objets[fixe]
                        or v.objets[fixe].get("mobile") or not v.feu(e, fixe)[0]):
                    continue
                pres_fl = aller(charge, v.salle(charge, fixe))
                if pres_fl is not None:
                    allumages.append((*pres_fl, fautes_source, fixe))
    for pret, cout_flamme, fautes_prep, flamme in allumages:
        allume = pret.apres(faits=[(("allume", source), True)])
        cout = cout_source + cout_flamme
        if not v.feu(e, source)[0]:
            porteur = v.lieu(pret, flamme)
            etape = (p._etape("demander_feu", porteur, outil=flamme, contenu={"allumer": source})
                     if porteur in v.personnes() and flamme not in pret.portes
                     else p._etape("allumer", source, outil=flamme))
            mesure = p._mesurer(v, pret, [etape], allume, 1)
            if mesure is None:
                continue
            temps, pression, allume = mesure
            cout += temps + pression
        combustion = p.FLAMME_EN_MAIN if source in allume.portes else 0
        for final, cout_trajet in _trajets(v, allume, combustion):
            cout_reste = cout + cout_trajet
            if but(v, final):
                yield fautes_prep, cout_reste, final, False
                continue
            # Un seul geste conclusif, jamais un graphe de suites hypothétiques.
            for fautes, minutes, _, suivant, duree, abime, pression in p._suites(v, final, vises, but, conclure=True):
                yield (fautes_prep + fautes, cout_reste + minutes + duree * combustion
                       + duree * pression, suivant, abime)


def _trajets(v, depart, combustion):
    """Les prix entre salles, sans développer de geste ni changer les faits.

    Les étapes intermédiaires comptent leur propre pression, comme dans la file
    principale ; un détour peut ainsi coûter moins qu'un trajet payé entièrement
    au prix du lieu d'arrivée. Seuls les lieux changent, pas l'inventaire.
    """
    from itertools import count
    from .obstacles import cout_route
    ordre = count()
    prix = {depart: 0}
    file = [(0, next(ordre), depart)]
    while file:
        cout, _, e = heapq.heappop(file)
        if cout != prix[e]:
            continue
        yield e, cout
        for vers, _ in v.allers(e, v.ouvertes(e)):
            route = v.route(e, vers)
            fin = v.arrivee(e, vers, route)
            total = cout + cout_route(route, e.orientation) * (1 + combustion) + v.prix_route(e, route)
            if total < prix.get(fin, float("inf")):
                prix[fin] = total
                heapq.heappush(file, (total, next(ordre), fin))
