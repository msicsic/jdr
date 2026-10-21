"""Contrôle commun des assertions du MJ avant leur affichage.

Le contrôle s'applique à la prose finale du MJ. Les affirmations mécaniques
(entités, positions, passages, possession, ressources, lumière, présence des PNJ,
missions, résultats) doivent découler des faits fournis ; une invention dans ces
domaines est refusée. L'ambiance est libre et enregistrée avec son lieu. Un nom
d'entité absent de tout ce que le MJ a reçu est refusé sans dépendre de l'auditeur.
Le texte accepté est affiché tel que Luna l'a écrit.
"""

import copy
import re

from .monde import ErreurMonde
from . import lexique


VERDICTS = ("neutre", "hypothese", "ambiance", "parole", "engagement", "mecanique",
            "invention_protegee", "contradictoire")
AMBIANCES_PAR_LIEU = 30


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
            textes.append(decrire(monde, objet["id"], technique=False))
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
                "locuteur": {"type": "string"},
                "citation": {"type": "string"},
                "entites": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
                "motif": {"type": "string"},
            },
            "required": ["indice", "verdict", "sources", "locuteur", "citation", "entites", "motif"]}},
    },
    "required": ["segments"],
}
CHAMPS_AUDIT = set(SCHEMA_AUDIT["properties"]["segments"]["items"]["required"])


def schema_audit(faits, nombre):
    """Les sources citables sont exactement les clés fournies : une référence inventée
    ou un chemin approximatif ne peut pas être produit. Une entrée obligatoire par segment,
    sous la clé de son indice : un rapport ne peut ni sauter, ni fusionner, ni ajouter un segment."""
    def ligne():
        item = copy.deepcopy(SCHEMA_AUDIT["properties"]["segments"]["items"])
        item["properties"]["sources"]["items"] = {"type": "string", "enum": sorted(faits)}
        del item["properties"]["indice"]
        item["required"] = [k for k in item["required"] if k != "indice"]
        return item
    cles = [str(i) for i in range(nombre)]
    return {"type": "object", "additionalProperties": False,
            "properties": {"segments": {"type": "object", "additionalProperties": False,
                                        "properties": {c: ligne() for c in cles}, "required": cles}},
            "required": ["segments"]}


class AuditIllisible(ErreurMonde):
    """Le rapport de l'auditeur est mal formé : une faute de l'auditeur, pas du texte contrôlé."""

