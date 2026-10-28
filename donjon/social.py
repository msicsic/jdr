"""Couche sociale entre PNJ : nouvelles, rumeurs et réputations.

Un PNJ qui a une nouvelle (un geste illicite vu, un bien aperçu aux mains d'un autre, un
mensonge découvert, un objet disparu, une rumeur reçue) la confie à un personnage qu'il
perçoit dans sa salle et à qui il fait confiance ; le geste prend sa minute. Il ne la confie
ni à celui qu'elle accuse, ni à celui qui la lui a apprise. L'auditeur l'adopte avec la règle
des paroles du joueur : ce qu'il a vu récemment prime, sinon jet de CHA du locuteur contre
sa confiance. Une rumeur passe de proche en proche jusqu'au troisième relais, en perdant de
sa confiance. Le joueur entend ce qui se dit dans sa salle, en clair s'il connaît ce dont on
parle, sinon comme un échange à voix basse. Tout est déterministe ; Luna n'intervient pas.

Un avis de menace prévient plutôt qui le locuteur croit concerné et dont il se soucie.
L'auditeur pèse sa source et sa conviction ; un avis contraire plus étayé ouvre une dispute
finie, dont seuls les poids égaux se départagent au jet opposé. Les nouvelles et leurs
destinataires déjà servis restent suivis par le même registre, hors des souvenirs bornés.

Une parole, du joueur comme d'un PNJ, est entendue de tous ceux qui en saisissent les mots
(``ouie``) : qui n'en est pas le destinataire la retient aussi (``retenir_parole``), et ce
qu'elle transmet le touche par la même règle que le destinataire (``recevoir``) : une
affirmation se juge comme une confidence, une nouvelle comme une rumeur, un aveu se croit, un nom
se pèse (``voix.se_nommer``). Qui parle d'une voix que l'auditeur ne sait à qui prêter reste un
inconnu pour lui : sa méfiance va à cette voix, son ouï-dire ne nomme personne (``voix``).
"""
import copy
import json

from .francais import pluriel as nombre_pluriel
from .francais import quantite
from .esprits import RECENT, croire, esprit, lire, memoriser, pnjs
from .francais import complement_de, designer, de, groupe_nominal
from .relations import se_fie, envers

# ``dette_niee`` : un débiteur refuse de rendre ce qu'il doit ; ``pret_garde`` : un emprunteur garde un
# prêt échu qu'on lui réclame (``biens``).
NOUVELLES = ("vu_agir", "vol_surpris", "vu_porter", "mensonge_decouvert", "mensonge_dementi", "absence",
             "dette_niee", "pret_garde", "mort_vue", "intention_lue")
RANG_MAX = 2           # une rumeur entendue de troisième main n'est plus répétée
GESTES = {"tuer": "a tenté de tuer", "saisir": "a tenté de saisir", "ligoter": "a tenté de ligoter",
          "delier": "a tenté de délier", "liberer": "a tenté de libérer",
          "enfermer": "a enfermé", "trainer": "a traîné", "prendre": "a pris", "poser": "a posé", "ouvrir": "a ouvert", "fermer": "a fermé",
          "deverrouiller": "a déverrouillé", "verrouiller": "a verrouillé",
          "crocheter": "a crocheté la serrure de", "forcer": "a tenté de crocheter la serrure de",
          "frapper": "a frappé", "briser": "a forcé",
          "manger": "a mangé une part de", "servir": "a servi une part de", "alimenter": "a rechargé",
          "allumer": "a allumé", "eteindre": "a éteint", "pousser": "a poussé", "assommer": "a tenté d’assommer"}

# Indépendant des quarante souvenirs. À saturation, on garde les faits déjà suivis
# et on tait les nouveaux : évincer une entrée autoriserait une répétition indue.
DITS_MAX = 512


