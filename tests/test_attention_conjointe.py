"""Direction vue, rotation commune et connaissance strictement personnelle."""
import copy
import json
import unittest

from donjon import signes, spatial, relations
from donjon.esprits import lire, croire, percevoir_tous, percus
from donjon.pnj import agir, GESTE
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_signes import scene, intention
from tests.test_peur_transmise import auberge
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


def situation(variante="relais"):
    if variante == "relais":
        m, observateur, proche, cible, salle = scene(), "ilse", "aubin", "brune", "antichambre"
    else:
        m, observateur, proche, cible, salle = auberge(), "lucien", "hugues", "odile", "salle_commune"
    for qui, case in ((observateur, (3, 5)), (proche, (4, 5)), (cible, (1, 5))):
        placer(m, qui, salle, case)
    m.joueur.update(salle=salle, position=[3, 6], orientation="est")
    m.objets[observateur]["orientation"] = "est"
    lire(m, observateur)["relations"].clear()
    lire(m, observateur)["relations"][proche] = relations._nouvelle(
        {"confiance": 70, "affection": 40}, m.data["minutes"])
    intention(m, proche, "abriter")
    croire(m, proche, cible, "lieu", salle, "vu", salle=salle, case=[1, 5])
    signes.regarder(m, proche, lire(m, proche)["intention"], cible, "surveille", "crainte")
    # Aucun savoir préalable sur le tiers caché : seule sa propre vue peut l'apprendre.
    lire(m, observateur)["croyances"].pop(cible, None)
    lire(m, observateur)["intention"] = None
    percevoir_tous(m)
    signes.percevoir_tous(m)
    return m, observateur, proche, cible


