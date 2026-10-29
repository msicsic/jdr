"""U-M fabrication : vrais formulaires Node, moteur et vues après recharge, sans MJ."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from donjon.artisanat import SCHEMA_ASSEMBLAGE, USAGES
from donjon.atelier import nouveau_atelier
from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.geometrie import placer
from donjon.gestes_publics import catalogue_public
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.noms import reference
from donjon.spatial import memoriser
from tests import test_descripteur_public as support
from tests.test_inventaire_public import etat
from tests.test_outils_publics import situation


def atelier(cases=True, planches=False):
    m = nouveau_atelier()
    m.data["mode_cases"] = cases
    m.joueur.update(orientation="est", capacite=100)
    for id in ("perche_1", "perche_2", "perche_3", "ficelle"):
        placer(m.objets[id], "cour", [3, 3])
    if planches:
        # Autres barres : des planches rectangulaires décrites, pas une exception de recette.
        from donjon.matiere import masse_deduite
        for id in ("perche_1", "perche_2", "perche_3"):
            o = m.objets[id]
            o.update(nom="planche", aliases=[])
            o["physique"]["dimensions"] = {"longueur_cm": 300, "largeur_cm": 10, "epaisseur_cm": 2}
            o["masse"] = masse_deduite(o["physique"])
    m = Monde(copy.deepcopy(m.data))
    if cases:
        from donjon.spatial import installer
        installer(m)
    memoriser(m)
    support.vues(m)
    return m


def proprietaire_test(m):
    from donjon.defi import nouveau_defi
    base = nouveau_defi(depart="fixe")
    m.objets["marchand"] = copy.deepcopy(base.objets["marchand"])
    m.objets["marchand"]["lieu"] = "cour"
    m.objets["marchand"]["connait_noms"] = []
    m.objets["marchand"]["profil"].update(liens={}, pulsions=[], protege=[])
    placer(m.objets["marchand"], "cour", [3, 3])
    e = copy.deepcopy(base.data["esprits"]["marchand"])
    e.update(croyances={}, relations={}, voix=[], noms=[], pulsions=[])
    m.data["esprits"]["marchand"] = e
    from tests.support import calme
    calme(m, "marchand")
    return "marchand"


def valeurs(m, geste, cible="ficelle", soigne=False):
    ref = lambda id: reference(m, id)
    if geste == "decouper":
        return {"Cible": ref(cible), "Outil": ref("couteau" if cible == "ficelle" else "hache"),
                "Longueur (cm)": 100}
    return {"Montants 1": ref("perche_2"), "Montants 2": ref("perche_1"),
            "Barreaux": ref("perche_3"), "Lien": ref("ficelle"), "Outil": ref("hache"),
            "Longueur (cm)": 300, "Largeur (cm)": 35, "Rythme": "soigne" if soigne else "normal"}


def page(m, geste, choix=None, public=None):
    e = copy.deepcopy(etat(m) if public is None else public)
    formulaires = e["catalogue_gestes"]["fabrication"]
    index = next(i for i, f in enumerate(formulaires) if f["geste"] == geste)
    e["sonde_fabrication"] = {"index": index, "valeurs": choix or valeurs(m, geste)}
    racine = Path(__file__).resolve().parents[1]
    p = subprocess.run(["node", str(racine / "tests/clic_page.js"), str(racine / "donjon/web/page.html")],
                       input=json.dumps(e), capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(p.stdout)["fabrication"]


def commande(d):
    p = d["parametres"]
    if d["geste"] == "decouper":
        return f"découper {d['cible']} à {p['longueur_cm']} cm avec {p['outil']}"
    a, b = p["pieces"]["montants"]
    return (f"assembler {d['cible']} montants {a}, {b} barreaux {p['pieces']['barreaux']} "
            f"lien {p['lien']} outil {p['outil']} longueur {p['longueur_cm']} largeur {p['largeur_cm']} rythme {p['rythme']}")


@unittest.skipUnless(shutil.which("node"), "node absent")
class FabricationPubliqueTests(unittest.TestCase):
    boucle = support.DescripteurPublicTests.boucle

    def comparer(self, m, clic):
        d = DescripteurPublic(clic["envoye"])
        texte = commande(d.contenu)
        p = proposition_descripteur(m, d)
        self.assertEqual(p, analyser(m, texte))
        try:
            plan = Moteur(m).preparer(d)
        except ErreurMonde as exc:
            with self.assertRaises(ErreurMonde) as autre:
                Moteur(m).preparer(p)
            self.assertEqual(str(exc), str(autre.exception))
        else:
            self.assertEqual(plan.__dict__, Moteur(m).preparer(p).__dict__)
        a, la = self.boucle(m.copier(), d)
        b, lb = self.boucle(m.copier(), texte)
        self.assertEqual(la, lb)
        da, db = copy.deepcopy(a.data), copy.deepcopy(b.data)
        for data in (da, db):
            for tour in data.get("conversation", []):
                tour.pop("joueur", None)
        self.assertEqual(da, db)
        self.assertEqual(support.vues(a), support.vues(b))
        self.assertEqual(etat(a), etat(b))
        return a, la

    def test_echelles_perches_et_planches_normale_soignee_meme_plan_effet_rendu_recharge(self):
        for autre in (False, True):
            with self.subTest(planches=autre):
                m = atelier(cases=not autre, planches=autre)
                clic = page(m, "assembler", valeurs(m, "assembler", soigne=autre))
                a, _ = self.comparer(m, clic)
                e = next(o for o in a.objets.values() if o.get("assemblage"))
                self.assertEqual((e["longueur_cm"], e["barreaux"]), (300, 8))
                self.assertEqual(a.objets["perche_3"]["longueur_cm"], 12)
                self.assertEqual(a.objets["ficelle"]["longueur_cm"], 1040)
                self.assertTrue(a.objets["perche_2"]["incorpore"])
                self.assertEqual(clic["clics"], 17)
                self.assertEqual(clic["incomplet"], 0)
                self.assertEqual(clic["clavier"], 0)
                self.assertEqual(clic["occupe"], 0)
                self.assertEqual(clic["envois"], 1)
                self.assertTrue(clic["ferme_apres_etat"])

    def test_ficelle_un_metre_et_barre_meme_plan_effet_texte_et_vues_recharges(self):
        for cible in ("ficelle", "perche_2"):
            with self.subTest(cible=cible):
                m = atelier()
                clic = page(m, "decouper", valeurs(m, "decouper", cible))
                a, _ = self.comparer(m, clic)
                self.assertEqual(a.objets[cible + "_1"]["longueur_cm"], 100)
                self.assertEqual(a.objets[cible]["longueur_cm"], m.objets[cible]["longueur_cm"] - 100)
                self.assertEqual(a.objets["perche_1"], m.objets["perche_1"])
                self.assertEqual(clic["clics"], 8)

    def test_ressources_perimees_absentes_lointaines_et_privees_sans_substitution(self):
        for geste in ("assembler", "decouper"):
            for cause in ("supprimee", "partie", "lointaine", "privee"):
                with self.subTest(geste=geste, cause=cause):
                    m = atelier()
                    cible = "perche_2" if geste == "assembler" else "ficelle"
                    clic = page(m, geste)
                    if cause == "supprimee":
                        del m.objets[cible]
                    elif cause == "partie":
                        m.objets[cible]["lieu"] = "terrasse"
                        placer(m.objets[cible], "terrasse", [1, 1])
                    elif cause == "lointaine":
                        placer(m.objets[cible], "cour", [5, 3])
                    else:
                        # Une affaire de PNJ ne devient pas une ressource du menu.
                        m.objets[cible]["lieu"] = proprietaire_test(m)
                    m = m.copier()
                    from donjon.spatial import installer
                    installer(m)
                    memoriser(m)
                    support.vues(m)
                    avant = copy.deepcopy(m.data)
                    a, lignes = self.boucle(m, DescripteurPublic(clic["envoye"]))
                    self.assertEqual(a.data, avant)
                    self.assertIn("Tu ne vois plus cette ressource à portée.", lignes)

    def test_description_manquante_et_bien_autrui_gardent_les_refus_de_commande(self):
        for geste in ("assembler", "decouper"):
            for cause in ("physique", "proprietaire", "mauvais_outil", "doublon"):
                with self.subTest(geste=geste, cause=cause):
                    m = atelier()
                    cible = "perche_2" if geste == "assembler" else "ficelle"
                    if cause == "physique":
                        for cle in ("physique", "ressource", "longueur_cm", "charge_jeu_kg"):
                            m.objets[cible].pop(cle, None)
                    elif cause == "proprietaire":
                        m.objets[cible]["proprietaire"] = proprietaire_test(m)
                        m = m.copier()
                        from donjon.spatial import installer
                        installer(m)
                        memoriser(m)
                        support.vues(m)
                    choix = valeurs(m, geste)
                    if cause == "mauvais_outil":
                        choix["Outil"] = reference(m, "couteau" if geste == "assembler" else "perche_1")
                    elif cause == "doublon":
                        choix["Montants 1" if geste == "assembler" else "Outil"] = choix["Montants 2" if geste == "assembler" else "Cible"]
                    clic = page(m, geste, choix)
                    if cause == "physique":
                        champ = next(c for c in clic["champs"] if c["nom"] == ("Montants 1" if geste == "assembler" else "Cible"))
                        self.assertIn("Description physique manquante", champ["detail"])
                    avant = copy.deepcopy(m.data)
                    a, lignes = self.comparer(m, clic)
                    self.assertEqual(a.data, avant)
                    self.assertFalse(any(o.get("assemblage") for o in a.objets.values()))
                    if cause == "physique":
                        self.assertTrue(any("n'est pas encore décrit" in l for l in lignes))

    def test_projection_ne_revele_ni_capacites_ni_mesures_cachees_ou_inventaires_prives(self):
        m, _, _ = situation("alimenter")
        public = etat(m)
        self.assertEqual({r["id"] for r in public["fabrication"]}, {r["id"] for r in public["ressources"]})
        for r in public["fabrication"]:
            self.assertEqual(set(r) - {"foyer"}, {"id", "nom", "type", "description_physique"})
        from donjon.defi import nouveau_defi
        base = nouveau_defi(depart="fixe")
        m.objets["ferme"] = {**copy.deepcopy(base.objets["coffre"]), "id": "ferme", "lieu": "joueur", "ouverte": False}
        for id, lieu, position in (("secret", "ferme", None), ("prive", "marchand", None),
                                  ("loin", m.joueur["salle"], [6, 3]), ("autre_salle", "reserve", [1, 1])):
            m.objets[id] = {**copy.deepcopy(nouveau_atelier().objets["perche_1"]),
                            "id": id, "lieu": lieu, "nom": "MESURE SECRÈTE"}
            if position:
                placer(m.objets[id], lieu, position)
        projection = etat(m)["fabrication"]
        self.assertFalse({"secret", "prive", "loin", "autre_salle"} & {r["id"] for r in projection})
        self.assertNotIn("MESURE SECRÈTE", json.dumps(projection, ensure_ascii=False))
        m = atelier()
        m.objets["perche_1"]["nom"] = m.objets["perche_2"]["nom"] = "perche identique"
        clic = page(m, "assembler")
        c = clic["champs"][0]
        self.assertEqual(len([r for r in c["choix"] if "perche identique" in r["texte"]]), 2)
        self.assertEqual(c["valeur"], reference(m, "perche_2"))

    def test_catalogue_derive_des_schemas_et_reellement_lu_par_la_page(self):
        m = atelier()
        c = catalogue_public()["fabrication"]
        self.assertEqual([f["cible"] for f in c if f["geste"] == "assembler"], list(USAGES))
        self.assertEqual(sum(f["chemin"][:2] == ["pieces", "montants"] for f in c[0]["champs"]),
                         SCHEMA_ASSEMBLAGE["properties"]["pieces"]["properties"]["montants"]["minItems"])
        public = etat(m)
        public["catalogue_gestes"]["fabrication"][0]["libelle"] = "Atelier public modifié"
        clic = page(m, "assembler", public=public)
        self.assertEqual(clic["offres"][0], "Atelier public modifié")
        c[0]["champs"][-1]["choix"].clear()
        self.assertEqual(catalogue_public()["fabrication"][0]["champs"][-1]["choix"], ["normal", "soigne"])

    def test_descripteurs_malformes_refuses_avec_attendu_sans_mutation(self):
        m = atelier()
        valide = page(m, "assembler")["envoye"]
        variantes = []
        for valeur in ([], {}, None, "perche_1", {"montants": ["perche_1"], "barreaux": "perche_3"},
                       {"montants": [[], "perche_2"], "barreaux": "perche_3"}):
            d = copy.deepcopy(valide)
            d["parametres"]["pieces"] = valeur
            variantes.append(d)
        for champ, valeur in (("longueur_cm", True), ("largeur_cm", 0), ("rythme", {}), ("outil", []),
                              ("difficulte", 0), ("effets", []), ("lien", m.objets["ficelle"]["nom"])):
            d = copy.deepcopy(valide)
            d["parametres"][champ] = valeur
            variantes.append(d)
        for d in variantes:
            with self.subTest(d=d), self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(DescripteurPublic(d))
            self.assertTrue(refus.exception.attendu)
        self.assertFalse(any(o.get("assemblage") for o in m.objets.values()))


if __name__ == "__main__":
    unittest.main()
