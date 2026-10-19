# État du développement

Point de reprise, à tenir à jour à chaque fin de jalon. Mis à jour le 2026-10-19.

## Où on en est

- `main` contient les jalons PNJ A à I (`docs/plan-pnj.md`, tableau « Jalons » et sections
  « Écarts retenus »). Le dernier fusionné est **I. Demander, écouter, protéger** :
  - le corps commun (faim, froid, fatigue) pour tous, joueur compris (`donjon/corps.py`) ;
    malus aux jets, PV à l'extrême, manger ; le scénario déclare des états ;
  - le joueur demande une part de vivres ou de bois ;
  - les PNJ font du bruit ; action `ecouter`, mieux contre une porte ;
  - protéger : donnée `protege`, appel à l'aide, protecteur qui accourt, victime prévenue.
  - avant I : H (sécurité perçue, abri, rondes en routine), G (le feu partagé).
- Luna (`gpt-6-luna`) reste le MJ. Le stratège Luna des PNJ (jalon E) est optionnel
  (`--stratege`), désactivé par défaut. Remesuré sur le Relais de F, il n'apporte presque
  plus rien : +5 % d'événements, −1 % d'oisiveté urgente. Le moteur fait désormais seul
  ce qui était son apport principal.
- Après F, branche `recharger-foyer` : mettre un combustible dans un foyer, c'est le recharger
  (`deplacer` vers un foyer devient `alimenter`) ; le combustible peut être porté ou à portée
  de main ; le titre de `deplacer` vers le joueur dit « Prendre », sans rangement que l'état
  ne modélise pas. Détail et vérification réelle dans `docs/plan-pnj.md` (écarts du jalon F).
- Branche `messages-refus` : les refus du moteur guident la correction du MJ. Chaque
  `ErreurMonde` porte `attendu` (champ fautif, valeur reçue, identifiants valables), transmis
  dans `retour_moteur` et jamais au joueur ; les causes fusionnées sont séparées ; l'étape,
  l'effet ou l'ajout fautif est numéroté. Mesure Haiku A/B sur les trois bancs : les refus
  corrigeables passent de 4 répétés et jamais corrigés à 2 corrigés dès la première relance.
  Restent hors périmètre : les messages d'audit (contrôle narratif, contre-revue).
- Branche `contre-revue` : le raccourci `detacher` libère la fixation sur place (la prendre
  est une étape `deplacer` explicite) ; un rapport de contre-revue mal formé est redemandé
  une fois puis le plan validé passe, au lieu d'être renvoyé au MJ comme un refus. Cas réel
  « fais levier sous l'axe » : 2 appels, conforme du premier coup (contre 4 à 8 avant).
- Branche `banc-haiku` : Claude Haiku 5.5 est une option du jeu (`--connexion anthropic`,
  `donjon/claude.py`, `requirements-claude.txt`) ; Luna reste le MJ par défaut. Correctifs
  communs révélés par le fil complet des appels (`tools/banc_parties.py --fil`) : citation de
  fait inconnue écartée au lieu d'invalider la réponse ; audit narratif à une entrée
  obligatoire par segment, audit illisible redemandé ; texte vide signalé sans audit ;
  apparence d'un personnage acceptée en aspect ou portrait ; rappel d'une parole déjà
  entendue classé mécanique. Comparatif final sur les trois bancs (31 tours MJ) : Luna
  3,55 appels et 20 s par tour MJ, Haiku 3,68 appels et 12 s, 1 repli chacun (celui de
  Haiku corrigé ensuite), Haiku 0,17 $ les trois parties. Ni l'un ni l'autre ne réfléchit
  dans le jeu : Haiku ne le peut pas sous outil imposé, Luna en medium ne produit aucun jeton
  de réflexion. `tools/sonde_reflexion.py` vérifie hors jeu qu'une réflexion se constate.
