"""L'ouïe commune au joueur et aux PNJ : tout geste fait un bruit selon sa nature, la distance et
les passages l'atténuent, chacun l'interprète selon ce qu'il croit (connu, inconnu, méfiance).

Chaque cas vérifie l'état du monde après rechargement, et ce que le joueur lit quand il est là."""
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon.commandes import analyser
from donjon.deliberation import bruit_a_voir
from donjon.esprits import croire, esprit, lire
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.ouie import INTENSITES, PORTE, nature, perte, propager, parvenu, retentir
from donjon.spatial import QUART
from donjon.temps import MINUTE, instant
from tests.support import calme, refusee, regarder
from tests.test_tensions import chronique, placer, recharger, relais


def faire(m, commande):
    moteur = Moteur(m)
    return moteur.executer(moteur.preparer(analyser(m, commande)))


def plan(operation, cible="", outil="", lieu="", condition=""):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu, "condition": condition}


def intention(m, id, *etapes, but="manger", motif="faim"):
    lire(m, id)["intention"] = {"but": {"type": but}, "motif": motif, "depuis": 0, "attente": 0,
                                "plan": list(etapes)}


def souvenirs(m, id, sorte):
    return [s for s in lire(m, id)["memoire"] if s["type"] == sorte]


def vu_agir(m, id):
    return [(s["auteur"], s["objet"]) for s in souvenirs(m, id, "vu_agir")]


class EchelleTests(unittest.TestCase):
    def test_une_echelle_declaree_une_fois(self):
        ordre = [nature("faufiler"), nature("aller"), nature("prendre"), nature("dire"), nature("crocheter"),
                 nature("appel")]
        self.assertEqual(ordre, ["feutre", "pas", "geste", "voix", "bruyant", "appel"])
        self.assertEqual([INTENSITES[n] for n in ordre], sorted(INTENSITES[n] for n in ordre))
        self.assertIsNone(nature("attendre"))
        # Fait en douce, un geste ordinaire est feutré ; un geste bruyant le reste.
        self.assertEqual((nature("prendre", discret=True), nature("crocheter", discret=True)), ("feutre", "bruyant"))
        # Un geste du joueur que l'arbitrage dit fracassant est bruyant.
        self.assertEqual(nature("improviser", bruit=3), "bruyant")

    def test_la_distance_et_les_portes_attenuent(self):
        self.assertEqual([perte((0, 0), (d, 0)) for d in (1, 2, 3, 4, 6, 7, 12, 13)], [0, 1, 1, 2, 2, 3, 3, 4])
        m = relais()
        # Au palier, collé à la porte fermée des vannes ; une voix dans la salle des vannes.
        entrees = propager(m, "crypte", (4, 1), INTENSITES["voix"])
        niveau, direction = parvenu(entrees, "beffroi", (0, 3))
        self.assertEqual((niveau, direction), (INTENSITES["voix"] - 2 - PORTE, "ouest"))
        m.objets["porte"]["ouverte"] = True
        self.assertGreater(parvenu(propager(m, "crypte", (4, 1), INTENSITES["voix"]), "beffroi", (0, 3))[0], niveau)


def jusqu_a(m, cible):
    """Le joueur se tourne sur place jusqu'à l'instant ``cible`` (dixièmes de seconde), rechargé
    en route : se tourner ne fait pas de bruit."""
    n = 0
    while instant(m) < cible:
        with patch.object(Monde, "d20", return_value=1):
            faire(m, "tourner sud" if n % 2 == 0 else "tourner nord")
        n += 1
        if n % 10 == 0:
            m = recharger(m)
    return recharger(m)


def brune_crochete_dans_le_dos_de_gorm(gorm_la_sait=True):
    """Cas réel : au refuge, Brune, à bout de faim (Gorm lui a refusé une part), crochète la réserve à
    trois cases dans le dos de Gorm, qui regarde vers l'échoppe ; il la sait là. Le joueur est loin, à
    la galerie."""
    m = refusee(calme(relais(), "marchand", "brune", "ilse", "aubin"))
    for n, id in enumerate(("ilse", "aubin")):
        placer(m, id, "crypte", (2 + n, 3))
    m.objets["crochets"]["lieu"] = "brune"
    placer(m, "brune", "antichambre", (7, 3))
    regarder(m, "brune", "reserve")
    placer(m, "marchand", "antichambre", (4, 1))
    m.objets["marchand"]["orientation"] = "ouest"
    if gorm_la_sait:
        croire(m, "marchand", "brune", "lieu", "antichambre", "vu", salle="antichambre", case=[7, 3])
    lire(m, "brune")["besoins"]["faim"] = 99.0
    intention(m, "brune", plan("crocheter", "reserve", "crochets"))
    esprit(m, "brune")["libre"] = 5
    m.joueur["orientation"] = "nord"
    return recharger(m)


