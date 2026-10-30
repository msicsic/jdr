"""Une parole de service se juge, s'exécute et s'abandonne sur le même devis autonome.

Les parcours utilisent le moteur réel, la sauvegarde et les textes rendus au joueur.
"""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon.biens import bourse
from donjon.deliberation import promesse_en_cours, refus_retenu, retenir_refus
from donjon.echanges import demander, engager, engagements_echus, executer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.paroles import preparer_parole
from donjon.planification import devis_pulsion
from donjon.paroles import engagements_enregistres
from tests.support import calme, presentes, regarder
from tests import test_crochetage_surenchere as cs
from tests.test_parts_achetees import antichambre_du_banc, parole
from tests.test_refus_retenus import face_a_face
from tests.test_tensions import chronique, recharger, vivre


def relais_reel():
    source = Path(__file__).parent / "data" / "taches_relais42_avant_part.json.gz"
    return recharger(Monde(json.loads(gzip.decompress(source.read_bytes()))))


def sans_flamme(m, vendeur):
    """Le vendeur a du combustible mais n'a aucun moyen cru de produire une flamme."""
    # La lumière du jour permet de voir les échanges sans fournir une flamme.
    m.data["salles"][m.objets[vendeur]["lieu"]]["lumiere_naturelle"] = 1
    for k, o in m.objets.items():
        if "allumage" in o.get("usages", ()) or "allume" in o:
            if "allumage" in o.get("usages", ()):
                # Il ne connaît aucun outil d'allumage (sans changer les moyens du joueur).
                lire(m, vendeur)["croyances"].pop(k, None)
            else:
                o.update(allume=False, combustible=0)
                croire(m, vendeur, k, "etat", {"allume": False, "charge": False, "faible": False}, "vu")


