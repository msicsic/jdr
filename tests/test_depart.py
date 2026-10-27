"""Le départ tiré de la graine (``depart.py``) : une règle commune à tous les scénarios. La même
graine donne le même départ, aussi après rechargement ; des graines différentes, des départs
différents dans les bornes ; le tirage ne décale pas les jets ; le même laps, découpé autrement,
donne le même monde ; le banc compte les nuits distinctes."""
import json
import unittest
from unittest.mock import patch

from donjon.auberge import nouveau_auberge
from donjon.banc_pnj import REPERES, creer, executer
from donjon.corps import FAITS
from donjon.crue import nouvelle_crue
from donjon.defi import nouveau_defi
from donjon.depart import DEFAUT, PLAFOND, bornes
from donjon.esprits import lire
from donjon.geometrie import position_entree
from donjon.mine import nouveau_mine
from donjon.spatial import installer
from tests.test_temps_etat import decouper, etat_pnj
from tests.test_tensions import recharger

SCENARIOS = {"relais": (nouveau_defi, "scenario_relais.json"), "crue": (nouvelle_crue, "scenario_crue.json"),
             "mine": (nouveau_mine, "scenario_mine.json"), "auberge": (nouveau_auberge, "scenario_auberge.json")}


def declare(fichier):
    with open(f"donjon/{fichier}", encoding="utf-8") as f:
        return json.load(f)


def depart(m):
    """Ce que le tirage fixe : corps, besoins, rondes (période et dernière visite), horloges."""
    ids = sorted(id for id, o in m.objets.items() if o.get("profil"))
    return {"corps": {id: {k: m.objets[id]["corps"][k] for k in FAITS} for id in ids},
            "besoins": {id: dict(lire(m, id)["besoins"]) for id in ids},
            "visites": {id: dict(lire(m, id)["visites"]) for id in ids},
            "periodes": {id: [x["condition"].get("periode") for x in m.objets[id]["profil"]["pulsions"]] for id in ids},
            "horloges": {h["id"]: h["minute"] for h in m.data.get("horloges", [])}}


class DepartTireTests(unittest.TestCase):
    def test_meme_graine_meme_depart_aussi_apres_rechargement(self):
        for nom, (creer_, _) in SCENARIOS.items():
            with self.subTest(nom):
                a, b = creer_(7), creer_(7)
                self.assertEqual(depart(a), depart(b))
                self.assertEqual(a.data["depart"], b.data["depart"])
                relu = recharger(a)
                self.assertEqual(depart(relu), depart(a))
                self.assertEqual(relu.data["depart"]["tirage"], a.data["depart"]["tirage"])

    def test_un_rechargement_ne_tire_plus_rien(self):
        # Le tirage est fait à la création : ce qui a changé depuis n'est pas retiré au chargement.
        m = nouveau_defi(7)
        lire(m, "brune")["besoins"]["securite"] = 3.0
        m.objets["ilse"]["corps"]["repas"] = 11
        relu = recharger(m)
        self.assertEqual(lire(relu, "brune")["besoins"]["securite"], 3.0)
        self.assertEqual(relu.objets["ilse"]["corps"]["repas"], 11)

    def test_graines_differentes_departs_differents_dans_les_bornes(self):
        for nom, (creer_, fichier) in SCENARIOS.items():
            with self.subTest(nom):
                scenario = declare(fichier)
                mondes = [creer_(g) for g in range(1, 13)]
                self.assertEqual(len({json.dumps(depart(m), sort_keys=True) for m in mondes}), len(mondes))
                fixe = creer_(1, "fixe")
                for m in mondes:
                    self._dans_les_bornes(m, fixe, scenario)

    def _dans_les_bornes(self, m, fixe, scenario):
        b = bornes(m)
        self.assertEqual(set(b), set(DEFAUT))
        self.assertEqual(b, {**DEFAUT, **scenario.get("depart", {}).get("bornes", {})})
        for id, o in scenario["objets"].items():
            if not o.get("profil"):
                continue
            for k in FAITS:
                d = o.get("corps", FAITS)[k]
                self.assertLessEqual(abs(m.objets[id]["corps"][k] - d), b["corps"] * d + 1, (id, k))
            for nom, x in o["profil"]["besoins"].items():
                self.assertLessEqual(abs(lire(m, id)["besoins"][nom] - x["depart"]), b["besoins"] + 1e-9, (id, nom))
            # Personne n'est à l'extrême au départ, sauf déclaré au-delà du plafond.
            for nom, v in lire(m, id)["besoins"].items():
                self.assertLessEqual(v, max(PLAFOND, lire(fixe, id)["besoins"][nom]) + 1e-9, (id, nom))
            for x, y in zip(o["profil"]["pulsions"], m.objets[id]["profil"]["pulsions"]):
                if "periode" not in x["condition"]:
                    continue
                p, q = x["condition"]["periode"], y["condition"]["periode"]
                self.assertLessEqual(abs(q - p), b["periodes"] * p + 1, (id, x))
                # La prochaine ronde tombe dans la première part ``rondes`` de sa période.
                echeance = lire(m, id)["visites"][y["condition"]["lieu"]] + q
                self.assertTrue(0 <= echeance <= b["rondes"] * q, (id, x, echeance))
        for h, g in zip(scenario.get("horloges", []), m.data.get("horloges", [])):
            self.assertLessEqual(abs(g["minute"] - h["minute"]), b["horloges"] * h["minute"] + 1)

    def test_depart_fixe_garde_le_depart_declare(self):
        for nom, (creer_, fichier) in SCENARIOS.items():
            with self.subTest(nom):
                scenario, m = declare(fichier), creer_(42, "fixe")
                self.assertNotIn("tirage", m.data["depart"])
                for id, o in scenario["objets"].items():
                    if o.get("profil"):
                        self.assertEqual(m.objets[id]["profil"]["pulsions"], o["profil"]["pulsions"])
                        self.assertEqual(lire(m, id)["visites"], {})
                        for nom_, x in o["profil"]["besoins"].items():
                            self.assertEqual(lire(m, id)["besoins"][nom_], x["depart"])
                self.assertEqual(m.data.get("horloges"), scenario.get("horloges"))

    def test_le_tirage_ne_decale_pas_les_jets(self):
        tire, fixe = nouveau_defi(1985), nouveau_defi(1985, "fixe")
        self.assertEqual(tire.data["jets"], fixe.data["jets"])
        self.assertEqual([tire.d20() for _ in range(20)], [fixe.d20() for _ in range(20)])

    def test_le_meme_laps_decoupe_donne_le_meme_monde(self):
        # Un départ tiré (graine 7 ; une autre que celle des scènes de ``test_temps_etat``).
        def scene():
            m = nouveau_defi(7)
            installer(m)
            m.joueur.update(salle="chambre_cloche", position=[3, 7], orientation="nord")
            return m
        d_un_bloc, morcele = decouper(scene, 5)
        self.assertEqual(depart(scene())["besoins"], depart(nouveau_defi(7))["besoins"])
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))


