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
import copy
import heapq
import json
from contextlib import contextmanager
from itertools import count
from time import perf_counter

from .deliberation import (ATTENTE_PART, CAUSES, REDEMANDE, _connus, appels_vains, apport_cru, _cru, _disponible_cru,
                           _lieu_cru, besoin_de_part, gardes, illicite, lumiere_crue, moyens_crus, noir_cru,
                           peur_du_noir, profil, promesse_en_cours, refus_retenu, tient)
from . import force
from .biens import PRIX_PART
from .esprits import lire
from .perception import brule, recharge
from .spatial import porte_par

PROFONDEUR = 8         # gestes au plus dans un plan (un trajet compte pour un)
NOEUDS = 4000          # états examinés au plus
DEMANDE = 3            # demander : on préfère ce qu'on peut faire seul
PRET = 0.5             # chance qu'on accède à une demande, d'un objet qu'il porte ou d'une part
CHERCHER = 3           # chercher quelqu'un qu'on a perdu de vue : on n'est pas sûr de le trouver
FLAMME_EN_MAIN = 1     # par minute, tant qu'une flamme allumée par le plan se consume en main
NOIR = 3               # par minute passée dans le noir, fois ce que le noir l'inquiète (``peur_du_noir``)
GARDE = 2              # par minute loin de chaque lieu où il garde ses biens, quand ils le pressent
RESTER = 30            # minutes qu'il compte passer là où le mène un but qui se tient en restant
TACHE = 5              # minutes de travail d'une tâche payée, en plus du chemin (``_engager``)
SALAIRE = 3            # minutes de peine qu'il paie une pièce, à qui fait une tâche pour lui
SURENCHERE = 2         # refusé pour un prix trop bas, il offre au moins tant de fois ce prix (``_engager``)
# Effets qui achèvent un but sans rien permettre ensuite : un geste qui les produit sans
# atteindre le but cherché ne mène nulle part (se chauffer quand on a faim).
TERMINAUX = ("mange", "part", "chauffe", "inspecte", "servi")
# Ce qui compte sur un tiers : lui demander, lui acheter, le payer (``devis_pulsion`` les écarte).
TIERS = ("demander", "acheter", "engager")
# Usages que les gestes savent employer : un objet n'est pris que s'il peut servir à l'un d'eux.
USAGES = ("crochetage", "allumage", "combustible", *force.CHOC, *force.COUPE)
# Chaque recherche s'y consigne quand le banc le demande (``diagnostics``) ; sinon None.
DIAGNOSTIC = None
# Le dernier résultat de chaque PNJ pour chaque but, avec tout ce dont il dépendait. Il ne tient
# pas à l'objet monde : le moteur agit sur une copie de travail à chaque action.
_MEMOIRE = {}
# Le graphe de la dernière recherche de chaque PNJ pour chaque but (``_explorer``), avec tout ce dont
# il dépendait (None : des entrées vues une fois, sans graphe gardé) : quand seuls le prix d'une faute
# ou celui d'abîmer ont changé (la détresse qui monte), la recherche se refait sur lui sans
# recalculer un seul geste.
_GRAPHES = {}
# Vrai (tests) : un résultat repris de la mémoire ou cherché parmi ce qu'il vaut la peine de
# porter est recalculé par une recherche complète, et comparé.
VERIFIER = False


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
    égaux quand le sont (salle, portes, faits) : le tuple qu'il est."""

    def __new__(cls, salle, portes, faits):
        portes, faits = frozenset(portes), dict(faits)
        etat = tuple.__new__(cls, (salle, portes, frozenset(faits.items())))
        etat.salle, etat.portes, etat.faits = salle, portes, faits
        return etat

    def __lt__(self, autre):
        return False

    def apres(self, salle=None, portes=None, faits=()):
        salle = self.salle if salle is None else salle
        portes = self.portes if portes is None else frozenset(portes)
        faits = {**self.faits, **dict(faits)}
        suivant = tuple.__new__(Etat, (salle, portes, frozenset(faits.items())))
        suivant.salle, suivant.portes, suivant.faits = salle, portes, faits
        return suivant

    def fait(self, *cle):
        return self.faits.get(cle)


