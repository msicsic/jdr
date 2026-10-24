"""Même marché PNJ/joueur, depuis le plan jusqu'à la sauvegarde et au récit perçu."""
import unittest
from unittest.mock import patch

from donjon import agendas, planification as p, relations
from donjon.banc_pnj import creer
from donjon.deliberation import retenir_refus
from donjon.echanges import executer, annoncer_abandon
from donjon.esprits import lire, percevoir_tous, croire
from donjon.pnj_propositions import gestes
from donjon.spatial import porte_par
from tests.support import calme, regarder, presentes
from tests.test_tensions import placer, recharger, vivre


def scene(scenario="crue", confiance=70, honnetete=90):
    a, b = ("brune", "marchand") if scenario == "crue" else ("odon", "mathe")
    m = presentes(creer(scenario, 42, "fixe"))
    calme(m, *[x for x, o in m.objets.items() if o.get("profil")])
    s = "antichambre" if scenario == "crue" else "baraquement"
    placer(m, a, s, [1, 4])
    placer(m, b, s, [2, 4])
    m.joueur.update(salle=s, position=[1, 3])
    regarder(m, a, b)
    regarder(m, b, a)
    regarder(m, "joueur", b)
    m.objets["vivres"].update(lieu=b, portions=8)
    m.objets[a]["profil"]["valeurs"]["honnetete"] = honnetete
    lire(m, a)["besoins"]["faim"] = 85
    lire(m, b)["relations"][a] = relations._nouvelle({"confiance": confiance})
    if scenario == "crue":
        m.objets["bois"].update(lieu=a, proprietaire=a)
        m.objets["lanterne"].update(lieu=a, proprietaire=a, allume=True, combustible=60)
        m.objets["brasero"].update(lieu=s, position=[2, 5], position_salle=s, allume=False, combustible=0)
    else:
        m.data["finances_pnj"][a] = 8
    percevoir_tous(m)
    m.data["connus"] = list(m.objets)
    return recharger(m), a, b


def offres(m, a):
    v = p.Vue(m, a)
    v.motif = "faim"
    return list(gestes(v, p.depart(m, a, v), {}, p.a_mange))


def offre(m, a, b, type):
    return next(x[2][0] for x in offres(m, a) if x[2][0]["cible"] == b
                and x[2][0]["contenu"]["demande"] == {"type": "part", "objet": "vivres"}
                and x[2][0]["contenu"]["contrepartie"]["type"] == type)


