"""Échanges typés entre personnages : affirmer, demander un objet, l'acheter, confier une
tâche, remettre.

Les mêmes règles valent pour le joueur et pour les PNJ. Une affirmation démentie par ce que
l'auditeur a vu récemment est rejetée et le locuteur perd sa confiance ; sinon un jet de CHA
du locuteur, contre un DD que la confiance de l'auditeur abaisse ou relève, décide s'il la
croit. Un objet n'est remis que par celui qui le porte, s'il fait confiance au demandeur et
n'en a pas besoin ; son altruisme rend le partage plus facile, sa volonté (``jet_persuasion``)
le rend plus dur à convaincre, et ce que vaut pour lui le prix qu'on ne lui paie pas aussi
(``biens.reticence``). Ce qu'il accorde dépend de qui il croit entendre (``voix``) : à une voix
qu'il ne sait à qui prêter, la confiance d'un étranger ; prudent, il lui demande d'abord « Qui va
là ? » (issue « qui_va_la »), même pour un achat ou pour lui rendre son bien. Payé son prix
(``biens.prix``), il vend sans se faire prier, s'il ne le garde pas et ne se méfie pas de
l'acheteur. Remis par son propriétaire, un objet qui dure est prêté (``biens.preter`` :
l'emprunteur en use sans faute et le rendra), ce qui se consomme est donné ; son propriétaire
qui le redemande le récupère, sauf s'il sert encore. Une tâche confiée devient un engagement
que le planificateur du moteur exécute quand rien de plus urgent ne presse ; sur un bien de celui
qui la confie, elle en confie la garde (``biens.gardes``). Tout est déterministe hors des jets du
moteur.
"""
from .francais import pluriel as nombre_pluriel
from .francais import quantite
from . import agendas
from .caractere import penchant
from .esprits import RECENT, constater, croire, croyance, esprit, lire, memoriser, percevoir
from .paroles import _phrase, _stats_pnj, dementi, jet_persuasion
from .relations import FIABLE, avis, mefiance, percue, rancune

ENGAGEMENT_MAX = 240   # minutes avant qu'un engagement non tenu soit abandonné
PARTAGE = 12           # DD d'une demande (une part, un objet prêté), que l'altruisme de celui qui donne abaisse
TACHE = 12             # DD d'une tâche confiée
PAS_PROPOSITION = 5.0  # minutes de valeur propre par point de persuasion
PRIX_SANS_PRIX = 1     # convention commune pour un objet sans prix déclaré


def _devis_proposition(monde, id, condition, pour, devis=None):
    """Le devis existant, sur ses croyances, avec la permission de la tâche proposée."""
    if not monde.objets.get(id, {}).get("profil"):
        return None
    cle = (id, tuple(sorted(condition.items())), pour)
    if devis is not None and cle in devis:
        return devis[cle]
    if _charge_irrealisable(monde, id, condition, pour):
        resultat = None
    else:
        copie = monde.copier()
        agendas.prendre(copie, id, {"condition": condition, "pour": pour, "minute": copie.data["minutes"]})
        resultat = devis_service(copie, id, condition, pour)
    if devis is not None:
        devis[cle] = resultat
    return resultat


def _charge_irrealisable(monde, id, condition, pour):
    """Preuve d'impossibilité du devis existant, sans exploration ni mutation.

    Le devis d'entretien vise (allumé, chargé). Sans réservoir rechargeable,
    aucun geste autonome ne peut rendre « chargé » vrai : alimenter et la part
    de combustible exigent tous deux ``brule``. Si sa charge initiale est fausse
    ou inconnue, ce but est donc inaccessible, indépendamment des trajets.
    La projection et ses dates restent celles du planificateur commun.
    """
    from .perception import brule
    from .deliberation import _cru
    from .planification import _vu_avant_la_tache
    if not condition.get("allume") or brule(monde.objets[condition["objet"]]):
        return False
    etat = _cru(monde, id, condition["objet"], "etat") or {}
    # Ajouter la proposition datée de maintenant ne change pas cette lecture :
    # sans engagement préalable, _vu_avant_la_tache prend déjà maintenant.
    return (_vu_avant_la_tache(monde, id, condition, pour)
            or not (etat.get("charge") and not etat.get("faible")))


def devis_service(monde, id, condition, pour):
    """Le devis autonome et les fournitures que son bénéficiaire peut réellement livrer.

    La recherche autorise une demande au bénéficiaire. Avant tout accord, celui-ci
    doit pouvoir la fournir selon le même contrat de livraison que lors du geste.
    Les essais matériels restent sur une copie, sans jet ni publication.
    """
    from .deliberation import besoin_de_part
    from .planification import devis_pulsion
    from .spatial import porte_par
    # Ni le joueur ni un personnage sans autonomie n'exécute un plan de PNJ.
    # L'absence de devis n'interdit pas une remise déjà possible en main.
    if not monde.objets.get(id, {}).get("profil"):
        return None
    devis = devis_pulsion(monde, id, condition, pour)
    if devis is None:
        return None
    copie = None
    for etape in devis[1]:
        if etape["operation"] not in ("demander", "acheter") or etape["cible"] != pour:
            continue
        objet = etape["outil"]
        if objet not in monde.objets:
            continue
        if pour == "joueur":
            return None  # Une réponse future du joueur n'est pas une fourniture acquise.
        if copie is None:
            copie = monde.copier()
        siens_a_portee(copie, pour)
        if accueil(copie, id, pour) or garde(copie, pour, copie.objets[objet]):
            return None
        if besoin_de_part(copie.objets[objet]):
            if _remettre_part(copie, pour, id, objet, 0) == "impossible":
                return None
        elif necessaire(copie, pour, objet):
            return None
        elif not porte_par(copie, objet, pour):
            if not copie.objets.get(pour, {}).get("profil"):
                return None
            livraison = {"objet": objet, "remettre": id}
            agendas.prendre(copie, pour, {"condition": livraison, "pour": id, "minute": copie.data["minutes"]})
            if devis_pulsion(copie, pour, livraison, id) is None:
                return None
    return devis


def valeur_proposition(monde, auditeur, terme, pour, *, devis=None):
    """Prix propre, en minutes ; les tâches sont chiffrées par le plan cru de l'auditeur."""
    from .biens import prix
    from .caractere import valeur_pieces
    from .deliberation import besoin_de_part, parts
    from .vol import proprietaire
    t = terme["type"]
    if t == "rien":
        return 0.0
    if t == "pieces":
        return valeur_pieces(monde, auditeur, terme["montant"])
    if t == "tache":
        trouve = _devis_proposition(monde, auditeur, terme["condition"], pour, devis)
        return None if trouve is None else trouve[0]
    # Le prix est une donnée de valeur, pas une lecture de l'état caché du bien.
    objet = terme["objet"]
    montant = prix(monde, objet, t == "part")
    if t == "objet" and "pieces" in monde.objets[objet]:
        crue = croyance(monde, auditeur, objet, "pieces")
        n = monde.objets[objet]["pieces"] if proprietaire(monde, monde.objets[objet]) == auditeur else (crue["valeur"] if crue else 0)
        montant = (montant or PRIX_SANS_PRIX) + n
    if montant is None and t == "objet" and besoin_de_part(monde.objets[objet]) is not None:
        # Il compte sa propre réserve ; la quantité cachée chez l'autre ne nourrit pas son jugement.
        quantite = parts(monde.objets[objet]) if proprietaire(monde, monde.objets[objet]) == auditeur else 1
        montant = quantite * (prix(monde, objet, True) or PRIX_SANS_PRIX)
    # Céder un bien ne retire aucune pièce de sa bourse : même sans argent, un
    # outil ou une clé garde sa valeur. ``depense`` plafonne au numéraire possédé.
    return valeur_pieces(monde, auditeur, montant if montant is not None else PRIX_SANS_PRIX)


def _livraison_proposition(monde, donneur, receveur, terme):
    """Vérifier le bien réellement remis, sur copie, avant tout accord.

    Pour une part, le devis éventuel porte sur la pièce détachée, jamais le lot.
    Les propres biens à portée sont constatés comme lors d'une demande historique.
    """
    from .propositions import prestation
    from .spatial import porte_par
    condition = prestation(monde, donneur, receveur, terme)
    if terme["type"] not in ("objet", "part"):
        return True
    if porte_par(monde, terme["objet"], donneur):
        return True
    if not monde.objets.get(donneur, {}).get("profil"):
        return False  # Aucune prise future exécutée par un acteur sans autonomie.
    copie = monde.copier()
    siens_a_portee(copie, donneur)
    if terme["type"] == "part":
        return _remettre_part(copie, donneur, receveur, terme["objet"], 0) != "impossible"
    condition = condition or {"objet": terme["objet"], "remettre": receveur}
    return _devis_proposition(copie, donneur, condition, receveur) is not None


