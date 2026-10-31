"""L'appel négocié : qui vient à qui (``docs/plan-ouie.md``, « L'appel négocié »).

Héler est un cri (``pnj.heler``, nature « hele ») ; l'appelé qui saisit son nom ne se contente plus de
dire « Ici ! » et d'attendre : appelé et appelant conviennent, par des paroles typées que le moteur
tranche, de qui vient à qui. Une seule règle pour les PNJ et pour le joueur.

- « J'arrive ! » (``ARRIVE``) : celui qui le dit vient à l'autre, qui l'attend ;
- « Ici, viens ! » (``VIENS``) : celui qui le dit reste où il est, l'autre vient ;
- « Qu'est-ce que tu veux ? » (``QUOI``) : l'appelé ne sait pourquoi on l'appelle et n'a pas de raison
  de bouger ; l'appelant dit ce qu'il veut (``raison_de`` : une demande, une offre, un avertissement,
  une tâche), et l'appelé décide de nouveau, sans redemander ;
- le silence : il se méfie de cette voix, ou ne veut pas se signaler (un geste qu'il veut sans témoin).

Ce que dit l'appelé se décide par ``decider`` : sur qui a besoin de qui (il cherche lui-même l'appelant,
on le prie de venir, la raison dite), qui peut bouger (un geste en cours sur place, une garde, ce qu'il
fait sur place, l'attente de quelqu'un d'autre, l'eau, un chemin qu'il croit coupé), et ce qui le presse
ailleurs. L'appelant qui entend « Ici, viens ! » répond « J'arrive ! » s'il peut venir.

Ce qui est convenu entre dans l'esprit des deux : qui reste attend (``rejoint`` : qui, jusqu'à quand, et
si l'autre a promis de venir), qui a dit « J'arrive ! » doit venir (``rejoindre`` : qui, où, jusqu'à
quand), une parole due qui passe après ce qui presse (``deliberation._candidats``). L'attente se règle
sur la distance (``delai`` : le temps de venir par le plus court chemin, plus une marge). Qui attend
quelqu'un qui a promis de venir ne le cherche plus : il l'attend (``deliberation._attendre_qui_vient``).
« J'arrive ! » est une parole donnée : qui l'attend en vain jusqu'à l'échéance le voit, et lui en tient
rigueur comme d'une autre parole non tenue (``relations``, cause « parole_rompue »).

Le joueur répond ou demande de même, sans le MJ (``paroles.reponse_a_l_appel``, ``sons``) ; les réponses
des PNJ lui parviennent par l'ouïe commune (``ecoute``).
"""
from . import memoire
import re

from .esprits import esprit, lire, memoriser

ARRIVE, VIENS, QUOI = "arrive", "viens", "quoi"
SORTES = (ARRIVE, VIENS, QUOI)
PHRASES = {ARRIVE: "J'arrive !", VIENS: "Ici, viens !", QUOI: "Qu'est-ce que tu veux ?"}
# Ce que l'appelant dit vouloir, à « Qu'est-ce que tu veux ? » : une sorte de contenu, sa phrase.
RAISONS = {"demande": "J'ai quelque chose à te demander.", "offre": "J'ai quelque chose pour toi.",
           "avertissement": "J'ai à te prévenir de quelque chose.", "tache": "J'ai une tâche pour toi.",
           "propos": "J'ai à te parler."}
# Les gestes d'un plan qui disent pourquoi il cherche quelqu'un.
GESTES_RAISON = {"demander": "demande", "acheter": "demande", "demander_feu": "demande", "engager": "tache",
                 "confier": "tache", "remettre": "offre", "servir": "offre", "dire": "avertissement"}
# Les gestes du joueur qui répondent : la méthode d'``emettre_son``, aussi l'effet du plan.
METHODES = {"repondre": VIENS, "arriver": ARRIVE, "demander_raison": QUOI}
MARGE = 2            # minutes ajoutées au temps de venir, plus la moitié de ce temps (``delai``)
OUVRIR = 20          # dixièmes de seconde : ouvrir une porte fermée en chemin (``delai``)
MOTS = re.compile(r"«\s*(.+?)\s*»")


# --- Ce que dit un cri ----------------------------------------------------------------------------

