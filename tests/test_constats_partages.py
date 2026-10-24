"""Les constats passent par la parole commune et survivent à la reprise de partie."""
import copy
import unittest
from unittest.mock import patch

from donjon import pnj, social
from donjon.deliberation import moyens_crus, retenir_refus, tient
from donjon.esprits import RECENT, constater, croire, lire, memoriser, percevoir
from donjon.monde import Monde
from donjon.spatial import position_cible
from donjon.temps import ecouler
from tests.support import calme, lier, regarder
from tests.test_social import placer, recharger, relais
from tests.test_temps_etat import plan


def scene():
    m = calme(relais(), "marchand", "ilse", "brune", "aubin")
    placer(m, "ilse", "antichambre", [2, 4])
    placer(m, "marchand", "antichambre", [3, 4])
    placer(m, "brune", "crypte", [4, 3])
    placer(m, "aubin", "crypte", [5, 3])
    m.joueur.update(salle="antichambre", position=[2, 3])
    regarder(m, "ilse", "marchand")
    regarder(m, "marchand", "ilse")
    regarder(m, "joueur", "ilse")
    lier(m, "ilse", "marchand", True)
    lier(m, "marchand", "ilse", True)
    # Les vivres sont à l'écart : Gorm ne voit pas lui-même la réserve épuisée.
    m.objets["vivres"].update(lieu="echoppe", position=[4, 3], position_salle="echoppe", portions=0)
    for id in ("ilse", "marchand"):
        croire(m, id, "vivres", "lieu", "echoppe", "savoir", salle="echoppe", case=[4, 3])
    m.data["connus"] = sorted(set(m.data["connus"]) | {"vivres", "porte", "reserve", "brasero"})
    m.data["visitees"] = sorted(set(m.data["visitees"]) | {"echoppe"})
    return m


def constater_echec(m, operation, objet):
    # Le geste réel apprend l'épuisement ou le verrou par l'essai.
    if objet == "vivres":
        placer(m, "ilse", "echoppe", [4, 4])
    else:
        salle = m.objets[objet].get("relie", [m.objets[objet]["lieu"]])[0]
        placer(m, "ilse", salle, position_cible(m, objet, salle))
    with patch.object(Monde, "d20", return_value=20):
        pnj._executer(m, "ilse", plan(operation, objet), [], [])
    placer(m, "ilse", "antichambre", [2, 4])
    regarder(m, "ilse", "marchand")
    return recharger(m)


