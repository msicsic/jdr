"""La revue juge le sens ; adresse et validation restent au moteur, jusqu'à la recharge."""
import copy
import unittest

from donjon.biens import compte
from donjon.matiere import id_piece
from donjon.rendu import fiche
from donjon.spatial import porte_par
from tests.support import presentes
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_comptes_issue import audit
from tests.test_parole_corrections import banc
from tests.test_parts_achetees import antichambre_du_banc
from tests.test_propositions import scene
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import recharger, vivre


def revue(perimetre, *operations, conforme=False):
    return {"contenu_conforme": conforme, "perimetre": perimetre,
            "motif": "Objection dans le domaine déclaré.", "operations_demandees": list(operations)}


class FideliteAudienceTests(unittest.TestCase):
    def test_operations_evaluees_separement_pour_une_question_ordinaire(self):
        for saisie, qui in (("Ilse, tu m'entends ?", "ilse"),
                           ("Aubin, tu tiens le coup ?", "aubin")):
            with self.subTest(saisie=saisie):
                m = banc("noms-dialogue")
                r, sortie, appels = jouer(m, saisie, [
                    parole(saisie, ("propos", "", "", ""), personnage=qui),
                    dialogue("Ta question est entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))])
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 0)
                self.assertEqual(len(r.data["paroles_joueur"]), 1)
                self.assertEqual(r.data["paroles_joueur"][-1]["texte"], saisie)
                self.assertEqual(r.data["paroles_joueur"][-1]["auditeur"], qui)
                self.assertIn(saisie, sortie)
                self.assertEqual(r.joueur["or"], m.joueur["or"])
                self.assertIn("Ta question est entendue.", str(recharger(r).data["conversation"]))

    def test_adresse_ne_refuse_pas_le_contenu_des_le_premier_essai(self):
        autre = banc("sous-obstacle-auberge")
        autre.joueur["orientation"] = "ouest"
        from donjon.paroles import prevue
        from donjon.voix import reel
        for m, saisie, bien in (
            (banc("noms-dialogue"), "est-ce que quelqu'un a du bois ?", "bois"),
            (autre, "Avez-vous de quoi manger ?", "faim"),
        ):
            with self.subTest(saisie=saisie):
                m = recharger(m)
                cible = prevue(m, saisie)["personnage"]
                r, sortie, appels = jouer(m, saisie, [
                    parole(saisie, ("ressource", bien, "", ""), personnage=cible),
                    dialogue("Ta question est entendue.")],
                    [rapport(ligne("mecanique", sources=["conversation_validee"]))],
                    revues=[revue("adresse", "ressource")])
                self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
                self.assertFalse(any("retour_moteur" in e.get("faits", {}) for _, e in appels))
                self.assertEqual(r.data["paroles_joueur"][-1]["auditeur"], reel(r, cible))
                self.assertEqual(r.data["paroles_joueur"][-1]["texte"], saisie)
                self.assertEqual(r.joueur["or"], m.joueur["or"])
                self.assertIn(saisie, sortie)
                self.assertIn("Ta question est entendue.", str(r.data["conversation"]))

    def test_formes_validees_du_marche_sans_refus_prealable(self):
        bois = presentes(antichambre_du_banc(), "aubin")
        soupe = scene("aubin")
        soupe.objets["vivres"].update(nom="soupe", aliases=["soupe"], prix_part=2)
        for origine, lot, prix in ((bois, "planches", 3), (soupe, "vivres", 2)):
            for proposition in (False, True):
                if lot == "vivres" and not proposition:
                    # La demande historique de repas est un service consommé,
                    # pas une remise ; le marché explicite porte la part.
                    continue
                with self.subTest(lot=lot, proposition=proposition):
                    m = recharger(copy.deepcopy(origine))
                    saisie = ("je paie Aubin trois pièces pour une de ses planches" if lot == "planches"
                              else "je t'offre deux pièces pour une part de soupe")
                    p = parole(saisie, ("demande", lot, "", str(prix)), personnage="aubin")
                    if proposition:
                        p["proposition"]["contenu"] = [{"type": "proposition",
                            "demande": {"type": "part", "objet": lot},
                            "contrepartie": {"type": "pieces", "montant": prix}}]
                    piece = id_piece(m, lot)
                    # Le lot posé est livré au prochain pas ; les vivres portés immédiatement.
                    comptes = [compte("joueur", "aubin", montant=prix, etat="rendu"),
                               compte("aubin", "joueur", piece, 1,
                                      etat="du" if lot == "planches" else "rendu")]
                    texte = "Entendu."
                    r, sortie, appels = jouer(m, saisie, [p, dialogue(f"« {texte} »")],
                        [audit(texte, comptes, "aubin")],
                        revues=[revue("validation_moteur", "proposition")])
                    self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
                    self.assertEqual(r.joueur["or"], m.joueur["or"] - prix)
                    self.assertEqual(len(r.data["paroles_joueur"]), 1)
                    self.assertIn(texte, sortie)
                    sens = next(e["plan"]["parole"]["sens_contenu"][0]
                                for f, e in appels if f == "auditer_action")
                    self.assertIn("proposition", sens["operations"])
                    if not proposition:
                        self.assertEqual(sens["prix_offert"], prix)
                    r, _ = vivre(r, 3)
                    r = recharger(r)
                    self.assertTrue(porte_par(r, piece, "joueur"))
                    self.assertIn(r.objets[piece]["nom"], fiche(r))
                    self.assertEqual(r.objets[piece]["proprietaire"], "joueur")

    def test_question_de_dette_ne_rejuge_pas_le_reglement(self):
        for qui in ("aubin", "marchand"):
            m = presentes(banc("soir-appel" if qui == "aubin" else "comptes"), qui)
            nom = m.objets[qui]["nom"].split(",")[0]
            saisie = f"{nom}, tu me dois quelque chose ?"
            texte = "Entendu."
            # Chaque débiteur a bien une dette et un nom connu dans sa scène.
            r, sortie, appels = jouer(m, saisie, [
                parole(saisie, ("reclamer", "", "", ""), personnage=qui), dialogue(f"« {texte} »")],
                [audit(texte, [compte(qui, "joueur", montant=2, etat="rendu")], qui)],
                revues=[revue("validation_moteur", "reclamer")])
            self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
            self.assertEqual(r.joueur["or"], m.joueur["or"] + 2)
            self.assertIn(texte, sortie)

    def test_ecarts_de_sens_restent_refuses_sans_perdre_la_couverture(self):
        for faux_mots in (True, False):
            m = banc("noms-dialogue")
            saisie = "est-ce que quelqu'un a du bois ?"
            faux = parole("Je ne veux pas de bois." if faux_mots else saisie,
                          ("ressource", "bois" if faux_mots else "faim", "", ""), personnage="aubin")
            bon = parole(saisie, ("ressource", "bois", "", ""), personnage="aubin")
            r, sortie, appels = jouer(m, saisie, [faux, bon, dialogue("Ta question est entendue.")],
                [rapport(ligne("mecanique", sources=["conversation_validee"]))],
                revues=[revue("sens", "ressource"), revue("sens", "ressource", conforme=True)])
            self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 2)
            self.assertEqual(len(r.data["paroles_joueur"]), 1)
            self.assertEqual(r.data["paroles_joueur"][-1]["texte"], saisie)
            self.assertNotIn("Je ne veux pas de bois.", sortie)
            self.assertIn(saisie, sortie)

        # Un verdict hors périmètre ne dispense jamais d'une opération manquante.
        m = presentes(antichambre_du_banc(), "aubin")
        saisie = '« Je te paie trois pièces pour une planche. »'
        faux = parole(saisie, ("propos", "", "", ""), personnage="aubin")
        faux["proposition"]["operations_demandees"]["proposition"] = True
        correction = parole(saisie, personnage="aubin")
        # L'omission déclarée doit être examinée avant toute parole sans achat.
        r, sortie, appels = jouer(m, saisie, [faux, correction], [],
            revues=[revue("adresse", "proposition"), revue("validation_moteur"), revue("adresse")])
        self.assertEqual(sum(f == "auditer_action" for f, _ in appels), 1)
        self.assertEqual(r.joueur["or"], m.joueur["or"])
        self.assertFalse(r.data.get("paroles_joueur"))
        self.assertNotIn("Tu dis", sortie)
        self.assertIn("Tu n'as encore rien dit", sortie)
