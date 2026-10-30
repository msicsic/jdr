# Lot 358 — revalider une action différée après refus

Branche `codex-revalider-apres-refus`, base **`integration a3855ad9`**.
**Lot terminé, non fusionné. Code vérifié : `52d2f5b6`.**

**Invariant.** Une réponse refusée encore valable s'applique au prochain geste
d'un plan conservé comme à celui d'un nouveau plan. `pnj.refus_etape`, déjà appelé
au choix et par `agir`, consulte désormais `deliberation.refus_geste`. Cette
fonction traduit les opérations typées en demandes (bien, enquête, tâche,
mandat, feu, marché) et réutilise les juges existants des refus/offres. Aucun
nouvel essai, parole, jet ou perception au contrôle. Ni scénario ni prompt
modifié. Les règles de levée restent intactes : moyens/croyances, mandat
distinct, hausse de prix et meilleure contrepartie ; le délai seul ne lève
pas une impossibilité. Un préparatif d'observation reste possible avant le
suffixe social ; le suffixe est contrôlé lorsqu'il devient le prochain geste.

**Preuves.** Capture 306 originale à **t=4200**, plan de Gorm datant de minute 4,
refus de Maël minute 6 : refus d'admission et `MANQUE` avant toute réexécution,
sans modification de l'état, sans parole ni geste. Fixture compressée sans
retouche (`tests/data/refus-358-hameau-1985-4200.json.gz`), SHA-256 du JSON brut
`1529ca9f54e17c0c16de2d2d98e85a04b0bd7d3cdcc66065229885f4630c004a`.
Autre scène : tâche payée impossible de Mireille à Mathurine à l'auberge,
préparée avant sa réponse, conservée au-delà de `REDEMANDE`. Les tests contrôlent
monde complet, rendu, scène et écoute après recharge, reprise en bloc ou par
demi-minutes, plus les nouveaux moyens et les termes distincts.

**81/81 tests distincts verts, onze fichiers**, sans erreur ni saut : 73 voisins
(refus retenus, mandats/jugement, recours d'agenda, tâches payées, protéger,
engagement et propositions), puis huit régressions finales du lot, **22,626 s**.
Le premier passage de 79 tests (**886,013 s**) avait un seul échec de harnais :
l'attente d'un refus inchangé pendant deux minutes malgré un apprentissage
nouveau. La reprise contrôle chaque réexécution contre le refus alors valable ;
à 4200, aucun nouvel essai. Aucun oracle voisin affaibli. Précontrôles et
premier passage rouge conservés ; les huit tests finaux les remplacent.

**Banc achevé : douze paires de nuits, 4 h, graines 1985/7/42/2024.**
Référence `main 0bad227` → branche `52d2f5b6` : zéro plantage/usurpation,
retours non justifiés **0 → 0 dans chaque nuit**.

| Scénario | À expliquer | Dérives ouvertes | Maximum de passages/h |
|---|---:|---:|---:|
| Relais | 3 → 1 | 27 → 32 | 9 → 11 |
| Mine | 5 → 8 | 50 → 57 | 11 → 14 |
| Crue | 7 → 8 | 37 → 78 | 27 → 43 |

Les douze références exactes manquaient au cache : calculées une fois puis
rangées, avant la branche. Deux travailleurs réduits au plus ; enchaînement
détaché **696,666 s**, `fin.json ok=true`, codes régressions/banc **0/0**.
Les écarts avec `main`, antérieur aux autres lots de la base d'intégration,
ne prouvent pas une causalité du 358 ni une absence générale de boucles.
Restent notamment les répétitions de Mathe près de Lucien (mine 1985), les
appels d'Aubin à Brune (crue 42) et la dette de tâche finale (crue 2024).
Aucune conclusion de performance ; aucun calcul encore actif.

**Intégration.** Recouvrement **335 : `donjon/pnj.py`**, limité ici à
`refus_etape` ; `agir`, `planification.py`, `trajet_estime.py` et `agendas.py`
inchangés. Ni Luna ni suite complète. Bruts et `conclusion.json` dans
`C:/Users/msics/donjon/artifacts/revalider-358/` ; précontrôles aussi dans le
worktree. Code/tests inchangés depuis validation ; clôture documentaire seule.
