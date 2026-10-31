"""S1j (première partie) : dits, audiences et ancrage initial par leur porte."""
import ast
import copy
import json
from pathlib import Path
import unittest

from donjon import memoire, pnj, social
from donjon.emissions import lire as emissions
from donjon.esprits import lire, memoriser
from donjon.monde import Monde
from donjon.rendu import regarder
from donjon.scene import scene_percue
from donjon.temps import ecouler
from tests.test_deja_entendu import assemblee, dire
from tests.test_memoire_localisation import acces_croyances, RACINE
from tests import test_memoire_socle
from tests.test_tensions import recharger


REGISTRES = {'faits_dits', 'faits_initiaux'}


def acces_dits(source):
    """Alias locaux du contrôle S1f, complétés des écritures de clés racines.

    Les deux créations de schéma sont admises par leur expression exacte
    dans le test d'inventaire, sans exemption pour les autres dictionnaires.
    """
    acces = acces_croyances(source, registres=REGISTRES)
    arbre = ast.parse(source)
    parents = {c: n for n in ast.walk(arbre) for c in ast.iter_child_nodes(n)}

    def fonction(n):
        while n in parents:
            n = parents[n]
            if isinstance(n, ast.FunctionDef):
                return n.name
        return '<module>'

    cles = {(fonction(n), t.id): n.value.value
            for n in ast.walk(arbre) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
            and isinstance(n.value.value, str) for t in n.targets if isinstance(t, ast.Name)}

    def cle(n, f):
        return n.value if isinstance(n, ast.Constant) else cles.get((f, n.id)) if isinstance(n, ast.Name) else None

    for n in ast.walk(arbre):
        f = fonction(n)
        if isinstance(n, ast.Dict) and any(cle(k, f) in REGISTRES for k in n.keys):
            acces[f, ast.unparse(n)] += 1
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'dict':
            if any(k.arg in REGISTRES for k in n.keywords):
                acces[f, ast.unparse(n)] += 1
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in ('pop', '__setitem__', '__delitem__') and n.args and cle(n.args[0], f) in REGISTRES:
                acces[f, ast.unparse(n)] += 1
            if n.func.attr == 'update':
                valeurs = [k.arg for k in n.keywords]
                for a in [*n.args, *(k.value for k in n.keywords if k.arg is None)]:
                    if isinstance(a, ast.Dict):
                        valeurs.extend(cle(k, f) for k in a.keys)
                if any(v in REGISTRES for v in valeurs):
                    acces[f, ast.unparse(n)] += 1
    return acces


