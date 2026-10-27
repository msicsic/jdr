# Tâche Codex 160 : vérification d'intégration 7adc788 (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots moteur fusionnés depuis la vérification `2d504ae`
(lot 148) : 146 et 146 b (déplacement accepté, agendas évalués sans écriture, fin d'`amener`), 152 (dossiers à portée, côté
MJ), 154 (poser au sol), 155 (la lumière et l'abri partagent le danger de la fuite). **Aucun changement de code du jeu** ; un
défaut trouvé devient un petit lot, décrit avec son cas réel. Pas de Luna.

**Poste : le PC fixe**, dans ton propre worktree (code du jeu identique à `7adc788` : vérifie `git diff --stat 7adc788 -- donjon
tools` vide ; aucun `pull` pendant le lot). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`.
Deux autres lots tournent sur ce poste : **au plus 2 processus de calcul**, priorité réduite. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 148 (`docs/taches/codex-148-verif-integ-2d504ae.md`, rapport `rapport-codex-148-verif-integ.md`).

## Campagnes (une fois, en fond, à priorité réduite)
Les campagnes du lot 148 (`C:\Users\msics\donjon\artifacts\verif-integ-2d504ae\`, son lanceur), avec
`$d='C:\Users\msics\donjon\artifacts\verif-integ-7adc788'` et `Set-Location` vers ton worktree : audit 12 h quatre scénarios ×
1985, 7, 42, 2024, 3, 11, 99, 500 ; `rixe` et `rixe_douce` 8 h × quatre graines ; `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h,
graine 42, cinq scénarios (la crue 42 s'arrêtait au lot 148 : elle doit aller au bout) ; `crue_hameau` 12 h × quatre graines.

## Références (relire, jamais rejouer)
`artifacts\verif-integ-2d504ae\` (lot 148) et `artifacts\verif-integ-057766f\` (lot 131).

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées (Lucien,
  auberge 42/314).
- Tableau par scénario `2d504ae` → `7adc788`, mêmes mesures qu'au lot 148.
- Les deux défauts du lot 148 : crue 42 sous `VERIFIER` (doit aller au bout) ; Brune crue 2024 687–715 (passages par heure) ;
  et ce que le lot 155 laissait : Brune longtemps dans l'eau, Ilse affamée en attente (crue 2024).
- Agendas de Gorm dans la crue (informer, `amener` s'il est déclaré) : sommeil, réveils, atteints, abandonnés.
- Les défauts nouveaux, chacun avec un cas réel et l'invariant en cause ; pour une boucle, dire si elle existait déjà sur
  `2d504ae` dans la même nuit.

## Livraison
Branche `codex-verif-integ-7adc788` : seulement `docs/taches/rapport-codex-160-verif-integ.md` (une page) et une entrée
« Vérification d'intégration 7adc788 » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas
`main`). Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-7adc788\` (non versionnés).
