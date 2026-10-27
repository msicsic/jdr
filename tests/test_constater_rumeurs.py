"""Ce qu'un PNJ constate, ce qu'il raconte, comment il retrouve quelqu'un.

- Un geste manqué sur un objet qu'il croyait dans un contenant ouvert : sa main rencontre le
  contenant fermé, il l'apprend (fermé, verrouillé ou non), et croit toujours l'objet dedans.
- Le témoin d'un geste qui déplace un objet voit où il va : la nouvelle porte ce lieu, qui la
  croit en tire une croyance de lieu, et le volé va reprendre son bien.
- Chercher quelqu'un qu'on ne voit pas : on l'appelle ; il répond de la voix, on le croit là d'où
  vient la réponse ; de près, on se parle même dans le noir.

Chaque test vérifie l'état du monde après rechargement, et ce que le joueur lit quand il est là.
"""

from tests.support import lier, relation
import unittest
from unittest.mock import patch

from tests.scenarios_contractuels import nouveau_auberge
from donjon.esprits import connaitre, croire, lire, memoriser, percevoir_tous
from donjon.geometrie import position_entree
from donjon.perception import eclairage
from donjon.pnj import se_parler
from donjon.spatial import installer
from tests.support import calme, refusee, regarder, sans_evacues
from tests.test_temps_etat import intention, plan
from tests.test_tensions import attendre, chronique, placer, recharger, relais


def auberge():
    m = nouveau_auberge(1985, "fixe")
    installer(m)
    return m


def gestes(m, id):
    return [c["texte"] for c in m.data.get("chronique", [])
            if c["pnj"] == id and c["nature"] not in ("deplacement", "ouie")]


def lieu_cru(m, id, objet):
    c = lire(m, id)["croyances"].get(objet, {}).get("lieu")
    return None if c is None else (c["valeur"], c["source"])


