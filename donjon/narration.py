"""Contrôle commun des assertions du MJ avant leur affichage.

Le contrôle s'applique à la prose finale du MJ. Les affirmations mécaniques
(entités, positions, passages, possession, ressources, lumière, présence des PNJ,
missions, résultats) doivent découler des faits fournis ; une invention dans ces
domaines est refusée. L'ambiance est libre et enregistrée avec son lieu. Un nom
d'entité absent de tout ce que le MJ a reçu est refusé sans dépendre de l'auditeur.
Le texte libre accepté est complété par les comptes rédigés par le moteur.
"""
from . import agendas

import copy
import re

from .monde import ErreurMonde, normaliser
from . import lexique
from .refus import RapportIllisible, audit, liste as en_liste
from .noms import REGLE_DESIGNATIONS, hors_designations
from .propositions import SCHEMA_OFFRE


VERDICTS = ("neutre", "hypothese", "ambiance", "parole", "engagement", "mecanique",
            "invention_protegee", "contradictoire")
NATURES = ("neutre", "hypothese", "ambiance", "parole", "engagement", "mecanique")
AMBIANCES_PAR_LIEU = 30


def echanges_passes(monde, interlocuteurs):
    """Paroles réellement entendues, sans fenêtre globale ni identité privée.

    Les références sont celles de la scène actuelle, même si une présentation
    a changé depuis la parole. Le texte enregistré reste une citation historique.
    """
    from .voix import reel
    dossier = {ref: [{k: copy.deepcopy(p[k]) for k in ("texte", "revision", "minute") if k in p}
                 for p in monde.data.get("paroles_pnj", [])
                  if p["locuteur"] == reel(monde, ref) and "joueur" in p["auditeurs"]]
            for ref in interlocuteurs}
    for ref, paroles in dossier.items():
        # La révision est un compteur croissant, pas un numéro de tentative
        # narrative. Le registre ne contient pas la réponse encore proposée.
        paroles.sort(key=lambda p: (p.get('revision', 0), p.get('minute', 0)))
        for ordre, parole in enumerate(paroles, 1):
            parole['ordre_chronologique'] = ordre
            parole['anteriorite'] = {
                'par_rapport_a': 'reponse_en_cours_non_encore_prononcee',
                'statut': 'deja_prononcee_et_entendue_par_Corvus',
                'revision_courante': monde.data['revision'],
            }
            parole['rappel_exact'] = _rappel_exact(interlocuteurs[ref]['nom'], parole['texte'])
    return dossier


def _rappel_exact(nom, texte):
    return f"Tu as entendu {nom} dire : « {texte} »."


def rappels_exacts(faits):
    """Rendus historiques attribués, jamais des assertions sur leur contenu.

    La phrase entière est construite par le moteur : aucune recherche de mots
    introducteurs dans la prose du MJ ne peut exempter une affirmation libre.
    """
    catalogue = {}
    for ref, paroles in faits.get('echanges_passes', {}).items():
        if ref not in faits.get('interlocuteurs', {}):
            continue
        for parole in paroles:
            texte = parole.get('texte')
            if not isinstance(texte, str) or not texte.strip():
                continue
            # Le découpage commun du lot 95 borne les citations : jamais un
            # sous-texte arbitraire qui pourrait retirer une négation ou condition.
            for mots in dict.fromkeys([texte, *segments(texte)]):
                catalogue[_rappel_exact(faits['interlocuteurs'][ref]['nom'], mots)] = ref
                catalogue[f'« {mots} »'] = ref
    return catalogue


SCHEMA_RAPPELS = {"type": "array", "maxItems": 12,
    "description": "Toute affirmation du segment sur ce qu'un interlocuteur a dit ou fait envers "
        "Corvus dans un échange passé distinct de l'issue courante, même dans une nouvelle réplique, "
        "quel que soit le verdict. Extrais le sens et situe l'événement affirmé dans le temps, "
        "sans rechercher une formule particulière. L'issue courante (acte, "
        "perception, réaction ou absence de réaction) relève des faits et résultats actuels, "
        "pas des échanges passés, même raconté à un temps accompli. Ne l'extrais pas dans "
        "rappels ; sa compatibilité mécanique reste à contrôler avec les sources actuelles. "
        "Une décision actuelle ou une croyance sur le monde n'est pas un rappel. "
        "Compare les seuls événements antérieurs aux echanges_passes et aux "
        "résultats enregistrés fournis ; compatible ne signifie pas que le contenu ancien est vrai.",
    "items": {"type": "object", "additionalProperties": False,
        "properties": {"locuteur": {"type": "string"},
            "affirmation": {"type": "string"},
            "compatibilite": {"type": "string", "enum": ["etablie", "sans_fondement", "contradictoire"]}},
        "required": ["locuteur", "affirmation", "compatibilite"]}}


def attestations(monde, contexte):
    """Phrases produites par l'état courant, utiles au MJ pour formuler les faits mécaniques.

    Une référence à un objet entier ne prouve pas une phrase libre à son sujet. Le
    catalogue reste volontairement distinct des données utiles pour décider d'agir.
    """
    from .rendu import decrire, regarder, decrire_perception, decrire_contexte

    scene = " ".join(ligne.strip() for ligne in regarder(monde).splitlines()
                     if ligne.strip() and not ligne.startswith("=="))
    textes = [scene, decrire_perception(monde), decrire_contexte(monde)]
    for objet in contexte["objets_perceptibles"]:
        if objet["visible"]:
            from .voix import reel
            textes.append(decrire(monde, reel(monde, objet["id"]), technique=False))
    from .perception import non_vus_connus
    textes.extend(f"Tu ne vois pas {entite['nom']} en ce moment."
                  for entite in non_vus_connus(monde))
    return list(dict.fromkeys(p for texte in textes for p in segments(texte) if p))


def rendre_resultat(resultat):
    """Affiche les conséquences rédigées par le moteur, sans la ligne de calcul du jet."""
    lignes = [ligne for ligne in resultat.splitlines() if not ligne.startswith("1d20(")]
    return "\n".join(lignes).strip() or "Action accomplie."


SCHEMA_AUDIT = {
    "type": "object", "additionalProperties": False,
    "properties": {"segments": {"type": "array", "maxItems": 24,
        "items": {"type": "object", "additionalProperties": False,
            "properties": {
                "indice": {"type": "integer"},
                "verdict": {"type": "string", "enum": list(VERDICTS)},
                "sources": {"type": "array", "items": {"type": "string"}},
                "portee_mecanique": {"type": "string", "enum": ["aucune", "etablie", "sans_fondement", "contradictoire"]},
                "locuteur": {"type": "string"},
                "citation": {"type": "string"},
                "presentation": {"type": "string", "description": "Nom dont le locuteur se présente dans sa citation, y compris une réponse nominale ; vide pour une mention de tiers ou une autre parole."},
                "entites": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                "motif": {"type": "string"},
            },
            "required": ["indice", "verdict", "sources", "portee_mecanique", "locuteur", "citation", "presentation", "entites", "motif"]}},
    },
    "required": ["segments"],
}
CHAMPS_AUDIT = set(SCHEMA_AUDIT["properties"]["segments"]["items"]["required"])

def compte_bien_forme(c):
    if not isinstance(c, dict):
        return False
    if c.get("etat") == "offre":
        from .propositions import erreur_terme
        def terme(t):
            return erreur_terme(t) is None
        return (set(c) == set(SCHEMA_OFFRE["required"])
                and all(isinstance(c[k], str) for k in ("debiteur", "creancier"))
                and terme(c["condition"]) and terme(c["contrepartie"]))
    return (set(c) == {"debiteur", "creancier", "objet", "montant", "etat"}
            and all(isinstance(c[k], str) for k in ("debiteur", "creancier", "objet"))
            and type(c["montant"]) is int and c["montant"] >= -1
            and c["etat"] in ("du", "rendu", "absent"))


def schema_audit(faits, nombre):
    """Les sources citables sont exactement les clés fournies : une référence inventée
    ou un chemin approximatif ne peut pas être produit. Une entrée obligatoire par segment,
    sous la clé de son indice : un rapport ne peut ni sauter, ni fusionner, ni ajouter un segment."""
    def ligne():
        item = copy.deepcopy(SCHEMA_AUDIT["properties"]["segments"]["items"])
        item["properties"]["sources"]["items"] = {"type": "string", "enum": sorted(faits)}
        del item["properties"]["indice"]
        item["required"] = [k for k in item["required"] if k != "indice"]
        # Nature et fondement sont deux questions indépendantes : une absence
        # non prouvée reste une affirmation de nature mécanique. Le verdict
        # est déduit à la lecture, jamais demandé une seconde fois au modèle.
        del item["properties"]["verdict"]
        item["required"].remove("verdict")
        item["properties"]["nature"] = {"type": "string", "enum": list(NATURES),
            "description": "Nature du segment, indépendamment de son fondement mécanique ; "
                "le moteur déduit le verdict de cette nature et de portee_mecanique."}
        item["required"].append("nature")
        if "echanges_passes" in faits:
            item["properties"]["rappels"] = copy.deepcopy(SCHEMA_RAPPELS)
            item["required"].append("rappels")
        if "perception" in faits:
            item["properties"]["eclairages"] = {"type": "array", "maxItems": 12,
                "items": {"type": "string"},
                "description": "Identifiants des sources dont le segment affirme une contribution actuelle "
                    "à la lumière perçue ici, indépendamment du verdict. Extrais l'affirmation du texte, "
                    "pas la liste des faits. Une parole citée n'établit pas la vérité de son contenu. "
                    "Une source seulement vue, éteinte, supposée ou rappelée comme souvenir "
                    "n'affirme aucune contribution actuelle : []."}
            item["required"].append("eclairages")
        # Le motif n'intervient que dans un refus sémantique. Les champs
        # d'extraction ne portent un sens que pour les natures correspondantes.
        variantes = []
        for nature in NATURES:
            for refuse in (False, True):
                variante = copy.deepcopy(item)
                proprietes = variante["properties"]
                proprietes["nature"] = {"type": "string", "enum": [nature],
                                       "description": item["properties"]["nature"]["description"]}
                proprietes["portee_mecanique"]["enum"] = (
                    ["sans_fondement", "contradictoire"] if refuse else ["aucune", "etablie"])
                retirer = []
                if nature not in ("parole", "engagement"):
                    retirer.extend(("locuteur", "citation", "presentation"))
                if nature not in ("ambiance", "engagement"):
                    retirer.append("entites")
                if not refuse:
                    retirer.append("motif")
                else:
                    proprietes["motif"]["maxLength"] = 240
                for cle in retirer:
                    del proprietes[cle]
                    variante["required"].remove(cle)
                variantes.append(variante)
        return {"anyOf": variantes}
    cles = [str(i) for i in (range(nombre) if isinstance(nombre, int) else nombre)]
    return {"type": "object", "additionalProperties": False,
            "properties": {"segments": {"type": "object", "additionalProperties": False,
                                        "properties": {c: ligne() for c in cles}, "required": cles}},
            "required": ["segments"]}


