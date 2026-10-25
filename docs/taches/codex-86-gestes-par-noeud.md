# Tâche Codex 86 : générer les gestes d'un nœud sans refaire ce qui ne dépend pas de lui

Branche `codex-gestes-par-noeud` (elle porte ce fichier, issue de l'intégration après la fusion du lot 81 —
`git merge origin/integration` au début), worktree dans `tmp-worktrees/`. Lot de coût. Pas de Luna. **Un seul poste** :
priorité réduite, au plus 3 processus ; mesures de 12 h, trois versions ensemble, **un processus chacune**. Ce lot touche
`planification.gestes` et ce qu'il appelle ; pas le récit (les lots 83 et 85 du MJ tournent en même temps).

Lis `AGENTS.md`, **le rapport du lot 81** (`docs/taches/rapport-codex-81-cout-par-noeud.md` : après lui, `gestes` coûte
encore **≈ 461 µs par nœud** chez Joss/faim, contre 150 µs/nœud au total sur `42bb9c0` ; `route` 138 µs ; « génération et
premiers calculs géométriques restent coûteux ») et son outil `tools/profiler_cout_noeud.py`, le rapport du lot 76
(bissection), `docs/plan-planificateur.md`, puis `donjon/planification.py` (`gestes` et chaque famille de gestes, `Etat.apres`,
`_normaliser_suites`).

## Le constat
Sur 12 h, après le lot 81, l'auberge coûte encore ×2,7 (départ fixe) à ×4,5 (tiré) contre `42bb9c0`, presque tout entre 8 et
12 h (fixe : 377 s sur 453). Le coût par nœud est désormais dominé par la **génération des gestes**.

## D'abord, mesurer
Avec `tools/profiler_cout_noeud.py` sur la capture auberge 1985 à 480 (Joss/faim) et sur une capture plus tardive de la même
nuit (vers 600, à créer si besoin), décompose `gestes` par famille (aller, prendre, demander/acheter/proposer, parts,
recharges, portes, attendre…) et par sous-calcul (lecture des objets, permissions, prix, `Etat.apres`), en µs/nœud.

## L'invariant
**Ce qu'une famille de gestes lit et qui ne dépend pas du nœud (objets d'une salle, permissions, prix, candidats d'une salle
pour un but) se prépare une fois par `Vue` ou par clé exacte des parties du nœud qu'il lit, et se lit ensuite** ; ce qui dépend
du nœud se calcule seulement pour lui. **Mêmes gestes, même ordre, mêmes coûts au bit près, mêmes nœuds, mêmes décisions.**

## Vérification (demandée expressément)
- Profil avant/après (µs/nœud par famille), nœuds égaux ; tests : mêmes successeurs, même ordre, pour des états variés des
  captures mine et auberge.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference <base> --processus 3`), quatre scénarios × 4 graines.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche lancés ensemble, un processus chacune (`tools/empreintes_nuits.py jouer
  --heures 12 --scenarios mine auberge --graines 1985 --processus 1`, fixe et tiré) ; `comparer --calcul` : identiques.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche
`codex-gestes-par-noeud`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-86-gestes-par-noeud.md`.