class PnjProposentTests(unittest.TestCase):
    def test_offres_meme_laps_decoupe_avec_rechargement(self):
        from donjon.temps import MINUTE
        from tests.test_corps_blessable import passer
        from donjon.rendu import decrire_perception
        for scenario in ("crue", "mine"):
            m, a, b = scene(scenario)
            retenir_refus(m, a, b, "demander", "refus", objet="vivres")
            retenir_refus(m, a, b, "acheter", "refus", objet="vivres")
            bloc, decoupe = recharger(m), recharger(m)
            with patch.object(type(m), "d20", return_value=20):
                passer(bloc, 5 * MINUTE)
                for dt in (15, 85, 500, 4 * MINUTE):
                    passer(decoupe, dt)
                    decoupe = recharger(decoupe)
            self.assertEqual(bloc.data, decoupe.data)
            self.assertEqual(decrire_perception(bloc), decrire_perception(decoupe))

    def test_geste_atomique_retire_du_vrai_plan_deux_scenarios(self):
        from donjon.pnj import agir
        from donjon.temps import instant
        for scenario in ("crue", "mine"):
            m, a, b = scene(scenario)
            etape = offre(m, a, b, "tache" if scenario == "crue" else "pieces")
            etape.pop("suppose", None)
            e = lire(m, a)
            e["intention"] = {"but": {"type": "part", "objet": "vivres", "de": b},
                              "motif": "faim", "plan": [etape], "depuis": m.data["minutes"], "attente": 0}
            intention, plan = e["intention"], e["intention"]["plan"]
            lignes = []
            with patch.object(type(m), "d20", return_value=20):
                agir(m, a, instant(m), lignes)
            self.assertIs(lire(m, a), e)
            self.assertIs(lire(m, a)["intention"], intention)
            self.assertIs(lire(m, a)["intention"]["plan"], plan)
            self.assertEqual(plan, [])
            m = recharger(m)
            self.assertEqual(lire(m, a)["intention"]["plan"], [])
            self.assertEqual(m.objets["vivres"]["portions"], 7)
            self.assertIn("accepte", " ".join(lignes))

    def test_crue_mefiance_puis_promesse_reellement_tenue(self):
        for confiance in (10, 70):
            with self.subTest(confiance=confiance):
                m, a, b = scene(confiance=confiance)
                etape = offre(m, a, b, "tache")
                self.assertEqual(etape["contenu"]["contrepartie"]["condition"], {"objet": "brasero", "allume": True})
                lignes = []
                with patch.object(type(m), "d20", return_value=20):
                    accepte = executer(m, a, etape, lignes)
                if accepte:
                    self.assertTrue(all(o in m.data["references_personnes"] for o in m.objets))
                m = recharger(m)
                self.assertEqual(accepte, confiance == 70)
                self.assertEqual(len(agendas.en_cours(m, a)), int(accepte))
                self.assertEqual(m.objets["vivres"]["portions"], 7 if accepte else 8)
                self.assertIn("accepte" if accepte else "refuse", " ".join(lignes))
                self.assertTrue(any("propose" in c["texte"] for c in m.data["chronique"]))
                if accepte:
                    self.assertTrue(any(porte_par(m, o, a) for o in m.objets if o.startswith("vivres_")))
                    m, suite = vivre(m, 5, jet=20)
                    self.assertTrue(m.objets["brasero"]["allume"])
                    self.assertFalse(agendas.en_cours(m, a, objet="brasero", actifs=True))
                    self.assertTrue(any(c["nature"] == "contrepartie_tenue" for c in m.data["chronique"]))
                    self.assertTrue(any("allume" in c["texte"] or "recharge" in c["texte"] for c in m.data["chronique"]))

    def test_mine_refusee_puis_offre_de_pieces_apres_recharge(self):
        for confiance in (10, 70):
            m, a, b = scene("mine", confiance)
            retenir_refus(m, a, b, "demander", "refus", objet="vivres")
            m = recharger(m)
            etape = offre(m, a, b, "pieces")
            avant = m.data["finances_pnj"][a]
            lignes = []
            with patch.object(type(m), "d20", return_value=20):
                accepte = executer(m, a, etape, lignes)
            m = recharger(m)
            self.assertEqual(accepte, confiance == 70)
            self.assertEqual(m.data["finances_pnj"][a], avant - (etape["contenu"]["contrepartie"]["montant"] if accepte else 0))
            self.assertEqual(m.objets["vivres"]["portions"], 7 if accepte else 8)
            self.assertIn("accepte" if accepte else "refuse", " ".join(lignes))
            self.assertFalse(agendas.en_cours(m, a))

    def test_prive_invisible_et_lectures_dans_la_cle(self):
        m, a, b = scene()
        avant = offres(m, a)
        cle = p._entrees(p.Vue(m, a), {}, 8, 4000)
        lire(m, b)["relations"][a] = relations._nouvelle({"confiance": 0, "rancune": 90})
        lire(m, b)["besoins"]["faim"] = 100
        croire(m, b, "brasero", "etat", {"allume": True, "faible": False}, "vu")
        self.assertEqual(offres(m, a), avant)
        self.assertEqual(p._entrees(p.Vue(m, a), {}, 8, 4000), cle)
        croire(m, a, b, "etat", {"faim": True}, "vu")
        self.assertNotEqual(p._entrees(p.Vue(m, a), {}, 8, 4000), cle)
        agendas.prendre(m, a, {"condition": {"objet": "brasero", "allume": True}, "pour": b, "minute": 0})
        self.assertFalse(any(x[2][0]["contenu"]["contrepartie"]["type"] == "tache" for x in offres(m, a)))

    def test_planificateur_choisit_offre_apres_refus_simple(self):
        for h in (90, 20):
            m, a, b = scene(honnetete=h)
            retenir_refus(m, a, b, "demander", "refus", objet="vivres")
            retenir_refus(m, a, b, "acheter", "refus", objet="vivres")
            with patch.object(p, "VERIFIER", True):
                plan = p.planifier(recharger(m), a, "faim")
            self.assertIsNotNone(plan)
            self.assertIn("proposer", [x["operation"] for x in plan[1]])

    def test_reserve_crochetee_moins_chere_a_honnetete_20(self):
        for h in (90, 20):
            m, a, b = scene(honnetete=h)
            m.joueur.update(salle="chambre_cloche", position=[1, 3])
            m.objets["vivres"]["lieu"] = "reserve"
            m.data["finances_pnj"][a] = 0
            m.objets["crochets"].update(lieu=a, proprietaire=a)
            for qui, case in ((b, [1, 1]), ("aubin", [1, 2]), ("ilse", [1, 3])):
                placer(m, qui, "crypte", case)
                lire(m, qui)["libre"] = 1000000
                croire(m, a, qui, "lieu", "crypte", "vu", salle="crypte", case=case)
            croire(m, a, "vivres", "lieu", "reserve", "savoir", salle="antichambre", case=[8, 3])
            croire(m, a, "reserve", "verrouillee", True, "essai")
            percevoir_tous(m)
            retenir_refus(m, a, b, "demander", "refus", objet="vivres")
            with patch.object(p, "VERIFIER", True):
                plan = p.planifier(recharger(m), a, "faim")
            operations = [e["operation"] for e in plan[1]]
            self.assertIn("crocheter" if h == 20 else "proposer", operations)
            if h == 20:
                m, _ = vivre(recharger(m), 10, jet=20)
                self.assertLess(m.objets["vivres"]["portions"], 8)
                self.assertTrue(any("crochète" in c["texte"] for c in m.data["chronique"]))
                self.assertTrue(any("mange" in c["texte"] for c in m.data["chronique"]))

    def test_bien_cede_vaut_meme_sans_pieces(self):
        from donjon.echanges import valeur_proposition
        m, a, b = scene()
        m.data["finances_pnj"][a] = 0
        self.assertGreater(valeur_proposition(m, a, {"type": "objet", "objet": "lanterne"}, b), 0)

    def test_revoir_deux_etats_deja_vrais_ne_tient_pas_la_promesse(self):
        for objet, attribut, valeur in (("brasero", "allume", True), ("reserve", "verrouillee", True)):
            m, a, b = scene()
            condition = {"objet": objet, attribut: valeur}
            m.objets[objet][attribut] = valeur
            if attribut == "allume":
                m.objets[objet]["combustible"] = 60
            agendas.prendre(m, a, {"condition": condition, "pour": b, "minute": m.data["minutes"], "marche": True})
            m.data["minutes"] += 1
            croire(m, a, objet, "etat" if attribut == "allume" else attribut,
                   {"allume": True, "faible": False} if attribut == "allume" else True, "vu")
            agendas.echoir(m, a)
            m = recharger(m)
            self.assertEqual(len(agendas.en_cours(m, a)), 1)
            self.assertFalse(any(c.get("nature") == "contrepartie_tenue" for c in m.data.get("chronique", [])))

    def test_abandon_pese_la_faute_et_annonce_sa_trahison(self):
        for h in (90, 20):
            m, a, b = scene(honnetete=h)
            etape = offre(m, a, b, "tache")
            with patch.object(type(m), "d20", return_value=20):
                self.assertTrue(executer(m, a, etape, []))
            # Un nouveau devis plus coûteux laisse les valeurs départager tenir et renoncer.
            with patch("donjon.planification.devis_pulsion", return_value=(100, [])):
                agendas.echoir(m, a)
            m = recharger(m)
            e = agendas.en_cours(m, a)[0]
            self.assertEqual(bool(e.get("annule")), h == 20)
            if h == 20:
                lignes = []
                self.assertTrue(annoncer_abandon(m, a, b, e["condition"], lignes))
                m = recharger(m)
                self.assertIn("renonce", " ".join(lignes))
                self.assertFalse(agendas.en_cours(m, a))
                self.assertTrue(any(c["nature"] == "trahison" for c in m.data["chronique"]))


if __name__ == "__main__":
    unittest.main()