class ContenantFermeTests(unittest.TestCase):
    @patch("donjon.agendas._naissances", return_value=None)
    def test_brune_trouve_la_reserve_refermee_a_cle_et_la_croit_toujours_pleine(self, _naissance):
        """Cas réel (Relais) : Brune croit la réserve ouverte ; Gorm l'a refermée à clé. Dans la
        pénombre, elle tend la main vers les vivres : elle apprend la réserve fermée et
        verrouillée, croit toujours les vivres dedans, et va chercher ses crochets."""
        m = refusee(sans_evacues(relais()))
        # La scène du contenant fermé n'offre pas de bois propre à négocier.
        from tests.test_entretenir import sans
        sans(m, 'bois_bateliere')
        # Même ses outils ne convaincront pas Gorm : on vérifie ici le constat du verrou.
        from donjon import relations
        lire(m, "marchand")["relations"]["brune"] = relations._nouvelle({"confiance": 10})
        placer(m, "marchand", "crypte", position_entree(m, "crypte"))
        placer(m, "brune", "antichambre", [6, 3])
        croire(m, "brune", "marchand", "lieu", "crypte", "vu", salle="crypte", case=None)
        croire(m, "brune", "reserve", "etat", {"ouverte": True}, "vu")
        croire(m, "brune", "reserve", "verrouillee", False, "vu")
        m.objets["brune"]["profil"]["valeurs"]["honnetete"] = 20
        lire(m, "brune")["besoins"]["faim"] = 90.0
        self.assertLess(eclairage(m, "antichambre", [6, 3])["niveau"], 2)
        m, _ = attendre(recharger(m))
        croyances = lire(m, "brune")["croyances"]
        self.assertEqual(croyances["reserve"]["verrouillee"]["valeur"], True)
        self.assertEqual(croyances["reserve"]["verrouillee"]["source"], "essai")
        self.assertFalse(croyances["reserve"]["etat"]["valeur"]["ouverte"])
        self.assertEqual(croyances["vivres"]["lieu"]["valeur"], "reserve")
        # Elle n'est pas restée sans plan : elle a pris ses crochets pour forcer la réserve. (Gorm, qui
        # garde le refuge, va voir dès qu'il entend un bruit ; à portée de ses yeux ou de son oreille,
        # elle guette son occasion.)
        m, _ = attendre(m, 2)
        self.assertIn("Brune, batelière évacuée prend la trousse de crochets.", gestes(m, "brune"))
        self.assertIn(("crocheter", "reserve"), [(x["operation"], x["cible"]) for x in lire(m, "brune")["intention"]["plan"]])

    def test_lucien_trouve_le_coffre_ferme_dans_le_noir(self):
        """Même nature (auberge) : Lucien croit le coffre d'Anselme ouvert et veut le ballot ; le
        poêle est éteint. Sa main rencontre le coffre fermé à clé : il l'apprend et le force."""
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine")
        m.objets["poele"]["allume"] = False
        placer(m, "anselme", "salle_commune", [1, 1])
        placer(m, "lucien", "chambre_chaude", [1, 3])
        croire(m, "lucien", "anselme", "lieu", "salle_commune", "vu", salle="salle_commune", case=[1, 1])
        croire(m, "lucien", "coffre_marchand", "etat", {"ouverte": True}, "vu")
        croire(m, "lucien", "coffre_marchand", "verrouillee", False, "vu")
        lire(m, "lucien")["besoins"]["biens"] = 90.0
        self.assertEqual(eclairage(m, "chambre_chaude", [1, 3])["niveau"], 0)
        m, _ = attendre(recharger(m))
        croyances = lire(m, "lucien")["croyances"]
        self.assertEqual((croyances["coffre_marchand"]["verrouillee"]["valeur"],
                          croyances["coffre_marchand"]["verrouillee"]["source"]), (True, "essai"))
        self.assertEqual(croyances["ballot"]["lieu"]["valeur"], "coffre_marchand")
        m, _ = attendre(m, 3)
        self.assertIn("Lucien, voyageur au manteau gris s'acharne sur la serrure du coffre ferré.",
                      gestes(m, "lucien"))

    def test_ouvert_et_vide_il_constate_l_absence(self):
        """Le contenant est ouvert et l'objet n'y est plus : c'est l'objet qui manque."""
        m = refusee(sans_evacues(relais()))
        m.objets["reserve"].update(verrouillee=False, ouverte=True)
        m.objets["vivres"].update(lieu="echoppe", position=[1, 1], position_salle="echoppe")
        placer(m, "marchand", "crypte", position_entree(m, "crypte"))
        placer(m, "brune", "antichambre", [6, 3])
        croire(m, "brune", "reserve", "etat", {"ouverte": True}, "vu")
        croire(m, "brune", "vivres", "lieu", "reserve", "vu", salle="antichambre", case=[8, 3])
        m.objets["brune"]["profil"]["valeurs"]["honnetete"] = 20
        lire(m, "brune")["besoins"]["faim"] = 90.0
        m, _ = attendre(recharger(m))
        self.assertIsNone(lire(m, "brune")["croyances"]["vivres"]["lieu"]["valeur"])


