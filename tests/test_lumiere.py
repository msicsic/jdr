"""Avoir de la lumière : dans le noir, qui le craint cherche de quoi y voir, par les gestes
déclarés du planificateur ; une source qui consomme se recharge de ce qu'elle brûle, pour les
PNJ comme pour le joueur.

Chaque test vérifie l'état du monde après rechargement.
"""
import unittest

from donjon.banc_pnj import creer
from donjon.deplacement_objet import deplacer
from donjon.echanges import necessaire
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import ErreurMonde
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.planification import planifier_pulsion
from donjon.recit_pnj import but_en_mots
from tests.support import calme
from tests.test_tensions import chronique, recharger, relais, vivre

MINEURS = ("bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy")


def mine_noire(bois=False):
    """Placement d'auteur : la nuit est avancée, le poêle et la lampe du baraquement sont à sec et
    éteints ; personne ne presse, les rondes viennent d'être faites. Sans ``bois``, le bois du camp
    est brûlé : personne ne peut rallumer le poêle, le baraquement reste obscur."""
    m = creer("mine", 1985, "fixe")
    calme(m, *MINEURS)
    for k in ("lampe_baraque", "poele"):
        m.objets[k].update(allume=False, combustible=0)
    if not bois:
        for k in ("etais", "bois_gaspard"):
            m.objets[k]["charges"] = 0
    percevoir_tous(m)
    return m


def avec_briquet(m, id="remy"):
    """Placement d'auteur : Gaspard lui a donné son briquet."""
    deplacer(m, "briquet", id)
    m.objets["briquet"]["proprietaire"] = id
    return m


def inquiet(m, id="remy", securite=70.0):
    lire(m, id)["besoins"]["securite"] = securite
    percevoir_tous(m)
    return m


