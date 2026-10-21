"""Faits narratifs typés, validés et appliqués sur une copie du monde."""

import copy
import math

from .francais import designer, relation_physique
from .geometrie import placer
from .monde import ErreurMonde, normaliser, objet, reference_exacte
from .perception import eclairage
from .refus import liste
from .matiere import (SCHEMA as SCHEMA_PHYSIQUE, SCHEMA_CONTENU, appliquer as appliquer_physique,
                      decrire as decrire_physique, decrire_contenu, valider as valider_physique,
                      valider_contenu)
from .capacites_objet import (SCHEMA as SCHEMA_CAPACITES,
                             CAPACITES_REVUE, absence as absence_capacite,
                             aptitude_coupe,
                             empreinte as empreinte_capacite,
                             resume_constats,
                             noms as noms_capacites, proprietes as proprietes_capacites,
                             statut as statut_capacite)


TYPES = ("detail", "inscription", "parole", "objet", "evolution", "qualification")
SCHEMA_AJOUT_SIMPLE = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "type": {"type": "string", "enum": ["detail", "inscription", "parole"]},
        "ancrage": {"type": "string"}, "nom": {"type": "string"},
        "genre": {"type": "string", "enum": ["", "m", "f"]},
        "texte": {"type": "string"},
    },
    "required": ["type", "ancrage", "nom", "genre", "texte"],
}
SCHEMA_AJOUT_OBJET = {
    "type": "object", "additionalProperties": False,
    "properties": {
        **SCHEMA_AJOUT_SIMPLE["properties"],
        "type": {"type": "string", "enum": ["objet"]},
        "materiau": {"type": "string"},
        "masse": {"type": "number"},
        "mobile": {"type": "boolean"},
        "relation": {"type": "string", "enum": ["pose", "fixe", "contenu"]},
        "capacites": SCHEMA_CAPACITES,
    },
    "required": ["type", "ancrage", "nom", "genre", "texte", "materiau", "masse", "mobile", "relation", "capacites"],
}
SCHEMA_AJOUT_EVOLUTION = {
    "type": "object", "additionalProperties": False,
    "properties": {"type": {"type": "string", "enum": ["evolution"]},
                   "ancrage": {"type": "string"}},
    "required": ["type", "ancrage"],
}
SCHEMA_CAPACITES_EXISTANTES = copy.deepcopy(SCHEMA_CAPACITES)
SCHEMA_CAPACITES_EXISTANTES["items"]["anyOf"] = [
    option for option in SCHEMA_CAPACITES_EXISTANTES["items"]["anyOf"]
    if "tranchable" not in option["properties"]["nature"]["enum"]]
SCHEMA_AJOUT_QUALIFICATION = {
    "type": "object", "additionalProperties": False,
    "properties": {"type": {"type": "string", "enum": ["qualification"]},
                   "ancrage": {"type": "string"}, "capacites": SCHEMA_CAPACITES_EXISTANTES},
    "required": ["type", "ancrage", "capacites"],
}
SCHEMA_AJOUT_EXCLUSION = {
    "type": "object", "additionalProperties": False,
    "properties": {"type": {"type": "string", "enum": ["qualification"]},
                   "ancrage": {"type": "string"},
                   "ecartees": {"type": "array", "minItems": 1,
                                 "maxItems": len(CAPACITES_REVUE),
                                 "items": {"type": "string", "enum": [
                                     c for c in CAPACITES_REVUE if c != "tranchable"]}}},
    "required": ["type", "ancrage", "ecartees"],
}
SCHEMA_AJOUT_COUPE = {
    "type": "object", "additionalProperties": False,
    "properties": {"type": {"type": "string", "enum": ["qualification"]},
                   "ancrage": {"type": "string"}, "moyen": {"type": "string"},
                   "coupe_possible": {"type": "boolean"}},
    "required": ["type", "ancrage", "moyen", "coupe_possible"],
}
SCHEMA_AJOUT_PHYSIQUE = {
    "type": "object", "additionalProperties": False,
    "properties": {"type": {"type": "string", "enum": ["qualification"]},
                   "ancrage": {"type": "string"}, "physique": SCHEMA_PHYSIQUE},
    "required": ["type", "ancrage", "physique"],
}
SCHEMA_AJOUT_CONTENU = {
    "type": "object", "additionalProperties": False,
    "properties": {"type": {"type": "string", "enum": ["qualification"]},
                   "ancrage": {"type": "string"}, "contenu": SCHEMA_CONTENU},
    "required": ["type", "ancrage", "contenu"],
}
SCHEMA_FAITS = {
    "type": "object", "additionalProperties": False,
    "properties": {"ajouts": {"type": "array", "minItems": 1, "maxItems": 3,
        "items": {"anyOf": [SCHEMA_AJOUT_SIMPLE, SCHEMA_AJOUT_OBJET,
                            SCHEMA_AJOUT_EVOLUTION, SCHEMA_AJOUT_QUALIFICATION,
                            SCHEMA_AJOUT_EXCLUSION, SCHEMA_AJOUT_COUPE, SCHEMA_AJOUT_PHYSIQUE,
                            SCHEMA_AJOUT_CONTENU]}}},
    "required": ["ajouts"],
}


