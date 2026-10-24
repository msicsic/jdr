"""Les voix (``donjon/voix.py``) : héler quelqu'un, parler à une voix inconnue, reconnaître une voix,
se nommer.

- Héler est un cri : il porte comme un appel, à travers une porte fermée. Qui en saisit les mots
  entend qu'on appelle tel nom, sans alarme ; sans les mots, c'est un cri inquiétant. Un appel resté
  sans réponse compte la salle pour parcourue : on ne rappelle pas en boucle.
- Se parler, c'est s'entendre ; une voix qu'on ne sait à qui prêter est un étranger, à qui l'on
  peut répondre « Qui va là ? ».
- On connaît la voix de qui l'on a entendu parler en le voyant ; le voir ne suffit pas.
- Se nommer est une affirmation pesée : démasquée par la vraie voix, crue sur parole sinon, sans
  jamais valoir plus de confiance qu'un inconnu ; démasquée plus tard quand on entend la vraie voix.

Chaque cas vérifie l'état du monde après rechargement, et ce que lit le joueur quand il est là.
"""

from tests.support import lier, relation
import json
import unittest

from donjon.auberge import nouveau_auberge
from donjon.defi import nouveau_defi
from donjon.esprits import connaitre, croire, lire, memoriser, percevoir_tous
from donjon.geometrie import position_entree
from donjon.monde import Monde
from donjon.ouie import retentir
from donjon.paroles import jet_persuasion
from donjon.relations import AXES, ETRANGER, confiance, mefiance, percue
from donjon.spatial import installer
from donjon.voix import designation, nom_pour_joueur, reconnaitre, se_nommer
from tests.support import calme
from tests.test_paroles import jouer, parole, reponse_pnj
from tests.test_paroles import relais as relais_pres_de_gorm
from tests.test_temps_etat import decouper, etat_pnj
from tests.test_tensions import attendre, chronique, placer, recharger


def auberge():
    m = nouveau_auberge(1985, "fixe")
    installer(m)
    return calme(m, "anselme", "hugues", "odile", "joss", "mireille", "tilo", "mathurine", "lucien")


def lieu_cru(m, id, sujet):
    c = lire(m, id)["croyances"].get(sujet, {}).get("lieu")
    return None if c is None else (c["valeur"], c["source"])


def appels(m, qui):
    return [(c["minute"], c["texte"]) for c in m.data.get("chronique", [])
            if c["pnj"] == qui and " appelle : « " in c["texte"]]


def hugues_cherche_anselme(verrou=False):
    """Hugues a vu Lucien forcer le coffre d'Anselme et veut le prévenir ; il ne sait où il est.
    Anselme est dans sa chambre, porte fermée ; Hugues, sans lumière, au couloir."""
    m = auberge()
    m.objets["lanterne_hugues"]["allume"] = False
    placer(m, "anselme", "chambre_chaude", [2, 2])
    placer(m, "hugues", "couloir", list(position_entree(m, "couloir")))
    croire(m, "hugues", "anselme", "lieu", None, "essai", salle=None, case=None)
    memoriser(m, "hugues", {"type": "vu_agir", "auteur": "lucien", "operation": "forcer", "objet": "coffre_marchand"})
    memoriser(m, "hugues", {"type": "a_prevenir", "victime": "anselme", "auteur": "lucien"})
    lier(m, "hugues", "lucien", False, "vu")
    m.data["minutes"] = 2
    for s in m.data["salles"]:
        lire(m, "hugues")["visites"][s] = 0 if s == "couloir" else 1
    lire(m, "hugues")["besoins"]["devoir"] = 90.0
    if verrou:
        # Anselme s'est enfermé et se méfie d'Hugues : il ne répond pas, et Hugues ne peut entrer.
        m.objets["porte_chambre"]["verrouillee"] = True
        croire(m, "hugues", "porte_chambre", "verrouillee", True, "essai")
        lier(m, "anselme", "hugues", False, "vu")
    assert not m.objets["porte_chambre"]["ouverte"]
    return m


