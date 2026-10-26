"""Demandes utiles et marchés plausibles, état et parole relus après sauvegarde."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import relations
from donjon.echanges import anticiper_valeur, executer, offre_sensee, proposer, valeur_proposition
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj_propositions import recours, _contreparties
from donjon.propositions import demande_utile, demande_financee, en_mots
from donjon.rendu import regarder as rendu_regarder
from tests.test_tensions import recharger, placer
from tests.support import calme, presentes, regarder


class ContrepartiesTests(unittest.TestCase):
    def capture(self):
        with gzip.open(Path(__file__).parent / 'data/contreparties-mine1985-253.json.gz', 'rt', encoding='utf8') as f:
            return recharger(Monde(json.load(f)))

    def test_capture_mine_253_plan_ancien_et_nouveau_recours(self):
        m = self.capture()
        self.assertEqual(m.data['minutes'], 253)
        ancien = copy.deepcopy(lire(m, 'odon')['intention']['plan'][0])
        self.assertEqual(ancien['contenu']['demande'], {'type':'objet','objet':'paie'})
        avant = copy.deepcopy(m.data)
        lignes = []
        self.assertFalse(executer(m, 'odon', ancien, lignes))
        self.assertEqual(m.data, avant)
        self.assertEqual(lignes, [])
        demande = demande_utile(m, 'odon', ancien['contenu']['demande'])
        self.assertEqual(demande, {'type':'pieces','objet':'paie','montant':45})
        self.assertEqual(demande_utile(m, 'odon', {'type':'pieces','montant':200}),
                         {'type':'pieces','montant':45})
        self.assertIsNone(demande_utile(m, 'bram', {'type':'pieces','montant':200}))
        etapes = [{'operation':'prendre','cible':'paie','outil':'','lieu':'','condition':'sans_temoin'}]
        nouveau = recours(m, 'odon', 'argent', etapes)
        if nouveau:
            self.assertLessEqual(nouveau['contenu']['demande']['montant'], 1)
        # Revalidation dans un véritable tour moteur, même si le plan sauvegardé était ancien.
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition('attendre')))
        m = recharger(m)
        self.assertEqual(m.objets['paie']['proprietaire'], 'bram')
        self.assertEqual(m.objets['paie']['pieces'], 200)
        self.assertFalse(any(s['type']=='proposition' and s['minute']>=253
            and s['demande']==ancien['contenu']['demande'] for s in lire(m,'odon')['memoire']))
        self.assertNotIn('contre la bourse de la paie', ' '.join(m.data['journal'][-1]['faits']))
        self.assertNotIn('contre la bourse de la paie', rendu_regarder(m))

    def auberge(self):
        from donjon.auberge import nouveau_auberge
        from donjon.spatial import installer
        m = presentes(nouveau_auberge(depart='fixe'))
        installer(m)
        calme(m, *(i for i,o in m.objets.items() if o.get('profil')))
        placer(m,'lucien','salle_commune',[3,3])
        placer(m,'anselme','salle_commune',[3,4])
        m.joueur.update(salle='salle_commune',position=[4,3],orientation='ouest')
        regarder(m,'lucien','anselme')
        regarder(m,'anselme','lucien')
        m.objets['ballot'].update(lieu='anselme',proprietaire='anselme',prix=200)
        m.objets['crochets_lucien'].update(lieu='lucien',proprietaire='lucien',prix=1)
        m.data['finances_pnj']['lucien']=0
        percevoir_tous(m)
        lire(m,'lucien')['intention']={'but':{'type':'argent','objet':'ballot'},'motif':'argent','plan':[],'depuis':0,'attente':0}
        return recharger(m)

    def test_auberge_bien_indivisible_trop_cher_pas_offert_ni_affiche(self):
        m=self.auberge()
        demande={'type':'objet','objet':'ballot'}
        terme={'type':'objet','objet':'crochets_lucien'}
        self.assertFalse(offre_sensee(m,'lucien','anselme',demande,terme))
        self.assertGreater(anticiper_valeur(m,'lucien','anselme',demande,terme)['dd_base'],20)
        lignes=[]
        geste={'operation':'proposer','cible':'anselme','outil':'ballot','lieu':'','condition':'','contenu':{'demande':demande,'contrepartie':terme}}
        self.assertFalse(executer(m,'lucien',geste,lignes))
        moteur=Moteur(m)
        moteur.executer(moteur.preparer(proposition('attendre')))
        m=recharger(m)
        self.assertEqual(m.objets['ballot']['proprietaire'],'anselme')
        self.assertEqual(m.objets['crochets_lucien']['proprietaire'],'lucien')
        self.assertFalse(any(s['type']=='proposition' and s['demande']==demande for s in lire(m,'lucien')['memoire']))
        self.assertEqual(lignes,[])
        self.assertNotIn('contre '+en_mots(m,demande),' '.join(m.data['journal'][-1]['faits']))
        self.assertNotIn('contre '+en_mots(m,demande),rendu_regarder(m))

    def test_somme_utile_financee_livree_sans_ceder_la_bourse(self):
        m=self.auberge()
        m.objets['bourse_anselme'].update(lieu='anselme',pieces=200)
        croire(m,'lucien','bourse_anselme','pieces',200,'savoir')
        m.objets['crochets_lucien']['prix']=5
        m.objets['anselme']['profil']['pulsions']=[]
        lire(m,'anselme')['pulsions']=[]
        lire(m,'anselme')['relations']['lucien']=relations._nouvelle({'confiance':70})
        lire(m,'lucien')['relations']['anselme']=relations._nouvelle({'confiance':70})
        m.data['connus'].extend(['bourse_anselme','crochets_lucien'])
        percevoir_tous(m)
        m=recharger(m)
        demande=demande_utile(m,'lucien',{'type':'objet','objet':'bourse_anselme'})
        terme={'type':'objet','objet':'crochets_lucien'}
        demande=demande_financee(m,'lucien',demande,terme)
        self.assertLessEqual(demande['montant'],5)
        self.assertTrue(offre_sensee(m,'lucien','anselme',demande,terme))
        avant=m.data['finances_pnj']['anselme']
        lignes=[]
        geste={'operation':'proposer','cible':'anselme','outil':'bourse_anselme','lieu':'','condition':'','contenu':{'demande':demande,'contrepartie':terme}}
        with patch.object(Monde,'d20',return_value=20):
            self.assertTrue(executer(m,'lucien',geste,lignes))
        m=recharger(m)
        self.assertEqual(m.objets['bourse_anselme']['pieces'],200-demande['montant'])
        self.assertEqual(m.objets['bourse_anselme']['proprietaire'],'anselme')
        self.assertEqual(m.data['finances_pnj']['anselme'],avant)
        self.assertEqual(m.data['finances_pnj']['lucien'],demande['montant'])
        self.assertEqual(m.objets['crochets_lucien']['proprietaire'],'anselme')
        self.assertIn(en_mots(m,demande),' '.join(lignes))
        self.assertIn('accepte',' '.join(lignes))
        self.assertTrue(any(en_mots(m,demande) in b.get('texte','') for b in m.data['bruits']))
        self.assertTrue(any(s['type']=='proposition' and s['demande']==demande for s in lire(m,'lucien')['memoire']))

    def test_audit_terme_partiel_et_formes_invalides(self):
        from donjon.narration import compte_bien_forme
        from donjon.propositions import erreur_terme, offre
        valide = {"type": "pieces", "montant": 3, "objet": "bourse_anselme"}
        self.assertIsNone(erreur_terme(valide))
        self.assertTrue(compte_bien_forme(offre("anselme", "lucien", valide, {"type": "rien"})))
        for invalide in ({**valide, "montant": 0}, {**valide, "montant": True},
                         {**valide, "objet": 7}, {**valide, "en_plus": 1},
                         {"type": "tache", "condition": {"objet": "brasero", "allume": False}}):
            with self.subTest(invalide=invalide):
                self.assertIsNotNone(erreur_terme(invalide))
                self.assertFalse(compte_bien_forme(offre("anselme", "lucien", invalide, {"type": "rien"})))

    def test_estimation_sans_lecture_de_situation_ou_argent_prives(self):
        m=self.auberge()
        demande={'type':'objet','objet':'ballot'}
        terme={'type':'objet','objet':'crochets_lucien'}
        avant=copy.deepcopy(m.data)
        attendu=anticiper_valeur(m,'lucien','anselme',demande,terme)
        self.assertEqual(m.data,avant)
        m.objets['anselme']['profil']['situation']={'dette':10000}
        m.objets['anselme']['profil']['caracteristiques']['INT']=1
        m.data['finances_pnj']['anselme']=10000
        m.objets['bourse_anselme'].update(lieu='anselme',pieces=10000)
        self.assertEqual(anticiper_valeur(m,'lucien','anselme',demande,terme),attendu)

    def test_contenant_valorise_pieces_connues_et_quantite_inconnue_non_devinee(self):
        m=self.capture()
        valeur=valeur_proposition(m,'odon',{'type':'objet','objet':'paie'},'bram')
        m.objets['paie']['pieces']=9999
        self.assertEqual(valeur_proposition(m,'odon',{'type':'objet','objet':'paie'},'bram'),valeur)
        lire(m,'odon')['croyances']['paie'].pop('pieces')
        self.assertIsNone(demande_utile(m,'odon',{'type':'objet','objet':'paie'}))

if __name__=='__main__':unittest.main()
