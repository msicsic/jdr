# Tâche Codex 87 : un besoin dont la recherche a buté sans rien de nouveau attend, au lieu d'être recherché chaque minute

Branche `codex-borne-attente` (elle porte ce fichier, issue de l'intégration **020250e** : lots 38 à 86 sauf 85), worktree dans
`tmp-worktrees/`. Lot de coût **qui change des décisions** : à mesurer et à justifier. Pas de Luna. **Un seul poste** :
priorité réduite, au plus 3 processus ; mesures de 12 h, trois versions ensemble, un processus chacune.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `besoins` (« L'attente » : un besoin dont chaque recours a été essayé sans plan
attend), `refus-retenus` (un refus tient tant qu'aucun moyen nouveau n'est cru : `deliberation.moyens_crus`, `tient`),
`codex-cout-12h` 38, et les diagnostics des lots 63 (`origin/codex-faim-sans-plan`), 66 (`origin/codex-certificat-prix`) et
76 (bissection, dans l'intégration)), `docs/plan-planificateur.md`, `docs/plan-decision.md` (§ 8 ter : budget selon l'enjeu),
puis `donjon/deliberation.py` (`attentes`, `_classer`, `choisir`, `moyens_crus`), `donjon/planification.py` (`chercher`,
`BORNES`, `NOEUDS`).

## Le constat
Après les lots 81 et 86, l'auberge coûte encore ×2,4 (fixe) à ×3,8 (tiré) sur 12 h, presque tout entre 8 et 12 h. Les marches
de la bissection (calibration des signes, lots 45 et 55) ajoutent surtout des **recherches bornées** : Joss/faim 47 → 141,
Tilo/faim 0 → 118. Une recherche bornée ne prouve rien et n'est reprise ni par la mémoire ni par un certificat (lots 63, 66) :
elle est refaite à chaque choix, alors que, dans 71 % des paires successives mesurées au lot 63 pour Joss, aucune lecture
observée n'avait changé.

## D'abord, mesurer
Sur les nuits auberge 1985 fixe et tirée : pour chaque (PNJ, but) borné en fin de nuit, combien de recherches bornées
successives sans plan, ce qui change entre elles (moyens crus, croyances du but, prix de faute et désespoir, lumière), et
combien finissent par trouver un plan, après quoi.

## L'invariant
**Une recherche qui atteint sa borne sans plan met ce but en attente, comme un recours épuisé, jusqu'à un fait nouveau qui
peut lui servir** : un moyen cru nouveau pour ce besoin (la règle existante `moyens_crus` des refus retenus), un changement
de ce que la recherche lit pour ce but et qui peut créer une arête (une permission, une faute devenue acceptable parce que
la détresse a franchi un palier, une source de lumière, une porte crue ouverte), ou un franchissement de palier du besoin
lui-même ; sinon, le PNJ ne se « creuse pas la tête » à chaque minute. Les paliers sont ceux qui existent déjà (bandes, seuils
de désespoir) : pas de délai fixe ni de cas propre à Joss. L'attente se sauvegarde et se lit au même laps découpé.

**Ce lot change des décisions** : dis lesquelles (avant/après, nuits auberge et mine 12 h, et banc rapide 4 h des quatre
scénarios), et prouve qu'aucun recours qui aboutissait n'est perdu sans raison (pour chaque plan trouvé par la base après
une suite de bornées, la branche le trouve aussi, au plus tard au fait nouveau qui l'a rendu possible).

## Vérification (demandée expressément)
- Tests après rechargement, même laps découpé : Joss/faim borné sans fait nouveau, pas de seconde recherche ; un moyen
  nouveau (un vivre vu, un refus levé) la relance ; le désespoir qui franchit son palier la relance (Brune devant la réserve) ;
  une recherche non bornée inchangée.
- Banc rapide (`tools/comparer_bancs.py --reference 020250e --processus 3`, 4 h, 4 graines, quatre scénarios) : aucune
  usurpation, violation, plantage ni boucle nouvelle ; vols, sans recours, en attente, écarts lus.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche lancés ensemble, un processus chacune (`tools/empreintes_nuits.py jouer
  --heures 12 --scenarios mine auberge --graines 1985 --processus 1`, fixe et tiré) ; recherches bornées, CPU par tranche.
  Visée : l'auberge sous ×1,5 contre `42bb9c0`.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche `codex-borne-attente`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-87-borne-attente.md` (mesure, règle, décisions changées et
pourquoi, temps, limites).
