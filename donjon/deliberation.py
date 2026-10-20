"""Besoins, pulsions et délibération des PNJ ; planificateur borné sur leurs croyances.

Le profil d'auteur (``objet["profil"]``) déclare caractéristiques, traits, limites,
capacités, besoins et pulsions. Le moteur fait évoluer les besoins minute par minute ;
une pulsion qui cesse d'être satisfaite aux yeux du PNJ relance son besoin. Chaque minute,
le PNJ retient le but le plus urgent pour lequel il trouve un plan, cherché sur ce qu'il
croit, jamais sur la vérité du monde. Les étapes sont ensuite revalidées sur l'état réel
par ``pnj.py``. Tout est déterministe ; Luna n'intervient pas.
"""
from .corps import CORPS, SATIETE  # noqa: F401  (SATIETE : un repas, pour les gestes des PNJ)
from .esprits import RECENT, esprit, lire, memoriser
from .spatial import porte_par

BESOINS = ("devoir", "biens", "securite", "faim", "repos", "chaleur")
LIMITES = ("ne_vole_pas", "ne_blesse_pas", "ne_ment_pas")
CAPACITES = ("crochetage",)
OPERATIONS = ("aller", "prendre", "poser", "ouvrir", "fermer", "deverrouiller", "verrouiller",
              "crocheter", "manger", "inspecter", "reposer", "chauffer", "abriter", "alimenter", "allumer", "eteindre",
              "servir",
              "dire", "demander", "confier", "remettre")
PROGRESSIFS = ("aller", "reposer", "chauffer", "abriter")
EFFORTS = ("aller", "prendre", "poser", "crocheter", "alimenter", "servir", "inspecter")  # gestes qui creusent  # gestes qui durent : une minute sans les finir n'est pas un échec
SOCIALES = ("dire", "demander", "confier", "remettre")
PROFONDEUR = 4
PATIENCE = 30          # minutes d'attente d'une occasion avant de renoncer
REPIT = 60             # minutes avant de reprendre un but abandonné
ATTEINTE = 30          # une pulsion qui cesse d'être satisfaite relance son besoin
VOL = 60               # un vol vu par sa victime
REPOS_FIN = 20         # reposé : il se relève
CHALEUR_FIN = 20       # réchauffé : il s'écarte du feu
SECURITE_FIN = 30      # rassuré : il quitte l'abri
# Ce qui inquiète (+) ou rassure (−) la sécurité, valeurs par défaut que chaque profil nuance
# (donnée ``securite``) : par minute pour ce qui dure, d'un coup pour un événement.
SECURITE = {"noir": 0.5, "mefiance": 0.3, "bruit": 15, "illicite": 20,      # inquiète
            "lumiere": 0.2, "compagnie": 0.5, "ronde": 20}                 # rassure
REDEMANDE = 120        # minutes avant de redemander la même chose à qui vient de refuser
ATTENTE_PART = 60      # minutes pendant lesquelles on attend la part promise avant de redemander
REVOIR_FEU = 30        # un feu vu vif doit être revu avant que ce qui lui restait ne s'épuise
DESESPOIR = 95         # au-delà, le besoin l'emporte sur la crainte d'être vu ; sans abri, on appelle
APPEL_REPIT = 10       # minutes entre deux appels à l'aide
INERTIE = 5            # points au-delà du seuil avant qu'un besoin interrompe un plan en cours
STATS = ("FOR", "DEX", "INT", "PER", "CHA")


def profil(monde, id):
    return monde.objets[id].get("profil")


