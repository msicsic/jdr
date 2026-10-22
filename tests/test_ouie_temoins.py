"""L'ouïe et les témoins (branche ``ouie-temoins``, défauts 2, 3 et 6 de ``docs/audit-nuits.md``).

- Un bruit inconnu de sa propre salle s'examine comme celui d'un autre lieu : il le situe à une case,
  et aller voir le mène à portée de vue de cette case, ou au contact si rien ne l'éclaire.
- On est témoin d'un geste par l'ouïe, d'une certitude moindre que la vue : qui l'entend dans sa
  salle et croit l'objet tout près de là sait qu'on y touche ; il ne nomme l'auteur que s'il le
  reconnaît (il le croit là d'où vient le bruit).
- Être allé voir sans rien trouver (ou sans rien pouvoir voir) règle le bruit : le même, ou un
  moindre, venu du même endroit n'y renvoie plus ; seul un bruit nouveau le relance.

Chaque cas vérifie l'état du monde après rechargement."""
import copy
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon.esprits import croire, esprit, lire, percevoir_tous
from donjon.geometrie import distance, position_entree
from donjon.monde import Monde
from donjon.ouie import couvert, entendre, parcouru
from donjon.social import nouvelles
from donjon.temps import instant
from tests.support import calme, refusee, regarder
from tests.test_ouie import faire, intention, jusqu_a, plan, souvenirs, vu_agir
from tests.test_tensions import chronique, placer, recharger, relais

MINEURS = ("bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy")


def attendre(m, minutes):
    """Le joueur se tourne sur place ``minutes`` minutes durant, rechargé en route (``jusqu_a``) ; le
    d20 tombe à 1 : un crochetage échoue et recommence."""
    return jusqu_a(m, instant(m) + minutes * 600)


def etat(m):
    """Ce que le monde retient de tous les personnages et des objets."""
    ids = [id for id, o in m.objets.items() if o["type"] == "personnage"]
    return {"corps": {id: {k: m.objets[id].get(k) for k in ("lieu", "position", "orientation")} for id in ids},
            "esprits": copy.deepcopy(m.data.get("esprits", {})),
            "objets": {id: (o["lieu"], o.get("position"), o.get("ouverte"), o.get("verrouillee"), o.get("portions"))
                       for id, o in m.objets.items() if o["type"] != "personnage"},
            "chronique": copy.deepcopy(m.data.get("chronique", [])),
            "gestes_en_cours": copy.deepcopy(m.data.get("gestes_en_cours", [])),
            "jets": m.data["jets"], "instant": instant(m)}


def decouper(scene, minutes, jet=1):
    """Le même laps : une attente d'un bloc, puis des rotations du joueur rechargées en route."""
    with patch.object(Monde, "d20", return_value=jet):
        d_un_bloc = scene()
        while d_un_bloc.data["minutes"] < minutes:
            faire(d_un_bloc, "attendre")
        morcele, n = scene(), 0
        while instant(morcele) < instant(d_un_bloc):
            faire(morcele, "tourner sud" if n % 2 == 0 else "tourner nord")
            n += 1
            if n % 15 == 0:
                morcele = recharger(morcele)
    return d_un_bloc, recharger(morcele)


# --- Les scènes ---------------------------------------------------------------------------

def brune_loin_de_gorm(gardien="marchand"):
    """Cas réel (Relais, graine 7, minutes 28 à 31) : au refuge, dans la pénombre (on n'y voit qu'à
    trois cases), Brune, affamée et refusée, crochète la réserve ; ``gardien`` se tient à sept cases,
    le dos tourné, sans la savoir là. Gorm (``marchand``) : son devoir de garde ; Aubin : son courage
    (Gorm est alors loin, à la galerie)."""
    m = refusee(calme(relais(), "marchand", "brune", "ilse", "aubin"))
    placer(m, "ilse", "crypte", (2, 3))
    placer(m, "aubin", "crypte", (3, 3))
    if gardien != "marchand":
        placer(m, "marchand", "chambre_cloche", position_entree(m, "chambre_cloche"))
    m.objets["crochets"]["lieu"] = "brune"
    placer(m, "brune", "antichambre", (7, 3))
    regarder(m, "brune", "reserve")
    placer(m, gardien, "antichambre", (0, 3))
    m.objets[gardien]["orientation"] = "ouest"
    lire(m, "brune")["besoins"]["faim"] = 99.0
    intention(m, "brune", plan("crocheter", "reserve", "crochets"))
    esprit(m, "brune")["libre"] = 5
    m.joueur["orientation"] = "nord"
    percevoir_tous(m)
    for id in ("marchand", "aubin", "ilse"):
        lire(m, id)["croyances"].pop("brune", None)
    return recharger(m)