def sorte_du_cri(texte):
    """« appel » pour un nom hélé, la sorte d'une réponse (``SORTES``), « raison » pour ce que dit vouloir
    l'appelant, « ici » pour l'ancien « Ici ! » ; None pour un autre cri."""
    if " appelle : « " in texte:
        return "appel"
    mots = MOTS.search(texte)
    if not mots or " répond : « " not in texte:
        return None
    dits = mots.group(1)
    for sorte, phrase in PHRASES.items():
        if dits == phrase.rstrip(" !?").strip() or dits == phrase:
            return sorte
    if dits in RAISONS.values():
        return "raison"
    return "ici" if dits.startswith("Ici") else None


def texte(monde, qui, phrase):
    from .social import _qui
    return f"{_qui(monde, qui)} répond : « {phrase} »"


# --- Qui peut bouger, qui a besoin de qui --------------------------------------------------------

def se_cache(monde, qui):
    """Il ne veut pas se signaler : il prépare ou fait un geste qu'il veut sans témoin."""
    from .pnj import a_pas_feutres
    return a_pas_feutres(monde, qui) or any(g["auteur"] == qui for g in monde.data.get("gestes_en_cours", []))


def peut_venir(monde, qui, autre):
    """Il croit pouvoir aller là d'où vient la voix de ``autre`` : un chemin qu'il croit ouvert (ni porte
    qu'il sait verrouillée sans clé, ni salle noyée), et l'eau ne le met pas en péril là où il est."""
    from .eau import en_peril
    from .ouie import _place
    from .pnj import chemin
    if en_peril(monde, qui):
        return False
    ici, la = monde.objets[qui]["lieu"], _place(monde, autre)[0]
    return ici == la or la in monde.data["salles"] and chemin(monde, qui, ici, la) is not None


def retenu(monde, qui, autre):
    """Ce qui le tient là où il est : un geste en cours sur place (``passage.raison_de_rester``), une
    garde, ce qu'il fait sur place (assis, au feu, à l'abri), l'attente de quelqu'un d'autre, une
    promesse d'aller ailleurs."""
    from .deliberation import _sur_place
    from .passage import raison_de_rester
    e = lire(monde, qui)
    i = e["intention"]
    return bool(raison_de_rester(monde, qui) == "geste"
                or i and (i["but"]["type"] == "garder" or _sur_place(monde, qui, i))
                or e["rejoint"] and e["rejoint"]["qui"] != autre
                or e["rejoindre"] and e["rejoindre"]["qui"] != autre)


def _vise(intention, autre):
    return bool(intention) and (autre in intention["but"].values() or any(
        x.get("cible") == autre or (x.get("contenu") or {}).get("cherche") == autre for x in intention["plan"]))


def presse_ailleurs(monde, qui, autre):
    """Un besoin qui presse l'occupe, et son plan ne le mène pas à ``autre``."""
    from .deliberation import urgents
    i = lire(monde, qui)["intention"]
    return bool(i and i["plan"] and i["motif"] in urgents(monde, qui) and not _vise(i, autre))


def pressante(monde, qui, raison):
    """Une raison qui le fait venir lui-même : un avertissement (qui le regarde), une aide, ou la demande
    d'un objet qu'il a sur lui (il a de quoi y répondre)."""
    from .spatial import porte_par
    t = raison.get("type")
    return t in ("avertissement", "aide") or (
        t == "demande" and raison.get("objet") in monde.objets and porte_par(monde, raison["objet"], qui))


def decider(monde, qui, autre, raison=None, prie=False):
    """Ce que le PNJ ``qui`` répond à ``autre`` (un PNJ ou le joueur) qui l'a hélé, ou qui lui répond :
    None (le silence), ``ARRIVE``, ``VIENS`` ou ``QUOI``. ``raison`` : ce qu'``autre`` a dit vouloir ;
    ``prie`` : ``autre`` lui a dit « Ici, viens ! » (il ne viendra pas). Ni l'une ni l'autre : on ne
    redemande pas ce qu'il veut."""
    from .deliberation import cherche
    from .voix import repond
    if not repond(monde, qui, autre) or se_cache(monde, qui):
        return None
    # Une invitation à venir serait mensongère si son intention prioritaire
    # l'emmène ailleurs. Il ne promet ni de venir ni d'attendre dans ce cas.
    from .agendas import contrat_intention
    from .deliberation import Palier, _passe_avant
    i = lire(monde, qui)["intention"]
    contrat = contrat_intention(monde, qui)
    prioritaire = (contrat["palier"] < Palier.ATTENDRE_APPELANT if contrat
                   else _passe_avant(monde, qui, i))
    part_prioritaire = prioritaire and i and part(monde, qui, i["plan"])
    ici = None if part_prioritaire else VIENS
    if part_prioritaire and not _vise(i, autre):
        return None
    r = lire(monde, qui)["rejoint"]
    if r and r["qui"] == autre and not prie:
        return ici   # Il l'attend déjà ici ; prié de venir (l'autre ne le peut pas), il en décide de nouveau.
    if not peut_venir(monde, qui, autre) or retenu(monde, qui, autre) or presse_ailleurs(monde, qui, autre):
        return ici
    if prie or cherche(monde, qui, autre):
        return ARRIVE
    if raison is not None:
        return ARRIVE if pressante(monde, qui, raison) else ici
    return QUOI


