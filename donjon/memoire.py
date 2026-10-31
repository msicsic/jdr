"""Porte des épisodes et de leurs requêtes, au format historique.

S1 conserve la liste sauvegardée, son plafond et les crochets réentrants.
Aucune requête de ce module ne renvoie le stock mutable aux consommateurs.
"""
import copy
from contextlib import contextmanager

MEMOIRE_MAX = 40


def episodes(monde, id, *, types=None, derniers=None):
    """Copies profondes dans l'ordre du tampon, sans créer d'esprit.

    La fenêtre porte sur le tampon entier avant le filtre de types : les trois
    derniers souvenirs ne sont pas les trois derniers d'une famille choisie.
    Aucune récence, validité ni connaissance supplémentaire n'est inférée ici.
    """
    from .esprits import lire
    stock = lire(monde, id)['memoire']
    if derniers is not None:
        stock = stock[-derniers:] if derniers else []
    return [copy.deepcopy(s) for s in stock if types is None or s['type'] in types]


def rafraichir_geste_entendu(monde, id, objet):
    """Prolonge le dernier geste anonyme récent sur ce bien, sans crochet.

    Opération d'écriture : conserve l'installation historique de l'esprit,
    l'identité de l'occurrence et la borne inclusive de récence.
    """
    from .esprits import esprit, RECENT
    for s in reversed(esprit(monde, id)['memoire']):
        if (s['type'] == 'entendu_agir' and s['objet'] == objet
                and monde.data['minutes'] - s['minute'] <= RECENT):
            s['minute'] = monde.data['minutes']
            return True
    return False


def migrer_presences_percues(monde, id):
    """Retire les présences anciennes et en rend des copies, dans leur ordre."""
    from .esprits import lire
    presences = []
    for s in list(lire(monde, id)['memoire']):
        if s['type'] == 'presence_percue':
            evincer_episodes(monde, id, lambda episode: episode is s)
            presences.append(copy.deepcopy({k: s[k] for k in ('qui', 'salle', 'instant')}))
    return presences


def episodes_parts_promises(monde, id):
    """Copies ordonnées des promesses de parts et de leurs suites historiques."""
    from .esprits import lire
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire']
            if s['type'] in ('promis', 'nourri', 'recu', 'promesse_annulee', 'creance')]


def travaux_payes_retenus(monde, id):
    """Tous les travaux du tampon, doublons compris, sans politique de validité."""
    from .esprits import lire
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire'] if s['type'] == 'tache_payee']


def dernier_travail_paye(monde, id, condition):
    """Dernier accord et présence d'une créance de tâche ultérieure envers lui.

    L'ordre de la liste, et non la date, départage les occurrences.
    """
    from .esprits import lire
    stock = lire(monde, id)['memoire']
    for i in range(len(stock) - 1, -1, -1):
        s = stock[i]
        if s['type'] == 'tache_payee' and s['condition'] == condition:
            reclame = any(x['type'] == 'creance' and x['de'] == s['a'] and x.get('quoi') == 'tache'
                          for x in stock[i + 1:])
            return copy.deepcopy(s), reclame
    return None, False


def suivi_engagement(monde, id, condition, depuis):
    """Copie du dernier suivi, arrêtée par toute autre parole de même condition."""
    from .esprits import lire
    for s in reversed(lire(monde, id)['memoire']):
        if s.get('condition') != condition:
            continue
        if s['type'] in ('engagement_pris', 'engagement_tenu', 'engagement_abandonne'):
            break
        if s['type'] == 'suivi_engagement' and s['depuis'] == depuis:
            return copy.deepcopy(s)
    return None


def pret_retenu(monde, id, objet, a):
    """Souvenir du prêt ; ne consulte ni ne modifie la permission réelle."""
    from .esprits import lire
    return any(s['type'] == 'pret' and s.get('objet') == objet and s.get('a') == a
               for s in lire(monde, id)['memoire'])


