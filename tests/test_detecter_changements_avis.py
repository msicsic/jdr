"""Contrat de la sonde et de ses alertes, hors appel au modèle."""
import gzip
from collections import Counter
import copy
from contextlib import nullcontext
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import detecter_changements_avis as d
from tools import audit_nuits as audit


def entrees(valeur=0, lieu="salle"):
    return {**{c: valeur for c in d.CATEGORIES_EXTERNES}, "lieu": lieu,
            "_details": {"croyances": {}}, "besoins_continus": {}}


def episode(but, debut, quitte, valeur=0, accompli=False):
    intention = {"but": {"type": but}, "plan": [], "motif": but}
    return {"decision": d._resume_decision(intention), "debut_t": debut * 600,
            "fin_t": debut * 600, "quitte_t": quitte * 600,
            "debut_minute": debut, "quitte_minute": quitte,
            "cause_entree": "minute", "quitte_cause": "minute",
            "debut_entrees": entrees(valeur), "quitte_entrees": entrees(valeur),
            "accompli_au_depart": accompli}


class DetecterAvisTests(unittest.TestCase):
    def test_renouvellement_perceptif_reste_a_expliquer_et_preuves_prioritaires(self):
        for champ in ("perception", "provenance"):
            eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
            for ep in eps:
                ep["decision"]["plan"] = [{"operation": "demander", "cible": "tiers"}]
                for cle in ("debut_entrees", "quitte_entrees"):
                    ep[cle]["_details"].update(perception={}, provenance={"tiers.lieu": "entendu"})
            retour = eps[2]["debut_entrees"]
            retour["_details"][champ].update(
                {"tiers": ["salle", [2, 3]]} if champ == "perception" else {"tiers.lieu": "vu"})
            retour["perception_effective" if champ == "perception" else "provenance_croyances"] = 1
            with self.subTest(champ=champ):
                a = self.analyser(eps)
                self.assertEqual(a["comptes"], {"renouvellement_perceptif": 1})
                self.assertEqual((a["total_non_justifies"], a["total_justifies"], a["total_a_expliquer"]), (0, 0, 1))
                self.assertTrue(a["allers_retours"][0]["perception_diff_qr"][champ])
                n = {"scenario": "scene", "graine": 0, "heures": 1, "donnees": {"mesures": {}}}
                audit.ajouter_avis(n, a)
                self.assertEqual(n["donnees"]["mesures"]["avis_a_expliquer"], 1)
                self.assertIn("avis_a_expliquer", {x["code"] for x in audit.analyser_nuit(n)})
                # Une autre entrée changée reste à expliquer, sans être masquée.
                retour["alarmes_et_dangers"] = 1
                self.assertEqual(self.analyser(eps)["comptes"], {"entree_nouvelle_a_expliquer": 1})
                retour["alarmes_et_dangers"] = 0
                # L'entrée publiée employée conserve sa priorité du lot 271.
                eps[0]["quitte_entrees"]["_details"]["inventaire"] = {"portes": []}
                retour["_details"]["inventaire"] = {"portes": ["tiers"]}
                retour["inventaire_et_droits"] = 1
                eps[2]["moyen_admissible"] = True
                self.assertEqual(self.analyser(eps)["comptes"], {"entree_publiee_utilisee": 1})

    def test_provenance_en_scene_cibles_dates_et_recharge(self):
        from donjon.esprits import croire
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tache_promise_recours import reserve
        from tests.test_tensions import recharger
        m, acteur, cible, _ = reserve()
        m.data["minutes"] = 2
        localisation = d.lire(m, acteur)["croyances"][cible]["lieu"]
        lieu = localisation["valeur"]
        place = {k: localisation[k] for k in ("salle", "case")}
        croire(m, acteur, cible, "lieu", lieu, "entendu", **place)
        d.lire(m, acteur)["croyances"][cible]["lieu"]["minute"] = 1
        eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
        for ep in (eps[0], eps[2]):
            ep["decision"]["plan"] = [{"operation": "demander", "cible": cible}]
        avant = copy.deepcopy(m.data)
        eps[0]["debut_entrees"] = eps[0]["quitte_entrees"] = d.relever_entrees(m, acteur, 2)
        self.assertEqual(avant, m.data)
        for source, classe in (("entendu", "repetition_sans_entree_nouvelle"),
                              ("vu", "renouvellement_perceptif")):
            m.data["minutes"] = 2
            croire(m, acteur, cible, "lieu", lieu, source, **place)
            eps[2]["debut_entrees"] = d.relever_entrees(m, acteur, 2)
            self.assertEqual(self.analyser(eps)["comptes"], {classe: 1})
            etat, vue = copy.deepcopy(m.data), (regarder(m), scene_percue(m))
            m = recharger(m)
            self.assertEqual(etat, m.data)
            self.assertEqual(vue, (regarder(m), scene_percue(m)))
            eps[2]["debut_entrees"] = d.relever_entrees(m, acteur, 2)
            self.assertEqual(self.analyser(eps)["comptes"], {classe: 1})
        # Une source changée sur un autre objet n'est pas une cible du plan.
        eps[0]["quitte_entrees"] = eps[2]["debut_entrees"]
        croire(m, acteur, "garde_manger", "verrouillee", False, "vu")
        eps[2]["debut_entrees"] = d.relever_entrees(m, acteur, 2)
        self.assertEqual(self.analyser(eps)["total_non_justifies"], 1)

    def test_objet_percu_deplace_sans_revision_de_croyance_et_recharge(self):
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tache_promise_recours import reserve
        from tests.test_tensions import placer, recharger
        m, acteur, _, _ = reserve()
        m.data["minutes"] = 2
        eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
        avant = d.relever_entrees(m, acteur, 2)
        self.assertIn("lanterne_couloir", avant["_details"]["perception"])
        eps[0]["debut_entrees"] = eps[0]["quitte_entrees"] = avant
        placer(m, "lanterne_couloir", "cellier", [3, 2])
        etat, vue = copy.deepcopy(m.data), (regarder(m), scene_percue(m))
        eps[2]["debut_entrees"] = d.relever_entrees(m, acteur, 2)
        self.assertEqual(etat, m.data)
        self.assertEqual(self.analyser(eps)["comptes"], {"renouvellement_perceptif": 1})
        self.assertIn("lanterne_couloir", self.analyser(eps)["allers_retours"][0]["perception_diff_qr"]["perception"])
        m = recharger(m)
        self.assertEqual(etat, m.data)
        self.assertEqual(vue, (regarder(m), scene_percue(m)))
        self.assertEqual(eps[2]["debut_entrees"], d.relever_entrees(m, acteur, 2))

    def test_aubin_relais_2024_perception_nommee_et_recharge(self):
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tensions import recharger
        # Le moteur corrigé ne clôt plus ce parent sur un moyen manqué.
        # La sonde doit néanmoins savoir relire ce retour réellement observé
        # sur l'intégration : états et épisodes bruts, aucun classement figé.
        fichier = Path(__file__).parent / "data/sonde-276-aubin-relais-2024.json.gz"
        charge = json.loads(gzip.decompress(fichier.read_bytes()))
        captures = {int(t): Monde(etat) for t, etat in charge["captures"].items()}
        sonde = d.SondeAvis()
        sonde.episodes = copy.deepcopy(charge["episodes"])
        # JSON conserve les coordonnées mais pas les tuples de l'API percus.
        # Restaurer leur type sur toute la trace, sans recalculer les lectures.
        for eps in sonde.episodes.values():
            for ep in eps:
                for champ in ("debut_entrees", "quitte_entrees"):
                    entrees = ep.get(champ)
                    if entrees and "perception" in entrees["_details"]:
                        entrees["_details"]["perception"] = {
                            id: tuple(place) for id, place in entrees["_details"]["perception"].items()}
        retour = next(r for r in sonde.analyser()["allers_retours"]
                      if r["id"] == "aubin" and r["retour_t"] == 117518)
        self.assertEqual(retour["classe"], "renouvellement_perceptif")
        self.assertFalse(retour["non_justifie"])
        self.assertEqual(retour["perception_diff_qr"]["provenance"]["ilse.lieu"], ["entendu", "vu"])
        self.assertIsNone(retour["perception_diff_qr"]["perception"]["ilse"][0])
        self.assertIsNotNone(retour["perception_diff_qr"]["perception"]["ilse"][1])
        self.assertEqual(set(captures), {117503, 117518})
        releves = []
        for t, m in sorted(captures.items()):
            etat, vue = copy.deepcopy(m.data), (regarder(m), scene_percue(m))
            entrees_avant = d.relever_entrees(m, "aubin", m.data["minutes"])
            m = recharger(m)
            self.assertEqual(etat, m.data)
            self.assertEqual(vue, (regarder(m), scene_percue(m)))
            entrees_apres = d.relever_entrees(m, "aubin", m.data["minutes"])
            self.assertEqual(entrees_avant, entrees_apres)
            releves.append(entrees_apres)
        self.assertEqual(d._diff_perception(*releves, {"ilse"}), retour["perception_diff_qr"])

    def test_entrees_publiees_exigent_un_lien_avec_le_plan_admissible(self):
        for nature in ("portes", "possedes", "lieu", "engagement"):
            eps = [episode("agenda", 0, 1), episode("garder", 1, 2), episode("agenda", 2, 3)]
            for e in eps:
                for cle in ("debut_entrees", "quitte_entrees"):
                    e[cle]["_details"].update(inventaire={"portes": [], "possedes": []},
                                             social={"charges": [], "engagements_tenus": []})
            q, r = eps[0]["quitte_entrees"], eps[2]["debut_entrees"]
            if nature in ("portes", "possedes"):
                r["_details"]["inventaire"][nature] = ["bien"]
                r["inventaire_et_droits"] = 1
            elif nature == "lieu":
                q["_details"]["croyances"]["bien.lieu"] = '"ailleurs"'
                r["_details"]["croyances"]["bien.lieu"] = '"salle"'
                r["croyances_valeurs"] = 1
            else:
                c = {"objet": "bien", "allume": True}
                q["_details"]["social"]["charges"] = [["payeur", c, False]]
                r["_details"]["social"]["engagements_tenus"] = [
                    {"type": "engagement_tenu", "pour": "payeur", "condition": c, "minute": 2}]
                r["social_et_engagements"] = 1
            eps[2]["moyen_admissible"] = True
            # Référence imbriquée d'une contrepartie, et pas seulement tête du plan.
            eps[2]["decision"]["plan"] = [{"operation": "aller", "lieu": "salle"},
                {"operation": "proposer", "cible": "client", "contenu": {
                    "contrepartie": {"type": "objet", "objet": "bien"}}}]
            with self.subTest(nature=nature):
                a = self.analyser(eps)
                self.assertEqual(a["comptes"], {"entree_publiee_utilisee": 1})
                self.assertEqual(a["total_justifies"], 1)
                n = {"scenario": "scene", "graine": 0, "heures": 1, "donnees": {"mesures": {}}}
                audit.ajouter_avis(n, a)
                self.assertEqual(n["donnees"]["mesures"]["avis_classe_entree_publiee_utilisee"], 1)
                self.assertNotIn("avis_a_expliquer", {c["code"] for c in audit.analyser_nuit(n)})
                eps[2]["moyen_admissible"] = False
                self.assertEqual(self.analyser(eps)["total_justifies"], 0)
                eps[2]["moyen_admissible"] = True
                eps[2]["decision"]["plan"][1]["contenu"]["contrepartie"]["objet"] = "sans_rapport"
                self.assertEqual(self.analyser(eps)["total_justifies"], 0)
                # Les mots de la grammaire ne sont pas des références.
                eps[2]["decision"]["plan"] = [{"operation": "bien", "type": "bien"}]
                self.assertEqual(self.analyser(eps)["total_justifies"], 0)

    def test_engagement_retire_ou_ancien_ne_prouve_pas_un_accomplissement(self):
        eps = [episode("agenda", 0, 1), episode("garder", 1, 2), episode("agenda", 2, 3)]
        c = {"objet": "bien", "allume": True}
        q, r = eps[0]["quitte_entrees"], eps[2]["debut_entrees"]
        q["_details"]["social"] = {"charges": [["payeur", c, False]]}
        r["_details"]["social"] = {"charges": []}
        r["social_et_engagements"] = 1
        eps[2]["moyen_admissible"] = True
        eps[2]["decision"]["plan"] = [{"operation": "allumer", "cible": "bien"}]
        for recu in (None, {"type": "engagement_abandonne", "pour": "payeur", "condition": c, "minute": 2},
                     {"type": "engagement_tenu", "pour": "payeur", "condition": c, "minute": 0}):
            # Seul le reçu typé tenu entre dans le relevé de la sonde.
            r["_details"]["social"]["engagements_tenus"] = [recu] if recu and recu["type"] == "engagement_tenu" else []
            self.assertEqual(self.analyser(eps)["total_justifies"], 0)
        r["_details"]["social"]["engagements_tenus"][0]["minute"] = 2
        q["_details"]["social"]["charges"][0][2] = True
        self.assertEqual(self.analyser(eps)["total_justifies"], 0)
        q["_details"]["social"]["charges"][0][2] = False
        r["_details"]["social"]["charges"] = [["payeur", c, True]]
        self.assertEqual(self.analyser(eps)["total_justifies"], 0)

    def test_reveils_brune_reels_et_recharges(self):
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tensions import recharger
        # Le lot 303 prépare le contact des participants de lieu inconnu :
        # la nuit actuelle ne contient plus le retour historique à 929.
        # Relire les états et épisodes réels, sans figer leur classement.
        fichier = Path(__file__).parent / "data/sonde-271-brune-hameau-2024.json.gz"
        charge = json.loads(gzip.decompress(fichier.read_bytes()))
        sonde = d.SondeAvis()
        sonde.episodes = charge["episodes"]
        # Restaurer les tuples de l'API percus, comme pour la capture 276.
        for eps in sonde.episodes.values():
            for ep in eps:
                for champ in ("debut_entrees", "quitte_entrees"):
                    entrees = ep.get(champ)
                    if entrees and "perception" in entrees["_details"]:
                        entrees["_details"]["perception"] = {
                            id: tuple(place) for id, place in entrees["_details"]["perception"].items()}
        retours = {r["retour_t"]: r for r in sonde.analyser()["allers_retours"]
                   if r["id"] == "brune" and r["d1_but"].get("type") == "agenda"}
        for t, preuve in ((591, "possession_nouvelle"), (929, "lieu_cru_change")):
            self.assertEqual(retours[t]["classe"], "entree_publiee_utilisee")
            self.assertIn(preuve, {p["preuve"] for p in retours[t]["preuves"]})
        self.assertEqual(set(charge["captures"]), {"591", "929"})
        for t, etat in charge["captures"].items():
            with self.subTest(t=t):
                m = Monde(etat)
                vue, etat = (regarder(m), scene_percue(m)), copy.deepcopy(m.data)
                entrees = d.relever_entrees(m, "brune", m.data["minutes"])
                ep = next(e for e in sonde.episodes["brune"] if e["debut_t"] == int(t))
                self.assertEqual(d._canon(entrees), d._canon(ep["debut_entrees"]))
                m = recharger(m)
                self.assertEqual(etat, m.data)
                self.assertEqual(vue, (regarder(m), scene_percue(m)))
                self.assertEqual(entrees, d.relever_entrees(m, "brune", m.data["minutes"]))

    def test_sonde_ne_change_pas_nuit_hameau_et_recharge(self):
        from donjon import banc_pnj, planification
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tensions import recharger
        resultats = []
        for observer in (nullcontext, d.observer_avis):
            capture = {}
            creer = banc_pnj.creer
            def capturer(*a, **k):
                capture["monde"] = creer(*a, **k)
                return capture["monde"]
            planification._IMPOSSIBLES.clear()
            with patch.object(banc_pnj, "creer", capturer), observer() as sonde:
                _, mesures, donnees = banc_pnj.nuit("crue_hameau", 2024, 2/60,
                                                   "chambre_cloche", depart="tire")
            m = capture["monde"]
            vue, etat = (regarder(m), scene_percue(m)), copy.deepcopy(m.data)
            m = recharger(m)
            self.assertEqual(etat, m.data)
            self.assertEqual(vue, (regarder(m), scene_percue(m)))
            resultats.append((m.data, vue, mesures, donnees["chronique"]))
        self.assertEqual(*resultats)

    def test_cloture_et_contre_epreuves_en_scene_rechargee(self):
        from donjon import agendas
        from donjon.esprits import croire
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tache_promise_recours import reserve
        from tests.test_tensions import recharger
        for cas, classe in (("tenu", "entree_publiee_utilisee"),
                            ("retire", "entree_nouvelle_a_expliquer"),
                            ("sans_rapport", "entree_nouvelle_a_expliquer"),
                            ("sans_entree", "repetition_sans_entree_nouvelle")):
            initial, artisan, payeur, c = reserve()
            initial.objets[c["objet"]]["ouverte"] = False
            resultats = []
            for observer in (nullcontext, d.observer_avis):
                m = recharger(initial.copier())
                engagement = {"condition": c, "pour": payeur, "minute": 0}
                agendas.prendre(m, artisan, engagement)
                eps = [episode("agenda", 0, 1), episode("autre", 1, 2), episode("agenda", 2, 3)]
                eps[0]["debut_entrees"] = d.relever_entrees(m, artisan, 0)
                m.data["minutes"] = 1
                croire(m, artisan, payeur, "etat", {"occupe": True}, "vu")
                eps[0]["quitte_entrees"] = d.relever_entrees(m, artisan, 1)
                with observer():
                    m.data["minutes"] = 2
                    if cas == "tenu":
                        self.assertTrue(d.pnj._executer(m, artisan, {"operation": "verrouiller",
                            "cible": c["objet"], "outil": "cle_garde_manger",
                            "lieu": "", "condition": ""}, [], None))
                        agendas.echoir(m, artisan)
                        self.assertTrue(m.objets[c["objet"]]["verrouillee"])
                    elif cas == "retire":
                        agendas.retirer_proposition(m, artisan, engagement)
                    elif cas == "sans_rapport":
                        croire(m, artisan, payeur, "lieu", "dortoir", "vu", salle="dortoir", case=None)
                eps[2]["debut_entrees"] = d.relever_entrees(m, artisan, 2)
                eps[2]["decision"]["plan"] = [{"operation": "deverrouiller", "cible": c["objet"],
                                                "outil": "cle_garde_manger"}]
                eps[2]["moyen_admissible"] = True
                with self.subTest(cas=cas, sonde=observer is d.observer_avis):
                    self.assertEqual(self.analyser(eps)["comptes"], {classe: 1})
                    if cas == "tenu":
                        self.assertIn("engagement_accompli_publie", {
                            p["preuve"] for p in self.analyser(eps)["allers_retours"][0]["preuves"]})
                    etat, vue = copy.deepcopy(m.data), (regarder(m), scene_percue(m))
                    m = recharger(m)
                    self.assertEqual(etat, m.data)
                    self.assertEqual(vue, (regarder(m), scene_percue(m)))
                    resultats.append((m.data, vue))
            self.assertEqual(*resultats)

    def test_classes_causales_service(self):
        from types import SimpleNamespace
        for acteur, cause, parti, classe in (
                ("artisan", "geste", False, "prestataire_beneficiaire_present"),
                ("artisan", "geste", True, "prestataire_beneficiaire_parti"),
                ("payeur", "geste", False, "beneficiaire_ou_tiers"),
                ("tiers", "geste", False, "beneficiaire_ou_tiers"),
                (None, "physique", False, "cessation_physique"),
                (None, None, False, "cause_non_observee")):
            for champ in ("allume", "verrouillee", "lieu"):
                with self.subTest(classe=classe, champ=champ):
                    sonde = d.SondeAvis()
                    valeur = "salle" if champ == "lieu" else True
                    monde = SimpleNamespace(objets={"bien": {champ: valeur}}, data={"minutes": 0})
                    service = {"payeur": "payeur", "prestataire": "artisan",
                               "condition": {"objet": "bien", champ: valeur},
                               "reussite_t": None, "perte_t": None}
                    sonde.services["s"] = service
                    sonde.relever_services(monde)
                    monde.objets["bien"][champ] = "ailleurs" if champ == "lieu" else False
                    sonde.relever_services(monde, acteur, cause, {id(service): {"parti": parti}})
                    resultat = sonde.analyser()
                    self.assertEqual(resultat["services_par_classe"][classe], 1)
                    self.assertEqual(service["violation"], classe == "prestataire_beneficiaire_present")
                    nuit = {"scenario": "synthese", "graine": 0, "heures": 1,
                            "donnees": {"mesures": {}}}
                    audit.ajouter_avis(nuit, resultat)
                    self.assertEqual(nuit["donnees"]["mesures"]["avis_service_" + classe], 1)
                    constat = next(c for c in audit.analyser_nuit(nuit)
                                   if c["code"] == "avis_service_" + classe)
                    self.assertEqual(constat["niveau"], "violation" if service["violation"] else "observation")

    def analyser(self, eps, **kw):
        return d.analyser_episodes({"pnj": eps}, **kw)

    def test_retour_sans_entree_et_details(self):
        a = self.analyser([episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        self.assertEqual(a["total_non_justifies"], 1)
        self.assertEqual(a["par_pnj"]["pnj"]["repetition_sans_entree_nouvelle"], 1)
        self.assertEqual(a["allers_retours"][0]["retour_minute"], 2)

    def test_autre_moyen_exige_echec_observe_et_evite_dans_tout_le_plan(self):
        for genre in ("lumiere", "chaleur"):
            rate = {"operation": "acheter", "cible": "vendeur", "lieu": ""}
            eps = [episode(genre, 0, 1), episode("garder", 1, 2), episode(genre, 2, 3)]
            eps[0]["faits"] = [{"t": 600, "preuve": "etape_manquee", "etape": rate}]
            eps[2]["decision"]["plan"] = [{"operation": "confier", "cible": "artisan"}]
            eps[2]["moyen_admissible"] = True
            self.assertEqual(self.analyser(eps)["comptes"], {"changement_moyen_admissible": 1})
            # Un détour avant le même obstacle reste suspect.
            eps[2]["decision"]["plan"].append(rate)
            self.assertEqual(self.analyser(eps)["total_non_justifies"], 1)
            eps[2]["decision"]["plan"].pop()
            eps[2]["moyen_admissible"] = False
            self.assertEqual(self.analyser(eps)["total_non_justifies"], 1)
            eps[2]["moyen_admissible"] = True
            eps[0]["faits"] = []
            self.assertEqual(self.analyser(eps)["total_non_justifies"], 1)

    def test_rendez_vous_publie_et_recharge(self):
        from donjon import appel
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_tache_promise_recours import reserve
        from tests.test_tensions import recharger
        for retrouvailles in (False, True):
            initial, artisan, payeur, _ = reserve()
            initial = recharger(initial)
            resultats = []
            for observer in (nullcontext, d.observer_avis):
                m = recharger(initial.copier())
                d.lire(m, artisan)["rejoint"] = {"qui": payeur, "jusqu_a": 20, "vient": True}
                eps = [episode("lumiere", 0, 1), episode("attendre", 1, 2), episode("lumiere", 2, 3)]
                eps[1]["decision"] = d._resume_decision({"but": {"type": "attendre", "qui": payeur}})
                eps[2]["decision"]["plan"] = [{"operation": "engager", "cible": payeur}]
                with observer() as sonde:
                    if sonde:
                        sonde.episodes[artisan] = eps[:2]
                        sonde.relever_services(m)
                    m.data["minutes"] = 1
                    if retrouvailles:
                        appel.retrouves(m, artisan, payeur)
                    else:
                        # Expiration/rupture sans contact : l'absence ne prouve rien.
                        d.lire(m, artisan)["rejoint"] = None
                    if sonde:
                        sonde.episodes[artisan].append(eps[2])
                        a = sonde.analyser()
                        self.assertEqual(a["total_non_justifies"], 0 if retrouvailles else 1)
                        if retrouvailles:
                            self.assertEqual(a["comptes"], {"rendez_vous_intermediaire_accompli": 1})
                            eps[2]["decision"]["plan"][0]["cible"] = "autre"
                            self.assertEqual(sonde.analyser()["total_non_justifies"], 1)
                vue = regarder(m), scene_percue(m)
                avant = copy.deepcopy(m.data)
                m = recharger(m)
                self.assertEqual(avant, m.data)
                self.assertEqual(vue, (regarder(m), scene_percue(m)))
                resultats.append((m.data, *vue))
            self.assertEqual(*resultats)

    def test_cloture_service_publiee_puis_reunion_et_perte_rechargees(self):
        from donjon import biens
        from donjon.esprits import croire
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from tests.test_service_non_defait import serrure
        from tests.test_tensions import recharger
        initial, artisan, payeur, c = serrure()
        resultats = []
        for observer in (nullcontext, d.observer_avis):
            m = recharger(initial.copier())
            with observer() as sonde:
                if sonde:
                    sonde.services["s"] = {"prestataire": artisan, "payeur": payeur,
                        "condition": c, "reussite_t": None, "perte_t": None}
                    sonde.relever_services(m)
                croire(m, artisan, payeur, "lieu", "dortoir", "vu", salle="dortoir", case=None)
                copie = m.copier()
                with biens.clotures_services_du_choix(copie):
                    biens.services_proteges(copie, artisan)
                with self.assertRaises(RuntimeError):
                    with biens.clotures_services_du_choix(m):
                        biens.services_proteges(m, artisan)
                        raise RuntimeError("choix interrompu")
                if sonde:
                    self.assertNotIn("cloture", sonde.services["s"])
                with biens.clotures_services_du_choix(m):
                    self.assertNotIn(c, biens.services_proteges(m, artisan))
                if sonde:
                    self.assertTrue(sonde.services["s"]["cloture"]["presence"]["parti"])
                # Le bénéficiaire revient : la clôture publiée reste acquise.
                salle = m.objets[artisan]["lieu"]
                croire(m, artisan, payeur, "lieu", salle, "vu", salle=salle, case=None)
                m = recharger(m)
                m.data["minutes"] += 1
                self.assertTrue(d.pnj._executer(m, artisan, {"operation": "deverrouiller",
                    "cible": "garde_manger", "outil": "cle_garde_manger", "lieu": "", "condition": ""}, [], None))
                if sonde:
                    perte, = sonde.analyser()["services_etat_perdu"]
                    self.assertEqual(perte["classe"], "service_clos_avant_perte")
                    self.assertFalse(perte["violation"])
            vue = regarder(m), scene_percue(m)
            avant = copy.deepcopy(m.data)
            m = recharger(m)
            self.assertEqual(avant, m.data)
            self.assertEqual(vue, (regarder(m), scene_percue(m)))
            resultats.append((m.data, *vue))
        self.assertEqual(*resultats)

    def test_cycle_accompli_conserve_sa_preuve(self):
        a = self.analyser([episode("pulsion", 0, 1, accompli=True), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        self.assertEqual(a["total_cycles_accomplis"], 1)
        self.assertFalse(a["allers_retours"][0]["non_justifie"])

    def test_fin_intermediaire_seule_ne_prouve_pas_un_progres(self):
        for but in ("garder", "autre"):
            a = self.analyser([episode(but, 0, 1), episode("pulsion", 1, 2, accompli=True), episode(but, 2, 3)])
            self.assertEqual(a["comptes"], {"entree_nouvelle_a_expliquer": 1})

    def test_entree_changee_ne_certifie_pas_une_raison(self):
        eps = [episode("pulsion", 0, 1), episode("garder", 1, 2, 1), episode("pulsion", 2, 3, 2)]
        eps[0]["quitte_entrees"] = entrees(1)
        a = self.analyser(eps)
        self.assertEqual(a["total_a_expliquer"], 1)
        self.assertEqual(a["total_justifies"], 0)
        self.assertFalse(a["certification_complete"])
        n = {"scenario": "relais", "graine": 7, "heures": 1}
        audit.ajouter_avis(n, a)
        self.assertIn("avis_a_expliquer", {c["code"] for c in audit.analyser_nuit(n)})

    def test_horizon_et_deplacement(self):
        eps = [episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 62, 63)]
        self.assertEqual(self.analyser(eps)["total_non_justifies"], 0)
        eps[-1]["debut_t"] = 2 * 600
        eps[-1]["debut_entrees"]["lieu"] = "ailleurs"
        a = self.analyser(eps)
        self.assertEqual(a["comptes"], {"repetition_sans_entree_nouvelle": 1})

    def test_restauration_apres_exception(self):
        from donjon import perception
        choisir = d.deliberation.choisir
        executer, combustion = d.pnj._executer, perception.avancer_combustion
        with self.assertRaises(RuntimeError):
            with d.observer_avis():
                raise RuntimeError("essai")
        self.assertIs(d.deliberation.choisir, choisir)
        self.assertIs(d.pnj._executer, executer)
        self.assertIs(perception.avancer_combustion, combustion)

    def test_paliers_observes_stricts_et_regle_unique(self):
        for palier, attendu in ((12, "preemption_palier_superieur"),
                                (13, "repetition_sans_entree_nouvelle"),
                                (14, "repetition_sans_entree_nouvelle")):
            eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
            eps[0]["palier"], eps[1]["palier"] = 13, palier
            eps[1]["faits"] = [{"cle": eps[0]["decision"]["cle"], "t": 900,
                                "autrui": True, "progression": True}]
            # La préemption prime ; sinon la satisfaction observée prime sur le progrès.
            if palier == 12:
                self.assertEqual(self.analyser(eps)["comptes"], {attendu: 1})
            else:
                self.assertEqual(self.analyser(eps)["comptes"], {"satisfaction_ou_dementi_autrui": 1})
                eps[1]["faits"] = []
                self.assertEqual(self.analyser(eps)["comptes"], {attendu: 1})

    def test_progression_avec_preuve_et_derive_separee(self):
        eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
        eps[1]["faits"] = [{"cle": eps[0]["decision"]["cle"], "t": 900,
                            "progression": True, "preuve": "etape_executee"}]
        self.assertEqual(self.analyser(eps)["comptes"], {"progression_reelle": 1})
        self.assertEqual(self.analyser(eps)["total_derives_ouvertes"], 0)
        a = self.analyser([episode("a", 0, 1), episode("b", 1, 2), episode("c", 2, 3)])
        self.assertEqual(a["total_derives_ouvertes"], 1)
        self.assertEqual(a["total_non_justifies"], 0)

    def test_sonde_attribue_une_fin_survenue_pendant_action_autrui(self):
        sonde = d.SondeAvis()
        eps = [episode("a", 0, 1), episode("b", 1, 2), episode("a", 2, 3)]
        sonde.episodes["aidant"] = eps[:2]
        cle = eps[0]["decision"]["cle"]
        from types import SimpleNamespace
        monde = SimpleNamespace(data={"minutes": 1})
        with patch.object(d, "instant", return_value=900), \
             patch.object(d, "_est_accompli", return_value=False):
            avant = sonde.accomplissements(monde)
        with patch.object(d, "instant", return_value=900), \
             patch.object(d, "_est_accompli", side_effect=lambda m, qui, dec, minute: dec["cle"] == cle):
            sonde.constater(monde, "tiers", avant)
        sonde.episodes["aidant"].append(eps[2])
        a = sonde.analyser()
        self.assertEqual(a["comptes"], {"satisfaction_ou_dementi_autrui": 1})
        self.assertEqual(a["allers_retours"][0]["preuves"][0]["acteur"], "tiers")

    def test_etat_paye_perdu_sans_duree_ne_viole_pas_un_contrat(self):
        from types import SimpleNamespace
        sonde = d.SondeAvis()
        sonde.episodes["payeur"] = []
        souvenir = {"type": "tache_payee", "a": "artisan", "minute": 0,
                    "condition": {"objet": "bien", "verrouillee": True}, "prix": 2}
        monde = SimpleNamespace(objets={"bien": {"verrouillee": False}}, data={"minutes": 0})
        with patch.object(d, "lire", return_value={"memoire": [souvenir]}), patch.object(d, "instant", return_value=600):
            sonde.relever_services(monde)
            monde.objets["bien"]["verrouillee"] = True
            sonde.relever_services(monde)
            souvenir.clear()  # Le souvenir borné disparaît, l'observation demeure.
            monde.objets["bien"]["verrouillee"] = False
            sonde.relever_services(monde)
        a = sonde.analyser()
        self.assertEqual(a["total_services_etat_perdu"], 1)
        self.assertFalse(a["services_etat_perdu"][0]["violation"])
        self.assertEqual(a["total_non_justifies"], 0)
        nuit = {"scenario": "synthese", "graine": 0, "heures": 1}
        audit.ajouter_avis(nuit, a)
        constats = audit.analyser_nuit(nuit)
        self.assertEqual([c["niveau"] for c in constats], ["observation"])
        a["services_etat_perdu"][0]["classe"] = "etat_paye_perdu_apres_reussite_duree_non_specifiee"
        self.assertEqual(audit.analyser_nuit(nuit)[0]["code"], "avis_service_cause_non_observee")

    def test_torche_hameau_1985_service_perdu(self):
        nuit = d.jouer_nuit_sondee("crue_hameau", 1985, heures=9/60, verifier_empreinte=True)
        pertes = [s for s in nuit["analyse"]["services_etat_perdu"] if s["prestataire"] == "brune"]
        # Depuis 225 ce court départ ne produit plus la perte historique.
        self.assertEqual(pertes, [])
        self.assertTrue(all(s["reussite_t"] < s["perte_t"] < 9 * d.MINUTE for s in pertes))
        self.assertTrue(all(not s["violation"] for s in pertes))

    def test_torche_historique_217_rechargee(self):
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        with gzip.open(Path(__file__).parent / "fixtures/changements_avis/service-217.json.gz", "rt", encoding="utf8") as f:
            capture = json.load(f)
        sonde = d.SondeAvis()
        # Le paiement observé appartient au fil d'audit, même si le souvenir
        # a déjà disparu des deux captures de fin de service.
        contrat = copy.deepcopy(capture["services"][0])
        contrat.update(reussite_t=None, perte_t=None)
        sonde.services["contrat_capture"] = contrat
        for phase in ("reussite", "perte"):
            monde = Monde(copy.deepcopy(capture["etats"][phase]))
            with tempfile.TemporaryDirectory() as dossier:
                chemin = Path(dossier) / "monde.json"
                monde.sauver(chemin)
                recharge = Monde.charger(chemin)
            self.assertEqual(monde.data, recharge.data)
            self.assertEqual(regarder(monde), regarder(recharge))
            self.assertEqual(scene_percue(monde), scene_percue(recharge))
            sonde.relever_services(recharge)
        pertes = sonde.analyser()["services_etat_perdu"]
        self.assertEqual(len(pertes), 1)
        self.assertEqual(pertes[0]["reussite_t"], capture["services"][0]["reussite_t"])
        self.assertEqual(pertes[0]["perte_t"], capture["services"][0]["perte_t"])
        self.assertLess(pertes[0]["reussite_t"], pertes[0]["perte_t"])
        self.assertEqual(pertes[0]["reussite_t"] // d.MINUTE, 7)
        self.assertEqual(pertes[0]["perte_t"] // d.MINUTE, 8)
        self.assertFalse(pertes[0]["violation"])
        self.assertEqual(pertes[0]["classe"], "cause_non_observee")

    def test_transition_reelle_et_physique_apres_recharge(self):
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        from donjon import perception
        with gzip.open(Path(__file__).parent / "fixtures/changements_avis/service-217.json.gz",
                       "rt", encoding="utf8") as f:
            capture = json.load(f)
        for physique in (False, True):
            resultats = []
            for observer in (nullcontext, d.observer_avis):
                monde = Monde(copy.deepcopy(capture["etats"]["reussite"]))
                with tempfile.TemporaryDirectory() as dossier:
                    chemin = Path(dossier) / "monde.json"
                    monde.sauver(chemin)
                    monde = Monde.charger(chemin)
                    with observer() as sonde:
                        if sonde:
                            service = copy.deepcopy(capture["services"][0])
                            service.update(reussite_t=None, perte_t=None)
                            sonde.services["capture"] = service
                        if physique:
                            perception.avancer_combustion(monde, 1000, [])
                        else:
                            fait = d.pnj._executer(monde=monde, id="brune", etape={
                                "operation": "eteindre", "cible": "torche", "outil": "",
                                "lieu": "", "condition": ""}, lignes=[], gestes=None)
                            self.assertTrue(fait)
                    if sonde:
                        pertes = sonde.analyser()["services_etat_perdu"]
                        self.assertEqual(len(pertes), 1)
                        self.assertEqual(pertes[0]["classe"], "cessation_physique" if physique
                                         else "prestataire_beneficiaire_present")
                    monde.sauver(chemin)
                    monde = Monde.charger(chemin)
                    resultats.append((monde.data, regarder(monde), scene_percue(monde)))
            self.assertEqual(resultats[0], resultats[1])

    def test_alerte_et_archive_sans_mesure(self):
        n = {"scenario": "relais", "graine": 7, "heures": 1, "donnees": {"chronique": [], "mesures": {}}}
        self.assertIn("avis_non_mesures", {c["code"] for c in audit.analyser_nuit(n)})
        a = self.analyser([episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        audit.ajouter_avis(n, a)
        self.assertEqual(n["donnees"]["mesures"]["avis_non_justifies"], 1)
        self.assertNotIn("avis_services_etat_perdu", n["donnees"]["mesures"])
        self.assertIn("avis_non_justifie", {c["code"] for c in audit.analyser_nuit(n)})

    def test_autre_etat_serrure_monde_et_rendu_recharges(self):
        from tests.test_service_non_defait import serrure
        from tests.test_tensions import recharger
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        initial, artisan, payeur, condition = serrure()
        resultats = []
        for observer in (nullcontext, d.observer_avis):
            monde = recharger(initial.copier())
            with observer() as sonde:
                if sonde:
                    sonde.services["serrure"] = {
                        "prestataire": artisan, "payeur": payeur, "condition": condition,
                        "reussite_t": None, "perte_t": None}
                self.assertTrue(d.pnj._executer(monde, artisan, {
                    "operation": "deverrouiller", "cible": "garde_manger",
                    "outil": "cle_garde_manger", "lieu": "", "condition": ""}, [], None))
            if sonde:
                perte, = sonde.analyser()["services_etat_perdu"]
                self.assertEqual(perte["classe"], "prestataire_beneficiaire_present")
            monde = recharger(monde)
            self.assertFalse(monde.objets["garde_manger"]["verrouillee"])
            resultats.append((monde.data, regarder(monde), scene_percue(monde)))
        self.assertEqual(resultats[0], resultats[1])

    def test_position_perdue_pendant_marche_hors_executeur(self):
        from tests.test_tache_promise_recours import reserve
        from tests.test_tensions import recharger
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        initial, artisan, payeur, _ = reserve()
        d.lire(initial, artisan)["intention"] = {
            "but": {"type": "pulsion", "objet": artisan, "lieu": "cuisine"},
            "motif": "devoir", "depuis": initial.data["minutes"], "attente": 0,
            "plan": [{"operation": "aller", "lieu": "cuisine", "cible": "",
                      "outil": "", "condition": ""}]}
        resultats = []
        for observer in (nullcontext, d.observer_avis):
            monde = recharger(initial.copier())
            with observer() as sonde:
                if sonde:
                    sonde.services["position"] = {"prestataire": artisan, "payeur": payeur,
                        "condition": {"objet": artisan, "lieu": "cellier"},
                        "reussite_t": None, "perte_t": None}
                for _ in range(100):
                    d.pnj.agir(monde, artisan, d.instant(monde), [], [])
                    if monde.objets[artisan]["lieu"] != "cellier":
                        break
                self.assertNotEqual(monde.objets[artisan]["lieu"], "cellier")
            if sonde:
                perte, = sonde.analyser()["services_etat_perdu"]
                self.assertEqual(perte["classe"], "prestataire_beneficiaire_present")
            monde = recharger(monde)
            resultats.append((monde.data, regarder(monde), scene_percue(monde)))
        self.assertEqual(resultats[0], resultats[1])

    def test_captures_reelles(self):
        with gzip.open(Path(__file__).parent / "fixtures/changements_avis/episodes.json.gz", "rt", encoding="utf-8") as f:
            captures = json.load(f)
        for capture in captures:
            with self.subTest(capture=capture["nom"]):
                a = d.analyser_episodes(capture["episodes"])
                self.assertEqual(dict(Counter(r["classe_199"] for r in a["allers_retours"])), capture["comptes"])
                self.assertTrue(capture["chronique"])
                if capture["nom"] == "crue_hameau-1985-brune-123253":
                    suspect = next(r for r in a["allers_retours"] if r["retour_t"] == 123253)
                    self.assertTrue(suspect["non_justifie"])

    def test_comparateur_mesure_et_alerte(self):
        from tools import comparer_bancs as c
        config = {"empreintes": False, "heures": 5/60, "depart": "fixe",
                  "verifier": False, "joueurs": c.JOUEURS}
        n = c.jouer_nuit(("relais", 7, config))
        self.assertIsNone(n["plantage"])
        self.assertIn("avis_non_justifies", n["donnees"]["mesures"])
        self.assertIn("par_pnj", n["avis"])
        self.assertNotIn("avis_non_mesures", {x["code"] for x in n["constats"]})

    def test_comparateur_identite_conserve_les_alertes(self):
        from tools import comparer_bancs as c
        a = self.analyser([episode("pulsion", 0, 1), episode("garder", 1, 2), episode("pulsion", 2, 3)])
        detecteur = c.audit.detecteur_avis()
        config = {"empreintes": True, "heures": 1/60, "depart": "fixe",
                  "verifier": False, "joueurs": c.JOUEURS}
        with patch.object(detecteur, "analyser_episodes", return_value=a):
            n = c.jouer_nuit(("relais", 7, config))
        self.assertIn("avis_non_justifie", {x["code"] for x in n["constats"]})

    def test_audit_ecrit_une_nuit_mesuree(self):
        with tempfile.TemporaryDirectory() as dossier:
            resultat = audit.jouer_nuit(("relais", 7, 5/60, dossier, False, True, "fixe", False))
            with gzip.open(resultat[2], "rt", encoding="utf-8") as f:
                nuit = json.load(f)
        self.assertIsNone(nuit["plantage"])
        self.assertIn("avis_non_justifies", nuit["donnees"]["mesures"])
        self.assertNotIn("avis_non_mesures", {c["code"] for c in audit.analyser_nuit(nuit)})

    def test_monde_et_vue_joueur_identiques_apres_rechargement(self):
        from donjon import banc_pnj
        from donjon.monde import Monde
        from donjon.rendu import regarder
        for scenario in ("relais", "mine"):
            vues = []
            for observer in (nullcontext, d.observer_avis):
                capture = {}
                creer = banc_pnj.creer
                def capturer(*a, **k):
                    capture["monde"] = creer(*a, **k)
                    return capture["monde"]
                with patch.object(banc_pnj, "creer", capturer), observer():
                    banc_pnj.nuit(scenario, 7, 5/60, d.SALLES_JOUEUR[scenario], depart="fixe")
                with tempfile.TemporaryDirectory() as dossier:
                    chemin = Path(dossier) / "monde.json"
                    capture["monde"].sauver(chemin)
                    recharge = Monde.charger(chemin)
                vues.append((recharge.data, regarder(recharge)))
            with self.subTest(scenario=scenario):
                self.assertEqual(vues[0], vues[1])

    def test_identite_reelle_deux_scenarios(self):
        for scenario in ("relais", "mine"):
            with self.subTest(scenario=scenario):
                d.jouer_nuit_sondee(scenario, 7, heures=5/60, verifier_empreinte=True)
