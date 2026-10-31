"""U-M avis : choix web, parole typée, réception et recharge sans modèle."""
import copy
import json
import unittest
from unittest.mock import patch

from donjon import emissions, social
from donjon.commandes import DescripteurPublic
from donjon.dialogues import avis_publics, parole_information, preparer_direct
from donjon.esprits import croire, lire, prevision
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde
from donjon.narration import consigner
from donjon.paroles import preparer_parole
from donjon.rendu import fiche, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer
from donjon.temps import ecouler
from tests.test_avis_joueur import preparer
from tests.test_avis_menace import relation
from tests import test_information_publique as information_support
from tests.test_inventaire_public import etat
from tests.test_outils_publics import page
from tests.test_social import recharger


def choix(sujet="echoppe", valeur="oui", qui="marchand", **autres):
    return DescripteurPublic({"geste": "information", "cible": qui,
        "parametres": {"acte": "avis", "sujet": sujet, "valeur": valeur, **autres}})


class AvisPublicsTests(unittest.TestCase):
    # Le harnais de la vraie boucle vérifie aussi la sauvegarde avant affichage,
    # interdit analyse du clic et appels au modèle, puis compare l'état rechargé.
    boucle = information_support.InformationPubliqueTests.boucle

    def clic(self, m, d):
        public = etat(m)
        p = d.contenu["parametres"]
        public["sonde_avis"] = {"À qui parler": d.contenu["cible"],
            "Lieu de l'avis": p["sujet"], "Prévision": p["valeur"]}
        sonde = page(m, public)["avis"]
        self.assertEqual(sonde["envoye"], d.contenu)
        self.assertEqual(sonde["clics"], 8)
        for champ in ("incomplet", "clavier", "occupe"):
            self.assertEqual(sonde[champ], 0)
        self.assertEqual(sonde["envois"], 1)
        self.assertTrue(sonde["ferme_apres_etat"])
        for champ in sonde["champs"]:
            self.assertEqual(champ["choix"][0]["valeur"], "")
        return DescripteurPublic(sonde["envoye"])

    def parite(self, m, d):
        installer(m)
        direct = self.clic(m, d)
        p = parole_information(m, d.contenu)
        texte = {**p, "_intention": f"je dis à {p['personnage']} : « {p['replique']} »"}
        with patch.object(Monde, "d20", return_value=20):
            attendu, rapport = preparer_parole(m, texte)
            with patch("donjon.paroles.analyser", side_effect=AssertionError("Analyse du clic")):
                dossier = preparer_direct(m, direct)
        self.assertTrue(dossier.confirmation)
        self.assertEqual(dossier.travail.data, attendu.data)
        self.assertEqual(dossier.rapports, [rapport])
        consigner(attendu, dossier.reponse)
        attendu = recharger(attendu)
        etat(attendu)
        with patch("donjon.paroles.analyser", side_effect=AssertionError("Analyse du clic")):
            r, lignes, etats = self.boucle(m, [direct, "tenter"])
        self.assertEqual(etats[1]["revision"], m.data["revision"])
        self.assertEqual({k: v for k, v in r.data.items() if k != "conversation"},
                         {k: v for k, v in attendu.data.items() if k != "conversation"})
        self.assertIn("Compris :", "\n".join(lignes))
        self.assertIn(p["replique"], "\n".join(lignes))
        for parole in emissions.pnj(r):
            self.assertIn(parole["texte"], "\n".join(lignes))
        for duree in (13, 29, 18):
            # Le temps est partagé en laps, avec une recharge à chaque frontière.
            # Les deux voies doivent encore avoir le même monde et rendu public.
            ecouler(r, duree)
            ecouler(attendu, duree)
            r, attendu = recharger(r), recharger(attendu)
            self.assertEqual({k: v for k, v in r.data.items() if k != "conversation"},
                             {k: v for k, v in attendu.data.items() if k != "conversation"})
            self.assertEqual(scene_percue(r), scene_percue(attendu))
            self.assertEqual(fiche(r), fiche(attendu))
            self.assertEqual(regarder(r), regarder(attendu))
            self.assertEqual(emissions.lire(r), emissions.lire(attendu))
        return r

    def test_deux_lieux_valeurs_et_reception_apres_recharge(self):
        for salle, valeur in (("echoppe", "oui"), ("chambre_cloche", "non")):
            with self.subTest(salle=salle):
                m = preparer()
                crue = copy.deepcopy(m.data["crue"])
                r = self.parite(m, choix(salle, valeur))
                c = prevision(r, "marchand", salle)
                self.assertEqual(c["source"], "dit:joueur")
                self.assertEqual(c["valeur"], valeur == "oui")
                self.assertEqual(c["confiance"], .4)
                self.assertEqual(r.data["crue"], crue)
                self.assertIn("Je retiens ton avis : selon toi,", emissions.pnj(r)[-1]["texte"])

    def test_avis_contraire_meme_dispute_deux_lieux(self):
        for salle in ("echoppe", "chambre_cloche"):
            with self.subTest(salle=salle):
                m = preparer()
                croire(m, "marchand", salle, "prevision", [m.data["minutes"], -10000, 1], "vu", 1, rang=0)
                for qui in ("aubin", "ilse"):
                    relation(m, qui, "marchand", confiance=100, affection=100)
                    relation(m, qui, "joueur", confiance=1, affection=0)
                r = self.parite(m, choix(salle))
                self.assertTrue(any(c.get("dispute") for c in r.data["chronique"]))
                self.assertTrue(all(p["acte"] == "dispute" for p in emissions.pnj(r)))
                self.assertTrue(social.transmission_attestee(r, "joueur", "marchand",
                    {"type": "avis", "sujet": salle, "attribut": "menace", "valeur": True}))
                self.assertEqual(prevision(r, "ilse", salle)["source"], "dit:marchand")
                self.assertTrue(any(s["type"] == "dispute_perdue" for s in lire(r, "joueur")["memoire"]))

    def test_projection_connue_sans_prevision_ni_lieu_secret(self):
        m = preparer()
        m.data["visitees"].remove("crypte")
        m.data["connus"] = [id for id in m.data["connus"] if id != "crypte"]
        public = avis_publics(m)
        self.assertNotIn("crypte", [x["id"] for x in public["lieux"]])
        avant = copy.deepcopy(public)
        croire(m, "marchand", "crypte", "prevision", [m.data["minutes"], 10000, 1], "vu", 1, rang=0)
        self.assertEqual(avis_publics(m), avant)
        self.assertEqual(etat(m)["avis"], {**avant, "formulaires": etat(m)["avis"]["formulaires"]})
        for liste in public.values():
            for entree in liste:
                self.assertEqual(set(entree), {"id", "nom"})
        for mot in ("crypte", "prevision", "croyance", "position", "conviction"):
            self.assertNotIn(mot, json.dumps(public))
        self.assertRefus(m, choix("crypte"), "sujet")

    def assertRefus(self, m, d, champ):
        avant = copy.deepcopy(m.data)
        with self.assertRaises(ErreurMonde) as exc:
            preparer_direct(m, d)
        self.assertIn(champ, exc.exception.attendu)
        self.assertEqual(m.data, avant)

    def test_refus_forgeries_et_adresse_alteree_atomiques(self):
        m = preparer()
        for d, champ in ((choix("lieu_inconnu"), "sujet"), (choix(valeur="peut-être"), "valeur"),
                         (choix(effet="inonder"), "parametres"), (choix(qui="absent"), "cible")):
            with self.subTest(d=d):
                self.assertRefus(m, d, champ)
        d = choix()
        p = {**parole_information(m, d.contenu), "_adresse": d.contenu}
        p["contenu"][0]["valeur"] = "non"
        with self.assertRaises(ErreurMonde) as exc:
            preparer_parole(m, p)
        self.assertTrue(exc.exception.attendu)

    def test_annulation_et_depart_a_confirmation_sans_parole(self):
        m = preparer()
        r, _, _ = self.boucle(m, [self.clic(m, choix()), "annuler"])
        self.assertEqual(r.data["revision"], m.data["revision"])
        self.assertEqual(emissions.lire(r), emissions.lire(m))
        self.assertEqual(prevision(r, "marchand", "echoppe"), prevision(m, "marchand", "echoppe"))
        def depart(monde):
            monde.objets["marchand"]["lieu"] = "crypte"
            placer(monde.objets["marchand"], "crypte", [3, 3])
        r, lignes, _ = self.boucle(m, [choix(), "tenter"], mutation=depart)
        self.assertEqual(r.data["revision"], m.data["revision"])
        self.assertEqual(emissions.lire(r), emissions.lire(m))
        self.assertIn("perçois plus", "\n".join(lignes))


if __name__ == "__main__":
    unittest.main()
