# Tâche Codex 171 (MJ) : une mesure résolue par le moteur, citée telle quelle, n'est pas refusée

Petit lot issu de l'attribution des relances (lot 168, famille « mesures » : « deux pas », `force-4c-fuir` p1/p2 t1 ; « deux mètres
au nord et trois à l'ouest », `atelier` p2 t8, vérification Luna `227c496`). Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC
fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal du dépôt, `AGENTS.md`).
Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (167 b, agendas) et un sur le laptop
(170, consignes) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche l'audit narratif et
ses preuves (`narration.py`), et leurs tests ; **pas** `consignes.py` (lot 170), `mj.py`, `agendas.py`/`deliberation.py`/
`planification.py`. **Bruts dans `C:\Users\msics\donjon\artifacts\mesures-171\`, jamais dans le worktree.** Si une revue automatique
bloque Luna ou la poussée, termine le reste, commite localement et écris la commande exacte dans
`C:\Users\msics\donjon\artifacts\mesures-171\luna-a-jouer.txt`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne)
ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 95 (preuve exacte des segments moteur), 116, 168 (attribution,
`C:\Users\msics\donjon\artifacts\relances-168\attribution.json`) et 169, puis les fils cités dans
`C:\Users\msics\donjon\artifacts\verif-luna-227c496\`.

## L'invariant
**Une quantité ou une position que le moteur a résolue et fournie (nombre de pas d'une fuite, déplacement en mètres, orientation
relative d'un repère), reprise par le récit avec la même valeur, est prouvée de façon déterministe comme les segments exacts du lot
95 ; une valeur différente reste refusée.** Établis d'abord dans les fils pourquoi l'audit refuse (motif, source absente du dossier,
format de la quantité) ; corrige à la source commune (dossier de l'audit qui porte la mesure résolue, ou preuve déterministe de la
valeur), sans mot-clé ni règle propre à une scène. Le lot 61 (orientation) et le lot 101 (mots courants) restent tenus.

## Vérification
- Tests MJ simulé/console après rechargement : les deux cas réels admis, une autre mesure résolue admise ; une valeur fausse (trois
  pas au lieu de deux, mauvaise direction) toujours refusée ; état et rendu inchangés.
- Rejeu des audits concernés (cinq fois chacun, base contre branche, critère du lot 95), puis Luna, **une passe** de
  `force-4c-fuir`, `atelier`, `relais` ; référence `cdaf371` relue du cache.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-mesures-resolues` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/etat-dev.md` (« Branche `codex-mesures-resolues`, non fusionnée »). Rapport d'une
page : `docs/taches/rapport-codex-171-mesures-resolues.md`.
