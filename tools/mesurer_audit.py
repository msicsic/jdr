"""Mesure hors ligne des rapports narratifs d'un banc --fil (tokenizer o200k_base).

Les jetons par champ sont des fragments JSON tokenisés séparément : ils ne
s'additionnent pas exactement au total fournisseur (ponctuation et frontières).
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon.narration import segments


def arguments(trace):
    brut = trace.get('brut') or []
    for item in brut if isinstance(brut, list) else brut.get('contenu', []):
        if item.get('type') == 'function_call':
            return json.loads(item['arguments'])
    return {}


def mesurer(fichiers, encoder):
    champs, inutilises, tailles, appels = Counter(), Counter(), [], []
    nsegments = exacts = 0
    for fichier in fichiers:
        partie = json.loads(Path(fichier).read_text(encoding='utf-8'))
        for tour in partie.get('tours', []):
            for trace in tour.get('fil', []):
                if trace.get('fonction') != 'auditer_narration':
                    continue
                faits = trace['entree']['faits']
                textes = list(faits.get('attestations', []))
                for cle in ('resultat_resolu', 'conversation_validee'):
                    bloc = faits.get(cle) or {}
                    textes.extend(bloc.get('faits', []))
                    if isinstance(bloc.get('issue'), str):
                        textes.append(bloc['issue'])
                retour = faits.get('retour_moteur') or {}
                if isinstance(retour.get('obstacle'), str):
                    textes.append(retour['obstacle'])
                catalogue = {s for texte in textes if isinstance(texte, str) for s in segments(texte)}
                for parole in faits.get('paroles_entendues', []):
                    if isinstance(parole, dict) and parole.get('texte'):
                        catalogue.add('« ' + parole['texte'] + ' »')
                passages = trace['entree']['segments']
                nsegments += len(passages)
                exacts += sum(s in catalogue for s in passages.values())
                rapport = arguments(trace).get('segments', {})
                lignes = rapport.values() if isinstance(rapport, dict) else rapport
                champs_appel = Counter()
                for ligne in lignes:
                    verdict = ligne.get('verdict')
                    for cle, valeur in ligne.items():
                        n = len(encoder.encode(json.dumps({cle: valeur}, ensure_ascii=False, separators=(',', ':'))))
                        champs[cle] += n
                        champs_appel[cle] += n
                        if ((cle in ('locuteur', 'citation', 'presentation') and verdict not in ('parole', 'engagement'))
                                or (cle == 'entites' and verdict not in ('ambiance', 'engagement'))
                                or (cle == 'motif' and verdict not in ('invention_protegee', 'contradictoire')
                                    and ligne.get('portee_mecanique') not in ('sans_fondement', 'contradictoire'))):
                            inutilises[cle] += n
                sortie = (trace.get('usage') or {}).get('output_tokens', 0)
                tailles.append(sortie)
                appels.append({'fichier': str(fichier), 'saisie': tour['saisie'],
                               'sortie': sortie, 'segments': len(passages),
                               'jetons_fragments_par_champ': dict(champs_appel)})
    return {'appels': appels, 'nombre_appels': len(appels), 'segments': nsegments,
            'segments_exacts': exacts, 'jetons_sortie': sum(tailles),
            'sortie_moyenne': statistics.mean(tailles) if tailles else 0,
            'sortie_mediane': statistics.median(tailles) if tailles else 0,
            'jetons_fragments_par_champ': dict(champs),
            'jetons_fragments_non_utilises_selon_verdict': dict(inutilises),
            'champs_jamais_lus': [],
            'tokenizer': 'o200k_base, fragments séparés, approximation du tokenizer fournisseur'}


if __name__ == '__main__':
    import tiktoken
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dossier', type=Path)
    p.add_argument('--sortie', type=Path, required=True)
    a = p.parse_args()
    mesure = mesurer(sorted(a.dossier.rglob('*.json')), tiktoken.get_encoding('o200k_base'))
    a.sortie.write_text(json.dumps(mesure, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in mesure.items() if k != 'appels'}, ensure_ascii=False, indent=2))
