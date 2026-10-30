"""Noyau public, qualificatifs séparés : saisie, contrôles, affichage et recharge."""
from donjon.emissions import joueur as emissions_joueur
import copy
import unittest

from donjon.atelier import nouveau_atelier
from donjon.monde import ErreurMonde
from donjon.moteur import proposition
from donjon.narration import consigner, controler, voix_inconnues
from donjon.noms import public, reperes_designations
from donjon.rendu import decrire
from donjon.voix import designation, nom_pour_joueur, se_nommer
from tests.test_audits_attendu import jouer, ligne, rapport
from tests.test_luna_noms import action
from tests.test_luna_restes import jouer_physique
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import placer, recharger
from donjon.banc_pnj import creer
from tests.support import calme


def voix(qui):
    m = creer("relais", 1985, "fixe")
    calme(m, "ilse", "marchand", "brune", "aubin")
    m.joueur.update(salle="beffroi", position=[3, 3], orientation="est")
    for o in m.objets.values():
        if "allume" in o:
            o["allume"] = False
    m.data["voix_connues"] = []
    m.data["noms_connus"] = []
    placer(m, qui, m.joueur["salle"], [6, 3])
    m.data["entendus"] = [qui]
    se_nommer(m, "joueur", qui, qui)
    return recharger(m)