def remise_retenue(monde, id, de, objet, minute):
    """Réception de la même minute, avant l'épreuve d'engagement tenu.

    Comme le crochet historique, cette consultation installe l'esprit si absent.
    """
    from .esprits import esprit
    return any(s['type'] in ('nourri', 'recu') and s.get('de') == de
               and s.get('objet') == objet and s['minute'] == minute
               for s in esprit(monde, id)['memoire'])


def juger_reclamations_pret(monde, id, objet, pret, apres_jugement):
    """Marque chaque réclamation échue avant sa conséquence réentrante.

    L'itération porte le stock vivant : un ajout/une éviction dans la conséquence
    garde exactement son effet historique sur les occurrences suivantes.
    Aucun ajout ni crochet propre à cette opération.
    """
    from .esprits import esprit
    from .biens import RENDRE
    for s in esprit(monde, id)['memoire']:
        if (s['type'] == 'pret_reclame' and s['objet'] == objet and s['pret'] == pret
                and s['echu'] and not s.get('juge') and monde.data['minutes'] - s['minute'] >= RENDRE):
            s['juge'] = True
            apres_jugement()


def derniere_approche(monde, id, auteur, objet, lieu, cible, case=None):
    """Dernière approche de la charge ; les anciens lieux/cibles restent implicites."""
    from .esprits import lire
    return copy.deepcopy(next((s for s in reversed(lire(monde, id)['memoire'])
        if s['type'] == 'approche_charge' and s['auteur'] == auteur and s['objet'] == objet
        and s.get('lieu', lieu) == lieu and s.get('cible', cible) == cible
        and (case is None or s['case'] == case)), None))


def mise_en_garde_retenue(monde, id, destinataire, objet, preuve):
    """Même preuve d'approche, sans péremption ni effet de lecture."""
    from .esprits import lire
    return any(s['type'] == 'mise_en_garde' and s['a'] == destinataire
               and s['objet'] == objet and s['preuve'] == preuve
               for s in lire(monde, id)['memoire'])


def avertissements_a_donner(monde, id):
    """Copies dans l'ordre historique, y compris les avertissements déjà tenus."""
    from .esprits import lire
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire'] if s['type'] == 'a_prevenir']


def _avertissement(monde, id, victime, auteur):
    from .esprits import lire
    # Le premier, même déjà tenu : ne pas passer à une autre occurrence.
    return next((s for s in lire(monde, id)['memoire'] if s['type'] == 'a_prevenir'
                 and s['victime'] == victime and s['auteur'] == auteur), None)


def avertissement_du(monde, id, victime, auteur):
    return copy.deepcopy(_avertissement(monde, id, victime, auteur))


def acquitter_avertissement(monde, id, victime, auteur):
    """Marque tenu le premier avertissement correspondant, sans crochet."""
    alerte = _avertissement(monde, id, victime, auteur)
    if alerte is None or alerte.get('tenu'):
        return False
    alerte['tenu'] = True
    return True


def secours_retenus(monde, id, qui=None, *, en_attente=False):
    """Copies ordonnées des cris ; le lecteur conserve sa borne de récence."""
    from .esprits import lire
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire'] if s['type'] == 'secours'
            and (qui is None or s['qui'] == qui) and (not en_attente or not s.get('examine'))]


def _examiner_secours(monde, id, constate):
    from .esprits import lire
    secourus = []
    for s in lire(monde, id)['memoire']:
        if s['type'] == 'secours' and not s.get('examine') and constate(s):
            s['examine'] = True
            secourus.append(s['qui'])
    return secourus


def examiner_secours_du_lieu(monde, id, salle):
    """Acquitte chaque cri du lieu effectivement inspecté, dans l'ordre."""
    return _examiner_secours(monde, id, lambda s: s['salle'] == salle)


