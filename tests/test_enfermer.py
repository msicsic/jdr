"""Captivité : portes réelles, croyances, secours, sauvegarde et horloge."""
import unittest
from unittest.mock import patch
from donjon.banc_pnj import creer, appliquer_etats
from donjon import corps, tenir, pnj
from donjon.esprits import lire, croire, percevoir_tous
from donjon.deplacement_objet import deplacer
from donjon.moteur import Moteur, proposition
from donjon.commandes import analyser
from donjon.monde import ErreurMonde
from donjon.rendu import regarder
from donjon.relations import se_mefie
from donjon.temps import instant
from tests.support import presentes, calme
from tests.test_tensions import placer, recharger
from tests.test_corps_blessable import passer


def scene(cible="remy", salle="bureau"):
    m = presentes(creer("mine", 1985, "fixe"))
    calme(m, *[i for i,o in m.objets.items() if o["type"] == "personnage"])
    appliquer_etats(m, [cible + ":enferme:" + salle])
    porte = next(iter(m.data["salles"][salle]["sorties"].values()))["porte"]
    for n,(i,o) in enumerate((i,o) for i,o in m.objets.items() if o["type"] == "personnage" and i != cible):
        placer(m, i, "galerie", (n, 1))
    m.joueur.update(salle="baraquement", position=[4, 1], orientation="nord")
    if salle == "reserve":
        m.joueur.update(position=[3,5],orientation="sud")
    percevoir_tous(m)
    return m, porte


