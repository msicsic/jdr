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
from .memoire import episodes
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
              "dire", "demander", "acheter", "confier", "remettre", "rembourser", "demander_feu", "engager", "proposer", "interposer", "rester")
PROGRESSIFS = ("aller", "reposer", "chauffer", "abriter", "rester")  # gestes qui durent : une minute sans les finir n'est pas un échec
EFFORTS = ("aller", "prendre", "poser", "crocheter", "frapper", "alimenter", "servir", "inspecter")  # gestes qui creusent
# demander_feu : tendre sa source à qui porte une flamme pour qu'il l'y allume (``echanges.demander_feu``).
# engager : payer quelqu'un pour une tâche (``echanges.engager``).
SOCIALES = ("dire", "demander", "acheter", "confier", "remettre", "rembourser", "demander_feu", "engager", "proposer")
A_VUE = ("crocheter",)  # gestes qui demandent d'y voir (``planification.chance_crochetage``)
PROFONDEUR = 4
PATIENCE = 30          # minutes passées à attendre une occasion (ou un passage) avant de renoncer
ATTEINTE = 30          # une pulsion qui cesse d'être satisfaite relance son besoin
VOL = 60               # un vol vu par sa victime
REPOS_FIN = 20         # reposé : il se relève
CHALEUR_FIN = 20       # réchauffé : il s'écarte du feu
SECURITE_FIN = 30      # rassuré : il quitte l'abri
# Ce qui inquiète (+) ou rassure (−) la sécurité, valeurs par défaut que chaque profil nuance
# (donnée ``securite``) : par minute pour ce qui dure, d'un coup pour un événement.
SECURITE = {"coup": 40, "violence": 25, "mort": 30, "noir": 0.5, "mefiance": 0.3, "bruit": 15, "illicite": 20,      # inquiète
            "captif": 1, "eau": 2, "menace": 1, "crue": 10,     # par minute : captivité, eau, menace ;
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


def marge_engagement(monde, id):
    """Ténacité en points d'urgence ; aucune durée passée n'entre dans cette marge."""
    from .caractere import caracteristique
    return INERTIE + max(0, caracteristique(monde, id, "VOL")) / 4


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
                          "reserve", "securite", "protege", "situation", "alerte", "liens", "statuts"} | agendas.champs_profil()), "Profil de PNJ mal formé"
    from .esprits import verifier_statuts
    verifier_statuts(monde, p.get("statuts", []), declares=True)
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
        if 'echeance' in pulsion and (not pulsion.get('delegue_a')
                or type(pulsion['echeance']) is not int or pulsion['echeance'] < 0):
            from .monde import ErreurMonde
            raise ErreurMonde('Échéance de délégation invalide.',
                              f"{id}.pulsions.echeance reçu {pulsion['echeance']!r} ; attendu : entier >= 0 en minutes absolues, avec delegue_a=joueur.")
        assert (set(pulsion) <= {"besoin", "condition", "delegue_a", "echeance"} and pulsion.get("besoin") in seuils(monde, id)
                and condition_valide(monde, pulsion.get("condition"))
                and pulsion.get("delegue_a", "joueur") == "joueur"), "Pulsion de PNJ invalide"


