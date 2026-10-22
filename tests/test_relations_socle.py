"""Le socle des relations (sous-étape 3a de ``docs/plan-relations.md``) : ``donjon/relations.py`` est le
seul accès à ce qu'un personnage éprouve envers un autre, et sa traduction de la croyance ``fiable``
redonne exactement les règles d'avant.

Le code ne nomme l'attribut ``fiable`` nulle part ailleurs (``AccesTests``) ; les cas de méfiance et
de confiance se vérifient de bout en bout, après rechargement (``ChaineTests``).
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


class TraductionTests(unittest.TestCase):
    """3a : la croyance vraie vaut confiance 70, absente 40 (un étranger), fausse 15 ; les autres axes
    restent à 0 ; les seuils redonnent le tout ou rien d'avant."""

    def test_trois_valeurs(self):
        m = relais()
        self.assertEqual(relations.envers(m, "marchand", "brune"),
                         {**relations.ETRANGER, "confiance": 70, "minute": 0, "source": "savoir"})
        self.assertEqual(relations.envers(m, "marchand", "joueur"),
                         {**relations.ETRANGER, "minute": None, "source": None})
        croire(m, "marchand", "brune", relations.FIABLE, False, "vu")
        self.assertEqual(relations.envers(m, "marchand", "brune")["confiance"], 15)
        for valeur, fie, mefie, dit in ((True, True, False, True), (False, False, True, False)):
            croire(m, "ilse", "aubin", relations.FIABLE, valeur, "vu")
            self.assertEqual((relations.se_fie(m, "ilse", "aubin"), relations.se_mefie(m, "ilse", "aubin"),
                              relations.fiable(m, "ilse", "aubin")), (fie, mefie, dit))
        self.assertEqual((relations.se_fie(m, "marchand", "joueur"), relations.se_mefie(m, "marchand", "joueur"),
                          relations.fiable(m, "marchand", "joueur")), (False, False, None))
        self.assertFalse(relations.en_veut(m, "marchand", "brune") or relations.craint(m, "marchand", "brune"))
        self.assertEqual(relations.doit(m, "marchand", "brune"), 0)

    def test_un_oui_dire_ne_remplace_pas_une_mefiance_vue(self):
        """Une cause apprise de seconde main (rumeur, aveu, geste entendu) ne remplace pas une méfiance
        constatée ; une autre cause la remplace (sa date et sa source avec)."""
        m = relais()
        relations.eprouver(m, "marchand", "brune", "vu_agir")
        m.data["minutes"] = 12
        relations.eprouver(m, "marchand", "brune", "rumeur", "dit:ilse", 0.56)
        self.assertEqual(relations.envers(m, "marchand", "brune")["source"], "vu")
        relations.eprouver(m, "marchand", "brune", "pousse")
        self.assertEqual(relations.envers(m, "marchand", "brune")["minute"], 12)
        relations.eprouver(m, "ilse", "aubin", "aveu", "entendu")
        self.assertEqual(relations.envers(m, "ilse", "aubin")["source"], "entendu")


class ChaineTests(unittest.TestCase):
    """Chaque lecture passe par le module, du constat à ce que voient les autres règles, après
    rechargement."""

    def test_gorm_voit_ses_vivres_aux_mains_de_brune(self):
        """Le cas réel des vols découverts : Gorm ne se fie plus à Brune ; il refuse sa demande
        d'office, le jet de persuasion la dessert, Luna lit qu'il la croit peu fiable."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["vivres"]["lieu"] = "brune"
        placer(m, "marchand", "antichambre", [6, 1])
        m, _ = attendre(recharger(m))
        self.assertTrue(relations.se_mefie(m, "marchand", "brune"))
        self.assertEqual(relations.envers(m, "marchand", "brune")["source"], "vu")
        self.assertIn("brune", relations.connus(m, "marchand"))
        self.assertEqual(accueil(m, "brune", "marchand"), "mefiance")
        _, dd = jet_persuasion(m, "marchand", "brune", 10)
        from donjon.caractere import modificateur
        self.assertEqual(dd, 10 + 6 + modificateur(m, "marchand", "VOL"))
        self.assertIn("croit que Brune est peu fiable", esprits_interlocuteurs(m, ["marchand"])["marchand"]["croit"])

    def test_gorm_reconnait_son_marteau_dans_la_main_du_joueur(self):
        """Même nature, envers le joueur : la méfiance se lit dans l'humeur (``vol.mefiance``)."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["marteau"].update(proprietaire="marchand", lieu="joueur")
        m.objets["marteau"].pop("position", None)
        placer(m, "marchand", "antichambre", [2, 4])
        regarder(m, "marchand", "joueur")
        m, texte = attendre(recharger(m))
        self.assertTrue(relations.se_mefie(m, "marchand", "joueur"))
        self.assertEqual(mefiance(m, "marchand"), 1)
        self.assertIn("Gorm, gardien du relais, semble méfiant.", texte)

    def test_la_part_servie_fait_confiance(self):
        """L'autre sens : qui reçoit une part de qui il sait l'avoir servi s'y fie (cause « nourri »)."""
        m = relais()
        croire(m, "brune", "marchand", relations.FIABLE, False, "vu")
        relations.eprouver(m, "brune", "marchand", "nourri")
        m = recharger(m)
        self.assertTrue(relations.se_fie(m, "brune", "marchand"))
        self.assertEqual(lire(m, "brune")["croyances"]["marchand"][relations.FIABLE]["valeur"], True)


if __name__ == "__main__":
    unittest.main()
