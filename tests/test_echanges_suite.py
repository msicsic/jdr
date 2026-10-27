"""Suite des échanges : rendre ce qu'on doit est un choix, une seule règle pour toute contrepartie
payée et non livrée, les tâches payées entre PNJ, le prêt réclamé au joueur, la réclamation du joueur
par la parole, la demande de ce que l'autre pourrait avoir (``biens``, ``echanges``, ``paroles``).

Chaque test vérifie l'état du monde, et ce que le joueur lit, après rechargement.
"""

from tests.support import lier
import unittest
from unittest.mock import patch

from donjon.banc_pnj import creer, executer
from donjon.biens import bourse, comptes_joueur, rembourser
from donjon.deplacement_objet import deplacer
from donjon.echanges import ENGAGEMENT_MAX, demander, engager, enqueter
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.paroles import preparer_parole
from donjon.rendu import fiche
from donjon.relations import envers
from tests.support import calme, regarder
from tests.test_entretenir import sans
from tests.test_tensions import chronique, placer, recharger, relais, vivre


def memoires(m, id, sorte):
    return [s for s in lire(m, id)["memoire"] if s["type"] == sorte]


def fiable(m, id, qui):
    from donjon.relations import fiable as avis
    return avis(m, id, qui)


def ensemble(m, a, b, salle="antichambre"):
    """Placement d'auteur : ``a`` et ``b`` côte à côte, face à face, et chacun le sait."""
    placer(m, a, salle, (1, 3))
    placer(m, b, salle, (2, 3))
    regarder(m, a, b)
    regarder(m, b, a)
    percevoir_tous(m)


