"""4a : corps et conséquences perçues, dans le monde sauvegardé, pour plusieurs personnes."""
import copy
import unittest
from unittest.mock import patch

from donjon import corps, vecu
from donjon.banc_pnj import appliquer_etats, creer
from donjon.caractere import base, modificateur
from donjon.dialogues import interlocuteurs
from donjon.esprits import esprit, lire, percevoir_tous, percus
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.ouie import retentir, saisissent
from donjon.passage import laisser_passer
from donjon.pnj import avancer, peuvent_se_parler
from donjon.rendu import decrire, regarder
from donjon.scene import scene_percue
from donjon.temps import MINUTE, ecouler, instant
from tests.support import calme, regarder as orienter
from tests.test_tensions import placer, recharger


def scene():
    m = creer("relais", 1985, "fixe")
    calme(m, "marchand", "ilse", "aubin", "brune")
    m.joueur.update(salle="antichambre", position=[2, 5], orientation="est")
    placer(m, "ilse", "antichambre", (3, 5))
    placer(m, "marchand", "antichambre", (4, 5))
    placer(m, "aubin", "echoppe", (4, 4))
    orienter(m, "marchand", "ilse")
    percevoir_tous(m)
    return m


def passer(m, dt):
    minutes = ecouler(m, dt)
    lignes = []
    avancer(m, minutes, lignes, dt)
    m.verifier()
    return lignes


