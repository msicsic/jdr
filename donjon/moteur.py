"""Arbitrage borné et transitions atomiques. Le MJ ne reçoit aucun accès en écriture."""
from __future__ import annotations
from .francais import quantite

import copy
from dataclasses import dataclass, field

from .monde import ErreurMonde, objet
from .francais import accorder, complement_de, designer, sujet, groupe_nominal
from .geometrie import position_entree
from .deplacement_objet import deplacer, SOL_AUX_PIEDS
from .rendu import decrire, decrire_contexte, decrire_perception, regarder, prix, toucher
from .perception import avancer_combustion, eclairage
from .dialogues import verifier_remise, payer_remise
from .vol import proprietaire, appliquer as appliquer_vol
from .capacites_objet import statut as statut_capacite, absence as absence_capacite
from .refus import cibles, inaccessible, portes_avec_usage, ProprieteInconnue


ACTIONS = ["examiner", "toucher", "prendre", "poser", "acheter", "ouvrir", "fermer",
           "deverrouiller", "verrouiller", "crocheter", "frapper", "couper", "detacher", "bloquer", "debloquer",
           "copier", "lire", "parler", "aller", "attendre", "observer", "reperer", "allumer", "eteindre",
           "remettre", "voler", "installer", "franchir", "desinstaller", "marcher", "chasser", "faufiler", "tourner",
           "ecouter", "pousser", "ranimer", "fuir", "riposter", "se_rendre", "degager", "saisir", "ligoter", "delier", "liberer", "trainer", "tuer",
           "clarifier", "impossible"]
TRANCHE = 150      # dixièmes : une attente d'une durée donnée se vit par tranches de 15 s (``_attendre``)
METHODES = ["simple", "finesse", "levier", "percussion", "traction", "assommer"]
# Gestes dont le résultat est ce que le moteur fait percevoir. À distinguer de
# commandes.PERCEPTIONS : cette dernière règle borne l'exécution d'une question.
PERCEPTIONS = ("observer", "examiner", "toucher", "lire", "ecouter", "reperer")


