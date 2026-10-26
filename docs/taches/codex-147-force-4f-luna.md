# Tâche Codex 147 (force 4f) : Luna et les gestes de force

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste (dont une
vérification d'intégration qui joue des bancs) : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite.
Ce lot touche `consignes.py`, `mj.py`, `couverture_action.py`, `narration.py` et les schémas d'actions si besoin, les bancs
`tests/data/bancs/force-*` et leurs tests ; **pas** `agendas.py`, `deliberation.py`, `planification.py` (lot 146), ni les gestes
eux-mêmes (`tenir.py`, `corps.py`, `combat.py`) sauf un défaut de contrat commun révélé, dit au rapport. Termine ton dernier
message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, `docs/plan-force.md` (4f et les gestes 4d, 4e), les rapports des lots 12 (4b), 17 (4c),
126 (prises et liens), 134 (traîner), 136 (enfermer) et 145 (tuer), puis comment les actions 4b/4c sont déjà exposées au MJ
(`consignes`, schéma des actions, fiches et `attendu`).

## L'invariant
**Chaque geste de force que le moteur sait jouer (frapper, assommer, saisir, se dégager, ligoter, délier, traîner, enfermer,
tuer, fuir, riposter, se rendre) est proposable par le MJ sous sa forme typée, avec fiche avant tentative et `attendu` en cas
de refus ; aucun texte affiché n'affirme une mort, une perte de connaissance, une blessure ou un lien que le moteur n'a pas
établis ; aucun inconscient ni mort ne parle.** Expose les actions 4d/4e manquantes par la même voie que 4b/4c (une
description par action, aucune règle propre à une phrase) ; l'état du corps reste un domaine mécanique pour l'audit.
Contrôle les locuteurs autorisés de façon déterministe s'il ne l'est pas déjà (inconscient, mort).

## Vérification
- Tests MJ simulé/console après rechargement : chaque action nouvelle typée, préparée, exécutée et racontée ; une mort ou un
  évanouissement inventés refusés avant affichage ; un mort ou un inconscient qui parle refusé.
- Bancs Luna nouveaux `force-4f-*` (copies de scènes, comme 4b/4c) : « je la ligote avec la corde », « je l'achève »,
  « est-ce que je peux l'assommer ? », « je le traîne dans la crypte », « j'enferme Bram dans le bureau », un geste violent
  improvisé. **Une passe** de ces bancs et des cinq `force-4b-*`/`force-4c-*` ; critère : action typée ou refus juste en trois
  appels au plus, appels et secondes par tour MJ, aucune affirmation corporelle inventée.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-force-4f-luna` poussée (pas `main`).
`docs/plan-force.md` (4f), `docs/contrat-mj.md` si la règle change, `docs/etat-dev.md` (« Branche `codex-force-4f-luna`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-147-force-4f-luna.md`.
