"""Accès unique aux engagements et aux agendas ; stockage historique inchangé en A1.

Au premier lot qui en a besoin, chaque engagement deviendra un agenda d'origine
« contrat » s'il est payé, « parole » sinon, en conservant condition, bénéficiaire et minute.
Les lectures renvoient des copies : toute mutation passe par une opération nommée.
"""
import copy
import hashlib
import json
from contextlib import contextmanager

CHAMPS = {"engagements": list}

# Cause -> vocabulaire et valeurs ; aucune identité ni méthode d'action.
NAISSANCES = {
    "dette_situation": {"sorte": "obtenir", "valeurs": ("honnetete", "ambition")},
    "bien_spolie": {"sorte": "récupérer", "valeurs": ("ambition", "honnetete", "douceur", "fierte")},
}


def _dette_situation(monde, id):
    """Situation personnelle connue du porteur, distincte d'une créance locale."""
    return (monde.objets[id].get("profil") or {}).get("situation", {}).get("dette", 0)


def _torts_connus(monde, id):
    """Preuves propres persistantes ; ni mémoire courte ni enquête sur le réel."""
    from .esprits import lire
    e = lire(monde, id)
    for objet, portage in sorted(e["portages"].items()):
        connu = e["croyances"].get(objet, {})
        p = connu.get("lieu", {}).get("possession", {})
        if (p.get("proprietaire") == id and p.get("porteur") not in (None, id)
                and p.get("permis") is False
                and portage["auteur"] == p["porteur"] and not connu.get("fin")):
            yield objet, portage


def _naitre(monde, id, cause, parametres, origine, empreinte, *, sans_violence=True):
    stock = _stock(monde, id, creer=True)
    if any(a["origine"] == origine for a in stock):
        return
    n = 1
    while any(a["id"] == f"a{n}" for a in stock):
        n += 1
    a = {"id": f"a{n}", "sorte": NAISSANCES[cause]["sorte"],
         "parametres": parametres, "maniere": {"sans_violence": sans_violence},
         "origine": origine}
    _changer(monde, id, a, "actif", cause, empreinte)
    stock.append(a)


def _naissances(monde, id, empreinte):
    from .biens import richesse, VALEUR_OBJET
    for objet, p in _torts_connus(monde, id):
        # L'identité de preuve du portage survit aux regards successifs.
        cause = "bien_spolie"
        stock = _stock(monde, id) or []
        if any(a["origine"].get("preuve") == p["preuve"] for a in stock):
            continue
        # Le tarif déclaré du bien connu est une estimation de départ,
        # pas une lecture répétée d'un objet éventuellement disparu à distance.
        prix = monde.objets.get(objet, {}).get("prix") or VALEUR_OBJET
        _naitre(monde, id, cause, {"objet": objet, "qui": p["auteur"], "prix_cru": prix},
                {"type": "evenement", "de": p["auteur"], "cause": cause,
                 "preuve": p["preuve"], "minute": monde.data["minutes"]}, empreinte, sans_violence=False)
    dette = _dette_situation(monde, id)
    if dette <= richesse(monde, id):
        return
    cause = "dette_situation"
    stock = _stock(monde, id, creer=True)
    # Une même cause ne ressuscite pas un projet terminal. Une nouvelle dette
    # de même montant ne peut pas encore être distinguée par la situation.
    if any(a["origine"].get("type") == "situation" and a["origine"].get("cause") == cause
           for a in stock):
        return
    _naitre(monde, id, cause, {"pieces": dette},
            {"type": "situation", "de": id, "minute": monde.data["minutes"], "cause": cause}, empreinte)


def presents(monde, id):
    """Projets déclarés ou nés, pour l'arbitrage commun des urgences."""
    return bool(depart(monde, id) or _stock(monde, id))


def pieces_poursuivies(monde, id):
    return any(a["sorte"] == "obtenir" and a["etat"] in ("actif", "sommeil")
               for a in (_stock(monde, id) or []))


def champs_esprit(e):
    """L'état A4 est facultatif : aucune migration des esprits sans déclaration."""
    return set(e) - {"agendas", "contrat_intention"}