def evaluer_proposition(monde, proposant, auditeur, demande, contrepartie, *, devis=None):
    """P/G/L et DD communs, indépendants de l'identité du proposant. Aucun jet ni mutation."""
    from .caractere import caracteristique, valeur
    arret = accueil(monde, proposant, auditeur)
    if arret:
        return {"cause": arret}
    if demande["type"] in ("objet", "part"):
        objet = demande["objet"]
        if demande["type"] == "objet" and necessaire(monde, auditeur, objet):
            return {"cause": "necessaire"}
        if garde(monde, auditeur, monde.objets[objet]):
            return {"cause": "garde"}
        from .deliberation import parts
        if demande["type"] == "part" and parts(monde.objets[objet]) <= 0:
            return {"cause": "epuise"}
        if not _livraison_proposition(monde, auditeur, proposant, demande):
            return {"cause": "impossible"}
    if demande["type"] == "pieces" and "objet" in demande:
        from .spatial import porte_par
        objet = demande["objet"]
        if garde(monde, auditeur, monde.objets[objet]):
            return {"cause": "garde"}
        if not porte_par(monde, objet, auditeur):
            return {"cause": "impossible"}
    p = valeur_proposition(monde, auditeur, demande, proposant, devis=devis)
    if p is None:
        return {"cause": "impossible"}
    if demande["type"] == "tache":
        _, etapes = _devis_proposition(monde, auditeur, demande["condition"], proposant, devis)
        for e in etapes:
            if e["operation"] in ("alimenter", "manger", "servir"):
                for x in (e.get("cible"), e.get("outil")):
                    if x in monde.objets and garde(monde, auditeur, monde.objets[x]):
                        return {"cause": "garde"}
    # Une tâche promise ne vaut que si elle sert un but réellement cru de l'auditeur.
    buts = [x["condition"] for x in (monde.objets[auditeur].get("profil") or {}).get("pulsions", [])]
    buts += [x["condition"] for x in agendas.en_cours(monde, auditeur, actifs=True)]
    g = valeur_proposition(monde, auditeur, contrepartie, auditeur, devis=devis)
    if contrepartie["type"] == "tache" and contrepartie["condition"] not in buts:
        g = 0.0
    if g is None:
        g = 0.0  # Aucun moyen cru : il ne compte pas sur ce service.
    r = percue(monde, auditeur, proposant)
    if contrepartie["type"] == "tache":
        g *= r["confiance"] / 100
    # Une demande peut elle-même réaliser un but : le gain est le devis évité, sans vérité cachée.
    if demande["type"] == "tache" and demande["condition"] in buts:
        g += p
    lien = (penchant(monde, auditeur, "altruisme") + r["affection"] / 25
            + r["dette"] * valeur(monde, auditeur, "loyaute") / 50 - r["rancune"] / 20)
    return _bilan_valeur(p, g, lien, caracteristique(monde, auditeur, "INT"), r)


def _bilan_valeur(p, g, lien, intelligence, r):
    """Même prix de la disproportion pour le verdict et son anticipation."""
    mauvais = max(0, p - g) * max(0, intelligence - 8) / PAS_PROPOSITION
    # jet_persuasion porte déjà affection, rancune et dette/20 : ne les compter qu'une fois.
    dd = (PARTAGE + (p - g) / PAS_PROPOSITION + mauvais - lien
          + r["affection"] / 25 + r["dette"] / 20 - r["rancune"] / 20)
    return {"cause": None, "P": p, "G": g, "L": lien, "dd_base": dd}


def offre_sensee(monde, proposant, autre, demande, contrepartie, *, devis=None):
    """Le proposant se juge comme celui à qui l'on demanderait la contrepartie.

    Pas de jet ni d'accès aux dispositions privées de l'autre. Le lien peut rendre
    un marché acceptable à l'auditeur ; il ne justifie pas de proposer à perte.
    """
    if demande is None:
        return False
    if devis is None:
        devis = {}
    if contrepartie["type"] == "tache" and not promesse_autonome(monde, proposant, autre, contrepartie, devis=devis):
        return False
    bilan = evaluer_proposition(monde, autre, proposant, contrepartie, demande, devis=devis)
    if bilan["cause"] or bilan["P"] > bilan["G"]:
        return False
    # La demande reste bornée au but, y compris pour un plan ancien rechargé.
    from .propositions import demande_utile, demande_financee
    if (demande_utile(monde, proposant, demande) != demande
            or demande_financee(monde, proposant, demande, contrepartie) != demande):
        return False
    estimation = anticiper_valeur(monde, proposant, autre, demande, contrepartie)
    from .caractere import modificateur
    maximum = 20 + modificateur(monde, proposant, "CHA") + modificateur(monde, proposant, "ELO")
    return estimation["dd_base"] + 1 <= maximum


def promesse_autonome(monde, proposant, autre, terme, *, devis=None):
    """Un PNJ n'offre que le travail qu'il peut fournir sans réponse d'un tiers."""
    if proposant == "joueur":
        return True
    trouve = _devis_proposition(monde, proposant, terme["condition"], autre, devis)
    return trouve is not None and bool(trouve[1]) and not any(
        e["operation"] in ("demander", "acheter", "confier", "engager", "proposer")
        or e["condition"] == "sans_temoin" for e in trouve[1])


def anticiper_valeur(monde, proposant, autre, demande, contrepartie):
    """Évaluation commune de valeur sur les seules connaissances du proposant.

    Les dispositions privées ne sont pas devinées : situation, richesse liquide,
    intelligence et lien neutres. Les prix sont publics, les pièces d'un objet
    sont celles qu'il connaît. Aucun jet, livraison ni attitude réelle de l'autre.
    """
    from copy import copy
    from .biens import BOURSE
    from .esprits import CHAMPS
    m = copy(monde)
    m.objets = {i: dict(o) for i, o in monde.objets.items()}
    m.data = {**monde.data, "objets": m.objets,
              "finances_pnj": {autre: BOURSE},
              "esprits": {autre: {k: f() for k, f in CHAMPS.items()}}}
    m._cache_vue = {}
    m.objets[autre]["profil"] = None
    m.objets[autre]["corps"] = {}
    crues = lire(monde, proposant)["croyances"]
    m.data["esprits"][autre]["croyances"] = crues
    for i, o in m.objets.items():
        if "pieces" in o:
            o["pieces"] = crues.get(i, {}).get("pieces", {}).get("valeur", 0)
            # La richesse liquide adverse est inconnue, même si une bourse est visible.
            o["lieu"] = None
    p = valeur_proposition(m, autre, demande, proposant)
    g = valeur_proposition(m, autre, contrepartie, autre)
    # Les services non connus comme utiles ne sont pas un gain acquis.
    if p is None:
        return {"dd_base": float("inf")}
    return _bilan_valeur(p, g or 0.0, 0, 10, {"affection": 0, "dette": 0, "rancune": 0})


def proposer(monde, proposant, auditeur, demande, contrepartie):
    """Marché atomique : devis, jet, transferts et engagements avant publication des faits."""
    from .biens import donner, richesse
    from .deliberation import parts
    from .deplacement_objet import deplacer
    from .spatial import porte_par, proche
    from .vol import proprietaire
    from .propositions import verifier, payer_terme
    verifier(monde, {"type": "proposition", "demande": demande, "contrepartie": contrepartie}, proposant=proposant)
    original, monde = monde, monde.copier()
    for terme, de, a in ((demande, auditeur, proposant), (contrepartie, proposant, auditeur)):
        if terme["type"] == "tache" and agendas.en_cours(
                monde, de, condition=terme["condition"], personne=a, actifs=True):
            return {"cause": "deja"}
    if contrepartie.get("objet") and demande.get("objet") == contrepartie["objet"]:
        return {"cause": "meme_bien"}
    # Les remises présentes exigent le contact ; parler de loin ne téléporte aucun bien.
    if not proche(monde, auditeur, proposant):
        return {"cause": "portee"}
    # L'auditeur qui refuse même de traiter n'a aucun devis de livraison à faire.
    # Même évaluation que pour un marché recevable, avant les recherches matérielles.
    if accueil(monde, proposant, auditeur):
        return evaluer_proposition(monde, proposant, auditeur, demande, contrepartie)
    if contrepartie["type"] == "tache" and not promesse_autonome(monde, proposant, auditeur, contrepartie):
        return {"cause": "impossible"}
    for terme, de in ((demande, auditeur), (contrepartie, proposant)):
        if terme["type"] in ("objet", "part"):
            o = monde.objets[terme["objet"]]
            if proprietaire(monde, o) != de:
                return {"cause": "propriete"}
            if de == proposant and not porte_par(monde, o["id"], de):
                return {"cause": "absent"}
            if terme["type"] == "part" and parts(o) <= 0:
                return {"cause": "epuise"}
        elif terme["type"] == "pieces":
            if "objet" in terme:
                source = monde.objets[terme["objet"]]
                if proprietaire(monde, source) != de:
                    return {"cause": "propriete"}
                if garde(monde, de, source):
                    return {"cause": "garde"}
                if not porte_par(monde, source["id"], de):
                    return {"cause": "absent"}
                disponible = source["pieces"]
            else:
                disponible = richesse(monde, de)
            if disponible < terme["montant"]:
                return {"cause": "pauvre"}
    bilan = evaluer_proposition(monde, proposant, auditeur, demande, contrepartie)
    if bilan["cause"]:
        return bilan
    accepte, _ = jet_persuasion(monde, auditeur, proposant, bilan["dd_base"])
    original.data["jets"] = monde.data["jets"]
    if not accepte:
        return dict(bilan, cause="marche" if bilan["P"] > bilan["G"] else "persuasion")
    for terme, de, a in ((contrepartie, proposant, auditeur), (demande, auditeur, proposant)):
        t = terme["type"]
        if t in ("objet", "part"):
            if de == auditeur and not porte_par(monde, terme["objet"], de):
                siens_a_portee(monde, de)
                if t == "part":
                    if _remettre_part(monde, de, a, terme["objet"], 0) == "impossible":
                        return {"cause": "impossible"}
                else:
                    agendas.prendre(monde, de, {"condition": {"objet": terme["objet"], "remettre": a},
                                               "pour": a, "minute": monde.data["minutes"]})
                bilan["livraison_differee"] = True
                continue
            objet = detacher_part(monde, terme["objet"]) if t == "part" else terme["objet"]
            donner(monde, objet, a)
            deplacer(monde, objet, a)
            from .biens import compte, noter_compte
            noter_compte(monde, compte(de, a, objet, 1, "rendu"))
            if a != "joueur":
                memoriser(monde, a, {"type": "recu", "de": de, "objet": objet, "livraison": True,
                                     **({"lot": terme["objet"]} if t == "part" else {})})
        elif t == "pieces":
            payer_terme(monde, de, a, terme)
        elif t == "tache":
            engagement = {"condition": terme["condition"], "pour": a, "minute": monde.data["minutes"]}
            if not agendas.en_cours(monde, de, condition=terme["condition"], personne=a, actifs=True):
                agendas.prendre(monde, de, engagement)
                if de != "joueur":
                    memoriser(monde, de, {"type": "engagement_pris", "pour": a, "condition": terme["condition"]})
    if demande["type"] != "tache":
        from .relations import doit
        from .voix import identifie
        if identifie(monde, auditeur, proposant) and doit(monde, auditeur, proposant):
            memoriser(monde, auditeur, {"type": "dette_honoree", "de": proposant, "service": "demande"})
    original.adopter(monde)
    return dict(bilan, cause=None, accepte=True)


