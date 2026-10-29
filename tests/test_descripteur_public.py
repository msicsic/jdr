"""U-D : identité du clic, moteur commun, refus et vues persistantes sans MJ."""
import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch

import jeu
from donjon.auberge import nouveau_auberge
from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.defi import nouveau_defi
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.noms import reference
from donjon.rendu import carte, fiche, regarder
from donjon.scene import scene_percue
from donjon.spatial import installer, memoriser
from donjon.web.pont import PontWeb
from donjon.web.serveur import Serveur
from tests.support import calme


GESTES = ("examiner", "observer", "lire", "allumer", "eteindre", "manger", "ouvrir", "fermer", "prendre",
          "deverrouiller", "crocheter")


def scene(geste, porte=False):
    m = nouveau_auberge() if porte else nouveau_defi(depart="fixe")
    installer(m)
    calme(m, *(i for i, o in m.objets.items() if o["type"] == "personnage"))
    if porte:
        cible, autre = "porte_cellier", "porte_etable"
        m.joueur.update(salle="cuisine", position=[0, 1], orientation="est")
        # La lumière portée permet de voir les deux portes sans en changer les états.
        modele = nouveau_defi(depart="fixe").objets["lanterne"]
        m.objets["lampe_test"] = {**copy.deepcopy(modele), "id": "lampe_test"}
    else:
        cible = {"observer": "marchand", "lire": "gravure", "allumer": "torche", "eteindre": "torche",
                 "manger": "vivres", "ouvrir": "coffre", "fermer": "coffre"}.get(geste, "marteau")
        autre = "autre_cible"
        m.objets[autre] = {**copy.deepcopy(m.objets[cible]), "id": autre}
        m.joueur.update(salle="antichambre", position=[1, 3], orientation="est")
        for id, pos in ((cible, [2, 3]), (autre, [2, 4])):
            o = m.objets[id]
            o.update(lieu="antichambre")
            o.pop("ancrage_carte", None)
            placer(o, "antichambre", pos)
            o["proprietaire"] = None
    for id in (cible, autre):
        o = m.objets[id]
        o.update(nom="cible identique", aliases=[])
        if geste in ("ouvrir", "fermer", "deverrouiller", "crocheter"):
            o.update(ouverte=geste == "fermer", verrouillee=geste in ("deverrouiller", "crocheter"))
        if geste in ("allumer", "eteindre"):
            o["allume"] = geste == "eteindre"
    # Neutraliser les initiatives par des données de scène, sans changer le moteur.
    for o in m.objets.values():
        if o["type"] == "personnage":
            o["profil"]["pulsions"] = []
            o["profil"].pop("protege", None)
            o["profil"]["valeurs"].update(altruisme=0, empathie=0)
    m = Monde(copy.deepcopy(m.data))
    installer(m)
    calme(m, *(i for i, o in m.objets.items() if o["type"] == "personnage"))
    memoriser(m)
    vues(m)  # Initialiser les références publiques comme la page à l'ouverture.
    return m, cible, autre


def vues(m):
    return scene_percue(m), carte(m), fiche(m), regarder(m)