class MineTests(unittest.TestCase):
    def test_dans_le_noir_remy_allume_sa_lampe_au_briquet_et_la_garde_allumee(self):
        m = avec_briquet(mine_noire())
        m.objets["lampe_remy"]["allume"] = False
        m, _ = vivre(inquiet(m), 3)
        self.assertTrue(m.objets["lampe_remy"]["allume"])
        self.assertEqual(m.objets["lampe_remy"]["lieu"], "remy")
        self.assertIn("Rémy, jeune mineur allume la lampe de Rémy.", chronique(m))
        # Le baraquement reste obscur sans elle : il ne l'éteint pas pour la ménager.
        m, _ = vivre(m, 10)
        self.assertTrue(m.objets["lampe_remy"]["allume"])
        self.assertNotIn("Rémy, jeune mineur éteint la lampe de Rémy.", chronique(m))

    def test_le_poele_rallume_il_menage_sa_lampe(self):
        # Le poêle mort est une pulsion rompue de Josse : il obtient des bûches de Gaspard, qui
        # rallume le feu. Rémy, qui avait allumé sa lampe dans le noir, l'éteint quand le
        # baraquement est de nouveau éclairé ; la lampe que Gaspard porte n'y comptait pas.
        m = avec_briquet(mine_noire(bois=True))
        m.objets["etais"]["charges"] = 0
        m.objets["lampe_remy"]["allume"] = False
        m, _ = vivre(inquiet(m), 15)
        textes = chronique(m)
        self.assertTrue(m.objets["poele"]["allume"])
        self.assertLess(textes.index("Rémy, jeune mineur allume la lampe de Rémy."),
                        textes.index("Rémy, jeune mineur éteint la lampe de Rémy."))
        self.assertLess(textes.index("Gaspard, vieux mineur allume le poêle à bois."),
                        textes.index("Rémy, jeune mineur éteint la lampe de Rémy."))
        self.assertFalse(m.objets["lampe_remy"]["allume"])
        self.assertGreater(m.objets["lampe_remy"]["combustible"], 0)

    def test_sans_lampe_il_va_allumer_une_lampe_de_rechange(self):
        m = avec_briquet(mine_noire())
        del m.objets["lampe_remy"]
        lire(m, "remy")["croyances"].pop("lampe_remy", None)
        # Placement d'auteur : Josse a laissé la réserve ouverte, Rémy l'a vu.
        m.objets["porte_reserve"].update(verrouillee=False, ouverte=True)
        croire(m, "remy", "porte_reserve", "verrouillee", False, "vu")
        croire(m, "remy", "porte_reserve", "etat", {"ouverte": True}, "vu")
        m, _ = vivre(inquiet(m), 4)
        allumees = [k for k in ("lampe_rechange_1", "lampe_rechange_2") if m.objets[k]["allume"]]
        self.assertEqual(len(allumees), 1)
        self.assertEqual(m.objets["remy"]["lieu"], "reserve")
        self.assertIn("Rémy, jeune mineur allume la lampe de mineur de rechange.", chronique(m))

    def test_une_lampe_vide_se_remplit_d_huile_puis_s_allume(self):
        m = avec_briquet(mine_noire())
        m.objets["lampe_remy"].update(allume=False, combustible=0)
        deplacer(m, "bidon_huile", "remy")
        m, _ = vivre(inquiet(m), 4)
        lampe = m.objets["lampe_remy"]
        self.assertTrue(lampe["allume"])
        self.assertGreater(lampe["combustible"], 120 - 5)
        self.assertEqual(m.objets["bidon_huile"]["charges"], 2)
        textes = chronique(m)
        self.assertLess(textes.index("Rémy, jeune mineur alimente la lampe de Rémy."),
                        textes.index("Rémy, jeune mineur allume la lampe de Rémy."))

    def test_l_huile_ne_va_pas_au_poele_ni_le_bois_a_la_lampe(self):
        # Josse entretient son poêle avec des étais, pas avec l'huile des lampes, même portée.
        m = mine_noire(bois=True)
        m.objets["poele"]["combustible"] = 0
        for k in ("bidon_huile", "etais"):
            deplacer(m, k, "josse")
        croire(m, "josse", "poele", "etat", {"allume": False, "faible": False, "charge": False}, "vu")
        resultat = planifier_pulsion(m, "josse", {"objet": "poele", "allume": True})
        outils = {x["outil"] for x in resultat[1] if x["operation"] == "alimenter"}
        self.assertEqual(outils, {"etais"})

    def test_dans_la_lumiere_il_ne_cherche_rien(self):
        m = avec_briquet(creer("mine", 1985, "fixe"))
        calme(m, *MINEURS)
        m.objets["lampe_remy"]["allume"] = False
        m, _ = vivre(inquiet(m), 3)
        self.assertFalse(m.objets["lampe_remy"]["allume"])
        self.assertNotEqual((lire(m, "remy")["intention"] or {"but": {}})["but"].get("type"), "lumiere")

    def test_il_ne_prete_pas_la_lampe_qui_l_eclaire_dans_le_noir(self):
        m = mine_noire()
        self.assertTrue(m.objets["lampe_remy"]["allume"])
        self.assertTrue(necessaire(m, "remy", "lampe_remy"))
        # Dans la lumière, elle ne lui est pas nécessaire.
        lumineuse = creer("mine", 1985, "fixe")
        percevoir_tous(lumineuse)
        self.assertFalse(necessaire(lumineuse, "remy", "lampe_remy"))

    def test_avant_d_aller_dans_un_lieu_qu_il_sait_obscur_il_allume_sa_lampe(self):
        # Le poêle brûle au baraquement ; la galerie, Rémy l'a vue obscure. Le noir l'inquiète :
        # il allume sa lampe au poêle avant d'y aller. Gaspard, que le noir n'inquiète pas, y va tel quel.
        m = creer("mine", 1985, "fixe")
        calme(m, *MINEURS)
        m.objets["lampe_remy"]["allume"] = False
        m.objets["lampe_gaspard"]["allume"] = False
        m.objets["gaspard"].update(lieu="baraquement", position=[7, 4], position_salle="baraquement")
        percevoir_tous(m)
        ronde = {"lieu": "galerie", "periode": 60}
        for id in ("remy", "gaspard"):
            croire(m, id, "galerie", "etat", {"eclairee": False}, "vu")
            croire(m, id, "lampe_" + id, "etat", {"allume": False, "faible": False, "charge": True}, "vu")
        remy = [(x["operation"], x["cible"] or x["lieu"], x["outil"]) for x in planifier_pulsion(m, "remy", ronde)[1]]
        self.assertEqual(remy[1:], [("aller", "galerie", ""), ("inspecter", "galerie", "")])
        # Une flamme fixe du baraquement : la lampe suspendue ou le poêle.
        self.assertEqual(remy[0][:2], ("allumer", "lampe_remy"))
        self.assertIn(remy[0][2], ("lampe_baraque", "poele"))
        gaspard = [x["operation"] for x in planifier_pulsion(m, "gaspard", ronde)[1]]
        self.assertEqual(gaspard, ["aller", "inspecter"])


class MemoireTests(unittest.TestCase):
    def test_une_heure_dans_le_noir_ou_chaque_resultat_repris_ou_borne_est_recalcule(self):
        # La peur du noir, les sources, ce qu'elles brûlent : tout ce que lit la recherche de la
        # lumière entre dans sa mémoire (``planification._entrees``).
        from donjon import planification
        from donjon.planification import diagnostics
        m = avec_briquet(mine_noire())
        m.objets["lampe_remy"].update(allume=False, combustible=0)
        for id in ("remy", "lucien", "bram"):
            lire(m, id)["besoins"]["securite"] = 70.0
        avant, planification.VERIFIER = planification.VERIFIER, True
        try:
            with diagnostics() as recherches:
                m, _ = vivre(m, 60)
        finally:
            planification.VERIFIER = avant
        self.assertTrue(any(r["but"] == "lumiere" for r in recherches))
        self.assertTrue(any(r["memoire"] for r in recherches))


