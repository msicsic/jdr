# Rapport : trois lots en parallèle (temps réel, socle des relations, crochetage et surenchère)

Tâche `docs/taches/cloud-lots-abc.md`. Les trois branches sont poussées sur `origin` et ne sont pas fusionnées.

## Synthèse

| Lot | Branche | Base | Dernier commit | Suite (revérifiée avant de pousser) | PR brouillon |
|---|---|---|---|---|---|
| A | `temps-reel` | `main` 0551ba2 | 345ccea | 1218 tests OK, 18 sautés | #4 |
| B | `relations-socle` | `main` 0551ba2 | f95bcf9 | 1216 tests OK, 18 sautés | #3 |
| C | `crochetage-surenchere` | `main` 0551ba2, puis fusion de `main` d5d4bee | 39f8596 | 1221 tests OK, 18 sautés | #5 |

Sur `main` 0551ba2, la suite de référence passe : 1208 tests, 18 sautés. Les 18 tests sautés se répartissent ainsi :
- 14 faute de `jsonschema` ;
- 4 faute du SDK `anthropic`.

Ces deux dépendances sont facultatives. Node est présent, donc les tests du clic ont tourné.

Bilan des trois lots :
- **Usurpations et violations** : aucune, dans aucun lot ni aucun banc.
- **`VERIFIER`** : aucun écart sur une nuit de 8 h de chaque scénario. Il a été lancé avec `spatial.VERIFICATION` dans les lots B et C.
- **Audit de 12 h** (`tools/audit_nuits.py analyser`, 4 scénarios × 4 graines) : aucun plantage.

### Conduite et écarts à la consigne

- **Emplacement des worktrees.**
  - Ils sont dans `.worktrees/lot-a`, `lot-b` et `lot-c`, et non dans `../lot-*` comme le disait la tâche : `CLAUDE.md` interdit les worktrees à côté du dépôt.
  - `main` a été joué depuis un worktree détaché, en lecture seule.
- **Charge de la machine.**
  - Le poste a 4 cœurs : chaque banc a tourné avec `--processus 1`.
  - Les bancs des trois agents passaient un par un, sous un verrou commun (`flock`).
  - Les suites de tests tournaient en `nice`.
  - Les temps d'une nuit en horloge murale sont faussés par la charge des deux autres agents. Le lot A a donc aussi mesuré le temps au processeur.
- **Ajout au lot C en cours de route.** Une autre session a demandé d'ajouter au lot C le défaut N3 de `docs/reverification.md` : la surenchère sans borne et la tâche aussitôt due. Le lot C a fusionné `main` d5d4bee, puis refait la suite, `VERIFIER` et les bancs contre d5d4bee.
- **Pour la fusion.** `main` a avancé depuis, jusqu'à f1eee53 (`boucles-pnj`, `relances-luna`). Les trois branches ont un conflit avec lui :
  - dans `docs/etat-dev.md` pour les trois ;
  - dans `donjon/deliberation.py` pour les trois ;
  - dans `docs/plan-ouie.md` pour le lot C.

  Dans `deliberation.py`, les conflits sont courts :
  - lot A : le répit compté en temps, contre l'hystérésis entre recours de `boucles-pnj` ;
  - lot B : `FIABLE` contre l'avertissement de `prévenir` ;
  - lot C : `_plan_tache` contre la liste des engagements.

  Entre elles, les trois branches ne se heurtent que sur `docs/etat-dev.md`. Le lot B interdit tout accès direct à la croyance `fiable` (test `test_relations_socle`) ; les lots A et C n'en ajoutent aucun. Il faudra le revérifier après fusion avec le `main` actuel.

## Lot A — `temps-reel` : ce qui restait à la minute

Les points 1 à 4 sont faits. Le point 5 ne l'est pas : voir les limites.

### Causes