def textes_etablis(faits):
    """Catalogue exact, sans normalisation ni inférence à partir d'une prose libre.

    Seuls les champs de rendu du moteur font autorité, jamais la demande, une
    proposition refusée, une consigne, une croyance ou un attendu technique.
    Une citation historique autonome n'établit pas la vérité de son contenu.
    """
    catalogue = {}
    def ajouter(texte, source):
        if isinstance(texte, str):
            for passage in segments(texte):
                catalogue[passage] = source
    from .comptes_narratifs import phrases
    for texte in phrases(faits):
        ajouter(texte, "comptes")
    for texte in faits.get("attestations", []):
        ajouter(texte, "attestations")
    for cle in ("resultat_resolu", "conversation_validee"):
        bloc = faits.get(cle) or {}
        for texte in bloc.get("faits", []):
            ajouter(texte, cle)
        ajouter(bloc.get("issue"), cle)
    ajouter((faits.get("retour_moteur") or {}).get("obstacle"), "retour_moteur")
    for parole in faits.get("paroles_entendues", []):
        if isinstance(parole, dict) and isinstance(parole.get("texte"), str):
            catalogue["« " + parole["texte"] + " »"] = "paroles_entendues"
    for texte in rappels_exacts(faits):
        ajouter(texte, "echanges_passes")
    return catalogue


def segments_etablis(texte, faits):
    catalogue = textes_etablis(faits)
    etablis = {str(i): {"verdict": "mecanique", "sources": [catalogue[p]],
                     "portee_mecanique": "aucune", "locuteur": "", "citation": "",
                     "presentation": "", "entites": [], "motif": "",
                     **({"rappels": []} if "echanges_passes" in faits else {}),
                     **({"eclairages": []} if "perception" in faits else {})}
            for i, p in enumerate(segments(texte)) if p in catalogue}
    return etablis


class AuditIllisible(RapportIllisible):
    """Le rapport de l'auditeur est mal formé : une faute de l'auditeur, pas du texte contrôlé."""

INSTRUCTIONS_AUDIT = """Tu contrôles une réponse du maître du jeu avant qu'un joueur la voie.
Le jeu distingue deux sortes d'affirmations sur le monde.
Mécaniques : objets et personnages identifiés, positions, sorties et passages, portes et
attaches, possession, ressources (or, PV, combustible), lumière, présence des PNJ, missions,
récompenses, résultats d'action, indices et solutions. Elles doivent découler des faits fournis.
La vue courante est déjà fournie par l'état : perception.objets_visibles énumère exactement
les objets vus maintenant (les objet:<id> dont visible=true). Ce que Corvus voit ou ne voit
pas maintenant est mecanique, source perception, y compris une non-perception visuelle.
perception.non_vus_connus établit explicitement les entités déjà connues que Corvus ne voit
pas maintenant, indépendamment de la surface couverte. Cela prouve leur non-perception
visuelle, jamais leur absence ni leur position actuelle. Un souvenir de position ne prouve
pas où l'entité se trouve maintenant : l'ignorance de sa position actuelle n'est pas une absence.
Les attestations donnent aussi des formulations exactes du moteur, prouvées sans audit.
perception.couverture_vue borne les conclusions d'absence : portee aucune, partielle ou salle désigne
la surface réellement vue maintenant, jamais l'exploration mémorisée. Même une lumière
perçue ici ne garantit pas que toute la salle soit visible (orientation, murs, ombres).
Une absence de personne ou d'objet est une affirmation mécanique, jamais neutre : distingue
ne pas percevoir et ne pas être là. Une liste objets_visibles vide ne prouve aucune absence
hors de la surface couverte. Une absence dans toute la salle fondée sur la seule vue exige couverture_vue.portee=salle
et une cible décelable à ce niveau de visibilité ; les contenus cachés restent exclus.
Sans perception qui l'établit, classe sa portee_mecanique sans_fondement, même dans un segment
mixte avec une limite de vue vraie, même si le verdict proposé serait neutre. Une parole
de PNJ établit seulement qu'il l'a dite, pas la vérité de l'absence qu'il affirme.
Dire « tu ne vois pas de… ici » ne prétend ni avoir fouillé ni prouver que toute la salle
est vide. Juge ce que la réponse affirme, indépendamment d'une demande de chercher : elle
peut répondre sur la seule vue actuelle sans prétendre avoir exécuté cette recherche.
Cette liste ne décrit ni ce qui est caché, ni l'intérieur d'un contenant fermé, ni ce qui
est hors de vue ou dans le noir ; elle n'en prouve jamais l'absence. Les objets accessibles
mais visible=false et les souvenirs ne sont pas vus maintenant.
Un résultat positif ou négatif qui dépasse la perception courante (fouille, recherche de
traces, écoute derrière une porte, examen d'un contenu caché) doit venir d'une perception
exécutée par le moteur, dans resultat_resolu ou les résultats enregistrés. Une demande,
un plan préparé ou le seul silence des faits ne prouve aucun résultat de ce geste.
Sans cette source, c'est invention_protegee, jamais ambiance ; avec elle, c'est mecanique.
Ambiance : aspect, odeur, son de fond, température, texture, impression. Elle est libre tant
qu'elle ne crée ni objet manipulable, ni passage, ni personnage, ni ressource, ni indice.
Examine CHAQUE segment fourni, y compris ce qu'il sous-entend, et classe-le en entier :
Juge aussi sa portee_mecanique, indépendamment de sa forme et de son verdict : aucune,
etablie (cite les sources qui établissent exactement son effet ou sa condition),
sans_fondement, ou contradictoire (cite ce qui la contredit). Ce jugement porte aussi sur
les citations : une parole peut rapporter une croyance fausse sans la rendre vraie, mais
ne peut fixer elle-même un effet ou les termes d'une opération mécanique. Ces termes
doivent déjà venir de l'état ou d'une décision typée du moteur. Le fait d'avoir parlé,
la demande du joueur et un contenu propos vide ne prouvent aucun de ces termes.
- neutre : aucune affirmation sur le monde (salutation, question, conseil, invitation) ;
- hypothese : possibilité explicitement présentée comme incertaine ;
- ambiance : description sensorielle libre ; liste dans entites les éléments évoqués,
  en quelques mots chacun (« odeur de vase », « gouttes au plafond »). Ce que fait sentir un
  objet perçu dans l'état que disent les faits (le crépitement ou la fumée d'un feu allumé, la
  lueur d'une lanterne, l'eau qui clapote là où il y en a) est ambiance : les faits n'ont pas à
  le fournir ;
- mecanique : affirmation mécanique soutenue par les faits ; cite dans sources les clés
  des faits qui la soutiennent (par exemple objet:<id>, perception, salle, engagements).
  L'état du corps (blessure, conscience, mort, prise et liens) est mécanique : etat_corps
  et les résultats du moteur en font foi ; un geste demandé ou commencé ne prouve pas son issue.
  La vue courante et ses absences ont la source perception ; qu'il ne voie pas un objet dont il
  n'a qu'un souvenir (souvenirs_visuels, hors_de_vue) est mecanique, avec cette source ;
- parole : propos nouveau d'un personnage présent, attribué explicitement ; donne son
  identifiant exact et la citation littérale présente dans le segment ; son contenu peut être faux.
  Le passé des échanges et des gestes envers Corvus reste mécanique, même affirmé dans
  une nouvelle réplique. echanges_passes donne par référence publique les mots réellement
  entendus de chaque interlocuteur ; les résultats enregistrés établissent ses gestes.
  Extrais dans rappels les affirmations sur un échange passé distinct de l'issue courante,
  indépendamment du verdict, et juge leur compatibilité. Situe l'événement affirmé :
  les actes, perceptions, réactions et absences de réaction de l'issue courante relèvent
  des faits et résultats actuels, même racontés à un temps accompli ; ils ne sont pas
  des rappels et restent soumis au contrôle mécanique de leurs sources actuelles.
  La liberté du contenu d'une parole ne permet pas de réécrire ces échanges. Un rappel sans
  fondement ou contraire est refusé ; une décision actuelle reste libre de formulation.
  Un rappel seul est mecanique, avec sa source ; il atteste qu'il l'a dit, pas que c'est vrai ;
- engagement : un personnage présent s'engage à faire ce qui changerait le monde (se déplacer,
  donner, apporter, ouvrir, payer, aider) ou accepte de le faire, de sa bouche (« je vais me
  pousser », « je te l'apporte », « d'accord, j'y vais ») ou annoncé par le récit (« il va
  s'écarter ») ; locuteur = ce personnage ; citation = ses mots littéraux s'il parle, sinon vide ;
  entites = l'engagement qui le prévoit, recopié mot pour mot de
  esprits_interlocuteurs.<locuteur>.engagements ou de conversation_validee.faits, vide si rien ne
  le prévoit. Rappeler un engagement déjà dit (paroles_entendues) reste mecanique ;
- invention_protegee : crée ou suppose un élément mécanique absent des faits (objet utilisable,
  passage, personnage, ressource, indice, résultat), même plausible ou décoratif ;
- contradictoire : contraire aux faits, à la perception, à ambiance_etablie ou aux effets prévus ;
  cite dans sources les faits qui établissent cette contradiction. Un fait absent n'établit
  pas son contraire. Juge la compatibilité d'une ambiance nouvelle, pas sa présence dans le
  contexte ni la connaissance de sa cause. Une absence de sensation peut être une ambiance libre
  si elle ne conclut pas au résultat d'une perception active ni à l'absence d'un élément mécanique ;
  une perception déjà décrite ou un état mécanique incompatible peut la contredire.
Si un segment mêle plusieurs catégories, choisis la plus contraignante : contradictoire,
invention_protegee, engagement, parole, mecanique, ambiance, hypothese, neutre.
conversation_validee est une parole de Corvus que le moteur a déjà fait entendre : issue dit ce qu'il
en a établi (Corvus l'a dite, à qui, qui lui répond) ; la raconter, ou dire qu'elle résonne, est
mecanique, source conversation_validee. Ceux de conversation_validee.repondent lui répondent, et eux
seuls : la réplique de l'un d'eux, avec ses propres mots, est une parole (verdict parole), que rien
n'a à prévoir ni à fournir mot pour mot : ses mots manquent toujours des faits, ce n'est ni une
invention ni une contradiction ; seul ce qu'elle affirme peut contredire l'issue, et ce qu'elle
promet est un engagement. Dire que l'un d'eux se tait, ne répond pas ou ne l'a pas entendu est
contradictoire. repondent vide :
personne ne lui répond. Les temoins l'ont entendue et se taisent : dire qu'ils se taisent est
mecanique, source conversation_validee. Dans objet:<id>, a_portee_de_main
dit si Corvus peut le toucher d'ici ; a_portee_de_voix, si un personnage et lui s'entendent.
L'historique, une proposition non exécutée et une parole de personnage ne prouvent pas leur
contenu. resultat_resolu.gestes sont les gestes que Corvus vient d'accomplir, exécutés par le
moteur : les raconter, dans la manière que demande resultat_resolu.intention (style, rythme,
posture, mots choisis), est mecanique, source resultat_resolu ; leurs suites sont celles de
resultat_resolu.faits, sans autre effet. Si retour_moteur indique qu'aucune action n'a été exécutée ou que rien n'a été dit, raconter
comme fait ou commencé un geste du joueur (frapper, saisir, attendre, s'approcher, parler), ou
qu'un personnage lui répond ou y réagit, est contradictoire : seule l'explication de ce qui l'en
empêche est permise. Les champs à rendre dépendent du verdict et de la portée,
selon le schéma : aucun motif pour un segment admis ; un motif de refus bref
(240 caractères au plus). Ne fournis aucun champ absent de la variante choisie.
Rends un contrôle par segment, sous la clé de son indice, sans réécrire ni redécouper les segments.
"""

INSTRUCTIONS_AUDIT += "\n" + REGLE_DESIGNATIONS