def odon_au_coffre(bram_le_sait=False):
    """Cas réel (mine, graine 500, minutes 456 à 461) : dans le bureau noir (la chandelle est
    morte), Odon crochète le coffre de la paie ; Bram, qui le garde, se tient à la case voisine,
    tourné vers lui, sans le voir. ``bram_le_sait`` : Bram l'a entendu entrer et le croit là."""
    m = creer("mine", 1985, depart="fixe")
    calme(m, *MINEURS)
    m.objets["chandelle"].update(allume=False, combustible=0)
    placer(m, "odon", "bureau", (3, 2))
    regarder(m, "odon", "coffre_paie")
    placer(m, "bram", "bureau", (2, 2))
    m.objets["bram"]["orientation"] = "est"
    placer(m, "josse", "baraquement", (6, 2))
    m.joueur["orientation"] = "nord"
    intention(m, "odon", plan("crocheter", "coffre_paie", "crochets"), but="argent", motif="argent")
    esprit(m, "odon")["libre"] = 5
    percevoir_tous(m)
    lire(m, "bram")["croyances"].pop("odon", None)
    if bram_le_sait:
        croire(m, "bram", "odon", "lieu", "bureau", "entendu", salle="bureau", case=[3, 2])
    return recharger(m)


def lucien_au_coffre():
    """Cas réel (auberge, graine 1, minutes 313 à 449) : dans la chambre au poêle éteint, Lucien
    crochète le coffre ferré d'Anselme, à une diagonale d'Anselme, qui l'y a entendu entrer ; rien
    n'éclaire plus la chambre ni le couloir."""
    m = creer("auberge", 1, depart="fixe")
    for source in ("poele", "lanterne_couloir"):
        m.objets[source]["allume"] = False
    m.joueur["orientation"] = "nord"
    calme(m, *[id for id, o in m.objets.items() if o["type"] == "personnage" and o.get("profil")])
    placer(m, "lucien", "chambre_chaude", (1, 3))
    regarder(m, "lucien", "coffre_marchand")
    placer(m, "anselme", "chambre_chaude", (2, 2))
    m.objets["anselme"]["orientation"] = "est"
    intention(m, "lucien", plan("crocheter", "coffre_marchand", "crochets_lucien"), but="argent", motif="argent")
    esprit(m, "lucien")["libre"] = 5
    percevoir_tous(m)
    croire(m, "anselme", "lucien", "lieu", "chambre_chaude", "entendu", salle="chambre_chaude", case=[1, 3])
    return recharger(m)


# --- Défaut 2 : un bruit de sa propre salle --------------------------------------------------

class BruitDeSaSalleTests(unittest.TestCase):
    def test_cas_reel_gorm_va_voir_le_fracas_de_sa_salle(self):
        m = brune_loin_de_gorm()
        self.assertGreater(distance(m.objets["marchand"]["position"], m.objets["brune"]["position"]), 6)
        m = attendre(m, 3)
        textes = chronique(m)
        # Trop loin pour se retourner, il situe le fracas, va à portée de vue et la voit à l'œuvre.
        self.assertIn("Gorm entend un bruit : Refuge du relais.", textes)
        self.assertIn("Gorm va voir de près d'où venait le bruit : Refuge du relais.", textes)
        self.assertIn(("brune", "reserve"), vu_agir(m, "marchand"))
        self.assertFalse(lire(m, "marchand")["croyances"]["brune"]["fiable"]["valeur"])
        self.assertLess(distance(m.objets["marchand"]["position"], m.objets["brune"]["position"]), 7)

    def test_aubin_courageux_va_voir_le_fracas_de_sa_salle(self):
        # Autre cas de même nature : rien à garder, son courage l'y envoie (au-dessus de la moyenne).
        m = attendre(brune_loin_de_gorm("aubin"), 3)
        self.assertIn("Aubin va voir de près d'où venait le bruit : Refuge du relais.", chronique(m))
        self.assertIn(("brune", "reserve"), vu_agir(m, "aubin"))

    def test_le_bruit_retenu_porte_sa_case_que_le_mj_ne_recoit_pas(self):
        from donjon.esprits import dernier_son
        m = brune_loin_de_gorm()
        entendre(m, "marchand", "brune", "antichambre", (7, 3), "bruyant", 0, 4)
        bruit = souvenirs(m, "marchand", "bruit")[-1]
        self.assertEqual(bruit["case"], [7, 3])
        self.assertNotIn("case", dernier_son(m, "marchand"))

    def test_meme_laps_decoupe_meme_monde(self):
        d_un_bloc, morcele = decouper(brune_loin_de_gorm, 3)
        self.assertIn("Gorm va voir de près d'où venait le bruit : Refuge du relais.", chronique(morcele))
        self.assertEqual(etat(d_un_bloc), etat(morcele))