- `horloges.declencher` n'était appelé qu'à la fin d'une action du joueur. Une attente de 5 minutes retardait donc la rafale de l'auberge, et les PNJ ne la voyaient qu'à la fin.
- Le corps, les besoins et la sécurité ressentie étaient lus à l'instant pile de la minute (`deliberer` → `corps.vivre(1)`, `ressentir`).
  - L'effort était tiré de la première étape du plan, pas du geste fait.
  - Le corps du joueur ne changeait qu'au franchissement d'une minute, selon l'action qui la franchissait.
- La patience comptait des appels (`passage._patienter`) ou des minutes de délibération (`pnj._patienter`), et le répit se comptait à la minute.

### Règles changées

1. **Horloges à leur instant.** Elles se déclenchent dans `pnj._avancer`, à chaque minute franchie ; une échéance déjà passée se déclenche dès le début. L'appel en fin d'action (`moteur._terminer_etape`) est retiré.
2. **Temps vécu** : nouveau module `donjon/vecu.py`, avec un champ `corps["vecu"]`.
   - **Ce que chacun garde.** Chacun, joueur compris, garde l'état où il se trouve depuis un instant :
     - l'activité du geste fait (effort ou repos) ;
     - la chaleur d'un feu ;
     - l'eau ;
     - pour un PNJ, ce que sa sécurité gagne ou perd par minute (`deliberation.ecart_securite`, sorti de `ressentir`).
   - **Ce que `solder` applique** pour le temps passé :
     - faim, fatigue, froid, séchage et trempe, par `corps.vivre`, qui accepte maintenant des fractions de minute ;
     - dérive des besoins ;
     - sécurité.
   - **Pour un PNJ**, le compte se solde à chaque geste (`pnj.agir` → `monde._activite`). `vecu.minute` solde puis relit les conditions.
   - **Pour le joueur**, le compte se solde au début de chaque action.
   - Un état inchangé ne solde rien : le même laps, découpé autrement, donne le même monde.
   - La peine à l'extrême se compte en dixièmes.
   - `tourner` est ajouté à `corps.CALMES`.
3. **Froid sec** : 4 par heure au lieu de 2 (`corps.CORPS`).
4. **Patience et répit en temps.**
   - `pnj.commencer_attente` et `compter_attente` comptent dans `intention["attente"]` le temps réellement attendu, en dixièmes.
   - Le PNJ renonce au-delà de `PATIENCE` minutes, et un autre but remet le compte à zéro.
   - Les renoncements sont datés à l'instant (`deliberation.renoncer`, `stratege`).

### Cas vérifiés après rechargement

Fichier `tests/test_temps_reel.py`, 10 tests.

- **La rafale de l'auberge** :
  - elle tombe à la minute 2 pendant une attente de 5 minutes, et Hugues voit l'âtre éteint dès la minute 2 ;
  - dans un autre cas, une horloge éteint le brasero sous les yeux de Gorm, qui le rallume avant la fin de l'action du joueur ;
  - d'un bloc ou découpé, le monde est le même.
- **Le corps au temps vécu** :
  - Ilse traverse le noir, et la ronde de Gorm passe au chaud. Quel que soit l'instant de départ dans la minute (0, 15, 30 ou 45 s), on obtient le même chemin et les mêmes besoins, à 0,005 près.
  - Que le joueur marche puis tourne, ou l'inverse, ses besoins sont les mêmes.
  - Le froid sec monte de 4 par heure, pour le joueur comme pour Gorm.
- **La patience** :
  - Brune renonce après 30 minutes de guet comptées au temps, puis son répit court ;
  - Gorm, bloqué par le joueur, renonce au bout du temps attendu ;
  - d'un bloc ou découpé, le monde est le même.

Tests adaptés :
- **`test_marche`** : l'attente se compte en dixièmes.
- **`test_entretenir`** : la forme « Mathe appelle X et lui donne une part » n'était pas comptée.
- **`test_recit_pnj`** : Brune renonce devant une serrure trop sombre.
- **`test_refus_retenus`** : l'assertion ne porte plus que sur les offres pour un feu.
- **`test_lumiere_garde`** : avec la graine 42, la nuit est désormais une autre. La scène réelle de `main` à la minute 145 est enregistrée dans `tests/data/relais_42_minute_145.json.gz`.

