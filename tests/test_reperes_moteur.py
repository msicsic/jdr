"""G6 : position publique, requête typée, console et disque sans MJ narrateur."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.atelier import nouveau_atelier
from donjon.carte import carte
from donjon.localisation import phrases_positions
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.narration import segments_etablis, attestations, controler, consigner
from donjon.noms import reference
from donjon.rendu import position, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer, memoriser
from tests.test_audits_attendu import jouer
from tests.test_regard_joueur import relais, faire
from tests.test_relances_luna import action
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger
from tests.test_sous_obstacle import scene as conduite


class ReperesMoteurTests(unittest.TestCase):
    def atelier(self):
        m = nouveau_atelier()
        installer(m)
        m.joueur.update(position=[3, 2], orientation="nord")
        memoriser(m)
        return m

    def aubin(self, connu=True):
        m = relais()
        m.joueur.update(position=[1, 3], orientation="sud")
        m.objets["aubin"].update(lieu="antichambre", position_salle="antichambre", position=[1, 4])
        m.data["noms_connus"] = [i for i in m.data["noms_connus"] if i != "aubin"]
        if connu:
            m.data["noms_connus"].append("aubin")
        memoriser(m)
        return m

    def verifier_recharge(self, m):
        vue, scene, plan = regarder(m), scene_percue(m), carte(m)
        avant = copy.deepcopy(m.data)
        r = recharger(m)
        self.assertEqual(regarder(r), vue)
        self.assertEqual(scene_percue(r), scene)
        self.assertEqual(carte(r), plan)
        self.assertEqual(r.data, avant)
        return r

    def interroger(self, m, cible, demande, libelle=None):
        attendu = position(m, cible)
        libelle = libelle or {"mur_atelier": "le mur de l'atelier [mur_atelier]",
                              "aubin": "Aubin [aubin]", "marchand": "Gorm [marchand]",
                              "poutre_conduite": "la poutre effondrée [poutre_conduite]"}[cible]
        compris = f"Compris : Consulter le repère connu. (cible : {libelle})"
        avant = copy.deepcopy(m.data)
        r, sortie, appels = jouer(m, demande, [action(proposition("reperer", reference(m, cible)))], [])
        self.assertEqual([f for f, _ in appels], ["repondre_au_joueur"])
        self.assertIn(attendu, sortie)
        # La réponse exacte de G6 demeure entière ; U-P y joint son récapitulatif
        # exact, sans fiche, proposition en attente ni confirmation.
        self.assertEqual(r.data["conversation"][-1]["reponse"], attendu + "\n" + compris)
        self.assertEqual(r.data["conversation"][-1]["compris"], compris)
        self.assertNotIn("Faisabilité seulement", r.data["conversation"][-1]["reponse"])
        self.assertNotIn("tenter", r.data["conversation"][-1]["reponse"])
        self.assertEqual(r.data["conversation"][-1]["nature"], "resultat_moteur")
        for champ in ("objets", "joueur", "souvenirs_visuels", "journal", "temps"):
            self.assertEqual(r.data.get(champ), avant.get(champ), champ)
        recharge = self.verifier_recharge(r)
        self.assertEqual(position(recharge, cible), attendu)
        return r, attendu

    def test_171_mur_atelier_et_aubin_un_metre(self):
        _, mur = self.interroger(self.atelier(), "mur_atelier", "où se trouve le mur de l'atelier ?")
        self.assertIn("2 mètres vers nord et 3 mètres vers ouest", mur)
        self.assertIn("3,6 mètres", mur)
        self.assertIn("devant toi et à ta gauche", mur)
        _, aubin = self.interroger(self.aubin(), "aubin", "à quelle distance est Aubin ?")
        self.assertIn("1 mètre vers sud", aubin)
        self.assertIn("1 mètre de toi", aubin)
        self.assertIn("devant toi", aubin)

    def test_rotation_reprojette_le_meme_repere_sans_tourner_vers_la_cible(self):
        m = self.atelier()
        faire(m, "tourner ouest")
        _, texte = self.interroger(m, "mur_atelier", "de quel côté est le mur ?")
        self.assertIn("devant toi et à ta droite", texte)
        self.assertIn("2 mètres vers nord et 3 mètres vers ouest", texte)

    def test_souvenirs_objet_et_personne_sans_position_cachee(self):
        for m, cible, regard in ((conduite(), "poutre_conduite", "ouest"), (self.aubin(), "aubin", "nord")):
            with self.subTest(cible=cible):
                memoriser(m)
                faire(m, "tourner " + regard)
                self.assertFalse(m.visible(cible))
                souvenir = copy.deepcopy(m.data["souvenirs_visuels"][cible])
                attendu = position(m, cible)
                autre = m.copier()
                autre.objets[cible]["position"] = [0, 4] if cible == "aubin" else [5, 2]
                self.assertEqual(position(autre, cible), attendu)
                r, texte = self.interroger(autre, cible, "où l'avais-je vu ?")
                self.assertIn("Dernière observation", texte)
                self.assertIn("derrière toi", texte)
                self.assertIn("ne garantit pas sa position actuelle", texte)
                self.assertEqual(r.data["souvenirs_visuels"][cible], souvenir)

    def test_nom_prive_ne_devient_pas_identite_par_la_position(self):
        m = self.aubin(connu=False)
        _, texte = self.interroger(m, "aubin", "où se trouve cette personne ?",
                                   "le vieil homme voûté [personne_1]")
        self.assertNotIn("Aubin", texte)

    def test_cible_sans_repere_ne_divulgue_pas_sa_position(self):
        m = self.aubin()
        m.data["souvenirs_visuels"].pop("marchand", None)
        if "marchand" not in m.data["noms_connus"]:
            m.data["noms_connus"].append("marchand")
        _, texte = self.interroger(m, "marchand", "où se trouve le marchand ?")
        self.assertIn("Tu ne vois pas", texte)
        self.assertNotIn("échoppe", texte)

    def test_faux_repere_propose_ou_plan_modifie_ne_peut_pas_sortir(self):
        for m, cible in ((self.atelier(), "mur_atelier"), (self.aubin(), "aubin")):
            with self.subTest(cible=cible):
                moteur = Moteur(m)
                p = proposition("reperer", cible, justification="à cent mètres derrière toi")
                plan = moteur.preparer(p)
                plan.information = "Faux repère à cent mètres derrière toi."
                attendu = position(m, cible)
                self.assertEqual(moteur.executer(plan), attendu)
                self.assertNotIn("cent mètres", attendu)
                with self.assertRaises(ErreurMonde) as erreur:
                    moteur.preparer({**p, "position_relative": "cent mètres"})
                self.assertTrue(erreur.exception.attendu)
                with self.assertRaises(ErreurMonde) as erreur:
                    moteur.preparer(proposition("reperer", "cible_inventee"))
                self.assertTrue(erreur.exception.attendu)

    def test_reprise_exacte_seule_est_etablie_et_sans_audit(self):
        m = self.atelier()
        phrase = position(m, "mur_atelier")
        r, sortie, appels = jouer(m, "où se trouve le mur ?", [dialogue(phrase)], [])
        self.assertEqual([f for f, _ in appels], ["repondre_au_joueur"])
        faits = appels[0][1]["faits"]
        self.assertEqual(phrases_positions(faits)["mur_atelier"], phrase)
        self.assertTrue(segments_etablis(phrase, faits))
        self.assertFalse(segments_etablis(phrase.replace("2 mètres", "9 mètres"), faits))
        self.assertIn(phrase, sortie)
        self.verifier_recharge(r)

    def test_commande_locale_publie_apres_sauvegarde_sans_modele(self):
        m = self.atelier()
        attendu = position(m, "mur_atelier")
        publications = []
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)

            def afficher(*args, **kwargs):
                if args == (attendu,):
                    sauve = Monde.charger(chemin)
                    self.assertEqual(sauve.data["conversation"][-1]["reponse"], attendu)
                    publications.append(attendu)

            with (patch("builtins.input", side_effect=["reperer mur_atelier", "quitter"]),
                  patch("builtins.print", side_effect=afficher),
                  patch("donjon.mj.MJOpenAI._appeler_brut", side_effect=AssertionError("Modèle interdit"))):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)]), 0)
        self.assertEqual(publications, [attendu])

    def test_revalidation_de_la_distance_exacte_avant_enregistrement(self):
        m = self.atelier()
        phrase = position(m, "mur_atelier")
        faits = m.contexte()
        faits["attestations"] = attestations(m, faits)
        audit = controler(phrase, {"segments": {}}, faits)
        audit.update(texte_initial=phrase, faits=faits, fondement=phrase)
        m.joueur["position"] = [2, 2]  # Même côté, autre distance.
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            consigner(m, {**dialogue(phrase), "_audit": audit})
        self.assertEqual(m.data, avant)

    def test_salle_sans_cases_et_affaire_portee_dans_le_noir(self):
        m = self.atelier()
        m.data.pop("mode_cases")
        _, texte = self.interroger(m, "mur_atelier", "où est le mur ?")
        self.assertIn("Cour de l'atelier", texte)
        self.assertNotIn("mètre", texte)
        m = conduite()
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        self.assertEqual(position(m, "couteau"), "Le couteau à lame fine : dans tes affaires.")


if __name__ == "__main__":
    unittest.main()
