import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.defi import nouveau_defi
from donjon.faits_locaux import preparer_inscription, supports
from donjon.geometrie import placer
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import decrire
from donjon.spatial import installer as installer_cases


PROPOSITION = {"support": "antichambre_murs", "inscription": "Veille au niveau des eaux."}


class FaitsLocauxTests(unittest.TestCase):
    def test_inscription_persistante_et_lisible_comme_objet(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        travail, id = preparer_inscription(m, PROPOSITION, m.data["revision"])
        self.assertEqual(m.data, avant)
        self.assertEqual(travail.objets[id]["lieu"], PROPOSITION["support"])
        self.assertNotIn(PROPOSITION["support"], supports(travail))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            travail.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.trouver("inscription sur les murs"), id)
        self.assertIn(PROPOSITION["inscription"], decrire(reprise, id, detail=True))
        moteur = Moteur(reprise)
        plan = moteur.preparer(proposition("lire", id))
        with patch.object(Monde, "d20", return_value=20):
            self.assertIn(PROPOSITION["inscription"], moteur.executer(plan))
        self.assertIn(id, reprise.data["lus"])

    def test_support_invisible_lointain_ou_absent_refuse_sans_mutation(self):
        m = nouveau_monde()
        m.objets["poutre"] = objet("poutre", "poutre", "surface", "crypte",
                                    materiau="bois")
        self.assertNotIn("poutre", supports(m))
        avant = copy.deepcopy(m.data)
        for p in ({**PROPOSITION, "support": "poutre"},
                  {**PROPOSITION, "support": "seconde_cloche"},
                  {**PROPOSITION, "inscription": ""},
                  {**PROPOSITION, "mobile": True}):
            with self.subTest(p=p), self.assertRaises(ErreurMonde):
                preparer_inscription(m, p)
            self.assertEqual(m.data, avant)
        m.objets["lanterne"]["allume"] = False
        self.assertNotIn("antichambre_murs", supports(m))
        with self.assertRaises(ErreurMonde):
            preparer_inscription(m, PROPOSITION)

    def test_en_cases_le_detail_exige_proximite_et_lumiere(self):
        m = nouveau_defi()
        installer_cases(m)
        travail, id = preparer_inscription(m, PROPOSITION)
        self.assertTrue(travail.visible(id))
        travail.joueur["position"] = [7, 5]
        self.assertFalse(travail.visible(id))
        travail.joueur["position"] = [1, 3]
        for source in ("lanterne", "torche"):
            travail.objets[source]["allume"] = False
        self.assertFalse(travail.visible(id))
        with self.assertRaises(ErreurMonde):
            Moteur(travail).preparer(proposition("lire", id))

    def test_gravure_sur_poutre_existante(self):
        m = nouveau_defi()
        installer_cases(m)
        poutre = objet("poutre", "poutre du refuge", "surface", "antichambre",
                       genre="f", materiau="chêne")
        placer(poutre, "antichambre", [1, 2])
        m.objets["poutre"] = poutre
        proposition_mj = {"support": "poutre", "inscription": "Veille au niveau des eaux."}
        travail, id = preparer_inscription(m, proposition_mj)
        self.assertTrue(travail.visible(id))
        self.assertEqual(travail.objets[id]["lieu"], "poutre")
        self.assertEqual(travail.trouver("gravure sur la poutre du refuge"), id)

    def test_mj_propose_sans_texte_et_le_moteur_redige_la_reponse(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        reponse = {"mode": "enrichir_inscription", "texte": "", "faits": ["supports_inscription"],
                   "proposition": PROPOSITION}
        with patch.object(MJOpenAI, "_appeler", return_value=reponse) as appel:
            resultat = MJOpenAI().echanger(m, "Y a-t-il une inscription sur les murs ?")
        self.assertEqual(appel.call_count, 1)
        self.assertEqual(m.data, avant)
        self.assertIn(PROPOSITION["inscription"], resultat["texte"])
        self.assertEqual(resultat["_inscription"]["proposition"], PROPOSITION)

    def test_mj_recoit_le_refus_et_corrige_un_support_invente(self):
        m = nouveau_monde()
        avant = copy.deepcopy(m.data)
        premier = {"mode": "enrichir_inscription", "texte": "", "faits": ["supports_inscription"],
                   "proposition": {**PROPOSITION, "support": "poutre_inexistante"}}
        second = {"mode": "enrichir_inscription", "texte": "", "faits": ["supports_inscription"],
                  "proposition": PROPOSITION}
        with patch.object(MJOpenAI, "_appeler", side_effect=[premier, second]) as appel:
            resultat = MJOpenAI().echanger(m, "Que vois-je sur le mur ?")
        self.assertEqual(appel.call_count, 2)
        self.assertIn("poutre_inexistante", appel.call_args_list[1].args[1]["faits"]["retour_moteur"]["proposition_refusee"]["support"])
        self.assertIn(PROPOSITION["inscription"], resultat["texte"])
        self.assertEqual(m.data, avant)

    def test_enrichissement_refuse_un_recit_joint_non_valide(self):
        reponse = {"mode": "enrichir_inscription",
                   "texte": "Une seconde cloche est cachée sous le plancher.",
                   "faits": ["supports_inscription"], "proposition": PROPOSITION}
        with patch.object(MJOpenAI, "_appeler", return_value=reponse):
            with self.assertRaises(ErreurMonde):
                MJOpenAI().echanger(nouveau_monde(), "Que vois-je sur les murs ?")

    def test_console_sauvegarde_avant_affichage_et_relecture(self):
        reponse = {"mode": "enrichir_inscription", "texte": "", "faits": ["supports_inscription"],
                   "proposition": PROPOSITION}
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", return_value=reponse),
                  patch("builtins.input", side_effect=["mj y a-t-il une inscription sur les murs ?",
                                                      "lire inscription sur les murs", "quitter"]),
                  patch.object(Monde, "d20", return_value=20),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            recharge = Monde.charger(chemin)
        id = recharge.trouver("inscription sur les murs")
        self.assertIn(id, recharge.data["lus"])
        self.assertIn(PROPOSITION["inscription"], sortie.getvalue())
        self.assertEqual(len([o for o in recharge.objets.values() if o.get("origine_description") == "MJ"]), 1)

    def test_echec_de_sauvegarde_ne_montre_pas_l_inscription(self):
        reponse = {"mode": "enrichir_inscription", "texte": "", "faits": ["supports_inscription"],
                   "proposition": PROPOSITION}
        original = Monde.sauver
        def sauver(monde, chemin):
            if any(o.get("origine_description") == "MJ" for o in monde.objets.values()):
                raise OSError("Disque plein")
            return original(monde, chemin)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler", return_value=reponse),
                  patch.object(Monde, "sauver", sauver),
                  patch("builtins.input", side_effect=["mj y a-t-il une inscription sur les murs ?", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                jeu.main(["--console", "--save", str(chemin), "--connexion", "api"])
            self.assertNotIn(PROPOSITION["inscription"], sortie.getvalue())
            self.assertFalse(any(o.get("origine_description") == "MJ"
                                 for o in Monde.charger(chemin).objets.values()))


if __name__ == "__main__":
    unittest.main()
