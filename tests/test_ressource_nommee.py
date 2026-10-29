"""Même demande entre saisie, contenu, enquête, revue et sauvegarde."""
from donjon.emissions import joueur as emissions_joueur
import copy
import unittest

from donjon.paroles import SCHEMA_PAROLE, sens_contenu, verifier_contenus
from donjon.monde import ErreurMonde
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger


class RessourceNommeeTests(unittest.TestCase):
    def jouer_question(self, m, mots, sujet, cible, reponse, propositions=None, revues=()):
        avant = copy.deepcopy(m.data)
        r, texte, appels = jouer(m, mots,
            (propositions or [parole(mots, ('ressource', sujet, '', ''), personnage=cible)])
            + [dialogue(reponse)],
            [rapport(ligne('mecanique', sources=['conversation_validee']))], revues=revues)
        self.assertNotIn('Précise', texte)
        self.assertIn(reponse, texte)
        self.assertIn(reponse, str(r.data['conversation']))
        self.assertEqual(len(emissions_joueur(r)), 1)
        self.assertEqual(emissions_joueur(r)[0]['texte'], mots)
        for k in m.objets:
            self.assertEqual(r.objets[k].get('lieu'), avant['objets'][k].get('lieu'))
        faits = next(e['faits']['conversation_validee']['faits'] for f, e in appels
                     if f == 'repondre_au_joueur' and 'conversation_validee' in e['faits'])
        revue = [e['plan']['parole'] for f, e in appels if f == 'auditer_action'][-1]
        self.assertEqual(revue['contenu'][-1]['sujet'], sujet)
        self.assertEqual([{k: v for k, v in s.items() if k != 'operations'}
                          for s in revue['sens_contenu']], sens_contenu(revue['contenu']))
        self.assertTrue(all(s['operations'] == ['ressource'] for s in revue['sens_contenu']))
        return r, texte, faits, appels

    def test_cas_reel_bois_aubin_repond_et_ne_donne_rien(self):
        m = banc('noms-dialogue')
        r, _, faits, _ = self.jouer_question(m, "est-ce que quelqu'un a du bois ?", 'bois', 'aubin',
                                             "Aubin dit avoir ses planches.")
        self.assertTrue(any('dit avoir les planches de bac' in f for f in faits), faits)
        self.assertEqual(r.objets['planches']['charges'], m.objets['planches']['charges'])

    def test_autre_scenario_lampe_portee_alias_et_absence(self):
        m = banc('sous-obstacle-auberge')
        m.joueur['orientation'] = 'ouest'
        from donjon.paroles import prevue
        from donjon.voix import reel
        cible = prevue(m, 'As-tu une lampe ?')['personnage']
        qui = reel(m, cible)
        # Même mécanisme pour un bien durable, sans ressource comptée ni foyer.
        m.objets['lampe_temoin'] = {**banc('noms-dialogue').objets['lanterne'], 'id': 'lampe_temoin',
            'nom': 'lanterne de voyage', 'aliases': ['lampe'], 'lieu': qui, 'proprietaire': qui}
        m = recharger(m)
        _, _, faits, _ = self.jouer_question(m, 'As-tu une lampe ?', 'lampe', cible,
                                             "On te répond avoir une lanterne.")
        self.assertTrue(any('dit avoir la lanterne de voyage' in f for f in faits), faits)
        _, _, faits, _ = self.jouer_question(m, "As-tu de l'huile ?", 'huile', cible,
                                             "On te répond ne pas en avoir.")
        self.assertTrue(any("dit n'en avoir pas" in f for f in faits), faits)

    def test_correction_semantique_possible_au_lieu_du_refus_du_moteur(self):
        mots = "est-ce que quelqu'un a du bois ?"
        self.jouer_question(banc('noms-dialogue'), mots, 'bois', 'aubin', "Aubin dit avoir ses planches.",
            propositions=[parole(mots, ('ressource', s, '', ''), personnage='aubin')
                          for s in ('chaleur', 'bois')],
            revues=[{'conforme': False, 'motif': 'Le besoin élargit le bien nommé.'},
                    {'conforme': True, 'motif': ''}])

    def test_contenu_contraire_refuse_sans_effet_avant_correction(self):
        mots = "est-ce que quelqu'un a du bois ?"
        _, _, _, appels = self.jouer_question(banc('noms-dialogue'), mots, 'bois', 'aubin',
            "Aubin dit avoir ses planches.",
            propositions=[parole(mots, ('ressource', s, '', ''), personnage='aubin') for s in ('faim', 'bois')],
            revues=[{'conforme': False, 'motif': 'De la nourriture est contraire au bois demandé.'},
                    {'conforme': True, 'motif': ''}])
        refus = [e['faits']['retour_moteur'] for f, e in appels
                 if f == 'repondre_au_joueur' and 'retour_moteur' in e['faits']]
        self.assertTrue(any('contenu non conforme' in str(x) for x in refus))

    def test_recherche_limitee_aux_possessions_connues(self):
        from donjon.echanges import enqueter
        m = banc('noms-dialogue')
        # Un bien à lui hors de portée mais ignoré ne s'ajoute pas à sa réponse.
        m.objets['secret'] = {**m.objets['lanterne'], 'id': 'secret', 'lieu': 'crypte',
                              'proprietaire': 'aubin'}
        self.assertEqual(enqueter(m, 'joueur', 'aubin', 'lampe'), ('rien', []))
        m = recharger(m)
        self.assertEqual(enqueter(m, 'joueur', 'aubin', 'lampe'), ('rien', []))

    def test_sujet_vide_refus_avec_attendu_et_sens_generaux_conserves(self):
        m = banc('noms-dialogue')
        with self.assertRaises(ErreurMonde) as refus:
            verifier_contenus(m, [{'type': 'ressource', 'sujet': ''}])
        self.assertIn('contenu[0].sujet', refus.exception.attendu)
        for sujet in ('faim', 'chaleur', 'lampe', 'huile'):
            c = {'type': 'ressource', 'sujet': sujet}
            verifier_contenus(m, [c])
            self.assertTrue(sens_contenu([c])[0]['ressource_recherchee'])
        self.assertIn('bien nommé', str(SCHEMA_PAROLE))
