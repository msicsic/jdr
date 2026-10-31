"""Accès unique aux engagements et aux agendas ; stockage historique inchangé en A1.

Au premier lot qui en a besoin, chaque engagement deviendra un agenda d'origine
« contrat » s'il est payé, « parole » sinon, en conservant condition, bénéficiaire et minute.
Les lectures renvoient des copies : toute mutation passe par une opération nommée.
"""
from . import memoire
import copy
import hashlib
import json
import math
from contextlib import contextmanager

CHAMPS = {"engagements": list}

# Cause -> vocabulaire et valeurs ; aucune identité ni méthode d'action.
NAISSANCES = {
    "dette_situation": {"sorte": "obtenir", "valeurs": ("honnetete", "ambition")},
    "bien_spolie": {"sorte": "récupérer", "valeurs": ("ambition", "honnetete", "douceur", "fierte")},
    "occasion_protection": {"sorte": "offrir", "valeurs": ("ambition",)},
}


def _dette_situation(monde, id):
    """Situation personnelle connue du porteur, distincte d'une créance locale."""
    return (monde.objets[id].get("profil") or {}).get("situation", {}).get("dette", 0)


def _torts_connus(monde, id):
    """Preuves propres persistantes ; ni mémoire courte ni enquête sur le réel."""
    from .esprits import lire
    e = lire(monde, id)
    for objet, portage in sorted(e["portages"].items()):
        connu = memoire.faits_connus(monde, id, objet)
        p = connu.get("lieu", {}).get("possession", {})
        if (p.get("proprietaire") == id and p.get("porteur") not in (None, id)
                and p.get("permis") is False
                and portage["auteur"] == p["porteur"] and not connu.get("fin", {}).get("valeur")):
            yield objet, portage


def _biens_soupconnes(monde, id):
    """Une disparition propre attribuée reste distincte d'un portage prouvé."""
    from .esprits import lire
    e = lire(monde, id)
    r = e['indices_soupcon']
    for preuve, s in sorted(r['soupcons'].items()):
        if s['auteur'] is None:
            continue
        for objet, indices in sorted(s['indices'].items()):
            constat = r['constats'].get(objet, {}).get('present', {})
            if (indices.get('present') is True and constat.get('proprietaire') == id
                    and constat.get('valeur') is False and objet not in e['portages']
                    and not memoire.fait_brut(monde, id, objet, 'fin', {}).get('valeur')):
                yield objet, {'auteur': s['auteur'], 'preuve': preuve}


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
    from .occasion_protection import occasions
    for p in occasions(monde, id):
        cause = 'occasion_protection'
        if any(a['origine'].get('cause') == cause and a['parametres']['qui'] == p['qui']
               for a in (_stock(monde, id) or [])):
            continue
        _naitre(monde, id, cause, p, {'type': 'occasion', 'cause': cause,
                'de': p['qui'], 'minute': monde.data['minutes']}, empreinte)
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
    for objet, p in _biens_soupconnes(monde, id):
        # Le soupçon ouvre une enquête, jamais un droit de prise sur autrui.
        if any(a['parametres'].get('objet') == objet and a['origine'].get('preuve') == p['preuve']
               for a in (_stock(monde, id) or [])):
            continue
        prix = monde.objets.get(objet, {}).get('prix') or VALEUR_OBJET
        _naitre(monde, id, 'bien_spolie', {'objet': objet, 'qui': p['auteur'], 'prix_cru': prix},
                {'type': 'evenement', 'de': p['auteur'], 'cause': 'bien_spolie',
                 'preuve': p['preuve'], 'soupcon': True, 'minute': monde.data['minutes']}, empreinte)
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
    return set(e) - {"agendas", "contrat_intention", "mandats_percus"}


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
    if i['but'].get('agenda'):
        contrat = {**contrat, 'recours': entrees_recours(monde, id, i['but']['agenda'])}
    e["contrat_intention"] = {**{k: copy.deepcopy(i[k]) for k in ("but", "motif", "depuis")},
                              "contrat": copy.deepcopy(contrat)}
    a = _projet(monde, id, i['but'].get('agenda'))
    if a and i['plan'] and not any('mandat' in g.get('contenu', {}) for g in i['plan']):
        qui = i['but'].get('qui')
        for x in a.get('attributions', []):
            if x['etat'] == 'active' and qui in x['parametres']['qui'] and aide_echue(monde, x):
                x['etat'] = 'reprise'


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


def charges_suspendues(monde, id):
    """Charges du seul engagement courant ; aucune survie après son abandon."""
    from .esprits import lire
    i = lire(monde, id)["intention"]
    reconstruction = getattr(monde, "_reconstruction_charges", None)
    if i:
        return copy.deepcopy(i.get("charges_suspendues", {}))
    return copy.deepcopy(reconstruction[1]) if reconstruction and reconstruction[0] == id else {}


@contextmanager
def reconstruction_charges(monde, id, charges):
    """Une évaluation ne libère la garde qu'après le remplacement effectif du but."""
    ancien = getattr(monde, "_reconstruction_charges", None)
    monde._reconstruction_charges = (id, charges)
    try:
        yield
    finally:
        monde._reconstruction_charges = ancien


def retenir_charges(monde, id, conditions, *, restaurer=False):
    from .esprits import esprit
    i = esprit(monde, id)["intention"]
    if conditions:
        i["charges_suspendues"] = {"conditions": copy.deepcopy(conditions), "restaurer": restaurer}



def champs_profil():
    return {"agendas"}


def projets(monde, id):
    return copy.deepcopy(_stock(monde, id) or [])


def _projet(monde, titulaire, identifiant):
    return next((a for a in (_stock(monde, titulaire) or [])
                 if a["id"] == identifiant), None)


def filiation(monde, titulaire, identifiant):
    """Chaîne copiée racine → agenda ; la profondeur est le nombre d'arêtes.

    Les références sont locales au titulaire, jamais des identifiants globaux.
    Les liens restent consultables après la fin d'un projet.
    """
    chaine, vus = [], set()
    while True:
        if titulaire in vus:
            raise ValueError("Cycle de mandat")
        vus.add(titulaire)
        a = _projet(monde, titulaire, identifiant)
        if a is None:
            raise ValueError("Parent de mandat absent")
        chaine.append({"titulaire": titulaire, "agenda": identifiant})
        origine = a["origine"]
        if origine["type"] != "mandat":
            return list(reversed(chaine))
        titulaire, identifiant = origine["de"], origine["parent"]


def enfants(monde, titulaire, identifiant):
    a = _projet(monde, titulaire, identifiant)
    if a is None:
        raise ValueError("Agenda absent")
    return copy.deepcopy(a.get("confies", []))


def charge_joueur(monde, sorte, parametres):
    """Une charge explicite de Corvus, réutilisée pour ses confirmations."""
    p = _condition_mandat(monde, sorte, parametres)
    stock = _stock(monde, 'joueur', creer=True)
    a = next((a for a in stock if a['origine']['type'] == 'evenement'
              and a['sorte'] == sorte and a['parametres'] == p), None)
    if a is None:
        _place_charge_joueur(monde)
        a = {'id': 'j' + str(len(stock) + 1), 'sorte': sorte, 'parametres': p,
             'maniere': {'sans_violence': True}, 'origine': {
                 'type': 'evenement', 'de': 'joueur', 'minute': monde.data['minutes'], 'cause': 'parole'}}
        _changer(monde, 'joueur', a, 'actif', 'charge explicite', _croyances(monde, 'joueur'))
        stock.append(a)
    return copy.deepcopy(a)


def _place_charge_joueur(monde):
    from .monde import ErreurMonde
    actifs = [a['id'] for a in projets(monde, 'joueur') if a['etat'] == 'actif']
    if len(actifs) >= 3:
        raise ErreurMonde("Corvus a déjà trois charges actives.",
                          f'charges={actifs}; attendu : moins de 3 charges actives avant une nouvelle charge')


def offres_mandat_joueur(monde):
    """Offres effectivement entendues, jamais agendas privés des interlocuteurs."""
    return copy.deepcopy(monde.data.get('offres_mandat_joueur', []))


def proposer_mandat_joueur(monde, mandant, mandat):
    from .voix import identifie
    from .ouie import saisit
    if not saisit(monde, mandant, 'joueur', 'dire') or not identifie(monde, 'joueur', mandant):
        return None
    p = _condition_mandat(monde, mandat['sorte'], mandat['parametres'])
    # La filiation et les attributions sont contrôlées sur copie avant l'offre.
    confier(monde.copier(), mandant, mandat['parent'], 'joueur', mandat['sorte'], p, accepte=True,
            echeance=mandat.get('echeance'))
    stock = monde.data.setdefault('offres_mandat_joueur', [])
    ancienne = next((o for o in stock if o['mandant'] == mandant and o['parent'] == mandat['parent']
                     and o['sorte'] == mandat['sorte'] and o['parametres'] == p), None)
    if ancienne is not None:
        return copy.deepcopy(ancienne)
    o = {'id': 'm' + str(len(stock) + 1), 'mandant': mandant, 'parent': mandat['parent'],
         'sorte': mandat['sorte'], 'parametres': p, 'minute': monde.data['minutes'], 'statut': 'propose'}
    if 'echeance' in mandat:
        o['echeance'] = mandat['echeance']
    stock.append(o)
    return copy.deepcopy(o)


def repondre_mandat_joueur(monde, mandant, identifiant, accepter):
    from .monde import ErreurMonde
    o = next((o for o in monde.data.get('offres_mandat_joueur', [])
              if o['id'] == identifiant and o['mandant'] == mandant), None)
    if o is None:
        raise ErreurMonde("Corvus n'a pas reçu cette offre de mandat.",
                          f'offre={identifiant!r}, mandant={mandant}; attendu : {offres_mandat_joueur(monde)}')
    if o['statut'] != 'propose':
        return copy.deepcopy(o)
    jugement = {'qui': 'joueur', 'minute': monde.data['minutes'], 'sorte': o['sorte'],
                'parametres': o['parametres'], 'issue': 'accepte' if accepter else 'refus'}
    jugement['raison'] = 'adhesion' if accepter else 'refus'
    if accepter:
        echeance = o['echeance'] if 'echeance' in o else echeance_observee(
            monde, mandant, o['parent'], 'joueur', o['sorte'], o['parametres'])
        enfant = confier(monde, mandant, o['parent'], 'joueur', o['sorte'], o['parametres'], accepte=True,
                        echeance=echeance)
        o['agenda'] = enfant['id']
    retenir_jugement(monde, mandant, o['parent'], jugement)
    o['statut'] = 'accepte' if accepter else 'refuse'
    return copy.deepcopy(o)


def bilan_mandat_joueur(monde, mandant, identifiant, issue):
    from .monde import ErreurMonde
    a = _projet(monde, 'joueur', identifiant)
    if a is None or a['origine']['type'] != 'mandat' or a['origine']['de'] != mandant:
        raise ErreurMonde("Corvus n'a pas cette charge de cet interlocuteur.",
                          f'agenda={identifiant!r}, mandant={mandant}; attendu : mandat accepté de ce mandant')
    if issue not in ISSUES_COMPTE_RENDU:
        raise ErreurMonde("Cette issue de mandat est inconnue.",
                          f'issue={issue!r}; attendu : {ISSUES_COMPTE_RENDU}')
    if 'compte_rendu' in a:
        if a['compte_rendu']['contenu']['issue'] != issue:
            raise ErreurMonde("Ce mandat a déjà fait l'objet d'un compte rendu.",
                              f'issue={issue}; attendu : {a["compte_rendu"]["contenu"]["issue"]}')
        return copy.deepcopy(a['compte_rendu']['contenu'])
    contenu = {'type': 'compte_rendu', 'charge': {'mandant': mandant, 'parent': a['origine']['parent'],
               'agenda': a['id'], 'sorte': a['sorte'], 'parametres': copy.deepcopy(a['parametres'])}, 'issue': issue}
    if 'compte_rendu' not in a:
        _changer(monde, 'joueur', a, 'atteint' if issue == 'reussi' else 'abandonne',
                 'issue declaree', _croyances(monde, 'joueur'))
        retenir_compte_emis(monde, 'joueur', contenu)
    return contenu


def mandats_visibles(monde):
    from .voix import nom_pour_joueur
    lignes = []
    statuts = {'propose': 'offre à accepter', 'accepte': 'charge acceptée', 'refuse': 'offre refusée'}
    etats = {'actif': 'en cours', 'sommeil': 'en sommeil', 'atteint': 'terminée', 'abandonne': 'abandonnée'}
    issues = {'reussi': 'une réussite', 'echoue': 'un échec', 'renonce': 'un renoncement'}
    for o in offres_mandat_joueur(monde):
        lignes.append(f"Mandat {o['id']} de {nom_pour_joueur(monde, o['mandant'])} : "
                      + phrase_charge(monde, o['sorte'], o['parametres']) + ' — ' + statuts[o['statut']] +
                      (f" ; échéance : minute {o['echeance']}" if 'echeance' in o else '') +
                      (f" ({o['agenda']})" if o.get('agenda') else '') + '.')
    for a in projets(monde, 'joueur'):
        etat = 'issue déclarée' if a['raison'] == 'issue declaree' else etats[a['etat']]
        lignes.append(f"Charge {a['id']} : " + phrase_charge(monde, a['sorte'], a['parametres']) +
                      ' — ' + etat + '.')
        for r in a.get('comptes_recus', []):
            lignes.append(f"{nom_pour_joueur(monde, r['de'])} déclare {issues[r['contenu']['issue']]}.")
    return lignes