class TachesPayeesTests(unittest.TestCase):
    def test_relais42_la_part_ne_reste_pas_due_soixante_minutes(self):
        m = relais_reel()
        # Sauvegarde exacte de main 06602a6, juste avant l'achat de la minute 151.
        self.assertEqual(m.data["minutes"], 151)
        # 3c : son abri inquiet surveille désormais Brune ; il peut alors ne pas voir
        # Gorm repartir avec la torche, et croire encore pouvoir la lui demander.
        # Cette régression de paiement isole le service de ce séjour social nouveau.
        calme(m, "aubin")
        m, _ = vivre(m, 5)
        annules = [s for s in lire(m, "aubin")["memoire"] if s["type"] == "engagement_abandonne"]
        self.assertTrue(annules, chronique(m))
        self.assertLess(annules[0]["minute"], 156)
        self.assertIsNone(promesse_en_cours(m, "marchand", "planches"))
        self.assertIsNotNone(refus_retenu(m, "marchand", "aubin", ("acheter",), "planches"))
        self.assertFalse([x for x in lire(m, "aubin")["engagements"] if x["condition"].get("objet") == "brasero"])
        self.assertTrue(any("part des planches" in t and "pas été servie" in t for t in chronique(m)))
        # Gorm a repris lui-même l'entretien après avoir été libéré de la promesse.
        self.assertTrue(m.objets["brasero"]["allume"])
        # Corvus est à la chambre de la cloche : aucun faux service annoncé à distance.
        self.assertEqual(m.joueur["salle"], "chambre_cloche")

    def test_relais_refus_connu_ni_vente_ni_encaissement_et_refus_retenu(self):
        m = relais_reel()
        retenir_refus(m, "aubin", "marchand", "demander", "necessaire", objet="torche")
        avant = (bourse(m, "marchand"), bourse(m, "aubin"))
        # Le joueur assiste à l'échange ; les gestes et leur texte passent par le contrat social.
        m.joueur.update(salle="antichambre", position=[1, 4], orientation="est")
        regarder(m, "joueur", "aubin")
        percevoir_tous(m)
        lignes = []
        self.assertFalse(executer(m, "marchand", lire(m, "marchand")["intention"]["plan"][0], lignes))
        m = recharger(m)
        self.assertEqual((bourse(m, "marchand"), bourse(m, "aubin")), avant)
        self.assertEqual(lire(m, "aubin")["engagements"], [])
        self.assertIsNotNone(refus_retenu(m, "marchand", "aubin", ("acheter",), "planches"))
        self.assertTrue(any("(impossible)." in t for t in chronique(m)))
        self.assertTrue(lignes)  # Les noms encore inconnus restent masqués au joueur.

    def test_tilo_sans_flamme_ne_fait_pas_travailler_odile(self):
        m = cs.TacheAccepteeTests().tilo_paye_pour_l_atre(False)
        self.assertGreater(m.objets["bois_reserve"]["charges"], 0)
        avant = (bourse(m, "odile"), bourse(m, "tilo"))
        self.assertEqual(engager(m, "odile", "tilo", {"objet": "atre", "allume": True}, 20), "impossible")
        m = recharger(m)
        self.assertEqual((bourse(m, "odile"), bourse(m, "tilo")), avant)
        self.assertEqual(lire(m, "tilo")["engagements"], [])
        self.assertIsNone(devis_pulsion(m, "tilo", {"objet": "atre", "allume": True}, "odile"))

    def test_autre_service_le_payeur_ne_lui_allume_pas_sa_lanterne(self):
        m = cs.TacheAccepteeTests().tilo_paye_pour_l_atre(False)
        # Même nature, autre chaîne : Tilo sait la lanterne éteinte dans sa main et le briquet d'Odile.
        sans_flamme(m, "tilo")
        m.objets["lanterne_etable"].update(lieu="tilo", allume=False, combustible=40)
        croire(m, "tilo", "lanterne_etable", "lieu", "tilo", "vu", salle=None, case=None)
        croire(m, "tilo", "lanterne_etable", "etat", {"allume": False, "charge": True, "faible": False}, "vu")
        croire(m, "tilo", "briquet_odile", "lieu", "odile", "vu", salle=None, case=None)
        # Un prêt de l'outil reste autorisé ; refusé, le seul recours serait de faire allumer par Odile.
        retenir_refus(m, "tilo", "odile", "demander", "necessaire", objet="briquet_odile")
        m = recharger(m)
        self.assertEqual(engager(m, "odile", "tilo", {"objet": "atre", "allume": True}, 20), "impossible")
        self.assertFalse(m.objets["lanterne_etable"]["allume"])

    def test_le_bien_du_payeur_peut_etre_emprunte_pour_agir_soi_meme(self):
        m = cs.TacheAccepteeTests().tilo_paye_pour_l_atre(False)
        # Isoler la fourniture de l'outil du secours spontané d'Odile :
        # le nouveau contact peut lui faire entreprendre elle-même l'allumage
        # pour autrui avant le retour de Tilo, et réserver alors son briquet.
        from tests.support import sans_souci
        sans_souci(m, 'odile')
        m.joueur.update(salle="salle_commune", position=[3, 3], orientation="ouest")
        # Un autre outil d'allumage, prêté par Odile : c'est Tilo qui allume ensuite.
        m.objets["briquet"].update(lieu="odile", proprietaire="odile")
        croire(m, "tilo", "briquet", "lieu", "odile", "vu", salle=None, case=None)
        m = recharger(m)
        devis = devis_pulsion(m, "tilo", {"objet": "atre", "allume": True}, "odile")
        self.assertIsNotNone(devis)
        self.assertTrue(any(e["operation"] == "demander" and e["outil"] == "briquet" for e in devis[1]))
        self.assertEqual(engager(m, "odile", "tilo", {"objet": "atre", "allume": True}, 20), "accepte")
        m, lignes = vivre(recharger(m), 15)
        self.assertTrue(m.objets["atre"]["allume"], chronique(m))
        self.assertTrue(any("allume l'âtre" in t for t in chronique(m)))
        self.assertTrue(lignes)
        self.assertEqual(m.data.get("dettes", []), [])

    def test_part_gratuite_sans_flamme_refusee_au_joueur(self):
        m = antichambre_du_banc()
        sans_flamme(m, "aubin")
        m = recharger(m)
        with patch.object(Monde, "d20", return_value=20):
            m, rapport = preparer_parole(m, parole("aubin", "Aubin, donne-moi une part de bois.", "demande", "planches"))
        m = recharger(m)
        self.assertIn("Aubin, vieux passeur ne voit pas comment te donner les planches de bac.", rapport["faits"])
        self.assertEqual(lire(m, "aubin")["engagements"], [])
        self.assertEqual(m.objets["planches"]["charges"], 2)

    def test_autre_part_sans_flamme_joss_refuse_et_le_joueur_le_lit(self):
        m = calme(creer("auberge", 1985, "fixe"), "joss")
        face_a_face(m, "joss", "mireille", "etable", cases=((5, 3), (5, 2)))
        m.joueur.update(salle="etable", position=[4, 3], orientation="est")
        sans_flamme(m, "joss")
        # Depuis la branche des noms, Corvus ne nomme que qui s'est présenté : Joss l'a fait avant la scène.
        presentes(m, "joss")
        percevoir_tous(m)
        m = recharger(m)
        charges = m.objets["fagots_etable"]["charges"]
        with patch.object(Monde, "d20", return_value=20):
            m, rapport = preparer_parole(m, parole("joss", "Joss, donne-moi du bois pour me chauffer.",
                                                 "demande", "fagots_etable"))
        m = recharger(m)
        self.assertTrue(any("ne voit pas comment" in t for t in rapport["faits"]), rapport["faits"])
        self.assertEqual(lire(m, "joss")["engagements"], [])
        self.assertEqual(m.objets["fagots_etable"]["charges"], charges)

    def test_part_payee_devenue_impossible_rendue_et_visible_au_joueur(self):
        m = antichambre_du_banc()
        m.objets["briquet"]["lieu"] = "aubin"
        croire(m, "aubin", "briquet", "lieu", "aubin", "vu", salle=None, case=None)
        # Le brasero éteint a été vu : il ne s'agit pas d'aller le regarder.
        sans_flamme(m, "aubin")
        croire(m, "aubin", "briquet", "lieu", "aubin", "vu", salle=None, case=None)
        self.assertEqual(demander(m, "joueur", "aubin", "planches", "brasero", 1), "vendu")
        # Un moyen perdu et constaté après l'accord : on ne prolonge pas l'attente.
        m.objets["briquet"]["lieu"] = "joueur"
        lire(m, "aubin")["croyances"].pop("briquet", None)
        m, lignes = vivre(recharger(m), 2)
        self.assertFalse(m.objets["brasero"]["allume"])
        self.assertEqual(lire(m, "aubin")["engagements"], [])
        self.assertEqual(m.joueur["or"], 24)
        self.assertEqual(m.data.get("dettes", []), [])
        self.assertTrue(any("te rend 1 pièce" in t for t in lignes), lignes)

    def test_promesse_gratuite_devenue_impossible_annoncee(self):
        m = antichambre_du_banc()
        m.objets["briquet"]["lieu"] = "aubin"
        croire(m, "aubin", "briquet", "lieu", "aubin", "vu", salle=None, case=None)
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "joueur", "aubin", "planches"), "promis")
        sans_flamme(m, "aubin")
        m.objets["briquet"]["lieu"] = "joueur"
        m, lignes = vivre(recharger(m), 3)
        self.assertTrue(any("sa promesse est devenue impossible" in t for t in lignes), lignes)
        self.assertEqual(lire(m, "aubin")["engagements"], [])
        self.assertTrue(any(s["type"] == "abandon_annonce" for s in lire(m, "aubin")["memoire"]))

    def test_annulation_sauvee_n_informe_pas_a_distance_et_ne_promet_plus_le_service(self):
        m = relais_reel()
        m.objets["briquet"]["lieu"] = "aubin"
        croire(m, "aubin", "briquet", "lieu", "aubin", "vu", salle=None, case=None)
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "marchand", "aubin", "planches", "brasero"), "promis")
        sans_flamme(m, "aubin")
        m.objets["briquet"]["lieu"] = "joueur"
        engagements_echus(m, "aubin")
        m = recharger(m)
        self.assertTrue(lire(m, "aubin")["engagements"][0]["annule"])
        self.assertEqual(promesse_en_cours(m, "marchand", "planches"), "aubin")
        self.assertTrue(any("abandon à annoncer" in t for t in engagements_enregistres(m, "aubin")))
        # On éprouve l'annonce de cet abandon, sans conclure un nouveau marché de combustible.
        from donjon import relations
        lire(m, "aubin")["relations"]["marchand"] = relations._nouvelle({"confiance": 10})
        # Comme le premier test sur cette capture : isoler l'annonce du séjour
        # de sécurité prioritaire (80,5 dans l'état réel), qui peut la différer.
        calme(m, "aubin")
        m, lignes = vivre(recharger(m), 3)
        self.assertIsNone(promesse_en_cours(m, "marchand", "planches"))
        self.assertFalse(any("promesse" in t for t in lignes), lignes)  # Corvus est loin de l'échange.
        self.assertTrue(any(s["type"] == "promesse_annulee" for s in lire(m, "marchand")["memoire"]))


if __name__ == "__main__":
    unittest.main()
