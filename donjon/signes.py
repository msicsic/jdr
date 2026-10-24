"""Signes physiques, interprétations faillibles et décisions sociales.

``de`` et ``percus`` sont purs. Seul ``lire`` tire un dé et retient une impression.
La vérité et les jets restent au moteur ; ``publics`` ne projette que l'observation.
Les décisions de place/regard conservent leur cause dans l'intention avant de produire
un signe. Aucune relation n'est reconstruite d'après une simple proximité.
"""
import copy
import hashlib
import random

from . import relations
from .esprits import lire as esprit_lu
from .geometrie import distance

RELECTURE = 10
ATTITUDE_MAX = 120
COLERE_DEMIVIE = 15
GUET = 1                 # minute d'attente avant que sa durée soit un signe
PENOMBRE = 4
DISSIMULATION = 3
BANDE_RIEN = 8

# sorte, canal, lumière minimale, portée, difficulté, sens possibles, texte factuel
SIGNES = {
    "ecart": ("place", "vue", 1, None, 0, ("crainte", "hostilite"), "se tient à l'écart de {cible}"),
    "proche": ("place", "vue", 1, None, 0, ("attachement", "dependance"), "se tient près de {cible}"),
    "surveille": ("regard", "vue", 1, None, 0, ("mefiance", "crainte", "attirance"), "ne quitte pas {cible} des yeux"),
    "convoite": ("regard", "vue", 1, None, 0, ("guet", "garde"), "lance des regards vers {cible}"),
    "attend": ("duree", "vue", 1, None, 0, ("guet", "fatigue"), "reste à attendre sans rien faire"),
    "yeux_bas": ("expression", "vue", 2, 4, 2, ("crainte", "honte"), "baisse les yeux devant {cible}"),
    "dur": ("expression", "vue", 2, 4, 2, ("hostilite", "inquietude"), "a le regard dur et la mâchoire serrée"),
    "sourit": ("expression", "vue", 2, 4, 2, ("attachement", "flatterie"), "sourit à {cible}"),
    "doux": ("ton", "mots", 0, None, 3, ("attachement", "flatterie"), "parle doucement à {cible}"),
    "sec": ("ton", "mots", 0, None, 3, ("hostilite", "fatigue"), "a la voix sèche avec {cible}"),
    "brusque": ("expression", "vue", 1, None, 2, ("colere", "peur"), "fait des gestes brusques"),
    "fort": ("ton", "mots", 0, None, 3, ("colere", "peur"), "parle d'une voix forte"),
    "tremble": ("expression", "vue", 2, 4, 2, ("peur", "froid"), "tremble et se recroqueville"),
    "observe": ("regard", "vue", 1, None, 0, ("attention", "mefiance"), "regarde attentivement {cible}"),
    "hesite": ("ton", "mots", 0, None, 3, ("mensonge", "hesitation"), "hésite dans ses paroles"),
}
SENS = {v for s in SIGNES.values() for v in s[5]}


def installer(m):
    for cle, defaut in (("lectures", {}), ("signes_lus_joueur", {}), ("bilan_signes", {}),
                        ("tirages_lecture", 0), ("tirages_lecture_acteurs", {}), ("mesures_signes", {}), ("tons_percus", []), ("observations_joueur", [])):
        if cle not in m.data:
            m.data[cle] = copy.deepcopy(defaut)


def emotion(m, id):
    c = esprit_lu(m, id).get("emotions", {}).get("colere")
    if not c:
        return None
    niveau = c["niveau"] * 2 ** (-(m.data["minutes"] - c["depuis"]) / COLERE_DEMIVIE)
    return {**c, "niveau": niveau} if niveau >= 1 else None


def eprouver(m, id, autre, cause, delta):
    """Un tort effectivement éprouvé (après déduplication de la preuve commune)."""
    from .caractere import valeur
    if (delta.get("rancune", 0) <= 0 or cause not in
            ("vu_agir", "vol_surpris", "vu_porter", "pousse", "mensonge_decouvert", "imposture", "refus")):
        return
    if cause == "refus" and valeur(m, id, "fierte") < 60:
        return
    from .esprits import esprit
    esprit(m, id)["emotions"]["colere"] = {
        "contre": autre, "niveau": min(100, delta["rancune"] * 2), "depuis": m.data["minutes"]}


def guette(m, id):
    e = esprit_lu(m, id)
    i = e["intention"]
    if i and e["patience"] is not None and i["plan"] and i["plan"][0]["condition"] == "sans_temoin":
        return i["plan"][0]["cible"]
    return None


def dissimule(m, id, envers=None, intention=False):
    from .caractere import valeur
    e = esprit_lu(m, id)
    i = e["intention"]
    if intention or guette(m, id):
        return True
    if envers is None:
        return False
    r = relations.axes(m, id, envers)
    besoin = bool(i and any(x["cible"] == envers and x["operation"] in
                           ("demander", "acheter", "engager", "confier", "demander_passage") for x in i["plan"]))
    return bool((relations.peur(r) and valeur(m, id, "fierte") >= 60)
                or besoin and (relations.rancune(r) or relations.peur(r)))


