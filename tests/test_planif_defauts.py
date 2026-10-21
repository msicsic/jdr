"""Trois défauts du planificateur des PNJ, vérifiés après rechargement : la chance de crocheter
est celle du jet réel à la lumière qu'il croit ; une porte verrouillée se crochète comme un
contenant ; les pièces d'une bourse se comptent sur ce qu'il en croit, jamais sur l'objet."""
import unittest
from unittest.mock import patch

from donjon import pnj
from donjon.banc_pnj import creer
from donjon.caractere import modificateur
from donjon.deliberation import lumiere_crue
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.perception import eclairage
from donjon.planification import chance_crochetage, enrichir, planifier
from tests.support import calme, refusee
from tests.test_tensions import chronique, placer, recharger, relais, vivre

MINEURS = ("bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy")


def chance_reelle(m, id):
    """La part des vingt faces du d20 qui crochètent, à la lumière réelle de sa case."""
    o = m.objets[id]
    lumiere = eclairage(m, o["lieu"], o["position"])["niveau"]
    seuil = pnj.seuil_crochetage(lumiere)
    return sum(d + modificateur(m, id, "DEX") >= seuil for d in range(1, 21)) / 20


def odon_au_bureau(porte="verrouillee"):
    """Mine : la nuit est avancée ; Odon, endetté, affamé (son adresse s'en ressent), ses crochets
    en main, se tient devant le coffre de la paie. La chandelle du bureau est morte. ``porte`` : la
    porte du bureau verrouillée (il ne peut sortir chercher de la lumière), ou ouverte (la lueur du
    baraquement entre)."""
    m = creer("mine", 1985)
    calme(m, *MINEURS)
    lire(m, "odon")["besoins"]["faim"] = 78.0
    placer(m, "bram", "baraquement", (2, 2))
    placer(m, "odon", "bureau", (3, 2))
    m.objets["chandelle"].update(allume=False, combustible=0)
    if porte == "ouverte":
        m.objets["porte_bureau"].update(verrouillee=False, ouverte=True)
    percevoir_tous(m)
    return recharger(m)


def brune_aux_vannes(brasero=True):
    """Variante du Relais : la réserve de vivres est dans la salle des vannes ; Brune, affamée,
    refusée par Gorm, ses crochets en main, se tient devant. Sans ``brasero``, le feu de la conduite
    est mort et la salle des vannes est noire."""
    m = refusee(calme(relais(), "marchand", "ilse", "aubin"))
    lire(m, "brune")["besoins"]["faim"] = 85.0
    deplacer(m, "crochets", "brune")
    m.objets["reserve"].update(lieu="crypte", position_salle="crypte", position=[7, 4])
    for id in ("marchand", "brune", "ilse", "aubin"):
        croire(m, id, "vivres", "lieu", "reserve", "savoir", salle="crypte", case=[7, 4])
    placer(m, "brune", "crypte", (6, 3))
    placer(m, "marchand", "antichambre", (2, 2))
    if not brasero:
        m.objets["brasero"]["allume"] = False
    percevoir_tous(m)
    return recharger(m)


def tentatives(m, id, cible):
    nom = m.objets[cible]["nom"]
    return [t for t in chronique(m) if t.startswith(m.objets[id]["nom"].split(",")[0]) and nom in t
            and ("s'acharne" in t or "crochète" in t)]


