"""Banc multiple : les indicateurs d'une passe et le résumé par variante."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import banc_multi  # noqa: E402


def partie(*tours):
    return {"tours": [{"saisie": "x", "appels": a, "secondes": s, "replis": ["r"] if r else [], "refus": [],
                       "fil": []} for a, s, r in tours]}


class BancMultiTests(unittest.TestCase):
    def test_premier_delta_du_flux_et_absence_de_mesure_sans_delta(self):
        import banc_parties
        from donjon import transport_openai
        from donjon.fournisseurs import Reponse
        from donjon.mj import MJOpenAI
        from donjon.monde import ErreurMonde
        compteur = banc_parties.Compteur(3, fil=True)
        def repondre(demande):
            evenements = ([{'type': 'response.function_call_arguments.delta', 'delta': '{}'}]
                          if demande.intention == 'avec delta' else [])
            resultat = transport_openai.lire_evenements([*evenements,
                {'type': 'response.completed', 'response': {'status': 'completed', 'output': []}}])
            return Reponse({'ok': True}, resultat['output'], {'total_tokens': 7})
        with (patch.object(MJOpenAI, '_appeler_brut', MJOpenAI._appeler_brut),
              patch.object(MJOpenAI, '__init__', MJOpenAI.__init__),
              patch.object(transport_openai, 'lire_evenements', transport_openai.lire_evenements)):
            compteur.installer()
            mj = MJOpenAI(fournisseur=Mock(appeler=repondre))
            for intention in ('avec delta', 'sans delta'):
                self.assertEqual(mj._appeler_brut('', {}, intention, 'f', {}), {'ok': True})
            self.assertIn('premier_jeton', compteur.traces[0])
            self.assertGreaterEqual(compteur.traces[0]['premier_jeton'], 0)
            self.assertNotIn('premier_jeton', compteur.traces[1])
            self.assertLessEqual(compteur.appels[0]['debut'], compteur.appels[0]['fin'])
            self.assertEqual(compteur.appels[1]['tokens'], 7)
            mj.fournisseur.appeler = Mock(side_effect=ErreurMonde('interruption simulée'))
            with self.assertRaisesRegex(ErreurMonde, 'interruption simulée'):
                mj._appeler_brut('', {}, '', 'f', {})
            self.assertEqual(compteur.appels[-1]['tokens'], 0)
            self.assertIsNone(compteur.mesure)

    def test_latence_et_jetons_par_fonction_sans_confondre_revision_et_audit(self):
        p = partie((3, 12., False), (1, 4., False))
        usage = {"input_tokens": 100, "input_tokens_details": {"cached_tokens": 60},
                 "output_tokens": 20, "output_tokens_details": {"reasoning_tokens": 5}}
        p['tours'][0]['fil'] = [
            {"etape": "appel", "fonction": "repondre_au_joueur", "secondes": 5., "premier_jeton": 2.,
             "schema": {"properties": {"mode": {"enum": ["dialogue", "action"]}}}, "usage": usage},
            {"etape": "appel", "fonction": "auditer_narration", "secondes": 3., "usage": usage},
            {"etape": "appel", "fonction": "repondre_au_joueur", "secondes": 4.,
             "entree": {"controle_narratif": []}, "usage": usage}]
        with tempfile.TemporaryDirectory() as dossier:
            f = Path(dossier) / 'mesures.json'
            f.write_text(json.dumps(p), encoding='utf-8')
            m = banc_multi.mesurer([f])
        self.assertEqual(m['mediane_secondes_par_tour'], 8.)
        self.assertEqual(m['fonctions']['interpretation']['premiers_jetons'], [2.])
        audit = m['fonctions']['auditer_narration']
        self.assertEqual((audit['entree'], audit['cache'], audit['sortie'], audit['reflexion']), (100, 60, 20, 5))
        self.assertEqual(m['fonctions']['revision']['appels'], 1)
        self.assertIn('| mesure / auditer_narration | 1 | 1.50 | 25.0%', banc_multi.resumer([('mesure', m)]))

    def test_mesure_d_une_passe(self):
        with tempfile.TemporaryDirectory() as dossier:
            f = Path(dossier) / "a.json"
            f.write_text(json.dumps(partie((2, 10.0, False), (4, 20.0, True), (0, 0.0, False))), encoding="utf-8")
            m = banc_multi.mesurer([f])
        self.assertEqual((m["tours_mj"], m["appels_par_tour"], m["secondes_par_tour"], m["replis"]), (2, 3.0, 15.0, 1))

    def test_resume_moyenne_et_etendue_par_variante(self):
        base = {"appels_par_tour": 3.0, "secondes_par_tour": 10.0, "replis": 0, "tours_refus": 1,
                "obstacles": 4, "cout": 0.1, "reflexion": 1.0, "tours_mj": 31}
        passes = [("avant", {**base, "replis": 0}), ("avant", {**base, "replis": 2}), ("apres", base)]
        tableau = banc_multi.resumer(passes)
        self.assertIn("avant (2 passes)", tableau)
        self.assertIn("| Tours en repli | 1.0 (0.0 – 2.0) | 0.0 |", tableau)


if __name__ == "__main__":
    unittest.main()
