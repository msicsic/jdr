"""Syntaxe locale volontairement limitée ; les intentions libres vont au MJ."""
import re

from .monde import normaliser
from .moteur import proposition


AIDE = """COMMANDES LOCALES — sans appel API
  regarder | carte | fiche | inventaire | journal | contexte | aide
  lumière                              expliquer les conditions de visibilité
  allumer <source> | éteindre <source>  utiliser un outil d'allumage porté
  alimenter <source> avec <combustible>  recharger un feu, une lampe, avec un combustible porté ou à portée
  manger <nourriture>                   une part de ce qui est à toi ou à personne (5 min)
  écouter                               tendre l'oreille (3 min), mieux collé à une porte
  nord / sud / est / ouest              un pas en mode cases, sinon changement de pièce
  pas nord / pas sud / pas est / pas ouest  te tourner vers la direction puis avancer d'une case (1,5 s)
  chasse <direction>                    pas chassé sans te tourner (3 s de côté ou en arrière)
  faufiler <direction>                  pas feutré (3 s) : ne s'entend que de la case voisine
  tourner <direction> | demi-tour       te tourner sans avancer (0,5 s par huitième de tour)
  examiner <objet>                     voir les composants accessibles
  lire <inscription>                   tenter d'en comprendre le sens
  prendre <objet> | poser <objet>
  acheter <objet>                       auprès de son vendeur présent
  voler <objet>                        tentative discrète, jet de DEX si observé
  parler <personnage>
  offre <personnage> | negocier <personnage> 25
  accepter offre | refuser offre | accords
  donner <objet> à <personnage>         un objet porté ; avec un accord, contre le paiement convenu
  pousser <personnage> [vers <direction>]  bousculer quelqu'un au contact (FOR opposée, 3 s) ;
                                       réussi, il recule d'un pas. Il ne te fera plus confiance.
  ouvrir <objet> avec <clé> | fermer <objet>
  crocheter <serrure> avec <outil>
  retirer <fixation> avec <outil>
  frapper <cible> avec <outil>
  couper <cible> avec <outil>          entailler, puis sectionner si l'intégrité cède
  caler <porte> avec <objet> | débloquer <porte>
  copier <motif> avec <matériau>
  installer échelle contre mur | monter échelle | descendre échelle
  désinstaller échelle                 retirer l'accès vertical depuis son pied ou son sommet
  fabriquer échelle                    assemblage local si les matériaux sont à portée
  attendre                             5 minutes, le bruit diminue
  crier à l'aide | crier | siffler       émettre un son, sans garantie de secours
  sonner <objet>                        utiliser un objet sonore accessible
  sauver | quitter                     sauvegarde aussi après chaque action
  contexte                             début, objectif et dernier déplacement
  connexion | connecter                état du MJ / connexion au forfait ChatGPT
  comparaison                          résultats du mode --compare-model (F5 en TUI)

MJ — conversation et actions
  Une phrase libre appelle le LLM si le mode IA est actif.
  Le MJ répond aux questions et se souvient des derniers échanges, sans « tenter » ni jet.
  Les actions simples (« je prends cet objet ») s'exécutent directement après validation.
  Les manœuvres interprétées par le MJ avec un jet ou un risque attendent « tenter ».
  Hors ligne, utilisez les commandes explicites : contexte, lumière, regarder, journal.
  mj <phrase> force son utilisation, même pour une commande connue.
  Exemple : mj Je fais levier avec cet outil pour retirer cette fixation.
  tenter : exécuter sa proposition ; annuler : abandonner sans effet.
  Une nouvelle action remplace la proposition ; discuter avec le MJ la conserve.

PARLER (MJ) — le moteur fixe à qui Corvus parle
  Brune, … | je dis à Brune : …         à celui que tu nommes ; sinon à celui qui est en face de toi
  « … » | je lui dis … | je leur dis …  la suite de l'échange : à qui tu parlais, s'il t'entend
                                        encore ; sinon à celui qui est en face de toi
  à tous : … | je dis à tous …          à tous ceux qui t'entendent ; chacun décide pour lui
  je chuchote à Brune : … | je murmure …  à l'oreille, au contact : les autres n'en saisissent pas les mots
  Tous ceux qui entendent ta voix retiennent ce que tu dis ; seuls ceux à qui tu parles répondent.

L'objectif de ta partie est indiqué par « contexte ».
En mode cases : Ctrl+flèches pour marcher (on se tourne puis on avance), Maj+flèches pour un pas
chassé sans se tourner, Alt+flèches pour un pas feutré ; F6 pour piloter depuis la carte. Tu vois devant toi (120°) et sur les
côtés immédiats, pas derrière.
Manipuler exige d'être sur la case de l'objet ou juste à côté ; voir exige une ligne de vue.
Un personnage sur ta route s'écarte s'il le veut bien ; sinon demande-le-lui (MJ) ou pousse-le.
« etat <objet> » affiche les données internes avec --debug uniquement ;
« esprit <personnage> » affiche ses croyances, sa mémoire et son intention.
"""


