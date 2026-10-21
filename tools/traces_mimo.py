"""Capture sur disque de chaque appel physique MiMo, y compris les corrections."""
import copy
import json
from pathlib import Path


def sauver_json(chemin, valeur):
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(valeur, ensure_ascii=False, indent=2), encoding='utf-8')


class JournalMiMo:
    def __init__(self, dossier, maximum=300, erreur_budget=RuntimeError, contexte=lambda: {}):
        self.dossier = Path(dossier)
        self.appels = []
        self.maximum, self.erreur_budget = maximum, erreur_budget
        self.contexte = contexte

    def observateur(self):
        # Un fournisseur par partie : ses numéros locaux deviennent des identifiants globaux.
        courants = {}

        def noter(type_, numero, donnees):
            if type_ == 'debut':
                if len(self.appels) >= self.maximum:
                    raise self.erreur_budget('Budget maximal des appels physiques MiMo atteint.')
                index = len(self.appels) + 1
                nom = f'appels/{index:03d}-{donnees["fonction"]}'
                dossier = self.dossier / nom
                dossier.mkdir(parents=True, exist_ok=False)
                mesure = {'fonction': donnees['fonction'], 'essai': donnees['essai'],
                    'dossier_trace': nom, 'effort': 'none' if donnees['requete']['thinking']['type'] == 'disabled' else 'enabled'}
                mesure.update(copy.deepcopy(self.contexte()))
                self.appels.append(mesure)
                courants[numero] = (dossier, mesure)
                sauver_json(dossier / 'requete.json', donnees['requete'])
                q = json.loads(donnees['requete']['messages'][1]['content'])
                sauver_json(dossier / 'contexte-appel.json', q)
                (dossier / 'reponse.sse').touch()
            else:
                dossier, mesure = courants[numero]
                if type_ == 'octets':
                    with (dossier / 'reponse.sse').open('ab') as f:
                        f.write(donnees)
                        f.flush()
                elif type_ == 'evenement':
                    with (dossier / 'evenements.jsonl').open('a', encoding='utf-8') as f:
                        f.write(json.dumps(donnees, ensure_ascii=False) + '\n')
                elif type_ == 'fin':
                    mesure.update(copy.deepcopy(donnees['mesures']))
                    mesure.update(usage=donnees.get('usage'), schema_valide=donnees.get('schema_valide', False),
                        modele_retourne=donnees.get('modele_retourne'))
                    for cle in ('diagnostic_validation', 'diagnostic_flux', 'erreur_transport', 'statut_http'):
                        if cle in donnees:
                            mesure[cle] = copy.deepcopy(donnees[cle])
                            mesure['erreur_adaptateur'] = {'type': cle, 'message': str(donnees[cle])}
                    if not mesure['schema_valide'] and 'erreur_adaptateur' not in mesure:
                        mesure['erreur_adaptateur'] = {'type': 'sortie_non_validee',
                            'message': 'Réponse non admise : terminal absent, tronqué ou invalide.'}
                    sauver_json(dossier / 'reponse-interpretee.json', {'output': donnees['contenu'], 'usage': donnees.get('usage'),
                        'status': 'completed' if donnees.get('done_recu') and donnees.get('stop_reason') == 'stop' else 'incomplete'})
                    sauver_json(dossier / 'trace-complete.json', donnees)
                    if donnees.get('schema_valide'):
                        sauver_json(dossier / 'proposition-remise-au-jeu.json', donnees['arguments'])
                    sauver_json(dossier / 'mesure.json', mesure)
                    sauver_json(self.dossier / 'mesures.json', {'appels': self.appels})
        return noter