INSTRUCTIONS_REVISION = """\nLe contrôle de tes réponses précédentes dans ce tour (controle_narratif, chaque phrase
refusée et son motif) a relevé une rupture du contrat narratif. Chaque refus a son attendu : où (partie, segment),
ce qui a été reçu (la phrase ou la valeur en cause, citée), le verdict de l'auditeur s'il vient de
lui, et ce qui serait accepté. Corrige ce qu'il désigne, garde le reste ; il ne s'adresse jamais au joueur.
Réponds de nouveau à l'intention initiale, à partir de l'état actuel. L'ambiance reste libre.
Tu peux proposer un ajout persistant par le protocole déjà disponible si l'état et
la demande le permettent. Une inconnue mécanique se dit par la limite de perception ou de savoir
qui la cause dans la fiction. Une ambiance compatible se décrit directement comme perçue.
Les motifs et verdicts servent à corriger le texte, jamais à qualifier le récit par leur preuve.
Ne reproduis aucune phrase refusée. Appelle la fonction demandée une fois.
"""

REGLE_NARRATION = """
Le narrateur raconte le geste et le ton, sans affirmer aucun compte : le moteur écrit
les comptes et les offres. Seules les répliques citées des PNJ peuvent les évoquer,
avec un sens, des montants et des conditions compatibles avec l'issue et les offres
fournies ; elles ne créent aucun effet.
Ce que tu affirmes sur l'état mécanique (objets, personnages, positions, passages, possession,
ressources, lumière, missions, résultats) doit découler des faits fournis ; pour créer un
élément mécanique, propose un fait persistant lorsque ce mode est disponible. L'ambiance
(aspect, odeur, son de fond, texture, impression) est libre si elle ne crée ni objet
manipulable, ni passage, ni personnage, ni ressource, ni indice. Reste cohérent avec
ambiance_etablie : une ambiance admise est perçue, sans réserve qui la démente.
Ne nomme pas un objet ou un lieu dont les faits ne parlent pas.
Dis une inconnue mécanique par sa limite de perception ou de savoir dans la fiction.
Le récit parle de ce que tu perçois, sais ou supposes, jamais du degré de preuve fourni au MJ
(établi, attesté, indiqué, absence d'indication). L'ambiance libre n'a pas à justifier son origine.
Le joueur lit ton texte tel quel, justification comprise : écris-le à la deuxième personne (tu).
Hors des répliques citées entre « et », personne n'y dit « je », ni toi ni Corvus, et il ne nomme
ni Corvus, ni le joueur, ni le moteur, le MJ, le scénario, les faits ou les données : une
incertitude se dit de ce que Corvus sait, à la deuxième personne (« tu ne sais pas si… »).
Le quadrillage et les coordonnées restent internes : les positions se disent avec les repères
fournis, des directions et des distances en mètres ou en pas, jamais en cases ni en coordonnées.
Une voix inconnue (interlocuteurs.voix_<n>) se désigne dans le récit par son nom d'interlocuteur
(« la voix qui se dit … », « une voix »), jamais par le nom qu'elle prétend. Une réplique ne nomme
que qui son locuteur connaît (personne ne sait le nom de Corvus s'il ne l'a pas entendu).
"""




def segments(texte):
    """Découpage de couverture ; une assertion mixte condamne son segment entier."""
    passages, debut, citation = [], 0, 0
    texte = texte.strip()
    for i, caractere in enumerate(texte):
        if caractere == "«":
            citation += 1
        elif caractere == "»":
            citation = max(0, citation - 1)
        fin_phrase = (caractere in ".!?" and citation == 0
                      and (i + 1 == len(texte) or texte[i + 1].isspace()))
        # La ponctuation finale d'une réplique appartient aussi à la phrase qui
        # l'attribue. Une nouvelle phrase après » doit avoir son propre audit,
        # et donc son propre locuteur ; l'incise en minuscule reste dans la même.
        suite = texte[i + 1:].lstrip()
        fin_replique = (caractere == "»" and citation == 0 and i > 0
                        and texte[:i].rstrip().endswith((".", "!", "?", "…"))
                        and (not suite or suite[0].isupper()))
        if fin_phrase or fin_replique or caractere == "\n":
            passage = texte[debut:i + 1].strip()
            if passage:
                passages.append(passage)
            debut = i + 1
    dernier = texte[debut:].strip()
    if dernier:
        passages.append(dernier)
    return passages


def fondement(entree):
    """Ce que le MJ a reçu pour répondre, hors des croyances des personnages présents,
    normalisé pour le contrôle lexical."""
    faits = {k: v for k, v in entree.get("faits", {}).items() if k != "esprits_interlocuteurs"}
    return lexique.corpus(faits, entree.get("conversation", []), entree.get("message", ""))


def fondement_paroles(entree):
    """Ce que croient les personnages présents : seule leur bouche peut le dire."""
    return lexique.corpus(entree.get("faits", {}).get("esprits_interlocuteurs", {}))


CITATIONS = re.compile(r"«[^»]*»|“[^”]*”|\"[^\"]*\"")


def hors_paroles_etablies(monde, texte, paroles=(), faits=None, historique=True):
    """Exempte le seul emplacement audité ; un souvenir n'autorise aucune attribution libre."""
    citations = list(CITATIONS.finditer(texte))
    actuelles = {p['texte'].strip() for p in paroles if p.get('passage') == texte
                 and sum(c.group()[1:-1].strip() == p['texte'].strip() for c in citations) == 1}
    mots = {p['texte'].strip() for p in monde.data.get('paroles_joueur', [])}
    mots.update(p['texte'].strip() for p in monde.data.get('paroles_pnj',[]) if 'joueur' in p['auditeurs'])
    mots.update(s for p in monde.data.get('paroles_pnj', []) if 'joueur' in p['auditeurs']
                for s in segments(p['texte']))
    validee = (faits or {}).get('conversation_validee') or {}
    if validee.get('operation') == 'parole_joueur' and isinstance(validee.get('replique_joueur'), str):
        mots.add(validee['replique_joueur'].strip())
    def remplacer(citation):
        mots_cites = citation.group()[1:-1].strip()
        # Une citation passée peut être répétée seule, sans nouvelle relation d'identité.
        autonome = (historique and mots_cites in mots
                    and (texte.strip() == citation.group() or texte.strip() in rappels_exacts(faits or {})))
        return ' ' if mots_cites in actuelles or autonome else citation.group()
    return CITATIONS.sub(remplacer, texte)


def tel_quel(passage, extrait):
    """Les mots du passage, tels qu'écrits, dont la forme normalisée est ``extrait`` (« tu demandes a
    ilse » → « Tu demandes à Ilse ») : un refus cite le texte exact. À défaut, ``extrait``."""
    for i in range(len(passage)):
        if normaliser(passage[i]) != extrait[:1]:
            continue
        for j in range(i + len(extrait), min(len(passage), i + 2 * len(extrait) + 4) + 1):
            if normaliser(passage[i:j]) == extrait:
                return passage[i:j]
    return extrait


def mentions(monde, texte, base, paroles="", partie="texte", lieu=None, paroles_validees=None):
    """Obstacles déterministes : noms d'entités absents de ce que le MJ a reçu. Ce qu'un
    personnage croit ne se dit que par sa bouche, entre guillemets ; la narration n'en use pas.
    Un obstacle par nom, au premier segment qui le porte. ``lieu`` remplace « partie, segment »
    quand le texte n'est pas une réponse découpée pour l'auditeur (le texte d'un ajout)."""
    obstacles, vus = [], set()
    for indice, passage in enumerate(segments(texte)):
        citations = CITATIONS.findall(hors_paroles_etablies(monde,passage))
        validees={p['texte'].strip() for p in (paroles_validees or ())
                  if p.get('passage') == passage
                  and sum(c[1:-1].strip() == p['texte'].strip() for c in citations) == 1}
        recit = CITATIONS.sub(" ", passage)
        trouves = ([(m, False) for m in lexique.mentions_sans_fondement(monde, recit, base)]
                   + [(m, True) for citation in citations for m in lexique.mentions_sans_fondement(
                       monde,citation,base+(" "+paroles if paroles_validees is None
                           or citation[1:-1].strip() in validees else ""))])
        for m, cite in trouves:
            if m["terme"] in vus:
                continue
            vus.add(m["terme"])
            mot = tel_quel(passage, m["terme"])
            if not cite and paroles and lexique._motif(m["terme"]).search(paroles):
                # Un personnage présent le croit : sa bouche peut le dire, pas le récit.
                accepte = (f"« {mot} » seulement entre guillemets, dans la réplique d'un personnage "
                           "présent qui le croit (esprits_interlocuteurs), ou le passage sans ce nom")
            else:
                accepte = (f"le passage sans « {mot} » : ni ce que Corvus perçoit ou sait, ni ce que croient "
                           "les personnages présents ne le nomment")
            obstacles.append(audit("« " + mot + " » n'apparaît dans rien de ce que Corvus perçoit "
                                   "ou sait. Ne l'introduis pas sans fait établi ; ce qu'un personnage croit "
                                   "ne se dit que dans sa propre réplique.", accepte, partie=partie,
                                   segment=indice, texte=passage, recu=mot,
                                   lieu=lieu and f"{lieu}, segment {indice}"))
    return obstacles


# La personne du récit est un contrat grammatical, distinct du vocabulaire technique.
AUTEUR = re.compile(r"\b(?:le|au|du|un) joueur\b|\bMJ\b|\bCorvus\b|\bje\b|\bj['’]", re.IGNORECASE)

# Un nom commun ne désigne pas à lui seul les sources internes. On exige un lien
# syntaxique explicite : complément technique, source d'information ou opération
# du programme. Les emplois ambigus restent du ressort de l'audit sémantique.
SOURCES_INTERNES = r"(?:faits|donn[ée]es|moteur|sc[ée]nario|champs?|identifiants?)"
# Le moteur sujet d'une opération du contrat, même au subjonctif ou sous
# négation/pronom. Un complément concret (« moteur du moulin ») coupe ce lien.
OPERATIONS_CONTRAT = (r"(?:refus|valid|calcul|d[ée]termin|enregistr|sauvegard|ex[ée]cut|autoris"
                     r"|fourn|reconna|pr[ée]voi|propos|accept|exig|permet|d[ée]clar|expos)")
CONTEXTE_TECHNIQUE = re.compile(
    rf"\b{SOURCES_INTERNES}\s+(?:du|de ce)\s+(?:jeu|programme|syst[èe]me|dossier)\b"
    r"|\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b"
    r"|\b(?:le|du|au) moteur(?=\s+(?:(?:ne|pas|plus|jamais|en|y|le|la|les|te|vous|a|avait|ait|doit|devrait|peut|puisse)\s+|n['’]|l['’])*"
    + OPERATIONS_CONTRAT + r")"
    r"|\b(?:champs?|identifiants?|propositions?|sch[ée]mas?)\s+"
    r"(?:techniques?|internes?|typ[ée]e?s?|JSON|du moteur|du programme)\b"
    r"|\b(?:refus|validation|calcul|enregistrement|sauvegarde|ex[ée]cution|autorisation|d[ée]cision)"
    r"\s+(?:du|par le) moteur\b"
    r"|\b(?:les|des|aux) (?:faits|donn[ée]es)(?=\s+(?:ne\s+)?"
    r"(?:disent|pr[ée]cisent|indiquent|montrent|d[ée]crivent|permettent|fournis|re[çc]us))"
    rf"|\b(?:selon|d['’]apr[èe]s)\s+(?:les? |la |ce |ces |cet )?{SOURCES_INTERNES}\b",
    re.IGNORECASE)

