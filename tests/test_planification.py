"""Planificateur par recherche : les chaînes que les méthodes écrivaient, et celles qu'aucune
n'écrivait, trouvées à partir des seuls gestes déclarés."""
import unittest

from tests.support import refusee, sans_evacues
from donjon.defi import nouveau_defi
from donjon.esprits import croire, lire, memoriser
from donjon.planification import planifier
from donjon.spatial import installer


def relais(refus=True):
    m = sans_evacues(nouveau_defi())
    if refus:
        refusee(m)
    installer(m)
    return m


def gestes(resultat):
    return [(x["operation"], x["cible"] or x["lieu"], x["outil"]) for x in resultat[1]]


class FaimTests(unittest.TestCase):
    def test_refusee_elle_prend_les_crochets_et_force_la_reserve_sans_temoin(self):
        but, etapes = planifier(relais(), "brune", "faim")
        self.assertEqual(but, {"type": "manger", "objet": "vivres"})
        self.assertEqual(gestes((but, etapes)), [
            ("aller", "echoppe", ""), ("prendre", "crochets", ""), ("aller", "antichambre", ""),
            ("crocheter", "reserve", "crochets"), ("ouvrir", "reserve", ""), ("manger", "vivres", "")])
        self.assertEqual([x["condition"] for x in etapes[3:]], ["sans_temoin"] * 3)

    def test_elle_demande_d_abord_quand_rien_ne_l_en_empeche(self):
        m = relais(refus=False)
        croire(m, "brune", "marchand", "lieu", m.objets["marchand"]["lieu"], "vu")
        m.objets["brune"]["lieu"] = m.objets["marchand"]["lieu"]
        but, etapes = planifier(m, "brune", "faim")
        self.assertEqual(but, {"type": "part", "objet": "vivres", "de": "marchand"})
        self.assertEqual(gestes((but, etapes)), [("demander", "marchand", "vivres")])

    def test_une_part_promise_s_attend_pres_des_vivres(self):
        m = relais(refus=False)
        m.objets["brune"]["lieu"] = "echoppe"
        memoriser(m, "brune", {"type": "promis", "de": "marchand", "objet": "vivres"})
        but, etapes = planifier(m, "brune", "faim")
        self.assertEqual(but["type"], "part")
        self.assertEqual(gestes((but, etapes)), [("aller", "antichambre", "")])

    def test_le_proprietaire_ouvre_avec_sa_cle_et_referme_a_cle(self):
        m = relais()
        m.objets["marchand"]["lieu"] = "antichambre"
        but, etapes = planifier(m, "marchand", "faim")
        self.assertEqual(gestes((but, etapes)), [
            ("deverrouiller", "reserve", "cle_reserve"), ("ouvrir", "reserve", ""), ("manger", "vivres", ""),
            ("fermer", "reserve", ""), ("verrouiller", "reserve", "cle_reserve")])
        self.assertEqual({x["condition"] for x in etapes}, {""})

    def test_qui_ne_vole_pas_ne_trouve_rien_apres_un_refus(self):
        m = relais()
        m.objets["brune"]["profil"]["limites"].append("ne_vole_pas")
        self.assertIsNone(planifier(m, "brune", "faim"))


class LumiereTests(unittest.TestCase):
    def test_dans_le_noir_elle_va_chercher_de_la_lumiere_avant_de_crocheter(self):
        # Aucune méthode ne l'écrit : la chance de crocheter dans le noir rend le détour rentable.
        m = relais()
        m.objets["torche"].update(allume=False, combustible=30)
        croire(m, "brune", "torche", "lieu", "antichambre", "vu")
        croire(m, "brune", "torche", "etat", {"allume": False, "charge": True}, "vu")
        croire(m, "brune", "brasero", "etat", {"allume": True, "charge": True}, "vu")
        croire(m, "brune", "antichambre", "etat", {"eclairee": False}, "vu")
        resultat = planifier(m, "brune", "faim")
        operations = gestes(resultat)
        self.assertIn(("allumer", "torche", "brasero"), operations)
        self.assertLess(operations.index(("allumer", "torche", "brasero")),
                        operations.index(("crocheter", "reserve", "crochets")))

    def test_dans_la_lumiere_elle_ne_fait_pas_de_detour(self):
        m = relais()
        croire(m, "brune", "torche", "lieu", "antichambre", "vu")
        croire(m, "brune", "torche", "etat", {"allume": False, "charge": True}, "vu")
        croire(m, "brune", "antichambre", "etat", {"eclairee": True}, "vu")
        self.assertNotIn("torche", [x[1] for x in gestes(planifier(m, "brune", "faim"))])


class FroidTests(unittest.TestCase):
    def test_un_feu_eteint_se_rallume_avec_une_torche_allumee_au_fanal(self):
        m = nouveau_defi()
        installer(m)
        m.objets["brasero"].update(allume=False)
        for id in ("ilse",):
            croire(m, id, "brasero", "etat", {"allume": False, "charge": True}, "vu")
            croire(m, id, "torche", "lieu", "antichambre", "vu")
            croire(m, id, "torche", "etat", {"allume": False, "charge": True}, "vu")
            croire(m, id, "fanal", "etat", {"allume": True, "charge": True}, "vu")
        m.objets["ilse"]["lieu"] = "antichambre"
        but, etapes = planifier(m, "ilse", "chaleur")
        self.assertEqual(but, {"type": "chaleur", "objet": "brasero"})
        self.assertEqual(gestes((but, etapes)), [
            ("prendre", "torche", ""), ("allumer", "torche", "fanal"), ("aller", "echoppe", ""),
            ("allumer", "brasero", "torche"), ("chauffer", "brasero", "")])

    def test_un_feu_vif_suffit(self):
        m = nouveau_defi()
        installer(m)
        croire(m, "ilse", "brasero", "etat", {"allume": True, "charge": True}, "vu")
        m.objets["ilse"]["lieu"] = "antichambre"
        self.assertEqual(gestes(planifier(m, "ilse", "chaleur")),
                         [("aller", "echoppe", ""), ("chauffer", "brasero", "")])


if __name__ == "__main__":
    unittest.main()
