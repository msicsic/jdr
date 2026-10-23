"""Prix propres et attentes sociales : décisions, exécution et rendu après sauvegarde."""
import copy
import unittest
from unittest.mock import patch

from donjon import planification as p, relations
from donjon.banc_pnj import creer
from donjon.deliberation import retenir_refus
from donjon.esprits import croire, lire, memoriser, percevoir_tous
from donjon.pnj import _executer, _temoigner, commencer_geste, finir_gestes
from donjon.temps import instant
from tests import test_lumiere_garde as anciennes
from tests.support import calme, lier, regarder
from tests.test_tensions import placer, recharger, relais, vivre


def lien(m, id, autre, **axes):
    lire(m, id)["relations"][autre] = relations._nouvelle(axes, m.data["minutes"])


class GardeTests(unittest.TestCase):
    def test_neutre_valeurs_propriete_et_charge_confiee(self):
        m = relais()
        lire(m, "marchand")["besoins"]["biens"] = 90.0
        m.objets["marchand"]["profil"]["valeurs"].update(ambition=50, loyaute=90)
        lire(m, "marchand")["relations"].clear()
        m = recharger(m)
        self.assertEqual(p.Vue(m, "marchand").prix_gardes["antichambre"], 2)
        m.objets["marchand"]["profil"]["valeurs"]["ambition"] = 0
        self.assertEqual(p.Vue(m, "marchand").prix_gardes["antichambre"], 1)
        # Bram garde la paie confiée : sa loyauté compte, pas son ambition.
        m = anciennes.GardienTests().bram_et_odon()
        m.objets["coffre_paie"]["proprietaire"] = "josse"
        lire(m, "bram")["engagements"].append({"condition": {"objet": "coffre_paie", "verrouillee": True},
                                               "pour": "josse", "minute": 0})
        m.objets["bram"]["profil"]["valeurs"].update(ambition=0, loyaute=50)
        lire(m, "bram")["relations"].clear()
        lire(m, "bram")["besoins"]["biens"] = 90.0
        m = recharger(m)
        self.assertEqual(p.Vue(m, "bram").prix_gardes["bureau"], 2)
        m.objets["bram"]["profil"]["valeurs"]["ambition"] = 100
        self.assertEqual(p.Vue(m, "bram").prix_gardes["bureau"], 2)
        m.objets["bram"]["profil"]["valeurs"]["loyaute"] = 100
        self.assertEqual(p.Vue(m, "bram").prix_gardes["bureau"], 3)

    def test_gorm_et_bram_quittent_moins_le_bien_menace(self):
        for scenario, id, suspect, salle, bien in (
                ("relais", "marchand", "brune", "antichambre", "vivres"),
                ("mine", "bram", "odon", "bureau", "paie")):
            resultats = []
            for mefiant in (False, True):
                with self.subTest(scenario=scenario, mefiant=mefiant):
                    if scenario == "mine":
                        m = anciennes.GardienTests().bram_et_odon()
                    else:
                        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
                        placer(m, id, salle, (6, 3))
                        placer(m, suspect, salle, (7, 3))
                        for x, case in (("aubin", [3, 2]), ("ilse", [4, 2])):
                            placer(m, x, "echoppe", case)
                            lier(m, id, x, True)
                        percevoir_tous(m)
                        for x, case in (("aubin", [3, 2]), ("ilse", [4, 2])):
                            croire(m, id, x, "lieu", "echoppe", "vu", salle="echoppe", case=case)
                    lien(m, id, suspect, confiance=15 if mefiant else 40)
                    lire(m, id)["besoins"].update(biens=30.0, securite=75.0)
                    # Même rendu de présence pour le joueur après rechargement.
                    m = recharger(m)
                    m, lignes = vivre(m, 5)
                    from donjon.geometrie import cases, distance
                    occupes = {tuple(o["position"]) for o in m.objets.values()
                               if o["type"] == "personnage" and o["lieu"] == salle}
                    case = min((c for c in cases(m.data["salles"][salle]) if c not in occupes),
                               key=lambda c: distance(c, (6, 3) if scenario == "relais" else (2, 2)))
                    m.joueur.update(salle=salle, position=list(case))
                    if m.objets[id]["lieu"] == salle:
                        regarder(m, "joueur", id)
                    from tests.support import presentes
                    presentes(m)
                    m = recharger(m)
                    from donjon.rendu import regarder as rendu
                    texte = rendu(m)
                    self.assertIn(bien, m.objets)
                    if mefiant:
                        self.assertEqual(m.objets[id]["lieu"], salle)
                        self.assertIn(m.objets[id]["nom"].split(",")[0], texte)
                    resultats.append(m.objets[id]["lieu"] == salle)
            self.assertEqual(resultats, [False, True], scenario)

    def test_rancune_peur_et_positions_crues_entrent_dans_les_entrees(self):
        m = relais()
        lire(m, "marchand")["besoins"]["biens"] = 90.0
        for r in ({"confiance": 40, "rancune": 80}, {"confiance": 40, "peur": 80}):
            lien(m, "marchand", "brune", **r)
            croire(m, "marchand", "brune", "lieu", "antichambre", "savoir", salle="antichambre", case=[7, 1])
            proche = p.Vue(recharger(m), "marchand")
            avant = p._entrees(proche, {}, p.PROFONDEUR, p.NOEUDS)
            # Déplacer le vrai personnage sans réviser le savoir ne change pas le prix.
            placer(m, "brune", "beffroi", (2, 2))
            self.assertEqual(p.Vue(m, "marchand").prix_gardes, proche.prix_gardes)
            croire(m, "marchand", "brune", "lieu", "beffroi", "savoir", salle="beffroi", case=[2, 2])
            loin = p.Vue(recharger(m), "marchand")
            self.assertGreater(proche.prix_gardes["antichambre"], loin.prix_gardes["antichambre"])
            self.assertNotEqual(avant, p._entrees(loin, {}, p.PROFONDEUR, p.NOEUDS))