def clarte(monde, auditeur):
    """Un auditeur d'INT faible retient moins sûrement ce qu'on lui dit."""
    return 0.5 if _stats_pnj(monde, auditeur)["INT"] <= 8 else 1.0


def affirmer(monde, locuteur, auditeur, sujet, attribut, valeur):
    """« dementi », « doute », « crue » ou « decouvert » (crue puis démentie sous ses yeux)."""
    e = esprit(monde, auditeur)
    actuelle = croyance(monde, auditeur, sujet, attribut)
    if (actuelle and actuelle["valeur"] == valeur and actuelle["source"] in ("vu", "essai")
            and monde.data["minutes"] - actuelle["minute"] <= RECENT):
        return "crue"  # Il vient de le voir lui-même : la parole le confirme sans rien lui apprendre.
    from .voix import identifie, se_mefier, source_dite
    if dementi(monde, auditeur, sujet, attribut, valeur):
        # Il se méfie de qui lui ment : de lui s'il sait qui c'est, sinon de cette voix.
        if identifie(monde, auditeur, locuteur):
            memoriser(monde, auditeur, {"type": "mensonge_dementi", "locuteur": locuteur,
                                        "sujet": sujet, "attribut": attribut})
        se_mefier(monde, auditeur, locuteur, "vu")
        return "dementi"
    from .signes import flairer
    if flairer(monde, auditeur, locuteur, sujet, attribut, valeur):
        return "doute"
    if not jet_persuasion(monde, auditeur, locuteur, 10)[0]:
        memoriser(monde, auditeur, {"type": "parole_doutee", "locuteur": locuteur,
                                    "sujet": sujet, "attribut": attribut})
        return "doute"
    lieu = {"salle": valeur if valeur in monde.data["salles"] else None, "case": None} if attribut == "lieu" else {}
    source, certitude = source_dite(monde, auditeur, locuteur), round(0.7 * clarte(monde, auditeur), 2)
    if attribut == FIABLE:
        avis(monde, auditeur, sujet, valeur, source, certitude)  # Ce qu'il croit d'une personne : ``relations``.
    else:
        croire(monde, auditeur, sujet, attribut, valeur, source, certitude, **lieu)
    memoriser(monde, auditeur, {"type": "parole_crue", "locuteur": locuteur, "sujet": sujet, "attribut": attribut})
    # Ce qu'il a sous les yeux peut le démentir aussitôt.
    percevoir(monde, auditeur)
    if any(s["type"] == "mensonge_decouvert" and s.get("sujet") == sujet for s in e["memoire"][-3:]):
        return "decouvert"
    return "crue"


def necessaire(monde, auditeur, objet):
    """Un objet qui sert son plan en cours ou une de ses pulsions (l'objet, sa clé) n'est pas
    prêté, ni la source qui l'éclaire quand il a besoin d'y voir (``deliberation.lumiere_utile``).
    Le plan qui le rend à son propriétaire ne compte pas : ce n'est pas s'en servir."""
    intention = lire(monde, auditeur)["intention"]
    if (intention and "rendre" not in intention["but"]
            and any(objet in (e["cible"], e["outil"]) for e in intention["plan"])):
        return True
    if "allume" in monde.objets[objet] and monde.objets[auditeur].get("profil"):
        from .deliberation import lumiere_utile
        if lumiere_utile(monde, auditeur):
            return True
    profil = monde.objets[auditeur].get("profil")
    for pulsion in (profil or {}).get("pulsions", []):
        cible = pulsion["condition"].get("objet")
        if cible and (objet == cible or cible in monde.objets[objet].get("ouvre", [])):
            return True
    return False


def demande_de_part(monde, demandeur, auditeur, objet):
    """On peut demander une part d'une ressource comptée qui appartient à l'autre, même rangée
    ailleurs ou portée, pour ses gestes : vivres, recharge d'une source ou entretien d'un feu.
    Le partage ne transfère jamais le lot entier simplement parce que le donneur le porte."""
    from .deliberation import besoin_de_part
    from .social import _proprietaire
    o = monde.objets.get(objet)
    return bool(o and besoin_de_part(o) is not None
                and _proprietaire(monde, {"objet": objet}) == auditeur)


def foyer_de(monde, auditeur, demandeur, foyer=None, combustible=None):
    """Le feu qu'une part de combustible entretient : celui que vise le demandeur, sinon un foyer
    que l'auditeur connaît dans la salle d'où il l'entend demander (le joueur compris : qu'il le voie
    ou n'entende qu'une voix, il sait d'où elle vient), sinon le premier qu'il connaît. La source
    doit brûler ce combustible ; une source explicitement nommée n'est jamais remplacée."""
    from .deliberation import _connus, salle_crue
    from .ouie import _place
    from .perception import recharge
    def convient(f):
        return combustible is None or recharge(monde.objets[f], monde.objets[combustible])
    if foyer is not None:
        return foyer if foyer in monde.objets and "allume" in monde.objets[foyer] and convient(foyer) else None
    foyers = [f for f in _connus(monde, auditeur) if monde.objets[f].get("foyer") and convient(f)]
    salle = _place(monde, demandeur)[0]
    return next((f for f in foyers if salle_crue(monde, auditeur, f) == salle), foyers[0] if foyers else None)


def garde(monde, id, o):
    """Ce qu'il garde d'une ressource comptée qui est à lui : sa réserve (``reserve``), et ce dont
    il a lui-même besoin."""
    from .deliberation import besoin_de_part, part_pour, parts, reserve, urgents
    from .vol import proprietaire
    return (besoin_de_part(o) is not None and proprietaire(monde, o) == id
            and (parts(o) <= reserve(monde, id) or besoin_de_part(o) in urgents(monde, id)
                 and part_pour(monde, id, o["id"], besoin_de_part(o))))


def accueil(monde, demandeur, auditeur):
    """Ce qui arrête une demande avant qu'il la pèse : « mefiance » envers qui il croit entendre
    (``relations.percue``), « qui_va_la » si c'est une voix inconnue et qu'il est prudent ; None."""
    from .voix import qui_va_la
    r = percue(monde, auditeur, demandeur)
    if mefiance(r):
        return "mefiance"
    if rancune(r):
        return "rancune"
    return "qui_va_la" if qui_va_la(monde, auditeur, demandeur) else None


def contre_offre(monde, demandeur, auditeur, objet, raison):
    """Une condition qu'il sait honorer, jamais une nouvelle chance de persuasion.

    Les gardes et pulsions durables restent des empêchements. Un besoin corporel
    n'est exprimable que par un service du contrat commun ; le repas servi est
    aujourd'hui le seul de ces services qui apaise directement le corps.
    """
    from .biens import prix, reticence
    from .deliberation import _connus, SATIETE, urgents
    from .propositions import offre
    from .vol import proprietaire
    if raison not in ("refus", "necessaire") or accueil(monde, demandeur, auditeur):
        return None
    part = demande_de_part(monde, demandeur, auditeur, objet)
    demande = {"type": "part" if part else "objet", "objet": objet}
    if not _livraison_proposition(monde, auditeur, demandeur, demande):
        return None
    if raison == "refus":
        if proprietaire(monde, monde.objets[objet]) != auditeur:
            return None  # Il ne vend pas le bien d'un tiers.
        montant = prix(monde, objet, part) or PRIX_SANS_PRIX
        # Recherche monotone du seuil propre : aucune lecture de la bourse adverse.
        bas, haut = 1, montant
        while bas < haut:
            milieu = (bas + haut) // 2
            if reticence(monde, auditeur, montant, milieu) <= 0:
                haut = milieu
            else:
                bas = milieu + 1
        condition = {"type": "pieces", "montant": bas}
    else:
        intention = lire(monde, auditeur)["intention"]
        if not intention or intention["motif"] not in urgents(monde, auditeur):
            return None
        besoin = intention["motif"]
        if besoin != "faim":
            return None  # Pas de condition corporelle correspondante dans les termes communs.
        copie = monde.copier()
        e = esprit(copie, auditeur)
        e["besoins"][besoin] = max(0, e["besoins"][besoin] - SATIETE)
        e["intention"] = None
        if besoin in urgents(copie, auditeur) or necessaire(copie, auditeur, objet) or garde(copie, auditeur, copie.objets[objet]):
            return None
        nourritures = [o for o in sorted(_connus(monde, auditeur))
                       if monde.objets[o]["type"] == "nourriture" and o != objet]
        if not nourritures:
            return None
        condition = {"type": "tache", "condition": {"objet": nourritures[0], "servir": auditeur}}
    return offre(auditeur, demandeur, condition, demande)


def offre_retenue(monde, demandeur, auditeur, objet):
    return next((s for s in reversed(lire(monde, demandeur)["refus"])
                 if s["de"] == auditeur and s.get("objet") == objet and "contre_offre" in s), None)


def condition_remplie(monde, demandeur, refus, prix=0):
    """Une prestation accomplie depuis l'offre, pas une promesse ni une faim devinée."""
    terme = refus["contre_offre"]["condition"]
    if terme["type"] == "pieces":
        return prix >= terme["montant"]
    return refus.get("condition_tenue", False)


