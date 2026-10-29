"""La dynamique des besoins : l'effet de seuil (un besoin apaisé ne presse de nouveau que nettement
au-dessus de son seuil ; il n'interrompt le plan d'un autre que s'il presse nettement plus), ce
qu'un plan laisse monter chez les autres besoins (un but qui se tient en restant compte ce que le
lieu laisse monter ; à défaut d'un plan qui serve les deux, le plus fort l'emporte et l'autre
s'endure), et l'attente d'un besoin qu'aucun plan ne peut apaiser.

Chaque cas vérifie l'état du monde après rechargement."""

from tests.support import lier
import unittest
from unittest.mock import patch

from donjon.banc_pnj import _oisifs_urgents, creer
from donjon.deliberation import (INERTIE, REPRISE, attentes, deliberer, eveiller, gardes, seuils, urgents)
from donjon.esprits import croire, lire, percevoir_tous
from donjon.planification import NOIR, Vue
from tests.support import calme
from tests.test_tensions import placer, recharger, relais, vivre


def suivre(m, id, minutes, pas=1):
    """Fait vivre le monde et relève la salle de ``id`` après chaque pas (rechargé à chaque pas)."""
    lieux = []
    for _ in range(0, minutes, pas):
        m, _ = vivre(m, pas)
        lieux.append(m.objets[id]["lieu"])
    return m, lieux


def changements(lieux):
    return sum(a != b for a, b in zip(lieux, lieux[1:]))


class SeuilTests(unittest.TestCase):
    """L'effet de seuil, comme un thermostat."""

    def gorm(self):
        m = relais()
        calme(m, "marchand", "brune", "ilse", "aubin")
        return m

    def test_apaise_il_ne_presse_de_nouveau_que_nettement_au_dessus_de_son_seuil(self):
        m = self.gorm()
        b = lire(m, "marchand")["besoins"]
        seuil = seuils(m, "marchand")["devoir"]
        b["devoir"] = seuil + 1.0
        eveiller(m, "marchand", 1)
        self.assertIn("devoir", urgents(m, "marchand"))
        b["devoir"] = seuil - 1.0
        eveiller(m, "marchand", 2)
        m = recharger(m)
        self.assertEqual(lire(m, "marchand")["urgences"]["devoir"], {"etat": "apaise", "depuis": 2})
        lire(m, "marchand")["besoins"]["devoir"] = seuil + REPRISE - 1
        eveiller(m, "marchand", 3)
        self.assertNotIn("devoir", urgents(m, "marchand"))
        lire(m, "marchand")["besoins"]["devoir"] = seuil + REPRISE
        eveiller(m, "marchand", 4)
        m = recharger(m)
        self.assertIn("devoir", urgents(m, "marchand"))
        self.assertEqual(lire(m, "marchand")["urgences"]["devoir"]["etat"], "presse")

    def test_comble_un_besoin_retrouve_son_seuil(self):
        # Un repas, un feu, le repos : bien redescendu, il presse de nouveau à son seuil.
        m = self.gorm()
        b = lire(m, "marchand")["besoins"]
        seuil = seuils(m, "marchand")["faim"]
        b["faim"] = seuil + 5.0
        eveiller(m, "marchand", 1)
        b["faim"] = seuil - REPRISE - 1
        eveiller(m, "marchand", 2)
        self.assertNotIn("faim", lire(m, "marchand")["urgences"])
        b["faim"] = float(seuil)
        self.assertIn("faim", urgents(m, "marchand"))

    def test_un_besoin_n_interrompt_le_plan_d_un_autre_que_s_il_presse_nettement_plus(self):
        m = self.gorm()
        m.objets["ilse"]["profil"]["caracteristiques"]["VOL"] = 12
        s = seuils(m, "ilse")
        b = lire(m, "ilse")["besoins"]
        b.update(securite=s["securite"] + 14.0, chaleur=s["chaleur"] + 12.0)
        lire(m, "ilse")["intention"] = {"but": {"type": "abri", "lieu": "antichambre"}, "motif": "securite",
                                        "plan": [{"operation": "abriter", "cible": "", "outil": "", "lieu": "antichambre",
                                                  "condition": ""}], "depuis": 0, "attente": 0}
        # Le froid presse presque autant : il laisse finir l'abri (et ne le reprend pas à chaque minute).
        self.assertEqual(urgents(m, "ilse", inertie=True), ["securite"])
        self.assertEqual(urgents(m, "ilse")[:2], ["securite", "chaleur"])
        b["chaleur"] = s["chaleur"] + 14.0 + INERTIE + 3  # VOL 12 / 4
        self.assertEqual(urgents(m, "ilse", inertie=True)[0], "chaleur")


