"""G1 b : contrat fourni et chaîne console/monde/rendu/recharge, sans réseau."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon.compilateur import SCHEMA_COMPILATEUR
from donjon.couverture_action import entree
from donjon.dialogues import preparer_conversation
from donjon.agendas import contrats
from donjon.improvisation import effet, issue, proposition as improviser
from donjon.monde import nouveau_monde, Monde
from donjon.moteur import Moteur, SENS_PERCEPTIONS, proposition
from donjon.paroles import preparer_parole
from donjon.rendu import regarder, fiche, carte
from donjon.scene import scene_percue
from tests import test_cache_kv_local as cache
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_gardes_justes import crypte
from tests.test_parole_corrections import banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_relances_luna import action
from tests.test_tensions import recharger


class CompilateurFideliteTests(unittest.TestCase):
    def reprise(self, m):
        r = recharger(m)
        self.assertEqual(r.data, m.data)
        self.assertEqual((regarder(r), fiche(r), carte(r), scene_percue(r)),
                         (regarder(m), fiche(m), carte(m), scene_percue(m)))
        return r

    def test_projection_retablit_preuves_publiques_sans_source_invisible(self):
        for m in (nouveau_monde(), crypte()):
            with self.subTest(salle=m.joueur['salle']):
                avant = copy.deepcopy(m.data)
                _, e, _, _ = cache.PrefixeKVTests()._capter_appel(m, 'Que sais-je déjà de cet endroit ?')
                f = e['faits']
                self.assertIn('attestations', f)
                self.assertIn('evenements_recents', f)
                self.assertIn('niveau', f['perception'])
                self.assertNotIn('contributions', f['perception'])
                self.assertNotIn('esprits_interlocuteurs', f)
                self.assertNotIn('objet:anneau', f)
                self.assertEqual(m.data, avant)
                self.reprise(m)

    def test_questions_au_mj_ne_creent_pas_de_parole(self):
        for saisie, texte, audit in (
            ('ça sent quoi, ici ?', 'Une odeur de pierre humide flotte ici.',
             ligne('ambiance', entites=['odeur de pierre humide'])),
            ('il fait sombre ici ?', 'Tu y vois assez pour distinguer les détails.',
             ligne('mecanique', sources=['perception']))):
            with self.subTest(saisie=saisie):
                m = nouveau_monde()
                avant = copy.deepcopy(m.data)
                r, sortie, appels = jouer(m, 'mj ' + saisie, [dialogue(texte)], [rapport(audit)])
                self.assertIn(texte, sortie)
                self.assertNotIn('Tu dis', sortie)
                self.assertEqual(r.objets, m.objets)
                for k in ('minutes', 'jets', 'journal', 'paroles_joueur', 'paroles_pnj'):
                    self.assertEqual(r.data.get(k, []), avant.get(k, []))
                self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 1)
                self.reprise(r)

    def test_rappel_d_inscription_connue_sans_nouveau_jet(self):
        for inscription in ('Au veilleur revient le dernier serment.', 'La porte se ferme au soir.'):
            with self.subTest(inscription=inscription):
                m = nouveau_monde()
                m.objets['gravure']['inscription'] = inscription
                with patch.object(Monde, 'd20', return_value=20):
                    moteur = Moteur(m)
                    texte_lu = moteur.executer(moteur.preparer(proposition('lire', 'gravure')))
                m.memoriser('lire gravure', texte_lu, 'resultat_moteur')
                m = self.reprise(m)
                avant = copy.deepcopy(m.data)
                texte = f'L’inscription dit : « {inscription} »'
                r, sortie, appels = jouer(m, 'mj que dit cette inscription, exactement ?',
                    [dialogue(texte)], [rapport(ligne('mecanique', sources=['objet:gravure']))])
                self.assertIn(inscription, sortie)
                for k in ('minutes', 'jets', 'journal'):
                    self.assertEqual(r.data[k], avant[k])
                self.assertEqual(texte_lu, appels[0][1]['conversation'][0]['reponse'])
                self.assertIn('Tu comprends', str(appels[0][1]['faits']['evenements_recents']))
                self.reprise(r)

    def test_sons_effectifs_deux_formes_sans_jet_ni_reaction_inventee(self):
        for saisie, forme in (('je fredonne doucement', 'voix_melodique'),
                              ('je frappe doucement un rythme dans mes mains', 'corps_rythmique')):
            with self.subTest(forme=forme):
                m = nouveau_monde()
                p = improviser(saisie, issue('Brouillon.', [effet('son', 'joueur', texte=forme, valeur=1)]), minutes=0)
                r, sortie, appels = jouer(m, 'mj ' + saisie, [action(p)], [])
                self.assertEqual(r.data['jets'], m.data['jets'])
                self.assertEqual(r.data['journal'][-1]['action']['reussite']['effets'][0]['texte'], forme)
                self.assertNotIn('« tenter »', sortie)
                self.assertEqual(r.data['sons'][-1]['forme'], forme)
                self.assertEqual(r.data['sons'][-1]['intensite'], 1)
                self.assertEqual(sum(f == 'repondre_au_joueur' for f, _ in appels), 1)
                self.reprise(r)

    def test_prix_de_mission_et_amelioration_ne_sont_pas_confondus(self):
        for saisie, operation, montant in (("Gorm, combien me donnes-tu pour l'anneau ?", 'proposer', 0),
                                           ('Gorm, je veux vingt-quatre pièces pour cet anneau.', 'negocier', 24)):
            with self.subTest(operation=operation):
                m = crypte()
                mission = next(iter(m.data['missions']))
                p = dict(personnage='marchand', sujet=saisie, operation=operation, mission=mission,
                         montant_demande=montant)
                attendu, _ = preparer_conversation(m, p)
                r, sortie, appels = jouer(m, 'mj ' + saisie,
                    [dict(mode='conversation_pnj', texte='', faits=[], proposition=p), dialogue('Ta demande est entendue.')],
                    [rapport(ligne('mecanique', sources=['conversation_validee']))])
                self.assertEqual(contrats(r), contrats(attendu))
                self.assertEqual(contrats(r)[mission]['montant'], 20 if operation == 'proposer' else 22)
                self.assertEqual(r.joueur['or'], m.joueur['or'])
                self.assertIn(str(contrats(r)[mission]['montant']), sortie)
                self.assertEqual(appels[0][1]['faits']['missions_discutables'].keys(), {mission})
                self.reprise(r)

    def test_marche_garde_part_reference_et_prix_deux_montants(self):
        for prix in (3, 4):
            with self.subTest(prix=prix):
                m = banc('soir-appel')
                mots = f'Je te paie {prix} pièces pour une de tes planches.'
                saisie = f'je paie Aubin {prix} pièces pour une de ses planches'
                contenu = {'type': 'proposition', 'demande': {'type': 'part', 'objet': 'planches'},
                           'contrepartie': {'type': 'pieces', 'montant': prix}}
                p = parole(mots, personnage='aubin')
                p['proposition']['contenu'] = [contenu]
                p['proposition']['operations_demandees']['proposition'] = True
                attendu, _ = preparer_parole(m, {'personnage': 'aubin', 'replique': mots,
                    'contenu': [contenu], '_intention': saisie})
                r, sortie, _ = jouer(m, 'mj ' + saisie, [p, dialogue('Ta proposition est entendue.')],
                    [rapport(ligne('mecanique', sources=['conversation_validee']))])
                self.assertIn(mots, sortie)
                self.assertEqual(r.joueur['or'], attendu.joueur['or'])
                self.assertEqual(r.objets, attendu.objets)
                self.assertEqual(r.data['paroles_joueur'][-1]['texte'], mots)
                self.reprise(r)

    def test_correction_de_parole_sans_audit_ne_publie_ni_prose_ni_message_interne(self):
        for role in ('gardien', 'passeur'):
            with self.subTest(role=role):
                m = banc('echanges')
                mots = f'Tu sais où est passé le {role} ?'
                faux = parole(mots, ('localisation', 'le ' + role, '', ''), personnage='personne_2')
                r, sortie, _ = jouer(m, '« ' + mots + ' »', [faux, dialogue('Analyse interne écartée.')], [])
                self.assertIn('Corvus ne désigne pas une personne connue.', sortie)
                self.assertNotIn('Analyse interne', sortie)
                self.assertNotIn('sans contrôle narratif', sortie)
                self.assertEqual(r.objets, m.objets)
                self.assertEqual(r.data.get('paroles_joueur'), m.data.get('paroles_joueur'))
                self.reprise(r)
                # Le même sujet libre peut être prononcé, sans personne ou position inventée.
                r, sortie, _ = jouer(m, '« ' + mots + ' »', [parole(mots, ('propos', '', '', ''), personnage='personne_2'),
                    dialogue('Ta question est entendue.')], [rapport(ligne('mecanique', sources=['conversation_validee']))])
                self.assertIn(mots, sortie)
                self.assertEqual(r.data['paroles_joueur'][-1]['texte'], mots)
                self.assertEqual(set(r.objets), set(m.objets))
                self.reprise(r)

    def test_contrat_perception_rejoint_la_revue_et_le_schema(self):
        from donjon.couverture_action import entree
        for action_ in ('ecouter', 'observer'):
            plan = Moteur(nouveau_monde()).preparer(proposition(action_))
            self.assertEqual(entree('je perçois', plan)['plan']['contrat_perception'], SENS_PERCEPTIONS[action_])
            schema_simple = SCHEMA_COMPILATEUR['properties']['proposition']['anyOf'][0]
            self.assertIn(SENS_PERCEPTIONS[action_], schema_simple['properties']['action']['description'])

    def test_ecoute_sans_cible_ne_devient_pas_une_qualification_ni_un_deplacement(self):
        for saisie in ("j'écoute à la porte pour savoir s'il y a quelque chose derrière",
                       "je tends l'oreille près de l'ouverture"):
            with self.subTest(saisie=saisie):
                m = nouveau_monde()
                r, sortie, appels = jouer(m, 'mj ' + saisie, [action(proposition('ecouter'))], [])
                self.assertEqual(r.data['minutes'], m.data['minutes'] + 3)
                self.assertEqual(r.joueur.get('position'), m.joueur.get('position'))
                self.assertEqual(r.data['journal'][-1]['action']['action'], 'ecouter')
                revue = next(e for f, e in appels if f == 'auditer_action')
                self.assertEqual(revue['plan']['perception'], {'action': 'ecouter', 'cible': ''})
                self.assertEqual(revue['plan']['contrat_perception'], SENS_PERCEPTIONS['ecouter'])
                self.assertNotIn('Précise la manœuvre', sortie)
                self.reprise(r)

    def test_passage_specialise_et_vol_compose_gardent_leurs_etapes(self):
        from tests.test_sous_obstacle import scene, passage
        from donjon.operations import sequence, etape
        # Deux méthodes de passage ; la fiche n'invente aucune géométrie ni action.
        for methode in ('dessous', 'dessus'):
            m = scene()
            # Ce cas mesure le choix d'opération, sans contrainte d'encombrement.
            for o in m.objets.values():
                if o.get('lieu') == 'joueur':
                    o.update(lieu=m.joueur['salle'], position=list(m.joueur['position']),
                             position_salle=m.joueur['salle'])
            p = passage(methode=methode)
            r, sortie, _ = jouer(m, f'mj puis-je passer {methode} cet obstacle ?', [action(p)], [])
            self.assertEqual(r.objets, m.objets)
            self.assertEqual(r.joueur['position'], m.joueur['position'])
            self.assertIn('tenter', sortie)
            self.assertIn(methode, str(p))
            self.reprise(r)
        # Une occasion de vol ne remplace pas la posture d'un tiers par un fait.
        for cible in ('crochets', 'marteau'):
            m = nouveau_monde()
            moteur = Moteur(m)
            moteur.executer(moteur.preparer(proposition('aller', 'ouest')))
            p = sequence(etape('patienter'), etape('deplacer', cible, 'joueur', methode='discret'))
            r, sortie, _ = jouer(m, f"mj j'attends une occasion pour prendre discrètement {cible}", [action(p)], [])
            self.assertIn('tenter', sortie)
            self.assertEqual(r.objets[cible]['lieu'], m.objets[cible]['lieu'])
            self.assertEqual(r.objets['marchand'], m.objets['marchand'])
            self.assertFalse(any(o.get('origine_description') == 'geste du joueur' for o in r.objets.values()))
            self.reprise(r)


if __name__ == '__main__':
    unittest.main()
