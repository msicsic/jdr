"""Besoins, pulsions et délibération des PNJ ; planificateur borné sur leurs croyances.

Le profil d'auteur (``objet["profil"]``) déclare caractéristiques, traits, valeurs
(``caractere``), capacités, besoins et pulsions. Le moteur fait évoluer les besoins minute par minute ;
une pulsion qui cesse d'être satisfaite aux yeux du PNJ est rompue : il la rétablit sans attendre
que son besoin presse, et une atteinte relance ce besoin. Le PNJ retient le but le plus
urgent pour lequel il trouve un plan, cherché sur ce qu'il croit, jamais sur la vérité du monde
(``choisir``) : à chaque minute (``deliberer``, le filet de ce qui monte peu à peu), à la fin de
son plan, après un geste manqué, et après un événement qui change sa situation (``pnj._avancer``,
``esprits.reconsiderer``). Les étapes sont ensuite revalidées sur l'état réel par ``pnj.py``.
Tout est déterministe ; Luna n'intervient pas.
"""
from . import agendas
from collections import Counter
from enum import IntEnum
from typing import NamedTuple

from .biens import a_autrui
from .caractere import ARGENT, STATS, interdit, verifier_situation, verifier_valeurs
from .corps import CORPS, SATIETE  # noqa: F401  (SATIETE : un repas, pour les gestes des PNJ)
from .esprits import esprit, lire, memoriser
from .relations import FIABLE, se_fie, se_mefie
from .spatial import porte_par

BESOINS = ("devoir", "biens", "securite", "faim", "repos", "chaleur")
CAPACITES = ("crochetage",)
OPERATIONS = ("aller", "prendre", "poser", "ouvrir", "fermer", "deverrouiller", "verrouiller",
              "crocheter", "manger", "inspecter", "reposer", "chauffer", "abriter", "alimenter", "allumer", "eteindre",
              "servir", "frapper", "assommer", "dans_le_dos", "ranimer", "fuite", "se_rendre", "degager",
              "dire", "demander", "acheter", "confier", "remettre", "demander_feu", "engager", "proposer")
PROGRESSIFS = ("aller", "reposer", "chauffer", "abriter")  # gestes qui durent : une minute sans les finir n'est pas un échec
EFFORTS = ("aller", "prendre", "poser", "crocheter", "frapper", "alimenter", "servir", "inspecter")  # gestes qui creusent
# demander_feu : tendre sa source à qui porte une flamme pour qu'il l'y allume (``echanges.demander_feu``).
# engager : payer quelqu'un pour une tâche (``echanges.engager``).
SOCIALES = ("dire", "demander", "acheter", "confier", "remettre", "demander_feu", "engager", "proposer")
A_VUE = ("crocheter",)  # gestes qui demandent d'y voir (``planification.chance_crochetage``)
PROFONDEUR = 4
PATIENCE = 30          # minutes passées à attendre une occasion (ou un passage) avant de renoncer
REPIT = 60             # minutes avant de reprendre un but abandonné, comptées de l'instant du renoncement
ATTEINTE = 30          # une pulsion qui cesse d'être satisfaite relance son besoin
VOL = 60               # un vol vu par sa victime
REPOS_FIN = 20         # reposé : il se relève
CHALEUR_FIN = 20       # réchauffé : il s'écarte du feu
SECURITE_FIN = 30      # rassuré : il quitte l'abri
# Ce qui inquiète (+) ou rassure (−) la sécurité, valeurs par défaut que chaque profil nuance
# (donnée ``securite``) : par minute pour ce qui dure, d'un coup pour un événement.
SECURITE = {"coup": 40, "violence": 25, "mort": 30, "noir": 0.5, "mefiance": 0.3, "bruit": 15, "illicite": 20,      # inquiète
            "eau": 2, "menace": 1, "crue": 10,     # par minute : 50 cm d'eau, l'eau attendue bientôt ;
                                                   # d'un coup : la voir gagner un lieu
            "detresse": 0.5,                       # demi-point/minute, pondéré par le lien perçu
            "lumiere": 0.2, "compagnie": 0.5, "ronde": 20}                 # rassure
REDEMANDE = 120        # minutes avant de redemander la même chose à qui vient de refuser
ATTENTE_PART = 60      # minutes pendant lesquelles on attend la part promise avant de redemander
REVOIR_FEU = 30        # un feu vu vif doit être revu avant que ce qui lui restait ne s'épuise
DESESPOIR = 95         # au-delà, le besoin l'emporte sur la crainte d'être vu ; sans abri, on appelle
APPEL_REPIT = 10       # minutes entre deux appels à l'aide
# L'effet de seuil (``urgents``) : apaisé, un besoin ne presse de nouveau qu'à son seuil + REPRISE ;
# il n'interrompt le plan en cours d'un autre besoin que s'il presse plus que lui d'INERTIE.
REPRISE = 15
INERTIE = 5


def profil(monde, id):
    return monde.objets[id].get("profil")


def seuils(monde, id):
    """Seuil d'urgence de chaque besoin : ceux du corps, communs ; ceux de l'esprit, du profil."""
    p = profil(monde, id)
    return {**{nom: regle["urgence"] for nom, regle in CORPS.items()},
            **{nom: b["urgence"] for nom, b in (p or {}).get("besoins", {}).items()}}


def reserve(monde, id):
    """Parts qu'un personnage garde pour lui de chaque ressource comptée qu'il possède."""
    return (profil(monde, id) or {}).get("reserve", 1)


def besoin_de_part(o):
    """Catégorie d'une ressource comptée : vivres ou combustible. Le nom historique « chaleur »
    ne garantit pas qu'il chauffe : l'emploi vient de ``part_pour`` ou de la source à recharger."""
    if o["type"] == "nourriture":
        return "faim"
    return "chaleur" if "combustible" in o.get("usages", []) else None


def parts(o):
    return o.get("portions", o.get("charges", 0))


def part_pour(monde, id, objet, besoin, connus=None):
    """Une ressource pour ce besoin, selon les sources connues : du combustible ne chauffe
    qu'avec un foyer qui le brûle. La catégorie du consommable ne garantit pas son emploi."""
    from .perception import recharge
    o = monde.objets[objet]
    categorie = besoin_de_part(o)
    if categorie is None or categorie != besoin:
        return False
    if besoin != "chaleur":
        return True
    return any(monde.objets[s].get("foyer") and recharge(monde.objets[s], o)
               for s in (_connus(monde, id) if connus is None else connus))


def verifier_profil(monde, id, p):
    assert (isinstance(p, dict) and {"caracteristiques", "traits", "valeurs", "capacites", "besoins", "pulsions"}
            <= set(p) <= {"caracteristiques", "traits", "valeurs", "capacites", "besoins", "pulsions",
                          "reserve", "securite", "protege", "situation", "alerte", "liens"}), "Profil de PNJ mal formé"
    # Le seuil d'alerte, en crans de l'ouïe commune (``ouie.INTENSITES``) : un bruit inconnu qui lui
    # parvient à ce niveau l'envoie voir sans attendre (``alarme``).
    assert type(p.get("alerte", 0)) is int and -2 <= p.get("alerte", 0) <= 9, "Seuil d'alerte de PNJ invalide"
    verifier_situation(p.get("situation", {}))
    assert (isinstance(p.get("protege", []), list) and all(
        x in monde.objets and monde.objets[x]["type"] in ("personnage", "depouille") and x != id
        for x in p.get("protege", []))), "Protégés de PNJ invalides"
    assert type(p.get("reserve", 1)) is int and 0 <= p.get("reserve", 1) <= 10, "Réserve de PNJ invalide"
    assert (isinstance(p.get("securite", {}), dict) and set(p.get("securite", {})) <= set(SECURITE)
            and all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in p.get("securite", {}).values())),         "Sécurité de PNJ invalide"
    assert set(p["caracteristiques"]) == set(STATS) and all(
        type(v) is int and 1 <= v <= 20 for v in p["caracteristiques"].values()), "Caractéristiques de PNJ invalides"
    assert isinstance(p["traits"], str) and len(p["traits"]) <= 600, "Traits de PNJ invalides"
    verifier_valeurs(p["valeurs"])
    assert set(p["capacites"]) <= set(CAPACITES), "Capacité inconnue"
    for nom, b in p["besoins"].items():
        # Faim, froid et fatigue relèvent du corps, commun à tous : le profil ne les règle pas.
        assert (nom in BESOINS and nom not in CORPS and set(b) == {"depart", "derive_heure", "urgence"}
                and all(isinstance(b[k], (int, float)) for k in b)
                and 0 <= b["depart"] <= 100 and 0 < b["urgence"] <= 100), "Besoin de PNJ invalide"
    for pulsion in p["pulsions"]:
        assert (set(pulsion) <= {"besoin", "condition", "delegue_a"} and pulsion.get("besoin") in seuils(monde, id)
                and condition_valide(monde, pulsion.get("condition"))
                and pulsion.get("delegue_a", "joueur") == "joueur"), "Pulsion de PNJ invalide"


def condition_valide(monde, c):
    """Vocabulaire commun des buts : un objet en un lieu, un objet verrouillé, une ronde,
    une part de nourriture servie à quelqu'un, un feu entretenu, un objet prêté à rendre, un objet
    vendu à remettre."""
    return isinstance(c, dict) and (
        (set(c) == {"objet", "rendre"} and c["objet"] in monde.objets and c["rendre"] in monde.objets
         and monde.objets[c["rendre"]]["type"] in ("personnage", "depouille")) or
        # Un objet vendu à remettre à son acheteur (``echanges.differee``).
        (set(c) == {"objet", "remettre"} and c["objet"] in monde.objets
         and (c["remettre"] == "joueur" or c["remettre"] in monde.objets
              and monde.objets[c["remettre"]]["type"] in ("personnage", "depouille"))) or
        (set(c) == {"objet", "lieu"} and c["objet"] in monde.objets and c["lieu"] in monde.data["salles"])
        or (set(c) == {"objet", "servir"} and c["objet"] in monde.objets
            and monde.objets[c["objet"]]["type"] == "nourriture"
            and (c["servir"] == "joueur" or c["servir"] in monde.objets
                 and monde.objets[c["servir"]]["type"] in ("personnage", "depouille")))
        or (set(c) == {"objet", "verrouillee"} and c["objet"] in monde.objets and c["verrouillee"] is True)
        or (set(c) == {"objet", "allume"} and c["objet"] in monde.objets and "allume" in monde.objets[c["objet"]]
            and c["allume"] is True)
        or (set(c) == {"lieu", "periode"} and c["lieu"] in monde.data["salles"]
            and type(c["periode"]) is int and c["periode"] > 0))


def installer(monde, id):
    """Valeurs initiales des besoins et état des pulsions, à la première rencontre du profil."""
    p, e = profil(monde, id), esprit(monde, id)
    if not p:
        return
    for nom, b in p["besoins"].items():
        e["besoins"].setdefault(nom, float(b["depart"]))
    if len(e["pulsions"]) != len(p["pulsions"]):
        # Satisfaite (True) ; sinon un désir qui n'a jamais été satisfait (None), pas encore rompu.
        e["pulsions"] = [True if satisfaite(monde, id, x["condition"]) else None for x in p["pulsions"]]


def relancer(monde, id, besoin, montant):
    """Un événement (vol, atteinte à une pulsion) accroît un besoin déclaré ; un apaisement le réduit."""
    e = esprit(monde, id)
    if besoin in e["besoins"]:
        e["besoins"][besoin] = max(0.0, min(100.0, e["besoins"][besoin] + montant))


# --- Croyances utiles au plan -------------------------------------------------------------

