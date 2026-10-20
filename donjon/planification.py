"""Planificateur par recherche : le PNJ cherche, sur ce qu'il croit, la suite de gestes la
moins coûteuse qui atteint son but.

Chaque geste est déclaré une fois : ses conditions sur l'état cru, ses effets, son coût. Le
caractère entre dans les coûts : une limite interdit un geste ; s'en prendre au bien d'autrui
est une faute, comptée une fois par personne lésée, et un plan qui en a moins passe toujours
avant ; demander coûte un peu ; un geste difficile coûte selon sa chance de réussir. La recherche part de ce que le PNJ
croit (jamais de la vérité du monde) et simule ce que le plan change à mesure : ce qu'il aura
pris, ouvert, déverrouillé, allumé, où il se tiendra.

Le choix du but reste à ``deliberation.candidats`` ; l'exécution, geste par geste revalidé sur
l'état réel, à ``pnj.agir``. Le stratège complète ses gestes par la même recherche.
"""
import copy
import heapq
import json
from contextlib import contextmanager
from itertools import count
from time import perf_counter

from .deliberation import (ATTENTE_PART, REDEMANDE, _connus, _cru, _disponible_cru, _eclairee_crue, _lieu_cru,
                           autorise, besoin_de_part, illicite, profil, promesse_en_cours, refuse_recemment)
from .esprits import lire
from .spatial import porte_par

PROFONDEUR = 8         # gestes au plus dans un plan (un trajet compte pour un)
NOEUDS = 4000          # états examinés au plus
DEMANDE = 3            # demander : on préfère ce qu'on peut faire seul
PRET = 0.5             # chance qu'il prête à quelqu'un qui demande un objet qu'il porte
CHERCHER = 3           # chercher quelqu'un qu'on a perdu de vue : on n'est pas sûr de le trouver
FLAMME_EN_MAIN = 1     # par minute, tant qu'une flamme allumée par le plan se consume en main
CHANCE_MIN = 0.05
# Effets qui achèvent un but sans rien permettre ensuite : un geste qui les produit sans
# atteindre le but cherché ne mène nulle part (se chauffer quand on a faim).
TERMINAUX = ("mange", "part", "chauffe", "inspecte", "servi")
# Usages que les gestes savent employer : un objet n'est pris que s'il peut servir à l'un d'eux.
USAGES = ("crochetage", "allumage", "combustible")
# Chaque recherche s'y consigne quand le banc le demande (``diagnostics``) ; sinon None.
DIAGNOSTIC = None
# Le dernier résultat de chaque PNJ pour chaque but, avec tout ce dont il dépendait. Il ne tient
# pas à l'objet monde : le moteur agit sur une copie de travail à chaque action.
_MEMOIRE = {}
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


class Etat:
    """Où il se tient, ce qu'il porte, et ce que le plan a changé à ce qu'il croit."""
    __slots__ = ("salle", "portes", "faits", "_cle")

    def __init__(self, salle, portes, faits):
        self.salle, self.portes, self.faits = salle, frozenset(portes), dict(faits)
        self._cle = (salle, self.portes, frozenset(self.faits.items()))

    def __eq__(self, autre):
        return self._cle == autre._cle

    def __lt__(self, autre):
        return False

    def __hash__(self):
        return hash(self._cle)

    def apres(self, salle=None, portes=None, faits=()):
        return Etat(self.salle if salle is None else salle, self.portes if portes is None else portes,
                    {**self.faits, **dict(faits)})

    def fait(self, *cle):
        return self.faits.get(cle)


