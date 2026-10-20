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
import heapq
from itertools import count

from .deliberation import (_connus, _cru, _disponible_cru, _eclairee_crue, _lieu_cru, autorise, besoin_de_part,
                           illicite, profil, promesse_en_cours, refuse_recemment)
from .esprits import lire
from .spatial import porte_par

PROFONDEUR = 8         # gestes au plus dans un plan (un trajet compte pour un)
NOEUDS = 4000          # états examinés au plus
DEMANDE = 3            # demander : on préfère ce qu'on peut faire seul
CHERCHER = 3           # chercher quelqu'un qu'on a perdu de vue : on n'est pas sûr de le trouver
FLAMME_EN_MAIN = 1     # par minute, tant qu'une flamme allumée par le plan se consume en main
CHANCE_MIN = 0.05
# Effets qui achèvent un but sans rien permettre ensuite : un geste qui les produit sans
# atteindre le but cherché ne mène nulle part (se chauffer quand on a faim).
TERMINAUX = ("mange", "part", "chauffe", "inspecte", "servi")
# Usages que les gestes savent employer : un objet n'est pris que s'il peut servir à l'un d'eux.
USAGES = ("crochetage", "allumage", "combustible")


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
    """Ce que le PNJ croit, corrigé de ce que le plan a déjà changé."""

    def __init__(self, monde, id):
        from .vol import proprietaire
        self.monde, self.id = monde, id
        self.salles = monde.data["salles"]
        self.connus = _connus(monde, id)
        self.illicite = {o: illicite(monde, id, o) for o in self.connus}
        self.autorise = {o: autorise(monde, id, o) for o in self.connus}
        self.proprietaire = {o: proprietaire(monde, monde.objets[o]) for o in self.connus}
        self._routes = {}

    def route(self, depart, arrivee, portes):
        from .pnj import chemin
        cles = frozenset(k for k in portes if self.monde.objets[k].get("ouvre"))
        cle = (depart, arrivee, cles)
        if cle not in self._routes:
            self._routes[cle] = chemin(self.monde, self.id, depart, arrivee, cles)
        return self._routes[cle]

    def lieu(self, e, o):
        if o in e.portes:
            return self.id
        lieu = e.fait("lieu", o)
        return _lieu_cru(self.monde, self.id, o) if lieu is None else lieu

    def salle(self, e, sujet, profondeur=0):
        if sujet in e.portes or sujet == self.id:
            return e.salle
        lieu = self.lieu(e, sujet)
        if lieu is None or profondeur > 4:
            return None
        if lieu in self.salles:
            return lieu
        if lieu == "joueur":
            return _lieu_cru(self.monde, self.id, "joueur")
        return self.salle(e, lieu, profondeur + 1)

    def ouvert(self, e, c):
        v = e.fait("ouvert", c)
        if v is not None:
            return v
        etat = _cru(self.monde, self.id, c, "etat")
        return bool(etat and etat.get("ouverte"))

    def verrouille(self, e, c):
        v = e.fait("verrou", c)
        return v if v is not None else bool(_cru(self.monde, self.id, c, "verrouillee"))

    def feu(self, e, f):
        """(allumé, chargé) tels qu'il les croit ; inconnus : None."""
        etat = _cru(self.monde, self.id, f, "etat") or {}
        allume, charge = e.fait("allume", f), e.fait("charge", f)
        return (etat.get("allume") if allume is None else allume,
                (etat.get("charge") and not etat.get("faible")) if charge is None else charge)

    def a_portee(self, e, o):
        """Dans sa main, ou dans sa salle hors de tout contenant fermé."""
        if o in e.portes:
            return True
        lieu = self.lieu(e, o)
        if lieu == e.salle:
            return True
        return (lieu in self.monde.objets and self.monde.objets[lieu]["type"] == "contenant"
                and self.salle(e, lieu) == e.salle and self.ouvert(e, lieu))

    def flamme(self, e, k):
        """Une flamme qu'il a en main : un outil d'allumage, ou une source qu'il croit allumée."""
        o = self.monde.objets[k]
        return k in e.portes and ("allumage" in o.get("usages", []) or "allume" in o and self.feu(e, k)[0])

    def foyer_froid(self):
        """Le feu qu'une part de bois servirait : le premier foyer qu'il croit éteint."""
        return next((f for f in self.connus if self.monde.objets[f].get("foyer")
                     and (_cru(self.monde, self.id, f, "etat") or {}).get("allume") is False), None)

    def lumiere(self, e):
        if any("allume" in self.monde.objets[k] and self.feu(e, k)[0] for k in e.portes):
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
    objets = monde.objets
    # Aller : un trajet vers toute salle qu'il croit atteindre avec ce qu'il porte.
    for s in sorted(v.salles):
        if s != e.salle:
            route = v.route(e.salle, s, e.portes)
            if route is not None:
                yield 0, len(route), [_etape("aller", lieu=s)], e.apres(salle=s)
    for o in v.connus:
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
        if (ici and o not in e.portes and x.get("mobile") and v.autorise[o] and _disponible_cru(monde, id, o)
                and (x.get("ouvre") or set(x.get("usages", [])) & set(USAGES) or x["type"] == "nourriture"
                     or "allume" in x or o in vises.get("prendre", ()))):
            yield mal, 1, [_etape("prendre", o, condition=faute)], e.apres(portes=e.portes | {o}, faits=touche)
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
            if ici and _disponible_cru(monde, id, o):
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
        if x["type"] == "nourriture" and ici and _disponible_cru(monde, id, o) and v.autorise[o]:
            porte = o in e.portes
            dedans = [(("touche", contenant), True)] if contenant else []
            yield (0 if porte else mal, 1, [_etape("manger", o, condition="" if porte else faute)],
                   e.apres(faits=[(("mange", o), True), *dedans, *([] if porte else touche)]))
        # Un foyer : le recharger, l'allumer, s'y chauffer.
        if x.get("foyer") and v.salle(e, o) == e.salle:
            allume, charge = v.feu(e, o)
            if not (allume and charge):
                for bois in sorted(k for k in e.portes if "combustible" in objets[k].get("usages", [])
                                   and _disponible_cru(monde, id, k)):
                    yield 0, 1, [_etape("alimenter", o, outil=bois)], e.apres(faits=[(("charge", o), True)])
            if allume is False and charge:
                for flamme in sorted(k for k in e.portes if k != o and v.flamme(e, k)):
                    yield 0, 1, [_etape("allumer", o, outil=flamme)], e.apres(faits=[(("allume", o), True)])
            if allume:
                yield 0, 1, [_etape("chauffer", o)], e.apres(faits=[(("chauffe", o), True)])
        # Une source portable éteinte et chargée s'allume à une flamme fixe qu'il croit vive.
        if (o in e.portes and "allume" in x and x.get("mobile") and v.feu(e, o)[0] is False
                and (_cru(monde, id, o, "etat") or {}).get("charge")):
            for fixe in v.connus:
                if (fixe != o and "allume" in objets[fixe] and not objets[fixe].get("mobile")
                        and v.salle(e, fixe) == e.salle and v.feu(e, fixe)[0]):
                    yield 0, 1, [_etape("allumer", o, outil=fixe)], e.apres(faits=[(("allume", o), True)])
        # Une part : l'attendre si elle est promise, là où le donneur viendra la servir (près des
        # vivres, ou du feu qu'il entretiendra) ; sinon la demander à son propriétaire.
        if besoin_de_part(x) and _disponible_cru(monde, id, o):
            donneur = v.proprietaire[o]
            foyer = v.foyer_froid() if besoin_de_part(x) == "chaleur" else None
            if donneur not in (None, id, "joueur") and profil(monde, donneur):
                if promesse_en_cours(monde, id, o) == donneur:
                    if e.salle == (v.salle(e, foyer) if foyer else v.salle(e, o)):
                        yield 0, 0, [], e.apres(faits=[(("part", o), donneur)])
                elif not refuse_recemment(monde, id, donneur, "demander", o):
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


