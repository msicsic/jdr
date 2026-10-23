# Tâche Codex 28 : le coût de calcul des trajets réels

Branche `codex-cout-trajets` (elle porte ce fichier, issue d'`integration` **0ac6b15** : `main` 42bb9c0 + Q
`codex-trajets-reels` + correctif `defense`), worktree dans `tmp-worktrees/`. **Pas de Luna** (rien ne touche le MJ).
Lis `AGENTS.md` (section « Rythme des lots » : lot court), `docs/etat-dev.md` (entrée `codex-trajets-reels` et sa
fusion, « À revoir » : Trajets réels), `docs/taches/rapport-codex-20-trajets-reels.md`, puis
`donjon/planification.py` (`Etat`, `Vue`, `_entrees`, `_chercher`, `_explorer_etats`, `Vue.pression`),
`donjon/obstacles.py` (`cout_route`, `Parcours`, distances locales).

## Le constat
Depuis Q, le planificateur compte le vrai temps de marche ; le comportement est sain, mais une nuit coûte
**×3,7 à ×4,8** au processeur (mine 42, 8 h : 43,9 → 210,4 s ; auberge 42 : 31,2 → 115,6 s ; `main` 42bb9c0 et
la fusion lancés ensemble). Même nombre de recherches : les états sont plus nombreux (case, orientation, allure
dans `Etat`) et chacun plus cher (routes, approches, pression par salle). Recherches bornées à la mine 42 :
8 → 91 (Rémy `faim` 49, Josse `feu:poele` 39, Bram `lumiere` 3).

## L'invariant
Les PNJ décident exactement la même chose qu'à 0ac6b15, pour moins cher. Un seul commit par levier.

1. **Profil d'abord** (`py-spy` en échantillonnage, pas `cProfile`) : mine 42 et auberge 42, 4 h. Range les deux ou
   trois postes les plus lourds dans le rapport, avec leur part.
2. **Leviers exacts** sur ces postes : mémoriser ce qui ne dépend que de la géométrie, des portes et des obstacles
   (routes, approches, distances locales) sous une clé qui dit ce qu'elle lit ; ne pas recalculer la pression par
   salle d'un état à son successeur quand elle ne change pas ; tout ce qui garde l'ordre d'exploration et les
   coûts à l'identique. Chaque lecture gardée est recomparée par `spatial.VERIFICATION` ou `planification.VERIFIER`.
3. **Réduire l'espace d'états** (orientation, allure, case dans `Etat`) seulement par une équivalence exacte que tu
   prouves (deux états qui ne diffèrent que par un champ sans effet sur la suite) ; si le gain exige un modèle
   approché (changer des résultats, même bornés), **ne l'implémente pas** : propose-le dans le rapport avec son
   gain estimé.

Cible : au plus ×1,5 contre 42bb9c0 sur mine et auberge. Si elle n'est pas atteinte par des leviers exacts, dis
où reste le temps et ce qu'il faudrait changer.

## Vérifications (minimum, `AGENTS.md`)
- Empreintes identiques à 0ac6b15 : `tools/empreintes_nuits.py` (recherches et nœuds compris) ou
  `tools/comparer_bancs.py --empreintes --reference 0ac6b15`, 2 h, Relais, mine, auberge, crue × 4 graines.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, graine 42, mine et auberge.
- Temps au processeur : 42bb9c0, 0ac6b15 et la branche lancés ensemble, `tools/empreintes_nuits.py`, 4 h, graines
  42 et 1985, mine et auberge, deux processus chacun au plus.
- Tests ciblés pendant le travail, suite complète (`tools/tests.py --processus 3`) une fois, à la fin.
- Pas de banc 8 h ni d'audit dans ce lot.

## Livraison
Commits signés ; pousse la branche (pas `main`). Rapport d'une page
`docs/taches/rapport-codex-28-cout-trajets.md` : profil avant/après, leviers et clés des caches, temps, limites,
propositions non exactes. `docs/etat-dev.md` : entrée « Branche `codex-cout-trajets`, non fusionnée ».
