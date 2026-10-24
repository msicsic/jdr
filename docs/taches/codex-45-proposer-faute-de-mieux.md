# Tâche Codex 45 (A2b) : un PNJ propose « faute de mieux »

Branche `codex-proposer-recours` (elle porte ce fichier, issue de l'intégration **bafb9b9** : lots 38 à 43
compris), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un
invariant, vérification minimale, rapport d'une page. Pas de Luna sur ce poste (aucun changement du MJ).

Un autre lot tourne sur l'autre poste (44, gestes hors de portée : `moteur.py`, `obstacles.py`, `mj.py`,
`consignes.py`). Ne touche pas à ces fichiers.

Lis `AGENTS.md`, `docs/etat-dev.md` (« Décisions prises le 2026-10-24 », la première ; lot 29 `codex-propositions`),
**`docs/plan-relations.md` § 7.2, le paragraphe « Décision du 2026-10-24 »** (il remplace le projet initial du geste
`proposer`), § 7.1 (l'évaluation), le rapport `docs/taches/rapport-codex-29-propositions.md`, puis
`donjon/echanges.py` (`evaluer_proposition`, `proposer`, `demander`), `donjon/propositions.py`, `donjon/agendas.py`,
`donjon/relations.py` (`chance_demande`), `donjon/deliberation.py` (`choisir`, `retenir_refus`, `tient`),
`donjon/planification.py` (la faute dans un plan : `prix_faute`, les gestes qui lèsent).

Les lots 33 et 36 (branche `codex-proposer-cout`, non fusionnée) ont fait du geste `proposer` une option de la
recherche : +344 à +534 % de calcul, et Brune volait toujours sans rien avoir proposé. **Ne reprends pas ce geste.**
Tu peux reprendre de leur code ce qui sert ici sans la recherche (`donjon/pnj_propositions.py` : contreparties
portées, chance, publication atomique ; `relations.chance_proposition`), en le disant.

## L'invariant
**Proposer est un recours de dernier ressort, tenté une fois quand les moyens ordinaires échouent**, jamais comparé
aux autres moyens par le planificateur :
- quand le plan retenu contient une **faute** (voler, forcer, consommer le bien d'autrui) contre quelqu'un, le PNJ
  propose d'abord au lésé, avant le premier geste fautif, s'il croit pouvoir lui parler ;
- quand une **demande** vient d'être refusée (refus retenu, `retenir_refus`), il peut proposer à celui qui a refusé.
Une fois par lésé ou refusant et par besoin, tant que rien de nouveau n'est cru (la règle des refus retenus). Les
contreparties sont ce qu'il porte (objet, part) et ses pièces ; **pas de tâche promise dans ce lot**. Il choisit,
sur ses croyances (`chance_demande`, valeur crue de la contrepartie, jamais l'attitude privée de l'autre), l'offre
qu'il croit la plus acceptable au moindre coût pour lui ; rien d'acceptable : il ne propose pas. L'auditeur juge par
`echanges.evaluer_proposition`, comme pour le joueur ; acceptée, l'échange se fait (engagements comme pour le
joueur) et le plan fautif est abandonné pour une nouvelle délibération ; refusée, le refus est retenu et le plan
fautif reprend. Le récit dit l'offre et la réponse. Ce que lit le recours n'entre pas dans la recherche ; s'il lit
quelque chose dans `deliberation`, qu'il soit sauvegardé et identique d'un laps découpé à l'autre.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : crue, Brune affamée devant la réserve, Gorm méfiant : elle offre ses
  pièces, refus, puis le vol ; Gorm sans méfiance : accepté, part remise, aucun vol ; un autre cas de même nature
  (mine, Odon et le garde-manger de Mathe, ou une demande refusée à l'auberge suivie d'une offre acceptée).
- Banc rapide (`tools/comparer_bancs.py --reference bafb9b9`, 4 h, 4 graines, quatre scénarios) : aucune
  usurpation, violation, plantage ni boucle nouvelle ; mesures `propositions`, `acceptees` (reprends celles des lots
  33/36 si elles existent), vols ; écarts lus en deux lignes.
- **Temps** : base et branche **lancées ensemble** (`--sans-cache`), 4 h, graines 42 et 1985, mine et auberge : au
  plus +5 %.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` § 7.2 (ce qui est fait sous la décision),
`docs/etat-dev.md` (« Branche `codex-proposer-recours`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-45-proposer-recours.md` (invariant, fonctions, mesures, ce qui reste de 3e, limites).