class Vue:
    """Ce que le PNJ croit, corrigé de ce que le plan a déjà changé.

    Ses croyances ne bougent pas pendant une recherche : chaque lecture est faite une fois."""

    def __init__(self, monde, id):
        from .pnj import chemin
        from .vol import proprietaire
        self.monde, self.id = monde, id
        self.objets = monde.objets
        self.salles = monde.data["salles"]
        self.connus = _connus(monde, id)
        self.illicite = {o: illicite(monde, id, o) for o in self.connus}
        self.autorise = {o: autorise(monde, id, o) for o in self.connus}
        self.proprietaire = {o: proprietaire(monde, monde.objets[o]) for o in self.connus}
        # Ce qu'un geste sait employer (``gestes``) : clé, outil, vivres, combustible, flamme portable.
        self.utile = {o: bool(x.get("ouvre") or set(x.get("usages", [])) & set(USAGES) or x["type"] == "nourriture"
                              or "allume" in x) for o in self.connus for x in [self.objets[o]]}
        self._chemin = chemin
        self._routes, self._trajets, self._crus, self._agissables = {}, {}, {}, {}
        self.emplois = None    # ce que le but peut employer (``chercher``) ; None : tout

    def agissables(self, vises):
        """(objets, à porter) : les objets connus sur lesquels un geste est possible (``gestes``)
        — ce qu'un geste sait employer, un contenant, un foyer, ce que vise le but ; les autres ne
        donnent jamais rien — et, parmi eux, ceux qu'il vaut la peine de porter (``pertinent``)."""
        noms = frozenset(o for k in ("prendre", "poser", "fermer", "servir") for o in vises.get(k, ()))
        if noms not in self._agissables:
            objets = [o for o in self.connus if self.utile[o] or o in noms
                      or self.objets[o]["type"] == "contenant" or self.objets[o].get("foyer")]
            self._agissables[noms] = objets, {o for o in objets if self.pertinent(o, noms)}
        return self._agissables[noms]

    def pertinent(self, o, vises):
        """Le porter peut-il servir le but ? Une clé (passages, contenants), un contenant, ce que
        vise le but (``vises`` : leurs noms) ; les vivres si le but peut employer un repas ;
        combustible et flammes s'il peut employer un feu ; outil de crochetage et lumière s'il
        sait crocheter.

        Porter autre chose ne change ni les gestes possibles ni leur coût : le prendre ne fait
        qu'ajouter des minutes, le plan le moins coûteux n'en passe jamais par là, et la
        recherche rend le même résultat sans explorer ces détours."""
        if self.emplois is None:
            return True
        x = self.objets[o]
        usages = x.get("usages", [])
        return bool(x.get("ouvre") or x["type"] == "contenant" or o in vises
                    or "manger" in self.emplois and x["type"] == "nourriture"
                    or "feu" in self.emplois and ("combustible" in usages or "allumage" in usages or "allume" in x)
                    or "crochetage" in profil(self.monde, self.id)["capacites"]
                    and ("crochetage" in usages or "allume" in x))

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

    def refuse(self, autre, o):
        return self._memo((autre, o, "refus"), lambda: refuse_recemment(self.monde, self.id, autre, "demander", o))

    def promesse(self, o):
        return self._memo((o, "promesse"), lambda: promesse_en_cours(self.monde, self.id, o))

    def route(self, depart, arrivee, portes):
        trajet = (depart, arrivee, portes)
        if trajet in self._trajets:
            return self._trajets[trajet]
        cles = frozenset(k for k in portes if self.objets[k].get("ouvre"))
        cle = (depart, arrivee, cles)
        if cle not in self._routes:
            self._routes[cle] = self._chemin(self.monde, self.id, depart, arrivee, cles)
        self._trajets[trajet] = self._routes[cle]
        return self._routes[cle]

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

    def foyer_froid(self):
        """Le feu qu'une part de bois servirait : le premier foyer qu'il croit éteint."""
        if "foyer_froid" not in self._crus:
            self._crus["foyer_froid"] = next((f for f in self.connus if self.objets[f].get("foyer")
                                              and (self.cru(f, "etat") or {}).get("allume") is False), None)
        return self._crus["foyer_froid"]

    def lumiere(self, e):
        if any("allume" in self.objets[k] and self.feu(e, k)[0] for k in e.portes):
            return 2
        return 2 if _eclairee_crue(self.monde, self.id, e.salle) else 0


def _etape(operation, cible="", outil="", lieu="", condition="", contenu=None):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu, "condition": condition,
            **({"contenu": contenu} if contenu else {})}


