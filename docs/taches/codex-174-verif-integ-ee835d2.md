# Tâche Codex 174 : vérification d'intégration ee835d2 (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots moteur fusionnés depuis la vérification `7adc788`
(lot 160) : 146 d (fermeture périmée refusée), 146 e (amener par la parole et la demande, lumière devant la cible), 163 (le séjour
humide cède au sec), 167, 167 b et 167 c (s'interposer, agendas garder et protéger), et les lots MJ qui ne changent pas le moteur.
**Aucun changement de code du jeu** ; un défaut trouvé devient un petit lot, décrit avec son cas réel. Pas de Luna. **Bruts dans
`C:\Users\msics\donjon\artifacts\verif-integ-ee835d2\`, jamais dans le worktree.**

**Poste : le laptop**, dans ton propre worktree (code du jeu identique à `ee835d2` : vérifie `git diff --stat ee835d2 -- donjon
tools` vide ; aucun `pull` pendant le lot). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`.
Deux autres lots tournent sur le PC fixe ; l'utilisateur travaille sur ce poste : **au plus 2 processus de calcul**, priorité
réduite. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 160 (`docs/taches/codex-160-verif-integ-7adc788.md`, rapport `rapport-codex-160-verif-integ.md`).

## Campagnes (une fois, en fond, à priorité réduite)
Les campagnes du lot 160 (son lanceur dans `C:\Users\msics\donjon\artifacts\verif-integ-7adc788\` s'il y est, sinon celui du lot 148
dans `artifacts\verif-integ-2d504ae\`), avec `$d='C:\Users\msics\donjon\artifacts\verif-integ-ee835d2'` et `Set-Location` vers ton
worktree : audit 12 h quatre scénarios × 1985, 7, 42, 2024, 3, 11, 99, 500 ; `rixe` et `rixe_douce` 8 h × quatre graines ;
`VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios ; `crue_hameau` 12 h × quatre graines.

## Références (relire, jamais rejouer)
`artifacts\verif-integ-7adc788\` (lot 160) et `artifacts\verif-integ-2d504ae\` (lot 148), s'ils sont présents sur ce poste ; sinon
les chiffres des rapports 160 et 148, en le disant.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées (Lucien,
  auberge 42/314).
- Tableau par scénario `7adc788` → `ee835d2`, mêmes mesures qu'au lot 160.
- Ce que les lots 163 et 167 annonçaient à surveiller : eau et attente en crue (163 : eau en baisse, attente et passages en
  hausse, 34 passages/h en crue 2024), `fige_presse` de Josse (mine 1985 et 2024), interpositions spontanées (combien, envers qui,
  aucune violence), Brune 305 min sans but et vivres épuisés (crue 2024) ; galerie en fin de nuit (146 e : 3/8 → 2/8).
- Agendas de Gorm dans la crue (informer, amener) : sommeil, réveils, atteints, abandonnés ; Ilse et Brune à la galerie.
- Les défauts nouveaux, chacun avec un cas réel et l'invariant en cause ; pour une boucle, dire si elle existait déjà sur
  `7adc788` dans la même nuit.

## Livraison
Branche `codex-verif-integ-ee835d2` : seulement `docs/taches/rapport-codex-174-verif-integ.md` (une page) et une entrée
« Vérification d'intégration ee835d2 » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas
`main`). Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-ee835d2\` (non versionnés).
