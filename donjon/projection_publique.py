"""A1 : projection conservatrice d'une entrée préparée par le MJ actuel.

Cette fonction pure ne prépare ni n'envoie une requête. Son entrée est celle
du producteur actuel (Monde.contexte, dossiers publics, noms.public), jamais
un JSON proposé par Luna ou par le joueur. Elle ne certifie pas une sauvegarde
arbitrairement altérée. Les chemins sont des tuples JSON, indices compris.

Les valeurs restent à leur place, sans résumé, dédoublonnage ni réécriture de
conversation. La provenance décrit l'autorité de la source, pas la vérité de
sa prose : un récit ancien, une parole et un candidat refusé sont distincts
d'un fait moteur. Toute nouvelle famille de source demande un contrat ici.
"""
from dataclasses import dataclass
import copy


class ProvenanceAbsente(ValueError):
    """Un nouveau champ ne devient pas public par défaut."""


# Contrats des producteurs, pas une sélection selon la saisie ou le scénario.
SOURCES = {
    "salle": "perception_actuelle", "joueur": "fait_moteur",
    "perception": "perception_actuelle", "signes_percus": "perception_actuelle",
    "impressions": "perception_actuelle", "bruit": "perception_actuelle",
    "mode_cases": "fait_moteur", "minutes": "fait_moteur", "revision": "fait_moteur",
    "ambiance_etablie": "ambiance_enregistree",
    "personnages_connus": "connaissance_declaree", "noms_entendus": "parole_entendue",
    "souvenirs_faits": "souvenir", "souvenirs_personnages": "souvenir",
    "souvenirs_visuels": "souvenir", "lieux_connus": "connaissance_declaree",
    "scenario": "connaissance_declaree", "engagements": "fait_moteur",
    "missions_discutables": "fait_moteur", "comptes": "fait_moteur",
    "proposition_en_attente": "proposition_non_executee",
    "derniere_tentative": "evenement_joueur", "improvisation": "evenement_joueur",
    "evenements_recents": "evenement_joueur", "paroles_entendues": "parole_entendue",
    "echanges_passes": "parole_entendue", "interlocuteurs": "perception_actuelle",
    "esprits_interlocuteurs": "perception_actuelle", "connaissances_pnj": "fait_moteur",
    "attestations": "fait_moteur", "espace": "fait_moteur", "atelier": "fait_moteur",
    "franchissements": "fait_moteur", "passages_obstacles": "fait_moteur",
    "descriptions_a_completer": "catalogue_admission",
    "connaissances_a_completer": "catalogue_admission",
    "profil_joueur_a_completer": "catalogue_admission",
    "faits_narratifs_proposables": "catalogue_admission",
    "expression_joueur": "fait_moteur", "parole_prevue": "proposition_non_executee",
    "ambiance_ciblee": "ambiance_enregistree", "reperes_demandes": "saisie_joueur",
    "retour_moteur": "refus_moteur",
}
SOURCES_ENTREE = {
    "message": "saisie_joueur", "conversation": "historique_conversation",
    "retour_forme": "refus_moteur", "controle_narratif": "controle_non_factuel",
    "consigne_revision": "controle_non_factuel", "consigne_retour_moteur": "refus_moteur",
}

# Ces dossiers sont des entrées du metteur en voix des PNJ, pas un savoir de
# Corvus. Même une croyance vraie ou un engagement interne n'est pas entendu.
ESPRIT_PRIVE = frozenset(("traits", "valeurs", "croit", "but_actuel", "besoins_pressants",
                         "engagements", "a_entendu", "noms_pour_repliques", "nom_du_locuteur"))
INTERLOCUTEUR_PRIVE = frozenset(("intentions", "ton", "dernier_son_entendu",
                               "paroles_entendues", "refuse_ventes_apres_vol"))
