"""U-M outils : choix réels de la page, contrat commun et sauvegarde avant rendu."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.defi import nouveau_defi
from donjon.geometrie import placer
from donjon.gestes_publics import catalogue_public, correspond, offres, ressource_admise
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.spatial import memoriser
from tests import test_descripteur_public as support
from tests.test_inventaire_public import etat

scene, vues = support.scene, support.vues

def situation(geste, variante=0):
    porte = bool(variante and geste in ("deverrouiller", "crocheter", "frapper"))
    m, cible, autre = scene("ouvrir", porte=porte)
    if porte:
        m.joueur.update(position=[2, 1], orientation="nord")
    m.joueur["capacite"] = 100
    base = nouveau_defi(depart="fixe")
    modele = {"deverrouiller": "cle", "crocheter": "crochets", "frapper": "marteau",
              "alimenter": "bois", "mettre": "marteau"}[geste]
    if geste == "alimenter":
        source = base.objets["brasero" if not variante else "lanterne"]
        for id in (cible, autre):
            o = m.objets[id]
            position = o["position"]
            m.objets[id] = {**copy.deepcopy(source), "id": id, "nom": "source identique",
                            "lieu": m.joueur["salle"], "allume": False}
            placer(m.objets[id], m.joueur["salle"], position)
            if variante:
                m.objets[id]["contenu"] = {"matiere": "huile"}
    elif geste in ("crocheter", "deverrouiller"):
        for id in (cible, autre):
            m.objets[id].update(ouverte=False, verrouillee=True)
    for id in ("outil_un", "outil_deux"):
        m.objets[id] = {**copy.deepcopy(base.objets[modele]), "id": id, "nom": "ressource identique",
                        "aliases": [], "lieu": "joueur", "proprietaire": "joueur"}
        for k in ("position", "position_salle", "ancrage_carte"):
            m.objets[id].pop(k, None)
        if geste == "deverrouiller":
            m.objets[id]["ouvre"] = [cible]
        if geste == "alimenter" and variante:
            m.objets[id]["contenu"] = {"matiere": "huile"}
    if geste == "mettre":
        # Deux destinations homonymes : la seconde est celle que le joueur choisit.
        for id in (cible, autre):
            m.objets[id]["ouverte"] = True
        if variante:
            m.objets[autre].update(lieu="joueur", mobile=True, masse=1)
            m.objets[autre].pop("position", None)
            m.objets[autre].pop("position_salle", None)
        cible, autre = "outil_deux", "outil_un"
    m = Monde(copy.deepcopy(m.data))
    memoriser(m)
    vues(m)
    return m, cible, autre


def page(m, etat_public=None):
    racine = Path(__file__).resolve().parents[1]
    p = subprocess.run(["node", str(racine / "tests/clic_page.js"), str(racine / "donjon/web/page.html")],
                       input=json.dumps(etat(m) if etat_public is None else etat_public),
                       capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(p.stdout)


def choisir(m, geste, cible, ressource="outil_deux"):
    champ = "destination" if geste == "mettre" else "outil"
    attendu = {"geste": geste, "cible": cible, "parametres": {champ: ressource}}
    resultat = page(m)
    clic = next(c for c in resultat["outils"] + resultat["inventaire"] if c["envoye"] == attendu)
    return clic


@unittest.skipUnless(shutil.which("node"), "node absent")
class OutilsPublicsTests(unittest.TestCase):
    boucle = support.DescripteurPublicTests.boucle

    def test_catalogue_commun_sse_pilote_toutes_les_offres_de_carte(self):
        for geste in ("deverrouiller", "crocheter", "frapper", "alimenter", "mettre"):
            for variante in (0, 1):
                with self.subTest(geste=geste, variante=variante):
                    m, _, _ = situation(geste, variante)
                    e = etat(m)
                    self.assertEqual(e["catalogue_gestes"], catalogue_public())
                    attendus = {}
                    for niveau in e["scene"]["niveaux"]:
                        if niveau["niveau"] != e["scene"]["joueur"]["niveau"]:
                            continue
                        cibles = [(o, False) for o in niveau["objets"]]
                        cibles += [(s["porte"], True) for s in niveau["sorties"] if s.get("porte")]
                        for o, porte in cibles:
                            for action, libelle, formulaire in offres(o, porte, parametrees=True):
                                for r in e["ressources"]:
                                    if not ressource_admise(o, r, formulaire):
                                        continue
                                    d = {"geste": action, "cible": o["id"],
                                         "parametres": {formulaire["champ"]: r["id"]}}
                                    attendus[json.dumps(d, sort_keys=True)] = libelle
                    obtenus = {json.dumps(c["envoye"], sort_keys=True): c["libelle"] for c in page(m, e)["outils"]}
                    self.assertTrue(attendus)
                    self.assertEqual(obtenus, attendus)
                    # Retirer les formulaires des données SSE retire les sous-menus :
                    # aucune liste de verbes de repli n'existe dans la page.
                    for famille in ("objets", "portes"):
                        e["catalogue_gestes"][famille] = [ligne for ligne in e["catalogue_gestes"][famille] if len(ligne) == 3]
                    self.assertEqual(page(m, e)["outils"], [])
                    self.assertTrue(any(len(ligne) == 4 for ligne in catalogue_public()["objets"]))

    def test_formulaire_et_libelle_viennent_des_donnees_du_catalogue(self):
        m, _, _ = situation("mettre")
        e = etat(m)
        for famille in ("objets", "portes"):
            for ligne in e["catalogue_gestes"][famille]:
                if len(ligne) == 4:
                    ligne[1] = "Choix du catalogue"
                    ligne[3]["ressources"] = {"type": "outil"}
        resultat = page(m, e)["outils"]
        self.assertTrue(resultat)
        for clic in resultat:
            self.assertEqual(clic["libelle"], "Choix du catalogue")
            r = next(iter(clic["envoye"]["parametres"].values()))
            self.assertEqual(next(o["type"] for o in e["ressources"] if o["id"] == r), "outil")

    def comparer(self, m, clic):
        d = DescripteurPublic(clic["envoye"])
        geste, cible = d.contenu["geste"], d.contenu["cible"]
        p = d.contenu["parametres"]
        commande = (f"mettre {cible} dans {p['destination']}" if geste == "mettre" else
                    f"{geste} {cible} avec {p['outil']}")
        canonique = analyser(m, commande)
        self.assertEqual(proposition_descripteur(m, d), canonique)
        if geste == "frapper":
            self.assertEqual(analyser(m, f"forcer {cible} avec {p['outil']}"), canonique)
        try:
            direct = Moteur(m.copier()).preparer(d)
        except ErreurMonde as refus:
            with self.assertRaises(ErreurMonde) as texte:
                Moteur(m.copier()).preparer(canonique)
            self.assertEqual(str(refus), str(texte.exception))
            self.assertTrue(refus.attendu)
        else:
            self.assertEqual(direct.__dict__, Moteur(m.copier()).preparer(canonique).__dict__)
        a, la = self.boucle(m.copier(), d)
        b, lb = self.boucle(m.copier(), commande)
        self.assertEqual(la, lb)
        da, db = copy.deepcopy(a.data), copy.deepcopy(b.data)
        for data in (da, db):
            for tour in data.get("conversation", []):
                tour.pop("joueur", None)
        self.assertEqual(da, db)
        self.assertEqual(vues(a), vues(b))
        self.assertEqual(etat(a), etat(b))
        return a, la

    def test_cinq_gestes_homonymes_plans_effets_rendus_recharges_sans_modele(self):
        for geste in ("deverrouiller", "crocheter", "frapper", "alimenter", "mettre"):
            for variante in (0, 1):
                with self.subTest(geste=geste, variante=variante):
                    m, cible, autre = situation(geste, variante)
                    ressource = "autre_cible" if geste == "mettre" else "outil_deux"
                    clic = choisir(m, geste, cible, ressource)
                    self.assertEqual(clic["clics"], 3)
                    if geste != "mettre":
                        self.assertIn("(2/2)", clic.get("ressource", clic.get("destinataire", "")))
                    a, lignes = self.comparer(m, clic)
                    if geste in ("deverrouiller", "crocheter"):
                        self.assertFalse(a.objets[cible]["verrouillee"])
                        self.assertTrue(a.objets[autre]["verrouillee"])
                    elif geste == "frapper":
                        self.assertLess(a.objets[cible]["integrite"], m.objets[cible]["integrite"])
                        self.assertEqual(a.objets[autre]["integrite"], m.objets[autre]["integrite"])
                    elif geste == "alimenter":
                        self.assertEqual(a.objets["outil_deux"]["charges"], 1)
                        self.assertEqual(a.objets["outil_un"]["charges"], 2)
                        self.assertGreater(a.objets[cible]["combustible"], m.objets[cible]["combustible"])
                    else:
                        self.assertEqual(a.objets[cible]["lieu"], ressource)
                        self.assertEqual(a.objets[autre]["lieu"], "joueur")

    def test_ressource_supprimee_ou_partie_aucun_substitut(self):
        for geste in ("deverrouiller", "crocheter", "frapper", "alimenter", "mettre"):
            for suppression in (False, True):
                with self.subTest(geste=geste, suppression=suppression):
                    m, cible, autre = situation(geste)
                    ressource = "autre_cible" if geste == "mettre" else "outil_deux"
                    clic = choisir(m, geste, cible, ressource)
                    if suppression:
                        del m.objets[ressource]
                    else:
                        m.objets[ressource]["lieu"] = "reserve"
                        placer(m.objets[ressource], "reserve", [1, 1])
                    memoriser(m)
                    vues(m)
                    avant = copy.deepcopy(m.data)
                    a, lignes = self.boucle(m, DescripteurPublic(clic["envoye"]))
                    self.assertEqual(a.data, avant)
                    self.assertEqual(etat(a), etat(Monde(avant)))
                    self.assertIn("Tu ne vois plus cette cible ici.", lignes)
                    self.assertNotIn("descripteur.", "\n".join(lignes))

    def test_destination_fermee_et_outils_inadaptes_retires_puis_refus_du_choix_perime(self):
        for geste in ("deverrouiller", "crocheter", "frapper", "alimenter", "mettre"):
            with self.subTest(geste=geste):
                m, cible, _ = situation(geste)
                ressource = "autre_cible" if geste == "mettre" else "outil_deux"
                clic = choisir(m, geste, cible, ressource)
                if geste == "mettre":
                    m.objets[ressource]["ouverte"] = False
                else:
                    m.objets[ressource].update(ouvre=[], usages=[], puissance=0)
                self.assertNotIn(clic["envoye"], [c["envoye"] for c in page(m)["outils"] + page(m)["inventaire"]])
                avant = copy.deepcopy(m.data)
                a, lignes = self.comparer(m, clic)
                self.assertEqual(a.data, avant)

    def test_projection_publique_portee_sans_regles_ni_biens_prives(self):
        m, cible, _ = situation("alimenter")
        m.objets["contenant_ferme"] = {**copy.deepcopy(nouveau_defi(depart="fixe").objets["coffre"]),
                                       "id": "contenant_ferme", "lieu": "joueur", "ouverte": False,
                                       "masse": 1, "mobile": True}
        for id, lieu, position in (("proche", m.joueur["salle"], [2, 3]),
                                  ("loin", m.joueur["salle"], [6, 3]),
                                  ("invisible", "reserve", [1, 1]),
                                  ("bien_prive", "marchand", None),
                                  ("cache_ferme", "contenant_ferme", None)):
            m.objets[id] = {**copy.deepcopy(m.objets["outil_deux"]), "id": id, "lieu": lieu}
            if position:
                placer(m.objets[id], lieu, position)
        ressources = etat(m)["ressources"]
        ids = {o["id"] for o in ressources}
        self.assertIn("proche", ids)
        self.assertIn("outil_deux", ids)
        self.assertFalse(ids & {"loin", "invisible", "bien_prive", "cache_ferme", "marchand"})
        for o in ressources:
            self.assertLessEqual(set(o), {"id", "nom", "type", "foyer", "aptitudes"})
        m.data["mode_cases"] = False
        self.assertIn("proche", {o["id"] for o in etat(m)["ressources"]})

    def test_outil_porte_dans_le_noir_et_destination_requise_sans_substitution(self):
        m, cible, _ = situation("mettre")
        m.objets["sac"] = {**copy.deepcopy(m.objets["coffre"]), "id": "sac", "lieu": "joueur",
                           "mobile": True, "masse": 1, "ouverte": True}
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        memoriser(m)
        clic = choisir(m, "mettre", cible, "sac")
        a, _ = self.comparer(m, clic)
        self.assertEqual(a.objets[cible]["lieu"], "sac")
        for params in ({}, {"destination": ""}, {"destination": "sac", "outil": "outil_un"}):
            with self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(DescripteurPublic({"geste": "mettre", "cible": cible, "parametres": params}))
            self.assertTrue(refus.exception.attendu)

    def test_mettre_dans_source_recharge_foyer_et_lampe_sans_inventer_de_contenu(self):
        for variante in (0, 1):
            with self.subTest(variante=variante):
                m, source, _ = situation("alimenter", variante)
                clic = choisir(m, "mettre", "outil_deux", source)
                a, _ = self.comparer(m, clic)
                self.assertEqual(a.objets["outil_deux"]["charges"], 1)
                self.assertEqual(a.objets["outil_un"]["charges"], 2)
                self.assertGreater(a.objets[source]["combustible"], m.objets[source]["combustible"])
                self.assertEqual(a.objets["outil_deux"]["lieu"], "joueur")

    def test_propriete_inconnue_reste_une_admission_distincte_sans_modele(self):
        for variante in (0, 1):
            with self.subTest(variante=variante):
                m, cible, _ = situation("frapper", variante)
                clic = choisir(m, "frapper", cible)
                m.objets["outil_deux"]["usages"] = ["couper"]
                m.objets[cible].pop("seuil_coupe", None)
                self.assertNotIn(clic["envoye"], [c["envoye"] for c in page(m)["outils"] + page(m)["inventaire"]])
                avant = copy.deepcopy(m.data)
                a, lignes = self.boucle(m, DescripteurPublic(clic["envoye"]))
                self.assertEqual(a.data, avant)
                self.assertIn("Tu ne sais pas encore si cet objet se prête à ce geste.", lignes)

    def test_outil_pose_et_distant_refus_sans_substitution_puis_affaires_dans_le_noir(self):
        for geste in ("deverrouiller", "crocheter", "frapper", "alimenter"):
            with self.subTest(geste=geste):
                m, cible, _ = situation(geste)
                clic = choisir(m, geste, cible)
                m.objets["outil_deux"]["lieu"] = m.joueur["salle"]
                placer(m.objets["outil_deux"], m.joueur["salle"], [6, 3])
                memoriser(m)
                avant = copy.deepcopy(m.data)
                a, lignes = self.boucle(m, DescripteurPublic(clic["envoye"]))
                self.assertEqual(a.data, avant)
                self.assertTrue(any("en main" in l or "porter un combustible" in l or "ne vois plus" in l for l in lignes))
        m, _, _ = situation("frapper")
        for o in m.objets.values():
            if "allume" in o:
                o["allume"] = False
        memoriser(m)
        clic = choisir(m, "frapper", "outil_un", "outil_deux")
        a, _ = self.comparer(m, clic)
        self.assertLess(a.objets["outil_un"]["integrite"], m.objets["outil_un"]["integrite"])

    def test_serrure_percue_sur_porte_conserve_sa_cible_et_son_outil(self):
        m, porte, _ = situation("crocheter", 1)
        m.objets["serrure_test"] = {**copy.deepcopy(nouveau_defi(depart="fixe").objets["serrure"]),
                                  "id": "serrure_test", "lieu": porte, "cartographier": True}
        memoriser(m)
        clic = choisir(m, "crocheter", "serrure_test")
        a, _ = self.comparer(m, clic)
        self.assertFalse(a.objets[porte]["verrouillee"])


if __name__ == "__main__":
    unittest.main()
