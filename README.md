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
.\.venv\Scripts\python.exe jeu.py --defi --tui
.\.venv\Scripts\python.exe jeu.py --atelier --cases --tui --debug
.\.venv\Scripts\python.exe jeu.py --cases --console --offline
```

La partie reprend automatiquement. `--new` recommence en conservant l'ancienne sauvegarde dans
un fichier `.bak`. `--offline` interdit tout appel au modèle ; les commandes locales restent
disponibles. Installation : `python -m venv .venv`, puis
`.\.venv\Scripts\python.exe -m pip install -r requirements-tui.txt -r requirements-chatgpt.txt`.

## Jouer

- **Ctrl + flèches** : avancer d'une case ; **F6** puis flèches : piloter depuis la carte.
- **F1** aide, **F2** carte, **F3** personnage, **F4** copier le dernier échange, **F5** traces (debug).
- **Ctrl+S** sauvegarder, **Ctrl+Q** sauvegarder et quitter.
- `aide` liste les commandes locales (`examiner`, `prendre`, `ouvrir … avec …`, `retirer … avec …`,
  `couper … avec …`, `fabriquer échelle`, `crier`…). Elles n'appellent jamais le modèle.
- Toute autre phrase va au MJ. Une manœuvre avec jet ou risque est annoncée : **tenter** l'exécute,
  **annuler** l'abandonne. « je retente » reprend la dernière tentative échouée sans appel au modèle.

## Documentation

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
