"""Ordonnancement déterministe des faits et routage des préfixes pour le cache KV."""

ORDRE_AVANT_OBJETS = (
    "salle",
    "ambiance_etablie",
    "joueur",
    "perception",
    "mode_cases",
    "personnages_connus",
    "noms_entendus",
    "souvenirs_faits",
    "engagements",
    "souvenirs_personnages",
    "missions_discutables",
    "scenario",
    "souvenirs_visuels",
    "proposition_en_attente",
    "espace",
    "signes_percus",
    "impressions",
    "bruit",
    "minutes",
)

ORDRE_APRES_OBJETS = (
    "descriptions_a_completer",
    "connaissances_a_completer",
    "profil_joueur_a_completer",
    "faits_narratifs_proposables",
    "atelier",
    "franchissements",
    "passages_obstacles",
    "derniere_tentative",
    "improvisation",
    "expression_joueur",
    "comptes",
    "connaissances_pnj",
    "interlocuteurs",
    "esprits_interlocuteurs",
    "paroles_entendues",
    "evenements_recents",
    "echanges_passes",
    "parole_prevue",
    "ambiance_ciblee",
    "reperes_demandes",
    "attestations",
    "revision",
    "conversation_validee",
    "resultat_resolu",
    "retour_moteur",
    "effets_prevus",
)

ORDRE_ENTREE = (
    "faits",
    "conversation",
    "message",
    "segments",
    "designations",
    "nature",
    "retour_forme",
    "controle_narratif",
    "consigne_revision",
)

SLOTS_VOIE = {
    "interpreter": 0,
    "raconter": 1,
    "raconter_resultat": 1,
    "auditer_narration": 2,
    "auditer_action": 3,
    "auditer_portee": 3,
    "auditer_capacites": 3,
}


def _ordonner_esprit(esprit):
    if not isinstance(esprit, dict):
        return esprit
    fin = ("noms_pour_repliques", "nom_du_locuteur")
    ordonne = {cle: valeur for cle, valeur in esprit.items() if cle not in fin}
    for cle in fin:
        if cle in esprit:
            ordonne[cle] = esprit[cle]
    return ordonne


def ordonner_faits(faits):
    """Range les clés de ``faits`` des plus stables (scène, objets, catalogues) aux plus volatiles
    (intention du tour, révision, retour moteur) afin que le préfixe JSON soit partagé entre tours,
    relances et phases d'audit."""
    if not isinstance(faits, dict):
        return faits
    ordonne = {}
    for cle in ORDRE_AVANT_OBJETS:
        if cle in faits:
            ordonne[cle] = faits[cle]
    for cle in sorted(c for c in faits if isinstance(c, str) and c.startswith("objet:")):
        ordonne[cle] = faits[cle]
    for cle in ORDRE_APRES_OBJETS:
        if cle in faits:
            valeur = faits[cle]
            if cle == "esprits_interlocuteurs" and isinstance(valeur, dict):
                valeur = {ref: _ordonner_esprit(esprit) for ref, esprit in valeur.items()}
            ordonne[cle] = valeur
    for cle, valeur in faits.items():
        if cle not in ordonne:
            ordonne[cle] = valeur
    return ordonne


def ordonner_entree(entree):
    """Place ``faits`` (ordonné par stabilité) en tête de l'entrée JSON et les ajouts de relance
    (``retour_forme``, ``controle_narratif``, ``consigne_revision``) tout à la fin."""
    if not isinstance(entree, dict):
        return entree
    ordonne = {}
    for cle in ORDRE_ENTREE:
        if cle in entree:
            ordonne[cle] = ordonner_faits(entree[cle]) if cle == "faits" else entree[cle]
    for cle, valeur in entree.items():
        if cle not in ordonne:
            ordonne[cle] = valeur
    return ordonne


def voie_cache(fonction, entree, interpretation=None):
    """Identifie la voie de cache KV d'un appel pour éviter qu'interprétation, narration de dialogue,
    narration de résultat et audits n'évincent mutuellement leur préfixe."""
    if fonction == "repondre_au_joueur":
        faits = entree.get("faits", {}) if isinstance(entree, dict) else {}
        if isinstance(faits, dict) and "resultat_resolu" in faits:
            return "raconter_resultat"
        if interpretation is False or (isinstance(faits, dict) and "conversation_validee" in faits):
            return "raconter"
        return "interpreter"
    return fonction


def slot_cache(voie):
    """Indice de slot KV (0..3) pour les moteurs locaux multi-slots (llama-server)."""
    return SLOTS_VOIE.get(voie, 3)