def supports(monde):
    """Supports que le joueur peut effectivement détailler maintenant."""
    if eclairage(monde)["niveau"] < 2:
        return {}
    from .spatial import proche
    return {id: {"nom": o["nom"], "salle": monde.joueur["salle"],
                 "relations": (["pose"] if o.get("support_pose") and o["type"] != "contenant" else [])
                              + (["fixe"] if not o["mobile"] and o["type"] != "contenant"
                                 and (o.get("support_pose") or o.get("ancrage_carte")) else [])
                              + (["contenu"] if o["type"] == "contenant" and o.get("ouverte") else [])}
            for id, o in monde.objets.items()
            if o["type"] not in ("personnage", "partie_corps", "motif", "detail")
            and o["integrite"] > 0
            and monde.visible(id)
            and (not monde.data.get("mode_cases") or proche(monde, id))}


def inobservable(monde, id):
    """Pourquoi ``id`` ne peut pas recevoir de détail maintenant, en une seule cause."""
    if eclairage(monde)["niveau"] < 2:
        return "Il fait trop sombre pour en distinguer les détails."
    o = monde.objets.get(id)
    if o is None or not monde.visible(id):
        return "Tu ne vois pas ce support d'ici."
    if o["type"] in ("personnage", "partie_corps", "motif", "detail") or o["integrite"] <= 0:
        return "On ne peut pas y ajouter de détail."
    return "Tu es trop loin pour en distinguer les détails."


def catalogue(monde):
    from .dialogues import interlocuteurs
    from .transitions_scenario import disponibles
    accessibles = supports(monde)
    return {"supports": accessibles,
            "qualifiables": {id: {"nom": monde.objets[id]["nom"],
                                  "materiau": monde.objets[id]["materiau"],
                                  "description": monde.objets[id].get("description_visuelle", ""),
                                  "integrite": monde.objets[id]["integrite"],
                                  "maximum": monde.objets[id]["maximum"],
                                  "capacites": {capacite: statut_capacite(monde.objets[id], capacite)
                                                for capacite in CAPACITES_REVUE},
                                  "constats": resume_constats(monde.objets[id], monde.objets),
                                  "masse": monde.objets[id]["masse"],
                                  "physique": monde.objets[id].get("physique", "inconnue"),
                                  "contenu": monde.objets[id].get("contenu", "inconnu")}
                             for id in accessibles if monde.objets[id].get("masse", 0) > 0},
            "locuteurs": {
        id: {"nom": p["nom"]} for id, p in interlocuteurs(monde).items()},
        "evolutions": disponibles(monde),
        **({"potentiel_invention": potentiel(monde)} if potentiel(monde) is not None else {})}


