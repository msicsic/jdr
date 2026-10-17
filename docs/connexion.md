# Connexion au modèle et outils de développement

### Activer le MJ IA

#### Avec le forfait ChatGPT

Le jeu propose le flux officiel « Sign in with ChatGPT » pour les comptes et forfaits éligibles.
Il ne récupère pas les identifiants de Codex ou d'autres applications. L'autorisation se fait dans
le navigateur avec votre compte ChatGPT ; cela n'achète ni abonnement ni crédits.

Depuis le terminal, si la dépendance n'est pas déjà installée :

```powershell
python -m pip install -r requirements-chatgpt.txt
python connexion.py connecter
python jeu.py --connexion chatgpt
```

On peut aussi lancer le jeu sans `--offline`, puis saisir `connecter` dans le jeu. La commande
`connexion` affiche le mode en cours. Après une connexion réussie dans le navigateur, le jeu utilise
directement le forfait. Son utilisation reste soumise aux limites du compte.

Les modèles accessibles au compte se consultent ainsi :

```powershell
python connexion.py modeles
python jeu.py --connexion chatgpt --model gpt-6-luna
```

Le modèle demandé est vérifié dans le catalogue du compte avant le premier appel. Aucun modèle
de substitution n'est choisi silencieusement. `python connexion.py statut` liste les inscriptions
sans afficher les jetons ; `connecter --nouveau` ajoute un autre compte et `connecter --compte <id>`
réutilise une inscription. `python connexion.py deconnecter` révoque la session si possible,
efface les jetons locaux et conserve l'identifiant d'inscription pour une connexion ultérieure.

Les identifiants du jeu sont isolés dans `.seuil-auth/`, exclu de Git. Les jetons sont chiffrés avec
DPAPI sous Windows (liés au compte Windows) ; sur Unix, le répertoire et les fichiers sont privés.
Les retours OAuth vérifient `state`, PKCE, la signature du jeton d'identité, son émetteur,
son audience, sa durée de validité et son nonce. L'autorisation d'utiliser le forfait est vérifiée
séparément. Un verrou évite les rafraîchissements concurrents du même coffre.

Le transport forfait impose `store: false`, `stream: true` et des outils placés dans un namespace.
Un fragment de réponse n'est jamais exécuté : seul `response.completed` valide la proposition.
Les erreurs de forfait ne déclenchent aucun basculement vers une clé API facturée séparément.

Par défaut, le jeu privilégie une inscription ChatGPT enregistrée. `--connexion api` choisit
explicitement la clé API ; `--offline` interdit toute connexion, y compris la commande `connecter`.

#### Avec une clé API

Le connecteur utilise l'API OpenAI Responses et un appel de fonction strict `repondre_au_joueur`.
`proposer_action` reste disponible pour les tests d’arbitrage seuls.
La clé vient de `OPENAI_API_KEY`. On peut également copier `.env.example` vers `.env` et
y renseigner la clé localement. Les valeurs non vides du `.env` priment sur celles du terminal.
Ni la clé ni les en-têtes d'authentification ne sont enregistrés dans la sauvegarde.

Le modèle par défaut est `gpt-6-luna`, avec un effort de raisonnement `medium`.
Il est configurable via `OPENAI_MODEL`, le `.env` ou `--model` :

```powershell
python jeu.py --model gpt-6-luna --effort medium
```

Le modèle choisi doit être accessible avec votre compte et prendre en charge Responses,
les appels de fonction stricts et `reasoning.effort`. Aucun changement de modèle automatique n'est effectué.

Une phrase libre appelle le MJ. Le préfixe `mj` force ce chemin :

```text
mj Je glisse mon couteau sous la tête de l'axe supérieur et fais doucement levier.
tenter
```

Le MJ propose une seule manœuvre, son outil et, pour l'extraction d'une fixation, sa difficulté.
Une action simple et explicite (« je prend la clé ») est validée puis exécutée directement.
Si une manœuvre interprétée par le MJ exige un jet ou comporte un risque, le jeu affiche le test,
la durée et le risque : `tenter` applique alors la proposition ; `annuler` l'abandonne.
Les commandes locales explicites gardent leur exécution directe.
Les observations et examens sont affichés immédiatement.
Discuter avec le MJ conserve la proposition en attente ; une autre action la remplace.
Le MJ reçoit explicitement cette proposition afin de distinguer ce qui reste à tenter d’un résultat acquis.
Le moteur recompilé au moment d'agir vérifie que l'état n'a pas changé.

