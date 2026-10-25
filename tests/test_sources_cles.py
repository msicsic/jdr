"""Lot 85 b : la source désigne une clé du seul dossier reçu, avant affichage et sauvegarde."""
import copy
import unittest

from donjon.biens import compte
from donjon.monde import ErreurMonde
from donjon.narration import consigner, controler
from donjon.rendu import decrire_comptes, regarder
from donjon.sources import resoudre_sources
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class SourcesClesTests(unittest.TestCase):
    def test_cles_chemins_et_fiches_sans_deviner_de_suffixe(self):
        faits = {'conversation_validee': {'faits': ['dit'], 'repondent': ['aubin']},
            'comptes': {'issue': [{'montant': 2}]},
            'signes_percus': [{'id': 'signe:1', 'texte': 'Tremble.'}],
            'impressions': [{'id': 'impression:signe:1', 'texte': 'Semble avoir peur.'}],
            'objet:lampe': {'id': 'lampe'}, 'souvenirs': [{'id': 'lampe'}]}
        avant = copy.deepcopy(faits)
        for source, cle in (('conversation_validee.faits', 'conversation_validee'),
                            ('comptes.issue', 'comptes'), ('comptes.issue[0].montant', 'comptes'),
                            ('signes_percus.0.texte', 'signes_percus'),
                            ('signes_percus.signe:1.texte', 'signes_percus'),
                            ('signe:1', 'signes_percus'), ('impression:signe:1', 'impressions'),
                            ('lampe', 'objet:lampe'), ('objet:lampe', 'objet:lampe')):
            with self.subTest(source=source):
                self.assertEqual(resoudre_sources([source], faits), ([cle], []))
        for source in ('conversation_validee.invente', 'comptes.issue[9]', 'comptes.issue[0].absent',
                       'signe:2', 'Nom privé', 'dit'):
            self.assertEqual(resoudre_sources([source], faits), ([], [source]))
        self.assertEqual(faits, avant)
        faits['autre'] = [{'id': 'signe:1'}]
        self.assertEqual(resoudre_sources(['signe:1'], faits), ([], ['signe:1']))
        # La clé littérale prime sur une interprétation en chemin.
        faits['comptes.issue'] = {'autre': True}
        self.assertEqual(resoudre_sources(['comptes.issue'], faits), (['comptes.issue'], []))

    def test_remboursements_chemins_luna_console_puis_recharge(self):
        for script, qui, nom in (('soir-appel', 'aubin', 'Aubin'), ('comptes', 'marchand', 'Gorm')):
            with self.subTest(script=script):
                m = banc(script, noms_connus=['marchand', 'aubin', 'brune', 'ilse'])
                avant = m.joueur['or']
                mots = f'{nom}, rends-moi les deux pièces que tu me dois.'
                texte = f'{nom} te rend les deux pièces.'
                a = rapport({**ligne('mecanique', sources=['conversation_validee.faits', 'comptes.issue']),
                    'portee_mecanique': 'etablie', 'comptes': [compte(qui, 'joueur', montant=2, etat='rendu')]})
                r, sortie, appels = jouer(recharger(m), mots,
                    [parole(mots, ('reclamer', '', '', ''), personnage=qui), dialogue(texte)], [a])
                r = recharger(r)
                self.assertEqual(r.joueur['or'], avant + 2)
                self.assertFalse(any(d['de'] == qui for d in r.data['dettes']))
                self.assertNotIn(f'{nom} te doit 2 pièces', decrire_comptes(r))
                self.assertIn(texte, sortie)
                self.assertEqual(r.data['narrations_mj'][-1]['sources'], ['comptes', 'conversation_validee'])
                self.assertFalse(any('controle_narratif' in entree for _, entree in appels))
                for fonction, entree in appels:
                    if fonction in ('repondre_au_joueur', 'auditer_narration'):
                        self.assertEqual(next(iter(entree)), 'sources_autorisees')
                        self.assertEqual(entree['sources_autorisees'], list(entree['faits']))

    def test_signes_impressions_et_objets_en_console_sans_relance(self):
        for script in ('signes-ecart', 'signes-guet'):
            m = banc(script, noms_connus=['marchand', 'aubin', 'brune', 'ilse'])
            faits = m.contexte()
            for cle in ('signes_percus', 'impressions', 'objets_perceptibles'):
                if not faits.get(cle):
                    continue
                fiche = faits[cle][0]
                if cle == 'objets_perceptibles':
                    source, texte = fiche['id'], 'Tu peux regarder autour de toi.'
                else:
                    source, texte = fiche['id'], fiche['texte']
                with self.subTest(script=script, cle=cle):
                    avant, vue = copy.deepcopy(m.objets), regarder(m)
                    a = rapport({**ligne('mecanique', sources=[source]), 'portee_mecanique': 'etablie'})
                    r, sortie, appels = jouer(recharger(m), 'Que remarques-tu ?', [dialogue(texte)], [a])
                    r = recharger(r)
                    self.assertEqual(r.objets, avant)
                    self.assertEqual(regarder(r), vue)
                    self.assertIn(texte, sortie)
                    self.assertIn(texte, str(r.data['narrations_mj']))
                    self.assertFalse(any('controle_narratif' in entree for _, entree in appels))

    def test_source_inexistante_ecartee_attendu_complet_et_garde_de_sauvegarde(self):
        for script in ('signes-ecart', 'signes-noir'):
            m = banc(script, noms_connus=[])
            avant = copy.deepcopy(m.data)
            faits = {'salle': {}, **{f'cle_{i}': {} for i in range(20)}}
            a = rapport({**ligne('mecanique', sources=['salle.invente']), 'portee_mecanique': 'etablie'})
            texte = 'La porte est fermée.'
            controle = controler(texte, a, faits)
            self.assertEqual(controle['segments'][0]['sources'], [])
            self.assertEqual(len(controle['obstacles']), 1)
            attendu = controle['obstacles'][0]['attendu']
            self.assertIn('salle.invente', attendu)
            for cle in faits:
                self.assertIn(cle, attendu)
            with self.assertRaises(ErreurMonde) as erreur:
                consigner(m, {**dialogue(texte), '_audit': {'texte_initial': texte,
                    'segments': a['segments'], 'faits': faits, 'fondement': texte}})
            self.assertEqual(erreur.exception.attendu, attendu)
            self.assertEqual(recharger(m).data, avant)
