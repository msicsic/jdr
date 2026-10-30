"""Une charge de lieu partage le poste, la parole et la persistance des biens."""
import copy
import unittest

from donjon import agendas, defense, relations
from donjon.banc_pnj import creer
from donjon.deliberation import choisir
from donjon.esprits import croire, lire, memoriser, percevoir_tous
from donjon.passage import demander_passage, laisser_passer
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import MINUTE
from tests.support import calme, presentes, sans_souci, regarder as orienter
from tests.test_corps_blessable import passer
from tests.test_tensions import placer, recharger


CAS = (("relais", "marchand", "joueur", "antichambre", "echoppe",
        [1, 3], [2, 3], [0, 4], [0, 3]),
       ("auberge", "hugues", "lucien", "cuisine", "cellier",
        [2, 1], [2, 2], [3, 0], [2, 0]))


def epreuve(cas=CAS[0], suspect=True, vu=True, guet=False, obstacle=None):
    scenario, gardien, autre, salle, charge, proche, loin, poste, acces = cas
    m = sans_souci(presentes(creer(scenario, 1985, "fixe")))
    calme(m, *m.data["esprits"])
    # Épreuve déclarée en données ; aucun agenda historique ajouté au scénario.
    for id in m.data["esprits"]:
        p = m.objets[id]["profil"]
        p["pulsions"], p["agendas"] = [], []
        lire(m, id)["pulsions"], lire(m, id)["agendas"] = [], []
        lire(m, id)["intention"] = None
        lire(m, id)["memoire"] = []
    from donjon.geometrie import cases
    from donjon.spatial import _case_libre
    ailleurs = "chambre_cloche" if scenario == "relais" else "salle_commune"
    libres = iter(sorted(c for c in cases(m.data["salles"][ailleurs]) if _case_libre(m, ailleurs, c)))
    for id in m.data["esprits"]:
        if id not in (gardien, autre):
            placer(m, id, ailleurs, next(libres))
    placer(m, gardien, salle, poste)
    m.objets[gardien]["profil"]["agendas"] = [
        {"sorte": "garder", "parametres": {"lieu": charge}}]
    lire(m, gardien).pop("agendas", None)
    agendas.actualiser(m, gardien)
    def deplacer(case):
        if autre == "joueur":
            m.joueur.update(salle=salle, position=list(case), orientation="ouest")
        else:
            placer(m, autre, salle, case)
            m.joueur.update(salle=salle, position=[4, 1], orientation="ouest")
    deplacer(loin)
    orienter(m, gardien, autre)
    percevoir_tous(m)
    if obstacle is not None:
        if obstacle:
            o = "planches" if scenario == "relais" else "marmite"
            m.objets[o].update(lieu=salle, position=acces, position_salle=salle,
                               bloque_passage=True, mobile=False)
            croire(m, gardien, o, "lieu", salle, "vu", salle=salle, case=acces)
        else:
            tiers = next(i for i in m.data["esprits"] if i not in (gardien, autre))
            placer(m, tiers, salle, acces)
            croire(m, gardien, tiers, "lieu", salle, "vu", salle=salle, case=acces)
    if suspect:
        lire(m, gardien)["relations"].pop(autre, None)
        memoriser(m, gardien, {"type": "service_rendu", "de": autre, "preuve": "service-test"})
        memoriser(m, gardien, {"type": "vol_surpris", "auteur": autre,
                              "objet": "cle_reserve" if scenario == "relais" else "ballot"})
    else:
        lire(m, gardien)["relations"].pop(autre, None)
        for n in range(5):
            memoriser(m, gardien, {"type": "service_rendu", "de": autre, "preuve": f"ami:{n}"})
    if guet:
        croire(m, gardien, autre, "intention", "guet", "devine", signe="guet-test", envers=charge)
    if not vu:
        orienter(m, gardien, (2 * poste[0] - proche[0], 2 * poste[1] - proche[1]))
    deplacer(proche)
    percevoir_tous(m)
    return recharger(m)


