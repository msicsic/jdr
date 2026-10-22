"""Le temps fin sans état caché : tout ce dont dépend la suite est dans ``data``, de sorte que le
même laps de temps, découpé autrement par le joueur ou interrompu par un rechargement, donne le
même monde ; les bruits sont datés à l'instant ; un interlocuteur est un personnage que le joueur
perçoit ; un seul registre des gestes en cours, joueur compris, jusqu'à leur instant de fin."""

from tests.support import relation
import copy
import unittest
from unittest.mock import patch

import donjon.pnj as P
from donjon.commandes import analyser
from donjon.defi import nouveau_defi
from donjon.dialogues import interlocuteurs
from donjon.esprits import connaitre, esprit, lire
from donjon.faits_locaux import catalogue
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur, proposition
from donjon.operations import etape, sequence
from donjon.ouie import retentir
from donjon.paroles import preparer_parole
from donjon.spatial import installer
from donjon.temps import MINUTE, instant
from tests.support import calme, refusee, regarder
from tests.test_tensions import placer, recharger, relais


def faire(m, commande):
    moteur = Moteur(m)
    return moteur.executer(moteur.preparer(analyser(m, commande)))


def plan(operation, cible="", outil="", lieu="", condition=""):
    return {"operation": operation, "cible": cible, "outil": outil, "lieu": lieu, "condition": condition}


def intention(m, id, *etapes, but="manger", motif="faim"):
    lire(m, id)["intention"] = {"but": {"type": but}, "motif": motif, "depuis": 0, "attente": 0,
                                "plan": list(etapes)}


def etat_pnj(m):
    """Ce que le monde retient des PNJ : où ils sont, ce qu'ils pensent, ce qu'ils ont fait."""
    ids = ("marchand", "brune", "ilse", "aubin")
    return {"corps": {id: {k: m.objets[id].get(k) for k in ("lieu", "position", "orientation")} for id in ids},
            "esprits": copy.deepcopy({id: m.data["esprits"][id] for id in ids}),
            "objets": {id: (o["lieu"], o.get("position"), o.get("ouverte"), o.get("verrouillee"), o.get("portions"))
                       for id, o in m.objets.items() if o["type"] != "personnage"},
            "chronique": copy.deepcopy(m.data.get("chronique", [])),
            "gestes_en_cours": copy.deepcopy(m.data.get("gestes_en_cours", [])),
            "jets": m.data["jets"], "instant": instant(m)}


def decouper(scene, minutes, recharger_tous=25):
    """Le même laps : une attente d'un bloc (la proposition sans durée, que rien n'interrompt), puis
    une suite de rotations du joueur, rechargées en route."""
    d_un_bloc = scene()
    while d_un_bloc.data["minutes"] < minutes:
        Moteur(d_un_bloc).executer(Moteur(d_un_bloc).preparer(proposition("attendre")))
    morcele, n = scene(), 0
    while instant(morcele) < instant(d_un_bloc):
        faire(morcele, "tourner sud" if n % 2 == 0 else "tourner nord")
        n += 1
        if n % recharger_tous == 0:
            morcele = recharger(morcele)
    return d_un_bloc, morcele


def brune_affamee():
    """Brune veut crocheter la réserve sans témoin ; le joueur est loin, dans la galerie."""
    m = nouveau_defi(depart="fixe")
    installer(m)
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("ilse", "aubin")):
        placer(m, id, "crypte", (2 + n, 3))
    m.objets["crochets"]["lieu"] = "brune"
    placer(m, "brune", "antichambre", (7, 3))
    m.objets["brune"]["orientation"] = "est"
    lire(m, "brune")["besoins"]["faim"] = 0.9
    refusee(m)
    intention(m, "brune", plan("crocheter", "reserve", "crochets", condition="sans_temoin"))
    m.joueur.update(salle="chambre_cloche", position=[3, 7], orientation="nord")
    return m


def relais_libre():
    m = nouveau_defi(depart="fixe")
    installer(m)
    m.joueur.update(salle="chambre_cloche", position=[3, 7], orientation="nord")
    return m


