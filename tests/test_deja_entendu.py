"""Les témoins retiennent l'audience, sans transformer une parole en vérité."""
import copy
import unittest

from donjon import ecoute, pnj, social
from donjon.esprits import croire, lire
from donjon.rendu import regarder as rendu
from donjon.temps import ecouler
from unittest.mock import patch
from tests.support import regarder
from tests.test_constats_partages import scene
from tests.test_social import placer, recharger


def assemblee():
    m = scene()
    placer(m, "brune", "antichambre", [3, 5])
    for a in ("ilse", "marchand", "brune"):
        for b in ("ilse", "marchand", "brune"):
            if a != b:
                regarder(m, a, b)
                croire(m, a, b, "lieu", "antichambre", "vu", salle="antichambre",
                       case=m.objets[b]["position"])
    return m


def dire(m, noyau):
    lignes = []
    social.faire_entendre(m, "ilse", "marchand", "Ilse : « Les vivres sont épuisés. »",
                         ["vivres"], lignes, [{"type": "rumeur", "evenement": noyau, "rang": 0}])
    return lignes


class DejaEntenduTests(unittest.TestCase):
    def test_constat_temoin_absent_et_changement_apres_recharge(self):
        m = assemblee()
        noyau = {"type": "constat", "objet": "vivres", "attribut": "etat",
                 "valeur": {"disponible": False}, "observe": m.data["minutes"]}
        croire(m, "ilse", "vivres", "etat", noyau["valeur"], "essai")
        dire(m, noyau)
        m = recharger(m)
        for a, b in (("ilse", "brune"), ("brune", "marchand"), ("marchand", "brune")):
            self.assertTrue(social.deja_dit(m, a, b, noyau), (a, b))
        self.assertFalse(social.deja_dit(m, "ilse", "aubin", noyau))
        self.assertFalse(social.deja_dit(m, "brune", "aubin", noyau))
        # Aubin arrive après la parole : le registre ne lui invente aucun savoir.
        placer(m, "aubin", "antichambre", [2, 5])
        regarder(m, "ilse", "aubin")
        croire(m, "ilse", "aubin", "lieu", "antichambre", "vu", salle="antichambre", case=[2, 5])
        from tests.support import lier
        lier(m, "ilse", "aubin", True)
        ecouler(m, 600)
        with patch("donjon.monde.Monde.d20", return_value=20):
            self.assertTrue(social.bavarder(m, "ilse", []))
        self.assertTrue(social.deja_dit(recharger(m), "ilse", "aubin", noyau))
        self.assertEqual(m.objets["vivres"]["portions"], 0)
        ecouler(m, 600)
        m.objets["vivres"]["portions"] = 2
        croire(m, "brune", "vivres", "etat", {"disponible": True}, "vu")
        m = recharger(m)
        self.assertFalse(social.deja_dit(m, "ilse", "brune", noyau))
        self.assertTrue(social.deja_dit(m, "ilse", "marchand", noyau))
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_audience_cachee_non_inventee_et_parole_directe(self):
        from donjon.ouie import retentir
        m = assemblee()
        noyau = {"type": "affirmation", "sujet": "vivres", "attribut": "etat",
                 "valeur": {"disponible": False}}
        # Le canal acoustique commun reçoit aussi les paroles hors bavardage.
        retentir(m, "ilse", "dire", texte="Ilse : « Les vivres sont épuisés. »", cites=["vivres"],
                 parole={"a": ["marchand"], "contenu": [noyau]})
        self.assertTrue(social.deja_dit(recharger(m), "brune", "marchand", noyau))
        # Une présence qui n'est pas connue du témoin reste hors de son suivi.
        with patch("donjon.pnj.pourraient_se_parler", side_effect=lambda m, a, b: b != "marchand"):
            audience = social._audience_connue(m, "ilse", [noyau], "dire", observateur="brune")
        self.assertFalse(any(b == "marchand" for _, b, _ in audience))

    def test_avis_refuse_reste_entendu_sans_devenir_vrai(self):
        from tests.test_disputes import dispute
        m = dispute()
        avis = social.avis_exprime(m, "aubin", "antichambre", True)
        social.faire_entendre(m, "aubin", "marchand", "Aubin prévient Gorm.", [], [],
                             [{"type": "rumeur", "evenement": avis, "rang": 0, "dispute": True}])
        m = recharger(m)
        self.assertTrue(social.deja_dit(m, "aubin", "ilse", avis))
        # Ilse conserve sa preuve contraire ; avoir entendu ne vaut pas adoption.
        contraire = social.avis_exprime(m, "ilse", "antichambre", False)
        self.assertFalse(social.deja_dit(m, "ilse", "aubin", contraire))

    def test_positions_entendues_conservees_sans_ecraser_la_position_dite(self):
        m = assemblee()
        oui = {"type": "affirmation", "sujet": "vivres", "attribut": "etat",
               "valeur": {"disponible": True}}
        non = {**oui, "valeur": {"disponible": False}}
        social.retenir_dit(m, "brune", "marchand", oui)
        social._retenir_audience(m, [("brune", "marchand", non), ("brune", "marchand", oui)])
        m = recharger(m)
        self.assertTrue(social.deja_dit(m, "brune", "marchand", oui))
        self.assertTrue(social.deja_dit(m, "brune", "marchand", non))
        croire(m, "marchand", "vivres", "etat", {"disponible": False}, "vu")
        croire(m, "marchand", "vivres", "etat", {"disponible": True}, "vu")
        m = recharger(m)
        # L'aller-retour appris rouvre aussi une ancienne valeur entendue.
        self.assertFalse(social.deja_dit(m, "brune", "marchand", oui))
        self.assertFalse(social.deja_dit(m, "brune", "marchand", non))

    def test_laps_monde_et_mots_recharges_identiques(self):
        initial = assemblee()
        noyau = {"type": "constat", "objet": "vivres", "attribut": "etat",
                 "valeur": {"disponible": False}, "observe": initial.data["minutes"]}
        dire(initial, noyau)
        resultats = []
        for tranches in ((600,), (150,) * 4):
            m = recharger(initial)
            lignes = []
            for dt in tranches:
                pnj.avancer(m, ecouler(m, dt), lignes, dt)
                m = recharger(m)
            sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
            visible = rendu(m), ecoute.rendre(m, sons)
            self.assertEqual(visible, (rendu(recharger(m)), ecoute.rendre(recharger(m), sons)))
            resultats.append((copy.deepcopy(m.data), visible))
        self.assertEqual(*resultats)
