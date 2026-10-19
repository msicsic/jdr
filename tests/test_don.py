"""Donner un objet à un personnage présent ; une explication de refus ne fait parler personne."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.defi import nouveau_defi
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition


def relais_avec_cloche():
    """Cas d'une partie : la cloche rapportée au refuge, Gorm à côté, aucune mission au Relais."""
    m = nouveau_defi(1985)
    m.data["mode_cases"] = False
    m.joueur["salle"] = m.objets["marchand"]["lieu"]
    m.objets["cloche"]["lieu"] = "joueur"
    return m


class DonTests(unittest.TestCase):
    def test_donner_la_cloche_a_gorm_sans_mission(self):
        m = relais_avec_cloche()
        self.assertEqual(m.data["missions"], {})
        plan = Moteur(m).preparer(proposition("remettre", "cloche", "marchand"))
        or_avant = m.joueur["or"]
        Moteur(m).executer(plan)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "partie.json"
            m.sauver(chemin)
            recharge = Monde.charger(chemin)
        cloche = recharge.objets["cloche"]
        self.assertEqual((cloche["lieu"], cloche["proprietaire"]), ("marchand", "marchand"))
        self.assertEqual(recharge.joueur["or"], or_avant)
        souvenirs = recharge.data["esprits"]["marchand"]["memoire"]
        self.assertTrue(any(s["type"] == "don" and s["objet"] == "cloche" for s in souvenirs))

    def test_sans_destinataire_present_le_don_est_refuse(self):
        m = relais_avec_cloche()
        m.joueur["salle"] = next(s for s in m.data["salles"] if s != m.objets["marchand"]["lieu"]
                                 and not any(o["type"] == "personnage" and o["lieu"] == s for o in m.objets.values()))
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(proposition("remettre", "cloche", "marchand"))
        self.assertIn("outil = le personnage qui reçoit", refus.exception.attendu)


class ExplicationTests(unittest.TestCase):
    def test_une_explication_de_refus_ne_fait_pas_parler_un_personnage(self):
        # Cas d'une partie : Gorm « disait » au joueur un motif de refus inventé.
        texte = "Gorm te répond : « Pour me la remettre, dis-le-moi clairement. »"
        citation = "Pour me la remettre, dis-le-moi clairement."
        parole = {"segments": {"0": {"verdict": "parole", "sources": [], "locuteur": "marchand",
                                     "citation": citation, "entites": [], "motif": ""}}}
        sobre = "Gorm ne prend pas encore la cloche : rien ne s'est échangé."
        neutre = {"segments": {"0": {"verdict": "neutre", "sources": [], "locuteur": "", "citation": "",
                                     "entites": [], "motif": ""}}}
        faits = {"interlocuteurs": {"marchand": {"nom": "Gorm"}},
                 "retour_moteur": {"propositions_refusees": [["remettre", "refus"]]}}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler_brut", side_effect=[
                {"mode": "dialogue", "texte": texte, "faits": [], "proposition": None}, parole,
                {"mode": "dialogue", "texte": sobre, "faits": [], "proposition": None}, neutre]) as appel:
            reponse = mj._appeler("instr", {"faits": faits, "conversation": [], "message": "je donne la cloche"},
                                  "je donne la cloche", "repondre_au_joueur", {})
        self.assertEqual(reponse["texte"], sobre)
        self.assertEqual(appel.call_count, 4)


if __name__ == "__main__":
    unittest.main()