# Longueur maximale d'une parole de PNJ enregistrée, quelle que soit sa voie d'entrée.
LONGUEUR_PAROLE = 800


def potentiel(monde, salle=None):
    """Budget d'invention déclaré par le scénario pour ce lieu ; None si le lieu n'en fixe pas.

    Un objet créé par le MJ consomme définitivement une place du lieu où il apparaît :
    le déplacer ensuite ne libère rien. Les capacités permises bornent aussi les
    propriétés ajoutées à un objet existant de ce lieu.
    """
    salle = salle or monde.joueur["salle"]
    budget = monde.data["salles"][salle].get("potentiel_invention")
    if budget is None:
        return None
    return {**budget, "objets_restants": max(0, budget["objets_max"]
                                              - monde.data.get("inventions", {}).get(salle, 0))}


def _respecter_potentiel(monde, capacites, masse=None, nouvel_objet=False):
    budget = potentiel(monde)
    if budget is None:
        return
    if nouvel_objet and not budget["objets_restants"]:
        raise ErreurMonde("Ce lieu ne recèle plus rien de nouveau : ce qui s'y trouve est déjà connu.",
                          "potentiel_invention épuisé : plus aucun type objet ici ; un detail sans propriété reste possible.")
    if masse is not None and masse > budget["masse_max_kg"]:
        raise ErreurMonde("Un objet de plus de " + str(budget["masse_max_kg"]).replace(".", ",")
                          + " kg ne peut pas apparaître ici.",
                          f"masse au plus {budget['masse_max_kg']} (reçu {masse}).")
    interdites = sorted(set(noms_capacites(capacites)) - set(budget["capacites"]))
    if interdites:
        raise ErreurMonde("Ce lieu ne peut pas fournir d'objet doté de : " + ", ".join(interdites) + ".",
                          f"capacites permises ici : {', '.join(budget['capacites']) or 'aucune'} ; retire "
                          f"{', '.join(interdites)}.")


def _texte(texte, maximum):
    return (isinstance(texte, str) and 3 <= len(texte.strip()) <= maximum
            and all(ord(c) >= 32 for c in texte))


def _outil_de_coupe(monde, cible, identifiant):
    resolution = reference_exacte(monde.objets.values(), identifiant)
    moyen = monde.objets.get(resolution)
    if (not moyen or resolution == cible or moyen.get("lieu") != "joueur"
            or moyen.get("integrite", 0) <= 0
            or statut_capacite(moyen, "couper") != "etablie"):
        outils = sorted(i for i, o in monde.objets.items() if o.get("lieu") == "joueur" and i != cible
                        and o.get("integrite", 0) > 0 and statut_capacite(o, "couper") == "etablie")
        raise ErreurMonde("La qualification de coupe exige un outil possédé et utilisable.",
                          f"moyen : un outil tranchant en main, parmi {liste(outils)} (reçu « {identifiant} »).")
    return moyen


