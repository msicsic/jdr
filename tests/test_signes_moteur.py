"""G20 : descriptions demandées au MJ, projection courante et publication durable."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon import signes
from donjon.carte import carte
from donjon.esprits import lire
from donjon.monde import ErreurMonde, Monde
from donjon.narration import consigner
from donjon.noms import reference
from donjon.rendu import decrire_signes, regarder
from donjon.scene import scene_percue
from tests.test_audits_attendu import jouer
from tests.test_narration import dialogue
from tests.test_signes import scene, ecarter
from tests.test_tensions import recharger
from tools.banc_parties import preparer


def attitudes():
    donnees = json.loads(Path("tests/data/bancs/attitudes.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        fichier = Path(tmp) / "partie.json"
        preparer(donnees, fichier)
        return Monde.charger(fichier)


class SignesMoteurTests(unittest.TestCase):
    def recharge(self, m):
        texte, scene, plan = regarder(m), scene_percue(m), carte(m)
        avant = copy.deepcopy(m.data)
        r = recharger(m)
        self.assertEqual(regarder(r), texte)
        self.assertEqual(scene_percue(r), scene)
        self.assertEqual(carte(r), plan)
        self.assertEqual(r.data, avant)
        return r

    def test_banc_176_ilse_gorm_et_autre_pnj_sans_audit(self):
        for id, saisie in (("ilse", "Comment va Ilse ?"),
                           ("marchand", "Gorm a l'air de quoi ?"),
                           ("brune", "Brune m'en veut ?")):
            with self.subTest(id=id):
                m = attitudes() if id != "brune" else ecarter(scene(), "brune", "ilse")
                attendu = decrire_signes(m, [id])
                self.assertTrue(signes.textes(m, {id}))
                avant = copy.deepcopy(m.data)
                r, sortie, appels = jouer(m, saisie, [dialogue({"signes_de": [id]})], [])
                self.assertEqual([f for f, _ in appels], ["repondre_au_joueur"])
                self.assertIn(attendu, sortie)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], attendu)
                self.assertEqual(r.data["conversation"][-1]["reponse"], attendu)
                for cle in ("objets", "esprits", "lectures", "minutes", "revision", "paroles_pnj"):
                    self.assertEqual(r.data.get(cle), avant.get(cle), cle)
                self.recharge(r)

    def test_impressions_faillibles_et_plusieurs_personnages(self):
        m = ecarter(scene())
        with patch("donjon.signes._jet", return_value=20):
            signes.lire(m, "joueur")
        self.assertTrue(signes.impressions(m))
        attendu = decrire_signes(m, ["ilse", "brune", "ilse"])
        self.assertIn("semble", attendu)
        self.assertEqual(attendu.splitlines(), list(dict.fromkeys(attendu.splitlines())))
        r, sortie, appels = jouer(m, "Comment vont-ils ?",
            [dialogue({"signes_de": ["ilse", "brune", "ilse"]})], [])
        self.assertEqual(len(appels), 1)
        self.assertIn(attendu, sortie)
        self.recharge(r)

    def test_signe_et_impression_disparaissent_avant_ecriture(self):
        for id, autre in (("ilse", "brune"), ("brune", "ilse")):
            with self.subTest(id=id):
                m = ecarter(scene(), id, autre)
                with patch("donjon.signes._jet", return_value=20):
                    signes.lire(m, "joueur")
                anciens = signes.textes(m, {id})
                self.assertTrue(anciens)
                self.assertTrue(any("semble" in l for l in anciens))

                def ecrire(travail, reponse):
                    self.assertTrue(any(l in reponse["texte"] for l in anciens))
                    travail.joueur["orientation"] = "sud"
                    self.assertFalse(travail.visible(id))
                    consigner(travail, reponse)

                with patch("jeu.consigner_narration", side_effect=ecrire):
                    r, sortie, appels = jouer(m, "Comment va ce personnage ?",
                        [dialogue({"signes_de": [id]})], [])
                self.assertEqual(len(appels), 1)
                texte = r.data["conversation"][-1]["reponse"]
                self.assertEqual(texte, decrire_signes(r, [id]))
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], texte)
                for ligne in anciens:
                    self.assertNotIn(ligne, texte)
                    self.assertNotIn(ligne, sortie.split("Le MJ réfléchit…")[-1])
                self.assertFalse(signes.impressions(r))
                self.recharge(r)

    def test_perception_perdue_garde_le_souvenir_sans_attitude(self):
        m = ecarter(scene())
        anciens = signes.textes(m, {"ilse"})
        regarder(m)
        m.joueur["orientation"] = "sud"
        self.assertFalse(m.visible("ilse"))
        texte = decrire_signes(m, ["ilse"])
        self.assertIn("Tu ne vois pas", texte)
        for ancien in anciens:
            self.assertNotIn(ancien, texte)
        r, sortie, _ = jouer(m, "Comment va Ilse ?", [dialogue({"signes_de": ["ilse"]})], [])
        self.assertIn(texte, sortie)
        self.recharge(r)

    def test_identite_inconnue_reference_publique_uniquement(self):
        m = ecarter(scene())
        m.data["noms_connus"] = []
        ref = reference(m, "ilse")
        self.assertNotEqual(ref, "ilse")
        texte = decrire_signes(m, [ref])
        self.assertNotIn("Ilse", texte)
        with self.assertRaises(ErreurMonde) as exc:
            decrire_signes(m, ["ilse"])
        self.assertIn("texte.signes_de", exc.exception.attendu)
        r, sortie, appels = jouer(m, "Quelle est son attitude ?", [dialogue({"signes_de": [ref]})], [])
        self.assertIn(texte, sortie)
        self.assertEqual(len(appels), 1)
        self.recharge(r)

    def test_selection_invalide_corrigee_sans_effet(self):
        m = ecarter(scene())
        for selection in ([], ["absent_invente"], "ilse", [None], ["ilse"] * 13):
            with self.subTest(selection=selection):
                with self.assertRaises(ErreurMonde) as exc:
                    decrire_signes(m, selection)
                self.assertTrue(exc.exception.attendu)
        r, sortie, appels = jouer(m, "Comment va Ilse ?",
            [dialogue({"signes_de": ["absent_invente"]}), dialogue({"signes_de": ["ilse"]})], [])
        self.assertEqual(len(appels), 2)
        self.assertIn(decrire_signes(r, ["ilse"]), sortie)
        self.recharge(r)

    def test_texte_sur_disque_avant_affichage(self):
        m = ecarter(scene())
        attendu = decrire_signes(m, ["ilse"])
        sauver = Monde.sauver
        imprimer = print
        fichiers, publications = [], []

        def sauvegarder(monde, chemin):
            sauver(monde, chemin)
            fichiers.append(chemin)

        def publier(*args, **kwargs):
            if args == (attendu,):
                sauve = Monde.charger(fichiers[-1])
                self.assertEqual(sauve.data["conversation"][-1]["reponse"], attendu)
                self.assertEqual(sauve.data["narrations_mj"][-1]["texte"], attendu)
                publications.append(attendu)
            imprimer(*args, **kwargs)

        with patch.object(Monde, "sauver", sauvegarder), patch("builtins.print", side_effect=publier):
            r, _, _ = jouer(m, "Comment va Ilse ?", [dialogue({"signes_de": ["ilse"]})], [])
        self.assertEqual(publications, [attendu])
        self.recharge(r)

    def test_prose_libre_garde_audit(self):
        m = ecarter(scene())
        from tests.test_audits_attendu import rapport, ligne
        r, sortie, appels = jouer(m, "Comment va Ilse ?", [dialogue("Une impression vague demeure.")],
                                 [rapport(ligne("ambiance"))])
        self.assertIn("auditer_narration", [f for f, _ in appels])
        self.recharge(r)


if __name__ == "__main__":
    unittest.main()
