"""Syntaxe locale volontairement limitée ; les intentions libres vont au MJ."""
import re

from .monde import normaliser
from .moteur import proposition


AIDE = """COMMANDES LOCALES — sans appel API
  regarder | carte | fiche | inventaire | journal | contexte | aide
  lumière                              expliquer les conditions de visibilité
  allumer <source> | éteindre <source>  utiliser un outil d'allumage porté
  nord / sud / est / ouest              un pas en mode cases, sinon changement de pièce
  pas nord / pas sud / pas est / pas ouest  déplacer d'une case (sans IA)
  examiner <objet>                     voir les composants accessibles
  lire <inscription>                   tenter d'en comprendre le sens
  prendre <objet> | poser <objet>
  acheter <objet>                       auprès de son vendeur présent
  voler <objet>                        tentative discrète, jet de DEX si observé
  parler <personnage>
  offre <personnage> | negocier <personnage> 25
  accepter offre | refuser offre | accords
  remettre <objet> à <personnage>       remet l'objet contre le paiement convenu
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

L'objectif de ta partie est indiqué par « contexte ».
En mode cases : Ctrl+flèches pour marcher ; F6 pour piloter depuis la carte.
Manipuler exige d'être sur la case de l'objet ou juste à côté ; voir exige une ligne de vue.
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
    if texte.startswith("pas "):
        return proposition("marcher", texte[4:])
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
    if texte.startswith("sonner "):
        from .operations import etape, sequence
        return sequence(etape("emettre_son", monde.trouver(texte[7:]), methode="simple"))
    if texte.startswith("installer ") and " contre " in texte:
        cible, _, support = texte[10:].partition(" contre ")
        return proposition("installer", monde.trouver(cible), monde.trouver(support))
    for prefixe, action in (("monter ", "franchir"), ("descendre ", "franchir"), ("desinstaller ", "desinstaller")):
        if texte.startswith(prefixe):
            return proposition(action, monde.trouver(texte[len(prefixe):]))
    for prefixe in ("remettre ", "donner "):
        if texte.startswith(prefixe):
            objet, sep, destinataire = texte[len(prefixe):].partition(" a ")
            return proposition("remettre", monde.trouver(objet), monde.trouver(destinataire) if sep else "")
    if texte in ("contexte", "histoire", "objectif"):
        return proposition("observer", "contexte")
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