def condition_valide(monde, c):
    """Vocabulaire commun des buts : un objet en un lieu, un objet verrouillé, une ronde,
    une part de nourriture servie à quelqu'un, un feu entretenu, un objet prêté à rendre, un objet
    vendu à remettre, un séjour près d'une personne."""
    return isinstance(c, dict) and (
        (set(c) == {'objet', 'proteger', 'echeance'} and c['proteger'] is True
         and type(c['echeance']) is int and c['echeance'] >= 0
         and (c['objet'] == 'joueur' or c['objet'] in monde.objets
              and monde.objets[c['objet']]['type'] in ('personnage', 'depouille'))) or
        # Une demande, y compris sa sortie historique, survit au décès de
        # sa cible. Sa raison crue décide de la fin, pas le validateur.
        (set(c) == {"pres"} and (c["pres"] == "joueur" or c["pres"] in monde.objets
         and monde.objets[c["pres"]]["type"] in ("personnage", "depouille"))) or
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
    from .monde import mobile_par_nature
    c = lire(monde, id)["croyances"].get(sujet, {}).get("lieu")
    if c:
        return c["valeur"]
    o = monde.objets.get(sujet)
    # Les objets fixes font partie des lieux : on sait où ils sont sans les avoir revus.
    return o["lieu"] if o and not mobile_par_nature(o) else None


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
CAUSES = ("impossible", "necessaire", "absent", "eteinte", "rien", "indication", "inconnu")
DETAILS_REFUS = ("objet", "besoin", "prix", "tache", "flamme", "offre", "contre_offre", "condition_tenue", "information", "repere", "mandat")


def _meme_demande(s, autre, operations, objet, besoin, mandat=None):
    return (s["de"] == autre and s["operation"] in operations and s.get("objet", objet) == objet
            and s.get("besoin") == besoin and s.get("mandat") == mandat)


def retenir_refus(monde, id, autre, operation, raison, souvenir=True, **detail):
    """``autre`` refuse à ``id`` cette demande (``operation`` sur ``objet``, ou ``besoin`` pour « as-tu… ? ») :
    il s'en souvient (``souvenir``), et retient cette réponse à la place de la précédente pour la même
    demande, avec, quand le refus a une cause, ce qu'il croit alors de ses moyens (``moyens_crus``).
    « Qui va là ? » n'est pas un refus : il s'est nommé, il redemande."""
    detail = {k: v for k, v in detail.items() if k in DETAILS_REFUS and v is not None}
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
            c = lire(monde, id)["croyances"].get(detail.get("objet"), {}).get("lieu")
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
    e = esprit(monde, id)
    e["refus"] = [s for s in e["refus"] if not (s["de"] == autre and s["operation"] == operation
                                                 and s.get("objet") == objet and s.get("besoin") == besoin
                                                 and s.get("mandat") == mandat)]


def refus_retenu(monde, id, autre, operations, objet=None, besoin=None, *, mandat=None):
    """La dernière réponse refusée d'``autre`` à cette demande (``operations`` : les façons de la faire,
    demander ou acheter), si elle tient encore (``tient``) ; None sinon. Un refus sans objet (le
    passage) vaut pour tout objet."""
    refus = [s for s in lire(monde, id).get("refus", ()) if _meme_demande(s, autre, operations, objet, besoin, mandat)]
    dernier = max(refus, key=lambda s: s["minute"], default=None)
    return dernier if dernier is not None and tient(monde, id, dernier) else None


def refus_geste(monde, id, etape):
    """Un refus encore valable interdit-il ce geste social, même préparé avant sa réponse ?

    Les étapes emploient les identifiants de leurs demandes, pas toujours leur nom
    d'opération (une enquête est une étape ``demander``). Les règles de levée restent
    celles des refus et des offres ; un autre mandat ou un meilleur prix reste possible.
    Aucune parole, observation ou nouvelle réponse n'est produite par ce contrôle.
    """
    if not lire(monde, id).get("refus"):
        return False
    op, autre, objet = etape["operation"], etape["cible"], etape["outil"]
    contenu = etape.get("contenu") or {}
    besoin, mandat = None, None
    if op == "demander":
        if "ressource" in contenu:
            op, objet, besoin = "enqueter", None, contenu["ressource"]
        elif "localisation" in contenu:
            op, objet = "enqueter_lieu", contenu["localisation"]
        elif contenu.get("cause_detresse"):
            op, objet = "enqueter_cause", None
        elif contenu.get("type") == "reclamer_dette":
            op, objet = "reclamer_dette", None
        else:
            if _contre_offre_honoree(monde, id, autre, objet):
                return False
            from .planification import vue
            return bool(vue(monde, id).refuse(autre, objet))
    elif op in ("acheter", "proposer"):
        if op == "acheter" and _contre_offre_honoree(monde, id, autre, objet, contenu.get("prix", 0)):
            return False
        from .pnj_propositions import offre_refusee
        terme = (contenu["contrepartie"] if op == "proposer"
                 else {"type": "pieces", "montant": contenu.get("prix", 0)})
        objet = contenu["demande"].get("objet", autre) if op == "proposer" else objet
        if offre_refusee(monde, id, autre, objet, terme):
            return True
        if op == "proposer":
            return False
        retenu = refus_retenu(monde, id, autre, ("acheter", "demander"), objet)
        if retenu and "offre" in retenu:
            return False  # La nouvelle contrepartie vient d'être jugée par offre_refusee.
        from .planification import vue
        return vue(monde, id).refuse_achat(autre, objet)
    elif op in ("confier", "engager"):
        condition = contenu["condition"] if op == "engager" else contenu
        objet, mandat = condition["objet"], contenu.get("mandat")
    elif op == "demander_feu":
        objet = contenu.get("allumer")
    else:
        return False
    refus = refus_retenu(monde, id, autre, (op,), objet, besoin, mandat=mandat)
    if refus and op == "engager" and refus["raison"] == "cher":
        return contenu["prix"] <= refus["prix"]
    return refus is not None


def _contre_offre_honoree(monde, id, autre, objet, prix=0):
    """Le même accord cru au recours et à la remise vaut au contrôle du geste.

    Le refus reste mémorisé pour poursuivre son recours, sans rouvrir les
    demandes ordinaires. Seule la condition annoncée et effectivement remplie
    lève son obstacle ; la remise et le paiement restent jugés par le moteur.
    """
    from .echanges import offre_retenue, condition_remplie
    retenue = offre_retenue(monde, id, autre, objet)
    return bool(retenue and condition_remplie(monde, id, retenue, prix))


def tient(monde, id, s, connus=None):
    """Le refus ``s`` tient-il encore ? Pour une cause, tant qu'il ne croit aucun moyen qu'il ne croyait
    déjà au refus : ce qu'il apprend qui en ôte un (le bois vu épuisé, une porte crue fermée à clé) ne le
    lève pas, revoir la même chose non plus. Pour un prix trop bas, toujours (pour ce prix seulement).
    Sinon, depuis moins de ``REDEMANDE`` minutes."""
    if s["operation"] == "reclamer_dette":
        avant = s.get("cause", [])
        return all(f in avant or f[0] == "pieces" and any(
            a[:3] == f[:3] and a[3] >= f[3] for a in avant)
            for f in moyens_crus(monde, id, s, connus))
    if s['operation'] == 'enqueter_cause':
        from .causes import contexte
        # Une date rafraîchie du même signe n'est pas une nouvelle cause.
        # Relire aussi les premières sauvegardes du lot qui portaient cette date.
        return all(f[:3] in [a[:3] for a in s.get('cause', [])]
                   for f in contexte(monde, id, s['de']))
    if s["operation"] == "enqueter_lieu":
        avant = {tuple(f) for f in s.get("cause", [])}
        return all(tuple(f) in avant for f in moyens_crus(monde, id, s, connus))
    if "contre_offre" in s:
        # Ce moyen se poursuit par le recours, hors de la recherche ordinaire.
        # Un délai ou la perte d'un moyen ne fait pas oublier la condition dite.
        return True
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

    if op == "reclamer_dette":
        from .biens import entrees_creance
        return entrees_creance(monde, id, s["de"])

    if s.get("mandat"):
        # Une impossibilité de mandat porte sur le plan social complet estimé,
        # pas seulement sur la position de sa cible. Dates de regard exclues.
        from .agendas import _croyances
        return [["mandat", o, _croyances(monde, id, moyens_seuls=True), None]]

    if op == "enqueter_lieu":
        # Seulement les entrées du demandeur, jamais le savoir privé du témoin.
        # L'absence et les dates seules n'apportent aucune indication nouvelle.
        import json
        faits.update(tuple(f) for f in s.get("cause", []) if f[0] == "lieu_appris")
        if s.get("information"):
            faits.add(("lieu_appris", o, s["information"]["lieu"], None))
        if s["raison"] in ("mefiance", "rancune"):
            from .relations import axes
            faits.add(("relation", s["de"], None, json.dumps(axes(monde, id, s["de"]), sort_keys=True)))
            return sorted((list(f) for f in faits), key=str)
        if s.get("repere"):
            faits.add(("repere", o, s["repere"]["lieu"], s["repere"]["revision"]))
        for salle, indices in lire(monde, id)["indices_recherche"].get(o, {}).items():
            for indice in indices:
                # La réponse situe une salle, pas une case. Une autre case,
                # une confirmation visuelle ou un relais du même lieu ne
                # renouvellent donc pas ce renseignement. Un bruit sans
                # auteur reste utile à l'inspection, sans réarmer ce témoin.
                if indice[0] == "presence" or indice[0] == "bruit" and indice[2] == o:
                    faits.add(("lieu_appris", o, salle, None))
        return sorted((list(f) for f in faits), key=str)

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
    consommer_indices_recherche(monde, id, qui, salle)


def consommer_indices_recherche(monde, id, qui, salle):
    """Indices déjà connus au constat d'échec, ou encore disponibles dans une ancienne partie."""
    # Le constat consomme aussi les indices présents avant la recherche (anciennes parties
    # comprises). Leur répétition ne doit pas suffire à annuler ce constat.
    c = lire(monde, id)["croyances"].get(qui, {}).get("lieu")
    if c and c["valeur"] == salle:
        _situer_recherche(monde, id, qui, salle, c.get("case"))
        _retenir_indice(monde, id, qui, salle, _indice_presence(c))
    from .memoire import bruits_retenus
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
    e = esprit(monde, id)
    e["recherches"].get(qui, {}).pop(salle, None)


def _situer_recherche(monde, id, qui, salle, case):
    """Un déplacement positivement appris est nouveau, même vers un ancien lieu d'échec.

    L'absence ne déplace pas ce repère ; une localisation moins précise ne l'efface pas.
    Cela distingue un retour appris de la répétition d'une voix au même endroit.
    """
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
    recherches = esprit(monde, id)["recherches"]
    change = False
    if indice is None:
        c = lire(monde, id)["croyances"].get(qui, {}).get("lieu")
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
    un protégé, un réflexe, et ce qu'il fait sur place (il y attend aussi bien).
    La routine, aller voir un bruit, rétablir ce qui ne presse pas, l'argent lui cèdent."""
    return bool(intention) and (intention["motif"] in urgents(monde, id)
                                or intention["motif"] in ("engagement", "alerte", "rejoint")
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


def _attendre_qui_vient(monde, id, resultat, palier=None):
    """Le rendez-vous fournit le lieu où chercher son interlocuteur : qui doit venir le rejoint
    au lieu d'explorer ailleurs. Un départ attend le rendez-vous, sauf palier
    strictement supérieur : dans ce cas sa rupture est annoncée. Qui attend
    quelqu'un qui a promis de venir (« J'arrive ! ») ne va pas le chercher : un plan qui
    commence par aller à lui, ou le chercher, devient l'attendre là où il est, le temps convenu ; son
    but reprend quand ils se sont retrouvés. Un plan qui fait d'abord autre chose ici reste tel quel."""
    from .appel import _vise, part, plan_venir, rompre_attente
    r = lire(monde, id)["rejoint"]
    if resultat and r and part(monde, id, resultat[1]):
        if palier is not None and palier < Palier.ATTENDRE_APPELANT:
            rompre_attente(monde, id)
        else:
            return {"type": "attendre", "qui": r["qui"]}, []
    from .eau import en_peril
    if en_peril(monde, id):
        return resultat
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
    from .memoire import episodes_parts_promises
    e = lire(monde, id)
    episodes = episodes_parts_promises(monde, id)
    for s in reversed(episodes):
        if s["type"] in ("promesse_annulee", "creance") and s.get("objet") == objet:
            return None
        if s["type"] == "nourri" and s.get("objet") == objet:
            return None
        if s["type"] == "promis" and s["objet"] == objet:
            if remise is not None and bool(s.get("remise")) != remise:
                return None
            # Reçue, annulée ou remboursée : la part à remettre n'est plus attendue.
            if s.get("part") and any(x["type"] in ("recu", "promesse_annulee", "creance") and x.get("objet") == s["part"]
                                     for x in episodes):
                return None
            feu = e["croyances"].get(s.get("foyer"), {}).get("etat")
            if (monde.data["minutes"] - s["minute"] >= ATTENTE_PART or feu and feu["minute"] >= s["minute"]
                    and feu["valeur"].get("allume") and not feu["valeur"].get("faible")):
                return None
            return s["de"]
    return None


def satisfaite(monde, id, condition):
    if condition.get('proteger'):
        return False  # Une responsabilité n'est pas tenue au seul fait d'arriver.
    if "pres" in condition:
        # Un séjour n'est pas acquitté à l'arrivée. Son motif décide de sa fin.
        return False
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
        if condition["objet"] == id:
            # Sa propre position ne dépend pas d'une croyance sur un objet.
            return monde.objets[id]["lieu"] == condition["lieu"]
        # Le tenir soi-même ne suffit pas : l'objet doit être déposé (ou tenu par un autre) sur place.
        return (not porte_par(monde, condition["objet"], id)
                and salle_crue(monde, id, condition["objet"]) == condition["lieu"])
    from .portes import refermable
    # Une installation détruite n'a plus de remise sous clé à accomplir.
    return (not refermable(_cru(monde, id, condition["objet"], "fin"))
            or _cru(monde, id, condition["objet"], "verrouillee") is True
            and not _ouvert_cru(monde, id, condition["objet"]))


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


def detresses_percues(monde, id):
    """Signes et lectures communs de peur ; aucune émotion privée d'autrui."""
    from .signes import percus, actives
    signes = percus(monde, id)
    vus = {s["id"] for s in signes}
    detresses = {s["personnage"] for s in signes if s["signe"] in ("tremble", "fuit")}
    detresses.update(x for x, _, c in actives(monde, id)
                     if c["signe"] in vus and c["valeur"] in ("peur", "crainte", "inquietude"))
    detresses.update(s["qui"] for s in episodes(monde, id, types=('detresse',))
                     if s["type"] == "detresse" and s["minute"] == monde.data["minutes"])
    return detresses


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
    # Un cri reconnu reste perçu jusqu'à la prochaine minute, même hors de vue.
    # Aucune lecture de la sécurité, du secours ou de l'intention privée d'autrui.
    detresses = detresses_percues(monde, id)
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
    from .tenir import captif
    if captif(monde, id):
        ecart += taux(monde, id, "captif")
    return ecart


def inquieter(monde, id, cause, signe=1):
    """Un événement inquiète (un bruit sans cause vue, un geste illicite) ou rassure (une ronde)."""
    if monde.objets.get(id, {}).get("profil"):
        relancer(monde, id, "securite", signe * taux(monde, id, cause))


def proteges(monde, id):
    """Responsabilités communes, ordre historique du profil et sans doublon."""
    return list(dict.fromkeys([*(profil(monde, id) or {}).get("protege", ()),
                               *sorted(agendas.proteges(monde, id))]))


def protecteurs(monde, protege):
    """Ceux dont le profil déclare protéger ce personnage."""
    from .corps import vivant, conscient
    if not vivant(monde, protege):
        return []
    return [x for x, o in monde.objets.items() if conscient(monde, x) and protege in proteges(monde, x)]


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
    if any(c.get("lieu") == salle or "objet" in c and salle_crue(monde, id, c["objet"]) == salle
           for c in agendas.gardes(monde, id)):
        return True
    for x in p.get("pulsions", []):
        c = x["condition"]
        if x["besoin"] in ("devoir", "biens") and (
                c.get("lieu") == salle or "objet" in c and salle_crue(monde, id, c["objet"]) == salle):
            return True
    return any(salle_crue(monde, id, x) == salle for x in proteges(monde, id))


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
    from .memoire import bruits_retenus
    for s in reversed(bruits_retenus(monde, id)):
        if resolu(monde, id, s):
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
    alerte = p.get("alerte")
    from .memoire import bruits_retenus
    for s in reversed(bruits_retenus(monde, id)):
        if resolu(monde, id, s):
            continue
        if s["nature"] == "appel" and s.get("qui") in proteges(monde, id):
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
    from .memoire import avertissements_a_donner
    esprit(monde, id)
    for s in reversed(avertissements_a_donner(monde, id)):
        if s["victime"] not in monde.objets:
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
    for s in episodes(monde, id, types=('vu_agir',)):
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


def lumiere_devant_crue(monde, id, objet, salle):
    """Éclairage ambiant de la cible, sans source portée, pour prévoir ou économiser.

    La lumière de la salle ne remplace pas une observation devant la cible.
    Une nouvelle source posée peut en revanche améliorer cette observation.
    """
    vue = _cru(monde, id, objet, "lumiere")
    return lumiere_crue(monde, id, salle) if vue is None else max(vue, apport_cru(monde, id, objet))


def lumiere_utile(monde, id, *, apres=None):
    """A-t-il besoin d'y voir, maintenant ou pour son plan ? Là où il se tient, ou là où son plan
    le mène, il croit le noir (``noir_cru`` : sans ce qu'il porte), et le noir l'inquiète ; ou il
    y a un geste qui demande d'y voir (crocheter) là où il ne croit pas la pleine lumière.
    Après une remise, juge les moyens conservés et le plan actif restant ;
    le trajet de restitution ne constitue pas un emploi futur du bien."""
    e = lire(monde, id)
    salle, peur = monde.objets[id]["lieu"], peur_du_noir(monde, id) > 0
    if salle not in monde.data["salles"]:
        return False
    if apres is not None:
        v, etat = apres
        salle = etat.salle
    if peur and (noir_cru(monde, id, salle) if apres is None else v.noir(etat)):
        return True
    intention = e['intention']
    plan = intention['plan'] if intention and (apres is None or 'rendre' not in intention['but']) else []
    if apres is not None and intention and 'rendre' not in intention['but']:
        # Un plan terminé peut tenir son but en restant sur place. La remise
        # projetée retire le moyen, sans déplacer ce séjour à son destinataire.
        salle = monde.objets[id]['lieu']
        etat = etat.apres(salle=salle)
        if not plan and peur and v.noir(etat):
            return True
    for etape in plan:
        if etape["operation"] == "aller" and etape["lieu"] in monde.data["salles"]:
            salle = etape["lieu"]
            if apres is not None:
                etat = etat.apres(salle=salle)
        if (peur and (noir_cru(monde, id, salle) if apres is None else v.noir(etat))
                or etape["operation"] in A_VUE
                and (lumiere_devant_crue(monde, id, etape["cible"], salle) if apres is None
                     else v.lumiere_devant(etat, etape['cible'])) < 2):
            return True  # Sa chance au geste compte sur la lumière qu'il croit (``chance_crochetage``).
    return False


def abri_valide(monde, id, salle):
    """Même abri au choix, en route et au séjour, sur ce qui est perçu ou cru."""
    from .eau import menacee
    from .esprits import pnjs
    from .defense import lieux_dangereux
    if (salle not in monde.data["salles"] or menacee(monde, id, salle)
            or salle in lieux_dangereux(monde, id)):
        return False
    if salle == monde.objets[id]["lieu"]:
        a = autour(monde, id)
        return bool(a["lumiere"] or a["fiables"])
    return (_eclairee_crue(monde, id, salle)
            or any(x != id and se_fie(monde, id, x) and salle_crue(monde, id, x) == salle
                   for x in [*pnjs(monde), "joueur"]))


def _plan_abri(monde, id):
    """Se mettre à l'abri : rejoindre un lieu qu'il croit éclairé où se tient quelqu'un qu'il croit
    fiable, et y rester ; là où il est d'abord, s'il l'est déjà. Un lieu où il croit l'eau, ou l'y
    attend bientôt (``eau.menacee``), n'est pas un abri. Tant qu'il voit l'eau monter, l'abri est
    le plus haut lieu éclairé qu'elle ne menace pas, avec ou sans compagnie : elle monte par le bas.
    S'il n'en atteint aucun et que l'eau menace où il se tient, il gagne au moins le lieu où il attend
    le moins d'eau, éclairé ou non : piégé, il cherche d'abord à sortir de l'eau (``candidats``).
    Hors de ce péril, un proche fiable perdu de vue devient un contact à chercher,
    sous le même parent abri, sans destination d'abri supposée."""
    from .eau import altitude, attendue, menacee, monte
    from .esprits import pnjs
    ici = monde.objets[id]["lieu"]
    # Une destination encore valide garde la main pendant son trajet : la
    # traversée d'un lieu humide n'est pas une nouvelle preuve contre l'abri.
    from .planification import _etape, abri, aller
    from .pnj import refus_etape

    def admissible(etapes):
        return etapes is not None and refus_etape(monde, id, etapes) is None

    from .defense import lieux_dangereux
    dangereuses = lieux_dangereux(monde, id)

    def sures():
        """Les lieux éclairés, hors de l'eau, où il croit quelqu'un de sûr."""
        salles = []
        from .relations import envers
        for x in sorted([*pnjs(monde), "joueur"], key=lambda x: (-envers(monde, id, x)["affection"], x)):
            if x == id or not se_fie(monde, id, x):
                continue
            salle = salle_crue(monde, id, x)
            if (salle in monde.data["salles"] and salle not in salles and _eclairee_crue(monde, id, salle)
                    and abri_valide(monde, id, salle)):
                salles.append(salle)
        return salles

    def chercher_un_proche():
        # Chercher ne fait encore d'aucune salle un abri : le parent sera
        # réévalué après contact, comme après un trajet vers un abri connu.
        from .planification import contacter
        from .relations import envers
        if menacee(monde, id, ici) or monte(monde, id):
            return None
        for x in sorted([*pnjs(monde), "joueur"], key=lambda x: (-envers(monde, id, x)["affection"], x)):
            if x == id or not se_fie(monde, id, x) or salle_crue(monde, id, x) is not None:
                continue
            etapes = contacter(monde, id, x)
            if etapes and admissible(etapes):
                return {"type": "abri", "lieu": None, "qui": x}, etapes
        return None

    i = lire(monde, id)["intention"]
    en_route = (i["but"].get("lieu") if i and i["plan"] and i["motif"] == "securite" and i["but"]["type"] == "abri" else None)
    eau_monte = monte(monde, id)
    if en_route and abri_valide(monde, id, en_route):
        trouve = abri(monde, id, [en_route])
        # Le prix d'abandon n'est pas une précondition de l'abri : au palier
        # intermédiaire, comparer à rester ne doit pas annuler le trajet choisi.
        etapes = trouve[1] if trouve is not None else aller(monde, id, en_route)
        if admissible(etapes):
            return {"type": "abri", "lieu": en_route}, etapes + [_etape("abriter", lieu=en_route)]
    if menacee(monde, id, ici) or eau_monte:
        salles = sorted((s for s in monde.data["salles"] if abri_valide(monde, id, s)
                         and _eclairee_crue(monde, id, s)), key=lambda s: (-altitude(monde, s), s != ici, s))
    else:
        salles = sures()
        if salles and ici != salles[0]:
            # Le plus aimé d'abord ; chaque trajet doit rester possible et valoir ce qu'il laisse.
            for salle in salles:
                trouve = abri(monde, id, [salle])
                if trouve is not None and admissible(trouve[1]):
                    return {"type": "abri", "lieu": trouve[0]}, trouve[1] + [_etape("abriter", lieu=trouve[0])]
            return chercher_un_proche()
        salles.sort(key=lambda s: s != ici)
    from .planification import _etape, aller
    for salle in salles:
        etapes = aller(monde, id, salle)
        if not admissible(etapes):
            continue
        return {"type": "abri", "lieu": salle}, etapes + [_etape("abriter", lieu=salle)]
    if menacee(monde, id, ici):
        # Aucun lieu hors de l'eau à sa portée : moins d'eau, c'est déjà en sortir. Ce n'est pas un
        # abri où rester (``pnj._abriter``) : il s'y rend.
        ici_cm = attendue(monde, id, ici)
        moins = sorted((s for s in monde.data["salles"] if s not in dangereuses and attendue(monde, id, s) < ici_cm),
                       key=lambda s: (attendue(monde, id, s), -altitude(monde, s), s))
        for salle in moins:
            etapes = aller(monde, id, salle)
            if etapes and admissible(etapes):
                return {"type": "abri", "lieu": salle}, etapes
    return chercher_un_proche()


def _plan_lumiere(monde, id):
    """Avoir de la lumière, quand il se tient dans le noir (ce qu'il ressent, ``autour``) et que
    le noir l'inquiète : la recherche (``planification.eclairer``). La lumière se tient là où le
    plan l'a choisie (``planification.RESTER``) : sa lumière en main en chemin, il la porte
    jusqu'au bout, là où il garde ses biens. Sans flamme portable, le séjour qui termine
    le recours reste un progrès de sécurité, au même titre que l'abri. La lumière
    d'un autre ne le suit pas."""
    if not peur_du_noir(monde, id):
        return None
    from .defense import lieux_dangereux
    dangereuses = lieux_dangereux(monde, id)
    if monde.objets[id]["lieu"] in dangereuses:
        return None
    from .perception import allumee
    porte = any(porte_par(monde, k, id) and "allume" in o and allumee(o) for k, o in monde.objets.items())
    # Il y voit par sa lumière en main, ou par celle du lieu (ses sources, une lueur voisine sur sa
    # case : ``lumiere_crue``, comme le planificateur) ; pas par celle qu'un autre porte, qui le
    # quittera avec lui.
    if porte or lumiere_crue(monde, id, monde.objets[id]["lieu"]):
        from .eau import menacee
        i = lire(monde, id)["intention"]
        if not i or i["but"]["type"] != "lumiere":
            return None
        destinations = [x["lieu"] for x in i["plan"] if x["operation"] in ("aller", "abriter")]
        if destinations and destinations[-1] in dangereuses:
            return None
        trajet = porte and i["plan"] and all(x["operation"] == "aller" for x in i["plan"])
        sejour = (not porte and (not i["plan"] or any(x["operation"] == "abriter" for x in i["plan"]))
                  and not menacee(monde, id, monde.objets[id]["lieu"])
                  and lire(monde, id)["besoins"].get("securite", 0) > SECURITE_FIN)
        if sejour and not i["plan"]:
            # Une livraison ou un geste incertain a coupé le plan. Le séjour
            # devient exécutable seulement quand sa lumière est constatée.
            from .planification import _etape
            return i["but"], [_etape("abriter", lieu=monde.objets[id]["lieu"])]
        return (i["but"], i["plan"]) if trajet or sejour else None
    from .planification import eclairer
    return eclairer(monde, id)


def _plan_reposer(monde, id):
    """Se reposer là où l'on est."""
    from .planification import _etape
    return {"type": "repos"}, [_etape("reposer")]


def ouvert_par_soi(monde, id, objet, depuis):
    """A-t-il lui-même ouvert ou déverrouillé cet objet dans les ``depuis`` dernières minutes ?"""
    return any(s["type"] == "ouvert_par_soi" and s["objet"] == objet and monde.data["minutes"] - s["minute"] <= depuis
               for s in episodes(monde, id, types=('ouvert_par_soi',)))


def garde_sous_cle(monde, id, objet):
    p = profil(monde, id)
    return bool(p) and any(x["condition"] == {"objet": objet, "verrouillee": True} for x in p["pulsions"])


def de_son_fait(monde, id, condition):
    """On ne s'alarme pas de ce qu'on vient de défaire soi-même : sa clé, sa main."""
    if condition.get("verrouillee"):
        return ouvert_par_soi(monde, id, condition["objet"], 2)
    return "lieu" in condition and "objet" in condition and porte_par(monde, condition["objet"], id)


def charges_gardees(monde, id):
    """Une charge commune aux pulsions, agendas, coûts et interposition."""
    p = profil(monde, id) or {}
    return [x["condition"] for x in p.get("pulsions", ())
            if x["besoin"] == "biens" and not periodique(x["condition"])
            and "objet" in x["condition"]] + agendas.gardes(monde, id)


def _lieux_gardes(monde, id, siens=False):
    """Les salles où il croit ce qu'il garde : ses pulsions de biens sur un objet, hors rondes.
    ``siens`` : seulement ce dont il a la charge, le sien ou celui qu'on lui a confié (y toucher
    n'est pas une faute, ``illicite``), pas ce qu'il convoite."""
    return {s for c in charges_gardees(monde, id)
            if not (siens and "objet" in c and illicite(monde, id, c["objet"]))
            for s in [salle_crue(monde, id, c["objet"]) if "objet" in c else c["lieu"]]
            if s in monde.data["salles"]}


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
    declarees = {s for c in agendas.gardes(monde, id)
                 for s in [salle_crue(monde, id, c["objet"]) if "objet" in c else c["lieu"]]
                 if s in monde.data["salles"]}
    if "biens" in urgents(monde, id):
        return tuple(sorted(_lieux_gardes(monde, id)))
    return tuple(sorted(declarees | set(menaces(monde, id))))


def _plan_garder(monde, id, condition):
    """Rester près de ce qu'il garde, en comptant ce que le lieu laisse monter (``planification.garder``)."""
    from .planification import garder
    salle = salle_crue(monde, id, condition["objet"])
    etapes = None if salle not in monde.data["salles"] else garder(monde, id, salle)
    return None if etapes is None else ({"type": "garder", "lieu": salle}, etapes)


def _delegue(monde, id, pulsion):
    """Une pulsion confiée au joueur attend tant que le PNJ le croit fiable ; une pulsion qu'il a payé
    quelqu'un de rétablir aussi (``tache_payee``)."""
    return bool(pulsion.get("delegue_a") and not agendas.aide_echue(monde, pulsion)
                and not se_mefie(monde, id, pulsion["delegue_a"])
                or tache_payee(monde, id, pulsion["condition"]))


def tache_payee(monde, id, condition):
    """Il a payé quelqu'un pour rétablir ``condition`` (``echanges.engager``) : il ne le fait pas à sa
    place tant que la parole court (``echanges.ENGAGEMENT_MAX``), qu'il le croit fiable et qu'il n'a
    pas appris qu'elle n'a pas été tenue (une créance de ce travail). Renvoie à qui, ou None."""
    from .echanges import ENGAGEMENT_MAX
    from .memoire import dernier_travail_paye
    s, reclame = dernier_travail_paye(monde, id, condition)
    if s is not None:
        if monde.data["minutes"] - s["minute"] > ENGAGEMENT_MAX or se_mefie(monde, id, s["a"]):
            return None
        if reclame:
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
    (de combien ce besoin dépasse encore son seuil, 0 s'il ne presse plus) de la marge
    d'engagement (``INERTIE`` majorée par VOL). On achève le geste entamé avant de céder à la faim naissante, et deux besoins qui
    pressent ensemble ne s'interrompent pas l'un l'autre à chaque minute."""
    s, e = seuils(monde, id), lire(monde, id)
    v = e["besoins"]
    i = e["intention"]
    en_cours = i["motif"] if inertie and i else None
    avance = max(0.0, v.get(en_cours, 0) - s[en_cours]) if en_cours in s else 0.0

    def presse(b):
        ecart = v.get(b, 0) - s[b]
        return (ecart >= (REPRISE if _etat_urgence(e, b) == "apaise" else 0)
                and (en_cours in (None, b) or ecart >= avance + marge_engagement(monde, id)))
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
    """Un besoin dont chaque recours est sans moyen admissible se met en attente :
    recherche sans plan ou renoncement dont l'obstacle cru tient encore. Dès qu'un
    recours aboutit, il presse de nouveau. Un recours non évalué ne décide rien."""
    u = esprit(monde, id)["urgences"]
    for b in pressants:
        issues = [essais.get(i) for i, (motif, _) in enumerate(liste) if motif == b]
        if "plan" in issues:
            etat = "presse"
        elif all(x in ("rien", "renonce") for x in issues):
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
    if agendas.pieces_poursuivies(monde, id):
        return None  # Même acquisition déjà comparée, y compris le sommeil sans moyen nouveau.
    return enrichir(monde, id)


def _plan_creance(monde, id):
    """Ce qu'on lui doit (``biens.rembourser``), qui vaut pour lui plus que le chemin : aller trouver
    son débiteur, pour qu'il le lui rende (``planification.reclamer``)."""
    from .planification import reclamer
    return reclamer(monde, id)


def _plan_remboursement(monde, id):
    from .planification import rembourser
    return rembourser(monde, id)


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


def _continuer_progres(monde, id, besoin):
    """Un progrès appartient au recours qui l'a engagé, pas seulement au besoin.

    Chaque méthode revalide son propre état terminal sur les croyances présentes.
    L'arbitrage commun peut toujours l'interrompre pour une urgence supérieure.
    """
    intention = lire(monde, id)["intention"]
    repli = None
    for methode in (*RECOURS.get(besoin, ()), PROGRES[besoin][0]):
        resultat = methode(monde, id)
        if resultat and resultat[0] == intention["but"]:
            return resultat
        if resultat and repli is None:
            repli = resultat
    return repli


def retabli_par_son_plan(monde, id, condition):
    """La remise sous clé appartient au plan en cours, même sans besoin urgent.

    Le choix continue de revalider le but et les gestes ; leur abandon rend la
    garde indépendante de nouveau. L'urgence du motif ne dit pas si une
    précondition temporaire du plan doit être annulée.
    """
    e = lire(monde, id)
    i = e["intention"]
    if (not i or i["but"] != {"type": "pulsion", **condition}) and condition in (
            agendas.charges_suspendues(monde, id).get("conditions", ())):
        return True
    if not (condition.get("verrouillee") and i and any(
            x["operation"] == "verrouiller" and x["cible"] == condition["objet"] for x in i["plan"])):
        return False
    if i["but"] != {"type": "pulsion", **condition}:
        return True  # Précondition temporaire d'un autre but, urgent ou non.
    # La garde protège les autres buts, jamais contre son propre candidat.
    return False


def candidats(monde, id):
    """Buts envisageables, du besoin le plus pressant au moins pressant ; la routine (rondes,
    surveillance) passe après ce qui presse vraiment et après une tâche acceptée. (besoin, méthode)."""
    for candidat in _candidats(monde, id):
        yield candidat.besoin, candidat.methode


def secours(monde, id):
    """Conditions ordinaires utiles à un besoin perçu ou retenu, sans lire l'esprit d'autrui.

    Le seuil du souci est celui des avis de menace ; le poids départage ensuite
    les secours. La faim et le froid naissent du corps perçu ; une détresse
    déjà retenue peut reprendre après une priorité propre, sans nouvelle vue.
    Le contrat adopté conserve sa condition et sa raison indépendamment du moyen.
    Le choix seul lit la perception : la recherche reçoit une condition existante.
    """
    from .esprits import percus
    vus = percus(monde, id)[0]
    e = lire(monde, id)
    from .signes import detresse_retenue
    peurs = (detresses_percues(monde, id) | {x for x, c in e["croyances"].items()
             if (x == "joueur" or monde.objets.get(x, {}).get("type") == "personnage")
             and c.get("detresse", {}).get("valeur")
             and detresse_retenue(monde, id, x)}) if calme_pour_secourir(monde, id) else set()
    for autre in sorted(set(vus) | peurs):
        if autre == id or (autre != "joueur" and monde.objets.get(autre, {}).get("type") != "personnage"):
            continue
        poids = _poids_secours(monde, id, autre)
        if poids is None:
            continue
        etat = e["croyances"].get(autre, {}).get("etat", {})
        corps = etat.get("valeur", {})
        if corps.get("mort") or corps.get("conscient") is False:
            continue
        if autre in peurs:
            yield autre, "peur", poids, {"pres": autre}
        if autre not in vus:
            continue
        if etat.get("source") not in ("vu", "essai"):
            continue
        if corps.get("faim"):
            for objet in _connus(monde, id):
                if monde.objets[objet]["type"] == "nourriture" and _disponible_cru(monde, id, objet):
                    yield autre, "faim", poids, {"objet": objet, "servir": autre}
        if corps.get("chaleur"):
            salle = salle_crue(monde, id, autre)
            for objet in _connus(monde, id):
                if not monde.objets[objet].get("foyer") or salle is None or salle_crue(monde, id, objet) != salle:
                    continue
                condition = {"objet": objet, "allume": True}
                if not satisfaite(monde, id, condition):
                    yield autre, "chaleur", poids, condition


def _poids_secours(monde, id, autre):
    """Même disposition sociale à la naissance et à la revalidation du secours."""
    from .caractere import valeur
    from .relations import envers, rancune
    lien = envers(monde, id, autre)
    empathie = valeur(monde, id, "empathie")
    if rancune(lien) or valeur(monde, id, "altruisme") + empathie + lien["affection"] < 100:
        return None
    return empathie * (lien["affection"] + 20) / 100


def calme_pour_secourir(monde, id):
    """Sa propre détresse ne peut faire de lui une compagnie rassurante."""
    from .signes import de
    return not any(s["signe"] in ("tremble", "fuit") for s in de(monde, id))


class Palier(IntEnum):
    """Priorités communes, du premier but tenté au dernier."""
    PERIL_EAU = 0
    ALARME = 1
    RANIMER = 2
    DESESPOIR = 3
    BESOIN_PRESSANT = 4
    PAROLE_DUE = 5
    PREVENIR = 6
    REJOINDRE = 7
    ATTENDRE_APPELANT = 8
    BRUIT_A_VOIR = 9
    PULSION_ROMPUE = 10
    PROGRES_EN_COURS = 11
    SECOURS = 12
    ROUTINE = 13
    ARGENT = 14


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
    demande: object = None


def _raison_tient(monde, id, demande):
    """Une raison sociale est une croyance du porteur, jamais l'état d'autrui.

    Les demandes sans bénéficiaire ont leur propre prédicat de condition ou
    d'agenda. Une observation plus récente peut démentir une détresse ; perdre
    son champ de vision n'est pas une telle observation.
    """
    raison = demande.get("raison")
    if raison is None:
        return True
    if raison["besoin"] == "peur":
        from .signes import detresse_retenue
        etat = _cru(monde, id, raison["qui"], "etat") or {}
        return bool(_poids_secours(monde, id, raison["qui"]) is not None
                    and calme_pour_secourir(monde, id)
                    and not etat.get("mort") and etat.get("conscient") is not False
                    and not etat.get("parti")
                    and detresse_retenue(monde, id, raison["qui"]))
    etat = _cru(monde, id, raison["qui"], "etat") or {}
    return bool(_poids_secours(monde, id, raison["qui"]) is not None
                and etat.get(raison["besoin"]) and not etat.get("mort")
                and etat.get("conscient") is not False)


def _reprendre_demande(monde, id, demande):
    """Revalider la demande adoptée sans relancer son critère de naissance.

    Le planificateur reste seul juge des moyens. Une absence de plan ne
    prouve pas l'impossibilité : aucun plan périmé n'est réinstallé ici.
    """
    if not _raison_tient(monde, id, demande):
        return None
    if "condition" in demande:
        condition = demande["condition"]
        if satisfaite(monde, id, condition):
            return None
        if demande.get("tache") and _delegue(monde, id, {"condition": condition}):
            # Une parole payée en cours suspend l'action propre, pas le but.
            # Refaire une offre à plus bas prix n'est pas sa continuation.
            intention = lire(monde, id)["intention"]
            return (intention["but"], []) if intention else None
        return _plan_pulsion(monde, id, condition, demande.get("tache", False))
    if "agenda" in demande:
        if not any(a["id"] == demande["agenda"] and a["etat"] in ("actif", "sommeil")
                   for a in agendas.projets(monde, id)):
            return None
        return agendas.planifier(monde, id, demande["agenda"])
    raise ValueError("demande de poursuite inconnue")


def _fin_demande(monde, id, demande):
    """Une fin ou un démenti attesté ; None reste une absence de certificat.

    Les familles interprètent leurs conditions, l'arbitrage ne déduit jamais
    une fin de la longueur d'un plan ou d'une recherche sans réponse.
    """
    raison = demande.get("raison")
    if raison:
        if raison["besoin"] == "peur" and not _raison_tient(monde, id, demande):
            return "dementie", {"raison": raison, "detresse_retenue": lire(monde, id)["croyances"].get(raison["qui"], {}).get("detresse"),
                                "calme": calme_pour_secourir(monde, id),
                                "souci": _poids_secours(monde, id, raison["qui"])}
        etat = _cru(monde, id, raison["qui"], "etat") or {}
        if etat.get("mort") or etat.get("conscient") is False:
            return "dementie", {"raison": raison, "etat_cru": etat}
        if raison["besoin"] == "peur" or raison["besoin"] not in etat:
            return None
        if not etat[raison["besoin"]]:
            return "accomplie", {"raison": raison, "etat_cru": etat}
        if _poids_secours(monde, id, raison["qui"]) is None:
            from .caractere import valeur
            from .relations import envers, rancune
            lien = envers(monde, id, raison["qui"])
            return "dementie", {"raison": raison, "disposition": {
                "rancune": rancune(lien), "affection": lien["affection"],
                "altruisme": valeur(monde, id, "altruisme"),
                "empathie": valeur(monde, id, "empathie"), "seuil": 100}}
    if "condition" in demande and satisfaite(monde, id, demande["condition"]):
        return "accomplie", {"condition": demande["condition"], "satisfaite": True}
    if "agenda" in demande:
        projet = next((a for a in agendas.projets(monde, id) if a["id"] == demande["agenda"]), None)
        if projet is None or projet["etat"] == "abandonne":
            return "dementie", {"agenda": demande["agenda"], "etat": projet["etat"] if projet else "absent"}
        if projet["etat"] == "atteint":
            return "accomplie", {"agenda": demande["agenda"], "etat": "atteint"}
        if projet["etat"] == "sommeil":
            return "dementie", {"agenda": demande["agenda"], "etat": "sommeil",
                                "raison": projet["raison"], "croyances": projet["croyances"]}
    return None


def _sortie(intention, minute, cause, faits):
    from copy import deepcopy
    return {"cause": cause, "minute": minute, "faits": deepcopy(faits),
            "intention": {k: deepcopy(intention[k]) for k in ("but", "motif", "depuis")}}


def _domine(autre, actif, marge=INERTIE):
    """Même contrat d'arbitrage pour toute intention, attente et garde comprises."""
    return (autre.palier < actif.palier
            or autre.palier == actif.palier and autre.valeur >= actif.valeur + marge)


def _meme_demande_adoptee(candidat, intention, resultat, contrat):
    demande = contrat.get("demande")
    return candidat.demande == demande if demande else resultat[0] == intention["but"]


def _candidats(monde, id):
    """Candidats triés par leur urgence explicite, avec leur rang (la routine
    après le reste) et s'ils sont un recours de leur besoin (ce qui l'apaise ou le rétablit) ; une
    parole due, prévenir, attendre l'appelant, une alarme, sortir de l'eau, un bruit à voir et l'argent
    n'en sont pas : ils passent devant un recours en cours (``choisir``).

    Un besoin qui vient à peine de franchir son seuil laisse finir le plan en cours d'un autre
    motif, et un besoin apaisé ne presse de nouveau que nettement au-dessus (``urgents``)."""
    p, e = profil(monde, id), esprit(monde, id)
    buts = []

    def ajouter(besoin, methode, palier, departage=(), valeur=0, routine=False, recours=False, demande=None):
        buts.append(Candidat(besoin, methode, routine, recours, Urgence(palier, valeur, departage), demande))

    # Ceux qui laissent finir le plan en cours n'y ajoutent rien, mais restent pressants : ni
    # routine ni pulsion rompue de leur fait ne passe devant ce plan.
    pressants = urgents(monde, id)
    s = seuils(monde, id)
    for besoin in urgents(monde, id):
        ecart, rang_besoin = e["besoins"][besoin] - s[besoin], BESOINS.index(besoin)
        rang_recours = 0

        def ajouter_recours(methode, routine=False, demande=None):
            nonlocal rang_recours
            desespere = bool(agendas.presents(monde, id)) and e["besoins"][besoin] >= DESESPOIR
            # Les routines d'un besoin pressant précèdent les autres routines, même à écart nul.
            departage = ((0, -ecart, rang_besoin, rang_recours) if routine and not desespere
                         else (rang_besoin, rang_recours))
            ajouter(besoin, methode, Palier.DESESPOIR if desespere else (
                    Palier.ROUTINE if routine else Palier.BESOIN_PRESSANT),
                    departage, 0 if routine and not desespere else ecart, routine, True, demande)
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
                                periodique(x["condition"]), {"condition": x["condition"], "tache": True})
                if "allume" in x["condition"]:
                    # Un feu sans bois qu'il connaisse : il demande à qui pourrait en avoir.
                    ajouter_recours(lambda m, i: _plan_enquete(m, i, "chaleur"))
        if besoin == "biens":
            for x in pulsions:
                if periodique(x["condition"]):
                    continue
                if any(c.get("objet") == x["condition"].get("objet")
                       for c in agendas.gardes(monde, id)):
                    continue
                ajouter_recours(lambda m, i, c=x["condition"]: _plan_garder(m, i, c), True)
    # Toute parole de service suit le devis qui l'a fait accepter, jusqu'à son abandon annoncé.
    from .defense import interposition
    ajouter("devoir", interposition, Palier.PAROLE_DUE, (-1,))
    from .planification import planifier_engagement
    for rang, agenda in enumerate(agendas.essayables(monde, id)):
        if agenda["etat"] in ("actif", "sommeil"):
            ajouter("agenda", lambda m, i, a=agenda["id"]: agendas.planifier(m, i, a),
                    Palier.BESOIN_PRESSANT, (len(BESOINS), rang), agendas.poids(monde, id, agenda),
                    demande={"agenda": agenda["id"]})
    for rang, x in enumerate(agendas.en_cours(monde, id)):
        ajouter("engagement", lambda m, i, x=x: planifier_engagement(m, i, x), Palier.PAROLE_DUE, (rang,))
    # Un corps à terre connu : recours au même graphe de gestes, sans accès à ses PV ni son réveil.
    for rang, protege in enumerate(proteges(monde, id)):
        c = e["croyances"].get(protege, {}).get("etat", {})
        if c.get("valeur", {}).get("conscient") is False and not c["valeur"].get("mort"):
            from .planification import ranimer
            ajouter("devoir", lambda m, i, x=protege: ranimer(m, i, x), Palier.RANIMER, (-rang,))
    # Un protégé atteint sous ses yeux : il va le prévenir, comme une parole due.
    from .memoire import avertissements_a_donner
    if avertissements_a_donner(monde, id):
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
    for rang, lieu in enumerate(dict.fromkeys(agendas.suivis_delegations(monde, id))):
        ajouter('devoir', lambda m, i, s=lieu: voir(m, i, s),
                Palier.BESOIN_PRESSANT, (-1, rang))
    a_voir, alarme_ = bruit_a_voir(monde, id), alarme(monde, id)
    if alarme_:
        ajouter(alarme_[1], lambda m, i, s=alarme_[0]: voir(m, i, s), Palier.ALARME)
    # L'eau déjà présente ou la noyade attendue : sortir d'un séjour humide
    # n'attend pas que l'inquiétude franchisse son seuil (ni celui de noyade).
    from .eau import en_peril, traversee_sure
    evacuation = e["intention"] and e["intention"]["but"]["type"] == "abri"
    if ("securite" in p["besoins"] and en_peril(monde, id)
            and (evacuation or not traversee_sure(monde, id))):
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
                    Palier.PULSION_ROMPUE, (i, 0), recours=True, demande={"condition": c, "tache": True})
            if "allume" in c:
                ajouter(x["besoin"], lambda m, i: _plan_enquete(m, i, "chaleur"),
                        Palier.PULSION_ROMPUE, (i, 1), recours=True)
    # Assis pour se reposer, ou près du feu, il ne s'en va qu'une fois remis, ou pour plus pressant.
    # Seulement si son plan comporte bien ce geste : une ronde a le même motif que l'abri.
    for rang, (besoin, (methode, fin)) in enumerate(PROGRES.items()):
        if (e["intention"] and e["intention"]["motif"] == besoin and e["besoins"].get(besoin, 0) > fin
                and any(x["operation"] == GESTE_PROGRES[besoin] for x in e["intention"]["plan"])):
            ajouter(besoin, lambda m, i, b=besoin: _continuer_progres(m, i, b),
                    Palier.PROGRES_EN_COURS, (rang,), recours=True)
    for rang, (autre, besoin, poids, condition) in enumerate(secours(monde, id)):
        ajouter("empathie", lambda m, i, c=condition: _plan_pulsion(m, i, c),
                Palier.SECOURS, (autre, besoin, rang), poids,
                demande={"condition": condition, "raison": {"qui": autre, "besoin": besoin}})
    # La routine : ses rondes, même quand le besoin qu'elles servent ne presse pas.
    for rang, x in enumerate(p["pulsions"]):
        if (periodique(x["condition"]) and x["besoin"] not in pressants
                and not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)):
            ajouter(x["besoin"], lambda m, i, c=x["condition"]: _pulsion_a_soi(m, i, c),
                    Palier.ROUTINE, (1, rang), routine=True, recours=True,
                    demande={"condition": x["condition"], "tache": True})
    # L'argent : un poids permanent, qui ne presse jamais ; il ne passe qu'après tout le reste.
    # Ce qu'on lui doit d'abord, puis des pièces à prendre.
    ajouter(ARGENT, _plan_remboursement, Palier.ARGENT, (0,), routine=True)
    ajouter(ARGENT, _plan_creance, Palier.ARGENT, (1,), routine=True)
    ajouter(ARGENT, _plan_argent, Palier.ARGENT, (2,), routine=True)
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
    p = profil(monde, id)
    if not p:
        return
    e = esprit(monde, id)
    installer(monde, id)
    agendas.clore_aides_constatees(monde, id)
    COMPTES["choix"] += 1
    # Le danger immédiat se traite avant les besoins ordinaires, avec un choix au coût.
    from .defense import choisir as choisir_defense
    reaction = choisir_defense(monde, id)
    if reaction is None:
        from .tenir import evasion
        reaction = evasion(monde, id)
    if reaction is not None:
        but, etapes = reaction
        from .appel import part, rompre_attente
        if part(monde, id, etapes):
            rompre_attente(monde, id)
        ancien = e["intention"]
        if ancien and ancien["but"] != but:
            agendas.clore_intention(monde, id, _sortie(ancien, minute, "palier", {"reaction": but}))
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
        from .eau import en_peril
        if (not en_peril(monde, id)
                and chemin(monde, id, monde.objets[id]["lieu"], intention["but"]["lieu"]) is not None):
            from .appel import part, rompre_attente
            if part(monde, id, intention["plan"]):
                rompre_attente(monde, id)
            return  # Le réflexe déclaré garde la priorité jusqu'à son terme.
        e["intention"] = None  # Route coupée ou séjour dans l'eau : réévaluer les recours.
    pressants = urgents(monde, id)
    essais = {}
    # Revalidation de l'intention avant l'arbitrage. Le nombre de gestes ne dit
    # ni si son but est accompli, ni s'il est encore admissible.
    courant = e["intention"]
    precedent = courant
    contrat_precedent = agendas.contrat_intention(monde, id) or {}
    charges_precedentes = agendas.charges_suspendues(monde, id)
    sortie = None
    moyen_dementi = False
    manque = e["manque"]
    if courant and courant["plan"] and manque and manque["minute"] == minute:
        from .pnj import _geste
        if _geste(courant["plan"][0]) == manque["etape"]:
            if (contrat_precedent.get("demande") or {}).get("raison"):
                # Le moyen est démenti, pas la demande adoptée. Libérer son
                # ancien suffixe puis replanifier ; sa raison seule décide
                # de sa fin, même quand le bénéficiaire sort du champ.
                courant = {**courant, "plan": []}
                e["intention"] = courant
                moyen_dementi = True
            else:
                sortie = _sortie(courant, minute, "dementie", {"manque": manque})
                courant = None
                e["intention"] = None
    resultat = None
    choisi = None
    marge = marge_engagement(monde, id)
    from .planification import vues_du_choix
    with vues_du_choix(monde, id), agendas.reconstruction_charges(monde, id, charges_precedentes):
        agendas.actualiser(monde, id)
        if courant and contrat_precedent.get("demande"):
            fin = _fin_demande(monde, id, contrat_precedent["demande"])
            if fin:
                sortie = _sortie(courant, minute, *fin)
        # Les générateurs ne doivent pas préférer l'ancienne cible du moyen
        # manqué. La demande reste locale et sera revalidée séparément.
        parent = e["intention"]
        try:
            if moyen_dementi:
                e["intention"] = None
            tous = list(_candidats(monde, id))
        finally:
            e["intention"] = parent
        # Vérifier une occasion n'est pas reprendre le geste abandonné. La
        # ronde existante met les croyances à jour, même sans nouvelle reçue.
        lieux = {r["cause"]["salle"] for rs in e["renoncements"].values()
                 if isinstance(rs, list) for r in rs if r["cause"]["type"] != "corps"}
        for salle in sorted(lieux):
            condition = {"lieu": salle, "periode": PATIENCE}
            if not satisfaite(monde, id, condition):
                tous.append(Candidat("securite", lambda m, i, c=condition: _plan_pulsion(m, i, c),
                                     True, False, Urgence(Palier.ROUTINE, 0, (2,)), None))
        tous.sort(key=lambda c: c.urgence.cle())
        liste = [(c.besoin, c.methode) for c in tous]
        evaluations = {}

        def evaluer(n, candidat):
            if n in evaluations:
                return evaluations[n]
            besoin, urgence = candidat.besoin, candidat.urgence
            parent = e["intention"]
            try:
                from .pnj import refus_etape
                if moyen_dementi:
                    e["intention"] = None
                agenda = (candidat.demande or {}).get('agenda')
                if (courant and (courant['plan'] or contrat_precedent.get('phase') == 'attendre')
                        and not moyen_dementi
                        and agenda and agenda == courant['but'].get('agenda')
                        and contrat_precedent.get('recours') == agendas.entrees_recours(monde, id, agenda)
                        and refus_etape(monde, id, courant['plan']) is None):
                    # Le moyen adopté va jusqu'au constat, sauf nouvelle entrée
                    # ou démenti. Les urgences concurrentes gardent l'arbitrage.
                    proposition = (courant['but'], courant['plan'])
                else:
                    proposition = candidat.methode(monde, id)
            finally:
                e["intention"] = parent
            retenus = e["renoncements"].get(besoin, [])
            if (proposition and urgence.palier != Palier.PERIL_EAU
                    and any(renoncement_tient(monde, id, r, proposition)
                            for r in (retenus if isinstance(retenus, list) else []))):
                essais[n] = "renonce"
                evaluations[n] = None
                return None
            if proposition:
                from .pnj import refus_etape, _geste
                if (moyen_dementi and manque and manque["minute"] == minute and proposition[1]
                        and _geste(proposition[1][0]) == manque["etape"]):
                    # Même contrat que l'exécution : ne pas réinstaller le
                    # geste encore marqué manqué. Un autre moyen est permis.
                    proposition = None
            if proposition:
                from .pnj import refus_etape
                if refus_etape(monde, id, proposition[1]) is not None:
                    proposition = None
            if proposition and urgence.palier != Palier.PERIL_EAU:
                # Le même contrôle vaut aussi pour les recours sans trajet :
                # l'échec d'une évacuation ne rend pas licite un séjour humide.
                from .eau import en_peril, traversee_sure
                destination = monde.objets[id]["lieu"]
                for etape in proposition[1]:
                    if etape["operation"] == "aller":
                        destination = etape["lieu"]
                if (en_peril(monde, id, destination)
                        or en_peril(monde, id) and not traversee_sure(monde, id, proposition[1])):
                    proposition = None
            essais[n] = "plan" if proposition else "rien"
            evaluations[n] = proposition
            return proposition

        actif = None
        moyens_revalides = False
        if courant:
            # Une demande typée persiste indépendamment de sa naissance.
            # Pour les anciennes sauvegardes, on retrouve d'abord son candidat.
            contrat = agendas.contrat_intention(monde, id) or {}
            demande = contrat.get("demande")
            correspondants = [(n, c) for n, c in enumerate(tous)
                              if c.besoin == courant["motif"]
                              and (not demande or c.demande == demande)]
            for n, candidat in correspondants:
                proposition = evaluer(n, candidat)
                if proposition and _meme_demande_adoptee(candidat, courant, proposition, contrat):
                    actif = (candidat, proposition)
                    moyens_revalides = True
                    break
            if actif is None and demande:
                valeur = contrat["valeur"]
                if demande.get("raison"):
                    valeur = _poids_secours(monde, id, demande["raison"]["qui"])
                    valeur = 0 if valeur is None else valeur
                urgence = Urgence(Palier(contrat["palier"]), valeur, ())
                candidat = Candidat(courant["motif"],
                                    lambda m, i: _reprendre_demande(m, i, demande),
                                    False, True, urgence, demande)
                proposition = evaluer(len(tous), candidat)
                if proposition:
                    actif = (candidat, proposition)
                    moyens_revalides = True
                elif sortie is None:
                    fin = _fin_demande(monde, id, demande)
                    if fin:
                        sortie = _sortie(courant, minute, *fin)
                    from .pnj import refus_etape
                    if sortie is None and refus_etape(monde, id, []) is None:
                        # Une recherche sans réponse ne certifie ni la fin
                        # ni le démenti de la demande. Attendre un moyen ou
                        # une information garde son identité et son palier,
                        # sans réinstaller de geste périmé ; jamais dans l'eau.
                        actif = (candidat, (courant["but"], []))
            # Le geste manqué est un démenti du plan courant, pas une preuve
            # que tous les moyens vers le même but sont impossibles. Seule la
            # nouvelle planification ci-dessus peut le réinstaller.
        # La fin du service n'efface pas la remise en état de ses préparatifs.
        # Les moyens de cette phase sont recalculés sur le cru, non recopiés
        # d'un ancien suffixe (le destinataire a pu être rejoint ailleurs).
        restauration = False
        conditions = charges_precedentes.get("conditions", [])
        porteur = courant or precedent
        if porteur and conditions and (charges_precedentes.get("restaurer")
                                       or not (sortie and sortie["cause"] == "dementie")):
            fin = _fin_demande(monde, id, contrat_precedent["demande"]) if contrat_precedent.get("demande") else None
            condition = {k: v for k, v in porteur["but"].items() if k != "type"}
            if porteur["but"]["type"] == "pulsion":
                due = any(x["condition"] == condition and not x.get("annule")
                          for x in agendas.en_cours(monde, id))
                # Une charge personnelle peut être satisfaite par l'état cru ;
                # une parole due s'acquitte par son geste, pas par cet état.
                if not due and (porteur["motif"] != "engagement" and satisfaite(monde, id, condition) or any(
                        s["type"] == "engagement_tenu" and s.get("condition") == condition
                        and s["minute"] >= porteur["depuis"] for s in episodes(monde, id, types=('engagement_tenu',)))):
                    fin = ("accomplie", {"condition": condition})
            if (charges_precedentes.get("restaurer") or fin and fin[0] == "accomplie"):
                from .planification import restaurer_charges, _couper
                from .pnj import refus_etape
                if all(satisfaite(monde, id, c) for c in conditions):
                    retablir = (0, [], None)
                elif (courant and courant["plan"] and charges_precedentes.get("restaurer")
                      and refus_etape(monde, id, courant["plan"]) is None):
                    retablir = (0, courant["plan"], None)
                else:
                    retablir = restaurer_charges(monde, id, conditions)
                if retablir and retablir[1]:
                    urgence = Urgence(Palier(contrat_precedent.get("palier", Palier.PULSION_ROMPUE)),
                                      contrat_precedent.get("valeur", 0), ())
                    candidat = Candidat(porteur["motif"],
                                        lambda m, i: (porteur["but"], _couper(retablir[1])), False, True, urgence,
                                        contrat_precedent.get("demande"))
                    proposition = evaluer(len(tous) + 1, candidat)
                    if proposition:
                        actif = (candidat, proposition)
                        restauration = True
                        moyens_revalides = False
                        sortie = None
                    else:
                        charges_precedentes = {}
                else:
                    # Accompli ou aucun moyen admissible : plus de suspension.
                    charges_precedentes = {}
        for n, candidat in enumerate(tous):
            moyen_disponible = bool(actif and not moyens_revalides
                                    and actif[0].demande and actif[0].demande.get("raison")
                                    and candidat.demande and candidat.demande.get("raison") == actif[0].demande["raison"]
                                    and candidat.urgence.palier == actif[0].urgence.palier
                                    and candidat.urgence.valeur >= actif[0].urgence.valeur)
            if actif and not _domine(candidat.urgence, actif[0].urgence, marge) and not moyen_disponible:
                continue
            proposition = evaluer(n, candidat)
            if moyen_disponible and proposition and not proposition[1]:
                continue  # Une attente sans moyen ne remplace pas une autre attente.
            if proposition:
                choisi, resultat = candidat, proposition
                if actif and precedent and not _meme_demande_adoptee(
                        candidat, precedent, proposition, contrat_precedent):
                    cause = "palier" if candidat.urgence.palier < actif[0].urgence.palier else "gain"
                    sortie = _sortie(precedent, minute, cause,
                                     {"palier_actif": int(actif[0].urgence.palier),
                                      "palier_nouveau": int(candidat.urgence.palier),
                                      "valeur_active": actif[0].urgence.valeur,
                                      "valeur_nouvelle": candidat.urgence.valeur, "marge": marge,
                                      **({"moyen_actif": False, "moyen_nouveau": True} if moyen_disponible else {})})
                break
        if resultat is None and actif:
            choisi, resultat = actif
            if (moyens_revalides and courant["plan"] and resultat[1]
                    and courant["plan"][0] == resultat[1][0] and resultat[0] == courant["but"]
                    and not (choisi.demande and choisi.demande.get("tache")
                             and _delegue(monde, id, {"condition": choisi.demande["condition"]}))):
                from .pnj import refus_etape
                if refus_etape(monde, id, courant["plan"]) is None:
                    # Revalider le but n'oblige pas à reconstruire ses moyens.
                    # Les préparatifs et la remise en état du plan adopté
                    # restent tenus jusqu'à un démenti ou une préemption.
                    resultat = (courant["but"], courant["plan"])
    if resultat:
        besoin = choisi.besoin
        from .eau import en_peril
        but, etapes = resultat
        retenus = e["renoncements"].get(besoin)
        if isinstance(retenus, list):
            # Essayer un autre moyen ne réhabilite pas le premier. Seule la
            # levée de sa cause peut solder la mémoire de cet obstacle.
            e["renoncements"][besoin] = [r for r in retenus
                                        if r["but"] != but or obstacle_patience(monde, id, r["cause"])]
        # Une sortie nécessaire ne devient pas une attente de rendez-vous ou
        # de contrepartie dans l'eau après le contrôle du candidat.
        but, etapes = _attendre_qui_vient(monde, id, resultat, choisi.urgence.palier)
        if not en_peril(monde, id):
            from .pnj_propositions import plan_recours
            offre = plan_recours(monde, id, besoin, etapes)
            if offre:
                etapes = offre
        intention = precedent
        meme = bool(intention) and intention["but"] == but
        meme_engagement = bool(intention) and _meme_demande_adoptee(
            choisi, intention, (but, etapes), contrat_precedent)
        if intention and not meme_engagement and sortie is None:
            sortie = _sortie(intention, minute, None, {"evaluation": "indeterminee"})
        if sortie is None and meme_engagement:
            # Une continuation ne gomme pas la dernière sortie attestée.
            # Un seul événement est conservé : ce n'est pas une pile de buts.
            sortie = contrat_precedent.get("sortie")
        e["intention"] = {"but": but, "motif": besoin, "plan": etapes,
                          "depuis": intention["depuis"] if meme else minute,
                          "attente": intention["attente"] if meme else 0,
                          **({"attitude": intention["attitude"]} if meme and "attitude" in intention else {})}
        from .planification import suspensions
        charges = list(charges_precedentes.get("conditions", ())) if meme_engagement else []
        for c in suspensions(monde, id, etapes, but):
            if c not in charges:
                charges.append(c)
        agendas.retenir_charges(monde, id, charges,
                               restaurer=restauration and meme_engagement)
        agendas.retenir_intention(monde, id, {"palier": int(choisi.urgence.palier),
                                             "valeur": choisi.urgence.valeur,
                                             "demande": choisi.demande,
                                             "phase": "attendre" if not etapes else "continuer" if meme_engagement else "naitre",
                                             "sortie": sortie})
        if not meme:
            e["patience"] = None  # Un autre but : ce qu'il attendait pour l'ancien ne compte plus.
        _classer(monde, id, pressants, liste, essais, minute)
        return
    from .pnj_propositions import plan_recours
    refusee = e["demande_refusee"]
    from .eau import en_peril
    offre = plan_recours(monde, id, refusee["besoin"], None) if refusee and not en_peril(monde, id) else None
    e["intention"] = ({"but": {"type": "proposition", "objet": refusee["objet"]},
                       "motif": refusee["besoin"], "plan": offre, "depuis": minute, "attente": 0}
                      if offre else None)
    if precedent:
        agendas.clore_intention(monde, id, sortie or _sortie(
            precedent, minute, None, {"evaluation": "indeterminee"}))
    _classer(monde, id, pressants, liste, essais, minute)