class Vue:
    """Ce que le PNJ croit, corrigé de ce que le plan a déjà changé.

    Ses croyances ne bougent pas pendant une recherche : chaque lecture est faite une fois."""

    def __init__(self, monde, id):
        from .caractere import interdit
        from .pnj import chemin, parcours
        from .vol import proprietaire
        self.monde, self.id = monde, id
        self.objets = monde.objets
        self.salles = monde.data["salles"]
        self.connus = _connus(monde, id)
        # Toucher au bien d'autrui, hors ce qu'un prêt ou une garde permettent ; le consommer (le
        # manger, en servir une part), que rien ne permet.
        confies = {}
        self.illicite = {o: illicite(monde, id, o, confies=confies) for o in self.connus}
        self.consomme_illicite = {o: illicite(monde, id, o, "manger", confies) for o in self.connus}
        self.brise_illicite = {o: illicite(monde, id, o, "frapper", confies) for o in self.connus}
        # Le prix d'abîmer le bien d'autrui (forcer), au prix de sa douceur (``chercher``) ; None :
        # il ne l'envisage pas.
        self.degat = None
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
        # Ce qui donne du feu de main en main : un outil d'allumage, une source portable.
        self.flammes_portables = [o for o in self.connus if "allumage" in self.objets[o].get("usages", [])
                                  or "allume" in self.objets[o] and self.objets[o].get("mobile")]
        self.foyers = [o for o in self.connus if self.objets[o].get("foyer")]
        # Ce que le noir l'inquiète : chaque minute qu'il y passe lui coûte (``NOIR``), s'il croit
        # le noir quelque part (``noir_cru``) ; sinon, rien ne lui coûte d'y être.
        self.peur = peur_du_noir(monde, id)
        if self.peur and not any(noir_cru(monde, id, s) for s in self.salles):
            self.peur = 0
        # Les lieux où il garde ses biens, quand ils le pressent : chaque minute loin de l'un d'eux
        # lui coûte (``GARDE``).
        self.gardes = gardes(monde, id)
        self._chemin, self._parcourir, self._parcours = chemin, parcours, {}
        self._routes, self._trajets, self._crus, self._agissables, self._pressions = {}, {}, {}, {}, {}
        self._allers = {}
        self.salles_triees = sorted(self.salles)
        # Le besoin qu'une part de chaque objet apaise (``besoin_de_part``).
        self.besoin = {o: besoin_de_part(self.objets[o]) for o in self.connus}
        # Les portes de chaque salle : celles qu'il peut crocheter de là.
        self.portes_de = {s: frozenset(x["porte"] for x in d["sorties"].values() if x.get("porte"))
                          for s, d in self.salles.items()}
        self.emplois = None    # ce que le but peut employer (``chercher``) ; None : tout
        self.seul = None       # par ses seuls moyens : à qui seul il peut demander (``devis_pulsion``)

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
        si le but est la lumière, si le noir l'inquiète ou s'il sait crocheter.

        Porter autre chose ne change ni les gestes possibles ni leur coût : le prendre ne fait
        qu'ajouter des minutes, le plan le moins coûteux n'en passe jamais par là, et la
        recherche rend le même résultat sans explorer ces détours."""
        if self.emplois is None:
            return True
        x = self.objets[o]
        usages = x.get("usages", [])
        crochete = "crochetage" in profil(self.monde, self.id)["capacites"]
        voir = "lumiere" in self.emplois or self.peur > 0 or crochete
        return bool(x.get("ouvre") or x["type"] == "contenant" or o in vises
                    or self.verrous and set(usages) & set(force.CHOC + force.COUPE)
                    or "manger" in self.emplois and x["type"] == "nourriture"
                    or "feu" in self.emplois and ("combustible" in usages or "allumage" in usages or "allume" in x)
                    or crochete and "crochetage" in usages
                    or voir and ("allume" in x or "allumage" in usages or "combustible" in usages and any(
                        recharge(self.objets[s], x) for s in self.rechargeables)))

    def moyen_du_but(self, o, vises):
        """Ce qui vaut d'aller chercher qui le porte : ce que le but vise lui-même, ou, pour avoir de
        la lumière, une source ou une flamme. Pas ce qui ne servirait qu'en chemin (une lampe pour
        qui craint le noir, une clé), ni les moyens d'un feu ou d'un repas : leur part se cherche
        déjà chez son propriétaire (``_chercher``), et chercher quiconque porte un combustible ou
        une flamme élargit chaque recherche d'un feu sans la servir (voir les limites)."""
        if o in vises:
            return True
        x = self.objets[o]
        return bool(self.emplois is not None and "lumiere" in self.emplois
                    and ("allume" in x or "allumage" in x.get("usages", [])))

    def _memo(self, cle, calcul):
        crus = self._crus
        if cle not in crus:
            crus[cle] = calcul()
        return crus[cle]

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
        refus = self.retenu(autre, ("demander", "acheter"), o)
        return refus if refus and refus["raison"] != "pauvre" else None

    def refuse_tache(self, autre, o):
        """Un refus qui tient de faire pour lui une tâche sur ``o`` (``echanges.engager``) ; « cher »
        ne tient que pour son prix."""
        return self.retenu(autre, ("engager",), o)

    def refus_taches(self, o):
        """Combien ont refusé, depuis ``REDEMANDE`` minutes, une tâche sur ``o`` qu'il leur offrait :
        chaque refus lui apprend qu'un autre acceptera moins sûrement (``_engager``)."""
        def compter():
            minute = self.monde.data["minutes"]
            return sum(1 for s, _ in self.refus_tenus()
                       if s["operation"] == "engager" and s.get("objet") == o and minute - s["minute"] < REDEMANDE)
        return self._memo((o, "refus_taches"), compter)

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

    def promesse(self, o):
        cle = (o, "promesse")
        crus = self._crus
        if cle not in crus:
            crus[cle] = promesse_en_cours(self.monde, self.id, o)
        return crus[cle]

    def sur_soi(self, besoin, portes):
        """Porte-t-il de quoi apaiser ce besoin (une part qu'il n'a pas à demander) ?"""
        cle = (besoin, portes)
        crus = self._crus
        if cle not in crus:
            crus[cle] = any(self.besoin[k] == besoin and self.disponible(k) for k in portes)
        return crus[cle]

    def profil_de(self, x):
        """``deliberation.profil`` de ``x``, lu une fois."""
        cle = (x, "profil")
        crus = self._crus
        if cle not in crus:
            crus[cle] = profil(self.monde, x)
        return crus[cle]

    def allers(self, e, ouvertes):
        """[(salle, longueur du trajet)] : chaque autre salle qu'il croit atteindre depuis celle de
        ``e``, avec ce qu'il porte et les portes que le plan a déverrouillées (``route``)."""
        cle = (e.salle, e.portes, ouvertes)
        if cle not in self._allers:
            allers = []
            for s in self.salles_triees:
                if s != e.salle:
                    route = self.route(e, s, ouvertes)
                    if route is not None:
                        allers.append((s, len(route)))
            self._allers[cle] = allers
        return self._allers[cle]

    def route(self, e, arrivee, ouvertes=None):
        """Les sorties de sa salle jusqu'à ``arrivee``, avec les clés qu'il porte et les portes que
        le plan a déverrouillées (crochetées, ``ouvertes`` si on les a déjà) ; None s'il n'y croit
        aucun passage."""
        trajet = (e.salle, arrivee, e.portes, self.ouvertes(e) if ouvertes is None else ouvertes)
        if trajet in self._trajets:
            return self._trajets[trajet]
        cles = frozenset(k for k in e.portes if self.objets[k].get("ouvre"))
        cle = (e.salle, arrivee, cles, trajet[3])
        if cle not in self._routes:
            # Le parcours depuis sa salle vaut pour toutes les arrivées (``pnj.parcours``).
            depuis = (e.salle, cles, trajet[3])
            if depuis not in self._parcours:
                self._parcours[depuis] = self._parcourir(self.monde, self.id, e.salle, cles, trajet[3])
            self._routes[cle] = self._chemin(self.monde, self.id, e.salle, arrivee, cles, trajet[3],
                                             self._parcours[depuis])
        self._trajets[trajet] = self._routes[cle]
        return self._routes[cle]

    def ouvertes(self, e):
        """Les portes que le plan a déverrouillées."""
        return frozenset(cle[1] for cle, valeur in e.faits.items()
                         if cle[0] == "verrou" and valeur is False and self.objets[cle[1]]["type"] == "porte")

    def lieu(self, e, o):
        if o in e.portes:
            return self.id
        lieu = e.faits.get(("lieu", o))
        if lieu is not None:
            return lieu
        cle = (o, "lieu_cru")
        crus = self._crus
        if cle not in crus:
            crus[cle] = _lieu_cru(self.monde, self.id, o)
        return crus[cle]

    def salle(self, e, sujet, profondeur=0):
        if sujet in e.portes or sujet == self.id:
            return e.salle
        lieu = self.lieu(e, sujet)
        if lieu is None or profondeur > 4:
            return None
        if lieu in self.salles:
            return lieu
        if lieu == "joueur":
            return self._memo(("joueur", "lieu_cru"), lambda: _lieu_cru(self.monde, self.id, "joueur"))
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
        est (un outil d'allumage, ou une source portable qu'il croit allumée)."""
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
        qu'il veut allumer."""
        return [k for k in self.connus if "allume" in self.objets[k] and not self.objets[k].get("mobile")
                and self.salle(e, k) == e.salle and self.feu(e, k)[0]]

    def foyer_froid(self):
        """Le feu qu'une part de bois servirait : le premier foyer qu'il croit éteint."""
        if "foyer_froid" not in self._crus:
            self._crus["foyer_froid"] = next((f for f in self.connus if self.objets[f].get("foyer")
                                              and (self.cru(f, "etat") or {}).get("allume") is False), None)
        return self._crus["foyer_froid"]

    def attente_part(self, e, donneur, o, service):
        """Les minutes qu'il attendra la part ``o`` promise, là où elle se sert (``service``) : que le
        donneur aille d'où il le croit jusqu'à elle, la prenne s'il faut la porter, vienne la servir.
        Promise dans le plan, le donneur s'est mis en route en même temps que lui : le chemin qu'il a
        fait lui-même depuis la promesse (``promis_ou``) n'est plus à attendre. Au moins le geste de
        servir."""
        reserve = self.salle(e, o)
        depuis = self.salle(e, donneur) or reserve or service
        temps = 1 + self.trajet(depuis, reserve or depuis) + self.trajet(reserve or depuis, service)
        if reserve not in (None, service) and self.lieu(e, o) != donneur:
            temps += 1   # La prendre, pour la porter là où elle se sert.
        promis_ou = e.fait("promis_ou", o)
        if promis_ou is not None:
            temps -= self.trajet(promis_ou, service)
        return max(1, temps)

    def trajet(self, depart_, arrivee):
        """Les sorties d'une salle à une autre, par le chemin qu'il en connaît ; 0 sans chemin."""
        if depart_ == arrivee:
            return 0
        cle = ("trajet", depart_, arrivee)
        if cle not in self._crus:
            route = self._chemin(self.monde, self.id, depart_, arrivee, frozenset(), frozenset())
            self._crus[cle] = 0 if route is None else len(route)
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
        return self._crus[cle]

    def lumiere_devant(self, e, o):
        """La lumière qu'il croit avoir devant ``o``, là où un geste qui demande d'y voir se fait :
        pleine avec la lumière du plan (``lumiere``) ; sinon celle qu'il y a vue en s'y tenant
        (croyance ``lumiere`` de l'objet, ``esprits.constater_lumiere_devant``), et ce qu'y apporte
        une source qu'il sait allumée ou posée près de lui depuis (``deliberation.apport_cru``) ; à
        défaut, celle de la salle."""
        if self._eclaire_par_le_plan(e):
            return 2
        vue = self.cru(o, "lumiere")
        return self.lumiere(e) if vue is None else max(vue, self.apport(o))

    def apport(self, o):
        return self._memo((o, "apport"), lambda: apport_cru(self.monde, self.id, o))

    def _eclaire_par_le_plan(self, e):
        """Une source allumée en main, ou une source que le plan a allumée dans sa salle."""
        return (any("allume" in self.objets[k] and self.feu(e, k)[0] for k in e.portes)
                or any(cle[0] == "allume" and allume and self.salle(e, cle[1]) == e.salle
                       for cle, allume in e.faits.items()))

    def pression(self, e):
        """Ce que lui coûte une minute dans cet état, par ce qu'il y laisse monter : le noir, s'il le
        craint (``NOIR``), l'éloignement de chaque lieu où il garde ses biens (``GARDE``)."""
        pressions = self._pressions
        if e not in pressions:
            p = NOIR * self.peur if self.peur and self.noir(e) else 0
            pressions[e] = p + GARDE * sum(1 for g in self.gardes if g != e.salle)
        return pressions[e]

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


