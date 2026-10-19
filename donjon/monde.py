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
from .geometrie import cases


class ErreurMonde(ValueError):
    """Refus du moteur. Le message s'adresse au joueur ; ``attendu`` dit au MJ, en champs et
    identifiants, ce qu'une proposition corrigée doit contenir (voir ``refus.py``)."""

    def __init__(self, message="", attendu=""):
        super().__init__(message)
        self.attendu = attendu


def normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFD", texte.lower())
    return " ".join("".join(c for c in texte if unicodedata.category(c) != "Mn")
                    .replace("’", "'").strip(" .?!").split())


def reference_exacte(objets, texte):
    """Résout une référence structurée par identifiant, nom ou alias, sans deviner."""
    if not isinstance(texte, str):
        return None
    reference = normaliser(texte)
    objets = list(objets)
    for article in ("de la ", "du ", "des ", "la ", "le ", "les ", "un ", "une ", "l'"):
        if reference.startswith(article):
            reference = reference[len(article):]
            break
    if not reference:
        return None
    identifiants = [o["id"] for o in objets if reference == normaliser(o["id"])]
    if len(identifiants) == 1:
        return identifiants[0]
    noms = [o["id"] for o in objets if reference in
            [normaliser(n) for n in (o["nom"], *o.get("aliases", []))]]
    if len(noms) == 1:
        return noms[0]
    if identifiants or noms:
        raise ErreurMonde("Cette référence désigne plusieurs objets ; précisez lequel.")
    return None


def objet(id, nom, type, lieu, **proprietes):
    return {"id": id, "nom": nom, "type": type, "lieu": lieu,
            "aliases": [], "materiau": "", "masse": 0, "mobile": False,
            "integrite": 10, "maximum": 10, **proprietes}


def nouveau_monde(seed=1985):
    from .scenario_crypte import nouveau_monde as creer_crypte
    return creer_crypte(seed)


