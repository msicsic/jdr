"""Même bien et même quantité entre saisie, revue, transaction et recharge."""
import unittest

from donjon.banc_pnj import creer
from donjon.biens import compte, livraisons_dues
from donjon.esprits import lire, percevoir_tous
from donjon.matiere import id_piece, appliquer, valider
from donjon.paroles import resoudre, sens_contenu
from donjon.rendu import decrire_comptes, fiche
from donjon.spatial import porte_par
from tests.support import calme, presentes, regarder
from tests.test_audits_attendu import jouer
from tests.test_comptes_issue import audit
from tests.test_parts_achetees import antichambre_du_banc
from tests.test_repli_et_appel import dialogue, parole
from tests.test_tensions import placer, recharger, vivre


def auberge():
    m = presentes(calme(creer("auberge", 1985, "fixe"), "joss"), "joss")
    placer(m, "joss", "etable", (5, 3))
    m.joueur.update(salle="etable", position=[5, 2])
    regarder(m, "joss", "joueur")
    regarder(m, "joueur", "joss")
    # Une donnée explicite : le nom collectif diffère du nom d'une pièce.
    o = m.objets["fagots_etable"]
    o.update(nom="réserve de chauffage", aliases=["réserve de chauffage"], charges=3)
    appliquer(o, valider(o, {"forme": "bloc", "matiere": "bois", "pieces": 3,
        "nom_piece": "bûche de chauffage", "dimensions": {
            "longueur_cm": 40, "largeur_cm": 10, "hauteur_cm": 10}}))
    m.data["connus"].append("fagots_etable")  # La réserve a été examinée.
    percevoir_tous(m)
    return recharger(m)