def phrase_charge(monde, sorte, p):
    from .voix import nom_pour_joueur
    from .francais import lieu
    personnes = ', '.join(nom_pour_joueur(monde, q) for q in p['qui'])
    if sorte == 'amener':
        return 'amener ' + personnes + ' dans ' + lieu(monde.data['salles'][p['lieu']])
    from .paroles import _phrase
    if 'fait' in p:
        f = p['fait']
        return 'informer ' + personnes + ' : ' + _phrase(monde, f['sujet'], f['attribut'], f['valeur'])
    return 'informer ' + personnes + ' de l’avis sur la menace de l’eau'


ISSUES_COMPTE_RENDU = ("reussi", "echoue", "renonce")


def compte_a_rendre(monde, id):
    """Une charge terminale reste à annoncer, sans lire la situation du mandant."""
    from .pnj import pourraient_se_parler
    from .caractere import prix_faute
    for a in projets(monde, id):
        o = a["origine"]
        if (o["type"] != "mandat" or a["etat"] not in ("atteint", "abandonne")
                or "compte_rendu" in a or not pourraient_se_parler(monde, id, o["de"])):
            continue
        issue = ("reussi" if a["etat"] == "atteint" else
                 "renonce" if a["raison"] == "supplante" else "echoue")
        # Dissimuler son échec reste une faute pesée par l'honnêteté commune.
        faute = prix_faute(monde, id)
        if issue != "reussi" and faute is not None and faute < poids(monde, id, a):
            issue = "reussi"
        return {"type": "compte_rendu", "charge": {
            "mandant": o["de"], "parent": o["parent"], "agenda": a["id"],
            "sorte": a["sorte"], "parametres": a["parametres"]}, "issue": issue}
    return None


def retenir_compte_emis(monde, id, contenu):
    a = _projet(monde, id, contenu["charge"]["agenda"])
    _verifier_compte(monde, id, a, contenu)
    assert a["etat"] in ("atteint", "abandonne"), "Charge non terminée"
    if "compte_rendu" in a:
        return False
    a["compte_rendu"] = {"contenu": copy.deepcopy(contenu), "minute": monde.data["minutes"]}
    return True


def _constat_charge(monde, id, charge):
    """Issue prouvée par le porteur ; l'absence de preuve n'est pas un échec."""
    from .esprits import lire, RECENT
    from .social import transmission_attestee
    p = charge["parametres"]
    if charge["sorte"] == "informer":
        if all(transmission_attestee(monde, id, q, _noyau(charge)) for q in p["qui"]):
            return "reussi"
        return None
    constats = [memoire.fait_brut(monde, id, q, 'lieu', {}) for q in p["qui"]]
    propres = [c for c in constats if c.get("source") in ("vu", "essai")
               and monde.data["minutes"] - c["minute"] <= RECENT and c["valeur"] is not None]
    if any(c["valeur"] != p["lieu"] for c in propres):
        return "echoue"
    if len(propres) == len(constats):
        return "reussi"
    return None


def recevoir_compte(monde, id, locuteur, contenu):
    """Parole sur un contrat partagé, jamais lecture de l'état privé de l'enfant."""
    from .esprits import memoriser, poids_source
    from .echanges import jet_persuasion, clarte
    from .voix import source_dite, identifie, se_mefier
    charge = contenu["charge"]
    source = source_dite(monde, id, locuteur)
    memoriser(monde, id, {"type": "compte_rendu", "de": source,
                          "contenu": copy.deepcopy(contenu)})
    if id != charge["mandant"]:
        return _recevoir_issue(monde, id, locuteur, contenu)
    if charge["mandant"] != id or not identifie(monde, id, locuteur):
        return None
    parent = _projet(monde, id, charge["parent"])
    if parent is None or {"titulaire": locuteur, "agenda": charge["agenda"]} not in parent.get("confies", []):
        return None
    enfant = _projet(monde, locuteur, charge["agenda"])
    if (contenu["issue"] not in ISSUES_COMPTE_RENDU or charge["sorte"] != enfant["sorte"]
            or charge["parametres"] != enfant["parametres"]):
        return None
    propre = _constat_charge(monde, id, charge)
    dementi = propre is not None and propre != contenu["issue"]
    if dementi and id != 'joueur':
        se_mefier(monde, id, locuteur, "vu")
    # Corvus garde son jugement : le registre conserve seulement le dit.
    accepte = id != 'joueur' and not dementi and jet_persuasion(monde, id, locuteur, 10)[0]
    croyance = {"valeur": propre if propre is not None else contenu["issue"] if accepte else None,
                "source": ("entendu" if charge["sorte"] == "informer" else "vu") if propre is not None else source,
                "minute": monde.data["minutes"], "confiance": 1 if propre is not None else round(.7 * clarte(monde, id), 2)}
    croyance["poids"] = poids_source(monde, id, croyance) if id != 'joueur' or propre is not None else 0
    rapports = parent.setdefault("comptes_recus", [])
    rapports[:] = [r for r in rapports if (r["de"], r["contenu"]["charge"]["agenda"]) != (locuteur, charge["agenda"])]
    rapports.append({"de": locuteur, "contenu": copy.deepcopy(contenu), "croyance": croyance})
    return "dementi" if dementi else "crue" if accepte else "doute"


def _reviser_comptes(monde, id, a):
    from .esprits import memoriser, RECENT
    for r in a.get("comptes_recus", []):
        charge = r["contenu"]["charge"]
        propre = _constat_charge(monde, id, charge)
        source = "entendu" if charge["sorte"] == "informer" else "vu"
        c = r["croyance"]
        if propre is not None and (c["source"] != source or c["valeur"] != propre):
            if (c["source"].startswith("dit:") and c["valeur"] is not None and c["valeur"] != propre
                    and monde.data["minutes"] - c["minute"] <= RECENT):
                memoriser(monde, id, {"type": "mensonge_decouvert", "locuteur": r["de"],
                                      "sujet": id})
            c.update(valeur=propre, source=source, minute=monde.data["minutes"], confiance=1,
                     poids=.8 if source == "entendu" else 1)


def _percus(monde, id, *, creer=False):
    from .esprits import lire, esprit
    evaluation = getattr(monde, "_evaluation_agendas", None)
    if evaluation is not None and evaluation[0] == id:
        if evaluation[1]["percus"] is None and creer:
            evaluation[1]["percus"] = []
        return evaluation[1]["percus"]
    return esprit(monde, id).setdefault("mandats_percus", []) if creer else lire(monde, id).get("mandats_percus")


def mandats_percus(monde, id):
    """Contrats entendus, hors mémoire courte ; seules connaissances du porteur."""
    return copy.deepcopy(_percus(monde, id) or [])


def _charge_partagee(monde, titulaire, charge):
    if not isinstance(charge, dict) or set(charge) != {"mandant", "parent", "agenda", "sorte", "parametres"}:
        return False
    if charge["agenda"] is None:
        parent = _projet(monde, charge["mandant"], charge["parent"])
        return parent is not None and any(j["qui"] == titulaire and j["sorte"] == charge["sorte"]
                                         and j["parametres"] == charge["parametres"]
                                         for j in parent.get("jugements", []))
    enfant = _projet(monde, titulaire, charge["agenda"])
    return enfant is not None and charge == {
        "mandant": enfant["origine"].get("de"), "parent": enfant["origine"].get("parent"),
        "agenda": enfant["id"], "sorte": enfant["sorte"], "parametres": enfant["parametres"]}


def percevoir_mandat(monde, id, locuteur, charge, titulaire):
    """Réception de la charge effectivement dite ; aucun avancement privé lu."""
    from .voix import identifie
    if (id in ("joueur", charge["mandant"], titulaire) or locuteur != charge["mandant"]
            or not identifie(monde, id, locuteur) or not _charge_partagee(monde, titulaire, charge)):
        return None
    stock = _percus(monde, id, creer=True)
    r = next((r for r in stock if _identite_charge(r["de"], r["charge"]) == _identite_charge(titulaire, charge)), None)
    if r is None:
        r = {"de": titulaire, "charge": copy.deepcopy(charge), "minute": monde.data["minutes"], "source": "entendu"}
        stock.append(r)
    else:
        r.update(charge=copy.deepcopy(charge), source="entendu")
    abus = _abus_charge(monde, id, charge)
    if abus:
        r.setdefault("abus", abus)
    _actualiser_epreuves(monde, id)
    return "mandat entendu"


def _recevoir_issue(monde, id, locuteur, contenu):
    from .voix import identifie, source_dite
    from .echanges import jet_persuasion, clarte
    from .esprits import poids_source
    charge = contenu["charge"]
    if (id == "joueur" or not identifie(monde, id, locuteur)
            or not identifie(monde, id, charge["mandant"])
            or not _charge_partagee(monde, locuteur, charge)):
        return None
    stock = _percus(monde, id, creer=True)
    r = next((r for r in stock if _identite_charge(r["de"], r["charge"]) == _identite_charge(locuteur, charge)), None)
    if r is None:
        r = {"de": locuteur, "charge": copy.deepcopy(charge), "minute": monde.data["minutes"],
             "source": source_dite(monde, id, locuteur)}
        stock.append(r)
    r["charge"] = copy.deepcopy(charge)
    if r.get("croyance", {}).get("source") in ("vu", "entendu"):
        return "crue"  # Le résultat déjà constaté n'est pas rejugé sur un nouvel état des lieux.
    propre = _constat_charge(monde, id, charge)
    accepte = propre is None and jet_persuasion(monde, id, locuteur, 10)[0]
    c = {"valeur": propre if propre is not None else contenu["issue"] if accepte else None,
         "source": ("entendu" if charge["sorte"] == "informer" else "vu") if propre is not None else source_dite(monde, id, locuteur),
         "minute": monde.data["minutes"], "confiance": 1 if propre is not None else round(.7 * clarte(monde, id), 2)}
    c["poids"] = poids_source(monde, id, c)
    r["croyance"] = c
    _actualiser_epreuves(monde, id)
    return "crue" if propre is not None or accepte else "doute"


def _abus_charge(monde, id, charge):
    """Exposition crue à un péril ou mensonge imposé, selon le prix commun.

    Autoriser la violence ne suffit pas à la rendre nécessaire. Le contenu
    d'information doit contredire un savoir pour constituer une faute.
    """
    from .caractere import prix_faute
    from .esprits import croyance, poids_source
    if charge["sorte"] == "amener":
        from .eau import en_peril
        from .defense import lieux_dangereux
        lieu = charge["parametres"]["lieu"]
        return {"cause": "peril", "prix": None} if en_peril(monde, id, lieu) or lieu in lieux_dangereux(monde, id) else None
    fait = _noyau(charge)
    if fait["type"] == "affirmation":
        c = croyance(monde, id, fait["sujet"], fait["attribut"])
        if c and c["valeur"] is not None and poids_source(monde, id, c) > 0 and c["valeur"] != fait["valeur"]:
            prix = prix_faute(monde, id)
            if prix is None or prix > 0:
                return {"cause": "honnetete", "prix": prix}
    return None


def _epreuve(monde, id, mandant, preuve, issue, source="essai", poids=1):
    evaluation = getattr(monde, "_evaluation_agendas", None)
    arguments = (id, mandant, preuve, issue, source, poids)
    if evaluation is not None:
        evaluation[1]["epreuves"].append(arguments)
    else:
        from .relations import eprouver_mandat
        eprouver_mandat(monde, *arguments)


def _poids_abus(abus):
    from .caractere import FAUTE
    return 1 if abus["prix"] is None else min(1, abus["prix"] / FAUTE)


def _identite_charge(titulaire, charge):
    return hashlib.sha256(json.dumps([titulaire, charge["mandant"], charge["parent"],
                                     charge["sorte"], charge["parametres"]], sort_keys=True).encode()).hexdigest()


def _actualiser_epreuves(monde, id):
    from .esprits import lire, poids_source
    for a in _stock(monde, id) or []:
        o = a["origine"]
        if o["type"] != "mandat":
            continue
        preuve = f"{id}:{a['id']}"
        if a["etat"] in ("actif", "sommeil"):
            abus = _abus_charge(monde, id, a)
            if abus:
                a.setdefault("abus", abus)
        if a.get("abus"):
            charge = {"mandant": o["de"], "parent": o["parent"], "sorte": a["sorte"], "parametres": a["parametres"]}
            _epreuve(monde, id, o["de"], _identite_charge(id, charge), "abus", poids=_poids_abus(a["abus"]))
        if a["etat"] in ("atteint", "abandonne"):
            issue = "reussi" if a["etat"] == "atteint" else "echoue"
            sources = ([r["croyance"] for r in a.get("comptes_recus", [])
                        if r["croyance"]["valeur"] == "reussi"] if a["raison"] == "compte rendu cru" else
                       [memoire.fait_brut(monde, id, q, 'lieu', {})
                        for q in _destinataires(a)] if a["raison"] == "arrivee crue" else [])
            dites = [c for c in sources if c.get("source", "").startswith("dit:")]
            _epreuve(monde, id, o["de"], preuve, issue,
                     dites[0]["source"] if dites else "essai",
                     min(poids_source(monde, id, c) for c in dites) if dites else 1)
    for r in _percus(monde, id) or []:
        charge = r["charge"]
        # Connaître le contrat permet de reconnaître une arrivée, jamais de
        # transformer l'absence d'arrivée d'un projet en cours en échec.
        c = r.get("croyance")
        propre = (_constat_charge(monde, id, charge) if charge["agenda"] is not None
                  and (c is None or c["source"].startswith("dit:")) else None)
        if propre == "reussi" or propre is not None and "croyance" in r:
            r["croyance"] = {"valeur": propre, "source": "entendu" if charge["sorte"] == "informer" else "vu",
                             "minute": monde.data["minutes"], "confiance": 1, "poids": 1}
        preuve = f"{r['de']}:{charge['agenda']}"
        if r.get("abus"):
            _epreuve(monde, id, charge["mandant"], _identite_charge(r["de"], charge), "abus", r["source"],
                     _poids_abus(r["abus"]) * poids_source(monde, id, {"source": r["source"]}))
        c = r.get("croyance")
        if c and c["valeur"] is not None:
            _epreuve(monde, id, charge["mandant"], preuve, c["valeur"], c["source"],
                     poids_source(monde, id, c) if c["source"].startswith("dit:") else 1)


