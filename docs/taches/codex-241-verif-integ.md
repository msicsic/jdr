# Tâche Codex 241 : vérification d'intégration (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots fusionnés depuis la vérification `4306c14`
(lot 231) : 218 (restauration des charges), 229 (tests de 225), 230 (rendez-vous tenus), 232 (pureté des candidats),
233 avec 195 (ouïe des compagnons), 236 (recours non greffé), 238 (résultat emporté), 239 (renoncé = attente),
240 (aide stable).

**Aucun changement de code du jeu.** Un défaut trouvé devient un petit lot, décrit avec son cas réel. Pas de Luna.
**Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-<commit>\`**, jamais dans le worktree.

**Poste : le PC fixe**, dans ton propre worktree. Note le commit de départ ; le code du jeu doit y rester identique
(`git diff --stat <commit> -- donjon tools` vide), aucun `pull` pendant le lot. D'autres lots calculent sur ce poste :
**un seul processus de calcul à la fois**, priorité réduite, en fond. Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Modèle : le lot 231 (`docs/taches/codex-231-verif-integ-4306c14.md`, `rapport-codex-231-verif-integ.md`) ; ses bruts sont
sur ce poste dans `C:\Users\msics\donjon\artifacts\verif-integ-4306c14\` : **références à relire, jamais à rejouer**.

## Campagnes (une fois, en fond)
Compteurs actifs : classes 219, causes 227.
- Audit 12 h, quatre scénarios × graines 1985, 7, 42, 2024, 3, 11, 99, 500.
- `rixe` et `rixe_douce`, 8 h × quatre graines.
- `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios (dont mine 42 et rixe 42, arrêtées au lot 231).
- `crue_hameau`, 12 h × quatre graines.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées
  (dont Lucien auberge 42 à 435).
- Tableau par scénario `4306c14` → nouveau commit, mêmes mesures qu'au lot 231, avec compteurs 219/227 et S/F/D (lot 183).
- Suivis : richesse du hameau après 233 (perte acceptée, la chiffrer) ; Anselme auberge 7 (236) ; « sans recours » mine
  (239) ; retours chaleur/devoir de Gorm hameau 1985 (240) ; départs dans la minute d'un « Ici, viens ! » (230) ; attente
  hameau (1 761 au lot 231) ; avis adoptés (hameau 1,5 → 0 au lot 231).
- Défauts nouveaux, chacun avec un cas réel et l'invariant en cause ; pour une boucle, dire si elle existait déjà dans la
  même nuit sur `4306c14`.

## Livraison
- Branche `codex-verif-integ-2` : seulement `docs/taches/rapport-codex-241-verif-integ.md` (une page) et une entrée
  « Vérification d'intégration <commit> » dans `docs/etat-dev.md`. Poussée (pas `main`) ; si la revue bloque la poussée,
  laisse le commit local et dis-le.