class GesteBruyantTests(unittest.TestCase):
    def test_crocheter_dans_son_dos_le_fait_se_retourner_meme_s_il_la_sait_la(self):
        m = brune_crochete_dans_le_dos_de_gorm()
        self.assertFalse(lire(m, "marchand")["croyances"].get("brune", {}).get("fiable", {}).get("valeur") is False)
        with patch.object(Monde, "d20", return_value=1):
            faire(m, "tourner sud")
        m = recharger(m)
        self.assertIn("Gorm, gardien du relais se retourne au bruit.", chronique(m))
        self.assertIn(m.objets["marchand"]["orientation"], ("est", "sud-est"))
        self.assertIn(("brune", "reserve"), vu_agir(m, "marchand"))
        self.assertFalse(lire(m, "marchand")["croyances"]["brune"]["fiable"]["valeur"])

    def test_entendre_ne_depend_pas_du_decoupage(self):
        # Se retourner au bruit, en être témoin, retenir un bruit : tout est dans ``data``.
        from tests.test_temps_etat import decouper, etat_pnj
        with patch.object(Monde, "d20", return_value=1):
            d_un_bloc, morcele = decouper(brune_crochete_dans_le_dos_de_gorm, 5, recharger_tous=20)
        self.assertIn("Gorm, gardien du relais se retourne au bruit.", chronique(morcele))
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))

    def test_un_fracas_dans_une_autre_salle_gorm_de_garde_va_voir(self):
        # Autre cas : Gorm est à l'échoppe, le refuge (sa garde) est la salle voisine.
        m = brune_crochete_dans_le_dos_de_gorm(gorm_la_sait=False)
        placer(m, "marchand", "echoppe", (5, 3))
        regarder(m, "marchand", [0, 3])
        lire(m, "marchand")["croyances"].pop("brune", None)
        m = recharger(m)
        avant = lire(m, "marchand")["besoins"]["securite"]
        # Le bruit l'inquiète ; à la minute suivante, son devoir l'envoie voir.
        m = jusqu_a(m, MINUTE + 20)
        self.assertEqual([s["salle"] for s in souvenirs(m, "marchand", "bruit")], ["antichambre"])
        # Il s'inquiète à la mesure de ce qu'il entend, à travers le passage.
        self.assertGreater(lire(m, "marchand")["besoins"]["securite"], avant + 3)
        i = lire(m, "marchand")["intention"]
        self.assertEqual((i["but"], i["motif"]), ({"type": "voir", "lieu": "antichambre"}, "devoir"))
        with patch.object(Monde, "d20", return_value=1):
            faire(m, "attendre")
        m = recharger(m)
        self.assertIn("Gorm, gardien du relais passe dans : Refuge du relais.", chronique(m))
        # Arrivé, il la voit s'acharner sur la serrure : le bruit est expliqué.
        self.assertIn(("brune", "reserve"), vu_agir(m, "marchand"))
        self.assertIsNone(bruit_a_voir(m, "marchand"))


