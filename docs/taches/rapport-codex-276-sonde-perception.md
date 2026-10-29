# Lot 276 — entrées perceptives de la sonde 219

29 octobre 2026, laptop. **Branche `codex-sonde-perception`, non fusionnée**,
base `406a795`, code `5340a66`. Outils seulement ; aucun fichier de `donjon/`
modifié, aucune Luna ni suite complète. **Campagne terminée, aucun calcul actif.**

**Invariant et fonctions.** `relever_entrees` relève les entités effectivement
perçues et leur place par `percus`, sans réviser les croyances. L'analyse compare
aussi les sources des croyances sur les références structurelles du but et des
plans de départ/retour, offres imbriquées comprises ; une date rafraîchie seule
ne compte pas. `analyser_episodes` nomme les deltas dans `perception_diff_qr`.
Une différence perceptive seule, à lieu inchangé, devient
`renouvellement_perceptif`, à examiner ; une différence mêlée reste
`entree_nouvelle_a_expliquer`. Les preuves existantes, dont celles du 271,
gardent leur priorité. Le renouvellement rejoint `total_a_expliquer`, les
synthèses CLI et l'alerte de l'audit, jamais les justifiés.

**Preuves ciblées.** Aubin, Relais 2024, départ tiré, joueur passif
`chambre_cloche` : à **117518**, Ilse redevient perçue en `antichambre [5,1]`,
et `ilse.lieu` passe de `entendu` à `vu`, à valeur inchangée. Captures
117503/117518 identiques après recharge : monde, rendu, scène et relevés.
Les scènes Odile et lanterne déplacée vérifient le même contrat après
recharge ; date seule, source hors cible et retour sans changement restent
suspects. Les preuves du 271 gardent leur classe. **37 tests ciblés verts,
140,797 s**, contrôle AST du socle agendas inclus, méthodes existantes
conservées. Mireille historique, auberge 1985 **36720**, reste signalée à la
relecture de l'archive 219, dépourvue de relevés perceptifs.

**Identité nuit par nuit.** Les vingt paires de 4 h sont terminées : pour
**chacun** des scénarios Relais, mine, auberge, crue et crue_hameau, les quatre
graines **1985, 7, 42, 2024** passent toutes. **20/20 identités, 200 contrôles** :
monde complet, son SHA-256 recalculé et celui de la recharge, rendu, scène,
chronique, empreintes, mesures, récit et souvenirs. L'exécution initiale vérifie
également chaque recharge monde/rendu/scène. Relecture indépendante des vingt
archives brutes, sans simulation : `exploitation.json` détaille chaque nuit.
Un seul processus réduit, **2 183,929 s**, `fin.json` : `ok=true`, 20 nuits.

**Compteurs.** Les colonnes 276 analysent les **mêmes 616 retours** actuels avec
l'ancienne puis la nouvelle sonde ; le repère 271 est lu dans son bilan archivé.

| Classe | Lot 271 | 276 avant | 276 après |
|---|---:|---:|---:|
| Suspects | 1 | 1 | 0 |
| Entrées nouvelles à expliquer | 15 | 21 | 21 |
| Renouvellements perceptifs | 0 | 0 | 1 |
| **Total à examiner** | **15** | **21** | **22** |
| Entrées publiées utilisées | 26 | 28 | 28 |
| Cycles accomplis | 495 | 503 | 503 |
| Préemptions | 48 | 49 | 49 |
| Changements de moyen | 14 | 13 | 13 |
| Progressions | 1 | 1 | 1 |

**Un seul reclassement**, Aubin 117518 ; aucun retour ajouté ou retiré, aucune
hausse des justifiés. Dérives **203 → 203** (271 : 212) ; pertes d'état payé
**4 → 4** (271 : 4), trois cessations physiques et un bénéficiaire parti,
zéro violation de service. Les écarts intercampagnes figurent déjà dans
« 276 avant » ; leur cause n'est pas attribuée au lot. Aucune référence rejouée
ni comparaison des temps entre campagnes. Cette clôture n'a relancé aucun calcul.

**Limites.** Le défaut moteur de clôture à 117503 reste ouvert. Horizon 60 min,
preuves de fin et références structurelles bornent la sonde ; une archive sans
relevé perceptif garde son classement sans perception inventée. Aucune preuve
de nécessité causale ni identité exhaustive de toutes les entrées du choix.

Bruts : `C:/Users/msics/donjon/artifacts/perception-276/` : vingt archives
avec/sans sonde (états et épisodes inclus), sources, tests, `aubin.json`,
`mireille-historique.json`, `bilan.json`, `exploitation.json`, `fin.json`.
