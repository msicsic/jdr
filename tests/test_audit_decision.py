"""Le texte exact et la prose libre passent par le même contrat sauvegardé."""
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.mj import MJOpenAI
from donjon.monde import Monde, ErreurMonde
from donjon.narration import (controler, consigner, schema_audit, segments,
                              segments_etablis, attestations, NATURES, AuditIllisible)
from donjon.rendu import regarder
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger
from tests.test_verdict_coherent import crypte


class AuditDecisionTests(unittest.TestCase):
    def test_toutes_les_paires_du_schema_sont_coherentes(self):
        for faits in ({'salle': {}}, {'perception': {}, 'comptes': {}, 'echanges_passes': {}}):
            variantes = schema_audit(faits, [0])['properties']['segments']['properties']['0']['anyOf']
            paires = set()
            for variante in variantes:
                p = variante['properties']
                nature, = p['nature']['enum']
                for portee in p['portee_mecanique']['enum']:
                    ligne = {'nature': nature, 'portee_mecanique': portee, 'sources': list(faits)}
                    for cle in variante['required']:
                        if cle not in ligne:
                            ligne[cle] = {'array': [], 'object': {}}.get(p[cle]['type'], '')
                    # Le contrôleur peut refuser le texte, jamais lire une paire
                    # produite par le schéma comme deux jugements incompatibles.
                    rapport = controler('Une assertion à contrôler.', {'segments': {'0': ligne}}, faits)
                    self.assertEqual(controler('Une assertion à contrôler.',
                        {'segments': rapport['segments']}, faits), rapport)
                    verdict = rapport['segments'][0]['verdict']
                    paires.add((verdict, portee))
                    if nature == 'mecanique' and portee in ('sans_fondement', 'contradictoire'):
                        self.assertTrue(rapport['obstacles'])
            interdites = {('mecanique', 'sans_fondement'), ('mecanique', 'contradictoire'),
                          ('invention_protegee', 'etablie'), ('contradictoire', 'etablie')}
            toutes = {(v, p) for v in NATURES for p in
                      ('aucune', 'etablie', 'sans_fondement', 'contradictoire')}
            self.assertEqual(paires, (toutes - interdites) |
                {('invention_protegee', 'sans_fondement'), ('contradictoire', 'contradictoire')})
            for verdict, portee in interdites:
                with self.subTest(verdict=verdict, portee=portee), self.assertRaises(AuditIllisible):
                    controler('Une assertion à contrôler.', {'segments': {'0': {
                        'verdict': verdict, 'portee_mecanique': portee, 'sources': list(faits),
                        'motif': 'Rapport forgé.'}}}, faits)
            for complement in ({'verdict': 'mecanique'}, {'nature': 'invention_protegee'},
                               {'portee_mecanique': []}):
                with self.subTest(complement=complement), self.assertRaises(AuditIllisible):
                    controler('Une assertion à contrôler.', {'segments': {'0': {
                        'nature': 'mecanique', 'portee_mecanique': 'sans_fondement',
                        'sources': list(faits), 'motif': 'Rapport forgé.', **complement}}}, faits)

    def test_console_texte_exact_libre_et_melange_apres_recharge(self):
        for defi in (False, True):
            for melange in ('moteur', 'libre', 'melange'):
                with self.subTest(defi=defi, texte=melange), tempfile.TemporaryDirectory() as tmp:
                    chemin = Path(tmp) / 'partie.json'
                    appels, textes, originaux = [], [], []
                    libre = 'Une odeur de pierre mouillée flotte autour de toi.'
                    def appeler(mj, instructions, entree, intention, fonction, schema):
                        appels.append((fonction, entree))
                        if fonction == 'repondre_au_joueur':
                            moteur = next(s for t in entree['faits']['attestations'] for s in segments(t)
                                          if s.startswith('Tu te trouves'))
                            texte = moteur if melange == 'moteur' else libre if melange == 'libre' else moteur + ' ' + libre
                            textes.append(texte)
                            originaux.append(copy.deepcopy(mj._monde_controle.objets))
                            return dialogue(texte)
                        self.assertEqual(fonction, 'auditer_narration')
                        self.assertEqual(list(entree['segments'].values()), [libre])
                        self.assertEqual(list(entree['segments']), ['1' if melange == 'melange' else '0'])
                        return {'segments': {i: {'verdict': 'ambiance', 'portee_mecanique': 'aucune',
                            'sources': [], 'entites': ['odeur de pierre'], 'comptes': [], 'eclairages': []}
                            for i in entree['segments']}}
                    with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                          patch.object(MJOpenAI, '_appeler_brut', appeler),
                          patch('builtins.input', side_effect=['mj Que vois-je ?', 'quitter']),
                          patch('sys.stdout', io.StringIO()) as sortie):
                        args = ['--console', '--save', str(chemin), '--connexion', 'api']
                        self.assertEqual(jeu.main(args + (['--defi'] if defi else [])), 0)
                    reprise = Monde.charger(chemin)
                    self.assertEqual(len(appels), 1 if melange == 'moteur' else 2)
                    self.assertIn(textes[0], sortie.getvalue())
                    self.assertEqual(reprise.data['narrations_mj'][-1]['texte'], textes[0])
                    self.assertEqual(reprise.objets, originaux[0])
                    if melange != 'moteur':
                        self.assertIn(libre, str(reprise.contexte()['ambiance_etablie']))
                    self.assertEqual(regarder(recharger(reprise)), regarder(reprise))

    def test_refus_compact_garde_le_motif_et_attendu(self):
        texte = 'Une seconde cloche apparaît.'
        compacte = {'verdict': 'invention_protegee', 'portee_mecanique': 'sans_fondement',
                    'sources': [], 'motif': 'Objet sans fondement.'}
        ancienne = {**compacte, 'locuteur': '', 'citation': '', 'presentation': '', 'entites': []}
        a = controler(texte, {'segments': {'0': ancienne}}, {})
        b = controler(texte, {'segments': {'0': compacte}}, {})
        self.assertEqual(a, b)
        self.assertIn('Objet sans fondement.', b['obstacles'][0]['attendu'])
        self.assertFalse(segments_etablis(texte, {'demande': texte,
                          'retour_moteur': {'attendu': texte, 'proposition_refusee': {'texte': texte}}}))

    def test_attestation_changee_refusee_avant_sauvegarde(self):
        m = crypte()
        texte = next(s for t in attestations(m, m.contexte()) for s in segments(t) if s.startswith('Tu te trouves'))
        faits = {'attestations': [texte]}
        rapport = controler(texte, {'segments': {}}, faits)
        rapport.update(faits=faits, texte_initial=texte, fondement=texte, fondement_paroles='')
        m.joueur['salle'] = next(s for s in m.data['salles'] if s != m.joueur['salle'])
        with self.assertRaises(ErreurMonde):
            consigner(m, {**dialogue(texte), '_audit': rapport})

    def test_schema_ne_demande_que_les_champs_du_verdict(self):
        variantes = schema_audit({'salle': {}}, [2])['properties']['segments']['properties']['2']['anyOf']
        for v in variantes:
            p = v['properties']
            verdict = p['nature']['enum'][0]
            self.assertEqual(set(p), set(v['required']))
            self.assertEqual('locuteur' in p, verdict in ('parole', 'engagement'))
            self.assertEqual('entites' in p, verdict in ('ambiance', 'engagement'))
            if 'motif' in p:
                self.assertEqual(p['motif']['maxLength'], 240)

    def test_refus_exact_et_citation_historique_sans_nouvelle_parole(self):
        for texte, faits in (
                ('Cet objet est trop loin.', {'retour_moteur': {'obstacle': 'Cet objet est trop loin.',
                    'attendu': 'cible = un objet à portée de main'}}),
                ('« La pierre chante. »', {'paroles_entendues': [{'texte': 'La pierre chante.'}]})):
            with self.subTest(texte=texte):
                m = recharger(crypte())
                avant = copy.deepcopy(m.objets)
                mj = MJOpenAI('gpt-6-luna')
                with patch.object(mj, '_appeler_brut', return_value=dialogue(texte)) as appel:
                    reponse = mj._appeler('instr', {'faits': faits}, 'que sais-je ?', 'repondre_au_joueur', {})
                self.assertEqual(appel.call_count, 1)
                consigner(m, {**reponse, '_audit': mj._audit_courant})
                reprise = recharger(m)
                self.assertEqual(reprise.objets, avant)
                self.assertEqual(reprise.data['narrations_mj'][-1]['texte'], texte)
                self.assertFalse(reprise.data.get('paroles_pnj'))

    def test_couverture_exacte_issue_ne_credite_pas_une_issue_partielle(self):
        from donjon.biens import compte
        textes = ['Tu reçois trois pièces.', 'Tu dois encore une planche.']
        comptes = [compte('marchand', 'joueur', montant=3, etat='rendu'),
                   compte('joueur', 'marchand', objet='planches', montant=1)]
        faits = {'comptes': {'issue': comptes},
                 'conversation_validee': {'faits': textes, 'comptes': comptes}}
        complet = controler(' '.join(textes), {'segments': {}}, faits)
        self.assertFalse(complet['obstacles'])
        partiel = controler(textes[0], {'segments': {}}, faits)
        self.assertTrue(partiel['obstacles'])
        self.assertIn('omet un compte', partiel['obstacles'][0]['motif'])

