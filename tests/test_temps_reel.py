"""Ce qui restait à la minute vit au temps réel (``docs/plan-temps.md``, « Correctif : le temps réel ») :
les horloges du scénario se déclenchent à leur minute pendant la vie des PNJ, même au milieu d'un
long geste du joueur ; le corps, la dérive des besoins et la sécurité ressentie évoluent selon le
temps passé dans chaque état (``vecu``), pour les PNJ comme pour le joueur ; le froid sec monte de 4
par heure ; la patience et le répit se comptent en temps. Chaque cas se vérifie sur l'état du monde
après rechargement, et le même laps découpé autrement donne le même monde."""
import unittest

from donjon import vecu
from donjon.banc_pnj import creer
from donjon.corps import CORPS, EFFORT
from donjon.deliberation import PATIENCE, REPIT, choisir
from donjon.esprits import esprit, lire
from donjon.geometrie import position_entree
from donjon.temps import MINUTE, instant
from tests.support import calme, regarder
from tests.test_deliberation_evenements import Choix, loin, pret, scene
from tests.test_temps_etat import decouper, etat_pnj, faire
from tests.test_tensions import placer, recharger, relais, vivre


def rafale(minute):
    return {"id": "rafale_test", "minute": minute, "annonce": "Un courant d'air rabat les flammes de la conduite.",
            "lieux": ["echoppe"], "effets": [{"operation": "eteindre", "salles": ["echoppe"]}]}


def gorm_au_brasero():
    """Gorm entretient le brasero de la conduite et le regarde ; une rafale l'éteindra à la minute 2."""
    m = scene()
    loin(m, "ilse", "aubin", "brune")
    placer(m, "marchand", "echoppe", (5, 4))
    regarder(m, "marchand", "brasero")
    m.data["horloges"] = [rafale(2)]
    return pret(m)


class HorlogesTests(unittest.TestCase):
    def test_cas_reel_la_rafale_de_l_auberge_eteint_l_atre_a_sa_minute(self):
        # Cas réel : l'horloge ne se déclenchait qu'à la fin d'une action du joueur ; une attente de
        # 5 minutes retardait la rafale, et Hugues, dans la salle commune, ne voyait l'âtre éteint qu'à
        # la minute 5. Placement d'auteur : la rafale avancée à la minute 2.
        m = creer("auberge", 1985, "fixe")
        m.joueur.update(salle="dortoir", position=list(position_entree(m, "dortoir")))
        m.data["horloges"][0]["minute"] = 2
        texte = faire(m, "attendre")
        m = recharger(m)
        self.assertEqual(m.data["horloges_declenchees"], ["rafale"])
        self.assertFalse(m.objets["atre"]["allume"])
        vu = lire(m, "hugues")["croyances"]["atre"]["etat"]
        self.assertEqual((vu["valeur"]["allume"], vu["minute"]), (False, 2))
        self.assertNotIn("rafale", texte)  # Le joueur, au dortoir, n'est pas dans les lieux de l'annonce.

    def test_gorm_rallume_le_brasero_pendant_l_attente_du_joueur(self):
        # Autre cas de même nature : une horloge éteint le brasero à la minute 2 pendant une attente
        # de 5 minutes ; Gorm, qui le regarde, choisit de le rallumer à cet instant et le rallume
        # avant la fin de l'action.
        m = gorm_au_brasero()
        with Choix("marchand") as choix:
            faire(m, "attendre")
        m = recharger(m)
        self.assertEqual(m.data["horloges_declenchees"], ["rafale_test"])
        self.assertIn((2 * MINUTE, "marchand", {"type": "pulsion", "objet": "brasero", "allume": True}),
                      choix.choix)
        self.assertTrue(m.objets["brasero"]["allume"])
        rallume = [c for c in m.data["chronique"] if "allume le brasero" in c["texte"]]
        self.assertTrue(rallume and 2 * MINUTE < rallume[0]["instant"] < 5 * MINUTE, rallume)

    def test_l_horloge_ne_depend_pas_du_decoupage(self):
        d_un_bloc, morcele = decouper(gorm_au_brasero, 5)
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))
        self.assertEqual(d_un_bloc.data["horloges_declenchees"], morcele.data["horloges_declenchees"])


