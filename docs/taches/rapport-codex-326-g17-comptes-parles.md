# Lot 326 — G17, comptes parlés et reprise de la suite

Branche `codex-g17-comptes`, **terminée, non fusionnée**. Base initiale
`eb15b5e` ; intégrations `9f261f9`, `ad0e5a8` et **`64130fa` (G6)** fusionnées
sans rebase (`aba1e4b`, `b33d22a`, `f324cbe`), conflits documentaires seuls,
deux côtés conservés. Correctif final validé : **`700764d`**.

**Invariant.** Les répliques comptables sont formulées depuis les rôles,
termes, règlements et effets typés, par opération ; aucun mot de Luna ne
fixe leur montant ni leur sens. `comptes_parles` et `comptes_narratifs`
conservent paiements cumulés, dettes, livraisons, refus et offres. Admission
dans G15 sur copie, rejeu transactionnel avant sauvegarde et affichage ;
`narration.consigner` contrôle mots exacts, ordre et multiplicité. Le raccord
conserve les frontières prouvées des segments. Les autres opérations et
les propos libres résiduels gardent leurs faits et contrôles. Après fusion
336, offres stockées et missions passent par cette admission commune avec
leurs termes et paiements ; protection et échéance sont des mécaniques
explicites, pas des inférences à partir du récit.

**Suite du superviseur `bde5993` : 45 incidents (25 échecs, 20 erreurs).**
La [matrice individuelle](attribution-codex-326-g17-comptes-parles.md) conserve
chaque sous-cas et sa preuve.

| Incidents | Attribution et traitement |
|---:|---|
| 9 | Défaut G17 : une admission non vocale peut ne pas avoir de rapport. Lecture **et scellement** acceptent cette absence sans changer sa voie narrative. Le premier correctif était incomplet : six incidents subsistaient au scellement ; tous sont corrigés, les assertions d’état, sauvegarde et panne sont conservées. |
| 29 | Attentes périmées par le portage autorisé : les mots comptables ne sont plus ceux de Luna et leur deuxième appel disparaît. Lecture des faits depuis l’émission G15, attentes moteur explicites ; autres oracles mécaniques conservés. Le nom de Corvus reste contrôlé sur une réplique libre. |
| 7 | Préexistants tous reproduits sur l’intégration isolée `9f261f9` : cinq erreurs de rejeu et un audit en échec (`_retentir` sans `emission`), plus refus de vente d’huile après 8 h. Oracles intacts, laissés au lot 339. |

**Validation.** Référence unique : **29 tests comptés, deux échecs/cinq
erreurs, 346,410 s**, aucun incident supplémentaire. Branche : premier lot
**358 tests / 28 fichiers, 605,872 s**, conservé ; après fusion G6 et correctif
final, **156/156 tests verts / 12 fichiers, 185,283 s**. Consolidation sans
cumul des reprises : **403 tests / 32 fichiers, deux échecs et cinq erreurs**,
uniquement les sept préexistants (une classe de rejeu reste bloquée).
Aucun nouvel incident. Mots, soldes, possessions, missions, voix et rendu
rechargés contrôlés ; archives G15/G19 et nouveaux contrats stockés couverts.
Deux travailleurs réduits au plus ; calcul long détaché. Pas de suite complète,
Luna ou banc PNJ relancé pour la reprise. Tests non concernés réutilisés.

**Luna initiale archivée, avant intégration**, sur `cbc5af3` : une passe
`comptes`/`soir-appel`, référence `cdaf371` en cache, six tours MJ,
**26 → 16 appels**, quatre tours comptables sans rédaction, audit ou
réécriture de leurs comptes ; zéro repli ni erreur technique/recharge.
Gorm/Aubin rendent deux pièces, Brune garde sa dette ; achat de planche
refusé sans paiement, achat réussi couvert sans réseau. Rejeu des 16 réponses
archivées : 14 sorties et projections identiques, mondes et rendus du rejeu
identiques après recharge. Aucun gain général ni de vitesse revendiqué.

**Livraison et limites.** Garantie sur les répliques comptables typées,
pas sur toute la sémantique libre ; contrôles des voies non portées conservés,
décisions des PNJ inchangées. La suite entière n’est pas déclarée verte.
Recouvrements intégrés : G19/U-P/G5/G6 (`narration.py`), G5 (`mj.py`),
336 (`dialogues.py`). Bruts `C:/Users/msics/donjon/artifacts/g17-326/`, reprise
et preuves finales sous `reprise/64130fa/`. Rapport, matrice et état de
développement clôturés ; branche poussée vers origin, aucun calcul actif.
