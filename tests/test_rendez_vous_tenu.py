"""Une invitation engage à rester ; une rupture n'est connue que si entendue."""
import unittest
from unittest.mock import patch

from donjon import appel
from donjon.deliberation import Palier, _attendre_qui_vient
from donjon.esprits import lire
from tests import test_constater_rumeurs as rumeurs, test_rendez_vous as rendez, test_appel_negocie as scenes
from tests.test_rendez_vous import reprises
from tests.test_tensions import attendre, chronique, recharger


def depart(salle):
    return ({"type": "rejoindre", "qui": "ilse", "lieu": salle},
            [{"operation": "aller", "cible": "", "outil": "", "lieu": salle, "condition": ""}])


class RendezVousTenuTests(unittest.TestCase):
    assert_decoupage = rendez.RendezVousTests.assert_decoupage

    def test_scene_reelle_sans_invitation_que_mireille_ne_peut_tenir(self):
        m = rumeurs.ChercherQuelquUnTests().mireille_cherche_odile()
        m.joueur.update(salle="grenier", position=[6, 3])
        m.data["visitees"] = sorted(set(m.data["visitees"]) | {"grenier"})
        bloc, coupe, debut = reprises(m, 5)
        self.assert_decoupage(bloc, coupe, debut)
        invites = [c for c in bloc.data["chronique"] if c["pnj"] == "mireille" and "Ici, viens !" in c["texte"]]
        self.assertLessEqual(len(invites), 1)
        self.assertTrue(any("Mireille demande une part" in t for t in chronique(bloc)))
        # La voie joueur conserve l'oracle historique : pas de nom appris,
        # ni de troisième voix entraînée au grenier par les invitations.
        joueur, texte = attendre(recharger(m))
        self.assertEqual(sorted(joueur.data["entendus"]), ["mireille", "odile"])
        self.assertNotIn("Mireille", texte)

    def rendez_vous(self):
        m = scenes.JArriveTests().aubin_cherche_gorm_qui_le_hele()
        from tests.support import calme, sans_souci
        calme(m, "marchand", "aubin")
        sans_souci(m, "marchand")
        appel.attendre(m, "marchand", "aubin", True)
        appel.venir(m, "aubin", "marchand")
        return recharger(m)

    def test_autre_scene_reelle_gorm_et_mael_au_hameau(self):
        from donjon import banc_pnj, pnj
        m = banc_pnj.creer("crue_hameau", 42, "tire")
        m.joueur.update(salle="chambre_cloche", position=[1, 3])
        # Depuis 221, Maël peut d'abord demander son chemin à Aubin.
        # Déclarer l'appel pour éprouver le même contrat sur cette scène,
        # indépendamment du choix entre ces deux moyens de contact.
        pnj.appeler(m, "mael", "marchand", [])
        self.assertIsNotNone(lire(m, "marchand")["rejoint"])
        chroniquer = pnj._chroniquer

        def verifier_depart(monde, id, texte, nature="geste"):
            if nature == "deplacement":
                self.assertIsNone(lire(monde, id)["rejoint"], (id, texte))
            return chroniquer(monde, id, texte, nature)

        with patch.object(pnj, "_chroniquer", verifier_depart):
            bloc, coupe, debut = reprises(m, 2)
        self.assert_decoupage(bloc, coupe, debut)
        self.assertIn("Maël appelle : « Gorm ? »", chronique(bloc))

    def test_autre_paire_un_plan_sans_rapport_ne_rompt_pas_l_attente(self):
        m = self.rendez_vous()
        r = _attendre_qui_vient(m, "marchand", depart("echoppe"), Palier.ROUTINE)
        self.assertEqual(r, ({"type": "attendre", "qui": "aubin"}, []))
        lire(m, "marchand")["intention"] = {"but": r[0], "plan": r[1], "motif": "rejoint", "depuis": m.data["minutes"], "attente": 0}
        bloc, coupe, debut = reprises(recharger(m), 2)
        self.assert_decoupage(bloc, coupe, debut)
        debut_attente = next((i for i,c in enumerate(bloc.data["chronique"]) if "comme convenu" in c["texte"]), len(bloc.data["chronique"]))
        self.assertFalse([c for c in bloc.data["chronique"][:debut_attente] if c["pnj"] == "marchand" and c["nature"] == "deplacement"])

    def test_depart_prioritaire_annonce_et_invalide_le_lieu_convenu(self):
        m = self.rendez_vous()
        resultat = depart("echoppe")
        self.assertEqual(_attendre_qui_vient(m, "marchand", resultat, Palier.BESOIN_PRESSANT), resultat)
        m = recharger(m)
        self.assertIsNone(lire(m, "marchand")["rejoint"])
        self.assertIsNone(lire(m, "aubin")["rejoindre"])
        self.assertIsNone(lire(m, "aubin")["croyances"]["marchand"]["lieu"]["valeur"])
        self.assertIn("crypte", lire(m, "aubin")["recherches"]["marchand"])
        self.assertIn("Gorm répond : « Je ne peux plus t'attendre. »", chronique(m))
        bloc, coupe, debut = reprises(m, 2)
        self.assert_decoupage(bloc, coupe, debut)
        self.assertNotIn("Gorm cesse d'attendre Aubin, qui avait promis de venir.", chronique(bloc))

    def test_palier_egal_ne_suffit_pas_a_partir(self):
        m = self.rendez_vous()
        r = _attendre_qui_vient(m, "marchand", depart("echoppe"), Palier.ATTENDRE_APPELANT)
        self.assertEqual(r[1], [])
        self.assertIsNotNone(lire(recharger(m), "marchand")["rejoint"])

    def test_trajet_prioritaire_vers_l_appelant_ne_permet_pas_une_fausse_invitation(self):
        m = scenes.JArriveTests().aubin_cherche_gorm_qui_le_hele()
        # Même objectif que l'appel, mais retenu par un geste sur place :
        # cette retenue momentanée ne signifie pas qu'il compte attendre.
        with patch("donjon.appel.retenu", return_value=True):
            self.assertIsNone(appel.decider(m, "aubin", "marchand", prie=True))
        with patch("donjon.appel.retenu", return_value=False):
            self.assertEqual(appel.decider(m, "aubin", "marchand", prie=True), appel.ARRIVE)

    def test_reaction_immediate_clot_aussi_avant_le_depart(self):
        from donjon.deliberation import choisir
        m = self.rendez_vous()
        resultat = depart("echoppe")
        with patch("donjon.defense.choisir", return_value=resultat):
            choisir(m, "marchand", m.data["minutes"])
        m = recharger(m)
        self.assertIsNone(lire(m, "marchand")["rejoint"])
        self.assertIsNone(lire(m, "aubin")["rejoindre"])
        self.assertEqual(lire(m, "marchand")["intention"]["plan"], resultat[1])
        bloc, coupe, debut = reprises(m, 2)
        self.assert_decoupage(bloc, coupe, debut)

    def test_annonce_non_entendue_ne_donne_aucun_savoir_a_distance(self):
        m = self.rendez_vous()
        with patch("donjon.ouie.saisit", return_value=False):
            appel.rompre_attente(m, "marchand")
        m = recharger(m)
        self.assertIsNone(lire(m, "marchand")["rejoint"])
        self.assertIsNotNone(lire(m, "aubin")["rejoindre"])
        bloc, coupe, debut = reprises(m, 2)
        self.assert_decoupage(bloc, coupe, debut)

    def test_rupture_clot_les_invitations_reciproques_et_preserve_un_autre_contact(self):
        m = self.rendez_vous()
        lire(m, "aubin")["rejoindre"] = None
        appel.attendre(m, "aubin", "marchand", False)
        appel.venir(m, "aubin", "ilse")
        autre = lire(m, "aubin")["rejoindre"].copy()
        appel.rompre_attente(m, "marchand")
        m = recharger(m)
        self.assertIsNone(lire(m, "aubin")["rejoint"])
        self.assertEqual(lire(m, "aubin")["rejoindre"], autre)
        bloc, coupe, debut = reprises(m, 2)
        self.assert_decoupage(bloc, coupe, debut)

    def test_annonce_visible_et_adressee_au_joueur_reste_lisible_apres_recharge(self):
        from donjon.ecoute import ENTENDU, entendus, rendre
        from donjon.temps import instant
        m = self.rendez_vous()
        m.joueur.update(salle="crypte", position=[4, 2], orientation="est")
        m.objets["torche"].update(lieu="joueur", allume=True)
        self.assertTrue(m.visible("marchand"))
        lire(m, "marchand")["rejoint"] = None
        appel.attendre(m, "marchand", "joueur", True)
        debut = instant(m) - 1
        appel.rompre_attente(m, "marchand")
        texte = rendre(m, entendus(m, debut, ENTENDU))
        self.assertIn("Je ne peux plus t'attendre.", "\n".join(texte))
        recharge = recharger(m)
        self.assertEqual(texte, rendre(recharge, entendus(recharge, debut, ENTENDU)))
        self.assertEqual(m.data, recharge.data)

    def test_voyageur_va_au_lieu_convenu_sans_relancer_sa_recherche(self):
        m = self.rendez_vous()
        r = _attendre_qui_vient(m, "aubin", ({"type": "part", "de": "marchand", "objet": "vivres"}, depart("echoppe")[1]), Palier.BESOIN_PRESSANT)
        self.assertEqual(r[0]["lieu"], "crypte")
        self.assertEqual(r[1][-1]["operation"], "inspecter")
        bloc, coupe, debut = reprises(m, 3)
        self.assert_decoupage(bloc, coupe, debut)
        self.assertFalse([c for c in bloc.data["chronique"] if c["pnj"] == "aubin" and "appelle :" in c["texte"]])

    def test_delai_ecoule_et_chemin_coupe_ne_sont_pas_un_lieu_trouve_vide(self):
        from donjon.esprits import croire
        m = self.rendez_vous()
        m.objets["porte"].update(ouverte=False, verrouillee=True)
        croire(m, "aubin", "porte", "verrouillee", True, "essai")
        d = lire(m, "aubin")["rejoindre"].copy()
        m.data["minutes"] = d["jusqu_a"] + 1
        appel.tenir(m, "aubin", m.data["minutes"])
        self.assertEqual(lire(m, "aubin")["rejoindre"], d)
        self.assertEqual(appel.plan_venir(m, "aubin")[1], [])
        bloc, coupe, debut = reprises(recharger(m), 2)
        self.assert_decoupage(bloc, coupe, debut)
        self.assertFalse([c for c in bloc.data["chronique"] if c["pnj"] == "aubin" and "appelle :" in c["texte"]])


if __name__ == "__main__":
    unittest.main()