def _lieu_cru(monde, id, sujet):
    c = lire(monde, id)["croyances"].get(sujet, {}).get("lieu")
    if c:
        return c["valeur"]
    o = monde.objets.get(sujet)
    # Les objets fixes font partie des lieux : on sait où ils sont sans les avoir revus.
    return o["lieu"] if o and not o.get("mobile") else None


def salle_crue(monde, id, sujet, profondeur=0):
    if sujet in monde.objets and porte_par(monde, sujet, id):
        return monde.objets[id]["lieu"]
    lieu = _lieu_cru(monde, id, sujet)
    if lieu is None or profondeur > PROFONDEUR:
        return None
    if lieu in monde.data["salles"]:
        return lieu
    if lieu == "joueur":
        return _lieu_cru(monde, id, "joueur")
    return salle_crue(monde, id, lieu, profondeur + 1)


def _cru(monde, id, sujet, attribut):
    c = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    return None if c is None else c["valeur"]


def _ouvert_cru(monde, id, sujet):
    etat = _cru(monde, id, sujet, "etat")
    return bool(etat and etat.get("ouverte"))


def _connus(monde, id):
    """Objets dont le PNJ a une croyance ou qu'il porte, dans un ordre stable."""
    croyances = lire(monde, id)["croyances"]
    return sorted(s for s in monde.objets if s in croyances or porte_par(monde, s, id))


def periodique(condition):
    """Une ronde : avoir inspecté un lieu depuis moins de ``periode`` minutes."""
    return "periode" in condition


def s_use(condition):
    """Une ronde expire, un feu baisse, un protégé a faim : d'eux-mêmes, sans que personne y ait
    porté atteinte."""
    return periodique(condition) or "allume" in condition or "servir" in condition


def _disponible_cru(monde, id, objet):
    """Une nourriture ou une réserve qu'il a vue épuisée ne lui sert plus."""
    etat = _cru(monde, id, objet, "etat")
    return not etat or etat.get("disponible", True)


# --- La mémoire des refus ------------------------------------------------------------------------
# Un refus se retient selon sa cause. Ce que l'autre ne peut pas (« impossible » : il ne voit pas
# comment ; « absent » : il ne l'a pas ; « eteinte » : sa flamme ne brûle pas ; « rien » : il n'a rien
# de tel) ou ce qu'il garde (« necessaire ») tient tant que le demandeur ne croit rien de nouveau des
# moyens de sa demande (``moyens_crus``), sans délai. Trop peu payé (« cher »), il tient pour ce prix :
# une offre plus haute reste possible (``planification._engager``). Un refus d'humeur ou de méfiance,
# et tout autre, tient ``REDEMANDE`` minutes. Chaque demande a sa dernière réponse refusée, gardée à
# part des souvenirs, que le temps n'efface pas (``esprit["refus"]``) ; une demande accordée l'efface.
CAUSES = ("impossible", "necessaire", "absent", "eteinte", "rien")
DETAILS_REFUS = ("objet", "besoin", "prix", "tache", "flamme", "offre")


def _meme_demande(s, autre, operations, objet, besoin):
    return (s["de"] == autre and s["operation"] in operations and s.get("objet", objet) == objet
            and s.get("besoin") == besoin)


def retenir_refus(monde, id, autre, operation, raison, souvenir=True, **detail):
    """``autre`` refuse à ``id`` cette demande (``operation`` sur ``objet``, ou ``besoin`` pour « as-tu… ? ») :
    il s'en souvient (``souvenir``), et retient cette réponse à la place de la précédente pour la même
    demande, avec, quand le refus a une cause, ce qu'il croit alors de ses moyens (``moyens_crus``).
    « Qui va là ? » n'est pas un refus : il s'est nommé, il redemande."""
    detail = {k: v for k, v in detail.items() if k in DETAILS_REFUS and v is not None}
    if souvenir:
        memoriser(monde, id, {"type": "refus", "de": autre, "operation": operation, "raison": raison,
                              **{k: v for k, v in detail.items() if k in ("objet", "besoin")}})
    if raison == "qui_va_la":
        return
    oublier_refus(monde, id, autre, operation, detail.get("objet"), detail.get("besoin"))
    if operation == "acheter":
        # L'achat est la nouvelle réponse à cette demande de bien. À minute
        # égale, l'ancien refus gratuit ne doit pas cacher celui du marché.
        oublier_refus(monde, id, autre, "demander", detail.get("objet"), detail.get("besoin"))
    s = {"de": autre, "operation": operation, "raison": raison, "minute": monde.data["minutes"], **detail}
    if operation == "acheter" and detail.get("prix") and detail.get("objet"):
        from .pnj_propositions import entrees_refus
        s["offre"] = entrees_refus(monde, id, autre, detail["objet"],
                                   {"type": "pieces", "montant": detail["prix"]})
        if raison == "refus":
            s["raison"] = "persuasion"  # Un achat refusé est déjà une offre, pas une demande gratuite.
    if raison in CAUSES:
        s["cause"] = moyens_crus(monde, id, s)
    esprit(monde, id)["refus"].append(s)
    intention = lire(monde, id)["intention"]
    if operation in ("demander", "acheter") and detail.get("objet") and intention:
        esprit(monde, id)["demande_refusee"] = {"de": autre, "objet": detail["objet"],
                                                "besoin": intention["motif"]}


def oublier_refus(monde, id, autre, operation, objet=None, besoin=None):
    """La demande accordée (ou refusée de nouveau) : la réponse retenue ne vaut plus."""
    e = esprit(monde, id)
    e["refus"] = [s for s in e["refus"] if not (s["de"] == autre and s["operation"] == operation
                                                 and s.get("objet") == objet and s.get("besoin") == besoin)]


def refus_retenu(monde, id, autre, operations, objet=None, besoin=None):
    """La dernière réponse refusée d'``autre`` à cette demande (``operations`` : les façons de la faire,
    demander ou acheter), si elle tient encore (``tient``) ; None sinon. Un refus sans objet (le
    passage) vaut pour tout objet."""
    refus = [s for s in lire(monde, id).get("refus", ()) if _meme_demande(s, autre, operations, objet, besoin)]
    dernier = max(refus, key=lambda s: s["minute"], default=None)
    return dernier if dernier is not None and tient(monde, id, dernier) else None


def tient(monde, id, s, connus=None):
    """Le refus ``s`` tient-il encore ? Pour une cause, tant qu'il ne croit aucun moyen qu'il ne croyait
    déjà au refus : ce qu'il apprend qui en ôte un (le bois vu épuisé, une porte crue fermée à clé) ne le
    lève pas, revoir la même chose non plus. Pour un prix trop bas, toujours (pour ce prix seulement).
    Sinon, depuis moins de ``REDEMANDE`` minutes."""
    if "offre" in s:
        from .biens import prix
        from .pnj_propositions import refus_tient
        montant = ((prix(monde, s["objet"], besoin_de_part(monde.objets[s["objet"]]) is not None)
                    or s.get("prix", 0)) if s["operation"] == "acheter" else s["offre"]["gain"])
        return refus_tient(monde, id, s, {"type": "pieces", "montant": montant})
    if s["raison"] in CAUSES and "cause" in s:
        avant = {tuple(f) for f in s["cause"]}
        return all(tuple(f) in avant for f in moyens_crus(monde, id, s, connus))
    if s["raison"] == "cher":
        return True
    if s["raison"] == "oppose":
        # On s'oppose à lui sur cette chose : tant qu'il croit l'opposant là où elle est.
        return (monde.data["minutes"] - s["minute"] < REDEMANDE
                and salle_crue(monde, id, s["de"]) == salle_crue(monde, id, s["objet"]))
    return monde.data["minutes"] - s["minute"] < REDEMANDE


# --- Un geste défait sous ses yeux -------------------------------------------------------------
# Ce qu'un PNJ vient de faire de sa main à une chose (l'ouvrir, la fermer, la verrouiller, l'allumer…),
# un autre le défait sous ses yeux : on s'oppose à lui. Il ne le refait pas aussitôt, ni rien d'autre
# sur cette chose, tant qu'il croit l'opposant là (``tient``, raison « oppose ») ; il s'y oppose
# autrement (rester, appeler, dire). Une règle pour tous, joueur compris comme auteur.
ETATS_DONNES = ("ouverte", "verrouillee", "allume")
DEFAIT = 5             # minutes pendant lesquelles un état qu'il a donné est « ce qu'il vient de faire »


def changer_etat(monde, auteur, objet, attribut, avant):
    """``auteur`` (un PNJ ou le joueur) vient de changer de sa main l'``attribut`` d'``objet``, qui
    valait ``avant``. Chaque PNJ qui le voit faire, et qui venait lui-même de lui donner cette valeur
    (``esprit["donne"]``), retient qu'on s'oppose à lui sur cette chose (``retenir_refus``). Puis
    l'auteur PNJ retient l'état qu'il a donné. Rien ne change si la valeur est la même."""
    from .esprits import percoit, pnjs
    o = monde.objets[objet]
    apres, minute = o.get(attribut), monde.data["minutes"]
    if attribut not in ETATS_DONNES or bool(apres) == bool(avant):
        return
    for autre in pnjs(monde):
        if autre == auteur or not profil(monde, autre):
            continue
        donne = lire(monde, autre)["donne"].get(objet, {}).get(attribut)
        if (donne is not None and bool(donne[0]) == bool(avant) and minute - donne[1] < DEFAIT
                and percoit(monde, autre, auteur)):
            retenir_refus(monde, autre, auteur, "defaire", "oppose", souvenir=False, objet=objet)
            donnes = esprit(monde, autre)["donne"]
            del donnes[objet][attribut]
            if not donnes[objet]:
                del donnes[objet]
    if auteur in monde.objets and profil(monde, auteur):
        donne = esprit(monde, auteur)["donne"]
        for k in list(donne):
            donne[k] = {a: v for a, v in donne[k].items() if minute - v[1] < DEFAIT}
            if not donne[k]:
                del donne[k]
        donne.setdefault(objet, {})[attribut] = [bool(apres), minute]


def contrarie(monde, id, objet):
    """Quelqu'un s'oppose à lui sur cette chose, et l'opposition tient (``changer_etat``)."""
    return any(s["operation"] == "defaire" and s.get("objet") == objet and tient(monde, id, s)
               for s in lire(monde, id)["refus"])