class CorpsBlessableTests(unittest.TestCase):
    def test_pv_communs_et_surcharge_scenario_persistes(self):
        m = recharger(scene())
        for id in corps.personnages(m):
            o = m.joueur if id == "joueur" else m.objets[id]
            self.assertEqual(o["pv"], o["pv_max"])
            self.assertEqual(o["pv_max"], 6 + base(m, id, "FOR"))
        m.objets["ilse"].update(pv_max=25, pv=23)
        m = recharger(m)
        self.assertEqual((m.objets["ilse"]["pv"], m.objets["ilse"]["pv_max"]), (23, 25))

    def test_blessures_et_malus_du_joueur_et_de_deux_pnj_apres_recharge(self):
        for id in ("joueur", "ilse", "aubin"):
            with self.subTest(id=id):
                m = scene()
                o = m.joueur if id == "joueur" else m.objets[id]
                o["pv"] = o["pv_max"] * 2 // 3
                m = recharger(m)
                self.assertEqual(corps.blessure(m, id), 1)
                self.assertEqual(corps.malus(m, "FOR", id), -2)
                o = m.joueur if id == "joueur" else m.objets[id]
                o["pv"] = o["pv_max"] // 3
                m = recharger(m)
                self.assertEqual(corps.malus(m, "DEX", id), -4)
                self.assertEqual(corps.malus(m, "VOL", id), -2)
                self.assertEqual(modificateur(m, id, "FOR"), (base(m, id, "FOR") - 10) // 2 - 4)

    def test_repos_soigne_sur_le_temps_vecu_et_pas_l_effort(self):
        for id in ("joueur", "ilse"):
            with self.subTest(id=id):
                m = scene()
                o = m.joueur if id == "joueur" else m.objets[id]
                o["pv"] -= 3
                avant = o["pv"]
                vecu.noter(m, id, 0, "repos")
                ecouler(m, 30 * MINUTE)
                vecu.solder(m, id, instant(m))
                m = recharger(m)
                vecu.noter(m, id, instant(m), "effort")
                ecouler(m, 10 * MINUTE)
                vecu.solder(m, id, instant(m))
                self.assertEqual(corps.pv(m, id), avant)
                vecu.noter(m, id, instant(m), "repos")
                ecouler(m, 30 * MINUTE)
                vecu.solder(m, id, instant(m))
                m = recharger(m)
                self.assertEqual(corps.pv(m, id), avant + 1)

    def test_inconscient_ne_percoit_entend_parle_ni_laisse_passer(self):
        for id in ("ilse", "aubin"):
            with self.subTest(id=id):
                m = scene()
                if id == "aubin":
                    placer(m, "ilse", "crypte", (1, 1))
                placer(m, id, "antichambre", (3, 5))
                corps.endormir(m, id)
                m = recharger(m)
                avant = copy.deepcopy(lire(m, id)["croyances"])
                corps_avant = corps.valeurs(m, id)["faim"]
                percevoir_tous(m)
                retentir(m, "joueur", "crier", force="appel")
                self.assertEqual(percus(m, id), ({}, set()))
                self.assertNotIn(id, saisissent(m, "joueur"))
                self.assertNotIn(id, interlocuteurs(m))
                self.assertFalse(peuvent_se_parler(m, "marchand", id))
                self.assertEqual(laisser_passer(m, id, "joueur")[0], None)
                from donjon.pnj import appeler
                appeler(m, "marchand", id, [])
                self.assertTrue(any(s["type"] == "appel_sans_reponse" and s["qui"] == id
                                    for s in lire(m, "marchand")["memoire"]))
                self.assertEqual(retentir(m, id, "dire", texte="Je parle."), [])
                # Aucun protecteur pour cette épreuve : constater la durée sans intervention.
                m.objets["marchand"]["profil"]["protege"] = []
                passer(m, MINUTE // 2)
                m = recharger(m)
                self.assertEqual(lire(m, id)["croyances"], avant)
                self.assertIsNone(lire(m, id)["intention"])
                self.assertEqual(m.objets[id]["position"], [3, 5])
                passer(m, MINUTE // 2)
                self.assertGreater(corps.valeurs(m, id)["faim"], corps_avant)

    def test_etat_visible_sans_pv_ni_reveil_et_sans_cone(self):
        m = scene()
        corps.endormir(m, "ilse")
        m = recharger(m)
        self.assertIn("sans connaissance", decrire(m, "ilse"))
        obj = next(o for n in scene_percue(m)["niveaux"] for o in n["objets"] if o["id"] == "ilse")
        self.assertFalse(obj["etat_corps"]["conscient"])
        self.assertIsNone(obj["orientation"])
        self.assertNotIn("pv", obj)
        self.assertNotIn("inconscient", obj["etat_corps"])
        public = next(o for o in m.contexte()["objets_perceptibles"] if o["id"] == "ilse")
        self.assertFalse(public["etat_corps"]["conscient"])
        self.assertFalse({"pv", "pv_max", "corps", "orientation"} & set(public))

    def test_protecteur_ranime_ilse_et_un_autre_protege(self):
        for id in ("ilse", "brune"):
            with self.subTest(id=id):
                m = scene()
                placer(m, "ilse", "crypte", (1, 1))
                placer(m, id, "antichambre", (3, 5))
                m.objets["marchand"]["profil"]["protege"] = [id]
                corps.endormir(m, id)
                m = recharger(m)
                passer(m, 3 * MINUTE)
                m = recharger(m)
                self.assertTrue(corps.conscient(m, id))
                self.assertTrue(any(s["type"] == "reveil" for s in lire(m, id)["memoire"]))
                self.assertTrue(any("ranime" in c["texte"] for c in m.data["chronique"]))

    def test_reveil_naturel_zero_pv_et_meme_laps_decoupe(self):
        for id in ("ilse", "aubin"):
            with self.subTest(id=id):
                m = scene()
                m.objets["marchand"]["profil"]["protege"] = []
                corps.perdre(m, id, 100)
                reveil = corps.corps(m, id)["inconscient"]
                self.assertGreaterEqual(reveil, 31 * MINUTE)
                a, b = recharger(m), recharger(m)
                passer(a, reveil + 23)
                passer(b, reveil // 2)
                b = recharger(b)
                passer(b, reveil - reveil // 2 + 23)
                a, b = recharger(a), recharger(b)
                self.assertEqual(a.data, b.data)
                self.assertEqual(corps.pv(a, id), 1)
                self.assertTrue(corps.conscient(a, id))

    def test_ranimer_joueur_commande_contact_delai_et_persistance(self):
        m = scene()
        corps.endormir(m, "ilse")
        with self.assertRaises(ErreurMonde) as ctx:
            Moteur(m).preparer(proposition("ranimer", "ilse"))
        self.assertTrue(ctx.exception.attendu)
        m.objets["marchand"]["profil"]["protege"] = []
        passer(m, MINUTE)
        m = recharger(m)
        p = Moteur(m).preparer(proposition("ranimer", "ilse"))
        texte = Moteur(m).executer(p)
        m = recharger(m)
        self.assertTrue(corps.conscient(m, "ilse"))
        self.assertIn("ranimes", texte)

    def test_depouille_et_biens_et_decouverte_apres_recharge(self):
        for id in ("aubin", "brune"):
            with self.subTest(id=id):
                m = scene()
                salle, case = ("beffroi", (3, 3)) if id == "aubin" else ("antichambre", (3, 5))
                # Épreuve du plan : Aubin à la galerie du beffroi ; autre cas au refuge.
                if salle == "beffroi":
                    m.data["salles"][salle].update(lumiere_naturelle=2, fenetres=1)
                    m.joueur.update(salle=salle, position=[2, 3], orientation="est")
                    placer(m, "marchand", salle, (4, 3))
                placer(m, id, salle, case)
                orienter(m, "marchand", id)
                # Le témoin se souvient de la personne avant la mort.
                percevoir_tous(m)
                m.data.setdefault("paroles_pnj", []).append({"locuteur": id, "texte": "Je reste ici.",
                    "salle": salle, "minute": 0, "auditeurs": ["joueur"], "revision": 0})
                corps.mourir(m, id, cause="épreuve")
                m = recharger(m)
                self.assertEqual(m.data["paroles_pnj"][-1]["locuteur"], id)
                self.assertEqual(m.objets[id]["type"], "depouille")
                self.assertNotIn(id, m.data["esprits"])
                self.assertNotIn("orientation", m.objets[id])
                self.assertNotIn("profil", m.objets[id])
                self.assertTrue(all(o["proprietaire"] == id for o in m.objets.values() if o["lieu"] == id))
                percevoir_tous(m)
                m = recharger(m)
                self.assertTrue(lire(m, "marchand")["croyances"][id]["etat"]["valeur"]["mort"])
                self.assertTrue(any(s["type"] == "mort_vue" and s["objet"] == id for s in lire(m, "marchand")["memoire"]))
                self.assertIn("corps de", decrire(m, id))
                self.assertNotIn(id, interlocuteurs(m))

    def test_nouvelle_de_mort_sans_coupable_circule(self):
        from donjon.social import nouvelles, phrase, recevoir
        m = scene()
        corps.mourir(m, "aubin")
        placer(m, "marchand", "echoppe", (4, 5))
        orienter(m, "marchand", "aubin")
        percevoir_tous(m)
        m = recharger(m)
        _, noyau, _, _ = next(n for n in nouvelles(m, "marchand") if n[1]["type"] == "mort_vue")
        self.assertIn("Aubin est mort", phrase(m, noyau))
        with patch("donjon.paroles.jet_persuasion", return_value=(True, {})):
            recevoir(m, "ilse", "marchand", {"type": "nouvelle", "evenement": noyau, "rang": 0})
        m = recharger(m)
        self.assertTrue(lire(m, "ilse")["croyances"]["aubin"]["etat"]["valeur"]["mort"])

    def test_chute_a_zero_le_joueur_revient_dans_la_meme_action(self):
        for effet in ("blessure_chute", "blessure_franchissement"):
            with self.subTest(effet=effet):
                m = scene()
                m.joueur["pv"] = 1
                lignes = []
                Moteur._appliquer(m, (effet, "", 3), lignes)
                self.assertFalse(corps.conscient(m))
                attendu = corps.corps(m, "joueur")["inconscient"]
                Moteur._attendre_reveil(m, lignes)
                m = recharger(m)
                self.assertEqual(instant(m), attendu)
                self.assertEqual(corps.pv(m), 1)
                self.assertEqual(lignes[:2], ["Tu perds connaissance.", "Tu reviens à toi."])
                self.assertIn(m.data["salles"][m.joueur["salle"]]["nom"].upper(), lignes[2])

    def test_mort_joueur_cloture_persistante(self):
        from donjon.web.pont import PontWeb
        m = scene()
        corps.mourir(m, "joueur", "brune", "épreuve")
        m = recharger(m)
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(proposition("attendre"))
        self.assertIn("terminée", regarder(m))
        pont = PontWeb()
        pont.rafraichir(m, None, None)
        self.assertFalse(pont.soumettre("attendre"))
        self.assertEqual(pont.dernier_etat["fin"]["cause"], "épreuve")
        import io
        import tempfile
        from contextlib import redirect_stdout
        from pathlib import Path
        import jeu
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as sortie:
            chemin = Path(tmp) / "close.json"
            m.sauver(chemin)
            with patch("builtins.input", side_effect=AssertionError("Une partie close ne demande aucune commande")):
                self.assertEqual(jeu.main(["--offline", "--console", "--save", str(chemin)]), 0)
            self.assertEqual(Monde.charger(chemin).data["fin"]["cause"], "épreuve")
        self.assertIn("terminée", sortie.getvalue())

    def test_saut_complet_a_zero_se_recharge_reveille_sans_recit_pendant_l_absence(self):
        from tests.test_espace import terrasse, AJOUT
        from donjon.espace import preparer
        from donjon.operations import sequence, etape
        for jet in (1, 20):
            with self.subTest(jet=jet):
                m, _ = terrasse()
                m = preparer(m, AJOUT)
                m.joueur["pv"] = 1
                moteur = Moteur(m)
                plan = moteur.preparer(sequence(etape("sauter", "appui_terrasse_nord", "abord_terrasse_nord")))
                with patch.object(Monde, "d20", return_value=jet):
                    texte = moteur.executer(plan)
                m = recharger(m)
                self.assertEqual(m.joueur["salle"], "abord_terrasse_nord")
                self.assertEqual(corps.pv(m), 1)
                self.assertTrue(corps.conscient(m))
                self.assertIn("Tu perds connaissance.\nTu reviens à toi.", texte)
                self.assertFalse(m.data.get("fin"))

    def test_repos_fractionne_et_recharge_garde_exactement_le_soin(self):
        m = scene()
        m.joueur["pv"] -= 2
        vecu.noter(m, "joueur", 0, "repos")
        a, b = recharger(m), recharger(m)
        ecouler(a, 61 * MINUTE + 17)
        vecu.solder(a, "joueur", instant(a))
        for dt in (103, 19 * MINUTE, 42 * MINUTE - 86):
            ecouler(b, dt)
            vecu.solder(b, "joueur", instant(b))
            b = recharger(b)
        self.assertEqual(corps.pv(a), corps.pv(b))
        self.assertEqual(corps.corps(a, "joueur")["soin"], corps.corps(b, "joueur")["soin"])

    def test_tous_les_pnj_peuvent_devenir_depouille_sans_reference_invalide(self):
        from donjon.esprits import pnjs
        for scenario in ("relais", "mine", "auberge", "crue"):
            for id in pnjs(creer(scenario)):
                with self.subTest(scenario=scenario, id=id):
                    m = creer(scenario)
                    corps.mourir(m, id)
                    m = recharger(m)
                    moteur = Moteur(m)
                    moteur.executer(moteur.preparer(proposition("attendre")))
                    m = recharger(m)
                    self.assertEqual(m.objets[id]["type"], "depouille")
                    self.assertNotIn(id, m.data["esprits"])

    def test_invariants_invalides_refuses(self):
        m = scene()
        m.objets["ilse"]["pv"] = 0
        with self.assertRaises(ErreurMonde):
            m.verifier()
        appliquer_etats(m, ["ilse:inconscient"])
        esprit(m, "ilse")["eveil"] = 1
        with self.assertRaises(ErreurMonde):
            m.verifier()
