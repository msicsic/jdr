"""Marchés du joueur : état, paroles et promesses relus depuis la sauvegarde."""
from donjon.emissions import joueur as emissions_joueur
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, relations
from donjon.echanges import evaluer_proposition, proposer, ENGAGEMENT_MAX
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import ErreurMonde
from donjon.paroles import preparer_parole
from donjon.rendu import decrire_comptes
from donjon.spatial import porte_par
from tests.support import calme, regarder
from tests.test_tensions import relais, recharger, placer


def scene(qui="marchand", confiance=70, intelligence=10):
    m = calme(relais(), "marchand", "brune", "aubin", "ilse")
    m.joueur.update(salle="antichambre", position=[1, 3], orientation="est")
    placer(m, qui, "antichambre", [2, 3])
    regarder(m, qui, "joueur")
    m.objets["cloche"].update(lieu="joueur", proprietaire="joueur", prix=5)
    m.objets["vivres"].update(lieu=qui, proprietaire=qui, portions=8)
    m.data["connus"].extend(["cloche", "vivres", "brasero"])
    m.objets[qui]["profil"]["caracteristiques"]["INT"] = intelligence
    lire(m, qui)["relations"]["joueur"] = relations._nouvelle({"confiance": confiance})
    percevoir_tous(m)
    return recharger(m)


PART = {"type": "part", "objet": "vivres"}
CLOCHE = {"type": "objet", "objet": "cloche"}
TACHE = {"type": "tache", "condition": {"objet": "brasero", "allume": True}}


def parler(m, demande=PART, contrepartie=CLOCHE, texte="Je te donne ma cloche contre une part de vivres.", qui="marchand"):
    return preparer_parole(m, {"personnage": qui, "replique": texte, "_intention": "je dis à " +
                             ("Gorm" if qui == "marchand" else "Aubin") + " : " + texte,
                             "contenu": [{"type": "proposition", "demande": copy.deepcopy(demande),
                                          "contrepartie": copy.deepcopy(contrepartie)}]})


