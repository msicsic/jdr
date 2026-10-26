"""L'union typée ne peut pas transporter une charge mécanique dans un champ inutilisé."""
import json
import unittest

from donjon.monde import ErreurMonde
from donjon.refus import RefusDeForme
from donjon.paroles import CHAMPS_CONTENU, SCHEMA_PAROLE, TYPES, verifier_contenus
from donjon.voix import connait_nom, designation
from donjon.carte import carte
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_noms import relais, recharge
from tests.test_audits_attendu import jouer, rapport, ligne
from tests.test_repli_et_appel import parole, dialogue


def rendus(m):
    return regarder(m)+carte(m)+json.dumps(scene_percue(m),ensure_ascii=False)


class ContenusParoleTests(unittest.TestCase):
    def test_schema_et_validateur_partagent_tous_les_champs_sans_sens(self):
        variantes = SCHEMA_PAROLE['properties']['contenu']['items']['anyOf']
        for type_ in TYPES:
            if type_ == 'proposition':
                continue
            with self.subTest(type=type_):
                compatibles = [v for v in variantes if type_ in v['properties']['type']['enum']]
                self.assertEqual(len(compatibles), 1)
                types = compatibles[0]['properties']['type']
                for autre in TYPES:
                    self.assertEqual(autre + ' :' in types['description'], autre in types['enum'])
                for champ in ('sujet', 'attribut', 'valeur'):
                    p = compatibles[0]['properties'][champ]
                    self.assertEqual(p.get('enum') == [''], champ not in CHAMPS_CONTENU[type_])

    def test_questions_ordinaires_deux_scenarios_sans_correction_apres_recharge(self):
        from tests.test_gardes_justes import crypte
        from tests.test_parole_corrections import banc
        cas = ((crypte(), 'Gorm, que sais-tu de cette crypte ?', 'marchand'),
               (banc('echanges'), '« Tu sais où est passé le gardien ? »', 'brune'))
        for m, saisie, qui in cas:
            with self.subTest(saisie=saisie):
                m = recharge(m)
                avant = {id: o.get('lieu') for id, o in m.objets.items()}
                mots = saisie.strip('«» ')
                texte = 'Ta question a été entendue.'
                r, sortie, appels = jouer(m, saisie, [
                    parole(mots, ('propos', '', '', ''), personnage=designation(m, qui)),
                    dialogue(texte)], [rapport(ligne('mecanique', sources=['conversation_validee']))])
                self.assertEqual([f for f, _ in appels],
                                 ['repondre_au_joueur', 'repondre_au_joueur', 'auditer_narration'])
                self.assertFalse(any('retour_moteur' in e.get('faits', {}) for _, e in appels))
                rr = recharge(r)
                self.assertEqual(rr.data['paroles_joueur'][-1]['texte'], mots)
                self.assertIn(texte, sortie)
                self.assertIn(texte, str(rr.data['narrations_mj']))
                self.assertEqual({id: o.get('lieu') for id, o in rr.objets.items()}, avant)
                self.assertEqual(rendus(rr), rendus(r))

    def test_champs_sans_sens_refuses_pour_chaque_type(self):
        # Contrat de parole : ces champs doivent être vides pour ces types.
        vides={'propos':('sujet','attribut','valeur'), 'qui':('sujet','attribut','valeur'),
               'nom':('attribut','valeur'), 'reclamer':('attribut','valeur'),
               'ressource':('attribut','valeur'), 'demande':('attribut',),
               'passage':('attribut',), 'aveu':('attribut',)}
        m=relais()
        avant=json.dumps(m.data,sort_keys=True)
        for type_, champs in vides.items():
            for champ in champs:
                with self.subTest(type=type_,champ=champ):
                    c={'type':type_,'sujet':'','attribut':'','valeur':'',champ:'inattendu'}
                    with self.assertRaises(ErreurMonde) as refus:
                        verifier_contenus(m,[c])
                    self.assertIsInstance(refus.exception,RefusDeForme)
                    self.assertIn('contenu[0].'+champ,str(refus.exception.attendu))
                    self.assertIn('inattendu',str(refus.exception.attendu))
                    self.assertIn('vide',str(refus.exception.attendu))
                    self.assertEqual(avant,json.dumps(m.data,sort_keys=True))

    def test_cas_reel_charge_dans_propos_reprise_en_question_typee(self):
        m=relais()
        mots="comment t'appelles-tu ?"
        reponse='Gorm répond : « Gorm. »'
        m,sortie,appels=jouer(m,"je dis à l'homme trapu : "+mots,[
            parole(mots,('propos','nom','',''),personnage=designation(m,'marchand')),
            parole(mots,('qui','','',''),personnage=designation(m,'marchand')),
            dialogue(reponse)], [rapport(ligne('parole',locuteur='marchand',citation='Gorm.'))])
        m=recharge(m)
        self.assertTrue(connait_nom(m,'joueur','marchand'))
        self.assertIn('Gorm',rendus(m))
        self.assertIn(reponse,sortie)
        retours=[entree.get('faits',{}).get('retour_moteur',{}) for _,entree in appels]
        self.assertTrue(any('contenu[0].sujet' in str(r) and 'vide' in str(r) for r in retours))

    def test_meme_nature_propos_avec_objet_puis_propos_vide(self):
        m=relais()
        alias=designation(m,'marchand')
        reponse="L'homme trapu répond : « Bonsoir. »"
        m,sortie,_=jouer(m,"je dis à l'homme trapu : bonsoir",[
            parole('bonsoir',('propos','briquet','',''),personnage=alias),
            parole('bonsoir',('propos','','',''),personnage=alias),
            dialogue(reponse)], [rapport(ligne('parole',locuteur=alias,citation='Bonsoir.'))])
        m=recharge(m)
        self.assertFalse(connait_nom(m,'joueur','marchand'))
        self.assertNotIn('Gorm',rendus(m))
        self.assertEqual(m.objets['briquet']['lieu'],'joueur')
        self.assertIn(reponse,sortie)


if __name__=='__main__': unittest.main()