# La réserve sur la preuve existe aussi sans nommer ses sources internes. Ce
# vocabulaire ne suffit cependant pas seul : le passif sans support concret, les
# sujets impersonnels et l'absence d'information commentent ce que le récit sait.
PREUVE_MOTEUR = re.compile(
    r"\b(?:attest[ée]e?s?|[ée]tablie?s?|confirm[ée]e?s?|indiqu[ée]e?s?|pr[ée]cis[ée]e?s?)\b"
    r"|\b(?:rien|aucune?\s+\w+)(?:\s+\w+){0,3}\s+"
    r"(?:ne\s+(?:(?:te|lui|vous|nous)\s+|[tm]['’])?|n['’])"
    r"(?:indique|atteste|[ée]tablit|prouve|confirme|pr[ée]cise)\b"
    r"|\b(?:faute|manque|absence)\s+d['’](?:indication|information|preuve)s?\b"
    r"|\baucune?\s+(?:indication|information|preuve)s?\b"
    r"|\b(?:pas|non)(?:\s+\w+){0,3}\s+(?:indiqu[ée]e?s?|pr[ée]cis[ée]e?s?)\b", re.IGNORECASE)

PASSIF_PREUVE = re.compile(
    r"\b(?:est|sont|[ée]tait|[ée]taient|[ée]t[ée]|[êe]tre|reste|restent|demeure|demeurent)"
    r"(?:\s+(?:pas|point|jamais|encore|toujours|plus|bien|clairement|explicitement))*\s*$", re.I)
SUPPORT_CONCRET = re.compile(
    r"\s+(?:par|[àa]|au|aux|dans|sur|sous|pr[èe]s|contre|depuis|en)\b", re.I)


def reserves_preuve(texte):
    """Emplois de preuve ; un acte ou un support concret n'est pas une réserve.

    Les relations grammaticales sont communes aux sujets : aucun nom d'objet,
    de sensation ou de propriété du monde n'est sélectionné ici.
    """
    for m in PREUVE_MOTEUR.finditer(texte):
        if SUPPORT_CONCRET.match(texte, m.end()):
            continue
        if " " not in m.group() and not PASSIF_PREUVE.search(texte[:m.start()]):
            continue  # participe d'un acte, ou qualificatif sans assertion de savoir
        yield m.group()


# Même principe pour les unités : une case de maison ou des coordonnées bancaires
# ne sont pas une localisation sur la grille. Les écritures numériques le sont.
ESPACE_MOTEUR = re.compile(
    r"\b(?:quadrillage|coordonn[ée]es?)\s+(?:interne[s]?|du jeu|de la grille)\b"
    r"|\b(?:aux?|en) coordonn[ée]es?(?=\s*[\[(]?\s*[+-]?\d)"
    r"|\b(?:\d+|une?|deux|trois|quatre|cinq|six|sept|huit|neuf|dix)\s+cases?"
    r"(?=\s+(?:vers|au|[àa]|plus|de|du|en|devant|derri[èe]re|sur)\b)"
    r"|[\[(]\s*[+-]?\d+(?:\.\d+)?\s*[,;]\s*[+-]?\d+(?:\.\d+)?\s*[\])]"
    r"|\b[xy]\s*=\s*[+-]?\d+", re.IGNORECASE)


def unites_moteur(texte, partie="texte"):
    return [audit("Cette localisation emploie le quadrillage interne.",
                  "une localisation dans la fiction : repère, direction, distance en mètres ou en pas",
                  partie=partie, segment=i, texte=p, recu=m.group())
            for i, p in enumerate(segments(texte)) for m in ESPACE_MOTEUR.finditer(p)]


def verifier_unites(texte, partie):
    """Même garde à l'écriture d'une prose persistante qu'à sa proposition."""
    obstacles = unites_moteur(texte, partie)
    if obstacles:
        raise ErreurMonde("Cette description doit employer les repères du lieu.", obstacles[0]["attendu"])


# Déictiques de position : ils ne désignent jamais une orientation historique.
# Les citations des personnages restent des paroles, dont le contenu peut être faux.
RELATIFS_JOUEUR = re.compile(
    r"\b(?P<axe>devant|derri[èe]re)\s+toi\b|\b(?:[àa]|sur)\s+ta\s+(?P<cote>gauche|droite)\b"
    r"|\bdans\s+ton\s+(?P<dos>dos)\b|\b(?P<face>en\s+face\s+de)\s+toi\b", re.I)


def reperes_orientation(faits):
    """Seulement les positions déjà publiques : perception et dernière observation."""
    objets = {o["id"]: o for o in faits.get("objets_perceptibles", [])}
    objets.update({k[6:]: o for k, o in faits.items() if k.startswith("objet:")})
    reperes = {o["id"]: o for o in faits.get("souvenirs_visuels", [])}
    return {**reperes, **objets}


def cibles_orientation(texte, faits):
    from .noms import motif_designation
    return {ref for ref, o in reperes_orientation(faits).items() if any(
        motif_designation(nom).search(texte) for nom in
        [o.get("nom", "").split(",")[0], *o.get("aliases", [])] if nom)}


def sujet_locatif(proposition, avant_locatif, ref, faits):
    """Reconnaît seulement une attribution directe ; un nom unique ne suffit pas.

    « Gorm regarde quelque chose derrière toi » ne localise pas Gorm.
    Les autres constructions restent à lire par l'auditeur.
    """
    from .noms import motif_designation
    objet = reperes_orientation(faits)[ref]
    for nom in [objet.get("nom", "").split(",")[0], *objet.get("aliases", [])]:
        if not nom:
            continue
        for mention in motif_designation(nom).finditer(proposition[:avant_locatif]):
            lien = normaliser(proposition[mention.end():avant_locatif]).strip()
            if (re.match(r"(?:est|se trouve|se tient)\b", lien)
                    and not re.search(r"\b(?:il|elle|ils|elles|qui|que|mais|puis|tandis|quand)\b", lien)):
                return True
    return False


def orientations(texte, faits, partie="texte"):
    """Compare les locatifs explicites aux seuls repères publics courants.

    Une cible ou une polarité ambiguë reste du ressort de l'audit sémantique.
    La garde ne devine ni antécédent entre propositions, ni portée d'une négation.
    Même un segment classé neutre ou ambiance subit cette comparaison.
    """
    fiction = CITATIONS.sub(" ", texte)
    if not faits.get("mode_cases") or not RELATIFS_JOUEUR.search(fiction):
        return []
    reperes = reperes_orientation(faits)
    nommees = cibles_orientation(fiction, faits)
    demandees = set(faits.get("reperes_demandes", [])) & reperes.keys()
    obstacles = []
    for indice, passage in enumerate(segments(texte)):
        hors_citations = CITATIONS.sub(" ", passage)
        for m in RELATIFS_JOUEUR.finditer(hors_citations):
            # Un nom dans une autre proposition n'est pas l'antécédent établi
            # du locatif (« Gorm ... : elle a été vue ... »).
            debut = max(hors_citations.rfind(sep, 0, m.start()) for sep in ':;') + 1
            fins = [p for sep in ':;' if (p := hors_citations.find(sep, m.end())) >= 0]
            proposition = hors_citations[debut:min(fins, default=len(hors_citations))]
            visees = cibles_orientation(proposition, faits)
            nommee = bool(visees)
            if not visees and not nommees and len(demandees) == 1:
                visees = demandees
            direction = normaliser(m.group("axe") or m.group("cote") or (
                "derriere" if m.group("dos") else "devant"))
            ref = next(iter(visees)) if len(visees) == 1 else None
            o = reperes.get(ref, {})
            lieu = o.get("localisation") or o
            admises = lieu.get("orientation_relative", [])
            if ref is None or not admises or direction in admises:
                continue
            if nommee and not sujet_locatif(proposition, m.start() - debut, ref, faits):
                continue
            # Une négation peut porter sur un autre prédicat du même segment.
            # Elle ne prouve donc jamais, à elle seule, un locatif faux.
            negatif = re.search(r"\b(?:pas|plus|jamais|ni)\b", normaliser(proposition))
            if negatif:
                continue
            accepte = (f"{ref} : orientation_relative={admises}, "
                       f"repère absolu={lieu.get('position_relative', lieu.get('vu_a', 'inconnu'))}"
                       if ref is not None else "une cible publique nommée sans ambiguïté et son repère courant")
            obstacles.append(audit("Cette direction relative ne correspond pas à un repère courant univoque.",
                accepte + "; employer sa direction actuelle ou son repère absolu en mètres ; "
                "un souvenir ne garantit pas la présence actuelle", partie=partie, segment=indice,
                texte=passage, recu=m.group()))
    return obstacles


def eclairages(sources, faits, passage, indice, partie="texte"):
    """La contribution perçue établit l'effet, indépendamment de la vue de la source."""
    admises = {c["source"] for c in faits.get("perception", {}).get("contributions", [])
               if c.get("source") and c.get("niveau", 0) > 0}
    return [audit("Cette source ne contribue pas à la lumière perçue ici.",
                  f"perception.contributions : une source avec niveau > 0, parmi {sorted(admises)} ; "
                  "voir une source ou s'en souvenir ne suffit pas à établir son effet actuel",
                  partie=partie, segment=indice, texte=passage, recu=source)
            for source in dict.fromkeys(sources) if source not in admises]


def voix_auteur(texte, partie="texte"):
    """Obstacles déterministes : le texte affiché parle au joueur, à la deuxième personne, dans la
    fiction ; il ne parle ni du joueur, ni du moteur, ni de Corvus à la troisième personne. Les
    répliques citées des personnages restent libres."""
    obstacles, vus = unites_moteur(texte, partie), set()
    for indice, passage in enumerate(segments(texte)):
        fiction = CITATIONS.sub(" ", passage)
        for terme in sorted({m.group(0) for regle in (AUTEUR, CONTEXTE_TECHNIQUE)
                             for m in regle.finditer(fiction)} | set(reserves_preuve(fiction)), key=str.lower):
            if terme.lower() in vus:
                continue
            vus.add(terme.lower())
            obstacles.append(audit(
                f"Le joueur lit ce texte tel quel : écris-le à la deuxième personne, dans la fiction, sans « {terme} ».",
                f"le passage à la deuxième personne (tu), dans la fiction, sans « {terme} » hors d'une réplique "
                "entre guillemets" + _reecrire(terme), partie=partie, segment=indice, texte=passage, recu=terme))
    return obstacles


def _reecrire(terme):
    """Comment se dit, à la deuxième personne, ce que ce mot d'auteur disait : une indication pour que la
    première correction suffise."""
    mot = normaliser(terme)
    if PREUVE_MOTEUR.fullmatch(terme):
        return (" : décris directement l'ambiance compatible comme perçue, sans réserve de preuve ; "
                "pour une inconnue mécanique, dis la limite de perception ou de savoir dans la fiction")
    if mot in ("je", "j'", "j’"):
        return " : ce que tu dirais de toi se dit de ce que Corvus perçoit, sait ou ignore (« tu ne sais pas si… »)"
    if mot in ("corvus",) or mot.endswith("joueur"):
        return " : Corvus est « tu »"
    return " : dis ce que Corvus perçoit, sait ou ignore, sans parler du jeu"