def examiner_secours_constates(monde, id):
    """Vue actuelle ou état vu strictement après le cri, comme historiquement."""
    from .esprits import lire, percoit
    e = lire(monde, id)

    def constate(s):
        qui = s['qui']
        etat = e['croyances'].get(qui, {}).get('etat', {})
        vu = monde.visible(qui) if id == 'joueur' else percoit(monde, id, qui)
        return vu or etat.get('source') == 'vu' and etat['minute'] > s['minute']

    return _examiner_secours(monde, id, constate)


def retenir_episode(monde, id, evenement):
    """Copie, date et retient l'occurrence avant ses conséquences métier."""
    from .esprits import esprit, _date_indices_soupcon, GESTES_SOUPCON_MAX
    if evenement["type"] == "dit" and "valeur" in evenement:
        from .social import retenir_dit
        retenir_dit(monde, id, evenement["a"], {"type": "affirmation", **{
            k: evenement[k] for k in ("sujet", "attribut", "valeur")}})
    memoire = esprit(monde, id)["memoire"]
    souvenir = copy.deepcopy({"minute": monde.data["minutes"], **evenement})
    from .relations import identifier
    from .temps import instant
    if id != "joueur" and souvenir["type"] in ("vu_agir", "entendu_agir", "vu_porter", "vol_surpris"):
        # Même indice et même identité de preuve qu'avant la porte S1a.
        gestes = esprit(monde, id)["indices_soupcon"]["gestes"]
        gestes.append({"objet": souvenir["objet"], "instant": _date_indices_soupcon(monde)})
        del gestes[:-GESTES_SOUPCON_MAX]
    identifier(souvenir, instant(monde))
    memoire.append(souvenir)
    del memoire[:-MEMOIRE_MAX]
    from .relations import souvenir as eprouver_souvenir
    eprouver_souvenir(monde, id, souvenir)
    from .defense import retenir as retenir_violence
    retenir_violence(monde, id, souvenir)


def evincer_episodes(monde, id, retirer):
    """Filtre en place, dans l'ordre, sans crochet ni copie des survivants.

    Le prédicat porte la décision du consommateur ; il ne doit pas modifier
    le stock. L'identité de la liste et des épisodes conservés reste intacte.
    """
    from .esprits import esprit
    memoire = esprit(monde, id)["memoire"]
    memoire[:] = [s for s in memoire if not retirer(s)]


def bruits_retenus(monde, id, salle=None, *, examens=False):
    """Copies ordonnées des bruits, et éventuellement de leurs examens vains.

    Pas de filtre de péremption : chaque lecteur garde sa politique historique.
    Une consultation, même d'un esprit absent, ne crée rien.
    """
    from .esprits import lire
    types = ('bruit', 'examen') if examens else ('bruit',)
    return [copy.deepcopy(s) for s in lire(monde, id)['memoire']
            if s['type'] in types and (salle is None or s['salle'] == salle)]


def retirer_bruits(monde, id, salle):
    """Retire les bruits du lieu, sans toucher aux examens ni aux crochets."""
    evincer_episodes(monde, id, lambda s: s['type'] == 'bruit' and s['salle'] == salle)


def retenir_examen_sonore(monde, id, salle, case=None):
    """Consomme les bruits parcourus et retient l'examen vain historique."""
    from .esprits import esprit
    from .ouie import resolu, INTENSITES
    stock = esprit(monde, id)['memoire']
    vus = [s for s in stock if s['type'] == 'bruit' and s['salle'] == salle]
    attendus = [s for s in vus if not resolu(monde, id, s)]
    evincer_episodes(monde, id, lambda s: any(s is v for v in vus)
                     or (s['type'] == 'examen' and s['salle'] == salle and attendus))
    if attendus:
        qui = {s.get('qui') for s in attendus}
        retenir_episode(monde, id, {'type': 'examen', 'salle': salle,
                                   'case': list(case) if case is not None else None,
                                   'nature': max((s['nature'] for s in attendus), key=INTENSITES.get),
                                   **({'qui': qui.pop()} if len(qui) == 1 and None not in qui else {})})
    return bool(attendus)