def demander(monde, demandeur, auditeur, objet, foyer=None, prix=0, remettre_part=False):
    """« absent », « mefiance », « qui_va_la », « necessaire », « impossible », « pauvre »,
    « refus », « remis », « rendu », « promis » ou « vendu ».

    ``prix`` : les pièces offertes. Au moins le prix (``biens.prix``) au propriétaire, c'est un
    achat : accepté sans se faire prier, payé aussitôt. Moins, c'est une demande, que le prix non
    payé rend plus dure à qui une pièce compte (``biens.reticence``). Une voix qu'il ne sait à qui
    prêter s'entend d'abord demander qui va là, qu'elle offre de payer ou réclame son bien."""
    from .biens import prix as prix_de, reticence, richesse
    from .deliberation import besoin_de_part
    from .planification import devis_pulsion
    from .spatial import porte_par
    from .vol import proprietaire
    retenue = offre_retenue(monde, demandeur, auditeur, objet) if demandeur != "joueur" else None
    accord = bool(retenue and condition_remplie(monde, demandeur, retenue, prix))
    if accord and retenue["contre_offre"]["condition"]["type"] == "tache":
        # Le plan qui motivait la réserve est désormais caduc, après prestation réelle.
        intention = lire(monde, auditeur)["intention"]
        if intention and intention["motif"] == "faim":
            esprit(monde, auditeur)["intention"] = None
    part = demande_de_part(monde, demandeur, auditeur, objet)
    if objet not in monde.objets or not (part or porte_par(monde, objet, auditeur)
                                         or differee(monde, auditeur, objet, prix)):
        return "absent"
    arret = None if accord else accueil(monde, demandeur, auditeur)
    if arret == "qui_va_la":
        return arret
    o = monde.objets[objet]
    if not part and proprietaire(monde, o) == demandeur:
        # Son propriétaire le redemande : il le lui rend, sauf s'il s'en sert encore. Garder un prêt
        # échu qu'on lui réclame lui coûte la confiance du prêteur (``biens.pret_garde``).
        if necessaire(monde, auditeur, objet):
            from .biens import echu, pret_garde
            if demandeur != "joueur" and echu(monde, objet):
                pret_garde(monde, demandeur, auditeur, objet, [])
            return "necessaire"
        remettre(monde, auditeur, demandeur, objet, demande=True)
        return "rendu"
    if arret:
        return arret
    if prix and richesse(monde, demandeur) < prix:
        return "pauvre"
    # Avant de promettre un service, il compte ce qu'il porte et ses biens à portée,
    # comme lorsqu'on lui demande quelles ressources il possède.
    siens_a_portee(monde, auditeur)
    prix_ = prix_de(monde, objet, part)
    vente = (bool(prix_) and prix >= prix_ or accord and prix > 0) and proprietaire(monde, o) == auditeur
    # Ce qu'il perd à donner sans être payé : ce qui se consomme. Un objet qui dure, il le prête, et
    # le récupérera.
    perdu = part or besoin_de_part(o) is not None
    dd = PARTAGE - penchant(monde, auditeur, "altruisme") + (reticence(monde, auditeur, prix_, prix) if perdu else 0)
    if part:
        if garde(monde, auditeur, o):
            return "necessaire"
        source = foyer_de(monde, auditeur, demandeur, foyer, objet)
        if foyer is not None and source is None:
            return "impossible"  # La cible nommée n'est jamais remplacée par un autre feu.
        if remettre_part:
            return _remettre_part(monde, auditeur, demandeur, objet, prix if vente else 0,
                                  None if vente or accord else dd)
        if besoin_de_part(o) == "faim":
            condition = {"objet": objet, "servir": demandeur}
        elif vente and foyer is None or source is None:
            # La part est remise pour les gestes du demandeur, quelle que soit la substance.
            # Sans source compatible, on ne promet jamais d'entretenir un feu avec ce qui n'y brûle pas.
            return _remettre_part(monde, auditeur, demandeur, objet, prix if vente else 0,
                                  None if vente or accord else dd)
        else:
            condition = {"objet": source, "allume": True}
        engagements = agendas.en_cours(monde, auditeur)
        paye = False
        if not any(x["condition"] == condition and not x.get("annule") for x in engagements):
            engagement = {"condition": condition, "pour": demandeur, "minute": monde.data["minutes"],
                          "objet": objet,
                          **({"paye": {"objet": objet, "prix": prix, "quoi": "part"}} if vente else {})}
            agendas.prendre(monde, auditeur, engagement)
            if devis_pulsion(monde, auditeur, condition, demandeur) is None:
                agendas.retirer_proposition(monde, auditeur, engagement)
                return "impossible"
            if not vente and not accord and not jet_persuasion(monde, auditeur, demandeur, dd)[0]:
                agendas.retirer_proposition(monde, auditeur, engagement)
                return "refus"
            # Payée d'avance, la part est due : non servie à l'échéance, le prix est rendu ou dû
            # (``engagements_echus``).
            memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": condition})
            if vente:
                _vendre(monde, auditeur, demandeur, objet, prix)
                paye = True
        if demandeur != "joueur":
            memoriser(monde, demandeur, {"type": "promis", "de": auditeur, "objet": objet,
                                         **({"foyer": condition["objet"]} if "allume" in condition else {})})
        return "vendu" if paye else "promis"
    if not porte_par(monde, objet, auditeur):
        # Un objet à lui qu'il ne porte pas, acheté à son prix : il s'engage à l'aller chercher et à le
        # remettre ; payé d'avance, non remis à l'échéance, le prix est dû (``engagements_echus``).
        if necessaire(monde, auditeur, objet) or garde(monde, auditeur, o):
            return "necessaire"
        condition = {"objet": objet, "remettre": demandeur}
        engagements = agendas.en_cours(monde, auditeur)
        if any(x["condition"] == condition and not x.get("annule") for x in engagements):
            return "promis"
        engagement = {"condition": condition, "pour": demandeur, "minute": monde.data["minutes"],
                      "paye": {"objet": objet, "prix": prix, "quoi": "objet"}}
        agendas.prendre(monde, auditeur, engagement)
        if devis_pulsion(monde, auditeur, condition, demandeur) is None:
            agendas.retirer_proposition(monde, auditeur, engagement)
            return "impossible"
        memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": condition})
        _vendre(monde, auditeur, demandeur, objet, prix)
        return "vendu"
    # Prêter ce qui se consomme, c'est en donner les parts : il n'en prête pas ce qu'il garde.
    if necessaire(monde, auditeur, objet) or garde(monde, auditeur, o):
        return "necessaire"
    if not vente and not accord and not jet_persuasion(monde, auditeur, demandeur, dd)[0]:
        return "refus"
    if vente:
        from .biens import donner
        _vendre(monde, auditeur, demandeur, objet, prix)
        donner(monde, objet, demandeur)
    remettre(monde, auditeur, demandeur, objet, demande=True, achat=vente)
    return "vendu" if vente else "remis"


def detacher_part(monde, lot):
    """Une part d'une réserve comptée devient un objet, à sa place : une pièce du lot s'il la décrit
    (``matiere.prelever_piece``), sinon une réserve d'une charge, du même nom ; la réserve diminue
    d'autant. Renvoie son identifiant."""
    import copy
    from .matiere import id_piece, prelever_piece
    o = monde.objets[lot]
    piece = id_piece(monde, lot)
    if o.get("physique"):
        prelever_piece(monde, lot, piece)
        return piece
    part = copy.deepcopy(o)
    compteur = "portions" if o["type"] == "nourriture" else "charges"
    part.update(id=piece, masse=round(o["masse"] / max(1, o[compteur]), 3))
    part[compteur] = 1
    o[compteur] -= 1
    o["masse"] = round(o["masse"] - part["masse"], 3)
    monde.objets[piece] = part
    return piece


def _remettre_part(monde, vendeur, acheteur, lot, prix, persuasion=None):
    """Détacher et remettre une part, donnée ou vendue : les mêmes moyens et le même engagement
    de livraison. Impossible ou refusée, rien n'est prélevé ; payée, elle est remboursable comme
    tout objet vendu d'avance. Le demandeur garde l'identité de la part qu'il attend."""
    from .planification import devis_pulsion
    from .spatial import porte_par
    import copy
    # Une parole encore due ne prélève pas une deuxième part.
    for engagement in agendas.en_cours(monde, vendeur):
        c = engagement["condition"]
        if c.get("remettre") == acheteur and engagement.get("lot") == lot:
            return "promis"
    avant = copy.deepcopy(monde.objets[lot])
    piece = detacher_part(monde, lot)
    o = monde.objets[piece]
    # Il sait où il la met de côté.
    salle = o["lieu"] if o["lieu"] in monde.data["salles"] else None
    croire(monde, vendeur, piece, "lieu", o["lieu"], "vu", salle=salle,
           case=list(o["position"]) if salle and o.get("position") else None)
    condition = {"objet": piece, "remettre": acheteur}
    engagement = {"condition": condition, "pour": acheteur, "minute": monde.data["minutes"], "lot": lot,
                  **({"paye": {"objet": piece, "prix": prix, "quoi": "objet"}} if prix else {})}
    agendas.prendre(monde, vendeur, engagement)
    possible = porte_par(monde, piece, vendeur) or devis_pulsion(monde, vendeur, condition, acheteur) is not None
    issue = "impossible" if not possible else (
        "refus" if persuasion is not None and not jet_persuasion(monde, vendeur, acheteur, persuasion)[0] else None)
    if issue:
        agendas.retirer_proposition(monde, vendeur, engagement)
        del monde.objets[piece]
        del esprit(monde, vendeur)["croyances"][piece]
        monde.objets[lot] = avant
        return issue
    if prix:
        _vendre(monde, vendeur, acheteur, piece, prix)
    if porte_par(monde, piece, vendeur):
        remettre(monde, vendeur, acheteur, piece, demande=True, achat=bool(prix))   # payée, ce n'est pas un don
        return "vendu" if prix else "remis"
    memoriser(monde, vendeur, {"type": "engagement_pris", "pour": acheteur, "condition": condition, "lot": lot})
    if acheteur != "joueur":
        memoriser(monde, acheteur, {"type": "promis", "de": vendeur, "objet": lot,
                                   "part": piece, "remise": True})
    return "vendu" if prix else "promis"