def _signe(m, id, nom, envers, vrai, cache=False, elo=False):
    return {"id": "signe:" + hashlib.sha256(f"{id}:{nom}:{envers or ''}".encode()).hexdigest()[:20], "personnage": id, "signe": nom,
            "envers": envers, "vrai": vrai, "dissimule": cache, "elo": elo}


def _de(m, id):
    """Signes émis maintenant, vérité comprise : interne au moteur seulement."""
    from .corps import conscient
    if not conscient(m, id):
        return []
    if id == "joueur":
        from .temps import instant
        a = m.data.get("observation_joueur")
        if not a or not a["debut"] <= instant(m) < a["fin"]:
            return []
        return [_signe(m, id, "observe", a["cible"], "attention")]
    if id not in m.objets:
        return []
    e = esprit_lu(m, id)
    signes = []
    i = e["intention"] or {}
    for a in i.get("attitude", {}).values():
        signes.append(_signe(m, id, a["signe"], a["envers"], a["sens"],
                             dissimule(m, id, a["envers"])))
    objet = guette(m, id)
    if objet:
        if i["attente"] >= GUET * 600:
            signes.append(_signe(m, id, "attend", objet, "guet", True))
    for autre in relations.connus(m, id):
        r = relations.axes(m, id, autre)
        cache = dissimule(m, id, autre)
        if relations.vive(r, "peur"):
            signes.append(_signe(m, id, "yeux_bas", autre, "crainte", cache))
        if relations.vive(r, "rancune"):
            signes.append(_signe(m, id, "dur", autre, "hostilite", cache))
        if relations.vive(r, "affection"):
            signes.extend(_signe(m, id, n, autre, "attachement", cache) for n in ("sourit", "doux"))
        if relations.rancune(r) or relations.mefiance(r):
            signes.append(_signe(m, id, "sec", autre, "hostilite", cache))
    c = emotion(m, id)
    if c and c["niveau"] >= 20:
        signes.extend(_signe(m, id, n, c["contre"], "colere", dissimule(m, id, c["contre"]))
                      for n in ("brusque", "fort"))
    from .deliberation import seuils
    if e["besoins"].get("securite", 0) > seuils(m, id).get("securite", 100):
        signes.append(_signe(m, id, "tremble", None, "peur"))
    return signes


def de(m, id):
    """Émissions gardées tant que leurs seules causes demeurent identiques.

    La position et le regard restent vérifiés par ``percus``. Cette mémoire dérivée
    n'est pas sauvegardée : l'intégralité de sa clé vient du monde persistant.
    """
    from .corps import conscient
    from .temps import instant
    if id == "joueur":
        a = m.data.get("observation_joueur")
        cle = (repr(a), bool(a and a["debut"] <= instant(m) < a["fin"]), conscient(m, id))
    else:
        e = esprit_lu(m, id)
        i = e["intention"] or {}
        from .deliberation import seuils
        from .caractere import valeur
        c = emotion(m, id)
        cle = (relations.signature_signes(m, id),
               (c["contre"] if c and c["niveau"] >= 20 else None),
               valeur(m, id, "fierte") >= 60, repr(i.get("attitude")),
               guette(m, id), i.get("attente", 0) >= GUET * 600,
               tuple((x["operation"], x["cible"]) for x in i.get("plan", [])),
               e["besoins"].get("securite", 0) > seuils(m, id).get("securite", 100), conscient(m, id))
    cache = m.__dict__.setdefault("_emissions_signes", {})
    avant = cache.get(id)
    if avant is None or avant[0] != cle:
        cache[id] = (cle, _de(m, id))
    from .spatial import a_verifier
    resultat = cache[id][1]
    if a_verifier():
        assert resultat == _de(m, id), "Émissions de signes périmées"
    return resultat


def _niveau_distance(m, observateur, id):
    from .perception import eclairage
    from .spatial import position_acteur, _global
    salle, p = position_acteur(m, observateur)
    autre_salle, cible = position_acteur(m, id)
    if not m.data.get("mode_cases") or p is None or cible is None:
        return eclairage(m, autre_salle)["niveau"], 0
    return (eclairage(m, autre_salle, cible)["niveau"],
            distance(_global(m.data["salles"][salle], p), _global(m.data["salles"][autre_salle], cible)))


def _envers_percu(m, observateur, s, vus):
    cible = s["envers"]
    if cible is None or cible == observateur or cible in vus:
        return True
    # Une lecture ne révèle jamais une cible absente au joueur. Pour un PNJ,
    # une place crue suffit ; jamais la place véritable du tiers caché.
    if observateur == "joueur" or m.objets.get(cible, {}).get("type") != "personnage":
        return False
    from .deliberation import salle_crue
    return salle_crue(m, observateur, cible) == m.objets[observateur]["lieu"]


