# Lot 55 — Constats matériels partagés

Branche `codex-constats-partages`, non fusionnée ; base d'intégration `5b174ad`. Aucun appel à Luna.

**Invariant.** Un état matériel récemment vu ou essayé se confie par les nouvelles communes à un proche
de confiance : ressource épuisée, contenant ouvert vide, verrou, source éteinte, eau observée. Accusations
prioritaires ; une confidence par minute du jeu, repère sauvegardé commun à toutes les nouvelles. Destinataire et
témoins passent par `recevoir` : source `dit:`, confiance/rang du ouï-dire, date originale conservée.
Un constat propre de même minute ou postérieur prime. Revoir le même état ou l'apprendre autrement
ne le fait pas redire au même auditeur ; son suivi est sauvegardé dans la croyance.

**Fonctions.** `social._constats`, `nouvelles`, `bavarder`, `_adopter` et `phrase` assurent transmission et
parole. `esprits.croire` préserve les destinataires ; `constater` établit le vide visible. Prérequis
révélé au banc : une source mobile peut avoir quitté sa dernière case ; son absence n'établit plus son
extinction (`_flamme_sous_les_yeux`). `pnj` valide la mesure `constats_confies` ; `derniere_confidence`
borne les nouvelles sans changer la durée des paroles. `deliberation`, `planification.py` et les accords français inchangés.

**Vérification.** Douze tests nouveaux : gestes réels sur vivres épuisés/verrou, parole et état après
recharge, autres constats, date/vitesse de l'eau, déjà-su, relais/observation, confiance, priorité,
refus retenu, source transportée ; même laps découpé, égalité de tout `data`, au plus une confidence par minute.
Les anciennes scènes de jets préparés ou d'embuscade isolent les confidences ordinaires ; les autres
assertions visent l'accusation, le chemin sûr ou la livraison plutôt qu'une réplique tirée de la graine.
Suite complète unique : 1 789 tests, 4 sauts ; reprise finale de 26 fichiers, 294 tests, verte.
**Bilan consolidé : 1 790 tests, 4 sauts, aucun échec ni erreur** (`bilan-tests.json`).

**Banc rapide.** `tools/comparer_bancs.py --reference 5b174ad --heures 4 --scenarios relais mine auberge crue
--processus 3` ; graines 1985, 7, 42, 2024, référence en cache réutilisée après corrections.

| Moyenne par nuit | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Constats confiés (nouvelle mesure) | 3,5 | 22,25 | 12,5 | 7 |
| Sans recours, référence → branche (min) | 0 → 0 | 6,25 → 6,25 | 20 → 17,5 | 60 → 60 |
| Avertissements redits, référence → branche | 0 → 0 | 0 → 2,25 | 0 → 0,25 | 0,75 → 0,5 |

Aucun plantage, violation ni usurpation. Bascules 0 dans les trois premiers scénarios, crue 0,25 → 0,5,
maximum 1 : aucune alternance répétée. **Réserve : mine 2024, cinq avertissements redits**, sur le guet
d'Odon (dont un ancien épisode retransmis) et deux lampes distinctes homonymes. Les parts de soupe
homonymes produisent aussi un faux doublon textuel. Le critère « aucune répétition nouvelle » n'est
pas entièrement acquis ; les rumeurs d'intention préexistantes restent à corriger. Temps en cache non comparables.

**Limites.** Récent = 30 minutes ; dates à la minute, constat propre prioritaire à égalité. Chaque
hauteur d'eau différente peut être une nouvelle ; sa seule nouvelle date ne suffit pas. Le jet commun
permet de douter. Besoins sans recours, avis/disputes, déplacement pour bavarder et désignation des
objets homonymes restent hors lot ; aucun renforcement sémantique général du MJ.

Bruts : `artifacts/codex-55/` (`banc.json`, `suite.json`, `validation.json`, reprises et traces).
