"""U-M information : choix web réels, même parole, U-C et sauvegarde."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import jeu

from donjon.commandes import DescripteurPublic
from donjon.dialogues import information_publique, parole_information, preparer_information
from donjon.emissions import pnj
from donjon.esprits import croire, croyance
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde, objet
from donjon.narration import consigner
from donjon.paroles import preparer_parole
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.voix import reel
from donjon.web.pont import PontWeb
from tests import test_corps_publics as support_corps
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests.test_parole_corrections import banc
from tests.test_tensions import recharger


def descripteur(qui, acte, **parametres):
    return DescripteurPublic({"geste": "information", "cible": qui,
                              "parametres": {"acte": acte, **parametres}})


class InformationPubliqueTests(unittest.TestCase):
    def boucle(self, m, entrees, mutation=None):
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "partie.json"
            m.sauver(fichier)
            saisies, lignes, etats = iter([*entrees, "quitter"]), [], []
            faux = MagicMock(connexion="api", erreur_auth=None)
            faux.echanger.side_effect = AssertionError("Appel au modèle")
            test = self

            class Pont(PontWeb):
                def rafraichir(self, monde, *args):
                    self.monde = monde
                    super().rafraichir(monde, *args)
                    etats.append(copy.deepcopy(monde.data))

                def lire(self, *_):
                    entree = next(saisies)
                    if mutation and entree == "tenter":
                        mutation(self.monde)
                    return entree

                def ecrire(self, *args, **kw):
                    super().ecrire(*args, **kw)
                    texte = " ".join(str(a) for a in args)
                    lignes.append(texte)
                    if hasattr(self, "monde") and self.monde.data.get("conversation"):
                        if texte.strip() == self.monde.data["conversation"][-1]["reponse"].strip():
                            # JSON représente toute séquence par une liste ; tous
                            # les champs restent comparés, sans exclusion d'état.
                            test.assertEqual(Monde.charger(fichier).data,
                                             json.loads(json.dumps(self.monde.data)))

            with (patch("jeu.MJ", return_value=faux),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", side_effect=AssertionError("Analyse du clic")),
                  patch.object(Monde, "d20", return_value=20)):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(fichier)], interface=Pont()), 0)
            faux.echanger.assert_not_called()
            faux.raconter_resultat.assert_not_called()
            recharge = Monde.charger(fichier)
            self.assertEqual(recharge.data, json.loads(json.dumps(etats[-1])))
            self.assertEqual(etat(recharge), etat(Monde(json.loads(json.dumps(etats[-1])))))
            return recharge, lignes, etats

    def clic(self, m, d):
        p = d.contenu["parametres"]
        public = etat(m)
        public["sonde_information"] = {"À qui parler": d.contenu["cible"],
            "Acte d'information": p["acte"], "Personne": p.get("sujet", ""),
            "Sujet": p.get("sujet", ""), "Lieu annoncé": p.get("valeur", ""),
            "Ressource recherchée": p.get("sujet", "")}
        sonde = page(m, public)["information"]
        self.assertEqual(sonde["envoye"], d.contenu)
        for cle in ("incomplet", "clavier", "occupe"):
            self.assertEqual(sonde[cle], 0)
        self.assertEqual(sonde["envois"], 1)
        self.assertTrue(sonde["ferme_apres_etat"])
        self.assertEqual(sonde["clics"], {"qui": 6, "ressource": 8, "localisation": 8, "affirmation": 10}[p["acte"]])
        print(json.dumps({"mesure": "information", "descripteur": d.contenu,
                          "saisies_evitees": 1, "clics_formulaire": sonde["clics"],
                          "clics_confirmation": int(p["acte"] == "affirmation")}, ensure_ascii=False))
        return DescripteurPublic(sonde["envoye"]), sonde["clics"]

    def parite(self, m, d, *, confirmer=True):
        from donjon.spatial import installer
        # La vraie boucle réinstalle aussi le mode cases à l'ouverture de la
        # sauvegarde : même mémoire perceptive initiale pour les deux voies.
        installer(m)
        clic, _ = self.clic(m, d)
        p = parole_information(m, d.contenu)
        # La saisie nomme exactement le même interlocuteur, sans interpolation
        # d'un nom ambigu. Le chemin texte de preparer_parole reste intact.
        texte = {**p, "_intention": f"je dis à {p['personnage']} : « {p['replique']} »"}
        with patch.object(Monde, "d20", return_value=20):
            attendu, rapport = preparer_parole(m, texte)
            with patch("donjon.paroles.analyser", side_effect=AssertionError("Analyse du clic")):
                dossier = preparer_information(m, clic)
        self.assertEqual(dossier.travail.data, attendu.data)
        self.assertEqual(dossier.rapports, [rapport])
        consigner(attendu, dossier.reponse)
        attendu = recharger(attendu)
        etat(attendu)  # Même rafraîchissement public que celui de la boucle.
        with patch("donjon.paroles.analyser", side_effect=AssertionError("Analyse du clic")):
            r, lignes, etats = self.boucle(m, [clic, "tenter"] if confirmer else [clic, "annuler"])
        if confirmer:
            self.assertEqual({k: v for k, v in r.data.items() if k != "conversation"},
                             {k: v for k, v in attendu.data.items() if k != "conversation"})
            recharge = recharger(r)
            self.assertEqual(recharge.data, r.data)
            self.assertEqual(pnj(recharge), pnj(attendu))
            self.assertEqual(scene_percue(recharge), scene_percue(attendu))
            self.assertEqual(fiche(recharge), fiche(attendu))
            self.assertEqual(regarder(recharge), regarder(attendu))
            self.assertIn(p["replique"], "\n".join(lignes))
            for emission in pnj(recharge):
                if emission['acte'] == 'reponse_information':
                    self.assertIn(emission['texte'], "\n".join(lignes))
        return r, lignes, etats

    def test_questions_ressources_reponses_et_recharge(self):
        for qui, sujet in (("aubin", "bois"), ("brune", "faim"), ("aubin", "chaleur")):
            with self.subTest(qui=qui, sujet=sujet):
                m = banc("ressources")
                avant = copy.deepcopy(m.objets)
                r, _, _ = self.parite(m, descripteur(qui, "ressource", sujet=sujet))
                self.assertEqual(r.objets, avant)
                self.assertTrue(pnj(r)[-1]["texte"].startswith("J'ai ") if qui == "aubin"
                                else pnj(r)[-1]["texte"] == "Je n'en ai pas.")

    def test_voix_se_nomme(self):
        m = banc("soir-noir")
        # Une voix déjà entendue est choisissable sans apparaître sur la carte.
        from donjon.paroles import entendre_repondant
        entendre_repondant(m, "ilse")
        qui = next(x["id"] for x in information_publique(m)["destinataires"] if reel(m, x["id"]) == "ilse")
        self.assertTrue(qui.startswith("voix_"))
        r, _, _ = self.parite(m, descripteur(qui, "qui"))
        self.assertEqual(pnj(r)[-1]["texte"], "Je m'appelle Ilse.")
        self.assertEqual(r.data['voix_entendues']['ilse']['se_dit'], 'ilse')

    def test_mefiance_et_autre_refus_de_nom(self):
        from tests.test_avis_menace import relation
        for acte in ("ressource", "qui"):
            with self.subTest(acte=acte):
                m = banc("ressources")
                relation(m, "aubin", "joueur", confiance=0)
                d = descripteur("aubin", acte, **({"sujet": "bois"} if acte == "ressource" else {}))
                r, _, _ = self.parite(m, d)
                self.assertEqual(pnj(r)[-1]["modalite"], "refus")

    def test_localisations_crues_fausses(self):
        for sujet, lieu_cru, lieu_reel in (("ilse", "crypte", "beffroi"), ("brune", "beffroi", "crypte")):
            with self.subTest(sujet=sujet):
                m = banc("noms-dialogue")
                m.objets[sujet]["lieu"] = lieu_reel
                placer(m.objets[sujet], lieu_reel, [3, 3])
                croire(m, "aubin", sujet, "lieu", lieu_cru, "vu", 1., salle=lieu_cru, case=None)
                m = recharger(m)
                r, _, _ = self.parite(m, descripteur("aubin", "localisation", sujet=sujet))
                c = croyance(r, "joueur", sujet, "lieu")
                self.assertEqual(c["valeur"], lieu_cru)
                self.assertNotEqual(c["source"], "vu")
                self.assertEqual(r.objets[sujet]["lieu"], lieu_reel)

    def test_annonce_lieu_connu_consentement_et_annulation(self):
        m = banc("ressources")
        d = descripteur("aubin", "affirmation", sujet="cloche", valeur="antichambre")
        self.assertTrue(preparer_information(m, d).confirmation)
        r, lignes, etats = self.parite(m, d)
        self.assertIn("Compris :", "\n".join(lignes))
        self.assertEqual(etats[1]["revision"], m.data["revision"])
        self.assertEqual(croyance(r, "aubin", "cloche", "lieu")["valeur"], "antichambre")
        self.assertNotEqual(croyance(r, "aubin", "cloche", "lieu")["source"], "vu")
        annule, _, _ = self.parite(m, d, confirmer=False)
        self.assertEqual({k: v for k, v in annule.data.items() if k != "conversation"},
                         {k: v for k, v in m.data.items() if k != "conversation"})

    def test_autre_scenario_et_homonymes(self):
        m, cible, autre = support_corps.monde_geste("saisir", 1)
        for qui in (cible, autre):
            with self.subTest(qui=qui):
                r, _, _ = self.parite(m, descripteur(qui, "qui"))
                self.assertEqual(pnj(r)[-1]["locuteur"], qui)
        for d in (descripteur(cible, "ressource", sujet="faim"),
                  descripteur(cible, "localisation", sujet=autre),
                  descripteur(cible, "affirmation", sujet="joueur", valeur="salle_commune")):
            with self.subTest(d=d):
                self.parite(m, d)

    def test_projection_sans_position_croyance_ni_secret(self):
        m = banc("ressources")
        avant = information_publique(m)
        m.objets["secret_354"] = objet("secret_354", "opale indicible", "tresor", "crypte")
        croire(m, "aubin", "secret_354", "lieu", "crypte", "vu")
        self.assertEqual(information_publique(m), avant)
        brut = json.dumps(avant)
        for terme in ("opale", "secret_354", "croyance", "position", "profil", "offres"):
            self.assertNotIn(terme, brut)
        for liste in avant.values():
            for entree in liste:
                self.assertEqual(set(entree), {"id", "nom"})

    def test_refus_reference_perimee_et_entree_forgee(self):
        m = banc("ressources")
        d = descripteur("aubin", "qui")
        self.clic(m, d)
        m.objets["aubin"]["lieu"] = "crypte"
        placer(m.objets["aubin"], "crypte", [3, 3])
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as exc:
            preparer_information(m, d)
        self.assertIn("perçois plus", str(exc.exception))
        self.assertTrue(exc.exception.attendu)
        self.assertEqual(m.data, avant)
        recharge, lignes, _ = self.boucle(m, [d])
        self.assertEqual(recharge.data["revision"], m.data["revision"])
        self.assertEqual(pnj(recharge), pnj(m))
        self.assertIn("perçois plus", "\n".join(lignes))
        for d in (descripteur("brune", "localisation", sujet="cloche"),
                  descripteur("brune", "affirmation", sujet="cloche", valeur="crypte"),
                  descripteur("brune", "ressource", sujet="secret_354"),
                  descripteur("brune", "qui", effet="donner")):
            with self.subTest(d=d), self.assertRaises(ErreurMonde) as exc:
                preparer_information(m, d)
            self.assertTrue(exc.exception.attendu)

    def test_adresse_interne_ne_permet_pas_de_changer_le_contenu(self):
        m = banc("ressources")
        d = descripteur("aubin", "qui")
        p = {**parole_information(m, d.contenu), "_adresse": d.contenu}
        p["contenu"] = [{"type": "nom", "sujet": "joueur", "attribut": "", "valeur": ""}]
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as exc:
            preparer_parole(m, p)
        self.assertTrue(exc.exception.attendu)
        self.assertEqual(m.data, avant)

    def test_ressource_reference_masquee_reste_publique_dans_le_recapitulatif(self):
        from donjon.noms import reference
        m = banc("ressources")
        m.objets["outil_interne_secret_354"] = objet(
            "outil_interne_secret_354", "outil connu", "outil", "marchand", proprietaire="marchand")
        m.data["connus"].append("outil_interne_secret_354")
        m = recharger(m)
        ref = reference(m, "outil_interne_secret_354")
        self.assertTrue(ref.startswith("element_"))
        r, lignes, _ = self.parite(m, descripteur("aubin", "ressource", sujet=ref))
        self.assertNotIn("outil_interne_secret_354", "\n".join(lignes))
        self.assertNotIn("outil_interne_secret_354", r.data["conversation"][-1]["reponse"])

    def test_recherche_lexicale_reste_stable_apres_apprentissage_du_bien(self):
        from donjon.comprehension import contenu
        m = banc("comptes")
        for sujet in ("bois", "planches"):
            with self.subTest(sujet=sujet):
                c = {"type": "ressource", "sujet": sujet}
                attendu = "demander si l'interlocuteur possède " + sujet
                self.assertEqual(contenu(m, c), attendu)
                if sujet not in m.data["connus"]:
                    m.data["connus"].append(sujet)
                m = recharger(m)
                self.assertEqual(contenu(m, c), attendu)

    def test_confirmation_revalide_adresse_et_aucune_parole_si_depart(self):
        m = banc("ressources")
        d = descripteur("aubin", "affirmation", sujet="cloche", valeur="antichambre")
        def depart(monde):
            monde.objets["aubin"]["lieu"] = "crypte"
            placer(monde.objets["aubin"], "crypte", [3, 3])
        r, lignes, _ = self.boucle(m, [d, "tenter"], mutation=depart)
        self.assertEqual(r.data["revision"], m.data["revision"])
        self.assertEqual(pnj(r), pnj(m))
        self.assertIn("perçois plus", "\n".join(lignes))


if __name__ == "__main__":
    unittest.main()
