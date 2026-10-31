"""G14 : publication cosmétique, matérialisation unique et geste après recharge."""
import copy
import unittest

from donjon.faits_locaux import preparer_faits
from donjon.monde import ErreurMonde
from donjon.noms import reference
from donjon.voix import reel
from donjon.moteur import Moteur, proposition
from donjon.narration import (AuditIllisible, ambiance_ciblee, consigner, controler,
                              elements_ambiance, schema_audit)
from donjon.rendu import decrire, regarder
from donjon.scene import scene_percue
from tests.test_audits_attendu import jouer, ligne, rapport
from tests import test_creation_interactive as creation
from tests.test_fouille_faits import faits, revue
from tests.test_relances_luna import action
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger


def publier(m, support, nom, manipulable=True):
    texte = "Une " + nom + " baigne dans une atmosphère feutrée."
    e = dict(id="element", libelle=nom, ancrage=support, manipulable=manipulable)
    r, sortie, appels = jouer(m, "mj décris l'atmosphère", [dialogue(texte)],
                              [rapport(ligne("ambiance", entites=[e]))])
    return r, texte, sortie, appels


class CiblageAmbianceTests(unittest.TestCase):
    def test_publication_creation_geste_et_reprise_unique_apres_recharge(self):
        for index, (m, support, nom, matiere) in enumerate(creation.CreationInteractiveTests().scenes()):
            with self.subTest(nom=nom):
                if index == 0:
                    nom = "pierre mouillée"  # Détail évoqué dans l'ambiance historique du Relais.
                avant = copy.deepcopy(m.objets)
                m, prose, sortie, appels = publier(m, support, nom)
                self.assertIn(prose, sortie)
                self.assertEqual(m.objets, avant)
                source = elements_ambiance(m)[0]
                self.assertNotIn("objet", source)
                with self.assertRaisesRegex(ErreurMonde, "matérialisé avant le geste"):
                    Moteur(m).preparer(proposition("prendre", source["id"]))
                self.assertEqual(ambiance_ciblee(m, "je ramasse " + nom)[0]["texte"], prose)
                ajout = dict(type="objet", ancrage=source["id"], nom=nom, genre="m",
                             texte="Sa surface est mate.", materiau=matiere, masse=0.2,
                             mobile=True, relation="pose", capacites=[])
                # La référence existe avant toute adoption ou sauvegarde, sur
                # la copie où la suite jointe va être préparée (lot 433).
                registre = copy.deepcopy(m.data['references_personnes'])
                travail, _, etablis = preparer_faits(m, {'ajouts': [ajout]})
                neuf = etablis[0]['objet']
                self.assertIn(neuf, travail.data['references_personnes'])
                ref = reference(travail, neuf)
                self.assertEqual(reel(travail, ref), neuf)
                self.assertEqual(m.data['references_personnes'], registre)
                reponse = faits(ajout, proposition("prendre", source["id"]))
                reponses = [reponse, revue(reponse)]
                r, texte, appels = jouer(m, "mj je ramasse " + nom,
                                         reponses, [], suite=("tenter",))
                id = elements_ambiance(r)[0]["objet"]
                self.assertEqual(id, neuf)
                self.assertEqual(r.data['references_personnes'][id], travail.data['references_personnes'][id])
                self.assertEqual(reel(r, ref), id)
                self.assertEqual(r.objets[id]["lieu"], "joueur")
                self.assertEqual(sum(o["nom"] == nom for o in r.objets.values()), 1)
                self.assertIn(nom, texte)
                self.assertIn("Compris :", texte)
                self.assertEqual([f for f, _ in appels],
                                 ["repondre_au_joueur", "auditer_portee"]
                                 + ["auditer_action"])
                self.assertIn("Sa surface est mate.", decrire(r, id, detail=True))
                # Une nouvelle proposition de création, même sur le support initial,
                # retrouve l'objet emporté ; elle ne consomme plus de budget.
                ajout["ancrage"] = support
                reponse = faits(ajout, proposition("examiner", source["id"]))
                apres, affichage, _ = jouer(recharger(r), "mj j'examine " + nom,
                                            [reponse, revue(reponse)], [])
                self.assertEqual(sum(o["nom"] == nom for o in apres.objets.values()), 1)
                self.assertEqual(apres.data.get("inventions"), r.data.get("inventions"))
                self.assertEqual(elements_ambiance(apres)[0]["objet"], id)
                self.assertIn(decrire(apres, id, detail=True), affichage)
                recharge = recharger(apres)
                self.assertEqual(reference(recharge, id), ref)
                self.assertEqual(reel(recharge, ref), id)
                self.assertEqual((regarder(apres), scene_percue(apres)),
                                 (regarder(recharge), scene_percue(recharge)))
                # L'éviction de la prose bornée ne permet pas un second exemplaire.
                from donjon.narration import AMBIANCES_PAR_LIEU
                for _ in range(AMBIANCES_PAR_LIEU):
                    consigner(recharge, {"texte": "Un souffle frais passe.", "_audit": {
                        **controler("Un souffle frais passe.", rapport(ligne("ambiance")), {}),
                        "texte_initial": "Un souffle frais passe.", "faits": {}, "fondement": ""}})
                self.assertFalse(elements_ambiance(recharge))
                recharge, _, _, _ = publier(recharger(recharge), support, nom)
                self.assertEqual(elements_ambiance(recharge)[0]["objet"], id)
                travail, _, etablis = preparer_faits(recharge, {"ajouts": [ajout]})
                self.assertEqual(etablis[0]["objet"], id)
                self.assertEqual(sum(o["nom"] == nom for o in travail.objets.values()), 1)

    def test_identifiant_local_leve_une_ambiguite_de_libelles(self):
        m, support, nom, matiere = next(creation.CreationInteractiveTests().scenes())
        m, _, _, _ = publier(m, support, nom)
        source = copy.deepcopy(elements_ambiance(m)[0])
        m, _, _, _ = publier(m, "antichambre_murs", nom)
        ajout = dict(type="objet", ancrage=source["id"], nom=nom, genre="m",
                     texte="Sa surface est mate.", materiau=matiere, masse=0.2,
                     mobile=True, relation="pose", capacites=[])
        reponse = faits(ajout, proposition("prendre", source["id"]))
        r, texte, _ = jouer(m, "mj je ramasse " + nom, [reponse, revue(reponse)], [], suite=("tenter",))
        elements = {e["id"]: e for e in elements_ambiance(recharger(r))}
        self.assertEqual(r.objets[elements[source["id"]]["objet"]]["lieu"], "joueur")
        self.assertNotIn("objet", next(e for id, e in elements.items() if id != source["id"]))
        self.assertEqual(sum(o["nom"] == nom for o in r.objets.values()), 1)
        self.assertIn("Compris :", texte)

    def test_odeur_non_manipulable_dans_la_boucle_et_apres_recharge(self):
        m, _, _, _ = next(creation.CreationInteractiveTests().scenes())
        m, prose, _, _ = publier(m, "", "odeur de terre", False)
        avant = copy.deepcopy(m.objets)
        registre = copy.deepcopy(m.data['references_personnes'])
        source = elements_ambiance(m)[0]
        p = action(proposition("prendre", source["id"]))
        r, texte, appels = jouer(m, "mj je ramasse cette odeur de terre", [p, p], [])
        self.assertIn("sans objet à manipuler", texte)
        self.assertEqual(r.objets, avant)
        self.assertEqual(r.data['references_personnes'], registre)
        self.assertNotIn("objet", elements_ambiance(recharger(r))[0])
        self.assertEqual(r.data["ambiances"][r.joueur["salle"]][0]["texte"], prose)
        self.assertNotIn("auditer_action", [f for f, _ in appels])
        ajout = dict(type="objet", ancrage=source["id"], nom=source["libelle"], genre="f",
                     texte="Sa surface est mate.", materiau="terre", masse=0.2,
                     mobile=True, relation="pose", capacites=[])
        with self.assertRaisesRegex(ErreurMonde, "sans objet à manipuler"):
            preparer_faits(r, {"ajouts": [ajout]})

    def test_budget_epuise_ne_materialise_rien_et_ne_perd_pas_la_cible(self):
        m, support, nom, matiere = next(creation.CreationInteractiveTests().scenes())
        m, _, _, _ = publier(m, support, nom)
        m.data["salles"][m.joueur["salle"]]["potentiel_invention"]["objets_max"] = 0
        m = recharger(m)
        avant = copy.deepcopy(m.objets)
        registre = copy.deepcopy(m.data['references_personnes'])
        source = copy.deepcopy(elements_ambiance(m)[0])
        ajout = dict(type="objet", ancrage=source["id"], nom=nom, genre="m",
                     texte="Sa surface est mate.", materiau=matiere, masse=0.2,
                     mobile=True, relation="pose", capacites=[])
        reponse = faits(ajout, proposition("prendre", source["id"]))
        r, texte, appels = jouer(m, "mj je ramasse " + nom, [reponse, reponse], [])
        self.assertEqual(r.objets, avant)
        self.assertEqual(r.data['references_personnes'], registre)
        self.assertEqual(elements_ambiance(r)[0], source)
        self.assertIn("ne recèle plus rien", texte)
        self.assertFalse(r.data.get("inventions"))
        self.assertNotIn("auditer_action", [f for f, _ in appels])

    def test_enveloppes_invalides_refusees_et_revalidation_avant_publication(self):
        m, support, nom, _ = next(creation.CreationInteractiveTests().scenes())
        contexte = m.contexte()
        contexte.update({"objet:" + o["id"]: o for o in contexte.pop("objets_perceptibles")})
        texte = "Une " + nom + " baigne dans une atmosphère feutrée."
        e = dict(id="element", libelle=nom, ancrage=support, manipulable=True)
        for elements in ([e, e], [{**e, "libelle": "élément absent"}],
                         [{**e, "ancrage": "inconnu"}], [{**e, "ancrage": ""}],
                         [{**e, "objet": "invente"}], [{**e, "manipulable": 1}]):
            with self.subTest(elements=elements), self.assertRaises(AuditIllisible):
                controler(texte, rapport(ligne("ambiance", entites=elements)), contexte)
        audit = controler(texte, rapport(ligne("ambiance", entites=[e])), contexte)
        audit.update(texte_initial=texte, faits=contexte, fondement="")
        m.objets[support]["lieu"] = "echoppe"
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde):
            consigner(m, {"texte": texte, "_audit": audit})
        self.assertEqual(m.data, avant)
        # La production réelle demande la même enveloppe structurée.
        variantes = schema_audit(contexte, 1)["properties"]["segments"]["properties"]["0"]["anyOf"]
        ambiance = next(v for v in variantes if v["properties"]["nature"]["enum"] == ["ambiance"])
        self.assertEqual(ambiance["properties"]["entites"]["items"]["type"], "object")


if __name__ == "__main__":
    unittest.main()