Les commandes locales n'appellent pas l'API. Une phrase transmise au MJ peut déclencher
plusieurs appels : interprétation, contre-revues, correction et parfois narration du résultat.
Chaque action confiée au MJ reçoit aussi une contre-revue de fidélité entre l'intention et
le plan mécanique, ce qui ajoute au moins un appel et peut allonger l'attente.
Ces appels sont décomptés du forfait ou facturés sur le compte API. Le contexte contient
l’intention, la scène perceptible, la fiche, la prémisse, les six derniers événements et les douze
derniers échanges. Les paroles du joueur et du MJ sont séparées des faits du moteur. Le trésor encore caché et le sens
non déchiffré de la gravure sont exclus de cette vue. `store` vaut `false`.
La réponse de conversation vient du LLM ; les résultats d’actions restent décrits par le moteur,
avec parfois un appel de narration supplémentaire. Les affirmations libres affichées passent
par le contrôle décrit dans contrat-mj.md. Les avis non contrôlés d'une proposition et
les brouillons d'intention de Luna ne sont pas affichés. Le contrôle sémantique reste probabiliste.

En cas de clé invalide, délai réseau ou réponse incorrecte, l'action n'est pas appliquée.
Une erreur 401 coupe les appels répétés pour cette session ; connecter le forfait recrée un client.
Les commandes locales restent utilisables. La présence d'une clé ne signifie pas qu'elle est valide :
la bannière indique que la connexion sera vérifiée au premier échange.

### Comparer deux modèles pendant une partie

**`lancer.cmd` et `lancer-debug.cmd` utilisent Luna seul.** Le second lanceur ajoute les traces
locales dans `artifacts/mj/` et les commandes d'inspection, sans appel à un autre modèle.
La comparaison reste disponible uniquement sur demande explicite avec `--compare-model`.
Elle utilise la même connexion (forfait ChatGPT ou clé API) ; les appels supplémentaires
consomment donc cette connexion.

Pour choisir les modèles et l'effort de raisonnement :

```powershell
.\.venv\Scripts\python.exe jeu.py --tui --debug --model gpt-6.1-sol --compare-model gpt-6-luna
```

`--compare-effort low` change seulement l'effort du secondaire ; par défaut il est identique au principal.
`--debug` seul autorise l'inspection des objets et ne lance aucun second modèle.
Les données d'usage ne sont pas imprimées dans la Chronique ; les compteurs de tokens
restent dans le panneau de comparaison et les données détaillées dans ses journaux.

- **F5** ouvre ou ferme la console de comparaison. Les colonnes montrent les textes, les faits
  proposés, les actions, la validation du moteur, la durée et les tokens additionnés sur tous les appels
  de l'échange. Les faits refusés sont également visibles. Sur un terminal étroit, les colonnes s'empilent.
- La souris permet de sélectionner et faire défiler le texte ; **Ctrl+C** copie la sélection.
  **F4** copie toute la comparaison affichée. Les boutons permettent de parcourir les 100 dernières
  comparaisons de ce lancement. F2/F3 reviennent au jeu.
- Chaque demande au MJ part de **deux copies identiques** du monde, de l'historique et de la proposition
  en attente. Les premières requêtes ont la même empreinte, hors modèle et effort. Si un modèle propose
  un enrichissement, son appel de narration reçoit ses propres ajouts validés sur sa copie : ces seconds
  appels peuvent donc différer. Au tour suivant, tous deux repartent de la partie réelle du principal.
- **Seul le principal pilote la partie.** Le secondaire ne lance jamais de jet et n'enregistre aucun fait
  dans la sauvegarde. Il reste en arrière-plan ; son erreur ou sa lenteur n'empêchent pas de jouer.
  Si les demandes se succèdent trop vite, le secondaire les traite dans l'ordre sur leurs instantanés
  respectifs (huit en attente maximum, tout dépassement est signalé). À la fermeture, les demandes en
  attente sont abandonnées ; un appel déjà envoyé peut tout de même être consommé côté fournisseur.
- Les commandes purement locales ne déclenchent aucune comparaison. `--offline` interdit les deux modèles.
  En mode `--console`, saisir `comparaison` affiche le dernier état des résultats sans entremêler les
  sorties du secondaire avec la saisie du joueur.

