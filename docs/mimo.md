# Xiaomi MiMo dans Le Seuil

L'adaptateur est disponible sur `refactor/adaptateurs-fournisseurs`, sans fusion dans `main`.
Il utilise `mimo-v2.6-flash` par choix explicite. Luna reste le MJ par défaut et la comparaison reste désactivée.

La [campagne complète avec cet adaptateur](mimo-campagne-complete.md) est maintenant terminée :
90 saisies, 38 tours MJ, 120 requêtes réelles, sept rejets de format tous corrigés et aucun tour
en erreur technique. TTFT médian : 2,18 s. Un défaut sémantique reste confirmé : le modèle ajoute
des idées à une parole du joueur, que le jeu accepte et enregistre. Les quatre reprises sont vérifiées.

## Jouer

Installer les dépendances facultatives dans l'environnement Python utilisé pour jouer :

```powershell
python -m pip install -r requirements-mimo.txt
python jeu.py --connexion mimo --console --save sauvegardes/mimo.json
```

Renseigner `MIMO_API_KEY` dans l'environnement ou dans le `.env` local du worktree. `XIAOMI_API_KEY` est également reconnu,
avec priorité à `MIMO_API_KEY`. La clé OpenAI et la connexion ChatGPT ne servent jamais à authentifier Xiaomi.
Le fichier de clé utilisé pour les essais n'est pas copié dans le projet.

Ce mode choisit `mimo-v2.6-flash` et `--effort none`, indépendamment de `OPENAI_MODEL`.
`--model` permet un choix explicite. Les niveaux `low`, `medium` et `high` activent tous la réflexion MiMo ;
ce sont les deux états enabled/disabled du protocole Xiaomi, sans trois intensités distinctes.
Sans `--connexion mimo`, le comportement de sélection du fournisseur reste celui du jeu.
`--offline` interdit les appels, y compris avec une clé présente.

## Contrat de réponse

Les instructions métier et les schémas viennent du MJ commun. L'adaptateur ajoute uniquement le contrat de transport JSON :
`response_format: {"type": "json_object"}`, arguments de la fonction à la racine et schéma transmis dans le message.
Il n'utilise pas de canal outil et ne transforme pas les données en inventant un champ ou une valeur.
JSON est décodé strictement : doublons, NaN, texte après l'objet et non-respect du schéma sont refusés.

Une réponse complète qui échoue à cette validation peut être renvoyée **une fois** au modèle, avec sa sortie exacte et le diagnostic.
Le fournisseur ne soumet aucun de ces objets au moteur avant validation. Si la correction échoue, le joueur reçoit une erreur neutre.
Cette relance concerne le contrat de sortie. Le MJ et le moteur conservent ensuite leurs propres contrôles et leurs boucles métier.
La correction de format ne prouve pas que le modèle a conservé exactement le sens de sa première sortie ; les arguments et les deux
messages restent disponibles pour audit. Le défaut du saut à la perche observé dans la première
campagne n'est pas reproduit dans la nouvelle passe ; la fidélité sémantique reste partiellement garantie.

L'adaptateur distingue une erreur JSON d'un flux invalide ou incomplet : une coupure, un terminal manquant, une sortie tronquée
ou un refus ne déclenchent pas cette correction. Un HTTP 401 coupe les appels de la session ; aucune bascule vers un autre fournisseur.

## Transport et traces

La connexion HTTPS Xiaomi utilise IPv4 par défaut, avec le nom d'hôte et la vérification TLS habituels.
La sélection IPv4 est limitée à cette connexion : aucune modification de `socket.getaddrinfo` ni du système.
Les redirections HTTP sont refusées pour conserver la clé sur la destination prévue.
Le délai de la demande est partagé entre ses deux tentatives éventuelles et les lectures du flux.

Le lecteur SSE gère les commentaires, CRLF et événements répartis sur plusieurs lignes. Il exige `finish_reason=stop`,
le terminal `[DONE]` et une lecture à EOF. Une erreur de protocole conserve aussi les octets suivants, jusqu'à EOF ou au délai/volume maximal.
Le flux est limité à 4 Mo ; une capture interrompue par cette limite est marquée comme telle.

`brut.tentatives` conserve chaque requête sans en-têtes, les événements horodatés, le message reconstruit, les diagnostics,
la consommation et les octets SSE exacts en base64. Les coûts des deux tentatives sont additionnés.
`--debug` conserve les traces du jeu ; le banc ci-dessous écrit toutes les captures sur disque au fur et à mesure.
La clé et les en-têtes d'authentification ne sont pas journalisés.

