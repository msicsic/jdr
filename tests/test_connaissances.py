import copy
import io
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import patch

import jeu
from donjon.comparaison import Comparateur, texte_comparaison
from donjon.connaissances import catalogue, preparer_savoirs
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde, objet


TEXTE = "Gorm tient à l'anneau parce qu'il lui rappelle son ancien métier de veilleur."


def ajout(texte=TEXTE, sujet="lien_anneau", personnage="marchand"):
    return {"personnage": personnage, "savoirs": [{"sujet": sujet, "texte": texte}]}


def proposition(p=None):
    return {"mode": "enrichir_savoirs", "texte": "", "faits": ["connaissances_a_completer"],
            "proposition": p or ajout()}


def dialogue():
    return {"mode": "dialogue", "texte": "Gorm : « Cet anneau me rappelle mon ancien métier de veilleur. »",
            "faits": ["connaissances_pnj"], "proposition": None}


class ConnaissancesTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_monde()
        self.m.joueur["salle"] = "echoppe"

    def test_savoirs_auteur_situes_sans_reveler_contenu_cache(self):
        c = self.m.contexte()["connaissances_pnj"]
        self.assertIn("crochetage", c["marchand"]["porte_crypte"]["texte"])
        self.assertNotIn("coffre", str(c))
        self.assertNotIn("porte_crypte", catalogue(self.m)["marchand"]["sujets"])
        self.m.joueur["salle"] = "antichambre"
        self.assertEqual(self.m.contexte()["connaissances_pnj"], {})
        self.assertEqual(catalogue(self.m), {})
        with self.assertRaises(ErreurMonde):
            preparer_savoirs(self.m, ajout())

    def test_persistance_apres_oubli_conversation_et_non_remplacement(self):
        avant = copy.deepcopy(self.m.data)
        m = preparer_savoirs(self.m, ajout())
        self.assertEqual(self.m.data, avant)
        self.assertEqual(m.objets, self.m.objets)
        self.assertEqual(m.joueur, self.m.joueur)
        self.assertEqual(m.data["engagements"], self.m.data["engagements"])
        m.data["conversation"] = []
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "partie.json"
            m.sauver(p)
            m = Monde.charger(p)
        self.assertEqual(m.data["savoirs_pnj"]["marchand"]["lien_anneau"],
                         {"texte": TEXTE, "origine": "MJ", "revision": 1})
        self.assertNotIn("lien_anneau", catalogue(m)["marchand"]["sujets"])
        with self.assertRaises(ErreurMonde):
            preparer_savoirs(m, ajout("Un récit différent."))

    def test_validation_atomique_et_pas_de_mecanique_nouvelle(self):
        for p in (
            ajout(sujet="passage_secret"), ajout(sujet="porte_crypte"),
            ajout(personnage="porte"), ajout(texte=""), ajout(texte="x" * 601),
            {**ajout(), "or": 100}, {"personnage": "marchand", "savoirs": ajout()["savoirs"] * 2},
            {"personnage": "marchand", "savoirs": [*ajout()["savoirs"], {"sujet": "nouvelle_cle", "texte": "Une clé magique."}]},
        ):
            with self.subTest(p=p):
                avant = copy.deepcopy(self.m.data)
                with self.assertRaises(ErreurMonde):
                    preparer_savoirs(self.m, p)
                self.assertEqual(self.m.data, avant)
        with self.assertRaises(ErreurMonde):
            preparer_savoirs(self.m, ajout(), revision=999)

    def test_migration_et_autre_personnage_savoirs_distincts(self):
        d = copy.deepcopy(self.m.data)
        for cle in ("savoirs_pnj", "sujets_savoirs_pnj", "savoirs_version", "ajouts_savoirs"):
            d.pop(cle)
        d["objets"]["mira"] = objet("mira", "Mira", "personnage", "echoppe")
        m = Monde(d)
        self.assertEqual(Monde(copy.deepcopy(m.data)).data, m.data)
        m = preparer_savoirs(m, ajout("Mira a appris la couture auprès de sa famille.", "apprentissage_metier", "mira"))
        self.assertNotIn("porte_crypte", m.data["savoirs_pnj"]["mira"])
        self.assertNotIn("apprentissage_metier", m.data["savoirs_pnj"]["marchand"])
        m.data["sujets_savoirs_pnj"]["mira"] = {}
        self.assertNotIn("mira", catalogue(Monde(copy.deepcopy(m.data))))

    def test_narration_recoit_savoirs_valides_et_ne_modifie_pas_original(self):
        def appel(instructions, entree, intention, fonction, schema):
            if "conversation_validee" not in entree["faits"]:
                return proposition()
            self.assertEqual(entree["faits"]["connaissances_pnj"]["marchand"]["lien_anneau"]["texte"], TEXTE)
            self.assertEqual(entree["faits"]["conversation_validee"]["personnage"], "marchand")
            self.assertEqual(schema["properties"]["mode"]["enum"], ["dialogue"])
            return dialogue()
        avant = copy.deepcopy(self.m.data)
        with patch.object(MJOpenAI, "_appeler", side_effect=appel) as appels:
            r = MJOpenAI().echanger(self.m, "Gorm, pourquoi cet anneau ?")
        self.assertEqual(appels.call_count, 2)
        self.assertIn("_savoirs", r)
        self.assertNotIn("_conversation_pnj", r)
        self.assertEqual(self.m.data, avant)

    def test_echec_narration_ne_persiste_aucun_savoir(self):
        for r in (ErreurMonde("réseau"), {**dialogue(), "texte": ""}, proposition()):
            avant = copy.deepcopy(self.m.data)
            with patch.object(MJOpenAI, "_appeler", side_effect=[proposition(), r]), self.assertRaises(ErreurMonde):
                MJOpenAI().echanger(self.m, "Pourquoi cet anneau ?")
            self.assertEqual(self.m.data, avant)

    def test_boucle_sauve_avant_affichage_et_reutilise_apres_redemarrage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            self.m.sauver(path)
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "_appeler", side_effect=[proposition(), dialogue()]), patch("builtins.input", side_effect=["Gorm, pourquoi cet anneau ?", "quitter"]), patch("sys.stdout", io.StringIO()):
                jeu.main(["--console", "--connexion", "api", "--save", str(path)])
            m = Monde.charger(path)
            self.assertEqual(m.data["savoirs_pnj"]["marchand"]["lien_anneau"]["texte"], TEXTE)
            m.data["conversation"] = []
            def appel(instructions, entree, intention, fonction, schema):
                self.assertEqual(entree["faits"]["connaissances_pnj"]["marchand"]["lien_anneau"]["texte"], TEXTE)
                self.assertNotIn("lien_anneau", entree["faits"]["connaissances_a_completer"]["marchand"]["sujets"])
                return dialogue()
            with patch.object(MJOpenAI, "_appeler", side_effect=appel):
                MJOpenAI().echanger(m, "Rappelle-moi pourquoi tu veux cet anneau.")

    def test_sauvegarde_impossible_n_affiche_pas_nouveau_recit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partie.json"
            self.m.sauver(path)
            avant = path.read_bytes()
            sauver = Monde.sauver
            def echec(m, p):
                if "lien_anneau" in m.data["savoirs_pnj"]["marchand"]:
                    raise OSError("disque indisponible")
                return sauver(m, p)
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), patch.object(MJOpenAI, "_appeler", side_effect=[proposition(), dialogue()]), patch.object(Monde, "sauver", echec), patch("builtins.input", side_effect=["Gorm, pourquoi cet anneau ?", "quitter"]), patch("sys.stdout", io.StringIO()) as sortie:
                jeu.main(["--console", "--connexion", "api", "--save", str(path)])
            self.assertNotIn("mon ancien métier", sortie.getvalue())
            self.assertEqual(path.read_bytes(), avant)

    def test_comparaison_isole_les_inventions(self):
        fini = Event()
        c = Comparateur(MJOpenAI("principal"), MJOpenAI("secondaire"),
                        publier=lambda f: fini.set() if f["secondaire"]["statut"] == "Terminé" else None)
        avant = copy.deepcopy(self.m.data)
        autre = "Gorm tient à cet anneau comme symbole d'une promesse personnelle."
        try:
            with patch.object(c.principal, "_appeler", side_effect=[proposition(), dialogue()]), patch.object(c.secondaire, "_appeler", side_effect=[proposition(ajout(autre)), dialogue()]):
                r = c.echanger(self.m, "Pourquoi cet anneau ?")
                self.assertTrue(fini.wait(2))
            m = preparer_savoirs(self.m, r["_savoirs"]["proposition"])
            c.noter_savoirs(r["texte"], r["_savoirs"]["proposition"])
            self.assertEqual(m.data["savoirs_pnj"]["marchand"]["lien_anneau"]["texte"], TEXTE)
            self.assertEqual(c.fiches[1]["secondaire"]["reponse"]["_savoirs"]["proposition"]["savoirs"][0]["texte"], autre)
            self.assertIn("CONNAISSANCES ENREGISTRÉES", texte_comparaison(c.fiches[1]))
            self.assertIn("CONNAISSANCES PROPOSÉES", texte_comparaison(c.fiches[1]))
            self.assertEqual(self.m.data, avant)
        finally:
            c.fermer()
