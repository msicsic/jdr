"""3b : preuves dans le monde, mémoires et rendus après sauvegarde/reprise."""
import copy
import unittest
from unittest.mock import patch

from donjon import relations as R
from donjon.banc_pnj import creer
from donjon.caractere import modificateur
from donjon.echanges import accueil, demander, remettre, executer as _echanger
from donjon.esprits import lire, memoriser, percevoir_tous
from donjon.monde import Monde, ErreurMonde, nouveau_monde
from donjon.moteur import Moteur, proposition
from donjon.paroles import jet_persuasion, esprits_interlocuteurs
from donjon.pnj import commencer_geste, _etape, se_parler
from donjon.recit_pnj import Recit
from donjon.rejeu import Enregistreur, page
from donjon.temps import instant
from tests.support import calme, regarder, lier
from tests.test_social import recharger, placer, relais


def reunir(m, *ids):
    from donjon.geometrie import cases
    destinations = [(2 + n, 5) for n in range(len(ids))]
    pris = {tuple(o["position"]) for x, o in m.objets.items() if o["type"] == "personnage" and o["lieu"] == "antichambre" and x not in ids}
    pris.add(tuple(m.joueur["position"]) if m.joueur["salle"] == "antichambre" else (-1, -1))
    for x, o in m.objets.items():
        if o["type"] == "personnage" and x not in ids and o["lieu"] == "antichambre" and tuple(o["position"]) in destinations:
            libre = next(c for c in sorted(cases(m.data["salles"]["antichambre"])) if c not in pris and c not in destinations)
            placer(m, x, "antichambre", libre)
            pris.add(libre)
    for n, id in enumerate(ids):
        placer(m, id, "antichambre", destinations[n])
        regarder(m, id, destinations[1 if n == 0 else 0] if len(ids) > 1 else [3, 5])
    return m


def motifs(m, id, autre):
    return [x["type"] for x in R.envers(m, id, autre)["motifs"]]