def _examen_couvrant(monde, id, salle, n, qui, case):
    """Référence interne uniquement ; même ordre et mêmes bornes historiques."""
    from .esprits import RECENT, lire
    from .ouie import INTENSITES
    minute = monde.data['minutes']
    for s in reversed(lire(monde, id)['memoire']):
        if s['type'] != 'examen' or s['salle'] != salle or minute - s['minute'] > RECENT:
            continue
        if INTENSITES[n] > INTENSITES[s['nature']] or qui is not None and qui != s.get('qui'):
            return None
        if case is not None and s['case'] is None:
            return None
        return s
    return None


def examen_couvrant(monde, id, salle, n, qui=None, case=None):
    """Copie de l'examen qui couvre le bruit, ou None ; aucune écriture."""
    return copy.deepcopy(_examen_couvrant(monde, id, salle, n, qui, case))


def rafraichir_examen_sonore(monde, id, salle, n, qui=None, case=None):
    """Prolonge le même examen si le bruit est couvert, sans nouvel épisode."""
    examen = _examen_couvrant(monde, id, salle, n, qui, case)
    if examen is None:
        return False
    examen['minute'] = monde.data['minutes']
    return True


def retenir_bruit_sans_profil(monde, id, salle, n, niveau):
    """Remplace les bruits du lieu par leur maximum, sans délibération."""
    from .esprits import esprit
    from .ouie import INTENSITES
    anciens = [s for s in esprit(monde, id)['memoire'] if s['type'] == 'bruit' and s['salle'] == salle]
    retirer_bruits(monde, id, salle)
    retenir_episode(monde, id, {'type': 'bruit', 'salle': salle,
                               'nature': max([n, *(s['nature'] for s in anciens)], key=INTENSITES.get),
                               'niveau': max([niveau, *(s.get('niveau', niveau) for s in anciens)])})



# Localisation et preuves composées : le stockage reste celui des croyances
# historiques. Une lecture brute conserve la confiance initiale ; la façade
# esprits.croyance applique encore ses filtres et le vieillissement courant.


def _fait_stock(monde, id, sujet, attribut, defaut=None):
    """Accès privé ; aucune référence de stockage ne sort de cette porte."""
    from .esprits import lire
    return lire(monde, id)["croyances"].get(sujet, {}).get(attribut, defaut)


def fait_brut(monde, id, sujet, attribut, defaut=None):
    """Copie pure d'une preuve, sans vieillissement ni création d'esprit."""
    return copy.deepcopy(_fait_stock(monde, id, sujet, attribut, defaut))


_TOUS_LES_SUJETS = object()


def faits_connus(monde, id, sujet=_TOUS_LES_SUJETS):
    """Photographie ordonnée des preuves ; aucun droit ni état réel ajouté."""
    from .esprits import lire
    stock = lire(monde, id)["croyances"]
    return copy.deepcopy(stock if sujet is _TOUS_LES_SUJETS else stock.get(sujet, {}))


def localisation(monde, id, sujet):
    """Dernière preuve composée, confiance initiale et consommation comprises."""
    return fait_brut(monde, id, sujet, "lieu")


def rafraichir_mobilite_constatee(monde, id, sujet, source):
    from .esprits import lire
    lieu = lire(monde, id)["croyances"].get(sujet, {}).get("lieu")
    if (lieu and lieu["source"] == source == "vu" and lieu["minute"] == monde.data["minutes"]
            and personne_autre(monde, id, sujet)):
        lieu["mobilite"] = mobilite_crue(monde, id, sujet)


def reconnaitre_localisation_vocale(monde, id, sujet, *, imposture=False):
    """Reconnaissance de la même voix : confirme ou retire sa seule piste déclarée."""
    from .esprits import esprit
    attributs = esprit(monde, id)["croyances"].get(sujet, {})
    c = attributs.get("lieu")
    if c and c["source"] == "se_dit":
        if imposture:
            del attributs["lieu"]
        else:
            c.update(source="entendu", confiance=1.0)


