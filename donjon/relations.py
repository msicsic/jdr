"""Relations orientées. Seul accès aux axes, aux bandes et à leurs causes.

Les souvenirs sont la porte d'écriture (esprits.memoriser). Les lectures sont pures :
estompement depuis l'ancre du dernier événement, sans arrondis cumulés ni état caché.
« fiable » reste un avis dans la parole, jamais un attribut de croyance.
"""
import copy
import math
import hashlib
import json

FIABLE = "fiable"
AXES = ("confiance", "affection", "rancune", "peur", "dette", "ascendant")
ETRANGER = dict(zip(AXES, (40, 0, 0, 0, 0, 0)))
MEFIANCE, CONFIANCE, RANCUNE, PEUR = 30, 60, 40, 40
VIF = 60   # un axe qui se montre (``vive``)
MENTEUSE = 0
EPREUVES = {
    "garde_ignoree": {"confiance": -10, "rancune": 10},
    "service_rendu": {"confiance": 20, "affection": 10, "rancune": -15, "dette": 20},
    "vu_agir": {"confiance": -40, "affection": -10, "rancune": 40},
    "vol_surpris": {"confiance": -40, "affection": -10, "rancune": 40},
    "vu_porter": {"confiance": -40, "affection": -10, "rancune": 40},
    "tort_tiers": {"confiance": -25, "rancune": 10},
    "mensonge_decouvert": {"confiance": -35, "affection": -5, "rancune": 15},
    "imposture": {"confiance": -35, "affection": -5, "rancune": 15},
    "mensonge_dementi": {"confiance": -10},
    "dispute_perdue": {"rancune": 10},
    "parti_pris": {"affection": 3},
    "rumeur": {"confiance": -20},
    "aveu": {"confiance": -25},
    "refus": {"rancune": 5},
    "nourri": {"confiance": 10, "affection": 10, "rancune": -10, "dette": 20},
    "recu": {"confiance": 10, "affection": 10, "rancune": -10, "dette": 20},
    "pret_recu": {"dette": 10},
    "pret_rendu": {"confiance": 15, "affection": 5},
    "engagement_tenu": {"confiance": 15, "affection": 5, "dette": 10},
    "engagement_abandonne": {"confiance": -20, "rancune": 15},
    "parole_rompue": {"confiance": -20, "rancune": 15},   # « J'arrive ! » attendu en vain (``appel.tenir``)
    "prevenu": {"confiance": 15, "affection": 10, "dette": 10},
    "subi": {"confiance": -40, "affection": -15, "rancune": 40, "peur": 30},
    "violence_vue": {"confiance": -40, "peur": 20},
    "pousse": {"confiance": -30, "affection": -10, "rancune": 25, "peur": 20},
    "poussee_vue": {"confiance": -15, "peur": 10},
    "passage_accorde": {"confiance": 3, "affection": 2, "dette": 5},
    "epreuve_partagee": {"confiance": 3, "affection": 5},
    "dette_niee": {"confiance": -20, "rancune": 15},
    "pret_garde": {"confiance": -20, "rancune": 15},
    "dette_honoree": {"dette": -20},
}
BANDES = ("mefiance", "confiance", "rancune", "peur", "ascendant")


