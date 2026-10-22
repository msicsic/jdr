# Revérification après les fusions de la nuit (2026-10-22)

Contrôle seul : le moteur n'est pas modifié. Branche `reverification`, partie de `main` ec2352e, qui a
reçu depuis l'[audit des nuits](audit-nuits.md) et le [banc Luna du soir](banc-luna-soir.md) :
`refus-retenus`, `ouie-temoins`, `parole-corrections`, `verifier-eau`, `deliberation-evenements` (et
`voix-suite`, fusionnée juste avant l'audit, déjà comprise dans sa référence). Elles avaient été
vérifiées seules ou par deux ; ici ensemble, sur des nuits de 12 h et avec Luna. Les causes citées sont
probables, lues dans la chronique, le code et des traces des choix ; rien n'est corrigé.

## Ce qui a été joué

| Lot | Code | Nuits | Contrôles |
|---|---|---|---|
| A | `main` ec2352e | 16 : 4 scénarios × graines 7 11 99 314 | `planification.VERIFIER` continu (écart noté, la nuit continue), `spatial.VERIFICATION` 0,2, `Monde.verifier` à chaque pas, rejeu |
| B | `main` ec2352e | 48 : 4 × 1985 42 2024 3 500 1 2 5 13 21 77 123 | `Monde.verifier` ; `VERIFICATION` 0,2 sur les six premières graines |
| R | `main` 0489fea (avant les fusions) | 48 : mêmes graines que B | `Monde.verifier` (référence) |

12 h, départ tiré, joueur passif comme dans l'audit (relais et crue `chambre_cloche`, mine `galerie`,
auberge `dortoir`), au plus 6 processus de calcul, priorité réduite. 112 nuits ; les 64 nuits de `main`
couvrent les 16 graines de l'audit (lots A et B). Outil : `tools/audit_nuits.py` (inchangé) ; balayages
complémentaires (boucles à la seconde, surenchères, dettes immédiates) écrits à part pour ce rapport.
Données dans `artifacts/rv-verifier`, `rv-libre`, `rv-avant` (non versionnés).

Reproduire :

    python tools/audit_nuits.py jouer --graines 7 11 99 314 --heures 12 --dossier artifacts/rv-verifier \
        --processus 3 --verifier-continu --verification 0.2 --rejeu
    python tools/audit_nuits.py analyser --dossier artifacts/rv-verifier

## Contrôles

- **Aucun plantage** sur 112 nuits, **aucune violation de `Monde.verifier`** (chaque pas de 5 min),
  **aucun écart de `spatial.VERIFICATION`** (40 nuits à 0,2), **aucune usurpation**.
- **`planification.VERIFIER` : 0 écart** sur les 16 nuits du lot A (avant `verifier-eau` : mine 15/16 et
  auberge 11/16 en défaut). Recherches jouées arrêtées à leur borne, reconnues et notées
  (`planification.BORNES`) : 697, dans deux nuits seulement. Ce sont des manques en jeu, pas des écarts
  du contrôle : à l'auberge 11, Lucien cherche de la lumière 686 fois (minute 457 et suivantes) sans rien
  trouver dans sa borne de 4 000 nœuds (`trouve: null`) alors que la recherche complète a un plan de coût
  93 ; il reste dans le noir et la nuit coûte 2 868 s avec le contrôle. À la mine 99, Josse ne trouve
  rien pour son poêle (10 fois, optimum 23). `verifier-eau` en reconnaissait 161 sur 32 nuits ; la
  limite reste (une recherche neuve bornée à `NOEUDS`).
- Temps d'une nuit de 12 h avec `VERIFIER` continu (3 processus, d'autres calculs sur la machine) :
  relais 85–121 s, crue 44–68 s, auberge 575–2 868 s, mine 647–1 674 s.

## Chiffres, avant → après (lot R → lot B, 12 graines × 12 h, moyenne par nuit)

