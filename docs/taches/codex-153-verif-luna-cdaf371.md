# Tâche Codex 153 : vérification Luna de l'intégration cdaf371 (sans changer le code)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots MJ fusionnés depuis la vérification Luna
`9a39738` (lot 141) : 142 (déclaration erronée non confirmée, N9), 143 (contrats internes jamais affichés, N10), 147 (gestes de
force proposables par Luna) ; et des lots moteur 139, 140, 144 et 145 qui changent ce que Luna reçoit. **Aucun changement de
code du jeu** ; un défaut trouvé devient un petit lot, décrit avec son cas réel.

**Commit joué : `cdaf371`** (dernière fusion MJ). Les lots 150 à 152 le prennent pour référence : chaque partie jouée ici est
rangée dans le cache des références (`artifacts/references/<commit>/banc_multi/`) et leur servira sans rejeu. Si une partie de
`cdaf371` est déjà en cache (jouée par ces lots), relis-la.

**Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste, deux autres sur le laptop : Luna en
**trois exécutions au plus** pour ce lot, priorité réduite. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne)
ou par `QUESTION : …`.

Modèle : le lot 141 (`docs/taches/codex-141-verif-luna.md`, rapport `rapport-codex-141-verif-luna.md`). Référence `9a39738`
(parties en cache sur ce poste) : **relire, jamais rejouer**.

## Campagne
- Deux passes des vingt scripts du lot 141, plus `avis-joueur` et les onze bancs `force-4b-*`, `force-4c-*`, `force-4f-*` :
  `tools/banc_multi.py --variante integ=cdaf371 --variante ref=9a39738 --repetitions 2` (référence lue du cache ; les bancs de
  force sans référence en cache sont joués sur `cdaf371` seulement).
- Appels et secondes par tour MJ (moyenne et médiane), par fonction ; relances, refus, replis, audits illisibles ; jetons
  cachés par voie (`usage`).

## Ce que le rapport doit dire
- N9 (`soir-noir`, « Qui est là ? »), N10 (explications techniques affichées), N7 (rappel du nom), avis du joueur typés :
  corrigé, persistant ou non exercé, avec la passe et la saisie.
- Force : chaque geste 4b à 4f typé ou refusé juste en trois appels au plus ; les trois restes du lot 147 (traîner, enfermer,
  geste improvisé) sur deux passes ; aucune mort, perte de connaissance, blessure ou lien affirmés sans le moteur ; aucun mort
  ni inconscient qui parle.
- Les défauts déjà suivis : remboursement de Gorm, achats payés/livrés, fausse absence dans le noir, confusion de récit des
  planches : statut.
- Les défauts nouveaux, chacun avec son cas réel et l'invariant en cause.

## Livraison
Branche `codex-verif-luna-cdaf371` : seulement `docs/taches/rapport-codex-153-verif-luna.md` (une page) et une entrée
« Vérification Luna cdaf371 » dans `docs/etat-dev.md`. Commits signés si une clé est configurée, branche poussée (pas `main`).
Bruts dans `C:\Users\msics\donjon\artifacts\verif-luna-cdaf371\`.
