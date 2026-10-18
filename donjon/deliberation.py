"""Besoins, pulsions et délibération des PNJ ; planificateur borné sur leurs croyances.

Le profil d'auteur (``objet["profil"]``) déclare caractéristiques, traits, limites,
capacités, besoins et pulsions. Le moteur fait évoluer les besoins minute par minute ;
une pulsion qui cesse d'être satisfaite aux yeux du PNJ relance son besoin. Chaque minute,
le PNJ retient le but le plus urgent pour lequel il trouve un plan, cherché sur ce qu'il
croit, jamais sur la vérité du monde. Les étapes sont ensuite revalidées sur l'état réel
par ``pnj.py``. Tout est déterministe ; Luna n'intervient pas.
"""
from .esprits import RECENT, esprit, lire, memoriser
from .spatial import porte_par

BESOINS = ("devoir", "biens", "securite", "faim", "repos", "chaleur")
LIMITES = ("ne_vole_pas", "ne_blesse_pas", "ne_ment_pas")
CAPACITES = ("crochetage",)
OPERATIONS = ("aller", "prendre", "poser", "ouvrir", "fermer", "deverrouiller", "verrouiller",
              "crocheter", "manger", "inspecter", "reposer", "chauffer", "alimenter", "allumer", "servir",
              "dire", "demander", "confier", "remettre")
PROGRESSIFS = ("aller", "reposer", "chauffer")  # gestes qui durent : une minute sans les finir n'est pas un échec
SOCIALES = ("dire", "demander", "confier", "remettre")
PROFONDEUR = 4
PATIENCE = 30          # minutes d'attente d'une occasion avant de renoncer
REPIT = 60             # minutes avant de reprendre un but abandonné
ATTEINTE = 30          # une pulsion qui cesse d'être satisfaite relance son besoin
VOL = 60               # un vol vu par sa victime
SATIETE = 50           # un repas
REPOS_MINUTE = 2       # repos regagné par minute passée à se reposer
REPOS_FIN = 20         # reposé : il se relève
CHALEUR_MINUTE = 3     # chaleur regagnée par minute passée près d'un foyer allumé
CHALEUR_FIN = 20       # réchauffé : il s'écarte du feu
REDEMANDE = 120        # minutes avant de redemander la même chose à qui vient de refuser
ATTENTE_PART = 60      # minutes pendant lesquelles on attend la part promise avant de redemander
REVOIR_FEU = 30        # un feu vu vif doit être revu avant que ce qui lui restait ne s'épuise
DESESPOIR = 95         # au-delà, le besoin l'emporte sur la crainte d'être vu
STATS = ("FOR", "DEX", "INT", "PER", "CHA")


def profil(monde, id):
    return monde.objets[id].get("profil")


def reserve(monde, id):
    """Parts qu'un personnage garde pour lui de chaque ressource comptée qu'il possède."""
    return (profil(monde, id) or {}).get("reserve", 1)


def besoin_de_part(o):
    """Le besoin qu'une part de cette ressource apaise : la faim des vivres, le froid du combustible."""
    if o["type"] == "nourriture":
        return "faim"
    return "chaleur" if "combustible" in o.get("usages", []) else None


def parts(o):
    return o.get("portions", o.get("charges", 0))


def verifier_profil(monde, id, p):
    assert (isinstance(p, dict) and {"caracteristiques", "traits", "limites", "capacites", "besoins", "pulsions"}
            <= set(p) <= {"caracteristiques", "traits", "limites", "capacites", "besoins", "pulsions",
                          "reserve"}), "Profil de PNJ mal formé"
    assert type(p.get("reserve", 1)) is int and 0 <= p.get("reserve", 1) <= 10, "Réserve de PNJ invalide"
    assert set(p["caracteristiques"]) == set(STATS) and all(
        type(v) is int and 1 <= v <= 20 for v in p["caracteristiques"].values()), "Caractéristiques de PNJ invalides"
    assert isinstance(p["traits"], str) and len(p["traits"]) <= 600, "Traits de PNJ invalides"
    assert set(p["limites"]) <= set(LIMITES) and set(p["capacites"]) <= set(CAPACITES), "Limite ou capacité inconnue"
    for nom, b in p["besoins"].items():
        assert (nom in BESOINS and set(b) == {"depart", "derive_heure", "urgence"}
                and all(isinstance(b[k], (int, float)) for k in b)
                and 0 <= b["depart"] <= 100 and 0 < b["urgence"] <= 100), "Besoin de PNJ invalide"
    for pulsion in p["pulsions"]:
        assert (set(pulsion) <= {"besoin", "condition", "delegue_a"} and pulsion.get("besoin") in p["besoins"]
                and condition_valide(monde, pulsion.get("condition"))
                and pulsion.get("delegue_a", "joueur") == "joueur"), "Pulsion de PNJ invalide"


