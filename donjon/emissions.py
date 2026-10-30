"""Registre unique des paroles : émission et audition, jamais vérité du contenu.

Les autorisations de réponse du rapport ne sont pas des paroles prononcées.
Seule leur admission avec des mots les inscrit dans ce registre.
"""
import copy
import re


MODALITES = ("croyance", "refus", "offre", "constat")


def _anciennes(monde):
    data = monde if isinstance(monde, dict) else monde.data
    anciennes = []
    for cle, locuteur in (("paroles_joueur", "joueur"), ("paroles_pnj", None)):
        for p in data.get(cle, []):
            auteur = locuteur or p["locuteur"]
            anciennes.append({**copy.deepcopy(p), "locuteur": auteur,
                "acte": "parole_joueur" if locuteur else "parole_archivee",
                "parametres": {}, "modalite": "constat",
                "evenement": {"type": "archive", "registre": cle},
                "a": list(p.get("auditeurs", [])) if locuteur else [],
                "rendu": "", "statut": "prononcee", "ordre_historique_inconnu": True})
    # Les anciennes listes ne permettent pas de retrouver l'ordre intra-tour.
    return sorted(anciennes, key=lambda p: (p.get("revision", 0), p.get("minute", 0)))


def lire(monde):
    """Lecture pure, y compris des sauvegardes antérieures au registre."""
    anciennes = _anciennes(monde)
    data = monde if isinstance(monde, dict) else monde.data
    return data.get("emissions_parole", []) + anciennes


def installer(monde):
    if "paroles_joueur" not in monde.data and "paroles_pnj" not in monde.data:
        return
    flux = lire(monde)
    for ordre, p in enumerate(flux, 1):
        if "id" not in p:
            p["id"] = ordre
            p["ordre"] = ordre
    monde.data["emissions_parole"] = flux
    monde.data.pop("paroles_joueur", None)
    monde.data.pop("paroles_pnj", None)


def pnj(monde):
    return [p for p in lire(monde) if p["locuteur"] != "joueur"]


def joueur(monde):
    """Historique d'adresse du joueur, projection de l'ancien contrat.

    Ici auditeurs désigne les interlocuteurs adressés, comme avant G15. Les
    auditeurs acoustiques sont exclusivement ceux des émissions de lire().
    Aucune de ces projections n'est conservée dans la sauvegarde.
    """
    return [{**p, "auditeur": p.get("parametres", {}).get("personnage", p.get("auditeur", "personne")),
             "auditeurs": list(p.get("a", p["auditeurs"]))}
            for p in lire(monde) if p["locuteur"] == "joueur"]


def enregistrer(monde, locuteur, *, acte, parametres, modalite, evenement,
                auditeurs, a=(), texte, rendu="", revision=None, presentation="", forme="citation"):
    """Une occurrence physique, identifiée indépendamment de ses mots et de l'auteur.

    Aucun dédoublonnage textuel : redire les mêmes mots est une autre émission.
    L'admission doit précéder tout rendu et toute sauvegarde publiée.
    """
    from .ouie import _place
    from .temps import instant
    from .corps import conscient
    if not conscient(monde, locuteur):
        return None
    installer(monde)
    flux = monde.data.setdefault("emissions_parole", [])
    ordre = len(flux) + 1
    p = {"id": ordre, "ordre": ordre, "statut": "prononcee", "locuteur": locuteur,
         "acte": acte, "parametres": copy.deepcopy(parametres), "modalite": modalite,
         "evenement": copy.deepcopy(evenement), "a": list(a),
         "auditeurs": sorted(set(auditeurs)), "texte": texte, "rendu": rendu, "forme": forme,
         "salle": _place(monde, locuteur)[0], "minute": monde.data["minutes"],
         "instant": instant(monde), "revision": monde.data["revision"] if revision is None else revision,
         **({"presentation": presentation} if presentation else {})}
    assert modalite in MODALITES and acte and evenement.get("type")
    flux.append(p)
    return p


