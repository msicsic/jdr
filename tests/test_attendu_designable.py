"""Refus, références publiques, connaissance et reprise de la partie (lot 65)."""
import copy
import re
import unittest

from donjon.banc_pnj import creer
from donjon.commandes import analyser
from donjon.improvisation import proposition as improviser, issue
from donjon.monde import ErreurMonde, nouveau_monde
from donjon.moteur import ACTIONS, Moteur, proposition
from donjon.noms import public, reference
from donjon.operations import OPERATIONS, etape, sequence
from donjon.refus import cibles, inaccessible, perception
from donjon.rendu import regarder
from donjon.voix import apprendre_nom
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_refus import refus
from tests.test_repli_et_appel import dialogue
from tests.test_tensions import placer, recharger
from tests.support import calme


class AttenduDesignableTests(unittest.TestCase):
    def assertReferences(self, m, attendu, recus=()):
        """Aucun identifiant privé ni référence d'entité non désignable dans le refus."""
        mots = set(re.findall(r"[\w-]+", attendu))
        for id in m.objets:
            if id in recus:
                continue
            ref = reference(m, id)
            if not m.designable(id):
                self.assertNotIn(id, mots, attendu)
                self.assertNotIn(ref, mots, attendu)
            elif ref != id:
                self.assertNotIn(id, mots, attendu)

    def conduite(self):
        m = creer('relais', 1985, 'fixe')
        calme(m, 'marchand', 'aubin', 'brune', 'ilse')
        # Dans ce scénario la conduite porte encore l'id interne echoppe.
        m.joueur.update(salle='echoppe', position=[1, 2], orientation='ouest')
        return recharger(m)

    def test_cas_reel_conduite_retour_mj_console_et_recharge(self):
        m = self.conduite()
        avant = copy.deepcopy(m.data)
        p = proposition('prendre', 'pied-de-biche')
        attendu = refus(m, p).attendu
        self.assertNotIn('brune', attendu)
        self.assertNotIn('marchand', attendu)
        self.assertNotIn('barbe_gorm', attendu)
        self.assertReferences(m, attendu)
        # Le MJ simulé reçoit le contrat, puis explique le refus sans déplacer un objet.
        reponse = {'mode': 'action', 'texte': '', 'faits': [], 'proposition': p}
        r, sortie, appels = jouer(m, 'je prends le pied-de-biche',
            [reponse, dialogue('Tu ne vois rien de tel ici.')],
            [rapport(ligne('mecanique', sources=['retour_moteur']))])
        retour = next(e['faits']['retour_moteur'] for f, e in appels
                      if f == 'repondre_au_joueur' and 'retour_moteur' in e['faits'])
        self.assertReferences(r, retour['attendu'])
        self.assertIn('Tu ne vois rien de tel ici.', sortie)
        self.assertNotIn('références', sortie)
        self.assertNotIn('personne_', sortie)
        self.assertEqual(r.objets, avant['objets'])
        self.assertEqual(r.joueur['salle'], avant['joueur']['salle'])
        self.assertEqual(r.joueur['or'], avant['joueur']['or'])
        self.assertEqual(regarder(r), regarder(recharger(r)))
        self.assertEqual(retour['attendu'], public(r, {'attendu': retour['attendu']})['attendu'])

    def test_personne_inconnue_dans_le_noir_et_commande_locale(self):
        m = self.conduite()
        for o in m.objets.values():
            if 'allume' in o:
                o['allume'] = False
        m.data['souvenirs_visuels'] = {}
        m.data['personnages_vus'] = []
        m.data['connus'] = []
        # La même règle borne une saisie locale et une proposition du MJ.
        m = recharger(m)
        avant, vue = copy.deepcopy(m.data), regarder(m)
        with self.assertRaises(ErreurMonde) as local:
            analyser(m, 'prendre Gorm')
        self.assertReferences(m, local.exception.attendu)
        self.assertNotIn('marchand', local.exception.attendu)
        self.assertReferences(m, public(m, {'attendu': refus(m, proposition('prendre', 'Gorm')).attendu})['attendu'])
        self.assertEqual(m.data, avant)
        r = recharger(m)
        self.assertEqual(r.data, avant)
        self.assertEqual(regarder(r), vue)
        self.assertIn("aucune cible de ce nom n'est désignable ici", cibles(m, ['marchand']))

    def test_references_publiques_et_souvenir_ne_donnent_pas_acces(self):
        m = self.conduite()
        ref = reference(m, 'marchand')
        self.assertRegex(ref, r'personne_\d+')
        self.assertIn(ref, cibles(m, ['marchand']))
        self.assertIn(ref, public(m, {'attendu': 'acceptés : ' + cibles(m, ['marchand'])})['attendu'])
        # Un souvenir marqué et un nom appris restent désignables hors de vue.
        m.data['souvenirs_visuels']['poutre_conduite'] = {
            'salle': 'echoppe', 'position': [3, 3], 'nom': 'la poutre effondrée', 'symbole': '#'}
        apprendre_nom(m, 'joueur', 'marchand')
        m.joueur.update(salle='chambre_cloche', position=[1, 1], orientation='nord')
        m = recharger(m)
        for id in ('marchand', 'poutre_conduite'):
            self.assertTrue(m.designable(id))
            self.assertFalse(m.accessible(id))
            self.assertIn(reference(m, id), cibles(m, [id]))
            avant = copy.deepcopy(m.data)
            self.assertIsInstance(refus(m, proposition('prendre', id)), ErreurMonde)
            self.assertEqual(m.data, avant)
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_parcours_des_refus_cibles_actions_operations_et_aides(self):
        for m in (self.conduite(), recharger(nouveau_monde())):
            # Couvre toutes les entrées d'action et d'opération : celles qui refusent
            # une cible ne peuvent proposer un id caché ou privé.
            for p in ([proposition(a, 'introuvable') for a in ACTIONS]
                      + [sequence(etape(op, 'introuvable')) for op in OPERATIONS]
                      + [improviser('Saisir.', issue('Tu saisis.'), cibles=['introuvable'])]):
                with self.subTest(action=p):
                    try:
                        Moteur(m).preparer(p)
                    except ErreurMonde as exc:
                        self.assertReferences(m, public(m, {'attendu': exc.attendu})['attendu'])
            # Les aides spécialisées reçoivent aussi des candidats volontairement
            # trop larges : le constructeur commun les borne avant projection.
            for exc in (inaccessible(m, 'introuvable'), perception(m, 'marchand', acceptes=list(m.objets))):
                self.assertReferences(m, public(m, {'attendu': exc.attendu})['attendu'], recus=['marchand'])
            self.assertReferences(m, cibles(m, m.objets))

    def test_refus_de_combat_ne_liste_pas_tous_les_personnages(self):
        from donjon.combat import valider
        m = self.conduite()
        with self.assertRaises(ErreurMonde) as refuse:
            valider(m, 'joueur', 'introuvable')
        self.assertReferences(m, refuse.exception.attendu)
        self.assertNotIn('brune', refuse.exception.attendu)