def condition_valide(monde, c):
    """Vocabulaire commun des buts : un objet en un lieu, un objet verrouillé, une ronde,
    une part de nourriture servie à quelqu'un, un feu entretenu."""
    return isinstance(c, dict) and (
        (set(c) == {"objet", "lieu"} and c["objet"] in monde.objets and c["lieu"] in monde.data["salles"])
        or (set(c) == {"objet", "servir"} and c["objet"] in monde.objets
            and monde.objets[c["objet"]]["type"] == "nourriture" and c["servir"] in monde.objets
            and monde.objets[c["servir"]]["type"] == "personnage")
        or (set(c) == {"objet", "verrouillee"} and c["objet"] in monde.objets and c["verrouillee"] is True)
        or (set(c) == {"objet", "allume"} and c["objet"] in monde.objets and "allume" in monde.objets[c["objet"]]
            and c["allume"] is True)
        or (set(c) == {"lieu", "periode"} and c["lieu"] in monde.data["salles"]
            and type(c["periode"]) is int and c["periode"] > 0))


def installer(monde, id):
    """Valeurs initiales des besoins et état des pulsions, à la première rencontre du profil."""
    p, e = profil(monde, id), esprit(monde, id)
    if not p:
        return
    for nom, b in p["besoins"].items():
        e["besoins"].setdefault(nom, float(b["depart"]))
    if len(e["pulsions"]) != len(p["pulsions"]):
        e["pulsions"] = [satisfaite(monde, id, x["condition"]) for x in p["pulsions"]]


def relancer(monde, id, besoin, montant):
    """Un événement (vol, atteinte à une pulsion) accroît un besoin déclaré ; un apaisement le réduit."""
    e = esprit(monde, id)
    if besoin in e["besoins"]:
        e["besoins"][besoin] = max(0.0, min(100.0, e["besoins"][besoin] + montant))


# --- Croyances utiles au plan -------------------------------------------------------------

def _lieu_cru(monde, id, sujet):
    c = lire(monde, id)["croyances"].get(sujet, {}).get("lieu")
    if c:
        return c["valeur"]
    o = monde.objets.get(sujet)
    # Les objets fixes font partie des lieux : on sait où ils sont sans les avoir revus.
    return o["lieu"] if o and not o.get("mobile") else None


def salle_crue(monde, id, sujet, profondeur=0):
    if sujet in monde.objets and porte_par(monde, sujet, id):
        return monde.objets[id]["lieu"]
    lieu = _lieu_cru(monde, id, sujet)
    if lieu is None or profondeur > PROFONDEUR:
        return None
    if lieu in monde.data["salles"]:
        return lieu
    if lieu == "joueur":
        return _lieu_cru(monde, id, "joueur")
    return salle_crue(monde, id, lieu, profondeur + 1)


def _cru(monde, id, sujet, attribut):
    c = lire(monde, id)["croyances"].get(sujet, {}).get(attribut)
    return None if c is None else c["valeur"]


def _ouvert_cru(monde, id, sujet):
    etat = _cru(monde, id, sujet, "etat")
    return bool(etat and etat.get("ouverte"))


def _connus(monde, id):
    """Objets dont le PNJ a une croyance ou qu'il porte, dans un ordre stable."""
    croyances = lire(monde, id)["croyances"]
    return sorted(s for s in monde.objets if s in croyances or porte_par(monde, s, id))


def periodique(condition):
    """Une ronde : avoir inspecté un lieu depuis moins de ``periode`` minutes."""
    return "periode" in condition


def s_use(condition):
    """Une ronde expire, un feu baisse : d'eux-mêmes, sans que personne y ait porté atteinte."""
    return periodique(condition) or "allume" in condition


def _disponible_cru(monde, id, objet):
    """Une nourriture ou une réserve qu'il a vue épuisée ne lui sert plus."""
    etat = _cru(monde, id, objet, "etat")
    return not etat or etat.get("disponible", True)


