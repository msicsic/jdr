"""Une forme refusée et un typage contesté gardent une réponse de jeu, sauvée."""
import copy
import unittest

from donjon.paroles import prevue
from donjon.atelier import nouveau_atelier
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class SansMessageTechniqueTests(unittest.TestCase):
    def sans_technique(self, texte):
        for marque in ("Faits narratifs invalides", "Aucun ajout enregistré", "Reformule",
                       "accepté :", "proposition.contenu", "Réponse du MJ invalide"):
            self.assertNotIn(marque, texte)

    def test_description_mal_formee_corrigee_ou_repli_apres_recharge(self):
        for saisie in ("à quoi ressemble le mur de l'atelier ?", "à quoi ressemble la bobine de ficelle ?"):
            for corrigee in (False, True):
                with self.subTest(saisie=saisie, corrigee=corrigee):
                    m = recharger(nouveau_atelier())
                    avant = copy.deepcopy((m.objets, m.joueur, m.data.get("faits_locaux")))
                    faux = {"mode": "etablir_faits", "texte": "",
                            "faits": ["objet:mur_atelier", "faits_narratifs_proposables", "reperes_demandes"],
                            "proposition": None}
                    texte = "Tu n'en distingues pas davantage."
                    reponses = [faux, dialogue(texte)] if corrigee else [faux] * 3
                    r, sortie, appels = jouer(m, saisie, reponses,
                        [rapport(ligne("neutre"))] if corrigee else [])
                    self.sans_technique(sortie)
                    self.assertGreater(len(appels), 1)
                    self.assertEqual((r.objets, r.joueur, r.data.get("faits_locaux")), avant)
                    r = recharger(r)
                    self.sans_technique(str(r.data["conversation"]))
                    self.assertTrue(r.data["conversation"])
                    self.assertIn(r.data["conversation"][-1]["reponse"], sortie)
                    if corrigee:
                        self.assertEqual(r.data["conversation"][-1]["reponse"], texte)
                    else:
                        self.assertIn("mur" if "mur" in saisie else "bobine",
                                      r.data["conversation"][-1]["reponse"])

    def test_typage_refuse_ne_condamne_pas_les_mots_exacts(self):
        for nom, saisie in (("soir-noir", "il y a quelqu'un ?"),
                            ("echanges", "Vous m'entendez ?")):
            with self.subTest(nom=nom):
                m = banc(nom)
                cible = prevue(m, saisie)["personnage"]
                faux = parole(saisie, ("qui", "", "", ""), personnage=cible)
                bon = parole(saisie, ("propos", "", "", ""), personnage=cible)
                r, sortie, appels = jouer(m, saisie,
                    [faux, bon, dialogue("Ta question est entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))],
                    revues=[{"conforme": False, "motif": "Présence ou audition, pas identité."}])
                self.sans_technique(sortie)
                self.assertIn(saisie, sortie)
                self.assertIn("Tu dis", sortie)
                self.assertEqual(len(r.data["paroles_joueur"]), 1)
                self.assertEqual(r.data["paroles_joueur"][0]["texte"], saisie)
                self.assertEqual(r.joueur["or"], m.joueur["or"])
                self.assertEqual(r.data["journal"], m.data["journal"])
                self.assertIn("Ta question est entendue.", str(recharger(r).data["conversation"]))

    def test_faits_en_liste_de_libelles_n_arrivent_pas_au_joueur(self):
        for saisie in ("à quoi ressemble le mur de l'atelier ?", "à quoi ressemble la bobine de ficelle ?"):
            m = recharger(nouveau_atelier())
            faux = {"mode": "etablir_faits", "texte": "", "faits": [],
                    "proposition": {"ajouts": ["objet:mur_atelier", "faits_narratifs_proposables"]}}
            r, sortie, appels = jouer(m, saisie, [faux] * 3, [])
            self.sans_technique(sortie)
            self.assertIn("proposition.ajouts", appels[1][1]["retour_forme"]["attendu"])
            self.assertEqual(r.objets, m.objets)
            self.assertEqual(r.joueur, m.joueur)
            self.assertIn(recharger(r).data["conversation"][-1]["reponse"], sortie)

    def test_declaration_non_examinee_ne_disparait_pas(self):
        for preparation_refusee in (False, True):
            with self.subTest(preparation_refusee=preparation_refusee):
                m = banc("noms-dialogue")
                saisie = "Aubin, as-tu du bois ?"
                faux = parole(saisie, ("ressource", "bois", "", ""), personnage="aubin")
                if preparation_refusee:
                    faux["proposition"]["contenu"][0]["valeur"] = "champ interdit"
                vide = parole(saisie, personnage="aubin")
                r, sortie, _ = jouer(m, saisie, [faux, vide], [], revues=[{}] * 6)
                self.assertNotIn("Tu dis", sortie)
                self.assertFalse(recharger(r).data.get("paroles_joueur"))
                self.assertEqual(r.joueur["or"], m.joueur["or"])


if __name__ == "__main__":
    unittest.main()
