"""Une lacune de profondeur se complète, sans inventer une impossibilité."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.support import sans_indices_soupcon_passifs

DATA = Path(__file__).parent / "data"


def empreinte(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, default=repr).encode()).hexdigest()


def encoder(r):
    if r is None:
        return None
    return json.loads(json.dumps({"cout_hex": r[0].hex(), "etapes": r[1], "salle": r[2].salle,
                                  "portes": sorted(r[2].portes), "allure": r[2].allure,
                                  "faits": sorted([(list(k), v) for k, v in r[2].faits.items()], key=repr)}))


class CompletionTests(unittest.TestCase):
    def setUp(self):
        p._MEMOIRE.clear()
        p._GRAPHES.clear()
        p._IMPOSSIBLES.clear()

    def test_captures_reelles_plans_et_absences_prix_recharge_et_rendu(self):
        attendu = json.loads((DATA / "profondeurs-preuve/contrats.json").read_text(encoding="utf8"))
        for nom, qui, chemin in (
                ("joss-622-epuise", "joss", "profondeurs-preuve/joss-622-epuise.json.gz"),
                ("tilo-566-epuise", "tilo", "profondeurs-preuve/tilo-566-epuise.json.gz"),
                ("joss-622-plan", "joss", "profondeurs-preuve/joss-622-plan.json.gz"),
                ("mine-480", "remy", "cout-12h/mine-1985-480.json.gz")):
            with self.subTest(capture=nom), tempfile.TemporaryDirectory() as dossier:
                self.setUp()
                m = Monde(json.loads(gzip.decompress((DATA / chemin).read_bytes())))
                with p.diagnostics() as ds:
                    for _ in range(3):
                        p._MEMOIRE.clear()
                        r = p.chercher(m, qui, p.a_mange, nom="faim", memo=["besoin", "faim"],
                                       emplois=("manger",), motif="faim")
                        self.assertEqual(encoder(r), attendu[nom]["resultat"])
                if r is None:
                    self.assertEqual(ds[-1]["issue"], "impossible")
                    self.assertEqual(ds[-1]["noeuds"], 0)
                    from donjon import caractere
                    prix = caractere.prix_faute
                    def moins_cher(*a, **k):
                        x = prix(*a, **k)
                        return None if x is None else x * .9
                    with patch.object(caractere, "prix_faute", moins_cher), p.diagnostics() as d:
                        self.assertIsNone(p.chercher(m, qui, p.a_mange, nom="faim", memo=["besoin", "faim"],
                                                    emplois=("manger",), motif="faim"))
                    self.assertEqual(d[-1]["issue"], "impossible")
                    self.assertEqual(d[-1]["noeuds"], 0)
                fichier = Path(dossier) / "monde.json"
                m.sauver(fichier)
                recharge = Monde.charger(fichier)
                self.assertEqual(m.data, recharge.data)
                historique = sans_indices_soupcon_passifs(recharge)
                for e in historique['esprits'].values():
                    # 360 : provenance initiale ajoutée à la migration, comme
                    # dans l'oracle d'étapes. Le monde complet, provenance
                    # comprise, vient d'être comparé après sauvegarde/recharge.
                    self.assertIsInstance(e.pop('faits_initiaux'), dict)
                    # 332 ajoute ce registre à toute sauvegarde. Aucun regard
                    # suivi dans ces captures : conserver l'oracle historique
                    # après contrôle strict de sa vacuité, jamais d'un acte.
                    self.assertEqual(e.pop('regards_suivis', {}), {})
                    # L'oracle précède le service spontané. Seuls ses registres
                    # vides peuvent être exclus, jamais une tentative réelle.
                    self.assertEqual(e.pop('recours_services', []), [])
                    self.assertEqual(e.pop('recours_intermediaires', []), [])
                    self.assertIsNone(e.pop('service_en_cours', None))
                self.assertEqual(empreinte(historique), attendu[nom]["monde"])
                self.assertEqual(empreinte((regarder(recharge), scene_percue(recharge))), attendu[nom]["rendu"])

    def test_profondeur_minimale_et_permission_peuvent_reveler_un_but(self):
        e = {s: p.Etat(s, (), {}) for s in ("s", "a", "b", "x", "fin")}
        arcs = {"s": [("a", 0), ("x", 1)], "a": [("b", 0)], "b": [("x", 0)], "x": [("fin", 0)], "fin": []}
        for permission, trouve in ((None, False), (10, True)):
            g = {e[s]: [False, None, 0, [(f, 1, [], e[t], 0, False, 0) for t, f in arcs[s]], False]
                 for s in ("s", "a", "b")}
            g[e["x"]] = [False, None, None, None, False]  # coupé à la profondeur 3 en coût
            profondeurs = []
            def completer(etat, n, noeud):
                if noeud is None:
                    noeud = [etat.salle == "fin", None, 0, [], False]
                    g[etat] = noeud
                if n < 3 and noeud[3] is None:
                    profondeurs.append(n)
                    noeud[3] = [(0, 1, [], e["fin"], 0, False, 0)]
                return noeud, None
            r = p._parcours(SimpleNamespace(menacees=set()), g, e["s"], 3, permission, False, completer=completer)
            self.assertEqual(r[0], not trouve)
            self.assertEqual(profondeurs, [1] if trouve else [])
            if trouve:
                self.assertEqual(r[2], "but")

    def _scene(self):
        m = Monde(json.loads(gzip.decompress((DATA / "profondeurs-preuve/joss-622-epuise.json.gz").read_bytes())))
        v = p.Vue(m, "joss")
        v._explore_furtif = False
        e = p.depart(m, "joss", v)
        return v, e

    def _preuve(self, v, e, but, g):
        comptes = {"ajoutes": 0, "completes": 0, "enrichis": 0}
        def preparer(nom):
            return p._preparer_graphe_preuve(v, e, but, {}, 3, False, g.get(nom, {}), nom == "sombre", comptes)
        return p._sans_plan(v, e, but, 3, 1, False, g, False, preparer=preparer), comptes

    def test_decouverte_lumiere_exige_aussi_le_graphe_lumineux(self):
        v, e = self._scene()
        v.peur = 0
        v._lumiere_lue = False
        def but(vue, etat):
            if not vue.emploie_lumiere:
                vue._lumiere_lue = True
            return bool(etat.fait("fini"))
        fin = e.apres(faits=[(("fini",), True)])
        with patch.object(p, "_suites", lambda *a: [(0, 1, [], fin, 0, False, 0)]):
            r, _ = self._preuve(v, e, but, {})
        self.assertFalse(r[0])
        self.assertEqual(r[2], "but")
        self.assertFalse(v._lumiere_lue)

    def test_discretion_nouvelle_ne_publie_pas_de_graphe_tronque(self):
        v, e = self._scene()
        g = {"sombre": {e: [False, None, None, None, False]}}
        def suites(vue, *a):
            vue._discretion_lue = True
            return []
        with patch.object(p, "_suites", suites):
            r, _ = self._preuve(v, e, lambda *a: False, g)
        self.assertEqual(r[2], "discretion")
        self.assertIsNone(g["sombre"][e][3])

    def test_sortie_differee_admissible_est_un_but_pas_une_absence(self):
        v, e = self._scene()
        fin = e.apres(faits=[(("estimation",), True)])
        differe = p.SuiteDifferee(0, lambda v: [(0, 0, [], fin)], ())
        with patch.object(p, "_suites", lambda *a: [differe]):
            r, _ = self._preuve(v, e, lambda *a: False, {})
        self.assertFalse(r[0])
        self.assertEqual(r[2], "but")

    def test_borne_de_recherche_ne_declenche_pas_le_certificat(self):
        v, _ = self._scene()
        with patch.object(p, "_sans_plan", wraps=p._sans_plan) as prouver:
            with p.diagnostics() as ds:
                p.chercher(v.monde, v.id, p.a_mange, nom="faim", memo=["borne-test"],
                           emplois=("manger",), motif="faim", noeuds=1)
        self.assertEqual(ds[-1]["issue"], "borne")
        prouver.assert_not_called()

    def test_verifier_certificat_refait_toujours_la_complete(self):
        v, _ = self._scene()
        appels = []
        def explorer(*a, **k):
            appels.append(a[5])
            return None, 0, 0, 0
        with patch.object(p, "_explorer", explorer):
            p._verifier(v.monde, v.id, v, lambda *a: False, None, None, 8, p.NOEUDS,
                        1, False, None, None, "preuve", None, False, "impossibilité")
        self.assertEqual(appels, [p.NOEUDS, p.REFERENCE])

    def test_verifier_refuse_un_certificat_si_la_complete_trouve_un_plan(self):
        v, e = self._scene()
        def explorer(*a, **k):
            return ((1, [], e) if a[5] == p.REFERENCE else None), 0, 0, 0
        with patch.object(p, "_explorer", explorer), self.assertRaisesRegex(AssertionError, "certificat, complète"):
            p._verifier(v.monde, v.id, v, lambda *a: False, None, None, 8, p.NOEUDS,
                        1, False, None, None, "preuve", None, False, "impossibilité")


if __name__ == "__main__":
    unittest.main()