def chance_crochetage(monde, id, lumiere):
    """Sa chance au jet de ``pnj._crocheter`` à la lumière qu'il croit avoir : d20 + DEX contre
    ``pnj.seuil_crochetage``. 0 quand aucun jet ne l'atteint : il ne l'envisage pas."""
    from .caractere import modificateur
    from .pnj import seuil_crochetage
    reussites = 21 - (seuil_crochetage(lumiere) - modificateur(monde, id, "DEX"))
    return min(1.0, max(0.0, reussites / 20))


def gestes(v, e, vises=None, but=None):
    """Les gestes possibles depuis cet état : (fautes, minutes, étapes, état suivant[, durée[,
    abîme]]). Les fautes comptent les personnes lésées ; les minutes font le coût, et la durée
    réelle (celle qu'il passerait dans le noir) n'est donnée que quand elle en diffère : demander, ou
    chercher quelqu'un, coûte plus que le temps qu'il y passe. Abîmer le bien d'autrui (vrai) ajoute
    un prix qui n'est pas du temps, celui de sa douceur (``Vue.degat``, compté par ``_explorer``).

    ``vises`` ouvre les gestes que seul un but demande, sur les objets ou lieux qu'il vise :
    inspecter une salle, prendre un objet qui ne sert à aucun geste, poser, fermer et
    verrouiller, servir une part à quelqu'un. Les offrir partout élargirait la recherche sans
    rien lui apprendre."""
    monde, id = v.monde, v.id
    vises = vises or {}
    p = profil(monde, id)
    objets = v.objets
    # Aller : un trajet vers toute salle qu'il croit atteindre avec ce qu'il porte, par les portes
    # qu'il ne croit pas verrouillées ou que le plan a déverrouillées.
    for s, longueur in v.allers(e, v.ouvertes(e)):
        yield 0, longueur, [_etape("aller", lieu=s)], e.apres(salle=s)
    agissables, a_porter = v.agissables(vises)
    portes, faits, sa_salle = e.portes, e.faits, e.salle
    v_prendre, v_entretenir = vises.get("prendre", ()), vises.get("entretenir", ())
    v_poser, v_fermer, v_servir = vises.get("poser", ()), vises.get("fermer", ()), vises.get("servir", {})
    noms_vises = frozenset(o for k in ("prendre", "poser", "fermer", "servir") for o in vises.get(k, ()))
    # Une source allumée en main l'éclaire et lui donne une flamme. À qui n'a que faire de lumière
    # (ni le noir, ni la lumière comme but, ni une serrure à crocheter), une lampe ou un briquet ne
    # sert que de flamme, pour un feu qu'il croit éteint : une flamme en main suffit, et sans feu à
    # allumer il n'en faut aucune. Une lampe ou un briquet de plus, à prendre, à recharger ou à
    # allumer, ne lui apporterait alors rien, sauf ce que vise le but.
    eclaire_en_main = any("allume" in objets[k] and v.feu(e, k)[0] for k in e.portes)
    lumiere_compte = v.peur or "lumiere" in (v.emplois or ()) or "crochetage" in p["capacites"]
    assez = eclaire_en_main or not lumiere_compte and (
        any(v.flamme(e, k) for k in e.portes)
        or not any(v.feu(e, f)[0] is False for f in v.foyers + list(vises.get("entretenir", ()))))
    portes_ici = v.portes_de[sa_salle]
    for o in agissables:
        x = objets[o]
        # Un objet qu'il ne porte pas et qu'il croit dans une autre salle (sans être une porte de
        # celle-ci) n'offre ici aucun geste : on ne peut qu'en demander une part.
        if o not in portes and o not in portes_ici:
            ailleurs = v.salle(e, o)
            if ailleurs is not None and ailleurs != sa_salle:
                if v.besoin[o]:
                    yield from _parts(v, e, o, v.lieu(e, o), vises, but)
                continue
        superflu = (assez and ("allume" in x or "allumage" in x.get("usages", [])) and not x.get("foyer")
                    and o not in v_prendre and o not in v_entretenir)
        # ``Vue.lieu`` et ``Vue.a_portee`` : dans sa main, dans sa salle, ou dans un contenant ouvert
        # de sa salle.
        if o in portes:
            ici, dans = True, v.id
        else:
            dans = v.lieu(e, o)
            ici = dans == sa_salle or (dans in objets and objets[dans]["type"] == "contenant"
                                   and v.salle(e, dans) == sa_salle and v.ouvert(e, dans))
        contenant = dans if dans in objets and objets[dans]["type"] == "contenant" else None
        touche = [(("touche", contenant), True)] if contenant else []
        # Prêté ou acheté par le plan, le bien d'autrui s'emploie sans faute ; rien ne permet de
        # le consommer, sauf ce qu'il a acheté.
        illicite_ = v.illicite[o] and not faits.get(("permis", o))
        faute = "sans_temoin" if illicite_ else ""
        lese = v.proprietaire[o] if illicite_ else None
        mal = int(bool(lese) and not faits.get(("faute", lese)))
        if lese:
            touche = touche + [(("faute", lese), True)]
        conso = v.consomme_illicite[o] and not faits.get(("achete", o))
        faute_conso = "sans_temoin" if conso else ""
        lese_conso = v.proprietaire[o] if conso else None
        mal_conso = int(bool(lese_conso) and not faits.get(("faute", lese_conso)))
        touche_conso = [(("faute", lese_conso), True)] if lese_conso else []
        # Prendre ce qu'un geste sait employer : clé, outil, vivres, combustible, flamme portable.
        utile = (v.utile[o] or o in v_prendre) and o in a_porter and not superflu
        if ici and o not in portes and x.get("mobile") and v.autorise[o] and v.disponible(o) and utile:
            yield mal, 1, [_etape("prendre", o, condition=faute)], e.apres(portes=portes | {o}, faits=touche)
        # Le demander à qui le porte, s'il est là : il peut refuser, le plan se refait alors.
        porteur = dans if dans in objets and objets[dans]["type"] == "personnage" else None
        if dans == "joueur" and v.proprietaire[o] == id:
            porteur = "joueur"   # Son bien, prêté au joueur : il le lui redemande là où il le voit.
        # On ne demande un objet qu'à qui il appartient (ou s'il n'est à personne), ou ce qui est à
        # soi : recevoir le bien d'autrui de qui le détient n'en fait pas le sien.
        demandable = (utile and porteur and porteur != id and (porteur == "joueur" or v.profil_de(porteur))
                      and o not in e.portes and v.proprietaire[o] in (porteur, None, id))
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
                yield (0, 1 + DEMANDE / PRET, [_etape("demander", porteur, outil=o)],
                       e.apres(portes=e.portes | {o}, faits=permis), 1)
            # L'acheter à son propriétaire, s'il a un prix et qu'il peut le payer.
            prix = objets[o].get("prix")
            if (prix and v.proprietaire[o] == porteur and v.piece and not v.refuse_achat(porteur, o)
                    and v.richesse - (e.fait("depense") or 0) >= prix):
                yield (0, 1 + DEMANDE + v.depense(prix),
                       [_etape("acheter", porteur, outil=o, contenu={"prix": prix})],
                       e.apres(portes=e.portes | {o}, faits=[(("permis", o), True), (("achete", o), True),
                                                             (("depense",), (e.fait("depense") or 0) + prix)]), 1)
        touche = [x for x in touche if x[0][0] == "faute"]
        if o in v_poser and o in portes:
            yield (0, 1, [_etape("poser", o, lieu=sa_salle)],
                   e.apres(portes=portes - {o}, faits=[(("lieu", o), sa_salle)]))
        if o in v_fermer and v.salle(e, o) == sa_salle:
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
                lumiere = v.lumiere_devant(e, o)
                chance = chance_crochetage(monde, id, lumiere) if "crochetage" in p["capacites"] else 0
                if chance and v.autorise[o]:
                    for outil in sorted(k for k in e.portes if "crochetage" in objets[k].get("usages", [])):
                        yield (mal, 1 / chance, [_etape("crocheter", o, outil=outil, condition=faute,
                                                        contenu={"lumiere": lumiere})],
                               e.apres(faits=[(("verrou", o), False), (("touche", o), True), *touche]))
                # La forcer, par la règle du joueur (``force``) : avec un outil qu'il porte qui l'entame,
                # coup après coup jusqu'à la briser ; brisée, elle reste ouverte. Abîmer le bien
                # d'autrui heurte aussi sa douceur, une fois par personne lésée (``degat``).
                brise = v.proprietaire[o] if v.brise_illicite[o] else None
                if v.autorise[o] and not (brise and v.degat is None):
                    degat = [(("degat", brise), True)] if brise else []
                    abime = bool(brise) and not e.fait("degat", brise)
                    for outil in sorted(k for k in e.portes if force.adapte(x, objets[k])):
                        n, c = force.coups(monde, id, x, objets[outil]), force.chance(monde, id, objets[outil])
                        if n and c:
                            yield (int(bool(brise) and not e.fait("faute", brise)), n / c,
                                   [_etape("frapper", o, outil=outil, condition="sans_temoin" if brise else "")],
                                   e.apres(faits=[(("verrou", o), False), (("ouvert", o), True), (("touche", o), True),
                                                  *([(("faute", brise), True)] if brise else []), *degat]),
                                   n / c, abime)
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
            if brule(x) and not (allume and charge) and (x.get("foyer") or o in v_entretenir or not charge):
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
            if allume and x.get("foyer"):
                yield 0, 1, [_etape("chauffer", o)], e.apres(faits=[(("chauffe", o), True)])
        if v.besoin[o]:
            yield from _parts(v, e, o, dans, vises, but)
    for salle in vises.get("inspecter", ()):
        if salle == e.salle and not e.fait("inspecte", salle):
            yield 0, 1, [_etape("inspecter", lieu=salle)], e.apres(faits=[(("inspecte", salle), True)])
    for condition in vises.get("confier", ()):
        yield from _engager(v, e, condition)


