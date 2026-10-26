"""Accès unique aux engagements et aux agendas ; stockage historique inchangé en A1.

Au premier lot qui en a besoin, chaque engagement deviendra un agenda d'origine
« contrat » s'il est payé, « parole » sinon, en conservant condition, bénéficiaire et minute.
Les lectures renvoient des copies : toute mutation passe par une opération nommée.
"""
import copy
import hashlib
import json

CHAMPS = {"engagements": list}


def champs_esprit(e):
    """L'état A4 est facultatif : aucune migration des esprits sans déclaration."""
    return set(e) - {"agendas"}


def champs_profil():
    return {"agendas"}


def projets(monde, id):
    from .esprits import lire
    return copy.deepcopy(lire(monde, id).get("agendas", []))


def _croyances(monde, id):
    """Une nouvelle date de regard ne constitue pas un nouveau moyen."""
    from .esprits import lire
    def contenu(x):
        if isinstance(x, dict):
            return {k: contenu(v) for k, v in x.items() if k not in ("minute", "depuis")}
        if isinstance(x, list):
            return [contenu(v) for v in x]
        return x
    return hashlib.sha256(json.dumps(contenu(lire(monde, id)["croyances"]),
                                    sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def poids(monde, id, agenda):
    """Valeurs, situation et liens courants ; jamais de score sauvegardé."""
    from .caractere import valeur
    from .relations import envers
    p = monde.objets[id].get("profil") or {}
    qui = agenda["parametres"]["qui"]
    qui = [qui] if isinstance(qui, str) else qui
    liens = [envers(monde, id, a)["affection"] for a in qui]
    score = (valeur(monde, id, "altruisme") + valeur(monde, id, "loyaute")
             + p.get("situation", {}).get("projet", 0) + max(liens, default=0)) / 4
    echeance = agenda.get("echeance")
    if echeance is not None:
        score *= 1 + 60 / max(1, echeance - monde.data["minutes"])
    return score


def _changer(monde, id, a, etat, raison, empreinte):
    from .pnj import _chroniquer
    from .social import _qui
    if a.get("etat") == etat and a.get("raison") == raison:
        a["croyances"] = empreinte
        return
    a.update(etat=etat, depuis=monde.data["minutes"], raison=raison, croyances=empreinte)
    _chroniquer(monde, id, f"{_qui(monde, id)} : agenda {a['id']} {etat} ({raison}).", "decision")


def actualiser(monde, id):
    """Activation unique, révision sur les seules croyances du porteur."""
    from .esprits import esprit
    declarations = depart(monde, id)
    if not declarations:
        return
    e = esprit(monde, id)
    empreinte = _croyances(monde, id)
    if "agendas" not in e:
        e["agendas"] = []
        for n, declaration in enumerate(declarations):
            a = copy.deepcopy(declaration)
            a.setdefault("id", f"a{n + 1}")
            a.setdefault("maniere", {"sans_violence": True})
            a["origine"] = {"type": "scenario", "de": id, "minute": monde.data["minutes"], "cause": a["id"]}
            _changer(monde, id, a, "actif", "scenario", empreinte)
            e["agendas"].append(a)
    for a in e["agendas"]:
        if a["etat"] not in ("actif", "sommeil"):
            continue
        if a.get("echeance", float("inf")) < monde.data["minutes"]:
            _changer(monde, id, a, "abandonne", "echeance", empreinte)
            continue
        if a["sorte"] != "informer":
            _changer(monde, id, a, "sommeil", "sorte non prise en charge", empreinte)
            continue
        if _informe(monde, id, a):
            _changer(monde, id, a, "atteint", "parole entendue", empreinte)
    _limiter(monde, id, empreinte)


def _limiter(monde, id, empreinte):
    from .esprits import esprit
    actifs = [a for a in esprit(monde, id)["agendas"] if a["etat"] == "actif"]
    for a in sorted(actifs, key=lambda a: (poids(monde, id, a), a["origine"]["minute"], a["id"]))[:max(0, len(actifs) - 3)]:
        _changer(monde, id, a, "abandonne", "supplante", empreinte)


def essayables(monde, id):
    """Une nouvelle croyance autorise un essai, pas un réveil sans recours."""
    empreinte = None
    for a in projets(monde, id):
        if a["etat"] == "actif":
            yield a
        elif a["etat"] == "sommeil" and a["sorte"] == "informer":
            if empreinte is None:
                empreinte = _croyances(monde, id)
            if a["croyances"] != empreinte:
                yield a


def _destinataires(a):
    qui = a["parametres"]["qui"]
    return [qui] if isinstance(qui, str) else qui


def _noyau(a):
    return a["parametres"].get("avis", a["parametres"].get("fait"))


def _informe(monde, id, a):
    from .social import transmission_attestee
    return all(transmission_attestee(monde, id, qui, _noyau(a)) for qui in _destinataires(a))


def planifier(monde, id, identifiant):
    """Un seul prochain sous-but recherché ; aucun plan conservé dans l'agenda."""
    from .esprits import esprit, lire
    from .deliberation import salle_crue
    from .planification import chercher, _etape
    from .social import deja_dit, avis_exprime
    a = next(a for a in esprit(monde, id)["agendas"] if a["id"] == identifiant)
    empreinte = _croyances(monde, id)
    noyau = _noyau(a)
    # Un objectif de parole n'autorise ni une mesure inventée ni un mensonge.
    if noyau["type"] == "avis":
        from .eau import menacee
        connu = menacee(monde, id, noyau["objet"]) == noyau["valeur"]
        contenu = {"avis": avis_exprime(monde, id, noyau["objet"], noyau["valeur"])}
    else:
        cru = lire(monde, id)["croyances"].get(noyau["sujet"], {}).get(noyau["attribut"])
        connu = cru is not None and cru["valeur"] == noyau["valeur"]
        contenu = {k: noyau[k] for k in ("sujet", "attribut", "valeur")}
    if not connu:
        _changer(monde, id, a, "sommeil", "contenu non cru", empreinte)
        return None
    cibles = [qui for qui in _destinataires(a) if not deja_dit(monde, id, qui, noyau)]
    if not cibles:
        _changer(monde, id, a, "sommeil", "transmission non attestee", empreinte)
        return None
    # La route crue donne le coût de proximité, sans consulter la position réelle.
    from .planification import vue, depart as etat_depart, cout_route
    v = vue(monde, id)
    e = etat_depart(monde, id, v)
    def distance(qui):
        salle = salle_crue(monde, id, qui)
        route = v.route(e, salle) if salle is not None else None
        return (float("inf") if route is None else cout_route(route, e.orientation), qui)
    qui = min(cibles, key=distance)
    salle = salle_crue(monde, id, qui)
    trouve = None if salle is None else chercher(
        monde, id, lambda v, e: e.salle == salle, nom="agenda:" + identifiant,
        memo=["agenda", identifiant, salle], emplois=(), endurer=poids(monde, id, a))
    if trouve is None:
        _changer(monde, id, a, "sommeil", "sans plan admissible au cout", empreinte)
        return None
    if a["etat"] == "sommeil":
        _changer(monde, id, a, "actif", "plan apres croyance nouvelle", empreinte)
        _limiter(monde, id, empreinte)
        if a["etat"] != "actif":
            return None
    return {"type": "agenda", "agenda": identifiant, "qui": qui}, trouve[1] + [_etape("dire", qui, contenu=contenu)]


def en_cours(monde, id, *, condition=None, objet=None, personne=None, actifs=False):
    """Dans l'ordre enregistré, annulations à annoncer comprises sauf ``actifs``.
    ``personne`` vise le bénéficiaire ou une personne de la condition.
    """
    from .esprits import lire
    stock = monde.data.get("promesses_joueur", []) if id == "joueur" else lire(monde, id)["engagements"]
    return [copy.deepcopy(x) for x in stock
            if (condition is None or x["condition"] == condition)
            and (objet is None or x["condition"].get("objet") == objet)
            and (personne is None or x["pour"] == personne
                 or any(x["condition"].get(k) == personne for k in ("servir", "rendre", "remettre")))
            and (not actifs or not x.get("annule"))]


def prendre(monde, id, engagement):
    """Inscrire aussi la proposition provisoire, retirée si le devis ou le jet refuse."""
    from .esprits import esprit
    stock = monde.data.setdefault("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    stock.append(copy.deepcopy(engagement))


def retirer_proposition(monde, id, engagement):
    from .esprits import esprit
    stock = monde.data.get("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    stock.remove(engagement)


def tenir(monde, id, engagement):
    """Retirer une parole exécutée ; l'appelant inscrit son souvenir au même instant."""
    from .esprits import lire
    pour = engagement['pour']
    if pour != 'joueur':
        for s in lire(monde, pour)['recours_intermediaires']:
            if s['via'] == id and s['livraison'] == engagement['condition'].get('objet') and s['issue'] == 'accepte':
                s['abouti'] = True
    retirer_proposition(monde, id, engagement)


def affecter_part(monde, id, lot, part):
    """Une fourniture reçue donne son identité réelle au travail promis sur le lot."""
    from .esprits import esprit
    if id == 'joueur':
        return
    for x in esprit(monde, id)['engagements']:
        c = x['condition']
        if c.get('objet') == lot and any(k in c for k in ('servir', 'remettre')) and not x.get('annule'):
            c['objet'] = part
            if x['pour'] != 'joueur':
                for s in esprit(monde, x['pour'])['recours_intermediaires']:
                    if s['via'] == id and s['livraison'] == lot and s['issue'] == 'accepte':
                        s['livraison'] = part
            break  # Une seule part ne finance pas deux paroles.


def annoncer_abandon(monde, id, engagement):
    """Retirer une annulation désormais annoncée à son destinataire."""
    retirer_proposition(monde, id, engagement)


def oublier_personne(monde, personne):
    """Une mort libère tous les engagements visant cette personne."""
    for e in monde.data["esprits"].values():
        e["engagements"] = [x for x in e["engagements"] if x.get("pour") != personne
                            and not any(x["condition"].get(k) == personne for k in ("servir", "rendre", "remettre"))]
    if "promesses_joueur" in monde.data:
        monde.data["promesses_joueur"] = [x for x in monde.data["promesses_joueur"] if x["pour"] != personne]


def depart(monde, id):
    """Données déclarées par le scénario, sans activation ni écriture dans ``data``."""
    return copy.deepcopy((monde.objets[id].get("profil") or {}).get("agendas", []))


def contrats(monde):
    """Accords de mission historiques, distincts des paroles de service des PNJ."""
    return copy.deepcopy(monde.data.get("engagements", {}))


def installer_contrats(monde):
    monde.data.setdefault("engagements", {})


def proposer_contrat(monde, mission, montant):
    monde.data["engagements"][mission] = {"statut": "propose", "montant": montant}


def repondre_contrat(monde, mission, accepter):
    monde.data["engagements"][mission]["statut"] = "accepte" if accepter else "refuse"


def payer_contrat(monde, mission):
    accord = monde.data["engagements"][mission]
    accord["statut"] = "paye"
    accord["paye_revision"] = monde.data["revision"] + 1


def declares(rapport):
    """Champ public rendu ou sauvegardé, jamais un esprit de PNJ du monde."""
    return copy.deepcopy(rapport.get("engagements"))


def verifier(monde, id):
    stock = projets(monde, id)
    assert len([a for a in stock if a["etat"] == "actif"]) <= 3, "Trop d'agendas actifs"
    assert len({a["id"] for a in stock}) == len(stock), "Identifiants d'agenda dupliqués"
    for a in stock:
        assert (a["etat"] in ("actif", "sommeil", "atteint", "abandonne")
                and type(a["depuis"]) is int and isinstance(a["raison"], str)
                and a["origine"]["type"] == "scenario" and "plan" not in a
                and isinstance(a["croyances"], str)), "Agenda invalide"
    for engagement in en_cours(monde, id):
        from .deliberation import condition_valide
        # ``paye`` : une contrepartie payée d'avance (une part, un objet, une tâche), le bien et le prix
        # reçu (``echanges.engagements_echus``).
        from .biens import QUOI
        paye = engagement.get("paye")
        assert (isinstance(engagement, dict) and set(engagement) - {"paye", "lot", "objet", "annule"}
                - ({"realisee"} if id == "joueur" else set()) == {"condition", "pour", "minute"}
                and ("realisee" not in engagement or engagement["realisee"] is True)
                and ("objet" not in engagement or isinstance(engagement["objet"], str))
                and ("annule" not in engagement or engagement["annule"] in ("impossible", "refus"))
                and condition_valide(monde, engagement["condition"]) and "periode" not in engagement["condition"]
                and (engagement["pour"] == "joueur" or engagement["pour"] in monde.objets)
                and type(engagement["minute"]) is int
                and ("lot" not in engagement or isinstance(engagement["lot"], str) and engagement["lot"] in monde.objets
                     and "remettre" in engagement["condition"])
                and (paye is None or isinstance(paye, dict) and set(paye) == {"objet", "prix", "quoi"}
                     and paye["quoi"] in QUOI
                     and isinstance(paye["objet"], str) and type(paye["prix"]) is int and paye["prix"] > 0)
                ), "Engagement de PNJ invalide"


def echoir(monde, id):
    """Retire les engagements tenus, trop anciens ou qu'il ne peut plus tenir ; les souvenirs gardent
    la trace. Une part payée d'avance et non servie à l'échéance est rendue, ou due
    (``biens.rembourser``). Une garde finie, ce qu'il en porte encore (le bien, ses clés) lui reste
    prêté : il le rendra."""
    from .echanges import ENGAGEMENT_MAX, tenu, empeche, retenir_abandon, phrase_condition
    from .esprits import esprit, memoriser
    from .biens import _cles, preter, rembourser
    from .spatial import porte_par
    from .vol import proprietaire
    e = esprit(monde, id)
    restants, finis = [], []
    for engagement in e["engagements"]:
        if engagement.get("annule"):
            restants.append(engagement)  # Il doit encore prévenir, sans savoir magiquement l'autre informé.
        elif tenu(monde, id, engagement["condition"], engagement["minute"]):
            memoriser(monde, id, {"type": "engagement_tenu", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
            finis.append(engagement)
            if (engagement.get("paye") or {}).get("quoi") == "tache":
                from .pnj import _chroniquer
                from .social import _qui
                _chroniquer(monde, id, f"{_qui(monde, id)} a fait le travail que {_qui(monde, engagement['pour'])} "
                                       f"lui avait payé pour que {phrase_condition(monde, engagement['condition'])}.", "compte")
        elif monde.data["minutes"] - engagement["minute"] > ENGAGEMENT_MAX or empeche(monde, id, engagement):
            raison = "impossible" if empeche(monde, id, engagement) else "refus"
            memoriser(monde, id, {"type": "engagement_abandonne", "pour": engagement["pour"],
                                  "condition": engagement["condition"]})
            finis.append(engagement)
            if engagement.get("paye"):
                paye = engagement["paye"]
                rembourser(monde, id, engagement["pour"], paye["prix"], paye["objet"], paye["quoi"])
                retenir_abandon(monde, id, engagement, raison)  # Le prix rendu ne rend pas le service possible.
            else:
                engagement["annule"] = raison
                restants.append(engagement)
        else:
            restants.append(engagement)
    e["engagements"] = restants
    for engagement in finis:
        o, de = engagement["condition"].get("objet"), engagement["pour"]
        if ("rendre" in engagement["condition"] or "remettre" in engagement["condition"] or o not in monde.objets
                or proprietaire(monde, monde.objets[o]) != de):
            continue
        for k in sorted(_cles(monde, o, de)):
            if porte_par(monde, k, id) and not any(p["objet"] == k for p in monde.data.get("permissions", ())):
                preter(monde, k, id)


def observer_promesses(monde, lignes):
    """Le bénéficiaire juge une promesse du joueur sur ses observations, jamais à distance."""
    from .echanges import ENGAGEMENT_MAX, tenu, phrase_condition
    from .esprits import memoriser
    from .pnj import se_parler
    from .voix import nom_pour_joueur
    for engagement in en_cours(monde, "joueur"):
        a, c = engagement["pour"], engagement["condition"]
        faite = engagement.get("realisee", False) and tenu(monde, a, c, engagement["minute"])
        echue = monde.data["minutes"] - engagement["minute"] > ENGAGEMENT_MAX
        if not faite and not (echue and se_parler(monde, a, "joueur")):
            continue
        tenir(monde, "joueur", engagement)
        memoriser(monde, a, {"type": "engagement_tenu" if faite else "engagement_abandonne",
                            "de": "joueur", "condition": c})
        texte = ("Tu as tenu ta promesse envers " if faite else "Tu as abandonné ta promesse envers ")
        texte += nom_pour_joueur(monde, a) + " : " + phrase_condition(monde, c) + "."
        monde.data.setdefault("journal_promesses", []).append(texte)
        lignes.append(texte)


def etat_promis(monde):
    """Les seuls attributs qu'un effet doit changer pour réaliser les paroles du joueur."""
    etats = {}
    for engagement in en_cours(monde, "joueur"):
        c = engagement["condition"]
        o = monde.objets.get(c["objet"], {})
        cles = set(c) - {"objet"}
        if "allume" in c:
            cles.add("combustible")  # Entretenir une flamme déjà allumée produit aussi un résultat.
        etats.setdefault(c["objet"], {}).update({k: o.get(k) for k in cles})
    return etats


def constater_geste_joueur(monde, avant):
    """Une modification effective réalise la condition ; déplacer une flamme n'est pas l'allumer.

    La preuve du moteur persiste ; le bénéficiaire l'apprend seulement par sa perception.
    """
    for engagement in monde.data.get("promesses_joueur", []):
        c = engagement["condition"]
        o = monde.objets.get(c["objet"], {})
        cles = set(c) - {"objet"}
        if "allume" in c:
            cles.add("combustible")
        ancien = avant.get(c["objet"], {})
        change = (o.get("allume") != ancien.get("allume") or
                  o.get("combustible", 0) > (ancien.get("combustible") or 0)) if "allume" in c else any(
                      o.get(k) != ancien.get(k) for k in cles)
        if (change
                and all(o.get(k) == v for k, v in c.items() if k != "objet")):
            engagement["realisee"] = True


def promesses_visibles(monde):
    from .echanges import phrase_condition
    from .voix import nom_pour_joueur
    from .francais import groupe_nominal
    return ["Tu as promis " + groupe_nominal(nom_pour_joueur(monde, x["pour"]), "à") + " que "
            + phrase_condition(monde, x["condition"]) + "." for x in en_cours(monde, "joueur")]
