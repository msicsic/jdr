"""Planificateur par recherche : le PNJ cherche, sur ce qu'il croit, la suite de gestes la
moins coûteuse qui atteint son but.

Chaque geste est déclaré une fois : ses conditions sur l'état cru, ses effets, son coût. Le
caractère entre dans les coûts : s'en prendre au bien d'autrui est une faute, comptée une fois
par personne lésée, dont le prix vient de ses valeurs (``caractere.prix_faute``) ; à
l'honnêteté entière, le geste est interdit ; demander coûte un peu ; un geste difficile coûte
selon sa chance de réussir. La recherche part de ce que le PNJ croit (jamais de la vérité du
monde) et simule ce que le plan change à mesure : ce qu'il aura pris, ouvert, déverrouillé,
allumé, où il se tiendra.

Le choix du but reste à ``deliberation.candidats`` ; l'exécution, geste par geste revalidé sur
l'état réel, à ``pnj.agir``. Le stratège complète ses gestes par la même recherche.
"""
from . import agendas
from . import relations
import copy
import heapq
import json
import math
from contextlib import contextmanager
from itertools import count
from time import perf_counter
from types import MappingProxyType

from .deliberation import (ATTENTE_PART, CAUSES, REDEMANDE, _connus, appels_vains, apport_cru, _cru, _disponible_cru,
                           _lieu_cru, besoin_de_part, part_pour, gardes, illicite, lumiere_crue, lumiere_devant_crue, moyens_crus, noir_cru,
                           peur_du_noir, profil, promesse_en_cours, refus_retenu, salle_crue, taux, tient)
from . import eau, force
from .biens import PRIX_PART
from .esprits import lire
from .perception import brule, recharge
from .relations import se_fie, se_mefie
from .spatial import porte_par, QUART, VECTEURS, a_verifier
from .obstacles import Route, cout_route, sejours_route, metrique_necessaire, monde_cru
from .geometrie import cases
from .temps import MINUTE
from . import pnj, trajet_estime, route_admissible
from .portes import refermable

PROFONDEUR = 8         # gestes au plus dans un plan (un trajet compte pour un)
NOEUDS = 4000          # états examinés au plus
DEMANDE = 3            # demander : on préfère ce qu'on peut faire seul
CHERCHER = 3           # chercher quelqu'un qu'on a perdu de vue : on n'est pas sûr de le trouver
FLAMME_EN_MAIN = 1     # par minute, tant qu'une flamme allumée par le plan se consume en main
NOIR = 3               # par minute passée dans le noir, fois ce que le noir l'inquiète (``peur_du_noir``)
RESTER = 30            # minutes qu'il compte passer là où le mène un but qui se tient en restant
TACHE = 5              # minutes de travail d'une tâche payée, en plus du chemin (``_engager``)
SALAIRE = 3            # minutes de peine qu'il paie une pièce, à qui fait une tâche pour lui
PALIER = 1.5           # refusé pour un prix trop bas, il offre ce prix et moitié en plus, une hausse à la fois (``hausse``)
HABILE = 0.5           # chance de réussir à partir de laquelle il attend un crochetage discret (``bruit_crochetage``)
# Effets qui achèvent un but sans rien permettre ensuite : un geste qui les produit sans
# atteindre le but cherché ne mène nulle part (se chauffer quand on a faim).
TERMINAUX = ("mange", "part", "chauffe", "inspecte", "servi", "ranime", "parle")
# Ce qui compte sur un tiers ; un devis exclut la délégation du travail.
TIERS = ("demander", "acheter", "engager", "demander_feu", "confier")
# Usages que les gestes savent employer : un objet n'est pris que s'il peut servir à l'un d'eux.
USAGES = ("crochetage", "allumage", "combustible", *force.CHOC, *force.COUPE)
# Chaque recherche s'y consigne quand le banc le demande (``diagnostics``) ; sinon None.
DIAGNOSTIC = None
# Le dernier résultat de chaque PNJ pour chaque but, avec tout ce dont il dépendait. Il ne tient
# pas à l'objet monde : le moteur agit sur une copie de travail à chaque action.
_MEMOIRE = {}
# Le graphe de la dernière recherche de chaque PNJ pour chaque but (``_explorer``), avec tout ce dont
# il dépendait (None : nœuds relâchés après une preuve d'impossibilité) : quand seuls le prix d'une faute
# ou celui d'abîmer ont changé (la détresse qui monte), la recherche se refait sur lui sans
# recalculer un seul geste.
# Dès la première recherche, une petite marque de discrétion est retenue ;
# les nœuds ne le sont qu'à la deuxième rencontre des mêmes entrées.
_GRAPHES = {}
# Une impossibilité prouvée sur tout le graphe jusqu'à la profondeur autorisée ne dépend
# plus des prix. Une seule dernière preuve par PNJ/but ; une preuve bornée n'est jamais reprise.
_IMPOSSIBLES = {}
PREUVE_MAX = 4 * NOEUDS
# Vrai (tests) : un résultat repris de la mémoire ou cherché parmi ce qu'il vaut la peine de
# porter est recalculé par une recherche complète, et comparé.
VERIFIER = False
# Les écarts de plafond reconnus par ``VERIFIER`` : la recherche jouée est bornée et la complète
# trouve mieux ; ou l'ancienne recherche uniforme était bornée, et le nouveau résultat égale la
# complète (``ancienne_borne``). Une limite de recherche, pas de sa restriction ; l'audit les compte.
BORNES = []


@contextmanager
def diagnostics():
    """Consigne chaque recherche faite dans le bloc : qui, pour quel but, nœuds examinés,
    durée, profondeur atteinte, issue (plan, borne de nœuds atteinte, espace épuisé)."""
    global DIAGNOSTIC
    precedent, DIAGNOSTIC = DIAGNOSTIC, []
    try:
        yield DIAGNOSTIC
    finally:
        DIAGNOSTIC = precedent


class Etat(tuple):
    """Où il se tient, ce qu'il porte, et ce que le plan a changé à ce qu'il croit. Deux états sont
    égaux quand le sont salle, possessions, faits et allure (gestes furtifs)."""

    def __new__(cls, salle, portes, faits, case=None, orientation=None, allure=15):
        portes, faits = frozenset(portes), dict(faits)
        case, orientation = None, None
        etat = tuple.__new__(cls, (salle, portes, frozenset(faits.items()), allure))
        etat.salle, etat.portes, etat.faits = salle, portes, faits
        etat.case, etat.orientation = case, orientation
        etat.allure = allure
        return etat

    def __lt__(self, autre):
        return False

    def apres(self, salle=None, portes=None, faits=(), case=..., orientation=..., allure=None):
        case, orientation = None, None
        allure = self.allure if allure is None else allure
        salle = self.salle if salle is None else salle
        portes = self.portes if portes is None else frozenset(portes)
        if faits:
            faits = {**self.faits, **dict(faits)}
            geles = frozenset(faits.items())
        else:
            # Aucun fait nouveau : ceux de cet état, qu'aucun état ne modifie en place.
            faits, geles = self.faits, self[2]
        suivant = tuple.__new__(Etat, (salle, portes, geles, allure))
        suivant.salle, suivant.portes, suivant.faits = salle, portes, faits
        suivant.case, suivant.orientation = case, orientation
        suivant.allure = allure
        return suivant

    def fait(self, *cle):
        return self.faits.get(cle)


def prix_gardes(monde, id, lieux):
    """Prix par minute loin d'un lieu, compté une fois quel que soit le nombre de biens.

    Ambition pour ses biens (ou ce qu'il convoite), loyauté pour une charge
    confiée ou un lieu de devoir. La présence crue qui inquiète le plus renchérit cette garde.
    """
    from .caractere import valeur
    from .deliberation import charges_gardees
    from .esprits import pnjs
    from .vol import proprietaire
    prix = {s: 0 for s in lieux}
    if not prix:
        return prix
    for c in charges_gardees(monde, id):
        if "objet" not in c:
            continue
        o = c["objet"]
        s = salle_crue(monde, id, o)
        if s not in prix:
            continue
        confie = proprietaire(monde, monde.objets[o]) not in (None, id) and not illicite(monde, id, o)
        prix[s] = max(prix[s], 1 + valeur(monde, id, "loyaute" if confie else "ambition") / 50)
    for s in prix:
        if not prix[s]:
            # Un lieu de garde sans bien à lui (une ronde, un protégé : ``deliberation.de_garde``),
            # menacé par un guet qu'il a lu (``signes.intentions_lues``) : une charge, au prix de sa
            # loyauté, jamais gratuite.
            prix[s] = 1 + valeur(monde, id, "loyaute") / 50
        risques = [0]
        for autre in [*pnjs(monde), "joueur"]:
            if autre == id or salle_crue(monde, id, autre) != s:
                continue
            r = relations.axes(monde, id, autre)
            risques.append(max(0, 40 - r["confiance"]) / 100 + r["rancune"] / 100 + r["peur"] / 100)
        prix[s] *= 1 + max(risques)
    return prix


@contextmanager
def vues_du_choix(monde, id):
    """Préparation paresseuse pendant la sélection, avant toute écriture du choix.

    Les méthodes candidates ne font que proposer des plans. Les mises à jour de
    l'intention, des urgences et les gestes restent hors de ce bloc. Le témoin de
    vérification contrôle cette frontière, sans lui-même employer le partage.
    """
    ancien = getattr(monde, "_vues_du_choix", None)
    temoin = copy.deepcopy(monde.data) if VERIFIER else None
    origine = ancien[2] if ancien is not None and ancien[0] == id else lire(monde, id).get("attentes_bornees", {})
    bloc = (id, [None, None], dict(origine))
    monde._vues_du_choix = bloc
    termine = False
    from .agendas import evaluation
    with evaluation(monde, id):
        try:
            yield
            termine = True
        finally:
            monde._vues_du_choix = ancien
            if temoin is not None:
                assert monde.data == temoin, "Une méthode candidate a modifié le monde ou l'esprit"
            # L'effort et les transitions d'agenda appartiennent au choix réel,
            # jamais aux devis ni à une sélection interrompue.
            if termine:
                if ancien is not None and ancien[0] == id:
                    ancien[2].clear()
                    ancien[2].update(bloc[2])
                else:
                    from .esprits import esprit
                    esprit(monde, id)["attentes_bornees"] = bloc[2]


def vue(monde, id):
    """Une vue de recherche privée, préparée une fois par choix pour cet acteur.

    Aucun dictionnaire de calcul ne passe d'une recherche à l'autre : certains
    dépendent du motif, des emplois ou des découvertes de lumière/discrétion.
    La base reste vierge ; seuls ses relevés du monde sont partagés.
    """
    bloc = getattr(monde, "_vues_du_choix", None)
    if bloc is None or bloc[0] != id:
        return Vue(monde, id)
    partage = bloc[1]
    if partage[0] is None:
        partage[0] = Vue(monde, id)
    v = copy.copy(partage[0])
    v.__dict__ = {k: x.copy() if k.startswith("_") and isinstance(x, dict) else x
                  for k, x in v.__dict__.items()}
    v._partage_choix = partage
    return v


