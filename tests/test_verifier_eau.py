"""Branche ``verifier-eau``, vérifiée après rechargement :

- ``planification.VERIFIER`` : une recherche restreinte à ce qu'il vaut la peine de porter
  (``emplois``) n'explore qu'une partie de la recherche complète pour le même but ; ce que le but
  demande lui-même (avoir de la lumière : chercher qui porte une flamme) se lit du but
  (``Vue.eclairer``), pas d'``emplois`` ; la référence n'est pas bornée plus bas que ce qu'elle
  contrôle ; restreinte et complète ont le même coût (le plan peut différer à égalité) ;
- l'eau : tout plan compte ce qu'elle lui coûte (``Vue.pression``) ; on ne se chauffe pas, on ne se
  tient pas là où on la croit ou l'attend ; on ne descend pas dans une salle qu'on attend noyée ou
  d'où le retour serait coupé ; qui l'attend noyée là où il se tient en sort avant tout."""
import json
import unittest
from unittest.mock import patch

from donjon import eau, planification
from donjon.banc_pnj import creer, executer
from donjon.deliberation import deliberer
from donjon.esprits import lire, percevoir
from donjon.geometrie import position_entree
from donjon.planification import Vue, depart, diagnostics, planifier, planifier_pulsion
from tests.support import calme
from tests.test_eau import FIXES, attendre, crue
from tests import test_lumiere as lumiere, test_lumiere_garde as lumiere_garde
from tests.test_tensions import placer, recharger, vivre


def nuit(scenario, graine, salle):
    m = creer(scenario, graine)
    m.joueur.update(salle=salle, position=list(position_entree(m, salle)))
    return m


def par_blocs(m, jusqu_a, bloc):
    """Fait vivre le monde jusqu'à ``jusqu_a``, rechargé tous les ``bloc`` minutes."""
    while m.data["minutes"] < jusqu_a:
        executer(m, min(jusqu_a, m.data["minutes"] + bloc))
        m = recharger(m)
    return m


class VerifierTests(unittest.TestCase):
    def test_lucien_cherche_josse_pour_la_lumiere_et_la_reference_le_trouve_aussi(self):
        # Cas réel (``test_lumiere``, la mine noire, révélé à la fusion de ``ouie-temoins``) : dans le
        # noir, Lucien va chercher Josse, qui porte une lampe, et l'appelle ; la référence de
        # ``VERIFIER`` (sans ``emplois``) n'offrait pas ce geste et ne trouvait aucun plan.
        m = lumiere.avec_briquet(lumiere.mine_noire())
        m.objets["lampe_remy"].update(allume=False, combustible=0)
        for id in ("remy", "lucien", "bram"):
            lire(m, id)["besoins"]["securite"] = 70.0
        # Ses buts se choisissent aussi entre deux minutes (``deliberation-evenements``) : on regarde
        # chacun de ses choix, pas seulement l'état à la minute.
        from donjon import deliberation
        plans, choisir = [], deliberation.choisir

        def espion(monde, id, minute):
            resultat = choisir(monde, id, minute)
            i = lire(monde, id)["intention"]
            if id == "lucien" and i:
                plans.append(i)
            return resultat
        with patch.object(planification, "VERIFIER", True), diagnostics() as recherches,                 patch.object(deliberation, "choisir", espion):
            for _ in range(15):
                m, _ = vivre(m, 1)
        self.assertTrue(any(i["but"]["type"] == "lumiere" and any(
            (x.get("contenu") or {}).get("cherche") == "josse" for x in i["plan"]) for i in plans))
        self.assertTrue(any(r["pnj"] == "lucien" and r["but"] == "lumiere" for r in recherches))
        self.assertIn("Lucien appelle : « Josse ? »", [c["texte"] for c in m.data["chronique"]])

    def test_remy_cherche_gaspard_et_le_controle_passe(self):
        # Même nature (mine, le camp éteint) : Rémy va chercher Gaspard, qui a le briquet, l'appelle et
        # lui demande du feu ; chaque recherche de lumière, restreinte, a le coût de la complète.
        m = lumiere_garde.FeuDemandeTests().camp_eteint()
        with patch.object(planification, "VERIFIER", True), diagnostics() as recherches:
            m = lumiere_garde.suivre(m, 10, lambda m: m.objets["lampe_rechange_1"].get("allume"))
        self.assertTrue(any(r["pnj"] == "remy" and r["but"] == "lumiere" and r["issue"] == "plan" for r in recherches))
        self.assertIn("Rémy appelle : « Gaspard ? »", [c["texte"] for c in m.data["chronique"]])
        self.assertTrue(m.objets["lampe_rechange_1"]["allume"])

    def test_une_reference_bornee_n_est_pas_un_defaut(self):
        # La référence arrêtée par sa borne n'est pas un optimum : la restreinte ne doit que ne pas
        # coûter plus qu'elle (ici, elle ne trouve rien en un nœud).
        m = lumiere_garde.FeuDemandeTests().camp_eteint()
        with patch.object(planification, "VERIFIER", True), patch.object(planification, "REFERENCE", 1):
            m = lumiere_garde.suivre(m, 10, lambda m: m.objets["lampe_rechange_1"].get("allume"))
        self.assertTrue(m.objets["lampe_rechange_1"]["allume"])


