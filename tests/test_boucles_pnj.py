"""Trois boucles de la revérification des nuits (``docs/reverification.md``, N1, N2 et N4), dans la
délibération des PNJ. Chaque cas se vérifie sur l'état du monde après rechargement.

- N1 : un geste qu'un autre vient de défaire sous ses yeux ne se refait pas aussitôt : on s'oppose
  à lui sur cette chose (``deliberation.changer_etat``), tant qu'il croit l'opposant là.
- N2 : deux recours d'un même besoin ne se relaient pas à chaque événement : le recours en cours
  garde la main tant que son plan n'est pas achevé et que sa méthode le rend encore (``choisir``).
- N4 : on ne prévient de nouveau d'un lieu que s'il a changé depuis qu'on l'a dit, et pas qui a ce
  bien sous les yeux (``deliberation._a_dire``).
"""

from tests.support import lier
from tests.support import canal_constats_anterieur_337
import unittest
from unittest.mock import patch

from donjon.deliberation import contrarie, retenir_refus
from donjon.esprits import croire, lire, memoriser, percevoir_tous
from donjon.geometrie import cases
from donjon.monde import Monde
from donjon.spatial import installer
from tests.support import calme, regarder
from tests.test_temps_etat import decouper, etat_pnj
from tests.test_tensions import attendre, chronique, placer, recharger, relais

PROFILES_MINE = ("bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy")


def compte(m, texte):
    return chronique(m).count(texte)


def salles_de(m, id, depuis=0):
    """Les salles successives où le PNJ est passé depuis la minute ``depuis``, d'après la chronique."""
    return [c["texte"] for c in m.data.get("chronique", [])
            if c["pnj"] == id and " passe dans : " in c["texte"] and c["minute"] >= depuis]


def etat_mine(m):
    """Ce que le monde retient des PNJ de la mine (``test_temps_etat.etat_pnj``, pour ce scénario)."""
    import copy
    from donjon.temps import instant
    return {"corps": {id: {k: m.objets[id].get(k) for k in ("lieu", "position", "orientation")} for id in PROFILES_MINE},
            "esprits": copy.deepcopy({id: m.data["esprits"][id] for id in PROFILES_MINE}),
            "objets": {id: (o["lieu"], o.get("position"), o.get("ouverte"), o.get("verrouillee"), o.get("portions"))
                       for id, o in m.objets.items() if o["type"] != "personnage"},
            "chronique": copy.deepcopy(m.data.get("chronique", [])), "jets": m.data["jets"], "instant": instant(m)}


# --- N1 : ouvrir, fermer, rouvrir ---------------------------------------------------------------

def garde_manger_force():
    """Cas réel (mine 42, minutes 214 à 266) : Odon, affamé au point de ne plus craindre d'être vu
    (faim 96, ``DESESPOIR``), ses crochets en main, devant le garde-manger verrouillé de Mathe, qui
    est là avec sa clé ; le baraquement est éclairé, ils se voient. Les autres sont à la galerie."""
    from donjon.mine import nouveau_mine
    m = nouveau_mine(1985, "fixe")
    installer(m)
    m = calme(m, *PROFILES_MINE)
    sol = sorted(cases(m.data["salles"]["galerie"]))
    for n, k in enumerate(("bram", "gaspard", "josse", "lucien", "remy")):
        placer(m, k, "galerie", sol[2 * n])
    placer(m, "mathe", "baraquement", [3, 4])
    placer(m, "odon", "baraquement", [1, 4])
    regarder(m, "mathe", "odon")
    regarder(m, "odon", "garde_manger")
    m.objets["garde_manger"].update(verrouillee=True, ouverte=False)
    m.objets["cle_garde_manger"]["lieu"] = "mathe"
    m.objets["crochets"]["lieu"] = "odon"
    m.objets["pain_lucien"]["portions"] = 0
    croire(m, "odon", "pain_lucien", "etat", {"disponible": False}, "vu")
    croire(m, "odon", "vivres", "lieu", "garde_manger", "savoir", salle="baraquement", case=[2, 5])
    lire(m, "odon")["besoins"]["faim"] = 96.0
    # Comme cette nuit-là, Mathe se méfie de lui et vient de lui refuser une part : il ne la lui
    # redemande pas, ni ne la lui achète.
    lier(m, "mathe", "odon", False, "vu")
    retenir_refus(m, "odon", "mathe", "demander", "mefiance", objet="vivres")
    m.joueur.update(salle="galerie", position=list(sol[-1]), orientation="nord")
    percevoir_tous(m)
    return recharger(m)