class ChanceCrueTests(unittest.TestCase):
    def test_dans_le_noir_odon_ne_s_acharne_pas_sur_le_coffre(self):
        # Cas réel (mine, graine 1985, minute 450) : une heure d'essais au coffre dans le noir, où
        # aucun jet ne réussit ; le planificateur lui prêtait 5 %.
        m = odon_au_bureau()
        self.assertEqual(lumiere_crue(m, "odon", "bureau"), 0)
        self.assertEqual(chance_reelle(m, "odon"), 0)
        self.assertEqual(chance_crochetage(m, "odon", 0), 0)
        self.assertIsNone(enrichir(m, "odon"))
        m, _ = vivre(m, 15)
        self.assertEqual(tentatives(m, "odon", "coffre_paie"), [])
        self.assertTrue(m.objets["coffre_paie"]["verrouillee"])

    def test_dans_la_penombre_la_chance_crue_est_celle_du_jet(self):
        # La porte ouverte, la lueur du baraquement entre : il le sait, et sa chance est la vraie.
        m = odon_au_bureau("ouverte")
        self.assertEqual(lumiere_crue(m, "odon", "bureau"), 1)
        self.assertGreater(chance_reelle(m, "odon"), 0)
        self.assertEqual(chance_crochetage(m, "odon", lumiere_crue(m, "odon", "bureau")), chance_reelle(m, "odon"))
        but, etapes = enrichir(m, "odon")
        self.assertEqual(etapes[0]["operation"], "crocheter")

    def test_aux_vannes_noires_brune_ne_crochete_pas(self):
        # Autre cas de même nature : la réserve aux vannes, que Brune forçait dix-sept fois par nuit.
        m = brune_aux_vannes(brasero=False)
        self.assertEqual(lumiere_crue(m, "brune", "crypte"), 0)
        self.assertEqual(chance_reelle(m, "brune"), 0)
        resultat = planifier(m, "brune", "faim")
        self.assertNotIn("crocheter", [x["operation"] for x in (resultat or (None, []))[1]])
        m, _ = vivre(m, 10)
        self.assertEqual(tentatives(m, "brune", "reserve"), [])
        # Le brasero vif, la pénombre gagne les vannes : elle le sait, et elle essaie.
        m = brune_aux_vannes()
        self.assertEqual(lumiere_crue(m, "brune", "crypte"), 1)
        self.assertEqual(chance_crochetage(m, "brune", 1), chance_reelle(m, "brune"))
        self.assertEqual(planifier(m, "brune", "faim")[1][0]["operation"], "crocheter")

    def test_un_echec_apprend_la_lumiere_qu_il_avait(self):
        # Elle croyait les vannes éclairées (vues autrefois) ; la serrure résiste : elle sait
        # désormais la lumière qu'elle avait là, celle qui fait sa chance.
        m = brune_aux_vannes(brasero=False)
        croire(m, "brune", "crypte", "etat", {"eclairee": True, "niveau": 2}, "vu")
        with patch.object(Monde, "d20", return_value=20):
            self.assertFalse(pnj._crocheter(m, "brune", "reserve", "crochets"))
        m = recharger(m)
        self.assertEqual(lire(m, "brune")["croyances"]["crypte"]["etat"]["valeur"], {"eclairee": False, "niveau": 0})
        self.assertIsNone(planifier(m, "brune", "faim"))


class PorteTests(unittest.TestCase):
    def odon_devant_la_porte(self):
        """Mine : Odon, endetté, ses crochets en main, se tient devant la porte du bureau qu'il sait
        verrouillée ; les autres sont au filon, le joueur au puits ; le baraquement est éclairé."""
        m = creer("mine", 1985)
        calme(m, *MINEURS)
        for i, id in enumerate(("bram", "josse", "lucien", "mathe", "remy", "gaspard")):
            placer(m, id, "filon", (4 + i, 2))
        placer(m, "odon", "baraquement", (4, 1))
        m.joueur.update(salle="puits", position=[3, 2])
        percevoir_tous(m)
        return recharger(m)

    def test_odon_crochete_la_porte_du_bureau_pour_la_paie(self):
        # Cas réel : il croyait la porte verrouillée et n'envisageait jamais de la crocheter.
        m = self.odon_devant_la_porte()
        self.assertTrue(lire(m, "odon")["croyances"]["porte_bureau"]["verrouillee"]["valeur"])
        but, etapes = enrichir(m, "odon")
        self.assertEqual(but, {"type": "argent", "objet": "paie"})
        self.assertEqual([(x["operation"], x["cible"] or x["lieu"]) for x in etapes[:3]],
                         [("crocheter", "porte_bureau"), ("aller", "bureau"), ("crocheter", "coffre_paie")])
        # La porte est à Bram : la crocheter est une faute, qui attend de n'être vue de personne.
        self.assertEqual(etapes[0]["condition"], "sans_temoin")
        m, _ = vivre(m, 6, jet=20)
        self.assertIn("Odon, nouveau venu crochète la serrure de la porte du bureau.", chronique(m))
        self.assertFalse(m.objets["porte_bureau"]["verrouillee"])
        self.assertFalse(lire(m, "odon")["croyances"]["porte_bureau"]["verrouillee"]["valeur"])
        self.assertEqual(m.objets["paie"]["lieu"], "odon")

    def test_brune_crochete_la_porte_etanche_pour_la_reserve_du_palier(self):
        # Autre cas de même nature : la réserve est au palier, derrière la porte étanche verrouillée ;
        # Brune, affamée, une torche allumée en main, n'a pas la clé.
        m = refusee(calme(relais(), "marchand", "ilse", "aubin"))
        lire(m, "brune")["besoins"]["faim"] = 85.0
        for objet in ("crochets", "torche"):
            deplacer(m, objet, "brune")
        m.objets["torche"]["allume"] = True
        m.objets["reserve"].update(lieu="beffroi", position_salle="beffroi", position=[2, 2])
        for id in ("marchand", "brune", "ilse", "aubin"):
            croire(m, id, "vivres", "lieu", "reserve", "savoir", salle="beffroi", case=[2, 2])
            croire(m, id, "porte", "verrouillee", True, "savoir")
        placer(m, "brune", "crypte", (7, 3))
        placer(m, "marchand", "antichambre", (2, 2))
        percevoir_tous(m)
        m = recharger(m)
        _, etapes = planifier(m, "brune", "faim")
        self.assertEqual([(x["operation"], x["cible"] or x["lieu"]) for x in etapes],
                         [("crocheter", "porte"), ("aller", "beffroi"), ("crocheter", "reserve"),
                          ("ouvrir", "reserve"), ("manger", "vivres")])
        m, _ = vivre(m, 3, jet=20)
        self.assertIn("Brune, batelière évacuée crochète la serrure de la porte étanche du beffroi.", chronique(m))
        self.assertFalse(m.objets["porte"]["verrouillee"])
        self.assertFalse(lire(m, "brune")["croyances"]["porte"]["verrouillee"]["valeur"])
        # La porte crochetée, elle passe au palier.
        self.assertEqual(m.objets["brune"]["lieu"], "beffroi")