class RembourserTests(unittest.TestCase):
    """Garder l'argent dû est une faute au prix de son honnêteté, contre ce que valent pour lui ces
    pièces (``biens.garde_du``) : le débiteur malhonnête et endetté peut ne pas rendre, et son
    créancier, qui le constate, s'en méfie et peut le dire."""

    def dette_de_brune(self, honnetete=None):
        """Relais : Brune (honnêteté 20, endettée) doit 2 pièces à Ilse, pour une part qu'elle ne lui
        a jamais servie (placement d'auteur : la dette, comme ``engagements_echus`` la fait naître)."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        if honnetete is not None:
            m.objets["brune"]["profil"]["valeurs"]["honnetete"] = honnetete
        rembourser(m, "brune", "ilse", 2, "vivres", "part")
        ensemble(m, "brune", "ilse")
        return m

    def test_la_malhonnete_endettee_garde_ce_qu_on_lui_reclame(self):
        m = self.dette_de_brune()
        m, lignes = vivre(recharger(m), 1)
        self.assertEqual(m.data["dettes"][0]["montant"], 2)
        self.assertEqual((bourse(m, "brune"), bourse(m, "ilse")), (3, 8))
        self.assertIn("Brune refuse de rendre à Ilse les 2 pièces qu'elle lui doit.", chronique(m))
        self.assertEqual(envers(m, "ilse", "brune")["confiance"], 45)
        self.assertEqual(envers(m, "ilse", "brune")["motifs"][-1]["type"], "dette_niee")
        self.assertEqual(memoires(m, "ilse", "dette_niee")[-1]["auteur"], "brune")
        # Elle ne le lui redemande pas à chaque minute.
        m, _ = vivre(m, 3)
        self.assertEqual(sum("refuse de rendre" in t for t in chronique(m)), 1)

    def test_le_creancier_le_dit_a_qui_il_se_fie(self):
        m = self.dette_de_brune()
        m, _ = vivre(recharger(m), 1)
        # Aubin vient près d'Ilse ; désœuvrée, elle lui confie ce qu'elle sait de Brune.
        placer(m, "brune", "crypte", (2, 2))
        placer(m, "aubin", "antichambre", (1, 3))
        regarder(m, "ilse", "aubin")
        regarder(m, "aubin", "ilse")
        percevoir_tous(m)
        lire(m, "ilse")["intention"] = None
        m, _ = vivre(recharger(m), 2)
        self.assertTrue(any(t.startswith("Ilse ") and "à Aubin que Brune garde les 2 pièces qu'elle doit à Ilse" in t
                            for t in chronique(m)), chronique(m))
        self.assertEqual(envers(m, "aubin", "brune")["confiance"], 52)
        self.assertEqual(envers(m, "aubin", "brune")["motifs"][-1]["type"], "rumeur")

    def test_honnete_elle_rend_ce_qu_elle_doit(self):
        # Même dette, même bourse : à l'honnêteté entière, rendre ne se pèse pas.
        m = self.dette_de_brune(honnetete=100)
        m, _ = vivre(recharger(m), 1)
        self.assertEqual(m.data["dettes"], [])
        self.assertEqual((bourse(m, "brune"), bourse(m, "ilse")), (1, 10))
        self.assertIsNot(fiable(m, "ilse", "brune"), False)

    def test_a_l_auberge_la_somme_decide(self):
        # Autre cas de même nature, à l'auberge : Joss et Lucien, honnêteté 50 (faute à 20 minutes).
        # Une pièce vaut 4 minutes pour Joss : il la rend ; quatre en valent 24 pour Lucien : il les garde.
        m = calme(creer("auberge", 1985, "fixe"), "joss", "lucien", "mireille", "odile")
        rembourser(m, "joss", "mireille", 1, "fagots_etable", "part")
        rembourser(m, "lucien", "odile", 4, "bois_anselme", "tache")
        ensemble(m, "joss", "mireille", "cuisine")
        placer(m, "lucien", "salle_commune", (2, 2))
        placer(m, "odile", "salle_commune", (3, 2))
        regarder(m, "lucien", "odile")
        regarder(m, "odile", "lucien")
        percevoir_tous(m)
        m, _ = vivre(recharger(m), 1)
        self.assertEqual([(d["de"], d["montant"]) for d in m.data["dettes"]], [("lucien", 4)])
        self.assertIn("Joss rend 1 pièce à Mireille : la part des fagots de l'écurie n'a pas été servie.",
                      chronique(m))
        self.assertIn("Lucien refuse de rendre à Odile les 4 pièces qu'il lui doit.", chronique(m))
        self.assertEqual(envers(m, "odile", "lucien")["confiance"], 45)


class JoueurReclameTests(unittest.TestCase):
    """Le joueur réclame son dû par la parole (contenu ``reclamer``), tranché par le moteur ; il voit
    ce qu'on lui doit sur sa fiche."""

    def devant(self, qui="marchand"):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="echoppe", position=[2, 1])
        if qui != "marchand":
            placer(m, "marchand", "crypte", (2, 2))   # Placement d'auteur : Gorm est ailleurs.
        placer(m, qui, "echoppe", (1, 1))
        regarder(m, qui, "joueur")
        regarder(m, "joueur", qui)
        percevoir_tous(m)
        return m

    def parole(self, qui, sujet="", type_="reclamer"):
        texte = "Rends-moi ce que tu me dois."
        return {"personnage": qui, "replique": texte,
                "contenu": [{"type": type_, "sujet": sujet, "attribut": "", "valeur": ""}],
                "_intention": texte}

    def test_gorm_rend_ce_qu_il_doit_et_la_fiche_le_montrait(self):
        m = self.devant()
        rembourser(m, "marchand", "joueur", 2, "vivres", "part")
        m = recharger(m)
        self.assertIn("Gorm te doit 2 pièces : la part des vivres du refuge que tu avais payée ne t'a pas été "
                      "servie.", fiche(m))
        travail, rapport = preparer_parole(m, self.parole("marchand"))
        self.assertIn("Gorm te rend 2 pièces : la part des vivres du refuge que tu avais payée ne t'a pas été "
                      "servie.", rapport["faits"])
        m = recharger(travail)
        self.assertEqual((m.joueur["or"], m.data["dettes"]), (26, []))
        self.assertNotIn("Comptes", fiche(m))

    def test_brune_refuse_et_la_dette_demeure(self):
        # Autre cas de même nature : la débitrice malhonnête et endettée garde l'argent qu'on lui
        # réclame ; de vive voix, comme quand un PNJ créancier la retrouve.
        m = self.devant("brune")
        rembourser(m, "brune", "joueur", 2, "vivres", "part")
        m, lignes = vivre(recharger(m), 1)
        self.assertFalse([x for x in lignes if "pièce" in x])   # Elle ne rend rien d'elle-même.
        travail, rapport = preparer_parole(m, self.parole("brune"))
        self.assertIn("Brune refuse de te rendre les 2 pièces qu'elle te doit.", rapport["faits"])
        m = recharger(travail)
        self.assertEqual((m.joueur["or"], m.data["dettes"][0]["montant"]), (24, 2))
        self.assertIn("Brune te doit 2 pièces", fiche(m))
        self.assertEqual(memoires(m, "brune", "refus_rembourser")[-1]["a"], "joueur")

    def test_rien_n_est_du(self):
        m = self.devant("ilse")
        travail, rapport = preparer_parole(m, self.parole("ilse"))
        self.assertTrue(rapport["faits"][0].endswith(" ne te doit aucune pièce."), rapport["faits"])

    def test_son_objet_porte_par_un_autre(self):
        m = self.devant("brune")
        # Placement d'auteur : Corvus connaît son couteau, que Brune a gardé.
        m.objets["couteau"]["proprietaire"] = "joueur"
        m.data["connus"].append("couteau")
        deplacer(m, "couteau", "brune")
        travail, rapport = preparer_parole(m, self.parole("brune", "couteau"))
        self.assertTrue(any(" te rend le couteau" in f for f in rapport["faits"]), rapport["faits"])
        self.assertEqual(recharger(travail).objets["couteau"]["lieu"], "joueur")

    def test_une_reclamation_que_le_moteur_ne_sait_trancher_est_refusee_au_mj(self):
        m = self.devant("brune")
        with self.assertRaises(ErreurMonde) as refus:
            preparer_parole(m, self.parole("brune", "le trésor du roi"))
        self.assertIn("contenu[0].sujet", refus.exception.attendu)
        self.assertIn("le trésor du roi", refus.exception.attendu)


