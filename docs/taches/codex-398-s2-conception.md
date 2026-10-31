# Tâche Codex 398 : préparation de S2, découper les bascules en lots d'un invariant

Lot de conception, documentation seule, comme S0 (lot 373). S2 est l'étape « dossier et compte des échanges ; axes
calculés depuis le dossier (réparation, trahison, repentir) » du [plan de l'esprit social](../plan-esprit-social.md)
(§ 11, étape notée E2 dans le plan, S2 dans `docs/etat-dev.md`). S1 est en cours (S1a à S1e fusionnés, S1f en
vérification, S1g à S1p à venir).

Lis `AGENTS.md`, `docs/etat-dev.md` (court, dont « Questions de S0 » dans les décisions du 2026-10-30), le plan de
l'esprit social en entier, la [conception S0](../conception-memoire-unifiee.md) (§ 5 « Frontière avec S2 » et § 8) et
son annexe d'accès, et les rapports 373 et 378 à 385.

## Invariant (un seul)
**Chaque bascule de S2 devient un lot d'un seul invariant, avec ses données de départ, ses oracles lisibles, son cas
réel et un autre cas, et sa mesure (banc rapide 4 h) ; les cinq décisions de S0 y sont reportées telles que tranchées.**
Rappel des décisions :
1. rétention selon l'importance et l'âge ;
2. héritage minimal : une attitude sans acte devient « héritée, cause inconnue », non compensable ;
3. seul un acte rattaché au tort le compense ;
4. deux ouï-dire contradictoires de même force : incertitude racontable, vérification si l'action l'exige ;
5. le grief alimente la bande de refus, la colère seulement l'expression et l'urgence.

Le livrable contient :
- la liste ordonnée des sous-lots de S2. Au minimum : rétention âge/importance ; révision commune des faits (dont la
  décision 4) ; compte subjectif des échanges et dossier par personne ; axes dérivés du dossier, avec réparation,
  trahison et repentir (décisions 2 et 3) ; séparation colère/grief (décision 5). Pour chacun : fichiers attendus,
  dépendances, risques et critères de fusion ;
- ce qui dépend de S1g à S1p (champ par champ), pour dire quels sous-lots peuvent partir avant la fin de S1 ;
- la place d'E7 et de l'essai borné d'E9 après S2 (décision du placement du 2026-10-30), et ce que S2 doit leur
  fournir ;
- une mesure de la tranche verticale : l'auberge, avec des biographies écrites à la main, et les scènes à capturer.

Aucune ligne de code. Les briefs eux-mêmes restent au superviseur.

## Vérification
Relecture : chaque sous-lot tient en 30 à 45 minutes et porte un seul invariant ; chaque référence de fichier ou de
fonction citée existe (cite le chemin) ; aucune décision nouvelle n'est prise à la place de l'utilisateur. Les
questions ouvertes sont listées avec une recommandation.

## Contraintes
**Poste : le laptop.** Documentation seule ; aucun test, banc ni Luna. Lots en cours : 381 (A2 passage), 396 (U-T
social comptes), 397 (S1f). La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de
l'utilisateur) est autorisée.

## Livraison
- Branche `codex-s2-conception`, base `integration`, poussée vers origin.
- Document `docs/conception-s2.md` ; rapport d'une page `docs/taches/rapport-codex-398-s2-conception.md` ; entrée « non
  fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Termine par `LOT TERMINÉ` ou `QUESTION : …`.
