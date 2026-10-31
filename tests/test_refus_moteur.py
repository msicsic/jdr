"""G2 : refus publics exacts, sans explication libre, jusque dans la console et la sauvegarde."""
import copy
import unittest

from donjon.mj import demande_precision
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from tests.test_audits_attendu import jouer
from tests.test_contrats_internes import banc
from tests.test_relances_luna import action, avis, loin_de_la_poutre
from tests.test_repli_et_appel import dialogue
from tests.test_sous_obstacle import passage, scene
from donjon.improvisation import proposition as improviser, issue


class RefusMoteurTests(unittest.TestCase):
    def refus(self, monde, p):
        with self.assertRaises(ErreurMonde) as leve:
            Moteur(monde).preparer(p)
        self.assertTrue(leve.exception.attendu)
        return leve.exception

    def console(self, monde, saisie, reponses, texte, nombre):
        avant = copy.deepcopy(monde)
        reprise, sortie, appels = jouer(monde, "mj " + saisie, reponses, [])
        self.assertEqual([f for f, _ in appels], ["repondre_au_joueur"] * nombre)
        self.assertIn(texte, sortie)
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], texte)
        self.assertEqual(reprise.data["narrations_mj"][-1]["sources"], ["moteur"])
        self.assertEqual(reprise.objets, avant.objets)
        self.assertEqual(reprise.joueur, avant.joueur)
        for cle in ("revision", "minutes", "journal", "jets", "esprits", "paroles_pnj"):
            self.assertEqual(reprise.data.get(cle), avant.data.get(cle), cle)
        self.assertEqual(regarder(reprise), regarder(avant))
        for _, entree in appels[1:]:
            retour = entree.get("faits", {}).get("retour_moteur")
            if retour and retour.get("attendu"):
                self.assertNotIn(retour["attendu"], sortie)
        return reprise, appels

    def test_portee_cas_reel_et_autre_cible(self):
        m = loin_de_la_poutre()
        coup = improviser("coup de pied dans la poutre", issue("Tu frappes la poutre."),
                          cibles=["poutre_conduite"], approche="effort")
        self.console(m, "je donne un coup de pied dans la poutre", [action(coup)],
                     str(self.refus(m, coup)), 1)
        autre = proposition("prendre", "crochets")
        self.console(m, "je prends les crochets", [action(autre)],
                     str(self.refus(m, autre)), 1)

    def test_passage_trop_bas_et_autre_obstacle(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            with self.subTest(scenario=scenario):
                m = scene(scenario, cible)
                m.objets[cible]["passage"]["degagement_cm"] = 10
                p = passage(cible)
                refus = self.refus(m, p)
                self.assertIn("trop bas", str(refus))
                for saisie in ("ramper sous la poutre effondrée", "est-ce que je pourrais passer dessous ?"):
                    self.console(m, saisie, [action(p), action(p)], str(refus), 2)

    def test_forme_persistante_ne_dit_pas_impossible(self):
        from tests.test_improvisation import chant
        invalide = chant()
        invalide["minutes"] = 500
        autre = chant()
        autre["bruit"] = 500
        for p in (invalide, autre):
            with self.subTest(p=p):
                from donjon.refus import RefusDeForme
                m = banc("atelier")
                self.assertIsInstance(self.refus(m, p), RefusDeForme)
                # A3 valide la grammaire avant préparation : une correction de forme, puis repli.
                self.console(m, "je fredonne", [action(p)] * 2, demande_precision(), 2)

    def test_enveloppe_mal_formee_persistante_demande_precision(self):
        self.console(banc("atelier"), "je fredonne", [{"mode": "action"}] * 2,
                     demande_precision(), 2)

    def test_deux_refus_distincts_dans_l_ordre(self):
        m = nouveau_monde()
        for cible in ("torche", "lanterne"):
            m.objets[cible].update(allume=False, combustible=0)
        lire = proposition("lire", "gravure")
        allumer = proposition("allumer", "torche", "briquet")
        refus = [self.refus(m, p) for p in (lire, allumer)]
        self.assertNotEqual(str(refus[0]), str(refus[1]))
        # A5 : allumer substitue un autre geste à lire ; ce candidat ne produit donc
        # pas un second refus du monde. La troisième réponse reprend le geste initial.
        _, appels = self.console(m, "je lis la consigne", [action(lire), action(allumer), action(lire)],
                                 str(refus[0]), 3)
        retour = appels[2][1]['faits']['retour_moteur']
        self.assertEqual(retour['parametres_a_conserver']['action'], 'lire')
        self.assertIn('proposition.action', retour['attendu'])

    def test_refus_de_portee_en_correction_garde_le_premier_refus(self):
        m = loin_de_la_poutre()
        propositions = [proposition("prendre", "objet_inexistant"), proposition("prendre", "crochets")]
        refus = [self.refus(m, p) for p in propositions]
        self.console(m, "je cherche à récupérer les crochets", list(map(action, propositions)),
                     " ".join(map(str, refus)), 2)

    def test_correction_en_prose_ou_avis_ne_remplace_pas_le_refus(self):
        m = banc("atelier")
        p = proposition("prendre", "objet_inexistant")
        for correction in (dialogue("Gorm dit : « Il te faut une échelle. »"),
                           avis("impossible", "Il te faut une échelle."),
                           avis("clarifier", "Quel identifiant vises-tu ?")):
            with self.subTest(mode=correction):
                # Un avis typé est aussi une substitution A5 ; il doit être corrigé
                # sans jamais remplacer le premier refus par sa prose.
                avis_type = correction['mode'] == 'action'
                self.console(m, "je prends la pierre", [action(p), correction, *([action(p)] if avis_type else [])],
                             str(self.refus(m, p)), 3 if avis_type else 2)


if __name__ == "__main__":
    unittest.main()
