"""Portée des descriptions libres proposées comme faits persistants.

Une description d'un sujet ne doit pas établir au passage un autre fait autonome.
Le contrôleur doit couvrir le texte entier et justifier chaque affirmation autonome.
"""

import copy
import json

from .monde import ErreurMonde
from .refus import RapportIllisible, audit, citer, liste
from .narration import segments
from .capacites_objet import CAPACITES_REVUE, noms as noms_capacites


SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {"descriptions": {"type": "array", "maxItems": 24,
        "items": {"type": "object", "additionalProperties": False,
            "properties": {
                "representation": {"type": "string", "enum": [
                    "aspect", "objet", "texte_lisible", "etat_du_monde",
                    "portrait", "savoir_pnj", "indetermine"]},
                "mobilite": {"type": "array", "items": {"type": "string", "enum": [
                    "amovible", "fixe", "indetermine"]}},
                "placement": {"type": "string", "enum": [
                    "pose", "fixe", "contenu", "aucun", "indetermine"]},
                "impact_scenario": {"type": "string", "enum": [
                    "aucun", "objectif", "solution", "indice", "changement", "incertain"]},
                "capacites": {"type": "array", "maxItems": len(CAPACITES_REVUE),
                              "items": {"type": "string", "enum": list(CAPACITES_REVUE)}},
                "fragments": {"type": "array", "minItems": 1, "maxItems": 12,
                "items": {"type": "object", "additionalProperties": False,
                    "properties": {
                        "texte": {"type": "string"},
                        "portee": {"type": "string", "enum": ["sujet", "attestation", "ambiance", "sans_preuve"]},
                        "preuve": {"type": "string"},
                        "motif": {"type": "string"},
                    },
                    "required": ["texte", "portee", "preuve", "motif"]}}},
            "required": ["representation", "mobilite", "placement", "impact_scenario", "capacites", "fragments"]}}},
    "required": ["descriptions"],
}

# La portée d'une transaction ne se réduit pas à celle de sa prose : même une
# qualification sans texte peut remplacer indûment le geste demandé.
SCHEMA_FAITS = copy.deepcopy(SCHEMA)
SCHEMA_FAITS["properties"]["usages"] = {
    "type": "array", "minItems": 1, "maxItems": 3,
    "items": {"type": "object", "additionalProperties": False,
              "properties": {"perception_requise": {"type": "boolean"},
                             "indice": {"type": "boolean"},
                             "motif": {"type": "string"}},
              "required": ["perception_requise", "indice", "motif"]}}
SCHEMA_FAITS["required"].append("usages")


def contexte_admission(faits, proposition=None):
    """Les preuves publiques de la portée ; jamais un état caché du monde.

    Le catalogue seul dit où créer, pas ce qui existe déjà. La même projection
    que le compilateur fournit perceptions, objets connus et résultats établis.
    L'ambiance reste identifiée comme telle, sans devenir une attestation.
    """
    sources = {"salle", "scenario", "perception", "faits_narratifs_proposables",
               "descriptions_a_completer", "connaissances_a_completer",
               "souvenirs_faits", "souvenirs_visuels", "ambiance_etablie",
               "ambiance_ciblee", "engagements", "missions_discutables"}
    contexte = {cle: copy.deepcopy(valeur) for cle, valeur in faits.items()
                if cle in sources or cle.startswith("objet:")}
    if proposition is not None:
        from .monde import reference_exacte
        objets = [v for k, v in contexte.items() if k.startswith("objet:")]
        # Les anciennes projections ne portent que les fiches qualifiables du
        # catalogue public. Elles restent une source publique, jamais le monde brut.
        qualifiables = contexte.get("faits_narratifs_proposables", {}).get("qualifiables", {})
        objets.extend({"id": id, **v} for id, v in qualifiables.items()
                      if "objet:" + id not in contexte)
        admissions = []
        for indice, ajout in enumerate(proposition["ajouts"]):
            id = reference_exacte(objets, ajout.get("ancrage"))
            etablies = next((o for o in objets if o.get("id") == id), {})
            etablies = {k: v for k, v in etablies.items()
                        if not (k in ("physique", "contenu", "passage")
                                and v in ("inconnue", "inconnu"))}
            # Les sélecteurs et le moyen ne sont pas des propriétés nouvelles.
            mutation = {k: copy.deepcopy(v) for k, v in ajout.items()
                        if k not in ("type", "ancrage", "moyen")}
            admissions.append({"ajout": indice, "type": ajout["type"],
                "ancrage": ajout.get("ancrage"),
                "proprietes_etablies": copy.deepcopy(etablies),
                "proprietes_a_etablir": mutation,
                "moyen": ajout.get("moyen"),
                "suite_non_executee": copy.deepcopy(proposition.get("suite"))})
        contexte["admissions"] = admissions
    return contexte