def _cle(fait):
    return json.dumps(fait, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def faits_dits(noyau):
    """Identités et valeurs transmises, sans texte, date, preuve ni qualité de la source.

    Les constats et les affirmations partagent la même identité de propriété.
    Un geste reste un fait distinct d'un état ; son lieu dit est une valeur, pas
    la date ou la case depuis lesquelles le témoin l'a appris.
    """
    t = noyau["type"]
    if t in ("affirmation", "constat", "avis"):
        sujet = noyau.get("sujet", noyau.get("objet"))
        attribut, valeur = noyau["attribut"], noyau["valeur"]
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


def transmission_attestee(monde, id, auditeur, noyau):
    """Preuve positive du contenu partagé ; le registre plein n'en est pas une."""
    registre = lire(monde, id)["faits_dits"]
    return all(cle in registre and (
               auditeur in registre[cle]["dit_a"] and registre[cle]["dit_a"][auditeur] == valeur
               or valeur in registre[cle].get("entendu_a", {}).get(auditeur, []))
               for cle, valeur in faits_dits(noyau))


def deja_dit(monde, id, auditeur, noyau):
    registre = lire(monde, id)["faits_dits"]
    return all((cle in registre and auditeur in registre[cle]["dit_a"]
                and registre[cle]["dit_a"][auditeur] == valeur)
               or (cle in registre and valeur in registre[cle].get("entendu_a", {}).get(auditeur, []))
               # Une nouvelle identité ne peut plus être suivie à saturation.
               or cle not in registre and len(registre) >= DITS_MAX
               for cle, valeur in faits_dits(noyau))


def retenir_dit(monde, id, auditeur, noyau):
    registre = esprit(monde, id)["faits_dits"]
    for cle, valeur in faits_dits(noyau):
        if cle not in registre and len(registre) >= DITS_MAX:
            continue
        if cle not in registre:
            registre[cle] = {"valeur": copy.deepcopy(valeur), "dit_a": {}}
        registre[cle]["valeur"] = copy.deepcopy(valeur)
        registre[cle].pop("valeur_inconnue", None)
        registre[cle]["dit_a"][auditeur] = copy.deepcopy(valeur)


def _audience_connue(monde, locuteur, contenu, geste, observateur=None):
    """Photographie ce que chacun peut constater de l'audience de la parole.

    Entendre n'établit pas la vérité du contenu. Le registre suit seulement
    qui le sait déjà dit, y compris quand il refuse de le croire. Un témoin
    caché ne devient pas connu des autres par sa seule présence réelle.
    """
    from .ouie import saisit
    from .pnj import pourraient_se_parler
    from .paroles import _stats_pnj, capacite_transmission
    auditeurs = [x for x in sorted(pnjs(monde)) if x != locuteur
                 and monde.objets[x].get("profil") and saisit(monde, locuteur, x, geste)]
    suivis = []
    for observateur in ([observateur] if observateur is not None else [locuteur, *auditeurs]):
        if observateur == "joueur":
            continue
        capacite = min(capacite_transmission(_stats_pnj(monde, x)["INT"])
                       for x in (locuteur, observateur))
        for autre in [locuteur, *auditeurs]:
            if autre == observateur or not pourraient_se_parler(monde, observateur, autre):
                continue
            compris = min(capacite, capacite_transmission(_stats_pnj(monde, autre)["INT"]))
            for c in contenu[:compris]:
                if c["type"] in ("affirmation", "rumeur", "aveu"):
                    suivis.append((observateur, autre, c if c["type"] == "affirmation" else c["evenement"]))
    return suivis


def _retenir_audience(monde, audience):
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
    if attribut == "intention":
        valeur = {"valeur": valeur, "envers": details.get("envers")}
    registre = lire(monde, id)["faits_dits"]
    avant = {}
    if precedente:
        ancienne = ({"valeur": precedente["valeur"], "envers": precedente.get("envers")}
                    if attribut == "intention" else precedente["valeur"])
        avant = dict(faits_dits({"type": "affirmation", "sujet": sujet, "attribut": attribut,
                                "valeur": ancienne}))
    for cle, v in faits_dits({"type": "affirmation", "sujet": sujet, "attribut": attribut, "valeur": valeur}):
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
    e = esprit(monde, id)
    for s in e["memoire"]:
        if s["type"] == "dit" and "valeur" in s:
            retenir_dit(monde, id, s["a"], {"type": "affirmation", **{k: s[k] for k in ("sujet", "attribut", "valeur")}})
        elif s["type"] in NOUVELLES or s["type"] == "rumeur":
            for a in s.get("dit_a", []):
                retenir_dit(monde, id, a, s["evenement"] if s["type"] == "rumeur" else s)
    for sujet, attributs in e["croyances"].items():
        for attribut, c in attributs.items():
            for a in c.get("confie", {}).get("dit_a", []):
                retenir_dit(monde, id, a, {"type": "affirmation", "sujet": sujet, "attribut": attribut,
                                         "valeur": c["confie"]["valeur"]})


def _noyau(evenement):
    """Contenu et date d'observation, sans destinataires ni mode d'acquisition (``par``)."""
    return {**{k: v for k, v in evenement.items() if k not in ("minute", "dit_a", "par")},
            "observe": evenement.get("observe", evenement.get("minute", 0))}


def _fait(noyau):
    """Le fait dont parle la nouvelle, sans le lieu où chacun a vu l'objet aller : deux témoins
    du même geste racontent la même chose."""
    return {k: v for k, v in noyau.items() if k != "lieu"}


def accuse(evenement):
    if evenement["type"] in ("intention_lue", "vu_agir", "vol_surpris", "vu_porter", "dette_niee", "pret_garde"):
        return evenement["auteur"]
    if evenement["type"] in ("mensonge_decouvert", "mensonge_dementi"):
        return evenement.get("locuteur", "joueur")
    return None


def _proprietaire(monde, evenement):
    """Propriétaire déclaré de l'objet ou de son contenant ; le porter ne suffit pas à le posséder."""
    o = monde.objets.get(evenement.get("objet") or "")
    while o and o["type"] != "personnage":
        if o.get("proprietaire"):
            return o["proprietaire"]
        o = monde.objets.get(o["lieu"])
    return None


def _croit_encore(monde, id, noyau):
    """On ne répète que ce qu'on croit encore."""
    croyances = lire(monde, id)["croyances"]
    if noyau["type"] == "constat":
        c = croyances.get(noyau["objet"], {}).get(noyau["attribut"])
        return (monde.data["minutes"] - noyau["observe"] <= RECENT and _meme_constat(c, noyau))
    if noyau["type"] == "intention_lue":
        from .signes import intentions_lues
        return any(x == noyau["auteur"] and c.get("envers") == noyau["objet"] for x, c in intentions_lues(monde, id))
    if noyau["type"] == "absence":
        lieu = croyances.get(noyau["objet"], {}).get("lieu")
        return bool(lieu) and lieu["valeur"] is None
    if noyau["type"] == "mort_vue":
        return bool(lire(monde, id)["croyances"].get(noyau["objet"], {}).get("etat", {}).get("valeur", {}).get("mort"))
    return not se_fie(monde, id, accuse(noyau))


def nouvelles(monde, id):
    """Une seule version d'un fait : la dernière apprise, pas ses anciens souvenirs."""
    retenues, vus = [], set()
    for nouvelle in reversed(list(_nouvelles(monde, id))):
        cles = tuple(cle for cle, _ in faits_dits(nouvelle[1]))
        if cles not in vus:
            retenues.append(nouvelle)
            vus.add(cles)
    yield from reversed(retenues)


def _nouvelles(monde, id):
    """Suivi, noyau, rang, source : constats matériels puis souvenirs anciens à récents."""
    # Les croyances constituent déjà le registre daté des constats, sans souvenir
    # supplémentaire à chaque perception. Placés d'abord, ils passent après les accusations.
    yield from _constats(monde, id)
    yield from _avis(monde, id)
    for souvenir in lire(monde, id)["memoire"]:
        if souvenir["type"] in NOUVELLES:
            # Ce qu'il n'a fait qu'entendre (``pnj._temoins_a_l_oreille``) se dit avec moins de
            # certitude que ce qu'il a vu : comme de seconde main.
            noyau, rang, source = _noyau(souvenir), 1 if souvenir.get("par") == "ouie" else 0, None
        elif souvenir["type"] == "rumeur" and souvenir["rang"] < RANG_MAX:
            noyau, rang, source = {"observe": souvenir["minute"], **souvenir["evenement"]}, souvenir["rang"], souvenir["de"]
        else:
            continue
        if (accuse(noyau) == id
                or any(k not in monde.objets and k not in monde.data["salles"]
                       for k in (noyau.get("objet"),) if k and k != "joueur")
                or not _croit_encore(monde, id, noyau)):
            continue  # Sa propre accusation ne se transmet pas, même depuis une ancienne sauvegarde.
        if "lieu" in noyau and _cru_ailleurs(monde, id, noyau):
            noyau = _fait(noyau)  # Il ne le croit plus là : il dit le geste, sans le lieu.
        if noyau["type"] == "constat":
            c = lire(monde, id)["croyances"][noyau["objet"]][noyau["attribut"]]
            if c["source"] in ("vu", "essai"):
                continue  # Son propre constat est déjà offert, de première main.
            souvenir = c
        yield souvenir, noyau, rang, source


def _meme_constat(croyance, noyau):
    if not croyance:
        return False
    valeur = croyance["valeur"]
    return (all(valeur.get(k) == v for k, v in noyau["valeur"].items())
            if noyau["attribut"] == "etat" else valeur == noyau["valeur"])


def _avis(monde, id):
    """Menaces déduites des preuves du locuteur, sans lire l'esprit d'un autre."""
    from . import eau
    from .esprits import prevision, poids_source
    if not eau.active(monde):
        return
    for salle in sorted(monde.data["salles"]):
        c = prevision(monde, id, salle)
        if not c:
            continue
        menace = eau.menacee(monde, id, salle)
        reviser_dits(monde, id, salle, "menace", menace)
        if not menace or c.get("rang", 0) >= RANG_MAX:
            continue
        from .voix import auteur_dit
        source = auteur_dit(c["source"])[0] if c["source"].startswith("dit:") else None
        yield c, {"type": "avis", "objet": salle, "attribut": "menace", "valeur": True,
                  "prevision": copy.deepcopy(c["valeur"]), "observe": c["minute"],
                  "conviction": min(1, poids_source(monde, id, c) * c["confiance"])}, c.get("rang", 0), source


def _concerne(monde, id, autre, salle):
    from .caractere import valeur
    from .deliberation import salle_crue
    if valeur(monde, id, "altruisme") + valeur(monde, id, "empathie") + envers(monde, id, autre)["affection"] < 100:
        return False
    if salle_crue(monde, id, autre) == salle:
        return True
    # Une destination n'est connue que si elle a été convenue : aucune lecture du plan privé.
    rendez_vous = lire(monde, id)["rejoint"]
    return bool(rendez_vous and rendez_vous["qui"] == autre and rendez_vous["vient"]
                and monde.data["minutes"] < rendez_vous["jusqu_a"] and monde.objets[id]["lieu"] == salle)


def _constats(monde, id):
    for objet, attributs in lire(monde, id)["croyances"].items():
        if objet not in monde.objets and objet not in monde.data["salles"]:
            continue
        for attribut, c in attributs.items():
            if c["source"] not in ("vu", "essai") or monde.data["minutes"] - c["minute"] > RECENT:
                continue
            valeur = c["valeur"]
            if attribut == "etat":
                valeur = {k: False for k in ("disponible", "allume") if valeur.get(k) is False}
                if c["valeur"].get("vide") is True:
                    valeur["vide"] = True
                if "parti" in c["valeur"]:
                    valeur["parti"] = c["valeur"]["parti"]
                if not valeur:
                    continue
            elif not (attribut == "verrouillee" and valeur is True
                      or attribut == "eau" and valeur > 0):
                continue
            noyau = {"type": "constat", "objet": objet, "attribut": attribut,
                     "valeur": valeur, "observe": c["minute"]}
            if attribut == "eau":
                noyau["details"] = {k: c[k] for k in ("niveau", "montee", "repere") if k in c}
            yield c, noyau, 0, None


def _cru_ailleurs(monde, id, noyau):
    """Depuis ce que dit la nouvelle, il a appris que l'objet n'est plus là où elle le met."""
    lieu = lire(monde, id)["croyances"].get(noyau["objet"], {}).get("lieu")
    return bool(lieu) and lieu["minute"] > noyau["lieu"]["minute"] and lieu["valeur"] != noyau["lieu"]["valeur"]


def _sait(monde, id, noyau):
    if noyau["type"] == "avis":
        # Une conclusion commune n'est pas une preuve identique : les prévisions
        # peuvent différer en date, pente et conviction. Le locuteur n'a pas accès
        # à celles de l'auditeur ; celui-ci les pèsera seulement en recevant l'avis.
        # Le registre des faits dits borne les avertissements, même refusés.
        return False
    if noyau["type"] == "constat":
        c = lire(monde, id)["croyances"].get(noyau["objet"], {}).get(noyau["attribut"])
        return (_meme_constat(c, noyau) or bool(c and c["source"] in ("vu", "essai", "entendu")
                                               and c["minute"] >= noyau["observe"]))
    if noyau["type"] == "intention_lue":
        from .signes import intentions_lues
        return any(x == noyau["auteur"] and c.get("envers") == noyau["objet"]
                   for x, c in intentions_lues(monde, id))
    fait = faits_dits(noyau)
    return any((faits_dits(s) == fait if s["type"] in NOUVELLES
                else s["type"] == "rumeur" and faits_dits(s["evenement"]) == fait)
               for s in lire(monde, id)["memoire"])


def _auditeur(monde, id, souvenir, noyau, source):
    """Premier personnage présent à qui confier cette nouvelle, dans un ordre stable."""
    from .pnj import pourraient_se_parler
    from .signes import emotion
    colere = emotion(monde, id)
    accusee = accuse(noyau)
    if (colere and colere["niveau"] >= 20 and colere["contre"] == accusee and accusee in monde.objets
            and accusee != id and not deja_dit(monde, id, accusee, noyau)
            and pourraient_se_parler(monde, id, accusee)):
        return accusee
    for autre in sorted(pnjs(monde), key=lambda x: (-envers(monde, id, x)["affection"], x)):
        if (autre == id or deja_dit(monde, id, autre, noyau) or autre in (accuse(noyau), source)
                or not monde.objets[autre].get("profil")
                or monde.objets[autre]["lieu"] != monde.objets[id]["lieu"]
                or not pourraient_se_parler(monde, id, autre)
                or (not _concerne(monde, id, autre, noyau["objet"]) if noyau["type"] == "avis"
                    else not se_fie(monde, id, autre))):
            continue
        if noyau["type"] == "absence" and _proprietaire(monde, noyau) != autre:
            continue  # Un objet manquant ne regarde que son propriétaire.
        return autre
    return None


def _qui(monde, id, locuteur=None):
    """Nom d'une chronique, ou désignation que le locuteur peut réellement prononcer. Un défunt garde
    le nom qu'il portait (``corps.mourir``)."""
    if locuteur is not None:
        from .voix import connait_nom, identifie
        if not connait_nom(monde, locuteur, id):
            if id == 'joueur':
                return "l'étrangère" if monde.joueur.get('genre') == 'f' else "l'étranger"
            from .noms import nom
            return nom(monde, id, observateur=locuteur) if identifie(monde, locuteur, id) else "quelqu'un"
    if id in monde.data.get("defunts", {}):
        return monde.data["defunts"][id]["nom"].split(",")[0]
    return monde.joueur["nom"] if id == "joueur" else monde.objets[id]["nom"].split(",")[0]


def phrase(monde, noyau, locuteur=None):
    o = monde.objets.get(noyau.get("objet") or "")
    t = noyau["type"]
    if t == "avis":
        from .francais import lieu
        return ("l'eau menace " if noyau["valeur"] else "l'eau ne menace pas ") + lieu(monde.data["salles"][noyau["objet"]]) + " dans l'heure"
    if t == "constat":
        from .francais import accorder, lieu
        if noyau["attribut"] == "eau":
            return f"l'eau atteint {noyau['valeur']} cm dans " + lieu(monde.data["salles"][noyau["objet"]])
        qualite = ("fermé" if noyau["attribut"] == "verrouillee" else
                   ("parti" if noyau["valeur"]["parti"] else "revenu") if "parti" in noyau["valeur"] else
                   "vide" if "vide" in noyau["valeur"] else
                   "épuisé" if "disponible" in noyau["valeur"] else "éteint")
        return (designer(o) + (" sont " if nombre_pluriel(o) else " est ")
                + accorder(o, qualite, "vide" if qualite == "vide" else None)
                + (" à clé" if noyau["attribut"] == "verrouillee" else ""))
    if t == "intention_lue":
        return _qui(monde, noyau["auteur"], locuteur) + " semble guetter " + designer(o)
    if t == "absence":
        return designer(o) + " " + ("ont" if nombre_pluriel(o) else "a") + " disparu"
    if t == "mort_vue":
        defunt = monde.data["defunts"][noyau["objet"]]
        return _qui(monde, noyau["objet"], locuteur) + " est mort" + ("e" if defunt["genre"] == "f" else "")
    qui = _qui(monde, accuse(noyau), locuteur)
    if t in ("mensonge_decouvert", "mensonge_dementi"):
        return qui + (" semble mentir" if noyau.get("source") == "devine" else " ment")
    if t == "vol_surpris":
        return qui + " a tenté de dérober " + designer(o)
    il = "elle" if monde.objets.get(accuse(noyau), {}).get("genre") == "f" else "il"
    if t == "dette_niee":
        n = noyau["montant"]
        return f"{qui} garde {quantite(n, 'pièce', determinant='defini')} qu'{il} doit " + groupe_nominal(_qui(monde, noyau['victime'], locuteur), "à")
    if t == "pret_garde":
        return (f"{qui} garde {designer(o)} que {_qui(monde, noyau['victime'], locuteur)} lui a "
                + ("prêtée" if o.get("genre") == "f" else "prêté"))
    if t == "vu_porter":
        return qui + " porte " + designer(o) + ", qui n'est pas à " + ("lui" if monde.objets.get(accuse(noyau), {}).get("genre") != "f" else "elle")
    verbe = GESTES[noyau["operation"]]
    if noyau.get("objet") == "joueur":
        return qui + " " + verbe + " " + monde.joueur["nom"]  # Un geste contre lui (``pnj.CONTRAINTES``).
    return (qui + " " + (verbe[:-3] + " " + complement_de(o) if verbe.endswith(" de") else verbe + " " + designer(o))
            + _ou(monde, noyau))


def _ou(monde, noyau):
    """Où l'objet est allé, s'il l'a vu poser : « dans <salle> », « dans <contenant> » ; porté par
    l'auteur, la phrase le dit déjà (« a pris »)."""
    from .francais import lieu as designer_lieu
    lieu = (noyau.get("lieu") or {}).get("valeur")
    if lieu in monde.data["salles"]:
        return " dans " + designer_lieu(monde.data["salles"][lieu])
    if lieu in monde.objets and monde.objets[lieu]["type"] != "personnage":
        return " dans " + designer(monde.objets[lieu])
    return ""


def _lieu_dit(noyau):
    """Le lieu que la nouvelle donne à son objet (``_ou``), pour qui l'entend."""
    lieu = (noyau.get("lieu") or {}).get("valeur")
    return [lieu] if lieu and lieu != accuse(noyau) else []


def _adopter(monde, auditeur, locuteur, noyau, rang):
    """L'auditeur croit-il la nouvelle ? Effets sur ses croyances et ses besoins."""
    from .paroles import _stats_pnj, dementi, jet_persuasion
    from .voix import identifie, se_mefier, source_dite
    if noyau["type"] == "constat" and noyau.get("attribut") == "statuts":
        return recevoir_statuts(monde, auditeur, locuteur, noyau["objet"], noyau["valeur"],
                                minute=noyau["observe"], confiance=round(.7 * .8 ** rang, 2))
    objet = noyau.get("objet")
    observe = noyau.get("observe", monde.data["minutes"])
    proprietes = [json.loads(cle) for cle, _ in faits_dits(noyau)]
    if all(isinstance(cle, list) for cle in proprietes):
        for sujet, attribut, *_ in proprietes:
            c = lire(monde, auditeur)["croyances"].get(sujet, {}).get(attribut)
            if c and (c["minute"] > observe or c["minute"] == observe
                      and c["source"] in ("vu", "essai", "entendu", "devine")):
                return None  # Toute propriété transmise garde la date de sa source.
    actuelle = lire(monde, auditeur)["croyances"].get(objet, {}).get(noyau.get("attribut"))
    if noyau["type"] == "absence" and dementi(monde, auditeur, objet, "lieu", None):
        if identifie(monde, auditeur, locuteur):
            memoriser(monde, auditeur, {"type": "mensonge_dementi", "locuteur": locuteur, "sujet": objet,
                                        "attribut": "lieu"})
        se_mefier(monde, auditeur, locuteur, "vu")
        return "dementi"
    if not jet_persuasion(monde, auditeur, locuteur, 10)[0]:
        memoriser(monde, auditeur, {"type": "parole_doutee", "locuteur": locuteur, "evenement": noyau})
        return "doute"
    confiance = round(0.7 * (0.5 if _stats_pnj(monde, auditeur)["INT"] <= 8 else 1.0) * 0.8 ** rang, 2)
    source = source_dite(monde, auditeur, locuteur)
    if noyau["type"] == "constat":
        attribut, valeur = noyau["attribut"], noyau["valeur"]
        if attribut == "etat":
            valeur = {**(actuelle or {}).get("valeur", {}), **valeur}
        croire(monde, auditeur, objet, attribut, valeur, source, confiance,
               minute=noyau["observe"], **noyau.get("details", {}))
    elif noyau["type"] == "intention_lue":
        croire(monde, auditeur, noyau["auteur"], "intention", "guet", source,
               min(.4, noyau["confiance"] * confiance), signe=noyau["signe"], envers=objet,
               minute=observe,
               **({"episode": noyau["episode"]} if "episode" in noyau else {}))
    elif noyau["type"] == "mort_vue":
        actuelle = lire(monde, auditeur)["croyances"].get(objet, {}).get("etat")
        if not actuelle or actuelle["source"] != "vu":
            croire(monde, auditeur, objet, "etat", {"mort": True}, source, confiance, minute=observe)
            from .deliberation import inquieter
            inquieter(monde, auditeur, "mort")
    elif noyau["type"] == "absence":
        croire(monde, auditeur, objet, "lieu", None, source, confiance, minute=observe, salle=None, case=None)
    elif accuse(noyau) != auditeur:
        _apprendre_lieu(monde, auditeur, noyau, source, confiance)
    return "crue"


def _apprendre_lieu(monde, auditeur, noyau, source, confiance):
    """Une nouvelle qui dit où l'objet est allé donne au destinataire une croyance de lieu, à la
    confiance du ouï-dire. Ce qu'il en a constaté lui-même après le geste rapporté (vu, essayé,
    entendu après la minute ``lieu["minute"]``) prime ; ne pas l'avoir trouvé là où il l'attendait
    ne dit pas qu'il n'est pas ailleurs, et un ouï-dire cède à la nouvelle qui le précise."""
    lieu, objet = noyau.get("lieu"), noyau.get("objet")
    if not lieu or objet not in monde.objets or lieu["valeur"] == auditeur:
        return
    if not (lieu["valeur"] in monde.data["salles"] or lieu["valeur"] in monde.objets or lieu["valeur"] == "joueur"):
        return  # Le lieu a disparu depuis : il n'y a plus rien à en croire.
    actuelle = lire(monde, auditeur)["croyances"].get(objet, {}).get("lieu")
    if (actuelle and actuelle["valeur"] is not None and actuelle["source"] in ("vu", "essai", "entendu")
            and actuelle["minute"] > lieu["minute"]):
        return
    croire(monde, auditeur, objet, "lieu", lieu["valeur"], source, confiance, salle=lieu["salle"],
           case=lieu["case"])


def faire_entendre(monde, id, auditeur, texte, cites, lignes, contenu=(), reponse="", dite=True, suites=True,
                  geste="dire"):
    """Une parole retentit avec ses mots (``ouie``) : qui en saisit les mots sans en être le
    destinataire retient ce qu'elle transmet (``contenu``, typé : ``recevoir``). ``reponse`` : ce que
    l'auditeur y répond (accepter, refuser), de sa voix si ``dite`` (sinon un geste, lui remettre
    l'objet) : sa réponse retentit à son tour, sans rien transmettre ; qui le voit répondre connaît
    sa voix. Ce que le joueur perçoit de l'échange, s'il le voit : en clair s'il connaît chacun de
    ceux dont on parle. Sans le voir (le noir, son dos), il n'en a que ce que son ouïe lui fait
    entendre (``ecoute`` : une voix qu'il reconnaît, ou « une voix »)."""
    from .corps import conscient
    if not conscient(monde, id):
        return
    # Photographier les avis AVANT la réception des témoins. Les deux arguments
    # seront pesés ensemble, sans avantage dû à leur ordre de prononciation.
    avis = next((c for c in contenu if c.get("evenement", {}).get("type") == "avis"), None)
    presents = _avis_entendus(monde, id, avis["evenement"]["objet"], geste) if avis else {}
    opposition = (_contradiction(monde, id, avis["evenement"], presents)
                  if avis and not avis.get("dispute") else None)
    if id != "joueur" and auditeur != "joueur" and conscient(monde, auditeur):
        for c in contenu:
            if c["type"] in ("affirmation", "rumeur", "aveu"):
                retenir_dit(monde, id, auditeur, c if c["type"] == "affirmation" else c["evenement"])
    if suites and id != "joueur" and auditeur != "joueur" and conscient(monde, auditeur):
        from .relations import annoncer_suites
        annoncer_suites(monde, id, auditeur, lignes)
        annoncer_suites(monde, auditeur, id, lignes)
    from .ouie import retentir, nature
    from .paroles import _connu_du_joueur
    from .noms import texte as nommer_pour
    texte = nommer_pour(monde, texte, observateur=id)
    reponse = nommer_pour(monde, reponse, observateur=auditeur)
    diffuse = [dict(c, dispute=True) if opposition and c is avis else c for c in contenu]
    audience = _audience_connue(monde, id, diffuse, geste)
    retentir(monde, id, geste, texte=texte, cites=[auditeur, *cites],
             parole={"a": [auditeur], "contenu": diffuse})
    # Après réception : réviser une croyance pendant la parole ne doit pas
    # effacer la preuve que sa nouvelle valeur vient d'être entendue ensemble.
    _retenir_audience(monde, audience)
    if avis and avis.get("dispute"):
        for qui in presents:
            retenir_dit(monde, id, qui, avis["evenement"])
        from .ouie import saisit
        if id != "joueur" and saisit(monde, id, "joueur", geste):
            retenir_dit(monde, id, "joueur", avis["evenement"])
    if reponse and dite and conscient(monde, auditeur):
        retentir(monde, auditeur, "dire", texte=reponse, cites=[id], vers=[id])
    a = monde.joueur if id == "joueur" else monde.objets[id]
    b = monde.joueur if auditeur == "joueur" else monde.objets[auditeur]
    if id == "joueur" or auditeur == "joueur":
        lignes.append(f"{texte} {reponse}".strip())
        if opposition:
            _disputer(monde, id, avis["evenement"], avis["rang"], presents, lignes, opposition)
        return
    if a["lieu"] == monde.joueur["salle"] and monde.visible(id):
        if all(_connu_du_joueur(monde, x) for x in [id, auditeur, *cites] if x != "joueur"):
            lignes.append(f"{texte} {reponse}".strip())
        else:
            voix = " hausse la voix en parlant avec " if nature(geste) == "eclat" else " parle à voix basse avec "
            lignes.append(designer(a, debut=True) + voix + designer(b) + ".")
    elif monde.visible(id):
        lignes.append(designer(a, debut=True) + " parle avec " + designer(b) + ".")
    if opposition:
        _disputer(monde, id, avis["evenement"], avis["rang"], presents, lignes, opposition)


def _avis_entendus(monde, locuteur, salle, geste="dire"):
    """Auditeurs qui saisissent les mots, avec leur preuve avant la parole."""
    from .ouie import saisit
    from .esprits import prevision
    return {id: copy.deepcopy(prevision(monde, id, salle)) for id in sorted(pnjs(monde))
            if id != locuteur and monde.objets[id].get("profil")
            and saisit(monde, locuteur, id, geste)}


def _avis_de(monde, id, salle, c):
    from .eau import menacee
    from .esprits import poids_source
    return {"type": "avis", "objet": salle, "attribut": "menace", "valeur": menacee(monde, id, salle),
            "prevision": copy.deepcopy(c["valeur"]), "observe": c["minute"],
            "conviction": min(1, poids_source(monde, id, c) * c["confiance"])}


def _poids_dit(monde, id, locuteur, avis):
    from .esprits import poids_source
    from .voix import source_dite
    return round(poids_source(monde, id, {"source": source_dite(monde, id, locuteur)}) * avis["conviction"], 12)


def avis_exprime(monde, locuteur, salle, menace):
    """La position dite est distincte de ses preuves, joueur comme PNJ.

    Seules des observations propres étayent sa conviction. Sans estimation,
    le poids minimal est celui d'une source devinée, sans mesure inventée.
    """
    from .esprits import prevision_propre, poids_source
    c = prevision_propre(monde, locuteur)
    conviction = min(1, poids_source(monde, locuteur, c) * c["confiance"]) if c else .4
    return {"type": "avis", "objet": salle, "attribut": "menace", "valeur": menace,
            "prevision": menace, "observe": c["minute"] if c else monde.data["minutes"],
            "conviction": conviction}


def _contradiction(monde, locuteur, avis, entendus):
    """Premier auditeur qui tient un avis contraire plus étayé et peut répondre."""
    from .ouie import saisit
    for id, propre in entendus.items():
        if id == "joueur":
            continue  # Ses prises de parole appartiennent à la saisie du joueur.
        if not propre or propre.get("rang", 0) >= RANG_MAX:
            continue
        contraire = _avis_de(monde, id, avis["objet"], propre)
        if (contraire["valeur"] != avis["valeur"]
                and contraire["conviction"] > _poids_dit(monde, id, locuteur, avis)
                and not deja_dit(monde, id, locuteur, contraire)
                and saisit(monde, id, locuteur, "contredire")):
            return id, propre, contraire
    return None


def _disputer(monde, locuteur, avis, rang, entendus, lignes, opposition):
    """Un épisode fini : contradiction, réponse, éventuellement un éclat.

    Les faits dits bornent aussi les répliques, hors mémoire courte. Une parole
    de dispute ne déclenche pas une autre dispute ; ses témoins pèsent les deux
    sources ensemble, seulement s'ils en ont saisi les deux avis.
    """
    from .esprits import prevision, recevoir_prevision
    from .pnj import _chroniquer
    from .caractere import valeur, modificateur
    from .signes import emotion
    from .voix import identifie
    salle = avis["objet"]
    contradicteur, propre, contraire = opposition
    recoivent = _avis_entendus(monde, contradicteur, salle, "contredire")
    from .ouie import saisit
    if not saisit(monde, contradicteur, locuteur, "contredire"):
        return  # Une réponse reste une parole réellement entendue.
    for qui in entendus:
        retenir_dit(monde, locuteur, qui, avis)
    retenir_dit(monde, contradicteur, locuteur, contraire)
    # Le même désaccord déjà exposé ne devient pas un nouvel épisode lorsque
    # l'autre trouve plus tard son créneau de confidence.
    retenir_dit(monde, locuteur, contradicteur, avis)
    _chroniquer(monde, contradicteur, f"{_qui(monde, contradicteur)} contredit {_qui(monde, locuteur)}.", "social")
    monde.data["chronique"][-1]["dispute"] = True
    faire_entendre(monde, contradicteur, locuteur,
                   f"{_qui(monde, contradicteur)} : « Non, {phrase(monde, contraire)}. »", [salle], lignes,
                   [{"type": "rumeur", "evenement": contraire, "rang": propre.get("rang", 0), "dispute": True}],
                   geste="contredire")
    auditeurs_avis = set(entendus)
    if locuteur != "joueur":
        recevoir_prevision(monde, locuteur, contradicteur, contraire, propre.get("rang", 0))
    actuelle = prevision(monde, locuteur, salle)
    tient = actuelle and _avis_de(monde, locuteur, salle, actuelle)["valeur"] == avis["valeur"]
    if tient and locuteur != "joueur":
        auditeurs_avis.update(_avis_entendus(monde, locuteur, salle))
        faire_entendre(monde, locuteur, contradicteur,
                       f"{_qui(monde, locuteur)} : « Je maintiens : {phrase(monde, avis)}. »", [salle], lignes,
                       [{"type": "rumeur", "evenement": avis, "rang": rang, "dispute": True}])
        colere = emotion(monde, locuteur)
        if valeur(monde, locuteur, "fierte") > 60 or colere and colere["niveau"] >= 20:
            auditeurs_avis.update(_avis_entendus(monde, locuteur, salle, "disputer"))
            faire_entendre(monde, locuteur, contradicteur,
                           f"{_qui(monde, locuteur)} hausse la voix : « {phrase(monde, avis).capitalize()} ! »",
                           [salle], lignes,
                           [{"type": "rumeur", "evenement": avis, "rang": rang, "dispute": True}], geste="disputer")
            _chroniquer(monde, locuteur, f"{_qui(monde, locuteur)} hausse la voix dans la dispute.", "social")
            monde.data["chronique"][-1]["eclat"] = True
    partis = {locuteur: [], contradicteur: []}
    # Qui n'a saisi qu'un côté reçoit cet avis par la règle ordinaire ; il
    # n'assiste pas au débat et ne compte pas dans son désaveu public.
    for temoin in sorted(auditeurs_avis - set(recoivent) - {locuteur, contradicteur}):
        recevoir_prevision(monde, temoin, locuteur, avis, rang)
    for temoin in sorted(set(recoivent) - auditeurs_avis - {locuteur, contradicteur}):
        recevoir_prevision(monde, temoin, contradicteur, contraire, propre.get("rang", 0))
    for temoin in sorted(auditeurs_avis & set(recoivent) - {locuteur, contradicteur}):
        if temoin == "joueur":
            continue  # Il entend les arguments ; le moteur ne choisit pas son parti.
        _chroniquer(monde, temoin, f"{_qui(monde, temoin)} entend les deux avis de la dispute.", "social")
        monde.data["chronique"][-1]["dispute_vue"] = True
        poids = [_poids_dit(monde, temoin, x, a) for x, a in ((locuteur, avis), (contradicteur, contraire))]
        if poids[0] == poids[1]:
            jets = [monde.d20() + modificateur(monde, x, "CHA") + modificateur(monde, x, "ELO")
                    for x in (locuteur, contradicteur)]
            if jets[0] == jets[1]:
                memoriser(monde, temoin, {"type": "parole_doutee", "locuteur": locuteur, "evenement": avis})
                continue  # Égalité véritable : le témoin garde son avis ou doute.
            choix = int(jets[1] > jets[0])
        else:
            choix = int(poids[1] > poids[0])
        gagnant, retenu, r = ((locuteur, avis, rang), (contradicteur, contraire, propre.get("rang", 0)))[choix]
        issue = recevoir_prevision(monde, temoin, gagnant, retenu, r, departage=True)
        # Un constat propre plus fort/plus récent prime même les deux orateurs.
        courant = prevision(monde, temoin, salle)
        if not courant or _avis_de(monde, temoin, salle, courant)["valeur"] != retenu["valeur"]:
            continue
        if not identifie(monde, temoin, gagnant):
            continue  # Pas de relation envers l'identité d'une voix inconnue.
        _chroniquer(monde, temoin, f"{_qui(monde, temoin)} prend le parti {de(_qui(monde, gagnant))} ({issue}).", "social")
        monde.data["chronique"][-1]["parti_pris"] = True
        recoivent_parti = _avis_entendus(monde, temoin, salle)
        parti = _avis_de(monde, temoin, salle, courant)
        rang_parti = courant.get("rang", 0)
        faire_entendre(monde, temoin, gagnant,
                       f"{_qui(monde, temoin)} : « Je suis de ton avis : {phrase(monde, retenu)}. »", [salle], lignes,
                       [{"type": "rumeur", "evenement": parti, "rang": rang_parti, "dispute": True}])
        if rang_parti < RANG_MAX:
            for qui in recoivent_parti:
                if qui != "joueur":
                    recevoir_prevision(monde, qui, temoin, parti, rang_parti)
        if saisit(monde, temoin, gagnant) and identifie(monde, gagnant, temoin):
            memoriser(monde, gagnant, {"type": "parti_pris", "de": temoin})
        if saisit(monde, temoin, locuteur) and saisit(monde, temoin, contradicteur):
            partis[gagnant].append(temoin)
    if len(partis[locuteur]) != len(partis[contradicteur]):
        gagnant, perdant = ((locuteur, contradicteur) if len(partis[locuteur]) > len(partis[contradicteur])
                           else (contradicteur, locuteur))
        # Les suites sont celles d'un désaveu public, pas d'un mensonge prouvé.
        if identifie(monde, perdant, gagnant):
            memoriser(monde, perdant, {"type": "dispute_perdue", "de": gagnant, "sujet": salle})
    return


def qui_va_la(monde, id, autre, lignes):
    """``autre`` ne sait à qui est la voix d'``id`` : il demande « Qui va là ? », et ``id`` se nomme
    (« C'est … »). Chacun de sa voix : qui entend l'un et l'autre sait laquelle a dit quoi, et une
    voix qui dit son nom se nomme pour tous ceux qui en saisissent les mots (``voix.se_nommer``)."""
    from .voix import se_nommer
    a, b = _qui(monde, id), _qui(monde, autre)
    faire_entendre(monde, autre, id, f"{b} : « Qui va là ? »", [], lignes, [{"type": "qui"}])
    faire_entendre(monde, id, autre, f"{a} : « C'est {a}. »", [id], lignes, [{"type": "nom", "sujet": id}])
    se_nommer(monde, autre, id, id)


def _entendu(monde, id, auditeur, noyau, rang, lignes):
    cites = [x for x in (accuse(noyau), noyau.get("objet"), *_lieu_dit(noyau)) if x]
    faire_entendre(monde, id, auditeur, _qui(monde, id) + " glisse " + groupe_nominal(_qui(monde, auditeur, id), "à") + " que "
                   + phrase(monde, noyau, id) + ".", cites, lignes,
                   [{"type": "rumeur", "evenement": noyau, "rang": rang}])


def recevoir_statuts(monde, id, locuteur, sujet, valeurs, *, minute=None, confiance=.7):
    """Une prétention pèse comme sa voix, jamais comme le statut qu'elle revendique."""
    from .esprits import croyance, verifier_statuts, poids_source
    from .voix import source_dite
    import copy
    verifier_statuts(monde, valeurs)
    source = source_dite(monde, id, locuteur)
    ancienne = croyance(monde, id, sujet, "statuts")
    minute = monde.data["minutes"] if minute is None else minute
    nouvelle = {"source": source, "confiance": confiance}
    if ancienne and (ancienne["minute"] > minute or
                     poids_source(monde, id, ancienne) * ancienne["confiance"] >
                     poids_source(monde, id, nouvelle) * confiance):
        return "dementi"
    croire(monde, id, sujet, "statuts", copy.deepcopy(valeurs), source, confiance, minute=minute)
    return "crue"


def recevoir(monde, id, locuteur, c):
    """Ce qu'une parole transmet à ``id``, qui l'entend, destinataire ou non ; renvoie l'issue, ou
    None s'il n'y a rien à apprendre. Une affirmation se juge comme une confidence
    (``echanges.affirmer``) ; une nouvelle, comme une rumeur (``_adopter``) ; un aveu (le locuteur
    dit avoir fait un geste illicite) se croit : il ne le tient plus pour fiable et le sait de
    première main. Un nom (« C'est Corvus », « Ici ! » à son nom) se pèse (``voix.se_nommer``) ;
    une question (« Qui va là ? ») ne lui apprend rien. Ce qu'on dit de lui-même ne lui apprend rien."""
    from .corps import conscient
    if not conscient(monde, id):
        return None
    if c["type"] == "nom":
        from .voix import se_nommer
        return se_nommer(monde, id, locuteur, c["sujet"])
    if c["type"] in ("qui", "appel", "raison"):
        return None   # Une question, ou ce qu'on convient à un appel (``appel``) : rien à apprendre d'autrui.
    if c["type"] == "affirmation":
        if c["attribut"] == "statuts":
            return recevoir_statuts(monde, id, locuteur, c["sujet"], c["valeur"])
        if c["sujet"] == id:
            return None
        from .echanges import affirmer
        return affirmer(monde, locuteur, id, c["sujet"], c["attribut"], c["valeur"])
    noyau = c["evenement"]
    if noyau["type"] == "avis":
        if c.get("dispute"):
            return None  # Les deux arguments sont pesés ensemble à la fin de l'épisode.
        from .esprits import recevoir_prevision
        return recevoir_prevision(monde, id, locuteur, noyau, c["rang"])
    if c["type"] != "aveu" and accuse(noyau) == locuteur:
        return None  # Parler contre soi exige un aveu explicite, joueur comme PNJ.
    if accuse(noyau) == id or _sait(monde, id, noyau):
        return None
    if c["type"] == "aveu":
        from .voix import identifie, se_mefier
        if not identifie(monde, id, locuteur):
            # Une voix qui avoue : il s'en méfie, sans savoir à qui l'imputer ; il n'en fait pas une
            # nouvelle qui nommerait quelqu'un.
            se_mefier(monde, id, locuteur)
            return "crue"
        issue, rang = "crue", 0
    else:
        issue, rang = _adopter(monde, id, locuteur, noyau, c["rang"]), c["rang"] + 1
    if issue == "crue":
        memoriser(monde, id, {"type": "rumeur", "de": locuteur, "rang": rang, "evenement": noyau, "aveu": c["type"] == "aveu"})
        if noyau["type"] != "constat" and _proprietaire(monde, noyau) == id:
            from .deliberation import VOL, relancer
            relancer(monde, id, "biens", 30 if noyau["type"] == "absence" else VOL // 2)
    return issue


def retenir_parole(monde, id, locuteur, destinataires, texte, cites, contenu):
    """``id`` saisit les mots d'une parole qui ne lui était pas adressée : il retient qu'elle a été
    dite, et à qui ; ce qu'elle transmet le touche comme le destinataire (``recevoir``), dans la
    limite de ce que l'INT de l'un et de l'autre fait passer. Une demande ou une prière adressée
    à un autre ne l'engage à rien."""
    from .paroles import _stats_pnj, capacite_transmission
    from .pnj import _chroniquer
    from .voix import identifie
    memoriser(monde, id, {"type": "parole", "locuteur": locuteur, "a": list(destinataires), "texte": texte[:240],
                          "cites": list(cites), **({} if identifie(monde, id, locuteur) else {"voix_inconnue": True})})
    capacite = min(capacite_transmission(_stats_pnj(monde, x)["INT"]) for x in (locuteur, id))
    issues = [i for i in (recevoir(monde, id, locuteur, c) for c in contenu[:capacite]) if i]
    _retenir_audience(monde, _audience_connue(monde, locuteur, contenu, "dire", observateur=id))
    if issues:
        from .esprits import reconsiderer
        reconsiderer(monde, id)  # Ce qu'il a surpris lui apprend quelque chose.
    _chroniquer(monde, id, f"{_qui(monde, id)} surprend les mots {de(_qui(monde, locuteur))} "
                + groupe_nominal(", ".join(_qui(monde, x) for x in destinataires), "à")
                + (f" ({', '.join(issues)})" if issues else "") + ".", "ouie")


def bavarder(monde, id, lignes):
    """Confie au plus une nouvelle dans la minute courante ; True si une parole est dite."""
    from .pnj import _chroniquer
    if not monde.objets[id].get("profil"):
        return False
    if lire(monde, id)["derniere_confidence"] == monde.data["minutes"]:
        return False
    connues = list(nouvelles(monde, id))
    # Même une rumeur de constat reste moins urgente qu'une accusation.
    for souvenir, noyau, rang, source in sorted(reversed(connues), key=lambda x: x[1]["type"] in ("constat", "avis")):
        auditeur = _auditeur(monde, id, souvenir, noyau, source)
        if auditeur is None:
            continue
        if _sait(monde, auditeur, noyau):
            continue  # Limite historique : ce contrôle lit encore le savoir de l'auditeur.
        # Destinataire et témoins auditifs reçoivent le même contenu. Une accusation
        # adressée à son auteur reste une parole, sans lui apprendre une rumeur sur lui.
        # Si un tiers va contredire, le destinataire est lui aussi témoin des
        # deux positions : ne pas lui faire adopter la première avant le débat.
        debat = (noyau["type"] == "avis" and _contradiction(
            monde, id, noyau, _avis_entendus(monde, id, noyau["objet"])))
        issue = ("discuté" if debat else recevoir(
            monde, auditeur, id, {"type": "rumeur", "evenement": noyau, "rang": rang}))
        _chroniquer(monde, id, f"{_qui(monde, id)} dit {groupe_nominal(_qui(monde, auditeur), 'à')} que {phrase(monde, noyau)} ({issue or 'connu'}).",
                    "social")
        if noyau["type"] == "constat":
            monde.data["chronique"][-1]["constat_confie"] = True
        elif noyau["type"] == "avis":
            monde.data["chronique"][-1]["avis_exprime"] = True
        esprit(monde, id)["derniere_confidence"] = monde.data["minutes"]
        _entendu(monde, id, auditeur, noyau, rang, lignes)
        return True
    return False
