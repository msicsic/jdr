"""Jalon E : Luna stratège, validé par le moteur ; échanges sociaux entre PNJ."""

from tests.support import lier, relation
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
from donjon.esprits import croire, lire, percevoir_tous, percoit
from donjon.geometrie import placer, position_entree
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from donjon.pnj import avancer
from tests.support import refusee, regarder, presentes


def relais():
    m = creer("relais", depart="fixe")
    m.joueur.update(salle="chambre_cloche", position=list(position_entree(m, "chambre_cloche")))
    # Placement d'auteur : Gorm vient de faire ses rondes, il est à son poste.
    lire(m, "marchand")["visites"].update(antichambre=0, crypte=0)
    return presentes(m)


def reunir(m, *ids, salle="antichambre"):
    """Place les personnages côte à côte dans une salle, tournés les uns vers les autres, puis
    les laisse se percevoir."""
    from tests.support import regarder
    for n, id in enumerate(ids):
        m.objets[id]["lieu"] = salle
        placer(m.objets[id], salle, [1 + n, 4])
    for n, id in enumerate(ids):
        regarder(m, id, [1 + (n + 1 if n + 1 < len(ids) else n - 1), 4])
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
        if not self.reponses:  # Les autres PNJ consultés attendent.
            return {"decision": "attendre", "besoin": next(iter(entree["dossier"]["besoins"])), "but": "",
                    "etapes": [], "justification": "."}
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
        m = refusee(relais())
        deplacer(m, "pied_de_biche", "marchand")
        reunir(m, "brune", "marchand")
        m.joueur.update(salle="antichambre", position=[3, 4])
        regarder(m, "joueur", "marchand")  # Placement d'auteur : il les voit faire.
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
        # Une autre voie que le vol ne bloque pas le moteur : si elle avait échoué, il reprenait.
        self.assertNotIn("faim", lire(reprise, "brune")["renoncements"])
        self.assertEqual(reprise.data["stratege"]["bilan"]["plan"], 1)

    def test_en_jeu_le_joueur_entend_la_demande_et_la_partie_rechargee_la_garde(self):
        m = refusee(relais())
        deplacer(m, "pied_de_biche", "marchand")
        reunir(m, "brune", "marchand")
        m.joueur.update(salle="antichambre", position=[3, 4])
        regarder(m, "joueur", "marchand")  # Placement d'auteur : il les voit faire.
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
        # Brune pèse le vol ; Ilse, inquiète, se met à l'abri d'elle-même, sans stratège.
        self.assertEqual(appels, [("proposer_strategie", "brune")])
        self.assertIn("Brune demande le pied-de-biche à Gorm. Gorm lui remet le pied-de-biche.", sortie.getvalue())
        self.assertNotIn("décide", sortie.getvalue())
        # La stratégie a bien obtenu le prêt ; un marché peut ensuite lever le besoin
        # et faire rendre l'outil avant la fin des cinq minutes d'attente.
        porteur = reprise.objets["pied_de_biche"]["lieu"]
        self.assertIn(porteur, ("brune", "marchand"))
        if porteur == "marchand":
            self.assertTrue(any(s["type"] == "restitution" and s.get("objet") == "pied_de_biche"
                                and s.get("de") == "brune" for s in lire(reprise, "marchand")["memoire"]))
        self.assertEqual(reprise.data["stratege"]["bilan"]["plan"], 1)

    def test_un_refus_abandonne_la_strategie(self):
        m = refusee(relais())
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
        # La scène teste l'interdit à 100 ; l'Ilse du scénario a désormais une honnêteté graduée.
        m.objets["ilse"]["profil"]["valeurs"]["honnetete"] = 100
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
        # L'interdit du vol appartient ici au profil de la scène, plus à celui du scénario.
        m.objets["ilse"]["profil"]["valeurs"]["honnetete"] = 100
        reunir(m, "ilse", "brune")
        for objet, lieu in (("vivres", "reserve"), ("reserve", "antichambre"), ("crochets", "echoppe")):
            croire(m, "ilse", objet, "lieu", lieu, "savoir", salle=None, case=None)
        with self.assertRaisesRegex(stratege.ErreurStrategie, "il ne vole pas"):
            stratege.valider(m, "ilse", plan("faim", "manger", etape("manger", cible="vivres")))
        with self.assertRaisesRegex(stratege.ErreurStrategie, "ne sait pas crocheter"):
            stratege.valider(m, "ilse", plan("faim", "forcer", etape("crocheter", cible="reserve", outil="crochets")))
        # Brune peut mentir et voler, mais le geste attend de n'être vu de personne.
        decision = stratege.valider(m, "brune", plan("faim", "manger", etape("manger", cible="vivres")))
        # Le moteur dit comment : aller prendre les crochets, crocheter et ouvrir la réserve, puis manger.
        self.assertEqual([x["operation"] for x in decision["etapes"]][-4:], ["aller", "crocheter", "ouvrir", "manger"])
        self.assertIn("prendre", [x["operation"] for x in decision["etapes"]])
        self.assertEqual(decision["etapes"][-1]["condition"], "sans_temoin")
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
        m = refusee(relais())
        faux = Faux()
        stratege.activer(faux)
        lire(m, "brune")["besoins"]["faim"] = 96
        self.vivre(m, 1, faux)
        self.assertEqual(faux.recus, [])
        self.assertEqual(lire(m, "brune")["intention"]["but"]["type"], "manger")

    def test_ce_qu_il_a_confie_au_joueur_il_ne_le_fait_pas_a_sa_place(self):
        # Cas du banc A/B : Gorm, stratège en main, allait chercher la cloche confiée au joueur.
        m = relais()
        reunir(m, "marchand", "aubin")
        for proposition in (plan("devoir", "rapporter la cloche", etape("prendre", cible="cloche")),
                            plan("devoir", "confier la cloche à Aubin", etape("confier", cible="aubin", sujet="cloche",
                                                                              attribut="lieu", valeur="antichambre"))):
            with self.assertRaisesRegex(stratege.ErreurStrategie, "il a confié cette tâche"):
                stratege.valider(m, "marchand", proposition)
        # S'il cesse de croire le joueur fiable, la tâche lui revient.
        lier(m, "marchand", "joueur", False, "vu")
        stratege.valider(m, "marchand", plan("devoir", "rapporter la cloche", etape("prendre", cible="cloche")))

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
        # La tâche réalisable porte sur une place connue ; une absence crue en entrant la ferait
        # désormais abandonner et annoncer, au lieu de garder une promesse sans plan.
        croire(m, "aubin", "marteau", "lieu", "echoppe", "savoir", salle="echoppe",
               case=list(m.objets["marteau"]["position"]))
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



