"""A2 consultation : charge, raccourcis et paroles réellement sauvegardées."""
import copy
import io
import json
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import jeu
from donjon.commandes import consultation_locale
from donjon.comprehension import contenu as public
from donjon.contrats_consultation import CONSULTATIONS, typer
from donjon.dialogues import parole_information, parole_compte, comptes_publics
from donjon.emissions import joueur, pnj
from donjon.esprits import croire, croyance
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde, nouveau_monde
from donjon.paroles import SCHEMA_PAROLE, preparer_parole, verifier_contenus, SENS_CONTENU, CHAMPS_CONTENU
from donjon.rendu import regarder, fiche
from donjon.scene import scene_percue
from tests.test_comprehension import MJSimule, PontScript, dire
from tests.test_parole_corrections import banc
from tests.test_tensions import recharger
from tests.test_messages_decoupage import vivre


class ContratsConsultationTests(unittest.TestCase):
    def conforme(self, c):
        """Contrôle les contraintes de chaque variante ordinaire réellement émise."""
        variantes = SCHEMA_PAROLE["properties"]["contenu"]["items"]["anyOf"]
        s = next(s for s in variantes if s["properties"]["type"]["enum"] == [c["type"]])
        return (set(c) == set(s["required"]) and all(
            isinstance(v, str) and ("enum" not in s["properties"][k] or v in s["properties"][k]["enum"])
            and ("pattern" not in s["properties"][k] or re.search(s["properties"][k]["pattern"], v))
            for k, v in c.items()))

    def boucle(self, m, mots, c, *, question_mj=False):
        from donjon.repliques_moteur import reponse, sceller
        if question_mj:
            resultat = {"mode": "dialogue", "texte": "Tu ne connais pas sa réponse.", "proposition": None}
        else:
            resultat = dire(m, mots, mots, [c])
            p = resultat["_transactions"][0]["proposition"]
            _, rapport = preparer_parole(m, p)
            fixee = reponse(rapport)
            if fixee:
                resultat.update(sceller(fixee, rapport))
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "partie.json"
            m.sauver(chemin)
            mj = MJSimule(resultat)
            pont = PontScript(["mj " + mots, "tenter", "quitter"], chemin)
            with patch.object(jeu, "MJ", return_value=mj), patch.dict("os.environ", {"OPENAI_API_KEY": "test"}), \
                 patch.object(Monde, "d20", return_value=20), patch("sys.stdout", io.StringIO()):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(chemin)], interface=pont), 0)
            r = Monde.charger(chemin)
            self.assertEqual(r.data, json.loads(json.dumps(mj.monde.data)))
            texte = "\n".join(pont.historique)
            echange = r.data["conversation"][-1]
            self.assertIn(echange["reponse"], texte)
            self.assertEqual((regarder(r), fiche(r), scene_percue(r)),
                             (regarder(mj.monde), fiche(mj.monde), scene_percue(mj.monde)))
            reprise = PontScript(["quitter"], chemin)
            with patch("sys.stdout", io.StringIO()):
                jeu.main(["--console", "--offline", "--save", str(chemin)], interface=reprise)
            self.assertIn(echange["reponse"], "\n".join(reprise.historique))
            self.assertEqual(Monde.charger(chemin).data, r.data)
            return r, texte

    def test_cas_historique_ressources_et_autre_bien_sans_transfert(self):
        for script, mots, sujet in (("ressources", "Aubin, as-tu du bois ?", "bois"),
                                    ("sous-obstacle-auberge", "As-tu une lampe ?", "lampe")):
            with self.subTest(script=script):
                m = banc(script)
                if sujet == "lampe":
                    from donjon.paroles import prevue
                    from donjon.voix import reel
                    m.joueur["orientation"] = "ouest"
                    qui = reel(m, prevue(m, mots)["personnage"])
                    m.objets["lampe_temoin"] = {**banc("noms-dialogue").objets["lanterne"],
                        "id": "lampe_temoin", "nom": "lanterne de voyage", "aliases": ["lampe"],
                        "lieu": qui, "proprietaire": qui}
                    m = recharger(m)
                c = consultation_locale("ressource", sujet)
                avant = copy.deepcopy(m.objets)
                r, texte = self.boucle(m, mots, c)
                self.assertEqual(r.objets, avant)
                self.assertEqual(r.joueur, m.joueur)
                self.assertEqual(joueur(r)[-1]["texte"], mots)
                self.assertEqual(pnj(r)[-1]["acte"], "reponse_information")
                self.assertTrue(pnj(r)[-1]["texte"].startswith("J'ai "))
                self.assertIn(pnj(r)[-1]["rendu_public"], texte)
                self.assertIn(public(m, c), r.data["conversation"][-1]["compris"])

    def test_localisation_reponse_crue_et_non_position_cachee(self):
        for sujet, cru, reel in (("ilse", "crypte", "beffroi"), ("brune", "beffroi", "crypte")):
            with self.subTest(sujet=sujet):
                m = banc("noms-dialogue")
                m.objets[sujet]["lieu"] = reel
                placer(m.objets[sujet], reel, [3, 3])
                croire(m, "aubin", sujet, "lieu", cru, "vu", 1.0, salle=cru, case=None)
                m = recharger(m)
                mots = f"Aubin, où est {m.objets[sujet]['nom'].split(',')[0]} ?"
                c = consultation_locale("localisation", sujet)
                r, texte = self.boucle(m, mots, c)
                self.assertEqual(croyance(r, "joueur", sujet, "lieu")["valeur"], cru)
                self.assertEqual(r.objets[sujet]["lieu"], reel)
                self.assertIn("J'ai vu à la minute", pnj(r)[-1]["texte"])
                self.assertIn(public(m, c), r.data["conversation"][-1]["compris"])

    def test_reclamation_sous_forme_question_reglement_et_refus(self):
        for script, qui, gain in (("ressources", "aubin", 0), ("comptes", "marchand", 2),
                                  ("comptes", "brune", 0)):
            with self.subTest(script=script, qui=qui):
                from tests.support import presentes, regarder as voir
                m = presentes(banc(script), qui)
                voir(m, "joueur", qui)
                voir(m, qui, "joueur")
                mots = m.objets[qui]["nom"].split(',')[0] + ", tu me dois quelque chose ?"
                r, texte = self.boucle(m, mots, consultation_locale("reclamer"))
                self.assertEqual(r.joueur["or"], m.joueur["or"] + gain)
                self.assertIn("réclamer le dû : pièces", r.data["conversation"][-1]["compris"])
                self.assertIn(pnj(r)[-1]["texte"], texte)
                if qui == "brune":
                    self.assertEqual(pnj(r)[-1]["modalite"], "refus")

    def test_question_au_mj_ne_cree_aucune_parole_de_corvus(self):
        m = banc("ressources")
        r, texte = self.boucle(m, "Selon toi, Aubin possède-t-il du bois ?", None, question_mj=True)
        self.assertEqual(joueur(r), joueur(m))
        self.assertEqual(pnj(r), pnj(m))
        self.assertNotIn("Compris :", texte)
        self.assertEqual(r.objets, m.objets)

    def test_mots_sans_acte_type_ne_consultent_pas(self):
        m = banc("ressources")
        mots = "Aubin, as-tu du bois ?"
        p = {"personnage": "aubin", "replique": mots, "_intention": mots,
             "contenu": [{"type": "propos", "sujet": "", "attribut": "", "valeur": ""}]}
        r, rapport = preparer_parole(m, p)
        r = recharger(r)
        self.assertEqual(rapport["faits"], [])
        self.assertFalse(any(e["acte"] == "reponse_information" for e in pnj(r)))
        self.assertEqual(public(m, p["contenu"][0]), "propos sans effet mécanique typé")
        self.assertEqual(r.objets, m.objets)

    def test_raccourcis_information_et_comptes_gardent_la_meme_charge(self):
        m = banc("ressources")
        for acte, sujet in (("qui", ""), ("localisation", "brune"), ("ressource", "chaleur")):
            with self.subTest(acte=acte):
                d = {"geste": "information", "cible": "aubin",
                     "parametres": {"acte": acte, **({"sujet": sujet} if sujet else {})}}
                p = parole_information(m, d)
                self.assertEqual(p["contenu"], [consultation_locale(acte, sujet)])
                explicite = {**p, "_intention": "je dis à Aubin : « " + p["replique"] + " »"}
                with patch.object(Monde, "d20", return_value=20):
                    a, ra = preparer_parole(m, {**p, "_adresse": d})
                    b, rb = preparer_parole(m, explicite)
                self.assertEqual(recharger(a).data, recharger(b).data)
                self.assertEqual(ra, rb)
        d = next(x["descripteur"] for x in comptes_publics(m)["choix"]
                 if x["descripteur"]["cible"] == "aubin" and x["descripteur"]["parametres"].get("operation") == "question")
        self.assertEqual(parole_compte(m, d)["contenu"], [consultation_locale("reclamer")])

    def test_champs_voisins_et_interlocuteur_substitue_refuses_sans_mutation(self):
        m = banc("ressources")
        for acte, sujet in (("qui", ""), ("localisation", "brune"), ("ressource", "bois"), ("reclamer", "")):
            c = consultation_locale(acte, sujet)
            variantes = [(champ, valeur) for champ, valeur in (("attribut", "lieu"), ("valeur", "bois"),
                         ("sujet", 3), ("interlocuteur", "aubin"))]
            if acte in ("ressource", "localisation"):
                variantes += [("sujet", ""), ("sujet", "  ")]
            if acte == "qui":
                variantes.append(("sujet", "brune"))
            for champ, valeur in variantes:
                q = {**c, champ: valeur}
                with self.subTest(acte=acte, champ=champ, valeur=valeur):
                    p = {"personnage": "aubin", "replique": "Aubin, as-tu du bois ?",
                         "_intention": "Aubin, as-tu du bois ?", "contenu": [q]}
                    avant = copy.deepcopy(m.data)
                    self.assertFalse(self.conforme(q))
                    with self.assertRaises(ErreurMonde) as refus:
                        preparer_parole(m, p)
                    self.assertIn(champ, refus.exception.attendu)
                    self.assertEqual(recharger(m).data, avant)
        p = {"personnage": "brune", "replique": "Aubin, as-tu du bois ?", "_intention": "Aubin, as-tu du bois ?",
             "contenu": [consultation_locale("ressource", "bois")]}
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as refus:
            preparer_parole(m, p)
        self.assertIn("personnage = aubin", refus.exception.attendu)
        self.assertEqual(recharger(m).data, avant)

    def test_schema_effectivement_emis_et_sens_communs(self):
        from tests.test_cache_kv_local import PrefixeKVTests
        _, _, _, schema = PrefixeKVTests()._capter_appel(nouveau_monde(), "où est cette personne ?")
        parole = next(s for s in schema["properties"]["proposition"]["anyOf"] if "contenu" in s.get("properties", {}))
        variantes = parole["properties"]["contenu"]["items"]["anyOf"]
        for acte, contrat in CONSULTATIONS.items():
            variante = next(s for s in variantes if s["properties"]["type"]["enum"] == [acte])
            self.assertEqual(variante["description"], contrat["sens"])
            self.assertEqual(SENS_CONTENU[acte], contrat["sens"])
            self.assertEqual(CHAMPS_CONTENU[acte], contrat["champs"])
            self.assertTrue(self.conforme(consultation_locale(acte,
                "brune" if acte == "localisation" else "bois" if acte == "ressource" else "")))
        m = banc("ressources")
        c = consultation_locale("ressource", " CHALEUR ")
        verifier_contenus(m, [c])
        self.assertEqual(typer(m, c), {"type": "ressource", "besoin": "chaleur"})
        self.assertIn("combustible pour se chauffer", public(m, c))

    def test_consultation_laps_entier_ou_decoupe_avec_recharges(self):
        for script, mots in (("ressources", "Aubin, as-tu du bois ?"),
                              ("sous-obstacle-auberge", "As-tu une lampe ?")):
            with self.subTest(script=script), patch("donjon.agendas._naissances", return_value=None):
                m = banc(script)
                if script == "sous-obstacle-auberge":
                    m.joueur["orientation"] = "ouest"
                c = consultation_locale("ressource", "bois" if script == "ressources" else "lampe")
                m, _ = self.boucle(m, mots, c)
                a, _ = vivre(recharger(m), [1200])
                b, _ = vivre(recharger(m), [150] * 8)
                self.assertEqual(a.data, b.data)
                self.assertEqual((regarder(a), fiche(a), scene_percue(a)), (regarder(b), fiche(b), scene_percue(b)))