def _posture(m, s):
    """Existence physique du signe, indépendante de l'accès d'un observateur."""
    from .spatial import orientation_vers, position_cible
    o = m.joueur if s["personnage"] == "joueur" else m.objets[s["personnage"]]
    q = position_cible(m, s["envers"], o.get("lieu", o.get("salle"))) if s["envers"] else None
    if s["signe"] in ("ecart", "proche"):
        return q is not None and (distance(o["position"], q) >= 2 if s["signe"] == "ecart"
                                  else distance(o["position"], q) <= 1)
    if s["signe"] in ("surveille", "convoite", "observe"):
        return q is not None and orientation_vers(tuple(o["position"]), q) == o.get("orientation")
    return True


def _percus(m, observateur="joueur", tons=(), emissions=None, contexte=None):
    from .esprits import percus as objets_percus
    from .corps import conscient
    if not conscient(m, observateur):
        return []
    if contexte is not None:
        vus, niveaux = contexte
    elif observateur == "joueur":
        vus = {id: None for id, o in m.objets.items() if m.visible(id)}
    else:
        vus, _ = objets_percus(m, observateur)
    resultat = []
    for id in sorted(vus):
        if id != "joueur" and m.objets[id]["type"] != "personnage":
            continue
        niveau, loin = niveaux[id] if contexte is not None else _niveau_distance(m, observateur, id)
        for s in (de(m, id) if emissions is None else emissions.get(id, [])):
            regle = SIGNES[s["signe"]]
            if regle[1] != "vue" or niveau < regle[2] or regle[3] is not None and loin > regle[3]:
                continue
            if s["dissimule"] and regle[0] == "expression":
                continue
            if not _envers_percu(m, observateur, s, vus):
                continue
            # L'attitude est la cause d'un choix ; son signe exige encore la position
            # et l'orientation réelles. Une attitude périmée n'est pas un fait.
            if (s["signe"] in ("ecart", "proche") and s["envers"] not in vus
                    and s["envers"] != observateur) or not _posture(m, s):
                continue
            resultat.append({**s, "niveau": niveau, "distance": loin})
    # Les tons sont fournis par une parole effectivement saisie, jamais inférés d'un silence.
    for s in tons:
        if not s["dissimule"] and _envers_percu(m, observateur, s, vus):
            resultat.append({**s, "niveau": 2, "distance": 0})
    return resultat


def percus(m, observateur="joueur", tons=(), emissions=None):
    from .spatial import vue_memorisee, etat_fige
    with vue_memorisee(m), etat_fige(m):
        return _percus_gardes(m, observateur, tons, emissions)


def _percus_gardes(m, observateur, tons, emissions):
    from .spatial import a_verifier, position_cible
    from .esprits import percus as objets_percus
    from .corps import conscient
    if tons or not conscient(m, observateur):
        return _percus(m, observateur, tons, emissions)
    vus = ({id: None for id in m.objets if m.visible(id)} if observateur == "joueur"
           else objets_percus(m, observateur)[0])
    personnes = sorted(id for id in vus if id == "joueur" or m.objets[id]["type"] == "personnage")
    emissions = {id: de(m, id) for id in personnes} if emissions is None else emissions
    niveaux = {id: _niveau_distance(m, observateur, id) for id in personnes}
    # Une clé par observateur, indépendante des esprits et objets qu'il ne perçoit pas.
    # Les cibles crues ne sont jamais remplacées par une présence véritable.
    signature = tuple((id, niveaux[id], repr(emissions.get(id, [])),
                       tuple((s["id"], s["envers"] in vus, _envers_percu(m, observateur, s, vus),
                              position_cible(m, s["envers"], o.get("lieu", o.get("salle")))
                              if s["envers"] else None) for s in emissions.get(id, [])),
                       tuple(o.get("position") or ()), o.get("orientation"))
                      for id in personnes for o in [m.joueur if id == "joueur" else m.objets[id]])
    cache = m.__dict__.setdefault("_perceptions_signes", {})
    entree = cache.get(observateur)
    if entree is None or entree[0] != signature:
        cache[observateur] = (copy.deepcopy(signature), _percus(m, observateur, emissions=emissions,
                                                              contexte=(vus, niveaux)))
    resultat = cache[observateur][1]
    if a_verifier():
        assert resultat == _percus(m, observateur), "Signes perçus périmés"
    return resultat


def _nom(m, id):
    from .noms import nom
    from .francais import designer
    if not id:
        return ""
    if id == "joueur":
        return "toi"
    if id not in m.objets:
        return "une présence"
    if m.objets[id]["type"] == "personnage":
        from .noms import connait
        return m.objets[id]["nom"].split(",")[0] if connait(m, "joueur", id) else nom(m, id)
    return designer(m.objets[id])


