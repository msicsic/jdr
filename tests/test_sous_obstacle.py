"""Forme, saisie, MJ simulé, moteur, trajet, rendu et sauvegarde du même passage."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.banc_pnj import creer
from donjon.commandes import analyser
from donjon.esprits import croire, lire, percevoir_tous
from donjon.faits_locaux import preparer_faits
from donjon.matiere import valider_passage
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, objet
from donjon.moteur import Moteur, proposition
from donjon.obstacles import conditions, descriptions_crues, transitions
from donjon.operations import etape, sequence
from donjon.pnj import chemin
from donjon.spatial import trajet
from donjon.temps import instant
from tests.support import calme
from tests.test_marche import intention
from tests.test_tensions import placer, recharger
from tests.test_temps_etat import etat_pnj


FORME = {"degagement_cm": 45, "hauteur_cm": 100, "largeur_cm": 80,
         "profondeur_cm": 70, "charge_kg": 200, "appuis": True}


def passage(cible="poutre_conduite", methode="dessous"):
    return sequence(etape("passer_obstacle", cible, methode=methode))


def scene(scenario="relais", cible="poutre_conduite", forme=True):
    m = creer(scenario, 1985, "fixe")
    calme(m, *[i for i, o in m.objets.items() if o.get("profil")])
    o = m.objets[cible]
    if forme:
        # L'étape moteur est vérifiée avant de décrire les données des scénarios.
        o["passage"] = dict(FORME)
    else:
        o.pop("passage", None)
    x, y = o["position"]
    m.joueur.update(salle=o["lieu"], position=[x - 1, y], orientation="est")
    if scenario == "auberge":
        m.objets["chandelle_corvus"]["allume"] = True
    from donjon.pnj import ecarter
    ecarter(m)
    return m


def jouer(m, saisies, reponses=()):
    """Vraie boucle console, fournisseur remplacé ; aucun réseau ni coffre."""
    reponses = iter(reponses)
    def appel(instructions, entree, intention_, fonction, schema):
        if fonction == "auditer_action":
            return {"conforme": True, "motif": ""}
        if fonction == "auditer_narration":
            # Aucun récit libre n'est nécessaire pour ces mouvements du moteur.
            return {"segments": {}}
        return next(reponses)
    with tempfile.TemporaryDirectory() as tmp:
        chemin_ = Path(tmp) / "partie.json"
        m.sauver(chemin_)
        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_appeler_brut", side_effect=appel),
              patch.object(Monde, "d20", return_value=20),
              patch("builtins.input", side_effect=[*saisies, "quitter"]),
              patch("sys.stdout", io.StringIO()) as sortie):
            jeu.main(["--console", "--connexion", "api", "--recit-moteur", "--save", str(chemin_)])
        return Monde.charger(chemin_), sortie.getvalue()


def corridor(forme=True):
    """Même poutre ; les blocs d'auteur ferment les détours pour éprouver le contrat du trajet."""
    m = scene(forme=forme)
    for y in range(7):
        if y == 3:
            continue
        i = f"bloc_test_{y}"
        m.objets[i] = objet(i, "bloc de pierre", "meuble", "echoppe", position=[5, y],
                            position_salle="echoppe", bloque_passage=True, bloque_vue=True)
    m.data["salles"]["echoppe"]["sorties"].pop("sud")
    m.data["salles"]["crypte"]["sorties"] = {
        d: s for d, s in m.data["salles"]["crypte"]["sorties"].items() if s["vers"] != "echoppe"}
    for n, i in enumerate(("aubin", "ilse", "brune")):
        placer(m, i, "crypte", (3 + n, 5))
    placer(m, "marchand", "echoppe", (4, 3))
    m.objets["marchand"]["orientation"] = "est"
    m.joueur.update(salle="antichambre", position=[6, 5], orientation="sud")
    for i, o in m.objets.items():
        if o.get("bloque_passage") and o["lieu"] == "echoppe":
            croire(m, "marchand", i, "lieu", "echoppe", "savoir", salle="echoppe", case=list(o["position"]))
    if forme:
        croire(m, "marchand", "poutre_conduite", "passage", dict(FORME), "savoir")
    intention(m, "marchand", [{"operation": "aller", "lieu": "antichambre"}])
    m.verifier()
    return m


