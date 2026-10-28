"""Mise en récit / Narrateur littéraire : enrichissement d'ambiance et répliques contrôlés.

Ce composant intervient uniquement APRÈS que le moteur a validé, résolu et sauvegardé
l'état du monde. Sa narration est soumise aux gardes déterministes de ``donjon/narration.py``
(``voix_auteur``, ``paroles_sans_moteur``, ``voix_inconnues``, ``mentions``) avant tout
affichage ou enregistrement d'ambiance.
"""
import os
import re
import sys
from .fournisseurs.contrat import Demande, ErreurFournisseur
from . import lexique
from .monde import ErreurMonde
from .narration import (
    CITATIONS,
    INSTRUCTIONS_REVISION,
    chiffres_sans_fondement,
    mentions,
    paroles_sans_moteur,
    segments,
    voix_auteur,
    voix_inconnues,
)
from .refus import audit
from .voix import connait_appellation, connait_nom, nom_pour_joueur

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


def _fondement_narrateur(monde, entree, cible_id=None, faits=None):
    """Construit le corpus de fondement autorisé pour la narration et les paroles citées."""
    salle_id = monde.joueur.get("salle", "")
    salle_data = monde.data.get("salles", {}).get(salle_id, {})
    elements_base = [
        entree,
        monde.data.get("conversation", []),
        salle_data.get("nom", ""),
        salle_data.get("description", ""),
        monde.data.get("ambiances", {}).get(salle_id, []),
    ]
    salles_sorties = {
        (v.get("destination") if isinstance(v, dict) else v)
        for v in (salle_data.get("sorties") or {}).values()
        if isinstance(v, (str, dict))
    }
    salles_connues = {salle_id, *monde.data.get("salles_visitees", []), *(s for s in salles_sorties if isinstance(s, str))}
    for s_id in salles_connues:
        if s_id in monde.data.get("salles", {}):
            elements_base.append(monde.data["salles"][s_id].get("nom", ""))
    connus = set(monde.data.get("connus", []))
    for o_id, o in monde.objets.items():
        if o.get("type") == "personnage":
            if o.get("lieu") == salle_id or o_id in connus:
                elements_base.append(nom_pour_joueur(monde, o_id))
                elements_base.append(o.get("portrait", ""))
                if connait_nom(monde, "joueur", o_id):
                    elements_base.append(o.get("nom", ""))
                    elements_base.append(o.get("aliases", []))
        elif monde.accessible(o_id) or o_id in connus or o.get("lieu") == "joueur":
            if monde.visible(o_id) or o_id in connus or o.get("lieu") == "joueur":
                elements_base.append(o.get("nom", ""))
                elements_base.append(o.get("aliases", []))
                elements_base.append(o.get("description", ""))
                elements_base.append(o.get("description_visuelle", ""))
    for p_id in monde.data.get("noms_connus", []):
        if p_id in monde.objets:
            elements_base.append(monde.objets[p_id].get("nom", ""))
            elements_base.append(monde.objets[p_id].get("aliases", []))
    base = lexique.corpus(*elements_base)

    elements_paroles = [faits or []]
    if cible_id and cible_id in monde.objets:
        esprit = monde.data.get("esprits", {}).get(cible_id, {})
        elements_paroles.append(esprit)
        for x_id, x_obj in monde.objets.items():
            if x_obj.get("type") == "personnage" and connait_appellation(monde, cible_id, x_id):
                elements_paroles.append(x_obj.get("nom", ""))
                elements_paroles.append(x_obj.get("aliases", []))
    paroles_croyances = lexique.corpus(*elements_paroles)
    return base, paroles_croyances


