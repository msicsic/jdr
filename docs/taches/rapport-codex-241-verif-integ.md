# Vérification d’intégration c870c8b — lot 241

28 octobre 2026, PC fixe, branche `codex-verif-integ-2`, départ
`c870c8b4797b5c4072a3b0a63043e212aae62a39`. **49/49 nuits achevées,
zéro plantage ; intégration non déclarée verte.** Un travailleur détaché,
priorité réduite, de 14 h 12 à 18 h 11 ; aucune nuit rejouée, aucun pull,
Luna ni suite complète. Diff `donjon/ tools/` vide contre le départ.
Les 49 archives de `4306c14` sont exclusivement relues (47 nuits achevées).

**Contrôles.** Les cinq contrôles 8 h `VERIFIER` + spatial 0,2 terminent,
notamment mine 42 et rixe 42, arrêtées auparavant : zéro assertion de pureté
et zéro écart VERIFIER/spatial consigné. **Lucien, auberge 42 : 75 → 74
bornes**, mais **73 → 1** anciennes bornes à résultat exact et **2 → 73
plans manqués** : dès 435, garde du grenier (optimum 125,64), puis chambre
chaude jusqu’à 480 (optimum 108,32 à 105,12). Défaut de recherche bornée
persistant et amplifié ; invariant à traiter : ne pas confondre épuisement
du budget et impossibilité, sans modifier ici le moteur.

Moyennes **4306c14 → c870c8b**, huit nuits de 12 h/scénario, quatre au
hameau ; durées en PNJ·min, passages = maximum PNJ/heure. Tâches =
offertes/acceptées/tenues/rompues ; S/F/D = signatures/familles/diversité.
Les lignes 219/227 sont des sommes, sur ces mêmes nuits complètes.

| Mesure | Relais | Mine | Auberge | Crue | Hameau |
|---|---:|---:|---:|---:|---:|
| Sans recours | 2,50 → 0 | 58,12 → 0 | 4,38 → 0 | 0 → 0 | 10 → 3,75 |
| Attente | 470,62 → 489,38 | 1 321,25 → 1 132,50 | 430 → 306,88 | 1 162,50 → 1 097,50 | 1 761,25 → 931,25 |
| Noir | 296,88 → 311,25 | 891,25 → 981,88 | 818,75 → 735,62 | 61,25 → 51,25 | 270 → 78,75 |
| Eau | — | — | — | 96,25 → 98,12 | 6,25 → 20 |
| Appels/aide | 1,62/0,25 → 1,12/0 | 17,50/1,62 → 16/2,25 | 21/2,75 → 20,38/1,88 | 3,38/1,38 → 4,25/1,38 | 5,75/2,25 → 1/2 |
| Bascules/passages | 0,12/11 → 0/12 | 0,25/24 → 0/30 | 0,62/246 → 1/35 | 0,62/28 → 1,38/28 | 0/22 → 0,75/22 |
| Échanges | 52,88 → 53 | 158,62 → 159,25 | 188 → 183 | 68,12 → 64,38 | 158 → 116,50 |
| Propositions/acceptées | 8,38/3,38 → 8/3,25 | 14,12/0,50 → 16/1 | 10,25/0,50 → 9,38/0,25 | 9,75/1,75 → 9,50/1,50 | 19,25/4,50 → 17/3 |
| Offres identiques < 60 min | 0 → 0,12 | 0,25 → 0 | 0 → 0,12 | 0,12 → 0 | 0,25 → 0 |
| Avis/adoptés | 0/0 → 0/0 | 0/0 → 0/0 | 0/0 → 0/0 | 0,88/0 → 1,12/0,38 | 1,75/0 → 2,50/0 |
| Disputes/services constatés | 0/1,12 → 0/1 | 0/2,88 → 0/2,38 | 0/2,88 → 0/2,62 | 0,38/1,88 → 0,12/1,50 | 0,75/4,25 → 0,25/2,75 |
| Tâches | 1,50/1/1/0 → 1,62/1/1/0 | 0,88/0/0/0 → 1,50/0/0/0 | 0/0/0/0 → 0,12/0/0/0 | 1/0,25/0,25/0 → 0,12/0/0/0 | 3,50/1/1/0 → 2,25/0,50/0,50/0 |
| Constats/avertissements redits | 10,12/0,50 → 11,75/0,62 | 37,25/1,38 → 34,75/0,62 | 47/2,25 → 45,12/1,88 | 19,25/0,25 → 16,25/0,12 | 21/1,50 → 22,25/1,25 |
| S/F/D | 31/5,88/2,97 → 29,75/5,75/2,72 | 99,75/6,75/3,43 → 104,88/7,25/3,43 | 109,62/6,12/3,08 → 101,50/5,88/2,92 | 35,62/7,12/3,59 → 35,62/7,38/3,84 | 80,25/9/3,88 → 64,50/8,75/3,46 |
| 219 suspects/à expliquer | 3/27 → 1/24 | 4/90 → 7/107 | 6/105 → 8/88 | 0/85 → 3/67 | 15/53 → 2/42 |
| 227 physique/départ cru/fautif signalé | 8/0/0 → 8/0/0 | 0/0/0 → 0/0/0 | 1/0/0 → 2/0/0 | 0/1/0 → 0/0/0 | 4/0/0 → 1/0/1 |

