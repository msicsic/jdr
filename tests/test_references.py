"""Cache des références par commit : rempli puis réemployé sans rejouer, clé, --sans-cache,
référence non résolue jamais rangée ; pour comparer_bancs, banc_multi et la purge."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import banc_multi  # noqa: E402
import comparer_bancs as outil  # noqa: E402
import references  # noqa: E402


def depot(dossier):
    """Un petit dépôt git à un commit, sur la branche main."""
    racine = Path(dossier) / "depot"
    racine.mkdir()
    references.git(racine, "init", "-b", "main")
    (racine / "tools").mkdir()
    (racine / "tools" / "banc_parties.py").write_text("# outil de banc\n", encoding="utf-8")
    references.git(racine, "add", ".")
    commettre(racine, "initial")
    return racine


def commettre(racine, message):
    references.git(racine, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                   "commit", "--allow-empty", "-m", message)
    return references.git(racine, "rev-parse", "HEAD")


class Environnement(unittest.TestCase):
    def setUp(self):
        temporaire = tempfile.TemporaryDirectory()
        self.addCleanup(temporaire.cleanup)
        self.tmp = Path(temporaire.name)
        self.racine = depot(self.tmp)
        self.cache = self.tmp / "cache"
        environnement = patch.dict(os.environ, {"SEUIL_REFERENCES": str(self.cache)})
        environnement.start()
        self.addCleanup(environnement.stop)
        self.commit = references.git(self.racine, "rev-parse", "HEAD")


class ComparerBancsCacheTests(Environnement):
    def setUp(self):
        super().setUp()
        self.lancees = []

        def lancer(arbre, config, dossier, nom):
            self.lancees.append((nom, [tuple(n) for n in config["nuits"]]))
            return [{"scenario": s, "graine": g, "plantage": None, "secondes": 1.0, "secondes_cpu": 0.5,
                     "donnees": {"chronique": [], "mesures": {"x": g}}, "etat_final": f"{s}{g}"}
                    for s, g in config["nuits"]]
        remplacement = patch.object(outil, "lancer", lancer)
        remplacement.start()
        self.addCleanup(remplacement.stop)

    def config(self, **options):
        return {"empreintes": True, "heures": 2, "depart": "tire", "verifier": False, "joueurs": outil.JOUEURS,
                "scenarios": ["relais", "mine"], "graines": [1985, 7], "processus": 2, **options}

    def nuits(self, commit, config, cache=True):
        arbres = []
        resultat = outil.nuits_du_cote(lambda: arbres.append(1) or self.racine, commit, config, self.tmp,
                                       "reference", self.cache if cache else None)
        return resultat, len(arbres)

    def test_cache_rempli_puis_reemploye_sans_rejouer(self):
        premieres, arbres = self.nuits(self.commit, self.config())
        self.assertEqual(len(self.lancees[0][1]), 4)
        self.assertEqual(arbres, 1)
        fichiers = sorted((self.cache / self.commit / "comparer_bancs").rglob("*.json"))
        self.assertEqual(len(fichiers), 4)
        self.assertIn("relais-g1985-h2.0-tire-chambre_cloche-empreintes.json", [f.name for f in fichiers])
        secondes, arbres = self.nuits(self.commit, self.config())
        self.assertEqual(len(self.lancees), 1, "la seconde fois ne rejoue rien")
        self.assertEqual(arbres, 0, "aucun worktree quand tout vient du cache")
        self.assertTrue(all(n["cache"] for n in secondes))
        self.assertEqual([(n["scenario"], n["graine"]) for n in secondes],
                         [(n["scenario"], n["graine"]) for n in premieres])
        self.assertIsNone(outil.comparer_identite(premieres, secondes))

    def test_seules_les_nuits_manquantes_se_jouent(self):
        self.nuits(self.commit, self.config(graines=[7]))
        self.nuits(self.commit, self.config(graines=[1985, 7, 42]))
        self.assertEqual(self.lancees[1][1], [("relais", 1985), ("relais", 42), ("mine", 1985), ("mine", 42)])

    def test_cle_differente_si_un_parametre_change(self):
        self.nuits(self.commit, self.config())
        variantes = {"heures": 4, "depart": "fixe", "verifier": True, "empreintes": False, "localiser": True,
                     "joueurs": {**outil.JOUEURS, "mine": "bureau"}}
        for cle, valeur in variantes.items():
            with self.subTest(cle=cle):
                avant = len(self.lancees)
                self.nuits(self.commit, self.config(**{cle: valeur}))
                attendues = 2 if cle == "joueurs" else 4  # la salle du joueur ne change que la mine
                self.assertEqual(len(self.lancees[avant][1]), attendues)
        self.nuits(self.commit, self.config(processus=5))
        self.assertEqual(len(self.lancees), len(variantes) + 1, "le nombre de processus n'est pas dans la clé")

    def test_une_autre_observation_rejoue(self):
        self.nuits(self.commit, self.config())
        with patch.object(outil, "instrumentation", lambda: "autre"):
            self.nuits(self.commit, self.config())
        self.assertEqual(len(self.lancees), 2)

    def test_sans_cache_ni_lu_ni_range(self):
        self.nuits(self.commit, self.config())
        self.nuits(self.commit, self.config(), cache=False)
        self.assertEqual(len(self.lancees), 2)
        (fichier,) = [f for f in self.cache.rglob("relais-g7-*.json")]
        fichier.unlink()
        self.nuits(self.commit, self.config(), cache=False)
        self.assertFalse(fichier.exists())

    def test_reference_non_resolue_jamais_rangee(self):
        self.assertIsNone(references.resoudre(self.racine, "."))
        self.assertIsNone(references.resoudre(self.racine, "branche-inexistante"))
        for _ in range(2):
            self.nuits(None, self.config())
        self.assertEqual(len(self.lancees), 2)
        self.assertFalse(self.cache.exists())

    def test_plantage_non_range(self):
        def lancer(arbre, config, dossier, nom):
            self.lancees.append(nom)
            return [{"scenario": s, "graine": g, "plantage": {"minute": 3}, "secondes": 1, "secondes_cpu": 1}
                    for s, g in config["nuits"]]
        with patch.object(outil, "lancer", lancer):
            self.nuits(self.commit, self.config())
            self.nuits(self.commit, self.config())
        self.assertEqual(len(self.lancees), 2)

    def test_cle_relue_avant_reemploi(self):
        self.nuits(self.commit, self.config())
        fichier = next(self.cache.rglob("relais-g7-*.json"))
        enveloppe = json.loads(fichier.read_text(encoding="utf-8"))
        enveloppe["cle"]["graine"] = 8
        fichier.write_text(json.dumps(enveloppe), encoding="utf-8")
        self.nuits(self.commit, self.config())
        self.assertEqual(self.lancees[1][1], [("relais", 7)])

    def test_commande_deux_fois_puis_sans_cache(self):
        argv = ["--reference", "HEAD", "--empreintes", "--heures", "1", "--scenarios", "relais",
                "--graines", "1985", "--processus", "2"]
        dossier = os.getcwd()
        os.chdir(self.racine)
        self.addCleanup(os.chdir, dossier)
        sorties = []
        for options in ([], [], ["--sans-cache"]):
            sortie = io.StringIO()
            with redirect_stdout(sortie):
                self.assertEqual(outil.main(argv + options), 0)
            sorties.append(sortie.getvalue())
        self.assertEqual([nom for nom, _ in self.lancees], ["reference", "branche", "branche", "reference", "branche"])
        self.assertIn("rangées dans le cache", sorties[0])
        self.assertIn("1 nuits lues dans le cache", sorties[1])
        self.assertIn("d'autres conditions de charge", sorties[1])
        self.assertIn("branche : worktree", sorties[1])
        self.assertIn("non mises en cache", sorties[1])
        self.assertNotIn("lues dans le cache", sorties[2])
        self.assertEqual(len(list(self.cache.rglob("*.json"))), 1, "seule la référence est rangée")


def partie(script, erreurs=False, arret=None):
    return {"script": script, "arret": arret, "erreur_rechargement": None,
            "tours": [{"saisie": "x", "appels": 2, "secondes": 10.0, "replis": [], "refus": [],
                       "erreurs": ["délai"] if erreurs else [], "fil": []}]}


class BancMultiCacheTests(Environnement):
    def setUp(self):
        super().setUp()
        self.scripts = []
        for nom in ("relais", "crypte"):
            chemin = self.racine / f"{nom}.json"
            chemin.write_text(json.dumps({"scenario": nom, "tours": ["regarder"]}), encoding="utf-8")
            self.scripts.append(str(chemin))
        self.jouees, self.preparees, self.erreurs = [], [], set()

        def jouer_passe(nom, i, depot, sortie, args, scripts):
            self.jouees.append((nom, i, [Path(s).stem for s in scripts]))
            dossier = sortie / f"{nom}-r{i}"
            dossier.mkdir(parents=True, exist_ok=True)
            fichiers = []
            for s in scripts:
                f = dossier / f"{Path(s).stem}.json"
                f.write_text(json.dumps(partie(Path(s).stem, Path(s).stem in self.erreurs)), encoding="utf-8")
                fichiers.append(f)
            return fichiers

        def preparer(nom, ref, racine):
            self.preparees.append(nom)
            return self.racine
        for cible, valeur in (("BASE", self.racine), ("jouer_passe", jouer_passe), ("preparer_variante", preparer)):
            remplacement = patch.object(banc_multi, cible, valeur)
            remplacement.start()
            self.addCleanup(remplacement.stop)

    def banc(self, *options, scripts=None):
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            self.assertEqual(banc_multi.main(["--variante", "ref=HEAD", "--offline", *options,
                                              *(scripts or self.scripts)]), 0)
        return sortie.getvalue()

    def test_passes_rangees_puis_reemployees(self):
        self.banc("--repetitions", "2")
        self.assertEqual(self.jouees, [("ref", 1, ["relais", "crypte"]), ("ref", 2, ["relais", "crypte"])])
        self.assertEqual(len(list((self.cache / self.commit / "banc_multi").rglob("partie-*.json"))), 4)
        resume = self.banc("--repetitions", "3")
        self.assertEqual(self.jouees[2:], [("ref", 3, ["relais", "crypte"])], "seule la passe manquante se joue")
        self.assertIn("2 passes du cache, 0 en partie du cache, 1 jouées ici", resume)
        resume = self.banc("--repetitions", "3", scripts=self.scripts[:1])
        self.assertEqual(len(self.jouees), 3, "rien à rejouer")
        self.assertEqual(self.preparees, ["ref", "ref"], "aucun worktree quand tout vient du cache")
        self.assertIn("3 passes du cache", resume)
        self.assertIn("d'autres conditions de charge", resume)

    def test_script_ajoute_joue_seul(self):
        self.banc("--repetitions", "1", scripts=self.scripts[:1])
        resume = self.banc("--repetitions", "1")
        self.assertEqual(self.jouees[1], ("ref", 1, ["crypte"]))
        self.assertIn("1 en partie du cache", resume)

    def test_cle_differente_si_une_option_change(self):
        self.banc("--repetitions", "1")
        for options in (["--max-appels", "10"], ["--connexion", "chatgpt"], ["--effort", "high"],
                        ["--reflexion", "imposee"]):
            with self.subTest(options=options):
                avant = len(self.jouees)
                self.banc("--repetitions", "1", *options)
                self.assertEqual(len(self.jouees), avant + 1)
        avant = len(self.jouees)
        Path(self.scripts[0]).write_text(json.dumps({"scenario": "relais", "tours": ["autre"]}), encoding="utf-8")
        self.banc("--repetitions", "1")
        self.assertEqual(self.jouees[avant], ("ref", 1, ["relais"]), "un script modifié se rejoue")

    def test_sans_cache_et_depot_courant_jamais_ranges(self):
        self.banc("--repetitions", "1", "--sans-cache")
        self.banc("--repetitions", "1", "--sans-cache")
        self.assertEqual(len(self.jouees), 2)
        self.assertFalse(self.cache.exists())
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            for _ in range(2):
                banc_multi.main(["--variante", "ici=.", "--repetitions", "1", "--offline", *self.scripts])
        self.assertEqual(len(self.jouees), 4)
        self.assertFalse(self.cache.exists())
        self.assertIn("dépôt courant", sortie.getvalue())

    def test_partie_en_erreur_technique_non_rangee(self):
        self.erreurs = {"crypte"}
        self.banc("--repetitions", "1")
        self.banc("--repetitions", "1")
        self.assertEqual(self.jouees[1], ("ref", 1, ["crypte"]))


class PurgeTests(Environnement):
    def commande(self, *argv):
        dossier = os.getcwd()
        os.chdir(self.racine)
        try:
            sortie = io.StringIO()
            with redirect_stdout(sortie):
                self.assertEqual(references.main(list(argv)), 0)
            return sortie.getvalue()
        finally:
            os.chdir(dossier)

    def test_lister_et_purger(self):
        ancien = self.commit
        references.git(self.racine, "checkout", "-q", "-b", "a-cote")
        abandonne = commettre(self.racine, "à côté")
        references.git(self.racine, "checkout", "-q", "main")
        recent = commettre(self.racine, "récent")
        for commit in (ancien, abandonne, recent, "pas-un-commit"):
            references.ecrire(self.cache / commit / "comparer_bancs" / "nuit.json", {"x": 1}, {})
        liste = self.commande("lister")
        self.assertIn(recent[:10], liste)
        self.assertIn("comparer_bancs 1", liste)
        self.assertIn("pas-un-commit (commit inconnu)", liste)
        self.assertIn("1 commit(s) à retirer", self.commande("purger", "--simulation"))
        self.assertTrue((self.cache / abandonne).exists())
        self.commande("purger")
        self.assertFalse((self.cache / abandonne).exists())
        self.assertTrue((self.cache / ancien).exists())
        self.commande("purger", "--garder", "0")
        self.assertEqual(sorted(p.name for p in self.cache.iterdir()), sorted([recent, "pas-un-commit"]))


if __name__ == "__main__":
    unittest.main()
