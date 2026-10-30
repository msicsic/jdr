"""Rappels du passé : vraie boucle console, sauvegarde et références publiques."""
from donjon.emissions import pnj as emissions_pnj
import copy
import json
from pathlib import Path
import unittest

from donjon.narration import controler, echanges_passes, schema_audit
from donjon.dialogues import interlocuteurs
from tests.test_parole_corrections import banc, audit, ligne, narration
from tests.test_repli_et_appel import dialogue, jouer, parole, mj
from tests.test_tensions import recharger


def controle(qui, mots, rappel=None):
    l = ligne('parole', qui, mots)
    l['rappels'] = [] if rappel is None else [dict(locuteur=qui, affirmation=mots, compatibilite=rappel)]
    return audit(l)


class RedirePasseTests(unittest.TestCase):
    def test_rappels_rapportes_apres_recharge_et_ordre_explicite(self):
        from tests.test_parole_commune import scene
        scenes = [(self.dire(banc('soir-noir'), 'personne', 'Qui est là ?',
                            "Je m'appelle Ilse.", ('qui', '', '', '')),
                   'voix_1', "Je m'appelle Ilse.", "Je t’ai déjà dit que je m'appelle Ilse."),
                  (scene(), 'aubin', 'La lune est verte.',
                   'Je t’ai dit que la lune est verte.')]
        for m, qui, ancien, rappel in scenes:
            with self.subTest(qui=qui):
                if qui == 'aubin':
                    m.data.setdefault('paroles_pnj', []).append(dict(locuteur=qui,
                        texte=ancien, auditeurs=['joueur'], revision=m.data['revision'],
                        minute=m.data['minutes'], salle=m.joueur['salle']))
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                mots = 'Aubin, et alors ?' if qui == 'aubin' else 'Et alors ?'
                r, sortie, appels = jouer(m, '« ' + mots + ' »', [
                    parole(mots, ('propos', '', '', ''), personnage=qui),
                    dialogue(('Aubin' if qui == 'aubin' else 'Une voix') + ' répond : « ' + rappel + ' »')],
                    [controle(qui, rappel, 'etablie')])
                self.assertIn(rappel, sortie)
                dossier = narration(appels)['faits']['echanges_passes'][qui]
                self.assertEqual(dossier[0]['texte'], ancien)
                self.assertEqual(dossier[0]['ordre_chronologique'], 1)
                self.assertEqual(dossier[0]['anteriorite']['statut'],
                                 'deja_prononcee_et_entendue_par_Corvus')
                self.assertEqual(dossier[0]['anteriorite']['par_rapport_a'],
                                 'reponse_en_cours_non_encore_prononcee')
                recharge = recharger(r)
                self.assertEqual(recharge.data, r.data)
                self.assertEqual(emissions_pnj(recharge)[-1]['texte'], rappel)
                self.assertIn(rappel, recharge.data['conversation'][-1]['reponse'])
                self.assertEqual(recharge.data['jets'], avant['jets'])
                for identifiant, objet in avant['objets'].items():
                    for champ in ('salle', 'position', 'porteur', 'portions'):
                        self.assertEqual(recharge.objets[identifiant].get(champ), objet.get(champ))

    def test_audit_exact_de_la_partie_archivee(self):
        d = json.loads((Path(__file__).parent / 'data/redire-passe-112.json').read_text(encoding='utf-8'))
        # Le rapport ancien reste lisible : c'est précisément le défaut reproduit.
        self.assertFalse(controler(d['texte'], d['rapport'], d['faits'])['obstacles'])
        faits = copy.deepcopy(d['faits'])
        faits['echanges_passes'] = {'voix_1': [p for p in faits['paroles_entendues'] if p['locuteur'] == 'voix_1']}
        rapport = copy.deepcopy(d['rapport'])
        rapport['segments']['0']['rappels'] = [dict(locuteur='voix_1',
            affirmation=rapport['segments']['0']['citation'], compatibilite='contradictoire')]
        refus = controler(d['texte'], rapport, faits)['obstacles']
        self.assertEqual(len(refus), 1)
        self.assertIn(faits['echanges_passes']['voix_1'][0]['texte'], refus[0]['attendu'])

    def dire(self, m, qui, mots, reponse, contenu=('propos', '', '', '')):
        return jouer(m, '« ' + mots + ' »', [parole(mots, contenu, personnage=qui),
                     dialogue('Une voix répond : « ' + reponse + ' »')], [controle('voix_1', reponse)],
                     suite=("tenter",))[0]

    def test_cas_reel_tour_cinq_refuse_corrige_et_recharge(self):
        m = banc('soir-noir')
        m = self.dire(m, 'personne', 'Qui est là ?', 'C’est Ilse. Qui va là ?', ('qui', '', '', ''))
        m = self.dire(m, 'voix_1', 'Tu as de quoi manger ?', 'Non, je n’en ai pas.', ('ressource', 'faim', '', ''))
        m = self.dire(m, 'voix_1', "C'est moi, Brune.", 'Tu n’es pas Brune. Qui es-tu ?', ('nom', 'joueur', '', ''))
        faux = 'Je t’ai déjà dit que je ne te dirai pas qui je suis.'
        bon = "Je refuse de te dire mon nom."
        r, sortie, appels = jouer(recharger(m), "je demande à la voix comment elle s'appelle", [
            parole("Comment tu t'appelles ?", ('qui', '', '', ''), personnage='voix_1'),
            dialogue('La voix répond : « ' + faux + ' »'), dialogue('La voix répond : « ' + bon + ' »')],
            [controle('voix_1', faux, 'contradictoire'), controle('voix_1', bon, 'etablie')])
        self.assertNotIn(faux, sortie)
        self.assertIn(bon, sortie)
        self.assertEqual(emissions_pnj(r)[-1]['texte'], bon)
        self.assertNotIn(faux, str(r.data['conversation']))
        self.assertEqual(len(mj(appels)), 1)  # G16 : aucun récit du nom ni faux rappel admis.
        self.assertFalse(any(f == 'auditer_narration' for f, _ in appels))
        self.assertNotIn(faux, str(emissions_pnj(r)))
        historique = mj(appels)[0]['faits']['echanges_passes']
        self.assertEqual(historique['voix_1'][0]['texte'], "Je m'appelle Ilse.")
        self.assertNotIn('ilse', historique)
        corrections = [e['controle_narratif'] for e in mj(appels) if 'controle_narratif' in e]
        self.assertEqual(corrections, [])  # G16 : aucune rédaction libre à corriger.
        self.assertEqual(len(emissions_pnj(r)), 4)
        self.assertEqual(recharger(r).data['conversation'], r.data['conversation'])

    def test_autre_cas_part_servie_puis_faux_refus(self):
        from tests.test_paroles import relais
        from donjon.echanges import servir
        from donjon.corps import valeurs
        m = relais()
        # Mise en place de la rencontre, puis véritable service par le moteur.
        from tests.test_tensions import placer
        m.joueur['salle'] = 'antichambre'
        placer(m, 'marchand', 'antichambre', (6, 3))
        m.joueur['position'] = [6, 4]
        from tests.support import regarder
        regarder(m, 'joueur', 'marchand')
        regarder(m, 'marchand', 'joueur')
        valeurs(m, 'joueur')['faim'] = 80
        avant = m.objets['vivres']['portions']
        self.assertTrue(servir(m, 'marchand', 'vivres', 'joueur', []))
        dit = 'Oui, tu as reçu ta part.'
        m, sortie, _ = jouer(recharger(m), '« Gorm, merci pour la part. »', [
            parole('Gorm, merci pour la part.', ('propos', '', '', ''), personnage='marchand'),
            dialogue('Gorm répond : « ' + dit + ' »')], [controle('marchand', dit)])
        faux, bon = 'Je t’ai refusé cette part, je te l’ai dit.', 'Tu as reçu ta part, comme je te l’ai dit.'
        r, sortie, appels = jouer(recharger(m), '« Gorm, et ma part ? »', [
            parole('Gorm, et ma part ?', ('propos', '', '', ''), personnage='marchand'),
            dialogue('Gorm répond : « ' + faux + ' »'), dialogue('Gorm répond : « ' + bon + ' »')],
            [controle('marchand', faux, 'contradictoire'), controle('marchand', bon, 'etablie')])
        self.assertNotIn(faux, sortie)
        self.assertIn(bon, sortie)
        self.assertEqual(r.objets['vivres']['portions'], avant - 1)
        self.assertLess(valeurs(r, 'joueur')['faim'], 80)
        self.assertNotIn(faux, str(r.data['conversation']))
        self.assertEqual(emissions_pnj(r)[-1]['texte'], bon)
        self.assertIn(dit, str(narration(appels)['faits']['echanges_passes']['marchand']))

    def test_historique_sans_fenetre_globale_et_sans_auditeurs_prives(self):
        m = banc('soir-noir')
        m = self.dire(m, 'personne', 'Qui est là ?', 'C’est Ilse.', ('qui', '', '', ''))
        m.data.setdefault('paroles_pnj', []).extend([dict(locuteur='aubin', texte='Un autre échange.',
            auditeurs=['joueur'], revision=1, salle='beffroi', minute=0)] * 12)
        m.data['paroles_pnj'].append(dict(locuteur='ilse', texte='Secret.', auditeurs=['aubin'], revision=1, salle='beffroi', minute=0))
        faits = echanges_passes(recharger(m), interlocuteurs(m))
        self.assertEqual([p['texte'] for p in faits['voix_1']], ["Je m'appelle Ilse."])
        self.assertNotIn('auditeurs', str(faits))
        self.assertNotIn('Secret', str(faits))

    def test_ordre_croissant_et_parole_de_la_revision_courante_deja_entendue(self):
        m = banc('soir-noir')
        m.data['revision'] = 5
        m.data['paroles_pnj'] = [dict(locuteur='ilse', texte=texte,
            auditeurs=['joueur'], revision=revision, minute=0, salle='beffroi')
            for texte, revision in [('Seconde.', 5), ('Première.', 2)]]
        avant = copy.deepcopy(m.data)
        paroles = echanges_passes(recharger(m), {'ilse': {'nom': 'Une voix'}})['ilse']
        self.assertEqual([p['texte'] for p in paroles], ['Première.', 'Seconde.'])
        self.assertEqual([p['ordre_chronologique'] for p in paroles], [1, 2])
        self.assertTrue(all(p['anteriorite']['revision_courante'] == 5 for p in paroles))
        self.assertEqual(m.data, avant)

    def test_schema_exige_rappels_pour_tous_les_verdicts(self):
        s = schema_audit({'echanges_passes': {}}, 1)
        for v in s['properties']['segments']['properties']['0']['anyOf']:
            self.assertIn('rappels', v['required'])

    def test_rappel_refuse_meme_sous_verdict_neutre_et_rapport_relu(self):
        faits = {'echanges_passes': {'voix_1': [{'texte': 'Je te donne mon nom.'}]}}
        l = ligne('neutre')
        l['rappels'] = [dict(locuteur='voix_1', affirmation='Elle a refusé de se nommer.', compatibilite='contradictoire')]
        r = controler('Elle a refusé de se nommer.', audit(l), faits)
        self.assertIn('Je te donne mon nom.', r['obstacles'][0]['attendu'])
        self.assertEqual(controler('Elle a refusé de se nommer.', {'segments': r['segments']}, faits)['obstacles'], r['obstacles'])
