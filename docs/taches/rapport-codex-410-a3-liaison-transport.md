# Lot 410 — A3, liaison du transport

31 octobre 2026 — `codex-a3-liaison-transport`, base `integration`
`57299df44e1ca7e7dcbdfa65b320f125c377dcad`, non fusionnée.

**Reprise en cours, ne pas fusionner avant la nouvelle passe ciblée.** Même copie
du Relais, « je fredonne doucement » : base `origin/integration` **139 jetons,
0 réflexion, 8,502 s**, schéma 56 424 octets ; branche défaillante **0 jeton
déclaré, 0 réflexion, aucun delta, 5,838 s**, 62 963 octets. Retirer uniquement
la conjonction redondante propriétés/union donne une réponse complète de
**154 jetons, 0 réflexion, 8,251 s**, 60 623 octets, avec les mêmes 69 définitions.
Aucun `max_output_tokens` envoyé dans les trois cas, terminal reçu sans limite
chiffrée : aucune limite relevée. L'expérience isole la forme du schéma ; elle
ne révèle pas le fonctionnement interne du décodeur fournisseur. La correction
`union_seule` exige une preuve structurelle `restreint` pour chaque branche avant
de retirer les contraintes déjà présentes. Une contrainte non démontrée fait
refuser la projection ; les liaisons mode/charge et opération/paramètres restent
inchangées. Diagnostics et événements sans en-têtes opaques : `reprise-sortie/`.
Reprise ciblée : **39 tests verts, trois ignorés, 104,61 s**, six fichiers,
deux travailleurs à priorité réduite. Nouvelle passe des cinq bancs lancée
séparément ; fichier de fin `reprise-sortie/fin.json`, résultats à lire avant validation.

**Première livraison : NON VALIDÉE côté ChatGPT.** Tests et
empreintes passent ; les 27 appels de l'unique passe Luna échouent avant une
réponse complète. Le transport réel et la fidélité sémantique ne sont pas validés.

**Invariant et fonctions.** `fournisseurs.contrat.lier_modes` relie les neuf
modes à leur charge et au texte vide ou au dialogue sans proposition. Les
charges réemploient les contrats A2 attente/séquence, expression/son, passage
et consultation sociale, y compris la suite après faits. `proposer_action`
reprend aussi attente/passage. Aucune sélection selon saisie, lieu ou scénario.
OpenAI et Local partagent schéma mutualisé, instructions et enveloppe `reponse`
(OpenAI interdit `anyOf` à la racine), décodée avant le MJ. Une réponse ancienne
à plat subit le même contrôle. `fournisseurs.schema.verifier` contrôle la
grammaire avant audit/préparation, après disponibilité, avec chemin/reçu/accepté
dans `attendu` et correction bornée existante. Un mot-clé inconnu n'est pas ignoré.

**Preuves.** Croisements des charges entre modes, paramètres voisins des quatre
familles et des suites, parité des requêtes réellement émises cloud/local,
équivalence des références développées. Vrais adaptateurs réseau simulés, MJ,
revue et console/PontWeb : poutre du Relais/table de l'auberge, fredonnement/rythme
corporel, sauvegarde avant affichage, « Compris », état complet et vues après
reprise. Refus puis correction sur deux scènes : état/rendu identiques au témoin.
Les voisins A2 contrôlent aussi les laps en bloc/découpés avec recharges.
Une fixture devient `proposition('observer')` au lieu du seul champ `action`,
incomplet selon le schéma : toutes ses assertions de sécurité restent intactes.

**Mesures hors modèle.** Treize fichiers : **146 tests, zéro échec/erreur,
4 ignorés, 328,12 s** ; reprise finale A3/schéma : **15/15, 105,51 s**, aucun
ignoré. Deux travailleurs à priorité réduite ; aucune suite complète. Prévol :
**446 propriétés, 473 valeurs d'enum, 6 551 caractères comptés, profondeur 9**,
62 963 octets mutualisés, dans les [limites publiées OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs).
**Empreintes identiques** : chronique, mesures et état complet, Relais/auberge,
2 h × 1985/7/42/2024, huit nuits par version ; base `57299df4` puis `844ab4fa`,
`PYTHONHASHSEED=0`. Référence absente calculée une fois puis cachée, branche non
cachée. L'avis Relais 2024 « à expliquer » existe des deux côtés ; aucun gain
de vitesse revendiqué.

**Luna, une passe sur copies.** Appels interrompus : Relais **8/8**, atelier
**11/11**, échanges **3/3**, noms-dialogue **4/4**, sous-obstacle-relais **1/1**.
Total : **27 erreurs `incomplète : max_output_tokens`, 27 replis, 131,6 s**,
aucun audit atteint ni erreur de recharge. Aucun résultat exploitable, brut ou
usage dans les traces ; cause non isolée. Les codes de sortie 0 de `fin-reprise.json`
attestent seulement la fin des commandes. Pas de seconde passe. Le premier
lanceur avait échoué après les tests sur la collision `tools/tests.py`/dossier
`tests` (`fin.json`) ; corrigé sans changement du jeu ni nouvelle passe de tests,
il a repris les seuls calculs manquants. Bruts et commandes exactes :
`C:/Users/msics/donjon/artifacts/a3-liaison-transport-410/`, notamment
`tests-cibles.json`, `tests-finaux.json`, `empreintes.json`, `luna/`,
`commandes-reprise.json` et **`conclusion.json`** (verdict interprété).

**Limites.** La liaison des contrats portés est démontrée hors ligne, pas sur
ChatGPT ; l'invariant cloud reste non garanti. Les opérations transitoires et
leurs contrôles restent en place. Aucun audit retiré, aucune mécanique ni
registre d'esprit ajouté ; A4/A6 hors lot. Aucun serveur local réel éprouvé.