def differee(monde, auditeur, objet, prix):
    """Un objet à lui, qu'il ne porte pas, qu'on lui offre d'acheter à son prix (``biens.prix``) : il
    peut le vendre et aller le chercher pour le remettre. Ce qui se consomme se vend par parts."""
    from .biens import prix as prix_de
    from .deliberation import besoin_de_part
    from .vol import proprietaire
    o = monde.objets.get(objet)
    return bool(o and o.get("mobile") and besoin_de_part(o) is None and proprietaire(monde, o) == auditeur
                and prix_de(monde, objet) and prix >= prix_de(monde, objet))


# Les tâches qu'on peut payer quelqu'un de faire : ce que vise une pulsion qu'on rétablit soi-même
# d'ordinaire, et que le planificateur sait faire faire (``planification._engager``).
TACHES = ("allume", "verrouillee", "lieu")


def tache(condition):
    """La sorte de tâche qu'est cette condition, si on peut la payer (``TACHES``) ; None sinon."""
    return None if "periode" in condition else next((k for k in TACHES if k in condition), None)


def engager(monde, payeur, autre, condition, prix):
    """« mefiance », « qui_va_la », « deja », « pauvre », « impossible », « necessaire », « cher » ou
    « accepte ».

    ``payeur`` offre ``prix`` pièces pour qu'``autre`` fasse en sorte que ``condition`` soit vraie
    (un feu entretenu, un bien sous clé, un objet remis en place). Il accepte si ces pièces valent pour
    lui (``caractere.valeur_pieces``) au moins ce que la tâche lui coûte (son plan, comme s'il l'avait
    prise : ``planification.devis_pulsion``), sans jet, s'il n'y emploie pas ce qu'il garde (``garde``) : c'est un marché. Acceptée, elle devient son
    engagement, payé d'avance ; sur un bien du payeur, elle lui en confie la garde (``biens.gardes``).
    Non faite à l'échéance, le prix est dû (``engagements_echus``, ``biens.rembourser``)."""
    from .biens import payer, richesse
    from .caractere import valeur_pieces
    from .deliberation import illicite
    if payeur != "joueur" and condition["objet"] in monde.objets and illicite(monde, payeur, condition["objet"]):
        return "impossible"   # On ne fait pas faire à un autre ce qui serait, pour soi, une faute.
    arret = accueil(monde, payeur, autre)
    if arret:
        return arret
    # Celui qui le paie sait la tâche à faire : seul ce qu'il voit à l'instant la lui dit faite.
    if tenu(monde, autre, condition, monde.data["minutes"]):
        return "deja"
    if prix <= 0 or richesse(monde, payeur) < prix:
        return "pauvre"
    siens_a_portee(monde, autre)
    engagements = agendas.en_cours(monde, autre)
    if any(x["condition"] == condition and not x.get("annule") for x in engagements):
        return "deja"
    engagement = {"condition": dict(condition), "pour": payeur, "minute": monde.data["minutes"],
                  "paye": {"objet": condition.get("objet") or condition["lieu"], "prix": prix, "quoi": "tache"}}
    agendas.prendre(monde, autre, engagement)
    devis = devis_service(monde, autre, condition, payeur)
    if devis is None:
        agendas.retirer_proposition(monde, autre, engagement)
        return "impossible"  # Il ne voit pas comment s'y prendre avec ce qu'il sait.
    cout, etapes = devis
    # Ce qu'il garde (sa dernière part, ce dont il a besoin), il ne le donne pas, payé ou non.
    if any(monde.objets.get(x) and garde(monde, autre, monde.objets[x])
           for e in etapes if e["operation"] in ("alimenter", "manger", "servir") for x in (e["cible"], e["outil"])):
        agendas.retirer_proposition(monde, autre, engagement)
        return "necessaire"
    if valeur_pieces(monde, autre, prix) < cout:
        agendas.retirer_proposition(monde, autre, engagement)
        return "cher"
    payer(monde, payeur, autre, prix)
    memoriser(monde, autre, {"type": "engagement_pris", "pour": payeur, "condition": dict(condition), "prix": prix})
    if payeur != "joueur":
        memoriser(monde, payeur, {"type": "tache_payee", "a": autre, "condition": dict(condition), "prix": prix})
    return "accepte"


def siens_a_portee(monde, id):
    """Il sait ce qu'il porte et ce qui est à lui à portée de main (dans sa salle, hors de tout contenant
    fermé), même sans l'avoir regardé : il le constate (lieu et état). Renvoie ces objets."""
    from .spatial import porte_par
    from .vol import proprietaire
    salle = monde.objets[id]["lieu"]
    siens = []
    for k, o in monde.objets.items():
        if o["type"] == "personnage" or proprietaire(monde, o) != id:
            continue
        lieu, vus = o["lieu"], set()
        while lieu in monde.objets and lieu not in vus and monde.objets[lieu]["type"] == "contenant"                 and monde.objets[lieu].get("ouverte", True) is not False:
            vus.add(lieu)
            lieu = monde.objets[lieu]["lieu"]
        if not (porte_par(monde, k, id) or lieu == salle):
            continue
        ici = o["lieu"] in monde.data["salles"]
        croire(monde, id, k, "lieu", o["lieu"], "vu", salle=o["lieu"] if ici else None,
               case=list(o["position"]) if ici and o.get("position") else None)
        constater(monde, id, k, "vu")
        siens.append(k)
    return siens


def correspond_ressource(o, sujet):
    """Un bien nommé : correspondance lexicale aux données, sans synonymes inventés.

    Le nom peut être une expression entière à l'intérieur d'un nom composé.
    La matière et les catégories sont explicites ; aucune capacité n'est déduite.
    """
    from .monde import normaliser
    mots = lambda s: normaliser(s).replace("_", " ").replace("'", " ").split()
    demande = mots(sujet)
    for nom in (o["id"], o["nom"], *o.get("aliases", []), o.get("materiau", ""),
                o.get("type", ""), o.get("ressource", "")):
        termes = mots(nom)
        if demande and any(termes[i:i + len(demande)] == demande for i in range(len(termes))):
            return True
    return False


def enqueter(monde, demandeur, auditeur, besoin):
    """(« mefiance », « qui_va_la », « rien » ou « dit », ce qui a été dit) : ``demandeur`` demande à
    ``auditeur`` s'il a de quoi apaiser ``besoin`` (« As-tu des vivres ? », « du bois ? ») sans rien
    connaître de ce qu'il a. Le sujet peut aussi nommer un bien (nom, alias, matière ou catégorie).
    Il répond selon ses possessions connues ; pour un besoin général, ses ressources comptées pour ce
    besoin (``deliberation.besoin_de_part``) qu'il croit avoir encore, et où il les croit ; ce qu'il
    porte et ce qui est à lui à portée de main, il le sait (``siens_a_portee``). Le
    demandeur l'apprend, par ouï-dire, et rien de plus : [(objet, lieu cru)]."""
    from .deliberation import _connus, _disponible_cru, _lieu_cru, part_pour, parts
    from .paroles import BESOINS_DEMANDES
    from .spatial import porte_par
    from .vol import proprietaire
    from .deliberation import oublier_refus, retenir_refus
    arret = accueil(monde, demandeur, auditeur)
    if not arret:
        siens_a_portee(monde, auditeur)
    if arret:
        if demandeur != "joueur" and arret != "qui_va_la":
            # Refusé, il ne lui redemande pas de sitôt (``planification.s_enquerir``) ; à « Qui va
            # là ? », il se nomme et redemande.
            memoriser(monde, demandeur, {"type": "enquete", "de": auditeur, "besoin": besoin, "objets": []})
            retenir_refus(monde, demandeur, auditeur, "enqueter", arret, besoin=besoin, souvenir=False)
        return arret, []
    connus = _connus(monde, auditeur)
    dit = [(k, auditeur if porte_par(monde, k, auditeur) else _lieu_cru(monde, auditeur, k))
           for k in connus if k in monde.objets and monde.objets[k]["type"] != "personnage"
           and (part_pour(monde, auditeur, k, besoin, connus) if besoin in BESOINS_DEMANDES
                else correspond_ressource(monde.objets[k], besoin))
           and proprietaire(monde, monde.objets[k]) == auditeur
           and (besoin not in BESOINS_DEMANDES or parts(monde.objets[k]) > 0)
           and _disponible_cru(monde, auditeur, k)]
    dit = [(k, lieu) for k, lieu in dit if lieu is not None]
    if demandeur != "joueur":
        from .voix import source_dite
        source = source_dite(monde, demandeur, auditeur)
        for k, lieu in dit:
            salle = lieu if lieu in monde.data["salles"] else None
            croire(monde, demandeur, k, "lieu", lieu, source, round(0.7 * clarte(monde, demandeur), 2),
                   salle=salle, case=None)
        memoriser(monde, demandeur, {"type": "enquete", "de": auditeur, "besoin": besoin,
                                     "objets": [k for k, _ in dit]})
        # « Je n'en ai pas » se retient tant que rien de ce qu'il croit de ces ressources n'a changé ;
        # ce qu'il a dit avoir, il le sait désormais.
        if dit:
            oublier_refus(monde, demandeur, auditeur, "enqueter", besoin=besoin)
        else:
            retenir_refus(monde, demandeur, auditeur, "enqueter", "rien", besoin=besoin, souvenir=False)
    return ("dit" if dit else "rien"), dit


