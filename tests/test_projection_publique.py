"""A1 : couverture des sources A0 et chaîne moteur/rendus/sauvegarde, hors réseau."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer
from donjon.commandes import analyser
from donjon.mj import MJOpenAI
from donjon.monde import Monde
from donjon.moteur import Moteur
from donjon.projection_publique import (ProvenanceAbsente, projeter,
                                       verifier_couverture)
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.support import calme
from tools.oracle_g1 import empreinte

DATA = Path(__file__).parent / "data"


class EntreeCapturee(Exception):
    pass


def entree_actuelle(monde, message):
    """Arrête le vrai producteur avant le transport ; aucun modèle même simulé."""
    mj = MJOpenAI()
    def capturer(*_args, **_kwargs):
        raise EntreeCapturee

    # A6 branche désormais la projection avant _appeler. Ces oracles A1
    # continuent de contrôler le producteur brut, secrets témoins compris ;
    # test_raccord_libre contrôle ce qui arrive réellement au compilateur.
    with patch("donjon.projection_publique.projeter", wraps=projeter) as projection, \
         patch.object(mj, "_appeler", side_effect=capturer):
        try:
            mj._echanger(monde, message, None, True)
        except EntreeCapturee:
            return copy.deepcopy(projection.call_args.args[0])
    raise AssertionError("L'entrée actuelle n'a pas été produite")


def recharge(monde):
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        monde.sauver(chemin)
        return Monde.charger(chemin)


class ProjectionCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = json.loads((DATA / "oracle_g1.json").read_text(encoding="utf-8"))
        cls.corpus = json.loads(gzip.decompress((DATA / "projection_a1_entrees.json.gz").read_bytes()))

    def test_toutes_les_requetes_archivees_et_reprises_sont_couvertes(self):
        attendus = {c["id"] for c in self.oracle["cas"] if c["modele"]}
        sources = {s["path"]: s["sha256"] for s in self.oracle["sources"]
                   if s["campagne"] == "230e7b3"}
        self.assertEqual({e["id"] for e in self.corpus}, attendus)
        self.assertEqual(len(self.corpus), 36)
        self.assertEqual(len(attendus), 30)
        for e in self.corpus:
            with self.subTest(tour=e["id"], requete=e["requete"]):
                self.assertEqual(sources[e["source"]["path"]], e["source"]["sha256"])
                self.assertEqual(empreinte(e["entree"]), e["entree_sha256"])
                original = copy.deepcopy(e["entree"])
                projection = projeter(original)
                self.assertGreater(verifier_couverture(original, projection), 0)
                self.assertEqual(original, e["entree"])
                # Pas de tri ni de résumé ; même les erreurs de prose passées
                # restent dans leur historique, jamais devenues souvenirs.
                self.assertEqual(projection.entree["conversation"], original["conversation"])
                self.assertTrue(all(p["source"] for p in projection.provenances))

    def test_relais_4_texte_et_preuve_de_lecture_independants(self):
        e = next(e["entree"] for e in self.corpus if e["id"] == "relais/4")
        p = projeter(e)
        texte = e["faits"]["objet:gravure"]["inscription"]
        self.assertEqual(p.entree["faits"]["objet:gravure"]["inscription"], texte)
        self.assertTrue(any(texte in f for evenement in p.entree["faits"]["evenements_recents"]
                            for f in evenement["faits"]))
        for chemin in (("faits", "objet:gravure", "inscription"),
                       ("faits", "evenements_recents", 1, "faits", 0)):
            provenance = next(x for x in p.provenances if x["chemin"] == list(chemin))
            self.assertIn(provenance["nature"], ("perception_actuelle", "evenement_joueur"))
        self.assertTrue(any(x.get("tour") == 2 and x["nature"] == "evenement_joueur"
                            for x in p.provenances))

    def test_omission_exclusion_injustifiee_et_valeur_alteree_echouent(self):
        e = next(e["entree"] for e in self.corpus if e["id"] == "relais/4")
        for faute in ("omission", "exclusion", "valeur", "provenance"):
            with self.subTest(faute=faute):
                p = projeter(e)
                if faute == "omission":
                    p.provenances.pop()
                elif faute == "exclusion":
                    p.exclusions[0]["raison"] = "inutilisable ici"
                elif faute == "valeur":
                    p.entree["faits"]["objet:gravure"]["inscription"] = "autre texte"
                else:
                    p.provenances[0]["nature"] = ""
                with self.assertRaises(ValueError):
                    verifier_couverture(e, p)

    def test_champ_sans_contrat_refuse_plutot_qu_omis(self):
        e = copy.deepcopy(self.corpus[0]["entree"])
        e["faits"]["nouvelle_famille"] = {"secret": "inventé"}
        with self.assertRaises(ProvenanceAbsente):
            projeter(e)
        del e["faits"]["nouvelle_famille"]
        e["nouvelle_entree"] = "inventé"
        with self.assertRaises(ProvenanceAbsente):
            projeter(e)

    def test_la_filiation_d_une_part_ne_fait_pas_connaitre_son_lot(self):
        e = copy.deepcopy(self.corpus[0]["entree"])
        objet = next(k for k in e["faits"] if k.startswith("objet:"))
        e["faits"][objet]["lot_origine"] = "LOT_JAMAIS_PERCU"
        p = projeter(e)
        self.assertNotIn("LOT_JAMAIS_PERCU", json.dumps(p.publique()))
        self.assertNotIn("lot_origine", p.entree["faits"][objet])
        self.assertGreater(verifier_couverture(e, p), 0)

    def test_champ_nouveau_des_dossiers_mixtes_ne_devient_pas_public(self):
        for source, ref in (("interlocuteurs", "marchand"),
                            ("esprits_interlocuteurs", "marchand"),
                            ("souvenirs_personnages", "marchand"),
                            ("objet:marchand", None)):
            e = copy.deepcopy(next(e["entree"] for e in self.corpus if e["id"] == "crypte/23"))
            bloc = e["faits"][source] if ref is None else e["faits"][source][ref]
            bloc["nouvelle_propriete_auteur"] = "SECRET_SANS_CONTRAT"
            with self.subTest(source=source), self.assertRaises(ProvenanceAbsente):
                projeter(e)

    def test_marqueur_entrave_conserve_sans_ouvrir_les_champs_sans_contrat(self):
        for valeur in (True, False):
            e = copy.deepcopy(self.corpus[0]["entree"])
            objet = next(k for k in e["faits"] if k.startswith("objet:"))
            e["faits"][objet]["entrave"] = valeur
            p = projeter(e)
            self.assertIs(p.entree["faits"][objet]["entrave"], valeur)
            self.assertGreater(verifier_couverture(e, p), 0)
            chemin = ["faits", objet, "entrave"]
            preuve = next(v for v in p.provenances if v["chemin"] == chemin)
            self.assertEqual(preuve["destination"], chemin)
            # L'admission du marqueur moteur ne rend public aucun autre champ.
            e["faits"][objet]["capacite_non_portee"] = "SECRET_SANS_CONTRAT"
            with self.assertRaises(ProvenanceAbsente):
                projeter(e)

    def test_paroles_conservees_sans_croyances_ni_auditeurs_inconnus(self):
        e = copy.deepcopy(next(e["entree"] for e in self.corpus if e["id"] == "echanges/2"))
        p = projeter(e)
        self.assertTrue(e["faits"]["paroles_entendues"])
        self.assertEqual([x["texte"] for x in p.entree["faits"]["paroles_entendues"]],
                         [x["texte"] for x in e["faits"]["paroles_entendues"]])
        self.assertTrue(any(x["raison"].startswith("auditeur acoustique") for x in p.exclusions))
        for x in p.provenances:
            if x["chemin"][:2] == ["faits", "paroles_entendues"]:
                self.assertEqual(x["nature"], "parole_entendue")
        verifier_couverture(e, p)

    def test_date_de_vue_absente_non_inventee_depuis_revision_courante(self):
        e = next(e["entree"] for e in self.corpus if e["id"] == "relais/4")
        p = projeter(e)
        for x in p.provenances:
            if x["chemin"][:2] == ["faits", "souvenirs_visuels"]:
                self.assertFalse(x["date_observation_connue"])
                self.assertNotIn("minute", x)

    def test_lueur_anonyme_conserve_absence_d_identite(self):
        e = next(e["entree"] for e in self.corpus if e["id"] == "crypte/41")
        p = projeter(e)
        avant = e["faits"]["perception"]["contributions"]
        apres = p.entree["faits"]["perception"]["contributions"]
        anonymes = [i for i, c in enumerate(avant) if c.get("source", "absente") is None]
        self.assertTrue(anonymes)
        for i in anonymes:
            self.assertIn("source", apres[i])
            self.assertIsNone(apres[i]["source"])

    def test_source_non_connue_masquee_sans_perdre_effet_lumineux(self):
        e = copy.deepcopy(next(e["entree"] for e in self.corpus if e["id"] == "crypte/41"))
        c = next(c for c in e["faits"]["perception"]["contributions"] if c.get("source") is None)
        c["source"] = "source_jamais_percue"
        p = projeter(e)
        self.assertNotIn("source_jamais_percue", json.dumps(p.publique()))
        self.assertTrue(any(all(c[k] == nouveau[k] for k in c if k != "source")
                            for nouveau in p.entree["faits"]["perception"]["contributions"]))
        verifier_couverture(e, p)


class ProjectionMondeTests(unittest.TestCase):
    def rendu(self, m):
        return regarder(m), scene_percue(m)

    def assert_recharge(self, m, message):
        etat = copy.deepcopy(m.data)
        p = projeter(entree_actuelle(m, message))
        rendu = self.rendu(m)
        self.assertEqual(m.data, etat)
        r = recharge(m)
        self.assertEqual(r.data, etat)
        self.assertEqual(projeter(entree_actuelle(r, message)), p)
        self.assertEqual(self.rendu(r), rendu)
        self.assertEqual(r.data, etat)
        return r, p

    def test_support_reel_et_autre_support_connus_apres_recharge(self):
        for scenario, position in (("relais", [2, 3]), ("crypte", [4, 0])):
            with self.subTest(scenario=scenario):
                m = creer(scenario, 1985, "fixe")
                calme(m, *[i for i, o in m.objets.items() if o.get("profil")])
                m.joueur.update(salle="antichambre", position=position, orientation="est")
                # Le support du second scénario est sur la porte au nord.
                if scenario == "crypte":
                    m.joueur.update(position=[4, 1], orientation="nord")
                m = recharge(m)
                moteur = Moteur(m)
                resultat = moteur.executer(moteur.preparer(analyser(m, "examiner gravure")))
                texte = m.objets["gravure"]["inscription"]
                self.assertIn(texte, resultat)
                _, p = self.assert_recharge(m, "Que dit cette inscription exactement ?")
                self.assertEqual(p.entree["faits"]["objet:gravure"]["inscription"], texte)
                self.assertTrue(any(texte in f for e in p.entree["faits"]["evenements_recents"]
                                    for f in e["faits"]))

    def test_souvenir_date_sans_position_actuelle_ni_faux_souvenir(self):
        m = creer("relais", 1985, "fixe")
        calme(m, "marchand", "aubin", "brune", "ilse")
        m.joueur.update(salle="echoppe", position=[1, 2], orientation="nord")
        m.objets["marchand"].update(lieu="echoppe", position=[1, 1], orientation="sud")
        m.data["minutes"] = 17
        m.actualiser_souvenirs_personnages()
        self.assertTrue(m.visible("marchand"))
        m.joueur.update(salle="antichambre", position=[2, 3], orientation="est")
        # Le PNJ a bougé depuis la rencontre ; seule la mémoire est publique.
        m.objets["marchand"].update(lieu="chambre_cloche", position=[1, 1])
        m.data["minutes"] = 23
        m.memoriser("Je me rappelle une personne imaginaire.", "Tu aurais vu une personne imaginaire.")
        _, p = self.assert_recharge(m, "Qui ai-je rencontré ?")
        souvenirs = p.entree["faits"]["souvenirs_personnages"]
        souvenir = next(s for s in souvenirs.values() if s.get("minute") == 17)
        self.assertIn("source", souvenir)
        self.assertNotIn("position", souvenir)
        self.assertNotIn("lieu", souvenir)
        self.assertNotIn("personne imaginaire", json.dumps(souvenirs, ensure_ascii=False))
        self.assertTrue(any(x.get("minute") == 17 and x["nature"] == "souvenir"
                            for x in p.provenances))
        self.assertNotIn("objet:marchand", p.entree["faits"])

    def test_identite_privee_agenda_et_savoir_jamais_entendu_absents(self):
        m = creer("relais", 1985, "fixe")
        calme(m, "marchand", "aubin", "brune", "ilse")
        m.joueur.update(salle="antichambre", position=[2, 3], orientation="est")
        m.data["savoirs_pnj"]["brune"]["secret_test"] = {
            "texte": "SAVOIR_JAMAIS_ENTENDU", "origine": "jeu", "revision": m.data["revision"]}
        _, p = self.assert_recharge(m, "Que vois-je ?")
        texte = json.dumps(p.publique(), ensure_ascii=False)
        for interdit in ("SAVOIR_JAMAIS_ENTENDU", '"but_actuel"', '"besoins_pressants"',
                         '"croit"', '"objet:brune"'):
            self.assertNotIn(interdit, texte)
        for esprit in p.entree["faits"].get("esprits_interlocuteurs", {}).values():
            self.assertNotIn("valeurs", esprit)
        self.assertIn("personne_", texte)

    def test_dossier_prive_d_un_pnj_visible_jamais_transmis(self):
        m = creer("crypte", 1985, "fixe")
        m.joueur.update(salle="echoppe", position=[1, 2], orientation="nord")
        m.objets["marchand"].update(lieu="echoppe", position=[1, 1], orientation="sud")
        m.data["savoirs_pnj"]["marchand"]["secret_test"] = {
            "texte": "SAVOIR_PRIVE_DU_PNJ_VISIBLE", "origine": "jeu", "revision": m.data["revision"]}
        entree = entree_actuelle(m, "Que sais-tu ?")
        self.assertIn("SAVOIR_PRIVE_DU_PNJ_VISIBLE", json.dumps(entree))
        self.assertIn("croit", entree["faits"]["esprits_interlocuteurs"]["marchand"])
        _, p = self.assert_recharge(m, "Que sais-tu ?")
        self.assertNotIn("SAVOIR_PRIVE_DU_PNJ_VISIBLE", json.dumps(p.publique()))
        self.assertNotIn("connaissances_pnj", p.entree["faits"])
        self.assertTrue(any(x["raison"] == "état mental privé du PNJ" for x in p.exclusions))


if __name__ == "__main__":
    unittest.main()