class Vue:
    """Ce que le PNJ croit, corrigé de ce que le plan a déjà changé.

    Ses croyances ne bougent pas pendant une recherche : chaque lecture est faite une fois."""

    def __init__(self, monde, id):
        from .caractere import interdit
        from .vol import proprietaire
        self.monde, self.id = monde, id
        self.objets = monde.objets
        from .presence import salles_interieures, interieur
        self.salles = salles_interieures(monde, monde.objets[id]["lieu"])
        self.connus = _connus(monde, id)
        # Toucher au bien d'autrui, hors ce qu'un prêt ou une garde permettent ; le consommer (le
        # manger, en servir une part), que rien ne permet.
        # (``deliberation.illicite`` sans opération, avec « manger », avec « frapper » : ``biens.leses``.)
        from .biens import leses
        confies = {}
        self.illicite, self.consomme_illicite, self.brise_illicite = {}, {}, {}
        self.leses_bris = {}
        for o in self.connus:
            prendre, consommer, abimer = leses(monde, o, id, confies)
            self.illicite[o], self.consomme_illicite[o], self.brise_illicite[o] = (
                prendre is not None, consommer is not None, abimer is not None)
            self.leses_bris[o] = abimer
        # Le prix d'abîmer le bien d'autrui (forcer), au prix de sa douceur (``chercher``) ; None :
        # il ne l'envisage pas.
        self.degat = None
        self.motif = None
        self.desespere = False
        # Une serrure qu'il croit fermée à clé : forcer peut servir, et ce qui force vaut d'être porté.
        self.verrous = any(self.objets[o]["type"] in ("contenant", "porte") and _cru(monde, id, o, "verrouillee")
                           for o in self.connus)
        # ``deliberation.autorise``, d'après ce qui vient d'être jugé illicite.
        honnete = interdit(monde, id, "honnetete")
        self.autorise = {o: not (self.illicite[o] and honnete) for o in self.connus}
        self.proprietaire = {o: proprietaire(monde, monde.objets[o]) for o in self.connus}
        # Ce qu'il peut dépenser, et ce que vaut pour lui une pièce, en minutes (``caractere``).
        from .biens import richesse
        from .caractere import valeur_piece
        self.richesse = richesse(monde, id)
        self.piece = valeur_piece(monde, id) if profil(monde, id) else 0
        self._depenses = {}
        # Ce qu'un geste sait employer (``gestes``) : clé, outil, vivres, combustible, flamme portable.
        self.utile = {o: bool(x.get("ouvre") or set(x.get("usages", [])) & set(USAGES) or x["type"] == "nourriture"
                              or "allume" in x) for o in self.connus for x in [self.objets[o]]}
        # Les sources qu'il connaît et qu'un combustible recharge (``perception.recharge``).
        self.rechargeables = [o for o in self.connus if brule(self.objets[o])]
        self.sources_du_lot = {o: frozenset(s for s in self.rechargeables if recharge(self.objets[s], self.objets[o]))
                               for o in self.connus}
        self.sources_du_lot_triees = {o: tuple(s for s in self.rechargeables if s in sources)
                                      for o, sources in self.sources_du_lot.items()}
        self.combustibles_seuls = frozenset(o for o in self.connus for x in [self.objets[o]]
            if "combustible" in x.get("usages", ())
            and not set(x.get("usages", ())) & (set(USAGES) - {"combustible"})
            and not x.get("ouvre") and "allume" not in x)
        # Ce qui donne du feu de main en main : un outil d'allumage, une source portable.
        self.flammes_portables = [o for o in self.connus if "allumage" in self.objets[o].get("usages", [])
                                  or "allume" in self.objets[o] and self.objets[o].get("mobile")]
        self.foyers = [o for o in self.connus if self.objets[o].get("foyer")]
        # Ce que le noir l'inquiète : chaque minute qu'il y passe lui coûte (``NOIR``), s'il croit
        # le noir quelque part (``noir_cru``) ; sinon, rien ne lui coûte d'y être.
        self.peur = peur_du_noir(monde, id)
        if self.peur and not any(noir_cru(monde, id, s) for s in self.salles):
            self.peur = 0
        # Les lieux gardés et leur prix propre : aucune lecture de l'esprit d'autrui.
        self.gardes = gardes(monde, id)
        self.prix_gardes = prix_gardes(monde, id, self.gardes)
        # L'eau qu'il croit ou attend dans chaque salle (``eau.attendue``) : ce qu'elle lui coûte par
        # minute (``pression``), les salles où un but qui se tient en restant ne se tient pas
        # (``menacees``), celles où il ne descend pas (``descente``).
        self.eau, self.menacees, self.noyees, self.monte = {}, frozenset(), frozenset(), False
        if eau.active(monde):
            self.monte = eau.monte(monde, id)
            attendues = {s: eau.attendue(monde, id, s) for s in self.salles}
            self.menacees = frozenset(s for s, cm in attendues.items() if cm > 0)
            self.noyees = frozenset(s for s, cm in attendues.items() if cm >= eau.NOYEE_CM)
            if "securite" in (profil(monde, id) or {}).get("besoins", {}):
                for s in self.menacees:
                    cm = eau.eau_crue(monde, id, s)
                    # Ce que l'eau l'inquiète par minute là où il s'y tient (``deliberation.ressentir``).
                    self.eau[s] = (2 * taux(monde, id, "eau") * min(cm, eau.NOYEE_CM) / eau.NOYEE_CM if cm
                                   else taux(monde, id, "menace"))
        # Prévision à l'instant présent, puis pente : toutes les traversées
        # utilisent cette même photographie, y compris dans la marche.
        # Garder la droite sous le sol : borner à zéro avant de projeter
        # ferait apparaître artificiellement de l'eau dans les salles hautes.
        self.eau_route = {s: eau.attendue(monde, id, s, projection=True)
                          for s in self.salles} if eau.active(monde) else {}
        self.refus_routes = {}
        self._descentes = {}
        self._chemin, self._parcourir, self._parcours = pnj.chemin, pnj.parcours, {}
        self._passages_crus = any("passage" in c for c in lire(monde, id)["croyances"].values())
        self._metrique = metrique_necessaire(monde, id) if self._passages_crus else False
        self._metriques = {15: self._metrique}
        self._cru_spatial = interieur(monde_cru(monde, id)) if monde.data.get("mode_cases") else None
        self._approches = {}
        self._contextes_routes, self._tarifs_routes, self._effets_routes = {}, {}, {}
        self._mesures_allers = {}
        self._temoin_route = None
        self._contextes_pressions = {}
        self._contacts = {}
        self._locaux = {}
        self._moyennes = {}
        self._routes, self._trajets, self._crus, self._agissables, self._pressions = {}, {}, {}, {}, {}
        self._bornes_rester = {}
        # Le porteur peut n'être connu que par son bien, puis supposé retrouvé
        # par un plan de recherche. Il lui faut aussi l'a priori d'un inconnu.
        interlocuteurs = [x for x, o in self.objets.items() if o["type"] == "personnage" and x != id and o.get("profil")]
        self.chances_demandes = {x: relations.chance_demande(monde, id, x) for x in [*interlocuteurs, "joueur"]}
        # Les axes restent constants pendant cette vue, comme les croyances. Seule la
        # position crue est rejouée dans chaque état du plan.
        self.peurs_sociales = {x: peur / 50 for x in [*self.personnes(), "joueur"]
                              if (peur := relations.axes(monde, id, x)["peur"])}
        from .defense import actifs
        self.dangers = tuple(actifs(monde, id))
        for x in self.dangers:
            # Une violence active vaut la présence crainte maximale (100 / 50),
            # même si les relations n'ont pas encore traduit cette peur.
            self.peurs_sociales[x] = max(2, self.peurs_sociales.get(x, 0))
        self.taux_mefiance = taux(monde, id, "mefiance")
        # Gardes et eau sont figées par salle. Seules lumière et compagnie
        # peuvent rendre la pression dépendante des faits d'un nœud.
        self._pression_fixe = (None if self.peur or self.peurs_sociales else {
            s: 0 + NOIR * self.taux_mefiance * 0
               + sum(prix for g, prix in self.prix_gardes.items() if g != s)
               + NOIR * self.eau.get(s, 0) for s in self.salles})
        self._allers, self._lieux_crus = {}, {}
        self._situations_gestes, self._droits_gestes, self._lots_partageables = {}, {}, {}
        self.salles_triees = sorted(self.salles)
        # La catégorie de ressource comptée ; son emploi pour un besoin dépend de ``part_pour``
        # et une recharge de la source visée (``recharge``).
        self.besoin = {o: besoin_de_part(self.objets[o]) for o in self.connus}
        # Les sources portables qui ne servent qu'à y voir (``capacite``) : ni foyer, ni clé, ni outil
        # (``USAGES``, l'allumage compris), ni vivres, ni part.
        self.sources_seules = frozenset(
            o for o in self.connus for x in [self.objets[o]]
            if "allume" in x and x.get("mobile") and not x.get("foyer") and not x.get("ouvre")
            and not set(x.get("usages", ())) & set(USAGES) and x["type"] != "nourriture" and not self.besoin[o])
        # Les portes de chaque salle : celles qu'il peut crocheter de là.
        self.portes_de = {s: frozenset(x["porte"] for x in d["sorties"].values() if x.get("porte"))
                          for s, d in self.salles.items()}
        self.emplois = None    # ce que le but peut employer (``chercher``) ; None : tout
        # Le but est d'avoir de la lumière (``eclairer``) : lu du but lui-même (``chercher``), pas de ce
        # qu'il vaut la peine de porter, pour que la recherche restreinte et la complète offrent les
        # mêmes gestes propres au but.
        self.eclairer = False
        # Dépendance constatée dans le but ou dans les gestes réellement explorés,
        # par les lectures communes de lumière, jamais d'après une capacité du PNJ.
        self._lumiere_lue = False
        # Découverte par les gardes des gestes offerts, avant le filtre d'allure.
        self._discretion_lue = False
        self._explore_furtif = False
        self.seul = None       # par ses seuls moyens : à qui seul il peut demander (``devis_pulsion``)
        self._estime_part = False
        self._estimations_parts = {}
        self._depart_estimation = None
        self._devis_differes = self._devis_developpes = 0
        self._parts_lues, self._sources_vides, self._attentes_parts = {}, {}, {}
        self._contexte_parts = None
        # Un recours ordinaire épuisé ouvre l'aide sur place ; la garde ne se lève pas.
        from .deliberation import attentes, _lieux_gardes
        intention = lire(monde, id)["intention"]
        en_cours = ([intention["motif"]] if intention and any(
            x["operation"] == "confier" for x in intention["plan"]) else [])
        self.detresses = tuple(sorted(set(attentes(monde, id)) | set(en_cours)))
        self.poste = self.objets[id]["lieu"]
        self.poste_garde = self.poste in self.gardes and self.poste in _lieux_gardes(monde, id, siens=True)
        from .echanges import ENGAGEMENT_MAX
        self.aides = [(x["qui"], x) for x in lire(monde, id)["aides_attendues"].values()
                      if monde.data["minutes"] - x["minute"] <= ENGAGEMENT_MAX
                      and not se_mefie(monde, id, x["qui"])
                      and not refus_retenu(monde, id, x["qui"], ("confier",), x["condition"]["objet"])]

    @property
    def emploie_lumiere(self):
        return bool(self.peur or self.eclairer or self._lumiere_lue)

    def depense(self, prix):
        """Ce que lui coûte de payer ce prix, en minutes (``caractere.valeur_pieces``)."""
        if prix not in self._depenses:
            from .caractere import valeur_pieces
            self._depenses[prix] = valeur_pieces(self.monde, self.id, prix, depense=True)
        return self._depenses[prix]

    def agissables(self, vises):
        """(objets, à porter) : les objets connus sur lesquels un geste est possible (``gestes``)
        — ce qu'un geste sait employer, un contenant, une porte, un foyer, ce que vise le but ; les
        autres ne donnent jamais rien — et, parmi eux, ceux qu'il vaut la peine de porter
        (``pertinent``)."""
        noms = frozenset(o for k in ("prendre", "poser", "fermer", "servir") for o in vises.get(k, ()))
        if noms not in self._agissables:
            objets = [o for o in self.connus if self.utile[o] or o in noms
                      or self.objets[o]["type"] in ("contenant", "porte") or self.objets[o].get("foyer")]
            a_porter = {o for o in objets if self.pertinent(o, noms)}
            # Un objet qu'il ne vaut pas la peine de porter, que le but ne vise pas, et qui n'est ni
            # une serrure, ni un repas, ni une source, ni une part à demander, n'offre aucun geste.
            objets = [o for o in objets if o in a_porter and self.utile[o] or o in noms or self.besoin[o]
                      or self.objets[o]["type"] in ("contenant", "porte", "nourriture") or "allume" in self.objets[o]]
            self._agissables[noms] = objets, a_porter
        return self._agissables[noms]

    def pertinent(self, o, vises):
        """Le porter peut-il servir le but ? Une clé (passages, contenants), un contenant, ce que
        vise le but (``vises`` : leurs noms) ; les vivres si le but peut employer un repas ;
        combustible et flammes s'il peut employer un feu ; outil de crochetage s'il sait
        crocheter ; un outil qui force (choc, coupe) s'il croit une serrure fermée ; de quoi y voir (une source, une flamme pour l'allumer, ce qui la recharge)
        si le but ou un geste exploré emploie la lumière, ou si le noir lui coûte.

        Porter autre chose ne change ni les gestes possibles ni leur coût : le prendre ne fait
        qu'ajouter des minutes, le plan le moins coûteux n'en passe jamais par là, et la
        recherche rend le même résultat sans explorer ces détours."""
        if self.emplois is None:
            return True
        x = self.objets[o]
        usages = x.get("usages", [])
        crochete = "crochetage" in profil(self.monde, self.id)["capacites"]
        voir = self.emploie_lumiere
        return bool(x.get("ouvre") or x["type"] == "contenant" or o in vises
                    or self.verrous and set(usages) & set(force.CHOC + force.COUPE)
                    or "manger" in self.emplois and x["type"] == "nourriture"
                    or "feu" in self.emplois and ("combustible" in usages or "allumage" in usages or "allume" in x)
                    or crochete and "crochetage" in usages
                    or voir and ("allume" in x or "allumage" in usages or "combustible" in usages and any(
                        recharge(self.objets[s], x) for s in self.rechargeables)))

    def situations_gestes(self, e, agissables):
        """Localisation et portée, indépendantes des droits et des effets du but.

        Les chaînes de contenants et de porteurs lisent tous les lieux projetés ;
        seuls l'ouverture d'un contenant et l'état d'un porteur changent la portée.
        L'ordre des objets reste celui d'agissables, y compris les parts lointaines.
        """
        cle = (e.salle, e.portes, tuple(agissables), frozenset(
            (k, x) for k, x in e.faits.items() if k[0] in ("lieu", "ouvert", "assomme")))
        if cle not in self._situations_gestes:
            self._situations_gestes[cle] = self._situations_gestes_calculer(e, agissables)
        return self._situations_gestes[cle]

    def _situations_gestes_calculer(self, e, agissables):
        resultat, objets = [], self.objets
        for o in agissables:
            if o not in e.portes and o not in self.portes_de[e.salle]:
                ailleurs = self.salle(e, o)
                if ailleurs is not None and ailleurs != e.salle:
                    resultat.append((o, True, self.lieu(e, o), False, None))
                    continue
            if o in e.portes:
                ici, dans = True, self.id
            else:
                dans = self.lieu(e, o)
                ici = dans == e.salle or (dans in objets and objets[dans]["type"] == "contenant"
                        and self.salle(e, dans) == e.salle and self.ouvert(e, dans))
            porteur = dans if dans in objets and objets[dans]["type"] == "personnage" and dans != self.id else None
            if porteur and self.salle(e, porteur) == e.salle:
                etat_cru = self.cru(porteur, "etat") or {}
                ici = ici or e.fait("assomme", porteur) or etat_cru.get("conscient") is False
            contenant = dans if dans in objets and objets[dans]["type"] == "contenant" else None
            resultat.append((o, False, dans, ici, contenant))
        return resultat

    def droits_gestes(self, e):
        """Permissions et fautes : mêmes lectures pour tous les nœuds de cette clé."""
        cle = frozenset((k, x) for k, x in e.faits.items()
                        if k[0] in ("permis", "achete", "acquis", "faute"))
        if cle not in self._droits_gestes:
            self._droits_gestes[cle] = self._droits_gestes_calculer(e)
        return self._droits_gestes[cle]

    def _droits_gestes_calculer(self, e):
        resultat, faits = {}, e.faits
        for o in self.connus:
            illicite_ = self.illicite[o] and not faits.get(("permis", o))
            lese = self.proprietaire[o] if illicite_ else None
            mal = int(bool(lese) and not faits.get(("faute", lese, "honnetete")))
            touche = [(("faute", lese, "honnetete"), True)] if lese else []
            conso = self.consomme_illicite[o] and not (faits.get(("achete", o)) or faits.get(("acquis", o)))
            lese_conso = self.proprietaire[o] if conso else None
            mal_conso = int(bool(lese_conso) and not faits.get(("faute", lese_conso, "honnetete")))
            touche_conso = [(("faute", lese_conso, "honnetete"), True)] if lese_conso else []
            resultat[o] = (illicite_, "sans_temoin" if illicite_ else "", mal, touche,
                           "sans_temoin" if conso else "", mal_conso, touche_conso)
        return resultat

    def lot_partageable(self, o):
        """Préconditions fixes communes aux parts servies et remises."""
        if o not in self._lots_partageables:
            donneur = self.proprietaire[o]
            self._lots_partageables[o] = bool(self.besoin[o] and self.disponible(o)
                and donneur not in (None, self.id, "joueur") and self.profil_de(donneur))
        return self._lots_partageables[o]

    def capacite(self, e, o, libre=None):
        """Ce qu'une source portable apporte aux gestes de lumière, tel qu'ils le lisent (``feu``,
        ``flamme``, ``brule``, la faute de la toucher) : (rang, substance, sans faute). Rang 3 : allumée,
        elle éclaire et donne une flamme ; 2 : éteinte et chargée, une flamme l'allume ; 1 : éteinte et
        vide, elle se recharge de ``substance`` puis s'allume ; 0 : rien (son état inconnu, ou vide sans
        se recharger). ``libre`` : l'allumer ou la recharger n'est pas une faute (sinon, lu de l'état)."""
        allume, charge = self.feu(e, o)
        if allume:
            rang, substance = 3, None
        elif allume is False and charge:
            rang, substance = 2, None
        else:
            substance = brule(self.objets[o]) if allume is False else None
            rang = 1 if substance else 0
        if libre is None:
            libre = not (self.illicite[o] and not e.faits.get(("permis", o)))
        return rang, substance, libre

    @staticmethod
    def couvre(a, b):
        """La capacité ``a`` fait-elle tout ce que fait ``b`` ? Allumée, tout ; sinon un rang au moins
        aussi haut (une source vide, de la même substance), et sans faute si ``b`` l'est."""
        if a[0] == 3 or b[0] == 0:
            return True
        return (a[2] or not b[2]) and (a[0] > b[0] or a[0] == b[0] and (a[0] == 2 or a[1] == b[1]))

    def capacites_portees(self, e):
        """Les capacités des sources qui ne servent qu'à y voir qu'il porte dans cet état, sauf celles
        auxquelles il ne touche pas (``contrarie``). Lues une fois par état."""
        cle = ("capacites", e)
        if cle not in self._crus:
            self._crus[cle] = tuple({self.capacite(e, k) for k in e.portes
                                     if k in self.sources_seules and not self.contrarie(k)})
        return self._crus[cle]

    def doublon(self, e, o, noms_vises, entretenus=()):
        """Une source de plus qui n'apporte aucune capacité absente de celles qu'il porte : aucun geste
        ne l'acquiert (prendre, demander, acheter, la saisir sur un porteur, la faire remettre), sauf si
        le but la vise. Sa capacité est jugée au mieux : acquise par une demande, il s'en sert sans faute.

        Elle ne change aucun geste de lumière possible ni son coût : tout plan qui l'emploie a son
        pareil avec la source portée, sans le détour de l'acquérir ; la recherche rend le même résultat
        sans explorer ces inventaires (« on ne porte que ce qui peut servir le but »)."""
        if o not in self.sources_seules or o in e.portes or o in noms_vises or o in entretenus:
            return False
        portees = self.capacites_portees(e)
        if not portees:
            return False
        b = self.capacite(e, o, libre=True)
        return any(self.couvre(a, b) for a in portees)

    def embuscade_possible(self, e, cible):
        """Le plan ne peut supposer que les témoins crus disparaîtront entre ses gestes.

        Le désespoir permet d'assumer ce risque ; sinon on reconsidérera quand la perception
        changera. L'approche réelle refait encore ce contrôle sur place, vue et ouïe.
        """
        if self.desespere:
            return True
        return self._memo(("embuscade", e.salle, cible), lambda: not any(
            x not in (self.id, cible) and (x == "joueur" or self.objets.get(x, {}).get("type") == "personnage")
            and d.get("lieu", {}).get("valeur") == e.salle
            and d.get("etat", {}).get("valeur", {}).get("conscient") is not False
            for x, d in lire(self.monde, self.id)["croyances"].items()))

    def moyen_du_but(self, o, vises):
        """Ce qui vaut d'aller chercher qui le porte : ce que le but vise lui-même, ou, pour avoir de
        la lumière, une source ou une flamme. Pas ce qui ne servirait qu'en chemin (une lampe pour
        qui craint le noir, une clé), ni les moyens d'un feu ou d'un repas : leur part se cherche
        déjà chez son propriétaire (``_chercher``), et chercher quiconque porte un combustible ou
        une flamme élargit chaque recherche d'un feu sans la servir (voir les limites)."""
        if o in vises:
            return True
        x = self.objets[o]
        return bool(self.eclairer and ("allume" in x or "allumage" in x.get("usages", [])))

    def _memo(self, cle, calcul):
        crus = self._crus
        if cle not in crus:
            crus[cle] = calcul()
        return crus[cle]

    def se_mefie(self, autre):
        """Il se méfie d'``autre`` (``relations``) ; ce qu'il en éprouve entre dans ``_entrees``."""
        return self._memo((autre, "se_mefie"), lambda: se_mefie(self.monde, self.id, autre))

    def se_fie(self, autre):
        return self._memo((autre, "se_fie"), lambda: se_fie(self.monde, self.id, autre))

    def cru(self, sujet, attribut):
        cle = (sujet, attribut)
        crus = self._crus
        if cle not in crus:
            crus[cle] = _cru(self.monde, self.id, sujet, attribut)
        return crus[cle]

    def disponible(self, o):
        cle = (o, "disponible")
        crus = self._crus
        if cle not in crus:
            crus[cle] = _disponible_cru(self.monde, self.id, o)
        return crus[cle]

    def refus_tenus(self):
        """[(refus, s'il tient)] : la dernière réponse refusée de chaque demande
        (``deliberation.retenir_refus``), jugée une fois (``deliberation.tient``)."""
        def juger():
            # Les refus d'une même demande faite à plusieurs (une tâche, une part) ont les mêmes moyens :
            # ils ne se lisent qu'une fois.
            moyens = {}
            tenus = []
            for s in lire(self.monde, self.id).get("refus", ()):
                if s["raison"] in CAUSES and "cause" in s:
                    cle = (s["operation"], s.get("objet"), s.get("besoin"), s.get("tache"), s.get("flamme"),
                           s["de"] if s["operation"] == "enqueter" else None)
                    if cle not in moyens:
                        moyens[cle] = {tuple(f) for f in moyens_crus(self.monde, self.id, s, self.connus)}
                    tenus.append((s, moyens[cle] <= {tuple(f) for f in s["cause"]}))
                else:
                    tenus.append((s, tient(self.monde, self.id, s, self.connus)))
            return tenus
        return self._memo(("refus_tenus",), juger)

    def retenu(self, autre, operations, o):
        """Le refus d'``autre`` qui tient encore pour cette demande (``deliberation.refus_retenu``)."""
        def chercher_refus():
            refus = [(s, tenu) for s, tenu in self.refus_tenus() if s["de"] == autre and s["operation"] in operations
                     and s.get("objet", o) == o and s.get("besoin") is None]
            dernier = max(refus, key=lambda x: x[0]["minute"], default=None)
            return dernier[0] if dernier is not None and dernier[1] else None
        return self._memo((autre, o, operations, "retenu"), chercher_refus)

    def refuse(self, autre, o):
        """Il ne le lui redemande pas : un refus qui tient, demandé ou à vendre ; sauf faute d'argent
        pour l'acheter, ce qui n'empêche pas de le demander."""
        from .biens import restitution_retenue
        if restitution_retenue(self.monde, self.id, autre, o):
            return True
        refus = self.retenu(autre, ("demander", "acheter"), o)
        return refus if refus and refus["raison"] != "pauvre" else None

    def contrarie(self, o):
        """Quelqu'un s'oppose à lui sur cette chose et l'opposition tient (``deliberation.changer_etat``) :
        il n'y touche pas."""
        return self._memo((o, "contrarie"), lambda: any(
            s["operation"] == "defaire" and s.get("objet") == o and tenu for s, tenu in self.refus_tenus()))

    def refuse_tache(self, autre, o):
        """Un refus qui tient de faire pour lui une tâche sur ``o`` (``echanges.engager``) ; « cher »
        ne tient que pour son prix."""
        return self.retenu(autre, ("engager",), o)

    def hausse_faite(self, o):
        """Une offre de tâche sur ``o`` refusée à cette minute pour un prix trop bas : il ne hausse qu'une
        fois par délibération à la minute, pas d'un refus à l'autre en rafale (``_engager``)."""
        minute = self.monde.data["minutes"]
        return self._memo((o, "hausse_faite"), lambda: any(
            s["operation"] == "engager" and s.get("objet") == o and s["raison"] == "cher" and s["minute"] == minute
            for s, _ in self.refus_tenus()))

    def personnes(self):
        """Les PNJ qu'il connaît, dans un ordre stable."""
        return self._memo(("personnes",), lambda: [x for x in self.connus if self.objets[x]["type"] == "personnage"
                                                    and x != self.id and profil(self.monde, x)])

    def refuse_achat(self, autre, o):
        """Un refus qui tient, de lui vendre ou de donner, pour une raison que payer ne lève pas : il le
        garde, ne peut pas, ou se méfie de lui. Payer lève un refus d'humeur ; un achat refusé faute
        d'argent dépend de ce qu'il a (``richesse``)."""
        refus = self.retenu(autre, ("acheter", "demander"), o)
        return bool(refus and refus["raison"] not in ("refus", "pauvre"))

    def promesse(self, o, remise=None):
        cle = (o, "promesse", remise)
        crus = self._crus
        if cle not in crus:
            crus[cle] = promesse_en_cours(self.monde, self.id, o, remise)
        return crus[cle]

    def sur_soi(self, besoin, portes):
        """Porte-t-il de quoi apaiser ce besoin (une part qu'il n'a pas à demander) ?"""
        cle = (besoin, portes)
        crus = self._crus
        if cle not in crus:
            crus[cle] = any(part_pour(self.monde, self.id, k, besoin, self.connus) and self.disponible(k)
                           for k in portes)
        return crus[cle]

    def profil_de(self, x):
        """``deliberation.profil`` de ``x``, lu une fois."""
        cle = (x, "profil")
        crus = self._crus
        if cle not in crus:
            crus[cle] = profil(self.monde, x)
        return crus[cle]

    def allers(self, e, ouvertes):
        """[(salle, minutes du trajet)] : chaque autre salle qu'il croit atteindre depuis celle de
        ``e``, avec ce qu'il porte et les portes que le plan a déverrouillées (``route``)."""
        cle = (self.contexte_route(e), ouvertes)
        if cle not in self._allers:
            allers = []
            for s in self.salles_triees:
                if s != e.salle:
                    route = self.route(e, s, ouvertes)
                    if route is not None:
                        allers.append((s, cout_route(route, e.orientation)))
            self._allers[cle] = allers
        return self._allers[cle]

    def route(self, e, arrivee, ouvertes=None):
        """Les sorties de sa salle jusqu'à ``arrivee``, avec les clés qu'il porte et les portes que
        le plan a déverrouillées (crochetées, ``ouvertes`` si on les a déjà) ; None s'il n'y croit
        aucun passage."""
        if self._cru_spatial is None:
            route = self._chemin(self.monde, self.id, e.salle, arrivee, e.portes,
                                 self.ouvertes(e) if ouvertes is None else ouvertes, metrique=False)
            return route if route is not None and not route_admissible.refus(self, e, route, arrivee) else None
        ouvertes = self.ouvertes(e) if ouvertes is None else ouvertes
        cle = (self.contexte_route(e), ouvertes)
        if cle not in self._parcours:
            self._parcours[cle] = trajet_estime.parcours(self, e, ouvertes)
        admissible = (cle, arrivee)
        if admissible in self._routes:
            route, raison = self._routes[admissible]
            if raison:
                self.refus_routes[arrivee] = raison
            return route
        route = self._parcours[cle].get(arrivee)
        raison = None
        if route is not None:
            raison = route_admissible.refus(self, e, route, arrivee)
            if raison:
                self.refus_routes[arrivee] = raison
                route = None
        self._routes[admissible] = route, raison
        return route

    def contexte_route(self, e):
        """Géométrie et admissibilité : ni droits, ni effets terminaux du plan.

        Les possessions entières ne servent qu'aux franchissements métriques ;
        sinon seules les clés changent les parcours et les retours devant l'eau.
        """
        cle = (e.portes, e[2], e.allure)
        if cle not in self._contextes_routes:
            equipement = e.portes if self.metrique(e.allure) else frozenset(
                k for k in e.portes if self.objets[k].get("ouvre"))
            self._contextes_routes[cle] = (equipement, e.allure, self.portes_prevues(e))
        return (e.salle, self._contextes_routes[cle])

    def metrique(self, allure):
        if allure not in self._metriques:
            self._metriques[allure] = metrique_necessaire(self.monde, self.id, allure) if self._passages_crus else False
        return self._metriques[allure]

    def portes_prevues(self, e):
        return tuple(sorted((k, x) for k, x in e.faits.items() if k[0] in ("ouvert", "verrou")
                            and self.objets[k[1]]["type"] == "porte"))

    def arrivee(self, e, salle, route):
        """L'arrivée change la salle et enregistre les portes franchies."""
        if not isinstance(route, Route):
            return e.apres(salle=salle)
        orientation = next((k for k, v in VECTEURS.items() if route.chemin and v == route.chemin[-1][3]), e.orientation)
        if not route.portes:
            return e.apres(salle=salle, case=route.fin[1], orientation=orientation)
        cle = (id(route), self.contexte_route(e))
        if cle not in self._effets_routes:
            self._effets_routes[cle] = route, tuple((cle, valeur)
                for p in sorted(route.portes) if not self.ouvert(e, p) or self.verrouille(e, p)
                for cle, valeur in ((("ouvert", p), True), (("verrou", p), False)))
        faits = self._effets_routes[cle][1]
        return e.apres(salle=salle, case=route.fin[1], orientation=orientation, faits=faits)

    def prix_route(self, e, route):
        """Pression intégrée dans chaque salle parcourue, avant les effets du geste."""
        if not isinstance(route, Route):
            return cout_route(route) * self.pression(e)
        cle = (id(route), e.orientation, self.contexte_pression(e))
        if cle not in self._tarifs_routes:
            self._tarifs_routes[cle] = route, sum(d / MINUTE * self.pression(e.apres(salle=s))
                                                for s, d in sejours_route(route, e.orientation) if d)
        return self._tarifs_routes[cle][1]

    def mesure_aller(self, e, salle):
        """Durée, pression et effets de portes d'une arête entre salles.

        Les effets restent des écritures à composer avec le nœud destinataire,
        jamais un état complet repris d'un autre plan.
        """
        cle = (self.contexte_route(e), self.contexte_pression(e), salle)
        if cle not in self._mesures_allers:
            route = self.route(e, salle)
            if route is None:
                mesure = None
            else:
                arrivee = self.arrivee(e, salle, route)
                mesure = (cout_route(route, e.orientation), self.prix_route(e, route),
                          tuple((k, x) for k, x in arrivee.faits.items() if k[0] in ("ouvert", "verrou")
                                and self.objets[k[1]]["type"] == "porte"))
            self._mesures_allers[cle] = mesure
        elif self._mesures_allers[cle] is None:
            self.route(e, salle)  # restituer aussi la cause destinée au récit
        if a_verifier():
            # Un seul état complet à la fois, sans la projection contrôlée :
            # ses destinations consécutives partagent ce recalcul indépendant.
            # Une dépendance omise de contexte_route reste donc détectable.
            temoin = (e, e.case, e.orientation)
            if self._temoin_route is None or self._temoin_route[0] != temoin:
                self._temoin_route = temoin, trajet_estime.parcours(self, e, self.ouvertes(e))
            route = self._temoin_route[1].get(salle)
            if route is not None and route_admissible.refus(self, e, route, salle):
                route = None
            direct = None
            if route is not None:
                arrivee = self.arrivee(e, salle, route)
                direct = (sum(d for _, d in sejours_route(route, e.orientation)) / MINUTE,
                          sum(d / MINUTE * self.pression(e.apres(salle=s))
                              for s, d in sejours_route(route, e.orientation) if d),
                          tuple((k, x) for k, x in arrivee.faits.items() if k[0] in ("ouvert", "verrou")
                                and self.objets[k[1]]["type"] == "porte"))
            garde = self._mesures_allers[cle]
            assert ((garde is None and direct is None)
                    or garde is not None and direct is not None and garde[:2] == direct[:2]
                    and dict(garde[2]) == dict(direct[2])), "Table des trajets périmée"
        return self._mesures_allers[cle]

    def contexte_pression(self, e):
        if self._pression_fixe is not None:
            return None
        cle = (e.portes, e[2])
        if cle not in self._contextes_pressions:
            self._contextes_pressions[cle] = (e.portes, frozenset(
                (k, x) for k, x in e.faits.items() if k[0] in ("allume", "lieu")))
        return self._contextes_pressions[cle]

    def case_objet(self, e, objet, vus=()):
        """Position prévue, sinon crue ; le contenant ou le porteur donne sa case."""
        if objet in e.portes or objet == self.id:
            return e.case
        if objet in vus:
            return None
        if ("case_objet", objet) in e.faits:
            return e.fait("case_objet", objet)
        lieu = self.lieu(e, objet)
        if lieu in self.objets or lieu == "joueur":
            return self.case_objet(e, lieu, (*vus, objet))
        cru = lire(self.monde, self.id)["croyances"].get(objet, {}).get("lieu", {})
        if cru.get("salle") == e.salle and cru.get("case") is not None:
            return tuple(cru["case"])
        o = self.objets.get(objet, {})
        if o and not o.get("mobile") and o.get("type") != "personnage":
            from .spatial import position_cible
            return position_cible(self.monde, objet, e.salle)
        return None

    def approche(self, e, etape, cibles=None):
        """Approche moyenne depuis les entrées, sans position projetée."""
        if self._cru_spatial is None:
            return Route(fin=(e.salle, None))
        return trajet_estime.approche(self, e, etape, cibles)

    def present(self, e, cible):
        """La présence commune d'exécution, sur les lieux et ouvertures projetés.

        Une coordonnée d'approche ne prouve pas que la cible est matériellement
        dans la salle. Les contenants et porteurs sont lus sur la même projection,
        sans apprendre leurs positions réelles ni modifier le monde.
        """
        from collections import ChainMap
        if cible == "joueur":
            return self.salle(e, cible) == e.salle
        projetes, x = {}, cible
        while x in self.objets and x not in projetes:
            o = self.objets[x]
            lieu = e.salle if x == self.id else self.lieu(e, x)
            projetes[x] = {**o, "lieu": lieu, "ouverte": self.ouvert(e, x)}
            x = lieu
        m = copy.copy(self.monde)
        m.data = {**self.monde.data, "objets": ChainMap(projetes, self.objets), "joueur": {
            **self.monde.joueur, "salle": self.salle(e, "joueur")}}
        return m.present_physique(cible, salle=e.salle)

    def contacts(self, salle, cibles, centre=False):
        """Cases qui touchent les mêmes cibles ; leur ordre reste celui des tables."""
        cle = (salle, cibles, centre)

        def calculer():
            return frozenset(c for c in cases(self._cru_spatial.data["salles"][salle])
                             if (c == cibles[0] if centre else
                                 all(pnj._a_portee_de(self._cru_spatial, salle, c, cible) for cible in cibles)))

        if cle not in self._contacts:
            self._contacts[cle] = calculer()
        elif a_verifier():
            assert self._contacts[cle] == calculer(), "Cases de contact crues périmées"
        return self._contacts[cle]

    def ouvertes(self, e):
        """Les portes que le plan a déverrouillées."""
        return frozenset(cle[1] for cle, valeur in e.faits.items()
                         if cle[0] == "verrou" and valeur is False and self.objets[cle[1]]["type"] == "porte")

    def lieu(self, e, o):
        if o in e.portes:
            return self.id
        return self._lieu(e, o)

    def _lieu(self, e, o):
        """``lieu`` d'un objet qu'il ne porte pas : ce que le plan en a fait, sinon ce qu'il en croit
        (``_lieu_cru``, lu une fois)."""
        lieu = e.faits.get(("lieu", o)) if e.faits else None
        if lieu is not None:
            return lieu
        crus = self._lieux_crus
        if o not in crus:
            crus[o] = _lieu_cru(self.monde, self.id, o)
        return crus[o]

    def salle(self, e, sujet, profondeur=0):
        if sujet in e.portes or sujet == self.id:
            return e.salle
        lieu = self._lieu(e, sujet)
        if lieu is None or profondeur > 4:
            return None
        if lieu in self.salles:
            return lieu
        if lieu == "joueur":
            crus = self._lieux_crus
            if "joueur" not in crus:
                crus["joueur"] = _lieu_cru(self.monde, self.id, "joueur")
            return crus["joueur"]
        return self.salle(e, lieu, profondeur + 1)

    def ouvert(self, e, c):
        v = e.faits.get(("ouvert", c))
        if v is not None:
            return v
        etat = self.cru(c, "etat")
        return bool(etat and etat.get("ouverte"))

    def verrouille(self, e, c):
        v = e.faits.get(("verrou", c))
        return v if v is not None else bool(self.cru(c, "verrouillee"))

    def feu(self, e, f):
        """(allumé, chargé) tels qu'il les croit ; inconnus : None."""
        etat = self.cru(f, "etat") or {}
        allume, charge = e.faits.get(("allume", f)), e.faits.get(("charge", f))
        return (etat.get("allume") if allume is None else allume,
                (etat.get("charge") and not etat.get("faible")) if charge is None else charge)

    def a_portee(self, e, o):
        """Dans sa main, ou dans sa salle hors de tout contenant fermé."""
        if o in e.portes:
            return True
        lieu = self.lieu(e, o)
        if lieu == e.salle:
            return True
        return (lieu in self.objets and self.objets[lieu]["type"] == "contenant"
                and self.salle(e, lieu) == e.salle and self.ouvert(e, lieu))

    def flamme(self, e, k):
        """Une flamme qu'il a en main : un outil d'allumage, ou une source qu'il croit allumée."""
        o = self.objets[k]
        return k in e.portes and ("allumage" in o.get("usages", []) or "allume" in o and self.feu(e, k)[0])

    def flammes_d_autrui(self, e):
        """(porteur, flamme) : les flammes qu'il croit aux mains d'un autre qui se tient là où il
        est (un outil d'allumage, ou une source portable qu'il croit allumée). Lues une fois par état."""
        cle = ("flammes_d_autrui", e)
        if cle not in self._crus:
            self._crus[cle] = self._flammes_d_autrui(e)
        return self._crus[cle]

    def _flammes_d_autrui(self, e):
        trouvees = []
        for k in self.flammes_portables:
            autre = self.lieu(e, k)
            if (k in e.portes or autre not in self.objets or self.objets[autre]["type"] != "personnage"
                    or autre == self.id or not profil(self.monde, autre) or self.salle(e, autre) != e.salle):
                continue
            if "allumage" in self.objets[k].get("usages", []) or self.feu(e, k)[0]:
                trouvees.append((autre, k))
        return trouvees

    def refuse_feu(self, autre, source):
        return self.retenu(autre, ("demander_feu",), source)

    def flammes_fixes(self, e):
        """Les sources fixes qu'il croit allumées dans la salle où il se tient : il y porte ce
        qu'il veut allumer. Lues une fois par état."""
        cle = ("flammes_fixes", e)
        if cle not in self._crus:
            self._crus[cle] = [k for k in self.connus if "allume" in self.objets[k] and not self.objets[k].get("mobile")
                               and self.salle(e, k) == e.salle and self.feu(e, k)[0]]
        return self._crus[cle]

    def foyer_froid(self, combustible):
        """Le feu qu'une part de bois servirait : le premier foyer qu'il croit éteint."""
        cle = ("foyer_froid", combustible)
        if cle not in self._crus:
            self._crus[cle] = next((f for f in self.foyers if recharge(self.objets[f], self.objets[combustible])
                                   and (self.cru(f, "etat") or {}).get("allume") is False), None)
        return self._crus[cle]

    def attente_part(self, e, donneur, o, service, cible=None):
        """Les minutes qu'il attendra la part ``o`` promise, là où elle se sert (``service``) : que le
        donneur aille d'où il le croit jusqu'à elle, la prenne s'il faut la porter, vienne la servir.
        Promise dans le plan, le donneur s'est mis en route en même temps que lui : le chemin qu'il a
        fait lui-même depuis la promesse (``promis_ou``) n'est plus à attendre. Au moins le geste de
        servir."""
        # Cette lecture ne lit ni le but, ni les droits, ni les effets terminaux.
        # Les lieux (porteurs compris), portes prévues, positions compatibles des
        # anciennes parties et départ de promesse suffisent, avec les possessions
        # et l'allure. Tout le reste appartient à la Vue figée, jamais au temps.
        cle = (e.salle, e.portes, e.allure, e.case, e.orientation,
               frozenset((k, x) for k, x in e.faits.items()
                         if k[0] in ("lieu", "ouvert", "verrou", "case_objet", "promis_ou", "promis_case")),
               donneur, o, service, cible)
        if cle not in self._attentes_parts:
            self._attentes_parts[cle] = self._attente_part(e, donneur, o, service, cible)
        return self._attentes_parts[cle]

    def _attente_part(self, e, donneur, o, service, cible):
        reserve = self.salle(e, o)
        depuis = self.salle(e, donneur) or reserve or service
        DUREES = pnj.DUREES
        portees = frozenset(k for k in self.connus if self.lieu(e, k) == donneur)
        etat = e.apres(salle=depuis, portes=portees,
                       case=self.case_objet(e.apres(salle=depuis), donneur), orientation=None)
        temps = 0
        for salle, objet in ((reserve or depuis, o), (service, cible)):
            route = self.route(etat, salle)
            if route is None:
                return float(ATTENTE_PART)
            temps += cout_route(route, etat.orientation)
            etat = self.arrivee(etat, salle, route)
            if objet:
                approche = self.approche(etat, _etape("prendre", objet))
                if approche is None:
                    return float(ATTENTE_PART)
                temps += cout_route(approche, etat.orientation)
                etat = self.arrivee(etat, salle, approche)
            elif salle == service and e.case is not None and e.salle == service:
                approche = self.approche(etat, _etape("remettre"), cibles=(e.case,))
                if approche is None:
                    return float(ATTENTE_PART)
                temps += cout_route(approche, etat.orientation)
                etat = self.arrivee(etat, salle, approche)
            if salle == reserve and reserve != service and o not in etat.portes:
                temps += DUREES["prendre"] / MINUTE
                etat = etat.apres(portes=etat.portes | {o})
        servir = DUREES["servir"] / MINUTE
        temps += servir
        promis_ou = e.fait("promis_ou", o)
        if promis_ou is not None:
            temps -= self.trajet(promis_ou, service, case=e.fait("promis_case", o))
        return max(servir, temps)

    def sources_a_charger(self, e, vises):
        """Le besoin de combustible, une fois pour tous les lots de cet état.

        Lit uniquement possessions, faits allume/charge, emploi de lumière et
        sources entretenues ; compatibilités, disponibilité et feu cru sont figés.
        Deux états qui ne diffèrent que par salle, droits ou effets terminaux
        réemploient donc exactement ce test, sans réemployer leur résultat de but.
        """
        entretenus = frozenset(vises.get("entretenir", ()))
        cle = (e.portes, frozenset((k, x) for k, x in e.faits.items() if k[0] in ("allume", "charge")),
               self.emploie_lumiere, entretenus)
        if cle not in self._sources_vides:
            deja = any("allume" in self.objets[k] and self.feu(e, k)[0] for k in e.portes)
            disponibles = set().union(*(self.sources_du_lot[k] for k in e.portes if self.disponible(k)))
            self._sources_vides[cle] = frozenset(s for s in self.rechargeables
                if (s in entretenus or self.emploie_lumiere and not deja)
                and not self.feu(e, s)[1] and s not in disponibles)
        return self._sources_vides[cle]

    def trajet(self, depart_, arrivee, *, case=None, cible=None):
        """Temps estimé entre salles et vers une cible ; la case n'intervient pas."""
        etat = depart_ if isinstance(depart_, Etat) else Etat(depart_, (), {}, case)
        cle = ("trajet", etat, arrivee, cible)
        if cle not in self._crus:
            route = self.route(etat, arrivee)
            temps = 0 if route is None else cout_route(route, etat.orientation)
            if route is not None and cible:
                etat = self.arrivee(etat, arrivee, route)
                approche = self.approche(etat, _etape("prendre", cible))
                if approche is not None:
                    temps += cout_route(approche, etat.orientation)
            self._crus[cle] = temps
        return self._crus[cle]

    def feu_noye(self):
        """Tous les foyers qu'il connaît sont dans une salle qu'il croit noyée : une part de
        combustible n'y brûlerait pas."""
        cle = ("feu_noye",)
        if cle not in self._crus:
            from .eau import noyee_crue
            foyers = [f for f in self.connus if self.monde.objets[f].get("foyer")]
            self._crus[cle] = bool(foyers) and all(noyee_crue(self.monde, self.id, _lieu_cru(self.monde, self.id, f))
                                                   for f in foyers)
        return self._crus[cle]

    def lumiere(self, e):
        """La lumière qu'il croit avoir là où il se tient (0 noir, 1 pénombre, 2 éclairé) : pleine
        avec une source allumée en main ou une source que le plan a allumée dans sa salle ; sinon
        celle qu'il croit à la salle (``lumiere_crue``)."""
        if self._eclaire_par_le_plan(e):
            return 2
        cle = (e.salle, "lumiere")
        if cle not in self._crus:
            self._crus[cle] = lumiere_crue(self.monde, self.id, e.salle)
        niveau = self._crus[cle]
        if niveau < 2:
            self._lumiere_lue = True
        return niveau

    def lumiere_devant(self, e, o):
        """La lumière qu'il croit avoir devant ``o``, là où un geste qui demande d'y voir se fait :
        pleine avec la lumière du plan (``lumiere``) ; sinon celle qu'il y a vue en s'y tenant
        (croyance ``lumiere`` de l'objet, ``esprits.constater_lumiere_devant``), et ce qu'y apporte
        une source qu'il sait allumée ou posée près de lui depuis (``deliberation.apport_cru``) ; à
        défaut, celle de la salle."""
        if self._eclaire_par_le_plan(e):
            return 2
        niveau = lumiere_devant_crue(self.monde, self.id, o, e.salle)
        if niveau < 2:
            self._lumiere_lue = True
        return niveau

    def apport(self, o):
        return self._memo((o, "apport"), lambda: apport_cru(self.monde, self.id, o))

    def _eclaire_par_le_plan(self, e):
        """Une source allumée en main, ou une source que le plan a allumée dans sa salle."""
        return (any("allume" in self.objets[k] and self.feu(e, k)[0] for k in e.portes)
                or any(cle[0] == "allume" and allume and self.salle(e, cle[1]) == e.salle
                       for cle, allume in e.faits.items()))

    def pression(self, e):
        """Ce que lui coûte une minute dans cet état, par ce qu'il y laisse monter : le noir, s'il le
        craint (``NOIR``), l'éloignement de chaque lieu où il garde ses biens (``prix_gardes``), l'eau qu'il
        croit ou attend là (au taux où elle l'inquiète, ``NOIR`` par point, comme le noir)."""
        if self._pression_fixe is not None and e.salle in self._pression_fixe:
            return self._pression_fixe[e.salle]
        pressions = self._pressions
        # La case et l'orientation changent le trajet, pas le taux par salle.
        # Ne pas multiplier ces mêmes lectures pour tous les seuils d'arrivée.
        cle = (e.salle, self.contexte_pression(e))
        if cle not in pressions:
            p = NOIR * self.peur if self.peur and self.noir(e) else 0
            peur_sociale = max((peur for x, peur in self.peurs_sociales.items()
                                if self.salle(e, x) == e.salle), default=0)
            pressions[cle] = (p + NOIR * self.taux_mefiance * peur_sociale
                           + sum(prix for g, prix in self.prix_gardes.items() if g != e.salle)
                           + NOIR * self.eau.get(e.salle, 0))
        return pressions[cle]

    def dangereuse(self, e):
        """Le lieu prévu contient un auteur de violence encore actif à ses yeux."""
        return any(self.salle(e, x) == e.salle for x in self.dangers)

    def borne_rester(self, salle):
        """Plancher du séjour final, constant pour toute une recherche.

        Les sorties, sans serrures, obstacles ni eau infranchissable, donnent un
        sur-ensemble des salles que le plan peut atteindre, devis compris. Ne
        garder que les gardes et l'eau : lumière et compagnie peuvent changer.
        Ces lectures sont déjà dans ``_entrees`` (salles, prix_gardes, eau).
        """
        if salle not in self._bornes_rester:
            accessibles, file = set(), [salle]
            while file:
                s = file.pop()
                if s in accessibles:
                    continue
                if s not in self.salles:
                    return 0   # aucune minoration connue hors de la carte
                accessibles.add(s)
                file.extend(x["vers"] for x in self.salles[s]["sorties"].values())
            self._bornes_rester[salle] = RESTER * min(
                sum(prix for g, prix in self.prix_gardes.items() if g != s)
                + NOIR * self.eau.get(s, 0) for s in accessibles)
        return self._bornes_rester[salle]

    def violence(self, cible, defense=False):
        from .combat import prix_violence
        rendu = bool((self.cru(cible, "etat") or {}).get("reddition"))
        # Motif et valeurs sont constants dans cette vue ; seul l'état cru de reddition
        # distingue les cibles. Partager ce calcul ne change aucun terme du graphe.
        return self._memo(("prix_violence", defense, rendu),
                          lambda: prix_violence(self.monde, self.id, self.motif, defense, rendu))

    def descente(self, ici, salle, e=None):
        """Aller d'``ici`` à ``salle``, c'est descendre dans la crue : là-bas il attend plus d'eau qu'ici
        (il l'y attend et pas ici ; ou il l'a vue monter, et elle monte par le bas : plus bas, c'est
        plus d'eau à venir), et il l'y attend noyée, ou son retour coupé par une salle qu'il attend
        noyée (il s'enfermerait du côté de la crue). Tant qu'il la voit monter, il ne quitte pas non
        plus un lieu relié au plus haut pour un lieu que l'eau attendue en coupera (``piege``), même en
        plusieurs fois. Il n'y va pas ; monter, aller vers moins d'eau ou vers un lieu d'où il pourra
        revenir reste permis, même en traversant l'eau."""
        if not self.menacees:
            return False
        cle = (ici, salle, e)
        if cle not in self._descentes:
            from .spatial import altitude
            plus = (salle in self.menacees and ici not in self.menacees
                    or (salle in self.menacees or self.monte) and altitude(self.monde, salle) < altitude(self.monde, ici))
            self._descentes[cle] = (plus and (salle in self.noyees or not self._retour(salle, ici, e) and self.piege(salle, e))
                                    or self.monte and self.piege(salle, e) and not self.piege(ici, e))
        return self._descentes[cle]

    def piege(self, salle, e=None):
        """L'eau monte : il attend ce lieu noyé, ou coupé du plus haut lieu qu'il croit pouvoir gagner
        d'où il se tient (une salle qu'il attend noyée entre eux). Elle monte par le bas : le plus haut
        est le dernier qu'elle gagne."""
        cle = ("piege", salle, e)
        if cle not in self._descentes:
            if "sommet" not in self._descentes:
                from .spatial import altitude
                ici = self.monde.objets[self.id]["lieu"]
                cles = frozenset(k for k in self.connus if porte_par(self.monde, k, self.id) and self.objets[k].get("ouvre"))
                atteintes = self._parcourir(self.monde, self.id, ici, cles, frozenset()) if ici in self.salles else {}
                self._descentes["sommet"] = max(sorted(atteintes) or [ici], key=lambda s: altitude(self.monde, s))
            sommet = self._descentes["sommet"]
            self._descentes[cle] = salle in self.noyees or salle != sommet and not self._retour(salle, sommet, e)
        return self._descentes[cle]

    def _retour(self, depuis, vers, e=None):
        """Retour ou évacuation à l'horizon du séjour, avec des portes d'issue
        certaine et leurs durées ; les ouvertures déjà acquises comptent."""
        if self._cru_spatial is not None:
            e = e if e is not None else depart(self.monde, self.id, self)
            cle = ("retours", depuis, e.portes, e.allure, self.portes_prevues(e))
            if cle not in self._descentes:
                # Le même parcours, projeté à l'horizon du séjour. Ses portes
                # doivent avoir une issue certaine ; leurs durées sont payées
                # avant de juger l'eau, comme dans le trajet aller.
                self._descentes[cle] = trajet_estime.parcours(
                    self, e.apres(salle=depuis), self.ouvertes(e), delai=eau.HORIZON, certain=True)
            return vers in self._descentes[cle]
        vus, file = {depuis}, [depuis]
        while file:
            lieu = file.pop()
            if lieu == vers:
                return True
            for sortie in self.salles[lieu]["sorties"].values():
                suivante, porte = sortie["vers"], sortie.get("porte")
                # Un retour garanti ne suppose ni une serrure inconnue ouverte,
                # ni la réussite future d'un crochetage.
                equipement = e.portes if e is not None else (
                    k for k in self.connus if porte_par(self.monde, k, self.id))
                sure = (not porte or (self.ouvert(e, porte) or porte in self.ouvertes(e) if e is not None else
                        self.cru(porte, "etat") and self.cru(porte, "etat").get("ouverte"))
                        or self.cru(porte, "verrouillee") is False
                        or any(porte in self.objets[k].get("ouvre", ()) for k in equipement))
                if sure and suivante in self.salles and suivante not in vus and (suivante == vers or suivante not in self.noyees):
                    vus.add(suivante)
                    file.append(suivante)
        return False

    def noir(self, e):
        """S'y croit-il dans le noir ? Sans lumière, dans un lieu qu'il croit obscur (``noir_cru``)."""
        if self.lumiere(e):
            return False
        cle = (e.salle, "noir")
        if cle not in self._crus:
            self._crus[cle] = noir_cru(self.monde, self.id, e.salle)
        return self._crus[cle]


