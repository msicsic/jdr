"""La délibération suit les événements (``docs/plan-temps.md``, « Délibérer à l'événement ») : un
PNJ choisit de nouveau son but à la fin de son plan, après un geste manqué, et après un événement
qui change sa situation (un bruit qu'il interprète, quelqu'un qui entre dans son regard, une chose
qui change sous ses yeux, une parole), à l'instant, pas à la minute suivante ; la délibération de
chaque minute reste le filet de ce qui monte peu à peu. Chaque cas se vérifie sur l'état du monde
après rechargement ; l'instant où il reconsidère est dans son esprit, et le même laps découpé
autrement donne le même monde."""

from tests.support import lier, relation
import unittest
from unittest.mock import patch

from donjon import deliberation
from donjon.deliberation import CHALEUR_FIN, seuils
from donjon.esprits import croire, esprit, lire, percevoir_tous
from donjon.monde import Monde
from donjon.temps import MINUTE, instant
from tests.support import calme, refusee, regarder
from tests.test_temps_etat import decouper, etat_pnj, faire, intention, plan
from tests.test_tensions import placer, recharger, relais, vivre


def jusqu_a(m, t, recharger_tous=5):
    """Le joueur, loin, se tourne sur place (2 s par rotation) jusqu'à l'instant ``t`` ; le monde
    est rechargé en route."""
    n = 0
    while instant(m) < t:
        faire(m, "tourner sud" if n % 2 == 0 else "tourner nord")
        n += 1
        if n % recharger_tous == 0:
            m = recharger(m)
    return recharger(m)


class Choix:
    """Les instants où un PNJ choisit son but, et ce qu'il choisit."""

    def __init__(self, *ids):
        self.ids, self.choix = ids, []

    def __enter__(self):
        original = deliberation.choisir

        def espion(monde, id, minute):
            resultat = original(monde, id, minute)
            if id in self.ids:
                i = lire(monde, id)["intention"]
                self.choix.append((instant(monde), id, i["but"] if i else None))
            return resultat
        self._patch = patch.object(deliberation, "choisir", espion)
        self._patch.start()
        return self

    def __exit__(self, *exc):
        self._patch.stop()

    def instants(self, id, but=None):
        return [t for t, x, b in self.choix if x == id and (but is None or b and b.get("type") == but)]


def scene():
    m = relais()
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    m.joueur.update(salle="chambre_cloche", position=[3, 7], orientation="nord")
    return m


def pret(m):
    """La scène posée, chacun voit ce qu'il voit (sa première perception, qui ne fait que l'établir) ;
    puis la partie est rechargée."""
    percevoir_tous(m)
    return recharger(m)


def loin(m, *ids):
    """Placement d'auteur : ces PNJ sont montés à la galerie, hors de la scène."""
    for n, id in enumerate(ids):
        placer(m, id, "chambre_cloche", (1 + n, 1))


def a_soi(m, *ids):
    """Placement d'auteur : leurs crochets et leurs outils sont hors d'atteinte."""
    for k in ("crochets", "pied_de_biche", "marteau", "couteau"):
        m.objets[k].update(lieu="chambre_cloche", position=[5, 1], position_salle="chambre_cloche")