class ChainesTests(unittest.TestCase):
    def test_brune_donne_du_bois_puis_previent_gorm(self):
        m = calme(creer("crue", 7, "fixe"), "brune", "marchand", "aubin", "ilse")
        placer(m, "marchand", "crypte", [5, 3])
        reunir(m, "brune", "aubin")
        m.objets["brune"]["profil"]["protege"] = ["marchand"]
        m.objets["cloche"].update(proprietaire="marchand", lieu="antichambre", position=[6, 1], position_salle="antichambre")
        percevoir_tous(m)
        commencer_geste(m, "aubin", "prendre", "cloche", instant(m) + 600)
        self.assertTrue(any(x["type"] == "a_prevenir" for x in lire(m, "brune")["memoire"]))
        reunir(m, "brune", "marchand")
        m.objets["bois"].update(lieu="brune", proprietaire="brune")
        remettre(m, "brune", "marchand", "bois")
        m = recharger(m)
        self.assertEqual(R.envers(m, "marchand", "brune")["confiance"], 40)
        self.assertIsNone(accueil(m, "brune", "marchand"))
        etape = {**_etape("dire", "marchand"), "contenu": {"sujet": "aubin", "attribut": R.FIABLE, "valeur": False}}
        with patch.object(Monde, "d20", return_value=20):
            self.assertTrue(_echanger(m, "brune", etape, []))
        m = recharger(m)
        r = R.envers(m, "marchand", "brune")
        self.assertEqual(r["confiance"], 55)
        self.assertEqual(motifs(m, "marchand", "brune"), ["service_rendu", "prevenu"])
        self.assertIsNone(accueil(m, "brune", "marchand"))
        m.objets["marteau"].update(lieu="marchand", proprietaire="marchand")
        m.objets["marteau"].pop("position", None)
        with patch.object(Monde, "d20", return_value=1) as de:
            self.assertEqual(demander(m, "brune", "marchand", "marteau"), "refus")
            self.assertTrue(de.called)
        texte = Recit(m).texte(m, m.data.get("chronique", []))
        self.assertIn("prevenu", texte)
        self.assertIn("service_rendu", texte)

    def test_autre_service_leve_une_mefiance_sans_effacer_son_motif(self):
        m = reunir(calme(relais(), "brune", "marchand", "aubin", "ilse"), "ilse", "aubin")
        lier(m, "ilse", "aubin", False)
        for cause in ("engagement_tenu", "prevenu"):
            memoriser(m, "ilse", {"type": cause, "de": "aubin", "condition": {"objet": "brasero", "allume": True}})
        m = recharger(m)
        self.assertEqual(R.envers(m, "ilse", "aubin")["confiance"], 45)
        self.assertFalse(R.se_mefie(m, "ilse", "aubin"))
        self.assertNotIn("croit que Aubin est peu fiable", esprits_interlocuteurs(m, ["ilse"])["ilse"]["croit"])
        self.assertIn("prevenu", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_odon_refuse_par_mathe_et_vu_manger_le_pain_de_lucien(self):
        m = creer("mine", 7, "fixe")
        from donjon.deliberation import retenir_refus
        avant = R.envers(m, "odon", "mathe")["rancune"]
        retenir_refus(m, "odon", "mathe", "demander", "mefiance", objet="pain")
        # Le moteur des témoins est la même porte que pour les autres gestes illicites.
        pain = next(x for x, o in m.objets.items() if o["type"] == "nourriture" and o.get("proprietaire") == "lucien")
        salle = m.objets["mathe"]["lieu"]
        placer(m, "odon", salle, [3, 2])
        placer(m, "mathe", salle, [4, 2])
        regarder(m, "mathe", "odon")
        commencer_geste(m, "odon", "manger", pain, instant(m) + 600)
        m = recharger(m)
        self.assertGreater(R.envers(m, "odon", "mathe")["rancune"], avant)
        self.assertIn("refus", motifs(m, "odon", "mathe"))
        self.assertTrue(R.se_mefie(m, "mathe", "odon"))
        self.assertIn("tort_tiers", motifs(m, "mathe", "odon"))
        texte = Recit(m).texte(m, m.data.get("chronique", []))
        self.assertIn("refus", texte)
        self.assertIn("tort_tiers", texte)

    def test_refus_d_un_autre_personnage_garde_un_motif(self):
        m = reunir(relais(), "brune", "marchand")
        from donjon.deliberation import retenir_refus
        retenir_refus(m, "brune", "marchand", "demander", "refus", objet="vivres")
        m = recharger(m)
        self.assertGreater(R.envers(m, "brune", "marchand")["rancune"], 0)
        self.assertIn("refus", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_joueur_surpris_puis_don_sans_retablir_les_ventes(self):
        for cible in ("crochets", "marteau"):
            with self.subTest(cible=cible):
                m = nouveau_monde()
                m.joueur["salle"] = "echoppe"
                moteur = Moteur(m)
                with patch.object(Monde, "d20", return_value=1):
                    texte = moteur.executer(moteur.preparer(proposition("voler", cible)))
                avant = R.envers(m, "marchand", "joueur")["confiance"]
                # L'objet dérobé ou repris est rendu comme don, par le vrai geste du joueur.
                m.objets[cible].update(lieu="joueur", proprietaire="marchand", en_vente=False)
                m.objets[cible].pop("position", None)
                moteur = Moteur(m)
                texte += moteur.executer(moteur.preparer(proposition("remettre", cible, "marchand")))
                m = recharger(m)
                self.assertGreater(R.envers(m, "marchand", "joueur")["confiance"], avant)
                self.assertEqual(motifs(m, "marchand", "joueur"), ["vol_surpris", "service_rendu"])
                self.assertEqual(m.data["relations_pnj"]["marchand"]["vols_surpris"], 1)
                self.assertIn("Tu donnes", texte)
                self.assertIn("te surprend", texte)
                with self.assertRaisesRegex(ErreurMonde, "refuse"):
                    Moteur(m).preparer(proposition("acheter", "marteau" if cible == "crochets" else "crochets"))


class TempsEtContratsTests(unittest.TestCase):
    def test_liens_axes_et_avis_hors_croyances(self):
        for scenario in ("relais", "mine", "auberge", "crue"):
            m = recharger(creer(scenario, 7, "fixe"))
            self.assertNotIn("joueur", m.data["esprits"])
            for id in m.data["esprits"]:
                self.assertTrue(all(R.FIABLE not in a for a in lire(m, id)["croyances"].values()))
            self.assertIn("Ce qu'ils pensent", Recit(m).texte(m, []))

    def test_lecture_pure_et_estompement_independant_des_autres_axes(self):
        for cible in ("brune", "aubin"):
            m = relais()
            r = R._nouvelle({"confiance": 20, "affection": 70, "rancune": 80, "peur": 80})
            lire(m, "ilse")["relations"][cible] = r
            direct = m.copier()
            for minute in range(1, 61):
                m.data["minutes"] = minute
                memoriser(m, "ilse", {"type": "mensonge_dementi", "locuteur": cible})
                m = recharger(m)
                avant = copy.deepcopy(m.data)
                R.envers(m, "ilse", cible)
                self.assertEqual(m.data, avant)
            direct.data["minutes"] = 60
            for axe in ("affection", "rancune", "peur"):
                self.assertEqual(R.envers(m, "ilse", cible)[axe], R.envers(direct, "ilse", cible)[axe])
            self.assertIn("mensonge_dementi", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_hysteresis_persiste_a_la_reprise(self):
        m = reunir(relais(), "ilse", "aubin")
        lier(m, "ilse", "aubin", False)
        for n in range(3):
            m.data["minutes"] = n + 1
            memoriser(m, "ilse", {"type": "prevenu", "de": "aubin"})
            m = recharger(m)
            self.assertEqual(R.se_mefie(m, "ilse", "aubin"), n == 0)
        self.assertTrue(R.se_fie(m, "ilse", "aubin"))
        memoriser(m, "ilse", {"type": "mensonge_dementi", "locuteur": "aubin"})
        self.assertTrue(R.se_fie(recharger(m), "ilse", "aubin"))
        self.assertIn("prevenu", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_voix_inconnue_ne_prend_pas_la_relation_de_l_identite(self):
        # Les cas complets de voix du dépôt couvrent l'imposture et le nom prétendu.
        m = relais()
        from donjon.voix import retenir
        lire(m, "marchand")["voix"] = []
        placer(m, "brune", "crypte", [4, 3])
        retenir(m, "marchand", "brune")["se_dit"] = "ilse"
        self.assertEqual(R.percue(recharger(m), "marchand", "brune")["confiance"], 40)
        self.assertEqual(R.envers(m, "marchand", "ilse")["confiance"], 65)

    def test_rejeu_relations_et_motifs_dans_le_temps(self):
        m = reunir(relais(), "ilse", "aubin")
        enregistreur = Enregistreur(m)
        m.data["minutes"] = 1
        memoriser(m, "ilse", {"type": "prevenu", "de": "aubin"})
        m = recharger(m)
        enregistreur._noter(m)
        donnees = enregistreur.donnees(m, m.data.get("chronique", []))
        piste = [d["ilse|:relations"]["aubin"] for _, d in donnees["esprits"] if "ilse|:relations" in d]
        self.assertEqual([r["confiance"] for r in piste], [65, 80])
        self.assertEqual(piste[-1]["motifs"][-1]["type"], "prevenu")
        self.assertIn(":relations", page(donnees))

    def test_meme_preuve_rapportee_apres_oubli_n_est_pas_une_seconde_faute(self):
        for temoin, auteur, objet in (("marchand", "brune", "vivres"), ("aubin", "ilse", "planches")):
            m = relais()
            fait = {"type": "vu_agir", "auteur": auteur, "operation": "prendre", "objet": objet,
                    "victime": temoin, "preuve": "incident-unique"}
            memoriser(m, temoin, fait)
            confiance = R.envers(m, temoin, auteur)["confiance"]
            for n in range(45):
                memoriser(m, temoin, {"type": "bruit", "salle": "antichambre", "nature": "pas", "niveau": 3, "n": n})
            m = recharger(m)
            memoriser(m, temoin, {"type": "rumeur", "de": "ilse" if temoin == "marchand" else "marchand",
                                 "rang": 1, "evenement": fait})
            self.assertEqual(R.envers(recharger(m), temoin, auteur)["confiance"], confiance)
            self.assertIn("vu_agir", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_une_preuve_vue_complete_la_rumeur_ou_l_attribution_entendue(self):
        for temoin, auteur, objet in (("marchand", "brune", "vivres"), ("aubin", "ilse", "planches")):
            for par in ("rumeur", "ouie"):
                with self.subTest(temoin=temoin, par=par):
                    m = relais()
                    fait = {"type": "vu_agir", "auteur": auteur, "operation": "prendre", "objet": objet,
                            "victime": temoin, "preuve": "geste-en-cours"}
                    if par == "rumeur":
                        memoriser(m, temoin, {"type": "rumeur", "de": "ilse" if temoin == "marchand" else "marchand",
                                             "rang": 1, "evenement": fait})
                    else:
                        memoriser(m, temoin, {**fait, "par": "ouie"})
                    avant = R.envers(m, temoin, auteur)["confiance"]
                    m = recharger(m)
                    memoriser(m, temoin, fait)
                    m = recharger(m)
                    self.assertEqual(R.envers(m, temoin, auteur)["confiance"], 25)
                    self.assertLess(25, avant)
                    self.assertTrue(R.se_mefie(m, temoin, auteur))
                    self.assertIn("vu_agir", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_le_crochet_complete_une_preuve_renforcee_mais_le_circuit_social_bloque_la_redite(self):
        from donjon.social import recevoir
        for temoin, auteur, source in (("marchand", "brune", "ilse"), ("aubin", "ilse", "marchand")):
            m = relais()
            fait = {"type": "vol_surpris", "auteur": auteur, "objet": "marteau", "preuve": "meme-fait"}
            lier(m, temoin, source, True)
            # Première source seulement neutre, puis une source devenue pleinement sûre.
            lire(m, temoin)["relations"][source]["confiance"] = 40
            memoriser(m, temoin, {"type": "rumeur", "de": source, "rang": 1, "evenement": fait})
            self.assertEqual(R.envers(m, temoin, auteur)["confiance"], 57)
            m = recharger(m)
            lire(m, temoin)["relations"][source]["confiance"] = 100
            # Limite actuelle du circuit réel : une nouvelle déjà sue n'est pas
            # réévaluée. Le complément ci-dessous garantit seulement le contrat du crochet.
            self.assertIsNone(recevoir(m, temoin, source, {"type": "rumeur", "rang": 1, "evenement": fait}))
            m = recharger(m)
            self.assertEqual(R.envers(m, temoin, auteur)["confiance"], 57)
            memoriser(m, temoin, {"type": "rumeur", "de": source, "rang": 1, "evenement": fait})
            m = recharger(m)
            self.assertEqual(R.envers(m, temoin, auteur)["confiance"], 45)
            self.assertIn("rumeur", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_une_restitution_n_est_pas_un_don_et_seul_l_auteur_est_credite(self):
        from donjon.biens import preter
        from donjon.deplacement_objet import deplacer
        for emprunteur in ("brune", "ilse"):
            m = reunir(relais(), "marchand", emprunteur)
            m.objets["marteau"].update(lieu="marchand", proprietaire="marchand")
            m.objets["marteau"].pop("position", None)
            preter(m, "marteau", emprunteur)
            deplacer(m, "marteau", emprunteur)
            remettre(m, emprunteur, "marchand", "marteau")
            m = recharger(m)
            r = R.envers(m, "marchand", emprunteur)
            self.assertEqual((r["confiance"], r["dette"]), (80, 0))
            self.assertEqual(motifs(m, "marchand", emprunteur), ["pret_rendu"])
            self.assertIn("pret_rendu", Recit(m).texte(m, m.data.get("chronique", [])))
            # Reprendre soi-même son bien clôt le prêt, sans donner une preuve de parole tenue.
            autre = reunir(relais(), "marchand", emprunteur)
            autre.objets["marteau"].update(lieu=emprunteur, proprietaire="marchand")
            preter(autre, "marteau", emprunteur)
            deplacer(autre, "marteau", "marchand")
            self.assertEqual(R.envers(recharger(autre), "marchand", emprunteur)["confiance"], 65)

    def test_modulations_par_les_valeurs_apres_reprise(self):
        for id, autre in (("ilse", "aubin"), ("brune", "marchand")):
            resultats = []
            for v in (20, 80):
                m = reunir(relais(), id, autre)
                m.objets[id]["profil"]["valeurs"].update(fierte=v, loyaute=v, empathie=v, courage=v)
                memoriser(m, id, {"type": "pousse", "auteur": autre})
                m.data["minutes"] += 1
                memoriser(m, id, {"type": "nourri", "de": autre, "objet": "vivres"})
                m = recharger(m)
                r = R.envers(m, id, autre)
                resultats.append(r)
                self.assertIn("service_rendu", Recit(m).texte(m, m.data.get("chronique", [])))
            bas, haut = resultats
            self.assertGreater(haut["rancune"], bas["rancune"])
            self.assertGreater(haut["dette"], bas["dette"])
            self.assertGreater(haut["affection"], bas["affection"])
            self.assertLess(haut["peur"], bas["peur"])

    def test_persuasion_lit_les_axes_et_la_volonte(self):
        for id, autre in (("ilse", "aubin"), ("brune", "marchand")):
            m = reunir(relais(), id, autre)
            memoriser(m, id, {"type": "nourri", "de": autre, "objet": "vivres"})
            m = recharger(m)
            r = R.envers(m, id, autre)
            with patch.object(Monde, "d20", return_value=10):
                _, dd = jet_persuasion(m, id, autre, 12)
            self.assertEqual(dd, 12 + (50 - r["confiance"]) / 10 - r["affection"] / 25
                             - r["dette"] / 20 + r["rancune"] / 20 + modificateur(m, id, "VOL"))
            self.assertIn("service_rendu", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_dette_soldee_une_fois_par_demande_acceptee(self):
        for id, autre in (("marchand", "brune"), ("aubin", "ilse")):
            m = reunir(relais(), id, autre)
            r = lire(m, id)["relations"][autre]
            r["dette"] = 40
            m.objets[id]["profil"]["pulsions"] = []
            lire(m, id)["pulsions"] = []
            m.objets["vivres"].update(lieu=id, proprietaire=id)
            lire(m, id)["intention"] = None
            with patch.object(Monde, "d20", return_value=20):
                demander(m, autre, id, "vivres")
            m = recharger(m)
            self.assertEqual(R.doit(m, id, autre), 20)
            self.assertEqual(motifs(m, id, autre).count("dette_honoree"), 1)
            self.assertIn("dette_honoree", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_engagement_lointain_appris_quand_on_se_parle(self):
        for id, autre in (("marchand", "brune"), ("aubin", "ilse")):
            m = relais()
            placer(m, id, "crypte", [5, 3])
            placer(m, autre, "antichambre", [2, 5])
            memoriser(m, id, {"type": "engagement_tenu", "pour": autre,
                             "condition": {"objet": "brasero", "allume": True}})
            self.assertEqual(R.envers(m, autre, id)["confiance"], 65)
            m = recharger(m)
            reunir(m, id, autre)
            self.assertTrue(se_parler(m, id, autre))
            from donjon.social import faire_entendre
            lignes = []
            m.joueur.update(salle="antichambre", position=[2, 4])
            regarder(m, "joueur", id)
            faire_entendre(m, id, autre, "Une parole.", [], lignes)
            self.assertTrue(any("tenu sa parole" in l for l in lignes), lignes)
            m = recharger(m)
            self.assertEqual(R.envers(m, autre, id)["confiance"], 80)
            self.assertEqual(lire(m, id)["suites"], [])
            self.assertIn("tenu sa parole", " ".join(b.get("texte", "") for b in m.data.get("bruits", [])))

    def test_voir_un_abandon_intime_n_apprend_rien(self):
        for id, autre in (("marchand", "brune"), ("aubin", "ilse")):
            m = reunir(relais(), id, autre)
            memoriser(m, id, {"type": "engagement_abandonne", "pour": autre,
                             "condition": {"objet": "brasero", "allume": True}})
            m = recharger(m)
            self.assertEqual(R.envers(m, autre, id)["confiance"], 65)
            self.assertNotIn("engagement_abandonne", motifs(m, autre, id))
            self.assertNotIn("peu fiable", " ".join(esprits_interlocuteurs(m, [autre])[autre]["croit"]))

    def test_compagnie_dans_l_epreuve_gardee_apres_reprise(self):
        for id, autre in (("ilse", "aubin"), ("brune", "marchand")):
            m = reunir(relais(), id, autre)
            lire(m, id)["besoins"]["faim"] = 90
            lire(m, autre)["besoins"]["faim"] = 90
            percevoir_tous(m)
            with patch("donjon.corps.au_chaud", return_value=True):
                for minute in range(1, 61):
                    m.data["minutes"] = minute
                    R.partager(m, id, minute)
                    # La même minute consultée deux fois ne vaut qu'une minute vécue.
                    R.partager(m, id, minute)
                    if minute == 30:
                        m = recharger(m)
            m = recharger(m)
            self.assertEqual(R.envers(m, id, autre)["confiance"], 68)
            self.assertEqual(motifs(m, id, autre), ["epreuve_partagee"])
            self.assertIn("epreuve_partagee", Recit(m).texte(m, m.data.get("chronique", [])))

    def test_le_joueur_est_aussi_un_compagnon_percu_dans_l_epreuve(self):
        for id in ("ilse", "aubin"):
            m = reunir(relais(), id)
            m.joueur.update(salle="antichambre", position=[4, 5])
            regarder(m, id, "joueur")
            m.joueur["besoins"]["faim"] = 90
            lire(m, id)["besoins"]["faim"] = 90
            percevoir_tous(m)
            with patch("donjon.corps.au_chaud", return_value=True):
                for minute in range(1, 61):
                    m.data["minutes"] = minute
                    R.partager(m, id, minute)
                    if minute == 30:
                        m = recharger(m)
            m = recharger(m)
            self.assertEqual(R.envers(m, id, "joueur")["confiance"], 43)
            self.assertEqual(motifs(m, id, "joueur"), ["epreuve_partagee"])
            self.assertIn("epreuve_partagee", Recit(m).texte(m, m.data.get("chronique", [])))


if __name__ == "__main__":
    unittest.main()
