"""A4a partiel : intentions de parole, état et rendu après sauvegarde réelle."""
import copy
import unittest

from donjon import agendas, deliberation, echanges, ecoute, planification
from donjon.esprits import croire, lire
from donjon.rendu import regarder as rendu
from tests.test_avis_menace import scene
from tests.test_tensions import recharger


def planifier_choix(m, acteur, identifiant):
    avant = copy.deepcopy(m.data)
    with planification.vues_du_choix(m, acteur):
        resultat = agendas.planifier(m, acteur, identifiant)
        assert m.data == avant, "Une évaluation d'agenda a publié sa transition"
    return resultat


def declarer(m, acteur="aubin", cible="ilse", avis=True):
    contenu = ({"avis": {"type": "avis", "objet": "antichambre", "attribut": "menace", "valeur": True}}
               if avis else {"fait": {"type": "affirmation", "sujet": "brasero", "attribut": "lieu", "valeur": "antichambre"}})
    m.objets[acteur]["profil"]["agendas"] = [
        {"sorte": "informer", "parametres": {"qui": [cible], **contenu}}]
    agendas.actualiser(m, acteur)
    return m


class ActivationTests(unittest.TestCase):
    def test_gorm_previent_deux_personnes_meme_laps_decoupe(self):
        from donjon import eau, pnj
        from donjon.temps import ecouler
        from tests.test_social import placer
        from tests.support import calme
        m = scene()
        # Deux repères propres : aucune prévision empruntée à l'esprit d'Aubin.
        eau.observer(m, "marchand", "crypte")
        ecouler(m, 15 * 600)
        eau.observer(m, "marchand", "crypte")
        calme(m, "marchand", "ilse", "brune", "aubin")
        placer(m, "aubin", "echoppe", [1, 1])
        placer(m, "brune", "antichambre", [2, 4])
        for qui in ("ilse", "brune"):
            croire(m, "marchand", qui, "lieu", "antichambre", "vu", salle="antichambre", case=m.objets[qui]["position"])
        # Les destinataires écoutent ; leur évacuation appartient au prochain lot.
        for qui in ("ilse", "brune", "aubin"):
            lire(m, qui)["libre"] = 1000000
        # Ce test conserve son objectif de transmission indépendamment du
        # projet d'évacuation désormais déclaré par la crue.
        declarer(m, "marchand", "ilse")
        m.objets["marchand"]["profil"]["agendas"][0]["parametres"]["qui"] = ["ilse", "brune"]
        lire(m, "marchand").pop("agendas", None)
        agendas.actualiser(m, "marchand")
        m = recharger(m)
        a, b = recharger(m), recharger(m)
        def avancer(n, dt):
            lignes = []
            pnj.avancer(n, ecouler(n, dt), lignes, dt)
            return recharger(n)
        a = avancer(a, 3 * 600)
        for _ in range(6):
            b = avancer(b, 300)
        self.assertEqual(a.data, b.data)
        self.assertEqual(rendu(a), rendu(b))
        self.assertEqual(agendas.projets(a, "marchand")[0]["etat"], "atteint")

    def test_deux_parcours_parole_reception_et_rendu_recharges(self):
        for acteur, cible, avis in (("aubin", "ilse", True), ("marchand", "aubin", False)):
            with self.subTest(acteur=acteur):
                m = scene()
                if not avis:
                    croire(m, acteur, "brasero", "lieu", "antichambre", "vu", salle="antichambre", case=[2, 2])
                declarer(m, acteur, cible, avis)
                m = recharger(m)
                resultat = planifier_choix(m, acteur, "a1")
                self.assertIsNotNone(resultat)
                but, etapes = resultat
                self.assertEqual(but["type"], "agenda")
                lignes = []
                self.assertTrue(echanges.executer(m, acteur, etapes[-1], lignes))
                agendas.actualiser(m, acteur)
                self.assertEqual(agendas.projets(m, acteur)[0]["etat"], "atteint")
                avant = copy.deepcopy(m.data)
                m = recharger(m)
                self.assertEqual(m.data, avant)
                self.assertEqual(rendu(m), rendu(recharger(m)))
                sons = ecoute.entendus(m, -1, ecoute.ENTENDU)
                self.assertEqual(ecoute.rendre(m, sons), ecoute.rendre(recharger(m), sons))
                self.assertTrue(any("dit" in c["texte"] and c["pnj"] == acteur
                                    for c in m.data["chronique"]))
                if avis:
                    from donjon.esprits import prevision
                    self.assertEqual(prevision(m, cible, "antichambre")["source"], "dit:" + acteur)
                agendas.actualiser(m, acteur)
                self.assertEqual(agendas.projets(m, acteur)[0]["etat"], "atteint")

    def test_sommeil_sans_position_crue_et_reveil(self):
        m = declarer(scene())
        croire(m, "aubin", "ilse", "lieu", None, "vu", salle=None, case=None)
        self.assertIsNone(planifier_choix(m, "aubin", "a1"))
        m = recharger(m)
        self.assertEqual(agendas.projets(m, "aubin")[0]["etat"], "sommeil")
        agendas.actualiser(m, "aubin")
        self.assertEqual(agendas.projets(m, "aubin")[0]["etat"], "sommeil")
        depuis = agendas.projets(m, "aubin")[0]["depuis"]
        croire(m, "aubin", "brasero", "etat", {"allume": False}, "vu")
        agendas.actualiser(m, "aubin")
        self.assertIsNone(planifier_choix(m, "aubin", "a1"))
        self.assertEqual(agendas.projets(recharger(m), "aubin")[0]["etat"], "sommeil")
        self.assertEqual(agendas.projets(m, "aubin")[0]["depuis"], depuis)
        croire(m, "aubin", "ilse", "lieu", "antichambre", "vu", salle="antichambre", case=[3, 4])
        agendas.actualiser(m, "aubin")
        m = recharger(m)
        self.assertEqual(agendas.projets(m, "aubin")[0]["etat"], "sommeil")
        self.assertIsNotNone(planifier_choix(m, "aubin", "a1"))
        self.assertEqual(agendas.projets(recharger(m), "aubin")[0]["etat"], "actif")

    def test_desespoir_devant_agenda_et_pas_de_stock_sans_declaration(self):
        m = scene()
        avant = copy.deepcopy(m.data)
        agendas.actualiser(m, "aubin")
        self.assertEqual(m.data, avant)
        declarer(m)
        lire(m, "aubin")["besoins"]["faim"] = 100
        candidats = list(deliberation._candidats(m, "aubin"))
        faim = next(c for c in candidats if c.besoin == "faim")
        agenda = next(c for c in candidats if c.besoin == "agenda")
        self.assertLess(faim.urgence.cle(), agenda.urgence.cle())
        m = declarer(scene(), "marchand", "ilse", False)
        lire(m, "marchand")["besoins"]["biens"] = 100
        candidats = list(deliberation._candidats(m, "marchand"))
        agenda = next(c for c in candidats if c.besoin == "agenda")
        recours = [c for c in candidats if c.besoin == "biens" and c.recours]
        self.assertTrue(any(c.routine for c in recours))
        self.assertTrue(all(c.urgence.cle() < agenda.urgence.cle() for c in recours))

    def test_activation_unique_plafond_et_copies(self):
        m = scene()
        declarer(m)
        declaration = m.objets["aubin"]["profil"]["agendas"][0]
        # Nouvelle scène, avant la première activation.
        n = scene()
        n.objets["aubin"]["profil"]["agendas"] = [copy.deepcopy(declaration) for _ in range(5)]
        agendas.actualiser(n, "aubin")
        self.assertEqual(sum(a["etat"] == "actif" for a in agendas.projets(n, "aubin")), 3)
        avant = copy.deepcopy(n.data)
        agendas.actualiser(n, "aubin")
        self.assertEqual(n.data, avant)
        agendas.projets(n, "aubin")[0]["etat"] = "atteint"
        self.assertEqual(n.data, avant)
        self.assertEqual(recharger(n).data, avant)

    def test_abstention_du_registre_plein_ne_prouve_pas_une_transmission(self):
        from donjon import social
        m = declarer(scene())
        lire(m, "aubin")["faits_dits"] = {
            str(i): {"valeur": True, "dit_a": {}} for i in range(social.DITS_MAX)}
        agendas.actualiser(m, "aubin")
        self.assertEqual(agendas.projets(m, "aubin")[0]["etat"], "actif")
        self.assertIsNone(planifier_choix(m, "aubin", "a1"))
        m = recharger(m)
        self.assertEqual(agendas.projets(m, "aubin")[0]["etat"], "sommeil")
        self.assertEqual(agendas.projets(m, "aubin")[0]["raison"], "transmission non attestee")