def contrat_intention(monde, id):
    """Provenance de l'intention courante, jamais celle d'une intention remplacée."""
    from .esprits import lire
    e = lire(monde, id)
    c = e.get("contrat_intention")
    i = e["intention"]
    if c and i and all(c[k] == i[k] for k in ("but", "motif", "depuis")):
        return copy.deepcopy(c["contrat"])
    return None


def retenir_intention(monde, id, contrat):
    from .esprits import esprit
    e = esprit(monde, id)
    i = e["intention"]
    e["contrat_intention"] = {**{k: copy.deepcopy(i[k]) for k in ("but", "motif", "depuis")},
                              "contrat": copy.deepcopy(contrat)}


def clore_intention(monde, id, sortie):
    """Une seule dernière transition, sans pile de décisions ni agenda ajouté."""
    from .esprits import esprit
    c = esprit(monde, id).get("contrat_intention")
    if c and all(c[k] == sortie["intention"][k] for k in ("but", "motif", "depuis")):
        c["contrat"]["sortie"] = copy.deepcopy(sortie)
        c["contrat"]["phase"] = "finir" if sortie["cause"] is not None else "indeterminee"


def dernier_contrat_intention(monde, id):
    from .esprits import lire
    return copy.deepcopy(lire(monde, id).get("contrat_intention"))


def champs_profil():
    return {"agendas"}


def projets(monde, id):
    return copy.deepcopy(_stock(monde, id) or [])


def _stock(monde, id, creer=False):
    from .esprits import esprit, lire
    evaluation = getattr(monde, "_evaluation_agendas", None)
    if evaluation is not None and evaluation[0] == id:
        registre = evaluation[1]
        if registre["stock"] is None and creer:
            registre["stock"] = []
        return registre["stock"]
    if creer:
        return esprit(monde, id).setdefault("agendas", [])
    return lire(monde, id).get("agendas")


@contextmanager
def evaluation(monde, id, *, publier=True):
    """Projets et chroniques proposés hors de data, publiés après le choix réel.

    Comme les efforts bornés, un choix interrompu ne publie rien. Une évaluation
    imbriquée transmet ses propositions à l'évaluation parente, jamais au monde.
    """
    ancien = getattr(monde, "_evaluation_agendas", None)
    registre = {"stock": copy.deepcopy(_stock(monde, id)), "chroniques": []}
    monde._evaluation_agendas = (id, registre)
    try:
        yield
    except BaseException:
        raise
    else:
        if not publier:
            pass
        elif ancien is not None and ancien[0] == id:
            ancien[1]["stock"] = registre["stock"]
            ancien[1]["chroniques"].extend(registre["chroniques"])
        else:
            from .esprits import esprit
            from .pnj import _chroniquer
            if registre["stock"] is not None:
                esprit(monde, id)["agendas"] = registre["stock"]
            for texte in registre["chroniques"]:
                _chroniquer(monde, id, texte, "decision")
    finally:
        monde._evaluation_agendas = ancien