def refuse_recemment(monde, id, autre, operation, objet=None):
    """Le dernier refus de cet échange, s'il date de moins de ``REDEMANDE`` minutes."""
    return next((s for s in reversed(lire(monde, id)["memoire"])
                 if s["type"] == "refus" and s["de"] == autre and s["operation"] == operation
                 and s.get("objet", objet) == objet and monde.data["minutes"] - s["minute"] < REDEMANDE), None)


def promesse_en_cours(monde, id, objet):
    """Une part promise et pas encore servie, dans le délai où il l'attend."""
    for s in reversed(lire(monde, id)["memoire"]):
        if s["type"] == "nourri" and s.get("objet") == objet:
            return None
        if s["type"] == "promis" and s["objet"] == objet:
            return s["de"] if monde.data["minutes"] - s["minute"] < ATTENTE_PART else None
    return None


def satisfaite(monde, id, condition):
    if "servir" in condition:
        return False  # Une part servie solde l'engagement au moment du geste.
    if periodique(condition):
        vu = lire(monde, id)["visites"].get(condition["lieu"])
        return vu is not None and monde.data["minutes"] - vu < condition["periode"]
    if "allume" in condition:
        # Un feu qui baisse n'est plus entretenu ; un feu vu vif il y a longtemps n'est plus sûr :
        # il faut aller le voir, et le recharger tant qu'il reste le temps d'aller chercher du bois.
        c = lire(monde, id)["croyances"].get(condition["objet"], {}).get("etat")
        return bool(c and c["valeur"].get("allume") and not c["valeur"].get("faible")
                    and monde.data["minutes"] - c["minute"] < REVOIR_FEU)
    if "lieu" in condition:
        # Le tenir soi-même ne suffit pas : l'objet doit être déposé (ou tenu par un autre) sur place.
        return (not porte_par(monde, condition["objet"], id)
                and salle_crue(monde, id, condition["objet"]) == condition["lieu"])
    return _cru(monde, id, condition["objet"], "verrouillee") is True and not _ouvert_cru(monde, id, condition["objet"])


def illicite(monde, id, objet):
    from .vol import proprietaire
    return proprietaire(monde, monde.objets[objet]) not in (None, id)


def autorise(monde, id, objet):
    return not (illicite(monde, id, objet) and "ne_vole_pas" in profil(monde, id)["limites"])


# --- Planificateur ------------------------------------------------------------------------

class Echec(Exception):
    pass