INSTRUCTIONS_AUDIT = """Tu contrôles une réponse du maître du jeu avant qu'un joueur la voie.
Le jeu distingue deux sortes d'affirmations sur le monde.
Mécaniques : objets et personnages identifiés, positions, sorties et passages, portes et
attaches, possession, ressources (or, PV, combustible), lumière, présence des PNJ, missions,
récompenses, résultats d'action, indices et solutions. Elles doivent découler des faits fournis.
Ambiance : aspect, odeur, son de fond, température, texture, impression. Elle est libre tant
qu'elle ne crée ni objet manipulable, ni passage, ni personnage, ni ressource, ni indice.
Examine CHAQUE segment fourni, y compris ce qu'il sous-entend, et classe-le en entier :
- neutre : aucune affirmation sur le monde (salutation, question, conseil, invitation) ;
- hypothese : possibilité explicitement présentée comme incertaine ;
- ambiance : description sensorielle libre ; liste dans entites les éléments évoqués,
  en quelques mots chacun (« odeur de vase », « gouttes au plafond ») ;
- mecanique : affirmation mécanique soutenue par les faits ; cite dans sources les clés
  des faits qui la soutiennent (par exemple objet:<id>, perception, salle, engagements).
  Corvus perçoit exactement les objets objet:<id> fournis : qu'il ne voie pas un objet dont il
  n'a qu'un souvenir (souvenirs_visuels, hors_de_vue) est mecanique, avec cette source ;
- parole : propos nouveau d'un personnage présent, attribué explicitement ; donne son
  identifiant exact et la citation littérale présente dans le segment ; son contenu peut être faux.
  Rappeler ce qu'un personnage a déjà dit (paroles_entendues, conversation) n'est pas une parole :
  c'est mecanique, avec cette source ; cela atteste qu'il l'a dit, pas que c'est vrai ;
- engagement : un personnage présent s'engage à faire ce qui changerait le monde (se déplacer,
  donner, apporter, ouvrir, payer, aider) ou accepte de le faire, de sa bouche (« je vais me
  pousser », « je te l'apporte », « d'accord, j'y vais ») ou annoncé par le récit (« il va
  s'écarter ») ; locuteur = ce personnage ; citation = ses mots littéraux s'il parle, sinon vide ;
  entites = l'engagement qui le prévoit, recopié mot pour mot de
  esprits_interlocuteurs.<locuteur>.engagements ou de conversation_validee.faits, vide si rien ne
  le prévoit. Rappeler un engagement déjà dit (paroles_entendues) reste mecanique ;
- invention_protegee : crée ou suppose un élément mécanique absent des faits (objet utilisable,
  passage, personnage, ressource, indice, résultat), même plausible ou décoratif ;
- contradictoire : contraire aux faits, à la perception, à ambiance_etablie ou aux effets prévus.
Si un segment mêle plusieurs catégories, choisis la plus contraignante : contradictoire,
invention_protegee, engagement, parole, mecanique, ambiance, hypothese, neutre.
L'historique, une proposition non exécutée et une parole de personnage ne prouvent pas leur
contenu. resultat_resolu.gestes sont les gestes que Corvus vient d'accomplir, exécutés par le
moteur : les raconter, dans la manière que demande resultat_resolu.intention (style, rythme,
posture, mots choisis), est mecanique, source resultat_resolu ; leurs suites sont celles de
resultat_resolu.faits, sans autre effet. Si retour_moteur indique qu'aucune action n'a été exécutée ou que rien n'a été dit, raconter
comme fait ou commencé un geste du joueur (frapper, saisir, attendre, s'approcher, parler), ou
qu'un personnage lui répond ou y réagit, est contradictoire : seule l'explication de ce qui l'en
empêche est permise. Hors parole et engagement, locuteur et citation
sont vides ; hors ambiance et engagement, entites est vide.
Rends un contrôle par segment, sous la clé de son indice, sans réécrire ni redécouper les segments.
"""

INSTRUCTIONS_REVISION = """\nLe contrôle de tes réponses précédentes dans ce tour (controle_narratif, chaque phrase
refusée et son motif) a relevé des affirmations mécaniques non établies, contradictoires ou un
nom absent de ce que Corvus perçoit ou sait.
Réponds de nouveau à l'intention initiale, à partir de l'état actuel. L'ambiance reste libre.
Tu peux proposer un ajout persistant par le protocole déjà disponible si l'état et
la demande le permettent. Sinon, reformule sans présenter l'ajout comme un fait : ce que Corvus
ne perçoit ni ne sait, dis simplement qu'il l'ignore.
Ne reproduis aucune phrase refusée. Appelle la fonction demandée une fois.
"""

REGLE_NARRATION = """
Ce que tu affirmes sur l'état mécanique (objets, personnages, positions, passages, possession,
ressources, lumière, missions, résultats) doit découler des faits fournis ; pour créer un
élément mécanique, propose un fait persistant lorsque ce mode est disponible. L'ambiance
(aspect, odeur, son de fond, texture, impression) est libre si elle ne crée ni objet
manipulable, ni passage, ni personnage, ni ressource, ni indice. Reste cohérent avec
ambiance_etablie. Ne nomme pas un objet ou un lieu dont les faits ne parlent pas.
Dis une inconnue dans la fiction (ce que Corvus voit, entend ou ignore), jamais en parlant
de faits, de données ou de ce qui est « établi ».
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
        if fin_phrase or caractere == "\n":
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


def mentions(monde, texte, base, paroles=""):
    """Obstacles déterministes : noms d'entités absents de ce que le MJ a reçu. Ce qu'un
    personnage croit ne se dit que par sa bouche, entre guillemets ; la narration n'en use pas."""
    citations = " ".join(CITATIONS.findall(texte))
    recit = CITATIONS.sub(" ", texte)
    trouves = (lexique.mentions_sans_fondement(monde, recit, base)
               + lexique.mentions_sans_fondement(monde, citations, base + " " + paroles))
    return [{"segment": None, "texte": texte,
             "motif": "« " + m["terme"] + " » n'apparaît dans rien de ce que Corvus perçoit "
                      "ou sait. Ne l'introduis pas sans fait établi ; ce qu'un personnage croit "
                      "ne se dit que dans sa propre réplique."}
            for m in trouves]