def preparer_faits(monde, proposition, revision=None):
    """Valide plusieurs faits liés et les applique atomiquement sur une copie."""
    if revision is not None and revision != monde.data["revision"]:
        raise ErreurMonde("Le monde a changé avant l'enregistrement des faits.", "re-propose à partir des faits actuels.")
    if not isinstance(proposition, dict) or set(proposition) != {"ajouts"}:
        recus = sorted(proposition) if isinstance(proposition, dict) else type(proposition).__name__
        raise ErreurMonde("Faits narratifs mal formés.", f"etablir_faits a exactement le champ ajouts ; reçu : {recus}.")
    ajouts = proposition["ajouts"]
    if not isinstance(ajouts, list) or not 1 <= len(ajouts) <= 3:
        raise ErreurMonde("Nombre de faits narratifs invalide.", "ajouts : une liste de 1 à 3 faits.")
    autorises = catalogue(monde)
    travail = monde.copier()
    rendus = []
    etablis = []
    for index, ajout in enumerate(ajouts, 1):
        def refus(message, attendu):
            nature = ajout.get("type", "?") if isinstance(ajout, dict) else "?"
            return ErreurMonde(message, f"ajout {index} ({nature}) : {attendu}")
        if not isinstance(ajout, dict) or ajout.get("type") not in TYPES:
            recu = ajout.get("type") if isinstance(ajout, dict) else type(ajout).__name__
            raise refus("Fait narratif mal formé.", f"type parmi {', '.join(TYPES)} (reçu « {recu} »).")
        nature = ajout["type"]
        champs = ({"type", "ancrage"} if nature == "evolution" else
                  {"type", "ancrage", "moyen", "coupe_possible"}
                  if nature == "qualification" and "coupe_possible" in ajout else
                  {"type", "ancrage", "physique"}
                  if nature == "qualification" and "physique" in ajout else
                  {"type", "ancrage", "contenu"}
                  if nature == "qualification" and "contenu" in ajout else
                  {"type", "ancrage", "ecartees"}
                  if nature == "qualification" and "ecartees" in ajout else
                  {"type", "ancrage", "capacites"} if nature == "qualification" else
                  {"type", "ancrage", "nom", "genre", "texte", "materiau", "masse", "mobile", "relation", "capacites"}
                  if nature == "objet" else
                  {"type", "ancrage", "nom", "genre", "texte"})
        if set(ajout) != champs or not isinstance(ajout["ancrage"], str):
            raise refus("Fait narratif mal formé.",
                        f"champs exacts {', '.join(sorted(champs))} ; reçu : {', '.join(sorted(ajout))}.")
        ancrage = ajout["ancrage"]
        if nature == "evolution":
            from .transitions_scenario import preparer as preparer_transition
            travail, annonce = preparer_transition(travail, ancrage)
            rendus.append(annonce)
            etablis.append({"type": nature, "transition": ancrage})
            continue
        ancrage = reference_exacte(travail.objets.values(), ancrage) or ancrage
        if nature == "qualification":
            if ancrage not in autorises["qualifiables"]:
                # Une cause par refus : la lumière, la vue ou la distance, comme pour un détail ; un objet
                # que l'on voit de près sans masse (un mur, un sol) ne se qualifie pas.
                raise refus(inobservable(monde, ancrage) if ancrage not in autorises["supports"]
                            else "Cet objet ne peut pas être qualifié.",
                            f"ancrage « {ancrage} » : un objet qualifiable d'ici, parmi "
                            f"{liste(sorted(autorises['qualifiables']))} ; ne le remplace pas par un autre : "
                            "réponds en dialogue avec ce que Corvus en perçoit d'ici, sans détail nouveau.")
            cible = travail.objets[ancrage]
            if "physique" in ajout:
                # Le MJ dit ce qu'est concrètement l'objet ; le moteur vérifie la masse et déduit le reste.
                if "physique" in cible:
                    raise refus("Cet objet est déjà décrit.",
                                f"{ancrage} a déjà sa description physique ({decrire_physique(cible)}) : "
                                "ne la redonne pas ; re-propose directement l'action.")
                try:
                    physique = valider_physique(cible, ajout["physique"])
                except ErreurMonde as exc:
                    raise refus(str(exc), exc.attendu) from None
                appliquer_physique(cible, physique)
                rendus.append(designer(cible, debut=True) + " : " + decrire_physique(cible) + ".")
                etablis.append({"type": nature, "objet": ancrage, "physique": physique})
                continue
            if "contenu" in ajout:
                if "contenu" in cible:
                    raise refus("Ce contenu est déjà établi.",
                                f"{ancrage} : {decrire_contenu(cible)} ; ne le redonne pas.")
                try:
                    cible["contenu"] = valider_contenu(cible, ajout["contenu"])
                except ErreurMonde as exc:
                    raise refus(str(exc), exc.attendu) from None
                rendus.append(decrire_contenu(cible) + ".")
                etablis.append({"type": nature, "objet": ancrage, "contenu": cible["contenu"]})
                continue
            if "coupe_possible" in ajout:
                if type(ajout["coupe_possible"]) is not bool:
                    raise refus("Jugement de coupe mal formé.", f"coupe_possible : true ou false (reçu {ajout['coupe_possible']!r}).")
                moyen = _outil_de_coupe(travail, ancrage, ajout["moyen"])
                if statut_capacite(cible, "tranchable", moyen) != "inconnue":
                    raise refus("La coupe avec cet outil est déjà établie.",
                                f"la coupe de {ancrage} par {moyen['id']} est déjà {statut_capacite(cible, 'tranchable', moyen)} : "
                                "ne la qualifie plus ; re-propose directement l'action.")
                positive = ajout["coupe_possible"]
                observation = {
                    "capacite": "tranchable", "issue": "etablie" if positive else "ecartee",
                    "empreinte": empreinte_capacite(cible, usure=not positive),
                    "moyen_nom": designer(moyen), "moyen_id": moyen["id"],
                    "empreinte_moyen": empreinte_capacite(moyen, usure=not positive),
                    "puissance_observee": moyen.get("puissance", 0),
                }
                cible.setdefault("constats_capacites", []).append(observation)
                rendus.append((aptitude_coupe(cible, observation) if positive else
                               absence_capacite(cible, "tranchable", observation)) + ".")
                etablis.append({"type": nature, "objet": ancrage,
                                "coupe_possible": positive, "moyen": moyen["id"]})
                continue
            if "ecartees" in ajout:
                exclusions = ajout["ecartees"]
                if (not isinstance(exclusions, list) or not 1 <= len(exclusions) <= len(CAPACITES_REVUE)
                        or any(not isinstance(capacite, str) or capacite not in CAPACITES_REVUE
                               or capacite == "tranchable"
                               for capacite in exclusions)
                        or len(exclusions) != len(set(exclusions))):
                    raise refus("Constat physique mal formé.",
                                f"ecartees : liste sans doublon parmi {', '.join(c for c in CAPACITES_REVUE if c != 'tranchable')} "
                                "(la coupe se qualifie avec moyen et coupe_possible).")
                connues = [c for c in exclusions if statut_capacite(cible, c) != "inconnue"]
                if connues:
                    raise refus("Une capacité connue ne peut pas être écartée à nouveau.",
                                f"{', '.join(connues)} déjà établie(s) ou écartée(s) pour {ancrage} : retire-les de ecartees.")
                for capacite in exclusions:
                    observation = {"capacite": capacite, "issue": "ecartee",
                                   "empreinte": empreinte_capacite(cible),
                                   "moyen_nom": "", "moyen_id": "", "empreinte_moyen": "",
                                   "puissance_observee": 0}
                    cible.setdefault("constats_capacites", []).append(observation)
                    rendus.append(absence_capacite(cible, capacite, observation) + ".")
                etablis.append({"type": nature, "objet": ancrage,
                                "constats": list(exclusions)})
                continue
            _respecter_potentiel(travail, ajout["capacites"])
            nouvelles = proprietes_capacites(ajout["capacites"], cible["masse"], cible["mobile"])
            if not nouvelles:
                raise refus("Aucune propriété physique proposée.", "capacites : au moins une capacité renseignée.")
            if "tranchable" in noms_capacites(ajout["capacites"]):
                raise refus("La coupe d'un objet existant se qualifie avec un outil précis.",
                            "pour la coupe : qualification avec moyen (outil en main) et coupe_possible, sans capacites.")
            for capacite in noms_capacites(ajout["capacites"]):
                if statut_capacite(cible, capacite) == "ecartee":
                    raise refus("Une capacité écartée ne peut pas être rétablie sans changement physique.",
                                f"{capacite} est écartée pour {ancrage} : retire-la.")
            conflits = (set(nouvelles) & set(cible)) - {"integrite", "maximum"}
            if "maximum" in nouvelles and nouvelles["maximum"] != cible["maximum"]:
                raise refus("La ténacité proposée doit reprendre le maximum établi : "
                            + str(cible["maximum"]) + ".", f"tenacite = {cible['maximum']}.")
            if conflits:
                raise refus("Une propriété physique établie ne peut pas être réécrite.",
                            f"déjà établi pour {ancrage} : {', '.join(sorted(conflits))} ; retire ces capacités.")
            if "integrite" in nouvelles:
                nouvelles["integrite"] = cible["integrite"]
            cible.update(nouvelles)
            rendus.append("Tu précises les propriétés de " + designer(cible) + ".")
            etablis.append({"type": nature, "objet": ancrage,
                            "proprietes": sorted(nouvelles)})
            continue
        if any(not isinstance(ajout[k], str) for k in ("nom", "genre", "texte")):
            raise refus("Fait narratif mal formé.", "nom, genre et texte : des chaînes.")
        nom, genre, texte = ajout["nom"].strip(), ajout["genre"], ajout["texte"].strip()
        if not _texte(texte, 300):
            raise refus("Type ou texte du fait narratif invalide.", "texte : 3 à 300 caractères, sans saut de ligne.")
        if nature == "parole":
            if ancrage not in autorises["locuteurs"]:
                raise refus("Cette parole ne peut pas être attribuée à ce personnage ici.",
                            f"ancrage : un personnage présent, parmi {liste(sorted(autorises['locuteurs']))}.")
            if nom or genre or len(texte) > 240:
                raise refus("Cette parole ne peut pas être attribuée à ce personnage ici.",
                            "parole : nom et genre vides, texte de 240 caractères au plus.")
            from .ouie import saisissent
            from .voix import reel as _reel
            source = travail.joueur["salle"]
            # Qui en saisit les mots, par l'ouïe commune ; le joueur, à qui elle s'adresse.
            entendants = sorted(saisissent(travail, _reel(travail, ancrage)))
            if "joueur" not in entendants:
                entendants.append("joueur")
            from .voix import nom_pour_joueur, reel
            nom = nom_pour_joueur(travail, reel(travail, ancrage), court=False)
            # Le MJ désigne une voix inconnue comme le joueur (voix_<n>) : le moteur sait qui parle.
            designe, ancrage = ancrage, reel(travail, ancrage)
            if travail.visible(ancrage):
                from .voix import connaitre
                connaitre(travail, "joueur", ancrage)  # Il le voit parler : il saura reconnaître sa voix.
            evenement = {"locuteur": ancrage, "texte": texte, "salle": source,
                         "minute": travail.data["minutes"], "auditeurs": entendants,
                         "revision": monde.data["revision"] + 1}
            travail.data.setdefault("paroles_pnj", []).append(evenement)
            rendus.append(nom[0].upper() + nom[1:] + " dit : « " + texte + " ».")
            etablis.append({"type": nature, "locuteur": designe})
            continue
        if ancrage not in autorises["supports"]:
            # Une cause par refus : la lumière, la vue ou la distance. Le support visé reste celui
            # que le joueur demande : un autre support ne répondrait pas à sa question.
            raise refus(inobservable(monde, ancrage),
                        f"ancrage « {ancrage} » non observable de près ; ne le remplace pas par un autre support : "
                        "réponds en dialogue avec ce que Corvus en perçoit d'ici, sans détail nouveau. Supports "
                        f"observables : {liste(sorted(autorises['supports']))}.")
        support = travail.objets[ancrage]
        if nature == "inscription":
            if any(e["lieu"] == ancrage and e.get("inscription") for e in travail.objets.values()):
                raise refus("Une inscription est déjà établie sur ce support.",
                            f"{ancrage} porte déjà une inscription : lire, ou un autre support.")
            if nom or genre or len(texte) > 240:
                raise refus("La forme de cette inscription est invalide.",
                            "inscription : nom et genre vides, texte de 240 caractères au plus.")
            nom_support = designer(support)
            detail = objet("", "inscription sur " + nom_support, "motif", ancrage,
                           aliases=["inscription", "gravure", "gravure sur " + nom_support],
                           genre="f", materiau=support["materiau"],
                           motif="Des signes sont gravés sur " + nom_support + ".",
                           inscription=texte)
            rendus.append("Tu remarques une inscription gravée sur " + nom_support
                          + " : « " + texte + " ».")
        else:
            if (genre not in ("m", "f") or not _texte(nom, 60)
                    or any(normaliser(e["nom"]) == normaliser(nom)
                                             for e in travail.enfants(ancrage))):
                raise refus("Cet élément n'a pas de nom distinct sur son support.",
                            "genre m ou f ; nom de 3 à 60 caractères, différent des éléments déjà sur "
                            f"{ancrage} ({liste(e['nom'] for e in travail.enfants(ancrage))}).")
            if nature == "objet":
                masse, mobile, materiau, relation = (ajout[k] for k in ("masse", "mobile", "materiau", "relation"))
                if (type(masse) not in (int, float) or not math.isfinite(masse)
                        or not 0 <= masse <= 500 or type(mobile) is not bool
                        or (mobile and masse <= 0) or not isinstance(materiau, str)
                        or not 1 <= len(materiau.strip()) <= 40
                        or relation not in ("pose", "fixe", "contenu")
                        or relation not in autorises["supports"][ancrage]["relations"]
                        or (relation == "contenu" and
                            (support["type"] != "contenant" or not support.get("ouverte")))):
                    relations = autorises["supports"][ancrage]["relations"]
                    raise refus("Propriétés physiques de l'objet invalides.",
                                f"masse 0 à 500 (> 0 si mobile), mobile booléen, materiau 1 à 40 caractères, relation "
                                f"parmi {', '.join(relations)} pour {ancrage}"
                                + (" (contenu seulement dans un contenant ouvert)" if "contenu" in relations else "")
                                + f" ; reçu masse {masse!r}, mobile {mobile!r}, relation {relation!r}.")
                _respecter_potentiel(travail, ajout["capacites"], masse, nouvel_objet=True)
                salle = travail.joueur["salle"]
                if potentiel(travail) is not None:
                    inventions = travail.data.setdefault("inventions", {})
                    inventions[salle] = inventions.get(salle, 0) + 1
                detail = objet("", nom, "accessoire", ancrage, aliases=[nom],
                               genre=genre, materiau=materiau.strip(), masse=masse,
                               mobile=mobile, description_visuelle=texte,
                               relation_support=relation,
                               **proprietes_capacites(ajout["capacites"], masse, mobile),
                               **({"attache": True, "amovible": mobile} if relation == "fixe" else {}))
            else:
                detail = objet("", nom, "detail", ancrage, aliases=[nom],
                               genre=genre, materiau="", description_visuelle=texte)
            lien = (relation_physique(detail, support, ajout["relation"]) if nature == "objet"
                    else "sur " + designer(support))
            rendus.append("Tu remarques " + designer(detail, "indefini") + " " + lien
                          + ". " + texte)
        id = f'fait_{monde.data["revision"] + 1}_{index}'
        if id in travail.objets:
            raise refus("Ce détail existe déjà.", "re-propose à partir des faits actuels.")
        detail.update(id=id, origine_description="MJ", scene_detail=True)
        if nature != "objet":
            detail["detail_local"] = True
        else:
            detail["cartographier"] = True
            if not support["mobile"]:
                from .spatial import position_cible
                position = position_cible(travail, ancrage)
                if position is None:
                    raise refus("Le support n'a pas de position observable.",
                                f"{ancrage} n'est pas sur le plan : choisis un autre support, ou un detail.")
                placer(detail, travail.joueur["salle"], position)
                detail["position_autonome"] = True
                detail["ancrage_initial"] = ancrage
                if ajout["relation"] == "fixe" and support.get("ancrage_carte"):
                    detail["ancrage_carte"] = list(support["ancrage_carte"])
        travail.objets[id] = detail
        travail.data.setdefault("faits_vus", []).append({
            "objet": id, "nom": detail["nom"], "salle": travail.joueur["salle"],
            "description": detail.get("description_visuelle", ""),
            "inscription": detail.get("inscription", "")})
        etablis.append({"type": nature, "support": ancrage, "objet": id})
    travail.data["revision"] += 1
    travail.data.setdefault("enrichissements", []).append({
        "revision": travail.data["revision"], "origine": "MJ",
        "faits": copy.deepcopy(etablis)})
    travail.verifier()
    return travail, " ".join(rendus), etablis