def aubin_cherche_gorm():
    """Relais : Aubin a faim ; Gorm, qui garde les vivres, est à la salle des vannes, derrière la porte
    étanche fermée ; Aubin, au palier, ne sait où il est. Le joueur est à la galerie."""
    m = nouveau_defi(depart="fixe")
    installer(m)
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    placer(m, "brune", "chambre_cloche", (2, 2))
    placer(m, "ilse", "chambre_cloche", (4, 2))
    placer(m, "marchand", "crypte", (5, 2))
    placer(m, "aubin", "beffroi", list(position_entree(m, "beffroi")))
    m.objets["porte"]["verrouillee"] = False
    croire(m, "aubin", "marchand", "lieu", None, "essai", salle=None, case=None)
    lire(m, "aubin")["besoins"]["faim"] = 90.0
    m.data["minutes"] = 2
    for s in m.data["salles"]:
        lire(m, "aubin")["visites"][s] = 0 if s == "beffroi" else 1
    m.joueur.update(salle="chambre_cloche", position=[3, 7], orientation="nord")
    return recharger(m)


class HelerTests(unittest.TestCase):
    def test_hugues_hele_anselme_a_travers_la_porte(self):
        """Cas réel (auberge) : Hugues appelait Anselme sans fin, derrière la porte fermée de sa
        chambre. Héler porte comme un cri : Anselme l'entend, répond, Hugues le croit là d'où vient
        sa voix (il la connaît) ; à « Qu'est-ce que tu veux ? », il dit avoir à le prévenir, et Anselme vient
        à lui (``appel``). Le joueur, au couloir, entend l'appel d'Hugues
        dont il connaît la voix, et la réponse d'une voix qu'il ne connaît pas : celle qu'Hugues appelle
        Anselme (branche ``voix-inconnues`` : ce qu'il surprend lui nomme la voix, comme un ouï-dire).
        Anselme venant au couloir (``appel`` : « J'arrive ! »), le joueur le voit avant la fin de son
        attente : ce qu'il entend se rend sous le nom de qui il voit, sans qu'il connaisse sa voix."""
        m = hugues_cherche_anselme()
        m.joueur.update(salle="couloir", position=[1, 2])
        m.data["visitees"] = sorted({*m.data["visitees"], "couloir"})
        m.data["connus"] = sorted({*m.data["connus"], "hugues", "anselme"})
        connaitre(m, "joueur", "hugues")  # Placement d'auteur : il a déjà entendu Hugues parler.
        from tests.support import presentes
        presentes(m,'hugues')  # Le nom lui a également été présenté.
        m, texte = attendre(recharger(m))
        self.assertIn("Hugues appelle : « Anselme ? »", chronique(m))
        # Anselme ne sait pourquoi on l'appelle : Hugues le lui dit, il vient (``appel``).
        self.assertIn("Anselme répond : « Qu'est-ce que tu veux ? »", chronique(m))
        self.assertIn("Anselme répond : « J'arrive ! »", chronique(m))
        self.assertIn("Hugues dit à Anselme que Lucien est peu fiable (crue).", chronique(m))
        self.assertEqual(len(appels(m, "hugues")), 1)
        self.assertIn("Tu entends, tout près : Hugues appelle : « Anselme ? »", texte)
        # Branche des noms : la voix qu'Hugues appelle Anselme se révèle celle de qui vient au couloir,
        # que Corvus voit parler ; il apprend alors son nom, et ce qu'il a entendu se rend sous ce nom.
        self.assertIn("Tu entends, à l'est, Anselme répondre : « Qu'est-ce que tu veux ? »", texte)
        self.assertIn("anselme", m.data["noms_connus"])
        self.assertEqual(m.data["voix_entendues"]["anselme"]["appelee"], "anselme")
        self.assertNotIn("anselme", m.data["voix_connues"])
        # Une seule confidence est maintenant reçue : elle affecte la relation sans
        # nécessairement franchir sa bande de confiance (hystérésis).
        self.assertTrue(any(s["type"] == "avis_recu" and s["sujet"] == "lucien" and s["valeur"] is False
                            for s in lire(m, "anselme")["memoire"]))

    def test_aubin_hele_gorm_a_travers_la_porte_etanche(self):
        """Même nature (Relais) : Aubin, au palier, hèle Gorm, derrière la porte étanche fermée ;
        Gorm répond de la salle des vannes ; Aubin y va et obtient sa part. Avant, il l'appelait à
        chaque minute sans que sa voix ne passe la porte."""
        m = aubin_cherche_gorm()
        m, texte = attendre(m)
        self.assertEqual(len(appels(m, "aubin")), 1)
        self.assertIn("Gorm répond : « Ici, viens ! »", chronique(m))  # Il croit la porte fermée (``appel``).
        self.assertIn("Gorm appelle Aubin et lui donne une part des vivres du refuge.", chronique(m))
        # Le joueur, à la galerie, entend l'appel d'une voix qu'il ne connaît pas, sans nom.
        self.assertIn("Tu entends, à l'ouest, une voix inconnue appeler : « Gorm ? »", texte)
        self.assertNotIn("Aubin", texte)

    def test_le_meme_laps_decoupe_donne_le_meme_monde(self):
        d_un_bloc, morcele = decouper(aubin_cherche_gorm, 6)
        self.assertIn("Gorm répond : « Ici, viens ! »", [c["texte"] for c in morcele.data["chronique"]])
        self.assertEqual(etat_pnj(d_un_bloc), etat_pnj(morcele))

    def test_un_appel_sans_reponse_n_est_pas_repete_en_boucle(self):
        """Anselme, enfermé, se méfie d'Hugues et ne répond pas. Hugues hèle une fois dans chaque
        salle où il peut aller, puis cesse : chaque appel resté sans réponse compte la salle pour
        parcourue (``deliberation.appels_vains``)."""
        m = recharger(hugues_cherche_anselme(verrou=True))
        for _ in range(6):
            m, _ = attendre(m)
        m = recharger(m)
        faits = appels(m, "hugues")
        salles = [s["salle"] for s in lire(m, "hugues")["memoire"] if s["type"] == "appel_sans_reponse"]
        self.assertEqual(len(faits), len(salles))
        self.assertEqual(len(salles), len(set(salles)))
        self.assertNotIn("chambre_chaude", salles)
        self.assertTrue(all(minute < 12 for minute, _ in faits))
        self.assertFalse([t for t in chronique(m) if t.startswith("Anselme répond")])

    def test_un_cri_sans_les_mots_inquiete_les_mots_non(self):
        """Qui saisit les mots d'un appel par un nom entend qu'on appelle quelqu'un : pas d'alarme.
        Qui n'en reçoit que le cri (il lui parvient sous le seuil des mots, qu'une oreille aux aguets
        perçoit encore) retient un bruit inconnu, fort, comme un fracas."""
        from donjon.ouie import SEUIL, entendre
        from donjon.temps import instant
        m = auberge()
        placer(m, "hugues", "couloir", [1, 2])
        placer(m, "anselme", "dortoir", [1, 1])
        placer(m, "joss", "grenier", [1, 1])
        for id in ("anselme", "joss"):
            lire(m, id)["besoins"]["securite"] = 0.0
        t = instant(m)
        entendre(m, "anselme", "hugues", "couloir", (1, 2), "hele", t, SEUIL)      # les mots
        entendre(m, "joss", "hugues", "couloir", (1, 2), "hele", t, SEUIL - 1)     # le cri seul
        m = recharger(m)
        bruits = {id: [s["nature"] for s in lire(m, id)["memoire"] if s["type"] == "bruit"]
                  for id in ("anselme", "joss")}
        self.assertEqual(bruits, {"anselme": [], "joss": ["hele"]})
        self.assertEqual(lire(m, "anselme")["besoins"]["securite"], 0)
        # Le cri seul le pousse, courageux, à aller voir d'où il vient (``deliberation.bruit_a_voir``).
        from donjon.deliberation import bruit_a_voir
        m.objets["joss"]["profil"]["valeurs"]["courage"] = 70
        self.assertEqual(bruit_a_voir(m, "joss"), ("couloir", "securite"))
        # Le même appel saisi d'une voix connue : il croit Hugues là d'où il appelle.
        self.assertEqual(lieu_cru(m, "anselme", "hugues"), ("couloir", "entendu"))


