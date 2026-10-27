"""Attribution des gestes ordinaires : présence crue mobile, jamais position réelle."""
import copy
import unittest

from donjon.banc_pnj import creer
from donjon.ecoute import entendus, rendre, ENTENDU
from donjon.esprits import croire, lire
from donjon.ouie import _crus_la, retentir
from donjon.rendu import decrire_contexte
from donjon.temps import ecouler
from tests.support import calme, lier
from tests.test_tensions import placer, recharger


def scene(scenario="relais", auditeur="ilse", auteur="aubin", salle="antichambre"):
    m = creer(scenario, 1, depart="fixe")
    calme(m, *[i for i, o in m.objets.items() if o.get("profil")])
    placer(m, auditeur, salle, (4, 5))
    m.objets[auditeur]["orientation"] = "est"
    placer(m, auteur, salle, (1, 3))
    lier(m, auditeur, auteur, True)
    # La dernière perception était trois cases plus loin, la minute précédente.
    croire(m, auditeur, auteur, "lieu", salle, "vu", salle=salle, case=[1, 6])
    m.data.update(minutes=1, dixiemes=0)
    m.joueur.update(salle=salle, position=[7, 3], orientation="est")
    return recharger(m)


class PasCompagnonsTests(unittest.TestCase):
    def stable(self, m):
        avant = copy.deepcopy(m.data)
        rendu = (decrire_contexte(m), rendre(m, entendus(m, -1, ENTENDU)))
        recharge = recharger(m)
        self.assertEqual(avant, recharge.data)
        self.assertEqual(rendu, (decrire_contexte(recharge), rendre(recharge, entendus(recharge, -1, ENTENDU))))
        return recharge

    def test_voisins_hors_du_cone_relais_et_autre_cas_auberge(self):
        for args in (("relais", "ilse", "aubin", "antichambre"),
                     ("auberge", "odile", "hugues", "salle_commune")):
            with self.subTest(scenario=args[0]):
                m = scene(*args)
                orientation = m.objets[args[1]]["orientation"]
                presence = copy.deepcopy(lire(m, args[1])["croyances"][args[2]]["lieu"])
                for geste in ("aller", "prendre", "aller"):
                    self.assertNotIn(args[1], retentir(m, args[2], geste))
                    m = self.stable(m)
                self.assertEqual(orientation, m.objets[args[1]]["orientation"])
                self.assertFalse([s for s in lire(m, args[1])["memoire"] if s["type"] == "bruit"])
                self.assertEqual(presence, lire(m, args[1])["croyances"][args[2]]["lieu"])

    def test_mael_entend_le_refuge_depuis_une_autre_salle(self):
        m = scene("crue_hameau", "mael", "aubin")
        placer(m, "mael", "echoppe", (8, 3))
        m.objets["mael"]["orientation"] = "ouest"
        placer(m, "aubin", "antichambre", (0, 3))
        # Il croit Aubin au refuge ; l'ouïe ne situe pas sa case à travers la cloison.
        retentir(m, "aubin", "aller")
        m = self.stable(m)
        self.assertFalse([s for s in lire(m, "mael")["memoire"] if s["type"] == "bruit"])
        self.assertEqual("entendu", lire(m, "mael")["croyances"]["aubin"]["lieu"]["source"])

    def test_fracas_et_appel_restent_inhabituels(self):
        for nature in ("bruyant", "appel"):
            m = scene()
            placer(m, "ilse", "echoppe", (8, 3))
            m.objets["ilse"]["orientation"] = "ouest"
            retentir(m, "aubin", "forcer", force=nature)
            m = self.stable(m)
            self.assertTrue([s for s in lire(m, "ilse")["memoire"] if s["type"] == "bruit"])

    def test_expiration_absence_et_depart_crus(self):
        for cause in ("expire", "absent", "parti"):
            m = scene()
            if cause == "expire":
                m.data["minutes"] = 31
            elif cause == "absent":
                croire(m, "ilse", "aubin", "lieu", None, "vu", salle="antichambre", case=None)
            else:
                croire(m, "ilse", "aubin", "etat", {"parti": True}, "vu")
            m = recharger(m)
            self.assertNotIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))
            self.assertIn("ilse", retentir(m, "aubin", "aller"))
            self.stable(m)

    def test_distance_incompatible_et_frontiere_du_temps_fin(self):
        m = scene()
        m.data.update(minutes=0, dixiemes=15)
        self.assertNotIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))
        ecouler(m, 15)
        self.assertIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))
        self.stable(m)

    def test_meprise_sans_consulter_la_position_reelle(self):
        m = scene()
        placer(m, "aubin", "crypte", (1, 3))
        placer(m, "brune", "antichambre", (1, 3))
        lire(m, "ilse")["croyances"].pop("brune", None)
        presence = copy.deepcopy(lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        retentir(m, "brune", "aller")
        m = self.stable(m)
        self.assertEqual(presence, lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        self.assertNotIn("brune", lire(m, "ilse")["croyances"])

    def test_la_mefiance_porte_sur_la_meme_personne_que_l_attribution(self):
        from donjon.relations import se_mefie
        m = scene()
        m.data["minutes"] = 0
        croire(m, "ilse", "brune", "lieu", "antichambre", "vu", salle="antichambre", case=[7, 5])
        lier(m, "ilse", "brune", False)
        m.data["minutes"] = 1
        self.assertTrue(se_mefie(m, "ilse", "brune"))
        presence = copy.deepcopy(lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        self.assertNotIn("ilse", retentir(m, "aubin", "aller"))
        m = self.stable(m)
        self.assertEqual(presence, lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        self.assertEqual("vu", lire(m, "ilse")["croyances"]["brune"]["lieu"]["source"])

    def test_joueur_meme_attribution_sans_revelation_au_rendu(self):
        m = scene()
        croire(m, "joueur", "aubin", "lieu", "antichambre", "entendu", salle="antichambre", case=[1, 6])
        retentir(m, "aubin", "aller")
        m = self.stable(m)
        self.assertEqual("entendu", lire(m, "joueur")["croyances"]["aubin"]["lieu"]["source"])
        texte = " ".join(rendre(m, entendus(m, -1, ENTENDU)))
        self.assertIn("pas", texte)
        self.assertNotIn("Aubin", texte)

    def test_une_compatibilite_de_marche_ne_se_confirme_pas_elle_meme(self):
        m = scene()
        presence = copy.deepcopy(lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        for minute in (1, 10, 20, 30):
            m.data["minutes"] = minute
            self.assertNotIn("ilse", retentir(m, "aubin", "aller"))
            m = self.stable(m)
            self.assertEqual(presence, lire(m, "ilse")["croyances"]["aubin"]["lieu"])
        m.data["minutes"] = 31
        self.assertNotIn("aubin", _crus_la(m, "ilse", "antichambre", [1, 3]))

    def test_localisation_acoustique_dans_la_zone_deja_crue(self):
        m = scene()
        croire(m, "ilse", "aubin", "lieu", "antichambre", "vu", salle="antichambre", case=[1, 4])
        self.assertNotIn("ilse", retentir(m, "aubin", "aller"))
        m = self.stable(m)
        c = lire(m, "ilse")["croyances"]["aubin"]["lieu"]
        self.assertEqual((c["source"], c["case"], c["minute"]), ("entendu", [1, 3], 1))

    def test_meme_laps_entier_ou_decoupe_recharge(self):
        a, b = scene(), scene()
        ecouler(a, 45)
        for _ in range(3):
            ecouler(b, 15)
            b = recharger(b)
        retentir(a, "aubin", "aller")
        retentir(b, "aubin", "aller")
        self.assertEqual(self.stable(a).data, self.stable(b).data)

    def test_temoin_illicite_reconnait_la_presence_mobile_crue(self):
        from donjon.pnj import commencer_geste, temoigner_en_cours
        from tests.test_ouie_temoins import odon_au_coffre
        m = odon_au_coffre(True)
        croire(m, "bram", "odon", "lieu", "bureau", "vu", salle="bureau", case=[1, 4])
        m.data.update(minutes=1, dixiemes=0)
        commencer_geste(m, "odon", "crocheter", "coffre_paie", 1200, nature="bruyant")
        temoigner_en_cours(m)
        m = self.stable(m)
        self.assertTrue([s for s in lire(m, "bram")["memoire"]
                         if s["type"] == "vu_agir" and s["auteur"] == "odon" and s.get("par") == "ouie"])

    def test_marche_executee_et_temps_decoupe_dans_la_mine(self):
        from tests.test_ouie import mine_baraquement
        from tests.test_ouie_temoins import etat
        from donjon.pnj import avancer
        def vivre(laps):
            m = mine_baraquement("josse")
            for d in laps:
                ecouler(m, d)
                avancer(m, 0, [], dixiemes=d)
                m = recharger(m)
            return m
        a, b = vivre([600]), vivre([150, 150, 300])
        self.assertEqual(etat(a), etat(b))
        for m in (a, b):
            m = self.stable(m)
            self.assertFalse([c for c in m.data.get("chronique", [])
                              if c["pnj"] == "josse" and "se retourne au bruit" in c["texte"]])
