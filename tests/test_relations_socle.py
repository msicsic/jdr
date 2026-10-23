"""Le module reste le seul accès aux relations après la bascule 3b.

Les contrôles statiques de 3a subsistent ; les chaînes vérifient désormais les axes gradués.
"""
import ast
from pathlib import Path
import unittest

from donjon import relations
from donjon.echanges import accueil
from donjon.esprits import croire, lire
from donjon.paroles import esprits_interlocuteurs, jet_persuasion
from donjon.vol import mefiance
from tests.support import calme, regarder
from tests.test_social import attendre, placer, recharger, relais

RACINE = Path(__file__).resolve().parent.parent


def _sources():
    """Tout le code du jeu et de ses outils, hors des tests."""
    sources = [*RACINE.glob("*.py"), *(RACINE / "donjon").rglob("*.py"), *(RACINE / "tools").rglob("*.py")]
    assert len(sources) > 50, "Sources introuvables"
    return sources


def _fiable(noeud):
    """``noeud`` désigne l'attribut de la relation : le mot lui-même, ou ``FIABLE``."""
    return (isinstance(noeud, ast.Constant) and noeud.value == relations.FIABLE
            or isinstance(noeud, ast.Name) and noeud.id == "FIABLE"
            or isinstance(noeud, ast.Attribute) and noeud.attr == "FIABLE")


class AccesTests(unittest.TestCase):
    def test_aucun_seuil_numerique_d_axe_hors_relations(self):
        fautes = []
        for p in _sources():
            if p.name == "relations.py" and p.parent.name == "donjon":
                continue
            for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
                if not isinstance(n, ast.Compare):
                    continue
                termes = [n.left, *n.comparators]
                axes = {t.slice.value for t in termes if isinstance(t, ast.Subscript)
                        and isinstance(t.slice, ast.Constant) and t.slice.value in relations.AXES}
                nombres = [t.value for t in termes if isinstance(t, ast.Constant) and type(t.value) in (int, float)]
                # « confiance » sert aussi aux croyances, validées entre 0 et 1.
                if nombres and (axes - {"confiance"} or "confiance" in axes and any(v > 1 for v in nombres)):
                    fautes.append(f"{p.relative_to(RACINE)}:{n.lineno}")
        self.assertEqual(fautes, [])

    def test_seul_le_module_nomme_l_attribut(self):
        """Hors de ``relations``, le mot n'apparaît plus que par sa constante (``FIABLE``)."""
        fautes = []
        for p in _sources():
            if p.name == "relations.py" and p.parent.name == "donjon":
                continue
            for noeud in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
                if isinstance(noeud, ast.Constant) and noeud.value == relations.FIABLE:
                    fautes.append(f"{p.relative_to(RACINE)}:{noeud.lineno}")
        self.assertEqual(fautes, [])

    def test_personne_ne_lit_ni_n_ecrit_la_croyance_en_direct(self):
        """Ni ``croyances[x][FIABLE]``, ni ``.get(FIABLE)``, ni ``croire(…, FIABLE, …)`` hors de
        ``relations`` : la constante ne sert ailleurs qu'au mot de la parole (``paroles.ATTRIBUTS``, le
        contenu d'une affirmation) et à aiguiller vers le module (``esprits.croyance``, ``affirmer``)."""
        fautes = []
        for p in _sources():
            if p.name == "relations.py" and p.parent.name == "donjon":
                continue
            for noeud in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
                direct = (isinstance(noeud, ast.Subscript) and _fiable(noeud.slice)
                          or isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute)
                          and noeud.func.attr in ("get", "setdefault", "pop") and noeud.args and _fiable(noeud.args[0])
                          or isinstance(noeud, ast.Call) and getattr(noeud.func, "id", getattr(noeud.func, "attr", None))
                          in ("croire", "reviser", "_cru", "cru") and any(_fiable(a) for a in noeud.args))
                if direct:
                    fautes.append(f"{p.relative_to(RACINE)}:{noeud.lineno}")
        self.assertEqual(fautes, [])

    def test_plus_de_fiabilite_dans_voix(self):
        from donjon import voix
        self.assertFalse(hasattr(voix, "fiabilite"))


class ChaineTests(unittest.TestCase):
    def test_gorm_voit_ses_vivres_aux_mains_de_brune(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["vivres"]["lieu"] = "brune"
        placer(m, "marchand", "antichambre", [6, 1])
        m, _ = attendre(recharger(m))
        r = relations.envers(m, "marchand", "brune")
        self.assertEqual(r["confiance"], 25)
        self.assertTrue(relations.se_mefie(m, "marchand", "brune"))
        self.assertEqual(accueil(m, "brune", "marchand"), "mefiance")
        self.assertEqual(r["motifs"][-1]["type"], "vu_porter")
        self.assertIn("croit que Brune est peu fiable", esprits_interlocuteurs(m, ["marchand"])["marchand"]["croit"])
        self.assertNotIn(relations.FIABLE, lire(m, "marchand")["croyances"].get("brune", {}))

    def test_gorm_reconnait_son_marteau_dans_la_main_du_joueur(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["marteau"].update(proprietaire="marchand", lieu="joueur")
        m.objets["marteau"].pop("position", None)
        placer(m, "marchand", "antichambre", [2, 4])
        regarder(m, "marchand", "joueur")
        m, texte = attendre(recharger(m))
        self.assertEqual(relations.envers(m, "marchand", "joueur")["confiance"], 0)
        self.assertEqual(mefiance(m, "marchand"), 1)
        self.assertIn("fait des gestes brusques", texte)
        self.assertNotIn("humeur", m.objets["marchand"])


if __name__ == "__main__":
    unittest.main()
