"""Discours direct, fidélité et secours, dans la console avec recharge."""
from donjon.emissions import joueur as emissions_joueur
import unittest
from donjon.mj import parole_du_moteur
from donjon.paroles import analyser, mots_dits, prevue, SENS_REPLIQUE, SCHEMA_PAROLE
from tests.test_parole_corrections import banc
from tests.test_audits_attendu import jouer, rapport, ligne
from tests.test_repli_et_appel import parole, dialogue
from tests.test_tensions import recharger


class DiscoursIndirectTests(unittest.TestCase):
    def test_transposition_et_operation_conservees(self):
        for saisie, cible, mauvaise, bonne, contenu in (
            ("je demande à Brune si elle a de quoi manger", "brune",
             "Tu demandes à Brune si elle a de quoi manger.", "As-tu de quoi manger ?",
             (("ressource", "faim", "", ""),)),
            ("je lui dis que la porte est forcée", "aubin",
             "je lui dis que la porte est forcée", "La porte est forcée.", ())):
            with self.subTest(saisie=saisie):
                m = banc("ressources")
                cible = prevue(m, saisie)["personnage"]
                def revoir(entree):
                    r = entree["plan"]["parole"]["replique"]
                    return {"conforme": r == bonne, "motif": "La réplique raconte la parole."}
                r, sortie, appels = jouer(m, saisie,
                    [parole(mauvaise, *contenu, personnage=cible),
                     parole(bonne, *contenu, personnage=cible), dialogue("Ta parole est entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))],
                    revues=[revoir, revoir])
                r = recharger(r)
                self.assertIn(bonne, sortie)
                self.assertNotIn(mauvaise, sortie)
                self.assertEqual([p["texte"] for p in emissions_joueur(r)], [bonne])
                self.assertEqual(r.joueur["or"], m.joueur["or"])
                self.assertEqual(r.objets["brune"]["lieu"], m.objets["brune"]["lieu"])
                dossiers = [e["plan"]["parole"] for f, e in appels if f == "auditer_action"]
                self.assertEqual(len(dossiers), 2)
                self.assertEqual([c["type"] for c in dossiers[-1]["contenu"]],
                                 [c[0] for c in contenu])
                self.assertIn("Ta parole est entendue.", str(r.data["conversation"]))

    def test_guillemets_imposes_et_recharges(self):
        m = banc("ressources")
        mots = "Tu demandes à Brune si elle a de quoi manger."
        saisie = 'je dis à Brune : « ' + mots + ' »'
        r, sortie, _ = jouer(m, saisie,
            [parole("Réécriture interdite", personnage="brune"), dialogue("Ta parole est entendue.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))])
        self.assertIn(mots, sortie)
        self.assertEqual(emissions_joueur(recharger(r))[-1]["texte"], mots)

    def test_secours_ne_reprend_pas_le_cadre_narratif(self):
        m = banc("ressources")
        for saisie in ("je demande à Brune si elle a de quoi manger",
                       "je lui dis que la porte est forcée",
                       "Tu demandes à Brune si elle a de quoi manger ?",
                       "je confie à Aubin que je crains la nuit",
                       "Tu expliques à Aubin que la porte est forcée ?"):
            with self.subTest(saisie=saisie):
                secours = parole_du_moteur(m, saisie)
                self.assertEqual(secours["mode"], "dialogue")
                self.assertIsNone(mots_dits(analyser(m, saisie), saisie))
        self.assertEqual(SCHEMA_PAROLE["properties"]["replique"]["description"], SENS_REPLIQUE)

    def test_deux_refus_sans_mots_directs_ne_prononcent_rien(self):
        m = banc("ressources")
        saisie = "je demande à Brune si elle a de quoi manger"
        p = parole("Tu demandes à Brune si elle a de quoi manger.", personnage="brune")
        r, sortie, _ = jouer(m, saisie, [p, p], [],
            revues=[{"conforme": False, "motif": "Cadre narratif."}]*2)
        self.assertFalse(emissions_joueur(recharger(r)))
        self.assertNotIn("Tu dis à", sortie)
        self.assertIn("Précise ce que tu veux dire", sortie)