OBJET_PRIVE = frozenset(("profil", "humeur", "connait_noms", "vigilance", "refuse_ventes_apres_vol"))
ESPRIT_PUBLIC = frozenset(("voix_inconnue", "genre"))
INTERLOCUTEUR_PUBLIC = frozenset(("nom", "voix_inconnue", "personne_inconnue", "entendue",
                                "genre", "signes", "offres", "sujets_ouverts"))
# La copie d'un objet est un dossier mixte, contrairement aux dossiers publics
# du moteur. Une propriété d'auteur nouvelle n'est donc jamais admise par
# défaut. Ce contrat ne dépend ni du type d'objet, ni de son identifiant.
OBJET_PUBLIC = frozenset("""
    id nom type aliases genre pluriel nom_propre elision integrite maximum masse
    materiau mobile visible localisation a_portee_de_main a_portee_de_voix
    ancrage_carte appui_vertical description_visuelle description_tactile
    support_pose etat_corps maniere_de_parler orientation portrait rattache_a
    en_vente vendeur prix proprietaire puissance usages charges duree_combustion prix_part
    fixee_sur inscription motif allume combustible foyer luminosite amovible
    attache cote extraction resistance ouvre bloque_par detachee fixations
    ouverte positions_salles relie seuil_coupe verrouillee bloquee bloque_passage
    bloque_vue passage lieu position position_salle case_percue a_portee
    sens constats_capacites
""".split())
# Contrats des producteurs mécaniques déjà exposés par Monde.contexte :
# matiere.appliquer/fixer_longueur/valider_contenu et artisanat.appliquer.
# Ils couvrent aussi les pièces et structures créées pendant la partie, sans
# distinguer leur identifiant, leur lieu, ni leur scénario d'origine.
from .matiere import DIMENSIONS
OBJET_PUBLIC |= frozenset(DIMENSIONS) | frozenset("""
    physique ressource charge_jeu_kg contenu portions contenu_vide
    assemblage barreaux composants installation incorpore pieces
    description sonorite facettes facettes_etablies
""".split())
OBJET_PRIVE |= frozenset(("arbitrage", "pv", "pv_max", "corps"))
# tenir.finir marque tout lien qui retient un corps avec entrave=True et
# retire ce marqueur quand le lien est défait. C'est un état mécanique public
# du lien perceptible, également produit par banc_pnj.appliquer_etats.
OBJET_PUBLIC |= frozenset(("entrave",))
# faits_locaux produit une relation mécanique publique et des métadonnées
# de persistance. Ces dernières ne sont ni une perception ni une capacité.
OBJET_PUBLIC |= frozenset(("relation_support",))
OBJET_TECHNIQUE = frozenset(("origine_description", "scene_detail", "detail_local",
                             "cartographier", "position_autonome", "ancrage_initial", "origine_ambiance",
                             "lot_origine"))
SOUVENIR_PERSONNAGE_PUBLIC = frozenset(("nom", "portrait", "traits", "details", "source", "minute",
                                       "tour", "maniere_de_parler"))
SOUVENIR_VISUEL_PUBLIC = frozenset(("id", "nom", "derniere_salle", "hors_de_vue", "distance_metres",
                                   "vu_a", "orientation_relative", "source", "minute", "tour"))


def _verifier_champs(bloc, permis, chemin):
    for cle in bloc:
        if cle not in permis:
            raise ProvenanceAbsente((*chemin, cle))


def feuilles(valeur, chemin=()):
    """Valeurs atomiques ET conteneurs vides (dont l'absence est informative)."""
    if isinstance(valeur, (dict, list)) and valeur:
        elements = valeur.items() if isinstance(valeur, dict) else enumerate(valeur)
        for cle, contenu in elements:
            yield from feuilles(contenu, (*chemin, cle))
    else:
        yield chemin, valeur


def lire(valeur, chemin):
    for cle in chemin:
        valeur = valeur[cle]
    return valeur


