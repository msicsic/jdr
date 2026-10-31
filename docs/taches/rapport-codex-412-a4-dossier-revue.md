# Lot 412 — A4, dossier de revue

31 octobre 2026 — `codex-a4-dossier-revue`, base `integration`
`2634e48e7ba39533bcb9e876487bac7536ee57af`, non fusionnée.

**Verdict final : non validé pour fusion.** Le dossier est raccordé et les
omissions sonores sont détectées. La régression de fidélité apparue avec A4
reste ouverte après le correctif `6bad59cb` ; elle ne peut pas être renvoyée
à A5 comme simple défaut préexistant. Aucun audit retiré.

**Invariant et fonctions.** `comprehension.sens_propose` joint opération,
paramètres, manière et récits transitoires proposés aux contrats communs de
séquence/attente, expression/son et passage. `couverture_action.entree` les
associe aux étapes développées, effets des trois branches et conditions
calculées ; `MJ._auditer_action` fige le dossier. Les autres opérations gardent
paramètres et titre moteur, la parole son contrat distinct. Le correctif
ajoute méthode/outil canoniques à la manière et partage `_precisions` avec
« Compris ». La revue distingue forme concrète et nuance cosmétique, sans
exiger de nouveau paramètre pour cette dernière. Textes proposés et admission
ne prouvent pas la fidélité. Mécaniques et registres d’esprit inchangés.

**Tests.** Sept nouveaux tests couvrent pureté, paramètres canoniques,
précisions identiques au rendu, branches, son présent et omission dans
`attendu`. La vraie boucle console/PontWeb corrige le fredonnement du Relais
et un rythme corporel : un son, aucun jet, sauvegarde avant affichage,
réponse relue après reprise ; deux minutes en bloc ou huit tranches avec
recharges donnent le même monde complet et les mêmes vues. Verdicts simulés.
Passe initiale : 171 tests, un ignoré ; seul ancien texte attendu adapté,
fichier rejoué 18/18. Ses égalités exactes restent conservées. Après correctif,
**44 tests concernés, un ignoré, aucun échec ni erreur, 261,70 s**.

**Luna et comparaison demandée.** Première passe sur quatre scripts :
62 appels/26 tours MJ, **2,38 appels et 9,19 s/tour**, quatre contre-épreuves
sonores justes ; rythme réellement omis puis corrigé. Dans atelier, la revue
refuse cependant le sifflement pour sa manière absente, puis accepte des
notes de voix. Sur `origin/integration` figé en **40f062d8**, sans A4, même
script et mêmes fichiers de revue que la base initiale : **0/3 substitutions
acceptées**. Deux parties acceptent le sifflement ; la troisième refuse voix
mélodique puis souffle. Ce résultat déclenche la correction du contrat commun,
plutôt qu’un classement en limite A5.

**Correctif insuffisant.** Sept revues directes : **six booléens sur sept
attendus** ; les quatre cas sonores restent justes, le sifflement canonique
passe, mais le cri « de colère » est refusé pour sa nuance absente.
Dans le nouvel atelier, le faux refus du sifflement puis l’acceptation de
`voix_melodique` se reproduisent malgré les précisions moteur jointes.
Atelier : **22 appels/11 tours, 2 appels et 6,90 s/tour**, aucune erreur,
interruption, erreur de recharge ni repli. Ces corpus ne prouvent aucun gain
de latence. La présence déterministe du sens dans le dossier est garantie ;
son exploitation correcte par la revue sémantique ne l’est pas. Aucun succès
global de fidélité revendiqué, aucun traitement propre à ces formulations.

Empreintes finales **identiques**, chronique/mesures/monde complet :
Relais/auberge, 2 h × 1985/7/42/2024, référence réutilisée, branche seule
rejouée. Bruts `C:/Users/msics/donjon/artifacts/a4-dossier-revue-412/` :
`comparaison-base/fin.json`, `correction/fin.json`, `correction/revues.json`
et `correction/atelier.json`. Vérifications supplémentaires explicitement
demandées par le superviseur ; deux travailleurs au plus, priorité réduite,
aucune suite complète. Les refus de préparation et le repli historique après
deux revues illisibles restent sur leurs voies actuelles.