def verifier_narration(monde, texte, entree, mode="ambiance", cible_id=None, faits=None, se_nomme=False):
    """Applique les gardes déterministes de ``donjon/narration.py`` sur un texte généré."""
    if not texte or not texte.strip():
        return []
    base, paroles_croyances = _fondement_narrateur(monde, entree, cible_id=cible_id, faits=faits)
    obstacles = list(voix_auteur(texte))
    if mode == "ambiance":
        faits_moteur = {"resultat_moteur": entree.get("resultat_moteur", "")}
        obstacles.extend(paroles_sans_moteur(texte, faits_moteur, adresse=True))
        obstacles.extend(voix_inconnues(monde, [], {}, texte))
        obstacles.extend(mentions(monde, texte, base))
        for n in chiffres_sans_fondement(texte, entree.get("resultat_moteur", ""), monde.joueur):
            obstacles.append(
                audit(
                    f"Ce nombre (« {n} ») ne figure pas dans le résultat mécanique.",
                    f"l'ambiance sans le nombre « {n} » : aucun chiffre ni quantité mécanique non établie",
                    partie="texte",
                    segment=0,
                    texte=texte,
                    recu=n,
                )
            )
        return obstacles

    # Mode dialogue : réplique directe attribuée à cible_id
    paroles_extraites = []
    vrai_nom_pres = ""
    if se_nomme and cible_id and cible_id in monde.objets:
        vrai_nom_pres = monde.objets[cible_id].get("nom", "").split(",")[0].strip()
    if cible_id and cible_id in monde.objets:
        for passage in segments(texte):
            for c in CITATIONS.findall(passage):
                paroles_extraites.append({
                    "locuteur": cible_id,
                    "texte": c.strip("«»“”\" ").strip(),
                    "passage": passage,
                    "presentation": vrai_nom_pres,
                })
    inconnue = bool(
        cible_id and cible_id in monde.objets
        and not connait_nom(monde, "joueur", cible_id)
        and not se_nomme
    )
    faits_voix = {
        "interlocuteurs": (
            {cible_id: {"nom": nom_pour_joueur(monde, cible_id), "voix_inconnue": inconnue}}
            if cible_id and cible_id in monde.objets
            else {}
        ),
        "conversation_validee": {
            "faits": list(faits or []),
            "replique_joueur": entree.get("saisie_joueur", ""),
        },
    }
    obstacles.extend(voix_inconnues(monde, paroles_extraites, faits_voix, texte))
    obstacles.extend(
        mentions(
            monde,
            texte,
            base,
            paroles=paroles_croyances,
            paroles_validees=paroles_extraites if paroles_extraites else None,
        )
    )
    return obstacles


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
        texte = _nettoyer_texte_llm(reponse.arguments.get("texte") or "")
        obstacles = verifier_narration(monde, texte, entree, mode="ambiance")
        if obstacles:
            entree_rev = {
                **entree,
                "controle_narratif": obstacles,
            }
            demande_rev = Demande(
                instructions=PROMPT_NARRATEUR + INSTRUCTIONS_REVISION,
                entree=entree_rev,
                intention=intention,
                fonction="narrer_ambiance",
                schema=SCHEMA_NARRATEUR,
                modele=modele_choisi,
                effort="none",
                timeout=timeout,
            )
            reponse2 = fournisseur.appeler(demande_rev)
            texte = _nettoyer_texte_llm(reponse2.arguments.get("texte") or "")
            obstacles = verifier_narration(monde, texte, entree, mode="ambiance")
            if obstacles:
                valides = [
                    s for s in segments(texte)
                    if not verifier_narration(monde, s, entree, mode="ambiance")
                ]
                return " ".join(valides).strip()
        return texte
    except (ErreurFournisseur, ErreurMonde, TimeoutError, OSError) as exc:
        print(f"[narrateur] {exc}", file=sys.stderr)
        return ""


