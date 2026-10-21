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
from donjon.rendu import regarder, fiche, carte
from donjon.spatial import installer
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
        assert jeu.main(['--save', str(chemin), '--console', '--connexion', 'chatgpt',
                         '--model', 'gpt-6-luna', '--effort', 'medium', '--cases'], interface=interface) == 0
        recharge = Monde.charger(chemin)
        assert recharge.objets[cible]['lieu'] == 'joueur', interface.sorties
        dernier = recharge.data['conversation'][-1]['reponse']
        assert dernier in interface.deja_sauves
        etat = copy.deepcopy(recharge.data)
        reprise = Interface(['inventaire', 'regarder', 'quitter'], chemin)
        assert jeu.main(['--save', str(chemin), '--offline', '--console'], interface=reprise) == 0
        assert Monde.charger(chemin).data == etat
        assert recharge.objets[cible]['nom'].casefold() in '\n'.join(reprise.sorties).casefold()
        return {'cas': cas, 'cible': cible, 'lieu': 'joueur', 'recit_sauve_avant_affichage': True,
                'etat_identique_apres_reprise': True, 'sorties': interface.sorties,
                'sorties_apres_reprise': reprise.sorties, 'conversation': etat['conversation']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--max-appels', type=int, default=24)
    args = p.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=False)
    rapport = {'modele': 'gpt-6-luna', 'effort': 'medium', 'connexion': 'chatgpt',
               'ouvertures': 0, 'fermetures': 0, 'appels': [], 'parcours': []}

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
                'modele': payload['model'], 'effort': payload['reasoning']['effort'],
                'instructions_completes': bool(payload['instructions']),
                'entrees': len(payload['input']), 'sans_parent': True})
            self.socket.send(texte)

        def recv(self, timeout):
            texte = self.socket.recv(timeout=timeout)
            e = json.loads(texte)
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
                rapport['parcours'].append(parcours(cas))
        assert rapport['ouvertures'] == rapport['fermetures'] == len(CAS)
        assert all(a.get('terminal') == 'completed' for a in rapport['appels'])
        rapport['succes'] = True
    finally:
        (args.sortie / 'verification.json').write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: rapport[k] for k in ('succes', 'ouvertures', 'fermetures')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