AUTEUR = re.compile(r"\b(?:le|au|du|un) joueur\b|\bmoteur\b|\bMJ\b|\bCorvus\b|\bles faits\b|\bdonnées\b"
                    r"|\bscénario\b", re.IGNORECASE)


def voix_auteur(texte):
    """Obstacles déterministes : le texte affiché parle au joueur, à la deuxième personne, dans la
    fiction ; il ne parle ni du joueur, ni du moteur, ni de Corvus à la troisième personne. Les
    répliques citées des personnages restent libres."""
    trouves = sorted({m.group(0) for m in AUTEUR.finditer(CITATIONS.sub(" ", texte))}, key=str.lower)
    if not trouves:
        return []
    return [{"segment": None, "texte": texte,
             "motif": "Le joueur lit ce texte tel quel : écris-le à la deuxième personne, dans la fiction, "
                      "sans " + ", ".join(f"« {t} »" for t in trouves) + "."}]


def mentions_proposees(monde, reponse, base, paroles=""):
    """Même contrôle pour les textes d'un ajout persistant : détail, objet, inscription,
    parole, portrait ou savoir. Le nom propre de l'élément créé fait partie de l'ajout."""
    proposition = reponse.get("proposition") if isinstance(reponse, dict) else None
    if (reponse.get("mode") not in ("etablir_faits", "enrichir", "enrichir_savoirs")
            or not isinstance(proposition, dict)):
        return []
    obstacles = []
    for ajout in [*proposition.get("ajouts", []), *proposition.get("savoirs", [])]:
        if not isinstance(ajout, dict):
            continue
        propre = lexique.corpus(ajout.get("nom", "")) if isinstance(ajout.get("nom"), str) else ""
        # Un savoir prêté à un personnage peut reprendre ce qu'il croit.
        if ajout in proposition.get("savoirs", []):
            propre += " " + paroles
        for champ in ("texte", "description"):
            if isinstance(ajout.get(champ), str) and ajout[champ].strip():
                obstacles.extend({"partie": "description", **o}
                                 for o in mentions(monde, ajout[champ], base + " " + propre))
    return obstacles


def engagements_prevus(faits, locuteur):
    """Ce que le moteur a prévu que ce personnage fera : ses engagements enregistrés et l'issue
    qu'il vient de valider pour lui (conversation_validee)."""
    esprit = (faits.get("esprits_interlocuteurs") or {}).get(locuteur) or {}
    prevus = list(esprit.get("engagements") or [])
    validee = faits.get("conversation_validee")
    if isinstance(validee, dict) and (validee.get("personnage") == locuteur
                                      or locuteur in (validee.get("destinataires") or [])):
        prevus += list(validee.get("faits") or [])
    return {p.strip() for p in prevus if isinstance(p, str) and p.strip()}


def destinataires_parole(faits, locuteur):
    """Ceux à qui Corvus vient de parler (conversation_validee.destinataires), seuls à lui répondre ;
    sans parole de Corvus validée, rien ne restreint ``locuteur``."""
    validee = faits.get("conversation_validee")
    if isinstance(validee, dict) and isinstance(validee.get("destinataires"), list):
        return [x for x in validee["destinataires"] if isinstance(x, str)]
    return [locuteur]


# Les formes par lesquelles une réplique dit qui parle (texte normalisé) : ce qui suit est un nom
# que seul le moteur peut donner à une voix inconnue.
SE_NOMMER = re.compile(r"\b(?:je suis|je m'appelle|on m'appelle|mon nom est|mon nom,|c'est moi,?|moi,? c'est)"
                       r"\s+((?:\w|['-])+(?:\s+(?:\w|['-])+)?)")