def schema_admission(entrees, proposition=None):
    """Le contrat de correspondance est fixé avant l'appel, jamais deviné au retour."""
    schema = copy.deepcopy(SCHEMA_FAITS if proposition is not None else SCHEMA)
    descriptions = schema["properties"]["descriptions"]
    descriptions.update(minItems=len(entrees), maxItems=len(entrees))
    if proposition is not None:
        n = len(proposition["ajouts"])
        schema["properties"]["usages"].update(minItems=n, maxItems=n)
    return schema


def controler_usages(proposition, rapport):
    """Un jugement par mutation, jamais une autorisation d'exécuter sa suite.

    Un verdict négatif reste un refus ; la présence d'une suite ne l'efface pas.
    La correction porte sur l'affirmation excessive, sans abandonner le préalable.
    """
    ajouts = proposition.get("ajouts") if isinstance(proposition, dict) else None
    usages = rapport.get("usages") if isinstance(rapport, dict) else None
    if (not isinstance(ajouts, list) or not isinstance(usages, list)
            or len(ajouts) != len(usages) or not 1 <= len(ajouts) <= 3
            or any(not isinstance(a, dict) for a in ajouts)
            or any(not isinstance(u, dict)
                   or set(u) != {"perception_requise", "indice", "motif"}
                   or type(u["perception_requise"]) is not bool
                   or type(u["indice"]) is not bool or not isinstance(u["motif"], str)
                   for u in usages)):
        raise RapportIllisible("Contrôle de l'usage des faits incomplet.")
    from .moteur import PERCEPTIONS
    obstacles = []
    for i, (ajout, usage) in enumerate(zip(ajouts, usages)):
        for cause in ("perception_requise", "indice"):
            if usage[cause]:
                suite = proposition.get("suite")
                borne = ("un ajout limité à sa mutation autorisée, sans "
                         + ("résultat de perception" if cause == "perception_requise" else "indice")
                         + " supplémentaire ; conserver proposition.suite = " + repr(suite)
                         + " comme geste non exécuté, soumis aux validations ordinaires ; "
                         if suite is not None else "")
                obstacles.append(audit(
                    "Un fait narratif ne peut pas remplacer une perception." if cause == "perception_requise"
                    else "Un fait narratif ne peut pas créer un indice.",
                    borne + "pour établir un résultat de perception : mode = action, proposition.action parmi " + liste(sorted(PERCEPTIONS))
                    + " (examiner pour inspecter, toucher pour fouiller un contenant ouvert) ; "
                    f"cible = {ajout.get('ancrage')!r}, le support recherché ; le moteur produit et enregistre le résultat, "
                    "positif ou négatif, " + ("sans attribuer ce résultat à l'ajout préalable"
                    if suite is not None else "sans nouvel ajout etablir_faits"),
                    partie=f"proposition.ajouts[{i}]", recu=ajout,
                    verdict=(cause, usage["motif"])))
    return obstacles