def en_phase(decalage, qui, salle, case, avant):
    """La même scène, commencée ``decalage`` dixièmes après la frontière de minute : ``qui`` choisit
    son but dès le départ ; les autres sont calmes, le joueur au refuge."""
    m = relais()
    calme(m, "marchand", "brune", "ilse", "aubin")
    m.objets["porte"].update(ouverte=True, verrouillee=False)
    m.joueur.update(salle="antichambre", position=[6, 5])
    placer(m, qui, salle, case)
    avant(m)
    m.data["dixiemes"] = decalage
    esprit(m, qui)["libre"] = decalage
    choisir(m, qui, 0)
    return m


def vecu_en_trois_minutes(qui, salle, case, avant):
    """Ce que ``qui`` vit pendant trois minutes, à quatre phases de la minute : le changement de ses
    besoins, soldé au même instant relatif, après rechargement."""
    resultats = []
    for decalage in (0, 150, 300, 450):
        m = en_phase(decalage, qui, salle, case, avant)
        debut = dict(lire(m, qui)["besoins"])
        for _ in range(3):
            m, _ = vivre(m, 1)
        m = recharger(m)
        vecu.solder(m, qui, instant(m))  # La mesure : le temps vécu jusqu'à cet instant.
        fin = lire(m, qui)["besoins"]
        trajet = [c["instant"] - decalage for c in m.data["chronique"] if c["texte"].startswith(
            m.objets[qui]["nom"].split(",")[0]) and " passe dans : " in c["texte"]]
        resultats.append(({k: fin[k] - debut[k] for k in fin}, trajet, m.objets[qui]["lieu"]))
    return resultats