VERBES = {
    "examiner": "examiner", "regarder": "examiner", "inspecter": "examiner",
    "toucher": "toucher", "lire": "lire", "prendre": "prendre", "poser": "poser",
    "acheter": "acheter", "ouvrir": "ouvrir", "fermer": "fermer",
    "voler": "voler", "derober": "voler",
    "deverrouiller": "deverrouiller", "crocheter": "crocheter",
    "frapper": "frapper", "defoncer": "frapper", "forcer": "frapper",
    "couper": "couper", "decouper": "couper", "trancher": "couper",
    "retirer": "detacher", "extraire": "detacher", "detacher": "detacher",
    "caler": "bloquer", "bloquer": "bloquer", "debloquer": "debloquer",
    "decaler": "debloquer", "copier": "copier", "parler": "parler",
    "allumer": "allumer", "allume": "allumer", "eteindre": "eteindre", "eteins": "eteindre",
}


# Ce qu'une question peut faire exécuter : percevoir, sans rien changer au monde. Tout autre geste
# qu'elle évoque (« puis-je allumer ? ») se prépare sans s'exécuter : le joueur voit ce qu'il
# demanderait, puis le tente ou l'annule.
PERCEPTIONS = ("observer", "examiner")


def est_question(texte):
    """Reconnaît la ponctuation, les interrogatifs et l'inversion du sujet."""
    if "?" in texte:
        return True
    mots = normaliser(texte).split()
    if not mots:
        return False
    premier = mots[0]
    interrogatifs = {"ou", "qui", "que", "quoi", "quand", "combien", "comment",
                     "pourquoi", "quel", "quelle", "quels", "quelles", "lequel",
                     "laquelle", "lesquels", "lesquelles"}
    if premier in interrogatifs or premier.startswith(("qu'", "d'ou")):
        return True
    if len(mots) > 1 and (mots[:2] in (["est", "ce"], ["a", "quoi"], ["de", "quoi"])):
        return True
    if re.fullmatch(r"[a-z]+-(?:t-)?(?:je|tu|il|elle|on|nous|vous|ils|elles|ce)", premier):
        return True
    return "combien" in mots[1:] or mots[-1] in {"ou", "quand", "pourquoi", "comment"}


# Une question sur ce que Corvus peut faire (« puis-je… ? », « est-ce que je pourrais… ? », « est-il
# possible de… ? ») : le moteur y répond, par la fiche du geste ou par la raison de son refus.
FAISABILITE = re.compile(r"\b(?:est-ce que|est ce que) (?:je |j')(?:peux|pourrais|pourrai|arrive|arriverais|reussirais|saurais)\b"
                         r"|\b(?:puis|pourrais|pourrai|peux|arriverais|saurais)-je\b"
                         r"|^(?:et |mais |alors )?je (?:peux|pourrais|pourrai)\b"
                         r"|\b(?:est-il|serait-il|c'est|ce serait|est-ce) possible de\b"
                         r"|\by a-t-il moyen de\b|\bai-je moyen de\b")


def faisabilite(texte):
    """La saisie demande si Corvus peut accomplir un geste ; « qu'est-ce que je peux faire ? » demande
    lesquels, ce n'en est pas une."""
    forme = normaliser(texte)
    return (est_question(texte) and not re.match(r"(?:et |mais |alors )?(?:qu'|que |quoi |quel)", forme)
            and bool(FAISABILITE.search(forme)))


