"""Entretenir ce dont on a la charge : une pulsion rompue se rétablit sans attendre que son besoin
presse ; un feu à entretenir peut employer le bois d'un autre (une part demandée, que le donneur
met lui-même au feu) ; un protégé n'est servi que s'il a faim, et une seule fois.

Les cas réels : à l'auberge, la cuisinière à court de bois et les fagots du palefrenier ; à la
mine, le contremaître, son poêle et les bûches de Gaspard, la cuisinière et le blessé. Chaque
test vérifie l'état du monde après rechargement.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from donjon.banc_pnj import creer, executer
from donjon.echanges import tenu
from donjon.esprits import croire, lire
from donjon.monde import Monde
from donjon.spatial import installer


def recharger(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        repris = Monde.charger(chemin)
    installer(repris)
    assert repris.data == monde.data
    return repris


def sans(monde, *ids):
    """Placement d'auteur : ces objets ont été brûlés ou mangés ; personne n'y croit plus."""
    for id in ids:
        monde.objets.pop(id)
        for e in monde.data["esprits"].values():
            e["croyances"].pop(id, None)


def textes(chronique):
    return [c["texte"] for c in chronique]


def sans_derive(monde, id, besoin, valeur):
    """Placement d'auteur : ce besoin ne presse pas et ne dérive pas ; seule la pulsion rompue
    peut l'y faire penser."""
    monde.objets[id]["profil"]["besoins"][besoin]["derive_heure"] = 0
    lire(monde, id)["besoins"][besoin] = float(valeur)


class EntretenirUnFeuTests(unittest.TestCase):
    def test_la_cuisiniere_demande_au_palefrenier_du_bois_pour_son_fourneau(self):
        m = creer("auberge", 1985, "fixe")
        # Placement d'auteur : le bois de la cuisine est brûlé, le fourneau baisse ; Mireille sait
        # que Joss garde des fagots à l'étable (le banc le lui fait apprendre en cours de nuit).
        sans(m, "bois_cuisine")
        m.objets["fourneau"]["combustible"] = 8
        croire(m, "mireille", "fagots_etable", "lieu", "etable", "savoir", salle="etable", case=None)
        chronique, _ = executer(m, 10)
        m = recharger(m)
        # Une part demandée coûte selon sa chance d'être accordée (``planification.PRET``) : elle
        # préfère la payer une pièce, ce qui ne se refuse pas.
        self.assertIn("Mireille achète une part des fagots de l'écurie à Joss pour 1 pièce (vendu).", textes(chronique))
        self.assertIn("Joss, palefrenier alimente le fourneau.", textes(chronique))
        # Joss a mis une charge au fourneau ; ses fagots, il les a reposés à l'étable, où il les garde.
        self.assertTrue(m.objets["fourneau"]["allume"])
        self.assertGreater(m.objets["fourneau"]["combustible"], 30)
        self.assertEqual((m.objets["fagots_etable"]["charges"], m.objets["fagots_etable"]["lieu"]), (1, "etable"))
        joss = lire(m, "joss")
        self.assertEqual(joss["engagements"], [])
        self.assertTrue(any(s["type"] == "engagement_tenu" and s["pour"] == "mireille" for s in joss["memoire"]))
        # Le feu baisse de nouveau ; passé le délai où elle attendait la part promise, elle
        # redemande : il garde sa dernière charge, et elle ne la lui prend pas.
        chronique, _ = executer(m, 90)
        m = recharger(m)
        self.assertIn("Mireille demande une part des fagots de l'écurie à Joss (necessaire).", textes(chronique))
        self.assertEqual(m.objets["fagots_etable"]["charges"], 1)
        self.assertFalse(m.objets["fourneau"]["allume"])

    def test_le_contremaitre_tient_son_poele_sans_que_son_devoir_presse(self):
        m = creer("mine", 1985, "fixe")
        sans_derive(m, "josse", "devoir", 10)
        m.objets["poele"]["combustible"] = 8
        chronique, _ = executer(m, 10)
        m = recharger(m)
        self.assertLess(textes(chronique).index("Josse, contremaître prend les étais de boisage."),
                        textes(chronique).index("Josse, contremaître alimente le poêle à bois."))
        self.assertTrue(m.objets["poele"]["allume"])
        self.assertEqual(m.objets["etais"]["charges"], 2)
        self.assertLess(lire(m, "josse")["besoins"]["devoir"], 65)   # Son devoir ne presse toujours pas.

    def test_sans_bois_il_demande_les_buches_de_gaspard(self):
        m = creer("mine", 1985, "fixe")
        sans_derive(m, "josse", "devoir", 10)
        # Placement d'auteur : les étais sont brûlés ; Gaspard, qui a ses bûches, accepte (jet fixé).
        sans(m, "etais")
        m.objets["poele"]["combustible"] = 8
        with patch.object(Monde, "d20", return_value=15):
            chronique, _ = executer(m, 30)
        m = recharger(m)
        self.assertIn("Josse demande une part des bûches de Gaspard à Gaspard (promis).", textes(chronique))
        self.assertIn("Gaspard, vieux mineur alimente le poêle à bois.", textes(chronique))
        self.assertTrue(m.objets["poele"]["allume"])
        self.assertEqual(m.objets["bois_gaspard"]["charges"], 1)
        self.assertTrue(any(s["type"] == "engagement_tenu" and s["pour"] == "josse"
                            for s in lire(m, "gaspard")["memoire"]))
        # Le poêle baisse de nouveau ; passé le délai où il attendait la part promise, il redemande
        # (une part, ou les bûches que Gaspard a gardées en main), et Gaspard garde la dernière.
        with patch.object(Monde, "d20", return_value=15):
            chronique, _ = executer(m, 90)
        m = recharger(m)
        self.assertTrue(any(t.startswith("Josse demande ") and "bûches de Gaspard" in t and t.endswith("(necessaire).")
                            for t in textes(chronique)), textes(chronique))
        self.assertEqual(m.objets["bois_gaspard"]["charges"], 1)

    def test_on_ne_demande_pas_le_bois_qu_on_a_sur_soi(self):
        # Gorm a ses fagots en main et plus de flamme : il ne demande pas les planches d'Aubin pour
        # qu'Aubin vienne allumer à sa place ; il va chercher une flamme.
        from donjon.planification import planifier_pulsion
        from donjon.deplacement_objet import deplacer
        from donjon.esprits import percevoir_tous
        from tests.support import regarder
        m = creer("relais", 1985, "fixe")
        m.objets["brasero"].update(allume=False, combustible=0)
        deplacer(m, "bois", "marchand")
        m.objets["marchand"].update(lieu="echoppe", position=[3, 5], position_salle="echoppe")
        regarder(m, "marchand", "brasero")
        percevoir_tous(m)
        # Il sait la torche éteinte et le fanal allumé à l'antichambre, où Aubin a ses planches.
        for id, etat in (("torche", {"allume": False, "faible": False, "charge": True}),
                         ("fanal", {"allume": True, "faible": False, "charge": True})):
            croire(m, "marchand", id, "lieu", "antichambre", "savoir", salle="antichambre", case=None)
            croire(m, "marchand", id, "etat", etat, "savoir")
        _, plan = planifier_pulsion(m, "marchand", {"objet": "brasero", "allume": True})
        self.assertNotIn("demander", [x["operation"] for x in plan])
        self.assertIn(("allumer", "torche"), [(x["operation"], x["cible"]) for x in plan])
        self.assertEqual([(x["operation"], x["cible"]) for x in plan][-1], ("allumer", "brasero"))


