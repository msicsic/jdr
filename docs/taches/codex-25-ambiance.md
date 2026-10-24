# Tâche Codex 25 : une ambiance admise se dit sans précaution qui la dément

Branche `codex-ambiance` (elle porte ce fichier, issue de `main` 42bb9c0, avec `codex-luna-restes` fusionné),
worktree dans `tmp-worktrees/`. **Lot court (30 à 45 min) : suis « Rythme des lots » d'`AGENTS.md`.**
Lis `docs/contrat-mj.md` (niveaux mécanique / interactif / ambiance), le constat 4 de
`docs/taches/rapport-codex-22-luna-restes.md` et l'entrée « Luna, après `codex-luna-restes` » d'« À revoir »
dans `docs/etat-dev.md` ; puis `donjon/narration.py` (`controler`, `INSTRUCTIONS_AUDIT`,
`INSTRUCTIONS_REVISION`, `REGLE_NARRATION`) et `donjon/consignes.py`.

**Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt principal, copies seulement).
Ne touche ni `planification.py`, `deliberation.py`, `pnj.py`, `signes.py`, `agendas.py`, `echanges.py`
(lots en cours de fusion).

## Le constat
Après le lot 22, Luna écrit encore une ambiance suivie d'une réserve qui la dément ou la met en doute :
« … aucun autre son n'est attesté ici », une odeur suivie d'une réserve sur son origine, ou refuse de préciser
une odeur « faute d'indication ». Le récit confond **absence de preuve** (le moteur ne dit rien de ce bruit)
et **absence de perception** (Corvus ne l'entend pas). Une ambiance compatible avec l'état est libre (contrat) :
elle se dit comme perçue, sans qu'une phrase de méta-preuve (« attesté », « rien n'indique », « tu ne peux pas
savoir ») vienne la qualifier.

## L'invariant
Dans le texte affiché, une phrase ne parle jamais de ce qui est **établi, attesté, indiqué ou connu du moteur** :
Corvus perçoit, ignore ou suppose, en termes de fiction. Trouve d'où vient la formulation (consignes,
`INSTRUCTIONS_REVISION`, verdicts de l'auditeur relancés, refus cités) et corrige à la source ; ajoute ce
vocabulaire de preuve au contrôle déterministe existant de la voix d'auteur et du méta-langage (le mécanisme
commun, pas une liste propre à un exemple), avec `attendu` pour le MJ. Une incertitude mécanique réelle (un
personnage hors de vue) reste dite en termes de perception (« tu ne le vois pas d'ici »).

## Vérifications (rien d'autre)
- Tests après rechargement, réponses simulées (`tests/test_ambiance.py`) : le cas réel (calme + « aucun autre son
  n'est attesté ici ») et un autre de même nature (odeur + réserve sur son origine) ; la reformulation admise est
  enregistrée avec son lieu, aucune entité créée ; une incertitude mécanique reste dite en perception.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).
- Luna, **une passe** : `relais`, `crypte`, `luna-restes-ambiance` (la référence 42bb9c0 est dans le cache
  `artifacts/references/` si elle existe, sinon `banc_multi` la joue une fois) ; textes relus : aucune précaution
  de preuve, aucune ambiance refusée à tort.
- Doc : `docs/contrat-mj.md` (la règle), `docs/etat-dev.md` (« Branche `codex-ambiance`, non fusionnée » ;
  « À revoir » mis à jour).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport d'une page
`docs/taches/rapport-codex-25-ambiance.md` : la cause lue dans les fils, l'invariant, les fonctions, les cas, la
passe Luna, les limites.
