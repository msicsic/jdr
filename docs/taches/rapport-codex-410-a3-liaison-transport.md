# Lot 410 — A3, liaison du transport

31 octobre 2026 — branche `codex-a3-liaison-transport`, base `integration`
`57299df44e1ca7e7dcbdfa65b320f125c377dcad`, non fusionnée.

**Invariant et changement.** `fournisseurs.contrat.lier_modes` relie chacun
des neuf modes à sa charge, au texte vide ou au dialogue sans proposition.
Les charges réemploient les schémas canoniques A2 : attente/séquence,
expression/son, passage et consultation sociale, y compris la suite après
admission de faits. L'ancienne API `proposer_action` expose aussi les contrats
d'attente et de passage. Aucun choix de grammaire selon la saisie ou la scène.

**Transport et admission.** OpenAI interdit `anyOf` à la racine : une enveloppe
`reponse` commune à OpenAI et Local porte l'union, mutualisée sans perte de
contrainte ; les adaptateurs la défont avant le MJ. Instructions de transport,
entrée et schéma sont identiques. Une ancienne réponse à plat reste soumise
à la même validation. La validation commune du sous-ensemble de JSON Schema
employé par ces contrats précède les audits et préparateurs, après le contrôle
de disponibilité. Le refus conserve chemin, reçu et accepté dans `attendu` et
reprend la boucle de correction bornée existante. Les champs voisins interdits
sont diagnostiqués avant le contenu libre manquant. Un mot-clé de schéma non
pris en charge provoque une erreur explicite, jamais un contrôle ignoré.

**Preuves ciblées.** Croisements des charges entre les neuf modes ; mutations
des paramètres des quatre familles, dans la proposition et dans la suite ;
parité exacte des requêtes cloud/local et équivalence après développement des
références ; précontrôle des limites du fournisseur. Vrais adaptateurs réseau
simulés, MJ, revue, console/PontWeb : poutre du Relais et table de l'auberge,
fredonnement et rythme corporel, état complet et réponse sauvés avant affichage,
« Compris » et vues relus après reprise. Paramètre voisin refusé puis correction
sur deux scènes : même monde sauvegardé et même rendu que le témoin valide.
Les tests A2 voisins couvrent aussi le laps en bloc/découpé avec recharges.
Une seule fixture ancienne est complétée par `proposition('observer')` :
l'ancien objet réduit à `action` était volontairement hors du schéma ; les
assertions de disponibilité, relance et identité du schéma restent inchangées.

**Mesures.** Première passe ciblée : **146 tests, zéro échec, zéro erreur,
quatre ignorés**, treize fichiers, **328,12 s**, deux travailleurs à priorité
réduite ; pas de suite complète (`tests-cibles.json`). La reprise finale des deux fichiers
A3/schéma, les empreintes Relais/auberge (2 h × quatre graines, référence exacte
ci-dessus réemployée depuis le cache) et une passe Luna des cinq bancs demandés
sont consignées dans les bruts. Le résultat définitif et les dimensions finales
seront inscrits après lecture du fichier de fin ; aucun succès de calcul encore
inachevé n'est revendiqué. Le lanceur détaché vit, à priorité réduite, et écrit
`fin.json` en dernier ; ses commandes exactes restent dans `commandes.json`. Bruts :
`C:/Users/msics/donjon/artifacts/a3-liaison-transport-410/`.

**Limites.** La grammaire garantit la forme et la liaison des charges des
contrats portés, pas le choix sémantique de Luna ni la faisabilité dans le monde.
Les opérations transitoires conservent leurs schémas et contrôles mécaniques ;
ce lot n'est pas un portage général de leurs paramètres. Aucun audit retiré,
aucune nouvelle mécanique ni registre d'esprit, A4/A6 hors lot. Le serveur local
est éprouvé par ses vraies requêtes et réponses simulées ; aucune disponibilité
d'un serveur local réel n'est revendiquée. La fidélité Luna reste à mesurer.

Limites de schéma vérifiées selon la [documentation OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs).