def mentions_proposees(monde, reponse, base, paroles=""):
    """Même contrôle pour les textes d'un ajout persistant : détail, objet, inscription,
    parole, portrait ou savoir. Le nom propre de l'élément créé fait partie de l'ajout."""
    proposition = reponse.get("proposition") if isinstance(reponse, dict) else None
    if (reponse.get("mode") not in ("etablir_faits", "enrichir", "enrichir_savoirs")
            or not isinstance(proposition, dict)):
        return []
    obstacles = []
    groupes = [("ajouts", a) for a in proposition.get("ajouts", [])] + [("savoirs", a) for a in proposition.get("savoirs", [])]
    rangs = {"ajouts": 0, "savoirs": 0}
    for groupe, ajout in groupes:
        rang = rangs[groupe]
        rangs[groupe] += 1
        if not isinstance(ajout, dict):
            continue
        propre = lexique.corpus(ajout.get("nom", "")) if isinstance(ajout.get("nom"), str) else ""
        # Un savoir prêté à un personnage peut reprendre ce qu'il croit.
        if groupe == "savoirs":
            propre += " " + paroles
        for champ in ("nom", "texte", "description"):
            if isinstance(ajout.get(champ), str) and ajout[champ].strip():
                obstacles.extend(unites_moteur(ajout[champ],
                                              f"proposition.{groupe}[{rang}].{champ}"))
                obstacles.extend(mentions(monde, ajout[champ], base + " " + propre, partie="description",
                                          lieu=f"proposition.{groupe}[{rang}].{champ}",
                                          paroles_validees=[] if groupe=='ajouts' and ajout.get('type')!='parole' else None))
                if groupe=='ajouts' and ajout.get('type')!='parole':
                    obstacles.extend(voix_inconnues(monde,[],{},ajout[champ],partie='description',
                                                    citations_historiques=False))
    return obstacles


def engagements_prevus(faits, locuteur):
    """Ce que le moteur a prévu que ce personnage fera : ses engagements enregistrés et l'issue
    qu'il vient de valider pour lui (conversation_validee)."""
    esprit = (faits.get("esprits_interlocuteurs") or {}).get(locuteur) or {}
    prevus = list(agendas.declares(esprit) or [])
    dossier = faits.get("comptes", {})
    prevus += [phrase for o, phrase in zip(dossier.get("offres", []), dossier.get("formulations_offres", []))
               if o["debiteur"] == locuteur]
    validee = faits.get("conversation_validee")
    if isinstance(validee, dict) and (validee.get("personnage") == locuteur
                                      or locuteur in (validee.get("destinataires") or [])):
        prevus += list(validee.get("faits") or [])
    return {p.strip() for p in prevus if isinstance(p, str) and p.strip()}


def destinataires_parole(faits, locuteur):
    """Ceux qui répondent à la parole que Corvus vient de dire (conversation_validee.repondent : ses
    destinataires, et qui l'a entendue à la cantonade et a choisi de répondre), seuls à lui répondre ;
    sans parole de Corvus validée, rien ne restreint ``locuteur``."""
    validee = faits.get("conversation_validee")
    for cle in ("repondent", "destinataires"):
        if isinstance(validee, dict) and isinstance(validee.get(cle), list):
            return [x for x in validee[cle] if isinstance(x, str)]
    return [locuteur]


# Les formes par lesquelles une réplique dit qui parle : ce qui suit est un nom que seul le moteur peut
# donner à une voix inconnue. Une seule règle, celle de la parole de Corvus (``paroles.SE_NOMMER``).
from .paroles import SE_NOMMER  # noqa: E402


def voix_inconnues(monde, paroles, faits, texte="", partie="texte", citations_historiques=True):
    """Obstacles déterministes : une voix que Corvus ne sait à qui prêter (un interlocuteur
    ``voix_inconnue``) ne dit pas qui elle est au-delà de ce que le moteur lui fait dire : le nom
    qu'elle s'est donné (son nom d'interlocuteur) et ce qu'établit l'issue de cette parole
    (``conversation_validee``, la réplique de Corvus). Qui elle est, c'est au moteur de le décider
    (``voix.se_nommer``) ; le MJ ne le sait pas. Le moteur, lui, sait qui parle (``voix.reel``) et
    ce qu'il sait : elle nomme qui elle connaît (``voix.connait_nom`` ; Corvus, seulement s'il lui a
    donné son nom ou qu'elle a entendu parler de lui), jamais elle-même. Une voix que le moteur ne
    relie à personne ne nomme rien de plus que ce qui est établi. Le récit, hors des répliques, ne
    lui donne pas non plus le nom qu'elle s'est donné : c'est « la voix qui se dit … », pas cette
    personne."""
    interlocuteurs = faits.get("interlocuteurs") or {}
    passages = segments(texte) if texte.strip() else []
    obstacles = _noms_non_appris_recit(monde, paroles, faits, interlocuteurs, passages,
                                       partie, citations_historiques)
    obstacles.extend(_noms_voix_recit(monde, paroles, faits, interlocuteurs, passages,
                                      partie, citations_historiques))
    obstacles.extend(_noms_repliques(monde, paroles, faits, interlocuteurs, passages, partie))
    return obstacles


def _nom_court(monde, identifiant):
    """Nom littéral cité par les refus, sans modifier le contrat de leur message."""
    personne = monde.joueur if identifiant == "joueur" else monde.objets[identifiant]
    return personne["nom"].split(",")[0]


def _noms_non_appris_recit(monde, paroles, faits, interlocuteurs, passages, partie, historique):
    """Le narrateur ne nomme pas un corps dont le joueur n'a pas appris le nom."""
    from .voix import connait_nom, nom_pour_joueur
    obstacles = []
    for indice, passage in enumerate(passages):
        recit = hors_paroles_etablies(monde, passage, paroles, faits, historique)
        for identifiant, objet in monde.objets.items():
            voix_deja_controlee = any(
                isinstance(entree, dict) and entree.get("voix_inconnue")
                and identifiant in lexique.entites_citees(monde, entree.get("nom", ""))
                for entree in interlocuteurs.values())
            if (objet["type"] == "personnage" and not connait_nom(monde, "joueur", identifiant)
                    and not voix_deja_controlee):
                nom_ = objet["nom"].split(",")[0].split()[0]
                motif = r"(?<!\w)" + re.escape(lexique.normaliser(nom_)) + r"(?!\w)"
                if re.search(motif, lexique.normaliser(recit), re.I):
                    obstacles.append(audit("Le joueur n'a pas appris ce nom.",
                        "dans le récit : « " + nom_pour_joueur(monde, identifiant) + " », sans son nom",
                        partie=partie, segment=indice, texte=passage, recu=nom_))
    return obstacles


def _noms_voix_recit(monde, paroles, faits, interlocuteurs, passages, partie, historique):
    """Une appellation de voix ne devient pas une étiquette d'identité dans le récit."""
    obstacles = []
    for cle, entree in interlocuteurs.items():
        nom = entree.get("nom", "") if isinstance(entree, dict) and entree.get("voix_inconnue") else ""
        dits = sorted(x for x in lexique.entites_citees(monde, nom)
                      if x in monde.objets and monde.objets[x]["type"] == "personnage")
        for indice, passage in enumerate(passages if dits else []):
            recit = lexique.normaliser(hors_paroles_etablies(monde, passage, paroles, faits, historique))
            reste = hors_designations(recit, [lexique.normaliser(nom.split("(")[0])]) if nom else recit
            nommes = [x for x in dits if x in lexique.entites_citees(monde, reste)]
            if nommes:
                obstacles.append(audit(
                    f"Corvus ne sait pas qui parle : c'est {nom}, pas cette personne. Dans le récit, désigne-la "
                    "comme une voix (« la voix qui se dit … »), sans lui donner ce nom.",
                    f"dans le récit, cette voix ({cle}) se désigne comme dans interlocuteurs.{cle}.nom, « {nom} », "
                    f"jamais par « {_nom_court(monde, nommes[0])} » seul", partie=partie, segment=indice, texte=passage,
                    recu=_nom_court(monde, nommes[0])))
                break
    return obstacles


def _noms_repliques(monde, paroles, faits, interlocuteurs, passages, partie):
    """Le locuteur ne prononce que ses appellations connues ou établies par l'échange."""
    from .voix import connait_appellation, reel
    validee = faits.get("conversation_validee") or {}
    obstacles = []

    def nom_court(identifiant):
        return _nom_court(monde, identifiant)

    for parole in paroles:
        entree = interlocuteurs.get(parole["locuteur"]) or {}
        inconnue = bool(entree.get("voix_inconnue"))
        etabli = " ".join([entree.get("nom", "") if inconnue else "", *map(str, validee.get("faits") or []),
                           str(validee.get("replique_joueur", ""))])
        permis = lexique.entites_citees(monde, etabli)
        permis |= lexique.entites_citees(monde,parole.get('presentation',''))
        qui = reel(monde, parole["locuteur"])
        qui = qui if qui in monde.objets and monde.objets[qui]["type"] == "personnage" else None
        if not inconnue and qui is None:
            continue

        def tait(x):
            # Une voix inconnue : son propre nom, seulement s'il est établi. Tout locuteur : un autre, s'il
            # le sait (``voix.connait_nom``) ou si l'échange l'établit.
            if not inconnue and x == qui:
                return False
            return x not in permis and (qui is None or x == qui or not connait_appellation(monde, qui, x))
        nommes = sorted(x for x in lexique.entites_citees(monde, parole["texte"])
                        if x in monde.objets and monde.objets[x]["type"] == "personnage" and tait(x))
        if inconnue:
            # Se dire quelqu'un, c'est se nommer : seul le moteur en décide (``voix.se_nommer``).
            nommes += sorted(x for x in lexique.entites_citees(monde, " ".join(
                m.group(1) for m in SE_NOMMER.finditer(lexique.normaliser(parole["texte"]))))
                if x in monde.objets and monde.objets[x]["type"] == "personnage" and x not in permis
                and x not in nommes)
        corvus = re.compile(r"\b" + re.escape(lexique.normaliser(monde.joueur["nom"].split(",")[0])) + r"\b")
        if (corvus.search(lexique.normaliser(parole["texte"])) and not corvus.search(lexique.normaliser(etabli))
                and (qui is None or not connait_appellation(monde, qui, "joueur"))):
            nommes.append("joueur")  # Elle ne sait pas son nom.
        # La réplique est citée telle quelle dans un segment : c'est lui qui est en cause.
        indice = next((i for i, p in enumerate(passages) if f"« {parole['texte']} »" in p
                       or parole["texte"] in p), None)
        for x in nommes:
            if inconnue:
                motif = (f"{entree.get('nom', 'Cette voix')} : Corvus ne sait pas qui parle. Sa réplique ne se "
                         "nomme pas au-delà de ce que le moteur a établi (son nom d'interlocuteur, "
                         f"conversation_validee) et ne nomme que qui elle connaît : retire « {nom_court(x)} ».")
                accepte = (f"une réplique de {parole['locuteur']} sans « {nom_court(x)} » : elle ne se nomme que par "
                           f"interlocuteurs.{parole['locuteur']}.nom et conversation_validee, et ne nomme que qui "
                           "elle connaît")
            else:
                motif = (f"{nom_court(qui)} ne connaît pas le nom de {nom_court(x)} : une réplique ne nomme que qui "
                         f"son locuteur connaît. Retire « {nom_court(x)} ».")
                accepte = (f"une réplique de {parole['locuteur']} sans « {nom_court(x)} » (« toi », « l'étranger »…) : "
                           f"{parole['locuteur']} n'a ni entendu ce nom ni appris qui le porte")
            obstacles.append(audit(motif, accepte, partie=partie, segment=indice,
                                   texte=passages[indice] if indice is not None else parole["texte"],
                                   recu=nom_court(x)))
    return obstacles


