"""S1j : identités vocales/nominales, copies et continuité de sauvegarde."""
import copy
import gzip
import json
import unittest

from donjon import memoire, pnj, voix
from donjon.emissions import lire as emissions
from donjon.esprits import lire, percevoir_tous
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_memoire_paroles import acces_dits
from tests import test_memoire_socle, test_voix
from tests.test_memoire_socle import RACINE
from tests.test_paroles import jouer, parole, reponse_pnj, relais as pres_de_gorm
from tests.test_tensions import placer, recharger
from tests.test_voix import gorm_et_une_voix

REGISTRES = {'voix', 'voix_connues', 'voix_entendues', 'echange', 'noms', 'noms_connus'}


class IdentiteVocaleTests(unittest.TestCase):
    def test_inventaire_ferme_homonymes_et_contre_epreuves(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf-8'))
        mesures = {}
        for p in [*RACINE.glob('*.py'), *(RACINE / 'donjon').rglob('*.py'), *(RACINE / 'tools').rglob('*.py')]:
            relatif = p.relative_to(RACINE).as_posix()
            if relatif == 'donjon/memoire.py':
                continue
            acces = acces_dits(p.read_text(encoding='utf-8-sig'), registres=REGISTRES)
            if acces:
                mesures[relatif] = {f'{f}/{e}': n for (f, e), n in sorted(acces.items())}
        # Déclaration de schéma seule ; le reste est un inventaire exact des
        # homonymes publics, acoustiques, données d'auteur et paroles proposées.
        self.assertEqual(mesures['donjon/esprits.py'].pop('<module>/' + test_memoire_socle.AccesTests.schema_champs()), 1)
        mesures = {f: a for f, a in mesures.items() if a}
        self.assertEqual(mesures, fixture['voix_homonymes_s1j'])
        for registre in REGISTRES:
            for source in (
                f'e["{registre}"]', f'e.get("{registre}")', f'e.setdefault("{registre}", {{}})',
                f'cle = "{registre}"; stock = e[cle]; alias = stock; alias[s]["minute"] = 8',
                f'stock = e["{registre}"]; prendre = stock.get; prendre(s)',
                f'for entree in e["{registre}"].values():\n entree.clear()',
                f'def fuite(e):\n stock = e["{registre}"]; return stock',
                f'del e["{registre}"]', f'e.pop("{registre}")',
                f'e.update({registre}={{}})', f'e.update(**{{"{registre}": stock}})',
                f'e.__setitem__("{registre}", {{}})',
                f'e = {{"{registre}": stock}}', f'e = dict({registre}=stock)',
            ):
                with self.subTest(source=source):
                    self.assertTrue(acces_dits(source, registres=REGISTRES))

    def test_vues_pures_copies_et_entrees_protegees(self):
        m = gorm_et_une_voix()
        for qui in ('joueur', 'marchand'):
            voix.retenir(m, qui, 'brune')['mefiance'] = True
            memoire.retenir_pretention_vocale(m, qui, 'brune', 'ilse')
            self.assertFalse(memoire.voix_entendues(m, qui)['brune']['mefiance'])
        proposition = dict(instant=0, auteur='brune', a=['ilse'], noms=['ilse'])
        voix.retenir_echange(m, 'marchand', proposition)
        avant = copy.deepcopy(m.data)
        proposition['a'].clear()
        proposition['noms'].clear()
        for qui in ('absent', 'joueur', 'marchand'):
            memoire.voix_connues(m, qui).append('invente')
            memoire.noms_retenus(m, qui).clear()
            entrees = voix.entendues(m, qui)
            for entree in entrees.values():
                entree['se_dit'] = 'invente'
            entrees.clear()
            for retenue in memoire.echange_retenu(m, qui):
                retenue['a'].clear()
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)
        precedentes = voix.retenir_echange(m, 'marchand', dict(instant=1, auteur='ilse', a=[], noms=[]))
        avant = copy.deepcopy(m.data)
        precedentes[0]['a'].clear()
        self.assertEqual(m.data, avant)

    def test_eviction_dates_rangs_et_nom_conserve(self):
        m = gorm_et_une_voix()
        for qui in ('joueur', 'marchand'):
            for n in range(voix.VOIX_MAX):
                memoire.retenir_voix(m, qui, f'signature{n}', minute=10)
            memoire.retenir_voix(m, qui, 'signature0', minute=11)
            memoire.retenir_voix(m, qui, 'signature0', minute=3)
            memoire.retenir_voix(m, qui, 'nouvelle', minute=10)
            entrees = memoire.voix_entendues(m, qui)
            self.assertEqual(len(entrees), voix.VOIX_MAX)
            self.assertNotIn('signature1', entrees)
            self.assertEqual(entrees['signature0']['minute'], 11)
            self.assertEqual(entrees['nouvelle']['n'], 25)
            # Une entrée ancienne ajoutée à saturation peut s'évincer elle-même.
            memoire.retenir_voix(m, qui, 'trop_ancienne', minute=0)
            self.assertEqual(memoire.voix_entendues(m, qui), entrees)
            memoire.retenir_nom(m, qui, 'joueur' if qui != 'joueur' else 'ilse')
        avant = copy.deepcopy(m.data)
        self.assertEqual(recharger(m).data, avant)

    def test_migrations_et_corruptions_sans_reapprentissage(self):
        m = gorm_et_une_voix()
        # Vieille sauvegarde sans liste de voix : savoir initial uniquement.
        del lire(m, 'marchand')['voix']
        m = recharger(Monde(copy.deepcopy(m.data)))
        self.assertEqual(memoire.voix_connues(m, 'marchand'), ['aubin', 'brune', 'ilse'])
        self.assertEqual(recharger(m).data, m.data)
        for qui in ('joueur', 'marchand'):
            for champ, valeur in (
                ('voix', ['brune', 'brune']),
                ('voix_entendues', {'brune': dict(minute=0, se_dit=None, mefiance=1, n=1)}),
                ('voix_entendues', {'brune': dict(minute=0, se_dit=None, mefiance=False, n=0)}),
                ('voix_entendues', {'brune': dict(minute=0, se_dit=None, mefiance=False, n=1, fuite=True)}),
                ('noms', ['brune', 'brune']),
                ('echange', [dict(instant=0, auteur='brune', a='ilse', noms=[])]),
            ):
                if qui == 'joueur' and champ == 'echange':
                    continue
                corrompu = m.copier()
                if qui == 'joueur':
                    corrompu.data[{'voix': 'voix_connues', 'noms': 'noms_connus'}.get(champ, champ)] = valeur
                else:
                    lire(corrompu, qui)[champ] = valeur
                with self.subTest(qui=qui, champ=champ, valeur=valeur), self.assertRaises(AssertionError):
                    memoire.verifier_identite_vocale(corrompu, qui)
                    if qui == 'joueur':
                        memoire.verifier_noms_joueur(corrompu)

    def verifier_continuite(self, initial):
        resultats = []
        for tranches in ((1200,), (300,) * 4):
            m, lignes = recharger(initial), []
            for dt in tranches:
                pnj.avancer(m, ecouler(m, dt), lignes, dt)
                m = recharger(m)
            public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
            recharge = recharger(m)
            self.assertEqual(recharge.data, m.data)
            self.assertEqual((regarder(recharge), scene_percue(recharge), emissions(recharge)), public)
            resultats.append((copy.deepcopy(m.data), json.dumps(m.data), lignes, public))
        self.assertEqual(*resultats)

    def test_cas_reel_corvus_presente_et_voix_reconnue_ensuite(self):
        # Deux régressions historiques de voix-suite : Corvus vu se nommant,
        # puis Corvus nommé dans le noir et reconnu plus tard à la lumière.
        for noir in (False, True):
            m = test_voix.VoixInconnueTests().gorm_dans_le_noir() if noir else pres_de_gorm()
            m, _, _ = jouer(m, "je lui dis : c'est Corvus", [
                parole("C'est Corvus.", ('nom', 'joueur', '', '')), reponse_pnj('Gorm grogne.')])
            if noir:
                m.objets['brasero']['allume'] = True
                m, _, _ = jouer(recharger(m), 'je dis à Gorm : bonsoir', [
                    parole('Bonsoir.', personnage='marchand'), reponse_pnj('Gorm grogne.')])
            m = recharger(m)
            self.assertIn('joueur', memoire.noms_retenus(m, 'marchand'))
            self.assertIn('joueur', memoire.voix_connues(m, 'marchand'))
            self.assertNotIn('joueur', memoire.voix_entendues(m, 'marchand'))
            self.assertTrue(any(p['locuteur'] == 'joueur' for p in emissions(m)))
            self.verifier_continuite(m)

    def test_imposture_demasquee_apres_coup_et_projection_anonyme(self):
        m = gorm_et_une_voix()
        self.assertEqual(voix.se_nommer(m, 'marchand', 'brune', 'ilse'), 'crue')
        # Corvus entend aussi cette prétention ; le MJ ne reçoit pas la signature.
        voix.retenir(m, 'joueur', 'brune')
        memoire.retenir_pretention_vocale(m, 'joueur', 'brune', 'ilse')
        m = recharger(m)
        self.assertTrue(voix.designation(m, 'brune').startswith('voix_'))
        self.assertIn('Ilse', voix.nom_pour_joueur(m, 'brune'))
        self.assertEqual(voix.genre(m, 'brune'), 'féminin')
        from donjon.ouie import retentir
        placer(m, 'ilse', 'echoppe', (2, 1))
        m.objets['lanterne'].update(lieu='ilse', allume=True)
        percevoir_tous(m)
        retentir(m, 'ilse', 'dire', texte='Ilse dit bonsoir.')
        m = recharger(m)
        self.assertTrue(memoire.voix_entendues(m, 'marchand')['brune']['mefiance'])
        self.assertTrue(any(s['type'] == 'imposture' for s in memoire.episodes(m, 'marchand')))
        self.verifier_continuite(m)

    def test_capture_historique_mine_470_echanges_et_voix(self):
        capture = RACINE / 'tests/data/chercher-appeler-mine.json.gz'
        m = recharger(Monde(json.loads(gzip.decompress(capture.read_bytes()))))
        self.assertTrue(memoire.voix_connues(m, 'josse'))
        self.assertTrue(memoire.echange_retenu(m, 'josse'))
        self.verifier_continuite(m)


if __name__ == '__main__':
    unittest.main()