class Plan:
    """Simulation du plan : où sera le PNJ, ce qu'il portera, ce qu'il aura ouvert."""

    def __init__(self, monde, id):
        self.monde, self.id = monde, id
        self.salle = monde.objets[id]["lieu"]
        self.portes = {o for o in monde.objets if porte_par(monde, o, id)}
        self.ouverts, self.deverrouilles, self.etapes = set(), set(), []
        self.touches = set()  # contenants auxquels le plan accède, ouverts par lui ou déjà ouverts

    def ajouter(self, operation, cible="", outil="", lieu="", condition="", contenu=None):
        self.etapes.append({"operation": operation, "cible": cible, "outil": outil,
                            "lieu": lieu, "condition": condition, **({"contenu": contenu} if contenu else {})})

    def retablir(self):
        """Ce qu'il garde sous clé et auquel le plan accède, il le referme à clé avant de finir."""
        for x in profil(self.monde, self.id)["pulsions"]:
            cible = x["condition"].get("objet")
            if not x["condition"].get("verrouillee") or cible not in self.touches:
                continue
            if cible in self.ouverts or _ouvert_cru(self.monde, self.id, cible):
                self.ajouter("fermer", cible)
            cle = self.cle(cible)
            if cle in self.portes and (cible in self.deverrouilles or _cru(self.monde, self.id, cible, "verrouillee") is not True):
                self.ajouter("verrouiller", cible, outil=cle)

    def condition(self, objet):
        return "sans_temoin" if illicite(self.monde, self.id, objet) else ""

    def aller(self, cible, profondeur=0):
        from .pnj import chemin, portes_closes
        if self.salle == cible:
            return
        if chemin(self.monde, self.id, self.salle, cible, self.portes) is None:
            # Une porte crue verrouillée barre la route : la clé connue devient un sous-but.
            for porte in portes_closes(self.monde, self.id, self.salle, cible):
                cle = self.cle(porte)
                if cle and profondeur < PROFONDEUR:
                    self.obtenir(cle, profondeur + 1)
                    break
            if chemin(self.monde, self.id, self.salle, cible, self.portes) is None:
                raise Echec
        self.ajouter("aller", lieu=cible)
        self.salle = cible

    def rejoindre(self, sujet):
        """Aller là où il croit trouver quelqu'un ; s'il en a perdu la trace, le chercher dans la
        salle accessible qu'il a parcourue le moins récemment. Vrai s'il sait où le trouver."""
        from .pnj import chemin
        salle = salle_crue(self.monde, self.id, sujet)
        if salle is not None:
            self.aller(salle)
            return True
        visites = lire(self.monde, self.id)["visites"]
        routes = {s: chemin(self.monde, self.id, self.salle, s, self.portes) for s in self.monde.data["salles"]}
        routes = {s: r for s, r in routes.items() if r is not None}
        # La salle où il se tient compte : il la parcourt des yeux avant d'aller plus loin.
        salle = min(routes, key=lambda s: (visites.get(s, -1), len(routes[s]), s))
        self.aller(salle)
        self.ajouter("inspecter", lieu=salle)
        return False

    def cle(self, cible):
        return next((k for k in _connus(self.monde, self.id)
                     if cible in self.monde.objets[k].get("ouvre", [])
                     and (k in self.portes or autorise(self.monde, self.id, k))), None)

    def outil(self, usage):
        return next((k for k in _connus(self.monde, self.id)
                     if usage in self.monde.objets[k].get("usages", []) and _disponible_cru(self.monde, self.id, k)
                     and (k in self.portes or autorise(self.monde, self.id, k))), None)

    def _etat(self):
        return (self.salle, set(self.portes), set(self.ouverts), set(self.deverrouilles),
                list(self.etapes), set(self.touches))

    def _restaurer(self, etat):
        (self.salle, self.portes, self.ouverts, self.deverrouilles,
         self.etapes, self.touches) = etat

    def flamme(self, cible):
        """De quoi allumer ``cible``, qu'il aura en main ou à portée en l'atteignant.

        Un outil d'allumage, sinon une source qu'il croit allumée et qu'il peut prendre, sinon
        une source éteinte qu'il croit chargée, allumée à une flamme fixe qu'il croit vive : une
        source fixe ne se déplace pas, on lui apporte de quoi prendre feu.
        """
        briquet = self.outil("allumage")
        if briquet:
            self.obtenir(briquet)
            return briquet
        sources = [k for k in _connus(self.monde, self.id)
                   if k != cible and "allume" in self.monde.objets[k]
                   and (k in self.portes or autorise(self.monde, self.id, k))]
        etat = lambda k: _cru(self.monde, self.id, k, "etat") or {}
        vives = [k for k in sources if etat(k).get("allume")]
        mobiles = [k for k in sources if self.monde.objets[k].get("mobile")]
        essais = [(k, None) for k in vives if k in mobiles]
        essais += [(k, f) for k in mobiles if not etat(k).get("allume") and etat(k).get("charge")
                   for f in vives if not self.monde.objets[f].get("mobile")]
        for source, fixe in essais:
            avant = self._etat()
            try:
                self.obtenir(source)
                if fixe:
                    salle = salle_crue(self.monde, self.id, fixe)
                    if salle is None:
                        raise Echec
                    self.aller(salle)
                    self.ajouter("allumer", source, outil=fixe)
                return source
            except Echec:
                self._restaurer(avant)
        raise Echec

    def obtenir(self, objet, profondeur=0):
        if objet in self.portes:
            return
        o = self.monde.objets.get(objet)
        if (profondeur > PROFONDEUR or not o or not o.get("mobile")
                or not autorise(self.monde, self.id, objet)):
            raise Echec
        lieu = _lieu_cru(self.monde, self.id, objet)
        if lieu in self.monde.data["salles"]:
            self.aller(lieu, profondeur)
        elif lieu in self.monde.objets and self.monde.objets[lieu]["type"] == "contenant":
            self.acceder(lieu, profondeur + 1)
        else:
            raise Echec
        self.ajouter("prendre", objet, condition=self.condition(objet))
        self.portes.add(objet)

    def acceder(self, contenant, profondeur=0):
        """Se tenir devant un contenant ouvert, en l'ouvrant au besoin."""
        salle = salle_crue(self.monde, self.id, contenant)
        if salle is None or profondeur > PROFONDEUR:
            raise Echec
        self.touches.add(contenant)
        if _ouvert_cru(self.monde, self.id, contenant) or contenant in self.ouverts:
            self.aller(salle, profondeur)
            return
        condition = self.condition(contenant)
        if _cru(self.monde, self.id, contenant, "verrouillee") and contenant not in self.deverrouilles:
            cle, crochet = self.cle(contenant), None
            if cle is None and "crochetage" in profil(self.monde, self.id)["capacites"]:
                crochet = self.outil("crochetage")
            if cle is None and crochet is None:
                raise Echec
            self.obtenir(cle or crochet, profondeur + 1)
            self.aller(salle, profondeur)
            self.ajouter("deverrouiller" if cle else "crocheter", contenant, outil=cle or crochet,
                         condition=condition)
            self.deverrouilles.add(contenant)
        else:
            self.aller(salle, profondeur)
        self.ajouter("ouvrir", contenant, condition=condition)
        self.ouverts.add(contenant)


