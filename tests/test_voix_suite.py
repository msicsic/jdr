"""La suite des voix (branche ``voix-suite``) : quatre limites des branches ``voix``, ``parole-voix``,
``voix-inconnues`` et ``ouie-commune``.

- Un PNJ retient le nom de qui il sait être lui, quand il l'entend se nommer ou qu'une autre voix
  l'appelle ainsi (``voix.apprendre_nom``, ``noms`` de son esprit) ; une voix qui s'était dite X et
  qu'il reconnaît ensuite comme celle de X lui laisse ce nom.
- Le lien « une voix qu'on appelle Gorm » s'apprend par la même règle pour le joueur et les PNJ
  (``voix.lier``) : une voix à qui une autre s'adresse en la nommant, entendue dans le même échange.
- L'appelé se tourne vers l'appelant s'il le verrait ainsi, même au-delà d'un seuil ; qui attend
  d'être rejoint se tourne vers l'appelant qu'il entend approcher, dès qu'il peut le voir.
- Le MJ reçoit d'une voix inconnue le genre où elle parle d'elle-même, sans rien qui dise qui c'est.

Chaque cas vérifie l'état après rechargement, et ce que lit le joueur ou ce que reçoit le MJ.
"""
import json
import unittest

from donjon.deliberation import attendre_l_appelant
from donjon.esprits import connaitre, croire, lire, percevoir_tous, percoit
from donjon.narration import voix_inconnues
from donjon.paroles import esprits_interlocuteurs
from donjon.pnj import appeler, heler
from donjon.social import faire_entendre
from donjon.voix import connait_nom, designation, nom_pour_joueur, retenir
from tests.support import calme
from tests.test_ouie_commune import faire
from tests.test_paroles import jouer, parole, reponse_pnj
from tests.test_paroles import relais as relais_pres_de_gorm
from tests.test_temps_etat import decouper, etat_pnj
from tests.test_tensions import attendre, chronique, placer, recharger, relais
from tests.test_voix import VoixInconnueTests
from tests.test_voix_inconnues import brune_voix_inconnue


def voix_de_gorm(m):
    """Ce que le contrôle narratif reçoit d'une voix inconnue que le moteur sait être Gorm."""
    retenir(m, "joueur", "marchand")
    alias = designation(m, "marchand")
    assert alias.startswith("voix_"), alias
    return alias, {"interlocuteurs": {alias: {"nom": "une voix inconnue", "voix_inconnue": True}}}


