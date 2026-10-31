"""La crue : un niveau d'eau tiré de la graine, des salles mouillées puis noyées, et ce qui en
découle pour tous, joueur compris : se tremper, perdre le feu, ne plus passer, fuir vers le haut.

Chaque test contrôle l'état du monde, et ce que le joueur lit quand il est concerné, après
rechargement.
"""
import copy
import random
import unittest

from donjon import eau
from tests.scenarios_contractuels import donnees, nouvelle_crue, nouveau_defi
from donjon.esprits import croire, lire, percevoir
from donjon.monde import ErreurMonde, Monde, nouveau_monde_libre, objet
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.spatial import installer
from tests.support import calme
from tests.test_tensions import placer, recharger

# Bornes resserrées sur une valeur : la montée est connue d'avance (1 cm par minute depuis -150,
# jusqu'à +60 cm au pic, à la cinquième heure).
FIXES = {"montee_cm_heure": [60, 60], "heure_pic": [5, 5], "hauteur_pic_cm": [60, 60]}


def crue(bornes=None, graine=1985):
    """La crue du Relais ; des bornes fixées rendent le niveau connu d'avance."""
    data = donnees('crue')
    data["seed"] = graine
    data["depart"]["mode"] = "fixe"   # Placement d'auteur : le départ déclaré.
    if bornes:
        data["crue"]["bornes"] = copy.deepcopy(bornes)
    m = Monde(data)
    installer(m)
    # Placement d'auteur : le joueur est monté à la galerie, loin des PNJ.
    m.joueur.update(salle="chambre_cloche", position=[1, 3])
    return m