# Donner, comme prendre : l'infinitif de la commande, l'impératif et la première personne.
DONNER = ("je donne ", "je remets ", "je remet ", "donne ", "remets ", "donner ", "remettre ")
ARTICLES = ("le ", "la ", "les ", "l'", "un ", "une ", "mon ", "ma ", "mes ")


def _nomme(monde, texte, personnage):
    """L'objet accessible, ou le personnage, que ``texte`` nomme exactement ; sinon None."""
    for article in ARTICLES:
        if texte.startswith(article):
            texte = texte[len(article):]
            break
    if not texte:
        return None
    # Les mêmes noms que pour tout geste (``Monde.designable``) : ce qu'il verrait en se tournant compte.
    if personnage:
        from .dialogues import interlocuteurs
        candidats = set(interlocuteurs(monde)) | {i for i, o in monde.objets.items()
                                                   if o["type"] == "personnage" and monde.designable(i)}
    else:
        candidats = {i for i, o in monde.objets.items() if o["type"] != "personnage" and monde.designable(i)}
    trouves = [i for i in candidats
               if texte in [normaliser(n) for n in (i, monde.objets[i]["nom"], *monde.objets[i]["aliases"])]]
    return trouves[0] if len(trouves) == 1 else None


def don(monde, reste):
    """« <objet> à <personnage> », « à <personnage> <objet> » ou « <objet> » seul (« au », « aux »
    comptent pour « à le », « à les ») : le geste de
    donner. Chaque nom doit désigner exactement un objet et un personnage ; une phrase qui dit
    autre chose (un complément, une seconde action, « un coup de pied ») va au MJ."""
    mots = reste.split()
    lectures = [(reste, "")]
    for i, mot in enumerate(mots):
        if mot not in ("a", "au", "aux"):
            continue
        if i:
            lectures.append((" ".join(mots[:i]), " ".join(mots[i + 1:])))
        else:
            lectures.extend((" ".join(mots[j:]), " ".join(mots[1:j])) for j in range(2, len(mots)))
    dons = {(objet, destinataire) for objet, destinataire in
            ((_nomme(monde, o, False), _nomme(monde, d, True) if d else "") for o, d in lectures)
            if objet and destinataire is not None}
    if len(dons) != 1:
        from .monde import ErreurMonde
        raise ErreurMonde("Précise l'objet que tu donnes et à qui, par leur nom : donner <objet> à <personnage>.")
    objet, destinataire = dons.pop()
    return proposition("remettre", objet, destinataire)