class NomRetenuTests(unittest.TestCase):
    def test_cas_reel_gorm_voit_corvus_se_nommer_et_retient_son_nom(self):
        """Limite de ``voix-inconnues`` : Gorm voit Corvus lui dire « C'est Corvus » ; il le sait déjà
        là (« connu »), et rien n'enregistrait son nom. Dans le noir ensuite, sa voix, que Corvus ne
        connaît pas, ne pouvait pas l'appeler Corvus. Désormais il le retient."""
        m = relais_pres_de_gorm()
        self.assertTrue(percoit(m, "marchand", "joueur"))
        self.assertFalse(connait_nom(m, "marchand", "joueur"))
        reprise, _, _ = jouer(m, "je lui dis : c'est Corvus", [
            parole("C'est Corvus.", ("nom", "joueur", "", "")), reponse_pnj("Gorm hoche la tête.")])
        self.assertEqual(lire(reprise, "marchand")["noms"], ["joueur"])
        self.assertNotIn("joueur", lire(reprise, "marchand")["voix_entendues"])
        # Dans le noir, plus tard : la voix de Gorm peut nommer Corvus ; une autre voix non.
        reprise.objets["brasero"]["allume"] = False
        reprise.objets["lanterne"]["allume"] = False
        reprise.data["minutes"] += 30
        reprise = recharger(reprise)
        alias, faits = voix_de_gorm(reprise)
        reprise = recharger(reprise)
        self.assertTrue(connait_nom(reprise, "marchand", "joueur"))
        self.assertEqual(voix_inconnues(reprise, [{"locuteur": alias, "texte": "Corvus, approche."}], faits), [])
        self.assertFalse(connait_nom(reprise, "ilse", "joueur"))

    def test_meme_nature_la_voix_qui_se_disait_corvus_reconnue(self):
        """Gorm croit sur parole une voix qui se dit Corvus, dans le noir ; à la lumière, il voit
        Corvus parler : c'était bien lui. Avant, la voix inconnue oubliée emportait le nom avec elle
        (la croyance passait du ouï-dire au constat, et plus rien ne disait qu'il savait son nom)."""
        m = VoixInconnueTests().gorm_dans_le_noir()
        reprise, _, _ = jouer(m, "je lui dis : c'est Corvus", [
            parole("C'est Corvus.", ("nom", "joueur", "", "")), reponse_pnj("Gorm grogne.")])
        self.assertEqual(lire(reprise, "marchand")["voix_entendues"]["joueur"]["se_dit"], "joueur")
        reprise.objets["brasero"]["allume"] = True
        reprise = recharger(reprise)
        reprise, _, _ = jouer(reprise, "je dis à Gorm : bonsoir", [
            parole("Bonsoir.", personnage="marchand"), reponse_pnj("Gorm grogne.")])
        gorm = lire(reprise, "marchand")
        self.assertIn("joueur", gorm["voix"])
        self.assertNotIn("joueur", gorm["voix_entendues"])
        self.assertEqual(gorm["noms"], ["joueur"])
        self.assertTrue(connait_nom(reprise, "marchand", "joueur"))

    def test_voir_appeler_corvus_par_son_nom(self):
        """Ilse voit Corvus ; une voix qu'elle ne connaît pas (Gorm, dans l'ombre) l'appelle « Corvus ? »
        et il répond « Ici ! » : elle sait désormais son nom."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[1, 1], orientation="est")
        placer(m, "ilse", "antichambre", (4, 1))
        m.objets["ilse"]["orientation"] = "ouest"
        placer(m, "marchand", "echoppe", (1, 1))
        lire(m, "ilse")["voix"].remove("marchand")
        percevoir_tous(m)
        self.assertTrue(percoit(m, "ilse", "joueur"))
        heler(m, "marchand", "joueur", [])
        m = recharger(m)
        reprise, sortie, appels = jouer(m, "je réponds", [])
        self.assertEqual(appels, [])
        self.assertIn("Corvus répond : « Ici ! »", chronique(reprise))
        self.assertIn("joueur", lire(reprise, "ilse")["noms"])
        self.assertTrue(connait_nom(reprise, "ilse", "joueur"))


def deux_voix_dans_le_noir():
    """Relais, conduite basse dans le noir : Corvus près de Gorm, dont il connaît la voix ; Ilse à
    trois cases, qui ne connaît ni la voix de Gorm ni celle de Corvus. Brune et Aubin sont loin."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    m.objets["brasero"]["allume"] = False
    m.objets["lanterne"]["allume"] = False
    m.joueur.update(salle="echoppe", position=[1, 2], orientation="nord")
    placer(m, "marchand", "echoppe", (1, 1))
    placer(m, "ilse", "echoppe", (4, 2))
    placer(m, "brune", "chambre_cloche", (2, 2))
    placer(m, "aubin", "chambre_cloche", (4, 2))
    lire(m, "ilse")["voix"].remove("marchand")
    connaitre(m, "joueur", "marchand")
    m.data["connus"] = sorted({*m.data["connus"], "marchand"})
    percevoir_tous(m)
    m = recharger(m)
    assert not m.visible("marchand")
    assert not percoit(m, "ilse", "marchand") and not percoit(m, "ilse", "joueur")
    return m