class ContrepartieTests(unittest.TestCase):
    """Une seule règle pour toute contrepartie payée d'avance et non livrée à l'échéance : une part,
    un objet acheté, une tâche payée (``echanges.engagements_echus``, ``biens.rembourser``)."""

    def marteau_achete(self):
        """Relais : le marteau de l'échoppe est à Gorm (placement d'auteur, prix 7), posé sur l'établi ;
        Corvus le lui achète de vive voix. Gorm ne le porte pas : il ira le prendre pour le lui remettre."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["marteau"]["proprietaire"] = "marchand"
        croire(m, "marchand", "marteau", "lieu", "echoppe", "savoir", salle="echoppe", case=[8, 5])
        m.data["connus"].append("marteau")
        ensemble_joueur(m, "marchand")
        texte = "Gorm, je t'achète ton marteau."
        travail, rapport = preparer_parole(m, {
            "personnage": "marchand", "replique": texte, "_intention": texte,
            "contenu": [{"type": "demande", "sujet": "marteau", "attribut": "", "valeur": "7"}]})
        self.assertIn("pièces et ira chercher le marteau", " ".join(rapport["faits"]))
        m = recharger(travail)
        self.assertEqual(m.joueur["or"], 17)
        self.assertIn({"condition": {"objet": "marteau", "remettre": "joueur"}, "pour": "joueur",
                       "minute": m.data["minutes"], "paye": {"objet": "marteau", "prix": 7, "quoi": "objet"}},
                      lire(m, "marchand")["engagements"])
        return m

    def test_gorm_va_chercher_le_marteau_vendu_et_le_remet(self):
        m = self.marteau_achete()
        lignes = []
        for _ in range(20):
            m, ajout = vivre(m, 1)
            lignes += ajout
            if m.objets["marteau"]["lieu"] == "joueur":
                break
        self.assertEqual((m.objets["marteau"]["lieu"], m.objets["marteau"]["proprietaire"]), ("joueur", "joueur"))
        self.assertIn("Gorm te remet le marteau : tu l'avais payé.", lignes)
        self.assertEqual(lire(m, "marchand")["engagements"], [])
        self.assertEqual(m.data.get("dettes", []), [])
        self.assertEqual(m.data.get("permissions", []), [])   # Vendu, pas prêté.

    def test_non_remis_a_l_echeance_le_prix_est_du_et_rendu(self):
        # Autre cas de même nature : la parole échoit sans que le marteau soit remis ; Gorm, honnête,
        # rend les 7 pièces quand il retrouve Corvus, qui le lit et ne voit plus de créance.
        m = self.marteau_achete()
        placer(m, "marchand", "crypte", (2, 2))
        lire(m, "marchand")["engagements"][0]["minute"] = -ENGAGEMENT_MAX - 1
        m, _ = vivre(recharger(m), 1)
        self.assertEqual([(d["de"], d["a"], d["montant"], d["quoi"]) for d in m.data["dettes"]],
                         [("marchand", "joueur", 7, "objet")])
        self.assertIn("Gorm te doit 7 pièces : le marteau que tu avais payé ne t'a pas été remis.", comptes_joueur(m))
        ensemble_joueur(m, "marchand")
        m, lignes = vivre(recharger(m), 1)
        self.assertIn("Gorm te rend 7 pièces : le marteau que tu avais payé ne t'a pas été remis.", lignes)
        self.assertEqual((m.joueur["or"], m.data["dettes"]), (24, []))


def ensemble_joueur(m, qui):
    placer(m, qui, "echoppe", (1, 1))
    m.joueur.update(salle="echoppe", position=[2, 1])
    regarder(m, qui, "joueur")
    regarder(m, "joueur", qui)
    percevoir_tous(m)


class TachePayeeTests(unittest.TestCase):
    """Un PNJ paie un autre pour une tâche dont il a besoin ; l'autre accepte selon ce que vaut une
    pièce pour lui et ce que la tâche lui coûte ; acceptée, elle devient son engagement, payé
    d'avance ; non faite à l'échéance, il doit le prix."""

    def fourneau_sans_bois(self):
        """Auberge (cas réel de ``entretenir-feu``) : le bois de la cuisine est brûlé, le fourneau
        baisse ; Mireille sait que Joss garde des fagots à l'étable, mais Joss garde sa dernière charge."""
        m = creer("auberge", 1985, "fixe")
        deplacer(m, "bois_cuisine", "cellier")
        m.objets["bois_cuisine"]["charges"] = 0
        sans(m, "bois_reserve")   # La réserve d'Odile (branche ``ressources``) est brûlée aussi.
        m.objets["fagots_etable"]["charges"] = 1
        m.objets["fourneau"]["combustible"] = 8
        croire(m, "mireille", "fagots_etable", "lieu", "etable", "savoir", salle="etable", case=None)
        return m

    def test_mireille_paie_qui_veut_bien_entretenir_le_fourneau(self):
        m = self.fourneau_sans_bois()
        # La tâche doit être faisable par un donneur : sa dernière charge reste
        # nécessaire à Joss, les deux autres peuvent entretenir le fourneau.
        m.objets["fagots_etable"]["charges"] = 3
        ensemble(m, "mireille", "joss", "cuisine")
        # Au prix réel du trajet, demander gratuitement devient préférable.
        # L'offre payée est ici l'action à éprouver, établie avant sa réalisation.
        self.assertEqual(engager(m, "mireille", "joss", {"objet": "fourneau", "allume": True}, 2), "accepte")
        chronique_, _ = executer(m, 40)
        m = recharger(m)
        textes = [c["texte"] for c in chronique_]
        id = "joss"
        # Payé d'avance ; la tâche faite, l'engagement est tenu et le fourneau rallumé de son bois.
        self.assertTrue(any(s["type"] == "tache_payee" and s["a"] == id for s in lire(m, "mireille")["memoire"]))
        self.assertTrue(any(s["type"] == "engagement_tenu" and s["pour"] == "mireille"
                            for s in lire(m, id)["memoire"]), textes)
        self.assertTrue(m.objets["fourneau"]["allume"])
        self.assertEqual(m.data.get("dettes", []), [])

    def test_trop_cher_pour_qui_une_piece_vaut_peu(self):
        # Le même marché, refusé : une pièce vaut moins que les secondes de travail d'Odile, la
        # tâche lui en coûte davantage.
        m = calme(creer("auberge", 1985, "fixe"), "odile", "mireille")
        m.data["finances_pnj"]["odile"] = 600
        m.objets["fourneau"]["combustible"] = 8   # Le fourneau baisse : chacun le voit en cuisine.
        ensemble(m, "mireille", "odile", "cuisine")
        self.assertEqual(engager(m, "mireille", "odile", {"objet": "fourneau", "allume": True}, 1), "cher")
        m = recharger(m)
        self.assertEqual(lire(m, "odile")["engagements"], [])
        self.assertEqual((bourse(m, "mireille"), bourse(m, "odile")), (4, 600))

    def test_la_tache_non_faite_a_l_echeance_est_due(self):
        # Une tâche acceptée et jamais faite : à l'échéance, le prix est dû, et rendu (Anselme est
        # honnête) quand ils se retrouvent ; Mireille cesse alors de compter sur lui.
        m = calme(creer("auberge", 1985, "fixe"), "anselme", "mireille")
        m.objets["fourneau"]["combustible"] = 8
        m.objets["bois_anselme"]["charges"] = 5   # Placement d'auteur : il a de quoi, sans toucher à sa réserve.
        ensemble(m, "mireille", "anselme", "cuisine")
        with patch.object(Monde, "d20", return_value=20):
            issue = engager(m, "mireille", "anselme", {"objet": "fourneau", "allume": True}, 2)
        self.assertEqual(issue, "accepte")
        self.assertEqual((bourse(m, "mireille"), bourse(m, "anselme")), (2, 32))
        from donjon.deliberation import tache_payee
        self.assertEqual(tache_payee(m, "mireille", {"objet": "fourneau", "allume": True}), "anselme")
        placer(m, "anselme", "chambre_chaude", (2, 2))
        percevoir_tous(m)
        lire(m, "anselme")["engagements"][0]["minute"] = -ENGAGEMENT_MAX - 1
        m, _ = vivre(recharger(m), 1)
        self.assertEqual([(d["de"], d["a"], d["montant"], d["quoi"]) for d in m.data["dettes"]],
                         [("anselme", "mireille", 2, "tache")])
        self.assertIsNone(tache_payee(m, "mireille", {"objet": "fourneau", "allume": True}))
        ensemble(m, "mireille", "anselme", "cuisine")
        m, _ = vivre(recharger(m), 1)
        self.assertEqual(m.data["dettes"], [])
        self.assertIn("Anselme rend 2 pièces à Mireille : le travail payé n'a pas été fait.", chronique(m))


