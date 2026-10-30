"""Syntaxe locale volontairement limitée ; les intentions libres vont au MJ."""
import re
from dataclasses import dataclass

from .monde import normaliser
from .moteur import proposition


AIDE = """COMMANDES LOCALES — sans appel API
  regarder | carte | fiche | inventaire | journal | contexte | aide
  lumière                              expliquer les conditions de visibilité
  allumer <source> | éteindre <source>  utiliser un outil d'allumage porté
  alimenter <source> avec <combustible>  recharger un feu, une lampe, avec un combustible porté ou à portée
  manger <nourriture>                   une part de ce qui est à toi ou à personne (5 min)
  observer <personnage>                lire ses signes (3 secondes), avec le risque de se méprendre
  reperer <cible>                      consulter sa position perçue ou son dernier repère connu
  écouter                               tendre l'oreille (3 min), mieux collé à une porte
  nord / sud / est / ouest              un pas en mode cases, sinon changement de pièce
  pas nord / pas sud / pas est / pas ouest  te tourner vers la direction puis avancer d'une case (1,5 s)
  chasse <direction>                    pas chassé sans te tourner (3 s de côté ou en arrière)
  faufiler <direction>                  pas feutré (3 s) : ne s'entend que de la case voisine
  tourner <direction> | demi-tour       te tourner sans avancer (0,5 s par huitième de tour)
  examiner <objet>                     voir les composants accessibles
  lire <inscription>                   tenter d'en comprendre le sens
  prendre <objet> | poser <objet>
  ramper sous <obstacle> | enjamber <obstacle> | escalader <obstacle>
  monter <échelle> | descendre <échelle>
  franchir <obstacle> avec <appui>       reprendre un arbitrage déjà établi pour ce passage
  mettre <objet> dans <contenant>       déposer, ou alimenter une source avec un combustible
  prelever <lot>                       séparer une pièce du lot, dans la besace
  acheter <objet>                       auprès de son vendeur présent
  voler <objet>                        tentative discrète, jet de DEX si observé
  parler <personnage>
  saisir <personnage> | ligoter <personnage> avec <lien>
  assommer <personnage> [avec <arme>]   tenter de l'assommer ; la surprise dépend de ce qu'il perçoit
  fuir | riposter <agresseur> [avec <arme>] | se rendre à <agresseur>
  délier <personnage> [avec <lame>] | se libérer | se dégager
  traîner <corps> vers <direction>     une case, mains libres, 4,5 secondes
  ranimer <personnage>                 au contact, après une minute d'inconscience (10 secondes)
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
  ramper sous <obstacle> | passer par-dessus <obstacle>  fiche du passage ; « tenter » pour agir
  désinstaller échelle                 retirer l'accès vertical depuis son pied ou son sommet
  fabriquer échelle                    assemblage local si les matériaux sont à portée
  assembler <usage> montants <a>, <b> barreaux <c> lien <d> outil <e> longueur <cm> largeur <cm> rythme <normal|soigne>
  découper <pièce> à <cm> cm avec <outil>  couper à longueur, sans décrire ni choisir d'autres matériaux
  attendre [durée]                     5 minutes, ou « attendre 30 s », « attendre 10 min » ; le bruit
                                       diminue ; tu cesses d'attendre si quelqu'un paraît, ou si un
                                       appel, un cri, un fracas, des paroles nettes te parviennent
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
    "tuer": "tuer", "saisir": "saisir", "ligoter": "ligoter", "delier": "delier",
    "ranimer": "ranimer", "observer": "observer", "reperer": "reperer",
    "verrouiller": "verrouiller", "deverrouiller": "deverrouiller", "crocheter": "crocheter",
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
PERCEPTIONS = ("observer", "examiner", "reperer")


@dataclass(frozen=True)
class DescripteurPublic:
    """Un choix explicite, indépendant de son interface et de toute grammaire de saisie."""
    contenu: object


def geste_local(action, cible, outil="", methode="simple", destination="", direction=""):
    """La même proposition canonique pour le texte local et le choix structuré."""
    if action in {"pousser", "trainer"}:
        outil = direction
    if action in {"fuir", "degager"}:
        cible = ""
    if action == "liberer":
        cible = "joueur"
    if action in {"manger", "prelever", "alimenter", "mettre", "passer_obstacle"}:
        from .operations import etape, sequence
        if action == "mettre":
            return sequence(etape("deplacer", cible, destination, methode=methode))
        return sequence(etape(action, cible, outil=outil, methode=methode))
    return proposition(action, cible, outil, methode)


def passage_descripteur(monde, d):
    """Un choix encore offert, avec références exactes et paramètres fermés."""
    from .gestes_publics import passages_publics
    from .monde import ErreurMonde
    from .voix import reel
    p = d.get("parametres", {})
    attendus = ({"methode"} if d["geste"] == "passer_obstacle" else
                {"outil"} if d["geste"] == "franchir_obstacle" else set())
    if not isinstance(p, dict) or set(p) != attendus:
        raise ErreurMonde("Paramètres de passage incomplets ou inconnus.",
                          f"descripteur.parametres : reçu {p!r} ; champs exacts : {sorted(attendus)}.")
    offres = passages_publics(monde)
    if not any(o["geste"] == d["geste"] and o["cible"] == d["cible"] and
               o.get("methode") == p.get("methode") and o.get("outil") == p.get("outil") for o in offres):
        raise ErreurMonde("Ce passage n'est plus perçu avec une forme établie.",
                          f"descripteur : reçu {d!r} ; passages publics actuels : {offres!r}.")
    if d["geste"] == "franchir_obstacle":
        return passage_memorise(monde, reel(monde, d["cible"]), reel(monde, p["outil"]))
    return geste_local(d["geste"], reel(monde, d["cible"]), methode=p.get("methode", "simple"))


def passage_memorise(monde, cible, outil):
    """Rejouer le même arbitrage établi ; la prise fait partie du plan affiché."""
    from .franchissement import cle_arbitrage
    from .operations import etape, sequence
    from .monde import ErreurMonde
    destination = monde.objets[cible].get("appui_vertical", {}).get("haut")
    try:
        precedent = monde.data["arbitrages"].get(cle_arbitrage(monde, cible, outil, destination))
    except KeyError:
        precedent = None
    if not precedent or type(precedent.get("dd")) is not int or not 16 <= precedent["dd"] <= 22:
        raise ErreurMonde("Aucun arbitrage établi ne correspond à ce franchissement.",
                          f"franchir_obstacle : cible={cible!r}, outil={outil!r} ; attendu un arbitrage mémorisé pour la géométrie et la charge actuelles.")
    prise = [] if monde.est_porte(outil) else [etape("deplacer", outil, "joueur")]
    return sequence(*prise, etape("franchir_obstacle", cible, destination, outil,
                                "appui_mobile", precedent["dd"]))


def fabrication_locale(action, cible, parametres):
    """Choix de fabrication commun au formulaire et à la commande explicite.

    La difficulté normale reprend la convention de fabrication existante (12).
    Aucun paramètre ne décrit une propriété nouvelle d'une pièce.
    """
    if action == "decouper":
        return {"action": action, "cible": cible, **parametres, "justification": ""}
    return {"action": action, "usage": cible, **parametres,
            "difficulte": 0 if parametres["rythme"] == "soigne" else 12, "justification": ""}


def fabrication_descripteur(monde, d):
    from .monde import ErreurMonde
    from .voix import reel
    from .noms import reference
    from .gestes_publics import formulaires_fabrication, ressource_connue
    action, cible = d["geste"], d["cible"]
    p = d.get("parametres", {})
    offres = [f for f in formulaires_fabrication() if f["geste"] == action
              and (action == "decouper" or f["cible"] == cible)]
    if not offres:
        raise ErreurMonde("Cet usage n'est pas modélisé.",
                          f"descripteur.cible : reçu {cible!r} ; usages : {[f.get('cible') for f in formulaires_fabrication() if f['geste'] == action]}.")
    formulaire = offres[0]
    attendus = {c["chemin"][0] for c in formulaire["champs"]} - {"cible"}
    if not isinstance(p, dict) or set(p) != attendus:
        raise ErreurMonde("Paramètres de fabrication incomplets ou inconnus.",
                          f"descripteur.parametres : reçu {p!r} ; champs exacts : {sorted(attendus)}.")
    from copy import deepcopy
    p = deepcopy(p)

    def exacte(ref, champ):
        id = reel(monde, ref)
        if not ressource_connue(monde, id) or ref == id and reference(monde, id) != ref:
            raise ErreurMonde("Tu ne vois plus cette ressource à portée.",
                              f"descripteur.{champ} : reçu {ref!r} ; référence publique portée ou perçue à portée.")
        return id

    if action == "assembler":
        roles = {}
        for c in formulaire["champs"]:
            chemin = c["chemin"]
            if chemin[0] == "pieces":
                roles[chemin[1]] = max(roles.get(chemin[1], 0), chemin[2] + 1) if len(chemin) == 3 else 0
        pieces = p["pieces"]
        if (not isinstance(pieces, dict) or set(pieces) != set(roles)
                or any(n and (not isinstance(pieces[k], list) or len(pieces[k]) != n) for k, n in roles.items())):
            raise ErreurMonde("Pièces mal désignées.", f"descripteur.parametres.pieces : reçu {pieces!r} ; rôles et nombres : {roles}.")
    for c in formulaire["champs"]:
        chemin = c["chemin"]
        parent, cle = p, chemin[-1]
        if chemin == ["cible"]:
            valeur = cible
        else:
            for k in chemin[:-1]:
                parent = parent[k]
            valeur = parent[cle]
        if c["type"] == "ressource":
            if not isinstance(valeur, str) or not valeur or len(valeur) > 1000:
                raise ErreurMonde("Choisis une référence publique pour chaque ressource.",
                                  f"descripteur.{chemin} : reçu {valeur!r} ; chaîne non vide de 1000 caractères au plus.")
            id = exacte(valeur, ".".join(map(str, chemin)))
            if chemin == ["cible"]:
                cible = id
            else:
                parent[cle] = id
        elif c["type"] == "nombre":
            if type(valeur) is not int or valeur < c["minimum"] or ("maximum" in c and valeur > c["maximum"]):
                raise ErreurMonde("Choisis une dimension entière dans les limites du formulaire.",
                                  f"descripteur.{cle} : reçu {valeur!r} ; entier minimum {c['minimum']}, maximum {c.get('maximum', 'selon la pièce')}.")
        elif valeur not in c["choix"]:
            raise ErreurMonde("Ce choix de fabrication est inconnu.",
                              f"descripteur.{cle} : reçu {valeur!r} ; choix {c['choix']}.")
    return fabrication_locale(action, cible, p)


def proposition_descripteur(monde, descripteur):
    """Décode des références exactes ; aucune recherche de nom, ni préalable inventé.

    Le validateur du moteur appelle cette entrée avant ses contrôles usuels. Une
    cible du clic doit rester perçue, ou être une affaire portée pour un geste
    d'inventaire, à réception, même si son nom a changé.
    Les paramètres optionnels ne portent que des choix publics, jamais des effets.
    """
    from .monde import ErreurMonde
    from .noms import reference
    from .voix import reel
    from .gestes_publics import GESTES_CORPS, GESTES_PASSAGE, REACTIONS, dangers_publics
    d = descripteur.contenu
    if (isinstance(d, dict) and d.get('geste') == 'remettre'
            and isinstance(d.get('parametres'), dict) and 'compte' in d['parametres']):
        from .dialogues import valider_choix_compte, remise_convenue
        valider_choix_compte(monde, d)
        if remise_convenue(monde, reel(monde, d['cible']), reel(monde, d['parametres']['destinataire'])):
            raise ErreurMonde('Cet objet relève aussi d’un accord : vérifie ses termes avant de le remettre.',
                              f'descripteur.parametres.compte : reçu restitution de {d["cible"]!r} ; '
                              'attendu aucun accord de remise rémunérée concurrent, ou choix de cet accord.')
        d = {**d, 'parametres': {k: v for k, v in d['parametres'].items() if k != 'compte'}}
    if (not isinstance(d, dict) or not {"geste", "cible"} <= d.keys()
            or d.keys() - {"geste", "cible", "parametres"}
            or any(not isinstance(d[k], str) or not d[k] or len(d[k]) > 1000 for k in ("geste", "cible"))):
        raise ErreurMonde("Je n'ai pas compris ce geste : aucune modification.",
                          "descripteur : geste et cible non vides, parametres optionnels ; aucun autre champ.")
    action, cible = d["geste"], d["cible"]
    if action in GESTES_PASSAGE:
        return passage_descripteur(monde, d)
    if action in {"assembler", "decouper"}:
        return fabrication_descripteur(monde, d)
    actions = {"examiner", "observer", "lire", "allumer", "eteindre", "manger", "ouvrir", "fermer",
               "prendre", "poser", "remettre", "prelever", "deverrouiller", "crocheter", "tourner", "marcher",
               "frapper", "alimenter", "mettre"} | GESTES_CORPS
    if action not in actions:
        raise ErreurMonde("Je ne connais pas ce geste direct.",
                          f"descripteur.geste : reçu {action!r} ; acceptés : {', '.join(sorted(actions))}.")
    parametres = d.get("parametres", {})
    if (not isinstance(parametres, dict) or parametres.keys() - {"outil", "methode", "destinataire", "quantite", "destination", "direction", "parcours"}
            or any(not isinstance(v, str) or len(v) > 1000 for k, v in parametres.items() if k not in {"quantite", "parcours"})):
        raise ErreurMonde("Je n'ai pas compris les paramètres de ce geste.",
                          f"descripteur.parametres : reçu {parametres!r} ; outil, methode, destinataire, destination, direction : chaînes de 1000 caractères au plus ; quantite entière ; parcours structuré de marche.")
    if "parcours" in parametres:
        if action != "marcher" or set(parametres) != {"parcours"}:
            raise ErreurMonde("Ce trajet ne décrit pas une marche directe.",
                              f"descripteur.parametres : reçu {parametres!r}, geste={action!r} ; "
                              "accepté : parcours seul, avec geste=marcher.")
        return {**geste_local(action, cible), "parcours": parametres['parcours']}
    if "direction" in parametres:
        from .spatial import VECTEURS
        if action not in {"pousser", "trainer"} or parametres["direction"] not in ("", *VECTEURS):
            raise ErreurMonde("Choisis une direction de ce geste.",
                              f"descripteur.parametres.direction : reçu {parametres['direction']!r} pour {action} ; accepté pour pousser/trainer : {list(VECTEURS)}, ou vide pour pousser.")
    if action in {"pousser", "trainer"} and "outil" in parametres:
        raise ErreurMonde("Ce geste demande une direction, pas un outil.",
                          f"descripteur.parametres.outil : reçu {parametres['outil']!r} ; accepté : direction, outil absent.")
    if action != "mettre" and "destination" in parametres:
        raise ErreurMonde("Ce geste ne prend pas de destination.",
                          f"descripteur.parametres.destination : reçu {parametres['destination']!r} pour {action} ; accepté : champ absent.")
    if "quantite" in parametres and (action not in {"manger", "prelever"}
            or type(parametres["quantite"]) is not int or parametres["quantite"] != 1):
        raise ErreurMonde("Ce geste ne permet pas cette quantité.",
                          f"descripteur.parametres.quantite : reçu {parametres['quantite']!r} pour {action} ; accepté : 1 pour manger ou prelever, sinon champ absent.")
    if action != "remettre" and "destinataire" in parametres:
        raise ErreurMonde("Ce geste ne prend pas de destinataire.",
                          f"descripteur.parametres.destinataire : reçu {parametres['destinataire']!r} pour {action} ; accepté : champ absent.")

    def exacte(ref, champ, porte=False):
        id = reel(monde, ref)
        # Les références opaques sont des identités stables, y compris après
        # apprentissage du nom. Un nom ou un alias ne remplace jamais une référence.
        affaire = (porte and monde.objets.get(id, {}).get("lieu") == "joueur"
                   and monde.present_physique(id))
        if (id not in monde.objets or not (monde.visible(id) or affaire)
                or ref == id and reference(monde, id) != ref):
            raise ErreurMonde("Tu ne vois plus cette cible ici.",
                              f"descripteur.{champ} : reçu {ref!r} ; une référence publique encore perçue.")
        return id

    if action not in {"tourner", "marcher"}:
        cible = exacte(cible, "cible", action in {"poser", "remettre", "prelever", "manger", "allumer", "eteindre", "alimenter", "mettre", "frapper"})
    corporel = action in GESTES_CORPS and monde.objets.get(cible, {}).get("type") == "personnage"
    if action in GESTES_CORPS - {"frapper"} and not corporel:
        raise ErreurMonde("Ce geste demande une personne en vue.",
                          f"descripteur.cible : reçu {cible!r} ; accepté : personnage perçu.")
    if action in REACTIONS and d["cible"] not in dangers_publics(monde):
        raise ErreurMonde("Cette personne n'est plus un danger perçu.",
                          f"descripteur.cible : reçu {d['cible']!r} ; accepté : {dangers_publics(monde)} pour {action}.")
    if action in {"mettre", "alimenter"} or action == "frapper" and not corporel:
        from .noms import PERSONNES
        if monde.objets[cible]["type"] in (*PERSONNES, "partie_corps"):
            raise ErreurMonde("Ce menu demande un objet, pas un corps.",
                              f"descripteur.cible : reçu {cible!r} ; accepté : objet hors personnage, depouille et partie_corps.")
    if action == "mettre":
        if "outil" in parametres:
            raise ErreurMonde("Ce dépôt demande seulement une destination.",
                              f"descripteur.parametres.outil : reçu {parametres['outil']!r} ; accepté : champ absent.")
        destination = exacte(parametres.get("destination", ""), "parametres.destination", True)
        return geste_local(action, cible, methode=parametres.get("methode", "simple"), destination=destination)
    if action == "remettre":
        destinataire = exacte(parametres.get("destinataire", ""), "parametres.destinataire")
        if monde.objets[destinataire]["type"] != "personnage":
            raise ErreurMonde("La remise demande une personne en vue.",
                              f"descripteur.parametres.destinataire : reçu {parametres.get('destinataire')!r} ; accepté : référence publique d'un personnage perçu.")
        if "outil" in parametres:
            raise ErreurMonde("La remise demande seulement un destinataire.",
                              f"descripteur.parametres.outil : reçu {parametres['outil']!r} ; accepté : champ absent, destinataire dans parametres.destinataire.")
        return geste_local(action, cible, destinataire, parametres.get("methode", "simple"))
    outil = parametres.get("outil", "")
    if outil:
        outil = exacte(outil, "parametres.outil", True)
    return geste_local(action, cible, outil, parametres.get("methode", "simple"),
                       direction=parametres.get("direction", ""))


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
    if personnage:
        from .noms import resoudre as personne
        trouve = personne(monde, texte)
        if trouve:
            return trouve
    for article in ARTICLES:
        if texte.startswith(article):
            texte = texte[len(article):]
            break
    if not texte:
        return None
    # Les mêmes noms que pour tout geste (``Monde.designable``) : ce qu'il verrait en se tournant compte.
    if personnage:
        from .dialogues import interlocuteurs
        from .paroles import _connu_du_joueur
        # Un personnage qu'il sait nommer : pas une voix qu'il ne sait à qui prêter. Celui qu'il
        # connaît sans le voir ici se nomme aussi : le moteur dit qu'il n'est pas là.
        candidats = {d for d in interlocuteurs(monde) if d in monde.objets} | {
            i for i, o in monde.objets.items()
            if o["type"] == "personnage" and _connu_du_joueur(monde, i)}
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


def heler(monde, texte):
    """Héler par son nom quelqu'un que Corvus connaît (``paroles.hele``) : un geste du moteur, jamais
    une interprétation du MJ, même en forme de question (« je crie « Gorm ? » »)."""
    from .paroles import hele
    qui = hele(monde, texte)
    if qui is None:
        return None
    from .operations import etape, sequence
    return sequence(etape("emettre_son", qui, methode="heler"), justification="")


def repondre(monde, texte):
    """Répondre à qui vient de héler Corvus par son nom, ou de lui dire ce qu'il veut
    (``paroles.reponse_a_l_appel``) : « J'arrive ! », « Ici, viens ! », « Qu'est-ce que tu veux ? », les
    paroles de l'appel négocié (``appel``), jamais une interprétation du MJ, même en forme de question."""
    from .paroles import reponse_a_l_appel
    reponse = reponse_a_l_appel(monde, texte)
    if reponse is None:
        return None
    from .appel import METHODES
    from .operations import etape, sequence
    from .voix import designation
    qui, sorte = reponse
    methode = next(m for m, s in METHODES.items() if s == sorte)
    return sequence(etape("emettre_son", designation(monde, qui), methode=methode), justification="")