class DemandeTests(unittest.TestCase):
    def scene(self, scenario):
        m = relais() if scenario == "relais" else creer("auberge", 1985, "fixe")
        ids = [x for x, o in m.objets.items() if o.get("profil")]
        calme(m, *ids)
        acteur, donneurs, salle = (("ilse", ("aubin", "marchand"), "antichambre") if scenario == "relais"
                                    else ("joss", ("odile", "mireille"), "cuisine"))
        cases = ((6, 3), (5, 3), (7, 3)) if scenario == "relais" else ((3, 3), (2, 3), (4, 3))
        for x, case in zip((acteur, *donneurs), cases):
            placer(m, x, salle, case)
        # Deux objets interchangeables, de même coût, pour éprouver le choix du donneur.
        modele = copy.deepcopy(m.objets["torche"] if scenario == "relais" else m.objets["lanterne_etable"])
        for n, x in enumerate(donneurs):
            o = copy.deepcopy(modele)
            o.update(id=f"source_{n}", nom=f"lampe {n}", genre="f", lieu=x, proprietaire=x, allume=False, masse=1,
                     mobile=True, position=[1, 1], position_salle=salle)
            o.pop("prix", None)
            m.objets[o["id"]] = o
        percevoir_tous(m)
        for x in donneurs:
            lien(m, acteur, x, confiance=40)
            lien(m, x, acteur, confiance=70)
            m.objets[x]["profil"]["valeurs"]["altruisme"] = 100
            croire(m, acteur, x, "lieu", salle, "savoir", salle=salle, case=m.objets[x]["position"])
        for n, x in enumerate(donneurs):
            croire(m, acteur, f"source_{n}", "lieu", x, "savoir", salle=salle, case=m.objets[x]["position"])
        m.joueur.update(salle=salle, position=[6, 4] if scenario == "relais" else [3, 4])
        regarder(m, "joueur", acteur)
        from tests.support import presentes
        presentes(m)
        return recharger(m), acteur, donneurs

    def chercher(self, m, id):
        return p.chercher(m, id, lambda v, e: bool(e.portes & {"source_0", "source_1"}),
                          vises={"prendre": ["source_0", "source_1"]}, memo=["deux_sources"])

    def test_demande_au_donneur_qui_l_a_servi_puis_reception_et_rendu(self):
        for scenario in ("relais", "auberge"):
            with self.subTest(scenario=scenario):
                m, id, donneurs = self.scene(scenario)
                memoriser(m, id, {"type": "recu", "de": donneurs[1], "objet": "source_1", "don": True})
                # Refus d'une autre demande : il n'interdit pas les lampes, mais instruit son attente.
                retenir_refus(m, id, donneurs[0], "demander", "refus", objet="autre_objet")
                m = recharger(m)
                with patch.object(p, "VERIFIER", True):
                    trouve = self.chercher(m, id)
                    self.assertEqual(self.chercher(m, id)[1], trouve[1])  # Mémoire vérifiée.
                etapes = trouve[1]
                self.assertEqual(etapes[0]["cible"], donneurs[1])
                lignes = []
                with patch.object(type(m), "d20", return_value=20):
                    self.assertTrue(_executer(m, id, etapes[0], lignes, []))
                m = recharger(m)
                self.assertEqual(m.objets["source_1"]["lieu"], id)
                self.assertEqual(m.objets["source_0"]["lieu"], donneurs[0])
                self.assertTrue(any("remet" in t for t in lignes), lignes)
                self.assertIn(m.objets[donneurs[1]]["nom"].split(",")[0], "\n".join(lignes))
                from donjon.scene import scene_percue
                visibles = [o for niveau in scene_percue(m)["niveaux"] for o in niveau["objets"]]
                porteur = next(o for o in visibles if o["id"] == id)
                self.assertIn("source_1", [o["id"] for o in porteur["porte"]])
                self.assertNotIn("source_0", [o["id"] for o in porteur["porte"]])

    def test_aucun_acces_a_l_attitude_reelle_de_l_autre(self):
        m, id, donneurs = self.scene("relais")
        autre = donneurs[0]
        avant = relations.chance_demande(m, id, autre)
        lien(m, autre, id, confiance=0, rancune=100, peur=100, dette=100)
        m = recharger(m)
        self.assertEqual(relations.chance_demande(m, id, autre), avant)
        memoriser(m, id, {"type": "don", "a": autre, "objet": "source_0"})
        self.assertGreater(relations.chance_demande(recharger(m), id, autre), avant)

    def test_se_savoir_vu_reste_apres_le_geste_et_invalide_la_memoire(self):
        m = calme(relais(), "marchand", "brune", "aubin", "ilse")
        placer(m, "marchand", "antichambre", (6, 3))
        placer(m, "brune", "antichambre", (7, 3))
        regarder(m, "brune", "marchand")
        regarder(m, "marchand", "brune")
        percevoir_tous(m)
        avant = relations.chance_demande(m, "brune", "marchand")
        v = p.Vue(m, "brune")
        cle = p._entrees(v, {}, p.PROFONDEUR, p.NOEUDS)
        geste = commencer_geste(m, "brune", "crocheter", "reserve", instant(m) + 600)
        self.assertIn("marchand", geste["se_sait_vu"])
        finir_gestes(m, instant(m) + 601)
        m = recharger(m)
        self.assertFalse(m.data["gestes_en_cours"])
        self.assertLess(relations.chance_demande(m, "brune", "marchand"), avant)
        self.assertNotEqual(cle, p._entrees(p.Vue(m, "brune"), {}, p.PROFONDEUR, p.NOEUDS))
        m.data["minutes"] += 121
        self.assertEqual(relations.chance_demande(m, "brune", "marchand"), avant)

    def test_refus_materiel_ne_devient_pas_hostilite_et_bornes(self):
        m, id, donneurs = self.scene("relais")
        autre = donneurs[0]
        avant = relations.chance_demande(m, id, autre)
        retenir_refus(m, id, autre, "demander", "impossible", objet="source_0")
        self.assertEqual(relations.chance_demande(recharger(m), id, autre), avant)
        lien(m, id, autre, confiance=0, rancune=100, peur=100)
        self.assertEqual(relations.chance_demande(m, id, autre), 0.1)
        lien(m, id, autre, confiance=100, affection=100, dette=100)
        self.assertEqual(relations.chance_demande(m, id, autre), 0.9)

    def test_la_memoire_reprend_le_nouveau_choix_du_donneur(self):
        m, id, donneurs = self.scene("auberge")
        with patch.object(p, "VERIFIER", True):
            for prefere in (0, 1, 0):
                for n, autre in enumerate(donneurs):
                    lien(m, id, autre, confiance=90 if n == prefere else 40)
                m = recharger(m)
                self.assertEqual(self.chercher(m, id)[1][0]["cible"], donneurs[prefere])
                self.assertEqual(self.chercher(m, id)[1][0]["cible"], donneurs[prefere])

    def test_porteur_connu_par_son_objet_a_un_a_priori(self):
        m, id, donneurs = self.scene("auberge")
        autre = donneurs[1]
        # Le bien peut être connu alors que son propriétaire n'a jamais été situé.
        lire(m, id)["croyances"].pop(autre, None)
        lire(m, id)["relations"].pop(autre, None)
        v = p.Vue(recharger(m), id)
        self.assertNotIn(autre, v.personnes())
        self.assertEqual(v.chances_demandes[autre], 0.5)

    def test_un_temoin_non_remarque_n_est_appris_qu_en_le_voyant(self):
        m = calme(relais(), "marchand", "brune", "aubin", "ilse")
        placer(m, "marchand", "antichambre", (6, 3))
        placer(m, "brune", "antichambre", (7, 3))
        regarder(m, "marchand", "brune")
        m.objets["brune"]["orientation"] = "est"
        percevoir_tous(m)
        avant = relations.chance_demande(m, "brune", "marchand")
        geste = commencer_geste(m, "brune", "crocheter", "reserve", instant(m) + 600)
        self.assertIn("marchand", geste["temoins"])
        self.assertNotIn("marchand", geste["se_sait_vu"])
        self.assertEqual(relations.chance_demande(recharger(m), "brune", "marchand"), avant)
        regarder(m, "brune", "marchand")
        _temoigner(m, geste)
        _temoigner(m, geste)
        m = recharger(m)
        self.assertLess(relations.chance_demande(m, "brune", "marchand"), avant)
        self.assertEqual(sum(s["type"] == "se_sait_vu" and s["par"] == "marchand"
                             for s in lire(m, "brune")["memoire"]), 1)


if __name__ == "__main__":
    unittest.main()