class ParolesTests(unittest.TestCase):
    def test_inventaire_ferme_et_contre_epreuves(self):
        fixture = json.loads((RACINE / 'tests/fixtures/acces_memoire_s1a.json').read_text(encoding='utf-8'))
        mesures = {}
        for p in [*RACINE.glob('*.py'), *(RACINE / 'donjon').rglob('*.py'), *(RACINE / 'tools').rglob('*.py')]:
            relatif = p.relative_to(RACINE).as_posix()
            if relatif == 'donjon/memoire.py':
                continue
            acces = acces_dits(p.read_text(encoding='utf-8-sig'))
            if acces:
                mesures[relatif] = {f'{f}/{e}': n for (f, e), n in sorted(acces.items())}
        # Même frontière de schéma que S1a ; aucune création brute supplémentaire.
        for f, e in (('<module>', test_memoire_socle.AccesTests.schema_champs()),
                     ('esprit', "{'croyances': {}, 'memoire': [], 'faits_dits': {}}")):
            self.assertEqual(mesures['donjon/esprits.py'].pop(f'{f}/{e}'), 1)
        mesures = {f: a for f, a in mesures.items() if a}
        self.assertEqual(mesures, fixture['dits_restants_s1j'])
        self.assertEqual(mesures, {})
        for registre in REGISTRES:
            for source in (
                f'e["{registre}"]', f'e.get("{registre}")', f'e.setdefault("{registre}", {{}})',
                f'cle = "{registre}"; stock = e[cle]; alias = stock; alias[s]["valeur"] = 8',
                f'stock = e["{registre}"]; prendre = stock.get; prendre(s)',
                f'for fait in e["{registre}"].values():\n fait.clear()',
                f'def fuite(e):\n stock = e["{registre}"]; return stock',
                f'del e["{registre}"]', f'e.pop("{registre}")',
                f'e.update({registre}={{}})', f'e.update(**{{"{registre}": stock}})',
                f'e.__setitem__("{registre}", {{}})',
                f'e = {{"{registre}": stock}}', f'e = dict({registre}=stock)',
            ):
                with self.subTest(source=source):
                    self.assertTrue(acces_dits(source))

    def test_vues_pures_copies_imbriquees_et_admission_copiee(self):
        m = assemblee()
        noyau = {'type': 'affirmation', 'sujet': 'vivres', 'attribut': 'etat',
                 'valeur': {'disponible': False}}
        for qui in ('ilse', 'joueur'):
            social.retenir_dit(m, qui, 'marchand', noyau)
            social._retenir_audience(m, [(qui, 'marchand', noyau)])
            memoriser(m, qui, dict(type='parole', locuteur='ilse', a=['marchand'],
                                   texte='Les vivres sont épuisés.', cites=['vivres']))
        avant = copy.deepcopy(m.data)
        for qui in ('absent', 'ilse', 'joueur'):
            dits = memoire.dits_retenus(m, qui)
            for fait in dits.values():
                fait['dit_a'].clear()
                fait['entendu_a']['marchand'].clear()
            dits.clear()
            memoire.faits_initiaux(m, qui).clear()
            for parole in memoire.paroles_retenues(m, qui):
                parole['a'].clear()
                parole['cites'].clear()
            social.deja_dit(m, qui, 'marchand', noyau)
            social.transmission_attestee(m, qui, 'marchand', noyau)
        self.assertEqual(m.data, avant)
        self.assertEqual(recharger(m).data, avant)
        # Une valeur composée est copiée à l'entrée et dans chaque destination.
        compose = dict(type='affirmation', sujet='vivres', attribut='lieu',
                       valeur='antichambre', details={'possession': {'porteur': 'brune'}})
        social.retenir_dit(m, 'ilse', 'marchand', compose)
        avant = copy.deepcopy(m.data)
        compose['details']['possession']['porteur'] = 'aubin'
        for fait in memoire.dits_retenus(m, 'ilse').values():
            if isinstance(fait['valeur'], dict):
                fait['valeur']['possession']['porteur'] = 'aubin'
        self.assertEqual(m.data, avant)
        initiaux = memoire.faits_initiaux(m, 'ilse')
        for valeur in initiaux.values():
            if isinstance(valeur, dict):
                valeur.clear()
        self.assertEqual(m.data, avant)

    def test_saturation_n_atteste_pas_une_transmission_et_audience_sans_adoption(self):
        m = assemblee()
        for n in range(social.DITS_MAX):
            social.retenir_dit(m, 'ilse', 'marchand', dict(type='affirmation', sujet=f'objet{n}',
                                                         attribut='lieu', valeur=None))
        nouveau = dict(type='affirmation', sujet='nouveau', attribut='lieu', valeur=None)
        avant = memoire.dits_retenus(m, 'ilse')
        social.retenir_dit(m, 'ilse', 'marchand', nouveau)
        social._retenir_audience(m, [('ilse', 'brune', nouveau)])
        m = recharger(m)
        self.assertEqual(memoire.dits_retenus(m, 'ilse'), avant)
        self.assertTrue(social.deja_dit(m, 'ilse', 'marchand', nouveau))
        self.assertFalse(social.transmission_attestee(m, 'ilse', 'marchand', nouveau))
        avant = copy.deepcopy(m.data)
        social._retenir_audience(m, [('brune', 'marchand', nouveau)])
        self.assertTrue(social.transmission_attestee(m, 'brune', 'marchand', nouveau))
        self.assertEqual(memoire.faits_connus(m, 'brune'), avant['esprits']['brune']['croyances'])

    def test_schema_et_migration_historique_sans_reapprentissage(self):
        m = assemblee()
        noyau = dict(type='affirmation', sujet='vivres', attribut='etat', valeur={'disponible': False})
        cle, valeur = social.faits_dits(noyau)[0]
        lire(m, 'ilse')['faits_dits'][cle] = dict(valeur=valeur, dit_a=['marchand', 'aubin'])
        m = recharger(Monde(copy.deepcopy(m.data)))
        self.assertEqual(memoire.dits_retenus(m, 'ilse')[cle]['dit_a'], dict(marchand=False, aubin=False))
        self.assertEqual(recharger(m).data, m.data)
        for champ, valeur in (('faits_dits', {cle: dict(valeur=False, dit_a=['marchand'])}),
                               ('faits_initiaux', {1: True})):
            corrompu = m.copier()
            lire(corrompu, 'ilse')[champ] = valeur
            with self.assertRaises(AssertionError):
                memoire.verifier_dits(corrompu, 'ilse')

    def test_capture_mine3_et_audience_relais_chaine_complete(self):
        historique = Monde.charger(Path(__file__).parent / 'data/mine3-josse-deja-dit.json')
        autre = assemblee()
        noyau = dict(type='constat', objet='vivres', attribut='etat',
                     valeur={'disponible': False}, observe=autre.data['minutes'])
        dire(autre, noyau)
        self.assertTrue(any(p['locuteur'] == 'ilse' for p in emissions(autre)))
        self.assertTrue(any(p.get('locuteur') == 'ilse' for p in memoire.paroles_retenues(autre, 'brune')))
        self.assertTrue(social.transmission_attestee(autre, 'brune', 'marchand', noyau))
        self.assertFalse(social.transmission_attestee(autre, 'brune', 'aubin', noyau))
        for initial in (historique, autre):
            resultats = []
            for tranches in ((1200,), (150,) * 8):
                m, lignes = recharger(initial), []
                for dt in tranches:
                    pnj.avancer(m, ecouler(m, dt), lignes, dt)
                    m = recharger(m)
                public = regarder(m), scene_percue(m), copy.deepcopy(emissions(m))
                recharge = recharger(m)
                self.assertEqual(recharge.data, m.data)
                self.assertEqual((regarder(recharge), scene_percue(recharge), emissions(recharge)), public)
                if initial is historique:
                    self.assertFalse(any('Josse dit à Lucien que Odon semble guetter' in c['texte']
                                         for c in m.data['chronique']))
                resultats.append((copy.deepcopy(m.data), json.dumps(m.data), lignes, public))
            self.assertEqual(*resultats)


if __name__ == '__main__':
    unittest.main()
