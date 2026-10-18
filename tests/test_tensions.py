"""Jalon F : tensions du Relais — froid, feu entretenu, vivres comptés, demander avant de voler.

Chaque test vérifie l'état du monde et, quand le joueur est présent, ce qu'il lit, après
rechargement.
"""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.commandes import analyser
from donjon.deliberation import REDEMANDE, candidats
from donjon.defi import nouveau_defi
from donjon.deplacement_objet import deplacer
from donjon.echanges import demander
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.pnj import avancer
from donjon.spatial import installer


def recharger(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        return Monde.charger(chemin)


def relais():
    m = nouveau_defi()
    installer(m)
    # Placement d'auteur : le joueur est monté à la galerie, loin des PNJ.
    m.joueur.update(salle="chambre_cloche", position=[1, 3])
    return m


def placer(monde, id, salle, case):
    monde.objets[id].update(lieu=salle, position=list(case), position_salle=salle)


def calme(monde, *ids):
    """Placement d'auteur : ces PNJ n'ont aucun besoin pressant et restent où ils sont."""
    for id in ids:
        besoins = lire(monde, id)["besoins"]
        for b in besoins:
            besoins[b] = 0.0
    return monde


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
        m, texte = attendre(recharger(m), 6)
        for id, nom in (("aubin", "Aubin, vieux passeur"), ("ilse", "Ilse, meunière évacuée")):
            self.assertEqual(m.objets[id]["lieu"], "echoppe")
            self.assertLessEqual(lire(m, id)["besoins"]["chaleur"], 25)
            self.assertEqual(chronique(m).count(f"{nom} se chauffe près du brasero."), 1)
            self.assertIn(f"{nom} se chauffe près du brasero.", texte)

    def test_un_feu_eteint_ne_rechauffe_pas_et_corrige_ce_qu_il_croyait(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["brasero"].update(allume=False, combustible=0)
        lire(m, "aubin")["besoins"]["chaleur"] = 80.0
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
        percevoir_tous(m)
        return m

    def test_gorm_va_chercher_son_bois_et_recharge_le_feu_qui_baisse(self):
        m = self.gorm(40)
        # Le joueur, dans la conduite, voit Gorm revenir avec son bois.
        m.joueur.update(salle="echoppe", position=[4, 5])
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
        self.assertEqual(m.objets["brasero"]["combustible"], 120 - 3)
        textes = chronique(m)
        self.assertLess(textes.index("Gorm, gardien du relais alimente le brasero."),
                        textes.index("Gorm, gardien du relais allume le brasero."))
        # Sans rien pour l'allumer, il ne gaspille pas son bois dans un foyer froid.
        m = self.gorm(0)
        m.objets["brasero"]["allume"] = False
        deplacer(m, "bois", "marchand")
        placer(m, "marchand", "echoppe", [3, 5])
        percevoir_tous(m)
        m, _ = vivre(m, 5)
        self.assertEqual(m.objets["bois"]["charges"], 2)
        self.assertFalse(m.objets["brasero"]["allume"])


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
        with self.assertRaisesRegex(ErreurMonde, "n'est pas un foyer"):
            Moteur(m).preparer(sequence(etape("alimenter", "lanterne", outil="bois")))


class PartTests(unittest.TestCase):
    def affamee(self, id, faim=85.0):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, id)["besoins"]["faim"] = faim
        return m

    def test_brune_demande_d_abord_et_gorm_la_sert(self):
        m = self.affamee("brune")
        m, _ = vivre(m, 20, jet=20)
        textes = chronique(m)
        self.assertIn("Brune demande une part des vivres du refuge à Gorm (promis).", textes)
        self.assertEqual(m.objets["vivres"]["portions"], 3)
        self.assertEqual(m.objets["crochets"]["lieu"], "echoppe")
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertLess(lire(m, "brune")["besoins"]["faim"], 70)

    def test_refusee_brune_se_tourne_vers_le_vol(self):
        m = self.affamee("brune")
        m, _ = vivre(m, 8, jet=1)
        self.assertIn("Brune demande une part des vivres du refuge à Gorm (refus).", chronique(m))
        intention = lire(m, "brune")["intention"]
        self.assertEqual(intention["but"], {"type": "manger", "objet": "vivres"})
        self.assertEqual(intention["plan"][-1]["condition"], "sans_temoin")

    def test_ilse_refusee_ne_vole_pas_et_redemande_plus_tard(self):
        m = self.affamee("ilse")
        m, _ = vivre(m, 10, jet=1)
        self.assertEqual(chronique(m).count("Ilse demande une part des vivres du refuge à Gorm (refus)."), 1)
        m, _ = vivre(m, REDEMANDE - 20, jet=1)
        self.assertEqual(chronique(m).count("Ilse demande une part des vivres du refuge à Gorm (refus)."), 1)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertEqual(m.objets["vivres"]["portions"], 4)
        m, _ = vivre(m, 30, jet=20)
        self.assertIn("Ilse demande une part des vivres du refuge à Gorm (promis).", chronique(m))

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
