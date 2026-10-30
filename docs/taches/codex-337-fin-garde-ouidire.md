# Tâche Codex 337 : A4b, la fin de garde apprise par ouï-dire

Dernier reste d'A4b sur `garder` ([plan des agendas](../plan-agendas.md), paragraphe « Reste l'ouï-dire », après
le lot 179). Lis `AGENTS.md`, `docs/etat-dev.md`, puis les rapports 175 (fin sur destruction ou consommation
constatée), 179 (transferts constatés, ébauche d'ouï-dire retirée) et 55 (constats partagés par les nouvelles).

## Constat
Un gardien met fin à `garder` sur ce qu'il constate lui-même : bien remis à qui de droit, rendu au propriétaire,
perdu aux mains d'un tiers sans permission, détruit ou consommé. Il ne le fait jamais sur ce qu'on lui en dit.
L'ébauche du lot 179 a été retirée pour une raison précise : l'identité d'un fait transmis pouvait être masquée par
une ancienne accusation de portage, dépourvue des droits datés nécessaires.

## L'invariant
**Les propriétés qui terminent une garde (porteur, droits datés, fin d'objet) se transmettent par la voie commune
des nouvelles, comme les constats du lot 55.** Elles portent leur date d'observation, leur source et leur poids de
ouï-dire. Leur identité de fait est distincte de celle d'une accusation de portage : une ancienne accusation ne la
masque pas et ne la remplace pas. Le gardien qui croit la nouvelle, par la confiance commune, termine `garder` avec
la même cause et la même publication différée qu'un constat propre. Une preuve propre plus récente ou plus forte
prime, et une nouvelle fausse peut être crue. Aucune permission n'est inventée depuis l'état réel à la réception.
Si le joueur n'a pas les relations subjectives nécessaires, dis-le comme une limite et traite les PNJ.

## Contraintes de conception
- Contrat commun des nouvelles (`social`) et de la croyance de possession (`esprits.constater_possession`) ; pas de
  cas propre à un bien, un personnage ou un scénario.
- Pas de nouvelle parole automatique ajoutée si elle n'est pas nécessaire à l'invariant ; dis ce que tu ajoutes.
- Toute lecture nouvelle de la recherche entre dans `_entrees`.

## Vérification
- Une scène où un tiers voit le bien d'une garde passer à un autre sans permission puis le dit au gardien, qui met
  fin à sa garde (ou qui doute s'il ne le croit pas) ; un autre cas de même nature : remise au propriétaire, ou
  destruction, dans un autre scénario. Cas négatifs : ancienne accusation de portage présente, preuve propre plus
  récente, nouvelle non crue. Contrôle après rechargement du monde, du rendu et de la scène, avec le même laps
  entier ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Empreintes 2 h (cinq scénarios, quatre graines, références lues du cache) si les nuits ne doivent pas changer ;
  sinon banc rapide 4 h, avec aucune hausse des suspects 219 par nuit.
- Ni Luna ni suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Calcul détaché, avec un fichier de fin écrit en
dernier. Recouvrements possibles avec les lots 335 (suivi vocal) et 336 (occasion de protection), en cours :
signale tout fichier commun.

## Livraison
- Branche `codex-fin-garde-ouidire`, base `integration`, poussée vers origin
  (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-337-fin-garde-ouidire.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\garde-337\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
