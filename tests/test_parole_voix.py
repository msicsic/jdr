"""Nommer qui l'on connaît, se faire attendre de qui l'on hèle, héler soi-même (branche ``parole-voix``).

- Le joueur nomme un personnage d'après ce qu'il sait de lui (vu, voix connue, nom qu'une voix
  s'est donné), jamais d'après une place connue : cas réel du banc Luna, un personnage vu de loin
  dont la place connue s'est vidée n'était plus reconnu par son nom.
- Qui répond à un appel s'attend à être rejoint : il attend sur place un temps borné, sauf pour
  plus pressant, ou va vers l'appelant s'il le cherche aussi. Cas réel de la crue : l'appelé
  répondait « Ici ! » puis poursuivait sa ronde ou allait voir un bruit, d'où des chassés-croisés.
- Le joueur hèle quelqu'un par son nom (« j'appelle Gorm ») : un geste du moteur, par la règle des
  PNJ ; l'appelé répond et l'attend, le joueur entend sa réponse par l'ouïe commune.
Chaque cas vérifie l'état après rechargement et ce que lit le joueur."""
import unittest

from donjon import lexique
from donjon.commandes import analyser as commande
from donjon.deliberation import REJOINT
from donjon.esprits import croire, lire
from donjon.geometrie import position_entree
from donjon.spatial import position_cible
from donjon.monde import ErreurMonde
from donjon.paroles import _connu_du_joueur, analyser
from donjon.operations import etape, sequence
from donjon.paroles import hele
from donjon.pnj import appeler
from donjon.voix import connaitre, entendues
from tests.support import calme
from tests.test_repli_et_appel import jouer
from tests.test_tensions import chronique, placer, recharger, relais, vivre
from tests.test_temps_etat import decouper, etat_pnj, faire
from tests.test_voix import appels, aubin_cherche_gorm


def cite(monde, id):
    """Le nom d'``id`` figure-t-il dans ce que le MJ et le joueur ont lu récemment, hors de ce que
    Corvus sait de qui il est (``personnages_connus``) ?"""
    contexte = {k: v for k, v in monde.contexte().items() if k != "personnages_connus"}
    corpus = lexique.corpus(contexte, monde.data.get("conversation", []))
    return id in lexique.entites_citees(monde, corpus)


