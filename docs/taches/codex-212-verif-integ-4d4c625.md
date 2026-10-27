# Tâche Codex 212 : vérification d'intégration 4d4c625 (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots moteur fusionnés depuis la vérification `ee835d2`
(lot 174) : 175, 179 (fins de garder), 181 (départ définitif), 184 a/b (projet de pièces), 185 (prévision d'eau bornée), 189
(sortie extérieure), 191 (déjà entendu), 192 (naissance d'un projet sur un vol), 194 (porte d'un lieu gardé), 197 (empathie), 200
(occasions asymétriques, données), 201 (réserve brisée), 204 (portée au seuil), plus les lots MJ qui ne changent pas le moteur.
**Aucun changement de code du jeu** ; un défaut trouvé devient un petit lot, décrit avec son cas réel. Pas de Luna. **Bruts dans
`C:\Users\msics\donjon\artifacts\verif-integ-4d4c625\`, jamais dans le worktree.**

**Poste : le PC fixe**, dans ton propre worktree (code du jeu identique à `4d4c625` : vérifie `git diff --stat 4d4c625 -- donjon
tools` vide ; aucun `pull` pendant le lot). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; `PYTHONIOENCODING=utf-8`.
Deux autres lots calculent sur ce poste (205, 211) : **au plus 2 processus de calcul**, priorité réduite, en fond. Termine ton
dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Modèle : le lot 174 (`docs/taches/codex-174-verif-integ-ee835d2.md` s'il existe, sinon `rapport-codex-174-verif-integ.md`) et le
lot 160 (`docs/taches/codex-160-verif-integ-7adc788.md`, lanceur dans `C:\Users\msics\donjon\artifacts\verif-integ-7adc788\` sur ce
poste).

## Campagnes (une fois, en fond, à priorité réduite)
Avec `--detecter-avis` ou l'équivalent : **le compteur des changements d'avis du lot 199 doit être actif** dans l'audit. Audit 12 h
quatre scénarios × 1985, 7, 42, 2024, 3, 11, 99, 500 ; `rixe` et `rixe_douce` 8 h × quatre graines ; `VERIFIER` +
`spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios ; `crue_hameau` 12 h × quatre graines.

## Références (relire, jamais rejouer)
Les bruts `ee835d2` sont sur le laptop, pas ici : prends les chiffres du rapport 174 en le disant ; `artifacts\verif-integ-7adc788\`
(lot 160) est sur ce poste.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées (Lucien,
  auberge 42/314).
- Tableau par scénario `ee835d2` → `4d4c625`, mêmes mesures qu'au lot 174, plus les retours suspects du compteur 199 et S/F/D du
  lot 183 (richesse).
- Ce que les lots annonçaient à surveiller : hameau attente et noir (174 : attente 192,5 → 750) ; passages horaires (185, 189 :
  hameau 1985 20 → 40/h) ; récupérations nées naturellement (192, 200) ; projets de pièces (184 : noir de la mine) ; repas
  d'empathie et sans recours (197) ; mine noir 26 → 40 min (204) ; auberge retours 2 → 5 (204) ; départs définitifs (181, 189 :
  aucun départ involontaire).
- Les défauts nouveaux, chacun avec un cas réel et l'invariant en cause ; pour une boucle, dire si elle existait déjà dans la même
  nuit sur `ee835d2` (d'après le rapport 174).

## Livraison
Branche `codex-verif-integ-4d4c625` : seulement `docs/taches/rapport-codex-212-verif-integ.md` (une page) et une entrée
« Vérification d'intégration 4d4c625 » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas
`main`) ; si la poussée est bloquée, laisse le commit local et dis-le. Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-4d4c625\`.