def installer_faits_projetes(monde, id, sujet, faits):
    """Copie mécanique dans un devis isolé, sans admission ni crochet réel."""
    from .esprits import esprit
    esprit(monde, id)["croyances"].setdefault(sujet, {}).update(copy.deepcopy(faits))


def remplacer_faits_projetes(monde, id, faits):
    """Remplace le savoir d'un acteur de calcul par celui de son observateur."""
    from .esprits import esprit
    esprit(monde, id)["croyances"] = copy.deepcopy(faits)


def retirer_faits(monde, id, sujet):
    """Retrait historique complet d'un sujet (annulation d'un bien provisoire)."""
    from .esprits import esprit
    del esprit(monde, id)["croyances"][sujet]


def retirer_moyen_projete(monde, id, objet):
    """Épuisement d'une réservation dans la copie de calcul uniquement."""
    from .esprits import esprit
    attributs = esprit(monde, id)["croyances"].setdefault(objet, {})
    attributs['lieu'] = {'valeur': None, 'salle': None, 'case': None,
                        'source': 'savoir', 'minute': monde.data['minutes'], 'confiance': 1}
    etat = attributs.get('etat')
    if etat and 'disponible' in etat['valeur']:
        etat['valeur']['disponible'] = False


def verifier_localisation(monde, c):
    from .esprits import POSITIONS_HYPOTHESES
    assert c.get("mobilite", "mobile") in POSITIONS_HYPOTHESES["demi_vies"], "Mobilité crue invalide"
    if "hypothese_consommee" in c:
        p = c["hypothese_consommee"]
        assert (isinstance(p, dict) and set(p) == {"minute", "lieu"}
                and type(p["minute"]) is int and isinstance(p["lieu"], str)), "Hypothèse consommée invalide"
    # Une croyance peut survivre à son objet (détruit, retiré).
    assert (set(c) >= {"valeur", "salle", "case"}
            and (c["valeur"] is None or isinstance(c["valeur"], str))
            and (c["salle"] is None or c["salle"] in monde.data["salles"])
            and (c["case"] is None or (isinstance(c["case"], list) and len(c["case"]) == 2))), "Croyance de lieu invalide"
    if "possession" in c:
        p = c["possession"]
        assert (isinstance(p, dict) and set(p) == {"porteur", "proprietaire", "permis", "remis_par", "remise_autorisee"}
                and all(p[k] is None or isinstance(p[k], str)
                        for k in ("porteur", "proprietaire", "remis_par"))
                and type(p["permis"]) is bool and type(p["remise_autorisee"]) is bool), "Possession constatée invalide"


def verifier_faits(monde, id):
    """Validation historique, sans copie ni réparation d'une sauvegarde invalide."""
    from .esprits import lire, _croyance_valide
    stock = lire(monde, id)["croyances"]
    if id == "joueur":
        assert isinstance(stock, dict), "Croyances du joueur invalides"
    for sujet, attributs in stock.items():
        if id == "joueur":
            assert (isinstance(sujet, str) and isinstance(attributs, dict)
                    and (sujet in monde.data["salles"] and set(attributs) <= {"eau", "prevision"}
                         or set(attributs) <= {"fin", "lieu", "etat", "verrouillee", "statuts", "detresse"})), "Perception du joueur invalide"
        else:
            assert isinstance(sujet, str) and isinstance(attributs, dict), "Sujet de croyance invalide"
        for attribut, c in attributs.items():
            _croyance_valide(monde, attribut, c)


def personne_autre(monde, id, sujet):
    return sujet != id and (sujet == "joueur" or monde.objets.get(sujet, {}).get("type") == "personnage")


