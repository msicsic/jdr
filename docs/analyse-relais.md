# Analyse : ce qui décide une nuit du Relais

Branche `tension-relais`, analyse sans modification du moteur ni de `scenario_relais.json`.
Question : une nuit du Relais (`banc_pnj --heures 8 --joueur chambre_cloche`) semble décidée par
le jet de la minute 5 ; la tension est mince. Où se décide-t-elle, qu'est-ce qui reste figé,
pourquoi, et que changer ?

## Méthode

- `tools/tension_relais.py jouer` joue des nuits par `banc_pnj.executer` (mêmes chroniques et
  mêmes mesures que le banc, vérifié sur 1985 et 7) en notant chaque jet (minute, auteur,
  fonction, valeur) et un échantillon de l'état toutes les 5 minutes (salle, but et besoins de
  chaque PNJ ; vivres, bois, planches, brasero, réserve, crochets). `resumer` compare des fichiers.
- Base : 48 graines (1 à 40, 1985, 42, 2024, 99, 500, 777, 1234, 4242), 8 h ; variantes et
  comparaisons sur les graines 1 à 32. Le banc lui-même a joué 16 graines avec `--chronique` et
  `--sortie` (récits relus pour 1985 et 7), et `--rejeu` a écrit les pages de 1985 et 7 (non versionnées).