def _etape(operation, cible="", outil="", lieu="", condition="", contenu=None):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu, "condition": condition,
            **({"contenu": contenu} if contenu else {})}


def chance_crochetage(monde, id, lumiere, marge=0):
    """Sa chance au jet de ``pnj._crocheter`` à la lumière qu'il croit avoir : d20 + DEX contre
    ``pnj.seuil_crochetage`` (passé d'au moins ``marge``). 0 quand aucun jet ne l'atteint : il ne
    l'envisage pas."""
    from .caractere import modificateur
    from .pnj import seuil_crochetage
    reussites = 21 - (seuil_crochetage(lumiere) + marge - modificateur(monde, id, "DEX"))
    return min(1.0, max(0.0, reussites / 20))


def bruit_crochetage(monde, id, lumiere, discret=True):
    """Le bruit qu'il attend de son crochetage à cette lumière (``ouie.nature_crochetage``) : celui
    d'une serrure qui cède s'il a au moins ``HABILE`` de chance d'y réussir (il s'y sait habile : sa
    DEX, la lumière), sinon un fracas, celui d'un échec."""
    from .ouie import AISANCE, nature_crochetage
    return nature_crochetage(AISANCE if chance_crochetage(monde, id, lumiere, AISANCE) >= HABILE else None, discret)