def voix_inconnues(monde, paroles, faits, texte=""):
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
    validee = faits.get("conversation_validee") or {}
    obstacles = []
    recit = lexique.normaliser(CITATIONS.sub(" ", texte))
    for entree in interlocuteurs.values():
        nom = entree.get("nom", "") if isinstance(entree, dict) and entree.get("voix_inconnue") else ""
        pretendu = lexique.normaliser(nom.split("(")[0]).replace("une voix", "voix").strip()
        reste = recit.replace(pretendu, " ") if pretendu else recit
        dits = sorted(x for x in lexique.entites_citees(monde, nom)
                      if x in monde.objets and monde.objets[x]["type"] == "personnage")
        if dits and any(x in lexique.entites_citees(monde, reste) for x in dits):
            obstacles.append({"segment": None, "texte": texte,
                              "motif": f"Corvus ne sait pas qui parle : c'est {nom}, pas cette personne. Dans le "
                                       "récit, désigne-la comme une voix (« la voix qui se dit … »), sans lui "
                                       "donner ce nom."})
    for parole in paroles:
        entree = interlocuteurs.get(parole["locuteur"]) or {}
        if not entree.get("voix_inconnue"):
            continue
        etabli = " ".join([entree.get("nom", ""), *map(str, validee.get("faits") or []),
                           str(validee.get("replique_joueur", ""))])
        permis = lexique.entites_citees(monde, etabli)
        from .voix import connait_nom, reel
        qui = reel(monde, parole["locuteur"])
        qui = qui if qui in monde.objets and monde.objets[qui]["type"] == "personnage" else None

        def tait(x):
            # Son propre nom, seulement s'il est établi ; un autre, s'il le sait ou s'il est établi.
            return x not in permis and (qui is None or x == qui or not connait_nom(monde, qui, x))
        nommes = sorted(x for x in lexique.entites_citees(monde, parole["texte"])
                        if x in monde.objets and monde.objets[x]["type"] == "personnage" and tait(x))
        # Se dire quelqu'un, c'est se nommer : seul le moteur en décide (``voix.se_nommer``).
        nommes += sorted(x for x in lexique.entites_citees(monde, " ".join(
            m.group(1) for m in SE_NOMMER.finditer(lexique.normaliser(parole["texte"]))))
            if x in monde.objets and monde.objets[x]["type"] == "personnage" and x not in permis
            and x not in nommes)
        corvus = re.compile(r"\b" + re.escape(lexique.normaliser(monde.joueur["nom"].split(",")[0])) + r"\b")
        if (corvus.search(lexique.normaliser(parole["texte"])) and not corvus.search(lexique.normaliser(etabli))
                and (qui is None or not connait_nom(monde, qui, "joueur"))):
            nommes.append("joueur")  # Elle ne sait pas son nom.
        if nommes:
            obstacles.append({"segment": None, "texte": parole["texte"],
                              "motif": f"{entree.get('nom', 'Cette voix')} : Corvus ne sait pas qui parle. Sa "
                                       "réplique ne se nomme pas au-delà de ce que le moteur a établi (son nom "
                                       "d'interlocuteur, conversation_validee) et ne nomme que qui elle connaît : "
                                       "retire "
                                       + ", ".join(f"« {(monde.joueur if x == 'joueur' else monde.objets[x])['nom'].split(',')[0]} »"
                                                   for x in nommes)
                                       + "."})
    return obstacles


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
    rf"|\btu (?:as )?(?:{_DIRE}|{_DIT}) (?:a|au|aux)\b"
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