class TenirTests(unittest.TestCase):
    """Un but qui se tient en restant compte ce que le lieu laisse monter chez les autres besoins."""

    def lucien_au_grenier_noir(self, secours_spontane=True):
        """Placement d'auteur, l'auberge telle qu'écrite : Lucien, qui craint le noir, garde son
        coffret au grenier sans lumière ; ses biens et sa sécurité pressent. Le cas réel : il
        allait au couloir éclairé, puis revenait garder ses biens, et ainsi de suite."""
        m = creer("auberge", 1985, "fixe")
        # Garde et recherche d'un porteur isolées du secours spontané à un effrayé.
        # La compagnie de secours est exercée avec les profils actifs dans test_empathie_peur.
        from tests.support import sans_souci
        if not secours_spontane:
            sans_souci(m)
        calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
        m.objets["poele"].update(allume=False, combustible=0)
        m.objets["bois_anselme"]["charges"] = 0
        # Anselme ne paie personne pour rallumer son poêle (``echanges.engager``) et a déjà demandé à
        # chacun s'il avait du bois (``echanges.enqueter``) : la chambre reste noire.
        m.data["finances_pnj"]["anselme"] = 0
        placer(m, "lucien", "grenier", (2, 2))
        percevoir_tous(m)
        # Les réponses retiennent ce qu'il croyait alors (``deliberation.retenir_refus``) : après ce qu'il voit.
        from donjon.deliberation import retenir_refus
        for autre in ("odile", "mireille", "tilo", "joss", "hugues", "mathurine", "lucien"):
            retenir_refus(m, "anselme", autre, "enqueter", "rien", besoin="chaleur", souvenir=False)
        lire(m, "lucien")["besoins"].update(biens=65.0, securite=70.0)
        return m

    def test_lucien_rapporte_la_lanterne_de_l_etable_au_grenier_au_lieu_d_aller_et_venir(self):
        from donjon import pnj
        from donjon.deliberation import autour
        from donjon.rendu import regarder as rendu
        from donjon.scene import scene_percue
        # Scène de garde : ses biens pressent, sa sécurité est apaisée,
        # et il connaît une lumière à emporter. La poursuite concurrente du
        # ballot est vérifiée séparément, sans décider du sort de la lanterne.
        m = self.lucien_au_grenier_noir()
        p = m.objets["lucien"]["profil"]
        p["pulsions"] = [x for x in p["pulsions"] if x["condition"].get("objet") != "ballot"]
        lire(m, "lucien")["pulsions"] = []
        lire(m, "lucien")["besoins"].update(biens=85.0, securite=10.0)
        source = m.objets["mireille"]
        croire(m, "lucien", "mireille", "lieu", source["lieu"], "savoir",
               salle=source["lieu"], case=source["position"])
        croire(m, "lucien", "bougeoir_mireille", "lieu", "mireille", "savoir",
               salle=source["lieu"], case=source["position"])
        croire(m, "lucien", "bougeoir_mireille", "etat",
               {"allume": True, "faible": False, "charge": True}, "savoir")
        agir, passages = pnj.agir, []
        def agir_sonde(m, id, *args, **kwargs):
            avant = m.objets[id]['lieu']
            resultat = agir(m, id, *args, **kwargs)
            if id == 'lucien' and avant != m.objets[id]['lieu']:
                passages.append(m.objets[id]['lieu'])
            return resultat
        with patch.object(pnj, 'agir', agir_sonde):
            m, lieux = suivre(m, "lucien", 165, pas=5)
        # Compter aussi les trajets entre deux relevés de cinq minutes.
        self.assertEqual(passages, ['couloir', 'salle_commune', 'cuisine',
                                    'salle_commune', 'couloir', 'grenier'])
        self.assertEqual(lieux[-5:], ["grenier"] * 5)
        self.assertLessEqual(changements(lieux), 6)
        self.assertEqual(lire(m, "lucien")["intention"]["but"], {"type": "garder", "lieu": "grenier"})
        self.assertEqual(m.objets["bougeoir_mireille"]["lieu"], "lucien")
        self.assertTrue(m.objets["bougeoir_mireille"]["allume"])
        self.assertTrue(autour(m, "lucien")["lumiere"])
        self.assertFalse(any(c.get('pnj') == 'lucien' and '(rendu)' in c['texte']
                             for c in m.data['chronique']))
        # Le joueur constate la garde éclairée après la simulation.
        m.joueur.update(salle='grenier', position=[1, 2])
        texte = rendu(m)
        self.assertIn('Le bougeoir', texte)
        apres = recharger(m)
        self.assertEqual(m.data, apres.data)
        self.assertEqual(texte, rendu(apres))
        self.assertEqual(scene_percue(m), scene_percue(apres))

    def test_lucien_attend_une_information_apres_la_reprise_du_ballot(self):
        import copy
        from donjon import deliberation, pnj
        from donjon.agendas import contrat_intention
        from donjon.deliberation import obstacle_patience
        from donjon.ouie import nature
        from donjon.planification import bruit_crochetage
        from donjon.rendu import regarder as rendu
        from donjon.temps import instant, MINUTE
        from tools.detecter_changements_avis import observer_avis, analyser_episodes
        # Scène historique complète : conserver le contrôle 229 à 95 min.
        # Le recours débloqué change ensuite sa place et la fenêtre du vol.
        retenu, croyance95 = None, None
        vols, reprises, reprise_ballot, deplacements = [], [], [], []
        with observer_avis() as sonde:
            executer, choisir, agir = pnj._executer, deliberation.choisir, pnj.agir

            def executer_sonde(m, id, etape, *args, **kwargs):
                preuve = None
                if id == "lucien" and etape["condition"] == "sans_temoin":
                    bruit = (bruit_crochetage(m, id, pnj.lumiere_du_geste(m, id))
                             if etape["operation"] == "crocheter" else nature(etape["operation"], discret=True))
                    preuve = {"instant": instant(m), "operation": etape["operation"],
                              "vus": pnj.temoins_crus(m, id), "oreilles": pnj.oreilles_crues(m, id, bruit),
                              "presents": [x for x in lire(m, id)["croyances"] if x != id
                                           and (x == "joueur" or m.objets.get(x, {}).get("type") == "personnage")
                                           and deliberation.salle_crue(m, id, x) == m.objets[id]["lieu"]
                                           and lire(m, id)["croyances"][x].get("etat", {}).get("valeur", {}).get("conscient") is not False],
                              "obstacle": obstacle_patience(m, id, retenu["cause"]) if retenu else None,
                              "desespere": pnj.desespere(m, id)}
                resultat = executer(m, id, etape, *args, **kwargs)
                if resultat:
                    if preuve is not None:
                        vols.append(preuve)
                    if id == "anselme" and etape["operation"] == "prendre" and etape["cible"] == "ballot":
                        reprise_ballot.append(instant(m))
                return resultat

            def choisir_sonde(m, id, minute):
                avant = (lire(m, id)["intention"] or {}).get("but")
                resultat = choisir(m, id, minute)
                apres = (lire(m, id)["intention"] or {}).get("but")
                if id == "lucien" and retenu and avant != retenu["but"] and apres == retenu["but"]:
                    reprises.append({"instant": instant(m), "obstacle": obstacle_patience(m, id, retenu["cause"]),
                                     "croyance": copy.deepcopy(lire(m, id)["croyances"]["anselme"]["lieu"])})
                return resultat

            def agir_sonde(m, id, t, *args, **kwargs):
                avant = m.objets[id]["lieu"]
                resultat = agir(m, id, t, *args, **kwargs)
                if id == "lucien" and avant != m.objets[id]["lieu"]:
                    deplacements.append(t)
                return resultat

            with patch.object(pnj, "_executer", executer_sonde), \
                 patch.object(deliberation, "choisir", choisir_sonde), patch.object(pnj, "agir", agir_sonde):
                depart = self.lucien_au_grenier_noir(secours_spontane=False)
                # La scène de la reprise du ballot garde la chambre noire.
                # Depuis 277, l'absence de pièces n'empêche plus Anselme de
                # chercher un allumage gratuit : à 32 min, aller parler au
                # porteur d'une flamme modifie légitimement la fenêtre du vol.
                # Le poêle est ici hors d'usage, ce que les habitants savent :
                # même un allumage gratuit ne rend pas de lumière. Les buts,
                # les ressources et les témoins restent ceux de la scène.
                depart.objets["poele"]["integrite"] = 0
                for qui, objet in depart.objets.items():
                    if objet.get("profil"):
                        croire(depart, qui, "poele", "fin", "detruit", "vu")
                m, _ = suivre(depart, "lucien", 95, pas=5)
                retenu = copy.deepcopy(lire(m, "lucien")["renoncements"]["biens"][0])
                croyance95 = copy.deepcopy(lire(m, "lucien")["croyances"]["anselme"]["lieu"])
                self.assertTrue(obstacle_patience(m, "lucien", retenu["cause"]))
                self.assertNotEqual(lire(m, "lucien")["intention"]["but"], retenu["but"])
                m, _ = suivre(m, "lucien", 25, pas=5)
                recherche = dict(lire(m, "lucien")["recherches"]["anselme"])
                self.assertEqual(set(recherche), set(m.data["salles"]))
                m, _ = suivre(m, "lucien", 45, pas=5)
        self.assertTrue(reprises)
        for reprise in reprises:
            self.assertGreater(reprise["instant"], 95 * MINUTE)
            self.assertFalse(reprise["obstacle"])
            self.assertNotEqual(reprise["croyance"]["valeur"], croyance95["valeur"])
            self.assertGreater(reprise["croyance"]["minute"], 95)
        self.assertEqual({v["operation"] for v in vols}, {"crocheter", "ouvrir", "prendre"})
        for vol in vols:
            self.assertGreaterEqual(vol["instant"], 107 * MINUTE)
            self.assertLess(vol["instant"], 110 * MINUTE)
            self.assertEqual(vol["presents"], [])
            self.assertEqual(vol["vus"], [])
            self.assertEqual(vol["oreilles"], [])
            self.assertFalse(vol["obstacle"])
            self.assertFalse(vol["desespere"])
        self.assertTrue(reprise_ballot)
        self.assertGreater(min(reprise_ballot), max(v["instant"] for v in vols))
        self.assertFalse([t for t in deplacements if t >= 120 * MINUTE])
        avis = analyser_episodes({"lucien": sonde.episodes["lucien"]})
        self.assertEqual(avis["total_non_justifies"], 0)
        e = lire(m, "lucien")
        self.assertEqual(e["recherches"]["anselme"], recherche)
        self.assertEqual(e["intention"]["but"], {"type": "pulsion", "objet": "ballot", "lieu": "etable"})
        self.assertEqual(e["intention"]["plan"], [])
        self.assertEqual(contrat_intention(m, "lucien")["phase"], "attendre")
        self.assertEqual(contrat_intention(m, "lucien")["demande"],
                         {"condition": {"objet": "ballot", "lieu": "etable"}, "tache": True})
        self.assertIsNone(e["croyances"]["anselme"]["lieu"]["valeur"])
        self.assertEqual(e["croyances"]["ballot"]["lieu"]["valeur"], "anselme")
        self.assertEqual(m.objets["ballot"]["lieu"], "chambre_chaude")
        texte = rendu(m)
        apres = recharger(m)
        self.assertEqual(m.data, apres.data)
        self.assertEqual(texte, rendu(apres))

    def bram_au_bureau_noir(self, lampe=True, secours_spontane=True):
        """Placement d'auteur, la mine telle qu'écrite : la chandelle du bureau est à sec ; Bram, qui
        craint fort le noir, garde le coffre de la paie ; ses biens et sa sécurité pressent. Avec
        ``lampe``, il sait la lampe du filon allumée. Odon, dont il se méfie, ne convoite pas la paie
        (honnêteté entière) : il resterait sinon à la porte du bureau, qu'il sait crocheter, et Bram
        s'abriterait de lui (une limite connue, ``docs/plan-planificateur.md``)."""
        # Recours de lumière isolé du marché supplémentaire du bois d’Odon.
        from tests.scenarios_contractuels import creer as creer_contractuel
        m = creer_contractuel("mine", 1985, "fixe")
        # Isoler le recours de lumière des compagnons qui viendraient rassurer Bram.
        from tests.support import sans_souci
        if not secours_spontane:
            sans_souci(m)
        calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
        m.objets["odon"]["profil"]["valeurs"]["honnetete"] = 100
        m.objets["chandelle"].update(allume=False, combustible=0)
        percevoir_tous(m)
        if lampe:
            croire(m, "bram", "lampe_filon", "lieu", "filon", "savoir", salle="filon", case=None)
            croire(m, "bram", "lampe_filon", "etat", {"allume": True, "faible": False, "charge": True}, "savoir")
        lire(m, "bram")["besoins"].update(biens=70.0, securite=70.0)
        return m

    @patch("donjon.social._constats", return_value=())
    def test_bram_va_prendre_la_lampe_du_filon_et_revient_garder_la_paie_eclaire(self, _constats):
        # Isoler ce recours de lumière des nouvelles qui lui feraient choisir un autre moyen.
        from donjon.deliberation import autour
        m, lieux = suivre(self.bram_au_bureau_noir(secours_spontane=False), "bram", 3)
        self.assertEqual(lieux, ["bureau", "filon", "bureau"])
        self.assertEqual(m.objets["lampe_filon"]["lieu"], "bram")
        self.assertTrue(m.objets["lampe_filon"]["allume"])
        # Il y voit, là où il garde la paie.
        self.assertTrue(autour(m, "bram")["lumiere"])
        self.assertEqual(lire(m, "bram")["intention"]["but"], {"type": "garder", "lieu": "bureau"})

    def lucien_au_couloir_sans_lumiere(self):
        """Placement d'auteur : Lucien est au couloir éclairé ; il sait le grenier obscur et ne
        connaît aucune lumière à emporter et ne se fie à personne (pas d'abri) ; il ne garde que son
        coffret (ni ballot convoité)."""
        m = creer("auberge", 1985, "fixe")
        calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
        p = m.objets["lucien"]["profil"]
        # Ce test oppose deux besoins au poids neutre ; les valeurs propres sont testées ailleurs.
        p["valeurs"]["ambition"] = 50
        p["pulsions"] = [x for x in p["pulsions"] if x["condition"].get("objet") != "ballot"]
        lire(m, "lucien")["pulsions"] = []
        placer(m, "lucien", "couloir", (2, 1))
        percevoir_tous(m)
        croyances = lire(m, "lucien")["croyances"]
        for k in ("lanterne_hugues", "bougeoir_mireille", "lanterne_etable"):
            croyances.pop(k, None)
        lire(m, "lucien")["relations"].clear()
        croire(m, "lucien", "grenier", "etat", {"eclairee": False}, "vu")
        lire(m, "lucien")["besoins"]["biens"] = 65.0
        return m

    def test_sans_lumiere_a_emporter_le_plus_fort_l_emporte_et_l_autre_s_endure(self):
        # Aucun plan ne sert les deux. Ses biens laissés lui coûtent plus (``prix_gardes``) que le noir à sa
        # peur (0,5) : il retourne au grenier et y reste quand la sécurité presse, qui attend.
        from donjon.planification import garder
        m = self.lucien_au_couloir_sans_lumiere()
        self.assertEqual(gardes(m, "lucien"), ("grenier",))
        self.assertGreater(Vue(m, "lucien").prix_gardes["grenier"], NOIR * 0.5)
        self.assertEqual([x["operation"] for x in garder(m, "lucien", "grenier")], ["aller"])
        m, lieux = suivre(m, "lucien", 10, pas=5)
        self.assertEqual(lieux[-1], "grenier")
        lire(m, "lucien")["besoins"]["securite"] = 70.0
        m, lieux = suivre(m, "lucien", 30, pas=10)
        self.assertEqual(lieux, ["grenier"] * 3)
        self.assertIn("securite", attentes(m, "lucien"))

    def test_qui_craint_plus_le_noir_reste_dans_la_lumiere_et_endure_ses_biens(self):
        from donjon.planification import garder
        m = self.lucien_au_couloir_sans_lumiere()
        m.objets["lucien"]["profil"]["securite"] = {"noir": 0.8}
        self.assertGreater(NOIR * 0.8, Vue(m, "lucien").prix_gardes["grenier"])
        self.assertIsNone(garder(m, "lucien", "grenier"))
        m, lieux = suivre(m, "lucien", 30, pas=10)
        self.assertEqual(lieux, ["couloir"] * 3)
        self.assertIn("biens", attentes(m, "lucien"))
        self.assertEqual(lire(m, "lucien")["urgences"]["biens"]["etat"], "attente")


