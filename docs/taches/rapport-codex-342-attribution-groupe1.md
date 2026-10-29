# Lot 342 — attribution du groupe 1, calcul en cours

30 octobre 2026. Branche `codex-attribution-groupe1`, base `16b18a7`.
Ce document est un point de reprise ; le lot n'est pas terminé et aucun
correctif n'est encore livré.

La suite `6f490ba` signale 33 incidents : 13 échecs, 20 erreurs. Les six
incidents `_retentir` sans `emission` sont réservés au lot 339. L'attribution
doit distinguer défaut, interaction, préexistence et attente périmée, avant
toute modification d'oracle.

**Preuve en cours.** Les méthodes en incident sont rejouées sur l'intégration
exacte de l'essai (`e37d9ee`), puis sur chacun des quatre lots seul ajouté à
cette intégration. Témoins détachés : référence `e37d9ee`, 313 `e5d5d9e`,
315 `1b6e2b3`, 332 `d42bb4e`, 333 `ac8bf5d`. Les conflits de `tient`
conservent les deux opérations ; le test des étapes chaînées réunit les
dictionnaires 313 et 334 comme dans l'essai original. Chaque variante utilise
ses tests natifs ; une méthode absente est signalée, jamais comptée comme
preuve verte. Les incidents du rejeu et de l'audit réservés au 339 ne sont
rejoués que sur la référence. Les traces gardent les sous-tests individuels.

Le lanceur démarre deux processus réduits au plus, sans suite complète,
banc ni Luna. Les bruts sont dans
`C:/Users/msics/donjon/artifacts/groupe1-342/reprise-1/`. La fin est écrite
en dernier : **`fin-attribution.json`**. `rejeux_produits=true` signifie que
les tests ont été chargés et les rejeux produits ; ce n'est pas une attestation
de tests verts. Une tentative initiale invalide par masquage de `tests`
est conservée hors de `reprise-1/` ; elle ne prouve rien sur le moteur.

Les deux premiers témoins réels de référence passent : décès d'Ilse et capture
de la bourse. La perception depuis le nouveau contact vocal du 313 atteint un
devis projeté sans position du joueur : piste à confirmer par comparaison,
sans ajouter de position réelle au modèle fermé.

**À la reprise.** Lire les résultats et constituer la matrice des 33 incidents.
Confirmer les changements d'empreintes par diff des données complètes, avec
monde et rendu après recharge. Corriger sur les branches responsables dans
des worktrees distincts, pousser, reconstruire `essai-groupe-1` depuis la
nouvelle `origin/integration`, puis tester les seuls fichiers concernés.
`jeu.py` reste hors du périmètre. Aucun résultat final ni gain général n'est
revendiqué à ce stade.
