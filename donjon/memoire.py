"""Porte des épisodes et des faits crus, au format historique.

S1 conserve les clés sauvegardées, l'ordre, le plafond et les crochets réentrants.
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


ATTRIBUTS_MATERIELS = frozenset({"etat", "fin", "verrouillee", "lumiere", "pieces"})
ATTRIBUTS_EAU_STATUTS = frozenset({"eau", "prevision", "statuts"})


def attribut_lecture(attribut):
    return attribut in ("emotion", "intention", "parole_doutee") or attribut.startswith("attitude:")


def lecture_non_perimee(monde, attribut, preuve):
    """Borne historique de lecture ; aucune disparition physique n'est inférée."""
    from .esprits import RECENT
    from .signes import ATTITUDE_MAX
    limite = RECENT if attribut in ("emotion", "intention", "parole_doutee") else ATTITUDE_MAX
    return monde.data["minutes"] - preuve["minute"] < limite


def lecture_utilisable(monde, observateur, attribut, preuve):
    """Admissibilité historique de la projection des lectures, sans identité Python."""
    return (observateur == "joueur" or attribut_lecture(attribut) and (
        preuve["source"] == "devine" or preuve["source"].startswith("dit:") and "signe" in preuve)
    ) and lecture_non_perimee(monde, attribut, preuve)


def lectures_joueur(monde):
    return copy.deepcopy(monde.data.get("lectures", {}))


def lecture_retenue(monde, observateur, sujet, attribut, signe):
    """Preuve brute pour la relecture, y compris lorsqu'elle vient de périmer."""
    return (copy.deepcopy(monde.data.get("lectures", {}).get(signe)) if observateur == "joueur"
            else fait_brut(monde, observateur, sujet, attribut))


def lectures_actives(monde, observateur):
    """Copies ordonnées, mêmes sources et bornes 30/120 minutes qu'avant S1i."""
    from .esprits import lire
    if observateur == "joueur":
        valeurs = [(c["personnage"], c.get("attribut", ""), c)
                   for c in monde.data.get("lectures", {}).values()]
    else:
        valeurs = [(x, a, c) for x, d in lire(monde, observateur)["croyances"].items()
                   for a, c in d.items() if attribut_lecture(a)]
    return [(x, a, copy.deepcopy(c)) for x, a, c in valeurs
            if lecture_utilisable(monde, observateur, a, c)]


def retenir_lecture_joueur(monde, signe, preuve):
    monde.data["lectures"][signe] = copy.deepcopy(preuve)


def tenter_lecture(monde, observateur, signe):
    """Consomme l'essai, échec compris, avant le jet ; cadence sauvegardée."""
    from .esprits import esprit
    from .signes import RELECTURE
    essais = (monde.data["signes_lus_joueur"] if observateur == "joueur"
              else esprit(monde, observateur)["signes_lus"])
    dernier = essais.get(signe)
    if dernier is not None and monde.data["minutes"] - dernier < RELECTURE:
        return False
    essais[signe] = monde.data["minutes"]
    return True


def preparer_suivi_signes(monde, observateur, episodes):
    """Migration historique sans apprentissage ni reconstitution du passé physique."""
    suivis = monde.data.setdefault("suivi_signes", {})
    suivi = suivis.get(observateur)
    if suivi is None or suivi.get("version") != 2:
        suivi = suivis[observateur] = {"version": 2, "retenus": {}, "conclusions": {}}
        for _, _, c in lectures_actives(monde, observateur):
            if c["signe"] in episodes:
                suivi["retenus"][c["signe"]] = episodes[c["signe"]]


def episode_signe_retenu(monde, observateur, signe, defaut=None):
    return monde.data.get("suivi_signes", {}).get(observateur, {}).get("retenus", {}).get(signe, defaut)


def conclusion_signe(monde, observateur, signe):
    return monde.data.get("suivi_signes", {}).get(observateur, {}).get("conclusions", {}).get(signe)


def conclure_signe(monde, observateur, signe, episode):
    monde.data["suivi_signes"][observateur]["conclusions"][signe] = episode


def retenir_episode_signe(monde, observateur, signe, episode):
    monde.data["suivi_signes"][observateur]["retenus"][signe] = episode


def mesure_eau(monde, id, salle):
    """Mesure retenue, avec niveau, pente et repère ; None sans preuve."""
    return fait_brut(monde, id, salle, "eau")


def mesures_eau(monde, id):
    """Preuves d'eau par sujet, dans l'ordre historique, sans compléter le réel."""
    from .esprits import lire
    return {s: copy.deepcopy(a["eau"]) for s, a in lire(monde, id)["croyances"].items()
            if "eau" in a}


def avis_eau(monde, id, salle):
    """Avis reçu brut : conviction, date observée et rang inchangés."""
    return fait_brut(monde, id, salle, "prevision")


def statuts_connus(monde, id, sujet):
    """Preuve sourcée ; [] est un démenti explicite, None une absence de preuve."""
    return fait_brut(monde, id, sujet, "statuts")


def etat_connu(monde, id, sujet):
    """Preuve d'état, ou None si absente ; les propriétés omises restent inconnues."""
    return fait_brut(monde, id, sujet, "etat")


def fin_connue(monde, id, sujet):
    """None : aucune preuve ; preuve avec valeur None : fin explicitement démentie.

    La source, la date et la désignation restent celles de la preuve historique.
    Aucun état réel ni aucune valeur par défaut ne complète une preuve partielle.
    """
    return fait_brut(monde, id, sujet, "fin")


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
    """Admission historique : même preuve composée et même ordre des conséquences.

    Eau : remplacement de la mesure entière, puis retrait durable des avis
    antérieurs à la prévision propre constatée. Prévisions et statuts :
    remplacement entier, sans fusion ; leurs réceptions pondérées passent
    respectivement par recevoir_prevision et recevoir_statuts ci-dessous.
    Les constats/savoirs directs gardent leur admission sans pondération.
    """
    from .esprits import lire, esprit, _retenir_presence
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


# Révision S1h : politiques historiques distinctes, sans nouvelle règle commune.


def prevision_propre(monde, id):
    """L'estimation et la qualité de ses preuves, borne comprise, sans les modifier."""
    from .esprits import poids_source
    from .eau import estimation, borner
    e = estimation(monde, id)
    if e is None:
        return None
    vues = [c for c in mesures_eau(monde, id).values() if c.get("niveau") is not None]
    ancre = max(vues, key=lambda c: (c["minute"], c["niveau"]))
    pente = max((c for c in vues if c.get("repere") is not None and c.get("montee") is not None),
                key=lambda c: (c["repere"][0], c["montee"]))
    e, borne = borner(monde, id, (ancre["minute"], ancre["niveau"], e[2]))
    preuves = [ancre, pente] + ([borne] if borne else [])
    faible = min(preuves, key=lambda c: poids_source(monde, id, c) * c["confiance"])
    minute = max(ancre["minute"], pente["repere"][0], borne["minute"] if borne else 0)
    return {"valeur": list(e), "minute": minute,
            "source": faible["source"], "confiance": faible["confiance"]}


def prevision(monde, id, salle):
    """Prévision retenue pour ce lieu : preuves propres ou avis, jamais une mesure inventée.

    Une estimation propre étayée plus récente dément l'ancien avis ; à défaut, poids × conviction
    départage, l'égalité gardant la croyance déjà acquise.
    """
    from .esprits import poids_source
    propre = prevision_propre(monde, id)
    recue = avis_eau(monde, id, salle)
    if recue is None:
        return propre
    if propre and (propre["source"] in ("vu", "essai") and propre["minute"] > recue["minute"]
                   or poids_source(monde, id, propre) * propre["confiance"]
                   > poids_source(monde, id, recue) * recue["confiance"]):
        return propre
    if type(recue["valeur"]) is not bool:
        from .eau import borner
        valeur, _ = borner(monde, id, recue["valeur"])
        return {**recue, "valeur": list(valeur)}
    return recue