def moyens_crus(monde, id, s, connus=None):
    """[[sorte, sujet, lieu, allumé]] : ce que le demandeur ``id`` croit des moyens de la demande ``s``,
    ce qui pourrait la rendre possible, trié ; jamais l'état réel.

    Les moyens : pour une part ou un objet, ce qu'il lui demande, s'il ne l'a pas vu épuisé, où il le
    croit ; pour du feu, la source et la flamme, allumées ou non ; pour « as-tu… ? », ce qu'il croit
    que l'autre possède de ces ressources ; pour une tâche, où est ce qu'elle vise et tout ce qu'elle
    emploierait (chaque réserve de ce que brûle le feu à entretenir et de quoi l'allumer, les clés de
    ce qu'il faut fermer à clé). Puis leurs abords : les contenants et les portes de leur salle qu'il
    ne croit pas fermés à clé, et où sont leurs clés. L'état que la tâche doit changer (le feu éteint)
    n'est pas un moyen : c'est ce qu'il demande. Ils changent quand il apprend une ressource, voit
    l'autre avec du bois, croit une porte ouverte, entend une rumeur."""
    from .perception import recharge
    from .vol import proprietaire
    objets, salles = monde.objets, monde.data["salles"]
    croyances = lire(monde, id)["croyances"]
    connus = _connus(monde, id) if connus is None else connus
    op, o = s["operation"], s.get("objet")
    faits, abords = set(), []

    def etat(k):
        return (croyances.get(k, {}).get("etat") or {}).get("valeur") or {}

    def ressources(besoin):
        return [k for k in connus if part_pour(monde, id, k, besoin, connus)]

    def moyen(k):
        if besoin_de_part(objets[k]) and etat(k).get("disponible") is False:
            return   # Vu épuisé : ce n'est plus un moyen.
        allume = etat(k).get("allume") if "allume" in objets[k] else None
        faits.add(("moyen", k, _lieu_cru(monde, id, k), allume))
        abords.append(k)

    if op == "enqueter":
        moyens = [k for k in ressources(s.get("besoin")) if proprietaire(monde, objets[k]) == s["de"]]
    elif op in ("engager", "confier"):
        cible, moyens = objets.get(o), []
        if cible is not None:
            faits.add(("cible", o, _lieu_cru(monde, id, o), None))
            abords.append(o)
            if s.get("tache") == "allume":
                moyens = [k for k in connus if recharge(cible, objets[k]) or "allumage" in objets[k].get("usages", [])]
            elif s.get("tache") == "verrouillee":
                moyens = [k for k in connus if o in objets[k].get("ouvre", [])]
    elif op == "demander_feu":
        moyens = [k for k in (o, s.get("flamme")) if k in objets]
    else:
        # Une part ou un objet : ce qu'il lui demande, pas les ressources des autres.
        moyens = [o] if o in objets else []
    for k in moyens:
        moyen(k)

    def ouvert(x):
        if not (croyances.get(x, {}).get("verrouillee") or {}).get("valeur"):
            faits.add(("ouvert", x, None, None))
        for k in connus:
            if x in objets[k].get("ouvre", []):
                faits.add(("cle", k, _lieu_cru(monde, id, k), None))

    for k in abords:
        vus, lieu = set(), _lieu_cru(monde, id, k)
        while lieu in objets and lieu not in vus and objets[lieu]["type"] == "contenant":
            vus.add(lieu)
            ouvert(lieu)
            lieu = _lieu_cru(monde, id, lieu)
        if lieu in salles:
            for sortie in salles[lieu]["sorties"].values():
                if sortie.get("porte") in objets:
                    ouvert(sortie["porte"])
    return sorted((list(f) for f in faits), key=str)


def appels_vains(monde, id, qui):
    """Lieux cherchés en vain, jusqu'à un nouvel indice dans ce lieu (``esprits.croire``,
    ``ouie._bruit_inconnu``). Ni le temps écoulé ni un constat d'absence ne les rouvrent."""
    return set(lire(monde, id)["recherches"].get(qui, {}))


def recherche_vaine(monde, id, qui, salle):
    """Le résultat d'une recherche se retient comme celui d'une demande, hors mémoire bornée."""
    esprit(monde, id)["recherches"].setdefault(qui, {})[salle] = monde.data["minutes"]


def indice_recherche(monde, id, salle, qui=None):
    """Un nouvel indice rouvre ce lieu pour la personne identifiée, sinon pour les personnes
    cherchées, sans attribuer l'indice à l'une d'elles ni rouvrir les autres lieux."""
    recherches = esprit(monde, id)["recherches"]
    for sujet in ([qui] if qui is not None else recherches):
        recherches.get(sujet, {}).pop(salle, None)


def cherche(monde, id, qui):
    """Son but ou son plan vise ``qui`` : il le cherche, pour lui demander, le prévenir, le servir."""
    i = lire(monde, id)["intention"]
    if not i:
        return False
    return qui in i["but"].values() or any(
        x.get("cible") == qui or (x.get("contenu") or {}).get("cherche") == qui for x in i["plan"])


def _sur_place(monde, id, intention):
    """Assis pour se reposer, près du feu, à l'abri : un geste qui dure là où il se tient."""
    return bool(intention) and intention["motif"] in PROGRES and any(
        x["operation"] == GESTE_PROGRES[intention["motif"]] for x in intention["plan"])


def _passe_avant(monde, id, intention):
    """Ce qui passe avant l'attente d'être rejoint : un besoin qui presse, la parole donnée, prévenir
    un protégé, un réflexe, une stratégie, et ce qu'il fait sur place (il y attend aussi bien).
    La routine, aller voir un bruit, rétablir ce qui ne presse pas, l'argent lui cèdent."""
    return bool(intention) and (intention["motif"] in urgents(monde, id)
                                or intention["motif"] in ("engagement", "alerte", "strategie", "rejoint")
                                or intention["but"]["type"] == "prevenir" or _sur_place(monde, id, intention))


def rejoint(monde, id, qui):
    """``id`` et ``qui`` se sont retrouvés (ils se voient ou se parlent) : le rendez-vous convenu à un
    appel (``appel``) est tenu, l'attente de l'un et la venue de l'autre sont finies."""
    from .appel import retrouves
    retrouves(monde, id, qui)


def attendre(monde, id, minute):
    """Le rendez-vous convenu à un appel (``appel.tenir``) : tenu quand ils se retrouvent, échu sinon ;
    tant qu'il dure, attendre est un but (``_plan_attendre``) qui cède à ce qui presse davantage, et
    venir une parole due (``appel.plan_venir``)."""
    from .appel import tenir
    tenir(monde, id, minute)


def _plan_attendre(monde, id):
    """Attendre sur place d'être rejoint : aucun geste, il reste où il a répondu. Occupé sur place
    (``_sur_place``), il y reste à ce qu'il fait : ce but-là le garde."""
    e = lire(monde, id)
    r = e["rejoint"]
    return ({"type": "attendre", "qui": r["qui"]}, []) if r and not _sur_place(monde, id, e["intention"]) else None


def _attendre_qui_vient(monde, id, resultat):
    """Le rendez-vous fournit le lieu où chercher son interlocuteur : qui doit venir le rejoint
    au lieu d'explorer ailleurs. Qui attend quelqu'un qui a promis de venir (« J'arrive ! »)
    ne va pas le chercher : un plan qui
    commence par aller à lui, ou le chercher, devient l'attendre là où il est, le temps convenu ; son
    but reprend quand ils se sont retrouvés. Un plan qui fait d'abord autre chose ici reste tel quel."""
    from .appel import _vise, plan_venir
    d = lire(monde, id)["rejoindre"]
    if resultat and d and _vise({"but": resultat[0], "plan": resultat[1]}, d["qui"]):
        # Le même objectif cherche un interlocuteur qui vient de lui dire où venir. Le
        # rendez-vous est un moyen connu de ce plan, même d'une voix encore sans identité.
        return plan_venir(monde, id) or resultat
    r = lire(monde, id)["rejoint"]
    if not resultat or not r or not r["vient"]:
        return resultat
    but, etapes = resultat
    qui = r["qui"]
    if not _vise({"but": but, "plan": etapes}, qui) or etapes and etapes[0]["operation"] not in ("aller", "inspecter") and not (
            etapes[0].get("cible") == qui or (etapes[0].get("contenu") or {}).get("cherche") == qui):
        return resultat
    return {"type": "attendre", "qui": qui}, []


def promesse_en_cours(monde, id, objet, remise=None):
    """Une part promise et pas encore servie, dans le délai où il l'attend. Une recharge est
    servie quand le feu est revu vif ; une part à remettre, seulement à sa réception réelle.
    ``remise`` distingue ces deux services sans les confondre dans un plan."""
    e = lire(monde, id)
    for s in reversed(e["memoire"]):
        if s["type"] in ("promesse_annulee", "creance") and s.get("objet") == objet:
            return None
        if s["type"] == "nourri" and s.get("objet") == objet:
            return None
        if s["type"] == "promis" and s["objet"] == objet:
            if remise is not None and bool(s.get("remise")) != remise:
                return None
            # Reçue, annulée ou remboursée : la part à remettre n'est plus attendue.
            if s.get("part") and any(x["type"] in ("recu", "promesse_annulee", "creance") and x.get("objet") == s["part"]
                                     for x in e["memoire"]):
                return None
            feu = e["croyances"].get(s.get("foyer"), {}).get("etat")
            if (monde.data["minutes"] - s["minute"] >= ATTENTE_PART or feu and feu["minute"] >= s["minute"]
                    and feu["valeur"].get("allume") and not feu["valeur"].get("faible")):
                return None
            return s["de"]
    return None


def satisfaite(monde, id, condition):
    # Une charge envers quelqu'un qu'il sait mort n'a plus d'action à accomplir.
    destinataire = next((condition[k] for k in ("servir", "rendre", "remettre") if k in condition), None)
    if destinataire and (_cru(monde, id, destinataire, "etat") or {}).get("mort"):
        return True
    if "remettre" in condition:
        return False  # Un objet vendu se remet de la main à la main : le geste tient la parole.
    if "rendre" in condition:
        # Un objet prêté : rendu quand le prêt est clos (il est revenu à son propriétaire).
        from .biens import prets
        return not any(p["objet"] == condition["objet"] and p["a"] == id for p in prets(monde))
    if "servir" in condition:
        # Nourrir quelqu'un : tant qu'il ne le croit pas affamé (ce qu'il a vu de lui), rien à faire.
        # Une part promise, elle, se solde au geste (``echanges.tenu``).
        return not (_cru(monde, id, condition["servir"], "etat") or {}).get("faim")
    if periodique(condition):
        vu = lire(monde, id)["visites"].get(condition["lieu"])
        return vu is not None and monde.data["minutes"] - vu < condition["periode"]
    if "allume" in condition:
        # Un feu qui baisse n'est plus entretenu ; un feu vu vif il y a longtemps n'est plus sûr :
        # il faut aller le voir, et le recharger tant qu'il reste le temps d'aller chercher du bois.
        c = lire(monde, id)["croyances"].get(condition["objet"], {}).get("etat")
        return bool(c and c["valeur"].get("allume") and not c["valeur"].get("faible")
                    and monde.data["minutes"] - c["minute"] < REVOIR_FEU)
    if "lieu" in condition:
        # Le tenir soi-même ne suffit pas : l'objet doit être déposé (ou tenu par un autre) sur place.
        return (not porte_par(monde, condition["objet"], id)
                and salle_crue(monde, id, condition["objet"]) == condition["lieu"])
    return _cru(monde, id, condition["objet"], "verrouillee") is True and not _ouvert_cru(monde, id, condition["objet"])


def illicite(monde, id, objet, operation=None, confies=None):
    """Ce geste sur cet objet lèse-t-il quelqu'un ? Le bien d'autrui, hors ce qu'un prêt ou une
    garde confiée permettent (``biens.permis``, ``confies``) ; rien ne permet de consommer le bien
    d'autrui."""
    return a_autrui(monde, objet, id, operation, confies) is not None


def autorise(monde, id, objet):
    """Le bien d'autrui est interdit à qui a l'honnêteté à son comble ; pour les autres, c'est
    une faute dont le planificateur pèse le prix (``caractere.prix_faute``)."""
    return not (illicite(monde, id, objet) and interdit(monde, id, "honnetete"))


# --- Plans ---------------------------------------------------------------------------------
# Les plans viennent de la recherche (``planification``) ; ce module choisit le but.


def _plan_pulsion(monde, id, condition, tache=False):
    """Rétablir une pulsion ou tenir une parole donnée : la recherche (``planification``). ``tache`` :
    une pulsion à lui, qu'il peut payer quelqu'un de rétablir."""
    from .planification import planifier_pulsion
    return planifier_pulsion(monde, id, condition, tache)


def _plan_tache(monde, id, condition, payeur):
    """Faire la tâche que ``payeur`` lui a payée, par le plan de son devis."""
    from .planification import planifier_tache
    return planifier_tache(monde, id, condition, payeur)


def _pulsion_a_soi(monde, id, condition):
    return _plan_pulsion(monde, id, condition, tache=True)


def _plan_enquete(monde, id, besoin):
    """Rien de ce qu'il connaît n'apaise ce besoin : il demande à quelqu'un s'il en a
    (``planification.s_enquerir``)."""
    from .planification import s_enquerir
    return s_enquerir(monde, id, besoin)