def menager_flamme(monde, id, minute):
    """Une flamme portable qu'il a allumée ou employée pour allumer, et que son plan n'emploie
    plus, se consume pour rien : il l'éteint d'abord, et la garde pour plus tard. Celle qui
    l'éclaire quand il a besoin d'y voir (``lumiere_utile``), sans autre lumière en main, ne se
    consume pas pour rien."""
    from .perception import allumee
    from .biens import services_proteges
    proteges = {c["objet"] for c in services_proteges(monde, id) if c.get("allume")}
    e = esprit(monde, id)
    plan = e["intention"]["plan"] if e["intention"] else []
    vises = {x["cible"] for x in plan} | {x["outil"] for x in plan}
    allumees = {s["objet"] for s in episodes(monde, id, types=('flamme_employee',)) if s["type"] == "flamme_employee"}
    flamme = next((k for k in sorted(allumees) if k in monde.objets and k not in vises
                   and k not in proteges and porte_par(monde, k, id) and allumee(monde.objets[k])), None)
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


def obstacle_patience(monde, id, cause):
    """Juge commun de l'occasion attendue, uniquement sur les perceptions/croyances.

    Les dates de perception ne libèrent pas un obstacle retenu. Un témoin
    perdu de vue reste une présence crue jusqu'à un constat ou une nouvelle.
    Le passage emploie la géométrie commune, avec les obstacles *crus*.
    """
    from .pnj import temoins_crus, oreilles_crues, _franchissable
    e = lire(monde, id)
    if cause['type'] == 'contact':
        from .positions_crues import contact_interrompu_tient
        return contact_interrompu_tient(monde, id, cause)
    if cause["type"] == "corps":
        from .corps import conscient
        return not conscient(monde, id)
    if cause["type"] == "temoins":
        presents = set()
        if monde.objets[id]["lieu"] == cause["salle"]:
            presents.update(temoins_crus(monde, id))
            presents.update(oreilles_crues(monde, id, cause["nature"]))
        for qui, salle in cause.get("temoins", {}).items():
            if (salle_crue(monde, id, qui) == salle
                    and (_cru(monde, id, qui, "etat") or {}).get("conscient") is not False):
                presents.add(qui)
        if "temoins" in cause:
            # Une présence apprise depuis le renoncement ne disparaît pas non
            # plus par vieillissement du dernier bruit ou du dernier regard.
            for qui in e["croyances"]:
                if (qui != id and (qui == "joueur" or monde.objets.get(qui, {}).get("type") == "personnage")
                        and salle_crue(monde, id, qui) == cause["salle"]
                        and (_cru(monde, id, qui, "etat") or {}).get("conscient") is not False):
                    presents.add(qui)
        return sorted(presents)
    from .spatial import trajet
    o = monde.objets[id]
    places, solides = set(), set()
    for qui, attributs in e["croyances"].items():
        lieu = attributs.get("lieu") or {}
        salle, case = lieu.get("salle"), lieu.get("case")
        if qui == id or salle not in monde.data["salles"] or case is None or lieu.get("valeur") != salle:
            continue
        objet = monde.objets.get(qui, {})
        if qui == "joueur" or objet.get("type") == "personnage":
            places.add((salle, tuple(case)))
        elif objet.get("bloque_passage"):
            solides.add((salle, tuple(case)))
    arrivees = {(s, tuple(c)) for s, c in cause["arrivees"]}
    chemin = trajet(monde, o["lieu"], o["position"],
                    lambda s, c: (s, c) in arrivees and (s, c) not in places,
                    franchissable=lambda p: _franchissable(monde, id, p),
                    libre=lambda s, c: (s, c) not in solides and (s, c) not in places, solides=False)
    return chemin is None


