"""A1 : accès unique, stockage inchangé et parcours réels après rechargement.

Le même relevé AST sur 42bb9c0 trouve 46 accès directs (jeu et outils,
contrats de mission et champs publics compris), dans quatorze fichiers.
Les clés de dictionnaires produits pour le MJ/l'audit restent un format public.
"""
import ast
import copy
from pathlib import Path
import unittest

from donjon import agendas
from donjon.biens import bourse
from donjon.echanges import engager
from donjon.esprits import lire, percevoir_tous
from donjon.paroles import engagements_enregistres, preparer_parole
from donjon.spatial import porte_par
from tests.support import presentes, regarder
from tests.support import canal_constats_anterieur_337
from tests import test_crochetage_surenchere as cs
from tests.test_parts_achetees import antichambre_du_banc, parole
from tests.test_taches_payees import sans_flamme
from tests.test_tensions import recharger, vivre

RACINE = Path(__file__).resolve().parents[1]


def acces(source):
    """Lectures et écritures par indice ou méthode, y compris les retraits."""
    lignes = []
    for n in ast.walk(ast.parse(source)):
        cle = None
        if isinstance(n, ast.Subscript):
            cle = n.slice
        elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr in ("get", "setdefault", "pop", "__getitem__", "__setitem__", "__delitem__")
              and n.args):
            cle = n.args[0]
        if isinstance(cle, ast.Constant) and cle.value in ("engagements", "agendas", "confies", "confirme", "attributions", "mandats_percus", "agendas_joueur", "offres_mandat_joueur", "reference_temporelle", "sequence_obligations", "issues_obligations", "accord_initial"):
            lignes.append(n.lineno)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "update":
            lignes.extend(n.lineno for k in n.keywords if k.arg in ("engagements", "agendas", "confies", "confirme", "attributions", "mandats_percus", "agendas_joueur", "offres_mandat_joueur", "reference_temporelle", "sequence_obligations", "issues_obligations", "accord_initial"))
    return lignes


class AccesTests(unittest.TestCase):
    def test_seul_agendas_accede_au_stockage(self):
        sources = [*RACINE.glob("*.py"), *(RACINE / "donjon").rglob("*.py"),
                   *(RACINE / "tools").rglob("*.py")]
        self.assertGreater(len(sources), 50)
        fautes = [f"{p.relative_to(RACINE)}:{ligne}" for p in sources
                  if p != RACINE / "donjon" / "agendas.py"
                  for ligne in acces(p.read_text(encoding="utf-8"))]
        self.assertEqual(fautes, [])

    def test_controle_lectures_et_ecritures(self):
        for source in ('e["engagements"]', 'e["engagements"] = []',
                       'del e["engagements"]', 'e.get("engagements")',
                       'e.setdefault("engagements", [])', 'e.pop("engagements")',
                       'e.update(engagements=[])', 'profil.get("agendas")',
                       'a["confies"]', 'a.get("confirme")', 'a.update(confies=[])',
                       'a.get("attributions")', 'a.update(attributions=[])',
                       'a.get("agendas_joueur")', 'a.update(offres_mandat_joueur=[])',
                       'e.get("mandats_percus")', 'e.update(mandats_percus=[])',
                       'e.get("reference_temporelle")', 'e.update(reference_temporelle={})',
                       'e.get("sequence_obligations")', 'e.update(sequence_obligations=1)',
                       'e.get("issues_obligations")', 'e.update(issues_obligations=[])',
                       'e.get("accord_initial")', 'e.update(accord_initial={})'):
            with self.subTest(source=source):
                self.assertEqual(acces(source), [1])

    def test_lectures_copiees_et_depart_sans_effet(self):
        m = antichambre_du_banc()
        avant = copy.deepcopy(m.data)
        self.assertEqual(agendas.depart(m, "aubin"), [])
        self.assertEqual(agendas.en_cours(m, "aubin"), [])
        self.assertEqual(m.data, avant)
        # Une déclaration future reste une donnée, sans activer de mécanique A4.
        declaration = {"sorte": "garder", "parametres": {"lieu": "antichambre"}}
        m.objets["aubin"]["profil"]["agendas"] = [declaration]
        avant = copy.deepcopy(m.data)
        agendas.depart(m, "aubin")[0]["parametres"]["lieu"] = "galerie"
        self.assertEqual(m.data, avant)
        engagement = {"condition": {"objet": "brasero", "allume": True},
                      "pour": "joueur", "minute": m.data["minutes"]}
        agendas.prendre(m, "aubin", engagement)
        engagement["condition"]["allume"] = False
        lecture = agendas.en_cours(m, "aubin", objet="brasero", personne="joueur")
        self.assertTrue(lecture[0]["condition"]["allume"])
        lecture[0]["condition"]["allume"] = False
        self.assertTrue(agendas.en_cours(m, "aubin")[0]["condition"]["allume"])
        lecture.clear()
        self.assertEqual(len(agendas.en_cours(m, "aubin")), 1)