def raison_de(monde, appelant, appele):
    """Ce que l'appelant veut de l'appelé, d'après son intention : le premier geste de son plan qui vise
    l'appelé (une demande, une offre, une tâche, ce qu'il a à dire) ; sinon son but (prévenir, une part,
    réclamer, s'enquérir, servir ou rendre, un feu à entretenir) ou le besoin qui le lui fait chercher
    (une part de ce qui le nourrit, le chauffe ou l'éclaire) ; sinon lui parler. Un plan qui cherche quelqu'un s'arrête à la recherche :
    la demande vient ensuite (``planification._chercher``)."""
    i = lire(monde, appelant)["intention"] if appelant != "joueur" else None
    if not i:
        return {"type": "propos"}
    for x in i["plan"]:
        if x.get("cible") == appele and x["operation"] in GESTES_RAISON:
            t = GESTES_RAISON[x["operation"]]
            return {"type": t, **({"objet": x["outil"]} if t == "demande" and x.get("outil") else {})}
    but = i["but"]
    objet = {"objet": but["objet"]} if but.get("objet") in monde.objets else {}
    if but["type"] == "prevenir":
        return {"type": "avertissement"}
    if (but["type"] in ("part", "reclamer", "lumiere", "enquete") or i["motif"] in ("faim", "chaleur")
            or but["type"] == "pulsion" and "allume" in but):
        return {"type": "demande", **objet}
    if but["type"] == "pulsion" and ("servir" in but or "rendre" in but or "remettre" in but):
        return {"type": "offre", **objet}
    return {"type": "propos"}


# --- Le temps de venir ---------------------------------------------------------------------------

def venue(monde, de, vers):
    """Le temps qu'il faut à ``de`` pour venir au contact de ``vers``, en dixièmes de seconde, par le plus
    court chemin en temps (``spatial.trajet``, portes fermées ouvertes en passant) ; None sans cases ou
    sans passage."""
    from .geometrie import distance
    from .ouie import _place
    from .pnj import PAS
    from .spatial import trajet
    from .temps import MINUTE, duree_pas
    (s1, c1), (s2, c2) = _place(monde, de), _place(monde, vers)
    if c1 is None or c2 is None or s1 not in monde.data["salles"] or s2 not in monde.data["salles"]:
        return None
    pas = trajet(monde, s1, c1, lambda s, c: s == s2 and distance(c, c2) <= 1, solides=False)
    if pas is None:
        return None
    return sum(duree_pas(PAS, sens) + (OUVRIR if porte else 0) for _, _, porte, sens in pas)


