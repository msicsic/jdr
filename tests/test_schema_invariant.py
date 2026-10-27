"""L2 : contrat transport stable, disponibilités contrôlées avant tout récit."""
import copy
from contextlib import ExitStack
import json
import unittest
from unittest.mock import patch

from donjon.auberge import nouveau_auberge
from donjon.defi import nouveau_defi
from donjon.mj import MJ, verifier_disponibilite
from donjon.refus import RefusDeForme
from donjon.rendu import regarder
from tests import test_cache_kv_local as prefixe
from tests.test_repli_et_appel import jouer, dialogue, verdicts, NEUTRE
from tests.test_tensions import recharger


class SchemaInvariantTests(unittest.TestCase):
    def test_schemas_identiques_sur_deux_scenes_et_catalogues_variables(self):
        capter = prefixe.PrefixeKVTests()._capter_appel
        schemas = []
        for creer in (nouveau_defi, nouveau_auberge):
            m = creer(depart="fixe")
            avant = copy.deepcopy(m.data)
            for enrichir, intention in ((True, "Que vois-je ?"), (True, "Puis-je escalader le mur ?"),
                                       (False, "Explique.")):
                _, _, _, schema = capter(m, intention, enrichir=enrichir)
                if enrichir:
                    schemas.append(json.dumps(schema, ensure_ascii=False))
                else:
                    self.assertEqual(schema['properties']['mode']['enum'], ['dialogue'])
            with ExitStack() as pile:
                for nom in ('catalogue', 'catalogue_profil', 'catalogue_savoirs', 'catalogue_faits'):
                    pile.enter_context(patch('donjon.mj.' + nom, return_value={}))
                _, _, _, schema_vide = capter(m, 'Je regarde encore.', enrichir=True)
                schemas.append(json.dumps(schema_vide, ensure_ascii=False))
            self.assertEqual(m.data, avant)
            reprise = recharger(m)
            self.assertEqual(reprise.data, m.data)
            self.assertEqual(regarder(reprise), regarder(m))
        self.assertEqual(len(set(schemas)), 1)

    def test_modes_indisponibles_refuses_avant_audit_et_recharge_sans_effet(self):
        # Catalogue nul, isolement : chacun des modes spécialisés est indisponible.
        for creer in (nouveau_defi, nouveau_auberge):
            # Les scènes réelles passent par la console ; les catalogues sont désactivés
            # comme lorsqu'ils ont déjà été complétés dans une partie.
            for mode in ('enrichir', 'enrichir_joueur', 'enrichir_savoirs', 'etablir_faits',
                         'conversation_pnj', 'parole_joueur'):
                with self.subTest(scene=creer.__name__, mode=mode):
                    r = {'mode': mode, 'texte': '', 'faits': [], 'proposition': {}}
                    with self.assertRaises(RefusDeForme) as refus:
                        verifier_disponibilite(r, {})
                    self.assertIn(mode, refus.exception.attendu)
            # Inconnu reste écarté ; réponse neutre enregistrée et rendue après recharge.
            m = creer(depart="fixe")
            reponse = dialogue('Le silence se prolonge.')
            reponse['faits'] = ['source_inconnue']
            reprise, sortie, _ = jouer(m, 'mj Je contemple les environs.', [reponse], [verdicts(NEUTRE)])
            self.assertIn('Le silence se prolonge.', sortie)
            self.assertEqual(reprise.data['conversation'][-1]['reponse'], 'Le silence se prolonge.')
            self.assertEqual(regarder(reprise), regarder(recharger(reprise)))
            self.assertEqual(reprise.data, recharger(reprise).data)

    def test_modes_indisponibles_dans_la_console_ne_modifient_pas_le_monde(self):
        for creer, salle in ((nouveau_defi, 'chambre_cloche'), (nouveau_auberge, 'dortoir')):
            m = creer(depart='fixe')
            m.joueur['salle'] = salle
            self.assertFalse(m.contexte()['interlocuteurs'])
            with ExitStack() as pile:
                for nom in ('catalogue', 'catalogue_profil', 'catalogue_savoirs', 'catalogue_faits'):
                    pile.enter_context(patch('donjon.mj.' + nom, return_value={}))
                attendu, rendu, _ = jouer(m, 'mj Je contemple les environs.',
                    [dialogue('Le silence se prolonge.')], [verdicts(NEUTRE)])
                for mode in ('enrichir', 'enrichir_joueur', 'enrichir_savoirs', 'etablir_faits',
                             'conversation_pnj', 'parole_joueur'):
                    with self.subTest(scene=creer.__name__, mode=mode):
                        contenu = {'enrichir': {'ajouts': []}, 'enrichir_joueur': {'profil_joueur': {}},
                                   'enrichir_savoirs': {'savoirs': []}, 'etablir_faits': {'ajouts': []},
                                   'conversation_pnj': {'sujet': 'bonjour'}, 'parole_joueur': {'replique': 'bonjour'}}
                        invalide = {'mode': mode, 'texte': '', 'faits': [], 'proposition': contenu[mode]}
                        reprise, sortie, appels = jouer(m, 'mj Je contemple les environs.',
                            [invalide, dialogue('Le silence se prolonge.')], [verdicts(NEUTRE)])
                        corrections = [e['retour_forme'] for f, e in appels if 'retour_forme' in e]
                        self.assertEqual(len(corrections), 1)
                        self.assertIn(mode, corrections[0]['attendu'])
                        self.assertEqual(reprise.data, attendu.data)
                        self.assertEqual(sortie, rendu)
                        self.assertEqual(regarder(reprise), regarder(attendu))

    def test_branche_incompatible_corrigee_avant_audit_et_recharge(self):
        for creer in (nouveau_defi, nouveau_auberge):
            m = creer(depart='fixe')
            invalide = {'mode': 'action', 'texte': '', 'faits': [],
                        'proposition': {'profil_joueur': [{'champ': 'taille_cm', 'valeur': 178}]}}
            reprise, sortie, appels = jouer(m, 'mj Je contemple les environs.',
                [invalide, dialogue('Le silence se prolonge.')], [verdicts(NEUTRE)])
            correction = next(e['retour_forme'] for f, e in appels if 'retour_forme' in e)
            self.assertIn('action', correction['attendu'])
            temoin, rendu, _ = jouer(m, 'mj Je contemple les environs.',
                [dialogue('Le silence se prolonge.')], [verdicts(NEUTRE)])
            self.assertEqual(reprise.data, temoin.data)
            self.assertEqual(sortie, rendu)

    def test_question_exige_suite_avant_preparation_des_faits(self):
        for suite in (None, 'geste'):
            r = {'mode': 'etablir_faits', 'proposition': {'ajouts': [], 'suite': suite}}
            with self.assertRaises(RefusDeForme) as refus:
                verifier_disponibilite(r, {'faits_narratifs_proposables': {'supports': {'mur': {}}}}, True)
            self.assertIn('proposition.suite', refus.exception.attendu)
        verifier_disponibilite({'mode': 'etablir_faits', 'proposition': {'ajouts': [], 'suite': None}},
                              {'faits_narratifs_proposables': {'supports': {'mur': {}}}})

    def test_question_sans_suite_corrigee_sans_ajout_apres_recharge(self):
        from donjon.moteur import proposition
        for creer in (nouveau_defi, nouveau_auberge):
            m = creer(depart='fixe')
            # Les deux propositions aboutissent à la même préparation, jamais à un fait ajouté.
            geste = {'mode': 'action', 'texte': '', 'faits': [],
                     'proposition': proposition('observer')}
            for suite in ('absente', None):
                with self.subTest(scene=creer.__name__, suite=suite):
                    p = {'ajouts': []}
                    if suite is None:
                        p['suite'] = None
                    reprise, sortie, appels = jouer(m, 'mj Puis-je regarder autour de moi ?',
                        [{'mode': 'etablir_faits', 'texte': '', 'faits': [], 'proposition': p}, geste], [])
                    corrections = [e['retour_forme'] for f, e in appels if 'retour_forme' in e]
                    self.assertEqual(len(corrections), 1)
                    self.assertIn('proposition.suite', corrections[0]['attendu'])
                    temoin, rendu, _ = jouer(m, 'mj Puis-je regarder autour de moi ?', [geste], [])
                    self.assertEqual(reprise.data, temoin.data)
                    self.assertEqual(sortie, rendu)
                    self.assertEqual(regarder(reprise), regarder(temoin))

    def test_refus_disponibilite_relance_avec_attendu_et_schema_identique(self):
        m = nouveau_defi(depart='fixe')
        capter = prefixe.PrefixeKVTests()._capter_appel
        _, entree, _, schema = capter(m, 'Je regarde.')
        entree['faits']['profil_joueur_a_completer'] = {}
        appels = []
        def brut(instructions, e, intention, fonction, s):
            appels.append((copy.deepcopy(e), copy.deepcopy(s)))
            if len(appels) == 1:
                return {'mode': 'enrichir_joueur', 'texte': '', 'faits': [], 'proposition': {'profil_joueur': {}}}
            return {'mode': 'action', 'texte': '', 'faits': [], 'proposition': {'action': 'observer'}}
        mj = MJ(connexion='local')
        with patch.object(mj, '_appeler_brut', side_effect=brut):
            r = mj._appeler('', entree, 'Je regarde.', 'repondre_au_joueur', schema)
        self.assertEqual(r['mode'], 'action')
        self.assertIn('enrichir_joueur', appels[1][0]['retour_forme']['attendu'])
        self.assertEqual(appels[0][1], appels[1][1])


if __name__ == '__main__':
    unittest.main()