def mobilite_crue(monde, id, sujet):
    """Ce qui retient la personne, selon les seules preuves de l'observateur."""
    c = _fait_stock(monde, id, sujet, "lieu", {})
    from .esprits import croyance, lire
    preuve = croyance(monde, id, sujet, "etat") or {}
    etat = preuve.get("valeur", {}) if preuve.get("minute", -1) >= c.get("minute", 0) else {}
    if any(etat.get(k) for k in ("lie", "tenu", "enferme")) or etat.get("conscient") is False:
        return "retenu"
    croyances = lire(monde, id)["croyances"]
    lieu = croyances.get(sujet, {}).get("lieu", {}).get("salle")
    sorties = monde.data["salles"].get(lieu, {}).get("sorties", {}).values()
    if sorties and all(s.get("porte") and
                       (croyances.get(s["porte"], {}).get("verrouillee") or {}).get("valeur")
                       and not (croyances.get(s["porte"], {}).get("etat") or {}).get("valeur", {}).get("ouverte")
                       for s in sorties):
        return "retenu"
    intention = (croyance(monde, id, sujet, "intention") or {}).get("valeur")
    if etat.get("assis") or intention in ("garde", "guet"):
        return "pose"
    return "mobile"


def confiance_position(monde, id, sujet):
    """Confiance actuelle, sans effacer la dernière position ni rajeunir un relais."""
    c = _fait_stock(monde, id, sujet, "lieu")
    if not c:
        return 0.
    if not personne_autre(monde, id, sujet) or c["valeur"] is None:
        return c["confiance"]
    from .esprits import POSITIONS_HYPOTHESES
    regle = monde.data.get("positions_hypotheses", POSITIONS_HYPOTHESES)
    date = min(c["minute"], c.get("origine", {}).get("minute", c["minute"]))
    age = max(0, monde.data["minutes"] - date)
    return c["confiance"] * 2 ** (-age / regle["demi_vies"][c.get("mobilite", "mobile")])


def position_a_verifier(monde, id, sujet):
    c = _fait_stock(monde, id, sujet, "lieu")
    from .esprits import POSITIONS_HYPOTHESES
    return bool(personne_autre(monde, id, sujet) and c and c["valeur"] is not None
                and confiance_position(monde, id, sujet)
                <= monde.data.get("positions_hypotheses", POSITIONS_HYPOTHESES)["seuil"])


def hypothese_consommee(monde, id, sujet):
    """La piste expirée a déjà été éprouvée, sans nouvelle localisation positive."""
    c = _fait_stock(monde, id, sujet, "lieu", {})
    return personne_autre(monde, id, sujet) and "hypothese_consommee" in c


def consommer_hypothese(monde, id, sujet):
    """Une inspection/un appel épuise sa piste, pas la recherche de toute personne.

    Le repère appartient à la croyance, survit à son constat d'absence et aux
    relais de l'ancien renseignement. Seul croire admet une nouvelle preuve.
    """
    if not position_a_verifier(monde, id, sujet) or hypothese_consommee(monde, id, sujet):
        return
    from .esprits import esprit
    c = esprit(monde, id)["croyances"][sujet]["lieu"]
    c["hypothese_consommee"] = {"minute": monde.data["minutes"], "lieu": c["valeur"]}


@contextmanager
def verification_positions(monde, id, sujets):
    """Le résultat de sa propre vérification n'en programme pas une autre.

    Retrouver la même personne au même lieu clôt cette piste, même si le
    regard vient d'en rafraîchir la date. Une position différente reste une
    nouvelle entrée. Les perceptions ultérieures peuvent rouvrir la piste.
    """
    pistes = {s: localisation(monde, id, s)["valeur"]
              for s in sujets if position_a_verifier(monde, id, s)}
    for s in pistes:
        consommer_hypothese(monde, id, s)
    try:
        yield
    finally:
        from .esprits import esprit
        for s, lieu in pistes.items():
            c = esprit(monde, id)["croyances"][s]["lieu"]
            if c["valeur"] in (None, lieu):
                c["hypothese_consommee"] = {"minute": monde.data["minutes"], "lieu": lieu}