# --- Sécurité ----------------------------------------------------------------------------

def taux(monde, id, cause):
    return (profil(monde, id) or {}).get("securite", {}).get(cause, SECURITE[cause])


def autour(monde, id):
    """Ce qui, dans sa salle, l'inquiète ou le rassure : la lumière sur sa case, ceux qu'il y voit
    ou y entend tout près, et la détresse effectivement perçue chez ses proches."""
    from .esprits import pnjs
    from .perception import eclairage
    o = monde.objets[id]
    niveau = eclairage(monde, o["lieu"], o.get("position") if monde.data.get("mode_cases") else None)["niveau"]
    presents = [x for x in [*pnjs(monde), "joueur"] if x != id
                and (monde.joueur["salle"] if x == "joueur" else monde.objets[x]["lieu"]) == o["lieu"]]
    if monde.data.get("mode_cases"):
        from .pnj import de_pres
        from .spatial import acteurs_vus
        vus = acteurs_vus(monde, id, presents)
        # Ceux qu'il voit, et ceux qu'il entend tout près, même dans son dos.
        autres = [x for x in presents if x in vus or de_pres(monde, id, x)]
    else:
        autres = presents if niveau else []
    from .relations import axes, confiance, mefiance
    liens = {x: axes(monde, id, x) for x in autres}
    from .signes import percus, actives
    signes = percus(monde, id)
    vus = {s["id"] for s in signes}
    detresses = {s["personnage"] for s in signes if s["signe"] in ("tremble", "fuit")}
    detresses.update(x for x, _, c in actives(monde, id)
                     if c["signe"] in vus and c["valeur"] in ("peur", "crainte", "inquietude"))
    # Un cri reconnu reste perçu jusqu'à la prochaine minute, même hors de vue.
    # Aucune lecture de la sécurité, du secours ou de l'intention privée d'autrui.
    detresses.update(s["qui"] for s in lire(monde, id)["memoire"]
                     if s["type"] == "detresse" and s["minute"] == monde.data["minutes"])
    poids = {x: (r["confiance"] + r["affection"]) / 100 for x, r in liens.items()}
    # Les appels venus d'ailleurs ne procurent pas de compagnie, mais le lien demeure.
    inquietude = [sum(axes(monde, id, x)[a] for a in ("confiance", "affection")) / 100
                  for x in sorted(detresses)]
    return {"compagnie": max([p for x, p in poids.items() if x not in detresses] or [0]),
            "detresse": max(inquietude or [0]),
            "peur": max([r["peur"] / 50 for r in liens.values()] or [0]),
            "lumiere": niveau > 0,
            "fiables": sorted(x for x, r in liens.items() if confiance(r) and x not in detresses),
            "mefiants": sorted(x for x, r in liens.items() if mefiance(r))}


def ressentir(monde, id, minutes=1):
    """La sécurité perçue pendant ``minutes`` dans les conditions de l'instant (``ecart_securite``) ;
    la vie des PNJ la fait évoluer au temps passé dans chaque état (``vecu``)."""
    ecart = ecart_securite(monde, id)
    if ecart is not None:
        relancer(monde, id, "securite", ecart * minutes)


def ecart_securite(monde, id):
    """Ce que gagne ou perd sa sécurité par minute, là où il se tient : le noir, la méfiance et l'eau
    où l'on se tient inquiètent, comme la détresse perçue ; la lumière et les compagnons calmes rassurent. None
    s'il ne ressent pas sa sécurité."""
    from .corps import conscient
    if not conscient(monde, id):
        return None
    if "securite" not in lire(monde, id)["besoins"] or monde.objets[id]["lieu"] not in monde.data["salles"]:
        return None
    a = autour(monde, id)
    ecart = (-taux(monde, id, "lumiere") if a["lumiere"] else taux(monde, id, "noir"))
    ecart += taux(monde, id, "mefiance") if a["mefiants"] else 0
    ecart -= taux(monde, id, "compagnie") * a["compagnie"]
    ecart += taux(monde, id, "detresse") * a["detresse"]
    ecart += taux(monde, id, "mefiance") * a["peur"]
    # L'eau où il se tient, d'autant plus qu'elle est haute ; sinon l'eau qu'il y attend bientôt.
    from .eau import NOYEE_CM, menacee, profondeur
    ici = monde.objets[id]["lieu"]
    p = profondeur(monde, ici)
    if p:
        ecart += 2 * taux(monde, id, "eau") * min(p, NOYEE_CM) / NOYEE_CM
    elif menacee(monde, id, ici):
        ecart += taux(monde, id, "menace")
    return ecart


def inquieter(monde, id, cause, signe=1):
    """Un événement inquiète (un bruit sans cause vue, un geste illicite) ou rassure (une ronde)."""
    if monde.objets.get(id, {}).get("profil"):
        relancer(monde, id, "securite", signe * taux(monde, id, cause))


def protecteurs(monde, protege):
    """Ceux dont le profil déclare protéger ce personnage."""
    from .corps import vivant, conscient
    if not vivant(monde, protege):
        return []
    return [x for x, o in monde.objets.items() if conscient(monde, x) and protege in (o.get("profil") or {}).get("protege", [])]


def appeler_a_l_aide(monde, id, minute):
    """À bout d'inquiétude et sans abri, il appelle : un son fort, que d'autres entendent. Celui
    qui voit menacé ce qu'il garde, là où il se tient (``menaces``), n'attend pas d'être à bout :
    il appelle dès que l'inquiétude le presse, si elle l'emporte sur son courage
    (``voix.prudent``) ; plus courageux, il reste et surveille."""
    from .corps import conscient
    if not conscient(monde, id):
        return
    from .voix import prudent
    e = esprit(monde, id)
    # Un besoin durable sans recours peut demander du secours sans lever la garde.
    # L'épisode est celui du besoin, pas celui des quarante derniers souvenirs.
    pressants = urgents(monde, id)
    appelees = e["detresses_appelees"]
    appelees[:] = [b for b in appelees if b in pressants]
    detresses = ([b for b in attentes(monde, id) if b != "securite"
                  and (not any(x["besoin"] == b for x in profil(monde, id)["pulsions"])
                       or any(x["besoin"] == b and not satisfaite(monde, id, x["condition"])
                              and not _delegue(monde, id, x) for x in profil(monde, id)["pulsions"]))]
                 if monde.objets[id]["lieu"] in gardes(monde, id)
                 and monde.objets[id]["lieu"] in _lieux_gardes(monde, id, siens=True) else [])
    nouvelle_detresse = any(b not in appelees for b in detresses)
    menace = ("securite" in urgents(monde, id) and prudent(monde, id)
              and monde.objets[id]["lieu"] in menaces(monde, id))
    secours = e["secours"]
    # Un agresseur perçu près de lui garde le désarroi ouvert (``defense.dangers``).
    from .defense import dangers
    danger = bool(dangers(monde, id))
    # Sortir du lieu menacé, ou repasser juste sous DESESPOIR, n'est pas être rassuré.
    # Le même épisode dure tant que son besoin de sécurité presse (effet de seuil commun).
    if (secours and not danger and e["besoins"].get("securite", 0) < DESESPOIR
            and "securite" not in urgents(monde, id)):
        secours["apaise"] = True
    if e["besoins"].get("securite", 0) < DESESPOIR and not menace and not danger and not nouvelle_detresse:
        return
    # Un appel attend sa réponse : tant que le désarroi qui l'a fait lancer dure, il ne le répète pas,
    # que quelqu'un soit venu sans l'apaiser ou que personne ne vienne.
    if (e["intention"] and e["intention"]["but"]["type"] == "abri"
            or secours and (minute - secours["minute"] < APPEL_REPIT
                            or not secours["apaise"] and not nouvelle_detresse)):
        return
    appelees.extend(b for b in detresses if b not in appelees)
    e["secours"] = {"minute": minute, "apaise": False}
    memoriser(monde, id, {"type": "appel"})
    from .ecoute import appel
    appel(monde, id)


def de_garde(monde, id, salle):
    """Le lieu relève de son devoir de garde : il y fait une ronde, y garde un bien ou y entretient
    quelque chose (une pulsion du devoir ou des biens), ou un protégé s'y trouve, à ce qu'il croit."""
    p = profil(monde, id) or {}
    for x in p.get("pulsions", []):
        c = x["condition"]
        if x["besoin"] in ("devoir", "biens") and (
                c.get("lieu") == salle or "objet" in c and salle_crue(monde, id, c["objet"]) == salle):
            return True
    return any(salle_crue(monde, id, x) == salle for x in p.get("protege", []))


def _voir_en_cours(e):
    """Le lieu qu'il est en train d'aller voir : il passe d'abord, il ne court pas d'un bruit à l'autre."""
    i = e["intention"]
    return i["but"].get("lieu") if i and i["but"]["type"] == "voir" else None


def bruit_a_voir(monde, id):
    """(lieu, motif) du plus récent bruit inconnu qu'il ira voir, d'un autre lieu ou de sa salle même
    (il va alors à portée de vue de l'endroit d'où il vient, ``planification.voir``) : son devoir de
    garde l'y envoie ; un bruit inhabituel (un fracas, un appel), son courage aussi, s'il en a plus
    que la moyenne. None s'il n'ira pas (``ouie``)."""
    from .caractere import NEUTRE, valeur
    from .ouie import HABITUDE, HABITUELS, resolu
    courageux = valeur(monde, id, "courage") > NEUTRE
    e = lire(monde, id)
    minute = monde.data["minutes"]
    # Celui qu'il est en train d'aller voir passe d'abord : il ne court pas d'un bruit à l'autre.
    en_cours = _voir_en_cours(e)
    a_voir = []
    for s in reversed(e["memoire"]):
        if s["type"] != "bruit" or resolu(monde, id, s):
            continue
        inhabituel = s["nature"] not in HABITUELS
        if not inhabituel and minute - e["visites"].get(s["salle"], -HABITUDE - 1) <= HABITUDE:
            continue  # Il en revient : un pas de plus ne l'y renvoie pas.
        if de_garde(monde, id, s["salle"]):
            a_voir.append((s["salle"], "devoir"))
        elif courageux and inhabituel:
            a_voir.append((s["salle"], "securite"))
    return next((x for x in a_voir if x[0] == en_cours), a_voir[0] if a_voir else None)


def alarme(monde, id):
    """(lieu, motif) d'un bruit inconnu, d'un autre lieu ou de sa salle même, qui l'envoie voir avant
    tout le reste, comme une alarme : l'appel d'un protégé dont il a reconnu la voix (le protecteur
    accourt), ou un bruit qui lui est parvenu au moins à son seuil d'alerte (``profil["alerte"]``, en
    crans de l'ouïe commune ; plus bas pour un gardien). None sinon. Les autres bruits vont à
    ``bruit_a_voir``."""
    from .ouie import resolu
    p = profil(monde, id) or {}
    e = lire(monde, id)
    alerte = p.get("alerte")
    for s in reversed(e["memoire"]):
        if s["type"] != "bruit" or resolu(monde, id, s):
            continue
        if s["nature"] == "appel" and s.get("qui") in p.get("protege", []):
            return s["salle"], "devoir"
        if alerte is not None and s.get("niveau", -99) >= alerte:
            return s["salle"], "devoir"
    return None


def _deja_dit(monde, id, a, sujet, attribut, valeur=None):
    """Il a déjà dit à ``a`` ce qu'il croit de ``sujet`` (``attribut``) ; avec ``valeur``, la dernière
    fois qu'il le lui a dit, c'était cette valeur (un fait dit l'est jusqu'à ce que la valeur change,
    quelle que soit la date de ce qu'il en croit)."""
    from .social import deja_dit
    return deja_dit(monde, id, a, {"type": "affirmation", "sujet": sujet, "attribut": attribut,
                                 "valeur": False if valeur is None else valeur})