class QualificationRequise(ProprieteInconnue):
    """Une propriété de la cible est inconnue, sans conclure à un échec fictif."""

    def __init__(self, cible, capacite):
        self.cible = cible
        self.capacite = capacite
        super().__init__("Tu ne sais pas encore si cet objet se prête à ce geste.",
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
    dixiemes: int | None = None    # durée à la seconde près ; sinon, ses minutes (temps.duree)
    bruit: int = 0
    effets: list = field(default_factory=list)
    echec_critique: list = field(default_factory=list)
    echec: list = field(default_factory=list)
    risque: str = ""
    information: str = ""
    parole: dict | None = None  # dossier d'une parole préparée, pour la contre-revue de fidélité
    cle_arbitrage: str = ""
    origine: str = "règles"
    etapes: list = field(default_factory=list)
    plans: list = field(default_factory=list)
    regard: str = ""            # le joueur se tourne d'abord vers ce qu'il vise (spatial.orientation_vers)
    effort: bool = True        # le geste creuse et fatigue (``corps``)
    confirmation: bool = False   # la fiche doit précéder toute tentative, même par commande locale
    oppose: str = ""           # jet opposé : le personnage qui oppose la même caractéristique (pousser)
    marge: int | None = None   # au jet : de combien il passe le DD (None : manqué, ou pas encore jeté) ;
    #                            le bruit d'un crochetage en dépend (``ouie.nature_crochetage``)
    compris: str = ""          # texte libre admis : récapitulatif moteur figé avant affichage
    choix_public: object = None  # identité du clic conservée jusqu'à sa confirmation
    etat_consentement: str = ""

    @property
    def perception_canonique(self):
        """Perception seule, sans effet de monde proposé par le MJ.

        Connaître ce qui est perçu est une conséquence du capteur moteur.
        Les compositions et la lecture avec apprentissage gardent leur revue.
        """
        return (self.proposition.get("action") in PERCEPTIONS and not self.etapes
                and not self.stat and not self.confirmation and not self.echec
                and not self.echec_critique
                and all(e[0] == "connaitre" for e in self.effets))

    @property
    def perception(self):
        """Opération de perception préparée, jamais son résultat anticipé."""
        if self.proposition.get("action") in PERCEPTIONS:
            return {"action": self.proposition["action"], "cible": self.proposition.get("cible", "")}
        return None

    @property
    def realise_geste(self):
        """Un plan peut produire une perception seulement lors de son exécution."""
        return bool(self.effets or self.information or self.perception
                    or any(p.realise_geste for p in self.plans))

    def resume(self, monde, afficher_avis=True):
        if self.compris:
            from dataclasses import replace
            return self.compris + "\n" + replace(self, compris="").resume(monde, afficher_avis)
        from .noms import texte
        if self.etapes:
            plusieurs = len(self.plans) > 1
            lignes = [f"Une seule tentative, en {len(self.plans)} étapes successives :" if plusieurs else "Tentative proposée :"]
            lignes.extend((f"\nÉtape {i} — " if plusieurs else "") + p.resume(monde, afficher_avis=False)
                          for i, p in enumerate(self.plans, 1))
            if plusieurs:
                from .temps import dire_duree, duree
                lignes.append(f"Durée totale prévue : {dire_duree(duree(self))}. Arrêt au premier échec ; les étapes déjà réussies restent acquises.")
            lignes.append("« tenter » lance l'ensemble ; « annuler » abandonne sans exécuter aucune étape.")
            return texte(monde, "\n".join(lignes))
        lignes = [self.titre]
        if any(op == "frapper_personne" for op, _, _ in self.effets):
            return texte(monde, "\n".join([self.titre, self.information, self.risque]))
        if self.stat:
            from .caractere import modificateur
            mod = (monde.joueur["stats"][self.stat] - 10) // 2
            corps = modificateur(monde, "joueur", self.stat) - mod
            if self.oppose:
                from .caractere import modificateur
                adverse = f"contre la {self.stat} de {monde.objets[self.oppose]['nom'].split(',')[0]} " \
                          f"({modificateur(monde, self.oppose, self.stat):+d}, un d20 aussi)"
            else:
                adverse = f"difficulté {self.dd}"
            lignes.append(f'Test {self.stat} ({mod:+d}), outil {self.bonus:+d}'
                          + (f', faim, froid ou fatigue {corps:+d}' if corps else '') + f', {adverse}.')
        else:
            lignes.append("Pas de jet nécessaire.")
        if self.information:
            lignes.append(self.information)
        if self.echec_critique:
            lignes.append("Risque sur un 1 naturel : outil endommagé.")
        if self.risque:
            lignes.append(self.risque)
        if self.minutes:
            lignes.append(f'Durée : {self.minutes} min. Bruit : {self.bruit}.')
        return texte(monde, "\n".join(lignes))


def gestes_accomplis(plan, monde):
    """Les gestes que le joueur vient d'entreprendre, en mots du moteur : le titre du plan, ou ceux
    des étapes exécutées d'une manœuvre (elle s'arrête au premier échec). Leurs suites sont dans
    le résultat ; le récit peut raconter ces gestes sans autre fait."""
    if not plan.etapes:
        return [plan.titre] if plan.titre else []
    faites = len(monde.data["journal"][-1].get("etapes", [])) if monde.data["journal"] else 0
    return [p.titre for p in plan.plans[:faites] if p.titre]


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

    def _regard(self, p):
        """La direction vers laquelle le joueur doit se tourner pour voir ce qu'il vise (la cible ou
        l'outil d'un geste, la première étape d'une manœuvre qui vise un objet, après une attente
        par exemple), s'il ne le voit pas de face mais le verrait en se tournant ; None sinon."""
        if not isinstance(p, dict):
            return None
        if p.get("action") in ("trainer", "reperer"):
            # Traîner garde le regard du pas ; consulter un repère garde le
            # regard actuel, même si sa dernière position est derrière Corvus.
            return None
        from .spatial import regard_vers
        etapes = p.get("etapes") if isinstance(p.get("etapes"), list) else []
        cibles = p.get("cibles") if isinstance(p.get("cibles"), list) else []
        premiere = next((e.get("cible") for e in etapes
                         if isinstance(e, dict) and e.get("cible") in self.monde.objets), None)
        vises = [p.get("cible"), p.get("outil"), *cibles, premiere]
        return next((vers for id in vises if isinstance(id, str) for vers in [regard_vers(self.monde, id)] if vers),
                    None)

    def preparer(self, p, origine="règles"):
        from .commandes import DescripteurPublic, proposition_descripteur
        choix_public = p if isinstance(p, DescripteurPublic) else None
        if isinstance(p, DescripteurPublic):
            p = proposition_descripteur(self.monde, p)
        from .noms import texte
        from .tenir import autoriser
        if isinstance(p, dict) and isinstance(p.get("action"), str):
            autoriser(self.monde, "joueur", p["action"])
        try:
            plan = self._preparer_references(p, origine)
        except ErreurMonde as exc:
            # Le refus du moteur passe par la même connaissance que le résultat affiché.
            exc.args = (texte(self.monde, str(exc)),)
            raise
        plan.titre = texte(self.monde, plan.titre)
        plan.information = texte(self.monde, plan.information)
        from .gestes_publics import GESTES_CORPS
        if (p.get("action") in GESTES_CORPS and
                (p["action"] != "frapper" or self.monde.objets.get(p["cible"], {}).get("type") == "personnage")):
            from .consentement import plan_lourd, _empreinte, _etat
            from .comprehension import plan_admis
            # La famille portée partage la gravité U-C et le récapitulatif,
            # y compris pour la commande équivalente. Les règles de geste
            # et les confirmations antérieures restent souveraines.
            plan.confirmation = plan.confirmation or plan_lourd(plan)
            plan.compris = plan_admis(self.monde, plan)
            if choix_public and plan.confirmation:
                plan.choix_public = copy.deepcopy(choix_public)
                plan.etat_consentement = _empreinte(_etat(self.monde))
        return plan

    def _preparer_references(self, p, origine="règles"):
        """Comme ``_preparer`` ; si le joueur doit d'abord se tourner vers ce qu'il vise, le geste est
        jugé tourné vers lui, et la rotation s'ajoute à sa durée."""
        if self.monde.data.get("fin"):
            raise ErreurMonde("Cette partie est terminée.",
                              f"fin.cause={self.monde.data['fin']['cause']}, auteur=joueur : accepté fin=null ; actions acceptées : aucune.")
        from .corps import conscient
        if not conscient(self.monde):
            raise ErreurMonde("Tu es sans connaissance.",
                              "auteur=joueur, conscient=false : accepté conscient=true ; actions acceptées : aucune.")
        from .noms import references
        p = references(self.monde, p)
        vers = self._regard(p)
        if vers is None:
            return self._preparer(p, origine)
        from .spatial import QUART, quarts
        from .temps import duree
        j = self.monde.joueur
        ancien = j["orientation"]
        j["orientation"] = vers
        try:
            plan = self._preparer(p, origine)
        finally:
            j["orientation"] = ancien
        plan.regard = vers
        if not plan.etapes:
            plan.dixiemes = duree(plan) + QUART * quarts(ancien, vers)
        return plan

    def _preparer(self, p, origine="règles"):
        from .operations import preparer as preparer_operations
        if isinstance(p, dict) and p.get("action") == "improviser":
            from .improvisation import preparer
            return preparer(self.monde, p, origine)
        if isinstance(p, dict) and p.get("action") in ("fabriquer", "assembler"):
            from .artisanat import preparer
            return preparer(self.monde, p, origine)
        if isinstance(p, dict) and p.get("action") == "decouper":
            from .artisanat import preparer_decoupe
            return preparer_decoupe(self.monde, p, origine)
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
        if p["methode"] == "assommer" and not (action == "frapper" and m.objets.get(cible, {}).get("type") == "personnage"):
            raise ErreurMonde("Assommer ne vise qu'une personne.",
                              f"methode=assommer, action={action}, cible={cible} : frapper une cible de type personnage, ou methode simple.")
        plan = Plan(dict(p), m.data["revision"], "", origine=origine)
        if action == "reperer":
            for champ, accepte in (("outil", ""), ("methode", "simple"), ("difficulte", 0)):
                if p[champ] != accepte:
                    raise ErreurMonde("Consulter un repère se fait sans outil ni jet.",
                                      f"reperer.{champ} : reçu {p[champ]!r} ; accepté : {accepte!r}.")
            from .rendu import position
            plan.information = position(m, cible)
            plan.titre = "Consulter le repère connu."
            plan.minutes, plan.dixiemes, plan.effort = 0, 0, False
            return plan
        # Après validation de forme et rotation éventuelle : seule la vue
        # publique autorise une conclusion, jamais la position cachée.
        if (action in ("observer", "examiner") and cible in m.objets
                and not m.visible(cible) and not outil
                and p["methode"] == "simple" and not p["difficulte"]):
            from .rendu import non_perception
            information = non_perception(m, cible)
            if information:
                plan.titre = "Constater la vue actuelle."
                plan.minutes, plan.dixiemes, plan.effort = 0, 0, False
                plan.information = information
                return plan
        if action in ("saisir", "ligoter", "delier", "liberer", "trainer", "tuer"):
            from .tenir import preparer
            return preparer(m, p, plan)
        if action in ("fuir", "riposter", "se_rendre", "degager"):
            from .defense import preparer_joueur
            return preparer_joueur(m, p, plan)
        if action == "tourner":
            from .spatial import QUART, VECTEURS, quarts
            if not m.data.get("mode_cases"):
                raise ErreurMonde("Lance cette partie avec --cases pour te tourner vers une direction.",
                                  "partie sans cases : pas d'orientation.")
            if cible not in VECTEURS or outil or p["methode"] != "simple" or p["difficulte"]:
                raise ErreurMonde("Tourne-toi vers une direction : nord, sud, est, ouest, nord-est…",
                                  f"tourner : cible parmi {', '.join(VECTEURS)} (reçu « {cible} »), outil vide, "
                                  "methode simple, difficulte 0.")
            plan.titre = "Te tourner vers " + ("l'" if cible[0] in "eo" else "le ") + cible + "."
            plan.minutes, plan.dixiemes = 0, QUART * quarts(m.joueur.get("orientation"), cible)
            plan.effets = [("orienter", "", cible)]
            return plan
        if action in ("marcher", "chasser", "faufiler") or (action == "aller" and m.data.get("mode_cases")):
            from .spatial import preparer_pas
            if not m.data.get("mode_cases"):
                sorties = ", ".join(m.data["salles"][m.joueur["salle"]]["sorties"]) or "aucune"
                raise ErreurMonde("Lance cette partie avec --cases pour te déplacer case par case.",
                                  f"partie sans cases : utilise aller avec une sortie ({sorties}).")
            if outil or p["methode"] != "simple" or p["difficulte"]:
                raise ErreurMonde("Un pas se fait sans outil ni jet.", "un pas : outil vide, methode simple, difficulte 0.")
            destination = preparer_pas(m, cible)
            from .spatial import QUART, VECTEURS, quarts
            from .temps import PAS_CHASSE, PAS_FEUTRE, PAS_JOUEUR, duree_pas
            regard = m.joueur.get("orientation")
            vers = cible if cible in VECTEURS else None
            # Un pas en diagonale dure √2 fois un pas droit, à toute allure (``temps.duree_pas``).
            vecteur = VECTEURS[vers] if vers else (0, 0)
            if action == "faufiler":
                # À pas feutrés : il se tourne vers où il va, avance lentement, ne s'entend que de près.
                plan.titre = "Avancer à pas feutrés vers " + cible + "."
                duree = QUART * quarts(regard, vers) + duree_pas(PAS_FEUTRE, vecteur)
                destination["feutre"] = True
                if vers:
                    destination["orientation"] = vers
            elif action == "chasser":
                # Un pas chassé garde le regard : de côté ou en arrière, il prend le double.
                plan.titre = "Faire un pas chassé vers " + cible + "."
                duree = duree_pas(PAS_JOUEUR if vers is None or vers == regard else PAS_CHASSE, vecteur)
            else:
                plan.titre = "Avancer d'un pas vers " + cible + "."
                duree = QUART * quarts(regard, vers) + duree_pas(PAS_JOUEUR, vecteur)
                if vers:
                    destination["orientation"] = vers
            if "ecart" in destination:
                # Celui qui se tenait là s'écarte d'abord, le temps de son pas de côté.
                from .passage import duree_ecart
                ecart = destination["ecart"]
                qui = m.objets[ecart["personnage"]]
                plan.titre = plan.titre[:-1] + " ; " + (sujet(qui) if m.visible(qui["id"]) else "quelqu'un") \
                    + " s'écarte pour te laisser passer."
                duree += duree_ecart(m, qui["id"], (ecart["salle"], ecart["position"]))
            plan.minutes, plan.dixiemes = 0, duree
            plan.effets = [("marcher", "", destination)]
            return plan
        if action == "frapper" and m.objets.get(cible, {}).get("type") == "personnage":
            from .combat import preparer
            return preparer(m, p, plan)
        if action == "ranimer":
            if outil:
                raise ErreurMonde("Ranimer se fait à mains nues.", f"outil={outil} : outil vide pour ranimer.")
            from .corps import ranimer
            ranimer(m.copier(), "joueur", cible)
            plan.titre, plan.minutes, plan.dixiemes = "Ranimer " + designer(m.objets[cible]) + ".", 0, 100
            plan.effets = [("ranimer", cible, None)]
            return plan
        if action == "pousser":
            from .passage import preparer_poussee
            return preparer_poussee(m, p, plan)
        if action == "observer":
            if outil:
                raise ErreurMonde("Observer se fait sans outil.", f"observer.outil : reçu {outil!r} ; accepté : ''.")
            if p["methode"] != "simple":
                raise ErreurMonde("Observe simplement ce qui est devant toi.", f"observer.methode : reçu {p['methode']!r} ; accepté : simple.")
            if p["difficulte"]:
                raise ErreurMonde("Observer n'impose pas de difficulté.", f"observer.difficulte : reçu {p['difficulte']!r} ; accepté : 0.")
            if cible in m.objets and m.objets[cible]["type"] == "personnage":
                if not m.visible(cible):
                    from .refus import perception
                    acceptes = [id for id, o in m.objets.items() if o["type"] == "personnage" and m.visible(id)]
                    raise perception(m, cible, "observer.cible", acceptes, ("", "scene", "lumiere", "contexte"))
                plan.titre, plan.minutes, plan.dixiemes, plan.effort = "Observer cette personne.", 0, 30, False
                return plan
            if cible not in ("", "scene", "lumiere", "contexte"):
                raise ErreurMonde("On observe la scène, la lumière ou le contexte, pas un objet précis.",
                                  f"observer.cible : reçu « {cible} » ; acceptés : '', scene, lumiere, contexte ; "
                                  "pour cet objet : examiner, toucher ou lire avec son identifiant.")
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
            if not cible:
                plan.titre, plan.minutes, plan.effort = "Attendre cinq minutes.", 5, False
                plan.effets = [("calmer", "", 3)]
                return plan
            # Une durée donnée, en secondes : l'attente se fait par tranches et cesse dès que
            # quelque chose réclame l'attention du joueur (``_attendre``).
            from .temps import ATTENTE_MAX, MINUTE, dire_duree, lire_duree
            dixiemes = lire_duree(cible)
            if dixiemes is None or outil or p["methode"] != "simple" or p["difficulte"]:
                raise ErreurMonde("Dis combien de temps attendre : « attendre 30 s », « attendre 10 min ».",
                                  f"attendre : cible vide (cinq minutes) ou une durée en secondes, de 0.1 à "
                                  f"{ATTENTE_MAX // 10} (reçu « {cible} ») ; outil vide, methode simple, difficulte 0.")
            plan.titre, plan.effort = "Attendre " + dire_duree(dixiemes) + ".", False
            plan.minutes, plan.dixiemes = dixiemes // MINUTE, dixiemes
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
            from .eau import refuser_entree
            refuser_entree(m, sortie["vers"])
            plan.titre = "Aller vers " + cible + "."
            plan.effets = [("voyager", sortie["vers"], None)]
            return plan
        if action == "remettre":
            from .proximite import exiger
            from .dialogues import remise_convenue, verifier_don
            if remise_convenue(m, cible, outil):
                # Un accord accepté : la remise verse la récompense convenue, une seule fois.
                mission = verifier_remise(m, cible, outil)
                exiger(m, m.data["missions"][mission]["donneur"])
                plan.titre = "Remettre " + designer(m.objets[cible]) + " contre la récompense convenue."
                plan.effets = [("remettre", mission, None)]
                return plan
            destinataire = verifier_don(m, cible, outil)
            exiger(m, destinataire)
            from .voix import nom_pour_joueur
            plan.titre = "Donner " + designer(m.objets[cible]) + " " + groupe_nominal(nom_pour_joueur(m, destinataire, court=False), "à") + "."
            plan.effets = [("donner", cible, destinataire)]
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
                                  f"outil « {outil} » n'est pas un identifiant connu ; objets portés : {cibles(m, portes)}.")
            if t["lieu"] != "joueur":
                portes = sorted(i for i, x in m.objets.items() if x["lieu"] == "joueur")
                raise ErreurMonde("Tu n'as pas " + designer(t) + " en main.",
                                  f"prends d'abord {outil} : composer avec une étape deplacer {outil} vers joueur, puis ce geste."
                                  if m.accessible(outil) else
                                  f"{outil} n'est pas à portée ; objets portés : {cibles(m, portes)}.")
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
                raise ErreurMonde(designer(o, debut=True) + " appartient " + groupe_nominal(designer(m.objets[possesseur]), "à")
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
                                  f"acheter vise un objet en vente, parmi {cibles(m, en_vente)}.")
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
                raise ErreurMonde(f"Il te faudrait {quantite(cout, 'pièce')} ; tu n'en as que {m.joueur['or']}.",
                                  f"prix {cout} > or {m.joueur['or']} : achat impossible ; une négociation passe par "
                                  "le mode parole_joueur.")
            plan.effets.append(("payer", cible, {"vendeur": vendeur_id, "montant": cout}))
            plan.effets.append(("deplacer", cible, "joueur"))
        elif action == "verrouiller":
            from .tenir import valider_verrouillage
            valider_verrouillage(m, "joueur", cible, outil)
            plan.dixiemes, plan.confirmation = 50, True
            plan.effets = [("verrouiller", cible, None)]
            plan.risque = "Enfermer une personne est une contrainte pour les témoins."
        elif action in ("ouvrir", "fermer", "deverrouiller"):
            if o["type"] not in ("porte", "contenant"):
                ouvrables = sorted(i for i, x in m.objets.items()
                                   if x["type"] in ("porte", "contenant") and m.accessible(i))
                raise ErreurMonde(designer(o, debut=True) + " ne s'ouvre ni ne se ferme.",
                                  f"{action} vise une porte ou un contenant, parmi {cibles(m, ouvrables)} ; "
                                  f"{cible} est de type {o['type']}.")
            if action == "deverrouiller" or (action == "ouvrir" and o["verrouillee"] and t):
                cles = sorted(i for i, x in m.objets.items() if x["lieu"] == "joueur" and cible in x.get("ouvre", []))
                from .moyens_materiels import cle_adaptee
                if not cle_adaptee(o, t):
                    raise ErreurMonde(("Il te faut une clé pour cela." if not t else
                                       designer(t, debut=True) + " ne convient pas à cette serrure."),
                                      f"outil : une clé en main qui ouvre {cible}, parmi {cibles(m, cles)}"
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
                if not ouvrir:
                    from .portes import valider_fermeture
                    valider_fermeture(m, cible)
                plan.effets.append(("ouverture", cible, ouvrir))
        elif action == "crocheter":
            parent_id = o["lieu"] if o["type"] == "serrure" else cible
            parent = m.objets.get(parent_id, {})
            if not parent.get("verrouillee"):
                verrous = sorted(i for i, x in m.objets.items() if x.get("verrouillee") and m.accessible(i))
                raise ErreurMonde("Il n'y a rien de verrouillé à crocheter là.",
                                  f"crocheter vise une porte ou un contenant verrouillé (ou sa serrure), parmi {cibles(m, verrous)}.")
            if o.get("bloquee") or any(e.get("bloquee") for e in m.enfants(parent_id)):
                raise ErreurMonde("La serrure est bloquée ; le crochetage ne peut plus fonctionner.",
                                  f"serrure de {parent_id} grippée : il faut sa clé, ou forcer (frapper).")
            from .moyens_materiels import outil_crochetage
            if not outil_crochetage(o, t):
                raise ErreurMonde("Il faut un outil adapté pour crocheter.",
                                  f"outil : un objet en main d'usage crochetage, parmi {cibles(m, portes_avec_usage(m, 'crochetage'))}.")
            from .pnj import seuil_crochetage
            lumiere = eclairage(m)["niveau"]
            # Le seuil commun au joueur et aux PNJ ; la marge du jet fera son bruit (``_terminer_etape``).
            plan.stat, plan.dd, plan.minutes = "DEX", seuil_crochetage(lumiere), 3 + 2 * (2 - lumiere)
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
            from . import force
            usages = set(t.get("usages", [])) if t else set()
            puissance = t.get("puissance", 0) if t else 0
            coupe, choc = force.coupe(o, t), force.choc(t)
            if action == "couper" and not usages & {"couper", "couper_bois"}:
                tranchants = sorted(set(portes_avec_usage(m, "couper")) | set(portes_avec_usage(m, "couper_bois")))
                raise ErreurMonde("Il faut un outil de coupe utilisable.",
                                  f"outil : un objet en main d'usage couper ou couper_bois, parmi {cibles(m, tranchants)}"
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
            from .moyens_materiels import impact_objet
            if action == "frapper" and not (impact_objet(o, t) or not t and o["type"] == "porte"):
                chocs = sorted(set(portes_avec_usage(m, "percussion")) | set(portes_avec_usage(m, "levier")))
                raise ErreurMonde("Il faut un outil adapté à cette cible pour la frapper ou l'entamer.",
                                  f"outil : un objet en main d'usage percussion ou levier, parmi {cibles(m, chocs)}"
                                  + (f" ; {outil} ne convient pas" if outil else " ; outil vide refusé") + ".")
            if action == "couper":
                plan.titre = "Entailler " + designer(o) + " avec " + designer(t) + "."
            # La règle commune au joueur et aux PNJ (``force``).
            plan.stat, plan.dd = "FOR", force.DD
            plan.bonus, plan.bruit = (force.bonus(t) if action == "frapper" else 0), 3
            plan.effets = [("endommager", cible, force.degats(m, "joueur", t))]
            plan.echec_critique = [("endommager", outil, 1)] if outil else []
            if o["type"] == "porte":
                plan.dixiemes = 30
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
                                  f"outil : un objet en main d'usage cale, parmi {cibles(m, portes_avec_usage(m, 'cale'))}.")
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
                                  f"copier vise un objet portant un motif, parmi {cibles(m, motifs)}.")
            parent = m.objets.get(o["lieu"])
            if parent and parent["integrite"] == 0:
                raise ErreurMonde("Le support brisé ne permet plus une empreinte lisible.",
                                  f"{cible} n'est plus copiable.")
            if not t or "empreinte" not in t.get("usages", []) or t.get("charges", 0) < 1:
                raise ErreurMonde("Il faut un matériau à empreinte encore utilisable.",
                                  "outil : un objet en main d'usage empreinte et avec des charges, parmi "
                                  f"{cibles(m, (i for i in portes_avec_usage(m, 'empreinte') if m.objets[i].get('charges', 0) > 0))}.")
            plan.minutes = 2
            plan.effets = [("empreinte", cible, outil)]
        elif action == "lire":
            if not o.get("inscription"):
                lisibles = sorted(i for i, x in m.objets.items() if x.get("inscription") and m.accessible(i))
                raise ErreurMonde(designer(o, debut=True) + " ne porte pas d'inscription lisible.",
                                  f"lire vise un objet portant une inscription, parmi {cibles(m, lisibles)} ; "
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
        if plan.choix_public is not None:
            from .consentement import _empreinte, _etat
            # Ne jamais remplacer l'aperçu consenti, même si la révision n'a
            # pas bougé. La relecture exacte refuse aussi une référence perdue.
            nouveau = self.preparer(plan.choix_public, plan.origine)
            if plan.etat_consentement != _empreinte(_etat(self.monde)) or nouveau != plan:
                raise ErreurMonde("Le monde ou le plan a changé : choisis de nouveau ce geste pour vérifier son aperçu.",
                                  "consentement : état et plan identiques à l'aperçu requis ; reçu : choix public périmé.")
        if plan.revision != self.monde.data["revision"]:
            raise ErreurMonde("Le monde a changé : demandez un nouvel arbitrage.")
        plan = self.preparer(plan.proposition, plan.origine)
        if plan.etapes:
            return self._executer_operations(plan)
        if plan.perception_canonique and plan.dixiemes == 0 and not plan.effets:
            return plan.information
        if plan.proposition["action"] == "observer" and plan.proposition["cible"] not in self.monde.objets:
            return plan.information
        travail = self.monde.copier()
        from .spatial import vue_memorisee
        # La copie de transaction garde les lectures physiques pendant toute
        # l'action, y compris les souvenirs du joueur, le bilan et son rendu.
        # etat_vue invalide à chaque changement physique ; les signes ont leur
        # propre clé sociale. Rien de cette mémoire ne rejoint data ni la copie.
        with vue_memorisee(travail):
            return self._executer_simple(plan, travail)

    def _executer_simple(self, plan, travail):
        from .tenir import lacher
        lacher(travail, "joueur", plan.proposition["action"])
        debut_issues = len(travail.data.get("historique_corps", ()))
        travail.data["entendus"] = []
        lignes = []
        self._ouvrir_bilan(travail)
        if plan.regard:
            travail.joueur["orientation"] = plan.regard
            lignes.append("Tu te tournes vers " + ("l'" if plan.regard[0] in "eo" else "le ") + plan.regard + ".")
        reussite, jet = True, None
        if plan.stat:
            from .caractere import modificateur
            jet = travail.d20()
            mod = (travail.joueur["stats"][plan.stat] - 10) // 2
            corps = modificateur(travail, "joueur", plan.stat) - mod
            total = jet + mod + plan.bonus + corps
            contre = str(plan.dd)
            if plan.oppose:
                # Jet opposé : l'autre lance aussi, avec sa caractéristique modulée ; l'égalité lui reste.
                from .caractere import modificateur
                adverse = travail.d20()
                bonus = modificateur(travail, plan.oppose, plan.stat)
                plan.dd = adverse + bonus
                contre = f"1d20({adverse}) + {plan.stat}({bonus:+d}) = {plan.dd}"
                reussite = jet != 1 and total > plan.dd
            else:
                # Pas de réussite automatique sur 20 : les impossibilités sont rejetées avant le jet.
                reussite = jet != 1 and total >= plan.dd
                plan.marge = total - plan.dd if reussite else None
            lignes.append(f'1d20({jet}) + {plan.stat}({mod:+d}) + outil({plan.bonus:+d}) '
                          + (f'+ corps({corps:+d}) ' if corps else '')
                          + f'= {total} contre {contre} : ' + ("REUSSITE" if reussite else "ECHEC"))
        effets = plan.effets if reussite else plan.echec + (plan.echec_critique if jet == 1 else [])
        for effet in effets:
            resultat = self._appliquer(travail, effet, lignes)
            if effet[0] == "frapper_personne":
                reussite, jet = resultat["touche"], resultat["jet"]
            elif effet[0] == "tenir_personne" and effet[2]["operation"] == "saisir":
                reussite = bool(resultat)
            elif effet[0] in ("fuir", "degager"):
                reussite = bool(resultat)
        if plan.proposition["action"] == "fuir":
            # Chaque pas a déjà fait vivre sa durée sur l'horloge commune.
            plan.dixiemes = 0
        if not reussite and plan.proposition["action"] != "improviser":
            lignes.append("La tentative n'aboutit pas.")
        elif plan.information:
            lignes.append(plan.information)
        if plan.proposition["action"] == "attendre" and plan.proposition["cible"]:
            self._attendre(travail, plan, lignes)
        else:
            self._terminer_etape(travail, plan, lignes, effets, plan.proposition["action"], plan.proposition.get("methode"))
        if plan.proposition["action"] in ("ligoter", "delier", "liberer", "trainer", "tuer"):
            reussite = any(e["type"] == plan.proposition["action"] and e.get("auteur") == "joueur"
                          for e in travail.data.get("historique_corps", ())[debut_issues:])
            if not reussite:
                lignes.append("La tentative n'aboutit pas.")
        if plan.proposition["action"] == "observer":
            from .signes import bilan_signes
            lignes.extend(bilan_signes(travail, plan.proposition["cible"]) or ["Tu ne discernes aucun signe particulier."])
        self._clore_bilan(travail, lignes)
        from .noms import texte
        lignes = [texte(travail, ligne, citations=True) for ligne in lignes]
        travail.data["revision"] += 1
        travail.data["journal"].append({"tour": travail.data["revision"],
            "minutes": travail.data["minutes"], "action": self._action_journal(travail, plan.proposition),
            "origine": plan.origine, "dd": plan.dd, "jet": jet,
            "reussite": reussite, "faits": lignes[:]})
        travail.verifier()
        self.monde.data = travail.data
        return "\n".join(lignes) or "Action accomplie."

    @staticmethod
    def _attendre_reveil(travail, lignes):
        from .corps import conscient, corps, reveiller
        from .temps import instant, ecouler, MINUTE
        from .pnj import avancer, suivre_presences
        from .rendu import regarder
        lignes[:] = ["Tu perds connaissance."]
        while not conscient(travail) and not travail.data.get("fin"):
            reste = corps(travail, "joueur")["inconscient"] - instant(travail)
            if reste <= 0:
                reveiller(travail, "joueur")
                break
            dt = min(MINUTE, reste)
            minutes = ecouler(travail, dt)
            avancer(travail, minutes, [], dt)
        travail.data["entendus"] = []
        suivre_presences(travail)
        if travail.data.get("fin"):
            lignes.append("Ta partie est terminée.")
        else:
            lignes.extend(["Tu reviens à toi.", regarder(travail)])

    @staticmethod
    def _ouvrir_bilan(travail):
        """Pendant une action, les personnages entrent dans le regard du joueur et en sortent pas
        à pas, et leurs signes peuvent changer : on n'en dit que le bilan, à la fin de l'action."""
        from .pnj import suivre_presences
        suivre_presences(travail)

    @staticmethod
    def _clore_bilan(travail, lignes):
        """Qui le joueur voit désormais ou ne voit plus (``pnj.bilan_presences``), puis les signes
        qu'il remarque chez ceux qu'il voit encore (``signes.bilan_signes``)."""
        from .pnj import bilan_presences
        suivi = travail.__dict__.get("_presences") or {}
        lignes.extend(bilan_presences(travail))
        # Qui il a vu pendant l'action, même un instant, il sait qui c'est (``Monde.identifier``).
        travail.identifier(id for id, s in suivi.items() if s["vu"])
        from .signes import bilan_signes
        lignes.extend(l for l in bilan_signes(travail) if l not in lignes)

    @staticmethod
    def _terminer_etape(travail, plan, lignes, effets=(), geste=None, methode=None):
        if travail.joueur.get("parti"):
            lignes.append("Ta partie est terminée.")
            return
        from .corps import conscient
        if not conscient(travail):
            Moteur._attendre_reveil(travail, lignes)
            return
        Moteur._stabiliser(travail, lignes)
        # Le feu se consume minute par minute avec la vie des PNJ (``pnj.avancer``).
        from .temps import MINUTE, duree, ecouler, instant
        debut = instant(travail)
        if geste == "observer" and plan.proposition["cible"] in travail.objets:
            travail.data["observation_joueur"] = {"cible": plan.proposition["cible"], "debut": debut, "fin": debut + duree(plan)}
            from .signes import percevoir_tous as percevoir_signes
            percevoir_signes(travail)
        # Un geste illicite du joueur dure autant que son étape : quiconque le voit faire d'ici
        # là en est témoin, comme d'un geste de PNJ. Ceux qui le regardaient déjà ont été
        # départagés par son jet.
        from .esprits import percoit, pnjs
        from .ouie import nature as nature_de, nature_crochetage
        from .pnj import commencer_geste
        # Ce qu'on en entend tant qu'il dure : le bruit de son geste, feutré s'il le fait en douce ; un
        # crochetage, selon son adresse au jet (règle commune avec les PNJ, ``ouie.nature_crochetage``).
        adresse = geste == "crocheter" and plan.stat
        bruit = (nature_crochetage(plan.marge, methode == "discret") if adresse
                 else nature_de(geste, discret=methode == "discret", bruit=plan.bruit) if geste else None)
        if geste == "passer_obstacle":
            bruit = next((valeur["nature"] for op, _, valeur in plan.effets if op == "passer_obstacle"), bruit)
        gestes = [commencer_geste(travail, "joueur", "prendre", cible, debut + duree(plan),
                                  exclus=[id for id in pnjs(travail) if percoit(travail, id, "joueur")], nature=bruit)
                  for op, cible, _ in effets if op == "voler"]
        # Une bousculade n'a rien de discret : quiconque voit Corvus pendant le geste en est témoin.
        gestes += [commencer_geste(travail, "joueur", "pousser", cible, debut + duree(plan))
                   for op, cible, _ in effets if op == "pousser"]
        # Le bris d'une installation suit le même registre que le geste PNJ,
        # y compris un coup manqué ; le bruit seul n'attribue pas le tort.
        if geste == "frapper":
            from .biens import a_autrui
            from .pnj import est_contrainte
            cible = plan.proposition['cible']
            if (cible in travail.objets and not est_contrainte(travail, geste, cible)
                    and a_autrui(travail, cible, 'joueur', geste) is not None):
                operation = 'briser' if travail.objets[cible]['integrite'] == 0 else geste
                gestes.append(commencer_geste(travail, 'joueur', operation, cible,
                                              debut + duree(plan), nature=bruit))
        # Son geste retentit (``ouie``) : qui l'entend sans le voir l'interprète, se retourne de près.
        # Un appel, un cri, un sifflement, le son d'un objet ont leur nature déclarée (``sons``).
        from .ouie import retentir
        from .sons import nature_emise
        from .appel import METHODES as REPONSES
        heles = [valeur for op, _, valeur in effets if op == "heler"]
        reponses = [(valeur, REPONSES[op]) for op, _, valeur in effets if op in REPONSES]
        # Le cri d'un nom, ou la réponse à un appel, a déjà retenti (``pnj.heler``, ``appel.dire``).
        retournes = [] if heles or reponses or any(op == "frapper_personne" for op, _, _ in effets) else retentir(
            travail, "joueur", geste, discret=methode == "discret", bruit=plan.bruit,
            force=nature_emise(travail, effets) or (bruit if adresse or geste == "passer_obstacle" else None))
        lignes.extend(sujet(travail.objets[id]) + " se retourne vers toi." for id in retournes if travail.visible(id))
        # Le corps du joueur vit le temps de son geste dans l'état où il le fait : l'effort creuse,
        # attendre repose ; entrer dans l'eau trempe aussitôt. Le temps passé dans l'état précédent
        # est soldé s'il change, et chaque minute franchie le solde (``vecu``, ``pnj._avancer``).
        from .corps import CALMES
        from .eau import tremper
        from .vecu import noter
        tremper(travail, "joueur", lignes)
        action = plan.proposition.get("action")
        noter(travail, "joueur", debut, "repos" if action == "attendre"
              else "effort" if plan.effort and action not in CALMES else None)
        minutes = ecouler(travail, duree(plan))
        travail.data["bruit"] = max(0, travail.data["bruit"] + plan.bruit)
        # Les PNJ voient d'abord le résultat du geste du joueur, puis agissent à leur tour. Ce qu'ils
        # en voient date du début du geste, d'où leur vie repart : la minute de fin, plus tardive que
        # leurs gestes de cette période, ferait dépendre leurs croyances du découpage des actions.
        from .esprits import percevoir_tous
        fin = travail.data["minutes"], travail.data.get("dixiemes", 0)
        travail.data["minutes"], travail.data["dixiemes"] = divmod(debut, MINUTE)
        try:
            percevoir_tous(travail)
        finally:
            travail.data["minutes"], travail.data["dixiemes"] = fin
        from .pnj import avancer as avancer_pnj
        apparus = avancer_pnj(travail, minutes, lignes, duree(plan))
        if not conscient(travail):
            Moteur._attendre_reveil(travail, lignes)
            return
        # Qui a saisi son nom répond, le cri fini : après avoir vécu ces secondes (tourné vers la voix,
        # ou parti ailleurs) ; qui a saisi la réponse du joueur y donne suite (``appel``). Le joueur
        # l'entend par l'ouïe commune (``ecoute``).
        from .appel import reagir, repondre
        repondus = [qui for qui in heles if repondre(travail, "joueur", qui, lignes)]
        for qui, sorte in reponses:
            reagir(travail, qui, sorte, lignes)
        # Qui l'a vu faire sous ses yeux à lui : il le sait ; un témoin dans son dos, non.
        for geste in gestes:
            lignes.extend(designer(travail.objets[id], debut=True) + " t'a vu faire."
                          for id in geste["se_sait_vu"])
        # Ce qui parvient à ses oreilles pendant son geste : le fort de lui-même, le bas en écoutant.
        from .ecoute import ECOUTE, ENTENDU, entendus, portes_contre, rendre, retenir
        ecoute = plan.proposition.get("action") == "ecouter"
        parvenus = entendus(travail, debut, ECOUTE if ecoute else ENTENDU)
        retenir(travail, parvenus)
        entendu = rendre(travail, parvenus)
        if ecoute:
            # Le résultat dit la condition que l'ouïe a prise en compte : l'oreille collée à une porte.
            contre = portes_contre(travail)
            lignes.append("Tu tends l'oreille" + (" contre " + " et ".join(designer(travail.objets[p]) for p in contre)
                                                  if contre else "")
                          + (" : rien de particulier ne te parvient." if not entendu else "."))
        lignes.extend(entendu)
        if any(e[0] == "emettre_son" for e in plan.effets) and not apparus:
            lignes.append("Pour l'instant, aucune réponse ne te parvient.")
        if heles and not any(qui in repondus and (travail.visible(qui) or any(b["auteur"] == qui for b, _, _ in parvenus))
                             for qui in heles):
            lignes.append("Aucune réponse ne te parvient.")
        # Les horloges du scénario se sont déclenchées à leur minute, pendant la vie des PNJ.
        percevoir_tous(travail)
        travail.actualiser_souvenirs_personnages()
        from .objectifs import actualiser as actualiser_objectif
        actualiser_objectif(travail, lignes)
        if travail.data.get("mode_cases"):
            from .spatial import memoriser
            memoriser(travail)
        if plan.cle_arbitrage:
            travail.data["arbitrages"][plan.cle_arbitrage] = {
                "dd": plan.dd, "justification": "", "origine": plan.origine}
        return parvenus

    @classmethod
    def _attendre(cls, travail, plan, lignes):
        """Attendre une durée donnée, par tranches de ``TRANCHE`` au plus : le même laps, d'un bloc
        ou découpé, donne le même monde (``temps``). Le joueur cesse d'attendre à la fin de la
        tranche où il a vu, même un instant, quelqu'un qu'il ne voyait pas, ou entendu ce qui
        réclame son attention (``ecoute.eveille`` : un appel, un cri, un fracas, des paroles dont
        il saisit les mots). Le bruit qu'il avait fait retombe à la mesure du temps attendu."""
        from copy import copy
        from .ecoute import eveille
        from .esprits import pnjs
        from .temps import MINUTE, dire_duree, duree
        total, ecoule, entendu = duree(plan), 0, []
        vus = {id for id in pnjs(travail) if travail.visible(id)}
        while ecoule < total:
            tranche = copy(plan)
            tranche.minutes, tranche.dixiemes = 0, min(TRANCHE, total - ecoule)
            # Le bruit retombe avant que les PNJ en jugent, comme d'un bloc : trois crans par cinq minutes.
            calme = 3 * (ecoule + tranche.dixiemes) // (5 * MINUTE) - 3 * ecoule // (5 * MINUTE)
            travail.data["bruit"] = max(0, travail.data["bruit"] - calme)
            recit = []
            parvenus = cls._terminer_etape(travail, tranche, recit, (), "attendre", "simple")
            # Le même bruit d'une tranche à l'autre (des pas qui vont et viennent) se dit une fois.
            entendu.extend(ligne for ligne in recit if ligne not in entendu)
            ecoule += tranche.dixiemes
            # Qui il a vu pendant l'attente, même un instant (``pnj.suivre_presences``), ou voit à présent.
            suivi = travail.__dict__.get("_presences") or {}
            paru = any(s["vu"] and not s["debut"] for s in suivi.values()) or any(
                id not in vus for id in pnjs(travail) if travail.visible(id))
            if paru or any(eveille(b, niveau) for b, niveau, _ in parvenus):
                break
        lignes.append("Tu attends " + dire_duree(ecoule) + "." if ecoule == total else
                      "Au bout de " + dire_duree(ecoule) + ", tu cesses d'attendre.")
        lignes.extend(entendu)

    def _executer_operations(self, sequence):
        from .spatial import vue_memorisee
        travail = self.monde.copier()
        with vue_memorisee(travail):
            return self._executer_sequence(sequence, travail)

    def _executer_sequence(self, sequence, travail):
        from .operations import compiler
        lignes, trace, precedent = [], [], None
        # Une manœuvre est une seule action : un seul bilan de ce qu'on perçoit des autres, à la fin.
        self._ouvrir_bilan(travail)
        if sequence.regard:
            travail.joueur["orientation"] = sequence.regard
            lignes.append("Tu te tournes vers " + ("l'" if sequence.regard[0] in "eo" else "le ") + sequence.regard + ".")
        reussite, dernier_jet, dernier_dd = True, None, 0
        for numero, e in enumerate(sequence.etapes, 1):
            # Revalider sur l'état issu des étapes précédentes, jamais sur les effets du LLM.
            p = compiler(travail, e, precedent, sequence.proposition["justification"], sequence.origine)
            if numero == 1:
                # Ce qu'il a entendu pendant son geste précédent a servi à juger le premier (répondre à
                # qui vient de l'appeler, ``ecoute.appels``) ; la manœuvre retient ce qu'elle entend.
                travail.data["entendus"] = []
            details, jet = [], None
            if p.stat:
                from .caractere import modificateur
                jet = travail.d20()
                mod = (travail.joueur["stats"][p.stat] - 10) // 2
                corps = modificateur(travail, "joueur", p.stat) - mod
                total = jet + mod + p.bonus + corps
                reussite = jet != 1 and total >= p.dd
                p.marge = total - p.dd if reussite else None
                dernier_jet, dernier_dd = jet, p.dd
                details.append(f"1d20({jet}) + {p.stat}({mod:+d}) + outil({p.bonus:+d}) "
                               + (f"+ corps({corps:+d}) " if corps else "")
                               + f"= {total} contre {p.dd} : " + ("REUSSITE" if reussite else "ECHEC"))
            effets = p.effets if reussite else p.echec + (p.echec_critique if jet == 1 else [])
            for effet in effets:
                resultat = self._appliquer(travail, effet, details)
                if effet[0] == "frapper_personne":
                    reussite, jet = resultat["touche"], resultat["jet"]
                    dernier_jet = jet
            from .corps import conscient
            inconscient = not conscient(travail)
            self._terminer_etape(travail, p, details, effets, e["operation"], e["methode"])
            inconscient = inconscient or not conscient(travail) or any("Tu perds connaissance." == ligne for ligne in details)
            if e["operation"] == "patienter":
                details.append("Deux minutes passent à guetter une occasion ; rien ne garantit que le geste passera inaperçu.")
            if not reussite:
                details.append("Tu atteins le sol mais amortis mal la réception. La suite de la manœuvre est abandonnée."
                               if e["operation"] == "sauter" else
                               "La tentative n'aboutit pas. La suite de la manœuvre est abandonnée.")
            trace.append({"numero": numero, "operation": e, "jet": jet, "dd": p.dd, "reussite": reussite,
                          "minutes": p.minutes, "effets_appliques": [list(effet) for effet in effets], "faits": details[:]})
            lignes.extend(details)
            if not reussite or inconscient:
                break
            precedent = e
        self._clore_bilan(travail, lignes)
        from .noms import texte
        lignes = [texte(travail, ligne, citations=True) for ligne in lignes]
        for etape in trace:
            etape["faits"] = [texte(travail, ligne, citations=True) for ligne in etape["faits"]]
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
        from .tenir import autoriser, lacher
        operation = effet[2]["operation"] if effet[0] == "tenir_personne" else effet[0]
        if operation == "marcher":
            autoriser(m, "joueur", operation)
        lacher(m, "joueur", operation)
        from . import agendas
        from . import services
        service_avant = services.preparer(m, 'joueur', effet[1], effet[0])
        avant = agendas.etat_promis(m)
        from .esprits import constats_geste
        with constats_geste(m, "joueur", effet[1], effet[2] if isinstance(effet[2], str) else None):
            resultat = Moteur._appliquer_effet(m, effet, lignes)
        services.constater(m, 'joueur', effet[1], service_avant)
        if avant:
            agendas.constater_geste_joueur(m, avant)
        return resultat

    @staticmethod
    def _appliquer_effet(m, effet, lignes):
        from .deliberation import changer_etat
        op, cible, valeur = effet
        if op == "passer_obstacle":
            from .obstacles import appliquer
            appliquer(m, "joueur", cible, valeur, lignes)
            return
        if op == "manger":
            from .corps import SATIETE, valeurs
            o = m.objets[cible]
            o["portions"] -= 1
            v = valeurs(m, "joueur")
            v["faim"] = max(0.0, v["faim"] - SATIETE)
            lignes.append("Tu manges une part " + complement_de(o) + "."
                          + (" Il n'en reste plus." if o["portions"] == 0 else ""))
            return
        if op == "orienter":
            m.joueur["orientation"] = valeur
            lignes.append("Tu te tournes vers " + ("l'" if valeur[0] in "eo" else "le ") + valeur + ".")
            return
        if op == "pousser":
            from .passage import appliquer_poussee
            appliquer_poussee(m, "joueur", cible, None if valeur is None else (valeur["salle"], tuple(valeur["position"])),
                              lignes)
            return
        if op == "marcher":
            if valeur.get("ecart"):
                # Celui qui se tenait sur la case s'écarte d'abord (``passage.laisser_passer``).
                from .passage import s_ecarter
                ecart = valeur["ecart"]
                s_ecarter(m, ecart["personnage"], (ecart["salle"], tuple(ecart["position"])), "joueur", lignes)
            ancienne = m.joueur["salle"]
            from .presence import franchir
            if franchir(m, "joueur", ancienne, valeur["salle"], lignes):
                return
            m.joueur["salle"], m.joueur["position"] = valeur["salle"], list(valeur["position"])
            if valeur.get("orientation"):
                m.joueur["orientation"] = valeur["orientation"]
            if valeur["salle"] not in m.data["visitees"]:
                m.data["visitees"].append(valeur["salle"])
            lignes.append("Tu entres dans : " + m.data["salles"][valeur["salle"]]["nom"] + "."
                          if ancienne != valeur["salle"] else
                          "Tu avances à pas feutrés." if valeur.get("feutre") else "Tu avances d'un pas.")
            return
        if op in ("recit_improvise", "marque_improvisee", "blessure_improvisee", "son_improvise"):
            from .improvisation import appliquer
            appliquer(m, effet, lignes)
            return
        if op == "tenir_personne":
            from .tenir import commencer
            return commencer(m, "joueur", valeur["operation"], cible, valeur["outil"], lignes,
                             valeur["rotation_dixiemes"])
        if op == "frapper_personne":
            from .combat import frapper
            resultat = frapper(m, "joueur", cible, lignes=lignes, **valeur)
            # La blessure publique ne doit pas dépendre d'un récit.
            if resultat["touche"] and m.visible(cible):
                lignes.append(designer(m.objets[cible], debut=True)
                              + f" perd {resultat['degats']} PV.")
            return resultat
        if op in ("fuir", "se_rendre", "degager"):
            from .defense import appliquer_joueur
            return appliquer_joueur(m, op, cible, valeur, lignes)
        if op == "ranimer":
            from .corps import ranimer
            ranimer(m, "joueur", cible)
            lignes.append("Tu ranimes " + designer(m.objets[cible]) + ".")
            return
        if op == "blessure_chute":
            from .corps import perdre
            perdre(m, "joueur", valeur)
            lignes.append(f"La réception te coûte {valeur} PV.")
            return
        if op == "emettre_son":
            from .sons import appliquer
            appliquer(m, cible, valeur, lignes)
            return
        if op == "heler":
            from .pnj import heler
            heler(m, cible, valeur, lignes)  # Le cri ; la réponse vient le cri fini (``_terminer_etape``).
            return
        from .appel import METHODES as REPONSES
        if op in REPONSES:
            # Sa réponse à qui l'a hélé, ou lui a dit ce qu'il veut : à son nom, il se nomme ;
            # la suite que l'autre y donne vient le cri fini (``_terminer_etape``).
            from .appel import dire, dernier_cri
            dire(m, cible, valeur, REPONSES[op], lignes, nommer=dernier_cri(m, valeur) == "appel")
            return
        if op == "blessure_franchissement":
            from .corps import perdre
            perdre(m, "joueur", valeur)
            lignes.append(f"Tu retombes au pied de l'obstacle et perds {valeur} PV.")
            return
        if op in ("assembler", "decouper", "perdre_lien", "installer_assemblage", "retirer_assemblage"):
            from .artisanat import appliquer
            appliquer(m, effet, lignes)
            return
        if op in ("voler", "surprendre_vol"):
            appliquer_vol(m, effet, lignes)
            return
        if op == "remettre":
            payer_remise(m, cible, lignes)
            return
        if op == "donner":
            # L'objet change de mains ; le personnage s'en souvient. Aucune récompense n'est due.
            from .esprits import memoriser
            from .services import don_utile
            utile = don_utile(m, valeur, cible)
            o = m.objets[cible]
            pret = next((p for p in m.data.get("permissions", []) if p["objet"] == cible and p["a"] == "joueur" and p["de"] == valeur), None)
            ponctuel = bool(pret and m.data["minutes"] - pret["minute"] <= 240)
            deplacer(m, cible, valeur)
            o["proprietaire"] = valeur
            o.pop("vole_par", None)
            memoriser(m, valeur, {"type": "restitution" if pret else "don", "de": "joueur", "objet": cible,
                                "ponctuel": ponctuel, "service_utile": utile})
            from .voix import nom_pour_joueur
            lignes.append("Tu donnes " + designer(o) + " " + groupe_nominal(nom_pour_joueur(m, valeur, court=False), "à") + ".")
            return
        o = m.objets.get(cible)
        if op == "liberer":
            deplacer(m, cible, valeur)
            lignes.append(designer(o, debut=True) + " est libéré et déposé " + SOL_AUX_PIEDS + ".")
        elif op == "transferer":
            deplacer(m, cible, valeur)
            # Porter ne distingue pas la main du sac : le message ne prétend à aucun rangement.
            lignes.append("Tu portes maintenant " + designer(o) + "." if valeur == "joueur" and o.get("longueur_cm", 0) >= 100 else
                          "Tu prends " + designer(o) + "." if valeur == "joueur" else
                          designer(o, debut=True) + (" est " + accorder(o, "posé") + " " + SOL_AUX_PIEDS + "." if valeur in m.data["salles"] else
                          " est " + accorder(o, "placé") + " dans " + designer(m.objets[valeur]) + "."))
        elif op == "remarquer":
            from .esprits import memoriser
            memoriser(m, cible, {"type": "geste_remarque", "auteur": "joueur", "objet": valeur})
            lignes.append(o["nom"] + " remarque ton geste vers " + designer(m.objets[valeur]) + ".")
        elif op == "connaitre":
            if cible not in m.data["connus"]:
                m.data["connus"].append(cible)
        elif op == "allumage":
            avant, o["allume"] = o.get("allume"), valeur
            changer_etat(m, "joueur", cible, "allume", avant)
            lignes.append(designer(o, debut=True) + (" s'allume." if valeur else " s'éteint."))
        elif op == "prelever_piece":
            from .matiere import prelever_piece
            piece = prelever_piece(m, cible, valeur)
            reste = o.get("physique", {}).get("pieces", 1)
            lignes.append("Tu prends " + designer(piece, "indefini") + " ; il en reste " + str(reste) + ".")
        elif op == "alimentation":
            from .perception import alimenter
            alimenter(m, cible, valeur)
            lignes.append(designer(o, debut=True) + " est " + accorder(o, "rechargé") + " avec "
                          + designer(m.objets[valeur]) + ".")
        elif op == "deplacer":
            deplacer(m, cible, valeur)
            lignes.append("Tu prends " + designer(o) + "." if valeur == "joueur" else designer(o, debut=True) + " est " + accorder(o, "posé") + " " + SOL_AUX_PIEDS + ".")
        elif op == "payer":
            montant, vendeur = valeur["montant"], valeur["vendeur"]
            m.joueur["or"] -= montant
            m.data["finances_pnj"][vendeur] = m.data["finances_pnj"].get(vendeur, 0) + montant
            o["en_vente"] = False
            o["proprietaire"] = "joueur"
            o.pop("vendeur", None)
            lignes.append(f"Tu paies {quantite(montant, 'pièce')} à {m.objets[vendeur]['nom']}.")
        elif op == "voyager":
            from .presence import franchir
            if franchir(m, "joueur", m.joueur["salle"], cible, lignes):
                return
            from .eau import refuser_entree
            refuser_entree(m, cible)  # Par une échelle, un saut, un passage : on n'arrive pas sous l'eau.
            position = valeur if isinstance(valeur, (list, tuple)) else position_entree(m, cible, m.joueur["salle"])
            m.joueur["salle"] = cible
            m.joueur["position"] = list(position)
            if cible not in m.data["visitees"]:
                m.data["visitees"].append(cible)
            lignes.append("Tu entres dans : " + m.data["salles"][cible]["nom"] + ".")
        elif op == "ouverture":
            avant, o["ouverte"] = o.get("ouverte"), valeur
            changer_etat(m, "joueur", cible, "ouverte", avant)
            lignes.append(designer(o, debut=True) + (" s'ouvre." if valeur else " se ferme."))
        elif op == "verrouiller":
            from .tenir import enfermer
            from .temps import instant
            enfermer(m, "joueur", cible, instant(m) + 50)
            avant, o["verrouillee"] = o.get("verrouillee"), True
            m.data.setdefault("verrous_joueur", {})[cible] = True
            changer_etat(m, "joueur", cible, "verrouillee", avant)
            lignes.append(designer(o, debut=True) + " est " + accorder(o, "verrouillé") + ".")
        elif op == "deverrouiller":
            avant, o["verrouillee"] = o.get("verrouillee"), False
            m.data.setdefault("verrous_joueur", {})[cible] = False
            changer_etat(m, "joueur", cible, "verrouillee", avant)
            lignes.append(designer(o, debut=True) + " est " + accorder(o, "déverrouillé") + ".")
        elif op == "detacher":
            deplacer(m, cible, "joueur")
            lignes.append("Tu retires " + designer(o) + " et tu l'emportes.")
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
            lignes.append("Tu emportes " + designer(copie) + ". "
                          + designer(materiau, debut=True) + " a été "
                          + accorder(materiau, "consommé") + " en partie.")
        elif op == "dechiffrer":
            m.data["lus"].append(cible)
            lignes.append("Tu comprends : " + o.get("sens", o["inscription"]))
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
        from .force import briser
        for o in list(m.objets.values()):
            if o["type"] == "contenant" and o["integrite"] == 0:
                for enfant in briser(m, o["id"]):
                    lignes.append(designer(m.objets[enfant], debut=True) + " tombe au sol.")