def analyser(monde, texte):
    """Renvoie None pour une intention libre, sans prétendre comprendre tout le français."""
    if est_question(texte):
        return None
    texte = normaliser(texte)
    # Une prise explicite d'un objet nommé exactement ne nécessite pas de MJ.
    # Le complément entier doit correspondre : ne jamais avaler une condition,
    # une seconde action ou une précision telle que « discrètement ».
    for prefixe in ("je prends ", "je prend ", "je ramasse ", "ramasser ", "ramasse ", "prends "):
        if not texte.startswith(prefixe):
            continue
        nom = texte[len(prefixe):]
        for article in ("le ", "la ", "les ", "l'"):
            if nom.startswith(article):
                nom = nom[len(article):]
                break
        correspondances = [id for id, o in monde.objets.items()
                           if monde.accessible(id) and nom in
                           [normaliser(n) for n in (id, o["nom"], *o["aliases"])]]
        if len(correspondances) == 1:
            return proposition("prendre", correspondances[0])
        return None
    if texte.startswith(("pas feutre ", "faufiler ", "se faufiler ")):
        return proposition("faufiler", texte.rsplit(" ", 1)[-1])
    if texte.startswith(("pas chasse ", "chasse ")):
        return proposition("chasser", texte.split(" ", 2)[-1] if texte.startswith("pas ") else texte[7:])
    if texte.startswith("pas "):
        return proposition("marcher", texte[4:])
    if texte.startswith(("tourner ", "se tourner ", "me tourner ")):
        return proposition("tourner", texte.rsplit(" ", 1)[-1])
    if texte in ("demi-tour", "faire demi-tour"):
        from .spatial import VECTEURS
        regard = monde.joueur.get("orientation")
        dos = next((nom for nom, v in VECTEURS.items() if regard and v == tuple(-x for x in VECTEURS[regard])), "")
        return proposition("tourner", dos)
    if texte in ("fabriquer echelle", "fabriquer une echelle"):
        from .artisanat import dossier
        from .monde import ErreurMonde
        d = dossier(monde)
        suggestion = (d or {}).get("suggestion") or {}
        if "proposition" not in suggestion:
            raise ErreurMonde(suggestion.get("obstacle", "Aucun assemblage d'échelle n'est disponible dans cette situation."))
        return suggestion.get("travail_soigne", {}).get("proposition", suggestion["proposition"])
    sons = {"crier a l'aide": "appel", "je crie a l'aide": "appel", "appeler a l'aide": "appel",
            "crier au secours": "appel", "je crie au secours": "appel",
            "crier": "cri", "je crie": "cri", "siffler": "sifflement", "je siffle": "sifflement"}
    if texte in sons:
        from .operations import etape, sequence
        return sequence(etape("emettre_son", "joueur", methode=sons[texte]), justification="")
    if texte.startswith("alimenter ") and " avec " in texte:
        from .operations import etape, sequence
        foyer, _, bois = texte[10:].partition(" avec ")
        return sequence(etape("alimenter", monde.trouver(foyer), outil=monde.trouver(bois)))
    if texte.startswith("manger "):
        from .operations import etape, sequence
        return sequence(etape("manger", monde.trouver(texte[7:])))
    if texte.startswith("sonner "):
        from .operations import etape, sequence
        return sequence(etape("emettre_son", monde.trouver(texte[7:]), methode="simple"))
    if texte.startswith("installer ") and " contre " in texte:
        cible, _, support = texte[10:].partition(" contre ")
        return proposition("installer", monde.trouver(cible), monde.trouver(support))
    for prefixe, action in (("monter ", "franchir"), ("descendre ", "franchir"), ("desinstaller ", "desinstaller")):
        if texte.startswith(prefixe):
            return proposition(action, monde.trouver(texte[len(prefixe):]))
    for prefixe in DONNER:
        if texte.startswith(prefixe):
            return don(monde, texte[len(prefixe):])
    if texte.startswith("pousser "):
        # « pousser brune », « pousser brune vers l'ouest » : la direction est facultative.
        from .spatial import VECTEURS
        mots = texte[8:].split()
        dernier = mots[-1][2:] if mots and mots[-1].startswith("l'") else mots[-1] if mots else ""
        direction = dernier if len(mots) > 1 and dernier in VECTEURS else ""
        if direction:
            mots.pop()
            while mots and mots[-1] in ("vers", "le", "au"):
                mots.pop()
        cible = monde.trouver(" ".join(mots))
        if monde.objets[cible]["type"] != "personnage":
            return None
        return proposition("pousser", cible, direction)
    if texte in ("contexte", "histoire", "objectif"):
        return proposition("observer", "contexte")
    if texte in ("ecouter", "j'ecoute", "tendre l'oreille", "je tends l'oreille", "ecouter a la porte",
                 "j'ecoute a la porte", "ecouter derriere la porte"):
        return proposition("ecouter")
    if texte in ("lumiere", "eclairage", "observer", "observer scene", "observer la scene"):
        return proposition("observer", "lumiere")
    directions = {"n": "nord", "s": "sud", "e": "est", "o": "ouest"}
    texte = directions.get(texte, texte)
    if texte.startswith("aller "):
        texte = texte[6:]
    if texte in ("nord", "sud", "est", "ouest"):
        return proposition("aller", texte)
    if texte == "attendre":
        return proposition("attendre")
    verbe, sep, reste = texte.partition(" ")
    if not sep or verbe not in VERBES:
        return None
    cible, avec, outil = reste.partition(" avec ")
    # Une phrase longue ne doit pas être transformée silencieusement en commande approchante.
    if len(cible.split()) > 9 or (avec and len(outil.split()) > 6):
        return None
    cible_id = monde.trouver(cible)
    outil_id = monde.trouver(outil) if avec else ""
    action = VERBES[verbe]
    methode = "simple"
    if action == "detacher":
        t = monde.objets.get(outil_id, {})
        usages = t.get("usages", [])
        methode = ("percussion" if "percussion" in usages and "levier" not in usages else "levier") if outil_id else "simple"
    return proposition(action, cible_id, outil_id, methode)
