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
        o.setdefault("passage", dict(FORME))
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
                self.assertEqual(r.joueur["corps"]["vecu"]["activite"], "effort")
                self.assertTrue(r.objets[cible]["bloque_passage"])
                self.assertEqual(r.objets[cible].get("bloque_vue"), m.objets[cible].get("bloque_vue"))
                self.assertEqual(r.data["journal"][-1]["action"]["etapes"][0]["operation"], "passer_obstacle")
                r, sortie = jouer(r, ["examiner " + nom])
                self.assertIn(f"Dégagement dessous : {m.objets[cible]['passage']['degagement_cm']} cm", sortie)

    def test_commande_locale_attend_confirmation_et_ne_contacte_pas_le_mj(self):
        m = scene()
        self.assertEqual(analyser(m, "ramper sous la poutre effondrée"), passage())
        r, texte = jouer(m, ["ramper sous la poutre effondrée"])
        self.assertEqual(r.joueur["position"], [4, 3])
        self.assertIn("tenter", texte)
        r, texte = jouer(r, ["ramper sous la poutre effondrée", "tenter"])
        self.assertEqual(r.joueur["position"], [6, 3])
        self.assertIn("Tu passes", texte)

    def test_la_fiche_composee_compte_aussi_les_secondes_du_passage(self):
        m = scene()
        p = Moteur(m).preparer(sequence(etape("passer_obstacle", "poutre_conduite", methode="dessous"),
                                       etape("patienter")))
        self.assertIn("Durée totale prévue : 2 minutes 12 secondes", p.resume(m))
        self.assertEqual(p.dixiemes, 1320)
        self.assertEqual(m.joueur["position"], [4, 3])

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

    def test_qualification_ratee_puis_geste_le_joueur_lit_la_raison_du_monde(self):
        """Banc Luna `sous-obstacle-inconnu` : geste refusé (forme inconnue), qualification
        incohérente refusée par le moteur, puis le même geste : la raison du monde, jamais un
        message de la boucle du MJ, et rien n'est enregistré, après recharge."""
        geste = {"mode": "action", "texte": "", "faits": ["passages_obstacles"], "proposition": passage()}
        qualif = {"mode": "etablir_faits", "texte": "", "faits": ["passages_obstacles"],
                  "proposition": {"ajouts": [{"type": "qualification", "ancrage": "poutre_conduite",
                                              "passage": {**FORME, "degagement_cm": 30, "hauteur_cm": 20}}]}}
        question = "est-ce que je pourrais passer sous la poutre effondrée ?"
        # La qualification d'abord (aucun refus du monde encore) : le geste revenu suit son chemin.
        for saisie, reponses in ((question, [geste, qualif, geste]), ("je me faufile sous la poutre effondrée",
                                 [geste, qualif, geste]), (question, [qualif, geste, geste, geste])):
            with self.subTest(saisie=saisie, premier=reponses[0]["mode"]):
                m = recharger(scene(forme=False))
                r, texte = jouer(m, [saisie], [*reponses, geste, geste])
                texte = texte.split("Le MJ réfléchit…", 1)[1]  # la réponse, sans la légende du plan
                self.assertIn("pas encore décrits", texte)
                self.assertNotIn("correction des faits", texte)
                self.assertNotIn("échelle", texte)
                self.assertNotIn("passage", r.objets["poutre_conduite"])
                self.assertEqual((r.joueur["position"], instant(r)), ([4, 3], 0))

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

    def test_le_jet_du_joueur_a_la_meme_borne_de_caracteristique_que_le_pnj(self):
        from donjon.caractere import modificateur
        # À très faible FOR, trois malus ne descendent pas la caractéristique
        # sous 1 : le même socle vaut pour une étape et une action simple.
        for action in ("escalader", "pousser"):
            with self.subTest(action=action):
                m = scene()
                m.joueur["stats"]["FOR"] = 3
                m.joueur["besoins"].update(faim=95, repos=95, chaleur=95)
                m.objets["marchand"]["profil"]["caracteristiques"]["FOR"] = 3
                lire(m, "marchand")["besoins"].update(faim=95, repos=95, chaleur=95)
                self.assertEqual(modificateur(m, "joueur", "FOR"), -5)
                self.assertEqual(modificateur(m, "marchand", "FOR"), -5)
                if action == "escalader":
                    for o in m.objets.values():
                        if m.est_porte(o["id"]):
                            o["longueur_cm"] = 20
                    p = Moteur(m).preparer(passage(methode="dessus"))
                    jets = [15, *([20] * 20)]
                else:
                    m.joueur.update(position=[3, 3], orientation="sud")
                    placer(m, "aubin", "echoppe", (3, 4))
                    lire(m, "aubin")["libre"] = 10000
                    p = Moteur(m).preparer(proposition("pousser", "aubin", "sud"))
                    jets = [15, 8, *([20] * 20)]
                with patch.object(Monde, "d20", side_effect=jets):
                    texte = Moteur(m).executer(p)
                m = recharger(m)
                self.assertIn("REUSSITE", texte)
                if action == "escalader":
                    self.assertEqual(m.joueur["position"], [6, 3])
                else:
                    self.assertEqual(m.objets["aubin"]["position"], [3, 5])

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
    def test_un_raccourci_plus_rapide_garde_le_parcours_metrique_meme_avec_un_detour(self):
        from donjon.obstacles import metrique_necessaire
        from donjon.temps import PAS_JOUEUR, duree_pas
        m = corridor()
        # La cloison laisse un détour par le sud, mais le dessous au nord
        # économise du temps. La salle reste connexe : il faut aussi comparer les coûts.
        m.objets.pop("bloc_test_1")
        m.objets.pop("bloc_test_6")
        m.objets["bloc_test_3"] = objet("bloc_test_3", "bloc de pierre", "meuble", "echoppe",
                                       position=[5, 3], position_salle="echoppe", bloque_passage=True)
        croire(m, "marchand", "bloc_test_3", "lieu", "echoppe", "savoir", salle="echoppe", case=[5, 3])
        placer(m, "poutre_conduite", "echoppe", (5, 1))
        croire(m, "marchand", "poutre_conduite", "lieu", "echoppe", "savoir", salle="echoppe", case=[5, 1])
        m = recharger(m)
        ordinaire = trajet(m, "echoppe", (4, 1), lambda s, c: s == "echoppe" and c == (6, 1))
        self.assertIsNotNone(ordinaire)
        self.assertGreater(sum(duree_pas(PAS_JOUEUR, v) for _, _, _, v in ordinaire), 120)
        self.assertTrue(metrique_necessaire(m, "marchand"))
        avec = trajet(m, "echoppe", (4, 1), lambda s, c: s == "echoppe" and c == (6, 1),
                      passages=transitions(m, "marchand", descriptions_crues(m, "marchand")))
        self.assertEqual((avec[0][1], avec[0][2]["dixiemes"]), ((6, 1), 120))

    def test_domination_du_passage_et_case_de_depart_dans_la_recherche(self):
        from donjon import spatial
        from donjon.obstacles import metrique_necessaire
        from donjon.planification import Vue, _entrees
        for coupe in (False, True):
            with self.subTest(coupe=coupe):
                m = corridor() if coupe else scene()
                m.joueur.update(salle="antichambre", position=[6, 5])
                placer(m, "marchand", "echoppe", (4, 3))
                croire(m, "marchand", "poutre_conduite", "lieu", "echoppe", "savoir", salle="echoppe", case=[5, 3])
                croire(m, "marchand", "poutre_conduite", "passage", dict(FORME), "savoir")
                m = recharger(m)
                with patch.object(spatial, "VERIFICATION", 1):
                    self.assertEqual(metrique_necessaire(m, "marchand"), coupe)
                    self.assertEqual(metrique_necessaire(m, "marchand"), coupe)  # reprise vérifiée
                avant = _entrees(Vue(m, "marchand"), {}, 10, 100)
                placer(m, "marchand", "echoppe", (3, 3))
                m = recharger(m)
                apres = _entrees(Vue(m, "marchand"), {}, 10, 100)
                # Le modèle de recherche ne dépend plus de la case de départ.
                self.assertEqual(avant, apres)
                if not coupe:
                    # Un enjambement qui égale le détour au pas devient un
                    # raccourci pour une marche feutrée : l'allure entre dans la preuve.
                    bas = {**FORME, "hauteur_cm": 50, "degagement_cm": 0}
                    m.objets["poutre_conduite"]["passage"] = bas
                    croire(m, "marchand", "poutre_conduite", "passage", bas, "savoir")
                    self.assertFalse(metrique_necessaire(m, "marchand"))
                    self.assertTrue(metrique_necessaire(m, "marchand", 30))

    def test_le_pnj_rate_la_meme_escalade_sans_bond_et_on_l_entend(self):
        m = corridor()
        m.joueur.update(salle="echoppe", position=[6, 4], orientation="est")
        m.objets["poutre_conduite"]["passage"]["degagement_cm"] = 5
        croire(m, "marchand", "poutre_conduite", "passage",
               copy.deepcopy(m.objets["poutre_conduite"]["passage"]), "savoir")
        for o in m.objets.values():
            from donjon.spatial import porte_par
            if porte_par(m, o["id"], "marchand"):
                o["longueur_cm"] = 20
        # Un bruit survenu pendant l'attente, pas celui de l'initialisation à t=0.
        lire(m, "marchand")["libre"] = 5
        with patch.object(Monde, "d20", return_value=1):
            texte = Moteur(m).executer(Moteur(m).preparer(proposition("attendre", "1")))
        m = recharger(m)
        self.assertEqual(m.objets["marchand"]["position"], [4, 3])
        self.assertEqual(m.objets["marchand"]["corps"]["vecu"]["activite"], "effort")
        self.assertGreaterEqual(lire(m, "marchand")["libre"], 180)
        self.assertTrue(any("ne parvient pas à escalader" in c["texte"] for c in m.data["chronique"]))
        self.assertTrue(any(b["auteur"] == "marchand" and b["nature"] == "geste" for b in m.data["bruits"]))
        self.assertIn("Tu entends", texte)

    def test_le_prix_d_un_temps_fractionnaire_reste_des_pieces_entieres(self):
        from donjon.planification import prix_tache, SALAIRE
        from donjon.deliberation import retenir_refus
        for peine in (float(SALAIRE), SALAIRE + .15):
            with self.subTest(peine=peine):
                m = corridor()
                prix = prix_tache(peine)
                self.assertIs(type(prix), int)
                self.assertEqual(prix, 1 if peine == SALAIRE else 2)
                retenir_refus(m, "marchand", "aubin", "engager", "cher", objet="brasero", prix=prix,
                              tache={"objet": "brasero", "allume": True})
                r = recharger(m)
                self.assertIs(type(lire(r, "marchand")["refus"][-1]["prix"]), int)

    def test_une_sortie_mesuree_garde_sa_case_et_le_pnj_ouvre_sa_porte(self):
        from donjon.passage import raison_de_rester
        from donjon.spatial import _case_interieure
        for scenario, qui, salle, direction, obstacle in (
                ("auberge", "odile", "cuisine", "nord", "table_cuisine"),
                ("mine", "remy", "baraquement", "nord", "table")):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, "fixe")
                calme(m, *[i for i, o in m.objets.items() if o.get("profil")])
                sortie = m.data["salles"][salle]["sorties"][direction]
                case = _case_interieure(m, salle, sortie)
                placer(m, qui, salle, case)
                porte = m.objets[sortie["porte"]]
                porte.update(ouverte=False, verrouillee=False)
                croire(m, qui, porte["id"], "verrouillee", False, "essai")
                o = m.objets[obstacle]
                croire(m, qui, obstacle, "lieu", o["lieu"], "savoir", salle=o["lieu"], case=list(o["position"]))
                croire(m, qui, obstacle, "passage", copy.deepcopy(o["passage"]), "savoir")
                intention(m, qui, [{"operation": "aller", "lieu": sortie["vers"]}])
                m = recharger(m)
                from donjon.obstacles import parcours_cru
                route = parcours_cru(m, qui, salle).routes[sortie["vers"]]
                self.assertIn("duree_trajet", route[0])
                self.assertEqual(_case_interieure(m, salle, route[0]), case)
                self.assertEqual(raison_de_rester(m, qui), "geste")
                Moteur(m).executer(Moteur(m).preparer(proposition("attendre", "30")))
                m = recharger(m)
                self.assertTrue(m.objets[porte["id"]]["ouverte"])
                self.assertEqual(m.objets[qui]["lieu"], sortie["vers"])

    def test_scenes_luna_preparees_et_donnees_reelles_apres_recharge(self):
        import json
        from tools.banc_parties import preparer
        for f in sorted((Path(__file__).parent / "data" / "bancs").glob("sous-obstacle-*.json")):
            with self.subTest(script=f.stem), tempfile.TemporaryDirectory() as tmp:
                sauvegarde = Path(tmp) / "partie.json"
                preparer(json.loads(f.read_text(encoding="utf-8")), sauvegarde)
                m = Monde.charger(sauvegarde)
                cible = "lit_chaud" if "enjamber" in f.stem else "table_longue" if "auberge" in f.stem else "poutre_conduite"
                if "inconnu" in f.stem:
                    self.assertNotIn("passage", m.objets[cible])
                elif "trop-bas" in f.stem:
                    with self.assertRaisesRegex(ErreurMonde, "trop bas"):
                        Moteur(m).preparer(passage(cible))
                elif "trop-haut" in f.stem:
                    with self.assertRaisesRegex(ErreurMonde, "trop haut"):
                        Moteur(m).preparer(passage(cible, "dessus"))
                elif "encombre" in f.stem:
                    with self.assertRaisesRegex(ErreurMonde, "encombrant"):
                        Moteur(m).preparer(passage(cible))
                elif "enjamber" in f.stem:
                    p = Moteur(m).preparer(passage(cible, "dessus"))
                    self.assertEqual(p.plans[0].dixiemes, 60)
                    Moteur(m).executer(p)
                    r = recharger(m)
                    self.assertEqual(r.joueur["position"], [2, 0])
                else:
                    self.assertEqual(Moteur(m).preparer(passage(cible)).plans[0].dixiemes, 120)

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
        from donjon import planification, spatial
        from donjon.planification import Vue, depart, _entrees
        m = corridor()
        v = Vue(m, "marchand")
        e = depart(m, "marchand", v)
        route = v.route(e, "antichambre")
        self.assertIsNotNone(route)
        with patch.object(planification, "VERIFIER", True), patch.object(spatial, "VERIFICATION", 1):
            trouve = planification.aller(m, "marchand", "antichambre")
            self.assertIsNotNone(trouve)
            self.assertEqual(planification.aller(m, "marchand", "antichambre"), trouve)
        m.objets["perche_test"] = objet("perche_test", "perche", "outil", "echoppe", mobile=True, masse=1, longueur_cm=300)
        v = Vue(m, "marchand")
        e = depart(m, "marchand", v)
        self.assertIsNone(v.route(e.apres(portes=e.portes | {"perche_test"}), "antichambre"))
        # Même fermeture par le vrai planificateur, puis reprise après recharge,
        # sous ses deux contrôles de mémoire et de recherche complète.
        m.objets["perche_test"]["lieu"] = "marchand"
        croire(m, "marchand", "perche_test", "lieu", "marchand", "savoir", salle=None, case=None)
        m = recharger(m)
        with patch.object(planification, "VERIFIER", True), patch.object(spatial, "VERIFICATION", 1):
            self.assertIsNone(planification.aller(m, "marchand", "antichambre"))
            self.assertIsNone(planification.aller(m, "marchand", "antichambre"))
        avant = _entrees(Vue(m, "marchand"), {}, 10, 100)
        croire(m, "marchand", "poutre_conduite", "passage", {**FORME, "degagement_cm": 5}, "savoir")
        self.assertNotEqual(avant, _entrees(Vue(m, "marchand"), {}, 10, 100))
        self.assertTrue(m.objets["poutre_conduite"]["bloque_vue"])


