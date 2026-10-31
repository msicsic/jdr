"""Droits datés confiés : parole, garde, choix différé, recharge et rendu."""
import copy
import unittest
from unittest.mock import patch

from donjon import agendas, planification, social
from donjon.banc_pnj import creer
from donjon.biens import preter
from donjon.deplacement_objet import deplacer
from donjon.esprits import (constater_fin_objet, constater_possession, croire,
                            lire, memoriser, percevoir)
from donjon.monde import Monde
from donjon.geometrie import cases
from donjon.rendu import regarder
from donjon.temps import ecouler
from donjon.scene import scene_percue as scene_web
from tests.support import calme, lier, presentes, regarder as orienter
from tests.test_constats_partages import scene
from tests.test_social import placer
from tests.test_tensions import recharger, vivre


def garde(scenario="relais", objet="cle_reserve"):
    if scenario == "relais":
        m, gardien, temoin, porteur = scene(), "marchand", "ilse", "brune"
        salle, distante = "antichambre", "crypte"
    else:
        m = creer("auberge", 1985, "fixe")
        personnages = [x for x, o in m.objets.items() if o.get("profil")]
        m = calme(m, *personnages)
        gardien = "anselme"
        temoin, porteur = [x for x in personnages if x != gardien][:2]
        salle, distante = "salle_commune", "cuisine"
        places = iter(sorted(c for c in cases(m.data["salles"][distante]) if c != (3, 3)))
        for x in personnages:
            placer(m, x, distante, next(places))
        placer(m, gardien, salle, [3, 4])
        placer(m, temoin, salle, [2, 4])
        m.joueur.update(salle=salle, position=[2, 3])
    m.objets[gardien]["profil"].update(
        pulsions=[], agendas=[{"sorte": "garder", "parametres": {"objet": objet}}])
    lire(m, gardien)["pulsions"] = []
    m.objets[objet].update(proprietaire=gardien, longueur_cm=100)
    deplacer(m, objet, distante, [4, 3])
    croire(m, gardien, objet, "lieu", distante, "vu", salle=distante, case=[4, 3])
    agendas.actualiser(m, gardien)
    ecouler(m, 600)
    # Le tiers voit le bien porté ailleurs ; le gardien n'y assiste pas.
    deplacer(m, objet, porteur)
    placer(m, temoin, distante, [3, 3])
    orienter(m, temoin, porteur)
    percevoir(m, temoin)
    assert lire(m, temoin)["croyances"][objet]["lieu"]["possession"]["porteur"] == porteur
    placer(m, temoin, salle, [2, 4])
    orienter(m, temoin, gardien)
    orienter(m, gardien, temoin)
    orienter(m, "joueur", temoin)
    lier(m, temoin, gardien, True)
    lier(m, gardien, temoin, True)
    # Isoler la confidence étudiée des autres nouvelles ordinaires de la scène.
    e = lire(m, temoin)
    e["memoire"] = []
    e["croyances"] = {objet: e["croyances"][objet]}
    m.data["connus"] = sorted(m.objets)
    presentes(m)
    return recharger(m), gardien, temoin, porteur


def noyau(m, temoin, objet, attribut="lieu"):
    return next(n[1] for n in social.nouvelles(m, temoin)
                if n[1]["type"] == "constat" and n[1]["objet"] == objet
                and n[1]["attribut"] == attribut)


