"""L'appel négocié (``donjon/appel.py``) : qui vient à qui.

Avant, l'appelé qui saisissait son nom répondait « Ici ! » et attendait d'être rejoint cinq minutes,
quelle que soit la raison de l'appel : l'appelant cherchait, l'appelé attendait. Désormais ils en
conviennent par des paroles typées que le moteur tranche, pour les PNJ comme pour le joueur :
« J'arrive ! » (l'appelé vient), « Ici, viens ! » (l'appelé reste, l'appelant vient), « Qu'est-ce que tu
veux ? » (l'appelant dit ce qu'il veut, l'appelé décide de nouveau), ou le silence (méfiance, ou ne pas
vouloir se signaler). Ce qui est convenu entre dans l'esprit des deux, l'attente se règle sur la
distance, et « J'arrive ! » est une parole donnée : attendu en vain, on le voit et l'on lui en tient rigueur.

Chaque cas vérifie l'état après rechargement et ce que lit le joueur ; les cas réels viennent des
nuits de banc (Relais, auberge, mine) ; chaque sorte de réponse a un autre cas de même nature."""
import gzip
import json
import tempfile
import unittest
from pathlib import Path

from donjon import appel
from donjon.appel import ARRIVE, QUOI, VIENS, decider, delai
from donjon.deliberation import COMPTES
from donjon.esprits import croire, esprit, lire
from donjon.geometrie import position_entree
from donjon.monde import Monde
from donjon.paroles import reponse_a_l_appel
from donjon.planification import rejoindre
from donjon.pnj import appeler
from donjon.relations import envers, mefiance, percue, se_fie, se_mefie
from tests.support import lier, relation
from tests.test_parole_voix import gorm_derriere_la_porte
from tests.test_repli_et_appel import jouer
from tests.test_temps_etat import decouper, etat_pnj
from tests.test_tensions import attendre, chronique, placer, recharger, vivre
from tests.test_voix import appels, aubin_cherche_gorm, hugues_cherche_anselme


def suivre(m, minutes, fin):
    """Fait vivre le monde minute par minute jusqu'à ce que ``fin(m)`` soit vrai, au plus ``minutes``."""
    for _ in range(minutes):
        if fin(m):
            break
        m, _ = vivre(m, 1)
    return recharger(m)


def etat_tous(m):
    """``test_temps_etat.etat_pnj`` pour tous les personnages d'un scénario."""
    from donjon.esprits import pnjs
    from donjon.temps import instant
    return {"corps": {id: {k: m.objets[id].get(k) for k in ("lieu", "position", "orientation")} for id in pnjs(m)},
            "esprits": {id: m.data["esprits"].get(id) for id in pnjs(m)},
            "chronique": m.data.get("chronique", []), "jets": m.data["jets"], "instant": instant(m)}


def entre(textes, debut, fin):
    return textes[textes.index(debut):textes.index(fin)]


def josse_cherche_gaspard():
    """Cas réel de la mine (graine 2024, départ tiré, enregistré à la minute 340 sur ``main``) : le poêle
    du baraquement baisse ; Josse, qui le garde, cherche Gaspard pour une part de ses bûches et le hèle
    de salle en salle ; Gaspard, à la galerie du filon, finit par l'entendre (minute 346)."""
    return scene("mine_2024_minute_340.json.gz")


def porte_crue_ouverte(m, id):
    """``id`` sait la porte étanche ouverte à clé (il l'a vue) : il croit pouvoir la passer."""
    croire(m, id, "porte", "verrouillee", False, "vu")
    return recharger(m)