def place_videe():
    """Corvus voit Ilse de loin (trois cases, jamais de près) ; elle part à l'échoppe, il regarde sa
    place vide, puis le temps passe : rien de récent ne la nomme plus."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    m.joueur.update(salle="antichambre", position=[2, 2], orientation="sud")
    placer(m, "ilse", "antichambre", (2, 5))
    placer(m, "aubin", "crypte", (2, 3))
    placer(m, "brune", "crypte", (3, 3))
    m = recharger(m)
    faire(m, "attendre")
    placer(m, "ilse", "echoppe", (2, 1))
    for _ in range(7):
        faire(m, "attendre")
    return recharger(m)


class NommerTests(unittest.TestCase):
    def test_cas_reel_la_place_videe_ne_fait_pas_oublier_qui_elle_est(self):
        m = place_videe()
        # Ce qui la faisait connaître jusqu'ici a disparu : souvenir de place, portrait, mention récente.
        self.assertNotIn("ilse", m.data.get("souvenirs_visuels", {}))
        self.assertNotIn("ilse", m.data["souvenirs_personnages"])
        self.assertFalse(cite(m, "ilse"))
        self.assertIn("ilse", m.data["personnages_vus"])
        self.assertTrue(_connu_du_joueur(m, "ilse"))
        # Le MJ sait que Corvus la connaît, sans savoir où elle est.
        self.assertEqual(m.contexte()["personnages_connus"]["ilse"], m.objets["ilse"]["nom"])
        self.assertEqual(analyser(m, "je dis à Ilse : viens m'aider")["nomme"], "ilse")
        reprise, sortie, appels = jouer(m, "je dis à Ilse : viens m'aider", [], [])
        self.assertEqual(appels, [])
        self.assertIn("Tu ne vois pas Ilse d'ici : approche-toi pour lui parler.", sortie)
        self.assertEqual(reprise.data.get("paroles_joueur", []), [])

    def test_donner_a_qui_n_est_plus_la_le_moteur_dit_qu_il_n_est_pas_la(self):
        m = place_videe()
        m.objets["cloche"]["lieu"] = "joueur"
        m = recharger(m)
        p = commande(m, "je donne la cloche à Ilse")
        self.assertEqual((p["action"], p["cible"], p["outil"]), ("remettre", "cloche", "ilse"))
        reprise, sortie, appels = jouer(m, "je donne la cloche à Ilse", [], [])
        self.assertEqual(appels, [])
        self.assertIn("n'est pas là pour le recevoir", sortie)
        self.assertEqual(reprise.objets["cloche"]["lieu"], "joueur")

    def test_une_voix_connue_ou_un_nom_donne_suffisent_jamais_une_place(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[2, 2], orientation="sud")
        for id in ("brune", "aubin", "ilse"):
            placer(m, id, "crypte", (2 + ("brune", "aubin", "ilse").index(id), 3))
        # Jamais vue : Brune n'est qu'une voix connue ; Aubin, une voix inconnue qui s'est dite Aubin.
        for id in ("brune", "aubin", "ilse"):
            m.data["souvenirs_visuels"].pop(id, None)
        connaitre(m, "joueur", "brune")
        entendues(m, "joueur", ecrire=True)["ilse"] = {"minute": 0, "se_dit": "aubin", "mefiance": False, "n": 1}
        m = recharger(m)
        self.assertNotIn("brune", m.data.get("personnages_vus", []))
        for nom, id in (("Brune", "brune"), ("Aubin", "aubin")):
            self.assertTrue(_connu_du_joueur(m, id), id)
            reprise, sortie, appels = jouer(m, f"je dis à {nom} : approche", [], [])
            self.assertEqual(appels, [])
            self.assertIn(f"Tu ne vois pas {nom} d'ici : approche-toi pour lui parler.", sortie)
        # Ilse, ni vue ni entendue, ni nommée : il ne la connaît pas.
        self.assertFalse(_connu_du_joueur(m, "ilse"))
        with self.assertRaises(ErreurMonde):
            commande(m, "je donne la cloche à Ilse")



def gorm_en_ronde():
    """Cas réel, rejoué au Relais : Aubin a faim et hèle Gorm, qu'il ne sait où trouver ; Gorm, à
    la salle des vannes, s'en va faire sa ronde du refuge (routine). Avant, il répondait puis
    partait : Aubin le cherchait là d'où venait la voix, rappelait, et le trouvait plus tard."""
    m = aubin_cherche_gorm()
    lire(m, "marchand")["visites"]["antichambre"] = m.data["minutes"] - 46
    return recharger(m)


def lieux(m):
    return m.objets["marchand"]["lieu"], m.objets["aubin"]["lieu"]


