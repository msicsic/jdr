"""Deux parties réelles : WebSocket du jeu, état, affichage, sauvegarde et reprise."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jeu
from donjon.atelier import nouveau_atelier
from donjon.monde import Monde, nouveau_monde
from donjon.moteur import Moteur
from donjon.narration import rendre_resultat
from donjon.rendu import regarder, fiche, carte
from donjon.spatial import installer
from tests.perception_support import apres_regarder
from donjon.transport_openai import ouvrir_websocket

CAS = {'crypte': (nouveau_monde, 'cle'), 'atelier': (nouveau_atelier, 'ficelle')}


class Interface:
    def __init__(self, saisies, chemin):
        self.saisies, self.chemin = list(saisies), chemin
        self.sorties, self.deja_sauves = [], []

    def lire(self, *_):
        return self.saisies.pop(0) if self.saisies else 'quitter'

    def ecrire(self, *valeurs, **_):
        texte = ' '.join(str(v) for v in valeurs)
        self.sorties.append(texte)
        m = Monde.charger(self.chemin)
        if any(e['reponse'] == texte for e in m.data['conversation']):
            self.deja_sauves.append(texte)

    def montrer(self, vue):
        if vue in ('scene', 'fiche', 'carte'):
            self.sorties.append({'scene': regarder, 'fiche': fiche, 'carte': carte}[vue](Monde.charger(self.chemin)))

    def rafraichir(self, *_):
        pass

    def comparaison(self, *_):
        raise AssertionError('La comparaison doit rester désactivée')


def fixture(cas):
    creer, cible = CAS[cas]
    monde = creer()
    installer(monde)
    x, y = monde.objets[cible]['position']
    monde.joueur.update(position=[x - 1, y], orientation='est')
    monde.verifier()
    return monde, cible


def parcours(cas):
    with tempfile.TemporaryDirectory() as dossier:
        chemin = Path(dossier) / 'partie.json'
        monde, cible = fixture(cas)
        monde.sauver(chemin)
        demande = 'mj Je prends ' + ('la clé du veilleur.' if cible == 'cle' else 'la bobine de ficelle solide.')
        interface = Interface([demande, 'quitter'], chemin)
        resultats, executer = [], Moteur.executer
        def execution(moteur, *a, **kw):
            resultat = executer(moteur, *a, **kw)
            resultats.append(rendre_resultat(resultat))
            return resultat
        with patch.object(Moteur, 'executer', new=execution):
            assert jeu.main(['--save', str(chemin), '--console', '--connexion', 'chatgpt',
                             '--model', 'gpt-6-luna', '--effort', 'medium', '--cases'], interface=interface) == 0
        recharge = Monde.charger(chemin)
        assert recharge.objets[cible]['lieu'] == 'joueur', interface.sorties
        dernier = recharge.data['conversation'][-1]['reponse']
        compris = recharge.data['conversation'][-1]['compris']
        assert compris.startswith('Compris :'), compris
        assert len(resultats) == 1 and dernier == resultats[0] + '\n' + compris, (resultats, dernier)
        assert recharge.data['conversation'][-1]['nature'] == 'resultat_moteur'
        assert dernier in interface.deja_sauves
        etat = copy.deepcopy(recharge.data)
        vues = (regarder(recharge), fiche(recharge), carte(recharge))
        reprise = Interface(['inventaire', 'regarder', 'quitter'], chemin)
        assert jeu.main(['--save', str(chemin), '--offline', '--console'], interface=reprise) == 0
        # G5 / rapport 323 : regarder ajoute son résultat, sans nouvel acte.
        assert Monde.charger(chemin).data == apres_regarder(etat)
        assert (regarder(Monde.charger(chemin)), fiche(Monde.charger(chemin)),
                carte(Monde.charger(chemin))) == vues
        assert recharge.objets[cible]['nom'].casefold() in '\n'.join(reprise.sorties).casefold()
        # Une exécution peut être un plan simple ou composé : compter les commits moteur.
        executions = len(etat['journal']) - len(monde.data['journal'])
        assert executions == 1
        return {'cas': cas, 'cible': cible, 'lieu': 'joueur', 'recit_sauve_avant_affichage': True,
                'resultat_moteur': dernier,
                'executions_action': executions,
                'actions_journal': etat['journal'][len(monde.data['journal']):],
                'etat_identique_apres_reprise': True, 'sorties': interface.sorties,
                'sorties_apres_reprise': reprise.sorties, 'conversation': etat['conversation']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--max-appels', type=int, default=24)
    p.add_argument('--simuler-coupure', action='store_true',
                   help='Couper volontairement une réponse réelle par partie avant son terminal')
    args = p.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=False)
    rapport = {'modele': 'gpt-6-luna', 'effort': 'medium', 'connexion': 'chatgpt',
               'ouvertures': 0, 'fermetures': 0, 'appels': [], 'parcours': [],
               'coupures_simulees': 0, 'simulation_coupure': args.simuler_coupure}
    cas_courant, coupe_dans_partie = None, False

    class Observer:
        def __init__(self, socket):
            self.socket = socket
            self.fermee = False

        @property
        def close_code(self):
            return self.socket.close_code

        def send(self, texte):
            if len(rapport['appels']) >= args.max_appels:
                raise RuntimeError('Budget de vérification atteint')
            payload = json.loads(texte)
            for interdit in ('previous_response_id', 'stream_id', 'conversation', 'stream'):
                assert interdit not in payload
            rapport['appels'].append({'fonction': payload['tools'][0]['tools'][0]['name'],
                'cas': cas_courant,
                'modele': payload['model'], 'effort': payload['reasoning']['effort'],
                'instructions_completes': bool(payload['instructions']),
                'entrees': len(payload['input']), 'sans_parent': True})
            self.socket.send(texte)

        def recv(self, timeout):
            nonlocal coupe_dans_partie
            texte = self.socket.recv(timeout=timeout)
            e = json.loads(texte)
            if args.simuler_coupure and not coupe_dans_partie and e.get('type') == 'response.output_item.done':
                coupe_dans_partie = True
                rapport['coupures_simulees'] += 1
                rapport['appels'][-1]['coupure_simulee'] = True
                self.close()
                raise OSError('Coupure volontaire de vérification avant le terminal')
            if e.get('type') == 'response.completed':
                rapport['appels'][-1].update(terminal='completed', usage=e['response'].get('usage'))
            return texte

        def close(self):
            if not self.fermee:
                rapport['fermetures'] += 1
                self.fermee = True
            self.socket.close()

    def ouvrir(*a):
        socket = ouvrir_websocket(*a)
        rapport['ouvertures'] += 1
        return Observer(socket)

    try:
        with patch('donjon.transport_openai.ouvrir_websocket', side_effect=ouvrir):
            for cas in CAS:
                cas_courant, coupe_dans_partie = cas, False
                rapport['parcours'].append(parcours(cas))
        assert rapport['ouvertures'] == rapport['fermetures'] == len(CAS) + rapport['coupures_simulees']
        assert all(a.get('terminal') == 'completed' or a.get('coupure_simulee') for a in rapport['appels'])
        rapport['succes'] = True
    finally:
        (args.sortie / 'verification.json').write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: rapport[k] for k in ('succes', 'ouvertures', 'fermetures')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
