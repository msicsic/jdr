# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-18.

## Où on en est

- `main` contient les jalons PNJ A à H (`docs/plan-pnj.md`, tableau « Jalons » et sections
  « Écarts retenus »). Le dernier fusionné est **H. Se sentir en sécurité** :
  - la sécurité suit la perception : le noir, un bruit venu d'ailleurs, un geste illicite vu,
    la méfiance inquiètent ; la lumière, une compagnie fiable (le joueur compris), une ronde
    accomplie rassurent ; valeurs nuancées par profil (`securite`) ;
  - se mettre à l'abri : rejoindre la lumière près de qui l'on croit fiable ;
  - les rondes se font en routine, même quand rien ne presse ;
  - avant H, **G. Le feu partagé** : une flamme en allume une autre, la part de bois, les
    recours au froid, l'inertie d'un plan en cours, la flamme ménagée.
- Luna (`gpt-6-luna`) reste le MJ. Le stratège Luna des PNJ (jalon E) est optionnel
  (`--stratege`), désactivé par défaut. Remesuré sur le Relais de F, il n'apporte presque
  plus rien : +5 % d'événements, −1 % d'oisiveté urgente. Le moteur fait désormais seul
  ce qui était son apport principal.
- Après F, branche `recharger-foyer` : mettre un combustible dans un foyer, c'est le recharger
  (`deplacer` vers un foyer devient `alimenter`) ; le combustible peut être porté ou à portée
  de main ; le titre de `deplacer` vers le joueur dit « Prendre », sans rangement que l'état
  ne modélise pas. Détail et vérification réelle dans `docs/plan-pnj.md` (écarts du jalon F).
- La suite de tests passe : 534 tests, 31 ignorés, sans clé ni connexion.

## Décisions en attente

- **Suite du plan PNJ**, au choix :
  - la crue du Relais, événement de scénario qui s'appuie sur H pour inquiéter ;
  - un événement qui éteint le feu en laissant du bois (les `horloges` existent, aucun
    scénario n'en déclare encore) ;
  - d'autres remèdes au froid ; le joueur qui demande une part ;
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
