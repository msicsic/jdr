"""Naissance sur preuve propre de spoliation et acquisition par le graphe commun."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation, planification
from donjon.esprits import lire, percevoir_tous, constater_possession
from donjon.rendu import regarder as rendu
from tests.test_constater_rumeurs import auberge
from tests.test_tensions import relais, placer, recharger, vivre
from tests.support import calme, regarder


def scene(autre=False, vu=True, bien=None):
    if autre:
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        victime, auteur, objet, salle = "marchand", "brune", "marteau", "antichambre"
        cases = ([6, 3], [7, 3])
    else:
        m = calme(auberge(), "anselme", "lucien", "hugues", "odile", "joss", "mireille", "tilo", "mathurine")
        victime, auteur, objet, salle = "anselme", "lucien", "ballot", "salle_commune"
        cases = ([2, 2], [3, 2])
    objet = bien or objet
    placer(m, victime, salle, cases[0])
    placer(m, auteur, salle, cases[1])
    from donjon.geometrie import cases as cases_salle
    libres = iter(c for c in cases_salle(m.data["salles"][salle])
                  if list(c) not in [*cases, [5, 4]])
    for qui, o in m.objets.items():
        if qui not in (victime, auteur) and o["type"] == "personnage" and o["lieu"] == salle:
            placer(m, qui, salle, next(libres))
    m.objets[objet].update(lieu=auteur, proprietaire=victime)
    m.data.setdefault("finances_pnj", {})[victime] = 0
    m.joueur.update(salle=salle, position=[5, 4])
    # La vue commune constate le porteur illégitime et conserve son épreuve.
    if vu:
        regarder(m, victime, auteur)
        regarder(m, victime, objet)
        percevoir_tous(m)
    return m, victime, auteur, objet


class EvenementTests(unittest.TestCase):
    def recharge(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu(m), rendu(n))
        return n

    def test_deux_victimes_sur_preuve_persistante(self):
        for autre in (False, True):
            with self.subTest(autre=autre):
                m, id, auteur, objet = scene(autre)
                self.assertIn(objet, lire(m, id)["portages"])
                lire(m, id)["memoire"].clear()
                agendas.actualiser(m, id)
                a = agendas.projets(self.recharge(m), id)[0]
                self.assertEqual(a["sorte"], "récupérer")
                self.assertEqual((a["parametres"]["objet"], a["parametres"]["qui"]), (objet, auteur))
                with planification.vues_du_choix(m, id):
                    resultat = agendas.planifier(m, id, a["id"])
                self.assertIsNotNone(resultat)
                self.assertTrue(any(x["operation"] in ("demander", "prendre", "assommer") for x in resultat[1]))
                agendas.verifier(self.recharge(m), id)

    def test_ignorance_et_pret_ne_creent_pas_de_projet(self):
        m, id, auteur, objet = scene(vu=False)
        agendas.actualiser(m, id)
        self.assertEqual(agendas.projets(self.recharge(m), id), [])
        # Même position connue, mais permission établie : pas de tort.
        m, id, auteur, objet = scene()
        lire(m, id)["croyances"][objet]["lieu"]["possession"]["permis"] = True
        agendas.actualiser(m, id)
        self.assertEqual(agendas.projets(self.recharge(m), id), [])

    def test_fins_connues_et_pas_de_renaissance(self):
        for fin in ("rendu", "detruit", "consomme"):
            with self.subTest(fin=fin):
                m, id, auteur, objet = scene(autre=fin == "consomme",
                                            bien="vivres" if fin == "consomme" else None)
                agendas.actualiser(m, id)
                if fin == "rendu":
                    m.objets[objet]["lieu"] = id
                    constater_possession(m, id, objet, "essai")
                else:
                    m.objets[objet]["portions" if fin == "consomme" else "integrite"] = 0
                    percevoir_tous(m)
                    self.assertEqual(lire(m, id)["croyances"][objet]["fin"]["valeur"], fin)
                agendas.actualiser(m, id)
                a = agendas.projets(self.recharge(m), id)[0]
                self.assertIn(a["etat"], ("atteint", "abandonne"))
                agendas.actualiser(m, id)
                self.assertEqual(len(agendas.projets(self.recharge(m), id)), 1)

    def test_sommeil_et_publication_interrompue(self):
        m, id, auteur, objet = scene()
        avant = copy.deepcopy(m.data)
        with self.assertRaises(RuntimeError):
            with planification.vues_du_choix(m, id):
                agendas.actualiser(m, id)
                raise RuntimeError()
        self.assertEqual(m.data, avant)
        agendas.actualiser(m, id)
        with patch("donjon.planification.chercher", return_value=None) as chercher:
            with planification.vues_du_choix(m, id):
                self.assertIsNone(agendas.planifier(m, id, "a1"))
            self.assertEqual(chercher.call_count, 1)
            m = self.recharge(m)
            with planification.vues_du_choix(m, id):
                self.assertIsNone(agendas.planifier(m, id, "a1"))
            self.assertEqual(chercher.call_count, 1)

    def test_plafond_et_poids(self):
        m, id, auteur, objet = scene()
        m.objets[id]["profil"]["agendas"] = [
            {"sorte": "garder", "parametres": {"lieu": "salle_commune"}} for _ in range(3)]
        agendas.actualiser(m, id)
        stock = agendas.projets(self.recharge(m), id)
        self.assertEqual(len(stock), 4)
        self.assertEqual(sum(a["etat"] == "actif" for a in stock), 3)
        a = next(a for a in stock if a["sorte"] == "récupérer")
        poids = agendas.poids(m, id, a)
        m.objets[id]["profil"]["valeurs"]["ambition"] = 100
        self.assertGreaterEqual(agendas.poids(m, id, a), poids)

    def test_refus_retenu_selon_sa_cause(self):
        for autre in (False, True):
            m, id, auteur, objet = scene(autre)
            m.objets[id]["profil"]["valeurs"]["douceur"] = 100
            agendas.actualiser(m, id)
            with planification.vues_du_choix(m, id):
                avant = agendas.planifier(m, id, "a1")
            self.assertIsNotNone(avant)
            self.assertTrue(any(g["operation"] == "demander" for g in avant[1]))
            deliberation.retenir_refus(m, id, auteur, "demander", "mefiance", objet=objet)
            m = self.recharge(m)
            with planification.vues_du_choix(m, id):
                apres = agendas.planifier(m, id, "a1")
            self.assertFalse(apres and any(g["operation"] == "demander" for g in apres[1]))
            self.recharge(m)

    def test_suppression_non_apprise_ne_prouve_pas_la_fin(self):
        m, id, auteur, objet = scene(True)
        agendas.actualiser(m, id)
        poids = agendas.poids(m, id, agendas.projets(m, id)[0])
        del m.objets[objet]
        agendas.actualiser(m, id)
        self.assertEqual(agendas.poids(m, id, agendas.projets(m, id)[0]), poids)
        with planification.vues_du_choix(m, id):
            self.assertIsNone(agendas.planifier(m, id, "a1"))
        self.assertEqual(agendas.projets(self.recharge(m), id)[0]["etat"], "sommeil")

    def test_laps_entier_decoupe(self):
        m, id, auteur, objet = scene()
        agendas.actualiser(m, id)
        a, _ = vivre(self.recharge(m), 2, jet=20)
        b = self.recharge(m)
        for _ in range(2):
            b, _ = vivre(b, 1, jet=20)
        self.assertEqual(a.data, b.data)
        self.assertEqual(rendu(a), rendu(self.recharge(b)))

    def test_vol_effectif_et_reprise_par_moyen_commun(self):
        from donjon.pnj import _executer
        from donjon.deplacement_objet import deplacer
        from tests.test_temps_etat import plan
        for autre in (False, True):
            with self.subTest(autre=autre):
                m, id, auteur, objet = scene(autre, vu=False)
                salle = m.objets[id]["lieu"]
                deplacer(m, objet, salle, position=m.objets[auteur]["position"])
                self.assertTrue(_executer(m, auteur, plan("prendre", objet), [], []))
                regarder(m, id, auteur)
                percevoir_tous(m)
                self.assertIn(objet, lire(m, id)["portages"])
                agendas.actualiser(m, id)
                m = self.recharge(m)
                self.assertTrue(any(a["sorte"] == "récupérer" for a in agendas.projets(m, id)))
                self.assertTrue(_executer(m, auteur, plan("poser", objet, lieu=salle), [], []))
                regarder(m, id, objet)
                percevoir_tous(m)
                with planification.vues_du_choix(m, id):
                    resultat = agendas.planifier(m, id, "a1")
                self.assertIsNotNone(resultat)
                self.assertEqual(resultat[1][-1]["operation"], "prendre")
                for etape in resultat[1]:
                    self.assertTrue(_executer(m, id, etape, [], []))
                percevoir_tous(m)
                constater_possession(m, id, objet, "essai")
                self.assertEqual(m.objets[objet]["lieu"], id)
                agendas.actualiser(m, id)
                self.assertEqual(agendas.projets(self.recharge(m), id)[0]["etat"], "atteint")

    def test_reprise_autonome_apres_depot(self):
        from donjon.pnj import _executer
        from tests.test_temps_etat import plan
        for autre in (False, True):
            m, id, auteur, objet = scene(autre)
            agendas.actualiser(m, id)
            self.assertTrue(_executer(m, auteur, plan("poser", objet, lieu=m.objets[auteur]["lieu"]), [], []))
            # Le dépôt est acquis ; le voleur n'a plus de projet concurrent
            # dans cette épreuve de la reprise autonome de la victime.
            m.objets[auteur]["profil"]["pulsions"] = []
            lire(m, auteur)["pulsions"] = []
            m.objets[auteur]["profil"]["valeurs"]["ambition"] = 0
            m.objets[id]["profil"]["pulsions"] = []
            lire(m, id)["pulsions"] = []
            regarder(m, id, objet)
            percevoir_tous(m)
            deliberation.choisir(m, id, m.data["minutes"])
            self.assertEqual(lire(m, id)["intention"]["motif"], "agenda")
            m, _ = vivre(self.recharge(m), 3, jet=20)
            self.assertTrue(any(c["pnj"] == id and " prend " in c["texte"]
                                for c in m.data.get("chronique", [])))
            self.assertEqual(m.objets[objet]["proprietaire"], id)
            agendas.actualiser(m, id)
            self.assertEqual(agendas.projets(self.recharge(m), id)[0]["etat"], "atteint")

