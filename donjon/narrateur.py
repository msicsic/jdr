"""Mise en récit / Narrateur littéraire : enrichissement d'ambiance a posteriori.

Ce composant intervient uniquement APRÈS que le moteur a validé, résolu et sauvegardé
l'état du monde. Sa narration est purement cosmétique (ambiance, sensations) et n'a
aucune autorité mécanique. Zéro audit lourd requis.
"""
import os
from .fournisseurs.contrat import Demande
from .voix import nom_pour_joueur

PROMPT_NARRATEUR = """Tu es la voix narrative de LE SEUIL, un jeu de rôle d'exploration sombre et viscéral.
Ton rôle est d'enrichir le résultat mécanique d'une action en apportant une sensation sensorielle
(odeur, humidité, obscurité, écho, texture froide) ou une impression d'ambiance.
Consignes :
- Écris en 1 ou 2 phrases percutantes, toujours à la deuxième personne du singulier (« tu »).
- Sois sobre, sombre et évocateur.
- Ne contredis JAMAIS le résultat mécanique reçu. N'invente aucun nouvel objet ni aucun passage.
- N'inclus aucun chiffre, montant d'or ou statistique dans ta narration.
"""

SCHEMA_NARRATEUR = {
    "type": "object",
    "properties": {
        "texte": {
            "type": "string",
            "description": "Une ou deux phrases d'ambiance viscérale et sombre."
        }
    },
    "required": ["texte"],
    "additionalProperties": False,
}


def determiner_modele(fournisseur, modele_souhaite=None):
    """Détermine le modèle adapté au fournisseur pour la narration."""
    if modele_souhaite:
        return modele_souhaite
    from .config import MODELE_PAR_DEFAUT, MODELE_LOCAL, MODELE_CLAUDE, MODELE_MIMO
    cls_nom = fournisseur.__class__.__name__.lower()
    if "local" in cls_nom:
        return os.environ.get("LOCAL_MODEL", MODELE_LOCAL)
    if "anthropic" in cls_nom:
        return MODELE_CLAUDE
    if "mimo" in cls_nom:
        return MODELE_MIMO
    return os.environ.get("OPENAI_MODEL", MODELE_PAR_DEFAUT)


def _nettoyer_texte_llm(texte):
    """Élimine les scories de décodage contraint ou de balises internes du modèle."""
    if not texte:
        return ""
    for marqueur in ("<channel", "<|", "} #", "}#", "\n#", "// Correction", "# Correction"):
        if marqueur in texte:
            texte = texte.split(marqueur, 1)[0]
    return texte.strip().rstrip("}").rstrip("{").strip()


def narrer(fournisseur, monde, intention, resultat_moteur, modele=None, timeout=20):
    """Génère un vernis narratif d'ambiance à partir du résultat acté par le moteur."""
    if fournisseur is None:
        return ""
    salle_id = monde.joueur["salle"]
    salle_nom = monde.data["salles"][salle_id].get("nom", salle_id)
    entree = {
        "lieu": salle_nom,
        "intention": intention,
        "resultat_moteur": resultat_moteur,
    }
    modele_choisi = determiner_modele(fournisseur, modele)
    demande = Demande(
        instructions=PROMPT_NARRATEUR,
        entree=entree,
        intention=intention,
        fonction="narrer_ambiance",
        schema=SCHEMA_NARRATEUR,
        modele=modele_choisi,
        effort="none",  # Pas de réflexion lourde pour de l'habillage poétique
        timeout=timeout,
    )
    try:
        reponse = fournisseur.appeler(demande)
        texte = reponse.arguments.get("texte") or ""
        return _nettoyer_texte_llm(texte)
    except Exception:
        # En cas d'erreur ou timeout du narrateur, le résultat mécanique suffit
        return ""


PROMPT_DIALOGUE = """Tu es la voix du personnage ciblé dans LE SEUIL, un jeu de rôle d'exploration sombre.
Le joueur s'adresse à un personnage présent.
Consignes :
- Réponds directement dans la fiction au nom de `personnage_cible`, en 1 ou 2 phrases percutantes au style direct (ex: <personnage_cible> : « ... »).
- Réponds réellement à la question ou aux propos du joueur d'après ton rôle (`role_cible`), ton portrait (`portrait_cible`), le lieu et `faits_moteur`.
- Si le joueur demande ton nom ou qui tu es, réponds dans les guillemets avec ton vrai prénom (`vrai_prenom`), JAMAIS avec une description physique comme « l'homme large » ou « l'homme svelte ».
- Ne répète JAMAIS la question du joueur mot pour mot en guise de réponse.
- N'écris JAMAIS de texte générique ou méta (« Réponse du PNJ », « à déterminer », « Le joueur... », « Aucune action... »).
"""

