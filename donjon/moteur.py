"""Arbitrage borné et transitions atomiques. Le MJ ne reçoit aucun accès en écriture."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

from .monde import ErreurMonde, objet
from .francais import accorder, complement_de, designer
from .geometrie import position_entree, position_objet
from .deplacement_objet import deplacer
from .rendu import decrire, decrire_contexte, decrire_perception, regarder, prix, toucher
from .perception import avancer_combustion, eclairage
from .dialogues import verifier_remise, payer_remise
from .vol import proprietaire, appliquer as appliquer_vol
from .capacites_objet import statut as statut_capacite, absence as absence_capacite
from .refus import inaccessible, liste, portes_avec_usage


ACTIONS = ["examiner", "toucher", "prendre", "poser", "acheter", "ouvrir", "fermer",
           "deverrouiller", "crocheter", "frapper", "couper", "detacher", "bloquer", "debloquer",
           "copier", "lire", "parler", "aller", "attendre", "observer", "allumer", "eteindre",
           "remettre", "voler", "installer", "franchir", "desinstaller", "marcher", "ecouter", "clarifier", "impossible"]
METHODES = ["simple", "finesse", "levier", "percussion", "traction"]


class QualificationRequise(ErreurMonde):
    """Une propriété de la cible est inconnue, sans conclure à un échec fictif."""

    def __init__(self, cible, capacite):
        self.cible = cible
        self.capacite = capacite
        super().__init__(f"La capacité {capacite} de {cible} reste à établir.",
                         f"propose d'abord etablir_faits avec une qualification de « {capacite} » pour {cible} "
                         "(pour une coupe : objet, moyen et coupe_possible) ; l'intention sera réexaminée ensuite.")


def proposition(action, cible="", outil="", methode="simple", difficulte=0, justification=""):
    return dict(action=action, cible=cible, outil=outil, methode=methode,
                difficulte=difficulte, justification=justification)


@dataclass
class Plan:
    proposition: dict
    revision: int
    titre: str
    stat: str = ""
    dd: int = 0
    bonus: int = 0
    minutes: int = 1
    bruit: int = 0
    effets: list = field(default_factory=list)
    echec_critique: list = field(default_factory=list)
    echec: list = field(default_factory=list)
    risque: str = ""
    information: str = ""
    cle_arbitrage: str = ""
    origine: str = "règles"
    etapes: list = field(default_factory=list)
    plans: list = field(default_factory=list)
    effort: bool = True        # le geste creuse et fatigue (``corps``)

    def resume(self, monde, afficher_avis=True):
        if self.etapes:
            plusieurs = len(self.plans) > 1
            lignes = [f"Une seule tentative, en {len(self.plans)} étapes successives :" if plusieurs else "Tentative proposée :"]
            lignes.extend((f"\nÉtape {i} — " if plusieurs else "") + p.resume(monde, afficher_avis=False)
                          for i, p in enumerate(self.plans, 1))
            if plusieurs:
                lignes.append(f"Durée totale prévue : {self.minutes} min. Arrêt au premier échec ; les étapes déjà réussies restent acquises.")
            lignes.append("« tenter » lance l'ensemble ; « annuler » abandonne sans exécuter aucune étape.")
            return "\n".join(lignes)
        lignes = [self.titre]
        if self.stat:
            from .corps import malus
            mod, corps = (monde.joueur["stats"][self.stat] - 10) // 2, malus(monde, self.stat)
            lignes.append(f'Test {self.stat} ({mod:+d}), outil {self.bonus:+d}'
                          + (f', faim, froid ou fatigue {corps:+d}' if corps else '') + f', difficulté {self.dd}.')
        else:
            lignes.append("Pas de jet nécessaire.")
        if self.echec_critique:
            lignes.append("Risque sur un 1 naturel : outil endommagé.")
        if self.risque:
            lignes.append(self.risque)
        if self.minutes:
            lignes.append(f'Durée : {self.minutes} min. Bruit : {self.bruit}.')
        return "\n".join(lignes)


class Moteur:
    def __init__(self, monde):
        self.monde = monde

    @staticmethod
    def _action_journal(monde, proposition):
        """Le journal décrit une action structurée, sans prose libre du MJ."""
        action = copy.deepcopy(proposition)
        if "justification" in action:
            action["justification"] = ""
        if action.get("action") == "improviser":
            from .improvisation import action_persistante
            action = action_persistante(monde, action)
        return action

    def preparer(self, p, origine="règles"):
        from .operations import preparer as preparer_operations
        if isinstance(p, dict) and p.get("action") == "improviser":
            from .improvisation import preparer
            return preparer(self.monde, p, origine)
        if isinstance(p, dict) and p.get("action") == "fabriquer":
            from .artisanat import preparer
            return preparer(self.monde, p, origine)
        if isinstance(p, dict) and p.get("action") == "composer":
            return preparer_operations(self.monde, p, origine)
        attendus = set(proposition("examiner"))
        if not isinstance(p, dict) or set(p) != attendus:
            recus = sorted(p) if isinstance(p, dict) else type(p).__name__
            raise ErreurMonde("Je n'ai pas compris ce geste : aucune modification.",
                              f"une action simple a exactement les champs {', '.join(sorted(attendus))} ; reçu : {recus}.")
        fautifs = [k for k in ("action", "cible", "outil", "methode", "justification")
                   if not isinstance(p[k], str) or len(p[k]) > 1000]
        if fautifs:
            raise ErreurMonde("Je n'ai pas compris ce geste : aucune modification.",
                              f"champ(s) {', '.join(fautifs)} : du texte, 1000 caractères au plus.")
        if type(p["difficulte"]) is not int or not 0 <= p["difficulte"] <= 25:
            raise ErreurMonde("Difficulté invalide.", f"difficulte : un entier de 0 à 25 (reçu {p['difficulte']!r}).")
        action, cible, outil = p["action"], p["cible"], p["outil"]
        if action not in ACTIONS:
            raise ErreurMonde("Je ne connais pas ce geste.",
                              f"action « {action} » inconnue ; actions : {', '.join(ACTIONS[:-2])} ; ou composer pour "
                              "enchaîner des opérations, ou improviser pour un geste hors de ces actions.")
        if p["methode"] not in METHODES:
            raise ErreurMonde("Je ne connais pas cette façon de faire.",
                              f"methode « {p['methode']} » inconnue pour une action simple ; méthodes : {', '.join(METHODES)}.")
        if action in ("clarifier", "impossible"):
            raise ErreurMonde("Aucune action exécutable n'a été proposée.",
                              f"{action} ne s'exécute pas : réponds en mode dialogue.")
        if action in ("prendre", "poser", "voler", "detacher", "allumer", "eteindre"):
            return preparer_operations(self.monde, p, origine)
        if action in ("installer", "franchir", "desinstaller"):
            from .artisanat import preparer_usage
            return preparer_usage(self.monde, p, origine)
        m = self.monde
        plan = Plan(dict(p), m.data["revision"], "", origine=origine)
        if action == "marcher" or (action == "aller" and m.data.get("mode_cases")):
            from .spatial import preparer_pas
            if not m.data.get("mode_cases"):
                sorties = ", ".join(m.data["salles"][m.joueur["salle"]]["sorties"]) or "aucune"
                raise ErreurMonde("Lance cette partie avec --cases pour te déplacer case par case.",
                                  f"partie sans cases : utilise aller avec une sortie ({sorties}).")
            if outil or p["methode"] != "simple" or p["difficulte"]:
                raise ErreurMonde("Un pas se fait sans outil ni jet.", "un pas : outil vide, methode simple, difficulte 0.")
            destination = preparer_pas(m, cible)
            plan.titre = "Avancer d'un pas vers " + cible + "."
            plan.minutes = 1 if m.data.get("pas_depuis_minute", 0) == 9 else 0
            plan.effets = [("marcher", "", destination)]
            return plan
        if action == "observer":
            if cible not in ("", "scene", "lumiere", "contexte") or outil:
                raise ErreurMonde("On observe la scène, la lumière ou le contexte, pas un objet précis.",
                                  f"observer : cible vide, scene, lumiere ou contexte (reçu « {cible} »), outil vide ; "
                                  "pour un objet précis : examiner, toucher ou lire avec son identifiant.")
            plan.titre, plan.minutes = "Observer la scène.", 0
            plan.information = (decrire_contexte(m) if cible == "contexte" else
                                regarder(m) if cible == "scene" else decrire_perception(m))
            return plan
        if action == "ecouter":
            if cible or outil:
                raise ErreurMonde("Écouter se fait sur place, sans cible ni outil : on tend l'oreille.",
                                  "ecouter : cible et outil vides.")
            plan.titre, plan.minutes, plan.effort = "Tendre l'oreille quelques minutes.", 3, False
            return plan
        if action == "attendre":
            plan.titre, plan.minutes, plan.effort = "Attendre cinq minutes.", 5, False
            plan.effets = [("calmer", "", 3)]
            return plan
        if action == "aller":
            sorties = m.data["salles"][m.joueur["salle"]]["sorties"]
            sortie = sorties.get(cible)
            if not sortie:
                raise ErreurMonde(f"Il n'y a pas de sortie vers « {cible} » d'ici.",
                                  f"aller : cible = une direction de sortie parmi {', '.join(sorties) or 'aucune'}.")
            porte = m.objets.get(sortie["porte"])
            if porte and not porte["ouverte"]:
                raise ErreurMonde(designer(porte, debut=True) + " fermée te barre le passage.",
                                  f"ouvre d'abord {porte['id']} (ouvrir, ou deverrouiller avec sa clé si elle est "
                                  "verrouillée), éventuellement dans un composer.")
            plan.titre = "Aller vers " + cible + "."
            plan.effets = [("voyager", sortie["vers"], None)]
            return plan
        if action == "remettre":
            mission = verifier_remise(m, cible, outil)
            from .proximite import exiger
            exiger(m, m.data["missions"][mission]["donneur"])
            plan.titre = "Remettre " + designer(m.objets[cible]) + " contre la récompense convenue."
            plan.effets = [("remettre", mission, None)]
            return plan
        if not m.accessible(cible):
            raise inaccessible(m, cible)
        if action not in ("examiner", "parler"):
            from .proximite import exiger
            exiger(m, cible)
        if action == "examiner" and not m.visible(cible):
            raise ErreurMonde("Il fait trop noir pour examiner cet objet. Tu peux toucher tes affaires ou allumer une lumière.",
                              "examiner exige de voir : toucher fonctionne dans le noir, ou allume d'abord une source.")
        if action in ("lire", "detacher", "copier") and eclairage(m)["niveau"] < 2:
            raise ErreurMonde(f"La lumière est trop faible pour {action} avec précision.",
                              f"{action} exige une lumière franche : allume d'abord une source (allumer), "
                              "éventuellement dans un composer.")
        o = m.objets[cible]
        t = None
        if outil:
            t = m.objets.get(outil)
            if not t:
                portes = sorted(i for i, x in m.objets.items() if x["lieu"] == "joueur")
                raise ErreurMonde("Tu n'as rien de tel en main.",
                                  f"outil « {outil} » n'est pas un identifiant connu ; objets portés : {', '.join(portes) or 'aucun'}.")
            if t["lieu"] != "joueur":
                portes = sorted(i for i, x in m.objets.items() if x["lieu"] == "joueur")
                raise ErreurMonde("Tu n'as pas " + designer(t) + " en main.",
                                  f"prends d'abord {outil} : composer avec une étape deplacer {outil} vers joueur, puis ce geste."
                                  if m.accessible(outil) else
                                  f"{outil} n'est pas à portée ; objets portés : {liste(portes)}.")
            if t["integrite"] == 0:
                raise ErreurMonde(designer(t, debut=True) + " est hors d'usage.", "choisis un autre outil.")
            if outil == cible:
                raise ErreurMonde("La cible ne peut pas être son propre outil.", "outil : un autre objet que la cible, ou vide.")
        verbe = {"detacher": "Détacher", "deverrouiller": "Déverrouiller", "debloquer": "Débloquer", "eteindre": "Éteindre", "parler": "Parler à"}.get(action, action.capitalize())
        plan.titre = verbe + " " + designer(o) + (" avec " + designer(t) if t else "") + "."
        if action in ("examiner", "toucher"):
            plan.minutes = 0
            detail = True
            if m.data.get("mode_cases"):
                from .spatial import proche
                detail = proche(m, cible)
            plan.information = decrire(m, cible, detail=detail, technique=detail) if action == "examiner" else toucher(m, cible)
            if action == "examiner" and not detail:
                plan.information += " Approche-toi pour distinguer les petits détails."
            plan.effets = [("connaitre", cible, None)]
            if action == "toucher" and o["type"] == "contenant" and o["ouverte"]:
                plan.effets.extend(("connaitre", enfant["id"], None)
                                   for enfant in m.enfants(cible) if m.present_physique(enfant["id"]))
        elif action == "parler":
            if o["type"] != "personnage":
                raise ErreurMonde(designer(o, debut=True) + " ne peut pas te répondre.",
                                  "parler vise un personnage présent ; pour un objet : examiner.")
            raise ErreurMonde("Pour discuter librement, active le MJ et adresse ta question au personnage. "
                              "Hors ligne : offre <personnage>, negocier <personnage> <montant>, accepter offre, remettre <objet>.",
                              "pour faire parler Corvus à ce personnage : mode parole_joueur ; pour une récompense "
                              "de mission : mode conversation_pnj.")
        elif action == "acheter":
            possesseur = proprietaire(m, o)
            if possesseur not in (None, "joueur") and o.get("vole_par") != "joueur" and not o.get("en_vente"):
                raise ErreurMonde(designer(o, debut=True) + " appartient à " + designer(m.objets[possesseur])
                                  + " et n'est pas à vendre.",
                                  f"{cible} n'est pas en vente : demande-le en mode parole_joueur, ou propose voler "
                                  "si le joueur l'a explicitement voulu.")
            if not o["mobile"] or o.get("attache") or o.get("cale_de"):
                raise ErreurMonde(designer(o, debut=True) + " ne peut pas être emporté en l'état.",
                                  f"{cible} est fixe, attaché ou sert de cale : detacher ou debloquer d'abord, "
                                  "s'il est mobile.")
            if o["lieu"] == "joueur":
                raise ErreurMonde("Tu as déjà " + designer(o) + ".", f"{cible} est déjà porté : rien à acheter.")
            if m.charge() + o["masse"] > m.joueur["capacite"]:
                raise ErreurMonde(designer(o, debut=True) + " est trop lourd pour ce que tu portes déjà.",
                                  f"charge {m.charge()} + masse {o['masse']} > capacité {m.joueur['capacite']} : "
                                  "pose d'abord quelque chose (composer, étape deplacer vers la salle).")
            vendeur_id = o.get("vendeur")
            vendeur = m.objets.get(vendeur_id) if vendeur_id else None
            if not o.get("en_vente") or not vendeur or vendeur["type"] != "personnage":
                en_vente = sorted(i for i, x in m.objets.items() if x.get("en_vente") and m.accessible(i))
                raise ErreurMonde(designer(o, debut=True) + " n'est pas à vendre ici.",
                                  f"acheter vise un objet en vente, parmi {liste(en_vente)}.")
            if not m.present_physique(vendeur_id):
                raise ErreurMonde(designer(vendeur, debut=True) + " doit être présent pour cette vente.",
                                  f"le vendeur {vendeur_id} n'est pas dans la salle : rien à acheter tant qu'il est absent.")
            from .proximite import exiger
            exiger(m, vendeur_id)
            if (vendeur.get("refuse_ventes_apres_vol")
                    and m.data["relations_pnj"][vendeur_id]["vols_surpris"]):
                raise ErreurMonde(designer(vendeur, debut=True) + " refuse de te vendre quoi que ce soit depuis ta tentative de vol.",
                                  f"{vendeur_id} ne vend plus au joueur : aucune vente possible avec lui.")
            cout = prix(m, o)
            if cout > m.joueur["or"]:
                raise ErreurMonde(f"Il te faudrait {cout} pièces ; tu n'en as que {m.joueur['or']}.",
                                  f"prix {cout} > or {m.joueur['or']} : achat impossible ; une négociation passe par "
                                  "le mode parole_joueur.")
            plan.effets.append(("payer", cible, {"vendeur": vendeur_id, "montant": cout}))
            plan.effets.append(("deplacer", cible, "joueur"))
        elif action in ("ouvrir", "fermer", "deverrouiller"):
            if o["type"] not in ("porte", "contenant"):
                ouvrables = sorted(i for i, x in m.objets.items()
                                   if x["type"] in ("porte", "contenant") and m.accessible(i))
                raise ErreurMonde(designer(o, debut=True) + " ne s'ouvre ni ne se ferme.",
                                  f"{action} vise une porte ou un contenant, parmi {liste(ouvrables)} ; "
                                  f"{cible} est de type {o['type']}.")
            if action == "deverrouiller" or (action == "ouvrir" and o["verrouillee"] and t):
                cles = sorted(i for i, x in m.objets.items() if x["lieu"] == "joueur" and cible in x.get("ouvre", []))
                if not t or cible not in t.get("ouvre", []):
                    raise ErreurMonde(("Il te faut une clé pour cela." if not t else
                                       designer(t, debut=True) + " ne convient pas à cette serrure."),
                                      f"outil : une clé en main qui ouvre {cible}, parmi {liste(cles)}"
                                      + ("" if cles else " ; sinon crocheter avec un outil de crochetage, ou forcer"
                                         " (frapper)") + ".")
                if not o["verrouillee"]:
                    raise ErreurMonde(designer(o, debut=True) + " n'est pas verrouillé.",
                                      f"{cible} n'est pas verrouillé : ouvrir suffit.")
                plan.effets.append(("deverrouiller", cible, None))
            elif action == "ouvrir" and o["verrouillee"]:
                cles = sorted(i for i, x in m.objets.items() if x["lieu"] == "joueur" and cible in x.get("ouvre", []))
                raise ErreurMonde("C'est verrouillé. Il faut une clé adaptée ou une autre manœuvre.",
                                  f"{cible} est verrouillé : " + (f"outil = {cles[0]} (clé en main qui l'ouvre)" if cles else
                                  "aucune clé en main ne l'ouvre ; crocheter avec un outil de crochetage, ou forcer (frapper)")
                                  + ".")
            if action != "deverrouiller":
                ouvrir = action == "ouvrir"
                if o["ouverte"] == ouvrir:
                    raise ErreurMonde("C'est déjà " + ("ouvert." if ouvrir else "fermé."),
                                      f"{cible} est déjà {'ouvert' if ouvrir else 'fermé'} : rien à faire.")
                if not ouvrir and o.get("bloque_par"):
                    raise ErreurMonde("Impossible de refermer : " + designer(o) + " est calé.",
                                      f"debloquer {cible} d'abord, éventuellement dans un composer.")
                if not ouvrir and (o["integrite"] == 0 or o.get("detachee")):
                    raise ErreurMonde("Impossible de refermer : le battant est brisé ou détaché.",
                                      f"{cible} ne peut plus être fermé.")
                plan.effets.append(("ouverture", cible, ouvrir))
        elif action == "crocheter":
            parent_id = o["lieu"] if o["type"] == "serrure" else cible
            parent = m.objets.get(parent_id, {})
            if not parent.get("verrouillee"):
                verrous = sorted(i for i, x in m.objets.items() if x.get("verrouillee") and m.accessible(i))
                raise ErreurMonde("Il n'y a rien de verrouillé à crocheter là.",
                                  f"crocheter vise une porte ou un contenant verrouillé (ou sa serrure), parmi {liste(verrous)}.")
            if o.get("bloquee") or any(e.get("bloquee") for e in m.enfants(parent_id)):
                raise ErreurMonde("La serrure est bloquée ; le crochetage ne peut plus fonctionner.",
                                  f"serrure de {parent_id} grippée : il faut sa clé, ou forcer (frapper).")
            if not t or "crochetage" not in t.get("usages", []):
                raise ErreurMonde("Il faut un outil adapté pour crocheter.",
                                  f"outil : un objet en main d'usage crochetage, parmi {liste(portes_avec_usage(m, 'crochetage'))}.")
            lumiere = eclairage(m)["niveau"]
            plan.stat, plan.dd, plan.minutes = "DEX", 14 + 4 * (2 - lumiere), 3 + 2 * (2 - lumiere)
            if lumiere < 2:
                plan.titre = plan.titre[:-1] + " à tâtons."
            plan.effets = [("deverrouiller", parent_id, None)]
            plan.echec_critique = [("endommager", outil, 1)]
            serrure = next((e["id"] for e in m.enfants(parent_id) if e["type"] == "serrure"), None)
            if serrure:
                plan.echec_critique.append(("gripper", serrure, None))
        elif action in ("frapper", "couper"):
            if o["type"] in ("personnage", "partie_corps", "motif", "tresor"):
                raise ErreurMonde("Cette destruction ou ce combat n'est pas simulé dans ce prototype.",
                                  f"{action} ne vise pas un {o['type']} : aucune proposition de ce geste n'est possible.")
            if o["integrite"] == 0:
                raise ErreurMonde("C'est déjà brisé.", f"{cible} est déjà détruit : rien à faire.")
            usages = set(t.get("usages", [])) if t else set()
            puissance = t.get("puissance", 0) if t else 0
            coupe = bool(usages & {"couper", "couper_bois"}) and (
                puissance >= o["seuil_coupe"] if "seuil_coupe" in o else
                statut_capacite(o, "tranchable", t) == "etablie")
            choc = bool(usages & {"percussion", "levier"})
            if action == "couper" and not usages & {"couper", "couper_bois"}:
                tranchants = sorted(set(portes_avec_usage(m, "couper")) | set(portes_avec_usage(m, "couper_bois")))
                raise ErreurMonde("Il faut un outil de coupe utilisable.",
                                  f"outil : un objet en main d'usage couper ou couper_bois, parmi {liste(tranchants)}"
                                  + (f" ; {outil} n'a pas cet usage" if outil else "") + ".")
            if usages & {"couper", "couper_bois"} and (action == "couper" or not choc):
                etat_coupe = statut_capacite(o, "tranchable", t)
                if etat_coupe == "inconnue":
                    raise QualificationRequise(cible, "tranchable")
                if etat_coupe == "ecartee":
                    from .capacites_objet import constat as constat_capacite
                    raise ErreurMonde(absence_capacite(
                        o, "tranchable", constat_capacite(o, "tranchable", t)) + ".",
                        f"{cible} ne se coupe pas avec {outil} (qualification établie) : ne re-propose pas cette coupe.")
            if action == "couper" and not coupe:
                raise ErreurMonde(designer(t, debut=True) + " ne peut pas entamer " + designer(o) + ".",
                                  f"puissance de {outil} : {puissance}"
                                  + (f", seuil de coupe de {cible} : {o['seuil_coupe']}" if "seuil_coupe" in o else "")
                                  + " ; il faut un outil plus puissant.")
            if action == "frapper" and not (coupe or choc):
                chocs = sorted(set(portes_avec_usage(m, "percussion")) | set(portes_avec_usage(m, "levier")))
                raise ErreurMonde("Il faut un outil adapté à cette cible pour la frapper ou l'entamer.",
                                  f"outil : un objet en main d'usage percussion ou levier, parmi {liste(chocs)}"
                                  + (f" ; {outil} ne convient pas" if outil else " ; outil vide refusé") + ".")
            if action == "couper":
                plan.titre = "Entailler " + designer(o) + " avec " + designer(t) + "."
            plan.stat, plan.dd = "FOR", 10
            plan.bonus, plan.bruit = (2 if action == "frapper" and "percussion" in usages else 0), 3
            degats = puissance + max(0, (m.joueur["stats"]["FOR"] - 10) // 2)
            plan.effets = [("endommager", cible, degats)]
            plan.echec_critique = [("endommager", outil, 1)]
        elif action == "bloquer":
            if o["type"] != "porte":
                raise ErreurMonde("On ne cale qu'une porte.", f"bloquer vise une porte ; {cible} est de type {o['type']}.")
            if not o["ouverte"]:
                raise ErreurMonde(designer(o, debut=True) + " est fermée : on cale une porte ouverte.",
                                  f"ouvre d'abord {cible}, éventuellement dans un composer.")
            if o["detachee"] or o["integrite"] == 0:
                raise ErreurMonde(designer(o, debut=True) + " n'est plus montée : rien à caler.",
                                  f"{cible} est brisée ou détachée.")
            if o["bloque_par"]:
                raise ErreurMonde("La porte est déjà calée.", f"{cible} est déjà calée par {o['bloque_par']}.")
            if not t or "cale" not in t.get("usages", []):
                raise ErreurMonde("Il faut un objet utilisable comme cale.",
                                  f"outil : un objet en main d'usage cale, parmi {liste(portes_avec_usage(m, 'cale'))}.")
            plan.effets = [("caler", cible, outil)]
        elif action == "debloquer":
            porte_id = o.get("cale_de") or cible
            if not m.objets[porte_id].get("bloque_par"):
                raise ErreurMonde("Cette porte n'est pas calée.", f"{porte_id} n'est pas calée : rien à débloquer.")
            plan.effets = [("decaler", porte_id, m.joueur["salle"])]
        elif action == "copier":
            if not o.get("motif"):
                motifs = sorted(i for i, x in m.objets.items() if x.get("motif") and m.accessible(i))
                raise ErreurMonde("Il n'y a pas de motif à copier sur " + designer(o) + ".",
                                  f"copier vise un objet portant un motif, parmi {liste(motifs)}.")
            parent = m.objets.get(o["lieu"])
            if parent and parent["integrite"] == 0:
                raise ErreurMonde("Le support brisé ne permet plus une empreinte lisible.",
                                  f"{cible} n'est plus copiable.")
            if not t or "empreinte" not in t.get("usages", []) or t.get("charges", 0) < 1:
                raise ErreurMonde("Il faut un matériau à empreinte encore utilisable.",
                                  "outil : un objet en main d'usage empreinte et avec des charges, parmi "
                                  f"{liste(i for i in portes_avec_usage(m, 'empreinte') if m.objets[i].get('charges', 0) > 0)}.")
            plan.minutes = 2
            plan.effets = [("empreinte", cible, outil)]
        elif action == "lire":
            if not o.get("inscription"):
                lisibles = sorted(i for i, x in m.objets.items() if x.get("inscription") and m.accessible(i))
                raise ErreurMonde(designer(o, debut=True) + " ne porte pas d'inscription lisible.",
                                  f"lire vise un objet portant une inscription, parmi {liste(lisibles)} ; "
                                  f"pour décrire {cible} : examiner.")
            parent = m.objets.get(o["lieu"])
            if parent and parent["integrite"] == 0:
                raise ErreurMonde("L'inscription a été détruite avec son support.", f"{cible} n'est plus lisible.")
            if cible in m.data["lus"]:
                plan.minutes = 0
                plan.information = decrire(m, cible, detail=True)
            else:
                plan.stat, plan.dd, plan.minutes = "INT", 12, 2
                plan.effets = [("dechiffrer", cible, None)]
        else:
            raise ErreurMonde("Action non implémentée.", f"action « {action} » sans règle : choisis une autre action.")
        return plan

    def executer(self, plan):
        # Ne pas faire confiance à un Plan muté : recompiler depuis la proposition et l'état courant.
        if plan.revision != self.monde.data["revision"]:
            raise ErreurMonde("Le monde a changé : demandez un nouvel arbitrage.")
        plan = self.preparer(plan.proposition, plan.origine)
        if plan.etapes:
            return self._executer_operations(plan)
        if plan.proposition["action"] == "observer":
            return plan.information
        travail = self.monde.copier()
        lignes = []
        reussite, jet = True, None
        if plan.stat:
            from .corps import malus
            jet = travail.d20()
            mod, corps = (travail.joueur["stats"][plan.stat] - 10) // 2, malus(travail, plan.stat)
            total = jet + mod + plan.bonus + corps
            # Pas de réussite automatique sur 20 : les impossibilités sont rejetées avant le jet.
            reussite = jet != 1 and total >= plan.dd
            lignes.append(f'1d20({jet}) + {plan.stat}({mod:+d}) + outil({plan.bonus:+d}) '
                          + (f'+ corps({corps:+d}) ' if corps else '')
                          + f'= {total} contre {plan.dd} : ' + ("REUSSITE" if reussite else "ECHEC"))
        effets = plan.effets if reussite else plan.echec + (plan.echec_critique if jet == 1 else [])
        for effet in effets:
            self._appliquer(travail, effet, lignes)
        if not reussite and plan.proposition["action"] != "improviser":
            lignes.append("La tentative n'aboutit pas.")
        elif plan.information:
            lignes.append(plan.information)
        self._terminer_etape(travail, plan, lignes)
        travail.data["revision"] += 1
        travail.data["journal"].append({"tour": travail.data["revision"],
            "minutes": travail.data["minutes"], "action": self._action_journal(travail, plan.proposition),
            "origine": plan.origine, "dd": plan.dd, "jet": jet,
            "reussite": reussite, "faits": lignes[:]})
        travail.verifier()
        self.monde.data = travail.data
        return "\n".join(lignes) or "Action accomplie."

    @staticmethod
    def _terminer_etape(travail, plan, lignes):
        Moteur._stabiliser(travail, lignes)
        # Le feu se consume minute par minute avec la vie des PNJ (``pnj.avancer``).
        travail.data["minutes"] += plan.minutes
        travail.data["bruit"] = max(0, travail.data["bruit"] + plan.bruit)
        # Le corps du joueur suit le temps passé : l'effort creuse, attendre repose.
        from .corps import CALMES, vivre_joueur
        action = plan.proposition.get("action")
        vivre_joueur(travail, plan.minutes, effort=plan.effort and action not in CALMES,
                     repos=action == "attendre", lignes=lignes)
        # Les PNJ voient d'abord le résultat du geste du joueur, puis agissent à leur tour.
        from .esprits import percevoir_tous
        percevoir_tous(travail)
        from .pnj import avancer as avancer_pnj
        apparus = avancer_pnj(travail, plan.minutes, lignes)
        # Ce qui parvient à ses oreilles : le fort de lui-même, le bas en écoutant.
        from .ecoute import ECOUTE, ENTENDU, entendus, rendre
        ecoute = plan.proposition.get("action") == "ecouter"
        entendu = rendre(travail, entendus(travail, travail.data["minutes"] - plan.minutes,
                                           ECOUTE if ecoute else ENTENDU))
        lignes.extend(entendu)
        if ecoute and not entendu:
            lignes.append("Tu tends l'oreille : rien de particulier ne te parvient.")
        if any(e[0] == "emettre_son" for e in plan.effets) and not apparus:
            lignes.append("Pour l'instant, aucune réponse ne te parvient.")
        from .horloges import declencher as declencher_horloges
        declencher_horloges(travail, lignes)
        percevoir_tous(travail)
        from .sons import auditeurs
        a_portee = set(auditeurs(travail, travail.joueur["salle"], 3))
        for id, relation in travail.data["relations_pnj"].items():
            if id not in a_portee or any(e[0] == "emettre_son" for e in plan.effets):
                # L'audition a déjà été résolue spatialement, sans alerter tout le monde.
                continue
            pnj = travail.objets[id]
            from .vol import mefiance
            humeur = "méfiant" if mefiance(travail, id) else "inquiet" if travail.data["bruit"] >= 6 else "calme"
            if pnj.get("humeur") != humeur and travail.visible(id):
                lignes.append(pnj["nom"] + " semble " + humeur + ".")
            pnj["humeur"] = humeur
        travail.actualiser_souvenirs_personnages()
        from .objectifs import actualiser as actualiser_objectif
        actualiser_objectif(travail, lignes)
        if travail.data.get("mode_cases"):
            from .spatial import memoriser
            memoriser(travail)
        if plan.cle_arbitrage:
            travail.data["arbitrages"][plan.cle_arbitrage] = {
                "dd": plan.dd, "justification": "", "origine": plan.origine}

    def _executer_operations(self, sequence):
        from .operations import compiler
        travail, lignes, trace, precedent = self.monde.copier(), [], [], None
        reussite, dernier_jet, dernier_dd = True, None, 0
        for numero, e in enumerate(sequence.etapes, 1):
            # Revalider sur l'état issu des étapes précédentes, jamais sur les effets du LLM.
            p = compiler(travail, e, precedent, sequence.proposition["justification"], sequence.origine)
            details, jet = [], None
            if p.stat:
                from .corps import malus
                jet = travail.d20()
                mod, corps = (travail.joueur["stats"][p.stat] - 10) // 2, malus(travail, p.stat)
                total = jet + mod + p.bonus + corps
                reussite = jet != 1 and total >= p.dd
                dernier_jet, dernier_dd = jet, p.dd
                details.append(f"1d20({jet}) + {p.stat}({mod:+d}) + outil({p.bonus:+d}) "
                               + (f"+ corps({corps:+d}) " if corps else "")
                               + f"= {total} contre {p.dd} : " + ("REUSSITE" if reussite else "ECHEC"))
            effets = p.effets if reussite else p.echec + (p.echec_critique if jet == 1 else [])
            for effet in effets:
                self._appliquer(travail, effet, details)
            self._terminer_etape(travail, p, details)
            if e["operation"] == "patienter":
                details.append("Deux minutes passent à guetter une occasion ; rien ne garantit que le geste passera inaperçu.")
            if not reussite:
                details.append("Tu atteins le sol mais amortis mal la réception. La suite de la manœuvre est abandonnée."
                               if e["operation"] == "sauter" else
                               "La tentative n'aboutit pas. La suite de la manœuvre est abandonnée.")
            trace.append({"numero": numero, "operation": e, "jet": jet, "dd": p.dd, "reussite": reussite,
                          "minutes": p.minutes, "effets_appliques": [list(effet) for effet in effets], "faits": details[:]})
            lignes.extend(details)
            if not reussite:
                break
            precedent = e
        travail.data["revision"] += 1
        travail.data["journal"].append({"tour": travail.data["revision"], "minutes": travail.data["minutes"],
            "action": self._action_journal(travail, sequence.proposition),
            "origine": sequence.origine, "dd": dernier_dd,
            "jet": dernier_jet, "reussite": reussite, "etapes": trace, "faits": lignes[:]})
        travail.verifier()
        self.monde.data = travail.data
        return "\n".join(lignes) or "Manœuvre accomplie."

    @staticmethod
    def _appliquer(m, effet, lignes):
        op, cible, valeur = effet
        if op == "manger":
            from .corps import SATIETE, valeurs
            o = m.objets[cible]
            o["portions"] -= 1
            v = valeurs(m, "joueur")
            v["faim"] = max(0.0, v["faim"] - SATIETE)
            lignes.append("Tu manges une part " + complement_de(o) + "."
                          + (" Il n'en reste plus." if o["portions"] == 0 else ""))
            return
        if op == "marcher":
            ancienne = m.joueur["salle"]
            m.joueur["salle"], m.joueur["position"] = valeur["salle"], list(valeur["position"])
            m.data["pas_depuis_minute"] = (m.data.get("pas_depuis_minute", 0) + 1) % 10
            if valeur["salle"] not in m.data["visitees"]:
                m.data["visitees"].append(valeur["salle"])
            lignes.append("Tu entres dans : " + m.data["salles"][valeur["salle"]]["nom"] + "."
                          if ancienne != valeur["salle"] else "Tu avances d'un pas.")
            return
        if op in ("recit_improvise", "marque_improvisee", "blessure_improvisee", "son_improvise"):
            from .improvisation import appliquer
            appliquer(m, effet, lignes)
            return
        if op == "blessure_chute":
            m.joueur["pv"] = max(0, m.joueur["pv"] - valeur)
            lignes.append(f"La réception te coûte {valeur} PV.")
            return
        if op == "emettre_son":
            from .sons import appliquer
            appliquer(m, cible, valeur, lignes)
            return
        if op == "blessure_franchissement":
            m.joueur["pv"] = max(0, m.joueur["pv"] - valeur)
            lignes.append(f"Tu retombes au pied de l'obstacle et perds {valeur} PV.")
            return
        if op in ("assembler", "perdre_lien", "installer_assemblage", "retirer_assemblage"):
            from .artisanat import appliquer
            appliquer(m, effet, lignes)
            return
        if op in ("voler", "surprendre_vol"):
            appliquer_vol(m, effet, lignes)
            return
        if op == "remettre":
            payer_remise(m, cible, lignes)
            return
        o = m.objets.get(cible)
        if op == "liberer":
            deplacer(m, cible, valeur)
            lignes.append(designer(o, debut=True) + " est libéré et déposé au sol.")
        elif op == "transferer":
            deplacer(m, cible, valeur)
            lignes.append("Tu portes maintenant " + designer(o) + "." if valeur == "joueur" and o.get("longueur_cm", 0) >= 100 else designer(o, debut=True) + (" rejoint votre besace." if valeur == "joueur" else
                          " est " + accorder(o, "posé") + " au sol." if valeur in m.data["salles"] else
                          " est " + accorder(o, "placé") + " dans " + designer(m.objets[valeur]) + "."))
        elif op == "remarquer":
            from .esprits import memoriser
            memoriser(m, cible, {"type": "geste_remarque", "auteur": "joueur", "objet": valeur})
            lignes.append(o["nom"] + " remarque ton geste vers " + designer(m.objets[valeur]) + ".")
        elif op == "connaitre":
            if cible not in m.data["connus"]:
                m.data["connus"].append(cible)
        elif op == "allumage":
            o["allume"] = valeur
            lignes.append(designer(o, debut=True) + (" s'allume." if valeur else " s'éteint."))
        elif op == "alimentation":
            from .perception import alimenter
            alimenter(m, cible, valeur)
            lignes.append(designer(o, debut=True) + " est " + accorder(o, "rechargé") + " avec "
                          + designer(m.objets[valeur]) + ".")
        elif op == "deplacer":
            deplacer(m, cible, valeur)
            lignes.append(designer(o, debut=True) + (" rejoint votre besace." if valeur == "joueur" else " est " + accorder(o, "posé") + " au sol."))
        elif op == "payer":
            montant, vendeur = valeur["montant"], valeur["vendeur"]
            m.joueur["or"] -= montant
            m.data["finances_pnj"][vendeur] = m.data["finances_pnj"].get(vendeur, 0) + montant
            o["en_vente"] = False
            o["proprietaire"] = "joueur"
            o.pop("vendeur", None)
            lignes.append(f"Vous payez {montant} pièces à {m.objets[vendeur]['nom']}.")
        elif op == "voyager":
            position = valeur if isinstance(valeur, (list, tuple)) else position_entree(m, cible, m.joueur["salle"])
            m.joueur["salle"] = cible
            m.joueur["position"] = list(position)
            if cible not in m.data["visitees"]:
                m.data["visitees"].append(cible)
            lignes.append("Vous entrez dans : " + m.data["salles"][cible]["nom"] + ".")
        elif op == "ouverture":
            o["ouverte"] = valeur
            lignes.append(designer(o, debut=True) + (" s'ouvre." if valeur else " se ferme."))
        elif op == "deverrouiller":
            o["verrouillee"] = False
            lignes.append(designer(o, debut=True) + " est " + accorder(o, "déverrouillé") + ".")
        elif op == "detacher":
            deplacer(m, cible, "joueur")
            lignes.append(designer(o, debut=True) + " est " + accorder(o, "retiré") + " et " + accorder(o, "rangé") + " dans votre besace.")
        elif op == "endommager":
            o["integrite"] = max(0, o["integrite"] - valeur)
            lignes.append(designer(o, debut=True) + " est "
                          + accorder(o, "brisé" if o["integrite"] == 0 else "abîmé") + ".")
        elif op == "gripper":
            o["bloquee"] = True
            lignes.append("La serrure est désormais bloquée.")
        elif op == "caler":
            o["bloque_par"] = valeur
            deplacer(m, valeur, cible)
            m.objets[valeur]["cale_de"] = cible
            lignes.append("La porte reste ouverte, calée par " + designer(m.objets[valeur]) + ".")
        elif op == "decaler":
            cale = m.objets[o["bloque_par"]]
            deplacer(m, cale["id"], valeur)
            cale.pop("cale_de", None)
            o["bloque_par"] = None
            lignes.append(designer(cale, debut=True) + " est " + accorder(cale, "retiré") + " et " + accorder(cale, "posé") + " au sol.")
        elif op == "empreinte":
            materiau = m.objets[valeur]
            materiau["charges"] -= 1
            masse = min(0.05, materiau["masse"])
            materiau["masse"] -= masse
            base = f'empreinte_{m.data["revision"] + 1}'
            id = base
            numero = 2
            while id in m.objets:
                id, numero = f"{base}_{numero}", numero + 1
            copie = objet(id, "empreinte " + complement_de(o), "motif", "joueur",
                          aliases=["empreinte", "copie"], genre="f", mobile=True,
                          materiau=materiau["materiau"], masse=masse, motif=o["motif"],
                          inscription=o.get("inscription", ""), sens=o.get("sens", ""),
                          source=cible)
            m.objets[id] = copie
            lignes.append(designer(copie, debut=True) + " rejoint votre besace. "
                          + designer(materiau, debut=True) + " a été "
                          + accorder(materiau, "consommé") + " en partie.")
        elif op == "dechiffrer":
            m.data["lus"].append(cible)
            lignes.append("Vous comprenez : " + o.get("sens", o["inscription"]))
        elif op == "calmer":
            m.data["bruit"] = max(0, m.data["bruit"] - valeur)
            lignes.append("Cinq minutes passent. Le calme revient peu à peu.")
        else:
            raise ErreurMonde("Effet inconnu : transaction annulée.")

    @staticmethod
    def _stabiliser(m, lignes):
        for porte in (o for o in m.objets.values() if o["type"] == "porte"):
            fixations = [m.objets[id] for id in porte.get("fixations", []) if id in m.objets]
            for fixation in fixations:
                if fixation["integrite"] == 0 and fixation.get("attache"):
                    deplacer(m, fixation["id"], m.joueur["salle"])
            if (porte.get("fixations") and not any(f.get("attache") for f in fixations)
                    and not porte.get("detachee")):
                porte["detachee"] = True
                lignes.append("Sans ses fixations, " + designer(porte) + " bascule hors du cadre. Le passage est libre.")
            if porte["integrite"] == 0 or porte.get("detachee"):
                porte["ouverte"], porte["verrouillee"] = True, False
                if porte.get("bloque_par"):
                    Moteur._appliquer(m, ("decaler", porte["id"], m.joueur["salle"]), lignes)
        for o in list(m.objets.values()):
            if o["type"] == "contenant" and o["integrite"] == 0:
                o["ouverte"], o["verrouillee"] = True, False
                for enfant in m.enfants(o["id"]):
                    deplacer(m, enfant["id"], o["lieu"], position_objet(m, o)
                             if o["lieu"] in m.data["salles"] else None)
                    lignes.append(designer(enfant, debut=True) + " tombe au sol.")
