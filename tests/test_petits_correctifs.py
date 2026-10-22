"""Petits correctifs des PNJ, vérifiés après rechargement :

- la lumière d'un geste qui demande d'y voir se constate là où il s'accomplit : arrivé devant la
  serrure plus sombre que prévu, il renonce sans essai perdu, et la retient ;
- une part payée d'avance et jamais servie est rendue, ou due et réclamée, au joueur comme aux PNJ ;
- les PNJ forcent une porte ou un contenant par la règle du joueur (``force``) ;
- Gorm va chercher son propre bois : la lueur diffuse qui baigne une salle compte pour sa lumière,
  et une part demandée coûte selon la chance d'être accordée."""
import unittest

from donjon import force
from donjon.banc_pnj import creer
from donjon.biens import bourse
from donjon.deliberation import lumiere_crue, noir_cru
from donjon.deplacement_objet import deplacer
from donjon.echanges import ENGAGEMENT_MAX, demander
from donjon.esprits import croire, lire, percevoir_tous
from donjon.moteur import Moteur, proposition
from donjon.planification import DEMANDE, PRET, Vue, depart, gestes, planifier, planifier_pulsion
from tests.support import calme, refusee, regarder
from tests.test_planif_defauts import MINEURS
from tests.test_tensions import chronique, placer, recharger, relais, vivre


def de(m, id):
    """Les lignes de la chronique où ``id`` agit."""
    return [c for c in m.data.get("chronique", []) if c["pnj"] == id]


def essais(m, id, objet):
    nom = m.objets[objet]["nom"]
    return [c for c in de(m, id) if nom in c["texte"] and ("s'acharne" in c["texte"] or "crochète" in c["texte"])]


def renoncements(m, id, objet):
    nom = m.objets[objet]["nom"]
    return [c for c in de(m, id) if "renonce à crocheter" in c["texte"] and nom in c["texte"]]


