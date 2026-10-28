"""Une confidence suit un fait et son destinataire, indépendamment des souvenirs."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from donjon import pnj, social
from donjon.deliberation import _a_dire
from donjon.esprits import MEMOIRE_MAX, croire, lire, memoriser
from donjon.monde import Monde
from donjon.temps import ecouler
from tests.support import regarder
from tests.test_constats_partages import scene
from tests.test_social import recharger


def confier(m, id="ilse"):
    lignes = []
    with patch.object(Monde, "d20", return_value=20):
        dit = social.bavarder(m, id, lignes)
    return recharger(m), dit, "\n".join(lignes)


def oublier(m, *ids):
    for id in ids:
        for _ in range(MEMOIRE_MAX + 1):
            memoriser(m, id, {"type": "parole", "texte": "Autre chose."})


class DejaDitTests(unittest.TestCase):
    def test_capture_mine3_episode_relu_et_souvenirs_sortis_ne_se_redisent_pas(self):
        m = Monde.charger(Path(__file__).parent / "data/mine3-josse-deja-dit.json")
        # Capture originale avant la confidence de la minute 14 ; le joueur
        # est placé près d'eux pour vérifier aussi les mots rendus à l'écran.
        m.joueur.update(salle="baraquement", position=[4, 4])
        regarder(m, "joueur", "josse")
        m.data["connus"] = sorted(m.objets)
        m.data["noms_connus"] = [k for k, o in m.objets.items() if o["type"] == "personnage"]
        nouvelle = next(copy.deepcopy(s) for s in lire(m, "josse")["memoire"] if s["type"] == "intention_lue")
        m, dit, texte = confier(recharger(m), "josse")
        # L'ancien suivi porte déjà Lucien : le fait lui était connu dès la
        # minute 4 (Rémy). La reprise ne doit même pas redire l'épisode à 14.
        self.assertNotIn("glisse à Lucien que Odon semble guetter la porte du bureau", texte)
        self.assertTrue(social.deja_dit(m, "josse", "lucien", nouvelle))
        for minute in (62, 110, 178, 247):
            oublier(m, "josse", "lucien")
            ecouler(m, (minute - m.data["minutes"]) * 600)
            croire(m, "josse", "odon", "intention", "guet", "devine", .6,
                   envers="porte_bureau", signe=nouvelle["signe"], episode=minute)
            memoriser(m, "josse", {**nouvelle, "minute": minute, "episode": minute, "confiance": .6})
            m, _, texte = confier(recharger(m), "josse")
            self.assertNotIn("glisse à Lucien que Odon semble guetter la porte du bureau", texte)
        self.assertEqual(sum("Josse dit à Lucien que Odon semble guetter" in c["texte"]
                             for c in m.data["chronique"]), 0)
        self.assertEqual(m.objets["odon"]["lieu"], "baraquement")

    def test_intention_et_accusation_une_fois_meme_reapprises_apres_oubli(self):
        from tests.support import lier
        for nouvelle in (
                {"type": "intention_lue", "auteur": "brune", "objet": "reserve", "signe": "guet",
                 "confiance": .8, "source": "devine", "episode": 1},
                {"type": "vol_surpris", "auteur": "brune", "objet": "vivres"}):
            with self.subTest(type=nouvelle["type"]):
                m = scene()
                lier(m, "ilse", "brune", False)
                lignes = []
                for n in range(3):
                    oublier(m, "ilse", "marchand")
                    if nouvelle["type"] == "intention_lue":
                        croire(m, "ilse", "brune", "intention", "guet", "devine", .8,
                               envers="reserve", signe="guet", episode=n)
                    memoriser(m, "ilse", {**nouvelle, "episode": n, "preuve": str(n)})
                    m, dit, texte = confier(recharger(m))
                    self.assertEqual(dit, n == 0)
                    lignes.append(texte)
                    ecouler(m, 600)
                self.assertTrue(lignes[0])
                self.assertEqual(lignes[1:], ["", ""])
                self.assertEqual(sum(c["nature"] == "social" for c in m.data["chronique"]), 1)

    def test_objets_homonymes_distincts_chacun_une_fois(self):
        m = scene()
        m.objets["autres_vivres"] = {**copy.deepcopy(m.objets["vivres"]), "id": "autres_vivres"}
        for objet in ("vivres", "autres_vivres"):
            croire(m, "ilse", objet, "etat", {"disponible": False}, "essai")
            m.data["connus"].append(objet)
        textes = []
        for _ in range(2):
            m, dit, texte = confier(recharger(m))
            self.assertTrue(dit)
            textes.append(texte)
            ecouler(m, 600)
        self.assertEqual(textes[0], textes[1])
        for objet in ("vivres", "autres_vivres"):
            self.assertEqual(lire(m, "marchand")["croyances"][objet]["etat"]["source"], "dit:ilse")
            self.assertEqual(m.objets[objet]["portions"], 0)
        oublier(m, "ilse", "marchand")
        m, dit, texte = confier(recharger(m))
        self.assertFalse(dit)
        self.assertEqual(texte, "")

    def test_changement_puis_retour_connu_du_destinataire_rouvre_le_constat(self):
        m = scene()
        for _ in range(2):
            croire(m, "ilse", "vivres", "etat", {"disponible": False}, "essai")
            lire(m, "marchand")["croyances"].pop("vivres", None)
            m, dit, texte = confier(recharger(m))
            self.assertTrue(dit)
            self.assertIn("épuisés", texte)
            ecouler(m, 600)
            m, dit, _ = confier(m)
            self.assertFalse(dit)
            m.objets["vivres"]["portions"] = 2
            croire(m, "ilse", "vivres", "etat", {"disponible": True}, "vu")
            croire(m, "marchand", "vivres", "etat", {"disponible": True}, "vu")
            # Ilse doit savoir que Gorm a appris le changement : elle le lui
            # annonce explicitement, plutôt que lire sa croyance privée.
            social.faire_entendre(m, "ilse", "marchand", "Les vivres sont disponibles.", ["vivres"], [],
                                 [{"type": "affirmation", "sujet": "vivres", "attribut": "etat",
                                   "valeur": {"disponible": True}}])
            m = recharger(m)
            m.objets["vivres"]["portions"] = 0
        self.assertEqual(sum(bool(c.get("constat_confie")) for c in m.data["chronique"]), 2)

    def test_retour_vu_du_seul_locuteur_ne_rouvre_pas_les_destinataires(self):
        m = scene()
        croire(m, "ilse", "vivres", "etat", {"disponible": False}, "essai")
        m, dit, _ = confier(recharger(m))
        self.assertTrue(dit)
        for n in range(2):
            ecouler(m, 600)
            croire(m, "ilse", "vivres", "etat", {"disponible": True}, "vu")
            croire(m, "ilse", "vivres", "etat", {"disponible": False}, "essai")
            oublier(m, "ilse", "marchand")
            m, dit, texte = confier(recharger(m))
            self.assertFalse(dit)
            self.assertEqual(texte, "")
            self.assertEqual(lire(m, "marchand")["croyances"]["vivres"]["etat"]["valeur"],
                             {"disponible": False})
            self.assertEqual(m.objets["vivres"]["portions"], 0)

    def test_valeurs_distinctes_par_destinataire_et_reaffirmation_sans_changement(self):
        m = scene()
        noyau = {"type": "affirmation", "sujet": "vivres", "attribut": "etat",
                 "valeur": {"disponible": False}}
        croire(m, "marchand", "vivres", "etat", {"disponible": True}, "vu")
        social.retenir_dit(m, "ilse", "marchand", noyau)
        social.retenir_dit(m, "ilse", "aubin", {**noyau, "valeur": {"disponible": True}})
        m = recharger(m)
        self.assertTrue(social.deja_dit(m, "ilse", "marchand", noyau))
        croire(m, "marchand", "vivres", "etat", {"disponible": True}, "vu")
        self.assertTrue(social.deja_dit(recharger(m), "ilse", "marchand", noyau))
        croire(m, "marchand", "vivres", "etat", {"disponible": False}, "dit:ilse")
        croire(m, "marchand", "vivres", "etat", {"disponible": True}, "vu")
        self.assertTrue(social.deja_dit(recharger(m), "ilse", "marchand", noyau))

    def test_lieu_et_accusation_restent_dits_apres_oubli(self):
        from tests.test_boucles_pnj import ballot_rendu
        from donjon.echanges import executer
        from tests.test_temps_etat import plan
        m = ballot_rendu()
        # Les deux personnages se parlent au dortoir, le bien est ailleurs.
        for id, case in (("hugues", [1, 1]), ("anselme", [2, 1])):
            m.objets[id].update(lieu="dortoir", position=case, position_salle="dortoir")
        croire(m, "hugues", "anselme", "lieu", "dortoir", "vu", salle="dortoir", case=[2, 1])
        m.joueur.update(salle="dortoir", position=[1, 2])
        regarder(m, "joueur", "hugues")
        regarder(m, "hugues", "anselme")
        m.data["connus"] = sorted(m.objets)
        m.data["noms_connus"] = [k for k, o in m.objets.items() if o["type"] == "personnage"]
        m.data["visitees"] = sorted(m.data["salles"])
        croire(m, "hugues", "ballot", "lieu", "etable", "vu", salle="etable", case=[3, 2])
        lignes = []
        for c in _a_dire(m, "hugues", "anselme", "lucien"):
            executer(m, "hugues", {**plan("dire", "anselme"), "contenu": c}, lignes)
        self.assertTrue(any("ballot" in t for t in lignes))
        oublier(m, "hugues", "anselme")
        m = recharger(m)
        # Réapprendre le même incident ne permet pas de prévenir une seconde fois.
        memoriser(m, "hugues", {"type": "vu_agir", "auteur": "lucien", "operation": "poser", "objet": "ballot",
                                "lieu": {"valeur": "etable", "salle": "etable", "case": [3, 2], "minute": 10}})
        self.assertEqual(_a_dire(m, "hugues", "anselme", "lucien"), [])
        # Un aller-retour appris du seul Hugues ne réapprend rien à Anselme.
        croire(m, "hugues", "ballot", "lieu", "grenier", "vu", salle="grenier", case=[1, 1])
        croire(m, "hugues", "ballot", "lieu", "etable", "vu", salle="etable", case=[3, 2])
        self.assertEqual(_a_dire(recharger(m), "hugues", "anselme", "lucien"), [])
        croire(m, "hugues", "ballot", "lieu", "grenier", "vu", salle="grenier", case=[1, 1])
        self.assertEqual(_a_dire(recharger(m), "hugues", "anselme", "lucien"), [
            {"sujet": "ballot", "attribut": "lieu", "valeur": "grenier"}])

    def test_meme_laps_decoupe_meme_monde_et_rendu(self):
        initial = scene()
        croire(initial, "ilse", "vivres", "etat", {"disponible": False}, "essai")
        lire(initial, "marchand")["libre"] = 10000
        resultats = []
        for tranches in ((1200,), (150,) * 8):
            m, lignes = recharger(initial), []
            with patch.object(Monde, "d20", return_value=20):
                for dt in tranches:
                    minutes = ecouler(m, dt)
                    pnj.avancer(m, minutes, lignes, dt)
                    m = recharger(m)
            self.assertEqual(sum("les vivres du refuge sont épuisés" in t for t in lignes), 1)
            resultats.append((m.data, lignes))
        self.assertEqual(*resultats)

    def test_capture_mine3_meme_laps_decoupe_apres_recharge(self):
        resultats = []
        for tranches in ((1200,), (150,) * 8):
            m = Monde.charger(Path(__file__).parent / "data/mine3-josse-deja-dit.json")
            lignes = []
            for dt in tranches:
                minutes = ecouler(m, dt)
                pnj.avancer(m, minutes, lignes, dt)
                m = recharger(m)
            self.assertFalse(any("Josse dit à Lucien que Odon semble guetter" in c["texte"]
                                 for c in m.data["chronique"]))
            resultats.append((m.data, lignes))
        self.assertEqual(*resultats)

    def test_ancienne_valeur_d_un_souvenir_ne_rouvre_pas_la_nouvelle(self):
        from tests.support import lier
        m = scene()
        lier(m, "ilse", "brune", False)
        for montant in (1, 2):
            memoriser(m, "ilse", {"type": "dette_niee", "auteur": "brune", "victime": "aubin", "montant": montant})
        m, dit, texte = confier(recharger(m))
        self.assertTrue(dit)
        self.assertIn("2 pièces", texte)
        ecouler(m, 600)
        m, dit, texte = confier(recharger(m))
        self.assertFalse(dit)
        self.assertEqual(texte, "")

    def test_ancien_relais_ne_remplace_pas_une_propriete_plus_recente(self):
        from tests.support import lier
        for attribut, valeur, details, nouvelle in (
                ("intention", "fatigue", {"envers": "reserve", "signe": "guet"},
                 {"type": "intention_lue", "auteur": "brune", "objet": "reserve", "signe": "guet", "confiance": .8}),
                ("etat", {"disponible": True}, {},
                 {"type": "constat", "objet": "vivres", "attribut": "etat", "valeur": {"disponible": False}})):
            with self.subTest(attribut=attribut):
                m = scene()
                lier(m, "marchand", "ilse", True)
                ecouler(m, 10 * 600)
                sujet = "brune" if attribut == "intention" else "vivres"
                croire(m, "marchand", sujet, attribut, valeur, "devine" if details else "vu", **details)
                avant = copy.deepcopy(lire(m, "marchand")["croyances"][sujet][attribut])
                m = recharger(m)
                for observe in (4, 10):
                    self.assertIsNone(social.recevoir(m, "marchand", "ilse", {
                        "type": "rumeur", "rang": 0, "evenement": {**nouvelle, "observe": observe}}))
                    m = recharger(m)
                    self.assertEqual(lire(m, "marchand")["croyances"][sujet][attribut], avant)

    def test_registre_sature_ne_perd_pas_un_fait_ancien(self):
        m = scene()
        for n in range(social.DITS_MAX):
            social.retenir_dit(m, "ilse", "marchand", {"type": "affirmation", "sujet": f"objet{n}",
                                                       "attribut": "lieu", "valeur": "echoppe"})
        m = recharger(m)
        for n in (0, social.DITS_MAX):
            self.assertTrue(social.deja_dit(m, "ilse", "marchand", {"type": "affirmation", "sujet": f"objet{n}",
                                                                  "attribut": "lieu", "valeur": "echoppe"}))
        self.assertEqual(len(lire(m, "ilse")["faits_dits"]), social.DITS_MAX)

    def test_ancienne_sauvegarde_reprend_les_suivis_disponibles(self):
        m = scene()
        croire(m, "ilse", "vivres", "etat", {"disponible": False}, "essai")
        lire(m, "ilse")["croyances"]["vivres"]["etat"]["confie"] = {
            "valeur": {"disponible": False}, "dit_a": ["marchand"]}
        lire(m, "ilse").pop("faits_dits")
        m, dit, texte = confier(recharger(Monde(copy.deepcopy(m.data))))
        self.assertFalse(dit)
        self.assertEqual(texte, "")
        self.assertTrue(lire(m, "ilse")["faits_dits"])

    def test_ancien_registre_migre_chaque_destinataire_sans_reouvrir(self):
        m = scene()
        noyau = {"type": "affirmation", "sujet": "vivres", "attribut": "etat",
                 "valeur": {"disponible": False}}
        cle, valeur = social.faits_dits(noyau)[0]
        lire(m, "ilse")["faits_dits"][cle] = {"valeur": valeur, "dit_a": ["marchand", "aubin"]}
        m = recharger(Monde(copy.deepcopy(m.data)))
        for id in ("marchand", "aubin"):
            self.assertTrue(social.deja_dit(m, "ilse", id, noyau))
        self.assertEqual(m.data, recharger(m).data)
