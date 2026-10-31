"""Mort délibérée : échéance commune, témoins et état/rendu rechargés."""
import unittest
import copy
from unittest.mock import patch
from donjon import corps, tenir
from donjon.banc_pnj import appliquer_etats
from donjon.commandes import analyser
from donjon.esprits import lire, percevoir_tous
from donjon.monde import ErreurMonde, objet
from donjon.moteur import Moteur, proposition
from donjon.pnj import _executer
from donjon.relations import se_mefie
from donjon.rendu import regarder
from donjon.social import nouvelles, recevoir, phrase, _entendu
from donjon.temps import instant
from tests.support import regarder as orienter
from tests.test_trainer import scene
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


class TuerTests(unittest.TestCase):
    def test_parole_conservee_sans_interlocuteur_defunt_apres_recharge(self):
        from donjon import ecoute, ouie
        from donjon.rendu import fiche
        from donjon.scene import scene_percue
        for scenario in ('relais', 'auberge'):
            with self.subTest(scenario=scenario):
                m, c = scene(scenario)
                corps.corps(m, c)['inconscient'] = 0
                # Un appel portant des mots hors du champ visuel est reçu, avant
                # la transition commune de mort (toutes causes confondues).
                m.joueur['orientation'] = 'est'
                percevoir_tous(m)
                self.assertFalse(m.visible(c))
                ouie.retentir(m, c, 'heler', texte='Une voix appelle : « Ici ! »')
                self.assertIn(c, m.data['entendus'])
                voix = copy.deepcopy((m.data.get('voix_entendues'), m.data.get('voix_connues')))
                bruits = copy.deepcopy(m.data['bruits'])
                corps.mourir(m, c)
                self.assertEqual(m.objets[c]['type'], 'depouille')
                self.assertNotIn(c, m.data.get('entendus', []))
                self.assertEqual(m.data['bruits'], bruits)
                self.assertEqual((m.data.get('voix_entendues'), m.data.get('voix_connues')), voix)
                parole = next(b for b in m.data['bruits'] if b['auteur'] == c and b['nature'] == 'hele')
                self.assertIn('Ici !', str(ecoute.rendre(m, [(parole, parole['niveau'], parole['par'])])))
                self.assertTrue(c in m.data.get('voix_entendues', {}) or c in m.data.get('voix_connues', []))
                r = recharger(m)
                self.assertEqual(r.data, m.data)
                self.assertEqual((regarder(r), fiche(r), scene_percue(r)),
                                 (regarder(m), fiche(m), scene_percue(m)))
                avant = copy.deepcopy(r.data)
                ecoute.retenir(r, [(parole, parole['niveau'], parole['par'])])
                self.assertEqual(r.data, avant)  # Le rejeu du son ne réadmet pas le défunt.
                self.assertNotIn(c, ecoute.appels(r))

    def test_joueur_ligote_cri_temoin_nouvelle(self):
        m, c = scene()
        corps.corps(m, c)["inconscient"] = 0
        appliquer_etats(m, [c + ":ligote"])
        for i in ("marchand", "aubin"):
            corps.endormir(m, i)
        placer(m, "ilse", m.joueur["salle"], (3, 4))
        orienter(m, "ilse", "joueur")
        m.joueur["orientation"] = "ouest"
        percevoir_tous(m)
        debut = instant(m)
        with patch("donjon.ouie.retentir", wraps=__import__("donjon.ouie", fromlist=["retentir"]).retentir) as bruit:
            texte = Moteur(m).executer(Moteur(m).preparer(analyser(m, "tuer Brune")))
            self.assertTrue(any(a.args[1:3] == (c, "cri") for a in bruit.call_args_list))
        m = recharger(m)
        self.assertEqual(instant(m) - debut, 300)
        self.assertEqual(m.objets[c]["type"], "depouille")
        self.assertEqual(m.data["defunts"][c]["auteur"], "joueur")
        self.assertNotIn(c, m.data["esprits"])
        self.assertIn("tué", texte)
        self.assertIn("corps", regarder(m))
        self.assertTrue(se_mefie(m, "ilse", "joueur"))
        self.assertTrue(any(s.get("operation") == "tuer" for s in lire(m, "ilse")["memoire"]))
        self.assertTrue(any(s["type"] == "detresse" and s["qui"] == c for s in lire(m, "ilse")["memoire"]))
        temoin = next(s for s in lire(m, "ilse")["memoire"] if s.get("operation") == "tuer")
        self.assertIn("a tenté de tuer", phrase(m, temoin))
        noyau = next(n[1] for n in nouvelles(m, "ilse") if n[1]["type"] == "mort_vue")
        corps.corps(m, "aubin")["inconscient"] = 0
        placer(m, "aubin", "echoppe", (4, 4))
        placer(m, "ilse", "echoppe", (4, 5))
        orienter(m, "ilse", "aubin")
        orienter(m, "aubin", "ilse")
        from donjon.ouie import saisissent
        self.assertIn("aubin", saisissent(m, "ilse", "dire"))
        with patch("donjon.paroles.jet_persuasion", return_value=(True, {})):
            recevoir(m, "aubin", "ilse", {"type": "rumeur", "evenement": noyau, "rang": 0})
            _entendu(m, "ilse", "aubin", noyau, 0, [])
        m = recharger(m)
        etat = lire(m, "aubin")["croyances"][c]["etat"]
        self.assertTrue(etat["valeur"]["mort"])
        self.assertNotEqual(etat["source"], "vu")
        self.assertLess(etat["confiance"], 1)
        self.assertIn("morte", phrase(m, noyau))

    def test_autre_victime_sans_temoin_decouverte_sans_coupable(self):
        m, c = scene("auberge")
        salle = m.joueur["salle"]
        for i in list(m.data["esprits"]):
            if i != c:
                corps.endormir(m, i)
        m.joueur["orientation"] = "ouest"
        m.objets["arme_test"] = objet("arme_test", "arme", "outil", "joueur", mobile=True, usages=["couper"])
        p = Moteur(m).preparer(proposition("tuer", c, "arme_test"))
        self.assertEqual(p.dixiemes, 50)
        Moteur(m).executer(p)
        m = recharger(m)
        temoin = next(i for i in m.data["esprits"])
        corps.corps(m, temoin)["inconscient"] = 0
        placer(m, temoin, salle, (3, 4))
        orienter(m, temoin, c)
        percevoir_tous(m)
        m = recharger(m)
        mem = lire(m, temoin)["memoire"]
        self.assertTrue(any(s["type"] == "mort_vue" and s["objet"] == c for s in mem))
        self.assertFalse(any(s.get("operation") == "tuer" for s in mem))
        self.assertIn("corps", regarder(m))

    def test_echeance_decoupage_et_interruptions(self):
        for interrompu in (False, True):
            a, c = scene()
            tenir.commencer(a, "joueur", "tuer", c)
            b = recharger(a)
            if interrompu:
                corps.corps(a, c)["inconscient"] = 0
                corps.corps(b, c)["inconscient"] = 0
            passer(a, 300)
            for dt in (13, 107, 179):
                passer(b, dt)
                b = recharger(b)
                self.assertEqual(b.objets[c]["type"], "personnage")
            passer(b, 1)
            a, b = recharger(a), recharger(b)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))
            self.assertEqual(a.objets[c]["type"], "personnage" if interrompu else "depouille")

    def test_refus_libre_et_outil_invalide(self):
        m, c = scene()
        corps.corps(m, c)["inconscient"] = 0
        placer(m, "marchand", "echoppe", (4, 4))
        corps.endormir(m, "marchand")
        for outil in ("", "inexistant"):
            with self.assertRaises(ErreurMonde) as refus:
                tenir.valider(m, "joueur", "tuer", c, outil)
            self.assertTrue(refus.exception.attendu)
            self.assertNotIn("marchand", refus.exception.attendu)
        corps.endormir(m, c)
        with self.assertRaises(ErreurMonde) as refus:
            tenir.valider(m, "joueur", "tuer", c, "inexistant")
        self.assertIn("outil=inexistant", refus.exception.attendu)

    def test_depouiller_bien_du_mort_faute_et_temoin(self):
        from donjon.biens import a_autrui
        from donjon.vol import proprietaire
        m, _ = scene()
        c, auteur = "aubin", "brune"
        corps.corps(m, auteur)["inconscient"] = 0
        placer(m, c, m.joueur["salle"], (2, 5))
        m.objets["butin_test"] = objet("butin_test", "butin", "outil", c, mobile=True)
        corps.mourir(m, c)
        placer(m, auteur, m.joueur["salle"], (2, 4))
        placer(m, "ilse", m.joueur["salle"], (3, 4))
        orienter(m, "ilse", auteur)
        percevoir_tous(m)
        self.assertEqual(a_autrui(m, "butin_test", auteur, "prendre"), c)
        gestes = []
        self.assertTrue(_executer(m, auteur, {"operation": "prendre", "cible": "butin_test", "outil": "", "condition": "", "lieu": m.joueur["salle"]}, [], gestes))
        from donjon.pnj import commencer_geste
        for a, op, cible, nature in gestes:
            commencer_geste(m, a, op, cible, instant(m) + 20, nature=nature)
        m = recharger(m)
        self.assertEqual(m.objets["butin_test"]["lieu"], auteur)
        self.assertEqual(proprietaire(m, m.objets["butin_test"]), c)
        self.assertTrue(any(s.get("operation") == "prendre" and s.get("victime") == c for s in lire(m, "ilse")["memoire"]))
        m.joueur["orientation"] = "ouest"
        self.assertIn("corps", regarder(m))

    def test_pnj_tue_joueur_fin_persistante(self):
        m, c = scene()
        corps.corps(m, c)["inconscient"] = 0
        corps.endormir(m, "joueur")
        self.assertTrue(_executer(m, c, {"operation": "tuer", "cible": "joueur", "outil": ""}, [], []))
        passer(m, 300)
        m = recharger(m)
        self.assertEqual(m.data["fin"]["auteur"], c)
        self.assertTrue(regarder(m))
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(proposition("attendre"))

    def test_mort_en_cours_de_laps_retire_le_personnage_de_l_horloge(self):
        m, c = scene()
        tenir.commencer(m, "joueur", "tuer", c)
        passer(m, 1200)
        m = recharger(m)
        self.assertEqual(m.objets[c]["type"], "depouille")
        self.assertNotIn(c, m.data["esprits"])
        self.assertTrue(regarder(m))

    def test_pnj_tue_pnj_vue_et_interruption_auteur(self):
        from donjon.combat import interrompre
        for interruption in (False, True):
            m, c = scene()
            placer(m, "aubin", m.joueur["salle"], (2, 4))
            for i in ("ilse", "marchand"):
                corps.endormir(m, i)
            m.joueur["orientation"] = "ouest"
            m.objets["arme_test"] = objet("arme_test", "arme", "outil", "aubin", mobile=True, usages=["couper"])
            self.assertTrue(_executer(m, "aubin", {"operation": "tuer", "cible": c, "outil": "arme_test"}, [], []))
            passer(m, 20)
            if interruption:
                interrompre(m, "aubin")
            m = recharger(m)
            lignes = passer(m, 1180)
            m = recharger(m)
            self.assertEqual(m.objets[c]["type"], "personnage" if interruption else "depouille")
            self.assertEqual(any("a tué" in l for l in lignes), not interruption)
            self.assertTrue(regarder(m))
