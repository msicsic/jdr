"""Accords communs, gestes sociaux persistés et vue du joueur rechargée."""
import copy
import unittest
from unittest.mock import patch

from donjon.francais import designer, pluriel, quantite
from donjon.monde import Monde
from donjon.deplacement_objet import deplacer
from donjon.pnj_propositions import executer
from donjon.recit_pnj import Recit
from donjon.rendu import decrire, fiche
from donjon.web.pont import PontWeb
from donjon.esprits import lire
from tests.test_proposer_recours import scene
from tests.test_tensions import recharger


class AccordsTests(unittest.TestCase):
    def test_nombre_commun_et_priorite_des_donnees(self):
        for nom in ("outils de serrurier", "planches", "joyaux"):
            with self.subTest(nom=nom):
                self.assertTrue(pluriel({"nom": nom}))
                self.assertEqual(designer({"nom": nom}), "les " + nom)
        self.assertEqual(designer({"nom": "provisions", "pluriel": True}), "les provisions")
        self.assertEqual(designer({"nom": "rubis", "pluriel": False}), "le rubis")
        self.assertFalse(pluriel({"nom": "Corvus", "type": "personnage"}))
        self.assertFalse(pluriel({}))
        for nom in ("bois", "tas de planches", "repos", "corps", "prix"):
            self.assertFalse(pluriel({"nom": nom}))

    def test_quantites_pieces_parts_et_objets(self):
        for n in (0, 1, 2):
            for mot in ("pièce", "part", "objet"):
                with self.subTest(n=n, mot=mot):
                    self.assertEqual(quantite(n, mot), f"{n} {mot}" + ("s" if n == 2 else ""))
        self.assertEqual(quantite(1, "pièce", determinant="defini"), "la 1 pièce")
        self.assertEqual(quantite(2, "pièce", determinant="possessif"), "tes 2 pièces")
        self.assertEqual(quantite(2, "cheval", "chevaux"), "2 chevaux")

    def test_objets_dans_echange_chronique_recit_et_vue_recharges(self):
        for nom, donnees in (("outils de serrurier", {}), ("joyaux", {}),
                             ("provisions", {"pluriel": True, "genre": "f"})):
            with self.subTest(nom=nom):
                m = scene(70)
                m.objets["crochets"].pop("pluriel", None)
                m.objets["crochets"].update(nom=nom, prix=1, **donnees)
                # La cession grammaticale conserve sa capacité grâce à un vrai double.
                m.objets["crochets_rechange"] = {
                    **copy.deepcopy(m.objets["crochets"]), "id": "crochets_rechange",
                    "nom": "crochets de rechange", "lieu": "brune", "proprietaire": "brune"}
                from donjon.esprits import percevoir_tous
                percevoir_tous(m)
                contenu = {"demande": {"type": "part", "objet": "vivres"},
                           "contrepartie": {"type": "objet", "objet": "crochets"}}
                lignes = []
                with patch.object(Monde, "d20", return_value=20):
                    self.assertTrue(executer(m, "brune", "marchand", contenu, lignes))
                m.memoriser("L'échange entendu", " ".join(lignes), "action")
                avant = copy.deepcopy(m.data)
                m = recharger(m)
                self.assertEqual(m.data, avant)
                self.assertEqual(m.objets["crochets"]["proprietaire"], "marchand")
                journal = m.data["chronique"]
                self.assertIn("les " + nom + " contre", "\n".join(c["texte"] for c in journal))
                self.assertIn("les " + nom + " contre", "\n".join(Recit(m).entre_eux(m, journal)))
                self.assertIn("les " + nom + " contre", m.data["conversation"][-1]["reponse"])
                # Le marchand le pose devant le joueur ; le moteur déplace le bien,
                # puis la vraie perception et le rendu sont relus depuis le disque.
                deplacer(m, "crochets", m.joueur["salle"], m.joueur["position"])
                m = recharger(m)
                self.assertEqual(m.objets["crochets"]["proprietaire"], "marchand")
                self.assertTrue(m.visible("crochets"))
                self.assertIn("Les " + nom, decrire(m, "crochets"))
                self.assertNotIn("l'" + nom, str(journal))

    def test_monnaie_proposee_et_fiche_apres_recharge(self):
        for n in (1, 2):
            with self.subTest(n=n):
                m = scene(70)
                contenu = {"demande": {"type": "part", "objet": "vivres"},
                           "contrepartie": {"type": "pieces", "montant": n}}
                depart = m.data["finances_pnj"].get("brune", 5)
                with patch.object(Monde, "d20", return_value=20):
                    self.assertTrue(executer(m, "brune", "marchand", contenu, []))
                m = recharger(m)
                self.assertEqual(m.data["finances_pnj"]["brune"], depart - n)
                attendu = f"{n} pièce" + ("s" if n == 2 else "")
                journal = m.data["chronique"]
                self.assertIn(attendu + " contre", "\n".join(c["texte"] for c in journal))
                self.assertIn(attendu + " contre", "\n".join(Recit(m).entre_eux(m, journal)))
        for n in (0, 1, 2):
            m = scene()
            m.joueur["or"] = n
            m = recharger(m)
            self.assertEqual(m.joueur["or"], n)
            attendu = f"{n} pièce" + ("s" if n == 2 else "")
            self.assertIn(attendu + " |", fiche(m))
            avant = copy.deepcopy(m.data)
            pont = PontWeb()
            pont.rafraichir(m, None, None)
            self.assertEqual(pont.dernier_etat["or_texte"], attendu)
            self.assertEqual(m.data, avant)


    def test_cas_reel_auberge_lucien_une_piece_contre_ballot(self):
        from donjon.auberge import nouveau_auberge
        from donjon.esprits import croire, percevoir_tous
        from donjon.spatial import installer
        from tests.support import calme, presentes, regarder
        from tests.test_tensions import placer
        m = presentes(nouveau_auberge(7, depart="fixe"))
        installer(m)
        calme(m, *[id for id, o in m.objets.items() if o.get("profil")])
        m.joueur.update(salle="salle_commune", position=[4, 4], orientation="ouest")
        placer(m, "lucien", "salle_commune", [3, 4])
        placer(m, "anselme", "salle_commune", [3, 5])
        regarder(m, "lucien", "anselme")
        regarder(m, "anselme", "lucien")
        m.data["connus"].extend(["ballot", "lucien", "anselme"])
        percevoir_tous(m)
        croire(m, "lucien", "ballot", "lieu", m.objets["ballot"]["lieu"], "savoir",
               salle="chambre_chaude", case=None)
        lire(m, "lucien")["intention"] = {"but": {"type": "argent", "objet": "ballot"},
            "motif": "biens", "plan": [], "depuis": 0, "attente": 0}
        contenu = {"demande": {"type": "objet", "objet": "ballot"},
                   "contrepartie": {"type": "pieces", "montant": 1}}
        ballot = copy.deepcopy(m.objets["ballot"])
        finances = copy.deepcopy(m.data["finances_pnj"])
        lignes = []
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(executer(m, "lucien", "anselme", contenu, lignes))
        m.memoriser("L'échange entendu", " ".join(lignes), "action")
        m = recharger(m)
        self.assertEqual(m.objets["ballot"], ballot)  # Le refus ne transfère aucun bien.
        self.assertEqual(m.data["finances_pnj"], finances)
        journal = m.data["chronique"]
        self.assertIn("1 pièce contre le ballot", "\n".join(c["texte"] for c in journal))
        self.assertIn("1 pièce contre le ballot", "\n".join(Recit(m).entre_eux(m, journal)))
        self.assertIn("1 pièce contre le ballot", m.data["conversation"][-1]["reponse"])

if __name__ == "__main__":
    unittest.main()
