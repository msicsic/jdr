# Préparation du transport WebSocket dans le jeu

Branche `feat/websocket-persistant`, worktree `tmp-worktrees/websocket-persistant`,
créée depuis `5cc02c1`. Cette préparation ne fusionne rien dans `main`.

## Comportement

Le mode `chatgpt` utilise désormais la WebSocket native du connecteur du jeu,
sans interposition du banc de mesure. Une connexion est ouverte au premier appel
et réutilisée pour les interprétations, les contrôles, les corrections et les
narrations du même MJ. Les commandes locales et le jeu hors ligne n'ouvrent
aucune connexion. Le mode API OpenAI conserve son transport HTTP, et Anthropic
son connecteur existant. Aucun modèle, niveau de réflexion, prompt ou règle
de validation du monde n'est modifié.

Chaque `response.create` contient l'intégralité des instructions, des outils
et du contexte autorisé de cet appel. La socket est un transport ; elle n'est
pas utilisée comme historique du jeu. Aucun `previous_response_id`, conversation
serveur ou `stream_id`. Les changements de règles, de rôle et de perception
prennent donc effet à chaque requête complète.

`donjon/transport_openai.py` gère le transport et le décodage des événements.
Le parseur exige un terminal `response.completed` avec statut `completed`.
Il récupère les `output_item.done` lorsque le terminal ne répète pas les sorties.
Les contrôles existants du MJ exigent ensuite une unique fonction attendue et
des arguments lisibles ; le moteur conserve sa validation avant toute exécution.
La taille totale est limitée et le délai porte sur l'échange entier. Les appels
sur la même connexion sont sérialisés.

La connexion est fermée à la sortie, au changement de MJ, en cas de réponse
interrompue, d'erreur ou de trames invalides. Le jeton est relu via le coffre
existant ; une rotation de jeton ou de clé de session renouvelle la connexion
avant l'envoi. Une socket déjà fermée est également renouvelée, ainsi qu'une
socket âgée de 55 minutes, avant la limite documentée de 60 minutes.
Une demande ayant pu être envoyée n'est jamais réessayée automatiquement.
La consommation éventuelle d'une réponse perdue reste inconnue.

Les erreurs réseau du client sont remplacées par des messages sans ses objets
ou en-têtes. Un refus d'authentification 401 coupe les appels suivants de ce MJ.
Il n'existe aucun repli vers HTTP ou une clé API. Les erreurs de forfait gardent
leur raison fournie par le service. Aucun identifiant d'authentification ne rejoint
les sauvegardes ou les nouvelles traces de vérification.

La comparaison reste désactivée par défaut. Son chemin de fermeture libère
aussi les ressources des deux MJ, sans attendre l'appel secondaire en cours :
ce dernier ferme sa connexion quand son travail se termine.

## Validation

Suite complète : **847 tests passent** (`python -m unittest discover -s tests`).
Les 36 tests ciblés du transport, des parcours WebSocket, de la connexion et
du cycle de fermeture ont aussi été relancés après le dernier renforcement
de la corrélation des événements. Compilation Python vérifiée.

Les tests couvrent la réutilisation entre rôles, le renouvellement des règles
et du contexte, les coupures sans rejeu, l'authentification, le budget de délai,
la limite de volume, les terminaux manquants ou étrangers, la rotation de jeton
et la fermeture des connexions.

Les parcours de crypte et d'atelier traversent la saisie, le vrai MJ, le parseur,
le moteur, les audits, l'affichage et la sauvegarde. Des coupures simulées avant
l'action et après sa sauvegarde vérifient les deux scènes : aucun fragment
n'est affiché, aucune action partielle n'est créée et le repli de narration
conserve l'action déjà exécutée. Les vérifications comparent aussi l'état et
ce que le joueur voit après rechargement.

Deux parties réelles avec Luna medium ont également réussi : prendre la clé
dans la crypte et prendre la ficelle dans l'atelier. Huit appels terminés,
une ouverture et une fermeture par partie ; les quatre rôles successifs partagent
chaque connexion. Les récits sont enregistrés avant affichage, puis l'état complet
et l'inventaire sont vérifiés après reprise hors ligne. Ce contrôle valide
l'intégration ; il ne mesure pas un nouveau gain de latence.

Le résultat portable est dans [verification-websocket-jeu.json](verification-websocket-jeu.json). La dépendance
de test réelle est `websockets 16.1.1`, déjà utilisée par les bancs ; l'installation
normale passe par `requirements-chatgpt.txt`, qui exige `websockets>=16,<17`.
Pendant cette validation, `PYTHONPATH` désignait l'installation isolée du banc,
afin de conserver l'environnement Python principal tel quel.

Pour reproduire le contrôle réel, depuis le worktree avec ses dépendances :

```powershell
$env:SEUIL_AUTH = 'C:/Users/msics/donjon/.seuil-auth'
$env:PYTHONPATH = 'C:/Users/msics/donjon/tmp-worktrees/ttft-luna-medium/artifacts/ttft-deps'
& C:/Users/msics/donjon/.venv/Scripts/python.exe tools/verifier_websocket_jeu.py `
  --sortie artifacts/verification-websocket/NOUVELLE-PASSE --max-appels 24
```

Références de protocole : [WebSocket Responses](https://developers.openai.com/api/docs/guides/websocket-mode)
et [limites de Sign in with ChatGPT](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
