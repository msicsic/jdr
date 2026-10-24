"""Un rendez-vous cesse pour les deux avant la reprise de leur activité."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import appel
from donjon.ecoute import ENTENDU, entendus, rendre
from donjon.esprits import lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import instant
from tests import test_appel_negocie as scenes
from tests.test_appel_negocie import gorm_hele_corvus, gorm_libre_derriere_la_porte
from tests.test_parole_voix import gorm_derriere_la_porte
from tests.test_repli_et_appel import jouer
from tests.test_tensions import chronique, placer, recharger, vivre
from tests.test_voix import appels


def auberge_42():
    # Capture du moteur 5c2ce81, départ tiré, joueur passif au dortoir ; aucun placement corrigé.
    chemin = Path(__file__).with_name("data") / "rendez-vous-auberge-42-500.json.gz"
    with gzip.open(chemin, "rt", encoding="utf-8") as f:
        return recharger(Monde(json.load(f)))


def reprises(m, minutes):
    debut = instant(m)
    bloc, _ = vivre(recharger(m), minutes)
    coupe = recharger(m)
    for _ in range(minutes):
        coupe, _ = vivre(coupe, 1)
    return bloc, coupe, debut


class RendezVousTests(unittest.TestCase):
    def assert_rencontre(self, m, a, b):
        for x, y in ((a, b), (b, a)):
            if x != "joueur":
                for cle in ("rejoint", "rejoindre"):
                    self.assertNotEqual((lire(m, x)[cle] or {}).get("qui"), y)
        retrouvailles = [t for t in chronique(m) if " retrouve " in t and "comme convenu" in t]
        self.assertEqual(len(retrouvailles), 1)

    def assert_decoupage(self, bloc, coupe, debut):
        bloc.verifier()
        coupe.verifier()
        self.assertEqual(bloc.data, coupe.data)
        self.assertEqual(rendre(bloc, entendus(bloc, debut, ENTENDU)),
                         rendre(coupe, entendus(coupe, debut, ENTENDU)))
        self.assertEqual(regarder(bloc), regarder(coupe))
        self.assertEqual(regarder(bloc), regarder(recharger(bloc)))

    def test_capture_reelle_auberge_42_une_retrouvaille_et_la_demande_reprend(self):
        from donjon import pnj
        chroniquer = pnj._chroniquer
        annonces = []

        def annoncer(m, id, texte, nature="geste"):
            if "retrouve" in texte and "comme convenu" in texte:
                for x in ("odile", "anselme"):
                    self.assertIsNone(lire(m, x)["rejoint"])
                    self.assertIsNone(lire(m, x)["rejoindre"])
                annonces.append(texte)
            return chroniquer(m, id, texte, nature)

        with patch.object(pnj, "_chroniquer", annoncer):
            bloc, coupe, debut = reprises(auberge_42(), 10)
        self.assertEqual(len(annonces), 2)  # Une par rejeu du même laps.
        self.assert_decoupage(bloc, coupe, debut)
        self.assert_rencontre(bloc, "odile", "anselme")
        self.assertEqual(len(appels(bloc, "anselme")), 1)
        self.assertTrue(any("Anselme" in t and "une part" in t for t in chronique(bloc)))
        # Le témoin ne doit pas avoir besoin de charger une autre partie pour voir le même récit.
        self.assertEqual(chronique(bloc), chronique(recharger(bloc)))

    def test_relais_appele_qui_vient_et_l_appelant_ne_le_cherche_plus(self):
        m = scenes.JArriveTests().aubin_cherche_gorm_qui_le_hele()
        appelant = "marchand"
        from donjon.pnj import appeler
        appeler(m, appelant, "aubin", [])
        bloc, coupe, debut = reprises(m, 8)
        self.assert_decoupage(bloc, coupe, debut)
        self.assert_rencontre(bloc, appelant, "aubin")
        self.assertEqual(appels(bloc, "aubin"), [])
        self.assertEqual(len(appels(bloc, appelant)), 1)
        self.assertTrue(any("Aubin" in t and "part" in t for t in chronique(bloc)))

    def test_joueur_appelant_et_appele_reprise_sans_luna(self):
        for m, commandes, cle in (
                (gorm_libre_derriere_la_porte(), ("j'appelle Gorm", "viens"), "rejoindre"),
                (gorm_hele_corvus(porte_ouverte=True), ("viens",), "rejoindre")):
            with self.subTest(commandes=commandes):
                for commande in commandes:
                    m, sortie, modeles = jouer(m, commande, [], [])
                    self.assertFalse(modeles)
                self.assertEqual(lire(m, "marchand")[cle]["qui"], "joueur")
                bloc, coupe, debut = reprises(m, 4)
                self.assert_decoupage(bloc, coupe, debut)
                self.assertIsNone(lire(bloc, "marchand")[cle])
                self.assertNotIn("Gorm appelle : « Corvus ? »", chronique(bloc)[-10:])

    def test_joueur_qui_vient_clot_l_attente_apres_rechargement(self):
        m = gorm_derriere_la_porte()
        for commande in ("j'appelle Gorm", "j'arrive", "ouvrir porte"):
            m, sortie, modeles = jouer(m, commande, [], [])
            self.assertFalse(modeles)
        self.assertIsNone(lire(m, "marchand")["rejoint"])
        self.assertIn("Gorm retrouve Corvus, comme convenu.", chronique(m))
        bloc, coupe, debut = reprises(m, 4)
        self.assert_decoupage(bloc, coupe, debut)
        self.assert_rencontre(bloc, "marchand", "joueur")

    def test_appelant_parti_le_rendez_vous_reste_manque(self):
        m = scenes.JArriveTests().aubin_cherche_gorm_qui_le_hele()
        appel.attendre(m, "marchand", "aubin", vient=True)
        appel.venir(m, "aubin", "marchand")
        # Le voyageur ne peut plus venir : le lieu où l'appelant est parti est hors de sa vue.
        placer(m, "marchand", "echoppe", [4, 5])
        m.objets["porte"].update(ouverte=False, verrouillee=True)
        from donjon.esprits import croire
        croire(m, "aubin", "porte", "verrouillee", True, "essai")
        bloc, coupe, debut = reprises(m, 6)
        self.assert_decoupage(bloc, coupe, debut)
        self.assertIn("Gorm cesse d'attendre Aubin, qui avait promis de venir.", chronique(bloc))
        self.assertFalse(any("comme convenu" in t for t in chronique(bloc)))

    def test_dialogue_clot_les_deux_et_ne_clot_pas_un_autre_rendez_vous(self):
        m = scenes.JArriveTests().aubin_cherche_gorm_qui_le_hele()
        appel.attendre(m, "marchand", "aubin", vient=True)
        appel.venir(m, "aubin", "marchand")
        appel.attendre(m, "aubin", "ilse", vient=True)
        # La voie de dialogue appelle ce contrat une fois pour chaque participant.
        from donjon.deliberation import rejoint
        rejoint(m, "marchand", "aubin")
        rejoint(m, "aubin", "marchand")
        m = recharger(m)
        self.assert_rencontre(m, "marchand", "aubin")
        self.assertEqual(lire(m, "aubin")["rejoint"]["qui"], "ilse")