class RelaisTests(unittest.TestCase):
    def test_dans_l_echoppe_obscure_elle_rallume_le_brasero_au_briquet(self):
        m = relais()
        calme(m, "marchand", "brune", "ilse", "aubin")
        # Placement d'auteur : le brasero s'est éteint chargé ; Ilse s'y tient, le briquet en main ;
        # Gorm est aux vannes.
        m.objets["brasero"].update(allume=False, combustible=60)
        m.objets["marchand"].update(lieu="crypte", position=[5, 3], position_salle="crypte")
        m.objets["ilse"].update(lieu="echoppe", position=[3, 5], position_salle="echoppe")
        deplacer(m, "briquet", "ilse")
        m.objets["briquet"]["proprietaire"] = "ilse"
        percevoir_tous(m)
        croire(m, "ilse", "brasero", "etat", {"allume": False, "faible": False, "charge": True}, "vu")
        m, _ = vivre(inquiet(m, "ilse", 75.0), 3)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertIn("Ilse, meunière évacuée allume le brasero.", chronique(m))


class AubergeTests(unittest.TestCase):
    def test_au_cellier_obscur_elle_regagne_la_cuisine_eclairee(self):
        m = creer("auberge", 1985, "fixe")
        calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
        # Placement d'auteur : le bougeoir de Mireille s'est éteint au cellier.
        m.objets["bougeoir_mireille"]["allume"] = False
        m.objets["mireille"].update(lieu="cellier", position=[2, 3], position_salle="cellier")
        inquiet(m, "mireille")
        self.assertEqual(lire(m, "mireille")["croyances"]["cellier"]["etat"]["valeur"], {"eclairee": False})
        m, _ = vivre(m, 1)
        self.assertEqual(but_en_mots(m, lire(m, "mireille")["intention"]["but"]), "avoir de la lumière")
        m, _ = vivre(m, 3)
        self.assertEqual(m.objets["mireille"]["lieu"], "cuisine")
        self.assertTrue(lire(m, "mireille")["croyances"]["cuisine"]["etat"]["valeur"]["eclairee"])


class JoueurTests(unittest.TestCase):
    def lampe_vide(self):
        m = creer("mine", 1985, "fixe")
        # Placement d'auteur : le joueur a pris une lampe de rechange, vide, et le bidon d'huile.
        for k in ("lampe_rechange_1", "bidon_huile"):
            deplacer(m, k, "joueur")
        m.objets["lampe_rechange_1"]["combustible"] = 0
        return m

    def test_le_joueur_remplit_sa_lampe_d_huile(self):
        for geste in (etape("alimenter", "lampe_rechange_1", outil="bidon_huile"),
                      etape("alimenter", "lampe_rechange_1"),
                      etape("deplacer", "bidon_huile", "lampe_rechange_1")):
            with self.subTest(geste=geste["operation"], outil=geste["outil"]):
                m = self.lampe_vide()
                texte = Moteur(m).executer(Moteur(m).preparer(sequence(geste)))
                m = recharger(m)
                self.assertIn("La lampe de mineur de rechange est rechargée avec le bidon d'huile à lampe.", texte)
                self.assertEqual(m.objets["lampe_rechange_1"]["combustible"], 120)
                self.assertEqual(m.objets["bidon_huile"]["charges"], 2)
                self.assertEqual(m.objets["bidon_huile"]["lieu"], "joueur")
        # Rechargée, elle s'allume (le briquet est à Gaspard : la flamme du poêle, à portée).
        m.joueur.update(position=[5, 4])
        Moteur(m).executer(Moteur(m).preparer(sequence(etape("allumer", "lampe_rechange_1", outil="poele"))))
        self.assertTrue(recharger(m).objets["lampe_rechange_1"]["allume"])

    def test_chaque_source_se_recharge_de_ce_qu_elle_brule(self):
        m = self.lampe_vide()
        # Placement d'auteur : Josse a donné au joueur des étais, posés à ses pieds.
        m.objets["etais"].update(lieu="baraquement", position=[6, 4], position_salle="baraquement",
                                 proprietaire="joueur")
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(sequence(etape("alimenter", "lampe_rechange_1", outil="etais")))
        self.assertIn("brûle de l'huile", str(refus.exception))
        self.assertIn("bidon_huile", refus.exception.attendu)
        m.joueur.update(position=[5, 4], orientation="est")
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(sequence(etape("alimenter", "poele", outil="bidon_huile")))
        self.assertIn("brûle du bois", str(refus.exception))
        self.assertIn("etais", refus.exception.attendu)


if __name__ == "__main__":
    unittest.main()
