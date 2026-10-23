"""Contrats restés en marge des fusions : scènes complètes, état et vue après reprise."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon import corps, noms, relations as R
from donjon.biens import prix
from donjon.echanges import demander, executer, accueil
from donjon.esprits import lire, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj import _etape, _executer
from donjon.rendu import regarder
from donjon.social import phrase, faire_entendre
from donjon.temps import ecouler, MINUTE
from tests.support import calme, regarder as orienter
from tests.test_relations_graduees import reunir
from tests.test_relations_lectures import lien
from tests.test_social import relais, placer, recharger


def scene():
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    m.joueur.update(salle="antichambre", position=[2, 4], orientation="sud")
    return m


class RestesFusionsTests(unittest.TestCase):
    def _livrer(self, part):
        for vendeur, acheteur in (("marchand", "brune"), ("aubin", "ilse")):
            with self.subTest(part=part, vendeur=vendeur):
                m = reunir(scene(), vendeur, acheteur)
                lot = "bois" if part else "marteau"
                m.objets[lot].update(lieu="antichambre", position=[2, 6], position_salle="antichambre",
                                     proprietaire=vendeur)
                m.data["finances_pnj"][acheteur] = 100
                percevoir_tous(m)
                m = recharger(m)
                with patch.object(Monde, "d20", return_value=20):
                    self.assertEqual(demander(m, acheteur, vendeur, lot, prix=prix(m, lot) or 2,
                                             remettre_part=part), "vendu")
                m = recharger(m)
                promesse = next(x for x in lire(m, vendeur)["engagements"] if x["pour"] == acheteur)
                objet = promesse["condition"]["objet"]
                avant = R.envers(m, acheteur, vendeur)
                # Le vendeur va prendre le bien puis le remet par les gestes communs.
                placer(m, vendeur, "antichambre", [2, 5])
                lignes = []
                self.assertTrue(_executer(m, vendeur, _etape("prendre", objet), lignes, {}))
                m = recharger(m)
                self.assertTrue(executer(m, vendeur, _etape("remettre", acheteur, objet), lignes))
                m = recharger(m)
                self.assertEqual(m.objets[objet]["lieu"], acheteur)
                self.assertEqual(m.objets[objet]["proprietaire"], acheteur)
                apres = R.envers(m, acheteur, vendeur)
                self.assertEqual(apres["confiance"], avant["confiance"] + 15)
                self.assertGreater(apres["dette"], avant["dette"])
                self.assertEqual(apres["motifs"][-1]["type"], "engagement_tenu")
                self.assertEqual(lire(m, vendeur)["engagements"], [])
                self.assertEqual(lire(m, vendeur)["suites"], [])
                memoire = lire(m, acheteur)["memoire"]
                recu = next(x for x in memoire if x["type"] == "recu" and x["objet"] == objet)
                tenu = next(x for x in memoire if x["type"] == "engagement_tenu" and x["de"] == vendeur)
                self.assertEqual(recu["minute"], tenu["minute"])
                self.assertIn("remet", " ".join(lignes))
                faire_entendre(m, vendeur, acheteur, "Une parole.", [], [])
                self.assertEqual(R.envers(recharger(m), acheteur, vendeur), apres)

    def test_objet_vendu_d_avance_tenu_a_la_reception(self):
        self._livrer(False)

    def test_part_differee_tenue_a_la_reception(self):
        self._livrer(True)

    def test_accueil_et_reponses_suivent_les_bandes_apres_estompement(self):
        from donjon.appel import repondre
        from donjon.pnj import heler
        for source in ("joueur", "aubin"):
            for axe in ("peur", "rancune"):
                with self.subTest(source=source, axe=axe):
                    m = reunir(scene(), "ilse", "aubin")
                    orienter(m, "ilse", source)
                    lien(m, "ilse", source, **{axe: 45})
                    m.objets["ilse"]["profil"]["valeurs"].update(fierte=10, douceur=0)
                    # La même bande reste active sous 40 et sort sous 30, même après recharge.
                    for minutes, ferme in ((0, True), (40, True), (180, False)):
                        c = recharger(m)
                        ecouler(c, minutes * MINUTE)
                        c = recharger(c)
                        r = R.envers(c, "ilse", source)
                        if minutes == 40:
                            self.assertLess(r[axe], 40)
                            self.assertGreaterEqual(r[axe], 30)
                        self.assertEqual(accueil(c, source, "ilse"), "rancune" if axe == "rancune" and ferme else None)
                        lignes = []
                        heler(c, source, "ilse", lignes)
                        self.assertEqual(repondre(c, source, "ilse", lignes), not ferme)
                        c = recharger(c)
                        self.assertEqual("Ilse répond" in " ".join(lignes), not ferme)
                        self.assertEqual(bool(lire(c, "ilse")["rejoindre"]), False)

    def test_le_banc_compte_les_bandes_conservees(self):
        from donjon.banc_pnj import executer as nuit
        from donjon.relations import _bandes
        for axe, mesure in (("confiance", "mefiances"), ("rancune", "rancunes")):
            m = scene()
            for id in m.data["esprits"]:
                lire(m, id)["relations"].clear()
            r = R._nouvelle({axe: 20 if axe == "confiance" else 45})
            r[axe] = 35
            r["ancrages"]["rancune"] = [r["rancune"], 0]
            r["bandes"] = _bandes(r, r["bandes"])
            lire(m, "ilse")["relations"]["aubin"] = r
            m = recharger(m)
            _, mesures = nuit(m, 0)
            self.assertEqual(mesures[mesure], 1)
            self.assertIn("REFUGE DU RELAIS", regarder(m))

    def test_refus_clos_et_inconscient_en_identifiants(self):
        for mort in (True, False):
            m = scene()
            if mort:
                corps.mourir(m, "joueur", cause="epreuve")
            else:
                corps.endormir(m, "joueur")
            m = recharger(m)
            for action in ("attendre", "observer"):
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as ctx:
                    Moteur(m).preparer(proposition(action))
                e = ctx.exception
                self.assertIn("auteur=joueur", e.attendu)
                self.assertIn("fin.cause=epreuve" if mort else "conscient=false", e.attendu)
                self.assertIn("fin=null" if mort else "conscient=true", e.attendu)
                self.assertNotIn("auteur=", str(e))
                self.assertEqual(recharger(m).data, avant)
                self.assertIn("terminée" if mort else "sans connaissance", regarder(m))

    def test_depouilles_corps_visibles_sans_portrait_vivant_ni_voix(self):
        for id in ("aubin", "brune"):
            for connu in (False, True):
                with self.subTest(id=id, connu=connu):
                    m = reunir(scene(), id)
                    m.data["noms_connus"] = [id] if connu else []
                    m.objets[id].update(portrait="Un visage ridé ; il parle sans cesse.",
                        maniere_de_parler="Une voix sifflante.",
                        facettes={"silhouette": {"texte": "Un manteau brun couvre les épaules."},
                                  "voix": {"texte": "Voix sifflante."},
                                  "temperament": {"texte": "Une humeur joyeuse."}})
                    m.objets[id]["pv"] = 1
                    corps.mourir(m, id)
                    m = recharger(m)
                    o = m.objets[id]
                    self.assertNotIn("portrait", o)
                    self.assertNotIn("maniere_de_parler", o)
                    vue = next(o for o in m.contexte()["objets_perceptibles"] if o["type"] == "depouille")
                    self.assertTrue(vue["etat_corps"]["mort"])
                    self.assertEqual(vue["etat_corps"]["blessure"], 2)
                    from donjon.narration import attestations
                    self.assertTrue(attestations(m, m.contexte()))
                    moteur = Moteur(m)
                    texte = moteur.executer(moteur.preparer(proposition("examiner", noms.reference(m, id))))
                    m = recharger(m)
                    self.assertIn("grièvement blessé", texte)
                    self.assertIn("manteau brun", texte)
                    for sortie in (texte, json.dumps(vue, ensure_ascii=False)):
                        for interdit in ("sifflante", "joyeuse", "parle sans cesse"):
                            self.assertNotIn(interdit, sortie)
                        if not connu:
                            self.assertNotIn(m.data["defunts"][id]["nom"].split(",")[0], sortie)
                    self.assertEqual(o["type"], "depouille")
                    moteur = Moteur(m)
                    fouille = moteur.executer(moteur.preparer(proposition("toucher", noms.reference(m, id))))
                    m = recharger(m)
                    self.assertNotIn("sifflante", fouille)
                    self.assertEqual(m.objets[id]["type"], "depouille")

    def test_mimo_rejets_et_actions_sur_deux_scenes_apres_reprise(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("Dépendance MiMo facultative absente ; exécuter dans .venv-mimo")
        # Réutilise les parcours publics : transports simulés, état sauvé avant affichage,
        # scènes crypte/atelier et les deux rejets archivés, sans appel réseau.
        from tests import test_fournisseurs_jeu as fournisseurs, test_mimo as mimo
        fournisseurs.ParcoursFournisseursTests()._parcours("mimo", correction=True)
        mimo.MiMoTests().test_cli_mimo_rejoue_deux_rejets_reels_avec_correction_bornee()

    def test_un_pnj_designe_le_defunt_d_apres_sa_propre_vue(self):
        for id in ("aubin", "brune"):
            m = reunir(scene(), "marchand", id)
            m.objets["marchand"]["connait_noms"] = []
            lire(m, "marchand")["noms"] = []
            lire(m, "marchand")["croyances"].pop(id, None)
            orienter(m, "marchand", id)
            m.data["personnages_vus"] = []
            m.joueur.update(salle="chambre_cloche", position=[1, 1])
            corps.mourir(m, id)
            percevoir_tous(m)
            m = recharger(m)
            noyau = {"type": "mort_vue", "objet": id}
            attendu = noms.nom(m, id, observateur="marchand")
            self.assertNotEqual(attendu, "une personne inconnue")
            self.assertEqual(phrase(m, noyau, "marchand"), attendu + " est mort" + ("e" if id == "brune" else ""))
            self.assertEqual(noms.nom(m, id), "une personne inconnue")
            # Inverse : le joueur voit le corps, le PNJ ne l'a jamais vu.
            lire(m, "marchand")["croyances"].pop(id, None)
            placer(m, "marchand", "crypte", [1, 1])
            m.joueur.update(salle="antichambre", position=[2, 4], orientation="sud")
            m = recharger(m)
            self.assertEqual(noms.nom(m, id, observateur="marchand"), "une personne inconnue")


if __name__ == "__main__":
    unittest.main()