| Mesure | Relais | Crue | Mine | Auberge |
|---|---|---|---|---|
| minutes urgentes sans recours | 105 → 89 | 24 → 58 | 48 → 49 | 49 → 113 |
| minutes urgentes en attente | 236 → 339 | 550 → 983 | 1 237 → 1 328 | 1 040 → 1 152 |
| échanges | 28 → 19 | 40 → 28 | 165 → 63 | 245 → 107 |
| appels à l'aide | 0,7 → 0,2 | 8,5 → 0,2 | 39,6 → 4,8 | 23,5 → 4,0 |
| allés voir | 22 → 20 | 23 → 22 | 106 → 49 | 140 → 94 |
| vols vus | 1,2 → 1,1 | 0,4 → 0,7 | 0,1 → 0,5 | 0,1 → 0,9 |
| offres de tâche | 5,3 → 3,2 | 4,2 → 6,3 | 14,8 → 5,8 | 81 → 33 |
| tâches acceptées / faites | 0,5/0 → 0,1/0,1 | 0,8/0,2 → 0,7/0,6 | 0,2/0 → 0/0 | 1,1/0,8 → 1,6/0,9 |
| refus de rembourser | 0,3 → 0 | 0 → 0,4 | 0 → 0 | 0 → 0,6 |
| minutes dans le noir | 197 → 195 | 263 → 199 | 1 063 → 1 252 | 2 700 → 2 745 |
| minutes dans l'eau | – | 640 → 490 | – | – |
| renoncements | 1,8 → 1,5 | 0,4 → 1,0 | 0,1 → 2,7 | 0 → 1,7 |

Lecture : les échanges baissent de moitié à la mine et à l'auberge parce que les refus qui tiennent ne
sont plus redemandés (`refus-retenus`) ; l'attente monte à la crue (le froid, plus de feu hors de l'eau,
déjà noté par `verifier-eau`) ; « sans recours » double à l'auberge (Lucien qui guette et renonce, déjà
noté par `ouie-temoins` et `deliberation-evenements`). Aucun de ces écarts n'est un plantage ; les trois
boucles nouvelles ci-dessous expliquent une partie des gestes (crue 299 → 533 par nuit, dont 1 700
passages de porte dans la seule crue 3).

## Défauts nouveaux, du plus grave au moins grave

### N1. Ouvrir, fermer, rouvrir toutes les deux secondes (mine 42, 690 fois en 23 minutes)

`python -m donjon.banc_pnj --scenario mine --joueur galerie --graine 42 --heures 4 --chronique`,
minutes 215 à 238 : « Odon ouvre le garde-manger de la cuisinière » / « Mathe ferme le garde-manger »,
689 fois chacun, toutes les 2 s ; puis de 239 à 266 Odon crochète, Mathe reverrouille, Odon recrochète
(huit fois) ; Mathe appelle à l'aide toutes les deux minutes (12 fois). Le baraquement est éclairé, ils se
voient. Trace des choix (`deliberation.choisir`) : Odon, affamé (96), a pour plan `ouvrir garde_manger`
puis `manger vivres` (condition `sans_temoin`) ; Mathe, dont la pulsion « garde-manger verrouillé » est
rompue, a pour plan `fermer` puis `verrouiller`. Elle ferme (0,5 s) ; la porte qui change sous ses yeux
réveille Odon, qui choisit aussitôt de rouvrir ; le verrouillage de Mathe échoue sur un garde-manger
ouvert, elle choisit aussitôt de refermer. Avant `deliberation-evenements`, chacun ne rechoisissait qu'à
la minute ; aucune nuit du lot R n'a de rafale de ce genre.

Causes : (1) la condition `sans_temoin` ne porte que sur l'étape illicite (`manger`) : le premier geste
d'un plan qui ne vaut que sans témoin (ouvrir le bien d'autrui) s'exécute sous les yeux de la gardienne ;
(2) voir son propre geste défait par quelqu'un est un événement qui fait refaire le même geste à
l'instant, sans rien retenir de l'opposition. Invariant : un plan conditionné à l'absence de témoin ne
commence pas devant un témoin ; un geste défait sous ses yeux par autrui vaut un refus qui tient tant que
rien ne change (comme une demande refusée, `deliberation.retenir_refus`), et ne se retente pas à
l'instant.