class DescripteurPublicTests(unittest.TestCase):
    def boucle(self, m, entree):
        """Vraie boucle avec MJ actif : le moindre appel libre fait échouer le test."""
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "copie.json"
            m.sauver(fichier)
            test = self
            saisies = iter((entree, "quitter"))
            lignes, etats = [], []
            faux_mj = MagicMock(connexion="api", erreur_auth=None)
            faux_mj.echanger.side_effect = AssertionError("Appel au MJ")
            class Pont:
                def rafraichir(self, monde, *_):
                    self.monde = monde
                    etats.append(copy.deepcopy(monde.data))
                def lire(self, *_):
                    return next(saisies)
                def ecrire(self, *args, **_):
                    texte = " ".join(str(a) for a in args)
                    lignes.append(texte)
                    if hasattr(self, "monde") and self.monde.data.get("conversation"):
                        dernier = self.monde.data["conversation"][-1]
                        if texte == dernier["reponse"]:
                            test.assertEqual(Monde.charger(fichier).data, self.monde.data)
                def montrer(self, *_):
                    pass
            with (patch("jeu.MJ", return_value=faux_mj),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", wraps=analyser) as analyse,
                  patch.object(Monde, "d20", return_value=20)):
                self.assertEqual(jeu.main(["--console", "--connexion", "api", "--save", str(fichier)], interface=Pont()), 0)
            faux_mj.echanger.assert_not_called()
            faux_mj.raconter_resultat.assert_not_called()
            if isinstance(entree, DescripteurPublic):
                analyse.assert_not_called()
            recharge = Monde.charger(fichier)
            self.assertEqual(recharge.data, etats[-1])
            self.assertEqual(vues(recharge), vues(Monde(etats[-1])))
            return recharge, lignes

    def test_chaque_geste_objets_et_portes_parite_de_plan_effet_texte_et_recharge(self):
        for porte, gestes in ((False, GESTES[:9]), (True, ("examiner", "ouvrir", "fermer", "deverrouiller", "crocheter"))):
            for geste in gestes:
                with self.subTest(porte=porte, geste=geste):
                    m, premiere, seconde = scene(geste, porte)
                    cible, autre = seconde, premiere  # Choisir le second homonyme, jamais le premier par défaut.
                    self.assertTrue(m.visible(cible))
                    self.assertTrue(m.visible(autre))
                    self.assertEqual(m.objets[cible]["nom"], m.objets[autre]["nom"])
                    ref = reference(m, cible)
                    if porte:
                        m.joueur.update(position=[3, 4], orientation="sud")
                    d = DescripteurPublic({"geste": geste, "cible": ref})
                    p = proposition_descripteur(m, d)
                    self.assertEqual(p, analyser(m, geste + " " + ref))
                    a, b = m.copier(), m.copier()
                    try:
                        pa, pb = Moteur(a).preparer(d), Moteur(b).preparer(p)
                    except ErreurMonde as exc:
                        with self.assertRaises(ErreurMonde) as autre_refus:
                            Moteur(b).preparer(p)
                        self.assertEqual(str(exc), str(autre_refus.exception))
                    else:
                        self.assertEqual(pa.__dict__, pb.__dict__)
                    direct, ld = self.boucle(m.copier(), d)
                    texte, lt = self.boucle(m.copier(), geste + " " + ref)
                    # Seule la trace de la saisie diffère ; les réponses sont strictement identiques.
                    self.assertEqual(ld, lt)
                    dd, dt = copy.deepcopy(direct.data), copy.deepcopy(texte.data)
                    for data in (dd, dt):
                        for tour in data.get("conversation", []):
                            tour.pop("joueur", None)
                    self.assertEqual(dd, dt)
                    self.assertEqual(vues(direct), vues(texte))
                    # La simulation peut faire agir un PNJ pendant le geste. Le
                    # journal attribue au joueur le plan exact choisi, sans autre cible.
                    if direct.data["journal"]:
                        self.assertEqual(direct.data["journal"][-1]["action"], p)
                    if geste == "prendre":
                        self.assertEqual(direct.objets[cible]["lieu"], "joueur")
                        self.assertEqual(direct.objets[autre]["lieu"], "antichambre")
                    elif geste in ("ouvrir", "fermer"):
                        self.assertEqual(direct.objets[cible]["ouverte"], geste == "ouvrir")
                        self.assertEqual(direct.objets[autre]["ouverte"], geste == "fermer")
                    elif geste in ("allumer", "eteindre"):
                        # Un PNJ peut rallumer/éteindre ensuite cette même source.
                        # État complet et texte sont déjà comparés au moteur témoin ;
                        # le journal ci-dessus fixe l'identité de l'acte du joueur.
                        self.assertTrue(any("s'allume" in l or "s'éteint" in l for l in ld))

    def test_chaque_geste_perime_absent_ou_hors_vue_ne_change_pas_de_cible(self):
        for porte, gestes in ((False, GESTES[:9]), (True, ("examiner", "ouvrir", "fermer", "deverrouiller", "crocheter"))):
            for geste in gestes:
                for disparition in (False, True):
                    with self.subTest(porte=porte, geste=geste, disparition=disparition):
                        m, cible, autre = scene(geste, porte)
                        d = DescripteurPublic({"geste": geste, "cible": reference(m, cible)})
                        if disparition:
                            # Une référence disparue : une faute de référence ne se résout pas par le nom.
                            d = DescripteurPublic({"geste": geste, "cible": "reference_disparue"})
                        else:
                            m.joueur.update(salle="beffroi" if not porte else "grenier", position=[3, 3])
                        memoriser(m)
                        vues(m)
                        avant = copy.deepcopy(m.data)
                        recharge, lignes = self.boucle(m, d)
                        self.assertIn("Tu ne vois plus cette cible ici.", lignes)
                        self.assertEqual(recharge.data, avant)
                        self.assertNotIn("descripteur.cible", "\n".join(lignes))

    def test_entite_supprimee_apres_le_menu_ne_retombe_pas_sur_un_homonyme(self):
        for geste in ("prendre", "lire"):
            with self.subTest(geste=geste):
                m, cible, _ = scene(geste)
                ephemere = copy.deepcopy(m.objets[cible])
                ephemere["id"] = "cible_ephemere"
                m.objets["cible_ephemere"] = ephemere
                ref = reference(m, "cible_ephemere")
                self.assertIn(ref, {o["id"] for n in scene_percue(m)["niveaux"] for o in n["objets"]})
                d = DescripteurPublic({"geste": geste, "cible": ref})
                del m.objets["cible_ephemere"]
                vues(m)
                avant = copy.deepcopy(m.data)
                recharge, lignes = self.boucle(m, d)
                self.assertIn("Tu ne vois plus cette cible ici.", lignes)
                self.assertEqual(recharge.data, avant)

    def test_geste_devenu_impossible_reste_un_refus_du_moteur(self):
        for geste in ("ouvrir", "fermer"):
            m, cible, autre = scene(geste)
            d = DescripteurPublic({"geste": geste, "cible": cible})
            m.objets[cible]["ouverte"] = geste == "ouvrir"
            with self.assertRaises(ErreurMonde) as exc:
                Moteur(m).preparer(analyser(m, geste + " " + cible))
            recharge, lignes = self.boucle(m, d)
            self.assertIn(str(exc.exception), lignes)
            self.assertEqual(recharge.data, m.data)

    def test_parametres_publics_utilisent_la_meme_cle_et_le_meme_outil(self):
        for geste, modele in (("deverrouiller", "cle"), ("crocheter", "crochets")):
            with self.subTest(geste=geste):
                m, cible, autre = scene(geste, porte=True)
                m.joueur.update(position=[2, 1], orientation="nord")
                outil = copy.deepcopy(nouveau_defi(depart="fixe").objets[modele])
                outil.update(id="outil_test", lieu="joueur", nom="outil test", aliases=[])
                outil.pop("position", None)
                outil.pop("position_salle", None)
                if geste == "deverrouiller":
                    outil["ouvre"] = [cible]
                m.objets["outil_test"] = outil
                d = DescripteurPublic({"geste": geste, "cible": cible,
                                       "parametres": {"outil": "outil_test", "methode": "simple"}})
                self.assertEqual(proposition_descripteur(m, d), analyser(m, geste + " " + cible + " avec outil_test"))
                recharge, lignes = self.boucle(m, d)
                self.assertFalse(recharge.objets[cible]["verrouillee"])
                self.assertTrue(recharge.objets[autre]["verrouillee"])

    def test_page_ne_recoit_que_la_projection_percue_sans_preconditions(self):
        m = nouveau_defi(depart="fixe")
        installer(m)
        m.joueur.update(position=[5, 5], orientation="est")
        secret = copy.deepcopy(m.objets["marteau"])
        secret.update(id="entite_cachee_293", nom="secret cache 293", lieu=m.joueur["salle"])
        placer(secret, m.joueur["salle"], [3, 5])
        m.objets[secret["id"]] = secret
        pont = PontWeb()
        pont.rafraichir(m, None, None)
        self.assertNotIn("entite_cachee_293", json.dumps(pont.dernier_etat))
        self.assertNotIn("secret cache 293", json.dumps(pont.dernier_etat))
        interdits = {"profil", "besoins", "pulsions", "conditions", "preconditions", "effets", "seuil_coupe", "puissance"}
        def controler(v):
            if isinstance(v, dict):
                self.assertFalse(interdits & v.keys())
                for e in v.values():
                    controler(e)
            elif isinstance(v, list):
                for e in v:
                    controler(e)
        controler(pont.dernier_etat)

    def test_forme_fermee_et_aucun_effet_fourni_par_le_client(self):
        m, cible, _ = scene("prendre")
        for d in ({}, {"geste": "prendre", "cible": cible, "effets": []},
                  {"geste": "prendre", "cible": cible, "parametres": {"difficulte": 0}},
                  {"geste": "parler", "cible": cible}, {"geste": [], "cible": cible}):
            with self.subTest(d=d), self.assertRaises(ErreurMonde) as exc:
                Moteur(m).preparer(DescripteurPublic(d))
            self.assertTrue(exc.exception.attendu)

    def test_inconnu_ref_publique_exacte_sans_portrait_et_sans_voix_inventee(self):
        from donjon.noms import public
        m, cible, _ = scene("observer")
        m.objets[cible].pop("portrait", None)
        m.objets[cible].pop("facettes", None)
        ref = reference(m, cible)
        self.assertNotEqual(ref, cible)
        d = DescripteurPublic({"geste": "examiner", "cible": ref})
        recharge, lignes = self.boucle(m, d)
        self.assertNotIn(cible, json.dumps(public(recharge, lignes)))
        self.assertEqual(proposition_descripteur(m, d)["cible"], cible)
        with self.assertRaises(ErreurMonde):
            Moteur(m).preparer(DescripteurPublic({"geste": "examiner", "cible": cible}))

    def test_page_http_boucle_moteur_et_recharge_sans_analyse_ni_mj(self):
        from tests.test_web import Flux
        m, cible, autre = scene("prendre")
        with tempfile.TemporaryDirectory() as tmp:
            fichier = Path(tmp) / "partie.json"
            m.sauver(fichier)
            pont = PontWeb()
            serveur = Serveur(pont, 0)
            threading.Thread(target=serveur.serve_forever, daemon=True).start()
            faux_mj = MagicMock(connexion="api", erreur_auth=None)
            faux_mj.echanger.side_effect = AssertionError("Appel MJ au clic")
            with (patch("jeu.MJ", return_value=faux_mj),
                  patch.dict("os.environ", {"OPENAI_API_KEY": "test"}),
                  patch("jeu.analyser", side_effect=AssertionError("Analyse du clic"))):
                partie = threading.Thread(target=jeu.main,
                    args=(["--console", "--connexion", "api", "--save", str(fichier)],),
                    kwargs={"interface": pont}, daemon=True)
                partie.start()
                flux = Flux(serveur.server_address[1])
                def soumettre(corps):
                    c = http.client.HTTPConnection("127.0.0.1", serveur.server_address[1])
                    c.request("POST", "/commande", json.dumps(corps), {"Host": "127.0.0.1"})
                    r = c.getresponse()
                    self.assertEqual(r.status, 200)
                    r.read()
                    c.close()
                try:
                    flux.jusqu_a_pret()
                    soumettre({"descripteur": {"geste": "prendre", "cible": cible}})
                    evenements = flux.jusqu_a_pret()
                    recharge = Monde.charger(fichier)
                    self.assertEqual(recharge.objets[cible]["lieu"], "joueur")
                    self.assertEqual(recharge.objets[autre]["lieu"], "antichambre")
                    etat = next(e for e in evenements if e["type"] == "etat")
                    self.assertEqual(etat["scene"], scene_percue(recharge))
                    self.assertIn(recharge.data["conversation"][-1]["reponse"],
                                  [e.get("texte") for e in evenements])
                    soumettre({"descripteur": {"geste": "tourner", "cible": "ouest"}})
                    flux.jusqu_a_pret()
                    avant = Monde.charger(fichier)
                    soumettre({"descripteur": {"geste": "prendre", "cible": autre}})
                    refus = flux.jusqu_a_pret()
                    self.assertIn("Tu ne vois plus cette cible ici.", [e.get("texte") for e in refus])
                    soumettre({"texte": "quitter"})
                    partie.join(10)
                    self.assertFalse(partie.is_alive())
                    self.assertEqual(Monde.charger(fichier).data, avant.data)
                    self.assertEqual(next(e for e in refus if e["type"] == "etat")["scene"], scene_percue(avant))
                    faux_mj.echanger.assert_not_called()
                finally:
                    if partie.is_alive():
                        pont.commandes.put("quitter")
                        partie.join(5)
                    flux.connexion.close()
                    serveur.arreter()

    def test_http_transporte_le_descripteur_et_refuse_les_entrees_ambigues(self):
        pont = PontWeb()
        serveur = Serveur(pont, 0)
        threading.Thread(target=serveur.serve_forever, daemon=True).start()
        try:
            for corps, attendu in (({"texte": "x", "descripteur": {}}, 400),
                                    ({"descripteur": {"geste": "prendre", "cible": "torche"}}, 200)):
                pont.occupe = False
                c = http.client.HTTPConnection("127.0.0.1", serveur.server_address[1])
                c.request("POST", "/commande", json.dumps(corps), {"Host": "127.0.0.1"})
                r = c.getresponse()
                self.assertEqual(r.status, attendu)
                r.read()
                c.close()
            self.assertEqual(pont.commandes.get_nowait(), DescripteurPublic(corps["descripteur"]))
        finally:
            serveur.arreter()


if __name__ == "__main__":
    unittest.main()
