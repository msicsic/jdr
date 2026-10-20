# Le Seuil

Prototype de JDR ASCII en français, Python 3.11 ou supérieur. Un moteur déterministe tient
l'état du monde (positions, lumière, objets, ressources, dés) ; Luna, le MJ (`gpt-6-luna`),
interprète les phrases libres, propose des actions et des faits typés que le moteur valide,
et raconte. L'interface plein écran utilise Textual ; le mode console n'a besoin que de la
bibliothèque standard.

## Lancer

Sous Windows, double-cliquer sur un lanceur :

| Lanceur | Scène | Sauvegarde |
|---|---|---|
| `lancer.cmd` | Crypte du veilleur : retrouver l'anneau pour Gorm | `sauvegardes/partie.json` |
| `lancer-defi.cmd` | Relais des crues : rapporter la cloche d'alarme | `sauvegardes/defi.json` |
| `lancer-defi-hors-ligne.cmd` | Relais des crues sans aucun appel au modèle | `sauvegardes/defi.json` |
| `lancer-atelier.cmd` | Atelier : atteindre la terrasse (fabrication, saut, échelle) | `sauvegardes/atelier.json` |
| `lancer-debug.cmd` | Crypte avec traces du MJ dans `artifacts/mj/` | `sauvegardes/partie.json` |

En ligne de commande :

```powershell
.\.venv\Scripts\python.exe jeu.py --defi
.\.venv\Scripts\python.exe jeu.py --atelier --cases --tui --debug
.\.venv\Scripts\python.exe jeu.py --cases --console --offline
.\.venv\Scripts\python.exe jeu.py --crue --offline
```

Par défaut, la partie se joue dans le navigateur : le jeu lance un serveur local (127.0.0.1,
seulement depuis cette machine) et ouvre la page (récit, saisie, carte où un clic mène ou propose
un geste). `--tui` garde l'interface plein écran du terminal (et ses panneaux de `--debug`),
`--console` l'affichage ligne par ligne, choisi d'office quand l'entrée est redirigée.
`lancer.cmd` et `lancer-defi.cmd` ouvrent la page ; les lanceurs avec `--debug` gardent la TUI.

`--crue` joue le Relais dont l'eau monte selon la graine (`--seed`), sauvegardé dans
`sauvegardes/crue.json`.

La partie reprend automatiquement. `--new` recommence en conservant l'ancienne sauvegarde dans
un fichier `.bak`. `--offline` interdit tout appel au modèle ; les commandes locales restent
disponibles. `--recit-moteur` affiche les résultats d'action rédigés par le moteur au lieu du
récit de Luna (un appel de moins par action). Installation : `python -m venv .venv`, puis
`.\.venv\Scripts\python.exe -m pip install -r requirements-tui.txt -r requirements-chatgpt.txt`.
Claude Haiku peut remplacer Luna : `--connexion anthropic`, avec `ANTHROPIC_API_KEY` dans `.env`
et `-r requirements-claude.txt`.

## Jouer

- **Ctrl + flèches** : avancer d'une case ; **F6** puis flèches : piloter depuis la carte.
- **F1** aide, **F2** carte, **F3** personnage, **F4** copier le dernier échange, **F5** traces (debug).
- **Ctrl+S** sauvegarder, **Ctrl+Q** sauvegarder et quitter.
- `aide` liste les commandes locales (`examiner`, `prendre`, `ouvrir … avec …`, `retirer … avec …`,
  `couper … avec …`, `fabriquer échelle`, `crier`…). Elles n'appellent jamais le modèle.
- Toute autre phrase va au MJ. Une manœuvre avec jet ou risque est annoncée : **tenter** l'exécute,
  **annuler** l'abandonne. « je retente » reprend la dernière tentative échouée sans appel au modèle.

## Documentation

- [docs/etat-dev.md](docs/etat-dev.md) : où en est le développement, décisions en attente, reprise sur un autre poste.
- [docs/plan-pnj.md](docs/plan-pnj.md) : PNJ comportementaux, jalons A à F et leurs bilans.
- [docs/mecaniques.md](docs/mecaniques.md) : scènes, carte et cases, lumière, fabrication,
  franchissements, sons, manœuvres composées, dialogues, vol, savoirs des PNJ, limites.
- [docs/contrat-mj.md](docs/contrat-mj.md) : ce que le MJ peut affirmer, comment le moteur le contrôle.
- [docs/connexion.md](docs/connexion.md) : forfait ChatGPT, clé API, comparaison de modèles (désactivée).
- [docs/plan-migration-mj.md](docs/plan-migration-mj.md) : plan de migration en cours.
- [AGENTS.md](AGENTS.md) : règles de développement.

## Vérification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe tools\banc_parties.py tests\data\bancs\relais.json --max-appels 100
python jeu.py --demo
```

Les tests unitaires n'appellent pas le modèle. Le banc rejoue des parties scriptées avec Luna
sur une sauvegarde temporaire et mesure, par tour : appels, durée, replis du contrôle narratif,
refus de validation et mentions d'entités sans fondement (`artifacts/bancs/`). Les scripts
`tools/test_*_reel.py` vérifient des parcours précis avec de vrais appels.
