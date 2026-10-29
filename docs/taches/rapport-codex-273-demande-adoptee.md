# Lot 273 — demande adoptée et moyen démenti

29 octobre 2026. **Branche `codex-demande-adoptee`, non fusionnée**,
base `c9459ce`, moteur **`3ec23bb`**, banc sur **`527b505`**.

**Invariant.** `deliberation.choisir` libère le plan démenti sans effacer
sa demande adoptée ni son palier. Revalidation, attente, fin attestée et
préemption suivent le contrat existant ; aucun suffixe périmé recopié,
délai ajouté ou autre fichier moteur modifié. Refus, renoncements et
condition exacte de la demande conservés.

**Preuves.** 21 tests contrat/empathie verts (**98,600 s**), puis 28/29
compléments (**398,297 s**). Capture **Aubin Relais 2024, 117503** : demande
revalidée hors perception, sans sortie ni renaissance ; réessai interdit
dans la minute. **Mathé/Lucien, mine** : attente, moyen constaté puis
repas effectif. Recharges monde/rendu/scène et laps entiers/découpés
identiques ; fins, préemptions et suffixes vérifiés.

**Erreur Lucien instruite.** Test inchangé vert sur `c9459ce` isolée
(**92,579 s**), `KeyError: 'anselme'` sur branche (**67,480 s**). Anselme
conserve l'entretien du poêle : attente **palier 4 / valeur
50**, sécurité **4 / 11,485**, marge **7,5** ; il reste témoin et interdit
le vol. Après restitution refusée, une autre demande conservée ne lui
apprend pas le dépôt du ballot. Le test dépendait de ces deux abandons.
Prémisses explicites : capture historique à 95 min sans entretien
adopté, puis dépôt réellement effectué appris à 110 min. **30 assertions
originales identiques** (AST), test vert (**51,387 s**), neuf contrôles de
recharge. Les 49 autres tests étaient déjà verts ; moteur inchangé lors
de cette reprise. Preuves : `lucien-*/`, `diagnostic-lucien.json`.

**Banc terminé : critère « aucune hausse de suspects par nuit » tenu sur
20/20 paires**, total **1 → 0**. Quatre heures, départ tiré, cinq scénarios,
quatre graines, référence **`0e3e626`**, sonde actuelle **265/271** des deux
côtés ; quarante nuits calculées une fois (cache absent), un processus
réduit, **2 515,732 s**, code 0. Aucune conclusion de vitesse.
Aubin Relais 2024, retour **117518**, est suspect en référence et absent
des suspects de la branche. La trajectoire entière a changé ; la preuve
isolée de conservation de sa demande reste celle de la capture 117503.

Ordre des graines : **1985 / 7 / 42 / 2024**. Chaque composante du vecteur
219 compare une nuit. S/F/D : fonction `cats` du lot 183 inchangée,
signatures famille × auteur × texte exact, familles, moyenne des familles
par PNJ ; moyennes sur quatre nuits, PNJ inactifs compris.

| Scénario | 219 par nuit, référence → branche | S/F/D, référence → branche |
|---|---|---|
| Relais | 0/0/0/1 → 0/0/0/0 | 15,25/4,25/1,750 → 15/4,25/1,625 |
| Mine | 0/0/0/0 → 0/0/0/0 | 25,75/5/1,964 → 15,25/5/1,464 |
| Auberge | 0/0/0/0 → 0/0/0/0 | 9,25/4/1 → 9,25/4,25/1,031 |
| Crue | 0/0/0/0 → 0/0/0/0 | 23,50/6,75/3,063 → 27/6,75/3,250 |
| Hameau | 0/0/0/0 → 0/0/0/0 | 22,75/7,25/2,167 → 24,75/7,25/2,208 |

**Alertes et limites.** Zéro plantage, usurpation ou violation d'audit.
Deux nouvelles observations `voir_alterne` : Gorm, Relais et crue 2024,
relevé 5 min ; elles ne certifient pas une boucle. Deux bascules mesurées
en crue 2024, sous le seuil d'alerte 10. Entrées « à expliquer » **21 → 18**,
mais hausses sur **crue 7 : 0→2 ; crue 2024 : 1→2 ; hameau 42 : 2→4 ;
hameau 2024 : 0→1** ; non diagnostiquées, non déclarées bénignes. Dérives
ouvertes **203 → 205**, cycles **503 → 483**, préemptions **49 → 62**.
Pertes de service **4 → 4** (cessation physique 3→4, bénéficiaire parti 1→0),
aucune violation de service. Attente urgente **695 → 375 PNJ·min**, sans
recours **0 → 0**. **Recul net de richesse à la mine : S −40,8 %, D −25,5 %,
F stable** ; aucune amélioration générale ni stabilité universelle revendiquée.

Ni Luna ni suite complète. **Aucun calcul actif.** Bruts :
`C:/Users/msics/donjon/artifacts/demande-273-sol/`, `banc.json`,
`bilan.json`, `synthese-finale.json`, script `synthetiser-banc.py` ;
**`fin-banc.json` (`ok=true`)**. L'ancien `fin.json` (`ok=false`) archive
la première campagne arrêtée avant banc ; il n'est pas le bilan final.