def recevoir_prevision(monde, id, locuteur, noyau, rang, *, departage=False):
    """Révision historique : preuve propre postérieure, puis poids × conviction.

    Arrondi à douze décimales ; égalité refusée sauf départage de dispute.
    L'admission, la chronique puis la reconsidération gardent leur ordre.
    """
    from .esprits import poids_source, reconsiderer
    from .voix import source_dite
    from .pnj import _chroniquer
    actuelle = prevision(monde, id, noyau["objet"])
    candidate = {"valeur": noyau["prevision"], "minute": noyau["observe"],
                 "source": source_dite(monde, id, locuteur), "confiance": noyau["conviction"]}
    poids = round(poids_source(monde, id, candidate) * candidate["confiance"], 12)
    acquis = round(poids_source(monde, id, actuelle) * actuelle["confiance"], 12) if actuelle else 0
    if (actuelle and actuelle["source"] in ("vu", "essai") and actuelle["minute"] > candidate["minute"]
            or poids < acquis or poids == acquis and not departage):
        return "doute"
    admettre_fait(monde, id, noyau["objet"], "prevision", copy.deepcopy(candidate["valeur"]),
                  candidate["source"], candidate["confiance"], minute=candidate["minute"], rang=rang + 1)
    from .social import _qui
    _chroniquer(monde, id, f"{_qui(monde, id)} révise sa prévision de l'eau.", "social")
    monde.data["chronique"][-1]["changement_avis"] = "dit"
    reconsiderer(monde, id)
    return "crue"


def recevoir_statuts(monde, id, locuteur, sujet, valeurs, *, minute=None, confiance=.7):
    """Révision historique des statuts : date puis poids × conviction, égalité admise."""
    from .esprits import croyance, verifier_statuts, poids_source
    from .voix import source_dite
    verifier_statuts(monde, valeurs)
    source = source_dite(monde, id, locuteur)
    ancienne = croyance(monde, id, sujet, "statuts")
    minute = monde.data["minutes"] if minute is None else minute
    nouvelle = {"source": source, "confiance": confiance}
    if ancienne and (ancienne["minute"] > minute or
                     poids_source(monde, id, ancienne) * ancienne["confiance"] >
                     poids_source(monde, id, nouvelle) * confiance):
        return "dementi"
    admettre_fait(monde, id, sujet, "statuts", copy.deepcopy(valeurs), source, confiance, minute=minute)
    return "crue"


DETRESSE = ("peur", "crainte", "inquietude")


def detresse_retenue(m, observateur, sujet):
    """Besoin cru, sans péremption ni lecture privée ; perdre un signe ne le dément pas.

    Les anciennes parties conservent déjà les impressions datées : elles restent
    utilisables sans leur demander d'être à nouveau dans le champ de vision.
    """
    from .esprits import lire as esprit_lu
    crus = faits_connus(m, observateur, sujet)
    etat = fait_brut(m, observateur, sujet, "etat", {}).get("valeur", {})
    if etat.get("parti") or etat.get("mort") or etat.get("conscient") is False:
        return None
    if "detresse" in crus:
        return crus["detresse"] if crus["detresse"]["valeur"] else None
    anciennes = [c for a, c in crus.items()
                 if (a in ("emotion", "intention", "parole_doutee") or a.startswith("attitude:"))
                 and c.get("valeur") in DETRESSE and c.get("signe")]
    if anciennes:
        c = max(anciennes, key=lambda c: c.get("apprise", c["minute"]))
        return {"valeur": True, "source": c["source"], "minute": c["minute"],
                "preuve": {"canal": "lecture", "signe": c["signe"], "attribut": next(
                    a for a, v in crus.items() if v is c), "minute": c.get("apprise", c["minute"]),
                    "valeur": c["valeur"]}}
    # Une sauvegarde de l'ancien moteur peut porter la raison adoptée sans
    # avoir enregistré séparément son signe brut. Ne pas effacer cette raison.
    from .agendas import contrat_intention
    contrat = contrat_intention(m, observateur) or {}
    raison = (contrat.get("demande") or {}).get("raison")
    if raison == {"qui": sujet, "besoin": "peur"}:
        depuis = esprit_lu(m, observateur)["intention"]["depuis"]
        return {"valeur": True, "source": "devine", "minute": depuis,
                "preuve": {"canal": "adoption", "signe": "", "attribut": "", "minute": depuis, "valeur": "peur"}}
    return None


def retenir_detresses(m, observateur, signes):
    """Réviser seulement aux perceptions : preuve positive ou démenti discernable.

    Une expression corporelle absente est un calme vu seulement quand cette
    expression serait discernable. Un regard détourné ne contredit jamais une
    lecture d'attitude ; il faut une nouvelle lecture contradictoire du même signe.
    """
    from .esprits import croire, percus as objets_percus
    from .signes import SIGNES, _niveau_distance
    change = False
    positifs = {}
    ids = {s["id"] for s in signes}
    for s in signes:
        if s["signe"] in ("tremble", "fuit"):
            positifs[s["personnage"]] = ("vu", {"canal": "expression", "signe": s["id"],
                "attribut": "", "minute": m.data["minutes"], "valeur": s["signe"]})
    for sujet, a, c in lectures_actives(m, observateur):
        if c["valeur"] in DETRESSE and c["signe"] in ids and sujet not in positifs:
            positifs[sujet] = (c["source"], {"canal": "lecture", "signe": c["signe"],
                "attribut": a, "minute": c.get("apprise", c["minute"]), "valeur": c["valeur"]})
    for s in episodes(m, observateur, types=("detresse",)):
        if s["type"] == "detresse" and s["minute"] == m.data["minutes"] and s["qui"] not in positifs:
            positifs[s["qui"]] = ("entendu", {"canal": "appel", "signe": "", "attribut": "",
                "minute": s["minute"], "valeur": "appel"})
    vus = None
    sujets = set(positifs) | {x for x, d in faits_connus(m, observateur).items() if "detresse" in d}
    from .agendas import contrat_intention
    raison = ((contrat_intention(m, observateur) or {}).get("demande") or {}).get("raison")
    if raison and raison["besoin"] == "peur":
        sujets.add(raison["qui"])
    for sujet in sorted(sujets):
        crus = faits_connus(m, observateur, sujet)
        enregistre = crus.get("detresse")
        ancien = enregistre or detresse_retenue(m, observateur, sujet)
        source, preuve, valeur = None, None, True
        etat = fait_brut(m, observateur, sujet, "etat", {})
        if any(etat.get("valeur", {}).get(k) for k in ("parti", "mort")) or etat.get("valeur", {}).get("conscient") is False:
            source, valeur = etat["source"], False
            preuve = {"canal": "etat", "signe": "", "attribut": "etat", "minute": etat["minute"], "valeur": "indisponible"}
        elif sujet in positifs:
            source, preuve = positifs[sujet]
        elif ancien and ancien["valeur"]:
            p = ancien["preuve"]
            if p["canal"] == "lecture":
                revision = crus.get(p["attribut"], {})
                if (revision.get("signe") == p["signe"] and revision.get("valeur") not in DETRESSE
                        and revision.get("apprise", revision.get("minute", -1)) >= p["minute"]
                        and p["signe"] in ids):
                    source, valeur = revision["source"], False
                    preuve = {**p, "minute": revision["minute"], "valeur": revision["valeur"]}
            elif p["canal"] in ("expression", "appel"):
                if vus is None:
                    vus = objets_percus(m, observateur)[0]
                if sujet in vus:
                    niveau, distance_ = _niveau_distance(m, observateur, sujet)
                    regle = SIGNES["tremble"]
                    if niveau >= regle[2] and distance_ <= regle[3]:
                        source, valeur = "vu", False
                        preuve = {"canal": "calme", "signe": "", "attribut": "", "minute": m.data["minutes"], "valeur": "calme"}
        if preuve is None and ancien and not enregistre:
            source, preuve = ancien["source"], ancien["preuve"]
        if preuve is not None and (enregistre is None or ancien["valeur"] != valeur or valeur and any(
                preuve[k] != ancien["preuve"][k] for k in ("canal", "signe", "attribut"))):
            confiance = (crus.get(preuve["attribut"], {}).get("confiance", .5)
                         if preuve["canal"] in ("lecture", "adoption") else 1.0)
            croire(m, observateur, sujet, "detresse", valeur, source, confiance, preuve=preuve)
            from .deliberation import _poids_secours, calme_pour_secourir
            if (ancien is None or ancien["valeur"] != valeur) and (
                    raison and raison["besoin"] == "peur" and raison["qui"] == sujet
                    or valeur and calme_pour_secourir(m, observateur)
                    and _poids_secours(m, observateur, sujet) is not None):
                # Un démenti ne change le choix que si cette détresse portait
                # sa demande ; une naissance de secours exige sa propre
                # disponibilité. Mémoriser n'est pas réveiller sans recours.
                change = True
    return change


