"""L'avis est une prévision, jamais une observation d'eau fabriquée."""
import copy
import unittest

from donjon import eau, pnj, social, planification, route_admissible
from donjon.crue import nouvelle_crue
from donjon.esprits import croire, lire, poids_source, prevision
from donjon.rendu import regarder as rendu
from donjon.spatial import installer
from donjon.temps import ecouler
from tests.support import calme, regarder
from tests.test_social import placer, recharger


def relation(m, qui, autre, **axes):
    from donjon.relations import _nouvelle
    lire(m, qui)["relations"][autre] = _nouvelle(axes, m.data["minutes"])


def scene():
    m = nouvelle_crue(500, depart="fixe")
    installer(m)
    calme(m, "aubin", "ilse", "marchand", "brune")
    lire(m, "ilse")["besoins"]["securite"] = 65
    # Crue 500 inchangée : deux vrais repères aux vannes avant que la conduite
    # soit noyée. Le passage est ouvert pour isoler l'avis de la recherche de clé.
    ecouler(m, 140 * 600)
    eau.observer(m, "aubin", "crypte")
    m.objets["porte"].update(ouverte=True, verrouillee=False)
    ecouler(m, 15 * 600)
    eau.observer(m, "aubin", "crypte")
    for qui, case in (("aubin", [2, 4]), ("ilse", [3, 4]), ("marchand", [3, 5])):
        placer(m, qui, "antichambre", case)
    placer(m, "brune", "echoppe", [1, 1])
    m.joueur.update(salle="antichambre", position=[2, 3])
    m.data["connus"] = sorted(m.objets)
    m.data["visitees"] = sorted(m.data["salles"])
    m.data["noms_connus"] = ["aubin", "ilse", "marchand", "brune"]
    for qui in ("ilse", "marchand"):
        regarder(m, "aubin", qui)
        croire(m, "aubin", qui, "lieu", "antichambre", "vu", salle="antichambre", case=m.objets[qui]["position"])
        relation(m, "aubin", qui, affection=0, confiance=0)
    relation(m, "ilse", "aubin", confiance=100, affection=80)
    relation(m, "marchand", "aubin", confiance=0, affection=0)
    croire(m, "ilse", "chambre_cloche", "etat", {"eclairee": True, "niveau": 1, "propre": 1}, "savoir")
    return recharger(m)


def confier(m, qui="aubin"):
    lignes = []
    dit = social.bavarder(m, qui, lignes)
    return recharger(m), dit, "\n".join(lignes)