class GardeOuidireTests(unittest.TestCase):
    def test_contenant_inconnu_cite_sans_fuite_du_nom_au_joueur(self):
        from donjon.francais import designer
        from donjon.paroles import _connu_du_joueur
        m, g, t, p = garde("auberge", "ballot")
        contenant = "receptacle_cache"
        m.objets[contenant] = copy.deepcopy(m.objets["coffre_marchand"])
        m.objets[contenant]["id"] = contenant
        m.objets[contenant]["nom"] = "écrin de basalte"
        m.objets[contenant]["aliases"] = ["écrin de basalte"]
        self.assertFalse(_connu_du_joueur(m, contenant))
        croire(m, t, "ballot", "lieu", contenant, "vu",
               salle=m.objets[contenant]["lieu"], case=[4, 3],
               possession={"porteur": None, "proprietaire": None, "permis": False,
                           "remis_par": None, "remise_autorisee": False})
        m, texte = self.confier(recharger(m), t)
        self.assertNotIn(designer(m.objets[contenant]), texte)
        self.assertEqual(lire(m, g)["croyances"]["ballot"]["lieu"]["valeur"], contenant)
        r = recharger(m)
        self.assertEqual(m.data, r.data)
        self.assertEqual(regarder(m), regarder(r))
        self.assertEqual(scene_web(m), scene_web(r))

    def test_preuves_sans_porteur_salle_et_contenant_transmises_et_rechargees(self):
        from donjon.francais import designer, lieu
        from donjon.paroles import _connu_du_joueur, resoudre
        for scenario, objet, endroit in (("relais", "cle_reserve", "crypte"),
                                         ("auberge", "ballot", "coffre_marchand")):
            for connu in (False, True):
                with self.subTest(scenario=scenario, connu=connu):
                    m, g, t, p = garde(scenario, objet)
                    # Le témoin connaît le lieu ; cela ne présente pas son nom
                    # à Corvus. La scène nommée suppose ce souvenir explicitement.
                    m.data["connus"] = [x for x in m.data["connus"] if x != endroit]
                    if connu:
                        m.data["connus"].append(endroit)
                    possession = {"porteur": None, "proprietaire": None, "permis": False,
                                  "remis_par": None, "remise_autorisee": False}
                    salle = endroit if endroit in m.data["salles"] else m.objets[endroit]["lieu"]
                    # Preuve héritée admise à la recharge. Le bien est depuis
                    # porté ailleurs : le récit ne doit pas lire ce lieu privé.
                    croire(m, t, objet, "lieu", endroit, "vu", salle=salle,
                           case=[4, 3], possession=possession)
                    m = recharger(m)
                    self.assertEqual(_connu_du_joueur(m, endroit), connu)
                    self.assertEqual(resoudre(m, endroit), endroit if connu else None)
                    avant = copy.deepcopy(m.objets[objet])
                    m, texte = self.confier(m, t)
                    attendu = lieu(m.data["salles"][endroit]) if endroit in m.data["salles"] else designer(m.objets[endroit])
                    if connu:
                        self.assertIn("dans " + attendu, texte)
                    else:
                        self.assertNotIn(attendu, texte)
                    self.assertNotIn("aux mains de", texte)
                    self.assertNotIn("permission", texte)
                    self.assertEqual(m.objets[objet], avant)
                    c = lire(m, g)["croyances"][objet]["lieu"]
                    self.assertEqual((c["valeur"], c["possession"]), (endroit, possession))
                    r = recharger(m)
                    self.assertEqual(m.data, r.data)
                    self.assertEqual(regarder(m), regarder(r))
                    self.assertEqual(scene_web(m), scene_web(r))
                    self.assertEqual(_connu_du_joueur(r, endroit), connu)
                    self.assertEqual(resoudre(r, endroit), endroit if connu else None)
                    if not connu:
                        nom = (r.data["salles"].get(endroit) or r.objets[endroit])["nom"].casefold()
                        self.assertNotIn(nom, regarder(r).casefold())
                        self.assertNotIn(nom, str(scene_web(r)).casefold())

    def confier(self, m, temoin):
        lignes = []
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(social.bavarder(m, temoin, lignes))
        m = recharger(m)
        self.assertEqual(regarder(m), regarder(recharger(m)))
        self.assertEqual(scene_web(m), scene_web(recharger(m)))
        self.assertTrue(lignes)
        return m, "\n".join(lignes)

    def fin(self, m, gardien, cause):
        avant = copy.deepcopy(m.data)
        with self.assertRaises(RuntimeError):
            with planification.vues_du_choix(m, gardien):
                agendas.actualiser(m, gardien)
                raise RuntimeError("choix interrompu")
        self.assertEqual(m.data, avant)
        with planification.vues_du_choix(m, gardien):
            agendas.actualiser(m, gardien)
            self.assertEqual(m.data, avant)
        m = recharger(m)
        a = agendas.projets(m, gardien)[0]
        self.assertEqual((a["etat"], a["raison"]), ("abandonne", "bien cru " + cause))
        self.assertTrue(any("abandonne (bien cru " + cause + ")" in c["texte"]
                            for c in m.data["chronique"]))
        self.assertEqual(m.data, recharger(m).data)
        self.assertEqual(regarder(m), regarder(recharger(m)))
        self.assertEqual(scene_web(m), scene_web(recharger(m)))
        return m

    def test_perte_vue_par_un_tiers_dite_malgre_ancienne_accusation(self):
        m, g, t, p = garde()
        accusation = {"type": "vu_porter", "objet": "cle_reserve", "auteur": p}
        lier(m, t, p, False)
        memoriser(m, t, accusation)
        memoriser(m, g, accusation)
        social.retenir_dit(m, t, g, accusation)
        n = noyau(m, t, "cle_reserve")
        self.assertNotEqual(social.faits_dits(n), social.faits_dits(accusation))
        self.assertFalse(social.deja_dit(m, t, g, n))
        m, texte = self.confier(m, t)
        c = lire(m, g)["croyances"]["cle_reserve"]["lieu"]
        self.assertEqual((c["minute"], c["source"], c["confiance"]), (1, "dit:" + t, .7))
        self.assertEqual(c["possession"], n["details"]["possession"])
        self.assertIn("sans permission", texte)
        self.assertEqual(m.objets["cle_reserve"]["lieu"], p)
        self.fin(m, g, "perdu")

    def test_restitution_au_proprietaire_dans_un_autre_scenario(self):
        m, g, t, p = garde("auberge", "ballot")
        m.objets["ballot"]["proprietaire"] = p
        constater_possession(m, t, "ballot", "vu")
        m, texte = self.confier(recharger(m), t)
        self.assertIn("ce bien appartient", texte)
        self.assertEqual(m.objets["ballot"]["lieu"], p)
        self.fin(m, g, "rendu")

    def test_destruction_et_consommation_confiees(self):
        for objet, champ, cause in (("couteau", "integrite", "detruit"),
                                    ("vivres", "portions", "consomme")):
            m, g, t, p = garde(objet=objet)
            m.objets[objet][champ] = 0
            constater_fin_objet(m, t, objet, "vu")
            # Isoler la fin du constat de disponibilité déjà offert par le lot 55.
            lire(m, t)["croyances"][objet].pop("etat", None)
            m, texte = self.confier(recharger(m), t)
            self.assertIn("détruit" if cause == "detruit" else "consomm", texte)
            self.assertEqual(lire(m, g)["croyances"][objet]["fin"]["source"], "dit:" + t)
            self.fin(m, g, cause)

    def test_preuve_propre_plus_recente_ou_meme_minute_prime(self):
        for dt in (0, 600):
            m, g, t, p = garde()
            n = noyau(m, t, "cle_reserve")
            ecouler(m, dt)
            preter(m, "cle_reserve", p)
            constater_possession(m, g, "cle_reserve", "vu")
            avant = copy.deepcopy(lire(m, g)["croyances"]["cle_reserve"])
            with patch.object(Monde, "d20", return_value=20):
                self.assertIsNone(social.recevoir(m, g, t, {"type": "rumeur", "evenement": n, "rang": 0}))
            agendas.actualiser(m, g)
            m = recharger(m)
            self.assertEqual(lire(m, g)["croyances"]["cle_reserve"], avant)
            self.assertNotEqual(agendas.projets(m, g)[0]["etat"], "abandonne")
            self.assertEqual(scene_web(m), scene_web(recharger(m)))

    def test_nouvelle_doutee_ne_termine_pas_la_garde(self):
        m, g, t, p = garde()
        lier(m, g, t, False)
        avant = copy.deepcopy(lire(m, g)["croyances"]["cle_reserve"])
        with patch("donjon.paroles.jet_persuasion", return_value=(False, 0)):
            self.assertTrue(social.bavarder(m, t, []))
        agendas.actualiser(m, g)
        m = recharger(m)
        self.assertEqual(lire(m, g)["croyances"]["cle_reserve"], avant)
        self.assertNotEqual(agendas.projets(m, g)[0]["etat"], "abandonne")
        self.assertTrue(any(s["type"] == "parole_doutee" for s in lire(m, g)["memoire"]))
        self.assertEqual(regarder(m), regarder(recharger(m)))

    def test_droits_dates_et_nouvelle_fausse_sans_permission_inventee(self):
        for permis in (False, True):
            m, g, t, p = garde()
            if permis:
                preter(m, "cle_reserve", p)
                constater_possession(m, t, "cle_reserve", "vu")
            n = copy.deepcopy(noyau(m, t, "cle_reserve"))
            # L'état réel change après le témoignage : l'auditeur n'en sait rien.
            m.data["permissions"] = []
            deplacer(m, "cle_reserve", g)
            m.objets["cle_reserve"]["proprietaire"] = p
            m, _ = self.confier(recharger(m), t)
            self.assertEqual(lire(m, g)["croyances"]["cle_reserve"]["lieu"]["possession"],
                             n["details"]["possession"])
            self.assertEqual(m.objets["cle_reserve"]["lieu"], g)
            if not permis:
                self.fin(m, g, "perdu")
            else:
                agendas.actualiser(m, g)
                self.assertNotEqual(agendas.projets(m, g)[0]["etat"], "abandonne")
                self.assertEqual(m.data, recharger(m).data)

    def test_relais_date_poids_et_changement_de_droits_sans_changer_porteur(self):
        m, g, t, p = garde()
        m, _ = self.confier(m, t)
        n = noyau(m, g, "cle_reserve")
        self.assertEqual(n["observe"], 1)
        relais = next(x for x in social.nouvelles(m, g) if x[1] == n)
        self.assertEqual((relais[2], relais[3]), (1, t))
        # Un second auditeur reçoit réellement le relais, à son poids réduit,
        # même si les droits réels ont changé entre les deux paroles.
        autre = "aubin"
        lire(m, autre)["croyances"].pop("cle_reserve", None)
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(social.recevoir(m, autre, g, {"type": "rumeur", "evenement": n,
                                                         "rang": relais[2]}), "crue")
        c = lire(m, autre)["croyances"]["cle_reserve"]["lieu"]
        self.assertEqual((c["minute"], c["source"], c["confiance"]), (1, "dit:" + g, .56))
        ecouler(m, 600)
        preter(m, "cle_reserve", p)
        constater_possession(m, t, "cle_reserve", "vu")
        nouveau = noyau(m, t, "cle_reserve")
        self.assertFalse(social.deja_dit(m, t, g, nouveau))
        self.assertNotEqual(social.faits_dits(n), social.faits_dits(nouveau))
        m, _ = self.confier(recharger(m), t)
        c = lire(m, g)["croyances"]["cle_reserve"]["lieu"]
        self.assertTrue(c["possession"]["permis"])
        self.assertEqual(c["minute"], 2)
        self.assertEqual(m.data, recharger(m).data)

    def test_fin_ancienne_refusee_par_un_bien_revu_intact_ou_repare(self):
        for repare in (False, True):
            m, g, t, p = garde(objet="couteau")
            m.objets["couteau"]["integrite"] = 0
            constater_fin_objet(m, t, "couteau", "vu")
            n = copy.deepcopy(noyau(m, t, "couteau", "fin"))
            if repare:
                constater_fin_objet(m, g, "couteau", "vu")
            ecouler(m, 600)
            m.objets["couteau"]["integrite"] = 3
            constater_fin_objet(m, g, "couteau", "vu")
            m = recharger(m)
            with patch.object(Monde, "d20", return_value=20):
                self.assertIsNone(social.recevoir(m, g, t, {"type": "rumeur", "evenement": n, "rang": 0}))
            agendas.actualiser(m, g)
            m = recharger(m)
            self.assertIsNone(lire(m, g)["croyances"]["couteau"]["fin"]["valeur"])
            self.assertNotEqual(agendas.projets(m, g)[0]["etat"], "abandonne")
            self.assertEqual(regarder(m), regarder(recharger(m)))
            self.assertEqual(scene_web(m), scene_web(recharger(m)))

    def test_ancienne_accusation_ne_remplace_pas_les_droits_recus(self):
        for minute in (0, 1):
            m, g, t, p = garde()
            m, _ = self.confier(m, t)
            preuve = copy.deepcopy(lire(m, g)["croyances"]["cle_reserve"]["lieu"])
            ancien = {"type": "vu_agir", "auteur": "joueur", "operation": "prendre", "objet": "cle_reserve",
                      "observe": minute, "lieu": {"valeur": "joueur", "salle": "crypte", "case": [1, 1],
                                                  "minute": minute}}
            with patch.object(Monde, "d20", return_value=20):
                social.recevoir(m, g, t, {"type": "rumeur", "evenement": ancien, "rang": 0})
            m = recharger(m)
            self.assertEqual(lire(m, g)["croyances"]["cle_reserve"]["lieu"], preuve)
            self.fin(m, g, "perdu")

    def test_revoir_date_case_ou_source_ne_redit_pas_le_meme_droit(self):
        m, g, t, p = garde()
        m, _ = self.confier(m, t)
        for source in ("vu", "essai"):
            ecouler(m, 600)
            constater_possession(m, t, "cle_reserve", source, salle="crypte", case=[5, 3])
            n = noyau(m, t, "cle_reserve")
            self.assertTrue(social.deja_dit(m, t, g, n))
            self.assertTrue(social._sait(m, g, n))
        self.assertEqual(m.data, recharger(m).data)

    def test_fin_dite_apres_retrait_des_restes_et_relayee(self):
        m, g, t, p = garde(objet="couteau")
        m.objets["couteau"]["integrite"] = 0
        constater_fin_objet(m, t, "couteau", "vu")
        lire(m, t)["croyances"]["couteau"].pop("lieu", None)
        del m.objets["couteau"]
        m, texte = self.confier(recharger(m), t)
        self.assertIn("le couteau à lame fine est détruit", texte)
        self.assertTrue(any(n[1].get("attribut") == "fin" for n in social.nouvelles(m, g)))
        self.fin(m, g, "detruit")

    def test_confidence_et_fin_pendant_le_laps_entier_ou_decoupe(self):
        initial, g, t, p = garde()
        resultats = []
        for tranches in ((2,), (1, 1)):
            m = recharger(initial)
            for duree in tranches:
                m, _ = vivre(m, duree, jet=20)
                m = recharger(m)
            self.assertTrue(any(c.get("constat_confie") and c["pnj"] == t for c in m.data["chronique"]))
            self.assertEqual(agendas.projets(m, g)[0]["raison"], "bien cru perdu")
            resultats.append(m)
        a, b = resultats
        self.assertEqual(a.data, b.data)
        self.assertEqual(regarder(a), regarder(recharger(b)))
        self.assertEqual(scene_web(a), scene_web(recharger(b)))

    def test_meme_laps_entier_ou_decoupe_monde_rendu_scene(self):
        initial, g, t, p = garde()
        initial, _ = self.confier(initial, t)
        entier, _ = vivre(recharger(initial), 2)
        morceaux, _ = vivre(recharger(initial), 1)
        morceaux, _ = vivre(recharger(morceaux), 1)
        self.assertEqual(entier.data, morceaux.data)
        self.assertEqual(agendas.projets(entier, g)[0]["raison"], "bien cru perdu")
        self.assertEqual(regarder(entier), regarder(recharger(morceaux)))
        self.assertEqual(scene_web(entier), scene_web(recharger(morceaux)))

    def test_entrees_recherche_couvrent_la_perte_de_responsabilite(self):
        m, g, t, p = garde()
        def cle():
            with planification.vues_du_choix(m, g):
                v = planification.Vue(m, g)
                return planification._entrees(v, [], 8, 400)
        avant = cle()
        m, _ = self.confier(m, t)
        self.assertNotEqual(avant, cle())