class ParoleTenueTests(unittest.TestCase):
    def test_un_feu_vu_vif_avant_la_demande_n_est_pas_un_feu_entretenu(self):
        m = creer("mine", 1985, "fixe")
        condition = {"objet": "poele", "allume": True}
        croire(m, "gaspard", "poele", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        m.data["minutes"] += 10
        # Il le croit vif, mais il l'a vu avant qu'on lui demande d'y mettre du bois : il ira voir.
        self.assertFalse(tenu(m, "gaspard", condition, depuis=m.data["minutes"]))
        self.assertTrue(tenu(m, "gaspard", condition))
        croire(m, "gaspard", "poele", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        self.assertTrue(tenu(m, "gaspard", condition, depuis=m.data["minutes"]))
        # Une part promise ne se solde qu'au geste qui la sert, quoi qu'il croie de la faim de l'autre.
        self.assertFalse(tenu(m, "mathe", {"objet": "vivres", "servir": "lucien"}))


class ServirUnProtegeTests(unittest.TestCase):
    def test_la_cuisiniere_sert_le_blesse_quand_il_a_faim_et_une_seule_fois(self):
        m = creer("mine", 1985, "fixe")
        # Au départ, Lucien n'a pas faim : Mathe ne le sert pas.
        chronique, _ = executer(m, 30)
        self.assertNotIn("Mathe donne une part des vivres de la cuisine à Lucien.", textes(chronique))
        m = recharger(m)
        # Placement d'auteur : la fièvre l'a creusé, et Odon a mangé sa croûte de pain.
        lire(m, "lucien")["besoins"]["faim"] = 85.0
        sans(m, "pain_lucien")
        avant = m.objets["vivres"]["portions"]
        chronique, _ = executer(m, 120)
        m = recharger(m)
        # Sous ses yeux, ou en l'appelant s'il ne la voit pas (``echanges.servir``).
        servis = sum(t in ("Mathe donne une part des vivres de la cuisine à Lucien.",
                           "Mathe appelle Lucien et lui donne une part des vivres de la cuisine.")
                     for t in textes(chronique))
        self.assertEqual(servis, 1)
        self.assertLess(lire(m, "lucien")["besoins"]["faim"], 70)
        # Une seule part de plus est sortie du garde-manger (d'autres en ont acheté avant).
        self.assertEqual(m.objets["vivres"]["portions"], avant - 1)
        # Elle l'a vu manger : elle ne le croit plus affamé, et rien ne reste à faire.
        self.assertFalse(lire(m, "mathe")["croyances"]["lucien"]["etat"]["valeur"]["faim"])
        self.assertTrue(lire(m, "mathe")["pulsions"][1])
        self.assertTrue(m.objets["garde_manger"]["verrouillee"])


if __name__ == "__main__":
    unittest.main()