**Traité** (branche `boucles-pnj`, `docs/plan-planificateur.md`, « Les boucles de la revérification ») :
la cause (1) ne tenait pas — `sans_temoin` porte aussi sur ouvrir ; c'est la faim d'Odon passée à
`DESESPOIR` qui levait la précaution. Règle : ce qu'un PNJ vient de faire de sa main à une chose, un
autre le défait sous ses yeux : on s'oppose à lui sur cette chose, il n'y touche plus tant qu'il croit
l'opposant là (`deliberation.changer_etat`). Audit 12 h, 8 graines : bascules à la mine 180,6 → 2,1 par
nuit (mine 42 : 1 436 → 8) ; la même boucle à l'auberge (Lucien et le coffre d'Anselme) 15,5 → 2,5.

### N2. Aller-retour lumière ↔ abri à chaque seconde (crue 3, 1 700 passages par nuit)

`python -m donjon.banc_pnj --scenario crue --graine 3 --heures 8 --chronique`, à partir de la minute 322
(Ilse) et 378 (Brune) : « passe dans : Galerie de ronde » / « passe dans : Palier des vannes », Ilse 946
fois, Brune 747, jusqu'à 552 changements de salle dans une heure (avant : 64 au plus, toutes nuits
confondues). Trace des choix de Brune (minute 385) : au Palier des vannes, noir et 15 cm d'eau, sécurité
qui presse, but `lumiere`, plan « aller Galerie de ronde » ; arrivée sur la case [0, 10] de la Galerie,
éclairée (la lanterne du joueur passif), la lumière est atteinte, but `abri` au Refuge du relais, plan
« aller antichambre » ; un pas plus loin, de nouveau dans le noir du Palier, but `lumiere`… un choix par
seconde, chaque entrée de salle et le passage de l'autre réveillant chacun.

Causes : deux recours du même besoin (sécurité) se défont l'un l'autre. La lumière est jugée sur ce qui
éclaire sa case, y compris la lanterne d'un autre ; l'abri est un lieu éclairé par ses propres sources
(`esprits.constater_lumiere`, `propre`) ; le plan d'abri traverse le noir, qui relance la lumière.
L'inertie de `besoins` (`INERTIE`) ne joue qu'entre besoins différents ; la délibération à l'événement
rend la bascule immédiate. Invariant : un recours ne se choisit pas s'il défait aussitôt celui qu'on
vient d'atteindre pour le même besoin ; un passage dans le noir prévu par le plan en cours n'en change pas
le but.

**Traité** (branche `boucles-pnj`, même section) : la galerie est éclairée par le jour, pas par la
lanterne du joueur (éteinte). Les deux moitiés de la boucle : l'abri auprès de Gorm passait par le palier,
où l'eau attendue faisait de la galerie (le plus haut lieu) l'abri ; la lumière, dans le noir du palier,
renvoyait aussi à la galerie. Règles : le recours en cours garde la main sur les autres recours du même
besoin tant que sa méthode le rend encore (`choisir`) ; l'abri vers lequel il est en route garde la main
tant qu'il en est un, sauf eau qui monte sous ses yeux ou péril (`_plan_abri`). Crue 3 sur `main`
ec2352e : 1 705 → 136 passages en 8 h ; cas réel rejoué en scène (`tests/test_boucles_pnj.py`).

### N3. Surenchère sans borne et dette immédiate d'une tâche acceptée (auberge, 9 nuits sur 12)

