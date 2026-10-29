# Lot 280 — prêt échu et secours prioritaire

Branche `codex-pret-reclame`, **non fusionnée**, base `427fb36` (266 et 275
réunis). **Le moteur respecte l'invariant : la créance attend un secours de
palier supérieur, puis reprend dès que ce secours cesse.** Aucun fichier de
`donjon/` modifié ; aucun raccord avec les fonctions des lots 277 et 278.

**Cause établie avant modification des tests.** Scène exacte de
`PretReclameTests.lampe_pretee_au_joueur`, mine 1985, départ fixe, prêt daté
de −240 minutes. Le plan `reclamer joueur / demander lampe_gaspard` existe
dès le départ. Gaspard choisit toutefois :

| Instant (dixièmes de seconde) | Choix effectif | Palier |
|---|---|---|
| 0 | Nourrir Rémy, faim observée ; chercher Bram pour les biscuits | SECOURS, 12 |
| 62 | Appeler Bram, nouveau moyen commun du lot 275 | Moyen du secours |
| 162 | Attendre Bram après sa réponse | ATTENDRE_APPELANT, 8 |
| 203 | Rester près de Lucien | SECOURS, 12 |

Lucien tremble ; Gaspard voit ce signe, lit sa peur et conserve une croyance
`detresse=True`, source `vu`, preuve `expression/tremble`. Le souci social
est admissible (poids 20). La créance, au palier ARGENT 14, doit attendre.
Sur cette base, l'absence de réclamation à deux minutes est reproduite ;
Gaspard reste alors au baraquement près de Lucien. Le départ avec Odon
mentionné dans le signalement n'est pas reproduit par ce rejeu.

**Contre-épreuves sur copies.** Retirer seulement les naissances de secours
peur permet la réclamation à `203`. Retirer seulement `_appeler` permet la
réclamation à `244`, avant le secours de proximité dans cette autre
trajectoire. Ces sondes isolent les deux mécanismes, sans prétendre rejouer
intégralement les anciens lots. Sans souci spontané de Gaspard, la demande
a lieu à `0`. Sur la scène intacte après deux minutes, apaiser Rémy, Odon et
Lucien par placement d'auteur, puis laisser Gaspard le percevoir, suffit :
réclamation à la **minute 2**, permission et possession du joueur conservées.
Le diagnostic instrumenté et son rejeu sans consultation préalable du plan
de créance produisent exactement le même monde.

**Changement de test seulement.** Dans `tests/test_echanges_suite.py`, le test
de réclamation immédiate place explicitement Gaspard sans souci spontané
(`sans_souci`, déjà utilisé par le test de restitution). Les **89 assertions
préexistantes du fichier sont conservées**, comparaison AST. Le helper
`lampe_pretee_au_joueur` conserve la scène initiale ; `recharge_visible`
contrôle monde entier, rendu et scène perçue, sans mutation. Deux nouveaux
tests prouvent le report réel jusqu'au calme perçu et le même contrat avec
Gorm prêtant un marteau au Relais : demande, possession, reproche à l'échéance
et perte de confiance, toujours après recharge.

**Validation terminée sur `be99757`.** Les cinq tests de `PretReclameTests`
étaient verts en **50,545 s**. La vérification détachée des fichiers touchés
par les commits propres des lots 266/275 et de `test_echanges_suite` est
terminée : **211 tests verts / 14 fichiers entiers, 1 613,326 s**, zéro échec,
erreur ou ignoré ; dont les **23 tests** de `test_echanges_suite` en 78,122 s.
Un seul travailleur à priorité réduite ; `fin-verification.json` **code 0**,
résultats détaillés dans `tests.json`. `git diff --check` est propre. Aucun
nouveau calcul à la clôture ; ni Luna, ni suite complète, ni banc dans ce
lot : aucun comportement du moteur n'a changé. La suite complète sur fusion
d'essai revient au superviseur. La preuve porte sur ces scènes, pas sur
l'absence universelle de report des créances.

Bruts : `C:/Users/msics/donjon/artifacts/pret-280/` : captures avant/après,
`diagnostic.json`, `contre-epreuves.json`, `assertions.json`, sélection des
tests, scripts et résultats de vérification.