def fuite_joueur(forme=FORME, porte=None):
    """Le couloir coupé : seule la poutre mène à la sortie connue ; Brune frappe Corvus de face."""
    from donjon import combat
    m = corridor()
    croire(m, "marchand", "poutre_conduite", "passage", dict(forme), "savoir")
    m.objets["poutre_conduite"]["passage"] = dict(forme)
    placer(m, "marchand", "crypte", (2, 2))
    placer(m, "brune", "echoppe", (3, 3))
    m.objets["brune"]["orientation"] = "est"
    m.joueur.update(salle="echoppe", position=[4, 3], orientation="ouest")
    # Ce que Corvus porte, décrit : sans longueur, un objet compte pour une case (``conditions``).
    for i, longueur in (("briquet", 8), ("lanterne", 30), ("cire", 10), ("couteau", 25)):
        m.objets[i]["longueur_cm"] = longueur
    if porte:
        m.objets[porte] = objet(porte, "perche", "outil", "joueur", mobile=True, masse=1, longueur_cm=300)
    m.data.setdefault("exploration", {}).setdefault("echoppe", []).append([8, 3])
    percevoir_tous(m)
    with patch.object(Monde, "d20", side_effect=[20, 1]):
        combat.frapper(m, "brune", "joueur")
    return recharger(m)


