"""Branche ``pnj-lumiere-garde``, vérifiée après rechargement :

- dans le noir, on cherche qui porte la flamme qu'il faut (on l'appelle) et on lui demande du feu
  pour sa source, sans la lui emprunter ;
- la lumière crue devant une serrure compte une source allumée ou posée près d'elle depuis ;
- une part promise s'attend là où elle se sert, et ce temps compte comme tout autre (ses biens
  laissés, le noir) : un échange n'échappe plus au coût de l'éloignement ;
- un gardien ne laisse pas un bien que menace quelqu'un dont il se méfie pour s'abriter de lui :
  il reste ; il appelle à l'aide si sa crainte l'emporte sur son courage."""
import unittest

from donjon.banc_pnj import creer, executer
from donjon.deliberation import autour, gardes, menaces
from donjon.echanges import demander_feu
from donjon.esprits import croire, lire, percevoir_tous
from donjon.geometrie import position_entree
from donjon.planification import Vue, depart, gestes, planifier
from tests.support import calme, regarder
from tests.test_tensions import placer, recharger, relais, vivre

MINEURS = ("bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy")


def textes(m, *ids):
    return [c["texte"] for c in m.data.get("chronique", []) if c["pnj"] in ids]


def suivre(m, minutes, fini=None):
    """Fait vivre le monde minute par minute, rechargé à chaque pas ; s'arrête quand ``fini``."""
    for _ in range(minutes):
        m, _ = vivre(m, 1)
        if fini and fini(m):
            break
    return m


