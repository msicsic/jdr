# Tâche Codex 332 : 3d, l'attention conjointe

Suite de la sous-étape 3d (l'empathie) du [plan des relations](../plan-relations.md), signalée comme restant à
faire depuis le lot 53 (« suivre le regard d'un autre »). Lis `AGENTS.md`, `docs/etat-dev.md` et les rapports 53
(peur transmise), 11 (signes, relations 3c) et 266 (rester près d'un proche en détresse).

## Constat
Un PNJ qui voit un proche fixer une direction avec un signe de peur ou d'alerte ne regarde jamais lui-même de ce
côté. Il ne perçoit donc pas ce qui inquiète son proche, alors que ce danger serait dans son propre champ s'il se
tournait. `signes.regarder` donne déjà un regard daté et orienté dans l'intention de celui qui regarde.

## L'invariant
**Un PNJ qui perçoit le regard d'un proche (signe émis et perçu par la règle commune des signes) peut tourner son
propre regard dans la direction perçue, avec le coût de rotation commun. Il perçoit ensuite par sa seule vue : il
ne voit que ce que son champ, sa lumière et ses lignes de vue lui donnent. Il n'apprend jamais ce que l'autre voit
s'il ne le voit pas lui-même.** Une seule réorientation par regard perçu, sans recommencer par le seul délai. Un
regard non perçu (dos, noir, inconscient) ne déclenche rien. Le joueur suit la même règle s'il observe un regard ;
sinon, dis-le comme une limite.

## Contraintes de conception
- Passe par la perception commune et `signes`, sans cas propre à un personnage ou un scénario.
- Le coût de perception est à mesurer (le plan l'a signalé). Toute lecture nouvelle dans la recherche entre dans
  `_entrees`.
- Recouvrement probable avec le lot 330 (3d, demander la cause, en cours sur le PC fixe) : signale tout fichier
  commun et garde la règle commune.

## Vérification
- Une scène réelle où un proche fixe un agresseur ou l'eau hors du champ de l'observateur, qui se tourne et voit,
  et un autre cas de même nature dans un autre scénario. Cas négatifs : regard non perçu, cible hors de vue même
  après rotation, regard déjà suivi. Contrôle après rechargement du monde, du rendu et de la scène, avec le même
  laps entier ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Banc rapide : 4 h × cinq scénarios × quatre graines, références lues du cache. Aucune hausse des suspects 219 par
  nuit, zéro plantage ou usurpation. Mesure des regards suivis et du coût CPU de la nuit (branche seule).
- Ni Luna ni suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Banc détaché, avec un fichier de fin écrit en
dernier.

## Livraison
- Branche `codex-attention-conjointe`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-332-attention-conjointe.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\regard-332\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
