# Tâche Codex 237 (diagnostic) : trois alertes de la vérification 4306c14

La vérification d'intégration 4306c14 (lot 231, `docs/taches/rapport-codex-231-verif-integ.md`) relève, contre `4d4c625` :
1. **Mine** : minutes urgentes sans recours **3,12 → 58,12** PNJ·min par nuit, appels **5,38 → 17,50** ; attente 1 072 → 1 321.
2. **Gorm, hameau 1985, 541–545** : onze retours chaleur/devoir en quelques minutes (l'ancien même but chaleur existe à
   552–606, sans rafale).
3. **Maël, hameau 42, 419–451** : quatre retours suspects 219 entre restitution de torche et inspection, absents de la même
   nuit ancienne.

**Diagnostic seul : aucun code du jeu modifié.** Pour chaque alerte : la première décision fautive (minute, PNJ, but,
cause retenue), l'invariant commun en cause, et si elle existe encore sur l'intégration actuelle (après 218, 229, 230,
232). Proposer un petit lot par invariant distinct, avec ses fichiers. Si deux alertes ont la même cause, le dire.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le PC fixe**. Bruts du lot 231 sur ce poste : `C:\Users\msics\donjon\artifacts\verif-integ-4306c14\` (archives,
`analyse/manifest.json`, `complement231.json`). Rejoue sur un worktree détaché de `4306c14`, puis sur l'intégration ; une
seule nuit à la fois, priorité réduite, au plus 2 processus. Captures rechargées : monde et rendu identiques.

**Bruts dans `C:\Users\msics\donjon\artifacts\alertes-237\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## Livraison
- Branche `codex-alertes-231` : seulement `docs/taches/rapport-codex-237-alertes-231.md` (une page) et une entrée
  « Branche `codex-alertes-231`, non fusionnée » dans `docs/etat-dev.md`. Poussée (pas `main`) ; si la revue bloque la
  poussée, laisse le commit local et dis-le.