# --- Défaut 3 : témoin par l'ouïe --------------------------------------------------------------

class TemoinParLOuieTests(unittest.TestCase):
    def test_cas_reel_bram_entend_forcer_le_coffre_sans_savoir_qui(self):
        m = attendre(odon_au_coffre(), 1)
        self.assertIn("Bram entend que quelqu'un a tenté de crocheter la serrure du coffre de la paie.", chronique(m))
        atteintes = souvenirs(m, "bram", "entendu_agir")
        self.assertEqual([(s["operation"], s["objet"]) for s in atteintes], [("forcer", "coffre_paie")])
        # Il ne l'a pas reconnu : personne n'est accusé, et ce qu'il sait ne se répète pas en rumeur.
        self.assertNotIn("fiable", lire(m, "bram")["croyances"].get("odon", {}))
        self.assertEqual(vu_agir(m, "bram"), [])
        self.assertEqual(list(nouvelles(m, "bram")), [])
        # Ses biens touchés le pressent ; le bruit, qu'il situe, il va le voir.
        self.assertGreaterEqual(lire(m, "bram")["besoins"]["biens"], 60)
        self.assertIn("Bram va voir de près d'où venait le bruit : Bureau du contremaître.", chronique(m))
        # Au contact, dans le noir, il n'y voit rien : il a fait ce qu'il pouvait, le bruit est réglé.
        self.assertEqual(souvenirs(m, "bram", "bruit"), [])
        self.assertEqual([(s["case"], s["nature"]) for s in souvenirs(m, "bram", "examen")], [([3, 2], "bruyant")])
        # Josse, alerté, vient avec sa lampe ; Odon, qui les sait à portée d'oreille, n'insiste pas.
        m = attendre(m, 1)
        self.assertEqual(sum("s'acharne sur la serrure" in t for t in chronique(m)), 1)

    def test_bram_qui_le_croit_la_le_reconnait(self):
        m = attendre(odon_au_coffre(bram_le_sait=True), 1)
        self.assertIn("Bram entend qu'Odon a tenté de crocheter la serrure du coffre de la paie.", chronique(m))
        temoignages = [s for s in souvenirs(m, "bram", "vu_agir") if s["auteur"] == "odon"]
        self.assertTrue(temoignages and all(s["par"] == "ouie" for s in temoignages))
        fiable = lire(m, "bram")["croyances"]["odon"]["fiable"]
        self.assertEqual((fiable["valeur"], fiable["source"]), (False, "entendu"))
        # Ce qu'il n'a qu'entendu se dit avec moins de certitude : comme de seconde main.
        self.assertEqual({rang for _, _, rang, _ in nouvelles(m, "bram")}, {1})

    def test_cas_reel_anselme_entend_lucien_forcer_son_coffre(self):
        # Autre cas de même nature : la victime elle-même, qui a entendu entrer le voleur.
        m = attendre(lucien_au_coffre(), 1)
        self.assertIn("Anselme entend que Lucien a tenté de crocheter la serrure du coffre ferré.", chronique(m))
        self.assertIn(("lucien", "coffre_marchand"), vu_agir(m, "anselme"))
        self.assertFalse(lire(m, "anselme")["croyances"]["lucien"]["fiable"]["valeur"])

    def test_qui_veut_agir_sans_temoin_compte_ceux_qu_il_croit_a_portee_d_oreille(self):
        # L'auteur de son côté : Brune veut forcer la réserve sans témoin. Elle ne voit pas Gorm, à sept
        # cases dans la pénombre ; si elle le sait là, il l'entendrait : elle attend, sinon elle force.
        def brune_en_douce(le_sait):
            m = brune_loin_de_gorm()
            intention(m, "brune", plan("crocheter", "reserve", "crochets", condition="sans_temoin"))
            lire(m, "brune")["besoins"]["faim"] = 80.0
            if le_sait:
                croire(m, "brune", "marchand", "lieu", "antichambre", "entendu", salle="antichambre", case=[0, 3])
            return recharger(m)
        sait, ignore = attendre(brune_en_douce(True), 2), attendre(brune_en_douce(False), 1)
        self.assertFalse(any("s'acharne" in t for t in chronique(sait)))
        etape = lire(sait, "brune")["intention"]["plan"][0]
        self.assertEqual((etape["operation"], etape["condition"]), ("crocheter", "sans_temoin"))
        self.assertTrue(any("s'acharne" in t for t in chronique(ignore)))

    def test_la_vue_prime_sur_l_ouie(self):
        # Il voit faire : il est témoin par la vue, pas par l'ouïe.
        from tests.test_ouie import brune_crochete_dans_le_dos_de_gorm
        m = brune_crochete_dans_le_dos_de_gorm()
        m = attendre(m, 1)
        self.assertTrue(vu_agir(m, "marchand"))
        self.assertTrue(all(s.get("par") != "ouie" for s in souvenirs(m, "marchand", "vu_agir")))

    def test_meme_laps_decoupe_meme_monde(self):
        d_un_bloc, morcele = decouper(odon_au_coffre, 2)
        self.assertTrue(souvenirs(morcele, "bram", "entendu_agir"))
        self.assertEqual(etat(d_un_bloc), etat(morcele))


