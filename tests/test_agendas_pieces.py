"""Comparer travail, vente, prêt et faute ; gestes réels et recharges."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, echanges, planification, relations
from donjon.biens import richesse
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.rendu import regarder
from tests.test_agendas_naissance import scene
from tests.test_tensions import placer, recharger, vivre
from tests.support import regarder as tourner


def marche(acteur="odon", travail=False):
    m = scene(acteur)
    for qui, o in m.objets.items():
        if o.get("profil") and qui != acteur:
            lire(m, qui)["libre"] = 1000000
    placer(m, "bram", "bureau", (2, 2))
    m.objets[acteur]["profil"]["valeurs"]["honnetete"] = 100
    m.objets["bram"]["profil"]["valeurs"]["altruisme"] = 100
    for a, b in ((acteur, "bram"), ("bram", acteur)):
        lire(m, a)["relations"][b] = relations._nouvelle({"confiance": 100, "affection": 100})
    m.data["finances_pnj"]["bram"] = 50
    if travail:
        from donjon.spatial import porte_par
        from donjon.vol import proprietaire
        for objet, o in m.objets.items():
            if porte_par(m, objet, acteur) and proprietaire(m, o) == acteur:
                deplacer(m, objet, "reserve", position=[2, 2])
        # La tâche convenue autorise à prendre la clé du payeur à portée,
        # sans la posséder ni en promettre la vente.
        deplacer(m, "cle_paie", "bureau", position=[3, 1])
    else:
        m.objets["jeton"] = {**copy.deepcopy(m.objets["crochets"]), "id": "jeton",
            "nom": "jeton de cuivre", "aliases": ["jeton"], "usages": [],
            "lieu": acteur, "proprietaire": acteur, "prix": 40 - richesse(m, acteur)}
    percevoir_tous(m)
    tourner(m, acteur, "bram")
    croire(m, acteur, "bram", "lieu", "bureau", "vu", salle="bureau", case=[2, 2])
    return recharger(m)


class PiecesTests(unittest.TestCase):
    def stable(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        return n

    def test_deux_debiteurs_vendent_avant_une_faute(self):
        for acteur in ("odon", "remy"):
            with self.subTest(acteur=acteur):
                m = marche(acteur)
                m.objets[acteur]["profil"]["valeurs"]["honnetete"] = 70
                deliberation.choisir(m, acteur, m.data["minutes"])
                plan = lire(m, acteur)["intention"]["plan"]
                self.assertEqual(plan[-1]["operation"], "proposer", plan)
                self.assertNotIn("sans_temoin", [g["condition"] for g in plan])
                avant = richesse(m, acteur)
                m, _ = vivre(self.stable(m), 2, jet=20)
                self.assertGreater(richesse(m, acteur), avant)
                self.assertTrue(any(s["type"] == "proposition" and s["issue"] == "accepte"
                                    for s in lire(m, acteur)["memoire"]))
                self.stable(m)

    def test_travail_paye_par_contrat_commun_et_accompli(self):
        m = marche(travail=True)
        deliberation.choisir(m, "odon", m.data["minutes"])
        plan = lire(m, "odon")["intention"]["plan"]
        self.assertEqual(plan[-1]["operation"], "proposer", plan)
        self.assertEqual(plan[-1]["contenu"]["contrepartie"]["type"], "tache", plan)
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(echanges.executer(m, "odon", plan[-1], []))
        engagement = agendas.en_cours(self.stable(m), "odon")[0]
        self.assertEqual(engagement["paye"]["quoi"], "tache")
        m, _ = vivre(m, 3, jet=20)
        self.assertTrue(m.objets["coffre_paie"]["verrouillee"])
        self.assertEqual(agendas.en_cours(self.stable(m), "odon"), [])

    def test_faute_moins_chere_seulement_selon_honnetete(self):
        m = scene()
        m.objets["odon"]["profil"]["valeurs"]["honnetete"] = 0
        deliberation.choisir(m, "odon", m.data["minutes"])
        plan = lire(m, "odon")["intention"]["plan"]
        self.assertIn("sans_temoin", [g["condition"] for g in plan])
        self.stable(m)

    def test_sommeil_ne_recherche_pas_sans_moyen_nouveau(self):
        from donjon import argent_projet
        m = scene()
        m.objets["odon"]["profil"]["valeurs"]["honnetete"] = 100
        # Plus de tiers joignable ni de bien cessible connu.
        lire(m, "odon")["croyances"].clear()
        agendas.actualiser(m, "odon")
        with patch.object(planification, "chercher", wraps=planification.chercher) as recherche, \
                patch.object(argent_projet, "obtenir", wraps=argent_projet.obtenir) as devis:
            with planification.vues_du_choix(m, "odon"):
                self.assertIsNone(agendas.planifier(m, "odon", "a1"))
            n = recherche.call_count
            m = self.stable(m)
            for _ in range(3):
                with planification.vues_du_choix(m, "odon"):
                    self.assertIsNone(agendas.planifier(m, "odon", "a1"))
                self.assertIsNone(deliberation._plan_argent(m, "odon"))
            self.assertEqual(recherche.call_count, n)
            self.assertEqual(devis.call_count, 1)

    def test_borne_ne_change_pas_le_moyen_choisi(self):
        from donjon import argent_projet
        for m in (marche(), marche("remy"), marche(travail=True), scene()):
            acteur = "remy" if "jeton" in m.objets and m.objets["jeton"]["lieu"] == "remy" else "odon"
            a, b = self.stable(m), self.stable(m)
            deliberation.choisir(a, acteur, 0)
            with patch.object(argent_projet, "_borne_marche", return_value=0):
                deliberation.choisir(b, acteur, 0)
            self.assertEqual(lire(a, acteur)["intention"], lire(b, acteur)["intention"])
            self.assertEqual(a.data, b.data)
            self.stable(a)

    def test_refus_retenu_et_laps_decoupe(self):
        from donjon import pnj
        from donjon.temps import ecouler
        m = marche()
        def avancer(m, ticks):
            with patch.object(Monde, "d20", return_value=20):
                pnj.avancer(m, ecouler(m, ticks), [], ticks)
            return self.stable(m)
        a = avancer(self.stable(m), 1800)
        b = self.stable(m)
        for _ in range(6):
            b = avancer(b, 300)
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(b))

    def test_bourse_empruntee_sans_vol_et_refus_durable(self):
        from donjon.deliberation import retenir_refus
        m = marche()
        m.objets.pop("jeton")
        for e in m.data["esprits"].values():
            e["croyances"].pop("jeton", None)
        deplacer(m, "paie", "bram")
        percevoir_tous(m)
        croire(m, "odon", "paie", "pieces", 200, "savoir")
        deliberation.choisir(m, "odon", 0)
        plan = lire(m, "odon")["intention"]["plan"]
        self.assertTrue(any(g["operation"] == "demander" and g["outil"] == "paie" for g in plan), plan)
        self.assertNotIn("sans_temoin", [g["condition"] for g in plan])
        retenir_refus(m, "odon", "bram", "demander", "mefiance", objet="paie")
        m = self.stable(m)
        deliberation.choisir(m, "odon", 0)
        plan = (lire(m, "odon")["intention"] or {}).get("plan", [])
        self.assertFalse(any(g["operation"] == "demander" and g["outil"] == "paie" for g in plan))

        # Reprendre la scène sans refus : le geste commun établit un prêt,
        # conserve le propriétaire et rend les pièces disponibles au porteur.
        m = marche()
        deplacer(m, "paie", "bram")
        percevoir_tous(m)
        croire(m, "odon", "paie", "pieces", 200, "savoir")
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(echanges.executer(m, "odon", planification._etape("demander", "bram", outil="paie"), []))
        self.assertEqual(m.objets["paie"]["proprietaire"], "bram")
        self.assertEqual(m.objets["paie"]["lieu"], "odon")
        self.assertTrue(any(p["objet"] == "paie" for p in m.data.get("permissions", [])))
        self.stable(m)

    def test_marche_refuse_sans_nouveau_moyen_ne_se_repete_pas(self):
        from donjon.pnj_propositions import offre_refusee
        m = marche()
        deliberation.choisir(m, "odon", 0)
        geste = lire(m, "odon")["intention"]["plan"][-1]
        with patch.object(echanges, "proposer", return_value={"cause": "marche"}):
            self.assertTrue(echanges.executer(m, "odon", geste, []))
        terme = geste["contenu"]["contrepartie"]
        m = self.stable(m)
        self.assertTrue(offre_refusee(m, "odon", "bram", "bram", terme))
        m.data["minutes"] += 120
        self.assertTrue(offre_refusee(m, "odon", "bram", "bram", terme))