### Mesures, `main` 0551ba2 → branche

Bancs de 8 h ; Relais sur 8 graines, les autres sur 4.

| Par nuit | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| Usurpations, violations | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Minutes sans recours | 60,6 → 68,1 | 56,25 → 38,75 | 75 → 73,75 | 32,5 → 22,5 |
| Minutes en attente | 52,5 → 72,5 | 240 → 242,5 | 308,75 → 341,25 | 472,5 → 461,25 |
| Événements | 37,25 → 36,25 | 65,5 → 66,5 | 101,5 → 89,75 | 42,5 → 41 |
| Échanges | 15,4 → 16,6 | 43,75 → 44 | 81,25 → 67,5 | 21,5 → 20,75 |
| Vols vus | 1 → 1 | 0,75 → 0,75 | 1 → 1 | 0,25 → 0 |
| Temps d'une nuit, horloge murale (machine chargée) | 15,7 → 14,3 s | 53,3 → 46,6 s | 48,8 → 42 s | 17,6 → 18,2 s |

- **D'où viennent les écarts.** Ils tiennent à des nuits qui divergent une à une, pas à une tendance :
  - Relais : la hausse des minutes dans le noir (27 → 59) et de l'attente vient presque toute de la graine 42 ;
  - auberge : c'est la graine 42 de `main` qui était hors norme, avec 137 événements.
- **Temps au processeur** (graines 1985 et 7, `main` puis la branche, sous le verrou) : Relais 27,8 → 30,4 s, mine 60,8 → 69,2 s, auberge 84,3 → 90,8 s, crue 33,8 → 36,4 s. Cela fait +8 à +14 %. L'essentiel vient de la relecture des conditions après chaque geste.
- **Audit de 12 h.** Pour `main`, on a repris les nuits jouées pour le lot B, avec la même commande.

  | Constat | `main` → branche |
  |---|---|
  | Pressé sans but | 38 → 45 |
  | Noir long | 59 → 64 |
  | Aller voir alterné | 6 → 9 |
  | Appels nombreux | 3 → 0 |
  | Eau longue | 4 → 1 |
  | Dettes en fin de nuit | 5 → 2 |

### Limites

- Les conditions sont relues à chaque geste du PNJ, à son éveil et à la minute, mais pas aux gestes des autres. Un feu qui s'éteint loin de ses yeux pendant qu'il attend ne compte qu'à la minute.
- La fiche du joueur ne montre pas les secondes en cours.
- **Point 5 non fait.**
  - La combustion se compte en minutes entières. L'éteindre à l'instant demanderait de dater chaque allumage et de programmer l'extinction, ce qui touche beaucoup de modules.
  - La crue monte par centimètres, à la minute.
- Restent aussi à la minute :
  - l'effet de seuil des besoins ;
  - les échéances des paroles, des prêts et des dettes ;
  - les dates des croyances.
- **Défaut vu au banc, hors de ce lot** (Relais, graine 42).
  - Aubin, payé pour garder le brasero allumé, n'a pas de flamme pour le rallumer et ne rend pas la tâche.
  - Il promet deux fois une part de planches qu'il ne sert pas.
  - Gorm l'attend 160 minutes dans la conduite noire, alors que ses fagots sont dans la salle voisine.

## Lot B — `relations-socle` : sous-étape 3a, sans changer le comportement

### Cause

La relation tenait dans la croyance `fiable`. Le contrôle du nouveau test relève sur `main` 42 accès directs, en lecture ou en écriture, plus un accès propre dans `voix.fiabilite`.

### Règles changées