def seuils(monde, id):
    """Seuil d'urgence de chaque besoin : ceux du corps, communs ; ceux de l'esprit, du profil."""
    p = profil(monde, id)
    return {**{nom: regle["urgence"] for nom, regle in CORPS.items()},
            **{nom: b["urgence"] for nom, b in (p or {}).get("besoins", {}).items()}}


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
                          "reserve", "securite", "protege"}), "Profil de PNJ mal formé"
    assert (isinstance(p.get("protege", []), list) and all(
        x in monde.objets and monde.objets[x]["type"] == "personnage" and x != id
        for x in p.get("protege", []))), "Protégés de PNJ invalides"
    assert type(p.get("reserve", 1)) is int and 0 <= p.get("reserve", 1) <= 10, "Réserve de PNJ invalide"
    assert (isinstance(p.get("securite", {}), dict) and set(p.get("securite", {})) <= set(SECURITE)
            and all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in p.get("securite", {}).values())),         "Sécurité de PNJ invalide"
    assert set(p["caracteristiques"]) == set(STATS) and all(
        type(v) is int and 1 <= v <= 20 for v in p["caracteristiques"].values()), "Caractéristiques de PNJ invalides"
    assert isinstance(p["traits"], str) and len(p["traits"]) <= 600, "Traits de PNJ invalides"
    assert set(p["limites"]) <= set(LIMITES) and set(p["capacites"]) <= set(CAPACITES), "Limite ou capacité inconnue"
    for nom, b in p["besoins"].items():
        # Faim, froid et fatigue relèvent du corps, commun à tous : le profil ne les règle pas.
        assert (nom in BESOINS and nom not in CORPS and set(b) == {"depart", "derive_heure", "urgence"}
                and all(isinstance(b[k], (int, float)) for k in b)
                and 0 <= b["depart"] <= 100 and 0 < b["urgence"] <= 100), "Besoin de PNJ invalide"
    for pulsion in p["pulsions"]:
        assert (set(pulsion) <= {"besoin", "condition", "delegue_a"} and pulsion.get("besoin") in seuils(monde, id)
                and condition_valide(monde, pulsion.get("condition"))
                and pulsion.get("delegue_a", "joueur") == "joueur"), "Pulsion de PNJ invalide"


