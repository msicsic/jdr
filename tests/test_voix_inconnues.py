"""Les voix inconnues (branche ``voix-inconnues``) : trois limites de la branche ``voix``.

- Une demande d'une voix inconnue se juge comme celle d'un étranger vu : aucune confiance connue, une
  demande qui pèse moins (``voix.INCONNU``) ; ne rien savoir de qui demande (ni où il est, ni sa faim)
  ne rend pas la demande impossible. Ce qui la rendait « impossible » dans le cas relevé (la réserve
  noire de la mine) était la porte verrouillée de la réserve : la même demande d'une voix connue l'est
  aussi.
- La réplique d'une voix inconnue ne se nomme pas au-delà de ce que le moteur a établi et ne nomme
  que qui son locuteur connaît : le moteur sait qui parle (``voix.reel``) et ce qu'il sait
  (``voix.connait_nom``).
- Côté joueur : voir parler quelqu'un fait connaître sa voix, qu'il lui parle ou non (une réponse
  entre PNJ, une réplique que le MJ prête à un personnage qu'il voit) ; une voix à qui une autre
  s'adresse en la nommant, entendue dans le même échange, est « une voix qu'on appelle … » ; une
  voix qui dit son nom se dit ainsi. Le joueur répond à qui le hèle par le geste de réponse commun
  (``pnj.repondre_a``), sans le MJ : l'appelant le croit là.

Chaque cas vérifie l'état après rechargement, et ce que lit le joueur quand il est là.
"""
from donjon.emissions import pnj as emissions_pnj
import json
import unittest
from unittest.mock import patch

from donjon import lexique
from donjon.commandes import analyser as commande
from donjon.deliberation import _plan_pulsion
from donjon.echanges import PARTAGE, demander, foyer_de
from donjon.esprits import croire, lire, percevoir_tous
from donjon.monde import ErreurMonde, Monde
from donjon.narration import consigner, voix_inconnues
from donjon.operations import etape, sequence
from donjon.paroles import jet_persuasion, repond
from donjon.voix import INCONNU, connaitre, designation, nom_pour_joueur, retenir, se_nommer
from tests.support import calme
from tests.test_constater_rumeurs import ParlerALaVoixTests
from tests.test_parole_voix import gorm_derriere_la_porte
from tests.test_paroles import jouer, parole, reponse_pnj
from tests.test_paroles import relais as relais_pres_de_gorm
from tests.test_repli_et_appel import jouer as jouer_sans_mj
from tests.test_tensions import attendre, chronique, placer, recharger, relais
from tests.test_voix import VoixInconnueTests, auberge, gorm_et_une_voix, lieu_cru


def baraquement(salle="baraquement", voix_connue=True, eclaire=False):
    """Mine : Odon, affamé, demande sa part à Mathe (cas réel de la branche ``voix``). Mathe n'est pas
    prudente (elle ne demande pas « Qui va là ? »). Sans ``voix_connue``, elle n'a jamais entendu Odon
    et ne sait rien de lui ; ``eclaire`` : la lampe du baraquement allumée, elle le voit."""
    m = ParlerALaVoixTests("test_odon_demande_sa_part_a_mathe_dans_le_noir").baraquement_noir(salle)
    if not voix_connue:
        lire(m, "mathe")["voix"].remove("odon")
        lire(m, "mathe")["croyances"].pop("odon", None)
    lire(m, "mathe")["besoins"]["securite"] = 0.0
    if eclaire:
        m.objets["lampe_baraque"]["allume"] = True
    return recharger(m)


def part_servie(m):
    return "Mathe appelle Odon et lui donne une part des vivres de la cuisine." in chronique(m) or \
        "Mathe donne une part des vivres de la cuisine à Odon." in chronique(m)


