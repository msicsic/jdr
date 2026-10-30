"""Prépare une passe Luna E6 sur copies isolées, sans sauvegarde utilisateur."""
import argparse
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path[:] = [x for x in sys.path if Path(x or '.').resolve() != BASE / 'tools']
sys.path.insert(0, str(BASE))
from tests.test_accords_publics import situation
from tests.test_accord_libre_date import phrase


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sortie', type=Path, required=True)
    args = p.parse_args()
    dossier = args.sortie.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    scripts = []
    for tache in (False, True):
        m, d = situation(tache)
        nom = 'verrou' if tache else 'huile'
        source = dossier / (nom + '-source.json')
        m.sauver(source)
        s = phrase(d)
        cas = {'accepter': [s, 'tenter'], 'annuler': [s, 'annuler'],
               'paiement-futur': [s + ', mais je ne te paierai que plus tard'],
               'maintien': [s + ' et tu dois maintenir cet état jusqu’à mon retour'],
               'alternative': [s + ' ou me donner six pièces à la place'],
               'pret-date': [s + ' et me prêter ta lampe pour ces dix minutes'],
               'demain': [s.replace('dans dix minutes', 'demain')]}
        for cas_nom, tours in cas.items():
            script = dossier / f'e6-{nom}-{cas_nom}.json'
            script.write_text(json.dumps({'scenario': 'auberge', 'seed': 1985,
                'sauvegarde': str(source), 'tours': tours}, ensure_ascii=False, indent=2), encoding='utf-8')
            scripts.append(script)
    # Pas de seconde passe ni de référence : uniquement les cas du lot.
    commande = ("$env:SEUIL_AUTH='C:\\Users\\msics\\donjon\\.seuil-auth'; "
                "& 'C:\\Users\\msics\\donjon\\.venv\\Scripts\\python.exe' "
                f"'{BASE / 'tools' / 'banc_parties.py'}' "
                + ' '.join("'" + str(x) + "'" for x in scripts)
                + f" --connexion chatgpt --max-appels 160 --etiquette e6-363 --fil --sortie '{dossier / 'luna'}'")
    (dossier / 'luna-a-jouer.txt').write_text(commande + '\n', encoding='utf-8')
    print(dossier / 'luna-a-jouer.txt')


if __name__ == '__main__':
    main()