def cri(monde, texte):
    """Héler quelqu'un, ou répondre à qui vient de héler Corvus : un cri du moteur."""
    return heler(monde, texte) or repondre(monde, texte)


UNITES = {"s": 1, "sec": 1, "seconde": 1, "secondes": 1, "min": 60, "mn": 60, "minute": 60, "minutes": 60,
          "h": 3600, "heure": 3600, "heures": 3600}
DUREE = re.compile(r"(\d+(?:[.,]\d+)?)\s*([a-z]*)")


def attente(texte):
    """« attendre » (cinq minutes), « attendre 30 s », « attendre 10 min », « attendre 1 h 30 » : une
    durée en secondes (``Moteur._attendre``), que le joueur interrompt s'il voit paraître quelqu'un
    ou entend un appel, un cri, un fracas, des paroles dont il saisit les mots. Sans unité, des minutes. Sans durée, cinq minutes
    interruptibles aussi."""
    texte = texte.strip()
    if not texte:
        from .contrats_sequence import ATTENTES
        return proposition("attendre", str(ATTENTES["bloc"]["minutes"] * 60))
    secondes, fin, precedente = 0.0, 0, 3600
    for nombre in DUREE.finditer(texte):
        if texte[fin:nombre.start()].strip() not in ("", "et"):
            return None
        unite = nombre.group(2)
        if unite and unite not in UNITES:
            return None
        # Sans unité, l'unité qui suit la précédente (« 1 h 30 », « 2 min 30 ») : d'abord des minutes.
        facteur = UNITES[unite] if unite else max(1, precedente // 60)
        secondes += float(nombre.group(1).replace(",", ".")) * facteur
        fin, precedente = nombre.end(), facteur
    if fin == 0 or texte[fin:].strip():
        return None
    return proposition("attendre", f"{secondes:g}")


def perception_nommee(monde, texte):
    """La personne connue que vise entièrement une perception locale (« observer Ilse ») ; sinon None.

    Son accès sensoriel (lumière, présence, regard) est tranché par le moteur, qui en dit la cause :
    le contrôle des noms (``noms.verifier_saisie``) ne le devance pas pour un nom déjà relié.
    """
    verbe, sep, reste = normaliser(texte).partition(" ")
    if not sep or VERBES.get(verbe) not in PERCEPTIONS or " avec " in reste:
        return None
    from .noms import PERSONNES
    cible = _nomme(monde, reste, True)
    return cible if monde.objets.get(cible, {}).get("type") in PERSONNES else None


def analyser(monde, texte):
    """Renvoie None pour une intention libre, sans prétendre comprendre tout le français."""
    from .noms import verifier_saisie
    verifier_saisie(monde, texte)
    appel = cri(monde, texte)
    if appel:
        return appel
    if est_question(texte):
        return None
    texte = normaliser(texte)
    decoupe = re.fullmatch(r"decouper (.+) a ([0-9]{1,6}) cm avec (.+)", texte)
    if decoupe:
        cible, longueur, outil = decoupe.groups()
        return fabrication_locale("decouper", monde.trouver(cible),
                                  {"longueur_cm": int(longueur), "outil": monde.trouver(outil)})
    assemblage = re.fullmatch(
        r"assembler (\S+) montants (.+?), (.+?) barreaux (.+?) lien (.+?) outil (.+?) "
        r"longueur ([0-9]{1,6}) largeur ([0-9]{1,6}) rythme (normal|soigne)", texte)
    if assemblage:
        usage, a, b, barreaux, lien, outil, longueur, largeur, rythme = assemblage.groups()
        return fabrication_locale("assembler", usage, {
            "pieces": {"montants": [monde.trouver(a), monde.trouver(b)], "barreaux": monde.trouver(barreaux)},
            "lien": monde.trouver(lien), "outil": monde.trouver(outil),
            "longueur_cm": int(longueur), "largeur_cm": int(largeur), "rythme": rythme})
    for prefixe, methode in (("ramper sous ", "dessous"), ("je rampe sous ", "dessous"),
                              ("passer sous ", "dessous"), ("je passe sous ", "dessous"),
                              ("passer par-dessus ", "dessus"), ("je passe par-dessus ", "dessus"),
                              ("enjamber ", "dessus"), ("escalader ", "dessus")):
        if texte.startswith(prefixe):
            cible = _nomme(monde, texte[len(prefixe):], False)
            if cible is None:
                return None
            return geste_local("passer_obstacle", cible, methode=methode)
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
        return geste_local("marcher", texte[4:])
    if texte.startswith(("tourner ", "se tourner ", "me tourner ")):
        return geste_local("tourner", texte.rsplit(" ", 1)[-1])
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
        foyer, _, bois = texte[10:].partition(" avec ")
        return geste_local("alimenter", monde.trouver(foyer), monde.trouver(bois))
    if texte.startswith("mettre ") and " dans " in texte:
        cible, _, destination = texte[7:].partition(" dans ")
        return geste_local("mettre", monde.trouver(cible), destination=monde.trouver(destination))
    if texte.startswith("manger "):
        return geste_local("manger", monde.trouver(texte[7:]))
    if texte.startswith("prelever "):
        return geste_local("prelever", monde.trouver(texte[9:]))
    if texte.startswith("sonner "):
        from .operations import etape, sequence
        return sequence(etape("emettre_son", monde.trouver(texte[7:]), methode="simple"))
    if texte.startswith("franchir ") and " avec " in texte:
        cible, _, outil = texte[9:].partition(" avec ")
        cible, outil = _nomme(monde, cible, False), _nomme(monde, outil, False)
        if cible is None or outil is None:
            return None
        from .monde import ErreurMonde
        try:
            return passage_memorise(monde, cible, outil)
        except ErreurMonde:
            return None  # Premier arbitrage : le chemin libre reste disponible.
    if texte.startswith("installer ") and " contre " in texte:
        cible, _, support = texte[10:].partition(" contre ")
        return proposition("installer", monde.trouver(cible), monde.trouver(support))
    for prefixe, action in (("monter ", "franchir"), ("descendre ", "franchir"), ("desinstaller ", "desinstaller")):
        if texte.startswith(prefixe):
            return proposition(action, monde.trouver(texte[len(prefixe):]))
    for prefixe in DONNER:
        if texte.startswith(prefixe):
            return don(monde, texte[len(prefixe):])
    if texte.startswith("trainer "):
        cible, sep, direction = texte[8:].partition(" vers ")
        return geste_local("trainer", monde.trouver(cible), direction=direction.removeprefix("le ").removeprefix("l'"))
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
        return geste_local("pousser", cible, direction=direction)
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
    if texte == "attendre" or texte.startswith("attendre "):
        return attente(texte[9:])
    if texte in ("se liberer", "me liberer", "liberer"):
        return proposition("liberer", "joueur")
    if texte in ("se degager", "me degager", "degager"):
        return proposition("degager")
    if texte in ("fuir", "s'enfuir"):
        return geste_local("fuir", "")
    for prefixe, action in (("riposter ", "riposter"), ("se rendre a ", "se_rendre"),
                            ("assommer ", "frapper")):
        if texte.startswith(prefixe):
            cible, avec, outil = texte[len(prefixe):].partition(" avec ")
            return geste_local(action, monde.trouver(cible), monde.trouver(outil) if avec else "",
                               "assommer" if prefixe == "assommer " else "simple")
    verbe, sep, reste = texte.partition(" ")
    if not sep or verbe not in VERBES:
        return None
    cible, avec, outil = reste.partition(" avec ")
    # Une phrase longue ne doit pas être transformée silencieusement en commande approchante.
    if len(cible.split()) > 9 or (avec and len(outil.split()) > 6):
        return None
    action = VERBES[verbe]
    # Une perception peut nommer une personne connue hors de vue. C'est le
    # moteur qui tranche ensuite son accès sensoriel, comme pour la scène.
    cible_id = (_nomme(monde, cible, True) if action in PERCEPTIONS else None) or monde.trouver(cible)
    outil_id = monde.trouver(outil) if avec else ""
    methode = "simple"
    if action == "detacher":
        t = monde.objets.get(outil_id, {})
        usages = t.get("usages", [])
        methode = ("percussion" if "percussion" in usages and "levier" not in usages else "levier") if outil_id else "simple"
    return geste_local(action, cible_id, outil_id, methode)