class JoueurTests(unittest.TestCase):
    def test_cas_reel_et_autre_scenario_question_fiche_tenter_recharge(self):
        for scenario, cible, nom in (("relais", "poutre_conduite", "poutre effondrée"),
                                     ("auberge", "table_longue", "longue table")):
            with self.subTest(scenario=scenario):
                m = scene(scenario, cible)
                debut, jets = copy.deepcopy(m.joueur["position"]), m.data["jets"]
                question = f"est-ce que je pourrais passer sous la {nom} ?"
                reponse = {"mode": "action", "texte": "", "faits": ["passages_obstacles"], "proposition": passage(cible)}
                r, sortie = jouer(m, [question], [reponse])
                self.assertIn("Ramper sous", sortie)
                self.assertIn("12 secondes", sortie)
                self.assertIn("Bruit feutré", sortie)
                self.assertIn("Rien n'est encore tenté", sortie)
                self.assertNotIn("Il faut une échelle", sortie)
                self.assertEqual((r.joueur["position"], r.data["jets"], instant(r)), (debut, jets, 0))
                r, sortie = jouer(m, [question, "tenter"], [reponse])
                self.assertIn("Tu passes en rampant sous", sortie)
                self.assertEqual(r.joueur["position"], [debut[0] + 2, debut[1]])
                self.assertEqual(instant(r), 120)
                self.assertTrue(r.objets[cible]["bloque_passage"])
                self.assertEqual(r.objets[cible].get("bloque_vue"), m.objets[cible].get("bloque_vue"))
                self.assertEqual(r.data["journal"][-1]["action"]["etapes"][0]["operation"], "passer_obstacle")
                r, sortie = jouer(r, ["examiner " + nom])
                self.assertIn("Dégagement dessous : 45 cm", sortie)

    def test_commande_locale_attend_confirmation_et_ne_contacte_pas_le_mj(self):
        m = scene()
        self.assertEqual(analyser(m, "ramper sous la poutre effondrée"), passage())
        r, texte = jouer(m, ["ramper sous la poutre effondrée"])
        self.assertEqual(r.joueur["position"], [4, 3])
        self.assertIn("tenter", texte)
        r, texte = jouer(r, ["ramper sous la poutre effondrée", "tenter"])
        self.assertEqual(r.joueur["position"], [6, 3])
        self.assertIn("Tu passes", texte)

    def test_refus_physiques_une_cause_sans_effet_apres_recharge(self):
        cas = (("degagement_cm", 10, "dessous", "trop bas", "degagement_cm"),
               ("hauteur_cm", 200, "dessus", "trop haut", "hauteur_cm"),
               ("largeur_cm", 20, "dessous", "trop étroit", "largeur_cm"),
               ("appuis", False, "dessus", "prises", "appuis"),
               ("charge_kg", 1, "dessus", "poids", "charge_kg"))
        for champ, valeur, methode, message, attendu in cas:
            with self.subTest(champ=champ):
                m = scene()
                m.objets["poutre_conduite"]["passage"][champ] = valeur
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                with self.assertRaisesRegex(ErreurMonde, message) as r:
                    Moteur(m).preparer(passage(methode=methode))
                self.assertIn(attendu, r.exception.attendu)
                self.assertIn("accepté", r.exception.attendu)
                self.assertEqual(m.data, avant)
                r, texte = jouer(m, ["ramper sous la poutre effondrée" if methode == "dessous" else "passer par-dessus la poutre effondrée"])
                self.assertIn(message, texte)
                self.assertEqual(r.joueur["position"], [4, 3])
                self.assertEqual(instant(r), 0)

    def test_sans_description_refus_de_la_donnee_pas_d_echelle(self):
        m = recharger(scene(forme=False))
        with self.assertRaisesRegex(ErreurMonde, "pas encore décrits") as exc:
            Moteur(m).preparer(passage())
        self.assertIn("poutre_conduite.passage=null", exc.exception.attendu)
        self.assertNotIn("échelle", str(exc.exception))
        r, texte = jouer(m, ["ramper sous la poutre effondrée"])
        self.assertIn("pas encore décrits", texte)
        self.assertEqual(r.joueur["position"], [4, 3])

    def test_objet_long_et_masse_portee_joueur_et_pnj(self):
        for qui in ("joueur", "marchand"):
            m = scene()
            m.objets["perche_test"] = objet("perche_test", "longue perche", "outil", qui,
                                           mobile=True, masse=2, longueur_cm=250)
            m = recharger(m)
            with self.assertRaisesRegex(ErreurMonde, "encombrant") as exc:
                conditions(m, "poutre_conduite", "dessous", qui)
            self.assertIn("perche_test.longueur_cm=250", exc.exception.attendu)
            m.objets["perche_test"].update(longueur_cm=100, masse=20)
            # Le moteur du passage lit aussi les objets contenus dans un sac porté.
            with self.assertRaisesRegex(ErreurMonde, "lourd"):
                conditions(m, "poutre_conduite", "dessous", qui)

    def test_enjambement_sans_jet_escalade_et_echec_recharge(self):
        m = scene()
        # Le dégagement est nul ; un petit obstacle s'enjambe sans jet.
        m.objets["poutre_conduite"]["passage"].update(hauteur_cm=50, degagement_cm=0)
        r, texte = jouer(m, ["passer par-dessus la poutre effondrée", "tenter"])
        self.assertIn("Pas de jet nécessaire", texte)
        self.assertIn("Tu enjambes", texte)
        self.assertEqual((r.joueur["position"], instant(r)), ([6, 3], 60))
        m = scene()
        for o in m.objets.values():
            if m.est_porte(o["id"]):
                o["longueur_cm"] = 20
        p = Moteur(m).preparer(passage(methode="dessus"))
        self.assertEqual((p.plans[0].stat, p.plans[0].dd), ("FOR", 10))
        with patch.object(Monde, "d20", return_value=1):
            texte = Moteur(m).executer(p)
        m = recharger(m)
        self.assertIn("ECHEC", texte)
        self.assertEqual((m.joueur["position"], instant(m)), ([4, 3], 180))

    def test_pas_de_sol_ni_case_occupee_ni_diagonale(self):
        m = scene()
        placer(m, "aubin", "echoppe", (6, 3))
        with self.assertRaisesRegex(ErreurMonde, "Quelqu'un"):
            Moteur(m).preparer(passage())
        m.joueur["position"] = [4, 2]
        with self.assertRaisesRegex(ErreurMonde, "côté"):
            Moteur(m).preparer(passage())

    def test_qualification_additive_visible_validee_sauvee(self):
        m = scene(forme=False)
        ajout = {"ajouts": [{"type": "qualification", "ancrage": "poutre_conduite", "passage": dict(FORME)}]}
        travail, texte, etablis = preparer_faits(m, ajout)
        self.assertNotIn("passage", m.objets["poutre_conduite"])
        r = recharger(travail)
        self.assertEqual(r.objets["poutre_conduite"]["passage"], FORME)
        self.assertIn("Dégagement dessous", texte)
        with self.assertRaisesRegex(ErreurMonde, "déjà établie"):
            preparer_faits(r, ajout)
        for mauvais in ({**FORME, "degagement_cm": 100}, {**FORME, "hauteur_cm": float("nan")}, {**FORME, "appuis": 1}):
            with self.assertRaises(ErreurMonde) as exc:
                valider_passage(m.objets["poutre_conduite"], mauvais)
            self.assertTrue(exc.exception.attendu)