# --- Défaut 6 : être allé voir règle le bruit ---------------------------------------------------

class AllerVoirRegleTests(unittest.TestCase):
    def test_un_examen_vain_couvre_le_meme_bruit_pas_un_nouveau(self):
        m = odon_au_coffre()
        lire(m, "bram")["memoire"].append({"type": "bruit", "salle": "bureau", "nature": "bruyant", "niveau": 5,
                                            "case": [3, 2], "minute": m.data["minutes"]})
        self.assertTrue(parcouru(m, "bram", "bureau", (3, 2)))
        m = recharger(m)
        self.assertIsNotNone(couvert(m, "bram", "bureau", "bruyant", None, (3, 2)))
        # Dans ce bureau où il n'a rien pu voir, des pas, un autre bruit pareil ailleurs, ne lui
        # apprennent rien ; seul un bruit nouveau le relance : plus fort, d'une voix reconnue.
        self.assertIsNotNone(couvert(m, "bram", "bureau", "pas", None, (4, 2)))
        self.assertIsNotNone(couvert(m, "bram", "bureau", "bruyant", None, (0, 0)))
        self.assertIsNone(couvert(m, "bram", "bureau", "appel", None, (3, 2)))
        self.assertIsNone(couvert(m, "bram", "bureau", "bruyant", "odon", (3, 2)))

    def test_cas_reel_l_appel_repete_n_y_renvoie_plus(self):
        # Cas réel (mine, graine 18, minutes 455 à 560) : Mathe, au baraquement, va voir un appel du
        # bureau noir, n'y voit personne ; l'appel suivant, du même endroit, ne l'y renvoie plus.
        m = creer("mine", 18, depart="fixe")
        calme(m, *MINEURS)
        m.objets["chandelle"].update(allume=False, combustible=0)
        m.objets["porte_bureau"].update(verrouillee=False, ouverte=True)
        placer(m, "mathe", "baraquement", (2, 2))
        placer(m, "lucien", "bureau", (0, 3))
        percevoir_tous(m)
        entendre(m, "mathe", "lucien", "bureau", (0, 3), "appel", 0, 6)
        bruit = souvenirs(m, "mathe", "bruit")[-1]
        self.assertEqual((bruit["salle"], bruit.get("case")), ("bureau", None))
        # Elle y va, parcourt le bureau des yeux : rien (le noir).
        self.assertTrue(parcouru(m, "mathe", "bureau"))
        m = recharger(m)
        entendre(m, "mathe", "lucien", "bureau", (0, 3), "appel", 0, 6)
        self.assertEqual(souvenirs(m, "mathe", "bruit"), [])
        # Plus fort qu'un appel, rien ; mais de la salle même, elle le situe : c'est nouveau.
        placer(m, "mathe", "bureau", (4, 0))
        entendre(m, "mathe", "lucien", "bureau", (0, 3), "appel", 0, 6)
        self.assertEqual(souvenirs(m, "mathe", "bruit")[-1]["case"], [0, 3])


if __name__ == "__main__":
    unittest.main()