class PretReclameTests(unittest.TestCase):
    """Le prêteur réclame son prêt échu au joueur comme à un PNJ ; l'emprunteur qui ne le rend pas
    perd sa confiance."""

    def lampe_pretee_au_joueur(self):
        """Mine : Gaspard a prêté sa lampe au joueur il y a plus de 240 minutes (placement d'auteur :
        le prêt, daté de l'échéance) ; il est près de lui."""
        from tests.support import presentes
        m = presentes(calme(creer("mine", 1985, "fixe"), "gaspard"), "gaspard")
        salle, (x, y) = m.joueur["salle"], m.joueur["position"]
        placer(m, "gaspard", salle, (x + 1, y))
        regarder(m, "gaspard", "joueur")
        regarder(m, "joueur", "gaspard")
        percevoir_tous(m)
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "joueur", "gaspard", "lampe_gaspard"), "remis")
        m.data["permissions"][0]["minute"] = -ENGAGEMENT_MAX
        return recharger(m)

    def test_gaspard_la_redemande_et_le_joueur_qui_la_garde_perd_sa_confiance(self):
        m = self.lampe_pretee_au_joueur()
        m, lignes = vivre(m, 2)
        self.assertIn("Gaspard te demande de lui rendre la lampe de Gaspard : il te l'a prêtée il y a longtemps.",
                      lignes)
        self.assertEqual(memoires(m, "gaspard", "pret_reclame")[-1]["objet"], "lampe_gaspard")
        m, lignes = vivre(m, 31)
        self.assertIn("Gaspard te reproche de ne pas lui avoir rendu la lampe de Gaspard.", lignes)
        self.assertIs(fiable(m, "gaspard", "joueur"), False)
        self.assertEqual(memoires(m, "gaspard", "pret_garde")[-1]["auteur"], "joueur")

    def test_rendue_a_temps_rien_ne_lui_est_reproche(self):
        m = self.lampe_pretee_au_joueur()
        # Le prêteur reste à portée : pas de recherche de nourriture pour Rémy/Odon.
        from tests.support import sans_souci
        sans_souci(m, "gaspard")
        m, _ = vivre(m, 2)
        from donjon.moteur import Moteur, proposition
        moteur = Moteur(m)
        moteur.executer(moteur.preparer(proposition("remettre", "lampe_gaspard", "gaspard")))
        m, lignes = vivre(recharger(m), 31)
        self.assertEqual((m.objets["lampe_gaspard"]["lieu"], m.data["permissions"]), ("gaspard", []))
        self.assertIsNot(fiable(m, "gaspard", "joueur"), False)
        self.assertFalse(memoires(m, "gaspard", "pret_garde"))

    def test_un_emprunteur_pnj_qui_la_garde_perd_aussi_sa_confiance(self):
        # La même règle entre PNJ : Rémy, dans le noir, garde la lampe échue que Gaspard lui réclame.
        from tests.test_echanges_argent import PretTests
        m = PretTests().lampe_empruntee()
        # Accomplir l'allumage avant la réclamation : trois minutes de vie
        # autonome peuvent désormais suffire à transmettre la lampe à un tiers.
        from donjon.pnj import _executer, _etape
        self.assertTrue(_executer(m, "remy", _etape("allumer", "lampe_gaspard", outil="briquet"), [], []))
        m = recharger(m)
        self.assertEqual(m.objets["lampe_gaspard"]["lieu"], "remy")
        self.assertTrue(m.objets["lampe_gaspard"]["allume"])
        m.data["permissions"][0]["minute"] = -ENGAGEMENT_MAX
        self.assertEqual(demander(m, "gaspard", "remy", "lampe_gaspard"), "necessaire")
        m = recharger(m)
        self.assertEqual(envers(m, "gaspard", "remy")["confiance"], 45)
        self.assertEqual(envers(m, "gaspard", "remy")["motifs"][-1]["type"], "pret_garde")
        self.assertEqual(memoires(m, "gaspard", "pret_garde")[-1]["auteur"], "remy")