class DemandeDUneVoixInconnueTests(unittest.TestCase):
    def test_cas_reel_une_voix_jamais_entendue_obtient_sa_part_comme_un_etranger_vu(self):
        """Mathe n'a jamais entendu Odon et ne sait rien de lui : dans le noir, au même jet, elle lui
        promet sa part puis la lui sert, comme à un inconnu qu'elle verrait ; sa demande pèse seulement
        ``INCONNU`` de plus."""
        noir, vu = baraquement(voix_connue=False), baraquement(voix_connue=False, eclaire=True)
        percevoir_tous(vu)
        self.assertEqual(jet_persuasion(noir, "mathe", "odon", PARTAGE)[1],
                         jet_persuasion(vu, "mathe", "odon", PARTAGE)[1] + INCONNU)
        for m in (noir, vu):
            with patch.object(Monde, "d20", return_value=20):
                for _ in range(3):
                    m, _ = attendre(m)
            self.assertIn("Odon demande une part des vivres de la cuisine à Mathe (promis).", chronique(m))
            self.assertTrue(part_servie(m))
            self.assertTrue(any(s["type"] == "engagement_tenu" and s["pour"] == "odon"
                                for s in lire(m, "mathe")["memoire"]))

    def test_la_reserve_verrouillee_rend_la_part_impossible_quelle_que_soit_la_voix(self):
        """Ce qui avait été relevé comme « une voix inconnue rend la demande impossible » : enfermée
        dans la réserve noire, Mathe ne peut atteindre le garde-manger ; une voix connue s'entend
        répondre la même chose."""
        for connue in (True, False):
            m = baraquement("reserve", voix_connue=connue)
            self.assertIsNone(_plan_pulsion(m, "mathe", {"objet": "vivres", "servir": "odon"}))
            # Éprouver cette demande, pas le choix autonome entre demander
            # la part et rechercher un autre fournisseur (226).
            from donjon.echanges import executer
            from donjon.planification import _etape
            with patch.object(Monde, "d20", return_value=20):
                self.assertFalse(executer(m, "odon", _etape("demander", "mathe", outil="vivres"), []))
            m = recharger(m)
            self.assertIn("Odon demande une part des vivres de la cuisine à Mathe (impossible).", chronique(m))

    def test_le_joueur_inconnu_de_gorm_dans_le_noir(self):
        """Même nature (Relais) : Gorm ne sait rien de Corvus (ni lieu, ni voix) ; la demande d'une
        part, au jet qui convainc, est promise, et Gorm retient la voix sans rien en croire de plus."""
        m = VoixInconnueTests().gorm_dans_le_noir()
        lire(m, "marchand")["croyances"].pop("joueur", None)
        m = recharger(m)
        reprise, _, entrees = jouer(m, "je demande à Gorm une part des vivres", [
            parole("Gorm, une part des vivres, s'il te plaît.", ("demande", "vivres", "", "")),
            reponse_pnj("Gorm grogne.")], jet=20)
        self.assertIn("Gorm, gardien du relais accepte de t'en donner une part : il te la servira là où sont "
                      "les vivres.", entrees[1]["faits"]["conversation_validee"]["faits"])
        gorm = lire(reprise, "marchand")
        self.assertIn({"objet": "vivres", "servir": "joueur"}, [x["condition"] for x in gorm["engagements"]])
        self.assertIn("joueur", gorm["voix_entendues"])
        self.assertNotIn("fiable", gorm["croyances"].get("joueur", {}))

    def test_le_bois_demande_va_au_feu_de_la_salle_d_ou_vient_la_voix(self):
        """Une part de bois demandée par le joueur entretient le feu de la salle d'où il demande (le
        fourneau de la cuisine), pas le premier feu que le donneur connaît (l'âtre) : comme pour un PNJ,
        qu'on le voie ou qu'on n'entende que sa voix."""
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        placer(m, "joss", "cuisine", [1, 1])
        m.joueur.update(salle="cuisine", position=[2, 2])
        m = recharger(m)
        self.assertEqual(foyer_de(m, "joss", "joueur"), "fourneau")
        with patch.object(Monde, "d20", return_value=20):
            self.assertEqual(demander(m, "joueur", "joss", "fagots_etable"), "promis")
        m = recharger(m)
        self.assertIn({"objet": "fourneau", "allume": True}, [x["condition"] for x in lire(m, "joss")["engagements"]])


def brune_voix_inconnue():
    """Relais, conduite basse dans le noir, les quatre PNJ : Corvus, près de Gorm, entend Brune sans
    connaître sa voix (voix_<n>)."""
    m = gorm_et_une_voix("brune")
    m.joueur.update(salle="echoppe", position=[1, 2])
    placer(m, "brune", "echoppe", (1, 3))
    m.data["entendus"] = ["brune"]
    m.data["connus"] = sorted({*m.data["connus"], "brune", "marchand"})
    retenir(m, "joueur", "brune")
    m = recharger(m)
    assert not m.visible("brune") and designation(m, "brune").startswith("voix_")
    return m