def verifier(monde):
    from .geometrie import cases
    for salle, nombre in monde.data.get("inventions", {}).items():
        budget = monde.data["salles"].get(salle, {}).get("potentiel_invention")
        assert (budget is not None and type(nombre) is int
                and 0 < nombre <= budget["objets_max"]), "Budget d'invention dépassé"
    for salle in monde.data["salles"].values():
        budget = salle.get("potentiel_invention")
        assert budget is None or (
            isinstance(budget, dict) and set(budget) == {"objets_max", "masse_max_kg", "capacites"}
            and type(budget["objets_max"]) is int and budget["objets_max"] >= 0
            and type(budget["masse_max_kg"]) in (int, float) and budget["masse_max_kg"] >= 0
            and isinstance(budget["capacites"], list)
            and set(budget["capacites"]) <= set(CAPACITES_REVUE)), "Potentiel d'invention mal formé"
    for o in monde.objets.values():
        if o.get("relation_support"):
            relation = o["relation_support"]
            assert relation in ("pose", "fixe", "contenu"), "Relation physique invalide"
            parent = monde.objets.get(o["lieu"])
            assert ((relation == "fixe") == bool(o.get("attache"))), "Fixation incohérente"
            if relation == "fixe":
                assert (parent is not None and not parent["mobile"]
                        and parent["type"] != "contenant"
                        and o.get("amovible") == o["mobile"]
                        and o.get("ancrage_carte") == parent.get("ancrage_carte")), "Fixation incohérente"
            if relation == "pose" and parent is not None:
                assert (parent.get("support_pose") is True
                        and parent["type"] != "contenant"), "Support de pose invalide"
            if relation == "contenu":
                assert parent is not None and parent["type"] == "contenant", "Contenance incohérente"
        if o.get("position_autonome") and o["lieu"] == o.get("ancrage_initial"):
            support = monde.objets.get(o["lieu"])
            salle = o.get("position_salle")
            assert (support is not None and not support["mobile"]
                    and salle in monde.data["salles"]
                    and tuple(o.get("position", ())) in cases(monde.data["salles"][salle])
                    and o.get("cartographier") is True), "Position autonome invalide"
    assert (isinstance(monde.data.get("faits_vus", []), list)
            and all(isinstance(s, dict)
                    and set(s) == {"objet", "nom", "salle", "description", "inscription"}
                    and s["salle"] in monde.data["salles"]
                    and all(isinstance(s[k], str) for k in s)
                    for s in monde.data.get("faits_vus", []))), "Souvenirs de faits invalides"
    for parole in monde.data.get("paroles_pnj", []):
        assert (set(parole) == {"locuteur", "texte", "salle", "minute", "auditeurs", "revision"}
                and parole["locuteur"] in monde.objets
                and monde.objets[parole["locuteur"]]["type"] == "personnage"
                and parole["salle"] in monde.data["salles"]
                and _texte(parole["texte"], LONGUEUR_PAROLE)
                and isinstance(parole["auditeurs"], list)
                and all(a == "joueur" or a in monde.objets for a in parole["auditeurs"])
                and type(parole["minute"]) is int and parole["minute"] >= 0
                and type(parole["revision"]) is int
                and 0 <= parole["revision"] <= monde.data["revision"]), "Parole de PNJ invalide"
