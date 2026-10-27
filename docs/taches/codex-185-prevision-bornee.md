# Tâche Codex 185 : une observation sèche récente borne une prévision d'eau ancienne

Correctif issu du diagnostic 182 (`docs/taches/rapport-codex-182-attente-hameau.md`, bruts et captures
`C:\Users\msics\donjon\artifacts\attente-182\`, dont `entrees-exactes-42/` et `sensibilite-pentes.json`). Lot de 30 à 45 minutes
(`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Un autre lot tourne sur ce poste (184 : `agendas.py`, `deliberation.py`) : au plus 2 processus de calcul, priorité réduite. Ce lot
touche `eau.py`, les fonctions de prévision d'eau de `esprits.py` (`prevision_propre` et voisines) et leurs tests, et les entrées de
recherche si une lecture change (`planification._entrees`) ; **pas** `agendas.py`, `deliberation.py` (lot 184), `narration.py`,
`mj.py`. **Bruts dans `C:\Users\msics\donjon\artifacts\prevision-185\`, jamais dans le worktree.** Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-crue.md`, les rapports 41, 58, 80, 163 et 182, puis `eau.observer`, `eau.estimation`, `eau.attendue`,
`esprits.prevision_propre` et leurs lecteurs (`Vue.descente`, routes, `route_admissible`).

## L'invariant
**Une observation récente d'une salle (sèche, ou à un niveau mesuré) borne toute prévision extrapolée d'une mesure plus ancienne qui
la contredit au présent : la prévision repart de ce qui a été vu, sans inventer de pente nulle ni lire l'eau d'une salle non
observée.** Même contrat pour l'observation, la prévision, les routes, la clé de recherche et la sauvegarde ; une prévision reçue
par un avis suit la même borne. Les captures du lot 182 (Sève et Maël, hameau 42 ; Ilse à 420) sont les cas réels ; aucune règle
propre à un PNJ, une salle ou un scénario.

## Vérification
- Tests après rechargement : Sève retrouve sa route des vivres et Maël son abri dans les captures 182 ; une autre salle et un autre
  PNJ (crue historique) ; une pente toujours valable (pas d'observation contraire) reste appliquée ; une salle non revue garde sa
  prévision ; le refus d'une route réellement menacée tient (lots 41, 58) ; même laps d'un bloc ou découpé ; monde et rendu rechargés.
- Banc rapide 4 h, crue et hameau × quatre graines (références du cache) : attente, eau, noir et passages relevés, aucune usurpation,
  plantage ni boucle nouvelle ; empreintes 2 h Relais/mine/auberge identiques (sans eau active).
- `VERIFIER` + `spatial.VERIFICATION` 0,2, crue 2024 et hameau 42, 2 h.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-prevision-bornee` poussée (pas `main`).
`docs/plan-crue.md` (la règle change), `docs/etat-dev.md` (« Branche `codex-prevision-bornee`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-185-prevision-bornee.md`.