- **`donjon/relations.py`**, seul accès à la relation.
  - En 3a, le stockage ne change pas : la valeur reste dans la croyance `fiable`, traduite en cinq axes (confiance, affection, rancune, peur, dette).
  - La confiance vaut 70 si la croyance est vraie, 40 si elle est absente (un étranger), 15 si elle est fausse, et 0 pour un menteur reconnu à la voix.
  - Avec les seuils de méfiance (sous 30) et de confiance (dès 60), on retrouve exactement le tout ou rien d'avant.
  - Affection, rancune, peur et dette restent à 0. `en_veut`, `craint` et `doit` sont prêts mais ne disent encore rien.
- **Lectures** : `envers`, `percue`, `se_mefie`, `se_fie`, `fiable`, `connus` et `croyance`. `percue` remplace `voix.fiabilite`, qui est supprimée.
- **Écritures.**
  - `eprouver(monde, id, autre, cause, source, certitude)`, avec une cause nommée choisie parmi les 13 de la table `EPREUVES` (témoin, vol découvert, mensonge, rumeur, poussée, part servie…).
  - `avis`, pour une affirmation crue du type « X est (ou n'est pas) fiable ».
- **Lectures génériques.** `esprits.croyance` renvoie vers le module pour `fiable`. Cela concerne `paroles.dementi`, `echanges.affirmer` et le stratège.
- **Sites migrés** :
  - persuasion, refus, confidences et rumeurs, aveu ;
  - ouïe, appel, passage ;
  - sécurité, abri, délégation, tâche payée, humeur ;
  - contexte de Luna, stratège, récit, banc ;
  - planificateur (`Vue.se_mefie`, `Vue.se_fie`).
- **Garantie.** `tests/test_relations_socle.py` vérifie qu'aucun code du jeu ni des outils ne nomme `fiable` hors du module, ni n'accède directement à la croyance. `tests/test_voix.py` est adapté à `percue`.

### Cas vérifiés après rechargement

- **Cas réel** : Gorm voit ses vivres dans les mains de Brune.
  - Il se méfie d'elle et refuse sa demande d'office.
  - La persuasion de Brune a un DD de +6.
  - Luna lit « croit que Brune est peu fiable ».
- **Même nature, envers le joueur** : Gorm voit son marteau dans la main du joueur, et l'humeur affichée est « semble méfiant ».
- Une part servie rend la confiance.
- La traduction des trois valeurs est vérifiée.
- Un ouï-dire ne remplace pas une méfiance vue.

### Mesures

- **Nuits identiques à `main`.** 36 nuits de 8 h, sans un seul écart :
  - départ tiré : Relais 8 graines, mine, auberge et crue 4 graines chacune ;
  - départ fixe : 4 scénarios × 4 graines.

  Sont comparés : la chronique, le récit, les souvenirs, l'état final complet, les empreintes et les mesures.
- **Valeurs en départ tiré**, identiques des deux côtés :

  | Scénario | Sans recours | En attente | Événements | Échanges | Vols vus |
  |---|---|---|---|---|---|
  | Relais | 60,6 | 52,5 | 37,25 | 15,4 | 1 |
  | Mine | 56,25 | 240 | 65,5 | 43,75 | 0,75 |
  | Auberge | 75 | 308,75 | 101,5 | 81,25 | 1 |
  | Crue | 32,5 | 472,5 | 42,5 | 21,5 | 0,25 |

- **Audit de 12 h** : données et analyse identiques ; seuls les temps diffèrent.
- **Temps d'une nuit** (machine chargée, écarts dans les deux sens) : Relais 14,1 → 15,3 s, mine 54,4 → 51,8 s, auberge 53,5 → 49,1 s, crue 22,9 → 19,3 s.

### Limites

- La relation est encore stockée dans la croyance `fiable`, déclarée par les scénarios. La migration est pour 3b.
- Plusieurs endroits copient les croyances en bloc :
  - `_entrees` du planificateur ;
  - le dossier du stratège ;
  - la commande « esprit » ;
  - le rejeu ;
  - l'audit.

  En 3b, quand les relations quitteront les croyances, il faudra les y ajouter, sinon des plans périmés seraient repris.
- La règle « une méfiance vue tient » est gardée cause par cause, telle quelle, avec ses incohérences : une imposture reconnue à la voix remplace une méfiance vue, mais une rumeur ou un aveu non.
- `data["relations_pnj"]` et l'humeur ne sont pas touchés.
- Le test de garantie lit le code. Il ne verrait pas un nom d'attribut construit dynamiquement.

## Lot C — `crochetage-surenchere` : deux réglages décidés, plus le défaut N3

`main` d5d4bee a été fusionné par un commit de fusion (03d0884). Les mesures sont faites contre d5d4bee.

### Causes

- `crocheter` faisait toujours un fracas, même quand la serrure cédait du premier coup.
- **Défaut N3** (`docs/reverification.md`), à l'auberge : Odile offre à Tilo 2, puis 4, 8… jusqu'à 64 pièces, Tilo accepte et la dette naît 47 s plus tard. Deux causes :
  - la surenchère doublait l'offre sans autre borne que la bourse, plusieurs fois dans la même minute ;
  - l'acceptation (`devis_pulsion`) et l'empêchement (`_plan_pulsion`) ne jugeaient pas avec les mêmes éléments. Tilo croyait l'âtre allumé et le devis ne comptait qu'une recharge ; il le voyait ensuite éteint, sans flamme pour le rallumer, et la dette naissait aussitôt.

### Règles changées

1. **Le bruit du crochetage suit le jet.** La règle est commune au joueur et aux PNJ.
   - Un crochetage réussi est un geste ordinaire, feutré s'il est fait en douce. La chronique dit « crochète la serrure de … sans forcer ».
   - Un crochetage manqué (« s'acharne ») ou un forcement fait un fracas.
   - L'adresse (DEX diminuée par le corps, lumière) fait la chance de réussir, donc la part des essais discrets.
   - Fonctions et constantes :
     - `ouie.nature_crochetage`, avec `AISANCE` = 0 ;
     - côté PNJ, `pnj._crocheter` rend la marge du jet, tiré avant que le geste ne retentisse ;
     - côté joueur, `Plan.marge` et `Moteur._terminer_etape`, avec le même seuil que les PNJ (`pnj.seuil_crochetage`) ;
     - le voleur qui veut agir sans être entendu attend le bruit que lui promet son adresse (`planification.bruit_crochetage`, avec `HABILE` = 0,5, dans `pnj.agir`).
2. **Surenchère progressive.**
   - L'offre monte de 50 % par refus « cher » (`hausse`, `PALIER`) ; `SURENCHERE` est supprimée.
   - Une seule hausse par minute et par tâche (`Vue.hausse_faite`, qui entre dans `_entrees`).
   - Aucune offre, la première comprise, ne coûte au payeur (`Vue.depense`) plus que la peine que la tâche lui épargne. Au-delà, il renonce.
3. **Accepter une tâche se juge sur ce qui la rendrait impossible.**
   - L'empêchement (`echanges.empeche`) et l'exécution (`planification.planifier_tache`, `deliberation._plan_tache`) reprennent le devis qui a fait accepter la tâche.
   - Un feu payé se compte à recharger, et à rallumer si le payeur ne le croit pas allumé.
   - Ce que le payé a vu ou fait depuis l'offre fait foi (`_vu_avant_la_tache`).

### Cas vérifiés après rechargement

Fichier `tests/test_crochetage_surenchere.py`, 11 tests, plus `test_refus_retenus` réécrit.

- **Crochetage** :
  - Brune réussit en douce dans le dos de Gorm : il n'entend rien. Si elle manque, il se retourne et devient témoin.
  - Si elle réussit sans se cacher, Gorm reste témoin par l'oreille.
  - Le joueur, à l'échoppe, entend un échec mais pas une réussite.
  - Corvus crochète : s'il manque, Gorm vient voir ; s'il réussit, Gorm reste à l'échoppe.
  - Brune maladroite guette ; avec une DEX de 20, elle agit.
- **N3, cas réel** :
  - Odile offre 2, 3, 5, 8 pièces, une hausse par minute, puis renonce. Avant, elle montait jusqu'à 64.
  - Tilo, sans flamme, refuse au lieu d'accepter puis de devoir ; avec un briquet, il fait le travail.
- **N3, même nature** :
  - Joss fait le travail payé, sans dette.
  - Mireille offre 2, 3, puis 5 avec 30 pièces en poche ; elle s'arrête à 2 avec 6 pièces, et n'offre rien avec 3.
- **Tests adaptés** : le texte « sans forcer » dans `test_besoins`, `test_social` et `test_planif_defauts`. Dans `test_social`, Gorm n'entend plus une réussite faite en douce.

### Mesures, `main` d5d4bee → branche

Bancs de 8 h ; Relais sur 8 graines, les autres sur 4 ; moyennes par nuit.

| Crochetages | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| Essais | 3,4 → 3,4 | 24,8 → 25,3 | 13,3 → 6,5 | 0,75 → 0,75 |
| Réussis | 0,5 → 0,5 | 6,5 → 7 | 0,25 → 0,75 | 0,5 → 0,5 |
| Réussis sans forcer | 0 → 0,5 | 0 → 7 | 0 → 0,75 | 0 → 0,5 |
| Entendus sans être vus | 0,5 → 0,5 | 0,75 → 0,75 | 0,75 → 1 | 0,5 → 0 |
| Témoins par l'ouïe (tous gestes) | 0,6 → 0,6 | 0,75 → 0,75 | 1 → 1,75 | 0,5 → 0 |

Marchés de tâches à l'auberge :

| Mesure | Avant → après |
|---|---|
| Offres | 32 → 15,5 |
| Hausses | 5,75 → 0,75 |
| Offre la plus haute | 36,75 → 4,25 pièces |
| Pièces payées pour des tâches | 39,25 → 2,5 |
| Tâches dues moins d'une minute après l'acceptation | 1 → 0 |
| Dettes | 1,25 → 0 |
| Minutes sans recours | 75 → 45 |
| Échanges | 81 → 66 |

- **Crue** : tâches dues aussitôt 0,25 → 0, minutes en attente 472 → 516.
- **Relais** : mêmes mesures, sauf l'offre la plus haute d'une nuit.
- **Vols vus** : égaux à 0,25 près.
- **Temps d'une nuit** : +4 à +10 %, faussé par la charge des autres agents.
- **Audit de 12 h** :
  - dettes non soldées en fin de nuit : 5 → 0 ;
  - à l'auberge, hausses 5,75 → 0,75 et pièces payées pour des tâches 39 → 2,5 ;
  - N1 (ouvrir et fermer en boucle) et N4 (lieu redit en boucle) demeurent, hors de ce lot.

### Limites

- **Valeur d'une tâche.** Pour le payeur, une tâche vaut la peine qu'elle lui épargne, pas l'intensité de son besoin : un payeur pauvre n'offre plus rien.
- **Rythme des offres.** Les premières offres faites à plusieurs personnes dans la même minute restent permises ; seules les hausses sont limitées à une par minute. Le message du commit 967accf (« une offre de la tâche par minute ») ne correspond pas au code final.
- **Bruit attendu par le voleur.**
  - Avec les DEX des scénarios, aucun voleur ne se sait habile : il attend toujours un fracas et guette comme avant. Seul le bruit d'une réussite change.
  - Le planificateur ne pèse pas le risque d'être entendu comme il pèse celui d'être vu.
- **Réglages.** `AISANCE`, `HABILE` et `PALIER` sont des constantes à régler au banc. L'outil ne compte que par sa nature (des crochets, pas un levier).
- **Croyances fausses.** On accepte une tâche sur ce qu'on croit. Une croyance fausse découverte au premier geste rend encore la tâche impossible tout de suite : Joss croyait le ballot dans les mains d'Anselme.