def effets_tache(condition):
    """Ce qu'une tâche faite change, dans l'état cru d'un plan : un feu chargé et allumé, un bien
    fermé à clé, un objet en son lieu."""
    o = condition["objet"]
    if "allume" in condition:
        return [(("charge", o), True), (("allume", o), True)]
    if "verrouillee" in condition:
        return [(("verrou", o), True), (("ouvert", o), False)]
    return [(("lieu", o), condition["lieu"])]


def peine_tache(v, e, condition):
    """La peine d'une tâche, d'après ce qu'il en croit : le chemin d'ici (où se tient celui qu'il
    paie) jusqu'au lieu de la tâche, et ``TACHE`` minutes de travail ; None s'il ne sait où."""
    lieu = condition.get("lieu") or v.salle(e, condition["objet"])
    return None if lieu is None else v.trajet(e.salle, lieu) + TACHE


def prix_tache(peine):
    """Ce qu'il offre pour une tâche : une pièce par ``SALAIRE`` minutes de peine. Il ne sait pas ce
    que vaut une pièce pour l'autre : il paie la peine."""
    return max(1, -(-peine // SALAIRE))


def _engager(v, e, condition):
    """Payer quelqu'un, là où il se tient avec lui, pour qu'il fasse en sorte que ``condition`` soit
    vraie (``echanges.engager``), sur ce qu'il pourrait faire lui-même sans faute : il propose ses
    pièces à qui il ne se méfie pas et qui ne vient pas de refuser ; l'autre accepte si ces pièces valent pour lui la peine. Comme une demande, ce n'est pas
    acquis (``PRET``), d'autant moins que d'autres viennent de refuser (``Vue.refus_taches``) ; il paie aussitôt ce que lui coûtent ses pièces (``Vue.depense``), et attend
    que l'autre ait fait la tâche (sa peine). La tâche faite, son but est atteint ; il ne la fait pas
    à sa place tant qu'elle court (``deliberation.tache_payee``)."""
    o = condition["objet"]
    # On ne paie quelqu'un que pour ce qu'on pourrait faire soi-même sans faute : son bien, ce qui
    # n'est à personne, ce qu'on vous a confié ; pas le bien d'autrui qu'on convoite.
    if not v.piece or e.fait("engage", o) or o not in v.illicite or v.illicite[o] or "lieu" in condition and o in e.portes:
        return
    peine = peine_tache(v, e, condition)
    if peine is None:
        return
    prix = prix_tache(peine)
    if v.richesse - (e.fait("depense") or 0) < prix:
        return
    for autre in v.personnes():
        if v.salle(e, autre) != e.salle or v.cru(autre, "fiable") is False:
            continue
        # Un refus qui tient l'écarte ; trop peu payé, il ne tient que pour ce prix : il offre plus,
        # s'il le peut (``SURENCHERE``).
        offre, refus = prix, v.refuse_tache(autre, o)
        if refus:
            if refus["raison"] != "cher":
                continue
            offre = prix if prix > refus["prix"] else SURENCHERE * refus["prix"]
            if v.richesse - (e.fait("depense") or 0) < offre:
                continue
        yield (0, 1 + DEMANDE * (1 + v.refus_taches(o)) / PRET + v.depense(offre) + peine,
               [_etape("engager", autre, contenu={"condition": dict(condition), "prix": offre})],
               e.apres(faits=effets_tache(condition) + [(("engage", o), autre),
                                                        (("depense",), (e.fait("depense") or 0) + offre)]), 1)


def _parts(v, e, o, dans, vises, but):
    """Une part : l'attendre si elle est promise, là où le donneur viendra la servir (près des
    vivres, ou du feu qu'il entretiendra) ; sinon la demander à son propriétaire. Une part de
    combustible va au feu que le but entretient, sinon au premier qu'il croit éteint : le donneur le
    recharge et l'allume lui-même. On ne demande pas ce qu'on a sur soi. ``dans`` : où est ``o``
    (``Vue.lieu``).

    Promise ou vendue, elle n'est pas encore là : il l'attend où elle se sert, le temps que le
    donneur y vienne (``attente_part``), et ce temps-là compte comme tout autre, avec ce qu'il y
    laisse monter (loin de ses biens, dans le noir)."""
    besoin, id = v.besoin[o], v.id
    if not (besoin and v.disponible(o) and not (besoin == "chaleur" and v.feu_noye())
            and not v.sur_soi(besoin, e.portes)):
        return
    donneur = v.proprietaire[o]
    foyer = ((vises.get("entretenir") or (v.foyer_froid(),))[0]
             if besoin == "chaleur" else None)
    part = [(("part", o), donneur)] + ([(("charge", foyer), True), (("allume", foyer), True)]
                                       if foyer else [])
    if donneur not in (None, id, "joueur") and v.profil_de(donneur):
        promise = v.promesse(o) == donneur or e.fait("promis", o) == donneur
        if promise:
            service = v.salle(e, foyer) if foyer else v.salle(e, o)
            if e.salle == service:
                attente = v.attente_part(e, donneur, o, service)
                yield 0, attente, [], e.apres(faits=part), attente
        elif not e.fait("promis", o):
            ou = v.salle(e, donneur)
            promis = [(("promis", o), donneur), (("promis_ou", o), e.salle)]
            # Promise, elle ne mène qu'à l'attendre là où elle se sert : la demander ou
            # l'acheter ne sert que si, servie là, elle atteint le but (comme ``TERMINAUX``).
            service = v.salle(e, foyer) if foyer else v.salle(e, o)
            utile_part = but is None or service is not None and but(v, e.apres(salle=service, faits=part))
            # L'acheter s'il peut la payer : le prix lui coûte ce que valent ses pièces. Une
            # part se vend de ce qui est rangé ; ce que le donneur porte, il le remettrait
            # entier (``echanges.demande_de_part``).
            prix = v.objets[o].get("prix_part", PRIX_PART)
            if (utile_part and ou == e.salle and v.piece and dans != donneur and not v.refuse_achat(donneur, o)
                    and v.richesse - (e.fait("depense") or 0) >= prix):
                yield (0, 1 + DEMANDE + v.depense(prix),
                       [_etape("acheter", donneur, outil=o,
                               contenu={"prix": prix, **({"foyer": foyer} if foyer else {})})],
                       e.apres(faits=promis + [(("depense",), (e.fait("depense") or 0) + prix)]), 1)
        if not promise and not e.fait("promis", o) and not v.refuse(donneur, o):
            if ou == e.salle and utile_part:
                # Une part demandée n'est pas acquise : comme un objet demandé, elle coûte
                # selon la chance d'être accordée (``PRET``).
                yield (0, 1 + DEMANDE / PRET, [_etape("demander", donneur, outil=o,
                                                contenu={"foyer": foyer} if foyer else None)],
                       e.apres(faits=promis), 1)
            elif (ou is None and not e.fait("cherche", donneur)
                  and (but is None or but(v, e.apres(faits=part)))):
                # Le chercher ne sert que si sa part atteint le but.
                recherche = _chercher(v, e, donneur)
                if recherche is not None:
                    yield recherche


def _chercher(v, e, sujet):
    """Perdu de vue : il va le chercher là où il est passé le moins récemment, et l'y suppose,
    hors des salles où il l'a hélé en vain (``deliberation.appels_vains``) ; None s'il n'en reste
    aucune. Le plan s'arrête après cette recherche : la suite se décide sur ce qu'il aura vu."""
    visites = lire(v.monde, v.id)["visites"]
    vaines = appels_vains(v.monde, v.id, sujet)
    routes = {s: v.route(e, s) for s in v.salles if s not in vaines}
    routes = {s: r for s, r in routes.items() if r is not None}
    if not routes:
        return None
    salle = min(routes, key=lambda s: (visites.get(s, -1), len(routes[s]), s))
    # Il y parcourt la salle des yeux, et l'appelle s'il ne le voit pas (``pnj.appeler``).
    etapes = ([_etape("aller", lieu=salle)] if salle != e.salle else []) + [
        {**_etape("inspecter", lieu=salle, contenu={"cherche": sujet}), "suppose": True}]
    return 0, len(routes[salle]) + 1 + CHERCHER, etapes, e.apres(
        salle=salle, faits=[(("lieu", sujet), salle), (("cherche", sujet), True)]), len(routes[salle]) + 1


def depart(monde, id, v=None):
    v = v or Vue(monde, id)
    return Etat(monde.objets[id]["lieu"], [k for k in v.connus if porte_par(monde, k, id)], {})


# Ce qui change d'une minute à l'autre dans un objet, et qu'une recherche ne lit jamais : elle lit
# ce qu'il en croit. Le lieu vrai n'y entre que par ce qu'il porte, les propriétaires et les
# objets fixes (``_entrees``) ; les pièces d'une bourse, que par ce qu'il peut dépenser.
CHANGEANTS = frozenset(("lieu", "position", "position_salle", "orientation", "corps", "humeur", "combustible",
                        "portions", "charges", "ouverte", "verrouillee", "allume", "pieces"))


def _entrees(v, vises, profondeur, noeuds):
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
    return json.dumps([
        vises, profondeur, noeuds, None if v.emplois is None else sorted(v.emplois), monde.objets[id]["lieu"],
        [k for k in v.connus if porte_par(monde, k, id)],
        [[s, a, c["valeur"]] for s, d in croyances.items() for a, c in d.items()],
        # Les salles hélées en vain (``_chercher``), tant qu'elles comptent.
        [[q, sorted(appels_vains(monde, id, q))] for q in sorted({s["qui"] for s in esprit_["memoire"]
                                                                   if s["type"] == "appel_sans_reponse"})],
        [[s, minute - s["minute"] < ATTENTE_PART,
          # Une part de bois promise : le feu revu rechargé depuis (``promesse_en_cours``).
          croyances.get(s.get("foyer"), {}).get("etat", {}).get("minute", -1) >= s["minute"]]
         for s in esprit_["memoire"] if s["type"] in ("promis", "nourri")],
        # Les refus retenus, s'ils tiennent (``Vue.refus_tenus``) et s'ils sont récents (``refus_taches``).
        [[s, tenu, minute - s["minute"] < REDEMANDE] for s, tenu in v.refus_tenus()],
        esprit_["visites"],
        # Le lieu d'un objet fixe, sans croyance sur son lieu, se sait sans l'avoir vu (``_lieu_cru``).
        [[k, {a: w for a, w in o.items() if a not in CHANGEANTS}, "allume" in o,
          None if o.get("mobile") or "lieu" in croyances.get(k, ()) else o.get("lieu")]
         for k, o in monde.objets.items()],
        [[o, v.proprietaire[o]] for o in v.connus], v.salles, v.gardes,
        # Ce qu'un prêt ou une garde permettent (``biens.permis``), ce qu'il peut payer et ce que
        # vaut pour lui une pièce.
        [o for o in v.connus if v.illicite[o]], [o for o in v.connus if v.consomme_illicite[o]],
        [o for o in v.connus if v.brise_illicite[o]],
        v.richesse, v.piece,
        # Ce qu'une source allumée ou posée depuis apporte devant un objet où il a vu la lumière.
        [[o, v.apport(o)] for o in v.connus if "lumiere" in croyances.get(o, ())]], ensure_ascii=False)


def chercher(monde, id, but, vises=None, depuis=None, profondeur=PROFONDEUR, noeuds=NOEUDS, nom="", memo=None,
             emplois=None, motif=None, tenir=False, endurer=None, seul=None):
    """Le plan le moins coûteux vers ``but`` (une fonction de la vue et de l'état), ou None,
    depuis l'état ``depuis`` (par défaut, ce qu'il croit maintenant). ``nom`` désigne le but
    dans les diagnostics.

    ``emplois`` dit ce que le but peut employer : "manger" (un repas), "feu" (un feu à charger,
    allumer). Il borne ce qu'il vaut la peine de porter (``Vue.pertinent``) ; None : tout.

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

    ``seul`` : par ses seuls moyens, sans rien demander, acheter ni payer à un autre que ``seul`` (celui
    qui le paie), ni chercher quelqu'un d'autre pour cela (``TIERS``)."""
    from .caractere import modificateur, prix_faute
    debut = perf_counter()
    v = Vue(monde, id)
    faute = prix_faute(monde, id, motif)
    v.degat = prix_faute(monde, id, motif, "douceur")
    v.emplois = None if emplois is None else frozenset(emplois)
    v.seul = seul
    garde = graphe = None
    repris = False
    if memo is not None and depuis is None:
        # Ce que la recherche lit de son caractère et de son état : l'adresse modulée qui fait la
        # chance de crocheter, la force celle de forcer ; s'il envisage d'abîmer. Les gestes et leurs
        # coûts en dépendent, non du prix d'une faute ni de celui d'abîmer (``_explorer``).
        base = (_entrees(v, vises, profondeur, noeuds),
                json.dumps([modificateur(monde, id, "DEX"), modificateur(monde, id, "FOR"), tenir, v.degat is None,
                            seul]))
        entrees = (base, json.dumps([faute, v.degat, endurer]))
        place = (id, json.dumps(memo, ensure_ascii=False))
        garde = _MEMOIRE.get(place)
        if garde is not None and garde[0] != entrees:
            garde = None
        if garde is None:
            # Le graphe n'est gardé qu'à la deuxième recherche de suite sur les mêmes entrées : celles
            # qui changent à chaque fois n'en encombrent pas la mémoire.
            vu = _GRAPHES.get(place)
            if vu is None or vu[0] != base:
                _GRAPHES[place] = (base, None)
            elif vu[1] is None:
                graphe = {}
                _GRAPHES[place] = (base, graphe)
            else:
                graphe, repris = vu[1], True
    if garde is not None:
        _, trouve, issue = garde
        examines = etats = plus_profond = 0
        trouve = None if trouve is None else (trouve[0], copy.deepcopy(trouve[1]), trouve[2])
    else:
        trouve, examines, etats, plus_profond = _explorer(v, depuis or depart(monde, id, v), but, vises, profondeur,
                                                          noeuds, faute, tenir, graphe)
        issue = "plan" if trouve else "borne" if examines >= noeuds else "epuise"
        if endurer is not None and _endure(v, trouve, depuis, endurer):
            trouve, issue = None, "endure"
        if memo is not None and depuis is None:
            _MEMOIRE[place] = (entrees, None if trouve is None else (trouve[0], copy.deepcopy(trouve[1]), trouve[2]),
                               issue)
    if VERIFIER and (garde is not None or repris or v.emplois is not None):
        brute = Vue(monde, id)
        brute.degat, brute.seul = v.degat, seul
        refait = _explorer(brute, depuis or depart(monde, id, brute), but, vises, profondeur, noeuds, faute, tenir)[0]
        if endurer is not None and _endure(brute, refait, depuis, endurer):
            refait = None
        assert refait == trouve, (f"Recherche de {id} ({nom}, {'mémoire' if garde else 'graphe' if repris else 'emplois'}) : "
                                  f"{trouve} au lieu de {refait}")
    if DIAGNOSTIC is not None:
        DIAGNOSTIC.append({"minute": monde.data["minutes"], "pnj": id, "but": nom, "noeuds": examines,
                           "etats": etats, "profondeur": plus_profond, "issue": issue, "memoire": garde is not None,
                           "graphe": repris and garde is None, "etapes": len(trouve[1]) if trouve else None,
                           "duree": round(perf_counter() - debut, 6)})
    return trouve


def _endure(v, trouve, depuis, gain):
    """Le plan trouvé lui coûte-t-il autant que de rester où il est, avec ce que son état présent
    laisse monter, plus le ``gain`` que le but apporte d'autre ? Il ne s'y tient pas déjà (le plan
    a des étapes)."""
    return bool(trouve and trouve[1]) and trouve[0] >= RESTER * v.pression(depuis or depart(v.monde, v.id, v)) + gain


def _explorer(v, depart_, but, vises, profondeur, noeuds, faute, tenir=False, graphe=None):
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
    comprises."""
    ordre = count()
    infini = float("inf")
    degat = v.degat
    file = [(0, next(ordre), depart_, [], 0, False)]
    vus = {depart_: 0}
    examines = plus_profond = 0
    trouve = None
    while file and examines < noeuds:
        cout, _, e, etapes, n, final = heapq.heappop(file)
        if final:
            trouve = cout, copy.deepcopy(etapes), e
            break
        if vus.get(e, infini) < cout:
            continue
        examines += 1
        plus_profond = max(plus_profond, n)
        noeud = None if graphe is None else graphe.get(e)
        if noeud is None:
            noeud = [but(v, e), None, None, None]
            if graphe is not None:
                graphe[e] = noeud
        if noeud[0]:
            if not tenir:
                trouve = cout, copy.deepcopy(etapes), e
                break
            if noeud[1] is None:
                noeud[1] = v.pression(e)
            heapq.heappush(file, (cout + RESTER * noeud[1], next(ordre), e, etapes, n, True))
        if n >= profondeur:
            continue
        if noeud[3] is None:
            # Une flamme allumée par le plan se consume : on l'allume le plus tard possible.
            noeud[2] = sum(1 for k in e.portes if e.fait("allume", k))
            noeud[3] = _suites(v, e, vises, but)
        en_feu = noeud[2]
        for fautes, minutes, ajout, suivant, duree, abime, pression in noeud[3]:
            if fautes and faute is None:
                continue
            surcout = degat if abime else 0   # un prix qui n'est pas du temps (abîmer)
            total = cout + fautes * (faute or 0) + surcout + minutes * (1 + FLAMME_EN_MAIN * en_feu)
            if duree:
                total += duree * pression  # Le temps qu'il passe dans le noir, ou loin de ses biens.
            if total < vus.get(suivant, infini):
                vus[suivant] = total
                heapq.heappush(file, (total, next(ordre), suivant, etapes + ajout, n + 1, False))
    return trouve, examines, len(vus), plus_profond


def _suites(v, e, vises, but):
    """Les gestes depuis ``e`` qui mènent quelque part, chacun avec les termes de son coût : (fautes,
    minutes, étapes, état suivant, durée, abîme, ce que l'état suivant laisse monter par minute)."""
    suites = []
    for geste in gestes(v, e, vises, but):
        fautes, minutes, ajout, suivant = geste[:4]
        if v.seul and any(x["operation"] in TIERS and x["cible"] != v.seul
                          or (x.get("contenu") or {}).get("cherche") not in (None, v.seul) for x in ajout):
            continue   # Un devis ne compte pas sur ce qu'un tiers donnerait, vendrait ou ferait.
        duree = geste[4] if len(geste) > 4 else minutes
        if any(cle[0] in TERMINAUX and cle not in e.faits for cle in suivant.faits) and not but(v, suivant):
            continue
        suites.append((fautes, minutes, ajout, suivant, duree, geste[5] if len(geste) > 5 else False,
                       v.pression(suivant) if duree else 0))
    return suites


# --- Buts ---------------------------------------------------------------------------------

def _premier(e, sorte):
    return next(((cle[1], valeur) for cle, valeur in sorted(e.faits.items(), key=str) if cle[0] == sorte), None)


def a_mange(v, e):
    return _premier(e, "mange") is not None or any(
        cle[0] == "part" and v.monde.objets[cle[1]]["type"] == "nourriture" for cle in e.faits)


def rechauffe(v, e):
    return _premier(e, "chauffe") is not None or any(
        cle[0] == "part" and besoin_de_part(v.monde.objets[cle[1]]) == "chaleur" for cle in e.faits)


def retablir(v, e, etapes):
    """Ce qu'il garde sous clé et auquel le plan a touché, il le referme à clé avant de finir."""
    for x in profil(v.monde, v.id)["pulsions"]:
        cible = x["condition"].get("objet")
        if not x["condition"].get("verrouillee") or not e.fait("touche", cible):
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
    # Se chauffer se tient près du feu : ce que ce lieu laisse monter compte.
    trouve = chercher(monde, id, but, nom=besoin, memo=["besoin", besoin],
                      emplois={"faim": ("manger",), "chaleur": ("feu",)}[besoin], motif=besoin,
                      tenir=besoin == "chaleur")
    if trouve is None:
        return None
    _, etapes, e = trouve
    return _resultat(Vue(monde, id), e, _couper(etapes), besoin)


def _couper(etapes):
    """Après une recherche de quelqu'un, le plan s'arrête : la suite se décide sur ce qu'il aura vu."""
    fin = next((i + 1 for i, x in enumerate(etapes) if x.pop("suppose", False)), len(etapes))
    return etapes[:fin]


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


def devis_pulsion(monde, id, condition, payeur):
    """(coût, étapes) de rétablir ``condition`` (minutes de son plan, fautes comprises), ou None s'il
    ne voit pas comment : ce qu'une tâche qu'on lui propose lui coûterait (``echanges.engager``). Un
    feu qu'on le paie d'entretenir, il le compte à recharger et rallumer, pas seulement à aller
    voir : celui qui le paie le sait à entretenir. Par ses seuls moyens, ce que la garde du bien de
    ``payeur`` lui permet et ce que ``payeur`` lui prêterait : il ne compte pas sur ce qu'un tiers lui
    donnerait ou vendrait."""
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
        trouve = _remettre(monde, id, o, condition)
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
        but = lambda v, e: o not in e.portes and v.lieu(e, o) == lieu  # noqa: E731
        vises = {"prendre": (o,), "poser": (o,)}
    else:
        but = lambda v, e: v.verrouille(e, o) and not v.ouvert(e, o)  # noqa: E731
        vises = {"fermer": (o,)}
    if tache and sorte(condition) and "allume" not in condition:
        vises["confier"] = (dict(condition),)
    depuis = None
    if entretenir and "allume" in condition:
        # Celui qui le paie le sait à recharger : il le compte comme tel, quoi qu'il en ait vu.
        depuis = depart(monde, id).apres(faits=[(("charge", o), False)])
    trouve = chercher(monde, id, but, vises, depuis=depuis, nom=_nom_condition(condition),
                      memo=["pulsion", condition, "confier" in vises, entretenir],
                      emplois=("feu",) if "allume" in condition else (), seul=entretenir or None)
    if trouve is None:
        return None
    cout, etapes, e = trouve
    return cout, {"type": "pulsion", **condition}, retablir(Vue(monde, id), e, _couper(etapes))


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


def _remettre(monde, id, o, condition):
    """Un objet qu'il a vendu sans le porter (``echanges.differee``) : l'aller chercher, puis
    rejoindre l'acheteur et le lui remettre."""
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
    """(but, étapes) pour prendre des pièces (un objet qu'il croit en contenir, qui n'est pas à lui)
    qui valent pour lui plus que ce qu'il en coûte d'aller les prendre, faute comprise ; None sinon.
    L'argent ne presse jamais : aucune détresse n'use le prix de la faute (``caractere.ARGENT``).

    Il compte les pièces qu'il croit dedans (croyance ``pieces`` : su en la tenant, ou un savoir
    du scénario), jamais celles qui y sont : une bourse dont il ne sait rien ne le tente pas."""
    from .caractere import ARGENT, prix_faute, valeur_pieces
    if not profil(monde, id):
        return None
    crues = {o: _cru(monde, id, o, "pieces") for o in _connus(monde, id)}
    if not any(crues.values()):
        return None
    v = Vue(monde, id)
    faute = prix_faute(monde, id, ARGENT)
    # Ce qu'il ne peut prendre (son honnêteté l'interdit, la faute passe l'enjeu), ou qui vaut moins
    # que la seule faute de le prendre, ne se cherche pas : aucun plan n'en vaudrait la peine.
    bourses = tuple(o for o in v.connus if crues[o] and v.proprietaire[o] != id
                    and not porte_par(monde, o, id) and v.disponible(o) and v.autorise[o]
                    and (not v.illicite[o] or faute is not None and valeur_pieces(monde, id, crues[o]) > faute))
    if not bourses:
        return None
    trouve = chercher(monde, id, lambda v, e: any(b in e.portes for b in bourses), {"prendre": bourses},
                      nom="argent", memo=["argent"], emplois=(), motif=ARGENT)
    if trouve is None:
        return None
    cout, etapes, e = trouve
    pris = next(b for b in bourses if b in e.portes)
    if valeur_pieces(monde, id, crues[pris]) <= cout:
        return None  # Ces pièces ne valent pas, pour lui, ce qu'il lui en coûterait.
    return {"type": "argent", "objet": pris}, retablir(v, e, _couper(etapes))


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
    v = Vue(monde, id)
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


def s_enquerir(monde, id, besoin):
    """(but, étapes) pour demander à quelqu'un s'il a de quoi apaiser ``besoin`` (des vivres, du
    bois : ``echanges.enqueter``), quand rien de ce qu'il connaît n'y pourvoit : à qui il ne connaît
    rien de tel, qu'il ne se méfie pas et dont la réponse refusée ne tient plus (``deliberation.tient``),
    le plus proche de là où il le croit. None s'il n'a personne à qui le demander."""
    if not profil(monde, id):
        return None
    v = Vue(monde, id)
    e = depart(monde, id, v)
    # Qui n'en a pas, il ne le lui redemande pas tant que rien de ce qu'il croit de ces ressources n'a
    # changé ; qui s'est méfié, pas avant ``REDEMANDE`` minutes (``deliberation.tient``).
    interroges = {s["de"] for s in lire(monde, id).get("refus", ()) if s["operation"] == "enqueter"
                  and s.get("besoin") == besoin and tient(monde, id, s, v.connus)}
    connus = {v.proprietaire[o] for o in v.connus if v.besoin[o] == besoin}
    candidats = []
    for autre in v.personnes():
        salle = v.salle(e, autre)
        if autre in interroges or autre in connus or salle is None or v.cru(autre, "fiable") is False:
            continue
        longueur = v.trajet(e.salle, salle)
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
    None s'il n'y croit aucun passage."""
    trouve = chercher(monde, id, lambda v, e: e.fait("inspecte", salle), {"inspecter": (salle,)},
                      nom="voir:" + salle, memo=["voir", salle], emplois=())
    if trouve is None:
        return None
    return {"type": "voir", "lieu": salle}, _couper(trouve[1])


def eclaire(v, e):
    return v.lumiere(e) > 0


def eclairer(monde, id):
    """(but, étapes) pour avoir de la lumière là où il se tient, quand le noir l'inquiète ; None
    s'il y voit déjà, ou ne voit aucun moyen. Les moyens viennent des gestes déclarés : allumer
    une source qu'il porte ou qui est à portée, à une flamme qu'il porte ou à une flamme fixe ;
    prendre une source, la recharger du combustible qu'elle brûle ; la demander à qui la porte ;
    rejoindre un lieu qu'il croit éclairé."""
    v = Vue(monde, id)
    if not peur_du_noir(monde, id) or eclaire(v, depart(monde, id, v)):
        return None
    trouve = chercher(monde, id, eclaire, nom="lumiere", memo=["lumiere"], emplois=("lumiere",), motif="securite",
                      tenir=True, endurer=0)
    if trouve is None:
        return None
    _, etapes, e = trouve
    return {"type": "lumiere"}, retablir(v, e, _couper(etapes))


def garder(monde, id, salle):
    """Les étapes pour se tenir là où il garde ses biens, ou None. Il y restera : ce que le lieu
    laisse monter compte (le noir qu'il craint : il y porte de la lumière s'il le peut) ; s'il n'y
    est pas, il n'y va que si cela lui coûte moins que rester où il est, sinon il endure."""
    trouve = chercher(monde, id, lambda v, e: e.salle == salle, nom="garder:" + salle, memo=["garder", salle],
                      emplois=(), motif="biens", tenir=True, endurer=0)
    return None if trouve is None else retablir(Vue(monde, id), trouve[2], _couper(trouve[1]))


def abri(monde, id, salles):
    """(salle, étapes) pour gagner l'un des abris ``salles`` (éclairés, quelqu'un de sûr s'y
    tient), le moins coûteux avec ce qu'il y laissera monter en y restant ; None s'il n'en atteint
    aucun, ou si y aller lui coûte plus que d'endurer où il est : ce que l'abri lui apporte (y voir,
    ne plus côtoyer qui l'inquiète, une compagnie sûre, aux taux de son profil, ``NOIR`` par
    point) ne vaut pas ce qu'il laisse (ses biens).

    Quitter qui l'inquiète n'est pas un gain là où il garde un bien que cette présence menace
    (``deliberation.menaces``) : s'en aller, c'est le lui laisser, et cet éloignement lui coûte
    (``GARDE``) comme à tout plan."""
    from .deliberation import menaces, taux
    v = Vue(monde, id)
    e = depart(monde, id, v)
    ici = [x for x in v.connus + ["joueur"] if x != id and (x == "joueur" or v.objets[x]["type"] == "personnage")
           and v.salle(e, x) == e.salle]
    fuir = any(v.cru(x, "fiable") is False for x in ici) and e.salle not in menaces(monde, id)
    gain = ((taux(monde, id, "noir") + taux(monde, id, "lumiere") if v.peur and v.noir(e) else 0)
            + (taux(monde, id, "mefiance") if fuir else 0)
            + (0 if any(v.cru(x, "fiable") is True for x in ici) else taux(monde, id, "compagnie")))
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
    v = Vue(monde, id)
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
