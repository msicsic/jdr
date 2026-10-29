# Tâche Codex 335 : A4b, protéger en restant à portée de voix

Suite d'A4b du [plan des agendas](../plan-agendas.md). Ligne `protéger` du tableau des sortes : « être à portée de
voix de lui ». Lis `AGENTS.md`, `docs/etat-dev.md`, puis les rapports 167 c (`protéger` sur agenda) et 266
(rester près d'un proche en détresse : terminal de proximité). Lis aussi la règle d'ouïe commune
(`ouie.s_entendent`, `docs/plan-ouie.md`).

## Constat
Sans poste d'interposition, un agenda `protéger` dort avec la raison `suivi vocal non pris en charge`. Le
protecteur ne suit pas son protégé et ne se tient pas à portée de voix. Il ne l'entend donc pas appeler, alors que
répondre à son appel est déjà la règle (rapport 167 c). Le rapport 167 c écarte deux faux remèdes : rejoindre
seulement la salle, ou détourner une parole.

## L'invariant
**Un protecteur dont l'agenda `protéger` est actif se tient là où, selon ses seules croyances, il entendrait la
voix de son protégé : terminal commun de proximité vocale, calculé par la même règle d'ouïe que la parole
(distance, ouvertures, portes fermées).** Il s'y rend par la marche commune, avec le coût de ses trajets, et cède
à tout palier supérieur selon l'échelle commune. Le protégé perdu de vue est recherché par les moyens communs
(inspection, appel, question), sans jamais lire sa position réelle. L'agenda ne dort plus pour cette raison. Sa
fin sur mort ou départ cru, déjà livrée, reste inchangée. Il n'y a ni oscillation sur une portée limite, ni
déplacement à chaque pas du protégé sans entrée nouvelle.

## Contraintes de conception
- Réutilise le terminal de proximité du lot 266 et la règle d'ouïe ; pas de nouvelle distance en dur ni de cas
  propre à un personnage ou un scénario.
- Les épreuves déclarent leurs agendas `protéger` en données de tests (lots 167 b et 167 c). Aucun agenda
  historique ajouté aux scénarios.
- Toute lecture nouvelle de la recherche entre dans `_entrees`.

## Vérification
- Une scène où le protégé change de salle et où le protecteur se replace à portée de voix, puis répond à son appel
  ; un autre cas de même nature dans un autre scénario. Cas négatifs : protégé perdu de vue (recherche commune),
  palier supérieur prioritaire, portée limite sans oscillation. Contrôle après rechargement du monde, du rendu et de
  la scène, avec le même laps entier ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Banc rapide 4 h × cinq scénarios × quatre graines, références lues du cache : aucune hausse des suspects 219 par
  nuit, zéro plantage ou usurpation. Les nuits sans agenda `protéger` déclaré doivent rester identiques ; dis-le si
  elles changent.
- Ni Luna ni suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Banc détaché, avec un fichier de fin écrit en
dernier. Recouvrement possible avec les lots 330 (3d, demander la cause) et 333 (garder un lieu), en cours :
signale tout fichier commun.

## Livraison
- Branche `codex-suivi-vocal`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-335-suivi-vocal.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\vocal-335\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
