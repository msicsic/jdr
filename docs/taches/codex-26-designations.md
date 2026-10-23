# Tâche Codex 26 : une désignation enrichie de qualificatifs compatibles désigne la même entité

Branche `codex-designations` (elle porte ce fichier, issue de `main` 42bb9c0), worktree dans `tmp-worktrees/`.
**Lot court (30 à 45 min) : suis « Rythme des lots » d'`AGENTS.md`.** Lis `docs/contrat-mj.md`, la section
« Textes et états relus » de `docs/taches/rapport-codex-22-luna-restes.md` (repli `soir-noir`, faux refus), puis
`donjon/noms.py`, `donjon/narration.py` (`voix_inconnues`, contrôles nominaux), `donjon/couverture_action.py`.

**Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt principal, copies seulement).
Ne touche ni `planification.py`, `deliberation.py`, `pnj.py`, `signes.py`, `agendas.py`, `echanges.py`
(lots en cours de fusion).

## Le constat (bancs du lot 22)
- `soir-noir`, « C'est moi, Brune » : le garde nominal refuse « la voix toute proche qui se dit Ilse » comme
  désignation d'une voix inconnue (la forme admise est « une voix qui se dit Ilse ») ; repli, 7 appels.
- La contre-revue juge « bobine de ficelle solide » différente de « bobine de ficelle ».
Un qualificatif de perception (proche, solide, vieille, à ta gauche) ajouté à une désignation admise ne change
pas l'entité désignée ; seul un qualificatif qui **contredit** ce qui est établi (une autre matière, un autre nom
prétendu, une autre place perçue) ou qui **ajoute un fait mécanique** (un nom, une identité) est en cause.

## L'invariant
Le moteur reconnaît une désignation par son noyau (la forme admise : nom d'objet, « une voix qui se dit X »,
désignation d'une personne) et traite à part ce qui l'entoure : un qualificatif compatible est de l'ambiance ou
de la description, admis ; un qualificatif qui contredit l'état ou ajoute une identité reste refusé, avec son
`attendu`. Même règle pour le garde nominal déterministe et pour ce que reçoit la contre-revue (la désignation
canonique jointe à la forme écrite, pour qu'elle ne compare pas deux chaînes). Pas de liste d'adjectifs propre à
un exemple.

## Vérifications (rien d'autre)
- Tests après rechargement, réponses simulées (`tests/test_designations.py`) : le cas réel de `soir-noir` (voix
  toute proche qui se dit Ilse) et un autre de même nature (une voix qui se dit Gorm, « basse et lointaine ») ;
  « bobine de ficelle solide » et un autre objet qualifié ; contre-épreuves : « la voix d'Ilse » pour une voix
  inconnue, « bobine de chanvre » si sa matière est autre : refusés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).
- Luna, **une passe** : `soir-noir`, `atelier`, `echanges` (référence 42bb9c0 dans le cache `artifacts/references/`
  si elle existe) ; textes relus.
- Doc : `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-designations`, non fusionnée » ; « À revoir »).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport d'une page
`docs/taches/rapport-codex-26-designations.md` : la cause lue dans les fils, l'invariant, les fonctions, les cas,
la passe Luna, les limites.