class DecoupageTests(unittest.TestCase):
    def test_un_geste_sans_temoin_ne_depend_pas_du_decoupage(self):
        # Cas réel : en rotations de 2 s, Brune refaisait un tour d'horizon à chaque action du
        # joueur et ne crochetait jamais.
        d_un_bloc, morcele = decouper(brune_affamee, 5)
        self.assertIn("Brune, batelière évacuée s'acharne sur la serrure de la réserve de vivres.",
                      [c["texte"] for c in morcele.data["chronique"]])
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))

    def test_la_vie_du_relais_ne_depend_pas_du_decoupage(self):
        # Autre cas de même nature : quatre PNJ livrés à eux-mêmes, qui se voient les uns les
        # autres pendant que le joueur, loin, se tourne sur place.
        d_un_bloc, morcele = decouper(relais_libre, 5)
        self.assertGreater(len(morcele.data["chronique"]), 10)
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))

    def test_un_achat_et_un_pret_ne_dependent_pas_du_decoupage(self):
        # Ilse, refusée, achète sa part ; Aubin a emprunté la clé de Gorm et la lui rendra : bourses,
        # prêts et paroles de rendre sont dans ``data``.
        def scene():
            m = calme(relais_libre(), "marchand", "brune", "ilse", "aubin")
            lire(m, "ilse")["besoins"]["faim"] = 85.0
            refusee(m, "ilse")
            m.data["finances_pnj"]["ilse"] = 8
            placer(m, "aubin", "echoppe", (2, 1))
            from donjon.echanges import remettre
            remettre(m, "marchand", "aubin", "cle_reserve")
            return m
        d_un_bloc, morcele = decouper(scene, 10)
        self.assertIn("Ilse achète une part des vivres du refuge à Gorm pour 2 pièces (vendu).",
                      [c["texte"] for c in morcele.data["chronique"]])
        self.assertIn("Aubin rend la clé de la réserve à Gorm (rendu).", [c["texte"] for c in morcele.data["chronique"]])
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))
        self.assertEqual((d_un_bloc.data["finances_pnj"], d_un_bloc.data["permissions"]),
                         (morcele.data["finances_pnj"], morcele.data["permissions"]))

    def test_le_dernier_tour_d_horizon_est_dans_son_esprit(self):
        m = brune_affamee()
        tours = []
        original = P.tour_d_horizon
        with patch.object(P, "tour_d_horizon", side_effect=lambda monde, id: tours.append(id) or original(monde, id)):
            faire(m, "tourner sud")
            balayage = copy.deepcopy(esprit(m, "brune")["balayage"])
            m = recharger(m)
            self.assertEqual(lire(m, "brune")["balayage"], balayage)
            self.assertEqual((balayage["salle"], balayage["case"]), ("antichambre", [7, 3]))
            faire(m, "tourner nord")
        self.assertEqual(tours, ["brune"])  # Un seul tour, d'une action du joueur à l'autre.

    def test_un_ancien_esprit_recoit_son_tour_d_horizon(self):
        data = copy.deepcopy(brune_affamee().data)
        for e in data["esprits"].values():
            e.pop("balayage")
        self.assertIsNone(lire(Monde(data), "brune")["balayage"])


def voix_d_aubin(monde, minutes, lignes, dixiemes, original=P._avancer):
    """Pendant le geste du joueur, Aubin, dans son dos, marmonne."""
    resultat = original(monde, minutes, lignes, dixiemes)
    retentir(monde, "aubin", "dire", texte="Aubin marmonne.")
    return resultat


def aubin_dans_le_dos():
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    m.joueur.update(salle="antichambre", position=[6, 3], orientation="est")
    for n, id in enumerate(("marchand", "brune", "ilse")):
        placer(m, id, "crypte", (2 + n, 3))
    placer(m, "aubin", "antichambre", (1, 3))     # cinq cases derrière lui, immobile et muet
    m.objets["aubin"]["orientation"] = "nord"
    # Placement d'auteur : Corvus a déjà vu Aubin, il connaît sa voix (``esprits.connait``).
    connaitre(m, "joueur", "aubin")
    return recharger(m)