def chance_crochetage(monde, id, lumiere):
    """Comme le jet de ``pnj._crocheter`` : d20 + DEX contre 14, plus 4 par niveau de lumière manquant."""
    dex = profil(monde, id)["caracteristiques"]["DEX"]
    reussites = 21 - (14 + 4 * (2 - lumiere) - (dex - 10) // 2)
    return min(1.0, max(CHANCE_MIN, reussites / 20))


def gestes(v, e, vises=None, but=None):
    """Les gestes possibles depuis cet état : (fautes, minutes, étapes, état suivant). Les
    fautes comptent les personnes lésées.

    ``vises`` ouvre les gestes que seul un but demande, sur les objets ou lieux qu'il vise :
    inspecter une salle, prendre un objet qui ne sert à aucun geste, poser, fermer et
    verrouiller, servir une part à quelqu'un. Les offrir partout élargirait la recherche sans
    rien lui apprendre."""
    monde, id = v.monde, v.id
    vises = vises or {}
    p = profil(monde, id)
    objets = v.objets
    # Aller : un trajet vers toute salle qu'il croit atteindre avec ce qu'il porte.
    for s in sorted(v.salles):
        if s != e.salle:
            route = v.route(e.salle, s, e.portes)
            if route is not None:
                yield 0, len(route), [_etape("aller", lieu=s)], e.apres(salle=s)
    agissables, a_porter = v.agissables(vises)
    for o in agissables:
        x = objets[o]
        ici = v.a_portee(e, o)
        dans = v.lieu(e, o)
        contenant = dans if dans in objets and objets[dans]["type"] == "contenant" else None
        touche = [(("touche", contenant), True)] if contenant else []
        faute = "sans_temoin" if v.illicite[o] else ""
        lese = v.proprietaire[o] if v.illicite[o] else None
        mal = int(bool(lese) and not e.fait("faute", lese))
        if lese:
            touche = touche + [(("faute", lese), True)]
        # Prendre ce qu'un geste sait employer : clé, outil, vivres, combustible, flamme portable.
        utile = (v.utile[o] or o in vises.get("prendre", ())) and o in a_porter
        if ici and o not in e.portes and x.get("mobile") and v.autorise[o] and v.disponible(o) and utile:
            yield mal, 1, [_etape("prendre", o, condition=faute)], e.apres(portes=e.portes | {o}, faits=touche)
        # Le demander à qui le porte, s'il est là : il peut refuser, le plan se refait alors.
        porteur = dans if dans in objets and objets[dans]["type"] == "personnage" else None
        if (utile and porteur and porteur != id and profil(monde, porteur) and v.salle(e, porteur) == e.salle
                and o not in e.portes and not v.refuse(porteur, o)):
            yield 0, 1 + DEMANDE / PRET, [_etape("demander", porteur, outil=o)], e.apres(portes=e.portes | {o})
        touche = [x for x in touche if x[0][0] == "faute"]
        if o in vises.get("poser", ()) and o in e.portes:
            yield (0, 1, [_etape("poser", o, lieu=e.salle)],
                   e.apres(portes=e.portes - {o}, faits=[(("lieu", o), e.salle)]))
        if o in vises.get("fermer", ()) and v.salle(e, o) == e.salle:
            if v.ouvert(e, o):
                yield 0, 1, [_etape("fermer", o)], e.apres(faits=[(("ouvert", o), False)])
            elif not v.verrouille(e, o):
                for cle in sorted(k for k in e.portes if o in objets[k].get("ouvre", [])):
                    yield 0, 1, [_etape("verrouiller", o, outil=cle)], e.apres(faits=[(("verrou", o), True)])
        for pour in vises.get("servir", {}).get(o, ()):
            if ici and v.disponible(o):
                dedans = [(("touche", contenant), True)] if contenant else []
                yield (mal, 1, [_etape("servir", o, condition=faute, contenu={"pour": pour})],
                       e.apres(faits=[(("servi", o), pour), *dedans, *touche]))
        if x["type"] == "contenant" and v.salle(e, o) == e.salle:
            ouvert, verrou = v.ouvert(e, o), v.verrouille(e, o)
            if not ouvert and not verrou and v.autorise[o]:
                yield (mal, 1, [_etape("ouvrir", o, condition=faute)],
                       e.apres(faits=[(("ouvert", o), True), (("touche", o), True), *touche]))
            if verrou and not ouvert:
                for cle in sorted(k for k in e.portes if o in objets[k].get("ouvre", [])):
                    yield (0, 1, [_etape("deverrouiller", o, outil=cle, condition=faute)],
                           e.apres(faits=[(("verrou", o), False), (("touche", o), True)]))
                if "crochetage" in p["capacites"] and v.autorise[o]:
                    for outil in sorted(k for k in e.portes if "crochetage" in objets[k].get("usages", [])):
                        chance = chance_crochetage(monde, id, v.lumiere(e))
                        yield (mal, 1 / chance, [_etape("crocheter", o, outil=outil, condition=faute)],
                               e.apres(faits=[(("verrou", o), False), (("touche", o), True), *touche]))
        # Manger ce qui est à portée.
        if x["type"] == "nourriture" and ici and v.disponible(o) and v.autorise[o]:
            porte = o in e.portes
            dedans = [(("touche", contenant), True)] if contenant else []
            yield (0 if porte else mal, 1, [_etape("manger", o, condition="" if porte else faute)],
                   e.apres(faits=[(("mange", o), True), *dedans, *([] if porte else touche)]))
        # Un foyer : le recharger, l'allumer, s'y chauffer.
        if x.get("foyer") and v.salle(e, o) == e.salle:
            allume, charge = v.feu(e, o)
            if not (allume and charge):
                for bois in sorted(k for k in e.portes if "combustible" in objets[k].get("usages", [])
                                   and v.disponible(k)):
                    yield 0, 1, [_etape("alimenter", o, outil=bois)], e.apres(faits=[(("charge", o), True)])
            if allume is False and charge:
                for flamme in sorted(k for k in e.portes if k != o and v.flamme(e, k)):
                    yield 0, 1, [_etape("allumer", o, outil=flamme)], e.apres(faits=[(("allume", o), True)])
            if allume:
                yield 0, 1, [_etape("chauffer", o)], e.apres(faits=[(("chauffe", o), True)])
        # Une source portable éteinte et chargée s'allume à une flamme fixe qu'il croit vive.
        if (o in e.portes and "allume" in x and x.get("mobile") and v.feu(e, o)[0] is False
                and (v.cru(o, "etat") or {}).get("charge")):
            for fixe in v.connus:
                if (fixe != o and "allume" in objets[fixe] and not objets[fixe].get("mobile")
                        and v.salle(e, fixe) == e.salle and v.feu(e, fixe)[0]):
                    yield 0, 1, [_etape("allumer", o, outil=fixe)], e.apres(faits=[(("allume", o), True)])
        # Une part : l'attendre si elle est promise, là où le donneur viendra la servir (près des
        # vivres, ou du feu qu'il entretiendra) ; sinon la demander à son propriétaire.
        if besoin_de_part(x) and v.disponible(o):
            donneur = v.proprietaire[o]
            foyer = v.foyer_froid() if besoin_de_part(x) == "chaleur" else None
            if donneur not in (None, id, "joueur") and profil(monde, donneur):
                if v.promesse(o) == donneur:
                    if e.salle == (v.salle(e, foyer) if foyer else v.salle(e, o)):
                        yield 0, 0, [], e.apres(faits=[(("part", o), donneur)])
                elif not v.refuse(donneur, o):
                    ou = v.salle(e, donneur)
                    if ou == e.salle:
                        yield (0, 1 + DEMANDE, [_etape("demander", donneur, outil=o,
                                                        contenu={"foyer": foyer} if foyer else None)],
                               e.apres(faits=[(("part", o), donneur)]))
                    elif (ou is None and not e.fait("cherche", donneur)
                          and (but is None or but(v, e.apres(faits=[(("part", o), donneur)])))):
                        # Le chercher ne sert que si sa part atteint le but.
                        yield _chercher(v, e, donneur)
    for salle in vises.get("inspecter", ()):
        if salle == e.salle and not e.fait("inspecte", salle):
            yield 0, 1, [_etape("inspecter", lieu=salle)], e.apres(faits=[(("inspecte", salle), True)])


def _chercher(v, e, sujet):
    """Perdu de vue : il va le chercher là où il est passé le moins récemment, et l'y suppose.
    Le plan s'arrête après cette recherche : la suite se décide sur ce qu'il aura vu."""
    visites = lire(v.monde, v.id)["visites"]
    routes = {s: v.route(e.salle, s, e.portes) for s in v.salles}
    routes = {s: r for s, r in routes.items() if r is not None}
    salle = min(routes, key=lambda s: (visites.get(s, -1), len(routes[s]), s))
    etapes = ([_etape("aller", lieu=salle)] if salle != e.salle else []) + [{**_etape("inspecter", lieu=salle),
                                                                              "suppose": True}]
    return 0, len(routes[salle]) + 1 + CHERCHER, etapes, e.apres(
        salle=salle, faits=[(("lieu", sujet), salle), (("cherche", sujet), True)])


def depart(monde, id, v=None):
    v = v or Vue(monde, id)
    return Etat(monde.objets[id]["lieu"], [k for k in v.connus if porte_par(monde, k, id)], {})


# Ce qui change d'une minute à l'autre dans un objet, et qu'une recherche ne lit jamais : elle lit
# ce qu'il en croit. Le lieu vrai n'y entre que par ce qu'il porte, les propriétaires et les
# objets fixes (``_entrees``).
CHANGEANTS = frozenset(("lieu", "position", "position_salle", "orientation", "corps", "humeur", "combustible",
                        "portions", "charges", "ouverte", "verrouillee", "allume"))


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
        [[s, minute - s["minute"] < (REDEMANDE if s["type"] == "refus" else ATTENTE_PART)]
         for s in esprit_["memoire"] if s["type"] in ("refus", "promis", "nourri")],
        esprit_["visites"],
        # Le lieu d'un objet fixe, sans croyance sur son lieu, se sait sans l'avoir vu (``_lieu_cru``).
        [[k, {a: w for a, w in o.items() if a not in CHANGEANTS}, "allume" in o,
          None if o.get("mobile") or "lieu" in croyances.get(k, ()) else o.get("lieu")]
         for k, o in monde.objets.items()],
        [[o, v.proprietaire[o]] for o in v.connus], v.salles], ensure_ascii=False)