**Bilan et suivis.** Sur l’ensemble (47 → 49 nuits achevées), suspects 219
**31 → 23**, à expliquer **390 → 376**, cycles **3 781 → 3 948**, préemptions
**493 → 400**, satisfaction par autrui **2 → 1**, progression **1 → 0**.
Les huit rixes terminent sans coup/mort, avec deux suspects comme avant.
Zéro usurpation/mort ; **un coup porté et touché**, hameau 1985 à 652 :
Aubin assomme Gorm puis prend la torche ; Gorm est inconscient au relevé 655.
Absent de la même nuit ancienne, ce coup n’est pas en soi une violation.
Aucune volonté brisée relevée ; captivité exhaustive non certifiée.
Les **4 → 17 `ecarts`** comptent les pas laissés à autrui, pas des violations.

Anselme auberge 7, 420–479 : **246 → 4 passages**, aucune navette à 430–435.
Gorm hameau 1985, 541–545 : **onze suspects chaleur/devoir → zéro** ;
son épisode d’entretien du brasero dure de 532 à 720. Ce changement de
trajectoire ne mesure pas isolément l’effet du 240. Mine : sans recours
**58,12 → 0** ; le noir augmente malgré cette amélioration de classement.
Hameau : S **80,25 → 64,50 (−19,6 %)**, acceptées **4,50 → 3** : baisse
cohérente avec la perte acceptée après 233, sans attribution exclusive.
L’attente baisse de **47,1 %**, les avis adoptés restent à **zéro**.
Départs dans la minute d’un « Ici, viens ! », même comptage textuel :
**39 → 24**, dont auberge **15 → 6**, crue **10 → 15**, hameau **2 → 0**
(tous groupes inclus). Candidats seulement : urgence, partenaire et clôture
effective ne sont pas certifiés par ce comptage.

**Petits lots à instruire, aucun correctif.** Le 227 relève **22 pertes** :
21 physiques, une signalée fautive, zéro départ cru/tiers/cause inconnue.
Cas nouveau : Brune hameau 1985, paiement d’Ilse à 1, réussite à
`2436`, extinction à **41 (`24600`)** ; avant le geste, Ilse et torche crues
en crypte, `parti=false`. Sur `4306c14`, même service perdu physiquement à
64, sans extinction. Invariant à vérifier : clôture d’un service payé et
réutilisation du résultat doivent partager la preuve de départ. **Violation
moteur non certifiée** : la sonde conserve le paiement, mais pas l’historique
des clôtures ; son critère n’intègre pas l’ancrage ajouté par 238.
Autres alertes nouvelles : Bram mine 2024 à **613**, retour lumière après
`manque:acheter` via garde, sans nouvelle entre abandon et retour (aucun
même retour dans cette nuit ancienne) ; Gorm hameau 7 à **682**, engagement
du brasero → attente de Sève → même but, état initial retrouvé. La référence
contient ce but à 255/285 et 645/661, mais pas ce retour immédiat.
Invariant à instruire : réessai causal et continuité de l’attente ; ces
alertes ne prouvent ni répétition du même geste ni boucle durable. Aubin
crue 2024 à 39 reste le changement de moyen déjà arbitré au 233.
Autre alerte à expliquer : Ilse crue 7, entretien du poêle pendant
450 min dès 275 malgré la faim ; les relevés ne prouvent pas l'existence
d'un recours alimentaire admissible, donc pas de violation de priorité certifiée.

**Limites et preuves.** Aucun monde complet/rendu après rechargement dans
ces archives, aucune garantie universelle des boucles ni cause de lot
isolée. Temps de référence non comparés. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/verif-integ-c870c8b/` : 49 archives,
`FIN.txt`, lanceurs/journaux et `analyse/` (mesures, contrôles,
`suivis241.json`, `suspects241.json`, `preuves241.json` et manifestes).