def _croyances(monde, id):
    """Une nouvelle date de regard ne constitue pas un nouveau moyen."""
    from .esprits import lire
    def contenu(x):
        if isinstance(x, dict):
            return {k: contenu(v) for k, v in x.items() if k not in ("minute", "depuis")}
        if isinstance(x, list):
            return [contenu(v) for v in x]
        return x
    croyances = contenu(lire(monde, id)["croyances"])
    if any(a["sorte"] in ("obtenir", "récupérer") for a in (_stock(monde, id) or [])):
        from .biens import richesse
        from .spatial import porte_par
        e = lire(monde, id)
        croyances = [croyances, richesse(monde, id), _dette_situation(monde, id),
                     contenu(e["refus"]), contenu(e["relations"]), en_cours(monde, id),
                     sorted(o for o in monde.objets if porte_par(monde, o, id))]
    return hashlib.sha256(json.dumps(croyances,
                                    sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def poids(monde, id, agenda):
    """Valeurs, situation et liens courants ; jamais de score sauvegardé."""
    from .caractere import valeur
    from .relations import envers
    regle = NAISSANCES.get(agenda.get("origine", {}).get("cause"))
    if regle and agenda["sorte"] == "récupérer":
        from .biens import VALEUR_OBJET
        from .caractere import valeur_pieces
        valeurs = sum(valeur(monde, id, v) for v in regle["valeurs"])
        rancune = envers(monde, id, agenda["parametres"]["qui"])["rancune"]
        prix = agenda["parametres"].get("prix_cru")
        enjeu = valeur_pieces(monde, id, prix or VALEUR_OBJET)
        return enjeu * (valeurs + rancune) / 500
    if regle and agenda["origine"]["type"] == "situation":
        return sum(valeur(monde, id, v) for v in regle["valeurs"]) / len(regle["valeurs"])
    p = monde.objets[id].get("profil") or {}
    qui = agenda["parametres"].get("qui", [])
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
    texte = f"{_qui(monde, id)} : agenda {a['id']} {etat} ({raison})."
    evaluation = getattr(monde, "_evaluation_agendas", None)
    if evaluation is not None and evaluation[0] == id:
        evaluation[1]["chroniques"].append(texte)
    else:
        _chroniquer(monde, id, texte, "decision")


def actualiser(monde, id):
    """Activation unique, révision sur les seules croyances du porteur."""
    declarations = depart(monde, id)
    if not declarations and not _stock(monde, id):
        from .biens import richesse
        if _dette_situation(monde, id) <= richesse(monde, id) and not next(_torts_connus(monde, id), None):
            return
    empreinte = _croyances(monde, id)
    if declarations and _stock(monde, id) is None:
        stock = _stock(monde, id, creer=True)
        for n, declaration in enumerate(declarations):
            a = copy.deepcopy(declaration)
            a.setdefault("id", f"a{n + 1}")
            a.setdefault("maniere", {"sans_violence": True})
            a["origine"] = {"type": "scenario", "de": id, "minute": monde.data["minutes"], "cause": a["id"]}
            _changer(monde, id, a, "actif", "scenario", empreinte)
            stock.append(a)
    _naissances(monde, id, empreinte)
    for a in _stock(monde, id) or []:
        if a["etat"] not in ("actif", "sommeil"):
            continue
        if a.get("echeance", float("inf")) < monde.data["minutes"]:
            _changer(monde, id, a, "abandonne", "echeance", empreinte)
            continue
        if a["sorte"] == "obtenir":
            from .biens import richesse
            if (a["origine"]["type"] == "situation" and not _dette_situation(monde, id)):
                _changer(monde, id, a, "atteint", "dette personnelle soldee", empreinte)
            elif richesse(monde, id) >= a["parametres"]["pieces"]:
                _changer(monde, id, a, "atteint", "pieces disponibles", empreinte)
            continue
        if a["sorte"] == "récupérer":
            from .esprits import lire
            connu = lire(monde, id)["croyances"].get(a["parametres"]["objet"], {})
            if connu.get("fin"):
                _changer(monde, id, a, "abandonne", "bien cru " + connu["fin"]["valeur"], empreinte)
            elif connu.get("lieu", {}).get("possession", {}).get("porteur") == id:
                _changer(monde, id, a, "atteint", "bien cru rendu", empreinte)
            continue
        if a["sorte"] == "garder":
            raison = _fin_garde(monde, id, a)
            if raison:
                _changer(monde, id, a, "abandonne", raison, empreinte)
            continue
        if a["sorte"] == "protéger":
            from .esprits import lire
            qui = a["parametres"]["qui"]
            etat = lire(monde, id)["croyances"].get(qui, {}).get("etat", {}).get("valeur", {})
            if etat.get("mort"):
                _changer(monde, id, a, "abandonne", "protege cru mort", empreinte)
            elif etat.get("parti"):
                _changer(monde, id, a, "abandonne", "protege cru parti", empreinte)
            continue
        if a["sorte"] == "amener":
            from .deliberation import salle_crue
            from .eau import noyee_attendue
            destination = a["parametres"]["lieu"]
            # Une arrivée réelle à distance ne vaut pas une observation. Comme
            # pour une parole due, seule la position crue d'autrui fait foi.
            if all(salle_crue(monde, id, qui) == destination for qui in _destinataires(a)):
                _changer(monde, id, a, "atteint", "arrivee crue", empreinte)
            elif noyee_attendue(monde, id, destination):
                _changer(monde, id, a, "abandonne", "destination crue noyee", empreinte)
            elif _route_coupee(monde, id, a):
                _changer(monde, id, a, "abandonne", "route crue coupee", empreinte)
            continue
        if a["sorte"] != "informer":
            _changer(monde, id, a, "sommeil", "sorte non prise en charge", empreinte)
            continue
        if _informe(monde, id, a):
            _changer(monde, id, a, "atteint", "parole entendue", empreinte)
    _limiter(monde, id, empreinte)


def _limiter(monde, id, empreinte):
    actifs = [a for a in (_stock(monde, id) or []) if a["etat"] == "actif"]
    for a in sorted(actifs, key=lambda a: (poids(monde, id, a), a["origine"]["minute"], a["id"]))[:max(0, len(actifs) - 3)]:
        _changer(monde, id, a, "abandonne", "supplante", empreinte)


def essayables(monde, id):
    """Une nouvelle croyance autorise un essai, pas un réveil sans recours."""
    empreinte = None
    for a in projets(monde, id):
        if a["etat"] == "actif":
            yield a
        elif a["etat"] == "sommeil" and a["sorte"] in ("informer", "amener", "garder", "protéger", "obtenir", "récupérer"):
            if empreinte is None:
                empreinte = _croyances(monde, id)
            if a["croyances"] != empreinte:
                yield a


def _destinataires(a):
    qui = a["parametres"]["qui"]
    return [qui] if isinstance(qui, str) else qui


def _route_coupee(monde, id, a):
    """Une coupure prouvée, pas l'échec d'une recherche bornée ou d'une serrure.

    Même en supposant toutes les portes ouvertes, aucun chemin ne traverse les
    salles crues noyées. Les positions des destinataires restent des croyances.
    """
    from .deliberation import salle_crue
    from .eau import noyee_crue
    salles = monde.data["salles"]
    destination = a["parametres"]["lieu"]
    interdites = {s for s in salles if noyee_crue(monde, id, s)}
    for qui in _destinataires(a):
        depart = salle_crue(monde, id, qui)
        if depart not in salles:
            continue
        vus, file = {depart}, [depart]
        while file:
            salle = file.pop()
            for sortie in salles[salle]["sorties"].values():
                suivante = sortie["vers"]
                if suivante not in vus and suivante not in interdites:
                    vus.add(suivante)
                    file.append(suivante)
        if destination not in vus:
            return True
    return False


def _noyau(a):
    return a["parametres"].get("avis", a["parametres"].get("fait"))


def _informe(monde, id, a):
    from .social import transmission_attestee
    return all(transmission_attestee(monde, id, qui, _noyau(a)) for qui in _destinataires(a))


def planifier(monde, id, identifiant):
    """Un seul prochain sous-but recherché ; aucun plan conservé dans l'agenda."""
    from .esprits import lire
    from .deliberation import salle_crue
    from .planification import chercher, _etape
    from .social import deja_dit, avis_exprime
    contexte = getattr(monde, "_evaluation_agendas", None)
    # Une requête isolée reste un devis : aucune transition ni chronique.
    if contexte is None or contexte[0] != id:
        with evaluation(monde, id, publier=False):
            return planifier(monde, id, identifiant)
    a = next(a for a in _stock(monde, id) if a["id"] == identifiant)
    if a["etat"] not in ("actif", "sommeil"):
        return None
    empreinte = _croyances(monde, id)
    if a["sorte"] == "récupérer":
        if a["etat"] == "sommeil" and a["croyances"] == empreinte:
            return None
        objet = a["parametres"]["objet"]
        trouve = None
        # La parole est un recours commun, sans introduire de branche dans le
        # graphe de reprise. Son refus rend ensuite les moyens habituels au but.
        from .pnj_propositions import reclamation
        recours = reclamation(monde, id, objet)
        if recours:
            _changer(monde, id, a, "actif", "reclamation possible", empreinte)
            _limiter(monde, id, empreinte)
            return ({"type": "agenda", "agenda": identifiant, "objet": objet}, recours) if a["etat"] == "actif" else None
        if objet in monde.objets:
            trouve = chercher(monde, id, lambda v, e: objet in e.portes,
                              {"prendre": (objet,)}, nom="recuperer:" + objet,
                              memo=["recuperer", objet], emplois=(), endurer=poids(monde, id, a))
        if trouve is None:
            _changer(monde, id, a, "sommeil", "sans plan admissible au cout", empreinte)
            return None
        from .planification import _couper
        _changer(monde, id, a, "actif", "plan admissible", empreinte)
        _limiter(monde, id, empreinte)
        return ({"type": "agenda", "agenda": identifiant, "objet": objet}, _couper(trouve[1])) if a["etat"] == "actif" else None
    if a["sorte"] == "obtenir":
        if a["etat"] == "sommeil" and a["croyances"] == empreinte:
            return None
        from .argent_projet import obtenir
        # Le prix reçu pour un travail n'efface pas la parole : laisser le
        # recours d'engagement l'accomplir avant de rechercher une autre paie.
        resultat = None if any(x.get("paye") for x in en_cours(monde, id, actifs=True)) else obtenir(
            monde, id, a["parametres"]["pieces"], poids(monde, id, a))
        if resultat is None:
            _changer(monde, id, a, "sommeil", "sans plan admissible au cout", empreinte)
            return None
        _changer(monde, id, a, "actif", "plan admissible", empreinte)
        _limiter(monde, id, empreinte)
        return ({"type": "agenda", "agenda": identifiant, "pieces": a["parametres"]["pieces"]}, resultat) if a["etat"] == "actif" else None
    if a["sorte"] == "amener":
        return _amener(monde, id, a, empreinte)
    if a["sorte"] == "protéger":
        from .defense import interposition
        poste = interposition(monde, id)
        if poste is not None and poste[0]["objet"] == a["parametres"]["qui"]:
            _changer(monde, id, a, "actif", "interposition", empreinte)
            _limiter(monde, id, empreinte)
            return poste if a["etat"] == "actif" else None
        _changer(monde, id, a, "sommeil", "suivi vocal non pris en charge", empreinte)
        return None
    if a["sorte"] == "garder":
        from .planification import garder
        from .defense import interposition
        c = a["parametres"]
        poste = interposition(monde, id)
        if poste is not None and poste[0]["objet"] == c.get("objet"):
            if a["etat"] == "sommeil":
                _changer(monde, id, a, "actif", "plan apres croyance nouvelle", empreinte)
                _limiter(monde, id, empreinte)
                if a["etat"] != "actif":
                    return None
            return poste
        salle = salle_crue(monde, id, c["objet"]) if "objet" in c else c["lieu"]
        etapes = garder(monde, id, salle) if salle in monde.data["salles"] else None
        if etapes is None:
            _changer(monde, id, a, "sommeil", "sans plan admissible au cout", empreinte)
            return None
        if a["etat"] == "sommeil":
            _changer(monde, id, a, "actif", "plan apres croyance nouvelle", empreinte)
            _limiter(monde, id, empreinte)
            if a["etat"] != "actif":
                return None
        return {"type": "agenda", "agenda": identifiant}, etapes
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


def _amener(monde, id, a, empreinte):
    """Parole, demande, puis marche propre ; seules les traces du porteur font foi."""
    from .deliberation import salle_crue, refus_retenu
    from .eau import menacee
    from .esprits import lire
    from .echanges import ENGAGEMENT_MAX
    from .planification import vue, depart as etat_depart, cout_route, chercher, _etape
    from .social import deja_dit, avis_exprime
    destination = a["parametres"]["lieu"]
    v = vue(monde, id)
    e = etat_depart(monde, id, v)
    cibles = [q for q in _destinataires(a) if salle_crue(monde, id, q) != destination]
    def distance(q):
        from .spatial import distance as distance_spatiale
        salle = salle_crue(monde, id, q)
        route = (v.approche(e, _etape("confier", q)) if salle == e.salle
                 else v.route(e, salle) if salle is not None else None)
        case = v.case_objet(e, q) if salle == e.salle else None
        propre = monde.objets[id].get("position")
        local = distance_spatiale(propre, case) if propre is not None and case is not None else float("inf")
        return (float("inf") if route is None else 0 if salle == e.salle else cout_route(route, e.orientation), local, q)
    raisons, attendus = [], []
    for qui in sorted(cibles, key=distance):
        salle = salle_crue(monde, id, qui)
        condition = {"objet": qui, "lieu": destination}
        aide = lire(monde, id)["aides_attendues"].get(qui)
        accepte = (aide and aide["qui"] == qui and aide["condition"] == condition
                   and monde.data["minutes"] - aide["minute"] <= ENGAGEMENT_MAX)
        noyau = {"type": "avis", "objet": salle, "attribut": "menace", "valeur": True}
        # Un avis déjà transmis n'est pas répété ; aucune lecture de l'esprit d'autrui.
        if not accepte and salle and menacee(monde, id, salle) and not menacee(monde, id, destination) and not deja_dit(monde, id, qui, noyau):
            suite = [_etape("dire", qui, contenu={"avis": avis_exprime(monde, id, salle, True)})]
            lieu = salle
        elif accepte:
            lieu, suite = destination, []
            if e.salle == destination:
                attendus.append(qui)
                continue
        else:
            refus = refus_retenu(monde, id, qui, ("confier",), qui)
            if refus:
                raisons.append("refus " + refus["raison"])
                continue
            lieu, suite = salle, [_etape("confier", qui, contenu=condition)]
        but = (lambda v, e: bool(e.fait("parle", qui))) if suite else (lambda v, e: e.salle == lieu)
        trouve = None if lieu is None else chercher(
            monde, id, but, {"parole": suite}, nom="agenda:" + a["id"],
            memo=["agenda", a["id"], qui, lieu, suite], emplois=(), endurer=poids(monde, id, a))
        if trouve is None:
            raisons.append("sans plan admissible au cout")
            continue
        if a["etat"] == "sommeil":
            _changer(monde, id, a, "actif", "plan apres croyance nouvelle", empreinte)
            _limiter(monde, id, empreinte)
            if a["etat"] != "actif":
                return None
        return {"type": "agenda", "agenda": a["id"], "qui": qui}, trouve[1]
    if attendus:
        # Attendre un engagement accepté est un recours : laisser la routine
        # reprendre ici produirait des navettes vers le rendez-vous à chaque choix.
        if a["etat"] == "sommeil":
            _changer(monde, id, a, "actif", "plan apres croyance nouvelle", empreinte)
            _limiter(monde, id, empreinte)
            if a["etat"] != "actif":
                return None
        depuis = max(lire(monde, id)["aides_attendues"][q]["minute"] for q in attendus)
        # Une inspection achevée sans arrivée visible ne justifie pas de
        # recommencer sans fin ; la perception ordinaire continue pendant l'attente.
        suite = ([] if lire(monde, id)["visites"].get(destination, -1) >= depuis
                 else [_etape("inspecter", lieu=destination)])
        return {"type": "agenda", "agenda": a["id"], "qui": attendus[0]}, suite
    _changer(monde, id, a, "sommeil", raisons[0] if raisons else "arrivee attendue", empreinte)
    return None


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


def _fin_garde(monde, id, a):
    """Aucune interrogation de l'objet réel, même s'il a été supprimé."""
    from .esprits import lire
    objet = a["parametres"].get("objet")
    connu = lire(monde, id)["croyances"].get(objet, {})
    fin = connu.get("fin")
    if fin:
        return "bien cru " + fin["valeur"]
    lieu = connu.get("lieu", {})
    possession = lieu.get("possession")
    if not possession or lieu.get("valeur") is None:
        return None
    porteur, proprietaire = possession["porteur"], possession["proprietaire"]
    if porteur in (None, id):
        return None
    if (possession["remis_par"] == id and proprietaire != id
            and possession["remise_autorisee"]):
        return "bien cru remis"
    if porteur == proprietaire:
        return "bien cru rendu"
    if not possession["permis"]:
        return "bien cru perdu"
    return None


def gardes(monde, id):
    """Charges à tenir, sans activation pendant une lecture ou la perception.

    Le sommeil suspend la recherche, pas la responsabilité. Un état terminal
    ou une échéance échue la retire aussi avant le prochain choix.
    """
    stock = _stock(monde, id)
    return [copy.deepcopy(a["parametres"]) for a in (depart(monde, id) if stock is None else stock)
            if a["sorte"] == "garder" and a.get("etat", "actif") in ("actif", "sommeil")
            and a.get("echeance", float("inf")) >= monde.data["minutes"]
            and not _fin_garde(monde, id, a)]


def proteges(monde, id):
    """Responsabilités de protection déclarées, sans activation ni omniscience.

    Le sommeil ne décharge pas un protecteur ; les fins crues et l'échéance
    retirent la responsabilité dès la lecture, avant même sa publication.
    """
    from .esprits import lire
    stock = _stock(monde, id)
    croyances = lire(monde, id)["croyances"]
    return {a["parametres"]["qui"] for a in (depart(monde, id) if stock is None else stock)
            if a["sorte"] == "protéger" and a.get("etat", "actif") in ("actif", "sommeil")
            and a.get("echeance", float("inf")) >= monde.data["minutes"]
            and not any(croyances.get(a["parametres"]["qui"], {}).get("etat", {}).get("valeur", {}).get(k)
                        for k in ("mort", "parti"))}


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
    from .esprits import lire
    c = lire(monde, id).get("contrat_intention") if id != "joueur" else None
    if c is not None:
        from .deliberation import condition_valide, Palier
        assert (isinstance(c, dict) and set(c) == {"but", "motif", "depuis", "contrat"}
                and isinstance(c["but"], dict) and isinstance(c["motif"], str)
                and type(c["depuis"]) is int), "Provenance d'intention invalide"
        contrat = c["contrat"]
        assert (isinstance(contrat, dict) and set(contrat) - {"phase", "sortie"} == {"palier", "valeur", "demande"}
                and type(contrat["palier"]) is int and contrat["palier"] in list(Palier)
                and isinstance(contrat["valeur"], (int, float))), "Contrat d'intention invalide"
        assert contrat.get("phase", "continuer") in (
            "naitre", "continuer", "attendre", "finir", "indeterminee"), "Phase d'intention invalide"
        sortie = contrat.get("sortie")
        if sortie is not None:
            assert (isinstance(sortie, dict) and set(sortie) == {"cause", "minute", "faits", "intention"}
                    and sortie["cause"] in (None, "accomplie", "dementie", "palier", "gain")
                    and type(sortie["minute"]) is int and isinstance(sortie["faits"], dict)
                    and isinstance(sortie["intention"], dict)
                    and set(sortie["intention"]) == {"but", "motif", "depuis"}), "Sortie d'intention invalide"
        demande = contrat["demande"]
        assert (demande is None or isinstance(demande, dict)
                and (set(demande) == {"agenda"} and isinstance(demande["agenda"], str)
                     or "condition" in demande and set(demande) <= {"condition", "tache", "raison"}
                     and condition_valide(monde, demande["condition"])
                     and type(demande.get("tache", False)) is bool)), "Demande d'intention invalide"
        if demande and "raison" in demande:
            raison = demande["raison"]
            assert (isinstance(raison, dict) and set(raison) == {"qui", "besoin"}
                    and (raison["qui"] == "joueur" or raison["qui"] in monde.objets)
                    and raison["besoin"] in ("faim", "chaleur")), "Raison d'intention invalide"
    stock = projets(monde, id)
    assert len([a for a in stock if a["etat"] == "actif"]) <= 3, "Trop d'agendas actifs"
    assert len({a["id"] for a in stock}) == len(stock), "Identifiants d'agenda dupliqués"
    for a in stock:
        assert (a["etat"] in ("actif", "sommeil", "atteint", "abandonne")
                and type(a["depuis"]) is int and isinstance(a["raison"], str)
                and a["origine"]["type"] in ("scenario", "situation", "evenement") and "plan" not in a
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
