import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.artisanat import fabrication
from donjon.espace import preparer, a_completer, dossier
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.operations import sequence, etape
from donjon.mj import MJOpenAI
from donjon.rendu import regarder
from donjon.carte import carte
from donjon.transactions import du_type


AJOUT = {"abords": [{"cadre": "terrasse_nord", "terrain": "terre"}]}


def terrasse():
    m = nouveau_atelier()
    moteur = Moteur(m)
    with patch.object(Monde, "d20", return_value=20):
        moteur.executer(moteur.preparer(fabrication(["perche_1", "perche_2"], "perche_3", "ficelle", "hache")))
        id = m.trouver("echelle")
        moteur.executer(moteur.preparer(proposition("installer", id, "mur_atelier")))
        moteur.executer(moteur.preparer(proposition("franchir", id)))
    return m, id


class EspaceTests(unittest.TestCase):
    def test_vue_explicite_du_sol_sous_chaque_bord_et_pas_de_matiere_inventee(self):
        m, _ = terrasse()
        m = preparer(m, {"abords": [{"cadre": "terrasse_nord", "terrain": "pierre"}]})
        vue = dossier(m)
        nord = next(b for b in vue["bords"] if b["direction"] == "nord")
        self.assertEqual(nord["position_relative"], "en contrebas")
        self.assertTrue(any("nord" in t and "2,4 m en contrebas" in t and "pierre" in t for t in vue["observations_visibles"]))
        del m.objets["abord_terrasse_nord_sol"]
        vue = dossier(m)
        self.assertIsNone(next(b for b in vue["bords"] if b["direction"] == "nord")["terrain"])
        self.assertFalse(any("nord" in t and "pierre" in t for t in vue["observations_visibles"]))
        m.data["salles"]["terrasse"]["lumiere_naturelle"] = 0
        self.assertIsNone(dossier(m))

    def test_question_spatiale_recoit_observations_et_consignes_courtes(self):
        m, _ = terrasse()
        m = preparer(m, AJOUT)
        m.memoriser("il y a quoi sous la terrasse ?", "Les faits ne précisent pas ce qu'il y a en dessous.")
        avant = copy.deepcopy(m.data)
        r = {"mode": "dialogue", "texte": "Au nord, le passage est 2,40 m plus bas.", "faits": ["espace"], "proposition": None}
        with patch.object(MJOpenAI, "_appeler", return_value=r) as api:
            MJOpenAI().echanger(m, "il y a quoi sous la terrasse ?")
        self.assertEqual(api.call_count, 1)
        instructions, entree = api.call_args.args[:2]
        # Une question peut appeler la proposition d'un geste : les règles d'atelier restent fournies.
        self.assertIn("observations_visibles", instructions)
        self.assertTrue(entree["faits"]["espace"]["observations_visibles"])
        self.assertEqual(m.data, avant)

    def test_completion_pure_persistante_sans_objets_gratuits(self):
        m, id = terrasse()
        avant = copy.deepcopy(m.data)
        t = preparer(m, AJOUT, m.data["revision"])
        self.assertEqual(m.data, avant)
        self.assertFalse(a_completer(t))
        self.assertEqual(t.objets[id], m.objets[id])
        self.assertEqual(t.joueur, m.joueur)
        self.assertEqual(t.data["minutes"], m.data["minutes"])
        self.assertEqual(dossier(t)["installations"][0]["bord_oppose"], "nord")
        self.assertIn("2.4 m", regarder(t))
        self.assertNotIn("Passage extérieur", carte(t))  # pas encore visité
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"partie.json"
            t.sauver(p)
            charge = Monde.charger(p)
            self.assertEqual(charge.data, t.data)
            with self.assertRaises(ErreurMonde):
                preparer(charge, AJOUT)

    def test_cadre_invalide_collision_doublon_et_revision_refuses(self):
        for cas in ("cadre", "terrain", "doublon", "collision", "revision", "propriete"):
            with self.subTest(cas=cas):
                m, _ = terrasse()
                p = copy.deepcopy(AJOUT)
                revision = m.data["revision"]
                if cas == "cadre": p["abords"][0]["cadre"] = "crypte"
                if cas == "terrain": p["abords"][0]["terrain"] = "trésor"
                if cas == "doublon": p["abords"] *= 2
                if cas == "collision": m.data["salles"]["cour"]["plan"]["origine"] = [20, 6]
                if cas == "revision": revision -= 1
                if cas == "propriete": p["abords"][0]["hauteur_cm"] = 1
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde): preparer(m, p, revision)
                self.assertEqual(avant, m.data)

    def test_remonter_repositionner_descendre_et_retour(self):
        m, id = terrasse()
        m = preparer(m, AJOUT)
        moteur = Moteur(m)
        p = sequence(etape("soulever", id, "terrasse"),
                     etape("appuyer", id, outil="appui_terrasse_nord"), etape("franchir", id))
        avant = copy.deepcopy(m.data)
        plan = moteur.preparer(p)
        self.assertEqual(m.data, avant)
        with patch.object(Monde, "d20", return_value=20): moteur.executer(plan)
        self.assertEqual(m.joueur["salle"], "abord_terrasse_nord")
        self.assertEqual(m.objets[id]["installation"]["support"], "appui_terrasse_nord")
        self.assertFalse(m.data["salles"]["terrasse"]["sorties"])
        self.assertIn("Passage extérieur", carte(m))
        with patch.object(Monde, "d20", return_value=20):
            moteur.executer(moteur.preparer(proposition("franchir", id)))
        self.assertEqual(m.joueur["salle"], "terrasse")

    def test_contraintes_et_prevalidation_sequence_sans_retrait_partiel(self):
        for cas in ("masse", "prise", "longueur", "stabilite", "destination"):
            with self.subTest(cas=cas):
                m, id = terrasse()
                m = preparer(m, AJOUT)
                if cas == "masse": m.objets[id]["masse"] = 30
                if cas == "prise": m.objets["mur_atelier"]["appui_vertical"]["prise_sommet"] = False
                if cas == "longueur": m.objets[id]["longueur_cm"] = 150
                if cas == "stabilite": m.objets["appui_terrasse_nord"]["appui_vertical"]["sol_stable"] = False
                p = sequence(etape("soulever", id, "crypte" if cas == "destination" else "terrasse"),
                             etape("appuyer", id, outil="appui_terrasse_nord"))
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde): Moteur(m).preparer(p)
                self.assertEqual(avant, m.data)

    def test_saut_reception_reelle_sur_reussite_et_echec(self):
        for jet, perte in ((20, 2), (1, 5)):
            m, _ = terrasse()
            m = preparer(m, AJOUT)
            moteur = Moteur(m)
            p = sequence(etape("sauter", "appui_terrasse_nord", "abord_terrasse_nord"))
            plan = moteur.preparer(p)
            self.assertEqual(plan.dd, 13)
            pv = m.joueur["pv"]
            with patch.object(Monde, "d20", return_value=jet): moteur.executer(plan)
            self.assertEqual(m.joueur["pv"], pv-perte)
            self.assertEqual(m.joueur["salle"], "abord_terrasse_nord")
            with self.assertRaises(ErreurMonde): moteur.preparer(p)

    def test_complement_mj_avant_arbitrage_sans_muter_original(self):
        m, _ = terrasse()
        avant = copy.deepcopy(m.data)
        r = {"mode": "dialogue", "texte": "Le bord nord surplombe un passage.", "faits": ["espace"], "proposition": None}
        mj = MJOpenAI("gpt-6-luna", connexion="api")
        with patch.object(mj, "_appeler", side_effect=[AJOUT, r]) as api:
            reponse = mj.echanger(m, "il y a d'autres issues ?")
        self.assertEqual(api.call_count, 2)
        self.assertIn("espace", api.call_args_list[1].args[1]["faits"])
        self.assertEqual(m.data, avant)
        m = preparer(m, du_type(reponse, "espace")["proposition"], du_type(reponse, "espace")["revision"])
        with patch.object(mj, "_appeler", return_value=r) as api:
            mj.echanger(m, "il y a d'autres issues ?")
        self.assertEqual(api.call_count, 1)

    def test_console_enregistre_espace_avant_action_et_lecture(self):
        m, id = terrasse()
        p = sequence(etape("soulever", id, "terrasse"), etape("appuyer", id, outil="appui_terrasse_nord"), etape("franchir", id))
        r = {"mode": "action", "texte": "", "faits": ["espace"], "proposition": p,
             "_transactions": [{"type": "espace", "revision": m.data["revision"], "proposition": AJOUT}]}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp)/"test.json"
            m.sauver(chemin)
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                 patch("builtins.input", side_effect=["mj je remonte mon échelle puis je descends de l'autre côté", "tenter", "quitter"]), \
                 patch("jeu.MJOpenAI.echanger", return_value=r), patch("jeu.MJOpenAI.raconter_resultat", return_value={"mode": "dialogue", "texte": "Tu descends au nord."}), \
                 patch.object(Monde, "d20", return_value=20), patch("sys.stdout", new_callable=io.StringIO):
                jeu.main(["--console", "--atelier", "--connexion", "api", "--save", str(chemin)])
            charge = Monde.charger(chemin)
            self.assertEqual(charge.joueur["salle"], "abord_terrasse_nord")
            self.assertFalse(a_completer(charge))