class DesignationsTests(unittest.TestCase):
    def test_voix_qualifiees_apres_la_parole_reelle_et_recharge(self):
        for qui, forme in (("ilse", "La voix toute proche qui se dit Ilse"),
                           ("marchand", "La voix basse et lointaine qui se dit Gorm")):
            with self.subTest(qui=qui):
                m = voix(qui)
                ref = designation(m, qui)
                self.assertTrue(ref.startswith("voix_"))
                texte = forme + " demeure dans le noir."
                r, sortie, appels = jouer(m, "« C'est moi, Brune. »", [
                    parole("C'est moi, Brune.", personnage=ref), dialogue(texte)],
                    [rapport(ligne("mecanique", sources=["interlocuteurs"]))])
                # G16 / rapport 345 : l'identité reçoit ses mots moteur ; exercer
                # les qualificatifs libres au tour suivant, après cette même parole.
                r, description, suite = jouer(r, "mj que perçois-je ?", [dialogue(texte)],
                    [rapport(ligne("mecanique", sources=["interlocuteurs"]))])
                sortie += description
                appels.extend(suite)
                self.assertIn(texte, sortie)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], texte)
                self.assertEqual(emissions_joueur(r)[-1]["texte"], "C'est moi, Brune.")
                self.assertEqual(r.data["noms_connus"], [])
                self.assertFalse(r.visible(qui))
                self.assertEqual(nom_pour_joueur(r, qui), nom_pour_joueur(m, qui))
                self.assertEqual(public(r, {"attestations": [texte]})["attestations"], [texte])
                audits = [e for f, e in appels if f == "auditer_narration"]
                self.assertEqual(len(audits), 1)
                self.assertTrue(any(d["reference"] == ref and d["forme_ecrite"] == texte
                                    for d in audits[0]["designations"]))

    def test_identites_ajoutees_refusees_et_garde_refait_a_lecriture(self):
        m = voix("ilse")
        faits = {"interlocuteurs": m.contexte()["interlocuteurs"]}
        bon = "La voix toute proche qui se dit Ilse demeure dans le noir."
        for mauvais in ("La voix d'Ilse demeure dans le noir.",
                        "La voix de Gorm qui se dit Ilse demeure dans le noir.",
                        "La voix toute proche qui se dit Gorm demeure dans le noir.",
                        "La voix qui ne se dit pas Ilse demeure dans le noir."):
            with self.subTest(mauvais=mauvais):
                r, sortie, appels = jouer(m, "mj que perçois-je ?", [dialogue(mauvais), dialogue(bon)],
                    [rapport(ligne("mecanique", sources=["interlocuteurs"]))] * 2)
                self.assertNotIn(mauvais, sortie)
                self.assertIn(bon, sortie)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], bon)
                self.assertEqual(r.data["noms_connus"], [])
                refus = [e for f, e in appels if f == "repondre_au_joueur"][1]["controle_narratif"]
                self.assertTrue(all(x["attendu"] for x in refus))
                audit = controler(mauvais, rapport(ligne("mecanique", sources=["interlocuteurs"])), faits)
                audit.update(texte_initial=mauvais, faits=faits, fondement="Ilse Gorm")
                avant = copy.deepcopy(r.data)
                with self.assertRaises(ErreurMonde):
                    consigner(r, {"texte": mauvais, "_audit": audit})
                self.assertEqual(recharger(r).data, avant)

    def test_objets_qualifies_meme_reference_etat_et_rendu(self):
        for cible, demande, nom in (
            ("ficelle", "je ramasse la bobine de ficelle", "bobine de ficelle solide"),
            ("couteau", "je ramasse le vieux couteau", "couteau")):
            with self.subTest(cible=cible):
                m = nouveau_atelier()
                o = m.objets[cible]
                o.update(lieu=m.joueur["salle"], position=list(m.joueur["position"]),
                         position_salle=m.joueur["salle"])
                if cible == "couteau":
                    o["nom"] = nom
                r, sortie, appels = jouer_physique(m, [demande, "tenter"],
                                                  [action(proposition("prendre", cible))])
                self.assertEqual(r.objets[cible]["lieu"], "joueur")
                self.assertIn(nom, sortie)
                self.assertIn(nom, decrire(r, cible))
                revue = next(e for f, e in appels if f == "auditer_action")
                liens = [d for d in revue["designations"] if d["reference"] == cible]
                self.assertTrue(any(d["forme_ecrite"] == demande for d in liens))
                self.assertTrue(any(nom in d["forme_ecrite"] for d in liens))
                self.assertTrue(all(d["canonique"] == nom for d in liens))
                self.assertEqual(r.objets[cible]["materiau"], m.objets[cible]["materiau"])

    def test_matiere_contraire_refusee_avec_source_et_attendu(self):
        for cible, mauvais in (("ficelle", "La bobine de chanvre est à tes pieds."),
                               ("couteau", "Le couteau en cire est à tes pieds.")):
            with self.subTest(cible=cible):
                m = nouveau_atelier()
                o = m.objets[cible]
                o.update(lieu=m.joueur["salle"], position=list(m.joueur["position"]),
                         position_salle=m.joueur["salle"])
                if cible == "ficelle":
                    o["materiau"] = "lin"  # « fibres » seul ne contredirait pas « chanvre ».
                bon = "Tu peux regarder cet objet."
                avant = copy.deepcopy(o)
                r, sortie, appels = jouer(m, "mj décris cet objet", [dialogue(mauvais), dialogue(bon)],
                    [rapport(ligne("contradictoire", sources=["objet:" + cible],
                                   motif="La matière contredit celle de l'objet.")), rapport(ligne("neutre"))])
                self.assertNotIn(mauvais, sortie)
                self.assertIn(bon, sortie)
                self.assertEqual(r.data["narrations_mj"][-1]["texte"], bon)
                self.assertEqual(r.objets[cible], avant)
                refus = [e for f, e in appels if f == "repondre_au_joueur"][1]["controle_narratif"]
                self.assertTrue(all(x["attendu"] for x in refus))

    def test_la_contre_revue_garde_la_matiere_demandee_et_refuse_lecart(self):
        m = nouveau_atelier()
        m.objets["ficelle"].update(position=list(m.joueur["position"]))
        m.objets["ficelle"]["materiau"] = "lin"
        demande = "je ramasse la bobine de chanvre"
        bon = "Tu peux regarder cet objet."
        r, sortie, appels = jouer(m, demande, [action(proposition("prendre", "ficelle")), dialogue(bon)],
            [rapport(ligne("neutre"))], [{"conforme": False, "motif": "La matière demandée diffère."}])
        revue = next(e for f, e in appels if f == "auditer_action")
        liens = [d for d in revue["designations"] if d["reference"] == "ficelle"]
        self.assertTrue(any(d["forme_ecrite"] == demande and d["faits"]["materiau"] == "lin"
                            for d in liens))
        self.assertNotEqual(r.objets["ficelle"]["lieu"], "joueur")
        self.assertIn(bon, sortie)
        self.assertNotIn("Tu prends", sortie)
        retour = [e for f, e in appels if f == "repondre_au_joueur"][1]["faits"]["retour_moteur"]
        self.assertIn("attendu", retour)

    def test_noyau_commun_sans_effacer_les_qualificatifs_ni_les_ambiguities(self):
        faits = {"objet:a": {"nom": "bobine de ficelle", "materiau": "fibres"},
                 "objet:b": {"nom": "bobine de ficelle", "materiau": "fibres"}}
        texte = "la vieille bobine solide de ficelle à ta gauche"
        liens = reperes_designations(texte, faits)
        self.assertEqual({d["reference"] for d in liens}, {"a", "b"})
        self.assertTrue(all(d["forme_ecrite"] == texte for d in liens))
        m = voix("ilse")
        nom = m.contexte()["interlocuteurs"]
        self.assertTrue(voix_inconnues(m, [], {"interlocuteurs": nom},
            "La voix de Gorm qui se dit Ilse demeure dans le noir."))

    def test_appellation_rapportee_avec_apostrophe_typographique(self):
        m = voix("ilse")
        entree = m.data["voix_entendues"]["ilse"]
        entree.update(se_dit=None, appelee="ilse")
        m = recharger(m)
        texte = "La voix toute proche qu’on appelle Ilse demeure dans le noir."
        r, sortie, _ = jouer(m, "mj que perçois-je ?", [dialogue(texte)],
            [rapport(ligne("mecanique", sources=["interlocuteurs"]))])
        self.assertIn(texte, sortie)
        self.assertEqual(r.data["narrations_mj"][-1]["texte"], texte)
        self.assertEqual(public(r, {"attestations": [texte]})["attestations"], [texte])
        self.assertEqual(r.data["noms_connus"], [])


if __name__ == "__main__":
    unittest.main()
