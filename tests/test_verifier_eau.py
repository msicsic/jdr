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
import copy
import inspect
import unittest
from unittest.mock import patch

from donjon import eau, planification
from donjon.banc_pnj import creer, executer
from donjon.deliberation import deliberer
from donjon.esprits import croire, lire, percevoir
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
    def test_lucien_demande_la_lampe_vue_et_la_reference_le_trouve_aussi(self):
        # Cas réel (``test_lumiere``, la mine noire, révélé à la fusion de ``ouie-temoins``) : dans le
        # noir, Lucien va chercher Josse, qui porte une lampe, et l'appelle ; la référence de
        # ``VERIFIER`` (sans ``emplois``) n'offrait pas ce geste et ne trouvait aucun plan.
        m = lumiere.avec_briquet(lumiere.mine_noire())
        m.objets["lampe_remy"].update(allume=False, combustible=0)
        # Isoler la recherche du porteur : les flammes fixes, devenues moins
        # chères à rejoindre, ne doivent pas fournir un autre recours à ce test.
        from donjon.esprits import croire
        for k, o in m.objets.items():
            if "allume" in o and k != "lampe_josse":
                o.update(allume=False, combustible=0)
                croire(m, "lucien", k, "etat", {"allume": False, "charge": False}, "savoir")
            if "allumage" in o.get("usages", ()):
                o["usages"] = [u for u in o["usages"] if u != "allumage"]
        croire(m, "lucien", "josse", "lieu", None, "savoir", salle=None, case=None)
        m.objets["bidon_huile"]["charges"] = 0
        croire(m, "lucien", "bidon_huile", "etat", {"disponible": False}, "savoir")
        placer(m, "josse", "baraquement", (3, 2))
        # La recherche et le refus de la lampe, pas la mobilité du fournisseur :
        # il reste occupé à son poste pendant les quinze minutes observées.
        lire(m, "josse")["libre"] = 15 * 600
        m.objets["lampe_josse"].update(allume=True, combustible=720)
        # La lampe est effectivement vue avant la recherche : le test ne
        # dépend plus de l'arrivée fortuite de Josse dans le regard de Lucien.
        from tests.support import regarder
        regarder(m, "lucien", "josse")
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
                plans.append(copy.deepcopy(i))  # l'exécution retire ensuite les étapes en place
            return resultat
        from donjon import echanges
        from donjon.biens import valeur_capacites
        from donjon.caractere import valeur_pieces
        demander = echanges.demander
        signature = inspect.signature(demander)
        refus_lucien, ventes = [], []

        def transaction(monde, demandeur, auditeur, objet, *args, **options):
            suivi = objet == 'lampe_josse' and auditeur == 'josse'
            if suivi:
                prix = signature.bind(monde, demandeur, auditeur, objet, *args, **options).arguments.get('prix', 0)
                avant = copy.deepcopy(monde.data['finances_pnj'])
                capacite = valeur_capacites(monde, auditeur, objet)
                gain = valeur_pieces(monde, auditeur, prix)
            resultat = demander(monde, demandeur, auditeur, objet, *args, **options)
            if suivi and demandeur == 'lucien' and resultat == 'necessaire':
                self.assertEqual(monde.objets[objet]['lieu'], 'josse')
                self.assertEqual(monde.data['finances_pnj'], avant)
                refus_lucien.append(resultat)
            if suivi and resultat == 'vendu':
                self.assertEqual(demandeur, 'bram')
                self.assertGreaterEqual(gain, capacite)
                self.assertEqual(monde.objets[objet]['lieu'], demandeur)
                self.assertEqual(monde.objets[objet]['proprietaire'], demandeur)
                self.assertEqual(monde.data['finances_pnj'][demandeur], avant[demandeur] - prix)
                self.assertEqual(monde.data['finances_pnj'][auditeur], avant[auditeur] + prix)
                ventes.append(prix)
            return resultat

        with patch.object(planification, "VERIFIER", True), diagnostics() as recherches, \
                patch.object(deliberation, "choisir", espion), patch.object(echanges, 'demander', transaction):
            for _ in range(15):
                m, _ = vivre(m, 1)
        # L'espace enrichi borne d'abord la recherche. Josse entre ensuite dans
        # son champ ; le recours est désormais de demander la lampe vue, sans
        # inventer un appel que cette nuit ne produit plus.
        self.assertTrue(any(i["but"]["type"] == "lumiere" and any(
            x["operation"] == "demander" and x["cible"] == "josse" for x in i["plan"]) for i in plans))
        self.assertTrue(any(r["pnj"] == "lucien" and r["but"] == "lumiere" for r in recherches))
        self.assertTrue(any(c["texte"].startswith("Lucien demande la lampe du contremaître à Josse")
                            for c in m.data["chronique"]))
        # 202/228 : le refus de prêt à Lucien tient ; Bram peut ensuite payer
        # la capacité perdue (17 pièces). Le refus ne fige pas le porteur à vie.
        self.assertTrue(refus_lucien)
        self.assertEqual(ventes, [17])
        m = recharger(m)
        self.assertEqual(m.objets['lampe_josse']['lieu'], 'bram')
        self.assertEqual(m.objets['lampe_josse']['proprietaire'], 'bram')
        from donjon.rendu import regarder as rendu
        from donjon.scene import scene_percue
        recharge = recharger(m)
        self.assertEqual(m.data, recharge.data)
        self.assertEqual(rendu(m), rendu(recharge))
        self.assertEqual(scene_percue(m), scene_percue(recharge))

    def test_remy_cherche_gaspard_et_le_controle_passe(self):
        # Même nature (mine, le camp éteint) : Rémy va chercher Gaspard, qui a le briquet, l'appelle et
        # lui demande du feu ; chaque recherche de lumière, restreinte, a le coût de la complète.
        m = lumiere_garde.FeuDemandeTests().camp_eteint()
        with patch.object(planification, "VERIFIER", True), diagnostics() as recherches:
            m = lumiere_garde.suivre(m, 10, lambda m: m.objets["lampe_rechange_1"].get("allume"))
        self.assertTrue(any(r["pnj"] == "remy" and r["but"] == "lumiere" and r["issue"] == "plan" for r in recherches))
        self.assertIn("Rémy appelle : « Gaspard ? »", [c["texte"] for c in m.data["chronique"]])
        self.assertTrue(any(m.objets[k]["allume"] for k in ("lampe_rechange_1", "lampe_rechange_2")))

    def test_une_reference_bornee_n_est_pas_un_defaut(self):
        # La référence arrêtée par sa borne n'est pas un optimum : la restreinte ne doit que ne pas
        # coûter plus qu'elle (ici, elle ne trouve rien en un nœud).
        m = lumiere_garde.FeuDemandeTests().camp_eteint()
        with patch.object(planification, "VERIFIER", True), patch.object(planification, "REFERENCE", 1):
            m = lumiere_garde.suivre(m, 10, lambda m: m.objets["lampe_rechange_1"].get("allume"))
        self.assertTrue(any(m.objets[k]["allume"] for k in ("lampe_rechange_1", "lampe_rechange_2")))


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
        # Les occasions sociales ont changé : Aubin peut appeler avec de l'eau aux pieds,
        # puis rester dans ce refuge qui ne sera jamais noyé. Le contrat porte sur le piège
        # et le chauffage, à leur instant réel (pas sur la position à la fin du bloc de 5 min).
        from donjon import pnj
        appels, chauffes = [], []
        chroniquer = pnj._chroniquer
        def trace(monde, id, texte, *args, **kwargs):
            profondeur = eau.profondeur(monde, monde.objets[id]["lieu"])
            if "appelle à l'aide" in texte:
                appels.append((id, profondeur))
            if "se chauffe" in texte:
                chauffes.append((id, profondeur))
            return chroniquer(monde, id, texte, *args, **kwargs)
        with patch.object(pnj, "_chroniquer", trace):
            while m.data["minutes"] < 360:
                executer(m, min(360, m.data["minutes"] + 5))
                m = recharger(m)
        self.assertFalse([a for a in appels if a[1] >= eau.NOYEE_CM])
        self.assertFalse([a for a in chauffes if a[1] > 0])
        for id in ("marchand", "brune", "ilse", "aubin"):
            self.assertLess(eau.profondeur(m, m.objets[id]["lieu"]), 50, id)

    def test_le_meme_laps_decoupe_donne_le_meme_monde(self):
        d_un_bloc = nuit("crue", 500, "chambre_cloche")
        executer(d_un_bloc, 240)
        decoupe = par_blocs(nuit("crue", 500, "chambre_cloche"), 240, 40)
        self.assertEqual(json.dumps(recharger(d_un_bloc).data, sort_keys=True),
                         json.dumps(decoupe.data, sort_keys=True))

    def scene(self):
        """Autre crue (1 cm par minute depuis -150), à la minute 100.

        Aubin a mesuré sa vitesse ; les autres ont pu évacuer avant une
        seconde mesure. Une position d'auteur ne leur donne pas ce savoir.
        """
        m = calme(crue(FIXES), "marchand", "brune", "ilse", "aubin")
        m, _ = attendre(m, 100)
        self.assertEqual(eau.estimation(m, "aubin")[2], 60)
        return m

    def test_on_ne_descend_pas_ou_l_eau_va_noyer_et_on_ne_s_y_chauffe_pas(self):
        m = self.scene()
        # Le recours positif part du refuge après observation de la crue ;
        # une évacuation antérieure ne doit pas supprimer le trajet à éprouver.
        placer(m, "ilse", "antichambre", (1, 3))
        # 247 : depuis le suivi 242, Gorm ne transmet plus sa mesure à
        # Ilse dans cette scène. Sa prémisse est une montée connue :
        # connaissance d'auteur explicite, distincte de sa position.
        # Aucun savoir d'Aubin ni niveau réel n'est consulté par le plan.
        croire(m, "ilse", "crypte", "eau", eau.profondeur(m, "crypte"), "savoir",
               niveau=eau.niveau(m), repere=[m.data["minutes"], eau.niveau(m)], montee=60)
        self.assertEqual(eau.estimation(m, "ilse")[2], 60)
        # La ronde d'Aubin à la salle des vannes, le brasero de la conduite pour Ilse transie.
        self.assertIsNone(planifier_pulsion(m, "aubin", {"lieu": "crypte", "periode": 49}))
        lire(m, "ilse")["besoins"]["chaleur"] = 90.0
        # L'évacuation précoce ramène désormais Gorm au refuge ; il peut
        # refermer sa porte. Le recours positif testé ici suppose la route
        # ouverte vers le poêle sec, comme dans la scène d'origine.
        m.objets["porte"].update(ouverte=True, verrouillee=False)
        croire(m, "ilse", "porte", "etat", {"ouverte": True}, "vu")
        croire(m, "ilse", "porte", "verrouillee", False, "vu")
        m = recharger(m)
        but = planifier(m, "ilse", "chaleur")
        self.assertFalse(but and any(x["lieu"] in ("echoppe", "crypte") or x["cible"] == "brasero"
                                     for x in but[1]))
        # Elle monte se chauffer au poêle du guet, à la galerie, hors de l'eau (branche ``ressources``).
        gestes = [(x["operation"], x["lieu"] or x["cible"]) for x in but[1]]
        self.assertEqual(gestes[-1], ("chauffer", "poele_guet"))
        self.assertIn(("aller", "chambre_cloche"), gestes)
        # L'eau coûte à tout plan, par minute, comme le noir à qui le craint.
        v = Vue(m, "ilse")
        self.assertGreater(v.pression(depart(m, "ilse", v).apres(salle="echoppe")),
                           v.pression(depart(m, "ilse", v).apres(salle="chambre_cloche")))
        self.assertTrue(v.descente("antichambre", "crypte"))
        self.assertFalse(v.descente("crypte", "antichambre"))   # Vers moins d'eau, on peut aller.
        self.assertIn("echoppe", v.menacees)
        self.assertIn("crypte", v.noyees)
        # La suite s'exécute aussi dans le monde : ni descente vers
        # le brasero, ni chauffage dangereux annoncé. État et deux vues
        # du joueur restent identiques après sauvegarde/rechargement.
        executer(m, m.data["minutes"] + 5)
        self.assertNotIn(m.objets["ilse"]["lieu"], ("echoppe", "crypte"))
        self.assertFalse(any(c["pnj"] == "ilse" and "se chauffe" in c["texte"]
                             and "brasero" in c["texte"] for c in m.data["chronique"]))
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        recharge = recharger(m)
        self.assertEqual(m.data, recharge.data)
        self.assertEqual(regarder(m), regarder(recharge))
        self.assertEqual(scene_percue(m), scene_percue(recharge))

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