class ChaineTests(unittest.TestCase):
    def test_relais_part_promise_puis_tenue(self):
        m = antichambre_du_banc()
        m, rapport = preparer_parole(m, parole("aubin", "Je te paie trois pièces pour une de tes planches.",
                                              "demande", "planches", "3"))
        m = recharger(m)
        condition = {"objet": "planches_1", "remettre": "joueur"}
        self.assertEqual(len(agendas.en_cours(m, "aubin", condition=condition)), 1)
        self.assertTrue(any("ira chercher une part" in t for t in rapport["faits"]))
        self.assertTrue(any("engagement pris" in t for t in engagements_enregistres(m, "aubin")))
        m, lignes = vivre(m, 3)
        m = recharger(m)
        self.assertEqual(agendas.en_cours(m, "aubin"), [])
        self.assertTrue(porte_par(m, "planches_1", "joueur"))
        self.assertEqual(m.objets["planches_1"]["proprietaire"], "joueur")
        self.assertEqual(m.joueur["or"], 21)
        self.assertIn("Aubin te remet les planches de bac : tu l'avais payé.", lignes)
        self.assertTrue(any(s["type"] == "engagement_tenu" for s in lire(m, "aubin")["memoire"]))
        self.assertFalse(any("engagement pris" in t for t in engagements_enregistres(m, "aubin")))

    def abandon_paye(self):
        m = cs.TacheAccepteeTests().tilo_paye_pour_l_atre(briquet=True)
        presentes(m, "tilo")
        m.joueur.update(salle="salle_commune", position=[3, 3], orientation="ouest")
        regarder(m, "joueur", "tilo")
        percevoir_tous(m)
        m.joueur["or"] = 100
        avant = (m.joueur["or"], bourse(m, "tilo"))
        condition = {"objet": "atre", "allume": True}
        self.assertEqual(engager(m, "joueur", "tilo", condition, 20), "accepte")
        m = recharger(m)
        self.assertEqual(len(agendas.en_cours(m, "tilo", condition=condition, actifs=True)), 1)
        self.assertEqual((m.joueur["or"], bourse(m, "tilo")), (avant[0] - 20, avant[1] + 20))
        self.assertTrue(any("engagement pris" in t for t in engagements_enregistres(m, "tilo")))
        sans_flamme(m, "tilo")
        m.objets["briquet"]["lieu"] = "cuisine"
        lire(m, "tilo")["croyances"].pop("briquet", None)
        agendas.echoir(m, "tilo")
        m = recharger(m)
        self.assertFalse(m.objets["atre"]["allume"])
        self.assertEqual(agendas.en_cours(m, "tilo"), [])
        return m, avant

    def test_tache_payee_acceptee_puis_abandonnee(self):
        m, avant = self.abandon_paye()
        # Isoler le remboursement intégral d'une autre dépense autonome :
        # Tilo attend ici deux minutes. Le solde normal entre créancier et
        # débiteur reste exécuté par la vie des PNJ, même pendant cette attente.
        lire(m, 'tilo')['libre'] = 2 * 600
        m, lignes = vivre(m, 2)
        m = recharger(m)
        self.assertEqual(agendas.en_cours(m, "tilo"), [])
        self.assertEqual((m.joueur["or"], bourse(m, "tilo")), avant)
        self.assertEqual(m.data.get("dettes", []), [])
        self.assertTrue(any("te rend 20 pièces" in t for t in lignes), lignes)
        self.assertTrue(any(s["type"] == "engagement_abandonne" for s in lire(m, "tilo")["memoire"]))
        self.assertFalse(any("engagement pris" in t for t in engagements_enregistres(m, "tilo")))

    @canal_constats_anterieur_337
    def test_achat_apres_abandon_conserve_la_piece_due_puis_la_solde(self):
        from donjon.biens import payer, solder
        from donjon.rendu import regarder as rendu
        from donjon.scene import scene_percue
        m, avant = self.abandon_paye()
        odile = bourse(m, 'odile')
        total = m.joueur['or'] + sum(m.data['finances_pnj'].values())
        from tests.support import possessions_deja_confiees
        possessions_deja_confiees(m)  # La fenêtre de deux minutes porte sur achat puis solde.
        m, lignes = vivre(m, 2)
        m = recharger(m)
        # Parcours naturel 228 : une pièce réellement payée à Odile pour le
        # bois avant le solde de minute ; les dix-neuf autres sont remboursées.
        self.assertEqual(m.joueur['or'], avant[0] - 1)
        self.assertEqual(bourse(m, 'tilo'), 0)
        self.assertEqual(bourse(m, 'odile'), odile + 1)
        self.assertEqual(m.joueur['or'] + sum(m.data['finances_pnj'].values()), total)
        self.assertEqual(m.objets['bois_cuisine']['lieu'], 'tilo')
        self.assertEqual(m.objets['bois_cuisine']['proprietaire'], 'tilo')
        self.assertTrue(any('te rend 19 pièces' in t for t in lignes))
        self.assertEqual(m.data['dettes'], [dict(de='tilo', a='joueur', montant=1,
                                               objet='atre', quoi='tache', minute=0)])
        recharge = recharger(m)
        self.assertEqual(m.data, recharge.data)
        self.assertEqual(rendu(m), rendu(recharge))
        self.assertEqual(scene_percue(m), scene_percue(recharge))
        avant_solde = copy.deepcopy(m.data)
        solder(m, [])
        self.assertEqual(m.data, avant_solde)  # Sans fonds, ni oubli ni double versement.
        # Apport explicite, prélevé chez celle qui a reçu la pièce : aucun or créé.
        payer(m, 'odile', 'tilo', 1)
        solder(m, lignes)
        m = recharger(m)
        self.assertEqual((m.joueur['or'], bourse(m, 'tilo')), avant)
        self.assertEqual(bourse(m, 'odile'), odile)
        self.assertEqual(m.data['dettes'], [])
        self.assertEqual(m.joueur['or'] + sum(m.data['finances_pnj'].values()), total)
        self.assertTrue(any('te rend 1 pièce' in t for t in lignes))


if __name__ == "__main__":
    unittest.main()