class FuiteTests(unittest.TestCase):
    """La fuite (force 4c) suit la même arête de trajet que le passage et la marche des PNJ."""

    def test_le_joueur_fuit_sous_ou_par_dessus_l_obstacle_apres_recharge(self):
        bas = {**FORME, "degagement_cm": 5}
        for nom, forme, jet, passe in (("ramper", FORME, 1, True), ("escalader", bas, 20, True),
                                       ("escalade manquée", bas, 1, False)):
            with self.subTest(nom):
                m = fuite_joueur(forme)
                avant = copy.deepcopy(m.data)
                p = Moteur(m).preparer(proposition("fuir"))
                self.assertEqual(m.data, avant)
                if nom == "ramper":
                    self.assertIn("en rampant sous la poutre effondrée", p.titre)
                    self.assertEqual(p.dixiemes, 120 + 3 * 15 + 20)  # demi-tour initial réel
                else:
                    self.assertIn("en escaladant la poutre effondrée", p.titre)
                    self.assertIn("jet de FOR contre 10", p.titre)
                debut = instant(m)
                with patch.object(Monde, "d20", return_value=jet):
                    texte = Moteur(m).executer(p)
                m = recharger(m)
                self.assertTrue(m.objets["poutre_conduite"]["bloque_passage"])
                self.assertTrue(m.objets["poutre_conduite"]["bloque_vue"])
                if passe:
                    self.assertEqual(m.joueur["salle"], "antichambre")
                    self.assertIn("Tu as gagné une autre salle.", texte)
                    self.assertIn("rampant sous" if nom == "ramper" else "escalades", texte)
                    self.assertTrue(m.data["journal"][-1]["reussite"])
                else:
                    # Le temps et l'effort sont dépensés, Corvus reste de ce côté, tourné vers l'obstacle.
                    self.assertEqual((m.joueur["salle"], m.joueur["position"]), ("echoppe", [4, 3]))
                    self.assertEqual(m.joueur["orientation"], "est")
                    self.assertGreaterEqual(instant(m) - debut, 180)
                    self.assertIn("ECHEC", texte)
                    self.assertFalse(m.data["journal"][-1]["reussite"])

    def test_sans_forme_ou_trop_encombre_aucune_fuite_par_l_obstacle(self):
        for nom, m in (("forme inconnue", fuite_joueur()), ("perche portée", fuite_joueur(porte="perche_test"))):
            with self.subTest(nom):
                if nom == "forme inconnue":
                    del m.objets["poutre_conduite"]["passage"]
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as refus:
                    Moteur(m).preparer(proposition("fuir"))
                self.assertIn("sortie connue", str(refus.exception))
                self.assertNotIn("échelle", str(refus.exception))
                self.assertTrue(refus.exception.attendu)
                self.assertEqual(m.data, avant)

    def test_chercher_quelqu_un_compte_la_route_comme_la_recherche(self):
        from donjon.planification import Vue, depart, _chercher, CHERCHER
        from donjon.obstacles import cout_route
        m = corridor()
        v = Vue(m, "marchand")
        e = depart(m, "marchand", v)
        route = v.route(e, "antichambre")
        self.assertGreater(cout_route(route), 0)
        self.assertLess(cout_route(route), 1)
        self.assertIn(("antichambre", cout_route(route, e.orientation)), v.allers(e, frozenset()))
        lire(m, "marchand")["visites"].update({s: 999 for s in m.data["salles"] if s != "antichambre"})
        trouve = _chercher(v, e, "ilse")
        self.assertAlmostEqual(trouve[1], trouve[4] + CHERCHER)
        self.assertGreater(trouve[4], cout_route(route, e.orientation))  # approche au centre et inspection

    def test_le_pnj_fuit_sous_l_obstacle_par_le_meme_trajet_apres_recharge(self):
        from donjon import combat, defense
        from tests.support import regarder as orienter
        for forme in (True, False):
            with self.subTest(forme=forme):
                m = corridor(forme)
                placer(m, "brune", "echoppe", (3, 3))
                # Un Gorm faible et sans courage : la fuite l'emporte sur la riposte.
                m.objets["marchand"]["profil"]["valeurs"]["courage"] = 0
                m.objets["marchand"]["profil"]["caracteristiques"]["FOR"] = 3
                orienter(m, "marchand", "brune")
                orienter(m, "brune", "marchand")
                percevoir_tous(m)
                with patch.object(Monde, "d20", side_effect=[20, 1]):
                    combat.frapper(m, "brune", "marchand")
                self.assertEqual(defense.choisir(m, "marchand")[0]["type"], "fuir" if forme else "riposter")
                for _ in range(3):
                    Moteur(m).executer(Moteur(m).preparer(proposition("attendre", "15")))
                    m = recharger(m)
                rampe = any("rampe sous la poutre" in c["texte"] for c in m.data["chronique"])
                # Sans forme crue, le plan par salles ne connaît pas ce passage : Gorm reste coupé.
                self.assertEqual((m.objets["marchand"]["lieu"], rampe),
                                 ("antichambre", True) if forme else ("echoppe", False))


if __name__ == "__main__":
    unittest.main()