def identifier(s, instant):
    """Identité durable d'un fait ; une rumeur conserve celle de son événement d'origine."""
    if s["type"] in {*EPREUVES, "avis_recu", "restitution", "don", "engagement_pris"} and "preuve" not in s:
        s["preuve"] = hashlib.sha256(json.dumps([instant, s], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _bandes(r, avant=None):
    a = avant or {}
    return {"mefiance": r["confiance"] < (40 if a.get("mefiance") else MEFIANCE),
            "confiance": r["confiance"] >= (50 if a.get("confiance") else CONFIANCE),
            "rancune": r["rancune"] >= (30 if a.get("rancune") else RANCUNE),
            "peur": r["peur"] >= (30 if a.get("peur") else PEUR),
            "ascendant": r.get("ascendant", 0) >= (50 if a.get("ascendant") else CONFIANCE)}


def _nouvelle(axes=None, minute=0):
    r = {**ETRANGER, **(axes or {}), "minute": minute, "source": "savoir", "motifs": []}
    r["bandes"] = _bandes(r)
    r["ancrages"] = {a: [r[a], minute] for a in ("affection", "rancune", "peur", "ascendant")}
    return r


def _completer(r):
    """Vue du contrat actuel ; l'absence historique de l'axe signifie zéro."""
    return {**r, "ascendant": r.get("ascendant", 0),
            "bandes": {"ascendant": False, **r["bandes"]},
            "ancrages": {"ascendant": [0, 0], **r["ancrages"]}}


def installer(monde, id):
    from .esprits import esprit
    nouveau = "relations" not in monde.data.get("esprits", {}).get(id, {})
    e = esprit(monde, id)
    if nouveau:
        e["relations"] = {x: _nouvelle(a) for x, a in (monde.objets[id].get("profil") or {}).get("liens", {}).items()}


def connus(monde, id):
    from .esprits import lire
    id = _observateur_devis(monde, id)
    return sorted(lire(monde, id).get("relations", {}))


def _observateur_devis(monde, id):
    contexte = getattr(monde, "_contexte_devis", None)
    return contexte.observateur if contexte is not None and id == contexte.acteur else id


def oublier_portage(monde, id, objet):
    from .esprits import esprit
    esprit(monde, id)["portages"].pop(objet, None)


def portage_connu(monde, id, objet, porteur):
    from .esprits import lire
    e = lire(monde, id)
    p = e["portages"].get(objet)
    return bool(p and p["auteur"] == porteur
                and e["preuves_relations"].get(porteur + ":" + p["preuve"], {}).get("niveau", 0) >= 1)


def verifier_chronique(c):
    assert (set(c) == {"minute", "instant", "pnj", "texte", "nature", "relation", "cause", "bandes", "mefiance_levee", "service"}
            and isinstance(c["relation"], str) and c["cause"] in EPREUVES
            and isinstance(c["bandes"], dict) and set(c["bandes"]) in (set(BANDES), set(BANDES) - {"ascendant"})
            and all(type(v) is bool for v in c["bandes"].values())
            and type(c["mefiance_levee"]) is bool and (c["service"] is None or isinstance(c["service"], str))), "Chronique de relation invalide"


def _estompes(monde, id, autre, r):
    # Ascendant : même retour lent au lien initial que l’affection (1 point/h).
    # Aucune épreuve du présent lot ne modifie cet axe.
    from .caractere import valeur
    liens = (monde.objets[id].get("profil") or {}).get("liens", {}).get(autre, {})
    demie = max(1, 720 * valeur(monde, id, "fierte") / 50 / (1 + valeur(monde, id, "douceur") / 100))
    resultat = {}
    for a, (base, minute) in r["ancrages"].items():
        dt = max(0, monde.data["minutes"] - minute)
        if a in ("affection", "ascendant"):
            ancre = liens.get(a, 0)
            ecart = base - ancre
            resultat[a] = ancre + (1 if ecart >= 0 else -1) * max(0, abs(ecart) - dt / 60)
        else:
            resultat[a] = base * 2 ** (-dt / (demie if a == "rancune" else 120))
    return resultat


def _lecture_pure(monde, id, autre):
    from .esprits import lire
    brut = lire(monde, id).get("relations", {}).get(autre)
    if brut is None:
        return _nouvelle()
    r = _completer(brut)
    for a, v in _estompes(monde, id, autre, r).items():
        ancre = (monde.objets[id].get("profil") or {}).get("liens", {}).get(autre, {}).get(a, 0)
        r[a] = math.ceil(v - 1e-9) if a in ("affection", "ascendant") and r["ancrages"][a][0] > ancre else math.floor(v + 1e-9)
    r["bandes"] = _bandes(r, brut["bandes"])
    return r


def _lecture(monde, id, autre):
    from .esprits import lire
    id = _observateur_devis(monde, id)
    profil = monde.objets[id].get("profil") or {}
    brut = lire(monde, id).get("relations", {}).get(autre)
    cle = (monde.data["minutes"],
           tuple((profil.get("liens") or {}).get(autre, {}).get(a, 0)
                 for a in ("affection", "ascendant")),
           profil.get("valeurs", {}).get("fierte", 50),
           profil.get("valeurs", {}).get("douceur", 50))
    cache = monde.__dict__.setdefault("_lectures_relations", {})
    entree = cache.get((id, autre))
    if entree is None or entree[0] != cle or entree[1] != brut:
        copie = entree[1] if entree is not None and entree[1] == brut else copy.deepcopy(brut)
        cache[id, autre] = (cle, copie, _lecture_pure(monde, id, autre))
    resultat = cache[id, autre][2]
    from .spatial import a_verifier
    if a_verifier():
        assert resultat == _lecture_pure(monde, id, autre), "Lecture de relation périmée"
    return resultat


def signature_signes(monde, id):
    """Seulement les bandes et seuils effectivement lus par les émissions."""
    from .esprits import lire
    profil = monde.objets[id].get("profil") or {}
    brut = lire(monde, id)["relations"]
    cle = (monde.data["minutes"], repr(profil.get("liens")),
           profil.get("valeurs", {}).get("fierte", 50), profil.get("valeurs", {}).get("douceur", 50))
    cache = monde.__dict__.setdefault("_signatures_relations_signes", {})
    entree = cache.get(id)
    if entree is None or entree[0] != cle or entree[1] != brut:
        copie = entree[1] if entree is not None and entree[1] == brut else copy.deepcopy(brut)
        cache[id] = (cle, copie, _signature_signes_pure(monde, id))
    resultat = cache[id][2]
    from .spatial import a_verifier
    if a_verifier():
        assert resultat == _signature_signes_pure(monde, id), "Signature sociale périmée"
    return resultat


def _signature_signes_pure(monde, id):
    return tuple((x, vive(r, "peur"), vive(r, "rancune"), vive(r, "affection"),
                  peur(r), rancune(r), mefiance(r))
                 for x in connus(monde, id) for r in [axes(monde, id, x)])


def envers(monde, id, autre):
    return copy.deepcopy(_lecture(monde, id, autre))


def axes(monde, id, autre):
    r = _lecture(monde, id, autre)
    return {a: r[a] for a in AXES} | {"bandes": dict(r["bandes"])}


def statuts_reconnus(monde, id, autre, lieu, domaine):
    """Croyance sourcée de portée pertinente, sans lire le profil réel du titulaire."""
    from .esprits import croyance
    c = croyance(monde, id, autre, "statuts")
    if c is None:
        return None
    resultat = copy.deepcopy(c)
    resultat["valeur"] = [v for v in resultat["valeur"] if lieu in v["lieux"] and domaine in v["domaines"]]
    return resultat if resultat["valeur"] else None


def autorite_reconnue(monde, id, autre):
    """Ascendant qu'id reconnaît à autre, sans statut ni bonus de décision."""
    return _lecture(monde, id, autre)["ascendant"]


def autorite_mandat(monde, id, autre, lieu, domaine):
    """Une lecture perçue ; la dette figure déjà dans le jet commun.

    Statut : 3 points, ascendant : au plus 3, total au plus 5 points
    de DD. La peur ne confère aucun pouvoir de mandat dans ce lot.
    """
    from .voix import identifie
    r = percue(monde, id, autre)
    statut = statuts_reconnus(monde, id, autre, lieu, domaine) if identifie(monde, id, autre) else None
    return {"statut": statut, "ascendant": r["ascendant"], "dette": r["dette"],
            "bonus": min(5, (3 if statut else 0) + max(0, r["ascendant"]) * 3 / 100)}


def autorite_estimee(monde, observateur, autre, lieu, domaine):
    """Autorité que l'observateur croit avoir, sans lire le destinataire.

    Son propre statut cru est un a priori explicite. Le lien observateur ->
    autre ne dit pas quel ascendant autre lui reconnaît : cet ascendant et
    la dette réciproque inconnus sont estimés à zéro, sans retourner les axes.
    Ce n'est ni une reconnaissance réciproque ni le jet réel du mandaté.
    """
    statut = statuts_reconnus(monde, observateur, observateur, lieu, domaine)
    return {"statut": statut, "ascendant": 0, "dette": 0,
            "bonus": 3 if statut else 0}


def chance_demande(monde, id, autre):
    """Estimation du demandeur, jamais lecture de l'esprit de l'autre.

    Son lien sert d'a priori ; ses refus et les services qu'il a lui-même rendus
    le corrigent. Les signes lus (3c), puis les contreparties (3e), pourront
    enrichir cette seule estimation. Ce n'est pas la chance du jet réel.
    """
    from .deliberation import REDEMANDE
    from .esprits import lire
    id = _observateur_devis(monde, id)
    r, e = axes(monde, id, autre), lire(monde, id)
    chance = (0.5 + (r["confiance"] - 40) / 200 + r["affection"] / 500
              - r["rancune"] / 250 - r["peur"] / 500 + r["dette"] / 1000)
    # Une incapacité matérielle n'est pas un rejet de la personne. Elle reste
    # traitée par les refus de la demande précise dans le planificateur.
    refus = [s for s in e["refus"] if s["de"] == autre
             and monde.data["minutes"] - s["minute"] < REDEMANDE
             and s["raison"] in ("refus", "mefiance")]
    if refus:
        chance -= 0.3 if any(s["raison"] == "mefiance" for s in refus) else 0.15
    recents = [s for s in e["memoire"] if monde.data["minutes"] - s["minute"] < REDEMANDE]
    if any(s["type"] in ("don", "engagement_tenu") and s.get("a", s.get("pour")) == autre
           for s in recents):
        chance += 0.1  # Il espère la réciprocité, sans la savoir acquise.
    if any(s["type"] == "se_sait_vu" and s["par"] == autre for s in recents):
        chance -= 0.3
    return min(0.9, max(0.1, chance))


def chance_proposition(chance, gain):
    """La contrepartie crue améliore l'espoir, sans garantir l'accord réel."""
    return min(0.95, max(0.1, chance + 0.35 * gain / (gain + 3)))


def signature(monde, id):
    """Clé pure des lectures d'axes : le cache des signes n'accède pas au stockage.
    Les ancres et bandes comptent aussi, même si l'arrondi actuel ne bouge pas.
    """
    from .esprits import lire
    profil = monde.objets[id].get("profil") or {}
    return (monde.data["minutes"],
            tuple((x, tuple(r[a] for a in AXES), tuple(r["bandes"].items()),
                   tuple((a, tuple(v)) for a, v in r["ancrages"].items()))
                  for x, brut in lire(monde, id)["relations"].items() for r in [_completer(brut)]),
            repr(profil.get("liens")), profil.get("valeurs", {}).get("fierte"),
            profil.get("valeurs", {}).get("douceur"))


def percue(monde, auditeur, locuteur):
    from .voix import SUSPECTE, identifie, reconnaitre
    if identifie(monde, auditeur, locuteur):
        return envers(monde, auditeur, locuteur)
    r = _nouvelle()
    if reconnaitre(monde, auditeur, locuteur)[1] == SUSPECTE:
        r.update(confiance=MENTEUSE, source="entendu")
        r["bandes"] = _bandes(r)
    return r


def mefiance(r):
    return r.get("bandes", {}).get("mefiance", r["confiance"] < MEFIANCE)


def confiance(r):
    return r.get("bandes", {}).get("confiance", r["confiance"] >= CONFIANCE)


def rancune(r):
    """Bande, y compris pour une relation perçue envers une voix non identifiée."""
    return r["bandes"]["rancune"]


def peur(r):
    return r["bandes"]["peur"]


def affection_leve_orgueil(r):
    """Une affection d'au moins cinquante lève l'orgueil au passage (§ 3.5)."""
    return r["affection"] >= 50


def vive(r, axe):
    """Un axe assez marqué pour se lire sur le corps ou le visage, dès soixante (signes de 3c)."""
    return r[axe] >= VIF


def familier(r):
    """Une affection d'au moins quarante rend ses signes plus lisibles (lecture de 3c)."""
    return r["affection"] >= 40


def dette_notable(r):
    """Dette morale relevée par le récit et les mesures, dès vingt (§ 3.5)."""
    return r["dette"] >= 20


def se_mefie(monde, id, autre):
    from .esprits import lire
    r = lire(monde, id)["relations"].get(autre)
    return bool(r and r["bandes"]["mefiance"])


def se_fie(monde, id, autre):
    from .esprits import lire
    r = lire(monde, id)["relations"].get(autre)
    return bool(r and r["bandes"]["confiance"])


def en_veut(monde, id, autre, seuil=RANCUNE):
    r = envers(monde, id, autre)
    return rancune(r) if seuil == RANCUNE else r["rancune"] >= seuil


def craint(monde, id, autre, seuil=PEUR):
    r = envers(monde, id, autre)
    return peur(r) if seuil == PEUR else r["peur"] >= seuil


def doit(monde, id, autre):
    from .esprits import lire
    return lire(monde, id)["relations"].get(autre, ETRANGER)["dette"]


def fiable(monde, id, autre):
    r = envers(monde, id, autre)
    return True if confiance(r) else False if mefiance(r) else None


def croyance(monde, id, autre):
    """Avis dérivé pour le contrat de parole, jamais stocké en croyance."""
    r, v = envers(monde, id, autre), fiable(monde, id, autre)
    return None if v is None else {"valeur": v, "minute": r["minute"], "source": r["source"], "confiance": 1.0}


def _appliquer(monde, id, autre, cause, s, facteur=1, tiers=None):
    if id == "joueur" or autre in (None, id) or autre != "joueur" and (
            autre not in monde.objets or monde.objets[autre]["type"] != "personnage"):
        return
    from .esprits import esprit, reconsiderer, percoit
    e = esprit(monde, id)
    if (autre not in e["relations"] and autre not in e["voix"]
            and not any(c["source"] in ("vu", "essai", "entendu", "savoir") for c in e["croyances"].get(autre, {}).values())
            and not percoit(monde, id, autre)):
        return  # une identité seulement prétendue ou nommée n'est pas une personne identifiée
    from .caractere import valeur
    preuve = s.get("preuve") or hashlib.sha256(json.dumps(s, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    cle = autre + ":" + preuve
    preuves = esprit(monde, id)["preuves_relations"]
    niveau = 0.5 if cause == "rumeur" else 0.8 if cause == "aveu" or s.get("par") == "ouie" else 1.0
    precedente = preuves.get(cle)
    if precedente and precedente["niveau"] > niveau:
        return
    r = envers(monde, id, autre)
    effets = dict(EPREUVES[cause])
    if cause == "dette_honoree":
        effets["dette"] = -s.get("montant", 20)
    if cause == "refus" and s.get("raison") == "mefiance":
        effets["rancune"] += 10
    if tiers is not None:
        effets["confiance"] *= (50 + valeur(monde, id, "honnetete")) / 100
        effets["rancune"] *= envers(monde, id, tiers)["affection"] / 100
    if effets.get("rancune", 0) > 0:
        effets["rancune"] *= valeur(monde, id, "fierte") / 50
    if effets.get("dette", 0) > 0:
        effets["dette"] *= valeur(monde, id, "loyaute") / 50
    if cause in ("nourri", "recu", "service_rendu"):
        effets["affection"] *= (50 + valeur(monde, id, "empathie")) / 100
    if effets.get("peur", 0) > 0:
        effets["peur"] *= (100 - valeur(monde, id, "courage")) / 50
    souhaites = {a: round(v * facteur) for a, v in effets.items()}
    deja = precedente["effets"] if precedente else {}
    retenus = {a: (deja.get(a, 0) if abs(deja.get(a, 0)) >= abs(souhaites.get(a, 0)) else souhaites.get(a, 0))
               for a in set(deja) | set(souhaites)}
    preuves[cle] = {"niveau": niveau, "effets": retenus}
    effets = {a: retenus[a] - deja.get(a, 0) for a in retenus}
    avant = {a: r[a] for a in AXES}
    estompes = _estompes(monde, id, autre, r)
    for a, v in effets.items():
        montant = v
        if not montant:
            continue
        exact = min(100, max(0, estompes.get(a, r[a]) + montant))
        ancre = (monde.objets[id].get("profil") or {}).get("liens", {}).get(autre, {}).get(a, 0)
        r[a] = math.ceil(exact - 1e-9) if a in ("affection", "ascendant") and exact > ancre else math.floor(exact + 1e-9)
        if a in r["ancrages"]:
            r["ancrages"][a] = [exact, monde.data["minutes"]]
    delta = {a: r[a] - avant[a] for a in AXES if r[a] != avant[a]}
    if not delta:
        return
    bandes = r["bandes"]
    r["bandes"] = _bandes(r, bandes)
    motif = {"type": cause, "minute": monde.data["minutes"], "effets": delta}
    for k in ("objet", "operation", "raison", "sujet", "de", "victime"):
        if k in s:
            motif[k] = copy.deepcopy(s[k])
    r["motifs"] = (r["motifs"] + [motif])[-3:]
    r.update(minute=monde.data["minutes"], source=s.get("source", "entendu" if s.get("par") == "ouie" else "vu"))
    esprit(monde, id)["relations"][autre] = r
    from .signes import eprouver as eprouver_emotion
    if cause != "refus" or s.get("raison") == "mefiance":
        eprouver_emotion(monde, id, autre, cause, delta)
    reconsiderer(monde, id)
    from .pnj import _chroniquer
    from .social import _qui
    changes = [b for b in BANDES if bandes[b] != r["bandes"][b]]
    if changes or cause in ("dette_honoree", "service_rendu"):
        _chroniquer(monde, id, f"{_qui(monde, id)} envers {_qui(monde, autre)} : {resume(r)} ; {cause}.", "relation")
        monde.data["chronique"][-1].update(relation=autre, cause=cause, bandes=copy.deepcopy(r["bandes"]),
                                          mefiance_levee=bandes["mefiance"] and not r["bandes"]["mefiance"], service=s.get("service", s.get("objet")))


def souvenir(monde, id, s):
    """Crochet unique, après inscription. Un effet reçu s'inscrit chez le bénéficiaire."""
    from .esprits import memoriser
    from . import agendas
    from .voix import identifie, auteur_dit, source_dite
    t = s["type"]
    if t == "rumeur" and s.get("evenement", {}).get("type") == "intention_lue":
        return
    if id == "joueur":
        return
    autre = s.get("auteur", s.get("locuteur", s.get("de", s.get("qui"))))
    if t == "restitution":
        if s.get("ponctuel") and identifie(monde, id, autre):
            _appliquer(monde, id, autre, "pret_rendu", s)
        return
    if t == "engagement_pris":
        if doit(monde, id, s["pour"]):
            memoriser(monde, id, {"type": "dette_honoree", "de": s["pour"], "service": "demande", "preuve": "solde:" + s["preuve"]})
        return
    if t in ("engagement_tenu", "engagement_abandonne") and "pour" in s:
        if "rendre" in s["condition"]:
            return  # la remise attribuée constate la restitution, une seule fois
        pour = s["pour"]
        if pour != "joueur":
            from .esprits import esprit
            consequence = {"type": t, "de": id, "pour": pour, "condition": s["condition"], "minute": s["minute"], "preuve": s["preuve"]}
            connus = esprit(monde, pour)["memoire"]
            recu = any(x["type"] in ("nourri", "recu") and x.get("de") == id
                       and x.get("objet") == s["condition"].get("objet") and x["minute"] == s["minute"] for x in connus)
            if t == "engagement_tenu" and recu and identifie(monde, pour, id):
                memoriser(monde, pour, {k: v for k, v in consequence.items() if k != "pour"})
            else:
                esprit(monde, id)["suites"].append(consequence)
        return
    if t == "don" and "de" in s:
        t = "recu"
    if t == "dit" and s.get("attribut") == FIABLE and s.get("valeur") is False:
        from .esprits import lire
        alerte = next((x for x in lire(monde, id)["memoire"] if x["type"] == "a_prevenir"
                       and x["victime"] == s["a"] and x["auteur"] == s["sujet"]), None)
        if alerte and not alerte.get("tenu") and identifie(monde, s["a"], id):
            alerte["tenu"] = True
            memoriser(monde, s["a"], {"type": "prevenu", "de": id, "sujet": s["sujet"], "preuve": "service:" + alerte.get("preuve", str(alerte["minute"]))})
        return
    if t == "rumeur":
        from .social import accuse
        auteur = accuse(s["evenement"])
        if auteur and auteur != id:
            _appliquer(monde, id, auteur, "aveu" if s.get("aveu") else "rumeur",
                       dict(s, source="entendu" if s.get("aveu") else source_dite(monde, id, s["de"]),
                            preuve=s["evenement"].get("preuve") or hashlib.sha256(json.dumps(s["evenement"], sort_keys=True).encode()).hexdigest()),
                       1 if s.get("aveu") else percue(monde, id, s["de"])["confiance"] / 100)
        return
    if t == "avis_recu":
        source, _ = auteur_dit(s["source"])
        if s["valeur"] is False and source:
            _appliquer(monde, id, s["sujet"], "rumeur", s, percue(monde, id, source)["confiance"] / 100)
        return
    if t == "refus" and s.get("raison") in ("qui_va_la", "attente", "absent", "impossible", "eteinte", "rien", "place", "geste"):
        return  # une incapacité ou une demande d'identité n'est pas un affront
    if t == "recu" and s.get("livraison"):
        return  # une livraison payée n'est pas un don
    if t == "recu" and s.get("pret"):
        t = "pret_recu"
    # Une prestation déjà convenue conserve son épreuve d'engagement ;
    # la réception d'un repas ne crée pas en plus un service spontané.
    prestation = (t == "nourri" and agendas.en_cours(
        monde, autre, objet=s.get("objet"), personne=id, actifs=True)) if autre else False
    if (t in ("recu", "nourri") and not s.get("demande") and not prestation
            and s.get('service_utile') is True):
        t = "service_rendu"
    if t == "vol_surpris" and s.get("victime", id) != id:
        _appliquer(monde, id, autre, "tort_tiers", s, tiers=s.get("victime"))
        return
    if t in ("vu_porter", "vu_agir") and (t == "vu_porter" or s.get("operation") == "prendre"):
        from .esprits import esprit
        from .vol import proprietaire
        o = s.get("objet")
        if o in monde.objets and proprietaire(monde, monde.objets[o]) == id:
            portages = esprit(monde, id)["portages"]
            precedent = portages.get(o)
            if precedent and precedent["auteur"] == autre:
                s["preuve"] = precedent["preuve"]
            else:
                portages[o] = {"auteur": autre, "preuve": s["preuve"]}
    if t in ("subi", "pousse") and autre is None:
        return
    if t == "vu_agir":
        if s.get("operation") in ("frapper", "assommer", "enfermer", "tuer") and s.get("objet") in ("joueur", *monde.data["esprits"]):
            if s["objet"] != id:
                _appliquer(monde, id, autre, "violence_vue", s, 0.8 if s.get("par") == "ouie" else 1)
            return
        if s.get("operation") == "pousser":
            if s.get("objet") != id:
                _appliquer(monde, id, autre, "poussee_vue", s)
            return
        from .vol import proprietaire
        victime = s.get("victime") or proprietaire(monde, monde.objets[s["objet"]])
        _appliquer(monde, id, autre, "vu_agir" if victime == id else "tort_tiers", s,
                   0.8 if s.get("par") == "ouie" else 1, tiers=victime if victime != id else None)
        return
    if t not in EPREUVES:
        return
    if t in ("nourri", "recu", "pret_recu", "prevenu", "engagement_tenu", "engagement_abandonne", "parole_rompue",
             "refus", "passage_accorde", "service_rendu"):
        if autre is None or not identifie(monde, id, autre):
            return
    from .esprits import lire
    nouveau_service = t == "service_rendu" and autre + ':' + s['preuve'] not in lire(monde, id)['preuves_relations']
    _appliquer(monde, id, autre, t, s)
    if nouveau_service:
        from .services import lever_refus
        lever_refus(monde, id, autre, s.get("preuve"))
    if (t in ("recu", "service_rendu", "prevenu", "passage_accorde") or t == "pret_recu" and s.get("demande")) and autre != "joueur" and doit(monde, autre, id):
        memoriser(monde, autre, {"type": "dette_honoree", "de": id, "service": "demande" if s.get("demande") else t, "montant": EPREUVES[t].get("dette", 0), "preuve": "solde:" + s["preuve"]})


def avis(monde, id, autre, valeur, source, certitude):
    from .esprits import memoriser
    memoriser(monde, id, {"type": "avis_recu", "sujet": autre, "valeur": valeur, "source": source, "certitude": certitude})


def annoncer_suites(monde, auteur, pour, lignes):
    """Une suite hors de vue s'apprend dans une conversation, avec une parole entendue."""
    if auteur == "joueur" or pour == "joueur":
        return
    from .esprits import esprit, memoriser
    from .voix import identifie
    from .social import faire_entendre, _qui
    e = esprit(monde, auteur)
    if not identifie(monde, pour, auteur):
        return
    suites = [s for s in e["suites"] if s["pour"] == pour]
    for s in suites:
        e["suites"].remove(s)
        issue = "tenu" if s["type"] == "engagement_tenu" else "abandonné"
        texte = f"{_qui(monde, auteur)} dit à {_qui(monde, pour)} avoir {issue} sa parole."
        faire_entendre(monde, auteur, pour, texte, [], lignes, [], suites=False)
        from .pnj import _chroniquer
        _chroniquer(monde, auteur, texte, "social")
        memoriser(monde, pour, {k: v for k, v in s.items() if k not in ("pour", "minute")})


def partager(monde, id, minute):
    """Une heure perçue ensemble dans l'épreuve, sans dépendre des consultations ni des sauvegardes."""
    from .esprits import esprit, percus, memoriser
    from .deliberation import urgents
    from .corps import au_chaud
    e = esprit(monde, id)
    if e["compagnie_minute"] >= minute:
        return
    e["compagnie_minute"] = minute
    if not urgents(monde, id):
        return
    abri = (e["intention"] or {}).get("but", {}).get("type") == "abri"
    if not (abri or au_chaud(monde, id)):
        return
    vus, _ = percus(monde, id)
    for autre in sorted(vus):
        if autre == id or autre != "joueur" and (autre not in monde.objets or monde.objets[autre]["type"] != "personnage"):
            continue
        etat = e["croyances"].get(autre, {}).get("etat", {}).get("valeur", {})
        if not any(etat.get(b) for b in ("faim", "chaleur", "repos")):
            continue
        n = e["compagnie"].get(autre, 0) + 1
        e["compagnie"][autre] = n % 60
        if n >= 60:
            memoriser(monde, id, {"type": "epreuve_partagee", "de": autre})


def resume(r):
    mots = [texte for b, texte in (("mefiance", "se méfie"), ("confiance", "fait confiance"),
                                  ("rancune", "en veut"), ("peur", "craint"),
                                  ("ascendant", "reconnaît une autorité")) if r["bandes"][b]]
    if dette_notable(r):
        mots.append("se sent redevable")
    return ", ".join(mots) or "reste prudent"


def verifier(monde, id):
    from .esprits import lire
    e = lire(monde, id)
    assert isinstance(e["preuves_relations"], dict) and all(isinstance(p, str) and isinstance(v, dict) and set(v) == {"niveau", "effets"}
        and v["niveau"] in (0.5, 0.8, 1.0) and isinstance(v["effets"], dict) and set(v["effets"]) <= set(AXES)
        and all(type(d) is int for d in v["effets"].values()) for p, v in e["preuves_relations"].items()), "Preuves de relation invalides"
    assert isinstance(e["portages"], dict) and all(isinstance(o, str) and isinstance(p, dict) and set(p) == {"auteur", "preuve"}
        and all(isinstance(v, str) for v in p.values()) for o, p in e["portages"].items()), "Portages retenus invalides"
    assert type(e["compagnie_minute"]) is int and isinstance(e["compagnie"], dict) and all(
        isinstance(x, str) and type(n) is int and 0 <= n < 60 for x, n in e["compagnie"].items()), "Compagnie retenue invalide"
    assert isinstance(e["suites"], list) and all(
        isinstance(s, dict) and set(s) == {"type", "de", "pour", "condition", "minute", "preuve"}
        and s["type"] in ("engagement_tenu", "engagement_abandonne") and s["de"] == id
        and isinstance(s["pour"], str) and isinstance(s["condition"], dict) and type(s["minute"]) is int
        for s in e["suites"]), "Suites de parole invalides"
    liens = (monde.objets[id].get("profil") or {}).get("liens", {})
    assert isinstance(liens, dict), "Liens de départ invalides"
    for x, axes in liens.items():
        # Un lien survit à la mort de l'autre (``corps.mourir`` : la dépouille garde son identifiant).
        assert x != id and (x == "joueur" or x in monde.objets and monde.objets[x]["type"] in ("personnage", "depouille")), "Lien sans personnage"
        assert isinstance(axes, dict) and set(axes) <= set(AXES), "Axes de lien invalides"
        assert all(type(v) is int and 0 <= v <= 100 for v in axes.values()), "Valeur de lien invalide"
    for x, r in lire(monde, id)["relations"].items():
        assert isinstance(x, str) and x != id and isinstance(r, dict), "Relation invalide"
        ancien = "ascendant" not in r
        assert set(r) == {*(a for a in AXES if not ancien or a != "ascendant"),
                           "minute", "source", "motifs", "bandes", "ancrages"}, "Relation mal formée"
        assert ("ascendant" in r["bandes"]) == (not ancien), "Bande d'ascendant manquante"
        assert ("ascendant" in r["ancrages"]) == (not ancien), "Ancre d'ascendant manquante"
        r = _completer(r)
        assert all(type(r.get(a)) is int and 0 <= r[a] <= 100 for a in AXES), "Axe de relation invalide"
        assert type(r["minute"]) is int and r["minute"] >= 0 and isinstance(r["source"], str), "Date de relation invalide"
        assert set(r["bandes"]) == set(BANDES) and all(type(v) is bool for v in r["bandes"].values()), "Bandes invalides"
        assert isinstance(r["motifs"], list) and len(r["motifs"]) <= 3, "Motifs invalides"
        assert isinstance(r["ancrages"], dict) and set(r["ancrages"]) == {"affection", "rancune", "peur", "ascendant"}, "Ancres invalides"
        assert all(isinstance(v, list) and len(v) == 2 and isinstance(v[0], (int, float)) and math.isfinite(v[0])
                   and 0 <= v[0] <= 100 and type(v[1]) is int and v[1] >= 0 for v in r["ancrages"].values()), "Ancre de relation invalide"
        for m in r["motifs"]:
            assert m["type"] in EPREUVES and type(m["minute"]) is int and set(m["effets"]) <= set(AXES), "Motif invalide"