class EnfermerTests(unittest.TestCase):
    def test_etat_refuse_le_beffroi_sans_modifier_scenario(self):
        m=creer("relais",1985,"fixe")
        avant = recharger(m)
        with self.assertRaises(ValueError):
            appliquer_etats(m,["ilse:enferme:beffroi"])
        self.assertEqual(m.data, avant.data)

    def test_verrouillage_joueur_refus_et_fiche_recharge(self):
        m,p=scene()
        deplacer(m,"passe","joueur")
        m.objets[p]["verrouillee"]=False
        plan=Moteur(m).preparer(analyser(m,"verrouiller porte_bureau avec passe"))
        self.assertEqual(plan.dixiemes,50)
        self.assertTrue(plan.confirmation)
        texte=Moteur(m).executer(plan)
        m=recharger(m)
        self.assertTrue(m.objets[p]["verrouillee"])
        self.assertIn("verrouill",texte)
        for outil,ouverte,verrou in [("",False,False),("pioche",False,False),("passe",True,False),("passe",False,True)]:
            m.objets[p].update(ouverte=ouverte,verrouillee=verrou)
            with self.subTest(outil=outil,ouverte=ouverte,verrou=verrou), self.assertRaises(ErreurMonde) as cm:
                Moteur(m).preparer(proposition("verrouiller",p,outil))
            self.assertTrue(cm.exception.attendu)

    def test_auteur_croit_victime_sans_la_reveler_a_la_victime(self):
        for salle in ("bureau","reserve"):
            with self.subTest(salle=salle):
                m,p=scene(salle=salle)
                croire(m,"josse","remy","lieu",salle,"savoir",salle=salle,case=None)
                tenir.enfermer(m,"josse",p,instant(m)+50)
                m=recharger(m)
                gestes=[g for g in m.data["gestes_en_cours"] if g["operation"]=="enfermer"]
                self.assertEqual([g["objet"] for g in gestes],["remy"])
                self.assertFalse(any(s["type"]=="enferme" for s in lire(m,"remy")["memoire"]))
                pnj._ouvrir_en_chemin(m,"remy",m.objets[p],[])
                m=recharger(m)
                self.assertTrue(any(s["type"]=="enferme" for s in lire(m,"remy")["memoire"]))
                self.assertNotIn("auteur",next(s for s in lire(m,"remy")["memoire"] if s["type"]=="enferme"))
                self.assertIn("porte",regarder(recharger(m)))

    def test_forcer_sortie_avec_outil_bruit_et_recharge(self):
        m,p=scene("bram")
        deplacer(m,"cle_paie","baraquement",(5,1))
        deplacer(m,"pioche","bram")
        for i,o in m.objets.items():
            if o["type"]=="personnage" and i != "bram":
                corps.endormir(m,i)
        pnj._ouvrir_en_chemin(m,"bram",m.objets[p],[])
        from donjon.deliberation import choisir
        choisir(m,"bram",m.data["minutes"])
        self.assertIsNotNone(lire(m,"bram")["intention"])
        entendus=[]
        with patch.object(type(m),"d20",return_value=20):
            for _ in range(8):
                entendus.append(Moteur(m).executer(Moteur(m).preparer(proposition("attendre","60"))))
                m=recharger(m)
        self.assertIn("grand bruit", " ".join(entendus))
        self.assertEqual(m.objets[p]["integrite"],0)
        self.assertFalse(m.objets[p]["verrouillee"])
        self.assertTrue(m.objets[p]["ouverte"])
        self.assertNotEqual(m.objets["bram"]["lieu"],"bureau")
        self.assertIn("porte",regarder(m))

    def test_epaule_joueur_porte_et_pas_objet_quelconque(self):
        m,p=scene()
        plan=Moteur(m).preparer(proposition("frapper",p))
        self.assertEqual(plan.dixiemes,30)
        with patch.object(type(m),"d20",return_value=20):
            Moteur(m).executer(plan)
        self.assertLess(recharger(m).objets[p]["integrite"],25)

    def test_secours_protecteur_avec_cle(self):
        m,p=scene("lucien")
        placer(m,"josse","baraquement",(4,2))
        deplacer(m,"passe","josse")
        pnj._ouvrir_en_chemin(m,"lucien",m.objets[p],[])
        with patch.object(type(m),"d20",return_value=20):
            for _ in range(5):
                passer(m,600)
                m=recharger(m)
        self.assertFalse(m.objets[p]["verrouillee"])
        self.assertEqual(m.objets[p]["integrite"],25)

    def test_assommer_trainer_verrouiller_temoin_reveil_et_decoupage(self):
        m,p=scene("bram")
        m.objets[p].update(ouverte=True,verrouillee=False)
        m.joueur.update(salle="baraquement",position=[4,0],orientation="sud")
        placer(m,"bram","baraquement",(4,1))
        m.objets["bram"]["orientation"]="sud"
        for i,o in m.objets.items():
            if o.get("lieu")=="joueur" and o.get("mobile"):
                deplacer(m,i,"baraquement",(5,1))
        percevoir_tous(m)
        with patch.object(type(m),"d20",return_value=20):
            Moteur(m).executer(Moteur(m).preparer(proposition("frapper","bram","","assommer")))
        self.assertFalse(corps.conscient(m,"bram"))
        m.joueur["orientation"]="nord"
        for sens in ("nord","nord","est"):
            Moteur(m).executer(Moteur(m).preparer(proposition("trainer","bram",sens)))
            m=recharger(m)
        self.assertEqual(m.objets["bram"]["lieu"],"bureau")
        # Revenir par les deux pas communs et prendre la clé existante.
        for sens in ("sud","ouest","sud"):
            Moteur(m).executer(Moteur(m).preparer(proposition("marcher",sens)))
        deplacer(m,"passe","joueur")
        placer(m,"gaspard","baraquement",(5,0))
        # Le témoin vient d'être placé ici ; il ne poursuit pas un ancien
        # abri à la galerie pendant les deux gestes observés.
        lire(m,"gaspard")["intention"] = None
        # Il assiste au geste pendant ce laps, sans entreprendre un trajet.
        lire(m,"gaspard")["libre"] = instant(m) + 600
        m.objets["gaspard"]["orientation"]="ouest"
        percevoir_tous(m)
        Moteur(m).executer(Moteur(m).preparer(proposition("fermer",p)))
        texte=Moteur(m).executer(Moteur(m).preparer(proposition("verrouiller",p,"passe")))
        m=recharger(m)
        self.assertIn("verrouill",texte)
        self.assertTrue(any(e["type"]=="enfermer" and e["id"]=="bram" for e in m.data["historique_corps"]))
        self.assertTrue(any(s.get("operation")=="enfermer" for s in lire(m,"gaspard")["memoire"]))
        self.assertTrue(se_mefie(m,"gaspard","joueur"))
        # Au réveil il essaie, apprend, puis emploie les mêmes moyens d'évasion.
        corps.reveiller(m,"bram")
        deplacer(m,"cle_paie","baraquement",(5,1))
        deplacer(m,"pioche","bram")
        pnj._ouvrir_en_chemin(m,"bram",m.objets[p],[])
        a,b=recharger(m),recharger(m)
        with patch.object(type(m),"d20",return_value=20):
            passer(a,600)
            for dt in (13,47,540):
                passer(b,dt)
                b=recharger(b)
        a,b=recharger(a),recharger(b)
        self.assertEqual(a.data,b.data)
        self.assertEqual(regarder(a),regarder(b))
        self.assertFalse(a.objets[p]["verrouillee"])
        self.assertEqual(a.objets[p]["integrite"],0)

    def test_pas_de_victime_inconnue_ni_issue_ouverte_ignoree(self):
        m=creer("relais",1985,"fixe")
        self.assertTrue(any(not v for _,v in tenir.sorties_crues(m,"ilse","beffroi")))
        croire(m,"marchand","brune","lieu","beffroi","savoir",salle="beffroi",case=None)
        tenir.enfermer(m,"marchand","porte",instant(m)+50)
        self.assertFalse(any(g["operation"]=="enfermer" for g in m.data.get("gestes_en_cours",[])))
        m,p=scene()
        lire(m,"josse")["croyances"].pop("remy",None)
        tenir.enfermer(m,"josse",p,instant(m)+50)
        self.assertFalse(any(g["operation"]=="enfermer" and g["objet"]=="remy" for g in m.data.get("gestes_en_cours",[])))

    def test_crochetage_sortie_par_plan_commun(self):
        m,p=scene("odon")
        # Odon a déjà ses crochets, mais aucune clé du bureau.
        deplacer(m,"lampe_rechange_1","odon")
        m.objets["lampe_rechange_1"]["allume"]=True
        for i,o in m.objets.items():
            if o["type"]=="personnage" and i!="odon":
                corps.endormir(m,i)
        percevoir_tous(m)
        pnj._ouvrir_en_chemin(m,"odon",m.objets[p],[])
        from donjon.deliberation import choisir
        choisir(m,"odon",m.data["minutes"])
        self.assertIn("crocheter",[e["operation"] for e in lire(m,"odon")["intention"]["plan"]])
        with patch.object(type(m),"d20",return_value=20):
            for _ in range(4):
                passer(m,600)
                m=recharger(m)
        self.assertFalse(m.objets[p]["verrouillee"])
        self.assertEqual(m.objets[p]["integrite"],25)

    def test_fermer_verrouiller_composes_meme_contrat(self):
        from donjon.operations import sequence, etape
        m,p=scene()
        m.objets[p].update(ouverte=True,verrouillee=False)
        deplacer(m,"passe","joueur")
        plan=Moteur(m).preparer(sequence(etape("fermer",p),etape("verrouiller",p,outil="passe")))
        self.assertTrue(m.objets[p]["ouverte"])
        texte=Moteur(m).executer(plan)
        m=recharger(m)
        self.assertFalse(m.objets[p]["ouverte"])
        self.assertTrue(m.objets[p]["verrouillee"])
        self.assertIn("verrouill",texte)

    def test_constat_passe_reste_sauvegardable_apres_deces(self):
        m,p=scene()
        pnj._ouvrir_en_chemin(m,"remy",m.objets[p],[])
        corps.mourir(m,"remy")
        m=recharger(m)
        self.assertEqual(m.objets["remy"]["type"],"depouille")