def _texte(m, s):
    qui = "Tu" if s["personnage"] == "joueur" else _nom(m, s["personnage"])
    cible = _nom(m, s["envers"])
    from .francais import de
    forme = SIGNES[s["signe"]][6].replace("de {cible}", de(cible))
    return qui[:1].upper() + qui[1:] + " " + forme.format(cible=cible) + "."


def publics(m, observateur="joueur"):
    from .temps import instant
    tons_recents = [t["signe"] for t in m.data.get("tons_percus", []) if instant(m) - t["instant"] <= 30]
    return [{k: s[k] for k in ("id", "personnage", "signe", "envers")} | {"texte": _texte(m, s)}
            for s in percus(m, observateur, tons=tons_recents if observateur == "joueur" else ())]


def _compter(m, cle, combien=1):
    mesures = m.data.setdefault("mesures_signes", {})
    mesures[cle] = mesures.get(cle, 0) + combien


def _jet(m, observateur="joueur"):
    compteurs = m.data.setdefault("tirages_lecture_acteurs", {})
    n = compteurs.get(observateur, 0)
    compteurs[observateur] = n + 1
    m.data["tirages_lecture"] = m.data.get("tirages_lecture", 0) + 1
    return random.Random(f'{m.data["seed"]}:lecture:{observateur}:{n}').randint(1, 20)


def attribut(s):
    if s["signe"] in ("attend", "convoite"):
        return "intention"
    if s["signe"] in ("brusque", "fort", "tremble"):
        return "emotion"
    if s["signe"] == "hesite":
        return "parole_doutee"
    return "attitude:" + (s["envers"] or "")


def _occurrences(m, emissions=None, paroles=()):
    """Identité des émissions réelles : perdre la vue n'est pas leur disparition.

    Seuls les événements et les lectures enregistrent cette continuité. Les
    projections n'ont aucun effet ; tous les lecteurs partagent le même épisode.
    """
    from .temps import instant
    if emissions is None:
        emissions = {id: de(m, id) for id in ["joueur", *m.objets]
                     if id == "joueur" or m.objets[id]["type"] == "personnage"}
    suivi = m.data.setdefault("occurrences_signes", {"actifs": [], "episodes": {}, "paroles": {}})
    ids = {s["id"] for signes in emissions.values() for s in signes
           if SIGNES[s["signe"]][1] == "vue" and _posture(m, s)
           and not (s["dissimule"] and SIGNES[s["signe"]][0] == "expression")}
    for cle in ids - set(suivi["actifs"]):
        suivi["episodes"][cle] = suivi["episodes"].get(cle, 0) + 1
    suivi["actifs"] = sorted(ids)
    for s in paroles:
        cle = s["id"]
        if suivi["paroles"].get(cle) != instant(m):
            suivi["episodes"][cle] = suivi["episodes"].get(cle, 0) + 1
            suivi["paroles"][cle] = instant(m)
    return suivi["episodes"]


def _suivi(m, observateur, episodes):
    suivis = m.data.setdefault("suivi_signes", {})
    suivi = suivis.get(observateur)
    if suivi is None or suivi.get("version") != 2:
        # Une migration n'est pas un apprentissage. L'histoire physique absente
        # des anciennes sauvegardes ne peut pas être reconstruite rétroactivement.
        suivi = suivis[observateur] = {"version": 2, "retenus": {}, "conclusions": {}}
        for _, _, c in actives(m, observateur):
            if c["signe"] in episodes:
                suivi["retenus"][c["signe"]] = episodes[c["signe"]]
    return suivi


def interpreter(s, jet, bonus, dd):
    """Calcul pur du résultat ; les paramètres sont communs à tous les lecteurs."""
    marge = jet + bonus - dd
    sens = s["vrai"] if marge >= 0 else None
    if marge < -BANDE_RIEN:
        sens = "fatigue" if s["dissimule"] else next(x for x in SIGNES[s["signe"]][5] if x != s["vrai"])
    return sens, marge