def auteurs_dangereux(monde, id, protege=None):
    """Violences connues, jamais une identité déduite d'un bruit ou d'une position réelle."""
    from .esprits import RECENT
    if id == "joueur":
        return list(dict.fromkeys(s["auteur"] for s in violences_joueur(monde)
                                  if not s.get("clos") and monde.data["minutes"] - s["minute"] < RECENT))
    resultat = []
    for a, cs in faits_connus(monde, id).items():
        if a == id or "violence" not in cs:
            continue
        for victime, s in cs["violence"]["valeur"].items():
            if (monde.data["minutes"] - s["minute"] < RECENT and s["menace"] and not s["clos"]
                    and (protege is None or victime == protege)):
                resultat.append(a)
                break
    return resultat


def violences_joueur(monde):
    """Preuves de coups perçus, dans l'ordre sauvegardé, sans accès au réel."""
    return copy.deepcopy(monde.data.get("violences_joueur", []))


def retenir_danger(monde, id, auteur, victime, minute, menace, operation, source):
    """Même rétention historique, hors du tampon des quarante épisodes."""
    from .esprits import RECENT
    ancien = _fait_stock(monde, id, auteur, "violence", {}).get("valeur", {})
    observations = {v: dict(d) for v, d in ancien.items()
                    if monde.data["minutes"] - d["minute"] < RECENT}
    observations[victime] = dict(minute=minute, menace=menace, operation=operation, clos=False)
    admettre_fait(monde, id, auteur, "violence", observations, source)


def clore_danger(monde, id, auteur):
    """Neutralisation constatée, conservée au réveil et après rechargement."""
    if id == "joueur":
        for s in monde.data.get("violences_joueur", []):
            if s["auteur"] == auteur:
                s["clos"] = True
        return
    c = _fait_stock(monde, id, auteur, "violence", {})
    for s in c.get("valeur", {}).values():
        s["clos"] = True


def retenir_coup_joueur(monde, auteur, operation):
    from .esprits import RECENT
    stock = monde.data.setdefault("violences_joueur", [])
    stock[:] = [s for s in stock if s["auteur"] != auteur
                and monde.data["minutes"] - s["minute"] < RECENT]
    stock.append(dict(type="subi", auteur=auteur, operation=operation, minute=monde.data["minutes"]))


def installer_signes(m):
    for cle, defaut in (("lectures", {}), ("signes_lus_joueur", {}), ("bilan_signes", {}),
                        ("tirages_lecture", 0), ("tirages_lecture_acteurs", {}), ("mesures_signes", {}), ("tons_percus", []), ("observations_joueur", [])):
        if cle not in m.data:
            m.data[cle] = copy.deepcopy(defaut)


def verifier_signes_retenus(monde):
    """Schémas subjectifs portés ; les occurrences physiques restent dans signes."""
    import math
    from .esprits import lire
    from .signes import SENS

    def dates(stock):
        return isinstance(stock, dict) and all(isinstance(k, str) and type(v) is int
                                               for k, v in stock.items())

    assert dates(monde.data.get("signes_lus_joueur", {})), "Essais de lecture invalides"
    for id in monde.data.get("esprits", {}):
        assert dates(lire(monde, id)["signes_lus"]), "Essais de lecture invalides"
    lectures = monde.data.get("lectures", {})
    assert isinstance(lectures, dict), "Lectures du joueur invalides"
    for signe, c in lectures.items():
        assert (isinstance(signe, str) and isinstance(c, dict)
                and {"valeur", "source", "minute", "confiance", "signe", "envers", "personnage"} <= set(c)
                <= {"valeur", "source", "minute", "confiance", "signe", "envers", "personnage", "attribut", "apprise", "episode"}
                and c["signe"] == signe and c["valeur"] in SENS and c["source"] == "devine"
                and type(c["minute"]) is int and type(c["confiance"]) in (float, int)
                and math.isfinite(c["confiance"]) and 0 <= c["confiance"] <= 1
                and isinstance(c["personnage"], str) and (c["envers"] is None or isinstance(c["envers"], str))
                and ("attribut" not in c or isinstance(c["attribut"], str) and attribut_lecture(c["attribut"]))
                and all(type(c[k]) is int for k in ("apprise", "episode") if k in c)), "Lecture du joueur invalide"
    suivis = monde.data.get("suivi_signes", {})
    assert isinstance(suivis, dict), "Suivi de signes invalide"
    for id, suivi in suivis.items():
        assert isinstance(id, str) and isinstance(suivi, dict), "Suivi de signes invalide"
        # Les formats antérieurs à v2 sont abandonnés par preparer_suivi_signes,
        # sans reconstruire ni valider une histoire qui n'a pas été conservée.
        if suivi.get("version") == 2:
            assert (set(suivi) == {"version", "retenus", "conclusions"}
                    and dates(suivi["retenus"]) and dates(suivi["conclusions"])), "Suivi de signes invalide"
    violences = monde.data.get("violences_joueur", [])
    assert isinstance(violences, list), "Violences du joueur invalides"
    for s in violences:
        assert (isinstance(s, dict) and {"type", "auteur", "operation", "minute"} <= set(s)
                <= {"type", "auteur", "operation", "minute", "clos"}
                and s["type"] == "subi" and isinstance(s["auteur"], str) and bool(s["auteur"])
                and s["operation"] in ("frapper", "assommer", "pousser")
                and type(s["minute"]) is int and type(s.get("clos", False)) is bool), "Violence du joueur invalide"


# S1j : dits, audiences connues et ancrage initial ; politiques historiques.

DITS_MAX = 512


def dits_retenus(monde, observateur):
    """Copie du suivi subjectif des valeurs dites et audiences connues.

    Aucune date ou source absente du registre historique n'est reconstruite.
    Une valeur entendue n'est ni une valeur adoptée ni une preuve de vérité.
    """
    from .esprits import lire
    return copy.deepcopy(lire(monde, observateur)["faits_dits"])


def faits_initiaux(monde, observateur):
    """Copie de l'ancrage de départ encore inchangé de cet observateur."""
    from .esprits import lire
    return copy.deepcopy(lire(monde, observateur)["faits_initiaux"])


def paroles_retenues(monde, observateur):
    """Occurrences entendues du tampon, avec locuteur perçu et mots historiques."""
    return episodes(monde, observateur, types=("parole",))


def installation_dits(monde, observateur):
    """Présence des formats avant installation générique de l'esprit, sans mutation."""
    ancien = monde.data.get("esprits", {}).get(observateur, {})
    return "faits_initiaux" not in ancien, "faits_dits" not in ancien


def migrer_auditeurs_dits(monde, observateur):
    """Ancienne liste d'auditeurs : mêmes valeurs, ordre et copies par destinataire."""
    from .esprits import esprit
    for fait in esprit(monde, observateur)["faits_dits"].values():
        if isinstance(fait["dit_a"], list):
            fait["dit_a"] = {a: copy.deepcopy(fait["valeur"]) for a in fait["dit_a"]}


def verifier_dits(monde, observateur):
    """Schéma historique : contrôle joueur minimal, contrôle PNJ complet."""
    from .esprits import lire
    e = lire(monde, observateur)
    if observateur == "joueur":
        assert isinstance(e["faits_dits"], dict) and len(e["faits_dits"]) <= DITS_MAX, "Faits dits du joueur invalides"
        return
    assert isinstance(e["faits_initiaux"], dict) and all(isinstance(k, str) for k in e["faits_initiaux"]), "Faits initiaux invalides"
    assert (isinstance(e["faits_dits"], dict) and len(e["faits_dits"]) <= DITS_MAX
            and all(isinstance(k, str) and isinstance(v, dict) and {"valeur", "dit_a"} <= set(v)
                    and set(v) <= {"valeur", "dit_a", "entendu_a", "valeur_inconnue"}
                    and isinstance(v.get("valeur_inconnue", False), bool)
                    and isinstance(v["dit_a"], dict) and all(isinstance(a, str) for a in v["dit_a"])
                    and isinstance(v.get("entendu_a", {}), dict)
                    and all(isinstance(a, str) and isinstance(valeurs, list)
                            for a, valeurs in v.get("entendu_a", {}).items())
                    for k, v in e["faits_dits"].items())), "Faits dits invalides"


