"""Brancher le transport MiMo sur le banc existant, sans modifier ses scripts ni le jeu."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / 'tools'))
import banc_parties as banc
import jeu
from donjon.monde import Monde
from donjon.mj import MJ
from tools.traces_mimo import JournalMiMo, sauver_json
from donjon.config import MODELE_MIMO as MODELE


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('scripts', nargs='*', type=Path,
                   default=[BASE / 'tests/data/bancs' / (n + '.json') for n in ('relais', 'crypte', 'atelier', 'echanges')])
    p.add_argument('--cle-fichier', type=Path)
    p.add_argument('--sortie', type=Path, required=True)
    p.add_argument('--max-appels', type=int, default=300)
    p.add_argument('--offline', action='store_true')
    p.add_argument('--relances-format', type=int, choices=(0, 1), default=1)
    p.add_argument('--effort', choices=('none', 'low', 'medium', 'high'), default='none')
    p.add_argument('--ipv6-autorise', action='store_true', help='sinon IPv4 limité à la connexion Xiaomi')
    args = p.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    cle = 'hors-ligne'
    if not args.offline:
        cle = os.environ.get('MIMO_API_KEY') or os.environ.get('XIAOMI_API_KEY')
        if args.cle_fichier:
            candidates = [l.strip() for l in args.cle_fichier.read_text(encoding='utf-8-sig').splitlines()
                          if l.strip().startswith('sk-') and not any(c.isspace() for c in l.strip())]
            if len(candidates) != 1:
                p.error('Une clé Xiaomi unique est attendue dans le fichier local')
            cle = candidates[0]
        if not cle:
            p.error('MIMO_API_KEY ou --cle-fichier requis')
        from donjon.fournisseurs.mimo import MiMo
        MiMo(cle, relances_format=args.relances_format)  # Vérifier les dépendances avant la partie.
    args.sortie.mkdir(parents=True, exist_ok=False)
    transport = args.sortie / 'transport'
    transport.mkdir()
    (args.sortie / 'parties').mkdir()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=BASE, text=True).strip()
    rapport = {'modele': MODELE, 'effort': args.effort, 'api': 'JSON natif strict', 'ipv4': not args.ipv6_autorise,
               'relances_format': args.relances_format, 'offline': args.offline, 'base_jeu': revision, 'max_appels': args.max_appels,
               'appels': [], 'controles': [], 'parties': [], 'gardes_numeriques': []}
    courant = {}
    journal = JournalMiMo(transport, args.max_appels, banc.BudgetEpuise, contexte=lambda: courant)
    rapport['appels'] = journal.appels
    compteur = banc.Compteur(args.max_appels, fil=True, effort=args.effort)
    compteur.traces = rapport['controles']

    class MJMesure(MJ):
        def __init__(self, *a, **kw):
            from donjon.fournisseurs.mimo import MiMo
            kw['fournisseur'] = MiMo(cle, ipv4=not args.ipv6_autorise,
                relances_format=args.relances_format, observateur_transport=journal.observateur())
            super().__init__(*a, **kw)
            self.modele, self.effort = MODELE, args.effort

        def raconter_resultat(self, monde, resultat):
            trace = {'script': courant['script'], 'tour': courant.get('tour'), 'entree': copy.deepcopy(resultat)}
            rapport.setdefault('narrations', []).append(trace)
            try:
                retour = super().raconter_resultat(monde, resultat)
                trace['retour'] = copy.deepcopy(retour)
                return retour
            except Exception as exc:
                trace['erreur'] = str(exc)
                raise

    InterfaceOrigine = banc.Interface

    class InterfaceTrace(InterfaceOrigine):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.dossier = args.sortie / 'parties' / courant['script']
            self.dossier.mkdir()
            (self.dossier / 'etats').mkdir()
            self.affichages = []

        def lire(self, *a):
            saisie = super().lire(*a)
            courant['tour'] = len(self.tours) + 1
            if not (self.dossier / 'initial.json').exists() and self.sauvegarde.exists():
                shutil.copy2(self.sauvegarde, self.dossier / 'initial.json')
            return saisie

        def ecrire(self, *valeurs, **kw):
            texte = ' '.join(str(v) for v in valeurs)
            etat = self._etat()
            if etat and etat.data.get('conversation') and texte.strip() and texte in etat.data['conversation'][-1]['reponse']:
                # Le préfixe moteur et la narration peuvent être imprimés séparément.
                self.affichages.append({'tour': len(self.tours) + 1, 'texte': texte,
                    'sauve_avant_affichage': True,
                    'empreinte_etat': hashlib.sha256(self.sauvegarde.read_bytes()).hexdigest()})
            super().ecrire(*valeurs, **kw)

        def _clore(self):
            if self.courant is None:
                return
            super()._clore()
            tour = self.tours[-1]
            tour['appels_transport'] = [i for i, a in enumerate(journal.appels, 1)
                if a.get('script') == courant['script'] and a.get('tour') == len(self.tours)]
            if self.sauvegarde.exists():
                m = Monde.charger(self.sauvegarde)
                m.verifier()
                fichier = f'etats/{len(self.tours):03d}.json'
                shutil.copy2(self.sauvegarde, self.dossier / fichier)
                shutil.copy2(self.sauvegarde, self.dossier / 'final.json')
                tour['etat_recharge_verifie'] = True
                tour['etat_fichier'] = courant['script'] + '/' + fichier
                tour['empreinte_etat'] = hashlib.sha256(self.sauvegarde.read_bytes()).hexdigest()
            sauver_json(self.dossier / 'tours-en-cours.json', self.tours)
            sauver_json(self.dossier / 'affichages-sauves.json', self.affichages)
            progression = {'script': courant['script'], 'tour': len(self.tours), 'saisie': tour['saisie'],
                           'appels_tour': tour['appels'], 'appels_total': compteur.total,
                           'appels_physiques_tour': len(tour['appels_transport']), 'appels_physiques_total': len(journal.appels),
                           'replis': tour['replis'], 'erreurs': tour['erreurs'],
                           'mentions_sans_fondement': tour['mentions_sans_fondement']}
            sauver_json(args.sortie / 'progression.json', progression)
            if tour['appels']:
                print(json.dumps(progression, ensure_ascii=False), flush=True)

    garde = jeu.chiffres_sans_fondement
    def verifier_chiffres(texte, *sources):
        refuses = garde(texte, *sources)
        rapport['gardes_numeriques'].append({'script': courant['script'], 'apres_appel': len(rapport['appels']),
            'texte': texte, 'sources': copy.deepcopy(sources), 'nombres_refuses': refuses})
        return refuses

    for nom in ('jeu.py', 'donjon/mj.py', 'donjon/fournisseurs/mimo.py', 'donjon/transport_mimo.py',
                'tools/valider_mimo_parties.py', 'tools/traces_mimo.py', 'tools/banc_parties.py',
                'donjon/config.py', 'donjon/fournisseurs/__init__.py'):
        destination = args.sortie / 'code-utilise' / nom
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BASE / nom, destination)

    debut = time.monotonic()
    try:
        with patch.object(banc, 'MJOpenAI', MJMesure), patch.object(jeu, 'MJ', MJMesure), \
             patch.object(banc, 'Interface', InterfaceTrace), \
             patch.object(jeu, 'chiffres_sans_fondement', side_effect=verifier_chiffres), \
             patch.dict(os.environ, {'MIMO_API_KEY': cle}):
            compteur.installer()
            for script in args.scripts:
                courant['script'] = script.stem
                avant = len(rapport['appels'])
                partie = banc.jouer(script, compteur, args.offline, connexion='mimo')
                partie['modele'] = MODELE
                partie['appels_transport'] = list(range(avant + 1, len(rapport['appels']) + 1))
                dossier = args.sortie / 'parties' / script.stem
                shutil.copy2(script, dossier / 'script-original.json')
                finale = Monde.charger(dossier / 'final.json')
                etat_final = copy.deepcopy(finale.data)
                shutil.copy2(dossier / 'final.json', dossier / 'reprise.json')
                charge = Monde.charger(dossier / 'reprise.json')
                assert charge.data == etat_final
                reprise = InterfaceOrigine(['inventaire', 'regarder', 'quitter'], dossier / 'reprise.json', compteur)
                scenario = json.loads(Path(script).read_text(encoding='utf-8'))['scenario']
                assert jeu.main([*banc.LANCEMENT[scenario], '--save', str(dossier / 'reprise.json'), '--offline', '--console'], interface=reprise) == 0
                reprise._clore()
                finale_reprise = Monde.charger(dossier / 'reprise.json')
                finale_reprise.verifier()
                changements = sorted(k for k in etat_final.keys() | finale_reprise.data.keys()
                                     if etat_final.get(k) != finale_reprise.data.get(k))
                partie['reprise'] = {'etat_identique_avant_commandes': True,
                                    'etat_identique': finale_reprise.data == etat_final,
                                    'champs_modifies_par_observation': changements,
                                    'objets_et_joueur_identiques': all(etat_final.get(k) == finale_reprise.data.get(k)
                                        for k in ('objets', 'joueur', 'minutes', 'journal', 'engagements', 'finances_pnj')),
                                    'tours': reprise.tours}
                fichier = args.sortie / 'parties' / (script.stem + '.json')
                sauver_json(fichier, partie)
                from rapport_fil import ecrire
                ecrire(fichier)
                resume = banc.resumer(partie)
                resume['appels_mj'] = resume['appels']
                resume['appels_mj_par_tour'] = resume['appels_par_tour_mj']
                resume['appels'] = len(partie['appels_transport'])
                resume['appels_par_tour_mj'] = round(resume['appels'] / resume['tours_mj'], 2) if resume['tours_mj'] else 0
                resume['reprise_etat_identique'] = partie['reprise']['etat_identique']
                resume['rechargement_exact'] = partie['reprise']['etat_identique_avant_commandes']
                resume['reprise_objets_et_joueur_identiques'] = partie['reprise']['objets_et_joueur_identiques']
                rapport['parties'].append(resume)
                sauver_json(args.sortie / 'resume.json', rapport['parties'])
                print(json.dumps({'partie_terminee': resume}, ensure_ascii=False), flush=True)
                if partie['arret']:
                    break
    except Exception as exc:
        rapport['exception'] = {'type': type(exc).__name__, 'message': str(exc).replace(cle, '<CLE_MASQUEE>')}
        raise
    finally:
        rapport['secondes_total'] = time.monotonic() - debut
        rapport['appels_compteur'] = compteur.total
        sauver_json(args.sortie / 'rapport.json', rapport)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
