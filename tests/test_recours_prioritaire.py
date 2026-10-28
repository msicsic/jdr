"""Le séjour tarifé par un recours fait partie de son exécution, après recharge.

La capture crue provient du lot 88, nuit 2024 à 645 minutes, sans retouche.
"""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import ecoute, planification, pnj
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.geometrie import cases
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import ecouler, instant
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
    def aide_historique(self, minute):
        fichier = Path(__file__).parent / 'data' / f'aide-240-hameau-1985-{minute}.json.gz'
        return recharger(Monde(json.loads(gzip.decompress(fichier.read_bytes()))))

    def test_aide_historique_adoptee_independante_du_classement(self):
        from donjon import agendas, deliberation as d
        for etat in ('attente', 'presse'):
            m = self.aide_historique(544)
            e = lire(m, 'marchand')
            self.assertEqual(instant(m), 326556)
            self.assertEqual(e['intention']['plan'], [])
            self.assertEqual(agendas.contrat_intention(m, 'marchand')['phase'], 'attendre')
            but = dict(e['intention']['but'])
            e['urgences']['chaleur']['etat'] = etat
            for _ in range(3):
                d.choisir(m, 'marchand', m.data['minutes'])
                self.assertIsNotNone(lire(m, 'marchand')['intention'])
                self.assertEqual(lire(m, 'marchand')['intention']['but'], but)
                self.assertEqual(lire(m, 'marchand')['intention']['plan'], [])
                self.assertEqual(agendas.contrat_intention(m, 'marchand')['phase'], 'attendre')
                self.assertFalse(m.objets['brasero']['allume'])
                n = recharger(m)
                self.assertEqual(m.data, n.data)
                self.assertEqual(vue(m), vue(n))
                m = n
        # Sans attente adoptée ni promesse connue, la seule fin d'un plan ne
        # suffit pas à ouvrir une aide.
        for phase in ('attendre', 'continuer', None):
            m = self.aide_historique(544)
            e = lire(m, 'marchand')
            e['aides_attendues'].clear()
            if phase:
                e['contrat_intention']['contrat']['phase'] = phase
            else:
                e.pop('contrat_intention')
            self.assertIsNone(d._plan_froid(m, 'marchand'))

    def test_aide_capture_541_meme_monde_et_vue_laps_decoupes(self):
        from donjon import deliberation as d
        abandons = []
        choisir = d.choisir

        def observer(m, id, minute):
            avant = lire(m, id)['intention']
            resultat = choisir(m, id, minute)
            apres = lire(m, id)['intention']
            if id == 'marchand' and avant and avant['motif'] == 'chaleur' and not avant['plan']:
                if not apres or apres['motif'] != 'chaleur':
                    abandons.append((instant(m), avant, apres))
            return resultat

        with patch.object(d, 'choisir', observer):
            a = suite(self.aide_historique(541), False, 5)
            b = suite(self.aide_historique(541), True, 5)
        self.assertEqual(abandons, [])
        self.assertEqual(a.data, b.data)
        self.assertEqual(vue(a), vue(b))
        self.assertEqual(vue(a), vue(recharger(a)))
        self.assertEqual(lire(a, 'marchand')['intention']['motif'], 'chaleur')
        self.assertTrue(lire(a, 'marchand')['aides_attendues'])

    @patch("donjon.agendas._naissances", return_value=None)
    def test_capture_reelle_sans_navette_meme_monde_et_vue_decoupes(self, _naissance):
        # Comparer le maintien de l'abri historique, sans projets nouveaux d'autrui.
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

    def test_ronde_possible_avec_une_lumiere_portee_malgre_la_securite_haute(self):
        from donjon.deplacement_objet import deplacer
        m = mine()
        deplacer(m, "lampe_remy", "bram")
        m.objets["lampe_remy"].update(allume=True, proprietaire="bram")
        percevoir_tous(m)
        a = suite(recharger(m), False, 3)
        self.assertGreaterEqual(lire(a, "bram")["visites"].get("puits", -1), 0)
        self.assertTrue(a.objets["lampe_remy"]["allume"])
        self.assertEqual(a.objets["lampe_remy"]["lieu"], "bram")
        self.assertEqual(vue(a), vue(recharger(a)))

    def test_fin_de_plan_rechargee_sejour_seulement_apres_lumiere_constatee(self):
        m = mine()
        placer(m, "bram", "baraquement", (2, 2))
        e = lire(m, "bram")
        # État durable de fin de plan : la suite d'un geste incertain ou
        # d'une livraison a été coupée ; le moteur rechoisit sur le réel.
        e["intention"] = {"but": {"type": "lumiere"}, "motif": "securite",
                          "plan": [], "depuis": 0, "attente": 0}
        percevoir_tous(m)
        a = suite(recharger(m), False, 1)
        i = lire(a, "bram")["intention"]
        self.assertEqual(i["but"], {"type": "lumiere"})
        self.assertEqual(i["plan"][-1]["operation"], "abriter")
        self.assertEqual(a.objets["bram"]["lieu"], "baraquement")
        self.assertNotIn("puits", lire(a, "bram")["visites"])
        self.assertEqual(vue(a), vue(recharger(a)))


if __name__ == "__main__":
    unittest.main()
