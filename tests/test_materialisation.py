import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.mj import MJOpenAI
from donjon.monde import Monde, nouveau_monde
from donjon.operations import etape, sequence


def portee(nom, texte):
    def ligne(fragment, representation):
        return {"representation": representation, "mobilite": [], "placement": "aucun",
                "impact_scenario": "aucun", "capacites": [],
                "fragments": [{"texte": fragment, "portee": "sujet", "preuve": "", "motif": ""}]}
    return {"usages": [{"perception_requise": False, "indice": False, "motif": ""}], "descriptions": [ligne(nom, "objet"), ligne(texte, "aspect")]}


def segments(*verdicts):
    return {"segments": [{"indice": i, "verdict": v, "sources": [], "locuteur": "", "citation": "",
                          "entites": [], "motif": ""} for i, v in enumerate(verdicts)]}


def partie(ambiance):
    m = nouveau_monde()
    m.data["ambiances"] = {"antichambre": [{"texte": ambiance[0], "entites": ambiance[1], "revision": 0}]}
    return m


class MaterialisationTests(unittest.TestCase):
    def test_element_d_ambiance_ramasse_devient_un_objet_pris(self):
        # Une ambiance déjà affichée évoque des gravats ; le joueur veut en prendre un.
        m = partie(("Des gravats jonchent le sol près de l'entrée.", ["gravats au sol"]))
        texte_objet = "Un éclat de pierre grise, tranchant sur un bord."
        vus = {}

        def repondre(instructions, entree, intention, fonction, schema):
            if fonction == "auditer_portee":
                return portee("gravat", texte_objet)
            if fonction == "auditer_action":
                return {"conforme": True, "motif": ""}
            faits = entree["faits"]
            if "premier" not in vus:
                vus["premier"] = faits.get("ambiance_ciblee")
                return {"mode": "etablir_faits", "texte": "", "faits": ["ambiance_ciblee"],
                        "proposition": {"ajouts": [{
                            "type": "objet", "ancrage": "antichambre_sol", "nom": "gravat",
                            "genre": "m", "texte": texte_objet, "materiau": "pierre",
                            "masse": 0.4, "mobile": True, "relation": "pose", "capacites": []}]}}
            # Réexamen sur le monde qui contient le gravat : l'intention reprend sans être répétée.
            ids = [k[6:] for k, v in faits.items() if k.startswith("objet:") and v.get("nom") == "gravat"]
            vus["reexamen"] = ids
            return {"mode": "action", "texte": "", "faits": ["objet:" + ids[0]],
                    "proposition": sequence(etape("deplacer", ids[0], "joueur"))}

        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=repondre),
                  patch("builtins.input", side_effect=["je ramasse un gravat", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--recit-moteur", "--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertEqual(vus["premier"][0]["entites"], ["gravats au sol"])
        self.assertEqual(len(vus["reexamen"]), 1)
        gravat = reprise.objets[vus["reexamen"][0]]
        self.assertEqual(gravat["lieu"], "joueur")
        self.assertIn("gravat", sortie.getvalue())
        self.assertIn(gravat["id"], [o["id"] for o in reprise.objets.values() if reprise.est_porte(o["id"])])

    def test_element_non_manipulable_ne_cree_rien(self):
        m = partie(("Une odeur de vase monte du sol.", ["odeur de vase"]))
        reponse = "Une odeur ne se ramasse pas. Elle reste dans l'air humide."
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            objets = set(m.objets)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=[
                      {"mode": "dialogue", "texte": reponse, "faits": ["ambiance_ciblee"], "proposition": None},
                      segments("neutre", "ambiance")]) as appel,
                  patch("builtins.input", side_effect=["je prends l'odeur de vase", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--save", str(chemin), "--connexion", "api"]), 0)
            reprise = Monde.charger(chemin)
        self.assertIn("ambiance_ciblee", appel.call_args_list[0].args[1]["faits"])
        self.assertIn(reponse, sortie.getvalue())
        self.assertEqual(set(reprise.objets), objets)
        self.assertFalse(reprise.data["journal"])


if __name__ == "__main__":
    unittest.main()
