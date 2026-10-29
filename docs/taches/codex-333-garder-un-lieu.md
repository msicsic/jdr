# Tâche Codex 333 : A4b, s'interposer devant un lieu gardé

Suite d'A4b du [plan des agendas](../plan-agendas.md) (« interposition d'un lieu », restée ouverte depuis les lots
167, 167 b, 167 c, 175 et 179). Lis `AGENTS.md` et `docs/etat-dev.md`, puis les rapports 167 (interposition sur
approche d'une charge), 167 b (sorte `garder` objet/lieu) et 194 (porte d'un lieu gardé).

## Constat
`defense.interposition` ne protège que des **objets** (`charges` : biens gardés et protégés). Un gardien dont la
charge est un **lieu** (`garder` d'un lieu, poste déclaré, réserve sans objet nommé) ne s'interpose jamais devant
l'entrée quand un personnage dont il se méfie, ou dont il a lu le guet, s'en approche. Il ne le met pas non plus en
garde.

## L'invariant
**L'interposition d'un gardien porte sur toute charge crue, objet ou lieu, par la même règle.** Quand une approche
vue d'un personnage suspect (méfiance, guet lu) mène vers l'accès d'un lieu gardé, le gardien occupe la case
d'accès (le passage ou le seuil entre l'approchant et le lieu) sans violence, par la marche commune. Il le met en
garde par la parole typée existante. S'il persiste, l'épreuve relationnelle commune s'applique (méfiance, rancune).
Il n'y a ni déplacement rétroactif, ni lecture d'une intention privée, ni répétition de l'avertissement sur une
même approche. Une case d'accès occupée ou inaccessible ne déclenche rien. Le joueur peut être l'approchant.

## Contraintes de conception
- Étendre la règle commune (`charges`, `interposition`, `approche_vue`), sans branche par type de charge propre à
  un personnage ou un scénario.
- Les épreuves déclarent leurs gardes de lieu en données de tests, comme aux lots 167 b et 167 c. Aucun agenda
  historique ajouté aux scénarios.
- Toute lecture nouvelle de la recherche entre dans `_entrees`.

## Vérification
- Une scène où un gardien tient l'accès d'une réserve ou d'une salle contre un suspect qui s'approche, et un autre
  cas de même nature dans un autre scénario. Cas négatifs : approchant non suspect, approche non vue, case d'accès
  occupée, même approche sans nouvel avertissement. Contrôle après rechargement du monde, du rendu et de la scène,
  avec le même laps entier ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Changement de comportement : banc rapide 4 h × cinq scénarios × quatre graines, références lues du cache. Aucune
  hausse des suspects 219 par nuit, zéro plantage, usurpation ou coup.
- Ni Luna ni suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Banc détaché, avec un fichier de fin écrit en
dernier. Recouvrement possible avec les lots 330 (3d, demander la cause) et 332 (attention conjointe), en cours :
signale tout fichier commun.

## Livraison
- Branche `codex-garder-lieu`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-333-garder-un-lieu.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\lieu-333\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
