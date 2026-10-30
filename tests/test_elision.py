"""Accord commun des désignations : français, projection, parole et nouvelle rechargées."""
from donjon.emissions import joueur as emissions_joueur
import re
import unittest
from unittest.mock import patch

from donjon.francais import complement_de, groupe_nominal, inserer_designation
from donjon.noms import public, texte
from donjon.paroles import preparer_parole, annonce
from donjon.social import faire_entendre, phrase, recevoir
from tests.test_parole_corrections import banc
from tests.test_tensions import recharger
from tests.test_audits_attendu import jouer, rapport, ligne
from tests.test_repli_et_appel import dialogue, parole


class FrancaisTests(unittest.TestCase):
    def test_formes_et_capitales(self):
        for nom, de, a in (
            ("Aubin", "d'Aubin", "à Aubin"),
            ("Brune", "de Brune", "à Brune"),
            ("Le vieil homme voûté", "du vieil homme voûté", "au vieil homme voûté"),
            ("la batelière", "de la batelière", "à la batelière"),
            ("les gardes", "des gardes", "aux gardes"),
            ("l'homme", "de l'homme", "à l'homme"),
            ("L’étrangère", "de l’étrangère", "à l’étrangère"),
            ("un homme", "d'un homme", "à un homme"),
            ("une voix", "d'une voix", "à une voix"),
            ("des voyageurs", "de voyageurs", "à des voyageurs"),
        ):
            with self.subTest(nom=nom):
                self.assertEqual(groupe_nominal(nom, "de"), de)
                self.assertEqual(groupe_nominal(nom, "à"), a)
                self.assertEqual(groupe_nominal(nom, "de", debut=True), de[:1].upper() + de[1:])
        self.assertEqual(complement_de({"nom": "arche", "genre": "f"}), "de l'arche")

    def test_liaison_de_la_phrase_reprise_sans_doubler_l_article(self):
        motif = re.compile(r"(?<!\w)personne_1(?!\w)")
        for source, attendue in (
            ("Je parle de personne_1.", "Je parle du vieil homme."),
            ("Je parle d’personne_1.", "Je parle du vieil homme."),
            ("Je parle de l'personne_1.", "Je parle du vieil homme."),
            ("Je parle à personne_1.", "Je parle au vieil homme."),
            ("Je parle à l'personne_1.", "Je parle au vieil homme."),
            ("Je vois le personne_1.", "Je vois le vieil homme."),
            ("personne_1 arrive. personne_1 repart.", "Le vieil homme arrive. Le vieil homme repart."),
        ):
            with self.subTest(source=source):
                self.assertEqual(inserer_designation(source, motif, "le vieil homme"), attendue)


