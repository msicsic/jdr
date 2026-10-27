"""Une manière de geste ne change ni sa portée, ni les effets qu'il exécute."""
import copy
import unittest
from unittest.mock import patch

from donjon.improvisation import proposition, issue
from donjon.moteur import Moteur
from donjon.mj import MJOpenAI
from donjon.obstacles import dossier
from donjon.proximite import HorsDePortee
from donjon.spatial import memoriser
from donjon.temps import instant
from tests.test_sous_obstacle import scene, passage, jouer
from tests.test_tensions import recharger


def reponse(p):
    return {"mode": "action", "texte": "", "faits": [], "proposition": p}


class GesteHorsPorteeTests(unittest.TestCase):
    def souvenir(self, scenario="relais", cible="poutre_conduite"):
        m = scene(scenario, cible)
        memoriser(m)
        x, y = m.objets[cible]["position"]
        m.joueur.update(position=[x - 2, y], orientation="ouest")
        return recharger(m)

    def test_passage_hors_vue_refuse_puis_possible_apres_les_pas(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            with self.subTest(scenario=scenario):
                m = self.souvenir(scenario, cible)
                self.assertFalse(m.visible(cible))
                avant = copy.deepcopy(m.data)
                d = [e for e in dossier(m) if e["cible"] == cible and e["methode"] == "dessous"]
                self.assertEqual(d, [])
                self.assertEqual(m.data, avant)
                p = reponse(passage(cible))
                r, texte = jouer(m, ["est-ce que je pourrais passer dessous ?"], [p])
                self.assertIn("Approche-toi", texte)
                self.assertNotIn("Test DEX", texte)
                self.assertEqual(r.joueur["position"], m.joueur["position"])
                self.assertEqual(instant(r), instant(m))
                r, texte = jouer(r, ["est", "est-ce que je pourrais passer dessous ?", "tenter"], [p])
                self.assertIn("Ramper sous", texte)
                self.assertIn("Tu passes en rampant sous", texte)
                x, y = m.objets[cible]["position"]
                self.assertEqual(r.joueur["position"], [x + 1, y])
                self.assertTrue(r.objets[cible]["bloque_passage"])
                self.assertGreaterEqual(instant(r), instant(m) + 120)

    def test_improviser_refuse_toutes_les_approches_sans_jet_ni_fiche(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            for approche in ("expression", "manipulation", "effort", "adresse", "observation"):
                with self.subTest(scenario=scenario, approche=approche):
                    m = self.souvenir(scenario, cible)
                    p = proposition("Faire un geste", issue("Un geste."), issue("Le geste manque."),
                                    cibles=[cible], approche=approche, stat="DEX", difficulte=10)
                    avant = copy.deepcopy(m.data)
                    with self.assertRaises(HorsDePortee) as exc:
                        Moteur(m).preparer(p)
                    self.assertIn(cible, exc.exception.attendu)
                    self.assertEqual(m.data, avant)
                    r, texte = jouer(m, ["est-ce que je pourrais faire ce geste ?"], [reponse(p)])
                    self.assertIn("Approche-toi", texte)
                    self.assertNotIn("Test DEX", texte)
                    self.assertEqual(r.joueur["position"], m.joueur["position"])
                    self.assertEqual((instant(r), r.data["jets"]), (instant(m), m.data["jets"]))
                    self.assertFalse(r.data.get("gestes_improvises"))

    def test_contexte_reel_garde_le_passage_et_le_souvenir_sans_fiche_a_distance(self):
        m = self.souvenir()
        m.joueur["position"] = [3, 1]  # position du fil Luna d'intégration
        m = recharger(m)
        avant = copy.deepcopy(m.data)

        def appel(instructions, entree, intention, fonction, schema):
            self.assertEqual(fonction, "repondre_au_joueur")
            self.assertIn("passer_obstacle", instructions)
            self.assertIn("seulement en souvenir", instructions)
            faits = entree["faits"]
            self.assertTrue(any(e["id"] == "poutre_conduite" for e in faits["souvenirs_visuels"]))
            self.assertFalse(any(e.get("cible") == "poutre_conduite" and "fiche" in e
                                 for e in faits.get("passages_obstacles", [])))
            return reponse(passage())

        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_appeler_brut", side_effect=appel)):
            r = MJOpenAI().echanger(m, "est-ce que je pourrais passer sous la poutre effondrée ?")
        self.assertIn("Approche-toi", r["texte"])
        self.assertEqual(m.data, avant)



class RefusLocalTests(unittest.TestCase):
    def test_console_barricade_et_prise_refus_exact_puis_fiche_au_contact(self):
        from tests.test_audits_attendu import jouer as console
        from donjon.operations import sequence, etape
        from tests.test_tensions import placer
        for cible, p, saisie in (
            ("poutre_conduite", passage(), "est-ce que je pourrais passer sous la poutre effondrée ?"),
            ("crochets", sequence(etape("deplacer", "crochets", "joueur")),
             "est-ce que je pourrais récupérer la trousse de crochets ?"),
        ):
            with self.subTest(cible=cible):
                m = scene()
                m.data["salles"]["echoppe"]["lumiere_naturelle"] = 2
                m.joueur.update(position=[3, 1], orientation="est")
                placer(m, cible, "echoppe", (7, 1))  # six mètres, quatre cases
                m = recharger(m)
                with self.assertRaises(HorsDePortee) as refus:
                    Moteur(m).preparer(p, "MJ")
                m, _, _ = console(m, "quitter", [], [])  # perception initiale enregistrée
                avant = copy.deepcopy(m.data)
                r, texte, appels = console(m, saisie, [reponse(p)], [])
                self.assertEqual([f for f, _ in appels], ["repondre_au_joueur"])
                self.assertIn(str(refus.exception), texte)
                self.assertNotIn(refus.exception.attendu, texte)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], str(refus.exception))
                self.assertEqual({k: v for k, v in r.data.items() if k not in ("conversation", "narrations_mj")},
                                 {k: v for k, v in avant.items() if k not in ("conversation", "narrations_mj")})
                # Le même refus reste affiché après une nouvelle recharge.
                r, texte, appels = console(recharger(r), saisie, [reponse(p)], [])
                self.assertIn(str(refus.exception), texte)
                self.assertEqual({k: v for k, v in r.data.items() if k not in ("conversation", "narrations_mj")},
                                 {k: v for k, v in avant.items() if k not in ("conversation", "narrations_mj")})
                m.joueur["position"] = [6, 1]
                m = recharger(m)
                r, texte, appels = console(m, saisie, [reponse(p)], [])
                self.assertNotIn("Approche-toi", texte)
                self.assertIn("tenter", texte.lower())
                self.assertEqual(r.joueur["position"], m.joueur["position"])
                self.assertEqual(instant(r), instant(m))

    def test_cible_inconnue_garde_la_correction_ordinaire(self):
        from tests.test_audits_attendu import jouer as console
        m = scene()
        faux = reponse(passage("cible_inconnue"))
        r, texte, appels = console(m, "est-ce que je pourrais passer sous la poutre effondrée ?",
                                  [faux, reponse(passage())], [])
        interpretations = [e for f, e in appels if f == "repondre_au_joueur"]
        self.assertEqual(len(interpretations), 2)
        self.assertIn("attendu", interpretations[1]["faits"]["retour_moteur"])
        self.assertNotIn("Approche-toi", texte)
        self.assertIn("tenter", texte.lower())
