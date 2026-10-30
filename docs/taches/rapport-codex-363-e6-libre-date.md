# Lot 363 — E6, compilation libre d'un accord daté

Branche `codex-e6-libre-date`, base `integration a9f02e5c`, PC fixe.
**Calcul ciblé en cours ; livraison non validée, non fusionnée.**

**Contrat porté.** La compilation d'une proposition accepte un délai relatif
structuré `limite: {dans_secondes: n}`. `propositions.compiler_limites` le résout
sur copie à l'instant de la saisie, avant la préparation et la revue de parole.
La transaction ne conserve que la limite absolue E4 ; U-C, l'exécution et la
sauvegarde refusent toujours une limite relative. L'attente et la confirmation
ne recalculent pas la date. Le schéma d'exécution et les effets moteur restent
inchangés ; aucun banc autonome n'est nécessaire pour ce raccord du MJ.

Le dossier commun de fidélité donne les termes exécutables rendus par le moteur,
avec les repères temporels, la durée restante et le paiement présent lorsqu'il
y a des pièces. Les noms passent par la projection publique. Les consignes
communes exposent le périmètre E4, les clauses indivisibles et les voies existantes
`impossible`/`clarifier` pour les demandes non portées ou sans repère temporel.
L'aperçu « Compris » réemploie E4/E5 ; aucun changement à `comprehension.py`,
`consentement.py` ou `transactions.py` n'est nécessaire. Les contrôles de fidélité
restent en place. Recouvrements à surveiller avec 360/362 : `paroles.py`, `mj.py`,
`propositions.py` et `couverture_action.py`.

**Épreuves.** Cinq méthodes E6 couvrent huile d'Odile et verrou du garde-manger
par Joss : saisie → interprétation simulée → revue → aperçu → tenter/annuler →
effets → sauvegarde et recharge, avec contrôle des comptes, engagements,
paroles et rendu. La parité E5 compare les termes et effets mécaniques ainsi
que les réponses PNJ ; les mots imposés par le joueur restent ses propres mots.
La date est aussi éprouvée à un instant non entier puis après revalidation.
Les tests injectent une revue négative pour une clause omise ou déformée
(limite, paiement futur, maintien, alternative, prêt ou repère manquant) et
contrôlent l'absence d'exécution partielle après recharge. Cela prouve la
réaction à cette revue, pas son discernement sémantique en français réel.

Première passe : quatre méthodes sans erreur, onze erreurs de sous-cas dans
la méthode de refus (audit narratif manquant dans le harnais). Harnais corrigé,
sans modifier d'oracle moteur. Douze fichiers ciblés E1–E6/U-C/compréhension/G16
et contenus sont lancés avec deux travailleurs réduits ; un complément inclut
la reprise E6, paroles, contre-revue, contenu vide et G17/comptes moteur.
Résultats définitifs à lire avant de conclure ; aucune suite complète lancée.

**Luna.** Quatorze scripts sur copies indépendantes, une seule passe : pour
chaque prestation, acceptation, annulation, paiement futur, maintien, alternative,
prêt daté et « demain ». `tools/preparer_banc_e6.py` reproduit ces scripts et la
commande exacte `C:/Users/msics/donjon/artifacts/e6-363/luna-a-jouer.txt`.
Le gardien détaché attend la fin des tests puis lance le complément et Luna
séquentiellement, à priorité réduite, sans dépasser deux travailleurs de calcul.
Les bruts, empreintes des sources et résultats sont rangés dans ce même dossier ;
`fin-verification.json` est écrit en dernier. Il faut analyser les sorties Luna
et attribuer tout rouge avant de clore le lot.

**Limite explicite.** La résolution et la conservation du contenu typé sont
déterministes. L'exhaustivité de la traduction d'une phrase libre, notamment
le refus d'une clause non représentée par le modèle, reste sémantique : revue
existante et contrôle du joueur, sans garantie universelle nouvelle. Aucun
prêt daté, maintien continu, crédit, calendrier ni renégociation n'est ajouté.
