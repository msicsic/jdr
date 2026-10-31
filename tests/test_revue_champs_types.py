"""416 reprise : table exhaustive, distinction typé/cosmétique et recharge."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon.comprehension import champs_types_revue
from donjon.couverture_action import entree, schema, verifier, RapportInvalide
from donjon.mj import MJ
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.moteur import Moteur, Plan, proposition as geste
from donjon.improvisation import proposition, issue, effet
from tests.revue_support import rapport
from tests import test_reprise_fidele as reprise
from tests.test_reprise_fidele import son
from tests.test_paroles import relais


class RevueChampsTypesTests(unittest.TestCase):
    def test_refs_publiques_dans_table_et_schema_puis_comparees_au_moteur(self):
        from donjon.noms import reference
        m = relais()
        plan = Plan(geste("pousser", "brune"), m.data["revision"], "Pousser cette personne.")
        with patch("donjon.noms.connait", return_value=False):
            ref = reference(m, "brune")
            self.assertNotEqual(ref, "brune")
            dossier = entree("je pousse cette personne", plan, m)
            s = schema(plan, m)
            self.assertEqual(dossier["champs_types"]["cible"], ref)
            self.assertNotIn('brune', json.dumps(dossier, ensure_ascii=False).lower())
            self.assertNotIn('brune', json.dumps(s, ensure_ascii=False).lower())
            verifier(rapport(dossier), plan, monde=m)

    def test_chaque_champ_est_obligatoire_et_ne_peut_pas_devenir_cosmetique(self):
        p = proposition("Une manière libre", issue("Une prose libre", [effet("son", "joueur", texte="voix_melodique", valeur=1)]))
        plan = Moteur(nouveau_monde()).preparer(p)
        champs = champs_types_revue(p)
        self.assertIn("reussite.effets.0.texte", champs)
        self.assertIn("reussite.effets.0.valeur", champs)
        self.assertIn("minutes", champs)
        self.assertNotIn("intention", champs)
        self.assertNotIn("reussite.recit", champs)
        self.assertEqual(set(schema(plan)["properties"]["champs_types"]["required"]), set(champs))
        for champ in champs:
            for omission in (True, False):
                with self.subTest(champ=champ, omission=omission):
                    r = rapport(plan, perimetre="nuance_cosmetique")
                    if omission:
                        del r["champs_types"][champ]
                    else:
                        r["champs_types"][champ]["perimetre"] = "nuance_cosmetique"
                    with self.assertRaises(RapportInvalide) as refus:
                        verifier(r, plan)
                    self.assertIn(champ, refus.exception.attendu)

    def test_ecart_type_refuse_meme_avec_verdict_cosmetique_conforme(self):
        plan = Moteur(nouveau_monde()).preparer(son("sifflement"))
        for champ, demande in (("etapes.0.methode", "cri"), ("etapes.0.cible", "cloche")):
            with self.subTest(champ=champ):
                r = rapport(plan, perimetre="nuance_cosmetique", ecarts=[dict(champ=champ, demande=demande)])
                with self.assertRaises(ErreurMonde) as refus:
                    verifier(r, plan)
                self.assertNotIsInstance(refus.exception, RapportInvalide)
                self.assertIn(champ, refus.exception.attendu)
                self.assertEqual(refus.exception.champs_corrigeables,
                                 (champ,) if champ.endswith("methode") else ("",))

    def test_deux_rapports_cosmetiques_mal_classes_ne_font_pas_passer_le_plan(self):
        m = relais()
        plan = Moteur(m).preparer(son("sifflement"))
        r = rapport(plan)
        r["champs_types"]["etapes.0.methode"]["perimetre"] = "nuance_cosmetique"
        avant = copy.deepcopy(m.data)
        mj = MJ(connexion="chatgpt")
        with patch.object(mj, "_appeler_brut", return_value=r) as appels:
            with self.assertRaises(ErreurMonde) as refus:
                mj._auditer_action("je siffle un air joyeux", plan, m.data["revision"], m)
        self.assertEqual(appels.call_count, 2)
        self.assertIn("etapes.0.methode", refus.exception.attendu)
        self.assertIn("retour_revue", appels.call_args.args[1])
        self.assertEqual(m.data, avant)

    def test_fidele_ecart_et_vraie_nuance_dans_la_boucle_et_apres_recharge(self):
        parcours = reprise.RepriseFideleTests()
        for methode, mots in (("sifflement", "je siffle un air joyeux"), ("cri", "je crie de colère")):
            with self.subTest(methode=methode):
                m = relais()
                bon = son(methode)
                plan_bon = Moteur(m).preparer(bon)
                # Vraie nuance : la manière en prose change, les contrats restent égaux.
                bon["justification"] = "un air gai" if methode == "sifflement" else "un cri furieux"
                r, retours, _ = parcours.jouer(m, mots, [bon],
                    [rapport(plan_bon, False, "Nuance de style", "nuance_cosmetique")])
                self.assertFalse(retours)
                self.assertEqual(r.data["sons"][0]["nature"], methode)
                faux = proposition("Une manière sans autorité", issue("Une prose", [effet("son", "joueur", texte="voix_melodique", valeur=1)]))
                plan_faux = Moteur(m).preparer(faux)
                revue = rapport(plan_faux, perimetre="nuance_cosmetique", ecarts=[
                    dict(champ="reussite.effets.0.texte", demande=methode)])
                r, retours, _ = parcours.jouer(m, mots, [faux, bon], [revue, rapport(plan_bon)])
                self.assertTrue(retours)
                self.assertIn("proposition.reussite.effets.0.texte", retours[0]["attendu"])
                self.assertEqual(retours[0]["champs_corrigeables"], [""])
                self.assertEqual(len(r.data["sons"]), 1)
                self.assertEqual(r.data["sons"][0]["nature"], methode)
                self.assertNotIn("notes de ta voix", r.data["conversation"][-1]["reponse"])