def _plan_manger(monde, id):
    """Ce qui est à lui ou à personne ; sinon une part promise ou demandée à qui possède les
    vivres ; sinon, s'il n'a pas de scrupule, le bien d'autrui."""
    nourritures = [f for f in _connus(monde, id)
                   if monde.objets[f]["type"] == "nourriture" and _disponible_cru(monde, id, f)]
    licites = [f for f in nourritures if porte_par(monde, f, id) or not illicite(monde, id, f)]
    for resultat in (*(_plan_repas(monde, id, f) for f in licites), _plan_part(monde, id, nourritures),
                     *(_plan_repas(monde, id, f) for f in nourritures if f not in licites and autorise(monde, id, f))):
        if resultat:
            return resultat
    return None


def _plan_repas(monde, id, f):
    p = Plan(monde, id)
    try:
        if f not in p.portes:
            lieu = _lieu_cru(monde, id, f)
            if lieu in monde.data["salles"]:
                p.aller(lieu)
            elif lieu in monde.objets and monde.objets[lieu]["type"] == "contenant":
                p.acceder(lieu)
            else:
                raise Echec
        p.ajouter("manger", f, condition="" if f in p.portes else p.condition(f))
        p.retablir()
    except Echec:
        return None
    return {"type": "manger", "objet": f}, p.etapes


def _plan_part(monde, id, nourritures):
    """Une part promise s'attend près des vivres, où le donneur viendra la servir ; sinon on la
    demande à leur propriétaire, sauf s'il vient de refuser."""
    from .vol import proprietaire
    for f in nourritures:
        donneur = proprietaire(monde, monde.objets[f])
        if donneur in (None, id, "joueur") or not profil(monde, donneur):
            continue
        p = Plan(monde, id)
        try:
            if promesse_en_cours(monde, id, f) == donneur:
                salle = salle_crue(monde, id, f)
                if salle is None:
                    raise Echec
                p.aller(salle)
            elif refuse_recemment(monde, id, donneur, "demander", f):
                continue
            elif p.rejoindre(donneur):
                p.ajouter("demander", donneur, outil=f)
        except Echec:
            continue
        return {"type": "part", "objet": f, "de": donneur}, p.etapes
    return None


