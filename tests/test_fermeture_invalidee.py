"""Une manœuvre planifiée ne referme jamais un passage devenu libre."""
import copy
import unittest

from donjon import agendas, echanges, force, pnj, planification
from donjon.crue import nouvelle_crue
from donjon.esprits import croire, lire
from donjon.monde import ErreurMonde
from donjon.portes import valider_fermeture
from donjon.rendu import regarder
from donjon.spatial import installer
from tests.support import presentes
from tests.test_social import placer
from tests.test_tensions import recharger


class FermetureInvalideeTests(unittest.TestCase):
    def scene(self, graine, detachee=False):
        m = presentes(nouvelle_crue(graine, depart="fixe"))
        installer(m)
        placer(m, "brune", "crypte", [7, 3])
        m.joueur.update(salle="crypte", position=[6, 3], orientation="est")
        m.data["connus"] = sorted(m.objets)
        m.data["visitees"] = sorted(m.data["salles"])
        # Le plan et la promesse précèdent la disparition du battant.
        condition = {"objet": "porte", "verrouillee": True}
        agendas.prendre(m, "brune", {"condition": condition, "pour": "marchand", "minute": 0})
        croire(m, "brune", "porte", "etat", {"ouverte": True}, "vu")
        porte = m.objets["porte"]
        if detachee:
            from donjon.moteur import Moteur
            for fixation in porte["fixations"]:
                m.objets[fixation]["integrite"] = 0
            Moteur._stabiliser(m, [])
        else:
            porte["integrite"] = 0
            force.briser(m, "porte", "crypte")
        return recharger(m), condition

    def test_geste_perime_ne_corrompt_ni_devis_ni_sauvegarde(self):
        for graine, detachee in ((2024, False), (42, True)):
            with self.subTest(graine=graine, detachee=detachee):
                m, condition = self.scene(graine, detachee)
                self.assertTrue(pnj._accessible(m, "brune", "porte"))
                lignes = []
                resultat = pnj._executer(m, "brune", planification._etape("fermer", "porte"), lignes, [])
                # C'est la copie du devis qui révélait « Passage incohérent ».
                copie = m.copier()
                echanges.devis_service(copie, "brune", condition, "marchand")
                self.assertFalse(resultat)
                self.assertTrue(m.objets["porte"]["ouverte"])
                self.assertFalse(m.objets["porte"]["verrouillee"])
                self.assertTrue(lire(m, "brune")["croyances"]["porte"]["etat"]["valeur"]["ouverte"])
                self.assertFalse(any(" ferme " in x["texte"] for x in m.data.get("chronique", [])))
                avant, texte = copy.deepcopy(m.data), regarder(m)
                n = recharger(m)
                self.assertEqual(n.data, avant)
                self.assertEqual(regarder(n), texte)
                self.assertIn("dégondé" if detachee else "bris", texte.lower())

    def test_refus_materiels_distincts_avec_attendu(self):
        for detachee, champ in ((False, "integrite=0"), (True, "detachee=True")):
            m, _ = self.scene(2024, detachee)
            with self.assertRaises(ErreurMonde) as refus:
                valider_fermeture(m, "porte")
            self.assertIn(champ, refus.exception.attendu)


if __name__ == "__main__":
    unittest.main()