class RejointTests(unittest.TestCase):
    def test_cas_reel_l_appele_attend_et_l_appelant_le_trouve_au_premier_appel(self):
        m = gorm_en_ronde()
        m, _ = vivre(m, 2)  # Aubin hèle, Gorm répond.
        self.assertIn("Gorm répond : « Ici ! »", chronique(m))
        r = lire(m, "marchand")["rejoint"]
        self.assertEqual((r["qui"], r["jusqu_a"] - r["depuis"]), ("aubin", REJOINT))
        self.assertEqual(lire(m, "marchand")["intention"]["but"], {"type": "attendre", "qui": "aubin"})
        attendu_la = m.objets["marchand"]["lieu"]
        m = recharger(m)
        for _ in range(4):
            m, _ = vivre(m, 1)
            if not lire(m, "marchand")["rejoint"]:
                break
            self.assertEqual(m.objets["marchand"]["lieu"], attendu_la)  # Il attend là où il a répondu.
        m = recharger(m)
        self.assertEqual(len(appels(m, "aubin")), 1)
        self.assertIn("Gorm retrouve Aubin, qui l'avait hélé.", chronique(m))
        self.assertTrue(obtient_sa_part(m))
        self.assertIsNone(lire(m, "marchand")["rejoint"])

    def test_le_meme_laps_decoupe_donne_le_meme_monde(self):
        d_un_bloc, morcele = decouper(gorm_en_ronde, 6)
        self.assertIn("Gorm retrouve Aubin, qui l'avait hélé.", chronique(morcele))
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))

    def test_sans_personne_qui_vienne_il_cesse_d_attendre_a_l_echeance(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        placer(m, "marchand", "crypte", (5, 2))
        placer(m, "aubin", "beffroi", position_entree(m, "beffroi"))
        lire(m, "marchand")["visites"]["antichambre"] = -46  # Sa ronde l'attend.
        appeler(m, "aubin", "marchand", [])  # Aubin, sans rien vouloir de plus, ne vient pas.
        self.assertEqual(lire(m, "marchand")["rejoint"]["qui"], "aubin")
        m = recharger(m)
        ici = m.objets["marchand"]["lieu"]
        for _ in range(REJOINT - 1):
            m, _ = vivre(m, 1)
            self.assertEqual(m.objets["marchand"]["lieu"], ici)
        for _ in range(3):
            m, _ = vivre(m, 1)
        m = recharger(m)
        self.assertIn("Gorm cesse d'attendre Aubin.", chronique(m))
        self.assertIsNone(lire(m, "marchand")["rejoint"])
        self.assertGreaterEqual(lire(m, "marchand")["visites"]["antichambre"], REJOINT)  # Puis sa ronde.

    def test_un_besoin_plus_pressant_passe_avant(self):
        """Gorm a répondu à Aubin ; sa faim presse : il va manger d'abord, puis attend Aubin."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        placer(m, "marchand", "crypte", (5, 2))
        placer(m, "aubin", "beffroi", position_entree(m, "beffroi"))
        appeler(m, "aubin", "marchand", [])
        lire(m, "marchand")["besoins"]["faim"] = 95.0
        m = recharger(m)
        m, _ = vivre(m, 1)
        self.assertEqual(lire(m, "marchand")["intention"]["motif"], "faim")
        self.assertEqual(lire(m, "marchand")["rejoint"]["qui"], "aubin")
        while lire(m, "marchand")["intention"]["motif"] == "faim":
            m, _ = vivre(m, 1)
        self.assertLess(m.data["minutes"], REJOINT)
        self.assertEqual(lire(m, "marchand")["intention"]["but"], {"type": "attendre", "qui": "aubin"})

    def test_s_il_le_cherche_aussi_il_va_vers_lui(self):
        """Gorm hèle Aubin ; Aubin, qui cherche Gorm pour sa part et connaît sa voix, sait d'où vient
        l'appel : il va vers lui au lieu d'attendre."""
        m = aubin_cherche_gorm()
        self.assertIn("marchand", lire(m, "aubin")["voix"])
        # Aubin, affamé, cherche Gorm à la conduite basse (la délibération de la minute passée).
        lire(m, "aubin")["intention"] = {
            "but": {"type": "part", "objet": "vivres", "de": "marchand"}, "motif": "faim", "depuis": 2, "attente": 0,
            "plan": [{"operation": "aller", "cible": "", "outil": "", "lieu": "echoppe", "condition": ""},
                     {"operation": "inspecter", "cible": "", "outil": "", "lieu": "echoppe", "condition": "",
                      "contenu": {"cherche": "marchand"}}]}
        appeler(m, "marchand", "aubin", [])
        self.assertIn("Aubin répond : « Ici ! »", chronique(m))
        self.assertIsNone(lire(m, "aubin")["rejoint"])
        self.assertEqual(lire(m, "aubin")["croyances"]["marchand"]["lieu"]["valeur"], "crypte")
        m = recharger(m)
        for _ in range(4):
            m, _ = vivre(m, 1)
        m = recharger(m)
        self.assertTrue(obtient_sa_part(m))
        self.assertEqual(appels(m, "aubin"), [])


def obtient_sa_part(m):
    """Aubin, une fois Gorm retrouvé, obtient sa part : promise sur demande, ou achetée (le moyen
    dépend du prix de la demande et de sa bourse, pas de l'appel)."""
    return any(ligne in chronique(m) for ligne in (
        "Aubin demande une part des vivres du refuge à Gorm (promis).",
        "Aubin achète une part des vivres du refuge à Gorm pour 2 pièces (vendu)."))


def gorm_derriere_la_porte():
    """Corvus au palier des vannes, devant la porte étanche fermée ; Gorm, qu'il a vu mais jamais
    entendu parler, à la salle des vannes, derrière elle. Les autres sont loin."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("brune", "ilse", "aubin")):
        placer(m, id, "chambre_cloche", (2 + n, 2))
    placer(m, "marchand", "crypte", (5, 2))
    m.objets["porte"]["verrouillee"] = False
    m.joueur.update(salle="beffroi", position=list(position_cible(m, "porte", "beffroi")), orientation="ouest")
    m.data["visitees"] = sorted({*m.data["visitees"], "beffroi"})
    m.identifier(["marchand"])
    assert not m.objets["porte"]["ouverte"] and "marchand" not in m.data["voix_connues"]
    return recharger(m)


class HelerJoueurTests(unittest.TestCase):
    def test_formes(self):
        m = place_videe()
        for saisie in ("j'appelle Ilse", "je hèle Ilse", "je crie le nom d'Ilse", "j'appelle Ilse par son nom",
                       "je crie « Ilse ? »", "crier : Ilse !", "j'appelle Ilse à voix haute", "appeler Ilse"):
            self.assertEqual(hele(m, saisie), "ilse", saisie)
        # Un appel à l'aide, un cri, deux noms, une parole, un objet : pas un appel par le nom.
        for saisie in ("j'appelle à l'aide", "je crie", "j'appelle Ilse et Aubin", "Ilse ?", "« Ilse ? »",
                       "j'appelle la torche"):
            self.assertIsNone(hele(m, saisie), saisie)

    def test_cas_reel_il_hele_gorm_derriere_la_porte(self):
        m = gorm_derriere_la_porte()
        reprise, sortie, appels = jouer(m, "j'appelle Gorm", [], [])
        self.assertEqual(appels, [])  # Le moteur, jamais une interprétation du MJ.
        self.assertIn("Tu appelles : « Gorm ? »", sortie)
        # Une voix qu'il n'a jamais entendue : il entend ce qu'elle dit et le nom qu'elle se donne.
        self.assertIn("Tu entends, à l'ouest, une voix qui se dit Gorm répondre : « Ici ! »", sortie)
        self.assertEqual([e["se_dit"] for e in reprise.data["voix_entendues"].values()], ["marchand"])
        self.assertEqual(lire(reprise, "marchand")["rejoint"]["qui"], "joueur")
        self.assertEqual(lire(reprise, "marchand")["intention"]["but"], {"type": "attendre", "qui": "joueur"})
        self.assertIn("Corvus appelle : « Gorm ? »", chronique(reprise))
        self.assertIn("Gorm répond : « Ici ! »", chronique(reprise))
        # Corvus ouvre la porte : Gorm l'a attendu là ; ils se voient, l'attente est finie.
        reprise, sortie, _ = jouer(reprise, "ouvrir porte", [], [])
        self.assertIn("Tu aperçois au-delà du passage Gorm, gardien du relais.", sortie)
        self.assertEqual(reprise.objets["marchand"]["lieu"], "crypte")
        self.assertIsNone(lire(reprise, "marchand")["rejoint"])
        self.assertIn("Gorm retrouve Corvus, qui l'avait hélé.", chronique(reprise))

    def test_une_voix_connue_dit_qui_repond_meme_en_forme_de_question(self):
        m = gorm_derriere_la_porte()
        connaitre(m, "joueur", "marchand")
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "je crie « Gorm ? »", [], [])
        self.assertEqual(appels, [])
        self.assertIn("Tu entends, à l'ouest : Gorm répond : « Ici ! »", sortie)

    def test_qui_se_mefie_de_lui_ne_repond_pas(self):
        m = gorm_derriere_la_porte()
        connaitre(m, "marchand", "joueur")
        croire(m, "marchand", "joueur", "fiable", False, "vu")
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "je hèle Gorm", [], [])
        self.assertEqual(appels, [])
        self.assertIn("Aucune réponse ne te parvient.", sortie)
        self.assertNotIn("Gorm répond : « Ici ! »", chronique(reprise))
        self.assertIsNone(lire(reprise, "marchand")["rejoint"])

    def test_le_mj_ne_hele_que_qui_corvus_connait(self):
        m = gorm_derriere_la_porte()
        for id in ("ilse", "brune", "aubin"):
            m.data["souvenirs_visuels"].pop(id, None)
        m = recharger(m)
        from donjon.moteur import Moteur
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(sequence(etape("emettre_son", "ilse", methode="heler")))
        self.assertIn("Tu ne connais personne de ce nom", str(refus.exception))
        self.assertIn("reçu « ilse »", refus.exception.attendu)
        self.assertIn("marchand", refus.exception.attendu)
        # Une autre cause, un autre refus : héler sans nommer personne.
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(sequence(etape("emettre_son", "joueur", methode="heler")))
        self.assertIn("Dis qui tu appelles", str(refus.exception))
        self.assertIn("pas joueur", refus.exception.attendu)


if __name__ == "__main__":
    unittest.main()