class RepliquesTests(unittest.TestCase):
    def obstacles(self, m, texte, alias=None):
        alias = alias or designation(m, "brune")
        faits = {"interlocuteurs": m.contexte()["interlocuteurs"]}
        return voix_inconnues(m, [{"locuteur": alias, "texte": texte}], faits)

    def test_elle_nomme_qui_elle_connait_jamais_elle_meme(self):
        m = brune_voix_inconnue()
        alias = designation(m, "brune")
        self.assertTrue(alias.startswith("voix_"))
        # Brune connaît Gorm et Ilse : les nommer ne dit rien de qui parle.
        self.assertEqual(self.obstacles(m, "Gorm garde les vivres ; Ilse dort à la chambre."), [])
        # Se nommer, ou se dire quelqu'un d'autre : seul le moteur le décide.
        self.assertEqual(len(self.obstacles(m, "Je suis Brune.")), 1)
        self.assertEqual(len(self.obstacles(m, "Brune n'a rien vu.")), 1)
        self.assertEqual(len(self.obstacles(m, "Je m'appelle Ilse.")), 1)
        self.assertEqual(len(self.obstacles(m, "Moi, c'est Gorm.")), 1)
        # Quelqu'un dont elle ne sait rien.
        m.objets["brune"]["connait_noms"].remove("aubin")
        lire(m, "brune")["croyances"].pop("aubin")
        lire(m, "brune")["voix"].remove("aubin")
        m = recharger(m)
        self.assertEqual(len(self.obstacles(m, "Aubin a faim.")), 1)
        # Une voix que le moteur ne relie à personne ne nomme rien de plus que ce qui est établi.
        inconnue = {"interlocuteurs": {"voix_9": {"nom": "une voix inconnue", "voix_inconnue": True}}}
        self.assertEqual(len(voix_inconnues(m, [{"locuteur": "voix_9", "texte": "Gorm dort."}], inconnue)), 1)

    def test_le_nom_de_corvus_seulement_s_il_le_lui_a_donne(self):
        m = brune_voix_inconnue()
        self.assertEqual(len(self.obstacles(m, "Corvus, c'est toi ?")), 1)
        # Corvus s'est nommé à cette voix dans le noir : elle sait son nom.
        se_nommer(m, "brune", "joueur", "joueur")
        m = recharger(m)
        self.assertEqual(self.obstacles(m, "Corvus, c'est toi ?"), [])

    def test_la_reponse_s_enregistre_et_se_relit_apres_rechargement(self):
        """La chaîne : une réplique de la voix qui nomme Gorm est consignée (le moteur sait qui l'a
        dite) ; une réplique où la voix se nomme est refusée, sans rien enregistrer."""
        m = brune_voix_inconnue()
        alias = designation(m, "brune")
        citation = "Gorm est aux vannes."
        faits = {"interlocuteurs": m.contexte()["interlocuteurs"]}

        def reponse(c):
            texte = f"La voix répond : « {c} »"
            ligne = {"portee_mecanique": "aucune", "indice": 0, "verdict": "parole", "sources": [], "locuteur": alias, "citation": c,
                     "entites": [], "comptes": [], "motif": ""}
            return {"texte": texte, "_audit": {"segments": [ligne], "faits": faits, "texte_initial": texte,
                                               "fondement": lexique.corpus("Gorm, la voix"),
                                               "fondement_paroles": lexique.corpus("Gorm, vannes")}}
        consigner(m, reponse(citation))
        m = recharger(m)
        self.assertEqual((emissions_pnj(m)[-1]["locuteur"], emissions_pnj(m)[-1]["texte"]),
                         ("brune", citation))
        self.assertNotIn("brune", m.data["voix_connues"])  # Il ne la voit pas : toujours une voix inconnue.
        with self.assertRaisesRegex(ErreurMonde, "Aucun changement enregistré"):
            consigner(m, reponse("Je suis Brune, et Gorm est aux vannes."))


