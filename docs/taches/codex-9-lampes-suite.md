# Tâche Codex 9 : la suite des parts pour les lampes

Branche `codex-lampes-suite` (elle porte ce fichier, issue de `main` 9075aea), worktree dans
`tmp-worktrees/`. Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-lampes`, `lumiere-besoin`,
`cout-calcul`), `docs/taches/rapport-codex-3-lampes.md` et `docs/plan-planificateur.md` (« Lumière »,
« Coût de calcul, suite »).

## Trois points relevés à la fusion de `codex-lampes`
1. **Une règle par capacité** : `planification._parts_remises` compte un besoin de recharger une source
   pour qui a peur du noir, qui vise d'éclairer, **ou qui sait crocheter**
   (`"crochetage" in profil(...)["capacites"]`). C'est une heuristique liée à une capacité, pas un
   invariant. Invariant attendu : une part pour une source est envisagée quand la source chargée et
   allumée sert le but en cours, d'après ce que le but emploie (`vises`, la lumière qu'exige un geste du
   plan, comme la chance de crocheter selon `lumiere_crue`), pour n'importe quel geste qui dépend de la
   lumière. Garde la mémoire des recherches juste (`_entrees`, `VERIFIER`).
2. **Le noir de la crue** : au banc 8 h, minutes dans le noir 33,75 → 48,75 par nuit (min·PNJ), sans
   recours en hausse. Trouve la cause dans les chroniques (`--rejeu` aide) : défaut commun à corriger, ou
   conséquence voulue à expliquer.
3. **Le temps de l'auberge à 12 h** : le rapport mesure une nuit de 12 h à l'auberge 120 → 249 s et la
   mine 118 → 183 s. Remesure sur `main` actuel (après `cout-calcul`), contre la base d'avant les lampes
   (f1eee53) si utile ; si l'écart tient, trouve le poste (`py-spy` ou `tools/empreintes_nuits.py`) et
   allège-le sans changer les nuits (empreintes identiques), ou dis pourquoi c'est le prix du comportement.

## Vérifications
- Tests après rechargement (`tests/test_lampes_parts.py` étendu ou un fichier nouveau) : le cas réel de
  chaque point corrigé et un autre de même nature (un geste dépendant de la lumière autre que le
  crochetage, un personnage sans peur du noir ni capacité de crochetage).
- Suite complète verte (`tools/tests.py`) ; `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h,
  puis `VERIFIER` + `VERIFICATION 0,2` sur 8 h graine 42, de chaque scénario.
- Bancs : rapide (`tools/comparer_bancs.py`, 4 h, 4 graines, quatre scénarios) et 12 h auberge et crue
  (`tools/audit_nuits.py`, 4 graines), `main` puis la branche, `--processus 4` au plus ; noir, recharges,
  parts demandées / données / achetées / livrées, sans recours, en attente, usurpations et violations
  (aucune), temps au processeur.
- Docs : `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche `codex-lampes-suite`, non
  fusionnée », compte de tests).

## Livraison
Commits signés comme d'habitude ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-9-lampes-suite.md` : invariant, fonctions changées, cas vérifiés, mesures
avant → après, limites. La branche sera fusionnée après les relations 3b (qui changent aussi
`planification._entrees`) : garde les changements de la mémoire des recherches lisibles.