class FinDePlanTests(unittest.TestCase):
    def test_un_plan_fini_a_mi_minute_fait_choisir_aussitot(self):
        # Gorm prend la clé à une demi-seconde ; sa ronde de la salle des vannes est due. Avant,
        # il restait planté jusqu'à la minute suivante.
        m = scene()
        loin(m, "brune", "ilse", "aubin")
        placer(m, "marchand", "antichambre", (6, 5))
        regarder(m, "marchand", "cle")
        lire(m, "marchand")["visites"]["crypte"] = -500
        intention(m, "marchand", plan("prendre", "cle"), but="prendre", motif="devoir")
        esprit(m, "marchand")["libre"] = 5
        m = pret(m)
        with Choix("marchand") as choix:
            m = jusqu_a(m, 200)
        self.assertEqual(m.objets["cle"]["lieu"], "marchand")
        self.assertEqual(choix.instants("marchand", "pulsion")[0], 25)  # La clé prise (2 s), il repart.
        self.assertEqual(lire(m, "marchand")["intention"]["but"], {"type": "pulsion", "lieu": "crypte", "periode": 90})
        self.assertNotEqual(m.objets["marchand"]["position"], [6, 5])
        self.assertEqual(m.data["minutes"], 0)

    def test_un_objet_pose_a_mi_minute_fait_choisir_aussitot(self):
        # Autre cas de même nature : Aubin pose ses planches, puis part à sa ronde de la salle des vannes.
        m = scene()
        loin(m, "brune", "ilse", "marchand")
        placer(m, "aubin", "antichambre", (2, 4))
        m.objets["planches"].update(lieu="aubin")
        m.objets["planches"].pop("position", None)
        lire(m, "aubin")["visites"]["crypte"] = -500
        intention(m, "aubin", plan("poser", "planches", lieu="antichambre"), but="poser", motif="securite")
        esprit(m, "aubin")["libre"] = 5
        m = pret(m)
        with Choix("aubin") as choix:
            m = jusqu_a(m, 200)
        self.assertEqual(m.objets["planches"]["lieu"], "antichambre")
        self.assertEqual(choix.instants("aubin", "pulsion")[0], 25)
        self.assertNotEqual(m.objets["aubin"]["position"], [2, 4])
        self.assertEqual(m.data["minutes"], 0)


class GesteManqueTests(unittest.TestCase):
    def test_un_objet_absent_fait_choisir_aussitot(self):
        # Gorm tend la main vers son marteau, qu'on a emporté ; il l'apprend et part à sa ronde
        # du refuge sans attendre la minute.
        m = scene()
        loin(m, "brune", "ilse", "aubin")
        placer(m, "marchand", "echoppe", (7, 4))
        regarder(m, "marchand", "marteau")
        m.objets["marteau"].update(lieu="crypte", position=[1, 1], position_salle="crypte")
        lire(m, "marchand")["visites"]["antichambre"] = -500
        intention(m, "marchand", plan("prendre", "marteau"), but="prendre", motif="devoir")
        esprit(m, "marchand")["libre"] = 5
        m = pret(m)
        with Choix("marchand") as choix:
            m = jusqu_a(m, 200)
        self.assertIsNone(lire(m, "marchand")["croyances"]["marteau"]["lieu"]["valeur"])
        self.assertEqual(choix.instants("marchand")[0], 5)
        self.assertEqual(lire(m, "marchand")["intention"]["but"]["lieu"], "antichambre")
        self.assertEqual(m.objets["marchand"]["lieu"], "antichambre")
        self.assertEqual(m.data["minutes"], 0)

    def test_une_porte_verrouillee_fait_choisir_aussitot(self):
        # Autre cas de même nature : Aubin croit la porte étanche ouverte ; elle est verrouillée.
        m = scene()
        loin(m, "brune", "ilse", "marchand")
        placer(m, "aubin", "crypte", (7, 3))
        regarder(m, "aubin", [8, 3])
        lire(m, "aubin")["croyances"].setdefault("porte", {}).pop("verrouillee", None)
        lire(m, "aubin")["visites"]["antichambre"] = -500
        intention(m, "aubin", plan("ouvrir", "porte"), but="ouvrir", motif="securite")
        esprit(m, "aubin")["libre"] = 5
        m = pret(m)
        with Choix("aubin") as choix:
            m = jusqu_a(m, 200)
        self.assertTrue(lire(m, "aubin")["croyances"]["porte"]["verrouillee"]["valeur"])
        self.assertEqual(choix.instants("aubin")[0], 5)
        self.assertEqual(lire(m, "aubin")["intention"]["but"]["lieu"], "antichambre")
        self.assertNotEqual(m.objets["aubin"]["position"], [7, 3])

    def test_le_meme_geste_manque_ne_se_retente_qu_a_la_minute(self):
        # Brune manque son crochetage : le même geste ne se retente pas aussitôt, mais à la minute.
        m = scene()
        loin(m, "ilse", "aubin")
        placer(m, "marchand", "crypte", (1, 1))
        placer(m, "brune", "antichambre", (7, 3))
        regarder(m, "brune", "reserve")
        m.objets["crochets"]["lieu"] = "brune"
        intention(m, "brune", plan("crocheter", "reserve", "crochets"), but="crocheter", motif="faim")
        esprit(m, "brune")["libre"] = 5
        m = pret(m)
        with patch.object(Monde, "d20", return_value=1):
            m = jusqu_a(m, MINUTE - 20)
        essais = [c for c in m.data["chronique"] if "s'acharne" in c["texte"]]
        self.assertEqual(len(essais), 1)
        self.assertTrue(m.objets["reserve"]["verrouillee"])