def lire(m, observateur, signes=None, expres=False, occurrences=None):
    """Un essai par signe et par dix minutes ; échec compris. Pas de relance gratuite.

    La chronique omnisciente conserve les nouvelles conclusions et leur jet.
    Le banc de calibration instrumente aussi les essais sans nouvelle conclusion.
    Aucune fonction de projection ne transmet marge, justesse ou vérité au joueur/MJ.
    """
    from .caractere import modificateur, caracteristiques
    from .esprits import esprit, croire, reconsiderer
    installer(m)
    joueur = observateur == "joueur"
    e = None if joueur else esprit(m, observateur)
    essais = m.data["signes_lus_joueur"] if joueur else e["signes_lus"]
    if signes is None:
        signes = percus(m, observateur)
    episodes = (_occurrences(m, paroles=[s for s in signes if SIGNES[s["signe"]][1] == "mots"])
                if occurrences is None else occurrences)
    suivi = _suivi(m, observateur, episodes)
    for s in signes:
        cle = s["id"]
        dernier = essais.get(cle)
        episode = episodes[cle]
        if dernier is not None and m.data["minutes"] - dernier < RELECTURE:
            continue
        essais[cle] = m.data["minutes"]
        regle = SIGNES[s["signe"]]
        bonus = modificateur(m, observateur, "PSY") + (2 if expres else 0)
        if not joueur and (relations.familier(relations.axes(m, observateur, s["personnage"]))
                           or e["compagnie"].get(s["personnage"], 0) >= 60):
            bonus += 2
        bonus -= (PENOMBRE if s["niveau"] == 1 else 0) + (2 if s["distance"] > 4 else 0)
        dd = 10 + regle[4] + (modificateur(m, s["personnage"], "ELO" if s["elo"] else "VOL") + DISSIMULATION
                              if s["dissimule"] else 0)
        jet = _jet(m, observateur)
        sens, marge = interpreter(s, jet, bonus, dd)
        a = attribut(s)
        actuelle = (m.data["lectures"].get(cle) if joueur else
                    e["croyances"].get(s["personnage"], {}).get(a))
        active = actuelle and any(c is actuelle for _, _, c in actives(m, observateur))
        meme = bool(active and actuelle["valeur"] == sens and actuelle.get("envers") == s["envers"]
                    and suivi["retenus"].get(cle, actuelle.get("episode")) == episode)
        nouvelle = not meme if sens is not None else not active and suivi["conclusions"].get(cle) != episode
        suivi["conclusions"][cle] = episode
        psy = caracteristiques(m, observateur)["PSY"]
        tranche = "basse" if psy <= 9 else "haute" if psy >= 13 else "moyenne"
        _compter(m, "signes_" + regle[0])
        _compter(m, "essais_" + tranche)
        if sens is not None:
            _compter(m, "lectures")
            _compter(m, "lectures_" + tranche)
            _compter(m, "justes_" + tranche, int(marge >= 0))
            _compter(m, "meprises", int(marge < 0))
            c = {"valeur": sens, "source": "devine", "minute": m.data["minutes"],
                 "confiance": min(.8, .5 + .05 * (max(0, marge) if marge >= 0 else max(0, -marge - 6))), "signe": cle,
                 "envers": s["envers"], "personnage": s["personnage"], "attribut": attribut(s)}
            c.update(apprise=(actuelle.get("apprise", actuelle["minute"]) if meme else m.data["minutes"]),
                     episode=episode)
            suivi["retenus"][cle] = episode
            if joueur:
                m.data["lectures"][cle] = c
            else:
                utilisables_avant = usages(m, observateur)
                actuelle = e["croyances"].get(s["personnage"], {}).get(a)
                if not actuelle or actuelle["source"] not in ("vu", "essai", "savoir"):
                    croire(m, observateur, s["personnage"], a, sens, "devine", c["confiance"],
                           signe=cle, envers=s["envers"], apprise=c["apprise"], episode=episode)
                    if usages(m, observateur) != utilisables_avant:
                        reconsiderer(m, observateur)
                if sens == "guet" and nouvelle and (not actuelle or actuelle["source"] not in ("vu", "essai", "savoir")):
                    _compter(m, "guets_reperes")
                    from .esprits import memoriser
                    memoriser(m, observateur, {"type": "intention_lue", "auteur": s["personnage"],
                                               "objet": s["envers"], "signe": cle, "episode": episode,
                                               "confiance": c["confiance"], "source": "devine"})
        enregistrement = {"observation": copy.deepcopy(s), "lecture": sens, "jet": jet, "marge": marge,
                          "observateur": observateur, "psy": psy}
        if joueur:
            from .temps import instant
            m.data["observations_joueur"].append({"instant": instant(m), **enregistrement})
            del m.data["observations_joueur"][:-300]
        elif nouvelle:
            from .pnj import _chroniquer
            _chroniquer(m, observateur, f"Lecture de {s['personnage']} : {sens or 'aucune impression'}.", "lecture")
            m.data["chronique"][-1].update(enregistrement)
    return impressions(m) if joueur else None


def actives(m, observateur):
    """Lectures retenues et non périmées ; leur vérité n'est jamais consultée."""
    if observateur == "joueur":
        valeurs = [(c["personnage"], c.get("attribut", ""), c) for c in m.data.get("lectures", {}).values()]
    else:
        valeurs = [(x, a, c) for x, d in esprit_lu(m, observateur)["croyances"].items() for a, c in d.items()
                   if c["source"] == "devine" or c["source"].startswith("dit:") and "signe" in c]
    return [(x, a, c) for x, a, c in valeurs if m.data["minutes"] - c["minute"] <
            (30 if a in ("emotion", "intention", "parole_doutee") else ATTITUDE_MAX)]


