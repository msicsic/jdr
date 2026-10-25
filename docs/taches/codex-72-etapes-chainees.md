# Tâche Codex 72 : la recherche ne copie le chemin qu'une fois, quand elle le rend

Branche `codex-etapes-chainees` (elle porte ce fichier, issue de l'intégration **fbcf0ff**), worktree dans `tmp-worktrees/`.
Lot de coût, demandé par l'utilisateur. Pas de Luna. **Un seul poste** : priorité réduite, au plus 3 processus ; mesures
de 12 h, trois versions ensemble, **un processus chacune**. Les lots 66 (`_sans_plan`, `_parcours`, `_explorer`) et 71
(`Vue`, `_entrees`, `obstacles`) peuvent entrer dans l'intégration pendant ton lot : `git merge origin/integration` au
début si elle a avancé ; ce lot ne touche que l'intérieur de `_explorer_etats` et ce qui consomme ses étapes.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir », volet coût : **« Coût fixe, mêmes nœuds »**, point (c) et (d)),
`docs/plan-planificateur.md`, puis `donjon/planification.py` (`_explorer_etats` : `etapes + ajout` à chaque transition
poussée, `copy.deepcopy(etapes)` sur le chemin trouvé et à l'entrée/sortie de `_MEMOIRE` ; `SuiteDifferee` ; `_couper`),
`donjon/signes.py` (`percevoir_tous`).

## Le constat (revue externe du 2026-10-24, vérifié dans le code)
Chaque transition poussée dans le tas alloue et copie une liste `etapes + ajout` ; le chemin trouvé est copié en profondeur,
et encore à l'entrée et à la sortie de la mémoire. Sur des milliers d'états par recherche, un seul chemin (ou aucun) est
rendu. Par ailleurs `signes.percevoir_tous` recalcule les émissions et une signature (`repr`) de tous les acteurs à chaque
événement (la mine avait pris +35 % avec 3c) : à profiler.

## L'invariant
**Les étapes d'un plan se reconstruisent une seule fois, pour le chemin rendu** : chaque entrée du tas porte un maillon
immuable (parent, ajout), la liste n'est construite qu'au résultat, et la mémoire garde une forme immuable qui n'a pas besoin
de copie profonde. **Mêmes recherches, mêmes nœuds, mêmes égalités et même ordre de visite, mêmes décisions.** Puis, si le
profil le justifie, la même règle pour `percevoir_tous` : ne recalculer les émissions et signatures que des acteurs qui ont
changé (sinon, livre seulement la mesure).

## Vérification (demandée expressément)
- Profil avant/après (même nuit, même fenêtre) : part de l'allocation des étapes et des copies ; part de `percevoir_tous`.
- Tests : mêmes plans et même ordre sur les captures `tests/data/cout-12h/` et sur un plan à plusieurs étapes ; la mémoire
  rend un plan identique et non modifiable par l'appelant.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference fbcf0ff --processus 3`), quatre scénarios × 4 graines :
  identiques.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche **lancés ensemble**, un processus chacune
  (`tools/empreintes_nuits.py jouer --heures 12 --scenarios mine auberge --graines 1985 --processus 1`, tiré et fixe) ;
  `comparer --calcul` base contre branche : identiques, nœuds égaux.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche
`codex-etapes-chainees`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-72-etapes-chainees.md`.
