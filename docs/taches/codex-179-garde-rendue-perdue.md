# Tâche Codex 179 (A4b, suite du lot 175) : la garde finit quand le bien est cru rendu, remis ou perdu

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (178, enfermement et contre-revue) et une
vérification d'intégration sur le laptop (174) : au plus 2 processus de calcul, priorité réduite. Ce lot touche `agendas.py`,
`esprits.py` si besoin et leurs tests ; **pas** `tenir.py`, `couverture_action.py` (lot 178), `narration.py`, `consignes.py`,
`mj.py`, les scénarios historiques. **Bruts dans `C:\Users\msics\donjon\artifacts\garde-179\`, jamais dans le worktree.**
Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 4 `garder`, bilans 167 à 175), le rapport du lot 175 (fins constatées, croyance
`fin`, `agendas._fin_garde`), puis les croyances de possession et de lieu (`esprits`), les permissions (`biens.py`) et les
remises (`echanges.remettre`).

## L'invariant
**Un agenda `garder` d'un bien se termine, avec sa cause sauvegardée, publiée à la sortie du choix et sans renaissance, quand
son porteur croit que le bien n'est plus à garder pour lui : bien rendu à son propriétaire (ou remis par le gardien lui-même à
qui de droit), ou bien cru aux mains d'un autre sans permission (vu ou appris par une voie commune datée).** Même voie que la fin
constatée du lot 175 ; seules les croyances du gardien comptent ; une position inconnue ou non revue ne termine rien ; un bien
prêté avec permission ou confié ne termine pas la garde. Aucune règle propre à un objet, un personnage ou un scénario.

## Vérification
- Tests après rechargement, en données de tests (aucun agenda historique ajouté) : chaque cause sur deux cas de même nature ;
  prêt avec permission et position inconnue sans fin ; même laps d'un bloc ou découpé ; état et rendu rechargés identiques ;
  aucune reprise d'un agenda fini ; pas de double comptage avec la pulsion de garde (`prix_gardes`).
- Empreintes 2 h, quatre scénarios × quatre graines (`tools/comparer_bancs.py --empreintes`, références relues du cache) :
  identiques attendues hors données nouvelles, sinon écarts expliqués.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-garde-rendue-perdue` poussée (pas `main`).
`docs/plan-agendas.md` (A4b : fait et reste), `docs/etat-dev.md` (« Branche `codex-garde-rendue-perdue`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-179-garde-rendue-perdue.md`.
