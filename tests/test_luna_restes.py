"""Contrats communs du MJ : vraie boucle de jeu, état et texte après rechargement."""
from donjon.emissions import pnj as emissions_pnj, joueur as emissions_joueur
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.mj import MJOpenAI
from donjon.biens import compte
from donjon.matiere import id_piece
from donjon.monde import ErreurMonde, Monde
from donjon.narration import consigner, unites_moteur
from donjon.rendu import decrire
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_luna_noms import action
from tests.test_parole_commune import scene, paroles_retenues
from tests.test_repli_et_appel import dialogue, parole
from tests.test_sous_obstacle import FORME, passage, scene as scene_obstacle
from tests.test_tensions import recharger


def jouer_physique(m, saisies, reponses, jugements=()):
    reponses, jugements, appels = list(reponses), list(jugements), []
    def appel(instructions, entree, intention, fonction, schema):
        appels.append((fonction, entree))
        if fonction == "auditer_portee":
            return {"descriptions": [], "usages": [{"perception_requise": False, "indice": False, "motif": ""}
                                                    for _ in entree["proposition_faits"]["ajouts"]]}
        if fonction == "auditer_capacites":
            return {"jugements": [jugements.pop(0)]}
        if fonction == "auditer_action":
            return {"conforme": True, "motif": ""}
        return reponses.pop(0)
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        m.sauver(chemin)
        saisies = iter([*saisies, "quitter"])
        flux, premiere = io.StringIO(), True
        def lire(_=""):
            nonlocal premiere
            if premiere:
                flux.seek(0)
                flux.truncate()
                premiere = False
            return next(saisies)
        with (patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
              patch.object(MJOpenAI, "_appeler_brut", side_effect=appel),
              patch("builtins.input", side_effect=lire),
              patch("sys.stdout", flux) as sortie):
            jeu.main(["--console", "--connexion", "api", "--save", str(chemin)])
        return Monde.charger(chemin), sortie.getvalue(), appels


