"""3c : état, perception publique et reprise des mêmes scènes sociales."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import relations, signes, spatial
from donjon.banc_pnj import appliquer_reglages, creer
from donjon.commandes import analyser
from donjon.esprits import croire, lire, memoriser, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj import _etape, agir
from donjon.rendu import regarder as rendu
from donjon.scene import scene_percue
from tests.support import calme, presentes, regarder
from tests.test_social import placer, recharger


def intention(m, id, operation, cible="", outil="", condition="", attente=0):
    lire(m, id)["intention"] = {
        "but": {"type": "abri", "lieu": m.objets[id]["lieu"]}, "motif": "securite",
        "plan": [_etape(operation, cible, outil, m.objets[id]["lieu"], condition)],
        "depuis": m.data["minutes"], "attente": attente}


def scene():
    m = calme(creer("relais", 7, "fixe"), "ilse", "brune", "marchand", "aubin")
    presentes(m)
    placer(m, "ilse", "antichambre", [3, 5])
    placer(m, "brune", "antichambre", [4, 5])
    placer(m, "marchand", "crypte", [4, 3])
    placer(m, "aubin", "crypte", [3, 3])
    m.joueur.update(salle="antichambre", position=[2, 6], orientation="nord-est")
    for id in ("ilse", "brune"):
        lire(m, id)["relations"].clear()
    regarder(m, "ilse", "brune")
    regarder(m, "brune", "ilse")
    percevoir_tous(m)
    return m


def ecarter(m, id="ilse", autre="brune"):
    lire(m, id)["relations"][autre] = relations._nouvelle({"peur": 70}, m.data["minutes"])
    lire(m, id)["besoins"]["securite"] = 75
    intention(m, id, "abriter")
    agir(m, id, m.data["minutes"] * 600, [])
    return m


class SignesTests(unittest.TestCase):
    def test_perdre_un_signe_ne_prouve_pas_un_changement_attitude(self):
        m = ecarter(scene())
        signes.bilan_signes(m)
        avant = copy.deepcopy(lire(m, "ilse")["intention"])
        # La perception change sans décision du personnage.
        with patch("donjon.signes.publics", return_value=[]):
            lignes = signes.bilan_signes(m)
        self.assertTrue(any("ne distingues plus" in l for l in lignes))
        self.assertFalse(any("attitude" in l for l in lignes))
        self.assertEqual(lire(m, "ilse")["intention"], avant)
        m = recharger(m)
        self.assertTrue(signes.publics(m))

    def test_detourner_le_regard_consomme_la_rotation_commune(self):
        m = scene()
        intention(m, "ilse", "abriter")
        i = lire(m, "ilse")["intention"]
        m.objets["ilse"]["orientation"] = "est"
        duree = signes.regarder(m, "ilse", i, "brune", "convoite", "guet", detourner=True)
        self.assertEqual(duree, spatial.QUART * spatial.quarts("est", "ouest"))
        m = recharger(m)
        self.assertEqual(m.objets["ilse"]["orientation"], "ouest")
        self.assertNotIn("regard", lire(m, "ilse")["intention"].get("attitude", {}))

    def test_place_reelle_rendu_carte_observer_et_reprise(self):
        for id, autre in (("ilse", "brune"), ("brune", "ilse")):
            with self.subTest(id=id):
                m = ecarter(scene(), id, autre)
                self.assertGreaterEqual(spatial.distance(m.objets[id]["position"], m.objets[autre]["position"]), 2)
                m = recharger(m)
                from donjon.francais import de
                phrase = m.objets[id]["nom"].split(",")[0] + " se tient à l'écart " + de(m.objets[autre]["nom"].split(",")[0]) + "."
                self.assertIn(phrase, rendu(m))
                self.assertIn(phrase, [s["texte"] for s in signes.publics(m)])
                carte = scene_percue(m)
                o = next(o for n in carte["niveaux"] for o in n["objets"] if o["id"] == id)
                self.assertIn(phrase, [s["texte"] for s in o["signes"]])
                with patch("donjon.signes._jet", return_value=20):
                    texte = Moteur(m).executer(Moteur(m).preparer(analyser(m, "observer " + id)))
                m = recharger(m)
                self.assertIn("semble", texte)
                self.assertTrue(m.data["lectures"])
                self.assertTrue(signes.impressions(m))

    def test_noir_dos_ligne_de_vue_et_cible_cachee(self):
        m = ecarter(scene())
        self.assertTrue(signes.publics(m))
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        for s in m.data["salles"].values():
            s["fenetres"] = 0
        m = recharger(m)
        self.assertEqual(signes.publics(m), [])
        self.assertEqual(signes.impressions(m), [])
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(proposition("observer", "ilse"))
        self.assertTrue(refus.exception.attendu)
        m = ecarter(scene())
        m.joueur["orientation"] = "sud"
        self.assertEqual(signes.publics(recharger(m)), [])
        m = ecarter(scene())
        placer(m, "brune", "crypte", [5, 3])
        self.assertFalse(any(s["envers"] == "brune" for s in signes.publics(recharger(m))))

    def test_guet_lu_a_psy_14_manque_a_8_et_autre_guetteur(self):
        for guetteur, lecteur, scenario, salle, cible, p, q in (
                ("brune", "marchand", "relais", "antichambre", "reserve", [7, 3], [6, 4]),
                ("lucien", "hugues", "auberge", "chambre_chaude", "coffre_marchand", [1, 3], [2, 3])):
            m = scene() if scenario == "relais" else creer("auberge", 7, "fixe")
            m.data["salles"][salle]["lumiere_naturelle"] = 2
            placer(m, lecteur, salle, q)
            placer(m, guetteur, salle, p)
            regarder(m, lecteur, cible)
            outil = next(k for k, o in m.objets.items() if "crochetage" in o.get("usages", []))
            intention(m, guetteur, "crocheter", cible, outil, "sans_temoin", attente=600)
            lire(m, guetteur)["patience"] = 0
            # Le regard et l'attente sont ceux d'un véritable plan en cours, pas une émotion inventée.
            m = recharger(m)
            vus = [s for s in signes.percus(m, lecteur) if s["signe"] == "attend"]
            self.assertTrue(vus)
            m.objets[guetteur]["profil"]["caracteristiques"]["VOL"] = 10
            # Même signe et même dé ; +2 PSY réussit à DD15, -1 échoue.
            for psy, attendu in ((14, True), (8, False)):
                n = m.copier()
                n.objets[lecteur]["profil"]["caracteristiques"]["PSY"] = psy
                with patch("donjon.signes._jet", return_value=13):
                    signes.lire(n, lecteur, vus)
                n = recharger(n)
                self.assertEqual(bool(signes.intentions_lues(n, lecteur)), attendu)
                self.assertIn("semble guetter" if attendu else "Sorties", rendu(n) if not attendu else
                              __import__("donjon.social", fromlist=["phrase"]).phrase(n,
                                  next(s for s in lire(n, lecteur)["memoire"] if s["type"] == "intention_lue")))

    def test_guet_reel_relais7_puis_moteur_et_rechargement(self):
        # Capture sans déplacement ni retouche des profils de la nuit actuelle.
        # Le guet historique de la minute 122 s'est déplacé avec les étapes précédentes.
        source = Path(__file__).parent / "data/scenes/guet_relais7.json.gz"
        depart = Monde(json.loads(gzip.decompress(source.read_bytes())))
        self.assertEqual(depart.data["minutes"], 441)
        for psy, attendu in ((14, True), (8, False)):
            with self.subTest(psy=psy):
                m = depart.copier()
                m.objets["marchand"]["profil"]["caracteristiques"]["PSY"] = psy
                m = recharger(m)
                self.assertTrue(any(s["personnage"] == "brune" and s["signe"] == "attend"
                                    for s in signes.percus(m, "marchand")))
                # Même dé contrôlé pour isoler l'effet de PSY sur le cas réel.
                with patch("donjon.signes._jet", return_value=17):
                    signes.lire(m, "marchand")
                    Moteur(m).executer(Moteur(m).preparer(proposition("attendre", "0.1")))
                m = recharger(m)
                self.assertEqual(any(x == "brune" for x, _ in signes.intentions_lues(m, "marchand")), attendu)
                self.assertFalse(any(s["personnage"] == "brune" for s in m.contexte()["signes_percus"]))
                self.assertNotIn("Brune guette", rendu(m))

    def test_meprise_meme_rendu_et_persistance_pas_de_relance(self):
        m = ecarter(scene())
        # Même en observant exprès, cette PSY manque au-delà de la bande rien élargie.
        m.joueur["stats"]["PSY"] = 8
        s = next(s for s in signes.percus(m) if s["signe"] == "ecart")
        with patch("donjon.signes._jet", return_value=1):
            signes.lire(m, "joueur", [s], expres=True)
        m = recharger(m)
        c = m.data["lectures"][s["id"]]
        self.assertEqual(c["valeur"], "hostilite")
        self.assertIn("semble", signes.impressions(m)[0]["texte"])
        self.assertIn("hostilité", " ".join(x["texte"] for x in signes.impressions(m)))
        with patch("donjon.signes._jet", side_effect=AssertionError("nouveau dé")):
            signes.lire(m, "joueur", [s])
        self.assertEqual(m.data["lectures"][s["id"]], c)

    def test_une_meprise_peut_aussi_etre_nette(self):
        m = ecarter(scene())
        m.joueur["stats"]["PSY"] = 1
        s = next(s for s in signes.percus(m) if s["signe"] == "ecart")
        with patch("donjon.signes._jet", return_value=1):
            signes.lire(m, "joueur", [s])
        m = recharger(m)
        impression = next(i for i in signes.impressions(m) if i["envers"] == "brune")
        self.assertEqual(impression["lecture"], "hostilite")
        self.assertEqual(impression["nettete"], "nette")
        self.assertIn("semble", impression["texte"])
        self.assertNotIn("peut-être", impression["texte"])
        self.assertNotIn("vrai", impression)

    def test_la_lecture_transmise_se_perime_aussi(self):
        from donjon.esprits import croyance
        m = scene()
        s = next(s for s in signes.de(ecarter(m), "ilse") if s["signe"] == "ecart")
        croire(m, "brune", "ilse", "intention", "guet", "dit:marchand", .4,
               signe=s["id"], envers="reserve")
        m = recharger(m)
        self.assertTrue(signes.intentions_lues(m, "brune"))
        m.data["minutes"] += 31
        m = recharger(m)
        self.assertIsNone(croyance(m, "brune", "ilse", "intention"))
        self.assertEqual(signes.intentions_lues(m, "brune"), [])
        self.assertNotIn("guetter", rendu(m))

    def test_tirage_separe_reprise_et_expiration(self):
        m = ecarter(scene())
        avant = m.copier()
        signes.lire(m, "joueur")
        self.assertEqual(m.d20(), avant.d20())
        n = recharger(m)
        self.assertEqual(signes._jet(m), signes._jet(n))
        n.data["minutes"] += 121
        n = recharger(n)
        self.assertEqual(signes.impressions(n), [])
        self.assertNotIn("semble", rendu(n))

    def test_colere_tort_reel_dedup_estompement(self):
        for id, autre in (("ilse", "brune"), ("brune", "ilse")):
            m = scene()
            memoriser(m, id, {"type": "pousse", "auteur": autre, "preuve": "un-tort"})
            c = copy.deepcopy(signes.emotion(m, id))
            self.assertIsNotNone(c)
            memoriser(m, id, {"type": "pousse", "auteur": autre, "preuve": "un-tort"})
            self.assertEqual(signes.emotion(m, id), c)
            m = recharger(m)
            self.assertTrue(any(s["signe"] == "brusque" for s in signes.publics(m)))
            m.data["minutes"] += 15
            self.assertAlmostEqual(signes.emotion(m, id)["niveau"], c["niveau"] / 2)
            m.data["minutes"] += 150
            self.assertIsNone(signes.emotion(recharger(m), id))

    def test_perception_cache_suit_relations_emotion_attitude(self):
        m = scene()
        with spatial.vue_memorisee(m):
            self.assertFalse(signes.publics(m))
            ecarter(m)
            self.assertTrue(signes.publics(m))
        m = recharger(m)
        avant = copy.deepcopy(m.data)
        with patch.object(spatial, "VERIFICATION", 1), spatial.vue_memorisee(m):
            self.assertEqual(signes.publics(m), signes.publics(m))
            m.contexte()
        self.assertEqual(m.data, avant)

    def test_projection_sans_verite_axes_jets_ni_cible_invisible(self):
        m = ecarter(scene())
        signes.lire(m, "joueur")
        m = recharger(m)
        def verifier(v):
            if isinstance(v, dict):
                self.assertFalse(set(v) & {"vrai", "dissimule", "jet", "marge", "justes", *relations.AXES})
                for x in v.values():
                    verifier(x)
            elif isinstance(v, list):
                for x in v:
                    verifier(x)
        contexte = m.contexte()
        verifier(contexte["signes_percus"])
        verifier(contexte["impressions"])
        self.assertTrue(contexte["signes_percus"])
        placer(m, "brune", "crypte", [5, 3])
        public = json.dumps(m.contexte()["signes_percus"], ensure_ascii=False)
        self.assertNotIn("Brune", public)
        self.assertNotIn("brune", public)

    def test_dissimulation_et_ton_exigent_une_parole_saisie(self):
        m = scene()
        lire(m, "ilse")["relations"]["brune"] = relations._nouvelle({"affection": 70})
        self.assertFalse(any(s["signe"] == "doux" for s in signes.percus(m, "brune")))
        with patch("donjon.signes._jet", return_value=20):
            signes.entendre_ton(m, "brune", "ilse", ["brune"])
        m = recharger(m)
        self.assertTrue(any(c["signe"] for _, _, c in signes.actives(m, "brune")))
        lire(m, "ilse")["relations"]["brune"] = relations._nouvelle({"peur": 70})
        m.objets["ilse"]["profil"]["valeurs"]["fierte"] = 70
        self.assertTrue(signes.dissimule(m, "ilse", "brune"))
        self.assertFalse(any(s["signe"] == "yeux_bas" for s in signes.percus(recharger(m))))

    def test_reglages_gorm_et_validation(self):
        m = scene()
        appliquer_reglages(m, ["gorm.PSY=16", "ilse.fierte=80"])
        m = recharger(m)
        self.assertEqual(m.objets["marchand"]["profil"]["caracteristiques"]["PSY"], 16)
        self.assertIn("PSY", __import__("donjon.rendu", fromlist=["fiche"]).fiche(m))
        for invalide in ("gorm.PSY=100", "absent.PSY=16", "gorm.inconnu=5", "gorm.PSY=-1"):
            with self.assertRaises(ValueError):
                appliquer_reglages(m, [invalide])

    def test_un_gardien_lit_le_guet_puis_tourne_son_vrai_regard(self):
        m = scene()
        m.data["salles"]["antichambre"]["lumiere_naturelle"] = 2
        placer(m, "marchand", "antichambre", [6, 4])
        placer(m, "brune", "antichambre", [7, 3])
        m.joueur.update(position=[6, 5], orientation="nord")
        regarder(m, "marchand", "reserve")
        percevoir_tous(m)
        intention(m, "brune", "crocheter", "reserve", "crochets", "sans_temoin", attente=600)
        lire(m, "brune")["patience"] = 0
        self.assertFalse(relations.se_mefie(m, "marchand", "brune"))
        vus = [s for s in signes.percus(m, "marchand") if s["signe"] == "attend"]
        with patch("donjon.signes._jet", return_value=20):
            signes.lire(m, "marchand", vus)
        m = recharger(m)
        self.assertTrue(signes.intentions_lues(m, "marchand"))
        from donjon.deliberation import menaces
        self.assertIn("antichambre", menaces(m, "marchand"))
        lire(m, "marchand")["intention"] = None
        m.objets["marchand"]["orientation"] = "ouest"
        dt = signes.surveiller(m, "marchand")
        self.assertGreater(dt, 0)
        m = recharger(m)
        self.assertEqual(m.objets["marchand"]["orientation"], "nord-est")
        self.assertIn("Gorm ne quitte pas Brune des yeux.", rendu(m))
        self.assertFalse(relations.se_mefie(m, "marchand", "brune"))

    def test_mensonge_flaire_deux_locuteurs_sans_apprendre_le_vrai(self):
        from donjon.echanges import executer
        from donjon.esprits import croyance
        for auteur, auditeur in (("ilse", "brune"), ("brune", "ilse")):
            m = scene()
            croire(m, auteur, "cloche", "lieu", "chambre_cloche", "savoir", salle="chambre_cloche", case=None)
            lire(m, auditeur)["croyances"].pop("cloche", None)
            m.data["connus"].append("cloche")
            etape = {**_etape("dire", auditeur),
                     "contenu": {"sujet": "cloche", "attribut": "lieu", "valeur": "crypte"}}
            lignes = []
            with patch("donjon.signes._jet", return_value=20):
                self.assertTrue(executer(m, auteur, etape, lignes))
            m = recharger(m)
            doute = croyance(m, auditeur, auteur, "parole_doutee")
            self.assertEqual(doute["source"], "devine")
            self.assertEqual(doute["valeur"], "mensonge")
            self.assertIsNone(croyance(m, auditeur, "cloche", "lieu"))
            self.assertEqual(m.objets["cloche"]["lieu"], "chambre_cloche")
            self.assertTrue(lignes)
            self.assertTrue(any(s["type"] == "parole_doutee" for s in lire(m, auditeur)["memoire"]))

    def test_meme_observation_joueur_ne_decale_pas_les_lectures_d_un_pnj(self):
        m = ecarter(scene())
        n = m.copier()
        signes.lire(m, "joueur")
        # Autre flux d'observateur : mêmes jets, y compris après une sauvegarde.
        m, n = recharger(m), recharger(n)
        self.assertEqual(signes._jet(m, "brune"), signes._jet(n, "brune"))
        self.assertEqual(signes._jet(m, "ilse"), signes._jet(n, "ilse"))
        self.assertTrue(m.data["lectures"])
        self.assertIn("semble", rendu(m))


if __name__ == "__main__":
    unittest.main()


class FusionTests(unittest.TestCase):
    """Accords de la fusion de 3c avec les branches parues depuis sa base (garde, noms, corps)."""

    def test_guet_lu_sur_un_lieu_de_devoir_coute_comme_une_charge(self):
        # `codex-garde-pret` : à valeurs neutres, s'éloigner d'un lieu gardé coûte 2 par minute.
        # Un guet lu sur un lieu de ronde, sans bien à lui, le rend menacé (3c) : jamais gratuit.
        from donjon.deliberation import gardes
        from donjon.planification import Vue
        for scenario, gardien, guetteur, salle, cible, prix in (
                ("relais", "marchand", "brune", "crypte", "bois", 2.7),
                ("auberge", "odile", "lucien", "etable", "fagots_etable", 2)):
            with self.subTest(gardien=gardien):
                m = presentes(creer(scenario, 7, "fixe"))
                calme(m, gardien, guetteur)
                self.assertEqual(m.objets[cible]["lieu"], salle)
                placer(m, gardien, salle, [1, 1])
                placer(m, guetteur, salle, [2, 1])
                lire(m, gardien)["relations"].pop(guetteur, None)
                percevoir_tous(m)
                self.assertNotIn(salle, gardes(m, gardien))
                croire(m, gardien, guetteur, "intention", "guet", "devine", .6, signe="signe:essai", envers=cible)
                m = recharger(m)
                self.assertFalse(relations.se_mefie(m, gardien, guetteur))
                self.assertIn(salle, gardes(m, gardien))
                self.assertEqual(Vue(m, gardien).prix_gardes[salle], prix)

    def test_signe_et_impression_d_inconnus_par_leur_designation(self):
        # `codex-noms` : un signe ne nomme ni son auteur ni sa cible si le joueur n'a pas entendu leur
        # nom ; le MJ ne reçoit que des références opaques.
        for id, autre in (("ilse", "brune"), ("brune", "ilse")):
            with self.subTest(id=id):
                m = ecarter(scene(), id, autre)
                m.data["noms_connus"] = []
                with patch("donjon.signes._jet", return_value=20):
                    signes.lire(m, "joueur")
                m = recharger(m)
                textes = [s["texte"] for s in signes.publics(m) + signes.impressions(m)]
                self.assertTrue(textes)
                vue = rendu(m)
                public = json.dumps({k: m.contexte()[k] for k in ("signes_percus", "impressions")}, ensure_ascii=False)
                for nom in ("Ilse", "Brune"):
                    self.assertFalse(any(nom in t for t in textes))
                    self.assertNotIn(nom, vue.split("Sorties")[-1])
                    self.assertNotIn(nom, public)
                for cle in (id, autre):
                    self.assertNotIn('"' + cle + '"', public)
                self.assertIn("personne_", public)

    def test_l_inconscient_n_emet_ni_ne_lit_meme_vue_gardee(self):
        # 4a : la conscience n'est pas dans l'empreinte physique ; elle entre dans la clé sociale,
        # sans quoi les signes perçus gardés survivraient à l'évanouissement.
        from donjon import corps
        m = ecarter(scene())
        with patch.object(spatial, "VERIFICATION", 1), spatial.vue_memorisee(m):
            self.assertTrue(any(s["personnage"] == "ilse" for s in signes.publics(m)))
            self.assertTrue(signes.percus(m, "brune"))
            corps.endormir(m, "ilse")
            self.assertFalse(any(s["personnage"] == "ilse" for s in signes.publics(m)))
            self.assertEqual(signes.percus(m, "ilse"), [])
        m = recharger(m)
        self.assertFalse(any(s["personnage"] == "ilse" for s in signes.publics(m)))
        self.assertFalse(any(s["personnage"] == "ilse" for s in m.contexte()["signes_percus"]))
