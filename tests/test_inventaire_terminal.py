"""U-T inventaire : vrais numéros console/TUI, callbacks web et reprise."""
import copy
import json
import shutil
import unittest
from unittest.mock import patch

from donjon.commandes import DescripteurPublic
from donjon.geometrie import placer
from donjon.gestes_publics import gestes_du_monde, gestes_inventaire, rendre_liste
from donjon.inventaire_public import destinataires_publics, inventaire_public
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.noms import installer as installer_noms, reference
from donjon.spatial import memoriser
from tests import test_gestes_terminal as terminal
from tests import test_inventaire_public as web


CAS = (("poser", "marteau"), ("poser", "planches"),
       ("remettre", "marteau"), ("remettre", "planches"),
       ("manger", "vivres"), ("manger", "vivres"),
       ("allumer", "torche"), ("allumer", "lanterne"),
       ("eteindre", "torche"), ("eteindre", "lanterne"),
       ("prelever", "planches"), ("prelever", "planches"))


def scene(geste, modele, variante=0):
    m, cible, autre = web.besace(geste, modele)
    # Deux destinataires de même description, avec références publiques distinctes.
    m.objets["autre_personne"] = {**copy.deepcopy(m.objets["marchand"]), "id": "autre_personne"}
    placer(m.objets["autre_personne"], m.joueur["salle"], [2, 4])
    installer_noms(m)
    if geste == "prelever" and variante:
        m.objets[cible]["physique"].update(pieces=4, nom_piece="pièce de bois")
    if geste == "manger" and variante:
        m.objets[cible]["portions"] = 3
    m = Monde(copy.deepcopy(m.data))
    memoriser(m)
    web.vues(m)
    return m, cible, autre


def menu(m, cible, geste):
    liste = gestes_du_monde(m)
    d = {"geste": geste, "cible": reference(m, cible)}
    if geste == "remettre":
        d["parametres"] = {"destinataire": reference(m, "autre_personne")}
    if geste in ("manger", "prelever"):
        d["parametres"] = {"quantite": 1}
    numero = next(str(i) for i, choix in enumerate(liste, 1) if choix.descripteur.contenu == d)
    return liste, numero, DescripteurPublic(d)


def retirer_bien(m, cible):
    m.objets[cible]["lieu"] = "reserve"
    placer(m.objets[cible], "reserve", [1, 1])
    memoriser(m)


def retirer_personne(m, loin=False):
    salle = m.joueur["salle"] if loin else "echoppe"
    m.objets["autre_personne"]["lieu"] = salle
    placer(m.objets["autre_personne"], salle, [6, 3] if loin else [1, 1])
    memoriser(m)


class ProjectionTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node requis pour les callbacks de la page")
    def test_catalogue_identique_aux_callbacks_web_sur_public_seul(self):
        for n, (geste, modele) in enumerate(CAS):
            with self.subTest(geste=geste, modele=modele, n=n):
                m, cible, _ = scene(geste, modele, n % 2)
                liste = gestes_inventaire(inventaire_public(m), destinataires_publics(m))
                envoyes = [c["envoye"] for c in web.clics(m)
                           if c["envoye"]["geste"] in dict(CAS)]
                self.assertCountEqual([c.descripteur.contenu for c in liste], envoyes)
                self.assertEqual(len({c.libelle for c in liste}), len(liste))
                self.assertIn(menu(m, cible, geste)[2].contenu, envoyes)
                self.assertNotIn("marchand", rendre_liste(liste))
                self.assertNotIn("autre_personne", rendre_liste(liste))

    def test_projection_partagee_noir_contenu_ferme_absence_et_sans_carte(self):
        from donjon.web.pont import inventaire_public as depuis_pont
        self.assertIs(depuis_pont, inventaire_public)
        m, cible, _ = scene("prelever", "planches")
        coffre = copy.deepcopy(m.objets["coffre"])
        coffre.update(id="sac", lieu="joueur", ouverte=False)
        m.objets["sac"] = coffre
        m.objets["contenu_secret"] = {**copy.deepcopy(m.objets[cible]), "id": "contenu_secret", "lieu": "sac"}
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        memoriser(m)
        liste = gestes_du_monde(m)
        self.assertNotIn("contenu_secret", rendre_liste(liste))
        self.assertNotIn("remettre", {c.descripteur.contenu["geste"] for c in liste})
        self.assertIn(menu(m, cible, "prelever")[2], [c.descripteur for c in liste])
        m.data["mode_cases"] = False
        # Les offres à ressource s'ajoutent aux gestes simples de besace.
        simples = gestes_inventaire(inventaire_public(m), destinataires_publics(m))
        self.assertEqual(gestes_du_monde(m)[:len(simples)], simples)