class LeviersTests(unittest.TestCase):
    def tearDown(self):
        stratege.activer(None)

    def test_un_besoin_de_repos_se_satisfait_en_s_asseyant(self):
        m = relais()
        lire(m, "aubin")["besoins"].update(repos=85, securite=0, chaleur=0)
        lignes = []
        m.data["minutes"] += 40
        avancer(m, 40, lignes)
        self.assertLessEqual(lire(m, "aubin")["besoins"]["repos"], 20)
        self.assertIn("Aubin, vieux passeur s'assoit pour se reposer.", [c["texte"] for c in m.data["chronique"]])
        self.assertNotEqual((lire(m, "aubin")["intention"] or {}).get("but"), {"type": "repos"})

    def test_une_part_demandee_au_proprietaire_est_servie_puis_la_reserve_refermee(self):
        from donjon.echanges import demander
        m = relais()
        reunir(m, "brune", "marchand")
        m.joueur.update(salle="antichambre", position=[3, 4])
        regarder(m, "joueur", "marchand")  # Placement d'auteur : il les voit faire.
        m.data["connus"] = sorted({*m.data["connus"], "brune", "marchand", "vivres"})
        for id in ("marchand", "brune", "ilse", "aubin"):
            lire(m, id)["besoins"].update({b: 0 for b in lire(m, id)["besoins"] if b != "faim"})
        lire(m, "marchand")["besoins"]["faim"] = 0
        lire(m, "brune")["besoins"]["faim"] = 60
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "brune", "marchand", "vivres"), "promis")
        self.assertEqual(lire(m, "marchand")["engagements"][0]["condition"], {"objet": "vivres", "servir": "brune"})
        portions, biens = m.objets["vivres"]["portions"], lire(m, "marchand")["besoins"]["biens"]
        lignes = []
        m.data["minutes"] += 15
        avancer(m, 15, lignes)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            reprise = Monde.charger(chemin)
        self.assertEqual(reprise.objets["vivres"]["portions"], portions - 1)
        self.assertLessEqual(lire(reprise, "brune")["besoins"]["faim"], 60 - 50 + 2)
        self.assertIs(relation(reprise, "brune", "marchand")["valeur"], True)
        self.assertEqual(lire(reprise, "marchand")["engagements"], [])
        # Ce qu'il a ouvert lui-même, il le referme à clé, sans s'en alarmer.
        self.assertTrue(reprise.objets["reserve"]["verrouillee"])
        self.assertFalse(reprise.objets["reserve"].get("ouverte"))
        self.assertEqual(lire(reprise, "marchand")["besoins"]["biens"], biens)
        self.assertNotIn("atteinte", [s["type"] for s in lire(reprise, "marchand")["memoire"]])
        self.assertIn("Gorm appelle Brune et lui donne une part des vivres du refuge.",
                      [c["texte"] for c in reprise.data["chronique"]])
        # Près de la réserve, hors de sa vue : le joueur ne le lit pas de ses yeux (son ouïe le lui dit).
        self.assertNotIn("Gorm appelle Brune et lui donne une part des vivres du refuge.", lignes)
        self.assertNotIn("vu_agir", [s["type"] for x in ("brune", "ilse", "aubin") for s in lire(reprise, x)["memoire"]])

    def test_une_part_se_refuse_au_mefiant_ou_quand_il_a_faim(self):
        from donjon.echanges import demander
        m = relais()
        reunir(m, "brune", "marchand")
        lire(m, "marchand")["besoins"]["faim"] = 90
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "brune", "marchand", "vivres"), "necessaire")
            lire(m, "marchand")["besoins"]["faim"] = 0
            lier(m, "marchand", "brune", False, "vu")
            self.assertEqual(demander(m, "brune", "marchand", "vivres"), "mefiance")
            # Le joueur a un corps lui aussi : il peut demander une part, que Gorm s'engage à servir.
            self.assertEqual(demander(m, "joueur", "marchand", "vivres"), "promis")
            self.assertIn({"objet": "vivres", "servir": "joueur"},
                          [x["condition"] for x in lire(m, "marchand")["engagements"]])

    def test_qui_vient_de_refuser_ne_se_voit_pas_redemander_la_meme_chose(self):
        m = relais()
        reunir(m, "brune", "marchand")
        lier(m, "marchand", "brune", False, "vu")
        faux = Faux(plan("faim", "demander une part à Gorm", etape("demander", cible="marchand", outil="vivres")))
        stratege.activer(faux)
        decision = stratege.consulter(m, "brune", "besoin_sans_plan", "faim")
        stratege.adopter(m, "brune", decision, m.data["minutes"])
        m.data["minutes"] += 2
        avancer(m, 2, [])
        self.assertIn({"type": "refus", "de": "marchand", "operation": "demander", "raison": "mefiance", "objet": "vivres"},
                      [{k: v for k, v in x.items() if k not in ("minute", "preuve")} for x in lire(m, "brune")["memoire"]])
        with self.assertRaisesRegex(stratege.ErreurStrategie, "a refusé il y a"):
            stratege.valider(m, "brune", plan("faim", "redemander", etape("demander", cible="marchand", outil="vivres")))
        # Un refus porte sur ce qui était demandé : autre chose peut se demander.
        deplacer(m, "pied_de_biche", "marchand")
        croire(m, "brune", "pied_de_biche", "lieu", "marchand", "vu", salle="antichambre", case=None)
        stratege.valider(m, "brune", plan("faim", "emprunter", etape("demander", cible="marchand", outil="pied_de_biche")))

    def test_le_moteur_ajoute_le_deplacement_qu_un_geste_suppose(self):
        m = relais()
        decision = stratege.valider(m, "ilse", plan("securite", "inspecter l'échoppe", etape("inspecter", lieu="echoppe")))
        self.assertEqual([(x["operation"], x["lieu"]) for x in decision["etapes"]],
                         [("aller", "echoppe"), ("inspecter", "echoppe")])
        decision = stratege.valider(m, "brune", plan("faim", "demander une part à Gorm",
                                                     etape("demander", cible="marchand", outil="vivres")))
        self.assertEqual([x["operation"] for x in decision["etapes"]], ["aller", "demander"])

    def test_hors_de_vue_dans_la_salle_il_s_approche_pour_parler(self):
        m = relais()
        m.objets["marchand"]["lieu"] = "antichambre"
        placer(m.objets["marchand"], "antichambre", [7, 2])
        placer(m.objets["brune"], "antichambre", [1, 4])
        percevoir_tous(m)
        # Elle l'a vu passer derrière le pilier : elle le sait dans le refuge, sans le voir.
        croire(m, "brune", "marchand", "lieu", "antichambre", "vu", salle="antichambre", case=[7, 2])
        lire(m, "marchand")["besoins"].update(devoir=0, biens=0, faim=0)
        self.assertFalse(percoit(m, "brune", "marchand") and percoit(m, "marchand", "brune"))
        faux = Faux(plan("faim", "demander une part à Gorm", etape("demander", cible="marchand", outil="vivres")))
        stratege.activer(faux)
        with patch.object(Monde, "d20", return_value=20):
            lignes = []
            m.data["minutes"] += 5
            avancer(m, 5, lignes)
        self.assertIn("Brune demande une part des vivres du refuge à Gorm (promis).", [c["texte"] for c in m.data["chronique"]])

    def test_le_stratege_peut_demander_une_part_au_proprietaire(self):
        m = relais()
        reunir(m, "brune", "ilse")
        decision = stratege.valider(m, "brune", plan("faim", "demander une part à Gorm",
                                                     etape("aller", lieu="echoppe"),
                                                     etape("demander", cible="marchand", outil="vivres")))
        self.assertEqual(decision["etapes"][1]["outil"], "vivres")
        with self.assertRaisesRegex(stratege.ErreurStrategie, "part d'une nourriture"):
            stratege.valider(m, "brune", plan("faim", "demander", etape("demander", cible="ilse", outil="vivres")))


if __name__ == "__main__":
    unittest.main()