class IciViensTests(unittest.TestCase):
    def test_cas_reel_gorm_croit_la_porte_fermee_aubin_vient(self):
        """Relais : Aubin, affamé, hèle Gorm derrière la porte étanche, qu'il croit verrouillée de
        son côté : Gorm ne peut venir, il répond « Ici, viens ! » et attend ; Aubin répond « J'arrive ! »,
        vient, et obtient sa part au premier appel. Gorm n'a pas bougé entre la réponse et les
        retrouvailles."""
        m = aubin_cherche_gorm()
        self.assertFalse(appel.peut_venir(m, "marchand", "aubin"))
        m = suivre(m, 6, lambda m: "Aubin répond : « J'arrive ! »" in chronique(m))
        textes = chronique(m)
        self.assertIn("Gorm répond : « Ici, viens ! »", textes)
        self.assertIn("Aubin répond : « J'arrive ! »", textes)
        m = suivre(m, 8, lambda m: "Gorm retrouve Aubin, comme convenu." in chronique(m))
        textes = chronique(m)
        self.assertFalse([t for t in entre(textes, "Gorm répond : « Ici, viens ! »", "Gorm retrouve Aubin, comme convenu.")
                          if t.startswith("Gorm, gardien du relais passe dans")])
        m = suivre(m, 6, lambda m: any("Aubin" in t and "part des vivres" in t for t in chronique(m)))
        self.assertTrue(any(t.startswith(("Aubin demande une part des vivres", "Aubin achète une part des vivres"))
                            for t in chronique(m)))
        self.assertEqual(len(appels(m, "aubin")), 1)
        self.assertIsNone(lire(m, "marchand")["rejoint"])
        self.assertIsNone(lire(m, "aubin")["rejoindre"])

    def test_meme_nature_qui_garde_ne_quitte_pas_sa_garde(self):
        """Gorm garde la réserve (le but ``garder``) : hélé par Ilse, qui pourrait venir, il ne quitte pas
        sa garde et lui dit de venir ; libre, il lui demanderait ce qu'elle veut."""
        m = aubin_cherche_gorm()
        m = porte_crue_ouverte(m, "marchand")
        self.assertTrue(appel.peut_venir(m, "marchand", "aubin"))
        self.assertEqual(decider(m, "marchand", "aubin"), QUOI)
        esprit(m, "marchand")["intention"] = {"but": {"type": "garder", "lieu": "crypte"}, "motif": "biens",
                                              "plan": [], "depuis": 2, "attente": 0}
        m = recharger(m)
        self.assertEqual(decider(m, "marchand", "aubin"), VIENS)
        lignes = []
        appeler(m, "aubin", "marchand", lignes)
        m = recharger(m)
        self.assertIn("Gorm répond : « Ici, viens ! »", chronique(m))
        self.assertEqual(lire(m, "marchand")["rejoint"]["qui"], "aubin")

    def test_l_appelant_retenu_le_dit_et_l_appele_vient(self):
        """Cas vu au banc (mine, graine 42) : Mathe, qui garde le baraquement, hèle Gaspard ; il lui
        demande ce qu'elle veut, lui dit de venir ; retenue par sa garde, elle lui répond « Ici, viens ! »
        à son tour. Avant, chacun attendait l'autre jusqu'à l'échéance ; prié de venir, Gaspard en
        décide de nouveau : il vient. Même chose au Relais, Gorm de garde hélant Aubin."""
        m = porte_crue_ouverte(porte_crue_ouverte(aubin_cherche_gorm(), "marchand"), "aubin")
        lire(m, "aubin")["besoins"]["faim"] = 10.0   # Libre : il ne cherche plus Gorm.
        esprit(m, "marchand")["intention"] = {"but": {"type": "garder", "lieu": "crypte"}, "motif": "biens",
                                              "plan": [], "depuis": 2, "attente": 0}
        m = recharger(m)
        appeler(m, "marchand", "aubin", [])
        m = recharger(m)
        suite = ["Gorm appelle : « Aubin ? »", "Aubin répond : « Qu'est-ce que tu veux ? »",
                 "Gorm répond : « J'ai à te parler. »", "Aubin répond : « Ici, viens ! »",
                 "Gorm répond : « Ici, viens ! »", "Aubin répond : « J'arrive ! »"]
        self.assertEqual([t for t in chronique(m) if t in suite], suite)
        self.assertIsNone(lire(m, "aubin")["rejoint"])
        self.assertEqual(lire(m, "aubin")["rejoindre"]["qui"], "marchand")
        self.assertEqual((lire(m, "marchand")["rejoint"]["qui"], lire(m, "marchand")["rejoint"]["vient"]), ("aubin", True))


