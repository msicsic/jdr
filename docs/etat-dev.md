# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-18.

## Où on en est

- `main` contient les jalons PNJ A à F (`docs/plan-pnj.md`, tableau « Jalons » et sections
  « Écarts retenus »). Le dernier fusionné est **F. Tensions du Relais** :
  - faim pour tous et 4 parts de vivres ;
  - froid des évacués et brasero entretenu par Gorm avec des fagots comptés ;
  - un affamé demande une part avant de voler, cherche Gorm s'il l'a perdu de vue ;
  - geste `alimenter` commun au joueur et aux PNJ ;
  - ordre des buts : ce qui presse, parole donnée, ce qu'on finit, routine.
- Luna (`gpt-6-luna`) reste le MJ. Le stratège Luna des PNJ (jalon E) est optionnel
  (`--stratege`), désactivé par défaut. Remesuré sur le Relais de F, il n'apporte presque
  plus rien : +5 % d'événements, −1 % d'oisiveté urgente. Le moteur fait désormais seul
  ce qui était son apport principal.
- La suite de tests passe : 513 tests, 31 ignorés.

## Décisions en attente

- **Tournure non comprise par Luna** : « je ramasse les fagots et j'en mets une brassée dans
  le feu du brasero » échoue, car Luna y voit une pose dans le brasero et ne propose rien. Deux
  options :
  - une règle générale du moteur (mettre un combustible dans un foyer, c'est le recharger) ;
  - garder la limite. Pas de consigne propre à cette tournure (AGENTS.md).
- **Suite du plan PNJ**, au choix :
  - une sécurité qui se gagne autrement que par les rondes ;
  - un feu que les PNJ peuvent rallumer sans le briquet du joueur ;
  - partager le bois, d'autres remèdes au froid ;
  - la priorité du stratège aux PNJ que le joueur perçoit.
- **Branches d'essai**, poussées sur `origin` et non fusionnées :
  - `essai-code` : le MJ écrit un script Python borné au lieu du JSON ;
  - `essai-haiku` : adaptateur Anthropic pour évaluer Claude Haiku.
  Les mesures sont rapportées dans leurs commits. Rien n'en est retenu dans `main`.

## Reprendre sur un autre poste

1. `git clone https://github.com/msicsic/jdr.git`, puis l'installation du README (`.venv`,
   `requirements-tui.txt`, `requirements-chatgpt.txt`).
2. Connexion de Luna : `python connexion.py connecter` (forfait ChatGPT, voir
   `docs/connexion.md`). L'autorisation (`.seuil-auth/`) n'est pas versionnée et se refait
   sur chaque poste.
3. Clés éventuelles dans `.env`, non versionné : `OPENAI_API_KEY` pour `--connexion api`.
   `ANTHROPIC_API_KEY` ne sert qu'à la branche `essai-haiku`.
4. Vérifier : `python -m unittest discover -s tests -q`.

Non versionnés, donc absents d'un nouveau poste :
- `sauvegardes/` ;
- `artifacts/` (chroniques et verdicts des bancs, traces du MJ). Les bilans chiffrés des bancs
  sont recopiés dans `docs/plan-pnj.md`.

## Outils de mesure

- Banc moteur seul, sans appel à Luna :
  `python -m donjon.banc_pnj --heures 8 --graine 1985 --joueur chambre_cloche`
- Banc A/B du stratège, avec Luna, environ 15 minutes pour 8 graines :
  `python tools/banc_stratege.py --graines 1985 7 42 2024 --graines-sup 3 11 99 500`
  Ne pas lancer deux exécutions Luna en parallèle : la connexion ChatGPT n'en accepte
  qu'une.

## Règles de travail

- `AGENTS.md` : corriger l'invariant général, jamais le cas de l'exemple ; vérifier le cas réel
  et un autre cas de même nature après rechargement ; dire les limites.
- Une branche par jalon, fusionnée avant d'ouvrir la suivante ; pas de nouveau mécanisme en
  cours de jalon sans accord.
- Les phrases des docs tirées d'un test ou d'un scénario décrivent ce scénario, pas une règle
  de conception du jeu.
