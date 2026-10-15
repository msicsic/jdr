"""Etat sérialisable, relations spatiales et perception. Aucune dépendance externe."""
from __future__ import annotations

import copy
import json
import os
import random
import unicodedata
from pathlib import Path

from .perception import eclairage
from .francais import designer
from .geometrie import installer, cases


class ErreurMonde(ValueError):
    pass


def normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFD", texte.lower())
    return " ".join("".join(c for c in texte if unicodedata.category(c) != "Mn")
                    .replace("’", "'").strip(" .?!").split())


def objet(id, nom, type, lieu, **proprietes):
    return {"id": id, "nom": nom, "type": type, "lieu": lieu,
            "aliases": [], "materiau": "", "masse": 0, "mobile": False,
            "integrite": 10, "maximum": 10, **proprietes}


def nouveau_monde(seed=1985):
    objets = [
        objet("porte", "porte de la crypte", "porte", "antichambre",
              aliases=["porte", "battant"], materiau="chêne", masse=80,
              integrite=30, maximum=30, relie=["antichambre", "crypte"],
              ouverte=False, verrouillee=True, detachee=False, bloque_par=None,
              fixations=["axe_haut", "axe_bas"]),
        objet("gravure", "gravure du chevalier", "motif", "porte",
              aliases=["gravure", "runes", "inscription"], materiau="chêne",
              motif="Un chevalier agenouillé tend une clé à une silhouette couronnée.",
              inscription="Au veilleur revient le dernier serment.",
              sens="La clé du veilleur ouvre le coffre de la crypte."),
        objet("serrure", "serrure de la porte", "serrure", "porte",
              aliases=["serrure"], materiau="fer", bloquee=False),
        objet("axe_haut", "axe du gond supérieur", "fixation", "porte",
              aliases=["axe superieur", "gond superieur", "axe haut", "gond haut"],
              materiau="fer", masse=0.2, mobile=True, attache=True,
              amovible=True, cote="antichambre", resistance=12),
        objet("axe_bas", "axe du gond inférieur", "fixation", "porte",
              aliases=["axe inferieur", "gond inferieur", "axe bas", "gond bas"],
              materiau="fer", masse=0.2, mobile=True, attache=True,
              amovible=True, cote="antichambre", resistance=12),
        objet("couteau", "couteau à lame fine", "outil", "joueur",
              aliases=["couteau", "poignard", "dague"], materiau="acier", masse=0.3,
              mobile=True, usages=["levier_fin", "couper"], puissance=2,
              integrite=3, maximum=3),
        objet("cire", "bloc de cire malléable", "consommable", "joueur",
              aliases=["cire", "bloc de cire"], materiau="cire", masse=0.2,
              mobile=True, usages=["empreinte"], charges=2),
        objet("cle", "clé du veilleur", "cle", "antichambre",
              aliases=["cle", "cle du veilleur"], materiau="bronze", masse=0.1,
              mobile=True, ouvre=["coffre"]),
        objet("marchand", "Gorm le marchand", "personnage", "echoppe",
              aliases=["gorm", "marchand"], humeur="calme"),
        objet("pied_de_biche", "pied-de-biche", "outil", "echoppe",
              aliases=["pied de biche", "pied-de-biche", "levier"], materiau="fer",
              masse=2, mobile=True, usages=["levier", "percussion"], puissance=7,
              prix=12, en_vente=True),
        objet("marteau", "marteau", "outil", "echoppe",
              aliases=["marteau"], materiau="fer et bois", masse=1,
              mobile=True, usages=["percussion", "cale"], puissance=5,
              prix=7, en_vente=True),
        objet("crochets", "trousse de crochets", "outil", "echoppe",
              aliases=["crochets", "crochet", "trousse"], materiau="acier", masse=0.1,
              mobile=True, usages=["crochetage"], puissance=0,
              integrite=3, maximum=3, prix=8, en_vente=True),
        objet("coffre", "coffre de pierre", "contenant", "crypte",
              aliases=["coffre"], materiau="pierre", masse=150,
              integrite=40, maximum=40, ouverte=False, verrouillee=True),
        objet("anneau", "anneau du veilleur", "tresor", "coffre",
              aliases=["anneau", "tresor"], materiau="argent", masse=0.02, mobile=True),
    ]
    # Même les surfaces mentionnées ont une identité et peuvent être ciblées.
    for salle in ("antichambre", "echoppe", "crypte"):
        for surface in ("sol", "murs", "plafond"):
            objets.append(objet(f"{salle}_{surface}", surface, "surface", salle,
                                aliases=[surface], materiau="pierre",
                                integrite=100, maximum=100))
    return Monde({
        "version": 1, "seed": seed, "jets": 0, "revision": 0, "minutes": 0,
        "bruit": 0, "visitees": ["antichambre"], "connus": [], "lus": [],
        "journal": [], "arbitrages": {},
        "objectif_partie": {
            "objet": "anneau", "lieu": "joueur",
            "message": "OBJECTIF ATTEINT : vous avez retrouvé l'anneau du veilleur. L'exploration reste ouverte.",
        },
        "joueur": {"nom": "Corvus", "salle": "antichambre", "pv": 18,
                    "pv_max": 18, "or": 24, "capacite": 12,
                    "stats": {"FOR": 12, "DEX": 16, "INT": 14, "PER": 12, "CHA": 12}},
        "salles": {
            "antichambre": {"nom": "Antichambre", "sorties": {
                "ouest": {"vers": "echoppe", "porte": None},
                "nord": {"vers": "crypte", "porte": "porte"}}},
            "echoppe": {"nom": "Echoppe de Gorm", "sorties": {
                "est": {"vers": "antichambre", "porte": None}}},
            "crypte": {"nom": "Crypte du veilleur", "sorties": {
                "sud": {"vers": "antichambre", "porte": "porte"}}},
        },
        "objets": {o["id"]: o for o in objets},
    })