def chercher(monde, id, but, vises=None, depuis=None, profondeur=PROFONDEUR, noeuds=NOEUDS, nom="", memo=None,
             emplois=None):
    """Le plan le moins coûteux vers ``but`` (une fonction de la vue et de l'état), ou None,
    depuis l'état ``depuis`` (par défaut, ce qu'il croit maintenant). ``nom`` désigne le but
    dans les diagnostics.

    ``emplois`` dit ce que le but peut employer : "manger" (un repas), "feu" (un feu à charger,
    allumer). Il borne ce qu'il vaut la peine de porter (``Vue.pertinent``) ; None : tout.

    ``memo`` (une description JSON du but, qui le détermine avec ce qu'il croit) garde le
    résultat : tant que rien de ce que lit la recherche n'a changé (``_entrees``), le même but
    rend le même résultat sans refaire la recherche.

    Le coût est (personnes lésées, minutes) : le moins fautif d'abord. Renvoie
    (coût, étapes, état final)."""
    debut = perf_counter()
    v = Vue(monde, id)
    v.emplois = None if emplois is None else frozenset(emplois)
    garde = None
    if memo is not None and depuis is None:
        entrees = _entrees(v, vises, profondeur, noeuds)
        place = (id, json.dumps(memo, ensure_ascii=False))
        garde = _MEMOIRE.get(place)
        if garde is not None and garde[0] != entrees:
            garde = None
    if garde is not None:
        _, trouve, issue = garde
        examines = etats = plus_profond = 0
        trouve = None if trouve is None else (trouve[0], copy.deepcopy(trouve[1]), trouve[2])
    else:
        trouve, examines, etats, plus_profond = _explorer(v, depuis or depart(monde, id, v), but, vises, profondeur,
                                                          noeuds)
        issue = "plan" if trouve else "borne" if examines >= noeuds else "epuise"
        if memo is not None and depuis is None:
            _MEMOIRE[place] = (entrees, None if trouve is None else (trouve[0], copy.deepcopy(trouve[1]), trouve[2]),
                               issue)
    if VERIFIER and (garde is not None or v.emplois is not None):
        brute = Vue(monde, id)
        refait = _explorer(brute, depuis or depart(monde, id, brute), but, vises, profondeur, noeuds)[0]
        assert refait == trouve, (f"Recherche de {id} ({nom}, {'mémoire' if garde else 'emplois'}) : {trouve} "
                                  f"au lieu de {refait}")
    if DIAGNOSTIC is not None:
        DIAGNOSTIC.append({"minute": monde.data["minutes"], "pnj": id, "but": nom, "noeuds": examines,
                           "etats": etats, "profondeur": plus_profond, "issue": issue, "memoire": garde is not None,
                           "etapes": len(trouve[1]) if trouve else None,
                           "duree": round(perf_counter() - debut, 6)})
    return trouve


