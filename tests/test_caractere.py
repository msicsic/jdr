"""Caractères et valeurs : caractéristiques de l'esprit, modulées par les états ; valeurs en
poids dans les coûts du planificateur et dans les échanges ; anciennes limites migrées.

Chaque test vérifie l'état du monde après rechargement.
"""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from donjon import corps
from donjon.caractere import STATS, VALEURS, caracteristique, modificateur, prix_faute
from donjon.deplacement_objet import deplacer
from donjon.echanges import PARTAGE, demander
from donjon.esprits import croire, lire
from donjon.geometrie import position_entree
from donjon.monde import ErreurMonde, Monde
from donjon.operations import etape, sequence
from donjon.moteur import Moteur
from donjon.paroles import esprits_interlocuteurs, jet_persuasion
from donjon.planification import planifier
from donjon.stratege import ErreurStrategie, valider
from tests.support import refusee, sans_evacues
from tests.test_tensions import attendre, placer, recharger, relais


def ancienne_partie(monde):
    """Une sauvegarde d'avant les valeurs : limites tout ou rien, cinq caractéristiques."""
    limites = {"marchand": ["ne_vole_pas", "ne_blesse_pas", "ne_ment_pas"], "brune": ["ne_blesse_pas"],
               "ilse": ["ne_vole_pas", "ne_blesse_pas", "ne_ment_pas"], "aubin": ["ne_vole_pas", "ne_blesse_pas",
                                                                                 "ne_ment_pas"]}
    data = copy.deepcopy(monde.data)
    for id, liste in limites.items():
        p = data["objets"][id]["profil"]
        del p["valeurs"]
        p["limites"] = liste
        for stat in ("VOL", "ELO", "PSY"):
            del p["caracteristiques"][stat]
    for stat in ("VOL", "ELO", "PSY"):
        del data["joueur"]["stats"][stat]
    for id in limites:
        data["objets"][id]["corps"].pop("volonte_brisee")
    data["joueur"]["corps"].pop("volonte_brisee")
    return data


