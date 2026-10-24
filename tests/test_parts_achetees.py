"""Ce qu'on achète et ce qu'on sait avoir (relevés du banc Luna du soir) : une part de combustible
achetée est remise à l'acheteur, seule une part demandée pour un feu va au feu
(``echanges._vendre_part``) ; on sait ce qu'on porte et ce qui est à soi à portée de main quand on
vous demande si vous en avez (``echanges.siens_a_portee``).

Chaque test vérifie l'état du monde, et ce que le joueur lit, après rechargement.
"""
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon.biens import bourse
from donjon.deplacement_objet import deplacer
from donjon.esprits import lire, percevoir_tous
from donjon.monde import Monde
from donjon.paroles import preparer_parole
from donjon.spatial import porte_par
from tests.support import calme, regarder
from tests.test_tensions import placer, recharger, relais, vivre


def antichambre_du_banc():
    """Le banc Luna ``ressources`` (``tests/data/bancs/ressources.json``) : Corvus dans l'antichambre,
    Aubin devant lui, tourné vers le nord, ses planches dans son dos (il ne les a pas regardées)."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    m.joueur.update(salle="antichambre", position=[1, 3], orientation="sud")
    for qui, salle, case, orientation in (("aubin", "antichambre", (1, 4), "nord"),
                                          ("brune", "antichambre", (0, 3), "est"),
                                          ("ilse", "antichambre", (3, 5), "nord-ouest"),
                                          ("marchand", "echoppe", (4, 1), None)):
        placer(m, qui, salle, case)
        if orientation:
            m.objets[qui]["orientation"] = orientation
    percevoir_tous(m)
    m = recharger(m)
    assert "planches" not in lire(m, "aubin")["croyances"]
    return m


def parole(qui, texte, type_, sujet, valeur=""):
    return {"personnage": qui, "replique": texte, "_intention": "je lui dis : " + texte,
            "contenu": [{"type": type_, "sujet": sujet, "attribut": "", "valeur": valeur}]}


class PartAcheteeTests(unittest.TestCase):
    def test_une_planche_achetee_a_aubin_est_remise_a_corvus(self):
        # Cas réel : « je paie Aubin trois pièces pour une de ses planches » ; le moteur disait « il va
        # entretenir le feu », et Corvus payait sans rien recevoir.
        m = antichambre_du_banc()
        travail, rapport = preparer_parole(m, parole("aubin", "Je te paie trois pièces pour une de tes planches.",
                                                     "demande", "planches", "3"))
        self.assertIn("Aubin, vieux passeur prend tes 3 pièces et ira chercher une part des planches de bac pour "
                      "te la remettre.", rapport["faits"])
        m = recharger(travail)
        self.assertEqual((m.joueur["or"], bourse(m, "aubin"), m.objets["planches"]["charges"]), (21, 9, 1))
        self.assertEqual([x["condition"] for x in lire(m, "aubin")["engagements"]],
                         [{"objet": "planches_1", "remettre": "joueur"}])
        self.assertNotIn({"objet": "brasero", "allume": True}, [x["condition"] for x in lire(m, "aubin")["engagements"]])
        m, lignes = vivre(m, 3)
        self.assertIn("Aubin te remet les planches de bac : tu l'avais payé.", lignes)
        self.assertTrue(porte_par(m, "planches_1", "joueur"))
        self.assertEqual((m.objets["planches_1"]["proprietaire"], m.objets["planches_1"]["charges"]), ("joueur", 1))
        self.assertEqual(lire(m, "aubin")["engagements"], [])

    def test_une_part_des_fagots_de_joss_est_remise_a_corvus(self):
        # Autre cas de même nature, à l'auberge : Corvus achète une part des fagots de Joss, posés dans
        # l'étable ; Joss la prend et la lui remet.
        from tests.support import presentes
        m = presentes(calme(creer("auberge", 1985, "fixe"), "joss"), "joss")
        m.objets["fagots_etable"]["charges"] = 3
        placer(m, "joss", "etable", (5, 3))
        m.joueur.update(salle="etable", position=[5, 2])
        regarder(m, "joss", "joueur")
        regarder(m, "joueur", "joss")
        percevoir_tous(m)
        m = recharger(m)
        or_avant = m.joueur["or"]
        travail, rapport = preparer_parole(m, parole("joss", "Je t'achète une part de tes fagots, une pièce.",
                                                     "demande", "fagots_etable", "1"))
        self.assertIn("Joss, palefrenier prend tes 1 pièces et ira chercher une part des fagots de l'écurie pour "
                      "te la remettre.", rapport["faits"])
        m, lignes = vivre(recharger(travail), 3)
        piece = "fagots_etable_1"
        self.assertTrue(porte_par(m, piece, "joueur"), lignes)
        self.assertEqual((m.objets[piece]["proprietaire"], m.objets["fagots_etable"]["charges"]), ("joueur", 2))
        self.assertEqual(m.joueur["or"], or_avant - 1)
        self.assertEqual(lire(m, "joss")["engagements"], [])

    def test_une_part_demandee_sans_payer_va_toujours_au_feu(self):
        # Ce qui ne change pas : la part de bois qu'on demande pour se chauffer, le donneur la met au feu.
        m = antichambre_du_banc()
        # Pour promettre d'entretenir le feu, Aubin doit pouvoir l'allumer lui-même.
        m.objets["briquet"]["lieu"] = "aubin"
        with patch.object(Monde, "d20", return_value=20):
            travail, rapport = preparer_parole(m, parole("aubin", "Aubin, donne-moi un peu de bois.", "demande",
                                                         "planches"))
        self.assertIn("Aubin, vieux passeur accepte de t'en donner une part : il va entretenir le feu.",
                      rapport["faits"])
        m = recharger(travail)
        self.assertIn({"objet": "brasero", "allume": True}, [x["condition"] for x in lire(m, "aubin")["engagements"]])
        self.assertEqual((m.objets["planches"]["charges"], m.joueur["or"]), (2, 24))


class CeQuOnSaitAvoirTests(unittest.TestCase):
    def test_aubin_sait_ses_planches_dans_son_dos(self):
        # Cas réel : « Aubin, as-tu du bois ? » → « non », puis il les vendait au tour suivant.
        m = antichambre_du_banc()
        travail, rapport = preparer_parole(m, parole("aubin", "Aubin, as-tu du bois ?", "ressource", "chaleur"))
        self.assertIn("Aubin, vieux passeur dit avoir les planches de bac dans le refuge du relais.", rapport["faits"])
        m = recharger(travail)
        self.assertEqual(lire(m, "aubin")["croyances"]["planches"]["lieu"]["valeur"], "antichambre")

    def test_joss_sait_les_fagots_qu_il_porte_et_ceux_de_l_etable(self):
        # Autre cas de même nature : Joss, à l'étable, n'a rien regardé ; il porte une part de fagots et
        # sait la réserve posée là, à sa portée.
        m = calme(creer("auberge", 1985, "fixe"), "joss", "mireille")
        lire(m, "joss")["croyances"].pop("fagots_etable", None)
        from donjon.echanges import detacher_part, enqueter
        piece = detacher_part(m, "fagots_etable")
        deplacer(m, piece, "joss")
        placer(m, "joss", "etable", (5, 3))
        placer(m, "mireille", "etable", (5, 2))
        m = recharger(m)
        issue, dit = enqueter(m, "mireille", "joss", "chaleur")
        self.assertEqual((issue, sorted(dit)), ("dit", sorted([("fagots_etable", "etable"), (piece, "joss")])))
        m = recharger(m)
        self.assertEqual(lire(m, "mireille")["croyances"]["fagots_etable"]["lieu"]["valeur"], "etable")


if __name__ == "__main__":
    unittest.main()