def gestes(v, e, vises=None, but=None):
    """Les gestes possibles depuis cet état : (fautes, minutes, étapes, état suivant[, durée[,
    abîme]]). Les fautes comptent les personnes lésées ; les minutes font le coût, et la durée
    réelle (celle qu'il passerait dans le noir) n'est donnée que quand elle en diffère : demander, ou
    chercher quelqu'un, coûte plus que le temps qu'il y passe. Abîmer le bien d'autrui (vrai) ajoute
    un prix qui n'est pas du temps, celui de sa douceur (``Vue.degat``, compté par ``_explorer``).

    ``vises`` ouvre les gestes que seul un but demande, sur les objets ou lieux qu'il vise :
    inspecter une salle, prendre un objet qui ne sert à aucun geste, poser, fermer et
    verrouiller, servir une part à quelqu'un. Une SuiteDifferee décrit un groupe
    terminal dont la recherche ne calculera le détail qu'à sa borne de coût.
    Les offrir partout élargirait la recherche sans
    rien lui apprendre."""
    monde, id = v.monde, v.id
    vises = vises or {}
    p = profil(monde, id)
    objets = v.objets
    # Aller : un trajet vers toute salle qu'il croit atteindre avec ce qu'il porte, par les portes
    # qu'il ne croit pas verrouillées ou que le plan a déverrouillées.
    for s, longueur in v.allers(e, v.ouvertes(e)):
        yield 0, longueur, [_etape("aller", lieu=s)], e.apres(salle=s)
    # Le terminal établit seulement une prise de parole possible, jamais
    # l'accord ni le déplacement de l'auditeur. L'approche et son coût passent
    # par la même mesure que les autres échanges ; l'exécution valide l'ouïe.
    for etape in vises.get("parole", ()):
        qui = etape["cible"]
        if v.salle(e, qui) == e.salle and not e.fait("parle", qui):
            yield 0, 1, [etape], e.apres(faits=[(("parle", qui), True)])
    # Les gestes de défense sont offerts seulement aux buts qui les emploient.
    yield from _gestes_defense(v, e, vises)
    agissables, a_porter = v.agissables(vises)
    portes, faits, sa_salle = e.portes, e.faits, e.salle
    v_prendre, v_entretenir = vises.get("prendre", ()), vises.get("entretenir", ())
    v_poser, v_fermer, v_servir = vises.get("poser", ()), vises.get("fermer", ()), vises.get("servir", {})
    noms_vises = frozenset(o for k in ("prendre", "poser", "fermer", "servir") for o in vises.get(k, ()))
    # Une source allumée en main l'éclaire et lui donne une flamme. À qui n'a que faire de lumière
    # (ni le coût du noir, ni le but, ni les gestes explorés), une lampe ou un briquet ne
    # sert que de flamme, pour un feu qu'il croit éteint : une flamme en main suffit, et sans feu à
    # allumer il n'en faut aucune. Une lampe ou un briquet de plus, à prendre, à recharger ou à
    # allumer, ne lui apporterait alors rien, sauf ce que vise le but.
    eclaire_en_main = any("allume" in objets[k] and v.feu(e, k)[0] for k in e.portes)
    lumiere_compte = v.emploie_lumiere
    assez = eclaire_en_main or not lumiere_compte and (
        any(v.flamme(e, k) for k in e.portes)
        or not any(v.feu(e, f)[0] is False for f in v.foyers + list(vises.get("entretenir", ()))))
    droits = v.droits_gestes(e)
    for o, ailleurs, dans, ici, contenant in v.situations_gestes(e, agissables):
        x = objets[o]
        yield from _aide_sur_place(v, e, o, vises, noms_vises)
        # Un objet qu'il ne porte pas et qu'il croit dans une autre salle (sans être une porte de
        # celle-ci) n'offre ici aucun geste : on ne peut qu'en demander une part.
        if ailleurs:
            if v.besoin[o]:
                yield from _parts(v, e, o, dans, vises, but)
            continue
        if v.contrarie(o):
            continue   # On s'oppose à lui sur cette chose : il n'y touche pas tant que cela tient.
        superflu = (assez and ("allume" in x or "allumage" in x.get("usages", [])) and not x.get("foyer")
                    and o not in v_prendre and o not in v_entretenir)
        # Les lieux, la portée et les droits ne lisent pas les effets terminaux,
        # les promesses ni le budget du nœud ; leurs tables gardent leurs clés exactes.
        illicite_, faute, mal, touche_droit, faute_conso, mal_conso, touche_conso = droits[o]
        touche = ([(("touche", contenant), True)] if contenant else []) + touche_droit
        # Prendre ce qu'un geste sait employer : clé, outil, vivres, combustible, flamme portable.
        utile = (v.utile[o] or o in v_prendre) and o in a_porter and not superflu
        # Une source de plus, sans capacité que n'aient déjà celles qu'il porte : rien ne l'acquiert.
        if utile and v.doublon(e, o, noms_vises, v_entretenir):
            utile = False
        # Dans la projection, une charge suffisante ne s'épuise pas en chemin.
        # Porter un combustible sans aucune source à recharger ne change donc
        # aucun geste futur ; on ne développe pas ces inventaires équivalents.
        if (utile and o not in v_prendre and o in v.combustibles_seuls
                and not any(not v.feu(e, s)[1] for s in v.sources_du_lot_triees[o])):
            utile = False
        if ici and o not in portes and x.get("mobile") and v.autorise[o] and v.disponible(o) and utile:
            yield mal, 1, [_etape("prendre", o, condition=faute)], e.apres(portes=portes | {o}, faits=touche)
        # Le demander à qui le porte, s'il est là : il peut refuser, le plan se refait alors.
        porteur = dans if dans in objets and objets[dans]["type"] == "personnage" else None
        if dans == "joueur" and v.proprietaire[o] == id:
            porteur = "joueur"   # Son bien, prêté au joueur : il le lui redemande là où il le voit.
        # On ne demande un objet qu'à qui il appartient (ou s'il n'est à personne), ou ce qui est à
        # soi : recevoir le bien d'autrui de qui le détient n'en fait pas le sien.
        demandable = (utile and porteur and porteur != id and (porteur == "joueur" or v.profil_de(porteur))
                      and o not in e.portes and v.proprietaire[o] in (porteur, None, id)
                      and not (v.besoin[o] and v.proprietaire[o] == porteur))
        if (demandable and porteur != "joueur" and v.salle(e, porteur) is None and not e.fait("cherche", porteur)
                and v.moyen_du_but(o, noms_vises) and not v.refuse(porteur, o)):
            # Il ne sait où est celui qui porte ce que le but emploie : il va le chercher, comme pour
            # une part, et l'appelle là où il ne le voit pas (``_chercher``). La suite se décide sur
            # ce qu'il aura trouvé ; la recherche l'y suppose pour la suite du plan (le lui demander,
            # y prendre du feu).
            recherche = _chercher(v, e, porteur)
            if recherche is not None:
                yield recherche
        if demandable and v.salle(e, porteur) == e.salle:
            # Prêté par son propriétaire, il s'en sert sans faute (``biens.permis``).
            permis = [(("permis", o), True)]
            if not v.refuse(porteur, o):
                yield (0, 1 + DEMANDE / v.chances_demandes[porteur], [_etape("demander", porteur, outil=o)],
                       e.apres(portes=e.portes | {o}, faits=permis), 1)
            # Acheter au propriétaire ou racheter son propre bien au détenteur.
            prix = objets[o].get("prix")
            if (prix and porteur != "joueur" and v.proprietaire[o] in (porteur, id)
                    and v.piece and not v.refuse_achat(porteur, o)
                    and v.richesse - (e.fait("depense") or 0) >= prix):
                from .pnj_propositions import offre_refusee
                if not v._memo(("achat_refuse", porteur, o, prix), lambda: offre_refusee(
                        monde, id, porteur, o, {"type": "pieces", "montant": prix})):
                    yield (0, 1 + DEMANDE + v.depense(prix),
                           [_etape("acheter", porteur, outil=o, contenu={"prix": prix})],
                           e.apres(portes=e.portes | {o}, faits=[(("permis", o), True), (("achete", o), True),
                                                                 (("depense",), (e.fait("depense") or 0) + prix)]), 1)
        # Une violence ne sert que sur le porteur d’un moyen pertinent.
        # Son coût se compare à demander ; aucun ordre de recours imposé.
        if (utile and porteur and porteur not in (id, "joueur") and v.violence(porteur) is not None and v.autorise[o]
                and v.salle(e, porteur) == e.salle
                and not e.fait("assomme", porteur) and not ici and v.embuscade_possible(e, porteur)):
            from .combat import arme, force_crue, RISQUE, facteur_violence
            from .caractere import valeur
            chance = v._memo(("force_crue", porteur), lambda: force_crue(monde, id, porteur))
            risque = RISQUE * (1 - chance) * (100 - valeur(monde, id, "courage")) / 50
            outils = [k for k in sorted(e.portes) if arme(objets[k]) and not arme(objets[k])[0]]
            outil = max(outils, key=lambda k: arme(objets[k])[1], default="")
            doux = not e.fait("faute", porteur, "douceur")
            # Le seul effet utile de cette agression est de prendre ce moyen : grouper la
            # transition évite d'explorer un état intermédiaire identique pour chaque bien porté.
            # Les trois gestes restent distincts, revalidés un à un dans le monde réel.
            yield (mal, 1 + .025 / chance + risque,
                   [_etape("dans_le_dos", porteur, condition="dans_le_dos"),
                    _etape("assommer", porteur, outil=outil, condition="dans_le_dos"),
                    _etape("prendre", o, condition=faute)],
                   e.apres(portes=e.portes | {o}, faits=[(("assomme", porteur), True),
                       (("faute", porteur, "douceur"), True), *touche]),
                   1 + .025 / chance, facteur_violence(rendu=bool((v.cru(porteur, "etat") or {}).get("reddition"))) * doux)
        touche = [x for x in touche if x[0][0] == "faute"]
        if o in v_poser and o in portes:
            yield (0, 1, [_etape("poser", o, lieu=sa_salle)],
                   e.apres(portes=portes - {o}, faits=[(("lieu", o), sa_salle)]))
        if (o in v_fermer and refermable(e.fait("fin", o) or v.cru(o, "fin"))
                and v.salle(e, o) == sa_salle):
            if v.ouvert(e, o):
                yield 0, 1, [_etape("fermer", o)], e.apres(faits=[(("ouvert", o), False)])
            elif not v.verrouille(e, o):
                for cle in sorted(k for k in e.portes if o in objets[k].get("ouvre", [])):
                    yield 0, 1, [_etape("verrouiller", o, outil=cle)], e.apres(faits=[(("verrou", o), True)])
        for pour in v_servir.get(o, ()):
            if ici and v.disponible(o):
                dedans = [(("touche", contenant), True)] if contenant else []
                yield (mal_conso, 1, [_etape("servir", o, condition=faute_conso, contenu={"pour": pour})],
                       e.apres(faits=[(("servi", o), pour), *dedans, *touche_conso]))
        # Une serrure : un contenant de sa salle, ou une porte qui en sort. Une porte verrouillée est
        # un obstacle comme un contenant : la clé qu'il porte l'ouvre en chemin (``Vue.route``), le
        # crochetage la déverrouille ; la demander, c'est demander la clé.
        porte = x["type"] == "porte"
        if (x["type"] == "contenant" and v.salle(e, o) == e.salle) or porte and o in v.portes_de[e.salle]:
            ouvert, verrou = v.ouvert(e, o), v.verrouille(e, o)
            if not porte and not ouvert and not verrou and v.autorise[o]:
                yield (mal, 1, [_etape("ouvrir", o, condition=faute)],
                       e.apres(faits=[(("ouvert", o), True), (("touche", o), True), *touche]))
            if verrou and not ouvert:
                for cle in sorted(k for k in e.portes if o in objets[k].get("ouvre", []) and not porte):
                    yield (0, 1, [_etape("deverrouiller", o, outil=cle, condition=faute)],
                           e.apres(faits=[(("verrou", o), False), (("touche", o), True)]))
                # Sa chance est celle du jet à la lumière qu'il croit avoir devant la serrure ; nulle,
                # il n'essaie pas. L'étape retient cette lumière : devant, il la constate (``pnj.agir``).
                lumiere = v.lumiere_devant(e, o) if "crochetage" in p["capacites"] else None
                chance = chance_crochetage(monde, id, lumiere) if lumiere is not None else 0
                if chance and v.autorise[o]:
                    for outil in sorted(k for k in e.portes if "crochetage" in objets[k].get("usages", [])):
                        yield (mal, 1 / chance, [_etape("crocheter", o, outil=outil, condition=faute,
                                                        contenu={"lumiere": lumiere})],
                               e.apres(faits=[(("verrou", o), False), (("touche", o), True), *touche]))
                # La forcer, par la règle du joueur (``force``) : avec un outil qu'il porte qui l'entame,
                # coup après coup jusqu'à la briser ; brisée, elle reste ouverte. Abîmer le bien
                # d'autrui heurte aussi sa douceur, une fois par personne lésée (``degat``).
                brise = v.leses_bris[o]
                if v.autorise[o] and not (brise and v.degat is None):
                    degat = [(("degat", brise), True)] if brise else []
                    abime = bool(brise) and not e.fait("degat", brise)
                    for outil in sorted(k for k in e.portes if force.adapte(x, objets[k])) + ([""] if porte and vises.get("evader") else []):
                        n, c = force.coups(monde, id, x, objets.get(outil)), force.chance(monde, id, objets.get(outil))
                        if n and c:
                            cout_coups = n / c * (.05 if porte else 1)
                            yield (int(bool(brise) and not e.fait("faute", brise, "honnetete")), cout_coups,
                                   [_etape("frapper", o, outil=outil, condition="sans_temoin" if brise else "")],
                                   e.apres(faits=[(("verrou", o), False), (("ouvert", o), True), (("touche", o), True),
                                                  (("fin", o), "detruit"),
                                                  *([(("faute", brise, "honnetete"), True)] if brise else []), *degat]),
                                   cout_coups, abime)
        # Manger ce qui est à portée.
        if x["type"] == "nourriture" and ici and v.disponible(o) and v.autorise[o]:
            porte = o in e.portes
            dedans = [(("touche", contenant), True)] if contenant else []
            yield (0 if porte else mal_conso, 1, [_etape("manger", o, condition="" if porte else faute_conso)],
                   e.apres(faits=[(("mange", o), True), *dedans, *([] if porte else touche_conso)]))
        # Une source (un foyer, une lampe) qu'il porte ou qui est dans sa salle : la recharger du
        # combustible qu'elle brûle, l'allumer à une flamme qu'il porte (ou à une flamme fixe de sa
        # salle, s'il la porte), se chauffer à un foyer allumé.
        if "allume" in x and not superflu and (o in portes or ici or v.salle(e, o) == sa_salle and not x.get("mobile")):
            allume, charge = v.feu(e, o)
            # Un foyer se recharge tant qu'il n'est pas vif ; une lampe, quand elle est vide.
            if brule(x) and not charge:
                for bois in sorted(k for k in e.portes if recharge(x, objets[k]) and v.disponible(k)):
                    yield (mal, 1, [_etape("alimenter", o, outil=bois, condition=faute)],
                           e.apres(faits=[(("charge", o), True), *touche]))
            if allume is False and charge:
                flammes = sorted(k for k in e.portes if k != o and v.flamme(e, k))
                if o in e.portes:
                    flammes += [k for k in v.flammes_fixes(e) if k != o and k not in flammes]
                for flamme in flammes:
                    # La source d'autrui : y toucher est une faute, comme la prendre.
                    yield (mal, 1, [_etape("allumer", o, outil=flamme, condition=faute)],
                           e.apres(faits=[(("allume", o), True), *touche]))
                # Une flamme que porte un autre, là où il se tient : il lui tend sa source et lui
                # demande du feu. Cela n'ôte rien au porteur, ni prêt ni part : il l'accorde, sauf
                # méfiance (``echanges.demander_feu``). Seulement sa source, ou une qu'il peut
                # employer sans faute : l'autre ne prête pas la main au bien d'autrui.
                if o in e.portes and not illicite_:
                    for autre, flamme in v.flammes_d_autrui(e):
                        if not v.refuse_feu(autre, o):
                            yield (0, 1 + DEMANDE, [_etape("demander_feu", autre, outil=flamme,
                                                           contenu={"allumer": o})],
                                   e.apres(faits=[(("allume", o), True)]), 1)
            # Là où il croit ou attend l'eau, on ne se chauffe pas : elle trempe, et l'on y resterait.
            if allume and x.get("foyer") and sa_salle not in v.menacees:
                yield 0, 1, [_etape("chauffer", o)], e.apres(faits=[(("chauffe", o), True)])
        if v.besoin[o]:
            yield from _parts(v, e, o, dans, vises, but)
    for cible in vises.get("ranimer", ()):
        etat = lire(v.monde, v.id)["croyances"].get(cible, {}).get("etat", {}).get("valeur", {})
        if etat.get("conscient") is False and v.salle(e, cible) == e.salle and not e.fait("ranime", cible):
            yield 0, 1 / 6, [_etape("ranimer", cible)], e.apres(faits=[(("ranime", cible), True)])
    for salle in vises.get("inspecter", ()):
        if salle == e.salle and not e.fait("inspecte", salle):
            yield 0, 1, [_etape("inspecter", lieu=salle)], e.apres(faits=[(("inspecte", salle), True)])
    for condition in vises.get("confier", ()):
        yield from _engager(v, e, condition)


def _aide_sur_place(v, e, o, vises, noms_vises):
    """Demander un moyen sans quitter sa charge, après l'échec des recours ordinaires.

    Les mêmes moyens et effets que les gestes autonomes ; la parole s'exécute par
    ``confier``. La projection s'arrête à la demande, puis attend la réalisation réelle.
    Aucun accès aux moyens ou à l'intention privée de l'aidant.
    """
    if (v.seul or not v.poste_garde or not (v.motif in v.detresses or v.aides) or e.salle != v.poste
            or v.illicite[o] or not v.disponible(o) or v.contrarie(o)):
        return
    x = v.objets[o]
    conditions = []
    if ("allume" in x and v.salle(e, o) == e.salle and v.feu(e, o)[0] is False
            and (v.emploie_lumiere or o in vises.get("entretenir", ()))):
        conditions.append({"objet": o, "allume": True})
    if (x.get("mobile") and o not in e.portes and v.salle(e, o) not in (None, e.salle)
            and v.utile[o] and v.pertinent(o, noms_vises)
            and not v.doublon(e, o, noms_vises, vises.get("entretenir", ()))):
        conditions.append({"objet": o, "remettre": v.id})
    for condition in conditions:
        effets = effets_tache(condition)
        suivant = e.apres(faits=effets, portes=e.portes | {o} if "remettre" in condition else e.portes)
        if all(e.fait(*cle) == valeur for cle, valeur in effets):
            continue
        pending = next(((autre, x) for autre, x in v.aides if x["condition"] == condition), None)
        if pending:
            # Il ne répète pas une parole en cours. Pas d'effet dans le monde avant le geste.
            yield 0, TACHE, [{**_etape("inspecter"), "attendre_remise": True}], suivant, TACHE
            continue
        if v.motif not in v.detresses:
            continue   # Une parole en cours n'ouvre pas d'autres demandes.
        for autre in v.personnes():
            if v.salle(e, autre) != e.salle or v.se_mefie(autre) or v.retenu(autre, ("confier",), o):
                continue
            attente = v.attente_part(e, autre, o, e.salle, o)
            yield (0, 1 + DEMANDE / v.chances_demandes[autre] + attente,
                   [{**_etape("confier", autre, contenu=condition), "suppose": True}],
                   suivant, 1 + attente)


def effets_tache(condition):
    """Ce qu'une tâche faite change, dans l'état cru d'un plan : un feu chargé et allumé, un bien
    fermé à clé, un objet en son lieu."""
    o = condition["objet"]
    if "allume" in condition:
        return [(("charge", o), True), (("allume", o), True)]
    if "verrouillee" in condition:
        return [(("verrou", o), True), (("ouvert", o), False)]
    if "remettre" in condition:
        return [(("lieu", o), condition["remettre"])]
    return [(("lieu", o), condition["lieu"])]


def peine_tache(v, e, condition):
    """La peine d'une tâche, d'après ce qu'il en croit : le chemin d'ici (où se tient celui qu'il
    paie) jusqu'au lieu de la tâche, et ``TACHE`` minutes de travail ; None s'il ne sait où."""
    lieu = condition.get("lieu") or v.salle(e, condition["objet"])
    return None if lieu is None else v.trajet(e, lieu, cible=condition["objet"]) + TACHE


def prix_tache(peine):
    """Ce qu'il offre pour une tâche : une pièce par ``SALAIRE`` minutes de peine. Il ne sait pas ce
    que vaut une pièce pour l'autre : il paie la peine."""
    return max(1, math.ceil(peine / SALAIRE))


def hausse(prix):
    """L'offre qui suit un refus « cher » à ce prix : un palier plus haut (``PALIER``, au moins une
    pièce de plus)."""
    return max(prix + 1, math.ceil(prix * PALIER))


def _engager(v, e, condition):
    """Payer quelqu'un, là où il se tient avec lui, pour qu'il fasse en sorte que ``condition`` soit
    vraie (``echanges.engager``), sur ce qu'il pourrait faire lui-même sans faute : il propose ses
    pièces à qui il ne se méfie pas et qui ne vient pas de refuser ; l'autre accepte si ces pièces valent pour lui la peine. Comme une demande, ce n'est pas
    acquis (``relations.chance_demande``), selon son expérience de cet interlocuteur ; il paie aussitôt ce que lui coûtent ses pièces (``Vue.depense``), et attend
    que l'autre ait fait la tâche (sa peine). La tâche faite, son but est atteint ; il ne la fait pas
    à sa place tant qu'elle court (``deliberation.tache_payee``).

    Il n'offre que ce qui vaut la peine pour lui : ce que lui coûtent ces pièces (``Vue.depense``,
    ``caractere.valeur_pieces``) ne dépasse pas la peine que la tâche lui épargne. Refusé pour un prix
    trop bas, il hausse d'un palier (``hausse``) tant que l'offre vaut la peine ; au-delà, il renonce à
    ce marché. Une hausse à la fois : après un refus « cher », aucune offre haussée de la même tâche, à
    lui ou à un autre, avant la délibération de la minute suivante (``Vue.hausse_faite``)."""
    o = condition["objet"]
    # On ne paie quelqu'un que pour ce qu'on pourrait faire soi-même sans faute : son bien, ce qui
    # n'est à personne, ce qu'on vous a confié ; pas le bien d'autrui qu'on convoite.
    if not v.piece or e.fait("engage", o) or o not in v.illicite or v.illicite[o] or "lieu" in condition and o in e.portes:
        return
    peine = peine_tache(v, e, condition)
    if peine is None:
        return
    prix = prix_tache(peine)
    if v.richesse - (e.fait("depense") or 0) < prix or v.depense(prix) > peine:
        return
    for autre in v.personnes():
        if v.salle(e, autre) != e.salle or v.se_mefie(autre):
            continue
        # Un refus qui tient l'écarte ; trop peu payé, il ne tient que pour ce prix : il offre un
        # palier plus haut, à la délibération suivante, s'il le peut et tant que cela vaut la peine.
        offre, refus = prix, v.refuse_tache(autre, o)
        if refus:
            if refus["raison"] != "cher" or v.hausse_faite(o):
                continue
            offre = prix if prix > refus["prix"] else hausse(refus["prix"])
            if v.richesse - (e.fait("depense") or 0) < offre or v.depense(offre) > peine:
                continue
        yield (0, 1 + DEMANDE / v.chances_demandes[autre] + v.depense(offre) + peine,
               [_etape("engager", autre, contenu={"condition": dict(condition), "prix": offre})],
               e.apres(faits=effets_tache(condition) + [(("engage", o), autre),
                                                        (("depense",), (e.fait("depense") or 0) + offre)]), 1)


def _parts(v, e, o, dans, vises, but):
    if v._estime_part or not v.lot_partageable(o):
        return
    # Le but peut lire n'importe quel fait : aucun quotient approximatif de e.
    # But et visées sont fixes pendant une exploration, enregistrés une fois à
    # son entrée. La Vue ne traverse ni mutation du monde ni sauvegarde.
    cle = (v._contexte_parts, e, o, dans, v.emploie_lumiere)
    if cle in v._parts_lues:
        yield from v._parts_lues[cle]
        return
    resultat = []
    for g in _parts_calculer(v, e, o, dans, vises, but):
        resultat.append(g)
        yield g   # conserver le point de toute lecture de lumière dans _suites
    v._parts_lues[cle] = resultat


