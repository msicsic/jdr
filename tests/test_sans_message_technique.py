"""Une forme refusée et un typage contesté gardent une réponse de jeu, sauvée."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.mj import MJOpenAI, demande_precision
from donjon.monde import Monde
from donjon.narration import attestations, repli
from donjon.rendu import regarder, fiche, carte
from donjon.paroles import prevue
from donjon.atelier import nouveau_atelier
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger
from tools.verifier_websocket_jeu import Interface


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

    def test_repli_perceptible_independant_du_mode_invalide_sauve_avant_affichage(self):
        # Même garantie pour une description impérative et pour un mauvais mode action :
        # le contenu rejeté ne détermine ni la cible ni la réponse de secours.
        for cible in ("le mur de l'atelier", "la bobine de ficelle"):
            for faux in ({'mode': 'action'}, {'mode': 'etablir_faits', 'texte': '',
                         'faits': [], 'proposition': None}):
                with self.subTest(cible=cible, faux=faux), tempfile.TemporaryDirectory() as tmp:
                    m = recharger(nouveau_atelier())
                    saisie = 'décris ' + cible
                    attendu = repli(m, {'attestations': attestations(m, m.contexte())}, saisie,
                                    defaut=demande_precision())
                    self.assertNotEqual(attendu, demande_precision())
                    avant = copy.deepcopy(m.data)
                    vues = (regarder(m), fiche(m), carte(m))
                    chemin = Path(tmp) / 'partie.json'
                    m.sauver(chemin)
                    interface = Interface(['mj ' + saisie, 'quitter'], chemin)
                    appels = []
                    def appeler(_instructions, entree, _intention, fonction, _schema):
                        appels.append((fonction, entree))
                        self.assertEqual(fonction, 'repondre_au_joueur')
                        return copy.deepcopy(faux)
                    with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                          patch.object(MJOpenAI, '_appeler_brut', side_effect=appeler)):
                        self.assertEqual(jeu.main(['--console', '--connexion', 'api', '--save', str(chemin)],
                                                 interface=interface), 0)
                    r = Monde.charger(chemin)
                    self.assertEqual(len(appels), 2)
                    self.assertIn('retour_forme', appels[1][1])
                    self.assertEqual(r.data['conversation'][-1]['reponse'], attendu)
                    self.assertIn(attendu, interface.deja_sauves)
                    self.assertEqual(r.data['narrations_mj'][-1]['sources'], ['moteur'])
                    self.sans_technique('\n'.join(interface.sorties))
                    for cle in ('objets', 'joueur', 'revision', 'minutes', 'journal', 'jets',
                                'faits_locaux', 'esprits'):
                        self.assertEqual(r.data.get(cle), avant.get(cle), cle)
                    self.assertEqual((regarder(r), fiche(r), carte(r)), vues)
                    etat = copy.deepcopy(r.data)
                    reprise = Interface(['regarder', 'inventaire', 'quitter'], chemin)
                    self.assertEqual(jeu.main(['--console', '--offline', '--save', str(chemin)],
                                             interface=reprise), 0)
                    self.assertEqual(Monde.charger(chemin).data, etat)

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

    def test_omission_non_examinee_ne_disparait_pas(self):
        for preparation_refusee in (False, True):
            with self.subTest(preparation_refusee=preparation_refusee):
                m = banc("noms-dialogue")
                saisie = "Aubin, as-tu du bois ?"
                faux = parole(saisie, ("ressource", "bois", "", ""), personnage="aubin")
                faux['proposition']['operations_demandees']['proposition'] = True
                if preparation_refusee:
                    faux["proposition"]["contenu"][0]["valeur"] = "champ interdit"
                vide = parole(saisie, personnage="aubin")
                r, sortie, _ = jouer(m, saisie, [faux, vide], [], revues=[{}] * 6)
                self.assertNotIn("Tu dis", sortie)
                self.assertFalse(recharger(r).data.get('paroles_joueur'))
                self.assertEqual(r.joueur["or"], m.joueur["or"])


if __name__ == "__main__":
    unittest.main()
