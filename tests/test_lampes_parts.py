"""Des parts pour les gestes qui rechargent une source ; état et rendu après chaque recharge."""
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer, executer
from donjon.deplacement_objet import deplacer
from donjon.echanges import demander, executer as echanger, garde, necessaire
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.operations import etape, sequence
from donjon.paroles import preparer_parole
from donjon.perception import eclairage, recharge
from donjon.planification import eclairer
from donjon.rendu import decrire_perception
from tests.support import calme, lier, regarder, sans_le_sou
from tests.test_parts_achetees import parole
from tests.test_tensions import placer, recharger, vivre


def nuit_noire(scenario, qui, donneur, source, lot, salle):
    m = creer(scenario, 1985, "fixe")
    ids = [k for k, o in m.objets.items() if o.get("profil")]
    calme(m, *ids)
    for k, o in m.objets.items():
        if "allume" in o:
            o.update(allume=False, combustible=0)
            if k != source:
                o["contenu"] = {"matiere": "cire"}
        if "combustible" in o.get("usages", ()) and k != lot:
            o["charges"] = 0
    ailleurs = "dortoir" if scenario == "auberge" else "bureau"
    for i, id in enumerate(x for x in ids if x not in (qui, donneur)):
        placer(m, id, ailleurs, (1 + i % 4, 1 + i // 4))
    placer(m, qui, salle, (2, 2))
    placer(m, donneur, salle, (3, 2))
    deplacer(m, source, qui)
    m.objets[source]["proprietaire"] = qui
    deplacer(m, lot, salle, position=[3, 1])
    m.objets[lot].update(proprietaire=donneur, charges=3)
    m.joueur.update(salle=salle, position=[1, 2])
    briquet = "briquet_odile" if scenario == "auberge" else "briquet"
    deplacer(m, briquet, qui)
    m.objets[briquet]["proprietaire"] = qui
    percevoir_tous(m)
    for id in (qui, donneur):
        for s in m.data["salles"]:
            croire(m, id, s, "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
        for k, o in m.objets.items():
            if "allume" in o:
                croire(m, id, k, "etat", {"allume": False, "faible": False, "charge": False}, "vu")
            if "combustible" in o.get("usages", ()):
                croire(m, id, k, "etat", {"disponible": bool(o["charges"])}, "savoir")
        croire(m, id, lot, "lieu", salle, "savoir", salle=salle, case=[3, 1])
        croire(m, id, lot, "etat", {"disponible": True}, "savoir")
        croire(m, id, qui, "lieu", salle, "vu", salle=salle, case=[2, 2])
        croire(m, id, donneur, "lieu", salle, "vu", salle=salle, case=[3, 2])
    lire(m, qui)["besoins"]["securite"] = 90.0
    m.objets[qui]["profil"]["valeurs"]["honnetete"] = 100
    # Le choix se fait sur ce qui recharge sa source, même s'il porte déjà du combustible incompatible.
    autre = "fagots_etable" if scenario == "auberge" else "bois_gaspard"
    deplacer(m, autre, qui)
    m.objets[autre].update(proprietaire=qui, charges=1)
    return recharger(sans_le_sou(m, qui))


class PartsPourSourcesTests(unittest.TestCase):
    def test_cas_reel_auberge_apres_huit_heures_l_huile_achetee_recharge_la_lanterne_vide(self):
        # La vraie nuit épuise les 400 minutes de la lanterne. On ne remplace ni les autres
        # sources ni les ressources du scénario pour obtenir ce constat.
        m = creer("auberge", 1985, "tire")
        m.joueur.update(salle="dortoir", position=[1, 3])
        executer(m, 480)
        m = recharger(m)
        self.assertEqual(m.objets["lanterne_etable"]["combustible"], 0)
        self.assertFalse(m.objets["lanterne_etable"]["allume"])
        # Corvus rejoint Odile dans l'étable pour lui demander de l'huile, par la parole typée.
        calme(m, *(k for k, o in m.objets.items() if o.get("profil")))
        # Scène de vente : elle accepte de ne garder qu'une part pour elle.
        # Sur 881db69, une part a été préparée pour Lucien : les deux parts
        # restantes égalaient sa réserve de deux, et son refus était juste.
        # On ne rajoute aucune huile ; on explicite le surplus qu'elle vend.
        m.objets["odile"]["profil"]["reserve"] = 1
        m.joueur.update(salle="etable", position=[4, 1])
        # La nuit peut laisser un autre PNJ à l'ancien emplacement d'Odile.
        # Installer la conversation au contact, sans superposer les corps.
        from donjon.geometrie import cases, distance
        from donjon.pnj import occupants
        from donjon.spatial import _case_libre
        prises_joueur = occupants(m, sauf="joueur")
        place_joueur = min((c for c in cases(m.data["salles"]["etable"])
                            if ("etable", c) not in prises_joueur and _case_libre(m, "etable", c)),
                           key=lambda c: (distance(c, (4, 1)), c))
        m.joueur["position"] = list(place_joueur)
        prises = occupants(m, sauf="odile")
        libres = [c for c in cases(m.data["salles"]["etable"])
                  if ("etable", c) not in prises and _case_libre(m, "etable", c)
                  and distance(c, place_joueur) <= 1]
        placer(m, "odile", "etable", min(libres, key=lambda c: (distance(c, (3, 1)), c)))
        regarder(m, "joueur", "odile")
        regarder(m, "odile", "joueur")
        # La nuit peut laisser l'huile au cellier et Odile hors de vue dans le
        # noir. La scène de vente établit ce qu'elle a sous la main et sa voix.
        deplacer(m, "pot_huile", "odile")
        percevoir_tous(m)
        from donjon import ecoute
        from donjon.ouie import retentir
        from donjon.temps import instant
        from donjon.voix import se_nommer
        retentir(m, "odile", "dire", texte="Je suis Odile.", cites=["odile"], vers=["joueur"])
        se_nommer(m, "joueur", "odile", "odile")
        ecoute.retenir(m, ecoute.entendus(m, instant(m) - 1, 0))
        m = recharger(m)
        # Ce cas porte sur la vente d'une réserve disponible : une autre nuit
        # peut donner à Odile un plan qui l'emploie, et justifierait son refus.
        self.assertFalse(necessaire(m, "odile", "pot_huile"), lire(m, "odile")["intention"])
        self.assertFalse(garde(m, "odile", m.objets["pot_huile"]))
        huile_avant = m.objets["pot_huile"]["charges"]
        texte = "Odile, je t'achète une part de ton huile pour une pièce."
        bourse_avant = m.joueur["or"]
        objets_avant = set(m.objets)
        travail, rapport = preparer_parole(m, parole("odile", texte, "demande", "pot_huile", "1"))
        # À portée de main, elle remet la part aussitôt ; sinon elle promet de
        # la remettre. L'état ci-dessous contrôle la livraison dans les deux cas.
        self.assertTrue(any("une part du pot d'huile" in f for f in rapport["faits"]), rapport)
        m = recharger(travail)
        # Une part peut déjà avoir été préparée pour un PNJ pendant la nuit.
        piece = next(k for k in m.objets if k not in objets_avant and k.startswith("pot_huile_"))
        for _ in range(20):
            m, _ = vivre(m, 1)
            if m.objets[piece]["lieu"] == "joueur":
                break
        self.assertEqual(m.objets[piece]["lieu"], "joueur")
        self.assertEqual(m.objets[piece]["proprietaire"], "joueur")
        self.assertEqual(m.joueur["or"], bourse_avant - 1)
        regarder(m, "joueur", "lanterne_etable")
        moteur = Moteur(m)
        rendu = moteur.executer(moteur.preparer(sequence(
            etape("deplacer", "lanterne_etable", destination="joueur"), etape("alimenter", "lanterne_etable", outil=piece),
            etape("allumer", "lanterne_etable", outil="briquet"))))
        m = recharger(m)
        self.assertTrue(m.objets["lanterne_etable"]["allume"])
        self.assertGreater(m.objets["lanterne_etable"]["combustible"], 0)
        self.assertEqual(m.objets[piece]["charges"], 0)
        self.assertEqual(m.objets["pot_huile"]["charges"], huile_avant - 1)
        self.assertIn("lanterne", rendu)
        self.assertIn("que tu portes, éclaire la pièce", decrire_perception(m))

    def parcours(self, scenario, qui, donneur, source, lot, salle):
        m = nuit_noire(scenario, qui, donneur, source, lot, salle)
        plan = eclairer(m, qui)
        self.assertIsNotNone(plan)
        self.assertEqual(eclairer(m, qui), plan)  # Les marqueurs de replanification résistent au cache.
        demande = next(x for x in plan[1] if x["operation"] == "demander" and x["outil"] == lot)
        self.assertTrue(demande["contenu"]["remettre_part"])
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(echanger(m, qui, demande, []))
        m = recharger(m)
        # Un accord n'a ni rempli ni allumé la source ; une charge est réellement mise de côté.
        self.assertEqual(m.objets[source]["combustible"], 0)
        self.assertFalse(m.objets[source]["allume"])
        self.assertEqual(m.objets[lot]["charges"], 2)
        self.assertTrue(any(s["type"] == "promis" and s.get("part") for s in lire(m, qui)["memoire"]))
        attentes = eclairer(m, qui)
        self.assertIsNotNone(attentes)
        self.assertFalse(any(x["operation"] == "alimenter" for x in attentes[1]))
        self.assertEqual(eclairer(m, qui), attentes)
        lignes = []
        for _ in range(20):
            m, rendu = vivre(m, 1, jet=20)
            lignes += rendu
            if m.objets[source]["allume"]:
                break
        m = recharger(m)
        self.assertTrue(m.objets[source]["allume"], m.data.get("chronique"))
        self.assertGreater(m.objets[source]["combustible"], 0)
        self.assertEqual(m.objets[lot]["charges"], 2)
        self.assertTrue(any(o.get("proprietaire") == qui and k.startswith(lot + "_") and o["charges"] == 0
                            for k, o in m.objets.items()))
        self.assertFalse(lire(m, donneur)["engagements"])
        self.assertTrue(any("alimente" in x["texte"] for x in m.data.get("chronique", [])))
        self.assertGreater(eclairage(m)["niveau"], 0)
        self.assertIn("éclaire la pièce", decrire_perception(m))

    def test_auberge_lanterne_etable_vide_part_demandee_recharge_et_rendu(self):
        self.parcours("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable")

    def test_mine_lampe_remy_vide_part_demandee_recharge_et_rendu(self):
        self.parcours("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")

    def test_mine_lampe_vide_recharge_avec_le_bidon_pose_sans_echange(self):
        m = nuit_noire("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        m.objets["bidon_huile"].pop("proprietaire")
        m = recharger(m)
        p = eclairer(m, "remy")
        self.assertTrue(any(x["operation"] == "alimenter" and x["outil"] == "bidon_huile" for x in p[1]))
        m, lignes = vivre(m, 8, jet=20)
        self.assertTrue(m.objets["lampe_remy"]["allume"], lignes)
        self.assertEqual(m.objets["bidon_huile"]["charges"], 2)
        self.assertGreater(eclairage(m)["niveau"], 0)

    def test_le_contenu_declare_decide_aussi_pour_une_autre_substance(self):
        m = nuit_noire("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        # Le même contrat sans huile : la réserve et cette seule source déclarent de la cire.
        for k, o in m.objets.items():
            if "allume" in o and k != "lampe_remy":
                o["contenu"] = {"matiere": "huile"}
        m.objets["bidon_huile"]["contenu"] = {"matiere": "cire"}
        m.objets["lampe_remy"]["contenu"] = {"matiere": "cire"}
        m = recharger(m)
        self.assertTrue(recharge(m.objets["lampe_remy"], m.objets["bidon_huile"]))
        plan = eclairer(m, "remy")
        demande = next(x for x in plan[1] if x["operation"] == "demander" and x["outil"] == "bidon_huile")
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(echanger(m, "remy", demande, []))
        for _ in range(10):
            m, _ = vivre(recharger(m), 1, jet=20)
            if m.objets["lampe_remy"]["allume"]:
                break
        self.assertTrue(m.objets["lampe_remy"]["allume"])
        self.assertGreater(eclairage(m)["niveau"], 0)
        self.assertIn("éclaire la pièce", decrire_perception(recharger(m)))

    def test_les_refus_la_reserve_et_le_prix_valent_pour_toute_substance(self):
        for scenario, qui, donneur, source, lot, salle in (
            ("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable"),
            ("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve"),
        ):
            with self.subTest(scenario=scenario):
                m = nuit_noire(scenario, qui, donneur, source, lot, salle)
                lier(m, donneur, qui, False, "vu")
                self.assertEqual(demander(m, qui, donneur, lot, prix=1, remettre_part=True), "mefiance")
                lier(m, donneur, qui, True, "vu")
                m.objets[lot]["charges"] = 1
                self.assertEqual(demander(m, qui, donneur, lot, remettre_part=True), "necessaire")
                m.objets[lot]["charges"] = 3
                m.data["finances_pnj"][qui] = 5
                self.assertEqual(demander(m, qui, donneur, lot, prix=1, remettre_part=True), "vendu")
                m = recharger(m)
                self.assertEqual(m.data["finances_pnj"][qui], 4)
                self.assertEqual(m.objets[lot]["charges"], 2)
                self.assertFalse(m.objets[source]["allume"])

    def test_la_part_physique_conserve_son_contenu_et_recharge_apres_sauvegarde(self):
        from donjon.matiere import valider
        m = nuit_noire("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        lot = m.objets["bidon_huile"]
        # Trois blocs de cire : le contenant matériel et sa substance combustible diffèrent.
        lot.update(masse=1.8, materiau="bois", contenu={"matiere": "cire"})
        lot["physique"] = valider(lot, {"forme": "barre", "matiere": "bois", "pieces": 3,
                                       "nom_piece": "bloc de cire", "dimensions": {"longueur_cm": 100, "largeur_cm": 10, "epaisseur_cm": 1}})
        m.objets["lampe_remy"]["contenu"] = {"matiere": "cire"}
        for k, o in m.objets.items():
            if "allume" in o and k != "lampe_remy":
                o["contenu"] = {"matiere": "huile"}
        m = recharger(m)
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "remy", "gaspard", "bidon_huile", remettre_part=True), "promis")
        lot, piece = m.objets["bidon_huile"], m.objets["bidon_huile_1"]
        self.assertEqual((lot["charges"], lot["physique"]["pieces"]), (2, 2))
        self.assertEqual((piece["charges"], piece["physique"]["pieces"]), (1, 1))
        self.assertAlmostEqual(lot["masse"] + piece["masse"], 1.8)
        self.assertEqual(piece["contenu"], {"matiere": "cire"})
        self.assertIsNot(piece["contenu"], lot["contenu"])
        self.assertTrue(recharge(m.objets["lampe_remy"], piece))
        m = recharger(m)
        self.assertIsNot(m.objets["bidon_huile_1"]["contenu"], m.objets["bidon_huile"]["contenu"])
        for _ in range(10):
            m, _ = vivre(m, 1, jet=20)
            if m.objets["lampe_remy"]["allume"]:
                break
        m = recharger(m)
        self.assertTrue(m.objets["lampe_remy"]["allume"])
        self.assertEqual(m.objets["bidon_huile_1"]["charges"], 0)
        self.assertEqual(m.objets["bidon_huile"]["charges"], 2)
        self.assertIn("éclaire la pièce", decrire_perception(m))

    def test_une_reserve_portee_fournit_une_part_demandee_ou_achetee(self):
        from donjon.deliberation import retenir_refus
        for scenario, qui, donneur, source, lot, salle in (
            ("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable"),
            ("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve"),
        ):
            for prix in (0, 1):
                with self.subTest(scenario=scenario, prix=prix):
                    m = nuit_noire(scenario, qui, donneur, source, lot, salle)
                    deplacer(m, lot, donneur)
                    croire(m, qui, lot, "lieu", donneur, "savoir", salle=salle, case=[3, 2])
                    if prix:
                        m.data["finances_pnj"][qui] = 5
                        retenir_refus(m, qui, donneur, "demander", "refus", objet=lot)
                    m = recharger(m)
                    p = eclairer(m, qui)
                    op = "acheter" if prix else "demander"
                    geste = next(x for x in p[1] if x["operation"] == op and x["outil"] == lot)
                    with patch.object(Monde, "d20", return_value=20):
                        self.assertTrue(echanger(m, qui, geste, []))
                    m = recharger(m)
                    self.assertEqual(m.objets[lot]["lieu"], donneur)
                    self.assertEqual(m.objets[lot]["charges"], 2)
                    self.assertEqual(m.objets[lot + "_1"]["lieu"], qui)
                    self.assertFalse(lire(m, donneur)["engagements"])
                    self.assertEqual(m.objets[source]["combustible"], 0)
                    for _ in range(10):
                        m, _ = vivre(m, 1, jet=20)
                        if m.objets[source]["allume"]:
                            break
                    self.assertTrue(m.objets[source]["allume"])
                    self.assertIn("éclaire la pièce", decrire_perception(recharger(m)))

    def test_une_source_explicitement_incompatible_ne_se_remplace_pas(self):
        m = nuit_noire("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        self.assertFalse(recharge(m.objets["poele"], m.objets["bidon_huile"]))
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "remy", "gaspard", "bidon_huile", foyer="poele"), "impossible")
        m = recharger(m)
        self.assertEqual(m.objets["bidon_huile"]["charges"], 3)
        self.assertFalse(lire(m, "gaspard")["engagements"])

    def test_une_promesse_identifie_son_lot_sans_deduire_la_provenance_du_nom(self):
        m = nuit_noire("mine", "remy", "gaspard", "lampe_remy", "bidon_huile", "reserve")
        with patch.object(Monde, "d20", return_value=20), patch("donjon.matiere.id_piece", return_value="ration_reservee"):
            self.assertEqual(demander(m, "remy", "gaspard", "bidon_huile", remettre_part=True), "promis")
        m = recharger(m)
        eng = lire(m, "gaspard")["engagements"][0]
        self.assertEqual(eng["lot"], "bidon_huile")
        self.assertEqual(eng["condition"]["objet"], "ration_reservee")
        self.assertEqual(demander(m, "remy", "gaspard", "bidon_huile", remettre_part=True), "promis")
        self.assertEqual(m.objets["bidon_huile"]["charges"], 2)
        for _ in range(10):
            m, _ = vivre(recharger(m), 1, jet=20)
            if m.objets["lampe_remy"]["allume"]:
                break
        self.assertTrue(m.objets["lampe_remy"]["allume"])
        self.assertEqual(m.objets["ration_reservee"]["charges"], 0)
        self.assertIn("éclaire la pièce", decrire_perception(recharger(m)))

    def test_joueur_demande_et_achete_par_la_parole_typee_puis_alimente(self):
        for prix, portee in ((0, False), (1, False), (0, True), (1, True)):
            with self.subTest(prix=prix, portee=portee):
                m = nuit_noire("auberge", "joss", "odile", "lanterne_etable", "pot_huile", "etable")
                if portee:
                    deplacer(m, "pot_huile", "odile")
                m.objets["lanterne_etable"].pop("proprietaire")
                # Une lumière permet de désigner le pot et d'identifier Odile pour la parole du joueur.
                m.objets["chandelle_corvus"].update(allume=True, combustible=100)
                regarder(m, "joueur", "odile")
                regarder(m, "odile", "joueur")
                percevoir_tous(m)
                m = recharger(m)
                avant = m.joueur["or"]
                with patch.object(Monde, "d20", return_value=20):
                    travail, rapport = preparer_parole(m, parole("odile", "Odile, donne-moi une part de ton huile.",
                                                                 "demande", "pot_huile", str(prix) if prix else ""))
                self.assertTrue(any(("remettre" in f or "te remet" in f) for f in rapport["faits"]), rapport)
                self.assertFalse(any("entretenir le feu" in f for f in rapport["faits"]))
                m, lignes = vivre(recharger(travail), 5, jet=20)
                piece = "pot_huile_1"
                self.assertEqual(m.objets[piece]["lieu"], "joueur", lignes)
                self.assertEqual(m.joueur["or"], avant - prix)
                self.assertEqual(any("tu l'avais payé" in x for x in lignes), bool(prix and not portee))
                deplacer(m, "lanterne_etable", "joueur")
                moteur = Moteur(m)
                rendu = moteur.executer(moteur.preparer(sequence(etape("alimenter", "lanterne_etable", outil=piece))))
                m = recharger(m)
                self.assertGreater(m.objets["lanterne_etable"]["combustible"], 0)
                self.assertEqual(m.objets[piece]["charges"], 0)
                self.assertTrue(rendu)


if __name__ == "__main__":
    unittest.main()