def _plan_pulsion(monde, id, condition):
    p = Plan(monde, id)
    try:
        if periodique(condition):
            p.aller(condition["lieu"])
            p.ajouter("inspecter", lieu=condition["lieu"])
        elif "servir" in condition:
            f = condition["objet"]
            if f not in p.portes:
                lieu = _lieu_cru(monde, id, f)
                if lieu in monde.data["salles"]:
                    p.aller(lieu)
                elif lieu in monde.objets and monde.objets[lieu]["type"] == "contenant":
                    p.acceder(lieu)
                else:
                    raise Echec
            p.ajouter("servir", f, condition=p.condition(f), contenu={"pour": condition["servir"]})
        elif "lieu" in condition:
            p.obtenir(condition["objet"])
            p.aller(condition["lieu"])
            p.ajouter("poser", condition["objet"], lieu=condition["lieu"])
        elif "allume" in condition:
            # Recharger le feu avec un combustible qu'il peut prendre ; le rallumer s'il est éteint.
            foyer, bois = condition["objet"], p.outil("combustible")
            salle, etat = salle_crue(monde, id, foyer), _cru(monde, id, foyer, "etat") or {}
            if salle is None:
                raise Echec
            if not etat or etat.get("allume") and not etat.get("faible"):
                p.aller(salle)  # Vu vif il y a longtemps, ou jamais vu : il va voir où il en est.
                p.ajouter("inspecter", lieu=salle)
                return {"type": "pulsion", **condition}, p.etapes
            # Un feu qui baisse, ou un foyer froid et vide, attend du bois ; éteint, il faut l'allumer.
            eteint = etat.get("allume") is False
            vide = etat.get("faible") or not etat.get("charge", True)
            if vide and bois is None:
                raise Echec
            if vide:
                p.obtenir(bois)
            # La flamme vient en dernier : une torche se consume pendant le trajet.
            flamme = p.flamme(foyer) if eteint else None
            p.aller(salle)
            if vide:
                p.ajouter("alimenter", foyer, outil=bois)
            if flamme:
                p.ajouter("allumer", foyer, outil=flamme)
        else:
            cible = condition["objet"]
            cle = p.cle(cible)
            salle = salle_crue(monde, id, cible)
            if cle is None or salle is None:
                raise Echec
            p.obtenir(cle)
            p.aller(salle)
            if _ouvert_cru(monde, id, cible):
                p.ajouter("fermer", cible)
            p.ajouter("verrouiller", cible, outil=cle)
        p.retablir()
    except Echec:
        return None
    return {"type": "pulsion", **condition}, p.etapes


def _plan_reposer(monde, id):
    """Se reposer là où l'on est."""
    p = Plan(monde, id)
    p.ajouter("reposer")
    return {"type": "repos"}, p.etapes


def _plan_chauffer(monde, id):
    """Aller se tenir près d'un foyer qu'il croit allumé."""
    for f in _connus(monde, id):
        if not monde.objets[f].get("foyer") or not (_cru(monde, id, f, "etat") or {}).get("allume"):
            continue
        salle = salle_crue(monde, id, f)
        p = Plan(monde, id)
        try:
            if salle is None:
                raise Echec
            p.aller(salle)
        except Echec:
            continue
        p.ajouter("chauffer", f)
        return {"type": "chaleur", "objet": f}, p.etapes
    # Aucun feu vif : ranimer un foyer froid, comme la faim cherche des vivres. Son bois ou celui
    # de personne d'abord ; sinon une part demandée à qui en possède ; sinon, sans scrupule, le
    # bien d'autrui, sans témoin.
    foyers = [f for f in _connus(monde, id) if monde.objets[f].get("foyer")
              and (_cru(monde, id, f, "etat") or {}).get("allume") is False]
    bois = [b for b in _connus(monde, id) if "combustible" in monde.objets[b].get("usages", [])
            and _disponible_cru(monde, id, b)]
    licites = [b for b in bois if porte_par(monde, b, id) or not illicite(monde, id, b)]
    for f in foyers:
        for resultat in (*(_plan_ranimer(monde, id, f, b) for b in [None, *licites]),
                         _plan_part_de_bois(monde, id, f, bois),
                         *(_plan_ranimer(monde, id, f, b) for b in bois if b not in licites and autorise(monde, id, b))):
            if resultat:
                return resultat
    return None


def _plan_ranimer(monde, id, foyer, bois):
    """Recharger s'il le faut, allumer, se chauffer. Sans bois, seulement si le foyer est cru chargé."""
    charge = (_cru(monde, id, foyer, "etat") or {}).get("charge")
    if (bois is None) != bool(charge):
        return None
    p = Plan(monde, id)
    try:
        if bois:
            p.obtenir(bois)
        flamme = p.flamme(foyer)
        salle = salle_crue(monde, id, foyer)
        if salle is None:
            raise Echec
        p.aller(salle)
    except Echec:
        return None
    if bois:
        p.ajouter("alimenter", foyer, outil=bois)
    p.ajouter("allumer", foyer, outil=flamme)
    p.ajouter("chauffer", foyer)
    return {"type": "chaleur", "objet": foyer}, p.etapes