class CorpsVecuTests(unittest.TestCase):
    """Le corps et les besoins vivent le temps passé dans chaque état : la phase de la minute où l'on
    traverse un lieu ne change rien à ce qu'on y vit (avant, tout se lisait à l'instant pile de la
    minute : selon la phase, une traversée du noir comptait pour rien ou pour une minute entière)."""

    def comparer(self, resultats):
        reference, trajet, lieu = resultats[0]
        self.assertTrue(trajet, "Il devait traverser des salles")
        for ecarts, autre, ou in resultats[1:]:
            self.assertEqual((autre, ou), (trajet, lieu))  # Le même chemin, aux mêmes instants relatifs.
            for k, v in reference.items():
                self.assertAlmostEqual(ecarts[k], v, delta=0.005, msg=k)

    def test_cas_reel_ilse_traverse_le_noir_quelle_que_soit_la_minute(self):
        # Cas réel : le brasero éteint, la salle des vannes et la conduite sont noires ; Ilse, qui craint
        # le noir et dont la sécurité presse, gagne la lumière du refuge en traversant la conduite.
        def avant(m):
            m.objets["brasero"]["allume"] = False
            lire(m, "ilse")["besoins"]["securite"] = 70.0
        resultats = vecu_en_trois_minutes("ilse", "crypte", (2, 2), avant)
        self.comparer(resultats)
        # Le noir où elle s'est tenue l'a inquiétée : sans lui, la seule lumière l'aurait rassurée de
        # 0,2 par minute au plus.
        self.assertGreater(resultats[0][0]["securite"], -0.2 * 3 - 2)

    def test_gorm_passe_au_chaud_quelle_que_soit_la_minute(self):
        # Autre cas de même nature : la ronde de Gorm le fait passer par la conduite chauffée par le
        # brasero ; l'effort de la marche et la chaleur du feu comptent le temps passé.
        def avant(m):
            lire(m, "marchand")["besoins"].update(devoir=75.0, securite=30.0)
            lire(m, "marchand")["visites"]["antichambre"] = -1000   # sa ronde au refuge est échue
        resultats = vecu_en_trois_minutes("marchand", "crypte", (2, 2), avant)
        self.comparer(resultats)
        ecarts = resultats[0][0]
        # Trois minutes, dont la marche à l'effort (faim au moins 3 minutes au repos, au plus à l'effort).
        self.assertGreater(ecarts["faim"], 3 * CORPS["faim"]["heure"] / 60)
        self.assertLess(ecarts["faim"], 3 * CORPS["faim"]["heure"] / 60 * EFFORT)

    def corps_du_joueur(self, gestes):
        """Le joueur fait ``gestes`` (une suite de commandes), rechargé en route ; renvoie le monde, où
        ce qu'il a vécu est soldé jusqu'à l'instant, et les dixièmes passés à l'effort et au calme."""
        m = relais()
        calme(m, "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[6, 3], orientation="est")
        depart = dict(m.joueur["besoins"])
        effort = calme_ = 0
        for n, geste in enumerate(gestes):
            t = instant(m)
            faire(m, geste)
            if geste.startswith("pas "):
                effort += instant(m) - t
            else:
                calme_ += instant(m) - t
            if n % 7 == 6:
                m = recharger(m)
        m = recharger(m)
        vecu.solder(m, "joueur", instant(m))  # La mesure : le temps vécu jusqu'à cet instant.
        return m, depart, effort, calme_

    def test_le_corps_du_joueur_vit_chaque_geste_dans_l_ordre_qu_on_veut(self):
        # Cas réel : le corps du joueur ne changeait qu'au franchissement d'une minute, selon l'action
        # qui la franchissait. Marcher puis se tourner, ou se tourner puis marcher, dans la même minute,
        # c'est le même temps d'effort et de calme ; se tourner sur place ne creuse pas.
        marcher = ["pas ouest", "pas est"] * 6
        tourner = ["tourner ouest", "tourner est"] * 9
        a, depart, effort, calme_ = self.corps_du_joueur(marcher + tourner)
        b, _, effort_b, calme_b = self.corps_du_joueur(tourner + marcher)
        self.assertEqual((instant(a), effort, calme_), (instant(b), effort_b, calme_b))
        self.assertLess(instant(a) // MINUTE, 2)  # Moins de deux minutes : au plus une frontière franchie.
        for k in CORPS:
            self.assertAlmostEqual(a.joueur["besoins"][k], b.joueur["besoins"][k], delta=0.002, msg=k)
        # La faim compte la marche à l'effort et les rotations au calme, au temps près.
        heure = CORPS["faim"]["heure"] / 60 / MINUTE
        self.assertAlmostEqual(a.joueur["besoins"]["faim"] - depart["faim"],
                               heure * (effort * EFFORT + calme_), delta=0.002)

    def test_le_froid_sec_monte_de_4_par_heure(self):
        # Décision du 2026-10-22 : loin d'un feu et au sec, le froid monte de 4 par heure (2 avant), pour
        # le joueur comme pour un PNJ.
        m = relais()
        calme(m, "marchand", "brune", "ilse", "aubin")
        placer(m, "marchand", "chambre_cloche", (1, 1))   # loin de tout feu, au sec (Gorm n'est pas trempé)
        m.joueur.update(salle="chambre_cloche", position=[3, 7])
        m = recharger(m)
        joueur, gorm = m.joueur["besoins"]["chaleur"], lire(m, "marchand")["besoins"]["chaleur"]
        for _ in range(3):
            faire(m, "attendre")
        m = recharger(m)
        self.assertEqual(CORPS["chaleur"]["heure"], 4)
        # Le joueur : 15 minutes ; la première note de son corps est à sa première action.
        self.assertAlmostEqual(m.joueur["besoins"]["chaleur"] - joueur, 4 * 15 / 60, places=2)
        self.assertEqual(m.objets["marchand"]["lieu"], "chambre_cloche")
        self.assertFalse(m.objets["marchand"]["corps"]["trempe"])
        # Gorm : les 15 minutes, soldées à la dernière frontière (la 15e).
        self.assertAlmostEqual(lire(m, "marchand")["besoins"]["chaleur"] - gorm, 4 * 15 / 60, places=2)


def brune_guette():
    """Brune veut crocheter la réserve sans témoin ; le joueur, près d'elle, la regarde : elle guette
    (``test_besoins``, « sous les yeux du joueur »)."""
    from tests.test_besoins import relais as relais_sans_evacues
    m = relais_sans_evacues()
    # Ce guet n'est pas résolu par la vente des crochets au gardien.
    from donjon import relations
    lire(m, "marchand")["relations"]["brune"] = relations._nouvelle({"confiance": 10})
    m.joueur["position"] = [6, 4]
    regarder(m, "joueur", "reserve")
    return m


class PatienceTests(unittest.TestCase):
    """La patience se compte au temps passé à attendre, pas au nombre de fois qu'on y repense ; le
    répit après un renoncement se compte de son instant."""

    def renoncement(self, m, id, pas=1):
        """Le joueur attend jusqu'au renoncement de ``id`` ; renvoie le monde rechargé, l'instant où
        l'attente a commencé et celui du renoncement."""
        debut = None
        for _ in range(60):
            m, _ = vivre(m, pas)
            e = lire(m, id)
            if debut is None and e["patience"] is not None:
                debut = e["patience"]
            if e["renoncements"]:
                return m, debut, min(e["renoncements"].values())
        self.fail("Pas de renoncement")

    def test_cas_reel_brune_renonce_apres_trente_minutes_de_guet(self):
        m, debut, fin = self.renoncement(brune_guette(), "brune")
        self.assertIsNotNone(debut)
        # Trente minutes de guet, comptées au temps (au plus une minute de plus : on y repense au plus
        # tard à la minute suivante).
        self.assertGreaterEqual(fin - debut, PATIENCE * MINUTE)
        self.assertLessEqual(fin - debut, (PATIENCE + 1) * MINUTE)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        # Le répit court de cet instant : pas de nouveau guet avant ``REPIT`` minutes.
        e = lire(m, "brune")
        self.assertNotEqual((e["intention"] or {}).get("motif"), "faim")
        self.assertEqual(type(e["renoncements"]["faim"]), int)
        self.assertGreater(e["renoncements"]["faim"] + REPIT * MINUTE, instant(m))

    def test_gorm_bloque_par_le_joueur_compte_le_temps_qu_il_attend(self):
        # Autre cas de même nature : Gorm doit ouvrir la porte des vannes depuis la case où le joueur se
        # tient ; il le prie de passer, puis patiente. Son attente compte le temps passé (avant : une
        # unité par appel, quel que soit le temps), et au-delà de ``PATIENCE`` minutes il renonce.
        from tests.test_passage import JoueurSurLePassageTests
        m = JoueurSurLePassageTests.palier(None)
        # Sa ronde des vannes est échue : un but ordinaire, que la délibération garde (pas un réflexe).
        lire(m, "marchand")["intention"] = None
        lire(m, "marchand")["besoins"]["devoir"] = 75.0
        lire(m, "marchand")["visites"]["crypte"] = -1000
        choisir(m, "marchand", 0)
        but = lire(m, "marchand")["intention"]["but"]
        for _ in range(10):
            m, _ = vivre(m, 1)
        e = lire(m, "marchand")
        self.assertEqual((e["intention"]["but"], m.objets["marchand"]["lieu"]), (but, "beffroi"))
        # Bloqué depuis son premier pas, son attente est comptée jusqu'à cette minute et continue.
        self.assertEqual(e["patience"], instant(m))
        self.assertGreater(e["intention"]["attente"], 9 * MINUTE)
        self.assertLess(e["intention"]["attente"], 10 * MINUTE)
        # Placement d'auteur : vingt minutes de plus déjà passées à attendre.
        e["intention"]["attente"] += 20 * MINUTE
        m = recharger(m)
        for _ in range(2):
            m, _ = vivre(m, 1)
        e = lire(m, "marchand")
        self.assertIn("devoir", e["renoncements"])
        self.assertNotEqual((e["intention"] or {}).get("but"), but)
        self.assertEqual(m.objets["marchand"]["lieu"], "beffroi")

    def test_la_patience_ne_depend_pas_du_decoupage(self):
        d_un_bloc, morcele = decouper(brune_guette, 10)
        self.assertEqual(d_un_bloc.data["esprits"], morcele.data["esprits"])
        self.assertEqual({id: o.get("position") for id, o in d_un_bloc.objets.items()},
                         {id: o.get("position") for id, o in morcele.objets.items()})
        self.assertGreater(lire(morcele, "brune")["intention"]["attente"], 0)


if __name__ == "__main__":
    unittest.main()