def impressions(m):
    # Une impression sauvegardée est une mémoire ; l'affichage actuel exige le signe encore perçu.
    signes = {s["id"]: s for s in publics(m)}
    return [{"id": "impression:" + cle, "personnage": c["personnage"], "lecture": c["valeur"],
             "envers": c["envers"], "nettete": "nette" if c["confiance"] >= .65 else "vague",
             "texte": _impression(m, c)}
            for _, _, c in actives(m, "joueur") for cle in [c["signe"]] if cle in signes]


def _impression(m, c):
    qui = _nom(m, c["personnage"])
    from .francais import accorder
    o = m.objets.get(c["personnage"], {})
    cible = _nom(m, c["envers"])
    mots = {"crainte": "craindre " + cible, "hostilite": "éprouver de l'hostilité envers " + cible,
            "mefiance": "se méfier de " + cible, "attirance": "être " + accorder(o, "attiré") + " par " + cible,
            "attachement": "être " + accorder(o, "attaché") + " à " + cible, "dependance": "dépendre de " + cible,
            "guet": "guetter " + cible, "garde": "garder " + cible,
            "colere": "être en colère", "peur": "avoir peur", "froid": "avoir froid",
            "fatigue": "être " + accorder(o, "fatigué"), "honte": "avoir honte", "inquietude": "être " + accorder(o, "inquiet", "inquiète"),
            "flatterie": "flatter " + cible, "mensonge": "mentir", "hesitation": "hésiter", "attention": "prêter attention à " + cible}
    return qui[:1].upper() + qui[1:] + " semble " + ("peut-être " if c["confiance"] < .65 else "") + mots[c["valeur"]] + "."


def bilan_signes(m, observer=None):
    from .spatial import vue_memorisee, etat_fige
    with vue_memorisee(m), etat_fige(m):
        return _bilan_signes(m, observer)


def _bilan_signes(m, observer=None):
    installer(m)
    if observer is None:
        from .paroles import en_face
        candidats = sorted({s["personnage"] for s in percus(m)})
        from .monde import ErreurMonde
        try:
            id = en_face(m, candidats) if candidats else None
        except ErreurMonde:
            id = None
    else:
        id = observer
    avant_lectures = {_identite(c) for c in m.data["lectures"].values()}
    if id:
        lire(m, "joueur", [s for s in percus(m) if s["personnage"] == id], expres=observer is not None)
    signes = publics(m)
    avant = set(m.data["bilan_signes"])
    lignes = [s["texte"] for s in signes if s["id"] not in avant or observer == s["personnage"]]
    anciens = m.data["bilan_signes"]
    actuels = {s["id"]: s for s in signes}
    changes = sorted({s["personnage"] for cle, s in anciens.items() if cle not in actuels
                      and m.visible(s["personnage"])})
    lignes += ["Tu ne distingues plus certains signes chez " + _nom(m, x) + "."
               for x in changes]
    m.data["bilan_signes"] = actuels
    nouvelles = {cle for cle, c in m.data["lectures"].items() if _identite(c) not in avant_lectures}
    lignes += list(dict.fromkeys(s["texte"] for s in impressions(m) if s["personnage"] == id
                                and s["id"].removeprefix("impression:") in nouvelles))
    return lignes


def _identite(c):
    return (c["signe"], c["valeur"], c.get("envers"), c.get("apprise", c["minute"]))


def usages(m, id):
    """Ce que les consommateurs de 3c emploient vraiment : un nouveau savoir qui
    ne change aucun choix disponible ne doit pas interrompre le plan en cours.
    """
    from .deliberation import de_garde, salle_crue
    return tuple((x, a, c["valeur"], c.get("envers")) for x, a, c in actives(m, id)
                 if a == "attitude:" + id and c["valeur"] == "hostilite"
                 or a == "intention" and c["valeur"] == "guet"
                 and de_garde(m, id, salle_crue(m, id, c.get("envers"))))


def intentions_lues(m, id):
    return [(x, c) for x, a, c in actives(m, id) if a == "intention" and c["valeur"] == "guet"]


def hostile_cru(m, id, autre):
    return any(x == autre and a == "attitude:" + id and c["valeur"] == "hostilite"
               for x, a, c in actives(m, id))


def regarder(m, id, i, cible, signe, sens, *, detourner=False):
    """Décision réelle de regard, datée dans l'intention ; la rotation coûte son temps."""
    from .pnj import _case_crue
    from .spatial import QUART, orientation_vers, quarts, VECTEURS
    case = _case_crue(m, id, cible)
    if case is None:
        return 0
    o = m.objets[id]
    vers = orientation_vers(tuple(o["position"]), case)
    if vers is None:
        return 0
    if detourner:
        v = VECTEURS[vers]
        vers = next(n for n, p in VECTEURS.items() if p == (-v[0], -v[1]))
    avant = o.get("orientation")
    o["orientation"] = vers
    if detourner:
        i.get("attitude", {}).pop("regard", None)
    else:
        i.setdefault("attitude", {})["regard"] = {"signe": signe, "envers": cible, "sens": sens}
    return QUART * quarts(avant, vers)