class EvenementTests(unittest.TestCase):
    def test_un_voleur_qui_entre_dans_son_regard_le_fait_choisir_aussitot(self):
        # Brune, les vivres de Gorm en main, entre dans la conduite où il attend, tourné vers elle :
        # il voit son bien aux mains d'une autre et va le reprendre sans attendre la minute.
        m = scene()
        loin(m, "ilse", "aubin")
        placer(m, "marchand", "echoppe", (4, 2))
        m.objets["marchand"]["orientation"] = "sud"
        placer(m, "brune", "crypte", (4, 1))
        m.objets["vivres"].update(lieu="brune")
        m.objets["vivres"].pop("position", None)
        intention(m, "brune", plan("aller", lieu="antichambre"), but="rejoindre", motif="securite")
        esprit(m, "brune")["libre"] = 5
        m = pret(m)
        with Choix("marchand") as choix:
            m = jusqu_a(m, 300)
        vu = [s for s in lire(m, "marchand")["memoire"] if s["type"] == "vu_porter"]
        self.assertEqual([(s["auteur"], s["objet"]) for s in vu], [("brune", "vivres")])
        premier = choix.instants("marchand")[0]
        self.assertLess(premier, MINUTE)
        self.assertEqual(choix.choix[0][2], {"type": "pulsion", "objet": "vivres", "lieu": "antichambre"})
        self.assertNotEqual(m.objets["marchand"]["position"], [4, 2])
        self.assertEqual(m.data["minutes"], 0)

    def test_un_geste_illicite_sous_ses_yeux_le_fait_choisir_aussitot(self):
        # Autre cas de même nature : Gorm attend au refuge, tourné vers la réserve ; Brune s'y met à
        # crocheter. Témoin, il choisit aussitôt, sur ce qu'il vient de voir.
        m = scene()
        loin(m, "ilse", "aubin")
        placer(m, "marchand", "antichambre", (5, 3))
        regarder(m, "marchand", "reserve")
        placer(m, "brune", "antichambre", (7, 3))
        regarder(m, "brune", "reserve")
        m.objets["crochets"]["lieu"] = "brune"
        intention(m, "brune", plan("crocheter", "reserve", "crochets"), but="crocheter", motif="faim")
        esprit(m, "brune")["libre"] = 205
        m = pret(m)
        with Choix("marchand") as choix:
            m = jusqu_a(m, 300)
        self.assertIn("vu_agir", [s["type"] for s in lire(m, "marchand")["memoire"]])
        self.assertEqual(choix.instants("marchand")[0], 205)
        self.assertFalse(relation(m, "marchand", "brune")["valeur"])

    def test_un_bruit_a_voir_le_fait_partir_aussitot(self):
        # Gorm attend dans la conduite ; Brune force la porte étanche, dans la salle des vannes qu'il
        # garde. Il va voir au bruit, pas à la minute suivante.
        m = scene()
        loin(m, "ilse", "aubin")
        placer(m, "marchand", "echoppe", (4, 1))
        m.objets["marchand"]["orientation"] = "nord"
        placer(m, "brune", "crypte", (7, 3))
        regarder(m, "brune", [8, 3])
        m.objets["crochets"]["lieu"] = "brune"
        intention(m, "brune", plan("crocheter", "porte", "crochets"), but="crocheter", motif="faim")
        esprit(m, "brune")["libre"] = 205
        m = pret(m)
        with Choix("marchand") as choix:
            m = jusqu_a(m, 500)
        self.assertEqual(choix.instants("marchand", "voir")[0], 205)
        self.assertEqual(m.objets["marchand"]["lieu"], "crypte")
        self.assertEqual(m.data["minutes"], 0)

    def test_un_appel_le_fait_partir_aussitot(self):
        # Autre cas de même nature : le joueur crie à l'aide dans la salle des vannes, au milieu d'une
        # minute ; Gorm, qui la garde, y va aussitôt.
        m = scene()
        loin(m, "brune", "ilse", "aubin")
        placer(m, "marchand", "echoppe", (4, 1))
        m.objets["marchand"]["orientation"] = "nord"
        m.joueur.update(salle="crypte", position=[2, 5], orientation="nord")
        m = jusqu_a(pret(m), 200)
        with Choix("marchand") as choix:
            faire(m, "crier à l'aide")
        self.assertEqual(choix.instants("marchand", "voir")[0], 201)  # Le cri commence l'action : il y réagit aussitôt après.
        m = jusqu_a(recharger(m), MINUTE - 20)
        self.assertEqual(m.objets["marchand"]["lieu"], "crypte")

    def test_une_reserve_ouverte_sous_ses_yeux_la_fait_choisir_aussitot(self):
        # Brune, affamée, n'avait aucun moyen d'atteindre les vivres ; Gorm ouvre la réserve sous ses
        # yeux : elle choisit aussitôt d'en manger.
        m = scene()
        loin(m, "ilse", "aubin")
        a_soi(m)
        refusee(m)
        lire(m, "brune")["besoins"]["faim"] = 88.0
        placer(m, "brune", "antichambre", (5, 2))
        regarder(m, "brune", "reserve")
        placer(m, "marchand", "antichambre", (7, 3))
        regarder(m, "marchand", "reserve")
        intention(m, "marchand", plan("deverrouiller", "reserve", "cle_reserve"), plan("ouvrir", "reserve"),
                  but="ouvrir", motif="devoir")
        esprit(m, "marchand")["libre"] = 205
        m = pret(m)
        with Choix("brune") as choix:
            m = jusqu_a(m, 300)
        # Déverrouillée à 20,5 s (5 s), ouverte à 25,5 s : elle choisit à cet instant. (Gorm, qui l'a
        # ouverte sans raison de la laisser ouverte, la referme ensuite : c'est sa charge.)
        self.assertEqual(choix.instants("brune")[0], 255)
        self.assertEqual(choix.choix[0][2], {"type": "manger", "objet": "vivres"})

    def test_un_feu_eteint_sous_ses_yeux_le_fait_rallumer_aussitot(self):
        # Autre cas de même nature : Brune éteint le brasero sous les yeux de Gorm, qui l'entretient ;
        # sa charge rompue, il va le rallumer sans attendre la minute.
        m = scene()
        loin(m, "ilse", "aubin")
        placer(m, "marchand", "echoppe", (5, 4))
        regarder(m, "marchand", "brasero")
        placer(m, "brune", "echoppe", (3, 3))
        regarder(m, "brune", "brasero")
        intention(m, "brune", plan("eteindre", "brasero"), but="eteindre", motif="securite")
        esprit(m, "brune")["libre"] = 205
        m = pret(m)
        with Choix("marchand") as choix:
            m = jusqu_a(m, MINUTE + 200)
        self.assertEqual(choix.choix[0][0], 205)  # Éteint d'un geste, à 20,5 s.
        self.assertEqual(choix.choix[0][2], {"type": "pulsion", "objet": "brasero", "allume": True})
        self.assertTrue(m.objets["brasero"]["allume"])  # Rallumé à la torche du refuge.

    def test_la_reaction_ne_depend_pas_du_decoupage(self):
        # Le même laps, d'un bloc ou découpé en rotations rechargées en route, donne le même monde :
        # l'instant où chacun doit reconsidérer est dans son esprit.
        def voleur():
            m = scene()
            loin(m, "ilse", "aubin")
            placer(m, "marchand", "echoppe", (4, 2))
            m.objets["marchand"]["orientation"] = "sud"
            placer(m, "brune", "crypte", (4, 1))
            m.objets["vivres"].update(lieu="brune")
            m.objets["vivres"].pop("position", None)
            intention(m, "brune", plan("aller", lieu="antichambre"), but="rejoindre", motif="securite")
            esprit(m, "brune")["libre"] = 5
            percevoir_tous(m)
            return m
        d_un_bloc, morcele = decouper(voleur, 2, recharger_tous=7)
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))