def nouveau_monde_libre(salles, objets, salle_depart, position, scenario, objectif=None, seed=1985):
    """Crée une aventure sans les lieux, personnages ni objets de la crypte."""
    return Monde({
        "version": 1, "seed": seed, "jets": 0, "revision": 0, "minutes": 0,
        "bruit": 0, "visitees": [salle_depart], "connus": [], "lus": [],
        "journal": [], "arbitrages": {}, "scenario_id": "libre", "geometrie_version": 1,
        "joueur": {"nom": "Corvus", "salle": salle_depart, "position": list(position),
                   "pv": 18, "pv_max": 18, "or": 0, "capacite": 12,
                   "stats": {"FOR": 12, "DEX": 16, "INT": 14, "PER": 12, "CHA": 12}},
        "salles": copy.deepcopy(salles), "objets": copy.deepcopy(objets),
        "scenario": copy.deepcopy(scenario), "objectif_partie": copy.deepcopy(objectif),
    })


class Monde:
    def __init__(self, data):
        self.data = data
        from .profil_joueur import installer as installer_profil
        installer_profil(self)
        self._installer_eclairage()
        self._installer_recit()
        self._installer_personnages()
        from .dialogues import installer as installer_dialogues
        installer_dialogues(self)
        from .connaissances import installer as installer_savoirs
        installer_savoirs(self)
        from .vol import installer as installer_vol
        installer_vol(self)
        installer(self)
        if self.data.get("defi_relais"):
            from .defi import installer_consigne
            installer_consigne(self)
        from .franchissement import installer as installer_franchissements
        installer_franchissements(self)
        from .artisanat import installer as installer_artisanat
        installer_artisanat(self)
        from .espace import installer as installer_espace
        installer_espace(self)
        self.verifier()

    def _installer_recit(self):
        """Prémisse d'auteur persistante, ajoutée aux anciennes parties sans réinitialisation."""
        if "scenario" not in self.data:
            self.data["scenario"] = {
                "version": 1,
                "debut": "Tu as accepté de retrouver l'anneau du veilleur à la demande de Gorm. "
                         "Le marchand t'a conduit de son échoppe à cette antichambre, puis est retourné à ses affaires. "
                         "C'est là que ton exploration a commencé.",
                "objectif": "Retrouver l'anneau du veilleur dans la crypte.",
                "gorm": "Gorm tient l'échoppe à l'ouest de l'antichambre. Il t'a demandé de retrouver l'anneau, "
                        "mais n'a expliqué ni ce qu'il représente pour lui ni pourquoi il ne va pas le chercher lui-même. "
                        "Aucune récompense n'a été convenue.",
                "liberte_personnage": "Le joueur choisit les raisons personnelles de Corvus. "
                                      "Ne lui impose ni sentiments, ni amnésie, ni passé supplémentaire.",
            }
            if "echoppe" not in self.data["visitees"]:
                self.data["visitees"].append("echoppe")
        self.data.setdefault("conversation", [])

    def memoriser(self, joueur, reponse, nature="dialogue"):
        """Mémoire de conversation, jamais une source de nouvelles vérités physiques."""
        self.data["conversation"].append({"joueur": joueur[:2000], "reponse": reponse[:4000],
                                          "nature": nature, "revision": self.data["revision"]})
        self.data["conversation"] = self.data["conversation"][-12:]

    def _installer_personnages(self):
        """Portrait d'auteur et souvenir de la rencontre établie dans la prémisse."""
        self.data.setdefault("souvenirs_personnages", {})
        if self.data.get("scenario_id") == "libre":
            return
        if self.data.get("personnages_version") == 1:
            return
        gorm = self.objets["marchand"]
        gorm.setdefault("portrait", "Gorm est un homme trapu d'une cinquantaine d'années, au visage large.")
        gorm.setdefault("maniere_de_parler", "Gorm parle peu et va droit au but, d'une voix grave.")
        for detail in (
            objet("barbe_gorm", "barbe de Gorm", "partie_corps", "marchand",
                  aliases=["barbe", "sa barbe"], genre="f", materiau="poils",
                  description_visuelle="Sa barbe est courte et grisonnante.",
                  description_tactile="Les poils de sa barbe sont courts et rêches."),
            objet("mains_gorm", "mains de Gorm", "partie_corps", "marchand",
                  aliases=["mains", "ses mains"], genre="f", pluriel=True, materiau="peau",
                  description_visuelle="Ses mains sont larges et calleuses.",
                  description_tactile="La peau de ses mains est épaisse et rugueuse."),
        ):
            self.objets.setdefault(detail["id"], detail)
        # Pas de lecture de son humeur ou de sa position actuelle à distance.
        self.data["souvenirs_personnages"].setdefault("marchand", {
            **self._portrait_public(gorm),
            "details": [{"nom": self.objets[id]["nom"],
                         "description": self.objets[id]["description_visuelle"]}
                        for id in ("barbe_gorm", "mains_gorm")],
            "maniere_de_parler": gorm["maniere_de_parler"],
            "source": "Rencontre avec Gorm avant le début de l'exploration : il t'a conduit à l'antichambre.",
        })
        self.data["personnages_version"] = 1

    def _portrait_public(self, personnage):
        """Liste blanche : jamais de secrets, d'inventaire ou de lieu dans un souvenir."""
        return {"nom": personnage["nom"], "portrait": personnage.get("portrait", ""),
                "traits": {k: v["texte"] for k, v in personnage.get("facettes", {}).items() if "texte" in v},
                "details": [{"nom": e["nom"], "description": e["description_visuelle"]}
                            for e in self.enfants(personnage["id"])
                            if e.get("description_visuelle") and self.visible(e["id"])]}

    def actualiser_souvenirs_personnages(self):
        """Appelé par le moteur après une action ; une consultation reste sans effet."""
        if eclairage(self)["niveau"] < 2:
            return
        for o in self.presents():
            if o["type"] != "personnage":
                continue
            if self.data.get("mode_cases"):
                from .spatial import proche
                if not proche(self, o["id"]):
                    continue
            souvenir = self.data["souvenirs_personnages"].setdefault(o["id"], {})
            souvenir.update(self._portrait_public(o))
            souvenir["source"] = "Vu dans " + self.data["salles"][self.joueur["salle"]]["nom"]
            souvenir["minute"] = self.data["minutes"]

    def _installer_eclairage(self):
        """Extension additive des parties v1 ; aucune source existante n'est rallumée au chargement."""
        if self.data.get("eclairage_version") == 1:
            return
        for salle in self.data["salles"].values():
            salle.setdefault("fenetres", 0)
            salle.setdefault("lumiere_naturelle", 0)
        if self.data.get("scenario_id") == "libre":
            self.data["eclairage_version"] = 1
            return
        for o in (
            objet("lanterne", "lanterne", "luminaire", "joueur", aliases=["lampe"],
                  materiau="fer et verre", mobile=True, masse=0.8,
                  luminosite=2, allume=True, combustible=60),
            objet("torche", "torche", "luminaire", "antichambre", aliases=["flambeau"],
                  materiau="bois", mobile=True, masse=0.3,
                  luminosite=2, allume=False, combustible=30),
            objet("brasero", "brasero", "luminaire", "echoppe", aliases=["foyer"],
                  materiau="fer", masse=20, luminosite=2, allume=True, combustible=180),
            objet("briquet", "briquet à silex", "outil", "joueur", aliases=["briquet", "silex"],
                  materiau="fer et silex", mobile=True, masse=0.1, usages=["allumage"]),
        ):
            if (o["lieu"] == "joueur" and o["id"] not in self.objets
                    and self.charge() + o["masse"] > self.joueur["capacite"]):
                o["lieu"] = self.joueur["salle"]
            self.objets.setdefault(o["id"], o)
        self.data["eclairage_version"] = 1

    @property
    def objets(self):
        return self.data["objets"]

    @property
    def joueur(self):
        return self.data["joueur"]

    def copier(self):
        return Monde(copy.deepcopy(self.data))

    def enfants(self, id):
        return [o for o in self.objets.values() if o["lieu"] == id]

    def present_physique(self, id, trace=None):
        if id not in self.objets:
            return False
        trace = set() if trace is None else trace
        if id in trace:
            return False
        trace.add(id)
        o = self.objets[id]
        salle = self.joueur["salle"]
        if o.get("incorpore"):
            return False
        if o.get("appui_vertical"):
            a = o["appui_vertical"]
            return salle in (a["bas"], a["haut"])
        if o.get("installation"):
            support = self.objets.get(o["installation"]["support"], {})
            a = support.get("appui_vertical", {})
            return salle in (a.get("bas"), a.get("haut")) and o["lieu"] == a.get("bas")
        if o.get("cote") and o.get("attache") and o["cote"] != salle:
            return False
        if o["type"] == "porte":
            return salle in o["relie"]
        if o["lieu"] in (salle, "joueur"):
            return True
        parent = self.objets.get(o["lieu"])
        if not parent or not self.present_physique(parent["id"], trace):
            return False
        if parent["type"] == "contenant" and not parent["ouverte"]:
            return False
        return True

    def visible(self, id):
        o = self.objets.get(id, {})
        if o.get("detail_local"):
            if eclairage(self)["niveau"] < 2:
                return False
            if self.data.get("mode_cases"):
                from .spatial import proche
                if not proche(self, id):
                    return False
        if self.data.get("mode_cases"):
            from .spatial import visible
            return visible(self, id)
        return self.present_physique(id) and eclairage(self)["niveau"] > 0

    def accessible(self, id):
        if self.data.get("mode_cases"):
            from .spatial import proche
            return self.visible(id) or (self.present_physique(id) and
                   (self.est_porte(id) or (id in self.data["connus"] and proche(self, id))))
        if not self.present_physique(id):
            return False
        # Dans le noir on peut retrouver ses propres affaires ou une cible déjà examinée.
        return (self.visible(id) or self.objets[id]["lieu"] == "joueur"
                or id in self.data["connus"])

    def presents(self):
        return [o for o in self.objets.values() if self.visible(o["id"])]

    def trouver(self, texte):
        texte = normaliser(texte)
        for article in ("la ", "le ", "les ", "du ", "de la ", "l'"):
            if texte.startswith(article):
                texte = texte[len(article):]
                break
        candidats, exacts = [], []
        for o in self.objets.values():
            if not self.accessible(o["id"]):
                continue
            if texte == normaliser(o["id"]):
                return o["id"]
            noms = [o["nom"], *o["aliases"]]
            if texte in [normaliser(n) for n in noms]:
                exacts.append(o["id"])
            if texte and any(texte in normaliser(n) for n in noms):
                candidats.append(o["id"])
        candidats = exacts or candidats
        if len(candidats) == 1:
            return candidats[0]
        if candidats:
            raise ErreurMonde("Précisez : " + ", ".join(designer(self.objets[i]) for i in candidats) + ".")
        raise ErreurMonde("Vous ne voyez pas cet objet ici. Tapez « regarder ».")

    def charge(self):
        return sum(o["masse"] for o in self.objets.values() if self.est_porte(o["id"]))

    def est_porte(self, id):
        """Inclut les objets contenus dans une besace ou un contenant porté."""
        vus = set()
        while id in self.objets and id not in vus:
            vus.add(id)
            id = self.objets[id]["lieu"]
        return id == "joueur"

    def d20(self):
        self.data["jets"] += 1
        return random.Random(f'{self.data["seed"]}:{self.data["jets"]}').randint(1, 20)

    def contexte(self):
        """Vue du MJ bornée à ce qui est perceptible : pas de trésor caché ni de sens secret."""
        objets = []
        niveau = eclairage(self)["niveau"]
        if self.data.get("mode_cases"):
            from .spatial import champ_visible
            from .localisation import decrire as localiser
            champ_vision = champ_visible(self)
        for o in self.objets.values():
            if not self.accessible(o["id"]):
                continue
            vue = copy.deepcopy(o)
            vue["visible"] = self.visible(o["id"])
            if self.data.get("mode_cases"):
                from .spatial import proche, position_cible
                vue["a_portee"] = proche(self, o["id"])
                vue["case_percue"] = position_cible(self, o["id"])
                vue["localisation"] = localiser(self, o["id"], champ_vision)
            if o["type"] == "contenant" and o["ouverte"] and (not self.data.get("mode_cases") or vue["a_portee"]):
                vue["contenu_vide"] = not any(self.present_physique(e["id"]) for e in self.enfants(o["id"]))
            if o["id"] not in self.data["lus"]:
                vue.pop("sens", None)
            if niveau < 2 or (self.data.get("mode_cases") and not vue["a_portee"]):
                for champ in ("motif", "inscription", "sens", "portrait", "description_visuelle", "maniere_de_parler", "facettes"):
                    vue.pop(champ, None)
            objets.append(vue)
        from .dialogues import interlocuteurs, missions_discutables, contrats_publics
        from .connaissances import contexte as connaissances_pnj
        salle = copy.deepcopy(self.data["salles"][self.joueur["salle"]])
        salle["id"] = self.joueur["salle"]
        joueur = copy.deepcopy(self.joueur)
        joueur["salle_nom"] = salle["nom"]
        lieux_connus = {id: s["nom"] for id, s in self.data["salles"].items()
                       if id == self.joueur["salle"] or id in self.data["visitees"]}
        souvenirs_visuels = []
        if self.data.get("mode_cases"):
            for id, souvenir in self.data.get("souvenirs_visuels", {}).items():
                salle_souvenir = souvenir["salle"]
                if ((salle_souvenir, *souvenir["position"]) in champ_vision
                        or self.est_porte(id)):
                    continue
                souvenirs_visuels.append({
                    "nom": souvenir["nom"],
                    "derniere_salle": lieux_connus.get(salle_souvenir, "lieu encore sans nom"),
                })
        if self.data.get("mode_cases"):
            from .spatial import sortie_visible
            salle.pop("plan", None)  # Le MJ ne reçoit pas la géométrie des recoins invisibles.
            salle["sorties"] = {direction: sortie for direction, sortie in salle["sorties"].items()
                                if sortie_visible(self, self.joueur["salle"], direction)}
        for sortie in salle["sorties"].values():
            sortie["nom_destination"] = lieux_connus.get(sortie["vers"], "inexploré")
        return {"revision": self.data["revision"], "joueur": joueur, "lieux_connus": lieux_connus,
                "mode_cases": bool(self.data.get("mode_cases")), "salle": salle,
                "objets_perceptibles": objets,
                "souvenirs_visuels": souvenirs_visuels,
                "perception": eclairage(self),
                "scenario": self.contexte_scenario(),
                "souvenirs_personnages": copy.deepcopy(self.data["souvenirs_personnages"]),
                "interlocuteurs": interlocuteurs(self), "missions_discutables": missions_discutables(self),
                "engagements": contrats_publics(self),
                "connaissances_pnj": connaissances_pnj(self),
                "paroles_entendues": copy.deepcopy([
                    p for p in self.data.get("paroles_pnj", []) if "joueur" in p["auditeurs"]][-10:]),
                "souvenirs_faits": copy.deepcopy(self.data.get("faits_vus", [])[-20:]),
                "minutes": self.data["minutes"], "bruit": self.data["bruit"],
                "evenements_recents": [e for e in self.data["journal"]
                    if e["action"]["action"] not in (("marcher", "aller") if self.data.get("mode_cases") else ("marcher",))][-6:]}

    def contexte_scenario(self):
        """Prémisse publique et déplacements réellement enregistrés."""
        voyages = [e for e in self.data["journal"]
                   if e["reussite"] and (e["action"]["action"] == "aller" and not self.data.get("mode_cases")
                       or any(f.startswith(("Tu entres dans :", "Vous entrez dans :")) for f in e["faits"]))]
        scenario = copy.deepcopy(self.data["scenario"])
        if self.data.get("engagements") and "gorm" in scenario:
            scenario["gorm"] = scenario["gorm"].replace("Aucune récompense n'a été convenue.",
                "Au début de l'exploration, aucune récompense n'avait été convenue. Les engagements enregistrés indiquent l'accord actuel.")
        return {
            **scenario,
            "position": self.data["salles"][self.joueur["salle"]]["nom"],
            "dernier_deplacement": voyages[-1]["faits"] if voyages else [],
        }

    def verifier(self):
        d = self.data
        try:
            if d.get("mode_cases"):
                from .spatial import verifier as verifier_spatial
                verifier_spatial(self)
            from .espace import verifier as verifier_espace
            verifier_espace(self)
            from .artisanat import verifier as verifier_artisanat
            verifier_artisanat(self)
            from .connaissances import verifier as verifier_savoirs
            verifier_savoirs(self)
            from .vol import verifier as verifier_vol
            verifier_vol(self)
            from .objectifs import verifier as verifier_objectif
            verifier_objectif(self)
            from .faits_locaux import verifier as verifier_faits_locaux
            verifier_faits_locaux(self)
            assert d["version"] == 1, "Version de sauvegarde incompatible"
            assert d["joueur"]["salle"] in d["salles"], "Salle inconnue"
            assert d["joueur"]["or"] >= 0, "Or négatif"
            assert 0 <= d["joueur"]["pv"] <= d["joueur"]["pv_max"], "PV invalides"
            assert d["jets"] >= 0 and d["revision"] >= 0, "Compteurs invalides"
            from .dialogues import disponible
            for id, fonds in d["finances_pnj"].items():
                assert id in d["objets"] and d["objets"][id]["type"] == "personnage", "Bourse sans personnage"
                assert type(fonds) is int and fonds >= 0 and disponible(self, id) >= 0, "Fonds insuffisants pour les engagements"
            for id, mission in d["missions"].items():
                assert mission["donneur"] in d["finances_pnj"] and mission["objet"] in d["objets"], "Mission invalide"
                assert 0 < mission["prime_base"] <= mission["prime_plafond"], "Récompense invalide"
            for id, engagement in d["engagements"].items():
                assert id in d["missions"], "Engagement sans mission"
                assert engagement["statut"] in ("propose", "accepte", "refuse", "paye"), "Statut d'engagement invalide"
                assert type(engagement["montant"]) is int and 0 < engagement["montant"] <= d["missions"][id]["prime_plafond"], "Montant d'engagement invalide"
            for salle in d["salles"].values():
                plan = salle["plan"]
                assert 0 < len(plan["sol"]) <= 40 and all(0 < len(ligne) <= 40 for ligne in plan["sol"]), "Dimensions de plan invalides"
                assert all(set(ligne) <= {".", " "} for ligne in plan["sol"]) and cases(salle), "Sol invalide"
                assert len(plan["origine"]) == 2 and all(type(v) is int and abs(v) <= 100 for v in plan["origine"]), "Origine du plan invalide"
                assert salle["fenetres"] >= 0, "Nombre de fenêtres invalide"
                assert 0 <= salle["lumiere_naturelle"] <= 2, "Lumière naturelle invalide"
            for id, o in d["objets"].items():
                assert o["id"] == id, "Identité incohérente"
                assert 0 <= o["integrite"] <= o["maximum"], "Intégrité invalide"
                if "luminosite" in o:
                    assert 0 <= o["luminosite"] <= 2 and o["combustible"] >= 0, "Source lumineuse invalide"
                    assert not o["allume"] or (o["combustible"] > 0 and o["integrite"] > 0), "Source allumée sans combustible ou détruite"
                assert o["lieu"] in {*d["objets"], *d["salles"], "joueur"}, "Lieu inconnu"
                parents = {id}
                lieu = o["lieu"]
                while lieu in d["objets"]:
                    assert lieu not in parents, "Cycle de contenance"
                    parents.add(lieu)
                    lieu = d["objets"][lieu]["lieu"]
                if o.get("bloque_par"):
                    cale = d["objets"][o["bloque_par"]]
                    assert cale.get("cale_de") == id and cale["lieu"] == id, "Cale incohérente"
                if o.get("cale_de"):
                    assert d["objets"][o["cale_de"]].get("bloque_par") == id, "Blocage incohérent"
                if o.get("detachee") or o["integrite"] == 0:
                    if o["type"] == "porte":
                        assert o["ouverte"] and not o["verrouillee"], "Passage incohérent"
            assert self.charge() <= d["joueur"]["capacite"], "Inventaire trop lourd"
        except (AssertionError, KeyError, TypeError) as exc:
            raise ErreurMonde(f"Etat du monde invalide : {exc}") from exc

    def sauver(self, chemin):
        self.verifier()
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
        temporaire.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporaire, chemin)

    @classmethod
    def charger(cls, chemin):
        try:
            return cls(json.loads(Path(chemin).read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError) as exc:
            raise ErreurMonde(f"Impossible de charger la sauvegarde : {exc}") from exc