def nouveau_monde_libre(salles, objets, salle_depart, position, scenario, objectif=None, seed=1985):
    """Crée une aventure directement à partir de ses propres données."""
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
        from .esprits import installer as installer_esprits
        installer_esprits(self)
        from .corps import installer as installer_corps
        installer_corps(self)
        from .franchissement import installer as installer_franchissements
        installer_franchissements(self)
        from .matiere import installer as installer_matiere
        installer_matiere(self)
        from .artisanat import installer as installer_artisanat
        installer_artisanat(self)
        from .espace import installer as installer_espace
        installer_espace(self)
        self.verifier()

    def _installer_recit(self):
        self.data.setdefault("conversation", [])

    def memoriser(self, joueur, reponse, nature="dialogue"):
        """Mémoire de conversation, jamais une source de nouvelles vérités physiques."""
        self.data["conversation"].append({"joueur": joueur[:2000], "reponse": reponse[:4000],
                                          "nature": nature, "revision": self.data["revision"]})
        self.data["conversation"] = self.data["conversation"][-12:]

    def _installer_personnages(self):
        self.data.setdefault("souvenirs_personnages", {})

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
        for salle in self.data["salles"].values():
            salle.setdefault("fenetres", 0)
            salle.setdefault("lumiere_naturelle", 0)

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

    def present_physique(self, id, trace=None, salle=None):
        """Présence matérielle dans une salle, par défaut celle du joueur."""
        if id not in self.objets:
            return False
        trace = set() if trace is None else trace
        if id in trace:
            return False
        trace.add(id)
        o = self.objets[id]
        salle = salle or self.joueur["salle"]
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
        if o["lieu"] == salle or (o["lieu"] == "joueur" and self.joueur["salle"] == salle):
            return True
        parent = self.objets.get(o["lieu"])
        if not parent or not self.present_physique(parent["id"], trace, salle):
            return False
        if parent["type"] == "contenant" and not parent["ouverte"]:
            return False
        return True

    def visible(self, id):
        o = self.objets.get(id, {})
        from .esprits import cache_par_porteur
        if o and cache_par_porteur(self, o, "joueur"):
            return False
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
        raise ErreurMonde("Tu ne vois pas cet objet ici. Tape « regarder ».")

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
            # L'esprit d'un PNJ (profil, besoins, pulsions) reste interne au moteur.
            vue.pop("profil", None)
            if "constats_capacites" in vue:
                from .capacites_objet import resume_constats
                vue["constats_capacites"] = resume_constats(o, self.objets)
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
        from .narration import ambiance_etablie
        salle = copy.deepcopy(self.data["salles"][self.joueur["salle"]])
        salle["id"] = self.joueur["salle"]
        joueur = copy.deepcopy(self.joueur)
        joueur["salle_nom"] = salle["nom"]
        # Le corps se lit en mots : faim, froid, fatigue légers, supportables, pressants, extrêmes.
        from .corps import etat as etat_corps
        joueur.pop("besoins", None)
        joueur["corps"] = etat_corps(self)
        lieux_connus = {id: s["nom"] for id, s in self.data["salles"].items()
                       if id == self.joueur["salle"] or id in self.data["visitees"]}
        souvenirs_visuels = []
        if self.data.get("mode_cases"):
            for id, souvenir in self.data.get("souvenirs_visuels", {}).items():
                salle_souvenir = souvenir["salle"]
                if ((salle_souvenir, *souvenir.get("contact", souvenir["position"])) in champ_vision
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
                "ambiance_etablie": ambiance_etablie(self),
                "minutes": self.data["minutes"], "bruit": self.data["bruit"],
                "evenements_recents": [e for e in self.data["journal"]
                    if e["action"]["action"] not in (("marcher", "aller") if self.data.get("mode_cases") else ("marcher",))][-6:]}

    def contexte_scenario(self):
        """Prémisse publique et déplacements réellement enregistrés."""
        voyages = [e for e in self.data["journal"]
                   if e["reussite"] and (e["action"]["action"] == "aller" and not self.data.get("mode_cases")
                       or any(f.startswith(("Tu entres dans :", "Vous entrez dans :")) for f in e["faits"]))]
        scenario = copy.deepcopy(self.data["scenario"])
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
            from .matiere import verifier as verifier_matiere
            verifier_matiere(self)
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
            from .transitions_scenario import verifier as verifier_transitions_scenario
            verifier_transitions_scenario(self)
            from .pnj import verifier as verifier_pnj
            verifier_pnj(self)
            from .esprits import verifier as verifier_esprits
            verifier_esprits(self)
            from .corps import verifier as verifier_corps
            verifier_corps(self)
            from .ecoute import verifier as verifier_ecoute
            verifier_ecoute(self)
            from .horloges import verifier as verifier_horloges
            verifier_horloges(self)
            from .narration import verifier as verifier_narration
            verifier_narration(self)
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
                if o.get("en_vente"):
                    vendeur = o.get("vendeur")
                    assert (vendeur in d["objets"] and d["objets"][vendeur]["type"] == "personnage"
                            and type(o.get("prix")) is int and o["prix"] > 0), "Vente sans vendeur ou prix valide"
                if "luminosite" in o:
                    assert (type(o["luminosite"]) is int and 0 <= o["luminosite"] <= 2
                            and type(o["combustible"]) is int and o["combustible"] >= 0
                            and type(o["allume"]) is bool), "Source lumineuse invalide"
                    assert not o["allume"] or (o["combustible"] > 0 and o["integrite"] > 0), "Source allumée sans combustible ou détruite"
                assert "foyer" not in o or (o["foyer"] is True and "luminosite" in o), "Foyer invalide"
                if "combustible" in o.get("usages", []):
                    assert (type(o.get("charges")) is int and o["charges"] >= 0
                            and type(o.get("duree_combustion")) is int and 1 <= o["duree_combustion"] <= 240), "Combustible invalide"
                if "sonorite" in o:
                    assert type(o["sonorite"]) is int and 1 <= o["sonorite"] <= 3, "Sonorité invalide"
                if "usages" in o:
                    assert isinstance(o["usages"], list) and all(isinstance(u, str) for u in o["usages"]), "Usages d'outil invalides"
                    assert len(o["usages"]) == len(set(o["usages"])), "Usages d'outil dupliqués"
                if "puissance" in o:
                    assert type(o["puissance"]) is int and o["puissance"] >= 0, "Puissance d'outil invalide"
                if "seuil_coupe" in o:
                    assert type(o["seuil_coupe"]) is int and 1 <= o["seuil_coupe"] <= 7, "Résistance à la coupe invalide"
                if "constats_capacites" in o:
                    from .capacites_objet import CAPACITES_REVUE, empreinte, statut
                    constats = o["constats_capacites"]
                    assert isinstance(constats, list) and all(
                        isinstance(c, dict) and set(c) == {
                            "capacite", "issue", "empreinte", "moyen_nom", "moyen_id",
                            "empreinte_moyen", "puissance_observee"}
                        and c["capacite"] in CAPACITES_REVUE
                        and c["issue"] in ("etablie", "ecartee")
                        and (c["issue"] != "etablie" or c["capacite"] == "tranchable")
                        and isinstance(c["empreinte"], str) and len(c["empreinte"]) == 64
                        and isinstance(c["moyen_nom"], str)
                        and isinstance(c["moyen_id"], str)
                        and isinstance(c["empreinte_moyen"], str)
                        and ((c["capacite"] == "tranchable"
                              and c["moyen_id"] and len(c["empreinte_moyen"]) == 64)
                             or (c["capacite"] != "tranchable"
                                 and not c["moyen_id"] and not c["empreinte_moyen"]))
                        and type(c["puissance_observee"]) is int
                        and c["puissance_observee"] >= 0
                        for c in constats), "Constats physiques invalides"
                    actifs = {}
                    for c in constats:
                        qualite_stable = c["issue"] == "etablie"
                        if c["empreinte"] != empreinte(o, usure=not qualite_stable):
                            continue
                        if c["moyen_id"]:
                            moyen = d["objets"].get(c["moyen_id"])
                            if (moyen is None or c["empreinte_moyen"] !=
                                    empreinte(moyen, usure=not qualite_stable)):
                                continue
                            if qualite_stable and (o["integrite"] == 0 or moyen["integrite"] == 0):
                                continue
                        cle_constat = (c["capacite"], c["moyen_id"])
                        assert (cle_constat not in actifs or actifs[cle_constat] == c["issue"]), "Constats physiques contradictoires"
                        actifs[cle_constat] = c["issue"]
                        positif = statut({**o, "constats_capacites": []}, c["capacite"]) == "etablie"
                        if positif and c["capacite"] == "tranchable":
                            assert ((c["issue"] == "etablie") ==
                                    (c["puissance_observee"] >= o["seuil_coupe"])), "Constat physique contradictoire"
                        else:
                            assert not positif, "Constat physique contradictoire"
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