class VoixInconnueTests(unittest.TestCase):
    def gorm_dans_le_noir(self):
        """Relais : Corvus, à la conduite basse près de Gorm, sans lumière ; il a déjà entendu Gorm
        parler (il reconnaît sa voix), Gorm ne l'a jamais vu ni entendu."""
        m = relais_pres_de_gorm()
        m.objets["brasero"]["allume"] = False
        m.objets["lanterne"]["allume"] = False
        connaitre(m, "joueur", "marchand")
        m.data["entendus"] = ["marchand"]
        m.data["connus"] = sorted({*m.data["connus"], "marchand", "vivres"})
        return recharger(m)

    def test_le_joueur_dans_le_noir_demande_sa_part_a_gorm(self):
        """Cas demandé : Gorm entend une voix inconnue lui demander une part et décide comme face à
        un étranger : aucune confiance connue, une demande qui pèse moins. Au même jet, il l'accorde
        à qui il voit, la refuse à une voix dans le noir."""
        m = self.gorm_dans_le_noir()
        self.assertFalse(m.visible("marchand"))
        self.assertEqual(designation(m, "marchand"), "marchand")
        _, dd_noir = jet_persuasion(m, "marchand", "joueur", 10)
        reprise, sortie, entrees = jouer(m, "je demande à Gorm une part des vivres", [
            parole("Gorm, une part des vivres, s'il te plaît.", ("demande", "vivres", "", "")),
            reponse_pnj("Gorm ne bouge pas.")], jet=12)
        faits = entrees[1]["faits"]["conversation_validee"]["faits"]
        # Refusée, la part reste à vendre : il dit son prix (``echanges-argent``).
        self.assertIn("Gorm, gardien du relais n'est pas convaincu et garde les vivres du refuge ; il en veut "
                      "2 pièces.", faits)
        gorm = lire(reprise, "marchand")
        self.assertIn("joueur", gorm["voix_entendues"])
        self.assertNotIn("joueur", gorm["voix"])
        self.assertNotIn("fiable", gorm["croyances"].get("joueur", {}))
        self.assertTrue(next(s for s in reversed(gorm["memoire"]) if s["type"] == "parole")["voix_inconnue"])
        # À la lumière, le même jet suffit : il voit qui lui parle.
        eclaire = relais_pres_de_gorm()
        self.assertLess(jet_persuasion(eclaire, "marchand", "joueur", 10)[1], dd_noir)
        reprise, _, entrees = jouer(eclaire, "je demande à Gorm une part des vivres", [
            parole("Gorm, une part des vivres, s'il te plaît.", ("demande", "vivres", "", "")),
            reponse_pnj("Gorm hoche la tête.")], jet=12)
        self.assertIn("Gorm, gardien du relais accepte de t'en donner une part : il te la servira là où sont "
                      "les vivres.", entrees[1]["faits"]["conversation_validee"]["faits"])

    def test_le_joueur_se_nomme_sans_rien_gagner(self):
        """« C'est Corvus » : Gorm le croit sur parole et le situe, sans lui accorder plus de
        confiance qu'à un inconnu ; prudent, il lui aurait d'abord demandé qui va là."""
        m = self.gorm_dans_le_noir()
        lire(m, "marchand")["besoins"]["securite"] = 90.0  # Inquiet : il est prudent.
        m = recharger(m)
        reprise, _, entrees = jouer(m, "je demande à Gorm une part des vivres", [
            parole("Une part des vivres ?", ("demande", "vivres", "", "")), reponse_pnj("« Qui va là ? »")])
        self.assertIn("Gorm, gardien du relais ne sait pas qui lui parle : il demande « Qui va là ? » avant toute "
                      "chose.", entrees[1]["faits"]["conversation_validee"]["faits"])
        reprise, _, entrees = jouer(reprise, "je lui dis : c'est Corvus", [
            parole("C'est Corvus.", ("nom", "joueur", "", "")), reponse_pnj("Gorm grogne.")])
        self.assertEqual(entrees[1]["faits"]["conversation_validee"]["faits"],
                         ["Gorm, gardien du relais te croit sur parole : pour lui, c'est « Corvus » qui parle. Cela ne te "
                          "vaut pas plus de confiance qu'à un inconnu."])
        gorm = lire(reprise, "marchand")
        self.assertEqual(gorm["voix_entendues"]["joueur"]["se_dit"], "joueur")
        self.assertEqual(lieu_cru(reprise, "marchand", "joueur"), ("echoppe", "se_dit"))
        self.assertEqual({a: percue(reprise, "marchand", "joueur")[a] for a in AXES}, ETRANGER)

    def test_une_voix_inconnue_se_nomme_pour_le_joueur(self):
        """Corvus, dans le noir, entend Brune sans connaître sa voix : pour lui et pour le MJ, c'est
        « une voix inconnue » (voix_<n>). Il demande qui est là ; elle se nomme. Il n'en sait que ce
        qu'elle dit : « une voix qui se dit Brune » ; le MJ ne reçoit ni son identifiant ni ses traits."""
        m = self.gorm_dans_le_noir()
        placer(m, "brune", "echoppe", (1, 3))
        m.data["entendus"] = ["brune"]
        m.data["connus"] = sorted({*m.data["connus"], "brune"})
        from donjon.voix import retenir
        retenir(m, "joueur", "brune")
        m = recharger(m)
        alias = designation(m, "brune")
        self.assertTrue(alias.startswith("voix_"))
        contexte = m.contexte()
        self.assertIn(alias, contexte["interlocuteurs"])
        self.assertNotIn("brune", json.dumps(contexte["interlocuteurs"]).lower())
        reprise, sortie, entrees = jouer(m, "« Qui est là ? »", [
            parole("Qui est là ?", ("qui", "", "", ""), personnage=alias), reponse_pnj("« C'est Brune. »")])
        self.assertEqual(entrees[0]["faits"]["parole_prevue"]["personnage"], alias)
        self.assertNotIn("Batelière", json.dumps(entrees[0]["faits"]["esprits_interlocuteurs"], ensure_ascii=False))
        validee = entrees[1]["faits"]["conversation_validee"]
        self.assertEqual((validee["personnage"], validee["destinataires"]), (alias, [alias]))
        self.assertIn("Une voix inconnue se nomme : « Brune ».", validee["faits"])
        self.assertIn("Tu dis à une voix inconnue : « Qui est là ? »", sortie)
        self.assertEqual(nom_pour_joueur(reprise, "brune"), "une voix qui se dit Brune")
        self.assertEqual(reprise.contexte()["interlocuteurs"][alias]["nom"], "une voix qui se dit Brune")
        # Un nom n'est pas une identité : nommer « Brune », c'est s'adresser à la voix qui s'est dite Brune
        # (``voix.porteur_du_nom``), qui reste une voix inconnue pour lui ; jamais à Brune qu'il ne sait pas là.
        from donjon.paroles import analyser, destinataires
        self.assertEqual(destinataires(reprise, analyser(reprise, "je dis à Brune : approche")), ["brune"])
        self.assertEqual(designation(reprise, "brune"), alias)