class VoixAppeleeTests(unittest.TestCase):
    def test_cas_reel_deux_voix_inconnues_qui_se_nomment(self):
        """Ilse, dans le noir, entend une voix appeler « Corvus ? », puis une autre voix répondre
        « Gorm, je suis là. » à la première. Par la règle du joueur (``voix.lier``), l'une est « la voix
        qu'on appelle Corvus », l'autre « la voix qu'on appelle Gorm » : des ouï-dire, jamais une
        identité. Avant, seul le joueur l'apprenait ainsi."""
        m = deux_voix_dans_le_noir()
        heler(m, "marchand", "joueur", [])  # Gorm cherche Corvus dans le noir (placement d'auteur).
        m.data["entendus"] = ["marchand"]  # Ce que Corvus a entendu pendant son dernier geste.
        m = recharger(m)
        reprise, sortie, _ = jouer(m, "« Gorm, je suis là. »", [
            parole("Gorm, je suis là.", personnage="marchand"), reponse_pnj("Gorm grogne.")])
        self.assertIn("Tu dis à Gorm", sortie)
        ilse = lire(reprise, "ilse")
        self.assertEqual(ilse["voix_entendues"]["joueur"]["appelee"], "joueur")
        self.assertEqual(ilse["voix_entendues"]["marchand"]["appelee"], "marchand")
        self.assertIsNone(ilse["voix_entendues"]["joueur"]["se_dit"])
        # Un ouï-dire, pas une identité : elle ne reconnaît pas ces voix, mais sait le nom de Corvus.
        self.assertNotIn("marchand", ilse["voix"])
        self.assertTrue(connait_nom(reprise, "ilse", "joueur"))
        self.assertNotIn("joueur", ilse["noms"])

    def test_meme_nature_entre_pnj_le_nom_dit_apres_la_voix(self):
        """Ilse, dans le noir, entend une voix parler à une autre (Gorm à Aubin), puis cette autre
        héler la première par son nom (« Gorm ? ») : la voix qui a parlé d'abord est « la voix qu'on
        appelle Gorm ». Corvus, au même endroit et qui ne connaît aucune de ces voix, l'apprend de
        même : une seule règle."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["brasero"]["allume"] = False
        m.objets["lanterne"]["allume"] = False
        m.joueur.update(salle="echoppe", position=[1, 5], orientation="nord")
        placer(m, "ilse", "echoppe", (4, 2))
        placer(m, "marchand", "echoppe", (1, 1))
        placer(m, "aubin", "echoppe", (6, 4))
        for x in ("marchand", "aubin"):
            if x in lire(m, "ilse")["voix"]:
                lire(m, "ilse")["voix"].remove(x)
        lire(m, "aubin")["voix"].remove("marchand")
        percevoir_tous(m)
        m = recharger(m)
        lignes = []
        faire_entendre(m, "marchand", "aubin", "Gorm : « Qui fait ce bruit ? »", [], lignes)
        appeler(m, "aubin", "marchand", lignes)
        m = recharger(m)
        self.assertIn("Aubin appelle : « Gorm ? »", chronique(m))
        self.assertEqual(lire(m, "ilse")["voix_entendues"]["marchand"]["appelee"], "marchand")
        self.assertNotIn("marchand", lire(m, "ilse")["voix"])
        self.assertEqual(m.data["voix_entendues"]["marchand"]["appelee"], "marchand")
        self.assertEqual(nom_pour_joueur(m, "marchand"), "une voix qu'on appelle Gorm")

    def test_rien_d_une_voix_qu_il_connait(self):
        """Même échange, mais Ilse connaît la vraie voix de Gorm : rien de nouveau, ce n'est pas un
        ouï-dire qui la renseigne."""
        m = deux_voix_dans_le_noir()
        lire(m, "ilse")["voix"].append("marchand")
        heler(m, "marchand", "joueur", [])
        m.data["entendus"] = ["marchand"]
        m = recharger(m)
        reprise, _, _ = jouer(m, "« Gorm, je suis là. »", [
            parole("Gorm, je suis là.", personnage="marchand"), reponse_pnj("Gorm grogne.")])
        self.assertNotIn("marchand", lire(reprise, "ilse")["voix_entendues"])
        self.assertEqual(lire(reprise, "ilse")["voix_entendues"]["joueur"]["appelee"], "joueur")


class VersLAppelantTests(unittest.TestCase):
    def appele_pres_du_seuil(self):
        """Gorm, dans la conduite, tout près du passage vers le refuge mais à côté de lui ; Corvus,
        au refuge éclairé, à l'écart de l'axe du passage : tourné vers le seuil, Gorm ne le verrait pas ;
        tourné vers lui, si."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="antichambre", position=[5, 6], orientation="nord")
        placer(m, "marchand", "echoppe", (8, 2))
        m.objets["marchand"]["orientation"] = "ouest"
        percevoir_tous(m)
        self.assertFalse(percoit(m, "marchand", "joueur"))
        return recharger(m)

    def test_cas_reel_hele_d_une_autre_salle_il_se_tourne_vers_l_appelant(self):
        """Limite de ``ouie-commune`` : appelé d'une autre salle, il se tournait vers le seuil par où
        arrive la voix, pas vers l'appelant qu'il aurait vu par le passage."""
        m = self.appele_pres_du_seuil()
        texte = faire(m, "j'appelle Gorm")
        m = recharger(m)
        self.assertIn("Gorm, gardien du relais se tourne vers la voix qui l'appelle.", chronique(m))
        self.assertEqual(m.objets["marchand"]["orientation"], "sud-est")
        self.assertTrue(percoit(m, "marchand", "joueur"))
        self.assertEqual(lire(m, "marchand")["croyances"]["joueur"]["lieu"]["source"], "vu")
        # Il l'a vu crier son nom : il connaît sa voix, et sait que c'est lui.
        self.assertIn("joueur", lire(m, "marchand")["voix"])
        self.assertIn("répondre : « Ici ! »", texte)

    def test_hors_de_vue_du_passage_rien_de_plus(self):
        """L'appelant qu'il ne verrait pas en se tournant (hors de l'axe du passage) : la règle d'avant,
        le seuil, qu'il a déjà sous les yeux à côté de lui ; il ne se tourne pas."""
        m = self.appele_pres_du_seuil()
        m.joueur.update(position=[2, 1])
        m = recharger(m)
        faire(m, "j'appelle Gorm")
        m = recharger(m)
        self.assertEqual(m.objets["marchand"]["orientation"], "ouest")
        self.assertFalse(percoit(m, "marchand", "joueur"))

    def attend_aubin(self):
        """Gorm a répondu à l'appel d'Aubin et l'attend dans la conduite, tourné vers l'ouest ; Aubin,
        au refuge éclairé, vient vers lui dans l'axe du passage."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.joueur.update(salle="chambre_cloche", position=[3, 3], orientation="nord")
        placer(m, "marchand", "echoppe", (6, 3))
        m.objets["marchand"]["orientation"] = "ouest"
        placer(m, "aubin", "antichambre", (6, 3))
        m.objets["aubin"]["orientation"] = "ouest"
        percevoir_tous(m)
        attendre_l_appelant(m, "marchand", "aubin")
        croire(m, "aubin", "marchand", "lieu", "echoppe", "entendu", salle="echoppe", case=None)
        lire(m, "aubin")["besoins"]["faim"] = 90.0
        return m

    def test_qui_attend_se_tourne_vers_l_appelant_qui_approche(self):
        """Même nature : il entend l'appelant approcher dans la salle voisine ; dès qu'il le verrait par
        le passage, il se tourne vers lui, au lieu d'attendre qu'il soit sur lui pour se retourner au
        bruit. Le même laps, d'un bloc ou découpé et rechargé, donne le même monde."""
        m, _ = attendre(recharger(self.attend_aubin()))
        textes = chronique(m)
        tourne = textes.index("Gorm, gardien du relais se tourne vers Aubin, qui l'avait hélé.")
        self.assertLess(tourne, textes.index("Gorm retrouve Aubin, qui l'avait hélé."))
        self.assertLess(tourne, textes.index("Aubin, vieux passeur passe dans : Conduite basse."))
        # Jusqu'aux retrouvailles (ensuite, il le sert et marche devant lui : ses pas peuvent le faire
        # se retourner, ce qui est une autre affaire).
        avant = textes[:textes.index("Gorm retrouve Aubin, qui l'avait hélé.")]
        self.assertNotIn("Gorm, gardien du relais se retourne au bruit.", avant)
        d_un_bloc, morcele = decouper(self.attend_aubin, 2)
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))


