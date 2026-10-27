# Lot 169 — Issue courante et rappels

27 octobre 2026. Branche `codex-silence-rappel`, non fusionnée ; base `27b5268`
(avance rapide depuis `integration`). Correction du contrat livrée ; validation
Luna bloquée, amélioration sémantique non certifiée.

**Cause et invariant.** Les six audits désignés par l'attribution 168 ont été
extraits avec leurs entrées, rapports et candidats entiers. Dans `echanges`
p1 t2 / p2 t1 et `noms-dialogue` p2 t2 (deux essais), le segment est déjà jugé
mécanique et établi par `conversation_validee`, puis `rappels` extrait l'écoute
et le silence courants et les compare aux anciennes paroles. Le champ refusant
est donc bien `rappels[].compatibilite`, ou l'absence du locuteur dans le dossier,
pas la perte de l'issue moteur. Dans `crypte` p2 t41 (deux essais), il s'agit
réellement de propos passés attribués à Gorm : dossier vide, refus maintenu par
le contrôleur même si l'extraction dit `etablie`. Ces deux cas ne sont pas des
silences. Le premier candidat `noms-dialogue` attribue aussi un silence à Brune,
alors que l'issue dit « te répond » : sa compatibilité mécanique reste contestable.
Il ne faut donc pas supprimer indistinctement les six refus.

**Changement.** `narration.SCHEMA_RAPPELS` et `INSTRUCTIONS_AUDIT` définissent
l'événement à extraire par son rapport temporel à l'issue courante. Les actes,
perceptions, réactions et absences de réaction de cette issue restent contrôlés
avec leurs sources actuelles, même racontés à un temps accompli. Les échanges
passés restent extraits et contrôlés, y compris dans une nouvelle réplique.
Aucun mot-clé, branche de scène, champ d'exemption ou contournement de
`controler`/`consigner`. Contrat MJ mis à jour ; fichiers réservés intacts.

**Vérification.** 17 tests ciblés verts (7,349 s) : console et MJ simulé,
témoin inconnu du banc `echanges`, témoins connus de `noms-dialogue`, absence
de réponse dans `soir-noir`, anciens tests de faux rappels et de citations.
État complet et rendu après recharge identiques ; le silence ne crée aucune
parole de témoin. Le faux rappel du nom et celui d'un refus après une part
servie restent rejetés avant affichage et sauvegarde. Un premier lancement
dans le bac a rencontré les permissions des temporaires ; un rapport simulé
incohérent a été corrigé avant la reprise verte.
Suite complète unique : **2 235 tests, 257 fichiers, 1 957,560 s, zéro erreur
et zéro ignoré**, deux échecs MiMo historiques `6 != 5` (`test_fournisseurs_jeu`,
`test_restes_fusions`). Les trois nouveaux tests passent dans leur version finale,
y compris un témoin ayant déjà parlé avant son silence courant. Aucune seconde
suite. Deux travailleurs réduits ; l'un suspendu pendant les calculs du lot voisin,
puis repris seul pour finir. Les auxiliaires implicitement créés par les tests
ont été déplacés et leurs écritures suivantes redirigées vers `auxiliaires-tests/`.

**Luna et limites.** Aucun appel réseau exécuté. La revue automatique a rejeté
les 60 appels de rejeu explicitement demandés (six audits × cinq répétitions ×
base/branche), interprétés comme dépassant deux exécutions et une passe ; risque
invoqué : envoi répété d'extraits privés. Conformément au brief, commande exacte
et passe des trois bancs laissées dans `luna-a-jouer.txt`, sans contournement.
Les trois références `cdaf371` p1 sont exclusivement relues et leurs SHA-256
archivés : appels/tour **3,33 / 3,25 / 4,60** (`echanges`, `noms-dialogue`,
`soir-noir`), replis **0/0/0**, relances **0/0/1**. Aucun gain de latence établi.
Le critère du lot 95 et l'amélioration des fils réels ne sont **pas mesurés**.
Les tests simulés prouvent le traitement d'une extraction correcte, pas sa
production par Luna ; reconnaissance et compatibilité restent sémantiques.
Pas de changement du moteur autonome, donc pas de banc de nuits ajouté.

Bruts exclusivement `C:/Users/msics/donjon/artifacts/silence-169/`.
Aucune clé de signature Git configurée : livraison non signée. `main` intacte.