def admettre_fait(monde, id, sujet, attribut, valeur, source, confiance=1.0, **lieu):
    from .esprits import (lire, esprit, _retenir_presence, prevision_propre,
                          reconsiderer)
    monde_minute = monde.data["minutes"]
    if attribut == "lieu" and valeur is None:
        # Voir l'ancienne place vide vérifie aussi la piste, même avant le
        # dernier geste du tour d'horizon prévu par le plan.
        consommer_hypothese(monde, id, sujet)
    ancienne = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    croyance = {"valeur": valeur, "source": source, "minute": monde_minute, "confiance": confiance, **lieu}
    if attribut == "lieu" and (consommee := (ancienne or {}).get("hypothese_consommee")):
        date = min(croyance["minute"], croyance.get("origine", {}).get("minute", croyance["minute"]))
        directe = (source in ("vu", "entendu", "essai", "se_dit") and "origine" not in lieu
                   and ("minute" not in lieu or lieu["minute"] >= monde_minute))
        if valeur is None or not (directe or date > consommee["minute"]):
            croyance["hypothese_consommee"] = copy.deepcopy(consommee)
    esprit(monde, id)["croyances"].setdefault(sujet, {})[attribut] = croyance
    if attribut == "lieu" and personne_autre(monde, id, sujet) and valeur is not None:
        croyance.setdefault("mobilite", mobilite_crue(monde, id, sujet))
    if (id != "joueur" and attribut == "lieu" and source == "entendu" and valeur in monde.data["salles"]
            and (sujet == "joueur" or monde.objets.get(sujet, {}).get("type") == "personnage")):
        _retenir_presence(monde, id, sujet, valeur)
    if attribut == "lieu" and source in ("vu", "entendu") and valeur in monde.data["salles"]:
        # Le contexte d'une réponse retenue change avec un déplacement
        # réellement perçu de la personne, jamais avec une date, une autre
        # case dans la même salle ou la répétition d'un renseignement tiers.
        for reponse in esprit(monde, id).get("refus", ()):
            if reponse["operation"] != "enqueter_lieu" or reponse.get("objet") != sujet:
                continue
            repere = reponse.get("repere")
            if repere is None or repere["lieu"] != valeur:
                reponse["repere"] = {"lieu": valeur, "revision": (repere["revision"] if repere else 0) + 1}
    if attribut == "lieu":
        from .defense import approche_vue
        approche_vue(monde, id, sujet, ancienne or {}, croyance)
    if attribut == "eau" and source in ("vu", "essai"):
        # Une preuve propre postérieure dément l'avis durablement : le perdre de vue
        # ensuite ne doit pas ressusciter une ancienne prévision reçue.
        avis = [a for a in lire(monde, id)["croyances"].values() if "prevision" in a]
        propre = prevision_propre(monde, id) if avis else None
        if propre and propre["source"] in ("vu", "essai"):
            for a in avis:
                if propre["minute"] > a["prevision"]["minute"]:
                    del a["prevision"]
    from .social import reviser_dits
    if attribut != "prevision":  # Le fait dit est la menace, pas les coefficients de sa prévision.
        reviser_dits(monde, id, sujet, attribut, valeur, precedente=ancienne or {}, **lieu)
    if attribut == "lieu" and sujet in lire(monde, id)["recherches"] and valeur in monde.data["salles"]:
        # Un contenu positif nouveau rouvre ce lieu seul ; une répétition ou une absence,
        # même datée de nouveau, n'annule pas le résultat d'une recherche.
        from .deliberation import contact_recherche, indice_recherche
        if source == "vu" and (not ancienne or ancienne["valeur"] != valeur
                               or ancienne.get("case") != lieu.get("case")):
            contact_recherche(monde, id, sujet, valeur)
        indice_recherche(monde, id, valeur, sujet)
    if attribut == "etat" and (valeur.get("conscient") is False or valeur.get("reddition")):
        from .defense import constater_fin
        constater_fin(monde, id, sujet)