def _cle(fait):
    import json
    return json.dumps(fait, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def faits_dits(noyau):
    """Identités et valeurs transmises, sans texte, date, preuve ni qualité de la source.

    Les constats et les affirmations partagent la même identité de propriété.
    Un geste reste un fait distinct d'un état ; son lieu dit est une valeur, pas
    la date ou la case depuis lesquelles le témoin l'a appris.
    """
    t = noyau["type"]
    if t == "compte_rendu":
        return [(_cle({"type": t, "charge": noyau["charge"]}), noyau["issue"])]
    if t in ("affirmation", "constat", "avis"):
        sujet = noyau.get("sujet", noyau.get("objet"))
        attribut, valeur = noyau["attribut"], noyau["valeur"]
        if attribut == "lieu" and "possession" in noyau.get("details", {}):
            # Les droits constituent une preuve supplémentaire : le contenu
            # dit aussi le lieu nu. Connaître seulement ce lieu n'atteste pas
            # les droits ; connaître les droits ne fait pas oublier le lieu.
            return [(_cle([sujet, attribut]), valeur),
                    (_cle([sujet, attribut, "possession"]),
                     {"valeur": valeur, "possession": noyau["details"]["possession"]})]
        if attribut == "etat":
            return [(_cle([sujet, attribut, k]), v) for k, v in sorted(valeur.items())]
        return [(_cle([sujet, attribut]), valeur)]
    if t == "intention_lue":
        return [(_cle([noyau["auteur"], "intention"]), {"valeur": "guet", "envers": noyau["objet"]})]
    if t in ("absence", "mort_vue", "vu_porter"):
        sujet, attribut, valeur = (noyau["objet"], "etat", {"mort": True}) if t == "mort_vue" else (
            noyau["objet"], "lieu", noyau.get("auteur") if t == "vu_porter" else None)
        return faits_dits({"type": "affirmation", "sujet": sujet, "attribut": attribut, "valeur": valeur})
    identite = {k: noyau[k] for k in ("type", "auteur", "objet", "operation", "locuteur", "sujet", "attribut", "victime")
                if k in noyau}
    valeur = {k: noyau[k] for k in ("montant",) if k in noyau}
    faits = [(_cle(identite), valeur)]
    if "lieu" in noyau:
        faits.append((_cle([noyau["objet"], "lieu"]), noyau["lieu"]["valeur"]))
    return faits


def installer_faits_initiaux(monde, id, *, perception=False):
    """Ancrage de provenance de la scène de départ, distinct des croyances.

    L'installation du contrat sur une ancienne sauvegarde n'invente pas de
    transfert à partir de ses inventaires actuels. Le passé absent ne peut pas
    être reconstruit. Aucun savoir sur un tiers n'est ajouté aux croyances.
    """
    from .esprits import esprit, preuve_possession, faits_materiels
    e = esprit(monde, id)
    initiaux = e["faits_initiaux"]
    for sujet in monde.objets:
        p = preuve_possession(monde, sujet)
        if p:
            for attribut, valeur, details in faits_materiels(monde, sujet):
                # L'inventaire de départ a une provenance matérielle ; celui
                # qui le porte connaît aussi l'état de ses propres biens.
                # Aucune propriété cachée d'un bien tiers n'est un savoir.
                if attribut == "lieu" or p["porteur"] == id:
                    initiaux.update(copy.deepcopy(faits_dits({"type": "constat", "objet": sujet,
                        "attribut": attribut, "valeur": valeur, "details": details})))
    for sujet, attributs in faits_connus(monde, id).items():
        for attribut, c in attributs.items():
            # Les anciennes localisations sans droits ne deviennent pas une
            # nouvelle par la seule installation de la preuve de possession.
            localisation_ancienne = attribut == "lieu" and "possession" not in c
            if c["source"] != "savoir" and not (c["source"] == "vu" and (perception or localisation_ancienne)):
                continue
            noyau = {"type": "affirmation", "sujet": sujet, "attribut": attribut,
                     "valeur": c["valeur"], "details": c}
            initiaux.update(copy.deepcopy(faits_dits(noyau)))
            if attribut == "lieu" and sujet in monde.objets and c["valeur"] == monde.objets[sujet]["lieu"]:
                p = preuve_possession(monde, sujet, precedente=c)
                if p:
                    initiaux.update(copy.deepcopy(faits_dits({**noyau, "details": {"possession": p}})))


def fait_initial(monde, id, noyau):
    from .esprits import lire
    initiaux = lire(monde, id)["faits_initiaux"]
    if noyau.get("attribut") == "lieu":
        cle = _cle([noyau.get("objet", noyau.get("sujet")), "lieu"])
        if cle in initiaux and initiaux[cle] == noyau["valeur"]:
            return True
    return all(cle in initiaux and initiaux[cle] == valeur for cle, valeur in faits_dits(noyau))


def transmission_attestee(monde, id, auditeur, noyau):
    """Preuve positive du contenu partagé ; le registre plein n'en est pas une."""
    from .esprits import lire
    registre = lire(monde, id)["faits_dits"]
    return all(cle in registre and (
               auditeur in registre[cle]["dit_a"] and registre[cle]["dit_a"][auditeur] == valeur
               or valeur in registre[cle].get("entendu_a", {}).get(auditeur, []))
               for cle, valeur in faits_dits(noyau))


def deja_dit(monde, id, auditeur, noyau):
    from .esprits import lire
    registre = lire(monde, id)["faits_dits"]
    return all((cle in registre and auditeur in registre[cle]["dit_a"]
                and registre[cle]["dit_a"][auditeur] == valeur)
               or (cle in registre and valeur in registre[cle].get("entendu_a", {}).get(auditeur, []))
               # Une nouvelle identité ne peut plus être suivie à saturation.
               or cle not in registre and len(registre) >= DITS_MAX
               for cle, valeur in faits_dits(noyau))


def retenir_dit(monde, id, auditeur, noyau):
    from .esprits import esprit
    registre = esprit(monde, id)["faits_dits"]
    for cle, valeur in faits_dits(noyau):
        if cle not in registre and len(registre) >= DITS_MAX:
            continue
        if cle not in registre:
            registre[cle] = {"valeur": copy.deepcopy(valeur), "dit_a": {}}
        registre[cle]["valeur"] = copy.deepcopy(valeur)
        registre[cle].pop("valeur_inconnue", None)
        registre[cle]["dit_a"][auditeur] = copy.deepcopy(valeur)


def retenir_audience(monde, audience):
    from .esprits import esprit
    for observateur, autre, noyau in audience:
        registre = esprit(monde, observateur)["faits_dits"]
        for cle, valeur in faits_dits(noyau):
            if cle not in registre and len(registre) < DITS_MAX:
                registre[cle] = {"valeur": None, "valeur_inconnue": True, "dit_a": {}}
            if cle in registre:
                # Deux positions contraires peuvent avoir été entendues sans
                # que l'une efface l'autre ni la position personnellement dite.
                valeurs = registre[cle].setdefault("entendu_a", {}).setdefault(autre, [])
                if valeur not in valeurs:
                    valeurs.append(copy.deepcopy(valeur))


def reviser_dits(monde, id, sujet, attribut, valeur, precedente=None, **details):
    """Seul un changement appris par le destinataire rouvre ce qui lui a été dit.

    La dernière valeur crue par le locuteur sert aussi aux conclusions dérivées
    (menace). Ses changements ne suppriment pas les valeurs dites aux autres.
    """
    from .esprits import lire, esprit
    if attribut == "intention":
        valeur = {"valeur": valeur, "envers": details.get("envers")}
    registre = lire(monde, id)["faits_dits"]
    if id != "joueur":
        initiaux = esprit(monde, id)["faits_initiaux"]
        for cle, v in faits_dits({"type": "affirmation", "sujet": sujet, "attribut": attribut,
                                  "valeur": valeur, "details": details}):
            lieu_change = (attribut == "lieu" and (
                _cle([sujet, attribut]) in initiaux and initiaux[_cle([sujet, attribut])] != valeur
                or precedente and precedente["valeur"] != valeur))
            if lieu_change or cle in initiaux and initiaux[cle] != v:
                initiaux.pop(cle, None)
                # Les deux identités partagent le même ancrage de départ.
                if attribut == "lieu":
                    initiaux.pop(_cle([sujet, attribut]), None)
                    initiaux.pop(_cle([sujet, attribut, "possession"]), None)
    avant = {}
    if precedente:
        ancienne = ({"valeur": precedente["valeur"], "envers": precedente.get("envers")}
                    if attribut == "intention" else precedente["valeur"])
        avant = dict(faits_dits({"type": "affirmation", "sujet": sujet, "attribut": attribut,
                                "valeur": ancienne, "details": precedente}))
    for cle, v in faits_dits({"type": "affirmation", "sujet": sujet, "attribut": attribut,
                             "valeur": valeur, "details": details}):
        if precedente is None and registre.get(cle, {}).get("valeur_inconnue"):
            # Le contenu entendu n'était pas sa propre conclusion. La première
            # conclusion calculée ne prouve donc aucun changement appris.
            registre[cle]["valeur"] = copy.deepcopy(v)
            registre[cle].pop("valeur_inconnue")
            continue
        if precedente is None and cle not in registre:
            # Première conclusion dérivée : aucun changement connu. La suivre
            # empêche qu'une même conclusion réaffirmée rouvre un avis refusé.
            if len(registre) < DITS_MAX:
                esprit(monde, id)["faits_dits"][cle] = {"valeur": copy.deepcopy(v), "dit_a": {}}
            continue
        connue = cle in avant if precedente is not None else cle in registre
        ancienne = avant.get(cle) if precedente is not None else registre.get(cle, {}).get("valeur")
        if cle in registre:
            registre[cle]["valeur"] = copy.deepcopy(v)
            registre[cle].pop("valeur_inconnue", None)
        if connue and ancienne == v:
            continue
        for e in monde.data.get("esprits", {}).values():
            fait = e.get("faits_dits", {}).get(cle, {})
            dits = fait.get("dit_a", {})
            if id in dits and dits[id] != v:
                del dits[id]
            entendus = fait.get("entendu_a", {})
            if id in entendus:
                entendus[id] = [valeur for valeur in entendus[id] if valeur == v]


def migrer_dits(monde, id):
    """Reprendre ce qui reste des anciens suivis ; les souvenirs déjà perdus sont irrécupérables."""
    from .esprits import esprit
    from .social import NOUVELLES
    e = esprit(monde, id)
    for s in episodes(monde, id):
        if s["type"] == "dit" and "valeur" in s:
            retenir_dit(monde, id, s["a"], {"type": "affirmation", **{k: s[k] for k in ("sujet", "attribut", "valeur")}})
        elif s["type"] in NOUVELLES or s["type"] == "rumeur":
            for a in s.get("dit_a", []):
                retenir_dit(monde, id, a, s["evenement"] if s["type"] == "rumeur" else s)
    for sujet, attributs in faits_connus(monde, id).items():
        for attribut, c in attributs.items():
            for a in c.get("confie", {}).get("dit_a", []):
                retenir_dit(monde, id, a, {"type": "affirmation", "sujet": sujet, "attribut": attribut,
                                         "valeur": c["confie"]["valeur"]})


# Identités vocales et nominales : format et rétention historiques de S1j.
def voix_connues(monde, observateur):
    """Voix reliées à leur porteur par cet observateur, sans apprendre ni créer."""
    from .esprits import lire
    return list(monde.data.get('voix_connues', []) if observateur == 'joueur'
                else lire(monde, observateur)['voix'])


def _voix_entendues_stock(monde, observateur, *, ecrire=False):
    from .esprits import esprit, lire
    if observateur == 'joueur':
        return (monde.data.setdefault('voix_entendues', {}) if ecrire
                else monde.data.get('voix_entendues', {}))
    return (esprit if ecrire else lire)(monde, observateur)['voix_entendues']


def voix_entendues(monde, observateur):
    """Signature privée, date, rang et noms rapportés ; jamais une identité déduite."""
    return copy.deepcopy(_voix_entendues_stock(monde, observateur))


def noms_retenus(monde, observateur):
    """Noms appris explicitement ; les savoirs du scénario restent dans les faits."""
    from .esprits import lire
    return list(monde.data.get('noms_connus', []) if observateur == 'joueur'
                else lire(monde, observateur)['noms'])


def retenir_nom(monde, observateur, autre):
    from .esprits import esprit
    from .noms import connait
    if connait(monde, observateur, autre):
        return False
    noms = (monde.data['noms_connus'] if observateur == 'joueur'
            else esprit(monde, observateur)['noms'])
    noms.append(autre)
    return True


def installer_noms_joueur(monde):
    monde.data.setdefault('noms_connus', list(monde.data.get('scenario', {}).get('noms_connus', [])))


def installation_voix(monde, observateur):
    return 'voix' not in monde.data['esprits'].get(observateur, {})


def installer_voix_initiales(monde, observateur, personnages):
    from .esprits import esprit
    esprit(monde, observateur)['voix'] = sorted(
        x for x, attributs in faits_connus(monde, observateur).items()
        if x in personnages and x != observateur
        and any(c.get('source') == 'savoir' for c in attributs.values()))


def installer_voix_joueur(monde):
    monde.data.setdefault('voix_connues', [])
    monde.data.setdefault('voix_entendues', {})


def echange_retenu(monde, observateur):
    from .esprits import lire
    return copy.deepcopy(lire(monde, observateur)['echange'])


def _retenir_voix(monde, qui, signature, minute=None):
    """Il retient une voix inconnue entendue à ``minute`` (maintenant par défaut) ; renvoie ce qu'il
    en retient."""
    from .voix import VOIX_MAX
    minute = monde.data["minutes"] if minute is None else minute
    voix = _voix_entendues_stock(monde, qui, ecrire=True)
    entree = voix.get(signature)
    if entree is None:
        entree = voix[signature] = {"minute": minute, "se_dit": None, "mefiance": False,
                                    "n": 1 + max((e["n"] for e in voix.values()), default=0)}
        for vieille in sorted(voix, key=lambda s: (voix[s]["minute"], voix[s]["n"]))[:max(0, len(voix) - VOIX_MAX)]:
            del voix[vieille]
    entree["minute"] = max(entree["minute"], minute)
    return entree


def retenir_voix(monde, observateur, signature, minute=None):
    """Rafraîchit l'audition et applique l'éviction historique ; rend une copie."""
    return copy.deepcopy(_retenir_voix(monde, observateur, signature, minute))


def retenir_pretention_vocale(monde, observateur, signature, nom, *, mefiance=False):
    entree = _retenir_voix(monde, observateur, signature)
    entree['se_dit'] = nom
    if mefiance:
        entree['mefiance'] = True


def retenir_mefiance_vocale(monde, observateur, signature):
    _retenir_voix(monde, observateur, signature)['mefiance'] = True


def retenir_appellation_vocale(monde, observateur, signature, nom):
    entree = _retenir_voix(monde, observateur, signature)
    if entree['se_dit'] or entree['mefiance'] or entree.get('appelee') == nom:
        return False
    entree['appelee'] = nom
    return True


def reconnaitre_voix(monde, qui, autre):
    """``qui`` connaît désormais la voix d'``autre`` : il l'a entendu parler en sachant que c'était
    lui. Il la compare à ce que les voix inconnues lui ont dit : la voix d'``autre`` s'était dite
    quelqu'un d'autre, ou il s'en méfiait, il se méfie désormais d'``autre`` ; elle s'était
    dite ``autre``, c'était bien lui, ce qu'il en croyait sur sa parole devient un constat ; une
    autre voix s'était dite ``autre``, il sait qu'on lui a menti, sans savoir qui."""
    from .esprits import esprit, memoriser
    from .voix import connait_nom, apprendre_nom
    connues = monde.data.setdefault("voix_connues", []) if qui == "joueur" else esprit(monde, qui)["voix"]
    if autre == qui or autre in connues:
        return
    connues.append(autre)
    voix = _voix_entendues_stock(monde, qui, ecrire=True)
    entree = voix.pop(autre, None)
    if entree and entree['se_dit'] not in (None,autre) and not entree['mefiance'] \
            and not connait_nom(monde,qui,autre) and not connait_nom(monde,qui,entree['se_dit']):
        voix[autre] = entree  # Reconnaître le corps ne réfute pas un nom qu'on n'a pas encore relié.
        entree = None
    if entree and not entree["mefiance"] and autre in (entree["se_dit"], entree.get("appelee")):
        apprendre_nom(monde, qui, autre)
    if qui == "joueur":
        return  # Le joueur juge lui-même : ce qu'il entend s'affiche (``nom_pour_joueur``).
    if entree and (entree["mefiance"] or entree["se_dit"] not in (None, autre)):
        memoriser(monde, qui, {"type": "imposture", "locuteur": autre, "se_disait": entree["se_dit"]})
    elif entree and entree["se_dit"] == autre:
        reconnaitre_localisation_vocale(monde, qui, autre)
    if entree and not entree["mefiance"] and autre in (entree["se_dit"], entree.get("appelee")):
        apprendre_nom(monde, qui, autre)  # C'était bien lui : son nom ne s'oublie pas avec la voix inconnue.
    for signature, x in voix.items():
        if connait_nom(monde,qui,autre) and x["se_dit"] == autre and not x["mefiance"]:
            x["mefiance"] = True
            memoriser(monde, qui, {"type": "imposture", "se_disait": autre})
            reconnaitre_localisation_vocale(monde, qui, autre, imposture=True)


def retenir_echange(monde, id, parole):
    """Un PNJ garde en tête la parole nette qu'il vient de saisir, le temps d'un échange
    (``ECHANGE``) : c'est par elle qu'il reliera les voix qui suivent (``lier``). Renvoie celles
    d'avant, encore de l'échange."""
    from .esprits import esprit
    from .voix import ECHANGE, ECHANGE_MAX
    e = esprit(monde, id)
    recentes = [b for b in e["echange"] if 0 <= parole["instant"] - b["instant"] <= ECHANGE]
    e["echange"] = [*recentes, copy.deepcopy(parole)][-ECHANGE_MAX:]
    return copy.deepcopy(recentes)


def verifier_echange(echange):
    from .voix import ECHANGE_MAX
    assert isinstance(echange, list) and len(echange) <= ECHANGE_MAX and all(
        isinstance(b, dict) and set(b) == {"instant", "auteur", "a", "noms"} and type(b["instant"]) is int
        and isinstance(b["auteur"], str) and isinstance(b["a"], list) and isinstance(b["noms"], list)
        and all(isinstance(x, str) for x in [*b["a"], *b["noms"]]) for b in echange), "Échange retenu invalide"


def verifier_entrees(voix):
    from .voix import CHAMPS_VOIX, OPTIONNELS
    assert isinstance(voix, dict) and all(
        isinstance(s, str) and isinstance(e, dict) and CHAMPS_VOIX <= set(e) <= CHAMPS_VOIX | OPTIONNELS
        and type(e["minute"]) is int and (e["se_dit"] is None or isinstance(e["se_dit"], str))
        and isinstance(e.get("appelee", ""), str) and type(e["mefiance"]) is bool
        and type(e["n"]) is int and e["n"] >= 1 for s, e in voix.items()), "Voix entendues invalides"
    assert len({e["n"] for e in voix.values()}) == len(voix), "Voix entendues invalides"


def verifier_identite_vocale(monde, observateur):
    from .esprits import lire
    e = lire(monde, observateur) if observateur != 'joueur' else None
    connues = monde.data.get('voix_connues', []) if observateur == 'joueur' else e['voix']
    assert isinstance(connues, list) and all(isinstance(x, str) for x in connues) \
        and len(set(connues)) == len(connues), 'Voix connues invalides'
    verifier_entrees(_voix_entendues_stock(monde, observateur))
    if observateur != 'joueur':
        verifier_echange(e['echange'])
        noms = e['noms']
        assert isinstance(noms, list) and all(isinstance(x, str) for x in noms) \
            and len(set(noms)) == len(noms), 'Noms retenus invalides'


def verifier_noms_joueur(monde):
    noms = monde.data.get('noms_connus', [])
    assert isinstance(noms, list) and all(isinstance(x, str) for x in noms) \
        and len(set(noms)) == len(noms), 'Noms appris invalides'


# --- Réponses retenues : stockage et prédicats historiques inchangés ---

def reponses_retenues(monde, id):
    """Copies profondes ordonnées, sans péremption ni création d'esprit.

    Les décisions de réouverture restent celles de deliberation.tient et
    pnj_propositions.refus_tient : lire n'acquitte ni ne réarme une demande.
    """
    from .esprits import lire
    return copy.deepcopy(lire(monde, id).get('refus', []))


def installer_refus_projetes(monde, id, reponses):
    """Installe les réponses de l'observateur dans une projection de devis."""
    from .esprits import esprit
    esprit(monde, id)['refus'] = copy.deepcopy(reponses)


def retenir_cause_derniere_reponse(monde, id, cause):
    """Associe le contexte effectivement interrogé à la dernière réponse."""
    from .esprits import lire
    lire(monde, id)['refus'][-1]['cause'] = copy.deepcopy(cause)


def acquitter_contre_offre_service(monde, id, pour, nourriture):
    """La prestation accomplie acquitte seulement la condition convenue."""
    from .esprits import lire
    for refus in lire(monde, id)['refus']:
        offre = refus.get('contre_offre')
        if offre and offre['debiteur'] == pour and offre['condition'] == {
                'type': 'tache', 'condition': {'objet': nourriture, 'servir': pour}}:
            refus['condition_tenue'] = True


def lever_refus_service_constate(monde, id, beneficiaire):
    """Le service réellement constaté lève les seuls refus sociaux de ce tiers."""
    from .esprits import lire
    e = lire(monde, id)
    e['refus'][:] = [s for s in e['refus'] if not (
        s['de'] == beneficiaire and s['raison'] in ('mefiance', 'rancune'))]


def retenir_refus(monde, id, autre, operation, raison, souvenir=True, **detail):
    """``autre`` refuse à ``id`` cette demande (``operation`` sur ``objet``, ou ``besoin`` pour « as-tu… ? ») :
    il s'en souvient (``souvenir``), et retient cette réponse à la place de la précédente pour la même
    demande, avec, quand le refus a une cause, ce qu'il croit alors de ses moyens (``moyens_crus``).
    « Qui va là ? » n'est pas un refus : il s'est nommé, il redemande."""
    from .esprits import lire, esprit, memoriser
    from .deliberation import DETAILS_REFUS, CAUSES, _meme_demande, moyens_crus
    detail = {k: copy.deepcopy(v) for k, v in detail.items() if k in DETAILS_REFUS and v is not None}
    historiques = []
    repere = None
    if operation == "enqueter_lieu":
        for precedent in lire(monde, id)["refus"]:
            if _meme_demande(precedent, autre, (operation,), detail.get("objet"), detail.get("besoin")):
                if precedent.get("repere"):
                    repere = dict(precedent["repere"])
                historiques.extend(f for f in precedent.get("cause", []) if f[0] == "lieu_appris")
                if precedent.get("information"):
                    historiques.append(["lieu_appris", detail.get("objet"), precedent["information"]["lieu"], None])
    if souvenir:
        memoriser(monde, id, {"type": "refus", "de": autre, "operation": operation, "raison": raison,
                              **{k: v for k, v in detail.items() if k in ("objet", "besoin")}})
    if raison == "qui_va_la":
        return
    oublier_refus(monde, id, autre, operation, detail.get("objet"), detail.get("besoin"), mandat=detail.get("mandat"))
    if operation == "acheter":
        # L'achat est la nouvelle réponse à cette demande de bien. À minute
        # égale, l'ancien refus gratuit ne doit pas cacher celui du marché.
        oublier_refus(monde, id, autre, "demander", detail.get("objet"), detail.get("besoin"))
    s = {"de": autre, "operation": operation, "raison": raison, "minute": monde.data["minutes"], **detail}
    if historiques:
        s["cause"] = historiques
    if operation == "enqueter_lieu":
        if repere is None:
            c = fait_brut(monde, id, detail.get('objet'), 'lieu')
            lieu = (c["valeur"] if c and c["source"] in ("vu", "entendu")
                    and c["valeur"] in monde.data["salles"] else (detail.get("information") or {}).get("lieu"))
            if lieu is not None:
                repere = {"lieu": lieu, "revision": 0}
        if repere is not None:
            s["repere"] = repere
    if operation == "acheter" and detail.get("prix") and detail.get("objet"):
        from .pnj_propositions import entrees_refus
        s["offre"] = entrees_refus(monde, id, autre, detail["objet"],
                                   {"type": "pieces", "montant": detail["prix"]})
        if raison == "refus":
            s["raison"] = "persuasion"  # Un achat refusé est déjà une offre, pas une demande gratuite.
    if (raison in CAUSES or operation in ("enqueter_lieu", "reclamer_dette")) and "contre_offre" not in s:
        s["cause"] = moyens_crus(monde, id, s)
    esprit(monde, id)["refus"].append(s)
    intention = lire(monde, id)["intention"]
    if operation in ("demander", "acheter") and detail.get("objet") and intention:
        esprit(monde, id)["demande_refusee"] = {"de": autre, "objet": detail["objet"],
                                                "besoin": intention["motif"]}


def oublier_refus(monde, id, autre, operation, objet=None, besoin=None, *, mandat=None):
    """La demande accordée (ou refusée de nouveau) : la réponse retenue ne vaut plus."""
    from .esprits import esprit
    e = esprit(monde, id)
    e["refus"] = [s for s in e["refus"] if not (s["de"] == autre and s["operation"] == operation
                                                 and s.get("objet") == objet and s.get("besoin") == besoin
                                                 and s.get("mandat") == mandat)]

def _contre_offre_valide(monde, id, refus):
    from .deliberation import condition_valide
    o = refus["contre_offre"]
    if (not isinstance(o, dict) or set(o) != {"etat", "debiteur", "creancier", "condition", "contrepartie"}
            or o["etat"] != "offre" or o["debiteur"] != refus["de"] or o["creancier"] != id
            or o["contrepartie"] not in ({"type": "objet", "objet": refus.get("objet")},
                                         {"type": "part", "objet": refus.get("objet")})):
        return False
    c = o["condition"]
    return (isinstance(c, dict) and (
        set(c) == {"type", "montant"} and c["type"] == "pieces" and type(c["montant"]) is int and c["montant"] > 0
        or set(c) == {"type", "condition"} and c["type"] == "tache"
        and isinstance(c["condition"], dict) and c["condition"].get("servir") == o["debiteur"]
        and condition_valide(monde, c["condition"])))

def verifier_refus(monde, id):
    from .esprits import lire
    e = lire(monde, id)
    from .deliberation import DETAILS_REFUS
    assert isinstance(e.get("refus", []), list) and all(
        isinstance(s, dict) and set(s) <= {"de", "operation", "raison", "minute", "cause", *DETAILS_REFUS}
        and isinstance(s["de"], str) and isinstance(s["operation"], str) and isinstance(s["raison"], str)
        and type(s["minute"]) is int and type(s.get("prix", 0)) is int
        and type(s.get("condition_tenue", False)) is bool
        and ("repere" not in s or isinstance(s["repere"], dict)
             and set(s["repere"]) == {"lieu", "revision"}
             and s["repere"]["lieu"] in monde.data["salles"]
             and type(s["repere"]["revision"]) is int and s["repere"]["revision"] >= 0)
        and ("information" not in s or isinstance(s["information"], dict)
             and {"lieu", "minute", "source"} <= set(s["information"]) <= {"lieu", "minute", "source", "origine"}
             and s["information"]["lieu"] in monde.data["salles"]
             and type(s["information"]["minute"]) is int
             and isinstance(s["information"]["source"], str)
             and ("origine" not in s["information"] or isinstance(s["information"]["origine"], dict)
                  and set(s["information"]["origine"]) == {"source", "minute"}
                  and isinstance(s["information"]["origine"]["source"], str)
                  and type(s["information"]["origine"]["minute"]) is int))
        and ("contre_offre" not in s or _contre_offre_valide(monde, id, s))
        and isinstance(s.get("cause", []), list) and all(isinstance(f, list) and len(f) == 4 for f in s.get("cause", []))
        and ("offre" not in s or isinstance(s["offre"], dict) and set(s["offre"]) == {"cause", "gain"}
             and isinstance(s["offre"]["gain"], (int, float)) and s["offre"]["gain"] >= 0
             and isinstance(s["offre"]["cause"], list)
             and all(isinstance(f, list) and len(f) == 4 for f in s["offre"]["cause"]))
        for s in e.get("refus", [])
    ), "Refus retenus de PNJ invalides"


# --- Recours : vues sans acquittement, opérations aux instants historiques ---

def demande_refusee(monde, id):
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['demande_refusee'])


