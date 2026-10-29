"""Un foyer fixe peut être allumé par le porteur d'une flamme, après accord et travail réels."""
import unittest
import gzip
import json
from pathlib import Path
from unittest.mock import patch

from donjon import deliberation as d, echanges, planification as p
from donjon.banc_pnj import creer
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.rendu import regarder as rendu
from donjon.scene import scene_percue
from tests.support import calme, presentes, sans_souci
from tests.test_avis_menace import relation
from tests.test_tensions import placer, recharger, vivre


def scene(foyer='brasero'):
    m = presentes(creer('crue_hameau', 1985, 'fixe'))
    acteurs = [k for k, o in m.objets.items() if o.get('profil')]
    calme(m, *acteurs)
    sans_souci(m)
    # La scène isole le besoin de chaleur : attendre ailleurs dans le noir
    # ne constitue pas un autre problème à résoudre pendant le service.
    for salle in m.data['salles'].values():
        salle['lumiere_naturelle']=2
    m.data['gestes_en_cours'] = []
    for k in acteurs:
        m.objets[k]['profil']['pulsions'] = []
        lire(m,k).update(pulsions=[], intention=None, veille=None)
    # Un seul foyer et une seule flamme utilisables : la torche de Maël
    # laissée à disposition de Gorm dans cette scène d'auteur.
    for k,o in m.objets.items():
        if 'allume' in o:
            o.update(allume=False, combustible=0)
            if o.get('foyer') and k != foyer:
                o.pop('foyer')
        if 'allumage' in o.get('usages', ()):
            o['lieu'] = 'joueur'
    m.objets[foyer].update(allume=False, combustible=100)
    m.objets['torche'].update(lieu='marchand', allume=True, combustible=100, proprietaire='mael')
    m.data.setdefault('permissions',[]).append(
        {'objet':'torche','a':'marchand','de':'mael','minute':m.data['minutes']})
    m.objets['bois_guet'].update(lieu='marchand', charges=8)
    placer(m,'aubin','antichambre',(2,4))
    placer(m,'marchand','antichambre',(3,4))
    m.joueur.update(salle='antichambre', position=[2,3], orientation='sud')
    m.data['connus']=sorted(set(m.data['connus']) | {foyer})
    relation(m, 'marchand', 'aubin', confiance=100, affection=100)
    relation(m, 'aubin', 'marchand', confiance=100, affection=100)
    lire(m,'aubin')['besoins']['chaleur'] = 100.
    percevoir_tous(m)
    for qui in ('aubin','marchand'):
        for k,o in m.objets.items():
            if 'allume' in o:
                croire(m,qui,k,'etat',{'allume':o['allume'],'charge':o['combustible']>0,'faible':False},'vu')
        croire(m,qui,'torche','lieu','marchand','vu',salle=None,case=None)
        croire(m,qui,'bois_guet','lieu','marchand','vu',salle=None,case=None)
    # Aubin connaît la flamme, pas les réserves privées de son porteur : la
    # demande d'une part de bois n'est pas une autre tâche déjà disponible.
    for k,o in m.objets.items():
        if 'combustible' in o.get('usages', ()):
            lire(m,'aubin')['croyances'].pop(k,None)
    return recharger(m)


