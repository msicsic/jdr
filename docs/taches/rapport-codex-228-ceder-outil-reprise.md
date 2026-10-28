# Lot 228 — Conservation et compensation des capacités

**Branche `codex-ceder-outil-b`, non fusionnée.** Intégration `d9e5166`
fusionnée dans `e938352` (233/238/239/240 inclus) ; compensation `e8feb8f`,
arbitrage des six tests autorisé puis figé dans **`537a352`**.
Aucun MJ, deux travailleurs réduits au plus, commits non signés faute de clé.
Bruts : `C:/Users/msics/donjon/artifacts/ceder-228/reprise/`.

**Invariant.** Une cession ne perd pas une capacité sans compensation réelle.
`biens.valeur_capacites` isole la perte marginale du prix marchand ;
`echanges.necessaire` la compare au gain selon le cédant. Doublon conservé,
remplacement acquis simultanément ou valeur suffisante permettent la cession,
même d'un outil du plan courant. Prêts et réserves consommables restent distincts.
Achat sous-compensé **8,4 contre 0,909 refusé** ; prix compensant annoncé et
honoré. Le cache négatif de recours reste durable à dépendances crues égales ;
version changée pour rejuger les anciens refus sous le nouveau contrat.
Aucune exception par objet. `tenu`, `plan_recours`, `choisir` et les services
protégés n'ont pas été corrigés par 228 ; raccords des lots voisins conservés.

**Analyse préalable hameau 1985/42**, captures de référence `26258b4` :

| Offre | Perte / gain | Décision |
|---|---|---|
| 1985, allumage de torche pour une pièce | Service, aucune cession | Conserver |
| 42, clé de Brune, trois offres à 132–133 min | 12 / 5,174, aucun doublon cru | Maintenir le refus |
| 42, torche de Brune, 230 min | 12 / 4,840, aucun doublon cru | Maintenir le refus |

Ces cessions sous-compensées ne sont pas rétablies pour enrichir le banc.
Leurs états réels rechargés testent refus sans transfert puis prix suffisant.

**Arbitrage des six tests après fusion**, preuves et attentes explicites :

| Fichier | Preuve et adaptation |
|---|---|
| `etapes_chainees` | Lucien conserve ses crochets : capacité 14,4 contre huile 6. Il propose une pièce, refusée pour méfiance. Diff exhaustif : seul ce marché et les souvenirs entendus changent. **Réancrage déclaré du seul hash monde auberge** ; plans, visites, lignes et deux vues gardés. Assertions sémantiques ajoutées. |
| `verifier_eau` | Prêt à Lucien refusé sans transfert ; Bram achète ensuite pour 17 pièces. Compensation, titres et débit/crédit exacts vérifiés au transfert, état et deux vues après recharge. La lampe finit chez Bram. |
| `navettes_garde` | Aucun achat sans fonds ; financer le prix annoncé permet le recours seulement avec absence de solution (`None`). Une garde tenue (`[]`) ne reçoit toujours aucun recours. |
| `crochetage_surenchere` | Nouveau parcours naturel, jets 1/20 : propositions compensées avant la faute, refus ou acceptation ; coût ≤ gain, capacité compensée, transfert ou immobilité, monde/rendus rechargés contrôlés. L'épreuve du bruit du geste imposé isole les négociations et naissances d'agendas. |
| `ouie_temoins` | Même isolation explicite de la faute imposée ; attentes, bruit, reconnaissance par vue et témoins inchangés. |
| `rejeu` | Même isolation ; geste illicite effectivement enregistré, témoins et ordre temporel gardés. |

L'isolation neutralise `recours`, `plan_recours` et `agendas._naissances`
**dans les tests de faute seulement**. Une dette de situation ouvre autrement
un projet commercial autonome ; le nouveau parcours naturel laisse ces voies actives.
**47 tests ciblés distincts verts**, vérifiés par fichiers ; aucun code moteur
supplémentaire changé pendant cet arbitrage. Les MiMo et la torche sont corrigés
par l'intégration 238. **Suite complète finale unique : 2 590 tests / 298 fichiers, 6 échecs,
  zéro erreur, zéro ignoré, 2 609,210 s ; non validée pour intégration.**

**Six écarts finaux dans cinq autres fichiers**, laissés intacts hors extension :
comparaison ciblée de leurs 55 tests sur intégration (97,991 s), puis replays
sur copies pour attribution. Les six fichiers arbitrés passent dans la suite.

| Fichier restant | Cause observée |
|---|---|
| `securite` | Déjà rouge sur `d9e5166` : Ilse rejoint le refuge et reste en compagnie, distance 4 au lieu de ≤ 1. |
| `lumiere` (deux cas) | Rémy allume (et recharge le cas vide), puis rejoint le bureau éclairé et éteint sa lampe à 4 min. L'oracle attend encore le baraquement obscur ; état observé à 13 ou 4 min. |
| `agendas_socle` | Tilo achète du bois pour 1 avant de rendre 19 au joueur ; dette restante de 1 enregistrée, pas de pièce disparue. Priorité du remboursement à arbitrer : ne pas présenter ce parcours comme une restitution complète. |
| `pas_compagnons` | Hameau 1985 : bois vendu à Ilse pour 1, puis crochets proposés pour 8 (refusés : pauvreté/méfiance). Aucune promesse de torche conclue dans les deux minutes ; oracle de trajectoire non réancré. |
| `service_non_defait` | Même hameau sur dix minutes : aucun service de torche conclu, donc assertion non vacuement exigée de service existant en échec. Aucun service payé perdu constaté ; test non déclaré satisfait. |

Ces cinq défauts propres à la branche (plus celui d'intégration) restent à
arbitrer ; aucune modification de leur oracle ni correction moteur spéculative.
Bruts : `arbitrage-restes-integration`, `arbitrage-restes-causes` (JSON/log),
`suite-arbitrage-finale`. Pas de seconde suite complète après ce résultat.

**Mesures de la passe précédente**, référence `3c0e1ca`, avant 233/238/239/240 ;
non présentées comme une nouvelle comparaison de cette intégration :
vingt paires de 4 h, références calculées une fois et cachées, zéro plantage/usurpation.

| Scénario | S/F/D référence → branche |
|---|---|
| Relais | 10,75/4/1,563 → 10,25/4/1,5 |
| Mine | 26,75/5/1,893 → 26,5/5/1,893 |
| Auberge | 11,5/4,5/1,094 → identique |
| Crue | 25,75/7,5/3,5 → 27,25/7,25/3,438 |
| Hameau | 35/8/2,625 → 35,75/8/2,625 |

S hameau **36/26/34/44 → 36/35/28/44**, dans **[26 ; 44]**. Suspects
**2→2**, aucune hausse par nuit ; cycles **507→520**, préemptions **58→54**,
à expliquer **87→84**. Sans recours nul hors crue ; crue **13,75→15 PNJ·min/nuit**.
Mine fixe 1985/4 h : **910→887 recherches (−2,5 %), 10 925→9 959 nœuds (−8,8 %)**.
Temps de passes distinctes non comparés.

**Historique et limites.** Première suite de reprise : 2 558 tests, 8 échecs,
2 erreurs ; attribution par copies : 3 préexistants, 3 hérités de 202, 4 de reprise.
Aucun de ces anciens bilans n'est présenté comme le verdict final.
Relevé de cache conservateur, pas de garantie universelle contre les boucles.
Ancienne lanterne 400→47 à 480 min expliquée par allumages 436/438 séparés par
extinction ; poêle rallumé avec du bois réel. Le rallumage après extinction
d'une autre flamme n'est pas garanti par 228. Créneau dépassé par les vérifications.
