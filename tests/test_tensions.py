"""Jalon F : tensions du Relais — froid, feu entretenu, vivres comptés, demander avant de voler.

Chaque test vérifie l'état du monde et, quand le joueur est présent, ce qu'il lit, après
rechargement.
"""
from tests.revue_support import rapport as rapport_complet
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.commandes import analyser
from donjon.deliberation import REDEMANDE, candidats
# Scènes de mécanisme : ressources et liens déclarés avant les occasions 186.
from tests.scenarios_contractuels import nouveau_defi
from donjon.deplacement_objet import deplacer
from donjon.echanges import demander
from donjon.esprits import croire, lire, memoriser, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.pnj import avancer
from donjon.spatial import installer
from tests.support import calme, regarder, sans_le_sou


def recharger(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        return Monde.charger(chemin)


def relais():
    from tests.support import presentes
    m = presentes(nouveau_defi(depart="fixe"))
    installer(m)
    # Placement d'auteur : le joueur est monté à la galerie, loin des PNJ.
    m.joueur.update(salle="chambre_cloche", position=[1, 3])
    return m


def placer(monde, id, salle, case):
    monde.objets[id].update(lieu=salle, position=list(case), position_salle=salle)


def vivre(monde, minutes, jet=None):
    lignes = []
    monde.data["minutes"] += minutes
    if jet is None:
        avancer(monde, minutes, lignes)
    else:
        with patch.object(Monde, "d20", return_value=jet):
            avancer(monde, minutes, lignes)
    return recharger(monde), lignes


def attendre(monde, fois=1):
    texte = ""
    for _ in range(fois):
        texte += Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre"))) + "\n"
        monde = recharger(monde)
    return monde, texte


def chronique(monde):
    return [c["texte"] for c in monde.data.get("chronique", [])]


class FroidTests(unittest.TestCase):
    def test_trempes_ils_vont_se_chauffer_au_brasero_et_le_joueur_les_voit(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, "aubin")["besoins"]["chaleur"] = 80.0
        lire(m, "ilse")["besoins"]["chaleur"] = 75.0
        # Placement d'auteur : le joueur se tient dans la conduite, près du brasero.
        m.joueur.update(salle="echoppe", position=[4, 5])
        # Vingt-cinq minutes : réchauffés, ils sont encore là ; la ronde d'Aubin tombe à la trentième.
        m, texte = attendre(recharger(m), 5)
        for id, nom in (("aubin", "Aubin, vieux passeur"), ("ilse", "Ilse, meunière évacuée")):
            self.assertEqual(m.objets[id]["lieu"], "echoppe")
            self.assertLessEqual(lire(m, id)["besoins"]["chaleur"], 25)
            self.assertEqual(chronique(m).count(f"{nom} se chauffe près du brasero."), 1)
            self.assertIn(f"{nom} se chauffe près du brasero.", texte)

    def test_un_feu_eteint_ne_rechauffe_pas_et_corrige_ce_qu_il_croyait(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["brasero"].update(allume=False, combustible=0)
        lire(m, "aubin")["besoins"]["chaleur"] = 80.0
        # Placement d'auteur : Aubin a déjà brûlé ses planches, et Gorm son bois ; personne n'a de quoi
        # rallumer (demander à qui en aurait ne mène à rien : ``echanges.enqueter``).
        for bois in ("planches", "bois"):
            m.objets.pop(bois)
            for e in m.data["esprits"].values():
                e["croyances"].pop(bois, None)
        m, _ = vivre(m, 15)
        self.assertGreaterEqual(lire(m, "aubin")["besoins"]["chaleur"], 80)
        self.assertFalse(lire(m, "aubin")["croyances"]["brasero"]["etat"]["valeur"]["allume"])
        self.assertNotIn("Aubin, vieux passeur se chauffe près du brasero.", chronique(m))
        self.assertNotEqual((lire(m, "aubin")["intention"] or {}).get("motif"), "chaleur")


class FeuTests(unittest.TestCase):
    def gorm(self, combustible, **besoins):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["brasero"]["combustible"] = combustible
        lire(m, "marchand")["besoins"].update(devoir=80.0, **besoins)
        # De garde, ses rondes sont dues : elles le mènent là où il voit le feu.
        lire(m, "marchand")["visites"].clear()
        percevoir_tous(m)
        return m

    def test_gorm_va_chercher_son_bois_et_recharge_le_feu_qui_baisse(self):
        m = self.gorm(40)
        # Le joueur, dans la conduite, regarde le brasero : il voit Gorm revenir avec son bois.
        m.joueur.update(salle="echoppe", position=[4, 5])
        regarder(m, "joueur", "brasero")
        m, texte = attendre(recharger(m), 5)
        self.assertEqual(m.objets["bois"]["lieu"], "marchand")
        self.assertEqual(m.objets["bois"]["charges"], 1)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertGreater(m.objets["brasero"]["combustible"], 120)
        textes = chronique(m)
        self.assertLess(textes.index("Gorm, gardien du relais prend les fagots de bois sec."),
                        textes.index("Gorm, gardien du relais alimente le brasero."))
        self.assertIn("Gorm, gardien du relais alimente le brasero.", texte)

    def test_un_feu_qu_il_n_a_pas_revu_il_va_le_voir_avant_d_y_mettre_du_bois(self):
        m = self.gorm(150)
        placer(m, "marchand", "antichambre", [4, 1])
        croire(m, "marchand", "brasero", "etat", {"allume": True, "faible": False}, "vu")
        m.data["minutes"] += 40
        but, plan = next(r for _, methode in candidats(m, "marchand") if (r := methode(m, "marchand")))
        self.assertEqual(but, {"type": "pulsion", "objet": "brasero", "allume": True})
        self.assertEqual([(x["operation"], x["lieu"]) for x in plan], [("aller", "echoppe"), ("inspecter", "echoppe")])
        # Vu vif tout juste : rien à faire ; vu faible : il va chercher son bois.
        croire(m, "marchand", "brasero", "etat", {"allume": True, "faible": True}, "vu")
        but, plan = next(r for _, methode in candidats(m, "marchand") if (r := methode(m, "marchand")))
        self.assertIn(("prendre", "bois"), [(x["operation"], x["cible"]) for x in plan])
        self.assertEqual(plan[-1]["operation"], "alimenter")

    def test_le_feu_et_les_pnj_vivent_la_meme_minute(self):
        # Il reste trois minutes de feu : rechargé dans la minute, il ne s'éteint pas pendant l'attente.
        m = self.gorm(3)
        deplacer(m, "bois", "marchand")
        placer(m, "marchand", "echoppe", [3, 5])
        percevoir_tous(m)
        m, _ = attendre(recharger(m))
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertGreater(m.objets["brasero"]["combustible"], 100)

    def test_eteint_il_le_recharge_puis_le_rallume_s_il_a_de_quoi(self):
        m = self.gorm(0)
        m.objets["brasero"]["allume"] = False
        # Placement d'auteur : Gorm a ses fagots et le briquet que le joueur lui a laissé.
        deplacer(m, "bois", "marchand")
        deplacer(m, "briquet", "marchand")
        placer(m, "marchand", "echoppe", [3, 5])
        percevoir_tous(m)
        m, _ = vivre(m, 5)
        self.assertTrue(m.objets["brasero"]["allume"])
        # Dans le noir, il voit le feu éteint sans voir le foyer vide : son premier essai le lui
        # apprend ; il recharge une seule fois, allume, et le feu brûle depuis quelques minutes.
        self.assertGreaterEqual(m.objets["brasero"]["combustible"], 120 - 5)
        self.assertEqual(m.objets["bois"]["charges"], 1)
        textes = chronique(m)
        self.assertLess(textes.index("Gorm, gardien du relais alimente le brasero."),
                        textes.index("Gorm, gardien du relais allume le brasero."))
        # Sans rien pour l'allumer, il ne gaspille pas son bois dans un foyer froid.
        m = self.gorm(0)
        m.objets["brasero"]["allume"] = False
        # Placement d'auteur : aucune autre flamme au Relais, ni la torche ni le fanal.
        m.objets["torche"]["allume"] = False
        m.objets["fanal"]["allume"] = False
        deplacer(m, "bois", "marchand")
        placer(m, "marchand", "echoppe", [3, 5])
        percevoir_tous(m)
        m, _ = vivre(m, 5)
        self.assertEqual(m.objets["bois"]["charges"], 2)
        self.assertFalse(m.objets["brasero"]["allume"])

    def eteint_sans_briquet(self):
        """Brasero froid et vide, Gorm et ses fagots devant, sans outil d'allumage."""
        m = self.gorm(0)
        m.objets["brasero"]["allume"] = False
        # Placement d'auteur : Gorm n'a pas de quoi payer quelqu'un pour rallumer le feu à sa place
        # (``echanges.engager``) ; il s'y prend lui-même.
        m.data["finances_pnj"]["marchand"] = 0
        deplacer(m, "bois", "marchand")
        placer(m, "marchand", "echoppe", [3, 5])
        regarder(m, "marchand", "brasero")
        return m

    def test_dans_le_noir_il_voit_que_le_feu_ne_brille_plus(self):
        m = self.eteint_sans_briquet()
        m.objets["torche"]["allume"] = False
        croire(m, "marchand", "brasero", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        percevoir_tous(m)
        m = recharger(m)
        # Rien ne brille là où il regarde : éteint ; ce qui reste à brûler ne se voit pas.
        self.assertEqual(lire(m, "marchand")["croyances"]["brasero"]["etat"]["valeur"],
                         {"allume": False, "faible": False, "charge": True})
        # Hors de son regard, dans la galerie de la cloche, il garde ce qu'il croyait.
        placer(m, "marchand", "chambre_cloche", [1, 3])
        croire(m, "marchand", "brasero", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        percevoir_tous(m)
        self.assertTrue(lire(m, "marchand")["croyances"]["brasero"]["etat"]["valeur"]["allume"])

    def test_sans_briquet_il_rallume_le_brasero_a_la_torche(self):
        m = self.eteint_sans_briquet()
        # Placement d'auteur : la torche brûle au refuge.
        m.objets["torche"]["allume"] = True
        percevoir_tous(m)
        m, _ = vivre(m, 8)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertEqual(m.objets["torche"]["lieu"], "marchand")
        # Le feu pris, la torche ne sert plus : il l'éteint et la garde pour plus tard.
        self.assertFalse(m.objets["torche"]["allume"])
        self.assertGreater(m.objets["torche"]["combustible"], 0)
        textes = chronique(m)
        self.assertLess(textes.index("Gorm, gardien du relais allume le brasero."),
                        textes.index("Gorm, gardien du relais éteint la torche."))
        self.assertLess(textes.index("Gorm, gardien du relais prend la torche."),
                        textes.index("Gorm, gardien du relais alimente le brasero."))
        self.assertLess(textes.index("Gorm, gardien du relais alimente le brasero."),
                        textes.index("Gorm, gardien du relais allume le brasero."))

    def test_le_joueur_voit_gorm_rallumer_le_feu_a_la_torche_du_fanal(self):
        m = self.eteint_sans_briquet()
        m.objets["torche"]["allume"] = False
        # Le joueur, dans la conduite, sa lanterne allumée, assiste au retour du feu.
        m.joueur.update(salle="echoppe", position=[4, 5])
        percevoir_tous(m)
        m, texte = attendre(recharger(m), 3)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertIn("Gorm, gardien du relais allume le brasero.", texte)
        # Le feu pris, il garde la torche allumée pour sa ronde à la crypte, qu'il croit
        # obscure (le noir l'inquiète) ; il l'éteint là-bas, voyant qu'il y voit sans elle.
        textes = chronique(m)
        self.assertLess(textes.index("Gorm, gardien du relais allume le brasero."),
                        textes.index("Gorm, gardien du relais éteint la torche."))
        self.assertFalse(m.objets["torche"]["allume"])

    def test_une_flamme_employee_qui_ne_sert_plus_est_eteinte_et_gardee(self):
        m = self.gorm(150)
        # Placement d'auteur : Gorm tient la torche qui lui a servi, et une lanterne pour y voir.
        for id in ("torche", "lanterne"):
            deplacer(m, id, "marchand")
            m.objets[id]["allume"] = True
        memoriser(m, "marchand", {"type": "flamme_employee", "objet": "torche"})
        m, _ = vivre(m, 2)
        self.assertFalse(m.objets["torche"]["allume"])
        self.assertEqual(m.objets["torche"]["lieu"], "marchand")
        self.assertTrue(m.objets["lanterne"]["allume"])
        self.assertIn("Gorm, gardien du relais éteint la torche.", chronique(m))

    def test_torche_eteinte_il_l_allume_au_fanal_puis_rallume_le_brasero(self):
        m = self.eteint_sans_briquet()
        # Placement d'auteur : la torche est éteinte mais chargée ; seul le fanal brûle encore.
        m.objets["torche"]["allume"] = False
        percevoir_tous(m)
        m, _ = vivre(m, 12)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertTrue(m.objets["fanal"]["allume"])
        textes = chronique(m)
        self.assertLess(textes.index("Gorm, gardien du relais allume la torche."),
                        textes.index("Gorm, gardien du relais allume le brasero."))

    def test_la_flamme_meurt_en_route_il_le_constate(self):
        m = self.eteint_sans_briquet()
        # Placement d'auteur : la torche brûle ses dernières secondes au refuge, où Gorm l'a vue ;
        # le fanal est éteint.
        m.objets["torche"].update(allume=True, combustible=1)
        m.objets["fanal"]["allume"] = False
        croire(m, "marchand", "torche", "lieu", "antichambre", "vu", salle="antichambre",
               case=list(m.objets["torche"]["position"]))
        croire(m, "marchand", "torche", "etat", {"allume": True, "faible": True, "charge": True}, "vu")
        m.data["dixiemes"] = 550
        percevoir_tous(m)
        m, _ = vivre(m, 12)
        self.assertFalse(m.objets["brasero"]["allume"])
        self.assertFalse(m.objets["torche"]["allume"])
        etat = lire(m, "marchand")["croyances"]["torche"]["etat"]["valeur"]
        self.assertFalse(etat["allume"])
        self.assertFalse(etat["charge"])



class JoueurFeuTests(unittest.TestCase):
    def test_le_joueur_recharge_le_brasero_avec_du_bois_porte(self):
        m = relais()
        m.joueur.update(salle="echoppe", position=[3, 5])
        # Placement d'auteur : Gorm a confié ses fagots au joueur.
        deplacer(m, "bois", "joueur")
        avant = m.objets["brasero"]["combustible"]
        texte = Moteur(m).executer(Moteur(m).preparer(sequence(etape("alimenter", "brasero", outil="bois"))))
        m = recharger(m)
        self.assertIn("Le brasero est rechargé avec les fagots de bois sec.", texte)
        self.assertEqual(m.objets["bois"]["charges"], 1)
        self.assertEqual(m.objets["brasero"]["combustible"], avant + 120 - 1)
        # Même geste par la commande locale, jusqu'à épuiser le bois.
        Moteur(m).executer(Moteur(m).preparer(analyser(m, "alimenter brasero avec fagots")))
        m = recharger(m)
        self.assertEqual(m.objets["bois"]["charges"], 0)
        self.assertIn("Il n'en reste plus", Moteur(m).executer(Moteur(m).preparer(proposition("examiner", "bois"))))
        with self.assertRaisesRegex(ErreurMonde, "Il faut porter un combustible"):
            Moteur(m).preparer(sequence(etape("alimenter", "brasero", outil="bois")))
        # La lanterne ne déclare pas ce qu'elle brûle : elle est son propre réservoir.
        with self.assertRaisesRegex(ErreurMonde, "ne se recharge pas"):
            Moteur(m).preparer(sequence(etape("alimenter", "lanterne", outil="bois")))

    def test_le_joueur_allume_sa_lanterne_au_brasero_sans_briquet(self):
        m = relais()
        m.joueur.update(salle="echoppe", position=[3, 5])
        # Placement d'auteur : le briquet est resté au refuge, la lanterne s'est éteinte.
        placer(m, "briquet", "antichambre", (2, 2))
        m.objets["lanterne"]["allume"] = False
        plan = Moteur(m).preparer(sequence(etape("allumer", "lanterne")))
        self.assertEqual(plan.plans[0].titre, "Allumer la lanterne avec le brasero.")
        Moteur(m).executer(plan)
        m = recharger(m)
        self.assertTrue(m.objets["lanterne"]["allume"])
        self.assertTrue(m.objets["brasero"]["allume"])
        # Loin du brasero, la flamme n'est pas à portée ; une source fixe ne vient pas à soi.
        m.objets["lanterne"]["allume"] = False
        m.joueur.update(position=[5, 2])
        with self.assertRaisesRegex(ErreurMonde, "autre flamme"):
            Moteur(m).preparer(sequence(etape("allumer", "lanterne")))
        # Lanterne rallumée pour y voir : le fanal, fixe, n'atteint pas le brasero, fixe aussi.
        m.joueur.update(position=[3, 5])
        m.objets["lanterne"]["allume"] = True
        m.objets["brasero"]["allume"] = False
        with self.assertRaisesRegex(ErreurMonde, "autre flamme"):
            Moteur(m).preparer(sequence(etape("allumer", "brasero", outil="fanal")))

    def bois_au_sol(self, case=(4, 5), proprietaire="joueur"):
        m = relais()
        m.joueur.update(salle="echoppe", position=[3, 5])
        placer(m, "bois", "echoppe", case)
        # Placement d'auteur : Gorm a donné ses fagots au joueur, posés près du brasero.
        m.objets["bois"]["proprietaire"] = proprietaire
        return m

    def test_mettre_du_bois_dans_le_brasero_le_recharge_sans_emporter_le_tas(self):
        for geste in (etape("deplacer", "bois", "brasero"), etape("alimenter", "brasero", outil="bois"),
                      etape("alimenter", "brasero")):
            with self.subTest(geste=geste["operation"], outil=geste["outil"]):
                m = self.bois_au_sol()
                avant = m.objets["brasero"]["combustible"]
                texte = Moteur(m).executer(Moteur(m).preparer(sequence(geste)))
                m = recharger(m)
                self.assertIn("Le brasero est rechargé avec les fagots de bois sec.", texte)
                self.assertEqual(m.objets["bois"]["charges"], 1)
                self.assertEqual(m.objets["brasero"]["combustible"], avant + 120 - 1)
                # La brassée est prise sur le tas : les fagots restent au sol, près du brasero.
                self.assertEqual(m.objets["bois"]["lieu"], "echoppe")
                self.assertEqual(m.objets["bois"]["position"], [4, 5])

    def test_ramasser_le_tas_puis_le_mettre_au_feu(self):
        m = self.bois_au_sol()
        Moteur(m).executer(Moteur(m).preparer(sequence(etape("deplacer", "bois", "joueur"),
                                                       etape("deplacer", "bois", "brasero"))))
        m = recharger(m)
        self.assertEqual(m.objets["bois"]["lieu"], "joueur")
        self.assertEqual(m.objets["bois"]["charges"], 1)

    def test_le_foyer_ne_recoit_que_du_combustible_a_portee_et_a_soi(self):
        m = self.bois_au_sol(case=(5, 2))
        with self.assertRaisesRegex(ErreurMonde, "Approche-toi des fagots"):
            Moteur(m).preparer(sequence(etape("deplacer", "bois", "brasero")))
        m = self.bois_au_sol(proprietaire="marchand")
        with self.assertRaisesRegex(ErreurMonde, "appartient à autrui"):
            Moteur(m).preparer(sequence(etape("deplacer", "bois", "brasero")))
        m = self.bois_au_sol()
        m.objets["bois"]["charges"] = 0
        with self.assertRaisesRegex(ErreurMonde, "Il faut porter un combustible"):
            Moteur(m).preparer(sequence(etape("deplacer", "bois", "brasero")))
        with self.assertRaisesRegex(ErreurMonde, "n'est pas un contenant"):
            Moteur(m).preparer(sequence(etape("deplacer", "lanterne", "brasero")))

    def test_console_mettre_une_brassee_au_feu_enregistre_avant_affichage(self):
        import io
        import jeu
        from donjon.mj import MJOpenAI
        m = self.bois_au_sol()
        avant = m.objets["brasero"]["combustible"]
        proposee = sequence(etape("deplacer", "bois", "brasero"))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "defi.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=lambda *a: (
                      rapport_complet(a[1], True, "") if a[3] == "auditer_action" else
                      {"mode": "action", "texte": "", "faits": [], "proposition": proposee})),
                  patch("builtins.input", side_effect=[
                      "je ramasse les fagots et j'en mets une brassée dans le feu du brasero", "tenter", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--defi", "--save", str(chemin),
                                           "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("Le brasero est rechargé avec les fagots de bois sec.", sortie.getvalue())
        self.assertEqual(reprise.objets["bois"]["charges"], 1)
        self.assertEqual(reprise.objets["brasero"]["combustible"], avant + 120 - 1)
        self.assertEqual(reprise.objets["bois"]["lieu"], "echoppe")
        echange = reprise.data["conversation"][-1]
        self.assertEqual(echange["nature"], "resultat_moteur")
        self.assertIn("Le brasero est rechargé avec les fagots de bois sec.", echange["reponse"])


class PartTests(unittest.TestCase):
    def affamee(self, id, faim=85.0):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, id)["besoins"]["faim"] = faim
        return m

    def test_brune_demande_d_abord_et_gorm_la_sert(self):
        m = self.affamee("brune")
        # Aucun don spontané ne doit remplacer cette demande et sa livraison.
        from tests.support import sans_souci
        sans_souci(m)
        m, _ = vivre(m, 20, jet=20)
        textes = chronique(m)
        self.assertIn("Brune demande une part des vivres du refuge à Gorm (promis).", textes)
        self.assertEqual(m.objets["vivres"]["portions"], 3)
        self.assertEqual(m.objets["crochets"]["lieu"], "echoppe")
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertLess(lire(m, "brune")["besoins"]["faim"], 70)

    def test_refusee_brune_se_tourne_vers_le_vol(self):
        m = sans_le_sou(self.affamee("brune"), "brune")
        # Le refus laisse son recours au vol nécessaire, sans aide des témoins.
        from tests.support import sans_souci
        sans_souci(m)
        m, _ = vivre(m, 8, jet=1)
        self.assertIn("Brune demande une part des vivres du refuge à Gorm ; contre-offre annoncée (refus).", chronique(m))
        intention = lire(m, "brune")["intention"]
        self.assertEqual(intention["but"], {"type": "manger", "objet": "vivres"})
        self.assertEqual(intention["plan"][-1]["condition"], "sans_temoin")

    def test_ilse_sans_le_sou_retient_la_condition_sans_redemander_avec_le_temps(self):
        m = sans_le_sou(self.affamee("ilse"), "ilse")
        # Pas de tiers qui fournisse ou fasse inspecter la part refusée.
        from tests.support import sans_souci
        sans_souci(m)
        m, _ = vivre(m, 10, jet=1)
        self.assertEqual(chronique(m).count("Ilse demande une part des vivres du refuge à Gorm ; contre-offre annoncée (refus)."), 1)
        m, _ = vivre(m, REDEMANDE - 20, jet=1)
        self.assertEqual(chronique(m).count("Ilse demande une part des vivres du refuge à Gorm ; contre-offre annoncée (refus)."), 1)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertEqual(m.objets["vivres"]["portions"], 4)
        m, _ = vivre(m, 30, jet=20)
        self.assertNotIn("Ilse demande une part des vivres du refuge à Gorm (promis).", chronique(m))
        self.assertTrue(any(s.get("objet") == "vivres" and "contre_offre" in s for s in lire(m, "ilse")["refus"]))

    def test_refusee_ilse_achete_sa_part_avec_sa_bourse(self):
        # Même refus, mais elle a huit pièces : elle paie le prix dit (2), que Gorm accepte
        # sans se faire prier, et il la sert.
        m = self.affamee("ilse")
        # Seul l'achat de sa propre part est en jeu ; Aubin ne finance pas
        # en parallèle une part destinée à secourir un tiers.
        from tests.support import sans_souci
        sans_souci(m)
        self.assertEqual((m.data["finances_pnj"]["ilse"], m.data["finances_pnj"]["marchand"]), (8, 50))
        m, _ = vivre(m, 20, jet=1)
        textes = chronique(m)
        self.assertEqual(textes.count("Ilse demande une part des vivres du refuge à Gorm ; contre-offre annoncée (refus)."), 1)
        self.assertIn("Ilse achète une part des vivres du refuge à Gorm pour 2 pièces ; condition remplie (vendu).", textes)
        self.assertTrue(any(t.startswith("Gorm") and "donne une part des vivres du refuge" in t and "Ilse" in t
                            for t in textes))
        self.assertEqual((m.data["finances_pnj"]["ilse"], m.data["finances_pnj"]["marchand"]), (6, 52))
        self.assertEqual(m.objets["vivres"]["portions"], 3)
        self.assertTrue(any(s["type"] == "vente" and s["a"] == "ilse" and s["prix"] == 2
                            for s in lire(m, "marchand")["memoire"]))

    def test_elle_cherche_gorm_dont_elle_a_perdu_la_trace(self):
        m = self.affamee("ilse")
        # Placement d'auteur : Gorm est descendu aux vannes sans qu'Ilse le voie partir.
        placer(m, "marchand", "crypte", [2, 2])
        croire(m, "ilse", "marchand", "lieu", None, "vu", salle=None, case=None)
        m, _ = vivre(m, 30, jet=20)
        self.assertIn("Ilse demande une part des vivres du refuge à Gorm (promis).", chronique(m))
        self.assertTrue(lire(m, "ilse")["visites"])  # Elle a parcouru des salles pour le trouver.

    def test_la_parole_donnee_passe_avant_la_ronde_et_ne_rouvre_pas_sa_reserve_en_boucle(self):
        m = self.affamee("brune", 60.0)
        lire(m, "marchand")["besoins"].update(devoir=90.0, biens=80.0)
        placer(m, "marchand", "antichambre", [6, 3])
        placer(m, "brune", "antichambre", [7, 2])
        percevoir_tous(m)
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "brune", "marchand", "vivres"), "promis")
        m, _ = vivre(m, 15)
        textes = chronique(m)
        self.assertIn("Gorm donne une part des vivres du refuge à Brune.", textes)
        self.assertEqual(textes.count("Gorm, gardien du relais déverrouille la réserve de vivres."), 1)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertFalse(m.objets["reserve"]["ouverte"])

    def test_apres_avoir_mange_il_referme_sa_reserve(self):
        m = self.affamee("marchand")
        lire(m, "marchand")["besoins"]["biens"] = 80.0
        placer(m, "marchand", "antichambre", [6, 3])
        percevoir_tous(m)
        m, _ = vivre(m, 15)
        textes = chronique(m)
        self.assertIn("Gorm, gardien du relais mange une part des vivres du refuge.", textes)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertFalse(m.objets["reserve"]["ouverte"])
        self.assertNotIn("atteinte", [s["type"] for s in lire(m, "marchand")["memoire"]])


if __name__ == "__main__":
    unittest.main()
