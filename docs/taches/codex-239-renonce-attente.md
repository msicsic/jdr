# Tâche Codex 239 : un recours renoncé faute de moyen admissible est une attente, pas un « sans recours »

Diagnostic du lot 237 (`docs/taches/rapport-codex-237-alertes-231.md`, « Mine : inactivité mal qualifiée ») : à la mine,
les minutes urgentes « sans recours » (3 → 58 PNJ·min par nuit au lot 231) viennent toutes d'Odon. Graine 500 : après le
renoncement de 103 devant les témoins, le choix de 105 garde la faim « pressante » alors que manger le pain de Lucien est
`renonce` et qu'aucun recours d'enquête ne reste ; première inactivité mal classée à **107**. Graine 7 : **539**, vivres
derrière le garde-manger, même obstacle de témoins retenu. `deliberation._classer` ne conclut « attente » que pour des
essais tous `rien` ; `renonce` laisse l'ancien classement, que `inactivite` lit comme `sans_recours`. Le refus de voler
reste justifié. Toujours présent sur l'intégration (275 et 145 PNJ·min, mêmes premières inactivités).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste** : celui indiqué au lancement ; au plus 2 processus, priorité réduite.

**Fichiers** : `deliberation._classer`, `inactivite` et le relevé « sans recours / en attente » du banc s'il lit ce
classement, et leurs tests (`tests/test_reessai_obstacle.py`, `tests/test_signalements.py`). **Pas** : `deliberation.choisir`
et son raccord à `pnj_propositions.plan_recours` (lot 236), `pnj_propositions` (lot 228), `biens.services_proteges` et
`menager_flamme` (lot 238), `pnj.py` (lot 234), `ouie.py` (lot 233), le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\renonce-239\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## L'invariant
**Le choix et le signalement partagent la même absence de moyen admissible.** Un recours renoncé dont l'obstacle cru
tient encore (lot 225 : témoins, verrou, refus, absent) compte comme essayé sans moyen admissible, comme un essai `rien` ;
si tous les recours du besoin sont dans ce cas, le PNJ est « en attente », pas « sans recours ». Dès que l'obstacle cru
change ou qu'un moyen nouveau paraît, le recours redevient possible (règle du lot 225, inchangée). Aucune règle propre à
Odon, à la mine ou à la faim.

## Vérification
- Captures des deux cas réels (graines 500 et 7, rejoue sur l'intégration) : classement « attente » à 107 et 539, et
  reprise dès un constat qui lève l'obstacle ; un autre cas de même nature (autre besoin ou scénario). Monde et rendu
  rechargés identiques, même laps d'un bloc ou découpé.
- Changement de mesure, pas de comportement attendu : empreintes 2 h (`tools/comparer_bancs.py --empreintes`), mine et
  Relais × quatre graines, chronique et état identiques ; dire si une décision change et pourquoi. Banc rapide 4 h mine ×
  quatre graines : « sans recours » et « en attente » avant/après.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-renonce-attente` poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-renonce-attente`, non fusionnée ». Rapport d'une page
  `docs/taches/rapport-codex-239-renonce-attente.md`.