`python -m donjon.banc_pnj --scenario auberge --joueur dortoir --graine 42 --heures 6 --chronique` :
Odile offre à Tilo d'allumer l'âtre pour 2, 4, 8, 16, 32 pièces (« cher »), entre les minutes 324 et 326,
puis 64 à la minute 342 (« accepte ») ; 47 s plus tard « Tilo doit désormais 64 pièces à Odile : le
travail payé n'a pas été fait », et Tilo refuse de rendre (minutes 344 et 616). Même nuit : Anselme
offre 3, 6, 12, 24 à Odile (acceptée, dette 9 s après), 6 à Joss (dette à l'instant même de
l'acceptation). Offres de 16 pièces ou plus : 0 nuit sur 12 avant, 13 nuits d'auberge sur 16 après (lots A et B) ;
dettes nées moins d'une minute après l'acceptation : 15 en 64 nuits (dont 6 dans la seule auberge 11 :
Anselme paie 24 pièces à Tilo, Odile, Hugues, Mireille pour remettre son ballot, chacun accepte et doit
aussitôt) ; 48 ou 64 pièces jamais rendues par Tilo dans cinq nuits.

Causes : (1) la surenchère (`planification._engager`, `SURENCHERE`, branche `refus-retenus`) double le
dernier prix refusé sans autre borne que la bourse ; le coût de la dépense (`Vue.depense`) pèse peu pour
qui est riche, et la délibération à l'événement enchaîne les offres dans la même minute ; (2) on accepte
une tâche sur `planification.devis_pulsion` (avec les moyens du payeur, l'engagement déjà compté), mais
`echanges.empeche` la juge ensuite par `deliberation._plan_pulsion`, sans les mêmes entrées : la tâche
acceptée se découvre aussitôt infaisable et devient une dette. Invariant : une tâche n'est acceptée que
si le même jugement qui la rendrait aussitôt la tient faisable ; une offre ne dépasse pas ce que le
résultat vaut au payeur.

### N4. Prévenir de nouveau de ce que la victime sait (auberge, 3 nuits sur 12, jusqu'à 26 fois)

Auberge 3, minutes 487 à 500 : « Hugues dit à Anselme que le ballot de soie est dans la chambre au
poêle », 26 fois (auberge 500 : 15, auberge 123 : 10), alors qu'Anselme l'y a posé lui-même. La boucle B3
de l'audit (« Lucien est peu fiable » répété) est corrigée ; celle-ci est sa variante de lieu. Cause :
`deliberation._a_dire` ne tient pour dit un lieu que s'il l'a été depuis la minute de la croyance de lieu
de Hugues, et cette minute se renouvelle chaque fois qu'il revoit le ballot : dans la même salle que lui,
chaque minute. Invariant : on redit un lieu seulement s'il a changé depuis qu'on l'a dit (la valeur, pas
la date du dernier regard) ; on ne l'apprend pas à qui l'a déplacé lui-même sous ses yeux.

**Traité** (branche `boucles-pnj`, `docs/plan-ouie.md`, « Ce qu'on a déjà dit ») : un lieu dit l'est
jusqu'à ce que sa valeur change (le souvenir `dit` porte la valeur) ; on n'apprend pas à la victime où est
un bien qu'on croit dans sa salle. Audit 12 h, auberge : avertissements redits 4,4 (pire 21) → 0,75 (pire 2).

### N5. Luna (moyens et faibles)

- **Un PNJ vu nomme Corvus sans connaître son nom** (1 fois sur 2, `ressources`) : « Non. Je ne te dois
  rien, Corvus. » (Aubin, qui ne connaît pas ce nom : `voix.connait_nom` faux au départ). Le contrôle des
  noms connus (`narration.voix_inconnues`) ne vaut que pour une voix inconnue. Invariant : une réplique ne
  nomme que qui son locuteur connaît, qu'on le voie ou non.
- **Le joueur s'entend à la troisième personne** (2/2, `soir-appel`) : après l'achat d'une planche, au pas
  suivant, « Aubin te remet les planches de bac : tu l'avais payé. » puis « Tu entends, tout près : Aubin
  remet les planches de bac à Corvus. ». Le compte rendu de l'ouïe ne reconnaît pas le joueur comme
  destinataire du geste.
- **Silences et précautions absurdes imposés par l'auditeur** : « décris-moi l'ambiance de cette
  conduite » (1/2) — le crépitement d'un brasero allumé est refusé, Luna écrit « tu ignores si un feu
  crépite » ; « Brune, laisse-moi passer » coûte 7 appels et 38 s dans les deux passes (un repli en passe
  2, l'auditeur se contredisant dans son propre motif) ; « Ilse, tu m'entends ? » 5 appels en passe 2. Le
  défaut 6 du banc du soir reste la première source de relances.
- **« Tu demandes à passer sous la poutre… » pris pour une parole racontée** (passe 2) :
  `narration.parole_racontee` relève « tu demandes » dans une question de faisabilité, d'où une relance.
- **« Passer sous la poutre » répondu par « Il faut une échelle accessible et en état de servir. »**
  (2/2) : la question devient `franchir`, dont la seule méthode est l'échelle ; le joueur lit une raison
  qui ne répond pas à « passer dessous » (8 appels en passe 2).

## Défauts anciens

### Audit des nuits

| Défaut | Avant (lot R) | Après (lot B) | Verdict |
|---|---|---|---|
| V1 `VERIFIER` | mine 15/16, auberge 11/16 en défaut (audit) | 0 écart sur 16 nuits | corrigé |
| B1 appel à l'aide répété | ≥ 10 appels : 37 PNJ-nuits (mine 12/12) ; 39,6 par nuit à la mine | 1 (mine 42, pendant la boucle N1) ; 4,8 | corrigé, sauf sous N1 |
| B2 aller voir ↔ garder | alternances : 82 constats, 39 nuits | 23 constats ; retours voir 0,7 à 10 par nuit | corrigé en grande partie |
| B3 prévenir en boucle | « peu fiable » 5 à 7 fois, 3 nuits | 0 ; variante de lieu N4, 3 nuits | corrigé pour l'auteur, pas pour le lieu |
| B4 demandes refusées redemandées | 26 constats (offres « cher » 7 fois…) | seul Hugues (N4) | corrigé ; la surenchère N3 en est l'effet |
| B5 chercher qui se tait | Odile 23 appels | Lucien 41, Odile 32 | inchangé (conforme à la règle) |
| A1 bruit de sa salle | — | examiné ; retours voir rares | corrigé |
| A2 vol à côté, dans le noir | gestes illicites d'un présent ni vus ni entendus : 266 (12 auberges sur 12) | 19 (surtout Lucien posant le ballot dans l'étable noire) | corrigé en grande partie |
| A3 tâches payées non faites | dettes de Brune au Relais 4 nuits | Relais 0 ; mais N3 à l'auberge | corrigé au Relais, rouvert par N3 |
| A4 piégés par l'eau | ≥ 86 cm : 98 min par nuit ; 490 min à 71–91 cm (crue 500) | 10 min ; aucune série d'une heure à ≥ 50 cm | corrigé |
| A5 l'auberge dans le noir | 2 700 min | 2 745 min | inchangé (scénario) |

### Banc Luna du soir, saisies rejouées

| Saisie (banc) | Ce qu'affiche le jeu maintenant | Verdict |
|---|---|---|
| « as-tu de quoi manger, Ilse ? » (soir-appel) | « Tu dis à Ilse : « as-tu de quoi manger, Ilse ? » » ; Ilse répond (2/2) | corrigé (la réplique garde la minuscule de la saisie) |
| « « Brune, tu me dois deux pièces… » » (comptes) | Brune connue dans les deux passes : « Tu te tournes vers l'est. Tu dis à Brune… », elle refuse | non exercé (nom inconnu) |
| « je paie Aubin trois pièces pour une de ses planches » | « Aubin te remet les planches de bac : tu l'avais payé. » au pas suivant (2/2) | corrigé ; écho N5 à la 3e personne |
| « il y a quelqu'un ? », « « Qui est là ? » » (soir-noir) | « une voix féminine… te répond tout près : « Oui, je suis là. Qui parle ? » » (2/2) | corrigé |
| « est-ce que je pourrais passer sous la poutre effondrée ? » | « Il faut une échelle accessible et en état de servir. » (2/2) | refus de forme plus affiché ; réponse à côté (N5) |
| « Ilse, qu'est-ce que tu vas en faire ? » (echanges) | Ilse répond (2/2), plus de silence affirmé | corrigé |
| silences de l'auditeur (passage, absent) | « Brune, laisse-moi passer » 7 appels (2/2), 1 repli | non corrigé |
| parole à la cantonade dans le noir | soir-noir 3,3 appels par tour, 0 relance (soir : 4,7) | corrigé |
| « aucun passage praticable » | jamais vu | corrigé |
| « « C'est moi, Brune. » » | « Tu n'es pas Brune… » 4/4 (une première proposition `nom: joueur` refusée par le moteur, 2 fois) | corrigé |
| « Aubin, as-tu du bois ? » | « Oui. Les planches de bac sont là, dans le refuge. » 4/4 | corrigé |
| « je réponds » sans appel | parole à Aubin remplie par Luna : « Oui ? », « Oui, Aubin ? » (Luna invente qu'Aubin l'a appelé) | non corrigé (limite connue) |
| « est-ce que quelqu'un a du bois ? » | va au seul Aubin, réécrit « Quelqu'un a-t-il du bois ? » | non corrigé (limite connue) |
| voix d'auteur en « je » | refusée par le contrôle, corrigée (atelier) | corrigé |
| « je m'étire » | « en réalisant un geste d'effort » (2/2) | non corrigé |
| « je donne le briquet à Ilse » dans le noir | « Approche-toi d'une voix qui se dit Ilse… » (2/2) | corrigé |
| offre pour l'anneau (crypte) | pas de « Tu dis à Gorm : … » (2/2) | non corrigé |

## Banc Luna

`main` ec2352e, 2 passes, une exécution à la fois (un autre agent jouait Luna en même temps : les
secondes sont indicatives), `--fil`, neuf scripts : les quatre de référence, `comptes`, `ressources`,
`soir-appel`, `soir-noir`, `soir-voix`. Résultats : `artifacts/bancs-multi/20261022-155213-4432`.

| Banc | Tours MJ | Appels / tour | s / tour | Replis | Relances | Tours avec refus | Refus |
|---|---|---|---|---|---|---|---|
| **4 de référence** | 38 | **3,25** (3,18–3,32) | **15,1** | **0,5** | **5,5** (5–6) | **6,5** | **11** |
| relais | 11 | 3,95 | 17,3 | 0 | 2 | 3,5 | 7,5 |
| crypte | 9 | 2,67 | 12,7 | 0 | 0,5 | 1 | 1 |
| atelier | 11 | 2,91 | 12,9 | 0 | 1 | 2 | 2,5 |
| echanges | 7 | 3,43 | 18,1 | 0,5 | 2 | 0 | 0 |
| comptes | 2 | 3,00 | 11,6 | 0 | 0 | 0 | 0 |
| ressources | 3 | 3,00 | 13,1 | 0 | 0 | 0 | 0 |
| soir-appel | 6 | 3,00 | 17,6 | 0 | 1 | 0 | 0 |
| soir-noir | 5 | 3,30 | 13,8 | 0 | 0 | 1,5 | 1,5 |
| soir-voix | 4 | 3,62 | 12,2 | 0 | 1 | 0,5 | 0,5 |

Références : banc du soir 3,14 appels, 11,1 s, 0 repli, relances 4,7, tours avec refus 7,0, refus 10,3 ;
`parole-corrections` 3,24 appels, 15,0 s, 1 repli, relances 6, refus 11. Les quatre bancs de référence
restent au niveau de `parole-corrections` : la hausse depuis le soir vient de cette branche (correction à
part des refus de forme), pas des fusions suivantes. Le repli est « Brune, laisse-moi passer » (N5). Les
bancs ciblés du soir s'améliorent (soir-noir 4,70 → 3,30 appels, relances 3,5 → 0 ; soir-appel 3,67 →
3,00). Aucune erreur technique, aucun `attendu` ni identifiant affiché ; les seules coordonnées montrées
sont celles des refus « Approche-toi de … (case 21, 11 du plan) », déjà présentes avant.

## Limites de ce contrôle

- Les nuits avant et après divergent dès la première minute : la comparaison est statistique (12 graines
  par scénario), les boucles N1 et N2 n'ont chacune été vues que dans une nuit sur 16 de leur scénario,
  N3 dans 13 auberges sur 16, N4 dans 3.
- `VERIFIER` n'a tourné que sur 4 graines par scénario ; `VERIFICATION` à 0,2 sur 40 nuits.
- Le banc Luna n'a que 2 passes et tournait à côté d'un autre banc Luna et de l'audit : les secondes ne
  se comparent pas.
