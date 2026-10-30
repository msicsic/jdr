"""U-T outils : numéros réels, callbacks web, verdict et vues après recharge."""
import copy
import json
import shutil
import unittest
from unittest.mock import patch

from donjon.commandes import DescripteurPublic
from donjon.geometrie import placer
from donjon.gestes_publics import gestes_du_monde, liste_gestes, rendre_liste
from donjon.inventaire_public import ressources_publiques
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.spatial import memoriser
from tests import test_gestes_terminal as terminal
from tests import test_outils_publics as web


GESTES = ("deverrouiller", "crocheter", "frapper", "alimenter", "mettre")


def menu(m, cible, geste, ressource=None):
    ressource = ressource or ("autre_cible" if geste == "mettre" else "outil_deux")
    clic = web.choisir(m, geste, cible, ressource)
    d = DescripteurPublic(clic["envoye"])
    liste = gestes_du_monde(m)
    numero = next(str(i) for i, c in enumerate(liste, 1) if c.descripteur == d)
    return liste, numero, d


@unittest.skipUnless(shutil.which("node"), "Node requis pour les callbacks réels")
class ProjectionTests(unittest.TestCase):
    def comparer(self, m):
        e = web.etat(m)
        liste = liste_gestes(e["scene"], e["inventaire"], e["destinataires"], e["ressources"])
        page = web.page(m, e)
        attendus = {json.dumps(c["envoye"], sort_keys=True)
                    for c in page["outils"] + page["inventaire"]
                    if c["envoye"].get("parametres", {}).keys() & {"outil", "destination"}}
        obtenus = {json.dumps(c.descripteur.contenu, sort_keys=True) for c in liste
                   if c.descripteur.contenu.get("parametres", {}).keys() & {"outil", "destination"}}
        self.assertTrue(attendus)
        self.assertEqual(obtenus, attendus)
        # Corps et passages suivent les outils, sans renuméroter ce préfixe.
        self.assertEqual(liste, gestes_du_monde(m)[:len(liste)])
        self.assertEqual(len({c.libelle for c in liste}), len(liste))
        return liste

    def test_tous_les_choix_carte_besace_et_homonymes_identiques_au_web(self):
        for geste in GESTES:
            for variante in (0, 1):
                with self.subTest(geste=geste, variante=variante):
                    m, cible, _ = web.situation(geste, variante)
                    self.comparer(m)
                    liste, _, d = menu(m, cible, geste)
                    self.assertIn(d, [c.descripteur for c in liste])

    def test_conditions_libelles_et_ressources_lus_dans_le_catalogue(self):
        from donjon import gestes_publics as catalogue
        m, _, _ = web.situation("mettre")
        tables = {}
        for nom in ("OBJETS", "PORTES"):
            table = copy.deepcopy(getattr(catalogue, nom))
            tables[nom] = tuple((*ligne[:1], f"Choix du catalogue {ligne[0]}", ligne[2],
                                  {**ligne[3], "ressources": {"type": "outil"}})
                                 if len(ligne) == 4 else ligne for ligne in table)
        with patch.multiple(catalogue, **tables):
            liste = self.comparer(m)
        for c in liste:
            if c.descripteur.contenu.get("parametres", {}).keys() & {"outil", "destination"}:
                self.assertTrue(c.libelle.startswith("Choix du catalogue"))

    def test_projection_commune_aucune_ressource_privee_cachee_ou_lointaine(self):
        from donjon.web.pont import ressources_publiques as depuis_pont
        self.assertIs(depuis_pont, ressources_publiques)
        m, _, _ = web.situation("alimenter")
        m.objets["sac_ferme"] = {**copy.deepcopy(web.nouveau_defi(depart="fixe").objets["coffre"]), "id": "sac_ferme",
                                 "lieu": "joueur", "ouverte": False, "mobile": True, "masse": 1}
        for id, lieu, position in (("proche", m.joueur["salle"], [2, 3]),
                                  ("loin", m.joueur["salle"], [6, 3]),
                                  ("secret", "reserve", [1, 1]),
                                  ("prive", "marchand", None),
                                  ("cache", "sac_ferme", None)):
            m.objets[id] = {**copy.deepcopy(m.objets["outil_deux"]), "id": id, "lieu": lieu}
            if position:
                placer(m.objets[id], lieu, position)
        liste = self.comparer(m)
        ressources = ressources_publiques(m)
        ids = {r["id"] for r in ressources}
        self.assertTrue({"proche", "outil_un", "outil_deux"} <= ids)
        self.assertFalse(ids & {"loin", "secret", "prive", "cache", "marchand"})
        for c in liste:
            p = c.descripteur.contenu.get("parametres", {})
            for champ in ("outil", "destination"):
                if champ in p:
                    self.assertIn(p[champ], ids)
        for r in ressources:
            self.assertLessEqual(set(r), {"id", "nom", "type", "foyer", "aptitudes"})
            for cibles in r["aptitudes"].values():
                self.assertFalse(set(cibles) & {"secret", "prive", "cache", "marchand"})