def propositions_tentees(monde, id):
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['recours_propositions'])


def services_tentes(monde, id):
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['recours_services'])


def intermediaires_retenus(monde, id):
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['recours_intermediaires'])


def service_en_cours(monde, id):
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['service_en_cours'])


def retenir_service_tente(monde, id, tentative):
    """Une tentative par tiers/besoin, même si le devis échoue.

    Le prédicat historique (identité du refus, opération et minute) reste
    évalué par pnj_propositions ; ni cette porte ni une lecture ne le réarment.
    """
    from .esprits import lire
    stock = lire(monde, id)['recours_services']
    stock[:] = [s for s in stock if (s['de'], s['besoin']) != (tentative['de'], tentative['besoin'])]
    stock.append(copy.deepcopy(tentative))


def entreprendre_service(monde, id, demande, condition):
    from .esprits import lire
    lire(monde, id)['service_en_cours'] = copy.deepcopy({**demande, 'condition': condition})


def clore_service(monde, id):
    from .esprits import lire
    lire(monde, id)['service_en_cours'] = None


def restaurer_services_devises(monde, id, tentatives, service):
    """Annule le seul devis de service supplanté par une commission moins chère."""
    from .esprits import lire
    e = lire(monde, id)
    e['recours_services'][:] = copy.deepcopy(tentatives)
    e['service_en_cours'] = copy.deepcopy(service)


