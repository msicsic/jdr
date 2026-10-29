# Lot 326 — G17, comptes parlés

Branche `codex-g17-comptes`, **terminée, non fusionnée**, base `integration eb15b5e`. Code/tests validés : `cbc5af3`, inchangés depuis cette validation.
Bruts : `C:/Users/msics/donjon/artifacts/g17-326/`.

**Invariant.** Les mots comptables viennent des rôles, termes, états et effets
typés, par opération. `comptes_parles.difference` conserve les paiements que
le journal cumule ; `formuler` et `comptes_narratifs.phrases` fixent les
personnes grammaticales sans lire une phrase de Luna. Règlement, solde,
livraison différée, absence et refus restent distincts. Les offres de mission,
leur négociation, acceptation et refus n'entraînent aucun paiement anticipé.

**Chaîne.** `paroles.preparer_parole` et `dialogues.preparer_conversation`
admettent les mots dans G15 sur la copie transactionnelle ; le rejeu les
inscrit sur le monde sauvegardé avant affichage. Le dossier grammatical est
partagé avec le MJ. `narration.consigner` vérifie les émissions réellement
enregistrées : mots exacts, ordre et multiplicité. Luna ne rédige ni ne fait
auditer les comptes ainsi fixés. Les autres opérations conservent leurs faits ;
un propos libre résiduel garde sa rédaction et ses contrôles. Le raccord
conserve les frontières des segments prouvés, avec un saut de ligne seulement
si l'espace les fusionnerait. Les commandes sociales directes affichent aussi
les mots enregistrés.

**Sans réseau.** **203 tests distincts / 18 fichiers verts**, zéro échec,
erreur ou saut dans les dernières validations par fichier (`tests-valides.json`,
sans cumul). Console réelle et MJ simulé : remboursements Gorm/Aubin, refus de
Brune, règlement partiel et manque d'argent, achat de planches et autre achat,
offres à vingt/trente pièces, négociation/acceptation/refus sans paiement.
Mots, bourses, dettes, possessions, livraisons, missions, fiche, conversation
et émissions contrôlés après recharge. Cumuls de deux créances et deux achats,
parole à plusieurs opérations, propos libre résiduel et archives G15 86/87
vérifiés. Essais intermédiaires en échec conservés dans les bruts ; aucun oracle
d'état affaibli. Ni suite complète ni banc PNJ ; deux travailleurs réduits au plus.

**Luna, une seule passe.** `comptes` et `soir-appel` sur `cbc5af3`, référence
historique `cdaf371` entièrement relue du cache, aucun appel de référence
relancé. Six tours MJ : **26 → 16 appels**, rédaction **5 → 2**, audits
narratifs **7 → 2**, révisions **2 → 0**, obstacles **3 → 0**, refus de
validation **1 → 0**. Zéro repli, erreur technique, mention sans fondement
ou erreur de recharge. Les quatre tours comptables n'ont chacun que
l'interprétation et la fidélité : **zéro rédaction, audit ou réécriture de
leurs comptes, zéro repli comptable**. Gorm et Aubin rendent chacun deux
pièces ; Brune refuse et reconnaît les deux pièces dues. La proposition de
trois pièces contre une part de planches est **refusée par le moteur** : termes
conservés, aucun paiement annoncé. L'achat réussi est vérifié sans réseau,
pas réalisé par cette passe Luna. Les deux dialogues de ressources gardent
leur rédaction et leur audit. Les secondes du cache viennent d'une autre
charge : aucun gain de vitesse ni bénéfice général revendiqué.

La passe détachée a fini en **80,974 s**, `fin-luna.json` : **ok=true, code 0**,
fichier écrit en dernier. Priorité réduite et processus actif contrôlés au
départ ; aucun calcul actif à la clôture. Rejeu sans réseau des **16 réponses
archivées** : instructions, contextes, **14 sorties et projections d'état**
identiques au fil live.
Les mondes du rejeu, fiche, comptes et mots sont identiques après recharge :
Gorm **50 → 48**, Corvus **24 → 26** ; dette de Brune conservée à deux ;
Aubin **5 → 3** au remboursement (il avait auparavant acheté du bois à Brune),
puis bourses inchangées lors du refus d'achat. Quatre émissions comptables
conservées. Bruts : `analyse-luna.json`, `rejeu-comptes.json`,
`rejeu-soir-appel.json` ; états complets du rejeu conservés, aucune affirmation
d'identité avec un état intégral live qui n'était pas archivé. Aucun modèle
relancé pour la clôture.

**Limites et intégration.** Garantie sur les répliques comptables typées de
ce contrat, pas sur toute la sémantique du français libre ; contrôles des voies
non portées conservés, décisions des PNJ inchangées. Recouvrement G19/327 :
`narration.consigner` et `raccorder_emissions`, sans modification des règles
de rappels. Rapport et état de développement clôturés ; branche poussée vers
origin, sans fusion.


**Reprise de la suite d'essai `bde5993` (en cours).** Le superviseur a relevé
45 incidents (25 échecs, 20 erreurs). `origin/integration 9f261f9` est fusionné
sans rebase par `aba1e4b` ; conflit documentaire seul, deux côtés conservés.
L'intégration a ensuite avancé à `ad0e5a8` (323 et 336), fusionnée sans
rebase par `b33d22a`, conflit documentaire seul. Fichiers communs cumulés :
`narration.py`, `mj.py`, `dialogues.py`. Le premier calcul de branche a été
arrêté avant cette fusion ; la référence était déjà terminée et reste acquise.
La compatibilité des offres stockées de 336 avec G17 est portée au contrat
commun des résolutions : mêmes termes, paiement journalisé et admission G15,
condition explicite de protection/échéance rendue par le moteur, sans inférence
à partir de mots. Aucun nouveau comportement de PNJ.
[La matrice individuelle](attribution-codex-326-g17-comptes-parles.md) suit
chaque incident. Un défaut G17 explique neuf incidents : une admission non
vocale peut ne pas avoir de rapport ; `comptes_parles.reponse` accepte cette
absence et laisse sa voie narrative habituelle, au lieu d'appeler G15 sur
`None`. Les anciennes attentes comptables et accès au deuxième appel sont
portés au texte moteur et à l'émission qui conserve les faits ; les oracles
mécaniques restent inchangés. La contre-épreuve du nom inconnu reste exercée
sur une réplique libre. Sept incidents du rejeu/audit/huile sont laissés au
lot 339, tous reproduits sur l'intégration seule `9f261f9` : **29 tests comptés,
deux échecs et cinq erreurs, 346,410 s**, aucun incident supplémentaire.
Référence : 30 méthodes distinctes, un travailleur réduit, détaché. Branche :
28 fichiers en incident ou directement concernés par les fichiers communs,
deux travailleurs réduits au plus, calcul détaché ; aucune
nouvelle suite complète. Bruts `C:/Users/msics/donjon/artifacts/g17-326/reprise/`.
Résultats et attribution finale encore à lire ; ne pas considérer la reprise
comme validée avant `reprise/ad0e5a8/fin-reprise.json` et sa lecture.