class GesteQuiDureTests(unittest.TestCase):
    def test_un_abri_devenu_noir_se_quitte_aussitot(self):
        # Ilse s'abrite au refuge, à la lumière du fanal ; Brune, dont elle se méfie, l'éteint. Ce
        # n'est plus un abri : elle va à la conduite éclairée sans attendre la minute (avant, son
        # attente allait jusqu'à la minute).
        m = scene()
        # Le fanal doit être l'unique lumière de cette scène : la lueur
        # des autres sources rendrait encore l'abri valide après son extinction.
        for k, o in m.objets.items():
            if 'allume' in o and k != 'fanal':
                o['allume'] = False
        m.data['salles']['antichambre']['lumiere_naturelle'] = 0
        loin(m, "aubin", "marchand")
        placer(m, "ilse", "antichambre", (5, 2))
        regarder(m, "ilse", "fanal")
        lire(m, "ilse")["besoins"]["securite"] = 70.0
        lier(m, "ilse", "brune", False, "vu")
        intention(m, "ilse", plan("abriter", lieu="antichambre"), but="abri", motif="securite")
        lire(m, "ilse")["intention"]["but"]["lieu"] = "antichambre"
        placer(m, "brune", "antichambre", (4, 1))
        regarder(m, "brune", "fanal")
        intention(m, "brune", plan("eteindre", "fanal"), but="eteindre", motif="securite")
        esprit(m, "brune")["libre"] = 205
        m = pret(m)
        with Choix("ilse") as choix:
            m = jusqu_a(m, MINUTE - 20)
        self.assertFalse(m.objets["fanal"]["allume"])
        # La destination dépend des liens ; l'événement doit interrompre cet abri sombre
        # au même instant, sans attendre la prochaine minute.
        t, id, but = choix.choix[0]
        self.assertEqual((t, id), (205, "ilse"))
        self.assertNotEqual(but, {"type": "abri", "lieu": "antichambre"})
        self.assertNotEqual(m.objets["ilse"]["lieu"], "antichambre")