PROMPT_DIALOGUE = """Tu es la voix du personnage ciblé dans LE SEUIL, un jeu de rôle d'exploration sombre.
Le joueur s'adresse à un personnage présent.
Consignes :
- Réponds directement dans la fiction au nom de `personnage_cible`, en 1 ou 2 phrases percutantes au style direct (ex: <personnage_cible> : « ... »).
- Si `faits_moteur` est non vide, ta réplique DOIT exprimer fidèlement l'issue décrite dans `faits_moteur` (ex: si tu t'écartais pour laisser passer, si tu rends une dette, si tu dis où se trouve quelqu'un ou que tu l'ignores).
- Ne te présente par ton nom (`vrai_prenom`) que si le joueur demande qui tu es (ou si `faits_moteur` indique que tu te nommes).
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


def _formater_replique(replique, cible_nom, vrai_nom, role_cible, se_nomme_dans_faits):
    cible_label = cible_nom[:1].upper() + cible_nom[1:] if cible_nom else "MJ"
    nom_presente = vrai_nom or cible_label
    if replique and replique.lower().strip(".! ") in (cible_label.lower(), nom_presente.lower()):
        if se_nomme_dans_faits:
            if role_cible:
                replique = f"{cible_label} : « Je m'appelle {nom_presente}, {role_cible}. »"
            else:
                replique = f"{cible_label} : « Je m'appelle {nom_presente}. »"
        else:
            return ""
    elif replique and "«" not in replique and '"' not in replique and ":" not in replique:
        replique = f"{cible_label} : « {replique} »"
    if vrai_nom and cible_nom and vrai_nom.lower() != cible_nom.lower():
        replique = re.sub(
            r"(?i)(\b(?:je m'appelle|je suis|mon nom est|on m'appelle)\s+)" + re.escape(cible_nom),
            lambda m: m.group(1) + vrai_nom,
            replique,
        )
    return replique


def repondre_dialogue(fournisseur, monde, intention, personnage=None, faits=None, modele=None, timeout=20):
    """Génère une réponse ou réplique de dialogue directe dans la fiction."""
    if fournisseur is None:
        return ""
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
        if connait_nom(monde, "joueur", cible_id):
            vrai_nom = nom_complet.split(",")[0].strip()
            if "," in nom_complet:
                role_cible = nom_complet.split(",", 1)[1].strip()
        portrait_cible = o_cible.get("portrait") or ""
    from .francais import quantite
    from .rendu import prix
    en_vente = [o for o in monde.objets.values() if o.get("en_vente") and o.get("lieu") == salle_id]
    articles_desc = [f"{o['nom']} ({quantite(prix(monde, o), 'pièce')})" for o in en_vente]
    missions = [m_data.get("nom", m_id) for m_id, m_data in monde.data.get("missions", {}).items()]
    se_nomme_dans_faits = any("se nomme" in f for f in (faits or []))
    entree = {
        "lieu": salle_nom,
        "personnages_presents": pnjs,
        "personnage_cible": cible_nom[:1].upper() + cible_nom[1:] if cible_nom else "MJ",
        "role_cible": role_cible,
        "portrait_cible": portrait_cible,
        "faits_moteur": list(faits or []),
        "articles_en_vente_ici": articles_desc,
        "missions_connues": missions,
        "saisie_joueur": intention,
    }
    if se_nomme_dans_faits:
        entree["vrai_prenom"] = vrai_nom or (cible_nom[:1].upper() + cible_nom[1:] if cible_nom else "MJ")
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
        replique = _formater_replique(replique, cible_nom, vrai_nom, role_cible, se_nomme_dans_faits)
        if not replique:
            return ""
        obstacles = verifier_narration(
            monde, replique, entree, mode="dialogue", cible_id=cible_id, faits=faits, se_nomme=se_nomme_dans_faits
        )
        if obstacles:
            entree_rev = {
                **entree,
                "controle_narratif": obstacles,
            }
            demande_rev = Demande(
                instructions=PROMPT_DIALOGUE + INSTRUCTIONS_REVISION,
                entree=entree_rev,
                intention=intention,
                fonction="repondre_dialogue",
                schema=SCHEMA_DIALOGUE,
                modele=modele_choisi,
                effort="none",
                timeout=timeout,
            )
            reponse2 = fournisseur.appeler(demande_rev)
            replique2 = _nettoyer_texte_llm(reponse2.arguments.get("replique") or "")
            replique2 = _formater_replique(replique2, cible_nom, vrai_nom, role_cible, se_nomme_dans_faits)
            if not replique2:
                return ""
            obstacles2 = verifier_narration(
                monde, replique2, entree, mode="dialogue", cible_id=cible_id, faits=faits, se_nomme=se_nomme_dans_faits
            )
            if obstacles2:
                return ""
            return replique2
        return replique
    except (ErreurFournisseur, ErreurMonde, TimeoutError, OSError) as exc:
        print(f"[narrateur] {exc}", file=sys.stderr)
        return ""