- Branches `haiku-reflexion` et `narration-fidele` : Haiku joue par défaut avec réflexion
  adaptative (`--reflexion libre` ; `imposee` reste plus rapide, sans réflexion). Une réponse
  rendue en texte au lieu de l'appel est retranscrite en appel imposé. Banc (31 tours MJ) :
  0 repli, 1 tour refusé (contre 8 sans réflexion, 5 pour Luna), 22 s par tour MJ, 0,18 $
  les trois parties. Narration fidèle, quatre défauts communs corrigés : message technique
  affiché au joueur (consigner sans les croyances du locuteur), réplique du joueur réécrite
  (le personnage interpellé en tête est le destinataire, ses mots sont la réplique), geste
  refusé raconté comme tenté (audit), voix d'auteur dans le texte affiché (contrôle
  déterministe). Comparaison des textes : Luna ~190 caractères, sobre ; Haiku ~340, plus
  descriptif, et plus de dérives que les corrections encadrent.
- Branche `instructions-mj` : consignes du MJ réécrites (`donjon/consignes.py`), dans l'ordre de
  la décision (ton, autorité, mode, puis une section par mode), une règle à un seul endroit,
  sans anciens raccourcis ni rustines d'exemples ; ~15 000 caractères au lieu de ~24 000.
  Bancs multiples (même code, consignes seules) : Haiku 3 passes, 3,06 appels et 22 s par tour
  MJ contre 3,20 et 23,7, refus 1,3 contre 2,0, coût −8 % ; Luna 2 passes, 3,24 appels et 17 s
  contre 3,50 et 20,2, 0 repli contre 1, refus 4,5 contre 6.
- Outillage : `tools/banc_multi.py` joue des variantes (références git) en plusieurs passes et
  en parallèle, et résume moyenne et étendue ; le forfait ChatGPT a tenu 4 passes simultanées.
- La suite de tests passe : 598 tests, sans clé ni connexion.

## Décisions en attente

- **Fabrication générale** (en cours) : seule l'échelle à barreaux existe, avec des matériaux
  que l'auteur déclare (`ressource`, longueur, charge, dans `scenario_atelier.json`). Le MJ ne
  peut pas qualifier un objet existant comme matériau (planches du Relais). Étape 1 : cette
  qualification par `etablir_faits`, contrôlée comme les capacités.
- **Instructions conditionnées à l'état du monde** : plus tard ; critère retenu, inclure une
  règle quand le moteur pourrait valider ce type de proposition dans l'état actuel, jamais
  selon un lieu ou un scénario.
- **Suite du plan PNJ**, au choix :
  - la crue du Relais, événement de scénario qui s'appuie sur H pour inquiéter ;
  - un événement qui éteint le feu en laissant du bois (les `horloges` existent, aucun
    scénario n'en déclare encore) ;
  - la voix des PNJ : Luna donne voix aux échanges entre PNJ dont le joueur est témoin, et
    les répliques ne contredisent plus l'issue décidée par le moteur ;
  - une protection plus riche ; d'autres remèdes au froid ;
  - la priorité du stratège aux PNJ que le joueur perçoit.
- **Branches d'essai**, poussées sur `origin` et non fusionnées :
  - `essai-code` : le MJ écrit un script Python borné au lieu du JSON ;
  - `essai-haiku` : premier adaptateur Anthropic, remplacé par celui de `banc-haiku`.
  Les mesures sont rapportées dans leurs commits.

## Reprendre sur un autre poste

1. `git clone https://github.com/msicsic/jdr.git`, puis l'installation du README (`.venv`,
   `requirements-tui.txt`, `requirements-chatgpt.txt`).
2. Connexion de Luna : `python connexion.py connecter` (forfait ChatGPT, voir
   `docs/connexion.md`). L'autorisation (`.seuil-auth/`) n'est pas versionnée et se refait
   sur chaque poste.
3. Clés éventuelles dans `.env`, non versionné : `OPENAI_API_KEY` pour `--connexion api`.
   `ANTHROPIC_API_KEY` pour `--connexion anthropic` (Haiku, `requirements-claude.txt`).
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