def _parts_calculer(v, e, o, dans, vises, but):
    """Une part : l'attendre si elle est promise, là où le donneur viendra la servir (près des
    vivres, ou du feu qu'il entretiendra) ; sinon la demander à son propriétaire. Une part de
    combustible va au feu que le but entretient, sinon au premier qu'il croit éteint : le donneur le
    recharge et l'allume lui-même. On ne demande pas ce qu'on a sur soi. ``dans`` : où est ``o``
    (``Vue.lieu``).

    Promise ou vendue, elle n'est pas encore là : il l'attend où elle se sert, le temps que le
    donneur y vienne (``attente_part``), et ce temps-là compte comme tout autre, avec ce qu'il y
    laisse monter (loin de ses biens, dans le noir)."""
    if v._estime_part:
        return
    yield from _parts_remises(v, e, o, dans, vises, but)
    besoin, id = v.besoin[o], v.id
    if v.seul:
        return  # Une part servie est un service du donneur ; seule une part remise (ci-dessus) compte.
    if not (besoin and v.disponible(o)):
        return
    donneur = v.proprietaire[o]
    foyer = (next((f for f in vises.get("entretenir", ()) if recharge(v.objets[f], v.objets[o])),
                  v.foyer_froid(o)) if besoin == "chaleur" else None)
    if besoin == "chaleur" and (foyer is None or any(recharge(v.objets[foyer], v.objets[k])
                                                   and v.disponible(k) for k in e.portes)):
        return
    if besoin == "faim" and v.sur_soi(besoin, e.portes):
        return
    if foyer and v.salle(e, foyer) in v.menacees:
        return   # Un feu là où il croit ou attend l'eau : ni chaleur à y prendre, ni bois à y porter.
    part = [(("part", o), donneur)] + ([(("charge", foyer), True), (("allume", foyer), True)]
                                       if foyer else [])
    if donneur not in (None, id, "joueur") and v.profil_de(donneur):
        remise = v.promesse(o, True) == donneur
        promise = remise or v.promesse(o, False) == donneur or e.fait("promis", o) == donneur
        if promise:
            # Une part à remettre se reçoit auprès du demandeur ; la part servie
            # garde son lieu de service. Dans les deux cas, attendre n'est pas la recevoir.
            service = e.salle if remise else v.salle(e, foyer) if foyer else v.salle(e, o)
            if e.salle == service:
                attente = v.attente_part(e, donneur, o, service, None if remise else foyer or o)
                yield 0, attente, [], e.apres(faits=part), attente
        elif not e.fait("promis", o):
            ou = v.salle(e, donneur)
            promis = [(("promis", o), donneur), (("promis_ou", o), e.salle), (("promis_case", o), e.case)]
            # Promise, elle ne mène qu'à l'attendre là où elle se sert : la demander ou
            # l'acheter ne sert que si, servie là, elle atteint le but (comme ``TERMINAUX``). On ne
            # la demande ni ne l'achète qu'au donneur qui se tient là : ailleurs, rien à juger.
            utile_part = None
            if ou == e.salle:
                service = v.salle(e, foyer) if foyer else v.salle(e, o)
                utile_part = but is None or service is not None and but(v, e.apres(salle=service, faits=part))
            # L'acheter s'il peut la payer : le prix lui coûte ce que valent ses pièces.
            # Posé ou porté, le lot fournit une part ; le contenant reste au donneur.
            prix = v.objets[o].get("prix_part", PRIX_PART)
            if (utile_part and ou == e.salle and v.piece and not v.refuse_achat(donneur, o)
                    and v.richesse - (e.fait("depense") or 0) >= prix):
                yield (0, 1 + DEMANDE + v.depense(prix),
                       [_etape("acheter", donneur, outil=o,
                               contenu={"prix": prix, **({"foyer": foyer} if foyer else {})})],
                       e.apres(faits=promis + [(("depense",), (e.fait("depense") or 0) + prix)]), 1)
        if not promise and not e.fait("promis", o) and not v.refuse(donneur, o):
            if ou == e.salle and utile_part:
                # Une part demandée n'est pas acquise : comme un objet demandé, elle coûte
                # selon la chance d'être accordée (``relations.chance_demande``).
                yield (0, 1 + DEMANDE / v.chances_demandes[donneur], [_etape("demander", donneur, outil=o,
                                                contenu={"foyer": foyer} if foyer else None)],
                       e.apres(faits=promis), 1)
            elif (ou is None and not e.fait("cherche", donneur)
                  and (but is None or but(v, e.apres(faits=part)))):
                # Le chercher ne sert que si sa part atteint le but.
                recherche = _chercher(v, e, donneur)
                if recherche is not None:
                    yield recherche


def _parts_remises(v, e, o, dans, vises, but=None):
    """Demander, acheter ou attendre une part, avec un devis de la suite.

    Le devis atteint un but hypothétique terminal, jamais développé dans le graphe.
    Sa véritable identité n'est connue qu'à la remise : le plan exécuté s'arrête à
    la demande ou à l'attente, puis se refait sur la part réellement reçue. Aucune
    source du monde n'est réputée chargée à l'accord.
    """
    repas = o in vises.get('servir', {}) and v.besoin[o] == 'faim'
    if o in e.portes or not (repas or "combustible" in v.objets[o].get("usages", ())) or not v.disponible(o):
        return
    donneur = v.proprietaire[o]
    if donneur in (None, v.id, "joueur") or not v.profil_de(donneur):
        return
    if not repas and not (v.sources_du_lot[o] & v.sources_a_charger(e, vises)):
        return
    attente = 0 if dans == donneur and v.salle(e, donneur) == e.salle else v.attente_part(e, donneur, o, e.salle)
    promise = v.promesse(o, True) == donneur
    if not promise and v.promesse(o):
        return   # Une autre façon de servir cette part est déjà promise.
    ou = v.salle(e, donneur)
    if ou is None and not e.fait("cherche", donneur) and not v.refuse(donneur, o):
        recherche = _chercher(v, e, donneur)
        if recherche is not None:
            yield recherche
    if not promise and ou != e.salle:
        return
    offres = []
    if promise:
        offres.append((attente, {**_etape("inspecter"), "attendre_remise": True}, attente, 0))
    elif not v.refuse(donneur, o):
        offres.append((1 + DEMANDE / v.chances_demandes[donneur] + attente,
                       {**_etape("demander", donneur, outil=o, contenu={"remettre_part": True}), "suppose": True},
                       1 + attente, 0))
    prix = v.objets[o].get("prix_part", PRIX_PART)
    if not promise and v.piece and not v.refuse_achat(donneur, o) and v.richesse - (e.fait("depense") or 0) >= prix:
        offres.append((1 + DEMANDE + v.depense(prix) + attente,
                       {**_etape("acheter", donneur, outil=o, contenu={"prix": prix, "remettre_part": True}),
                        "suppose": True}, 1 + attente, prix))
    if not offres:
        return
    # Les suites ci-dessous sont toutes terminales. Leur prix contient au moins
    # celui de l'offre, moins le geste conventionnel que _mesurer remplacera par
    # une durée positive. Attente, devis, fautes et pressions sont non négatifs.
    # Borne nulle pour une attente promise : aucun tarif de parole n'y est imposé.
    borne = min(minutes if promise else max(0, minutes - 1)
                for minutes, _, _, _ in offres)
    yield SuiteDifferee(borne, _estimer_remise, (e, o, attente, offres, vises, but),
                       depuis=e, vises=vises, but=but)


class SuiteDifferee:
    """Nœud A* intermédiaire d'une suite terminale, sans effet sur le monde.

    Son coût déjà payé est celui du préfixe ; ``borne`` minore tout son reste.
    Pour un but qui se tient en restant, le plancher commun du séjour s'ajoute
    à h ici comme aux états ordinaires (``_explorer_etats``). La borne est
    cohérente : l'arête vers ce nœud coûte zéro, ses sorties terminales coûtent
    au moins la borne plus ce plancher, et leurs h sont nuls. Aucun résultat
    estimé n'est employé comme borne. Une seule évaluation par nœud du graphe.
    """
    def __init__(self, borne, calcul, arguments, *, depuis=None, vises=None, but=None):
        self.borne, self.calcul, self.arguments = borne, calcul, arguments
        self.depuis, self.vises, self.but = depuis, vises, but
        self.suites = None

    def developper(self, v):
        if self.suites is None:
            v._devis_developpes += 1
            gestes_ = self.calcul(v, *self.arguments)
            self.suites = (_normaliser_suites(v, self.depuis, self.vises, self.but, gestes_)
                           if self.depuis is not None else [(*g, 0) for g in gestes_])
            assert all(g[3].fait("estimation") and g[4] == 0 and g[1] >= self.borne
                       for g in self.suites), "Borne de suite terminale invalide"
        return self.suites


def _estimer_remise(v, e, o, attente, offres, vises, but):
    from .part_estimee import suites
    en_feu = sum(1 for k in e.portes if e.fait("allume", k))
    for minutes, demande, duree, paye in offres:
        depuis, pression = e, attente * v.pression(e)
        if not demande.get("attendre_remise"):
            mesure = _mesurer(v, e, [demande], e, 1)
            if mesure is None:
                continue
            temps_demande, pression_demande, depuis = mesure
            minutes += temps_demande - 1
            duree += temps_demande - 1
            pression += pression_demande
        v._estime_part = True
        try:
            if o in vises.get('servir', {}) and v.besoin[o] == 'faim':
                # Une part hypothétique sert le même but que la réserve. Le plan
                # réel s'arrête à sa demande et attend son identité effective.
                estimations = []
                for pour in vises['servir'][o]:
                    salle = v.salle(depuis, pour)
                    route = v.route(depuis, salle) if salle is not None else None
                    if route is None:
                        continue
                    fin = v.arrivee(depuis, salle, route).apres(portes=depuis.portes | {o},
                                                                  faits=[(('permis', o), True), (('servi', o), True)])
                    mesure = _mesurer(v, fin, [_etape('servir', o, contenu={'pour': pour})], fin, 1)
                    if mesure:
                        estimations.append((0, v.trajet(depuis, salle, cible=pour) + mesure[0] + mesure[1], mesure[2], 0))
            else:
                estimations = suites(v, depuis.apres(faits=[(("depense",), (e.fait("depense") or 0) + paye)]),
                                     o, vises, but or (lambda v, e: True))
        finally:
            v._estime_part = False
        for fautes, cout, final, abime in estimations:
            fin = final.apres(faits=[(("estimation",), True)])
            yield (fautes, minutes + duree * FLAMME_EN_MAIN * en_feu + pression + cout,
                   [{**demande, "part_estimee": o}], fin, 0, abime)


class TransitionMesuree(tuple):
    """Transition déjà mesurée, avec sa pression intégrée en dernier terme."""


def _chercher(v, e, sujet):
    """Perdu de vue : il va le chercher là où il est passé le moins récemment, et l'y suppose,
    hors des salles où il l'a cherché en vain (``deliberation.appels_vains``) ; None s'il n'en reste
    aucune. Le plan s'arrête après cette recherche : la suite se décide sur ce qu'il aura vu."""
    # Le contact inconnu peut d'abord faire l'objet d'une question présente.
    # Comme l'inspection, cette transition s'arrête avant toute suite supposée.
    question = None
    if e.salle == v.objets[v.id]["lieu"] and not e.fait("cherche", sujet):
        recours = s_enquerir(v.monde, v.id, sujet=sujet, _vue=v, _etat=e)
        if recours is not None:
            etapes = [{**x, "suppose": True} for x in recours[1]]
            suivant = e.apres(faits=[(("lieu", sujet), e.salle), (("cherche", sujet), True)])
            mesure = _mesurer(v, e, etapes, suivant, 1)
            if mesure is not None:
                temps, pression, suivant = mesure
                question = TransitionMesuree((0, temps + DEMANDE, etapes, suivant, temps, False, pression))
    visites = lire(v.monde, v.id)["visites"]
    vaines = appels_vains(v.monde, v.id, sujet)
    routes = {s: v.route(e, s) for s in v.salles if s not in vaines}
    routes = {s: r for s, r in routes.items() if r is not None}
    if not routes:
        return question
    # Le coût d'une route est celui de toute la recherche (``Vue.allers`` : passages compris).
    salle = min(routes, key=lambda s: (visites.get(s, -1), cout_route(routes[s], e.orientation), s))
    # Il y parcourt la salle des yeux, et l'appelle s'il ne le voit pas (``pnj.appeler``).
    etapes = ([_etape("aller", lieu=salle)] if salle != e.salle else []) + [
        {**_etape("inspecter", lieu=salle, contenu={"cherche": sujet}), "suppose": True}]
    suivant = e.apres(salle=salle, faits=[(("lieu", sujet), salle), (("cherche", sujet), True)])
    mesure = _mesurer(v, e, etapes, suivant, cout_route(routes[salle], e.orientation) + 1)
    if mesure is None:
        return question
    temps, pression, suivant = mesure
    recherche = TransitionMesuree((0, temps + CHERCHER, etapes, suivant, temps, False, pression))
    return min((question, recherche), key=lambda t: t[1] + t[6]) if question is not None else recherche


def depart(monde, id, v=None):
    v = v or vue(monde, id)
    o = monde.objets[id]
    return Etat(o["lieu"], [k for k in v.connus if porte_par(monde, k, id)], {})


# Ce qui change d'une minute à l'autre dans un objet, et qu'une recherche ne lit jamais : elle lit
# ce qu'il en croit. Le lieu vrai n'y entre que par ce qu'il porte, les propriétaires et les
# objets fixes (``_entrees``) ; les pièces d'une bourse, que par ce qu'il peut dépenser.
CHANGEANTS = frozenset(("lieu", "position", "position_salle", "orientation", "corps", "humeur", "combustible",
                        "portions", "charges", "ouverte", "verrouillee", "allume", "pieces"))


def _entrees(v, vises, profondeur, noeuds):
    # Seules ces lectures dépendent du candidat. Le relevé commun reste privé
    # au choix ; hors de ce bloc, une Vue ordinaire est toujours relue.
    partage = getattr(v, "_partage_choix", None)
    if partage is None:
        communes = _entrees_communes(v)
    else:
        if partage[1] is None:
            partage[1] = _entrees_communes(v)
        communes = partage[1]
    return communes, json.dumps([
        vises, profondeur, noeuds, None if v.emplois is None else sorted(v.emplois), v.eclairer,
        [[x, v.violence(x) is not None] for x in v.personnes()], _entrees_defense(v, vises)
    ], ensure_ascii=False, check_circular=False)


def _entrees_communes(v):
    """Tout ce que lit une recherche hors de son but, en JSON (comme une sauvegarde) : où il se
    tient et ce qu'il porte, ce qu'il croit (les valeurs, pas leur date), ses refus et promesses
    avec ce qu'en dit l'horloge, ses visites, les objets hors de ce qui change à chaque minute
    (``CHANGEANTS``), le propriétaire de ce qu'il connaît, les salles.

    Une lecture nouvelle dans la recherche (gestes, coûts, buts) doit y entrer, sans quoi un
    résultat périmé serait repris : ``VERIFIER`` le contrôle dans les tests."""
    monde, id = v.monde, v.id
    esprit_ = lire(monde, id)
    croyances = esprit_["croyances"]
    minute = monde.data["minutes"]
    from .signes import actives
    # Les cibles et obstacles restent localisés ; le départ est seulement la salle.
    metrique = v._metrique
    return json.dumps([
        [(x, a, c["valeur"], c.get("envers")) for x, a, c in actives(monde, id)],
        monde.objets[id]["lieu"],
        # Une occasion attendue ne garantit pas la fin d'un geste dans l'eau.
        (esprit_["patience"] is None) if v.eau_route else None,
        [k for k in v.connus if porte_par(monde, k, id)],
        # La fin des battants est lue par les gestes et leur restauration.
        [[s, a, c["valeur"]] for s, d in croyances.items() for a, c in d.items()
         if a != "fin" or monde.objets.get(s, {}).get("type") in ("porte", "contenant")],
        [[x, {a: r[a] for a in (*relations.AXES, "bandes")} ]
         for x in relations.connus(monde, id) for r in [relations.axes(monde, id, x)]],
        # Les salles cherchées en vain (``_chercher``), tant qu'elles comptent.
        [[q, sorted(appels_vains(monde, id, q))] for q in sorted(esprit_["recherches"])],
        [[s, minute - s["minute"] < ATTENTE_PART,
          # Une part de bois promise : le feu revu rechargé depuis (``promesse_en_cours``).
          croyances.get(s.get("foyer"), {}).get("etat", {}).get("minute", -1) >= s["minute"]]
         for s in esprit_["memoire"] if s["type"] in ("promis", "nourri", "recu", "promesse_annulee", "creance")],
        # Les refus retenus, s'ils tiennent (``Vue.refus_tenus``) et s'ils sont récents.
        # Le refus « cher » de cette minute même retient la hausse suivante (``Vue.hausse_faite``).
        [[s, tenu, minute - s["minute"] < REDEMANDE, minute == s["minute"]] for s, tenu in v.refus_tenus()],
        _ordre_visites(v.salles, esprit_["visites"]),
        # Le lieu d'un objet fixe, sans croyance sur son lieu, se sait sans l'avoir vu (``_lieu_cru``).
        [[k, {a: w for a, w in o.items() if a not in CHANGEANTS}, "allume" in o,
          None if o.get("mobile") or "lieu" in croyances.get(k, ()) else o.get("lieu")]
         for k, o in monde.objets.items()],
        [[o, v.proprietaire[o]] for o in v.connus], v.salles, v.gardes,
        v.prix_gardes, v.chances_demandes, v.detresses, v.poste_garde, v.aides,
        # Ce qu'un prêt ou une garde permettent (``biens.permis``), ce qu'il peut payer et ce que
        # vaut pour lui une pièce.
        [o for o in v.connus if v.illicite[o]], [o for o in v.connus if v.consomme_illicite[o]],
        [[o, v.leses_bris[o]] for o in v.connus if v.brise_illicite[o]],
        v.richesse, v.piece,
        [[o, bool(v.refuse(retour["a"], o))] for o, retour in
         monde.data.get("restitutions", {}).get(id, {}).items() if o in monde.objets],
        # Ce qu'une source allumée ou posée depuis apporte devant un objet où il a vu la lumière.
        [[o, v.apport(o)] for o in v.connus if "lumiere" in croyances.get(o, ())],
        # L'eau qu'il attend : où elle menace, où il l'attend noyée (``eau.attendue``).
        sorted(v.menacees), sorted(v.noyees), v.monte, v.eau_route, pnj.DUREES,
        # Le coût du noir ; le but explicite de lumière est dans la partie propre
        # au candidat. Les autres emplois se découvrent dans les gestes.
        # La discrétion lit les gardes des mêmes suites : permissions, capacités,
        # visées, refus, moyens et admissibilité sont déjà couverts ci-dessus.
        v.peur,
        # La suite estimée lit les mêmes routes, possessions, refus et gestes ;
        # ses pressions restent celles de la vue, y compris les menaces sociales.
        # La borne du séjour ne lit que salles, prix_gardes (ci-dessus) et eau.
        "part-estimee:trajet-geste", v.eau, v.peurs_sociales, v.taux_mefiance, v.dangers,
        # Modèle de trajet et positions crues des cibles/obstacles, jamais le départ réel.
        ([metrique, "trajet-estime:entrees-v1",
          [[s, d["lieu"].get("salle"), d["lieu"].get("case")] for s, d in croyances.items()
           if "lieu" in d]], bool(monde.data.get("mode_cases"))),
        [[k, o.get("position"), o.get("position_salle"), o.get("positions_salles")]
         for k, o in monde.objets.items() if not o.get("mobile") and o["type"] != "personnage"]
        ], ensure_ascii=False, check_circular=False)


def _ordre_visites(salles, visites):
    """La recherche ne lit que l'ordre et les égalités des dates (``_chercher``)."""
    dates = sorted({visites.get(s, -1) for s in salles})
    rangs = {date: rang for rang, date in enumerate(dates)}
    return {s: rangs[visites.get(s, -1)] for s in salles}