def demander_feu(monde, demandeur, auditeur, flamme, source):
    """« absent », « mefiance », « qui_va_la », « eteinte », « impossible » ou « allume ». Le
    demandeur tend sa source ; l'auditeur l'allume à la flamme qu'il porte. Cela ne lui ôte rien,
    ni prêt ni part : il le fait sans se faire prier, sauf s'il se méfie de lui ou ne sait qui
    lui parle (``accueil``)."""
    from .eau import sous_l_eau
    from .perception import flamme as donne_feu
    from .spatial import porte_par
    if flamme not in monde.objets or not porte_par(monde, flamme, auditeur):
        return "absent"
    arret = accueil(monde, demandeur, auditeur)
    if arret:
        return arret
    if not donne_feu(monde.objets[flamme]):
        return "eteinte"
    s = monde.objets.get(source)
    if (s is None or not porte_par(monde, source, demandeur) or s.get("allume") is not False
            or s.get("integrite", 1) == 0 or s.get("combustible", 0) <= 0 or sous_l_eau(monde, s)):
        return "impossible"
    s["allume"] = True
    return "allume"


def _vendre(monde, vendeur, acheteur, objet, prix):
    """L'acheteur paie ; chacun se souvient de la vente."""
    from .biens import payer
    payer(monde, acheteur, vendeur, prix)
    memoriser(monde, vendeur, {"type": "vente", "objet": objet, "a": acheteur, "prix": prix})
    if acheteur != "joueur":
        memoriser(monde, acheteur, {"type": "achat", "objet": objet, "de": vendeur, "prix": prix})


def tenu(monde, id, condition, depuis=None):
    """Ce qu'une parole demande est-il fait, à ses yeux ? Une parole donnée à la minute ``depuis``
    n'est tenue que sur ce qu'il a constaté depuis : un feu vu vif avant qu'on lui demande d'y
    mettre du bois n'est pas un feu entretenu. Une part à servir ne l'est qu'au geste qui la sert
    (``servir`` solde l'engagement), quoi qu'il croie de la faim de l'autre."""
    from .deliberation import satisfaite
    if "rendre" in condition:
        return satisfaite(monde, id, condition)  # Le prêt est clos : il le sait de sa main.
    if "servir" in condition or "remettre" in condition or not satisfaite(monde, id, condition):
        return False
    # Les croyances sont datées à la minute : dans la minute même de la parole, rien ne dit qu'il a vu
    # après l'avoir donnée (il choisit désormais entre deux minutes, ``deliberation.choisir``).
    nouvelles = lire(monde, id)["croyances"].get(condition.get("objet"), {}).values()
    return depuis is None or any(c["minute"] > depuis for c in nouvelles)


def confier(monde, demandeur, auditeur, condition):
    """« mefiance », « qui_va_la », « deja », « impossible », « refus » ou « accepte »."""
    arret = accueil(monde, demandeur, auditeur)
    if arret:
        return arret
    if tenu(monde, auditeur, condition):
        return "deja"
    siens_a_portee(monde, auditeur)
    # Une tâche sur un bien de celui qui la confie en confie la garde (``biens.gardes``) : il juge
    # s'il peut s'y prendre avec ce que la garde lui permet.
    engagement = {"condition": dict(condition), "pour": demandeur, "minute": monde.data["minutes"]}
    agendas.prendre(monde, auditeur, engagement)
    devis = devis_service(monde, auditeur, condition, demandeur)
    if devis is None:
        agendas.retirer_proposition(monde, auditeur, engagement)
        return "impossible"  # Il ne voit pas comment s'y prendre avec ce qu'il sait.
    if not jet_persuasion(monde, auditeur, demandeur,
                          TACHE - penchant(monde, auditeur, "altruisme") + devis[0] / PAS_PROPOSITION)[0]:
        agendas.retirer_proposition(monde, auditeur, engagement)
        return "refus"
    memoriser(monde, auditeur, {"type": "engagement_pris", "pour": demandeur, "condition": dict(condition)})
    if demandeur != "joueur" and "objet" in condition:
        esprit(monde, demandeur)["aides_attendues"][condition["objet"]] = {
            "qui": auditeur, "condition": dict(condition), "minute": monde.data["minutes"]}
    return "accepte"


def remettre(monde, donneur, receveur, objet, demande=False, achat=False):
    """Remis par son propriétaire, un objet qui dure est prêté, ce qui se consomme est donné ;
    remis à son propriétaire, il lui est rendu (``deplacer`` clôt le prêt) ; remis par un autre,
    il change seulement de mains."""
    from .biens import donner, preter
    from .deliberation import besoin_de_part
    from .deplacement_objet import deplacer
    from .vol import proprietaire
    from .services import don_utile
    utile = don_utile(monde, receveur, objet)
    o = monde.objets[objet]
    e = esprit(monde, donneur) if (monde.objets.get(donneur) or {}).get("profil") else None
    livre = [x for x in (agendas.en_cours(monde, donneur) if e else []) if x["condition"] == {"objet": objet, "remettre": receveur}]
    tenus = list(livre)
    if livre and proprietaire(monde, o) == donneur:
        # Ce qu'il a vendu et vient remettre : l'objet passe à l'acheteur, la parole est tenue.
        donner(monde, objet, receveur)
        tenus = livre
    elif proprietaire(monde, o) == donneur:
        if besoin_de_part(o):
            donner(monde, objet, receveur)
            memoriser(monde, donneur, {"type": "don", "objet": objet, "a": receveur})
        else:
            # Un bien sans propriétaire déclaré est à qui le porte : prêté, il reste au prêteur.
            o["proprietaire"] = donneur
            preter(monde, objet, receveur)
            memoriser(monde, donneur, {"type": "pret", "objet": objet, "a": receveur})
    permission = next((p for p in monde.data.get("permissions", []) if p["objet"] == objet), None)
    restitution = bool(permission and permission["de"] == receveur and permission["a"] == donneur)
    ponctuel = restitution and monde.data["minutes"] - permission["minute"] <= 240
    deplacer(monde, objet, receveur)
    if livre and 'lot' in livre[0]:
        agendas.affecter_part(monde, receveur, livre[0]['lot'], objet)
    from .biens import compte, noter_compte
    noter_compte(monde, compte(donneur, receveur, objet, 1, "rendu"))
    if receveur != "joueur":
        memoriser(monde, receveur, {"type": "restitution" if restitution else "recu", "objet": objet, "de": donneur,
                                     "pret": any(p["objet"] == objet and p["a"] == receveur for p in monde.data.get("permissions", [])),
                                     "livraison": bool(livre) or achat, "demande": demande, "ponctuel": ponctuel,
                                     "service_utile": utile,
                                     **({"lot": livre[0]["lot"]} if livre and "lot" in livre[0] else {})})
    # La conséquence s'apprend par la réception déjà inscrite, comme pour une part servie.
    # Une réussite sans réception reste une suite à annoncer (relations.souvenir).
    for x in tenus:
        agendas.tenir(monde, donneur, x)
        memoriser(monde, donneur, {"type": "engagement_tenu", "pour": receveur, "condition": x["condition"],
                                   **({"lot": x["lot"]} if "lot" in x else {})})


def servir(monde, id, nourriture, pour, lignes):
    """Donner une part à quelqu'un de la même salle, qu'on appelle s'il est hors de vue : il la
    mange, et sait gré de l'avoir reçue. Il faut pouvoir se parler (``pnj.peuvent_se_parler`` :
    s'entendre et savoir qui parle), comme pour tout échange."""
    from .deliberation import SATIETE
    from .esprits import percoit
    from .francais import complement_de
    from .pnj import _chroniquer, peuvent_se_parler
    from .social import _qui, faire_entendre
    o, autre = monde.objets[nourriture], monde.objets.get(pour)
    if pour == "joueur":
        return _servir_joueur(monde, id, nourriture, lignes)
    if (o.get("portions", 0) <= 0 or not autre or autre["type"] != "personnage"
            or autre["lieu"] != monde.objets[id]["lieu"] or not peuvent_se_parler(monde, id, pour)):
        return False
    appel = "" if percoit(monde, id, pour) and percoit(monde, pour, id) else f"appelle {_qui(monde, pour)} et lui "
    from .services import don_utile
    utile = don_utile(monde, pour, nourriture)
    o["portions"] -= 1
    besoins = esprit(monde, pour)["besoins"]
    if "faim" in besoins:
        besoins["faim"] = max(0.0, besoins["faim"] - SATIETE)
    memoriser(monde, pour, {"type": "nourri", "de": id, "objet": nourriture, "service_utile": utile})
    for refus in lire(monde, id)["refus"]:
        offre = refus.get("contre_offre")
        if offre and offre["debiteur"] == pour and offre["condition"] == {
                "type": "tache", "condition": {"objet": nourriture, "servir": pour}}:
            refus["condition_tenue"] = True
    constater(monde, id, pour, "vu")  # Il le voit manger : il sait sa faim apaisée, même dans le noir.
    e = esprit(monde, id)
    tenus = [x for x in agendas.en_cours(monde, id) if x["condition"] == {"objet": nourriture, "servir": pour}]
    for x in tenus:
        agendas.tenir(monde, id, x)
        memoriser(monde, id, {"type": "engagement_tenu", "pour": pour, "condition": x["condition"]})
    texte = (f"{_qui(monde, id)} {appel}donne une part {complement_de(o)}"
             + ("." if appel else f" à {_qui(monde, pour)}."))
    _chroniquer(monde, id, texte, "social")
    faire_entendre(monde, id, pour, texte, [nourriture], lignes)
    return True


def _servir_joueur(monde, id, nourriture, lignes):
    """La part promise au joueur : servie quand il est là, dans la salle des vivres, et qu'ils
    peuvent se parler (``pnj.peuvent_se_parler``) ; sinon on l'attend."""
    from .corps import SATIETE, valeurs
    from .francais import complement_de
    from .pnj import _chroniquer, peuvent_se_parler
    from .social import _qui
    o = monde.objets[nourriture]
    if (o.get("portions", 0) <= 0 or monde.joueur["salle"] != monde.objets[id]["lieu"]
            or not peuvent_se_parler(monde, id, "joueur")):
        return False
    o["portions"] -= 1
    v = valeurs(monde, "joueur")
    v["faim"] = max(0.0, v["faim"] - SATIETE)
    constater(monde, id, "joueur", "vu")
    e = esprit(monde, id)
    for x in [x for x in agendas.en_cours(monde, id) if x["condition"] == {"objet": nourriture, "servir": "joueur"}]:
        agendas.tenir(monde, id, x)
        memoriser(monde, id, {"type": "engagement_tenu", "pour": "joueur", "condition": x["condition"]})
    _chroniquer(monde, id, f"{_qui(monde, id)} donne une part {complement_de(o)} au joueur.", "social")
    from .voix import personne_pour_joueur
    lignes.append(f"{personne_pour_joueur(monde, id, court=True)[0]} te sert une part {complement_de(o)} ; tu manges.")
    return True


