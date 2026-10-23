"""4b : les coups se jouent, se voient et se rechargent par les contrats communs."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon import combat, corps, planification, spatial
from donjon.banc_pnj import creer
from donjon.deplacement_objet import deplacer
from donjon.esprits import lire, percevoir_tous, memoriser, croire
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.pnj import commencer_geste, _etape, agir
from donjon.relations import se_mefie
from donjon.rendu import regarder
from donjon.francais import sujet
from donjon.temps import instant, MINUTE
from tests.support import calme, presentes, regarder as orienter, refusee
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


def scene(cible="marchand", surprise=True):
    m = presentes(creer("rixe", 1985, "fixe"))
    calme(m, "marchand", "ilse", "aubin", "brune")
    for id, pos in (("brune", (2, 5)), (cible, (3, 5))):
        placer(m, id, "antichambre", pos)
    for id in {"ilse", "aubin", "marchand"} - {cible}:
        placer(m, id, "echoppe", (4 if id == "ilse" else 6 if id == "aubin" else 8, 4))
    m.joueur.update(salle="antichambre", position=[1, 5], orientation="est")
    m.objets[cible]["orientation"] = "est" if surprise else "ouest"
    m.objets["brune"]["orientation"] = "est"
    percevoir_tous(m)
    return m


def epreuve(cible="marchand", douceur=30):
    m = scene(cible)
    m.joueur.update(salle="chambre_cloche", position=[2, 2])
    refusee(m)
    lire(m, "brune")["besoins"]["faim"] = 80
    m.objets["brune"]["profil"]["valeurs"]["douceur"] = douceur
    # Même recours en l'absence de crochets utilisables ; aucune capacité n'est prêtée au PNJ.
    m.objets["brune"]["profil"]["capacites"] = []
    deplacer(m, "cle_reserve", cible)
    m.objets["cle_reserve"]["proprietaire"] = cible
    croire(m, "brune", "cle_reserve", "lieu", cible, "vu", salle=None, case=None)
    croire(m, "brune", cible, "lieu", "antichambre", "vu", salle="antichambre", case=[3, 5])
    return m


class CombatTests(unittest.TestCase):
    def test_assommer_surprise_et_identite_inconnue_apres_reveil_de_deux_victimes(self):
        for cible in ("marchand", "aubin"):
            with self.subTest(cible=cible):
                m = scene(cible)
                avant = corps.pv(m, cible)
                with patch.object(type(m), "d20", return_value=20):
                    r = combat.frapper(m, "brune", cible, methode="assommer")
                self.assertTrue(r["surprise"])
                self.assertFalse(corps.conscient(m, cible))
                self.assertEqual(corps.pv(m, cible), avant - 1)
                m = recharger(m)
                self.assertIn("sans connaissance", " ".join(regarder(m).split()))
                subi = next(s for s in lire(m, cible)["memoire"] if s["type"] == "subi")
                self.assertIsNone(subi["auteur"])
                # Le réveil ne fabrique pas une attribution, même si l'agresseur est encore là.
                corps.reveiller(m, cible)
                m = recharger(m)
                self.assertIsNone(next(s for s in lire(m, cible)["memoire"] if s["type"] == "subi")["auteur"])
                self.assertFalse(m.data.get("defunts"))

    def test_coup_vu_victime_et_temoin_se_mefient_apres_recharge(self):
        for cible in ("marchand", "aubin"):
            m = scene(cible, False)
            placer(m, "ilse", "antichambre", (3, 4))
            orienter(m, "ilse", "brune")
            percevoir_tous(m)
            with patch.object(type(m), "d20", side_effect=[20, 1]):
                r = combat.frapper(m, "brune", cible)
            m = recharger(m)
            self.assertTrue(r["touche"])
            self.assertEqual(next(s for s in lire(m, cible)["memoire"] if s["type"] == "subi")["auteur"], "brune")
            self.assertTrue(se_mefie(m, cible, "brune"))
            self.assertTrue(se_mefie(m, "ilse", "brune"))
            self.assertIn("ilse", r["temoins"])
            self.assertTrue(any(s["type"] == "a_frappe" for s in lire(m, "brune")["memoire"]))
            self.assertTrue(any(s["type"] == "vu_agir" for s in lire(m, "ilse")["memoire"]))

    def test_action_joueur_fiche_moteur_et_rechargement(self):
        for cible in ("brune", "marchand"):
            m = scene("marchand")
            if cible == "marchand":
                placer(m, "brune", "echoppe", (3, 3))
                m.joueur["position"] = [2, 5]
            deplacer(m, "marteau", "joueur")
            percevoir_tous(m)
            p = Moteur(m).preparer(proposition("frapper", cible, "marteau", "assommer"))
            self.assertIn("esquive", p.resume(m))
            avant = corps.pv(m, cible)
            with patch.object(type(m), "d20", return_value=20):
                texte = Moteur(m).executer(p)
            m = recharger(m)
            self.assertEqual(corps.pv(m, cible), avant - 1)
            self.assertIn("sans connaissance", texte)
            self.assertIn("sans connaissance", " ".join(regarder(m).split()))
            self.assertTrue(m.data["journal"][-1]["reussite"])

    def test_sans_connaissance_aucune_humeur_montree_apres_recharge(self):
        # Vu au banc Luna de la fusion : « Gorm … est à terre, sans connaissance et préoccupé ».
        # Comme une dépouille, un inconscient ne montre aucune humeur, au joueur ni au MJ.
        for cible in ("marchand", "brune"):
            with self.subTest(cible=cible):
                m = scene("marchand")
                if cible == "marchand":
                    placer(m, "brune", "echoppe", (3, 3))
                    m.joueur["position"] = [2, 5]
                m.objets[cible]["humeur"] = "préoccupé"
                percevoir_tous(m)
                p = Moteur(m).preparer(proposition("frapper", cible, "", "assommer"))
                with patch.object(type(m), "d20", return_value=20):
                    texte = Moteur(m).executer(p)
                m = recharger(m)
                self.assertFalse(corps.conscient(m, cible))
                nom = m.objets[cible]["nom"].split(",")[0]
                self.assertNotIn(nom + " semble", texte)
                vue = " ".join(regarder(m).split())
                self.assertIn("sans connaissance", vue)
                self.assertNotIn("préoccupé", vue)
                corps.reveiller(m, cible)
                m = recharger(m)
                self.assertIn("préoccupé", " ".join(regarder(m).split()))

    def test_victime_frappee_par_surprise_ne_semble_pas_calme(self):
        # Vu au banc Luna de la fusion : « Tu frappes Brune… Brune semble calme ». L'humeur montrée
        # suit l'état du personnage : un coup subi fait presser sa sécurité, il semble inquiet.
        for cible in ("brune", "marchand"):
            with self.subTest(cible=cible):
                m = scene("marchand")
                if cible == "marchand":
                    placer(m, "brune", "echoppe", (3, 3))
                    m.joueur["position"] = [2, 5]
                percevoir_tous(m)
                p = Moteur(m).preparer(proposition("frapper", cible, "", "simple"))
                with patch.object(type(m), "d20", return_value=20):
                    texte = Moteur(m).executer(p)
                m = recharger(m)
                self.assertTrue(corps.conscient(m, cible))
                self.assertIsNone(next(s for s in lire(m, cible)["memoire"] if s["type"] == "subi")["auteur"])
                # Accordée au genre : « Brune … semble inquiète », « Gorm … semble inquiet ».
                inquiet = "inquiète" if cible == "brune" else "inquiet"
                self.assertIn(sujet(m.objets[cible]) + " semble " + inquiet + ".", texte)
                self.assertNotIn(sujet(m.objets[cible]) + " semble calme", texte)
                self.assertIn(inquiet, " ".join(regarder(m).split()))

    def test_fiche_dit_si_la_victime_voit_venir_le_coup_apres_recharge(self):
        # Vu au banc Luna de la fusion : « j'assomme Gorm par derrière » refusé par la contre-revue,
        # qui ne savait pas que Gorm tourne le dos à Corvus. La fiche dit ce que le moteur établit.
        for cible, surprise in (("marchand", True), ("marchand", False), ("brune", True)):
            with self.subTest(cible=cible, surprise=surprise):
                m = scene("marchand", surprise)
                if cible == "marchand":
                    placer(m, "brune", "echoppe", (3, 3))
                    m.joueur["position"] = [2, 5]
                m = recharger(m)
                percevoir_tous(m)
                fiche = Moteur(m).preparer(proposition("frapper", cible, "", "assommer")).resume(m)
                attendu = " ne te voit pas : défense 10 par surprise." if surprise else " te voit : jet d'esquive."
                self.assertIn(sujet(m.objets[cible]) + attendu, fiche)
                corps.endormir(m, cible)
                m = recharger(m)
                self.assertIn("sans défense", Moteur(m).preparer(proposition("frapper", cible, "", "simple")).resume(m))

    def test_refus_une_cause_et_attendu(self):
        m = scene()
        deplacer(m, "couteau", "brune") if "couteau" in m.objets else None
        for args in (("brune", "marchand", "absent"), ("brune", "brune"), ("brune", "ilse")):
            with self.subTest(args=args), self.assertRaises(ErreurMonde) as cm:
                combat.valider(m, *args)
            self.assertTrue(cm.exception.attendu)
        self.assertEqual(combat.arme({"usages": ["couper"], "masse": .2, "puissance": 2}), (True, 2, "DEX"))
        self.assertIsNone(combat.arme({"masse": .1}))
        self.assertEqual(combat.arme({"masse": .5}), (False, 1, "FOR"))

    def test_coup_interrompt_et_zero_pv_ne_tue_pas(self):
        m = scene()
        e = lire(m, "marchand")
        commencer_geste(m, "marchand", "prendre", "marteau", 500)
        e.update(libre=500, intention=None)
        m.objets["marchand"]["pv"] = 1
        with patch.object(type(m), "d20", return_value=20):
            combat.frapper(m, "brune", "marchand")
        m = recharger(m)
        self.assertEqual(corps.pv(m, "marchand"), 0)
        self.assertFalse(corps.conscient(m, "marchand"))
        self.assertFalse(any(g["auteur"] == "marchand" for g in m.data["gestes_en_cours"]))
        self.assertEqual(m.objets["marchand"]["type"], "personnage")

    def test_meme_laps_bloc_ou_decoupe_avec_recharge(self):
        for cible in ("marchand", "aubin"):
            m = scene(cible)
            with patch.object(type(m), "d20", return_value=20):
                combat.frapper(m, "brune", cible, methode="assommer")
            a, b = recharger(m), recharger(m)
            passer(a, 30 * MINUTE)
            for dt in (13, 587, 7 * MINUTE, 22 * MINUTE):
                passer(b, dt)
                b = recharger(b)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))

    def test_meme_laps_y_compris_embuscade_en_cours(self):
        from donjon.deliberation import retenir_refus, choisir
        for cible in ("marchand", "aubin"):
            m = epreuve(cible)
            retenir_refus(m, "brune", cible, "demander", "necessaire", objet="cle_reserve")
            choisir(m, "brune", 0)
            a, b = recharger(m), recharger(m)
            passer(a, 10 * MINUTE)
            for dt in (15, 25, 20, 540, 9 * MINUTE):
                passer(b, dt)
                b = recharger(b)
            self.assertEqual(a.data, b.data)
            self.assertEqual(regarder(a), regarder(b))

    def test_console_montre_fiche_avant_de_tenter_un_geste_a_risque(self):
        import jeu
        from tools.verifier_websocket_jeu import Interface
        from donjon.monde import Monde
        m = scene()
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)
            journaux = []

            class Console(Interface):
                def lire(self, *args):
                    journaux.append(len(Monde.charger(self.chemin).data["journal"]))
                    return super().lire(*args)

            console = Console(["frapper Brune", "tenter", "quitter"], chemin)
            jeu.main(["--console", "--offline", "--save", str(chemin)], interface=console)
            self.assertEqual(journaux[:2], [0, 0])
            self.assertEqual(journaux[2], 1)
            self.assertIn("esquive", " ".join(console.sorties))

    def test_pnj_assomme_joueur_meme_regle_et_attente_jusqu_au_reveil(self):
        m = scene()
        # Le joueur regarde vers l'ouest, l'agresseur est dans son dos au contact.
        m.joueur["orientation"] = "ouest"
        e = lire(m, "brune")
        e["intention"] = {"but": {"type": "manger", "objet": "vivres"}, "motif": "faim",
                          "plan": [_etape("assommer", "joueur")], "depuis": 0, "attente": 0}
        with patch.object(type(m), "d20", return_value=20):
            texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
        m = recharger(m)
        self.assertTrue(corps.conscient(m))
        self.assertEqual(m.joueur["pv"], 17)
        self.assertIn("Tu perds connaissance.", texte)
        self.assertIn("Tu reviens à toi.", texte)
        self.assertGreaterEqual(m.data["minutes"], 25)
        self.assertFalse(m.data.get("fin"))

    def test_douceur_100_interdit_agression_mais_pas_future_defense(self):
        m = creer("rixe_douce", 1985, "fixe")
        self.assertIsNone(combat.prix_violence(m, "brune"))
        self.assertEqual(combat.prix_violence(m, "brune", defense=True), 0)

    def test_rotation_vers_une_cible_deja_visible_comptee_et_sauvee(self):
        m = scene()
        m.joueur["orientation"] = "nord-est"
        p = Moteur(m).preparer(proposition("frapper", "brune"))
        self.assertEqual(p.dixiemes, 20)
        Moteur(m).executer(p)
        m = recharger(m)
        self.assertEqual(m.joueur["orientation"], "est")
        self.assertEqual(instant(m), 20)

    def test_assommer_pour_prendre_cas_reel_et_autre_porteur_apres_recharge(self):
        from donjon.deliberation import choisir, retenir_refus
        from donjon.pnj import a_pas_feutres
        for cible in ("marchand", "aubin"):
            with self.subTest(cible=cible):
                m = epreuve(cible)
                # Les coûts font préférer la demande à l'agression, avant tout refus de la clé.
                plan = planification.planifier(m, "brune", "faim")
                self.assertIn("demander", [e["operation"] for e in plan[1]])
                self.assertNotIn("assommer", [e["operation"] for e in plan[1]])
                retenir_refus(m, "brune", cible, "demander", "necessaire", objet="cle_reserve")
                choisir(m, "brune", 0)
                self.assertTrue(a_pas_feutres(m, "brune"))
                self.assertEqual(lire(m, "brune")["intention"]["plan"][0]["operation"], "dans_le_dos")
                m = recharger(m)
                texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
                m = recharger(m)
                coups = [e for e in m.data["historique_corps"] if e["type"] == "coup"]
                self.assertEqual(len(coups), 1)
                self.assertTrue(coups[0]["surprise"])
                self.assertEqual(coups[0]["temoins"], [])
                self.assertEqual(m.objets["cle_reserve"]["lieu"], "brune")
                self.assertTrue(coups[0]["assomme"])
                if corps.conscient(m, cible):
                    self.assertTrue(any(e["type"] == "ranime" and e["id"] == cible for e in m.data["historique_corps"]))
                self.assertIn("cri", texte)
                self.assertNotIn("Brune", texte)
                self.assertEqual(corps.mesures(m)["morts"], 0)
                corps.reveiller(m, cible)
                m = recharger(m)
                self.assertIsNone(next(s for s in lire(m, cible)["memoire"] if s["type"] == "subi")["auteur"])

    def test_epreuve_douce_refuse_agression_et_temoins_empechent_embuscade(self):
        from donjon.deliberation import retenir_refus, choisir
        for douceur in (30, 100):
            m = epreuve(douceur=douceur)
            retenir_refus(m, "brune", "marchand", "demander", "necessaire", objet="cle_reserve")
            if douceur == 100:
                self.assertIsNone(planification.planifier(m, "brune", "faim"))
            else:
                placer(m, "ilse", "antichambre", (4, 5))
                orienter(m, "ilse", "brune")
                percevoir_tous(m)
                choisir(m, "brune", 0)
                Moteur(m).executer(Moteur(m).preparer(proposition("attendre", "30")))
                m = recharger(m)
                self.assertFalse(any(e["type"] == "coup" for e in m.data.get("historique_corps", [])))

    def test_lame_esquive_egalite_resistance_et_degats(self):
        m = scene("marchand", False)
        deplacer(m, "marteau", "brune")
        with patch.object(type(m), "d20", side_effect=[10, 10]):
            r = combat.frapper(m, "brune", "marchand")
        self.assertFalse(r["touche"])
        self.assertEqual(r["degats"], 0)
        m = recharger(m)
        with patch.object(type(m), "d20", side_effect=[20, 1, 20]):
            r = combat.frapper(m, "brune", "marchand", "marteau", "assommer")
        self.assertEqual(r["degats"], 1)
        self.assertFalse(r["assomme"])
        self.assertTrue(corps.conscient(recharger(m), "marchand"))


if __name__ == "__main__":
    unittest.main()