def clarification_nominale(monde, intention, texte, faits):
    """Une référence saisie sans lien nominal n'est pas une question sur le corps
    secret qui porte ce nom. Si le récit essaie néanmoins de l'employer, le moteur
    demande une désignation publique. Il ne demande pas au MJ de rédiger un démenti
    que le même garde nominal refuserait. Aucun nom ni lien privé n'est autorisé.

    Les paroles déjà validées et les résultats d'action gardent leurs transactions
    et leur contrôle ordinaires ; une parole peut mentionner un tiers sans le viser.
    """
    if faits.get("conversation_validee") or faits.get("resultat_resolu"):
        return None
    from .noms import PERSONNES
    from .paroles import _personnage
    for refus in voix_inconnues(monde, [], faits, texte):
        # ``recu`` n'est pas structuré dans un refus d'audit : les noms sont relus
        # dans l'état, jamais extraits de son message ou de celui de l'auditeur.
        # Une dépouille est une personne pour les noms (``noms.PERSONNES``).
        passage = refus["texte"]
        for id, o in monde.objets.items():
            if o["type"] not in PERSONNES:
                continue
            nom = o["nom"].split(",")[0].split()[0]
            motif = re.compile(r"(?<!\w)" + re.escape(normaliser(nom)) + r"(?!\w)")
            if (motif.search(normaliser(intention)) and motif.search(normaliser(passage))
                    and _personnage(monde, nom) is None):
                return ("Tu ne sais pas à qui rattacher ce nom. Désigne la personne par ce que tu vois "
                        "ou entends, ou demande-lui son nom.")
    return None


def citations_nouvelles(texte, faits):
    """Mots cités entre guillemets que rien de ce que le MJ a reçu ne contient : une parole
    nouvelle, et non le rappel d'une parole entendue ou d'une inscription. Le retour du moteur
    n'en fait pas partie : une proposition refusée n'a rien fait dire à personne."""
    connus = lexique.corpus({k: v for k, v in faits.items() if k != "retour_moteur"})
    cites = [(c, lexique.corpus(c.strip("«»“”\" "))) for c in CITATIONS.findall(texte)]
    return [c for c, mots in cites if mots and mots not in connus]


# Les formes par lesquelles un récit fait parler Corvus, à la deuxième personne (texte normalisé,
# sans accents ni guillemets). Un verbe qui dit aussi autre chose (« tu dis que… » rapporte la saisie,
# « tu lances » un geste) ne compte qu'avec un destinataire : « lui », « leur », « à … » ou un
# deux-points. Un verbe qui vise une personne (« tu appelles Ilse ») compte avec son objet, sauf
# « à l'aide », qui est un geste. Les formes inversées (« dis-tu ») ne servent qu'à citer Corvus.
_DIRE = ("dis|demandes|parles|reponds|lances|expliques|annonces|racontes|avoues|confies|affirmes|repetes"
         "|chuchotes|murmures|cries|proposes|promets|ordonnes|retorques|souffles|glisses|precises")
_DIT = ("dit|demande|parle|repondu|lance|explique|annonce|raconte|avoue|confie|affirme|repete|chuchote"
        "|murmure|crie|propose|promis|ordonne|retorque|souffle|glisse|precise")
_INTERPELLER = "appelles|interpelles|heles|salues|questionnes|supplies|remercies|previens"
_INTERPELLE = "appele|interpelle|hele|salue|questionne|supplie|remercie|prevenu"
PAROLE_DE_CORVUS = re.compile(
    rf"\btu (?:lui|leur) (?:as )?(?:{_DIRE}|{_DIT})\b"
    # « demander à + infinitif » (« tu demandes à passer ») : demander de pouvoir faire, pas parler à quelqu'un.
    rf"|\btu (?:as )?(?:{_DIRE}|{_DIT}) (?:a(?! \w+(?:er|ir|re|oir)\b)|au|aux)\b"
    rf"|\btu (?:as )?(?:{_DIRE}|{_DIT}) ?:"
    rf"|\btu (?:l'|la |le |les )?(?:as )?(?:{_INTERPELLER}|{_INTERPELLE}) (?!a\b)(?=\w)"
    rf"|\btu t'(?:es )?adresse[s]? a\b"
    rf"|\b(?:{_DIRE}|ajoutes|insistes|reprends|enchaines|appelles)-tu\b")
HYPOTHESE = re.compile(r"(?:\bsi|\bs'|\bquand|\blorsque|\bpour que|\bavant que)\s*$")


def parole_racontee(texte):
    """Les passages où le récit fait parler Corvus (« Tu demandes à Ilse… », « tu lui dis »,
    « « Viens », dis-tu ») ; une hypothèse (« si tu lui demandes ») n'en est pas une."""
    from .monde import normaliser
    recit = " ".join(normaliser(CITATIONS.sub(" , ", texte)).split())
    # Le passage cité va jusqu'au mot qui suit : « tu demandes a ilse », « tu appelles aubin ».
    return [recit[m.start():m.end()] + re.match(r"[^\s,.;:!?]*(?: [^\s,.;:!?]+)?", recit[m.end():]).group(0)
            for m in PAROLE_DE_CORVUS.finditer(recit)
            if not HYPOTHESE.search(recit[max(0, m.start() - 14):m.start()])]


def paroles_sans_moteur(texte, faits, adresse=False, partie="texte"):
    """Obstacles déterministes : une parole n'a lieu que si le moteur l'a fait entendre. Sans parole de
    Corvus validée dans ce tour (conversation_validee) ni geste résolu (resultat_resolu), le récit ne
    fait pas parler Corvus ; et quand rien n'a été dit — après un refus (retour_moteur), ou quand la
    saisie s'adresse à quelqu'un (``adresse``) sans que le moteur ait fait entendre une parole —
    personne ne lui répond : aucune citation nouvelle."""
    if isinstance(faits.get("conversation_validee"), dict) or isinstance(faits.get("resultat_resolu"), dict):
        return []
    prevu = (faits.get("parole_prevue") or {}).get("personnage") if isinstance(faits.get("parole_prevue"), dict) else None
    parler = "mode parole_joueur" + (f" (personnage = {prevu})" if prevu and prevu != "personne" else "")
    refus = isinstance(faits.get("retour_moteur"), dict)
    obstacles = []
    for indice, passage in enumerate(segments(texte)):
        for dit in map(lambda d: tel_quel(passage, d), parole_racontee(passage)):
            obstacles.append(audit(
                f"Corvus n'a rien dit dans ce tour : le récit ne le fait pas parler (« {dit} »). Si le joueur fait "
                "parler Corvus, propose parole_joueur : le moteur fixe à qui il parle et la fait entendre ; s'il "
                "agit, propose l'action.",
                f"{parler} si Corvus parle, le moteur la fait entendre ; mode action s'il agit ; sinon un récit où "
                "Corvus ne parle pas", partie=partie, segment=indice, texte=passage, recu=dit))
        for citation in citations_nouvelles(passage, faits) if refus or adresse else []:
            if refus:
                # Après un refus, rien n'a eu lieu : le motif vient du moteur, aucun personnage ne le connaît,
                # ne le dit ni ne réagit, quelle que soit la voie (action, parole, conversation, faits).
                obstacles.append(audit(
                    "Aucune action ni parole n'a eu lieu : c'est toi qui expliques l'obstacle. Aucun personnage "
                    "ne parle ni ne réagit ; ne cite entre guillemets que des paroles déjà entendues.",
                    "le passage sans cette citation : tu expliques toi-même l'obstacle de retour_moteur ; entre "
                    "guillemets, seulement des paroles déjà entendues (paroles_entendues, conversation)",
                    partie=partie, segment=indice, texte=passage, recu=citation.strip("«»“”\" ")))
            else:
                obstacles.append(audit(
                    "Le joueur s'adresse à un personnage, mais rien n'a encore été dit : personne ne répond à "
                    "une parole que le moteur n'a pas fait entendre. Si Corvus parle, propose parole_joueur ; "
                    "le personnage répondra ensuite.",
                    f"{parler} si Corvus parle (le personnage répondra ensuite) ; sinon le passage sans cette "
                    "citation", partie=partie, segment=indice, texte=passage, recu=citation.strip("«»“”\" ")))
    return obstacles


def _cles_visees(faits, passage):
    """Les clés objet:<id> fournies dont le nom (son premier mot, « brasero » de « brasero en fer »)
    figure dans ce passage : celles qui pourraient l'appuyer. Une indication, pas une preuve."""
    mots = set(re.findall(r"[a-z0-9]+", normaliser(passage)))
    tetes = {k: re.findall(r"[a-z0-9]+", normaliser(v["nom"].split(",")[0]))[:1] for k, v in faits.items()
             if k.startswith("objet:") and isinstance(v, dict) and isinstance(v.get("nom"), str)}
    return sorted(k for k, tete in tetes.items() if tete and len(tete[0]) > 2 and tete[0] in mots)


ACCEPTE_VERDICT = {
    "invention_protegee": ("le passage sans cet élément mécanique ; un élément mécanique nouveau passe par un "
                           "fait proposé (etablir_faits) quand le mode est offert, sauf un indice ou un résultat "
                           "de recherche, fouille ou examen : propose alors une action de perception "
                           "(examiner, toucher, ecouter…) sur sa cible, le moteur seul en donne le résultat ; une inconnue mécanique "
                           "se dit par sa limite de perception ou de savoir dans la fiction ; "
                           "l'ambiance compatible reste libre et se décrit directement comme perçue"),
    "contradictoire": ("le passage accordé aux faits fournis (perception, salle, objet:<id>, ambiance_etablie, "
                       "retour_moteur), ou sans cette affirmation"),
}


def cite_entiere(passage, citation):
    """La citation figure entière entre « et » dans le passage (espaces fines ou insécables comprises)."""
    return re.search(r"«\s*" + re.escape(citation) + r"\s*»", passage) is not None


def citation_du_segment(passage, citation):
    """La citation d'une parole est le texte entre « et » du segment : quand celle que recopie l'auditeur
    n'y figure pas telle quelle (« C'est Ilse », répond la voix…, avec les mots d'attribution), c'est la
    réplique du segment qu'elle recouvre, si une seule le fait. Une faute de recopie de l'auditeur ne
    refuse pas la réponse ; une citation qui ne recouvre aucune réplique reste refusée."""
    if not citation or cite_entiere(passage, citation):
        return citation
    cite = normaliser(citation)
    repliques = [r.strip() for r in re.findall(r"«\s*([^»]*?)\s*»", passage)]
    candidates = [r for r in repliques if len(normaliser(r)) >= 3
                  and (normaliser(r) in cite or cite in normaliser(r))]
    return candidates[0] if len(candidates) == 1 else citation