class NarrationTests(unittest.TestCase):
    def test_une_voix_inconnue_ne_se_nomme_pas_sans_le_moteur(self):
        """Vu avec Luna : à « Approche-toi, que je te voie », la voix inconnue répondait « Je suis
        Brune, oui », sans que le moteur l'ait fait se nommer (Luna reprenait la question du joueur).
        Le contrôle déterministe refuse qu'une voix inconnue nomme qui que ce soit au-delà de ce que
        le moteur a établi ; nommée, elle peut redire son nom."""
        from donjon.narration import voix_inconnues
        m = VoixInconnueTests().gorm_dans_le_noir()
        parole_ = [{"locuteur": "voix_1", "texte": "Je suis Brune, oui."}]
        inconnue = {"interlocuteurs": {"voix_1": {"nom": "une voix inconnue", "voix_inconnue": True}}}
        self.assertEqual(len(voix_inconnues(m, parole_, inconnue)), 1)
        nommee = {"interlocuteurs": {"voix_1": {"nom": "une voix qui se dit Brune", "voix_inconnue": True}}}
        self.assertEqual(voix_inconnues(m, parole_, nommee), [])
        validee = {**inconnue, "conversation_validee": {"faits": ["Une voix inconnue se nomme : « Brune »."]}}
        self.assertEqual(voix_inconnues(m, parole_, validee), [])
        # Vu ensuite avec Luna : la voix demandait « Tu dis t'appeler Corvus ? » sans qu'il se soit nommé.
        self.assertEqual(len(voix_inconnues(m, [{"locuteur": "voix_1", "texte": "Tu dis t'appeler Corvus ?"}],
                                            nommee)), 1)
        # Vu ensuite avec Luna : « Brune répond tout près de toi » ; le récit ne lui donne pas ce nom.
        self.assertEqual(len(voix_inconnues(m, [], nommee, "Brune répond tout près de toi : « Oui. »")), 1)
        self.assertEqual(voix_inconnues(m, [], nommee, "La voix qui se dit Brune répond : « Oui. »"), [])
        connue = {"interlocuteurs": {"brune": {"nom": "Brune, batelière évacuée"}}}
        self.assertEqual(voix_inconnues(m, [{"locuteur": "brune", "texte": "Je suis Brune."}], connue), [])