def retenir_intermediaire(monde, id, tentative):
    """Publie la commission choisie, jamais ses candidats de devis."""
    from .esprits import lire
    lire(monde, id)['recours_intermediaires'].append(copy.deepcopy(tentative))


def retenir_issue_intermediaire(monde, id, via, demande, issue):
    from .esprits import lire
    for s in lire(monde, id)['recours_intermediaires']:
        if s['via'] == via and s['objet'] == demande['objet'] and s['issue'] == 'preparee':
            s['issue'] = issue


def accomplir_livraison_intermediaire(monde, id, via, objet):
    from .esprits import lire
    for s in lire(monde, id)['recours_intermediaires']:
        if s['via'] == via and s['livraison'] == objet and s['issue'] == 'accepte':
            s['abouti'] = True


def affecter_livraison_intermediaire(monde, id, via, lot, part):
    from .esprits import esprit
    for s in esprit(monde, id)['recours_intermediaires']:
        if s['via'] == via and s['livraison'] == lot and s['issue'] == 'accepte':
            s['livraison'] = part


def retenir_proposition_tentee(monde, id, entrees):
    """Après le marché exécuté, remplace l'essai et acquitte son déclencheur."""
    from .esprits import lire
    e = lire(monde, id)
    e['recours_propositions'][:] = [x for x in e['recours_propositions']
                                  if (x['de'], x['besoin']) != (entrees['de'], entrees['besoin'])]
    e['recours_propositions'].append(copy.deepcopy(entrees))
    e['demande_refusee'] = None


