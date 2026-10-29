"""Consentement du libre : préparer sur copie, montrer, revalider, puis publier.

La gravité porte sur le vocabulaire des effets du moteur, jamais sur les mots
du joueur. Une opération nouvelle est lourde par défaut jusqu'à sa classification.
"""
import copy
import hashlib
import json
from dataclasses import dataclass, asdict

from .comprehension import plan_admis, transactions_admises
from .monde import ErreurMonde
from .moteur import Moteur
from .transactions import appliquer


# Effets réversibles usuels, perception et déplacement. Les autres effets
# (paiement, dommage, contrainte, consommation, engagement…) demandent l'accord.
EFFETS_LEGERS = frozenset((
    "orienter", "marcher", "voyager", "connaitre", "remarquer", "calmer",
    "transferer", "deplacer", "ouverture", "deverrouiller", "liberer",
    "allumage", "decaler", "retirer_assemblage", "installer_assemblage",
    "emettre_son", "heler", "repondre", "arriver", "demander_raison",
    "passer_obstacle", "recit_improvise", "son_improvise",
))
CONTENUS_LEGERS = frozenset(("propos", "qui", "ressource", "localisation"))
ADMISSIONS = frozenset(("espace", "complements", "savoirs", "profil_joueur", "faits"))


def effets_lourds(effets):
    """Même décision pour les effets compilés et les actes de parole typés."""
    return any(op not in EFFETS_LEGERS for op, _, _ in effets)


def plan_lourd(plan):
    return (effets_lourds([*plan.effets, *plan.echec, *plan.echec_critique])
            or any(plan_lourd(p) for p in plan.plans))


def transactions_lourdes(transactions):
    effets = []
    for t in transactions:
        p = t["proposition"]
        if t["type"] == "parole":
            effets.extend(("parole:" + c["type"], "", c) for c in p["contenu"]
                          if c["type"] not in CONTENUS_LEGERS)
        elif t["type"] == "conversation_pnj":
            # « proposer » demande au PNJ les termes d'une récompense ;
            # Corvus ne promet rien et doit ensuite accepter séparément.
            if p["operation"] not in ("discuter", "proposer"):
                effets.append(("accord:" + p["operation"], "", p))
        elif t["type"] not in ADMISSIONS:
            effets.append((t["type"], "", p))
    return effets_lourds(effets)


def _etat(monde):
    # Conservateur : tout changement d'état hors historique d'affichage impose
    # un nouvel aperçu. On ne tente pas de deviner les dépendances d'un PNJ.
    return {k: v for k, v in monde.data.items() if k != "conversation"}


def _empreinte(valeur):
    return hashlib.sha256(json.dumps(valeur, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


@dataclass
class PropositionLibre:
    reponse: dict
    origine: str
    travail: object
    rapports: list
    plan: object
    compris: str
    signature: str
    etat_initial: str = ""
    erreur: str = ""
    attendu: str = ""
    avis_narration: str = ""

    def est_actuel(self, monde):
        return self.etat_initial == _empreinte(_etat(monde))

    @property
    def proposition(self):
        return self.plan.proposition if self.plan else None

    @property
    def etapes(self):
        return self.plan.etapes if self.plan else []

    @property
    def confirmation(self):
        return (transactions_lourdes(self.reponse.get("_transactions", []))
                or bool(self.plan and (plan_lourd(self.plan) or self.plan.confirmation
                                      or self.plan.stat or self.plan.echec_critique)))

    def resume(self, monde):
        if self.erreur:
            return self.compris + "\nPlan indisponible : " + self.erreur + "\nAucune action exécutée."
        return self.compris + ("\n" + self.plan.resume(self.travail) if self.plan else "")

    def compte_parle(self):
        """Mots réellement entendus, issus des transactions de cette réponse."""
        from .emissions import entendues
        from .comptes_parles import reponse, sceller
        rapport = {"emissions": [p for r in self.rapports if r for p in entendues(r)]}
        texte = reponse(rapport)
        return sceller(texte, rapport) if texte else None

    def revalider(self, monde):
        try:
            suite = preparer(monde, self.reponse, self.origine, rebaser=True)
            if suite.signature != self.signature or self.reponse.get("_narration_perimee"):
                # Un récit admis dans l'ancien état ne décrit pas le nouvel
                # accord. Restituer les faits publics recalculés, sans modèle.
                from .paroles import annonce
                from .emissions import entendues, reponses
                lignes, prefixes = [], []
                rapport_courant = {"emissions": [p for r in suite.rapports if r
                                                for p in r.get("emissions", [])]}
                for t, rapport in zip(suite.reponse.get("_transactions", []), suite.rapports):
                    if t["type"] == "parole":
                        prefixes.append(annonce(monde, rapport))
                lignes.extend(p.get("rendu_public", p.get("rendu", ""))
                              for p in entendues(rapport_courant))
                suite.reponse.pop("_audit", None)
                suite.reponse.pop("_prefixe_moteur", None)
                suite.reponse.pop("_comptes_parles", None)
                compte = suite.compte_parle()
                suite.reponse.update({k: compte[k] for k in
                    ("texte", "_texte_moteur", "_comptes_parles")} if compte else {
                    "texte": "\n".join(lignes) or "Proposition revalidée par le moteur.",
                    "_texte_moteur": True})
                suite.reponse["_prefixe_moteur"] = "\n".join(prefixes)
                suite.reponse["_narration_perimee"] = True
                if reponses(rapport_courant) and (self.reponse.get("_audit")
                                                  or self.reponse.get("_narration_perimee")):
                    # Une autorisation de réponse n'est pas une parole entendue.
                    # Ne pas publier ses faits en guise de nouvelle réplique.
                    suite.avis_narration = "La réplique libre préparée dans l'ancien état a été écartée."
            return suite
        except ErreurMonde as exc:
            return PropositionLibre(self.reponse, self.origine, None, [], None,
                                    self.compris, "", erreur=str(exc), attendu=exc.attendu)


def preparer(monde, reponse, origine, *, rebaser=False):
    etat_initial = _empreinte(_etat(monde))
    r = copy.deepcopy(reponse)
    transactions = r.get("_transactions", [])
    if rebaser and transactions:
        # La liste conserve son ordre et les écarts de révision internes.
        delta = monde.data["revision"] - transactions[0]["revision"]
        for t in transactions:
            t["revision"] += delta
    travail, rapports = appliquer(monde, transactions)
    compris = transactions_admises(monde, transactions, rapports)
    plan = None
    if r["mode"] == "action":
        plan = Moteur(travail).preparer(r["proposition"], origine)
        compris = "\n".join(filter(None, (compris, plan_admis(travail, plan))))
    signature = _empreinte([etat_initial, asdict(plan) if plan else None, rapports, compris])
    return PropositionLibre(r, origine, travail, rapports, plan, compris, signature, etat_initial)
