# Tâche Codex 60 : un rendez-vous se clôt pour les deux, et l'appelant cesse de chercher

Branche `codex-rendez-vous` (elle porte ce fichier, issue de l'intégration **c592d68**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna.

Lots en même temps : 58 sur ce même poste (`planification.py`, `route_admissible.py`, `pnj._marcher`) ; un lot du MJ
sur l'autre poste. Ce lot touche `donjon/appel.py` et, s'il le faut, `deliberation._attendre_qui_vient` ; pas
`planification.py`. Les lots 56, 57 et 59 (comptes, offres, parole sans contenu) arrivent dans l'intégration pendant
ton lot : fais `git merge origin/integration` au début si elle a avancé.

Lis `AGENTS.md`, `docs/etat-dev.md` (**« Vérification d'intégration 5c2ce81 », défaut (3)** ; entrées `appel-negocie`,
`codex-chercher-appeler` lot 37), `docs/plan-ouie.md` (« L'appel négocié »), puis `donjon/appel.py` (`rejoint`,
`rejoindre`, « comme convenu », « Me voici ! », fin de l'attente), `donjon/deliberation.py` (`_attendre_qui_vient`,
`appels_vains`, `indice_recherche`). Bruts : `C:\Users\msics\donjon\artifacts\verif-integ-5c2ce81\extraits.txt`
(auberge 42, minutes 501-506, lignes ~140-170) et `audit-12h\auberge_42.json.gz`.

## Le constat (audit 12 h de l'intégration 5c2ce81)
Auberge 42, 501-506 : Anselme hèle « Odile ? » dix fois et Odile répond cinq fois « J'arrive ! » ; la chronique
écrit cinq fois « Odile retrouve Anselme, comme convenu » pendant qu'ils se croisent entre le cellier et la cuisine.
Retrouvailles redites à moins de dix minutes : 0 → 1 → 5 à l'auberge sur quatre graines. Cause probable : la fin du
rendez-vous est actée par l'appelée seule ; l'appelant ne la reçoit pas et reprend sa recherche.

## L'invariant
**Un rendez-vous convenu se clôt pour les deux à la même condition** (ils se voient ou se parlent), dans l'esprit de
chacun (`rejoint` de l'un, `rejoindre` de l'autre), et l'appelant qui l'a obtenu cesse de chercher et de héler celui
qu'il a retrouvé ; « retrouve …, comme convenu » ne s'écrit qu'une fois par rendez-vous. Trouve d'abord pourquoi les
deux ne voient pas la même fin (croisement à une porte, regard, ordre des délibérations) ; corrige la règle commune,
pas Anselme ni l'auberge. Même règle pour le joueur qui hèle ou répond.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : le cas réel (capture auberge 42 vers 500) : une seule retrouvaille,
  Anselme cesse de héler ; un autre cas de même nature (mine ou Relais, appelé qui vient à l'appelant) ; le joueur
  appelé ou appelant ; un rendez-vous manqué (l'un part) reste une attente vaine, comme avant.
- Banc rapide (`tools/comparer_bancs.py --reference c592d68`, 4 h, 4 graines, quatre scénarios) puis l'audit 12 h de
  l'auberge 42 et 7, branche seule : retrouvailles redites, appels, passages par heure.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-ouie.md`, `docs/etat-dev.md` (« Branche `codex-rendez-vous`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-60-rendez-vous.md`.
