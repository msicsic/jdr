"""Identités périmées, frontière publique et refus du menu de corps."""
import copy
import json
import unittest

from donjon import corps, defense
from donjon.commandes import DescripteurPublic
from donjon.gestes_publics import GESTES_CORPS, REACTIONS
from donjon.monde import ErreurMonde, objet
from donjon.moteur import Moteur
from donjon.noms import apprendre, reference
from donjon.spatial import memoriser
from tests import test_corps_publics as support
from tests.test_descripteur_public import vues
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page

placer = support.placer


class CorpsLimitesTests(unittest.TestCase):
    boucle = support.CorpsPublicsTests.boucle

    def test_tous_les_gestes_refusent_la_personne_partie_sans_homonyme(self):
        for geste in sorted(GESTES_CORPS):
            with self.subTest(geste=geste):
                m, cible, _ = support.monde_geste(geste)
                choix = next(c for c in page(m)["corps"]
                             if c["envoye"]["geste"] == geste and c["envoye"]["cible"] == reference(m, cible))
                placer(m.objets[cible], "reserve", [1, 1])
                memoriser(m); vues(m)
                avant = copy.deepcopy(m.data)
                a, lignes, _ = self.boucle(m, [DescripteurPublic(choix["envoye"])])
                self.assertIn("Tu ne vois plus cette cible ici.", lignes)
                self.assertEqual(a.data, avant)

    def test_danger_expire_refus_public_de_toutes_les_reactions(self):
        m, cible, _ = support.monde_geste("riposter")
        choix = [c for c in page(m)["corps"] if c["envoye"]["geste"] in REACTIONS]
        m.data["violences_joueur"] = []
        avant = copy.deepcopy(m.data)
        for c in choix:
            with self.subTest(geste=c["envoye"]["geste"]):
                a, lignes, _ = self.boucle(m.copier(), [DescripteurPublic(c["envoye"])])
                self.assertIn("Cette personne n'est plus un danger perçu.", lignes)
                self.assertEqual(a.data, avant)

    def test_reference_opaque_reste_le_meme_corps_apres_presentation(self):
        m, cible, autre = support.monde_geste("frapper")
        m.data["noms_connus"] = [id for id in m.data["noms_connus"] if id not in (cible, autre)]
        ref = reference(m, cible)
        self.assertNotEqual(ref, cible)
        d = DescripteurPublic(support.clic(m, cible, "frapper", {"methode": "simple", "outil": ""})["envoye"])
        apprendre(m, "joueur", cible)
        a, _, _ = self.boucle(m, [d, "tenter"])
        self.assertEqual(a.data["journal"][-1]["action"]["cible"], cible)
        self.assertLess(corps.pv(a, cible), corps.pv(m, cible))
        self.assertEqual(corps.pv(a, autre), corps.pv(m, autre))

    def test_inconscience_a_reception_suit_la_regle_sans_cible_substituee(self):
        # La règle commune autorise un coup sur une personne sans défense ;
        # l'interface doit annoncer cet état plutôt qu'inventer un refus.
        m, cible, autre = support.monde_geste("frapper")
        d = DescripteurPublic(support.clic(m, cible, "frapper", {"methode": "simple", "outil": ""})["envoye"])
        corps.endormir(m, cible)
        a, lignes, _ = self.boucle(m, [d, "tenter"])
        self.assertIn("sans défense", "\n".join(lignes))
        self.assertLess(corps.pv(a, cible), corps.pv(m, cible))
        self.assertEqual(corps.pv(a, autre), corps.pv(m, autre))

    def test_projection_ne_transmet_ni_personne_cachee_ni_arme_privee(self):
        m, cible, autre = support.monde_geste("frapper")
        secret = copy.deepcopy(m.objets[autre])
        secret.update(id="personne_cachee", nom="IdentiteSecrete", aliases=[])
        placer(secret, "reserve", [1, 1])
        m.objets[secret["id"]] = secret
        m.objets["arme_privee"] = objet("arme_privee", "ArmeSecrete", "outil", cible, usages=["percussion"])
        defense.noter_coup(m, secret["id"], "joueur", True)
        e = etat(m)
        texte = json.dumps(e, ensure_ascii=False)
        for interdit in ("personne_cachee", "IdentiteSecrete", "arme_privee", "ArmeSecrete"):
            self.assertNotIn(interdit, texte)
        self.assertFalse(e["dangers"])
        for niveau in e["scene"]["niveaux"]:
            for o in niveau["objets"]:
                self.assertFalse(set(o) & {"pv", "pv_max", "stats", "profil", "preconditions", "force"})
        for f in e["catalogue_gestes"]["corps"]:
            self.assertLessEqual(set(f), {"geste", "libelle", "champs", "danger"})

    def test_parametres_fautifs_refuses_avec_attendu(self):
        m, cible, _ = support.monde_geste("frapper")
        for geste, p in (("frapper", {"direction": "est"}), ("trainer", {"outil": "moyen_deux"}),
                         ("pousser", {"direction": "secret"}), ("frapper", {"methode": "surprise"}),
                         ("frapper", {"parcours": {"id": "trajet", "pas": ["est"]}}),
                         ("marcher", {"parcours": {"id": "trajet", "pas": ["est"]}, "direction": "est"})):
            with self.subTest(geste=geste, p=p), self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(DescripteurPublic({"geste": geste, "cible": reference(m, cible), "parametres": p}))
            self.assertTrue(refus.exception.attendu)


if __name__ == "__main__":
    unittest.main()
