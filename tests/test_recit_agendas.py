"""309 : références locales, paramètres et filiation, sans effet de l'observateur.

La fixture est la capture intégrale du lot 306, hameau 42 à la minute 5,
compressée sans modification (hameau-42-final-monde.json).
"""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon import agendas
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.paroles import engagements_enregistres
from donjon.recit_pnj import Recit, but_en_mots
from donjon.rejeu import Enregistreur
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_tensions import recharger, relais
from tools.audit_nuits import _releve


def capture():
    p = Path(__file__).parent / "data/agenda-309-hameau-42-minute-5.json.gz"
    return Monde(json.loads(gzip.decompress(p.read_bytes())))


class RecitAgendasTests(unittest.TestCase):
    def verifier(self, m, acteur, attendu):
        avant = copy.deepcopy(m.data)
        rendu, scene = regarder(m), scene_percue(m)
        but = copy.deepcopy(lire(m, acteur)["intention"]["but"])
        textes = []
        for n in (m, recharger(m)):
            self.assertEqual(n.data, avant)
            self.assertEqual(regarder(n), rendu)
            self.assertEqual(scene_percue(n), scene)
            mots = but_en_mots(n, but, titulaire=acteur)
            self.assertEqual(mots, attendu)
            self.assertEqual(_releve(n)["pnj"][acteur]["b"], attendu)
            recit = Recit(n)
            recit._episode(n, acteur, n.data["minutes"])
            recit.clore(n)
            self.assertIn(attendu, recit.texte(n, []))
            ep = recit.donnees(n, [])["episodes"][acteur][0]
            self.assertEqual(ep["mots"], attendu)
            self.assertEqual(ep["but"], but)
            self.assertIn("intention en cours : " + attendu,
                          engagements_enregistres(n, acteur))
            rejeu = Enregistreur(n)
            rejeu._penser(n, acteur)
            self.assertEqual(rejeu._esprit[f"{acteur}|:but"][0], attendu)
            self.assertEqual(n.data, avant)
            textes.append(recit.texte(n, []))
        self.assertEqual(textes[0], textes[1])

    def test_capture_306_agenda_sans_cible_et_sous_mandat(self):
        m = capture()
        self.assertEqual(m.data["minutes"], 5)
        self.assertEqual(lire(m, "aubin")["intention"]["but"],
                         {"type": "agenda", "agenda": "a1"})
        charge = "amener (lieu : Galerie de ronde ; qui : Brune)"
        self.verifier(m, "aubin", charge + " — mandat : Gorm/evacuer_crue → Aubin/a1")
        self.verifier(m, "ilse", charge + " — mandat : Gorm/evacuer_crue → Aubin/a1 → Ilse/a1")

    def declarer(self, sorte, parametres):
        m = relais()
        m.objets["aubin"]["profil"]["agendas"] = [
            {"id": "projet", "sorte": sorte, "parametres": parametres}]
        agendas.actualiser(m, "aubin")
        self.assertEqual(agendas.projets(m, "aubin")[0]["sorte"], sorte)
        return m, "aubin", "projet"

    def test_chaque_sorte_avec_et_sans_champs_du_sous_but(self):
        from tests.test_agendas_evenement import scene as spoliation
        from tests.test_agendas_naissance import scene as dette
        scenes = [
            (*self.declarer("amener", {"qui": ["ilse", "brune"], "lieu": "chambre_cloche"}),
             "amener (lieu : Galerie de ronde ; qui : Ilse, Brune)"),
            (*self.declarer("informer", {"qui": ["ilse"], "avis": {
                "type": "avis", "objet": "antichambre", "attribut": "menace", "valeur": True}}),
             'informer (avis : {"attribut": "menace", "objet": "antichambre", "type": "avis", "valeur": true} ; qui : Ilse)'),
            (*self.declarer("garder", {"lieu": "antichambre"}),
             "garder (lieu : Refuge du relais)"),
            (*self.declarer("protéger", {"qui": "ilse"}), "protéger (qui : Ilse)"),
        ]
        m = dette()
        agendas.actualiser(m, "odon")
        a = agendas.projets(m, "odon")[0]
        self.assertEqual(a["sorte"], "obtenir")
        scenes.append((m, "odon", a["id"], "obtenir (pieces : 40)"))
        m, acteur, auteur, objet = spoliation(autre=True)
        agendas.actualiser(m, acteur)
        a = agendas.projets(m, acteur)[0]
        self.assertEqual(a["sorte"], "récupérer")
        scenes.append((m, acteur, a["id"],
                       "récupérer (objet : marteau ; prix_cru : 7 ; qui : Brune)"))
        for m, acteur, identifiant, attendu in scenes:
            for champs in ({}, {"qui": "brune"}, {"objet": "brasero"}, {"pieces": 999}):
                with self.subTest(sorte=attendu, champs=champs):
                    lire(m, acteur)["intention"] = {
                        "but": {"type": "agenda", "agenda": identifiant, **champs},
                        "motif": "agenda", "plan": [], "depuis": m.data["minutes"], "attente": 0}
                    self.verifier(m, acteur, attendu)

    def test_reference_inconnue_ou_titulaire_non_precise_sans_deviner(self):
        m = capture()
        avant = copy.deepcopy(m.data)
        but = {"type": "agenda", "agenda": "a1"}
        self.assertEqual(but_en_mots(m, but), json.dumps(but, ensure_ascii=False, sort_keys=True))
        self.assertEqual(but_en_mots(m, but, titulaire="seve"),
                         json.dumps(but, ensure_ascii=False, sort_keys=True))
        # a1 de Brune n'est pas a1 d'Aubin ou d'Ilse.
        self.assertEqual(but_en_mots(m, but, titulaire="brune"), "obtenir (pieces : 20)")
        self.assertEqual(m.data, avant)


if __name__ == "__main__":
    unittest.main()
