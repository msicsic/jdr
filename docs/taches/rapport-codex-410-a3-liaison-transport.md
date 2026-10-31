# Lot 410 — A3, liaison du transport

31 octobre 2026 — branche `codex-a3-liaison-transport`, base `integration`
`57299df44e1ca7e7dcbdfa65b320f125c377dcad`, non fusionnée. Code final `962d81b2`.

**Verdict : transport validé sur les cinq bancs, sans relever la limite.** La
reprise remplace le verdict initial non validé (27/27 interruptions). Elle ne
garantit pas la fidélité sémantique de Luna ; une omission sonore est mesurée.

**Invariant et correction.** `contrat.lier_modes` relie neuf modes à leur charge
et les contrats A2 aux paramètres des opérations, y compris les suites après
faits et l'ancienne API simple. OpenAI et Local partagent l'enveloppe `reponse`
et le schéma mutualisé ; `schema.verifier` contrôle avant audit/préparation,
après disponibilité, avec `attendu`. Aucun choix selon saisie, lieu ou scénario.
La conjonction des contraintes communes avec l'union liée faisait échouer le
fournisseur avant tout jeton déclaré. `schema.union_seule` retire cette
conjonction seulement si `restreint` prouve que chaque branche la porte déjà.
Une contrainte non démontrée refuse la projection ; aucun élargissement des
charges ni des paramètres. Les contrôles moteur et les audits sont conservés.

**Diagnostic réel, même copie du Relais**, « je fredonne doucement » :

| Forme | Schéma, octets | Sortie / réflexion | Temps | Résultat |
|---|---:|---:|---:|---|
| Base `origin/integration` | 56 424 | 139 / 0 | 8,502 s | complet |
| Branche avant correction | 62 963 | 0 / 0 | 5,838 s | `max_output_tokens`, aucun delta |
| Même requête, union seule | 60 623 | 154 / 0 | 8,251 s | complet |

Les deux formes de branche gardent les mêmes 69 définitions : leur nombre seul
n'explique pas l'échec. Aucun plafond chiffré envoyé/reçu pour ces appels
ChatGPT, aucune limite relevée. L'expérience isole la forme du schéma, sans
prétendre connaître le fonctionnement interne du fournisseur. Le schéma final,
projeté avant mutualisation, fait **58 775 octets, 27 définitions, profondeur 8,
424 propriétés, 449 valeurs d'enum et 5 789 caractères comptés** : prévol conforme.

**Preuves et tests.** Croisements de modes, paramètres voisins, suites,
projection refusée si une contrainte serait perdue, distinction booléen/nombre,
parité cloud/local et équivalence des langages acceptés. Vraie boucle
console/PontWeb et adaptateurs réseau simulés : poutre/table, deux sons,
sauvegarde avant affichage, état complet et vues après reprise ; laps découpés
dans les voisins A2. **39 tests verts, 3 ignorés, 104,61 s**, six fichiers ;
auparavant 146 tests (4 ignorés) et reprise 15/15. Une fixture `observer` est
complétée sans changer ses assertions de sécurité. Deux travailleurs à priorité
réduite, aucune suite complète. **Empreintes Relais/auberge identiques** à la
base : chronique, mesures et monde complet, 2 h × 1985/7/42/2024, huit nuits par
version, référence puis branche ; référence absente calculée une fois et cachée.
Pas de nouveau calcul PNJ pour la projection, sans modification du moteur.

**Nouvelle passe Luna autorisée, cinq bancs sur copies.** **66 appels / 27 tours
MJ = 2,44 appels et 10,04 s par tour**, médiane 9,08 s ; **zéro interruption,
erreur technique, erreur de recharge, refus de forme ou repli**. Sortie maximale
**238 jetons**, réflexion déclarée nulle. Le coût mesuré dépasse le repère fourni
de 2,3 appels/8,5 s de 6 %/18 % : ordre de coût comparable, mais corpus
et charge non appariés, aucune non-régression de latence prouvée. Sifflement,
passage dessous et ressource bois suivent leurs contrats ; le fredonnement au
Relais devient encore une expression sans effet son, explicitement affichée
dans « Compris ». Validité de forme et fidélité de saisie restent distinctes.

**Livraison et limites.** Bruts : `C:/Users/msics/donjon/artifacts/a3-liaison-transport-410/` ;
reprise dans `reprise-sortie/` (`diagnostic.json`, `tests-finaux.json`, `mesures-luna.json`,
`commande-luna.json`, `conclusion.json`). L'erreur d'agrégation du lanceur après
les cinq parties est corrigée par relecture seule ; original conservé dans
`fin-lanceur.json`. Aucun appel supplémentaire. Contrats transitoires conservés,
aucune mécanique ni registre d'esprit ajouté, A4/A6 hors lot ; serveur local réel
non éprouvé. Le prochain lot de fidélité doit traiter l'omission sonore.
