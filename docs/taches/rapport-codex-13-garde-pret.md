# Rapport Codex 13 — Garde et chance de demande

Branche `codex-garde-pret`, non fusionnée. Base : `main` **a7ecb50**, tâche portée par
**6cd5c69**. Implémentation : commit signé SSH **cec331f**. Travail dans
`tmp-worktrees/codex-garde-pret`, sans modification ni fusion de `main`.

## Règles retenues

`GARDE` est remplacé par `planification.prix_gardes`, calculé une fois par vue et par lieu.
La base est **1 + valeur/50** : ambition pour ce qui est à soi ou convoité, loyauté pour un
bien d'autrui dont la garde est permise. L'ambition pondère la conservation du patrimoine ;
la loyauté pondère une responsabilité envers son propriétaire. À valeurs 50 et sans
présence suspecte, on retrouve exactement **2**. L'intervalle 1–3 garde un coût à toute
charge, sans mettre les profils extrêmes à zéro ou à l'infini.

Plusieurs biens au même lieu prennent le plus fort attachement, sans multiplier le coût
par objet. La base est multipliée par **1 + risque**, le plus fort risque parmi les personnes
qu'il croit près de ces biens : **max(0, 40−confiance)/100 + rancune/100 + peur/100**.
Les axes sont ceux du gardien envers cette personne, sa position est crue. Les trois bandes
méfiance, rancune et peur peuvent activer une garde menacée même sans urgence de biens.
La peur augmente aussi le coût propre de sa sécurité : rester n'est pas un interdit de fuir.

`PRET` est retiré. **`relations.chance_demande`** est l'unique estimation commune :

**0,5 + (confiance−40)/200 + affection/500 − rancune/250 − peur/500 + dette/1000**,
bornée à **0,1–0,9**.

Ce sont exclusivement les axes du demandeur, un a priori issu de son expérience. Une dette
ressentie après avoir reçu un service rend un échange plus plausible ; elle ne révèle pas
la dette réelle de l'autre. Durant `REDEMANDE` (120 minutes), un refus personnel retenu retire
0,15, ou 0,3 s'il s'agit de méfiance ; un don ou un engagement tenu pour cet interlocuteur
ajoute 0,1 d'espoir de réciprocité ; se savoir vu fauter par lui retire 0,3. Chaque terme est
compté une fois, sans cumul de répétitions. Les incapacités matérielles ne deviennent pas
des rejets personnels ; les refus précis gardent leur contrat et leur cause.

La chance s'applique aux objets portés, parts servies, parts livrées et tâches payées, via
`DEMANDE / chance`. L'ancienne majoration d'une tâche par les refus d'autres personnes est
retirée : l'estimation porte sur l'interlocuteur auquel il s'adresse. Un propriétaire connu
uniquement par un bien a lui aussi un a priori, même avant d'avoir été situé.

Les témoins remarqués sont conservés dans la mémoire de l'auteur, y compris quand celui-ci
ne les remarque qu'après le début du geste. Un témoin qu'il n'a pas perçu ne modifie pas son
estimation. Les cartes **`prix_gardes` et `chances_demandes` entrent dans `_entrees`** pour le
cache des résultats et des graphes. Aucune attitude privée de l'autre n'est consultée.
Aucune donnée de scénario, consigne Luna ni règle de persuasion réelle n'est changée.

## Cas vérifiés

Dix nouveaux tests dans `tests/test_garde_pret.py`, avec sauvegarde et rechargement :

- Gorm face à Brune, puis Bram face à Odon : le gardien reste près du bien menacé ; sans
  cette méfiance, il quitte le lieu. Le joueur retrouve le gardien dans le rendu rechargé.
- Attachement neutre à 2, variation par ambition, charge confiée par permission effective
  pondérée par loyauté ; plusieurs biens au même lieu comptés une fois.
- Rancune et peur renchérissent la garde ; déplacer réellement un suspect sans réviser la
  croyance ne change pas ce prix. Réviser la position crue change les entrées du cache.
- Ilse au Relais et Joss à l'auberge choisissent le donneur qui les a servis, plutôt que
  celui qui leur a refusé autre chose. L'objet est réellement remis ; après rechargement,
  le monde et la scène du joueur le montrent porté par le demandeur.
- Inverser l'attitude réelle de l'autre ne change pas l'estimation. Un service que l'auteur
  sait avoir rendu la change ; le cache suit les changements d'expérience du demandeur.
- Un témoin visible, puis un témoin initialement dans son dos et remarqué en cours de geste :
  seul le témoin remarqué est retenu, une fois, après la fin du registre des gestes.
- Incapacité matérielle distincte du rejet personnel, bornes de probabilité, propriétaire
  seulement connu par son bien.

