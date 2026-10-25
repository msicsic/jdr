"""Les noms sont entendus, les corps reconnus : chaîne moteur/rendus/sauvegarde."""
import json
import unittest
from pathlib import Path
import tempfile

from donjon.banc_pnj import creer
from donjon.carte import carte
from donjon.dialogues import interlocuteurs
from donjon.esprits import lire, percevoir_tous
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur
from donjon.commandes import analyser
from donjon.narration import voix_inconnues
from donjon.paroles import preparer_parole, identites
from donjon.rendu import regarder, decrire
from donjon.scene import scene_percue
from donjon.social import faire_entendre
from donjon.voix import connaitre, connait_nom, designation, nom_pour_joueur
from tests.support import calme
from tests.test_tensions import placer


def recharge(m):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'partie.json'
        m.sauver(p)
        return Monde.charger(p)


def relais():
    m=creer('relais',1985,'fixe')
    calme(m,'marchand','aubin','brune','ilse')
    m.joueur.update(salle='echoppe',position=[1,2],orientation='nord')
    placer(m,'marchand','echoppe',[1,1])
    m.objets['marchand']['orientation']='sud'
    return recharge(m)


def dire(m, texte, contenu=()):
    return preparer_parole(m, {'personnage':designation(m,'marchand'),'replique':texte,
        'contenu':list(contenu),'_intention':"je dis à l'homme trapu : "+texte})


