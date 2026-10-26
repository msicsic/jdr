"""Avis exprimés : console/MJ, conséquences et paroles rechargées ensemble."""
import copy
import unittest

from donjon import eau, paroles, social
from donjon.esprits import croire, lire, prevision
from donjon.monde import ErreurMonde
from donjon.rendu import regarder as rendu
from tests.support import regarder
from tests.test_avis_menace import scene, relation
from tests.test_social import recharger
from tests.test_repli_et_appel import jouer, parole, dialogue, verdicts, NEUTRE


def preparer():
    m = scene()
    regarder(m, "joueur", "marchand")
    for qui in ("aubin", "ilse", "marchand"):
        regarder(m, qui, "joueur")
        relation(m, qui, "joueur", confiance=100, affection=80)
        for a in lire(m, qui)["croyances"].values():
            a.pop("eau", None)
            a.pop("prevision", None)
    return recharger(m)


def dire(m, salle="echoppe", valeur="oui", adresse="Gorm"):
    texte = f"l'eau {'menace' if valeur == 'oui' else 'ne menace pas'} {m.data['salles'][salle]['nom']}"
    saisie = f"je dis à {adresse} : {texte}"
    dest = paroles.prevue(m, saisie)["personnage"]
    return paroles.preparer_parole(m, {"personnage": dest, "replique": texte,
        "_intention": saisie, "contenu": [{"type": "avis", "sujet": salle,
        "attribut": "menace", "valeur": valeur}]})


