"""A6 : entrée libre réelle, contrats et effets retrouvés après recharge."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from tests.revue_support import rapport as rapport_complet
from donjon.compilation import schema_reponse
from donjon.emissions import joueur, pnj
from donjon.mj import MJ
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import proposition
from donjon.operations import etape, sequence
from donjon.projection_publique import projeter, verifier_couverture
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from tests.test_comprehension import PontScript
from tests.test_messages_decoupage import vivre
from tests.test_parole_corrections import banc
from tests.test_paroles import relais
from tests.test_repli_et_appel import parole
from tests.test_sous_obstacle import scene, passage
from tests.test_tensions import recharger


class RaccordLibreTests(unittest.TestCase):
    def test_contrats_des_producteurs_sur_tous_les_etats_initiaux(self):
        from donjon.banc_pnj import creer
        from donjon.atelier import nouveau_atelier
        mondes = [(s, creer(s, 1985, "fixe"))
                  for s in ("relais", "crypte", "mine", "auberge", "crue", "rixe")]
        mondes.append(("atelier", nouveau_atelier()))
        for nom, m in mondes:
            with self.subTest(scenario=nom):
                mj = MJ(connexion="chatgpt")
                recus = []

                def capter(instructions, entree, *args):
                    recus.append(entree)
                    raise RuntimeError("requête capturée")

                with patch.object(mj, "_appeler", side_effect=capter):
                    with self.assertRaisesRegex(RuntimeError, "requête capturée"):
                        mj._compiler_libre(m, "Que puis-je faire ici ?")
                self.assertEqual(len(recus), 1)

    def test_entree_du_compilateur_projetee_sans_perte_publique_et_sans_mutation(self):
        for m, mots in ((relais(), "je siffle"), (banc("ressources"), "Aubin, as-tu du bois ?")):
            with self.subTest(mots=mots):
                mj = MJ(connexion="chatgpt")
                avant = copy.deepcopy(m.data)
                traces, recus = [], []
                mj.observateur = traces.append

                def capter(instructions, entree, *args):
                    recus.append(copy.deepcopy(entree))
                    raise RuntimeError("requête capturée")

                with patch("donjon.projection_publique.projeter", wraps=projeter) as projection, \
                     patch.object(mj, "_appeler", side_effect=capter):
                    with self.assertRaisesRegex(RuntimeError, "requête capturée"):
                        mj._compiler_libre(m, mots)
                originale = projection.call_args.args[0]
                publique = projeter(originale)
                self.assertGreater(verifier_couverture(originale, publique), 0)
                self.assertEqual(recus, [publique.entree])
                self.assertEqual(recus[0]["conversation"], originale["conversation"])
                self.assertEqual(m.data, avant)
                self.assertTrue(publique.exclusions)
                self.assertNotIn("projection_publique", recus[0])
                self.assertEqual(traces[-1]["projection_publique"],
                                 dict(provenances=publique.provenances, exclusions=publique.exclusions))
                for esprit in recus[0]["faits"].get("esprits_interlocuteurs", {}).values():
                    self.assertFalse(set(esprit) & {"traits", "valeurs", "croit", "but_actuel", "engagements"})

    def test_champ_de_contexte_non_porte_refuse_avant_le_modele(self):
        m = nouveau_monde()
        contexte = m.contexte()
        contexte["source_sans_contrat"] = "secret"
        mj = MJ(connexion="chatgpt")
        with patch.object(m, "contexte", return_value=contexte), \
             patch.object(mj, "_appeler_brut", side_effect=AssertionError("Contexte non couvert")):
            from donjon.monde import ErreurMonde
            with self.assertRaises(ErreurMonde) as refus:
                mj._compiler_libre(m, "je regarde")
        self.assertIn("source_sans_contrat", refus.exception.attendu)

    def jouer(self, m, saisie, r, *, suite=("tenter",)):
        mj = MJ(connexion="chatgpt")
        appels, apercus = [], []

        def brut(instructions, entree, intention, fonction, schema):
            appels.append((fonction, copy.deepcopy(entree)))
            if fonction == "auditer_action":
                if "contenu_conforme" in schema["properties"]:
                    from donjon.paroles import operations_contenu
                    from donjon.couverture_action import OPERATIONS
                    codes = operations_contenu(entree["plan"]["parole"]["contenu"])
                    return dict(contenu_conforme=True, motif="", perimetre="sens",
                                operations_demandees={t: t in codes for t in OPERATIONS})
                return rapport_complet(entree)
            self.assertEqual(fonction, "repondre_au_joueur")
            self.assertEqual(schema, schema_reponse())
            return copy.deepcopy(r)

        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "copie.json"
            m.sauver(chemin)

            class Pont(PontScript):
                def rafraichir(self, monde, pending, mj):
                    if pending:
                        apercus.append(copy.deepcopy(monde.data))
                    super().rafraichir(monde, pending, mj)

            pont = Pont(["mj " + saisie, *suite, "quitter"], chemin)
            with patch.object(jeu, "MJ", return_value=mj), patch.object(mj, "_appeler_brut", side_effect=brut), \
                 patch.object(mj, "_compiler_libre", wraps=mj._compiler_libre) as compiler, \
                 patch.object(Monde, "d20", return_value=20), patch("sys.stdout", io.StringIO()):
                self.assertEqual(jeu.main(["--console", "--connexion", "chatgpt", "--save", str(chemin)], interface=pont), 0)
            self.assertEqual(compiler.call_count, 1)
            self.assertEqual(compiler.call_args.args[1], saisie)
            self.assertEqual(sum(f == "repondre_au_joueur" for f, _ in appels), 1)
            self.assertTrue(any(f == "auditer_action" for f, _ in appels))
            r = Monde.charger(chemin)
            self.assertEqual(r.data, json.loads(json.dumps(pont.vu)))
            e = r.data["conversation"][-1]
            self.assertIn("Compris :", e["compris"])
            self.assertIn(e["reponse"], "\n".join(pont.historique))
            for a in apercus:
                for cle in ("objets", "joueur", "minutes", "dixiemes", "jets"):
                    self.assertEqual(a[cle], m.data[cle], cle)
            reprise = PontScript(["quitter"], chemin)
            with patch("sys.stdout", io.StringIO()):
                jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise)
            self.assertEqual(Monde.charger(chemin).data, r.data)
            self.assertIn(e["reponse"], "\n".join(reprise.historique))
            self.assertEqual((regarder(r), fiche(r), scene_percue(r)),
                             (regarder(recharger(r)), fiche(recharger(r)), scene_percue(recharger(r))))
        # Le monde issu du raccord garde la même évolution, y compris après
        # plusieurs sauvegardes, pour un laps entier et ses quatre tranches.
        a, _ = vivre(r.copier(), [600])
        b, _ = vivre(r.copier(), [150] * 4)
        self.assertEqual(a.data, b.data)
        self.assertEqual((regarder(a), fiche(a), scene_percue(a)),
                         (regarder(b), fiche(b), scene_percue(b)))
        return r, apercus

    def action(self, m, saisie, p, **kw):
        return self.jouer(m, saisie, dict(mode="action", texte="", faits=[], proposition=p), **kw)

    def test_sequence_attente_cas_reel_et_autre_cible_avec_consentement(self):
        for cible in ("crochets", "bourse_test"):
            with self.subTest(cible=cible):
                m = nouveau_monde()
                m.joueur["salle"] = "echoppe"
                if cible == "bourse_test":
                    m.objets[cible] = {**copy.deepcopy(m.objets["crochets"]), "id": cible,
                                       "nom": "bourse de cuir", "aliases": ["bourse"]}
                    m.data["connus"].append(cible)
                mots = ("J'attends que Gorm ait le dos tourné pour prendre discrètement les crochets"
                        if cible == "crochets" else "je guette une occasion puis dérobe la bourse")
                r, apercus = self.action(m, mots, proposition("voler", cible, methode="finesse"))
                self.assertTrue(apercus)
                self.assertEqual(r.objets[cible]["lieu"], "joueur")
                self.assertIn("Guetter une occasion", r.data["conversation"][-1]["compris"])

    def test_expression_son_cas_reel_et_autre_forme(self):
        for methode, mots in (("sifflement", "je siffle un air joyeux"), ("cri", "je crie de colère")):
            with self.subTest(methode=methode):
                r, _ = self.action(relais(), mots, sequence(etape("emettre_son", "joueur", methode=methode)))
                self.assertEqual(len(r.data["sons"]), 1)
                self.assertEqual(r.data["sons"][0]["nature"], methode)

    def test_passage_cas_reel_et_autre_support(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            with self.subTest(scenario=scenario):
                m = scene(scenario, cible)
                r, _ = self.action(m, "je voudrais passer sous " + cible, passage(cible))
                self.assertEqual(r.joueur["position"][0], m.joueur["position"][0] + 2)
                self.assertTrue(r.objets[cible]["bloque_passage"])

    def test_consultation_cas_reel_et_autre_information_sans_transfert(self):
        for sujet in ("bois", "vivres"):
            with self.subTest(sujet=sujet):
                m = banc("ressources")
                mots = "Aubin, as-tu du " + sujet + " ?"
                r, _ = self.jouer(m, mots, parole(mots, ("ressource", sujet, "", ""), personnage="aubin"))
                self.assertEqual(r.objets, m.objets)
                self.assertEqual(r.joueur, m.joueur)
                self.assertEqual(joueur(r)[-1]["texte"], mots)
                self.assertEqual(pnj(r)[-1]["acte"], "reponse_information")

    def test_famille_transitoire_cas_reel_et_autre_cible(self):
        for cible in ("cle", "crochets"):
            with self.subTest(cible=cible):
                m = nouveau_monde()
                # Donnée d'auteur : objet sans propriétaire dans la pièce du joueur.
                m.objets[cible].update(lieu=m.joueur["salle"], proprietaire=None, en_vente=False)
                m.objets[cible].pop("prix", None)
                r, _ = self.action(m, "je ramasse " + cible, proposition("prendre", cible))
                self.assertEqual(r.objets[cible]["lieu"], "joueur")

    def test_liberation_saisie_libre_liens_de_deux_producteurs_apres_recharge(self):
        from donjon import corps
        from donjon.banc_pnj import appliquer_etats
        from donjon.esprits import percevoir_tous
        from donjon.moteur import Moteur
        from tests.test_tenir import situation
        for cible, origine in (("brune", "etat"), ("aubin", "geste")):
            with self.subTest(cible=cible, origine=origine):
                m = situation(cible)
                for id, o in m.objets.items():
                    if o["type"] == "personnage":
                        corps.endormir(m, id)
                if origine == "etat":
                    appliquer_etats(m, [cible + ":ligote"])
                else:
                    moteur = Moteur(m)
                    moteur.executer(moteur.preparer(proposition("ligoter", cible, "corde_test")))
                # État d'auteur : ces liens retiennent maintenant Corvus.
                liens = corps.corps(m, cible).pop("lie")
                corps.corps(m, "joueur")["lie"] = liens
                lien = liens["lien"]
                m.objets[lien]["lieu"] = "joueur"
                percevoir_tous(m)
                m = recharger(m)
                self.assertIs(m.objets[lien]["entrave"], True)
                or_avant = m.joueur["or"]
                r, apercus = self.action(m, "je dénoue mes liens", proposition("liberer", "joueur"))
                self.assertTrue(apercus)
                self.assertNotIn("lie", corps.corps(r, "joueur"))
                self.assertNotIn("entrave", r.objets[lien])
                self.assertEqual(r.joueur["or"], or_avant)
                self.assertIn("liens", r.data["conversation"][-1]["reponse"])

    def test_matieres_typees_retrouvees_apres_geste_recharge_et_laps(self):
        from donjon.atelier import nouveau_atelier
        source = nouveau_atelier()
        for cible in ("ficelle", "perche_1"):
            with self.subTest(cible=cible):
                m = nouveau_monde()
                m.objets[cible] = copy.deepcopy(source.objets[cible])
                m.objets[cible]["lieu"] = m.joueur["salle"]
                physique = copy.deepcopy(m.objets[cible]["physique"])
                r, _ = self.action(m, "je ramasse " + cible, proposition("prendre", cible))
                self.assertEqual(r.objets[cible]["lieu"], "joueur")
                self.assertEqual(r.objets[cible]["physique"], physique)

    def test_commande_directe_ne_passe_pas_par_le_compilateur(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "copie.json"
            nouveau_monde().sauver(chemin)
            pont = PontScript(["prendre cle", "quitter"], chemin)
            with patch.object(MJ, "_compiler_libre", side_effect=AssertionError("Commande directe")), \
                 patch("sys.stdout", io.StringIO()):
                self.assertEqual(jeu.main(["--console", "--offline", "--save", str(chemin)], interface=pont), 0)
            self.assertEqual(Monde.charger(chemin).objets["cle"]["lieu"], "joueur")