def attendre(monde, jusqu_a):
    """Le joueur attend, cinq minutes à la fois, par le moteur réel ; renvoie le monde rechargé
    et ce qu'il a lu."""
    lu = []
    while monde.data["minutes"] < jusqu_a:
        lu.append(Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre"))))
    return recharger(monde), "\n".join(lu)


class TirageTests(unittest.TestCase):
    def test_la_crue_est_tiree_de_la_graine_a_part_des_jets(self):
        m = nouvelle_crue(7, "fixe")
        b = m.data["crue"]["bornes"]
        r = random.Random("7:crue")
        montee = r.randint(*b["montee_cm_heure"])
        attendu = {"montee_cm_heure": montee, "minute_pic": r.randint(b["heure_pic"][0] * 60, b["heure_pic"][1] * 60),
                   "hauteur_pic_cm": r.randint(*b["hauteur_pic_cm"]), "baisse_cm_heure": r.randint(*b["baisse_cm_heure"])}
        self.assertEqual(m.data["crue"]["tirage"], attendu)
        niveaux = [eau.niveau(m, t) for t in range(0, 480, 30)]
        for _ in range(20):
            m.d20()
        reprise = recharger(m)
        self.assertEqual(reprise.data["crue"]["tirage"], attendu)
        self.assertEqual([eau.niveau(reprise, t) for t in range(0, 480, 30)], niveaux)
        self.assertEqual(nouvelle_crue(7, "fixe").data["crue"]["tirage"], attendu)
        self.assertNotEqual(nouvelle_crue(8, "fixe").data["crue"]["tirage"], attendu)

    def test_les_valeurs_tirees_restent_dans_les_bornes(self):
        for graine in range(30):
            m = nouvelle_crue(graine, "fixe")
            b, x = m.data["crue"]["bornes"], m.data["crue"]["tirage"]
            self.assertTrue(b["montee_cm_heure"][0] <= x["montee_cm_heure"] <= b["montee_cm_heure"][1])
            self.assertTrue(b["heure_pic"][0] * 60 <= x["minute_pic"] <= b["heure_pic"][1] * 60)
            self.assertTrue(b["hauteur_pic_cm"][0] <= x["hauteur_pic_cm"] <= b["hauteur_pic_cm"][1])
            # Au départ, l'eau est sous les salles basses.
            self.assertEqual(m.data["crue"]["historique"], [])

    def test_l_eau_monte_se_tient_au_plafond_puis_baisse(self):
        m = crue({**FIXES, "hauteur_pic_cm": [-100, -100], "baisse_cm_heure": [30, 30]})
        self.assertEqual([eau.niveau(m, t) for t in (0, 30, 50, 120, 300, 360, 1000)],
                         [-150, -120, -100, -100, -100, -130, -150])

    def test_le_jeu_et_le_banc_lancent_la_crue(self):
        import io
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import jeu
        from donjon.banc_pnj import creer
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "crue.json"
            with (patch("builtins.input", side_effect=["attendre", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--crue", "--console", "--offline", "--seed", "42",
                                           "--save", str(chemin)]), 0)
            self.assertIn("l'eau suinte par les vannes", sortie.getvalue())
            reprise = Monde.charger(chemin)
        self.assertTrue(reprise.data["mode_cases"])
        self.assertEqual(reprise.data["crue"]["tirage"], nouvelle_crue(42, "fixe").data["crue"]["tirage"])
        # « attendre » : cinq minutes, sauf si quelqu'un paraît (``Moteur._attendre``) ; la sauvegarde
        # garde le temps que le joueur a lu.
        from donjon.temps import instant
        from tests.test_attente import annonce
        lu = next(l for l in sortie.getvalue().splitlines() if l.startswith(("Tu attends ", "Au bout de ")))
        self.assertEqual(instant(reprise), annonce(lu))
        self.assertEqual(creer("crue", 42, "fixe").data["crue"]["tirage"], reprise.data["crue"]["tirage"])

    def test_le_relais_n_a_pas_de_crue(self):
        m = nouveau_defi(depart="fixe")
        installer(m)
        self.assertFalse(eau.active(m))
        self.assertEqual(eau.profondeur(m, "echoppe"), 0)
        self.assertNotIn("eau", m.contexte()["salle"])
        self.assertNotIn("crue", recharger(m).data)


class SallesTests(unittest.TestCase):
    def test_les_salles_basses_sont_mouillees_puis_noyees_selon_leur_altitude(self):
        m, _ = attendre(crue(FIXES), 140)
        # Niveau -10 : la conduite (-120) est noyée, la salle des vannes (-100) presque.
        self.assertEqual(eau.niveau(m), -10)
        self.assertEqual(m.data["crue"]["etats"], {"antichambre": "seche", "beffroi": "mouillee",
                                                   "chambre_cloche": "seche", "crypte": "mouillee",
                                                   "echoppe": "noyee"})
        self.assertEqual([(h["salle"], h["etat"]) for h in m.data["crue"]["historique"] if "etat" in h],
                         [("echoppe", "mouillee"), ("crypte", "mouillee"), ("beffroi", "mouillee"),
                          ("echoppe", "noyee")])
        self.assertEqual(eau.profondeur(m, "crypte"), 90)

    def test_le_feu_d_une_salle_noyee_s_eteint_et_n_y_reprend_pas(self):
        m = calme(crue(FIXES), "marchand", "brune", "ilse", "aubin")
        m.objets["lanterne"]["combustible"] = 600      # Placement d'auteur : une lanterne pleine.
        self.assertTrue(m.objets["brasero"]["allume"])
        m, _ = attendre(m, 135)
        self.assertFalse(m.objets["brasero"]["allume"])
        self.assertGreater(m.objets["brasero"]["combustible"], 0)  # Noyé, pas consumé.
        self.assertIn({"minute": 130, "eteint": "brasero", "salle": "echoppe"}, m.data["crue"]["historique"])
        # Le joueur, pris par l'eau près du brasero, ne le rallume pas : sous l'eau, rien ne prend.
        m.joueur.update(salle="echoppe", position=[4, 4], orientation="ouest")
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(proposition("allumer", "brasero", "briquet"))
        self.assertIn("sous l'eau", str(refus.exception))
        self.assertIn("brasero", refus.exception.attendu)
        # Sa lanterne, portée hors de l'eau, brûle encore.
        self.assertTrue(recharger(m).objets["lanterne"]["allume"])


class JoueurTests(unittest.TestCase):
    def test_entrer_dans_l_eau_trempe_et_le_joueur_le_voit(self):
        m, _ = attendre(crue(FIXES), 60)          # 30 cm dans la conduite
        m.joueur.update(salle="antichambre", position=[0, 3], orientation="ouest")
        self.assertEqual(m.joueur["corps"]["trempe"], 0)
        texte = Moteur(m).executer(Moteur(m).preparer(proposition("marcher", "ouest")))
        self.assertIn("Tu entres dans : Conduite basse.", texte)
        self.assertIn("L'eau t'arrive aux genoux : te voilà trempé.", texte)
        reprise = recharger(m)
        self.assertGreater(reprise.joueur["corps"]["trempe"], 0)
        self.assertIn("L'eau couvre le sol : elle t'arrive aux genoux (30 cm).", " ".join(regarder(reprise).split()))
        self.assertEqual(reprise.contexte()["salle"]["eau"],
                         {"etat": "mouillee", "profondeur_cm": 30, "hauteur": "aux genoux"})

    def test_debout_dans_l_eau_on_ne_seche_pas_meme_pres_du_feu(self):
        m, _ = attendre(crue(FIXES), 60)
        m.joueur.update(salle="echoppe", position=[4, 4], orientation="ouest")
        m.joueur["corps"].update(trempe=10, seche=0)
        m, _ = attendre(m, 100)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertGreaterEqual(m.joueur["corps"]["trempe"], 50)
        self.assertEqual(m.joueur["corps"]["seche"], 0)

    def test_une_salle_noyee_ne_se_traverse_plus(self):
        m, _ = attendre(crue(FIXES), 140)
        m.joueur.update(salle="antichambre", position=[0, 3], orientation="ouest")
        from donjon.pnj import ecarter
        ecarter(m)  # Placement d'auteur : qui se tenait sur ce seuil s'écarte.
        self.assertIn("ouest (inexploré, eau trop haute pour passer)", regarder(m))
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(proposition("marcher", "ouest"))
        self.assertIn("trop haute", str(refus.exception))
        self.assertIn("echoppe", refus.exception.attendu)
        self.assertEqual(recharger(m).joueur["salle"], "antichambre")


class PnjTests(unittest.TestCase):
    def test_un_pnj_voit_l_eau_et_ne_passe_plus_par_une_salle_noyee(self):
        from donjon.pnj import chemin
        from donjon.planification import planifier_pulsion
        m = calme(crue(FIXES), "marchand", "brune", "ilse", "aubin")
        placer(m, "aubin", "antichambre", (1, 3))
        self.assertIsNotNone(chemin(m, "aubin", "antichambre", "crypte"))
        m, _ = attendre(m, 140)
        placer(m, "aubin", "antichambre", (1, 3))
        percevoir(m, "aubin")
        m = recharger(m)
        # Du refuge, il voit la conduite noyée par le passage ouvert : il la croit telle.
        self.assertEqual(lire(m, "aubin")["croyances"]["echoppe"]["eau"]["valeur"], 110)
        self.assertIsNone(chemin(m, "aubin", "antichambre", "crypte"))
        # Gorm, qui l'a vue de même, ne trouve plus de geste pour entretenir le brasero.
        placer(m, "marchand", "antichambre", (2, 2))
        percevoir(m, "marchand")
        self.assertIsNone(planifier_pulsion(m, "marchand", {"objet": "brasero", "allume": True}))

    def test_le_feu_noye_on_ne_demande_plus_de_bois_pour_lui(self):
        from donjon.planification import planifier
        m = calme(crue(FIXES), "marchand", "brune", "ilse", "aubin")
        placer(m, "ilse", "antichambre", (1, 3))
        placer(m, "marchand", "antichambre", (2, 2))
        m.objets["brasero"]["allume"] = False
        croire(m, "ilse", "brasero", "etat", {"allume": False, "faible": False, "charge": True}, "vu")
        # Placement d'auteur : le poêle du guet, à la galerie, est froid et vide ; allumé, elle y
        # monterait se chauffer, hors de l'eau (branche ``ressources``).
        m.objets["poele_guet"].update(allume=False, combustible=0)
        croire(m, "ilse", "poele_guet", "etat", {"allume": False, "faible": False, "charge": False}, "vu")
        percevoir(m, "ilse")
        # Feu éteint : elle le rallumerait (une torche au fanal), ou demanderait du bois à Gorm.
        but, etapes = planifier(m, "ilse", "chaleur")
        self.assertIn("brasero", [x["cible"] for x in etapes] + [but.get("objet")] + [
            (x.get("contenu") or {}).get("foyer") for x in etapes])
        m, _ = attendre(m, 140)
        placer(m, "ilse", "antichambre", (1, 3))
        placer(m, "marchand", "antichambre", (2, 2))
        percevoir(m, "ilse")
        # La conduite noyée, le brasero est sous l'eau, et le poêle du guet coupé d'elle par la
        # conduite : rien à demander.
        self.assertIsNone(planifier(recharger(m), "ilse", "chaleur"))

    def test_un_pnj_dans_l_eau_se_trempe_et_s_en_inquiete(self):
        from donjon.corps import vivre
        from donjon.deliberation import ressentir
        m = calme(crue(FIXES), "marchand", "brune", "ilse", "aubin")
        placer(m, "marchand", "echoppe", (1, 1))
        m.data["minutes"] = 80            # 50 cm dans la conduite
        m = recharger(m)
        besoins = lire(m, "marchand")["besoins"]
        besoins["securite"] = 10.0
        ressentir(m, "marchand")
        # 50 cm d'eau : deux points par minute ; le brasero l'éclaire, ce qui rassure un peu.
        self.assertAlmostEqual(besoins["securite"], 10 + 2 - 0.2)
        percevoir(m, "marchand")
        # La voir gagner sa salle, et la salle des vannes par le passage ouvert.
        self.assertAlmostEqual(besoins["securite"], 10 + 2 - 0.2 + 2 * 10)
        vivre(m, "marchand", 3)
        m = recharger(m)
        self.assertEqual(m.objets["marchand"]["corps"]["trempe"], 3)
        self.assertEqual(lire(m, "marchand")["croyances"]["echoppe"]["eau"]["valeur"], 50)

    def test_l_eau_qui_monte_fait_fuir_vers_la_galerie(self):
        m = calme(crue(FIXES), "marchand", "brune", "aubin")
        # Ilse réagit ici à l'eau elle-même, sans demande d'évacuation de Gorm.
        m.objets["marchand"]["profil"]["agendas"] = []
        # Ilse craint la crue (sa sécurité presse déjà) ; elle se tient au refuge, près de la conduite.
        # Gorm a laissé ouverte la porte étanche : Ilse ne sait pas où est la clé.
        placer(m, "ilse", "antichambre", (1, 3))
        m.objets["porte"].update(ouverte=True, verrouillee=False)
        m, _ = attendre(m, 80)
        e = lire(m, "ilse")
        # Depuis le 374, elle gagne l'abri dès 31, avant un second relevé
        # personnel de l'eau. Le départ sûr ne prouve pas sa vitesse : la
        # première observation est conservée, aucune pente n'est inventée.
        conduite = e['croyances']['echoppe']['eau']
        self.assertEqual(conduite['source'], 'vu')
        self.assertGreater(conduite['valeur'], 0)
        self.assertIsNone(conduite['montee'])
        self.assertIsNone(eau.estimation(m, "ilse"))
        self.assertEqual(m.objets["ilse"]["lieu"], "chambre_cloche")
        # Elle conserve son abri sec en hauteur, sans lui attribuer une
        # prévision de montée qu'elle n'a pas pu mesurer avant de partir.
        intention = e["intention"]
        if intention and intention["but"] != {"type": "abri", "lieu": "chambre_cloche"}:
            # Le contrat 213 conserve une intention bloquée, sans exécuter ses
            # anciens moyens. Une ronde retenue en attente n'est pas un départ.
            from donjon.agendas import contrat_intention
            self.assertEqual(intention["plan"], [])
            contrat = contrat_intention(m, "ilse")
            self.assertIsNotNone(contrat)
            self.assertEqual(contrat["phase"], "attendre")
        # Trempée en arrivant (son départ, puis l'eau de la conduite), elle a séché au poêle du guet,
        # le feu hors de l'eau (branche ``ressources``).
        self.assertEqual(m.objets["ilse"]["corps"]["trempe"], 0)
        from donjon.corps import au_chaud
        self.assertTrue(au_chaud(m, "ilse"))
        # Au refuge, ceux qui ne l'ont pas vue monter assez longtemps y restent.
        self.assertEqual(m.objets["brune"]["lieu"], "antichambre")

    def test_une_alarme_sans_passage_tombe(self):
        from donjon.deliberation import alarme, deliberer
        from donjon.esprits import memoriser
        m, _ = attendre(calme(crue(FIXES), "marchand", "brune", "ilse", "aubin"), 140)
        placer(m, "marchand", "antichambre", (2, 2))
        percevoir(m, "marchand")
        # Placement d'auteur : un appel d'Ilse, sa protégée, venu de la galerie (``ouie``) ; Gorm
        # voudrait accourir, mais il croit la conduite noyée : aucun plan, il ne part pas.
        memoriser(m, "marchand", {"type": "bruit", "salle": "chambre_cloche", "nature": "appel", "niveau": 3,
                                  "qui": "ilse"})
        self.assertEqual(alarme(m, "marchand"), ("chambre_cloche", "devoir"))
        deliberer(m, "marchand", m.data["minutes"])
        self.assertNotEqual((lire(m, "marchand")["intention"] or {}).get("but"),
                            {"type": "voir", "lieu": "chambre_cloche"})


class ReveleParLaCrueTests(unittest.TestCase):
    """Règles communes révélées par le banc de la crue, vraies hors de l'eau."""

    def test_un_pnj_ne_prend_rien_dans_les_mains_d_autrui(self):
        # Au banc, Aubin et Ilse prenaient tour à tour la même clé, l'une dans la main de l'autre.
        from donjon.deplacement_objet import deplacer
        from donjon.pnj import _executer
        m = calme(crue(), "marchand", "brune", "ilse", "aubin")
        placer(m, "ilse", "antichambre", (6, 5))
        placer(m, "aubin", "antichambre", (7, 4))
        deplacer(m, "cle", "aubin")
        etape = {"operation": "prendre", "cible": "cle", "outil": "", "lieu": "", "condition": ""}
        self.assertFalse(_executer(m, "ilse", etape, [], []))
        # Même règle pour les vivres que Gorm tient : Brune ne les mange pas dans sa main.
        placer(m, "marchand", "antichambre", (2, 2))
        placer(m, "brune", "antichambre", (2, 3))
        deplacer(m, "vivres", "marchand")
        etape = {"operation": "manger", "cible": "vivres", "outil": "", "lieu": "", "condition": ""}
        self.assertFalse(_executer(m, "brune", etape, [], []))
        m = recharger(m)
        self.assertEqual((m.objets["cle"]["lieu"], m.objets["vivres"]["lieu"]), ("aubin", "marchand"))
        self.assertEqual(m.objets["vivres"]["portions"], 4)


class AutreLieuTests(unittest.TestCase):
    """Les mêmes règles hors du Relais : une cave et sa cuisine, sans personne."""

    def monde(self):
        salles = {
            "cuisine": {"nom": "Cuisine", "sorties": {"sud": {"vers": "cave", "porte": None, "case": [1, 3]}},
                        "fenetres": 1, "lumiere_naturelle": 2, "altitude_cm": 0,
                        "plan": {"origine": [0, -4], "sol": ["...", "...", "..."], "repere": "K"}},
            "cave": {"nom": "Cave", "sorties": {"nord": {"vers": "cuisine", "porte": None, "case": [1, -1]}},
                     "fenetres": 0, "lumiere_naturelle": 0, "altitude_cm": -100,
                     "plan": {"origine": [0, 0], "sol": ["...", "...", "..."], "repere": "V"}}}
        objets = {"poele": objet("poele", "poêle de la cave", "luminaire", "cave", foyer=True, allume=True,
                                 combustible=300, luminosite=1, position=[2, 2], position_salle="cave")}
        scenario = {"version": 1, "debut": "La pluie ne cesse pas.", "objectif": "Rester au sec.",
                    "liberte_personnage": "Corvus choisit sa voie."}
        m = nouveau_monde_libre(salles, objets, "cuisine", [1, 2], scenario)
        m.data["crue"] = {"depart_cm": -130, "bornes": {"montee_cm_heure": [30, 30], "heure_pic": [8, 8],
                                                         "hauteur_pic_cm": [40, 40]}}
        m = Monde(m.data)
        installer(m)
        m.joueur["orientation"] = "sud"
        return m

    def test_la_cave_se_noie_son_feu_s_eteint_et_on_n_y_descend_plus(self):
        m, _ = attendre(self.monde(), 70)     # 5 cm dans la cave
        texte = Moteur(m).executer(Moteur(m).preparer(proposition("marcher", "sud")))
        self.assertIn("Tu entres dans : Cave.", texte)
        self.assertIn("L'eau t'arrive aux chevilles : te voilà trempé.", texte)
        m.joueur.update(salle="cuisine", position=[1, 2], orientation="sud")
        m, lu = attendre(m, 260)          # niveau -0 : la cave a 100 cm d'eau
        self.assertTrue(eau.noyee(m, "cave"))
        self.assertFalse(m.objets["poele"]["allume"])
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(proposition("marcher", "sud"))
        self.assertIn("sud (Cave, eau trop haute pour passer)", regarder(m))
        m, lu = attendre(m, 270)
        self.assertIn("L'eau gagne le sol où tu te tiens.", lu)
        self.assertEqual(recharger(m).data["crue"]["etats"]["cuisine"], "mouillee")



class AltitudeTests(unittest.TestCase):
    """L'altitude du sol est celle que l'eau atteint ; elle ne fait pas un autre étage."""

    def test_des_salles_basses_du_meme_etage_se_voient_et_s_eclairent(self):
        from donjon.perception import CarteLumiere
        from donjon.spatial import _salles_relies
        m = recharger(crue())
        self.assertNotEqual(eau.altitude(m, "echoppe"), eau.altitude(m, "crypte"))
        self.assertTrue(m.objets["brasero"]["allume"])
        # La lueur du brasero de la conduite basse passe dans la salle des vannes, un peu plus haute,
        # et au refuge ; pas jusqu'à la galerie, à l'étage, au bout d'un escalier.
        self.assertTrue({"antichambre", "crypte", "echoppe"} <= _salles_relies(m, "crypte"))
        lueurs = {c["source"] for c in CarteLumiere(m, "crypte").ambiance("crypte")}
        self.assertIn("brasero", lueurs)
        self.assertNotIn("chambre_cloche", _salles_relies(m, "beffroi"))
        self.assertNotIn("brasero", {c["source"] for c in CarteLumiere(m, "chambre_cloche").ambiance("chambre_cloche")})


if __name__ == "__main__":
    unittest.main()