class DivergenceDuBancTests(unittest.TestCase):
    def nuit(self, graine, depart="tire", minutes=60, souci=True):
        m = creer("relais", graine, depart)
        if not souci:
            # Comme les marchés/nouvelles déjà isolés dans l'oracle du départ,
            # les secours peuvent tirer des dés de demande indépendants du départ.
            from tests.support import sans_souci
            sans_souci(m)
        m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
        empreintes = {}
        _, mesures = executer(m, minutes, empreintes=empreintes)
        return empreintes, mesures

    def test_empreintes_aux_reperes_et_issue(self):
        a, mesures = self.nuit(3)
        self.assertEqual(set(a), {str(k) for k in REPERES if k <= 60} | {"issue"})
        self.assertEqual(a, self.nuit(3)[0])  # La même graine : la même nuit.
        self.assertEqual(mesures["jets_par_heure"], mesures["jets"])  # Une heure de nuit.

    @patch("donjon.social._constats", return_value=())
    @patch("donjon.agendas._naissances", return_value=None)
    def test_le_depart_tire_fait_diverger_les_nuits(self, _naissance, _constats):
        # Les marchés A6 tirent aussi des dés : le départ seul est l'oracle ici.
        # Comparer les départs seuls ; la persuasion des nouvelles tire aussi des dés.
        # Départ déclaré : une seule nuit jusqu'à la cinquième minute, quelle que soit la graine.
        fixes = {self.nuit(g, "fixe", 5, souci=False)[0]["5"] for g in (1, 2, 3, 4)}
        tirees = {self.nuit(g, "tire", 5, souci=False)[0]["5"] for g in (1, 2, 3, 4)}
        self.assertEqual(len(fixes), 1)
        self.assertGreater(len(tirees), 2)

    def test_la_cloche_confiee_au_joueur_n_est_pas_sans_recours(self):
        # Gorm a confié la cloche au joueur, passif au banc : son devoir urgent, que rien d'autre ne
        # retient, attend le joueur ; il n'est pas compté sans recours.
        from tests.support import calme
        m = calme(creer("relais", 1985, "fixe"), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
        lire(m, "marchand")["besoins"]["devoir"] = 90.0
        m.objets["brasero"]["allume"] = True
        lire(m, "marchand")["croyances"].setdefault("brasero", {})["etat"] = {
            "valeur": {"allume": True}, "source": "vu", "minute": 0, "confiance": 1.0}
        from donjon.banc_pnj import _oisifs_urgents
        oisifs, sans_recours, attente, confies = _oisifs_urgents(m)
        self.assertEqual((oisifs, sans_recours, attente, confies), (1, 0, 0, 1))
        # Qu'il cesse de croire le joueur fiable : la cloche lui revient, il est sans recours.
        from tests.support import lier
        lier(m, "marchand", "joueur", False, "vu")
        self.assertEqual(_oisifs_urgents(m), (1, 1, 0, 0))


if __name__ == "__main__":
    unittest.main()
