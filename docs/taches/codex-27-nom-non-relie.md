# Tâche Codex 27 : un nom que Corvus ne relie à personne de présent ne désigne personne, pour tout geste

Branche `codex-nom-non-relie` (elle porte ce fichier, issue de `codex-designations` 64351b2, lot 26 livré et non
encore fusionné), worktree dans `tmp-worktrees/`. **Lot court (30 à 45 min) : suis « Rythme des lots » d'`AGENTS.md`.**
Lis `docs/contrat-mj.md`, `docs/plan-ouie.md` (« Corrections de la parole » : nom inconnu, vocatif), le rapport du
lot 26, puis `donjon/noms.py`, `donjon/paroles.py` (`_vocatifs`, refus d'un nom inconnu), `donjon/commandes.py`,
`jeu.py` (ce qui part au MJ après un refus local).

**Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt principal, copies seulement).
Ne touche ni `planification.py`, `deliberation.py`, `pnj.py`, `signes.py`, `agendas.py`, `echanges.py`.

## Le constat (banc `echanges`, lots 22 et 26)
« je pousse Aubin » : Corvus connaît le nom « Aubin » mais ne l'a relié à aucune des personnes qu'il voit (le
vieil homme n'a pas dit son nom devant lui). La saisie part au MJ ; la contre-revue refuse puis accepte, selon
les passes, de rapprocher Aubin du vieil homme ; 5 à 11 appels. Même famille : « bonsoir, vous tenez le coup ? »,
où Luna nomme Ilse sans identité apprise (refusé par le garde nominal, réécriture, +2 appels).
Pour la parole, la règle existe déjà (« Tu ne connais personne du nom de X ici », `parole-corrections`) ; pour un
geste (pousser, frapper, donner, observer…) non : un jugement sémantique décide ce qui est déterministe.

## L'invariant
Qui un nom désigne pour Corvus se décide par le moteur (`noms`), pour toute saisie : un nom relié à une personne
présente la désigne ; un nom connu mais relié à personne de présent, ou inconnu, ne désigne personne. Dans ce cas
le refus est local, une cause, sans appel au MJ, en ligne comme hors ligne (« Tu ne sais pas lequel d'entre eux
est Aubin » si des inconnus sont là, « Tu ne vois pas Aubin d'ici » s'il est relié à un absent), comme les autres
refus locaux de désignation. Le MJ ne reçoit jamais une saisie dont le seul objet est un nom non résolu.
Côté narration, si Luna nomme quelqu'un que Corvus ne connaît pas sous ce nom, le garde existant suffit ; vérifie
seulement que les consignes et le contexte disent bien à Luna quels noms sont reliés à qui (sans en ajouter).

## Vérifications (rien d'autre)
- Tests après rechargement (`tests/test_nom_non_relie.py`) : « je pousse Aubin » (cas réel, banc `echanges`) et un
  autre geste de même nature (« je donne la cloche à Brune », Brune non reliée) ; contre-épreuve : nom relié,
  le geste part normalement ; nom relié à un absent ; 0 appel au MJ dans les cas refusés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).
- Luna, **une passe** : `echanges`, `noms-dialogue` (références dans `artifacts/references/` si elles existent).
- Doc : `docs/contrat-mj.md` ou `docs/plan-ouie.md` (la règle), `docs/etat-dev.md` (« Branche
  `codex-nom-non-relie`, non fusionnée » ; « À revoir »).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport d'une page
`docs/taches/rapport-codex-27-nom-non-relie.md`.
