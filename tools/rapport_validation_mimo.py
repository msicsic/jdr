"""Indexer une campagne MiMo terminée et ses captures intégrales, sans appel réseau."""
import argparse
import html
import json
from pathlib import Path
import statistics

from rapport_fil import ecrire


def lire(chemin):
    return json.loads(chemin.read_text(encoding='utf-8'))


def distribution(valeurs):
    valeurs = sorted(v for v in valeurs if v is not None)
    if not valeurs:
        return None
    return {'n': len(valeurs), 'mediane': statistics.median(valeurs),
            'moyenne': statistics.mean(valeurs), 'min': valeurs[0], 'max': valeurs[-1]}


def duree(mesure, precision=3):
    return f'{mesure["mediane"]:.{precision}f} s' if mesure else '—'


def produire(racine, observations=None):
    rapport = lire(racine / 'rapport.json')
    appels = rapport['appels']
    metriques = {'modele': rapport['modele'], 'effort': rapport['effort'],
                 'appels': len(appels), 'tours_mj': 0, 'tours_avec_erreur': 0,
                 'schema_valide': sum(bool(a.get('schema_valide')) for a in appels),
                 'erreurs_transport_ou_schema': sum(bool(a.get('erreur_adaptateur')) for a in appels),
                 'ttft_s': distribution(a.get('ttft_s') for a in appels),
                 'reponse_complete_s': distribution(a.get('complet_s') for a in appels),
                 'tokens_reflexion': sum((a.get('usage') or {}).get('completion_tokens_details', {}).get('reasoning_tokens', 0) for a in appels),
                 'reponses_avec_reflexion_visible': sum(a.get('premiere_reflexion_s') is not None for a in appels),
                 'narrations_resultat': len(rapport.get('narrations', [])),
                 'narrations_resultat_en_erreur': sum('erreur' in n for n in rapport.get('narrations', [])),
                 'gardes_numeriques_declenchees': sum(bool(g['nombres_refuses']) for g in rapport.get('gardes_numeriques', [])),
                 'parties': [], 'liaisons_tours_appels': [],
                 'observations_manuelles': lire(observations) if observations else []}
    liens_parties, lignes_appels = [], []
    for resume in rapport['parties']:
        nom = resume['script']
        chemin = racine / 'parties' / (nom + '.json')
        partie = lire(chemin)
        ecrire(chemin)
        identifiants = partie['appels_transport']
        transports = [appels[i - 1] for i in identifiants]
        tours = [t for t in partie['tours'] if t['appels']]
        assert sum(len(t['appels_transport']) if 'appels_transport' in t else t['appels'] for t in tours) == len(identifiants)
        position = 0
        for num, tour in enumerate(partie['tours'], 1):
            if not tour['appels']:
                continue
            indices = tour.get('appels_transport', identifiants[position:position + tour['appels']])
            position += tour['appels']
            metriques['liaisons_tours_appels'].append({'script': nom, 'tour': num, 'saisie': tour['saisie'], 'appels': indices})
        affichages = lire(racine / 'parties' / nom / 'affichages-sauves.json')
        mesure = {**resume, 'ttft_s': distribution(a.get('ttft_s') for a in transports),
                  'duree_tour_s': distribution(t['secondes'] for t in tours),
                  'reprise': {k: v for k, v in partie['reprise'].items() if k != 'tours'},
                  'affichages_constates_dans_sauvegarde': len(affichages)}
        metriques['parties'].append(mesure)
        metriques['tours_mj'] += resume['tours_mj']
        metriques['tours_avec_erreur'] += resume['tours_avec_erreur']
        liens_parties.append(f'<tr><td><a href="parties/{html.escape(nom)}.html">{html.escape(nom)}</a></td>'
                            f'<td>{resume["tours_mj"]}</td><td>{resume["appels"]}</td><td>{resume["tours_avec_erreur"]}</td>'
                            f'<td>{duree(mesure["duree_tour_s"], 2)}</td>'
                            f'<td><a href="parties/{html.escape(nom)}/final.json">État final</a> · '
                            f'<a href="parties/{html.escape(nom)}/reprise.json">Après reprise</a></td></tr>')
    assert sum(p['appels'] for p in metriques['parties']) == len(appels)
    for num, appel in enumerate(appels, 1):
        dossier = 'transport/' + appel['dossier_trace']
        erreur = (appel.get('erreur_adaptateur') or {}).get('message', '')
        liens = []
        for nom, titre in [('requete.json', 'Requête complète'), ('reponse.sse', 'SSE brut'),
                           ('evenements.jsonl', 'Événements horodatés'), ('reponse-interpretee.json', 'Réponse complète'),
                           ('proposition-remise-au-jeu.json', 'Proposition validée'), ('mesure.json', 'Mesure')]:
            if (racine / dossier / nom).exists():
                liens.append(f'<a href="{dossier}/{nom}">{titre}</a>')
        ttft = appel.get('ttft_s')
        lignes_appels.append(f'<tr><td>{num}</td><td>{html.escape(appel["fonction"])}</td>'
                             f'<td>{ttft:.3f} s</td><td>{" · ".join(liens)}</td>'
                             f'<td>{html.escape(erreur)}</td></tr>' if ttft is not None else
                             f'<tr><td>{num}</td><td>{html.escape(appel["fonction"])}</td><td>—</td>'
                             f'<td>{" · ".join(liens)}</td><td>{html.escape(erreur)}</td></tr>')
    (racine / 'metriques.json').write_text(json.dumps(metriques, ensure_ascii=False, indent=2), encoding='utf-8')
    observations_html = ''.join('<li>' + html.escape(o['constat']) + '</li>' for o in metriques['observations_manuelles'])
    page = f'''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Validation MiMo — parties réelles</title>
<style>body{{font:16px/1.5 system-ui;max-width:1500px;margin:40px auto;padding:0 24px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;text-align:left;vertical-align:top}}a{{color:#165c9e}}td:last-child{{overflow-wrap:anywhere}}h2{{margin-top:2em}}</style>
<h1>MiMo v2.6 Flash — banc réel du jeu</h1>
<p>Réflexion : {html.escape(rapport['effort'])}, API Xiaomi, JSON natif strict. IPv4 : {rapport['ipv4']}.
Relances de format autorisées : {rapport.get('relances_format', 0)}. Base du jeu : {html.escape(rapport['base_jeu'])}.
Scripts conservés dans les dossiers de parties, contrôle moteur conservé, comparaison désactivée.
Une passe : ce résultat ne mesure pas une fiabilité générale.</p>
<p>{metriques['tours_mj']} tours MJ, {len(appels)} appels, {metriques['tours_avec_erreur']} tours avec erreur.
TTFT médian : {duree(metriques['ttft_s'])} ; réponse complète médiane : {duree(metriques['reponse_complete_s'])} par appel.
Le TTFT part de l’envoi de la requête et attend le premier contenu JSON non vide ; il ne mesure ni le premier octet SSE ni la réponse affichée au joueur.</p>
<p>La narration et ses audits sont tous effectués par MiMo. Un verdict favorable de son propre audit ne prouve pas la cohérence factuelle.</p>
<ul>{observations_html}</ul>
<p><a href="metriques.json">Mesures et correspondance tour → appels</a> · <a href="rapport.json">Rapport complet</a></p>
<h2>Parties et texte affiché</h2><table><tr><th>Script</th><th>Tours MJ</th><th>Appels</th><th>Tours avec erreur</th><th>Durée médiane par tour</th><th>Sauvegardes</th></tr>{''.join(liens_parties)}</table>
<p>Chaque rapport de partie donne la saisie, le texte affiché, les instructions réelles, les réponses intégrales et les validations.
Les dossiers de parties conservent aussi l’état après chaque tour. Les corrections de format, lorsqu’elles sont autorisées,
comptent comme des appels physiques distincts ; chaque sortie reçue reste conservée.</p>
<h2>Appels bruts, sans troncature</h2><table><tr><th>N°</th><th>Fonction</th><th>TTFT</th><th>Fichiers</th><th>Erreur</th></tr>{''.join(lignes_appels)}</table></html>'''
    (racine / 'index.html').write_text(page, encoding='utf-8')
    return metriques


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('campagne', type=Path)
    p.add_argument('--observations', type=Path)
    args = p.parse_args()
    produire(args.campagne, args.observations)