RESSOURCES = {"faim": "de quoi manger", "chaleur": "du bois"}   # ce qu'on demande sans le connaître


def _il(o):
    return "elle" if o.get("genre") == "f" else "il"


def _si_il(o):
    return "si elle" if o.get("genre") == "f" else "s'il"


def _ou_dit(monde, lieu):
    """Où il dit avoir sa ressource : « dans la réserve », « sur lui »."""
    from .francais import designer, lieu as designer_lieu
    if lieu in monde.data["salles"]:
        return " dans " + designer_lieu(monde.data["salles"][lieu])
    if lieu in monde.objets and monde.objets[lieu]["type"] == "personnage":
        return " sur lui"
    return " dans " + designer(monde.objets[lieu]) if lieu in monde.objets else ""


def _avec_joueur(monde, id, etape, lignes):
    """Un geste social d'un PNJ vers le joueur : lui remettre un objet (vendu, prêté, rendu), ou lui
    redemander ce qu'il lui a prêté. Il faut le savoir là et pouvoir se parler, comme avec un PNJ.
    Le joueur n'a pas d'esprit : redemandé, il rend l'objet ou le garde à son gré ; le PNJ s'en
    souvient (``pret_reclame``), et un prêt échu qu'il ne lui rend pas lui coûte sa confiance
    (``biens.prets_reclames``). Renvoie True si le PNJ a obtenu ce qu'il visait."""
    from .biens import echu, pret
    from .francais import accorder, designer
    from .ouie import retentir
    from .pnj import _chroniquer, _rate, se_parler
    from .social import _qui
    from .spatial import porte_par
    from .voix import personne_pour_joueur
    op = etape["operation"]
    if op == "dire" and "annulation" in etape.get("contenu", {}):
        return annoncer_abandon(monde, id, "joueur", etape["contenu"]["annulation"], lignes)
    objet = monde.objets.get(etape["outil"])
    if objet is None or op not in ("remettre", "demander"):
        return False
    if monde.joueur["salle"] != monde.objets[id]["lieu"]:
        return _rate(monde, id, "joueur")   # Il ne le trouve pas là où il le croyait.
    if not se_parler(monde, id, "joueur"):
        return False
    nom = personne_pour_joueur(monde, id, court=True)[0]
    if op == "remettre":
        if not porte_par(monde, objet["id"], id):
            return False
        vendu = any(x["condition"] == {"objet": objet["id"], "remettre": "joueur"} and x.get("paye")
                    for x in agendas.en_cours(monde, id))
        remettre(monde, id, "joueur", objet["id"])
        _chroniquer(monde, id, f"{_qui(monde, id)} remet {designer(objet)} au joueur.", "social")
        lignes.append(f"{nom} te remet {designer(objet)}" + (" : tu l'avais payé." if vendu else "."))
        retentir(monde, id, "dire", texte=f"{_qui(monde, id)} remet {designer(objet)} à {_qui(monde, 'joueur', id)}.",
                 cites=["joueur", objet["id"]], vers=["joueur"], appris=True)
        return True
    p = pret(monde, objet["id"])
    if not p or p["de"] != id or p["a"] != "joueur" or not porte_par(monde, objet["id"], "joueur"):
        return False
    texte = f"{_qui(monde, id)} demande à {_qui(monde, 'joueur', id)} de lui rendre {designer(objet)}."
    _chroniquer(monde, id, texte, "social")
    lignes.append(f"{nom} te demande de lui rendre {designer(objet)}"
                  + (f" : {_il(monde.objets[id])} te l'a {accorder(objet, 'prêté')} il y a longtemps."
                     if echu(monde, objet["id"]) else "."))
    retentir(monde, id, "dire", texte=texte, cites=["joueur", objet["id"]], vers=["joueur"], appris=True)
    memoriser(monde, id, {"type": "pret_reclame", "objet": objet["id"], "a": "joueur", "pret": p["minute"],
                          "echu": echu(monde, objet["id"])})
    # La réponse est au joueur : il ne le redemande pas de sitôt (``deliberation.tient``).
    from .deliberation import retenir_refus
    retenir_refus(monde, id, "joueur", "demander", "attente", objet=objet["id"])
    return False


def phrase_condition(monde, condition):
    from .francais import accorder, designer, lieu
    x = monde.objets[condition["objet"]]
    o = designer(x)
    verbe = "soient" if nombre_pluriel(x) else "soit"
    if "servir" in condition:
        from .social import _qui
        from .francais import complement_de
        return f"une part {complement_de(x)} soit servie à {_qui(monde, condition['servir'])}"
    if "remettre" in condition:
        from .social import _qui
        return f"{o} {verbe} {accorder(x, 'remis')} à {_qui(monde, condition['remettre'])}"
    if "lieu" in condition:
        return f"{o} {verbe} dans {lieu(monde.data['salles'][condition['lieu']])}"
    return f"{o} {verbe} {accorder(x, 'allumé' if 'allume' in condition else 'verrouillé')}"


def phrase_affirmee(monde, sujet, attribut, valeur, pour_joueur):
    """Ce qui est affirmé, vu du joueur (« tu es ») ou de la chronique (« Corvus est »)."""
    texte = _phrase(monde, sujet, attribut, valeur)
    if sujet == "joueur" and texte.startswith("toi est"):
        texte = ("tu es" if pour_joueur else monde.joueur["nom"] + " est") + texte[len("toi est"):]
    if not pour_joueur:
        texte = texte.replace("porté par toi", "porté par " + monde.joueur["nom"])
    return texte


def annoncer_abandon(monde, id, autre, condition, lignes):
    """Un abandon gratuit s'annonce en retrouvant son destinataire ; aucun savoir à distance."""
    from .pnj import _chroniquer, se_parler
    from .social import _qui, faire_entendre
    from .ouie import retentir
    if not se_parler(monde, id, autre):
        return False
    engagements = agendas.en_cours(monde, id)
    engagement = next((x for x in engagements if x.get("annule") and x["pour"] == autre
                       and x["condition"] == condition), None)
    if engagement is None:
        return False
    agendas.annoncer_abandon(monde, id, engagement)
    from .recit_pnj import but_en_mots
    il = _il(monde.objets[id])
    promis = but_en_mots(monde, {"type": "pulsion", **condition})
    impossible = engagement["annule"] == "impossible"
    suite = "ne peut plus tenir sa promesse" if impossible else "renonce à sa promesse"
    texte = f"{_qui(monde, id)} prévient {_qui(monde, autre)} qu'{il} {suite} : {promis}."
    memoriser(monde, id, {"type": "abandon_annonce", "pour": autre, "condition": condition})
    if autre != "joueur":
        retenir_abandon(monde, id, engagement)
        faire_entendre(monde, id, autre, texte, [condition["objet"]], lignes)
    else:
        retentir(monde, id, "dire", texte=texte, cites=["joueur", condition["objet"]], vers=["joueur"], appris=True)
        if monde.visible(id):
            from .voix import personne_pour_joueur
            annonce = "sa promesse est devenue impossible" if impossible else "sa promesse est abandonnée"
            lignes.append(f"{personne_pour_joueur(monde, id, court=True)[0]} te prévient : {annonce}.")
    _chroniquer(monde, id, texte, "social")
    return True


def retenir_abandon(monde, id, engagement, raison=None):
    """L'abandon reçu est aussi un refus du service, payé ou gratuit : le remboursement ne le lève pas."""
    from .deliberation import retenir_refus
    autre, condition = engagement["pour"], engagement["condition"]
    if autre == "joueur":
        return
    paye = engagement.get("paye") or {}
    # Une part à remettre a été promise sous le nom de son lot (``_remettre_part``).
    objet = engagement.get("objet") or engagement.get("lot") or paye.get("objet") or condition["objet"]
    op = ("engager" if paye.get("quoi") == "tache" else "acheter" if paye else
          "demander" if "objet" in engagement else "confier")
    memoriser(monde, autre, {"type": "promesse_annulee", "de": id, "objet": objet})
    retenir_refus(monde, autre, id, op, raison or engagement.get("annule") or "impossible", objet=objet,
                  prix=paye.get("prix") if op == "engager" else None,
                  tache=tache(condition) if op in ("engager", "confier") else None)


def empeche(monde, id, engagement):
    """Une parole de service devenue impossible : le même devis autonome qu'à l'acceptation.

    Une vente garde aussi son bien et ses parts disponibles. Le prix devient dû ; une parole
    gratuite devient un abandon à annoncer (``engagements_echus``). Le prêt à rendre reste en
    suspens tant que l'emprunteur s'en sert : ce n'est pas un service qu'il ne peut plus livrer."""
    from .deliberation import parts
    from .vol import proprietaire
    paye = engagement.get("paye")
    if engagement.get("annule") or "rendre" in engagement["condition"] or "periode" in engagement["condition"]:
        return False
    if paye and paye["quoi"] != "tache":
        o = monde.objets.get(paye["objet"])
        if o is None or proprietaire(monde, o) != id or paye["quoi"] == "part" and parts(o) <= 0:
            return True
    return devis_service(monde, id, engagement["condition"], engagement["pour"]) is None


def engagements_echus(monde, id):
    """Compatibilité des appelants : le cycle des engagements appartient aux agendas."""
    agendas.echoir(monde, id)


