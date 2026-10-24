# Tâche Codex 30 : le planificateur raisonne par salle, avec un trajet estimé

Branche `codex-trajet-estime` (elle porte ce fichier, issue de l'intégration **ecbbed7** : lots 27 et 28 fusionnés),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un
invariant, vérification minimale, rapport d'une page. Pas de Luna sur ce poste.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-trajets-reels`, `codex-cout-trajets` et leurs fusions,
« À revoir »), les rapports `docs/taches/rapport-codex-20-trajets-reels.md` et
`rapport-codex-28-cout-trajets.md`, puis `donjon/planification.py` (`Etat`, `_explorer_etats`, `Vue.allers`,
`Vue.trajet`, `Vue.contacts`, `_entrees`), `donjon/obstacles.py` (`cout_route`, `parcours_cru`),
`donjon/part_estimee.py`, `donjon/pnj.py` (`parcours`, `chemin`, `_marcher`), `donjon/defense.py`
(`chemin_fuite`).

## Le constat (mesuré, nuit de 4 h, graine 42, avant Q → intégration)
Le surcoût des trajets réels vient du planificateur : autant de recherches, mais beaucoup plus d'états
(mine 4 186 → 15 001, auberge 3 445 → 23 987), surtout pour les buts profonds (Odon `argent`, 3 255 → 12 760
états, 76 % du temps de recherche ; Lucien `faim`, 1 339 → 15 666). Depuis Q, `Etat` distingue la case,
l'orientation et l'allure : deux ordres des mêmes gestes ne finissent plus au même état (près de la lampe ou
près du briquet), et chaque développement calcule un vrai trajet. Après le lot 28, une nuit coûte encore
×1,7 (mine) et ×2,3 (auberge) contre 42bb9c0.

## L'invariant (décision de l'utilisateur, 2026-10-24)
**Dans la recherche, le trajet s'estime ; il ne se mesure qu'à l'exécution.** L'identité d'un état de
recherche redevient la salle, les portes et les faits (plus l'allure seulement si un geste en dépend
vraiment : dis-le) ; ni case ni orientation. Le coût d'aller d'une salle à une autre, ou jusqu'à un objet
ou une personne dans une salle, est une **estimation propre à chaque salle**, tirée de sa géométrie et
calculée une fois par géométrie (pas une minute forfaitaire comme avant Q) : par exemple la distance réelle
moyenne entre ses entrées et entre une entrée et un point de la salle, au pas de l'allure, plus une rotation
moyenne. Choisis le critère, justifie-le, et mesure son erreur contre le vrai trajet sur les plans joués
(médiane, pire cas). Le supplément d'un passage sous ou par-dessus un obstacle, les portes, le noir et la
pression par salle restent comptés. **Une seule fonction de coût de route** dans la recherche
(`obstacles.cout_route` ou son remplaçant) ; l'exécution (`pnj._marcher`), la fuite du joueur
(`defense.chemin_fuite`) et ce que voit le joueur gardent le trajet réel. Ce que la recherche lit entre dans
`_entrees` ; `planification.VERIFIER` refait la recherche avec le même modèle.

Ce n'est pas un retour à l'avant-Q : un trajet court reste court, une grande salle coûte plus qu'une petite.
Les tests de Q qui fixent des secondes exactes de plan (allumer près / loin) s'adaptent à l'estimation :
garde ce qu'ils vérifient (près moins cher que loin, exécution en temps réel), dis chaque adaptation.

Hors de ce lot : fusionner des états par dominance sur la position (piste à mesurer seulement si
l'estimation ne suffit pas ; dis dans le rapport si elle apporterait encore quelque chose, sans la coder).

## Vérification (minimale)
- Tests ciblés : `tests/test_trajets_reels.py`, `test_cout_trajets` (ou ceux du lot 28), `test_sous_obstacle`,
  `test_defense`, `test_planification` ; un test nouveau après rechargement : même plan pour deux positions de
  départ dans la même salle, et une grande salle plus chère qu'une petite, exécution au temps réel.
- Banc rapide (`tools/comparer_bancs.py`, 4 h, 4 graines, quatre scénarios, contre l'intégration de base) :
  aucune usurpation, violation, plantage ni boucle nouvelle (`tools/audit_nuits.py` : bascules, passages par
  heure) ; écarts de mesures lus et expliqués en deux lignes.
- Temps : `42bb9c0`, la base et la branche **lancés ensemble** (`--sans-cache`), 4 h, graines 42 et 1985,
  mine et auberge, deux processus chacun ; nœuds et recherches bornées par nuit. Visée : au plus ×1,3
  contre 42bb9c0.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, graine 42, mine et auberge : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (le modèle de trajet de la
recherche), `docs/etat-dev.md` (« Branche `codex-trajet-estime`, non fusionnée » ; « À revoir » mis à jour).
Rapport d'une page : `docs/taches/rapport-codex-30-trajet-estime.md` (critère d'estimation et son erreur,
fonctions, temps et nœuds, écarts de comportement, limites).