SCHEMA_DIALOGUE = {
    "type": "object",
    "properties": {
        "replique": {
            "type": "string",
            "description": "La réponse ou réplique directe dans la fiction (ex: Gorm : « ... »)."
        }
    },
    "required": ["replique"],
    "additionalProperties": False,
}


def repondre_dialogue(fournisseur, monde, intention, personnage=None, faits=None, modele=None, timeout=20):
    """Génère une réponse ou réplique de dialogue directe dans la fiction."""
    if fournisseur is None:
        return ""
    import re
    salle_id = monde.joueur["salle"]
    salle_nom = monde.data["salles"][salle_id].get("nom", salle_id)
    pnjs_ids = [
        o["id"]
        for o in monde.objets.values()
        if o.get("type") == "personnage" and o.get("lieu") == salle_id and o["id"] != "joueur"
    ]
    pnjs = [nom_pour_joueur(monde, pid) for pid in pnjs_ids]
    cible_id = personnage if (personnage and personnage in monde.objets) else (pnjs_ids[0] if pnjs_ids else None)
    cible_nom = nom_pour_joueur(monde, cible_id) if cible_id else (personnage or "MJ")
    role_cible = ""
    portrait_cible = ""
    vrai_nom = ""
    if cible_id and cible_id in monde.objets:
        o_cible = monde.objets[cible_id]
        nom_complet = o_cible.get("nom", "")
        vrai_nom = nom_complet.split(",")[0].strip()
        if "," in nom_complet:
            role_cible = nom_complet.split(",", 1)[1].strip()
        portrait_cible = o_cible.get("portrait") or ""
    from .francais import quantite
    from .rendu import prix
    en_vente = [o for o in monde.objets.values() if o.get("en_vente") and o.get("lieu") == salle_id]
    articles_desc = [f"{o['nom']} ({quantite(prix(monde, o), 'pièce')})" for o in en_vente]
    missions = [m_data.get("nom", m_id) for m_id, m_data in monde.data.get("missions", {}).items()]
    entree = {
        "lieu": salle_nom,
        "personnages_presents": pnjs,
        "personnage_cible": cible_nom[:1].upper() + cible_nom[1:] if cible_nom else "MJ",
        "vrai_prenom": vrai_nom or (cible_nom[:1].upper() + cible_nom[1:] if cible_nom else "MJ"),
        "role_cible": role_cible,
        "portrait_cible": portrait_cible,
        "faits_moteur": list(faits or []),
        "articles_en_vente_ici": articles_desc,
        "missions_connues": missions,
        "saisie_joueur": intention,
    }
    modele_choisi = determiner_modele(fournisseur, modele)
    demande = Demande(
        instructions=PROMPT_DIALOGUE,
        entree=entree,
        intention=intention,
        fonction="repondre_dialogue",
        schema=SCHEMA_DIALOGUE,
        modele=modele_choisi,
        effort="none",
        timeout=timeout,
    )
    try:
        reponse = fournisseur.appeler(demande)
        replique = _nettoyer_texte_llm(reponse.arguments.get("replique") or "")
        cible_label = cible_nom[:1].upper() + cible_nom[1:] if cible_nom else "MJ"
        nom_presente = vrai_nom or cible_label
        if replique and replique.lower().strip(".! ") in (cible_label.lower(), nom_presente.lower()):
            if role_cible:
                replique = f"{cible_label} : « Je m'appelle {nom_presente}, {role_cible}. »"
            else:
                replique = f"{cible_label} : « Je m'appelle {nom_presente}. »"
        elif replique and "«" not in replique and '"' not in replique and ":" not in replique:
            replique = f"{cible_label} : « {replique} »"
        if vrai_nom and cible_nom and vrai_nom.lower() != cible_nom.lower():
            replique = re.sub(
                r"(?i)(\b(?:je m'appelle|je suis|mon nom est|on m'appelle)\s+)" + re.escape(cible_nom),
                lambda m: m.group(1) + vrai_nom,
                replique,
            )
        return replique
    except Exception:
        return ""
