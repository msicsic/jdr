"""Le rapport d'audit doit montrer les messages texte, même hors appel d'outil."""
import html
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from rapport_fil import _reponse


class MessagesDansLeFil(unittest.TestCase):
    def test_json_texte_integral_visible(self):
        texte = '{"segments":{"0":{"motif":"réponse complète"}}}'
        rendu = _reponse([{'type': 'message', 'role': 'assistant',
                           'content': [{'type': 'output_text', 'text': texte}]}])
        self.assertIn(html.escape(texte), rendu)
        self.assertNotIn('Aucune réponse reçue', rendu)

    def test_balises_retournees_par_llm_ne_sont_pas_executees(self):
        texte = '<script>exemple</script><tool_call>texte à auditer</tool_call>'
        rendu = _reponse([{'type': 'message', 'content': [{'type': 'output_text', 'text': texte}]}])
        self.assertIn(html.escape(texte), rendu)
        self.assertNotIn('<script>', rendu)


if __name__ == '__main__':
    unittest.main()
