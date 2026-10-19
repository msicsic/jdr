"""Portée des descriptions libres proposées comme faits persistants.

Une description d'un sujet ne doit pas établir au passage un autre fait autonome.
Le contrôleur doit couvrir le texte entier et justifier chaque affirmation autonome.
"""

from .monde import ErreurMonde
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

INSTRUCTIONS = """Tu fais la contre-revue de descriptions proposées par le MJ.
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


def descriptions(reponse):
    """Champs libres qui deviendraient des affirmations du MJ sur le monde."""
    mode = reponse.get("mode") if isinstance(reponse, dict) else None
    proposition = reponse.get("proposition") if isinstance(reponse, dict) else None
    if mode not in ("etablir_faits", "enrichir", "enrichir_savoirs") or not isinstance(proposition, dict):
        return []
    resultat = []
    for ajout in proposition.get("ajouts", []):
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


def controler(entrees, rapport, attestations=()):
    lignes = rapport.get("descriptions") if isinstance(rapport, dict) else None
    if (not isinstance(lignes, list) or len(lignes) != len(entrees)
            or any(not isinstance(entree, dict)
                   or set(entree) != {"sujet", "texte", "representations_autorisees"}
                   or not isinstance(entree["representations_autorisees"], list)
                   or not entree["representations_autorisees"]
                   for entree in entrees)):
        raise ErreurMonde("Contrôle de portée incomplet.")
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
            raise ErreurMonde("Contrôle de portée mal formé.")
        if ligne["representation"] not in entree["representations_autorisees"]:
            obstacles.append({"partie": "description", "segment": indice,
                              "texte": entree["texte"],
                              "motif": "La représentation requise par ce fait n'est pas celle de l'ajout proposé."})
        declarees = set(entree["sujet"].get("capacites", []))
        affirmees = set(ligne["capacites"])
        if affirmees - declarees:
            obstacles.append({"partie": "description", "segment": indice,
                              "texte": entree["texte"],
                              "motif": "Une capacité affirmée n'est pas enregistrée sur l'objet."})
        cle_sujet = (entree["sujet"].get("support"), entree["sujet"].get("nom"))
        capacites_affirmees.setdefault(cle_sujet, set()).update(affirmees)
        relation = entree["sujet"].get("relation")
        if relation is not None and ("indetermine" in ligne["mobilite"]
                                    or ("fixe" in ligne["mobilite"] and relation != "fixe")
                                    or ("amovible" in ligne["mobilite"] and
                                        entree["sujet"].get("mobile") is False)
                                    or ligne["placement"] not in ("aucun", relation)):
            obstacles.append({"partie": "description", "segment": indice,
                              "texte": entree["texte"],
                              "motif": "La fixation ou la mobilité décrite contredit l'objet proposé."})
        if ligne["impact_scenario"] != "aucun":
            obstacles.append({"partie": "description", "segment": indice,
                              "texte": entree["texte"],
                              "motif": "Un ajout descriptif ne peut pas modifier ou fournir un objectif de scénario."})
        for fragment in ligne["fragments"]:
            portee, preuve = fragment["portee"], fragment["preuve"]
            if portee == "attestation":
                if preuve != fragment["texte"] or preuve not in attestations:
                    obstacles.append({"partie": "description", "segment": indice,
                                      "texte": fragment["texte"],
                                      "motif": "La preuve citée ne correspond pas à une attestation exacte du moteur."})
            elif preuve:
                raise ErreurMonde("Une description cite une preuve hors de sa portée.")
            if portee == "sans_preuve":
                obstacles.append({"partie": "description", "segment": indice,
                                  "texte": fragment["texte"],
                                  "motif": fragment["motif"] or "Cette affirmation exige un fait distinct."})
    for indice, entree in enumerate(entrees):
        declarees = set(entree["sujet"].get("capacites", []))
        cle_sujet = (entree["sujet"].get("support"), entree["sujet"].get("nom"))
        if declarees - capacites_affirmees[cle_sujet]:
            obstacles.append({"partie": "description", "segment": indice,
                              "texte": entree["texte"],
                              "motif": "Une capacité proposée n'est pas annoncée par le nom ou la description."})
            capacites_affirmees[cle_sujet].update(declarees)
    return obstacles