@dataclass
class Projection:
    entree: dict
    provenances: list
    # Journal technique séparé : ses chemins peuvent nommer des secrets. Ne
    # jamais le transmettre au compilateur ni le publier comme contexte.
    exclusions: list

    def publique(self):
        return {"entree": copy.deepcopy(self.entree),
                "provenances": copy.deepcopy(self.provenances)}


def projeter(entree):
    """Conserve chaque donnée publique et attache sa source exacte.

    Aucun souvenir n'est déduit du français de la conversation. Les dates
    d'observation ne sont reprises que si la mémoire les fournit ; la date
    de cette projection ne prétend jamais être celle de l'observation.
    """
    faits = entree["faits"]
    for cle in entree:
        if cle != "faits" and cle not in SOURCES_ENTREE:
            raise ProvenanceAbsente((cle,))
    for cle in faits:
        if cle not in SOURCES and not cle.startswith("objet:"):
            raise ProvenanceAbsente(("faits", cle))
    for source, permis in (("esprits_interlocuteurs", ESPRIT_PUBLIC | ESPRIT_PRIVE),
                           ("interlocuteurs", INTERLOCUTEUR_PUBLIC | INTERLOCUTEUR_PRIVE),
                           ("souvenirs_personnages", SOUVENIR_PERSONNAGE_PUBLIC)):
        for ref, bloc in faits.get(source, {}).items():
            _verifier_champs(bloc, permis, ("faits", source, ref))
    for i, bloc in enumerate(faits.get("souvenirs_visuels", [])):
        _verifier_champs(bloc, SOUVENIR_VISUEL_PUBLIC, ("faits", "souvenirs_visuels", i))
    for cle, bloc in faits.items():
        if cle.startswith("objet:"):
            _verifier_champs(bloc, OBJET_PUBLIC | OBJET_PRIVE | OBJET_TECHNIQUE, ("faits", cle))

    provenance, exclusions = [], []
    # Seuls les répertoires de désignation publics font connaître une référence.
    connus = {"joueur", *faits.get("personnages_connus", {}),
              *faits.get("souvenirs_personnages", {}), *faits.get("interlocuteurs", {})}
    connus.update(k[6:] for k in faits if k.startswith("objet:"))
    connus.update(s["id"] for s in faits.get("souvenirs_visuels", []))
    connus.update(s["id"] for s in faits.get("perception", {}).get("non_vus_connus", []))
    connus.update(faits.get("echanges_passes", {}))
    for p in faits.get("paroles_entendues", []):
        connus.add(p["locuteur"])

    def secret(chemin):
        if len(chemin) < 2 or chemin[0] != "faits":
            return None
        source = chemin[1]
        if source.startswith("objet:") and len(chemin) >= 3 and chemin[2] in OBJET_TECHNIQUE:
            return "métadonnée de création et de persistance, sans autorité perceptive"
        if source == "connaissances_pnj":
            return "dossier de savoir privé du PNJ ; les mots transmis restent dans les paroles"
        if source == "esprits_interlocuteurs" and len(chemin) >= 4 and chemin[3] in ESPRIT_PRIVE:
            return "état mental privé du PNJ"
        if source == "interlocuteurs" and len(chemin) >= 4 and chemin[3] in INTERLOCUTEUR_PRIVE:
            return "dossier privé de formulation du PNJ"
        if source.startswith("objet:") and len(chemin) >= 3 and chemin[2] in OBJET_PRIVE:
            return "état interne du personnage"
        if (source == "perception" and len(chemin) == 5 and chemin[2] == "contributions"
                and chemin[4] == "source"
                and lire(entree, chemin) is not None
                and lire(entree, chemin) not in connus):
            return "identité non perçue de la source lumineuse"
        if (source in ("paroles_entendues", "echanges_passes") and len(chemin) >= 5
                and chemin[-2] == "auditeurs" and isinstance(chemin[-1], int)
                and lire(entree, chemin) not in connus):
            return "auditeur acoustique sans désignation connue de Corvus"
        return None

    def origine(chemin, destination):
        source = chemin[1] if chemin[0] == "faits" else chemin[0]
        nature = (("perception_actuelle" if source.startswith("objet:") else SOURCES[source]) if chemin[0] == "faits"
                  else SOURCES_ENTREE[source])
        origine = {"chemin": list(chemin), "nature": nature,
                   "destination": list(destination),
                   "source": list(chemin[:2] if chemin[0] == "faits" else chemin[:1]),
                   "revision_projection": faits.get("revision")}
        if nature == "souvenir":
            origine.update(source_observation=None, date_observation_connue=False)
        if chemin[0] == "faits":
            bloc = faits[source]
            if source == "souvenirs_personnages" and len(chemin) >= 3:
                bloc = bloc[chemin[2]]
            elif source in ("souvenirs_visuels", "souvenirs_faits", "paroles_entendues",
                            "evenements_recents") and len(chemin) >= 3:
                bloc = bloc[chemin[2]]
            if isinstance(bloc, dict):
                origine.update({k: copy.deepcopy(bloc[k]) for k in ("minute", "tour") if k in bloc})
                if nature == "souvenir":
                    origine["source_observation"] = bloc.get("source")
                    origine["date_observation_connue"] = "minute" in bloc or "tour" in bloc
            if "proposition_pour_reprise" in chemin or "proposition_refusee" in chemin:
                origine["nature"] = "proposition_non_executee"
        elif source == "conversation" and len(chemin) >= 2:
            bloc = entree[source][chemin[1]]
            if isinstance(bloc, dict) and "revision" in bloc:
                origine["revision_historique"] = bloc["revision"]
        return origine

    def parcourir(valeur, chemin=(), destination=()):
        raison = secret(chemin)
        if raison:
            exclusions.extend({"chemin": list(c), "motif": "secret", "raison": raison}
                              for c, _ in feuilles(valeur, chemin))
            return _EXCLU
        if isinstance(valeur, dict) and valeur:
            resultat = {}
            for cle, contenu in valeur.items():
                copie = parcourir(contenu, (*chemin, cle), (*destination, cle))
                if copie is not _EXCLU:
                    resultat[cle] = copie
            return resultat if resultat else _EXCLU
        if isinstance(valeur, list) and valeur:
            resultat = []
            for i, contenu in enumerate(valeur):
                copie = parcourir(contenu, (*chemin, i), (*destination, len(resultat)))
                if copie is not _EXCLU:
                    resultat.append(copie)
            return resultat if resultat else _EXCLU
        provenance.append(origine(chemin, destination))
        return copy.deepcopy(valeur)

    return Projection(parcourir(entree), provenance, exclusions)


_EXCLU = object()


def verifier_couverture(entree, projection):
    """Preuve exhaustive par chemin ; une omission, valeur ou exclusion altérée échoue."""
    originales = dict(feuilles(entree))
    gardees = {tuple(p["chemin"]): p for p in projection.provenances}
    exclues = {tuple(e["chemin"]): e for e in projection.exclusions}
    if len(gardees) != len(projection.provenances) or len(exclues) != len(projection.exclusions):
        raise ValueError("Chemin dupliqué")
    if gardees.keys() & exclues.keys() or gardees.keys() | exclues.keys() != originales.keys():
        raise ValueError("Couverture incomplète ou contradictoire")
    # Recalculer les motifs avec le contrat commun : une justification libre
    # ou un simple compteur d'exclusions ne constitue pas une preuve.
    attendue = projeter(entree)
    if projection != attendue:
        raise ValueError("Projection ou justification différente du contrat")
    for chemin, p in gardees.items():
        if not p.get("nature") or lire(projection.entree, p["destination"]) != originales[chemin]:
            raise ValueError(f"Donnée sans équivalent : {chemin}")
    return len(gardees)
