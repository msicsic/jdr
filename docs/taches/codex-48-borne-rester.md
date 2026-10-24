# Tâche Codex 48 : une borne exacte pour les buts qui se tiennent en restant

Branche `codex-borne-rester` (elle porte ce fichier, issue de l'intégration **3aba83b** : lots 38 à 45 compris),
worktree dans `tmp-worktrees/`. Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop lents »).
Pas de Luna.

**Lots en même temps** : 49 sur ce même poste (`part_estimee.py` : les devis vides) ; 46 sur l'autre poste
(`planification.py` : `Vue.pertinent`, `emplois`, les gestes de prise de lumière) ; 47 (`paroles.py`, `mj.py`).
Ce lot touche `_explorer_etats` et la construction de la `Vue` ; ne touche ni `part_estimee.py`, ni les gestes de
lumière, ni `paroles.py`/`mj.py`. Deux lots font des bancs sur ce poste : priorité réduite, au plus 4 processus.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-cout-12h` lot 38, « Décisions prises le 2026-10-24 », `besoins`
« Ce qu'un plan laisse monter »), `docs/plan-planificateur.md` (`RESTER`, pression, borne du lot 38), puis
`donjon/planification.py` (`RESTER`, `Vue.pression`, `_explorer_etats`, les suites différées du lot 38, `_entrees`,
`_sans_plan`, `_parcours`, `VERIFIER`).

## Le diagnostic (mesuré sur l'intégration, graine 1985, 12 h)
Un but qui se tient en restant (garder, lumière, abri, se chauffer) compte `RESTER` × ce que son état final laisse
monter. Pour Lucien `garder:*` à l'auberge, rester coûte ~100 minutes : la recherche examine donc tout état de coût
inférieur, ~3 700 états par recherche, avec une borne nulle sur les états ordinaires (lot 38). Prototype : une borne
h = `RESTER` × plancher de pression (le minimum, sur les salles atteignables, de la somme des gardes laissées ailleurs
et de l'eau attendue), nulle pendant la passe de découverte de la lumière : **0 résultat changé sur 97 rejeux**,
nœuds −31 à −68 %, fenêtre 480-570 de l'auberge −24 %, chronique identique sur 12 h.

## L'invariant
**Pour un but qui se tient en restant, la recherche ordonne ses états par coût + une borne inférieure admissible et
cohérente de ce que coûtera le séjour final**, calculée une fois par `Vue` ; nulle quand on ne sait pas la minorer.
Démontre l'admissibilité (jamais plus que le vrai coût restant) et la cohérence (dans le code et le plan) ; les égalités
gardent leur rang historique ; le certificat d'absence et les graphes repris restent justes ; ce que lit la borne
entre dans `_entrees`. Mêmes décisions : aucun coût, prix, borne de nœuds ni donnée changé.

## Vérification (demandée expressément)
- Tests après rechargement : Lucien (capture `tests/data/cout-12h/auberge-1985-480.json.gz`) : moins d'états, même
  résultat ; un autre but qui se tient en restant (lumière ou abri, mine ou crue) ; l'égalité de rang et le certificat.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference 3aba83b`), quatre scénarios × 4 graines :
  identiques.
- **Temps sur 12 h** : `42bb9c0`, la base `3aba83b` et la branche **lancés ensemble**
  (`tools/empreintes_nuits.py jouer --heures 12 --scenarios mine auberge --graines 42 1985 --processus 2`), CPU par
  nuit et par tranche de 4 h, nœuds ; `comparer --calcul` base contre branche : identiques.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la borne, sa preuve),
`docs/etat-dev.md` (« Branche `codex-borne-rester`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-48-borne-rester.md` (preuve, fonctions, temps par tranche, nœuds, limites).