def verifier_recours(monde, id):
    from .esprits import lire
    _verifier_recours(lire(monde, id))


def _verifier_recours(e):
    from .propositions import erreur_terme
    def cible(x):
        return isinstance(x, dict) and all(isinstance(x.get(k), str) for k in ("de", "besoin", "objet"))
    assert e["demande_refusee"] is None or cible(e["demande_refusee"]), "Déclencheur de recours invalide"
    assert isinstance(e['recours_intermediaires'], list) and all(
        set(s) == {'de', 'besoin', 'objet', 'operation', 'minute', 'via', 'issue', 'livraison', 'abouti'}
        and all(isinstance(s[k], str) for k in ('de', 'besoin', 'objet', 'operation', 'via', 'issue', 'livraison'))
        and type(s['abouti']) is bool and type(s['minute']) is int
        for s in e['recours_intermediaires']), 'Intermédiaires invalides'
    assert e['service_en_cours'] is None or (cible(e['service_en_cours'])
        and set(e['service_en_cours']) == {'de', 'besoin', 'objet', 'condition'}
        and erreur_terme({'type': 'tache', 'condition': e['service_en_cours']['condition']}) is None), 'Service en cours invalide'
    assert isinstance(e['recours_services'], list) and all(
        isinstance(s, dict) and set(s) == {'de', 'besoin', 'objet', 'operation', 'minute'}
        and all(isinstance(s[k], str) for k in ('de', 'besoin', 'objet', 'operation'))
        and type(s['minute']) is int for s in e['recours_services']), 'Tentatives de service invalides'
    assert isinstance(e["recours_propositions"], list) and all(
        cible(x) and isinstance(x.get("cause"), list) and isinstance(x.get("lien"), dict)
        and type(x.get("pieces")) is int and x["pieces"] >= 0 and isinstance(x.get("biens"), dict)
        and all(isinstance(o, str) and type(n) is int and n >= 0 for o, n in x["biens"].items())
        for x in e["recours_propositions"]), "Tentatives de proposition invalides"