def _a_dire(monde, id, victime, auteur):
    """Ce qu'il a à apprendre à ``victime`` d'``auteur`` : qu'il n'est pas fiable, s'il ne le lui a
    jamais dit ; où sont les biens qu'il lui a vu déplacer, s'il ne lui a pas déjà dit ce lieu-là et
    qu'il ne croit pas la victime auprès d'eux (elle les a sous les yeux, elle les y a peut-être
    posés). On prévient d'un fait que la victime ignore, à ce qu'il croit, pas d'un souvenir : chaque
    minute d'un même crochetage vu, chaque regard qui renouvelle ce qu'il croit, ne relance pas
    l'avertissement."""
    contenus = [] if _deja_dit(monde, id, victime, auteur, FIABLE) else [
        {"sujet": auteur, "attribut": FIABLE, "valeur": False}]
    for c in _lieux_a_dire(monde, id, victime, auteur):
        if _deja_dit(monde, id, victime, c["sujet"], "lieu", c["valeur"]):
            continue
        if salle_crue(monde, id, victime) == salle_crue(monde, id, c["sujet"]):
            continue
        contenus.append(c)
    return contenus


def _plan_prevenir(monde, id):
    """Un geste illicite vu contre un protégé : aller lui dire ce qu'il en ignore encore."""
    e = esprit(monde, id)
    for s in reversed(e["memoire"]):
        if s["type"] != "a_prevenir" or s["victime"] not in monde.objets:
            continue
        contenus = _a_dire(monde, id, s["victime"], s["auteur"])
        if not contenus:
            continue
        from .planification import _etape, rejoindre
        chemin = rejoindre(monde, id, s["victime"])
        if chemin is None:
            continue
        etapes, trouve = chemin
        if trouve:
            etapes += [_etape("dire", s["victime"], contenu=c) for c in contenus]
        return {"type": "prevenir", "qui": s["victime"]}, etapes
    return None


def _lieux_a_dire(monde, id, victime, auteur):
    """Les biens de ``victime`` qu'il a vu ``auteur`` déplacer : il lui dit où il les croit encore
    (``pnj._lieu_vu``), pour qu'elle aille les reprendre."""
    from .vol import proprietaire
    objets = []
    for s in lire(monde, id)["memoire"]:
        o = s.get("objet")
        if (s["type"] == "vu_agir" and s["auteur"] == auteur and "lieu" in s and o in monde.objets
                and o not in objets and proprietaire(monde, monde.objets[o]) == victime):
            objets.append(o)
    contenus = []
    for o in objets:
        lieu = _lieu_cru(monde, id, o)
        if lieu is not None and lieu != victime:
            contenus.append({"sujet": o, "attribut": "lieu", "valeur": lieu})
    return contenus


def _eclairee_crue(monde, id, salle):
    """Éclairée quand il y était, ou par une source qu'il y croit allumée ; une source portée, par
    lui ou par un autre, n'y compte pas (elle suit son porteur)."""
    vue = _cru(monde, id, salle, "etat")
    if vue is not None:
        return vue.get("eclairee", False)
    if monde.data["salles"][salle].get("lumiere_naturelle"):
        return True
    porteurs = {"joueur"} | {k for k, o in monde.objets.items() if o["type"] == "personnage"}
    return any("allume" in monde.objets[k] and (_cru(monde, id, k, "etat") or {}).get("allume")
               and not porte_par(monde, k, id) and _lieu_cru(monde, id, k) not in porteurs
               and salle_crue(monde, id, k) == salle for k in _connus(monde, id))


def sources_posees_crues(monde, id, salle):
    """{source: case ou None} : les sources qu'il croit allumées et posées dans cette salle (pas
    dans une main : elles suivent leur porteur), avec la case où il les croit."""
    croyances = lire(monde, id)["croyances"]
    trouvees = {}
    for k in _connus(monde, id):
        o = monde.objets[k]
        etat = (croyances.get(k, {}).get("etat") or {}).get("valeur") or {}
        if "allume" not in o or not etat.get("allume") or porte_par(monde, k, id):
            continue
        lieu = croyances.get(k, {}).get("lieu")
        if lieu is not None:
            if lieu["valeur"] != salle:
                continue
            trouvees[k] = lieu.get("case")
        elif not o.get("mobile") and o["lieu"] == salle:
            trouvees[k] = o.get("position")   # Un objet fixe fait partie du lieu.
    return trouvees


def apport_cru(monde, id, objet):
    """La lumière qu'il croit, devant ``objet``, d'une source allumée ou posée près de lui depuis
    qu'il y a vu clair ou sombre (croyance ``lumiere``, qui retient les sources qu'il croyait alors
    allumées là, ``allumees``) : selon la distance qu'il croit entre elles (portée d'une source,
    ``perception.PORTEES``), sans ce qui pourrait faire ombre, qu'il constatera devant
    (``pnj._assez_de_lumiere``). 0 si rien n'a changé à sa connaissance."""
    from .geometrie import distance
    from .perception import PORTEES
    c = lire(monde, id)["croyances"].get(objet, {})
    vue = c.get("lumiere")
    if vue is None:
        return 0
    salle = salle_crue(monde, id, objet)
    lieu = c.get("lieu")
    case = lieu.get("case") if lieu else monde.objets[objet].get("position") if not monde.objets[objet].get("mobile") else None
    if salle not in monde.data["salles"] or case is None:
        return 0
    apport = 0
    for k, ou in sources_posees_crues(monde, id, salle).items():
        if k in vue.get("allumees", ()) or ou is None:
            continue
        plein, penombre = PORTEES[max(1, min(3, monde.objets[k].get("luminosite", 1)))]
        d = distance(ou, case)
        apport = max(apport, 2 if d <= plein else 1 if d <= penombre else 0)
    return apport


def lumiere_crue(monde, id, salle):
    """Le niveau de lumière qu'il croit là (0 noir, 1 pénombre, 2 éclairé), sans ce qu'on y porte :
    celui qu'il y a vu en s'y tenant (``esprits.constater_lumiere`` ; d'ailleurs, sans la lueur
    d'une voisine qu'il y avait sur sa case, ``_niveau_cru``). Un lieu dont il ne sait rien :
    éclairé à plein s'il y croit le jour ou une source allumée (``_eclairee_crue``), sinon il
    l'imagine comme celui où il se tient (``noir_cru``) ; sans rien savoir d'aucun, rien ne lui
    fait croire le noir."""
    ici = monde.objets[id]["lieu"]
    vue = _cru(monde, id, salle, "etat")
    if vue is not None:
        return _niveau_cru(vue, salle == ici)
    if _eclairee_crue(monde, id, salle):
        return 2
    vue = _cru(monde, id, ici, "etat") if ici != salle and ici in monde.data["salles"] else None
    return 2 if vue is None else _niveau_cru(vue, False)


def _niveau_cru(vue, sur_place):
    """Sur place, la lumière qu'il a vue sur sa case ; d'ailleurs, celle que la salle tient de ses
    propres sources (``esprits.constater_lumiere`` : la lueur d'une voisine n'éclaire que le seuil)."""
    if not sur_place and "propre" in vue:
        return vue["propre"]
    return vue.get("niveau", 2 if vue.get("eclairee") else 0)


def noir_cru(monde, id, salle):
    """S'y croit-il dans le noir, sans ce qu'il porte ? Un lieu qu'il a vu obscur ; un lieu dont il
    ne sait rien, il l'imagine comme celui où il se tient."""
    vue = _cru(monde, id, salle, "etat")
    if vue is None:
        ici = monde.objets[id]["lieu"]
        vue = _cru(monde, id, ici, "etat") if ici != salle and ici in monde.data["salles"] else None
    return vue is not None and not vue.get("eclairee", False)


def peur_du_noir(monde, id):
    """Ce que le noir l'inquiète par minute (``SECURITE``, nuancé par son profil) ; 0 s'il ne
    s'inquiète de rien, ou pas du noir."""
    p = profil(monde, id) or {}
    return taux(monde, id, "noir") if "securite" in p.get("besoins", {}) else 0


def lumiere_utile(monde, id):
    """A-t-il besoin d'y voir, maintenant ou pour son plan ? Là où il se tient, ou là où son plan
    le mène, il croit le noir (``noir_cru`` : sans ce qu'il porte), et le noir l'inquiète ; ou il
    y a un geste qui demande d'y voir (crocheter) là où il ne croit pas la pleine lumière."""
    e = lire(monde, id)
    salle, peur = monde.objets[id]["lieu"], peur_du_noir(monde, id) > 0
    if salle not in monde.data["salles"]:
        return False
    if peur and noir_cru(monde, id, salle):
        return True
    for etape in e["intention"]["plan"] if e["intention"] else []:
        if etape["operation"] == "aller" and etape["lieu"] in monde.data["salles"]:
            salle = etape["lieu"]
        if (peur and noir_cru(monde, id, salle)
                or etape["operation"] in A_VUE and lumiere_crue(monde, id, salle) < 2):
            return True  # Sa chance au geste compte sur la lumière qu'il croit (``chance_crochetage``).
    return False


def _plan_abri(monde, id):
    """Se mettre à l'abri : rejoindre un lieu qu'il croit éclairé où se tient quelqu'un qu'il croit
    fiable, et y rester ; là où il est d'abord, s'il l'est déjà. Un lieu où il croit l'eau, ou l'y
    attend bientôt (``eau.menacee``), n'est pas un abri. Tant qu'il voit l'eau monter, l'abri est
    le plus haut lieu éclairé qu'elle ne menace pas, avec ou sans compagnie : elle monte par le bas.
    S'il n'en atteint aucun et que l'eau menace où il se tient, il gagne au moins le lieu où il attend
    le moins d'eau, éclairé ou non : piégé, il cherche d'abord à sortir de l'eau (``candidats``)."""
    from .eau import altitude, attendue, menacee, monte
    from .esprits import pnjs
    ici = monde.objets[id]["lieu"]
    # L'abri vers lequel il est en route garde la main tant qu'il en est encore un à ses yeux : un
    # abri meilleur apparu en chemin (quelqu'un de sûr qui passe ailleurs) ne le détourne pas, ni un
    # lieu qu'il traverse en chemin, où il attend l'eau sans la voir monter ni s'y croire en péril :
    # ce passage, son plan le prévoyait. Sans cela, deux qui se cherchent se croisent sans fin, et
    # qui va vers un abri par un palier menacé rebrousse chemin vers le plus haut lieu, puis repart.
    # Là où il se tient, s'il y est à l'abri, il reste. Devant l'eau qu'il voit monter, ou s'il se
    # croit en péril, le plus haut lieu compte, quel que soit celui vers lequel il allait.
    from .eau import en_peril
    from .planification import _etape, abri

    def sures():
        """Les lieux éclairés, hors de l'eau, où il croit quelqu'un de sûr."""
        salles = []
        from .relations import envers
        for x in sorted([*pnjs(monde), "joueur"], key=lambda x: (-envers(monde, id, x)["affection"], x)):
            if x == id or not se_fie(monde, id, x):
                continue
            salle = salle_crue(monde, id, x)
            if (salle in monde.data["salles"] and salle not in salles and _eclairee_crue(monde, id, salle)
                    and not menacee(monde, id, salle)):
                salles.append(salle)
        return salles

    i = lire(monde, id)["intention"]
    en_route = (i["but"].get("lieu") if i and i["plan"] and i["motif"] == "securite" and i["but"]["type"] == "abri"
                and i["but"].get("lieu") != ici else None)
    eau_monte = monte(monde, id)
    if en_route and not eau_monte and not en_peril(monde, id) and en_route in (abris := sures()) and ici not in abris:
        trouve = abri(monde, id, [en_route])
        if trouve is not None:
            return {"type": "abri", "lieu": trouve[0]}, trouve[1] + [_etape("abriter", lieu=trouve[0])]
    if menacee(monde, id, ici) or eau_monte:
        salles = sorted((s for s in monde.data["salles"] if not menacee(monde, id, s)
                         and _eclairee_crue(monde, id, s)), key=lambda s: (-altitude(monde, s), s != ici, s))
    else:
        salles = sures()
        if salles and ici != salles[0]:
            # Le plus aimé d'abord ; chaque trajet doit rester possible et valoir ce qu'il laisse.
            for salle in salles:
                trouve = abri(monde, id, [salle])
                if trouve is not None:
                    return {"type": "abri", "lieu": trouve[0]}, trouve[1] + [_etape("abriter", lieu=trouve[0])]
            return None
        salles.sort(key=lambda s: s != ici)
    from .planification import _etape, aller
    for salle in salles:
        etapes = aller(monde, id, salle)
        if etapes is None:
            continue
        return {"type": "abri", "lieu": salle}, etapes + [_etape("abriter", lieu=salle)]
    if menacee(monde, id, ici):
        # Aucun lieu hors de l'eau à sa portée : moins d'eau, c'est déjà en sortir. Ce n'est pas un
        # abri où rester (``pnj._abriter``) : il s'y rend.
        ici_cm = attendue(monde, id, ici)
        moins = sorted((s for s in monde.data["salles"] if attendue(monde, id, s) < ici_cm),
                       key=lambda s: (attendue(monde, id, s), -altitude(monde, s), s))
        for salle in moins:
            etapes = aller(monde, id, salle)
            if etapes:
                return {"type": "abri", "lieu": salle}, etapes
    return None