class EauTests(unittest.TestCase):
    def test_crue_500_personne_ne_se_chauffe_dans_l_eau_ni_ne_reste_piege(self):
        # Cas réel (crue 500, minutes 165 à 185) : Brune allait se chauffer au brasero sous 88 cm
        # d'eau, Gorm faire sa ronde à la salle des vannes ; la conduite noyée et la porte étanche
        # verrouillée les y enfermaient (475 minutes sous l'eau, 48 appels à l'aide).
        m = par_blocs(nuit("crue", 500, "chambre_cloche"), 167, 60)
        but = planifier(m, "brune", "chaleur")
        # Depuis la branche ``ressources``, le poêle du guet chauffe la galerie, au sec : s'y chauffer
        # est permis (relations graduées et appel négocié réunis, elle le croit encore allumé à 167) ;
        # jamais près d'un feu là où elle attend l'eau.
        self.assertFalse(but and any(x["lieu"] == "echoppe" or x["operation"] == "chauffer"
                                     and eau.attendue(m, "brune", m.objets[x["cible"]]["lieu"]) > 0
                                     for x in but[1]))
        self.assertIsNone(planifier_pulsion(m, "marchand", {"lieu": "crypte", "periode": 72}))
        # Personne n'appelle à l'aide depuis l'eau. Relations graduées et profils réunis : Brune vole la
        # réserve sous les yeux de Gorm (min 150) ; au refuge, au sec, Gorm, Aubin et Ilse appellent
        # alors à l'aide contre elle, ce qui n'est pas le piège de l'eau.
        appels = []
        while m.data["minutes"] < 360:
            nouvelles, _ = executer(m, min(360, m.data["minutes"] + 5))
            appels += [(c["pnj"], eau.profondeur(m, m.objets[c["pnj"]]["lieu"]))
                       for c in nouvelles if "appelle à l'aide" in c["texte"]]
            m = recharger(m)
        self.assertFalse([a for a in appels if a[1] > 0])
        mouillee = min(h["minute"] for h in m.data["crue"]["historique"] if h["salle"] == "echoppe")
        chronique = m.data["chronique"]
        self.assertFalse([c for c in chronique if c["minute"] > mouillee and "se chauffe" in c["texte"]])
        for id in ("marchand", "brune", "ilse", "aubin"):
            self.assertLess(eau.profondeur(m, m.objets[id]["lieu"]), 50, id)

    def test_le_meme_laps_decoupe_donne_le_meme_monde(self):
        d_un_bloc = nuit("crue", 500, "chambre_cloche")
        executer(d_un_bloc, 240)
        decoupe = par_blocs(nuit("crue", 500, "chambre_cloche"), 240, 40)
        self.assertEqual(json.dumps(recharger(d_un_bloc).data, sort_keys=True),
                         json.dumps(decoupe.data, sort_keys=True))

    def scene(self):
        """Même nature, une autre crue (1 cm par minute depuis -150) : à la minute 100, tous au refuge
        ont vu l'eau monter ; ils attendent la conduite (130 cm) et la salle des vannes (110 cm)
        noyées dans l'heure, le refuge mouillé (10 cm)."""
        m = calme(crue(FIXES), "marchand", "brune", "ilse", "aubin")
        m, _ = attendre(m, 100)
        self.assertEqual(eau.estimation(m, "aubin")[2], 60)
        return m

    def test_on_ne_descend_pas_ou_l_eau_va_noyer_et_on_ne_s_y_chauffe_pas(self):
        m = self.scene()
        # La ronde d'Aubin à la salle des vannes, le brasero de la conduite pour Ilse transie.
        self.assertIsNone(planifier_pulsion(m, "aubin", {"lieu": "crypte", "periode": 49}))
        lire(m, "ilse")["besoins"]["chaleur"] = 90.0
        m = recharger(m)
        but = planifier(m, "ilse", "chaleur")
        self.assertFalse(but and any(x["lieu"] in ("echoppe", "crypte") or x["cible"] == "brasero"
                                     for x in but[1]))
        # Elle monte se chauffer au poêle du guet, à la galerie, hors de l'eau (branche ``ressources``).
        self.assertEqual([(x["operation"], x["lieu"] or x["cible"]) for x in but[1]],
                         [("aller", "chambre_cloche"), ("chauffer", "poele_guet")])
        # L'eau coûte à tout plan, par minute, comme le noir à qui le craint.
        v = Vue(m, "ilse")
        self.assertGreater(v.pression(depart(m, "ilse", v).apres(salle="echoppe")),
                           v.pression(depart(m, "ilse", v).apres(salle="chambre_cloche")))
        self.assertTrue(v.descente("antichambre", "crypte"))
        self.assertFalse(v.descente("crypte", "antichambre"))   # Vers moins d'eau, on peut aller.

    def test_qui_attend_l_eau_noyer_sa_salle_en_sort_avant_tout(self):
        m = self.scene()
        # Placement d'auteur : Aubin s'est attardé à la salle des vannes (50 cm, noyée dans l'heure).
        placer(m, "aubin", "crypte", (2, 2))
        percevoir(m, "aubin")
        m = recharger(m)
        self.assertTrue(eau.en_peril(m, "aubin"))
        deliberer(m, "aubin", m.data["minutes"])
        self.assertEqual(lire(m, "aubin")["intention"]["motif"], "securite")
        for _ in range(10):
            m, _ = vivre(m, 1)
        self.assertNotIn(m.objets["aubin"]["lieu"], ("crypte", "echoppe"))
        self.assertFalse(eau.en_peril(m, "aubin"))


if __name__ == "__main__":
    unittest.main()
