"""Lot 376 : perceptions composables, état et rendu après sauvegarde/rechargement."""
import copy
import gzip
import json
from pathlib import Path
import unittest

from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.pnj import avancer
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler, instant
from tests.test_presences import recharger, scene


def capture():
    with gzip.open(Path(__file__).parent / "data/messages-376-auberge-accord.json.gz", "rt", encoding="utf-8") as f:
        return Monde(json.load(f))


def vivre(m, laps, moteur=False):
    lignes = []
    for dt in laps:
        if moteur:
            mj = Moteur(m)
            p = mj.preparer(proposition("attendre"))
            p.minutes, p.dixiemes, p.information = 0, dt, ""
            p.effets = []
            # Transaction d'attente neutre de durée contrôlée, sans l'interruption
            # du choix public : celui-ci est exercé séparément plus bas.
            texte = mj._executer_simple(p, m.copier())
            faits = texte.splitlines() if texte != "Action accomplie." else []
            assert m.data["journal"][-1]["faits"] == faits
            # Le libellé de la commande n'est pas une perception du monde.
            lignes.extend(l for l in faits if l != "Cinq minutes passent. Le calme revient peu à peu.")
        else:
            minutes = ecouler(m, dt)
            avancer(m, minutes, lignes, dixiemes=dt)
        avant = copy.deepcopy(m.data)
        rendu = regarder(m), scene_percue(m)
        m = recharger(m)
        assert m.data == avant
        assert (regarder(m), scene_percue(m)) == rendu
    return m, lignes


def sans_journal(m):
    data = copy.deepcopy(m.data)
    data.pop("journal", None)
    data.pop("revision", None)
    # La provenance d'une parole garde le numéro de son action, dont le nombre
    # diffère volontairement ; son instant, ses mots et son audience restent comparés.
    for p in data.get("emissions_parole", []):
        p.pop("revision", None)
    return data


class MessagesDecoupageTests(unittest.TestCase):
    def meme_monde(self, a, b):
        a, b = sans_journal(a), sans_journal(b)
        self.assertTrue(a == b, "Champs différents : " + repr(
            [k for k in a.keys() | b.keys() if a.get(k) != b.get(k)]))

    def comparer(self, m, *, moteur=False, laps=(600, 600, 600)):
        a, la = vivre(m.copier(), [sum(laps)], moteur)
        b, lb = vivre(m.copier(), laps, moteur)
        self.assertEqual(la, lb)
        self.meme_monde(a, b)
        self.assertEqual((regarder(a), scene_percue(a)), (regarder(b), scene_percue(b)))
        return a, la

    def comparer_transaction(self, m, laps):
        # Une seule commande, comme le bloc : entendus décrit le dernier
        # geste du joueur et n'est pas réinitialisé entre événements PNJ.
        # La vie découpée/rechargée sert d'oracle de toutes ses perceptions.
        m.data['entendus'] = []
        from donjon.vecu import noter
        noter(m, 'joueur', instant(m), 'repos')
        a, la = self.comparer(m, laps=laps)
        b, lb = vivre(m.copier(), [sum(laps)], moteur=True)
        from donjon.noms import texte
        self.assertEqual([texte(a, ligne, citations=True) for ligne in la], lb)
        self.meme_monde(a, b)
        self.assertEqual((regarder(a), scene_percue(a)), (regarder(b), scene_percue(b)))
        return b, lb

    def test_capture_371_livraison_extinction_et_depart(self):
        m, lignes = self.comparer(capture())
        self.assertEqual(m.joueur["or"], 47)
        self.assertFalse(m.objets["lanterne_etable"]["allume"])
        self.assertEqual(m.objets["pot_huile_1"]["lieu"], "joueur")
        self.assertIn("Odile, aubergiste du Col-Pendu, quitte la pièce.", lignes)
        extinction = lignes.index("La lanterne d'écurie s'éteint.")
        self.assertEqual(lignes[extinction + 1], "Tu ne vois plus Joss, palefrenier.")
        self.assertFalse(any("un instant" in l for l in lignes))

    def test_capture_371_decoupe_fin_avant_et_apres_extinction(self):
        self.comparer(capture(), laps=(599, 1, 599, 1, 1, 599))

    def test_capture_371_par_le_moteur_et_son_journal(self):
        self.comparer(capture(), moteur=True)

    def test_relais_passage_bref_et_sons(self):
        m = scene("echoppe", [1, 5], "est", "antichambre", [6, 1], "crypte")
        a, lignes = self.comparer(m, laps=(10, 90, 200, 300, 1200))
        self.assertEqual(a.objets["marchand"]["lieu"], "crypte")
        self.assertEqual([l for l in lignes if "Gorm" in l],
                         ["Gorm, gardien du relais, entre dans la pièce.",
                          "Gorm, gardien du relais, quitte la pièce."])
        self.assertTrue(any(l.startswith("Tu entends") for l in lignes))

    def test_relais_par_le_moteur(self):
        m = scene("echoppe", [1, 5], "est", "antichambre", [6, 1], "crypte")
        self.comparer(m, moteur=True, laps=(10, 90, 200, 300, 1200))

    def test_attente_interrompue_garde_tout_ce_qui_a_ete_percu(self):
        m = scene("echoppe", [1, 5], "est", "antichambre", [6, 1], "crypte")
        attendu = m.copier()
        mj = Moteur(attendu)
        texte = mj.executer(mj.preparer(proposition("attendre", "300")))
        dt = instant(attendu) - instant(m)
        self.assertLess(dt, 3000)
        attendu = recharger(attendu)
        bloc, lignes = vivre(m, [dt], moteur=True)
        self.assertEqual(texte.splitlines()[1:], lignes)
        self.assertEqual(sans_journal(attendu), sans_journal(bloc))

    def test_deplacement_cache_ne_devoile_pas_le_personnage(self):
        m = scene("chambre_cloche", [1, 3], "nord", "antichambre", [6, 1], "crypte")
        self.assertFalse(m.visible("marchand"))
        a, lignes = self.comparer(m)
        self.assertFalse(a.visible("marchand"))
        self.assertFalse(any("Gorm" in l for l in lignes))

    def test_conversation_et_ton_bref_aux_frontieres(self):
        from tests.test_contact_position_inconnue import source_ailleurs
        # Le ton est reçu à 1200, puis expire avant le prochain événement à
        # 1300. Il doit être publié au même instant, y compris sans borne
        # d'action à 1200. Les deux voies rechargent après chaque tranche.
        _, lignes = self.comparer_transaction(source_ailleurs(), (1199, 1, 1, 2399))
        self.assertEqual(lignes.count("La femme large parle doucement à l'homme taillé en bloc."), 1)

    def test_transaction_pnj_ne_republie_pas_les_sons_copies(self):
        from tests.test_reprise_contact import capture as contact
        # La transaction d'Ilse à 143408 adopte des copies de la file de
        # bruits ; leurs événements et leurs émissions restent les mêmes.
        # La voie moteur contrôle aussi le dernier rendu et son journal.
        self.comparer_transaction(contact(), (2399, 1, 7, 1, 1, 591))


if __name__ == "__main__":
    unittest.main()