def _plan_lumiere(monde, id):
    """Avoir de la lumière, quand il se tient dans le noir (ce qu'il ressent, ``autour``) et que
    le noir l'inquiète : la recherche (``planification.eclairer``). La lumière se tient là où le
    plan l'a choisie (``planification.RESTER``) : sa lumière en main en chemin, il la porte
    jusqu'au bout, là où il garde ses biens. La lumière d'un autre ne le suit pas : rien ne se
    poursuit alors."""
    if not peur_du_noir(monde, id):
        return None
    from .perception import allumee
    porte = any(porte_par(monde, k, id) and "allume" in o and allumee(o) for k, o in monde.objets.items())
    # Il y voit par sa lumière en main, ou par celle du lieu (ses sources, une lueur voisine sur sa
    # case : ``lumiere_crue``, comme le planificateur) ; pas par celle qu'un autre porte, qui le
    # quittera avec lui.
    if porte or lumiere_crue(monde, id, monde.objets[id]["lieu"]):
        i = lire(monde, id)["intention"]
        return ((i["but"], i["plan"]) if porte and i and i["but"]["type"] == "lumiere" and i["plan"]
                and all(x["operation"] == "aller" for x in i["plan"]) else None)
    from .planification import eclairer
    return eclairer(monde, id)


def _plan_reposer(monde, id):
    """Se reposer là où l'on est."""
    from .planification import _etape
    return {"type": "repos"}, [_etape("reposer")]


def ouvert_par_soi(monde, id, objet, depuis):
    """A-t-il lui-même ouvert ou déverrouillé cet objet dans les ``depuis`` dernières minutes ?"""
    return any(s["type"] == "ouvert_par_soi" and s["objet"] == objet and monde.data["minutes"] - s["minute"] <= depuis
               for s in lire(monde, id)["memoire"])


def garde_sous_cle(monde, id, objet):
    p = profil(monde, id)
    return bool(p) and any(x["condition"] == {"objet": objet, "verrouillee": True} for x in p["pulsions"])


def de_son_fait(monde, id, condition):
    """On ne s'alarme pas de ce qu'on vient de défaire soi-même : sa clé, sa main."""
    if condition.get("verrouillee"):
        return ouvert_par_soi(monde, id, condition["objet"], 2)
    return "lieu" in condition and "objet" in condition and porte_par(monde, condition["objet"], id)


def _lieux_gardes(monde, id, siens=False):
    """Les salles où il croit ce qu'il garde : ses pulsions de biens sur un objet, hors rondes.
    ``siens`` : seulement ce dont il a la charge, le sien ou celui qu'on lui a confié (y toucher
    n'est pas une faute, ``illicite``), pas ce qu'il convoite."""
    p = profil(monde, id) or {}
    return {s for x in p.get("pulsions", []) if x["besoin"] == "biens" and not periodique(x["condition"])
            and "objet" in x["condition"] and not (siens and illicite(monde, id, x["condition"]["objet"]))
            for s in [salle_crue(monde, id, x["condition"]["objet"])] if s in monde.data["salles"]}


def menaces(monde, id):
    """Les salles où il croit un bien dont il a la charge et, avec, quelqu'un dont il se méfie, à qui
    il en veut ou qu'il craint (bandes de ``relations``) : ce bien est menacé à ses yeux. S'en
    éloigner, c'est le lui laisser (``gardes``) ; ce n'est pas s'abriter de lui (``planification.abri``)."""
    from .esprits import pnjs
    lieux = set(_lieux_gardes(monde, id, siens=True))
    from .signes import intentions_lues
    lieux.update(salle_crue(monde, id, c["envers"]) for _, c in intentions_lues(monde, id)
                 if de_garde(monde, id, salle_crue(monde, id, c["envers"])))
    lieux.discard(None)
    if not lieux:
        return ()
    from .relations import en_veut, craint
    mefiants = [x for x in [*pnjs(monde), "joueur"] if x != id
               and (se_mefie(monde, id, x) or en_veut(monde, id, x) or craint(monde, id, x))]
    mefiants += [x for x, _ in intentions_lues(monde, id)]
    return tuple(sorted(s for s in lieux if any(salle_crue(monde, id, x) == s for x in mefiants)))


def gardes(monde, id):
    """Les salles où il croit ce qu'il garde (ses pulsions de biens qui ne sont pas des rondes),
    quand ses biens le pressent, ou quand il y croit quelqu'un qui le menace (``menaces``) :
    s'en tenir loin lui coûte (``planification.prix_gardes``), quel que soit le plan."""
    if "biens" in urgents(monde, id):
        return tuple(sorted(_lieux_gardes(monde, id)))
    return menaces(monde, id)


def _plan_garder(monde, id, condition):
    """Rester près de ce qu'il garde, en comptant ce que le lieu laisse monter (``planification.garder``)."""
    from .planification import garder
    salle = salle_crue(monde, id, condition["objet"])
    etapes = None if salle not in monde.data["salles"] else garder(monde, id, salle)
    return None if etapes is None else ({"type": "garder", "lieu": salle}, etapes)


def _delegue(monde, id, pulsion):
    """Une pulsion confiée au joueur attend tant que le PNJ le croit fiable ; une pulsion qu'il a payé
    quelqu'un de rétablir aussi (``tache_payee``)."""
    return bool(pulsion.get("delegue_a") and not se_mefie(monde, id, pulsion["delegue_a"])
                or tache_payee(monde, id, pulsion["condition"]))


def tache_payee(monde, id, condition):
    """Il a payé quelqu'un pour rétablir ``condition`` (``echanges.engager``) : il ne le fait pas à sa
    place tant que la parole court (``echanges.ENGAGEMENT_MAX``), qu'il le croit fiable et qu'il n'a
    pas appris qu'elle n'a pas été tenue (une créance de ce travail). Renvoie à qui, ou None."""
    from .echanges import ENGAGEMENT_MAX
    memoire = lire(monde, id)["memoire"]
    for i in range(len(memoire) - 1, -1, -1):
        s = memoire[i]
        if s["type"] == "tache_payee" and s["condition"] == condition:
            if monde.data["minutes"] - s["minute"] > ENGAGEMENT_MAX or se_mefie(monde, id, s["a"]):
                return None
            if any(x["type"] == "creance" and x["de"] == s["a"] and x.get("quoi") == "tache" for x in memoire[i + 1:]):
                return None
            return s["a"]
    return None


def _etat_urgence(e, besoin):
    return e["urgences"].get(besoin, {}).get("etat")


def urgents(monde, id, inertie=False):
    """Besoins qui pressent, du plus pressant (le plus au-delà de son seuil) au moins pressant,
    qu'il ait ou non un moyen de les apaiser (``attentes``).

    Un seul effet de seuil : un besoin presse quand il dépasse un repère d'une marge. Son repère
    est son seuil ; apaisé (``eveiller``), il ne presse de nouveau que nettement au-dessus
    (``REPRISE``), comme un thermostat. Avec ``inertie`` (le choix du but), le plan en cours d'un
    autre besoin est aussi un repère : un besoin ne l'interrompt que s'il presse plus que lui
    (de combien ce besoin dépasse encore son seuil, 0 s'il ne presse plus) d'``INERTIE`` au
    moins. On achève le geste entamé avant de céder à la faim naissante, et deux besoins qui
    pressent ensemble ne s'interrompent pas l'un l'autre à chaque minute."""
    s, e = seuils(monde, id), lire(monde, id)
    v = e["besoins"]
    i = e["intention"]
    en_cours = i["motif"] if inertie and i and i["plan"] else None
    avance = max(0.0, v.get(en_cours, 0) - s[en_cours]) if en_cours in s else 0.0

    def presse(b):
        ecart = v.get(b, 0) - s[b]
        return (ecart >= (REPRISE if _etat_urgence(e, b) == "apaise" else 0)
                and (en_cours in (None, b) or ecart >= avance + INERTIE))
    return sorted((b for b in s if presse(b)), key=lambda b: (s[b] - v[b], BESOINS.index(b)))


def attentes(monde, id):
    """Ceux des besoins qui pressent pour lesquels il n'a trouvé aucun plan sur ce qu'il croit : ils
    attendent que quelque chose change dans ce qu'il croit, sans être oubliés (``deliberer``)."""
    e = lire(monde, id)
    return [b for b in urgents(monde, id) if _etat_urgence(e, b) == "attente"]


def inactivite(monde, id):
    """Pourquoi un PNJ pressé n'entreprend rien, sur ses croyances (lecture seule).

    Le banc, le récit et l'audit distinguent le recours non entrepris, l'absence de moyen,
    la charge confiée et la charge déjà satisfaite. Un besoin haut ne suffit pas à dire
    qu'il reste une tâche à faire ; aucune recherche supplémentaire n'est lancée ici.
    """
    p = profil(monde, id)
    if not p or lire(monde, id)["intention"] is not None:
        return None
    pressants = urgents(monde, id)
    if not pressants:
        return None
    rompues = {b: [x for x in p["pulsions"] if x["besoin"] == b and not satisfaite(monde, id, x["condition"])]
               for b in pressants}
    a_faire = [b for b, r in rompues.items()
               if any(not _delegue(monde, id, x) for x in r) or not any(x["besoin"] == b for x in p["pulsions"])]
    sans_plan = attentes(monde, id)
    if any(b not in sans_plan for b in a_faire):
        return "sans_recours"
    if a_faire:
        return "attente"
    return "confiee" if any(rompues.values()) else "satisfaite"