class VoirParlerTests(unittest.TestCase):
    def test_voir_gorm_repondre_a_aubin_fait_connaitre_sa_voix(self):
        """Corvus, à la lumière, voit Aubin demander sa part à Gorm et Gorm lui répondre, sans qu'on
        lui parle : il connaît désormais leurs deux voix. Avant, seule la voix de qui demandait."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        # Sans secours spontané, Gorm demeure en vue pour répondre à Aubin.
        from tests.support import sans_souci
        sans_souci(m, "marchand", "ilse")
        m.joueur.update(salle="echoppe", position=[1, 2], orientation="nord")
        placer(m, "marchand", "echoppe", (1, 1))
        placer(m, "aubin", "echoppe", (2, 1))
        lire(m, "aubin")["besoins"]["faim"] = 90.0
        m = recharger(m)
        self.assertTrue(m.visible("aubin") and m.visible("marchand"))
        self.assertEqual(m.data["voix_connues"], [])
        m, texte = attendre(m)
        self.assertTrue(any(t.startswith("Aubin demande une part des vivres du refuge à Gorm")
                            or t.startswith("Aubin achète une part") for t in chronique(m)))
        self.assertIn("aubin", m.data["voix_connues"])
        self.assertIn("marchand", m.data["voix_connues"])

    def test_une_replique_du_mj_d_un_personnage_qu_il_voit(self):
        """Gorm, que Corvus voit, lui répond par la bouche du MJ : Corvus connaît sa voix ; dans le
        noir ensuite, il la reconnaît."""
        m = relais_pres_de_gorm()
        self.assertTrue(m.visible("marchand"))
        citation = "Les vivres sont au refuge."
        texte = f"Gorm répond : « {citation} »"
        faits = {"interlocuteurs": {"marchand": {"nom": "Gorm"}}}
        ligne = {"portee_mecanique": "aucune", "indice": 0, "verdict": "parole", "sources": [], "locuteur": "marchand", "citation": citation,
                 "entites": [], "comptes": [], "motif": ""}
        consigner(m, {"texte": texte, "_audit": {"segments": [ligne], "faits": faits, "texte_initial": texte,
                                                 "fondement": lexique.corpus("Gorm, vivres, refuge"),
                                                 "fondement_paroles": lexique.corpus("vivres refuge")}})
        m = recharger(m)
        self.assertIn("marchand", m.data["voix_connues"])
        m.objets["brasero"]["allume"] = False
        m.objets["lanterne"]["allume"] = False
        m = recharger(m)
        self.assertFalse(m.visible("marchand"))
        self.assertEqual(designation(m, "marchand"), "marchand")

    def test_une_voix_qui_dit_son_nom_se_dit_ainsi(self):
        """Mine, réserve noire : Mathe, inquiète, demande « Qui va là ? » à la voix d'Odon, qui répond
        « C'est Odon. » ; Corvus, dans le noir près d'eux, entend chaque voix dire ses mots : celle
        d'Odon se dit Odon, celle de Mathe reste une voix inconnue."""
        m = ParlerALaVoixTests("test_odon_demande_sa_part_a_mathe_dans_le_noir").baraquement_noir("reserve")
        lire(m, "mathe")["voix"].remove("odon")
        lire(m, "mathe")["croyances"].pop("odon", None)
        lire(m, "mathe")["besoins"]["securite"] = 60.0
        m.joueur.update(salle="reserve", position=[4, 1])
        m.data["visitees"] = sorted({*m.data["visitees"], "reserve"})
        # Contrôler la présentation avant l'évasion : une porte brisée peut ensuite
        # laisser entrer la lumière et rendre la personne visible à Corvus.
        from donjon.moteur import Moteur, proposition
        m, textes = recharger(m), []
        for _ in range(120):
            textes.append(Moteur(m).executer(Moteur(m).preparer(proposition("attendre", "1"))))
            m = recharger(m)
            if m.data["voix_entendues"].get("odon", {}).get("se_dit") == "odon":
                break
        texte = " ".join(textes)
        self.assertIn("Odon demande une part des vivres de la cuisine à Mathe (qui_va_la).", chronique(m))
        self.assertIn("une voix inconnue : « Qui va là ? »", texte)
        self.assertEqual(nom_pour_joueur(m, "odon"), "une voix qui se dit Odon")
        self.assertEqual(nom_pour_joueur(m, "mathe"), "une voix inconnue")
        self.assertEqual(m.data["voix_entendues"]["odon"]["se_dit"], "odon")