class AllumerPourSoiTests(unittest.TestCase):
    def recharge(self,m):
        n=recharger(m)
        self.assertEqual(m.data,n.data)
        self.assertEqual(rendu(m),rendu(n))
        self.assertEqual(scene_percue(m),scene_percue(n))
        return n

    def offres(self,m,foyer='brasero'):
        v=p.vue(m,'aubin'); e=p.depart(m,'aubin',v)
        return list(p._allumer_pour_soi(v,e,foyer))

    def test_capture_269_catalogue_ouvre_mais_devis_gorm_impossible(self):
        source=Path(__file__).parent/'data/allumer-277-aubin-615.json.gz'
        m=self.recharge(Monde(json.loads(gzip.decompress(source.read_bytes()))))
        v=p.vue(m,'aubin'); e=p.depart(m,'aubin',v)
        self.assertEqual(v.flammes_d_autrui(e),[('marchand','torche')])
        self.assertFalse(v.poste_garde)
        # Le besoin peut recharger d'abord ; la tâche doit alors exister au catalogue.
        e=e.apres(faits=[(('charge','brasero'),True)])
        demandes=list(p._allumer_pour_soi(v,e,'brasero'))
        self.assertTrue(any(g[2][0]['operation']=='confier' and g[2][0]['cible']=='marchand'
                            for g in demandes))
        condition={'objet':'brasero','allume':True}
        self.assertTrue(d.condition_valide(m,condition))
        self.assertIsNone(echanges._devis_proposition(m,'marchand',condition,'aubin'))
        demande=next(g[2][0] for g in demandes if g[2][0]['operation']=='confier'
                     and g[2][0]['cible']=='marchand')
        self.assertFalse(echanges.executer(m,'aubin',demande,[]))
        self.assertFalse(m.objets['brasero']['allume'])
        m=self.recharge(m)
        v=p.vue(m,'aubin'); e=p.depart(m,'aubin',v).apres(faits=[(('charge','brasero'),True)])
        self.assertFalse(any(g[2][0]['operation']=='confier' and g[2][0]['cible']=='marchand'
                             for g in p._allumer_pour_soi(v,e,'brasero')))

    def test_demande_travail_reel_chaleur_et_decoupage_deux_foyers(self):
        for foyer in ('brasero','poele_guet'):
            with self.subTest(foyer=foyer), patch.object(Monde,'d20',return_value=20):
                m=scene(foyer)
                plan=p.planifier(m,'aubin','chaleur')
                self.assertIsNotNone(plan)
                self.assertEqual(plan[1][-1]['operation'],'confier')
                self.assertEqual(plan[1][-1]['contenu'],{'objet':foyer,'allume':True})
                self.assertTrue(echanges.executer(m,'aubin',plan[1][-1],[]))
                self.assertFalse(m.objets[foyer]['allume'])
                self.assertEqual(m.objets['marchand']['lieu'],'antichambre')
                m=self.recharge(m)
                self.assertEqual(p.planifier(m,'aubin','chaleur')[1],[])
                bloc,_=vivre(self.recharge(m),8,jet=20)
                pas=self.recharge(m)
                for _ in range(8):
                    pas,_=vivre(pas,1,jet=20)
                    pas=self.recharge(pas)
                self.assertEqual(bloc.data,pas.data)
                self.assertEqual(rendu(bloc),rendu(pas))
                self.assertTrue(bloc.objets[foyer]['allume'])
                self.assertLess(lire(bloc,'aubin')['besoins']['chaleur'],100)
                self.assertTrue(any(c['pnj']=='marchand' and 'allume' in c['texte'] for c in bloc.data['chronique']))
                self.recharge(bloc)

    def test_pas_de_flamme_crue_pas_de_charge_ni_demande_sous_eau(self):
        m=scene()
        self.assertTrue(self.offres(m))
        croire(m,'aubin','torche','etat',{'allume':False,'charge':True,'faible':False},'vu')
        self.assertEqual(self.offres(self.recharge(m)),[])
        m=scene()
        croire(m,'aubin','brasero','etat',{'allume':False,'charge':False,'faible':False},'vu')
        self.assertEqual(self.offres(self.recharge(m)),[])
        m=scene()
        croire(m,'aubin','echoppe','eau',100,'vu')
        m=self.recharge(m)
        self.assertEqual(self.offres(m),[])
        self.assertIsNone(p.planifier(m,'aubin','chaleur'))

    def test_refus_retenu_sans_redemande_par_delai_et_offre_payee(self):
        m=scene()
        self.assertTrue(any(g[2][0]['operation']=='engager' for g in self.offres(m)))
        from donjon.deliberation import retenir_refus
        retenir_refus(m,'aubin','marchand','confier','impossible',objet='brasero',tache='allume')
        for dt in (0,1,60):
            m.data['minutes']+=dt
            m=self.recharge(m)
            self.assertFalse(any(g[2][0]['operation']=='confier' for g in self.offres(m)))

    def test_position_reelle_cachee_ne_change_pas_le_catalogue(self):
        m=scene(); avant=self.offres(m)
        placer(m,'marchand','crypte',(2,3))
        self.assertEqual(avant,self.offres(m))

    def test_accord_paye_apres_refus_gratuit_attend_le_travail(self):
        m=scene()
        from donjon.deliberation import retenir_refus
        retenir_refus(m,'aubin','marchand','confier','refus',objet='brasero',tache='allume')
        m.data['finances_pnj']['aubin']=100
        offre=next(g[2][0] for g in self.offres(m) if g[2][0]['operation']=='engager')
        offre['contenu']['prix']=20
        self.assertTrue(echanges.executer(m,'aubin',offre,[]))
        self.assertFalse(m.objets['brasero']['allume'])
        m=self.recharge(m)
        self.assertEqual(p.planifier(m,'aubin','chaleur')[1],[])
        m,_=vivre(m,8,jet=20)
        self.assertTrue(m.objets['brasero']['allume'])
        self.assertLess(lire(m,'aubin')['besoins']['chaleur'],100)
        self.recharge(m)

    def test_parole_du_joueur_utilise_le_meme_service(self):
        from donjon.paroles import preparer_parole
        from tests.test_parts_achetees import parole
        m=scene()
        m.joueur.update(position=[3,5],orientation='nord')
        texte="Gorm, peux-tu allumer le brasero pour moi ?"
        contenu=parole('marchand',texte,'demande','brasero','allumer')
        contenu['contenu']=[{'type':'proposition',
                             'demande':{'type':'tache','condition':{'objet':'brasero','allume':True}},
                             'contrepartie':{'type':'rien'}}]
        with patch.object(Monde,'d20',return_value=20):
            m,rapport=preparer_parole(m,contenu)
        self.assertTrue(any(x['condition']=={'objet':'brasero','allume':True}
                            and x['pour']=='joueur' for x in lire(m,'marchand')['engagements']),rapport)
        self.assertFalse(m.objets['brasero']['allume'])
        m=self.recharge(m)
        m,_=vivre(m,8,jet=20)
        self.assertTrue(m.objets['brasero']['allume'])
        self.recharge(m)

    def test_devis_impossible_sans_combustible_refus_reel_recharge(self):
        m=scene()
        m.objets['brasero']['combustible']=0
        for o in m.objets.values():
            if 'combustible' in o.get('usages', ()):
                o['charges']=0
        percevoir_tous(m)
        for qui in ('aubin','marchand'):
            croire(m,qui,'brasero','etat',{'allume':False,'charge':False,'faible':False},'vu')
            for k,o in m.objets.items():
                if 'combustible' in o.get('usages', ()):
                    croire(m,qui,k,'etat',{'disponible':False},'vu')
        m=self.recharge(m)
        self.assertEqual(self.offres(m),[])
        self.assertIsNone(p.planifier(m,'aubin','chaleur'))
        demande=p._etape('confier','marchand',contenu={'objet':'brasero','allume':True})
        self.assertFalse(echanges.executer(m,'aubin',demande,[]))
        self.assertFalse(m.objets['brasero']['allume'])
        for dt in (0,60):
            m.data['minutes']+=dt
            m=self.recharge(m)
            self.assertFalse(any(g[2][0]['operation']=='confier' for g in self.offres(m)))

