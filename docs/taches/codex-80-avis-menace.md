# Tâche Codex 80 (A3 = 3f, première partie) : un PNJ dit son avis sur la menace d'un lieu à qui il croit en danger

Branche `codex-avis-menace` (elle porte ce fichier, issue de l'intégration **882907c** : lots 38 à 78 compris), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna (côté PNJ). **Un seul poste** :
priorité réduite, au plus 3 processus.

Ce lot touche `donjon/social.py` (`bavarder`, `nouvelles`, `recevoir`), `donjon/esprits.py` (formation d'une croyance de
menace), `donjon/eau.py` en lecture ; pas `planification.py`. Un autre lot tourne en même temps (bissection ou vérification).

Lis `AGENTS.md`, **`docs/plan-relations.md` § 7.3 « Les avis » et § 9 « 3f »** (épreuve de la crue : Aubin a vu l'eau aux
vannes, Gorm doute, Ilse croit et monte), `docs/plan-agendas.md` (A3 : « l'avis "la menace d'un lieu" est la brique de
l'évacuation »), `docs/etat-dev.md` (entrées `codex-constats-partages` 55, `codex-deja-dit` 64, `verifier-eau`,
`codex-route-admissible` 41, `codex-eau-plan-marche` 58), puis `donjon/social.py`, `donjon/esprits.py`, `donjon/eau.py`
(`menacee`, `attendue`, `estimation`), `donjon/relations.py`.

## Le manque
Un PNJ qui a vu l'eau monter vers une salle (et l'attend dans l'heure) ne le dit à personne : ceux qui se tiennent dans cette
salle ne l'apprennent qu'en voyant l'eau eux-mêmes. Le lot 55 confie des constats (l'eau observée) ; il ne confie pas
l'**avis** « cette salle sera gagnée », ni à **qui il croit en danger**.

## L'invariant (§ 7.3, seulement le prédicat « menace d'un lieu » dans ce lot)
**Un PNJ qui croit un lieu menacé par l'eau dans l'heure le dit, par les nouvelles communes, à qui il croit dans ce lieu (ou
en route vers lui) et dont il se soucie** (altruisme + empathie + affection envers lui ≥ 100, la règle du plan) ; l'auditeur
forme sa croyance par la règle des sources (vu ou essai 1 ; entendu 0,8 ; dit par X 0,7 × confiance/100 × (1 +
affection/200) ; deviné 0,4) : il la remplace si son poids × conviction l'emporte, sinon il garde la sienne (pas de dispute
dans ce lot). Sa croyance nouvelle entre dans ses plans par la lecture existante de l'eau attendue (`eau.attendue`), sans
règle propre : s'il croit sa salle menacée, il en sort selon les règles des lots 41 et 58. Le registre des faits dits (lot 64)
évite de le redire. Pas de cas propre à la crue ni à Aubin.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : l'épreuve du plan (crue : Aubin a vu l'eau aux vannes, le dit à Ilse et à
  Gorm au refuge ; Ilse, qui lui fait confiance, le croit et monte ; Gorm, qui ne lui fait pas confiance ou a vu autrement,
  garde son avis) ; un PNJ qui ne se soucie pas de l'autre ne dit rien ; l'avis dit une fois.
- Banc rapide (`tools/comparer_bancs.py --reference 882907c --processus 3`, 4 h, 4 graines, crue et Relais) : avis exprimés,
  changements d'avis, minutes dans l'eau, `eau_longue`, aucune usurpation ni boucle nouvelle. Puis l'audit 12 h de la crue
  500 et 2024, branche seule : où chacun finit.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (3f : ce qui est fait), `docs/etat-dev.md` (« Branche
`codex-avis-menace`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-80-avis-menace.md`.
