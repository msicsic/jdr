"""Jalon E : Luna stratège, validé par le moteur ; échanges sociaux entre PNJ."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon import stratege
from donjon.banc_pnj import creer
from donjon.deplacement_objet import deplacer
from donjon.echanges import confier
from donjon.esprits import croire, lire, percevoir_tous
from donjon.geometrie import placer, position_entree
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from donjon.pnj import avancer


def relais():
    m = creer("relais")
    m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
    return m


def reunir(m, *ids, salle="antichambre"):
    """Place les personnages côte à côte dans une salle, puis les laisse se percevoir."""
    for n, id in enumerate(ids):
        m.objets[id]["lieu"] = salle
        placer(m.objets[id], salle, [1 + n, 4])
    percevoir_tous(m)


def etape(operation, cible="", outil="", lieu="", sujet="", attribut="", valeur=""):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu,
            "sujet": sujet, "attribut": attribut, "valeur": valeur}


def plan(besoin, but, *etapes):
    return {"decision": "plan", "besoin": besoin, "but": but, "etapes": list(etapes), "justification": "."}


class Faux:
    """Luna simulée : renvoie ses réponses dans l'ordre et garde ce qu'elle a reçu."""

    def __init__(self, *reponses):
        self.reponses, self.recus = list(reponses), []

    def __call__(self, instructions, entree, intention, fonction, schema):
        self.recus.append((entree, schema))
        return self.reponses.pop(0)


class StrategeTests(unittest.TestCase):
    def tearDown(self):
        stratege.activer(None)

    def vivre(self, m, minutes, faux):
        stratege.activer(faux)
        lignes = []
        m.data["minutes"] += minutes
        avancer(m, minutes, lignes)
        return lignes

    def test_un_plan_illicite_laisse_le_caractere_choisir_puis_la_demande_aboutit(self):
        m = relais()
        deplacer(m, "pied_de_biche", "marchand")
        reunir(m, "brune", "marchand")
        m.joueur.update(salle="antichambre", position=[3, 4])
        m.data["connus"] = sorted({*m.data["connus"], "brune", "marchand", "pied_de_biche"})
        faux = Faux(plan("faim", "demander le pied-de-biche à Gorm",
                         etape("demander", cible="marchand", outil="pied_de_biche")))
        with patch.object(Monde, "d20", return_value=20):
            lignes = self.vivre(m, 3, faux)
        dossier = faux.recus[0][0]["dossier"]
        self.assertEqual(dossier["declencheur"]["nature"], "plan_illicite")
        self.assertTrue(any(x["condition"] == "sans_temoin" for x in dossier["plan_moteur"]))
        self.assertEqual(m.objets["pied_de_biche"]["lieu"], "brune")
        self.assertIn("Brune demande le pied-de-biche à Gorm. Gorm lui remet le pied-de-biche.", lignes)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        types = [s["type"] for s in lire(reprise, "brune")["memoire"]]
        self.assertIn("strategie_aboutie", types)
        self.assertIn({"type": "pret", "objet": "pied_de_biche", "a": "brune"},
                      [{k: v for k, v in s.items() if k != "minute"} for s in lire(reprise, "marchand")["memoire"]])
        # Le vol est seulement remis à plus tard : le répit court depuis la décision.
        self.assertEqual(lire(reprise, "brune")["renoncements"]["faim"], 1)
        self.assertEqual(reprise.data["stratege"]["bilan"]["plan"], 1)

    def test_en_jeu_le_joueur_entend_la_demande_et_la_partie_rechargee_la_garde(self):
        m = relais()
        deplacer(m, "pied_de_biche", "marchand")
        reunir(m, "brune", "marchand")
        m.joueur.update(salle="antichambre", position=[3, 4])
        m.data["connus"] = sorted({*m.data["connus"], "brune", "marchand", "pied_de_biche"})
        appels = []

        def luna(instructions, entree, intention, fonction, schema):
            appels.append((fonction, entree["dossier"]["personnage"]["id"]))
            if entree["dossier"]["personnage"]["id"] != "brune":
                return {"decision": "attendre", "besoin": "securite", "but": "", "etapes": [], "justification": "."}
            return plan("faim", "demander le pied-de-biche à Gorm",
                        etape("demander", cible="marchand", outil="pied_de_biche"))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch.object(MJOpenAI, "_appeler_brut", side_effect=luna),
                  patch.object(Monde, "d20", return_value=20),
                  patch("builtins.input", side_effect=["attendre", "quitter"]),
                  patch("sys.stdout", io.StringIO()) as sortie):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin), "--stratege"]), 0)
            reprise = Monde.charger(chemin)
        # Brune pèse le vol, Ilse cherche à se rassurer ; le budget de l'heure est alors épuisé.
        self.assertEqual(appels, [("proposer_strategie", "brune"), ("proposer_strategie", "ilse")])
        self.assertIn("Brune demande le pied-de-biche à Gorm. Gorm lui remet le pied-de-biche.", sortie.getvalue())
        self.assertNotIn("décide", sortie.getvalue())
        self.assertEqual(reprise.objets["pied_de_biche"]["lieu"], "brune")
        self.assertEqual(reprise.data["stratege"]["bilan"]["plan"], 1)

    def test_un_refus_abandonne_la_strategie(self):
        m = relais()
        deplacer(m, "pied_de_biche", "marchand")
        reunir(m, "brune", "marchand")
        faux = Faux(plan("faim", "demander le pied-de-biche à Gorm",
                         etape("demander", cible="marchand", outil="pied_de_biche"),
                         etape("aller", lieu="echoppe")))
        with patch.object(Monde, "d20", return_value=1):
            self.vivre(m, 3, faux)
        e = lire(m, "brune")
        self.assertEqual(m.objets["pied_de_biche"]["lieu"], "marchand")
        self.assertIn("strategie_echouee", [s["type"] for s in e["memoire"]])
        self.assertNotEqual((e["intention"] or {}).get("but", {}).get("type"), "strategie")
        self.assertIn("Brune renonce à demander le pied-de-biche à Gorm.", [c["texte"] for c in m.data["chronique"]])

    def test_le_moteur_refuse_un_mensonge_d_un_honnete_puis_accepte_la_correction(self):
        m = relais()
        reunir(m, "ilse", "marchand", "brune")
        faux = Faux(plan("securite", "rassurer Gorm",
                         etape("dire", cible="marchand", sujet="brune", attribut="lieu", valeur="chambre_cloche")),
                    plan("securite", "dire à Gorm où est Brune",
                         etape("dire", cible="marchand", sujet="brune", attribut="lieu", valeur="antichambre")))
        stratege.activer(faux)
        decision = stratege.consulter(m, "ilse", "besoin_sans_plan", "securite")
        self.assertEqual(decision["etapes"][0]["contenu"], {"sujet": "brune", "attribut": "lieu", "valeur": "antichambre"})
        refus = faux.recus[1][0]["refus_precedent"]["erreur"]
        self.assertIn("il ne ment pas", refus)
        self.assertEqual(m.data["stratege"]["bilan"], {"appels": 2, "refus": 1, "plan": 1})

    def test_limites_et_capacites_bornent_les_gestes(self):
        m = relais()
        reunir(m, "ilse", "brune")
        for objet, lieu in (("vivres", "reserve"), ("reserve", "antichambre"), ("crochets", "echoppe")):
            croire(m, "ilse", objet, "lieu", lieu, "savoir", salle=None, case=None)
        with self.assertRaisesRegex(stratege.ErreurStrategie, "il ne vole pas"):
            stratege.valider(m, "ilse", plan("faim", "manger", etape("manger", cible="vivres")))
        with self.assertRaisesRegex(stratege.ErreurStrategie, "ne sait pas crocheter"):
            stratege.valider(m, "ilse", plan("faim", "forcer", etape("crocheter", cible="reserve", outil="crochets")))
        # Brune peut mentir et voler, mais le geste attend de n'être vu de personne.
        decision = stratege.valider(m, "brune", plan("faim", "manger", etape("manger", cible="vivres")))
        self.assertEqual(decision["etapes"][0]["condition"], "sans_temoin")
        mensonge = stratege.valider(m, "brune", plan("securite", "accuser Ilse",
                                                     etape("dire", cible="ilse", sujet="ilse", attribut="fiable", valeur="non")))
        self.assertEqual(mensonge["etapes"][0]["contenu"]["valeur"], False)
        with self.assertRaisesRegex(stratege.ErreurStrategie, "suivre"):
            stratege.valider(m, "brune", {"decision": "suivre", "besoin": "faim", "but": "", "etapes": []})

    def test_un_geste_contredit_par_ses_croyances_est_refuse(self):
        m = relais()
        reunir(m, "brune", "ilse")
        with self.assertRaisesRegex(stratege.ErreurStrategie, "ne croit pas que ce personnage porte cet objet"):
            stratege.valider(m, "brune", plan("faim", "demander", etape("demander", cible="ilse", outil="vivres")))
        with self.assertRaisesRegex(stratege.ErreurStrategie, "ne porte pas cet objet"):
            stratege.valider(m, "brune", plan("faim", "donner", etape("remettre", cible="ilse", outil="crochets")))
        # Prendre d'abord, remettre ensuite : le plan le lui aura mis en main.
        stratege.valider(m, "brune", plan("faim", "donner", etape("prendre", cible="crochets"),
                                          etape("remettre", cible="ilse", outil="crochets")))

    def test_a_bout_le_besoin_passe_outre_les_scrupules(self):
        m = relais()
        faux = Faux()
        stratege.activer(faux)
        lire(m, "brune")["besoins"]["faim"] = 96
        self.vivre(m, 1, faux)
        self.assertEqual(faux.recus, [])
        self.assertEqual(lire(m, "brune")["intention"]["but"]["type"], "manger")

    def test_le_dossier_ne_contient_que_ce_que_le_pnj_sait(self):
        m = relais()
        ids = {o["id"] for o in stratege.dossier(m, "brune", "desoeuvre")["objets_connus"]}
        self.assertEqual(ids, set(lire(m, "brune")["croyances"]) - {"joueur"} - {
            p for p in m.objets if m.objets[p]["type"] == "personnage"})
        enum = stratege.schema(m, "brune")["properties"]["etapes"]["items"]["properties"]["cible"]["enum"]
        self.assertNotIn("cloche", enum)
        self.assertNotIn("cle_reserve", json.dumps(stratege.dossier(m, "brune", "desoeuvre")))

    def test_une_tache_confiee_devient_un_engagement_tenu(self):
        m = relais()
        reunir(m, "marchand", "aubin")
        croire(m, "aubin", "marteau", "lieu", "echoppe", "savoir", salle="echoppe", case=None)
        condition = {"objet": "marteau", "lieu": "antichambre"}
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(confier(m, "marchand", "aubin", condition), "accepte")
        lire(m, "aubin")["besoins"].update(securite=0, repos=0, faim=0)
        self.vivre(m, 40, None)
        self.assertEqual(m.objets["marteau"]["lieu"], "antichambre")
        self.assertEqual(lire(m, "aubin")["engagements"], [])
        self.assertIn("engagement_tenu", [s["type"] for s in lire(m, "aubin")["memoire"]])
        m.verifier()

    def test_budget_par_pnj_et_par_heure(self):
        m = relais()
        stratege.activer(Faux())
        self.assertTrue(stratege.disponible(m, "ilse", "besoin_sans_plan"))
        s = stratege.etat(m)
        s["dernier"]["ilse"] = m.data["minutes"]
        self.assertFalse(stratege.disponible(m, "ilse", "besoin_sans_plan"))
        s["appels"] = [m.data["minutes"]]
        self.assertTrue(stratege.disponible(m, "aubin", "besoin_sans_plan"))
        self.assertFalse(stratege.disponible(m, "aubin", "desoeuvre"))
        s["appels"].append(m.data["minutes"])
        self.assertFalse(stratege.disponible(m, "aubin", "besoin_sans_plan"))

    def test_sans_strategie_rien_ne_change(self):
        m = relais()
        self.vivre(m, 60, None)
        self.assertNotIn("stratege", m.data)
        self.assertFalse(any(c.get("nature") == "decision" for c in m.data.get("chronique", [])))


if __name__ == "__main__":
    unittest.main()
