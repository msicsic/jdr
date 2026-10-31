# Tâche Codex 423 : « prendre une planche » ne prend pas le tas entier par la saisie libre

Limite relevée par la passe Luna du lot 422 (G13, fusionné ; `docs/taches/rapport-codex-422-g13-qualification.md`,
script `tests/data/bancs/lots.json`). Le joueur demande une pièce d'un lot, et Luna propose `deplacer` du lot entier.
La revue de fidélité refuse ; la correction `prelever` est alors rejetée par la reprise fidèle d'A5 (lot 415), qui
conserve l'opération `deplacer`. Enfin une revue admet le déplacement du tas entier. Le joueur reçoit tout le tas au lieu
d'une planche. Bruts : `C:\Users\msics\donjon\artifacts\g13-qualification-422\` (PC fixe).

Le contrat des lots est ancien (lot 78 : nom de pièce, quantité et unité ; opération `prelever` qui réemploie les règles
de `deplacer`). La forme A du compilateur (A0 à A6) est fusionnée.

Lis `AGENTS.md` (contrat du MJ, « Fidélité de la saisie »), `docs/etat-dev.md` (court), les rapports 415, 416 et 422.
Pour le lot 78, cherche « pièce de lot » dans `docs/historique-lots.md`.

## Invariant (un seul)
**Une demande sur une pièce d'un lot (quantité, unité, nom de pièce) produit `prelever` de cette pièce, jamais
`deplacer` du lot entier. Quand une revue de fidélité refuse une opération qui ne respecte pas la quantité demandée,
la reprise fidèle (A5) laisse corriger l'opération et la quantité que le refus met en cause, sans rouvrir le reste.**
Le déplacement du lot entier n'est admis que si la saisie le demande.

Établis d'abord sur la base d'avant A4–A6 (`origin/integration` d'avant `b1d74a71`, sur copie) si le même script donnait
`prelever`. Le défaut est-il ancien (typage de Luna) ou apporté par la reprise A5 ? Corrige le contrat commun : la liste
des champs corrigeables d'un refus de quantité, et/ou la définition commune de `prelever` et `deplacer` donnée à Luna.
Aucun mot-clé ni exception de scénario.

## Vérification
`test_lots` (ou le fichier du 78), `test_reprise_fidele`, `test_dossier_revue`, `test_qualification` ; cas réel (le
script `lots`, une planche) et autre cas (une part de bois, une bûche d'un fagot) dans la vraie boucle, avec MJ simulé
et recharge : une pièce prélevée, le lot diminué, la quantité exacte. **Luna : une passe ciblée** sur copies, `lots` et
`ressources`. Si la revue automatique la bloque ou si le coffre est illisible sur ce poste, laisse la commande exacte
dans les bruts. Pas de suite complète.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/comprehension.py`, `donjon/mj.py`, les contrats de famille,
`donjon/operations.py`, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 419 (vérification de
contact). Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs
détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-piece-de-lot-libre`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-423-piece-de-lot-libre.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\piece-de-lot-423\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
