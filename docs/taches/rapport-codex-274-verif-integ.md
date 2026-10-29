# Lot 274 — Vérification d’intégration

29 octobre 2026, branche `codex-verif-integ-3`, code de départ `0bad227`.
**49/49 archives achevées, zéro plantage.** Bruts et `FIN.json` (`ok=true`) :
`C:/Users/msics/donjon/artifacts/verif-integ-0bad227/`. Aucun calcul relancé
pour les références, aucune modification de `donjon/` ou `tools/`, pas de Luna
ni de suite complète. La première interruption vient du redémarrage Windows
planifié de 03:32, pas du jeu ; les archives complètes ont ensuite été
conservées et les nuits manquantes seules relancées.

**Résultats de contrôle.** Zéro usurpation, mort, volonté brisée, écart
`VERIFIER` ou plantage ; les cinq nuits `VERIFIER` + `spatial.VERIFICATION`
0,2 finissent sans assertion spatiale. Captifs : aucun relevé explicite, mais
le format d’audit ne capture pas leur état, donc la captivité exhaustive n’est
pas certifiée. Sur les 19 pertes de service du 227, aucune n’est marquée comme
violation (contre 22 pertes, dont une marquée fautive, à `c870c8b`).

`VERIFIER` atteint 88 bornes à l’auberge graine 42 (74 à `c870c8b`) ; les
88 résultats enregistrés ont le même coût que l’optimum de contrôle. Le cas
Lucien à 435 min, sans plan trouvé à l’ancien relevé, ne réapparaît pas : les
premières bornes actuelles sont à 400 et 437 min. Cela réduit le constat de
recherche manquée, sans supprimer la limite de recherche bornée.

**Moyennes par nuit, `c870c8b` → `0bad227`**, audit 12 h (huit graines,
quatre scénarios) et hameau 12 h (quatre graines). Attente, noir et eau en
PNJ·min ; bascules en moyenne, passages = maximum PNJ/heure ; constats et
avertissements redits selon le lot 241 ; S/F/D selon le lot 183.

| Mesure | Relais | Mine | Auberge | Crue | Hameau |
|---|---:|---:|---:|---:|---:|
| Sans recours / attente | 0/489 → 0/548 | 0/1 132 → 0/1 208 | 0/307 → 0/339 | 0/1 098 → 0,62/1 138 | 3,75/931 → 0/1 062 |
| Noir / eau | 311/— → 324/— | 982/— → 1 043/— | 736/— → 702/— | 51/98 → 24/94 | 79/20 → 133/14 |
| Appels / aide | 1,12/0 → 1,88/0,25 | 16/2,25 → 16,38/3 | 20,38/1,88 → 17,5/2,25 | 4,25/1,38 → 3,75/1,38 | 1/2 → 2,25/1,5 |
| Bascules / passages max | 0/12 → 0,12/9 | 0/30 → 0/27 | 1/35 → 1/40 | 1,38/28 → 0,75/32 | 0,75/22 → 0,25/18 |
| Échanges | 53 → 54,62 | 159,25 → 159,12 | 183 → 197,88 | 64,38 → 59,62 | 116,5 → 109,5 |
| Propositions / acceptées | 8/3,25 → 7,75/3 | 16/1 → 10,38/0 | 9,38/0,25 → 8,5/0,38 | 9,5/1,5 → 7,5/1,12 | 17/3 → 11,25/2,25 |
| Avis exprimés / changements | 0/0 → 0/0 | 0/0 → 0/0 | 0/0 → 0/0 | 1,12/0,38 → 0,75/0,12 | 2,5/0 → 2,25/0 |
| Disputes / pertes de service (moyennes) | 0/1 → 0/1 | 0/0 → 0/0 | 0/0,25 → 0/0,12 | 0,12/0 → 0/0 | 0,25/0,5 → 0,5/0 |
| Constats / avertissements redits | 11,75/0,62 → 11,5/1,25 | 34,75/0,62 → 35,62/1,12 | 45,12/1,88 → 51,25/2,5 | 16,25/0,12 → 17,5/0,75 | 22,25/1,25 → 22,25/1,25 |
| S/F/D | 29,75/5,75/2,72 → 31,62/5,75/3,06 | 104,88/7,25/3,43 → 101,62/7,12/3,50 | 101,50/5,88/2,92 → 107/6,12/3,09 | 35,62/7,38/3,84 → 31,88/7,50/3,69 | 64,50/8,75/3,46 → 56,25/8,50/3,42 |

**Sondes 219/227 et suivis.** Sur les mêmes 49 nuits, le 219 actuel (avant
lot 276) compte **7 suspects et 170 à expliquer**, contre **23 et 376** à
la vérification 241. Il compte aussi 3 906 cycles (3 948), 396 préemptions
(400), **107 changements de moyen**, **106 entrées publiées utilisées** et
une progression réelle ; ces deux classes ne figuraient pas dans le 219 de
241 (lots 265/271). Le 227 relève 19 pertes : 14 cessations physiques et cinq
prestataires partis, toutes non fautives. Hameau : l’attente monte de **931 à
1 062 PNJ·min**, la richesse S baisse de **64,50 à 56,25**, le noir augmente de
79 à 133 et l’eau baisse de 20 à 14. Aucun mandat oral naturel trouvé ; six
activations de l’agenda `evacuer_crue` sont marquées « mandataire estimé »
(une autre est le rejeu de contrôle).

**Alerte nouvelle, à instruire.** Hameau 1985, Gorm (`marchand`), à
`385475` (642 min) : le 219 relève le retour du but « interposer Brune contre
Aubin dans l’antichambre », 7,38 min après sa suspension à 635 min. Pendant
l’intervalle, Gorm s’interpose à 636, change de cible vers Ilse au relevé 640 ;
Aubin quitte l’antichambre à 642 (conduite basse puis refuge) avant la
réactivation du but. Le relevé initial/retour de Gorm est identique. La même
nuit `c870c8b` ne contient pas cette interposition ; son unique suspect est
Brune à 426 min. **Petit lot proposé :** vérifier le contrat général de
revalidation des présences et positions des deux cibles avant l’exécution d’un
but d’interposition repris après interruption, avec ce cas et un second cas
de présence changeante. L’alerte décrit une intention, pas une action fautive.

Autre changement notable : crue 2024, 15 entrées de frappe en neuf secondes,
six coups portés ; Brune est inconsciente au relevé 600 et rétablie à 605.
Aucun coup ne suit l’instant d’inconscience, aucun décès ; la même nuit
`c870c8b` n’avait pas de violence. À suivre dans le contrôle des conséquences
d’action, sans violation établie ici. Le coup Aubin→Gorm de la nuit hameau
1985 (652 min à 241) n’est pas reproduit.

**Cache `main` et verdict.** `main` pointe `c870c8b` ; 20 références cache de
4 h couvrent relais, mine, auberge, crue et hameau. Les préfixes des 20 nuits
actuelles divergent tous avant 4 h (premiers écarts dans les deux premières
minutes) ; ce cache court ne remplace donc pas la comparaison 12 h et les
écarts ne sont pas attribués à un lot unique. Les 49 archives `c870c8b` ont
été relues, jamais rejouées. **Intégration non propre pour avancer `main`**
tant que le petit lot de revalidation de l’interposition n’a pas établi si
l’action est refusée lorsque la cible a quitté le lieu.