def eveiller(monde, id, minute):
    """L'effet de seuil de chaque besoin, d'après sa valeur, comme un thermostat : il presse à son
    seuil ; repassé au-dessous, il est apaisé et ne presse de nouveau qu'à son seuil + ``REPRISE``,
    à moins d'être d'abord bien redescendu (à son seuil − ``REPRISE``) : un besoin comblé (un
    repas, un feu, le repos) retrouve son seuil, celui qui frôle son seuil ne bat plus à chaque
    minute. L'état vit dans l'esprit (``urgences``) : le même laps, découpé autrement, donne le
    même monde."""
    s, e = seuils(monde, id), esprit(monde, id)
    u = e["urgences"]
    for b in s:
        v, etat = e["besoins"].get(b, 0), _etat_urgence(e, b)
        if etat in ("presse", "attente") and v < s[b]:
            u[b] = {"etat": "apaise", "depuis": minute}
        if _etat_urgence(e, b) == "apaise" and v < s[b] - REPRISE:
            del u[b]
        elif etat is None and v >= s[b] or etat == "apaise" and v >= s[b] + REPRISE:
            u[b] = {"etat": "presse", "depuis": minute}


def _classer(monde, id, pressants, liste, essais, minute):
    """Un besoin qui presse et dont chaque recours a été essayé sans plan (ou qui n'en a aucun) se
    met en attente ; dès qu'un recours aboutit, il presse de nouveau. Un recours qu'on n'a pas
    essayé (un but plus pressant a abouti avant, ou il y a renoncé pour un temps) ne décide rien."""
    u = esprit(monde, id)["urgences"]
    for b in pressants:
        issues = [essais.get(i) for i, (motif, _) in enumerate(liste) if motif == b]
        if "plan" in issues:
            etat = "presse"
        elif all(x == "rien" for x in issues):
            etat = "attente"
        else:
            continue
        if u.get(b, {}).get("etat") != etat:
            u[b] = {"etat": etat, "depuis": minute}


def confie_a_autrui(monde, id, objet):
    """Ce qu'il a confié à quelqu'un qu'il croit fiable, il ne le fait pas à sa place."""
    p = profil(monde, id)
    return bool(p) and any(x["condition"].get("objet") == objet and _delegue(monde, id, x) for x in p["pulsions"])


def _plan_faim(monde, id):
    """Apaiser la faim : le plan le moins coûteux trouvé par la recherche (``planification``)."""
    from .planification import planifier
    return planifier(monde, id, "faim")


def _plan_argent(monde, id):
    """Des pièces à prendre qui valent, pour lui, plus que ce qu'il lui en coûte : la recherche
    (``planification.enrichir``)."""
    from .planification import enrichir
    return enrichir(monde, id)


def _plan_creance(monde, id):
    """Ce qu'on lui doit (``biens.rembourser``), qui vaut pour lui plus que le chemin : aller trouver
    son débiteur, pour qu'il le lui rende (``planification.reclamer``)."""
    from .planification import reclamer
    return reclamer(monde, id)


def _plan_froid(monde, id):
    """Se réchauffer : le plan le moins coûteux trouvé par la recherche (``planification``)."""
    from .planification import planifier
    return planifier(monde, id, "chaleur")


# Besoins qu'un geste qui dure apaise : la méthode, et le seuil où il s'achève.
PROGRES = {"repos": (_plan_reposer, REPOS_FIN), "chaleur": (_plan_froid, CHALEUR_FIN),
           "securite": (_plan_abri, SECURITE_FIN)}
GESTE_PROGRES = {"repos": "reposer", "chaleur": "chauffer", "securite": "abriter"}
# Ce qu'un besoin tente avant le geste qui l'apaise : dans le noir, avoir de la lumière.
RECOURS = {"securite": (_plan_lumiere,)}
# Les besoins qu'une part d'une ressource apaise (``besoin_de_part``), hors la faim : quand rien de ce
# qu'il connaît n'y pourvoit, il demande à qui pourrait en avoir (``_plan_enquete``).
ENQUETES = ("chaleur",)


def retabli_par_son_plan(monde, id, condition):
    """Ce qu'il défait lui-même pour un plan qui le rétablit n'est pas à réparer d'abord, tant
    que le motif de ce plan presse encore (un besoin urgent, une parole à tenir)."""
    e = lire(monde, id)
    i = e["intention"]
    if not (condition.get("verrouillee") and i and any(
            x["operation"] == "verrouiller" and x["cible"] == condition["objet"] for x in i["plan"])):
        return False
    but = {k: v for k, v in i["but"].items() if k != "type"}
    return i["motif"] in urgents(monde, id) or i["motif"] == "engagement" and any(
        x["condition"] == but for x in agendas.en_cours(monde, id))


def candidats(monde, id):
    """Buts envisageables, du besoin le plus pressant au moins pressant ; la routine (rondes,
    surveillance) passe après ce qui presse vraiment et après une tâche acceptée. (besoin, méthode)."""
    for besoin, methode, _, _, _ in _candidats(monde, id):
        yield besoin, methode


class Palier(IntEnum):
    """Priorités historiques, du premier but tenté au dernier."""
    PERIL_EAU = 0
    ALARME = 1
    RANIMER = 2
    BESOIN_PRESSANT = 3
    PAROLE_DUE = 4
    PREVENIR = 5
    REJOINDRE = 6
    ATTENDRE_APPELANT = 7
    BRUIT_A_VOIR = 8
    PULSION_ROMPUE = 9
    PROGRES_EN_COURS = 10
    ROUTINE = 11
    ARGENT = 12


class Urgence(NamedTuple):
    palier: Palier
    valeur: float
    departage: tuple

    def cle(self):
        """Petit palier d'abord, grand écart au seuil ensuite, départage déclaré enfin."""
        return self.palier, -self.valeur, self.departage


class Candidat(NamedTuple):
    besoin: str
    methode: object
    routine: bool
    recours: bool
    urgence: Urgence


def _candidats(monde, id):
    """Candidats triés par leur urgence explicite, avec leur rang (la routine
    après le reste) et s'ils sont un recours de leur besoin (ce qui l'apaise ou le rétablit) ; une
    parole due, prévenir, attendre l'appelant, une alarme, sortir de l'eau, un bruit à voir et l'argent
    n'en sont pas : ils passent devant un recours en cours (``choisir``).

    Un besoin qui vient à peine de franchir son seuil laisse finir le plan en cours d'un autre
    motif, et un besoin apaisé ne presse de nouveau que nettement au-dessus (``urgents``)."""
    p, e = profil(monde, id), esprit(monde, id)
    buts = []

    def ajouter(besoin, methode, palier, departage=(), valeur=0, routine=False, recours=False):
        buts.append(Candidat(besoin, methode, routine, recours, Urgence(palier, valeur, departage)))

    # Ceux qui laissent finir le plan en cours n'y ajoutent rien, mais restent pressants : ni
    # routine ni pulsion rompue de leur fait ne passe devant ce plan.
    pressants = urgents(monde, id)
    s = seuils(monde, id)
    for besoin in urgents(monde, id, inertie=True):
        ecart, rang_besoin = e["besoins"][besoin] - s[besoin], BESOINS.index(besoin)
        rang_recours = 0

        def ajouter_recours(methode, routine=False):
            nonlocal rang_recours
            # Les routines d'un besoin pressant précèdent les autres routines, même à écart nul.
            departage = ((0, -ecart, rang_besoin, rang_recours) if routine
                         else (rang_besoin, rang_recours))
            ajouter(besoin, methode, Palier.ROUTINE if routine else Palier.BESOIN_PRESSANT,
                    departage, 0 if routine else ecart, routine, True)
            rang_recours += 1

        if besoin == "faim":
            ajouter_recours(_plan_faim)
            # Rien de ce qu'il connaît ne le nourrit : il demande à qui pourrait en avoir.
            ajouter_recours(lambda m, i: _plan_enquete(m, i, "faim"))
            continue
        for methode in RECOURS.get(besoin, ()):
            ajouter_recours(methode)
        if besoin in PROGRES:
            # Le geste qui apaise d'abord ; les pulsions du même besoin (les rondes) restent des recours.
            ajouter_recours(PROGRES[besoin][0])
        if besoin in ENQUETES:
            ajouter_recours(lambda m, i, b=besoin: _plan_enquete(m, i, b))
        pulsions = [x for x in p["pulsions"] if x["besoin"] == besoin]
        for x in pulsions:
            if (not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)
                    and not retabli_par_son_plan(monde, id, x["condition"])):
                # Une ronde peut attendre qu'il ait tenu parole ; un feu à voir ou à recharger, non.
                ajouter_recours(lambda m, i, c=x["condition"]: _pulsion_a_soi(m, i, c),
                                periodique(x["condition"]))
                if "allume" in x["condition"]:
                    # Un feu sans bois qu'il connaisse : il demande à qui pourrait en avoir.
                    ajouter_recours(lambda m, i: _plan_enquete(m, i, "chaleur"))
        if besoin == "biens":
            for x in pulsions:
                if periodique(x["condition"]):
                    continue
                ajouter_recours(lambda m, i, c=x["condition"]: _plan_garder(m, i, c), True)
    # Toute parole de service suit le devis qui l'a fait accepter, jusqu'à son abandon annoncé.
    from .planification import planifier_engagement
    for rang, x in enumerate(agendas.en_cours(monde, id)):
        ajouter("engagement", lambda m, i, x=x: planifier_engagement(m, i, x), Palier.PAROLE_DUE, (rang,))
    # Un corps à terre connu : recours au même graphe de gestes, sans accès à ses PV ni son réveil.
    for rang, protege in enumerate(p.get("protege", ())):
        c = e["croyances"].get(protege, {}).get("etat", {})
        if c.get("valeur", {}).get("conscient") is False and not c["valeur"].get("mort"):
            from .planification import ranimer
            ajouter("devoir", lambda m, i, x=protege: ranimer(m, i, x), Palier.RANIMER, (-rang,))
    # Un protégé atteint sous ses yeux : il va le prévenir, comme une parole due.
    if any(s["type"] == "a_prevenir" for s in e["memoire"]):
        ajouter("devoir", _plan_prevenir, Palier.PREVENIR)
    # « J'arrive ! » à un appel : une parole due, comme une autre (``appel.plan_venir``).
    if e["rejoindre"]:
        from .appel import plan_venir
        ajouter("engagement", plan_venir, Palier.REJOINDRE)
    # Il a convenu d'attendre qui l'a hélé ou qu'il a hélé (``appel``), après ce qui presse et la
    # parole due ; un bruit, ce qui ne presse pas et la routine attendent.
    if e["rejoint"]:
        ajouter("rejoint", _plan_attendre, Palier.ATTENDRE_APPELANT)
    # Un bruit inconnu qu'il doit, ou ose, aller voir : après ce qui presse, avant la routine ; une
    # alarme (l'appel d'un protégé, un bruit à son seuil d'alerte), avant tout le reste.
    from .planification import voir
    a_voir, alarme_ = bruit_a_voir(monde, id), alarme(monde, id)
    if alarme_:
        ajouter(alarme_[1], lambda m, i, s=alarme_[0]: voir(m, i, s), Palier.ALARME)
    # Là où il se tient, il attend l'eau trop haute pour s'y mouvoir : en sortir passe avant tout.
    from .eau import en_peril
    if "securite" in p["besoins"] and en_peril(monde, id):
        ajouter("securite", _plan_abri, Palier.PERIL_EAU)
    if a_voir and a_voir != alarme_:
        ajouter(a_voir[1], lambda m, i, s=a_voir[0]: voir(m, i, s), Palier.BRUIT_A_VOIR)
    # Ce dont il a la charge et qu'il voit rompu, il le rétablit sans attendre que son besoin
    # presse : un feu qui baisse, un protégé qui a faim, ce qu'il garde sous clé et a lui-même
    # ouvert. Les rondes ont leur routine ; un désir jamais satisfait attend son besoin.
    for i, x in enumerate(p["pulsions"]):
        c = x["condition"]
        if (e["pulsions"][i] is False and x["besoin"] not in pressants and not periodique(c)
                and not _delegue(monde, id, x) and not satisfaite(monde, id, c)
                and not retabli_par_son_plan(monde, id, c)):
            ajouter(x["besoin"], lambda m, i, c=c: _pulsion_a_soi(m, i, c),
                    Palier.PULSION_ROMPUE, (i, 0), recours=True)
            if "allume" in c:
                ajouter(x["besoin"], lambda m, i: _plan_enquete(m, i, "chaleur"),
                        Palier.PULSION_ROMPUE, (i, 1), recours=True)
    # Assis pour se reposer, ou près du feu, il ne s'en va qu'une fois remis, ou pour plus pressant.
    # Seulement si son plan comporte bien ce geste : une ronde a le même motif que l'abri.
    for rang, (besoin, (methode, fin)) in enumerate(PROGRES.items()):
        if (e["intention"] and e["intention"]["motif"] == besoin and e["besoins"].get(besoin, 0) > fin
                and any(x["operation"] == GESTE_PROGRES[besoin] for x in e["intention"]["plan"])):
            ajouter(besoin, methode, Palier.PROGRES_EN_COURS, (rang,), recours=True)
    # La routine : ses rondes, même quand le besoin qu'elles servent ne presse pas.
    for rang, x in enumerate(p["pulsions"]):
        if (periodique(x["condition"]) and x["besoin"] not in pressants
                and not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)):
            ajouter(x["besoin"], lambda m, i, c=x["condition"]: _pulsion_a_soi(m, i, c),
                    Palier.ROUTINE, (1, rang), routine=True, recours=True)
    # L'argent : un poids permanent, qui ne presse jamais ; il ne passe qu'après tout le reste.
    # Ce qu'on lui doit d'abord, puis des pièces à prendre.
    ajouter(ARGENT, _plan_creance, Palier.ARGENT, (0,), routine=True)
    ajouter(ARGENT, _plan_argent, Palier.ARGENT, (1,), routine=True)
    yield from sorted(buts, key=lambda c: c.urgence.cle())


