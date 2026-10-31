"""U-T avis : vrais terminaux, callbacks web, réception et dispute rechargées."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon import emissions, social
from donjon.dialogues import AvisTerminal, avis_publics, formulaires_avis, parole_information, preparer_direct
from donjon.esprits import croire, lire, prevision
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer
from donjon.temps import ecouler
from tests import test_information_terminal as terminal
from tests.test_avis_joueur import preparer
from tests.test_avis_menace import relation
from tests import test_avis_publics as web
from tests.test_gestes_terminal import sans_saisie
from tests.test_social import recharger


def parcours(m, d):
    f = AvisTerminal(avis_publics(m))
    entrees = ["avis"]
    while not f.terminee:
        valeur = (d.contenu["cible"] if f.destinataire is None else
                  next(x for x in f.formulaires if x["acte"] == "avis") if f.formulaire is None else
                  d.contenu["parametres"][f.champ["champ"]])
        numero = next(str(i) for i, (v, _) in enumerate(f.choix(), 1) if v == valeur)
        entrees.append(numero)
        obtenu = f.saisir(numero)
    assert obtenu == d
    return entrees


def partir(m):
    m.objets["marchand"]["lieu"] = "crypte"
    placer(m.objets["marchand"], "crypte", [3, 3])


class FormulaireAvisTests(unittest.TestCase):
    def test_catalogue_public_fige_choix_explicites_et_refus(self):
        m = preparer()
        m.data["visitees"].remove("crypte")
        m.data["connus"] = [x for x in m.data["connus"] if x != "crypte"]
        m = recharger(m)
        avant = copy.deepcopy(m.data)
        public = avis_publics(m)
        f = AvisTerminal(public)
        rendu = f.rendre()
        public["destinataires"].clear()
        self.assertEqual(f.rendre(), rendu)
        self.assertEqual(f.formulaires, formulaires_avis())
        self.assertNotIn("crypte", json.dumps(f.public))
        for entrees in (parcours(m, web.choix()), parcours(m, web.choix("chambre_cloche", "non"))):
            self.assertEqual(len(entrees), 5)
        for texte in ("", "0", "1 2", "1,2", "marchand", "9" * 5000):
            with self.assertRaises(ValueError):
                f.saisir(texte)
        f.saisir("1")
        f.saisir("1")
        self.assertEqual(f.valeurs, [])
        self.assertEqual(f.champ["champ"], "sujet")
        self.assertNotIn("crypte", [x for x, _ in f.choix()])
        f.saisir("1")
        self.assertEqual(f.champ["champ"], "valeur")
        self.assertEqual(len(f.valeurs), 1)  # Pas de prévision présélectionnée.
        self.assertFalse(f.terminee)
        self.assertIsNone(f.saisir("annuler"))
        with self.assertRaises(ValueError):
            f.saisir("1")
        self.assertEqual(m.data, avant)
        for d in (web.choix("crypte"), web.choix(valeur="peut-être"), web.choix(effet="inonder")):
            with self.assertRaises(ErreurMonde) as exc:
                preparer_direct(m, d)
            self.assertTrue(exc.exception.attendu)
            self.assertEqual(m.data, avant)
        # Un formulaire figé n'autorise pas un lieu devenu inconnu.
        m.data["connus"].append("crypte")
        d = web.choix("crypte")
        parcours(m, d)
        m.data["connus"].remove("crypte")
        with self.assertRaises(ErreurMonde) as exc:
            preparer_direct(m, d)
        self.assertIn("sujet", exc.exception.attendu)

    def test_homonymes_et_croyance_privee_absente(self):
        m, cible, autre = terminal.web.support_corps.monde_geste("saisir", 1)
        f = AvisTerminal(avis_publics(m))
        noms = [nom for _, nom in f.choix()]
        self.assertEqual(len(noms), len(set(noms)))
        lieu = f.public["lieux"][0]["id"]
        for qui in (cible, autre):
            self.assertTrue(parcours(m, web.choix(lieu, qui=qui)))
        avant = avis_publics(m)
        croire(m, cible, lieu, "prevision", [m.data["minutes"], 10000, 1], "vu", 1, rang=0)
        self.assertEqual(avis_publics(m), avant)


class ParcoursAvis:
    # Même harnais de la boucle console et du vrai pilote Textual que le 369 :
    # sauvegarde avant publication, pas d'analyse ni de modèle, gestes bloqués
    # pendant le formulaire, aucune mutation avant son dernier choix.
    jouer = terminal.ParcoursInformation.jouer

    async def comparer(self, m, d, *, annuler=False, depart=None, invalide=False):
        installer(m)
        entrees = [*parcours(m, d), "annuler" if annuler else "tenter"]
        clic = web.AvisPublicsTests().clic(m, d)
        self.assertEqual(clic, d)
        # Le témoin web vérifie déjà la parité avec la parole typée de G18.
        if not annuler and not depart:
            attendu = web.AvisPublicsTests().parite(m.copier(), clic)
        else:
            if depart == "reception":
                def preparation(monde, choix):
                    partir(monde)
                    return preparer_direct(monde, choix)
                with patch("donjon.dialogues.preparer_direct", side_effect=preparation):
                    attendu, _, _ = web.AvisPublicsTests().boucle(m.copier(), [clic, entrees[-1]])
            else:
                attendu, _, _ = web.AvisPublicsTests().boucle(m.copier(), [clic, entrees[-1]],
                    mutation=partir if depart == "confirmation" else None)
        with patch.object(terminal, "partir", partir):
            obtenu, lignes, captures, publications = await self.jouer(m, entrees,
                depart=depart, invalide=invalide)
        self.assertEqual(captures, [d.contenu])
        if not annuler and not depart:
            # Le témoin web a déjà traversé ces trois laps avec recharge.
            for duree in (13, 29, 18):
                ecouler(obtenu, duree)
                obtenu = recharger(obtenu)
        self.assertEqual(sans_saisie(obtenu.data), sans_saisie(attendu.data))
        self.assertEqual(recharger(obtenu).data, obtenu.data)
        self.assertEqual(scene_percue(obtenu), scene_percue(attendu))
        self.assertEqual(fiche(obtenu), fiche(attendu))
        self.assertEqual(regarder(obtenu), regarder(attendu))
        self.assertEqual(emissions.lire(obtenu), emissions.lire(attendu))
        if depart or annuler:
            self.assertEqual(emissions.lire(obtenu), emissions.lire(m))
            self.assertEqual(obtenu.data["revision"], m.data["revision"])
        else:
            self.assertTrue(publications)
            self.assertIn("Compris :", "\n".join(lignes))
            self.assertIn(parole_information(m, d.contenu)["replique"], "\n".join(lignes))
            for p in emissions.pnj(attendu):
                self.assertIn(p["texte"], "\n".join(lignes))
        if depart:
            self.assertIn("perçois plus", "\n".join(lignes))
        print("MESURE_UT_389=" + json.dumps({"interface": self.interface, "descripteur": d.contenu,
            "annule": annuler, "depart": depart, "saisies": entrees,
            "touches_jusqua_reponse": sum(len(x) + 1 for x in entrees),
            "touches_avec_f7": sum(len(x) + 1 for x in entrees) + (self.interface == "tui"),
            "appels_modele": 0}, ensure_ascii=False))
        return obtenu

    async def test_deux_lieux_avis_oppose_reception_et_recharge(self):
        for lieu, valeur in (("echoppe", "oui"), ("chambre_cloche", "non")):
            with self.subTest(lieu=lieu):
                m = preparer()
                crue = copy.deepcopy(m.data["crue"])
                r = await self.comparer(m, web.choix(lieu, valeur))
                c = prevision(r, "marchand", lieu)
                self.assertEqual(c["source"], "dit:joueur")
                self.assertEqual(c["valeur"], valeur == "oui")
                self.assertEqual(c["confiance"], .4)
                self.assertEqual(r.data["crue"], crue)

    async def test_dispute_contraire_deux_lieux(self):
        for lieu in ("echoppe", "chambre_cloche"):
            with self.subTest(lieu=lieu):
                m = preparer()
                croire(m, "marchand", lieu, "prevision", [m.data["minutes"], -10000, 1], "vu", 1, rang=0)
                for qui in ("aubin", "ilse"):
                    relation(m, qui, "marchand", confiance=100, affection=100)
                    relation(m, qui, "joueur", confiance=1, affection=0)
                r = await self.comparer(m, web.choix(lieu))
                self.assertTrue(any(c.get("dispute") for c in r.data["chronique"]))
                self.assertTrue(all(p["acte"] == "dispute" for p in emissions.pnj(r)))
                self.assertEqual(prevision(r, "ilse", lieu)["source"], "dit:marchand")
                self.assertTrue(social.transmission_attestee(r, "joueur", "marchand",
                    {"type": "avis", "sujet": lieu, "attribut": "menace", "valeur": True}))
                self.assertTrue(any(s["type"] == "dispute_perdue" for s in lire(r, "joueur")["memoire"]))

    async def test_annulations_et_depart_revalides(self):
        m = preparer()
        d = web.choix()
        r = await self.comparer(m, d, annuler=True)
        self.assertEqual(r.objets, m.objets)
        r, _, captures, _ = await self.jouer(m, [*parcours(m, d)[:-1], "annuler"], invalide=True)
        self.assertEqual(captures, [])
        self.assertEqual(r.data, m.data)
        for depart in ("reception", "confirmation"):
            await self.comparer(preparer(), d, depart=depart)


class ConsoleAvisTests(ParcoursAvis, unittest.IsolatedAsyncioTestCase):
    interface = "console"


@unittest.skipUnless(terminal.tui.TEXTUAL, "Installer requirements-tui.txt")
class TuiAvisTests(ParcoursAvis, unittest.IsolatedAsyncioTestCase):
    interface = "tui"
