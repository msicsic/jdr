"""Surfaces paresseuses : contrat MJ, console, état et rendu rechargés."""
import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jeu
from donjon.faits_locaux import preparer_faits
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.operations import sequence, etape
from donjon.rendu import regarder
from tests import test_cache_kv_local as prefixe


class SurfacesDemandeTests(unittest.TestCase):
    def capter(self, m, texte, **kwargs):
        return prefixe.PrefixeKVTests()._capter_appel(m, texte, **kwargs)[1]['faits']

    def test_demande_lexique_et_catalogue_sur_deux_surfaces(self):
        for nom in ('murs', 'plafond'):
            m = nouveau_monde()
            avant = copy.deepcopy(m.data)
            id = 'antichambre_' + nom
            absents = self.capter(m, 'Bonjour.')
            self.assertNotIn('objet:' + id, absents)
            self.assertNotIn(id, absents['faits_narratifs_proposables']['supports'])
            presents = self.capter(m, 'Je regarde le ' + nom.rstrip('s'))
            self.assertIn('objet:' + id, presents)
            self.assertIn(id, presents['faits_narratifs_proposables']['supports'])
            self.assertEqual(m.data, avant)

    def test_detail_et_mecanique_conservent_la_surface_sans_demande(self):
        for id in ('antichambre_sol', 'antichambre_murs'):
            m = nouveau_monde()
            m, _, etablis = preparer_faits(m, {'ajouts': [{'type': 'detail', 'ancrage': id,
                'nom': 'trace claire', 'genre': 'f', 'texte': 'Une trace claire marque la pierre.'}]})
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / 'copie.json'
                m.sauver(p)
                r = Monde.charger(p)
                self.assertEqual(m.data, r.data)
                self.assertEqual(regarder(m), regarder(r))
                for texte in ('Bonjour.', 'Je regarde la trace claire.'):
                    self.assertIn('objet:' + id, self.capter(r, texte))
                action = {'action': 'examiner', 'cible': etablis[0]['objet'],
                          'outil': '', 'methode': 'simple', 'difficulte': 0, 'justification': ''}
                a = self.console(r, 'Je regarde la trace claire.', action)
                b = self.console(r, 'Je regarde la trace claire.', action, False)
                self.assertEqual(a[:3], b[:3])
                self.assertIn('trace claire', a[2])
        m = nouveau_monde()
        m.objets['antichambre_sol']['integrite'] -= 1
        self.assertIn('objet:antichambre_sol', self.capter(m, 'Bonjour.'))
        m.objets['antichambre_murs']['propriete_future'] = True
        self.assertIn('objet:antichambre_murs', self.capter(m, 'Bonjour.'))

    def console(self, m, texte, proposition, projection=True):
        requetes = []
        def appel(instructions, entree, intention, fonction, schema):
            if fonction == 'auditer_action':
                return {'conforme': True, 'motif': ''}
            requetes.append(copy.deepcopy(entree['faits']))
            return {'mode': 'action', 'texte': '', 'faits': [], 'proposition': proposition}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'copie.json'
            m.sauver(p)
            with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                  patch.object(MJOpenAI, '_appeler_brut', side_effect=appel),
                  patch('builtins.input', side_effect=['mj ' + texte, 'tenter', 'quitter']),
                  patch('sys.stdout', io.StringIO()) as sortie):
                if projection:
                    jeu.main(['--console', '--connexion', 'api', '--recit-moteur', '--save', str(p)])
                else:
                    with patch('donjon.projection_surfaces.projeter'):
                        jeu.main(['--console', '--connexion', 'api', '--recit-moteur', '--save', str(p)])
            r = Monde.charger(p)
            return r.data, regarder(r), sortie.getvalue(), requetes

    def test_console_examen_et_depot_identiques_au_temoin_apres_recharge(self):
        for nom in ('murs', 'plafond'):
            p = {'action': 'examiner', 'cible': 'antichambre_' + nom,
                 'outil': '', 'methode': 'simple', 'difficulte': 0, 'justification': ''}
            a = self.console(nouveau_monde(), 'Je regarde les ' + nom, p)
            b = self.console(nouveau_monde(), 'Je regarde les ' + nom, p, False)
            self.assertEqual(a[:3], b[:3])
            self.assertIn('objet:antichambre_' + nom, a[3][0])
        p = sequence(etape('deplacer', 'torche', 'joueur'), etape('deplacer', 'torche', 'sol'))
        for demande in ('Je pose la torche à mes pieds.', 'je pose ma torche au sol'):
            a = self.console(nouveau_monde(), demande, p)
            b = self.console(nouveau_monde(), demande, p, False)
            self.assertEqual(a[:3], b[:3])
            if demande == 'Je pose la torche à mes pieds.':
                self.assertNotIn('objet:antichambre_sol', a[3][0])
            else:
                # Limite assumée : le lexique conserve une mention locative.
                self.assertIn('objet:antichambre_sol', a[3][0])
            self.assertEqual(a[0]['objets']['torche']['lieu'], a[0]['joueur']['salle'])

    def test_objets_a_completer_et_proposition_en_attente_conserves(self):
        m = nouveau_monde()
        f = self.capter(m, 'Je détaille la lanterne.')
        self.assertIn('lanterne', f['faits_narratifs_proposables']['qualifiables'])
        m, _, etablis = preparer_faits(m, {'ajouts': [{'type': 'detail', 'ancrage': 'lanterne',
            'nom': 'trace terne', 'genre': 'f', 'texte': 'Une trace terne marque le métal.'}]})
        a = self.console(m, 'Je regarde la trace terne.', {
            'action': 'examiner', 'cible': etablis[0]['objet'], 'outil': '',
            'methode': 'simple', 'difficulte': 0, 'justification': ''})
        self.assertIn('trace terne', a[2])
        # Une référence structurée suffit même sans reprise de son nom.
        from donjon.projection_surfaces import projeter
        f = {'objet:antichambre_murs': {}, 'perception': {}}
        self.assertFalse(projeter(m, f, [{'id': 'antichambre_murs'}], 'Continuer.',
                                 {'cible': 'antichambre_murs'}))

    def test_projection_bornee_et_contrat_ambiance_sur_deux_scenes(self):
        from donjon.atelier import nouveau_atelier
        for creer in (nouveau_monde, nouveau_atelier):
            m = creer()
            capter = prefixe.PrefixeKVTests()._capter_appel
            apres = capter(m, 'Bonjour.')
            with patch('donjon.projection_surfaces.projeter'):
                avant = capter(m, 'Bonjour.')
            self.assertEqual(apres[0], avant[0])
            self.assertEqual(apres[3], avant[3])
            f, g = avant[1]['faits'], apres[1]['faits']
            for cle in ('descriptions_a_completer', 'connaissances_a_completer',
                        'profil_joueur_a_completer'):
                self.assertEqual(f[cle], g[cle])
            retires = {k[6:] for k in f if k.startswith('objet:') and k not in g}
            self.assertTrue(retires)
            self.assertTrue(all(m.objets[id]['type'] == 'surface' for id in retires))
            self.assertEqual(f['perception'], g['perception'])
            from donjon.projection_surfaces import projeter
            faits = {'ambiance_ciblee': [{'texte': 'Un reflet pâle.', 'entites': ['reflet']}],
                     'objet:' + next(iter(retires)): {}}
            self.assertFalse(projeter(m, faits, [{'id': id} for id in retires], 'Je touche le reflet.'))