class ChaineTests(unittest.TestCase):
    def test_cas_reel_chuchotement_echanges_jusqu_au_dossier_mj_et_recharge(self):
        m = banc("echanges")
        from donjon.noms import apprendre
        apprendre(m, "joueur", "brune")
        mots = "Je me méfie d'Aubin."
        r, sortie, appels = jouer(m, "je chuchote à Brune que je me méfie d'Aubin", [
            parole(mots, ("propos", "", "", ""), personnage="brune"),
            dialogue("Brune t'écoute.")],
            [rapport(ligne("mecanique", sources=["conversation_validee"]))])
        validee = next(e["faits"]["conversation_validee"] for f, e in appels
                       if f == "repondre_au_joueur" and "conversation_validee" in e["faits"])
        self.assertEqual(validee["sujet"], "Je me méfie du vieil homme voûté.")
        self.assertIn("Tu chuchotes à Brune : « " + mots + " »", sortie)
        r = recharger(r)
        self.assertEqual(emissions_joueur(r)[-1]["texte"], mots)
        self.assertEqual(emissions_joueur(r)[-1]["auditeurs"], ["brune"])
        self.assertIn(mots, str(r.data["conversation"]))
        self.assertNotIn("aubin", r.data["noms_connus"])
        self.assertEqual(public(r, {"sujet": mots})["sujet"], validee["sujet"])

    def test_nouvelle_sur_une_personne_designee_entendue_et_rechargee(self):
        from donjon.esprits import lire
        m = banc("echanges")
        # Corvus comprend l'échange, mais Brune désigne un corps dont elle ignore le nom.
        from donjon.noms import apprendre
        for id in ("brune", "ilse", "aubin"):
            apprendre(m, "joueur", id)
        lire(m, "brune")["noms"] = ["ilse"]
        m.objets["brune"]["connait_noms"] = ["ilse"]
        noyau = {"type": "dette_niee", "auteur": "ilse", "victime": "aubin", "montant": 2}
        nouvelle = phrase(m, noyau, "brune")
        lignes = []
        from donjon.monde import Monde
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(recevoir(m, "aubin", "brune", {"type": "rumeur", "evenement": noyau, "rang": 0}), "crue")
            faire_entendre(m, "brune", "aubin", "Brune dit que " + nouvelle + ".", ["ilse", "aubin"],
                          lignes, [{"type": "rumeur", "evenement": noyau, "rang": 0}])
        m = recharger(m)
        self.assertTrue(any(s["type"] == "rumeur" and s["evenement"] == noyau
                            for s in lire(m, "aubin")["memoire"]))
        rendu = texte(m, "\n".join(lignes))
        self.assertIn("doit au vieil homme voûté", rendu)
        self.assertNotIn("Aubin", rendu)
        self.assertNotIn("aubin", lire(m, "brune")["noms"])

    def test_adresse_a_une_designation_et_citations_conservees(self):
        m = banc("echanges")
        m.joueur["orientation"] = "sud"
        r, bilan = preparer_parole(m, {"personnage": "personne_1", "replique": "Bonsoir.",
            "contenu": [{"type": "propos"}], "_intention": "je dis au vieil homme : Bonsoir."})
        r = recharger(r)
        self.assertIn("Tu dis au vieil homme voûté", annonce(r, bilan))
        self.assertIn("au vieil homme voûté", bilan["issue"])
        self.assertEqual(texte(r, "Aubin dit : « d'Aubin »", citations=True),
                         "Le vieil homme voûté dit : « d'Aubin »")
        self.assertEqual(public(r, "Je parle à personne_1 de personne_1."),
                         "Je parle au vieil homme voûté du vieil homme voûté.")
        self.assertEqual(public(r, {"personnage": "personne_1"}), {"personnage": "personne_1"})
        self.assertEqual(public(r, {"objet:personne_1": {}}), {"objet:personne_1": {}})

    @patch("donjon.agendas._naissances", return_value=None)
    def test_don_et_promesse_a_un_corps_designe_apres_recharge(self, _naissance):
        from donjon import agendas
        from donjon.moteur import Moteur, proposition
        from donjon.noms import designation
        for id, orientation, complement in (("aubin", "sud", "au vieil homme voûté"),
                                              ("brune", "ouest", "à la femme sèche")):
            with self.subTest(id=id):
                m = banc("echanges")
                m.joueur["orientation"] = orientation
                m.objets["cire"].update(lieu="joueur", proprietaire="joueur")
                m = recharger(m)
                plan = Moteur(m).preparer(proposition("remettre", "cire", designation(m, id)))
                self.assertIn(complement, plan.titre)
                rendu = Moteur(m).executer(plan)
                agendas.prendre(m, "joueur", {"pour": id, "condition": {"objet": "brasero", "allume": True},
                                               "minute": m.data["minutes"]})
                m = recharger(m)
                self.assertEqual(m.objets["cire"]["lieu"], id)
                self.assertIn(complement, rendu)
                self.assertIn("Tu as promis " + complement, agendas.promesses_visibles(m)[0])


if __name__ == "__main__":
    unittest.main()
