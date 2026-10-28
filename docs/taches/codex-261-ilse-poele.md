# Tâche 261 (diagnostic) : Ilse entretient le poêle 450 minutes malgré sa faim (crue 7)

La vérification d'intégration 241 (`docs/taches/rapport-codex-241-verif-integ.md`, fusionnée ; bruts
`C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\`) relève une alerte à expliquer : **crue, graine 7, Ilse entretient
le poêle pendant 450 minutes à partir de 275, alors que sa faim presse**. Les relevés ne disent pas si un recours
alimentaire admissible existait ; aucune violation de priorité n'est certifiée.

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir
1. **Reproduire** : rejoue la nuit crue 7 sur l'intégration actuelle (départ tiré, joueur et durée de l'audit 241, 12 h)
   et dis si l'épisode y est encore ; sinon reprends la nuit sur `c870c8b` (worktree détaché) pour le capturer.
2. **Expliquer le choix d'Ilse** à quelques instants clés (par exemple 275, 400, 600) : besoins et paliers comparés par
   `deliberation.choisir`, recours de la faim essayés et leur issue (plan trouvé, refus retenu, attente bornée, sans plan),
   ce qu'elle croit des vivres (où, à qui, épuisés), pourquoi l'entretien du poêle passe devant.
3. **Verdict** : comportement juste (aucun recours de faim admissible d'après ses croyances : dire lequel manque) ou
   défaut (un recours admissible existe et n'est pas pris : dire la fonction et la règle commune en cause, en une phrase,
   sans proposer d'exception à Ilse, au poêle ou à la crue).

Sources : `docs/plan-planificateur.md`, `donjon/deliberation.py` (`choisir`, `_candidats`, `_classer`), outils de
diagnostic du banc (`python -m donjon.banc_pnj --diagnostic`, `tools/`). Captures rechargées pour les instants clés : monde
et rendu identiques après rechargement.

Lot de 30 à 45 minutes. **Poste : le PC fixe**, un processus à priorité réduite. Pas de Luna, pas de suite complète, pas
de banc comparatif.

## Livraison
- Branche `codex-ilse-poele` : seulement `docs/taches/rapport-codex-261-ilse-poele.md` (une page) et une entrée « non
  fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\ilse-261\`. Commite ; pousse si tu
  peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou
  `QUESTION : …`.