class RumeurAvecLieuTests(unittest.TestCase):
    def test_hugues_voit_lucien_poser_le_ballot_et_anselme_va_le_reprendre(self):
        """Cas réel (auberge, graine 42) : Lucien pose le ballot d'Anselme à l'étable sous les yeux
        d'Hugues. Hugues sait où il est ; il prévient Anselme, et lui dit où est le ballot ;
        Anselme va le reprendre et le repose dans sa chambre."""
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        m.objets["ballot"]["lieu"] = "lucien"
        placer(m, "lucien", "etable", [3, 2])
        placer(m, "hugues", "etable", [5, 2])
        placer(m, "joss", "cuisine", [1, 1])
        placer(m, "anselme", "salle_commune", [2, 2])
        croire(m, "hugues", "anselme", "lieu", "salle_commune", "vu", salle="salle_commune", case=[2, 2])
        regarder(m, "hugues", "lucien")
        intention(m, "lucien", plan("poser", "ballot", lieu="etable"), but="pulsion", motif="biens")
        m.joueur.update(salle="salle_commune", position=[5, 4])
        m.data["visitees"] = sorted(set(m.data["visitees"]) | {"salle_commune", "etable"})
        m.data["connus"] = sorted(set(m.data["connus"]) | {"ballot", "hugues", "anselme", "lucien"})
        from tests.support import presentes
        presentes(m,"hugues","anselme","lucien")
        connaitre(m, "joueur", "hugues")  # Il a déjà vu Hugues : il reconnaît sa voix.
        m, texte = attendre(recharger(m))
        vu = next(s for s in lire(m, "hugues")["memoire"] if s["type"] == "vu_agir")
        self.assertEqual((vu["operation"], vu["lieu"]["valeur"], vu["lieu"]["salle"], vu["lieu"]["case"]),
                         ("poser", "etable", "etable", [3, 2]))
        self.assertIn("Hugues dit à Anselme que le ballot de soie est dans l'étable (crue).", chronique(m))
        # Le joueur, dans la salle commune, l'entend en clair : il connaît la voix, le ballot, l'étable.
        self.assertIn("Hugues dit à Anselme que le ballot de soie est dans l'étable.", texte)
        # Anselme est allé le reprendre, et l'a reposé dans sa chambre (il a d'abord offert la tâche,
        # en vain : quelques minutes de plus).
        self.assertIn("Anselme, marchand drapier prend le ballot de soie.", gestes(m, "anselme"))
        m, _ = attendre(m)
        self.assertEqual(m.objets["ballot"]["lieu"], "chambre_chaude")
        # Qui l'a entendu dire puis voit Anselme le porter ne tient pas Hugues pour menteur : un
        # objet qu'on voit dans les mains de quelqu'un a pu être déplacé depuis.
        self.assertFalse(any(" ment " in t or t.endswith(" ment.") for t in chronique(m)))

    def test_ilse_dit_a_gorm_ou_brune_a_pose_ses_vivres(self):
        """Même nature (Relais, une confidence) : Ilse voit Brune poser les vivres de Gorm à
        l'échoppe ; elle le lui glisse aux vannes, avec le lieu ; Gorm, qui les croyait dans la
        réserve, va les rapporter au refuge."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        placer(m, "aubin", "chambre_cloche", [5, 5])
        m.objets["vivres"]["lieu"] = "brune"
        placer(m, "brune", "echoppe", [4, 3])
        placer(m, "ilse", "echoppe", [5, 4])
        placer(m, "marchand", "crypte", [4, 3])
        regarder(m, "ilse", "brune")
        intention(m, "brune", plan("poser", "vivres", lieu="echoppe"), but="pulsion", motif="faim")
        m, _ = attendre(recharger(m))
        self.assertEqual(lieu_cru(m, "ilse", "vivres"), ("echoppe", "vu"))
        # Placement d'auteur : Ilse retrouve Gorm aux vannes, où le joueur se tient.
        placer(m, "ilse", "crypte", [3, 3])
        regarder(m, "ilse", "marchand")
        regarder(m, "marchand", "ilse")
        m.joueur.update(salle="crypte", position=[5, 5])
        m.data["visitees"] = sorted(set(m.data["visitees"]) | {"crypte", "echoppe"})
        m.data["connus"] = sorted(set(m.data["connus"]) | {"vivres", "brune", "ilse", "marchand"})
        connaitre(m, "joueur", "ilse")
        m, texte = attendre(recharger(m))
        self.assertIn("Ilse glisse à Gorm que Brune a posé les vivres du refuge dans la conduite basse.", texte)
        rumeur = next(s for s in lire(m, "marchand")["memoire"] if s["type"] == "rumeur")
        self.assertEqual(rumeur["evenement"]["lieu"]["valeur"], "echoppe")
        m, _ = attendre(m, 2)
        self.assertIn("Gorm, gardien du relais prend les vivres du refuge.", gestes(m, "marchand"))
        self.assertEqual(m.objets["vivres"]["lieu"], "antichambre")

    def test_qui_l_a_vu_ailleurs_depuis_tait_le_lieu(self):
        """Une nouvelle ne répète que ce qu'on croit encore : Ilse a vu depuis les vivres ailleurs ;
        elle dit le geste sans le lieu, et Gorm n'en tire aucun lieu."""
        m = calme(relais(), "marchand", "brune", "ilse", "aubin")
        memoriser(m, "ilse", {"type": "vu_agir", "auteur": "brune", "operation": "poser", "objet": "vivres",
                              "lieu": {"valeur": "echoppe", "salle": "echoppe", "case": [4, 3], "minute": 0}})
        lier(m, "ilse", "brune", False, "vu")
        m.data["minutes"] = 3
        croire(m, "ilse", "vivres", "lieu", "reserve", "vu", salle="antichambre", case=[8, 3])
        placer(m, "ilse", "crypte", [3, 3])
        placer(m, "marchand", "crypte", [4, 3])
        placer(m, "brune", "echoppe", [1, 1])
        regarder(m, "ilse", "marchand")
        regarder(m, "marchand", "ilse")
        m, _ = attendre(recharger(m))
        self.assertIn("Ilse dit à Gorm que Brune a posé les vivres du refuge (crue).", chronique(m))
        self.assertEqual(lieu_cru(m, "marchand", "vivres"), ("reserve", "savoir"))


