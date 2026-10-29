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
                and portage["auteur"] == p["porteur"] and not connu.get("fin", {}).get("valeur")):
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
    constats = [lire(monde, id)["croyances"].get(q, {}).get("lieu", {}) for q in p["qui"]]
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
    if dementi:
        se_mefier(monde, id, locuteur, "vu")
    accepte = not dementi and jet_persuasion(monde, id, locuteur, 10)[0]
    croyance = {"valeur": propre if propre is not None else contenu["issue"] if accepte else None,
                "source": ("entendu" if charge["sorte"] == "informer" else "vu") if propre is not None else source,
                "minute": monde.data["minutes"], "confiance": 1 if propre is not None else round(.7 * clarte(monde, id), 2)}
    croyance["poids"] = poids_source(monde, id, croyance)
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
    if (titulaire not in monde.objets
            or monde.objets[titulaire]["type"] != "personnage"):
        raise ValueError("Titulaire de mandat invalide")
    p = _condition_mandat(monde, sorte, parametres)
    if echeance is not None and (type(echeance) is not int or echeance < monde.data['minutes']):
        raise ValueError("Échéance de mandat invalide")
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
    _limiter(monde, titulaire, empreinte)
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
    c = lire(monde, id)['croyances'].get(autre, {}).get('lieu', {})
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
    from math import ceil
    p = _condition_mandat(monde, sorte, parametres)
    croyances = lire(monde, id)['croyances']
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
                         for s, d in lire(monde, id)["croyances"].items()})
    if not moyens_seuls and any(a["sorte"] in ("obtenir", "récupérer") for a in (_stock(monde, id) or [])):
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
        _reviser_comptes(monde, id, a)
        if a["etat"] == "atteint" and a["raison"] == "compte rendu cru" and not _acheve_par_comptes(monde, id, a):
            _changer(monde, id, a, "actif", "compte rendu dementi", empreinte)
        if a["etat"] not in ("actif", "sommeil"):
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
            connu = lire(monde, id)["croyances"].get(a["parametres"]["objet"], {})
            if connu.get("fin", {}).get("valeur"):
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


def _personne_disponible_crue(monde, id, qui):
    """Identité connue, ni mort ni départ crus ; aucune lecture du corps réel."""
    from .esprits import lire
    from .noms import PERSONNES
    etat = lire(monde, id)["croyances"].get(qui, {}).get("etat", {}).get("valeur", {})
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
    croyances = lire(monde, id)["croyances"]
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
    choix = [(mesure[0] if mesure else float("inf"), id, propre)]
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
        return _amener(monde, id, a, empreinte, cout=cout, cibles=restants)
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
        preuve = e['croyances'].get(c.get('servir', objet), {}).get(attribut)
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


def prendre(monde, id, engagement):
    """Inscrire aussi la proposition provisoire, retirée si le devis ou le jet refuse."""
    from .esprits import esprit
    stock = monde.data.setdefault("promesses_joueur", []) if id == "joueur" else esprit(monde, id)["engagements"]
    stock.append(copy.deepcopy(engagement))


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
                    and raison["besoin"] in ("faim", "chaleur", "peur")), "Raison d'intention invalide"
    stock = projets(monde, id)
    assert len([a for a in stock if a["etat"] == "actif"]) <= 3, "Trop d'agendas actifs"
    assert len({a["id"] for a in stock}) == len(stock), "Identifiants d'agenda dupliqués"
    for a in stock:
        assert (a["etat"] in ("actif", "sommeil", "atteint", "abandonne")
                and type(a["depuis"]) is int and isinstance(a["raison"], str)
                and a["origine"]["type"] in ("scenario", "situation", "evenement", "mandat") and "plan" not in a
                and isinstance(a["croyances"], str)), "Agenda invalide"
        _verifier_filiation(monde, id, a)
        jugements = a.get("jugements", [])
        assert isinstance(jugements, list), "Jugements de mandat invalides"
        from .relations import CLES_AUTORITE
        for j in jugements:
            assert (isinstance(j, dict) and set(j) >= {"qui", "minute", "sorte", "parametres", "issue", "raison"}
                    and j["qui"] in monde.objets and type(j["minute"]) is int
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