def _acheve_par_comptes(monde, id, a):
    from .esprits import poids_source
    rapports = a.get("comptes_recus", [])
    if not rapports or a["sorte"] not in ("amener", "informer"):
        return False
    for qui in _destinataires(a):
        charge = {"sorte": a["sorte"], "parametres": {**a["parametres"], "qui": [qui]}}
        if _constat_charge(monde, id, charge) == "reussi":
            continue
        if not any(r["contenu"]["charge"]["sorte"] == a["sorte"]
                   and {k: v for k, v in r["contenu"]["charge"]["parametres"].items() if k != "qui"}
                       == {k: v for k, v in a["parametres"].items() if k != "qui"}
                   and qui in r["contenu"]["charge"]["parametres"]["qui"]
                   and r["croyance"]["valeur"] == "reussi"
                   and poids_source(monde, id, r["croyance"]) > 0 for r in rapports):
            return False
    return True


def retenir_jugement(monde, mandant, parent, jugement):
    """Décision du destinataire conservée avant tout récit, y compris un refus."""
    if getattr(monde, "_evaluation_agendas", None) is not None:
        raise ValueError("Publier le jugement après le devis")
    a = _projet(monde, mandant, parent)
    if a is None:
        raise ValueError("Parent de mandat absent")
    a.setdefault("jugements", []).append(copy.deepcopy(jugement))
    from .voix import identifie
    if jugement['qui'] != 'joueur' and identifie(monde, jugement["qui"], mandant):
        abus = _abus_charge(monde, jugement["qui"], jugement)
        if abus:
            a["jugements"][-1]["abus"] = abus
            charge = {**jugement, "mandant": mandant, "parent": parent}
            _epreuve(monde, jugement["qui"], mandant, _identite_charge(jugement["qui"], charge),
                     "abus", poids=_poids_abus(abus))


def devis_mandat(monde, mandant, parent, titulaire, sorte, parametres):
    """Plan social et coût commun sur copie ; aucune obligation publiée."""
    copie = monde.copier()
    a = confier(copie, mandant, parent, titulaire, sorte, parametres, accepte=True)
    cout = []
    resultat = planifier(copie, titulaire, a["id"], cout=cout)
    return (cout[0], resultat[1]) if resultat is not None and cout else None


def devis_observateur(monde, observateur, parent, acteur, sorte, parametres, *, transmis=(), duree=None):
    """Prochain sous-but estimé sur les seules données de l'observateur.

    Les connaissances partagées ou à transmettre sont explicites ; le mandat
    hypothétique ne publie rien. Le jugement réel reste ``devis_mandat``.
    """
    from .planification import ContexteDevis
    if acteur == 'joueur':
        # Le calcul traite toute personne comme un acteur neutre. Corvus n'a
        # pas d'esprit automatique : son substitut existe seulement dans la
        # copie de calcul, avec les seules croyances du mandant.
        from .esprits import esprit
        copie = monde.copier()
        substitut = '__mandataire__'
        while substitut in copie.objets:
            substitut += '_'
        copie.objets[substitut] = {'id': substitut, 'type': 'personnage', 'nom': 'mandataire',
                                   'lieu': None, 'mobile': True}
        connus = memoire.faits_connus(copie, observateur)
        if 'joueur' not in connus:
            return None
        memoire.installer_faits_projetes(copie, observateur, substitut, connus['joueur'])
        return devis_observateur(copie, observateur, parent, substitut, sorte, parametres,
                                 transmis=transmis, duree=duree)
    p = _condition_mandat(monde, sorte, parametres)
    if (not _personne_disponible_crue(monde, observateur, acteur)
            or any(not _personne_disponible_crue(monde, observateur, q) for q in p["qui"])):
        return None
    contexte = ContexteDevis(observateur, acteur, transmis)
    copie = contexte.projeter(monde)
    if copie is None:
        return None
    if any(q not in copie.objets for q in p["qui"]):
        # Une identité dans l'agenda ne fournit pas à elle seule les
        # connaissances nécessaires à son apparition dans le modèle fermé.
        return None
    # Un devis n'est pas une publication : reconstruire une filiation lirait
    # les esprits des ancêtres, absents à juste titre du modèle fermé.
    a = copy.deepcopy(_projet(monde, observateur, parent))
    if a is None:
        raise ValueError("Parent de mandat absent")
    a.update(id="devis", sorte=sorte, parametres=_condition_mandat(copie, sorte, p),
             etat="actif", origine={"type": "scenario"})
    for champ in ("confies", "jugements", "attributions"):
        a.pop(champ, None)
    copie.data["esprits"][acteur]["agendas"] = [a]
    if sorte == "informer" and "avis" in parametres:
        from .eau import menacee
        from .esprits import croire
        from .social import avis_exprime
        avis = parametres["avis"]
        if menacee(monde, observateur, avis["objet"]) != avis["valeur"]:
            return None
        dit = avis_exprime(copie, observateur, avis["objet"], avis["valeur"])
        # Hypothèse explicite d'une parole acceptée, comme les faits transmis.
        # La réception réelle garde son jugement ; aucune mesure ne voyage ici.
        croire(copie, acteur, avis["objet"], "prevision", dit["valeur"],
               "dit:" + observateur, dit["conviction"])
    cout = []
    resultat = planifier(copie, acteur, a["id"], cout=cout)
    if duree is not None and resultat is not None:
        from .planification import duree_devis
        duree.append(duree_devis(copie, acteur, resultat[1]))
    return (cout[0], resultat[1]) if resultat is not None and cout else None


def _condition_mandat(monde, sorte, parametres):
    """Structure et identité persistantes, indépendantes de la disponibilité.

    Un jugement et une filiation restent valides après la mort d'une cible.
    L'admissibilité du prochain geste dépend des croyances, séparément.
    """
    from .noms import PERSONNES
    if sorte not in ("amener", "informer") or not isinstance(parametres, dict):
        raise ValueError("Sorte de mandat invalide")
    p = copy.deepcopy(parametres)
    qui = p.get("qui")
    qui = [qui] if isinstance(qui, str) else qui
    if (not isinstance(qui, list) or not qui
            or any(not isinstance(q, str) or q not in monde.objets
                   or monde.objets[q]["type"] not in PERSONNES for q in qui)):
        raise ValueError("Destinataires de mandat invalides")
    p["qui"] = sorted(set(qui))
    if sorte == "amener":
        if set(p) != {"qui", "lieu"} or p["lieu"] not in monde.data["salles"]:
            raise ValueError("Destination de mandat invalide")
    elif (set(p) not in ({"qui", "fait"}, {"qui", "avis"})
          or not isinstance(_noyau({"parametres": p}), dict)):
        raise ValueError("Contenu de mandat invalide")
    return p


def confier(monde, mandant, parent, titulaire, sorte, parametres, *, accepte, echeance=None):
    """Publier une acceptation déjà jugée ; aucun jet, choix ni ancien contrat.

    Refus : aucun effet. Relance : même enfant, même état (même terminal),
    date de confirmation renouvelée sans effacer la date d'origine.
    Cette publication entre deux esprits ne s'effectue pas dans un devis.
    """
    from .monde import ErreurMonde
    if type(accepte) is not bool:
        raise ValueError("Acceptation de mandat invalide")
    if not accepte:
        return None
    if getattr(monde, "_evaluation_agendas", None) is not None:
        raise ValueError("Publier le mandat après le devis")
    if titulaire != 'joueur' and (titulaire not in monde.objets
            or monde.objets[titulaire]["type"] != "personnage"):
        raise ValueError("Titulaire de mandat invalide")
    p = _condition_mandat(monde, sorte, parametres)
    if echeance is not None and (type(echeance) is not int or echeance < monde.data['minutes']):
        raise ErreurMonde("Cette échéance de mandat est dépassée ou invalide.",
                          f'echeance={echeance!r}; attendu : entier >= {monde.data["minutes"]}, ou None')
    chaine = filiation(monde, mandant, parent)
    if titulaire in {r["titulaire"] for r in chaine}:
        raise ErreurMonde("Ce mandat reviendrait à l'un de ses mandants.",
                          f"titulaire={titulaire} ; attendu : titulaire absent de {chaine}")
    if len(chaine) >= 3:
        raise ErreurMonde("Ce mandat a déjà été confié deux fois de suite.",
                          f"parent={mandant}/{parent}, profondeur={len(chaine)-1} ; attendu : profondeur < 2")
    a = _projet(monde, mandant, parent)
    precedentes = [x for x in a.get('attributions', []) if _meme_charge(x, sorte, p)]
    for x in precedentes:
        if x['titulaire'] == titulaire and x['etat'] != 'active':
            raise ErreurMonde("Cette charge a déjà été retirée à ce titulaire.",
                              f"titulaire={titulaire} ; attendu : titulaire non essayé pour {sorte}/{p}")
        if x['etat'] == 'active' and x['titulaire'] != titulaire and not aide_echue(monde, x):
            raise ErreurMonde("Cette charge est encore confiée à quelqu'un.",
                              f"titulaire={titulaire} ; attendu : attribution échue pour {sorte}/{p}")
        if x['etat'] == 'active' and x['titulaire'] == titulaire:
            ancien = _projet(monde, titulaire, x['agenda'])
            if ancien['sorte'] != sorte or _condition_mandat(monde, sorte, ancien['parametres']) != p:
                raise ErreurMonde("Cette demande recouvre une charge déjà confiée à ce titulaire.",
                                  f"parametres={p} ; attendu : {ancien['parametres']}")
    for ref in a.get("confies", []):
        enfant = _projet(monde, ref["titulaire"], ref["agenda"])
        if (ref["titulaire"] == titulaire and enfant["sorte"] == sorte
                and _condition_mandat(monde, sorte, enfant["parametres"]) == p):
            enfant["confirme"] = monde.data["minutes"]
            return copy.deepcopy(enfant)
    if titulaire == 'joueur':
        _place_charge_joueur(monde)
    actualiser(monde, titulaire)
    stock = _stock(monde, titulaire) or []
    n = 1
    while any(x["id"] == f"a{n}" for x in stock):
        n += 1
    enfant = {"id": f"a{n}", "sorte": sorte, "parametres": p,
              "maniere": copy.deepcopy(a.get("maniere", {"sans_violence": True})),
              "origine": {"type": "mandat", "de": mandant, "parent": parent,
                          "minute": monde.data["minutes"]},
              "confirme": monde.data["minutes"]}
    empreinte = _croyances(monde, titulaire)
    _changer(monde, titulaire, enfant, "actif", "mandat", empreinte)
    _stock(monde, titulaire, creer=True).append(enfant)
    a.setdefault("confies", []).append({"titulaire": titulaire, "agenda": enfant["id"]})
    for x in precedentes:
        if x['etat'] == 'active':
            x['etat'] = 'remplacee'
    for qui in p['qui']:
        attribution = {'sorte': sorte, 'parametres': {**copy.deepcopy(p), 'qui': [qui]},
                       'titulaire': titulaire, 'agenda': enfant['id'],
                       'minute': monde.data['minutes'], 'etat': 'active'}
        if echeance is not None:
            attribution['echeance'] = echeance
        a.setdefault('attributions', []).append(attribution)
    if titulaire != 'joueur':
        _limiter(monde, titulaire, empreinte)
    _actualiser_epreuves(monde, titulaire)
    return copy.deepcopy(enfant)


def _meme_charge(x, sorte, p):
    qui = p['qui']
    return (x['sorte'] == sorte and bool(set(_destinataires(x)) & ({qui} if isinstance(qui, str) else set(qui)))
            and {k: v for k, v in x['parametres'].items() if k != 'qui'}
                == {k: v for k, v in p.items() if k != 'qui'})


def _confies_attendus(monde, a):
    """L'accord entendu reste attendu jusqu'à son échéance, sans lire l'enfant.

    Les anciens accords sans attribution datée gardent leur attente historique.
    """
    suivies = [x for x in a.get('attributions', []) if _meme_charge(x, a['sorte'], a['parametres'])]
    anciennes = {q for j in a.get('jugements', []) if j['issue'] == 'accepte'
                 and _meme_charge(j, a['sorte'], a['parametres']) for q in _destinataires(j)}
    anciennes -= {q for x in suivies for q in x['parametres']['qui']}
    return anciennes | {q for x in suivies if x['etat'] == 'active' and not aide_echue(monde, x)
                         for q in x['parametres']['qui']}


def avertissements(monde, id, parent, sorte, p):
    """Seulement un ancien titulaire cru ici ; pas de détour ni de télépathie."""
    from .deliberation import salle_crue
    from .planification import _etape
    a = _projet(monde, id, parent)
    return [_etape('dire', x['titulaire'], contenu={'retrait_mandat': {
                'parent': parent, 'agenda': x['agenda']}})
            for x in a.get('attributions', [])
            if _meme_charge(x, sorte, p) and _avertissement_du(monde, id, x)
            and (x['etat'] != 'active' or aide_echue(monde, x))
            and salle_crue(monde, id, x['titulaire']) == monde.objets[id]['lieu']]


def _presence_connue(monde, id, autre):
    from .esprits import lire
    c = memoire.fait_brut(monde, id, autre, 'lieu', {})
    return {k: copy.deepcopy(c[k]) for k in ('valeur', 'source', 'salle', 'case') if k in c}


def _avertissement_du(monde, id, x):
    v = x.get('avertissement')
    return (v is None or not v['entendu']
            and v['presence'] != _presence_connue(monde, id, x['titulaire']))