def executer(monde, id, etape, lignes):
    """Un geste social d'une minute ; renvoie True s'il a obtenu ce qu'il visait."""
    from .francais import complement_de, designer, groupe_nominal
    from .pnj import _chroniquer
    from .esprits import percoit
    from .social import _qui, faire_entendre
    from .spatial import porte_par
    autre, op = etape["cible"], etape["operation"]
    o = monde.objets.get(autre)
    from .pnj import _rate, se_parler
    if autre == "joueur":
        return _avec_joueur(monde, id, etape, lignes)
    if not o or o["type"] != "personnage" or not o.get("profil"):
        return False
    if o["lieu"] != monde.objets[id]["lieu"]:
        # Personne ne lui répond là où il le croyait : il l'apprend, comme tout geste manqué.
        return _rate(monde, id, autre)
    if not se_parler(monde, id, autre):
        return False  # Ils ne peuvent ni se voir ni s'entendre : rien ne se dit.
    a, b, contenu = _qui(monde, id), _qui(monde, autre), etape.get("contenu", {})
    objet = monde.objets.get(etape["outil"])
    if op == "acheter" and objet:
        from .pnj_propositions import offre_refusee
        if offre_refusee(monde, id, autre, objet["id"],
                         {"type": "pieces", "montant": contenu.get("prix", 0)}):
            return False
    transmis = []  # Ce que la parole transmet à qui l'entend sans en être le destinataire.
    reponse, dite = "", True  # Ce que l'autre y répond, et s'il le dit de sa voix.
    if op == "dire" and "annulation" in contenu:
        return annoncer_abandon(monde, id, autre, contenu["annulation"], lignes)
    if op == "dire":
        from .social import deja_dit
        if deja_dit(monde, id, autre, {"type": "affirmation", **contenu}):
            return True  # Un ancien plan ne fait pas redire un fait appris entre-temps.
        issue = affirmer(monde, id, autre, contenu["sujet"], contenu["attribut"], contenu["valeur"])
        recit = f"{a} dit à {b} que {phrase_affirmee(monde, contenu['sujet'], contenu['attribut'], contenu['valeur'], False)}"
        clair = f"{a} dit à {b} que {phrase_affirmee(monde, contenu['sujet'], contenu['attribut'], contenu['valeur'], True)}."
        cites, reussi = [contenu["sujet"], contenu["valeur"] if isinstance(contenu["valeur"], str) else None], True
        transmis = [{"type": "affirmation", **{k: contenu[k] for k in ("sujet", "attribut", "valeur")}}]
        memoriser(monde, id, {"type": "dit", "a": autre, "sujet": contenu["sujet"], "attribut": contenu["attribut"],
                              "valeur": contenu["valeur"]})
    elif op == "proposer":
        from .pnj_propositions import executer
        return executer(monde, id, autre, contenu, lignes)
    elif op == "demander" and "ressource" in contenu:
        # « As-tu du bois ? » : il répond par ce qu'il a vraiment, et l'autre l'apprend.
        issue, dit = enqueter(monde, id, autre, contenu["ressource"])
        recit = f"{a} demande à {b} {_si_il(o)} a {RESSOURCES[contenu['ressource']]}"
        clair = recit + "."
        reponse = (f"{b} dit avoir " + " et ".join(designer(monde.objets[k]) + _ou_dit(monde, lieu) for k, lieu in dit)
                   + "." if dit else f"{b} dit n'en avoir pas." if issue == "rien" else f"{b} refuse de répondre.")
        cites = [k for k, _ in dit] + [lieu for _, lieu in dit]
        reussi = issue == "dit"
    elif op == "engager":
        condition, prix = contenu["condition"], contenu["prix"]
        issue = engager(monde, id, autre, condition, prix)
        recit = (f"{a} offre {quantite(prix, 'pièce')} à {b} pour qu'{_il(o)} fasse en sorte que "
                 f"{phrase_condition(monde, condition)}")
        clair = recit + "."
        reponse = f"{b} accepte et prend l'argent." if issue == "accepte" else f"{b} refuse."
        cites = [condition["objet"], condition.get("lieu")]
        reussi = issue == "accepte"
    elif op in ("demander", "acheter"):
        if objet is None:
            return False
        # La nature de la demande se juge avant l'échange : après un prêt, le demandeur porte l'objet.
        part = demande_de_part(monde, id, autre, objet["id"])
        prix = contenu.get("prix", 0) if op == "acheter" else 0
        issue = demander(monde, id, autre, objet["id"], contenu.get("foyer"), prix, contenu.get("remettre_part", False))
        quoi = "une part " + complement_de(objet) if part else designer(objet)
        recit = (f"{a} achète {quoi} à {b} pour {quantite(prix, 'pièce')}" if op == "acheter"
                 else f"{a} demande {quoi} à {b}")
        clair = recit + "."
        reponse = {"remis": f"{b} lui remet {quoi}.", "rendu": f"{b} lui rend {designer(objet)}.",
                   "vendu": f"{b} accepte et prend l'argent.",
                   "promis": f"{b} accepte de lui en donner."}.get(issue, f"{b} refuse.")
        dite = issue not in ("remis", "rendu")  # Remettre l'objet est un geste, pas une parole.
        cites, reussi = [objet["id"]], issue in ("remis", "rendu", "promis", "vendu")
    elif op == "demander_feu":
        source = monde.objets.get(contenu.get("allumer"))
        if objet is None or source is None:
            return False
        issue = demander_feu(monde, id, autre, objet["id"], source["id"])
        recit = f"{a} demande du feu à {b} pour {designer(source)}"
        clair = recit + "." + (f" {b} l'allume {groupe_nominal(designer(objet), 'à')}." if issue == "allume" else f" {b} refuse.")
        cites, reussi = [objet["id"], source["id"]], issue == "allume"
        if reussi:
            # Allumée dans sa main : il la ménagera quand elle ne lui servira plus (``menager_flamme``).
            memoriser(monde, id, {"type": "flamme_employee", "objet": source["id"]})
        elif issue == "absent":
            from .pnj import _rate
            _rate(monde, id, objet["id"])   # Il ne la porte pas : il l'apprend.
        if issue in ("allume", "eteinte", "impossible"):
            constater(monde, id, source["id"], "essai")
            if objet["id"] in monde.objets:
                constater(monde, id, objet["id"], "vu")
    elif op == "confier":
        issue = confier(monde, id, autre, contenu)
        for s in lire(monde, id)['recours_intermediaires']:
            if s['via'] == autre and s['objet'] == contenu['objet'] and s['issue'] == 'preparee':
                s['issue'] = issue
        recit = f"{a} demande à {b} de faire en sorte que {phrase_condition(monde, contenu)}"
        clair = recit + "."
        reponse = f"{b} accepte." if issue in ("accepte", "deja") else f"{b} refuse."
        cites = [contenu["objet"], contenu.get("lieu")]
        reussi = issue in ("accepte", "deja")
    else:
        if objet is None or not porte_par(monde, objet["id"], id):
            return False
        from .vol import proprietaire
        rendu = proprietaire(monde, objet) == autre
        remettre(monde, id, autre, objet["id"])
        issue, recit = ("rendu", f"{a} rend {designer(objet)} à {b}") if rendu else (
            "remis", f"{a} remet {designer(objet)} à {b}")
        clair, cites, reussi = recit + ".", [objet["id"]], True
    offre = None
    retenue = offre_retenue(monde, id, autre, objet["id"]) if op in ("demander", "acheter") and objet else None
    honoree = bool(reussi and retenue and condition_remplie(monde, id, retenue, contenu.get("prix", 0)))
    if op in ("demander", "acheter") and objet and not reussi and "ressource" not in contenu:
        from .deliberation import retenir_refus
        from .propositions import offre_en_mots, cites_terme
        offre = contre_offre(monde, id, autre, objet["id"], issue)
        if offre:
            # La condition existe avant que sa réponse soit entendue ou affichée.
            retenir_refus(monde, id, autre, op, issue, objet=objet["id"],
                          prix=contenu.get("prix"), contre_offre=offre)
            reponse += " " + offre_en_mots(monde, offre)
            cites += cites_terme(offre["condition"])
    detail = " ; contre-offre annoncée" if offre else " ; condition remplie" if honoree else ""
    _chroniquer(monde, id, f"{recit}{detail} ({issue}).", "social")
    nommes = [x for x in cites if x and (x in monde.objets or x in monde.data["salles"] or x == "joueur")]
    if issue == "qui_va_la":
        # Il ne sait à qui est cette voix : « Qui va là ? » ; l'autre se nomme (``voix.se_nommer``),
        # et redemandera.
        from .social import qui_va_la
        faire_entendre(monde, id, autre, clair, nommes, lignes, transmis)
        qui_va_la(monde, id, autre, lignes)
    else:
        faire_entendre(monde, id, autre, clair, nommes, lignes, transmis, reponse, dite)
    if "ressource" not in contenu:   # « As-tu… ? » retient sa réponse (``enqueter``).
        # Un feu refusé l'est pour cette source ; un objet demandé, pour cet objet ; une tâche, pour ce
        # qu'elle vise. Le refus se retient selon sa cause (``deliberation.retenir_refus``) ; accordée,
        # la demande n'a plus de refus qui tienne.
        from .deliberation import oublier_refus, retenir_refus
        vise = (contenu.get("allumer") if op == "demander_feu" else objet["id"] if objet
                else contenu["condition"]["objet"] if op == "engager" else contenu.get("objet"))
        if reussi:
            for x in (("demander", "acheter") if op in ("demander", "acheter") else (op,)):
                oublier_refus(monde, id, autre, x, vise)
        elif not offre:
            condition = contenu["condition"] if op == "engager" else contenu if op == "confier" else None
            retenir_refus(monde, id, autre, op, issue, objet=vise,
                          prix=contenu["prix"] if op in ("engager", "acheter") else None,
                          tache=tache(condition) if condition else None,
                          flamme=objet["id"] if op == "demander_feu" and objet else None)
    return reussi