class FeuDemandeTests(unittest.TestCase):
    """La dernière flamme est dans la main d'un autre, qu'on ne voit pas dans le noir."""

    def camp_eteint(self):
        """Cas réel (mine, nuits 1985, 7, 42, 2024, à partir de la minute 450) : le camp s'éteint ;
        plus de bois, plus d'huile dans les lampes de chacun ; restent les deux lampes de rechange
        de la réserve et le briquet de Gaspard. Rémy, qui craint le noir, est dans la réserve, la
        porte ouverte ; il ne sait plus où est Gaspard. Les autres sont au bureau, calmes."""
        m = creer("mine", 1985, "fixe")
        calme(m, *MINEURS)
        for k in ("poele", "lampe_baraque", "chandelle", "lampe_filon", "lampe_gaspard", "lampe_remy", "lampe_josse"):
            m.objets[k].update(allume=False, combustible=0)
        for k in ("etais", "bois_gaspard"):
            m.objets[k]["charges"] = 0
        m.objets["porte_reserve"].update(verrouillee=False, ouverte=True)
        for i, id in enumerate(("bram", "josse", "lucien", "mathe", "odon")):
            placer(m, id, "bureau", (1 + i, 1))
        m.objets["porte_bureau"]["ouverte"] = False
        placer(m, "gaspard", "galerie", (2, 2))
        placer(m, "remy", "reserve", (1, 1))
        m.joueur.update(salle="filon", position=[2, 2])
        percevoir_tous(m)
        croire(m, "remy", "gaspard", "lieu", None, "vu", salle=None, case=None)
        for k in ("etais", "bois_gaspard"):
            croire(m, "remy", k, "etat", {"disponible": False}, "vu")
        croire(m, "remy", "porte_reserve", "verrouillee", False, "essai")
        croire(m, "remy", "porte_reserve", "etat", {"ouverte": True}, "essai")
        lire(m, "remy")["besoins"]["securite"] = 70.0
        return recharger(m)

    def test_remy_cherche_gaspard_et_lui_demande_du_feu(self):
        m = suivre(self.camp_eteint(), 10, lambda m: m.objets["lampe_rechange_1"].get("allume"))
        lampe = m.objets["lampe_rechange_1"]
        self.assertEqual(lampe["lieu"], "remy")
        self.assertTrue(lampe["allume"])
        self.assertEqual(m.objets["briquet"]["lieu"], "gaspard")   # Rien n'a été prêté.
        vus = textes(m, "remy", "gaspard")
        self.assertIn("Rémy appelle : « Gaspard ? »", vus)
        self.assertTrue(any(t.startswith("Rémy demande du feu à Gaspard") and t.endswith("(allume).") for t in vus))
        self.assertTrue(autour(m, "remy")["lumiere"])
        # Sa lampe allumée de la main d'un autre, il la ménagera quand elle ne lui servira plus.
        self.assertTrue(any(s["type"] == "flamme_employee" and s["objet"] == "lampe_rechange_1"
                            for s in lire(m, "remy")["memoire"]))

    def test_joss_cherche_odile_et_allume_sa_lanterne_a_son_briquet(self):
        # Autre cas de même nature (auberge) : Joss, sa lanterne éteinte en main dans l'étable noire,
        # croit les foyers allumés ; il les trouve morts, puis cherche Odile, qui porte un briquet.
        m = creer("auberge", 1985, "fixe")
        ids = [k for k, o in m.objets.items() if o.get("profil")]
        calme(m, *ids)
        for k, o in m.objets.items():
            if "allume" in o:
                o["allume"] = False
        m.objets["lanterne_etable"].update(lieu="etable", position=[2, 2])
        placer(m, "joss", "etable", (3, 2))
        placer(m, "odile", "cellier", (2, 2))
        for i, id in enumerate(x for x in ids if x not in ("joss", "odile")):
            placer(m, id, "dortoir", (1 + i % 4, 1 + i // 4))
        m.joueur.update(salle="grenier", position=[2, 2])
        percevoir_tous(m)
        for s in m.data["salles"]:
            # Il croit les salles où il n'est pas éclairées par leurs foyers, vus allumés plus tôt.
            if s != "etable":
                croire(m, "joss", s, "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
        croire(m, "joss", "odile", "lieu", None, "vu", salle=None, case=None)
        croire(m, "joss", "briquet_odile", "lieu", "odile", "savoir", salle=None, case=None)
        lire(m, "joss")["besoins"]["securite"] = 75.0
        m = suivre(recharger(m), 15, lambda m: m.objets["lanterne_etable"].get("allume"))
        self.assertEqual(m.objets["lanterne_etable"]["lieu"], "joss")
        self.assertTrue(m.objets["lanterne_etable"]["allume"])
        self.assertEqual(m.objets["briquet_odile"]["lieu"], "odile")
        vus = textes(m, "joss")
        self.assertIn("Joss appelle : « Odile ? »", vus)
        self.assertTrue(any(t.startswith("Joss demande du feu à Odile") for t in vus))

    def test_qui_se_mefie_ne_donne_pas_de_feu_et_on_ne_le_lui_redemande_pas(self):
        m = self.camp_eteint()
        placer(m, "remy", "galerie", (3, 2))
        m.objets["lampe_rechange_1"]["lieu"] = "remy"
        croire(m, "gaspard", "remy", "fiable", False, "vu")
        percevoir_tous(m)
        self.assertEqual(demander_feu(m, "remy", "gaspard", "briquet", "lampe_rechange_1"), "mefiance")
        self.assertFalse(m.objets["lampe_rechange_1"]["allume"])
        # Par le geste social, le refus se retient : la recherche ne le propose plus.
        from donjon.echanges import executer as echanger
        etape = {"operation": "demander_feu", "cible": "gaspard", "outil": "briquet", "lieu": "", "condition": "",
                 "contenu": {"allumer": "lampe_rechange_1"}}
        self.assertFalse(echanger(m, "remy", etape, []))
        m = recharger(m)
        v = Vue(m, "remy")
        self.assertFalse(any(g[2] and g[2][0]["operation"] == "demander_feu" for g in gestes(v, depart(m, "remy", v))))


class LumiereDevantTests(unittest.TestCase):
    """De loin, la lumière devant une serrure est celle qu'il y a vue, plus ce qu'une source qu'il
    sait allumée ou posée près d'elle depuis y apporte."""

    def test_odon_compte_la_chandelle_rallumee_pres_du_coffre(self):
        # Cas réel (mine) : Odon a vu le coffre de la paie dans le noir (le camp éteint) ; la
        # chandelle du bureau, à trois pas du coffre, est rallumée depuis, et il le sait.
        m = creer("mine", 1985, "fixe")
        calme(m, *MINEURS)
        for k in ("poele", "lampe_baraque", "chandelle"):
            m.objets[k].update(allume=False)
        m.objets["porte_bureau"]["verrouillee"] = False
        placer(m, "odon", "bureau", (4, 2))
        from donjon.esprits import constater_lumiere_devant
        percevoir_tous(m)
        constater_lumiere_devant(m, "odon", "coffre_paie")
        self.assertEqual(lire(m, "odon")["croyances"]["coffre_paie"]["lumiere"]["valeur"], 0)
        placer(m, "odon", "baraquement", (4, 1))
        m.data["minutes"] += 5
        m.objets["chandelle"].update(allume=True, combustible=300)
        croire(m, "odon", "chandelle", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        m = recharger(m)
        v = Vue(m, "odon")
        self.assertEqual(v.lumiere_devant(depart(m, "odon", v), "coffre_paie"), 1)
        # Ce qu'il savait déjà allumé quand il l'a vue sombre n'y ajoute rien.
        from donjon.esprits import constater_lumiere_devant as constater
        placer(m, "odon", "bureau", (4, 2))
        constater(m, "odon", "coffre_paie")
        self.assertIn("chandelle", lire(m, "odon")["croyances"]["coffre_paie"]["lumiere"]["allumees"])
        m = recharger(m)
        v = Vue(m, "odon")
        self.assertEqual(v.lumiere_devant(depart(m, "odon", v), "coffre_paie"),
                         lire(m, "odon")["croyances"]["coffre_paie"]["lumiere"]["valeur"])

    def test_brune_compte_la_torche_posee_pres_de_la_reserve(self):
        # Autre cas de même nature (Relais) : Brune a vu la réserve dans la pénombre ; une torche
        # allumée est posée depuis à côté, et elle la voit : son plan y compte la pleine lumière.
        from donjon.deplacement_objet import deplacer
        from donjon.esprits import constater_lumiere_devant
        from tests.support import refusee
        m = refusee(calme(relais(), "marchand", "ilse", "aubin"))
        lire(m, "brune")["besoins"]["faim"] = 85.0
        deplacer(m, "crochets", "brune")
        for i, id in enumerate(("marchand", "ilse", "aubin")):
            placer(m, id, "crypte", (2 + i, 2))
        placer(m, "brune", "antichambre", (8, 2))
        percevoir_tous(m)
        constater_lumiere_devant(m, "brune", "reserve")
        self.assertEqual(lire(m, "brune")["croyances"]["reserve"]["lumiere"]["valeur"], 1)
        placer(m, "brune", "antichambre", (5, 2))
        m.data["minutes"] += 3
        deplacer(m, "torche", "antichambre", position=[7, 3])
        m.objets["torche"]["allume"] = True
        regarder(m, "brune", "torche")
        percevoir_tous(m)
        m = recharger(m)
        v = Vue(m, "brune")
        self.assertEqual(v.lumiere_devant(depart(m, "brune", v), "reserve"), 2)
        crocheter = next(x for x in planifier(m, "brune", "faim")[1] if x["operation"] == "crocheter")
        self.assertEqual(crocheter["contenu"], {"lumiere": 2})


class AttentePartTests(unittest.TestCase):
    """Une part promise ou vendue s'attend là où elle se sert : ce temps compte, avec ce qu'il laisse
    monter (ses biens laissés, le noir), comme pour tout autre plan."""

    def gorm_reel(self):
        """Cas réel (Relais, graine 42, départ tiré, joueur à la galerie) : à la minute 145, Brune a
        forcé la réserve ; les biens de Gorm le pressent ; le brasero baisse. Sur ``main``, il
        achetait une part des planches d'Aubin à la minute 150, puis retournait l'attendre près du
        brasero, loin de ses biens, sans que le plan ait compté ce temps."""
        m = creer("relais", 42)
        m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
        executer(m, 145)
        return recharger(m)

    def test_gorm_va_chercher_ses_fagots_au_lieu_d_acheter_les_planches(self):
        from donjon.deliberation import urgents
        m = self.gorm_reel()
        self.assertIn("biens", urgents(m, "marchand"))
        self.assertEqual(gardes(m, "marchand"), ("antichambre",))
        m = suivre(m, 10)
        vus = textes(m, "marchand")
        self.assertIn("Gorm, gardien du relais prend les fagots de bois sec.", vus)
        self.assertIn("Gorm, gardien du relais alimente le brasero.", vus)
        self.assertEqual(m.objets["bois"]["charges"], 1)
        self.assertEqual(m.objets["planches"]["charges"], 2)
        self.assertFalse(any("planches" in t for t in vus))

    def test_l_attente_d_une_part_se_compte_la_ou_elle_se_sert(self):
        # Autre cas de même nature : la part de vivres que Gorm a promise à Brune se sert près des
        # vivres, dans le refuge ; le refuge plongé dans le noir, l'attente y coûte ce noir.
        m = calme(relais(), "marchand", "ilse", "aubin")
        lire(m, "brune")["besoins"]["faim"] = 80.0
        placer(m, "brune", "echoppe", (3, 2))
        placer(m, "marchand", "echoppe", (4, 2))
        percevoir_tous(m)
        from unittest.mock import patch
        from donjon.echanges import demander
        from donjon.monde import Monde
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "brune", "marchand", "vivres"), "promis")
        m = recharger(m)
        v = Vue(m, "brune")
        e = depart(m, "brune", v).apres(salle="antichambre")
        attente = [g for g in gestes(v, e) if not g[2] and ("part", "vivres") in g[3].faits]
        # Gorm vient de la conduite jusqu'au refuge, puis sert : deux minutes, comptées.
        self.assertEqual([(g[1], g[4]) for g in attente], [(2, 2)])
        lumiere = planifier(m, "brune", "faim")
        croire(m, "brune", "antichambre", "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
        from donjon.planification import _MEMOIRE, chercher, a_mange
        _MEMOIRE.clear()
        sombre = chercher(m, "brune", a_mange, emplois=("manger",), motif="faim")
        _MEMOIRE.clear()
        croire(m, "brune", "antichambre", "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "vu")
        claire = chercher(m, "brune", a_mange, emplois=("manger",), motif="faim")
        self.assertEqual(lumiere[1], [{"operation": "aller", "cible": "", "outil": "", "lieu": "antichambre",
                                       "condition": ""}])
        self.assertGreater(sombre[0], claire[0])
        # Dans le monde : elle va attendre sa part près des vivres, et Gorm la lui sert.
        m = suivre(m, 8, lambda m: any(s["type"] == "nourri" for s in lire(m, "brune")["memoire"]))
        self.assertEqual(m.objets["brune"]["lieu"], "antichambre")
        self.assertTrue(any(s["type"] == "nourri" and s["de"] == "marchand" for s in lire(m, "brune")["memoire"]))


class GardienTests(unittest.TestCase):
    """Un gardien ne laisse pas à qui le menace le bien qu'il garde pour aller s'abriter de lui."""

    def bram_et_odon(self, courage=None):
        """Cas réel (mine ; limite relevée par la branche ``besoins``) : Bram garde la paie au bureau,
        une lampe allumée en main ; Odon, dont il se méfie, y entre pour la paie. Ses biens ne le
        pressent pas, sa sécurité si ; il croit Josse au baraquement éclairé."""
        from donjon.deplacement_objet import deplacer
        m = creer("mine", 1985, "fixe")
        calme(m, *MINEURS)
        deplacer(m, "lampe_filon", "bram")
        m.objets["lampe_filon"]["allume"] = True
        placer(m, "odon", "bureau", (2, 2))
        if courage is not None:
            m.objets["bram"]["profil"]["valeurs"]["courage"] = courage
        percevoir_tous(m)
        croire(m, "bram", "josse", "fiable", True, "vu")
        lire(m, "bram")["besoins"].update(biens=30.0, securite=70.0)
        return recharger(m)

    def test_bram_reste_pres_de_la_paie_et_appelle_a_l_aide(self):
        m = self.bram_et_odon()
        self.assertEqual(menaces(m, "bram"), ("bureau",))
        self.assertEqual(gardes(m, "bram"), ("bureau",))
        m = suivre(m, 5)
        self.assertEqual(m.objets["bram"]["lieu"], "bureau")
        self.assertIn("Bram appelle à l'aide.", textes(m, "bram"))
        self.assertEqual(m.objets["paie"]["lieu"], "coffre_paie")
        # Josse, qui le protège, accourt au bureau.
        self.assertEqual(m.objets["josse"]["lieu"], "bureau")

    def test_plus_courageux_il_reste_et_surveille_sans_appeler(self):
        m = suivre(self.bram_et_odon(courage=90), 10)
        self.assertEqual(m.objets["bram"]["lieu"], "bureau")
        self.assertNotIn("Bram appelle à l'aide.", textes(m, "bram"))
        self.assertEqual(m.objets["paie"]["lieu"], "coffre_paie")

    def test_gorm_ne_laisse_pas_la_reserve_a_brune(self):
        # Autre cas de même nature (Relais) : Gorm, au refuge avec sa réserve, se méfie de Brune qui
        # s'y tient ; il croit Aubin et Ilse dans la conduite éclairée.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        placer(m, "marchand", "antichambre", (6, 3))
        placer(m, "brune", "antichambre", (7, 3))
        placer(m, "aubin", "echoppe", (3, 2))
        placer(m, "ilse", "echoppe", (4, 2))
        percevoir_tous(m)
        croire(m, "marchand", "brune", "fiable", False, "vu")
        for x, case in (("aubin", [3, 2]), ("ilse", [4, 2])):
            croire(m, "marchand", x, "fiable", True, "vu")
            croire(m, "marchand", x, "lieu", "echoppe", "vu", salle="echoppe", case=case)
        lire(m, "marchand")["besoins"]["securite"] = 75.0
        m = suivre(recharger(m), 4)
        self.assertEqual(m.objets["marchand"]["lieu"], "antichambre")
        self.assertIn("Gorm appelle à l'aide.", textes(m, "marchand"))
        # Sans bien menacé (Brune ailleurs), rien ne le retient : il va s'abriter près d'Aubin.
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        placer(m, "marchand", "antichambre", (6, 3))
        placer(m, "brune", "beffroi", (2, 2))
        placer(m, "aubin", "echoppe", (3, 2))
        placer(m, "ilse", "echoppe", (4, 2))
        percevoir_tous(m)
        for x, case in (("aubin", [3, 2]), ("ilse", [4, 2])):
            croire(m, "marchand", x, "fiable", True, "vu")
            croire(m, "marchand", x, "lieu", "echoppe", "vu", salle="echoppe", case=case)
        lire(m, "marchand")["besoins"]["securite"] = 75.0
        self.assertEqual(menaces(m, "marchand"), ())
        m = suivre(recharger(m), 3)
        self.assertEqual(m.objets["marchand"]["lieu"], "echoppe")


if __name__ == "__main__":
    unittest.main()