def surveiller(m, id):
    """Un PNJ libre se tourne vers une menace qu'il croit dans sa salle."""
    from .deliberation import salle_crue, de_garde
    from .esprits import esprit
    e = esprit(m, id)
    i = e["intention"]
    if not m.data.get("mode_cases") or guette(m, id) or (i and i["plan"] and i["plan"][0]["operation"] not in ("abriter", "chauffer", "reposer", "inspecter")):
        return 0
    suspects = {x for x in [*relations.connus(m, id), "joueur"] if x != id
                and (relations.se_mefie(m, id, x) or relations.craint(m, id, x))}
    suspects.update(x for x, c in intentions_lues(m, id) if de_garde(m, id, salle_crue(m, id, c.get("envers"))))
    suspects = sorted(x for x in suspects if salle_crue(m, id, x) == m.objets[id]["lieu"])
    if not suspects:
        if i:
            i.get("attitude", {}).pop("regard", None)
        return 0
    if i is None:
        i = e["intention"] = {"but": {"type": "surveiller", "qui": suspects[0]}, "motif": "securite",
                               "plan": [], "depuis": m.data["minutes"], "attente": 0}
    x = suspects[0]
    return regarder(m, id, i, x, "surveille", "crainte" if relations.craint(m, id, x) else "mefiance")