def paroles_sans_moteur(texte, faits, adresse=False):
    """Obstacles déterministes : une parole n'a lieu que si le moteur l'a fait entendre. Sans parole de
    Corvus validée dans ce tour (conversation_validee) ni geste résolu (resultat_resolu), le récit ne
    fait pas parler Corvus ; et quand rien n'a été dit — après un refus (retour_moteur), ou quand la
    saisie s'adresse à quelqu'un (``adresse``) sans que le moteur ait fait entendre une parole —
    personne ne lui répond : aucune citation nouvelle."""
    if isinstance(faits.get("conversation_validee"), dict) or isinstance(faits.get("resultat_resolu"), dict):
        return []
    obstacles = []
    if parole_racontee(texte):
        obstacles.append({"segment": None, "texte": texte,
                          "motif": "Corvus n'a rien dit dans ce tour : le récit ne le fait pas parler ("
                                   + ", ".join(f"« {p} »" for p in parole_racontee(texte)) + "). Si le "
                                   "joueur fait parler Corvus, propose parole_joueur : le moteur fixe à qui "
                                   "il parle et la fait entendre ; s'il agit, propose l'action."})
    if isinstance(faits.get("retour_moteur"), dict) and citations_nouvelles(texte, faits):
        # Après un refus, rien n'a eu lieu : le motif vient du moteur, aucun personnage ne le connaît,
        # ne le dit ni ne réagit, quelle que soit la voie (action, parole, conversation, faits).
        obstacles.append({"segment": None, "texte": texte,
                          "motif": "Aucune action ni parole n'a eu lieu : c'est toi qui expliques "
                                   "l'obstacle. Aucun personnage ne parle ni ne réagit ; ne cite "
                                   "entre guillemets que des paroles déjà entendues."})
    elif adresse and citations_nouvelles(texte, faits):
        obstacles.append({"segment": None, "texte": texte,
                          "motif": "Le joueur s'adresse à un personnage, mais rien n'a encore été dit : "
                                   "personne ne répond à une parole que le moteur n'a pas fait entendre. "
                                   "Si Corvus parle, propose parole_joueur ; le personnage répondra ensuite."})
    return obstacles