class LumiereDevantLaSerrureTests(unittest.TestCase):
    """Le plan comptait sur la lumière de la case d'où il partait ; devant la serrure, il la
    constate. Plus sombre, il ne tente rien et reconsidère sur ce qu'il vient de voir."""

    def odon_vers_le_bureau(self):
        """Cas réel (mine, graine 1985, minute 450) : Odon, endetté, ses crochets en main, se tient
        dans le baraquement éclairé ; il ne sait rien du bureau, dont la chandelle est morte, et
        l'imagine comme le baraquement. La porte, qu'il croit verrouillée, ne l'est plus. Les autres
        sont au filon, le joueur au puits."""
        m = creer("mine", 1985)
        calme(m, *MINEURS)
        for i, id in enumerate(("bram", "josse", "lucien", "mathe", "remy", "gaspard")):
            placer(m, id, "filon", (4 + i, 2))
        placer(m, "odon", "baraquement", (4, 1))
        m.objets["chandelle"].update(allume=False, combustible=0)
        m.objets["porte_bureau"]["verrouillee"] = False
        m.joueur.update(salle="puits", position=[3, 2])
        percevoir_tous(m)
        return recharger(m)

    def test_odon_constate_la_penombre_devant_le_coffre_sans_essai_perdu(self):
        m = self.odon_vers_le_bureau()
        self.assertNotIn("bureau", lire(m, "odon")["croyances"])
        self.assertEqual(lumiere_crue(m, "odon", "bureau"), 2)
        for _ in range(3):
            m, _ = vivre(m, 1)
        # Arrivé devant le coffre, dans la lueur du baraquement : il n'essaie pas, et le sait.
        self.assertEqual(m.objets["odon"]["lieu"], "bureau")
        self.assertEqual(len(renoncements(m, "odon", "coffre_paie")), 1)
        self.assertEqual(essais(m, "odon", "coffre_paie"), [])
        self.assertEqual(lire(m, "odon")["croyances"]["coffre_paie"]["lumiere"]["valeur"], 1)
        # Il reprend sur la lumière qu'il a vue : son plan la porte, et devant, il essaie.
        etape = next(x for x in lire(m, "odon")["intention"]["plan"] if x["operation"] == "crocheter")
        self.assertEqual(etape["contenu"], {"lumiere": 1})
        m, _ = vivre(m, 1)
        self.assertEqual(len(essais(m, "odon", "coffre_paie")), 1)
        self.assertEqual(len(renoncements(m, "odon", "coffre_paie")), 1)

    def brune_au_refuge(self):
        """Relais : Brune, affamée, refusée par Gorm, ses crochets en main, au milieu du refuge
        éclairé par le fanal ; la réserve, au fond, n'est qu'en pénombre. Les autres sont aux vannes."""
        m = refusee(calme(relais(), "marchand", "ilse", "aubin"))
        lire(m, "brune")["besoins"]["faim"] = 85.0
        deplacer(m, "crochets", "brune")
        placer(m, "brune", "antichambre", (4, 1))
        for i, id in enumerate(("marchand", "ilse", "aubin")):
            placer(m, id, "crypte", (2 + i, 2))
        percevoir_tous(m)
        return recharger(m)

    def test_brune_constate_la_penombre_devant_la_reserve(self):
        # Autre cas de même nature : la salle crue éclairée, la serrure dans la pénombre.
        m = self.brune_au_refuge()
        self.assertEqual(lumiere_crue(m, "brune", "antichambre"), 2)
        self.assertEqual(planifier(m, "brune", "faim")[1][0]["contenu"], {"lumiere": 2})
        m, _ = vivre(m, 2)
        self.assertEqual(len(renoncements(m, "brune", "reserve")), 1)
        self.assertEqual(essais(m, "brune", "reserve"), [])
        self.assertEqual(lire(m, "brune")["croyances"]["reserve"]["lumiere"]["valeur"], 1)
        m, _ = vivre(m, 1)
        self.assertEqual(len(essais(m, "brune", "reserve")), 1)

    def test_dans_le_noir_elle_n_essaie_rien_et_va_chercher_de_la_lumiere(self):
        # La réserve aux vannes, que le brasero mort laisse noires ; Brune les croit éclairées (vues
        # autrefois) : devant la serrure, aucun jet ne réussirait. Elle n'essaie rien, et son plan
        # passe par la lumière.
        m = refusee(calme(relais(), "marchand", "ilse", "aubin"))
        lire(m, "brune")["besoins"]["faim"] = 85.0
        deplacer(m, "crochets", "brune")
        m.objets["reserve"].update(lieu="crypte", position_salle="crypte", position=[7, 4])
        m.objets["brasero"]["allume"] = False
        croire(m, "brune", "vivres", "lieu", "reserve", "savoir", salle="crypte", case=[7, 4])
        placer(m, "brune", "antichambre", (4, 1))
        placer(m, "marchand", "antichambre", (6, 5))
        # Placement d'auteur : Gorm laisse ses charges (sinon, la réserve déplacée, il en ressort aussitôt
        # ses vivres et rallume le brasero : la salle n'est plus noire quand Brune y arrive).
        m.objets["marchand"]["profil"]["pulsions"] = []
        lire(m, "marchand")["pulsions"] = []
        for i, id in enumerate(("ilse", "aubin")):
            placer(m, id, "beffroi", (2 + i, 3))
        percevoir_tous(m)
        croire(m, "brune", "crypte", "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "vu")
        m = recharger(m)
        for _ in range(6):
            m, _ = vivre(m, 1)
            if renoncements(m, "brune", "reserve"):
                break
        self.assertEqual(m.objets["brune"]["lieu"], "crypte")
        self.assertEqual(len(renoncements(m, "brune", "reserve")), 1)
        self.assertEqual(essais(m, "brune", "reserve"), [])
        self.assertEqual(lire(m, "brune")["croyances"]["reserve"]["lumiere"]["valeur"], 0)
        # Ce qu'elle a vu devant la serrure décide : plus de crochetage sans lumière en main.
        plan = (planifier(m, "brune", "faim") or (None, []))[1]
        if "crocheter" in [x["operation"] for x in plan]:
            avant = plan[:[x["operation"] for x in plan].index("crocheter")]
            self.assertIn("allumer", [x["operation"] for x in avant])


class PartPayeeTests(unittest.TestCase):
    """Une part payée d'avance dont la contrepartie n'est pas livrée à l'échéance est rendue, ou
    devient une dette que le payeur connaît et peut réclamer."""

    def ilse_achete(self):
        """Relais : Ilse, affamée, achète une part des vivres à Gorm, près de lui au refuge."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, "ilse")["besoins"]["faim"] = 80.0
        placer(m, "ilse", "antichambre", (1, 3))
        placer(m, "marchand", "antichambre", (2, 3))
        percevoir_tous(m)
        self.assertEqual(demander(m, "ilse", "marchand", "vivres", prix=2), "vendu")
        self.assertEqual((bourse(m, "ilse"), bourse(m, "marchand")), (6, 52))
        self.assertEqual(lire(m, "marchand")["engagements"][0]["paye"], {"objet": "vivres", "prix": 2, "quoi": "part"})
        return m

    def test_les_vivres_epuises_gorm_rend_les_pieces(self):
        # Cas réel (limite de ``echanges-argent``) : la part payée n'est jamais servie.
        m = self.ilse_achete()
        m.objets["vivres"]["portions"] = 0  # Placement d'auteur : quelqu'un a mangé la dernière part.
        m, _ = vivre(recharger(m), 1)
        self.assertEqual(lire(m, "marchand")["engagements"], [])
        self.assertEqual(m.data["dettes"], [])
        self.assertEqual((bourse(m, "ilse"), bourse(m, "marchand")), (8, 50))
        self.assertIn("Gorm rend 2 pièces à Ilse : la part des vivres du refuge n'a pas été servie.", chronique(m))
        types = [s["type"] for s in lire(m, "ilse")["memoire"]]
        self.assertIn("creance", types)
        self.assertIn("rembourse_par", types)

    def test_la_promesse_expiree_la_dette_est_reclamee(self):
        # Autre cas de même nature : la promesse échoit, Gorm est aux vannes. La dette est connue ;
        # Ilse va la réclamer, et Gorm la lui rend quand ils se retrouvent.
        m = self.ilse_achete()
        placer(m, "marchand", "crypte", (2, 2))
        percevoir_tous(m)
        croire(m, "ilse", "marchand", "lieu", "crypte", "savoir", salle="crypte", case=[2, 2])
        lire(m, "marchand")["engagements"][0]["minute"] = -ENGAGEMENT_MAX - 1
        lire(m, "ilse")["besoins"]["faim"] = 0.0
        m, _ = vivre(recharger(m), 1)
        self.assertEqual(m.data["dettes"], [{"de": "marchand", "a": "ilse", "montant": 2, "objet": "vivres",
                                             "quoi": "part", "minute": 1}])
        self.assertEqual((bourse(m, "ilse"), bourse(m, "marchand")), (6, 52))
        self.assertIn("creance", [s["type"] for s in lire(m, "ilse")["memoire"]])
        self.assertIn("dette", [s["type"] for s in lire(m, "marchand")["memoire"]])
        self.assertEqual(lire(m, "ilse")["intention"]["but"], {"type": "reclamer", "qui": "marchand"})
        for _ in range(6):
            m, _ = vivre(m, 1)
            if not m.data["dettes"]:
                break
        self.assertEqual(m.data["dettes"], [])
        self.assertEqual((bourse(m, "ilse"), bourse(m, "marchand")), (8, 50))

    def test_le_joueur_est_rembourse_et_le_lit(self):
        # Le même contrat pour le joueur : il a payé sa part ; les vivres manquent, Gorm le lui rend.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[1, 3])
        placer(m, "marchand", "antichambre", (2, 3))
        regarder(m, "marchand", "joueur")
        from donjon.corps import valeurs
        valeurs(m, "joueur")["faim"] = 80.0
        percevoir_tous(m)
        or_avant = m.joueur["or"]
        self.assertEqual(demander(m, "joueur", "marchand", "vivres", prix=2), "vendu")
        self.assertEqual(m.joueur["or"], or_avant - 2)
        m.objets["vivres"]["portions"] = 0
        m, lignes = vivre(recharger(m), 1)
        self.assertEqual(m.joueur["or"], or_avant)
        self.assertEqual(m.data["dettes"], [])
        self.assertIn("Gorm te rend 2 pièces : la part des vivres du refuge que tu avais payée ne t'a pas été "
                      "servie.", lignes)


class ForcerTests(unittest.TestCase):
    """Les PNJ forcent par la règle du joueur : outil qui fait choc ou qui coupe, FOR, bruit,
    faute au prix de l'honnêteté et de la douceur sur le bien d'autrui."""

    def brune_aux_vannes(self, douceur=None):
        """Relais : Brune, affamée, refusée par Gorm, sans crochets (le joueur les a), le pied-de-biche
        en main, se tient aux vannes, devant la porte étanche du beffroi verrouillée."""
        m = refusee(calme(relais(), "marchand", "ilse", "aubin"))
        lire(m, "brune")["besoins"]["faim"] = 85.0
        deplacer(m, "crochets", "joueur")
        croire(m, "brune", "crochets", "lieu", "joueur", "vu", salle=None, case=None)
        deplacer(m, "pied_de_biche", "brune")
        placer(m, "brune", "crypte", (6, 3))
        if douceur is not None:
            m.objets["brune"]["profil"]["valeurs"]["douceur"] = douceur
        return m

    def test_brune_force_la_porte_du_beffroi_qui_n_est_a_personne(self):
        # Les vivres sont derrière la porte étanche ; la porte n'est à personne : la forcer ne lèse
        # personne, même à qui a la douceur entière.
        m = self.brune_aux_vannes()
        deplacer(m, "vivres", "beffroi", position=[4, 3])
        croire(m, "brune", "vivres", "lieu", "beffroi", "savoir", salle="beffroi", case=[4, 3])
        croire(m, "brune", "porte", "verrouillee", True, "savoir")
        percevoir_tous(m)
        m = recharger(m)
        etapes = planifier(m, "brune", "faim")[1]
        self.assertEqual([(x["operation"], x["cible"] or x["lieu"]) for x in etapes],
                         [("frapper", "porte"), ("aller", "beffroi"), ("manger", "vivres")])
        self.assertEqual(etapes[0]["outil"], "pied_de_biche")
        for _ in range(20):
            m, _ = vivre(m, 1)
            if m.objets["brune"]["lieu"] == "beffroi":
                break
        porte = m.objets["porte"]
        self.assertEqual((porte["integrite"], porte["ouverte"], porte["verrouillee"]), (0, True, False))
        self.assertIn("Brune, batelière évacuée force la porte étanche du beffroi.", chronique(m))
        self.assertFalse(lire(m, "brune")["croyances"]["porte"]["verrouillee"]["valeur"])
        # Chaque coup s'entend : Gorm, au refuge, a entendu un bruit venu des vannes.
        self.assertTrue(any(c["texte"].startswith("Gorm entend un bruit") for c in de(m, "marchand")))
        m, _ = vivre(m, 2)
        self.assertLess(lire(m, "brune")["besoins"]["faim"], 85.0)

    def test_moins_douce_elle_force_la_reserve_de_gorm(self):
        # Autre cas de même nature : la réserve de Gorm. À la douceur entière, l'abîmer est exclu ;
        # à 60, c'est une faute qu'elle pèse, et la serrure cède sous les coups.
        m = self.brune_aux_vannes()
        placer(m, "brune", "antichambre", (6, 3))
        percevoir_tous(m)
        self.assertNotIn("frapper", [x["operation"] for x in (planifier(m, "brune", "faim") or (None, []))[1]])
        m = self.brune_aux_vannes(douceur=60)
        placer(m, "brune", "antichambre", (6, 3))
        for i, id in enumerate(("marchand", "ilse", "aubin")):
            placer(m, id, "beffroi", (2 + i, 3))
        percevoir_tous(m)
        m = recharger(m)
        self.assertEqual(planifier(m, "brune", "faim")[1][0]["operation"], "frapper")
        for _ in range(25):
            m, _ = vivre(m, 1)
            if m.objets["reserve"]["integrite"] == 0:
                break
        reserve = m.objets["reserve"]
        self.assertEqual((reserve["integrite"], reserve["ouverte"], reserve["verrouillee"]), (0, True, False))
        # Brisée, elle laisse tomber ce qu'elle tenait.
        self.assertEqual(m.objets["vivres"]["lieu"], "antichambre")

    def test_un_temoin_voit_forcer(self):
        # Ilse, tout près, la voit frapper la réserve : elle ne lui fait plus confiance.
        m = self.brune_aux_vannes(douceur=60)
        placer(m, "brune", "antichambre", (6, 3))
        placer(m, "marchand", "beffroi", (2, 3))
        placer(m, "aubin", "beffroi", (3, 3))
        placer(m, "ilse", "antichambre", (6, 5))
        regarder(m, "ilse", "brune")
        percevoir_tous(m)
        lire(m, "brune")["besoins"]["faim"] = 96.0  # Au-delà du désespoir, la crainte d'être vue ne la retient plus.
        m = recharger(m)
        for _ in range(4):
            m, _ = vivre(m, 1)
        souvenirs = [s for s in lire(m, "ilse")["memoire"] if s["type"] == "vu_agir" and s["auteur"] == "brune"]
        self.assertTrue(souvenirs)
        self.assertEqual({s["operation"] for s in souvenirs} - {"briser"}, {"frapper"})
        self.assertFalse(lire(m, "ilse")["croyances"]["brune"]["fiable"]["valeur"])

    def test_la_regle_est_celle_du_joueur(self):
        # Le joueur frappe par la même règle : même DD, même bonus, mêmes dégâts.
        m = relais()
        deplacer(m, "pied_de_biche", "joueur")
        m.joueur.update(salle="crypte", position=[8, 3])
        moteur = Moteur(m)
        plan = moteur.preparer(proposition("frapper", "porte", "pied_de_biche"))
        t = m.objets["pied_de_biche"]
        self.assertEqual((plan.stat, plan.dd, plan.bonus), ("FOR", force.DD, force.bonus(t)))
        self.assertEqual(plan.effets, [("endommager", "porte", force.degats(m, "joueur", t))])


class BoisDeGormTests(unittest.TestCase):
    """Gorm va chercher son propre bois aux vannes plutôt que de demander les planches d'Aubin."""

    def gorm_devant_le_brasero(self):
        """Relais : le brasero baisse ; Gorm, près de lui dans la conduite, est passé aux vannes (en
        pénombre : la lueur du brasero les baigne), où sont ses fagots ; Aubin et ses planches sont
        au refuge. Ses biens ne le pressent pas."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        placer(m, "marchand", "crypte", (4, 1))
        percevoir_tous(m)
        placer(m, "marchand", "echoppe", (3, 3))
        m.objets["brasero"]["combustible"] = 30
        percevoir_tous(m)
        return recharger(m)

    def test_les_vannes_baignees_de_la_lueur_du_brasero_ne_sont_pas_noires(self):
        # La croyance en cause : vues de la case où il se tenait, les vannes n'avaient que la lueur
        # du brasero ; elle les baigne tout entières (``ambiance``), ce n'est pas un seuil.
        m = self.gorm_devant_le_brasero()
        self.assertEqual(lire(m, "marchand")["croyances"]["crypte"]["etat"]["valeur"],
                         {"eclairee": True, "niveau": 1, "propre": 1})
        self.assertEqual(lumiere_crue(m, "marchand", "crypte"), 1)
        self.assertFalse(noir_cru(m, "marchand", "crypte"))
        # Le cellier de l'auberge, porte fermée, sans lumière : il reste noir.
        a = creer("auberge", 1985, "fixe")
        placer(a, "mireille", "cellier", (2, 2))
        deplacer(a, "bougeoir_mireille", "cuisine", position=[1, 1])
        percevoir_tous(a)
        self.assertEqual(lire(a, "mireille")["croyances"]["cellier"]["etat"]["valeur"],
                         {"eclairee": False, "niveau": 0, "propre": 0})

    def test_gorm_va_chercher_ses_fagots(self):
        # Cas réel (Relais, graines 1985, 99 : minutes 106, 124) : Gorm demandait, puis achetait, une
        # part des planches d'Aubin au lieu d'aller aux vannes.
        m = self.gorm_devant_le_brasero()
        but, etapes = planifier_pulsion(m, "marchand", {"objet": "brasero", "allume": True})
        self.assertEqual([(x["operation"], x["cible"] or x["lieu"]) for x in etapes],
                         [("aller", "crypte"), ("prendre", "bois"), ("aller", "echoppe"), ("alimenter", "brasero")])
        for _ in range(6):
            m, _ = vivre(m, 1)
        self.assertGreater(m.objets["brasero"]["combustible"], 60)
        self.assertEqual(m.objets["bois"]["charges"], 1)
        self.assertEqual(m.objets["planches"]["charges"], 2)
        self.assertFalse(any("planches" in c["texte"] for c in de(m, "marchand")))

    def test_une_part_demandee_coute_selon_sa_chance_comme_un_objet(self):
        # La règle commune : une part demandée n'est pas acquise ; elle coûte 1 + DEMANDE / PRET,
        # comme un objet demandé à qui le porte.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        lire(m, "ilse")["besoins"]["faim"] = 80.0
        placer(m, "ilse", "antichambre", (1, 3))
        placer(m, "marchand", "antichambre", (2, 3))
        percevoir_tous(m)
        v = Vue(m, "ilse")
        demandes = [g for g in gestes(v, depart(m, "ilse", v)) if g[2] and g[2][0]["operation"] == "demander"]
        self.assertEqual([(g[2][0]["outil"], g[1]) for g in demandes], [("vivres", 1 + DEMANDE / PRET)])


if __name__ == "__main__":
    unittest.main()
