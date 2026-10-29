# Tâche Codex 290 (refonte G0) : aligner la documentation du MJ sur le nouveau contrat

**Documentation seulement : aucun fichier sous `donjon/`, `tests/` ou `tools/`, aucun appel à Luna, aucun banc.**

Le nouveau « Contrat du MJ » est inscrit dans `AGENTS.md` (commit `424b599`), d'après les décisions de l'utilisateur
sur les lots 287 et 288 (sections « Décisions prises le 2026-10-29 » de `docs/etat-dev.md`,
`docs/conception-refonte-mj.md` section 10, `docs/conception-valeur-llm.md` section 8). **Ne modifie pas `AGENTS.md`** ;
s'il te semble contradictoire ou incomplet, dis-le dans le rapport (`QUESTION : …`).

## À faire
1. **`docs/contrat-mj.md`** (1 154 lignes). En tête : le contrat cible, renvoyant à `AGENTS.md` et aux deux documents de
   conception, avec la clause de transition. Pour chaque section existante, marque si elle :
   - **reste valable** (gardes de noms, références, refus et `attendu`, faits typés, portée des gestes…) ;
   - **est transitoire** (audit narratif du mécanique, révisions, explications de refus, contre-revue et fidélité de
     parole) : indique le lot G ou U de la refonte qui la remplace ;
   - **est caduque** sous le nouveau contrat.

   Ne supprime rien d'utile à la transition ; un contrôle reste décrit tant que son lot de portage n'est pas fusionné.
2. **`docs/plan-prompt.md`** et **`docs/plan-migration-mj.md`** : un encadré en tête qui dit ce que la refonte reprend,
   remplace ou rend sans objet (L0 à L8, phases 3 et 6 reportées).
3. **`docs/plan-refonte-mj.md`** (nouveau, court) : la feuille de route unique des lots de la refonte. Elle reprend
   l'ordre de la section 7 de `docs/conception-valeur-llm.md` :
   G0 → G2/G4/U-D → G1/U-P/U-C → G5/G6/G7/G20 → premiers U-M/U-T → G15 à G19 et menus sociaux → G12/G13 puis K0/K1/K2/D0
   → G14 et G8 à G11/U-A → G21.

   Une ligne par lot : invariant, dépendances, fichiers probables, mesures sur les quatre axes du gameplay
   (interprétation, vitesse perçue, invention à la volée, richesse des interactions PNJ). Une colonne « état » (à faire,
   en cours, fusionné). C'est le document que le superviseur tiendra à jour.
4. **`docs/etat-dev.md`** : une entrée « non fusionnée » pour ce lot ; dans « À revoir », renvoie les pistes MJ du lot
   (L2 à L8, audits) vers la feuille de route.

## Contraintes
- **Poste : le PC fixe.** Lecture et rédaction seulement.
- Phrases courtes, un fait par phrase, sans jargon inutile.

## Livraison
- Branche `codex-g0-contrat` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si la
  poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-290-g0-contrat.md`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
