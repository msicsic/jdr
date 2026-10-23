import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.improvisation import issue, proposition as improviser
from donjon.mj import MJOpenAI
from donjon.monde import ErreurMonde, Monde, nouveau_monde


def audit(texte):
    from donjon.narration import segments
    return {"segments": [{"indice": i, "verdict": "ambiance", "sources": [], "locuteur": "",
                          "citation": "", "entites": [], "motif": ""}
                         for i, _ in enumerate(segments(texte))]}


def jouer(saisies, recit, proposition, d20=None):
    """Joue les saisies avec un MJ simulé ; recit est le texte de narration ou une exception."""
    vus = []

    def repondre(instructions, entree, intention, fonction, schema):
        if fonction == "auditer_action":
            return {"conforme": True, "motif": ""}
        if fonction == "auditer_narration":
            return audit(recit)
        if "resultat_resolu" in entree["faits"]:
            vus.append(entree["faits"]["resultat_resolu"])
            if isinstance(recit, Exception):
                raise recit
            return {"mode": "dialogue", "texte": recit, "faits": ["resultat_resolu"], "proposition": None}
        return {"mode": "action", "texte": "", "faits": [], "proposition": proposition}

    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        nouveau_monde().sauver(chemin)
        correctifs = [patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                      patch.object(MJOpenAI, "_appeler_brut", side_effect=repondre),
                      patch("builtins.input", side_effect=[*saisies, "quitter"])]
        if d20 is not None:
            correctifs.append(patch.object(Monde, "d20", return_value=d20))
        with patch("sys.stdout", io.StringIO()) as sortie:
            for c in correctifs:
                c.start()
            try:
                code = jeu.main(["--console", "--save", str(chemin), "--connexion", "api"])
            finally:
                for c in reversed(correctifs):
                    c.stop()
        return code, sortie.getvalue(), Monde.charger(chemin), vus


ETIREMENT = improviser("S'étirer", issue("Brouillon non affiché.", []), approche="effort")


class RecitResultatTests(unittest.TestCase):
    def test_geste_raconte_par_luna_apres_application(self):
        # Cas réel du banc : « je m'étire » affichait « Tu réalises ce geste d'effort. »
        recit = "Tu étires longuement les bras au-dessus de la tête, et tes épaules se dénouent."
        code, sortie, reprise, vus = jouer(["je m'étire"], recit, ETIREMENT)
        self.assertEqual(code, 0)
        self.assertIn(recit, sortie)
        self.assertNotIn("Tu réalises ce geste.", sortie)
        self.assertEqual(vus[0]["intention"], "je m'étire")
        # Le journal garde le résultat du moteur ; la conversation garde ce que le joueur a lu.
        self.assertIn("Tu réalises ce geste.", reprise.data["journal"][-1]["faits"])
        self.assertEqual(reprise.data["conversation"][-1]["reponse"], recit)
        self.assertEqual(reprise.data["narrations_mj"][-1]["texte"], recit)

    def test_le_recit_recoit_les_gestes_accomplis(self):
        """Banc Luna : « je ramasse la bobine » racontée « Tu ramasses la bobine » était jugée
        contradictoire, le résultat ne disant que « Tu portes maintenant… » ; le geste exécuté est
        désormais un fait du résultat. Une manœuvre arrêtée au premier échec ne donne que ses
        étapes exécutées."""
        _, _, _, vus = jouer(["je m'étire"], "Tu t'étires.", ETIREMENT)
        # Le geste dans les mots du moteur ; la manière demandée reste dans l'intention.
        self.assertEqual((vus[0]["gestes"], vus[0]["intention"]), (["Geste."], "je m'étire"))
        from donjon.moteur import Moteur, gestes_accomplis
        m = nouveau_monde()
        etape = lambda op, cible, **k: {"operation": op, "cible": cible, "destination": "", "outil": "",
                                        "methode": "simple", "difficulte": 0, **k}
        prises = [o for o, x in m.objets.items() if x.get("mobile") and x["lieu"] == m.joueur["salle"]
                  and m.accessible(o)]
        moteur = Moteur(m)
        plan = moteur.preparer({"action": "composer", "justification": "", "etapes": [
            etape("deplacer", prises[0], destination="joueur")]})
        moteur.executer(plan)
        self.assertEqual(gestes_accomplis(plan, m), [plan.plans[0].titre])
        self.assertTrue(plan.plans[0].titre.startswith("Prendre "))

    def test_nombre_invente_rend_le_texte_du_moteur(self):
        recit = "Tu t'étires et perds 5 PV dans un faux mouvement."
        _, sortie, reprise, _ = jouer(["je m'étire"], recit, ETIREMENT)
        self.assertNotIn(recit, sortie)
        self.assertIn("Tu réalises ce geste.", sortie)
        self.assertEqual(reprise.joueur["pv"], nouveau_monde().joueur["pv"])
        self.assertEqual(reprise.data["conversation"][-1]["reponse"], "Tu réalises ce geste.")

    def test_panne_du_recit_rend_le_texte_du_moteur_sans_rejouer(self):
        _, sortie, reprise, _ = jouer(["je m'étire"], ErreurMonde("réseau"), ETIREMENT)
        self.assertIn("Tu réalises ce geste.", sortie)
        self.assertEqual(len(reprise.data["journal"]), 1)

    def test_tenter_raconte_la_demande_d_origine(self):
        saut = improviser("Bondir", issue("Brouillon.", []), issue("Brouillon.", []),
                         approche="adresse", stat="DEX", difficulte=12)
        recit = "Tu prends ton élan et bondis souplement."
        _, sortie, reprise, vus = jouer(["je bondis sur place", "tenter"], recit, saut, d20=20)
        self.assertEqual(vus[0]["intention"], "je bondis sur place")
        self.assertIn(recit, sortie)
        self.assertTrue(reprise.data["journal"][-1]["reussite"])

    def test_option_recit_moteur_sans_appel(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=lambda *a: (
                      {"conforme": True, "motif": ""} if a[3] == "auditer_action" else
                      {"mode": "action", "texte": "", "faits": [], "proposition": ETIREMENT})) as appel,
                  patch("builtins.input", side_effect=["je m'étire", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                jeu.main(["--recit-moteur", "--console", "--save", str(chemin), "--connexion", "api"])
        self.assertEqual(appel.call_count, 2)
        self.assertIn("Tu réalises ce geste.", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
