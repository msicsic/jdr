"""Compilation via console réelle : copies, mots/effets et rendu après recharge."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.agendas import contrats
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import proposition
from donjon.operations import sequence, etape
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_gardes_justes import crypte
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger
from tests import test_cache_kv_local as cache


class CompilateurPublicTests(unittest.TestCase):
    def test_contextes_publics_reels_schema_invariant_et_taille_mesuree(self):
        capter = cache.PrefixeKVTests()._capter_appel
        schemas = []
        for m in (nouveau_monde(), crypte()):
            avant = copy.deepcopy(m.data)
            _, entree, _, schema = capter(m, 'Je prends la clé.')
            schemas.append(schema)
            self.assertTrue(entree['compilation'])
            faits = entree['faits']
            self.assertNotIn('anneau', {k[6:] for k in faits if k.startswith('objet:')})
            self.assertNotIn('esprits_interlocuteurs', faits)
            self.assertIn('attestations', faits)
            self.assertIn('evenements_recents', faits)
            self.assertTrue(all('portrait' not in o for k, o in faits.items() if k.startswith('objet:')))
            self.assertEqual(m.data, avant)
            self.assertEqual(regarder(m), regarder(recharger(m)))
        self.assertEqual(*schemas)

    def test_nom_non_appris_et_objet_cache_absents_meme_dans_la_salle(self):
        from tests.test_noms import relais
        m = relais()
        m.objets['secret_g1'] = dict(m.objets['couteau'], id='secret_g1',
            nom='sentinelle_secrete_g1', lieu='coffre')
        _, entree, _, _ = cache.PrefixeKVTests()._capter_appel(m, "Je salue l'homme.")
        texte = json.dumps(entree, ensure_ascii=False)
        self.assertNotIn('sentinelle_secrete_g1', texte)
        self.assertNotIn('secret_g1', texte)
        self.assertNotIn('Gorm', texte)
        self.assertNotIn('"marchand"', texte)

    def test_gestes_et_sequences_admis_executés_sauves_avant_affichage(self):
        for cible, saisie in (('cle', 'Je ramasse la clé.'), ('cire', 'Je récupère la cire.')):
            for compose in (False, True):
                with self.subTest(cible=cible, compose=compose):
                    m = nouveau_monde()
                    m.objets[cible]['lieu'] = 'antichambre'
                    p = sequence(etape('deplacer', cible, 'joueur')) if compose else proposition('prendre', cible)
                    appels = []
                    def brut(_self, instructions, entree, intention, fonction, schema):
                        appels.append((fonction, copy.deepcopy(entree)))
                        if fonction == 'auditer_action':
                            return {'conforme': True, 'motif': ''}
                        self.assertTrue(entree['compilation'])
                        return {'mode': 'action', 'texte': '', 'faits': [], 'proposition': p}
                    with tempfile.TemporaryDirectory() as tmp:
                        chemin = Path(tmp) / 'partie.json'
                        m.sauver(chemin)
                        with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                              patch('donjon.mj.MJ._appeler_brut', brut),
                              patch('builtins.input', side_effect=['mj ' + saisie, 'tenter', 'quitter']),
                              patch('sys.stdout', io.StringIO()) as sortie):
                            self.assertEqual(jeu.main(['--console', '--save', str(chemin)]), 0)
                        r = Monde.charger(chemin)
                    self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 1)
                    self.assertEqual(r.objets[cible]['lieu'], 'joueur')
                    self.assertEqual(r.data['journal'][-1]['action'], p)
                    texte = r.data['conversation'][-1]['reponse']
                    self.assertEqual(r.data['conversation'][-1]['nature'], 'resultat_moteur')
                    self.assertIn(texte, sortie.getvalue())
                    rr = recharger(r)
                    self.assertEqual(rr.data, r.data)
                    self.assertEqual(regarder(rr), regarder(r))
                    self.assertEqual(fiche(rr), fiche(r))
                    self.assertEqual(scene_percue(rr), scene_percue(r))

    def test_negociation_mission_conserve_montant_et_accord_sur_copie(self):
        from donjon.dialogues import preparer_conversation
        for montant in (24, 26):
            with self.subTest(montant=montant):
                m = crypte()
                mission = next(iter(m.data['missions']))
                donneur = m.data['missions'][mission]['donneur']
                p = {'personnage': donneur, 'sujet': 'la prime', 'operation': 'negocier',
                     'mission': mission, 'montant_demande': montant}
                avant = copy.deepcopy(contrats(m))
                attendu, _ = preparer_conversation(m, p)
                r, sortie, appels = jouer(m, f'mj Gorm, je demande {montant} pièces pour l’anneau.',
                    [{'mode': 'conversation_pnj', 'texte': '', 'faits': [], 'proposition': p},
                     dialogue('Tu as présenté ta demande.')],
                    [rapport(ligne('mecanique', sources=['conversation_validee']))])
                self.assertEqual(contrats(m), avant)
                self.assertTrue(appels[0][1]['compilation'])
                self.assertEqual(appels[0][1]['faits']['missions_discutables'].keys(), {mission})
                self.assertIn('Tu as présenté ta demande.', r.data['conversation'][-1]['reponse'])
                self.assertIn('Tu as présenté ta demande.', sortie)
                self.assertNotEqual(contrats(r), avant)
                self.assertEqual(contrats(r), contrats(attendu))
                self.assertEqual(r.data, recharger(r).data)
                self.assertEqual(regarder(r), regarder(recharger(r)))


if __name__ == '__main__':
    unittest.main()
