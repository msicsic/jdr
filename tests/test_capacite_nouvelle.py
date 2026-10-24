"""Acquisitions substituables : gestes communs, monde et rendu après sauvegarde."""
import copy
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.deplacement_objet import deplacer
from donjon.esprits import croire, percevoir_tous
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from tests.test_tensions import recharger, placer
from tests.test_une_source import scene, chercher, jouer, acquiert


def preparer():
    m = scene("mine", "remy", "baraquement", "bureau", "lampe_remy",
              {"lampe_remy": (True, "remy")}, "briquet")
    m.joueur.update(salle="baraquement", position=[3, 3], orientation="nord")
    m.objets["lampe_remy"]["allume"] = True
    croire(m, "remy", "lampe_remy", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
    # Deux outils de coupe, un coffre qu'ils peuvent entamer. Les propriétés viennent
    # des règles communes de force, sans opération ni scénario spécial.
    deplacer(m, "pioche", "remy")
    a = m.objets["pioche"]
    a.update(usages=["couper"], puissance=2, proprietaire="remy")
    b = copy.deepcopy(a)
    b.update(id="autre_outil", nom="autre outil", lieu="baraquement", position=[3, 2],
             position_salle="baraquement")
    m.objets[b["id"]] = b
    deplacer(m, "garde_manger", "baraquement", position=[4, 2])
    m.objets["garde_manger"].update(proprietaire="remy", ouverte=False, verrouillee=True,
                                  seuil_coupe=2, integrite=8, maximum=8)
    percevoir_tous(m)
    for o in ("pioche", "autre_outil", "garde_manger"):
        croire(m, "remy", o, "lieu", m.objets[o]["lieu"], "savoir", salle="baraquement",
               case=m.objets[o].get("position", [2, 2]))
    croire(m, "remy", "garde_manger", "etat", {"ouverte": False, "verrouillee": True}, "vu")
    croire(m, "remy", "garde_manger", "verrouillee", True, "vu")
    return recharger(m)


def acquisitions(v, e, vises=None):
    return [x for g in p.gestes(v, e, vises) if not isinstance(g, p.SuiteDifferee) for x in g[2]
            if x["operation"] in ("prendre", "demander", "acheter")]


def regle_lumiere(v, e, o, noms, entretenus=()):
    """Témoin lot 46 : seules les facettes de lumière et les sources seules comptent."""
    if o not in v.sources_seules or o in e.portes or o in noms or o in entretenus:
        return False
    candidate = frozenset(f for f in v.capacite(e, o, libre=True) if f[0] == "lumiere")
    return any(v.couvre(frozenset(f for f in v.capacite(e, k) if f[0] == "lumiere"), candidate)
               for k in e.portes if k in v.sources_seules and not v.contrarie(k))


class CapaciteNouvelleTests(unittest.TestCase):
    def test_outil_double_et_outil_meilleur_plan_joue_apres_recharge(self):
        for puissance in (2, 6):
            with self.subTest(puissance=puissance):
                m = preparer()
                m.objets["autre_outil"]["puissance"] = puissance
                m = recharger(m)
                v = p.Vue(m, "remy")
                e = p.depart(m, "remy", v)
                self.assertEqual(v.doublon(e, "autre_outil", ()), puissance == 2)
                self.assertEqual(any(x["cible"] == "autre_outil" for x in acquisitions(v, e)), puissance > 2)
                but = lambda v, e: v.ouvert(e, "garde_manger")
                r, d = chercher(m, "remy", but, {}, emplois=None)
                complet, dc = chercher(m, "remy", but, {}, regle=False, noeuds=p.REFERENCE, emplois=None)
                self.assertEqual((r[0], r[1]), (complet[0], complet[1]))
                # Le meilleur outil n'est acquis que si le gain paie l'acquisition.
                if puissance == 6:
                    self.assertTrue(acquiert(r[1], "autre_outil"))
                else:
                    self.assertFalse(acquiert(r[1], "autre_outil"))
                    self.assertLess(d["etats"], dc["etats"])
                with patch.object(type(m), "d20", return_value=20):
                    fin = jouer(self, m, "remy", r[1])
                self.assertTrue(fin.objets["garde_manger"]["ouverte"])
                self.assertEqual(fin.objets["autre_outil"]["lieu"], "remy" if puissance > 2 else "baraquement")
                self.assertIn("garde-manger", regarder(fin))
                self.assertIn("garde_manger", {o["id"] for n in scene_percue(fin)["niveaux"] for o in n["objets"]})

    def test_cles_union_et_objet_vise(self):
        m = preparer()
        deplacer(m, "cle_paie", "remy")
        deplacer(m, "passe", "remy")
        for o in ("cle_paie", "passe"):
            m.objets[o]["proprietaire"] = "remy"
        cle = copy.deepcopy(m.objets["cle_paie"])
        cle.update(id="double_cle", nom="double de la cle", lieu="baraquement", position=[3, 1],
                   position_salle="baraquement", proprietaire="remy",
                   ouvre=["coffre_paie", "porte_bureau", "porte_reserve"])
        m.objets[cle["id"]] = cle
        croire(m, "remy", cle["id"], "lieu", "baraquement", "savoir", salle="baraquement", case=[3, 1])
        m = recharger(m)
        v = p.Vue(m, "remy")
        e = p.depart(m, "remy", v)
        self.assertTrue(v.doublon(e, "double_cle", ()))
        self.assertFalse(any(x["cible"] == "double_cle" for x in acquisitions(v, e)))
        # Même serrure seule : le second exemplaire reste également écarté.
        m.objets["double_cle"]["ouvre"] = ["coffre_paie"]
        m = recharger(m)
        v = p.Vue(m, "remy")
        self.assertTrue(v.doublon(p.depart(m, "remy", v), "double_cle", ()))
        but = lambda v, e: "double_cle" in e.portes
        r, _ = chercher(m, "remy", but, {"prendre": ("double_cle",)}, emplois=())
        self.assertTrue(acquiert(r[1], "double_cle"))
        fin = jouer(self, m, "remy", r[1])
        self.assertEqual(fin.objets["double_cle"]["lieu"], "remy")

    def test_combustibles_substances_et_disponibilite(self):
        m = preparer()
        deplacer(m, "bidon_huile", "remy")
        m.objets["bidon_huile"].update(proprietaire="remy", charges=3)
        autre = copy.deepcopy(m.objets["bidon_huile"])
        autre.update(id="autre_huile", nom="autre reserve d'huile", lieu="baraquement",
                     position=[4, 3], position_salle="baraquement")
        m.objets[autre["id"]] = autre
        croire(m, "remy", "autre_huile", "lieu", "baraquement", "savoir", salle="baraquement", case=[4, 3])
        croire(m, "remy", "autre_huile", "etat", {"disponible": True}, "vu")
        deplacer(m, "bois_gaspard", "baraquement", position=[3, 3])
        m.objets["bois_gaspard"].update(proprietaire="remy", charges=2)
        # Bois : une capacité absente de l'huile portée, pour le poêle vide.
        croire(m, "remy", "bidon_huile", "lieu", "remy", "savoir", salle="baraquement", case=[2, 2])
        croire(m, "remy", "bidon_huile", "etat", {"disponible": True}, "vu")
        croire(m, "remy", "bois_gaspard", "lieu", "baraquement", "savoir", salle="baraquement", case=[3, 3])
        croire(m, "remy", "bois_gaspard", "etat", {"disponible": True}, "vu")
        m = recharger(m)
        v = p.Vue(m, "remy")
        e = p.depart(m, "remy", v)
        self.assertTrue(v.doublon(e, "autre_huile", ()))
        self.assertFalse(any(x["cible"] == "autre_huile" for x in acquisitions(v, e)))
        self.assertFalse(v.doublon(e, "bois_gaspard", ()))
        self.assertTrue(any(x["cible"] == "bois_gaspard" for x in acquisitions(v, e)))
        but = lambda v, e: e.fait("charge", "poele")
        r, _ = chercher(m, "remy", but, {"entretenir": ("poele",)}, emplois=("feu",))
        self.assertIsNotNone(r)
        self.assertTrue(acquiert(r[1], "bois_gaspard"))
        fin = jouer(self, m, "remy", r[1])
        self.assertGreater(fin.objets["poele"]["combustible"], 0)
        self.assertEqual(fin.objets["autre_huile"]["lieu"], "baraquement")

    def test_doublon_ecarte_sur_toutes_les_voies_d_acquisition(self):
        m = preparer()
        placer(m, "gaspard", "baraquement", [4, 2])
        deplacer(m, "autre_outil", "gaspard")
        m.objets["autre_outil"].update(proprietaire="gaspard", prix=1)
        m.objets["remy"]["profil"]["valeurs"].update(honnetete=0, douceur=0)
        croire(m, "remy", "autre_outil", "lieu", "gaspard", "savoir", salle="baraquement", case=[4, 2])
        croire(m, "remy", "gaspard", "lieu", "baraquement", "savoir", salle="baraquement", case=[4, 2])
        m = recharger(m)
        v = p.Vue(m, "remy")
        v.desespere = True
        e = p.depart(m, "remy", v)
        self.assertTrue(v.doublon(e, "autre_outil", ()))
        self.assertFalse(any(x["outil"] == "autre_outil" or x["cible"] == "autre_outil"
                             for x in acquisitions(v, e)))
        with patch.object(v, "doublon", return_value=False):
            offerts = [g[2] for g in p.gestes(v, e) if not isinstance(g, p.SuiteDifferee)
                       and any(x["operation"] == "prendre" and x["cible"] == "autre_outil" for x in g[2])]
            self.assertTrue(any(any(x["operation"] == "assommer" for x in suite) for suite in offerts))
        # Même point de contrôle pour faire apporter le moyen d'une autre salle.
        deplacer(m, "autre_outil", "bureau", position=[3, 2])
        m.objets["autre_outil"]["proprietaire"] = "remy"
        croire(m, "remy", "autre_outil", "lieu", "bureau", "savoir", salle="bureau", case=[3, 2])
        v = p.Vue(recharger(m), "remy")
        v.poste_garde, v.poste, v.motif, v.detresses = True, "baraquement", "faim", ("faim",)
        self.assertEqual(list(p._aide_sur_place(v, e, "autre_outil", {}, frozenset())), [])
        with patch.object(v, "doublon", return_value=False):
            self.assertTrue(list(p._aide_sur_place(v, e, "autre_outil", {}, frozenset())))

    def test_faute_et_reunion_de_facettes_sans_combiner_qualites(self):
        m = preparer()
        v = p.Vue(m, "remy")
        e = p.depart(m, "remy", v)
        v.illicite["pioche"] = True
        self.assertFalse(v.doublon(e, "autre_outil", ()))
        self.assertTrue(v.doublon(e.apres(faits=[(("permis", "pioche"), True)]), "autre_outil", ()))
        # Le but peut faire poser le premier moyen : il ne doit pas couvrir le second.
        self.assertFalse(v.doublon(e.apres(faits=[(("permis", "pioche"), True)]), "autre_outil", {"pioche"}))

    def test_captures_reelles_meme_complete_monde_et_rendu(self):
        chercher_original = p.chercher
        for scenario, qui, faire, fichier in (
            ("mine", "remy", lambda m, q: p.planifier(m, q, "faim"), "cout-12h/mine-1985-480.json.gz"),
            ("auberge", "lucien", lambda m, q: p.garder(m, q, "etable"), "cout-12h/auberge-1985-480.json.gz"),
            ("auberge-491", "joss", lambda m, q: p.planifier_pulsion(m, q, {"objet": "poele", "allume": True}),
             "capacite-nouvelle/auberge-1985-491.json.gz"),
        ):
            with self.subTest(scenario=scenario):
                chemin = Path(__file__).parent / "data" / fichier
                original = Monde(json.loads(gzip.decompress(chemin.read_bytes())))
                plans, etats, mondes = [], [], []
                for temoin, plafond in ((True, p.NOEUDS), (True, p.REFERENCE), (False, p.NOEUDS)):
                    m = recharger(original)
                    def recherche(*a, **k):
                        parametres = {**k, "noeuds": plafond}
                        if plafond == p.REFERENCE:
                            parametres["emplois"] = None
                        return chercher_original(*a, **parametres)
                    with ExitStack() as pile:
                        if temoin:
                            pile.enter_context(patch.object(p.Vue, "doublon", regle_lumiere))
                        for nom in ("_MEMOIRE", "_GRAPHES", "_IMPOSSIBLES"):
                            pile.enter_context(patch.object(p, nom, {}))
                        pile.enter_context(patch.object(p, "chercher", recherche))
                        with p.diagnostics() as diag:
                            plans.append(faire(m, qui))
                        etats.append(diag[-1]["etats"])
                        moteur = Moteur(m)
                        lignes = moteur.executer(moteur.preparer(proposition("attendre")))
                    recharge = recharger(m)
                    self.assertEqual(m.data, recharge.data)
                    self.assertEqual(regarder(m), regarder(recharge))
                    self.assertEqual(scene_percue(m), scene_percue(recharge))
                    mondes.append((m.data, lignes, regarder(recharge), scene_percue(recharge)))
                self.assertEqual(plans[0], plans[1])
                self.assertEqual(plans[1], plans[2])
                self.assertLessEqual(etats[2], etats[0])
                if scenario == "auberge-491":
                    self.assertLess(etats[2], etats[0])
                self.assertEqual(mondes[0], mondes[1])
                self.assertEqual(mondes[1], mondes[2])

    def test_qualite_changee_invalide_la_recherche_memorisee(self):
        m = preparer()
        but = lambda v, e: v.ouvert(e, "garde_manger")
        with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                patch.object(p, "_IMPOSSIBLES", {}), patch.object(p, "VERIFIER", True):
            avant = p.chercher(m, "remy", but, memo=["outil-52"], emplois=None)
            self.assertFalse(acquiert(avant[1], "autre_outil"))
            m.objets["autre_outil"]["puissance"] = 6
            m = recharger(m)
            with p.diagnostics() as diag:
                apres = p.chercher(m, "remy", but, memo=["outil-52"], emplois=None)
            self.assertFalse(diag[0]["memoire"])
            self.assertTrue(acquiert(apres[1], "autre_outil"))
            with patch.object(type(m), "d20", return_value=20):
                fin = jouer(self, m, "remy", apres[1])
            self.assertTrue(fin.objets["garde_manger"]["ouverte"])


if __name__ == "__main__":
    unittest.main()
