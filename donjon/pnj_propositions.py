"""Un recours après le choix ordinaire ; aucune lecture depuis la recherche.

Contreparties portées puis service autonome, sans geste de marché dans la
recherche. L'auditeur évalue le marché réel par le contrat du joueur.
"""
from .memoire import fait_brut
from . import relations, memoire
from .esprits import lire, memoriser


def verifier(e):
    """Façade de validation historique ; le stockage appartient à memoire."""
    memoire._verifier_recours(e)


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
        etat = fait_brut(monde, id, autre, "etat", {}).get("valeur", {})
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
    objet = demande.get("objet", autre)
    causes = moyens_crus(monde, id, {"de": autre, "operation": "proposer", "objet": objet})
    return {"de": autre, "besoin": besoin, "objet": objet,
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


def _entrees_negatives(monde, id, autre, demande, entrees):
    """Valeurs du jugement et des devis, sans dates de regard ni délai de reprise.

    Les besoins entrent par leurs effets sur les valeurs et les détresses : une
    croissance sans effet sur le marché n'est pas une nouvelle contrepartie.
    Les positions crues restent nécessaires au devis des livraisons/services.
    Le relevé est volontairement conservateur sur les connaissances et les accès.
    """
    import hashlib
    import json
    from .biens import valeur_bien
    from .caractere import STATS, caracteristique
    from .deliberation import _connus
    from .planification import vue, CHANGEANTS
    from .pnj import DUREES
    from .propositions import taches_crues
    from . import agendas
    e, v = lire(monde, id), vue(monde, id)
    connus = sorted(_connus(monde, id))
    def sans_dates(x):
        if isinstance(x, dict):
            return {k: sans_dates(y) for k, y in x.items()
                    if k not in ('minute', 'depuis', 'attente', 'instant')}
        if isinstance(x, (list, tuple)):
            return [sans_dates(y) for y in x]
        return x
    projection = json.dumps([
        # Le contrat de compensation a changé : un ancien verdict négatif
        # n'est pas une preuve sous les règles actuelles, même à monde égal.
        2, demande, entrees, monde.objets[id]['lieu'], monde.objets[id].get('profil'),
        {o: {a: {k: c[k] for k in ('valeur', 'salle', 'case', 'possession', 'envers') if k in c}
             for a, c in d.items()} for o, d in memoire.faits_connus(monde, id).items()},
        [[o, {k: x for k, x in monde.objets[o].items()
               if k not in CHANGEANTS and k not in ('profil', 'esprit')},
          valeur_bien(monde, id, o), valeur_bien(monde, id, o, True)] for o in connus],
        {q: relations.axes(monde, id, q) for q in relations.connus(monde, id)},
        sans_dates(memoire.reponses_retenues(monde, id)), sans_dates(agendas.en_cours(monde, id)),
        # Les compteurs du corps/vecu avancent même sans effet sur un devis.
        # Ses conséquences mécaniques passent par les caractéristiques réelles.
        sans_dates(e['pulsions']), sans_dates(e['intention']),
        [caracteristique(monde, id, s) for s in STATS],
        sans_dates(monde.data.get('permissions', [])),
        # services_proteges clôt les traces périmées : le relevé d'entrées
        # retient leurs données et les croyances, sans provoquer cette écriture.
        [s for s in monde.data.get('services_rendus', []) if s['de'] == id],
        list(taches_crues(monde, id, autre)),
        [getattr(v, k) for k in ('salles', 'proprietaire', 'gardes', 'prix_gardes',
          'chances_demandes', 'detresses', 'poste_garde', 'aides', 'illicite',
          'consomme_illicite', 'brise_illicite', 'richesse', 'piece', 'peur',
          'eau', 'peurs_sociales', 'taux_mefiance', 'dangers')],
        sorted(v.menacees), sorted(v.noyees), v.monte, v.eau_route,
        [[o, v.apport(o)] for o in connus if memoire.fait_brut(monde, id, o, 'lumiere') is not None],
        [[o, x.get('lieu'), x.get('position'), x.get('position_salle'), x.get('positions_salles')]
         for o, x in monde.objets.items() if not x.get('mobile') and x['type'] != 'personnage'],
        monde.data.get('mode_cases'), DUREES,
    ], ensure_ascii=False, sort_keys=True, default=lambda x: sorted(x))
    return hashlib.sha256(projection.encode('utf-8')).hexdigest()


def entrees_refus(monde, id, autre, objet, terme, *, devis=None):
    """Les moyens de cette demande et la force réellement offerte, pas la fortune disponible."""
    from .biens import prix, proprietaire
    from .deliberation import moyens_crus
    from .echanges import PRIX_SANS_PRIX
    from .spatial import porte_par
    if terme["type"] == "tache":
        from .echanges import valeur_proposition, PAS_PROPOSITION
        gain = (valeur_proposition(monde, id, terme, autre, devis=devis) or 0) / PAS_PROPOSITION
    else:
        gain = (terme["montant"] if terme["type"] == "pieces" else
                prix(monde, terme["objet"], terme["type"] == "part") or PRIX_SANS_PRIX)
    cause = moyens_crus(monde, id, {"de": autre, "operation": "proposer", "objet": objet})
    cause += [["porte", o, id, None] for o in sorted(monde.objets)
              if porte_par(monde, o, id) and proprietaire(monde, o) == id]
    cause.append(["inventaire", id, None, None])
    return {"cause": cause,
            "gain": gain}


def refus_tient(monde, id, refus, terme, *, devis=None):
    apres = entrees_refus(monde, id, refus["de"], refus["objet"], terme, devis=devis)
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
    devis = {}
    return any(s["de"] == autre and s.get("objet") == objet
               and s["operation"] in ("acheter", "proposer") and "offre" in s
               and refus_tient(monde, id, s, terme, devis=devis) for s in memoire.reponses_retenues(monde, id))


def reclamation(monde, id, objet):
    """Réclamer au porteur cru avant de reprendre, sans consulter son état privé."""
    from .deliberation import salle_crue, refus_retenu
    from .defense import actifs, lieux_dangereux
    if objet not in monde.objets:
        return None
    connu = memoire.faits_connus(monde, id, objet)
    porteur = connu.get('lieu', {}).get('possession', {}).get('porteur')
    if not porteur or porteur == id:
        return None
    etat = fait_brut(monde, id, porteur, 'etat', {}).get('valeur', {})
    if etat.get('conscient') is False:
        return None
    salle = salle_crue(monde, id, porteur)
    if (salle != monde.objets[id]['lieu'] or salle in lieux_dangereux(monde, id)
            or porteur in actifs(monde, id)
            or relations.peur(relations.envers(monde, id, porteur))
            or refus_retenu(monde, id, porteur, ('demander',), objet=objet)):
        return None
    return [{'operation': 'demander', 'cible': porteur, 'outil': objet,
                       'lieu': '', 'condition': '',
                       'contenu': {'type': 'reclamer', 'sujet': objet}}]


def plan_recours(monde, id, besoin, etapes):
    """La condition entendue est un moyen, après les moyens ordinaires seulement.

    Aucune comparaison de marchés dans la recherche : le service utilise son
    planificateur existant, puis le demandeur revient réclamer la contrepartie.

    ``None`` : aucun moyen ordinaire trouvé pour ce besoin. Une liste, même
    vide, est au contraire un résultat du but choisi : sans faute à éviter,
    il n'a pas de manque que l'ancien refus d'une autre demande comblerait.
    """
    if etapes is not None and not any(g["condition"] == "sans_temoin" for g in etapes):
        return None
    etapes = [] if etapes is None else etapes
    from .biens import richesse
    from .echanges import condition_remplie
    from .planification import planifier_pulsion, rejoindre
    e = lire(monde, id)
    # Une commission acceptée est un moyen attendu, pas un prétexte à tenter
    # aussi une faute pendant que l'autre accomplit sa parole.
    from .deliberation import refus_retenu
    from .echanges import ENGAGEMENT_MAX
    for s in memoire.intermediaires_retenus(monde, id):
        aide = e['aides_attendues'].get(s['objet'])
        if (s['besoin'] == besoin and not s['abouti'] and s['issue'] == 'accepte'
                and aide and aide['qui'] == s['via']
                and _dernier_recours(monde, id, s['de'], etapes)
                and monde.data['minutes'] - aide['minute'] <= ENGAGEMENT_MAX
                and not any(refus_retenu(monde, id, s['via'], ('confier',), objet=o)
                            for o in (s['objet'], s['livraison']))):
            return [{'operation': 'inspecter', 'cible': '', 'outil': '', 'lieu': '', 'condition': ''}]
    en_cours = memoire.service_en_cours(monde, id)
    if en_cours and en_cours['besoin'] == besoin:
        from .deliberation import satisfaite, refus_retenu
        refus = refus_retenu(monde, id, en_cours['de'], ('demander', 'acheter', 'proposer'), objet=en_cours['objet'])
        if (not refus or refus['raison'] not in ('mefiance', 'rancune')
                or satisfaite(monde, id, en_cours['condition'])):
            memoire.clore_service(monde, id)
        elif _dernier_recours(monde, id, en_cours['de'], etapes):
            plan = _plan_service(monde, id, en_cours['de'], en_cours['condition'])
            if plan:
                return plan
            memoire.clore_service(monde, id)
    intermediaire = devis_intermediaire(monde, id, besoin, etapes)
    # Deviser le service ne doit pas le marquer entrepris si la commission est
    # moins chère. Les deux recours restent hors de la recherche ordinaire.
    avant = memoire.services_tentes(monde, id), memoire.service_en_cours(monde, id)
    service = rendre_service(monde, id, besoin, etapes)
    if intermediaire:
        cout, plan, tentative = intermediaire
        cout_service = float('inf')
        if service:
            from .echanges import _devis_proposition, valeur_proposition
            en_cours = memoire.service_en_cours(monde, id)
            if en_cours:
                devis = _devis_proposition(monde, id, en_cours['condition'], en_cours['de'])
                cout_service = devis[0] if devis else float('inf')
            else:
                g = service[-1]
                terme = {'type': 'part' if g['operation'] == 'servir' else 'objet',
                         'objet': g['cible'] if g['operation'] == 'servir' else g['outil']}
                cout_service = valeur_proposition(monde, id, terme, tentative['de'])
        if cout_service is None or cout < cout_service:
            memoire.restaurer_services_devises(monde, id, *avant)
            memoire.retenir_intermediaire(monde, id, tentative)
            return plan
    if service:
        return service
    refusee = memoire.demande_refusee(monde, id)
    if refusee and refusee["besoin"] == besoin:
        for s in reversed(memoire.reponses_retenues(monde, id)):
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


def _dernier_recours(monde, id, autre, etapes):
    from .biens import proprietaire
    if etapes and not any(g['condition'] == 'sans_temoin' for g in etapes):
        return False
    for g in etapes:
        if g['operation'] in ('demander', 'acheter', 'confier', 'engager', 'proposer'):
            return False
        if g['condition'] == 'sans_temoin':
            return proprietaire(monde, g['cible']) == autre
    return True


def devis_intermediaire(monde, id, besoin, etapes):
    """Un seul porteur cru bien accueilli, sans consulter les liens des autres.

    La commission est une tâche ordinaire ; seule son approche est devisée par
    le demandeur. Le porteur fera son propre devis au moment de l'accepter.
    """
    from .deliberation import refus_retenu, _connus, besoin_de_part
    from .planification import rejoindre, vue, depart, TACHE
    r = memoire.demande_refusee(monde, id)
    if not r or r['besoin'] != besoin or not _dernier_recours(monde, id, r['de'], etapes):
        return None
    refus = refus_retenu(monde, id, r['de'], ('demander', 'acheter', 'proposer'), objet=r['objet'])
    if not refus or refus['raison'] not in ('mefiance', 'rancune'):
        return None
    cle = {**r, 'operation': refus['operation'], 'minute': refus['minute']}
    if any(all(s[k] == v for k, v in cle.items()) for s in memoire.intermediaires_retenus(monde, id)):
        return None
    attitudes = memoire.faits_connus(monde, id, r['de'])
    candidats = []
    v = debut = None
    for qui in sorted(_connus(monde, id)):
        if qui in (id, r['de'], 'joueur') or not monde.objets.get(qui, {}).get('profil'):
            continue
        if attitudes.get('attitude:' + qui, {}).get('valeur') != 'attachement':
            continue
        if (fait_brut(monde, id, qui, 'attitude:' + id) or {}).get('valeur') in ('mefiance', 'hostilite'):
            continue
        if relations.se_mefie(monde, id, qui):
            continue
        if v is None:
            v = vue(monde, id)
            debut = depart(monde, id, v)
        salle = v.salle(debut, qui)
        if salle is None or v.route(debut, salle) is None:
            continue
        cout = v.trajet(debut, salle, cible=qui) + TACHE
        candidats.append((cout, qui))
    if not candidats:
        return None
    cout, qui = min(candidats)
    route = rejoindre(monde, id, qui)
    if not route or not route[1]:
        return None
    o = monde.objets.get(r['objet'], {})
    condition = {'objet': r['objet'],
                 'servir' if besoin_de_part(o) == 'faim' else 'remettre': id}
    geste = {'operation': 'confier', 'cible': qui, 'outil': '', 'lieu': '',
             'condition': '', 'contenu': condition}
    return cout, [*route[0], geste], {**cle, 'via': qui, 'issue': 'preparee',
                                   'livraison': r['objet'], 'abouti': False}


def _plan_service(monde, id, autre, condition):
    from .echanges import _devis_proposition, promesse_autonome
    from .deliberation import illicite
    terme, devis = {'type': 'tache', 'condition': condition}, {}
    if not promesse_autonome(monde, id, autre, terme, devis=devis):
        return None
    plan = _devis_proposition(monde, id, condition, autre, devis)[1]
    if any(g['cible'] in monde.objets and illicite(monde, id, g['cible'], g['operation'])
           for g in plan if g['operation'] not in ('aller', 'inspecter')):
        return None
    return plan


def rendre_service(monde, id, besoin, etapes):
    """Après un refus social, un seul service autonome avant une faute ou l'impasse.

    La tentative est durable même impossible ; un délai ou un rechargement ne
    fait pas deviser à nouveau le même couple refus/besoin.
    """
    from .deliberation import refus_retenu, salle_crue
    from .propositions import taches_crues
    refusee = memoire.demande_refusee(monde, id)
    if not refusee or refusee['besoin'] != besoin:
        return None
    autre, objet = refusee['de'], refusee['objet']
    refus = refus_retenu(monde, id, autre, ('demander', 'acheter', 'proposer'), objet=objet)
    if not refus or refus['raison'] not in ('mefiance', 'rancune'):
        return None
    if salle_crue(monde, id, autre) != monde.objets[id]['lieu']:
        return None
    # Une faute contre un autre propriétaire ne sert pas de prétexte à ce recours.
    if not _dernier_recours(monde, id, autre, etapes):
        return None
    cle = {'de': autre, 'besoin': besoin, 'objet': objet,
           'operation': refus['operation'], 'minute': refus['minute']}
    if cle in memoire.services_tentes(monde, id):
        return None
    memoire.retenir_service_tente(monde, id, cle)
    terme = next(taches_crues(monde, id, autre), None)
    if terme:
        plan = _plan_service(monde, id, autre, terme['condition'])
        if plan:
            memoire.entreprendre_service(monde, id, refusee, terme['condition'])
            return plan
    # Un bien porté qui répond à un manque observé ne demande aucun devis.
    from .biens import proprietaire
    from .spatial import porte_par
    from .deliberation import besoin_de_part, parts
    etat = fait_brut(monde, id, autre, 'etat', {}).get('valeur', {})
    for o, x in sorted(monde.objets.items()):
        manque = besoin_de_part(x)
        if (manque and etat.get(manque) and parts(x) > 0
                and porte_par(monde, o, id) and proprietaire(monde, o) == id):
            if manque == 'faim':
                return [{'operation': 'servir', 'cible': o, 'outil': '', 'lieu': '',
                         'condition': '', 'contenu': {'pour': autre}}]
            return [{'operation': 'remettre', 'cible': autre, 'outil': o,
                     'lieu': '', 'condition': ''}]
    return None


def recours(monde, id, besoin, etapes):
    """Une seule offre avant la faute retenue, ou après la demande refusée."""
    import json
    from .biens import proprietaire
    from .deliberation import _connus, salle_crue, refus_retenu
    if etapes and not any(g["condition"] == "sans_temoin" for g in etapes):
        return None  # Un ancien refus ne remplace jamais un moyen ordinaire nouveau.
    e, candidats = lire(monde, id), []
    # Même transaction que les recours bornés de la recherche : aucune écriture
    # du monde pendant l'évaluation, publication seulement à la sortie du choix.
    choix = getattr(monde, '_vues_du_choix', None)
    retenues = choix[2] if choix is not None and choix[0] == id else e['attentes_bornees']
    service_devise = False
    # Les demandes ordinaires du préfixe gardent leur chance avant tout recours.
    for n, geste in enumerate(etapes):
        if geste["operation"] in ("demander", "acheter", "confier", "engager", "proposer"):
            return None
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
    refusee = memoire.demande_refusee(monde, id)
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
        if autre not in _connus(monde, id) or not monde.objets.get(autre, {}).get("profil"):
            continue
        contact = None
        if salle_crue(monde, id, autre) != monde.objets[id]["lieu"]:
            from .planification import Vue, depart, _appeler, _couper
            v = Vue(monde, id)
            contact = _appeler(v, depart(monde, id, v), autre)
            if contact is None:
                continue
        # Il sait où le trouver ; la marche sociale normale le rejoint au contact.
        entrees = _entrees(monde, id, autre, besoin, demande)
        cle = json.dumps(['recours_proposition', autre, besoin, demande['objet']], ensure_ascii=False)
        dependances = _entrees_negatives(monde, id, autre, demande, entrees)
        negatif = retenues.get(cle)
        sans_service = json.dumps([dependances, False])
        avec_service = json.dumps([dependances, True])
        if negatif in (sans_service, avec_service):
            service_devise = service_devise or negatif == avec_service
            continue
        avant = next((x for x in memoire.propositions_tentees(monde, id) if x["de"] == autre and x["besoin"] == besoin), None)
        refus = [s for s in memoire.reponses_retenues(monde, id) if s["de"] == autre and s.get("objet") == demande["objet"]
                 and s["operation"] in ("acheter", "proposer") and "offre" in s]
        if not refus and avant and _tient(avant, entrees):
            continue
        chance = relations.chance_demande(monde, id, autre)
        offres = [(relations.chance_proposition(chance, gain), -cout, t)
                  for t, cout, gain in _contreparties(monde, id, autre, demande)
                  if not any(refus_tient(monde, id, s, t) for s in refus)]
        offres = [o for o in offres if o[0] > chance]
        complet = not service_devise and not (avant and _tient(avant, entrees))
        if complet:
            from .propositions import taches_crues
            from .echanges import offre_sensee, valeur_proposition, PAS_PROPOSITION
            # Un seul service devisé par recours, après les biens et pièces.
            terme = next(taches_crues(monde, id, autre), None)
            service_devise = terme is not None
            devis = {}
            if terme and offre_sensee(monde, id, autre, demande, terme, devis=devis):
                cout = valeur_proposition(monde, id, terme, autre, devis=devis)
                if cout is not None and cout > 0 and not any(
                        refus_tient(monde, id, s, terme, devis=devis) for s in refus):
                    offres.append((relations.chance_proposition(chance, cout / PAS_PROPOSITION), -cout, terme))
        if not offres:
            if complet:
                retenues[cle] = avec_service if service_devise else sans_service
            continue
        if contact is not None:
            # L'appel sert une négociation réellement admissible. Il ne
            # remplace pas un plan par un contact sans contrepartie possible.
            # Le choix final de l'offre et son accord attendent la venue.
            return _couper(contact[2])[0]
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
    objet = demande.get("objet", autre)
    if offre_refusee(monde, id, autre, objet, terme):
        return False
    if not offre_sensee(monde, id, autre, demande, terme):
        return False
    e = lire(monde, id)
    besoin = e["intention"]["motif"]
    entrees = _entrees(monde, id, autre, besoin, demande)
    bilan = proposer(monde, id, autre, demande, terme)
    e = lire(monde, id)
    memoire.retenir_proposition_tentee(monde, id, entrees)
    issue = bilan["cause"] or "accepte"
    if autre == 'joueur' and issue == 'attente':
        import copy
        monde.data.setdefault('offres_joueur', {})['marche_' + id] = {
            'de': id, 'demande': copy.deepcopy(demande), 'contrepartie': copy.deepcopy(terme), 'statut': 'propose'}
    agenda = (e['intention'] or {}).get('but', {}).get('agenda')
    from . import agendas
    agendas.conclure_offre(monde, id, agenda, issue)
    memoriser(monde, id, {"type": "proposition", "a": autre, "demande": demande,
                          "contrepartie": terme, "issue": issue})
    if bilan["cause"] and issue != 'attente':
        retenir_refus(monde, id, autre, "proposer", issue, objet=objet, besoin=besoin,
                      offre=entrees_refus(monde, id, autre, objet, terme))
    recit = f"{_qui(monde, id)} propose à {_qui(monde, autre)} {en_mots(monde, terme)} contre {en_mots(monde, demande)}"
    _chroniquer(monde, id, f"{recit} ({issue}).", "social")
    reponse = (f"{_qui(monde, autre)} accepte l'échange."
               + (" La remise est promise." if bilan.get("livraison_differee") else " Les biens convenus sont remis.")
               if not bilan["cause"] else f"{_qui(monde, autre)} refuse l'échange.")
    if issue == 'attente':
        reponse = ''  # Aucune parole ne doit être prêtée au joueur.
    elif issue == 'accepte' and (terme['type'] == 'tache' or demande['type'] == 'tache'):
        reponse = f"{_qui(monde, autre)} accepte l'échange. Le service convenu est promis."
    faire_entendre(monde, id, autre, recit + ".", cites_terme(demande) + cites_terme(terme), lignes,
                   reponse=reponse)
    if issue == 'attente':
        lignes.append("Tu peux accepter offre ou refuser offre. Aucun paiement n'a encore lieu.")
    return True  # L'offre est achevée même refusée : la suite sera délibérée de nouveau.