class EnqueteTests(unittest.TestCase):
    """On demande à qui pourrait en avoir ce qu'on ne connaît pas (« as-tu du bois ? ») : il répond
    par ce qu'il a vraiment, et le demandeur l'apprend par ouï-dire."""

    def test_mireille_apprend_les_fagots_de_joss_et_les_achete(self):
        # Cas réel (limite de ``entretenir-feu``) : Mireille ne sait rien des fagots de Joss.
        m = creer("auberge", 1985, "fixe")
        deplacer(m, "bois_cuisine", "cellier")
        m.objets["bois_cuisine"]["charges"] = 0
        sans(m, "bois_reserve")   # La réserve d'Odile (branche ``ressources``) est brûlée aussi.
        m.objets["fourneau"]["combustible"] = 8
        m.data["finances_pnj"]["mireille"] = 0   # Placement d'auteur : sans le sou, elle ne peut rien payer.
        self.assertNotIn("fagots_etable", lire(m, "mireille")["croyances"])
        # Connaître un autre combustible de Joss ne dit pas s'il a de quoi chauffer le fourneau.
        self.assertIn("burette_huile", lire(m, "mireille")["croyances"])
        chronique_, _ = executer(m, 60)
        m = recharger(m)
        textes = [c["texte"] for c in chronique_]
        self.assertTrue(any(t.startswith("Mireille demande à Joss s'il a du bois") for t in textes), textes)
        # Elle l'a appris de lui, par ouï-dire (ce qu'elle a vu ensuite peut l'avoir précisé).
        self.assertIn({"de": "joss", "besoin": "chaleur", "objets": ["fagots_etable"]},
                      [{k: s[k] for k in ("de", "besoin", "objets")} for s in memoires(m, "mireille", "enquete")])
        self.assertTrue(any(t.startswith("Mireille demande une part des fagots de l'écurie à Joss") for t in textes), textes)

    @patch("donjon.social._constats", return_value=())
    def test_au_relais_gorm_apprend_les_planches_d_aubin(self, _constats):
        # On isole l'enquête et ses jets des confidences spontanées sur les états.
        # Autre cas de même nature, au Relais : le brasero est mort, Gorm (sans le sou) ignore les
        # planches d'Aubin ; il lui demande s'il a du bois, l'apprend, et en obtient une part.
        from tests.test_securite import dans_le_noir
        m = dans_le_noir(calme(relais(), "marchand", "brune", "ilse", "aubin"), "ilse", 75.0)
        m.data["finances_pnj"]["marchand"] = 0
        # Placement d'auteur : ni ses fagots ni la torche ne sont à sa portée, et les planches d'Aubin
        # sont rangées dans la conduite obscure. Gorm, qui choisit désormais à l'événement, irait sinon
        # à la torche, verrait le bois et n'aurait rien à demander (``deliberation-evenements``).
        for k in ("bois", "torche"):
            m.objets[k].update(lieu="chambre_cloche", position=[5, 1], position_salle="chambre_cloche")
        m.objets["planches"].update(lieu="echoppe", position=[8, 6], position_salle="echoppe")
        # La part promise comprend l'allumage : Aubin dispose de sa propre flamme.
        m.objets["briquet"]["lieu"] = "aubin"
        croire(m, "aubin", "planches", "lieu", "echoppe", "vu", salle="echoppe", case=[8, 6])
        self.assertNotIn("planches", lire(m, "marchand")["croyances"])
        from tests.test_tensions import attendre
        m.joueur.update(salle="antichambre", position=[3, 4], orientation="ouest")
        m.objets["lanterne"]["allume"] = False
        m, _ = attendre(recharger(m), 4)
        self.assertIn("Gorm demande à Aubin s'il a du bois (dit).", chronique(m))
        self.assertIn({"de": "aubin", "besoin": "chaleur", "objets": ["planches"]},
                      [{k: s[k] for k in ("de", "besoin", "objets")} for s in memoires(m, "marchand", "enquete")])
        self.assertIn("Gorm demande une part des planches de bac à Aubin (promis).", chronique(m))

    def test_rien_a_dire_et_la_mefiance(self):
        # Autre cas de même nature : qui n'a rien le dit ; qui se méfie ne répond pas.
        m = calme(creer("auberge", 1985, "fixe"), "tilo", "mireille", "joss")
        self.assertEqual(enqueter(m, "mireille", "tilo", "chaleur"), ("rien", []))
        self.assertEqual(enqueter(m, "mireille", "joss", "chaleur")[0], "dit")
        lier(m, "joss", "mireille", False, "vu")
        self.assertEqual(enqueter(m, "mireille", "joss", "chaleur")[0], "mefiance")

    def test_le_joueur_demande_s_il_a_du_bois(self):
        m = calme(creer("auberge", 1985, "fixe"), "joss")
        m.joueur.update(salle="etable", position=[5, 2])
        regarder(m, "joss", "joueur")
        regarder(m, "joueur", "joss")
        percevoir_tous(m)
        texte = "As-tu du bois ?"
        travail, rapport = preparer_parole(m, {
            "personnage": "joss", "replique": texte, "_intention": texte,
            "contenu": [{"type": "ressource", "sujet": "chaleur", "attribut": "", "valeur": ""}]})
        self.assertTrue(any("dit avoir les fagots de l'écurie dans l'étable" in f for f in rapport["faits"]),
                        rapport["faits"])
        _, rapport = preparer_parole(m, {"personnage": "joss", "replique": texte, "_intention": texte,
                            "contenu": [{"type": "ressource", "sujet": "bois", "attribut": "", "valeur": ""}]})
        self.assertTrue(any("dit avoir les fagots de l'écurie dans l'étable" in f for f in rapport["faits"]))


if __name__ == "__main__":
    unittest.main()