def constater_pulsions(monde, id):
    """Ses pulsions, d'après ce qu'il croit maintenant : ce qui était satisfait et ne l'est plus est
    rompu (False) jusqu'à ce qu'il le rétablisse, quelle qu'en soit la cause ; un désir jamais
    satisfait le reste (None). Une atteinte (ses biens forcés ou déplacés, un feu éteint par un
    autre) relance son besoin. À chaque minute, et à chaque choix entre deux minutes : un feu
    éteint sous ses yeux est rompu dès qu'il le voit."""
    p, e = profil(monde, id), esprit(monde, id)
    for i, x in enumerate(p["pulsions"]):
        etat, avant = satisfaite(monde, id, x["condition"]), e["pulsions"][i]
        # Une ronde expire, un feu baisse d'eux-mêmes : ce n'est pas une atteinte.
        if (avant and not etat and not s_use(x["condition"])
                and not de_son_fait(monde, id, x["condition"])):
            # Ses biens forcés ou déplacés : un vol découvert, même sans coupable.
            relancer(monde, id, x["besoin"], VOL if x["besoin"] == "biens" else ATTEINTE)
            memoriser(monde, id, {"type": "atteinte", "condition": dict(x["condition"])})
        e["pulsions"][i] = True if etat else (None if avant is None else False)


# Le banc compte les choix de but : ceux du filet de la minute et ceux qu'un événement, la fin d'un
# plan ou un geste manqué ont provoqués (``pnj._avancer``). Une mesure, hors de l'état du monde.
COMPTES = Counter()


def deliberer(monde, id, minute):
    """La minute de vie intérieure : besoins, pulsions, puis le choix du but et du plan
    (``choisir``). C'est le filet de ce qui monte peu à peu (besoins, échéances, un plan devenu
    moins bon) ; les événements font choisir entre deux minutes. Le corps, la dérive des besoins
    et la sécurité ressentie ont vécu le temps passé dans chaque état jusqu'à l'instant
    (``vecu.minute``) : ils ne sont pas échantillonnés ici."""
    from .corps import conscient
    if not conscient(monde, id):
        return
    p = profil(monde, id)
    if not p:
        return
    installer(monde, id)
    from .relations import partager
    partager(monde, id, minute)
    constater_pulsions(monde, id)
    from .echanges import engagements_echus
    engagements_echus(monde, id)
    eveiller(monde, id, minute)
    COMPTES["minute"] += 1
    choisir(monde, id, minute)


def choisir(monde, id, minute):
    """Le choix du but et du plan, sur ce qu'il croit à cet instant : à chaque minute après ses
    besoins (``deliberer``), et entre deux minutes à la fin de son plan, après un geste manqué ou
    un événement qui change sa situation (``pnj._avancer``). Ne fait rien passer du temps : ses
    besoins, ses pulsions et leurs échéances vivent à la minute. Ce que la recherche a déjà
    trouvé sur les mêmes entrées est repris (``planification``)."""
    from .corps import conscient
    if not conscient(monde, id):
        return
    from . import stratege
    p = profil(monde, id)
    if not p:
        return
    e = esprit(monde, id)
    installer(monde, id)
    COMPTES["choix"] += 1
    # Le danger immédiat se traite avant les besoins ordinaires, avec un choix au coût.
    from .defense import choisir as choisir_defense
    reaction = choisir_defense(monde, id)
    if reaction is not None:
        but, etapes = reaction
        ancien = e["intention"]
        e["intention"] = {"but": but, "motif": "devoir" if but["type"] == "proteger" else "securite",
                          "plan": etapes, "depuis": ancien["depuis"] if ancien and ancien["but"] == but else minute,
                          "attente": 0}
        return
    # Ce qu'il croit de ses charges et de ses paroles, tel qu'il est maintenant : une pulsion rompue
    # sous ses yeux, une parole tenue, échue ou devenue impossible (à la minute, déjà fait).
    constater_pulsions(monde, id)
    from .echanges import engagements_echus
    engagements_echus(monde, id)
    attendre(monde, id, minute)
    intention = e["intention"]
    if intention and intention["motif"] == "alerte":
        from .pnj import chemin
        if chemin(monde, id, monde.objets[id]["lieu"], intention["but"]["lieu"]) is not None:
            return  # Le réflexe déclaré garde la priorité jusqu'à son terme.
        e["intention"] = None  # Plus aucun passage qu'il croie ouvert : il ne peut accourir.
    if intention and intention["but"]["type"] == "strategie" and intention["plan"]:
        return  # Une stratégie choisie va à son terme, ou tombe au premier geste manqué.
    pressants = urgents(monde, id, inertie=True)
    tous = list(_candidats(monde, id))
    liste = [(besoin, methode) for besoin, methode, _, _, _ in tous]
    essais = {}
    # Hystérésis entre recours, comme entre besoins (``INERTIE``) : le recours en cours d'un besoin
    # garde la main sur les autres recours du même besoin et du même rang tant que son plan n'est pas
    # achevé et que sa méthode le rend encore sur ce qu'il croit (rien de neuf ne l'a rendu impossible
    # ou ne l'a changé). Ainsi la lumière ne défait pas l'abri dont le chemin passe par le noir, ni
    # l'inverse. Ce qui n'est pas un recours (une alarme, une parole due, prévenir…) passe devant ; la
    # routine n'en a pas besoin (une ronde faite reste faite pour sa période, rien ne s'y relaie).
    from .temps import MINUTE, instant
    maintenant = instant(monde)
    courant = intention if intention and intention["plan"] else None
    retenu = None    # (besoin, rang, résultat) : un autre recours de ce besoin, s'il faut y revenir
    resultat = None
    from .planification import vues_du_choix
    with vues_du_choix(monde, id):
        for n, (besoin, methode, routine, recours, _) in enumerate(tous):
            if retenu is not None and (besoin, routine, recours) != (retenu[0], retenu[1], True):
                continue
            if besoin in e["renoncements"] and e["renoncements"][besoin] + REPIT * MINUTE > maintenant:
                essais[n] = "renonce"
                continue
            resultat = methode(monde, id)
            if not resultat:
                essais[n] = "rien"
                continue
            essais[n] = "plan"
            if retenu is not None:
                if resultat[0] == courant["but"]:
                    break   # Sa méthode rend encore le recours en cours : il le garde.
                continue
            if recours and not routine and courant and besoin == courant["motif"] and resultat[0] != courant["but"]:
                retenu = (besoin, routine, resultat)   # Le sien d'abord, si sa méthode le rend encore.
                continue
            break
        else:
            resultat = retenu[2] if retenu else None
    if resultat:
        besoin = retenu[0] if retenu else besoin   # Retenu : la boucle a pu finir sur un autre but.
        but, etapes = _attendre_qui_vient(monde, id, resultat)
        from .pnj_propositions import recours
        offre = recours(monde, id, besoin, etapes)
        if offre:
            etapes = [offre]
        if stratege.plan_illicite(monde, id, besoin, but, etapes, minute):
            return
        intention = e["intention"]
        meme = bool(intention) and intention["but"] == but
        e["intention"] = {"but": but, "motif": besoin, "plan": etapes,
                          "depuis": intention["depuis"] if meme else minute,
                          "attente": intention["attente"] if meme else 0,
                          **({"attitude": intention["attitude"]} if meme and "attitude" in intention else {})}
        if not meme:
            e["patience"] = None  # Un autre but : ce qu'il attendait pour l'ancien ne compte plus.
        _classer(monde, id, pressants, liste, essais, minute)
        stratege.occupe(monde, id)
        return
    from .pnj_propositions import recours
    refusee = e["demande_refusee"]
    offre = recours(monde, id, refusee["besoin"], []) if refusee else None
    e["intention"] = ({"but": {"type": "proposition", "objet": refusee["objet"]},
                       "motif": refusee["besoin"], "plan": [offre], "depuis": minute, "attente": 0}
                      if offre else None)
    _classer(monde, id, pressants, liste, essais, minute)
    stratege.desoeuvre(monde, id, minute, urgents(monde, id))


def menager_flamme(monde, id, minute):
    """Une flamme portable qu'il a allumée ou employée pour allumer, et que son plan n'emploie
    plus, se consume pour rien : il l'éteint d'abord, et la garde pour plus tard. Celle qui
    l'éclaire quand il a besoin d'y voir (``lumiere_utile``), sans autre lumière en main, ne se
    consume pas pour rien."""
    from .perception import allumee
    e = esprit(monde, id)
    plan = e["intention"]["plan"] if e["intention"] else []
    vises = {x["cible"] for x in plan} | {x["outil"] for x in plan}
    allumees = {s["objet"] for s in e["memoire"] if s["type"] == "flamme_employee"}
    flamme = next((k for k in sorted(allumees) if k in monde.objets and k not in vises
                   and porte_par(monde, k, id) and allumee(monde.objets[k])), None)
    if flamme is None:
        return
    autres = any(k != flamme and porte_par(monde, k, id) and allumee(o) for k, o in monde.objets.items())
    if not autres and lumiere_utile(monde, id):
        return
    geste = {"operation": "eteindre", "cible": flamme, "outil": "", "lieu": "", "condition": ""}
    if e["intention"]:
        plan.insert(0, geste)
    else:
        e["intention"] = {"but": {"type": "menager", "objet": flamme}, "motif": "menager", "plan": [geste],
                          "depuis": minute, "attente": 0}


def renoncer(monde, id, minute):
    """Il abandonne son but : il ne le reprend qu'après ``REPIT`` minutes, comptées de cet instant
    (``renoncements`` : l'instant, en dixièmes de seconde)."""
    from .temps import instant
    e = esprit(monde, id)
    intention = e["intention"]
    e["renoncements"][intention["motif"]] = instant(monde)
    e["patience"] = None
    memoriser(monde, id, {"type": "renoncement", "but": dict(intention["but"])})
    e["intention"] = None