class QuoiTests(unittest.TestCase):
    def test_cas_reel_hugues_previent_anselme_qui_vient(self):
        """Auberge : Hugues, sans lumière au couloir, veut prévenir Anselme, enfermé dans sa chambre,
        que Lucien a forcé son coffre. Anselme ne sait pourquoi on l'appelle : « Qu'est-ce que tu
        veux ? » ; Hugues : « J'ai à te prévenir de quelque chose. » ; un avertissement le regarde :
        « J'arrive ! ». Anselme vient au couloir, Hugues l'y attend sans bouger, et le prévient."""
        m = recharger(hugues_cherche_anselme())
        confiance_avant = envers(m, "anselme", "lucien")["confiance"]
        m, texte = attendre(m)
        textes = chronique(m)
        suite = ["Hugues appelle : « Anselme ? »", "Anselme répond : « Qu'est-ce que tu veux ? »",
                 "Hugues répond : « J'ai à te prévenir de quelque chose. »", "Anselme répond : « J'arrive ! »",
                 "Hugues retrouve Anselme, comme convenu.", "Hugues dit à Anselme que Lucien est peu fiable (crue)."]
        self.assertEqual([t for t in textes if t in suite], suite)
        self.assertFalse([t for t in entre(textes, suite[0], suite[4]) if t.startswith("Hugues, ancien soldat passe dans")])
        self.assertTrue([t for t in entre(textes, suite[0], suite[4]) if t.startswith("Anselme, marchand drapier passe dans")])
        self.assertEqual(len(appels(m, "hugues")), 1)
        self.assertIsNone(lire(m, "hugues")["rejoint"])
        self.assertIsNone(lire(m, "anselme")["rejoindre"])
        # L'avertissement arrive une fois, plus tôt. Une rumeur baisse la confiance sans
        # forcément franchir sa bande d'hystérésis ; les retrouvailles ne décident pas l'avis.
        self.assertLess(envers(m, "anselme", "lucien")["confiance"], confiance_avant)
        self.assertTrue(any(s["type"] == "avis_recu" and s["sujet"] == "lucien" and s["valeur"] is False
                            for s in lire(m, "anselme")["memoire"]))

    def test_cas_reel_mine_josse_dit_ce_qu_il_veut_gaspard_le_fait_venir(self):
        """Mine (graine 2024) : Josse hèle Gaspard pour une part de ses bûches (le poêle qu'il garde
        baisse). Gaspard demande ce qu'il veut ; une demande de ce qu'il n'a pas sur lui ne le fait pas
        venir : « Ici, viens ! » ; Josse répond « J'arrive ! », le rejoint, et demande sa part."""
        m = josse_cherche_gaspard()
        m = suivre(m, 10, lambda m: "Gaspard répond : « Ici, viens ! »" in chronique(m))
        textes = chronique(m)
        suite = ["Gaspard répond : « Qu'est-ce que tu veux ? »", "Josse répond : « J'ai quelque chose à te demander. »",
                 "Gaspard répond : « Ici, viens ! »", "Josse répond : « J'arrive ! »"]
        self.assertEqual([t for t in textes if t in suite], suite)
        demande = "Josse demande une part des bûches de Gaspard à Gaspard "
        m = suivre(m, 4, lambda m: any(t.startswith(demande) for t in chronique(m)))
        self.assertIn("Gaspard retrouve Josse, comme convenu.", chronique(m))
        # La demande est faite après les retrouvailles ; son issue dépend du jet de partage
        # et de son éventuel recours, qui ne font pas partie du contrat de l'appel.
        textes = chronique(m)
        self.assertLess(textes.index("Gaspard retrouve Josse, comme convenu."),
                        next(i for i, t in enumerate(textes) if t.startswith(demande)))
        self.assertIsNone(lire(m, "josse")["rejoindre"])

    def test_le_meme_laps_decoupe_donne_le_meme_monde(self):
        d_un_bloc, morcele = decouper(lambda: recharger(hugues_cherche_anselme()), 4)
        self.assertIn("Anselme répond : « J'arrive ! »", chronique(morcele))
        self.assertEqual(etat_tous(d_un_bloc), etat_tous(morcele))