Les traces sont enregistrées dans `artifacts/comparaisons/comparaison-*.jsonl` (un fichier par lancement,
plusieurs versions d'une même comparaison, repérées par `numero` et `version`). Elles contiennent les
questions, réponses, propositions, erreurs et usages, sans clés ni jetons d'authentification.
Une panne d'écriture du journal est signalée dans la console debug et ne bloque pas le jeu.

`tools/test_comparaison_reel.py` teste une question sur les yeux de Gorm avec les deux modèles : deux
à quatre appels réels, aucun changement de la sauvegarde utilisateur. `tools/apercu_comparaison.py`
produit des captures de l'interface avec des réponses simulées, hors ligne.

### Vérification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
python jeu.py --demo
```

Les tests couvrent notamment l'accès depuis le bon côté, la non-divulgation des secrets,
les objets et outils absents, les achats, les risques, l'empreinte persistante, les portes calées,
la destruction de contenants, l'atomicité, la sauvegarde et le contrat API avec réponses simulées.
Ils couvrent aussi la question exacte ci-dessus, les réponses sans action, le noir complet, le rallumage,
la lumière bloquée par les portes ou contenants, la consommation du combustible et la migration des sauvegardes.

Un test distinct effectue **quatre véritables appels**, décomptés du forfait ou facturés à la clé API :
question sur l'arrivée, question sur la lumière, extraction plausible d'un petit axe au couteau,
puis tentative impossible de soulever tout le battant avec la lame. Il ne modifie aucune partie :

```powershell
python tools/test_mj_reel.py
```

Le test narratif utilise **six appels réels** dans une conversation suivie, sans toucher à la
sauvegarde utilisateur :

```powershell
python tools/test_recit_reel.py --connexion chatgpt
```

`python tools/test_personnages_reel.py` effectue deux appels réels supplémentaires pour vérifier
le portrait de Gorm malgré une ancienne réponse erronée, puis la distinction entre souvenir
et humeur actuelle à distance. Il ne modifie aucune sauvegarde.

`python tools/test_enrichissement_reel.py` teste trois questions (au plus six appels réels) :
création d'un détail de Gorm, rappel identique après sauvegarde/rechargement et portrait d'un autre
personnage sans description initiale. Le test emploie une partie temporaire et vérifie aussi l'examen
local des détails créés. Les tests automatiques couvrent les refus de modification, les échecs réseau
ou disque, le maintien d'une manœuvre en attente et le rafraîchissement de la TUI.

Le 9 octobre 2026, six échanges avec `gpt-6.1-sol` via le forfait ont été relus :

- Arrivée : récit du passage par l’échoppe de Gorm.
- Relance « pourquoi il ne va pas le chercher lui-même ? » : résolution du pronom, sans inventer ses raisons.
- Visibilité sans fenêtres : explication par la lanterne et la lueur de l’ouest.
- Extraction au couteau : proposition validée pour l’axe supérieur, DD 18.
- « Donc je l’ai retiré ? » : distinction entre proposition et réussite, porte toujours fermée.
- Après extinction effective de la lanterne : pénombre, silhouettes visibles mais détails illisibles.

Les temps observés étaient de 3,7 à 5,4 secondes par réponse. Cet échantillon n’est pas une
preuve de fidélité générale : les tests automatiques contrôlent surtout le contrat, la mémoire,
la séparation dialogue/action et la conservation de l’état. La prose se vérifie aussi en jouant.

Référence d'intégration : [appels de fonction de l'API OpenAI](https://developers.openai.com/api/docs/guides/function-calling).
Connexion forfait : [inscription et connexion](https://developers.openai.com/siwc/token-sharing-open-source/sign-in),
[requêtes d'inférence](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference),
[contraintes du flux](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).

Les tests TUI utilisent le pilote clavier de Textual, hors réseau : prise et dépôt de la clé,
rafraîchissement des vues, boutons de confirmation, redimensionnement, historique de saisie
et maintien de l’interface pendant un appel simulé du MJ. Sans Textual, ces tests sont ignorés.
`tools/apercu_tui.py` exporte des captures SVG à plusieurs tailles, dans `artifacts/tui`,
sans modifier la sauvegarde utilisateur.

Références TUI : [tests Textual](https://textual.textualize.io/guide/testing/),
[workers et threads](https://textual.textualize.io/guide/workers/).
Copie : [sélection de texte Textual](https://textual.textualize.io/FAQ/#how-can-i-select-and-copy-text-in-a-textual-app),
[presse-papiers Pyperclip](https://pyperclip.readthedocs.io/en/latest/).
