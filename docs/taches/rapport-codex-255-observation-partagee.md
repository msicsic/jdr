# Lot 255 — chronologie des observations partagées

**Non fusionnable : les deux critères du brief échouent. Chantier 206 → 235 →
250 → 255 à mettre de côté selon la décision consignée au brief.** Branche
`codex-sait-observations-c`, moteur `58beadb` ; intégration `4318a5b` fusionnée
sans rebase dans `5eac995`. Conflits réunis, deux tests d'étapes conservés,
`recevoir_statuts` du 254 conservé.

**Invariant et correction.** Capture historique `9371144`, hameau 1985 à 219 :
Brune annonce 79 cm stables observés à 216 ; Aubin répète sa hausse estimée à
211. La co-perception existait ; le suivi écrasait les précisions sans date et
confondait vitesse inconnue et zéro. `social._retenir_information` et `_nouveau`
datent chaque composante de portée dans la voie commune parole/observation ;
un niveau seul ne rajeunit pas une direction ancienne. `esprits.verifier`
valide les dates ; `None` distingue l'inconnu du zéro. Aucun accès nouveau à
l'esprit de l'auditeur, aucun MJ/scénario/planificateur modifié hors fusion.

**Preuves ciblées : 83 tests distincts verts / neuf fichiers** (82/82 en
67,439 s, complément final 4/4 en 4,916 s). Capture 219 rejouée sur trois minutes,
entière ou en douze laps ; monde/rendu/scène/mots rechargés identiques. Autre
scène au Relais : précision partielle, vraie décrue encore annoncée ; auditeur
de dos toujours informé, date invalide refusée. Oracle du point commun devenu
`[1, None]` au lieu de `[1, 0]`, assertions sur la vitesse privée et la décrue
commune conservées. Pas de nouvelle suite ni de test relancé à cette clôture.

**Banc terminé : 20 paires × 4 h**, référence exacte **4318a5b**, cache commun,
un travailleur réduit ; 1 587,766 s écoulées, moteur figé, zéro plantage/usurpation.
Les temps du cache ne sont pas comparés. Valeurs S/F/D selon le lot 183 :

| Scénario | Confidences réf. → 250¹ → 255 | S/F/D réf. → 250¹ → 255 |
|---|---|---|
| Relais | 28 → 26 → 17 | 13,25/4,25/1,563 → 13,75/4,50/1,813 → 14,25/4,25/1,938 |
| Mine | 68 → 54 → 61 | 28,50/4,75/2,036 → 20/4,25/1,536 → 19/4,25/1,500 |
| Auberge | 43 → 19 → 18 | 11/4,25/1,063 → 10,75/4,25/0,969 → 10,75/4,25/0,938 |
| Crue | 49 → 48 → 52 | 18,75/6,25/2,750 → 21,50/6,50/3 → 21,25/6,50/3,063 |
| Hameau | 46 → 122 → 140 | 21,75/7/2,083 → 43,75/8/2,667 → 48,75/8/3,167 |

¹ Historique 250 sur l'ancienne intégration 1194876 : les trois colonnes ne
mesurent pas le seul delta 255. **Redites : 0 → 46 → 21** ; les 46 du hameau
1985 disparaissent, mais **21 au hameau 7** : à 204–215, Maël annonce la baisse,
Ilse puis Aubin la hausse, même niveau de conduite. L'invariant n'est donc
pas garanti généralement ; aucune nouvelle correction ni exception ajoutée.

**Suspects bruts : référence 2 → 255 4** (250 historique : 8). Hausse par nuit :
mine 1985 **0 → 2**, hameau 1985 **0 → 1** ; crue 7 **1 → 1**, auberge 2024
**1 → 0** ; les seize autres nuits **0 → 0**. Arbitrage conservateur, compteurs
inchangés, preuves et chroniques aux bornes dans `arbitrage-preuves.json` :

- **Lucien, mine 1985, 1 → 198 → 206 : maintenu.** Abri, repos réel puis retour
  près de Rémy ; repos 94,9 → 78,9, sécurité 62,4 → 59,6. Variation continue
  plausible, mais aucun certificat de priorité ne justifie le retour : pas de
  reclassement opportuniste en cycle accompli ni preuve de redite commune.
- **Mathe, mine 1985, 118 : maintenu.** Achat de pain pour Gaspard abandonné à
  70815, repris à 70890 ; Gaspard revient au baraquement, sans preuve que ce
  déplacement lève l'échec d'achat. Pas de correction de service revendiquée.
- **Aubin, hameau 1985, 1–2 : maintenu.** Gorm cru à l'échoppe puis absent ;
  questions à Brune, Ilse, Maël, nouvelle recherche. Capture historique par
  gestes conservée ; aucune entrée nouvelle entre abandon et reprise établie.
- **Aubin, crue 7, 3 : préexistant, maintenu.** Même triplet 2014/2029/2059
  dans les deux variantes : absence de Gorm, puis enquête auprès de Brune.
  L'issue parlée change (« dit » → « rien »), pas le signalement.

Le suspect de référence Odile (auberge 2024, 226–227) disparaît du candidat ;
sa chronique de référence montre acquisition, jonction puis remise à Mathurine,
mais aucune soustraction au compteur de référence n'est faite. Les deux anciens
suspects 250 absents (Mathe 150–177, Aubin hameau 2024) ne sont pas déclarés corrigés.
Cycles **489 → 502**, préemptions **46 → 45**, à expliquer **55 → 83**, dérives
**233 → 211**, états payés perdus **5 → 5**. Aucun gain général revendiqué.

**Limites :** anciens suivis sans date non enrichis ; contradictions de même
date non arbitrées par le mécanisme. Régression 251 des parts promises signalée
par le superviseur, réservée au 259 : ni corrigée ni invoquée comme cause prouvée
ici ; aucun nouveau test en échec observé à cette clôture. Aucune suite complète
ni Luna. Bruts : `C:/Users/msics/donjon/artifacts/partagee-255/` (`fin.json`,
`criteres.json`, `synthese.json`, `arbitrage-preuves.json`).
