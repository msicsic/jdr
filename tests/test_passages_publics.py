"""U-M passage : callbacks de la page, contrat moteur et publication rechargée."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.atelier import nouveau_atelier
from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.franchissement import cle_arbitrage
from donjon.geometrie import placer
from donjon.gestes_publics import passages_publics
from donjon.monde import ErreurMonde, Monde, objet
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.spatial import installer, memoriser
from tests import test_corps_publics as support
from tests.test_descripteur_public import vues
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests.test_sous_obstacle import scene
from tools.banc_parties import preparer


def normaliser(m):
    m = Monde(copy.deepcopy(m.data))
    memoriser(m)
    vues(m)
    return m


def clic(m, cible, geste, **parametres):
    d = {"geste": geste, "cible": cible}
    if parametres:
        d["parametres"] = parametres
    return next(c for c in page(m)["envoisClic"] if c["envoye"] == d)


def atelier(echelle=False, haut=False, memorise=True, porte=False):
    m = nouveau_atelier()
    installer(m)
    a = m.objets["mur_atelier"]["appui_vertical"]
    m.joueur.update(salle="cour", position=[2, 3], orientation="sud")
    a.update(position_bas=[2, 4], position_haut=[2, 0])
    placer(m.objets["perche_1"], "cour", [2, 3])
    placer(m.objets["perche_2"], "cour", [3, 3])
    m.objets["perche_1"].update(proprietaire="joueur")
    if porte:
        m.objets["perche_1"]["lieu"] = "joueur"
    if echelle:
        m.objets["echelle_test"] = objet("echelle_test", "échelle", "assemblage", "cour",
            assemblage="barreaux", longueur_cm=300, largeur_cm=40, barreaux=8,
            composants={"perche_1": 300}, charge_jeu_kg=200,
            mobile=True, masse=5, proprietaire="joueur", installation={"support": "mur_atelier"})
        placer(m.objets["echelle_test"], "cour", [2, 3])
        if haut:
            m.joueur.update(salle="terrasse", position=[2, 0], orientation="nord")
    m = normaliser(m)
    if not echelle and memorise:
        # Un vrai plan MJ, préparé puis tenté, établit l'arbitrage. On conserve
        # ensuite sa trace sur la scène initiale pour rejouer le même contexte.
        depart = copy.deepcopy(m.data)
        p = sequence(*([] if porte else [etape("deplacer", "perche_1", "joueur")]),
                     etape("franchir_obstacle", "mur_atelier", "terrasse", "perche_1", "appui_mobile", 19))
        with patch.object(Monde, "d20", return_value=20):
            Moteur(m).executer(Moteur(m).preparer(p, "MJ"))
        depart["arbitrages"] = copy.deepcopy(m.data["arbitrages"])
        m = normaliser(Monde(depart))
    return m


class PassagesPublicsTests(unittest.TestCase):
    boucle = support.CorpsPublicsTests.boucle

    def parite(self, m, cible, geste, texte, parametres=None, effet=None):
        c = clic(m, cible, geste, **(parametres or {}))
        self.assertEqual(c["clics"], 2)
        d = DescripteurPublic(c["envoye"])
        canonique = analyser(m, texte)
        self.assertEqual(proposition_descripteur(m, d), canonique)
        pa, pb = Moteur(m).preparer(d), Moteur(m).preparer(canonique)
        self.assertEqual(pa.resume(m), pb.resume(m))
        da, db = copy.deepcopy(pa.__dict__), copy.deepcopy(pb.__dict__)
        for x in (da, db):
            x.pop("choix_public"); x.pop("etat_consentement")
        self.assertEqual(da, db)
        suites = ["tenter"] if pa.confirmation or pa.stat else []
        a, la, _ = self.boucle(m.copier(), [d, *suites])
        b, lb, _ = self.boucle(m.copier(), [texte, *suites])
        self.assertEqual(la, lb)
        for x in (a.data, b.data):
            for tour in x["conversation"]:
                tour.pop("joueur", None)
        self.assertEqual(a.data, b.data)
        self.assertEqual(vues(a), vues(b))
        self.assertEqual(etat(a), etat(b))
        if effet:
            effet(a)
        self.assertTrue(a.data["journal"])
        self.assertIn("Compris :", "\n".join(la))
        return pa

    def test_dessous_enjamber_escalader_deux_scenarios(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            for methode, hauteur, verbe in (("dessous", 100, "ramper sous "),
                                            ("dessus", 50, "enjamber "), ("dessus", 100, "escalader ")):
                with self.subTest(scenario=scenario, methode=methode, hauteur=hauteur):
                    m = scene(scenario, cible)
                    m.objets[cible]["passage"].update(hauteur_cm=hauteur, degagement_cm=0 if hauteur == 50 else 45)
                    for id, o in m.objets.items():
                        if m.est_porte(id):
                            o["longueur_cm"] = 20
                    m = normaliser(m)
                    debut = list(m.joueur["position"])
                    self.parite(m, cible, "passer_obstacle", verbe + cible, {"methode": methode},
                                lambda a: self.assertEqual(a.joueur["position"], [debut[0] + 2, debut[1]]))

    def test_echelle_montee_descente_et_perche_au_sol_ou_portee(self):
        for haut in (False, True):
            with self.subTest(echelle=True, haut=haut):
                m = atelier(echelle=True, haut=haut)
                self.parite(m, "echelle_test", "franchir", ("descendre " if haut else "monter ") + "echelle_test",
                            effet=lambda a: self.assertEqual(a.joueur["salle"], "cour" if haut else "terrasse"))
        for porte in (False, True):
            with self.subTest(perche=True, porte=porte):
                m = atelier(porte=porte)
                self.parite(m, "mur_atelier", "franchir_obstacle", "franchir mur_atelier avec perche_1",
                            {"outil": "perche_1"}, lambda a: self.assertEqual(a.joueur["salle"], "terrasse"))

    def test_bancs_reels_refus_publics_et_forme_inconnue(self):
        racine = Path(__file__).parent / "data/bancs"
        attendus = {"trop-bas": "trop bas", "trop-haut": "trop haut", "encombre": "encombrant"}
        for script in sorted(racine.glob("sous-obstacle-*.json")):
            with self.subTest(script=script.name), tempfile.TemporaryDirectory() as tmp:
                fichier = Path(tmp) / "partie.json"
                preparer(json.loads(script.read_text(encoding="utf-8")), fichier)
                m = normaliser(Monde.charger(fichier))
                cible = "poutre_conduite" if "poutre_conduite" in m.objets else (
                    "lit_chaud" if "enjamber" in script.name else "table_longue")
                if "enjamber" in script.name:
                    cible = next(i for i, o in m.objets.items() if "lit à rideaux" in o["nom"])
                if "inconnu" in script.name:
                    self.assertFalse([o for o in passages_publics(m) if o["cible"] == cible])
                    continue
                methode = "dessus" if any(x in script.name for x in ("trop-haut", "enjamber")) else "dessous"
                d = DescripteurPublic(clic(m, cible, "passer_obstacle", methode=methode)["envoye"])
                refus = next((v for k, v in attendus.items() if k in script.name), None)
                if refus:
                    avant = copy.deepcopy(m.data)
                    a, lignes, _ = self.boucle(m, [d])
                    self.assertIn(refus, "\n".join(lignes))
                    self.assertEqual({k: v for k, v in a.data.items() if k != "conversation"},
                                     {k: v for k, v in avant.items() if k != "conversation"})
                else:
                    self.parite(m, cible, "passer_obstacle", ("enjamber " if methode == "dessus" else "ramper sous ") + cible,
                                {"methode": methode})

    def test_annuler_et_confirmation_perimee_sans_effet(self):
        for m, cible, geste, params in ((normaliser(scene()), "poutre_conduite", "passer_obstacle", {"methode": "dessous"}),
                (atelier(), "mur_atelier", "franchir_obstacle", {"outil": "perche_1"}),
                (atelier(echelle=True), "echelle_test", "franchir", {})):
            with self.subTest(geste=geste):
                d = DescripteurPublic(clic(m, cible, geste, **params)["envoye"])
                avant = copy.deepcopy(m.data)
                a, _, _ = self.boucle(m.copier(), [d, "annuler"])
                self.assertEqual({k: v for k, v in a.data.items() if k != "conversation"},
                                 {k: v for k, v in avant.items() if k != "conversation"})
                p = Moteur(m).preparer(d)
                self.assertTrue(p.choix_public)
                m.joueur["stats"]["DEX"] += 1  # Aucun changement de révision.
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde):
                    Moteur(m).executer(p)
                self.assertEqual(m.data, avant)

    def test_projection_connue_sans_preconditions_et_arbitrage_absent(self):
        m = atelier(memorise=False)
        self.assertFalse([p for p in passages_publics(m) if p["geste"] == "franchir_obstacle"])
        m = atelier()
        offres = passages_publics(m)
        self.assertTrue(any(o["geste"] == "franchir_obstacle" for o in offres))
        self.assertTrue(all(set(o) <= {"cible", "geste", "methode", "libelle", "outil", "ancrage"} for o in offres))
        # La construction du menu n'appelle aucun validateur de faisabilité.
        with patch("donjon.franchissement.conditions", side_effect=AssertionError("aptitude")):
            self.assertEqual(passages_publics(m), offres)
        with patch.object(m, "visible", return_value=False):
            self.assertFalse(passages_publics(m))

    def test_perche_abimee_reste_offerte_mais_refus_moteur_et_recharge(self):
        m = atelier()
        m.objets["perche_1"]["integrite"] -= 1
        m = normaliser(m)
        d = DescripteurPublic(clic(m, "mur_atelier", "franchir_obstacle", outil="perche_1")["envoye"])
        avant = copy.deepcopy(m.data)
        a, lignes, _ = self.boucle(m, [d])
        self.assertIn("intact", "\n".join(lignes))
        self.assertEqual({k: v for k, v in a.data.items() if k != "conversation"},
                         {k: v for k, v in avant.items() if k != "conversation"})

    def test_homonymes_et_arbitrage_lie_a_la_geometrie_et_charge(self):
        m = atelier()
        for id in ("perche_1", "perche_2"):
            m.objets[id]["nom"] = "perche identique"
        offres = passages_publics(m)
        self.assertIn("(1/2)", next(o["libelle"] for o in offres if o.get("outil") == "perche_1"))
        self.assertIn("(2/2)", next(o["libelle"] for o in offres if o.get("outil") == "perche_2"))
        self.assertEqual(proposition_descripteur(m, DescripteurPublic(
            clic(m, "mur_atelier", "franchir_obstacle", outil="perche_2")["envoye"]))["etapes"][-1]["outil"], "perche_2")
        # Le sceau est exactement celui enregistré par le compilateur historique.
        self.assertIn(cle_arbitrage(m, "mur_atelier", "perche_1", "terrasse"), m.data["arbitrages"])
        m.joueur["masse_kg"] += 1
        self.assertFalse([o for o in passages_publics(m) if o["geste"] == "franchir_obstacle"])

    def test_reference_ou_qualification_disparue_et_parametres_injectes(self):
        m = normaliser(scene())
        d = DescripteurPublic(clic(m, "poutre_conduite", "passer_obstacle", methode="dessous")["envoye"])
        for changement in ("forme", "vue", "parametres"):
            with self.subTest(changement=changement):
                a, entree = m.copier(), copy.deepcopy(d)
                if changement == "forme":
                    a.objets["poutre_conduite"].pop("passage")
                elif changement == "vue":
                    a.joueur.update(salle="antichambre", position=[1, 3], orientation="ouest")
                else:
                    entree.contenu["parametres"]["difficulte"] = 0
                avant = copy.deepcopy(a.data)
                with self.assertRaises(ErreurMonde) as exc:
                    Moteur(a).preparer(entree)
                self.assertTrue(exc.exception.attendu)
                self.assertEqual(a.data, avant)

    def test_premier_arbitrage_et_intention_composee_restent_au_libre(self):
        m = atelier(memorise=False)
        self.assertIsNone(analyser(m, "franchir mur_atelier avec perche_1"))
        m = atelier()
        self.assertIsNone(analyser(m, "franchir mur_atelier avec perche_1 puis prendre la hache"))
        self.assertIsNone(analyser(m, "franchir mur_atelier avec perche_1 sans la prendre"))

    def test_trace_persistante_meme_forme_json_pour_un_autre_mouvement_compose(self):
        m = atelier(echelle=True, haut=True)
        p = sequence(etape("sauter", "mur_atelier", "cour"))
        with patch.object(Monde, "d20", return_value=20):
            Moteur(m).executer(Moteur(m).preparer(p))
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "partie.json"
            m.sauver(fichier)
            r = Monde.charger(fichier)
            self.assertEqual(r.data, m.data)
            self.assertEqual(vues(r), vues(m))
            self.assertEqual(etat(r), etat(m))
            self.assertEqual(r.joueur["salle"], "cour")
            self.assertEqual(r.data["journal"][-1]["etapes"][0]["effets_appliques"][0][0], "voyager")


if __name__ == "__main__":
    unittest.main()
