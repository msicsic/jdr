# Tâche Codex 38 : le coût des nuits de 12 h, mêmes décisions

Branche `codex-cout-12h` (elle porte ce fichier, issue de l'intégration **63a717c** : Q, R, A0, A1, lots 25 à 32,
34, 35, 37), worktree dans `tmp-worktrees/`. Pas de Luna sur ce poste. Le lot 33/36 (les PNJ proposent) n'est pas
dans cette base et n'est pas à reprendre ici.

Lis `AGENTS.md`, `docs/etat-dev.md` (« Fusions des lots 31 et 32 » : **le coût sur 12 h** et son profil ; entrées
`codex-trajet-estime`, `codex-cout-exact`, `codex-part-estimee`, `codex-cout-suite`), `docs/plan-planificateur.md`,
puis `donjon/planification.py` (`chercher`, `_explorer_etats`, `gestes`, `_parts`, `_parts_remises`, `_plan_garder`,
`_entrees`, `_GRAPHES`, `_sans_plan`, `VERIFIER`, `BORNES`), `donjon/part_estimee.py` (`suites`, `_preparer`),
`donjon/obstacles.py` (`trajet_estime`, `cout_route`, `sejours_route`).

## Le constat (mesuré sur da13f9d, voir `docs/etat-dev.md`)
Contre `main` 42bb9c0, une nuit de 12 h coûte ×3,3 à ×4,4 (mine, auberge ; graines 42 et 1985), et le surcoût croît
avec l'heure : ×1,3 de 0 à 4 h, ×2,3 à ×5,7 de 4 à 8 h, ×3,7 à ×4,5 de 8 à 12 h. Presque tout est dans les recherches
de fin de nuit (Rémy `faim`, Josse `feu:poele`, Tilo et Joss `faim`, Mireille `feu:fourneau`, Lucien `garder`).
Profil auberge 1985, 8 h-9 h : 38 → 336 états développés par recherche, chacun 3,6 fois plus cher ; `_parts_remises`
52 % du temps, dont le devis 31 % ; `_plan_garder` 44 %. Mine 1985 : 7 % dans des `from . import` locaux de fonctions
chaudes (`_mesurer`, `sejours_route`, `perception.substance`, `Vue.arrivee`, `prix_route`, `route`).
Hypothèse, à confirmer ou infirmer d'abord, chiffres à l'appui : un trajet coûte maintenant des secondes et une
demande des minutes ; une recherche en coût uniforme développe donc presque tous les déplacements avant le geste qui
règle le besoin, et chaque développement recalcule les parts envisageables et leurs devis.

## L'invariant
**Une recherche ne développe que ce qui peut encore battre le meilleur coût connu, et chaque lecture coûteuse se
calcule une fois par état.** Mêmes décisions qu'avant. Trois moyens, dans cet ordre, chacun mesuré seul :
1. **Une borne inférieure admissible et cohérente** du coût restant (recherche A*) : jamais plus que le vrai coût,
   tirée de ce que la recherche lit déjà (par exemple le moins cher des gestes qui concluent le but, plus le trajet
   estimé minimal jusqu'à une salle où il peut avoir lieu). Justifie l'admissibilité dans le code et le plan ; borne
   nulle quand on ne sait pas borner. Le certificat d'absence (`_sans_plan`) et les graphes repris restent justes
   (dis comment). `VERIFIER` compare toujours à la recherche complète.
2. **Parts et devis une fois par état et par donneur** (et par lot), réutilisés par tous les gestes de cet état et
   d'un état équivalent ; clé exacte de tout ce qu'ils lisent.
3. **Imports des fonctions chaudes au niveau du module** (ou par une référence gardée), sans cycle nouveau.

Les décisions doivent rester identiques. A* peut changer l'ordre des visites : si deux plans de même coût échangent
leur rang, garde l'ordre actuel des égalités dans la clé de la file ; si tu ne le peux pas, compte les recherches
dont le résultat change et dis pourquoi aucune n'est plus chère. Ne change aucun coût, aucun prix, aucune borne de
nœuds, aucune donnée de scénario.

## Vérification (demandée expressément, hors du minimum d'un lot)
- Tests ciblés (`test_planification`, `test_planif_cout`, `test_cout_suite`, ceux de la part estimée,
  `test_trajet_estime`) ; un test nouveau : une recherche avec la borne développe moins d'états et rend le même
  plan, et le certificat d'absence reste prouvé, après rechargement.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference 63a717c`), quatre scénarios × 4 graines :
  identiques.
- **Temps sur 12 h** : `42bb9c0`, la base `63a717c` et la branche **lancés ensemble**
  (`tools/empreintes_nuits.py jouer --depot <worktree détaché> --heures 12 --scenarios mine auberge --graines 42 1985
  --processus 2`, une sortie par version), puis `empreintes_nuits.py comparer --calcul` base contre branche (mêmes
  nuits, mêmes résultats de recherches). Temps processeur par nuit et, si l'outil le permet, par tranche de 4 h ;
  nœuds et recherches bornées. **Visée : au plus ×1,5 contre 42bb9c0**, chaque moyen mesuré seul (au moins sur mine
  1985 et auberge 1985).
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, graine 42, mine et auberge : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la borne et son admissibilité, le cache
des parts), `docs/etat-dev.md` (« Branche `codex-cout-12h`, non fusionnée » ; « À revoir » mis à jour). Rapport d'une
page : `docs/taches/rapport-codex-38-cout-12h.md` (hypothèse vérifiée ou non, gain de chaque moyen, temps par
tranche, limites). Si la visée n'est pas atteinte, dis ce qui domine encore, profil à l'appui, sans élargir le lot.