def place(m, id, etape, lignes):
    """Choisir une case de séjour parmi celles qui permettent encore le geste.

    Un pas fait partie du trajet commun : obstacles, occupation et temps restent ses juges.
    La distance sociale se juge sur les positions crues, la chaleur sur le foyer visé.
    """
    from .pnj import _case_crue, _marcher
    from .spatial import _case_libre
    from .esprits import esprit
    from .deliberation import salle_crue
    o, e = m.objets[id], esprit(m, id)
    i = e["intention"]
    if not m.data.get("mode_cases") or not i or etape["operation"] not in ("abriter", "chauffer", "reposer"):
        return None
    ici = o["lieu"]
    liens = []
    for x in sorted(set(relations.connus(m, id)) | {x for x, _, _ in actives(m, id)}):
        if x == id or salle_crue(m, id, x) != ici:
            continue
        p = _case_crue(m, id, x)
        if p is None:
            continue
        r = relations.axes(m, id, x)
        hostile = hostile_cru(m, id, x)
        if relations.peur(r) or relations.rancune(r) or hostile:
            # Le poids de l'écart suit l'axe le plus fort ; la décision, les bandes communes.
            evite = max(r["peur"], r["rancune"], relations.RANCUNE if hostile else 0)
            liens.append((x, p, -evite, "ecart", "crainte" if r["peur"] >= r["rancune"] else "hostilite"))
        elif relations.vive(r, "affection") or relations.confiance(r) and e["besoins"].get("securite", 0) >= 50:
            liens.append((x, p, max(r["affection"], r["confiance"]), "proche",
                          "attachement" if relations.vive(r, "affection") else "dependance"))
    if not liens:
        i.get("attitude", {}).pop("place", None)
        return None
    cible = _case_crue(m, id, etape["cible"]) if etape["operation"] == "chauffer" else None
    depart = tuple(o["position"])
    def possible(p):
        return cible is None or distance(p, cible) <= 2
    def score(p):
        return sum((max(0, 3 - distance(p, q)) * (-v) if v < 0 else min(3, max(0, distance(p, q) - 1)) * v)
                   for _, q, v, _, _ in liens)
    # Un mouvement ne doit pas alterner entre cases de même valeur.
    candidats = [depart] + [(depart[0] + dx, depart[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                           if dx or dy]
    candidats = [p for p in candidats if _case_libre(m, ici, p) and possible(p)]
    if not candidats:
        return None
    meilleur = min(candidats, key=lambda p: (score(p), distance(p, depart), p))
    x, q, v, signe, sens = max(liens, key=lambda l: (abs(l[2]), l[0]))
    if signe == "ecart" and distance(meilleur, q) >= 2 or signe == "proche" and distance(meilleur, q) <= 1:
        i.setdefault("attitude", {})["place"] = {"signe": signe, "envers": x, "sens": sens}
    if meilleur != depart and score(meilleur) < score(depart):
        return _marcher(m, id, lambda salle, p: salle == ici and tuple(p) == meilleur, lignes)
    return None


def verifier(m):
    assert type(m.data.get("tirages_lecture", 0)) is int and m.data.get("tirages_lecture", 0) >= 0
    for id in m.data.get("esprits", {}):
        e = esprit_lu(m, id)
        assert isinstance(e["emotions"], dict) and set(e["emotions"]) <= {"colere"}
        c = e["emotions"].get("colere")
        assert c is None or (set(c) == {"contre", "niveau", "depuis"} and isinstance(c["contre"], str)
                             and type(c["depuis"]) is int and 0 <= c["niveau"] <= 100)
        i = e["intention"]
        if i:
            assert set(i.get("attitude", {})) <= {"place", "regard"}
            assert all(set(a) == {"signe", "envers", "sens"} and a["signe"] in SIGNES
                       and a["sens"] in SENS and isinstance(a["envers"], str) for a in i.get("attitude", {}).values())


def percevoir_tous(m):
    """Aux événements du monde et aux minutes, jamais à une simple consultation du joueur."""
    from .esprits import pnjs
    from .spatial import vue_memorisee, etat_fige
    emissions = {id: de(m, id) for id in ["joueur", *m.objets]
                 if id == "joueur" or m.objets[id]["type"] == "personnage"}
    episodes = _occurrences(m, emissions)
    if not any(emissions.values()):
        return
    with vue_memorisee(m), etat_fige(m):
        for id in pnjs(m):
            lire(m, id, percus(m, id, emissions=emissions), occurrences=episodes)


def mesures(m):
    compte = m.data.get("mesures_signes", {})
    resultat = {cle: compte.get(cle, 0) for cle in ("lectures", "meprises", "guets_reperes", "attentes_sous_regard")}
    for sorte in sorted({v[0] for v in SIGNES.values()}):
        resultat["signes_" + sorte] = compte.get("signes_" + sorte, 0)
    for tranche in ("basse", "moyenne", "haute"):
        n = compte.get("lectures_" + tranche, 0)
        resultat["lectures_" + tranche] = n
        resultat["justesse_" + tranche] = compte.get("justes_" + tranche, 0) / n if n else 0
    return resultat


def attente_sous_regard(m, id, dt):
    from .esprits import pnjs, percoit
    if not guette(m, id):
        return
    if any((esprit_lu(m, x)["intention"] or {}).get("attitude", {}).get("regard", {}).get("envers") == id
           and percoit(m, x, id) for x in pnjs(m) if x != id):
        _compter(m, "attentes_sous_regard", dt / 600)


def tons(m, auteur, destinataires):
    return [s for s in de(m, auteur) if SIGNES[s["signe"]][1] == "mots"
            and (s["envers"] is None or s["envers"] in destinataires)]


def entendre_ton(m, observateur, auteur, destinataires):
    from .voix import identifie
    if observateur == auteur or not identifie(m, observateur, auteur):
        return
    tons_entendus = tons(m, auteur, destinataires)
    if observateur == "joueur":
        from .temps import instant
        installer(m)
        m.data["tons_percus"] = [{"instant": instant(m), "signe": s} for s in tons_entendus if not s["dissimule"]]
    signes = percus(m, observateur, tons=tons_entendus)
    lire(m, observateur, [s for s in signes if SIGNES[s["signe"]][1] == "mots"])


def flairer(m, observateur, auteur, sujet, a, valeur):
    """Une affirmation contraire à ce que croit son auteur : on flaire, sans apprendre le vrai.

    Le joueur ne porte pas de croyances : seules ses observations enregistrées peuvent
    établir qu'il savait le contraire ; la vérité d'un objet caché ne suffit jamais.
    """
    from .esprits import croyance, memoriser
    from .voix import identifie, se_mefier
    if auteur == "joueur":
        o = m.objets.get(sujet)
        from .esprits import ETATS_VISIBLES
        connue = (o.get(a) if o and m.visible(sujet)
                  and (a == "lieu" or a in ETATS_VISIBLES.get(o["type"], ())) else None)
    else:
        c = croyance(m, auteur, sujet, a)
        connue = c["valeur"] if c else None
    if connue is None or connue == valeur or not identifie(m, observateur, auteur):
        return False
    # Le signe de parole est reçu dans ce circuit seulement après les mots saisis.
    s = _signe(m, auteur, "hesite", observateur, "mensonge", True, elo=True)
    from .temps import instant
    s["id"] += ":" + str(instant(m)) + ":" + hashlib.sha256(repr((sujet, a, valeur)).encode()).hexdigest()[:16]
    lire(m, observateur, [{**s, "niveau": 2, "distance": 0}])
    c = croyance(m, observateur, auteur, "parole_doutee")
    if not c or c.get("signe") != s["id"] or c["valeur"] != "mensonge":
        return False
    memoriser(m, observateur, {"type": "parole_doutee", "locuteur": auteur, "sujet": sujet, "attribut": a, "source": "devine"})
    memoriser(m, observateur, {"type": "mensonge_dementi", "locuteur": auteur, "sujet": sujet, "attribut": a, "source": "devine"})
    se_mefier(m, observateur, auteur, "devine")
    return True
