# Tâche Codex 164 (MJ) : un avis du joueur sur une menace est saisi comme un avis

Petit lot de correction (limite des lots 124 et 128, encore 3/6 au lot 153). Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le
PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (163, délibération) et un sur le laptop (161,
consignes et assemblage des instructions de `mj.py`) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité
réduite. Ce lot touche les définitions communes des contenus de parole (`paroles.py` : `SENS_CONTENU`, schéma de parole,
analyse des opérations) et la voie de la parole de `mj.py` si nécessaire, avec leurs tests ; **pas** `consignes.py`, l'assemblage
des instructions de `mj._echanger`, les `REGLES` (lot 161), `narration.py`, `deliberation.py`/`planification.py` (lot 163).
**Bruts dans `C:\Users\msics\donjon\artifacts\avis-164\` (dépôt principal), jamais dans le worktree.** Termine ton dernier message
par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 124 (avis du joueur), 128 (opérations analysées avant le contenu),
141 et 153 (avis 2/3 puis 3/6), et les fils `avis-joueur` du lot 153 (`C:\Users\msics\donjon\artifacts\verif-luna-cdaf371\`).

## Le défaut
Dans `avis-joueur`, « l'eau va gagner la conduite basse / la galerie de ronde » est typé `propos` (sans effet) une fois sur deux :
p1 avis/propos/avis, p2 propos/propos/avis. Le mode `propos` est réservé à l'absence d'opération applicable (lot 128).

## L'invariant
**Une parole du joueur qui exprime une prévision de menace sur un lieu connu est typée `avis` (sujet, menace, valeur) ; `propos`
ne la couvre pas.** Établis d'abord dans les fils la cause : définition de `avis` trop étroite ou ambiguë dans `SENS_CONTENU`,
analyse des opérations qui ne la propose pas, revue de fidélité qui admet `propos`, raccourci des mots exacts. Corrige le contrat
commun (définition, couverture des opérations, refus d'un `propos` qui omet une opération reconnue) ; aucun mot-clé ni règle
propre à l'eau, à un lieu ou à un script.

## Vérification
- Tests MJ simulé/console après rechargement : les trois saisies du banc typées `avis` (réception par les PNJ, faits dits),
  une parole ordinaire restée `propos`, une prévision sur un lieu inconnu refusée avec `attendu`.
- Luna, **deux passes** de `avis-joueur` et une de `noms-dialogue`, `soir-appel` ; référence `cdaf371` relue du cache ; avis
  typés sur six, appels par tour.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-avis-saisie` poussée (pas `main`). `docs/contrat-mj.md`
si la règle change, `docs/etat-dev.md` (« Branche `codex-avis-saisie`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-164-avis-saisie.md`.