INSTRUCTIONS = """Tu fais la contre-revue de descriptions proposées par le MJ.
Si proposition_faits est fournie, rends aussi usages : un jugement pour CHAQUE ajout, dans
l'ordre, même sans description libre (qualification, inscription, parole, évolution).
Compare l'ajout à la mutation de chaque dossier admissions, séparée de sa
suite_non_executee. Les proprietes_a_etablir sont l'objet de l'admission, pas des
preuves préalables exigibles. Juge les affirmations qui dépassent cette mutation :
- perception_requise=true si l'ajout affirme un résultat de recherche, de fouille ou
  d'examen au-delà de cette mutation, au lieu de laisser exécuter cette perception.
  Cela vaut aussi pour un simple aspect du support qui remplace le geste, un résultat négatif
  ou hypothétique. La création ou qualification préalable ne vaut pas exécution ni
  résultat de la suite : celle-ci reste à valider par le moteur. Décrire l'aspect ordinaire
  ou les propriétés matérielles inconnues en réponse à une question descriptive reste permis ;
- indice=true si l'ajout crée un signe permettant d'inférer un passage, une présence, un
  événement ou quelque chose de caché, même sans aucun lien avec l'objectif de la partie.
  Une parole établit seulement les mots prononcés, pas leur vérité ; une évolution déclarée
  applique une mécanique du scénario. Ne traite pas leur contenu comme une découverte inventée.
Le motif explique ce jugement. Le nom et tous les champs de l'ajout comptent ;
ne te limite pas au texte des descriptions. Une odeur ou une texture sans valeur d'indice
et sans résultat de geste reste une ambiance légitime.
Avant d'évaluer les preuves, détermine quelle représentation une phrase impose au jeu :
- aspect : propriété visuelle locale d'un objet, d'un détail ou de son support, sans autre objet autonome ni message à lire ;
- objet : chose distincte dont l'existence, la position et les interactions doivent être suivies ;
- texte_lisible : signes portant un contenu littéral que le joueur peut lire ;
- etat_du_monde : événement, savoir, lieu, déplacement ou conséquence au-delà du sujet ;
- portrait : seule apparence de la partie du personnage indiquée (l'aspect d'un personnage est un portrait) ;
- savoir_pnj : souvenir, motivation ou croyance personnelle attribuée au personnage ;
  cela établit son point de vue, pas la vérité des référents extérieurs ;
- indetermine : portée impossible à trancher.
Classe d'après ce que la phrase fait croire au joueur, et non d'après le type proposé par
le MJ. Un sujet peut être décrit visuellement tout en exigeant une autre représentation.
Pour chaque entrée, liste TOUTES les contraintes de mobilité AFFIRMÉES par le texte :
amovible, fixe au support ou indéterminée si une contrainte est affirmée mais incompréhensible.
La liste est vide si la mobilité n'est pas évoquée, notamment par un nom seul. Une phrase
peut affirmer à la fois fixation et transport : conserve les deux. « Fixé » décrit
l'attache actuelle, pas l'impossibilité de déplacer l'objet après détachement.
La relation actuelle (posé, fixé, contenu) doit correspondre à la proposition structurée.
Classe séparément le placement explicitement décrit : pose, fixe, contenu, aucun si le
texte ne le mentionne pas, indetermine si la relation décrite est ambiguë. Ne déduis pas
le placement du seul support fourni dans la transaction.
Classe aussi ce que le nom et le texte AFFIRMENT sur l'objectif public de la partie :
aucun, objectif lui-même, nouvelle solution, indice, changement de situation ou incertain.
Un objet identique à l'objectif, un indice qui indique sa position, ou une phrase qui
annonce un résultat de mission ont un impact même sans citer la mission par son nom.
Une capacité ordinaire ne prouve pas à elle seule qu'un objectif sera atteint : sa réussite
éventuelle dépend d'actions ultérieures validées par le moteur. Ne classe pas comme solution
un simple outil polyvalent qui pourrait être utile dans plusieurs situations.
Les ajouts libres ne peuvent pas établir un nouvel objectif, indice ou résultat de mission :
ils exigent une transition de scénario déclarée par la partie.
Classe les capacités physiques affirmées ou clairement impliquées par chaque nom et phrase :
son (on peut le faire résonner), lumiere (on peut l'allumer pour éclairer), couper
(tranchant utilisable), levier (appui rigide utilisable pour faire levier) et allumage
(l'objet produit lui-même des étincelles ou une flamme pour allumer une AUTRE source).
tranchable décrit au contraire une propriété de la cible : une lame adaptée peut entamer
son corps. Elle n'implique pas que l'objet lui-même soit un outil.
Recevoir une flamme ne confère pas allumage à l'objet qui la reçoit.
Un composant intégré à l'objet fait partie du sujet décrit.
Liste vide
si le texte n'en donne aucun indice. Un objet ne reçoit pas une capacité par son seul type
proposé : le nom ou sa description doivent la rendre intelligible au joueur.
Cherche activement ce que le joueur pourrait vérifier séparément du sujet créé : existence,
position, propriété ou conséquence d'un autre élément. Une phrase plausible n'est pas une
preuve. Examine aussi les sous-entendus et les propositions secondaires. Une capacité
formulée avec une catégorie de cibles hypothétiques n'affirme pas qu'un exemplaire de
cette catégorie existe ici. Une cible particulière
désignée comme présente ou modifiée exige en revanche un fait distinct.
Chaque entrée porte sur un sujet exact et contient un texte exact. Découpe ce texte en
fragments CONTIGUS, dans l'ordre, sans perdre ni modifier aucun caractère, espaces compris.
Sépare une affirmation sur le sujet d'une affirmation autonome sur autre chose.
La mutation_autorisee du sujet sera validée et appliquée par le moteur si ton rapport passe.
L'existence du sujet proposé et ses propriétés descriptives sont donc l'objet de cette
transaction ; ne réclame pas une attestation antérieure pour elles. Cherche ce que la
transaction laisserait sans représentation au-delà de ce sujet.
Pour un savoir_pnj, le sujet est seulement le souvenir ou la croyance du personnage.
La portée du sujet doit respecter sa consigne dans connaissances_a_completer.
Une assertion autonome sur un objet présent, un lieu accessible, un secret, une récompense
ou une évolution de quête exige une représentation distincte. Une expérience passée
personnelle peut rester subjective sans créer de nouvel acteur interactif.
Pour chaque fragment, indique :
- sujet : propriété du seul sujet indiqué, y compris son aspect ou sa relation locale ;
- attestation : fait déjà établi, seulement si le fragment entier est identique à une
  attestation fournie par le moteur ; copie cette attestation dans preuve ;
- ambiance : impression sensorielle autour du sujet (odeur, son de fond, lumière ambiante,
  texture), sans autre objet, passage, personnage, ressource ou indice ;
- sans_preuve : fait autonome nouveau, contradiction ou portée indécidable. Explique-le.
Pour sujet, ambiance et sans_preuve, preuve est vide. Même si l'affirmation semble vraisemblable,
classe-la sans_preuve si elle exige un autre ajout au monde.
Les paroles et inscriptions littérales sont conservées comme citations et ne figurent pas
parmi ces entrées. Rends un rapport pour chaque entrée, dans le même ordre.
"""


