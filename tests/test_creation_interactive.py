"""G12 : l'admission précède le geste, sans invention de découverte."""
import copy
import unittest

from donjon.atelier import nouveau_atelier
from donjon.defi import nouveau_defi
from donjon.faits_locaux import preparer_faits, lier_suite
from donjon.monde import ErreurMonde
from donjon.moteur import proposition
from donjon.portee_narrative import contexte_admission
from donjon.projection_publique import ProvenanceAbsente, projeter, verifier_couverture
from donjon.rendu import decrire, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer
from tests.test_audits_attendu import jouer
from tests.test_fouille_faits import faits, revue
from tests.test_messages_decoupage import vivre
from tests.test_projection_publique import entree_actuelle
from tests.test_relances_luna import action
from tests.test_tensions import recharger


class CreationInteractiveTests(unittest.TestCase):
    def scenes(self):
        for m, support, nom, matiere in (
                (nouveau_defi(depart="fixe"), "antichambre_sol", "pierre détachée", "pierre"),
                (nouveau_atelier(), "cour_sol", "éclat de bois", "bois")):
            installer(m)
            yield m, support, nom, matiere

    def test_creation_reprise_ramassage_recharge_et_laps_decoupe(self):
        for m, support, nom, matiere in self.scenes():
            for suite_incluse in (False, True):
                with self.subTest(nom=nom, suite=suite_incluse):
                    ajout = dict(type="objet", ancrage=support, nom=nom, genre="m",
                                 texte="Sa surface est mate.", materiau=matiere,
                                 masse=0.2, mobile=True, relation="pose", capacites=[])
                    # La suite peut nommer le sujet proposé ; le moteur ne le
                    # résout qu'après son admission. Sinon Luna reçoit son id.
                    identifiant = f"fait_{m.data['revision'] + 1}_1"
                    p = proposition("prendre", nom if suite_incluse else identifiant)
                    r = faits(ajout, p if suite_incluse else None)
                    sorties = [r, revue(r)]
                    if not suite_incluse:
                        sorties.append(action(p))
                    avant = copy.deepcopy(m.data)
                    monde, texte, appels = jouer(m, "mj je ramasse " + nom,
                                                sorties, [], suite=("tenter",))
                    self.assertEqual(m.data, avant)
                    self.assertEqual(monde.objets[identifiant]["lieu"], "joueur")
                    self.assertEqual(len([o for o in monde.objets.values()
                                          if o.get("nom") == nom]), 1)
                    self.assertIn(nom, texte)
                    self.assertIn("Compris :", texte)
                    self.assertEqual([f for f, _ in appels],
                                     ["repondre_au_joueur", "auditer_portee"]
                                     + ([] if suite_incluse else ["repondre_au_joueur"])
                                     + ["auditer_action"])
                    self.assertIn(ajout["texte"], decrire(monde, identifiant, detail=True))
                    self.assertEqual(monde.data["faits_vus"][-1]["objet"], identifiant)
                    if not suite_incluse:
                        reprise = appels[2][1]["faits"]
                        self.assertEqual(reprise["objet:" + identifiant]["nom"], nom)
                        self.assertNotIn("origine_description", reprise["objet:" + identifiant])
                    copie = recharger(monde)
                    self.assertEqual((regarder(monde), scene_percue(monde)),
                                     (regarder(copie), scene_percue(copie)))
                    a, _ = vivre(copie.copier(), [40])
                    b, _ = vivre(copie.copier(), [10] * 4)
                    self.assertEqual(a.data, b.data)
                    self.assertEqual((regarder(a), scene_percue(a)),
                                     (regarder(b), scene_percue(b)))

    def test_indices_et_perceptions_negatives_refuses_avant_creation(self):
        for m, support, _, _ in self.scenes():
            for nom, texte, perception, indice in (
                    ("empreinte révélatrice", "Cette empreinte désigne le coupable.", False, True),
                    ("trace de passage", "Ces marques révèlent où se cache un objet.", False, True),
                    ("absence derrière la porte", "Il n'y a rien derrière la porte.", True, False),
                    ("silence dans le coffre", "Aucun objet ne se trouve dans le coffre.", True, False)):
                with self.subTest(support=support, nom=nom):
                    mauvais = faits(dict(type="detail", ancrage=support, nom=nom,
                                         genre="m", texte=texte))
                    p = proposition("examiner", support)
                    monde, affichage, appels = jouer(m, "mj je vérifie ce qui se trouve ici", [
                        mauvais, revue(mauvais, perception=perception, indice=indice), action(p)], [])
                    refus = appels[2][1]["controle_narratif"][0]
                    self.assertIn("proposition.ajouts[0]", refus["attendu"])
                    self.assertIn(support, refus["attendu"])
                    self.assertNotIn(refus["attendu"], affichage)
                    self.assertNotIn(texte, affichage)
                    self.assertNotIn(texte, str(monde.data))
                    self.assertEqual(set(monde.objets), set(m.objets))
                    self.assertEqual(monde.data['references_personnes'], m.data['references_personnes'])
                    self.assertEqual(recharger(monde).data['references_personnes'], m.data['references_personnes'])
                    self.assertEqual(monde.data.get("faits_vus", []), m.data.get("faits_vus", []))
                    self.assertIn(decrire(monde, support, detail=True), affichage)
                    self.assertEqual(monde.data["conversation"][-1]["nature"], "resultat_moteur")

    def test_projection_de_creation_exhaustive_sans_metadonnee_faisant_preuve(self):
        for m, support, nom, matiere in self.scenes():
            with self.subTest(nom=nom):
                travail, _, ajouts = preparer_faits(m, {"ajouts": [dict(
                    type="objet", ancrage=support, nom=nom, genre="m", texte="Sa surface est mate.",
                    materiau=matiere, masse=0.2, mobile=True, relation="pose", capacites=[])]})
                id = ajouts[0]["objet"]
                entree = entree_actuelle(travail, "je le ramasse")
                projection = projeter(entree)
                self.assertGreater(verifier_couverture(entree, projection), 0)
                objet = projection.entree["faits"]["objet:" + id]
                self.assertEqual(objet["relation_support"], "pose")
                self.assertNotIn("origine_description", objet)
                self.assertTrue(any(e["chemin"][-1] == "origine_description"
                                    for e in projection.exclusions))
                contexte = contexte_admission(projection.entree["faits"])
                self.assertEqual(contexte["objet:" + id], objet)
                self.assertEqual(contexte["perception"], projection.entree["faits"]["perception"])
                self.assertNotIn("connaissances_pnj", contexte)
                entree["faits"]["objet:" + id]["nouveau_champ_sans_contrat"] = True
                with self.assertRaises(ProvenanceAbsente):
                    projeter(entree)

    def test_liaison_limitee_aux_references_admises_et_refus_des_ambiguities(self):
        m = nouveau_atelier()
        installer(m)
        ajout = dict(type="objet", ancrage="cour_sol", nom="éclat de bois", genre="m",
                     texte="Sa surface est mate.", materiau="bois", masse=0.2,
                     mobile=True, relation="pose", capacites=[])
        travail, _, etablis = preparer_faits(m, {"ajouts": [ajout]})
        id = etablis[0]["objet"]
        p = {"etapes": [{"cible": ajout["nom"], "destination": "joueur"}],
             "cibles": [ajout["nom"], "inconnu"], "justification": ajout["nom"],
             "texte": ajout["nom"], "etapes.0.cible": ajout["nom"], "quantite": 2}
        avant = copy.deepcopy(p)
        liee = lier_suite(p, travail, etablis)
        self.assertEqual(liee["etapes"], [{"cible": id, "destination": "joueur"}])
        self.assertEqual(liee["cibles"], [id, "inconnu"])
        self.assertEqual(liee["etapes.0.cible"], id)
        self.assertEqual(liee["texte"], ajout["nom"])
        self.assertEqual(liee["justification"], ajout["nom"])
        self.assertEqual(liee["quantite"], 2)
        self.assertEqual(p, avant)
        # Deux ajouts de même nom sur deux supports ne donnent aucun droit
        # de choisir silencieusement l'un d'eux.
        travail.objets["autre"] = {**travail.objets[id], "id": "autre"}
        with self.assertRaises(ErreurMonde) as refus:
            lier_suite(p, travail, [*etablis, {"objet": "autre"}])
        self.assertIn("proposition.suite.etapes[0].cible", refus.exception.attendu)
        self.assertIn(id, refus.exception.attendu)


if __name__ == "__main__":
    unittest.main()
