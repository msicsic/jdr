"""Couche sociale entre PNJ sur le Relais à quatre : rumeurs, vols découverts, rondes.

Chaque test vérifie l'état du monde et ce que le joueur lit, après rechargement.
"""

from tests.support import lier, relation
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.defi import nouveau_defi
from donjon.esprits import lire, memoriser, croire, percoit
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.paroles import esprits_interlocuteurs
from donjon.social import RANG_MAX
from donjon.spatial import installer
from donjon.vol import mefiance
from donjon.relations import envers
from tests.support import calme, regarder, refusee, presentes


def recharger(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        return Monde.charger(chemin)


def attendre(monde, fois=1, jet=None):
    texte = ""
    for _ in range(fois):
        if jet is None:
            texte += Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre"))) + "\n"
        else:
            with patch.object(Monde, "d20", return_value=jet):
                texte += Moteur(monde).executer(Moteur(monde).preparer(proposition("attendre"))) + "\n"
        monde = recharger(monde)
    return monde, texte


def chronique(monde):
    return [c["texte"] for c in monde.data.get("chronique", [])]


def placer(monde, id, salle, case):
    monde.objets[id].update(lieu=salle, position=list(case), position_salle=salle)


def relais():
    m = nouveau_defi(depart="fixe")
    installer(m)
    return presentes(m)


def rumeurs(monde, id):
    return [s for s in lire(monde, id)["memoire"] if s["type"] == "rumeur"]


class RumeurTests(unittest.TestCase):
    def ilse_a_vu_le_joueur(self):
        """Ilse surprend Corvus qui tente de dérober le marteau de Gorm, puis Gorm revient au refuge."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Gorm connaît déjà Corvus, absent pendant le geste : la rumeur porte sur une
        # personne identifiée, sans quoi il ne peut lui attribuer une relation.
        lire(m, "marchand")["voix"].append("joueur")
        m.objets["marteau"].update(proprietaire="marchand", lieu="antichambre", position=[1, 4],
                                   position_salle="antichambre")
        placer(m, "marchand", "crypte", [4, 3])
        placer(m, "brune", "echoppe", [7, 1])
        placer(m, "aubin", "crypte", [5, 3])
        regarder(m, "ilse", "joueur")
        self.assertTrue(percoit(m, "ilse", "joueur"))
        with patch.object(Monde, "d20", return_value=1):
            Moteur(m).executer(Moteur(m).preparer(
                sequence(etape("deplacer", "marteau", "joueur", methode="discret"))))
        self.assertEqual([s["type"] for s in lire(m, "ilse")["memoire"]][-1], "vol_surpris")
        # Placement d'auteur : Gorm revient de sa ronde et se tient près d'Ilse.
        placer(m, "marchand", "antichambre", [2, 5])
        return recharger(m)

    def test_ilse_le_dit_a_gorm_qui_cesse_de_croire_le_joueur(self):
        m, texte = attendre(self.ilse_a_vu_le_joueur(), jet=15)
        fiable = relation(m, "marchand", "joueur")
        self.assertEqual((fiable["valeur"], fiable["source"]), (False, "dit:ilse"))
        self.assertEqual(rumeurs(m, "marchand")[0]["evenement"]["type"], "vol_surpris")
        self.assertIn("Ilse glisse à Gorm que l'étranger a tenté de dérober le marteau.", texte)
        from donjon.voix import connait_nom
        self.assertFalse(connait_nom(m,'ilse','joueur'))
        self.assertFalse(connait_nom(m,'marchand','joueur'))
        self.assertIn("Ilse dit à Gorm que Corvus a tenté de dérober le marteau (crue).", chronique(m))
        # La réputation change son jeu : vigilance accrue, cloche plus confiée au joueur.
        self.assertEqual(mefiance(m, "marchand"), 1)
        lire(m, "marchand")["besoins"]["devoir"] = 80.0
        m, _ = attendre(m)
        # Il va lui-même chercher la cloche à la galerie et la repose au refuge.
        self.assertIn("Gorm, gardien du relais prend la cloche d'alarme.", chronique(m))
        self.assertEqual(m.objets["cloche"]["lieu"], "antichambre")
        # Luna le fait parler d'après ce qu'on lui a dit, en nommant la source.
        self.assertIn("croit que toi est peu fiable (Ilse le lui a dit)",
                      esprits_interlocuteurs(m, ["marchand"])["marchand"]["croit"])

    def test_un_jet_rate_laisse_gorm_sceptique(self):
        m, texte = attendre(self.ilse_a_vu_le_joueur(), jet=1)
        self.assertNotIn("fiable", lire(m, "marchand")["croyances"].get("joueur", {}))
        self.assertEqual(lire(m, "marchand")["memoire"][-1]["type"], "parole_doutee")
        self.assertIn("Ilse dit à Gorm que Corvus a tenté de dérober le marteau (doute).", chronique(m))
        # Ilse ne répète pas à Gorm ce qu'elle lui a déjà dit.
        m, _ = attendre(m, 2, jet=15)
        self.assertNotIn("fiable", lire(m, "marchand")["croyances"].get("joueur", {}))

    def test_la_rumeur_passe_de_main_en_main_puis_s_eteint(self):
        m, _ = attendre(self.ilse_a_vu_le_joueur(), jet=15)
        # Placement d'auteur : Ilse s'éloigne ; Aubin rejoint Gorm, puis Brune rejoint Aubin.
        placer(m, "ilse", "echoppe", [1, 1])
        placer(m, "aubin", "antichambre", [1, 5])
        regarder(m, "marchand", "aubin")  # Il le voit arriver près de lui.
        m, _ = attendre(m, jet=15)
        rumeur = rumeurs(m, "aubin")[0]
        self.assertEqual((rumeur["de"], rumeur["rang"]), ("marchand", RANG_MAX))
        fiable = relation(m, "aubin", "joueur")
        self.assertEqual(fiable["source"], "dit:marchand")
        from donjon.relations import envers
        self.assertEqual(envers(m, "aubin", "joueur")["confiance"], 27)
        placer(m, "marchand", "crypte", [4, 3])
        placer(m, "brune", "antichambre", [2, 6])
        m, _ = attendre(m, 2, jet=15)
        # De troisième main, Aubin ne la répète plus (Ilse a pu, elle, la lui dire en repassant).
        self.assertFalse(any(r["de"] == "aubin" for r in rumeurs(m, "brune")))

    def test_on_ne_dit_rien_a_l_accuse_ni_a_qui_on_se_mefie(self):
        m = self.ilse_a_vu_le_joueur()
        placer(m, "marchand", "crypte", [4, 3])
        placer(m, "brune", "antichambre", [2, 5])
        lier(m, "ilse", "brune", False, "vu")
        m, _ = attendre(m, 2, jet=15)
        self.assertNotIn("fiable", lire(m, "brune")["croyances"].get("joueur", {}))
        self.assertFalse(any("Ilse dit" in t for t in chronique(m)))

    def test_hors_de_ce_que_le_joueur_connait_il_n_entend_qu_un_murmure(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.data['noms_connus'].remove('brune')
        # Placement d'auteur : Ilse a vu Brune crocheter la réserve ; elle retrouve Gorm dans la conduite.
        memoriser(m, "ilse", {"type": "vu_agir", "auteur": "brune", "operation": "crocheter", "objet": "reserve"})
        lier(m, "ilse", "brune", False, "vu")
        m.joueur.update(salle="echoppe", position=[0, 3])
        placer(m, "ilse", "echoppe", [2, 1])
        regarder(m, "ilse", "marchand")  # Elle le voit, à deux pas.
        regarder(m, "joueur", "ilse")    # Le joueur les voit parler.
        placer(m, "brune", "crypte", [4, 3])
        m.data["visitees"] = ["echoppe"]
        m, texte = attendre(recharger(m), jet=15)
        self.assertEqual(envers(m, "marchand", "brune")["confiance"], 52)
        self.assertEqual(envers(m, "marchand", "brune")["motifs"][-1]["type"], "rumeur")
        self.assertIn("Ilse, meunière évacuée parle à voix basse avec Gorm, gardien du relais.", texte)
        self.assertNotIn("réserve", texte)


class VolDecouvertTests(unittest.TestCase):
    def test_gorm_voit_ses_vivres_aux_mains_de_brune(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["vivres"]["lieu"] = "brune"
        placer(m, "marchand", "antichambre", [6, 1])
        m, _ = attendre(recharger(m))
        e = lire(m, "marchand")
        self.assertIn({"type": "vu_porter", "auteur": "brune", "objet": "vivres"},
                      [{k: v for k, v in s.items() if k not in ("minute", "dit_a", "preuve", "victime", "deja_entendu")} for s in e["memoire"]])
        self.assertFalse(relation(m, "marchand", "brune")["valeur"])
        self.assertGreaterEqual(e["besoins"]["biens"], 50)

    def test_gorm_reconnait_son_marteau_dans_la_main_du_joueur(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["marteau"].update(proprietaire="marchand", lieu="joueur")
        m.objets["marteau"].pop("position", None)
        placer(m, "marchand", "antichambre", [2, 4])
        regarder(m, "marchand", "joueur")
        m, texte = attendre(recharger(m))
        self.assertFalse(relation(m, "marchand", "joueur")["valeur"])
        self.assertEqual(mefiance(m, "marchand"), 1)
        self.assertIn("Gorm, gardien du relais, semble méfiant.", texte)

    def test_un_objet_prete_n_est_pas_un_vol(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["marteau"].update(proprietaire="marchand", lieu="joueur")
        m.objets["marteau"].pop("position", None)
        memoriser(m, "marchand", {"type": "pret", "objet": "marteau", "a": "joueur"})
        placer(m, "marchand", "antichambre", [2, 4])
        m, _ = attendre(recharger(m))
        self.assertNotIn("fiable", lire(m, "marchand")["croyances"].get("joueur", {}))

    def test_temoin_qui_entre_pendant_le_geste(self):
        m = calme(refusee(relais()), "marchand", "ilse", "aubin")
        # Placement d'auteur : Brune, crochets en main, mange dans la réserve ouverte ; Ilse, dans
        # la conduite, vient parcourir le refuge des yeux pendant ce temps : ses pas ne s'entendent
        # pas d'aussi loin.
        m.objets["reserve"].update(verrouillee=False, ouverte=True)
        lire(m, "brune")["besoins"]["faim"] = 90.0
        placer(m, "brune", "antichambre", [7, 3])
        placer(m, "ilse", "echoppe", [8, 3])
        placer(m, "aubin", "crypte", [5, 3])
        m.joueur.update(salle="chambre_cloche", position=[1, 3])
        croire(m, "brune", "reserve", "verrouillee", False, "vu")
        croire(m, "brune", "reserve", "etat", {"ouverte": True}, "vu")
        # Elle finit son geste en cours à la première minute ; Ilse franchit le seuil
        # avant qu'elle ait fini de manger, même avec le détour jusqu'au centre.
        lire(m, "brune")["libre"] = 600
        # Calme, elle fait sa ronde en routine (inquiète, elle se mettrait d'abord à l'abri).
        lire(m, "ilse")["besoins"]["securite"] = 40.0
        # Sa ronde de l'échoppe est faite, celle du refuge est due.
        lire(m, "ilse")["visites"] = {"echoppe": 0}
        self.assertFalse(percoit(m, "ilse", "brune"))
        m, _ = attendre(recharger(m))
        self.assertIn("Brune, batelière évacuée mange une part des vivres du refuge.", chronique(m))
        self.assertIn("vu_agir", [s["type"] for s in lire(m, "ilse")["memoire"]])


class RondeTests(unittest.TestCase):
    def test_la_ronde_de_gorm_decouvre_la_reserve_forcee(self):
        m = calme(relais(), "brune", "ilse", "aubin")
        m.objets["reserve"].update(verrouillee=False, ouverte=True)
        lire(m, "marchand")["besoins"].update(devoir=80.0, biens=30.0)
        m.joueur.update(salle="chambre_cloche", position=[1, 3])
        m, _ = attendre(recharger(m), 3)
        textes = chronique(m)
        self.assertIn("Gorm, gardien du relais ferme la réserve de vivres.", textes)
        self.assertIn("Gorm, gardien du relais verrouille la réserve de vivres.", textes)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertIn("antichambre", lire(m, "marchand")["visites"])
        self.assertIn("atteinte", [s["type"] for s in lire(m, "marchand")["memoire"]])

    def test_aubin_va_aux_vannes_et_revient(self):
        m = calme(relais(), "marchand", "brune", "ilse")
        # Calme, il fait ses rondes en routine (inquiet, il se mettrait d'abord à l'abri).
        lire(m, "aubin")["besoins"].update(securite=40.0, chaleur=0.0)
        m.joueur.update(salle="chambre_cloche", position=[1, 3])
        m, _ = attendre(recharger(m), 2)
        textes = chronique(m)
        aller = textes.index("Aubin, vieux passeur passe dans : Salle des vannes.")
        self.assertIn("Aubin, vieux passeur passe dans : Refuge du relais.", textes[aller:])
        self.assertEqual(m.objets["aubin"]["lieu"], "antichambre")
        visites = lire(m, "aubin")["visites"]
        self.assertGreater(visites["antichambre"], visites["crypte"])
        # Les deux rondes faites, il reste au refuge jusqu'à ce que l'une d'elles expire.
        m, _ = attendre(m, 4)
        self.assertEqual(m.objets["aubin"]["lieu"], "antichambre")


class DesespoirTests(unittest.TestCase):
    def brune_devant_ilse(self, faim):
        m = calme(refusee(relais()), "marchand", "ilse", "aubin")
        m.objets["crochets"]["lieu"] = "brune"
        m.objets["crochets"].pop("position", None)
        lire(m, "brune")["besoins"]["faim"] = faim
        placer(m, "brune", "antichambre", [7, 2])
        placer(m, "ilse", "antichambre", [6, 1])
        m.joueur.update(salle="chambre_cloche", position=[1, 3])
        return recharger(m)

    def test_affamee_a_l_extreme_elle_crochete_sous_les_yeux_d_ilse(self):
        m, _ = attendre(self.brune_devant_ilse(97.0), jet=20)
        textes = [c["texte"] for c in m.data["chronique"]]
        self.assertIn("Brune, batelière évacuée crochète la serrure de la réserve de vivres sans forcer.", textes)
        self.assertIn("Brune, batelière évacuée mange une part des vivres du refuge.", textes)
        # Réussi en douce, le crochetage ne fait qu'un bruit feutré (``ouie.nature_crochetage``) : Gorm,
        # à l'échoppe, ne l'entend pas (avant la branche crochetage-surenchere, un fracas qui le faisait
        # venir) ; Ilse, elle, l'a vue faire.
        self.assertNotIn("Gorm entend un bruit : Refuge du relais.", textes)
        souvenirs = [s for s in lire(m, "ilse")["memoire"] if s["type"] == "vu_agir"]
        self.assertEqual(souvenirs[0]["auteur"], "brune")
        self.assertFalse(relation(m, "ilse", "brune")["valeur"])

    def test_sinon_elle_attend_que_personne_ne_la_voie(self):
        m, _ = attendre(self.brune_devant_ilse(80.0), jet=20)
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        self.assertGreater(lire(m, "brune")["intention"]["attente"], 0)


if __name__ == "__main__":
    unittest.main()