def descriptions(reponse, faits=None):
    """Champs libres qui deviendraient des affirmations du MJ sur le monde."""
    mode = reponse.get("mode") if isinstance(reponse, dict) else None
    proposition = reponse.get("proposition") if isinstance(reponse, dict) else None
    if mode not in ("etablir_faits", "enrichir", "enrichir_savoirs") or not isinstance(proposition, dict):
        return []
    admissions = (contexte_admission(faits, proposition)["admissions"]
                  if faits is not None and mode == "etablir_faits" else [])
    resultat = []
    for indice, ajout in enumerate(proposition.get("ajouts", [])):
        if not isinstance(ajout, dict):
            raise ErreurMonde("Description proposée mal formée.", "chaque ajout est un objet JSON.")
        if mode == "etablir_faits" and ajout.get("type") in ("detail", "objet"):
            if not isinstance(ajout.get("nom"), str) or not isinstance(ajout.get("texte"), str):
                raise ErreurMonde("Description proposée mal formée.", f"{ajout['type']} : nom et texte sont des chaînes.")
            autonome = ajout["type"] == "objet"
            if autonome and (not isinstance(ajout.get("capacites"), list)
                            or any(not isinstance(c, dict) or not isinstance(c.get("nature"), str)
                                   for c in ajout["capacites"])):
                raise ErreurMonde("Capacités proposées mal formées.",
                                  "objet : capacites est une liste (éventuellement vide) d'objets {nature, …}.")
            sujet = {"nature": "élément proposé sur un support",
                     "support": ajout.get("ancrage"), "nom": ajout["nom"]}
            sujet["mutation_autorisee"] = (["créer un objet physique", "lier au support",
                                             "enregistrer sa masse, sa mobilité et sa relation physique",
                                             "enregistrer son apparence visible"]
                                            if autonome else
                                            ["créer un aspect local", "lier au support",
                                             "enregistrer son apparence visible"])
            if autonome:
                sujet.update(mobile=ajout.get("mobile"), masse=ajout.get("masse"),
                            materiau=ajout.get("materiau"), relation=ajout.get("relation"),
                            capacites=noms_capacites(ajout.get("capacites", [])))
            attendue = "objet" if autonome else "aspect"
            resultat.append({"sujet": sujet, "texte": ajout["nom"],
                             "representations_autorisees": [attendue]})
            resultat.extend({"sujet": sujet, "texte": phrase,
                             "representations_autorisees": (["aspect", "objet"] if autonome
                                                             else ["aspect"])}
                            for phrase in segments(ajout["texte"]))
        elif mode == "etablir_faits" and ajout.get("type") == "qualification":
            # Même sans prose, chaque propriété proposée a une entrée exacte.
            # La valeur structurée reste distincte d'un récit de son utilisation.
            for champ, valeur in ajout.items():
                if champ in ("type", "ancrage", "moyen"):
                    continue
                sujet = {"nature": "propriété proposée d'un objet existant",
                         "support": ajout.get("ancrage"), "nom": ajout.get("ancrage"),
                         "propriete": champ,
                         "mutation_autorisee": {champ: copy.deepcopy(valeur)},
                         "capacites": (noms_capacites(valeur) if champ == "capacites" else [])}
                if admissions:
                    from .capacites_objet import statut
                    objet = admissions[indice]["proprietes_etablies"]
                    fiche = faits.get("faits_narratifs_proposables", {}).get("qualifiables", {}).get(objet.get("id"), {})
                    capacites = fiche.get("capacites", objet.get("capacites", {}))
                    # Les constats projetés sont des résumés publics sans les
                    # empreintes privées qu'exige statut(). Seul le catalogue
                    # moteur peut attester leur validité ; à défaut, on lit les
                    # propriétés intrinsèques, sans reconstruire ces empreintes.
                    intrinseques = {k: v for k, v in objet.items() if k != "constats_capacites"}
                    sujet["capacites_etablies"] = [c for c in CAPACITES_REVUE
                        if (capacites.get(c) == "etablie" if isinstance(capacites, dict) and c in capacites
                            else statut(intrinseques, c) == "etablie")]
                resultat.append({"sujet": sujet,
                    "texte": json.dumps({champ: valeur}, ensure_ascii=False, sort_keys=True),
                    "representations_autorisees": ["objet", "aspect"]})
        elif mode == "enrichir":
            if not isinstance(ajout.get("description"), str):
                if "type" in ajout:
                    # La forme trahit le mode voulu : un ajout typé décrit un objet ou un lieu.
                    raise ErreurMonde("Ajout typé sous le mode enrichir : mode = etablir_faits (enrichir ne décrit "
                                      "que la facette d'un personnage : personnage, facette, description).",
                                      "mode = etablir_faits pour des ajouts typés.")
                raise ErreurMonde("Description proposée mal formée.", "enrichir : description est une chaîne.")
            sujet = {"nature": "facette d'un personnage",
                     "personnage": ajout.get("personnage"), "facette": ajout.get("facette"),
                     "mutation_autorisee": ["enregistrer cette facette du personnage"]}
            # L'apparence d'un personnage, qu'on la nomme portrait ou aspect, porte la même
            # garantie : rien d'autre que le sujet décrit.
            resultat.extend({"sujet": sujet, "texte": phrase,
                             "representations_autorisees": ["portrait", "aspect"]}
                            for phrase in segments(ajout["description"]))
    if mode == "enrichir_savoirs":
        ajouts = proposition.get("savoirs")
        if not isinstance(ajouts, list):
            raise ErreurMonde("Savoirs proposés mal formés.", "enrichir_savoirs : savoirs est une liste.")
        for ajout in ajouts:
            if (not isinstance(ajout, dict) or not isinstance(ajout.get("sujet"), str)
                    or not isinstance(ajout.get("texte"), str)):
                raise ErreurMonde("Savoir proposé mal formé.", "chaque savoir a sujet et texte (chaînes).")
            sujet = {"nature": "savoir subjectif d'un personnage",
                     "personnage": proposition.get("personnage"),
                     "sujet": ajout["sujet"],
                     "mutation_autorisee": ["enregistrer le souvenir ou la croyance du personnage"]}
            resultat.extend({"sujet": sujet, "texte": phrase,
                             "representations_autorisees": ["savoir_pnj"]}
                            for phrase in segments(ajout["texte"]))
    if (len(resultat) > 24 or any(not isinstance(e["texte"], str) or not e["texte"].strip()
                                   for e in resultat)):
        raise ErreurMonde("Description proposée mal formée.",
                          f"au plus 24 phrases descriptives au total (reçu {len(resultat)}), aucune vide : raccourcis les textes.")
    return resultat