- Indicateurs : *nuits distinctes à t* (chroniques identiques jusqu'à la minute t), *écart de
  salle* (part des PNJ dans une salle différente, moyenne sur les paires de nuits), jets par nuit
  et avant 120 min, *issues* (qui a mangé combien, et s'il y a eu un geste illicite), puis les
  mesures du banc.

## Ce qui décide une nuit

**Le seul hasard est le jet de dés, et il y en a peu.** `Monde.d20` tire le jet n de la graine
s par `Random("s:n")` : deux graines dont les premiers jets ont la même issue donnent la même
nuit (1985 et 1 sont identiques, 99 et 4, 11 et 10). Tout le reste (états de départ, dérives des
besoins, rondes, durées des gestes, perception) est déterministe et identique d'une graine à
l'autre.

7,7 jets par nuit en moyenne (4 à 24), presque tous de deux sortes :

| jet | par nuit | quand |
|---|---|---|
| persuasion (part demandée) : Brune → Gorm | 1,0 | minute 6, toujours |
| crochetage de Brune (une minute par essai) | 2,6 | 123 à 140, si Gorm a refusé |
| persuasion d'Ilse, d'Aubin, de Gorm (planches) | 4,0 | 245 à 475 |

Jets par heure : 1,0 · 0 · 2,6 · 0,06 · 1,3 · 1,35 · 0,96 · 0,38. La plus longue plage sans
aucun jet dure 193 minutes en moyenne (117 au moins).

**L'arbre des nuits** (48 graines) :

| minute | nuits distinctes |
|---|---|
| 0 à 5 | 1 |
| 6 à 120 | 2 (Gorm promet à Brune : 27 ; il refuse : 21) |
| 150 à 240 | 12 (minute du crochetage réussi, 123 à 140) |
| 300 | 19 |
| 480 | 27 |

Le jet de la minute 6 réussit sur 9 ou plus (DD 12 − 2 d'altruisme de Gorm − 2 de confiance + 1
de VOL ; Brune n'a ni CHA ni ELO) : 60 %. Puis plus rien d'aléatoire pendant deux heures dans la
branche du refus, quatre heures dans celle de la promesse : les 27 nuits « promis » restent
**identiques à la case près** jusqu'à la minute 252 (écart de salle 0,00 entre elles).

**Les deux branches se rejoignent.** Écart de salle entre une nuit « promis » et une nuit « refus » :
0,25 à 10 min, 0,25 à 120, 0,17 à 240, 0,07 à 300, 0,05 à 480. Les buts diffèrent plus (0,4 à 0,5),
mais les gens sont aux mêmes endroits : Brune passe la nuit au refuge puis trois heures près du
brasero, quelle que soit la branche ; Aubin fait ses rondes sur le même rythme (salles toutes les
5 min, graine 1985) :

```
aubin  RRRRRRRCCCRRRVVVRRRRRRRRRVVVRRRRRRRRRVVVRRRRRRRRRVVVRRRRRRRRRVVVRRRRRRRVVVVCCCRRRR…
brune  RVRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCRRRR…
```

**Les issues sont presque toujours les mêmes.** Sur 48 nuits, 7 issues : chacun mange une part
(Brune donnée ou volée), Aubin a la quatrième ou non. Le jet de la minute 6 change *comment* Brune
mange, pas *qui* mange. Le vol ajoute trois méfiances et une rumeur, rien d'autre : personne ne lui
reprend les crochets, ne déplace les vivres, ne la surveille autrement ; Gorm a « garder ses biens
(biens) » sans geste à faire dix fois dans la graine 7.

## Ce qui reste figé

- **Le calendrier de la faim.** Première minute où la faim atteint 70 : Brune 0, Ilse 245, Aubin
  345, Gorm 395, dans les 48 nuits. Les demandes de part tombent à ces minutes (6, ~252, ~352,
  ~400), et ce sont elles qui portent presque tous les jets. Une part rassasie de 50, soit 8 h 20 de
  faim : chacun n'a qu'une crise par nuit.
- **Les rondes** (Gorm 45 et 90 min, Ilse 40 et 40, Aubin 30 et 60), déclenchées par une sécurité ou
  un devoir urgents en permanence par conception (`docs/plan-pnj.md`, jalon F).
- **Le feu.** Gorm recharge à 110 (ou 122) et 227 (ou 235), demande les planches d'Aubin vers 360,
  essuie un refus une fois sur deux ; le brasero s'éteint vers 385 dans 46 nuits sur 48. Sans
  conséquence : le froid sec monte de 2 par heure, la chaleur la plus haute en fin de nuit est 60
  (seuil 70), 21 minutes·PNJ de froid urgent par nuit en tout.
- **L'emploi du temps.** Aux échantillons, sans aucune intention : Gorm 64 %, Ilse 69 %, Brune 82 %,
  Aubin 84 %.
- **Brune ne fait qu'attendre.** Refusée, elle prend la trousse (min 7), guette 30 minutes sans
  témoin (`PATIENCE`), renonce, attend 60 minutes (`REPIT`), revient à 97, guette encore ; la
  première tentative de crochetage a lieu à la minute 123 dans les 21 nuits « refus », quand sa faim
  passe 95 (`DESESPOIR`) et lève la condition « sans témoin ». Ce n'est pas une occasion saisie, c'est
  un seuil franchi à heure fixe ; d'où des témoins (Ilse, Gorm) presque à chaque fois.
- **Le deuxième acte est coupé.** Dans la branche « promis », Brune a de nouveau faim vers 400, au
  moment où Gorm, affamé lui-même, garde la dernière part (`necessaire`) ; elle reprend la trousse et
  guette… et la nuit s'arrête à 480. Joué sur 12 h (24 graines), elle force la réserve dans 23 nuits
  sur 24, deux fois dans 7 d'entre elles.

## Causes

### Données du Relais

1. **Une seule personne peut fauter.** Gorm, Ilse et Aubin ont honnêteté et douceur 100 : ni vol, ni
   mensonge, ni poussée. Tout conflit passe par Brune, et Brune par une seule ressource.
2. **Les ressources ne manquent qu'à la fin.** 4 parts pour 4 bouches dont trois n'ont faim qu'après
   4 h ; le bois tient jusqu'à 385 min et son manque ne coûte rien (froid trop lent). Le seul
   arbitrage réel (la dernière part, les planches d'Aubin) tombe en dernière heure.
3. **Tout se passe dans la salle de tous.** Réserve, Gorm, abri des évacués : le refuge. Brune n'y a
   jamais d'occasion ; la discrétion n'y joue aucun rôle.
4. **Des états de départ synchronisés** : les crises de faim sont réglées par les minutes déclarées
   (`corps.repas`) et arrivent à heure fixe, trois d'entre elles en même temps (245 à 400).
5. **Aucun événement** : le Relais ne déclare pas d'horloge ; rien n'arrive que les PNJ n'aient
   eux-mêmes provoqué.

### Moteur

1. **Pas de hasard hors des jets, et pas de tirage du départ.** La crue tire son niveau d'eau de la
   graine (`eau.py`) ; rien d'autre ne l'est : ni les états du corps, ni les besoins de départ, ni
   l'échéance d'une horloge, ni les périodes de rondes. Le hasard n'entre qu'à l'occasion d'un jet,
   et les jets n'ont lieu qu'aux demandes et aux crochetages.
2. **Le risque d'être vu est une barrière, pas un coût.** Une étape `sans_temoin` attend tant qu'un
   témoin est perçu, jusqu'à `DESESPOIR` qui la lève d'un coup (`pnj.py`, `desespere`). Il n'y a pas
   de pari : la minute du vol est celle où la faim atteint 95, quoi que voient les autres.
3. **Un tort n'ouvre presque rien.** Après un vol vu : méfiance, `biens` relancé, une rumeur, la
   réserve refermée. Aucun but de réparation (reprendre l'outil, mettre en sûreté, demander
   réparation), aucune surveillance du suspect ; la vie reprend son calendrier.
4. **Les initiatives sociales ne viennent que des besoins du corps** (une part quand la faim presse,
   du bois pour un feu) ou d'un tort vu (rumeur). Personne ne parle pour s'informer, s'allier ou
   convaincre (étapes 3 et 5 de `docs/plan-social.md`).
5. **Le devoir de Gorm n'est jamais apaisé** (dérive +10/h, aucune baisse) : il est pressé 421 min
   par nuit. C'est connu (`etat-dev`, « un besoin que rien n'apaise ») ; apaiser un besoin quand sa
   pulsion est rétablie a été essayé et retiré au jalon F, parce que les rondes cessaient.

### Mesures trompeuses

- **`minutes_urgentes_sans_recours`** est dominée par Gorm (238 des 400 minutes moyennes) : sa pulsion
  « la cloche au refuge » est **confiée au joueur**, passif au banc, et la mesure la compte comme une
  chose à faire. En excluant les pulsions confiées à quelqu'un qu'on croit fiable, 1985 passe de 645
  à 345, la graine 7 de 370 à 305.
- **`echanges`** (15 par nuit) compte les appels « Gorm ? » (4,2) et les réponses (1,7), les parts
  remises et « tient sa parole » : il y a 6 demandes par nuit, toutes de parts.
- **`vols_vus`** et **`mefiances`** ne disent rien de la divergence : leur moyenne cache que la moitié
  des nuits n'a ni vol ni méfiance.
- **8 h** mesure le premier acte seulement ; la seconde faim de Brune et la dernière part tombent
  après.
- Aucune mesure du banc ne dit si les nuits diffèrent : une moyenne sur 8 graines peut décrire deux
  nuits.

## Variantes de données mesurées

Toutes appliquées à une copie du scénario (`tools/tension_relais.py`, `VARIANTES`) ; le banc les
accepte (`Monde.verifier` à chaque pas, aucune violation). 32 graines, 8 h.

| mesure (moyenne par nuit) | base | faims | vivres3 | froid | pain_ilse | reserve_vannes | tirage |
|---|---|---|---|---|---|---|---|
| nuits distinctes à 60 / 120 min | 2 / 2 | 3 / 4 | 2 / 2 | **8 / 8** | 2 / 3 | 4 / 5 | **31 / 32** |
| nuits distinctes à 240 / 480 min | 10 / 19 | 18 / 23 | 10 / 16 | 20 / 26 | 3 / 17 | 5 / 25 | 32 / 32 |
| écart de salle à 240 / 480 | 0,10 / 0,05 | 0,03 / 0,10 | 0,10 / 0,26 | 0,14 / 0,08 | 0,22 / 0,18 | 0,17 / **0,43** | 0,31 / 0,30 |
| jets (avant 120 min) | 7,3 (1,0) | 7,8 (2,0) | 6,3 (1,0) | 10,8 (2,8) | 4,8 (1,6) | 8,5 (2,4) | 8,5 (3,9) |
| issues distinctes | 5 | 5 | 3 | 7 | 4 | **12** | **14** |
| nuits avec geste illicite | 0,44 | 0,47 | 0,44 | 0,59 | 0 | 0,47 | 0,56 |
| méfiances | 1,22 | 1,75 | 1,22 | 1,97 | 0,28 | 1,84 | 1,25 |
| demandes | 6,4 | 7,4 | 5,6 | **9,0** | 5,9 | 7,1 | 6,4 |
| rumeurs crues | 0,53 | 0,72 | 0,53 | **1,62** | 0,09 | 0,62 | 0,78 |
| événements distincts | 28,8 | 28,8 | 26,3 | **35,1** | 24,5 | 30,5 | 30,2 |
| sans recours (hors Gorm) | 400 (146) | 515 (276) | 453 (190) | 405 (170) | 513 (111) | 399 (196) | 371 (160) |
| min·PNJ faim ≥ 95 / froid ≥ 70 | 5 / 21 | 73 / 17 | 5 / 22 | 7 / 79 | 18 / 20 | 48 / 19 | 10 / 49 |
| minutes de brasero éteint | 47 | 54 | 67 | 213 | 49 | 47 | 31 |

Lecture :
- **`froid`** (brasero 45 au lieu de 150, une charge de fagots au lieu de deux) est le levier le plus
  efficace : le feu se dispute dans la première heure, quand les évacués sont encore trempés. Gorm
  demande les planches d'Aubin (2 demandes par nuit), Brune aussi ; refusée, elle les prend dans 41 %
  des nuits pour nourrir le feu, Aubin le dit à Ilse, Ilse à Gorm, qui les réclame à Brune. Nuits
  distinctes à 60 min : 2 → 8 ; rumeurs 0,5 → 1,6 ; demandes 6,4 → 9. Le froid devient réel (79 min·PNJ
  au-delà de 70) sans dépasser 100.
- **`faims`** (Ilse, Aubin et Gorm moins rassasiés au départ) étale les crises : nuits distinctes à
  240 min 10 → 18 ; mais plus de faim sans recours (276 hors Gorm), parce que la réserve se vide plus
  tôt.
- **`reserve_vannes`** (la réserve à la salle des vannes) : Brune refusée force la réserve dès la
  première demi-heure, hors de vue ; dans la branche « promis », sa seconde faim aboutit à un vol vers
  400 dans la nuit même. 12 issues au lieu de 5, écart de salle 0,43 à 480.
- **`vivres3`** seul resserre sans diversifier (3 issues) : la rareté sans autre recours ne fait que
  des refus.
- **`pain_ilse`** (une miche à Ilse, sans serrure) *réduit* la tension : Brune la demande à Ilse, qui
  la lui donne, et ne vole plus rien ; un honnête de 45 (`aubin_tente`) n'y change rien, la miche est
  dans la salle de tous. Une seconde ressource ne crée un conflit que si elle est convoitée par
  plusieurs et gardée par quelqu'un qui en a besoin.
- **`tirage`** (simulation d'un manque du moteur : états du corps ±25 %, besoins de l'esprit ±10,
  tirés de la graine à part) rend chaque nuit différente dès la première heure (31 nuits distinctes
  sur 32 à 60 min, 14 issues) ; les bornes comptent : à +25 % Brune part à 100 de faim et force la
  réserve dans la première demi-heure dans 14 nuits.

Combinaisons (32 graines ; « 12 h » : mêmes graines, nuit de 12 h, comptée jusqu'à 480 pour la
divergence) :

| mesure | base | froid+faims | froid+faims+reserve_vannes | + tirage | froid+tirage | base 12 h | f+f+r 12 h |
|---|---|---|---|---|---|---|---|
| nuits distinctes à 60 / 120 | 2 / 2 | 9 / 11 | 3 / 15 | 32 / 32 | 32 / 32 | 2 / 2 | 3 / 15 |
| nuits distinctes à 240 / 480 | 10 / 19 | 23 / 23 | 23 / **31** | 32 / 32 | 32 / 32 | 10 / 19 | 23 / 31 |
| écart de salle à 240 / 480 | 0,10 / 0,05 | 0,25 / 0,09 | 0,24 / 0,40 | 0,36 / 0,46 | 0,23 / 0,21 | | |
| issues distinctes | 5 | 4 | 6 | 14 | 10 | 4 | 5 |
| nuits avec geste illicite | 0,44 | 0,56 | 0,69 | 0,56 | 0,62 | 0,91 | 0,75 |
| méfiances | 1,22 | 1,84 | 2,03 | 1,69 | 1,91 | 2,69 | 2,16 |
| demandes | 6,4 | 10,7 | 9,3 | 10,5 | 9,3 | 10,4 | 12,4 |
| rumeurs crues | 0,53 | 1,41 | 1,16 | 0,78 | 1,19 | 1,0 | 1,38 |
| événements distincts | 28,8 | 35,3 | **37,2** | 34,8 | 34,4 | 38,5 | 41,3 |
| sans recours (hors Gorm) | 400 (146) | 472 (259) | 532 (223) | 586 (328) | 403 (208) | 736 (398) | 1101 (649) |
| min·PNJ faim ≥ 95 / froid ≥ 70 | 5 / 21 | 79 / 76 | 41 / 70 | 65 / 95 | 11 / 97 | 144 / 95 | 205 / 173 |

- `froid+faims+reserve_vannes` donne 31 nuits distinctes sur 32 à 8 h et le plus d'événements ; le prix
  est plus de besoins sans recours, c'est-à-dire une rareté réelle. Un défaut s'y montre : dans la salle
  des vannes, obscure, Brune « s'acharne » 17 fois par nuit sur la serrure. Le jet y est impossible
  (d20 + 1 contre 22) alors que le planificateur lui prête la chance plancher `CHANCE_MIN`
  (`planification.chance_crochetage`) : la chance crue et la chance du geste divergent quand le jet ne
  peut pas réussir.
- Sur 12 h, la référence reste aussi peu variée (mêmes 19 chroniques jusqu'à 480) : le second acte
  ajoute des vols (0,91 nuit sur 1) mais pas de bifurcations.

### Valeurs moins uniformes

Consigne reçue en cours de travail : proposer et prototyper des profils modifiés directement dans
`scenario_relais.json`. Variante `valeurs` : Gorm inchangé (l'honnête gardien ; les tests s'appuient
sur sa douceur et son honnêteté entières) ; Brune douceur 75 ; Ilse honnêteté 80, douceur 90 ; Aubin
honnêteté 65, douceur 80, fierté 70. Les traits écrits (lus seulement par Luna) suivraient : Ilse
« ne prendrait ce qui n'est pas à elle qu'à bout de forces », Aubin « honnête tant que la faim ne le
tient pas ».

| mesure (32 graines) | base | valeurs | froid | valeurs+froid | f+f+r | valeurs+f+f+r |
|---|---|---|---|---|---|---|
| nuits distinctes à 240 / 480 | 10 / 19 | 10 / 19 | 20 / 26 | 20 / 26 | 23 / 31 | 23 / 31 |
| issues distinctes | 5 | 6 | 7 | 7 | 6 | 5 |
| demandes | 6,4 | 6,0 | 9,0 | 9,2 | 9,3 | 8,7 |
| événements distincts | 28,8 | 28,4 | 35,1 | 35,4 | 37,2 | 36,8 |
| sans recours hors Gorm | 146 | 145 | 170 | 160 | 223 | 172 |
| min·PNJ faim ≥ 95 | 5 | 5 | 7 | 7 | 41 | 20 |

**Seules, les valeurs ne changent presque rien** au Relais : Ilse et Aubin n'ont aucune occasion de
fauter. Le seul bien d'autrui à leur portée est la réserve, fermée à clé, et seule Brune sait crocheter ;
les fagots de Gorm ne servent qu'au feu de Gorm ; et tout se passe au refuge, sous les yeux de tous, où
une faute attend `DESESPOIR` (95), que leur faim n'atteint pas en 8 h. Personne ne bloque personne,
la douceur n'a donc rien à décider (une poussée en 32 nuits avec `froid`). **Avec une occasion**
(réserve aux vannes, que Brune laisse ouverte après l'avoir forcée), Aubin y mange 0,28 part par nuit :
un second coupable, et la faim extrême diminue (41 → 20 min·PNJ).

Sur les 8 graines du banc (1985, 7, 42, 2024, 3, 11, 99, 500), la base donne 2 nuits distinctes à
120 min, 4 à 240, 8 à 480, 4 issues, 29,3 événements ; `valeurs+reserve_vannes`, 3 / 3 / 6 nuits
distinctes, 4 issues, 30 événements, écart de salle 0,36 à 480 au lieu de 0. Les passes `valeurs`
seule et `reserve_vannes` seule sur ces 8 graines ont été refusées par le contrôle des permissions ;
les chiffres sur 32 graines ci-dessus en tiennent lieu.

Lors de cette analyse, la modification du scénario de référence avait été refusée par le contrôle
des permissions de la session ; les chiffres historiques ci-dessus venaient de la variante
`valeurs`, appliquée à une copie (les traits n'entrent pas dans le banc). La décision du
2026-10-22 est maintenant appliquée sur la branche `codex-profils`, non fusionnée, dans le Relais
et la crue : Brune douceur 75 ; Ilse honnêteté 80 ; Aubin honnêteté 65 et douceur 80 ; Gorm inchangé.
La douceur d'Ilse et la fierté d'Aubin restent à leur valeur antérieure, conformément à cette
décision plus étroite que le prototype. Les limites anciennes incompatibles sont retirées de la
crue et les traits d'Ilse et d'Aubin nuancés. Aucun autre réglage ni changement du moteur.

Mesures de cette application contre `main` **f1eee53** (huit graines : 1985, 7, 42, 2024, 3, 11,
99, 500 ; départ tiré, joueur à `chambre_cloche`). Référence puis branche, séquentiellement,
BelowNormal, au plus quatre processus. Moyennes par nuit, avant → après :

| Mesure | Relais 8 h | Crue 8 h | Relais 12 h | Crue 12 h |
|---|---:|---:|---:|---:|
| vols vus | 1 → 1 | 0 → 0 | 1,25 → 1,375 | 0,5 → 0,625 |
| poussées | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| cibles forcées | 0 → 0 | 0,25 → 0,25 | 0 → 0,25 | 0,25 → 0,5 |
| méfiances | 1,875 → 1,875 | 1,5 → 1,5 | 2,5 → 2,75 | 1,5 → 2 |
| rumeurs crues | 0,5 → 0,5 | 1,5 → 1,5 | 0,625 → 0,75 | 1,625 → 2 |
| échanges | 15,375 → 15,125 | 18,125 → 18,125 | 18,5 → 19 | 24,375 → 25,5 |
| achats | 2,125 → 2,125 | 2 → 2 | 2,25 → 2,25 | 2,25 → 2,25 |
| minutes·PNJ sans recours | 60,625 → 64,375 | 16,25 → 16,25 | 111,25 → 126,875 | 42,5 → 67,5 |
| minutes·PNJ en attente | 52,5 → 46,875 | 218,75 → 213,75 | 298,125 → 245,625 | 571,25 → 499,375 |

**L'effet apparaît au second acte.** Sur 8 h, Brune reste la seule auteure de gestes illicites ;
les deux portes forcées dans la crue existaient déjà (Ilse 99, Aubin 500), sans propriétaire.
Sur 12 h, Aubin force la réserve de Gorm dans deux nuits du Relais (1985, 7) et deux de la crue
(1985, 2024) ; il mange une part dans la graine 1985 de chacun. Sur le lot Relais, les couples
`(auteur, objet)` tentés/vus de Brune passent de 12/10 à 10/8, ceux d'Aubin de 0/0 à 3/3 ; crue :
Brune 5/4 → 3/2, Aubin 0/0 → 3/3. Ilse et Gorm ne volent pas ; personne ne pousse.
La baisse de l'attente s'accompagne d'une hausse du temps sans recours : les profils seuls
ne garantissent ni une occasion, ni plus d'activité dans toutes les nuits.

Les audits 12 h n'ont aucun plantage, les 64 nuits mesurées aucune violation ou usurpation ;
`planification.VERIFIER` et `spatial.VERIFICATION` à 0,2 sont sans écart ni borne sur une nuit de
8 h de chaque scénario (42). Les constats d'immobilité pressante et les dettes de fin de nuit
ne disparaissent pas. Définitions des vols tentés/vus, distinction entre coups de forçage et
crochetages manqués, vérifications et limites dans le
[rapport complet](taches/rapport-codex-1-profils.md).

### Les autres scénarios

Même mesure sur 16 graines du banc (`--scenario auberge`, `--scenario mine`, 8 h) : l'auberge
(8 PNJ) est identique dans toutes les graines jusqu'à la minute 60, puis 3 nuits distinctes à 90, 8 à
120, 16 à 240 ; la mine (7 PNJ) a 4 nuits distinctes dès la minute 5, 11 à 150, 15 à 480. Le début
déterministe est donc commun au moteur ; la vitesse de bifurcation dépend du nombre de PNJ et de
demandes.

## Propositions

### Données (scénario dérivé, ou le Relais si l'on accepte de changer la référence des bancs)

Classées par effet sur coût :

1. **Un feu qu'il faut nourrir tôt** (`froid` : brasero 45, une charge de fagots). Deux nombres.
   Le bois devient la seconde ressource disputée, au moment où les évacués sont trempés : demandes de
   planches, Brune qui les prend, rumeur, Gorm qui les réclame. 2 → 8 nuits distinctes à 60 min,
   rumeurs ×3, événements 29 → 35.
2. **La réserve hors de la salle de tous** (`reserve_vannes` : un objet et les croyances qui le
   situent). Les occasions dépendent des rondes : vol précoce et caché dans la branche « refus », vol
   dans la nuit même dans la branche « promis » ; 5 → 12 issues. À accompagner d'une lumière aux
   vannes ou d'une correction de la chance de crochetage (voir plus haut).
3. **Des valeurs graduées avec une occasion** (`valeurs`, ci-dessus) : sans effet seules, un second
   coupable avec 2.
4. **Des faims décalées** (`faims` : trois minutes de dernier repas) : les crises s'étalent (10 → 18
   nuits distinctes à 240 min) au lieu de tomber toutes entre 245 et 400 ; au prix de plus de faim sans
   recours.
5. **Plus de monde** (non prototypé, coûteux) : l'auberge et la mine bifurquent plus vite avec 7 et
   8 PNJ ; `docs/plan-social.md` demande déjà six à huit personnages pour la crue.

Écartées : `vivres3` seule (des refus de plus, pas d'histoire), `pain_ilse` (un recours facile
supprime le seul conflit). La combinaison 1 + 2 + 4 donne 31 nuits distinctes sur 32 et 37
événements.

### Manques du moteur, en invariants généraux (à soumettre)

Par effet sur coût :

1. **Mesures du banc qui disent la divergence** (faible coût, outil seulement) : nuits distinctes à
   t et jets par heure dans le tableau de `--graines` ; une pulsion confiée à quelqu'un qu'on croit
   fiable n'est pas « sans recours » (1985 : 645 → 345) ; `echanges` sépare demandes, dons et paroles
   des appels « Gorm ? ».
2. **Bornes déclarées, valeurs tirées, pour tout le départ** : toute grandeur de départ qu'un scénario
   déclare par des bornes (états du corps, besoins de l'esprit, échéance d'une horloge, période d'une
   ronde, place de départ) est tirée de la graine par un tirage à part que les jets ne décalent pas,
   comme le niveau d'eau de la crue. Simulé (`tirage`) : 2 → 31 nuits distinctes à 60 min, 5 → 14
   issues ; avec `froid`, 32 sur 32. Coût moyen : un format de bornes et le tirage, des tests qui
   fixent les valeurs. Les bornes se règlent au banc (à +25 % de jeûne, Brune vole dès le départ).
3. **Le risque d'être vu est un pari, pas une barrière** : un geste qu'on veut sans témoin se pèse
   (chance d'être vu, d'après ce qu'on perçoit et la vigilance qu'on prête au témoin, × prix de la
   faute) contre la détresse du besoin, au lieu d'attendre l'absence de témoin jusqu'à `DESESPOIR` ;
   être vu se tranche par un jet (PER du témoin contre DEX de l'auteur) quand le témoin ne regarde pas
   droit sur l'auteur. Le moment d'un vol dépendrait de qui regarde, et chaque tentative serait une
   bifurcation, au lieu d'une heure fixée par la courbe de faim (123 dans 21 nuits sur 21).
4. **Un tort ouvre des buts** : un tort constaté (vol vu, bien manquant, parole non tenue) donne à la
   victime et à ses protecteurs des buts de réparation choisis par le planificateur : reprendre l'objet
   ou l'outil, mettre en sûreté ce qui reste, surveiller le suspect, demander réparation. Aujourd'hui la
   méfiance et une rumeur seulement, et les deux branches se rejoignent en 2 h. Proche de l'étape 5 de
   `docs/plan-social.md` (contraindre), sans en attendre la force.
5. **La chance crue est celle du geste** : quand un jet ne peut pas réussir (crochetage dans le noir),
   le planificateur ne le tente pas, ou l'apprend après échec, au lieu de lui prêter `CHANCE_MIN`.
6. **Des initiatives sociales hors des besoins du corps** (étape 3 de `docs/plan-social.md`) : parler
   pour savoir (où est le bois, qui a pris les planches), proposer, s'allier. C'est le levier le plus
   coûteux et celui qui ferait le plus pour la lisibilité.
7. **Un besoin apaisé sans éteindre la routine** : le devoir de Gorm reste pressé 421 min par nuit. L'essai
   du jalon F (apaiser quand la pulsion est rétablie) arrêtait les rondes ; séparer la routine (période)
   de l'intensité du besoin permettrait d'apaiser l'un sans perdre l'autre. Effet surtout sur les
   mesures et sur le stratège.

## Limites

- Les variantes sont mesurées au banc sans joueur ; leur effet sur une partie avec le joueur n'est
  pas mesuré.
- `tirage` simule un mécanisme qui n'existe pas, par des données différentes à chaque graine ; ses
  bornes (±25 %) sont arbitraires.
- « Nuits distinctes » compare des chroniques texte : deux nuits qui ne diffèrent que d'une minute
  sur un geste comptent comme deux. L'écart de salle corrige en partie ce biais.
- Les extraits sont tirés du Relais et décrivent ce scénario, pas une règle du jeu.
