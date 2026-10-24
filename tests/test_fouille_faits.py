"""Une découverte vient d'une perception exécutée, avant affichage et recharge."""
import copy
import unittest

from donjon.atelier import nouveau_atelier
from donjon.defi import nouveau_defi
from donjon.moteur import proposition
from donjon.portee_narrative import controler_usages, descriptions
from donjon.refus import RapportIllisible
from donjon.rendu import decrire
from donjon.spatial import installer
from tests.test_audits_attendu import jouer
from tests.test_relances_luna import action
from tests.test_tensions import recharger


def faits(ajout, suite=None):
    return {"mode": "etablir_faits", "texte": "", "faits": [],
            "proposition": {"ajouts": [ajout], **({"suite": suite} if suite else {})}}


def revue(reponse, perception=False, indice=False):
    return {"usages": [{"perception_requise": perception, "indice": indice,
                        "motif": "La demande exige une perception." if perception else ""}],
            "descriptions": [{"representation": e["representations_autorisees"][0],
                              "mobilite": [], "placement": "aucun", "impact_scenario": "aucun",
                              "capacites": [], "fragments": [{"texte": e["texte"],
                                  "portee": "sujet", "preuve": "", "motif": ""}]}
                             for e in descriptions(reponse)]}


class FouilleFaitsTests(unittest.TestCase):
    def test_recherche_relais_et_fouille_atelier_refusent_les_faits_puis_executent(self):
        for m, cible, saisie, nom, texte in (
                (nouveau_defi(depart="fixe"), "antichambre_sol",
                 "je cherche des traces de pas sur le sol", "surface du sol",
                 "La poussière forme une fine pellicule sur la pierre."),
                (nouveau_atelier(), "cour_sol", "je fouille ce coin de la cour",
                 "pavage", "La pierre est rugueuse et claire.")):
            for avec_suite in (False, True):
                with self.subTest(cible=cible, suite=avec_suite):
                    installer(m)
                    m = recharger(m)
                    avant = copy.deepcopy(m.data)
                    p = proposition("examiner", cible)
                    reponse = faits({"type": "detail", "ancrage": cible,
                                     "nom": nom, "genre": "m", "texte": texte},
                                    p if avec_suite else None)
                    r, affichage, appels = jouer(m, "mj " + saisie,
                        [reponse, revue(reponse, perception=True), action(p)], [])
                    self.assertEqual([f for f, _ in appels],
                        ["repondre_au_joueur", "auditer_portee", "repondre_au_joueur", "auditer_action"])
                    contexte = appels[1][1]
                    self.assertEqual(contexte["demande"], saisie)
                    self.assertEqual(contexte["proposition_faits"], reponse["proposition"])
                    refus = appels[2][1]["controle_narratif"][0]
                    self.assertIn("examiner", refus["attendu"])
                    self.assertIn(cible, refus["attendu"])
                    self.assertIn("proposition.ajouts[0]", refus["attendu"])
                    self.assertNotIn(refus["attendu"], affichage)
                    self.assertNotIn(texte, affichage)
                    temoin, _, _ = jouer(m, "mj " + saisie, [action(p)], [])
                    self.assertEqual(r.objets, temoin.objets)
                    self.assertEqual(r.data.get("faits_vus", []), avant.get("faits_vus", []))
                    resultat = r.data["conversation"][-1]
                    self.assertEqual(resultat["nature"], "resultat_moteur")
                    self.assertIn(resultat["reponse"], affichage)
                    self.assertEqual(resultat["reponse"], temoin.data["conversation"][-1]["reponse"])
                    self.assertIn(decrire(r, cible, detail=True), resultat["reponse"])
                    self.assertEqual(r.data["minutes"], avant["minutes"])

    def test_indice_sans_quete_refuse_meme_si_pas_de_recherche_demandee(self):
        m = nouveau_atelier()
        installer(m)
        ajout = {"type": "detail", "ancrage": "cour_sol", "nom": "sillons",
                 "genre": "m", "texte": "Des sillons montrent qu'une lourde charge a été traînée ici."}
        mauvais = faits(ajout)
        bon = faits({**ajout, "nom": "pierre claire", "texte": "La pierre a une teinte claire."})
        r, texte, appels = jouer(m, "mj décris le pavage", [
            mauvais, revue(mauvais, indice=True), bon, revue(bon)], [])
        refus = appels[2][1]["controle_narratif"][0]
        self.assertIn("indice", refus["attendu"])
        self.assertIn("examiner", refus["attendu"])
        self.assertNotIn(ajout["texte"], texte)
        self.assertNotIn(ajout["texte"], str(r.data))
        self.assertIn(bon["proposition"]["ajouts"][0]["texte"], texte)

    def test_qualification_sans_prose_ne_contourne_pas_la_perception(self):
        m = nouveau_atelier()
        installer(m)
        p = faits({"type": "qualification", "ancrage": "hache",
                   "capacites": [{"nature": "son", "intensite": 1}]})
        r, texte, appels = jouer(m, "mj je scrute la hache à la recherche de marques", [
            p, revue(p, perception=True), action(proposition("examiner", "hache"))], [])
        self.assertEqual(appels[1][1]["descriptions"], [])
        self.assertNotIn("auditer_capacites", [f for f, _ in appels])
        self.assertEqual(r.objets["hache"], m.objets["hache"])
        self.assertEqual(r.data["conversation"][-1]["nature"], "resultat_moteur")
        self.assertIn(decrire(r, "hache", detail=True), texte)

    def test_detail_legitime_persiste_sans_repetition_du_support_quel_que_soit_son_nom(self):
        for nom in ("sol", "surface du sol", "teinte claire"):
            with self.subTest(nom=nom):
                m = nouveau_defi(depart="fixe")
                installer(m)
                ajout = {"type": "detail", "ancrage": "antichambre_sol", "nom": nom,
                         "genre": "m", "texte": "La pierre présente une teinte mate et claire."}
                p = faits(ajout)
                r, texte, appels = jouer(m, "mj décris l'aspect de la pierre", [p, revue(p)], [])
                self.assertIn(ajout["texte"], texte)
                self.assertNotIn("sur le sol", texte)
                id = r.data["faits_vus"][-1]["objet"]
                self.assertEqual(r.objets[id]["lieu"], ajout["ancrage"])
                self.assertIn(ajout["texte"], decrire(r, id, detail=True))
                self.assertEqual(len(appels), 2)

    def test_rapport_exhaustif_et_une_cause_par_refus_pour_tous_les_types(self):
        m = nouveau_defi(depart="fixe")
        installer(m)
        for nature in ("detail", "objet", "inscription", "qualification", "parole", "evolution"):
            with self.subTest(nature=nature):
                p = {"ajouts": [{"type": nature, "ancrage": "antichambre_sol"}]}
                with self.assertRaises(RapportIllisible):
                    controler_usages(p, {"usages": []})
                with self.assertRaises(RapportIllisible):
                    controler_usages(p, None)
                refus = controler_usages(p, {"usages": [{"perception_requise": True,
                                                        "indice": True, "motif": "Découverte."}]})
                self.assertEqual(len(refus), 2)
                self.assertNotEqual(refus[0]["motif"], refus[1]["motif"])


if __name__ == "__main__":
    unittest.main()
