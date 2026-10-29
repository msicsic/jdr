# Tâche Codex 336 : A6, l'occasion : offrir sa protection contre paiement

Suite d'A6 du [plan des agendas](../plan-agendas.md), § 6.5 (« une occasion : un PNJ voit qu'un autre a besoin de
ce qu'il peut offrir et que cela vaut pour lui ») et cas 3 du tableau (« un combattant cupide devient mercenaire »).
Lis `AGENTS.md`, `docs/etat-dev.md`, puis les rapports 184 (table des naissances, dette), 192 (naissance par
événement), 167 c (agenda `protéger`), 115 (tâche promise) et 330 (cause de la détresse).

## Constat
La table des naissances ne connaît que la dette et le portage illégitime constaté. Un PNJ qui perçoit la peur d'un
autre (signe ou impression, cause crue) et qui croit cet autre solvable ne lui propose jamais sa protection, même
quand son caractère s'y prête (ambition, courage, force crue). L'auberge déclare pourtant Hugues, ancien soldat, et
Anselme, marchand inquiet pour son ballot.

## L'invariant
**Une occasion fait naître une offre de protection par la table commune des naissances.** Le PNJ croit qu'un autre
craint un danger (signe, impression ou cause apprise ; jamais son état privé). Il croit pouvoir le protéger
(courage, force crue, disponibilité). Il croit le paiement possible (pièces crues de l'autre) et digne de la peine,
selon ses valeurs et la valeur commune de la pièce. Il propose alors sa protection contre paiement par la
proposition commune. L'autre la juge par l'évaluation commune ; s'il accepte, un agenda `protéger` d'origine
`contrat` naît chez le protecteur, payé et tenu par le contrat commun des tâches, avec sa fin (échéance, danger
passé, mort ou départ cru). Un refus est retenu selon sa cause, sans offre redite par le seul délai. Sans peur crue,
sans moyens crus ou sans intérêt, aucune offre. Le joueur peut être le destinataire.

## Contraintes de conception
- Une entrée de la table des naissances et la proposition commune : pas de cas propre à Hugues, Anselme ou
  l'auberge, ni de donnée de scénario ajoutée pour provoquer l'occasion.
- Un invariant : l'offre de protection. Les autres occasions (débauche, travail cherché) sont hors lot.
- Toute lecture nouvelle de la recherche entre dans `_entrees`.

## Vérification
- Une scène à l'auberge (Hugues voit Anselme inquiet et solvable, offre, acceptation, protection tenue puis payée)
  et un autre cas de même nature dans un autre scénario. Cas négatifs : pas de peur crue, demandeur insolvable cru,
  refus retenu, offre jugée sans intérêt. Contrôle après rechargement du monde, du rendu et de la scène, avec le même
  laps entier ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Banc rapide 4 h × cinq scénarios × quatre graines, références lues du cache : aucune hausse des suspects 219 par
  nuit, zéro plantage ou usurpation ; offres, acceptations et protections nées dans les nuits.
- Ni Luna ni suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Banc détaché, avec un fichier de fin écrit en
dernier. Recouvrements possibles avec les lots 333 (garder un lieu) et 335 (suivi vocal de `protéger`), en cours :
signale tout fichier commun.

## Livraison
- Branche `codex-occasion-protection`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-336-occasion-protection.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\occasion-336\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
