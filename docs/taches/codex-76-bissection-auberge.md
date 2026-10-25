# Tâche Codex 76 : trouver par bissection ce qui a rendu l'auberge cinq fois plus lente

Branche `codex-bissection-auberge` (elle porte ce fichier, issue de l'intégration **1171fc3**), worktree dans
`tmp-worktrees/`. **Diagnostic, sans modification du moteur.** Pas de Luna. **Un seul poste** : priorité réduite, au plus 3
processus (une nuit par version testée, versions lancées deux par deux au plus).

Lis `AGENTS.md`, `docs/etat-dev.md` (les entrées de coût : lots 30, 31, 38, 46, 48, 49, 51, 71, 72 ; les diagnostics des lots
62, 63, 75 sur leurs branches `origin/codex-salles-interet`, `origin/codex-faim-sans-plan`, `origin/codex-pertinence-arriere`)
et `tools/empreintes_nuits.py`.

## Le constat
Nuit de 12 h, **auberge, graine 1985**, temps CPU : `main` **42bb9c0** 96 à 125 s, intégration **1171fc3** 593 à 834 s selon les
séries (départ tiré et fixe), soit **×5 à ×8**. La mine, elle, est revenue près de `main`. Trois diagnostics successifs
(lots 62, 63, 75) ont réfuté leur hypothèse sur la cause ; le dernier montre, sur la fenêtre 480-505, Lucien
(`garder:grenier`, `placer:ballot`, `garder:etable`) à 81 % des nœuds, et Joss/Tilo/faim bon marché. Il faut cesser de deviner.

## Ce qu'il faut faire
1. **Bissection** sur l'historique de `integration` entre `42bb9c0` et `1171fc3` (`git log --first-parent`, commits de
   fusion seulement) : à chaque étape, jouer **la même nuit** (auberge 1985, départ fixe, 12 h ; `tools/empreintes_nuits.py
   jouer --depot <worktree détaché> --heures 12 --scenarios auberge --graines 1985 --departs fixe --processus 1`) sur le
   commit milieu, temps CPU et nœuds. Le saut n'est peut-être pas unique : relève chaque marche de plus de +30 % et
   continue la bissection sur chacune. Worktrees détachés sous `.worktrees/`, supprimés ensuite. Les anciens commits peuvent
   demander un autre lanceur (voir comment les lots 46 à 72 ont lancé `42bb9c0`).
2. Pour chaque marche trouvée : le lot fusionné en cause, et, sur la nuit avant/après la marche, le temps et les nœuds par
   (PNJ, but) des recherches (`--diagnostic`), pour dire **ce qui** coûte plus : plus de recherches neuves, plus de nœuds par
   recherche, recherches bornées, ou un coût par nœud plus élevé ; et si les nuits divergent (décisions différentes) ou non.
3. Recommandation : le ou les invariants à écrire dans un lot de coût, fondés sur ces chiffres.

## Livraison
Commits signés (outil éventuel et rapport seulement), branche poussée (pas `main`). Rapport d'une page :
`docs/taches/rapport-codex-76-bissection-auberge.md` (commits testés et leurs temps, marches, lots en cause, ce qui coûte,
recommandation, limites). Une entrée dans `docs/etat-dev.md`. Bruts dans `artifacts/bissection-auberge/`.
