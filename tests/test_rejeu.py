"""Le rejeu du banc : il observe la nuit sans la changer, et rejoue à chaque instant ce qui a été."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer, executer, nuits
from donjon.esprits import lire
from donjon.geometrie import position_entree
from donjon.rejeu import Enregistreur, page


def nuit(minutes, enregistrer):
    m = creer("relais", 7, "fixe")
    m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
    enregistreur = Enregistreur(m) if enregistrer else None
    if enregistreur:
        with enregistreur.observer():
            chronique, mesures = executer(m, minutes)
    else:
        chronique, mesures = executer(m, minutes)
    empreinte = hashlib.sha1(json.dumps([chronique, mesures, m.data], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return m, chronique, enregistreur, empreinte


def rejouer(piste, jusqua):
    etat = {}
    for instant, changes in piste:
        if instant > jusqua:
            break
        for k, v in changes.items():
            if v is None:
                etat.pop(k, None)
            else:
                etat[k] = v
    return etat


class RejeuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.monde, cls.chronique, cls.enregistreur, cls.empreinte = nuit(90, True)

    def test_la_nuit_est_la_meme_avec_ou_sans_enregistreur(self):
        self.assertEqual(nuit(90, False)[3], self.empreinte)

    def test_la_fin_du_rejeu_est_l_etat_final(self):
        m, d = self.monde, self.enregistreur.donnees(self.monde, self.chronique)
        etats, esprits = rejouer(d["etats"], d["fin"]), rejouer(d["esprits"], d["fin"])
        for id in d["personnages"]:
            o = m.objets[id]
            self.assertEqual(etats[id], [o["lieu"], o.get("position"), o.get("orientation")], id)
            croit = {objet: [c["lieu"].get("valeur"), c["lieu"].get("salle"), c["lieu"].get("case")]
                     for objet, c in lire(m, id)["croyances"].items() if c.get("lieu")}
            self.assertEqual({k.split("|", 1)[1]: v for k, v in esprits.items()
                              if k.startswith(id + "|") and not k.split("|", 1)[1].startswith(":")}, croit, id)

    def test_chaque_instant_garde_ce_qui_a_ete(self):
        d = self.enregistreur.donnees(self.monde, self.chronique)
        instants = [i for i, _ in d["etats"]]
        self.assertEqual(instants, sorted(set(instants)))  # Un instant, une entrée, dans l'ordre.
        bouges = {id for _, changes in d["etats"][1:] for id in changes if id in d["personnages"]}
        self.assertTrue(bouges)  # Ils ont bougé ou tourné pendant la nuit, et c'est noté.
        for id, vus in rejouer(d["vues"], d["fin"]).items():
            self.assertTrue(all(0 <= i < len(d["cases"]) for i in vus), id)

    def test_la_page_porte_ses_donnees(self):
        d = self.enregistreur.donnees(self.monde, self.chronique, "essai")
        d["chronique"].append({"minute": 1, "pnj": None, "texte": "</script><b>"})
        html = page(d)
        self.assertNotIn("/*DONNEES*/", html)
        self.assertEqual(html.count("</script>"), 1)  # Une chronique ne ferme pas le script.
        donnees = json.loads(re.search(r"const D = (.*?);\nconst CS", html, re.S).group(1))
        self.assertEqual(donnees["titre"], "essai")

    def test_la_lumiere_rejouee_est_celle_du_moteur(self):
        d = self.enregistreur.donnees(self.monde, self.chronique)
        self.assertEqual(rejouer(d["lumiere"], d["fin"]), degres(self.monde, self.enregistreur))

    def test_les_retournements_enregistres_sont_ceux_de_la_chronique(self):
        retournes = sum("tourne" in r[2].split("+") for b in self.enregistreur.bruits for r in b["r"])
        racontes = sum("se retourne au bruit" in c["texte"] or "se tourne vers la voix" in c["texte"]
                       for c in self.chronique)
        self.assertEqual(retournes, racontes)
        for b in self.enregistreur.bruits:
            self.assertIn(b["n"], ("feutre", "pas", "geste", "voix", "bruyant", "hele", "appel"))
            self.assertTrue(all(r[0] in self.enregistreur.personnages for r in b["r"]))
        self.assertEqual([b["t"] for b in self.enregistreur.bruits], sorted(b["t"] for b in self.enregistreur.bruits))


class AutresNuitsTests(unittest.TestCase):
    def test_la_lumiere_suit_les_sources_dans_un_autre_scenario(self):
        for scenario in ("auberge", "mine"):
            m = creer(scenario, 7, "fixe")
            enregistreur = Enregistreur(m)
            with enregistreur.observer():
                executer(m, 120)
            self.assertEqual(rejouer(enregistreur.lumiere, 10 ** 9), degres(m, enregistreur), scenario)

    def test_les_gestes_illicites_gardent_leurs_temoins(self):
        # Scène déterminée : les nouvelles relations peuvent éviter le vol au cours
        # d'une nuit libre. Ici le geste et l'arrivée du témoin doivent bien se produire.
        from tests.test_ouie import brune_crochete_dans_le_dos_de_gorm, faire
        from tests.test_social import recharger
        from donjon.monde import Monde
        m = brune_crochete_dans_le_dos_de_gorm()
        enregistreur = Enregistreur(m)
        with enregistreur.observer(), patch.object(Monde, "d20", return_value=1):
            faire(m, "attendre")
        m = recharger(m)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertTrue(enregistreur.gestes)
        vus = 0
        for g in enregistreur.gestes:
            self.assertIn(g["a"], enregistreur.personnages + ["joueur"])
            for qui, quand in g["temoins"]:
                self.assertGreaterEqual(quand, g["t"])
                self.assertNotEqual(qui, g["a"])
                vus += 1
        self.assertTrue(vus)
        self.assertTrue(any(g["op"] == "forcer" and g["objet"] == "reserve" for g in enregistreur.gestes))
        html = page(enregistreur.donnees(m, m.data.get("chronique", [])))
        donnees = json.loads(re.search(r"const D = (.*?);\nconst CS", html, re.S).group(1))
        self.assertTrue(donnees["gestes"])

    def test_une_page_par_graine(self):
        with tempfile.TemporaryDirectory() as dossier:
            nuits("relais", [7, 42], 0.5, "chambre_cloche", rejeu=str(Path(dossier) / "essai.html"))
            for graine in (7, 42):
                html = (Path(dossier) / f"essai_{graine}.html").read_text(encoding="utf-8")
                self.assertIn(f"graine {graine}", html)
            nuits("relais", [7], 0.2, "chambre_cloche", rejeu=dossier)
            self.assertTrue((Path(dossier) / "rejeu_7.html").exists())

    @unittest.skipUnless(shutil.which("node"), "node absent : le script de la page ne peut pas tourner")
    def test_la_page_tourne_avec_ses_filtres(self):
        m, chronique, enregistreur, _ = nuit(90, True)
        with tempfile.TemporaryDirectory() as dossier:
            fichier = Path(dossier) / "rejeu.html"
            fichier.write_text(page(enregistreur.donnees(m, chronique, "essai")), encoding="utf-8")
            sortie = subprocess.run(["node", str(Path(__file__).with_name("rejeu_page.js")), str(fichier)],
                                    capture_output=True, text=True, encoding="utf-8", check=True).stdout
        resultat = json.loads(sortie)
        self.assertTrue(all(n > 0 for n in resultat["lumieres"]))
        self.assertEqual(set(resultat["lignes"]), {"tout", "ouie", "paroles", "illicite", "voir", "deplacement"})
        self.assertTrue(resultat["lignes"]["tout"] >= resultat["lignes"]["ouie"] > 0)
        self.assertGreater(resultat["ondes"], 0)
        panneaux = " ".join(resultat["relations"].values())
        self.assertIn("Envers ", panneaux)
        for axe in ("confiance", "affection", "rancune", "peur", "dette"):
            self.assertRegex(panneaux, axe + r" \d+")


def degres(monde, enregistreur):
    """Les degrés de lumière recalculés de zéro, comme le fait la page de jeu (``scene``)."""
    from donjon.perception import CarteLumiere
    resultat = {}
    for (salle, x, y), i in enregistreur._index.items():
        carte = CarteLumiere(monde, salle)
        g = next(g for s, g in carte.geometrie.sol if s == (salle, x, y))
        n = carte.niveau(g)
        resultat[str(i)] = 3 if n == 2 else 2 if carte.directe(g) else 1 if n else 0
    return resultat


if __name__ == "__main__":
    unittest.main()
