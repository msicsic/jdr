# Tâche Codex 346 : A1, la projection publique avec provenance

Premier lot de la reprise de G1 sous la forme A, décidée par l'utilisateur. Lis `AGENTS.md` (contrat du MJ),
`docs/conception-g1.md` (sections 2.1, 5 A et 6 en entier), `docs/plan-refonte-mj.md`, puis les rapports 318 et
324 (oracle A0, fusionné : `tools/oracle_g1.py`, `tests/data/oracle_g1.json`). La branche `origin/codex-g1-compilateur`
(lots 294/296/304/311, non fusionnée et suspendue) sert seulement de contre-exemple : elle a retiré des données utiles.

## Le constat
Le compilateur compact du G1 réduisait le contexte d'interprétation et a perdu des données dont Luna avait besoin.
Exemple établi : `relais/4` au 294, `faits.evenements_recents` retiré, la preuve de l'examen de la gravure au tour
précédent avait disparu, alors que la consigne exacte et la conversation restaient. La forme A part de l'inverse :
aucune dépendance utile supprimée, seuls les secrets et les doublons à l'équivalence prouvée sont exclus.

## L'invariant
**Toute donnée publique que l'interprétation actuelle reçoit pour une saisie libre a un équivalent dans une
projection publique, chacune avec sa provenance (perception actuelle, souvenir daté hors de vue, parole entendue,
événement récent du joueur, fait établi par le moteur, connaissance déclarée), calculée de façon déterministe sur
les seules données perceptibles ou connues de Corvus.** Une donnée sans provenance n'y entre pas ; un faux souvenir
(jamais perçu, jamais entendu) n'a pas d'équivalent. Aucune réduction sémantique : ce lot ne trie ni ne résume la
conversation.

## Périmètre
- Une fonction de projection (module au choix, par exemple à côté de `sources.py`) et sa preuve de couverture.
  **Elle n'est pas branchée sur l'interprétation dans ce lot** : le raccord est le lot A6. Ne change ni les consignes,
  ni le schéma d'action, ni les revues, ni `mj.py` hors d'une lecture.
- Couverture prouvée par un test : pour chaque requête d'interprétation archivée du corpus de l'oracle A0
  (30 tours MJ des six scripts G1, références lues, aucun appel au modèle), chaque donnée publique de l'entrée
  actuelle se retrouve dans la projection avec une provenance ; les seules exclusions sont nommées (secret, doublon
  prouvé équivalent). Une exclusion non justifiée fait échouer le test.
- Cas : `relais/4` (texte connu de la gravure et preuve de l'examen précédent) et un autre support connu ; un
  souvenir hors de vue (objet ou personne vus ailleurs, désignation et date conservées, sans position actuelle) ; un
  faux souvenir absent ; état, projection et rendu identiques après sauvegarde et recharge.
- Aucune entité non perçue, identité privée ou agenda secret dans la projection (réutilise les projections publiques
  existantes, `personne_<n>`, désignations).

## Vérification
Tests ciblés des fichiers touchés et de l'oracle A0 ; pas de Luna (aucun chemin du modèle n'est changé), pas de
suite complète, pas de banc PNJ. Mesure dans le rapport : taille de la projection contre l'entrée actuelle, nombre
d'exclusions par motif.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Lots en cours : 341 (mandat du joueur, `paroles.py`),
342 (attribution du groupe 1, tests), 344 (U-M corps, `web/`), 345 (G16, `paroles.py`, `dialogues.py`, `narration.py`) :
signale tout fichier commun. Si l'invariant exige de modifier l'entrée actuelle de l'interprétation, arrête-toi et
pose la question.

## Livraison
- Branche `codex-a1-provenance`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-346-a1-provenance-publique.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\a1-346\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