class BruitsTests(unittest.TestCase):
    def entendre(self, m, commande):
        with patch.object(P, "_avancer", voix_d_aubin):
            return faire(m, commande)

    def test_une_voix_pendant_une_rotation_sans_minute_franchie_s_entend(self):
        m = aubin_dans_le_dos()
        m.data["dixiemes"] = 100
        self.assertFalse(m.visible("aubin"))
        texte = self.entendre(m, "tourner nord")
        self.assertEqual((m.data["minutes"], m.data["dixiemes"]), (0, 110))
        self.assertIn("Tu entends, ", texte)
        self.assertIn("Aubin marmonne.", texte)
        m = recharger(m)
        self.assertEqual(m.data["bruits"][-1]["instant"], 110)
        # Entendu une fois : l'action suivante ne le redit pas.
        self.assertNotIn("Aubin marmonne", faire(m, "tourner sud"))

    def test_une_voix_pendant_un_pas_s_entend(self):
        m = aubin_dans_le_dos()
        m.data["dixiemes"] = 300
        texte = self.entendre(m, "pas est")
        self.assertEqual(m.joueur["position"], [7, 3])
        self.assertEqual(m.data["minutes"], 0)
        self.assertIn("Aubin marmonne.", texte)

    def test_les_bruits_des_anciennes_parties_sont_passes(self):
        data = copy.deepcopy(aubin_dans_le_dos().data)
        data["minutes"] = 4
        data["bruits"] = [{"minute": 3, "pnj": "aubin", "salle": "antichambre", "nature": "voix", "intensite": 2,
                           "texte": "Aubin marmonne.", "cites": []},
                          {"instant": 3 * MINUTE, "pnj": "aubin", "salle": "antichambre", "nature": "voix",
                           "intensite": 2, "texte": "Aubin marmonne.", "cites": []}]
        m = Monde(data)
        # Ils ne disent pas ce qui en parvenait au joueur ; d'avant son geste, ils ne lui parviennent plus.
        self.assertEqual(m.data["bruits"], [])
        self.assertNotIn("Aubin marmonne", faire(m, "tourner nord"))


class InterlocuteursTests(unittest.TestCase):
    def test_un_pnj_muet_dans_le_dos_n_est_pas_un_interlocuteur(self):
        m = aubin_dans_le_dos()
        self.assertFalse(m.visible("aubin"))
        contexte = m.contexte()
        self.assertNotIn("aubin", contexte["interlocuteurs"])
        self.assertNotIn("aubin", [o["id"] for o in contexte["objets_perceptibles"]])
        self.assertNotIn("aubin", catalogue(m)["locuteurs"])
        with self.assertRaises(ErreurMonde):
            preparer_parole(m, {"personnage": "aubin", "replique": "Qui est là ?", "contenu": []})

    def test_un_pnj_entendu_de_pres_devient_interlocuteur(self):
        m = aubin_dans_le_dos()
        with patch.object(P, "_avancer", voix_d_aubin):
            faire(m, "tourner nord")
        self.assertFalse(m.visible("aubin"))
        m = recharger(m)
        self.assertEqual(m.data["entendus"], ["aubin"])
        self.assertIn("aubin", m.contexte()["interlocuteurs"])
        self.assertIn("aubin", catalogue(m)["locuteurs"])
        # Le geste suivant, il se tait : il n'est plus perçu.
        faire(m, "tourner est")
        self.assertNotIn("aubin", recharger(m).contexte()["interlocuteurs"])

    def test_un_pnj_devant_lui_dans_le_noir_n_est_pas_un_interlocuteur(self):
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        m.objets["lanterne"]["allume"] = False
        m.joueur.update(salle="beffroi", position=[1, 3], orientation="est")
        for n, id in enumerate(("marchand", "brune", "ilse")):
            placer(m, id, "crypte", (2 + n, 3))
        placer(m, "aubin", "beffroi", (3, 3))
        m = recharger(m)
        self.assertFalse(m.visible("aubin"))
        self.assertNotIn("aubin", m.contexte()["interlocuteurs"])
        self.assertNotIn("aubin", catalogue(m)["locuteurs"])


def gorm_part_vers_l_ouest():
    """Gorm, au refuge, regarde vers l'est ; le joueur, arrivé dans son dos, est près de son
    marteau ; Gorm va se mettre en route vers l'échoppe, à l'ouest, au milieu du geste du joueur."""
    m = nouveau_defi(depart="fixe")
    installer(m)
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    placer(m, "marchand", "antichambre", (5, 5))
    regarder(m, "marchand", [8, 5])
    m.objets["marteau"].update(proprietaire="marchand", lieu="antichambre", position=[3, 5],
                               position_salle="antichambre")
    m.joueur.update(salle="antichambre", position=[2, 5], orientation="est")
    m.objets["lanterne"]["allume"] = False
    for n, id in enumerate(("brune", "ilse", "aubin")):
        placer(m, id, "crypte", (2 + n, 3))
    intention(m, "marchand", plan("aller", lieu="echoppe"), but="rejoindre", motif="devoir")
    esprit(m, "marchand")["libre"] = instant(m) + 100
    return recharger(m)


