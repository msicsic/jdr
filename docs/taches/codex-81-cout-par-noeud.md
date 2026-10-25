# Tâche Codex 81 : un nœud coûte ce qu'il coûtait avant les trajets réels

Branche `codex-cout-par-noeud` (elle porte ce fichier, issue de l'intégration **cf08508** : lots 38 à 80 compris), worktree
dans `tmp-worktrees/`. Lot de coût, demandé par l'utilisateur (« les bancs sont trop lents »). Pas de Luna. **Un seul
poste** : priorité réduite, au plus 3 processus ; mesures de 12 h, trois versions ensemble, **un processus chacune**.

Lis `AGENTS.md`, **le rapport du lot 76** (`docs/taches/rapport-codex-76-bissection-auberge.md`, dans l'intégration) et son
outil `tools/mesurer_bissection_auberge.py`, `docs/etat-dev.md` (entrées `codex-trajets-reels` (Q), `codex-trajet-estime`
30, `codex-cout-exact` 31, `codex-cout-12h` 38, `codex-cout-fixe` 71), `docs/plan-planificateur.md`, puis
`donjon/planification.py` (`gestes`, `_mesurer`, `Vue.prix_route`, `Vue.route`, `Vue.allers`, `Vue.trajet`, `Vue.pression`),
`donjon/obstacles.py` (`cout_route`, `sejours_route`), `donjon/trajet_estime.py`.

## Le constat (lot 76, bissection de l'auberge 1985, départ fixe, 12 h)
Le premier et le plus grand saut est **Q (trajets réels) : 144 → 624 s CPU (+332 %) à nœuds presque égaux** (936 162 →
947 538) ; Joss/faim **462 089 → 442 922 nœuds mais 27 → 136 s** : **chaque nœud coûte environ cinq fois plus** depuis Q
(cases, orientations, allures et tarifs réels dans la génération et la tarification des gestes). Le lot 31 a repris une partie
(1 149 → 342 s), le reste des marches vient de nuits qui divergent (calibration +51 %, lot 45 +51 %, lot 55 +67 % : plus de
recherches bornées). Le lot 76 recommande : « génération/tarification par état fixé ».

## D'abord, mesurer
Sur la capture `tests/data/cout-12h/auberge-1985-480.json.gz` et une recherche Joss/faim, au profileur, à **42bb9c0** (un
worktree détaché, son lanceur) et sur la base : temps par nœud et sa décomposition (génération des gestes, `_mesurer`,
`prix_route`, `route`, `pression`, normalisation, tas). Dis ce qui, par nœud, a été ajouté par Q et reste après le lot 31.

## L'invariant
**Ce qu'un nœud lit de la géométrie et des tarifs ne dépend que de sa salle, de ses portes et des faits de route ; cela se
calcule une fois par `Vue` (ou par clé exacte de ces entrées) et se lit ensuite**, au lieu d'être remesuré à chaque
développement : une table des coûts de route entre salles et vers les cibles de chaque salle, par allure, avec leurs
pressions et leurs suppléments de passage, construite paresseusement et partagée par tous les nœuds de la recherche (et
par la référence de `VERIFIER`). **Mêmes coûts au bit près, mêmes nœuds, mêmes décisions.** Pas de changement de modèle de
trajet.

## Vérification (demandée expressément)
- Profil avant/après sur la capture (temps par nœud, nœuds égaux) ; tests de la table (porte ouverte/fermée, obstacle, eau
  attendue, allure, lumière) : coûts identiques à la mesure directe.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference cf08508 --processus 3`), quatre scénarios × 4 graines :
  identiques.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche **lancés ensemble**, un processus chacune (`tools/empreintes_nuits.py
  jouer --heures 12 --scenarios mine auberge --graines 1985 --processus 1`, fixe et tiré) ; `comparer --calcul` base contre
  branche : identiques, nœuds égaux. Visée : l'auberge sous ×2 contre `42bb9c0`.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche
`codex-cout-par-noeud`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-81-cout-par-noeud.md` (profil
avant/après, ce qui coûtait, temps par tranche, limites).
