"""Distinguer une redite d'une nouvelle extinction et de deux objets homonymes."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import ecoute, pnj, social
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.temps import ecouler, instant
from tests.test_social import recharger


class AvisReditsReelsTests(unittest.TestCase):
    def parcours(self, scenario, minute, duree):
        chemin = Path(__file__).parent / 'fixtures/avis_redits' / f'{scenario}-2024-{minute}.json.gz'
        resultats = []
        for tranches in ((duree,), (150,) * (duree // 150)):
            with gzip.open(chemin, 'rt', encoding='utf-8') as f:
                m = recharger(Monde(json.load(f)))
            lignes = []
            rallumages = []
            transmissions = []
            reviser = social.reviser_dits
            retenir = social.retenir_dit
            def revision(monde, id, sujet, attribut, valeur, **details):
                if sujet == 'torche' and attribut == 'etat' and valeur.get('allume'):
                    rallumages.append((id, instant(monde)))
                return reviser(monde, id, sujet, attribut, valeur, **details)
            def transmission(monde, id, auditeur, noyau):
                if (id == 'brune' and noyau.get('objet', noyau.get('sujet')) == 'torche'
                        and noyau.get('attribut') == 'etat' and noyau.get('valeur', {}).get('allume') is False):
                    entree = (auditeur, instant(monde))
                    if entree not in transmissions:
                        transmissions.append(entree)
                return retenir(monde, id, auditeur, noyau)
            with patch.object(social, 'reviser_dits', revision), patch.object(social, 'retenir_dit', transmission):
                for dt in tranches:
                    pnj.avancer(m, ecouler(m, dt), lignes, dt)
                    m = recharger(m)
            sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
            visible = regarder(m), ecoute.rendre(m, sons)
            recharge = recharger(m)
            self.assertEqual(visible, (regarder(recharge), ecoute.rendre(recharge, sons)))
            resultats.append((m.data, visible, rallumages, transmissions))
        self.assertEqual(*resultats)
        self.rallumages = rallumages
        self.transmissions = transmissions
        return m

    def test_mine_2024_deux_lampes_homonymes_restent_deux_faits(self):
        m = self.parcours('mine', 70, 12 * 600)
        dits = [c for c in m.data['chronique'] if c['pnj'] == 'josse' and c.get('constat_confie')
                and 'Lucien' in c['texte'] and 'rechange' in c['texte']]
        # Les secours déplacent Rémy : il peut annoncer une des lampes à Mathe
        # devant Lucien. Josse ne répète pas ce que Lucien a déjà entendu.
        # Exiger deux identités et leurs preuves explicites d'audience, sans
        # accepter le repli de deja_dit quand son registre est saturé.
        self.assertTrue(dits)
        identites = set()
        directs = 0
        for objet in ('lampe_rechange_1', 'lampe_rechange_2'):
            self.assertFalse(m.objets[objet]['allume'])
            fait = {'type': 'constat', 'objet': objet, 'attribut': 'etat', 'valeur': {'allume': False}}
            for cle, valeur in social.faits_dits(fait):
                identites.add(cle)
                entree = lire(m, 'josse')['faits_dits'][cle]
                direct = entree['dit_a'].get('lucien') == valeur
                self.assertTrue(direct or valeur in entree.get('entendu_a', {}).get('lucien', []))
                directs += direct
            self.assertTrue(social.deja_dit(m, 'josse', 'lucien', fait))
        self.assertEqual(len(identites), 2)
        self.assertEqual(len(dits), directs)

    def test_crue_2024_chaque_redite_exige_un_rallumage_appris(self):
        m = self.parcours('crue', 140, 110 * 600)
        # La sortie précoce de l'eau change les visites et les allumages.
        # Une seconde annonce exige toujours un rallumage appris entre les deux,
        # sans imposer les horaires d'une ancienne trajectoire.
        self.assertTrue(self.transmissions)
        for auditeur in {a for a, _ in self.transmissions}:
            dits = [t for a, t in self.transmissions if a == auditeur]
            appris = [t for a, t in self.rallumages if a == auditeur]
            for avant, apres in zip(dits, dits[1:]):
                self.assertTrue(any(avant < t <= apres for t in appris))
        # Recevoir la parole ne garantit pas l'adoption de son contenu : la
        # confiance a changé avec les trajets. La réouverture par une perception
        # positive est exercée séparément ci-dessous, sans imposer cette adoption.

    def test_rallumage_prive_ne_rouvre_pas_le_fait_sur_la_capture_rechargee(self):
        chemin = Path(__file__).parent / 'fixtures/avis_redits/crue-2024-140.json.gz'
        with gzip.open(chemin, 'rt', encoding='utf-8') as f:
            m = recharger(Monde(json.load(f)))
        fait = {'type': 'constat', 'objet': 'torche', 'attribut': 'etat', 'valeur': {'allume': False}}
        m.objets['torche']['allume'] = False
        croire(m, 'marchand', 'torche', 'etat', {'allume': False}, 'vu')
        social.retenir_dit(m, 'brune', 'marchand', fait)
        m = recharger(m)
        self.assertTrue(social.deja_dit(m, 'brune', 'marchand', fait))
        m.objets['torche']['allume'] = True
        croire(m, 'marchand', 'torche', 'etat', {'allume': True}, 'vu')
        m.objets['torche']['allume'] = False
        croire(m, 'brune', 'torche', 'etat', {'allume': False}, 'vu')
        m = recharger(m)
        self.assertTrue(social.deja_dit(m, 'brune', 'marchand', fait))
        self.assertEqual(regarder(m), regarder(recharger(m)))
