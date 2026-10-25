"""Lot 74 : refus démontrables, vraie console, état et texte après recharge."""
import copy
import unittest

from donjon.biens import compte
from donjon.geometrie import placer
from donjon.monde import ErreurMonde
from donjon.narration import consigner, controler, orientations, schema_audit, voix_auteur
from donjon.spatial import installer, memoriser
from donjon.scenario_crypte import nouveau_monde
from tests.support import presentes
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_sous_obstacle import scene
from tests.test_tensions import recharger


def crypte():
    m = presentes(nouveau_monde())
    installer(m)
    m.joueur.update(salle='echoppe', position=[2, 1], orientation='sud-est')
    memoriser(m)
    m.joueur['orientation'] = 'ouest'
    return recharger(m)


def audit_lumiere(source):
    return rapport({**ligne('mecanique', sources=['perception']), 'eclairages': [source]})


def conduite():
    m = scene()
    m.joueur['orientation'] = 'sud-ouest'
    memoriser(m)
    m.joueur['orientation'] = 'est'
    return recharger(m)


class GardesJustesTests(unittest.TestCase):
    def accepte(self, m, saisie, texte, audit):
        avant = copy.deepcopy(m.objets)
        r, sortie, appels = jouer(recharger(m), saisie, [dialogue(texte)], [audit])
        self.assertIn(texte, sortie)
        self.assertIn(texte, str(r.data['conversation']))
        self.assertIn(texte, str(r.data['narrations_mj']))
        self.assertEqual(r.objets, avant)
        self.assertFalse(any('controle_narratif' in e for _, e in appels))
        # Même lecture après une seconde ouverture ; aucun objet réintroduit par la prose.
        rr, rendu, _ = jouer(r, saisie, [dialogue(texte)], [audit])
        self.assertIn(texte, rendu)
        self.assertEqual(rr.objets, avant)
        return r, appels

    def test_refus_de_brune_dit_dans_le_monde_et_compte_conserve(self):
        m = banc('comptes')
        texte = 'Elle maintient son refus des deux pièces qu’elle te doit.'
        audit = rapport({**ligne('mecanique', sources=['comptes']),
                         'comptes': [compte('brune', 'joueur', montant=2)]})
        mots = 'Brune, rends-moi les deux pièces que tu me dois.'
        r, sortie, appels = jouer(m, mots,
            [parole(mots, ('reclamer', '', '', ''), personnage='brune'), dialogue(texte)], [audit])
        self.assertIn(texte, sortie)
        self.assertIn(texte, str(r.data['narrations_mj']))
        self.assertEqual(r.joueur['or'], m.joueur['or'])
        self.assertEqual(r.data['dettes'], m.data['dettes'])
        self.assertFalse(any('controle_narratif' in e for _, e in appels))

    def test_autre_refus_ordinaire_et_vrai_meta_d_auteur(self):
        self.accepte(scene(), 'que puis-je faire ?', 'Son refus te laisse libre de partir.',
                     rapport(ligne('neutre')))
        self.assertFalse(voix_auteur('Le refus précédent de Brune tient toujours.'))
        self.assertFalse(voix_auteur('Son refus de proposition de mariage tient toujours.'))
        mauvais, bon = 'Le moteur refuse cette proposition.', 'Tu peux regarder autour de toi.'
        r, sortie, appels = jouer(recharger(scene()), 'que puis-je faire ?',
            [dialogue(mauvais), dialogue(bon)], [rapport(ligne('neutre')), rapport(ligne('neutre'))])
        self.assertNotIn(mauvais, sortie)
        self.assertNotIn(mauvais, str(r.data['narrations_mj']))
        self.assertIn(bon, sortie)
        self.assertTrue(any('controle_narratif' in e for _, e in appels))

    def test_crochets_et_autre_cible_avec_negation_distincte(self):
        for m, nom, cible in ((crypte(), 'La trousse de crochets', 'crochets'),
                              (scene(), 'La poutre effondrée', 'poutre_conduite')):
            with self.subTest(cible=cible):
                memoriser(m)
                m.joueur['orientation'] = 'ouest'
                texte = f'Tu ne peux pas agir d’ici sur {nom.lower()} : sa dernière position connue est derrière toi.'
                self.accepte(m, f'où est {nom.lower()} ?', texte,
                             rapport(ligne('mecanique', sources=['souvenirs_visuels'])))

    def test_deux_referents_et_deux_propositions_ne_deviennent_pas_une_preuve(self):
        m = crypte()
        texte = ('Tu ne peux pas simplement attendre que Gorm ait le dos tourné puis prendre la trousse '
                 'depuis ici : elle a été vue à trois mètres vers le sud et un mètre vers l’est, '
                 'derrière toi et à gauche, et il faut être juste à côté pour agir sur elle.')
        self.accepte(m, 'où est la trousse de crochets ?', texte,
                     rapport(ligne('mecanique', sources=['souvenirs_visuels'])))
        faits = m.contexte()
        self.assertEqual(orientations('Gorm est ici. Elle est devant toi.', faits), [])
        self.assertEqual(orientations('Gorm regarde quelque chose derrière toi.', faits), [])
        self.assertEqual(orientations('Gorm est ici et elle est derrière toi.', faits), [])
        self.assertEqual(orientations('La trousse de crochets est derrière toi et à ta gauche, '
                                     'mais tu ne peux pas encore la prendre.', faits), [])

    def test_lumiere_percue_source_non_vue_et_autre_source(self):
        autre = conduite()
        lampe = autre.objets['lanterne']
        lampe['lieu'] = autre.joueur['salle']
        placer(lampe, lampe['lieu'], autre.objets['brasero']['position'])
        autre.joueur['orientation'] = 'sud-ouest'
        memoriser(autre)
        autre.joueur['orientation'] = 'est'
        for m, source, texte in ((crypte(), 'brasero', 'Le brasero éclaire la pièce.'),
                                 (autre, 'lanterne', 'La lanterne éclaire la pièce.')):
            with self.subTest(scenario=m.data['scenario']['titre'] if 'titre' in m.data['scenario'] else m.joueur['salle']):
                self.assertFalse(m.visible(source))
                self.assertTrue(any(c['source'] == source and c['niveau'] > 0
                                    for c in m.contexte()['perception']['contributions']))
                _, appels = self.accepte(m, 'décris la lumière', texte, audit_lumiere(source))
                faits = appels[0][1]['faits']
                c = next(c for c in faits['perception']['contributions'] if c['source'] == source)
                self.assertTrue(c['effet_percu'])
                self.assertFalse(c['source_visible'])

    def test_source_sans_contribution_refusee_et_extinction_avant_enregistrement(self):
        for m in (crypte(), conduite()):
            with self.subTest(salle=m.joueur['salle']):
                texte, bon = 'Le brasero éclaire la pièce.', 'Ta lanterne éclaire la pièce.'
                faits = m.contexte()
                a = controler(texte, audit_lumiere('brasero'), faits)
                self.assertFalse(a['obstacles'])
                a.update(texte_initial=texte, faits=faits, fondement='brasero')
                m.objets['brasero']['allume'] = False
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as e:
                    consigner(m, {**dialogue(texte), '_audit': a})
                self.assertIn('perception.contributions', e.exception.attendu)
                self.assertEqual(m.data, avant)
                r, sortie, appels = jouer(recharger(m), 'décris la lumière',
                    [dialogue(texte), dialogue(bon)], [audit_lumiere('brasero'), audit_lumiere('lanterne')])
                self.assertNotIn(texte, sortie)
                self.assertNotIn(texte, str(r.data['narrations_mj']))
                self.assertIn(bon, sortie)
                self.assertFalse(r.objets['brasero']['allume'])
                refus = next(e['controle_narratif'] for _, e in appels if 'controle_narratif' in e)
                self.assertIn('perception.contributions', refus[0]['attendu'])
                self.assertNotIn(refus[0]['attendu'], sortie)

    def test_schema_extraction_et_compatibilite_des_anciens_audits(self):
        schema = schema_audit({'perception': {}}, 1)['properties']['segments']['properties']['0']
        self.assertIn('eclairages', schema['required'])
        self.assertFalse(controler('Tu peux regarder.', rapport(ligne('neutre')), {})['obstacles'])