def _plan_part_de_bois(monde, id, foyer, bois):
    """Une part de bois promise s'attend près du feu, où le donneur viendra l'entretenir ; sinon on
    la demande au propriétaire du bois, sauf s'il vient de refuser."""
    from .vol import proprietaire
    for b in bois:
        donneur = proprietaire(monde, monde.objets[b])
        if donneur in (None, id, "joueur") or not profil(monde, donneur):
            continue
        p = Plan(monde, id)
        try:
            if promesse_en_cours(monde, id, b) == donneur:
                salle = salle_crue(monde, id, foyer)
                if salle is None:
                    raise Echec
                p.aller(salle)
            elif refuse_recemment(monde, id, donneur, "demander", b):
                continue
            elif p.rejoindre(donneur):
                p.ajouter("demander", donneur, outil=b, contenu={"foyer": foyer})
        except Echec:
            continue
        return {"type": "part", "objet": b, "de": donneur}, p.etapes
    return None


def ouvert_par_soi(monde, id, objet, depuis):
    """A-t-il lui-même ouvert ou déverrouillé cet objet dans les ``depuis`` dernières minutes ?"""
    return any(s["type"] == "ouvert_par_soi" and s["objet"] == objet and monde.data["minutes"] - s["minute"] <= depuis
               for s in lire(monde, id)["memoire"])


def garde_sous_cle(monde, id, objet):
    p = profil(monde, id)
    return bool(p) and any(x["condition"] == {"objet": objet, "verrouillee": True} for x in p["pulsions"])


def de_son_fait(monde, id, condition):
    """On ne s'alarme pas de ce qu'on vient de défaire soi-même : sa clé, sa main."""
    if condition.get("verrouillee"):
        return ouvert_par_soi(monde, id, condition["objet"], 2)
    return "lieu" in condition and "objet" in condition and porte_par(monde, condition["objet"], id)


def _plan_garder(monde, id, condition):
    salle = salle_crue(monde, id, condition["objet"])
    if salle is None:
        return None
    p = Plan(monde, id)
    try:
        p.aller(salle)
    except Echec:
        return None
    return {"type": "garder", "lieu": salle}, p.etapes


def _delegue(monde, id, pulsion):
    """Une pulsion confiée au joueur attend tant que le PNJ le croit fiable."""
    return pulsion.get("delegue_a") and _cru(monde, id, pulsion["delegue_a"], "fiable") is not False


def urgents(monde, id):
    """Besoins au-delà de leur seuil, du plus pressant au moins pressant."""
    p, e = profil(monde, id), esprit(monde, id)
    return sorted((b for b in p["besoins"] if e["besoins"][b] >= p["besoins"][b]["urgence"]),
                  key=lambda b: (p["besoins"][b]["urgence"] - e["besoins"][b], BESOINS.index(b)))


def confie_a_autrui(monde, id, objet):
    """Ce qu'il a confié à quelqu'un qu'il croit fiable, il ne le fait pas à sa place."""
    p = profil(monde, id)
    return bool(p) and any(x["condition"].get("objet") == objet and _delegue(monde, id, x) for x in p["pulsions"])


# Besoins qu'un geste qui dure apaise : la méthode, et le seuil où il s'achève.
PROGRES = {"repos": (_plan_reposer, REPOS_FIN), "chaleur": (_plan_chauffer, CHALEUR_FIN)}


def retabli_par_son_plan(monde, id, condition):
    """Ce qu'il défait lui-même pour un plan qui le rétablit n'est pas à réparer d'abord, tant
    que le motif de ce plan presse encore (un besoin urgent, une parole à tenir)."""
    e = lire(monde, id)
    i = e["intention"]
    if not (condition.get("verrouillee") and i and any(
            x["operation"] == "verrouiller" and x["cible"] == condition["objet"] for x in i["plan"])):
        return False
    but = {k: v for k, v in i["but"].items() if k != "type"}
    return i["motif"] in urgents(monde, id) or i["motif"] == "engagement" and any(
        x["condition"] == but for x in e["engagements"])