class AttenteTests(unittest.TestCase):
    """Un besoin qu'aucun plan ne peut apaiser attend, sans être oublié."""

    def test_le_devoir_de_gorm_sans_tache_possible_attend_puis_reprend_a_la_ronde_echue(self):
        m = relais()
        calme(m, "marchand", "brune", "ilse", "aubin")
        lire(m, "marchand")["besoins"]["devoir"] = 85.0
        croire(m, "marchand", "brasero", "etat", {"allume": True, "faible": False, "charge": True}, "vu")
        deliberer(m, "marchand", m.data["minutes"])
        m = recharger(m)
        e = lire(m, "marchand")
        self.assertIsNone(e["intention"])
        self.assertEqual(attentes(m, "marchand"), ["devoir"])
        # Le banc ne le compte pas sans recours : ce qui reste à faire (la cloche) est confié au
        # joueur, une catégorie à part (oisifs, sans recours, en attente, confiées).
        self.assertEqual(_oisifs_urgents(m), (1, 0, 0, 1))
        # Qu'il cesse de croire le joueur fiable : la cloche lui revient ; sans plan pour elle sur ce
        # qu'il croit, son devoir est en attente, pas sans recours.
        autre = recharger(m)
        lier(autre, "marchand", "joueur", False, "vu")
        self.assertEqual(_oisifs_urgents(autre), (1, 0, 1, 0))
        # Rien n'est oublié : la ronde du refuge échue, le devoir a de nouveau un plan.
        e["visites"]["antichambre"] = m.data["minutes"] - 100
        deliberer(m, "marchand", m.data["minutes"])
        m = recharger(m)
        self.assertEqual(lire(m, "marchand")["intention"]["motif"], "devoir")
        self.assertEqual(lire(m, "marchand")["urgences"]["devoir"]["etat"], "presse")
        self.assertEqual(attentes(m, "marchand"), [])

    def test_la_faim_refusee_attend_puis_redemande_quand_le_refus_a_vieilli(self):
        from donjon.deliberation import REDEMANDE
        from donjon.deliberation import retenir_refus
        m = relais()
        calme(m, "marchand", "brune", "ilse", "aubin")
        lire(m, "ilse")["besoins"]["faim"] = 80.0
        # Un refus de méfiance tient ``REDEMANDE`` minutes, et payer ne le lève pas ; ce qu'il garde
        # tient tant que rien de ce qu'elle en croit n'a changé (``test_refus_retenus``).
        retenir_refus(m, "ilse", "marchand", "demander", "mefiance", objet="vivres")
        # Elle a déjà demandé aux autres s'ils avaient à manger (``echanges.enqueter``) : rien.
        for autre in ("aubin", "brune"):
            retenir_refus(m, "ilse", autre, "enqueter", "rien", besoin="faim", souvenir=False)
        deliberer(m, "ilse", m.data["minutes"])
        m = recharger(m)
        self.assertIsNone(lire(m, "ilse")["intention"])
        self.assertEqual(attentes(m, "ilse"), ["faim"])
        m.data["minutes"] += REDEMANDE
        deliberer(m, "ilse", m.data["minutes"])
        m = recharger(m)
        self.assertEqual(lire(m, "ilse")["intention"]["motif"], "faim")
        self.assertEqual(attentes(m, "ilse"), [])


if __name__ == "__main__":
    unittest.main()