def chercher(monde, id, but, vises=None, depuis=None, profondeur=PROFONDEUR, noeuds=NOEUDS):
    """Le plan le moins coûteux vers ``but`` (une fonction de la vue et de l'état), ou None,
    depuis l'état ``depuis`` (par défaut, ce qu'il croit maintenant).

    Le coût est (personnes lésées, minutes) : le moins fautif d'abord. Renvoie
    (coût, étapes, état final)."""
    v = Vue(monde, id)
    depart_ = depuis or depart(monde, id, v)
    ordre = count()
    infini = (float("inf"), float("inf"))
    file = [((0, 0), next(ordre), depart_, [], 0)]
    vus = {depart_: (0, 0)}
    examines = 0
    while file and examines < noeuds:
        cout, _, e, etapes, n = heapq.heappop(file)
        if vus.get(e, infini) < cout:
            continue
        examines += 1
        if but(v, e):
            return cout, etapes, e
        if n >= profondeur:
            continue
        for fautes, minutes, ajout, suivant in gestes(v, e, vises, but):
            if any(cle[0] in TERMINAUX and cle not in e.faits for cle in suivant.faits) and not but(v, suivant):
                continue
            # Une flamme allumée par le plan se consume : on l'allume le plus tard possible.
            brule = sum(1 for k in e.portes if e.fait("allume", k))
            total = (cout[0] + fautes, cout[1] + minutes * (1 + FLAMME_EN_MAIN * brule))
            if total < vus.get(suivant, infini):
                vus[suivant] = total
                heapq.heappush(file, (total, next(ordre), suivant, etapes + ajout, n + 1))
    return None


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
    trouve = chercher(monde, id, but)
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
    trouve = chercher(monde, id, but, vises)
    if trouve is None:
        return None
    _, etapes, e = trouve
    return {"type": "pulsion", **condition}, retablir(v, e, _couper(etapes))


def aller(monde, id, salle):
    """Les étapes pour se rendre dans une salle, ou None s'il n'y croit aucun passage."""
    trouve = chercher(monde, id, lambda v, e: e.salle == salle)
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