def candidats(monde, id):
    """Buts envisageables, du besoin le plus pressant au moins pressant ; la routine (rondes,
    surveillance) passe après ce qui presse vraiment et après une tâche acceptée."""
    p, e = profil(monde, id), esprit(monde, id)
    buts = []
    for besoin in urgents(monde, id):
        if besoin == "faim":
            buts.append((besoin, _plan_manger, False))
            continue
        if besoin in PROGRES:
            buts.append((besoin, PROGRES[besoin][0], False))
            continue
        pulsions = [x for x in p["pulsions"] if x["besoin"] == besoin]
        for x in pulsions:
            if (not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)
                    and not retabli_par_son_plan(monde, id, x["condition"])):
                # Une ronde peut attendre qu'il ait tenu parole ; un feu à voir ou à recharger, non.
                buts.append((besoin, lambda m, i, c=x["condition"]: _plan_pulsion(m, i, c),
                             periodique(x["condition"])))
        if besoin == "biens":
            for x in pulsions:
                if periodique(x["condition"]):
                    continue
                buts.append((besoin, lambda m, i, c=x["condition"]: _plan_garder(m, i, c), True))
    buts += [("engagement", lambda m, i, c=x["condition"]: _plan_pulsion(m, i, c), False) for x in e["engagements"]]
    # Ce qu'il garde sous clé et a lui-même ouvert, il le referme sans attendre l'urgence.
    for x in p["pulsions"]:
        c = x["condition"]
        if (c.get("verrouillee") and ouvert_par_soi(monde, id, c["objet"], RECENT) and not satisfaite(monde, id, c)
                and not retabli_par_son_plan(monde, id, c)):
            buts.append((x["besoin"], lambda m, i, c=c: _plan_pulsion(m, i, c), False))
    # Assis pour se reposer, ou près du feu, il ne s'en va qu'une fois remis, ou pour plus pressant.
    for besoin, (methode, fin) in PROGRES.items():
        if e["intention"] and e["intention"]["motif"] == besoin and e["besoins"].get(besoin, 0) > fin:
            buts.append((besoin, methode, False))
    # Ce qui presse vraiment, la parole donnée et ce qu'on finit, puis la routine, par urgence.
    for besoin, methode, _ in sorted(buts, key=lambda x: x[2]):
        yield besoin, methode


def deliberer(monde, id, minute):
    """Une minute de vie intérieure : besoins, pulsions, choix du but et du plan."""
    p = profil(monde, id)
    e = esprit(monde, id)
    if not p:
        return
    installer(monde, id)
    for nom, b in p["besoins"].items():
        e["besoins"][nom] = round(min(100.0, max(0.0, e["besoins"][nom] + b["derive_heure"] / 60)), 3)
    for i, x in enumerate(p["pulsions"]):
        etat = satisfaite(monde, id, x["condition"])
        # Une ronde expire, un feu baisse d'eux-mêmes : ce n'est pas une atteinte.
        if (e["pulsions"][i] and not etat and not s_use(x["condition"])
                and not de_son_fait(monde, id, x["condition"])):
            # Ses biens forcés ou déplacés : un vol découvert, même sans coupable.
            relancer(monde, id, x["besoin"], VOL if x["besoin"] == "biens" else ATTEINTE)
            memoriser(monde, id, {"type": "atteinte", "condition": dict(x["condition"])})
        e["pulsions"][i] = etat
    from .echanges import engagements_echus
    from . import stratege
    engagements_echus(monde, id)
    intention = e["intention"]
    if intention and intention["motif"] == "alerte":
        return  # Le réflexe déclaré garde la priorité jusqu'à son terme.
    if intention and intention["but"]["type"] == "strategie" and intention["plan"]:
        return  # Une stratégie choisie va à son terme, ou tombe au premier geste manqué.
    for besoin, methode in candidats(monde, id):
        if e["renoncements"].get(besoin, -REPIT) + REPIT > minute:
            continue
        resultat = methode(monde, id)
        if not resultat:
            continue
        but, etapes = resultat
        if stratege.plan_illicite(monde, id, besoin, but, etapes, minute):
            return
        intention = e["intention"]
        meme = bool(intention) and intention["but"] == but
        e["intention"] = {"but": but, "motif": besoin, "plan": etapes,
                          "depuis": intention["depuis"] if meme else minute,
                          "attente": intention["attente"] if meme else 0}
        stratege.occupe(monde, id)
        return
    e["intention"] = None
    stratege.desoeuvre(monde, id, minute, urgents(monde, id))


def renoncer(monde, id, minute):
    e = esprit(monde, id)
    intention = e["intention"]
    e["renoncements"][intention["motif"]] = minute
    memoriser(monde, id, {"type": "renoncement", "but": dict(intention["but"])})
    e["intention"] = None