def reserve_forcee():
    """Même nature (Relais) : Brune, affamée à 96, ses crochets en main, devant la réserve verrouillée
    de Gorm, qui est dans le refuge avec sa clé et la garde sous clé."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    for n, id in enumerate(("ilse", "aubin")):
        placer(m, id, "crypte", (2 + n, 3))
    placer(m, "brune", "antichambre", (7, 3))
    placer(m, "marchand", "antichambre", (5, 3))
    regarder(m, "brune", "reserve")
    regarder(m, "marchand", "brune")
    m.objets["crochets"]["lieu"] = "brune"
    # Écarter l'accord, devenu moins cher que l'effraction avec le vrai temps.
    retenir_refus(m, "brune", "marchand", "demander", "mefiance", objet="vivres")
    lire(m, "brune")["besoins"]["faim"] = 96.0
    m.joueur.update(salle="chambre_cloche", position=[3, 7], orientation="nord")
    percevoir_tous(m)
    return recharger(m)


def vivre_avec_jet(m, fois, jet=20):
    """Cinq minutes à la fois, rechargé à chaque fois ; un jet fixé pour que le crochetage réussisse."""
    with patch.object(Monde, "d20", return_value=jet):
        m, _ = attendre(m, fois)
    return m


class GesteDefaitTests(unittest.TestCase):
    def test_odon_ne_rouvre_pas_ce_que_mathe_vient_de_refermer(self):
        # Avant : « Odon ouvre » / « Mathe ferme » 689 fois chacun, toutes les deux secondes, puis
        # crochetage et reverrouillage en boucle, et Mathe qui appelle à l'aide toutes les 2 minutes.
        # Mathe garde sa charge ; aucun tiers ne fournit de repas à Odon.
        from tests.support import sans_souci
        m = vivre_avec_jet(sans_souci(garde_manger_force()), 4)
        ouvre = compte(m, "Odon, nouveau venu ouvre le garde-manger de la cuisinière.")
        ferme = compte(m, "Mathe, cuisinière ferme le garde-manger de la cuisinière.")
        self.assertLessEqual(ouvre, 1)
        self.assertLessEqual(ferme, 1)
        self.assertLessEqual(compte(m, "Odon, nouveau venu crochète la serrure du garde-manger de la cuisinière."), 1)
        self.assertLessEqual(compte(m, "Mathe, cuisinière appelle à l'aide."), 1)
        # Elle a refermé à clé ; il retient qu'elle s'y oppose, et n'y touche plus tant qu'elle est là.
        self.assertTrue(m.objets["garde_manger"]["verrouillee"])
        self.assertFalse(m.objets["garde_manger"]["ouverte"])
        self.assertTrue(contrarie(m, "odon", "garde_manger"))
        i = lire(m, "odon")["intention"]
        self.assertFalse(i and any(x["cible"] == "garde_manger" for x in i["plan"]))

    def test_brune_ne_reforce_pas_la_reserve_sous_les_yeux_de_gorm(self):
        # Même nature, au Relais : un seul essai sous ses yeux ; Gorm referme, Brune n'y revient pas
        # tant qu'il est là. Parti (et elle le constate), l'opposition ne tient plus.
        m = vivre_avec_jet(reserve_forcee(), 4)
        self.assertLessEqual(compte(m, "Brune, voyageuse trempée crochète la serrure de la réserve de vivres."), 1)
        self.assertLessEqual(compte(m, "Brune, voyageuse trempée ouvre la réserve de vivres."), 1)
        self.assertTrue(contrarie(m, "brune", "reserve"))
        self.assertTrue(m.objets["reserve"]["verrouillee"])
        i = lire(m, "brune")["intention"]
        self.assertFalse(i and any(x["cible"] == "reserve" for x in i["plan"]))
        # Gorm parti à la crypte, et Brune le sachant, l'opposition ne tient plus.
        placer(m, "marchand", "crypte", (5, 5))
        croire(m, "brune", "marchand", "lieu", "crypte", "vu", salle="crypte", case=[5, 5])
        m = recharger(m)
        self.assertFalse(contrarie(m, "brune", "reserve"))

    def test_le_joueur_eteint_le_brasero_que_gorm_vient_d_allumer(self):
        # L'auteur est le joueur : Gorm, un briquet en main, vient de rallumer le brasero ; le joueur
        # l'éteint sous ses yeux. Gorm ne le rallume pas lui-même tant qu'il croit le joueur là ;
        # le sachant parti, l'opposition ne tient plus.
        from tests.test_temps_etat import faire
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        for n, id in enumerate(("ilse", "aubin", "brune")):
            placer(m, id, "crypte", (2 + n, 3))
        placer(m, "marchand", "echoppe", (3, 3))
        m.objets["brasero"]["allume"] = False
        m.objets["briquet"].update(lieu="marchand", proprietaire="marchand")
        m.joueur.update(salle="echoppe", position=[4, 5])
        regarder(m, "marchand", "brasero")
        percevoir_tous(m)
        m, _ = attendre(recharger(m), 1)
        self.assertTrue(m.objets["brasero"]["allume"])
        self.assertEqual(compte(m, "Gorm, gardien du relais allume le brasero."), 1)
        regarder(m, "marchand", "joueur")
        regarder(m, "joueur", "brasero")
        faire(m, "eteindre brasero")
        m = recharger(m)
        self.assertFalse(m.objets["brasero"]["allume"])
        self.assertTrue(contrarie(m, "marchand", "brasero"))
        m, _ = attendre(m, 2)
        self.assertFalse(m.objets["brasero"]["allume"])
        self.assertEqual(compte(m, "Gorm, gardien du relais allume le brasero."), 1)
        # Le joueur parti, et Gorm le sachant, l'opposition ne tient plus : le feu est de nouveau à lui.
        m.joueur.update(salle="chambre_cloche", position=[3, 7])
        croire(m, "marchand", "joueur", "lieu", "chambre_cloche", "vu", salle="chambre_cloche", case=[3, 7])
        m = recharger(m)
        self.assertFalse(contrarie(m, "marchand", "brasero"))

    def test_meme_laps_decoupe_meme_monde(self):
        with patch.object(Monde, "d20", return_value=20):
            d_un_bloc, morcele = decouper(garde_manger_force, 4)
        self.assertEqual(etat_mine(d_un_bloc), etat_mine(morcele))


# --- N2 : la lumière et l'abri -------------------------------------------------------------------

def palier_menace():
    """Cas réel (crue 3, minutes 378 et suivantes) : l'eau baisse, elle tient encore le Palier des
    vannes (15 cm), la Salle des vannes et la Conduite basse. Brune et Ilse, la sécurité pressante,
    sont l'une dans la Galerie de ronde (que le jour éclaire en pénombre), l'autre dans le palier, noir ;
    Gorm et Aubin, qu'elles croient fiables, sont au refuge éclairé, par la porte étanche ouverte. Avant :
    de la galerie, l'abri auprès de Gorm les menait au palier ; là, dans un lieu où elles croient l'eau,
    l'abri devenait le plus haut lieu éclairé, la galerie ; arrivées, de nouveau le refuge… et la
    lumière, dans le noir du palier, en faisait autant (946 et 747 passages dans la nuit)."""
    from tests.test_eau import FIXES, attendre as attendre_crue, crue
    m = calme(crue(FIXES), "marchand", "brune", "ilse", "aubin")
    m, _ = attendre_crue(m, 404)
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    placer(m, "marchand", "antichambre", (1, 1))
    placer(m, "aubin", "antichambre", (1, 2))
    placer(m, "brune", "chambre_cloche", (1, 11))
    placer(m, "ilse", "beffroi", (7, 3))
    m.objets["porte"].update(verrouillee=False, ouverte=True)
    m.objets["lanterne"]["allume"] = False
    m.joueur.update(salle="antichambre", position=[0, 4], orientation="nord")
    for i, autre in (("brune", "ilse"), ("ilse", "brune")):
        for x in ("marchand", "aubin", autre):
            lier(m, i, x, True, "vu")
        croire(m, i, "marchand", "lieu", "antichambre", "vu", salle="antichambre", case=[1, 1])
        croire(m, i, "aubin", "lieu", "antichambre", "vu", salle="antichambre", case=[1, 2])
        croire(m, i, "antichambre", "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "vu")
        croire(m, i, "porte", "etat", {"ouverte": True}, "vu")
        croire(m, i, "porte", "verrouillee", False, "vu")
        lire(m, i)["besoins"]["securite"] = 75.0
        # Ce cas contrôle la tenue d'un abri déjà choisi pendant la traversée.
        # Le déclarer évite d'hériter du but issu de la nuit préparatoire, qui
        # change avec les relations ; sans ce but, Ilse choisit légitimement le haut.
        from tests.test_marche import intention
        intention(m, i, [{"operation": "aller", "lieu": "antichambre"}],
                  but={"type": "abri", "lieu": "antichambre"}, motif="securite")
        # Scène d'auteur : elles ont mesuré la baisse annoncée ici. Les
        # anciennes mesures de la nuit préparatoire peuvent encore leur
        # faire croire à une montée, et justifier un second trajet vers le haut.
        from donjon import eau
        t = m.data['minutes']
        niveau = eau.niveau(m, t)
        precedent = eau.niveau(m, t - eau.REPERE)
        pente = round((niveau - precedent) * 60 / eau.REPERE)
        assert pente < 0
        for connu in lire(m, i)['croyances'].values():
            connu.pop('eau', None)
        croire(m, i, 'beffroi', 'eau', niveau - eau.altitude(m, 'beffroi'), 'vu',
               niveau=niveau, repere=[t, niveau], montee=pente)
    percevoir_tous(m)
    # La nuit préparatoire peut encore enregistrer un passage à la minute 404,
    # avant le placement d'auteur. Le contrôle porte sur la scène qui commence ici.
    m.data["chronique"] = []
    return recharger(m)


def galerie_ou_refuge():
    """Même nature, sans l'eau (Relais) : Brune dans la galerie, Ilse dans le palier noir, chacune
    croyant l'autre fiable, Gorm et Aubin au refuge. Avant : l'abri de chacune suivait l'autre, qui
    bougeait, et la lumière renvoyait du palier à la galerie (23 passages en quinze minutes)."""
    m = calme(relais(), "marchand", "brune", "ilse", "aubin")
    placer(m, "marchand", "antichambre", (1, 1))
    placer(m, "aubin", "antichambre", (1, 2))
    placer(m, "brune", "chambre_cloche", (1, 11))
    placer(m, "ilse", "beffroi", (7, 3))
    for i, autre in (("brune", "ilse"), ("ilse", "brune")):
        for x in ("marchand", "aubin", autre):
            lier(m, i, x, True, "vu")
        croire(m, i, "antichambre", "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "vu")
        croire(m, i, "beffroi", "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
        croire(m, i, "chambre_cloche", "etat", {"eclairee": True, "niveau": 1, "propre": 1}, "vu")
        croire(m, i, "crypte", "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
        croire(m, i, "porte", "etat", {"ouverte": True}, "vu")
        croire(m, i, "porte", "verrouillee", False, "vu")
        lire(m, i)["besoins"]["securite"] = 75.0
    m.objets["porte"].update(verrouillee=False, ouverte=True)
    m.objets["lanterne"]["allume"] = False
    m.joueur.update(salle="antichambre", position=[0, 4], orientation="nord")
    percevoir_tous(m)
    return recharger(m)


class RecoursTests(unittest.TestCase):
    @canal_constats_anterieur_337
    def test_par_le_palier_menace_elles_gagnent_un_abri_sans_alternance(self):
        # Sur ``main`` : 16 et 19 passages entre la galerie et le palier en quinze minutes.
        m, _ = attendre(palier_menace(), 3)
        for id in ("brune", "ilse"):
            passages = salles_de(m, id, 404)
            self.assertLessEqual(len(passages), 4, passages)
            # Les constats partagés peuvent changer son premier abri : un détour
            # reste possible, jamais l'alternance répétée galerie/palier.
            self.assertLessEqual(sum("Galerie de ronde" in t for t in passages), 1, passages)
            i = lire(m, id)["intention"]
            self.assertIn(i["but"], ({"type": "abri", "lieu": m.objets[id]["lieu"]}, {"type": "lumiere"}))
            self.assertEqual(i["plan"][-1]["operation"], "abriter")
            self.assertEqual(i["plan"][-1]["lieu"], m.objets[id]["lieu"])
            from donjon.eau import noyee_crue
            self.assertFalse(noyee_crue(m, id, m.objets[id]["lieu"]))

    def test_palier_menace_meme_laps_decoupe_meme_monde(self):
        d_un_bloc, morcele = decouper(palier_menace, 404 + 10)
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))

    def test_brune_et_ilse_ne_se_croisent_plus_entre_la_galerie_et_le_palier(self):
        # Sur ``main`` : 23 passages entre la galerie et le palier en quinze minutes.
        # L'abri en route garde la main ; qui gagne d'abord la lumière peut
        # s'y rassurer avant de rejoindre sa compagnie, sans refaire la boucle.
        m, _ = attendre(galerie_ou_refuge(), 3)
        for id in ("brune", "ilse"):
            passages = salles_de(m, id)
            self.assertLessEqual(sum("Galerie de ronde" in t for t in passages), 1, passages)
            # Le séjour du recours de lumière peut laisser changer le chemin
            # avant de repartir : quatre salles distinctes restent un trajet,
            # pas l'ancienne alternance entre le palier et la galerie.
            self.assertLessEqual(len(passages), 4, passages)
            self.assertEqual(len(passages), len(set(passages)), passages)
            i = lire(m, id)["intention"]
            self.assertIn(i["but"], ({"type": "abri", "lieu": m.objets[id]["lieu"]}, {"type": "lumiere"}))
            self.assertEqual(i["plan"][-1]["operation"], "abriter")
            self.assertEqual(i["plan"][-1]["lieu"], m.objets[id]["lieu"])

    def test_meme_laps_decoupe_meme_monde(self):
        d_un_bloc, morcele = decouper(galerie_ou_refuge, 3)
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))

    def test_seule_les_pas_du_joueur_dans_le_noir_ne_la_font_pas_rebrousser(self):
        # Même nature, seule : Brune part de la galerie pour le refuge ; le joueur, sa lanterne
        # éteinte, va et vient dans le palier noir par pas chassés. Chaque pas qu'elle entend la fait
        # choisir de nouveau. Sur ``main`` : 22 passages entre la galerie et le palier en 4 minutes.
        from donjon.temps import instant
        from tests.test_temps_etat import faire
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        for n, id in enumerate(("marchand", "aubin", "ilse")):
            placer(m, id, "antichambre", (1, 1 + n))
        placer(m, "brune", "chambre_cloche", (1, 11))
        for x in ("marchand", "aubin", "ilse"):
            lier(m, "brune", x, True, "vu")
            # La scène suppose un refuge connu : le placement physique des
            # compagnons hors de vue ne donne pas cette information à Brune.
            croire(m, "brune", x, "lieu", "antichambre", "savoir",
                   salle="antichambre", case=list(m.objets[x]["position"]))
        croire(m, "brune", "antichambre", "etat", {"eclairee": True, "niveau": 2, "propre": 2}, "vu")
        for s in ("beffroi", "crypte"):
            croire(m, "brune", s, "etat", {"eclairee": False, "niveau": 0, "propre": 0}, "vu")
        croire(m, "brune", "porte", "etat", {"ouverte": True}, "vu")
        croire(m, "brune", "porte", "verrouillee", False, "vu")
        lire(m, "brune")["besoins"]["securite"] = 75.0
        m.objets["porte"].update(verrouillee=False, ouverte=True)
        m.objets["lanterne"]["allume"] = False
        m.joueur.update(salle="beffroi", position=[4, 4], orientation="est")
        percevoir_tous(m)
        m, n = recharger(m), 0
        while instant(m) < 4 * 600:
            faire(m, "chasse est" if n % 2 == 0 else "chasse ouest")
            n += 1
            if n % 10 == 0:
                m = recharger(m)
        m = recharger(m)
        passages = salles_de(m, "brune")
        self.assertEqual(sum("Galerie de ronde" in t for t in passages), 0, passages)
        self.assertEqual(m.objets["brune"]["lieu"], "antichambre")


# --- N4 : prévenir de ce qu'on a déjà dit --------------------------------------------------------

def ballot_rendu():
    """Cas réel (auberge 3, minutes 487 à 500) : Hugues a vu Lucien déplacer le ballot d'Anselme ; il
    l'a dit à Anselme, qui l'a repris et posé lui-même dans la chambre au poêle, où il se tient.
    Hugues le voit là, chaque minute. Avant : « le ballot de soie est dans la chambre au poêle »,
    redit 26 fois, la croyance de lieu de Hugues se renouvelant à chaque regard."""
    from donjon.auberge import nouveau_auberge
    m = nouveau_auberge(1985, "fixe")
    installer(m)
    m = calme(m, *[k for k, o in m.objets.items() if o.get("profil")])
    placer(m, "anselme", "chambre_chaude", [2, 2])
    placer(m, "hugues", "chambre_chaude", [1, 1])
    regarder(m, "hugues", "anselme")
    m.objets["ballot"].update(lieu="chambre_chaude", position=[2, 3], position_salle="chambre_chaude")
    m.data["minutes"] = 20
    memoriser(m, "hugues", {"type": "vu_agir", "auteur": "lucien", "operation": "poser", "objet": "ballot",
                            "lieu": {"valeur": "etable", "salle": "etable", "case": [3, 2], "minute": 10}})
    memoriser(m, "hugues", {"type": "a_prevenir", "victime": "anselme", "auteur": "lucien"})
    lier(m, "hugues", "lucien", False, "vu")
    m.joueur.update(salle="dortoir", position=[1, 1])
    percevoir_tous(m)
    return recharger(m)


class PrevenirTests(unittest.TestCase):
    def test_hugues_ne_redit_pas_a_anselme_ou_est_le_ballot_qu_il_a_sous_les_yeux(self):
        m, _ = attendre(ballot_rendu(), 4)
        textes = chronique(m)
        self.assertEqual([t for t in textes if t.startswith("Hugues dit à Anselme que le ballot")], [])
        self.assertEqual(len([t for t in textes if t.startswith("Hugues dit à Anselme que Lucien est peu fiable")]), 1)

    def test_un_lieu_dit_ne_se_redit_que_s_il_change(self):
        # Même nature : Anselme est au dortoir, le ballot à l'étable. Hugues le lui dit une fois ; le
        # revoir là n'y change rien ; le ballot déplacé ailleurs, il le lui dit de nouveau.
        from donjon.deliberation import _plan_prevenir
        m = ballot_rendu()
        placer(m, "anselme", "dortoir", [0, 0])
        m.objets["ballot"].update(lieu="etable", position=[3, 2], position_salle="etable")
        croire(m, "hugues", "ballot", "lieu", "etable", "vu", salle="etable", case=[3, 2])
        croire(m, "hugues", "anselme", "lieu", "dortoir", "vu", salle="dortoir", case=[0, 0])
        memoriser(m, "hugues", {"type": "dit", "a": "anselme", "sujet": "lucien", "attribut": "fiable", "valeur": False})
        m = recharger(m)
        dits = [x["contenu"] for x in _plan_prevenir(m, "hugues")[1] if x["operation"] == "dire"]
        self.assertEqual(dits, [{"sujet": "ballot", "attribut": "lieu", "valeur": "etable"}])
        memoriser(m, "hugues", {"type": "dit", "a": "anselme", "sujet": "ballot", "attribut": "lieu", "valeur": "etable"})
        m.data["minutes"] += 5
        croire(m, "hugues", "ballot", "lieu", "etable", "vu", salle="etable", case=[3, 2])   # Il le revoit.
        m = recharger(m)
        self.assertIsNone(_plan_prevenir(m, "hugues"))
        croire(m, "hugues", "ballot", "lieu", "grenier", "vu", salle="grenier", case=[1, 1])
        m = recharger(m)
        dits = [x["contenu"] for x in _plan_prevenir(m, "hugues")[1] if x["operation"] == "dire"]
        self.assertEqual(dits, [{"sujet": "ballot", "attribut": "lieu", "valeur": "grenier"}])


if __name__ == "__main__":
    unittest.main()