Tests existants adaptés sans supprimer leurs contrôles d'état : `test_dynamique_besoins`
pose l'ambition neutre pour conserver son opposition entre noir et biens ;
`test_petits_correctifs` vérifie le coût à la chance calculée ; `test_entretenir` suit la
part désormais demandée à Joss, toujours servie et consommée ; `test_ouie` vérifie le lieu
appris plutôt qu'une minute strictement positive ; `test_ressources` suit la nouvelle part
d'Odile choisie par Anselme, avec conservation du bois et des trois foyers.

Suite complète finale par `tools/tests.py --processus 2` : **1 428 tests, 14 sautés**
(dépendances MiMo facultatives absentes), **0 échec, 0 erreur**, 894,9 s écoulées sur la
machine partagée. Nouvelle passe ciblée finale : dix tests de cette tâche et six tests
du comparateur, tous verts.

`planification.VERIFIER = True` et `spatial.VERIFICATION = 1` : **2 h, graine 42,
quatre scénarios**, sans écart signalé. Puis les mêmes quatre scénarios et graine sur
**8 h, VERIFIER actif, VERIFICATION à 0,2**, sans écart signalé. Aucune usurpation,
aucun plantage dans ces huit nuits de contrôle. Les contrôles conservent les bornes
existantes du planificateur ; ils ne prouvent pas l'optimalité au-delà de sa recherche
bornée. Les bancs et contrôles ont été lancés l'un après l'autre, jamais ensemble.

## Bancs comparés

`tools/comparer_bancs.py` : quatre scénarios, graines **1985, 7, 42, 2024**, départ tiré,
4 h puis 8 h. Pour chaque lot, référence `main` a7ecb50 puis branche, l'une après l'autre,
**4 processus au plus**, priorité réduite. Joueur passif : chambre de la cloche au Relais
et à la crue, galerie à la mine, dortoir à l'auberge. Moyennes par nuit, **avant → après**.
Les temps processeur aident à lire la mesure sur la machine partagée ; les nuits peuvent
diverger et la charge extérieure interdit d'en déduire un coût isolé de la seule formule.

Le comparateur observe maintenant les départs d'un lieu gardé et les minutes-lieux loin de
biens dont le PNJ a la charge, d'après ses croyances, même sans urgence. Ce sont des relevés
à la minute : une excursion entièrement entre deux relevés peut ne pas être comptée.
`demandes_objet` compte les chroniques sociales contenant « demande », hors offres de tâches ;
`refus_demande` compte les issues refus, méfiance, nécessaire, impossible et absent. Les offres
de tâches sont indiquées séparément. « Qui va là ? » n'est pas un refus ; aucun cas de ce type
dans les lots mesurés.

### 4 heures

| Mesure | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Demandes sociales | 2 → 2 | 6,75 → 7,25 | 3 → 3 | 3 → 2,75 |
| Refus de demande | 1,5 → 1,5 | 5 → 5,25 | 1,5 → 1,5 | 2,5 → 2,25 |
| Achats conclus | 1 → 0,75 | 1,5 → 1,25 | 1,5 → 1,5 | 0,25 → 0,25 |
| Tâches proposées | 0,5 → 1 | 0 → 0 | 0 → 0 | 1,5 → 1,5 |
| Tâches acceptées | 0 → 0 | 0 → 0 | 0 → 0 | 0,5 → 0,5 |
| Minutes sans recours | 45 → 45 | 6,25 → 6,25 | 20 → 20 | 60 → 60 |
| Minutes en attente | 5 → 5 | 0 → 0 | 1,25 → 1,25 | 15 → 15 |
| Départs loin des biens | 3,75 → 3 | 0 → 0 | 2,5 → 2 | 3,25 → 3,25 |
| Minutes-lieux loin des biens | 20,5 → 17,5 | 0 → 0 | 75,25 → 75,75 | 21,5 → 21,5 |
| Vols vus | 1,25 → 1,25 | 0,25 → 0,25 | 0 → 0 | 1,25 → 1,25 |
| Usurpations | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Violations / plantages | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Secondes processeur | 8,78 → 7,07 | 14,45 → 13,38 | 15,38 → 14,21 | 10,08 → 10,3 |
| Secondes écoulées | 9,48 → 7,54 | 15,54 → 13,9 | 16,36 → 15,06 | 10,66 → 11,23 |

### 8 heures