def chercher(monde, id, but, vises=None, depuis=None, profondeur=PROFONDEUR, noeuds=NOEUDS, nom="", memo=None,
             emplois=None, motif=None, tenir=False, endurer=None, seul=None):
    """Le plan le moins coûteux vers ``but`` (une fonction de la vue et de l'état), ou None,
    depuis l'état ``depuis`` (par défaut, ce qu'il croit maintenant). ``nom`` désigne le but
    dans les diagnostics.

    ``emplois`` dit ce que le but peut employer : "manger" (un repas), "feu" (un feu à charger,
    allumer). Il borne ce qu'il vaut la peine de porter (``Vue.pertinent``) ; None : tout. Il ne fait
    que retirer : ce que le but demande lui-même se lit de ``vises`` (``"eclairer"`` : avoir de la
    lumière, ``Vue.eclairer``), pour que la recherche complète du même but (``VERIFIER``) offre tous
    les gestes de la restreinte.

    ``memo`` (une description JSON du but, qui le détermine avec ce qu'il croit) garde le
    résultat : tant que rien de ce que lit la recherche n'a changé (``_entrees``), le même but
    rend le même résultat sans refaire la recherche.

    Le coût est en minutes ; chaque personne lésée y ajoute le prix d'une faute, selon son
    honnêteté et la détresse du besoin ``motif`` (``caractere.prix_faute``) ; une faute qu'il
    n'envisage pas écarte le geste. Renvoie (coût, étapes, état final).

    ``tenir`` : le but se tient en restant (``_explorer``). ``endurer`` (un gain, en minutes, ou
    None) : s'il ne s'y tient pas déjà, il n'y va que si cela coûte moins que rester où il est
    (``RESTER`` minutes de ce que son état présent laisse monter, plus ce que le but lui apporte
    d'autre, ``endurer``) ; sinon il endure, et rien n'est rendu.

    ``seul`` : servir soi-même. Le commanditaire peut fournir des moyens ; le bien
    même à livrer ou servir peut être demandé à son porteur. Aucun travail délégué,
    ni recherche d'un tiers inconnu (``TIERS``)."""
    from .caractere import modificateur, prix_faute, valeur
    if not monde.objets.get(id, {}).get("profil"):
        raise ValueError(f"chercher : acteur sans profil autonome : {id}")
    debut = perf_counter()
    v = vue(monde, id)
    v.motif = motif
    faute = prix_faute(monde, id, motif)
    v.degat = prix_faute(monde, id, motif, "douceur")
    from .deliberation import DESESPOIR
    v.desespere = lire(monde, id)["besoins"].get(motif, 0) >= DESESPOIR
    v.emplois = None if emplois is None else frozenset(emplois)
    v.eclairer = bool((vises or {}).get("eclairer"))
    v.seul = seul
    garde = graphe = None
    repris = False
    absence = False
    preuve_noeuds, preuve_issue = 0, None
    completion = None
    attente = False
    retenues = None
    if memo is not None and depuis is None:
        # Ce que la recherche lit de son caractère et de son état : l'adresse modulée qui fait la
        # chance de crocheter, la force celle de forcer ; s'il envisage d'abîmer. Les gestes et leurs
        # coûts en dépendent, non du prix d'une faute ni de celui d'abîmer (``_explorer``).
        base = (_entrees(v, vises, profondeur, noeuds),
                json.dumps([modificateur(monde, id, "DEX"), modificateur(monde, id, "FOR"), tenir, v.degat is None,
                            seul, None if v.degat is None else [
                                valeur(monde, id, "courage"), v.desespere]]))
        entrees = (base, json.dumps([faute, v.degat, endurer]))
        place = (id, json.dumps(memo, ensure_ascii=False))
        garde = _MEMOIRE.get(place)
        if garde is not None and garde[0] != entrees:
            garde = None
        signature_vide = (base, faute is None)
        # La borne n'est pas une preuve d'impossibilité. Elle épuise l'effort
        # consacré à ce recours : seuls de nouveaux moyens/lectures ou un
        # palier du besoin le réveillent, pas la seule baisse de ses prix.
        from .deliberation import BESOINS, seuils
        choix = getattr(monde, "_vues_du_choix", None)
        if choix is not None and choix[0] == id and (motif in BESOINS or motif is None):
            besoins = lire(monde, id)["besoins"]
            paliers = [[b, besoins.get(b, 0) >= seuil, besoins.get(b, 0) >= DESESPOIR]
                       for b, seuil in seuils(monde, id).items() if motif is None or b == motif]
            signature_attente = json.dumps([signature_vide, paliers],
                                           ensure_ascii=False)
            retenues = choix[2]
            attente = retenues.get(place[1]) == signature_attente
            if attente:
                garde = (entrees, None, "attente", True)
            else:
                retenues.pop(place[1], None)
        vide_garde = _IMPOSSIBLES.get(place)
        if garde is None and vide_garde == (signature_vide, True):
            garde = (entrees, None, "impossible", False)
        absence = garde is not None and garde[2] == "impossible"
        if garde is None:
            # Le graphe n'est gardé qu'à la deuxième recherche de suite sur les mêmes entrées : celles
            # qui changent à chaque fois n'en encombrent pas la mémoire.
            vu = _GRAPHES.get(place)
            if vu is None or vu[0] != base:
                # Retenir dès la première recherche la découverte, sans garder
                # tous les nœuds des entrées qui ne reviendront jamais.
                graphe = {"garder": False, "discretion": False}
                _GRAPHES[place] = (base, graphe)
            elif vu[1] is None:
                graphe = {}
                _GRAPHES[place] = (base, graphe)
            else:
                graphe = vu[1]
                repris = graphe.get("garder", True)
                graphe["garder"] = True
    if garde is not None:
        _, trouve, issue, borne = garde
        examines = etats = plus_profond = 0
    else:
        voir = v.emploie_lumiere   # avant toute lecture : le graphe où la recherche commence (``_explorer``)
        trouve, examines, etats, plus_profond = _explorer(v, depuis or depart(monde, id, v), but, vises, profondeur,
                                                          noeuds, faute, tenir, graphe)
        borne = examines >= noeuds
        issue = "plan" if trouve else "borne" if borne else "epuise"
        if (trouve is None and not borne and graphe is not None and graphe.get("garder", True) and memo is not None and depuis is None
                and (vide_garde is None or vide_garde[0] != signature_vide)):
            completion = {"ajoutes": 0, "completes": 0, "enrichis": 0}
            def preparer_preuve(nom_graphe):
                return _preparer_graphe_preuve(v, depuis or depart(monde, id, v), but, vises,
                                               profondeur, tenir, graphe.get(nom_graphe, {}),
                                               nom_graphe == "sombre", completion)
            vide, preuve_noeuds, preuve_issue = _sans_plan(
                v, depart(monde, id, v), but, profondeur, faute, tenir, graphe, voir,
                preparer=preparer_preuve)
            _IMPOSSIBLES[place] = (signature_vide, vide)
            if vide:
                # Le certificat suffit désormais, sans retenir tous les états développés.
                _GRAPHES[place] = (base, None)
        if endurer is not None and _endure(v, trouve, depuis, endurer):
            trouve, issue = None, "endure"
        if memo is not None and depuis is None:
            _MEMOIRE[place] = (entrees, trouve, issue, borne)
    if retenues is not None and not attente:
        if issue == "borne" and trouve is None:
            retenues[place[1]] = signature_attente
        else:
            retenues.pop(place[1], None)
    if VERIFIER:
        _verifier(monde, id, v, but, vises, depuis, profondeur, noeuds, faute, tenir, endurer, seul, nom,
                  trouve, borne, "impossibilité" if absence else "mémoire" if garde is not None else "graphe" if repris else "borne")
    # Une seule liste publique, indépendante du graphe et de la mémoire, même
    # dans les contenus imbriqués. Le résultat interne reste immuable.
    rendu = None if trouve is None else (trouve[0], [_degeler_etape(x) for x in trouve[1]], trouve[2])
    if DIAGNOSTIC is not None:
        DIAGNOSTIC.append({"minute": monde.data["minutes"], "pnj": id, "but": nom, "noeuds": examines,
                           "etats": etats, "profondeur": plus_profond, "issue": issue, "memoire": garde is not None,
                           "graphe": repris and garde is None, "etapes": len(trouve[1]) if trouve else None,
                           "impossible": absence, "preuve_noeuds": preuve_noeuds, "preuve_issue": preuve_issue,
                           "devis_differes": v._devis_differes, "devis_developpes": v._devis_developpes,
                           "duree": round(perf_counter() - debut, 6)})
        if completion is not None:
            DIAGNOSTIC[-1].update({"preuve_" + k: x for k, x in completion.items()})
    return rendu


# Nœuds de la recherche de référence de ``VERIFIER`` : elle explore tout ce qu'il connaît, plus que la
# recherche restreinte qu'elle contrôle ; bornée comme elle, elle s'arrêterait avant l'optimum.
REFERENCE = 15 * NOEUDS


def _egaux(a, b):
    """Deux résultats de même coût (à l'arrondi des sommes près), ou tous deux sans plan."""
    if a is None or b is None:
        return a is None and b is None
    return abs(a[0] - b[0]) <= 1e-9 * max(1.0, abs(a[0]))


def _verifier(monde, id, v, but, vises, depuis, profondeur, noeuds, faute, tenir, endurer, seul, nom, trouve, borne,
              reprise):
    """``VERIFIER`` : deux contrôles, chacun avec sa référence.

    Repris de la mémoire ou du graphe (``reprise``), le résultat doit être exactement celui d'une
    recherche uniforme refaite de zéro avec les mêmes paramètres (mêmes gestes, même plafond) :
    même plan, mêmes égalités. Si cette référence atteint son plafond, un autre résultat n'est
    permis que s'il égale le coût de la complète à ``REFERENCE`` ; il est noté dans ``BORNES``.

    Cherché parmi ce qu'il vaut la peine de porter (``emplois``), il doit avoir le coût de l'optimum
    d'une recherche complète pour le même but (``emplois`` à None, mêmes gestes propres au but :
    ``Vue.eclairer``), bornée à ``REFERENCE`` nœuds. Le coût, pas le plan : les deux recherches
    n'examinent pas les mêmes gestes, l'ordre de découverte qui départage deux plans de même coût
    diffère donc nécessairement. Une recherche qui atteint sa borne n'est pas un optimum : si la
    restreinte l'atteint, l'écart n'est pas un défaut de la restriction mais une limite de la recherche
    jouée : il est noté (``BORNES``), pas tenu pour faux ;
    si la référence l'atteint, la restreinte doit seulement ne pas coûter plus qu'elle."""
    def refaire(emplois, borne):
        brute = Vue(monde, id)
        # Même photographie du monde : géométrie et tarifs ne dépendent ni du
        # but ni des emplois. Découvertes et graphe de référence restent privés.
        for nom_table in ("_contextes_routes", "_contextes_pressions", "_parcours", "_routes", "_allers",
                          "_approches", "_contacts", "_locaux", "_moyennes", "_effets_routes",
                          "_tarifs_routes", "_mesures_allers"):
            setattr(brute, nom_table, getattr(v, nom_table))
        brute.degat, brute.seul, brute.emplois, brute.eclairer = v.degat, seul, emplois, v.eclairer
        brute.motif = v.motif
        brute.desespere = v.desespere
        r = _explorer(brute, depuis or depart(monde, id, brute), but, vises, profondeur, borne, faute, tenir,
                      differer=False, borner=False, decouvrir_discretion=False)
        refait = r[0]
        if endurer is not None and _endure(brute, refait, depuis, endurer):
            refait = None
        return refait, r[1] >= borne
    divergence_bornee = False
    if reprise is not None:
        refait, refait_borne = refaire(v.emplois, noeuds)
        divergence_bornee = refait != trouve and refait_borne
        assert refait == trouve or divergence_bornee, (
            f"Recherche de {id} ({nom}, {reprise}) : {trouve} au lieu de {refait}")
        if reprise == "impossibilité":
            # La preuve évite même la recherche bornée : seul le recalcul de contrôle connaît
            # le nombre de nœuds qu'elle aurait effectivement examinés avec ces nouveaux prix.
            borne = refait_borne
    if v.emplois is None and not divergence_bornee and reprise != "impossibilité":
        return
    refait, reference_bornee = refaire(None, REFERENCE)
    if reprise == "impossibilité":
        assert trouve is None and refait is None, (
            f"Recherche de {id} ({nom}, certificat, complète) : {trouve} au lieu de {refait}")
        if reference_bornee:
            BORNES.append({"minute": monde.data["minutes"], "pnj": id, "but": nom,
                           "trouve": None, "optimum": None, "certificat_reference_bornee": True})
        return
    if divergence_bornee:
        assert _egaux(refait, trouve), (
            f"Recherche de {id} ({nom}, ancienne borne, complète) : {trouve} au lieu de {refait}")
        BORNES.append({"minute": monde.data["minutes"], "pnj": id, "but": nom,
                       "trouve": None if trouve is None else trouve[0],
                       "optimum": None if refait is None else refait[0], "ancienne_borne": True})
        return
    if borne:
        if refait is not None and (trouve is None or refait[0] < trouve[0]):
            BORNES.append({"minute": monde.data["minutes"], "pnj": id, "but": nom,
                           "trouve": None if trouve is None else trouve[0], "optimum": refait[0]})
        return
    if reference_bornee:
        assert trouve is not None or refait is None, (
            f"Recherche de {id} ({nom}, emplois, référence bornée) : {trouve} au lieu de {refait}")
        assert refait is None or trouve[0] <= refait[0] + 1e-9 * max(1.0, abs(refait[0])), (
            f"Recherche de {id} ({nom}, emplois, référence bornée) : {trouve} au lieu de {refait}")
        return
    assert _egaux(refait, trouve), f"Recherche de {id} ({nom}, emplois) : {trouve} au lieu de {refait}"


def _endure(v, trouve, depuis, gain):
    """Le plan trouvé lui coûte-t-il autant que de rester où il est, avec ce que son état présent
    laisse monter, plus le ``gain`` que le but apporte d'autre ? Il ne s'y tient pas déjà (le plan
    a des étapes)."""
    return bool(trouve and trouve[1]) and trouve[0] >= RESTER * v.pression(depuis or depart(v.monde, v.id, v)) + gain


def _explorer(v, depart_, but, vises, profondeur, noeuds, faute, tenir=False, graphe=None, *, differer=True,
              borner=True, decouvrir_discretion=True):
    """Découvrir les moyens que le but et ses gestes emploient, puis chercher.

    Une lecture de lumière dans un état sombre révèle ce que la lumière peut
    changer. Si des sources avaient été écartées, la recherche est reprise avec
    ces moyens, depuis son départ et avec sa borne entière : l'ordre des plans
    ne dépend pas de l'ordre où les objets ont fait découvrir cette lecture.

    La découverte dépend de l'ordre d'exploration, donc du prix d'une faute, que le graphe
    repris ne fixe pas : il garde deux graphes, sans les moyens d'éclairer (``sombre``) et
    avec (``lumiere``), chacun ne dépendant que des entrées, et chaque nœud du premier retient
    si l'examiner a lu la lumière. Repris, il rejoue la découverte telle qu'une recherche
    neuve la ferait avec ce prix-là (``_explorer_etats``).

    La garde d'un geste admissible découvre aussi le besoin de discrétion.
    Les deux départs sont alors repris ensemble, puis cette possibilité est
    retenue par PNJ/but sous les entrées du graphe, indépendamment des prix.
    ``decouvrir_discretion=False`` ne sert qu'au témoin historique de VERIFIER.
    """
    v._depart_estimation = depart_
    v._contexte_parts = (but, json.dumps(vises, sort_keys=True, ensure_ascii=False))
    sombre = lumineux = None
    if graphe is not None and graphe.get("garder", True):
        sombre, lumineux = graphe.setdefault("sombre", {}), graphe.setdefault("lumiere", {})
    v._explore_furtif = bool(graphe and graphe.get("discretion"))
    v._decouvrir_discretion = decouvrir_discretion
    if not decouvrir_discretion:
        # Témoin historique de VERIFIER : les deux allures dès qu'une faute
        # est autorisée, même sans geste offert qui puisse en avoir besoin.
        v._explore_furtif = (any(v.illicite[o] and v.autorise[o] for o in v.connus)
                             or v.degat is not None and any(v.violence(x) is not None for x in v.personnes()))
    v._discretion_lue = v._explore_furtif
    lumiere_initiale = v._lumiere_lue
    voir = v.emploie_lumiere
    resultat = _explorer_etats(v, depart_, but, vises, profondeur, noeuds, faute, tenir,
                               lumineux if voir else sombre, decouvrir=not voir, differer=differer, borner=borner)
    if not voir and v.emploie_lumiere and not (v._discretion_lue and not v._explore_furtif):
        v._agissables.clear()
        resultat = _explorer_etats(v, depart_, but, vises, profondeur, noeuds, faute, tenir, lumineux,
                                   differer=differer, borner=borner)
    if v._discretion_lue and not v._explore_furtif:
        # Un plan discret marche feutré depuis le départ : reprise entière,
        # même plafond et même ordre, y compris la découverte de lumière.
        if graphe is not None:
            graphe["discretion"] = True
        v._explore_furtif = True
        v._lumiere_lue = lumiere_initiale
        v._agissables.clear()
        resultat = _explorer_etats(v, depart_, but, vises, profondeur, noeuds, faute, tenir,
                                   lumineux if voir else sombre, decouvrir=not voir, differer=differer, borner=borner)
        if not voir and v.emploie_lumiere:
            v._agissables.clear()
            resultat = _explorer_etats(v, depart_, but, vises, profondeur, noeuds, faute, tenir, lumineux,
                                       differer=differer, borner=borner)
    return resultat


def _departs(v, e):
    # L'exécution marche à pas feutrés dès le début d'un plan comportant un
    # geste sans témoin. Les deux allures sont donc des états initiaux, pas un
    # supplément découvert trop tard au moment de la faute.
    if getattr(v, "_cru_spatial", None) is None:
        return [e]
    if getattr(v, "_explore_furtif", False):
        return [e.apres(allure=15), e.apres(allure=30)]
    return [e]


class _ListeEtape(tuple):
    """Liste gelée, distinguée des tuples pour restituer exactement le contrat public."""
    __slots__ = ()


def _figer_etape(x):
    if isinstance(x, dict):
        return MappingProxyType({k: _figer_etape(v) for k, v in x.items()})
    if isinstance(x, list):
        return _ListeEtape(_figer_etape(v) for v in x)
    if isinstance(x, tuple):
        return tuple(_figer_etape(v) for v in x)
    return x


def _degeler_etape(x):
    if isinstance(x, MappingProxyType):
        return {k: _degeler_etape(v) for k, v in x.items()}
    if isinstance(x, _ListeEtape):
        return [_degeler_etape(v) for v in x]
    if isinstance(x, tuple):
        return tuple(_degeler_etape(v) for v in x)
    return x


def _reconstruire_etapes(maillon):
    """Ne parcourir les préfixes que pour le gagnant ; geler ses seules étapes.

    Les ajouts des suites appartiennent au graphe et se lisent sans mutation.
    Les maillons (parent, ajout) ne copient aucun préfixe. Le résultat gelé ne
    partage aucun dictionnaire ni liste avec les suites ou avec l'appelant.
    """
    ajouts = []
    while maillon is not None:
        maillon, ajout = maillon
        ajouts.append(ajout)
    return tuple(_figer_etape(x) for ajout in reversed(ajouts) for x in ajout)


def _explorer_etats(v, depart_, but, vises, profondeur, noeuds, faute, tenir=False, graphe=None,
                    decouvrir=False, *, differer=True, borner=True):
    """Recherche du moindre coût sur les états crus : (trouvé ou None, nœuds examinés, états vus,
    profondeur atteinte). ``faute`` : le prix d'une personne lésée, None s'il ne l'envisage pas.

    ``tenir`` : le but se tient en restant là où il mène (la lumière, ses biens, le feu, l'abri) ;
    y rester ``RESTER`` minutes compte, avec ce que l'état final laisse monter (``Vue.pression``).
    Un état qui atteint le but s'explore encore : plus loin, un autre peut le tenir à moindre prix
    (rapporter une lanterne là où il garde ses biens).

    ``graphe`` (un dictionnaire, ou None pour n'en rien garder) garde, pour chaque état développé,
    s'il atteint le but, ce qu'il laisse monter et ses gestes avec chaque terme de leur coût
    (``_suites``). Ils ne dépendent que de ce que lit la recherche (``_entrees``), pas du prix d'une
    faute ni de celui d'abîmer, qui n'entrent qu'ici, dans la même somme : repris d'une recherche à
    l'autre, le graphe rend exactement la recherche qu'on aurait refaite, comparaisons et égalités
    comprises. Dans la passe de découverte, chaque nœud retient aussi si son but (« but ») ou ses
    gestes (« gestes ») ont lu la lumière : rejoué, il la relit au même point."""
    ordre = count()
    infini = float("inf")
    degat = v.degat
    departs = _departs(v, depart_)
    # H <= RESTER * pression(final) : gardes et eau sont fixes par salle,
    # tous les autres termes sont non négatifs. H est constant sur les états
    # ordinaires, donc H <= coût(arête) + H. Pour une suite différée, h est
    # H + suite.borne : son arête entrante coûte zéro et sa sortie terminale
    # paie au moins suite.borne + H. Aux résultats, h = 0.
    # La découverte doit garder son arrêt historique, y compris les états
    # qui auraient été évités par un meilleur ordre face aux résultats.
    sejour = v.borne_rester(depart_.salle) if borner and tenir and not decouvrir else 0
    # Une place dans l'ordre historique est réservée à chaque groupe différé.
    # Ses sorties gardent cette place et leur ordre interne, même calculées plus
    # tard : les égalités restent celles de la file en coût uniforme. Les nœuds
    # différés passent avant les vrais à priorité égale, pour révéler toutes les
    # sorties susceptibles d'égaler le meilleur prix avant de décider.
    # Le deuxième terme conserve aussi le coût de file sans H : ajouter une
    # constante flottante peut arrondir deux coûts distincts au même nombre.
    file = [(sejour, 0, 1, (next(ordre), 0), 0, e, None, 0, False) for e in departs]
    vus = {e: 0 for e in departs}
    examines = plus_profond = 0
    trouve = None
    # La passe de découverte (``decouvrir``) n'a plus rien à apprendre dès la première lecture de
    # lumière : seule la passe suivante, avec les moyens d'éclairer, décidera du plan. Ses nœuds
    # restent justes pour la rejouer (le cinquième terme : où elle a lu la lumière).
    while (file and examines < noeuds and not (decouvrir and v._lumiere_lue)
           and not (getattr(v, "_discretion_lue", False) and not v._explore_furtif)):
        _, _, _, rang, cout, e, etapes, n, final = heapq.heappop(file)
        if isinstance(final, SuiteDifferee):
            for i, (fautes, minutes, ajout, suivant, _, abime, _) in enumerate(final.developper(v)):
                if fautes and faute is None:
                    continue
                if ((suivant.allure == 15 or suivant.fait("furtif"))
                        and (not tenir or suivant.salle not in v.menacees)):
                    total = cout + fautes * (faute or 0) + ((degat or 0) * abime if abime else 0) + minutes
                    total += RESTER * v.pression(suivant) if tenir else 0
                    heapq.heappush(file, (total, total, 1, (rang[0], i), total,
                                         suivant, (etapes, ajout), n + 1, True))
            continue
        if final:
            trouve = cout, _reconstruire_etapes(etapes), e
            break
        if vus.get(e, infini) < cout:
            continue
        examines += 1
        plus_profond = max(plus_profond, n)
        noeud = None if graphe is None else graphe.get(e)
        if noeud is None:
            noeud = [but(v, e) and (e.allure == 15 or e.fait("furtif")), None, None, None, False]
            if graphe is not None:
                graphe[e] = noeud
        elif noeud[4] == "but":
            v._lumiere_lue = True   # le but y a lu la lumière quand il fut examiné
        if decouvrir and v._lumiere_lue and not noeud[4]:
            noeud[4] = "but"   # rejoué, ce nœud refera la même découverte
        if noeud[0] and not (tenir and e.salle in v.menacees):
            # Un but qui se tient en restant ne se tient pas là où il croit ou attend l'eau.
            if not tenir:
                trouve = cout, _reconstruire_etapes(etapes), e
                break
            if noeud[1] is None:
                noeud[1] = v.pression(e)
            total = cout + RESTER * noeud[1]
            heapq.heappush(file, (total, total, 1, (next(ordre), 0), total, e, etapes, n, True))
        if n >= profondeur:
            continue
        if noeud[3] is None:
            # Une flamme allumée par le plan se consume : on l'allume le plus tard possible.
            noeud[2] = sum(1 for k in e.portes if e.fait("allume", k))
            noeud[3] = _suites(v, e, vises, but)
            if decouvrir and v._lumiere_lue and not noeud[4]:
                noeud[4] = "gestes"
        elif noeud[4] == "gestes":
            v._lumiere_lue = True   # ses gestes y ont lu la lumière : seulement s'il les développe
        en_feu = noeud[2]
        suites = noeud[3]
        if decouvrir or not differer:
            # La lecture de lumière définit les moyens offerts à la deuxième
            # passe : elle doit se produire au point historique, avant tout tri.
            suites = [g for s in suites for g in (s.developper(v) if isinstance(s, SuiteDifferee) else [s])]
            if decouvrir and v._lumiere_lue and not noeud[4]:
                noeud[4] = "gestes"
        for suite in suites:
            if isinstance(suite, SuiteDifferee):
                v._devis_differes += 1
                heapq.heappush(file, (cout + suite.borne + sejour, cout + suite.borne, 0, (next(ordre), 0), cout,
                                     e, etapes, n, suite))
                continue
            fautes, minutes, ajout, suivant, duree, abime, pression = suite
            if fautes and faute is None:
                continue
            surcout = (degat or 0) * abime if abime else 0   # un prix qui n'est pas du temps (abîmer)
            estime = suivant.fait("estimation")
            total = cout + fautes * (faute or 0) + surcout + minutes
            if not estime:
                total += duree * FLAMME_EN_MAIN * en_feu
            if duree:
                total += duree * pression  # Le temps qu'il passe dans le noir, ou loin de ses biens.
            if estime:
                if (suivant.allure == 15 or suivant.fait("furtif")) and (not tenir or suivant.salle not in v.menacees):
                    total += RESTER * v.pression(suivant) if tenir else 0
                    heapq.heappush(file, (total, total, 1, (next(ordre), 0), total,
                                         suivant, (etapes, ajout), n + 1, True))
            elif total < vus.get(suivant, infini):
                vus[suivant] = total
                heapq.heappush(file, (total + sejour, total, 1, (next(ordre), 0), total,
                                     suivant, (etapes, ajout), n + 1, False))
    return trouve, examines, len(vus), plus_profond