def scene(nom):
    """Une scène réelle de banc, enregistrée sur ``main`` (``tests/data``)."""
    source = Path(__file__).parent / "data" / nom
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "partie.json"
        chemin.write_bytes(gzip.decompress(source.read_bytes()))
        m = Monde.charger(chemin)
    # Enregistrée avant la branche des noms (pas de migration des sauvegardes) : les liens que le
    # scénario déclare (``connait_noms``) sont repris de ses données, sans quoi personne n'y saurait le
    # nom des autres et nul ne hélerait par un nom.
    # Le nom du fichier commence par celui du scénario (« crue_42_… », « mine_2024_… »).
    scenario = json.loads((Path(__file__).parents[1] / "donjon" / f"scenario_{nom.split('_')[0]}.json")
                          .read_text(encoding="utf-8"))
    for id, o in scenario["objets"].items():
        if "connait_noms" in o and id in m.objets:
            m.objets[id]["connait_noms"] = list(o["connait_noms"])
    return recharger(m)


class JArriveTests(unittest.TestCase):
    def test_cas_reel_crue_venu_comme_promis_il_se_signale(self):
        """Crue (graine 42, minute 221) : Brune, au refuge, hèle Gorm ; à « Qu'est-ce que tu veux ? »,
        une demande de ce qu'il a sur lui : « J'arrive ! ». Gorm vient au refuge et la voit ; elle, qui ne
        le voit pas, l'attendait encore et l'aurait cru parjure à l'échéance (vu au banc). Venu comme
        promis, il le lui dit : « Me voici ! » ; ils se sont retrouvés, sans parole rompue."""
        m = scene("crue_42_minute_215.json.gz")
        # Isoler l'annonce d'arrivée : la capture place Gorm au repos dans
        # 18 cm d'eau. Son évacuation passe désormais avant une nouvelle parole.
        # La crue native est vérifiée par les bancs de survie ; ici les paroles
        # et leurs conséquences restent celles du contrat d'appel.
        m.data.pop("crue")
        # Depuis la fusion des lampes (une part d'un lot porté se demande) et des noms, cette nuit ne mène
        # plus d'elle-même à l'appel de la minute 221 : il est placé d'autorité tel qu'il se faisait alors.
        # Brune, au refuge, cherche Gorm pour une part de son bois et parcourt la salle sans le voir ;
        # tournée au nord-est, elle ne voit pas le seuil par où il entrera.
        esprit(m, "brune")["intention"] = {
            "but": {"type": "part", "objet": "bois", "de": "marchand"}, "motif": "chaleur",
            "plan": [{"operation": "inspecter", "cible": "", "outil": "", "lieu": "antichambre", "condition": "",
                      "contenu": {"cherche": "marchand"}}], "depuis": m.data["minutes"], "attente": 0}
        m.objets["brune"]["orientation"] = "nord-est"
        appeler(m, "brune", "marchand", [])
        m = suivre(recharger(m), 10, lambda m: "Brune retrouve Gorm, comme convenu." in chronique(m))
        textes = chronique(m)
        suite = ["Brune appelle : « Gorm ? »", "Gorm répond : « Qu'est-ce que tu veux ? »",
                 "Brune répond : « J'ai quelque chose à te demander. »", "Gorm répond : « J'arrive ! »",
                 "Gorm, gardien du relais passe dans : Refuge du relais.", "Gorm répond : « Me voici ! »",
                 "Brune retrouve Gorm, comme convenu."]
        textes = textes[textes.index(suite[0]):]
        self.assertEqual([t for t in textes if t in suite], suite)
        m = suivre(m, 5, lambda m: False)
        self.assertNotIn("Brune cesse d'attendre Gorm, qui avait promis de venir.", chronique(m))
        self.assertFalse(se_mefie(m, "brune", "marchand"))
        self.assertIsNone(lire(m, "brune")["rejoint"])
        self.assertIsNone(lire(m, "marchand")["rejoindre"])

    def aubin_cherche_gorm_qui_le_hele(self):
        """Gorm hèle Aubin, qui cherche Gorm pour sa part et connaît sa voix."""
        m = aubin_cherche_gorm()
        lire(m, "aubin")["intention"] = {
            "but": {"type": "part", "objet": "vivres", "de": "marchand"}, "motif": "faim", "depuis": 2, "attente": 0,
            "plan": [{"operation": "aller", "cible": "", "outil": "", "lieu": "echoppe", "condition": ""},
                     {"operation": "inspecter", "cible": "", "outil": "", "lieu": "echoppe", "condition": "",
                      "contenu": {"cherche": "marchand"}}]}
        return m

    def test_qui_cherche_l_appelant_vient(self):
        """Aubin cherche Gorm : à son appel, « J'arrive ! » ; Gorm l'attend là où il est, le temps qu'il
        faut à Aubin pour venir ; Aubin vient et obtient sa part, sans rappeler."""
        m = self.aubin_cherche_gorm_qui_le_hele()
        appeler(m, "marchand", "aubin", [])
        m = recharger(m)
        self.assertIn("Aubin répond : « J'arrive ! »", chronique(m))
        r, d = lire(m, "marchand")["rejoint"], lire(m, "aubin")["rejoindre"]
        self.assertEqual((r["qui"], r["vient"], d["qui"], d["salle"]), ("aubin", True, "marchand", "crypte"))
        self.assertEqual(r["jusqu_a"], d["jusqu_a"])
        m = suivre(m, 6, lambda m: any(t.startswith(("Aubin demande une part", "Aubin achète une part"))
                                         for t in chronique(m)))
        self.assertIn("Gorm retrouve Aubin, comme convenu.", chronique(m))
        self.assertEqual(appels(m, "aubin"), [])
        self.assertNotIn("Gorm cesse d'attendre Aubin, qui avait promis de venir.", chronique(m))

    def test_le_temps_d_attente_suit_la_distance(self):
        """L'échéance est le temps de venir, et sa moitié, plus une marge : plus loin, plus longue. Du
        palier, Aubin est à quelques pas de Gorm ; de la galerie de ronde, plus loin ; à l'auberge, la même
        règle, d'un étage à l'autre."""
        m = aubin_cherche_gorm()
        pres, d_pres = appel.venue(m, "aubin", "marchand"), delai(m, "aubin", "marchand")
        placer(m, "aubin", "chambre_cloche", [3, 6])  # La galerie de ronde, au-delà du palier.
        loin, d_loin = appel.venue(m, "aubin", "marchand"), delai(m, "aubin", "marchand")
        self.assertGreater(loin, pres)
        self.assertGreaterEqual(d_loin, d_pres)
        self.assertEqual(d_pres, appel.MARGE + 1)
        a = recharger(hugues_cherche_anselme())
        placer(a, "hugues", "grenier", list(position_entree(a, "grenier")))
        placer(a, "anselme", "cuisine", list(position_entree(a, "cuisine")))
        t = appel.venue(a, "hugues", "anselme")
        self.assertGreater(t, 0)
        self.assertEqual(delai(a, "hugues", "anselme"), appel.MARGE + -(-(t + t // 2) // 600))

    def test_qui_avait_promis_et_ne_vient_pas_rompt_sa_parole(self):
        """Même nature, la parole rompue : Aubin a répondu « J'arrive ! », puis la porte se ferme à clé et
        il le sait : il ne peut venir. Gorm l'attend jusqu'à l'échéance, cesse d'attendre et le voit :
        une parole non tenue, comme une promesse abandonnée (relations graduées : confiance −20, rancune ;
        lié à Aubin par une confiance de 65, il ne lui fait plus confiance, sans encore s'en méfier)."""
        m = self.aubin_cherche_gorm_qui_le_hele()
        appeler(m, "marchand", "aubin", [])
        m.objets["porte"].update(verrouillee=True, ouverte=False)
        croire(m, "aubin", "porte", "verrouillee", True, "essai")
        jusqu_a = lire(m, "marchand")["rejoint"]["jusqu_a"]
        m = recharger(m)
        self.assertTrue(se_fie(m, "marchand", "aubin"))
        m = suivre(m, jusqu_a + 2, lambda m: lire(m, "marchand")["rejoint"] is None)
        self.assertIn("Gorm cesse d'attendre Aubin, qui avait promis de venir.", chronique(m))
        r = envers(m, "marchand", "aubin")
        self.assertEqual(r["confiance"], 45)
        self.assertGreater(r["rancune"], 0)
        self.assertEqual(r["motifs"][-1]["type"], "parole_rompue")
        self.assertFalse(se_fie(m, "marchand", "aubin"))
        self.assertTrue(any(s["type"] == "parole_rompue" and s["qui"] == "aubin" for s in lire(m, "marchand")["memoire"]))
        self.assertEqual([c["minute"] for c in m.data["chronique"]
                          if c["texte"] == "Gorm cesse d'attendre Aubin, qui avait promis de venir."], [jusqu_a])

    def test_le_meme_laps_decoupe_donne_le_meme_monde(self):
        d_un_bloc, morcele = decouper(aubin_cherche_gorm, 6)
        self.assertIn("Aubin répond : « J'arrive ! »", chronique(morcele))
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))


class SilenceTests(unittest.TestCase):
    def test_qui_guette_un_geste_sans_temoin_ne_se_signale_pas(self):
        """Brune guette l'occasion de forcer la réserve (un geste qu'elle veut sans témoin) : hélée par
        Gorm, à deux pas, elle se tait ; Gorm retient l'appel resté sans réponse."""
        m = aubin_cherche_gorm()
        placer(m, "brune", "crypte", (3, 2))
        esprit(m, "brune")["intention"] = {
            "but": {"type": "manger", "objet": "vivres"}, "motif": "faim", "depuis": 2, "attente": 0,
            "plan": [{"operation": "crocheter", "cible": "reserve", "outil": "crochets", "lieu": "", "condition": "sans_temoin"}]}
        m = recharger(m)
        self.assertTrue(appel.se_cache(m, "brune"))
        avant = COMPTES["silence"]
        self.assertFalse(appel.repondre(m, "marchand", "brune", []))
        m = recharger(m)
        self.assertEqual(COMPTES["silence"], avant + 1)
        self.assertNotIn("Brune répond", " ".join(chronique(m)))
        self.assertTrue(any(s["type"] == "appel_sans_reponse" and s["qui"] == "brune"
                            for s in lire(m, "marchand")["memoire"]))

    def test_meme_nature_qui_se_mefie_se_tait(self):
        m = aubin_cherche_gorm()
        lier(m, "marchand", "aubin", False, "vu")
        m = recharger(m)
        self.assertIsNone(decider(m, "marchand", "aubin"))
        m, _ = vivre(m, 1)
        self.assertNotIn("Gorm répond", " ".join(chronique(m)))
        self.assertIsNone(lire(m, "marchand")["rejoint"])


def gorm_libre_derriere_la_porte():
    """Corvus au palier ; Gorm, libre, derrière la porte étanche qu'il sait ouverte à clé : il peut venir."""
    return porte_crue_ouverte(gorm_derriere_la_porte(), "marchand")


class JoueurHeleTests(unittest.TestCase):
    def test_qu_est_ce_que_tu_veux_puis_viens(self):
        """Gorm, libre, ne sait ce que Corvus lui veut : « Qu'est-ce que tu veux ? » ; Corvus : « viens »
        (sans le MJ) ; Gorm : « J'arrive ! », ouvre la porte et le rejoint."""
        m = gorm_libre_derriere_la_porte()
        reprise, sortie, appels_mj = jouer(m, "j'appelle Gorm", [], [])
        self.assertEqual(appels_mj, [])
        self.assertIn("Tu entends, à l'ouest, une voix qui se dit Gorm répondre : « Qu'est-ce que tu veux ? »", sortie)
        self.assertEqual(appel.en_attente(reprise), [("marchand", QUOI)])
        self.assertIsNone(lire(reprise, "marchand")["rejoint"])
        reprise, sortie, appels_mj = jouer(reprise, "viens", [], [])
        self.assertEqual(appels_mj, [])
        self.assertIn("Tu réponds : « Ici, viens ! »", sortie)
        self.assertIn("Tu entends, à l'ouest, une voix qui se dit Gorm répondre : « J'arrive ! »", sortie)
        self.assertEqual(lire(reprise, "marchand")["rejoindre"]["qui"], "joueur")
        for _ in range(3):
            reprise, sortie, _ = jouer(reprise, "attendre 30 s", [], [])
        self.assertEqual(reprise.objets["marchand"]["lieu"], "beffroi")
        self.assertIsNone(lire(reprise, "marchand")["rejoindre"])
        self.assertNotIn("Gorm appelle : « Corvus ? »", chronique(reprise))  # Il l'a vu en entrant.

    def test_ici_viens_puis_j_arrive(self):
        """Gorm croit la porte verrouillée : « Ici, viens ! » ; Corvus : « j'arrive », ouvre la porte ; ils
        se retrouvent comme convenu."""
        m = gorm_derriere_la_porte()
        reprise, sortie, _ = jouer(m, "j'appelle Gorm", [], [])
        self.assertIn("Tu entends, à l'ouest, une voix qui se dit Gorm répondre : « Ici, viens ! »", sortie)
        self.assertEqual(lire(reprise, "marchand")["rejoint"]["vient"], False)
        reprise, sortie, appels_mj = jouer(reprise, "j'arrive", [], [])
        self.assertEqual(appels_mj, [])
        self.assertIn("Tu réponds : « J'arrive ! »", sortie)
        self.assertEqual(lire(reprise, "marchand")["rejoint"]["vient"], True)
        reprise, sortie, _ = jouer(reprise, "ouvrir porte", [], [])
        self.assertIn("Gorm retrouve Corvus, comme convenu.", chronique(reprise))
        self.assertIsNone(lire(reprise, "marchand")["rejoint"])
        self.assertFalse(se_mefie(reprise, "marchand", "joueur"))

    def test_j_arrive_de_qui_le_cherche(self):
        """Gorm cherche Corvus (but placé d'autorité) : hélé par lui, « J'arrive ! »."""
        m = gorm_libre_derriere_la_porte()
        etapes, _ = rejoindre(m, "marchand", "joueur")
        esprit(m, "marchand")["intention"] = {"but": {"type": "rejoindre", "qui": "joueur"}, "motif": "devoir",
                                              "plan": etapes, "depuis": 0, "attente": 0}
        m = recharger(m)
        reprise, sortie, appels_mj = jouer(m, "j'appelle Gorm", [], [])
        self.assertEqual(appels_mj, [])
        self.assertIn("répondre : « J'arrive ! »", sortie)
        self.assertEqual(lire(reprise, "marchand")["rejoindre"]["qui"], "joueur")

    def test_le_silence_de_qui_se_mefie(self):
        from donjon.voix import connaitre
        m = gorm_derriere_la_porte()
        connaitre(m, "marchand", "joueur")
        lier(m, "marchand", "joueur", False, "vu")
        m = recharger(m)
        reprise, sortie, _ = jouer(m, "j'appelle Gorm", [], [])
        self.assertIn("Aucune réponse ne te parvient.", sortie)
        self.assertEqual(appel.en_attente(reprise), [])


def gorm_hele_corvus(porte_ouverte=False):
    """Gorm, derrière la porte étanche, cherche Corvus (but placé d'autorité : aucun scénario ne fait
    chercher le joueur) et le hèle ; Corvus, au palier, l'entend."""
    m = gorm_libre_derriere_la_porte() if porte_ouverte else gorm_derriere_la_porte()
    croire(m, "marchand", "joueur", "lieu", None, "essai", salle=None, case=None)
    # Branche des noms : Gorm ne hèle Corvus par son nom que s'il l'a entendu (placement d'auteur :
    # Corvus s'est présenté à lui avant la scène) ; sinon il appelle « l'étranger ».
    from donjon.noms import apprendre
    apprendre(m, "marchand", "joueur")
    for s in m.data["salles"]:
        lire(m, "marchand")["visites"][s] = 0 if s == "crypte" else 1
    etapes, _ = rejoindre(m, "marchand", "joueur")
    esprit(m, "marchand")["intention"] = {"but": {"type": "rejoindre", "qui": "joueur"}, "motif": "devoir",
                                          "plan": etapes, "depuis": m.data["minutes"], "attente": 0}
    m, texte = attendre(recharger(m))
    assert "Tu entends, à l'ouest, une voix inconnue appeler : « Corvus ? »" in texte, texte
    return m


class JoueurHeleParUnPnjTests(unittest.TestCase):
    def test_j_arrive_puis_ne_vient_pas(self):
        """Corvus répond « j'arrive » à Gorm qui le hèle : Gorm l'attend là, le temps de venir. Corvus ne
        vient pas : à l'échéance, Gorm cesse d'attendre et se méfie de cette voix, qu'il ne connaît pas
        (comme d'un mensonge, ``voix.se_mefier``) : Corvus, jamais identifié, n'en porte pas la relation."""
        m = gorm_hele_corvus()
        reprise, sortie, appels_mj = jouer(m, "j'arrive", [], [])
        self.assertEqual(appels_mj, [])
        self.assertIn("Tu réponds : « J'arrive ! »", sortie)
        r = lire(reprise, "marchand")["rejoint"]
        self.assertEqual((r["qui"], r["vient"]), ("joueur", True))
        self.assertEqual(lire(reprise, "marchand")["intention"]["but"], {"type": "attendre", "qui": "joueur"})
        for _ in range(r["jusqu_a"] - reprise.data["minutes"] + 1):
            reprise, _, _ = jouer(reprise, "attendre 1 min", [], [])
        self.assertIn("Gorm cesse d'attendre Corvus, qui avait promis de venir.", chronique(reprise))
        self.assertTrue(mefiance(percue(reprise, "marchand", "joueur")))
        self.assertEqual(envers(reprise, "marchand", "joueur")["confiance"], 40)

    def test_viens_quand_il_ne_peut_pas_venir(self):
        """Gorm croit la porte verrouillée : à « viens », il répond « Ici, viens ! » à son tour."""
        m = gorm_hele_corvus()
        reprise, sortie, appels_mj = jouer(m, "viens ici", [], [])
        self.assertEqual(appels_mj, [])
        self.assertIn("Tu réponds : « Ici, viens ! »", sortie)
        self.assertIn("une voix inconnue répondre : « Ici, viens ! »", sortie)

    def test_viens_et_il_vient(self):
        m = gorm_hele_corvus(porte_ouverte=True)
        reprise, sortie, _ = jouer(m, "« Viens ! »", [], [])
        self.assertIn("répondre : « J'arrive ! »", sortie)
        self.assertEqual(lire(reprise, "marchand")["rejoindre"]["qui"], "joueur")

    def test_qu_est_ce_que_tu_veux(self):
        m = gorm_hele_corvus(porte_ouverte=True)
        reprise, sortie, appels_mj = jouer(m, "qu'est-ce que tu veux ?", [], [])
        self.assertEqual(appels_mj, [])
        self.assertIn("Tu réponds : « Qu'est-ce que tu veux ? »", sortie)
        self.assertIn("une voix inconnue répondre : « J'ai à te parler. »", sortie)
        self.assertEqual(appel.en_attente(reprise), [("marchand", "raison")])
        reprise, sortie, _ = jouer(reprise, "Gorm, viens", [], [])
        self.assertIn("répondre : « J'arrive ! »", sortie)
        # On ne redemande pas ce qu'il veut : le moteur refuse, sans le MJ.
        reprise, sortie, appels_mj = jouer(gorm_hele_corvus(porte_ouverte=True), "qu'est-ce que tu veux ?", [], [])
        reprise, sortie, appels_mj = jouer(reprise, "« Qu'est-ce que tu veux ? »", [], [])
        self.assertIn("Tu sais déjà ce qu'on te veut", sortie)


class FormesTests(unittest.TestCase):
    def test_formes(self):
        m = gorm_hele_corvus()
        for saisie, sorte in (("j'arrive", ARRIVE), ("J'arrive !", ARRIVE), ("je viens", ARRIVE),
                              ("« J'arrive tout de suite ! »", ARRIVE), ("je réponds que j'arrive", None),
                              ("Gorm, j'arrive !", ARRIVE), ("je crie j'arrive", ARRIVE),
                              ("viens", VIENS), ("viens ici", VIENS), ("« Ici, viens ! »", VIENS), ("je réponds", VIENS),
                              ("« Ici ! »", VIENS), ("par ici", VIENS),
                              ("qu'est-ce que tu veux ?", QUOI), ("« Que veux-tu ? »", QUOI), ("je réponds : quoi ?", QUOI),
                              ("ici", None), ("oui", None), ("viens, j'arrive", None), ("viens m'aider", None)):
            reponse = reponse_a_l_appel(m, saisie)
            self.assertEqual(reponse and reponse[1], sorte, saisie)
            if sorte:
                self.assertEqual(reponse[0], "marchand", saisie)
        # Personne n'attend de réponse : ces mots ne répondent à personne.
        self.assertIsNone(reponse_a_l_appel(gorm_derriere_la_porte(), "j'arrive"))


if __name__ == "__main__":
    unittest.main()
