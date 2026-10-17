"""Besoins, pulsions et délibération des PNJ ; planificateur borné sur leurs croyances.

Le profil d'auteur (``objet["profil"]``) déclare caractéristiques, traits, limites,
capacités, besoins et pulsions. Le moteur fait évoluer les besoins minute par minute ;
une pulsion qui cesse d'être satisfaite aux yeux du PNJ relance son besoin. Chaque minute,
le PNJ retient le but le plus urgent pour lequel il trouve un plan, cherché sur ce qu'il
croit, jamais sur la vérité du monde. Les étapes sont ensuite revalidées sur l'état réel
par ``pnj.py``. Tout est déterministe ; Luna n'intervient pas.
"""
from .esprits import esprit, lire, memoriser
from .spatial import porte_par

BESOINS = ("devoir", "biens", "securite", "faim", "repos")
LIMITES = ("ne_vole_pas", "ne_blesse_pas")
CAPACITES = ("crochetage",)
OPERATIONS = ("aller", "prendre", "poser", "ouvrir", "fermer", "deverrouiller", "verrouiller",
              "crocheter", "manger")
PROFONDEUR = 4
PATIENCE = 30          # minutes d'attente d'une occasion avant de renoncer
REPIT = 60             # minutes avant de reprendre un but abandonné
ATTEINTE = 30          # une pulsion qui cesse d'être satisfaite relance son besoin
VOL = 60               # un vol vu par sa victime
SATIETE = 50           # un repas
STATS = ("FOR", "DEX", "INT", "PER", "CHA")


def profil(monde, id):
    return monde.objets[id].get("profil")


def verifier_profil(monde, id, p):
    assert (isinstance(p, dict) and set(p) == {"caracteristiques", "traits", "limites", "capacites",
                                               "besoins", "pulsions"}), "Profil de PNJ mal formé"
    assert set(p["caracteristiques"]) == set(STATS) and all(
        type(v) is int and 1 <= v <= 20 for v in p["caracteristiques"].values()), "Caractéristiques de PNJ invalides"
    assert isinstance(p["traits"], str) and len(p["traits"]) <= 600, "Traits de PNJ invalides"
    assert set(p["limites"]) <= set(LIMITES) and set(p["capacites"]) <= set(CAPACITES), "Limite ou capacité inconnue"
    for nom, b in p["besoins"].items():
        assert (nom in BESOINS and set(b) == {"depart", "derive_heure", "urgence"}
                and all(isinstance(b[k], (int, float)) for k in b)
                and 0 <= b["depart"] <= 100 and 0 < b["urgence"] <= 100), "Besoin de PNJ invalide"
    for pulsion in p["pulsions"]:
        c = pulsion.get("condition", {})
        assert (set(pulsion) <= {"besoin", "condition", "delegue_a"} and pulsion.get("besoin") in p["besoins"]
                and c.get("objet") in monde.objets
                and ((set(c) == {"objet", "lieu"} and c["lieu"] in monde.data["salles"])
                     or (set(c) == {"objet", "verrouillee"} and c["verrouillee"] is True))
                and pulsion.get("delegue_a", "joueur") == "joueur"), "Pulsion de PNJ invalide"


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
    """Un événement (vol, atteinte à une pulsion) accroît un besoin déclaré."""
    e = esprit(monde, id)
    if besoin in e["besoins"]:
        e["besoins"][besoin] = min(100.0, e["besoins"][besoin] + montant)


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


def satisfaite(monde, id, condition):
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

    def ajouter(self, operation, cible="", outil="", lieu="", condition=""):
        self.etapes.append({"operation": operation, "cible": cible, "outil": outil,
                            "lieu": lieu, "condition": condition})

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

    def cle(self, cible):
        return next((k for k in _connus(self.monde, self.id)
                     if cible in self.monde.objets[k].get("ouvre", [])
                     and (k in self.portes or autorise(self.monde, self.id, k))), None)

    def outil(self, usage):
        return next((k for k in _connus(self.monde, self.id)
                     if usage in self.monde.objets[k].get("usages", [])
                     and (k in self.portes or autorise(self.monde, self.id, k))), None)

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
    for f in _connus(monde, id):
        o = monde.objets[f]
        etat = _cru(monde, id, f, "etat")
        if o["type"] != "nourriture" or (etat and not etat.get("disponible", True)):
            continue
        if not (porte_par(monde, f, id) or autorise(monde, id, f)):
            continue
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
            return {"type": "manger", "objet": f}, p.etapes
        except Echec:
            continue
    return None


def _plan_pulsion(monde, id, condition):
    p = Plan(monde, id)
    try:
        if "lieu" in condition:
            p.obtenir(condition["objet"])
            p.aller(condition["lieu"])
            p.ajouter("poser", condition["objet"], lieu=condition["lieu"])
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
    except Echec:
        return None
    return {"type": "pulsion", **condition}, p.etapes


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


def candidats(monde, id):
    """Buts envisageables, du besoin le plus pressant au moins pressant."""
    p, e = profil(monde, id), esprit(monde, id)
    urgents = sorted((b for b in p["besoins"] if e["besoins"][b] >= p["besoins"][b]["urgence"]),
                     key=lambda b: (p["besoins"][b]["urgence"] - e["besoins"][b], BESOINS.index(b)))
    for besoin in urgents:
        if besoin == "faim":
            yield besoin, _plan_manger
            continue
        pulsions = [x for x in p["pulsions"] if x["besoin"] == besoin]
        for x in pulsions:
            if not satisfaite(monde, id, x["condition"]) and not _delegue(monde, id, x):
                yield besoin, lambda m, i, c=x["condition"]: _plan_pulsion(m, i, c)
        if besoin == "biens":
            for x in pulsions:
                yield besoin, lambda m, i, c=x["condition"]: _plan_garder(m, i, c)


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
        if e["pulsions"][i] and not etat:
            relancer(monde, id, x["besoin"], ATTEINTE)
            memoriser(monde, id, {"type": "atteinte", "condition": dict(x["condition"])})
        e["pulsions"][i] = etat
    intention = e["intention"]
    if intention and intention["motif"] == "alerte":
        return  # Le réflexe déclaré garde la priorité jusqu'à son terme.
    for besoin, methode in candidats(monde, id):
        if e["renoncements"].get(besoin, -REPIT) + REPIT > minute:
            continue
        resultat = methode(monde, id)
        if not resultat:
            continue
        but, etapes = resultat
        meme = bool(intention) and intention["but"] == but
        e["intention"] = {"but": but, "motif": besoin, "plan": etapes,
                          "depuis": intention["depuis"] if meme else minute,
                          "attente": intention["attente"] if meme else 0}
        return
    e["intention"] = None


def renoncer(monde, id, minute):
    e = esprit(monde, id)
    intention = e["intention"]
    e["renoncements"][intention["motif"]] = minute
    memoriser(monde, id, {"type": "renoncement", "but": dict(intention["but"])})
    e["intention"] = None
