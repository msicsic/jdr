"""G16 : mots, croyance et rendu dans la console réelle, puis après recharge."""
import copy
import unittest

from donjon.emissions import pnj
from donjon.esprits import croire, croyance, lire
from donjon.monde import ErreurMonde
from donjon.narration import consigner
from donjon.paroles import SCHEMA_PAROLE, preparer_parole
from donjon.repliques_moteur import reponse, sceller
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.consentement_support import jouer
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import parole, dialogue
from tests.test_tensions import recharger


class InformationsParleesTests(unittest.TestCase):
    def assertRecharge(self, m, sortie):
        r = recharger(m)
        self.assertEqual(r.data, m.data)
        self.assertEqual(regarder(r), regarder(m))
        self.assertEqual(scene_percue(r), scene_percue(m))
        self.assertEqual(pnj(r), pnj(m))
        for emission in pnj(r):
            if emission['acte'] == 'reponse_information':
                self.assertIn(emission['rendu_public'], sortie)
                self.assertIn(emission['texte'], str(r.data['conversation']))
        return r

    def question(self, m, mots, contenu, qui):
        r, sortie, appels = jouer(m, mots, [parole(mots, *contenu, personnage=qui)], [])
        self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 1)
        self.assertFalse(any(f in ('auditer_narration', 'repondre_dialogue') for f, _ in appels))
        self.assertEqual(pnj(r)[-1]['acte'], 'reponse_information')
        return self.assertRecharge(r, sortie), sortie, appels

    def test_voix_se_nomme_puis_imposture_brune_sans_changer_identite(self):
        m, sortie, _ = self.question(banc('soir-noir'), '« Qui est là ? »', [('qui', '', '', '')], 'personne')
        self.assertEqual(pnj(m)[-1]['texte'], "Je m'appelle Ilse.")
        self.assertEqual(m.data['voix_entendues']['ilse']['se_dit'], 'ilse')
        m, sortie, _ = self.question(m, "« C'est moi, Brune. »", [('nom', 'joueur', '', '')], 'voix_1')
        self.assertEqual(lire(m, 'ilse')['voix_entendues']['joueur']['se_dit'], 'brune')
        self.assertEqual(m.joueur['nom'], 'Corvus')
        self.assertIn('Brune', pnj(m)[-1]['texte'])

    def test_autre_nom_et_refus_de_se_nommer(self):
        from tests.test_avis_menace import relation
        for qui in ('aubin', 'brune'):
            with self.subTest(qui=qui):
                m = banc('ressources')
                relation(m, qui, 'joueur', confiance=0)
                m, _, _ = self.question(m, f'{m.objets[qui]["nom"].split(",")[0]}, qui es-tu ?',
                                       [('qui', '', '', '')], qui)
                self.assertEqual(pnj(m)[-1]['texte'], 'Je refuse de te dire mon nom.')
                self.assertEqual(pnj(m)[-1]['modalite'], 'refus')

    def test_ressources_reelles_et_refus_sans_transfert(self):
        for qui, sujet in [('aubin', 'bois'), ('brune', 'faim'), ('aubin', 'diamant')]:
            with self.subTest(qui=qui, sujet=sujet):
                m = banc('ressources')
                avant = copy.deepcopy(m.objets)
                mots = f'{m.objets[qui]["nom"].split(",")[0]}, as-tu {sujet} ?'
                r, _, _ = self.question(m, mots, [('ressource', sujet, '', '')], qui)
                self.assertEqual(r.objets, avant)
                mots = pnj(r)[-1]['texte']
                self.assertTrue(mots.startswith("J'ai ") if sujet == 'bois' else mots == "Je n'en ai pas.")

    def test_localisation_crue_fausse_et_autre_croyance_datee(self):
        from donjon.geometrie import placer
        for sujet, lieu_cru, lieu_reel in [('ilse', 'crypte', 'beffroi'), ('brune', 'beffroi', 'crypte')]:
            with self.subTest(sujet=sujet):
                m = banc('noms-dialogue')
                m.objets[sujet]['lieu'] = lieu_reel
                placer(m.objets[sujet], lieu_reel, [3, 3])
                croire(m, 'aubin', sujet, 'lieu', lieu_cru, 'vu', 1.0, salle=lieu_cru, case=None)
                m = recharger(m)
                nom = m.objets[sujet]['nom'].split(',')[0]
                r, _, _ = self.question(m, f'Aubin, où est {nom} ?', [('localisation', sujet, '', '')], 'aubin')
                self.assertEqual(croyance(r, 'joueur', sujet, 'lieu')['valeur'], lieu_cru)
                self.assertEqual(r.objets[sujet]['lieu'], lieu_reel)
                self.assertIn(m.data['salles'][lieu_cru]['nom'].lower(), pnj(r)[-1]['texte'].lower())
                self.assertIn("J'ai vu à la minute", pnj(r)[-1]['texte'])

    def test_information_et_compte_dans_ordre_sans_reformulation(self):
        m = banc('comptes')
        mots = 'Gorm, as-tu du bois et rends-moi les pièces dues.'
        r, sortie, appels = jouer(m, mots, [parole(mots, ('ressource', 'bois', '', ''),
            ('reclamer', '', '', ''), personnage='marchand')], [])
        texte = pnj(r)[-1]['texte']
        self.assertLess(texte.index("J'ai"), texte.index('Je te rends 2 pièces.'))
        self.assertEqual(r.joueur['or'], m.joueur['or'] + 2)
        self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
        self.assertRecharge(r, sortie)

    def test_propos_residuel_garde_redaction_et_audit(self):
        from tests.test_audits_attendu import ligne, rapport
        m = banc('ressources')
        m.objets['aubin']['profil']['caracteristiques']['INT'] = 14
        mots = 'Aubin, as-tu du bois ? Que penses-tu du calme ?'
        libre = 'Le calme me plaît.'
        r, sortie, appels = jouer(m, mots, [parole(mots, ('ressource', 'bois', '', ''),
            ('propos', '', '', ''), personnage='aubin'), dialogue(f'« {libre} »')],
            [rapport(ligne('parole', locuteur='aubin', citation=libre))])
        audits = [e for f, e in appels if f == 'auditer_narration']
        self.assertEqual(len(audits), 1)
        self.assertEqual(list(audits[0]['segments'].values()), [f'« {libre} »'])
        self.assertIn(libre, sortie)
        self.assertRecharge(r, sortie)

    def test_publication_refuse_reformulation_omission_et_double(self):
        m = banc('ressources')
        p = parole('Aubin, as-tu du bois ?', ('ressource', 'bois', '', ''), personnage='aubin')['proposition']
        prepare, rapport = preparer_parole(m, {k: p[k] for k in SCHEMA_PAROLE['required']})
        exacte = sceller(reponse(rapport), rapport)
        consigner(prepare, exacte)
        for texte in ('Il te donne du bois.', '', exacte['texte'] + ' ' + exacte['texte']):
            with self.subTest(texte=texte):
                with self.assertRaises(ErreurMonde) as e:
                    consigner(prepare, {**exacte, 'texte': texte})
                self.assertTrue(e.exception.attendu)
        self.assertEqual(m.data['revision'] + 1, prepare.data['revision'])


if __name__ == '__main__':
    unittest.main()
