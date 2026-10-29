# Tâche Codex 308 (diagnostic) : les portions servies en moins et l'alerte de Gorm au Relais après le lot 303

Diagnostic seul, **aucun code du jeu modifié**. Lis `AGENTS.md`, le rapport
`docs/taches/rapport-codex-303-service-rejoindre.md` et ses bruts `C:\Users\msics\donjon\artifacts\service-303\`
(comparaison de douze nuits, `analyse-alertes.json`).

## Le constat
Le lot 303 (fusionné) prépare le contact avant un service à un participant de lieu inconnu. Sur douze nuits de 4 h, les
portions servies passent de 33 à 30, dont **Relais 5 → 3**. Les questions de localisation passent de 50 à 88, les appels
de 34 à 43 et les dérives ouvertes de 162 à 186. Relais 7 ajoute un constat `but_hors_besoin` : Gorm va auprès d'Aubin
alors que ses biens le pressent. Ce constat n'a pas été certifié bénin.

## La question
Pour chaque portion perdue et pour le constat de Gorm, établis la cause et dis si c'est le comportement attendu par
l'invariant du 303, ou un défaut :

- **comportement attendu** : contact cherché avant le service, au lieu d'un geste refusé sur place ;
- **défaut** possible, par exemple :
  - un contact qui ne se conclut jamais ;
  - une charge qui perd son parent ;
  - une recherche qui préempte à tort un besoin plus pressant.

Compare chaque nuit à sa référence `79beaf1`, en cache, et localise le premier écart. Rejoue les captures avant et après
l'écart, sur le code actuel et sur la base. Pour les questions et les dérives en hausse, dis si elles sont des contacts
légitimes ou des répétitions sans entrée nouvelle (classes de la sonde 219 et 271).

## Vérification
- Captures : monde, rendu et scène identiques après recharge.
- Un processus à la fois, priorité réduite. Pas de Luna, ni de suite complète, ni de banc comparatif nouveau au-delà des
  nuits nécessaires. Calcul long détaché avec un fichier de fin.

Si un défaut est établi, propose le petit lot de correction : l'invariant et les fonctions en cause. Ne le code pas.

## Contraintes
**Poste : le laptop**, où tournent une vérification d'intégration et un lot du MJ.

## Livraison
- Branche `codex-services-apres-303`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur :
  la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-308-services-apres-303.md`.
- Entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\services-308\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