class AttentionConjointeTests(unittest.TestCase):
    def test_direction_seule_prepare_le_geste_sans_relation_ni_rechoix(self):
        for variante in ('relais', 'auberge'):
            with self.subTest(variante=variante):
                m, qui, proche, cible = situation(variante)
                s = next(s for s in signes.percus(m, qui)
                         if s['personnage'] == proche and 'direction' in s)
                self.assertIsNone(s['envers'])
                e = lire(m, qui)
                e['eveil'] = None
                avant = copy.deepcopy(e['croyances'])
                tirages = copy.deepcopy(m.data.get('tirages_lecture_acteurs', {}))
                signes.lire(m, qui, signes=[s])
                self.assertEqual(e['croyances'], avant)
                self.assertEqual(m.data.get('tirages_lecture_acteurs', {}), tirages)
                self.assertNotIn(s['id'], e['signes_lus'])
                self.assertIsNone(e['eveil'])
                self.assertNotIn(cible, e['croyances'])
                etat = copy.deepcopy(m.data), regarder(m), scene_percue(m)
                m = recharger(m)
                self.assertEqual(etat, (m.data, regarder(m), scene_percue(m)))
                self.assertGreater(agir(m, qui, m.data['minutes'] * 600, [])[0], 0)
                percevoir_tous(m)
                self.assertIn(cible, lire(m, qui)['croyances'])
                etat = copy.deepcopy(m.data), regarder(m), scene_percue(m)
                n = recharger(m)
                self.assertEqual(etat, (n.data, regarder(n), scene_percue(n)))

    def test_coup_reel_rixe_le_proche_regarde_l_agresseur_hors_champ(self):
        from tests.test_defense import epreuve
        m = epreuve()
        placer(m, "ilse", "antichambre", (3, 6))
        m.objets["ilse"]["orientation"] = "est"
        m.joueur.update(position=[3, 4], orientation="est")
        lire(m, "ilse")["intention"] = None
        lire(m, "ilse")["relations"]["aubin"] = relations._nouvelle(
            {"confiance": 70, "affection": 40}, m.data["minutes"])
        intention(m, "aubin", "abriter")
        signes.regarder(m, "aubin", lire(m, "aubin")["intention"], "brune", "surveille", "crainte")
        signes.percevoir_tous(m)
        self.assertNotIn("brune", percus(m, "ilse")[0])
        self.assertTrue(any(s["signe"] == "tremble" for s in signes.percus(m, "ilse")))
        self.assertEqual(agir(m, "ilse", 0, [])[:2], (20, GESTE))
        percevoir_tous(m)
        self.assertIn("brune", percus(m, "ilse")[0])
        self.assertEqual(lire(m, "ilse")["croyances"]["brune"]["lieu"]["source"], "vu")
        avant = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        m = recharger(m)
        self.assertEqual(avant, (m.data, regarder(m), scene_percue(m)))

    def test_deux_scenarios_direction_sans_cible_rotation_vue_et_recharge(self):
        for variante in ("relais", "auberge"):
            with self.subTest(variante=variante):
                m, qui, proche, cible = situation(variante)
                self.assertNotIn(cible, percus(m, qui)[0])
                s = next(s for s in signes.percus(m, qui) if s["personnage"] == proche and "direction" in s)
                self.assertIsNone(s["envers"])
                self.assertEqual(s["direction"], "ouest")
                self.assertNotIn(cible, lire(m, qui)["croyances"])
                duree, issue, _ = agir(m, qui, m.data["minutes"] * 600, [])
                self.assertEqual((duree, issue), (spatial.QUART * 4, GESTE))
                percevoir_tous(m)
                self.assertEqual(lire(m, qui)["croyances"][cible]["lieu"]["source"], "vu")
                avant = copy.deepcopy(m.data), regarder(m), scene_percue(m)
                m = recharger(m)
                self.assertEqual(avant, (m.data, regarder(m), scene_percue(m)))
                self.assertEqual(signes.suivre_regard(m, qui), 0)
                self.assertEqual(signes.mesures(m)["regards_suivis"], 1)

    def test_non_percu_dos_noir_inconscient_et_pas_proche(self):
        for condition in ("dos", "noir", "inconscient", "inconscient_proche", "inconnu"):
            with self.subTest(condition=condition):
                m, qui, proche, _ = situation()
                if condition == "dos":
                    placer(m, proche, "antichambre", (5, 5))
                    m.objets[qui]["orientation"] = "ouest"
                elif condition == "noir":
                    for o in m.objets.values():
                        if o.get("allume"):
                            o["allume"] = False
                elif condition.startswith("inconscient"):
                    from donjon.corps import corps
                    corps(m, proche if condition.endswith("proche") else qui).update(
                        inconscient=6000, inconscient_depuis=0)
                    lire(m, proche if condition.endswith("proche") else qui).update(
                        libre=6000, veille=None, eveil=None)
                else:
                    lire(m, qui)["relations"].clear()
                avant = m.objets[qui]["orientation"]
                self.assertEqual(signes.suivre_regard(m, qui), 0)
                self.assertEqual(m.objets[qui]["orientation"], avant)
                self.assertFalse(lire(recharger(m), qui)["regards_suivis"])

    def test_la_direction_ne_donne_pas_la_vue_a_travers_un_obstacle(self):
        m, qui, proche, cible = situation()
        # Un meuble opaque intercepte la ligne. Le proche peut toujours fixer
        # la dernière case connue : ce regard n'apprend rien sur le tiers.
        meuble = next(x for x, o in m.objets.items() if o["type"] == "contenant")
        placer(m, meuble, "antichambre", (2, 5))
        m.objets[meuble]["bloque_vue"] = True
        signes.percevoir_tous(m)
        self.assertEqual(signes.suivre_regard(m, qui), 20)
        percevoir_tous(m)
        self.assertNotIn(cible, percus(m, qui)[0])
        self.assertNotIn(cible, lire(m, qui)["croyances"])
        m = recharger(m)
        self.assertNotIn(cible, lire(m, qui)["croyances"])
        self.assertNotIn(cible, json.dumps(scene_percue(m)))

    def test_pas_de_repetition_au_delai_et_nouvelle_direction_physique(self):
        m, qui, proche, cible = situation()
        self.assertEqual(signes.suivre_regard(m, qui), 20)
        m.objets[qui]["orientation"] = "est"
        m.data["minutes"] += 20
        signes.percevoir_tous(m)
        m = recharger(m)
        self.assertEqual(signes.suivre_regard(m, qui), 0)
        self.assertEqual(m.objets[qui]["orientation"], "est")
        placer(m, cible, "antichambre", (4, 6))
        croire(m, proche, cible, "lieu", "antichambre", "vu", salle="antichambre", case=[4, 6])
        signes.regarder(m, proche, lire(m, proche)["intention"], cible, "surveille", "crainte")
        signes.percevoir_tous(m)
        self.assertEqual(signes.suivre_regard(m, qui), 10)
        self.assertEqual(m.objets[qui]["orientation"], "sud")

    def test_joueur_voit_direction_sans_identite_cachee(self):
        m, _, proche, cible = situation()
        publics = signes.publics(m)
        self.assertTrue(any(s.get("direction") == "ouest" and s["personnage"] == proche for s in publics))
        self.assertNotIn(cible, json.dumps(publics))
        self.assertIn("regarde dans cette direction : ouest", regarder(m))
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_regard_fixe_ne_suit_pas_secretement_la_cible_mobile(self):
        m, qui, proche, cible = situation()
        placer(m, cible, "crypte", (3, 3))
        signes.percevoir_tous(m)
        self.assertEqual(signes.suivre_regard(m, qui), 20)
        percevoir_tous(m)
        self.assertNotIn(cible, lire(m, qui)["croyances"])
        self.assertNotIn(cible, str(signes.publics(m)))
        m = recharger(m)
        self.assertEqual(signes.suivre_regard(m, qui), 0)

    def test_impression_historique_ne_revele_pas_la_cible_du_regard_actuel(self):
        from unittest.mock import patch
        m, qui, proche, cible = situation()
        m.joueur.update(position=[2, 3], orientation="sud")
        with patch("donjon.signes._jet", return_value=20):
            signes.lire(m, "joueur", expres=True)
        self.assertTrue(any(c["envers"] == cible for c in m.data["lectures"].values()))
        m.joueur.update(position=[3, 6], orientation="est")
        self.assertNotIn(cible, str(signes.impressions(m)))
        self.assertEqual(signes.impressions(m), signes.impressions(recharger(m)))

    def test_meme_laps_entier_ou_decoupe_et_recharge(self):
        for variante in ("relais", "auberge"):
            m, qui, _, cible = situation(variante)
            a, b = recharger(m), recharger(m)
            passer(a, 80)
            for dt in (3, 17, 21, 39):
                passer(b, dt)
                b = recharger(b)
            a = recharger(a)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))
            self.assertEqual(scene_percue(a), scene_percue(b))
            self.assertGreater(signes.mesures(a)["regards_suivis"], 0)


if __name__ == "__main__":
    unittest.main()
