"""Un constat du battant lie le choix, la recherche et l'exécution."""
import copy
import unittest

from donjon import deliberation, planification
from donjon.banc_pnj import creer
from donjon.esprits import constater, croire, lire
from donjon.monde import ErreurMonde
from donjon.portes import valider_fermeture
from donjon.rendu import decrire, regarder
from tests.test_garde_plan import gardien_servant
from tests.test_tensions import recharger, vivre


class BattantsBrisesTests(unittest.TestCase):
    def test_constats_coherents_acteurs_et_installations(self):
        for scenario, acteur, cible in (("relais", "marchand", "reserve"),
                                        ("mine", "mathe", "garde_manger"),
                                        ("relais", "joueur", "reserve")):
            for source in ("vu", "essai"):
                with self.subTest(scenario=scenario, source=source):
                    m = creer(scenario, 1985, "fixe")
                    o = m.objets[cible]
                    o.update(ouverte=True, verrouillee=False, integrite=0)
                    croire(m, acteur, cible, "verrouillee", True, "savoir")
                    constater(m, acteur, cible, source)
                    m = recharger(m)
                    c = lire(m, acteur)["croyances"][cible]
                    self.assertFalse(c["verrouillee"]["valeur"])
                    self.assertEqual(c["fin"]["valeur"], "detruit")
                    condition = {"objet": cible, "verrouillee": True}
                    self.assertTrue(deliberation.satisfaite(m, acteur, condition))
                    if acteur != "joueur":
                        self.assertIsNone(planification.planifier_pulsion(m, acteur, condition))
                    with self.assertRaises(ErreurMonde):
                        valider_fermeture(m, cible)
                    m.joueur.update(salle=o["lieu"], position=list(o["position"]))
                    texte = decrire(m, cible)
                    self.assertIn("brisé", texte)
                    self.assertNotIn("verrouillé", texte)
                    self.assertEqual(texte, decrire(recharger(m), cible))
                    self.assertEqual(m.data, recharger(m).data)

    def test_crue_2024_reelle_apres_destruction(self):
        from donjon.moteur import Moteur, proposition
        from tools.detecter_changements_avis import observer_avis, analyser_episodes
        from donjon.geometrie import position_entree
        # Nuit réelle de la base du lot 201 : stock historique d'avant les occasions
        # du lot 200, où Brune brise la réserve vers 45 min (avec le bois cessible
        # du lot 200, elle le vend au lieu de briser).
        from tests.scenarios_contractuels import creer as creer_contractuel
        m = creer_contractuel("crue", 2024)
        m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
        with observer_avis() as sonde:
            for _ in range(12):
                Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
                m = recharger(m)
        self.assertEqual(m.objets["reserve"]["integrite"], 0)
        c = lire(m, "marchand")["croyances"]["reserve"]
        self.assertEqual(c["fin"]["valeur"], "detruit")
        self.assertFalse(c["verrouillee"]["valeur"])
        a = analyser_episodes(sonde.episodes)
        retours = [x for x in a["allers_retours"] if x["id"] == "marchand"
                   and x["d1_but"] and x["d1_but"].get("objet") == "reserve"
                   and x["d1_but"].get("verrouillee")]
        self.assertEqual(retours, [])
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_essai_et_vue_meme_information_de_contenu(self):
        m = gardien_servant()
        m.objets["reserve"].update(ouverte=True, verrouillee=False)
        constater(m, "marchand", "reserve", "vu")
        avant = copy.deepcopy(lire(m, "marchand")["croyances"]["reserve"])
        constater(m, "marchand", "reserve", "essai")
        apres = lire(m, "marchand")["croyances"]["reserve"]
        self.assertEqual({k: v["valeur"] for k, v in avant.items()},
                         {k: v["valeur"] for k, v in apres.items()})
        constater(m, "marchand", "reserve", "vu")
        self.assertEqual(avant, lire(m, "marchand")["croyances"]["reserve"])

    def test_croyance_seule_invalide_les_entrees_et_les_gestes(self):
        m = gardien_servant()
        m.objets["reserve"].update(ouverte=True, verrouillee=False)
        constater(m, "marchand", "reserve", "vu")
        def entree():
            return planification._entrees_communes(planification.vue(m, "marchand"))
        avant = entree()
        croire(m, "marchand", "reserve", "fin", "detruit", "vu")
        self.assertNotEqual(avant, entree())
        v = planification.vue(m, "marchand")
        e = planification.depart(m, "marchand", v)
        gestes = list(planification.gestes(v, e, {"fermer": ("reserve",)}))
        self.assertFalse(any(x["operation"] in ("fermer", "verrouiller")
                             and x.get("cible") == "reserve" for g in gestes for x in g[2]))
        self.assertEqual(planification.retablir(v, e.apres(faits=[(("touche", "reserve"), True)]), []), [])
        self.assertGreater(m.objets["reserve"]["integrite"], 0)  # Aucun oracle physique.

    def test_essai_sans_vue_ne_revele_pas_le_contenu_ni_le_verrou_ferme(self):
        m = gardien_servant()
        from tests.test_tensions import placer
        placer(m, "marchand", "crypte", [2, 3])
        m.objets["reserve"].update(ouverte=True, verrouillee=False)
        croire(m, "marchand", "reserve", "etat", {"ouverte": True, "vide": False}, "vu")
        for o in m.objets.values():
            if o["lieu"] == "reserve":
                o["lieu"] = "antichambre"
        constater(m, "marchand", "reserve", "essai")
        self.assertFalse(lire(m, "marchand")["croyances"]["reserve"]["etat"]["valeur"]["vide"])
        croire(m, "marchand", "reserve", "etat", {"ouverte": True}, "essai")
        constater(m, "marchand", "reserve", "essai")
        self.assertNotIn("vide", lire(m, "marchand")["croyances"]["reserve"]["etat"]["valeur"])
        m.objets["reserve"].update(ouverte=False, verrouillee=True)
        croire(m, "marchand", "reserve", "verrouillee", True, "savoir")
        constater(m, "marchand", "reserve", "essai")
        self.assertTrue(lire(m, "marchand")["croyances"]["reserve"]["verrouillee"]["valeur"])

    def test_restauration_ne_referme_pas_le_battant_brise_par_le_plan(self):
        m = gardien_servant()
        v = planification.vue(m, "marchand")
        e = planification.depart(m, "marchand", v).apres(faits=[
            (("touche", "reserve"), True), (("ouvert", "reserve"), True),
            (("verrou", "reserve"), False), (("fin", "reserve"), "detruit")])
        self.assertEqual(planification.retablir(v, e, []), [])

    def test_propre_plan_jamais_auto_exclu(self):
        m = gardien_servant()
        condition = {"objet": "reserve", "verrouillee": True}
        e = lire(m, "marchand")
        e["besoins"]["biens"] = 99
        e["intention"] = {"motif": "biens", "but": {"type": "pulsion", **condition},
                          "plan": [{"operation": "verrouiller", "cible": "reserve"}]}
        self.assertFalse(deliberation.retabli_par_son_plan(m, "marchand", condition))
        e["intention"]["but"] = {"type": "manger", "objet": "vivres"}
        self.assertTrue(deliberation.retabli_par_son_plan(m, "marchand", condition))

    def test_brisee_et_fermee_laps_entier_decoupe_recharge(self):
        for brisee in (True, False):
            with self.subTest(brisee=brisee):
                m = gardien_servant()
                lire(m, "brune")["besoins"]["faim"] = 0
                m.objets["reserve"].update(ouverte=False, verrouillee=False,
                                            integrite=0 if brisee else 30)
                constater(m, "marchand", "reserve", "vu")
                croire(m, "marchand", "reserve", "verrouillee", False, "essai")
                bloc, _ = vivre(recharger(m), 4)
                morceaux = recharger(m)
                for _ in range(4):
                    morceaux, _ = vivre(morceaux, 1)
                self.assertEqual(bloc.data, morceaux.data)
                self.assertEqual(bloc.data, recharger(bloc).data)
                self.assertEqual(regarder(bloc), regarder(recharger(bloc)))
                if brisee:
                    self.assertFalse(bloc.objets["reserve"]["verrouillee"])
                    self.assertFalse(any(c["pnj"] == "marchand" and " ferme " in c["texte"]
                                         for c in bloc.data.get("chronique", [])))
                else:
                    self.assertTrue(bloc.objets["reserve"]["verrouillee"])