def gorm_hele_corvus(voix_connue=False):
    """Corvus au palier, devant la porte étanche fermée ; Gorm, à la salle des vannes, derrière elle,
    le cherche sans savoir où il est (intention placée d'autorité : aucun scénario ne fait encore
    chercher le joueur) : il parcourt la salle et l'appelle par son nom. Corvus attend, et entend le
    cri d'une voix qu'il ne connaît pas."""
    from donjon.esprits import esprit
    from donjon.planification import rejoindre
    m = gorm_derriere_la_porte()
    from donjon.noms import apprendre
    apprendre(m,'marchand','joueur')  # Placement d'auteur : il le cherche sous un nom déjà présenté.
    if voix_connue:
        connaitre(m, "marchand", "joueur")
    croire(m, "marchand", "joueur", "lieu", None, "essai", salle=None, case=None)
    for s in m.data["salles"]:
        lire(m, "marchand")["visites"][s] = 0 if s == "crypte" else 1
    etapes, _ = rejoindre(m, "marchand", "joueur")
    esprit(m, "marchand")["intention"] = {"but": {"type": "rejoindre", "qui": "joueur"}, "motif": "devoir",
                                          "plan": etapes, "depuis": m.data["minutes"], "attente": 0}
    m, texte = attendre(recharger(m))
    assert "Tu entends, à l'ouest, une voix inconnue appeler : « Corvus ? »" in texte, texte
    return m


class RepondreTests(unittest.TestCase):
    def test_formes(self):
        m = gorm_hele_corvus()
        for saisie in ("je réponds", "je lui réponds", "je réponds à Gorm", "je réponds à l'appel",
                       "je réponds : ici !", "je réponds « Ici ! »", "je crie « Ici ! »", "« Ici ! »",
                       "« Oui, je suis là ! »", "je réponds fort", "je crie ici", "répondre"):
            self.assertEqual(repond(m, saisie), "marchand", saisie)
        # Autre chose qu'une réponse : une parole, un autre nom, un cri, un appel.
        for saisie in ("je réponds que j'arrive", "« Ici, et j'ai faim ! »", "je réponds à Ilse", "je crie",
                       "j'appelle Gorm", "ici"):
            self.assertIsNone(repond(m, saisie), saisie)
        # Personne ne l'a appelé : « je réponds » n'est pas une réponse à un appel.
        self.assertIsNone(repond(gorm_derriere_la_porte(), "je réponds"))

    def test_cas_reel_corvus_repond_a_gorm_qui_le_hele(self):
        m = gorm_hele_corvus()
        self.assertIn("Gorm appelle : « Corvus ? »", chronique(m))
        reprise, sortie, appels = jouer_sans_mj(m, "je réponds", [], [])
        self.assertEqual(appels, [])  # Le geste du moteur, jamais une interprétation du MJ.
        self.assertIn("Tu réponds : « Ici, viens ! »", sortie)
        self.assertIn("Corvus répond : « Ici, viens ! »", chronique(reprise))
        # Gorm, qui ne connaît pas sa voix, le croit là sur sa parole.
        self.assertEqual(lieu_cru(reprise, "marchand", "joueur"), ("beffroi", "se_dit"))
        self.assertEqual(lire(reprise, "marchand")["voix_entendues"]["joueur"]["se_dit"], "joueur")

    def test_ici_entre_guillemets_d_une_voix_connue(self):
        """Même nature : Gorm connaît la voix de Corvus ; « « Ici ! » » juste après l'appel est la même
        réponse, et Gorm le sait là, sûr de lui."""
        m = gorm_hele_corvus(voix_connue=True)
        reprise, sortie, appels = jouer_sans_mj(m, "« Ici ! »", [], [])
        self.assertEqual(appels, [])
        self.assertIn("Tu réponds : « Ici, viens ! »", sortie)
        self.assertEqual(lieu_cru(reprise, "marchand", "joueur"), ("beffroi", "entendu"))

    def test_le_mj_ne_repond_qu_a_qui_vient_d_appeler(self):
        from donjon.moteur import Moteur
        sans_appel = gorm_derriere_la_porte()
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(sans_appel).preparer(sequence(etape("emettre_son", "marchand", methode="repondre")))
        self.assertIn("Personne ne vient de t'appeler", str(refus.exception))
        self.assertIn("reçu cible « marchand »", refus.exception.attendu)
        m = gorm_hele_corvus()
        with self.assertRaises(ErreurMonde) as refus:
            Moteur(m).preparer(sequence(etape("emettre_son", "ilse", methode="repondre")))
        self.assertIn("Ce n'est pas cette voix", str(refus.exception))
        self.assertIn(designation(m, "marchand"), refus.exception.attendu)
        self.assertIn("reçu « ilse »", refus.exception.attendu)
        # La forme reconnue donne le geste, sous le nom que Corvus connaît à l'appelant.
        self.assertEqual(commande(m, "je réponds")["etapes"][0]["cible"], designation(m, "marchand"))
        self.assertNotIn("marchand", json.dumps(commande(m, "je réponds")))


if __name__ == "__main__":
    unittest.main()
