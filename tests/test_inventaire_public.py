"""U-M inventaire : callbacks réels, identité, quantité et reprise sans modèle."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from donjon.commandes import DescripteurPublic, analyser, proposition_descripteur
from donjon.defi import nouveau_defi
from donjon.geometrie import placer
from donjon.monde import ErreurMonde, Monde
from donjon.moteur import Moteur
from donjon.noms import reference, installer as installer_noms
from donjon.spatial import memoriser
from donjon.web.pont import PontWeb
from tests import test_descripteur_public as support_descripteur
from tests.test_matiere import planches

scene, vues = support_descripteur.scene, support_descripteur.vues


def besace(geste, modele="marteau"):
    m, premiere, seconde = scene("prendre")
    m.joueur["capacite"] = 50  # Les deux lots doivent tenir avant tout geste.
    original = nouveau_defi(depart="fixe").objets[modele]
    for id in (premiere, seconde):
        m.objets[id] = {**copy.deepcopy(original), "id": id, "lieu": "joueur",
                        "nom": "bien identique", "aliases": [], "proprietaire": "joueur"}
        for k in ("position", "position_salle", "ancrage_carte"):
            m.objets[id].pop(k, None)
        if geste == "prelever" or modele == "planches":
            m.objets[id]["physique"] = planches()
        if geste in ("allumer", "eteindre"):
            m.objets[id]["allume"] = geste == "eteindre"
    m.objets["marchand"]["lieu"] = m.joueur["salle"]
    placer(m.objets["marchand"], m.joueur["salle"], [2, 3])
    m = Monde(copy.deepcopy(m.data))
    memoriser(m)
    vues(m)
    return m, seconde, premiere


def etat(m):
    pont = PontWeb()
    pont.rafraichir(m, None, None)
    return pont.dernier_etat


def clics(m):
    page = Path(__file__).resolve().parents[1] / "donjon/web/page.html"
    sonde = Path(__file__).with_name("clic_page.js")
    p = subprocess.run(["node", str(sonde), str(page)], input=json.dumps(etat(m)),
                       capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(p.stdout)["inventaire"]


@unittest.skipUnless(shutil.which("node"), "node absent")
class InventairePublicTests(unittest.TestCase):
    boucle = support_descripteur.DescripteurPublicTests.boucle

    def test_chaque_geste_deux_biens_homonymes_plan_effet_texte_et_vues_recharges(self):
        # Cas réels du Relais (planches, torche, vivres), puis autres biens de même nature.
        for geste, modeles in (("poser", ("marteau", "planches")),
                               ("remettre", ("marteau", "planches")),
                               ("manger", ("vivres", "vivres")),
                               ("allumer", ("torche", "lanterne")),
                               ("eteindre", ("torche", "lanterne")),
                               ("prelever", ("planches", "planches"))):
            for n, modele in enumerate(modeles):
                with self.subTest(geste=geste, modele=modele, n=n):
                    m, cible, autre = besace(geste, modele)
                    if geste == "manger" and n:
                        m.objets[cible]["portions"] = 3
                    if geste == "prelever" and n:
                        m.objets[cible]["physique"].update(pieces=4, nom_piece="pièce de bois")
                    if geste == "remettre" and n:
                        # Un second destinataire homonyme : choisir celui-là explicitement.
                        m.objets["autre_personne"] = {**copy.deepcopy(m.objets["marchand"]), "id": "autre_personne"}
                        installer_noms(m)
                        destinataire = "autre_personne"
                    else:
                        destinataire = "marchand"
                    memoriser(m)
                    ref = reference(m, cible)
                    dons = reference(m, destinataire)
                    envois = [c for c in clics(m) if c["envoye"]["geste"] == geste
                              and c["envoye"]["cible"] == ref
                              and (geste != "remettre" or c["envoye"]["parametres"]["destinataire"] == dons)]
                    self.assertEqual(len(envois), 1)
                    self.assertEqual(envois[0]["clics"], 3 if geste == "remettre" else 2)
                    d = DescripteurPublic(envois[0]["envoye"])
                    commande = (f"donner {ref} à {dons}" if geste == "remettre" else f"{geste} {ref}")
                    p = proposition_descripteur(m, d)
                    self.assertEqual(p, analyser(m, commande))
                    a, b = m.copier(), m.copier()
                    direct_plan, texte_plan = Moteur(a).preparer(d), Moteur(b).preparer(analyser(b, commande))
                    if geste == 'remettre':
                        # Lot 380 : les remises rejoignent U-C. Le transport du
                        # clic ajoute la garde de péremption ; le plan reste identique.
                        self.assertTrue(direct_plan.confirmation)
                        self.assertTrue(texte_plan.confirmation)
                        self.assertEqual(direct_plan.choix_public, (d, 'règles'))
                        self.assertTrue(direct_plan.etat_consentement)
                        self.assertEqual(texte_plan.choix_public, (p, 'règles'))
                        self.assertEqual(direct_plan.etat_consentement, texte_plan.etat_consentement)
                        direct_plan.choix_public = None
                        texte_plan.choix_public = None
                    self.assertEqual(direct_plan.__dict__, texte_plan.__dict__)
                    direct, ld = self.boucle(m.copier(), d, confirmer=geste == 'remettre')
                    texte, lt = self.boucle(m.copier(), commande, confirmer=geste == 'remettre')
                    self.assertEqual(ld, lt)
                    dd, dt = copy.deepcopy(direct.data), copy.deepcopy(texte.data)
                    for data in (dd, dt):
                        for tour in data.get("conversation", []):
                            tour.pop("joueur", None)
                    self.assertEqual(dd, dt)
                    self.assertEqual(vues(direct), vues(texte))
                    self.assertEqual(etat(direct), etat(texte))
                    self.assertEqual(direct.objets[autre]["lieu"], "joueur")
                    if geste == "poser":
                        self.assertEqual(direct.objets[cible]["lieu"], m.joueur["salle"])
                    elif geste == "remettre":
                        self.assertEqual(direct.objets[cible]["lieu"], destinataire)
                    elif geste == "manger":
                        self.assertEqual(direct.objets[cible]["portions"], m.objets[cible]["portions"] - 1)
                        self.assertEqual(direct.objets[autre]["portions"], m.objets[autre]["portions"])
                    elif geste == "prelever":
                        self.assertEqual(direct.objets[cible]["physique"]["pieces"], m.objets[cible]["physique"]["pieces"] - 1)
                        self.assertEqual(direct.objets[autre]["physique"]["pieces"], 2)
                        self.assertEqual(direct.objets[cible + "_1"]["lieu"], "joueur")
                    else:
                        self.assertEqual(direct.objets[cible]["allume"], geste == "allumer")
                        self.assertEqual(direct.objets[autre]["allume"], geste == "eteindre")
                    if geste in {"poser", "remettre"} and modele == "planches":
                        self.assertEqual(direct.objets[cible]["physique"]["pieces"], 2)

    def test_cible_perimee_pour_tous_les_gestes_ne_vise_pas_un_homonyme(self):
        for geste, modele in (("poser", "marteau"), ("remettre", "marteau"), ("manger", "vivres"),
                               ("allumer", "torche"), ("eteindre", "torche"), ("prelever", "planches")):
            with self.subTest(geste=geste):
                m, cible, autre = besace(geste, modele)
                d = next(c["envoye"] for c in clics(m) if c["envoye"]["geste"] == geste and c["envoye"]["cible"] == cible)
                m.objets[cible]["lieu"] = "reserve"
                placer(m.objets[cible], "reserve", [1, 1])
                memoriser(m)
                avant = copy.deepcopy(m.data)
                recharge, lignes = self.boucle(m, DescripteurPublic(d))
                self.assertEqual(recharge.data, avant)
                self.assertEqual(recharge.objets[autre]["lieu"], "joueur")
                self.assertIn("Tu ne vois plus cette cible ici.", lignes)

    def test_menu_sans_mode_cases_et_sans_destinataire_percu(self):
        m, cible, autre = besace("poser")
        m.data["mode_cases"] = False
        for o in m.objets.values():
            if o["type"] == "personnage":
                o["lieu"] = "echoppe"
                placer(o, "echoppe", [1, 1])
        self.assertIsNone(etat(m)["scene"])
        self.assertEqual(etat(m)["destinataires"], [])
        envois = clics(m)
        self.assertTrue(envois)
        self.assertNotIn("remettre", {c["envoye"]["geste"] for c in envois})
        d = next(c["envoye"] for c in envois if c["envoye"] == {"geste": "poser", "cible": cible})
        recharge, lignes = self.boucle(m, DescripteurPublic(d))
        self.assertEqual(recharge.objets[cible]["lieu"], m.joueur["salle"])
        self.assertEqual(recharge.objets[autre]["lieu"], "joueur")

    def test_destinataire_parti_ou_eloigne_refus_public_sans_effet_apres_recharge(self):
        for loin in (False, True):
            with self.subTest(loin=loin):
                m, cible, autre = besace("remettre")
                d = next(c["envoye"] for c in clics(m) if c["envoye"]["geste"] == "remettre" and c["envoye"]["cible"] == cible)
                salle = m.joueur["salle"] if loin else "echoppe"
                m.objets["marchand"]["lieu"] = salle
                placer(m.objets["marchand"], salle, [6, 3] if loin else [1, 1])
                memoriser(m)
                self.assertNotIn(d["parametres"]["destinataire"], {p["id"] for p in etat(m)["destinataires"]})
                avant = copy.deepcopy(m.data)
                recharge, lignes = self.boucle(m, DescripteurPublic(d))
                self.assertEqual(recharge.data, avant)
                self.assertTrue(any("Approche-toi" in l or "Tu ne vois plus" in l for l in lignes))
                self.assertNotIn("descripteur.", "\n".join(lignes))

    def test_quantite_ou_destinataire_non_admis_ne_sont_jamais_ignores(self):
        m, cible, _ = besace("prelever", "planches")
        for geste, parametres in (("prelever", {"quantite": 2}), ("prelever", {"quantite": True}),
                                  ("manger", {"quantite": "1"}), ("poser", {"quantite": 1}),
                                  ("poser", {"destinataire": "marchand"}), ("remettre", {}),
                                  ("remettre", {"destinataire": "lanterne"}),
                                  ("remettre", {"destinataire": "marchand"})):
            with self.subTest(geste=geste, parametres=parametres), self.assertRaises(ErreurMonde) as refus:
                Moteur(m).preparer(DescripteurPublic({"geste": geste, "cible": cible, "parametres": parametres}))
            self.assertTrue(refus.exception.attendu)

    def test_biens_portes_connus_dans_le_noir_et_prelevement_perime(self):
        for geste in ("poser", "allumer", "prelever"):
            with self.subTest(geste=geste):
                m, cible, autre = besace(geste, "torche" if geste == "allumer" else "planches")
                d = next(c["envoye"] for c in clics(m) if c["envoye"]["geste"] == geste and c["envoye"]["cible"] == cible)
                for o in m.objets.values():
                    if "allume" in o:
                        o["allume"] = False
                memoriser(m)
                if geste == "prelever":
                    self.assertTrue(any(c["envoye"] == d for c in clics(m)))
                    separe, lignes = self.boucle(m.copier(), DescripteurPublic(d))
                    self.assertEqual(separe.objets[cible]["physique"]["pieces"], 1)
                    self.assertEqual(separe.objets[cible + "_1"]["lieu"], "joueur")
                    m.objets[cible]["physique"]["pieces"] = 1
                    avant = copy.deepcopy(m.data)
                    recharge, lignes = self.boucle(m, DescripteurPublic(d))
                    self.assertEqual(recharge.data, avant)
                    self.assertTrue(any("une pièce" in l for l in lignes))
                else:
                    self.assertIn(cible, {o["id"] for o in etat(m)["inventaire"]})
                    recharge, lignes = self.boucle(m, DescripteurPublic(d))
                    self.assertTrue(recharge.objets[cible]["allume"] if geste == "allumer" else recharge.objets[cible]["lieu"] != "joueur")

    def test_projection_fermee_sans_contenu_cache_ni_personne_non_percue(self):
        m, cible, _ = besace("poser")
        coffre = copy.deepcopy(m.objets["coffre"])
        coffre.update(id="besace_fermee", lieu="joueur", ouverte=False)
        m.objets[coffre["id"]] = coffre
        m.objets["secret_inventaire_298"] = {**copy.deepcopy(m.objets[cible]), "id": "secret_inventaire_298", "lieu": coffre["id"]}
        m.objets["brune"].update(lieu="echoppe")
        placer(m.objets["brune"], "echoppe", [1, 1])
        e = etat(m)
        self.assertNotIn("secret_inventaire_298", json.dumps(e))
        self.assertNotIn("brune", json.dumps(e["destinataires"]))
        for o in e["inventaire"]:
            self.assertLessEqual(set(o), {"id", "nom", "type", "allume", "pieces"})
            self.assertEqual(m.objets[o["id"]]["lieu"], "joueur")
        for p in e["destinataires"]:
            self.assertEqual(set(p), {"id", "nom"})
        # Identité publique d'un inconnu : l'identifiant privé n'est pas un choix.
        ref = reference(m, "marchand")
        self.assertNotEqual(ref, "marchand")
        self.assertIn(ref, {p["id"] for p in e["destinataires"]})
        self.assertNotIn("marchand", json.dumps(e["destinataires"]))


if __name__ == "__main__":
    unittest.main()