def recherches_retenues(monde, id):
    """Copie ordonnée des lieux écartés par personne, dates historiques comprises."""
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['recherches'])


def lieux_ecartes(monde, id, qui):
    """Lieux et dates d'échec connus de cet observateur, sans création ni expiration."""
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['recherches'].get(qui, {}))


def indices_recherche_consommes(monde, id, qui):
    """Copie des indices déjà consommés, sans consulter la présence réelle."""
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['indices_recherche'].get(qui, {}))


def presence_recherche_retenue(monde, id, qui):
    """Dernière présence positive, conservée malgré une absence ultérieure."""
    from .esprits import lire
    return copy.deepcopy(lire(monde, id)['presence_recherche'].get(qui))


def appels_vains(monde, id, qui):
    """Lieux cherchés en vain, jusqu'à un nouvel indice dans ce lieu (``esprits.croire``,
    ``ouie._bruit_inconnu``). Ni le temps écoulé ni un constat d'absence ne les rouvrent."""
    from .esprits import lire
    return set(lire(monde, id)['recherches'].get(qui, {}))


def recherche_vaine(monde, id, qui, salle):
    """Le résultat d'une recherche se retient comme celui d'une demande, hors mémoire bornée."""
    from .esprits import esprit
    esprit(monde, id)["recherches"].setdefault(qui, {})[salle] = monde.data["minutes"]
    consommer_indices_recherche(monde, id, qui, salle)


def consommer_indices_recherche(monde, id, qui, salle):
    """Indices déjà connus au constat d'échec, ou encore disponibles dans une ancienne partie."""
    # Le constat consomme aussi les indices présents avant la recherche (anciennes parties
    # comprises). Leur répétition ne doit pas suffire à annuler ce constat.
    c = fait_brut(monde, id, qui, 'lieu')
    if c and c["valeur"] == salle:
        _situer_recherche(monde, id, qui, salle, c.get("case"))
        _retenir_indice(monde, id, qui, salle, _indice_presence(c))
    for s in bruits_retenus(monde, id, salle, examens=True):
        _retenir_indice(monde, id, qui, salle, indice_bruit(s))


def _indice_presence(c):
    # La date, la confiance et la chaîne de relais ne changent pas ce qui a été appris.
    force = 2 if c["source"] == "vu" else 1 if c["source"] == "entendu" else 0
    return ["presence", force, c.get("case")]


def indice_bruit(s):
    """Ce qui est perceptible du bruit, sans identité cachée ni date de répétition."""
    from .ouie import INTENSITES
    return ["bruit", INTENSITES[s["nature"]], s.get("qui"), s.get("case")]


def _retenir_indice(monde, id, qui, salle, indice):
    from .esprits import esprit
    from copy import deepcopy
    connus = esprit(monde, id)["indices_recherche"].setdefault(qui, {}).setdefault(salle, [])

    def couvre(a, b):
        # Une information moins forte ou moins précise n'ajoute rien. Une autre voix ou
        # une autre position située constitue en revanche un indice distinct.
        return (a[0] == b[0] and a[1] >= b[1] and a[2:-1] == b[2:-1]
                and (b[-1] is None or a[-1] == b[-1]))

    if any(couvre(ancien, indice) for ancien in connus):
        return False
    connus[:] = [ancien for ancien in connus if not couvre(indice, ancien)]
    connus.append(deepcopy(indice))
    return True


def contact_recherche(monde, id, qui, salle):
    """Une présence directement retrouvée ou une réponse saisie permet un nouveau contact ici."""
    from .esprits import esprit
    e = esprit(monde, id)
    e["recherches"].get(qui, {}).pop(salle, None)


def _situer_recherche(monde, id, qui, salle, case):
    """Un déplacement positivement appris est nouveau, même vers un ancien lieu d'échec.

    L'absence ne déplace pas ce repère ; une localisation moins précise ne l'efface pas.
    Cela distingue un retour appris de la répétition d'une voix au même endroit.
    """
    from .esprits import esprit
    from copy import deepcopy
    e = esprit(monde, id)
    avant = e["presence_recherche"].get(qui)
    deplace = bool(avant and (avant[0] != salle
                             or case is not None and avant[1] is not None and case != avant[1]))
    if not avant or avant[0] != salle or case is not None:
        e["presence_recherche"][qui] = [salle, deepcopy(case)]
    return deplace


def indice_recherche(monde, id, salle, qui=None, *, indice=None):
    """Seul un contenu nouveau rouvre son lieu, pour la personne identifiée ou celles cherchées.

    Ce suivi survit aux changements de but, à l'effacement des quarante souvenirs et à la
    recharge. Réentendre une voix ou réexpliquer un bruit ne crée pas un nouvel indice.
    """
    from .esprits import esprit
    recherches = esprit(monde, id)["recherches"]
    change = False
    if indice is None:
        c = fait_brut(monde, id, qui, 'lieu')
        if not c or c["valeur"] != salle:
            return False
        indice = _indice_presence(c)
        if _situer_recherche(monde, id, qui, salle, c.get("case")):
            change = salle in recherches.get(qui, {})
            recherches.get(qui, {}).pop(salle, None)
    for sujet in ([qui] if qui is not None else recherches):
        if _retenir_indice(monde, id, sujet, salle, indice):
            change |= salle in recherches.get(sujet, {})
            recherches.get(sujet, {}).pop(salle, None)
    return change


def installation_recherches(monde, id):
    """Drapeaux de migration relevés avant l'installation historique de l'esprit."""
    ancien = monde.data['esprits'].get(id, {})
    return 'recherches' not in ancien, 'indices_recherche' not in ancien


def migrer_recherches(monde, id, migrer_recherches, migrer_indices):
    """Reconstruit uniquement les anciens registres absents, sans nouvel épisode."""
    from .esprits import esprit
    e = esprit(monde, id)

    for souvenir in episodes(monde, id, types=("appel_sans_reponse",)):
        if migrer_recherches and souvenir["type"] == "appel_sans_reponse":
            salles = e["recherches"].setdefault(souvenir["qui"], {})
            salles[souvenir["salle"]] = max(salles.get(souvenir["salle"], -1), souvenir["minute"])
    if migrer_indices:
        for qui, salles in e["recherches"].items():
            for salle in salles:
                consommer_indices_recherche(monde, id, qui, salle)


def verifier_recherches(monde, id):
    """Validation inchangée des trois registres sauvegardés de recherche."""
    from .esprits import lire
    e = lire(monde, id)
    assert isinstance(e["recherches"], dict) and all(
        q in monde.objets or q == "joueur" for q in e["recherches"]
    ) and all(isinstance(salles, dict) and all(s in monde.data["salles"] and type(t) is int
              for s, t in salles.items()) for salles in e["recherches"].values()), "Recherches de PNJ invalides"
    assert isinstance(e["indices_recherche"], dict) and all(
        (q in monde.objets or q == "joueur") and isinstance(salles, dict)
        and all(s in monde.data["salles"] and isinstance(indices, list)
                and all(isinstance(x, list) and len(x) in (3, 4)
                        and ((x[0] == "presence" and len(x) == 3 and type(x[1]) is int and 0 <= x[1] <= 2)
                             or (x[0] == "bruit" and len(x) == 4 and type(x[1]) is int and x[1] > 0
                                 and (x[2] is None or x[2] == "joueur" or x[2] in monde.objets)))
                        and (x[-1] is None or isinstance(x[-1], list) and len(x[-1]) == 2
                             and all(type(n) is int for n in x[-1])) for x in indices)
                for s, indices in salles.items())
        for q, salles in e["indices_recherche"].items()), "Indices de recherche invalides"
    assert isinstance(e["presence_recherche"], dict) and all(
        (q in monde.objets or q == "joueur") and isinstance(p, list) and len(p) == 2
        and p[0] in monde.data["salles"] and (p[1] is None or isinstance(p[1], list)
            and len(p[1]) == 2 and all(type(n) is int for n in p[1]))
        for q, p in e["presence_recherche"].items()), "Présences de recherche invalides"