def _suites(v, e, vises, but, conclure=False):
    """Les gestes depuis ``e`` qui mènent quelque part, chacun avec les termes de son coût : (fautes,
    minutes, étapes, état suivant, durée, abîme, ce que l'état suivant laisse monter par minute)."""
    return _normaliser_suites(v, e, vises, but, gestes(v, e, vises, but), conclure)


def _normaliser_suites(v, e, vises, but, possibles, conclure=False):
    """Même contrat pour les gestes immédiats et les suites révélées à leur borne."""
    suites = []
    for geste in possibles:
        if isinstance(geste, SuiteDifferee):
            suites.append(geste)
            continue
        fautes, minutes, ajout, suivant = geste[:4]
        furtif = any(x.get("condition") in ("sans_temoin", "dans_le_dos") for x in ajout)
        if (furtif and e.allure != 30 and getattr(v, "_cru_spatial", None) is not None
                and (getattr(v, "_explore_furtif", False) or not getattr(v, "_decouvrir_discretion", True))):
            continue   # filtre historique ; seule la découverte lit les gardes suivantes
        if furtif:
            suivant = suivant.apres(faits=[(("furtif",), True)])
        decouvre_furtif = furtif and e.allure != 30 and getattr(v, "_cru_spatial", None) is not None
        lumiere = v._lumiere_lue if decouvre_furtif else None
        try:
            # Le devis a déjà évalué les trajets entre salles ; ne calculer ici que
            # ses gestes conclusifs, avant leurs pressions coûteuses.
            if conclure and (any(x["operation"] == "aller" for x in ajout) or not but(v, suivant)):
                continue
            if v.seul and any(x["operation"] in TIERS and (x["operation"] not in ("demander", "acheter")
                              or x["cible"] != v.seul and x["outil"] not in
                              (*vises.get("prendre", ()), *vises.get("servir", ())))
                              or (x.get("contenu") or {}).get("cherche") not in (None, v.seul) for x in ajout):
                continue   # Acquisition du bien visé permise, travail délégué exclu.
            # Écarter les effets terminaux inutiles avant de mesurer leur approche.
            if (len(suivant.faits) > len(e.faits) and any(cle[0] in TERMINAUX and cle not in e.faits for cle in suivant.faits)
                    and not but(v, suivant)):
                continue
        finally:
            if decouvre_furtif:
                # Ces lectures n'existent pas dans l'allure ordinaire historique.
                # Seule la reprise feutrée doit les faire découvrir à la lumière.
                v._lumiere_lue = lumiere
        if furtif and getattr(v, "_cru_spatial", None) is not None:
            if getattr(v, "_decouvrir_discretion", True):
                v._discretion_lue = True
            if e.allure != 30:
                continue
        duree = geste[4] if len(geste) > 4 else minutes
        if isinstance(geste, TransitionMesuree):
            pression = geste[6]
        elif ajout and not suivant.fait("estimation"):
            mesure = _mesurer(v, e, ajout, suivant, duree)
            if mesure is None:
                continue
            temps, pression, suivant = mesure
            minutes += temps - duree
            duree = temps
        else:
            pression = duree * v.pression(e) if duree else 0
        suites.append((fautes, minutes, ajout, suivant, duree, geste[5] if len(geste) > 5 else False,
                       pression / duree if duree else 0))
    return suites


def _mesurer(v, e, ajout, suivant, ancienne_duree):
    """Lire l'arête entre salles ; composer directement les autres séquences."""
    if v._cru_spatial is not None and len(ajout) == 1 and ajout[0]["operation"] == "aller":
        mesure = v.mesure_aller(e, ajout[0]["lieu"])
        if mesure is None:
            return None
        temps, pression, portes = mesure
        # Une mesure garde les portes connues, pas seulement ses écritures.
        # Composer uniquement les changements effectifs ; les autres faits et
        # l'état destinataire restent partagés, sans recopier tout le plan.
        changements = [(k, x) for k, x in portes
                       if suivant.faits.get(k) == e.faits.get(k)
                       and (k not in suivant.faits or suivant.faits[k] != x)]
        return temps, pression, suivant.apres(faits=changements) if changements else suivant
    return _mesurer_direct(v, e, ajout, suivant, ancienne_duree)


def _mesurer_direct(v, e, ajout, suivant, ancienne_duree):
    """Approches estimées, portes et gestes aux tarifs communs d'exécution.

    Les coûts sociaux restent séparés du temps. Une probabilité multiplie les
    tentatives du geste, jamais la marche d'approche.
    """
    DUREES, DURABLES, TOUR = pnj.DUREES, pnj.DURABLES, pnj.TOUR
    if any(x["operation"] not in (*DUREES, *DURABLES, "aller", "assommer", "dans_le_dos", "fuite")
                                      for x in ajout):
        return ancienne_duree, ancienne_duree * v.pression(e), suivant
    courant, temps, pression = e, 0, 0
    for etape in ajout:
        op, cible = etape["operation"], etape["cible"]
        if op == "aller":
            route = v.route(courant, etape["lieu"])
        else:
            if any(not v.present(courant, x)
                   for x in pnj._a_toucher(v.monde, v.id, etape, courant.portes)):
                return None
            route = v.approche(courant, etape)
        if route is None:
            return None
        duree = cout_route(route, courant.orientation)
        temps += duree
        pression += v.prix_route(courant, route)
        courant = v.arrivee(courant, etape["lieu"] if op == "aller" else courant.salle, route)
        if op == "aller":
            continue
        rotation = 2 * QUART if cible else 0
        geste = DUREES.get(op, 20) / MINUTE
        if op in DURABLES:
            # Ces buts durent et se réévaluent à la minute ; RESTER demeure
            # l'horizon de séjour, distinct de ce premier geste.
            geste = 1
        elif op == "crocheter":
            geste *= ancienne_duree
        elif op == "frapper":
            if cible == "joueur" or v.objets.get(cible, {}).get("type") == "personnage":
                geste = ancienne_duree
            else:
                geste *= ancienne_duree
        elif op == "assommer":
            geste = max(0, ancienne_duree - 1)
        elif op == "dans_le_dos":
            geste = 0
        elif op == "fuite":
            geste = 0
        geste += rotation / MINUTE
        if etape.get("condition") == "sans_temoin" and not v.desespere:
            geste += TOUR / MINUTE
        temps += geste
        pression += geste * v.pression(courant)
    if v._cru_spatial is None:
        return ancienne_duree, ancienne_duree * v.pression(e), suivant
    faits = dict(suivant.faits)
    faits.update({k: x for k, x in courant.faits.items() if k[0] in ("ouvert", "verrou")
                  and suivant.faits.get(k) == e.faits.get(k)})
    return temps, pression, suivant.apres(case=courant.case, orientation=courant.orientation, faits=faits.items())


def _preparer_graphe_preuve(original, depart_, but, vises, profondeur, tenir, source, sombre, comptes):
    """Photographie privée pour compléter les seules lectures manquantes du graphe.

    Les tarifs sont ceux de la recherche jouée. Une découverte de lumière reste
    attachée à son nœud sombre ; une discrétion nouvelle empêche de certifier ce
    graphe de départs. Ni ces découvertes ni les devis ne modifient la Vue jouée.
    """
    v = Vue(original.monde, original.id)
    for a in ("degat", "seul", "emplois", "eclairer", "motif", "desespere"):
        setattr(v, a, getattr(original, a))
    for a in ("_contextes_routes", "_contextes_pressions", "_parcours", "_routes", "_allers",
              "_approches", "_contacts", "_locaux", "_moyennes", "_effets_routes",
              "_tarifs_routes", "_mesures_allers"):
        setattr(v, a, getattr(original, a))
    v._depart_estimation = depart_
    v._contexte_parts = (but, json.dumps(vises, sort_keys=True, ensure_ascii=False))
    v._explore_furtif = original._explore_furtif
    v._decouvrir_discretion = True
    v._lumiere_lue = not sombre
    # La table de pertinence appartient à ce graphe. Un devis sombre peut
    # découvrir la lumière avant sa première lecture des gestes ; il ne doit
    # pas préparer alors une table lumineuse pour les autres nœuds sombres.
    v.agissables(vises or {})
    g = {}
    for e, noeud in source.items():
        n = list(noeud)
        if n[3] is not None:
            n[3] = [copy.copy(s) if isinstance(s, SuiteDifferee) else s for s in n[3]]
        g[e] = n

    def completer(e, n, noeud):
        v._lumiere_lue = not sombre
        v._discretion_lue = v._explore_furtif
        neuf = noeud is None
        if neuf:
            noeud = [but(v, e) and (e.allure == 15 or e.fait("furtif")), None, None, None, False]
            if sombre and v._lumiere_lue:
                noeud[4] = "but"
            g[e] = noeud
            comptes["ajoutes"] += 1
            comptes["enrichis"] += 1
        if v._discretion_lue and not v._explore_furtif:
            return noeud, "discretion"
        if (noeud[4] == "but" or noeud[0] and not (tenir and e.salle in v.menacees)
                or n >= profondeur or noeud[4] == "gestes"):
            return noeud, None
        if noeud[3] is None:
            noeud[2] = sum(1 for k in e.portes if e.fait("allume", k))
            noeud[3] = _suites(v, e, vises, but)
            comptes["completes"] += 1
            comptes["enrichis"] += not neuf
        for s in noeud[3]:
            if isinstance(s, SuiteDifferee):
                s.developper(v)
        if v._discretion_lue and not v._explore_furtif:
            return noeud, "discretion"
        if sombre and v._lumiere_lue:
            noeud[4] = "gestes"
        return noeud, None

    return v, g, completer


def _sans_plan(v, depart_, but, profondeur, faute, tenir, graphe, voir, *, preparer=None):
    """Certificat d'absence de but, indépendamment des coûts, jamais une heuristique : (prouvé,
    états examinés, issue). ``graphe`` : les deux graphes gardés de ``_explorer`` ; ``voir`` : s'il
    employait la lumière avant toute lecture (le coût du noir, la lumière comme but).

    Qui emploie la lumière dès le départ cherche sur le graphe ``lumiere`` : la preuve s'y fait.
    Sinon la recherche jouée passe d'abord sur le graphe ``sombre`` ; un état dont l'examen y a lu
    la lumière (son but, ou ses gestes s'il les développe) la fait reprendre depuis son départ avec
    les moyens d'éclairer, sur le graphe ``lumiere``, et c'est cette reprise qui décide du plan.
    Qu'un tel état soit atteignable dans le graphe sombre, un autre prix d'une faute peut l'y faire
    examiner : l'absence n'est prouvée que si le graphe ``lumiere`` la prouve aussi. Le producteur
    ``preparer`` fournit une photographie privée qui complète les seuls nœuds manquants ; sans
    producteur, le parcours reste une lecture de graphe et rend une lacune à leur rencontre."""
    def parcours(nom, examines=0):
        if preparer is None:
            return _parcours(v, graphe.get(nom, {}), depart_, profondeur, faute, tenir, examines)
        privee, g, completer = preparer(nom)
        r = _parcours(privee, g, depart_, profondeur, faute, tenir, examines, completer=completer)
        if r[2] != "discretion":
            graphe.setdefault(nom, {}).update(g)
        return r

    # Même graphe admissible et mêmes départs ; les manques sont développés
    # à leur profondeur minimale seulement si un producteur de nœuds est fourni.
    if voir:
        return parcours("lumiere")[:3]
    prouve, examines, issue, lue = parcours("sombre")
    if not prouve or not lue:
        return prouve, examines, issue
    return parcours("lumiere", examines)[:3]


def _parcours(v, graphe, depart_, profondeur, faute, tenir, examines=0, *, completer=None):
    """Parcours en largeur d'un graphe gardé : (aucun but, états examinés, issue, lumière lue).

    Un état est développé à sa profondeur minimale. Contrairement à l'épuisement d'une recherche
    pondérée (et a fortiori à sa borne), cela couvre tous les chemins autorisés de longueur au plus
    ``profondeur``. La permission de commettre une faute reste une condition ; son prix et celui
    d'abîmer ne créent aucune arête. Le producteur optionnel complète les nœuds manquants à
    leur profondeur minimale. Sans lui, un trou reste une lacune. Une rencontre du but ou
    l'atteinte du plafond de preuve (``PREUVE_MAX``, compté depuis
    ``examines``) ne conclut rien. Un état du graphe sombre dont l'examen a lu la lumière (``_explorer_etats``,
    cinquième terme) n'est pas suivi : y arriver fait reprendre la recherche avec lumière ; le
    parcours le signale."""
    from collections import deque
    departs = _departs(v, depart_)
    file, vus, lue = deque((e, 0) for e in departs), set(departs), False
    while file:
        if examines >= PREUVE_MAX:
            return False, examines, "borne", lue
        e, n = file.popleft()
        examines += 1
        noeud = graphe.get(e)
        if completer is not None:
            noeud, cause = completer(e, n, noeud)
            if cause:
                return False, examines, cause, lue
        if noeud is None:
            return False, examines, "lacune", lue
        if noeud[4] == "but":
            lue = True   # son but lit la lumière : la recherche reprendrait avec les moyens d'éclairer
            continue
        if noeud[0] and not (tenir and e.salle in v.menacees):
            return False, examines, "but", lue
        if n >= profondeur:
            continue
        if noeud[4] == "gestes":
            lue = True   # ses gestes lisent la lumière : de même, s'il les développe
            continue
        if noeud[3] is None:
            return False, examines, "lacune", lue
        suites = []
        for s in noeud[3]:
            if isinstance(s, SuiteDifferee):
                if s.suites is None:
                    return False, examines, "lacune", lue
                suites.extend(s.suites)
            else:
                suites.append(s)
        for fautes, _, _, suivant, *_ in suites:
            if fautes and faute is None:
                continue
            if suivant.fait("estimation"):
                if ((suivant.allure == 15 or suivant.fait("furtif"))
                        and not (tenir and suivant.salle in v.menacees)):
                    return False, examines, "but", lue
                continue
            if suivant in vus:
                continue
            vus.add(suivant)
            file.append((suivant, n + 1))
    return True, examines, "epuise", lue


# --- Buts ---------------------------------------------------------------------------------

def _premier(e, sorte):
    return next(((cle[1], valeur) for cle, valeur in sorted(e.faits.items(), key=str) if cle[0] == sorte), None)


def a_mange(v, e):
    # ``_premier(e, "mange") is not None``, sans trier les faits : un test de but à chaque état.
    return any(cle[0] == "mange" or cle[0] == "part" and v.monde.objets[cle[1]]["type"] == "nourriture"
               for cle in e.faits)


def rechauffe(v, e):
    return any(cle[0] == "chauffe" or cle[0] == "part" and part_pour(v.monde, v.id, cle[1], "chaleur", v.connus)
               and any(v.salle(e, f) == e.salle and v.feu(e, f)[0] and recharge(v.objets[f], v.objets[cle[1]])
                       for f in v.foyers) for cle in e.faits)


def retablir(v, e, etapes):
    """Ce qu'il garde sous clé et auquel le plan a touché, il le referme à clé avant de finir."""
    for x in profil(v.monde, v.id)["pulsions"]:
        cible = x["condition"].get("objet")
        if (not x["condition"].get("verrouillee") or not e.fait("touche", cible)
                or not refermable(e.fait("fin", cible) or v.cru(cible, "fin"))):
            continue
        if v.ouvert(e, cible):
            etapes.append(_etape("fermer", cible))
        cle = next((k for k in sorted(e.portes) if cible in v.monde.objets[k].get("ouvre", [])), None)
        if cle and (e.fait("verrou", cible) is False or _cru(v.monde, v.id, cible, "verrouillee") is not True):
            etapes.append(_etape("verrouiller", cible, outil=cle))
    return etapes


def _resultat(v, e, etapes, sorte):
    if sorte == "faim":
        mange = _premier(e, "mange")
        if mange:
            return {"type": "manger", "objet": mange[0]}, retablir(v, e, etapes)
    elif sorte == "chaleur":
        foyer = _premier(e, "chauffe")
        if foyer:
            return {"type": "chaleur", "objet": foyer[0]}, retablir(v, e, etapes)
    part = _premier(e, "part")
    return {"type": "part", "objet": part[0], "de": part[1]}, retablir(v, e, etapes)


def planifier(monde, id, besoin):
    """(but, étapes) pour apaiser la faim ou le froid, ou None."""
    but = {"faim": a_mange, "chaleur": rechauffe}[besoin]
    if besoin == "chaleur" and eau.active(monde):
        # Se chauffer demande un feu hors de l'eau (``gestes``, ``_parts``) : si chaque foyer qu'il
        # connaît est là où il croit ou attend l'eau, aucun plan ne le réchauffe ; inutile de le chercher.
        v = vue(monde, id)
        if v.foyers and all(salle_crue(monde, id, f) in v.menacees for f in v.foyers):
            return None
    # Se chauffer se tient près du feu : ce que ce lieu laisse monter compte.
    trouve = chercher(monde, id, but, nom=besoin, memo=["besoin", besoin],
                      emplois={"faim": ("manger",), "chaleur": ("feu",)}[besoin], motif=besoin,
                      tenir=besoin == "chaleur")
    if trouve is None:
        return None
    _, etapes, e = trouve
    return _resultat(vue(monde, id), e, _couper(etapes), besoin)


def _couper(etapes):
    """Arrêter avant une livraison attendue ou après un geste incertain ; replanifier sur le réel.

    Les marqueurs restent dans le résultat de recherche mémorisé : le relire ne doit pas rendre
    exécutables les gestes qui dépendent encore d'une personne ou d'une part à recevoir.
    """
    prefixe = []
    for originale in etapes:
        x = dict(originale)
        x.pop("part_estimee", None)
        if x.pop("attendre_remise", False):
            break
        suppose = x.pop("suppose", False)
        prefixe.append(x)
        if suppose:
            break
    return prefixe


def planifier_pulsion(monde, id, condition, tache=False):
    """(but, étapes) pour rétablir une pulsion (ou tenir une parole donnée), ou None.

    Une ronde : aller inspecter le lieu. Une part à servir. Un objet à remettre en place. Un feu
    à entretenir : aller le voir s'il n'en a pas de nouvelles sûres, sinon le recharger et le
    rallumer, ou demander pour lui une part de combustible à qui en possède. Un objet à garder
    sous clé : le fermer et le verrouiller. Un objet vendu : l'aller chercher, puis le remettre.

    ``tache`` : une pulsion à lui (pas une parole donnée), qu'il peut aussi payer quelqu'un de
    rétablir (``_engager``)."""
    trouve = _pulsion(monde, id, condition, tache)
    return None if trouve is None else trouve[1:]


def planifier_tache(monde, id, condition, payeur):
    """(but, étapes) pour tenir la parole donnée à ``payeur``, ou None : le plan de son devis
    (``devis_pulsion``), celui sur lequel il l'a acceptée et sur lequel il la jugerait impossible
    (``echanges.empeche``)."""
    trouve = _pulsion(monde, id, condition, False, entretenir=payeur)
    return None if trouve is None else trouve[1:]


def planifier_engagement(monde, id, engagement):
    """Tenir sa parole par le plan du devis, ou rejoindre l'autre pour lui annoncer son abandon."""
    if engagement.get("annule"):
        chemin = rejoindre(monde, id, engagement["pour"])
        if chemin is None:
            return None
        etapes, trouve = chemin
        if trouve:
            etapes.append(_etape("dire", engagement["pour"], contenu={"annulation": engagement["condition"]}))
        return {"type": "prevenir", "qui": engagement["pour"]}, etapes
    return planifier_tache(monde, id, engagement["condition"], engagement["pour"])


def devis_pulsion(monde, id, condition, payeur):
    """(coût, étapes) de rétablir ``condition`` (minutes de son plan, fautes comprises), ou None s'il
    ne voit pas comment : ce qu'une tâche qu'on lui propose lui coûterait (``echanges.engager``). Un
    feu qu'on le paie d'entretenir, il le compte à recharger et rallumer, pas seulement à aller
    voir : celui qui le paie le sait à entretenir. Par ses seuls moyens, ce que la garde du bien de
    ``payeur`` lui permet et les biens que ``payeur`` lui remettrait : il ne compte sur personne
    pour accomplir le service à sa place (ni part servie, ni feu allumé par un autre)."""
    if not monde.objets.get(id, {}).get("profil"):
        raise ValueError(f"devis_pulsion : acteur sans profil autonome : {id}")
    trouve = _pulsion(monde, id, condition, False, entretenir=payeur)
    return None if trouve is None else (trouve[0], trouve[2])


def _pulsion(monde, id, condition, tache, entretenir=None):
    """(coût, but, étapes) de ``planifier_pulsion``, ou None."""
    from .deliberation import salle_crue
    from .echanges import tache as sorte
    o = condition.get("objet")
    if "rendre" in condition:
        trouve = _rendre(monde, id, o, condition)
        return None if trouve is None else (0, *trouve)
    if "remettre" in condition:
        if entretenir:
            return _devis_remise(monde, id, o, condition, entretenir)
        trouve = _remettre(monde, id, o, condition, seul=entretenir)
        return None if trouve is None else (0, *trouve)
    if "periode" in condition:
        lieu = condition["lieu"]
        but, vises = (lambda v, e: e.fait("inspecte", lieu)), {"inspecter": (lieu,)}
    elif "servir" in condition:
        but, vises = (lambda v, e: e.fait("servi", o)), {"servir": {o: (condition["servir"],)}}
    elif "allume" in condition:
        etat = _cru(monde, id, o, "etat") or {}
        salle = salle_crue(monde, id, o)
        if salle is None:
            return None
        if not entretenir and (not etat or etat.get("allume") and not etat.get("faible")):
            # Vu vif il y a longtemps, ou jamais vu : il va voir où il en est.
            but, vises = (lambda v, e: e.fait("inspecte", salle)), {"inspecter": (salle,)}
        else:
            # Le recharger et le rallumer, de son bois ou de celui de personne, emprunté, ou d'une
            # part demandée à qui en possède : le donneur entretient alors ce feu (``gestes``).
            but, vises = (lambda v, e: v.feu(e, o) == (True, True)), {"entretenir": (o,)}
            if tache:
                vises["confier"] = (dict(condition),)
    elif "lieu" in condition:
        lieu = condition["lieu"]
        if o == id:
            # Se rendre soi-même sur place est une marche, jamais une prise de
            # personnage. Le devis et l'engagement emploient le même graphe.
            but = lambda v, e: e.salle == lieu  # noqa: E731
            vises = {}
        else:
            but = lambda v, e: o not in e.portes and v.lieu(e, o) == lieu  # noqa: E731
            vises = {"prendre": (o,), "poser": (o,)}
    else:
        if not refermable(_cru(monde, id, o, "fin")):
            return None
        but = lambda v, e: v.verrouille(e, o) and not v.ouvert(e, o)  # noqa: E731
        vises = {"fermer": (o,)}
    if tache and sorte(condition) and "allume" not in condition:
        vises["confier"] = (dict(condition),)
    depuis = None
    if entretenir and "allume" in condition and _vu_avant_la_tache(monde, id, condition, entretenir):
        # Celui qui le paie le sait à recharger, et éteint s'il ne le croit pas allumé (l'offre le dit) :
        # il le compte comme tel, quoi qu'il en ait vu avant que la tâche ne lui soit payée ; ce qu'il en
        # voit ensuite (qu'il l'a rechargé, rallumé lui-même), il le croit.
        dit = (_cru(monde, entretenir, o, "etat") or {}) if entretenir != "joueur" else {}
        depuis = depart(monde, id).apres(faits=[(("charge", o), False)]
                                         + ([] if dit.get("allume") else [(("allume", o), False)]))
    trouve = chercher(monde, id, but, vises, depuis=depuis, nom=_nom_condition(condition),
                      memo=["pulsion", condition, "confier" in vises, entretenir],
                      emplois=("feu",) if "allume" in condition else (), seul=entretenir or None)
    if trouve is None:
        return None
    cout, etapes, e = trouve
    return cout, {"type": "pulsion", **condition}, retablir(vue(monde, id), e, _couper(etapes))


