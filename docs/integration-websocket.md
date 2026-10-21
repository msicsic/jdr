# Préparation du transport WebSocket dans le jeu

Branche `feat/websocket-persistant`, worktree `tmp-worktrees/websocket-persistant`,
créée depuis `5cc02c1`, fusionnée dans `main` le 2026-10-21.

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
Une coupure réseau ou l'erreur de limite de durée déclenche une reconnexion et
une tentative supplémentaire du même appel LLM. Les fragments de la tentative
perdue sont abandonnés ; le contexte complet est renvoyé à l'identique, sans
parent. La fermeture est terminée avant d'ouvrir la nouvelle socket. Le budget
de délai initial est partagé entre les deux tentatives, sans boucle illimitée.
La consommation éventuelle d'une réponse perdue reste inconnue. L'action moteur
est exécutée uniquement après le retour final validé, jamais lors du rejeu LLM.

Les erreurs réseau du client sont remplacées par des messages sans ses objets
ou en-têtes. Un refus d'authentification 401 coupe les appels suivants de ce MJ.
Il n'existe aucun repli vers HTTP ou une clé API. Les erreurs de forfait gardent
leur raison fournie par le service. Aucun identifiant d'authentification ne rejoint
les sauvegardes ou les nouvelles traces de vérification.

La comparaison reste désactivée par défaut. Son chemin de fermeture libère
aussi les ressources des deux MJ, sans attendre l'appel secondaire en cours :
ce dernier ferme sa connexion quand son travail se termine.

## Validation

Validation initiale (`fa342cd`) : **847 tests passent** sur la suite complète
(`python -m unittest discover -s tests`). Après ajout de la reconnexion
transparente : **82 tests ciblés passent** (transport, parcours WebSocket,
connexion, comparaison, prototype et récit). Compilation Python vérifiée.

Les tests couvrent la réutilisation entre rôles, le renouvellement des règles
et du contexte, les coupures avec reconnexion transparente, l'authentification, le budget de délai,
la limite de volume, les terminaux manquants ou étrangers, la rotation de jeton
et la fermeture des connexions.

Les parcours de crypte et d'atelier traversent la saisie, le vrai MJ, le parseur,
le moteur, les audits, l'affichage et la sauvegarde. Des coupures simulées avant
l'action et après sa sauvegarde vérifient les deux scènes : aucun fragment
n'est affiché, aucune action partielle n'est créée et le repli de narration
conserve l'action déjà exécutée. Les vérifications comparent aussi l'état et
ce que le joueur voit après rechargement.

Les coupures transitoires sont injectées aux quatre étapes (interprétation,
audit d'action, narration, audit de narration) sur les deux scènes. Le même
appel repart à l'identique et réussit sans message d'erreur au joueur. Le
journal contient un seul commit moteur. Les contrôles couvrent aussi le refus
`websocket_connection_limit_reached`, le renouvellement préventif à 55 minutes,
l'échec initial d'ouverture, les deux échecs consécutifs et le budget de délai
commun aux tentatives. Quota, authentification et trames invalides ne déclenchent
pas cette reprise de transport.

Deux parties réelles avec Luna medium ont également réussi : prendre la clé
dans la crypte et prendre la ficelle dans l'atelier. Huit appels terminés,
une ouverture et une fermeture par partie ; les quatre rôles successifs partagent
chaque connexion. Les récits sont enregistrés avant affichage, puis l'état complet
et l'inventaire sont vérifiés après reprise hors ligne. Ce contrôle valide
l'intégration ; il ne mesure pas un nouveau gain de latence.

Après ajout de la reconnexion transparente, deux autres parties réelles ont
réussi avec une coupure volontaire après `output_item.done` et avant lecture
du terminal de la première réponse. Dix demandes envoyées, deux réponses
volontairement perdues et huit terminées ; quatre ouvertures et fermetures,
soit une connexion initiale et une reconnexion par partie. Les deux actions
ont un seul commit moteur, sont sauvegardées avant affichage et conservées
après reprise. Voir [verification-websocket-reconnexion.json](verification-websocket-reconnexion.json).

Une première passe réelle s'était arrêtée après la crypte sur une assertion
trop étroite du vérificateur : elle exigeait une proposition simple `prendre`.
Le contrôle compte désormais les commits moteur, indépendamment de la forme
simple ou composée du plan. Les quatre autres réponses de cette passe étaient
terminées, et la possession, la sauvegarde et la reprise étaient déjà vérifiées.
Cette passe et ses deux ouvertures sont conservées séparément dans l'export.
Total du contrôle réel de reconnexion : six ouvertures, 15 demandes dont trois
réponses volontairement perdues, 12 terminées. Aucune règle du jeu ni instruction
du modèle n'a été changée pour satisfaire le contrôle.

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

Ajouter `--simuler-coupure` pour vérifier la reprise transparente avant un
terminal réel dans chacune des deux parties.

Références de protocole : [WebSocket Responses](https://developers.openai.com/api/docs/guides/websocket-mode)
et [limites de Sign in with ChatGPT](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
