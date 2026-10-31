"""Lot 432 : du refus du rendu à la correction, sans fuite ni écriture partielle."""
import ast
import copy
import gzip
import inspect
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import narration, rendu
from donjon.enrichissement import preparer_complements
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.moteur import proposition
from donjon.noms import reference, references
from donjon.voix import reel
from tests import test_attendu_designable
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger


def capture():
    # Capture 423, branche, avant T4 ; proposition R58 conservée à l'identique.
    return json.loads(gzip.decompress(
        (Path(__file__).parent / 'data/refus-rendu-432.json.gz').read_bytes()))


class RefusRenduTests(unittest.TestCase):
    def assertPublic(self, m, attendu, recus=()):
        test_attendu_designable.AttenduDesignableTests.assertReferences(self, m, attendu, recus)

    def test_r58_et_autre_partie_correction_console_et_recharge(self):
        f = capture()
        for facette in ('mains', 'yeux'):
            with self.subTest(facette=facette):
                m = Monde(copy.deepcopy(f['monde']))
                reponse = copy.deepcopy(f['reponse'])
                ajout = reponse['proposition']['ajouts'][0]
                ajout['facette'] = facette
                if facette == 'yeux':
                    ajout['description'] = 'Ses yeux sont gris clair.'
                avant, vue = copy.deepcopy(m.data), rendu.regarder(m)
                travail = preparer_complements(m, references(m, reponse['proposition']))
                id = 'detail_aubin_' + facette
                ref = reference(travail, id)
                # Cause réelle : corps et détail visibles, référence neuve indécodable.
                self.assertTrue(travail.visible('aubin'))
                self.assertTrue(travail.visible(id))
                self.assertIsNone(reel(travail, ref))
                with (patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}),
                      patch.object(MJOpenAI, '_appeler_brut', return_value=copy.deepcopy(reponse))):
                    with self.assertRaises(ErreurMonde) as leve:
                        MJOpenAI(connexion='api')._echanger_prepare(m, f['saisie'])
                exc = leve.exception
                self.assertEqual(str(exc), "Cet objet n'est pas visible.")
                self.assertIn('decrire.cible', exc.attendu)
                self.assertIn(repr(ref), exc.attendu)
                acceptes = exc.attendu.split('acceptés : ', 1)[1]
                self.assertNotIn(ref, acceptes)
                self.assertIn('planches', acceptes)
                self.assertPublic(travail, exc.attendu)
                self.assertEqual(m.data, avant)
                self.assertEqual(recharger(m).data, avant)
                self.assertEqual(rendu.regarder(recharger(m)), vue)

                # Correction vers une cible proposée par le refus : examen moteur.
                # La capture n'a pas encore la qualification permettant de prélever.
                p = proposition('examiner', 'planches')
                corrigee = {'mode': 'action', 'texte': '', 'faits': [], 'proposition': p}
                reprise, sortie, appels = jouer(m, 'mj ' + f['saisie'],
                    [reponse, corrigee], [], suite=('mj examine les planches',))
                self.assertIn(str(exc), sortie)
                self.assertNotIn(exc.attendu, sortie)
                self.assertNotIn(ajout['description'], sortie)
                self.assertNotIn(id, reprise.objets)
                self.assertEqual(reprise.objets, m.objets)
                self.assertIn('planches', reprise.data['connus'])
                self.assertIn(rendu.decrire(reprise, 'planches', detail=True), sortie)
                self.assertEqual(rendu.regarder(reprise), rendu.regarder(recharger(reprise)))
                self.assertEqual(rendu.fiche(reprise), rendu.fiche(recharger(reprise)))
                self.assertEqual([fn for fn, _ in appels].count('repondre_au_joueur'), 2)

    def test_parcours_des_refus_du_rendu_sans_fuite(self):
        for m in (nouveau_monde(), Monde(capture()['monde'])):
            avant = copy.deepcopy(m.data)
            comptes = {f.__name__: 0 for f in (rendu.decrire, rendu.toucher, rendu.position)}
            for fonction in (rendu.decrire, rendu.toucher, rendu.position):
                for id in [*m.objets, 'introuvable', None]:
                    with self.subTest(fonction=fonction.__name__, id=id):
                        try:
                            fonction(m, id)
                        except ErreurMonde as exc:
                            comptes[fonction.__name__] += 1
                            self.assertIn('reçu', exc.attendu)
                            self.assertIn('acceptés', exc.attendu)
                            self.assertPublic(m, exc.attendu, recus=('introuvable',))
            self.assertTrue(all(comptes.values()), comptes)
            self.assertEqual(m.data, avant)
            self.assertEqual(rendu.regarder(m), rendu.regarder(recharger(m)))

    def test_attestations_refusent_un_contexte_visible_perime(self):
        m = nouveau_monde()
        contexte = m.contexte()
        cible = next(o for o in contexte['objets_perceptibles'] if o['id'] == 'cle')
        self.assertTrue(cible['visible'])
        m.objets['cle']['lieu'] = 'crypte'
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as leve:
            narration.attestations(m, contexte)
        self.assertIn('decrire.cible', leve.exception.attendu)
        self.assertPublic(m, leve.exception.attendu)
        self.assertEqual(m.data, avant)
        self.assertEqual(rendu.regarder(m), rendu.regarder(recharger(m)))

    def test_refus_de_publication_et_correction_sauvegardee(self):
        m = nouveau_monde()
        for texte in ('Corvus attend.', 'Le joueur attend.'):
            avant = copy.deepcopy(m.data)
            r = {'texte': texte, '_audit': {'texte_initial': texte,
                 'segments': rapport(ligne('neutre'))['segments'], 'faits': {}, 'fondement': ''}}
            with self.assertRaises(ErreurMonde) as leve:
                narration.consigner(m, r)
            self.assertTrue(leve.exception.attendu)
            self.assertIn(texte.split()[0], leve.exception.attendu)
            self.assertEqual(m.data, avant)
        with self.assertRaises(ErreurMonde) as leve:
            narration.consigner(m, {'texte': 'Tu attends.'})
        self.assertIn('reponse._audit', leve.exception.attendu)
        reprise, sortie, _ = jouer(m, 'mj que perçois-je ?', [dialogue('Tu attends.')],
                                   [rapport(ligne('neutre'))])
        self.assertIn('Tu attends.', sortie)
        self.assertEqual(reprise.data['narrations_mj'][-1]['texte'], 'Tu attends.')
        self.assertEqual(rendu.regarder(reprise), rendu.regarder(recharger(reprise)))

    def test_audits_illisibles_portent_aussi_le_champ_recu_et_attendu(self):
        for r in ({}, {'segments': {}}, rapport({'nature': 'invalide'}),
                  rapport(ligne('neutre') | {'rappels': False}),
                  rapport(ligne('neutre') | {'eclairages': False}),
                  rapport(ligne('mecanique') | {'portee_mecanique': 'contradictoire'}),
                  rapport(ligne('contradictoire') | {'portee_mecanique': 'contradictoire'})):
            with self.subTest(rapport=r), self.assertRaises(narration.AuditIllisible) as leve:
                narration.controler('Tu attends.', r, {})
            self.assertIn('reçu', leve.exception.attendu)
            self.assertIn('accept', leve.exception.attendu)
        for elements in ([{}], ['bruit'] * 9):
            with self.assertRaises(narration.AuditIllisible) as leve:
                narration.valider_elements_ambiance(elements, '', {})
            self.assertIn('reçu', leve.exception.attendu)
            self.assertIn('accept', leve.exception.attendu)
        with self.assertRaises(narration.AuditIllisible) as leve:
            narration.controler('Tu attends.', rapport(ligne('contradictoire', sources=['inventee'])
                | {'portee_mecanique': 'contradictoire'}), {})
        self.assertIn("reçu ['inventee']", leve.exception.attendu)

    def test_aucune_levee_sans_attendu_dans_rendu_et_narration(self):
        # Garde exhaustive des sites, complétée par les parcours exécutés ci-dessus.
        for module in (rendu, narration):
            for noeud in ast.walk(ast.parse(inspect.getsource(module))):
                if (isinstance(noeud, ast.Raise) and isinstance(noeud.exc, ast.Call)
                        and isinstance(noeud.exc.func, ast.Name)
                        and noeud.exc.func.id in ('ErreurMonde', 'AuditIllisible')):
                    with self.subTest(module=module.__name__, ligne=noeud.lineno):
                        self.assertGreaterEqual(len(noeud.exc.args), 2)
                        self.assertNotEqual(ast.literal_eval(noeud.exc.args[1])
                            if isinstance(noeud.exc.args[1], ast.Constant) else None, '')


if __name__ == '__main__':
    unittest.main()