def controler(texte, rapport, faits, partie="texte"):
    """Valide le rapport de l'auditeur et renvoie ses obstacles, jamais sa seule assurance. Chaque
    obstacle porte un ``attendu`` (``refus.audit``) : le segment, la phrase ou la valeur en cause, le
    verdict de l'auditeur tel quel, et ce qui serait accepté."""
    passages = segments(texte)
    lignes = rapport.get("segments") if isinstance(rapport, dict) else None
    if isinstance(lignes, dict):
        # Refaire la preuve exacte à chaque lecture, y compris lors de la
        # sauvegarde. Aucun drapeau du MJ ne peut exempter une phrase libre.
        etablis = segments_etablis(texte, faits)
        lignes = {**lignes, **etablis}
        # Forme demandée à l'auditeur : une entrée par segment, sous la clé de son indice.
        if set(lignes) != {str(i) for i in range(len(passages))}:
            raise AuditIllisible("Contrôle narratif incomplet.")
        lignes = [{**lignes[str(i)], "indice": i} if isinstance(lignes[str(i)], dict) else lignes[str(i)]
                  for i in range(len(passages))]
    elif isinstance(lignes, list) and len(lignes) == len(passages):
        etablis = segments_etablis(texte, faits)
        lignes = [{**etablis[str(i)], "indice": i} if str(i) in etablis else ligne
                  for i, ligne in enumerate(lignes)]
    if (not passages or len(passages) > 24 or not isinstance(lignes, list)
            or len(lignes) != len(passages)):
        raise AuditIllisible("Contrôle narratif incomplet.")
    from .comptes_narratifs import controler as controler_comptes
    locuteurs = {i: l.get('locuteur') for i, l in enumerate(lignes) if isinstance(l, dict)}
    obstacles = orientations(texte, faits, partie) + controler_comptes(texte, faits, partie, locuteurs)
    paroles, ambiances, lignes_validees = [], [], []
    for indice, (passage, ligne) in enumerate(zip(passages, lignes)):
        if isinstance(ligne, dict):
            if "nature" in ligne:
                nature, portee = ligne["nature"], ligne.get("portee_mecanique")
                if ("verdict" in ligne or nature not in NATURES
                        or not isinstance(portee, str)
                        or portee not in ("aucune", "etablie", "sans_fondement", "contradictoire")):
                    raise AuditIllisible("Qualification narrative ambiguë ou mal formée.")
                verdict = ({"sans_fondement": "invention_protegee", "contradictoire": "contradictoire"}
                           .get(portee, nature) if nature == "mecanique" else nature)
                ligne = {k: v for k, v in ligne.items() if k != "nature"}
                ligne["verdict"] = verdict
            verdict = ligne.get("verdict")
            defauts = {}
            if verdict not in ("parole", "engagement"):
                defauts.update(locuteur="", citation="", presentation="")
            if verdict not in ("ambiance", "engagement"):
                defauts["entites"] = []
            if (verdict not in ("invention_protegee", "contradictoire")
                    and ligne.get("portee_mecanique") in ("aucune", "etablie")):
                defauts["motif"] = ""
            ligne = {**defauts, **ligne}
        # Champ extrait par les nouveaux audits, conservé pour l'enregistrement.
        # Les anciens rapports ne portaient pas cette extraction.
        rappels = ligne.get("rappels") if isinstance(ligne, dict) else None
        if rappels is not None:
            if (not isinstance(rappels, list) or len(rappels) > 12 or any(
                    not isinstance(r, dict) or set(r) != {"locuteur", "affirmation", "compatibilite"}
                    or not all(isinstance(r[k], str) for k in r)
                    or r["compatibilite"] not in ("etablie", "sans_fondement", "contradictoire")
                    for r in rappels)):
                raise AuditIllisible("Contrôle des échanges passés mal formé.")
            ligne = {k: v for k, v in ligne.items() if k != "rappels"}
            for rappel in rappels:
                if (rappel["compatibilite"] != "etablie"
                        or rappel["locuteur"] not in faits.get("echanges_passes", {})):
                    precedents = faits.get("echanges_passes", {}).get(rappel["locuteur"], [])
                    obstacles.append(audit("Ce rappel ne correspond pas aux échanges enregistrés.",
                        f"echanges_passes.{rappel['locuteur']} : {precedents} ; "
                        "respecter ces paroles et les résultats enregistrés, ou répondre sans affirmer ce passé",
                        partie=partie, segment=indice, texte=passage, recu=rappel["affirmation"]))
        lumieres = ligne.get("eclairages") if isinstance(ligne, dict) else None
        if lumieres is not None:
            if (not isinstance(lumieres, list) or len(lumieres) > 12
                    or any(not isinstance(s, str) for s in lumieres)):
                raise AuditIllisible("Contrôle des contributions lumineuses mal formé.")
            ligne = {k: v for k, v in ligne.items() if k != "eclairages"}
            obstacles.extend(eclairages(lumieres, faits, passage, indice, partie))
        # Les anciens rapports restent lisibles ; leur extraction comptable
        # n'a plus aucun rôle de preuve ni de décision.
        if isinstance(ligne, dict):
            ligne = {k: v for k, v in ligne.items() if k != "comptes"}
        # Les rapports archivés avant le champ de présentation n'établissent aucune présentation.
        if isinstance(ligne,dict) and 'presentation' not in ligne:
            ligne = {**ligne,'presentation':''}
        if (not isinstance(ligne, dict) or set(ligne) != CHAMPS_AUDIT
                or type(ligne["indice"]) is not int or ligne["indice"] != indice
                or ligne["verdict"] not in VERDICTS
                or ligne.get("portee_mecanique") not in ("aucune", "etablie", "sans_fondement", "contradictoire")
                or not isinstance(ligne["sources"], list)
                or any(not isinstance(s, str) for s in ligne["sources"])
                or not isinstance(ligne["entites"], list)
                or any(not isinstance(e, str) for e in ligne["entites"])
                or any(not isinstance(ligne[k], str) for k in ("locuteur", "citation", "presentation", "motif"))):
            raise AuditIllisible("Contrôle narratif mal formé.")
        verdict = ligne["verdict"]
        # Deux jugements typés d'un même segment ne peuvent simultanément
        # l'établir et le rejeter. Le motif libre n'est pas un champ de vérité.
        portee = ligne["portee_mecanique"]
        if (verdict == "mecanique" and portee in ("sans_fondement", "contradictoire")
                or verdict in ("invention_protegee", "contradictoire") and portee == "etablie"):
            raise AuditIllisible("Le verdict narratif et la portée mécanique se contredisent.")
        # Une source inconnue ne prouve rien : elle est écartée, et une affirmation
        # mécanique sans source restante est refusée plus bas.
        ligne = {**ligne, "sources": [s for s in ligne["sources"] if s in faits]}
        if verdict == "contradictoire" and not ligne["sources"]:
            # Une absence dans le contexte n'est pas une preuve négative. Ce
            # défaut du rapport revient au lecteur, sans faire réécrire le MJ.
            raise AuditIllisible("Une contradiction doit citer le fait qu'elle contredit.")
        if ligne["portee_mecanique"] == "contradictoire" and not ligne["sources"]:
            raise AuditIllisible("Une contradiction mécanique doit citer le fait qu'elle contredit.")
        # Ces champs ne portent aucun sens hors de leur verdict. Les vider évite qu'une
        # erreur de format de l'auditeur rejette un segment contrôlé par son verdict réel.
        if verdict not in ("parole", "engagement"):
            ligne = {**ligne, "locuteur": "", "citation": "", "presentation": ""}
        if verdict not in ("ambiance", "engagement"):
            ligne = {**ligne, "entites": []}
        lignes_validees.append({**ligne,
                               **({"rappels": rappels} if rappels is not None else {}),
                               **({"eclairages": lumieres} if lumieres is not None else {})})
        # La citation est le texte entre les guillemets : ceux que l'auditeur recopie avec elle
        # ne la rendent pas fausse (« D'accord » cité « « D'accord » »).
        locuteur, citation = ligne["locuteur"], ligne["citation"].strip().strip("«»\"“”  ")
        def refuser(motif, accepte, recu=None):
            # Le verdict est celui de l'auditeur, rendu tel quel avec son motif : rien de plus sûr.
            obstacles.append(audit(motif, accepte, partie=partie, segment=indice, texte=passage, recu=recu,
                                   verdict=(verdict, ligne["motif"])))
        if ligne["portee_mecanique"] in ("sans_fondement", "contradictoire"):
            refuser(ligne["motif"] or "La portée mécanique de cette réponse n'est pas établie.",
                    "une réponse dont les effets et conditions mécaniques découlent des sources fournies ; "
                    "sinon ne les affirme pas, même dans une citation ; "
                    f"perception actuelle : {faits.get('perception', {})} ; "
                    "une non-perception ne prouve pas une absence hors de la portée couverte")
        elif (verdict == "mecanique" or ligne["portee_mecanique"] == "etablie") and not ligne["sources"]:
            visees = _cles_visees(faits, passage)
            refuser("Cette affirmation mécanique ne cite aucun fait du moteur.",
                    "une affirmation que soutient un fait fourni, dite comme lui"
                    + (f" (clés qui nomment ce qu'elle vise : {en_liste(visees)})" if visees else "")
                    + ", ou le passage sans elle")
        elif verdict in ("parole", "engagement") and locuteur not in faits.get("interlocuteurs", {}):
            presents = en_liste(faits.get("interlocuteurs") or {})
            refuser("Seul un personnage présent peut parler ; aucun locuteur présent ne correspond à cette parole.",
                    f"un locuteur parmi les interlocuteurs présents ({presents}), ou le passage sans parole",
                    f"locuteur {locuteur}" if locuteur else None)
        elif verdict in ("parole", "engagement") and locuteur not in destinataires_parole(faits, locuteur):
            # Le moteur a décidé l'issue de la parole de Corvus pour ses destinataires seulement.
            destinataires = destinataires_parole(faits, locuteur)
            refuser(("Seuls " + ", ".join(destinataires) + " répondent à Corvus" if destinataires
                     else "Personne ne répond à Corvus") + " ; les autres l'ont entendu sans être interpellés et "
                    "se taisent.",
                    f"une réponse de {en_liste(destinataires)} seulement (conversation_validee.repondent) ; "
                    f"{locuteur} se tait", f"locuteur {locuteur}")
        elif verdict == "engagement" and (not ligne["entites"] or any(
                e.strip() not in engagements_prevus(faits, locuteur) for e in ligne["entites"])):
            # Sa parole atteste qu'il l'a dit ; ce qu'il fera, seul le moteur le décide.
            prevus = sorted(engagements_prevus(faits, locuteur))
            accepte = (f"seulement ce que le moteur a prévu pour {locuteur} : "
                       + " ; ".join(f"« {e} »" for e in prevus) + " ; sinon une réponse sans promesse"
                       if prevus else
                       f"aucun engagement n'est prévu pour {locuteur} : une réponse sans promesse (répondre, "
                       "hésiter, refuser, se taire)")
            refuser("Ce personnage s'engage à agir sans que le moteur l'ait prévu : rien dans "
                    "esprits_interlocuteurs.engagements ni conversation_validee ne le dit. Fais-le répondre sans "
                    "rien promettre (il peut répondre, hésiter, refuser ou se taire), et n'annonce pas qu'il le fera.",
                    accepte, citation or None)
        elif verdict == "parole" or (verdict == "engagement" and citation):
            from .faits_locaux import LONGUEUR_PAROLE
            citation = citation_du_segment(passage, citation)
            if (not 3 <= len(citation.strip()) <= LONGUEUR_PAROLE or any(ord(c) < 32 for c in citation)
                    or len(re.findall(r"«\s*"+re.escape(citation)+r"\s*»",passage)) != 1):
                refuser("Une parole doit être citée entre « et », en entier, dans le segment.",
                        f"la réplique de {locuteur} entière entre « et » dans ce segment, de 3 à {LONGUEUR_PAROLE} "
                        "caractères", f"citation {citation}" if citation else "citation vide")
            else:
                if ligne['presentation'] and not re.search(
                        r'(?<!\w)'+re.escape(ligne['presentation'])+r'(?!\w)',citation):
                    # Un nom extrait sans mots correspondants n'établit aucun
                    # lien nominal. Écarter cette seule donnée ne réécrit ni ne
                    # refuse une réplique contrôlée et ne fait apprendre aucun nom.
                    ligne = {**ligne, "presentation": ""}
                    lignes_validees[-1] = ligne
                paroles.append({"locuteur": locuteur, "texte": citation, "passage": passage,
                                **({'presentation':ligne['presentation']} if ligne['presentation'] else {})})
        elif verdict == "ambiance":
            ambiances.append({"texte": passage,
                              "entites": [e.strip()[:80] for e in ligne["entites"] if e.strip()]})
        elif verdict in ("invention_protegee", "contradictoire"):
            refuser(ligne["motif"] or "Affirmation mécanique non établie.", ACCEPTE_VERDICT[verdict])
    return {"segments": copy.deepcopy(lignes_validees), "paroles": paroles, "ambiances": ambiances,
            "obstacles": obstacles, "texte_controle": texte.strip()}


