import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.monde import Monde, ErreurMonde
from donjon.mj import MJOpenAI
from donjon.profil_joueur import preparer, catalogue, reponse
from donjon.rendu import fiche


TAILLE = {"profil_joueur": [{"champ": "taille_cm", "valeur": 178}]}


class ProfilJoueurTests(unittest.TestCase):
    def test_socle_humain_adulte_et_migration_respecte_identite(self):
        m = nouveau_atelier()
        self.assertEqual((m.joueur["espece"], m.joueur["stade_vie"]), ("humain", "adulte"))
        self.assertIn("Humain adulte", fiche(m))
        del m.joueur["espece"]
        del m.joueur["stade_vie"]
        m.joueur["taille_cm"] = 182
        charge = Monde(copy.deepcopy(m.data))
        self.assertEqual(charge.joueur["espece"], "humain")
        self.assertEqual(charge.joueur["taille_cm"], 182)
        charge.joueur["espece"] = "elfe"
        charge = Monde(copy.deepcopy(charge.data))
        self.assertEqual(charge.joueur["espece"], "elfe")
        self.assertFalse(catalogue(charge))

    def test_traits_visuels_persistants_sans_capacite_ni_anatomie_inventee(self):
        m = nouveau_atelier()
        p = {"profil_joueur": [{"champ": "couleur_yeux", "valeur": "gris"},
                               {"champ": "couleur_cheveux", "valeur": "bruns"},
                               {"champ": "corpulence", "valeur": "robuste"}]}
        t = preparer(m, p)
        self.assertEqual(t.joueur["stats"], m.joueur["stats"])
        self.assertEqual(t.joueur["masse_kg"], m.joueur["masse_kg"])
        self.assertNotIn("taille_cm", t.joueur)
        self.assertIn("yeux gris", reponse(t, p))
        self.assertEqual(Monde(copy.deepcopy(t.data)).joueur, t.joueur)
        self.assertNotIn("couleur_yeux", catalogue(t))
        for champ, valeur in (("espece", "dragon"), ("couleur_yeux", "ailes"), ("corpulence", "bleus")):
            with self.assertRaises(ErreurMonde):
                preparer(m, {"profil_joueur": [{"champ": champ, "valeur": valeur}]})

    def test_detail_additif_persistant_sans_action_ni_bonus(self):
        m = nouveau_atelier()
        avant = copy.deepcopy(m.data)
        t = preparer(m, TAILLE, m.data["revision"])
        self.assertEqual(avant, m.data)
        self.assertEqual(t.joueur["taille_cm"], 178)
        self.assertNotIn("age_ans", t.joueur)
        for k in ("pv", "stats", "masse_kg", "position", "salle"):
            self.assertEqual(t.joueur[k], m.joueur[k])
        self.assertEqual((t.data["minutes"], t.data["jets"]), (0, 0))
        self.assertEqual(reponse(t, TAILLE), "Tu mesures 1 m 78.")
        self.assertIn("Taille : 1 m 78", fiche(t))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"m.json"
            t.sauver(p)
            charge = Monde.charger(p)
            self.assertEqual(charge.data, t.data)
            self.assertNotIn("taille_cm", catalogue(charge))

    def test_pas_de_redefinition_ni_champ_mecanique_ni_valeur_hors_cadre(self):
        m = nouveau_atelier()
        for p in ({"profil_joueur": [{"champ": "taille_cm", "valeur": 240}]},
                  {"profil_joueur": [{"champ": "taille_cm", "valeur": True}]},
                  {"profil_joueur": [{"champ": "pv", "valeur": 200}]},
                  {"profil_joueur": TAILLE["profil_joueur"]*2}):
            with self.assertRaises(ErreurMonde): preparer(m, p)
        t = preparer(m, TAILLE)
        with self.assertRaises(ErreurMonde): preparer(t, TAILLE)
        with self.assertRaises(ErreurMonde): preparer(m, TAILLE, 99)

    def test_mj_retourne_detail_valide_sans_second_appel(self):
        m = nouveau_atelier()
        avant = copy.deepcopy(m.data)
        r = {"mode": "enrichir_joueur", "texte": "", "faits": ["profil_joueur_a_completer"], "proposition": TAILLE}
        with patch.object(MJOpenAI, "_appeler", return_value=r) as api:
            resultat = MJOpenAI().echanger(m, "je mesure combien ?")
        self.assertEqual(api.call_count, 1)
        self.assertEqual(resultat["texte"], "Tu mesures 1 m 78.")
        self.assertEqual(resultat["_profil_joueur"]["proposition"], TAILLE)
        self.assertEqual(m.data, avant)
        self.assertIn("jamais l'altitude", api.call_args.args[0])

    def test_console_enregistre_avant_reponse(self):
        r = {"mode": "enrichir_joueur", "texte": "", "faits": ["profil_joueur_a_completer"], "proposition": TAILLE}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"m.json"
            with patch("builtins.input", side_effect=["je mesure combien ?", "quitter"]), \
                 patch.object(MJOpenAI, "_appeler", return_value=r), \
                 patch("sys.stdout", new_callable=io.StringIO) as output:
                jeu.main(["--console", "--atelier", "--connexion", "api", "--save", str(p)])
            self.assertEqual(Monde.charger(p).joueur["taille_cm"], 178)
            self.assertIn("Tu mesures 1 m 78.", output.getvalue())
            self.assertNotIn("« tenter »", output.getvalue())
