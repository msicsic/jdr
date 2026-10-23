# Tâche Codex 13 : `GARDE` et `PRET` tirés des valeurs et des relations

Branche `codex-garde-pret` (elle porte ce fichier, issue de `main` après la fusion des relations 3b et du
corps blessable 4a), worktree dans `tmp-worktrees/`. Lis `AGENTS.md`, `docs/etat-dev.md` (« Décisions
prises le 2026-10-22 » : « `GARDE` et `PRET` à tirer des valeurs et des relations » ; entrées `besoins`,
`petits-correctifs-pnj`, `pnj-lumiere-garde`, `codex-relations-3b`), `docs/plan-planificateur.md`
(« Dynamique des besoins », « Lumière et garde »), `docs/plan-relations.md` (§ 6.3, § 7.2, 3e).

## Aujourd'hui
Deux constantes du planificateur (`donjon/planification.py`) :
- `GARDE = 2` : coût par minute loin de chaque lieu où il garde ses biens, quand ils le pressent, et pour
  un bien menacé (`deliberation.menaces`). Le même pour tous : le plus attaché à ses biens comme le
  plus détaché.
- `PRET = 0.5` : chance qu'on accède à une demande (objet porté, part, tâche, `DEMANDE / PRET`). La même
  quelle que soit la personne à qui l'on demande.

## L'invariant
- `GARDE` vient du PNJ : de ses valeurs (déclarées une fois, par exemple l'ambition pour ce qui est à
  soi, la loyauté pour une garde confiée ; à justifier dans le plan) et de ce qu'il éprouve envers qui il
  croit près de ses biens (relations 3b : méfiance, rancune, peur). Un attachement neutre (valeurs à 50,
  personne de suspect) doit redonner à peu près l'ancien 2.
- `PRET` devient une chance estimée par le demandeur, sur ce qu'il sait : ce qu'il éprouve envers l'autre
  et ce qu'il en a vécu (refus retenus, dettes, services rendus, s'il sait que l'autre l'a vu fauter),
  jamais ce que l'autre éprouve réellement (le moteur ne lit pas dans la tête de l'autre). La lecture
  des signes (3c) affinera plus tard cette estimation, et le plan la fera disparaître en 3e (geste
  `proposer`) : écris-la à un seul endroit (`relations` ou une fonction du planificateur), que 3c et 3e
  pourront enrichir.
- Les deux entrent dans `planification._entrees` : `VERIFIER` sans écart.

## Vérifications
- Tests après rechargement : Gorm, qui garde ses biens et se méfie de Brune, s'en éloigne moins qu'un
  gardien sans méfiance ; un demandeur qui a été bien servi par quelqu'un lui demande plutôt qu'à un autre
  qui l'a refusé ; un autre cas de même nature par règle (mine ou auberge).
- `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, de chaque
  scénario, sans écart. Suite complète verte (`tools/tests.py`).
- Bancs : rapide (4 h, 4 graines, quatre scénarios) puis 8 h, `main` puis la branche
  (`tools/comparer_bancs.py`, `--processus 4` au plus) : demandes, refus, achats, minutes sans recours et
  en attente, éloignements de ses biens, vols vus, usurpations et violations (aucune), temps.
- Docs : `docs/plan-planificateur.md`, `docs/plan-relations.md` (ce qui est fait de § 6.3 et ce qui reste
  à 3e), `docs/etat-dev.md` (« Branche `codex-garde-pret`, non fusionnée », compte de tests).

## Rapport
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-13-garde-pret.md` : règles, valeurs choisies et pourquoi, cas vérifiés,
mesures avant → après, limites, réglages proposés. Ce lot touche `planification` comme `codex-relations-3c`
et `codex-lampes-suite` : garde les changements localisés.
