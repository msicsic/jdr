# Tâche Codex 175 (A4b, suite) : un agenda finit quand son objet cesse d'être, selon les croyances

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot tourne sur ce poste (172, contre-revue des gestes de force) et une
vérification d'intégration sur le laptop (174) : au plus 2 processus de calcul, priorité réduite. Ce lot touche `agendas.py`,
`deliberation.py`, `defense.py` si besoin, et leurs tests ; **pas** `couverture_action.py`, `tenir.py`, `consignes.py` (lot 172),
`mj.py`, `narration.py`, les scénarios historiques. **Bruts dans `C:\Users\msics\donjon\artifacts\fins-175\`, jamais dans le
worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Déjà livré : 167 (s'interposer), 167 b (`garder` sur le plan commun, fin à l'échéance), 167 c (`protéger` commun profil/agenda,
fin sur mort crue avec cause, position inconnue non terminale). Lis leurs rapports, `docs/plan-agendas.md` (§ 4 `garder` et
`protéger`, § 6, bilans 146 b à 167 c), puis `agendas.py` (transitions, causes, publication après le choix du lot 146 b).

## L'invariant
**Un agenda `garder` ou `protéger` se termine, avec sa cause sauvegardée et sans renaissance, quand son porteur croit que l'objet
de l'agenda n'est plus à garder : bien rendu à son propriétaire ou remis par le porteur, bien cru détruit ou consommé, bien cru
perdu (vu aux mains d'un autre sans permission, ou constaté absent de son dernier lieu connu), protégé cru parti hors d'atteinte
(départ vu ou appris, sans retour attendu).** Une position simplement inconnue ou non revue ne termine rien (lot 167 c). La
transition passe par la voie commune de `agendas.py`, publiée à la sortie du choix (lot 146 b) ; aucune lecture de l'état réel
hors des croyances, aucune règle propre à un objet, un personnage ou un scénario.

## Vérification
- Tests après rechargement, en données de tests (aucun agenda historique ajouté) : chaque cause sur deux cas de même nature
  (deux biens, deux protégés) ; position inconnue sans fin ; même laps d'un bloc ou découpé ; état et rendu rechargés identiques ;
  aucune reprise d'un agenda fini.
- Empreintes 2 h, quatre scénarios × quatre graines (`tools/comparer_bancs.py --empreintes`, références relues du cache) :
  identiques attendues (aucun agenda historique de ces sortes), sinon écarts expliqués.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-fins-agendas` poussée (pas `main`).
`docs/plan-agendas.md` (A4b : fait et reste : suivi à portée de voix, interposition d'un lieu), `docs/etat-dev.md` (« Branche
`codex-fins-agendas`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-175-fins-agendas.md`.
