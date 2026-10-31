"""G13 : admettre les inconnues, conserver l'établi et reprendre le geste."""
import copy
import unittest

from donjon.atelier import nouveau_atelier
from donjon.coherence_physique import propositions
from donjon.faits_locaux import preparer_faits
from donjon.matiere import DIMENSIONS
from donjon.monde import ErreurMonde
from donjon.moteur import proposition
from donjon.operations import etape, sequence
from donjon.rendu import decrire, regarder
from donjon.scene import scene_percue
from tests.test_audits_attendu import jouer
from tests.test_assemblage import assembler
from tests.test_fouille_faits import faits, revue
from tests.test_matiere import planches, relais_avec_planches
from tests.test_messages_decoupage import vivre
from tests.test_relances_luna import action
from tests.test_tensions import recharger


def description(p):
    return {**copy.deepcopy(p), "nom_piece": p.get("nom_piece", ""),
            "dimensions": {d: p["dimensions"].get(d, 0) for d in DIMENSIONS}}


def qualification(cible, physique, suite=None):
    return faits(dict(type="qualification", ancrage=cible, physique=physique), suite)


PHYSIQUE_OK = {"jugements": [{"compatible": True, "motif": ""}]}


def decoupe(cible, outil="hache", longueur=50):
    return dict(action="decouper", cible=cible, outil=outil, longueur_cm=longueur, justification="")