def _sujet(sujet):
    """Le sujet d'une description, tel que la proposition le nomme."""
    for cle in ("nom", "facette", "sujet"):
        if isinstance(sujet.get(cle), str) and sujet[cle]:
            qui = sujet.get("personnage")
            return f"{cle} « {sujet[cle]} »" + (f" de {qui}" if isinstance(qui, str) and qui else "")
    return sujet.get("nature", "sujet")


def controler(entrees, rapport, attestations=()):
    """Les obstacles du rapport de portée, chacun avec son ``attendu`` (``refus.audit``) : la description
    en cause, ce que l'auditeur y a lu et ce qui serait accepté."""
    lignes = rapport.get("descriptions") if isinstance(rapport, dict) else None
    if (not isinstance(lignes, list) or len(lignes) != len(entrees)
            or any(not isinstance(entree, dict)
                   or set(entree) != {"sujet", "texte", "representations_autorisees"}
                   or not isinstance(entree["representations_autorisees"], list)
                   or not entree["representations_autorisees"]
                   for entree in entrees)):
        raise RapportIllisible("Contrôle de portée incomplet.")
    obstacles = []
    capacites_affirmees = {}
    for indice, (entree, ligne) in enumerate(zip(entrees, lignes)):
        if (not isinstance(ligne, dict)
                or set(ligne) != {"representation", "mobilite", "placement", "impact_scenario", "capacites", "fragments"}
                or ligne["representation"] not in (
                    "aspect", "objet", "texte_lisible", "etat_du_monde",
                    "portrait", "savoir_pnj", "indetermine")
                or not isinstance(ligne["mobilite"], list)
                or any(m not in ("amovible", "fixe", "indetermine") for m in ligne["mobilite"])
                or len(ligne["mobilite"]) != len(set(ligne["mobilite"]))
                or ligne["placement"] not in ("pose", "fixe", "contenu", "aucun", "indetermine")
                or ligne["impact_scenario"] not in (
                    "aucun", "objectif", "solution", "indice", "changement", "incertain")
                or not isinstance(ligne["capacites"], list)
                or any(c not in CAPACITES_REVUE for c in ligne["capacites"])
                or len(ligne["capacites"]) != len(set(ligne["capacites"]))
                or not isinstance(ligne["fragments"], list)
                or not 1 <= len(ligne["fragments"]) <= 12
                or any(not isinstance(f, dict)
                       or set(f) != {"texte", "portee", "preuve", "motif"}
                       or any(not isinstance(f[k], str) for k in f)
                       or not f["texte"]
                       or f["portee"] not in ("sujet", "attestation", "ambiance", "sans_preuve")
                       for f in ligne["fragments"])
                or "".join(f["texte"] for f in ligne["fragments"]) != entree["texte"]):
            raise RapportIllisible("Contrôle de portée mal formé.")
        lieu = f"description {indice} ({_sujet(entree['sujet'])})"

        def refuser(motif, accepte, verdict, recu=None, lieu=lieu, texte=entree["texte"]):
            # Le verdict est celui de l'auditeur de portée, rendu tel quel : rien de plus sûr.
            obstacles.append(audit(motif, accepte, partie="description", segment=indice, texte=texte,
                                   recu=recu, verdict=verdict, lieu=lieu))
        if ligne["representation"] not in entree["representations_autorisees"]:
            refuser("La représentation requise par ce fait n'est pas celle de l'ajout proposé.",
                    f"une phrase qui décrit ce sujet comme {' ou '.join(entree['representations_autorisees'])}, "
                    "et rien d'autre", f"représentation {ligne['representation']}")
        declarees = (set(entree["sujet"].get("capacites", []))
                     | set(entree["sujet"].get("capacites_etablies", [])))
        affirmees = set(ligne["capacites"])
        if affirmees - declarees:
            refuser("Une capacité affirmée n'est pas enregistrée sur l'objet.",
                    f"capacites déclarées dans l'ajout ({liste(sorted(declarees))}) : déclare "
                    f"{liste(sorted(affirmees - declarees))} dans capacites, ou ne l'affirme pas dans le texte",
                    f"capacités lues {', '.join(sorted(affirmees))}")
        cle_sujet = (entree["sujet"].get("support"), entree["sujet"].get("nom"))
        capacites_affirmees.setdefault(cle_sujet, set()).update(affirmees)
        relation = entree["sujet"].get("relation")
        if relation is not None and ("indetermine" in ligne["mobilite"]
                                    or ("fixe" in ligne["mobilite"] and relation != "fixe")
                                    or ("amovible" in ligne["mobilite"] and
                                        entree["sujet"].get("mobile") is False)
                                    or ligne["placement"] not in ("aucun", relation)):
            refuser("La fixation ou la mobilité décrite contredit l'objet proposé.",
                    f"une description accordée à relation = {relation}, mobile = {entree['sujet'].get('mobile')}, "
                    "ou ces champs accordés au texte",
                    f"mobilité {', '.join(ligne['mobilite']) or 'aucune'}, placement {ligne['placement']}")
        if ligne["impact_scenario"] != "aucun":
            refuser("Un ajout descriptif ne peut pas modifier ou fournir un objectif de scénario.",
                    "une description sans objectif, solution, indice ni changement du scénario",
                    f"impact {ligne['impact_scenario']}")
        for fragment in ligne["fragments"]:
            portee, preuve = fragment["portee"], fragment["preuve"]
            if portee == "attestation":
                if preuve != fragment["texte"] or preuve not in attestations:
                    refuser("La preuve citée ne correspond pas à une attestation exacte du moteur.",
                            "un fragment recopié mot pour mot d'une attestation du moteur (attestations), ou "
                            "le fragment retiré", ("attestation", "preuve " + citer(preuve)),
                            texte=fragment["texte"])
            elif preuve:
                raise RapportIllisible("Une description cite une preuve hors de sa portée.")
            if portee == "sans_preuve":
                refuser(fragment["motif"] or "Cette affirmation exige un fait distinct.",
                        "le texte sans ce fragment, ou ce fragment établi par un fait distinct proposé à part",
                        ("sans_preuve", fragment["motif"]), texte=fragment["texte"])
    for indice, entree in enumerate(entrees):
        declarees = set(entree["sujet"].get("capacites", []))
        cle_sujet = (entree["sujet"].get("support"), entree["sujet"].get("nom"))
        if declarees - capacites_affirmees[cle_sujet]:
            manquantes = sorted(declarees - capacites_affirmees[cle_sujet])
            obstacles.append(audit("Une capacité proposée n'est pas annoncée par le nom ou la description.",
                                   f"un nom ou une description qui annonce {liste(manquantes)}, ou capacites "
                                   "sans elles", partie="description", segment=indice, texte=entree["texte"],
                                   verdict=("capacités lues", ""),
                                   lieu=f"description {indice} ({_sujet(entree['sujet'])})"))
            capacites_affirmees[cle_sujet].update(declarees)
    return obstacles
