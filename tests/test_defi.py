"""Vérifie que les deux itinéraires du Relais des crues sont praticables."""
import copy
import unittest
from collections import deque
from pathlib import Path
from unittest.mock import patch

from donjon.artisanat import dossier as dossier_atelier
from donjon.carte import carte
from donjon.commandes import analyser
from donjon.defi import BEFFROI, OBJECTIF, PIED_BEFFROI, REFUGE, actualiser, nouveau_defi
from donjon.mj import MJOpenAI
from donjon.monde import Monde, ErreurMonde
from donjon.moteur import Moteur, proposition
from donjon.improvisation import proposition as improviser, issue
from donjon.operations import etape, sequence
from donjon.perception import eclairage
from donjon.spatial import installer as installer_spatial, preparer_pas


class DefiRelaisTests(unittest.TestCase):
    def setUp(self):
        self.m = nouveau_defi()
        installer_spatial(self.m)
        self.moteur = Moteur(self.m)

    def agir(self, action, cible="", outil=""):
        return self.moteur.executer(self.moteur.preparer(proposition(action, cible, outil)))

    def test_palper_coffre_ouvert_vide_corrige_recit_improvise(self):
        self.m.joueur.update(salle=BEFFROI, position=[4, 3])
        self.assertTrue(next(o for o in self.m.contexte()["objets_perceptibles"]
                             if o["id"] == "coffre")["contenu_vide"])
        p = improviser("Palper à la main les objets à l'intérieur du coffre",
                       issue("Tu sens des formes et des matières dans le coffre."),
                       cibles=["coffre"], approche="observation")
        plan = self.moteur.preparer(p, "MJ")
        self.assertEqual(plan.proposition["action"], "toucher")
        texte = self.moteur.executer(plan)
        self.assertIn("est vide", texte)
        self.assertNotIn("formes", texte)
        self.assertEqual(self.m.data["journal"][-1]["action"]["action"], "toucher")
        self.assertFalse(self.m.data.get("gestes_improvises"))

    def test_palper_coffre_ouvert_revele_son_contenu_reel(self):
        self.m.joueur.update(salle=BEFFROI, position=[4, 3])
        self.m.objets["cle"]["lieu"] = "coffre"
        self.m.objets["cle"].pop("position", None)
        self.assertFalse(next(o for o in self.m.contexte()["objets_perceptibles"]
                              if o["id"] == "coffre")["contenu_vide"])
        texte = self.agir("toucher", "coffre")
        self.assertIn("clé du relais", texte)
        self.assertIn("cle", self.m.data["connus"])

    def victoire(self):
        self.assertTrue(self.m.data.get("objectif_atteint"))
        lignes = []
        self.assertTrue(actualiser(self.m, lignes))
        self.assertTrue(self.m.data["objectif_atteint"])

    def marcher_jusqua(self, destination):
        """Cherche un chemin local sur une copie puis exécute réellement chaque pas."""
        simulation = self.m.copier()
        debut = tuple(simulation.joueur["position"])
        file, vus = deque([(debut, [])]), {debut}
        chemin = None
        while file:
            position, trajet = file.popleft()
            if position == tuple(destination):
                chemin = trajet
                break
            simulation.joueur["position"] = list(position)
            for direction in ("nord", "sud", "est", "ouest"):
                try:
                    suivant = preparer_pas(simulation, direction)
                except ErreurMonde:
                    continue
                p = tuple(suivant["position"])
                if suivant["salle"] == self.m.joueur["salle"] and p not in vus:
                    vus.add(p)
                    file.append((p, trajet + [direction]))
        self.assertIsNotNone(chemin, "Aucun chemin réel vers " + str(destination))
        for direction in chemin:
            self.agir("marcher", direction)

    def aller_dans(self, destination):
        salle = self.m.data["salles"][self.m.joueur["salle"]]
        direction, sortie = next((d, s) for d, s in salle["sorties"].items()
                                  if s["vers"] == destination)
        dx, dy = {"nord": (0, -1), "sud": (0, 1), "est": (1, 0), "ouest": (-1, 0)}[direction]
        case = sortie["case"]
        self.marcher_jusqua((case[0] - dx, case[1] - dy))
        self.agir("marcher", direction)
        self.assertEqual(self.m.joueur["salle"], destination)

    def test_route_interieure_avec_cle_et_retour(self):
        self.assertEqual(self.m.data["scenario"]["objectif"], OBJECTIF)
        self.assertFalse(self.m.visible("cle"))
        self.assertNotIn("cle", [o["id"] for o in self.m.contexte()["objets_perceptibles"]])
        examen = self.agir("examiner", "gravure")
        self.assertIn("contournant", examen)
        self.assertIn("face ouest de la cloison", examen)
        self.marcher_jusqua((6, 5))
        self.assertTrue(self.m.visible("cle"))
        self.agir("prendre", "cle")
        self.aller_dans("echoppe")
        self.aller_dans("crypte")
        self.marcher_jusqua((7, 3))
        self.agir("deverrouiller", "porte", "cle")
        self.agir("ouvrir", "porte")
        self.aller_dans(PIED_BEFFROI)
        self.aller_dans(BEFFROI)
        self.assertEqual(self.m.joueur["salle"], BEFFROI)
        self.marcher_jusqua((1, 3))
        self.agir("prendre", "cloche")
        self.assertFalse(self.m.data.get("objectif_atteint", False))
        self.aller_dans(PIED_BEFFROI)
        self.aller_dans("crypte")
        self.aller_dans("echoppe")
        self.aller_dans(REFUGE)
        self.assertEqual(self.m.joueur["salle"], REFUGE)
        self.victoire()

    def test_consigne_touche_la_cloison_et_relation_transmise_au_mj(self):
        salle = self.m.data["salles"][REFUGE]
        self.assertEqual(salle["plan"]["sol"][3][3], " ")
        self.assertEqual(self.m.objets["gravure"]["position"], [2, 3])
        self.assertEqual(self.m.objets["antichambre_murs"]["position"], [2, 3])
        self.assertTrue(self.m.visible("gravure"))
        fait = next(o for o in self.m.contexte()["objets_perceptibles"]
                    if o["id"] == "gravure")
        self.assertEqual(fait["fixee_sur"], "la face ouest de la cloison de pierre")

        self.m.memoriser("comment la consigne est elle attachée ?",
                         "Elle tient au mur, mais sa fixation est inconnue.")
        mj = MJOpenAI("gpt-6-luna")
        reponse = {"mode": "dialogue", "texte": "La consigne est sur la cloison.",
                   "faits": ["objet:gravure"], "proposition": None}
        with patch.object(mj, "_appeler", return_value=reponse) as appel:
            mj._echanger(self.m, "comment la consigne est elle attachée ?", None, True)
        instructions, entree, *_ = appel.call_args.args
        self.assertEqual(entree["faits"]["objet:gravure"]["fixee_sur"],
                         "la face ouest de la cloison de pierre")
        self.assertIn("L'état actuel prime", instructions)

    def test_ancienne_partie_ajuste_la_cloison_sans_deplacer_la_consigne(self):
        donnees = copy.deepcopy(self.m.data)
        donnees["salles"][REFUGE]["plan"]["sol"][3] = ".... ...."
        donnees["objets"]["antichambre_murs"]["position"] = [3, 3]
        donnees["objets"]["gravure"].pop("fixee_sur")
        donnees["exploration"][REFUGE].append([3, 3])
        reprise = Monde(donnees)
        self.assertEqual(reprise.data["salles"][REFUGE]["plan"]["sol"][3], "...  ....")
        self.assertEqual(reprise.objets["gravure"]["position"], [2, 3])
        self.assertEqual(reprise.objets["antichambre_murs"]["position"], [2, 3])
        self.assertNotIn([3, 3], reprise.data["exploration"][REFUGE])
        self.assertIn("! ##", carte(reprise))

    def test_route_exterieure_par_echelle_et_retour(self):
        with self.assertRaises(ErreurMonde):
            self.agir("installer", "echelle_relais", "appui_clocher")
        self.marcher_jusqua((7, 4))
        self.agir("installer", "echelle_relais", "appui_clocher")
        self.assertEqual(self.m.objets["echelle_relais"]["position"], [8, 3])
        with patch.object(Monde, "d20", return_value=20):
            self.agir("franchir", "echelle_relais")
        self.assertEqual(self.m.joueur["salle"], BEFFROI)
        self.assertEqual(self.m.joueur["position"], [0, 3])
        self.marcher_jusqua((1, 3))
        self.agir("prendre", "cloche")
        self.assertFalse(self.m.data.get("objectif_atteint", False))
        with patch.object(Monde, "d20", return_value=20):
            self.agir("franchir", "echelle_relais")
        self.assertEqual(self.m.joueur["salle"], REFUGE)
        self.victoire()

    def test_escalier_de_galerie_vers_palier_noir_reste_sur_la_carte(self):
        self.m.joueur.update(salle=BEFFROI, position=[0, 11])
        self.m.objets["torche"].update(allume=False, combustible=0)
        self.m.objets["lanterne"].update(allume=False, combustible=0)
        from donjon.spatial import memoriser
        memoriser(self.m)
        self.assertEqual(self.m.data["exploration"][PIED_BEFFROI], [])

        self.agir("marcher", "ouest")
        self.assertEqual((self.m.joueur["salle"], self.m.joueur["position"]),
                         (PIED_BEFFROI, [8, 3]))
        self.assertEqual(self.m.data["exploration"][PIED_BEFFROI], [[8, 3]])
        plan = carte(self.m).split("=== LEGENDE ===")[0]
        self.assertEqual(plan.count("@"), 1)
        self.assertIn("@ ^", plan)
        self.assertIn("v ", plan)

    def test_mj_recoit_la_manoeuvre_pour_monter_une_echelle_libre(self):
        self.marcher_jusqua((7, 3))
        manoeuvre = next(x for x in dossier_atelier(self.m)["manoeuvres"]
                         if x["echelle"] == "echelle_relais")
        self.assertEqual(manoeuvre["installation"], None)
        self.assertEqual(manoeuvre["installer_sur"], ["appui_clocher"])
        self.assertEqual(manoeuvre["installer_puis_franchir"], ["appui_clocher"])
        self.assertFalse(manoeuvre["franchir_maintenant"])

        mj = MJOpenAI("gpt-6-luna")
        # Forme réellement proposée par Luna : l'appui est mis dans destination.
        proposition_mj = sequence(etape("appuyer", "echelle_relais",
                                      destination="appui_clocher", methode="appui_mobile"),
                                  etape("franchir", "echelle_relais"))
        reponse = {"mode": "action", "texte": "", "faits": ["atelier"],
                   "proposition": proposition_mj}
        with patch.object(mj, "_appeler", return_value=reponse) as appel:
            resultat_mj = mj._echanger_prepare(self.m, "je monte a l'echelle")
        self.assertEqual(resultat_mj["proposition"], proposition_mj)
        instructions, entree, *_ = appel.call_args.args
        self.assertIn("appuyer puis franchir", instructions)
        self.assertEqual(entree["faits"]["atelier"]["manoeuvres"], [manoeuvre])

        plan = self.moteur.preparer(resultat_mj["proposition"], "LLM : gpt-6-luna")
        self.assertIn("2 étapes", plan.resume(self.m))
        self.assertEqual(plan.proposition["etapes"][0],
                         etape("appuyer", "echelle_relais", outil="appui_clocher"))
        variante = copy.deepcopy(proposition_mj)
        variante["etapes"][1]["destination"] = "appui_clocher"
        self.assertEqual(self.moteur.preparer(variante).proposition["etapes"][1],
                         etape("franchir", "echelle_relais"))
        autre_appui = copy.deepcopy(proposition_mj)
        autre_appui["etapes"][0]["destination"] = "cle"
        with self.assertRaises(ErreurMonde):
            self.moteur.preparer(autre_appui)
        with patch.object(Monde, "d20", return_value=20):
            self.moteur.executer(plan)
        self.assertEqual(self.m.objets["echelle_relais"]["installation"]["support"],
                         "appui_clocher")
        self.assertEqual(self.m.joueur["salle"], BEFFROI)
        chemin = Path("artifacts/tests/verification-echelle.json")
        try:
            self.m.sauver(chemin)
            reprise = Monde.charger(chemin)
            self.assertEqual(reprise.joueur["salle"], BEFFROI)
            self.assertIn("H1", carte(reprise))
        finally:
            chemin.unlink(missing_ok=True)

    def test_mj_recoit_l_installation_pour_deplacer_echelle_sur_appui(self):
        self.marcher_jusqua((7, 3))
        mj = MJOpenAI("gpt-6-luna")
        reponse = {"mode": "action", "texte": "", "faits": ["atelier"],
                   "proposition": proposition("installer", "echelle_relais", "appui_clocher")}
        with patch.object(mj, "_appeler", return_value=reponse) as appel:
            resultat_mj = mj._echanger_prepare(self.m, "je déplace l'echelle sur l'appui")
        self.assertEqual(resultat_mj["proposition"], reponse["proposition"])
        self.assertEqual(appel.call_args.args[1]["faits"]["atelier"]["manoeuvres"][0]
                         ["installer_sur"], ["appui_clocher"])
        plan = self.moteur.preparer(resultat_mj["proposition"], "LLM : gpt-6-luna")
        self.moteur.executer(plan)
        self.assertEqual(self.m.objets["echelle_relais"]["position"], [8, 3])

    def test_crochetage_au_toucher_dans_la_penombre(self):
        self.m.joueur.update(salle="crypte", position=[8, 3])
        self.m.objets["crochets"]["lieu"] = "joueur"
        for id in ("torche", "lanterne"):
            self.m.objets[id].update(allume=False, combustible=0)
        self.assertEqual(eclairage(self.m)["niveau"], 1)
        phrase = "j'utilise mes crochets pour crochetter la serrure"
        self.assertIsNone(analyser(self.m, phrase))
        mj = MJOpenAI("gpt-6-luna")
        reponse = {"mode": "action", "texte": "", "faits": ["objet:serrure", "objet:crochets"],
                   "proposition": proposition("crocheter", "serrure", "crochets", methode="finesse")}
        with patch.object(mj, "_appeler", return_value=reponse) as appel:
            resultat_mj = mj._echanger_prepare(self.m, phrase)
        self.assertEqual(appel.call_args.args[1]["faits"]["perception"]["niveau"], 1)
        plan = self.moteur.preparer(resultat_mj["proposition"], "LLM : gpt-6-luna")
        self.assertEqual((plan.dd, plan.minutes), (18, 5))
        self.assertIn("à tâtons", plan.resume(self.m))
        with patch.object(Monde, "d20", return_value=20):
            self.moteur.executer(plan)
        self.assertFalse(self.m.objets["porte"]["verrouillee"])
        chemin = Path("artifacts/tests/verification-crochetage.json")
        try:
            self.m.sauver(chemin)
            self.assertFalse(Monde.charger(chemin).objets["porte"]["verrouillee"])
        finally:
            chemin.unlink(missing_ok=True)

    def test_double_refus_explique_action_et_echec_du_rallumage(self):
        for id in ("torche", "lanterne"):
            self.m.objets[id].update(allume=False, combustible=0)
        self.assertEqual(eclairage(self.m)["niveau"], 1)
        avant = copy.deepcopy(self.m.data)
        lire = {"mode": "action", "texte": "", "faits": ["objet:gravure"],
                "proposition": proposition("lire", "gravure")}
        allumer = {"mode": "action", "texte": "", "faits": ["objet:torche"],
                   "proposition": sequence(etape("allumer", "torche", outil="briquet"))}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler", side_effect=[lire, allumer]) as appel:
            reponse = mj._echanger_prepare(self.m, "je lis la consigne")
        self.assertEqual(appel.call_count, 2)
        self.assertEqual(reponse["mode"], "dialogue")
        self.assertIn("Tu ne parviens pas à lire la consigne émaillée", reponse["texte"])
        self.assertIn("la lumière est insuffisante", reponse["texte"])
        self.assertIn("La torche n'a plus de combustible", reponse["texte"])
        self.assertEqual(self.m.data, avant)

    def test_attendre_seul_ne_remplace_pas_l_action_refusee(self):
        for id in ("torche", "lanterne"):
            self.m.objets[id].update(allume=False, combustible=0)
        avant = copy.deepcopy(self.m.data)
        lire = {"mode": "action", "texte": "", "faits": ["objet:gravure"],
                "proposition": proposition("lire", "gravure")}
        attendre = {"mode": "action", "texte": "", "faits": ["retour_moteur"],
                    "proposition": sequence(etape("patienter"))}
        mj = MJOpenAI("gpt-6-luna")
        with patch.object(mj, "_appeler", side_effect=[lire, attendre]):
            reponse = mj._echanger_prepare(self.m, "je lis la consigne")
        self.assertEqual(reponse["mode"], "dialogue")
        self.assertIn("la lumière est insuffisante", reponse["texte"])
        self.assertIn("Attendre ne réalise pas", reponse["texte"])
        self.assertEqual(self.m.data, avant)


if __name__ == "__main__":
    unittest.main()