class Parcours:
    async def jouer(self, m, cible, geste, mutation=None, ressource=None):
        liste, numero, d = menu(m, cible, geste, ressource)
        temoin = m.copier()
        if mutation:
            mutation(temoin)
        try:
            plan_attendu = Moteur(temoin.copier()).preparer(d).__dict__
        except ErreurMonde as exc:
            refus = str(exc)
            plan_attendu = None
        else:
            refus = None
        attendu, lignes_web = web.OutilsPublicsTests().boucle(temoin.copier(), d)
        plans = []
        preparer = Moteur.preparer

        def preparation(moteur, p, *args, **kwargs):
            if isinstance(p, DescripteurPublic):
                self.assertEqual(p, d)
                if mutation:
                    mutation(moteur.monde)
            plan = preparer(moteur, p, *args, **kwargs)
            if isinstance(p, DescripteurPublic):
                plans.append(copy.deepcopy(plan.__dict__))
            return plan

        with patch.object(Moteur, "preparer", preparation):
            if self.interface == "console":
                obtenu, lignes, menus = terminal.ConsoleTests().jouer_console(m, ["99999", "1 2", numero])
                self.assertEqual(menus[0], rendre_liste(liste))
            else:
                with patch.object(terminal, "menu", return_value=(liste, numero, d)):
                    obtenu, lignes = await terminal.TerminalTests().jouer_tui(m, geste, cible, invalides=True)
        self.assertIn("Numéro inconnu dans la liste affichée.", lignes)
        self.assertIn("Choix ambigu : saisis un seul numéro de la liste affichée.", lignes)
        self.assertEqual(terminal.sans_saisie(obtenu.data), terminal.sans_saisie(attendu.data))
        self.assertEqual(web.vues(obtenu), web.vues(attendu))
        self.assertEqual(web.etat(obtenu), web.etat(attendu))
        self.assertEqual(web.vues(obtenu), web.vues(Monde(copy.deepcopy(obtenu.data))))
        if refus:
            self.assertIn(refus, lignes_web)
            self.assertIn(refus, lignes)
            self.assertEqual(obtenu.data, temoin.data)
            self.assertEqual(plans, [])
        else:
            self.assertEqual(plans, [plan_attendu])
            for tour in attendu.data.get("conversation", []):
                self.assertIn(tour["reponse"], lignes)
        return obtenu, numero

    async def test_chaque_geste_deux_cas_plan_texte_effet_et_vues_recharges(self):
        mesures = []
        for geste in GESTES:
            for variante in (0, 1):
                with self.subTest(geste=geste, variante=variante):
                    m, cible, autre = web.situation(geste, variante)
                    obtenu, numero = await self.jouer(m, cible, geste)
                    if geste in ("deverrouiller", "crocheter"):
                        self.assertFalse(obtenu.objets[cible]["verrouillee"])
                        self.assertTrue(obtenu.objets[autre]["verrouillee"])
                    elif geste == "frapper":
                        self.assertLess(obtenu.objets[cible]["integrite"], m.objets[cible]["integrite"])
                        self.assertEqual(obtenu.objets[autre]["integrite"], m.objets[autre]["integrite"])
                    elif geste == "alimenter":
                        self.assertEqual(obtenu.objets["outil_deux"]["charges"], 1)
                        self.assertEqual(obtenu.objets["outil_un"]["charges"], 2)
                        self.assertGreater(obtenu.objets[cible]["combustible"], m.objets[cible]["combustible"])
                    else:
                        self.assertEqual(obtenu.objets[cible]["lieu"], "autre_cible")
                        self.assertEqual(obtenu.objets[autre]["lieu"], "joueur")
                    mesures.append({"interface": self.interface, "geste": geste, "variante": variante,
                                    "numero": numero, "touches_depuis_liste": len(numero) + 1,
                                    "touches_avec_f7": len(numero) + 2 if self.interface == "tui" else None,
                                    "appels_modele": 0})
        print("MESURES_UT_307=" + json.dumps(mesures, ensure_ascii=False))

    async def test_chaque_ressource_partie_refus_sans_substitution(self):
        for geste in GESTES:
            with self.subTest(geste=geste):
                m, cible, _ = web.situation(geste)
                ressource = "autre_cible" if geste == "mettre" else "outil_deux"

                def retirer(monde):
                    monde.objets[ressource]["lieu"] = "reserve"
                    placer(monde.objets[ressource], "reserve", [1, 1])
                    memoriser(monde)

                await self.jouer(m, cible, geste, retirer)

    async def test_destination_refermee_et_outils_perdant_leur_capacite_refus_moteur(self):
        for geste in GESTES:
            with self.subTest(geste=geste):
                m, cible, _ = web.situation(geste)
                def mutation(monde):
                    if geste == "mettre":
                        monde.objets["autre_cible"]["ouverte"] = False
                    else:
                        monde.objets["outil_deux"].update(ouvre=[], usages=[], puissance=0)
                await self.jouer(m, cible, geste, mutation)

    async def test_propriete_inconnue_deux_cibles_ne_declenche_aucun_modele(self):
        for variante in (0, 1):
            with self.subTest(variante=variante):
                m, cible, _ = web.situation("frapper", variante)
                def mutation(monde):
                    monde.objets["outil_deux"]["usages"] = ["couper"]
                    monde.objets[cible].pop("seuil_coupe", None)
                await self.jouer(m, cible, "frapper", mutation)

    async def test_besace_dans_le_noir_avec_et_sans_carte(self):
        for cases in (False, True):
            with self.subTest(cases=cases):
                m, cible, _ = web.situation("mettre", 1)
                m.data["mode_cases"] = cases
                for o in m.objets.values():
                    if "allume" in o:
                        o["allume"] = False
                memoriser(m)
                obtenu, _ = await self.jouer(m, cible, "mettre")
                self.assertEqual(obtenu.objets[cible]["lieu"], "autre_cible")


@unittest.skipUnless(shutil.which("node"), "Node requis pour les callbacks réels")
class ConsoleTests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = "console"


@unittest.skipUnless(terminal.tui.TEXTUAL and shutil.which("node"), "Textual et Node requis")
class TUITests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = "tui"
