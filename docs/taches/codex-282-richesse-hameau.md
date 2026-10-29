# Tâche 282 (diagnostic seul) : richesse et attente du hameau entre c870c8b et 0bad227

La vérification d'intégration 274 (`docs/taches/rapport-codex-274-verif-integ.md`, fusionné ; archives
`C:\Users\msics\donjon\artifacts\verif-integ-0bad227\crue-hameau-12h\` et
`C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\` pour la référence) mesure au hameau (`crue_hameau`, 12 h, quatre
graines 1985/7/42/2024, départ tiré, joueur passif) : attente urgente **931 → 1 062 PNJ·min**, richesse S
**64,50 → 56,25**, noir **79 → 133**, propositions/acceptées **17/3 → 11,25/2,25**. Les lots fusionnés entre les deux
commits sont décrits dans `docs/etat-dev.md` (245 à 274).

## Ce qu'il faut établir
Par graine : quelles signatures sociales (fonction `cats` du lot 183) sont perdues ou gagnées, quelles attentes
augmentent (PNJ, besoin, intervalle) et pourquoi selon les croyances (recours sans moyen admissible, refus retenu, garde,
eau, noir). Pour chaque perte ou attente importante : est-elle **juste** (contrainte réelle, perte de rencontres fortuites
acceptée au lot 233) ou un **défaut** (recours admissible jamais tenté, croyance périmée, boucle) ? Le premier écart de
chaque nuit et le lot qui l'introduit si la chronique et les rapports suffisent à le désigner (pas de bissection longue).
Captures des moments décisifs : monde, rendu et scène identiques après recharge. Si un défaut est établi, propose un petit
lot avec son invariant, sans le corriger.

**Diagnostic seul : aucun fichier de `donjon/`, `tools/`, `tests/` ni scénario modifié.** Relecture des archives d'abord ;
rejeu seulement si nécessaire, un processus à priorité réduite à la fois, worktree détaché (jamais le dépôt principal).
Pas de Luna, pas de suite complète, pas de banc comparatif. **Poste : le PC fixe.**

## Livraison
Branche `codex-richesse-hameau` : rapport d'une page `docs/taches/rapport-codex-282-richesse-hameau.md` et entrée dans
`docs/etat-dev.md`, commit, poussée ; si elle échoue depuis le PC fixe, laisse le commit local et donne son hash, sans
passer par l'API GitHub. Bruts dans `C:\Users\msics\donjon\artifacts\richesse-282\`. Termine par `LOT TERMINÉ` (résumé
d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
