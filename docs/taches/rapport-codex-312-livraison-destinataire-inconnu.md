# Lot 312 — livrer à un destinataire de lieu inconnu

29 octobre 2026. Branche **`codex-livraison-inconnu`, non fusionnée**, base
**`06465d9`**, moteur vérifié **`cf0adfd`**. **Lot terminé**, branche poussée,
aucun calcul actif. Aucun MJ, scénario, `biens.py`, `dialogues.py` ni `mj.py` modifié.

**Invariant et code.** Inconnu ne signifie pas absent. `_devis_remise` vérifie
l'acquisition, puis chiffre inspection, appel ou question par `_localiser`,
extrait du service 303, et `_chercher`. Devis, `planifier_tache`,
`echanges.empeche` et annulation gardent ce contrat unique. Aucune remise ni
restauration sur une présence supposée. `_contact_possible` écarte mort et
départ crus, aussi dans `rejoindre`. Ni position cachée, délai de reprise ou
champ de sauvegarde ajouté.

**Six preuves.** Relais 7 à **856**, repris avant l'annulation observée au 308 :
Gorm garde but, motif, date et charges suspendues, demande Aubin à Brune puis
livre `vivres_1`. La fonction de devis extraite de `06465d9` reproduit plan
`None` et empêchement vrai. Mathe/Lucien à la mine exerce l'autre chaîne.
Monde/rendu/scène/textes identiques après recharge réelle et **huit minutes
entières ou découpées** ; parole tenue, aucun abandon. Devis pur, indépendant
des positions cachées ; départ cru, bien détruit et recours épuisés empêchent
encore. Le seul temps ne rouvre pas une recherche.

**Tests : 95/95 verts, onze fichiers, 1 328,220 s**, zéro échec, erreur ou
ignoré. Première passe conservée : deux fixtures spatiales corrigées, oracle inchangé.
**Banc : douze paires de 4 h**, départ tiré, un travailleur réduit, référence
puis branche ; douze références manquantes calculées une fois et rangées en
cache, puis douze nuits de branche, **1 352,251 s** cumulées. Aucun plantage ni
usurpation ; huit chroniques identiques.

| Nuit | Livraisons tenues | Annulées | Portions servies | Suspects 219 |
|---|---:|---:|---:|---:|
| Relais 1985 | 0 → 3 | 3 → 0 | 1 → 1 | 0 → 0 |
| Relais 7 | 2 → 3 | 1 → 0 | 0 → 1 | 0 → 0 |
| Relais 42 | 3 → 3 | 0 → 0 | 0 → 0 | 0 → 0 |
| Relais 2024 | 0 → 3 | 1 → 0 | 2 → 2 | 0 → 0 |
| Auberge 1985 | 3 → 4 | 1 → 0 | 3 → 4 | 0 → 0 |
| Auberge 7 | 1 → 1 | 0 → 0 | 2 → 2 | 0 → 0 |
| Auberge 42 | 1 → 1 | 0 → 0 | 3 → 3 | 0 → 0 |
| Auberge 2024 | 0 → 0 | 0 → 0 | 3 → 3 | 0 → 0 |
| Mine 1985 | 1 → 1 | 0 → 0 | 6 → 6 | 0 → 0 |
| Mine 7 | 1 → 1 | 0 → 0 | 3 → 3 | 0 → 0 |
| Mine 42 | 1 → 1 | 0 → 0 | 4 → 4 | 0 → 0 |
| Mine 2024 | 1 → 1 | 0 → 0 | 3 → 3 | 0 → 0 |
| **Total** | **14 → 22** | **6 → 0** | **30 → 32** | **0 → 0** |

Une preuve commune compte une livraison : le récapitulatif initial doublait les
reçus donneur/destinataire. `synthese.json` corrigé, brut conservé. À l'auberge
1985, Odile livre `vivres_1` à Mathurine à la minute 95 au lieu d'abandonner à 93.

**Boucles et avis.** Aucun nouveau seuil de répétition, aucune bascule ni
répétition nouvelle d'appel ou de question : dans les quatre nuits modifiées,
toutes les reprises existantes gardent exactement textes et instants de la
référence. Le seuil `repetition` d'auberge 2024 est inchangé, chronique identique.
**Aucun essai nouveau repris par le seul délai identifié.** Les deux nouveaux
avis de Gorm (Relais 7/2024) sont des retours à la livraison après rencontre
d'Aubin, aux instants **1710/1342** : provenance de son lieu `entendu → vu`,
puis remise réussie à **1772/1650**, pas une relance chronométrée. Les classes
brutes sont conservées : avis à expliquer **11 → 12**, dérives **186 → 199**
(dont +7/+11 aux Relais 7/2024, −6 au Relais 1985, +1 à l'auberge 1985).

**Limites.** Rencontre incertaine ; échéance historique des paroles à **240 min**
inchangée. Les douze avis et 199 dérives ne sont pas tous certifiés bénins :
aucune garantie universelle contre les boucles ni gain de coût revendiqué.
Ni Luna ni suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/livraison-312/` : `tests-cibles.json`,
`banc.json`, `synthese.json`, `analyse-alertes.json`, `analyse-repetitions.json` ;
`fin.json` conservé et **`fin-cloture.json`, ok=true**. Code/tests inchangés
depuis les vérifications.
