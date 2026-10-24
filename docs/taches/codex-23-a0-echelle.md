# Tâche Codex 23 : A0, le choix du but sur une échelle commune (sans changer les nuits)

Branche `codex-a0-echelle` (elle porte ce fichier, issue de `main` 42bb9c0), worktree dans `tmp-worktrees/`.
**Lot court (30 à 45 min) : suis la section « Rythme des lots » d'`AGENTS.md`.** Lis `docs/plan-agendas.md`
§ 6.1 et § 9 (A0) pour le contexte, sans en faire davantage ; puis `donjon/deliberation.py` : `urgents`,
`_candidats`, `candidats`, `choisir`.

Ne touche que `deliberation.py` (et la doc). Q (trajets réels) tourne sur `planification.py`, `obstacles.py`,
`part_estimee.py`, `defense.py`, `pnj._marcher` ; R sur `signes.py`, `relations.py`.

## Le constat
`_candidats` ordonne les buts par construction : des `insert(0, …)` (péril de l'eau, alarme, ranimer un
protégé), des `append` dans un ordre écrit à la main (besoins pressants par écart au seuil, parole due,
prévenir, attendre l'appelant, bruit à voir, pulsions rompues, progrès en cours), puis un tri stable sur le
seul drapeau `routine`, l'argent en dernier. L'ordre n'est dit nulle part ; on ne pourra pas y placer un agenda.

## L'invariant
Chaque candidat porte une **urgence** explicite et comparable, et l'ordre de `_candidats` est **le tri par
cette urgence**, rien d'autre (plus d'insertion en tête ni d'ordre d'ajout qui décide, sauf comme dernier
départage écrit dans la clé). L'échelle :
- des **paliers** nommés dans l'ordre actuel (péril de l'eau, alarme, ranimer, besoins pressants, parole
  due…, routine, argent) ;
- dans le palier des besoins pressants, une **valeur** : l'écart au seuil (celui de `urgents`), sur laquelle un
  agenda pourra plus tard se placer (§ 6.1) ; ne l'anticipe pas autrement.
L'ordre obtenu doit être **exactement** l'ordre actuel, égalités comprises. `choisir` (hystérésis entre recours,
`INERTIE`) ne change pas, sauf pour lire l'urgence si c'est plus simple.

## Vérifications (rien d'autre)
- Un test d'équivalence (`tests/test_echelle_choix.py`) : l'ancienne `_candidats` copiée dans le test comme
  référence ; sur des nuits jouées (quatre scénarios et `rixe`, 2 h, 2 graines) et sur des scènes qui
  déclenchent chaque palier (alarme, eau, protégé à terre, parole due, appel, bruit à voir, pulsion rompue,
  routine, argent), à chaque choix, même liste (besoin, rang, recours, identité de méthode) dans le même
  ordre. Plus un test de rechargement : même ordre après sauvegarde et rechargement.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).
- Empreintes : `tools/comparer_bancs.py --reference 42bb9c0 --empreintes` (2 h, quatre scénarios × 4 graines) :
  identiques. Pas de banc 8 h ni de Luna (ce sera à l'intégration).
- Doc : `docs/plan-agendas.md` § 6.1, les paliers et la valeur tels qu'implémentés ;
  `docs/etat-dev.md`, « Branche `codex-a0-echelle`, non fusionnée », compte de tests.

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport d'une page
`docs/taches/rapport-codex-23-a0-echelle.md` : l'échelle (paliers, valeur, départage), la preuve d'équivalence,
les empreintes, les limites.
