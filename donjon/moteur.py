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


ACTIONS = ["examiner", "toucher", "prendre", "poser", "acheter", "ouvrir", "fermer",
           "deverrouiller", "crocheter", "frapper", "couper", "detacher", "bloquer", "debloquer",
           "copier", "lire", "parler", "aller", "attendre", "observer", "allumer", "eteindre",
           "remettre", "voler", "installer", "franchir", "desinstaller", "marcher", "clarifier", "impossible"]
METHODES = ["simple", "finesse", "levier", "percussion", "traction"]


class QualificationRequise(ErreurMonde):
    """Une propriété de la cible est inconnue, sans conclure à un échec fictif."""

    def __init__(self, cible, capacite):
        self.cible = cible
        self.capacite = capacite
        super().__init__(f"La capacité {capacite} de {cible} reste à établir.")


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
            mod = (monde.joueur["stats"][self.stat] - 10) // 2
            lignes.append(f'Test {self.stat} ({mod:+d}), outil {self.bonus:+d}, difficulté {self.dd}.')
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
        if not isinstance(p, dict) or set(p) != set(proposition("examiner")):
            raise ErreurMonde("Proposition mal formée : aucune modification.")
        if any(not isinstance(p[k], str) or len(p[k]) > 1000
               for k in ("action", "cible", "outil", "methode", "justification")):
            raise ErreurMonde("Proposition mal formée.")
        if type(p["difficulte"]) is not int or not 0 <= p["difficulte"] <= 25:
            raise ErreurMonde("Difficulté invalide.")
        action, cible, outil = p["action"], p["cible"], p["outil"]
        if action not in ACTIONS or p["methode"] not in METHODES:
            raise ErreurMonde("Cette opération n'est pas prise en charge.")
        if action in ("clarifier", "impossible"):
            raise ErreurMonde("Aucune action exécutable n'a été proposée.")
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
                raise ErreurMonde("Lance cette partie avec --cases pour te déplacer case par case.")
            if outil or p["methode"] != "simple" or p["difficulte"]:
                raise ErreurMonde("Un pas se fait sans outil ni jet.")
            destination = preparer_pas(m, cible)
            plan.titre = "Avancer d'un pas vers " + cible + "."
            plan.minutes = 1 if m.data.get("pas_depuis_minute", 0) == 9 else 0
            plan.effets = [("marcher", "", destination)]
            return plan
        if action == "observer":
            if cible not in ("", "scene", "lumiere", "contexte") or outil:
                raise ErreurMonde("Une observation de la scène ne modifie aucun objet.")
            plan.titre, plan.minutes = "Observer la scène.", 0
            plan.information = (decrire_contexte(m) if cible == "contexte" else
                                regarder(m) if cible == "scene" else decrire_perception(m))
            return plan
        if action == "attendre":
            plan.titre, plan.minutes = "Attendre cinq minutes.", 5
            plan.effets = [("calmer", "", 3)]
            return plan
        if action == "aller":
            sortie = m.data["salles"][m.joueur["salle"]]["sorties"].get(cible)
            if not sortie:
                raise ErreurMonde("Il n'y a pas de sortie dans cette direction.")
            porte = m.objets.get(sortie["porte"])
            if porte and not porte["ouverte"]:
                raise ErreurMonde("La porte fermée vous barre le passage.")
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
            raise ErreurMonde("La cible est absente ou inaccessible depuis ici.")
        if action not in ("examiner", "parler"):
            from .proximite import exiger
            exiger(m, cible)
        if action == "examiner" and not m.visible(cible):
            raise ErreurMonde("Il fait trop noir pour examiner cet objet. Vous pouvez toucher vos affaires ou allumer une lumière.")
        if action in ("lire", "detacher", "copier") and eclairage(m)["niveau"] < 2:
            raise ErreurMonde("La lumière est insuffisante pour cette manœuvre précise.")
        o = m.objets[cible]
        t = None
        if outil:
            t = m.objets.get(outil)
            if not t or t["lieu"] != "joueur" or t["integrite"] == 0:
                raise ErreurMonde("Il faut posséder cet outil en état de servir.")
            if outil == cible:
                raise ErreurMonde("La cible ne peut pas être son propre outil.")
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
                raise ErreurMonde("Cet objet ne peut pas vous répondre.")
            raise ErreurMonde("Pour discuter librement, active le MJ et adresse ta question au personnage. "
                              "Hors ligne : offre <personnage>, negocier <personnage> <montant>, accepter offre, remettre <objet>.")
        elif action == "acheter":
            possesseur = proprietaire(m, o)
            if possesseur not in (None, "joueur") and o.get("vole_par") != "joueur" and not o.get("en_vente"):
                raise ErreurMonde("Cet objet appartient à " + designer(m.objets[possesseur]) + ". Utilise acheter ou tente explicitement de le voler.")
            if not o["mobile"] or o.get("attache") or o.get("cale_de"):
                raise ErreurMonde("Cet objet doit d'abord être détaché ou débloqué.")
            if o["lieu"] == "joueur":
                raise ErreurMonde("Vous possédez déjà cet objet.")
            if m.charge() + o["masse"] > m.joueur["capacite"]:
                raise ErreurMonde("Cet objet dépasse votre capacité de portage.")
            vendeur_id = o.get("vendeur")
            vendeur = m.objets.get(vendeur_id) if vendeur_id else None
            if not o.get("en_vente") or not vendeur or vendeur["type"] != "personnage":
                raise ErreurMonde("Cet objet n'est pas à vendre ici.")
            if not m.present_physique(vendeur_id):
                raise ErreurMonde(designer(vendeur, debut=True) + " doit être présent pour cette vente.")
            from .proximite import exiger
            exiger(m, vendeur_id)
            if (vendeur.get("refuse_ventes_apres_vol")
                    and m.data["relations_pnj"][vendeur_id]["vols_surpris"]):
                raise ErreurMonde(designer(vendeur, debut=True) + " refuse de te vendre quoi que ce soit depuis ta tentative de vol.")
            cout = prix(m, o)
            if cout > m.joueur["or"]:
                raise ErreurMonde("Vous n'avez pas assez de pièces.")
            plan.effets.append(("payer", cible, {"vendeur": vendeur_id, "montant": cout}))
            plan.effets.append(("deplacer", cible, "joueur"))
        elif action in ("ouvrir", "fermer", "deverrouiller"):
            if o["type"] not in ("porte", "contenant"):
                raise ErreurMonde("Cet objet n'a pas d'ouverture modélisée.")
            if action == "deverrouiller" or (action == "ouvrir" and o["verrouillee"] and t):
                if not t or cible not in t.get("ouvre", []):
                    raise ErreurMonde("Cette clé ne convient pas à cette serrure.")
                if not o["verrouillee"]:
                    raise ErreurMonde("Ce n'est pas verrouillé.")
                plan.effets.append(("deverrouiller", cible, None))
            elif action == "ouvrir" and o["verrouillee"]:
                raise ErreurMonde("C'est verrouillé. Il faut une clé adaptée ou une autre manœuvre.")
            if action != "deverrouiller":
                ouvrir = action == "ouvrir"
                if o["ouverte"] == ouvrir:
                    raise ErreurMonde("C'est déjà " + ("ouvert." if ouvrir else "fermé."))
                if not ouvrir and (o["integrite"] == 0 or o.get("detachee") or o.get("bloque_par")):
                    raise ErreurMonde("Impossible de refermer : battant brisé, détaché ou calé.")
                plan.effets.append(("ouverture", cible, ouvrir))
        elif action == "crocheter":
            parent_id = o["lieu"] if o["type"] == "serrure" else cible
            parent = m.objets.get(parent_id, {})
            if not parent.get("verrouillee"):
                raise ErreurMonde("Aucun verrou fermé à crocheter ici.")
            if o.get("bloquee") or any(e.get("bloquee") for e in m.enfants(parent_id)):
                raise ErreurMonde("La serrure est bloquée ; le crochetage ne peut plus fonctionner.")
            if not t or "crochetage" not in t.get("usages", []):
                raise ErreurMonde("Il faut un outil utilisable pour le crochetage.")
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
                raise ErreurMonde("Cette destruction ou ce combat n'est pas simulé dans ce prototype.")
            if o["integrite"] == 0:
                raise ErreurMonde("C'est déjà brisé.")
            usages = set(t.get("usages", [])) if t else set()
            puissance = t.get("puissance", 0) if t else 0
            coupe = bool(usages & {"couper", "couper_bois"}) and (
                puissance >= o["seuil_coupe"] if "seuil_coupe" in o else
                statut_capacite(o, "tranchable", t) == "etablie")
            choc = bool(usages & {"percussion", "levier"})
            if action == "couper" and not usages & {"couper", "couper_bois"}:
                raise ErreurMonde("Il faut un outil de coupe utilisable.")
            if usages & {"couper", "couper_bois"} and (action == "couper" or not choc):
                etat_coupe = statut_capacite(o, "tranchable", t)
                if etat_coupe == "inconnue":
                    raise QualificationRequise(cible, "tranchable")
                if etat_coupe == "ecartee":
                    from .capacites_objet import constat as constat_capacite
                    raise ErreurMonde(absence_capacite(
                        o, "tranchable", constat_capacite(o, "tranchable", t)) + ".")
            if action == "couper" and not coupe:
                raise ErreurMonde("Cet outil ne peut pas entamer " + designer(o) + ".")
            if action == "frapper" and not (coupe or choc):
                raise ErreurMonde("Il faut un outil adapté à cette cible pour la frapper ou l'entamer.")
            if action == "couper":
                plan.titre = "Entailler " + designer(o) + " avec " + designer(t) + "."
            plan.stat, plan.dd = "FOR", 10
            plan.bonus, plan.bruit = (2 if action == "frapper" and "percussion" in usages else 0), 3
            degats = puissance + max(0, (m.joueur["stats"]["FOR"] - 10) // 2)
            plan.effets = [("endommager", cible, degats)]
            plan.echec_critique = [("endommager", outil, 1)]
        elif action == "bloquer":
            if o["type"] != "porte" or not o["ouverte"] or o["detachee"] or o["integrite"] == 0:
                raise ErreurMonde("Il faut une porte ouverte encore montée.")
            if o["bloque_par"]:
                raise ErreurMonde("La porte est déjà calée.")
            if not t or "cale" not in t.get("usages", []):
                raise ErreurMonde("Il faut un objet utilisable comme cale.")
            plan.effets = [("caler", cible, outil)]
        elif action == "debloquer":
            porte_id = o.get("cale_de") or cible
            if not m.objets[porte_id].get("bloque_par"):
                raise ErreurMonde("Cette porte n'est pas calée.")
            plan.effets = [("decaler", porte_id, m.joueur["salle"])]
        elif action == "copier":
            if not o.get("motif"):
                raise ErreurMonde("Il n'y a pas de motif à copier sur cet objet.")
            parent = m.objets.get(o["lieu"])
            if parent and parent["integrite"] == 0:
                raise ErreurMonde("Le support brisé ne permet plus une empreinte lisible.")
            if not t or "empreinte" not in t.get("usages", []) or t.get("charges", 0) < 1:
                raise ErreurMonde("Il faut un matériau à empreinte encore utilisable.")
            plan.minutes = 2
            plan.effets = [("empreinte", cible, outil)]
        elif action == "lire":
            if not o.get("inscription"):
                raise ErreurMonde("Cet objet ne porte pas d'inscription lisible.")
            parent = m.objets.get(o["lieu"])
            if parent and parent["integrite"] == 0:
                raise ErreurMonde("L'inscription a été détruite avec son support.")
            if cible in m.data["lus"]:
                plan.minutes = 0
                plan.information = decrire(m, cible, detail=True)
            else:
                plan.stat, plan.dd, plan.minutes = "INT", 12, 2
                plan.effets = [("dechiffrer", cible, None)]
        else:
            raise ErreurMonde("Action non implémentée.")
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
            jet = travail.d20()
            mod = (travail.joueur["stats"][plan.stat] - 10) // 2
            total = jet + mod + plan.bonus
            # Pas de réussite automatique sur 20 : les impossibilités sont rejetées avant le jet.
            reussite = jet != 1 and total >= plan.dd
            lignes.append(f'1d20({jet}) + {plan.stat}({mod:+d}) + outil({plan.bonus:+d}) '
                          f'= {total} contre {plan.dd} : ' + ("REUSSITE" if reussite else "ECHEC"))
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
        avancer_combustion(travail, plan.minutes, lignes)
        travail.data["minutes"] += plan.minutes
        travail.data["bruit"] = max(0, travail.data["bruit"] + plan.bruit)
        # Les PNJ voient d'abord le résultat du geste du joueur, puis agissent à leur tour.
        from .esprits import percevoir_tous
        percevoir_tous(travail)
        from .pnj import avancer as avancer_pnj
        apparus = avancer_pnj(travail, plan.minutes, lignes)
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
                jet = travail.d20()
                mod = (travail.joueur["stats"][p.stat] - 10) // 2
                total = jet + mod + p.bonus
                reussite = jet != 1 and total >= p.dd
                dernier_jet, dernier_dd = jet, p.dd
                details.append(f"1d20({jet}) + {p.stat}({mod:+d}) + outil({p.bonus:+d}) = {total} contre {p.dd} : " + ("REUSSITE" if reussite else "ECHEC"))
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