def _vu_avant_la_tache(monde, id, condition, payeur):
    """L'état du feu qu'il croit date-t-il d'avant la tâche que ``payeur`` lui paie (ou n'en croit-il
    rien) ? La tâche date de son engagement ; à l'offre, de maintenant. Ce qu'il a vu ou constaté de
    sa main à cette minute même (les croyances sont datées à la minute) est de son temps ; un savoir ou
    un ouï-dire de cette minute ne dit rien de plus que l'offre."""
    debut = next((x["minute"] for x in agendas.en_cours(monde, id)
                  if x["pour"] == payeur and x["condition"] == condition and not x.get("annule")), monde.data["minutes"])
    etat = lire(monde, id)["croyances"].get(condition["objet"], {}).get("etat")
    return etat is None or etat["minute"] < debut or etat["minute"] == debut and etat["source"] not in ("vu", "essai")


def _nom_condition(c):
    sorte = ("ronde" if "periode" in c else "servir" if "servir" in c else "feu" if "allume" in c
             else "rendre" if "rendre" in c else "remettre" if "remettre" in c else "placer" if "lieu" in c
             else "sous_cle")
    return f"{sorte}:{c.get('objet') or c.get('lieu')}"


def _rendre(monde, id, o, condition):
    """Un objet prêté qui ne lui sert plus (``echanges.necessaire``) : rejoindre son propriétaire
    et le lui rendre."""
    from .echanges import necessaire
    if not porte_par(monde, o, id) or necessaire(monde, id, o):
        return None
    chemin = rejoindre(monde, id, condition["rendre"])
    if chemin is None:
        return None
    etapes, trouve = chemin
    if trouve:
        etapes.append(_etape("remettre", condition["rendre"], outil=o))
    return {"type": "pulsion", **condition}, etapes


def _devis_remise(monde, id, o, condition, seul):
    """Acquisition et livraison chiffrées ensemble, comme tout autre service."""
    trouve = chercher(monde, id, lambda v, e: o in e.portes and e.salle == v.salle(e, condition['remettre']),
                      {'prendre': (o,)}, nom='remettre:' + o,
                      memo=['remettre', o, condition['remettre']], emplois=(), seul=seul)
    if trouve is None:
        return None
    remise = _etape('remettre', condition['remettre'], outil=o)
    v = vue(monde, id)
    mesure = _mesurer(v, trouve[2], [remise], trouve[2], 1)
    if mesure is None:
        return None
    cout = trouve[0] + mesure[0] + mesure[1]
    return cout, {'type': 'pulsion', **condition}, _couper(trouve[1]) + [remise]


def _remettre(monde, id, o, condition, seul=None):
    """Un objet qu'il a vendu sans le porter (``echanges.differee``) : l'aller chercher, puis
    rejoindre l'acheteur et le lui remettre."""
    if seul:
        trouve = _devis_remise(monde, id, o, condition, seul)
        return None if trouve is None else trouve[1:]
    if not porte_par(monde, o, id):
        trouve = chercher(monde, id, lambda v, e: o in e.portes, {"prendre": (o,)}, nom="remettre:" + o,
                          memo=["remettre", o], emplois=())
        if trouve is None:
            return None
        return {"type": "pulsion", **condition}, _couper(trouve[1])
    chemin = rejoindre(monde, id, condition["remettre"])
    if chemin is None:
        return None
    etapes, trouve = chemin
    if trouve:
        etapes.append(_etape("remettre", condition["remettre"], outil=o))
    return {"type": "pulsion", **condition}, etapes


def enrichir(monde, id):
    """But et étapes d'une acquisition de pièces, d'après son devis commun."""
    resultat = devis_enrichissement(monde, id)
    return resultat[1:] if resultat else None


def devis_enrichissement(monde, id):
    """(coût, but, étapes) pour prendre des pièces (un objet qu'il croit en contenir, qui n'est pas à lui)
    qui valent pour lui plus que ce qu'il en coûte d'aller les prendre, faute comprise ; None sinon.
    L'argent ne presse jamais : aucune détresse n'use le prix de la faute (``caractere.ARGENT``).

    Il compte les pièces qu'il croit dedans (croyance ``pieces`` : su en la tenant, ou un savoir
    du scénario), jamais celles qui y sont : une bourse dont il ne sait rien ne le tente pas."""
    from .caractere import ARGENT, interdit, prix_faute, valeur_pieces
    from .vol import proprietaire
    if not profil(monde, id):
        return None
    crues = {o: _cru(monde, id, o, "pieces") for o in _connus(monde, id)}
    if not any(crues.values()):
        return None
    faute = prix_faute(monde, id, ARGENT)
    # Ce qu'il ne peut prendre (son honnêteté l'interdit, la faute passe l'enjeu), ou qui vaut moins
    # que la seule faute de le prendre, ne se cherche pas : aucun plan n'en vaudrait la peine. Jugé sur
    # les seules bourses crues, par les lectures de la vue (``Vue.illicite``, ``Vue.autorise``) : la vue
    # entière ne se construit que s'il en reste une à chercher.
    honnete, confies = interdit(monde, id, "honnetete"), {}
    bourses = []
    for o, n in crues.items():
        if (not n or proprietaire(monde, monde.objets[o]) == id or porte_par(monde, o, id)
                or not _disponible_cru(monde, id, o)):
            continue
        lese = illicite(monde, id, o, confies=confies)
        # L'interdiction de voler n'interdit pas de demander un prêt au
        # propriétaire qui porte la bourse. Le graphe valide chaque moyen.
        porteur = _lieu_cru(monde, id, o)
        emprunt = (porteur == proprietaire(monde, monde.objets[o])
                   and porteur in _connus(monde, id)
                   and bool(profil(monde, porteur)))
        if emprunt or not (lese and honnete) and (not lese or faute is not None and valeur_pieces(monde, id, n) > faute):
            bourses.append(o)
    if not bourses:
        return None
    bourses = tuple(bourses)
    v = vue(monde, id)
    trouve = chercher(monde, id, lambda v, e: any(b in e.portes for b in bourses), {"prendre": bourses},
                      nom="argent", memo=["argent"], emplois=(), motif=ARGENT)
    if trouve is None:
        return None
    cout, etapes, e = trouve
    pris = next(b for b in bourses if b in e.portes)
    if valeur_pieces(monde, id, crues[pris]) <= cout:
        return None  # Ces pièces ne valent pas, pour lui, ce qu'il lui en coûterait.
    return cout, {"type": "argent", "objet": pris}, retablir(v, e, _couper(etapes))


def reclamer(monde, id):
    """(but, étapes) pour aller trouver qui lui doit des pièces (``biens.dettes``) ou garde un objet
    qu'il lui a prêté au-delà de l'échéance (``biens.echu``), là où il le croit, quand ce qu'il lui
    doit vaut pour lui plus que le chemin (un objet sans prix déclaré vaut ``biens.VALEUR_OBJET``) ;
    None sinon. Pour une dette, se retrouver suffit : le débiteur rend ce qu'il peut, s'il le veut
    (``biens.solder``) ; s'il est déjà près de lui, rien à faire. Pour un prêt, il le lui redemande
    (``demander``), joueur compris. Un débiteur retrouvé sans le sou, ou qui vient de refuser, il ne le
    relance pas de sitôt ; un emprunteur qui vient de refuser ou à qui il l'a déjà redemandé non plus."""
    from .biens import VALEUR_OBJET, dettes, echu, nie_recemment, prets, prix
    from .caractere import ARGENT, valeur_pieces
    from .deliberation import REDEMANDE
    if not profil(monde, id):
        return None
    du, objets = {}, {}
    minute = monde.data["minutes"]
    for d in dettes(monde):
        if d["a"] == id and d["de"] in monde.objets and not nie_recemment(monde, id, d["de"]):
            du[d["de"]] = du.get(d["de"], 0) + d["montant"]
    for p in prets(monde):
        if (p["de"] == id and p["objet"] in monde.objets and (p["a"] == "joueur" or p["a"] in monde.objets)
                and echu(monde, p["objet"])
                and not refus_retenu(monde, id, p["a"], ("demander",), p["objet"])):
            objets.setdefault(p["a"], []).append(p["objet"])
    if not du and not objets:
        return None
    vains = {s["de"] for s in lire(monde, id)["memoire"] if s["type"] == "creance_vaine" and minute - s["minute"] < REDEMANDE}
    v = vue(monde, id)
    e = depart(monde, id, v)
    meilleur = None
    for de in sorted(set(du) | set(objets)):
        salle = v.salle(e, de)
        a_rendre = sorted(objets.get(de, ()))
        if salle is None or not a_rendre and (de in vains or salle == e.salle):
            continue
        valeur = (valeur_pieces(monde, id, du[de]) if de in du and de not in vains else 0) + sum(
            valeur_pieces(monde, id, prix(monde, o) or VALEUR_OBJET) for o in a_rendre)
        if salle == e.salle:
            trouve = (0, [], e)
        else:
            trouve = chercher(monde, id, lambda v, e, s=salle: e.salle == s, nom="reclamer:" + de,
                              memo=["reclamer", de, salle], emplois=(), motif=ARGENT)
        if trouve is not None and valeur > trouve[0] and (meilleur is None or trouve[0] < meilleur[0]):
            meilleur = (trouve[0], de, _couper(trouve[1]) + [_etape("demander", de, outil=o) for o in a_rendre[:1]])
    if meilleur is None:
        return None
    return {"type": "reclamer", "qui": meilleur[1]}, meilleur[2]


def s_enquerir(monde, id, besoin=None, *, sujet=None, _vue=None, _etat=None):
    """(but, étapes) pour demander à quelqu'un s'il a de quoi apaiser ``besoin`` (des vivres, du
    bois : ``echanges.enqueter``), quand rien de ce qu'il connaît n'y pourvoit : à qui il ne connaît
    rien de tel, qu'il ne se méfie pas et dont la réponse refusée ne tient plus (``deliberation.tient``),
    le plus proche de là où il le croit. Avec ``sujet``, demander le lieu d'une personne à
    un interlocuteur cru présent ; ne supposer ni ce qu'il sait, ni une réponse positive.
    None s'il n'a personne à qui le demander."""
    if not profil(monde, id):
        return None
    v = _vue or vue(monde, id)
    e = _etat or depart(monde, id, v)
    if sujet is not None:
        interroges = {s["de"] for s in lire(monde, id)["refus"]
                      if s["operation"] == "enqueter_lieu" and s.get("objet") == sujet
                      and tient(monde, id, s, v.connus)}
        for autre in sorted(v.personnes()):
            if (autre != sujet and autre not in interroges and not v.se_mefie(autre)
                    and v.salle(e, autre) == e.salle):
                return ({"type": "enquete", "qui": autre, "objet": sujet},
                        [_etape("demander", autre, contenu={"localisation": sujet})])
        return None
    # Qui n'en a pas, il ne le lui redemande pas tant que rien de ce qu'il croit de ces ressources n'a
    # changé ; qui s'est méfié, pas avant ``REDEMANDE`` minutes (``deliberation.tient``).
    interroges = {s["de"] for s in lire(monde, id).get("refus", ()) if s["operation"] == "enqueter"
                  and s.get("besoin") == besoin and tient(monde, id, s, v.connus)}
    connus = {v.proprietaire[o] for o in v.connus if part_pour(monde, id, o, besoin, v.connus)}
    candidats = []
    for autre in v.personnes():
        salle = v.salle(e, autre)
        if autre in interroges or autre in connus or salle is None or v.se_mefie(autre):
            continue
        longueur = v.trajet(e, salle, cible=autre)
        if salle == e.salle or longueur:
            candidats.append((longueur, autre, salle))
    for _, autre, salle in sorted(candidats):
        etapes = [] if salle == e.salle else aller(monde, id, salle)
        if etapes is not None:
            return ({"type": "enquete", "besoin": besoin, "qui": autre},
                    etapes + [_etape("demander", autre, contenu={"ressource": besoin})])
    return None


def voir(monde, id, salle):
    """(but, étapes) pour aller voir d'où venait un bruit inconnu : y parcourir le lieu des yeux ;
    None s'il n'y croit aucun passage. S'il a situé le bruit (``ouie.source`` : il l'a entendu de la
    salle même), il va à portée de vue de cette case, ou au contact si rien ne l'éclaire
    (``pnj.agir``) : l'étape porte la case (``vers``)."""
    from .ouie import source
    trouve = chercher(monde, id, lambda v, e: e.fait("inspecte", salle), {"inspecter": (salle,)},
                      nom="voir:" + salle, memo=["voir", salle], emplois=())
    if trouve is None:
        return None
    etapes, case = _couper(trouve[1]), source(monde, id, salle)
    if case is not None:
        etapes = [{**x, "contenu": {**x.get("contenu", {}), "vers": list(case)}}
                  if x["operation"] == "inspecter" and x["lieu"] == salle else x for x in etapes]
    return {"type": "voir", "lieu": salle}, etapes


def eclaire(v, e):
    return v.lumiere(e) > 0 and not v.dangereuse(e)


def eclairer(monde, id):
    """(but, étapes) pour avoir de la lumière là où il se tient, quand le noir l'inquiète ; None
    s'il y voit déjà, ou ne voit aucun moyen. Les moyens viennent des gestes déclarés : allumer
    une source qu'il porte ou qui est à portée, à une flamme qu'il porte ou à une flamme fixe ;
    prendre une source, la recharger du combustible qu'elle brûle ; la demander à qui la porte ;
    rejoindre un lieu qu'il croit éclairé."""
    v = vue(monde, id)
    if not peur_du_noir(monde, id) or eclaire(v, depart(monde, id, v)):
        return None
    trouve = chercher(monde, id, eclaire, {"eclairer": True}, nom="lumiere", memo=["lumiere"], emplois=(),
                      motif="securite", tenir=True, endurer=0)
    if trouve is None:
        return None
    _, etapes, e = trouve
    # Le coût de ce recours comprend un séjour (tenir=True). Une lumière fixe
    # n'accompagne pas le PNJ : exporter seulement le trajet perdrait cet état
    # terminal dès le choix suivant. Le même geste que l'abri fait vivre le
    # progrès et son terme, sans délai ajouté ni nouvelle mémoire de recherche.
    # Le terminal reste soumis à la coupure commune des gestes supposés et
    # livraisons attendues. Une attente sans geste n'a encore rien rétabli.
    if etapes and not any("allume" in v.objets[k] and v.feu(e, k)[0] for k in e.portes):
        etapes = [*etapes, _etape("abriter", lieu=e.salle)]
    return {"type": "lumiere"}, retablir(v, e, _couper(etapes))


def garder(monde, id, salle):
    """Les étapes pour se tenir là où il garde ses biens, ou None. Il y restera : ce que le lieu
    laisse monter compte (le noir qu'il craint : il y porte de la lumière s'il le peut) ; s'il n'y
    est pas, il n'y va que si cela lui coûte moins que rester où il est, sinon il endure."""
    trouve = chercher(monde, id, lambda v, e: e.salle == salle, nom="garder:" + salle, memo=["garder", salle],
                      emplois=(), motif="biens", tenir=True, endurer=0)
    return None if trouve is None else retablir(vue(monde, id), trouve[2], _couper(trouve[1]))


def abri(monde, id, salles):
    """(salle, étapes) pour gagner l'un des abris ``salles`` (éclairés, quelqu'un de sûr s'y
    tient), le moins coûteux avec ce qu'il y laissera monter en y restant ; None s'il n'en atteint
    aucun, ou si y aller lui coûte plus que d'endurer où il est : ce que l'abri lui apporte (y voir,
    ne plus côtoyer qui l'inquiète, une compagnie sûre, aux taux de son profil, ``NOIR`` par
    point) ne vaut pas ce qu'il laisse (ses biens).

    Quitter qui l'inquiète n'est pas un gain là où il garde un bien que cette présence menace
    (``deliberation.menaces``) : s'en aller, c'est le lui laisser, et cet éloignement lui coûte
    (``prix_gardes``) comme à tout plan."""
    from .deliberation import abri_valide, menaces, taux
    v = vue(monde, id)
    e = depart(monde, id, v)
    salles = [s for s in salles if abri_valide(monde, id, s)]
    ici = [x for x in v.connus + ["joueur"] if x != id and (x == "joueur" or v.objets[x]["type"] == "personnage")
           and v.salle(e, x) == e.salle]
    fuir = any(v.se_mefie(x) for x in ici) and e.salle not in menaces(monde, id)
    ici_liens = [relations.axes(monde, id, x) for x in ici]
    compagnie = max([(r["confiance"] + r["affection"]) / 100 for r in ici_liens] or [0])
    compagnie_possible = max([(r["confiance"] + r["affection"]) / 100
                             for x in [*v.personnes(), "joueur"] if v.salle(e, x) in salles and v.se_fie(x)
                             for r in [relations.axes(monde, id, x)]] or [0])
    gain = ((taux(monde, id, "noir") + taux(monde, id, "lumiere") if v.peur and v.noir(e) else 0)
            + (taux(monde, id, "mefiance") if fuir else 0)
            + max(0, compagnie_possible - compagnie) * taux(monde, id, "compagnie"))
    trouve = chercher(monde, id, lambda v, e: e.salle in salles, nom="abri", memo=["abri", sorted(salles)],
                      emplois=(), motif="securite", tenir=True, endurer=RESTER * NOIR * gain)
    return None if trouve is None else (trouve[2].salle, _couper(trouve[1]))


def aller(monde, id, salle):
    """Les étapes pour se rendre dans une salle, ou None s'il n'y croit aucun passage."""
    trouve = chercher(monde, id, lambda v, e: e.salle == salle, nom="aller", memo=["aller", salle], emplois=())
    return None if trouve is None else trouve[1]


def rejoindre(monde, id, sujet):
    """(étapes, trouvé) : aller là où il croit quelqu'un, sinon le chercher là où il est passé le
    moins récemment ; None si rien n'est atteignable."""
    v = vue(monde, id)
    e = depart(monde, id, v)
    salle = v.salle(e, sujet)
    if salle is not None:
        etapes = aller(monde, id, salle)
        return None if etapes is None else (etapes, True)
    recherche = _chercher(v, e, sujet)
    if recherche is None:
        return None
    etapes = recherche[2]
    return _couper(etapes), False


def ranimer(monde, id, cible):
    trouve = chercher(monde, id, lambda v, e: e.fait("ranime", cible), {"ranimer": (cible,)},
                      nom="ranimer:" + cible, memo=["ranimer", cible], emplois=())
    return None if trouve is None else ({"type": "ranimer", "qui": cible}, trouve[1])


def _entrees_defense(v, vises):
    ds = (vises or {}).get("danger", ())
    if not ds:
        return None
    from .force import force_crue
    from .caractere import valeur
    from .corps import corps
    return [valeur(v.monde, v.id, "courage"),
            [[a, force_crue(v.monde, v.id, a), v.violence(a, True)] for a in ds],
            bool(corps(v.monde, v.id).get("tenu_par"))]


def _gestes_defense(v, e, vises):
    ds = vises.get("danger", ())
    if not ds:
        return
    from .combat import arme, RISQUE
    from .caractere import valeur
    from .force import force_crue
    from .defense import EXPOSITION
    for a in ds:
        if vises.get("riposter") and v.salle(e, a) == e.salle and not e.fait("repousse", a):
            prix = v.violence(a, True)
            if prix is not None:
                chance = force_crue(v.monde, v.id, a)
                risque = RISQUE * (1 - chance) * (100 - valeur(v.monde, v.id, "courage")) / 50
                outils = [k for k in sorted(e.portes) if arme(v.objets[k])]
                outil = max(outils, key=lambda k: arme(v.objets[k])[1], default="")
                yield (0, .025 / chance + risque + prix,
                       [_etape("frapper", a, outil=outil, contenu={"defense": True})],
                       e.apres(faits=[(("repousse", a), True)]), .025 / chance)
    if vises.get("fuir") and all(v.salle(e, a) != e.salle for a in ds) and not e.fait("fui"):
        # Fermer derrière soi appartient au plan, avec la même règle de clé que garder.
        portes = sorted(p for p in v.portes_de[e.salle] & set(vises.get("fermer", ()))
                        if refermable(e.fait("fin", p) or v.cru(p, "fin")))
        closes = all(not v.ouvert(e, p) for p in portes)
        verrouillables = [p for p in portes if any(p in v.objets[k].get("ouvre", ()) for k in e.portes)]
        if closes and all(v.verrouille(e, p) for p in verrouillables):
            chance = max(force_crue(v.monde, v.id, a) for a in ds)
            # Prix des pas exposés : la fuite ne reçoit aucune avance gratuite.
            yield (0, EXPOSITION * chance, [_etape("fuite", ds[0])],
                   e.apres(faits=[(("fui",), True)]), 0)


def reagir(monde, id, dangers, aide=None):
    """Le graphe compare les moyens de sortir du danger ; un coup est toujours revalidé."""
    from . import corps
    from .defense import etat_cru
    if corps.corps(monde, id).get("tenu_par"):
        return {"type": "degager"}, [_etape("degager")]
    ennemis = list(dangers)
    protection = bool(aide and aide[2])
    if protection:
        ennemis = [a for a in aide[2] if etat_cru(monde, id, a).get("conscient") is not False
                   and not etat_cru(monde, id, a).get("reddition")]
    if aide and not ennemis:
        protege, salle, _ = aide
        trajet = aller(monde, id, salle)
        r = (salle, trajet) if trajet else voir(monde, id, salle)
        if r:
            return {"type": "proteger", "qui": protege, "lieu": salle}, r[1]
    if not ennemis:
        return None
    # Fuir un danger et protéger sont des buts distincts : quitter son protégé ne le protège pas.
    v = vue(monde, id)
    portes = sorted({p for a in ennemis for p in v.portes_de.get(salle_crue(monde, id, a), ())})
    vises = {"danger": ennemis, "riposter": True, "fuir": not protection, "fermer": portes}
    but = lambda v, e: bool(e.fait("fui") or any(e.fait("repousse", a) for a in ennemis))
    trouve = chercher(monde, id, but, vises, nom="proteger" if protection else "defense",
                      memo=["defense", vises], emplois=(), motif="devoir" if protection else "securite")
    if trouve:
        etapes = trouve[1]
        fuite = trouve[2].fait("fui")
        genre = "fuir" if fuite else "proteger" if protection else "riposter"
        return {"type": genre, "qui": ennemis[0]}, etapes
    if corps.blessure(monde, id) == 2 and dangers:
        return {"type": "reddition", "qui": dangers[0]}, [_etape("se_rendre", dangers[0])]
    return None