class AvisMenaceTests(unittest.TestCase):
    def test_parole_entendue_restituee_depuis_la_sauvegarde(self):
        from donjon import ecoute
        m = scene()
        m.joueur["orientation"] = "nord"  # Aubin parle dans son dos.
        m.data["voix_connues"] = ["aubin"]
        m, dit, _ = confier(m)
        self.assertTrue(dit)
        sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
        texte = "\n".join(ecoute.rendre(m, sons))
        self.assertIn("l'eau menace le refuge du relais dans l'heure", texte.lower())
        self.assertEqual(prevision(m, "ilse", "antichambre")["source"], "dit:aubin")
        self.assertEqual(texte, "\n".join(ecoute.rendre(recharger(m), sons)))

    def test_aubin_previent_ilse_et_gorm_ilse_croit_et_monte(self):
        m = scene()
        mesures = copy.deepcopy(lire(m, "ilse")["croyances"])
        m, dit, texte = confier(m)
        self.assertTrue(dit)
        self.assertIn("l'eau menace le refuge du relais dans l'heure", texte.lower())
        self.assertEqual(prevision(m, "ilse", "antichambre")["source"], "dit:aubin")
        self.assertGreater(eau.attendue(m, "ilse", "antichambre"), 0)
        for sujet, attributs in mesures.items():
            self.assertEqual(lire(m, "ilse")["croyances"][sujet].get("eau"), attributs.get("eau"))
        ecouler(m, 600)
        m, dit, texte = confier(m)
        self.assertTrue(dit)
        self.assertIn("Gorm", texte)
        self.assertIsNone(prevision(m, "marchand", "antichambre"))
        self.assertFalse(eau.en_peril(m, "ilse"))  # Menacé ne veut pas encore dire noyé.
        # Les autres écoutent sans entreprendre une nouvelle tâche pendant ce parcours.
        for qui in ("aubin", "marchand", "brune"):
            lire(m, qui)["libre"] = 100000
        lignes = []
        dt = 6000
        pnj.avancer(m, ecouler(m, dt), lignes, dt)
        m = recharger(m)
        self.assertEqual(m.objets["ilse"]["lieu"], "chambre_cloche")
        self.assertTrue(any("Galerie de ronde" in c["texte"] for c in m.data["chronique"] if c["pnj"] == "ilse"))
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_pas_de_souci_pas_de_parole_et_pas_de_lecture_du_plan_prive(self):
        m = scene()
        m.objets["aubin"]["profil"]["valeurs"].update(altruisme=0, empathie=0)
        m, dit, texte = confier(m)
        self.assertNotIn("menace", texte)
        self.assertFalse(any(c.get("avis_exprime") for c in m.data.get("chronique", [])))
        # Une localisation inconnue n'est pas remplacée par la position vraie.
        m = scene()
        for qui in ("ilse", "marchand"):
            croire(m, "aubin", qui, "lieu", None, "vu", salle=None, case=None)
        m, _, texte = confier(m)
        self.assertNotIn("menace", texte)

    def test_destination_convenue_et_autre_lieu_meme_regle(self):
        m = scene()
        croire(m, "aubin", "ilse", "lieu", "chambre_cloche", "vu", salle="chambre_cloche", case=[1, 1])
        croire(m, "aubin", "marchand", "lieu", None, "vu", salle=None, case=None)
        t = m.data["minutes"]
        lire(m, "aubin")["rejoint"] = {"qui": "ilse", "depuis": t, "jusqu_a": t + 15, "vient": True}
        m, dit, texte = confier(m)
        self.assertTrue(dit)
        self.assertIn("menace", texte)
        # Autre locuteur, autre auditeur et autre altitude : même pipeline de parole.
        m = scene()
        for qui in ("aubin", "ilse"):
            placer(m, qui, "beffroi", [2, 2] if qui == "aubin" else [3, 2])
        placer(m, "marchand", "chambre_cloche", [1, 1])
        m.joueur.update(salle="beffroi", position=[2, 3])
        regarder(m, "joueur", "ilse")
        regarder(m, "ilse", "aubin")
        croire(m, "ilse", "crypte", "eau", 60, "essai", niveau=-40, repere=[t, -40], montee=120)
        croire(m, "ilse", "aubin", "lieu", "beffroi", "vu", salle="beffroi", case=[2, 2])
        for a in lire(m, "aubin")["croyances"].values():
            a.pop("eau", None)
        relation(m, "aubin", "ilse", confiance=100, affection=0)
        m, dit, texte = confier(m, "ilse")
        self.assertTrue(dit)
        self.assertIn("palier des vannes", texte.lower())
        self.assertEqual(prevision(m, "aubin", "beffroi")["source"], "dit:ilse")
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_avis_une_fois_meme_apres_oubli_et_nouveaux_reperes(self):
        m = scene()
        for _ in range(2):
            m, _, _ = confier(m)
            ecouler(m, 600)
        for qui in ("aubin", "ilse", "marchand"):
            lire(m, qui)["memoire"].clear()
        eau.observer(m, "aubin", "crypte")
        m, _, texte = confier(m)
        self.assertNotIn("menace", texte)
        self.assertEqual(sum(bool(c.get("avis_exprime")) for c in m.data["chronique"]), 2)

    def test_sources_conviction_et_constat_propre_plus_recent(self):
        m = scene()
        noyau = next(n[1] for n in social.nouvelles(m, "aubin") if n[1]["type"] == "avis" and n[1]["objet"] == "antichambre")
        relation(m, "marchand", "aubin", confiance=100, affection=0)
        t = m.data["minutes"]
        croire(m, "marchand", "crypte", "eau", 80, "vu", niveau=-20, repere=[t, -20], montee=0)
        avant = copy.deepcopy(lire(m, "marchand")["croyances"])
        self.assertEqual(social.recevoir(m, "marchand", "aubin", {"type": "rumeur", "evenement": noyau, "rang": 0}), "doute")
        self.assertEqual(avant, lire(recharger(m), "marchand")["croyances"])
        m, _, _ = confier(m)
        relation(m, "ilse", "aubin", confiance=100, affection=0)
        croire(m, "ilse", "crypte", "eau", 80, "vu", .7, niveau=-20,
               repere=[t - 1, -20], montee=0, minute=t - 1)
        self.assertEqual(prevision(m, "ilse", "antichambre")["source"], "dit:aubin")
        ecouler(m, 600)
        croire(m, "ilse", "crypte", "eau", 80, "vu", .1, niveau=-20, repere=[t, -20], montee=0)
        m = recharger(m)
        self.assertEqual(prevision(m, "ilse", "antichambre")["source"], "vu")
        self.assertEqual(eau.attendue(m, "ilse", "antichambre"), 0)
        self.assertEqual(lire(m, "ilse")["croyances"]["crypte"]["eau"]["repere"][0], t)
        croire(m, "ilse", "crypte", "eau", 0, "vu", niveau=None, repere=None, montee=None)
        self.assertIsNone(prevision(recharger(m), "ilse", "antichambre"))
        relation(m, "ilse", "aubin", confiance=80, affection=50)
        self.assertAlmostEqual(poids_source(m, "ilse", {"source": "dit:aubin"}), .7)
        for source, poids in (("vu", 1), ("essai", 1), ("entendu", .8), ("devine", .4)):
            self.assertEqual(poids_source(m, "ilse", {"source": source}), poids)

    def test_prevision_dans_les_entrees_et_la_route_sans_alterer_les_mesures(self):
        m = scene()
        avant = planification._entrees(planification.Vue(m, "ilse"), {}, 8, 4000)
        mesures = copy.deepcopy(lire(m, "ilse")["croyances"])
        m, _, _ = confier(m)
        v = planification.Vue(m, "ilse")
        self.assertNotEqual(avant, planification._entrees(v, {}, 8, 4000))
        self.assertEqual(route_admissible.attendue(v, "antichambre", 60), eau.attendue(m, "ilse", "antichambre", 60))
        self.assertEqual(eau.estimation(m, "ilse"), None)
        for s, a in mesures.items():
            self.assertEqual(a.get("eau"), lire(m, "ilse")["croyances"][s].get("eau"))

    def test_meme_laps_decoupe_monde_et_parole_identiques_apres_reprise(self):
        initial = scene()
        for qui in ("marchand", "brune"):
            lire(initial, qui)["libre"] = 100000
        resultats = []
        for tranches in ((6000,), (150,) * 40):
            m, lignes = recharger(initial), []
            for dt in tranches:
                pnj.avancer(m, ecouler(m, dt), lignes, dt)
                m = recharger(m)
            self.assertTrue(any("menace" in t for t in lignes))
            self.assertEqual(m.objets["ilse"]["lieu"], "chambre_cloche")
            # Les résumés visuels transitoires sont rendus par tranche ; les avis,
            # la chronique et le rendu de la scène après recharge doivent être identiques.
            resultats.append((m.data, sorted(t for t in lignes if "menace" in t), rendu(m)))
        self.assertEqual(*resultats)
