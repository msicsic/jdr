# Tâche Codex 71 : le coût fixe d'un choix se paie une fois, mêmes recherches

Branche `codex-cout-fixe` (elle porte ce fichier, issue de l'intégration **fbcf0ff** : lots 38 à 68 compris), worktree dans
`tmp-worktrees/`. Lot de coût, demandé par l'utilisateur (« les bancs sont trop lents »). Pas de Luna. **Un seul poste** :
priorité réduite, au plus 3 processus ; les trois versions des mesures de 12 h ensemble, **un processus chacune**. Le lot
66 (certificat d'absence : `_sans_plan`, `_parcours`, `_explorer`) et le lot 72 (`_explorer_etats`, étapes) peuvent
entrer dans l'intégration pendant ton lot : `git merge origin/integration` au début si elle a avancé ; garde tes
changements loin de ces fonctions.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir », volet coût : **« Coût fixe, mêmes nœuds »**, points (a) et (b), et le
principe « réduire l'espace plutôt qu'ajouter un cache »), `docs/plan-planificateur.md`, puis `donjon/planification.py`
(`Vue.__init__`, `_entrees`, `chercher`, les appels de `Vue(monde, id)` : une dizaine), `donjon/deliberation.py`
(`_candidats`, `choisir` : les candidats d'un même choix appellent chacun leur recherche), `donjon/obstacles.py`
(`metrique_necessaire` et les deux autres clés `json.dumps(... m.data["salles"] ...)`, lignes ~154, 270, 372).

## Le constat (revue externe du 2026-10-24, vérifié dans le code ; diagnostic du coût)
- Pour chaque candidat d'un même `choisir` (faim, enquête, pulsions, garder, créance…), une `Vue(monde, id)` neuve est
  construite et `_entrees` recalcule et sérialise tout ce qui ne dépend pas du but, alors que ni le monde ni l'esprit n'ont
  changé entre deux candidats. Le diagnostic mesurait ~17 % de coût fixe à l'auberge (2 200 vues et entrées pour 1 350
  recherches, reprises de la mémoire comprises).
- `obstacles.metrique_necessaire` (et deux clés voisines) sérialisent toute la géométrie du scénario
  (`json.dumps(m.data["salles"], …)`) à chaque appel pour leur clé de cache, alors que les calculs réels sont rares.

## L'invariant
**Ce qui ne dépend que de l'état du monde et de l'esprit se calcule une fois par état, pas une fois par candidat ni par
appel** : la `Vue` et la partie de `_entrees` indépendante du but sont partagées par les candidats d'un même choix tant
que rien n'a changé (une clé exacte et bon marché de cet état, ou un partage limité au même appel de `choisir` — préfère
le plus simple qui est exact), et les clés de géométrie reposent sur une identité immuable de la carte (révision des
salles, ou empreinte calculée une fois par révision) au lieu de la sérialiser. **Mêmes recherches, mêmes nœuds, mêmes
décisions** : rien ne change dans ce que lit la recherche ; `VERIFIER` et `spatial.VERIFICATION` restent sans écart.

## Vérification (demandée expressément)
- Mesure avant/après au profileur (même nuit, même fenêtre) : part de `Vue.__init__`, `_entrees`, des clés de géométrie.
- Tests : une vue partagée invalidée dès que le monde ou l'esprit change (un objet déplacé, une croyance) ; la clé de
  géométrie change quand une salle change (porte, obstacle) ; mêmes résultats sur les captures `tests/data/cout-12h/`.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference fbcf0ff --processus 3`), quatre scénarios ×
  4 graines : identiques.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche **lancés ensemble**, un processus chacune
  (`tools/empreintes_nuits.py jouer --heures 12 --scenarios mine auberge --graines 1985 --processus 1`, tiré et fixe) ;
  `comparer --calcul` base contre branche : identiques, nœuds égaux.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche
`codex-cout-fixe`, non fusionnée » ; « À revoir » mis à jour). Rapport d'une page : `docs/taches/rapport-codex-71-cout-fixe.md`.
