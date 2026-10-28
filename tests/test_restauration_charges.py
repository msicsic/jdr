"""Une suspension appartient à l'engagement, pas au suffixe de ses moyens."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import agendas, deliberation as d, planification as p
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde, ErreurMonde
from donjon.rendu import decrire, regarder
from tests.support import calme, sans_souci
from tests.test_garde_plan import gardien_servant
from tests.test_tensions import placer, recharger, vivre


def avancer_precis(m, dixiemes):
    from donjon.temps import ecouler
    from donjon.pnj import avancer
    minutes = ecouler(m, dixiemes)
    avancer(m, minutes, [], dixiemes)
    return recharger(m)


def livraison(scenario='relais', poste=False):
    if scenario == 'relais':
        m = gardien_servant()
        auteur, autre, contenant = 'marchand', 'brune', 'reserve'
    else:
        m = creer('mine', 1985, 'fixe')
        auteur, autre, contenant = 'mathe', 'lucien', 'garde_manger'
        placer(m, auteur, 'baraquement', [2, 4])
        placer(m, autre, 'baraquement', [4, 4])
        m.joueur.update(salle='galerie', position=[1, 1])
    ids = [i for i, o in m.objets.items() if o.get('profil')]
    calme(m, *ids)
    sans_souci(m)
    for i in ids:
        m.objets[i]['profil']['pulsions'] = []
        lire(m, i)['pulsions'] = []
        for a in agendas.en_cours(m, i):
            agendas.retirer_proposition(m, i, a)
        lire(m, i)['intention'] = None
    garde = {'objet': contenant, 'verrouillee': True}
    m.objets[auteur]['profil']['pulsions'] = [{'besoin': 'biens', 'condition': garde}]
    if poste:
        m.objets[auteur]['profil']['pulsions'].append(
            {'besoin': 'devoir', 'condition': {'objet': auteur, 'lieu': m.objets[auteur]['lieu']}})
        placer(m, autre, 'echoppe', [4, 4])
    m.objets['vivres']['lieu'] = contenant
    m.objets[contenant].update(ouverte=False, verrouillee=True)
    croire(m, auteur, 'vivres', 'lieu', contenant, 'savoir',
           salle=m.objets[auteur]['lieu'], case=list(m.objets[contenant]['position']))
    percevoir_tous(m)
    croire(m, auteur, contenant, 'verrouillee', True, 'essai')
    croire(m, auteur, contenant, 'etat', {'ouverte': False}, 'essai')
    croire(m, auteur, autre, 'lieu', m.objets[autre]['lieu'], 'savoir',
           salle=m.objets[autre]['lieu'], case=list(m.objets[autre]['position']))
    c = {'objet': 'vivres', 'remettre': autre}
    agendas.prendre(m, auteur, {'condition': c, 'pour': autre, 'minute': m.data['minutes']})
    lire(m, auteur)['besoins']['biens'] = 85
    d.choisir(m, auteur, m.data['minutes'])
    return recharger(m), auteur, autre, contenant, garde


class RestaurationChargesTests(unittest.TestCase):
    def verifier_rendus(self, m):
        n = recharger(m)
        self.assertEqual(m.data, n.data)
        self.assertEqual(regarder(m), regarder(n))
        from donjon.scene import scene_percue
        self.assertEqual(scene_percue(m), scene_percue(n))

    def verifier_livraison(self, scenario, poste=False):
        m, auteur, autre, contenant, garde = livraison(scenario, poste)
        self.assertIn(garde, agendas.charges_suspendues(m, auteur)['conditions'])
        bloc, _ = vivre(recharger(m), 6)
        decoupe = recharger(m)
        for _ in range(12):
            decoupe = avancer_precis(decoupe, 300)
        self.assertEqual(bloc.data, decoupe.data)
        self.verifier_rendus(bloc)
        self.assertEqual(bloc.objets['vivres']['lieu'], autre)
        self.assertTrue(bloc.objets[contenant]['verrouillee'])
        self.assertFalse(bloc.objets[contenant]['ouverte'])
        gestes = [x['texte'] for x in bloc.data['chronique'] if x['pnj'] == auteur]
        remise = next(n for n, t in enumerate(gestes) if ' remet ' in t)
        self.assertEqual(sum(' déverrouille ' in t for t in gestes), 1)
        self.assertFalse(any(' verrouille ' in t for t in gestes[:remise]))
        self.assertTrue(any(' verrouille ' in t for t in gestes[remise:]))
        if poste:
            self.assertEqual(bloc.objets[auteur]['lieu'], m.objets[auteur]['lieu'])
        bloc.joueur.update(salle=bloc.objets[contenant]['lieu'],
                           position=list(bloc.objets[contenant]['position']))
        self.assertIn('verrouillé', decrire(recharger(bloc), contenant))

    def test_gorm_livre_et_restaure_apres_recharge(self):
        self.verifier_livraison('relais')

    def test_mathe_autre_contenant_et_scenario(self):
        self.verifier_livraison('mine')

    def test_part_promise_reste_due_meme_sans_faim_du_beneficiaire(self):
        for scenario in ('relais', 'mine'):
            with self.subTest(scenario=scenario):
                m, auteur, autre, contenant, _ = livraison(scenario)
                for a in agendas.en_cours(m, auteur):
                    agendas.retirer_proposition(m, auteur, a)
                lire(m, auteur)['intention'] = None
                c = {'objet': 'vivres', 'servir': autre}
                agendas.prendre(m, auteur, {'condition': c, 'pour': autre, 'minute': m.data['minutes']})
                self.assertTrue(d.satisfaite(m, auteur, c))
                portions = m.objets['vivres']['portions']
                d.choisir(m, auteur, m.data['minutes'])
                bloc, _ = vivre(recharger(m), 5)
                m = recharger(m)
                for _ in range(5):
                    m, _ = vivre(m, 1)
                self.assertEqual(bloc.data, m.data)
                self.assertEqual(m.objets['vivres']['portions'], portions - 1)
                self.assertEqual(agendas.en_cours(m, auteur), [])
                self.assertTrue(m.objets[contenant]['verrouillee'])
                gestes = [x['texte'] for x in m.data['chronique'] if x['pnj'] == auteur]
                service = next(n for n, t in enumerate(gestes) if 'donne une part' in t)
                self.assertFalse(any(' verrouille ' in t for t in gestes[:service]))
                self.assertEqual(sum(' déverrouille ' in t for t in gestes), 1)
                self.verifier_rendus(m)

    def test_livraison_distante_et_retour_au_poste(self):
        self.verifier_livraison('relais', poste=True)

    def test_reconstruction_forcee_perte_du_suffixe_et_abandon(self):
        m, auteur, autre, contenant, garde = livraison()
        # Précondition réellement exécutée, puis moyens invalidés. La charge
        # reste portée même si aucune fermeture ne figure dans le préfixe.
        m = avancer_precis(m, 120)
        self.assertFalse(m.objets[contenant]['verrouillee'])
        i = lire(m, auteur)['intention']
        i['plan'] = [p._etape('prendre', 'vivres')]
        lire(m, auteur)['manque'] = {'minute': m.data['minutes'],
            'etape': {k: i['plan'][0][k] for k in ('operation', 'cible', 'outil', 'lieu')}}
        m = recharger(m)
        d.choisir(m, auteur, m.data['minutes'])
        self.assertEqual(lire(m, auteur)['intention']['but'].get('remettre'), autre)
        self.assertIn(garde, agendas.charges_suspendues(m, auteur)['conditions'])
        self.assertTrue(d.retabli_par_son_plan(m, auteur, garde))
        self.verifier_rendus(m)
        termine, _ = vivre(recharger(m), 5)
        self.assertEqual(termine.objets['vivres']['lieu'], autre)
        self.assertTrue(termine.objets[contenant]['verrouillee'])
        self.verifier_rendus(termine)
        # Un abandon effectif libère la garde, sans contrat orphelin.
        lire(m, auteur)['intention'] = None
        for a in agendas.en_cours(m, auteur):
            agendas.retirer_proposition(m, auteur, a)
        self.assertFalse(d.retabli_par_son_plan(m, auteur, garde))
        m, _ = vivre(recharger(m), 2)
        self.assertTrue(m.objets[contenant]['verrouillee'])
        self.verifier_rendus(m)

    def test_suffixe_perdu_sans_abandon_la_restauration_est_recalculee(self):
        m, auteur, autre, contenant, _ = livraison()
        m = avancer_precis(m, 120)
        i = lire(m, auteur)['intention']
        i['plan'] = [g for g in i['plan'] if g['operation'] not in ('fermer', 'verrouiller')]
        self.assertTrue(i['charges_suspendues'])
        m = recharger(m)
        bloc, _ = vivre(recharger(m), 5)
        for _ in range(5):
            m, _ = vivre(m, 1)
        self.assertEqual(m.data, bloc.data)
        self.assertEqual(m.objets['vivres']['lieu'], autre)
        self.assertTrue(m.objets[contenant]['verrouillee'])
        self.verifier_rendus(m)

    def test_porte_ouverte_par_le_passage_et_retour_physique(self):
        m, auteur, autre, _, _ = livraison()
        garde = {'objet': 'porte', 'verrouillee': True}
        m.objets[auteur]['profil']['pulsions'] = [{'besoin': 'biens', 'condition': garde}]
        lire(m, auteur)['pulsions'] = []
        lire(m, auteur)['intention'] = None
        placer(m, auteur, 'crypte', [7, 3])
        placer(m, autre, 'beffroi', [2, 3])
        m.objets['vivres']['lieu'] = auteur
        cle = next(k for k, o in m.objets.items() if 'porte' in o.get('ouvre', ()))
        m.objets[cle]['lieu'] = auteur
        percevoir_tous(m)
        croire(m, auteur, 'porte', 'verrouillee', True, 'essai')
        croire(m, auteur, 'porte', 'etat', {'ouverte': False}, 'essai')
        croire(m, auteur, autre, 'lieu', 'beffroi', 'savoir', salle='beffroi', case=[2, 3])
        d.choisir(m, auteur, m.data['minutes'])
        self.assertIn(garde, agendas.charges_suspendues(m, auteur)['conditions'])
        m = recharger(m)
        bloc, _ = vivre(recharger(m), 6)
        for _ in range(6):
            m, _ = vivre(m, 1)
        self.assertEqual(m.data, bloc.data)
        self.assertEqual(m.objets['vivres']['lieu'], autre)
        self.assertTrue(m.objets['porte']['verrouillee'])
        self.assertFalse(m.objets['porte']['ouverte'])
        self.verifier_rendus(m)

    def test_reconstruction_forcee_pendant_la_restauration(self):
        m, auteur, autre, contenant, _ = livraison()
        # Perte du suffixe pour exercer la phase de restauration indépendante.
        i = lire(m, auteur)['intention']
        i['plan'] = [g for g in i['plan'] if g['operation'] not in ('fermer', 'verrouiller')]
        captures = []
        choisir = d.choisir
        def observer(monde, qui, minute):
            resultat = choisir(monde, qui, minute)
            if qui == auteur and agendas.charges_suspendues(monde, qui).get('restaurer'):
                captures.append(copy.deepcopy(monde.data))
            return resultat
        with patch.object(d, 'choisir', observer):
            vivre(m, 5)
        self.assertTrue(captures)
        m = recharger(Monde(captures[0]))
        # Cette phase passe par le même juge de tête que tous les candidats,
        # même quand la recherche a trouvé des moyens de fermer.
        from donjon import pnj
        refuse = recharger(m)
        valider = pnj.refus_etape
        def fermeture_refusee(monde, qui, plan):
            if qui == auteur and plan and plan[0]['operation'] in ('fermer', 'verrouiller'):
                return {'cause': 'test_de_revalidation_commune'}
            return valider(monde, qui, plan)
        with patch.object(pnj, 'refus_etape', fermeture_refusee):
            d.choisir(refuse, auteur, refuse.data['minutes'])
        intention = lire(refuse, auteur)['intention']
        self.assertFalse(intention and intention['plan'] and intention['plan'][0]['operation'] in ('fermer', 'verrouiller'))
        self.verifier_rendus(refuse)
        i = lire(m, auteur)['intention']
        lire(m, auteur)['manque'] = {'minute': m.data['minutes'],
            'etape': {k: i['plan'][0][k] for k in ('operation', 'cible', 'outil', 'lieu')}}
        d.choisir(m, auteur, m.data['minutes'])
        self.assertTrue(agendas.charges_suspendues(m, auteur)['restaurer'])
        m, _ = vivre(recharger(m), 3)
        self.assertEqual(m.objets['vivres']['lieu'], autre)
        self.assertTrue(m.objets[contenant]['verrouillee'])
        self.verifier_rendus(m)

    def test_plan_coupe_n_execute_pas_la_remise_dependante(self):
        m, auteur, autre, _, _ = livraison()
        e = p.depart(m, auteur)
        futur = p._etape('prendre', 'vivres')
        futur['attendre_remise'] = True
        recherche = (1, [p._etape('demander', autre, outil='vivres'), futur],
                     e.apres(portes=e.portes | {'vivres'}))
        with patch.object(p, 'chercher', return_value=recherche), patch.object(
                p, '_mesurer', return_value=(1, 0, recherche[2])):
            devis = p._devis_remise(m, auteur, 'vivres', {'objet': 'vivres', 'remettre': autre}, autre)
        self.assertEqual([g['operation'] for g in devis[2]], ['demander'])

    def test_schema_refuse_charge_invalide_et_ancienne_partie_reste_lisible(self):
        m, auteur, *_ = livraison()
        self.verifier_rendus(m)
        faux = copy.deepcopy(m.data)
        faux['esprits'][auteur]['intention']['charges_suspendues']['restaurer'] = 'oui'
        with self.assertRaisesRegex(ErreurMonde, 'Charges suspendues'):
            Monde(faux)
        faux = copy.deepcopy(m.data)
        faux['esprits'][auteur]['intention']['charges_suspendues'] = None
        with self.assertRaisesRegex(ErreurMonde, 'Charges suspendues'):
            Monde(faux)
        del lire(m, auteur)['intention']['charges_suspendues']
        self.verifier_rendus(m)

    def test_capture_historique_rejouee_bloc_et_decoupe(self):
        source = Path(__file__).parent / 'data/charges-218-hameau-1985.json.gz'
        m = Monde(json.loads(gzip.decompress(source.read_bytes())))
        bloc, _ = vivre(recharger(m), 10)
        decoupe = recharger(m)
        for _ in range(10):
            decoupe, _ = vivre(decoupe, 1)
        self.assertEqual(bloc.data, decoupe.data)
        self.verifier_rendus(bloc)


if __name__ == '__main__':
    unittest.main()
