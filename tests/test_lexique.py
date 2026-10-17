import unittest

from donjon import lexique
from donjon.monde import nouveau_monde


class LexiqueTests(unittest.TestCase):
    def test_entite_cachee_sans_fondement(self):
        m = nouveau_monde()
        fondement = lexique.corpus(m.contexte())
        # Le marteau est dans l'échoppe, hors de vue : rien de ce que sait Corvus ne le nomme.
        # L'anneau, lui, est nommé par la prémisse : le citer est fondé.
        mentions = lexique.mentions_sans_fondement(
            m, "Derrière la porte, un marteau et l'anneau.", fondement)
        self.assertEqual(mentions, [{"terme": "marteau", "entites": ["marteau"]}])

    def test_entite_percue_et_pluriel(self):
        m = nouveau_monde()
        fondement = lexique.corpus(m.contexte())
        self.assertEqual(lexique.mentions_sans_fondement(m, "La porte et les murs sont froids.", fondement), [])

    def test_terme_long_examine_seul(self):
        m = nouveau_monde()
        # « axe du gond supérieur » contient « axe » : un seul terme examiné.
        fondement = lexique.corpus("axe du gond supérieur")
        self.assertEqual(lexique.mentions_sans_fondement(m, "L'axe du gond supérieur grince.", fondement), [])

    def test_texte_d_un_ajout_persistant_controle_aussi(self):
        from donjon.narration import mentions_proposees
        m = nouveau_monde()
        base = lexique.corpus(m.contexte())
        def detail(nom, texte):
            return {"mode": "etablir_faits", "texte": "", "faits": [], "proposition": {"ajouts": [
                {"type": "detail", "ancrage": "antichambre_murs", "nom": nom, "genre": "f", "texte": texte}]}}
        self.assertTrue(mentions_proposees(m, detail("rayure", "Elle désigne le marteau."), base))
        # Le nom de l'élément créé appartient à l'ajout lui-même.
        self.assertFalse(mentions_proposees(m, detail("trace de marteau", "Un choc ancien."), base))

    def test_fondement_issu_d_un_texte_affiche(self):
        m = nouveau_monde()
        fondement = lexique.corpus(m.contexte(), "Gorm parle d'un anneau du veilleur.")
        self.assertEqual(lexique.mentions_sans_fondement(m, "L'anneau du veilleur t'attend.", fondement), [])


if __name__ == "__main__":
    unittest.main()