class InterpositionLieuTests(unittest.TestCase):
    def preuve(self, m):
        rendu, scene = regarder(m), scene_percue(m)
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(rendu, regarder(n))
        self.assertEqual(scene, scene_percue(n))
        return n

    def test_deux_scenarios_poste_parole_persistance_et_recharge(self):
        for cas in CAS:
            _, gardien, autre, salle, charge, _, _, depart, acces = cas
            with self.subTest(scenario=cas[0]):
                m = epreuve(cas)
                avant = copy.deepcopy(m.data)
                r = defense.interposition(m, gardien)
                self.assertEqual(r[0]["objet"], charge)
                self.assertEqual(r[1][0]["contenu"]["position"], acces)
                self.assertEqual(agendas.planifier(m, gardien, "a1"), r)
                self.assertEqual(m.data, avant)
                self.assertEqual(m.objets[gardien]["position"], depart)
                choisir(m, gardien, m.data["minutes"])
                lignes = passer(m, MINUTE)
                m = self.preuve(m)
                self.assertEqual((m.objets[gardien]["lieu"], m.objets[gardien]["position"]), (salle, acces))
                self.assertIn("N'approche pas davantage", " ".join(lignes))
                self.assertEqual(len([s for s in lire(m, gardien)["memoire"] if s["type"] == "mise_en_garde"]), 1)
                from donjon.emissions import pnj as emissions_pnj
                paroles = [p for p in emissions_pnj(m) if p["locuteur"] == gardien
                            and "N'approche pas davantage" in p["texte"]]
                self.assertEqual(len(paroles), 1)
                self.assertIn(autre, paroles[0]["auditeurs"])
                self.assertEqual(paroles[0]["parametres"]["contenu"],
                                 [{"type": "raison", "raison": "mise_en_garde"}])
                self.assertIn(m.objets[gardien]["nom"], regarder(m))
                self.assertIn(gardien, str(scene_percue(m)))
                axes = relations.axes(m, gardien, autre)
                self.assertEqual(laisser_passer(m, gardien, autre)[1], "garde")
                self.assertEqual(demander_passage(m, gardien, autre, []), "mefiance")
                m = self.preuve(m)
                apres = relations.axes(m, gardien, autre)
                self.assertLess(apres["confiance"], axes["confiance"])
                self.assertGreater(apres["rancune"], axes["rancune"])
                self.assertFalse(m.data.get("historique_corps"))

    def test_laps_entier_ou_decoupe_monde_rendu_scene_identiques(self):
        for cas in CAS:
            a = epreuve(cas)
            b = recharger(a)
            passer(a, MINUTE)
            for dt in (13, 87, 210, 290):
                passer(b, dt)
                b = self.preuve(b)
            a = self.preuve(a)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))
            self.assertEqual(scene_percue(a), scene_percue(b))

    def test_approche_non_vue_ou_personne_sure(self):
        for cas in CAS:
            for options in ({"suspect": False}, {"vu": False}):
                m = epreuve(cas, **options)
                self.assertIsNone(defense.interposition(m, cas[1]))
                self.assertFalse(any(s["type"] == "approche_charge" and s["objet"] == cas[4]
                                     for s in lire(m, cas[1])["memoire"]))
                passer(m, MINUTE)
                m = self.preuve(m)
                self.assertFalse(any(s["type"] == "mise_en_garde" for s in lire(m, cas[1])["memoire"]))

    def test_guet_lu_et_garde_endormie(self):
        for cas in CAS:
            m = epreuve(cas, suspect=False, guet=True)
            gardien = cas[1]
            lire(m, gardien)["agendas"][0]["etat"] = "sommeil"
            self.assertEqual(agendas.planifier(m, gardien, "a1")[0]["type"], "interposer")
            passer(m, MINUTE)
            m = self.preuve(m)
            self.assertEqual(m.objets[gardien]["position"], cas[-1])
            self.assertTrue(any(s["type"] == "mise_en_garde" for s in lire(m, gardien)["memoire"]))

    def test_acces_occupe_ou_obstacle_cru_ne_declenche_rien(self):
        for cas in CAS:
            for obstacle in (False, True):
                m = epreuve(cas, obstacle=obstacle)
                _, gardien, autre, salle, _, _, _, _, acces = cas
                m = self.preuve(m)
                self.assertIsNone(defense.interposition(m, gardien))
                passer(m, MINUTE)
                m = self.preuve(m)
                self.assertFalse(any(s["type"] == "mise_en_garde" for s in lire(m, gardien)["memoire"]))
                self.assertFalse(m.data.get("historique_corps"))

    def test_meme_approche_sans_nouvel_avertissement(self):
        for cas in CAS:
            m = epreuve(cas)
            passer(m, MINUTE)
            m = self.preuve(m)
            passer(m, 31 * MINUTE)
            m = self.preuve(m)
            paroles = [c for c in m.data.get("chronique", []) if "s'interpose" in c["texte"]]
            self.assertEqual(len(paroles), 1)
            self.assertEqual(m.objets[cas[1]]["position"], cas[-1])

    def test_gardien_dedans_rejoint_le_seuil_par_la_marche(self):
        m = epreuve()
        placer(m, "marchand", "echoppe", [8, 3])
        m.objets["marchand"]["orientation"] = "est"
        lire(m, "marchand")["memoire"] = [s for s in lire(m, "marchand")["memoire"]
                                           if s["type"] != "approche_charge"]
        m.joueur["position"] = [2, 3]
        percevoir_tous(m)
        m.joueur["position"] = [1, 3]
        percevoir_tous(m)
        m = self.preuve(m)
        self.assertIsNotNone(defense.interposition(m, "marchand"))
        self.assertEqual(m.objets["marchand"]["lieu"], "echoppe")
        lignes = passer(m, MINUTE)
        m = self.preuve(m)
        self.assertEqual((m.objets["marchand"]["lieu"], m.objets["marchand"]["position"]),
                         ("antichambre", [0, 3]))
        self.assertIn("N'approche pas davantage", " ".join(lignes))
        self.assertFalse(m.data.get("historique_corps"))

    def test_reprise_du_meme_poste_ne_repete_pas_la_parole(self):
        for cas in CAS:
            m = epreuve(cas)
            passer(m, MINUTE)
            placer(m, cas[1], cas[3], cas[-2])
            percevoir_tous(m)
            passer(m, MINUTE)
            m = self.preuve(m)
            self.assertEqual(m.objets[cas[1]]["position"], cas[-1])
            self.assertEqual(len([c for c in m.data.get("chronique", []) if "s'interpose" in c["texte"]]), 1)