def delai(monde, de, vers):
    """L'échéance d'un rendez-vous, en minutes entières à partir de maintenant : le temps que met ``de``
    à venir à ``vers`` et sa moitié, plus ``MARGE`` minutes ; sans chemin connu, la marge seule deux
    fois."""
    from .temps import MINUTE
    t = venue(monde, de, vers)
    return 2 * MARGE if t is None else MARGE + -(-(t + t // 2) // MINUTE)


# --- Convenir ------------------------------------------------------------------------------------

def attendre(monde, id, qui, vient):
    """``id`` (un PNJ) attend ``qui`` là où il est, le temps que ``qui`` mette à venir (``delai``) ;
    ``vient`` : ``qui`` a promis de venir. Il s'arrête aussitôt, sauf pour ce qui passe avant l'attente
    (``deliberation._passe_avant``) ; la délibération en décide ensuite."""
    from .deliberation import _passe_avant, _plan_attendre
    from .esprits import reconsiderer
    minute = monde.data["minutes"]
    e = esprit(monde, id)
    if e["rejoint"] and e["rejoint"]["qui"] != qui:
        return   # Il attend déjà quelqu'un ici : il y reste, l'autre l'y trouvera ; un rendez-vous à la fois.
    e["rejoint"] = {"qui": qui, "depuis": minute, "jusqu_a": minute + delai(monde, qui, id), "vient": bool(vient)}
    resultat = _plan_attendre(monde, id)
    if resultat and not _passe_avant(monde, id, e["intention"]):
        e["intention"] = {"but": resultat[0], "motif": "rejoint", "plan": resultat[1], "depuis": minute, "attente": 0}
    reconsiderer(monde, id)


def venir(monde, id, qui):
    """``id`` (un PNJ) a dit « J'arrive ! » : il doit aller à ``qui``, là d'où vient sa voix, avant
    l'échéance du rendez-vous (``rejoindre``) ; il choisit son but à la fin de son geste."""
    from .esprits import reconsiderer
    from .ouie import _place
    minute = monde.data["minutes"]
    esprit(monde, id)["rejoindre"] = {"qui": qui, "salle": _place(monde, qui)[0], "depuis": minute,
                                      "jusqu_a": minute + delai(monde, id, qui)}
    reconsiderer(monde, id)


def dire(monde, qui, autre, sorte, lignes, raison=None, nommer=False):
    """``qui`` (un PNJ ou le joueur) crie à ``autre`` sa réponse (``sorte``) ou ce qu'il veut (``raison``) :
    un cri, nature « hele », que chacun saisit par l'ouïe commune. ``nommer`` : l'appelé qui répond à son
    nom se nomme ; l'appelant qui en saisit les mots le croit là d'où vient la réponse
    (``voix.se_nommer``). Ce que ``qui`` promet entre dans son esprit : il attend (« Ici, viens ! »), il
    doit venir (« J'arrive ! »). Vrai si ``autre`` en a saisi les mots."""
    from .ouie import retentir, saisit
    from .pnj import _chroniquer
    from .voix import connait_nom, se_nommer
    phrase = RAISONS[raison["type"]] if raison is not None else PHRASES[sorte]
    cri = texte(monde, qui, phrase)
    _chroniquer(monde, qui, cri, "reponse")   # Une réaction, pas un geste de son but.
    if qui == "joueur":
        lignes.append(f"Tu réponds : « {phrase} »")
    elif monde.visible(qui):
        lignes.append(cri)
    # Ces mots ne disent pas son nom : seul l'appelant qui le connaît déjà sait qui répond (branche des
    # noms, ``voix.connait_nom``) ; les autres relient la voix au nom hélé (``voix.lier``).
    nommer = nommer and connait_nom(monde, autre, qui)
    contenu = [{"type": "nom", "sujet": qui}] if nommer else []
    if raison is not None:
        contenu.append({**raison, "type": "raison", "sorte": raison["type"]})
    else:
        contenu.append({"type": "appel", "sorte": sorte})
    entendu = saisit(monde, qui, autre, "heler")
    retentir(monde, qui, "heler", texte=cri, cites=[autre], parole={"a": [autre], "contenu": contenu})
    if qui != "joueur" and raison is None:
        if sorte == VIENS:
            attendre(monde, qui, autre, vient=False)
        elif sorte == ARRIVE:
            if (lire(monde, qui)["rejoint"] or {}).get("qui") == autre:
                esprit(monde, qui)["rejoint"] = None   # Il ne l'attend plus : il y va.
            venir(monde, qui, autre)
    if nommer and entendu:
        se_nommer(monde, autre, qui, qui)
    return entendu


def repondre(monde, appelant, appele, lignes):
    """``appele`` a peut-être saisi son nom, hélé par ``appelant`` (un PNJ ou le joueur) : un PNJ répond
    selon ce qu'il décide (``decider``) ; le joueur répond s'il le veut, de lui-même. Vrai s'il a répondu ;
    un appelant PNJ resté sans réponse le retient (``appel_sans_reponse``)."""
    from .ouie import saisit
    from .deliberation import COMPTES
    sorte = None
    if appele != "joueur" and monde.objets[appele].get("profil") and saisit(monde, appelant, appele, "heler"):
        sorte = decider(monde, appele, appelant)
        if sorte is None:
            COMPTES["silence"] += 1
    if sorte is None:
        _sans_reponse(monde, appelant, appele)
        return False
    entendre(monde, appelant, appele, sorte, lignes, appelant=True,
             entendu=dire(monde, appele, appelant, sorte, lignes, nommer=True))
    return True


def _sans_reponse(monde, appelant, appele):
    if appelant != "joueur":
        from .deliberation import recherche_vaine
        recherche_vaine(monde, appelant, appele, monde.objets[appelant]["lieu"])
        memoriser(monde, appelant, {"type": "appel_sans_reponse", "qui": appele,
                                    "salle": monde.objets[appelant]["lieu"]})


def entendre(monde, x, y, sorte, lignes, appelant, entendu=True):
    """``x`` (un PNJ ou le joueur) a peut-être saisi ce que ``y`` vient de lui répondre (``sorte``) ;
    ``appelant`` : ``x`` avait hélé ``y``. Un PNJ y donne suite : « J'arrive ! », il l'attend ; « Ici,
    viens ! », il répond « J'arrive ! » s'il peut venir ; « Qu'est-ce que tu veux ? », il dit ce qu'il
    veut, et l'appelé décide de nouveau. Le joueur répond de lui-même (``reagir`` après coup)."""
    if not entendu:
        if appelant:
            _sans_reponse(monde, x, y)
        return
    if x == "joueur":
        return
    # Une réponse adressée et réellement saisie établit un nouveau contact, même si cette
    # voix avait déjà été entendue au même endroit. Elle ne se déduit pas d'un bruit attribué.
    from .ouie import _place
    from .deliberation import contact_recherche
    salle = _place(monde, y)[0]
    contact_recherche(monde, x, y, salle)
    if sorte == ARRIVE:
        attendre(monde, x, y, vient=True)
    elif sorte == VIENS:
        # Il vient s'il le peut ; l'appelant qui ne le peut pas le dit (« Ici, viens ! » à son tour),
        # une fois : qui l'entend vient, ou se tait.
        suite = decider(monde, x, y, prie=True)
        if suite == ARRIVE or suite == VIENS and appelant:
            vu = dire(monde, x, y, suite, lignes)
            if vu and y != "joueur":
                entendre(monde, y, x, suite, lignes, appelant=False)
    elif sorte == QUOI and appelant:
        raison = raison_de(monde, x, y)
        vu = dire(monde, x, y, None, lignes, raison=raison)
        if vu and y != "joueur":
            suite = decider(monde, y, x, raison=raison)
            if suite is None:
                from .deliberation import COMPTES
                COMPTES["silence"] += 1
                _sans_reponse(monde, x, y)
                return
            entendre(monde, x, y, suite, lignes, appelant=True, entendu=dire(monde, y, x, suite, lignes))


# --- Le joueur répond ----------------------------------------------------------------------------

def en_attente(monde):
    """Ceux qui attendent une réponse du joueur, avec ce qu'ils lui ont crié en dernier et qu'il a saisi
    juste avant (``ecoute.appels``) : [(id, « appel », « raison », ``QUOI`` ou ``VIENS``)], le plus récent
    d'abord."""
    from .ecoute import ENTENDU, REPONDRE
    from .ouie import VOCALES
    from .temps import instant
    maintenant, entendus_ = instant(monde), monde.data.get("entendus", [])
    derniers, attendent = set(), []
    for b in reversed(monde.data.get("bruits", [])):
        if b["nature"] not in VOCALES or b["niveau"] < ENTENDU or not b["texte"] or b["auteur"] in derniers:
            continue
        derniers.add(b["auteur"])
        sorte = sorte_du_cri(b["texte"])
        if (b["nature"] == "hele" and b.get("a") == ["joueur"] and sorte in ("appel", "raison", QUOI, VIENS)
                and b["auteur"] in monde.objets
                and (b["auteur"] in entendus_ or maintenant - b["instant"] <= REPONDRE)):
            attendent.append((b["auteur"], sorte))
    return attendent


def dernier_cri(monde, qui):
    """Ce que ``qui`` a crié en dernier au joueur, que le joueur a saisi (``sorte_du_cri``), sans
    limite de temps : ce à quoi répond le joueur, une fois sa réponse admise."""
    from .ecoute import ENTENDU
    from .ouie import VOCALES
    for b in reversed(monde.data.get("bruits", [])):
        if b["auteur"] == qui and b["nature"] in VOCALES and b["niveau"] >= ENTENDU and b["texte"]:
            return sorte_du_cri(b["texte"]) if b["nature"] == "hele" and b.get("a") == ["joueur"] else None
    return None


def permises(sorte_du_dernier_cri):
    """Ce que le joueur peut répondre à ce cri : à un appel, toutes les réponses ; à « Qu'est-ce que tu
    veux ? », à ce que l'appelant veut ou à « Ici, viens ! », venir ou faire venir."""
    return SORTES if sorte_du_dernier_cri == "appel" else (ARRIVE, VIENS)


def reagir(monde, qui, sorte, lignes):
    """Le joueur vient de répondre ``sorte`` à ``qui``, son cri fini : ``qui`` y donne suite s'il en a
    saisi les mots, par la règle commune (``entendre``) ; s'il avait lui-même été hélé par le joueur
    (« Qu'est-ce que tu veux ? »), il attend le joueur qui arrive, ou décide s'il vient quand le
    joueur le prie de venir."""
    from .ouie import saisit
    dernier = dernier_cri(monde, qui)
    entendu = qui in monde.objets and saisit(monde, "joueur", qui, "heler")
    if dernier in (QUOI, VIENS):
        # Il attend que le joueur dise qui vient : venir, il l'attend ; le prier de venir, il vient s'il
        # le peut, et à « Qu'est-ce que tu veux ? » répond aussi qu'il ne le peut pas, une fois.
        if not entendu:
            return
        if sorte == ARRIVE:
            attendre(monde, qui, "joueur", vient=True)
        elif sorte == VIENS:
            suite = decider(monde, qui, "joueur", prie=True)
            if suite == ARRIVE or suite == VIENS and dernier == QUOI:
                dire(monde, qui, "joueur", suite, lignes)
        return
    entendre(monde, qui, "joueur", sorte, lignes, appelant=True, entendu=entendu)


# --- Le rendez-vous ------------------------------------------------------------------------------

def part(monde, id, etapes):
    """Le plan quitte le lieu de la réponse, indépendamment de son motif."""
    return any(x["operation"] == "aller" and x["lieu"] != monde.objets[id]["lieu"] for x in etapes)


def rompre_attente(monde, id):
    """Annoncer le départ avant de reprendre un plan qui quitte le rendez-vous.

    Seul celui qui saisit l'annonce apprend la rupture ; sinon il doit encore
    constater le lieu vide. Aucun déplacement caché ne lui est communiqué.
    """
    from .deliberation import recherche_vaine
    from .esprits import croire, reconsiderer
    from .ouie import retentir, saisit
    from .pnj import _chroniquer
    from .voix import source_dite
    e = esprit(monde, id)
    r = e["rejoint"]
    if not r:
        return
    e["rejoint"] = None
    qui = r["qui"]
    if qui != "joueur" and qui not in monde.objets:
        return
    entendu = saisit(monde, id, qui, "heler")
    cri = texte(monde, id, "Je ne peux plus t'attendre.")
    # L'écoute de cette annonce situe encore la voix ici, puis l'annonce
    # invalide ce lieu comme destination convenue, sans inventer le suivant.
    bruits = monde.data.get("bruits", [])
    dernier = bruits[-1] if bruits else None
    retentir(monde, id, "heler", texte=cri, cites=[qui], parole={"a": [qui], "contenu": []})
    # Le choix du but n'a pas de liste de lignes où afficher la réplique.
    # Elle reste à rendre par l'écoute, même si le locuteur était visible.
    bruits = monde.data.get("bruits", [])
    if bruits and bruits[-1] is not dernier:
        bruits[-1].pop("vu", None)
    if entendu and qui == "joueur":
        croire(monde, qui, id, "lieu", None, source_dite(monde, qui, id), salle=None, case=None)
    if entendu and qui != "joueur":
        d = esprit(monde, qui)["rejoindre"]
        attend = esprit(monde, qui)["rejoint"]
        if d and d["qui"] == id or attend and attend["qui"] == id:
            salle = d["salle"] if d and d["qui"] == id else (
                memoire.fait_brut(monde, qui, id, 'lieu') or {}).get("valeur")
            for cle in ("rejoindre", "rejoint"):
                if (esprit(monde, qui)[cle] or {}).get("qui") == id:
                    esprit(monde, qui)[cle] = None
            if salle in monde.data["salles"]:
                recherche_vaine(monde, qui, id, salle)
            croire(monde, qui, id, "lieu", None, source_dite(monde, qui, id), salle=None, case=None)
            reconsiderer(monde, qui)
    _chroniquer(monde, id, cri, "reponse")


def rencontre(monde, id, qui):
    """``id`` et ``qui`` se retrouvent : il le voit, ou il le sait là et ils peuvent se parler."""
    from .esprits import percoit
    from .pnj import pourraient_se_parler
    return percoit(monde, id, qui) or pourraient_se_parler(monde, id, qui)


def _retrouver(monde, id, qui):
    """Une rencontre constatée clôt les deux moitiés du rendez-vous avant leur prochain geste.

    Si l'autre ne le sait pas encore là, il faut d'abord qu'il entende le signal ; le regard de
    l'un ne donne aucune perception à l'autre. Les deux reprennent ensuite leur but sur leurs
    connaissances présentes, au lieu de finir une recherche devenue caduque.
    """
    if qui != "joueur" and not rencontre(monde, qui, id):
        if not se_signaler(monde, id, qui):
            return
    retrouves(monde, id, qui)


def retrouves(monde, id, qui):
    """Contact constaté ou parole réellement échangée : une clôture, un récit pour les deux.

    Les voies de dialogue appellent aussi cette clôture (``deliberation.rejoint``), sans devoir
    attendre le prochain choix d'un but. Un autre rendez-vous éventuel reste intact.
    """
    from .esprits import percevoir, reconsiderer
    from .pnj import _chroniquer
    from .social import _qui
    attendait = None
    for x, y in ((id, qui), (qui, id)):
        if x == "joueur":
            continue
        e = esprit(monde, x)
        change = False
        for k in ("rejoint", "rejoindre"):
            if (e[k] or {}).get("qui") == y:
                if k == "rejoint" and attendait is None:
                    attendait = x, y
                e[k] = None
                change = True
        if change:
            percevoir(monde, x)
            reconsiderer(monde, x)
    if attendait:
        x, y = attendait
        _chroniquer(monde, x, f"{_qui(monde, x)} retrouve {_qui(monde, y)}, comme convenu.", "reponse")


def tenir(monde, id, minute):
    """Le rendez-vous de ``id``, d'après ce qu'il voit, à chaque choix de son but (``deliberation.attendre``).
    Il attendait : retrouvé, l'attente est finie ; à l'échéance, il cesse d'attendre et, si l'autre avait
    promis de venir, il le voit : une parole non tenue (``relations``). Il devait venir : arrivé, ou là
    sans y trouver personne, il n'a plus à venir. Le délai écoulé ne lui apprend
    pas que le lieu est vide."""
    from .pnj import _chroniquer
    from .social import _qui
    from .voix import se_mefier
    e = esprit(monde, id)
    r = e["rejoint"]
    if r and r["qui"] != "joueur" and r["qui"] not in monde.objets:
        e["rejoint"] = None
    elif r and rencontre(monde, id, r["qui"]):
        qui = r["qui"]
        d = lire(monde, qui)["rejoindre"] if qui != "joueur" else None
        if d and d["qui"] == id and minute < r["jusqu_a"]:
            # Le voyageur traite l'arrivée à son prochain choix, après son geste en cours.
            # Celui qui attend ne repart pas entre l'aperçu au seuil et ce choix.
            from .esprits import percevoir, reconsiderer
            if not rencontre(monde, qui, id):
                se_signaler(monde, id, qui)
            percevoir(monde, qui)
            reconsiderer(monde, qui)
        else:
            _retrouver(monde, id, qui)
    elif r and minute >= r["jusqu_a"]:
        e["rejoint"] = None
        if r["vient"]:
            _chroniquer(monde, id, f"{_qui(monde, id)} cesse d'attendre {_qui(monde, r['qui'])}, qui avait promis "
                                   "de venir.", "reponse")
            # Une parole non tenue (``relations.souvenir``) ; d'une voix qu'il ne sait à qui prêter, il se
            # méfie de cette voix (``voix.se_mefier``), comme d'un mensonge.
            memoriser(monde, id, {"type": "parole_rompue", "qui": r["qui"]})
            se_mefier(monde, id, r["qui"], cause="parole_rompue")
        else:
            _chroniquer(monde, id, f"{_qui(monde, id)} cesse d'attendre {_qui(monde, r['qui'])}.", "reponse")
    d = e["rejoindre"]
    if not d:
        return
    if d["qui"] != "joueur" and d["qui"] not in monde.objets:
        e["rejoindre"] = None
    # L'aperçu d'une autre salle ne termine pas le trajet promis : les gestes d'interaction
    # exigent d'avoir rejoint le lieu. Une parole échangée clôt aussi la venue, via ``rejoint``.
    elif monde.objets[id]["lieu"] == d["salle"] and rencontre(monde, id, d["qui"]):
        _retrouver(monde, id, d["qui"])
    elif monde.objets[id]["lieu"] == d["salle"] and (
              e["visites"].get(d["salle"], -1) > d["depuis"]
              or memoire.lieux_ecartes(monde, id, d["qui"]).get(d["salle"], -1) >= d["depuis"]):
        e["rejoindre"] = None
        memoriser(monde, id, {"type": "rendez_vous_manque", "qui": d["qui"]})


ME_VOICI = "Me voici !"


def se_signaler(monde, id, qui):
    """``id`` voit son interlocuteur du rendez-vous, qui ne le sait pas encore là : il se signale
    (« Me voici ! »), qu'il soit venu ou qu'il l'attende. Renvoie si les mots lui sont parvenus ;
    le signal seul ne clôt rien. Une voix connue actualise la présence par l'ouïe commune."""
    from .ouie import retentir, saisit
    from .pnj import _chroniquer
    from .voix import connait_nom, se_nommer
    if qui == "joueur" or not any((lire(monde, qui)[k] or {}).get("qui") == id
                                   for k in ("rejoint", "rejoindre")):
        return False
    cri = texte(monde, id, ME_VOICI)
    _chroniquer(monde, id, cri, "reponse")
    entendu = saisit(monde, id, qui, "dire")
    # « Me voici ! » ne dit pas son nom : qui l'attend le reconnaît s'il le connaît déjà (``voix.connait_nom``).
    nomme = connait_nom(monde, qui, id)
    retentir(monde, id, "dire", texte=cri, cites=[qui],
             parole={"a": [qui], "contenu": [{"type": "nom", "sujet": id}] if nomme else []})
    if entendu:
        if nomme:
            se_nommer(monde, qui, id, id)
    return entendu


def plan_venir(monde, id):
    """Tenir « J'arrive ! » : aller là d'où venait sa voix et y parcourir la salle des yeux, en l'appelant
    s'il ne le voit pas (``pnj._inspecter``)."""
    from .planification import aller
    d = lire(monde, id)["rejoindre"]
    if not d:
        return None
    regarder = [{"operation": "inspecter", "cible": "", "outil": "", "lieu": d["salle"], "condition": "",
                 "contenu": {"cherche": d["qui"]}}]
    but = {"type": "rejoindre", "qui": d["qui"], "lieu": d["salle"]}
    if monde.objets[id]["lieu"] == d["salle"]:
        return but, regarder
    etapes = aller(monde, id, d["salle"])
    # Un chemin coupé ne permet pas de rappeler depuis un autre lieu :
    # garder la destination jusqu'à un constat ou une rupture entendue.
    return (but, []) if etapes is None else (but, etapes + regarder)


def verifier(monde, e):
    """La forme du rendez-vous dans un esprit (``esprits.verifier``)."""
    r, d = e["rejoint"], e["rejoindre"]
    assert r is None or (isinstance(r, dict) and set(r) == {"qui", "depuis", "jusqu_a", "vient"}
                         and (r["qui"] == "joueur" or r["qui"] in monde.objets) and type(r["vient"]) is bool
                         and type(r["depuis"]) is int and type(r["jusqu_a"]) is int), "Attente de PNJ invalide"
    assert d is None or (isinstance(d, dict) and set(d) == {"qui", "salle", "depuis", "jusqu_a"}
                         and (d["qui"] == "joueur" or d["qui"] in monde.objets) and d["salle"] in monde.data["salles"]
                         and type(d["depuis"]) is int and type(d["jusqu_a"]) is int), "Rendez-vous de PNJ invalide"
