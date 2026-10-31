"""Même recherche et même partie que fbcf0ff, sans copie de préfixe."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from donjon import planification as p
from donjon.monde import Monde
from donjon.moteur import Moteur, proposition
from donjon.rendu import regarder
from donjon.scene import scene_percue
from tests.test_planification import relais
from tests.test_tensions import recharger
from tests.support import sans_indices_soupcon_passifs
from tests.support import canal_constats_anterieur_337


DONNEES = Path(__file__).parent / "data/cout-12h"


def _empreinte(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _sans_ascendant_neutre(x):
    """Projection pré-248, y compris les relations sérialisées dans les refus.

    Refuse tout axe actif : l'oracle doit continuer à détecter un changement
    de comportement. Les formats JSON imbriqués sont conservés exactement.
    """
    if isinstance(x, dict):
        resultat = {}
        for k, valeur in x.items():
            if k == 'ascendant':
                assert (type(valeur) is int and valeur == 0 or valeur is False or
                        isinstance(valeur, list) and len(valeur) == 2 and
                        type(valeur[0]) is int and valeur[0] == 0 and
                        type(valeur[1]) is int and valeur[1] >= 0), 'Ascendant non neutre'
            else:
                resultat[k] = _sans_ascendant_neutre(valeur)
        return resultat
    if isinstance(x, list):
        return [_sans_ascendant_neutre(v) for v in x]
    if isinstance(x, str) and x.startswith(('{', '[')):
        try:
            valeur = json.loads(x)
        except ValueError:
            return x
        normalise = _sans_ascendant_neutre(valeur)
        if normalise != valeur:
            for tri in (True, False):
                for ascii_ in (True, False):
                    options = dict(sort_keys=tri, ensure_ascii=ascii_)
                    if json.dumps(valeur, **options) == x:
                        return json.dumps(normalise, **options)
            raise AssertionError('Format JSON de relation inconnu')
    return x


def _etat(e):
    return e.salle, sorted(e.portes), sorted(e.faits.items(), key=repr), e.allure


@canal_constats_anterieur_337
def observer_capture(scenario):
    """Oracle enregistré sur la base : toutes les sorties du tas et tous les plans,
    puis la chaîne moteur, monde, journal et vue après recharge (480–485 min).
    Les préfixes du tas ne font volontairement pas partie de la projection.
    """
    m = recharger(Monde(json.loads(gzip.decompress(
        (DONNEES / f"{scenario}-1985-480.json.gz").read_bytes()))))
    visites, plans = hashlib.sha256(), hashlib.sha256()
    n_visites = n_plans = 0
    pop, chercher = p.heapq.heappop, p.chercher

    def retirer(file):
        nonlocal n_visites
        entree = pop(file)
        if sys._getframe(1).f_code.co_name == "_explorer_etats":
            *priorite, e, chemin, profondeur, final = entree
            terme = ["differe", final.borne] if isinstance(final, p.SuiteDifferee) else final
            x = [priorite, _etat(e), profondeur, terme]
            visites.update(json.dumps(x, sort_keys=True, ensure_ascii=False).encode() + b"\n")
            n_visites += 1
        return entree

    def rechercher(*a, **k):
        nonlocal n_plans
        r = chercher(*a, **k)
        x = [a[1], k.get("nom"), None if r is None else [r[0], r[1], _etat(r[2])]]
        plans.update(json.dumps(x, sort_keys=True, ensure_ascii=False).encode() + b"\n")
        n_plans += 1
        return r

    with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
            patch.object(p, "_IMPOSSIBLES", {}), patch.object(p, "VERIFIER", False), \
            patch.object(p.heapq, "heappop", retirer), patch.object(p, "chercher", rechercher), \
            p.diagnostics() as diagnostics:
        moteur = Moteur(m)
        lignes = moteur.executer(moteur.preparer(proposition("attendre")))
    recharge = recharger(m)
    assert m.data == recharge.data
    assert regarder(m) == regarder(recharge)
    assert scene_percue(m) == scene_percue(recharge)
    if scenario == 'auberge':
        # 202/228 : l'huile ne compense pas les seuls crochets. La proposition
        # à une pièce est refusée pour méfiance ; aucun outil n'est cédé.
        assert any(c['texte'] == "Lucien propose à Joss 1 pièce contre une part de la burette d'huile d'écurie (mefiance)."
                   for c in recharge.data['chronique'])
        assert recharge.objets['crochets_lucien']['lieu'] == 'lucien'
        from donjon.biens import valeur_capacites
        from donjon.echanges import valeur_proposition
        assert valeur_capacites(recharge, 'lucien', 'crochets_lucien') > valeur_proposition(
            recharge, 'lucien', {'type': 'part', 'objet': 'burette_huile'}, 'lucien', sans='crochets_lucien')
    historique = sans_indices_soupcon_passifs(recharge)
    # Les preuves de fin (175) et de possession (179) ne figurent pas dans
    # l'oracle ancien. Monde et rendus complets restent comparés après
    # recharge ci-dessus ; seuls ces savoirs nouveaux sortent de la projection.
    for e in [*historique["esprits"].values(), historique.get("connaissances_joueur", {})]:
        for sujet, attributs in list(e.get("croyances", {}).items()):
            attributs.pop("fin", None)
            if e is historique.get("connaissances_joueur"):
                attributs.pop("lieu", None)
            elif "lieu" in attributs:
                attributs["lieu"].pop("possession", None)
            if not attributs:
                del e["croyances"][sujet]
    if "connaissances_joueur" in historique and not any(historique["connaissances_joueur"].values()):
        del historique["connaissances_joueur"]
    for e in historique["esprits"].values():
        # 360 : provenance initiale uniquement ; le monde complet reste
        # comparé après recharge, avant cette projection pré-337.
        e.pop("faits_initiaux", None)
        # Le contrat 213 ajoute la provenance de l'intention à la sauvegarde.
        # Sa persistance est vérifiée dans test_contrat_engagement ; l'oracle
        # historique conserve ici les décisions, plans, monde et vues du joueur.
        e.pop("contrat_intention", None)
        # L'oracle antérieur au registre d'effort ne contient pas ce champ.
        # Un effort réellement retenu ne serait pas une migration vide.
        assert not e.get("attentes_bornees"), "La capture historique a changé de décisions"
        e.pop("attentes_bornees", None)
        assert e.pop('recours_services', []) == [], 'Une tentative de service a changé la capture'
        assert e.pop('recours_intermediaires', []) == [], 'Une commission a changé la capture'
        assert e.pop('service_en_cours', None) is None, 'Un projet de service a changé la capture'
    # 376/391 : le seul champ changé dans ces deux mondes est le fait sonore
    # du dernier journal. Restaurer son ancien texte doit retrouver exactement
    # l'empreinte historique : aucune autre donnée n'est écartée du contrôle.
    preuve = json.loads((DONNEES.parent / 'parite-391-etapes.json').read_text(encoding='utf-8'))[scenario]
    assert historique['journal'][96]['faits'] == preuve['faits_apres']
    ancien = copy.deepcopy(historique)
    ancien['journal'][96]['faits'] = preuve['faits_avant']
    assert _empreinte(_sans_ascendant_neutre(ancien)) == preuve['monde_avant']
    return {"visites": visites.hexdigest(), "n_visites": n_visites,
            "plans": plans.hexdigest(), "n_plans": n_plans,
            "diagnostics": _empreinte([{k: v for k, v in d.items() if k != "duree"} for d in diagnostics]),
            # 248 : retrouver le hash historique en retirant seulement le
            # sixième axe neutre, sans remplacer aucun hash attendu.
            "monde": _empreinte(_sans_ascendant_neutre(historique)), "lignes": _empreinte(lignes),
            "regarder": _empreinte(regarder(recharge)), "scene": _empreinte(scene_percue(recharge))}


class EtapesTests(unittest.TestCase):
    def test_projection_historique_refuse_un_ascendant_actif(self):
        for valeur in (1, True, [1, 0]):
            with self.subTest(valeur=valeur), self.assertRaisesRegex(AssertionError, 'non neutre'):
                _sans_ascendant_neutre({'relation': {'ascendant': valeur}})

    def test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges(self):
        attendu = json.loads((DONNEES / "etapes-attendues.json").read_text(encoding="utf-8"))
        calcul = json.loads((DONNEES.parent / "profondeurs-preuve/etapes-calcul.json").read_text(encoding="utf-8"))
        contacts = json.loads((DONNEES.parent / "contact-226-etapes.json").read_text(encoding="utf-8"))
        rendez_vous = json.loads((DONNEES.parent / "rendez-vous-230-etapes.json").read_text(encoding="utf-8"))
        pas = json.loads((DONNEES.parent / "pas-233-etapes.json").read_text(encoding="utf-8"))
        acoustique = json.loads((DONNEES.parent / 'parite-391-etapes.json').read_text(encoding='utf-8'))
        # Lot 191 : le registre d'audience change le monde sauvegardé ; dans
        # la mine, une parole supprimée change aussi les reprises du graphe
        # et les lignes. Les plans et les vues restent l'oracle historique.
        paroles = {
            "mine": {
                "visites": "9a5260767ab9a7fbdc7970b62060e9d04bf680685687e628a8d4880e8d1e0e51",
                "n_visites": 4956,
                "diagnostics": "827bb1e37ba176d398472b218b1505d4310ede27fcd2200cbcf064b1f2d0286f",
                "monde": "c7c8900af39bd1ccab5777a25164b9efe297d96c823794a05578bbc77388ecc1",
                "lignes": "37c42d6a8fd5ac7fe31193886396a2573881be8e5280b81c74de01f2cf4d73dd"},
            # Lot 211 : les localisations inconnues changent le parcours du
            # graphe (8 212 → 8 294 visites), sans changer plans ni monde/rendu.
            # Lot 221 : la question ajoute 48 visites ; mêmes plans, monde,
            # lignes et rendus complets après recharge.
            "auberge": {
                "visites": "86c65822867ed8b3aaa3d67c57741ec7e0fe0159277cd94336e38d38f2dd7937",
                "n_visites": 8342,
                "diagnostics": "c4bd5ec754384c1195966e279ccfd3a46f4edcd101576f652894ec08fae8181b",
                "monde": "f85db4952442efdfb10ab7797c96d21fb9d35c7f43c39d4cf063351ebb564969"}}
        for scenario in ("mine", "auberge"):
            with self.subTest(scenario=scenario):
                self.assertEqual(set(acoustique[scenario]['empreintes']), {'monde', 'lignes'})
                # Le lot 92 c réduit les reprises, donc les visites et diagnostics.
                # Plans, monde, lignes et rendus restent ceux de l'oracle historique.
                nouvelles_mesures = calcul[scenario]
                self.assertLessEqual(set(nouvelles_mesures), {"visites", "n_visites", "diagnostics"})
                # La capture historique mesure les étapes du planificateur,
                # sans la naissance A6 éprouvée séparément après recharge.
                from donjon import agendas
                with patch.object(agendas, "_naissances", return_value=None):
                    # 226 change le comportement : Odon cherche Josse pour
                    # manger, Anselme cherche Lucien pour le bois. Plans,
                    # monde et journal changent ; les deux vues du joueur
                    # gardent exactement leurs empreintes historiques.
                    self.assertEqual(set(contacts[scenario]),
                                     {"visites", "n_visites", "plans", "n_plans", "diagnostics", "monde", "lignes"})
                    # 230 : les rendez-vous tenus changent les contacts et
                    # recherches ; les deux vues gardent l'oracle historique.
                    self.assertLessEqual(set(rendez_vous.get(scenario, {})), set(contacts[scenario]))
                    # 195/233 : moins de rotations, plus de choix à l'ouïe.
                    # Captures 480–485 rejouées sur 01ce467 et sur le candidat :
                    # plans/visites/état interne changent, mais lignes et les
                    # deux vues historiques restent strictement identiques.
                    self.assertEqual(set(pas[scenario]),
                                     {"visites", "n_visites", "plans", "n_plans", "diagnostics", "monde"})
                    # Réancrage 228 explicite du monde d'auberge uniquement :
                    # crochets → pièce dans le refus et ses souvenirs entendus.
                    # Diff exhaustif archivé dans reprise/capture-differences.json.
                    compensation = ({'monde': '66e43f9693b962a30e3a48b4b9fc7b0af2436bc9d4d3448f37ca7ade18f2d2d7'}
                                    if scenario == 'auberge' else {})
                    # 244 : une flamme faible n'ouvre plus les acquisitions
                    # de combustible sans gain de capacité. Seule l'exploration
                    # change (20 632 → 8 573 visites), plans et monde conservés.
                    reserve = ({'visites': '727ad9bb04e40a5e2602b0e93032d4d337be6fe23c896d8cbe917c30fafb6a5b',
                                'n_visites': 8573,
                                'diagnostics': '713286253ce4161d93c4833e73e951671caacd67758398a206448edb605acadd'}
                               if scenario == 'auberge' else {})
                    # 320/e0be70d : seul le registre emissions_parole et ses
                    # liens bruits[].emission enrichissent le monde rechargé.
                    # Diff exhaustif et parent direct vert : rapport 334.
                    # Garder ce monde complet, sans exclure le nouveau registre
                    # ni modifier les oracles de visites, plans, lignes ou vues.
                    emissions = {'monde': {
                        # 332 : seuls registres et provenance des regards
                        # changent. Diff intégral des mondes dans groupe1-342 ;
                        # plans, visites, lignes et vues restent identiques.
                        'mine': 'f6fef42c0ff663398182fcece93c50df3ab43ad071b27a491194ee94f1e9bcd6',
                        'auberge': '52bb40f121653875af09faa5edd9b5c11654a4ec8c375d00bfd83535ae2636ee',
                    }[scenario]}
                    # 313 : les positions inconnues/incluses sont mesurées au
                    # contact commun. Comparaison eb15b5e : monde COMPLET,
                    # plans, lignes et deux vues rechargées identiques ; seules
                    # les visites changent (+40 mine, -48 auberge), avec leurs
                    # diagnostics. Ne pas recaler les empreintes de monde déjà
                    # rouges sur cette intégration (attribution-suite/).
                    contact_inconnu = {
                        'mine': {'visites': '381b569e7d5a4ec6b9071e96a2530d3f2665b5c7ff7545c9a1e4ac724b7a1e8a',
                                 'n_visites': 16349},
                        'auberge': {'visites': 'f87967ccef03c066d0c76604790559ffd87bba3c3a9a0bf0682e0432dc0c174a',
                                    'n_visites': 8525,
                                    'diagnostics': '0ac8422ae26c05775ec4d05db80943c9eacd60d9ec8ee6e6a7047ef9abc6e878'}}
                    self.assertLessEqual(set(contact_inconnu[scenario]),
                                         {'visites', 'n_visites', 'diagnostics'})
                    self.assertEqual(observer_capture(scenario), {**attendu[scenario], **nouvelles_mesures,
                                                                 **paroles[scenario], **contacts[scenario],
                                                                 **rendez_vous.get(scenario, {}), **pas[scenario],
                                                                 **compensation, **reserve, **contact_inconnu[scenario],
                                                                 **emissions, **acoustique[scenario]['empreintes']})

    def test_plusieurs_ajouts_egalite_differee_et_aucune_reconstruction_sans_resultat(self):
        e = p.Etat("s", (), {})
        a = e.apres(faits=[(("prepare",), True)])
        fin = a.apres(faits=[(("estimation",), True)])
        prefixe = [p._etape("prendre"), p._etape("ouvrir")]
        dernier = [{**p._etape("demander", contenu={"condition": {"objets": ["x", "y"]}}),
                    "suppose": True}]

        def suites(v, courant, vises, but):
            if courant == e:
                return [(0, 1, prefixe, a, 0, False, 0)]
            return [p.SuiteDifferee(1, lambda v: [(0, 1, dernier, fin, 0, False)], ()),
                    (0, 1, [p._etape("second")], fin, 0, False, 0)]

        for tenir in (False, True):
            v = SimpleNamespace(degat=0, menacees=set(), _devis_developpes=0, _devis_differes=0,
                                borne_rester=lambda s: 0, pression=lambda e: 0)
            visites = []
            pop = p.heapq.heappop
            def retirer(file):
                x = pop(file)
                visites.append((x[3], x[5], "differe" if isinstance(x[8], p.SuiteDifferee) else x[8]))
                return x
            with patch.object(p, "_suites", suites), \
                    patch.object(p.heapq, "heappop", retirer), \
                    patch.object(p, "_reconstruire_etapes", wraps=p._reconstruire_etapes) as reconstruire:
                r = p._explorer_etats(v, e, lambda v, e: False, {}, 8, 20, 0, tenir=tenir)[0]
                self.assertEqual(visites, [((0, 0), e, False), ((1, 0), a, False),
                                          ((2, 0), a, "differe"), ((2, 0), fin, True)])
                self.assertEqual(reconstruire.call_count, 1)
                self.assertEqual([x["operation"] for x in r[1]], ["prendre", "ouvrir", "demander"])
                self.assertEqual(p._couper([p._degeler_etape(x) for x in r[1]]), prefixe +
                                 [p._etape("demander", contenu={"condition": {"objets": ["x", "y"]}})])
                with self.assertRaises(TypeError):
                    r[1][-1]["contenu"]["condition"]["objets"][0] = "corruption"
                reconstruire.reset_mock()
                self.assertIsNone(p._explorer_etats(v, e, lambda v, e: False, {}, 8, 1, 0)[0])
                reconstruire.assert_not_called()
        # Le graphe lui-même ne peut plus altérer un résultat déjà gelé.
        prefixe[0]["operation"] = "corruption"
        dernier[0]["contenu"]["condition"]["objets"].clear()
        self.assertEqual(r[1][0]["operation"], "prendre")
        self.assertEqual(list(r[1][-1]["contenu"]["condition"]["objets"]), ["x", "y"])

    def test_memoire_isole_les_mutations_profondes_des_deux_appelants(self):
        m = relais()
        suites = p._suites

        def enrichir(*a, **k):
            resultat = suites(*a, **k)
            for s in resultat:
                if not isinstance(s, p.SuiteDifferee):
                    for x in s[2]:
                        x["contenu"] = {**x.get("contenu", {}), "trace": [{"objets": ["x"]}],
                                        "tuple": (1, [2])}
            return resultat

        with patch.object(p, "_MEMOIRE", {}), patch.object(p, "_GRAPHES", {}), \
                patch.object(p, "_IMPOSSIBLES", {}), patch.object(p, "_suites", enrichir), p.diagnostics() as ds:
            def chercher():
                return p.chercher(m, "brune", p.a_mange, memo="etapes", emplois=("manger",))
            premier = chercher()
            attendu = copy.deepcopy(premier[1])
            self.assertGreater(len(attendu), 2)
            for resultat in (premier, chercher()):
                resultat[1][0]["operation"] = "corruption"
                resultat[1][0]["contenu"]["trace"][0]["objets"].append("corruption")
                resultat[1][0]["contenu"]["tuple"][1].append(3)
                resultat[1].clear()
            self.assertEqual(chercher()[1], attendu)
            self.assertEqual([d["memoire"] for d in ds], [False, True, True])
            interne = next(iter(p._MEMOIRE.values()))[1][1]
            with self.assertRaises(TypeError):
                interne[0]["operation"] = "corruption"
