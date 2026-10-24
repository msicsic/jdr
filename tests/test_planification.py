"""Planificateur par recherche : les chaînes que les méthodes écrivaient, et celles qu'aucune
n'écrivait, trouvées à partir des seuls gestes déclarés."""
import unittest

from tests.support import refusee, sans_evacues
from donjon.defi import nouveau_defi
from donjon.esprits import croire, lire, memoriser
from donjon.deliberation import REDEMANDE, retenir_refus
from donjon.planification import a_mange, chercher, diagnostics, planifier
from donjon.spatial import installer


def relais(refus=True):
    m = sans_evacues(nouveau_defi(depart="fixe"))
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
        # Promise, la part s'attend près des vivres : le plan l'y mène, et ce temps compte.
        self.assertEqual(gestes((but, etapes)), [("demander", "marchand", "vivres"), ("aller", "antichambre", "")])

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
        m.objets["brune"]["profil"]["valeurs"]["honnetete"] = 100
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


class DemanderTests(unittest.TestCase):
    def test_sans_crochets_elle_demande_la_cle_a_qui_la_porte(self):
        # Aucune méthode ne l'écrit : demander un objet porté est un geste comme un autre.
        m = relais()
        del m.objets["crochets"]
        lire(m, "brune")["croyances"].pop("crochets", None)
        croire(m, "brune", "cle_reserve", "lieu", "marchand", "vu")
        m.objets["marchand"]["lieu"] = "echoppe"
        croire(m, "brune", "marchand", "lieu", "echoppe", "vu")
        self.assertEqual(gestes(planifier(m, "brune", "faim")), [
            ("aller", "echoppe", ""), ("demander", "marchand", "cle_reserve"), ("aller", "antichambre", ""),
            ("deverrouiller", "reserve", "cle_reserve"), ("ouvrir", "reserve", ""), ("manger", "vivres", "")])

    def test_apres_un_refus_elle_ne_redemande_pas(self):
        m = relais()
        # Cette épreuve isole la voie sociale ; une agression est désormais un recours séparé.
        m.objets["brune"]["profil"]["valeurs"]["douceur"] = 100
        del m.objets["crochets"]
        lire(m, "brune")["croyances"].pop("crochets", None)
        croire(m, "brune", "cle_reserve", "lieu", "marchand", "vu")
        retenir_refus(m, "brune", "marchand", "demander", "necessaire", objet="cle_reserve")
        self.assertIsNone(planifier(m, "brune", "faim"))


class FroidTests(unittest.TestCase):
    def test_un_feu_eteint_se_rallume_avec_une_torche_allumee_au_fanal(self):
        m = nouveau_defi(depart="fixe")
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
        m = nouveau_defi(depart="fixe")
        installer(m)
        croire(m, "ilse", "brasero", "etat", {"allume": True, "charge": True}, "vu")
        m.objets["ilse"]["lieu"] = "antichambre"
        self.assertEqual(gestes(planifier(m, "ilse", "chaleur")),
                         [("aller", "echoppe", ""), ("chauffer", "brasero", "")])


class PertinenceTests(unittest.TestCase):
    def test_ce_qui_ne_sert_pas_le_but_n_est_pas_porte_et_le_resultat_reste(self):
        # Aubin a faim, ne sait pas crocheter ; le marchand vient de lui refuser une part. Porter
        # la torche, le bois, les crochets ou le marteau ne change rien : sans les explorer, la
        # recherche aboutit au même résultat, ici aucun plan.
        m = nouveau_defi(depart="fixe")
        installer(m)
        for o in ("torche", "bois", "crochets", "cle", "marteau"):
            croire(m, "aubin", o, "lieu", m.objets[o]["lieu"], "vu")
        for refus in (False, True):
            if refus:
                retenir_refus(m, "aubin", "marchand", "demander", "necessaire", objet="vivres")
                retenir_refus(m, "aubin", "marchand", "proposer", "necessaire", objet="vivres")
            with diagnostics() as recherches:
                complet = chercher(m, "aubin", a_mange)
                borne = chercher(m, "aubin", a_mange, emplois=("manger",))
            self.assertEqual(complet, borne)
            self.assertLess(recherches[1]["noeuds"], recherches[0]["noeuds"])
        self.assertIsNone(borne)


class MemoireTests(unittest.TestCase):
    """Un résultat se reprend sans chercher tant que rien de ce que lit la recherche n'a changé."""

    def test_meme_situation_meme_resultat_sans_chercher(self):
        m = relais()
        with diagnostics() as recherches:
            premier = planifier(m, "brune", "faim")
            second = planifier(m, "brune", "faim")
            second[1].append("modifié par l'appelant")
            troisieme = planifier(m, "brune", "faim")
        self.assertEqual(premier, troisieme)
        self.assertEqual([r["memoire"] for r in recherches], [False, True, True])

    def test_une_croyance_une_limite_ou_l_horloge_relancent_la_recherche(self):
        m = relais()
        crocheter = ("crocheter", "reserve", "crochets")
        self.assertIn(crocheter, gestes(planifier(m, "brune", "faim")))
        # Elle ne sait plus où sont les crochets, puis les revoit.
        croire(m, "brune", "crochets", "lieu", None, "vu")
        self.assertIsNone(planifier(m, "brune", "faim"))
        croire(m, "brune", "crochets", "lieu", "echoppe", "vu")
        self.assertIn(crocheter, gestes(planifier(m, "brune", "faim")))
        # Une honnêteté à son comble : voler n'est plus permis.
        m.objets["brune"]["profil"]["valeurs"]["honnetete"] = 100
        self.assertIsNone(planifier(m, "brune", "faim"))
        # Le refus s'oublie avec le temps : elle peut redemander sa part ; un nouveau refus l'en empêche.
        m.data["minutes"] += REDEMANDE
        self.assertEqual(gestes(planifier(m, "brune", "faim")), [("aller", "echoppe", ""),
                                                                 ("demander", "marchand", "vivres"),
                                                                 ("aller", "antichambre", "")])
        retenir_refus(m, "brune", "marchand", "demander", "necessaire", objet="vivres")
        self.assertIsNone(planifier(m, "brune", "faim"))

    def test_une_nuit_ou_chaque_resultat_repris_ou_borne_est_recalcule(self):
        # Repris de la mémoire, ou cherché parmi ce qu'il vaut la peine de porter : une recherche
        # complète, sur tout ce qu'il connaît, rend le même résultat.
        from donjon import planification
        from donjon.banc_pnj import creer, executer
        from donjon.geometrie import position_entree
        m = creer("relais", 42, "fixe")
        m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
        avant, planification.VERIFIER = planification.VERIFIER, True
        try:
            with diagnostics() as recherches:
                executer(m, 240)
        finally:
            planification.VERIFIER = avant
        self.assertTrue(any(r["memoire"] for r in recherches))


if __name__ == "__main__":
    unittest.main()
