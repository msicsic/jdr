# Tâche Codex 264 (diagnostic) : deux retours sans nouvelle (Bram mine 2024, Gorm hameau 7)

La vérification d'intégration 241 (`docs/taches/rapport-codex-241-verif-integ.md`, fusionnée, « Petits lots à
instruire » ; bruts `C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\`, dont `analyse/suspects241.json`) relève deux
alertes nouvelles du compteur 219, absentes des mêmes nuits sur `4306c14` :
- **Bram, mine 2024, 613** : retour au but de lumière après un `manque:acheter`, en passant par la garde, sans nouvelle
  entre l'abandon et le retour ;
- **Gorm, hameau 7, 682** : engagement du brasero → attente de Sève → même but, état initial retrouvé. La référence
  contient ce but à 255/285 et 645/661, mais pas ce retour immédiat.

Invariant en jeu : le **réessai lié à l'obstacle** (lot 225 : on ne reprend un but abandonné que si l'on croit sa cause
levée ou un moyen nouveau) et la **continuité de l'attente** (lots 213, 240). Ces alertes ne prouvent ni répétition du
même geste ni boucle durable.

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir, pour chacun des deux cas
1. **Reproduire** sur l'intégration actuelle (départ tiré, joueur et durée de l'audit 241) ; sinon sur `c870c8b`
   (worktree détaché). Capturer avant l'abandon et avant le retour ; monde et rendu identiques après rechargement.
2. **La cause de l'abandon** (obstacle retenu ou non, sa forme) et **ce qui autorise le retour** : une entrée nouvelle
   réelle (croyance changée, moyen nouveau, autre palier), ou aucune.
3. **Verdict** : retour justifié (dire l'entrée nouvelle, et si le compteur 219 devrait la reconnaître) ou défaut (la
   règle commune en cause en une phrase, sans exception propre à Bram, à Gorm ou au scénario).

Lot de 30 à 45 minutes. **Poste : le laptop** (l'utilisateur y travaille), un processus à priorité réduite, une nuit à
la fois. Pas de Luna, pas de suite complète, pas de banc comparatif.

## Livraison
- Branche `codex-retours-241` : seulement `docs/taches/rapport-codex-264-retours-241.md` (une page) et une entrée « non
  fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\retours-264\`. Commite ; pousse si tu
  peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
