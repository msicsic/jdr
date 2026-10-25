"""Le séjour tarifé par un recours fait partie de son exécution, après recharge.

La capture crue provient du lot 88, nuit 2024 à 645 minutes, sans retouche.
"""
import gzip
import json
from pathlib import Path
import unittest

from donjon import ecoute, planification, pnj
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.geometrie import cases
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import ecouler
from tests.support import calme
from tests.test_tensions import placer, recharger


def capture():
    return Monde(json.loads(gzip.decompress(
        Path(__file__).with_name("fixtures").joinpath("recours-645.json.gz").read_bytes())))


def mine():
    m = creer("mine", 1985, "fixe")
    ids = [k for k, o in m.objets.items() if o.get("profil")]
    calme(m, *ids)
    # Un gardien sans flamme portable, une ronde encore due près du puits
    # obscur, et un baraquement éclairé dont il connaît la lumière.
    sol = sorted(cases(m.data["salles"]["filon"]))
    for n, k in enumerate(x for x in ids if x != "bram"):
        placer(m, k, "filon", sol[n])
    placer(m, "bram", "puits", sorted(cases(m.data["salles"]["puits"]))[0])
    m.objets["chandelle"].update(allume=False, combustible=0)
    m.objets["porte_bureau"].update(ouverte=True, verrouillee=False)
    m.objets["bram"]["profil"]["pulsions"] = [
        {"besoin": "devoir", "condition": {"lieu": "puits", "periode": 40}}]
    e = lire(m, "bram")
    e["pulsions"] = [None]
    e["besoins"]["securite"] = 90.0
    e["visites"].pop("puits", None)
    m.joueur.update(salle="filon", position=list(sol[-1]))
    percevoir_tous(m)
    for k in ids + ["joueur"]:
        if k != "bram":
            croire(m, "bram", k, "lieu", None, "vu", salle=None, case=None)
    croire(m, "bram", "baraquement", "etat",
           {"eclairee": True, "niveau": 2, "propre": 2}, "vu")
    croire(m, "bram", "puits", "etat",
           {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
    return recharger(m)


def suite(m, decoupe, minutes=30):
    planification._MEMOIRE.clear()
    planification._GRAPHES.clear()
    for dt in ([150] * (minutes * 4) if decoupe else [minutes * 600]):
        pnj.avancer(m, ecouler(m, dt), [], dt)
        m = recharger(m)
    return m


def vue(m):
    return regarder(m), ecoute.rendre(m, ecoute.entendus(m, -1, ecoute.ENTENDU))


def passages(m, id, depuis=0):
    return [c for c in m.data.get("chronique", [])
            if c["pnj"] == id and c["minute"] >= depuis and " passe dans :" in c["texte"]]


class RecoursPrioritaireTests(unittest.TestCase):
    def test_capture_reelle_sans_navette_meme_monde_et_vue_decoupes(self):
        a, b = suite(capture(), False), suite(capture(), True)
        self.assertEqual(a.data, b.data)
        self.assertEqual(vue(a), vue(b))
        self.assertLessEqual(len(passages(a, "aubin", 645)), 12)
        i = lire(a, "aubin")["intention"]
        self.assertEqual(i["motif"], "securite")
        self.assertEqual(i["plan"][-1]["operation"], "abriter")
        self.assertTrue(any(c["pnj"] == "aubin" and "reste dans la lumière" in c["texte"]
                            for c in a.data["chronique"] if c["minute"] >= 645))

    def test_gardien_mine_et_reprise_de_la_ronde_apres_apaisement(self):
        a, b = suite(mine(), False), suite(mine(), True)
        self.assertEqual(a.data, b.data)
        self.assertEqual(vue(a), vue(b))
        self.assertLessEqual(len(passages(a, "bram")), 4)
        self.assertTrue(any("reste dans la lumière" in c["texte"]
                            for c in a.data["chronique"] if c["pnj"] == "bram"))
        # La fin dépend du besoin, jamais d'un délai : une fois rassuré,
        # le gardien peut reprendre sa ronde immédiatement.
        lire(a, "bram")["besoins"]["securite"] = 0.0
        a = suite(recharger(a), False, 3)
        self.assertGreaterEqual(lire(a, "bram")["visites"].get("puits", -1), 30)

    def test_lumiere_portable_ordinaire_sans_sejour_impose(self):
        from tests.test_lumiere import avec_briquet, mine_noire, inquiet
        m = inquiet(avec_briquet(mine_noire()))
        m.objets["lampe_remy"]["allume"] = False
        a = suite(m, False, 3)
        self.assertTrue(a.objets["lampe_remy"]["allume"])
        self.assertEqual(a.objets["lampe_remy"]["lieu"], "remy")
        self.assertTrue(any("allume la lampe de Rémy" in c["texte"] for c in a.data["chronique"]))
        self.assertEqual(vue(a), vue(recharger(a)))


if __name__ == "__main__":
    unittest.main()