class ChercherQuelquUnTests(unittest.TestCase):
    def mireille_cherche_odile(self):
        """Mireille a faim, sa marmite est vide ; elle ne sait où est Odile, qui garde les vivres.
        Odile est au grenier, dans le noir ; le bougeoir de Mireille est éteint."""
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        m.objets["marmite"]["portions"] = 0
        m.objets["bougeoir_mireille"]["allume"] = False
        croire(m, "mireille", "marmite", "etat", {"disponible": False}, "vu")
        placer(m, "odile", "grenier", [1, 1])
        placer(m, "mireille", "cuisine", [3, 3])
        croire(m, "mireille", "odile", "lieu", None, "essai", salle=None, case=None)
        # Le grenier est le lieu où elle est passée le moins récemment : elle l'y cherche d'abord.
        m.data["minutes"] = 2
        for s in m.data["salles"]:
            lire(m, "mireille")["visites"][s] = 0 if s == "grenier" else 1
        lire(m, "mireille")["besoins"]["faim"] = 90.0
        self.assertEqual(eclairage(m, "grenier", [1, 1])["niveau"], 0)
        return m

    def test_mireille_appelle_odile_dans_le_grenier_noir(self):
        """Cas réel (auberge, graine 7 : Mireille tournait 70 minutes sans voir Odile dans le
        noir) : elle l'appelle, Odile répond, Mireille la croit là d'où vient sa voix, et lui
        demande sa part sans la voir."""
        m = self.mireille_cherche_odile()
        m.joueur.update(salle="grenier", position=[6, 3])
        m.data["visitees"] = sorted(set(m.data["visitees"]) | {"grenier"})
        m.data["connus"] = sorted(set(m.data["connus"]) | {"mireille", "odile"})
        for x in ("mireille", "odile"):
            connaitre(m, "joueur", x)  # Il les a déjà vues : il reconnaît leurs voix.
        from tests.support import presentes
        presentes(m,'mireille','odile')  # Leurs noms ont également été présentés.
        m, texte = attendre(recharger(m))
        self.assertIn("Mireille appelle : « Odile ? »", chronique(m))
        # Elles conviennent de qui vient (``appel``) : une part de ce qu'Odile n'a pas sur elle.
        self.assertIn("Odile répond : « Qu'est-ce que tu veux ? »", chronique(m))
        self.assertIn("Odile répond : « Ici, viens ! »", chronique(m))
        self.assertTrue(any(t.startswith("Mireille demande une part des vivres du cellier à Odile ")
                            for t in chronique(m)))
        # Le joueur, au grenier, entend l'appel et la réponse sans rien voir.
        self.assertIn("Tu entends, tout près : Mireille appelle : « Odile ? »", texte)
        self.assertIn("Odile répond : « Ici, viens ! »", texte)
        m, _ = attendre(m)
        self.assertIn("Odile appelle Mireille et lui donne une part des vivres du cellier.", chronique(m))

    def test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix(self):
        """Le joueur dans le noir, qui n'a jamais entendu Mireille ni Odile : il entend des voix
        inconnues. Il saisit les mots d'un appel, « Odile ? », puis une autre voix qui y répond : celle
        qu'on appelle Odile, un ouï-dire et non une identité (branche ``voix-inconnues``) ; rien ne lui
        dit qui appelait. Il pourrait répondre à ces voix, que le MJ ne connaît que comme des voix
        inconnues (``voix.designation``), sans leur identifiant."""
        import json
        m = self.mireille_cherche_odile()
        m.joueur.update(salle="grenier", position=[6, 3])
        m.data["visitees"] = sorted(set(m.data["visitees"]) | {"grenier"})
        m, texte = attendre(recharger(m))
        self.assertTrue(any(t.startswith("Mireille demande une part des vivres du cellier à Odile ")
                            for t in chronique(m)))
        self.assertIn("Tu entends, tout près, une voix inconnue appeler : « Odile ? »", texte)
        self.assertIn("Tu entends, tout près, une voix qu'on appelle Odile répondre : « Qu'est-ce que tu veux ? »", texte)
        self.assertNotIn("Mireille", texte)
        self.assertNotIn("Odile répond :", texte)
        self.assertEqual(sorted(m.data["entendus"]), ["mireille", "odile"])
        from donjon.voix import designation, nom_pour_joueur
        for x in ("mireille", "odile"):
            self.assertTrue(designation(m, x).startswith("voix_"))
        self.assertEqual(nom_pour_joueur(m, "mireille"), "une voix inconnue")
        self.assertEqual(nom_pour_joueur(m, "odile"), "une voix qu'on appelle Odile")
        self.assertNotIn("odile", m.data["voix_connues"])
        interlocuteurs = m.contexte()["interlocuteurs"]
        self.assertTrue(all(k.startswith("voix_") for k in interlocuteurs))
        self.assertNotIn("Mireille", json.dumps(interlocuteurs, ensure_ascii=False))
        self.assertNotIn("odile", json.dumps(interlocuteurs, ensure_ascii=False))

    def test_qui_se_mefie_ne_repond_pas(self):
        m = self.mireille_cherche_odile()
        lier(m, "odile", "mireille", False, "vu")
        m, _ = attendre(recharger(m))
        self.assertIn("Mireille appelle : « Odile ? »", chronique(m))
        self.assertFalse([t for t in chronique(m) if t.startswith("Odile répond")])
        # Sans réponse, elle ne la croit pas au grenier sur sa voix. (Odile, qui entend dans son grenier
        # noir des pas qu'elle ne sait à qui prêter, va voir de près d'où ils venaient, branche
        # ``ouie-temoins`` : elle sort et Mireille finit par la voir ailleurs.)
        self.assertNotEqual((lieu_cru(m, "mireille", "odile") or (None,))[0], "grenier")

    def test_hugues_cherche_anselme_pour_le_prevenir(self):
        """Même nature (auberge) : Hugues a vu Lucien forcer le coffre d'Anselme et veut le
        prévenir ; Anselme est au dortoir, dans le noir. Hugues l'appelle, Anselme répond, et
        Hugues le prévient de vive voix sans le voir."""
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        m.objets["lanterne_hugues"]["allume"] = False
        placer(m, "anselme", "dortoir", [0, 0])
        placer(m, "hugues", "couloir", list(position_entree(m, "couloir")))
        croire(m, "hugues", "anselme", "lieu", None, "essai", salle=None, case=None)
        memoriser(m, "hugues", {"type": "vu_agir", "auteur": "lucien", "operation": "forcer",
                                "objet": "coffre_marchand"})
        memoriser(m, "hugues", {"type": "a_prevenir", "victime": "anselme", "auteur": "lucien"})
        lier(m, "hugues", "lucien", False, "vu")
        m.data["minutes"] = 2
        for s in m.data["salles"]:
            lire(m, "hugues")["visites"][s] = 0 if s == "dortoir" else 1
        lire(m, "hugues")["besoins"]["devoir"] = 90.0
        self.assertEqual(eclairage(m, "dortoir", [0, 0])["niveau"], 0)
        m, _ = attendre(recharger(m))
        self.assertIn("Hugues appelle : « Anselme ? »", chronique(m))
        self.assertIn("Anselme répond : « Qu'est-ce que tu veux ? »", chronique(m))
        self.assertIn("Hugues dit à Anselme que Lucien est peu fiable (crue).", chronique(m))
        from donjon.relations import envers
        self.assertEqual(envers(m, "anselme", "lucien")["confiance"], 52)
        self.assertEqual(envers(m, "anselme", "lucien")["motifs"][-1]["type"], "rumeur")