class Parcours:
    async def jouer(self, m, cible, geste, mutation=None):
        liste, numero, d = menu(m, cible, geste)
        temoin = m.copier()
        if mutation:
            mutation(temoin)
        attendu, lignes_web = web.InventairePublicTests().boucle(
            temoin, d, confirmer=geste == 'remettre' and not mutation)
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
                obtenu, lignes, menus = terminal.ConsoleTests().jouer_console(
                    m, ["99999", "1 2", numero, *(['tenter'] if geste == 'remettre' and not mutation else [])])
                self.assertEqual(menus[0], rendre_liste(liste))
            else:
                with patch.object(terminal, "menu", return_value=(liste, numero, d)):
                    obtenu, lignes = await terminal.TerminalTests().jouer_tui(
                        m, geste, cible, invalides=True, confirmer=geste == 'remettre' and not mutation)
        self.assertIn("Numéro inconnu dans la liste affichée.", lignes)
        self.assertIn("Choix ambigu : saisis un seul numéro de la liste affichée.", lignes)
        self.assertEqual(terminal.sans_saisie(obtenu.data), terminal.sans_saisie(attendu.data))
        self.assertEqual(web.vues(obtenu), web.vues(attendu))
        self.assertEqual(web.etat(obtenu), web.etat(attendu))
        self.assertEqual(web.vues(obtenu), web.vues(Monde(copy.deepcopy(obtenu.data))))
        for tour in attendu.data.get("conversation", []):
            self.assertIn(tour["reponse"].strip(), [l.strip() for l in lignes])
        if mutation:
            # Le refus exact du même descripteur web, sans état mécanique modifié.
            self.assertEqual(obtenu.data, temoin.data)
            self.assertTrue(any(l in lignes for l in lignes_web if "Tu ne vois plus" in l or "Approche-toi" in l or "une pièce" in l), lignes)
        else:
            plan = Moteur(m.copier()).preparer(d)
            # U-C prépare l'aperçu puis revalide le choix public à sa
            # confirmation ; chaque préparation doit garder le même plan.
            self.assertEqual(plans, [plan.__dict__] * (2 if plan.confirmation else 1))
        return obtenu, numero

    async def test_chaque_geste_parite_plan_texte_monde_fiche_scene_carte_recharges(self):
        mesures = []
        for n, (geste, modele) in enumerate(CAS):
            with self.subTest(geste=geste, modele=modele, n=n):
                m, cible, autre = scene(geste, modele, n % 2)
                obtenu, numero = await self.jouer(m, cible, geste)
                self.assertEqual(obtenu.objets[autre]["lieu"], "joueur")
                if geste == "manger":
                    self.assertEqual(obtenu.objets[autre]["portions"], m.objets[autre]["portions"])
                if geste in ("allumer", "eteindre"):
                    self.assertEqual(obtenu.objets[autre]["allume"], geste == "eteindre")
                if geste == "remettre":
                    self.assertEqual(obtenu.objets[cible]["lieu"], "autre_personne")
                if geste == "poser":
                    self.assertEqual(obtenu.objets[cible]["lieu"], m.joueur["salle"])
                if geste == "manger":
                    self.assertEqual(obtenu.objets[cible]["portions"], m.objets[cible]["portions"] - 1)
                if geste in ("allumer", "eteindre"):
                    self.assertEqual(obtenu.objets[cible]["allume"], geste == "allumer")
                if geste == "prelever":
                    self.assertEqual(obtenu.objets[cible]["physique"]["pieces"], m.objets[cible]["physique"]["pieces"] - 1)
                if geste in ("poser", "remettre") and modele == "planches":
                    self.assertEqual(obtenu.objets[cible]["physique"]["pieces"], 2)
                mesures.append({"interface": self.interface, "geste": geste, "modele": modele,
                                "numero": numero, "touches_depuis_liste": len(numero) + 1,
                                "touches_avec_f7": len(numero) + 2 if self.interface == "tui" else None,
                                "appels_modele": 0})
        print("MESURES_UT_301=" + json.dumps(mesures, ensure_ascii=False))

    async def test_chaque_geste_bien_perime_sans_substitution(self):
        for geste, modele in dict(CAS).items():
            with self.subTest(geste=geste):
                m, cible, _ = scene(geste, modele)
                await self.jouer(m, cible, geste, lambda monde: retirer_bien(monde, cible))

    async def test_destinataire_parti_eloigne_et_quantite_perimee(self):
        for loin in (False, True):
            with self.subTest(loin=loin):
                m, cible, _ = scene("remettre", "planches")
                await self.jouer(m, cible, "remettre", lambda monde: retirer_personne(monde, loin))
        m, cible, _ = scene("prelever", "planches")
        await self.jouer(m, cible, "prelever", lambda monde: monde.objets[cible]["physique"].update(pieces=1))

    async def test_sans_carte_et_bien_porte_dans_le_noir(self):
        for cases in (False, True):
            with self.subTest(cases=cases):
                m, cible, _ = scene("poser", "planches")
                m.data["mode_cases"] = cases
                for o in m.objets.values():
                    if "allume" in o:
                        o["allume"] = False
                memoriser(m)
                await self.jouer(m, cible, "poser")


class ConsoleTests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = "console"


@unittest.skipUnless(terminal.tui.TEXTUAL, "Installer les dépendances TUI")
class TUITests(Parcours, unittest.IsolatedAsyncioTestCase):
    interface = "tui"