def renoncement_tient(monde, id, retenu, proposition):
    """Un autre but ou un moyen qui évite l'obstacle reste possible."""
    but, plan = proposition
    if but != retenu["but"]:
        return False
    cause = retenu["cause"]
    etape = cause["etape"]
    cles = ("operation", "cible", "lieu")
    meme_obstacle = any(all(p.get(k) == etape.get(k) for k in cles) for p in plan)
    if cause["type"] == "temoins":
        meme_obstacle = any(
            p.get("cible") and p["cible"] == etape.get("cible")
            or p.get("condition") == "sans_temoin"
            and salle_crue(monde, id, p.get("cible")) == cause["salle"] for p in plan)
    if not meme_obstacle:
        return False
    return bool(obstacle_patience(monde, id, cause))


def renoncer(monde, id, minute, cause=None):
    """Retient l'obstacle réellement rencontré, sans échéance de réessai."""
    from copy import deepcopy
    from .temps import instant
    e = esprit(monde, id)
    intention = e["intention"]
    if cause is None:
        from .corps import conscient
        assert not conscient(monde, id), "Un renoncement conscient doit transmettre sa cause"
        cause = {"type": "corps", "salle": monde.objets[id]["lieu"],
                 "etape": dict(intention["plan"][0]) if intention["plan"] else {}}
    motif = intention["motif"]
    retenus = e["renoncements"].get(motif, [])
    # L'ancien entier ne portait aucune cause : ne pas en inventer une lors
    # d'une migration. Les nouveaux renoncements remplacent ces seuls délais.
    if not isinstance(retenus, list):
        retenus = []
    retenu = {"instant": instant(monde), "but": deepcopy(intention["but"]), "cause": deepcopy(cause)}
    def meme_obstacle(r):
        return (r["but"] == retenu["but"] and r["cause"]["type"] == cause["type"]
                and r["cause"]["salle"] == cause["salle"]
                and all(r["cause"]["etape"].get(k) == cause["etape"].get(k)
                        for k in ("operation", "cible", "lieu")))
    e["renoncements"][motif] = [r for r in retenus if not meme_obstacle(r)] + [retenu]
    e["patience"] = None
    memoriser(monde, id, {"type": "renoncement", "but": dict(intention["but"])})
    e["intention"] = None
