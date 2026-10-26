# Vérification d’intégration 057766f — lot 131

26 octobre 2026. **Analyse seule** des campagnes archivées : 32 nuits de 12 h,
huit rixes de 8 h, cinq nuits de 8 h `VERIFIER` + `spatial.VERIFICATION` 0,2.
Aucun rejeu, Luna, test complet, changement de code ni mesure CPU ; un processus
d’analyse à priorité réduite. **Aucun plantage, violation signalée, usurpation,
coup contre une personne ni décès observé** ; les coups relevés visent des objets.
Aucun écart des contrôles. Une alerte de borne historique : **Lucien, auberge 42,
314 min**, lumière, retenu = optimum **73,4743**, identique à `590653e`.

Moyennes par nuit, ordre **42bb9c0 → 590653e → 057766f** ; durées en
PNJ·minutes, passages = pire PNJ/heure des huit nuits. `—` = compteur absent,
pas zéro ; eau hors crue = sans objet. Valeurs arrondies à deux décimales.

| Mesure | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| Sans recours | 205,62→91,88→91,88 | 23,12→29,38→30 | 188,12→153,75→133,12 | 141,25→151,25→150,62 |
| Attente | 131,25→455→454,38 | 1400→1459,38→1431,88 | 461,88→481,88→493,12 | 499,38→551,25→582,50 |
| Noir | 198,75→231,88→233,75 | 1413,12→1394,38→1461,88 | 1014,38→981,88→951,88 | 64,38→110,62→92,50 |
| Eau | s.o. | s.o. | s.o. | 228,75→390,62→393,75 |
| Appels | 0,50→1,12→1,12 | 5,25→3,88→7,38 | 17,50→15,50→14,50 | 2,38→5,88→3,25 |
| Appels à l’aide | 2→0,38→0,38 | 2→2,12→3 | 1,25→2,88→2,38 | 0,75→2,25→1,88 |
| Bascules | 1,50→0,25→0,25 | 0,62→0,25→0,25 | 1,12→1→1,38 | 2→2,12→2 |
| Passages (pire) | 165→10→10 | 17→16→21 | 28→38→32 | 36→24→24 |
| Échanges | 28→27,88→27,88 | 87,88→125,75→120,88 | 77→146,75→140,50 | 28,75→68,75→69,50 |
| Propositions | —→1,25→1,62 | —→13,75→9 | —→7,88→5,38 | —→4,38→4 |
| Acceptées | —→0→0 | —→0,25→0,25 | —→1→0,88 | —→0,25→0,50 |
| Offres identiques < 60 min | 0→0→0 | 0→0→0 | 0→0→0 | 0→0→0 |
| Avis exprimés | —→0→0 | —→0→0 | —→0→0 | —→9→8,50 |
| Avis adoptés | —→0→0 | —→0→0 | —→0→0 | —→0,25→0,12 |
| Constats confiés | —→6,75→6,38 | —→33,62→33 | —→49,38→49,62 | —→22,88→21,38 |
| Avertissements redits | 1,75→0,12→0,12 | 4→2,38→1,88 | 0,38→2→1,38 | 0,75→1,12→0,88 |

**Nouveaux mécanismes, totaux sur huit nuits par scénario** (absents des versions
anciennes). Services `service_rendu` : Relais 0, mine **7**, auberge 0, crue 0.
Tâches promises en contrepartie, **offertes/acceptées/tenues/rompues** : Relais
**6/0/0/0**, mine **9/0/0/0**, auberge **0/0/0/0**, crue **3/1/0/1** ; comptage
des termes typés des propositions, distinct des tâches achetées contre des pièces.
Disputes/éclats : **0/0**, **0/0**, **0/0**, **2/0**, respectivement.
Services naturels : **Mathe → Lucien**, mine, graines/minutes **1985/36, 7/169,
2024/124, 3/9, 11/123, 99/121, 500/49** ; aucun en 42, aucune méfiance levée
par ces sept événements, pas de preuve de réparation délibérée. Disputes naturelles :
**Aubin contredit Brune à 544 puis Ilse à 557**, crue 99 ; Gorm révise sa prévision
à 557, trois prises de parti, aucun éclat. Les 12 h exercent donc les lots 115,
120 et 121, avec une réserve majeure pour 115 ci-dessous.

**Suivi historique.** Borne de Lucien persistante, sans perte d’optimum.
Contrepartie **mine 1985, Odon à 253** : correction maintenue, « 1 pièce prise
dans la bourse », jamais la bourse entière. **Crue 2024** : six avertissements
textuellement redits persistent, dont Brune → Gorm sur la torche à **146/242/444** ;
rallumages intermédiaires, pas six défauts établis. Les huit hauteurs d’eau dites
par Ilse à 217–686 restent distinctes. **Odile, auberge 7, 641–644** : anciens
appels non observés, parcours changé ; aucune preuve générale de correction.

**Défaut nouveau à isoler dans un petit lot : devis et engagement incompatibles.**
Crue **11**, **Ilse → Aubin à 210** : promesse de verrouiller la porte contre
le pied-de-biche acceptée à l’instant **126226**, puis abandon pour impossibilité
à **126336**, soit **11 s plus tard**, sans geste sur la porte entre les deux.
La porte avait été forcée par Aubin à **86**. Souvenirs : engagement pris,
proposition acceptée, engagement abandonné et abandon annoncé ; aucun engagement
restant à 720. Invariant à rétablir : **le devis autonome avant accord et le
contrôle d’exécutabilité de l’engagement doivent partager leurs préconditions** ;
une impossibilité préexistante ne doit pas devenir une promesse acceptée puis
aussitôt annulée. Fonctions à examiner : `echanges.promesse_autonome`,
`echanges.proposer`, `echanges.empeche`, `agendas.echoir`. Ce marché n’existe
pas dans la même nuit `590653e` ; ce défaut n’est pas une boucle. La cause précise
du désaccord de validation reste à reproduire dans le lot correctif.

**Alertes, sans nouveau défaut de boucle établi.** Odon, mine 2024 : **15 appels
à Gaspard de 571 à 696**, aucun dans cette nuit `590653e` ; retour au couloir
à 574/576 et au baraquement à 623/624/627, avec nouveaux bruits enregistrés.
À vérifier : pertinence des indices autorisant un rappel, sans assimiler ces appels
à une boucle prouvée. Gorm alterne entretien/garde en crue 11 à 360/365 puis
525/530, et crue 2024 à 535/540 puis 565/570 : nouvelles alertes au seuil ;
entretien/garde déjà présent en crue 11 sur `590653e` à 365/370, mais pas cette
paire en crue 2024 (entretien/autres buts y alternaient déjà). Crue 99,
entretien/abri à 205/210 puis 235/240 : même séquence dans les deux versions.
Ces changements de buts seuls n’établissent pas une boucle fautive.
Les 105 alertes `fige_presse` (105 auparavant), noir et eau
ne prouvent aucun plan admissible ignoré. Pas de contrôle général de toutes les
boucles, du MJ ou du rendu après recharge : les archives contiennent des relevés
et états sociaux finaux, pas une sauvegarde complète à recharger.

Bruts : `C:/Users/msics/donjon/artifacts/verif-integ-057766f/` ; analyse dans
`analyse-131/` : script, tableau détaillé, CSV des **96 nuits** des trois versions,
constats et événements contextualisés, contrôles et empreintes des entrées.
Références et campagnes relues sans modification. Aucune clé Git de signature
configurée ; commit non signé, branche `codex-verif-integ-057766f` poussée.