class NomsTests(unittest.TestCase):
    def rendus(self,m):
        return '\n'.join([regarder(m),carte(m),json.dumps(scene_percue(m),ensure_ascii=False)])

    def test_cas_reel_voir_gorm_puis_l_entendre_se_nommer(self):
        m=relais()
        m.actualiser_souvenirs_personnages()
        m=recharge(m)
        self.assertTrue(m.visible('marchand'))
        self.assertNotIn('marchand',identites(m))
        self.assertEqual(designation(m,'marchand'),'personne_4')
        self.assertEqual(nom_pour_joueur(m,'marchand'),"l'homme trapu")
        self.assertNotIn('Gorm',self.rendus(m))
        self.assertNotIn('Gorm',json.dumps(m.contexte(),ensure_ascii=False))
        self.assertEqual(m.trouver("l'homme trapu"),'marchand')
        with self.assertRaises(ErreurMonde): m.trouver('Gorm')
        # La question devient une parole du moteur, qui enregistre le nom avant son affichage.
        m,rapport=dire(m,"Comment t'appelles-tu ?",[{'type':'qui','sujet':'','attribut':'','valeur':''}])
        self.assertIn('Gorm',' '.join(rapport['faits']))
        m=recharge(m)
        self.assertTrue(connait_nom(m,'joueur','marchand'))
        self.assertIn('Gorm',self.rendus(m))
        self.assertIn('marchand',identites(m))

    def test_une_voix_connue_ne_donne_aucun_nom(self):
        m=relais()
        connaitre(m,'joueur','marchand')
        m=recharge(m)
        self.assertIn('marchand',m.data['voix_connues'])
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertNotIn('Gorm',self.rendus(m))

    def test_une_voix_reconnue_jamais_vue_ne_revele_aucun_portrait(self):
        m=relais()
        placer(m,'marchand','echoppe',[4,3])
        m.objets['marchand']['portrait']='Un homme au manteau chartreuse.'
        m.data['personnes']['marchand']['nom']="l'homme au manteau chartreuse"
        m.data['entendus']=['marchand']
        m.data['personnages_vus']=[i for i in m.data.get('personnages_vus',[]) if i!='marchand']
        m.data['souvenirs_personnages'].pop('marchand',None)
        connaitre(m,'joueur','marchand')
        m=recharge(m)
        self.assertFalse(m.visible('marchand'))
        self.assertTrue(designation(m,'marchand').startswith('voix_'))
        self.assertEqual(nom_pour_joueur(m,'marchand'),'une voix reconnue')
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertNotIn('chartreuse',json.dumps(m.contexte(),ensure_ascii=False))
        from donjon.noms import public
        rendu=public(m,{'personne':'marchand','description':'Gorm est ici.'})
        self.assertTrue(rendu['personne'].startswith('voix_reconnue_'))
        self.assertNotIn('chartreuse',json.dumps(rendu))
        self.assertNotIn('Gorm',json.dumps(rendu))
        self.assertNotIn('Gorm',self.rendus(m))

    def test_tout_corps_jamais_vu_reste_sans_apparence_meme_dans_un_texte(self):
        from donjon.noms import nom,texte
        from donjon.voix import retenir
        for voix_ in ('absente','entendue','reconnue'):
            with self.subTest(voix=voix_):
                m=relais()
                placer(m,'marchand','crypte',[2,3])
                m.objets['marchand']['portrait']='Un homme au manteau chartreuse.'
                m.data['personnes']['marchand']['nom']="l'homme au manteau chartreuse"
                m.data['personnages_vus']=[]
                m.data['souvenirs_personnages'].pop('marchand',None)
                if voix_!='absente': retenir(m,'joueur','marchand')
                if voix_=='reconnue': connaitre(m,'joueur','marchand')
                m=recharge(m)
                self.assertFalse(m.visible('marchand'))
                self.assertEqual(nom(m,'marchand'),'une personne inconnue')
                self.assertNotIn('chartreuse',texte(m,'Gorm est là.'))
                self.assertNotIn('Gorm',nom_pour_joueur(m,'marchand'))
                self.assertNotIn('chartreuse',self.rendus(m)+json.dumps(m.contexte()))

    def test_une_designation_ne_change_pas_le_regard_memorise(self):
        from donjon import spatial
        from donjon.voix import identifie
        from unittest.mock import patch
        m=relais()
        placer(m,'aubin','echoppe',[1,3])  # Derrière Corvus, qui regarde au nord.
        m=recharge(m)
        avant=json.dumps(m.data,sort_keys=True)
        vus={i:m.visible(i) for i in m.objets}
        rendus=self.rendus(m)
        with patch.object(spatial,'VERIFICATION',1), spatial.vue_memorisee(m), spatial.etat_fige(m):
            self.assertFalse(m.visible('aubin'))
            self.assertTrue(identifie(m,'joueur','aubin'))
            self.assertFalse(m.visible('aubin'))
        self.assertEqual(avant,json.dumps(m.data,sort_keys=True))
        m=recharge(m)
        self.assertEqual(vus,{i:m.visible(i) for i in m.objets})
        self.assertEqual(rendus,self.rendus(m))

    def test_une_croyance_rapportee_descriptive_ne_donne_aucun_nom(self):
        from unittest.mock import patch
        m=creer('auberge',1985,'fixe')
        calme(m,'joss')
        m.joueur.update(salle='cuisine',position=[1,2],orientation='nord')
        placer(m,'joss','cuisine',[1,1])
        m.objets['joss']['orientation']='sud'
        # La parole effectivement saisie décrit le locuteur sans donner son nom.
        mots='Tu peux me faire confiance.'
        with patch.object(Monde,'d20',return_value=20):
            m,_=preparer_parole(m,{'personnage':designation(m,'joss'),'replique':mots,
                'contenu':[{'type':'affirmation','sujet':'joueur','attribut':'fiable','valeur':'oui'}],
                '_intention':f'je dis à {nom_pour_joueur(m,"joss")} : '+mots})
        m=recharge(m)
        # L'avis reçu (relations graduées) garde sa source : la voix de Corvus, vue parler.
        self.assertTrue(any(s['type']=='avis_recu' and s['sujet']=='joueur' and s['source']=='dit:joueur'
                            for s in lire(m,'joss')['memoire']))
        self.assertFalse(connait_nom(m,'joss','joueur'))
        self.assertTrue(voix_inconnues(m,[{'locuteur':designation(m,'joss'),
            'texte':'Corvus, approche.'}],{'interlocuteurs':interlocuteurs(m)}))
        self.assertNotIn('Joss',self.rendus(m))

    def test_aubin_nomme_gorm_visible_qui_n_a_pas_parle(self):
        m=relais()
        placer(m,'aubin','echoppe',[1,3])
        faire_entendre(m,'aubin','marchand','Aubin : « Gorm, as-tu du pain ? »',['marchand'],[])
        m=recharge(m)
        self.assertTrue(connait_nom(m,'joueur','marchand'))
        self.assertIn('Gorm',self.rendus(m))
        self.assertFalse(connait_nom(m,'joueur','aubin'))

    def test_les_etiquettes_du_recit_ne_sont_pas_des_noms_prononces(self):
        m=relais()
        placer(m,'aubin','echoppe',[1,3])
        faire_entendre(m,'aubin','marchand','Aubin dit à Gorm : « Bonjour. »',['marchand'],[])
        m=recharge(m)
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertFalse(connait_nom(m,'joueur','aubin'))
        self.assertNotIn('Gorm',self.rendus(m))

    def test_appeler_une_apparence_puis_entendre_ici_ne_donne_aucun_nom(self):
        # Depuis l'appel négocié, la réponse à un appel passe par ``appel.dire`` (« Ici, viens ! »).
        from donjon.appel import VIENS, dire as repondre_a_l_appel
        from donjon.pnj import heler
        m=relais()
        lignes=[]
        heler(m,'joueur','marchand',lignes)
        repondre_a_l_appel(m,'marchand','joueur',VIENS,lignes,nommer=True)
        m=recharge(m)
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertFalse(connait_nom(m,'marchand','joueur'))
        self.assertNotIn('Gorm',self.rendus(m))

    def test_un_producteur_pnj_designe_corvus_avant_sa_presentation(self):
        from donjon.social import phrase
        m=relais()
        fait={'type':'vu_agir','auteur':'joueur','operation':'prendre','objet':'briquet'}
        self.assertFalse(connait_nom(m,'marchand','joueur'))
        self.assertIn("l'étranger",phrase(m,fait,locuteur='marchand'))
        placer(m,'aubin','echoppe',[1,3])
        faire_entendre(m,'marchand','aubin','Gorm : « Corvus a pris le briquet. »',['joueur'],[])
        m=recharge(m)
        self.assertNotIn('Corvus',m.data['bruits'][-1]['texte'])
        self.assertFalse(connait_nom(m,'aubin','joueur'))
        self.assertNotIn('Corvus',phrase(m,fait,locuteur='marchand'))
        self.assertNotIn('Gorm',self.rendus(m))
        m,_=dire(m,'Je suis Corvus.')
        m=recharge(m)
        self.assertTrue(connait_nom(m,'marchand','joueur'))
        self.assertIn('Corvus',phrase(m,fait,locuteur='marchand'))
        self.assertNotIn('Gorm',self.rendus(m))

    def test_meme_nature_auberge_pnj_voit_corvus_puis_apprend_son_nom(self):
        m=creer('auberge',1985,'fixe')
        ids=[i for i,o in m.objets.items() if o['type']=='personnage']
        calme(m,*ids)
        # Deux corps proches à la cuisine ; aucune connaissance de l'étranger déclarée.
        m.joueur.update(salle='cuisine',position=[1,2],orientation='nord')
        placer(m,'joss','cuisine',[1,1])
        m.objets['joss']['orientation']='sud'
        percevoir_tous(m)
        m=recharge(m)
        self.assertFalse(connait_nom(m,'joss','joueur'))
        faits={'interlocuteurs':{designation(m,'joss'):{'nom':nom_pour_joueur(m,'joss')}}}
        self.assertTrue(voix_inconnues(m,[{'locuteur':designation(m,'joss'),'texte':'Corvus, approche.'}],faits))
        nom=nom_pour_joueur(m,'joss')
        m,rapport=preparer_parole(m,{'personnage':designation(m,'joss'),'replique':'Je suis Corvus.',
            'contenu':[],'_intention':f'je dis à {nom} : Je suis Corvus.'})
        m=recharge(m)
        self.assertTrue(connait_nom(m,'joss','joueur'))
        self.assertEqual(voix_inconnues(m,[{'locuteur':designation(m,'joss'),'texte':'Corvus, approche.'}],faits),[])
        self.assertNotIn('Joss',self.rendus(m))

    def test_don_vise_la_designation_par_la_saisie_locale(self):
        m=relais()
        p=analyser(m,"je donne le briquet à l'homme trapu")
        self.assertIsNotNone(p)
        resultat=Moteur(m).executer(Moteur(m).preparer(p))
        m=recharge(m)
        self.assertEqual(m.objets['briquet']['lieu'],'marchand')
        self.assertIn("homme trapu",resultat)
        self.assertNotIn('Gorm',resultat+self.rendus(m))
        self.assertNotIn('Gorm',' '.join(m.data['journal'][-1]['faits']))

    def test_resultat_de_manoeuvre_et_journal_gardent_la_designation(self):
        from donjon.operations import etape, sequence
        m=relais()
        m.objets['briquet']['nom']='briquet de Gorm'
        moteur=Moteur(m)
        resultat=moteur.executer(moteur.preparer(sequence(etape('deplacer','briquet','echoppe'))))
        m=recharge(m)
        self.assertEqual(m.objets['briquet']['lieu'],'echoppe')
        faits=m.data['journal'][-1]['faits']+m.data['journal'][-1]['etapes'][0]['faits']
        self.assertNotIn('Gorm',resultat+' '.join(faits)+self.rendus(m))

    def test_apercu_de_tentative_ne_nomme_ni_opposant_ni_risque(self):
        from donjon.moteur import proposition
        for id_,nom_ in [('aubin','Aubin'),('marchand','Gorm')]:
            with self.subTest(id=id_):
                m=relais()
                placer(m,id_,'echoppe',[1,1])
                if id_!='marchand': placer(m,'marchand','crypte',[2,2])
                m=recharge(m)
                avant=json.dumps(m.data,sort_keys=True)
                plan=Moteur(m).preparer(proposition('pousser',designation(m,id_)))
                from donjon.couverture_action import entree
                revue=json.dumps(entree('écarte cet homme',plan,m),ensure_ascii=False)
                self.assertNotIn(nom_,revue)
                self.assertNotIn('('+id_+')',revue)
                self.assertIn(designation(m,id_),revue)
                self.assertNotIn(nom_,plan.resume(m))
                self.assertIn(nom_pour_joueur(m,id_).lower(),plan.resume(m).lower())
                self.assertEqual(avant,json.dumps(m.data,sort_keys=True))
                m=recharge(m)
                plan=Moteur(m).preparer(plan.proposition)
                self.assertNotIn(nom_,plan.resume(m)+self.rendus(m))
                self.assertFalse(connait_nom(m,'joueur',id_))

    def test_frontiere_mj_refuse_l_id_devine_puis_accepte_la_reference_publique(self):
        from unittest.mock import patch
        from donjon.mj import MJ
        from donjon.moteur import proposition
        for id_,nom_ in [('aubin','Aubin'),('marchand','Gorm')]:
            with self.subTest(id=id_):
                m=relais()
                placer(m,id_,'echoppe',[1,1])
                if id_!='marchand': placer(m,'marchand','crypte',[2,2])
                m=recharge(m)
                avant=json.dumps(m.data,sort_keys=True)
                def action(cible):return {'mode':'action','texte':'','faits':[],
                                          'proposition':proposition('pousser',cible)}
                mj=MJ()
                with patch.object(mj,'_appeler_brut',side_effect=[action(id_),action(designation(m,id_))]) as appels, \
                     patch.object(mj,'_auditer_action'):
                    r=mj.echanger(m,f'je pousse {nom_pour_joueur(m,id_)}')
                self.assertEqual(appels.call_count,2)
                retour=appels.call_args_list[1].args[1]['controle_narratif']
                self.assertIn('proposition.cible',json.dumps(retour,ensure_ascii=False))
                self.assertEqual(r['proposition']['cible'],id_)
                self.assertEqual(avant,json.dumps(m.data,sort_keys=True))
                m=recharge(m)
                self.assertNotIn(nom_,Moteur(m).preparer(r['proposition']).resume(m)+self.rendus(m))

    def test_frontiere_references_couvre_champs_et_union_sans_reecrire_les_mots(self):
        from donjon.noms import verifier_references,CHAMPS_REFERENCES,LISTES_REFERENCES
        from donjon.refus import RefusDeForme
        m=relais()
        faits=m.contexte()
        alias=designation(m,'marchand')
        for champ in CHAMPS_REFERENCES|LISTES_REFERENCES:
            with self.subTest(champ=champ):
                valeur=['marchand'] if champ in LISTES_REFERENCES else 'marchand'
                with self.assertRaises(RefusDeForme):
                    verifier_references(m,{'etapes':[{champ:valeur}]},faits)
                valeur=[alias] if champ in LISTES_REFERENCES else alias
                verifier_references(m,{'etapes':[{champ:valeur}]},faits)
        mots={'personnage':alias,'replique':'Je suis Aubin. Gorm, écoute.',
              'contenu':[{'type':'nom','sujet':'aubin','attribut':'','valeur':''}]}
        avant=json.dumps(mots,sort_keys=True)
        verifier_references(m,mots,faits)
        self.assertEqual(avant,json.dumps(mots,sort_keys=True))
        with self.assertRaises(RefusDeForme):
            verifier_references(m,{'savoirs':[{'sujet':'marchand','texte':'bonjour'}]},faits)
        with self.assertRaises(RefusDeForme):
            verifier_references(m,{'ajouts':[{'type':'parole','ancrage':'marchand','texte':'bonjour'}]},faits)
        with self.assertRaises(RefusDeForme):
            verifier_references(m,{'cible':'marchand'},{**faits,'texte_prive_contaminant':'marchand'})

    def test_recit_ne_nomme_pas_un_inconnu_meme_si_fait_contamine(self):
        m=relais()
        faits={'interlocuteurs':interlocuteurs(m),'poison':'Gorm'}
        self.assertTrue(voix_inconnues(m,[],faits,'Gorm te regarde.'))
        self.assertEqual(voix_inconnues(m,[],faits,"L'homme trapu te regarde."),[])

    def test_les_liens_declares_et_introduction_sont_des_donnees(self):
        m=relais()
        self.assertTrue(connait_nom(m,'aubin','marchand'))
        m=creer('auberge',1985,'fixe')
        self.assertTrue(connait_nom(m,'joueur','odile'))
        self.assertFalse(connait_nom(m,'joueur','joss'))

    def test_deux_memes_apparences_rechargees_restent_uniques(self):
        m=relais()
        m.joueur.update(position=[3,2],orientation='nord')
        for id in ('brune','ilse'):
            placer(m,id,'echoppe',[3+('brune','ilse').index(id),1])
            m.objets[id]['portrait']='Une femme en manteau sombre.'
            del m.data['personnes'][id]
        from donjon.noms import installer
        installer(m)
        avant=[nom_pour_joueur(m,id) for id in ('brune','ilse')]
        self.assertEqual(len(set(avant)),2)
        m=recharge(m)
        self.assertEqual(avant,[nom_pour_joueur(m,id) for id in ('brune','ilse')])

    def test_tout_le_contexte_masque_portrait_cite_et_identifiants_composes(self):
        from donjon.monde import objet
        m=relais()
        m.objets['marchand']['portrait'] += ' « Gorm », dit le portrait.'
        m.objets['bras_gorm']=objet('bras_gorm','bras de Gorm','partie_corps','marchand',
                                  description_visuelle='Un tatouage dit « Gorm ».')
        m=recharge(m)
        avant=json.dumps(m.data,sort_keys=True)
        contexte=json.dumps(m.contexte(),ensure_ascii=False)
        self.assertNotIn('Gorm',contexte)
        self.assertNotIn('bras_gorm',contexte)
        from donjon.noms import reference
        self.assertEqual(m.trouver(reference(m,'bras_gorm')),'bras_gorm')
        self.assertEqual(m.trouver("bras de l'homme trapu"),'bras_gorm')
        with self.assertRaises(ErreurMonde): m.trouver('bras_gorm')
        self.assertNotIn('"marchand"',contexte)
        self.assertEqual(avant,json.dumps(m.data,sort_keys=True))
        self.assertNotIn('Gorm',decrire(m,'marchand',detail=True))

    def test_un_pseudonyme_devine_ne_donne_aucun_acces_hors_perception(self):
        from donjon.noms import designation as pseudonyme
        from donjon.moteur import proposition
        m=relais()
        placer(m,'brune','chambre_cloche',[1,1])
        alias=pseudonyme(m,'brune')
        avant=json.dumps(m.data,sort_keys=True)
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(proposition('examiner',alias))
        self.assertNotIn('Brune',str(refus.exception))
        self.assertEqual(avant,json.dumps(m.data,sort_keys=True))

    def test_voie_mj_une_mention_de_tiers_ne_devine_pas_son_corps(self):
        from tests.test_audits_attendu import jouer, rapport, ligne
        from tests.test_repli_et_appel import parole, dialogue
        m=relais()
        m.joueur.update(position=[3,2],orientation='nord')
        placer(m,'marchand','echoppe',[3,1])
        placer(m,'aubin','echoppe',[4,1])
        m.actualiser_souvenirs_personnages()
        self.assertTrue(m.visible('marchand') and m.visible('aubin'))
        alias=designation(m,'aubin')
        citation='Gorm pourra te renseigner.'
        reponse="Le vieil homme voûté répond : « "+citation+" »"
        m,sortie,appels=jouer(m,'je dis au vieil homme voûté : bonsoir',[
            parole('bonsoir',('propos','','',''),personnage=alias),dialogue(reponse)],
            [rapport(ligne('parole',locuteur=alias,citation=citation))])
        self.assertIn(reponse,sortie)
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertFalse(connait_nom(m,'joueur','aubin'))
        m=recharge(m)
        self.assertNotIn('Gorm',self.rendus(m))
        self.assertIn(citation,m.data['paroles_pnj'][-1]['texte'])
        premiere=appels[0][1]['faits']['esprits_interlocuteurs'][alias]
        self.assertNotIn('noms_pour_repliques',premiere)
        narration=next(e['faits']['esprits_interlocuteurs'][alias] for f,e in appels
                      if f=='repondre_au_joueur' and e['faits'].get('conversation_validee'))
        self.assertIn('Gorm',narration['noms_pour_repliques'])
        self.assertNotIn('marchand',json.dumps(narration))

    def test_se_donner_un_nom_ne_presente_pas_le_corps_du_tiers(self):
        m=relais()
        m,rapport=dire(m,'Je suis Gorm.')
        m=recharge(m)
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertNotIn('Gorm',self.rendus(m))
        self.assertIn('« Gorm »',' '.join(rapport['faits']))

    def test_identite_privee_ne_fonde_pas_le_nom_dans_le_recit(self):
        m=relais()
        alias=designation(m,'marchand')
        faits={'interlocuteurs':interlocuteurs(m),
               'esprits_interlocuteurs':{alias:{'nom_du_locuteur':'Gorm'}}}
        self.assertTrue(voix_inconnues(m,[],faits,'Gorm te regarde.'))
        self.assertNotIn('Gorm',json.dumps(m.contexte(),ensure_ascii=False))
        self.assertNotIn('Gorm',self.rendus(recharge(m)))

    def test_le_mj_recoit_l_identite_privee_du_locuteur_pour_sa_presentation(self):
        from tests.test_audits_attendu import jouer, rapport, ligne
        from tests.test_repli_et_appel import parole, dialogue
        for id,nom_,apparence in [('marchand','Gorm',"l'homme trapu"),('ilse','Ilse','la femme ronde')]:
            with self.subTest(locuteur=id):
                m=relais()
                placer(m,'marchand','crypte',[2,3])
                placer(m,id,'echoppe',[1,1])
                alias=designation(m,id)
                citation=f"Je m'appelle {nom_}."
                reponse=apparence[:1].upper()+apparence[1:]+' dit : « '+citation+' »'
                m,sortie,appels=jouer(m,'je dis à '+apparence+' : bonsoir',[
                    parole('bonsoir',('propos','','',''),personnage=alias),dialogue(reponse)],
                    [rapport(ligne('parole',locuteur=alias,citation=citation))])
                self.assertNotIn('nom_du_locuteur',appels[0][1]['faits']['esprits_interlocuteurs'][alias])
                prive=next(e['faits']['esprits_interlocuteurs'][alias] for f,e in appels
                           if f=='repondre_au_joueur' and e['faits'].get('conversation_validee'))
                self.assertEqual(prive['nom_du_locuteur'],nom_)
                self.assertNotIn(id,json.dumps(prive))
                m=recharge(m)
                self.assertTrue(connait_nom(m,'joueur',id))
                self.assertIn(nom_,self.rendus(m))
                self.assertIn(citation,sortie)

    def test_paquet_nominal_prive_uniquement_dans_la_phase_narrative_au_fournisseur(self):
        from donjon.mj import MJ
        from donjon.fournisseurs import Reponse
        from donjon.transactions import appliquer
        from donjon.narration import consigner
        from tests.test_audits_attendu import rapport,ligne
        from tests.test_repli_et_appel import parole,dialogue
        for id_,nom_ in [('marchand','Gorm'),('ilse','Ilse')]:
            with self.subTest(locuteur=id_):
                m=relais()
                placer(m,'marchand','crypte',[2,3])
                placer(m,id_,'echoppe',[1,1])
                m=recharge(m)
                alias=designation(m,id_)
                apparence=nom_pour_joueur(m,id_)
                demandes=[]
                class Fournisseur:
                    def appeler(self,demande):
                        demandes.append(demande)
                        if demande.fonction=='auditer_narration':
                            audit=ligne('parole',locuteur=alias,citation=nom_+'.')
                            audit['presentation']=nom_
                            r=rapport(audit)
                        elif demande.fonction=='auditer_action':
                            r={'contenu_conforme':True,'motif':'Parole sans opération demandée.',
                               'operations_demandees':[]}
                        elif demande.entree['faits'].get('conversation_validee'):
                            r=dialogue(apparence[:1].upper()+apparence[1:]+' dit : « '+nom_+'. »')
                        else:
                            r=parole("Comment t'appelles-tu ?",('propos','','',''),personnage=alias)
                        return Reponse(r,None)
                    def fermer(self):pass
                r=MJ(fournisseur=Fournisseur()).echanger(m,'je dis à '+apparence+" : comment t'appelles-tu ?")
                phases=[d for d in demandes if d.fonction=='repondre_au_joueur']
                self.assertEqual(len(phases),2)
                for nom in ('Gorm','Aubin','Ilse','Brune'):
                    self.assertNotIn(nom,json.dumps(phases[0].entree['faits'],ensure_ascii=False))
                esprit=phases[1].entree['faits']['esprits_interlocuteurs'][alias]
                self.assertEqual(esprit['nom_du_locuteur'],nom_)
                self.assertTrue(esprit['noms_pour_repliques'])
                self.assertNotIn(id_,json.dumps(esprit))
                m,_=appliquer(m,r.get('_transactions',[]))
                consigner(m,r)
                m=recharge(m)
                self.assertTrue(connait_nom(m,'joueur',id_))
                self.assertIn(nom_,self.rendus(m))

    def test_nom_prive_cite_par_le_narrateur_reste_refuse_apres_audit(self):
        from tests.test_audits_attendu import jouer,rapport,ligne
        from tests.test_repli_et_appel import parole,dialogue
        from donjon.faits_locaux import preparer_faits
        for id_,nom_ in [('marchand','Gorm'),('ilse','Ilse')]:
            with self.subTest(locuteur=id_):
                m=relais()
                placer(m,'marchand','crypte',[2,3])
                placer(m,id_,'echoppe',[1,1])
                m=recharge(m)
                alias=designation(m,id_)
                apparence=nom_pour_joueur(m,id_)
                faux='Son nom est « '+nom_+' ».'
                sur='Tu vois toujours '+apparence+'.'
                r=rapport(ligne('mecanique',sources=['esprits_interlocuteurs']))
                m,sortie,appels=jouer(m,'je dis à '+apparence+' : bonjour',[
                    parole('bonjour',('propos','','',''),personnage=alias),
                    dialogue(faux),dialogue(faux),dialogue(sur)],
                    [r,r,rapport(ligne('mecanique',sources=['interlocuteurs']))])
                m=recharge(m)
                self.assertNotIn(nom_,sortie+self.rendus(m))
                self.assertFalse(connait_nom(m,'joueur',id_))
                self.assertEqual(len([f for f,_ in appels if f=='repondre_au_joueur']),4)
                avant=json.dumps(m.data,sort_keys=True)
                with self.assertRaises(ErreurMonde):
                    preparer_faits(m,{'ajouts':[{'type':'detail','ancrage':'briquet',
                        'nom':'marque','genre':'f','texte':faux}]})
                self.assertEqual(avant,json.dumps(m.data,sort_keys=True))

    def test_citation_exacte_de_corvus_etablie_sans_exempter_un_fragment(self):
        from tests.test_audits_attendu import jouer,rapport,ligne
        from tests.test_repli_et_appel import dialogue
        m=relais()
        mots='Je cherche Gorm.'
        m,_=dire(m,mots)
        m=recharge(m)
        self.assertEqual(m.data['paroles_joueur'][-1]['texte'],mots)
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        citation='« '+mots+' »'
        self.assertFalse(voix_inconnues(m,[],{},citation))
        self.assertTrue(voix_inconnues(m,[],{},'Le nom est « Gorm ».'))
        self.assertTrue(voix_inconnues(m,[],{},'Cet homme est « '+mots+' »'))
        # Un détail attaché à un objet n'est pas une restitution autonome de parole.
        from donjon.faits_locaux import preparer_faits
        with self.assertRaises(ErreurMonde):
            preparer_faits(m,{'ajouts':[{'type':'detail','ancrage':'briquet','nom':'marque',
                'genre':'f','texte':citation}]})
        m,sortie,_=jouer(m,"Qu'ai-je dit ?",[dialogue(citation)],
                         [rapport(ligne('mecanique',sources=['evenements_recents']))])
        m=recharge(m)
        self.assertIn(citation,sortie)
        self.assertEqual(m.data['paroles_joueur'][-1]['texte'],mots)
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertNotIn('Gorm',self.rendus(m))

    def test_une_citation_auditee_ne_transfere_pas_sa_provenance_a_un_autre_segment(self):
        from donjon.narration import controler
        from tests.test_audits_attendu import jouer,rapport,ligne
        from tests.test_repli_et_appel import parole as saisir_parole,dialogue
        for id_,nom_ in [('marchand','Gorm'),('ilse','Ilse')]:
            with self.subTest(locuteur=id_):
                m=relais()
                placer(m,'marchand','crypte',[2,3])
                placer(m,id_,'echoppe',[1,1])
                m=recharge(m)
                alias=designation(m,id_)
                mots=nom_+' est loin.'
                parole=nom_pour_joueur(m,id_)+' dit : « '+mots+' »'
                faux='Son nom est « '+mots+' »'
                texte=parole+'\n'+faux
                faits={'interlocuteurs':{alias:{'nom':nom_pour_joueur(m,id_)}}}
                controle=controler(texte,rapport(ligne('parole',locuteur=alias,citation=mots),
                    ligne('mecanique',sources=['interlocuteurs'])),faits)
                self.assertFalse(controle['obstacles'])
                refus=voix_inconnues(m,controle['paroles'],faits,texte)
                self.assertTrue(any(r['segment']==1 for r in refus))
                self.assertFalse(any(r['segment']==0 for r in refus))
                duplique=parole+' et « '+mots+' »'
                r=controler(duplique,rapport(ligne('parole',locuteur=alias,citation=mots)),faits)
                self.assertTrue(r['obstacles'])
                sur='Tu vois toujours '+nom_pour_joueur(m,id_)+'.'
                audits=rapport(ligne('parole',locuteur=alias,citation=mots),
                    ligne('mecanique',sources=['interlocuteurs']))
                m,sortie,_=jouer(m,'je dis à '+nom_pour_joueur(m,id_)+' : bonjour',[
                    saisir_parole('bonjour',('propos','','',''),personnage=alias),
                    dialogue(texte),dialogue(texte),dialogue(sur)],
                    [audits,audits,rapport(ligne('mecanique',sources=['interlocuteurs']))])
                m=recharge(m)
                self.assertNotIn(faux,sortie)
                self.assertFalse(connait_nom(m,'joueur',id_))
                self.assertNotIn(nom_,self.rendus(m))
                self.assertFalse(any(p['texte']==mots for p in m.data.get('paroles_pnj',[])))

    def test_deux_presentations_nominales_typees_relient_le_locuteur(self):
        from tests.test_audits_attendu import jouer, rapport, ligne
        from tests.test_repli_et_appel import parole, dialogue
        for id,nom_,apparence,citation in [('marchand','Gorm',"l'homme trapu",'Gorm.'),
                ('ilse','Ilse','la femme ronde','Ilse. Et toi, comment tu t’appelles ?')]:
            with self.subTest(locuteur=id):
                m=relais()
                placer(m,'marchand','crypte',[2,3])
                placer(m,id,'echoppe',[1,1])
                alias=designation(m,id)
                reponse=apparence[:1].upper()+apparence[1:]+' répond : « '+citation+' »'
                audit=ligne('parole',locuteur=alias,citation=citation)
                audit['presentation']=nom_
                m,sortie,_=jouer(m,'je dis à '+apparence+" : comment t'appelles-tu ?",[
                    parole("comment t'appelles-tu ?",('propos','','',''),personnage=alias),
                    dialogue(reponse)],[rapport(audit)])
                m=recharge(m)
                self.assertTrue(connait_nom(m,'joueur',id))
                self.assertIn(nom_,self.rendus(m))
                self.assertEqual(m.data['paroles_pnj'][-1]['presentation'],nom_)
                self.assertIn(citation,sortie)

    def test_presentation_typee_ne_peut_pas_ajouter_un_nom_non_prononce(self):
        from donjon.narration import controler
        from tests.test_audits_attendu import rapport, ligne
        m=relais()
        alias=designation(m,'marchand')
        audit=ligne('parole',locuteur=alias,citation='Bonsoir.')
        audit['presentation']='Gorm'
        controle=controler("L'homme trapu dit : « Bonsoir. »",rapport(audit),
                          {'interlocuteurs':interlocuteurs(m)})
        self.assertFalse(controle['obstacles'])
        self.assertEqual(controle['segments'][0]['presentation'],'')
        self.assertNotIn('presentation',controle['paroles'][0])
        self.assertFalse(connait_nom(recharge(m),'joueur','marchand'))

    def test_le_fait_parole_partage_la_presentation_typee_et_le_garde_des_noms(self):
        from donjon.faits_locaux import preparer_faits as preparer
        m=relais()
        alias=designation(m,'marchand')
        m,_,_=preparer(m,{'ajouts':[{'type':'parole','ancrage':alias,'nom':'','genre':'',
                                'texte':'Gorm.','presentation':'Gorm'}]})
        m=recharge(m)
        self.assertTrue(connait_nom(m,'joueur','marchand'))
        self.assertIn('Gorm',self.rendus(m))
        self.assertEqual(m.data['paroles_pnj'][-1]['presentation'],'Gorm')
        avant=json.dumps(m.data,sort_keys=True)
        with self.assertRaises(ErreurMonde):
            preparer(m,{'ajouts':[{'type':'parole','ancrage':'marchand','nom':'','genre':'',
                                 'texte':'Corvus, approche.','presentation':''}]})
        self.assertEqual(avant,json.dumps(m.data,sort_keys=True))

    def test_une_voix_qui_se_dit_aubin_ne_nomme_pas_le_vrai_corps_d_aubin(self):
        from donjon.voix import retenir, connait_appellation
        from donjon.paroles import analyser as analyser_parole, destinataires
        from donjon.noms import reference
        m=relais()
        placer(m,'aubin','echoppe',[2,1])
        placer(m,'ilse','echoppe',[4,3])
        retenir(m,'joueur','ilse')['se_dit']='aubin'
        m.data['entendus']=['ilse']
        m=recharge(m)
        self.assertTrue(connait_appellation(m,'joueur','aubin'))
        self.assertFalse(connait_nom(m,'joueur','aubin'))
        connaitre(m,'joueur','aubin')
        m=recharge(m)
        self.assertFalse(m.data['voix_entendues']['ilse']['mefiance'])
        self.assertFalse(connait_nom(m,'joueur','aubin'))
        self.assertEqual(destinataires(m,analyser_parole(m,'je dis à Aubin : bonsoir')),['ilse'])
        scene=scene_percue(m)
        apparu=next(o for n in scene['niveaux'] for o in n['objets'] if o['id']==reference(m,'aubin'))
        self.assertNotIn('Aubin',apparu['nom'])
        with self.assertRaises(ErreurMonde): m.trouver('Aubin')
        self.assertNotIn('aubin',m.contexte()['personnages_connus'])


if __name__=='__main__': unittest.main()
