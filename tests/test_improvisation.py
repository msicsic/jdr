import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition as action
from donjon.improvisation import proposition, issue, effet
from donjon.mj import MJOpenAI
from donjon.rendu import decrire
from donjon.esprits import dernier_son, lire


def chant():
    return proposition("Fredonner une chanson", issue("Tu fredonnes quelques mesures.",
                       [effet("son", "joueur", texte="voix_melodique", valeur=1)]), bruit=1)


def marque():
    return proposition("Graver un repère", issue("Tu traces une flèche sur le bois.", [effet("marquer", "perche_1", texte="flèche vers le nord")]),
                       cibles=["perche_1"], outil="couteau", approche="manipulation", minutes=2)


def jongler():
    return proposition("Jongler avec une clé", issue("Tu rattrapes la clé."), issue("La clé tombe au sol.", [effet("deplacer", "cle", "antichambre")]),
                       cibles=["cle"], approche="adresse", stat="DEX", difficulte=12)


def reponse(p):
    return {"mode": "action", "texte": "", "faits": ["improvisation"], "proposition": p}


class ImprovisationTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_atelier()
        self.moteur = Moteur(self.m)

    def test_geste_sans_jet_purete_et_evenement_persistant(self):
        p = proposition("S'étirer", issue("Tu étires tes bras et délies tes épaules."))
        avant = copy.deepcopy(self.m.data)
        plan = self.moteur.preparer(p, "MJ")
        self.assertEqual(self.m.data, avant)
        self.assertFalse(plan.stat)
        self.assertIn("Geste", plan.resume(self.m))
        self.assertNotIn("S'étirer", plan.resume(self.m))
        with patch.object(Monde, "d20", side_effect=AssertionError("Sans dé")):
            texte = self.moteur.executer(plan)
        self.assertIn("geste", texte)
        self.assertNotIn("S'étirer", texte)
        self.assertNotIn("délies", texte)
        self.assertEqual(self.m.data["minutes"], 1)
        self.assertEqual(self.m.joueur["pv"], 18)
        self.assertEqual(self.m.data["gestes_improvises"][-1]["approche"], "expression")
        self.assertNotIn("intention", self.m.data["gestes_improvises"][-1])
        self.assertNotIn("S'étirer", str(self.m.data["journal"]))

    def test_son_entendu_sans_reponse_inventee_et_isolation(self):
        self.moteur.executer(self.moteur.preparer(chant()))
        self.assertFalse(self.m.data["sons"][-1]["auditeurs"])
        from donjon.monde import nouveau_monde
        crypte = nouveau_monde()
        # Un rythme frappé dans l'antichambre : Gorm, dans l'échoppe, l'entend sans le voir (l'ouïe
        # commune, ``ouie.SONS`` : un son franc comme un fracas) et le retient, sans rien inventer.
        rythme = proposition("Taper des mains", issue("Un rythme.",
            [effet("son", "joueur", texte="corps_rythmique", valeur=2)]), bruit=2)
        Moteur(crypte).executer(Moteur(crypte).preparer(rythme))
        self.assertEqual(crypte.data["sons"][-1]["auditeurs"], ["marchand"])
        self.assertEqual({k: dernier_son(crypte, "marchand")[k] for k in ("salle", "nature")},
                         {"salle": "antichambre", "nature": "bruyant"})
        self.assertIsNone(lire(crypte, "marchand")["intention"])
        self.assertFalse(crypte.data["engagements"])

    def test_forme_sonore_structuree_et_souvenir_apres_rechargement(self):
        from donjon.monde import nouveau_monde
        from donjon.dialogues import interlocuteurs
        m = nouveau_monde()
        m.joueur["salle"] = "echoppe"
        moteur = Moteur(m)
        chant_texte = moteur.executer(moteur.preparer(chant()))
        self.assertIn("notes de ta voix", chant_texte)
        frappe = proposition("Taper des mains", issue("La porte répond au rythme.",
            [effet("son", "joueur", texte="corps_rythmique", valeur=2)]), bruit=2)
        texte = moteur.executer(moteur.preparer(frappe))
        self.assertIn("rythme avec ton corps", texte)
        self.assertNotIn("La porte répond", texte)
        avec_texte_libre = proposition("Frapper des mains", issue("Un bruit retentit.", [
            effet("son", "joueur", texte="Une cloche cachée répond", valeur=1)]), bruit=1)
        with self.assertRaisesRegex(ErreurMonde, "forme sonore"):
            moteur.preparer(avec_texte_libre)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "sons.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual([s["forme"] for s in reprise.data["sons"][-2:]],
                         ["voix_melodique", "corps_rythmique"])
        # Gorm le voit faire : ce qu'il voit n'a pas besoin de l'ouïe, il n'en garde aucun bruit.
        self.assertEqual(reprise.data["sons"][-1]["auditeurs"], ["marchand"])
        self.assertIsNone(interlocuteurs(reprise)["marchand"]["dernier_son_entendu"])

    def test_marque_cree_detail_examinable_et_sauvegarde(self):
        avant = copy.deepcopy(self.m.data)
        plan = self.moteur.preparer(marque())
        self.assertEqual(self.m.data, avant)
        self.moteur.executer(plan)
        self.assertEqual(self.m.objets["marque_1"]["lieu"], "perche_1")
        self.assertIn("flèche vers le nord", decrire(self.m, "marque_1", detail=True))
        self.assertIn("marque 1", decrire(self.m, "perche_1", detail=True))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"m.json"
            self.m.sauver(p)
            charge = Monde.charger(p)
            self.assertEqual(charge.data, self.m.data)
            self.assertIn("flèche vers le nord", decrire(charge, "marque_1", detail=True))

    def test_marquer_sans_outil_ou_sur_pnj_interdit(self):
        for cas in ("outil", "pnj", "inaccessible", "noir"):
            with self.subTest(cas=cas):
                p = marque()
                m = self.m.copier()
                if cas == "outil": p["outil"] = ""
                if cas == "pnj": p["reussite"]["effets"][0]["cible"] = "marchand"
                if cas == "inaccessible": m.objets["perche_1"]["lieu"] = "crypte"
                if cas == "noir": m.data["salles"]["cour"]["lumiere_naturelle"] = 0
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde): Moteur(m).preparer(p)
                self.assertEqual(m.data, avant)

    def test_echec_deplace_reellement_et_dd_memorisee(self):
        from donjon.monde import nouveau_monde
        m = nouveau_monde()
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(action("prendre", "cle")))
        plan = moteur.preparer(jongler())
        self.assertIn("geste concernant la clé", plan.resume(m))
        self.assertNotIn("Jongler", plan.resume(m))
        with patch.object(Monde, "d20", return_value=1):
            t = moteur.executer(plan)
        self.assertEqual(m.objets["cle"]["lieu"], "antichambre")
        self.assertIn("posée au sol", t)
        moteur.executer(moteur.preparer(action("prendre", "cle")))
        p = jongler()
        p["difficulte"] = 18
        self.assertEqual(moteur.preparer(p).dd, 12)

    def test_pas_de_contournement_vol_attaches_poids_teleportation(self):
        from donjon.monde import nouveau_monde
        for cible, salle, destination in (("crochets", "echoppe", "joueur"), ("porte", "antichambre", "joueur"),
                                         ("perche_1", "cour", "crypte"), ("perche_1", "cour", "joueur")):
            with self.subTest(cible=cible, destination=destination):
                m = self.m.copier() if salle == "cour" else nouveau_monde()
                m.joueur["salle"] = salle
                if cible == "perche_1" and destination == "joueur": m.objets[cible]["masse"] = 99
                p = proposition("Déplacer", issue("Tu déplaces l'objet.", [effet("deplacer", cible, destination)]), cibles=[cible])
                with self.assertRaises(ErreurMonde): Moteur(m).preparer(p)

    def test_consequences_bornees_et_jet_obligatoire_pour_blessure(self):
        for pv, effets, stat in ((18, [effet("blesser", "joueur", valeur=4)], "DEX"),
                                (2, [effet("blesser", "joueur", valeur=2)], "DEX"),
                                (18, [effet("blesser", "joueur", valeur=2)]*2, "DEX"),
                                (18, [effet("blesser", "joueur", valeur=1)], "")):
            m = self.m.copier()
            m.joueur["pv"] = pv
            p = proposition("Faire un effort", issue("Tu te cognes.", effets), issue("Tu renonces.") if stat else None,
                            approche="effort", stat=stat, difficulte=12 if stat else 0)
            with self.assertRaises(ErreurMonde): Moteur(m).preparer(p)

    def test_plan_mute_et_revision_revalides(self):
        plan = self.moteur.preparer(chant())
        plan.effets = [("payer", "crochets", -100)]
        self.moteur.executer(plan)
        self.assertEqual(self.m.joueur["or"], 24)
        with self.assertRaises(ErreurMonde): self.moteur.executer(plan)

    def test_refus_impossible_reexamine_intention_sans_regle_de_mot_cle(self):
        refus = reponse(action("impossible", justification="Je ne vois pas de voie."))
        with patch.object(MJOpenAI, "_appeler", side_effect=[refus, reponse(chant())]) as api, \
             patch.object(MJOpenAI, "_appeler_brut", return_value={"conforme": True, "motif": "", "perimetre": "sens", "evenements_requis": ["son"]}):
            sortie = MJOpenAI().echanger(self.m, "je chante")
        self.assertEqual(api.call_count, 2)
        self.assertEqual(sortie["proposition"], chant())
        self.assertEqual(self.m.data["revision"], 0)

    def test_question_sans_action_et_corrections_bornees(self):
        # Une question sur un geste le propose : préparé, jamais exécuté par cet échange.
        with (patch.object(MJOpenAI, "_appeler", return_value=reponse(chant())) as api,
              patch.object(MJOpenAI, "_auditer_action")):
            sortie = MJOpenAI().echanger(self.m, "Est-ce que je peux chanter ?")
        self.assertEqual(api.call_count, 1)
        self.assertEqual(sortie["mode"], "action")
        self.assertEqual(self.m.data["revision"], 0)
        invalide = chant()
        invalide["minutes"] = 500
        # Un refus de forme (une borne dépassée) reçoit sa correction à part, en plus de la correction
        # ordinaire : trois propositions au plus, puis une demande de précision moteur (G2).
        with patch.object(MJOpenAI, "_appeler", side_effect=[reponse(invalide), reponse(invalide), reponse(invalide),
                                                         ErreurMonde("narration indisponible")]) as api, \
             patch.object(MJOpenAI, "_appeler_brut", return_value={"conforme": True, "motif": "", "perimetre": "sens"}):
            sortie = MJOpenAI().echanger(self.m, "je chante")
        self.assertEqual(api.call_count, 3)
        self.assertEqual(sortie["mode"], "dialogue")
        self.assertNotIn("sort des limites", sortie["texte"])

    def test_console_applique_et_sauve_geste_sans_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"partie.json"
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                 patch("builtins.input", side_effect=["je fredonne pour passer le temps", "quitter"]), \
                 patch("jeu.MJ.echanger", return_value=reponse(chant())), \
                 patch("jeu.MJ.raconter_resultat", side_effect=AssertionError("Pas de second appel de narration")), \
                 patch("sys.stdout", new_callable=io.StringIO) as output:
                jeu.main(["--console", "--atelier", "--connexion", "api", "--save", str(p)])
            m = Monde.charger(p)
            self.assertEqual(m.data["minutes"], 1)
            self.assertEqual(m.data["gestes_improvises"][-1]["approche"], "expression")
            self.assertNotIn("Fredonner une chanson", str(m.data["journal"]))
            self.assertNotIn("« tenter »", output.getvalue())

    def test_contre_revue_corrige_deux_effets_omis_avant_affichage_et_sauvegarde(self):
        cas = (
            ("je fredonne doucement", proposition("Fredonner", issue("Tu fredonnes.")),
             chant(), "son_improvise", "notes de ta voix"),
            ("je grave une flèche sur la perche", proposition("Graver une flèche",
             issue("Une flèche apparaît."), cibles=["perche_1"], outil="couteau",
             approche="manipulation"), marque(), "marque_improvisee", "flèche vers le nord"),
        )
        for phrase, omise, corrigee, operation, attendu in cas:
            with self.subTest(phrase=phrase), tempfile.TemporaryDirectory() as tmp:
                chemin = Path(tmp) / "partie.json"
                appels = []

                def faux_appel(_instructions, entree, _intention, fonction, _schema):
                    if fonction == "auditer_action":
                        effets = entree["plan"]["effets_reussite"]
                        conforme = any(e[0] == operation for e in effets)
                        appels.append(("audit", conforme))
                        # Même un verdict positif ne peut couvrir un effet absent.
                        return {"conforme": True, "motif": "", "perimetre": "sens",
                                "evenements_requis": ["son" if operation == "son_improvise" else "marquer"]}
                    self.assertEqual(fonction, "repondre_au_joueur")
                    corrige = "retour_moteur" in entree["faits"]
                    appels.append(("proposition", corrige))
                    return reponse(copy.deepcopy(corrigee if corrige else omise))

                with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                      patch.object(MJOpenAI, "_appeler_brut", side_effect=faux_appel),
                      patch("builtins.input", side_effect=[phrase, "quitter"]),
                      patch("sys.stdout", new_callable=io.StringIO) as output):
                    jeu.main(["--console", "--atelier", "--connexion", "api", "--save", str(chemin)])
                reprise = Monde.charger(chemin)
                self.assertEqual(appels, [("proposition", False), ("audit", False),
                                         ("proposition", True), ("audit", True)])
                self.assertEqual(reprise.data["revision"], 1)
                self.assertIn(attendu, output.getvalue())
                self.assertTrue(any(e["operation"] == ("son" if operation == "son_improvise" else "marquer")
                                    for e in reprise.data["journal"][-1]["action"]["reussite"]["effets"]))
                if operation == "son_improvise":
                    self.assertEqual(reprise.data["sons"][-1]["forme"], "voix_melodique")
                else:
                    self.assertIn(attendu, decrire(reprise, "marque_1", detail=True))


class BruitDuSonTests(unittest.TestCase):
    def test_bruit_du_geste_decoule_du_son_produit(self):
        from donjon.improvisation import effet, issue, proposition as improviser
        from donjon.monde import nouveau_monde
        m = nouveau_monde()
        p = improviser("Fredonner", issue("Brouillon.", [effet("son", "joueur", texte="voix_melodique", valeur=2)]),
                       bruit=0)
        plan = Moteur(m).preparer(p)
        self.assertEqual(plan.bruit, 2)
        Moteur(m).executer(plan)
        self.assertEqual(m.data["sons"][-1]["intensite"], 2)
        self.assertEqual(m.data["bruit"], 2)