def _explorer(v, depart_, but, vises, profondeur, noeuds):
    """A* sur les états crus : (trouvé ou None, nœuds examinés, états vus, profondeur atteinte)."""
    ordre = count()
    infini = (float("inf"), float("inf"))
    file = [((0, 0), next(ordre), depart_, [], 0)]
    vus = {depart_: (0, 0)}
    examines = plus_profond = 0
    trouve = None
    while file and examines < noeuds:
        cout, _, e, etapes, n = heapq.heappop(file)
        if vus.get(e, infini) < cout:
            continue
        examines += 1
        plus_profond = max(plus_profond, n)
        if but(v, e):
            trouve = cout, etapes, e
            break
        if n >= profondeur:
            continue
        # Une flamme allumée par le plan se consume : on l'allume le plus tard possible.
        brule = sum(1 for k in e.portes if e.fait("allume", k))
        for fautes, minutes, ajout, suivant in gestes(v, e, vises, but):
            if any(cle[0] in TERMINAUX and cle not in e.faits for cle in suivant.faits) and not but(v, suivant):
                continue
            total = (cout[0] + fautes, cout[1] + minutes * (1 + FLAMME_EN_MAIN * brule))
            if total < vus.get(suivant, infini):
                vus[suivant] = total
                heapq.heappush(file, (total, next(ordre), suivant, etapes + ajout, n + 1))
    return trouve, examines, len(vus), plus_profond


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
    trouve = chercher(monde, id, but, nom=besoin, memo=["besoin", besoin],
                      emplois={"faim": ("manger",), "chaleur": ("feu",)}[besoin])
    if trouve is None:
        return None
    _, etapes, e = trouve
    return _resultat(Vue(monde, id), e, _couper(etapes), besoin)


