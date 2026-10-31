"""Distinguer une redite d'une nouvelle extinction et de deux objets homonymes."""
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import ecoute, pnj, social
from donjon.esprits import croire, lire, percevoir
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler, instant
from tests.test_social import recharger
from tests.support import canal_constats_anterieur_337


class AvisReditsReelsTests(unittest.TestCase):
    def parcours(self, scenario, minute, duree, secours_spontane=True, preparer=None):
        chemin = Path(__file__).parent / 'fixtures/avis_redits' / f'{scenario}-2024-{minute}.json.gz'
        resultats = []
        for tranches in ((duree,), (150,) * (duree // 150)):
            with gzip.open(chemin, 'rt', encoding='utf-8') as f:
                m = recharger(Monde(json.load(f)))
            if preparer:
                preparer(m)
                m = recharger(m)
            if not secours_spontane:
                # L'oracle porte sur l'audience de deux faits : conserver
                # les déplacements historiques sans nouveau secours autonome.
                from tests.support import sans_souci
                sans_souci(m)
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
            scene = scene_percue(m)
            recharge = recharger(m)
            self.assertEqual(m.data, recharge.data)
            self.assertEqual(visible, (regarder(recharge), ecoute.rendre(recharge, sons)))
            self.assertEqual(scene, scene_percue(recharge))
            resultats.append((m.data, visible, rallumages, transmissions))
        self.assertEqual(*resultats)
        self.rallumages = rallumages
        self.transmissions = transmissions
        return m

    # 360 : cette capture éprouve la non-redite de constats de 55 déclarés
    # récents ; la provenance réelle reste dans test_nouvelles_initiales.
    @canal_constats_anterieur_337
    def test_mine_2024_deux_lampes_homonymes_restent_deux_faits(self):
        m = self.parcours('mine', 70, 12 * 600, secours_spontane=False)
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

    def extinction_apprise(self, m):
        # Cette ancienne capture n'a pas la provenance du 360. Sa migration
        # ancre l'état porté actuel ; la chronique atteste pourtant l'aller-
        # retour appris : Brune allume à 97, éteint à 104, prévient Aubin à 122.
        # Restituer la vue antérieure attestée, puis lui faire percevoir
        # l'extinction actuelle, sans modifier la torche ni forcer une parole.
        for minute, texte in ((97, 'allume la torche.'), (104, 'éteint la torche.')):
            self.assertTrue(any(c['pnj'] == 'brune' and c['minute'] == minute
                                and c['texte'].endswith(texte) for c in m.data['chronique']))
        fait = {'type': 'constat', 'objet': 'torche', 'attribut': 'etat', 'valeur': {'allume': False}}
        self.assertTrue(social.deja_dit(m, 'brune', 'aubin', fait))
        self.assertFalse(any(n[1].get('objet') == 'torche' and n[1].get('attribut') == 'etat'
                             for n in social.nouvelles(m, 'brune')))
        etat = lire(m, 'brune')['croyances']['torche']['etat']['valeur']
        croire(m, 'brune', 'torche', 'etat', {**etat, 'allume': True}, 'vu', minute=97)
        percevoir(m, 'brune')
        self.assertFalse(m.objets['torche']['allume'])
        self.assertEqual(lire(m, 'brune')['croyances']['torche']['etat']['valeur'], etat)
        self.assertTrue(any(n[1].get('objet') == 'torche' and n[1].get('attribut') == 'etat'
                            for n in social.nouvelles(m, 'brune')))
        # Le savoir propre de Brune ne rouvre pas son ancien destinataire.
        self.assertTrue(social.deja_dit(m, 'brune', 'aubin', fait))

    def test_crue_2024_chaque_redite_exige_un_rallumage_appris(self):
        # 395, décision utilisateur : isoler les avis des buts concurrents de
        # souci spontané, comme les lampes du 375. Besoins, liens, audience et
        # jets restent ceux de la capture ; aucune confidence n'est imposée.
        m = self.parcours('crue', 140, 110 * 600, secours_spontane=False,
                          preparer=self.extinction_apprise)
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

    def test_crue_2024_non_isolee_aucune_redite_sans_rallumage_appris(self):
        # 395 : conserver aussi le sens négatif avec les profils d'origine.
        # Une absence de parole ici ne prouve pas la transmission spontanée.
        self.parcours('crue', 140, 110 * 600, preparer=self.extinction_apprise)
        for auditeur in {a for a, _ in self.transmissions}:
            dits = [t for a, t in self.transmissions if a == auditeur]
            appris = [t for a, t in self.rallumages if a == auditeur]
            for avant, apres in zip(dits, dits[1:]):
                self.assertTrue(any(avant < t <= apres for t in appris))

    def test_rallumage_appris_rouvre_le_fait_sur_la_capture_rechargee(self):
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
        self.assertFalse(social.deja_dit(m, 'brune', 'marchand', fait))
        self.assertEqual(regarder(m), regarder(recharger(m)))