def condition_valide(monde, c):
    """Vocabulaire commun des buts : un objet en un lieu, un objet verrouillé, une ronde,
    une part de nourriture servie à quelqu'un, un feu entretenu."""
    return isinstance(c, dict) and (
        (set(c) == {"objet", "lieu"} and c["objet"] in monde.objets and c["lieu"] in monde.data["salles"])
        or (set(c) == {"objet", "servir"} and c["objet"] in monde.objets
            and monde.objets[c["objet"]]["type"] == "nourriture"
            and (c["servir"] == "joueur" or c["servir"] in monde.objets
                 and monde.objets[c["servir"]]["type"] == "personnage"))
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


# --- Sécurité ----------------------------------------------------------------------------

def taux(monde, id, cause):
    return (profil(monde, id) or {}).get("securite", {}).get(cause, SECURITE[cause])


def autour(monde, id):
    """Ce qui, dans sa salle, l'inquiète ou le rassure : la lumière sur sa case, ceux qu'il y voit
    et croit fiables, ceux qu'il y voit et ne croit pas fiables."""
    from .esprits import pnjs
    from .perception import eclairage
    o = monde.objets[id]
    niveau = eclairage(monde, o["lieu"], o.get("position") if monde.data.get("mode_cases") else None)["niveau"]
    presents = [x for x in [*pnjs(monde), "joueur"] if x != id
                and (monde.joueur["salle"] if x == "joueur" else monde.objets[x]["lieu"]) == o["lieu"]]
    if monde.data.get("mode_cases"):
        from .spatial import acteurs_vus
        autres = acteurs_vus(monde, id, presents)
    else:
        autres = presents if niveau else []
    return {"lumiere": niveau > 0,
            "fiables": sorted(x for x in autres if _cru(monde, id, x, "fiable") is True),
            "mefiants": sorted(x for x in autres if _cru(monde, id, x, "fiable") is False)}


def ressentir(monde, id):
    """Une minute de sécurité perçue : le noir et la méfiance inquiètent, la lumière et la
    compagnie de qui l'on croit fiable rassurent."""
    if "securite" not in esprit(monde, id)["besoins"] or monde.objets[id]["lieu"] not in monde.data["salles"]:
        return
    a = autour(monde, id)
    ecart = (-taux(monde, id, "lumiere") if a["lumiere"] else taux(monde, id, "noir"))
    ecart += taux(monde, id, "mefiance") if a["mefiants"] else 0
    ecart -= taux(monde, id, "compagnie") if a["fiables"] else 0
    relancer(monde, id, "securite", ecart)


def inquieter(monde, id, cause, signe=1):
    """Un événement inquiète (un bruit sans cause vue, un geste illicite) ou rassure (une ronde)."""
    if monde.objets.get(id, {}).get("profil"):
        relancer(monde, id, "securite", signe * taux(monde, id, cause))


def protecteurs(monde, protege):
    """Ceux dont le profil déclare protéger ce personnage."""
    return [x for x, o in monde.objets.items() if protege in (o.get("profil") or {}).get("protege", [])]


def appeler_a_l_aide(monde, id, minute):
    """À bout d'inquiétude et sans abri, il appelle : un son fort, que d'autres entendent."""
    e = esprit(monde, id)
    if (e["besoins"].get("securite", 0) < DESESPOIR
            or e["intention"] and e["intention"]["but"]["type"] == "abri"
            or any(s["type"] == "appel" and minute - s["minute"] < APPEL_REPIT for s in e["memoire"])):
        return
    memoriser(monde, id, {"type": "appel"})
    from .ecoute import appel
    appel(monde, id)


def _plan_prevenir(monde, id):
    """Un geste illicite vu contre un protégé : aller le lui dire."""
    e = esprit(monde, id)
    for s in reversed(e["memoire"]):
        if s["type"] != "a_prevenir":
            continue
        dit = any(x["type"] == "dit" and x["a"] == s["victime"] and x["sujet"] == s["auteur"]
                  and x["minute"] >= s["minute"] for x in e["memoire"])
        if dit or s["victime"] not in monde.objets:
            continue
        p = Plan(monde, id)
        try:
            if not p.rejoindre(s["victime"]):
                return {"type": "prevenir", "qui": s["victime"]}, p.etapes
        except Echec:
            continue
        p.ajouter("dire", s["victime"], contenu={"sujet": s["auteur"], "attribut": "fiable", "valeur": False})
        return {"type": "prevenir", "qui": s["victime"]}, p.etapes
    return None


def _eclairee_crue(monde, id, salle):
    """Éclairée quand il y était, ou par une source qu'il y croit allumée."""
    vue = _cru(monde, id, salle, "etat")
    if vue is not None:
        return vue.get("eclairee", False)
    if monde.data["salles"][salle].get("lumiere_naturelle"):
        return True
    return any("allume" in monde.objets[k] and (_cru(monde, id, k, "etat") or {}).get("allume")
               and salle_crue(monde, id, k) == salle for k in _connus(monde, id))


def _plan_abri(monde, id):
    """Se mettre à l'abri : rejoindre un lieu qu'il croit éclairé où se tient quelqu'un qu'il croit
    fiable, et y rester ; là où il est d'abord, s'il l'est déjà."""
    from .esprits import pnjs
    ici = monde.objets[id]["lieu"]
    salles = []
    for x in [*pnjs(monde), "joueur"]:
        if x == id or _cru(monde, id, x, "fiable") is not True:
            continue
        salle = salle_crue(monde, id, x)
        if salle in monde.data["salles"] and salle not in salles and _eclairee_crue(monde, id, salle):
            salles.append(salle)
    for salle in sorted(salles, key=lambda s: s != ici):
        p = Plan(monde, id)
        try:
            p.aller(salle)
        except Echec:
            continue
        p.ajouter("abriter", lieu=salle)
        return {"type": "abri", "lieu": salle}, p.etapes
    return None


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
    s, e = seuils(monde, id), esprit(monde, id)
    return sorted((b for b in s if e["besoins"].get(b, 0) >= s[b]),
                  key=lambda b: (s[b] - e["besoins"][b], BESOINS.index(b)))


def confie_a_autrui(monde, id, objet):
    """Ce qu'il a confié à quelqu'un qu'il croit fiable, il ne le fait pas à sa place."""
    p = profil(monde, id)
    return bool(p) and any(x["condition"].get("objet") == objet and _delegue(monde, id, x) for x in p["pulsions"])


def _plan_faim(monde, id):
    """Apaiser la faim : le plan le moins coûteux trouvé par la recherche (``planification``)."""
    from .planification import planifier
    return planifier(monde, id, "faim")


def _plan_froid(monde, id):
    """Se réchauffer : le plan le moins coûteux trouvé par la recherche (``planification``)."""
    from .planification import planifier
    return planifier(monde, id, "chaleur")


# Besoins qu'un geste qui dure apaise : la méthode, et le seuil où il s'achève.
PROGRES = {"repos": (_plan_reposer, REPOS_FIN), "chaleur": (_plan_froid, CHALEUR_FIN),
           "securite": (_plan_abri, SECURITE_FIN)}
GESTE_PROGRES = {"repos": "reposer", "chaleur": "chauffer", "securite": "abriter"}


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
    surveillance) passe après ce qui presse vraiment et après une tâche acceptée.

    Un besoin qui vient à peine de franchir son seuil laisse finir le plan en cours d'un autre
    motif : on achève le geste entamé avant de céder à la fatigue ou à la faim naissantes."""
    p, e = profil(monde, id), esprit(monde, id)
    buts = []
    en_cours = e["intention"]["motif"] if e["intention"] and e["intention"]["plan"] else None
    pressants = urgents(monde, id)
    for besoin in pressants:
        if (en_cours and besoin != en_cours
                and e["besoins"][besoin] < seuils(monde, id)[besoin] + INERTIE):
            continue
        if besoin == "faim":
            buts.append((besoin, _plan_faim, False))
            continue
        if besoin in PROGRES:
            # Le geste qui apaise d'abord ; les pulsions du même besoin (les rondes) restent des recours.
            buts.append((besoin, PROGRES[besoin][0], False))
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
    # Un protégé atteint sous ses yeux : il va le prévenir, comme une parole due.
    if any(s["type"] == "a_prevenir" for s in e["memoire"]):
        buts.append(("devoir", _plan_prevenir, False))
    # Ce qu'il garde sous clé et a lui-même ouvert, il le referme sans attendre l'urgence.
    for x in p["pulsions"]:
        c = x["condition"]
        if (c.get("verrouillee") and ouvert_par_soi(monde, id, c["objet"], RECENT) and not satisfaite(monde, id, c)
                and not retabli_par_son_plan(monde, id, c)):
            buts.append((x["besoin"], lambda m, i, c=c: _plan_pulsion(m, i, c), False))
    # Assis pour se reposer, ou près du feu, il ne s'en va qu'une fois remis, ou pour plus pressant.
    # Seulement si son plan comporte bien ce geste : une ronde a le même motif que l'abri.
    for besoin, (methode, fin) in PROGRES.items():
        if (e["intention"] and e["intention"]["motif"] == besoin and e["besoins"].get(besoin, 0) > fin
                and any(x["operation"] == GESTE_PROGRES[besoin] for x in e["intention"]["plan"])):
            buts.append((besoin, methode, False))
    # La routine : ses rondes, même quand le besoin qu'elles servent ne presse pas.
    for x in p["pulsions"]:
        if (periodique(x["condition"]) and x["besoin"] not in pressants
                and not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x)):
            buts.append((x["besoin"], lambda m, i, c=x["condition"]: _plan_pulsion(m, i, c), True))
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
    # Le corps suit le geste en cours : l'effort creuse, le repos délasse.
    from .corps import vivre
    geste = e["intention"]["plan"][0]["operation"] if e["intention"] and e["intention"]["plan"] else None
    vivre(monde, id, 1, effort=geste in EFFORTS, repos=geste == "reposer")
    ressentir(monde, id)
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


def menager_flamme(monde, id, minute):
    """Une flamme portable qu'il a allumée ou employée pour allumer, et que son plan n'emploie
    plus, se consume pour rien : il l'éteint d'abord, et la garde pour plus tard. Une lanterne
    portée pour y voir n'est pas concernée."""
    from .perception import allumee
    e = esprit(monde, id)
    plan = e["intention"]["plan"] if e["intention"] else []
    vises = {x["cible"] for x in plan} | {x["outil"] for x in plan}
    allumees = {s["objet"] for s in e["memoire"] if s["type"] == "flamme_employee"}
    flamme = next((k for k in sorted(allumees) if k in monde.objets and k not in vises
                   and porte_par(monde, k, id) and allumee(monde.objets[k])), None)
    if flamme is None:
        return
    geste = {"operation": "eteindre", "cible": flamme, "outil": "", "lieu": "", "condition": ""}
    if e["intention"]:
        plan.insert(0, geste)
    else:
        e["intention"] = {"but": {"type": "menager", "objet": flamme}, "motif": "menager", "plan": [geste],
                          "depuis": minute, "attente": 0}


def renoncer(monde, id, minute):
    e = esprit(monde, id)
    intention = e["intention"]
    e["renoncements"][intention["motif"]] = minute
    memoriser(monde, id, {"type": "renoncement", "but": dict(intention["but"])})
    e["intention"] = None