class TrajetTests(unittest.TestCase):
    def test_pnj_passe_dessous_et_meme_laps_decoupe_recharge(self):
        m = corridor()
        chemin_ = trajet(m, "echoppe", (4, 3), lambda s, c: s == "antichambre",
                         passages=transitions(m, "marchand", descriptions_crues(m, "marchand")))
        self.assertEqual(chemin_[0][1], (6, 3))
        self.assertEqual(chemin_[0][2]["dixiemes"], 120)
        bloc, morceaux = recharger(m), recharger(m)
        Moteur(bloc).executer(Moteur(bloc).preparer(proposition("attendre", "30")))
        for _ in range(15):
            Moteur(morceaux).executer(Moteur(morceaux).preparer(proposition("tourner", "nord" if _ % 2 == 0 else "sud")))
            morceaux = recharger(morceaux)
        bloc = recharger(bloc)
        self.assertEqual(instant(bloc), instant(morceaux))
        self.assertEqual(etat_pnj(bloc), etat_pnj(morceaux))
        self.assertEqual(bloc.objets["marchand"]["lieu"], "antichambre")
        self.assertTrue(any("rampe sous" in c["texte"] for c in bloc.data["chronique"]))

    def test_le_plan_ne_devine_pas_la_forme_reelle(self):
        m = corridor()
        route = chemin(m, "marchand", "echoppe", "antichambre")
        self.assertIsNotNone(route)
        self.assertGreater(route[-1]["duree_trajet"], 120)
        # Forme vraie inchangée, croyance trop basse et trop haute : aucun passage cru.
        croire(m, "marchand", "poutre_conduite", "passage", {**FORME, "degagement_cm": 5, "hauteur_cm": 250}, "savoir")
        m = recharger(m)
        self.assertIsNone(chemin(m, "marchand", "echoppe", "antichambre"))
        # La géométrie n'est pas une croyance transmise par le nom de l'obstacle.
        del lire(m, "marchand")["croyances"]["poutre_conduite"]["passage"]
        self.assertEqual(descriptions_crues(m, "marchand"), {})
        self.assertIsNone(trajet(m, "echoppe", (4, 3), lambda s, c: s == "antichambre"))

    def test_cout_et_equipement_prevu_dans_la_recherche_et_sa_cle(self):
        from donjon.planification import Vue, depart, _entrees
        m = corridor()
        v = Vue(m, "marchand")
        e = depart(m, "marchand", v)
        route = v.route(e, "antichambre")
        self.assertIsNotNone(route)
        m.objets["perche_test"] = objet("perche_test", "perche", "outil", "echoppe", mobile=True, masse=1, longueur_cm=300)
        v = Vue(m, "marchand")
        e = depart(m, "marchand", v)
        self.assertIsNone(v.route(e.apres(portes=e.portes | {"perche_test"}), "antichambre"))
        avant = _entrees(v, {}, 10, 100)
        croire(m, "marchand", "poutre_conduite", "passage", {**FORME, "degagement_cm": 5}, "savoir")
        self.assertNotEqual(avant, _entrees(Vue(m, "marchand"), {}, 10, 100))
        self.assertTrue(m.objets["poutre_conduite"]["bloque_vue"])


if __name__ == "__main__":
    unittest.main()
