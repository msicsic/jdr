"""Les dossiers suivent la main ; les repères suivent toujours la vue."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon import artisanat, espace, franchissement, obstacles
from donjon.atelier import nouveau_atelier
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from donjon.operations import etape, sequence
from donjon.rendu import regarder
from donjon.spatial import installer, proche
from donjon.temps import instant
from tests.test_sous_obstacle import scene, passage
from tests.test_tensions import recharger
from tests.test_espace import terrasse


DOSSIERS = (artisanat.dossier, franchissement.dossier, obstacles.dossier, espace.dossier)


def console(m, p, tenter=False, requetes=None):
    faits = []

    def appel(instructions, entree, intention, fonction, schema):
        if fonction == "auditer_action":
            return {"conforme": True, "motif": ""}
        if fonction == "auditer_narration":
            return {"segments": {}}
        if requetes is not None:
            requetes.append((instructions, copy.deepcopy(entree)))
        faits.append(copy.deepcopy(entree["faits"]))
        return {"mode": "action", "texte": "", "faits": [], "proposition": p}

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "copie.json"
        m.sauver(path)
        saisies = ["regarder", "est-ce que je pourrais faire ce geste ?"]
        if tenter:
            saisies.append("tenter")
        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_appeler_brut", side_effect=appel),
              patch.object(Monde, "d20", return_value=20),
              patch("builtins.input", side_effect=[*saisies, "quitter"]),
              patch("sys.stdout", io.StringIO()) as sortie):
            jeu.main(["--console", "--connexion", "api", "--save", str(path)])
        return Monde.charger(path), sortie.getvalue(), faits


class DossiersProchesTests(unittest.TestCase):
    def test_obstacles_relais_et_auberge_vue_console_et_recharge(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            with self.subTest(scenario=scenario):
                m = scene(scenario, cible)
                x, y = m.objets[cible]["position"]
                m.joueur["position"] = [x - 2, y]
                m = recharger(m)
                self.assertTrue(m.visible(cible))
                self.assertFalse(proche(m, cible))
                avant = copy.deepcopy(m.data)
                self.assertFalse(any(e["cible"] == cible for e in obstacles.dossier(m)))
                self.assertEqual(m.data, avant)
                r, texte, faits = console(m, passage(cible))
                self.assertIn(m.objets[cible]["nom"], texte)
                self.assertIn("Approche-toi", texte)
                self.assertIn("objet:" + cible, faits[0])
                self.assertFalse(any(e["cible"] == cible for e in faits[0].get("passages_obstacles", [])))
                self.assertEqual((r.joueur["position"], instant(r)), (m.joueur["position"], instant(m)))
                self.assertIn(m.objets[cible]["nom"], regarder(recharger(r)))
                r.joueur["position"] = [x - 1, y]
                r = recharger(r)
                fin, texte, faits = console(r, passage(cible), tenter=True)
                self.assertTrue(any(e["cible"] == cible and "fiche" in e for e in faits[0]["passages_obstacles"]))
                self.assertIn("Tu passes en rampant sous", texte)
                self.assertEqual(fin.joueur["position"], [x + 1, y])
                self.assertEqual(recharger(fin).data, fin.data)

    def test_atelier_repere_eloigne_puis_decoupe_preparee_au_contact(self):
        m = nouveau_atelier()
        installer(m)
        m.joueur.update(position=[2, 3], orientation="nord")
        m = recharger(m)
        self.assertTrue(m.visible("perche_2"))
        self.assertFalse(artisanat.dossier(m))
        p = {"action": "decouper", "cible": "perche_2", "outil": "hache",
             "longueur_cm": 100, "justification": "Prélever un morceau de perche."}
        r, texte, faits = console(m, p)
        self.assertIn("perche de bois 2", texte)
        self.assertNotIn("atelier", faits[0])
        self.assertEqual(r.objets["perche_2"]["longueur_cm"], 300)
        r.joueur["position"] = [2, 2]
        r = recharger(r)
        fin, texte, faits = console(r, p)
        self.assertIn("perche_2", faits[0]["atelier"]["ressources"])
        self.assertIn("Couper la perche", texte)
        self.assertEqual(fin.objets["perche_2"]["longueur_cm"], 300)
        self.assertEqual(instant(fin), instant(r))
        self.assertIn("perche de bois 2", regarder(recharger(fin)))

    def test_franchissement_et_espace_seulement_au_contact_et_perche_portee(self):
        m = nouveau_atelier()
        installer(m)
        m.objets["perche_1"]["lieu"] = "joueur"
        m.joueur.update(position=[2, 3], orientation="nord")
        m = recharger(m)
        self.assertTrue(m.visible("mur_atelier"))
        self.assertIsNone(franchissement.dossier(m))
        self.assertIsNone(espace.dossier(m))
        self.assertIn("perche_1", artisanat.dossier(m)["ressources"])
        p = sequence(etape("franchir_obstacle", "mur_atelier", "terrasse", "perche_1", "appui_mobile", 18))
        r, texte, faits = console(m, p)
        self.assertIn("objet:mur_atelier", faits[0])
        self.assertNotIn("franchissements", faits[0])
        self.assertNotIn("espace", faits[0])
        self.assertIn("mur de l'atelier", texte)
        r.joueur.update(position=[1, 0], orientation="ouest")
        r = recharger(r)
        fin, texte, faits = console(r, p)
        self.assertTrue(faits[0]["franchissements"]["possibilites"])
        self.assertTrue(faits[0]["espace"]["bords"])
        self.assertIn("DEX", texte)
        self.assertEqual(fin.joueur["salle"], "cour")
        self.assertEqual(instant(fin), instant(r))
        self.assertEqual(recharger(fin).data, fin.data)

    def test_non_percu_exclu_de_tous_les_dossiers_meme_au_contact(self):
        m = scene()
        m.joueur["orientation"] = "ouest"
        m = recharger(m)
        self.assertTrue(proche(m, "poutre_conduite"))
        self.assertFalse(m.visible("poutre_conduite"))
        self.assertFalse(any(e["cible"] == "poutre_conduite" for e in obstacles.dossier(m)))
        for m in (scene(), nouveau_atelier()):
            installer(m)
            m = recharger(m)
            # Le prédicat de perception est indépendant de la portée et de la
            # connaissance passée : aucune source non vue ne passe le filtre.
            with patch.object(m, "visible", return_value=False):
                for dossier in DOSSIERS:
                    self.assertFalse(dossier(m))

    def test_installations_filtrees_comme_leurs_supports_apres_recharge(self):
        m, echelle = terrasse()
        m.joueur.update(position=[0, 0], orientation="est")
        support = copy.deepcopy(m.objets["mur_atelier"])
        support["id"] = "autre_appui"
        support["appui_vertical"].update(position_bas=[3, 0], position_haut=[3, 0])
        m.objets[support["id"]] = support
        autre = copy.deepcopy(m.objets[echelle])
        autre.update(id="autre_echelle", position=[3, 0])
        autre["installation"]["support"] = support["id"]
        m.objets[autre["id"]] = autre
        m = recharger(m)
        self.assertTrue(m.visible(autre["id"]))
        self.assertFalse(proche(m, autre["id"]))
        avant = copy.deepcopy(m.data)
        d = espace.dossier(m)
        self.assertEqual([e["objet"] for e in d["installations"]], [echelle])
        self.assertNotIn("autre_appui", [e["appui"] for e in d["bords"]])
        self.assertNotIn("autre_echelle", artisanat.dossier(m)["assemblages"])
        self.assertEqual(m.data, avant)

    def test_sans_coordonnees_pas_de_portee_inventee_mais_biens_portes(self):
        m = nouveau_atelier()
        m.joueur.pop("position", None)
        m.objets["perche_1"]["lieu"] = "joueur"
        m = recharger(m)
        avant = copy.deepcopy(m.data)
        self.assertEqual(artisanat.dossier(m)["ressources"], ["perche_1"])
        self.assertIsNone(franchissement.dossier(m))
        self.assertIsNone(espace.dossier(m))
        self.assertFalse(obstacles.dossier(m))
        self.assertEqual(m.data, avant)