def gorm_et_une_voix(qui="brune"):
    """Relais, conduite basse dans le noir : Gorm, et ``qui`` à trois cases, qu'il ne voit pas."""
    m = nouveau_defi(depart="fixe")
    installer(m)
    m = calme(m, "marchand", "brune", "ilse", "aubin")
    m.objets["brasero"]["allume"] = False
    m.objets["lanterne"]["allume"] = False
    m.joueur.update(salle="chambre_cloche", position=[3, 7])
    for n, x in enumerate(("brune", "ilse", "aubin")):
        placer(m, x, "chambre_cloche", (2 + 2 * n, 2))
    placer(m, "marchand", "echoppe", (1, 1))
    placer(m, qui, "echoppe", (4, 1))
    lire(m, "marchand")["voix"] = []
    for x in ("brune", "ilse", "aubin"):
        lier(m, "marchand", x, True, "savoir")
    m = recharger(m)
    assert not m.visible(qui) and qui not in lire(m, "marchand")["voix"]
    return m


class SeNommerTests(unittest.TestCase):
    def test_demasque_par_la_vraie_voix(self):
        """Brune, dans le noir, dit à Gorm être Ilse ; Gorm connaît la voix d'Ilse : ce n'est pas
        elle. Il se méfie de cette voix, sans savoir à qui elle est."""
        m = gorm_et_une_voix()
        connaitre(m, "marchand", "ilse")
        self.assertEqual(se_nommer(m, "marchand", "brune", "ilse"), "demasque")
        m = recharger(m)
        self.assertTrue(lire(m, "marchand")["voix_entendues"]["brune"]["mefiance"])
        self.assertTrue(mefiance(percue(m, "marchand", "brune")))
        self.assertTrue(relation(m, "marchand", "brune")["valeur"])  # Brune n'est pas soupçonnée.
        self.assertNotEqual(lieu_cru(m, "marchand", "ilse"), ("echoppe", "se_dit"))

    def test_demasque_qui_il_reconnait(self):
        """Il connaît la voix de Brune : elle a beau se dire Ilse, il sait que c'est elle, et ment."""
        m = gorm_et_une_voix()
        connaitre(m, "marchand", "brune")
        self.assertEqual(se_nommer(m, "marchand", "brune", "ilse"), "demasque")
        self.assertFalse(relation(recharger(m), "marchand", "brune")["valeur"])

    def test_cru_sur_parole_sans_gain_de_confiance_puis_demasque(self):
        """Gorm ne connaît ni la voix d'Ilse ni celle de Brune : « C'est Ilse » est cru comme un
        ouï-dire ; il croit Ilse là, mais la voix reste une inconnue : la confiance qu'il a en Ilse
        ne lui vaut rien. Plus tard, il voit Ilse parler : ce n'était pas sa voix, il sait qu'on lui
        a menti, sans savoir qui. Le jour où il voit Brune parler, il reconnaît la voix menteuse."""
        m = gorm_et_une_voix()
        self.assertEqual(se_nommer(m, "marchand", "brune", "ilse"), "crue")
        m = recharger(m)
        self.assertEqual(lieu_cru(m, "marchand", "ilse"), ("echoppe", "se_dit"))
        self.assertEqual(reconnaitre(m, "marchand", "brune"), ("ilse", "pretendue"))
        self.assertEqual({a: percue(m, "marchand", "brune")[a] for a in AXES}, ETRANGER)
        # DD gradué d'un étranger (+1), plus ce qu'une voix inconnue fait perdre.
        from donjon.caractere import modificateur
        from donjon.voix import INCONNU
        self.assertEqual(jet_persuasion(m, "marchand", "brune", 10)[1],
                         10 + 1 + INCONNU + modificateur(m, "marchand", "VOL"))
        # Ilse vient parler sous ses yeux, lanterne en main : il connaît désormais sa voix.
        placer(m, "ilse", "echoppe", (2, 1))
        m.objets["lanterne"]["lieu"] = "ilse"
        m.objets["lanterne"]["allume"] = True
        percevoir_tous(m)
        retentir(m, "ilse", "dire", texte="Ilse dit bonsoir.")
        m = recharger(m)
        self.assertIn("ilse", lire(m, "marchand")["voix"])
        self.assertTrue(lire(m, "marchand")["voix_entendues"]["brune"]["mefiance"])
        self.assertTrue(relation(m, "marchand", "brune")["valeur"])
        # Brune parle à son tour sous ses yeux : c'était sa voix.
        m.objets["lanterne"]["lieu"] = "brune"
        placer(m, "ilse", "chambre_cloche", (4, 2))
        percevoir_tous(m)
        retentir(m, "brune", "dire", texte="Brune dit bonsoir.")
        m = recharger(m)
        self.assertFalse(relation(m, "marchand", "brune")["valeur"])
        self.assertIn({"locuteur": "brune", "se_disait": "ilse"},
                      [{k: s.get(k) for k in ("locuteur", "se_disait")} for s in lire(m, "marchand")["memoire"]
                       if s["type"] == "imposture"])

    def test_c_etait_bien_lui(self):
        """Ilse se nomme dans le noir : Gorm la croit là sur parole. Il l'entend plus tard parler en la
        voyant : c'était bien elle ; sa croyance devient un constat, et sa confiance s'applique."""
        m = gorm_et_une_voix("ilse")
        self.assertEqual(se_nommer(m, "marchand", "ilse", "ilse"), "crue")
        self.assertEqual({a: percue(m, "marchand", "ilse")[a] for a in AXES}, ETRANGER)
        m.objets["lanterne"]["lieu"] = "ilse"
        m.objets["lanterne"]["allume"] = True
        percevoir_tous(m)
        lire(m, "marchand")["croyances"]["ilse"]["lieu"].update(source="se_dit")  # Ce qu'elle disait.
        retentir(m, "ilse", "dire", texte="Ilse dit bonsoir.")
        m = recharger(m)
        self.assertIn("ilse", lire(m, "marchand")["voix"])
        self.assertNotIn("ilse", lire(m, "marchand")["voix_entendues"])
        self.assertTrue(confiance(percue(m, "marchand", "ilse")))
        self.assertFalse(any(s["type"] == "imposture" for s in lire(m, "marchand")["memoire"]))

    def test_le_joueur_imposteur(self):
        """Corvus dit à Gorm, dans le noir, être Brune ; Gorm connaît la voix de Brune : ce n'est
        pas elle. Le MJ reçoit le fait ; Gorm se méfie de cette voix."""
        m = VoixInconnueTests().gorm_dans_le_noir()
        connaitre(m, "marchand", "brune")
        m.data["connus"] = sorted({*m.data["connus"], "brune"})
        reprise, _, entrees = jouer(recharger(m), "je dis à Gorm : c'est Brune", [
            parole("C'est Brune.", ("nom", "brune", "", "")), reponse_pnj("Gorm se raidit.")])
        self.assertIn("Gorm, gardien du relais sait que tu n'es pas « Brune ».",
                      entrees[1]["faits"]["conversation_validee"]["faits"])
        self.assertTrue(lire(reprise, "marchand")["voix_entendues"]["joueur"]["mefiance"])
        self.assertTrue(mefiance(percue(reprise, "marchand", "joueur")))


