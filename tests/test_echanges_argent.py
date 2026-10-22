"""Prêter, confier la garde, l'argent : des permissions que le moteur connaît et une pièce qui vaut,
pour chacun, ce que lui en disent ses besoins et ses valeurs (``biens``, ``caractere``).

Chaque test vérifie l'état du monde après rechargement.
"""
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon.biens import a_autrui, reticence
from donjon.caractere import valeur_piece, valeur_pieces
from donjon.deliberation import illicite
from donjon.deplacement_objet import deplacer
from donjon.echanges import confier, demander
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.paroles import preparer_parole
from donjon.planification import enrichir, planifier
from tests.support import calme, refusee
from tests.test_lumiere import avec_briquet, inquiet, mine_noire
from tests.test_tensions import chronique, placer, recharger, relais, vivre


def memoires(m, id, sorte):
    return [s for s in lire(m, id)["memoire"] if s["type"] == sorte]


class PretTests(unittest.TestCase):
    def lampe_empruntee(self):
        """Mine noire : Rémy, qui craint le noir, n'a plus sa lampe ; Gaspard, près de lui, porte
        la sienne éteinte et la lui prête ; Rémy a un briquet."""
        m = avec_briquet(mine_noire())
        # Placement d'auteur : Rémy a laissé sa lampe à la réserve, fermée à clé.
        deplacer(m, "lampe_remy", "reserve", position=[2, 2])
        croire(m, "remy", "lampe_remy", "lieu", "reserve", "vu", salle="reserve", case=[2, 2])
        m.objets["lampe_gaspard"]["allume"] = False
        placer(m, "gaspard", m.objets["remy"]["lieu"], m.objets["remy"]["position"][:1]
               + [m.objets["remy"]["position"][1] + 1])
        percevoir_tous(m)
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "remy", "gaspard", "lampe_gaspard"), "remis")
        return recharger(inquiet(m))

    def test_la_lampe_pretee_s_allume_sans_faute_puis_revient_a_gaspard(self):
        m = self.lampe_empruntee()
        self.assertEqual(m.data["permissions"], [
            {"objet": "lampe_gaspard", "a": "remy", "de": "gaspard", "minute": m.data["minutes"]}])
        self.assertIn({"objet": "lampe_gaspard", "rendre": "gaspard"},
                      [x["condition"] for x in lire(m, "remy")["engagements"]])
        self.assertFalse(illicite(m, "remy", "lampe_gaspard", "allumer"))
        self.assertTrue(illicite(m, "odon", "lampe_gaspard", "allumer"))   # prêtée à Rémy, pas à Odon
        m, _ = vivre(m, 3)
        self.assertTrue(m.objets["lampe_gaspard"]["allume"])
        # Aucun geste illicite : Gaspard, qui le regarde, ne le prend pas pour un voleur.
        self.assertFalse([g for g in m.data.get("gestes_en_cours", []) if g["auteur"] == "remy"])
        self.assertFalse(any(s.get("auteur") == "remy" for s in lire(m, "gaspard")["memoire"]
                             if s["type"] in ("vu_agir", "vu_porter")))
        self.assertIsNot((lire(m, "gaspard")["croyances"].get("remy", {}).get("fiable") or {}).get("valeur"), False)
        # Le baraquement de nouveau éclairé, rassuré, la lampe ne lui sert plus : il la rend.
        m.objets["lampe_baraque"].update(allume=True, combustible=200)
        lire(m, "remy")["besoins"]["securite"] = 0.0
        percevoir_tous(m)
        m, _ = vivre(recharger(m), 6)
        self.assertEqual(m.objets["lampe_gaspard"]["lieu"], "gaspard")
        self.assertIn("Rémy rend la lampe de Gaspard à Gaspard (rendu).", chronique(m))
        self.assertEqual(m.data["permissions"], [])
        self.assertFalse([x for x in lire(m, "remy")["engagements"] if "rendre" in x["condition"]])
        self.assertTrue(illicite(m, "remy", "lampe_gaspard", "allumer"))

    def test_le_proprietaire_qui_la_redemande_la_recupere_sauf_si_elle_sert(self):
        m = self.lampe_empruntee()
        m, _ = vivre(m, 3)  # Il l'a allumée : dans le noir, elle lui sert.
        self.assertEqual(demander(m, "gaspard", "remy", "lampe_gaspard"), "necessaire")
        m.objets["lampe_baraque"].update(allume=True, combustible=200)
        percevoir_tous(m)
        lire(m, "remy")["intention"] = None
        self.assertEqual(demander(m, "gaspard", "remy", "lampe_gaspard"), "rendu")
        m = recharger(m)
        self.assertEqual((m.objets["lampe_gaspard"]["lieu"], m.data["permissions"]), ("gaspard", []))

    def test_le_joueur_emprunte_une_lampe_et_la_pose_sans_la_voler(self):
        m = calme(creer("mine", 1985, "fixe"), "gaspard")
        salle, (x, y) = m.joueur["salle"], m.joueur["position"]
        placer(m, "gaspard", salle, (x + 1, y))
        percevoir_tous(m)
        self.assertEqual(a_autrui(m, "lampe_gaspard"), "gaspard")
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "joueur", "gaspard", "lampe_gaspard"), "remis")
        m = recharger(m)
        self.assertEqual(m.objets["lampe_gaspard"]["lieu"], "joueur")
        self.assertIsNone(a_autrui(m, "lampe_gaspard"))
        self.assertEqual(a_autrui(m, "lampe_gaspard", operation="manger"), "gaspard")  # rien ne consomme
        # La poser n'est pas un vol : aucune méthode discrète n'est exigée, et rien n'est volé.
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(sequence(etape("deplacer", "lampe_gaspard", salle))))
        m = recharger(m)
        self.assertEqual(m.objets["lampe_gaspard"]["lieu"], salle)
        self.assertEqual(m.objets["lampe_gaspard"]["proprietaire"], "gaspard")
        self.assertNotIn("vole_par", m.objets["lampe_gaspard"])
        self.assertFalse(memoires(m, "gaspard", "vol_surpris"))
        # Rendue à son propriétaire (il la reprend), le prêt est clos.
        deplacer(m, "lampe_gaspard", "gaspard")
        self.assertEqual(recharger(m).data["permissions"], [])