class ParlerALaVoixTests(unittest.TestCase):
    """Se parler, c'est saisir chacun les mots de l'autre (ouïe commune) et savoir qui parle (le
    voir, ou reconnaître sa voix)."""

    def test_par_la_porte_du_cellier_ouverte_puis_fermee(self):
        """Mireille, à la cuisine contre la porte du cellier ; Odile de l'autre côté, dans le noir.
        Porte ouverte, elles se parlent à quelques pas ; porte fermée, seulement collées contre."""
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        placer(m, "mireille", "cuisine", [2, 0])
        placer(m, "odile", "cellier", [2, 1])
        m.objets["porte_cellier"]["ouverte"] = True
        self.assertTrue(se_parler(m, "mireille", "odile"))
        percevoir_tous(m)
        m = recharger(m)
        # Vue par la porte, ou entendue : elle la sait au cellier, à sa case.
        self.assertEqual(lieu_cru(m, "mireille", "odile")[0], "cellier")
        self.assertEqual(lire(m, "mireille")["croyances"]["odile"]["lieu"]["case"], [2, 1])
        m.objets["porte_cellier"]["ouverte"] = False
        self.assertFalse(se_parler(m, "mireille", "odile"))
        placer(m, "odile", "cellier", [2, 3])
        self.assertTrue(se_parler(recharger(m), "mireille", "odile"))

    def test_odon_demande_sa_part_a_mathe_dans_le_noir(self):
        """Cas réel (mine, graine 1985, 420 minutes) : au baraquement noir, Odon affamé demande sa
        part à Mathe, qui reconnaît sa voix et lui répond."""
        m = recharger(self.baraquement_noir())
        from donjon.moteur import Moteur, proposition
        for _ in range(120):
            moteur = Moteur(m)
            moteur.executer(moteur.preparer(proposition("attendre", "1")))
            m = recharger(m)
            if any("Odon demande une part" in c and "à Mathe" in c for c in chronique(m)):
                break
        # Les autres marchés peuvent consommer des jets : l'issue ne définit pas la voix reconnue.
        self.assertTrue(any(c in chronique(m) for c in (
            "Odon demande une part des vivres de la cuisine à Mathe (refus).",
            "Odon demande une part des vivres de la cuisine à Mathe (promis).")))
        # Elle le situe à sa voix, quel que soit le résultat de la demande.
        self.assertEqual(lieu_cru(m, "mathe", "odon"), (m.objets["odon"]["lieu"], "entendu"))

    def test_une_voix_jamais_entendue_ne_se_reconnait_pas(self):
        """Même nature, mais Mathe n'a jamais entendu Odon : c'est une voix inconnue, qu'elle ne
        prête à personne. Elle l'entend pourtant lui demander sa part ; inquiète (sa sécurité presse
        plus que son courage ne la retient), elle répond « Qui va là ? » ; Odon se nomme, et elle le
        croit là sur sa parole, sans lui accorder plus qu'à un inconnu. Ils sont dans la réserve
        noire (au baraquement, le poêle qu'on viendrait rallumer les éclairerait)."""
        m = self.baraquement_noir(salle="reserve")
        lire(m, "mathe")["voix"].remove("odon")
        lire(m, "mathe")["croyances"].pop("odon", None)
        lire(m, "mathe")["besoins"]["securite"] = 60.0
        # Observer l'échange à son instant : désormais Odon peut ensuite forcer
        # la porte et quitter réellement cette réserve fermée à clé.
        from donjon.moteur import Moteur, proposition
        m = recharger(m)
        for _ in range(120):
            Moteur(m).executer(Moteur(m).preparer(proposition("attendre", "1")))
            m = recharger(m)
            if lire(m, "mathe")["voix_entendues"].get("odon", {}).get("se_dit") == "odon":
                break
        self.assertIn("Odon demande une part des vivres de la cuisine à Mathe (qui_va_la).", chronique(m))
        self.assertNotIn("odon", lire(m, "mathe")["voix"])
        self.assertEqual(lire(m, "mathe")["voix_entendues"]["odon"]["se_dit"], "odon")
        self.assertEqual(lieu_cru(m, "mathe", "odon"), ("reserve", "se_dit"))
        self.assertNotIn("fiable", lire(m, "mathe")["croyances"]["odon"])
        # Nommé, il redemande aussitôt : plus de « Qui va là ? ».
        self.assertEqual(sum("(qui_va_la)" in t for t in chronique(m)), 1)

    def test_servir_une_part_suit_la_meme_regle(self):
        """Donner une part à qui l'on appelle hors de vue est un échange comme un autre
        (``pnj.peuvent_se_parler`` : s'entendre). Dans la réserve noire, Mathe sert Odon qu'elle
        appelle, qu'elle connaisse sa voix ou non ; Odon, qui ne sait pas qui le sert, ne lui en sait
        pas gré."""
        from donjon.echanges import servir
        m = self.baraquement_noir(salle="reserve")
        lire(m, "odon")["voix"].remove("mathe")
        lire(m, "odon")["relations"].pop("mathe", None)
        portions = m.objets["vivres"]["portions"]
        self.assertTrue(servir(m, "mathe", "vivres", "odon", []))
        m = recharger(m)
        self.assertEqual(m.objets["vivres"]["portions"], portions - 1)
        self.assertIn("Mathe appelle Odon et lui donne une part des vivres de la cuisine.", chronique(m))
        self.assertNotIn("fiable", lire(m, "odon")["croyances"]["mathe"])
        connaitre(m, "odon", "mathe")
        self.assertTrue(servir(m, "mathe", "vivres", "odon", []))
        from donjon.relations import envers
        self.assertEqual(envers(recharger(m), "odon", "mathe")["confiance"], 50)

    def test_dans_la_lumiere_on_se_tourne_vers_une_voix_inconnue(self):
        """Une voix inconnue dans son dos, en pleine lumière : il se tourne vers elle et voit qui
        parle ; il le connaît désormais. Dans le noir, il ne le saurait pas."""
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        placer(m, "mireille", "cuisine", [2, 2])
        placer(m, "anselme", "cuisine", [4, 2])
        regarder(m, "mireille", [0, 2])
        regarder(m, "anselme", "mireille")
        self.assertNotIn("anselme", lire(m, "mireille")["voix"])
        self.assertTrue(se_parler(m, "anselme", "mireille"))
        percevoir_tous(m)
        m = recharger(m)
        self.assertIn("anselme", lire(m, "mireille")["voix"])
        # Au grenier noir, ni l'un ni l'autre ne voit l'autre : ils se parlent, mais Mireille
        # n'entend qu'une voix inconnue, qu'elle retient sans savoir à qui elle est ; Anselme, qui
        # s'adressait à elle, la croit là sur sa parole (``voix.se_nommer``), sans connaître sa voix.
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        m.objets["bougeoir_mireille"]["allume"] = False
        placer(m, "mireille", "grenier", [2, 2])
        placer(m, "anselme", "grenier", [4, 2])
        self.assertTrue(se_parler(m, "anselme", "mireille"))
        m = recharger(m)
        self.assertNotIn("anselme", lire(m, "mireille")["voix"])
        self.assertIn("anselme", lire(m, "mireille")["voix_entendues"])
        self.assertIsNone(lieu_cru(m, "mireille", "anselme"))
        self.assertNotIn("mireille", lire(m, "anselme")["voix"])
        self.assertEqual(lieu_cru(m, "anselme", "mireille"), ("grenier", "se_dit"))

    def test_le_joueur_dans_le_noir_face_a_qui_ne_le_connait_pas(self):
        """Corvus, au grenier noir, s'adresse à Odile, qu'il connaît mais qui ne l'a jamais vu ni
        entendu : il lui parle ; elle entend une voix inconnue (``test_voix``)."""
        from donjon.paroles import analyser, destinataires
        m = calme(auberge(), "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")
        placer(m, "odile", "grenier", [4, 2])
        m.joueur.update(salle="grenier", position=[6, 2], orientation="ouest")
        connaitre(m, "joueur", "odile")
        m.data["connus"] = sorted({*m.data["connus"], "odile"})
        m.data["entendus"] = ["odile"]  # Il vient de reconnaître sa voix.
        m = recharger(m)
        self.assertNotIn("joueur", lire(m, "odile")["voix"])
        self.assertEqual(destinataires(m, analyser(m, "je dis à Odile : c'est moi")), ["odile"])

    def test_le_scenario_declare_qui_se_connait(self):
        """Au début d'une partie, chacun connaît la voix de ceux que le scénario lui fait connaître
        (un savoir à leur sujet) ; le joueur, étranger, n'en connaît aucune."""
        m = relais()
        self.assertEqual(lire(m, "brune")["voix"], ["aubin", "ilse", "marchand"])
        self.assertEqual(m.data["voix_connues"], [])

    def baraquement_noir(self, salle="baraquement"):
        from donjon.geometrie import cases
        from tests.scenarios_contractuels import nouveau_mine
        m = nouveau_mine(1985, "fixe")
        installer(m)
        m = calme(m, "bram", "gaspard", "josse", "lucien", "mathe", "odon", "remy")
        if salle == "baraquement":
            for k in ("lampe_baraque", "poele"):
                m.objets[k]["allume"] = False
        # Josse n'a pas d'huile dans sa lampe : sinon, voyant le poêle mort, il irait demander du feu
        # pour elle à qui porte une flamme (``echanges.demander_feu``) et rallumerait le poêle ; le
        # baraquement ne serait plus noir.
        m.objets["lampe_josse"]["combustible"] = 0
        if salle == "reserve":
            # Dans la réserve noire, demander sa part puis l'attendre au garde-manger, dans le noir
            # du baraquement, coûte à Odon un peu plus que de forcer le garde-manger
            # (``planification.attente_part``) : honnête ici, il n'a que la parole, et la scène
            # éprouve ce qu'elle vise, le jugement de sa demande.
            m.objets["odon"]["profil"]["valeurs"]["honnetete"] = 100
        sol = sorted(cases(m.data["salles"]["galerie"]))
        for n, k in enumerate(("bram", "gaspard", "josse", "lucien", "remy")):
            placer(m, k, "galerie", sol[2 * n])
        placer(m, "mathe", salle, [3, 3])
        placer(m, "odon", salle, [5, 3])
        m.data["minutes"] = 3
        croire(m, "odon", "mathe", "lieu", salle, "entendu", salle=salle, case=[3, 3])
        lire(m, "odon")["besoins"]["faim"] = 95.0
        m.objets["pain_lucien"]["portions"] = 0
        croire(m, "odon", "pain_lucien", "etat", {"disponible": False}, "vu")
        self.assertEqual(eclairage(m, salle, [3, 3])["niveau"], 0)
        return m