class ConstatsPartagesTests(unittest.TestCase):
    def confier(self, m):
        lignes = []
        with patch.object(Monde, "d20", return_value=20):
            dit = social.bavarder(m, "ilse", lignes)
        return recharger(m), dit, "\n".join(lignes)

    def test_reserve_epuisee_dite_crue_et_visible_apres_recharge(self):
        m = constater_echec(scene(), "manger", "vivres")
        self.assertEqual(lire(m, "ilse")["croyances"]["vivres"]["etat"]["source"], "essai")
        m, dit, texte = self.confier(m)
        self.assertTrue(dit)
        self.assertIn("les vivres du refuge sont épuisés", texte)
        c = lire(m, "marchand")["croyances"]["vivres"]["etat"]
        self.assertEqual((c["valeur"], c["source"], c["confiance"]),
                         ({"disponible": False}, "dit:ilse", .7))
        s = {"operation": "demander", "objet": "vivres", "de": "ilse"}
        self.assertFalse(any(f[0] == "moyen" for f in moyens_crus(m, "marchand", s)))
        self.assertEqual(m.objets["vivres"]["portions"], 0)
        self.assertTrue(any(c.get("constat_confie") for c in m.data["chronique"]))
        self.assertTrue(any("les vivres du refuge sont épuisés" in c["texte"] for c in m.data["chronique"]))

    def test_verrou_constate_par_le_geste_dit_et_cru(self):
        m = scene()
        m.objets["porte"].update(ouverte=False, verrouillee=True)
        croire(m, "marchand", "porte", "verrouillee", False, "savoir")
        m = constater_echec(m, "ouvrir", "porte")
        m, dit, texte = self.confier(m)
        self.assertTrue(dit)
        self.assertIn("la porte étanche du beffroi est fermée à clé", texte)
        c = lire(m, "marchand")["croyances"]["porte"]["verrouillee"]
        self.assertEqual((c["valeur"], c["source"]), (True, "dit:ilse"))
        self.assertTrue(m.objets["porte"]["verrouillee"])

    def test_deja_su_pas_repete_meme_revu_et_memoire_evincee(self):
        m = constater_echec(scene(), "manger", "vivres")
        m, _, _ = self.confier(m)
        for _ in range(45):
            memoriser(m, "marchand", {"type": "parole", "texte": "Autre chose."})
        ecouler(m, 600)
        croire(m, "ilse", "vivres", "etat", {"disponible": False}, "essai")
        m, dit, texte = self.confier(recharger(m))
        self.assertFalse(dit)
        self.assertEqual(texte, "")
        self.assertEqual(sum(bool(c.get("constat_confie")) for c in m.data["chronique"]), 1)

    def test_constat_propre_posterieur_prime_sur_la_parole(self):
        m = constater_echec(scene(), "manger", "vivres")
        noyau = next(x[1] for x in social.nouvelles(m, "ilse") if x[1]["type"] == "constat")
        ecouler(m, 600)
        m.objets["vivres"]["portions"] = 3
        constater(m, "marchand", "vivres", "vu")
        m = recharger(m)
        avant = copy.deepcopy(lire(m, "marchand")["croyances"]["vivres"]["etat"])
        self.assertIsNone(social.recevoir(m, "marchand", "ilse", {"type": "rumeur", "evenement": noyau, "rang": 0}))
        m = recharger(m)
        self.assertEqual(lire(m, "marchand")["croyances"]["vivres"]["etat"], avant)
        self.assertTrue(lire(m, "marchand")["croyances"]["vivres"]["etat"]["valeur"]["disponible"])

    def test_constats_vus_et_relais_sans_verite_omnisciente(self):
        for objet, attribut, valeur, fragment in (
                ("brasero", "etat", {"allume": False}, "le brasero est éteint"),
                ("reserve", "etat", {"ouverte": True, "vide": True}, "la réserve de vivres est vide."),
                ("echoppe", "eau", 35, "l'eau atteint 35 cm dans la conduite basse")):
            with self.subTest(attribut=attribut, objet=objet):
                m = scene()
                if objet == "reserve":
                    m.objets[objet]["ouverte"] = True
                    constater(m, "ilse", objet, "vu")
                    self.assertTrue(lire(m, "ilse")["croyances"][objet]["etat"]["valeur"]["vide"])
                else:
                    croire(m, "ilse", objet, attribut, valeur, "vu")
                m, dit, texte = self.confier(recharger(m))
                self.assertTrue(dit)
                self.assertIn(fragment, texte)
                self.assertEqual(lire(m, "marchand")["croyances"][objet][attribut]["source"], "dit:ilse")
                self.assertTrue(any(n[1]["type"] == "constat" for n in social.nouvelles(m, "marchand")))

    def test_eau_dite_plus_tard_garde_la_date_et_la_vitesse_observees(self):
        from donjon.eau import estimation
        m = scene()
        croire(m, "ilse", "echoppe", "eau", 35, "vu", niveau=55, montee=12, repere=[0, 55])
        ecouler(m, 10 * 600)
        m, dit, texte = self.confier(recharger(m))
        self.assertTrue(dit)
        self.assertIn("35 cm", texte)
        self.assertEqual(estimation(m, "marchand"), (0, 55, 12))

    def test_recent_et_accusation_prioritaire(self):
        m = constater_echec(scene(), "manger", "vivres")
        lier(m, "ilse", "brune", False, "vu")
        memoriser(m, "ilse", {"type": "vol_surpris", "auteur": "brune", "objet": "vivres"})
        m, dit, texte = self.confier(m)
        self.assertTrue(dit)
        self.assertIn("a tenté de dérober", texte)
        self.assertNotIn("épuisés", texte)
        ecouler(m, (RECENT + 1) * 600)
        self.assertFalse(any(n[1]["type"] == "constat" for n in social.nouvelles(m, "ilse")))

    def test_pas_de_confidence_sans_confiance(self):
        m = constater_echec(scene(), "manger", "vivres")
        lier(m, "ilse", "marchand", False)
        m, dit, texte = self.confier(m)
        self.assertFalse(dit)
        self.assertEqual(texte, "")

    def test_relais_puis_vue_ne_repetent_pas_un_constat_deja_confie(self):
        m = constater_echec(scene(), "manger", "vivres")
        noyau = next(x[1] for x in social.nouvelles(m, "ilse") if x[1]["type"] == "constat")
        # Ilse a d'abord reçu la même nouvelle d'Aubin. La parole et sa propre
        # observation ne sont pas deux raisons de redire le même fait à Gorm.
        memoriser(m, "ilse", {"type": "rumeur", "evenement": noyau, "rang": 1, "de": "aubin"})
        m, dit, _ = self.confier(recharger(m))
        self.assertTrue(dit)
        self.assertEqual(lire(m, "marchand")["croyances"]["vivres"]["etat"]["confiance"], .7)
        ecouler(m, 600)
        lire(m, "marchand")["croyances"].pop("vivres")  # Même s'il a oublié ou douté.
        m, dit, _ = self.confier(m)
        self.assertFalse(dit)

    def test_refus_retenu_ne_se_leve_pas_quand_on_perd_un_moyen(self):
        m = scene()
        retenir_refus(m, "marchand", "ilse", "demander", "rien", objet="vivres")
        s = lire(m, "marchand")["refus"][-1]
        m = constater_echec(m, "manger", "vivres")
        m, _, _ = self.confier(m)
        self.assertTrue(tient(m, "marchand", s))

    def test_source_portee_quittant_sa_case_ne_devient_pas_un_constat_d_extinction(self):
        m = scene()
        m.objets["torche"].update(lieu="marchand", allume=True)
        croire(m, "ilse", "torche", "lieu", "marchand", "vu", salle="antichambre", case=[3, 4])
        croire(m, "ilse", "torche", "etat", {"allume": True}, "vu")
        placer(m, "marchand", "antichambre", [1, 1])
        regarder(m, "ilse", (3, 4))
        percevoir(m, "ilse")
        m = recharger(m)
        self.assertTrue(lire(m, "ilse")["croyances"]["torche"]["etat"]["valeur"]["allume"])
        self.assertTrue(m.objets["torche"]["allume"])
        self.assertFalse(any(n[1].get("objet") == "torche" for n in social.nouvelles(m, "ilse")))

    def test_meme_laps_decoupe_meme_monde_et_nouvelle_entendue(self):
        initial = constater_echec(scene(), "manger", "vivres")
        initial.objets["brasero"]["allume"] = False
        croire(initial, "ilse", "brasero", "etat", {"allume": False}, "essai")
        lire(initial, "marchand")["libre"] = 10000  # Il écoute sans entreprendre de rallumer le feu.
        resultats = []
        for tranches in ((1200,), (150,) * 8):
            m, lignes = recharger(initial), []
            with patch.object(Monde, "d20", return_value=20):
                for dt in tranches:
                    minutes = ecouler(m, dt)
                    pnj.avancer(m, minutes, lignes, dt)
                    m = recharger(m)
            self.assertTrue(any("les vivres du refuge sont épuisés" in l for l in lignes))
            self.assertEqual(lire(m, "marchand")["croyances"]["vivres"]["etat"]["source"], "dit:ilse")
            dits = [c["instant"] for c in m.data["chronique"]
                    if c["pnj"] == "ilse" and c.get("constat_confie")]
            self.assertGreaterEqual(len(dits), 2)
            self.assertEqual(len(dits), len({t // 600 for t in dits}), dits)
            resultats.append(m.data)
        self.assertEqual(*resultats)