class AvisJoueurTests(unittest.TestCase):
    def test_deux_lieux_deux_auditeurs_et_conviction_devinee(self):
        for salle, adresse, qui in (("echoppe", "Gorm", "marchand"), ("chambre_cloche", "Ilse", "ilse")):
            with self.subTest(salle=salle):
                m = preparer()
                avant = copy.deepcopy(m.data["crue"])
                m, rapport = dire(m, salle, adresse=adresse)
                m = recharger(m)
                self.assertEqual(prevision(m, qui, salle)["source"], "dit:joueur")
                self.assertEqual(prevision(m, qui, salle)["confiance"], .4)
                self.assertTrue(eau.menacee(m, qui, salle))
                self.assertEqual(m.data["crue"], avant)
                self.assertTrue(any(s.get("locuteur") == "joueur" for s in lire(m, qui)["memoire"]))
                self.assertEqual(rendu(m), rendu(recharger(m)))
                self.assertIn("retient ton avis", " ".join(rapport["faits"]))

    def test_estimation_propre_conviction_et_position_negative(self):
        m = preparer()
        croire(m, "joueur", "echoppe", "eau", 10, "vu", niveau=10, montee=20, repere=[m.data["minutes"], 10])
        noyau = social.avis_exprime(m, "joueur", "echoppe", False)
        self.assertEqual(noyau["conviction"], 1)
        self.assertFalse(noyau["valeur"])
        m, _ = dire(m, valeur="non")
        self.assertFalse(prevision(recharger(m), "marchand", "echoppe")["valeur"])

    def test_contradiction_temoins_et_pas_de_parole_inventee_du_joueur(self):
        m = preparer()
        t = m.data["minutes"]
        croire(m, "marchand", "echoppe", "prevision", [t, -10000, 1], "vu", 1, rang=0)
        relation(m, "ilse", "marchand", confiance=100, affection=100)
        relation(m, "ilse", "joueur", confiance=1, affection=0)
        relation(m, "aubin", "marchand", confiance=100, affection=100)
        relation(m, "aubin", "joueur", confiance=1, affection=0)
        m, rapport = dire(m)
        m = recharger(m)
        self.assertTrue(any(c.get("dispute") for c in m.data["chronique"]))
        self.assertEqual(prevision(m, "ilse", "echoppe")["source"], "dit:marchand")
        self.assertIn("Non, l'eau ne menace pas", " ".join(rapport["faits"]))
        self.assertNotIn("Je maintiens", " ".join(rapport["faits"]))
        self.assertTrue(any(s["type"] == "dispute_perdue" for s in lire(m, "joueur")["memoire"]))
        n = sum(bool(c.get("dispute")) for c in m.data["chronique"])
        m, _ = dire(m)
        self.assertEqual(sum(bool(c.get("dispute")) for c in recharger(m).data["chronique"]), n)

    def test_refus_atomiques_attendu(self):
        m = preparer()
        for champ, valeur in (("sujet", "lieu_inconnu"), ("attribut", "digue"), ("valeur", "peut-être")):
            contenu = {"type": "avis", "sujet": "echoppe", "attribut": "menace", "valeur": "oui", champ: valeur}
            avant = copy.deepcopy(m.data)
            with self.assertRaises(ErreurMonde) as erreur:
                paroles.verifier_contenus(m, [contenu])
            self.assertIn(champ, erreur.exception.attendu)
            self.assertIn(valeur, erreur.exception.attendu)
            self.assertEqual(m.data, avant)

    def test_cantonade_et_chuchotement(self):
        m = preparer()
        m, _ = dire(m, adresse="tous")
        m = recharger(m)
        for qui in ("aubin", "ilse", "marchand"):
            self.assertEqual(prevision(m, qui, "echoppe")["source"], "dit:joueur")
        m = preparer()
        m.joueur["position"] = [3, 4]
        saisie = "je chuchote à Gorm : l'eau va gagner la conduite basse"
        m, _ = paroles.preparer_parole(m, {"personnage": "marchand", "replique": "l'eau va gagner la conduite basse",
            "_intention": saisie, "contenu": [{"type": "avis", "sujet": "echoppe", "attribut": "menace", "valeur": "oui"}]})
        m = recharger(m)
        self.assertEqual(prevision(m, "marchand", "echoppe")["source"], "dit:joueur")
        self.assertIsNone(prevision(m, "ilse", "echoppe"))

    def test_observations_reelles_persistantes_sans_lire_le_niveau_cache(self):
        from donjon.spatial import memoriser
        from donjon.temps import ecouler
        m = preparer()
        m.joueur.update(salle="crypte", position=[1, 2])
        memoriser(m)
        ecouler(m, 15 * 600)
        memoriser(m)
        m = recharger(m)
        self.assertIsNotNone(eau.estimation(m, "joueur"))
        avant = social.avis_exprime(m, "joueur", "echoppe", True)
        m.data["crue"]["tirage"]["hauteur_pic_cm"] += 1000
        self.assertEqual(social.avis_exprime(m, "joueur", "echoppe", True), avant)
        self.assertEqual(avant["conviction"], 1)

    def test_gorm_a_reellement_vu_l_eau_baisser(self):
        from donjon.temps import ecouler
        m = preparer()
        pic = m.data["crue"]["tirage"]["minute_pic"]
        ecouler(m, (pic + 1 - m.data["minutes"]) * 600)
        eau.observer(m, "marchand", "echoppe")
        ecouler(m, 15 * 600)
        eau.observer(m, "marchand", "echoppe")
        self.assertLess(eau.estimation(m, "marchand")[2], 0)
        m, rapport = dire(recharger(m), salle="chambre_cloche")
        m = recharger(m)
        self.assertTrue(any(c.get("dispute") for c in m.data["chronique"]))
        self.assertIn("Non, l'eau ne menace pas", " ".join(rapport["faits"]))
        self.assertFalse(eau.menacee(m, "marchand", "chambre_cloche"))
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_console_mj_simule_puis_recharge(self):
        m = preparer()
        saisie = "je dis à Gorm : l'eau va gagner la conduite basse"
        m, sortie, _ = jouer(m, saisie, [
            parole("l'eau va gagner la conduite basse", ("avis", "echoppe", "menace", "oui"), personnage="marchand"),
            {**dialogue("Gorm t'écoute."), "faits": ["conversation_validee"]}], [verdicts(NEUTRE)])
        self.assertIn("l'eau va gagner la conduite basse", sortie)
        self.assertEqual(prevision(m, "marchand", "echoppe")["source"], "dit:joueur")
        self.assertEqual(rendu(m), rendu(recharger(m)))

    def test_operation_declaree_ne_peut_rester_propos_aux_mots_exacts(self):
        # La déclaration porte l'intention, indépendamment du premier contenu.
        for mots, salle, valeur in (("l'eau va gagner la conduite basse", "echoppe", "oui"),
                                    ("l'eau ne menace pas le refuge du relais", "antichambre", "non")):
            with self.subTest(mots=mots):
                m = preparer()
                saisie = "je dis à Gorm : " + mots
                correcte = parole(mots, ("avis", salle, "menace", valeur), personnage="marchand")
                omise = copy.deepcopy(correcte)
                omise["proposition"]["contenu"] = [{"type": "propos", "sujet": "", "attribut": "", "valeur": ""}]
                m, sortie, appels = jouer(m, saisie, [omise, correcte,
                    {**dialogue("Gorm t'écoute."), "faits": ["conversation_validee"]}], [verdicts(NEUTRE)])
                recharge = recharger(m)
                self.assertEqual(len(recharge.data["paroles_joueur"]), 1)
                self.assertEqual(prevision(recharge, "marchand", salle)["source"], "dit:joueur")
                self.assertIn(mots, sortie)
                self.assertNotIn("Le contenu proposé ne porte pas", sortie)
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
                self.assertEqual(rendu(m), rendu(recharge))


if __name__ == "__main__":
    unittest.main()