class GardeTests(unittest.TestCase):
    def test_ilse_garde_la_reserve_sous_cle_avec_la_cle_de_gorm(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Placement d'auteur : Gorm a laissé la réserve ouverte et sa clé à côté, et descend aux vannes.
        m.objets["reserve"].update(ouverte=True, verrouillee=False)
        deplacer(m, "cle_reserve", "antichambre", position=[6, 3])
        placer(m, "marchand", "antichambre", (5, 3))
        placer(m, "ilse", "antichambre", (6, 4))
        percevoir_tous(m)
        # Sans la garde, prendre la clé de Gorm serait illicite, quelle que soit l'honnêteté d'Ilse.
        self.assertTrue(illicite(m, "ilse", "cle_reserve"))
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(confier(m, "marchand", "ilse", {"objet": "reserve", "verrouillee": True}), "accepte")
        self.assertFalse(illicite(m, "ilse", "cle_reserve"))
        self.assertFalse(illicite(m, "ilse", "reserve", "fermer"))
        self.assertTrue(illicite(m, "ilse", "vivres"))        # la garde ne livre pas le contenu
        placer(m, "marchand", "crypte", (2, 2))
        m, _ = vivre(recharger(m), 2)
        self.assertEqual(chronique(m).count("Ilse, meunière évacuée prend la clé de la réserve."), 1)
        self.assertIn("Ilse, meunière évacuée verrouille la réserve de vivres.", chronique(m))
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertFalse(m.objets["reserve"]["ouverte"])
        # Brune la regardait faire : elle n'a vu aucun geste illicite.
        self.assertFalse([s for s in memoires(m, "brune", "vu_agir") if s["auteur"] == "ilse"])
        # La tâche faite, la clé qu'elle porte encore lui reste prêtée : elle la rend à Gorm (dès qu'elle
        # a fini, à l'instant : ``deliberation-evenements`` ; c'est parfois déjà fait).
        if "Ilse rend la clé de la réserve à Gorm (rendu)." not in chronique(m):
            self.assertEqual([(p["objet"], p["a"], p["de"]) for p in m.data["permissions"]],
                             [("cle_reserve", "ilse", "marchand")])
            m, _ = vivre(m, 4)
        self.assertIn("Ilse rend la clé de la réserve à Gorm (rendu).", chronique(m))
        self.assertEqual((m.objets["cle_reserve"]["lieu"], m.data["permissions"]), ("marchand", []))
        self.assertTrue(illicite(m, "ilse", "cle_reserve"))


class AchatTests(unittest.TestCase):
    def brune_refusee(self, pieces, honnetete=50):
        """Gorm vient de lui refuser une part ; elle a ``pieces`` pièces et ses crochets ; une
        Brune plus scrupuleuse que celle du Relais (``honnetete``)."""
        m = refusee(calme(relais(), "marchand", "ilse", "aubin"))
        m.data["finances_pnj"]["brune"] = pieces
        m.objets["brune"]["profil"]["valeurs"]["honnetete"] = honnetete
        lire(m, "brune")["besoins"]["faim"] = 85.0
        placer(m, "marchand", "antichambre", (5, 3))
        placer(m, "brune", "antichambre", (6, 2))
        m.objets["crochets"]["lieu"] = "brune"
        m.objets["crochets"].pop("position", None)
        percevoir_tous(m)
        return recharger(m)

    def test_l_affamee_qui_a_de_quoi_payer_achete_au_lieu_de_forcer_la_reserve(self):
        # Sans le sou, elle forcerait la réserve en cachette.
        but, etapes = planifier(self.brune_refusee(0), "brune", "faim")
        self.assertIn("crocheter", [x["operation"] for x in etapes])
        # La Brune du Relais (honnêteté 20), qui doit son bac : ses pièces lui coûtent plus que la
        # faute, elle force la réserve même avec huit pièces. Aucune règle ne l'écrit.
        but, etapes = planifier(self.brune_refusee(8, honnetete=20), "brune", "faim")
        self.assertIn("crocheter", [x["operation"] for x in etapes])
        # Trois pièces, honnêteté 50 : la part (2) lui coûte moins que la faute.
        m = self.brune_refusee(3)
        but, etapes = planifier(m, "brune", "faim")
        self.assertEqual([x["operation"] for x in etapes], ["acheter"])
        m, _ = vivre(m, 6)
        self.assertIn("Brune achète une part des vivres du refuge à Gorm pour 2 pièces (vendu).", chronique(m))
        self.assertEqual((m.data["finances_pnj"]["brune"], m.data["finances_pnj"]["marchand"]), (1, 52))
        self.assertLess(lire(m, "brune")["besoins"]["faim"], 85.0)
        self.assertFalse([g for g in m.data.get("gestes_en_cours", []) if g["auteur"] == "brune"])
        self.assertFalse(any(s["type"] == "vu_agir" and s["auteur"] == "brune"
                             for id in ("marchand", "ilse", "aubin") for s in lire(m, id)["memoire"]))

    def test_le_vendeur_refuse_ce_qu_il_garde_et_a_qui_il_se_mefie(self):
        m = self.brune_refusee(3)
        m.objets["vivres"]["portions"] = 1       # sa réserve : il garde la dernière part
        self.assertEqual(demander(m, "brune", "marchand", "vivres", prix=2), "necessaire")
        m.objets["vivres"]["portions"] = 4
        croire(m, "marchand", "brune", "fiable", False, "vu")
        self.assertEqual(demander(m, "brune", "marchand", "vivres", prix=2), "mefiance")
        m = recharger(m)
        self.assertEqual((m.data["finances_pnj"]["brune"], m.objets["vivres"]["portions"]), (3, 4))

    def test_vendre_ou_donner_selon_ce_que_vaut_une_piece_pour_lui(self):
        m = creer("auberge", 1985, "fixe")
        # Anselme, marchand ambitieux dont le commerce réclame tout : une pièce lui est chère, il
        # rechigne à donner sans être payé ; Odile, qui en a davantage pour elle, beaucoup moins.
        self.assertGreater(valeur_piece(m, "anselme"), valeur_piece(m, "odile"))
        self.assertGreater(reticence(m, "anselme", 2), 0)
        self.assertLessEqual(reticence(m, "odile", 2), 0)
        self.assertEqual(reticence(m, "anselme", 2, offre=2), round((0 - 2) / 2))  # payé, rien ne manque


class ArgentTests(unittest.TestCase):
    def paie_a_portee(self, dette):
        """Mine : Odon est seul au bureau, devant le coffre de la paie, ses crochets en main ; il
        n'a pas faim. Seule sa dette change d'un cas à l'autre."""
        m = creer("mine", 1985, "fixe")
        calme(m, "bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy")
        p = m.objets["odon"]["profil"]
        p["valeurs"]["honnetete"] = 70
        p["situation"] = {"dette": dette} if dette else {}
        placer(m, "bram", "baraquement", (2, 2))
        placer(m, "odon", "bureau", (3, 2))
        percevoir_tous(m)
        return recharger(m)

    def test_la_paie_tente_l_endette_et_pas_l_autre(self):
        sans_dette, endette = self.paie_a_portee(0), self.paie_a_portee(40)
        self.assertGreater(valeur_pieces(endette, "odon", 200), valeur_pieces(sans_dette, "odon", 200))
        self.assertIsNone(enrichir(sans_dette, "odon"))
        but, etapes = enrichir(endette, "odon")
        self.assertEqual(but, {"type": "argent", "objet": "paie"})
        self.assertIn(("prendre", "paie"), [(x["operation"], x["cible"]) for x in etapes])
        # Seul au bureau, il prend la paie. (Placement d'auteur : le coffre n'est plus fermé à clé, et il
        # le sait ; crocheté, le fracas fait accourir Bram aussitôt, et Odon, vu, attendrait.)
        endette.objets["coffre_paie"]["verrouillee"] = False
        croire(endette, "odon", "coffre_paie", "verrouillee", False, "essai")
        m, _ = vivre(recharger(endette), 5, jet=20)
        self.assertIn("Odon, nouveau venu prend la bourse de la paie.", chronique(m))
        self.assertEqual(m.objets["paie"]["lieu"], "odon")
        self.assertEqual(m.objets["paie"]["proprietaire"], "bram")   # volée, pas donnée
        self.assertEqual(m.objets["paie"]["pieces"], 200)
        # Sans dette, mêmes moyens, même main sûre : il n'y touche pas.
        m, _ = vivre(sans_dette, 5, jet=20)
        self.assertFalse([t for t in chronique(m) if t.startswith("Odon") and "paie" in t])
        self.assertEqual(m.objets["paie"]["lieu"], "coffre_paie")


class JoueurPaieTests(unittest.TestCase):
    def devant_gorm(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="echoppe", position=[2, 1])
        placer(m, "marchand", "echoppe", (1, 1))
        m.objets["marchand"]["orientation"] = "est"
        percevoir_tous(m)
        return m

    def parole(self, valeur, sujet="vivres", type_="demande"):
        return {"personnage": "marchand", "replique": "Gorm, je te paie une part de tes vivres.",
                "contenu": [{"type": type_, "sujet": sujet, "attribut": "", "valeur": valeur}],
                "_intention": "Gorm, je te paie une part de tes vivres."}

    def test_le_joueur_paie_sa_part_et_gorm_la_sert(self):
        m = self.devant_gorm()
        with patch.object(Monde, "d20", return_value=1):
            travail, rapport = preparer_parole(m, self.parole("2"))
        self.assertIn("Gorm, gardien du relais prend tes 2 pièces", " ".join(rapport["faits"]))
        m = recharger(travail)
        self.assertEqual((m.joueur["or"], m.data["finances_pnj"]["marchand"]), (22, 52))
        self.assertIn({"objet": "vivres", "servir": "joueur"},
                      [x["condition"] for x in lire(m, "marchand")["engagements"]])
        self.assertEqual(memoires(m, "marchand", "vente")[-1]["a"], "joueur")

    def test_moins_que_le_prix_reste_une_demande_et_il_dit_son_prix(self):
        m = self.devant_gorm()
        with patch.object(Monde, "d20", return_value=1):
            travail, rapport = preparer_parole(m, self.parole("1"))
        self.assertIn("il en veut 2 pièces", " ".join(rapport["faits"]))
        m = recharger(travail)
        self.assertEqual((m.joueur["or"], m.data["finances_pnj"]["marchand"]), (24, 50))

    def test_offrir_plus_qu_il_n_a_est_refuse_au_mj(self):
        m = self.devant_gorm()
        with self.assertRaises(ErreurMonde) as refus:
            preparer_parole(m, self.parole("30"))
        self.assertIn("contenu[0].valeur", refus.exception.attendu)
        self.assertIn("de 0 à 24", refus.exception.attendu)
        self.assertEqual(m.joueur["or"], 24)


class VoixTests(unittest.TestCase):
    def test_une_voix_inconnue_qui_offre_de_payer_s_entend_d_abord_demander_qui_va_la(self):
        """Mine, baraquement noir : Mathe n'a jamais entendu Odon. Il offre trois pièces pour une part
        (le prix) : prudente, elle demande d'abord « Qui va là ? », et rien n'est payé ; nommé, il
        reste une voix d'étranger, mais le prix payé vaut : elle vend."""
        from tests.test_constater_rumeurs import ParlerALaVoixTests
        m = ParlerALaVoixTests().baraquement_noir()
        lire(m, "mathe")["voix"].remove("odon")
        lire(m, "mathe")["croyances"].pop("odon", None)
        lire(m, "mathe")["besoins"]["securite"] = 60.0
        m.data["finances_pnj"]["odon"] = 5
        self.assertEqual(demander(m, "odon", "mathe", "vivres", prix=3), "qui_va_la")
        self.assertEqual((m.data["finances_pnj"]["odon"], m.data["finances_pnj"]["mathe"]), (5, 10))
        from donjon.voix import se_nommer
        se_nommer(m, "mathe", "odon", "odon")
        self.assertEqual(demander(m, "odon", "mathe", "vivres", prix=3), "vendu")
        m = recharger(m)
        self.assertEqual((m.data["finances_pnj"]["odon"], m.data["finances_pnj"]["mathe"]), (2, 13))
        self.assertIn({"objet": "vivres", "servir": "odon"},
                      [x["condition"] for x in lire(m, "mathe")["engagements"]])


if __name__ == "__main__":
    unittest.main()