class VoirSansEntendreTests(unittest.TestCase):
    def test_voir_quelqu_un_ne_fait_pas_connaitre_sa_voix(self):
        """Gorm voit Brune sans l'entendre : il ne connaît pas sa voix ; il l'entend parler sous ses
        yeux : il la connaît. Le joueur de même."""
        m = relais_pres_de_gorm()
        placer(m, "brune", "echoppe", (2, 1))
        lire(m, "marchand")["voix"] = []
        m = recharger(m)
        percevoir_tous(m)
        self.assertTrue(m.visible("brune"))
        self.assertNotIn("brune", lire(m, "marchand")["voix"])
        self.assertNotIn("brune", m.data["voix_connues"])
        retentir(m, "brune", "dire", texte="Brune dit bonsoir.")
        m = recharger(m)
        self.assertIn("brune", lire(m, "marchand")["voix"])
        self.assertIn("brune", m.data["voix_connues"])


class ChargementTests(unittest.TestCase):
    def test_voix_entendues_dans_la_sauvegarde(self):
        m = gorm_et_une_voix()
        se_nommer(m, "marchand", "brune", "ilse")
        recharge = Monde(json.loads(json.dumps(m.data)))
        self.assertEqual(lire(recharge, "marchand")["voix_entendues"], lire(m, "marchand")["voix_entendues"])


if __name__ == "__main__":
    unittest.main()
