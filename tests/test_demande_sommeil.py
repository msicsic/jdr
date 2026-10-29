"""Demandes tenues : sommeil sans moyen, réveil sur moyen nouveau, part reçue.

Les captures sont des états réels rechargés, pas des scènes composées pour
l'assertion : Relais 2024 à 117503 (Aubin), mine 1985 à 200 (Remy) avant le
sommeil, et mine 1985 à la première divergence de la part reçue (Josse).
"""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon import agendas, deliberation as d
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger


DATA = Path(__file__).parent / "data"


def capture(nom):
    return Monde(json.loads(gzip.decompress((DATA / nom).read_bytes())))


def etat(m, id):
    e = lire(m, id)
    contrat = agendas.dernier_contrat_intention(m, id) or {}
    return {"intention": copy.deepcopy(e["intention"]),
            "contrat": copy.deepcopy(contrat.get("contrat")),
            "sommeil": copy.deepcopy(m.data.get("demandes_sommeil", {}).get(id, []))}


class DemandeSommeilTests(unittest.TestCase):
    def recharge_visible(self, m):
        avant = copy.deepcopy(m.data), regarder(m), scene_percue(m)
        r = recharger(m)
        self.assertEqual(avant, (r.data, regarder(r), scene_percue(r)))
        return r

    def test_capture_117503_la_demande_d_aubin_survit_a_l_echec(self):
        m = capture("demande-273-relais-117503.json.gz")
        avant = etat(m, "aubin")
        self.assertIsNone(avant["contrat"]["sortie"])
        d.choisir(m, "aubin", m.data["minutes"])
        apres = etat(m, "aubin")
        self.assertIsNotNone(apres["intention"])
        self.assertIsNone(apres["contrat"]["sortie"])
        self.assertEqual(apres["contrat"]["demande"], avant["contrat"]["demande"])
        self.assertIn(apres["contrat"]["phase"], ("continuer", "attendre"))
        self.recharge_visible(m)

    def test_part_recue_continue_la_demande_au_lieu_du_lot(self):
        m = capture("demande-273-fourniture-mine-1985-373.json.gz")
        avant = etat(m, "josse")
        self.assertEqual(avant["intention"]["but"]["objet"], "biscuits")
        self.assertEqual(avant["intention"]["plan"][0]["operation"], "demander")
        candidats = [c.demande for c in d._candidats(m, "josse") if c.demande]
        objets = {(c.get("condition") or {}).get("objet") for c in candidats
                  if (c.get("condition") or {}).get("servir") == "odon"}
        self.assertNotIn("biscuits", objets)
        self.assertIn("biscuits_1", objets)

        d.choisir(m, "josse", m.data["minutes"])
        apres = etat(m, "josse")
        self.assertEqual(apres["intention"]["but"]["objet"], "biscuits_1")
        self.assertEqual(apres["intention"]["plan"],
                         [{"operation": "servir", "cible": "biscuits_1", "outil": "",
                           "lieu": "", "condition": "", "contenu": {"pour": "odon"}}])
        # Le but garde son identité et son palier : la part est un moyen, pas
        # une nouvelle demande.
        self.assertEqual(apres["intention"]["depuis"], avant["intention"]["depuis"])
        self.assertEqual(apres["contrat"]["palier"], avant["contrat"]["palier"])
        self.assertIsNone(apres["contrat"]["sortie"])

    def test_meme_raison_ne_vaut_pas_objet_precis(self):
        m = capture("demande-273-fourniture-mine-1985-373.json.gz")
        raison = {"qui": "odon", "besoin": "faim"}
        lot = {"condition": {"objet": "biscuits", "servir": "odon"}, "raison": raison}
        part = {"condition": {"objet": "biscuits_1", "servir": "odon"}, "raison": raison}
        autre = {"condition": {"objet": "vivres", "servir": "odon"}, "raison": raison}
        self.assertTrue(d._meme_demande_tenue(part, lot, m, "josse"))
        self.assertTrue(d._meme_demande_tenue(autre, lot, m, "josse"))
        # Une mission nomme son objet : même raison ne suffit pas, et une
        # restitution ne suit pas une part d'un autre lot.
        tache = {"condition": {"objet": "biscuits", "remettre": "odon"}, "tache": True}
        tache_part = {"condition": {"objet": "biscuits_1", "remettre": "odon"}, "tache": True}
        tache_autre = {"condition": {"objet": "vivres", "remettre": "odon"}, "tache": True}
        rendre = {"condition": {"objet": "biscuits", "rendre": "odon"}, "tache": True}
        rendre_part = {"condition": {"objet": "biscuits_1", "rendre": "odon"}, "tache": True}
        self.assertTrue(d._meme_demande_tenue(tache_part, tache, m, "josse"))
        self.assertFalse(d._meme_demande_tenue(tache_autre, tache, m, "josse"))
        self.assertFalse(d._meme_demande_tenue(rendre_part, rendre, m, "josse"))
        self.assertFalse(d._meme_demande_tenue(
            tache, {"condition": {"objet": "biscuits", "remettre": "odon"}, "raison": raison},
            m, "josse"))

    def test_sommeil_sans_moyen_puis_reveil_sur_moyen_nouveau(self):
        m = capture("demande-273-sommeil-mine-1985-200.json.gz")
        avant = etat(m, "remy")
        self.assertEqual(avant["intention"]["but"],
                         {"type": "pulsion", "objet": "biscuits", "servir": "josse"})
        self.assertEqual(avant["intention"]["plan"], [])
        self.assertEqual(avant["contrat"]["phase"], "attendre")
        self.assertIsNone(d._reprendre_demande(m, "remy", avant["contrat"]["demande"]))

        d.choisir(m, "remy", m.data["minutes"])
        endormi = etat(m, "remy")
        self.assertEqual(len(endormi["sommeil"]), 1)
        record = endormi["sommeil"][0]
        self.assertEqual(record["palier"], 12)
        self.assertEqual(record["demande"], avant["contrat"]["demande"])
        self.assertTrue(endormi["intention"] is None
                        or endormi["intention"]["but"] != record["but"],
                        "le palier de la demande endormie doit être libéré")
        self.assertIsNone(endormi["contrat"].get("sortie"))

        # Aucun délai ne réveille : les choix répétés à la même minute, sans
        # entrée nouvelle, laissent le sommeil et son empreinte intacts.
        for _ in range(6):
            d.choisir(m, "remy", m.data["minutes"])
        meme_minute = etat(m, "remy")
        self.assertEqual(len(meme_minute["sommeil"]), 1)
        self.assertEqual(meme_minute["sommeil"][0]["entrees"], record["entrees"])
        self.assertTrue(meme_minute["intention"] is None
                        or meme_minute["intention"]["but"] != record["but"])
        m = self.recharge_visible(m)
        self.assertEqual(len(etat(m, "remy")["sommeil"]), 1)

        # Un moyen nouveau, publié dans ses croyances : la demande se réveille
        # avec son but, son palier et sa date d'origine.
        o = m.objets["biscuits"]
        o.update(lieu="remy", proprietaire="remy", portions=1)
        salle, case = m.objets["remy"]["lieu"], m.objets["remy"].get("position")
        croire(m, "remy", "biscuits", "lieu", "remy", "vu", salle=salle,
               case=list(case) if case else None)
        croire(m, "remy", "biscuits", "etat", {"disponible": True}, "vu")
        croire(m, "remy", "josse", "etat", {"faim": True, "mort": False, "conscient": True}, "vu")
        d.choisir(m, "remy", m.data["minutes"])
        reveille = etat(m, "remy")
        self.assertEqual(reveille["sommeil"], [])
        self.assertIsNotNone(reveille["intention"], reveille)
        self.assertEqual(reveille["intention"]["but"], record["but"])
        self.assertEqual(reveille["intention"]["depuis"], record["depuis"])
        self.assertIn(reveille["intention"]["plan"][0]["operation"],
                      ("servir", "aller", "prendre"))
        self.assertEqual(reveille["contrat"]["palier"], record["palier"])
        # Le réveil reprend le palier de la demande et préempte la routine en
        # cours par ce palier ; il ne clôt pas la demande elle-même.
        self.assertNotEqual(reveille["contrat"]["phase"], "finir")
        self.assertNotEqual((reveille["contrat"].get("sortie") or {}).get("cause"), "dementie")
        self.recharge_visible(m)


if __name__ == "__main__":
    unittest.main()