def _couper(etapes):
    """Après une recherche de quelqu'un, le plan s'arrête : la suite se décide sur ce qu'il aura vu."""
    fin = next((i + 1 for i, x in enumerate(etapes) if x.pop("suppose", False)), len(etapes))
    return etapes[:fin]


def planifier_pulsion(monde, id, condition):
    """(but, étapes) pour rétablir une pulsion (ou tenir une parole donnée), ou None.

    Une ronde : aller inspecter le lieu. Une part à servir. Un objet à remettre en place. Un feu
    à entretenir : aller le voir s'il n'en a pas de nouvelles sûres, sinon le recharger et le
    rallumer. Un objet à garder sous clé : le fermer et le verrouiller."""
    from .deliberation import salle_crue
    v = Vue(monde, id)
    o = condition.get("objet")
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
        if not etat or etat.get("allume") and not etat.get("faible"):
            # Vu vif il y a longtemps, ou jamais vu : il va voir où il en est.
            but, vises = (lambda v, e: e.fait("inspecte", salle)), {"inspecter": (salle,)}
        else:
            but, vises = (lambda v, e: v.feu(e, o) == (True, True)), {}
    elif "lieu" in condition:
        lieu = condition["lieu"]
        but = lambda v, e: o not in e.portes and v.lieu(e, o) == lieu  # noqa: E731
        vises = {"prendre": (o,), "poser": (o,)}
    else:
        but = lambda v, e: v.verrouille(e, o) and not v.ouvert(e, o)  # noqa: E731
        vises = {"fermer": (o,)}
    trouve = chercher(monde, id, but, vises, nom=_nom_condition(condition), memo=["pulsion", condition],
                      emplois=("feu",) if "allume" in condition else ())
    if trouve is None:
        return None
    _, etapes, e = trouve
    return {"type": "pulsion", **condition}, retablir(v, e, _couper(etapes))


def _nom_condition(c):
    sorte = ("ronde" if "periode" in c else "servir" if "servir" in c else "feu" if "allume" in c
             else "placer" if "lieu" in c else "sous_cle")
    return f"{sorte}:{c.get('objet') or c.get('lieu')}"


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
    _, _, etapes, _ = _chercher(v, e, sujet)
    return _couper(etapes), False