Le TTFT mesuré attend le premier contenu JSON non vide après le début de l'envoi. Le premier événement SSE et le premier
contenu de réflexion ont leurs propres mesures. Le délai avant le texte final au joueur comprend l'ensemble des appels et contrôles.

## Banc raccordé au fournisseur du jeu

Le banc réutilise `banc_parties.jouer`, les scripts et les boucles réelles. Il injecte le même `MiMo` que celui du jeu,
sans surcharge d'une méthode OpenAI ni copie de transport. Il enregistre les états après chaque saisie et vérifie la reprise.
Le plafond porte sur les appels physiques, corrections comprises ; les appels MJ sont comptés séparément.

```powershell
python tools/valider_mimo_parties.py --cle-fichier '<fichier local de clé Xiaomi>' --sortie artifacts/mimo-campagne --max-appels 150
python tools/rapport_validation_mimo.py artifacts/mimo-campagne
```

Sans script indiqué, les quatre scripts Relais, Crypte, Atelier et Échanges sont joués.
Pour la mesure stricte comparable à la première campagne, utiliser `--relances-format 0`.
`--effort medium` active la réflexion ; `--ipv6-autorise` laisse le système choisir les adresses pour Xiaomi.
`--offline` fait le prévol sans réseau. Les deux scripts `mimo-simple-crypte.json` et `mimo-simple-atelier.json`
permettent un essai court sur deux ramassages, sans changer les règles ni les instructions.

Le lanceur standard `banc_parties.py --connexion mimo --fil` accepte aussi le fournisseur, avec les compteurs MJ habituels.
Pour borner les corrections en appels physiques et conserver les fichiers SSE séparés, employer `valider_mimo_parties.py`.

## Vérifications de cette finition

- **998 tests passent**, avec les dépendances facultatives Anthropic et MiMo présentes.
- Les 112 captures de la grande campagne sont rejouées sans réseau et sans relance : mêmes requêtes,
  mêmes arguments acceptés, 106 réponses conformes et les mêmes six rejets.
- La correction de format est vérifiée sur deux scènes complètes avec réponse réseau simulée : cinq appels physiques,
  quatre appels MJ, une seule action exécutée, narration sauvegardée avant affichage et état conservé après reprise.
- Les deux rejets réellement capturés sont aussi rejoués par le nouvel accès `--connexion mimo`, avec épuisement de la correction :
  aucun changement de monde ni fuite du diagnostic au joueur, puis sauvegarde et reprise vérifiées.
- Les quatre scripts existants terminent le prévol hors ligne : 90 saisies, aucun appel et aucun échec de rechargement.

Deux essais **réels** Xiaomi, réflexion désactivée, ont ensuite réussi :

| Scène | Résultat moteur | Appels physiques | Durée du tour MJ |
|---|---|---:|---:|
| Crypte | Clé prise, une seule exécution, inventaire et reprise corrects | 4 | 21,4 s |
| Atelier | Ficelle prise, une seule exécution, inventaire et reprise corrects | 4 | 11,8 s |

Aucune erreur, correction de format ou substitution de narration sur ces deux essais.
Sur les huit appels : TTFT médian **2,03 s**, réponse complète médiane **4,52 s**, zéro token de réflexion déclaré et aucun contenu de réflexion reçu.
Ce petit essai confirme le raccord technique sur ces actions ; il ne mesure pas la fiabilité générale de la narration.
À ce stade de l'essai court, la correction de format était vérifiée avec des réponses simulées.
La campagne complète ultérieure vérifie maintenant sept corrections réussies sur le service réel.
Un essai supplémentaire distinct sur les six rejets antérieurs avait été refusé par le contrôle automatique d'autorisation, qui jugeait
le renvoi des contextes et sorties capturés insuffisamment autorisé. Aucun de ces six appels n'a été envoyé.

[Résultats structurés](verification-mimo-fini/resultats.json) · archive complète des deux essais réels : `artifacts/mimo/essai-reel.zip`, non versionnée

Décompresser l'archive et ouvrir `index.html` pour les messages, prompts, validations et sauvegardes.
Les empreintes SHA-256 permettent de vérifier les fichiers de la campagne et la version de code copiée avant les appels.

Sources du protocole : [JSON natif Xiaomi](https://mimo.mi.com/docs/en-US/quick-start/usage-guide/text-generation/structured-output),
[modèle et réflexion désactivée](https://mimo.mi.com/models/en-US/mimo-v2.6-flash).
