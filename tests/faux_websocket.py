"""Serveur Responses local pour exercer le vrai transport et le vrai parseur."""
import copy
import json


class FauxWebSocket:
    def __init__(self, repondre):
        self.repondre = repondre
        self.envois, self.evenements = [], []
        self.close_code = None
        self.fermetures = 0

    def send(self, donnees):
        if self.close_code is not None:
            raise OSError('fermée')
        p = json.loads(donnees)
        self.envois.append(copy.deepcopy(p))
        r = self.repondre(p)
        if isinstance(r, list):
            self.evenements.extend(r)
            return
        r = copy.deepcopy(r)
        r.setdefault('id', 'r' + str(len(self.envois)))
        self.evenements.extend([
            {'type': 'response.created', 'response': {'id': r['id']}},
            *[{'type': 'response.output_item.done', 'response_id': r['id'], 'output_index': i, 'item': x}
              for i, x in enumerate(r.get('output', []))],
            {'type': 'response.completed', 'response': {**r, 'output': []}}])

    def recv(self, timeout):
        assert timeout > 0
        if not self.evenements:
            raise OSError('coupure simulée')
        return json.dumps(self.evenements.pop(0))

    def close(self):
        self.close_code = 1000
        self.fermetures += 1


def resultat(payload, arguments):
    outil = payload['tools'][0]
    if outil['type'] == 'namespace':
        outil = outil['tools'][0]
    return {'status': 'completed', 'output': [{'type': 'function_call', 'name': outil['name'],
            'namespace': 'donjon', 'arguments': json.dumps(arguments)}]}