class BouclesTests(unittest.TestCase):
    """Deux boucles de l'audit des nuits (``docs/audit-nuits.md``, B1 et B3), dans la délibération :
    un appel à l'aide ne se répète pas tant que dure le même désarroi ; on ne prévient une victime
    que de ce qu'elle ignore encore."""

    def test_un_appel_a_l_aide_sans_reponse_ne_se_repete_pas(self):
        # Cas réel (mine 7) : Lucien, à bout dans le noir, appelait toutes les 10 minutes jusqu'au
        # matin. Ici Ilse, seule et à bout, sans personne qui accoure : un seul appel en 40 minutes.
        from tests.test_protection import seule_et_a_bout
        m = seule_et_a_bout(relais())
        m.objets["marchand"]["profil"]["protege"] = []
        m = recharger(m)
        for _ in range(8):
            m, _ = vivre(m, 5)
            lire(m, "ilse")["besoins"]["securite"] = 99.0   # Rien ne la rassure.
        textes = [c["texte"] for c in m.data["chronique"]]
        self.assertEqual(textes.count("Ilse appelle à l'aide."), 1)

    def test_rassuree_puis_de_nouveau_a_bout_elle_rappelle(self):
        # Même nature : un nouveau désarroi, après avoir été rassurée, appelle de nouveau.
        from tests.test_protection import seule_et_a_bout
        m = seule_et_a_bout(relais())
        m.objets["marchand"]["profil"]["protege"] = []
        m, _ = vivre(recharger(m), 2)
        lire(m, "ilse")["besoins"]["securite"] = 40.0
        m, _ = vivre(recharger(m), 1)
        lire(m, "ilse")["besoins"]["securite"] = 99.0
        m, _ = vivre(recharger(m), 15)
        textes = [c["texte"] for c in m.data["chronique"]]
        self.assertEqual(textes.count("Ilse appelle à l'aide."), 2)

    def test_on_ne_previent_pas_deux_fois_du_meme_fait(self):
        # Cas réel (auberge 5) : Hugues disait à Anselme « Lucien est peu fiable » à chaque minute d'un
        # crochetage vu. Un fait dit ne se redit pas ; le lieu d'un bien, s'il le croit ailleurs depuis.
        from donjon.deliberation import _plan_prevenir
        from donjon.esprits import memoriser
        from donjon.banc_pnj import creer
        m = creer("auberge", 1985, "fixe")
        calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
        memoriser(m, "hugues", {"type": "a_prevenir", "victime": "anselme", "auteur": "lucien"})
        self.assertEqual(_plan_prevenir(m, "hugues")[1][-1]["contenu"],
                         {"sujet": "lucien", "attribut": "fiable", "valeur": False})
        memoriser(m, "hugues", {"type": "dit", "a": "anselme", "sujet": "lucien", "attribut": "fiable", "valeur": False})
        m.data["minutes"] += 3
        memoriser(m, "hugues", {"type": "a_prevenir", "victime": "anselme", "auteur": "lucien"})
        m = recharger(m)
        self.assertIsNone(_plan_prevenir(m, "hugues"))
        # Autre cas de même nature : il voit ensuite Lucien poser le ballot à l'étable ; il a à lui dire
        # où il est, et seulement cela.
        croire(m, "hugues", "ballot", "lieu", "etable", "vu", salle="etable", case=[3, 2])
        memoriser(m, "hugues", {"type": "vu_agir", "auteur": "lucien", "operation": "poser", "objet": "ballot",
                                "lieu": {"valeur": "etable", "salle": "etable", "case": [3, 2],
                                         "minute": m.data["minutes"]}})
        memoriser(m, "hugues", {"type": "a_prevenir", "victime": "anselme", "auteur": "lucien"})
        etapes = _plan_prevenir(recharger(m), "hugues")[1]
        self.assertEqual([x["contenu"] for x in etapes if x["operation"] == "dire"],
                         [{"sujet": "ballot", "attribut": "lieu", "valeur": "etable"}])