| Mesure | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Demandes sociales | 4,25 → 6 | 26 → 27 | 9,25 → 12,5 | 7 → 7 |
| Refus de demande | 2,5 → 3,5 | 11,5 → 12,25 | 4 → 5,5 | 4,75 → 4,75 |
| Achats conclus | 1,5 → 1,25 | 2 → 1,75 | 4,5 → 3,25 | 0,5 → 0,5 |
| Tâches proposées | 1,75 → 2,75 | 6 → 6,75 | 0,75 → 0,75 | 4 → 4,75 |
| Tâches acceptées | 0,25 → 0,25 | 0 → 0 | 0,25 → 0,25 | 0,5 → 0,5 |
| Minutes sans recours | 102,5 → 100 | 13,75 → 13,75 | 131,25 → 125 | 112,5 → 112,5 |
| Minutes en attente | 31,25 → 31,25 | 283,75 → 283,75 | 8,75 → 8,75 | 62,5 → 62,5 |
| Départs loin des biens | 6,5 → 4,25 | 0,75 → 0,75 | 5,75 → 5,25 | 4,25 → 5,25 |
| Minutes-lieux loin des biens | 28,5 → 22 | 5,25 → 5,25 | 172,5 → 169 | 27 → 28 |
| Vols vus | 1,25 → 1,25 | 0,5 → 0,5 | 1,25 → 1,5 | 1,5 → 1,5 |
| Usurpations | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Violations / plantages | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Secondes processeur | 20,74 → 16,58 | 49,28 → 55,23 | 46,33 → 51,52 | 29,18 → 28,96 |
| Secondes écoulées | 23,34 → 17,96 | 54,92 → 60,49 | 50,13 → 55,15 | 31,16 → 30,28 |

## Lecture des résultats et limites

À 8 h, les départs loin des biens passent de 6,5 à 4,25 au Relais et de 5,75 à 5,25 à
l'auberge ; la crue passe de 4,25 à 5,25, avec 27 → 28 minutes-lieux. Une règle qui rend
l'attachement personnel ne garantit pas une baisse uniforme des départs. Les minutes sans
recours baissent au Relais et à l'auberge, restent égales à la mine et à la crue ; les
minutes en attente restent égales dans les quatre scénarios.

Les demandes augmentent au Relais, à la mine et à l'auberge, avec davantage de refus ; les
achats baissent. Les tâches proposées augmentent au Relais, à la mine et à la crue, sans
hausse des tâches acceptées ; aucune tâche due aussitôt dans ces nuits. La chance estimée
reste imparfaite. Elle n'a pas été calibrée pour prédire le jet réel, le besoin matériel de
l'auditeur ou la valeur d'une contrepartie.

Audit à 8 h : aucun plantage, violation ou usurpation. À la graine 42 du Relais, les appels
à l'aide de Gorm passent de dix à un ; le signalement de treize alternances de buts n'est
plus levé, et le maximum de passages par heure passe de 41 à 8. Un signalement d'alternance
aller voir/autre but apparaît. À l'auberge, les signalements
passent de 9 à 10 pour « figé pressé » et de 1 à 2 pour « voir alterné » ; le nouveau cas
figé est Mireille, 225 minutes sans but, avec du devoir persistant. Les minutes sans
recours globales baissent néanmoins. Ces alertes d'audit ne sont pas présentées comme
corrigées par ce lot ; aucun signalement de demande répétée en boucle.

Le temps processeur à 8 h varie de **−20,1 %** au Relais à **+12,1 %** à la mine,
**+11,2 %** à l'auberge et **−0,8 %** à la crue. Le coût accru des deux scénarios est une
limite observée ; ces nuits différentes ne séparent pas le coût des nouvelles lectures de
celui des décisions et recherches supplémentaires.

Réglages proposés : conserver cette base neutre et ces bornes pour l'intégration ; mesurer
ensuite la calibration par interlocuteur et les signes lus en 3c, puis enrichir l'estimation
unique avec les contreparties de 3e. Une simple hausse globale de la chance pour supprimer
les refus masquerait ce qui manque. Ne pas réduire les coûts de garde pour faire disparaître
l'alerte de devoir de Mireille, qui n'est pas une garde de biens.

Restent explicitement à faire : lecture des signes et attitude réciproque en 3c ; geste
`proposer`, contreparties, réparation et intermédiaires en 3e. La garde dépend toujours des
pulsions de biens hors rondes, pas de chaque objet possédé. Les expériences récentes suivent
la fenêtre de 120 minutes et la mémoire bornée à 40 souvenirs ; elles peuvent donc être
oubliées plus tôt. Le risque se juge au lieu cru actuel des tiers, pas selon leur déplacement
hypothétique pendant le plan. Aucune ancienne sauvegarde n'est migrée.

Les traces détaillées restent locales, non versionnées, dans `artifacts/` :
`tests-final.json`, `tests-garde-pret-final.json`, `comparaison-4h-final.json`,
`comparaison-8h.json`, `verification-2h.json`, `verification-8h.json`, et leurs journaux.
La signature SSH du commit d'implémentation a été vérifiée avec la clé publique locale.