class FormeTests(unittest.TestCase):
    def test_la_meme_regle_pour_une_autre_propriete_physique_inconnue(self):
        from donjon.atelier import nouveau_atelier
        from donjon.operations import etape, sequence
        for question, p in (("est-ce que je pourrais faire sonner la ficelle ?",
                             sequence(etape("emettre_son", "ficelle"))),
                            ("est-ce que je pourrais allumer la ficelle ?",
                             sequence(etape("allumer", "ficelle")))):
            with self.subTest(question=question):
                m = nouveau_atelier()
                avant = copy.deepcopy(m.objets["ficelle"])
                r, texte, appels = jouer_physique(m, [question], [action(p)])
                self.assertEqual(len(appels), 1)
                self.assertIn("Tu ne sais pas encore si cet objet se prête à ce geste", texte)
                self.assertEqual(r.objets["ficelle"], avant)
                self.assertEqual(r.data["minutes"], m.data["minutes"])

    def test_forme_inconnue_donne_immediatement_le_manque_du_monde(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            with self.subTest(cible=cible):
                m = scene_obstacle(scenario, cible, forme=False)
                avant = copy.deepcopy(m.data)
                r, texte, appels = jouer_physique(m,
                    [f"est-ce que je pourrais passer sous {m.objets[cible]['nom']} ?"],
                    [action(passage(cible))])
                self.assertIn("Le dégagement sous l'obstacle et sa hauteur ne sont pas encore décrits", texte)
                self.assertEqual(len(appels), 1)
                self.assertNotIn("passage", r.objets[cible])
                self.assertEqual(r.joueur["position"], avant["joueur"]["position"])
                self.assertEqual(r.data["minutes"], avant["minutes"])
                self.assertFalse(unites_moteur(texte))

    def test_description_nouvelle_persistante_avant_la_fiche_puis_le_passage(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            with self.subTest(cible=cible):
                m = scene_obstacle(scenario, cible, forme=False)
                ajout = {"mode": "etablir_faits", "texte": "", "faits": [], "proposition": {
                    "ajouts": [{"type": "qualification", "ancrage": cible, "passage": dict(FORME)}],
                    "suite": passage(cible)}}
                q = f"est-ce que je pourrais passer sous {m.objets[cible]['nom']} ?"
                r, texte, appels = jouer_physique(m, [q], [ajout],
                                                [{"compatible": True, "motif": "Disposition plausible."}])
                self.assertEqual([f for f, _ in appels],
                                 ["repondre_au_joueur", "auditer_portee", "auditer_capacites", "auditer_action"])
                self.assertIn("Ramper sous", texte)
                self.assertEqual(r.objets[cible]["passage"], FORME)
                self.assertEqual(r.joueur["position"], m.joueur["position"])
                entree = next(e for f, e in appels if f == "auditer_capacites")["qualifications"][0]
                self.assertEqual(entree["champs_a_etablir"], ["passage"])
                self.assertTrue(entree["objet"]["bloque_passage"])
                self.assertIn("physique", entree["objet"])
                r, texte, _ = jouer_physique(r, ["ramper sous " + m.objets[cible]["nom"], "tenter",
                                                "tourner ouest", "examiner " + m.objets[cible]["nom"]], [])
                self.assertIn("Tu passes en rampant", texte)
                self.assertEqual(r.joueur["position"][0], m.joueur["position"][0] + 2)
                self.assertTrue(r.objets[cible]["bloque_passage"])
                self.assertIn("Dégagement dessous", decrire(r, cible))

    def test_dimension_impossible_refusee_avant_la_revue_physique(self):
        for scenario, cible in (("relais", "poutre_conduite"), ("auberge", "table_longue")):
            with self.subTest(cible=cible):
                m = scene_obstacle(scenario, cible, forme=False)
                ajout = {"mode": "etablir_faits", "texte": "", "faits": [], "proposition": {
                    "ajouts": [{"type": "qualification", "ancrage": cible,
                                "passage": {**FORME, "degagement_cm": 200}}]}}
                r, texte, appels = jouer_physique(m,
                    [f"est-ce que je pourrais passer sous {m.objets[cible]['nom']} ?"],
                    [ajout, action(passage(cible))])
                self.assertFalse(any(f == "auditer_capacites" for f, _ in appels))
                self.assertNotIn("passage", r.objets[cible])
                self.assertIn("ne sont pas encore décrits", texte)
                self.assertEqual(r.joueur["position"], m.joueur["position"])

    def test_faits_et_suite_pour_une_autre_propriete_sans_reinterpretation(self):
        from donjon.atelier import nouveau_atelier
        from donjon.operations import etape, sequence
        m = nouveau_atelier()
        suite = sequence(etape("emettre_son", "hache"))
        ajout = {"mode": "etablir_faits", "texte": "", "faits": [], "proposition": {
            "ajouts": [{"type": "qualification", "ancrage": "hache",
                        "capacites": [{"nature": "son", "intensite": 1}]}], "suite": suite}}
        r, texte, appels = jouer_physique(m, ["est-ce que je peux faire sonner la hache ?"], [ajout],
                                         [{"compatible": True, "motif": "Un tintement discret est plausible."}])
        self.assertEqual([f for f, _ in appels], ["repondre_au_joueur", "auditer_portee", "auditer_capacites", "auditer_action"])
        self.assertEqual(r.objets["hache"]["sonorite"], 1)
        self.assertEqual(r.data["minutes"], m.data["minutes"])
        self.assertFalse(r.data["journal"])
        self.assertIn("Rien n'est encore tenté", texte)
        r, texte, appels = jouer_physique(r, ["sonner hache"], [])
        self.assertEqual(appels, [])
        self.assertTrue(r.data["journal"])


class ParoleTests(unittest.TestCase):
    def test_ressource_typee_decrite_par_le_meme_contrat_que_le_schema(self):
        for question, besoin in (("est-ce que quelqu'un a du bois ?", "chaleur"),
                                 ("qui a de quoi manger ?", "faim")):
            with self.subTest(besoin=besoin):
                r, texte, appels = jouer(scene(), question, [
                    parole(question, ("ressource", besoin, "", ""), personnage="ilse"),
                    dialogue("Ta question a été entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                revue = next(e["plan"]["parole"] for f, e in appels if f == "auditer_action")
                from donjon.paroles import RESSOURCES_DEMANDEES, SCHEMA_PAROLE
                self.assertEqual(revue["sens_contenu"][0]["ressource_recherchee"], RESSOURCES_DEMANDEES[besoin])
                schema = next(v["properties"] for v in SCHEMA_PAROLE["properties"]["contenu"]["items"]["anyOf"]
                              if "ressource" in v["properties"]["type"]["enum"])
                self.assertIn(RESSOURCES_DEMANDEES[besoin], schema["sujet"]["description"])
                self.assertEqual(emissions_joueur(r)[-1]["texte"], question)
                self.assertIn(question, texte)

    def test_nom_absent_de_la_citation_ecarte_sans_relance_ni_apprentissage(self):
        from tests.test_noms import relais
        from tests.test_tensions import placer
        from donjon.voix import designation, nom_pour_joueur, connait_nom
        for qui, nom in (("marchand", "Gorm"), ("aubin", "Aubin")):
            with self.subTest(nom=nom):
                m = relais()
                if qui != "marchand":
                    placer(m, "marchand", "crypte", (2, 3))
                    placer(m, qui, "echoppe", (1, 1))
                m = recharger(m)
                alias, apparence = designation(m, qui), nom_pour_joueur(m, qui)
                texte = apparence[:1].upper() + apparence[1:] + " dit : « Bonsoir. »"
                faux = ligne("parole", locuteur=alias, citation="Bonsoir.")
                faux["presentation"] = nom
                r, sortie, appels = jouer(m, "je dis à " + apparence + " : bonsoir", [
                    parole("bonsoir", personnage=alias), dialogue(texte)], [rapport(faux)])
                self.assertEqual([f for f, _ in appels].count("auditer_narration"), 1)
                self.assertEqual([f for f, _ in appels].count("repondre_au_joueur"), 2)
                self.assertIn(texte, sortie)
                self.assertNotIn(nom, sortie)
                self.assertFalse(connait_nom(r, "joueur", qui))
                self.assertNotIn("presentation", emissions_pnj(r)[-1])

    def test_adresse_individuelle_deja_fixee_pour_la_revue(self):
        for saisie in ("est-ce que quelqu'un a du bois ?", "qui peut nous aider ?"):
            for destinataire, adresse in (("ilse", "individuelle"),):
                with self.subTest(saisie=saisie, destinataire=destinataire):
                    r, texte, appels = jouer(scene(), saisie, [
                        parole(saisie, personnage=destinataire), dialogue("Ta question résonne.")],
                        [rapport(ligne("mecanique", sources=["conversation_validee"]))],
                        revues=[{"contenu_conforme": True, "motif": ""}])
                    self.assertEqual(emissions_joueur(r)[-1]["auditeur"], destinataire)
                    self.assertEqual(emissions_joueur(r)[-1]["texte"], saisie)
                    self.assertNotIn("Précise à qui", texte)
                    revues = [e for f, e in appels if f == "auditer_action"]
                    self.assertEqual(len(revues), 0)  # Mots exacts, aucune opération déclarée.
                    self.assertEqual(paroles_retenues(r, "aubin")[-1][2], saisie)

    def test_revue_du_contenu_seule_et_transfert_reel_hors_de_son_dossier(self):
        for cible in ("planches", "vivres"):
            with self.subTest(cible=cible):
                m = scene(ilse=(1, 5), aubin=(2, 3))
                # Un objet de l'interlocuteur, demandé pour soi ; le moteur décide l'issue.
                m.objets[cible].update(proprietaire="aubin", lieu="aubin")
                saisie = f"je paie Aubin trois pièces pour une part de {m.objets[cible]['nom']}"
                rendu = cible == "planches"
                recit = "Tu m'as payé 3 pièces."
                controle = ligne("mecanique", sources=["conversation_validee", "comptes"])
                controle["comptes"] = [compte("joueur", "aubin", montant=3, etat="rendu"),
                    compte("aubin", "joueur", id_piece(m, cible) if rendu else cible,
                           1, "rendu" if rendu else "du")]
                r, texte, appels = jouer(m, saisie, [parole("Je voudrais une part pour trois pièces.",
                    ("demande", cible, "", "3"), personnage="aubin"), dialogue(recit)],
                    [rapport(controle)])
                revue = next(e["plan"]["parole"] for f, e in appels if f == "auditer_action")
                self.assertEqual(set(revue), {"replique", "contenu", "sens_contenu", "comptes_avant"})
                self.assertFalse(any(c["etat"] == "rendu" for c in revue["comptes_avant"]))
                self.assertEqual(r.joueur["or"], m.joueur["or"] - 3)
                if cible == "planches":
                    self.assertEqual(r.objets[cible]["charges"], m.objets[cible]["charges"] - 1)
                    self.assertEqual(r.objets["planches_1"]["lieu"], "joueur")
                else:
                    self.assertEqual(r.objets[cible], m.objets[cible])
                self.assertIn(m.objets[cible]["nom"], revue["contenu"][0]["sujet"])
                self.assertEqual(len(emissions_joueur(r)), 1)
                self.assertIn("Tu dis", texte)
                self.assertIn(recit, texte)
                self.assertIn(recit, str(r.data["conversation"]))


class TexteTests(unittest.TestCase):
    def test_proses_persistantes_refusees_a_la_frontiere_decriture(self):
        from donjon.faits_locaux import preparer_faits
        from donjon.enrichissement import catalogue as portraits, preparer_complements
        from donjon.connaissances import catalogue as savoirs, preparer_savoirs
        from donjon.rendu import regarder
        for mauvais in ("Une marque à une case du seuil.", "Une marque située en (5, 11)."):
            m = scene(aubin=(2, 3))
            p = next(iter(portraits(m).items()))
            s = next(iter(savoirs(m).items()))
            propositions = [
                (preparer_faits, {"ajouts": [{"type": "detail", "ancrage": "planches", "nom": "marque",
                                             "genre": "f", "texte": mauvais}]}),
                (preparer_faits, {"ajouts": [{"type": "parole", "ancrage": "aubin", "nom": "",
                                             "genre": "", "texte": mauvais, "presentation": ""}]}),
                (preparer_complements, {"ajouts": [{"personnage": p[0],
                    "facette": p[1]["facettes_disponibles"][0], "description": mauvais}]}),
                (preparer_savoirs, {"personnage": s[0], "savoirs": [
                    {"sujet": next(iter(s[1]["sujets"])), "texte": mauvais}]})]
            avant = copy.deepcopy(m.data)
            for preparer, proposition in propositions:
                with self.subTest(voie=preparer.__name__, texte=mauvais):
                    with self.assertRaises(ErreurMonde) as e:
                        preparer(m, proposition, m.data["revision"])
                    self.assertIn("repères du lieu", str(e.exception))
                    self.assertIn("proposition.", e.exception.attendu)
                    r = recharger(m)
                    self.assertEqual(r.data, avant)
                    self.assertNotIn(mauvais, regarder(r))

    def test_positions_hors_de_vue_reprises_en_metres_et_persistantes(self):
        for cible, est in (("planches", 2), ("briquet", 3)):
            with self.subTest(cible=cible):
                m = scene()
                from donjon.geometrie import cases
                sol = cases(m.data["salles"][m.joueur["salle"]])
                m.joueur["position"] = list(next(c for c in sorted(sol) if (c[0] + est, c[1] + 2) in sol))
                p = [m.joueur["position"][0] + est, m.joueur["position"][1] + 2]
                m.objets[cible].update(lieu=m.joueur["salle"], position=p,
                                       position_salle=m.joueur["salle"])
                m.data.setdefault("souvenirs_visuels", {})[cible] = {
                    "salle": m.joueur["salle"], "position": list(p),
                    "nom": m.objets[cible]["nom"], "symbole": "!"}
                m.joueur["orientation"] = "nord"
                reponse = f"Tu ne le vois plus d'ici. Tu l'as vu à 2 mètres vers le sud et {est} mètres vers l'est."
                r, texte, appels = jouer(m, f"où est {m.objets[cible]['nom']} ?", [dialogue(reponse)], [rapport(
                    ligne("mecanique", sources=["souvenirs_visuels"]),
                    ligne("mecanique", sources=["souvenirs_visuels"]))])
                self.assertIn(reponse, texte)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], reponse)
                self.assertEqual(r.objets[cible]["lieu"], m.objets[cible]["lieu"])
                faits = appels[0][1]["faits"]
                souvenir = next(s for s in faits["souvenirs_visuels"] if s["id"] == cible)
                self.assertEqual(souvenir["vu_a"], f"2 mètres vers sud et {est} mètres vers est")
                for s in faits["salle"]["sorties_connues"].values():
                    self.assertNotIn("case", s)
                for s in faits["souvenirs_visuels"]:
                    self.assertNotIn("case", s.get("vu_a", ""))

    def test_unites_et_coordonnees_refusees_puis_reformulees(self):
        for mauvais in ("Il est à deux cases vers le sud.", "Il est aux coordonnées (5, 11).",
                        "Il se trouve en [2, 4].", "Il se trouve en x=3, y=7."):
            with self.subTest(mauvais=mauvais):
                bon = "Tu peux regarder autour de toi."
                r, texte, _ = jouer(scene(), "où est-il ?", [dialogue(mauvais), dialogue(bon)],
                    [rapport(ligne("mecanique", sources=["souvenirs_visuels"])), rapport(ligne("neutre"))])
                self.assertNotIn(mauvais, texte)
                self.assertIn(bon, texte)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], bon)

    def test_enregistrement_refait_le_controle_deterministe(self):
        for mauvais in ("Tu attends à une case du seuil.", "Tu vois une marque en (4, 8)."):
            m = scene()
            bon = "Tu attends près du seuil."
            r, _, _ = jouer(m, "où suis-je ?", [dialogue(bon)],
                            [rapport(ligne("neutre"))])
            # Même un audit altéré ne peut contourner le contrôle à l'écriture.
            from donjon.narration import controler
            faits = {"salle": {}}
            audit = controler(mauvais, rapport(ligne("mecanique", sources=["salle"])), faits)
            audit.update(texte_initial=mauvais, faits=faits, fondement="")
            avant = copy.deepcopy(r.data)
            with self.assertRaises(ErreurMonde):
                consigner(r, {"texte": mauvais, "_audit": audit})
            self.assertEqual(recharger(r).data, avant)

    def test_ambiance_absente_ne_justifie_pas_un_verdict_de_contradiction(self):
        for texte, entite in (("Des bruits lointains flottent dans l'air.", "bruits lointains"),
                              ("Une odeur de terre humide emplit l'air.", "odeur de terre")):
            with self.subTest(texte=texte):
                m = scene()
                avant = copy.deepcopy(m.objets)
                r, sortie, appels = jouer(m, "décris l'atmosphère", [dialogue(texte)], [
                    rapport(ligne("contradictoire", motif="Rien ne prouve cette perception.")),
                    rapport(ligne("ambiance", entites=[entite]))])
                self.assertIn(texte, sortie)
                self.assertEqual([f for f, _ in appels].count("repondre_au_joueur"), 1)
                self.assertEqual([f for f, _ in appels].count("auditer_narration"), 2)
                self.assertEqual(r.data["ambiances"][r.joueur["salle"]][-1]["texte"], texte)
                self.assertEqual(r.objets, avant)
                self.assertNotIn("rien de tel", sortie)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], texte)


if __name__ == "__main__":
    unittest.main()