class PiecesCruesTests(unittest.TestCase):
    def paie_a_portee(self):
        """Mine : Odon, endetté, seul au bureau devant le coffre de la paie, ses crochets en main ;
        il sait, comme le camp, que la paie compte 200 pièces."""
        m = creer("mine", 1985)
        calme(m, *MINEURS)
        placer(m, "bram", "baraquement", (2, 2))
        placer(m, "odon", "bureau", (3, 2))
        percevoir_tous(m)
        return recharger(m)

    def test_odon_compte_les_pieces_qu_il_croit_dans_la_paie(self):
        # Cas réel : enrichir lisait le vrai compte de la bourse.
        m = self.paie_a_portee()
        self.assertEqual(lire(m, "odon")["croyances"]["paie"]["pieces"]["valeur"], 200)
        # Bram a vidé la paie sans qu'il le sache : il la convoite toujours.
        m.objets["paie"]["pieces"] = 1
        m = recharger(m)
        self.assertEqual(enrichir(m, "odon")[0], {"type": "argent", "objet": "paie"})
        # Il la croit presque vide (rien ne lui dit le contraire), pleine en vérité : elle ne le tente pas.
        m.objets["paie"]["pieces"] = 200
        croire(m, "odon", "paie", "pieces", 1, "vu")
        self.assertIsNone(enrichir(recharger(m), "odon"))
        # Il la prend : la tenant, il en sait le compte.
        croire(m, "odon", "paie", "pieces", 200, "savoir")
        m, _ = vivre(recharger(m), 5, jet=20)
        self.assertEqual(m.objets["paie"]["lieu"], "odon")
        self.assertEqual(lire(m, "odon")["croyances"]["paie"]["pieces"]["valeur"], m.objets["paie"]["pieces"])

    def test_lucien_ne_convoite_pas_une_bourse_dont_il_ne_sait_rien(self):
        # Autre cas de même nature : l'auberge, la bourse d'Anselme dans le coffre ferré. Lucien sait
        # où elle est ; tant qu'il ne sait pas ce qu'elle contient, elle ne le tente pas.
        m = creer("auberge", 1985)
        calme(m, *[k for k, o in m.objets.items() if o["type"] == "personnage" and o.get("profil")])
        croire(m, "lucien", "bourse_anselme", "lieu", "coffre_marchand", "vu", salle="chambre_chaude",
               case=m.objets["coffre_marchand"]["position"])
        self.assertIsNone(enrichir(recharger(m), "lucien"))
        croire(m, "lucien", "bourse_anselme", "pieces", 150, "vu")
        but, _ = enrichir(recharger(m), "lucien")
        self.assertEqual(but, {"type": "argent", "objet": "bourse_anselme"})


if __name__ == "__main__":
    unittest.main()