class GenreDeLaVoixTests(unittest.TestCase):
    def test_cas_reel_le_mj_sait_si_la_voix_parle_au_feminin(self):
        """Vu avec Luna (branche ``voix-inconnues``) : la voix de Gorm, inconnue de Corvus, disait « Je
        ne suis pas convaincue ». Le MJ reçoit le genre où la voix parle d'elle-même ; rien de plus."""
        m = VoixInconnueTests().gorm_dans_le_noir()
        m.data["voix_connues"] = []
        retenir(m, "joueur", "marchand")
        m = recharger(m)
        alias = designation(m, "marchand")
        self.assertTrue(alias.startswith("voix_"))
        contexte = m.contexte()
        self.assertEqual(contexte["interlocuteurs"][alias]["genre"], "masculin")
        esprits = esprits_interlocuteurs(m, ["marchand"])
        self.assertEqual(esprits[alias]["genre"], "masculin")
        texte = json.dumps([contexte["interlocuteurs"], esprits], ensure_ascii=False)
        self.assertNotIn("marchand", texte)
        self.assertNotIn("Gorm", texte)

    def test_meme_nature_la_voix_de_brune(self):
        m = brune_voix_inconnue()
        alias = designation(m, "brune")
        self.assertEqual(m.contexte()["interlocuteurs"][alias]["genre"], "féminin")
        self.assertNotIn("brune", json.dumps(m.contexte()["interlocuteurs"]).lower())


if __name__ == "__main__":
    unittest.main()