class QualificationTests(unittest.TestCase):
    def verifier_laps(self, monde, cible):
        copie = recharger(monde)
        a, _ = vivre(copie.copier(), [20])
        b, _ = vivre(copie.copier(), [5] * 4)
        self.assertEqual(a.data, b.data)
        self.assertEqual((regarder(a), scene_percue(a), decrire(a, cible, detail=True)),
                         (regarder(b), scene_percue(b), decrire(b, cible, detail=True)))

    def test_planches_du_relais_qualification_prelevement_et_recharge(self):
        m = relais_avec_planches()
        # Prémisse : Corvus dispose légalement du bois et porte une hache.
        m.objets["planches"]["proprietaire"] = "joueur"
        m.objets["hache"] = copy.deepcopy(nouveau_atelier().objets["hache"])
        m.objets["hache"]["lieu"] = "joueur"
        m = recharger(m)
        p = sequence(etape("prelever", "planches", "joueur"))
        r = qualification("planches", planches())
        avant = copy.deepcopy(m.data)
        monde, texte, appels = jouer(m, "mj je prends une planche du tas",
                                    [r, revue(r), PHYSIQUE_OK, action(p)], [], suite=("tenter",))
        self.assertEqual(m.data, avant)
        self.assertEqual(monde.objets["planches_1"]["lieu"], "joueur")
        self.assertEqual(monde.objets["planches_1"]["physique"]["matiere"], "bois")
        self.assertIn("Compris :", texte)
        self.assertEqual([f for f, _ in appels].count("auditer_capacites"), 1)
        self.assertEqual([f for f, _ in appels].count("auditer_narration"), 0)
        self.verifier_laps(monde, "planches_1")

    def test_planche_qualifiee_decoupee_et_reprise_sans_repetition(self):
        m = nouveau_atelier()
        m.data["mode_cases"] = False
        o = m.objets["perche_1"]
        o["nom"], o["materiau"] = "planche", ""
        physique = description(o.pop("physique"))
        physique["dimensions"].update(diametre_cm=0, largeur_cm=20, epaisseur_cm=1)
        o.pop("diametre_cm")
        o.pop("charge_jeu_kg")
        # Une planche ordinaire de section rectangulaire, même masse et longueur.
        p = decoupe("perche_1")
        r = qualification("perche_1", physique)
        masse = o["masse"]
        monde, texte, appels = jouer(m, "mj je coupe 50 cm de ma planche",
                                    [r, revue(r), PHYSIQUE_OK, action(p)], [], suite=("tenter",))
        self.assertEqual(monde.objets["perche_1"]["longueur_cm"], 250)
        self.assertEqual(monde.objets["perche_1_1"]["longueur_cm"], 50)
        self.assertAlmostEqual(sum(monde.objets[i]["masse"] for i in ("perche_1", "perche_1_1")), masse)
        self.assertIn("bois", decrire(monde, "perche_1_1", detail=True))
        self.assertIn("50 cm", texte)
        self.assertEqual([f for f, _ in appels].count("auditer_capacites"), 1)
        monde, texte, appels = jouer(recharger(monde), "mj je recoupe 50 cm de ma planche",
                                    [action(p)], [], suite=("tenter",))
        self.assertEqual(monde.objets["perche_1"]["longueur_cm"], 200)
        self.assertEqual([f for f, _ in appels], ["repondre_au_joueur", "auditer_action"])
        self.verifier_laps(monde, "perche_1")

    def test_ficelle_qualifiee_avant_les_noeuds_puis_decoupee_sans_requalification(self):
        for suite_jointe in (False, True):
            with self.subTest(suite_jointe=suite_jointe):
                m = nouveau_atelier()
                m.data["mode_cases"] = False
                o = m.objets["ficelle"]
                physique = description(o.pop("physique"))
                o.pop("ressource")
                o["materiau"] = ""
                o["lieu"] = "joueur"
                p = assembler(["perche_1", "perche_2"], "perche_3")
                r = qualification("ficelle", physique, p if suite_jointe else None)
                sorties = [r, revue(r), PHYSIQUE_OK] + ([] if suite_jointe else [action(p)])
                monde, texte, appels = jouer(m, "mj je noue les barreaux de mon échelle avec la ficelle",
                                            sorties, [], suite=("tenter",))
                self.assertTrue(any(o.get("assemblage") for o in monde.objets.values()))
                self.assertEqual(monde.objets["ficelle"]["longueur_cm"], 1040)
                self.assertEqual(monde.objets["ficelle"]["materiau"], "fibres")
                self.assertIn("fibres", decrire(monde, "ficelle", detail=True))
                self.assertIn("Compris :", texte)
                self.assertEqual([f for f, _ in appels].count("auditer_capacites"), 1)
                self.assertEqual(len(appels), 4 if suite_jointe else 5)
                monde, texte, appels = jouer(recharger(monde), "mj je coupe 50 cm de ficelle",
                                            [action(decoupe("ficelle"))], [], suite=("tenter",))
                self.assertEqual(monde.objets["ficelle"]["longueur_cm"], 990)
                self.assertEqual(monde.objets["ficelle_1"]["physique"]["matiere"], "fibres")
                self.assertEqual([f for f, _ in appels], ["repondre_au_joueur", "auditer_action"])
                self.verifier_laps(monde, "ficelle")

    def test_une_grandeur_partielle_etablie_ne_se_remplace_pas(self):
        for champ, valeur in (("longueur_cm", 250), ("diametre_cm", 4),
                              ("largeur_cm", 8), ("charge_jeu_kg", 80), ("ressource", "lien")):
            with self.subTest(champ=champ):
                m = nouveau_atelier()
                m.data["mode_cases"] = False
                o = m.objets["perche_1"]
                physique = description(o.pop("physique"))
                o[champ] = valeur
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as refus:
                    preparer_faits(m, {"ajouts": qualification("perche_1", physique)["proposition"]["ajouts"]})
                self.assertIn("perche_1." + champ, refus.exception.attendu)
                self.assertIn("reçu", refus.exception.attendu)
                self.assertIn("accepté", refus.exception.attendu)
                self.assertEqual(m.data, avant)
                self.assertEqual(recharger(m).data, avant)

    def test_perche_de_fer_de_200g_refusee_avant_revue_et_sauvegarde(self):
        m = nouveau_atelier()
        m.data["mode_cases"] = False
        o = m.objets["perche_1"]
        physique = description(o.pop("physique"))
        o["materiau"] = physique["matiere"] = "fer"
        o["masse"] = 0.2
        # Aucune charge encore établie ; la seule cause est la masse incompatible.
        o.pop("charge_jeu_kg")
        r = qualification("perche_1", physique)
        monde, texte, appels = jouer(m, "mj je décris ma perche de fer",
                                    [r, action(proposition("examiner", "perche_1"))], [])
        self.assertNotIn("physique", monde.objets["perche_1"])
        self.assertEqual(monde.objets["perche_1"]["masse"], 0.2)
        self.assertFalse(any(f == "auditer_capacites" for f, _ in appels))
        retours = [e["faits"]["retour_moteur"] for f, e in appels
                   if "retour_moteur" in e.get("faits", {})]
        self.assertIn("perche_1 pèse 0.2 kg", retours[0]["attendu"])
        self.assertNotIn(retours[0]["attendu"], texte)
        self.assertIn(decrire(monde, "perche_1", detail=True), texte)

    def test_mesures_connues_refusees_dans_la_boucle_et_rendues_apres_recharge(self):
        for cible in ("perche_1", "ficelle"):
            with self.subTest(cible=cible):
                m = nouveau_atelier()
                m.data["mode_cases"] = False
                o = m.objets[cible]
                o["lieu"] = "joueur"
                physique = description(o.pop("physique"))
                avant = copy.deepcopy(o)
                physique["dimensions"]["longueur_cm"] /= 2
                r = qualification(cible, physique, decoupe(cible))
                monde, texte, appels = jouer(m, "mj je coupe 50 cm de cet objet",
                    [r, action(proposition("examiner", cible))], [])
                self.assertEqual(monde.objets[cible], avant)
                retour = appels[1][1]["faits"]["retour_moteur"]
                self.assertIn(cible + ".longueur_cm", retour["attendu"])
                self.assertNotIn(retour["attendu"], texte)
                self.assertFalse(any(f == "auditer_capacites" for f, _ in appels))
                self.assertIn(decrire(recharger(monde), cible, detail=True), texte)
                self.assertIn(f"Longueur disponible : {avant['longueur_cm'] / 100:g} m", texte)

    def test_revue_recoit_aussi_les_mesures_et_l_etat_deja_etablis(self):
        objet = dict(id="perche", nom="perche", longueur_cm=300, diametre_cm=5,
                     charge_jeu_kg=110, integrite=4, maximum=10, masse=4)
        entree = propositions(qualification("perche", planches(pieces=1)), {"objet:perche": objet})[0]
        for champ, valeur in objet.items():
            self.assertEqual(entree["objet"][champ], valeur)
        self.assertEqual(entree["champs_a_etablir"], ["physique"])

    def test_revue_negative_interdit_l_admission_et_l_usage_sur_deux_matieres(self):
        for cible in ("perche_1", "ficelle"):
            with self.subTest(cible=cible):
                m = nouveau_atelier()
                m.data["mode_cases"] = False
                m.objets[cible]["lieu"] = "joueur"
                physique = description(m.objets[cible].pop("physique"))
                r = qualification(cible, physique, decoupe(cible))
                monde, texte, appels = jouer(m, "mj je coupe 50 cm de cet objet", [r, revue(r),
                    {"jugements": [{"compatible": False, "motif": "Description incompatible avec l'objet."}]},
                    action(proposition("examiner", cible))], [])
                self.assertNotIn("physique", monde.objets[cible])
                self.assertNotIn(cible + "_1", monde.objets)
                self.assertEqual(monde.objets[cible]["masse"], m.objets[cible]["masse"])
                refus = appels[3][1]["controle_narratif"][0]
                self.assertEqual(refus["partie"], "qualification")
                self.assertIn(cible, refus["attendu"])
                self.assertNotIn(refus["attendu"], texte)
                self.assertIn(decrire(recharger(monde), cible, detail=True), texte)

    def test_un_autre_obstacle_apres_admission_est_affiche_et_la_propriete_reste_acquise(self):
        m = nouveau_atelier()
        m.data["mode_cases"] = False
        physique = description(m.objets["perche_1"].pop("physique"))
        r = qualification("perche_1", physique)
        p = decoupe("perche_1", outil="couteau")
        monde, texte, appels = jouer(m, "mj je coupe 50 cm de la perche au couteau",
                                    [r, revue(r), PHYSIQUE_OK, action(p), action(p)], [])
        self.assertIn("physique", monde.objets["perche_1"])
        self.assertEqual(monde.objets["perche_1"]["longueur_cm"], 300)
        self.assertIn("Il faut un outil adapté", texte)
        self.assertEqual([f for f, _ in appels].count("auditer_capacites"), 1)
        self.assertIn("3 m", decrire(recharger(monde), "perche_1", detail=True))


if __name__ == "__main__":
    unittest.main()
