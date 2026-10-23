"""Les décisions graduées : scènes physiques et paroles, après reprise."""
import copy
import unittest
from unittest.mock import patch

from donjon import relations as R
from donjon.esprits import croire, lire, memoriser, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from tests.support import calme, regarder
from tests.test_social import relais, recharger, placer
from tests.test_relations_graduees import reunir


def lien(m, id, autre, **axes):
    lire(m, id)["relations"][autre] = R._nouvelle({"confiance": 65, **axes}, m.data["minutes"])


class LecturesTests(unittest.TestCase):
    def test_une_ancienne_case_crue_ne_devient_pas_une_proximite_racontee(self):
        from tests.test_marche import intention
        for id, autre in (("ilse", "aubin"), ("brune", "marchand")):
            m = calme(relais(), "ilse", "aubin", "brune", "marchand")
            for n, x in enumerate(x for x in ("ilse", "aubin", "brune", "marchand") if x != id):
                lire(m, x)["libre"] = 600000
                if x != autre:
                    placer(m, x, "crypte", [2 + n, 3])
            placer(m, id, "antichambre", [3, 5])
            placer(m, autre, "antichambre", [5, 5])
            m.objets[id]["orientation"] = "ouest"
            m.joueur.update(salle="antichambre", position=[2, 6], orientation="nord-est")
            lire(m, id)["relations"].clear()
            lien(m, id, autre, affection=50)
            croire(m, id, autre, "lieu", "antichambre", "vu", salle="antichambre", case=[4, 5])
            lire(m, id)["besoins"]["securite"] = 75
            intention(m, id, [{"operation": "abriter", "lieu": "antichambre"}], but={"type": "abri", "lieu": "antichambre"})
            m = recharger(m)
            texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
            m = recharger(m)
            self.assertEqual(m.objets[id]["position"], [3, 5])
            self.assertEqual(m.objets[autre]["position"], [5, 5])
            nom = m.objets[id]["nom"].split(",")[0]
            self.assertIn(nom + " reste en compagnie.", texte)
            self.assertNotIn(nom + " reste près ", texte)

    def test_avis_et_aveu_ne_racontent_pas_un_basculement_absent(self):
        from donjon.paroles import preparer_parole
        for id in ("ilse", "aubin"):
            m = reunir(calme(relais(), "ilse", "brune", "aubin", "marchand"), id)
            m.joueur.update(salle="antichambre", position=[4, 5], orientation="ouest")
            regarder(m, id, "joueur")
            lire(m, id)["voix"] = sorted(set(lire(m, id)["voix"]) | {"joueur"})
            lien(m, id, "joueur", confiance=100)
            lien(m, id, "brune", confiance=100)
            m.data["connus"] = sorted(set(m.data["connus"]) | {"cle_reserve", id, "brune"})
            nom = m.objets[id]["nom"].split(",")[0]
            avis = f"{nom}, Brune n'est pas fiable."
            with patch.object(Monde, "d20", return_value=20):
                m, rapport = preparer_parole(m, {"personnage": id, "replique": avis, "_intention": avis,
                    "contenu": [{"type": "affirmation", "sujet": "brune", "attribut": R.FIABLE, "valeur": "non"}]})
            m = recharger(m)
            self.assertEqual(R.envers(m, id, "brune")["confiance"], 80)
            self.assertTrue(R.se_fie(m, id, "brune"))
            self.assertIn("retient ce que tu lui dis", " ".join(rapport["faits"]))
            aveu = f"{nom}, j'ai pris cette clé."
            with patch.object(Monde, "d20", return_value=20):
                m, rapport = preparer_parole(m, {"personnage": id, "replique": aveu, "_intention": aveu,
                    "contenu": [{"type": "aveu", "sujet": "cle_reserve", "attribut": "", "valeur": "prendre"}]})
            m = recharger(m)
            self.assertEqual(R.envers(m, id, "joueur")["confiance"], 75)
            self.assertTrue(R.se_fie(m, id, "joueur"))
            self.assertIn("retient ton aveu", " ".join(rapport["faits"]))
            self.assertNotIn("plus pour fiable", " ".join(rapport["faits"]))

    def test_affection_seule_leve_l_orgueil_pour_deux_passants(self):
        from donjon.passage import laisser_passer, s_ecarter
        from tests.test_passage import refuge, faire
        for passant in ("joueur", "aubin"):
            for affection in (49, 50):
                with self.subTest(passant=passant, affection=affection):
                    m = refuge()
                    if passant != "joueur":
                        m.joueur.update(salle="antichambre", position=[2, 5])
                        placer(m, passant, "antichambre", [1, 3])
                    m.objets["brune"]["profil"]["valeurs"].update(fierte=80, altruisme=30)
                    lien(m, "brune", passant, affection=affection)
                    m = recharger(m)
                    if passant == "joueur":
                        if affection < 50:
                            with self.assertRaises(ErreurMonde) as refus:
                                faire(m, "marcher", "ouest")
                            self.assertIn("ne s'écarte pas", str(refus.exception))
                        else:
                            self.assertIn("s'écarte pour te laisser passer", faire(m, "marcher", "ouest"))
                    else:
                        case, raison = laisser_passer(m, "brune", passant)
                        if affection < 50:
                            self.assertEqual(raison, "orgueil")
                        else:
                            lignes = []
                            s_ecarter(m, "brune", case, passant, lignes)
                            self.assertIn("laisser passer Aubin", " ".join(lignes))
                    m = recharger(m)
                    self.assertEqual(m.objets["brune"]["position"] == [0, 3], affection < 50)

    def test_la_confidence_va_au_plus_aime_puis_a_l_identifiant(self):
        from donjon.social import bavarder
        for id, accuse in (("ilse", "brune"), ("brune", "ilse")):
            for aff_aubin, aff_gorm, attendu in ((80, 20, "aubin"), (20, 80, "marchand"), (50, 50, "aubin")):
                m = reunir(calme(relais(), "ilse", "brune", "aubin", "marchand"), id, "aubin", "marchand", accuse)
                lien(m, id, "aubin", affection=aff_aubin)
                lien(m, id, "marchand", affection=aff_gorm)
                lien(m, id, accuse, confiance=15)
                memoriser(m, id, {"type": "vol_surpris", "auteur": accuse, "objet": "marteau", "victime": id})
                # Confidence à froid : la colère immédiate demande désormais des comptes à l’auteur.
                m.data["minutes"] += 60
                m.joueur.update(salle="antichambre", position=[1, 5], orientation="est")
                percevoir_tous(m)
                m = recharger(m)
                lignes = []
                with patch.object(Monde, "d20", return_value=20):
                    self.assertTrue(bavarder(m, id, lignes))
                m = recharger(m)
                texte = next(c["texte"] for c in m.data["chronique"] if " dit à " in c["texte"])
                self.assertIn("dit à " + ("Aubin" if attendu == "aubin" else "Gorm"), texte)
                self.assertTrue(any(s["type"] == "rumeur" and s["de"] == id for s in lire(m, attendu)["memoire"]))
                self.assertTrue(lignes)  # Le joueur voit ou entend réellement l'échange.

    def test_peur_ou_rancune_seules_empechent_de_repondre_a_l_appel(self):
        from donjon.appel import repondre
        from donjon.pnj import heler
        for source in ("joueur", "aubin"):
            for axe in ("peur", "rancune"):
                for n in (59, 60):
                    m = reunir(calme(relais(), "ilse", "brune", "aubin", "marchand"), "ilse", "aubin")
                    m.joueur.update(salle="antichambre", position=[1, 5], orientation="est")
                    regarder(m, "ilse", source)
                    lire(m, "ilse")["voix"] = sorted(set(lire(m, "ilse")["voix"]) | {source})
                    lien(m, "ilse", source, **{axe: n})
                    percevoir_tous(m)
                    m = recharger(m)
                    lignes = []
                    heler(m, source, "ilse", lignes)
                    self.assertEqual(repondre(m, source, "ilse", lignes), n < 60)
                    m = recharger(m)
                    reponses = [c for c in m.data["chronique"] if c["pnj"] == "ilse" and "répond" in c["texte"]]
                    self.assertEqual(bool(reponses), n < 60)
                    # Depuis l'appel négocié, la réponse est convenue (« Qu'est-ce que tu veux ? »…).
                    self.assertEqual("Ilse répond" in " ".join(lignes), n < 60)
                    self.assertTrue(R.se_fie(m, "ilse", source))

    def test_rancune_seule_refuse_echange_et_passage(self):
        from donjon.echanges import demander
        for source in ("joueur", "aubin"):
            m = reunir(calme(relais(), "ilse", "brune", "aubin", "marchand"), "ilse", "aubin")
            m.joueur.update(salle="antichambre", position=[1, 5], orientation="est")
            regarder(m, "ilse", source)
            lien(m, "ilse", source, rancune=60)
            m.objets["marteau"].update(lieu="ilse", proprietaire="ilse")
            m.objets["marteau"].pop("position", None)
            m = recharger(m)
            self.assertEqual(demander(m, source, "ilse", "marteau"), "rancune")
            lignes = []
            if source == "joueur":
                from donjon.paroles import preparer_parole
                m, rapport = preparer_parole(m, {"personnage": "ilse", "replique": "Laisse-moi passer.",
                    "contenu": [{"type": "passage", "sujet": "", "attribut": "", "valeur": ""}]})
                lignes = rapport["faits"]
            else:
                from donjon.echanges import executer
                from donjon.pnj import _etape
                from donjon.passage import demander_passage
                self.assertEqual(demander_passage(m, "ilse", source, lignes), "rancune")
                self.assertFalse(executer(m, source, _etape("demander", "ilse", "marteau"), lignes))
            m = recharger(m)
            self.assertEqual(m.objets["marteau"]["lieu"], "ilse")
            self.assertEqual(m.objets["ilse"]["position"], [2, 5])
            self.assertTrue(R.se_fie(m, "ilse", source))
            self.assertIn("refuse", " ".join(lignes))
            self.assertNotIn("ne te fait pas confiance", " ".join(lignes))

    def test_peur_seule_fait_surveiller_un_bruit_connu(self):
        from donjon.ouie import retentir
        for auteur in ("joueur", "aubin"):
            for peur in (0, 50):
                m = reunir(calme(relais(), "ilse", "brune", "aubin", "marchand"), "ilse", "aubin")
                m.joueur.update(salle="antichambre", position=[4, 5])
                if auteur == "aubin":
                    placer(m, auteur, "antichambre", [4, 5])
                    m.joueur["position"] = [1, 5]
                lien(m, "ilse", auteur, peur=peur)
                regarder(m, "ilse", auteur)
                percevoir_tous(m)
                m.objets["ilse"]["orientation"] = "ouest"
                m = recharger(m)
                retournes = retentir(m, auteur, "marcher")
                m = recharger(m)
                self.assertEqual("ilse" in retournes, bool(peur))
                self.assertEqual(m.objets["ilse"]["orientation"] == "ouest", not peur)
                self.assertTrue(R.se_fie(m, "ilse", auteur))
                self.assertEqual(any("se retourne au bruit" in c["texte"] for c in m.data.get("chronique", []) if c["pnj"] == "ilse"), bool(peur))

    def test_la_recherche_recalcule_son_cout_quand_la_peur_change_ou_s_estompe(self):
        from donjon.planification import chercher, diagnostics, _MEMOIRE, _GRAPHES
        from tests.test_marche import intention
        for id, autre in (("ilse", "joueur"), ("aubin", "brune")):
            m = calme(relais(), "ilse", "brune", "aubin", "marchand")
            placer(m, id, "echoppe", [8, 3])
            placer(m, "brune", "antichambre", [5, 5])
            m.joueur.update(salle="antichambre", position=[4, 5], orientation="ouest")
            croire(m, id, autre, "lieu", "antichambre", "vu", salle="antichambre", case=[4, 5] if autre == "joueur" else [5, 5])
            lien(m, id, autre)
            m = recharger(m)
            _MEMOIRE.clear()
            _GRAPHES.clear()
            def chercher_abri():
                return chercher(m, id, lambda v, e: e.salle == "antichambre", memo=["test-peur"], emplois=(), tenir=True)
            with diagnostics() as recherches:
                neutre = chercher_abri()
                chercher_abri()
                physiques = copy.deepcopy(lire(m, id)["croyances"])
                lien(m, id, autre, peur=80)
                m = recharger(m)
                effraye = chercher_abri()
                m.data["minutes"] += 120
                m = recharger(m)
                apaise = chercher_abri()
            self.assertEqual([r["memoire"] for r in recherches], [False, True, False, False])
            self.assertEqual(physiques, lire(m, id)["croyances"])
            self.assertGreater(effraye[0], neutre[0])
            self.assertGreater(effraye[0], apaise[0])
            intention(m, id, apaise[1])
            texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
            m = recharger(m)
            self.assertEqual(m.objets[id]["lieu"], "antichambre")
            self.assertIn("Tu entends des pas", texte)

    def test_l_abri_rejoint_le_plus_aime_des_proches_fiables(self):
        from donjon.deliberation import _plan_abri
        from tests.test_marche import intention
        for id in ("ilse", "brune"):
            for aime in ("aubin", "marchand"):
                m = calme(relais(), "ilse", "brune", "aubin", "marchand")
                placer(m, id, "echoppe", [3, 5])
                placer(m, "aubin", "antichambre", [5, 5])
                placer(m, "marchand", "crypte", [5, 3])
                if id == "brune":
                    placer(m, "ilse", "antichambre", [3, 5])
                m.joueur.update(salle="antichambre", position=[1, 5], orientation="est")
                m.objets["porte"].update(ouverte=True, verrouillee=False)
                lire(m, id)["relations"].clear()
                for x in ("aubin", "marchand"):
                    lire(m, x)["libre"] = 6000  # Ils restent occupés ici pendant l'arrivée.
                    lien(m, id, x, affection=80 if x == aime else 20)
                    salle = m.objets[x]["lieu"]
                    croire(m, id, x, "lieu", salle, "vu", salle=salle, case=m.objets[x]["position"])
                    croire(m, id, salle, "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "vu")
                m = recharger(m)
                choix = _plan_abri(m, id)
                self.assertIsNotNone(choix)
                but, plan = choix
                self.assertEqual(but["lieu"], m.objets[aime]["lieu"])
                intention(m, id, plan, but=but)
                # Le joueur suit l'arrivée du compagnon choisi, sans changer ce choix.
                m.joueur.update(salle=but["lieu"], position=[1, 5] if but["lieu"] == "antichambre" else [2, 3], orientation="est")
                texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
                m = recharger(m)
                self.assertEqual(m.objets[id]["lieu"], m.objets[aime]["lieu"])
                self.assertIn("reste près " + ("d'Aubin" if aime == "aubin" else "de Gorm"), texte)

    def test_dans_la_meme_salle_il_se_place_pres_du_plus_aime(self):
        from tests.test_marche import intention
        from donjon.geometrie import distance
        for id in ("ilse", "brune"):
            for aime in ("aubin", "marchand"):
                m = calme(relais(), "ilse", "brune", "aubin", "marchand")
                placer(m, id, "antichambre", [4, 5])
                placer(m, "aubin", "antichambre", [1, 5])
                placer(m, "marchand", "antichambre", [7, 5])
                if id == "brune":
                    placer(m, "ilse", "echoppe", [3, 5])
                m.joueur.update(salle="antichambre", position=[2, 6] if aime == "aubin" else [6, 6], orientation="nord")
                lire(m, id)["relations"].clear()
                for x in ("aubin", "marchand"):
                    lien(m, id, x, affection=80 if x == aime else 20)
                    lire(m, x)["libre"] = 6000
                    croire(m, id, x, "lieu", "antichambre", "vu", salle="antichambre", case=m.objets[x]["position"])
                lire(m, id)["besoins"]["securite"] = 70
                intention(m, id, [{"operation": "abriter", "lieu": "antichambre"}], but={"type": "abri", "lieu": "antichambre"})
                m = recharger(m)
                texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre")))
                m = recharger(m)
                self.assertLessEqual(distance(m.objets[id]["position"], m.objets[aime]["position"]), 1)
                self.assertIn("reste près " + ("d'Aubin" if aime == "aubin" else "de Gorm"), texte)