class PieceDeLotTests(unittest.TestCase):
    def achat(self, m, qui, lot, mots, contenu, mauvais=None, source_invalide=False):
        m = recharger(m)
        or_avant, nombre = m.joueur["or"], m.objets[lot]["charges"]
        piece = id_piece(m, lot)
        prix = 3 if qui == "aubin" else 1
        c = compte(qui, "joueur", piece, 1)
        cs = [compte("joueur", qui, montant=prix, etat="rendu"), c]
        bon = "Entendu."
        p = parole(mots, ("demande", lot, "", str(prix)), personnage=qui)
        p["proposition"]["contenu"] = [contenu]
        propositions = [p]
        if source_invalide:
            import copy
            faux = copy.deepcopy(p)
            faux["proposition"]["contenu"][0]["contrepartie"]["objet"] = lot
            propositions.insert(0, faux)
        revues = [{"conforme": True, "motif": "Même bien et une seule part."}]
        if mauvais:
            faux = parole(mots, ("demande", mauvais, "", str(prix)), personnage=qui)
            propositions.insert(0, faux)
            revues.insert(0, {"conforme": False, "motif": "Un autre objet est demandé."})
        r, sortie, appels = jouer(m, mots, propositions + [dialogue(f"« {bon} »")],
                                  [audit(bon, cs, qui)], revues=revues)
        self.assertIn(bon, sortie)
        self.assertNotIn("Précise", sortie)
        self.assertEqual(r.joueur["or"], or_avant - prix)
        self.assertEqual(r.objets[lot]["charges"], nombre - 1)
        self.assertIn(c, livraisons_dues(r))
        self.assertIn("remettre", decrire_comptes(r))
        dossiers = [e["plan"]["parole"] for f, e in appels if f == "auditer_action"]
        sens = dossiers[-1]["sens_contenu"][0]["demande"]
        self.assertEqual((sens["objet"], sens["quantite"], sens["unite"]), (lot, 1, "part"))
        self.assertEqual(sens["nom_lot"], m.objets[lot]["nom"])
        # Le dossier conserve les désignations et quantités communes ; la revue
        # reçoit en plus les opérations exécutables et le prix du lot 89.
        self.assertEqual([{k: v for k, v in s.items() if k not in ("operations", "prix_offert")}
                          for s in dossiers[-1]["sens_contenu"]], sens_contenu([contenu], m))
        self.assertIn(bon, str(recharger(r).data["conversation"]))
        r, lignes = vivre(r, 3)
        r = recharger(r)
        self.assertTrue(porte_par(r, piece, "joueur"), lignes)
        self.assertEqual(r.objets[piece]["proprietaire"], "joueur")
        self.assertFalse(livraisons_dues(r))
        self.assertIn(r.objets[piece]["nom"], fiche(r))
        self.assertEqual(lire(r, qui)["engagements"], [])
        return r, dossiers

    def test_source_pieces_corrigee_sans_perdre_achat(self):
        from donjon.echanges import enqueter
        for m, qui, lot, prix, mots in (
                (presentes(antichambre_du_banc(), "aubin"), "aubin", "planches", 3,
                 "je paie Aubin trois pièces pour une de ses planches"),
                (auberge(), "joss", "fagots_etable", 1,
                 "Je t'achète une bûche de chauffage pour une pièce.")):
            with self.subTest(vendeur=qui):
                enqueter(m, "joueur", qui, "bois")
                contenu = {"type": "proposition", "demande": {"type": "part", "objet": lot},
                           "contrepartie": {"type": "pieces", "montant": prix}}
                from donjon.propositions import verifier
                from donjon.monde import ErreurMonde
                import copy
                faux = copy.deepcopy(contenu)
                faux["contrepartie"]["objet"] = lot
                avant = copy.deepcopy(m.data)
                with self.assertRaises(ErreurMonde) as refus:
                    verifier(m, faux)
                self.assertIn("contrepartie.objet", refus.exception.attendu)
                self.assertIn(repr(lot), refus.exception.attendu)
                self.assertIn("retirer", refus.exception.attendu)
                self.assertIn(repr(contenu["contrepartie"]), refus.exception.attendu)
                self.assertEqual(m.data, avant)
                self.achat(m, qui, lot, mots, contenu, source_invalide=True)

    def test_planche_singuliere_marche_reel_et_demande(self):
        for type_ in ("proposition", "demande"):
            with self.subTest(type=type_):
                m = presentes(antichambre_du_banc(), "aubin")
                from donjon.echanges import enqueter
                enqueter(m, "joueur", "aubin", "bois")
                contenu = ({"type": "proposition", "demande": {"type": "part", "objet": "planches"},
                    "contrepartie": {"type": "pieces", "montant": 3}} if type_ == "proposition" else
                    {"type": "demande", "sujet": "planche", "attribut": "", "valeur": "3"})
                _, dossiers = self.achat(m, "aubin", "planches",
                    "je paie Aubin trois pièces pour une planche", contenu)
                self.assertIn("planche", dossiers[-1]["sens_contenu"][0]["demande"]["designations"])

    def test_piece_de_reserve_nommee_sans_alias_manuel(self):
        m = auberge()
        self.assertEqual(m.trouver("bûche de chauffage"), "fagots_etable")
        self.assertEqual(resoudre(m, "bûche"), "fagots_etable")
        _, dossiers = self.achat(m, "joss", "fagots_etable",
            "Je t'achète une bûche de chauffage pour une pièce.",
            {"type": "demande", "sujet": "bûche de chauffage", "attribut": "", "valeur": "1"})
        self.assertIn("bûche de chauffage", str(dossiers[-1]))

    def test_autre_objet_refuse_avant_transaction(self):
        m = presentes(antichambre_du_banc(), "aubin")
        from donjon.echanges import enqueter
        enqueter(m, "joueur", "aubin", "bois")
        avant = dict(m.objets["briquet"])
        r, dossiers = self.achat(m, "aubin", "planches",
            "je paie Aubin trois pièces pour une planche",
            {"type": "demande", "sujet": "planche", "attribut": "", "valeur": "3"},
            mauvais="briquet")
        self.assertEqual(dossiers[0]["sens_contenu"][0]["demande"]["objet"], "briquet")
        self.assertEqual(r.objets["briquet"], avant)

    def test_sens_garde_quantite_identite_et_connaissance(self):
        m = recharger(auberge())
        lot = "fagots_etable"
        c = {"type": "proposition", "demande": {"type": "part", "objet": lot},
             "contrepartie": {"type": "objet", "objet": lot}}
        sens = sens_contenu([c], m)[0]
        self.assertEqual(sens["demande"]["unite"], "part")
        self.assertEqual(sens["contrepartie"]["unite"], "objet")
        self.assertEqual(sens["demande"]["quantite"], 1)
        self.assertIn("bûche de chauffage", sens["demande"]["designations"])
        m.objets["reserve_cachee"] = {**m.objets[lot], "id": "reserve_cachee",
            "nom": "réserve secrète", "aliases": [], "lieu": "grenier"}
        m = recharger(m)
        c["demande"]["objet"] = "reserve_cachee"
        self.assertNotIn("demande", sens_contenu([c], m)[0])
