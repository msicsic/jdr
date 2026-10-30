"""U-M corps : vrais callbacks, plans, consentement et publication rechargée."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import jeu
from donjon import corps, defense
from donjon.auberge import nouveau_auberge
from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.defi import nouveau_defi
from donjon.esprits import percevoir_tous
from donjon.geometrie import placer
from donjon.gestes_publics import GESTES_CORPS, REACTIONS, catalogue_public
from donjon.monde import ErreurMonde, Monde, objet
from donjon.moteur import Moteur
from donjon.noms import apprendre, reference
from donjon.spatial import installer, memoriser
from donjon.temps import instant, MINUTE
from donjon.web.pont import PontWeb
from tests.support import calme
from tests.test_descripteur_public import vues
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests.test_tenir import situation


def monde_geste(geste, variante=0):
    m = situation() if not variante else nouveau_auberge(depart="fixe")
    if variante:
        installer(m)
    cible, autre = ("brune", "marchand") if not variante else ("lucien", "hugues")
    salle = "antichambre" if not variante else "salle_commune"
    m.joueur.update(salle=salle, position=[1, 3], orientation="est")
    calme(m, *(i for i, o in m.objets.items() if o["type"] == "personnage"))
    for id, o in m.objets.items():
        if o["type"] == "personnage" and id not in (cible, autre):
            corps.endormir(m, id)
    for id, position in ((cible, [2, 3]), (autre, [2, 4])):
        placer(m.objets[id], salle, position)
        m.objets[id].update(orientation="est", nom="personne identique", aliases=[])
        apprendre(m, "joueur", id)
    m.joueur["capacite"] = 100
    for id in ("moyen_un", "moyen_deux"):
        m.objets[id] = objet(id, "moyen identique", "outil", "joueur",
                             usages=["percussion", "lien"], puissance=3, masse=1)
    if geste in ("ligoter", "trainer", "tuer", "delier", "ranimer"):
        corps.endormir(m, cible)
    if geste == "ranimer":
        corps.corps(m, cible)["inconscient_depuis"] = instant(m) - MINUTE
    if geste in ("delier", "liberer"):
        qui = "joueur" if geste == "liberer" else cible
        m.objets["moyen_un"].update(entrave=True, lieu=qui)
        corps.corps(m, qui)["lie"] = {"lien": "moyen_un", "par": autre, "depuis": instant(m)}
    if geste in REACTIONS:
        defense.noter_coup(m, cible, "joueur", True)
        if geste == "degager":
            corps.corps(m, "joueur")["tenu_par"] = cible
        if not variante:
            m.data.setdefault("exploration", {}).setdefault(salle, []).append([0, 3])
    percevoir_tous(m)
    memoriser(m)
    vues(m)
    m.verifier()
    return m, cible, autre


def clic(m, cible, geste, parametres=None):
    d = {"geste": geste, "cible": reference(m, cible)}
    if parametres:
        d["parametres"] = parametres
    return next(c for c in page(m)["corps"] if c["envoye"] == d)


def commande(geste, ref, p):
    if geste == "frapper":
        return ("assommer" if p.get("methode") == "assommer" else "frapper") + " " + ref + (" avec " + p["outil"] if p.get("outil") else "")
    if geste in ("trainer", "pousser"):
        return geste + " " + ref + (" vers " + p["direction"] if p.get("direction") else "")
    if geste == "se_rendre":
        return "se rendre a " + ref
    if geste in ("degager", "liberer"):
        return "se " + geste
    if geste == "fuir":
        return geste
    return geste + " " + ref + (" avec " + p["outil"] if p.get("outil") else "")


class CorpsPublicsTests(unittest.TestCase):
    def boucle(self, m, entrees, mutation=None):
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "partie.json"
            m.sauver(fichier)
            saisies, lignes, etats = iter([*entrees, "quitter"]), [], []
            faux = MagicMock(connexion="api", erreur_auth=None)
            faux.echanger.side_effect = AssertionError("Appel au modèle")
            test = self

            class Pont(PontWeb):
                def rafraichir(self, monde, *args):
                    self.monde = monde
                    super().rafraichir(monde, *args)
                    etats.append(copy.deepcopy(monde.data))

                def lire(self, *_):
                    entree = next(saisies)
                    if mutation and entree == "tenter":
                        mutation(self.monde)
                    return entree

                def ecrire(self, *args, **kw):
                    super().ecrire(*args, **kw)
                    texte = " ".join(str(a) for a in args)
                    lignes.append(texte)
                    if hasattr(self, "monde") and self.monde.data.get("conversation"):
                        if texte.strip() == self.monde.data["conversation"][-1]["reponse"].strip():
                            test.assertEqual(Monde.charger(fichier).data, self.monde.data)

            with (patch("jeu.MJ", return_value=faux),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", wraps=analyser) as analyse,
                  patch.object(Monde, "d20", return_value=20)):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(fichier)], interface=Pont()), 0)
            faux.echanger.assert_not_called()
            faux.raconter_resultat.assert_not_called()
            if all(isinstance(e, DescripteurPublic) or e in ("tenter", "annuler") for e in entrees):
                analyse.assert_not_called()
            recharge = Monde.charger(fichier)
            self.assertEqual(recharge.data, etats[-1])
            self.assertEqual(vues(recharge), vues(Monde(etats[-1])))
            self.assertEqual(etat(recharge), etat(Monde(etats[-1])) )
            return recharge, lignes, etats

    def test_gestes_deux_scenarios_parite_plan_effet_rendu_recharge(self):
        variantes = [(g, {}) for g in sorted(GESTES_CORPS)]
        variantes += [("frapper", {"methode": "assommer", "outil": ""}),
                      ("frapper", {"methode": "simple", "outil": "moyen_deux"})]
        for variante in (0, 1):
            for geste, p in variantes:
                if geste == "ligoter":
                    p = {"outil": "moyen_deux"}
                elif geste in ("trainer", "pousser"):
                    p = {"direction": "ouest" if geste == "trainer" else "est"}
                elif geste in ("delier", "tuer", "riposter") or geste == "frapper" and not p:
                    p = {"outil": "", **({"methode": "simple"} if geste == "frapper" else {})}
                with self.subTest(variante=variante, geste=geste, p=p):
                    m, cible, autre = monde_geste(geste, variante)
                    choix = clic(m, cible, geste, p)
                    d = DescripteurPublic(choix["envoye"])
                    texte = commande(geste, reference(m, cible), p)
                    canonique = analyser(m, texte)
                    self.assertEqual(proposition_descripteur(m, d), canonique)
                    pa, pb = Moteur(m).preparer(d), Moteur(m).preparer(canonique)
                    self.assertEqual(pa.resume(m), pb.resume(m))
                    da, db = copy.deepcopy(pa.__dict__), copy.deepcopy(pb.__dict__)
                    for x in (da, db):
                        x.pop("choix_public"); x.pop("etat_consentement")
                    self.assertEqual(da, db)
                    avant = copy.deepcopy(m.data)
                    a, la, ea = self.boucle(m.copier(), [d, "tenter"])
                    b, lb, _ = self.boucle(m.copier(), [texte, "tenter"])
                    self.assertEqual(la, lb)
                    for x in (a.data, b.data):
                        for t in x["conversation"]:
                            t.pop("joueur", None)
                    self.assertEqual(a.data, b.data)
                    self.assertEqual(vues(a), vues(b))
                    self.assertEqual(etat(a), etat(b))
                    # La fiche précède les effets ; aucune personne homonyme
                    # ne remplace celle du clic dans le journal de Corvus.
                    self.assertTrue(pa.confirmation)
                    self.assertIn("Compris :", "\n".join(la))
                    self.assertEqual({k: v for k, v in ea[1].items() if k != "conversation"},
                                     {k: v for k, v in avant.items() if k != "conversation"})
                    self.assertTrue(a.data["journal"])
                    self.assertEqual(a.data["journal"][-1]["action"], canonique)
                    if geste == "frapper":
                        self.assertLess(corps.pv(a, cible), corps.pv(m, cible))
                        self.assertEqual(corps.pv(a, autre), corps.pv(m, autre))
                    elif geste == "ligoter":
                        self.assertEqual(corps.corps(a, cible)["lie"]["lien"], "moyen_deux")
                    elif geste in ("delier", "liberer"):
                        self.assertNotIn("lie", corps.corps(a, "joueur" if geste == "liberer" else cible))
                    elif geste == "tuer":
                        self.assertFalse(corps.vivant(a, cible))
                    elif geste == "ranimer":
                        self.assertTrue(corps.conscient(a, cible))

    def test_annulation_des_gestes_lourds_sans_effet(self):
        for geste, p in (("frapper", {"methode": "simple", "outil": ""}),
                         ("frapper", {"methode": "assommer", "outil": ""}),
                         ("ligoter", {"outil": "moyen_deux"}), ("tuer", {"outil": ""})):
            m, cible, _ = monde_geste(geste)
            d = DescripteurPublic(clic(m, cible, geste, p)["envoye"])
            avant = copy.deepcopy(m.data)
            a, lignes, _ = self.boucle(m, [d, "annuler"])
            self.assertIn("Compris :", "\n".join(lignes))
            self.assertEqual({k: v for k, v in a.data.items() if k != "conversation"},
                             {k: v for k, v in avant.items() if k != "conversation"})

    def test_cible_partie_ou_arme_absente_refus_sans_substitut(self):
        for perte in ("cible", "outil"):
            m, cible, autre = monde_geste("frapper")
            d = DescripteurPublic(clic(m, cible, "frapper", {"methode": "simple", "outil": "moyen_deux"})["envoye"])
            id = cible if perte == "cible" else "moyen_deux"
            placer(m.objets[id], "reserve", [1, 1])
            memoriser(m); vues(m)
            avant = copy.deepcopy(m.data)
            a, lignes, _ = self.boucle(m, [d])
            self.assertIn("Tu ne vois plus cette cible ici.", lignes)
            self.assertNotIn("descripteur.", "\n".join(lignes))
            self.assertEqual(a.data, avant)

    def test_revalidation_refuse_changement_sans_revision_ou_reference_perdue(self):
        for changement in ("partie", "inconsciente", "arme", "orientation"):
            m, cible, _ = monde_geste("frapper")
            d = DescripteurPublic(clic(m, cible, "frapper", {"methode": "simple", "outil": "moyen_deux"})["envoye"])
            def muter(m):
                if changement == "partie":
                    placer(m.objets[cible], "reserve", [1, 1])
                elif changement == "inconsciente":
                    corps.endormir(m, cible)
                elif changement == "arme":
                    placer(m.objets["moyen_deux"], "reserve", [1, 1])
                else:
                    m.objets[cible]["orientation"] = "ouest"
            a, lignes, _ = self.boucle(m, [d, "tenter"], muter)
            self.assertFalse(a.data["journal"])
            self.assertTrue(any("ne vois plus" in l or "plan a changé" in l for l in lignes))
            self.assertNotIn("descripteur.", "\n".join(lignes))

    def test_reactions_seulement_danger_percu_et_encore_visible(self):
        m, cible, autre = monde_geste("frapper")
        self.assertFalse(etat(m)["dangers"])
        self.assertFalse([c for c in page(m)["corps"] if c["envoye"]["geste"] in REACTIONS])
        defense.noter_coup(m, cible, "joueur", True)
        e = etat(m)
        self.assertEqual(e["dangers"], [reference(m, cible)])
        cs = [c for c in page(m)["corps"] if c["envoye"]["geste"] in REACTIONS]
        self.assertEqual({c["envoye"]["geste"] for c in cs}, REACTIONS)
        self.assertTrue(all(c["envoye"]["cible"] == reference(m, cible) for c in cs))
        # Un souvenir d'agression n'autorise pas le navigateur à identifier
        # une personne qui n'est plus perçue dans sa scène.
        placer(m.objets[cible], "reserve", [1, 1])
        self.assertFalse(etat(m)["dangers"])
        for c in cs:
            with self.assertRaises(ErreurMonde):
                Moteur(m).preparer(DescripteurPublic(c["envoye"]))

    def test_catalogue_et_moyens_publics_pilotent_les_callbacks(self):
        m, cible, _ = monde_geste("frapper")
        e = etat(m)
        self.assertEqual(e["catalogue_gestes"], catalogue_public())
        for r in e["ressources"]:
            self.assertLessEqual(set(r), {"id", "nom", "type", "aptitudes", "foyer"})
        c = clic(m, cible, "frapper", {"methode": "assommer", "outil": "moyen_deux"})
        self.assertIn("(2/2)", c["choix"][-1])
        self.assertEqual(c["clics"], 4)  # cible, geste, méthode, moyen ; tenter en sus.
        e["catalogue_gestes"]["corps"] = []
        self.assertEqual(page(m, e)["corps"], [])
        e = etat(m)
        e["ressources"] = []
        cs = page(m, e)["corps"]
        self.assertFalse(any(c["envoye"].get("parametres", {}).get("outil") for c in cs))
        self.assertTrue(any(c["envoye"]["geste"] == "frapper" for c in cs))

    def test_scenes_reelles_force_4b_4c_et_ligature(self):
        from tools.banc_parties import preparer
        for script, geste, cible, p in (
            ("force-4b-frapper", "frapper", "brune", {"methode": "simple", "outil": ""}),
            ("force-4b-assommer", "frapper", "marchand", {"methode": "assommer", "outil": ""}),
            ("force-4c-fuir", "fuir", "brune", {})):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as tmp:
                donnees = json.loads((Path(__file__).parent / "data/bancs" / (script + ".json")).read_text(encoding="utf-8"))
                fichier = Path(tmp) / "scene.json"
                with patch.object(Monde, "d20", side_effect=[20, 1]):
                    preparer(donnees, fichier)
                m = Monde.charger(fichier)
                memoriser(m); vues(m)
                d = DescripteurPublic(clic(m, cible, geste, p)["envoye"])
                a, lignes, _ = self.boucle(m, [d, "tenter"])
                if script.endswith("assommer"):
                    self.assertFalse(corps.conscient(a, cible))
                    self.assertIn("sans connaissance", "\n".join(lignes))
                elif geste == "fuir":
                    self.assertNotEqual(a.joueur["salle"], m.joueur["salle"])
                else:
                    self.assertLess(corps.pv(a, cible), corps.pv(m, cible))
        # La ligature 4d et sa seconde scène sont exécutées et rechargées
        # dans le parcours de parité, avec vérification du lien effectivement posé.


if __name__ == "__main__":
    unittest.main()