class PropositionsTests(unittest.TestCase):
    def test_deplacer_une_flamme_ne_vaut_pas_allumage_deux_sources(self):
        from donjon.moteur import Moteur, proposition
        for lampe in ("torche", "lanterne"):
            m = scene()
            m.objets[lampe].update(lieu="joueur", proprietaire="joueur", allume=True, combustible=60)
            m.data["connus"].append(lampe)
            t = {"type": "tache", "condition": {"objet": lampe, "allume": True}}
            with patch.object(type(m), "d20", return_value=20):
                m, _ = parler(m, contrepartie=t, texte="Une part contre ma promesse d'allumer cette source.")
            moteur = Moteur(m)
            moteur.executer(moteur.preparer(proposition("poser", lampe)))
            m = recharger(m)
            self.assertNotIn("realisee", agendas.en_cours(m, "joueur")[0])
            self.assertIn("Tu as promis", decrire_comptes(m))

    def test_accepter_honore_la_dette_de_deux_auditeurs(self):
        for qui in ("marchand", "aubin"):
            m = scene(qui)
            lire(m, qui)["relations"]["joueur"] = relations._nouvelle({"confiance": 70, "dette": 40})
            with patch.object(type(m), "d20", return_value=20):
                m, r = parler(m, contrepartie={"type": "rien"}, texte="Une part sans contrepartie.", qui=qui)
            m = recharger(m)
            self.assertIn("accepte", " ".join(r["faits"]))
            self.assertEqual(relations.doit(m, qui, "joueur"), 20)
            self.assertTrue(any(x["type"] == "dette_honoree" for x in lire(m, qui)["memoire"]))

    def test_promesse_de_depot_par_le_vrai_moteur_deux_objets(self):
        from donjon.moteur import Moteur, proposition
        for objet in ("cloche", "cire"):
            m = scene()
            m.objets[objet].update(lieu="joueur", proprietaire="joueur")
            m.data["connus"].append(objet)
            t = {"type": "tache", "condition": {"objet": objet, "lieu": "antichambre"}}
            with patch.object(type(m), "d20", return_value=20):
                m, _ = parler(m, contrepartie=t, texte="Je promets de déposer cet objet ici contre une part de vivres.")
            m = recharger(m)
            # Attendre et revoir un état déjà vrai n'est jamais l'exécution d'une tâche.
            m.data["minutes"] += 1
            percevoir_tous(m)
            agendas.observer_promesses(m, [])
            self.assertEqual(len(agendas.en_cours(m, "joueur")), 1)
            moteur = Moteur(m)
            moteur.executer(moteur.preparer(proposition("poser", objet)))
            m = recharger(m)
            m.data["minutes"] += 1
            percevoir_tous(m)
            lignes = []
            agendas.observer_promesses(m, lignes)
            m = recharger(m)
            self.assertEqual(m.objets[objet]["lieu"], "antichambre")
            self.assertEqual(agendas.en_cours(m, "joueur"), [])
            self.assertIn("tenu ta promesse", decrire_comptes(m))

    def test_meme_promesse_ne_paie_pas_deux_fois(self):
        for condition in (TACHE["condition"], {"objet": "cloche", "lieu": "antichambre"}):
            m = scene()
            t = {"type": "tache", "condition": condition}
            with patch.object(type(m), "d20", return_value=20):
                m, _ = parler(m, contrepartie=t, texte="Une part contre ma promesse.")
                parts = m.objets["vivres"]["portions"]
                m, r = parler(m, contrepartie=t, texte="Une part contre ma promesse.")
            m = recharger(m)
            self.assertEqual(m.objets["vivres"]["portions"], parts)
            self.assertEqual(len(agendas.en_cours(m, "joueur")), 1)
            self.assertIn("déjà", " ".join(r["faits"]))

    def test_console_mj_simule_et_historique_recharge(self):
        from tests.test_paroles import jouer, reponse_pnj
        for confiance in (10, 70):
            m = scene(confiance=confiance)
            saisie = "Gorm, je te donne ma cloche contre une part de vivres."
            texte = "Gorm refuse l'échange." if confiance == 10 else "Gorm accepte l'échange."
            reponse = {"mode": "parole_joueur", "texte": "", "faits": ["interlocuteurs"],
                       "proposition": {"personnage": "marchand", "replique": saisie,
                                       "contenu": [{"type": "proposition", "demande": PART, "contrepartie": CLOCHE}]}}
            from donjon.paroles import OPERATIONS, operations_contenu
            codes = operations_contenu(reponse["proposition"]["contenu"])
            reponse["proposition"]["operations_demandees"] = {t: t in codes for t in OPERATIONS}
            m, sortie, _ = jouer(m, saisie, [reponse, reponse_pnj(texte)])
            self.assertIn(texte, sortie)
            self.assertTrue(any(texte in x["reponse"] for x in m.data["conversation"]))
            self.assertEqual(porte_par(m, "cloche", "marchand"), confiance == 70)

    def test_cloche_contre_part_et_autre_proposant(self):
        for qui in ("marchand", "aubin"):
            with self.subTest(qui=qui):
                m = scene(qui)
                with patch.object(type(m), "d20", return_value=20):
                    m, r = parler(m, qui=qui)
                m = recharger(m)
                self.assertTrue(porte_par(m, "cloche", qui))
                self.assertEqual(m.objets["cloche"]["proprietaire"], qui)
                self.assertEqual(m.objets["vivres"]["portions"], 7)
                self.assertTrue(any(porte_par(m, i, "joueur") for i in m.objets if i.startswith("vivres_")))
                self.assertIn("accepte l'échange", " ".join(r["faits"]))
                self.assertIn("Je te donne", emissions_joueur(m)[-1]["texte"])

    def test_mefiance_et_rancune_sans_remise(self):
        for confiance, rancune, cause in ((10, 0, "confiance"), (70, 80, "veut encore")):
            m = scene(confiance=confiance)
            lire(m, "marchand")["relations"]["joueur"] = relations._nouvelle({"confiance": confiance, "rancune": rancune})
            m, r = parler(m)
            m = recharger(m)
            self.assertTrue(porte_par(m, "cloche", "joueur"))
            self.assertEqual(m.objets["vivres"]["portions"], 8)
            self.assertIn(cause, " ".join(r["faits"]))

    def test_confiance_pondere_deux_taches_promises(self):
        for condition in ({"objet": "brasero", "allume": True}, {"objet": "cloche", "lieu": "antichambre"}):
            gains = []
            for confiance in (40, 80):
                m = scene(confiance=confiance)
                t = {"type": "tache", "condition": condition}
                # Le devis reste celui du moteur ; sa magnitude est isolée ici du plan particulier.
                with patch("donjon.echanges._devis_proposition", return_value=(20, [])):
                    gains.append(evaluer_proposition(m, "joueur", "marchand", PART, t)["G"])
            self.assertAlmostEqual(gains[1], gains[0] * 2)
            self.assertGreater(gains[0], 0)

    def test_promesse_inscrite_tenue_ou_abandonnee_et_visible(self):
        for abandon in (False, True):
            m = scene()
            with patch.object(type(m), "d20", return_value=20):
                m, r = parler(m, contrepartie=TACHE, texte="Je promets d'entretenir le brasero contre une part de vivres.")
            m = recharger(m)
            self.assertEqual(len(agendas.en_cours(m, "joueur")), 1)
            self.assertIn("Tu as promis", decrire_comptes(m))
            self.assertIn("engagements", " ".join(r["faits"]))
            m.data["minutes"] += ENGAGEMENT_MAX + 1 if abandon else 1
            if abandon:
                croire(m, "marchand", "brasero", "etat", {"allume": False}, "vu")
            else:
                avant = agendas.etat_promis(m)
                m.objets["brasero"]["allume"] = True
                m.objets["brasero"]["combustible"] += 10
                agendas.constater_geste_joueur(m, avant)
                croire(m, "marchand", "brasero", "etat", {"allume": True, "faible": False}, "vu")
            lignes = []
            agendas.observer_promesses(m, lignes)
            m = recharger(m)
            self.assertEqual(agendas.en_cours(m, "joueur"), [])
            cause = "engagement_abandonne" if abandon else "engagement_tenu"
            self.assertTrue(any(x["type"] == cause and x.get("de") == "joueur" for x in lire(m, "marchand")["memoire"]))
            self.assertIn("abandonné" if abandon else "tenu", decrire_comptes(m))
            self.assertTrue(lignes)

    def test_intelligence_protege_deux_mauvais_marches_meme_graine(self):
        for prix in (30, 40):
            sorties = []
            for intelligence in (8, 20):
                m = scene(intelligence=intelligence)
                m.objets["vivres"]["prix_part"] = prix
                m.objets["cloche"]["prix"] = 1
                # Même graine du monde et même jet ; seule l'INT de l'auditeur varie.
                with patch.object(type(m), "d20", return_value=20):
                    m, r = parler(m)
                m = recharger(m)
                sorties.append(porte_par(m, "cloche", "marchand"))
                self.assertIn("accepte" if intelligence == 8 else "refuse", " ".join(r["faits"]))
            self.assertEqual(sorties, [True, False])

    def test_necessaire_et_garde_sans_jet(self):
        for qui in ("marchand", "aubin"):
            for cause in ("necessaire", "garde"):
                m = scene(qui)
                if cause == "necessaire" and qui == "aubin":
                    m.objets[qui]["profil"]["pulsions"].append(
                        {"besoin": next(iter(m.objets[qui]["profil"]["besoins"])),
                         "condition": {"objet": "vivres", "lieu": "antichambre"}})
                    lire(m, qui)["pulsions"].append(None)
                portions = 1 if cause == "garde" else 8
                m.objets["vivres"]["portions"] = portions
                demande = PART if cause == "garde" else {"type": "objet", "objet": "vivres"}
                with patch("donjon.echanges.jet_persuasion") as jet:
                    m, r = parler(m, demande=demande, qui=qui)
                m = recharger(m)
                self.assertTrue(porte_par(m, "cloche", "joueur"))
                self.assertEqual(m.objets["vivres"]["portions"], portions)
                self.assertIn("réserve" if cause == "garde" else "nécessaire", " ".join(r["faits"]))
                jet.assert_not_called()

    def test_formes_invalides_attendu_et_aucune_mutation(self):
        for terme in ({"type": "pieces", "montant": -1}, {"type": "tache", "condition": {"objet": "inconnu", "allume": True}},
                      {"type": "objet", "objet": []}, {"type": "rien", "montant": 4}):
            m = scene()
            avant = copy.deepcopy(m.data)
            with self.assertRaises(ErreurMonde) as e:
                parler(m, contrepartie=terme)
            self.assertIn("contrepartie", e.exception.attendu)
            self.assertEqual(m.data, avant)
            self.assertTrue(porte_par(recharger(m), "cloche", "joueur"))

    def test_schema_accepte_les_deux_unions(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema facultatif")
        from donjon.paroles import SCHEMA_PAROLE
        for contenu in ([{"type": "proposition", "demande": PART, "contrepartie": TACHE}],
                        [{"type": "propos", "sujet": "", "attribut": "", "valeur": ""}]):
            jsonschema.validate({"personnage": "marchand", "replique": "Bonjour", "contenu": contenu}, SCHEMA_PAROLE)


if __name__ == "__main__":
    unittest.main()