def avertir_retrait(monde, id, autre, retrait, *, entendu):
    """Effet d'une tentative de parole, après contrôle de portée et de voix."""
    a = _projet(monde, id, retrait['parent'])
    refs = [x for x in a.get('attributions', [])
            if x['titulaire'] == autre and x['agenda'] == retrait['agenda']]
    if not refs or not any(_avertissement_du(monde, id, x) for x in refs):
        return False
    if not any(x['etat'] != 'active' or aide_echue(monde, x) for x in refs):
        return False
    for x in refs:
        x['avertissement'] = {'minute': monde.data['minutes'], 'entendu': entendu,
                             'presence': _presence_connue(monde, id, autre)}
    if entendu:
        enfant = _projet(monde, autre, retrait['agenda'])
        if enfant['etat'] in ('actif', 'sommeil'):
            _changer(monde, autre, enfant, 'abandonne', 'retrait entendu', _croyances(monde, autre))
            from .esprits import reconsiderer
            if autre != 'joueur':
                reconsiderer(monde, autre)
        # Le retrait porte sur la charge entière qui avait été acceptée.
        for x in refs:
            if x['etat'] == 'active':
                x['etat'] = 'reprise'
    return True


def charge_retiree(monde, id, autre, retrait):
    """Contenu de l'accord connu, sans lire l'avancement privé du titulaire."""
    a = _projet(monde, id, retrait['parent'])
    refs = [x for x in a.get('attributions', [])
            if x['titulaire'] == autre and x['agenda'] == retrait['agenda']]
    if not refs:
        return None
    return {'sorte': refs[0]['sorte'], 'parametres': {
        **copy.deepcopy(refs[0]['parametres']),
        'qui': sorted({q for x in refs for q in x['parametres']['qui']})}}


def echeance_observee(monde, id, parent, acteur, sorte, parametres):
    """Date issue du plan fermé du mandant ; un devis incertain n'en reçoit pas."""
    from .esprits import lire
    if id == 'joueur':
        return None  # Aucun plan privé prêté au joueur.
    from math import ceil
    p = _condition_mandat(monde, sorte, parametres)
    croyances = memoire.faits_connus(monde, id)
    transmis = [(q, 'lieu') for q in p['qui'] if 'lieu' in croyances.get(q, {})]
    if 'fait' in p:
        transmis.append((p['fait']['sujet'], p['fait']['attribut']))
    duree = []
    devis_observateur(monde, id, parent, acteur, sorte, p, transmis=transmis, duree=duree)
    return (monde.data['minutes'] + ceil(monde.data.get('dixiemes', 0) / 600 + duree[0])
            if duree and duree[0] is not None else None)


def _stock(monde, id, creer=False):
    from .esprits import esprit, lire
    evaluation = getattr(monde, "_evaluation_agendas", None)
    if evaluation is not None and evaluation[0] == id:
        registre = evaluation[1]
        if registre["stock"] is None and creer:
            registre["stock"] = []
        return registre["stock"]
    if id == 'joueur':
        return monde.data.setdefault('agendas_joueur', []) if creer else monde.data.get('agendas_joueur')
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
    registre = {"stock": copy.deepcopy(_stock(monde, id)), "chroniques": [],
                "percus": copy.deepcopy(_percus(monde, id)), "epreuves": []}
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
            ancien[1]["percus"] = registre["percus"]
            ancien[1]["epreuves"].extend(registre["epreuves"])
        else:
            from .esprits import esprit
            from .pnj import _chroniquer
            if registre["stock"] is not None:
                if id == 'joueur':
                    monde.data['agendas_joueur'] = registre['stock']
                else:
                    esprit(monde, id)["agendas"] = registre["stock"]
            if registre["percus"] is not None:
                esprit(monde, id)["mandats_percus"] = registre["percus"]
            for texte in registre["chroniques"]:
                _chroniquer(monde, id, texte, "decision")
            from .relations import eprouver_mandat
            for arguments in registre["epreuves"]:
                eprouver_mandat(monde, *arguments)
    finally:
        monde._evaluation_agendas = ancien


