# Lot 52 — acquisition d'une capacité nouvelle

Branche `codex-capacite-nouvelle`, non fusionnée ; base `5c2ce81`, ancien `42bb9c0`.
Pas de Luna, coût, plafond ou scénario changé ; lot 51 intact.

**Résultat : règle généralisée, mais pas d'accélération démontrée.** Sur les huit nuits de 12 h,
monde et décisions sont identiques à la base, recherches comprises (`comparer --calcul`).
Mine : 4 914 717 nœuds avant comme après, CPU 941,02 → 959,53 s (+2 %). Auberge :
2 577 681 → 2 575 090 nœuds (−0,10 %), CPU 835,74 → 830,89 s (−0,6 %). Les 486 recherches
bornées restent les mêmes. C1 ne résout pas la lenteur actuelle.

**Mesure préalable**, première minute de la capture à 480, appels de `gestes` (catégories
cumulables, inventaire initial compris) :

| Capture | États développés / avec acquisitions | Lumière | Allumage | Crochetage | Choc | Combustible | Clés |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mine 1985 | 1 727 / 1 625 (94,1 %) | 1 653 | 1 047 | 112 | 56 | 984 | 474 |
| Auberge 1985 | 1 917 / 1 037 (54,1 %) | 905 | 0 | 1 861 | 0 | 337 | 1 917 |

Aucun contenant porté ni monnaie. Acquisitions dominantes : lampes, briquet, huile.
Ce relevé à 8 h ne décrit pas toute la fin de nuit ; un préparatif n'est pas nécessairement redondant.

**Définition.** `Vue.capacite` : facettes `(emploi, cible, qualité, sans faute)`, lues des serrures,
substances/sources rechargées, outils/qualités (`force`, armes), lumière. `capacites_portees` les
réunit ; `couvre` les compare ; `doublon` filtre les cinq acquisitions communes de `gestes` et
`_aide_sur_place`, référence comprise. Le but garde ses objets. Lectures déjà dans `_entrees`
et la FOR modulée de `chercher`. [Définition complète et preuve](../plan-planificateur.md).

**CPU**, secondes **ancien / base / branche** : versions lancées ensemble, deux nuits au plus
par version, trois travailleurs partagés à priorité réduite, sans cache. Petits écarts non significatifs.

| Nuit | Total | 0–4 h | 4–8 h | 8–12 h | Nœuds base → branche | Bornées ancien / base / branche |
|---|---|---|---|---|---|---|
| Mine 42 tiré | 87.4 / 61.2 / 61.7 | 8.2 / 9.4 / 9.1 | 15.4 / 14.6 / 14.6 | 63.7 / 37.1 / 37.9 | 456697 → 456697 | 108 / 0 / 0 |
| Mine 1985 tiré | 78.3 / 489.8 / 499.7 | 7.3 / 10.8 / 10.5 | 21.0 / 45.2 / 45.2 | 50.0 / 433.7 / 444.0 | 1624710 → 1624710 | 4 / 137 / 137 |
| Auberge 42 tiré | 69.9 / 253.4 / 246.4 | 5.3 / 8.7 / 8.7 | 10.5 / 48.8 / 49.0 | 54.1 / 195.8 / 188.6 | 707533 → 707413 | 0 / 2 / 2 |
| Auberge 1985 tiré | 58.6 / 129.4 / 131.8 | 4.5 / 7.7 / 7.6 | 10.2 / 37.4 / 39.4 | 43.9 / 84.2 / 84.8 | 372848 → 372842 | 8 / 0 / 0 |
| Mine 42 fixe | 74.3 / 167.9 / 172.6 | 6.8 / 11.0 / 11.2 | 13.7 / 42.7 / 44.3 | 53.7 / 114.2 / 117.1 | 1195859 → 1195859 | 16 / 0 / 0 |
| Mine 1985 fixe | 182.4 / 222.1 / 225.4 | 6.7 / 10.5 / 10.9 | 14.1 / 36.6 / 37.6 | 161.5 / 174.9 / 176.9 | 1637451 → 1637451 | 56 / 144 / 144 |
| Auberge 42 fixe | 69.0 / 90.0 / 88.3 | 5.1 / 11.5 / 11.5 | 14.8 / 31.6 / 32.0 | 49.0 / 46.9 / 44.7 | 275003 → 275003 | 37 / 0 / 0 |
| Auberge 1985 fixe | 72.4 / 362.9 / 364.4 | 5.7 / 12.0 / 11.8 | 8.5 / 20.1 / 21.1 | 58.2 / 330.8 / 331.4 | 1222297 → 1219832 | 3 / 203 / 203 |

**Vérification.** Captures rejouées de 480 à 570, caches vides : 1 236 recherches, mêmes 425 365
nœuds à la mine ; 2 547 recherches, 274 277 → 274 241 à l'auberge ; aucun écart. Joss à 491 :
967 → 931 nœuds, même plan que la complète (967), capture versionnée, monde/lignes/rendu vérifiés
après recharge. À 480, résultat de la complète, **sans réduction supplémentaire**. Sept nouveaux
tests : outils équivalent/meilleur, combustibles identique/autre substance, clés identiques/réunies,
cible du but, cinq acquisitions et mémoire invalidée. Empreintes 2 h, quatre scénarios × quatre
graines : identiques. `VERIFIER` et spatial 1, mine/auberge 42, 2 h : sans écart ni borne.
Suite complète unique, trois processus à priorité réduite : **1 766 tests, 4 ignorés**, verte, 749,8 s.

**Limites.** Vivres, contenants et foyers gardent leur identité ; l'argent acquis n'augmente pas
le budget projeté. Couverture prudente sans permission, pas de cumul de quantités, d'usure future
ou d'encombrement ; parts estimées. Pas de preuve d'équivalence générale des contenants ni de
gain sur les capacités différentes. Bruts : `artifacts/capacite-52/` ; outils reproductibles :
`mesurer_capacites.py`, `verifier_capacites.py`, `mesurer_capacites_nuits.py`.