def brune_crochete_ilse_arrive():
    """Brune crochète la réserve, au fond du refuge ; Ilse, dans l'échoppe, va venir au refuge."""
    m = nouveau_defi(depart="fixe")
    installer(m)
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("marchand", "aubin")):
        placer(m, id, "crypte", (2 + n, 3))
    m.objets["crochets"]["lieu"] = "brune"
    placer(m, "brune", "antichambre", (7, 3))
    regarder(m, "brune", "reserve")
    placer(m, "ilse", "echoppe", (6, 3))
    regarder(m, "ilse", [0, 3])
    intention(m, "brune", plan("crocheter", "reserve", "crochets"))
    # Sa ronde du refuge est due : elle y va, et l'y mène encore quand le bruit la fait reconsidérer.
    lire(m, "ilse")["visites"]["antichambre"] = -500
    intention(m, "ilse", plan("aller", lieu="antichambre"), plan("inspecter", lieu="antichambre"),
              but="garder", motif="devoir")
    esprit(m, "brune")["libre"] = 5
    esprit(m, "ilse")["libre"] = 25      # elle se met en route pendant l'action suivante du joueur
    m.joueur.update(salle="chambre_cloche", position=[3, 7], orientation="nord")
    return recharger(m)


class GestesEnCoursTests(unittest.TestCase):
    def test_qui_se_retourne_pendant_le_vol_du_joueur_en_est_temoin(self):
        m = gorm_part_vers_l_ouest()
        moteur = Moteur(m)
        geste = moteur.preparer(sequence(etape("deplacer", "marteau", "joueur", methode="discret")))
        self.assertFalse(geste.stat)  # Personne ne le regarde quand il commence : pas de jet.
        texte = moteur.executer(geste)
        self.assertIn("Tu dérobes le marteau.", texte)
        self.assertIn("Gorm, gardien du relais t'a vu faire.", texte)
        m = recharger(m)
        self.assertEqual(m.objets["marteau"]["lieu"], "joueur")
        # Il l'a vu prendre : il le sait dans les mains de Corvus (``pnj._lieu_vu``).
        self.assertIn({"type": "vu_agir", "auteur": "joueur", "operation": "prendre", "objet": "marteau",
                       "lieu": {"valeur": "joueur", "salle": None, "case": None, "minute": 0}},
                      [{k: v for k, v in s.items() if k not in ("minute", "preuve", "victime")} for s in lire(m, "marchand")["memoire"]])
        self.assertEqual(lire(m, "marchand")["croyances"]["marteau"]["lieu"]["valeur"], "joueur")
        self.assertFalse(relation(m, "marchand", "joueur")["valeur"])
        # Le geste fini quitte le registre à l'action suivante.
        faire(m, "tourner sud")
        self.assertEqual(m.data["gestes_en_cours"], [])

    def test_un_geste_de_pnj_a_cheval_sur_deux_actions_garde_ses_temoins(self):
        m = brune_crochete_ilse_arrive()
        with patch.object(Monde, "d20", return_value=20):
            faire(m, "tourner sud")
        m = recharger(m)
        self.assertEqual([(g["auteur"], g["operation"], g["objet"], g["temoins"]) for g in m.data["gestes_en_cours"]],
                         [("brune", "crocheter", "reserve", [])])
        self.assertGreater(m.data["gestes_en_cours"][0]["fin"], instant(m))
        with patch.object(Monde, "d20", return_value=20):
            faire(m, "attendre")
        m = recharger(m)
        self.assertIn({"type": "vu_agir", "auteur": "brune", "operation": "crocheter", "objet": "reserve"},
                      [{k: v for k, v in s.items() if k not in ("minute", "preuve", "victime")} for s in lire(m, "ilse")["memoire"]])
        self.assertFalse(relation(m, "ilse", "brune")["valeur"])
        self.assertEqual(m.data["gestes_en_cours"], [])


if __name__ == "__main__":
    unittest.main()