def diffuser(monde, auteur, geste, texte, dits, contenu, a, auditeurs, source=None, cites=()):
    """Adaptateur de l'ouïe : les rôles viennent de l'opération, jamais des phrases."""
    source = source or {}
    acte = source.get("acte", "reaction_pnj" if auteur != "joueur" else "parole_joueur")
    # Un acte de dispute est transmis comme tel par la mécanique sociale.
    mots = dits if dits is not None else " ".join(re.findall(r"«\s*(.*?)\s*»", texte))
    p = enregistrer(monde, auteur, acte=acte,
        parametres=source.get("parametres", {"contenu": list(contenu), "geste": geste}),
        modalite=source.get("modalite", "croyance" if contenu else "constat"),
        evenement=source.get("evenement", {"type": "geste_vocal", "geste": geste}),
        auditeurs=auditeurs, a=a, texte=mots or texte, rendu=texte,
        revision=source.get("revision"), forme="citation" if dits is not None or mots else "discours_rapporte")
    if p and auteur != "joueur" and "joueur" in auditeurs:
        from .voix import mots as mots_percus, nom_pour_joueur
        percu = mots_percus(monde, "joueur", auteur, texte, [auteur, *cites], monde.visible(auteur), dits)
        p["rendu_public"] = (texte if percu == texte else
            f"{nom_pour_joueur(monde, auteur)} : « {percu} »" if percu else "")
    return p


def publiques(monde, flux):
    """La projection d'un événement entendu ne révèle pas ses auditeurs cachés.

    Les paramètres privés de réception ne sont pas des mots entendus. Le
    registre les conserve ; le dossier public ne transporte que leur source.
    """
    from .voix import connait_nom, designation
    connus = {"joueur"} | {id for id in monde.objets
                           if connait_nom(monde, "joueur", id) or monde.visible(id)}
    resultat = []
    for p in flux:
        if p.get("statut") == "a_formuler":
            resultat.append({**copy.deepcopy(p), "locuteur": designation(monde, p["locuteur"])})
            continue
        if p["locuteur"] != "joueur" and "joueur" not in p["auditeurs"]:
            continue
        if p.get("forme") == "discours_rapporte" and not p.get("rendu_public"):
            continue
        resultat.append({**copy.deepcopy(p),
            "locuteur": designation(monde, p["locuteur"]) if p["locuteur"] != "joueur" else "joueur",
            "a": [a for a in p.get("a", []) if a in connus],
            "auditeurs": [a for a in p["auditeurs"] if a in connus],
            "rendu": p.get("rendu_public", ""),
            "parametres": {}, "evenement": {"type": p["evenement"]["type"], "emission": p.get("id"),
                **({"faits": copy.deepcopy(p["evenement"].get("faits", []))}
                   if p["acte"] in ("reponse_comptable", "reponse_information") else {})}})
    return resultat


def entendues(rapport):
    return [p for p in rapport.get("emissions", [])
            if p.get("statut") == "prononcee" and "joueur" in p.get("auditeurs", [])]


def reponses(rapport):
    return [p for p in rapport.get("emissions", [])
            if p.get("statut") == "a_formuler" and p.get("acte") == "reponse_corvus"]


def memes_mots(a, b):
    """Égalité des mots enregistrés, aux seules variantes typographiques près."""
    import unicodedata
    def typo(s):
        return " ".join(unicodedata.normalize("NFC", s).replace("’", "'").split())
    return typo(a) == typo(b)


def reprise(rapport, locuteur, citation):
    """Une citation d'émission courante ne donne aucun nouveau droit de parole."""
    return next((p for p in entendues(rapport)
                 if p["locuteur"] == locuteur and p.get("forme", "citation") == "citation"
                 and memes_mots(p["texte"], citation)), None)


def faits(rapport):
    """Projection de compatibilité du rapport, sans liste de phrases concurrente."""
    resultat = []
    for p in rapport.get("emissions", []):
        if p.get("statut") == "a_formuler":
            resultat.extend(p["evenement"].get("faits", []))
        elif "joueur" in p.get("auditeurs", []) and p.get("rendu_public", p.get("rendu")):
            if p["acte"] in ("reponse_comptable", "reponse_information"):
                resultat.extend(p["evenement"].get("faits", []))
            resultat.append(p.get("rendu_public", p["rendu"]))
    return resultat


def verifier(monde):
    for ordre, p in enumerate(monde.data.get("emissions_parole", []), 1):
        assert p["id"] == p["ordre"] == ordre, "Ordre des émissions invalide"
        assert p["statut"] == "prononcee" and p["modalite"] in MODALITES, "Émission invalide"
        assert p["locuteur"] == "joueur" or p["locuteur"] in monde.objets, "Auteur de parole invalide"
        assert isinstance(p["texte"], str) and p["texte"].strip(), "Parole vide"
        assert p["acte"] and isinstance(p["parametres"], dict) and p["evenement"].get("type"), "Source de parole invalide"
        assert isinstance(p["auditeurs"], list) and all(
            a == "joueur" or a in monde.objets for a in p["auditeurs"]), "Auditeurs invalides"
        assert 0 <= p["revision"] <= monde.data["revision"], "Révision de parole invalide"