class FiletTests(unittest.TestCase):
    def test_un_besoin_qui_franchit_son_seuil_en_marchant_se_pese_a_la_minute(self):
        # Ilse fait sa ronde ; sa faim franchit son seuil à la minute : c'est le filet de la minute
        # qui le pèse, pendant qu'elle marche, sans événement.
        m = scene()
        loin(m, "brune", "aubin")
        placer(m, "marchand", "crypte", (1, 1))
        placer(m, "ilse", "antichambre", (6, 5))
        lire(m, "ilse")["visites"]["echoppe"] = -500
        faim = seuils(m, "ilse")["faim"]
        lire(m, "ilse")["besoins"]["faim"] = faim - 0.001
        m = pret(m)
        with Choix("ilse") as choix:
            m = jusqu_a(m, MINUTE + 100)
        faims = [t for t, _, b in choix.choix if b and b.get("type") != "pulsion"]
        self.assertTrue(faims)
        self.assertEqual(faims[0], MINUTE)

    def test_se_chauffer_cesse_a_son_seuil_et_la_suite_commence(self):
        # Ilse se chauffe au brasero ; réchauffée à la minute, elle part aussitôt à sa ronde, sans
        # une minute de plus près du feu.
        m = scene()
        loin(m, "brune", "aubin")
        placer(m, "marchand", "crypte", (1, 1))
        placer(m, "ilse", "echoppe", (3, 3))
        regarder(m, "ilse", "brasero")
        lire(m, "ilse")["besoins"]["chaleur"] = CHALEUR_FIN + 0.5
        lire(m, "ilse")["visites"]["antichambre"] = -500
        intention(m, "ilse", plan("chauffer", "brasero"), but="chaleur", motif="chaleur")
        m = pret(m)
        m = jusqu_a(m, MINUTE + 200)
        self.assertLessEqual(lire(m, "ilse")["besoins"]["chaleur"], CHALEUR_FIN)
        self.assertEqual(lire(m, "ilse")["intention"]["but"], {"type": "pulsion", "lieu": "antichambre", "periode": 40})
        self.assertNotEqual(m.objets["ilse"]["position"], [3, 3])


if __name__ == "__main__":
    unittest.main()