class CaracteristiquesTests(unittest.TestCase):
    def test_chacun_a_les_huit_caracteristiques(self):
        m = relais()
        self.assertEqual(set(m.joueur["stats"]), set(STATS))
        self.assertEqual(m.joueur["stats"]["VOL"], 10)
        self.assertEqual(m.objets["marchand"]["profil"]["caracteristiques"]["VOL"], 13)
        mauvais = copy.deepcopy(m.data)
        mauvais["joueur"]["stats"]["VOL"] = 30
        with self.assertRaises(ErreurMonde):
            Monde(mauvais)

    def test_les_etats_modulent_les_caracteristiques_de_tous(self):
        m = relais()
        # Brune a faim depuis la veille : plus faible et plus maladroite, l'esprit intact.
        self.assertGreaterEqual(lire(m, "brune")["besoins"]["faim"], corps.CORPS["faim"]["urgence"])
        self.assertEqual(caracteristique(m, "brune", "DEX"), 15 - 2 * corps.MALUS)
        self.assertEqual(caracteristique(m, "brune", "INT"), 12)
        # La fatigue rend confus et moins attentif.
        lire(m, "brune")["besoins"]["repos"] = 90.0
        m = recharger(m)
        self.assertEqual(caracteristique(m, "brune", "INT"), 12 - 2 * corps.MALUS)
        self.assertEqual(caracteristique(m, "brune", "PER"), 11 - 2 * corps.MALUS)
        self.assertEqual(caracteristique(m, "brune", "CHA"), 11)
        # Le joueur, par la même règle que ses jets.
        corps.valeurs(m, "joueur").update(faim=80.0)
        self.assertEqual(modificateur(m, "joueur", "DEX"), (16 - 10) // 2 + corps.malus(m, "DEX"))

    def test_la_volonte_brisee_se_garde_et_se_borne(self):
        m = relais()
        self.assertEqual(modificateur(m, "ilse", "VOL"), -1)
        corps.briser(m, "ilse", 3)
        m = recharger(m)
        self.assertEqual(m.objets["ilse"]["corps"]["volonte_brisee"], 3)
        self.assertEqual(modificateur(m, "ilse", "VOL"), -4)
        corps.briser(m, "ilse", 99)
        self.assertEqual(recharger(m).objets["ilse"]["corps"]["volonte_brisee"], corps.BRISURE_MAX)
        corps.briser(m, "ilse", -99)
        self.assertEqual(modificateur(recharger(m), "ilse", "VOL"), -1)

    def test_la_volonte_de_l_auditeur_resiste_et_l_eloquence_convainc(self):
        m = relais()
        # Gorm (VOL 13) est plus dur à convaincre : le DD monte d'un cran.
        _, dd = jet_persuasion(m, "marchand", "ilse", 10)
        _, dd_sans = jet_persuasion(m, "ilse", "marchand", 10)
        self.assertEqual(dd - modificateur(m, "marchand", "VOL"), dd_sans - modificateur(m, "ilse", "VOL"))
        # Ilse (CHA 13, ELO 12) : au jet juste suffisant, son éloquence fait la différence.
        juste = dd - modificateur(m, "ilse", "CHA") - modificateur(m, "ilse", "ELO")
        with patch.object(Monde, "d20", return_value=juste):
            self.assertTrue(jet_persuasion(m, "marchand", "ilse", 10)[0])
            m.objets["ilse"]["profil"]["caracteristiques"]["ELO"] = 10
            self.assertFalse(jet_persuasion(m, "marchand", "ilse", 10)[0])


class ValeursTests(unittest.TestCase):
    def test_une_ancienne_partie_garde_ses_limites_en_valeurs(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "ancienne.json"
            chemin.write_text(json.dumps(ancienne_partie(relais()), ensure_ascii=False), encoding="utf-8")
            m = recharger(Monde.charger(chemin))
        for id in ("marchand", "ilse", "aubin"):
            self.assertNotIn("limites", m.objets[id]["profil"])
            self.assertEqual(m.objets[id]["profil"]["valeurs"]["honnetete"], 100)
            self.assertEqual(m.objets[id]["profil"]["valeurs"]["douceur"], 100)
        brune = m.objets["brune"]["profil"]
        self.assertEqual((brune["valeurs"]["honnetete"], brune["valeurs"]["douceur"]), (50, 100))
        self.assertEqual(set(brune["valeurs"]), set(VALEURS))
        self.assertEqual(brune["caracteristiques"]["VOL"], 10)
        self.assertEqual(m.joueur["stats"]["ELO"], 10)
        # Les comportements suivent : refusées, l'honnête n'a aucun plan, l'autre force la réserve.
        m = sans_evacues(m)
        refusee(m, "brune")
        refusee(m, "ilse")
        self.assertIsNone(prix_faute(m, "marchand"))
        but, etapes = planifier(m, "brune", "faim")
        self.assertIn("sans_temoin", {x["condition"] for x in etapes})

    def test_memes_moyens_valeurs_differentes(self):
        """Brune devant la réserve ouverte, Gorm à la salle des vannes : peu scrupuleuse, elle se
        sert ; plus honnête, elle va lui demander sa part."""
        def situation(honnetete):
            m = sans_evacues(relais())
            m.objets["reserve"].update(verrouillee=False, ouverte=True)
            placer(m, "marchand", "crypte", position_entree(m, "crypte"))
            croire(m, "brune", "marchand", "lieu", "crypte", "vu", salle="crypte", case=None)
            croire(m, "brune", "reserve", "etat", {"ouverte": True}, "vu")
            m.objets["brune"]["profil"]["valeurs"]["honnetete"] = honnetete
            return attendre(recharger(m), 4)[0]

        def gestes(m):
            return [c["texte"] for c in m.data["chronique"]
                    if c["pnj"] == "brune" and c["nature"] not in ("deplacement", "ouie")]

        avide, honnete = situation(20), situation(50)
        self.assertEqual(gestes(avide), ["Brune, batelière évacuée mange une part des vivres du refuge."])
        # Elle va lui demander sa part, sans rien prendre ; si Gorm a quitté les vannes, elle le cherche
        # en le hélant (selon l'instant où chacun choisit, il est parfois déjà revenu à sa vue).
        self.assertIn(gestes(honnete), (["Brune demande une part des vivres du refuge à Gorm (promis)."],
                                        ["Brune appelle : « Gorm ? »",
                                         "Brune demande une part des vivres du refuge à Gorm (promis)."]))
        self.assertIn({"de": "marchand", "objet": "vivres"},
                      [{k: s[k] for k in ("de", "objet")} for s in lire(honnete, "brune")["memoire"]
                       if s["type"] == "nourri"])
        # Les deux ont mangé ; une seule a volé.
        for m in (avide, honnete):
            self.assertEqual(m.objets["vivres"]["portions"], 3)
            self.assertLess(lire(m, "brune")["besoins"]["faim"], corps.CORPS["faim"]["urgence"])

    def test_la_detresse_use_l_honnetete_et_la_volonte_y_resiste(self):
        m = refusee(sans_evacues(relais()))
        valeurs = m.objets["brune"]["profil"]["valeurs"]
        valeurs["honnetete"] = 90
        faim = lire(m, "brune")["besoins"]
        faim["faim"] = 80.0
        self.assertIsNone(planifier(m, "brune", "faim"))
        faim["faim"] = 97.0
        m = recharger(m)
        _, etapes = planifier(m, "brune", "faim")
        self.assertIn("sans_temoin", {x["condition"] for x in etapes})
        # Avec plus de volonté, elle tient encore.
        m.objets["brune"]["profil"]["caracteristiques"]["VOL"] = 18
        self.assertIsNone(planifier(recharger(m), "brune", "faim"))
        # À l'honnêteté entière, jamais, même à bout.
        m.objets["brune"]["profil"]["valeurs"]["honnetete"] = 100
        lire(m, "brune")["besoins"]["faim"] = 100.0
        self.assertIsNone(planifier(recharger(m), "brune", "faim"))

    def test_le_partage_depend_de_l_altruisme_de_qui_donne(self):
        def demande(altruisme):
            m = relais()
            m.objets["marchand"]["profil"]["valeurs"]["altruisme"] = altruisme
            # Au jet juste suffisant pour un donneur altruiste (penchant +2).
            dd = jet_persuasion(m, "marchand", "ilse", PARTAGE - 2)[1]
            juste = dd - modificateur(m, "ilse", "CHA") - modificateur(m, "ilse", "ELO")
            with patch.object(Monde, "d20", return_value=juste):
                issue = demander(m, "ilse", "marchand", "vivres")
            return issue, recharger(m)

        issue, m = demande(70)
        self.assertEqual(issue, "promis")
        self.assertEqual(lire(m, "marchand")["engagements"][0]["pour"], "ilse")
        issue, m = demande(30)
        self.assertEqual(issue, "refus")
        self.assertEqual(lire(m, "marchand")["engagements"], [])

    def test_le_stratege_ne_fait_mentir_que_qui_peut_mentir(self):
        def proposer(m, id):
            return valider(m, id, {"decision": "plan", "besoin": "faim", "but": "tromper Gorm",
                                   "justification": "", "etapes": [{
                                       "operation": "dire", "cible": "marchand", "outil": "", "lieu": "",
                                       "sujet": "reserve", "attribut": "verrouillee", "valeur": "non"}]})
        m = relais()
        # La scène oppose l'interdit à 100 au mensonge permis ; Ilse est désormais à 80 au Relais.
        m.objets["ilse"]["profil"]["valeurs"]["honnetete"] = 100
        for id in ("ilse", "brune"):
            croire(m, id, "reserve", "verrouillee", True, "vu")
            croire(m, id, "marchand", "lieu", "echoppe", "vu", salle="echoppe", case=None)
        with self.assertRaisesRegex(ErreurStrategie, "il ne ment pas"):
            proposer(m, "ilse")
        self.assertEqual(proposer(m, "brune")["etapes"][-1]["contenu"],
                         {"sujet": "reserve", "attribut": "verrouillee", "valeur": False})

    def test_le_mj_recoit_les_valeurs_de_qui_parle(self):
        m = recharger(relais())
        self.assertEqual(esprits_interlocuteurs(m, ["marchand"])["marchand"]["valeurs"]["honnetete"], 100)

    def test_un_temoin_fatigue_remarque_moins(self):
        def difficulte(fatigue):
            m = relais()
            m.joueur.update(salle="echoppe", position=[3, 5])
            deplacer(m, "bois", "echoppe")
            placer(m, "bois", "echoppe", (4, 5))
            placer(m, "marchand", "echoppe", (2, 5))
            lire(m, "marchand")["besoins"]["repos"] = fatigue
            m = recharger(m)
            plan = Moteur(m).preparer(sequence(etape("deplacer", "bois", "joueur", methode="discret")))
            return int(re.search(r"difficulté (\d+)", plan.resume(m)).group(1))

        self.assertEqual(difficulte(10.0) - difficulte(90.0), corps.MALUS)


if __name__ == "__main__":
    unittest.main()
