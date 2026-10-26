import copy
import gzip
import json
import unittest
from pathlib import Path
from donjon.monde import Monde, nouveau_monde
from donjon.narration import attestations, consigner, segments_etablis
from donjon.perception import non_vus_connus
from donjon.spatial import installer
from donjon.noms import reference
from donjon.monde import ErreurMonde
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import recharger


class NonPerceptionTests(unittest.TestCase):
    def scenes(self):
        m = Monde(json.loads(gzip.decompress(Path('tests/data/scenes/guet_relais7.json.gz').read_bytes())))
        m.data['noms_connus'] = ['brune', 'marchand', 'ilse', 'aubin']
        autre = nouveau_monde()
        autre.data.pop("mode_cases", None)
        # Objet connu, autre salle, sans divulgation de sa position actuelle.
        cible = next(id for id,o in autre.objets.items() if o['lieu'] in autre.data['salles'] and o['lieu'] != autre.joueur['salle'] and o['type'] != 'personnage')
        autre.data['connus'].append(cible)
        return [(m, 'marchand'), (autre, cible)]

    def test_console_preuve_exacte_et_paraphrase_apres_recharge(self):
        for m, id in self.scenes():
            for exacte in (True, False):
                with self.subTest(id=id, exacte=exacte):
                    m = recharger(m)
                    avant = copy.deepcopy(m.data)
                    nom_public = next(e["nom"] for e in non_vus_connus(m) if e["id"] == reference(m,id))
                    phrase = (f'Tu ne vois pas {nom_public} en ce moment.' if exacte
                              else f'{nom_public} reste hors de ta vue actuelle.')
                    audits = [] if exacte else [rapport(ligne('mecanique', ['perception']))]
                    r, texte, appels = jouer(m, 'mj que vois-je ?', [dialogue(phrase)], audits)
                    faits = appels[0][1]['faits']
                    preuve = faits['perception']['non_vus_connus']
                    self.assertIn({'id': reference(m,id), 'nom': nom_public}, preuve)
                    self.assertTrue(all(set(e) == {'id','nom'} for e in preuve))
                    if id == 'marchand':
                        self.assertEqual(faits['perception']['couverture_vue']['portee'], 'partielle')
                    self.assertEqual(sum(f == 'auditer_narration' for f,_ in appels), int(not exacte))
                    self.assertIn(phrase, texte)
                    self.assertEqual(r.data['conversation'][-1]['reponse'], phrase)
                    self.assertEqual(r.data['narrations_mj'][-1]['texte'], phrase)
                    for champ in ('objets','joueur','journal','minutes','jets'):
                        self.assertEqual(r.data[champ], avant[champ])

    def test_une_entite_inconnue_n_est_pas_revelee_et_visible_retire_la_preuve(self):
        m = nouveau_monde()
        installer(m)
        for o in m.objets.values():
            if 'allume' in o: o['allume'] = False
        m.data['salles'][m.joueur['salle']]['lumiere_naturelle'] = 0
        connus = set().union(*(set(m.data.get(c,())) for c in ('connus','souvenirs_visuels','personnages_vus','noms_connus')))
        inconnu = next(id for id in m.objets if id not in connus)
        self.assertNotIn(reference(m,inconnu), [e['id'] for e in non_vus_connus(m)])
        id = next(id for id,o in m.objets.items() if o['lieu'] == m.joueur['salle'])
        m.data['connus'].append(id)
        self.assertIn(reference(m,id), [e['id'] for e in non_vus_connus(m)])
        m.data['salles'][m.joueur['salle']]['lumiere_naturelle'] = 2
        m.data.pop('mode_cases',None)
        self.assertTrue(m.visible(id))
        self.assertNotIn(reference(m,id), [e['id'] for e in non_vus_connus(m)])

    def test_attestation_refusee_a_la_sauvegarde_si_la_vue_change(self):
        m = nouveau_monde()
        m.data.pop('mode_cases', None)
        id = next(id for id,o in m.objets.items() if o['lieu'] == m.joueur['salle'])
        m.data['connus'].append(id)
        for o in m.objets.values():
            if 'allume' in o: o['allume'] = False
        m.data['salles'][m.joueur['salle']]['lumiere_naturelle'] = 0
        entite = next(e for e in non_vus_connus(m) if e['id'] == reference(m,id))
        phrase = f"Tu ne vois pas {entite['nom']} en ce moment."
        faits = {'attestations': attestations(m, m.contexte())}
        etablis = segments_etablis(phrase, faits)
        reponse = {'texte': phrase, '_audit': {'texte_initial': phrase,
                   'segments': etablis, 'faits': faits}}
        m.data['salles'][m.joueur['salle']]['lumiere_naturelle'] = 2
        self.assertTrue(m.visible(id))
        with self.assertRaisesRegex(ErreurMonde, 'ne correspond plus'):
            consigner(m, reponse)

if __name__ == '__main__': unittest.main()

