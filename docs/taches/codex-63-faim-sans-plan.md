# Tâche Codex 63 : une recherche sans plan ne se refait que si une de ses lectures a changé

Branche `codex-faim-sans-plan` (elle porte ce fichier, issue de l'intégration **de3e986** : lots 38 à 59 compris), worktree
dans `tmp-worktrees/`. Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop lents »). Pas de Luna.
Le lot 60 (`appel.py`, `deliberation.rejoint`) entre dans l'intégration pendant ton lot : `git merge origin/integration`
au début si elle a avancé.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir », volet coût : **A, les entrées de la mémoire des recherches** et le
principe « réduire l'espace plutôt qu'ajouter un cache » ; entrées `codex-cout-suite` (certificats d'absence),
`planif-rapide`, `codex-trajet-estime` lot 30 (la case des personnes dans la clé), `codex-une-source` 46), **le rapport
du lot 62** `docs/taches/rapport-codex-62-salles-interet.md` (sur la branche `origin/codex-salles-interet`) et son outil
`tools/mesurer_salles_interet.py`, puis `donjon/planification.py` (`chercher`, `_entrees`, `_MEMOIRE`, `_GRAPHES`,
`_IMPOSSIBLES`, `_sans_plan`, `_parcours`, `VERIFIER`), `donjon/deliberation.py` (`attentes`, `_classer`).

## Le constat (lot 62, deux nuits de 12 h, graine 1985, sur 04bca30)
Après 8 h, à la mine, **Rémy/faim : 299 recherches épuisées, 600 694 nœuds, 84 % des nœuds** des recherches neuves ; à
l'auberge, **Joss/faim 165 bornées, Tilo/faim 118** : les deux faims font **90 % des nœuds**. Ces recherches ne trouvent
rien, et sont refaites encore et encore : leur clé exacte (`_entrees`) change (par exemple la case d'une personne qui a
bougé, une croyance sans rapport avec la faim), la mémoire ne les reprend pas, et le certificat d'absence ne vaut que
pour une recherche épuisée (les bornées n'en ont pas). Le filtre « salles d'intérêt » est réfuté (lot 62).

## D'abord, mesurer
Pour les recherches successives de Rémy/faim (mine 1985) et de Joss/faim (auberge 1985 fixe) : quels composants de
`_entrees` changent entre deux recherches identiques en résultat, et lesquels la recherche a **effectivement lus**
(trace des lectures pendant l'exploration : croyances, objets, personnes, relations, refus, prix). Chiffre la part des
recherches dont aucun composant lu n'a changé.

## L'invariant
**Une recherche dont aucune lecture n'a changé rend le même résultat sans être refaite** : la clé de la mémoire (et du
certificat d'absence) porte sur ce que la recherche a lu, enregistré pendant l'exploration (trace automatique), et non
sur un relevé écrit à la main de tout l'esprit. Exact par construction si toute lecture passe par la trace : prouve-le
(les lectures directes de `monde`/`Vue` hors trace sont recensées et routées, ou la trace se rabat sur la clé actuelle).
`VERIFIER` refait une recherche complète pour chaque reprise et compare. Si la trace n'est pas faisable proprement dans
ce lot, livre la mesure et un plan, sans code. Pas d'élargissement aux recherches bornées : une recherche bornée non
reprise reste refaite (elle n'a pas tout lu).

## Vérification (demandée expressément)
- Tests après rechargement : Rémy (capture `tests/data/cout-12h/mine-1985-480.json.gz`) : la seconde recherche sans
  lecture changée est reprise, même résultat, et une lecture changée (un vivre apparu, un refus levé) la fait refaire ;
  `VERIFIER` sans écart.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference de3e986`), quatre scénarios × 4 graines :
  identiques.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche **lancés ensemble** (`tools/empreintes_nuits.py jouer --heures
  12 --scenarios mine auberge --graines 42 1985 --processus 2`, tiré et fixe), CPU par nuit et par tranche, nœuds,
  recherches neuves et reprises ; `comparer --calcul` base contre branche : identiques.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la clé par lectures, sa preuve),
`docs/etat-dev.md` (« Branche `codex-faim-sans-plan`, non fusionnée » ; A dans « À revoir » mis à jour). Rapport d'une
page : `docs/taches/rapport-codex-63-faim-sans-plan.md` (mesure, règle, temps, reprises, limites).
