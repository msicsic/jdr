# Tâche Codex 342 : attribuer et corriger les incidents de la suite d'essai du groupe 1

Lis `AGENTS.md`, `docs/etat-dev.md`, puis l'[attribution du lot 319](attribution-codex-319-up-recapitulatif.md), qui a
suivi la même démarche.

## Constat
`essai-groupe-1` (`6f490ba`) réunit l'intégration d'alors (après le lot 319) et quatre lots non fusionnés :
- 315, `codex-reclamations-repetees` ;
- 313, `codex-contact-inconnu` ;
- 332, `codex-attention-conjointe` ;
- 333, `codex-garder-lieu`.

Les conflits ont été résolus par le superviseur : `deliberation.tient()` garde les deux branches, et
`tests/test_etapes_chainees.py` réunit les dictionnaires des lots 313 et 334.

La suite complète de cette branche compte **2 963 tests, avec 13 échecs et 20 erreurs**. Le journal est dans
`C:\Users\msics\donjon\artifacts\suite-groupe1-6f490ba\suite.log` (et `suite.json`). Premières causes relevées :
- **13 `KeyError: 'position'`** dans `esprits._percus` (`monde.joueur` sans position), atteint par
  `pnj.croit_present` → `percoit` : `test_eau`, `test_corps_blessable`, `test_rejeu`, `test_localisation_crue`,
  `test_agendas_destinataires`, `test_dynamique_besoins`, `test_recours_prioritaire`… La ligne date du lot 181 :
  c'est un nouvel appel qui l'atteint sans position ;
- **6 `TypeError … _retentir() … 'emission'`** : préexistants, traités par le lot 339 (ne les corrige pas ici) ;
- les échecs de `test_mine`, `test_lumiere`, `test_taches_payees`, `test_reclamations_repetees`, `test_pas_compagnons`,
  `test_bourse_redemandee`, `test_etapes_chainees` (empreintes mine/auberge) et `test_completion_preuves`
  (captures), plus un `KeyError: 'anselme'`.

## Ce qui est demandé
1. Pour chaque incident : le lot responsable, prouvé par la branche du lot seule sur l'intégration, ou par le
   retrait d'un seul lot. Classe ensuite l'incident : préexistant sur l'intégration seule, défaut d'un lot,
   défaut d'interaction entre lots, ou attente périmée par un changement légitime (avec preuve).
2. **Défaut** : corrige l'invariant commun dans la branche du lot fautif (worktree à part dans `.worktrees/`),
   sans cas propre au test, et pousse cette branche. Un défaut d'interaction se corrige dans le lot qui introduit
   le second appel. **Attente périmée** : remplace-la seulement avec la preuve, en gardant toutes les autres
   assertions.
3. Refais `essai-groupe-1` = `origin/integration` + les quatre branches corrigées, avec les mêmes résolutions de
   conflit, puis relance **seulement** les fichiers en incident et les fichiers de test des fichiers de code
   modifiés. Pas de suite complète : le superviseur la relancera.

## Contraintes
- Pas de banc ni de Luna, sauf si une correction change le comportement d'un PNJ : banc rapide 4 h des scénarios
  touchés, références lues du cache.
- **Poste : le PC fixe.** Deux processus au plus, priorité réduite. Calcul long détaché, avec un fichier de fin.
- Ne touche pas `jeu.py` (le lot 325 y a une fusion en cours).

## Livraison
- Corrections poussées sur les branches des lots fautifs, et `essai-groupe-1` refaite et poussée.
- Matrice `docs/taches/attribution-codex-342-groupe1.md` (un incident par ligne : lot, classe, preuve, correctif)
  et rapport d'une page `docs/taches/rapport-codex-342-attribution-groupe1.md`, sur la branche
  `codex-attribution-groupe1` (base `integration`), poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; la poussée est autorisée).
- Bruts dans `C:\Users\msics\donjon\artifacts\groupe1-342\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