def controler(texte, rapport, faits):
    """Valide le rapport de l'auditeur et renvoie ses obstacles, jamais sa seule assurance."""
    passages = segments(texte)
    lignes = rapport.get("segments") if isinstance(rapport, dict) else None
    if isinstance(lignes, dict):
        # Forme demandée à l'auditeur : une entrée par segment, sous la clé de son indice.
        if set(lignes) != {str(i) for i in range(len(passages))}:
            raise AuditIllisible("Contrôle narratif incomplet.")
        lignes = [{**lignes[str(i)], "indice": i} if isinstance(lignes[str(i)], dict) else lignes[str(i)]
                  for i in range(len(passages))]
    if (not passages or len(passages) > 24 or not isinstance(lignes, list)
            or len(lignes) != len(passages)):
        raise AuditIllisible("Contrôle narratif incomplet.")
    obstacles, paroles, ambiances, lignes_validees = [], [], [], []
    for indice, (passage, ligne) in enumerate(zip(passages, lignes)):
        if (not isinstance(ligne, dict) or set(ligne) != CHAMPS_AUDIT
                or type(ligne["indice"]) is not int or ligne["indice"] != indice
                or ligne["verdict"] not in VERDICTS
                or not isinstance(ligne["sources"], list)
                or any(not isinstance(s, str) for s in ligne["sources"])
                or not isinstance(ligne["entites"], list)
                or any(not isinstance(e, str) for e in ligne["entites"])
                or any(not isinstance(ligne[k], str) for k in ("locuteur", "citation", "motif"))):
            raise AuditIllisible("Contrôle narratif mal formé.")
        verdict = ligne["verdict"]
        # Une source inconnue ne prouve rien : elle est écartée, et une affirmation
        # mécanique sans source restante est refusée plus bas.
        ligne = {**ligne, "sources": [s for s in ligne["sources"] if s in faits]}
        # Ces champs ne portent aucun sens hors de leur verdict. Les vider évite qu'une
        # erreur de format de l'auditeur rejette un segment contrôlé par son verdict réel.
        if verdict not in ("parole", "engagement"):
            ligne = {**ligne, "locuteur": "", "citation": ""}
        if verdict not in ("ambiance", "engagement"):
            ligne = {**ligne, "entites": []}
        lignes_validees.append(ligne)
        # La citation est le texte entre les guillemets : ceux que l'auditeur recopie avec elle
        # ne la rendent pas fausse (« D'accord » cité « « D'accord » »).
        locuteur, citation = ligne["locuteur"], ligne["citation"].strip().strip("«»\"“”  ")
        if verdict == "mecanique" and not ligne["sources"]:
            obstacles.append({"segment": indice, "texte": passage,
                              "motif": "Cette affirmation mécanique ne cite aucun fait du moteur."})
        elif verdict in ("parole", "engagement") and locuteur not in faits.get("interlocuteurs", {}):
            obstacles.append({"segment": indice, "texte": passage,
                              "motif": "Seul un personnage présent peut parler ; aucun locuteur présent "
                                       "ne correspond à cette parole."})
        elif verdict in ("parole", "engagement") and locuteur not in destinataires_parole(faits, locuteur):
            # Le moteur a décidé l'issue de la parole de Corvus pour ses destinataires seulement.
            obstacles.append({"segment": indice, "texte": passage,
                              "motif": "Corvus s'adressait à " + ", ".join(destinataires_parole(faits, locuteur))
                                       + " : eux seuls lui répondent ; les autres l'ont entendu sans être "
                                         "interpellés et se taisent."})
        elif verdict == "engagement" and (not ligne["entites"] or any(
                e.strip() not in engagements_prevus(faits, locuteur) for e in ligne["entites"])):
            # Sa parole atteste qu'il l'a dit ; ce qu'il fera, seul le moteur le décide.
            obstacles.append({"segment": indice, "texte": passage,
                              "motif": "Ce personnage s'engage à agir sans que le moteur l'ait prévu : rien "
                                       "dans esprits_interlocuteurs.engagements ni conversation_validee ne le "
                                       "dit. Fais-le répondre sans rien promettre (il peut répondre, hésiter, "
                                       "refuser ou se taire), et n'annonce pas qu'il le fera."})
        elif verdict == "parole" or (verdict == "engagement" and citation):
            from .faits_locaux import LONGUEUR_PAROLE
            if (not 3 <= len(citation.strip()) <= LONGUEUR_PAROLE or any(ord(c) < 32 for c in citation)
                    or f"« {citation} »" not in passage):
                obstacles.append({"segment": indice, "texte": passage,
                                  "motif": "Une parole doit être citée entre « et », en entier, dans le segment."})
            else:
                paroles.append({"locuteur": locuteur, "texte": citation})
        elif verdict == "ambiance":
            ambiances.append({"texte": passage,
                              "entites": [e.strip()[:80] for e in ligne["entites"] if e.strip()]})
        elif verdict in ("invention_protegee", "contradictoire"):
            obstacles.append({"segment": indice, "texte": passage,
                              "motif": ligne["motif"] or "Affirmation mécanique non établie."})
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
    if (rapport["obstacles"] or rapport["texte_controle"] != texte
            or mentions(monde, texte, audit["fondement"], audit.get("fondement_paroles", ""))
            or voix_inconnues(monde, rapport["paroles"], audit["faits"], texte)):
        # Même base que l'audit : ce qu'un personnage croit peut figurer dans sa propre réplique.
        raise ErreurMonde("Le MJ n'a pas pu formuler une réponse sûre. Aucun changement enregistré.")
    paroles = []
    if rapport["paroles"]:
        from .sons import auditeurs
        from .voix import connaitre, reel
        for parole in rapport["paroles"]:
            # Le MJ désigne une voix inconnue comme le joueur (voix_<n>) : le moteur sait qui parle.
            locuteur = monde.objets[reel(monde, parole["locuteur"])]
            if not monde.present_physique(locuteur["id"]):
                raise ErreurMonde("Le locuteur n'est plus présent pour cette parole.")
            if monde.visible(locuteur["id"]):
                connaitre(monde, "joueur", locuteur["id"])  # Il le voit parler : il saura reconnaître sa voix.
            entendants = auditeurs(monde, salle, 2)
            if "joueur" not in entendants:
                entendants.append("joueur")
            paroles.append({
                "locuteur": locuteur["id"], "texte": parole["texte"], "salle": salle,
                "minute": monde.data["minutes"], "auditeurs": entendants,
                "revision": monde.data["revision"],
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
