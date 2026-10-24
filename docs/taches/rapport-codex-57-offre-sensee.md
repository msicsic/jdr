# Lot 57 — Une offre sensée et un refus retenu

Branche `codex-offre-sensee`, base **c592d68**, brief **aa9168e**, non fusionnée.
Code **e65310c**, signature SSH vérifiée. Aucun appel à Luna, ni modification de
`main` ou de `planification.py`.

**Contrats.** `pnj_propositions._contreparties` et `executer` font juger le marché
inversé par `echanges.evaluer_proposition` : pas de bien gardé ou nécessaire, ni
de perte propre supérieure au gain. `valeur_proposition` conserve la valeur d'un
bien même sans numéraire : le plafonnement d'une dépense aux pièces possédées
mettait à zéro le coût d'un outil pour un PNJ sans argent.

Le refus sauvegardé porte les moyens de cette demande précise et la force de
l'offre réellement faite (`entrees_refus`, `refus_tient`, `retenir_refus`, `tient`).
Un délai, l'estompement de la rancune, un autre bien déplacé ou davantage
d'argent disponible sans montant offert plus élevé ne relancent pas. Même
retenue pour l'achat ; le dernier marché remplace la demande gratuite du bien.
L'ancienne trace de recours reste compatible avec les sauvegardes existantes.

**Ilse reproduite**, crue 7, **minute 353**, sur **5c2ce81** : elle accepte 5 pièces,
demande à Gorm une part de `bois_guet`, reçoit « impossible » et abandonne dans
la minute. Le bois est chez Brune, hors des moyens de livraison de Gorm.
`devis_service` vérifie les fournitures du bénéficiaire sur une copie, par les
livraisons communes, sans jet ni transfert publié. Tâche payée, confiée,
évaluation de marché et contrôle d'empêchement emploient ce devis ; le cas réel
est refusé avant paiement. La scène avant offre est conservée en fixture gzip.

**Vérification ciblée.** Brune/Gorm et autre auditeur, refus après recharge,
fortune accrue sans meilleure offre, moyen nouvellement cru ; achat refusé,
même prix et prix supérieur ; clé gardée de Bram même de faible prix ; passe de
Josse et outil d'Odon trop coûteux, même sans argent ; offre sensée acceptée et
livrée du lot 45 ; même laps découpé et rechargé ; Ilse et seconde réserve de bois,
refus entendu et sauvegardé sans paiement ni abandon consécutif.

**Banc rapide**, 4 h × 1985/7/42/2024 × quatre scénarios, contre **c592d68** :
aucun plantage, violation ou usurpation. Moyennes par nuit, référence → branche :

| Scénario | Offres | Acceptées | Vols tentés |
|---|---:|---:|---:|
| Relais | 0,75 → 0,5 | 0,5 → 0,25 | 0 → 0,5 |
| Mine | 5,25 → 5,25 | 1,25 → 1,25 | 0,25 → 0,25 |
| Auberge | 2 → 1,5 | 0,75 → 0,75 | 0 → 0 |
| Crue | 5 → 2,75 | 0,25 → 0 | 2 → 2 |

**Audit 12 h**, branche seule, offres/acceptées/vols tentés : crue 11 **2/0/2**,
crue 7 **4/0/2**, mine 42 **10/1/1**, mine 1985 **17/2/1**. Aucun plantage,
usurpation ou tâche due aussitôt. Deux paires textuelles à moins d'une heure :
Odon apprend le coffre ouvert (**125 → 139**, empreinte des moyens) ; Lucien
demande deux lots homonymes distincts (**646**, `bois_gaspard_1` puis
`bois_gaspard`, souvenirs sauvegardés). Pas de même offre redite sans moyen
nouveau dans ces quatre nuits. Les autres alertes concernent notamment le noir,
des attentes et un avertissement redit.

**Suite complète unique**, trois processus à priorité réduite : **1 800 tests**,
**4 sauts**, 755,7 s ; trois attentes de scénario ajustées et leurs fichiers
repris en entier. Avec le cinquième test ciblé ajouté : bilan consolidé
**1 801 tests, 4 sauts, aucun échec ni erreur**. Reprises : 38 tests puis les cinq
tests d'offres et les deux de ressources, tous verts. Le test d'appel vérifie
les retrouvailles suivies de la demande ; le banc de récit fixe son jet. Le test
de ressources vérifie encore les trois foyers à cinq heures et le bois fini à
sept heures ; la nouvelle suite de marchés peut laisser un foyer s'éteindre.

**Limites.** Ce filtre protège le proposant ; il ne garantit pas l'acceptation
ni une estimation exacte de la valeur pour l'autre. Le prix absent garde la
convention commune ; aucun nouveau modèle de valeur ou de surenchère. Un moyen
nouvellement cru autorise un essai, sans garantir qu'il aboutira. Les anciennes
tentatives sans nouvelle empreinte ne peuvent reconstituer une offre oubliée.
Le devis vérifie le plan trouvé ; il peut refuser une tâche dont un autre plan
aurait été faisable. Une fourniture perdue ou un refus appris ensuite peut
encore provoquer un abandon. Le banc ne mesure pas une équivalence de temps :
nuits différentes et suite complète en parallèle.
Bruts non versionnés : `artifacts/offre-sensee/`.