SUBSTANCE = ("mecanique", "parole", "engagement")


def rescape(texte, rapport, faits, fautif):
    """Les segments d'une réponse que le contrôle a admis, réunis en une réponse qui passe le même
    contrôle : un dernier recours quand aucune réponse entière n'est admise. Chaque segment est
    contrôlé pour lui-même (une assertion mixte condamne son segment entier) : ce qui reste est
    compatible avec l'état. ``fautif(texte)`` : les contrôles déterministes du texte entier (voix
    d'auteur, noms sans fondement, paroles nouvelles), refaits sur chaque segment gardé. Renvoie
    (texte, rapport, nombre d'affirmations), ou None s'il ne reste aucune affirmation mécanique ni
    parole, seulement des politesses ou de l'ambiance qui ne répondent à rien."""
    passages = segments(texte)
    refuses = {o["segment"] for o in rapport["obstacles"]}
    gardes = [(p, ligne) for i, (p, ligne) in enumerate(zip(passages, rapport["segments"]))
              if i not in refuses and not fautif(p)]
    substance = sum(ligne["verdict"] in SUBSTANCE for _, ligne in gardes)
    if not substance:
        return None
    for separateur in (" ", "\n"):
        nouveau = separateur.join(p for p, _ in gardes)
        if segments(nouveau) == [p for p, _ in gardes]:
            break
    else:
        return None
    controle = controler(nouveau, {"segments": {str(k): {c: v for c, v in ligne.items() if c != "indice"}
                                                for k, (_, ligne) in enumerate(gardes)}}, faits)
    if controle["obstacles"] or fautif(nouveau):
        return None
    return nouveau, controle, substance


def repli(monde, faits, message):
    """Ce que dit le moteur quand aucune réponse du MJ n'est admise, sans rien inventer : à une parole,
    que ses destinataires l'ont entendue sans répondre ; à une question, ce que Corvus perçoit de ce
    qu'elle vise (les attestations du moteur qui le nomment), puis ce qui manque pour en dire plus."""
    validee = faits.get("conversation_validee")
    if isinstance(validee, dict) and validee.get("operation") == "parole_joueur":
        noms = [monde.objets[d]["nom"].split(",")[0] for d in validee.get("destinataires") or []
                if d in monde.objets]
        if not noms:
            return "Personne ne te répond."
        qui = noms[0] if len(noms) == 1 else ", ".join(noms[:-1]) + " et " + noms[-1]
        return f"{qui} t'{'a' if len(noms) == 1 else 'ont'} entendu, sans te répondre."
    vises = lexique.entites_citees(monde, message or "")
    phrases, vues = [], set()
    for a in faits.get("attestations", []):
        # Une même phrase du moteur revient avec un autre article (« Un brasero… », « Le brasero… »).
        sans_article = re.sub(r"^(?:un|une|le|la|les|l')\s*", "", lexique.normaliser(a)) if isinstance(a, str) else ""
        if sans_article and sans_article not in vues and vises & lexique.entites_citees(monde, a):
            vues.add(sans_article)
            phrases.append(a)
    phrases = phrases[:3]
    if phrases:
        return " ".join(phrases) + " Ce que tu perçois et ce que tu sais n'en disent pas davantage."
    return ("Rien de ce que tu perçois ou sais ne permet d'y répondre avec certitude. Précise ce que tu "
            "veux regarder, examiner ou tenter.")


def consigner(monde, reponse):
    """Enregistre une réponse contrôlée, ses paroles et son ambiance sur l'état à sauvegarder."""
    audit = reponse.get("_audit")
    salle = monde.joueur["salle"]
    if not audit:
        if reponse.get("_texte_moteur") is not True:
            raise ErreurMonde("Réponse du MJ sans contrôle narratif.")
        monde.data.setdefault("narrations_mj", []).append({
            "texte": reponse["texte"], "revision": monde.data["revision"],
            "sources": ["moteur"]})
        monde.data["narrations_mj"] = monde.data["narrations_mj"][-60:]
        return
    texte = reponse["texte"]
    rapport = controler(audit["texte_initial"], {"segments": audit["segments"]}, audit["faits"])
    if rapport["obstacles"]:
        raise ErreurMonde("Le MJ n'a pas pu formuler une réponse sûre. Aucun changement enregistré.",
                          rapport["obstacles"][0]["attendu"])
    etablis = segments_etablis(audit["texte_initial"], audit["faits"])
    if any(ligne['sources'] == ['echanges_passes'] for ligne in etablis.values()):
        from .dialogues import interlocuteurs
        from .noms import public
        courants = {'interlocuteurs': public(monde, interlocuteurs(monde))}
        courants['echanges_passes'] = echanges_passes(monde, courants['interlocuteurs'])
        actuels = rappels_exacts(courants)
        for indice, ligne in etablis.items():
            passage = segments(audit['texte_initial'])[int(indice)]
            if ligne['sources'] == ['echanges_passes'] and passage not in actuels:
                raise ErreurMonde("Ce rappel ne correspond plus aux paroles entendues.",
                                  f"segment {indice} : reçu {passage!r} ; un rappel exact des échanges enregistrés.")
    if any(ligne["sources"] == ["attestations"] for ligne in etablis.values()):
        actuelles = {s for t in attestations(monde, monde.contexte()) for s in segments(t)}
        for indice, ligne in etablis.items():
            passage = segments(audit["texte_initial"])[int(indice)]
            if ligne["sources"] == ["attestations"] and passage not in actuelles:
                raise ErreurMonde("Cette description ne correspond plus à ce que tu perçois.",
                                  f"segment {indice} : reçu {passage!r} ; une attestation actuelle du moteur.")
    from .perception import eclairage
    from .noms import public
    courants = {"perception": public(monde, eclairage(monde))}
    for indice, ligne in enumerate(rapport["segments"]):
        contraires = eclairages(ligne.get("eclairages", []), courants,
                               segments(audit["texte_initial"])[indice], indice)
        if contraires:
            raise ErreurMonde("Cette lumière ne te parvient plus.", contraires[0]["attendu"])
    if RELATIFS_JOUEUR.search(CITATIONS.sub(" ", texte)):
        contraires = orientations(texte, {**monde.contexte(),
            "reperes_demandes": audit["faits"].get("reperes_demandes", [])})
        if contraires:
            raise ErreurMonde("Cette direction ne correspond plus à ton regard actuel.",
                              contraires[0]["attendu"])
    if (rapport["obstacles"] or rapport["texte_controle"] != texte or voix_auteur(texte)
            or mentions(monde, texte, audit["fondement"], audit.get("fondement_paroles", ""),
                        paroles_validees=rapport['paroles'])
            or voix_inconnues(monde, rapport["paroles"], audit["faits"], texte)):
        # Même base que l'audit : ce qu'un personnage croit peut figurer dans sa propre réplique.
        raise ErreurMonde("Le MJ n'a pas pu formuler une réponse sûre. Aucun changement enregistré.")
    paroles = []
    if rapport["paroles"]:
        from .ouie import auditeurs_parole, _place
        from .dialogues import reels
        from .voix import connaitre, reel
        for parole in rapport["paroles"]:
            # Le MJ désigne une voix inconnue comme le joueur (voix_<n>) : le moteur sait qui parle.
            locuteur = monde.objets[reel(monde, parole["locuteur"])]
            entendants = auditeurs_parole(monde, locuteur["id"])
            if locuteur["id"] not in reels(monde) or "joueur" not in entendants:
                raise ErreurMonde("La voix de ce locuteur ne te parvient plus.",
                                  f"locuteur = {parole['locuteur']} : un interlocuteur actuellement perçu et audible.")
            if monde.visible(locuteur["id"]):
                connaitre(monde, "joueur", locuteur["id"])  # Il le voit parler : il saura reconnaître sa voix.
            # Qui en saisit les mots, par l'ouïe commune ; le joueur, à qui elle s'adresse.
            from .noms import entendre as entendre_noms
            for auditeur in entendants:
                entendre_noms(monde, auditeur, locuteur["id"], parole["texte"])
                if parole.get('presentation'):
                    from .noms import presenter
                    presenter(monde,auditeur,locuteur['id'],parole['presentation'],parole['texte'])
            paroles.append({
                "locuteur": locuteur["id"], "texte": parole["texte"], "salle": _place(monde, locuteur["id"])[0],
                "minute": monde.data["minutes"], "auditeurs": entendants,
                "revision": monde.data["revision"],
                **({'presentation':parole['presentation']} if parole.get('presentation') else {}),
            })
    monde.data.setdefault("narrations_mj", []).append({
        "texte": texte, "revision": monde.data["revision"],
        "sources": sorted({source for ligne in rapport["segments"] for source in ligne["sources"]}),
    })
    monde.data["narrations_mj"] = monde.data["narrations_mj"][-60:]
    monde.data.setdefault("paroles_pnj", []).extend(paroles)
    if rapport["ambiances"]:
        lieu = monde.data.setdefault("ambiances", {}).setdefault(salle, [])
        lieu.extend({**a, "revision": monde.data["revision"]} for a in rapport["ambiances"])
        monde.data["ambiances"][salle] = lieu[-AMBIANCES_PAR_LIEU:]


def chiffres_sans_fondement(texte, *sources):
    """Nombres écrits en chiffres dans le texte et absents des sources du résultat."""
    connus = set(re.findall(r"\d+", " ".join(str(s) for s in sources)))
    return [n for n in re.findall(r"\d+", texte) if n not in connus]


def ambiance_ciblee(monde, message):
    """Éléments d'ambiance du lieu dont le message du joueur reprend un mot significatif."""
    def racines(texte):
        # Singulier et pluriel réguliers se rejoignent : « gravat » vise « gravats ».
        return {m.rstrip("sx") for m in re.findall(r"[a-z0-9]+", lexique.corpus(texte)) if len(m) >= 4}

    demandes = racines(message)
    return [a for a in ambiance_etablie(monde)
            if demandes & {r for e in a["entites"] for r in racines(e)}]


def ambiance_etablie(monde, salle=None):
    """Descriptions d'ambiance déjà affichées pour ce lieu, sans valeur mécanique."""
    return [{"texte": a["texte"], "entites": a["entites"]}
            for a in monde.data.get("ambiances", {}).get(salle or monde.joueur["salle"], [])]


def verifier(monde):
    for salle, liste in monde.data.get("ambiances", {}).items():
        assert (salle in monde.data["salles"] and isinstance(liste, list)
                and len(liste) <= AMBIANCES_PAR_LIEU
                and all(isinstance(a, dict) and set(a) == {"texte", "entites", "revision"}
                        and isinstance(a["texte"], str) and bool(a["texte"].strip())
                        and isinstance(a["entites"], list)
                        and all(isinstance(x, str) for x in a["entites"])
                        and type(a["revision"]) is int for a in liste)), "Ambiance invalide"
    for e in monde.data.get("narrations_mj", []):
        assert (isinstance(e, dict) and set(e) == {"texte", "revision", "sources"}
                and isinstance(e["texte"], str) and bool(e["texte"].strip())
                and type(e["revision"]) is int and 0 <= e["revision"] <= monde.data["revision"]
                and isinstance(e["sources"], list)
                and all(isinstance(s, str) for s in e["sources"])), "Narration du MJ invalide"
