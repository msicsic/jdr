# Lot 228 — Conservation et compensation des capacités

**Branche `codex-ceder-outil-b`, non fusionnée.** Base `d9e5166`
(233/238/239/240), fusion `e938352` ; compensation `e8feb8f`, arbitrages
autorisés `537a352` puis **`d3a4d67`**. Aucun nouveau code moteur pendant
les arbitrages. Deux travailleurs réduits au plus, aucun Luna ; commits non
signés faute de clé. Bruts : `C:/Users/msics/donjon/artifacts/ceder-228/reprise/`.

**Invariant.** `biens.valeur_capacites` isole la capacité marginale du prix ;
`echanges.necessaire` et le jugement commun acceptent doublon conservé,
remplacement acquis ou gain compensant selon le cédant, même pour un outil
du plan courant. Achat **8,4 contre 0,909 refusé**. Prêts/réserves distincts.
Recours négatif durable à dépendances crues égales, anciens verdicts rejugés
sous le nouveau contrat. Aucun cas particulier moteur ; fonctions réservées
`tenu`, `plan_recours`, `choisir` et services protégés conservés.

**Analyse préalable hameau**, référence `26258b4` :

| Offre | Perte / gain | Décision |
|---|---|---|
| 1985, allumage pour une pièce | Service sans cession | Reste admissible |
| 42, trois offres de clé à 132–133 min | 12 / 5,174, sans doublon | Refus maintenus |
| 42, torche à 230 min | 12 / 4,840, sans doublon | Refus maintenu |

**Torche native : autre choix, pas interdiction du service.** Douze jugements
de torche avant deux minutes restent admissibles. La vente de crochets contre
huit pièces est maintenant compensée (**P=G=33,899**), classée **6,20** :
la borne d'acquisition d'argent écarte alors le travail moins rentable.
L'intégration interdit cette cession même compensée et choisit le service
classé **55,43**. Les offres de vente échouent ensuite pour pauvreté/méfiance.
Preuve : `torche-cause-synthese.json`, traces complètes `torche-choix-*.json`.

**Arbitrages et preuves**, aucune exception ajoutée au moteur :

| Fichiers | Attente finale |
|---|---|
| Six premiers oracles | Lucien conserve ses crochets (14,4 contre huile 6) : **seul hash monde auberge réancré explicitement**, autres empreintes gardées. Prêt de lampe refusé puis vente à Bram pour 17, titres/comptes/recharge contrôlés. Navettes : aucun recours sur garde tenue. Faute isolée pour bruit/ouïe/rejeu ; marché naturel testé séparément, jets 1/20. |
| `pas_compagnons`, `service_non_defait` | Monde naturel conservé dans un test distinct : service admissible et quatre ventes tentées, aucun outil cédé. **Reconstruction déclarée** du contrat historique : torche d'Ilse remise à Brune, offre typée réellement acceptée/payée, puis autonomie intacte. Annonce sauvegardée, travail tenu, service protégé, monde/rendus et bloc/découpe contrôlés. Chaque ancrage créé est confronté à la croyance au constat ; Ilse non localisée n'est pas réputée partie. |
| `lumiere` ×2 | Extinction juste après arrivée au bureau : chandelle crue allumée, niveau 2, `lumiere_utile=False`. Ordre recharge/allumage/extinction, combustible, état et deux vues vérifiés. |
| `agendas_socle` | Remboursement intégral conservé avec Tilo occupé. Parcours naturel ajouté : achat 1, remboursement 19, dette 1 sauvegardée, aucun double versement ; apport réel prélevé chez Odile puis solde. Or total conservé. |
| `securite` | Intact : distance 4 au lieu de ≤1, déjà reproduite sur `d9e5166` ; placement confié au lot 234. |

**48 ciblés distincts verts**, quatre fichiers, résultats assemblés sans
nouvelle exécution dans `vigilance-cibles-livraison.json`.
**Suite complète laissée au superviseur**, conformément à la consigne et
à `AGENTS.md` **`4422f13`** : passe en cours arrêtée, aucun verdict final
revendiqué (`suite-vigilance-interrompue.json`). Les anciens résultats complets
restent historiques : dernière passe achevée, 2 590 tests, six échecs/zéro erreur,
utilisée pour le diagnostic ; les quatre fichiers concernés sont maintenant verts
en ciblés. Chronique (300) et mémoire (40) bornées expliquent le remplacement
de l'ancienne annonce par l'engagement tenu ; les assertions portent sur ces étapes.

**Mesures antérieures**, vingt paires de 4 h contre `3c0e1ca`
(avant 233/238/239/240), références calculées une fois et cachées :

| Scénario | S/F/D référence → branche |
|---|---|
| Relais | 10,75/4/1,563 → 10,25/4/1,5 |
| Mine | 26,75/5/1,893 → 26,5/5/1,893 |
| Auberge | 11,5/4,5/1,094 → identique |
| Crue | 25,75/7,5/3,5 → 27,25/7,25/3,438 |
| Hameau | 35/8/2,625 → 35,75/8/2,625 |

S hameau **36/26/34/44 → 36/35/28/44**, dans **[26 ; 44]**. Suspects
**2→2**, sans hausse par nuit ; cycles **507→520**, préemptions **58→54**,
à expliquer **87→84** ; zéro plantage/usurpation. Sans recours nul hors crue,
crue **13,75→15 PNJ·min/nuit**. Mine : **910→887 recherches, 10 925→9 959
nœuds (−8,8 %)**. Temps distincts non comparés ; aucun nouveau banc sur `d9e5166`.

**Limites.** Cache conservateur ; aucune garantie universelle contre les boucles
ni de sélection d'une offre admissible. Ancienne lanterne 400→47 expliquée par
allumages 436/438 séparés par extinction ; poêle rallumé avec du bois réel.
Rallumage après extinction d'une autre flamme non garanti. Créneau dépassé ;
détails supplémentaires dans `vigilance-detail-avant-4422f13.md` (bruts).
