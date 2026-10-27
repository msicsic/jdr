"""Lot 83 : rapports cohérents et références publiques, console puis recharge."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon.biens import compte
from donjon.narration import AuditIllisible, consigner, controler
from donjon.monde import Monde
from donjon.rendu import decrire_comptes, regarder
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_gardes_justes import crypte
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


def jugement(verdict, portee, sources=('perception',)):
    return rapport({**ligne(verdict, sources=sources), 'portee_mecanique': portee})


def noir():
    return Monde.charger(Path(__file__).parent / 'data/scenes/signes_ecart_relais_noir.json')


class VerdictCoherentTests(unittest.TestCase):
    def test_schema_coherent_refus_direct_console_et_recharge(self):
        # Première campagne archivée : signes-guet, « Tu es seul… » ;
        # autre assertion mécanique de même nature : orientation de Gorm.
        from donjon.narration import schema_audit
        for m, faux, saisie, portee in (
                (Monde(json.loads(gzip.decompress((Path(__file__).parent /
                    'data/scenes/guet_relais7.json.gz').read_bytes()))),
                 'Tu es seul dans la Galerie de ronde, plongée dans la pénombre.',
                 'mj Que vois-je ?', 'sans_fondement'),
                (crypte(), 'Gorm est face à toi.', 'Gorm me fait-il face ?', 'contradictoire')):
            with self.subTest(texte=faux):
                avant = copy.deepcopy(m.data)
                variantes = schema_audit({'perception': {}}, [0])['properties']['segments']['properties']['0']['anyOf']
                self.assertTrue(all('verdict' not in v['properties'] for v in variantes))
                self.assertTrue(any(v['properties']['nature']['enum'] == ['mecanique']
                    and portee in v['properties']['portee_mecanique']['enum'] for v in variantes))
                bon = 'Tu peux regarder autour de toi.'
                r, sortie, appels = jouer(recharger(m), saisie,
                    [dialogue(faux), dialogue(bon)],
                    [rapport({'nature': 'mecanique', 'portee_mecanique': portee,
                              'sources': ['perception'], 'motif': 'Affirmation non établie.', 'comptes': []}),
                     rapport({'nature': 'neutre', 'portee_mecanique': 'aucune', 'sources': [], 'comptes': []})])
                self.assertNotIn(faux, sortie)
                self.assertNotIn(faux, str(recharger(r).data.get('narrations_mj')))
                self.assertIn(bon, sortie)
                self.assertIn(bon, str(recharger(r).data.get('narrations_mj')))
                self.assertEqual([f for f, _ in appels], ['repondre_au_joueur', 'auditer_narration',
                    'repondre_au_joueur', 'auditer_narration'])
                self.assertEqual(r.objets, avant['objets'])
                self.assertEqual(r.joueur['position'], m.joueur['position'])
                self.assertEqual(regarder(recharger(r)), regarder(m))

    def test_absence_et_orientation_rapport_redemande_puis_texte_corrige(self):
        scenes = ((noir(), "Elle n'est pas là pour que tu le lui demandes.",
                   'Ilse a-t-elle peur de Brune ?', 'sans_fondement'),
                  (crypte(), 'Gorm est face à toi.', 'Gorm me fait-il face ?', 'contradictoire'))
        for m, faux, saisie, portee in scenes:
            with self.subTest(portee=portee):
                avant = copy.deepcopy(m.objets)
                bon = 'Tu peux regarder autour de toi.'
                r, sortie, appels = jouer(recharger(m), saisie,
                    [dialogue(faux), dialogue(bon)],
                    [jugement('mecanique', portee),
                     jugement('contradictoire' if portee == 'contradictoire' else 'invention_protegee', portee),
                     jugement('neutre', 'aucune', ())])
                self.assertNotIn(faux, sortie)
                self.assertNotIn(faux, str(r.data.get('narrations_mj')))
                self.assertNotIn(faux, str(r.data.get('conversation')))
                self.assertIn(bon, sortie)
                self.assertIn(bon, str(recharger(r).data['narrations_mj']))
                self.assertEqual(r.objets, avant)
                self.assertEqual(r.joueur['position'], m.joueur['position'])
                fonctions = [f for f, _ in appels]
                self.assertEqual(fonctions, ['repondre_au_joueur', 'auditer_narration',
                                            'auditer_narration', 'repondre_au_joueur', 'auditer_narration'])
                # La redemande porte sur le même texte, sans accuser celui du MJ.
                self.assertEqual(appels[1][1], appels[2][1])
                self.assertEqual(regarder(recharger(r)), regarder(m))

    def test_rapport_coherent_sans_recriture_et_motif_libre_non_interprete(self):
        for m in (noir(), crypte()):
            with self.subTest(salle=m.joueur['salle']):
                texte = 'Tu portes une lanterne.'
                a = jugement('mecanique', 'etablie', ('joueur',))
                r, sortie, appels = jouer(recharger(m), 'que porte-je ?', [dialogue(texte)], [a])
                self.assertIn(texte, sortie)
                self.assertIn(texte, str(recharger(r).data['narrations_mj']))
                self.assertEqual(r.objets, m.objets)
                self.assertEqual(len(appels), 2)
        # Limite explicite : un motif libre n'est pas une preuve typée.
        a['segments']['0']['motif'] = "L'assertion est contredite, mais les champs disent établie."
        self.assertFalse(controler(texte, a, {'joueur': {}})['obstacles'])

    def test_verdict_negatif_et_portee_etablie_illisibles_avant_enregistrement(self):
        m = crypte()
        texte = 'Gorm est face à toi.'
        for verdict, portee in (('contradictoire', 'etablie'), ('invention_protegee', 'etablie'),
                                ('mecanique', 'contradictoire'), ('mecanique', 'sans_fondement')):
            with self.subTest(verdict=verdict, portee=portee):
                a = jugement(verdict, portee)
                with self.assertRaises(AuditIllisible):
                    controler(texte, a, {'perception': {}})
                avant = copy.deepcopy(m.data)
                with self.assertRaises(AuditIllisible):
                    consigner(m, {**dialogue(texte), '_audit': {
                        'texte_initial': texte, 'segments': a['segments'], 'faits': {'perception': {}},
                        'fondement': texte}})
                self.assertEqual(m.data, avant)

    def test_deux_audits_illisibles_par_texte_ne_l_autorisent_jamais(self):
        for m, faux in ((noir(), "Elle n'est pas là pour que tu le lui demandes."),
                        (crypte(), 'Gorm est face à toi.')):
            with self.subTest(texte=faux):
                r, sortie, appels = jouer(recharger(m), 'que vois-je ?',
                    [dialogue(faux)] * 3, [jugement('mecanique', 'contradictoire')] * 6)
                self.assertNotIn(faux, sortie)
                self.assertNotIn(faux, str(recharger(r).data.get('narrations_mj')))
                self.assertNotIn(faux, str(r.data.get('conversation')))
                self.assertEqual(r.objets, m.objets)
                self.assertEqual(sum(f == 'auditer_narration' for f, _ in appels), 6)
                self.assertEqual(regarder(r), regarder(m))

    def test_gorm_corvus_et_autre_remboursement_acceptes_sans_relance(self):
        for script, qui, nom in (('comptes', 'marchand', 'Gorm'), ('soir-appel', 'aubin', 'Aubin')):
            with self.subTest(script=script):
                m = banc(script, noms_connus=['marchand', 'aubin', 'brune', 'ilse'])
                avant = m.joueur['or']
                mots = f'{nom}, rends-moi les deux pièces que tu me dois.'
                texte = 'Ta demande est entendue.'
                a = jugement('mecanique', 'etablie', ('comptes',))
                a['segments']['0']['comptes'] = [compte(nom.lower(), 'Corvus', montant=2, etat='rendu')]
                r, sortie, appels = jouer(recharger(m), mots,
                    [parole(mots, ('reclamer', '', '', ''), personnage=qui), dialogue(texte)], [a])
                self.assertIn(texte, sortie)
                self.assertIn(texte, str(recharger(r).data['narrations_mj']))
                self.assertEqual(r.joueur['or'], avant + 2)
                self.assertFalse(any(d['de'] == qui for d in r.data['dettes']))
                self.assertNotIn(f'{nom} te doit 2 pièces', decrire_comptes(recharger(r)))
                self.assertFalse(any('controle_narratif' in e for _, e in appels))
                if script == 'comptes':
                    self.assertIn('Brune te doit 2 pièces', decrire_comptes(r))

    def test_references_objets_offres_et_ambiguite_sans_nom_prive(self):
        from donjon.noms import references_fournies
        faits = {'joueur': {'nom': 'Corvus'}, 'interlocuteurs': {'marchand': {'nom': 'Gorm, marchand'}},
                 'objet:planches': {'nom': 'planches', 'aliases': ['madrier']}}
        c = {'debiteur': 'Gorm', 'creancier': 'Corvus', 'etat': 'offre',
             'condition': {'type': 'part', 'objet': 'madrier'},
             'contrepartie': {'type': 'pieces', 'montant': 2}}
        r = references_fournies(c, faits)
        self.assertEqual((r['debiteur'], r['creancier'], r['condition']['objet']),
                         ('marchand', 'joueur', 'planches'))
        self.assertEqual(c['debiteur'], 'Gorm')
        self.assertEqual(references_fournies({'debiteur': 'Nom privé'}, faits)['debiteur'], 'Nom privé')
        faits['interlocuteurs']['personne_4'] = {'nom': 'une personne inconnue'}
        self.assertEqual(references_fournies({'debiteur': 'une'}, faits)['debiteur'], 'une')
        faits['joueur']['nom'] = 'Alix'
        self.assertEqual(references_fournies({'creancier': 'Alix'}, faits)['creancier'], 'joueur')
        self.assertEqual(references_fournies({'creancier': 'Corvus'}, faits)['creancier'], 'Corvus')
        faits['souvenirs_visuels'] = [{'id': 'broche_1', 'nom': 'broche argentée', 'hors_de_vue': True}]
        self.assertEqual(references_fournies({'objet': 'broche argentée'}, faits)['objet'], 'broche_1')
        faits['personnages_connus'] = {'marchand': 'Gorm, marchand'}
        faits['souvenirs_visuels'].append({'id': 'marchand', 'nom': 'homme grisonnant'})
        faits['interlocuteurs']['marchand'] = {'nom': 'homme grisonnant'}
        self.assertEqual(references_fournies({'debiteur': 'Gorm'}, faits)['debiteur'], 'marchand')
        faits['objet:autre'] = {'nom': 'autre', 'aliases': ['madrier']}
        with self.assertRaises(ValueError):
            references_fournies(c, faits)

    def test_comptes_de_personnes_connues_hors_de_vue_apres_recharge(self):
        from tests.test_tensions import placer
        for script, qui, nom, lieu in (('comptes', 'marchand', 'Gorm', 'antichambre'),
                                       ('soir-appel', 'aubin', 'Aubin', 'echoppe')):
            with self.subTest(qui=qui):
                m = banc(script, noms_connus=['marchand', 'aubin', 'brune', 'ilse'])
                placer(m, qui, lieu, (1, 1))
                m = recharger(m)
                self.assertNotIn(qui, m.contexte()['interlocuteurs'])
                texte = 'Tu peux consulter tes comptes.'
                a = jugement('mecanique', 'etablie', ('comptes',))
                a['segments']['0']['comptes'] = [compte(nom, 'Corvus', montant=2)]
                r, sortie, appels = jouer(m, 'qui me doit des pièces ?', [dialogue(texte)], [a])
                self.assertIn(texte, sortie)
                self.assertIn(texte, str(recharger(r).data['narrations_mj']))
                self.assertEqual(r.joueur['or'], m.joueur['or'])
                self.assertEqual(r.data['dettes'], m.data['dettes'])
                self.assertIn(f'{nom} te doit 2 pièces', decrire_comptes(r))
                self.assertFalse(any('controle_narratif' in e for _, e in appels))