def _croyances(monde, id, *, moyens_seuls=False):
    """Une nouvelle date de regard ne constitue pas un nouveau moyen."""
    from .esprits import lire
    def contenu(x):
        if isinstance(x, dict):
            return {k: contenu(v) for k, v in x.items() if k not in ("minute", "depuis")}
        if isinstance(x, list):
            return [contenu(v) for v in x]
        return x
    # La preuve datée qu'un bien n'est pas fini protège l'adoption des
    # nouvelles ; elle n'ajoute aucun moyen au plan, qui lisait déjà None.
    croyances = contenu({s: {a: c for a, c in d.items()
                            if a != "fin" or c["valeur"] is not None}
                         for s, d in memoire.faits_connus(monde, id).items()})
    if not moyens_seuls and any(a["sorte"] in ("obtenir", "récupérer", "offrir") for a in (_stock(monde, id) or [])):
        from .biens import richesse
        from .spatial import porte_par
        e = lire(monde, id)
        croyances = [croyances, richesse(monde, id), _dette_situation(monde, id),
                     contenu(memoire.reponses_retenues(monde, id)), contenu(e["relations"]), en_cours(monde, id),
                     sorted(o for o in monde.objets if porte_par(monde, o, id))]
        from .caractere import caracteristiques, VALEURS, valeur
        croyances += [caracteristiques(monde, id), {v: valeur(monde, id, v) for v in VALEURS}]
    return hashlib.sha256(json.dumps(croyances,
                                    sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def entrees_recours(monde, id, identifiant):
    """Événements qui rouvrent les moyens d'un projet, hors déplacement propre.

    Les dates de regard et le prix changeant du trajet ne sont pas des
    nouvelles. Les accords, refus, ressources, états crus et échéances le sont.
    Le suffixe exécuté et le contrôle d'admissibilité restent dans l'intention.
    """
    from .esprits import lire
    from .spatial import porte_par
    e = lire(monde, id)
    def contenu(x):
        if isinstance(x, dict):
            return {k: contenu(v) for k, v in x.items()
                    if k not in ('minute', 'depuis', 'source', 'origine')}
        if isinstance(x, list):
            return [contenu(v) for v in x]
        return x
    croyances = contenu(memoire.faits_connus(monde, id))
    # Son propre trajet n'est pas une nouvelle sur les moyens de son but.
    soi = croyances.get(id, {})
    for cle in ('lieu', 'position', 'orientation'):
        soi.pop(cle, None)
    a = _projet(monde, id, identifiant)
    donnees = [croyances, contenu(memoire.reponses_retenues(monde, id)), contenu(e['relations']),
               en_cours(monde, id), e['aides_attendues'],
               [aide_echue(monde, x) for x in e['aides_attendues'].values()],
               sorted(o for o in monde.objets if porte_par(monde, o, id)),
               monde.objets[id].get('profil'),
               [a[k] for k in ('sorte', 'parametres', 'etat')] if a else None]
    return hashlib.sha256(json.dumps(donnees, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


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
    if id == 'joueur':
        for a in _stock(monde, id) or []:
            _reviser_comptes(monde, id, a)
            if a['etat'] in ('actif', 'sommeil') and (
                    _constat_charge(monde, id, a) == 'reussi' or _acheve_par_comptes(monde, id, a)):
                _changer(monde, id, a, 'atteint', 'realisation connue', _croyances(monde, id))
        return
    declarations = depart(monde, id)
    _actualiser_epreuves(monde, id)
    if not declarations and not _stock(monde, id):
        from .biens import richesse
        from .occasion_protection import occasions
        if (_dette_situation(monde, id) <= richesse(monde, id) and not next(_torts_connus(monde, id), None)
                and not next(_biens_soupconnes(monde, id), None)
                and not next(occasions(monde, id), None)):
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
        _reviser_comptes(monde, id, a)
        if a["etat"] == "atteint" and a["raison"] == "compte rendu cru" and not _acheve_par_comptes(monde, id, a):
            _changer(monde, id, a, "actif", "compte rendu dementi", empreinte)
        if a["etat"] not in ("actif", "sommeil"):
            continue
        if a['sorte'] == 'offrir':
            continue
        if a['origine']['type'] == 'contrat':
            engagements = en_cours(monde, id, actifs=True)
            if not any(x['condition'] == a['origine']['condition'] and x['minute'] == a['origine']['minute'] for x in engagements):
                _changer(monde, id, a, 'atteint', 'contrat clos', empreinte)
            continue
        if a.get("echeance", float("inf")) < monde.data["minutes"]:
            _changer(monde, id, a, "abandonne", "echeance", empreinte)
            continue
        if a["sorte"] in ("amener", "informer") and not _destinataires_disponibles(monde, id, a):
            _changer(monde, id, a, "abandonne", "destinataires crus indisponibles", empreinte)
            continue
        if _acheve_par_comptes(monde, id, a):
            _changer(monde, id, a, "atteint", "compte rendu cru", empreinte)
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
            connu = memoire.faits_connus(monde, id, a['parametres']['objet'])
            if connu.get("fin", {}).get("valeur"):
                _changer(monde, id, a, "abandonne", "bien cru " + connu["fin"]["valeur"], empreinte)
            elif connu.get("lieu", {}).get("possession", {}).get("porteur") == id:
                _changer(monde, id, a, "atteint", "bien cru rendu", empreinte)
            elif a['origine'].get('soupcon') and a['origine']['preuve'] not in lire(monde, id)['indices_soupcon']['soupcons']:
                _changer(monde, id, a, 'abandonne', 'soupcon leve', empreinte)
            continue
        if a["sorte"] == "garder":
            raison = _fin_garde(monde, id, a)
            if raison:
                _changer(monde, id, a, "abandonne", raison, empreinte)
            continue
        if a["sorte"] == "protéger":
            from .esprits import lire
            qui = a["parametres"]["qui"]
            etat = memoire.fait_brut(monde, id, qui, 'etat', {}).get("valeur", {})
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
    _actualiser_epreuves(monde, id)


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
        elif a["etat"] == "sommeil" and a["sorte"] in ("informer", "amener", "garder", "protéger", "obtenir", "récupérer", "offrir"):
            if empreinte is None:
                empreinte = _croyances(monde, id)
            if a["croyances"] != empreinte:
                yield a


def _destinataires(a):
    qui = a["parametres"]["qui"]
    return [qui] if isinstance(qui, str) else qui


def _personne_disponible_crue(monde, id, qui):
    """Identité connue, ni mort ni départ crus ; aucune lecture du corps réel."""
    from .esprits import lire
    from .noms import PERSONNES
    etat = memoire.fait_brut(monde, id, qui, 'etat', {}).get("valeur", {})
    return (monde.objets.get(qui, {}).get("type") in PERSONNES
            and not etat.get("mort") and not etat.get("parti"))


def _destinataires_disponibles(monde, id, a):
    return [q for q in _destinataires(a) if _personne_disponible_crue(monde, id, q)]


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


def planifier(monde, id, identifiant, *, cout=None):
    """Choisir le sous-but, puis son exécutant ; les devis restent directs."""
    contexte = getattr(monde, "_evaluation_agendas", None)
    if contexte is None or contexte[0] != id:
        with evaluation(monde, id, publier=False):
            return planifier(monde, id, identifiant, cout=cout)
    mesure = [] if cout is None else cout
    resultat = _prochain_sous_but(monde, id, identifiant, cout=mesure)
    # Tous les chemins directs passent le même contrat, y compris un constat
    # ou une attente. L'absence de coût n'est jamais assimilée à l'impossible.
    if resultat is not None and not mesure:
        from .planification import mesure_recours
        devis = mesure_recours(monde, id, resultat[1])
        if devis is None:
            resultat = None
        else:
            mesure.append(sum(devis))
    if resultat is not None and (len(mesure) != 1 or not math.isfinite(mesure[0])):
        raise ValueError("Recours admissible sans coût fini")
    if cout is not None or getattr(monde, "_contexte_devis", None) is not None:
        return resultat
    a = _projet(monde, id, identifiant)
    if a['etat'] in ('actif', 'sommeil'):
        for x in a.get('attributions', []):
            if x['etat'] in ('remplacee', 'reprise'):
                suite = avertissements(monde, id, identifiant, x['sorte'], x['parametres'])
                if suite:
                    return {'type': 'agenda', 'agenda': identifiant}, suite
    return choisir_mandataire(monde, id, identifiant, resultat, mesure)


def choisir_mandataire(monde, id, identifiant, propre, mesure):
    """Comparer les coûts espérés depuis le seul esprit du mandant.

    La confiance dirigée représente la fiabilité crue. L'autorité estimée
    améliore l'espoir d'accord, jamais le jugement réel du destinataire.
    Les faits nécessaires sont des paroles préparatoires ordinaires.
    """
    from .deliberation import salle_crue, refus_retenu
    from .esprits import lire
    from .relations import axes, chance_demande, autorite_estimee
    from .planification import chercher, _etape
    from .pnj import DUREES
    a = _projet(monde, id, identifiant)
    if a["etat"] not in ("actif", "sommeil") or a["sorte"] not in ("amener", "informer"):
        return propre
    qui = propre[0].get("qui") if propre else None
    if propre is None:
        attribues = _confies_attendus(monde, a)
        cibles = [q for q in _destinataires_disponibles(monde, id, a) if q not in attribues]
        if a["sorte"] == "amener":
            cibles = [q for q in cibles if salle_crue(monde, id, q) != a["parametres"]["lieu"]]
        else:
            from .social import deja_dit
            cibles = [q for q in cibles if not deja_dit(monde, id, q, _noyau(a))]
        qui = min(cibles, default=None)
    if qui is None:
        return propre
    if not _personne_disponible_crue(monde, id, qui):
        return None
    p = copy.deepcopy(a["parametres"])
    p["qui"] = [qui]
    mandat = {"parent": identifiant, "sorte": a["sorte"], "parametres": p}
    # L'acceptation entendue appartient au mandant ; aucune lecture de
    # l'avancement privé de l'enfant, aucun renouvellement automatique.
    if qui in _confies_attendus(monde, a):
        return propre[0], []
    chaine = filiation(monde, id, identifiant)
    if len(chaine) >= 3:
        return propre
    exclus = {r["titulaire"] for r in chaine} | set(p["qui"])
    exclus |= {x['titulaire'] for x in a.get('attributions', []) if _meme_charge(x, a['sorte'], p)}
    croyances = memoire.faits_connus(monde, id)
    transmis = [(qui, "lieu")] if "lieu" in croyances.get(qui, {}) else []
    if a["sorte"] == "informer" and "fait" in p:
        fait = p["fait"]
        cle = (fait["sujet"], fait["attribut"])
        if cle not in transmis:
            transmis.append(cle)
    paroles = []
    for sujet, attribut in transmis:
        c = croyances.get(sujet, {}).get(attribut)
        if c is None:
            return propre
        paroles.append({"sujet": sujet, "attribut": attribut, "valeur": copy.deepcopy(c["valeur"])})
    if a["sorte"] == "informer" and "avis" in p:
        from .social import avis_exprime
        avis = p["avis"]
        paroles.append({"avis": avis_exprime(monde, id, avis["objet"], avis["valeur"])})
    if propre is not None and (not mesure or not math.isfinite(mesure[0])):
        raise ValueError("Recours admissible sans devis")
    choix = [(mesure[0] if propre is not None else float("inf"), id, propre)]
    for acteur in sorted(croyances):
        if acteur in exclus or acteur == "joueur" or not _personne_disponible_crue(monde, id, acteur):
            continue
        if refus_retenu(monde, id, acteur, ("confier",), qui, mandat=mandat):
            continue
        salle = salle_crue(monde, id, acteur)
        if salle is None:
            continue
        devis = devis_observateur(monde, id, identifiant, acteur, a["sorte"], p, transmis=transmis)
        if devis is None:
            continue
        route = chercher(monde, id, lambda v, e: e.salle == salle,
                         nom="mandataire:" + acteur, memo=["mandataire", acteur, salle],
                         emplois=(), endurer=poids(monde, id, a))
        if route is None:
            continue
        autorite = autorite_estimee(monde, id, acteur, salle, a["sorte"])
        chance = min(.95, chance_demande(monde, id, acteur) + autorite["bonus"] / 20)
        fiabilite = max(.1, axes(monde, id, acteur)["confiance"] / 100)
        cout = route[0] + (len(paroles) * DUREES["dire"] + DUREES["confier"]) / 600
        cout += devis[0] / (chance * fiabilite)
        suite = route[1] + [_etape("dire", acteur, contenu=c) for c in paroles]
        suite.append(_etape("confier", acteur, contenu={"mandat": mandat, "objet": qui}))
        but = propre[0] if propre else {"type": "agenda", "agenda": identifiant, "qui": qui}
        choix.append((cout, acteur, (but, suite)))
    retenu = min(choix, key=lambda x: (x[0], x[1]))
    # Conserver le moyen déjà entrepris tant que son surcoût relatif reste
    # dans la marge de ténacité commune. Ni date ni durée d'attente ajoutée.
    from .deliberation import marge_engagement
    intention = lire(monde, id)['intention']
    if intention and intention['but'].get('agenda') == identifiant:
        ancien = next((g['cible'] for g in reversed(intention['plan'])
                       if 'mandat' in g.get('contenu', {})
                       and g['contenu']['mandat'] == mandat), id)
        tenu = next((x for x in choix if x[1] == ancien and x[2] is not None), None)
        if tenu and tenu[0] <= retenu[0] * (1 + marge_engagement(monde, id) / 100):
            retenu = tenu
    if retenu[1] != id:
        _changer(monde, id, a, "actif", "mandataire estime", _croyances(monde, id))
        _limiter(monde, id, _croyances(monde, id))
        if a["etat"] != "actif":
            return None
    if retenu[2] is None:
        return None
    but, suite = retenu[2]
    return but, avertissements(monde, id, identifiant, a['sorte'], p) + suite


def _prochain_sous_but(monde, id, identifiant, *, cout=None):
    """Un seul prochain sous-but recherché ; aucun plan conservé dans l'agenda."""
    from .esprits import lire
    from .deliberation import salle_crue
    from .planification import chercher, _etape
    from .social import deja_dit, avis_exprime
    a = next(a for a in _stock(monde, id) if a["id"] == identifiant)
    if a["etat"] not in ("actif", "sommeil"):
        return None
    if a["sorte"] in ("amener", "informer"):
        disponibles = _destinataires_disponibles(monde, id, a)
        if not disponibles:
            _changer(monde, id, a, "sommeil", "destinataires crus indisponibles", _croyances(monde, id))
            return None
        confies = _confies_attendus(monde, a)
        restants = [q for q in disponibles if q not in confies]
        if not restants:
            return {"type": "agenda", "agenda": identifiant}, []
    empreinte = _croyances(monde, id)
    if a['sorte'] == 'offrir':
        from .occasion_protection import peur_crue, fonds_crus
        from .echanges import offre_sensee
        from .pnj_propositions import offre_refusee
        from .planification import rejoindre, _etape, RESTER
        p = a['parametres']
        qui = p['qui']
        c = p['contrepartie']['condition']
        # La date du devis n'est pas un motif de redémarchage. Les termes sont
        # remis à jour seulement après le contrôle du refus commun.
        if (not peur_crue(monde, id, qui) or fonds_crus(monde, id, qui) < p['demande']['montant']
                or offre_refusee(monde, id, qui, qui, p['contrepartie'])):
            _changer(monde, id, a, 'sommeil', 'occasion indisponible ou refusee', empreinte)
            return None
        c['echeance'] = monde.data['minutes'] + RESTER
        if not offre_sensee(monde, id, qui, p['demande'], p['contrepartie']):
            _changer(monde, id, a, 'sommeil', 'offre sans interet', empreinte)
            return None
        contact = rejoindre(monde, id, qui)
        if contact is None:
            return None
        suite, trouve = contact
        if trouve:
            suite.append(_etape('proposer', qui, contenu={k: copy.deepcopy(p[k]) for k in ('demande', 'contrepartie')}))
        return {'type': 'agenda', 'agenda': identifiant}, suite
    if a["sorte"] == "récupérer":
        if a["etat"] == "sommeil" and a["croyances"] == empreinte:
            return None
        objet = a["parametres"]["objet"]
        if a['origine'].get('soupcon'):
            # Question et recherche de l'interlocuteur sont des moyens communs.
            # Aucune possession inventée ; un silence ne prouve pas l'innocence.
            from .deliberation import refus_retenu
            from .planification import rejoindre
            qui = a['parametres']['qui']
            if not refus_retenu(monde, id, qui, ('enqueter_lieu',), objet=objet):
                contact = rejoindre(monde, id, qui)
                if contact is not None:
                    suite, trouve = contact
                    if trouve:
                        suite = suite + [_etape('demander', qui, contenu={'localisation': objet})]
                    if suite:
                        _changer(monde, id, a, 'actif', 'enquete sur soupcon', empreinte)
                        _limiter(monde, id, empreinte)
                        return ({'type': 'agenda', 'agenda': identifiant, 'objet': objet}, suite) if a['etat'] == 'actif' else None
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
        if cout is not None:
            cout.append(trouve[0])
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
            monde, id, a["parametres"]["pieces"], poids(monde, id, a), cout=cout)
        if resultat is None:
            _changer(monde, id, a, "sommeil", "sans plan admissible au cout", empreinte)
            return None
        _changer(monde, id, a, "actif", "plan admissible", empreinte)
        _limiter(monde, id, empreinte)
        return ({"type": "agenda", "agenda": identifiant, "pieces": a["parametres"]["pieces"]}, resultat) if a["etat"] == "actif" else None
    if a["sorte"] == "amener":
        return _amener(monde, id, a, empreinte, cout=cout, cibles=restants)
    if a["sorte"] == "protéger":
        from .defense import interposition
        poste = interposition(monde, id)
        if poste is not None and poste[0]["objet"] == a["parametres"]["qui"]:
            _changer(monde, id, a, "actif", "interposition", empreinte)
            _limiter(monde, id, empreinte)
            return poste if a["etat"] == "actif" else None
        from .planification import proximite
        trouve = proximite(monde, id, a['parametres']['qui'], portee='voix', endurer=poids(monde, id, a))
        if trouve is None:
            _changer(monde, id, a, 'sommeil', 'sans plan admissible au cout', empreinte)
            return None
        _changer(monde, id, a, 'actif', 'proximite vocale', empreinte)
        _limiter(monde, id, empreinte)
        if cout is not None:
            cout.append(trouve[0])
        return ({'type': 'agenda', 'agenda': identifiant, 'qui': a['parametres']['qui']}, trouve[1]) if a['etat'] == 'actif' else None
    if a["sorte"] == "garder":
        from .planification import garder
        from .defense import interposition
        c = a["parametres"]
        poste = interposition(monde, id)
        if poste is not None and poste[0]["objet"] == c.get("objet", c.get("lieu")):
            if a["etat"] == "sommeil":
                _changer(monde, id, a, "actif", "plan apres croyance nouvelle", empreinte)
                _limiter(monde, id, empreinte)
                if a["etat"] != "actif":
                    return None
            return poste
        salle = salle_crue(monde, id, c["objet"]) if "objet" in c else c["lieu"]
        etapes = garder(monde, id, salle, cout=cout) if salle in monde.data["salles"] else None
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
        cru = memoire.fait_brut(monde, id, noyau['sujet'], noyau['attribut'])
        connu = cru is not None and cru["valeur"] == noyau["valeur"]
        contenu = {k: noyau[k] for k in ("sujet", "attribut", "valeur")}
    if not connu:
        _changer(monde, id, a, "sommeil", "contenu non cru", empreinte)
        return None
    cibles = [qui for qui in restants if not deja_dit(monde, id, qui, noyau)]
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
    if cout is not None:
        from .pnj import DUREES
        cout.append(trouve[0] + DUREES["dire"] / 600)
    return {"type": "agenda", "agenda": identifiant, "qui": qui}, trouve[1] + [_etape("dire", qui, contenu=contenu)]


def _amener(monde, id, a, empreinte, *, cout=None, cibles=None):
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
    cibles = [q for q in (_destinataires(a) if cibles is None else cibles)
              if salle_crue(monde, id, q) != destination]
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
        if cout is not None:
            cout.append(trouve[0])
        return {"type": "agenda", "agenda": a["id"], "qui": qui}, trouve[1]
    if attendus:
        # Attendre un engagement accepté est un recours : laisser la routine
        # reprendre ici produirait des navettes vers le rendez-vous à chaque choix.
        if a["etat"] == "sommeil":
            _changer(monde, id, a, "actif", "plan apres croyance nouvelle", empreinte)
            _limiter(monde, id, empreinte)
            if a["etat"] != "actif":
                return None
        aides = [lire(monde, id)["aides_attendues"][q] for q in attendus]
        # L'échéance ouvre un constat ; elle n'annule pas la parole et
        # n'autorise pas une deuxième délégation identique au même acteur.
        depuis = max(x['echeance'] + 1 if aide_echue(monde, x) else x['minute'] for x in aides)
        # Une inspection achevée sans arrivée visible ne justifie pas de
        # recommencer sans fin ; la perception ordinaire continue pendant l'attente.
        suite = ([] if lire(monde, id)["visites"].get(destination, -1) >= depuis
                 else [_etape("inspecter", lieu=destination)])
        return {"type": "agenda", "agenda": a["id"], "qui": attendus[0]}, suite
    _changer(monde, id, a, "sommeil", raisons[0] if raisons else "arrivee attendue", empreinte)
    return None


def aide_echue(monde, aide):
    """Aucune échéance reconstruite pour une ancienne parole."""
    return 'echeance' in aide and monde.data['minutes'] > aide['echeance']


def clore_aides_constatees(monde, id):
    """Une réalisation apprise clôt la parole, même si le résultat se perd ensuite.

    Publication au début du choix, jamais pendant une lecture de candidat.
    Une ancienne preuve antérieure à l'accord ne tient pas une nouvelle parole.
    """
    from .esprits import lire
    from .deliberation import profil, satisfaite
    e = lire(monde, id)
    for objet, aide in list(e['aides_attendues'].items()):
        c = aide['condition']
        attribut = 'etat' if 'allume' in c or 'servir' in c else 'lieu' if any(
            k in c for k in ('lieu', 'rendre', 'remettre')) else 'verrouillee'
        preuve = memoire.fait_brut(monde, id, c.get('servir', objet), attribut)
        if not preuve or preuve['minute'] <= aide['minute']:
            continue
        destinataire = c.get('remettre', c.get('rendre'))
        faite = (preuve.get('possession', {}).get('porteur') == destinataire
                 if destinataire else satisfaite(monde, id, c))
        if faite:
            del e['aides_attendues'][objet]
    for pulsion in profil(monde, id)['pulsions']:
        if pulsion.get('delegue_a') and satisfaite(monde, id, pulsion['condition']):
            # Le mandat initial est achevé ; la charge propre reste au mandant.
            del pulsion['delegue_a']
            pulsion.pop('echeance', None)


def suivis_delegations(monde, id):
    """Contrôles dus d'après les accords connus et les constats du mandant.

    Une visite après l'échéance clôt ce contrôle : le seul écoulement du temps
    ne justifie jamais de recommencer une ronde identique.
    """
    from .esprits import lire
    from .deliberation import profil, salle_crue, satisfaite, se_mefie
    e = lire(monde, id)
    aides = list(e['aides_attendues'].values())
    aides += [dict(qui=p['delegue_a'], condition=p['condition'], echeance=p['echeance'])
              for p in profil(monde, id)['pulsions'] if p.get('delegue_a') and 'echeance' in p]
    for aide in aides:
        if (not aide_echue(monde, aide) or satisfaite(monde, id, aide['condition'])
                or se_mefie(monde, id, aide['qui'])):
            continue
        c = aide['condition']
        lieu = c.get('lieu') or salle_crue(monde, id, c['objet']) or salle_crue(monde, id, aide['qui'])
        if lieu in monde.data['salles'] and e['visites'].get(lieu, -1) <= aide['echeance']:
            yield lieu


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


def moyens_promis(monde, id, condition=None, pour=None):
    """Charges matérielles des paroles actives, sans nouveau registre persistant.

    Une remise réserve le bien entier ; un service réserve les parts consommées
    par son devis cru. La parole que l'on revalide n'est comptée qu'une fois.
    La restitution d'un prêt acquis pour ce transport ne le réserve pas une
    seconde fois. Les outils réutilisables ne sont pas consommés par leur emploi.
    """
    from collections import Counter
    from .planification import devis_pulsion
    charges, entiers = Counter(), set()
    engagements = en_cours(monde, id, actifs=True)
    propre = next((x for x in engagements if x['condition'] == condition and x['pour'] == pour), None)
    # Le prêt acquis pour un transport ajoute une restitution, pas un second
    # emploi du bien. Seul le transport revalidé en bénéficie : sa réservation
    # reste opposable aux autres offres, y compris après acquisition du prêt.
    # prendre ajoute en fin de registre : une restitution antérieure au
    # transport est une charge préexistante, pas un prêt acquis pour lui.
    transport = None
    for x in engagements:
        c = x['condition']
        if x is propre:
            if any(k in c for k in ('remettre', 'lieu')):
                transport = c.get('objet')
            continue
        if transport is not None and c.get('objet') == transport and 'rendre' in c:
            continue
        o = c.get('objet')
        if any(k in c for k in ('remettre', 'rendre', 'lieu')) and o != id:
            entiers.add(o)
        elif 'servir' in c:
            charges[o] += 1
        elif x.get('objet'):
            charges[x['objet']] += 1
        elif monde.objets.get(id, {}).get('profil'):
            devis = devis_pulsion(monde, id, c, x['pour'])
            if devis:
                for g in devis[1]:
                    if g['operation'] in ('servir', 'manger'):
                        charges[g['cible']] += 1
                    elif g['operation'] == 'alimenter':
                        charges[g['outil']] += 1
    return charges, entiers


def disponibilite_promise(monde, id, objet, *, part=False, condition=None, pour=None):
    """Disponibilité crue après les paroles, jamais le stock distant caché.

    À portée, le propriétaire compte ses biens (contrat de siens_a_portee).
    À distance, « disponible » ne prouve qu'une part, pas un nombre inconnu.
    """
    from .deliberation import _disponible_cru, parts
    from .echanges import siens_a_portee
    from .spatial import porte_par
    charges, entiers = moyens_promis(monde, id, condition, pour)
    if objet in entiers or not part and charges[objet]:
        return False
    if not charges[objet]:
        return True
    copie = monde.copier()
    siens = (siens_a_portee(copie, id) if id != 'joueur' else
             [o for o in copie.objets if porte_par(copie, o, id)])
    n = parts(copie.objets[objet]) if objet in siens else int(_disponible_cru(monde, id, objet))
    return n > charges[objet]


def monde_devis_libre(monde, id, condition, pour):
    """Projection jetable des moyens non promis, commune à tous les devis.

    Les réservations ne changent ni les objets réels ni les croyances sauvées.
    Retirer un moyen épuisé laisse la recherche choisir un autre moyen cru.
    """
    from .deliberation import _disponible_cru, parts
    from .echanges import siens_a_portee
    from .esprits import esprit
    from .spatial import porte_par
    charges, entiers = moyens_promis(monde, id, condition, pour)
    if not charges and not entiers:
        return monde
    copie = monde.copier()
    siens = siens_a_portee(copie, id)
    for o in sorted(set(charges) | entiers):
        if o not in copie.objets:
            continue
        n = parts(copie.objets[o]) if o in siens else int(_disponible_cru(monde, id, o))
        if o not in entiers and n > charges[o]:
            continue
        # Sans localisation utilisable, le bien n'est plus un moyen du devis.
        # Le lieu physique de cette copie ne sert qu'à retirer le porté.
        if porte_par(copie, o, id):
            copie.objets[o].update(lieu=copie.objets[id]['lieu'],
                                   position=copy.deepcopy(copie.objets[id].get('position')),
                                   position_salle=copie.objets[id]['lieu'])
        memoire.retirer_moyen_projete(copie, id, o)
    return copie


def reference_temporelle(engagement):
    """Référence acceptée, en dixièmes absolus, ou None ; jamais une date déduite.

    L'identité est celle de l'obligation datée ; version 1 désigne ses termes initiaux.
    Ni la minute renouvelable, ni le devis, ni une fin de protection ne la modifient.
    La copie retournée n'autorise aucune renégociation implicite.
    """
    return copy.deepcopy(engagement.get('reference_temporelle'))


def issues_temporelles(monde):
    """Histoire mécanique des accords clos, distincte de leur connaissance."""
    return copy.deepcopy(monde.data.get('issues_obligations', []))


def accord_initial(proposant, auditeur, demande, contrepartie):
    return copy.deepcopy(dict(proposant=proposant, auditeur=auditeur,
                              demande=demande, contrepartie=contrepartie))


def accord_deja_conclu(monde, accord):
    """Une soumission identique reste acquittée même après livraison ou clôture."""
    return any(x.get('accord_initial') == accord for _, x in _obligations_datees(monde)) or any(
        i['engagement'].get('accord_initial') == accord for i in monde.data.get('issues_obligations', []))


def prochaine_expiration(monde, defaut):
    return min((reference_temporelle(x)['limite'] + 1
                for _, x in _obligations_datees(monde)), default=defaut)


def _obligations_datees(monde):
    if not monde.data.get('sequence_obligations'):
        return []
    stocks = [('joueur', monde.data.get('promesses_joueur', []))]
    stocks.extend((id, e['engagements']) for id, e in monde.data.get('esprits', {}).items())
    return [(id, x) for id, stock in stocks for x in stock if reference_temporelle(x)]


def _clore_datee(monde, id, engagement, realisation=None, *, connue=False):
    from .temps import instant
    from .biens import rembourser
    from .esprits import esprit
    r = reference_temporelle(engagement)
    # La clôture est un événement unique, même si une ancienne copie circule encore.
    if any(reference_temporelle(x['engagement']) == r for x in issues_temporelles(monde)):
        return
    a_temps = realisation is not None and realisation <= r['limite']
    monde.data.setdefault('issues_obligations', []).append({
        'titulaire': id, 'engagement': copy.deepcopy(engagement),
        'realisation': realisation, 'verdict': 'tenue_a_temps' if a_temps else 'en_retard',
        'cloture': instant(monde), 'constatee': connue})
    retirer_proposition(monde, id, engagement)
    if a_temps and id != 'joueur':
        from .biens import retenir_service
        retenir_service(monde, id, engagement)
    if not a_temps and engagement.get('paye'):
        p = engagement['paye']
        # Le compte réel n'apprend rien à un créancier distant.
        rembourser(monde, id, engagement['pour'], p['prix'], p['objet'], p['quoi'], informer=False)
    if id != 'joueur':
        e = esprit(monde, id)
        intention = e['intention']
        # Le contrat adopté donne la condition exacte, y compris pour un préparatif.
        demande = (e.get('contrat_intention') or {}).get('demande') or {}
        but = {k: v for k, v in intention['but'].items() if k != 'type'} if intention else {}
        if (intention and (demande.get('condition') == engagement['condition']
                           or intention['motif'] == 'engagement' and but == engagement['condition'])
                and not any(x['condition'] == engagement['condition'] for x in en_cours(monde, id))):
            e['intention'] = None
            e['eveil'] = instant(monde)


def expirer_obligations(monde):
    """T est inclus : la clôture sans réalisation arrive à T+1 dixième."""
    from .temps import instant
    for id, x in list(_obligations_datees(monde)):
        if instant(monde) > reference_temporelle(x)['limite']:
            _clore_datee(monde, id, x)


def etat_realisations(monde):
    """Photographie avant un effet réel ; une perception ne passe jamais ici."""
    etats = {}
    for id, x in _obligations_datees(monde):
        etats[('obligation', reference_temporelle(x)['id'])] = _etat_realisation(monde, id, x['condition'])
    return etats


def _etat_realisation(monde, id, c):
    from .spatial import porte_par
    from .perception import faible, allumee, fin_objet
    o = monde.objets[c['objet']]
    if 'lieu' in c:
        lieu, vus = o['lieu'], set()
        while lieu in monde.objets and lieu not in vus:
            vus.add(lieu)
            lieu = monde.objets[lieu]['lieu']
        salle = monde.joueur['salle'] if lieu == 'joueur' else lieu
        return {'lieu': None if porte_par(monde, c['objet'], id) else salle}
    if 'allume' in c:
        return {'allume': allumee(o) and not faible(o), 'combustible': o.get('combustible', 0)}
    if 'verrouillee' in c:
        return {'verrouillee': o.get('verrouillee') is True and not o.get('ouverte')
                and fin_objet(o) != 'detruit'}
    return {}


def constater_realisations(monde, avant, auteur='joueur'):
    from .temps import instant
    for id, x in list(_obligations_datees(monde)):
        c = x['condition']
        # Remise et service ont leur événement propre : un simple lieu ne les prouve pas.
        if 'remettre' in c or 'servir' in c:
            continue
        o = _etat_realisation(monde, id, c)
        cle = ('obligation', reference_temporelle(x)['id'])
        if cle not in avant:
            continue  # Une obligation née dans l'effet n'hérite pas de son état antérieur.
        ancien = avant[cle]
        cles = set(c) - {'objet'}
        change = (o.get('allume') != ancien.get('allume') or
                  o.get('combustible', 0) > (ancien.get('combustible') or 0)) if 'allume' in c else any(
                      o.get(k) != ancien.get(k) for k in cles)
        if change and all(o.get(k) == v for k, v in c.items() if k != 'objet'):
            connue = id == auteur and id != 'joueur'
            _clore_datee(monde, id, x, instant(monde), connue=connue)
            if connue:
                from .esprits import memoriser
                memoriser(monde, id, {'type': 'engagement_tenu', 'pour': x['pour'], 'condition': c})


def _constater_issues(monde, id, lignes=None):
    """Publier seulement avec le constat ou la parole réellement reçue."""
    from .echanges import tenu, phrase_condition
    from .esprits import memoriser, lire
    from .voix import nom_pour_joueur
    for issue in monde.data.get('issues_obligations', []):
        if issue['titulaire'] != id or issue['constatee']:
            continue
        x = issue['engagement']
        reussie = issue['verdict'] == 'tenue_a_temps'
        observateur = x['pour'] if id == 'joueur' else id
        if reussie:
            c = x['condition']
            if not tenu(monde, observateur, c, x['minute']):
                continue
        elif id == 'joueur':
            # Pouvoir parler n'est pas une preuve de manquement. Le bénéficiaire
            # doit avoir reçu un constat négatif après la limite ; le silence ne suffit pas.
            from .deliberation import satisfaite
            c = x['condition']
            attribut = 'etat' if 'allume' in c else 'lieu' if 'lieu' in c else 'verrouillee'
            preuve = memoire.fait_brut(monde, observateur, c['objet'], attribut)
            if ('remettre' in c or 'servir' in c or not preuve
                    or preuve['source'] not in ('vu', 'essai')
                    or preuve['minute'] * 600 <= reference_temporelle(x)['limite']
                    or satisfaite(monde, observateur, c)):
                continue
        issue['constatee'] = True
        if id != 'joueur':
            memoriser(monde, id, {'type': 'engagement_tenu' if reussie else 'engagement_abandonne',
                                  'pour': x['pour'], 'condition': x['condition']})
        else:
            memoriser(monde, x['pour'], {'type': 'engagement_tenu' if reussie else 'engagement_abandonne',
                                        'de': id, 'condition': x['condition']})
            texte = ('Tu as tenu ta promesse envers ' if reussie else 'Tu as abandonné ta promesse envers ')
            texte += nom_pour_joueur(monde, x['pour']) + ' : ' + phrase_condition(monde, x['condition']) + '.'
            monde.data.setdefault('journal_promesses', []).append(texte)
            lignes.append(texte)


def _verifier_reference_temporelle(monde, engagement, chemin, sequence, titulaire=None):
    from .monde import ErreurMonde
    from .temps import instant

    def refuser(champ, recu, accepte):
        raise ErreurMonde('Référence temporelle d’obligation invalide.',
                          f'{chemin}.{champ} : reçu {recu!r} ; accepté : {accepte}.')

    r = reference_temporelle(engagement)
    if 'reference_temporelle' not in engagement:
        if 'accord_initial' in engagement:
            refuser('accord_initial', engagement['accord_initial'], 'une obligation avec référence temporelle')
        return None
    champs = {'id', 'version', 'creation', 'limite'}
    if not isinstance(r, dict):
        refuser('reference_temporelle', r, f'un dictionnaire de champs {sorted(champs)}')
    if set(r) != champs:
        refuser('reference_temporelle', sorted(r), f'exactement {sorted(champs)}')
    chemin += '.reference_temporelle'
    if type(r['id']) is not int:
        refuser('id', r['id'], 'un entier')
    if not 0 < r['id'] <= sequence:
        refuser('id', r['id'], f'un identifiant entre 1 et sequence_obligations={sequence}')
    if type(r['version']) is not int or r['version'] != 1:
        refuser('version', r['version'], '1 (termes initiaux ; révision non portée)')
    if type(r['creation']) is not int:
        refuser('creation', r['creation'], 'un entier en dixièmes de seconde')
    if r['creation'] < 0:
        refuser('creation', r['creation'], 'un instant positif ou nul')
    if r['creation'] > instant(monde):
        refuser('creation', r['creation'], f'un instant <= {instant(monde)}')
    if type(r['limite']) is not int:
        refuser('limite', r['limite'], 'un entier en dixièmes de seconde')
    if r['limite'] < 0:
        refuser('limite', r['limite'], 'un instant positif ou nul')
    if r['limite'] < r['creation']:
        refuser('limite', r['limite'], f'un instant >= creation={r["creation"]}')
    chemin = chemin.removesuffix('.reference_temporelle')
    from .deliberation import condition_valide
    c = engagement.get('condition')
    if (not condition_valide(monde, c) or set(c) not in (
            {'objet', 'allume'}, {'objet', 'verrouillee'}, {'objet', 'lieu'},
            {'objet', 'remettre'}, {'objet', 'servir'})):
        refuser('condition', c, 'une prestation ponctuelle : allume, verrouillee, lieu, remettre ou servir')
    if 'accord_initial' in engagement:
        from .propositions import erreur_terme
        a = engagement['accord_initial']
        if not isinstance(a, dict) or set(a) != {'proposant', 'auditeur', 'demande', 'contrepartie'}:
            refuser('accord_initial', a, '{proposant, auditeur, demande, contrepartie}')
        for cle in ('proposant', 'auditeur'):
            if not isinstance(a[cle], str) or a[cle] != 'joueur' and a[cle] not in monde.data.get('esprits', {}):
                refuser('accord_initial.' + cle, a[cle], 'joueur ou un identifiant d’esprit')
        for cle in ('demande', 'contrepartie'):
            erreur = erreur_terme(a[cle], cle == 'contrepartie')
            if erreur:
                suffixe, recu, accepte = erreur
                refuser('accord_initial.' + cle + suffixe, recu, accepte)
        service, paiement = ((a['demande'], a['contrepartie']) if 'limite' in a['demande']
                             else (a['contrepartie'], a['demande']))
        if service.get('limite') != r['limite']:
            refuser('accord_initial.limite', service.get('limite'), r['limite'])
        contractant, beneficiaire = ((a['auditeur'], a['proposant']) if 'limite' in a['demande']
                                    else (a['proposant'], a['auditeur']))
        if titulaire is not None and contractant != titulaire:
            refuser('accord_initial.contractant', contractant, titulaire)
        if engagement['pour'] != beneficiaire:
            refuser('accord_initial.beneficiaire', beneficiaire, engagement['pour'])
        if paiement['type'] != 'pieces':
            refuser('accord_initial.paiement', paiement, 'pieces payées maintenant')
        attendu = (service['condition'] if service['type'] == 'tache' else
                   {'objet': c['objet'], 'remettre': engagement['pour']})
        if c != attendu or service['type'] == 'part' and engagement.get('lot') != service['objet']:
            refuser('accord_initial.prestation', service, 'les termes de cette obligation')
        p = engagement.get('paye')
        if not isinstance(p, dict) or set(p) != {'objet', 'prix', 'quoi'}:
            refuser('paye', p, '{objet, prix, quoi}')
        if type(p['prix']) is not int:
            refuser('paye.prix', p['prix'], 'un entier strictement positif')
        if p['prix'] != paiement['montant']:
            refuser('accord_initial.montant', paiement['montant'], p['prix'])
        if p['objet'] != c['objet']:
            refuser('paye.objet', p['objet'], c['objet'])
        quoi = 'objet' if service['type'] == 'part' else 'tache'
        if p['quoi'] != quoi:
            refuser('paye.quoi', p['quoi'], quoi)
    return r


def verifier_references_temporelles(monde):
    """Validation commune de recharge, joueur et PNJ ; aucune migration de date.

    La séquence ne recule pas quand un engagement est retiré, même provisoire.
    Elle n'existe que si une première référence a été explicitement créée.
    """
    from .monde import ErreurMonde
    sequence = monde.data.get('sequence_obligations', 0)
    if type(sequence) is not int or sequence < 0:
        raise ErreurMonde('Compteur d’obligations invalide.',
                          f'sequence_obligations : reçu {sequence!r} ; accepté : un entier >= 0.')
    stocks = [('joueur', monde.data.get('promesses_joueur', []))]
    stocks.extend((id, e['engagements']) for id, e in monde.data.get('esprits', {}).items())
    from .temps import instant
    issues = monde.data.get('issues_obligations', [])
    if not isinstance(issues, list):
        raise ErreurMonde('Historique temporel invalide.',
                          f'issues_obligations : reçu {issues!r} ; accepté : une liste.')
    for rang, issue in enumerate(issues):
        chemin = f'issues_obligations[{rang}]'
        def refuser(champ, recu, accepte):
            raise ErreurMonde('Issue temporelle invalide.',
                              f'{chemin}.{champ} : reçu {recu!r} ; accepté : {accepte}.')
        champs = {'titulaire', 'engagement', 'realisation', 'verdict', 'cloture', 'constatee'}
        if not isinstance(issue, dict) or set(issue) != champs:
            refuser('forme', issue, f'exactement les champs {sorted(champs)}')
        id, x = issue['titulaire'], issue['engagement']
        if not isinstance(id, str) or id != 'joueur' and id not in monde.data.get('esprits', {}):
            refuser('titulaire', id, 'joueur ou un identifiant d’esprit')
        if not isinstance(x, dict) or reference_temporelle(x) is None:
            refuser('engagement', x, 'une obligation avec reference_temporelle')
        r = _verifier_reference_temporelle(monde, x, chemin + '.engagement', sequence, id)
        cloture, fait = issue['cloture'], issue['realisation']
        if type(cloture) is not int or not r['creation'] <= cloture <= instant(monde):
            refuser('cloture', cloture, f'un entier entre {r["creation"]} et {instant(monde)}')
        if fait is not None and (type(fait) is not int or not r['creation'] <= fait <= cloture):
            refuser('realisation', fait, f'None ou un entier entre {r["creation"]} et {cloture}')
        verdict = 'tenue_a_temps' if fait is not None and fait <= r['limite'] else 'en_retard'
        if issue['verdict'] != verdict:
            refuser('verdict', issue['verdict'], verdict)
        if verdict == 'en_retard' and cloture <= r['limite']:
            refuser('cloture', cloture, f'un instant > limite={r["limite"]}')
        if type(issue['constatee']) is not bool:
            refuser('constatee', issue['constatee'], 'un booléen')
        stocks.append((chemin, [x]))
    identites, accords = set(), []
    for id, stock in stocks:
        for rang, engagement in enumerate(stock):
            chemin = f'obligations.{id}[{rang}]'
            r = _verifier_reference_temporelle(monde, engagement, chemin, sequence,
                                              id if not id.startswith('issues_obligations[') else None)
            if r is None:
                continue
            if r['id'] in identites:
                raise ErreurMonde('Identité d’obligation dupliquée.',
                                  f'{chemin}.reference_temporelle.id : reçu {r["id"]!r} ; '
                                  'accepté : un identifiant distinct de toute autre obligation.')
            identites.add(r['id'])
            if 'accord_initial' in engagement:
                accord = engagement['accord_initial']
                if accord in accords:
                    raise ErreurMonde('Accord initial dupliqué.',
                                      f'{chemin}.accord_initial : reçu {accord!r} ; accepté : un accord distinct.')
                accords.append(accord)


def prendre(monde, id, engagement, *, limite=None, accord=None):
    """Inscrire aussi la proposition provisoire, retirée si le devis ou le jet refuse.

    E4 conserve les termes initiaux pour dédupliquer leur soumission après clôture.
    Aucune métadonnée ajoutée aux engagements ordinaires ou aux anciennes parties.
    """
    from .esprits import esprit
    from .monde import ErreurMonde
    from .temps import instant
    engagement = copy.deepcopy(engagement)
    if accord is not None:
        if limite is None:
            raise ErreurMonde('Cet accord doit porter une limite.',
                              f'limite : reçu {limite!r} ; accepté : un entier >= 0 en dixièmes absolus.')
        engagement['accord_initial'] = copy.deepcopy(accord)
    if 'reference_temporelle' in engagement:
        raise ErreurMonde('Cette référence d’obligation ne peut pas être réutilisée.',
                          f'reference_temporelle : reçu {engagement["reference_temporelle"]!r} ; '
                          'accepté : champ absent ; prendre alloue identité et version.')
    if limite is not None:
        verifier_references_temporelles(monde)
        sequence = monde.data.get('sequence_obligations', 0) + 1
        engagement['reference_temporelle'] = {
            'id': sequence, 'version': 1, 'creation': instant(monde), 'limite': limite}
        _verifier_reference_temporelle(monde, engagement, f'obligations.{id}', sequence, id)
        monde.data['sequence_obligations'] = sequence
    stock = monde.data.setdefault("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    stock.append(engagement)


def admettre_contrat(monde, id, engagement):
    """Un service durable accepté utilise la responsabilité commune des agendas."""
    c = engagement['condition']
    if not c.get('proteger'):
        return
    if depart(monde, id) and _stock(monde, id) is None:
        actualiser(monde, id)
    stock = _stock(monde, id, creer=True)
    n = 1
    while any(a['id'] == f'a{n}' for a in stock):
        n += 1
    a = {'id': f'a{n}', 'sorte': 'protéger', 'parametres': {'qui': c['objet']},
         'echeance': c['echeance'], 'maniere': {'sans_violence': False},
         'origine': {'type': 'contrat', 'de': engagement['pour'], 'minute': engagement['minute'],
                     'condition': copy.deepcopy(c)}}
    _changer(monde, id, a, 'actif', 'tache payee', _croyances(monde, id))
    stock.append(a)
    _limiter(monde, id, _croyances(monde, id))


def commencer_service(monde, id, cible):
    from .esprits import esprit
    for x in esprit(monde, id)['engagements']:
        if x['condition'].get('proteger') and x['condition']['objet'] == cible and not x.get('annule'):
            x.setdefault('commence', monde.data['minutes'])


def conclure_offre(monde, id, identifiant, issue):
    a = _projet(monde, id, identifiant)
    if a and a['sorte'] == 'offrir' and issue in ('accepte', 'attente'):
        _changer(monde, id, a, 'atteint', 'offre ' + issue, _croyances(monde, id))


def retirer_proposition(monde, id, engagement):
    from .esprits import esprit
    stock = monde.data.get("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    stock.remove(engagement)


def renouveler(monde, id, engagement, minute):
    """Confirmer la même obligation, sans changer sa place ni ses contreparties."""
    from .esprits import esprit
    stock = monde.data.get('promesses_joueur', []) if id == 'joueur' else esprit(monde, id)['engagements']
    for x in stock:
        if x == engagement and not x.get('annule'):
            x['minute'] = minute
            return copy.deepcopy(x)
    raise ValueError('Engagement actif absent lors du renouvellement')


def tenir(monde, id, engagement):
    """Retirer une parole exécutée ; l'appelant inscrit son souvenir au même instant."""
    pour = engagement['pour']
    if pour != 'joueur':
        memoire.accomplir_livraison_intermediaire(monde, pour, id, engagement['condition'].get('objet'))
    if reference_temporelle(engagement):
        from .temps import instant
        _clore_datee(monde, id, engagement, instant(monde), connue=True)
    else:
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
                memoire.affecter_livraison_intermediaire(monde, x['pour'], id, lot, part)
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
    return [] if id == 'joueur' else copy.deepcopy((monde.objets[id].get("profil") or {}).get("agendas", []))


def _fin_garde(monde, id, a):
    """Aucune interrogation de l'objet réel, même s'il a été supprimé."""
    from .esprits import lire
    objet = a["parametres"].get("objet")
    connu = memoire.faits_connus(monde, id, objet)
    fin = connu.get("fin")
    if fin and fin["valeur"]:
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
    croyances = memoire.faits_connus(monde, id)
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


def _verifier_compte(monde, id, a, contenu):
    assert (isinstance(contenu, dict) and set(contenu) == {"type", "charge", "issue"}
            and contenu["type"] == "compte_rendu" and contenu["issue"] in ISSUES_COMPTE_RENDU), "Contenu de compte rendu invalide"
    charge, o = contenu["charge"], a["origine"]
    assert (o["type"] == "mandat" and charge == {
        "mandant": o["de"], "parent": o["parent"], "agenda": a["id"],
        "sorte": a["sorte"], "parametres": a["parametres"]}), "Charge rapportée incohérente"


def _verifier_filiation(monde, id, a):
    origine = a["origine"]
    actifs = []
    attributions = a.get('attributions', [])
    assert isinstance(attributions, list), 'Attributions invalides'
    for x in attributions:
        assert (isinstance(x, dict) and set(x) - {'echeance', 'avertissement'} == {
            'sorte', 'parametres', 'titulaire', 'agenda', 'minute', 'etat'}
            and x['etat'] in ('active', 'remplacee', 'reprise')
            and type(x['minute']) is int and x['minute'] >= 0), 'Attribution invalide'
        p = _condition_mandat(monde, x['sorte'], x['parametres'])
        assert p == x['parametres'] and len(p['qui']) == 1, 'Charge attribuée invalide'
        assert {'titulaire': x['titulaire'], 'agenda': x['agenda']} in a.get('confies', []), 'Attribution sans mandat'
        enfant = _projet(monde, x['titulaire'], x['agenda'])
        assert (enfant['sorte'] == x['sorte']
                and _meme_charge(x, enfant['sorte'], enfant['parametres'])), 'Attribution incohérente'
        if 'echeance' in x:
            assert type(x['echeance']) is int and x['echeance'] >= x['minute'], 'Échéance attribuée invalide'
        if 'avertissement' in x:
            v = x['avertissement']
            assert (isinstance(v, dict) and set(v) == {'minute', 'entendu', 'presence'}
                    and type(v['minute']) is int and v['minute'] >= x['minute']
                    and type(v['entendu']) is bool and isinstance(v['presence'], dict)
                    and set(v['presence']) <= {'valeur', 'source', 'salle', 'case'}), 'Avertissement invalide'
        if x['etat'] == 'active':
            assert not any(_meme_charge(y, x['sorte'], p) for y in actifs), 'Plusieurs titulaires actifs'
            actifs.append(x)
    emis = a.get("compte_rendu")
    if emis is not None:
        assert (origine["type"] == "mandat" and a["etat"] in ("atteint", "abandonne")
                and set(emis) == {"contenu", "minute"} and type(emis["minute"]) is int), "Compte rendu émis invalide"
        _verifier_compte(monde, id, a, emis["contenu"])
    rapports = a.get("comptes_recus", [])
    assert isinstance(rapports, list), "Comptes rendus reçus invalides"
    identites = set()
    for r in rapports:
        assert isinstance(r, dict) and set(r) == {"de", "contenu", "croyance"}, "Compte rendu reçu invalide"
        c, charge = r["croyance"], r["contenu"]["charge"]
        cle = (r["de"], charge["agenda"])
        assert cle not in identites, "Compte rendu dupliqué"
        identites.add(cle)
        assert {"titulaire": r["de"], "agenda": charge["agenda"]} in a.get("confies", []), "Charge rapportée inconnue"
        enfant = _projet(monde, r["de"], charge["agenda"])
        _verifier_compte(monde, r["de"], enfant, r["contenu"])
        assert charge["mandant"] == id and charge["parent"] == a["id"], "Mandant rapporté incohérent"
        assert (set(c) == {"valeur", "source", "minute", "confiance", "poids"}
                and c["valeur"] in (None, *ISSUES_COMPTE_RENDU)
                and c["source"] in ("vu", "entendu", "dit:" + r["de"])
                and type(c["minute"]) is int and 0 <= c["confiance"] <= 1
                and 0 <= c["poids"] <= 1.05), "Croyance de compte rendu invalide"
    if origine["type"] == "mandat":
        assert (set(origine) == {"type", "de", "parent", "minute"}
                and isinstance(origine["de"], str) and isinstance(origine["parent"], str)
                and type(origine["minute"]) is int
                and type(a.get("confirme")) is int
                and a["confirme"] >= origine["minute"]), "Origine de mandat invalide"
        try:
            chaine = filiation(monde, id, a["id"])
            assert len(chaine) <= 3, "Profondeur de mandat dépassée"
            _condition_mandat(monde, a["sorte"], a["parametres"])
        except ValueError as e:
            raise AssertionError(str(e)) from e
        parent = _projet(monde, origine["de"], origine["parent"])
        assert parent.get("confies", []).count({"titulaire": id, "agenda": a["id"]}) == 1, "Mandat sans lien réciproque"
    else:
        assert "confirme" not in a, "Confirmation sans mandat"
    refs = a.get("confies", [])
    assert isinstance(refs, list), "Enfants de mandat invalides"
    identites, conditions = set(), []
    for r in refs:
        assert (isinstance(r, dict) and set(r) == {"titulaire", "agenda"}
                and isinstance(r["titulaire"], str) and isinstance(r["agenda"], str)), "Référence de mandat invalide"
        cle = (r["titulaire"], r["agenda"])
        assert cle not in identites, "Enfant de mandat dupliqué"
        identites.add(cle)
        enfant = _projet(monde, *cle)
        assert enfant is not None, "Enfant de mandat absent"
        o = enfant["origine"]
        assert (o["type"] == "mandat" and o["de"] == id
                and o["parent"] == a["id"]), "Parent de mandat incohérent"
        try:
            condition = (r["titulaire"], enfant["sorte"],
                         _condition_mandat(monde, enfant["sorte"], enfant["parametres"]))
        except ValueError as e:
            raise AssertionError(str(e)) from e
        assert condition not in conditions, "Condition de mandat dupliquée"
        conditions.append(condition)


def verifier(monde, id):
    from .esprits import lire
    if id == 'joueur':
        assert isinstance(monde.data.get('agendas_joueur', []), list), 'Agendas joueur invalides'
        offres = offres_mandat_joueur(monde)
        assert isinstance(offres, list), 'Offres de mandat invalides'
        assert len({o['id'] for o in offres}) == len(offres), 'Offre de mandat dupliquée'
        for o in offres:
            assert (isinstance(o, dict) and set(o) - {'agenda', 'echeance'} == {
                'id', 'mandant', 'parent', 'sorte', 'parametres', 'minute', 'statut'}
                and o['statut'] in ('propose', 'accepte', 'refuse')
                and type(o['minute']) is int and o['minute'] >= 0
                and isinstance(o['id'], str)), 'Offre de mandat invalide'
            assert _condition_mandat(monde, o['sorte'], o['parametres']) == o['parametres'], 'Charge proposée invalide'
            assert 'echeance' not in o or type(o['echeance']) is int and o['echeance'] >= o['minute'], 'Échéance proposée invalide'
            assert _projet(monde, o['mandant'], o['parent']) is not None, 'Parent proposé absent'
            if o['statut'] == 'accepte':
                a = _projet(monde, 'joueur', o['agenda'])
                assert a is not None and a['origine']['de'] == o['mandant'] and a['origine']['parent'] == o['parent'], 'Offre acceptée sans filiation'
            else:
                assert 'agenda' not in o, 'Offre sans accord avec agenda'
    percus = lire(monde, id).get("mandats_percus", [])
    assert isinstance(percus, list), "Mandats perçus invalides"
    identites = set()
    for r in percus:
        assert (isinstance(r, dict) and set(r) - {"croyance", "abus"} == {"de", "charge", "minute", "source"}
                and isinstance(r["de"], str) and type(r["minute"]) is int and r["minute"] >= 0
                and r["source"] in ("entendu", "dit:" + r["de"])
                and _charge_partagee(monde, r["de"], r["charge"])), "Mandat perçu invalide"
        cle = _identite_charge(r["de"], r["charge"])
        assert cle not in identites, "Mandat perçu dupliqué"
        identites.add(cle)
        if "croyance" in r:
            c = r["croyance"]
            assert (set(c) == {"valeur", "source", "minute", "confiance", "poids"}
                    and c["valeur"] in (None, *ISSUES_COMPTE_RENDU)
                    and c["source"] in ("vu", "entendu", "dit:" + r["de"])
                    and type(c["minute"]) is int and 0 <= c["confiance"] <= 1
                    and 0 <= c["poids"] <= 1.05), "Issue perçue invalide"
        _verifier_abus(r)
    c = lire(monde, id).get("contrat_intention") if id != "joueur" else None
    if c is not None:
        from .deliberation import condition_valide, Palier
        assert (isinstance(c, dict) and set(c) == {"but", "motif", "depuis", "contrat"}
                and isinstance(c["but"], dict) and isinstance(c["motif"], str)
                and type(c["depuis"]) is int), "Provenance d'intention invalide"
        contrat = c["contrat"]
        assert (isinstance(contrat, dict) and set(contrat) - {"phase", "sortie", "recours"} == {"palier", "valeur", "demande"}
                and type(contrat["palier"]) is int and contrat["palier"] in list(Palier)
                and isinstance(contrat["valeur"], (int, float))), "Contrat d'intention invalide"
        assert 'recours' not in contrat or (isinstance(contrat['recours'], str)
                and len(contrat['recours']) == 64), "Entrées de recours invalides"
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
                    and raison["besoin"] in ("faim", "chaleur", "peur")), "Raison d'intention invalide"
    stock = projets(monde, id)
    assert len([a for a in stock if a["etat"] == "actif"]) <= 3, "Trop d'agendas actifs"
    assert len({a["id"] for a in stock}) == len(stock), "Identifiants d'agenda dupliqués"
    for a in stock:
        if id == 'joueur':
            assert a['parametres'] == _condition_mandat(monde, a['sorte'], a['parametres']), 'Charge joueur invalide'
        _verifier_abus(a)
        assert (a["etat"] in ("actif", "sommeil", "atteint", "abandonne")
                and type(a["depuis"]) is int and isinstance(a["raison"], str)
                and a["origine"]["type"] in ("scenario", "situation", "evenement", "mandat", "occasion", "contrat") and "plan" not in a
                and isinstance(a["croyances"], str)), "Agenda invalide"
        _verifier_filiation(monde, id, a)
        jugements = a.get("jugements", [])
        assert isinstance(jugements, list), "Jugements de mandat invalides"
        from .relations import CLES_AUTORITE
        for j in jugements:
            _verifier_abus(j)
            assert (isinstance(j, dict) and set(j) >= {"qui", "minute", "sorte", "parametres", "issue", "raison"}
                    and (j["qui"] == 'joueur' or j["qui"] in monde.objets) and type(j["minute"]) is int
                    and j["issue"] in ("accepte", "refus", "impossible", "mefiance", "rancune", "qui_va_la")
                    and j["raison"] in ("adhesion", "dette", "autorite", "confirmation", j["issue"])), "Jugement de mandat invalide"
            _condition_mandat(monde, j["sorte"], j["parametres"])
            if "autorite" in j:
                assert (set(j["autorite"]) == CLES_AUTORITE
                        and 0 <= j["autorite"]["bonus"] <= 5
                        and all(isinstance(j[k], (int, float)) for k in ("cout", "total", "dd"))), "Bilan de mandat invalide"
    for engagement in en_cours(monde, id):
        from .deliberation import condition_valide
        # ``paye`` : une contrepartie payée d'avance (une part, un objet, une tâche), le bien et le prix
        # reçu (``echanges.engagements_echus``).
        from .biens import QUOI
        paye = engagement.get("paye")
        assert (isinstance(engagement, dict) and set(engagement) - {"paye", "lot", "objet", "annule", "commence", "reference_temporelle", "accord_initial"}
                - ({"realisee"} if id == "joueur" else set()) == {"condition", "pour", "minute"}
                and ("realisee" not in engagement or engagement["realisee"] is True)
                and ("objet" not in engagement or isinstance(engagement["objet"], str))
                and ("annule" not in engagement or engagement["annule"] in ("impossible", "refus"))
                and condition_valide(monde, engagement["condition"]) and "periode" not in engagement["condition"]
                and (engagement["pour"] == "joueur" or engagement["pour"] in monde.objets)
                and type(engagement["minute"]) is int
                and ('commence' not in engagement or engagement['condition'].get('proteger')
                     and type(engagement['commence']) is int and engagement['commence'] >= engagement['minute'])
                and ("lot" not in engagement or isinstance(engagement["lot"], str) and engagement["lot"] in monde.objets
                     and "remettre" in engagement["condition"])
                and (paye is None or isinstance(paye, dict) and set(paye) == {"objet", "prix", "quoi"}
                     and paye["quoi"] in QUOI
                     and isinstance(paye["objet"], str) and type(paye["prix"]) is int and paye["prix"] > 0)
                ), "Engagement de PNJ invalide"


def _verifier_abus(a):
    from .caractere import ENJEU
    if "abus" in a:
        abus = a["abus"]
        assert (isinstance(abus, dict) and set(abus) == {"cause", "prix"}
                and abus["cause"] in ("peril", "honnetete")
                and (abus["prix"] is None or isinstance(abus["prix"], (int, float))
                     and 0 < abus["prix"] <= ENJEU)), "Abus de mandat invalide"


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
    expirer_obligations(monde)
    _constater_issues(monde, id)
    e = esprit(monde, id)
    restants, finis = [], []
    for engagement in e["engagements"]:
        if reference_temporelle(engagement):
            # Un état trouvé vrai n'est jamais une réalisation datée.
            restants.append(engagement)
        elif engagement.get("annule"):
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
    for a in _stock(monde, id) or []:
        if a['origine']['type'] == 'contrat' and a['etat'] in ('actif', 'sommeil'):
            x = next((x for x in finis if x['condition'] == a['origine']['condition']
                      and x['minute'] == a['origine']['minute']), None)
            if x:
                from .occasion_protection import fin
                raison = fin(monde, id, x['condition'], x['minute'])
                reussi = x.get('commence') is not None and raison in ('echeance', 'danger cru passe')
                _changer(monde, id, a, 'atteint' if reussi else 'abandonne',
                         raison or 'contrat impossible', _croyances(monde, id))
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
    actualiser(monde, 'joueur')
    from .echanges import ENGAGEMENT_MAX, tenu, phrase_condition
    from .esprits import memoriser
    from .pnj import se_parler
    from .voix import nom_pour_joueur
    expirer_obligations(monde)
    _constater_issues(monde, 'joueur', lignes)
    for engagement in en_cours(monde, "joueur"):
        if reference_temporelle(engagement):
            continue
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
    expirer_obligations(monde)
    etats = etat_realisations(monde)
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
    constater_realisations(monde, avant)
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
    from .propositions import en_mots, en_mots_limite
    from .temps import instant
    def date(x):
        r = reference_temporelle(x)
        return en_mots_limite(r['limite'], instant(monde)) if r else ''
    lignes = ["Tu as promis " + groupe_nominal(nom_pour_joueur(monde, x["pour"]), "à") + " que "
              + phrase_condition(monde, x["condition"]) + date(x) + "." for x in en_cours(monde, "joueur")]
    for id, x in _obligations_datees(monde):
        if id == 'joueur' or x['pour'] != 'joueur':
            continue
        a = x.get('accord_initial')
        if not a:
            continue
        service, paiement = ((a['demande'], a['contrepartie']) if 'limite' in a['demande']
                             else (a['contrepartie'], a['demande']))
        lignes.append(nom_pour_joueur(monde, id) + ' a accepté ' + en_mots(monde, service)
                      + ' contre un paiement déjà effectué de ' + en_mots(monde, paiement) + '.')
    return lignes