class PasConnusTests(unittest.TestCase):
    def test_brune_marche_dans_le_refuge_ou_gorm_la_sait_rien(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        for n, id in enumerate(("ilse", "aubin")):
            placer(m, id, "crypte", (2 + n, 3))
        placer(m, "marchand", "antichambre", (1, 3))
        m.objets["marchand"]["orientation"] = "ouest"
        placer(m, "brune", "antichambre", (5, 1))
        croire(m, "marchand", "brune", "lieu", "antichambre", "vu", salle="antichambre", case=[5, 1])
        m.objets["torche"].update(lieu="antichambre", position=[7, 5], position_salle="antichambre")
        croire(m, "brune", "torche", "lieu", "antichambre", "vu", salle="antichambre", case=[7, 5])
        intention(m, "brune", plan("prendre", "torche"), but="lumiere", motif="securite")
        esprit(m, "brune")["libre"] = 5
        m = recharger(m)
        faire(m, "attendre")
        m = recharger(m)
        self.assertEqual(m.objets["torche"]["lieu"], "brune")
        self.assertEqual(m.objets["marchand"]["orientation"], "ouest")
        self.assertNotIn("Gorm, gardien du relais se retourne au bruit.", chronique(m))
        self.assertEqual(souvenirs(m, "marchand", "bruit"), [])
        # Il l'a entendue : il la croit là où elle s'est arrêtée.
        crue = lire(m, "marchand")["croyances"]["brune"]["lieu"]
        self.assertEqual((crue["source"], crue["salle"]), ("entendu", "antichambre"))
        self.assertLessEqual(max(abs(crue["case"][0] - m.objets["brune"]["position"][0]),
                                 abs(crue["case"][1] - m.objets["brune"]["position"][1])), 1)


def ilse_au_refuge():
    """Ilse, au refuge, regarde vers l'est ; le joueur arrive de l'échoppe, dans son dos. Elle ne
    le sait pas là."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("marchand", "brune", "aubin")):
        placer(m, id, "crypte", (2 + n, 3))
    placer(m, "ilse", "antichambre", (4, 5))
    m.objets["ilse"]["orientation"] = "est"
    m.joueur.update(salle="echoppe", position=[8, 3], orientation="est")
    return recharger(m)


class JoueurTests(unittest.TestCase):
    def test_le_joueur_entre_a_pas_normaux_derriere_ilse_elle_se_retourne(self):
        m = ilse_au_refuge()
        texte = faire(m, "pas est")
        m = recharger(m)
        self.assertEqual(m.joueur["salle"], "antichambre")
        self.assertIn(m.objets["ilse"]["orientation"], ("ouest", "nord-ouest"))
        self.assertEqual(lire(m, "ilse")["croyances"]["joueur"]["lieu"]["valeur"], "antichambre")
        self.assertIn("Ilse, meunière évacuée, se retourne vers toi.", texte)
        # Le temps de se retourner retarde son geste suivant.
        self.assertGreaterEqual(lire(m, "ilse")["libre"], instant(m) - 15 + 4 * QUART)

    def test_a_pas_feutres_a_quelques_cases_elle_n_entend_rien(self):
        m = ilse_au_refuge()
        texte = faire(m, "faufiler est")
        m = recharger(m)
        self.assertEqual(m.joueur["salle"], "antichambre")
        self.assertEqual(m.objets["ilse"]["orientation"], "est")
        self.assertNotIn("joueur", lire(m, "ilse")["croyances"])
        self.assertNotIn("se retourne", texte)

    def test_le_joueur_entend_crocheter_dans_la_salle_voisine(self):
        m = brune_crochete_dans_le_dos_de_gorm()
        placer(m, "marchand", "crypte", (5, 3))
        m.joueur.update(salle="echoppe", position=[5, 3], orientation="ouest")
        m = recharger(m)
        with patch.object(Monde, "d20", return_value=1):
            texte = faire(m, "attendre")
        self.assertTrue(any(l.startswith("Tu entends un grand bruit") and l.endswith(" à l'est.") for l in texte.splitlines()))
        # Il ne la voit pas : rien ne la nomme.
        self.assertNotIn("Brune", texte)
        m = recharger(m)
        # Un grand bruit ne lui dit pas qui le fait : seule une voix reconnue le lui apprend.
        self.assertNotIn("brune", m.data["entendus"])


def mine_baraquement(qui):
    """Dans la mine, au baraquement : ``qui`` regarde vers l'ouest ; Odon, dans son dos, part vers la
    galerie. Rémy se méfie d'Odon depuis le début ; Josse lui fait confiance."""
    m = creer("mine", depart="fixe")
    autres = [x for x in ("bram", "gaspard", "josse", "lucien", "mathe", "remy") if x != qui]
    calme(m, qui, "odon", *autres)
    for n, id in enumerate(autres):
        placer(m, id, "bureau" if n < 3 else "entree", (1 + n % 3, 1))
    placer(m, qui, "baraquement", (4, 3))
    m.objets[qui]["orientation"] = "ouest"
    placer(m, "odon", "baraquement", (7, 3))
    croire(m, qui, "odon", "lieu", "baraquement", "vu", salle="baraquement", case=[7, 3])
    intention(m, "odon", plan("aller", lieu="galerie"), but="rejoindre", motif="devoir")
    esprit(m, "odon")["libre"] = 5
    return recharger(m)


class MefianceTests(unittest.TestCase):
    def test_un_bruit_d_odon_dont_remy_se_mefie_se_surveille(self):
        m = mine_baraquement("remy")
        self.assertFalse(lire(m, "remy")["croyances"]["odon"]["fiable"]["valeur"])
        faire(m, "attendre")
        m = recharger(m)
        self.assertIn("Rémy, jeune mineur se retourne au bruit.", chronique(m))
        self.assertNotEqual(m.objets["remy"]["orientation"], "ouest")

    def test_le_meme_bruit_de_qui_l_on_croit_fiable_ne_le_fait_pas_se_retourner(self):
        m = mine_baraquement("josse")
        self.assertTrue(lire(m, "josse")["croyances"]["odon"]["fiable"]["valeur"])
        faire(m, "attendre")
        m = recharger(m)
        self.assertNotIn("Josse, contremaître se retourne au bruit.", chronique(m))
        self.assertEqual(m.objets["josse"]["orientation"], "ouest")


def bruit_au_refuge(qui):
    """``qui`` est seul à l'échoppe ; au refuge voisin, que sa garde ne concerne pas, Brune crochète
    la réserve. Il ne la sait pas là."""
    m = brune_crochete_dans_le_dos_de_gorm(gorm_la_sait=False)
    placer(m, "marchand", "crypte", (5, 3))
    for id in ("ilse", "aubin"):
        if id != qui:
            placer(m, id, "crypte", (2 if id == "ilse" else 3, 4))
    placer(m, qui, "echoppe", (5, 3))
    regarder(m, qui, [0, 3])
    lire(m, qui)["croyances"].pop("brune", None)
    # Le refuge n'est pas sous sa garde : ses rondes servent sa propre sécurité.
    m.objets[qui]["profil"]["pulsions"] = []
    lire(m, qui)["pulsions"] = []
    return recharger(m)


class CourageTests(unittest.TestCase):
    def test_ilse_peu_courageuse_s_inquiete_sans_y_aller(self):
        m = bruit_au_refuge("ilse")
        avant = lire(m, "ilse")["besoins"]["securite"]
        m = jusqu_a(m, MINUTE + 20)
        self.assertEqual([s["salle"] for s in souvenirs(m, "ilse", "bruit")], ["antichambre"])
        self.assertGreater(lire(m, "ilse")["besoins"]["securite"], avant + 3)
        self.assertIsNone(bruit_a_voir(m, "ilse"))
        with patch.object(Monde, "d20", return_value=1):
            faire(m, "attendre")
        m = recharger(m)
        self.assertEqual(m.objets["ilse"]["lieu"], "echoppe")
        self.assertNotIn("Ilse, meunière évacuée passe dans : Refuge du relais.", chronique(m))
        self.assertEqual(vu_agir(m, "ilse"), [])

    def test_aubin_plus_courageux_va_voir(self):
        m = bruit_au_refuge("aubin")
        m = jusqu_a(m, MINUTE + 20)
        i = lire(m, "aubin")["intention"]
        self.assertEqual((i["but"], i["motif"]), ({"type": "voir", "lieu": "antichambre"}, "securite"))
        with patch.object(Monde, "d20", return_value=1):
            faire(m, "attendre")
        m = recharger(m)
        self.assertIn("Aubin, vieux passeur passe dans : Refuge du relais.", chronique(m))
        self.assertIn(("brune", "reserve"), vu_agir(m, "aubin"))


class CroyanceEntendueTests(unittest.TestCase):
    """Révélé par l'ouïe à l'auberge : entendre quelqu'un dans le noir entretient la croyance qu'il
    est là ; un geste social vers lui qui reste sans réponse doit la corriger, comme tout geste
    manqué, sans quoi le PNJ le redemande sans fin."""

    def test_demander_a_qui_n_est_pas_la_corrige_la_croyance(self):
        m = refusee(calme(relais(), "marchand", "brune", "ilse", "aubin"), id="ilse")
        for n, id in enumerate(("ilse", "aubin")):
            placer(m, id, "crypte", (2 + n, 3))
        placer(m, "marchand", "crypte", (5, 3))
        placer(m, "brune", "antichambre", (6, 1))
        # Brune croit Gorm près d'elle au refuge, entendu à l'instant ; il est aux vannes.
        croire(m, "brune", "marchand", "lieu", "antichambre", "entendu", salle="antichambre", case=[7, 1])
        lire(m, "brune")["besoins"]["faim"] = 80.0
        intention(m, "brune", {"operation": "demander", "cible": "marchand", "outil": "vivres", "lieu": "",
                               "condition": ""}, but="part", motif="faim")
        m = recharger(m)
        faire(m, "attendre")
        m = recharger(m)
        # Personne ne lui répond au refuge : la croyance du départ est corrigée ; elle le cherche,
        # l'appelle, et ne lui demande sa part qu'une fois retrouvé, aux vannes.
        self.assertIn("Brune appelle : « Gorm ? »", chronique(m))
        self.assertIn("Gorm répond : « Ici ! »", chronique(m))
        self.assertGreater(lire(m, "brune")["croyances"]["marchand"]["lieu"]["minute"], 0)
        self.assertNotIn("Brune demande une part des vivres du refuge à Gorm (refus).", chronique(m))


if __name__ == "__main__":
    unittest.main()
