# Plan : un planificateur par recherche pour les PNJ

Proposition de jalon, à valider. Première étape de l'ordre retenu dans `docs/plan-crue.md` :
avant d'ajouter des comportements (barrer, fuir, porter le feu, convaincre), remplacer les
méthodes de plan écrites à la main par une recherche sur les actions. Le joueur reste passif ;
tout se mesure au banc sans joueur et à son récit.

## Point de départ

`donjon/deliberation.py` fait choisir à chaque PNJ un but par urgence (`candidats`), puis
cherche un plan avec une méthode écrite pour ce but, dont les recours sont dans un ordre fixe :
- faim : ses vivres, sinon une part demandée, sinon (sans scrupule) le bien d'autrui ;
- froid : un feu vif, sinon ranimer un foyer, sinon une part de bois, sinon le bois d'autrui ;
- pulsions : une branche par forme de condition (ronde, objet à sa place, servir, feu
  entretenu, sous clé) ;
- sous-tâches communes de la classe `Plan` : `aller`, `obtenir`, `acceder`, `rejoindre`,
  `flamme`, `cle`, `outil`, `retablir`.

Environ 480 lignes de méthodes. Chaque capacité nouvelle s'y écrit deux fois (pour le joueur et
pour les PNJ) ; `flamme` sait seulement qu'une torche s'allume à une flamme fixe ;
`assembler`, `decouper` et `prelever` n'existent pas pour les PNJ.

## Ce qui change, ce qui reste

**Remplacé** : les méthodes de plan (`_plan_manger`, `_plan_repas`, `_plan_part`,
`_plan_chauffer`, `_plan_ranimer`, `_plan_part_de_bois`, `_plan_pulsion`, `_plan_garder`, les
sous-tâches de `Plan`), et la complétion des gestes du stratège (`stratege.completer`), qui
passera par le même planificateur.

**Gardé** : le choix du but (urgences, parole donnée, routine), la perception et les croyances,
l'exécution geste par geste revalidée sur l'état réel (`pnj.agir`), les gardes (`sans_temoin`),
les gestes qui durent (se chauffer, se reposer, s'abriter), le stratège Luna en dernier recours.

## Le modèle

**État de recherche** : une projection des croyances du PNJ, jamais la vérité. Où il est, ce
qu'il porte, où il croit chaque objet et chaque personne, ce qu'il croit ouvert, verrouillé,
allumé, chargé ; les promesses qu'on lui a faites ; les refus récents. Le plan simule ce qui
change à mesure (il aura ouvert, pris, allumé).

**Actions** : les opérations existantes des PNJ, chacune déclarée une fois, avec :
- ses **conditions** sur l'état (« dans la salle crue de l'objet », « le contenant cru ouvert »,
  « porte la clé », « capacité crochetage et un outil de crochetage ») ;
- ses **effets** sur l'état (« porte l'objet », « ouvert », « foyer allumé ») ;
- son **coût** en minutes, plus ce que le profil y ajoute ;
- sa **garde** à l'exécution (`sans_temoin` pour le bien d'autrui).

Les opérations : aller, prendre, poser, ouvrir, fermer, déverrouiller, verrouiller,
crocheter, manger, inspecter, alimenter, allumer, éteindre, servir, demander (objet ou part),
attendre une part promise, se chauffer, se reposer, s'abriter. Une action dont l'issue dépend
d'un autre (demander) a un **effet attendu** et une **chance** estimée d'après ce que le PNJ
croit : la confiance que l'autre lui porte, ce qu'il sait du besoin de l'autre, un refus récent.
Son coût est divisé par cette chance. Un geste difficile (crocheter) a une chance qui dépend de
la lumière et des caractéristiques, comme son jet.

**Buts** : des conditions sur l'état, celles qu'on a déjà. Faim : avoir mangé. Froid : se tenir
près d'un feu cru vif. Pulsions : l'objet à sa place, sous clé, le feu entretenu, la salle
inspectée. Le choix du but ne change pas ; seule la façon d'y parvenir est cherchée.

**Le caractère comme coût** : les limites restent des interdits (`ne_vole_pas` exclut toute
action sur le bien d'autrui). Sans limite, un geste illicite coûte cher, et ce coût baisse avec
l'urgence du besoin (au-delà de `DESESPOIR`, il compte peu). Demander coûte un peu, plus après
un refus. Ces coûts reproduisent l'ordre actuel (le sien, puis demander, puis voler) sans
l'écrire ; un profil pourra les nuancer plus tard (un caractère qui préfère prendre que
demander).

**Recherche** : A* en avant depuis l'état projeté, bornée (profondeur 8, quelques milliers de
nœuds), déterministe (départage par identifiants triés). Le meilleur plan sous le coût total ;
aucun plan si rien n'aboutit dans la borne.

**Quand chercher** : aujourd'hui chaque PNJ replanifie à chaque minute, ce que permettent des
méthodes peu coûteuses. Une recherche le sera davantage : on ne replanifie qu'à un changement
de but, un geste manqué, ou un changement de croyance qui touche le plan ; sinon on suit le plan
en cours. Le temps de calcul est mesuré au banc.

## Étapes du jalon

1. **Le planificateur seul** (`donjon/planification.py`) : état projeté, actions déclarées,
   recherche. Tests sur des situations isolées, les mêmes que les méthodes actuelles (vivres
   sous clé, clé dans un contenant, porte verrouillée sur le chemin, part demandée, feu à
   ranimer avec une torche allumée au fanal).
2. **En parallèle, sans effet** : au banc, chaque minute, les deux calculent un plan pour le
   même but ; le récit liste les désaccords. On corrige jusqu'à ce que les différences restantes
   soient voulues ou défendables.
3. **Bascule de la faim et du froid** : le planificateur décide pour ces deux besoins. Critère A
   ci-dessous. Les tests existants des comportements doivent passer, ou leur changement être
   justifié un par un.
4. **Bascule du reste** (pulsions, garder, prévenir, complétion du stratège), puis retrait des
   méthodes remplacées.
5. **Critère B**, puis bilan dans `docs/plan-pnj.md`.

## Critères

**A. Ne rien perdre** (banc, 4 graines × 8 h, récit à l'appui) : autant d'événements distincts
ou plus, aucune violation ni usurpation, pas plus de minutes urgentes sans recours, temps de
calcul du banc au plus doublé.

**B. Retrouver et trouver** :
- retrouver sans méthode écrite les chaînes aujourd'hui codées à la main : la clé d'une porte
  sur le chemin, le crochetage, la part promise attendue près des vivres, la torche allumée au
  fanal pour rallumer le brasero ;
- en trouver qui ne sont écrites nulle part, avec les seules actions existantes. Deux visées :
  prendre de la lumière avant de crocheter dans le noir (la chance le justifie), et demander un
  outil porté par quelqu'un qu'on croit fiable.

**C. Moins de règles** : les méthodes retirées, en lignes ; ce qu'il a fallu ajouter pour
déclarer les actions.

## Risques

- **Comportements déplacés** : un plan « équivalent » mais différent change la suite de la
  nuit. L'étape 2 (en parallèle, sans effet) sert à le voir avant de basculer.
- **Temps de calcul** : borne de la recherche, cache par révision des croyances, replanifier
  moins souvent.
- **Chances mal estimées** : un PNJ qui demande toujours, ou jamais. Elles se lisent dans le
  récit et se règlent par des constantes du moteur, pas par personnage.
- **Tests liés aux méthodes** : certains vérifient un plan exact ; ils passent à l'état du
  monde et au comportement observé.

## Hors périmètre

L'influence (proposition jugée sur les buts, avis, confier un but), les relations graduées, la
crue, la fabrication par les PNJ, l'apprentissage de méthodes. Le planificateur les rend
possibles sans méthode nouvelle ; ils viennent aux jalons suivants.

## Bilan

Fait sur la branche `planificateur`, étapes 1 à 5.

- **Comparaison avant bascule**, sans effet, à chaque plan demandé : 8 graines × 8 h et la suite
  de tests. Faim 2 811 accords, froid 585, pulsions et paroles données 3 425 ; restent deux
  écarts d'ordre, gardés parce qu'équivalents ou plus économes (prendre la torche puis les
  planches dans la même salle ; recharger le brasero avant d'aller chercher la torche). Deux
  défauts trouvés et corrigés en route : servir dans une réserve déjà ouverte ne la faisait plus
  refermer à clé ; un bois cru épuisé servait encore à recharger.
- **Critère A** : banc 4 graines × 8 h, mesures identiques à `main` après la bascule de tout ce
  que faisaient les méthodes ; 57 s contre 43 s (+33 %, sous le double). La suite passe ; un test
  supposait l'ordre de la méthode (sa fenêtre passe de 2 à 4 minutes).
- **Critère B** : les chaînes écrites à la main sont retrouvées sans elles (clé, crochetage, part
  promise attendue près des vivres ou du feu, torche allumée au fanal, refermer à clé). Trouvées
  sans être écrites nulle part :
  - dans le noir, Brune va allumer une torche au brasero avant de crocheter la réserve (chance
    5 % sans lumière, 45 % avec) ;
  - demander un objet que porte quelqu'un : sans crochets, Brune demande la clé à Gorm ; au banc
    (graine 42), Gorm, à court de bois, demande ses planches à Aubin, qui les lui remet, puis
    recharge le brasero.
- **Critère C** : `deliberation.py` passe de 931 à 572 lignes ; `planification.py` en a 432 ;
  net +71 lignes. Le gain n'est pas dans le compte : un geste nouveau se déclare une fois, au
  lieu d'une méthode par besoin qui l'emploie.

Limites :
- la chance d'une demande est une constante (`PRET`), pas encore ce que le PNJ croit de l'autre ;
- le caractère ne pèse que par les limites et la faute comptée par personne lésée ; la détresse
  ne la rend pas moins coûteuse (`desespere` ne joue toujours que sur l'attente d'une occasion).
  Levé depuis par l'étape 1 de `docs/plan-social.md` : la faute a un prix, selon l'honnêteté,
  que la détresse use (`caractere.prix_faute`) ;
- les gestes ouverts par un seul but (`vises`) restent une liste écrite dans `planifier_pulsion` ;
- le banc mesure un Relais où ces nouveautés pèsent peu : c'est la crue qui doit les mettre à
  l'épreuve.

## Vitesse (branche `planif-rapide`)

Mesuré d'abord (`banc_pnj --diagnostic`) : 41 % d'une nuit dans les recherches, surtout celles
qui échouent en épuisant l'espace (jamais la borne de nœuds) ; l'espace venait de ce qu'il
pouvait porter d'inutile au but. Trois changements, sans effet sur les comportements (empreinte
des 4 nuits identique) :
- le dernier résultat de chaque PNJ pour chaque but est repris tant que rien de ce que lit la
  recherche n'a changé (`_entrees` : croyances, refus et promesses selon l'horloge, ce qu'il
  porte, les objets hors de ce qui change à chaque minute, les salles) ;
- chaque but dit ce qu'il peut employer (repas, feu) ; on ne prend ou ne demande que ce qui peut
  le servir (`Vue.pertinent`), et l'on ne parcourt que les objets sur lesquels un geste est
  possible ;
- des lectures moins chères.

`planification.VERIFIER` refait par une recherche complète chaque résultat repris ou borné ; la
suite et une nuit de test le font. Limites : une lecture nouvelle de la recherche (un coût qui
lirait l'urgence d'un besoin, l'heure, l'esprit d'un autre, l'état vrai d'un objet) doit entrer
dans `_entrees`, sinon un résultat périmé serait repris ; la pertinence suppose que porter un objet de plus ne rend aucun
geste moins cher, et qu'un but sans emplois déclarés (le stratège) cherche sur tout ; une
recherche qui atteignait la borne de nœuds pourrait désormais aboutir.

## Lumière (branche `lumiere-besoin`)

Manque relevé par la mine : les lampes de Gaspard et Rémy s'éteignent, deux lampes de rechange
restent à la réserve, et personne n'allume ni ne remplit une lampe. Règles communes retenues :

- **Recharger ce qui consomme** (`perception.brule`, `substance`, `recharge`) : une source brûle
  son contenu déclaré (`matiere.SUBSTANCES` : une lampe de l'huile, une chandelle de la cire) ;
  un foyer sans contenu déclaré brûle du bois ; une source sans contenu déclaré (une torche) est
  son propre réservoir. Une réserve de combustible fournit son contenu déclaré, sinon la
  matière dont elle est faite. `alimenter` recharge toute source de ce qu'elle brûle, pour le
  joueur (opération, commande locale, verser l'huile dans la lampe), le MJ (consignes), le
  stratège et les PNJ ; un refus dit ce que brûle la source et quelles réserves conviennent
  (`attendu`). La mine déclare l'huile de ses lampes, un bidon d'huile à la réserve, et ce que
  le camp en sait (lampes de rechange prêtes, briquet de Gaspard).
- **Avoir de la lumière** (`planification.eclairer`) : un recours de la sécurité, avant l'abri,
  quand il se tient dans le noir (ce qu'il ressent) et que le noir l'inquiète
  (`deliberation.peur_du_noir`). Aucune méthode écrite : les gestes déclarés suffisent.
  Allumer une source qu'il porte ou qui est à portée, à une flamme qu'il porte (briquet, autre
  source) ou à une flamme fixe de sa salle s'il porte la source ; la recharger ; la prendre ou
  la demander à qui la porte ; rejoindre un lieu qu'il croit éclairé. Le but est atteint quand
  il porte une source allumée, qu'une source allumée par le plan éclaire sa salle, ou que sa
  salle est crue éclairée.
- **Le noir comme coût** : chaque minute réelle (pas la préférence de demander ou chercher)
  passée dans un lieu qu'il croit obscur coûte `NOIR` × sa peur du noir. Un lieu dont il ne sait
  rien, il l'imagine comme celui où il se tient. D'où, sans règle de plus : allumer sa lampe au
  poêle avant une ronde dans une galerie qu'il sait noire (Rémy, et pas Gaspard qui ne craint
  pas le noir) ; au banc de l'auberge, Odile allume la lampe du comptoir pendant sa ronde.
- **Garder la lumière qui sert** (`deliberation.lumiere_utile`) : là où il se tient, ou là où son
  plan le mène, il croit le noir et le craint, ou un geste demande d'y voir (crocheter). Une
  flamme employée n'est alors pas éteinte pour la ménager, sauf s'il porte une autre lumière ;
  une source qui l'éclaire ainsi n'est pas prêtée (`echanges.necessaire`).
- **La salle éclairée sans ce qu'on porte** : la croyance `eclairee` d'une salle juge le lieu,
  pas les sources que quelqu'un y porte, lui ou un autre (elles suivent leur porteur). Sans cela,
  Rémy éteignait sa lampe parce que Gaspard passait avec la sienne, et se retrouvait dans le noir.
- **Avec l'entretien du feu** (`entretenir-feu`) : la sécurité qui presse passe par ses recours
  (lumière, puis abri) avant les pulsions rompues, qui viennent après ce qui presse ; rien ne
  s'y oppose. Un feu rompu se rétablit tout de suite, au besoin par une part de bois demandée
  (le donneur recharge et rallume) ; quand le feu éclaire de nouveau la salle, la lampe allumée
  pour y voir n'est plus utile et se ménage. Une part de bois promise compte pour la lumière
  (le feu rallumé) comme pour la chaleur.
- Toucher la source d'autrui (l'allumer, la recharger) est une faute comme la prendre.

Mémoire et vitesse : les lectures nouvelles (peur, contenu, croyances de lumière, salle où il se
tient) sont dans `_entrees` ; `VERIFIER` passe sur une nuit de chaque scénario. Ce que la lumière
rend pertinent (sources, flammes, ce qui les recharge) vient du coût du noir, d'un but explicite
de lumière ou d'une lecture de lumière par le but ou ses gestes (voir « Lumière employée ») ; une lampe ou un briquet de plus ne s'explore
pas quand une source allumée est déjà en main, ou, pour qui n'a que faire de lumière, quand il a
déjà une flamme ou qu'aucun feu n'est à allumer ; une lampe pleine ne se recharge pas. Sans ces
élagages, la recherche du poêle de Josse atteignait la borne de nœuds. Temps d'une nuit
(graine 42, processeur) : Relais 6,4 → 6,0 s, mine 10,5 → 13,3 s, auberge 41,5 → 27 s (autre
nuit), crue 7,9 → 6,0 s.

Bancs (8 h ; Relais 8 graines, mine, auberge et crue 4) : Relais identique. Mine : nuits
décalées en fin de nuit, mesures voisines ; quand le poêle meurt, la dernière flamme est le
briquet de Gaspard, que personne ne voit dans le noir : « avoir de la lumière » reste sans geste.
Auberge : Lucien, dans le grenier noir, va au couloir éclairé au lieu d'y appeler à l'aide, puis
revient garder ses biens : il va et vient (jusqu'à 39 fois dans une nuit) ; les lanternes
restent allumées pour qui craint le noir, d'où plus de gestes vus (vols vus 2,75 → 11,25,
confidences 5,5 → 16), moins de bruits allés voir (88,5 → 39). Crue : une nuit sur quatre se
décale.

Rebanc après accord avec `integration` (entretenir le feu, vols vus comptés une fois), contre
`integration` : Relais 7 nuits sur 8 identiques ; minutes urgentes sans recours mine 670 → 636,
auberge 673 → 581, crue 281 → 273 ; vols vus et témoins égaux, sauf l'auberge (0,5 → 1 vol vu
par nuit). À la mine, quand le camp s'éteint, ceux qui craignent le noir vont au bureau qu'ils
croient éclairé (la lampe de bureau, morte depuis) et y tiennent compagnie à Bram.

Limites :
- le va-et-vient entre deux besoins dont l'urgence dépend du lieu (la garde au grenier noir, la
  lumière du couloir) : rien ne retient dans la lumière celui qui n'emporte pas de lumière ;
  l'abri a la même faiblesse ;
- demander une flamme suppose de croire son porteur là : dans le noir, on ne retrouve personne
  (manque déjà relevé) ; on n'allume pas sa lampe à celle d'un autre sans la lui emprunter. Levé
  par `pnj-lumiere-garde` : on cherche (et appelle) qui porte la flamme, et on lui demande du feu ;
- inspecter dans le noir compte encore comme une ronde ; seul crocheter demande d'y voir ;
- une lampe n'a pas de contenance : chaque charge ajoute sa durée ;
- une lampe prêtée reste celle d'autrui : l'allumer est une faute (prêts, manque déjà relevé).

## Défauts corrigés (branche `planif-defauts`)

Trois écarts entre ce que la recherche supposait et ce que le PNJ croit ou ce que le geste réel
permet. Règles communes, sans branche propre à un cas :

- **La chance crue est celle du jet réel.** `planification.chance_crochetage` et `pnj._crocheter`
  partent du même seuil (`pnj.seuil_crochetage` : 14, plus 4 par niveau de lumière manquant) ; la
  lumière est celle qu'il croit là où il se tient (`deliberation.lumiere_crue`). Plus de chance
  plancher (`CHANCE_MIN`, 5 %) : quand aucun jet ne réussit, le geste n'est pas envisagé, et le
  plan passe par la lumière (en prendre, en demander, en allumer) ou n'existe pas. La croyance de
  lumière d'une salle porte désormais son niveau (`etat` : `{"eclairee", "niveau"}`, 0 noir,
  1 pénombre, 2 éclairé), vu là où il se tient, sans les sources portées
  (`esprits.constater_lumiere`). Un lieu dont il ne sait rien : éclairé s'il y croit une source
  allumée, sinon imaginé comme celui où il se tient (la règle de `noir_cru`). Un essai manqué fait
  constater la lumière qu'il avait (le niveau de sa case) : un plan fait sur la lueur vue de
  l'entrée se corrige au premier échec. Une lampe allumée pour crocheter reste utile tant que le
  lieu n'est pas cru en pleine lumière (`lumiere_utile`).
- **Une porte verrouillée est une serrure comme un contenant.** Une porte qui sort de sa salle et
  qu'il croit verrouillée se crochète (même chance, même faute selon son propriétaire, même bruit,
  `ouie` : crocheter est bruyant) ; le trajet passe ensuite par les portes que le plan a
  déverrouillées (`pnj.chemin`, `ouvertes` ; `Vue.route`). La clé qu'il porte l'ouvre toujours en
  chemin, et demander la clé reste demander un objet. Données de la mine : la porte du bureau est
  à Bram (la crocheter est une faute, qui attend de n'être vue de personne).
- **Les pièces se comptent sur ce qu'il croit.** `enrichir` lit la croyance `pieces` d'une bourse
  (sue en la tenant : `esprits.constater` ; ou un savoir du scénario : la mine déclare que le camp
  sait la paie de 200 pièces), jamais le compte de l'objet ; une bourse dont il ne sait rien ne le
  tente pas. `pieces` entre dans `CHANGEANTS` : la recherche ne lit le vrai compte que de ce qu'il
  peut dépenser (`richesse`).

Cas vérifiés après rechargement (`tests/test_planif_defauts.py`) : Odon au bureau noir n'essaie
plus le coffre (cas réel, mine 1985, une heure d'essais), et dans la pénombre sa chance crue est
la vraie ; Brune devant la réserve placée aux vannes noires n'essaie pas, et l'essaie dans la
pénombre du brasero ; un échec lui apprend la lumière qu'elle avait. Odon crochète la porte du
bureau pour la paie ; Brune crochète la porte étanche pour une réserve placée au palier. Odon
convoite la paie qu'il croit pleine même vide, pas celle qu'il croit vide même pleine, et sait le
compte en la tenant ; Lucien ne convoite la bourse d'Anselme qu'en sachant ce qu'elle contient.
`VERIFIER` passe sur une nuit de 8 h de chaque scénario.

Bancs 8 h contre `main`, lancés au même moment (Relais 8 graines, mine, auberge et crue 4 ;
moyennes par nuit, avant → après) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| minutes sans recours | 293,75 → 296,25 | 462,5 → 448,75 | 690 → 642,5 | 417,5 → 417,5 |
| achats | 1,62 → 1,5 | 1 → 1 | 0,75 → 0,75 | 2 → 2 |
| vols vus | 1 → 1 | 0,75 → 0,75 | 1 → 0,25 | 0 → 0 |
| crochetages : essais (réussis) | 3,62 (0,62) → 3,5 (0,62) | 28,5 (0) → 0,75 (0) | 31,5 (0,75) → 0,25 (0,25) | 0 → 0 |
| événements distincts | 31,88 → 31,75 | 43,5 → 43,75 | 47,75 → 38,75 | 36,25 → 36,25 |
| renoncements | 1 → 1,25 | 3,75 → 6 | 2,25 → 1,25 | 0,25 → 0,25 |
| temps processeur d'une nuit | 10,8 → 10,7 s | 33,3 → 31,4 s | 27,9 → 32,5 s | 11,3 → 11,5 s |

Aucune usurpation ni violation. À chaque essai des nuits contrôlées (Relais 7 et 500, mine 7 et
1985, auberge 42 et 1985), la chance crue égale la chance réelle. Écarts expliqués :
- mine : les 28 à 30 essais d'Odon au coffre dans le bureau noir (minute 450, aucun possible)
  tombent à un seul, celui qui lui apprend le noir (il avait vu la lueur du baraquement depuis la
  porte) ; il n'y a plus de fracas à aller voir (alles voir 18,5 → 15). Odon envisage désormais de
  crocheter la porte du bureau, mais le baraquement n'est jamais sans témoin : il guette, puis
  renonce (deux renoncements de plus par nuit) ; aucune porte crochetée au banc ;
- auberge : Lucien s'acharnait 35 à 52 fois sur le coffre ferré de la chambre noire pour le
  ballot (graines 7, 42, 2024) ; ce fracas faisait se retourner, aller voir, en être témoin (vols vus). Sans lui, moins d'événements et d'échanges ; la graine 1985, où il
  réussit d'un coup en pleine lumière, est identique. Le temps augmente : ses recherches du ballot,
  sans issue dans le noir, épuisent l'espace au lieu de reprendre un plan ;
- Relais : la pénombre du refuge compte pour 15 % (DEX 0) et non plus 35 % : trois nuits décalent
  le moment où Brune force la réserve ; la crue est identique.

Limites :
- la lumière crue d'une salle est celle de la case où il se tenait : la serrure peut être plus ou
  moins éclairée ; il le constate au premier essai (au plus un essai perdu par arrivée). Levé par
  `petits-correctifs-pnj` : il la constate devant la serrure, avant d'essayer ;
- un essai à chance réelle faible mais non nulle (5 % avec DEX + 2 dans le noir) reste envisagé,
  à son coût (1 / chance minutes) : les jets sont indépendants, un échec n'apprend rien de plus ;
- forcer une porte (frapper) n'est pas un geste des PNJ ; seuls la clé et le crochetage lèvent
  une porte verrouillée, et le PNJ n'apprend une porte verrouillée qu'en l'essayant ou par savoir.
  Forcer est devenu un geste des PNJ (`petits-correctifs-pnj`) ;
- personne n'apprend le contenu d'une bourse autrement qu'en la tenant ou par un savoir déclaré :
  ni la voir compter, ni l'entendre dire ;
- au banc, Lucien, dans la chambre noire, ne va pas chercher de lumière : sa recherche n'en trouve
  aucun moyen ; il retourne garder ses biens. Diagnostiqué dans `pnj-lumiere-garde` : ses plans de
  lumière existent (le couloir éclairé) mais coûtent plus que ses biens laissés (`GARDE`), et la
  seule lampe portable qu'il connaît est à Hugues, qui se méfie de lui.

## Dynamique des besoins (branche `besoins`)

Décidé avec l'utilisateur, trois volets ; aucune branche propre à un personnage, un lieu ou la
lumière.

**L'effet de seuil** (`deliberation.urgents`, `eveiller`, état `esprit["urgences"]`). Un seul effet
de seuil : un besoin presse quand il dépasse un repère d'une marge. Son repère est son seuil ;
repassé au-dessous, il est apaisé et ne presse de nouveau qu'à son seuil + `REPRISE` (15), comme un
thermostat, à moins d'être d'abord bien redescendu (seuil − `REPRISE`) : un repas, un feu, le repos
rendent le seuil ordinaire. Au choix du but (`inertie`), le plan en cours d'un autre besoin est
aussi un repère : un besoin ne l'interrompt que s'il presse plus que lui d'`INERTIE` (5) ; l'ancienne
`INERTIE` (un besoin qui vient de franchir son seuil laisse finir le plan en cours) en est le cas
où le besoin servi ne presse plus. L'état (« presse », « apaise », « attente », et depuis quand) est
dans l'esprit. `REPRISE` à 15 : à 10, les rondes de Lucien (mine) qui le rassurent de 20 le
refaisaient battre ; au-delà de 15 un besoin apaisé tarde trop (le froid d'Ilse au Relais restait
entre 70 et 85 avant le seuil redescendu, corrigé par la remise à zéro sous seuil − 15).

**Ce qu'un plan laisse monter** (`planification.Vue.pression`, `RESTER`, `GARDE`). Une minute dans
un état coûte ce qu'il y laisse monter : le noir pour qui le craint (`NOIR` × peur, déjà compté en
chemin), et l'éloignement de chaque lieu où il garde ses biens quand ils le pressent (`GARDE` = 2,
`deliberation.gardes`). Un but qui se tient en restant (la lumière, garder ses biens, l'abri, se
chauffer) compte en plus `RESTER` (30) minutes de ce que son état final laisse monter ; la recherche
explore au-delà du premier état qui atteint le but, d'où, sans règle de plus, rapporter une lampe là
où il garde ses biens. Pour la lumière et la garde (`endurer`), il ne part que si le plan coûte moins
que rester où il est ; sinon il endure, et le besoin attend. L'abri y ajoute ce qu'il apporte (y
voir, quitter qui l'inquiète, une compagnie sûre, aux taux du profil). Le plan de lumière se tient
jusqu'au lieu choisi : la lampe en main en chemin, il va jusqu'au bout. `GARDE` à 2 : plus que le
noir à la peur ordinaire (0,5 × 3) et que la compagnie (0,5 × 3), moins que pour qui craint fort le
noir (Bram, 0,8 × 3) ; à 1, Bram quittait son bureau pour la compagnie de la galerie, la lampe en
main.

**L'attente** (`deliberation._classer`, `attentes`). Un besoin qui presse et dont chaque recours a été
essayé sans plan (ou qui n'en a aucun) se met en attente ; dès qu'un recours aboutit, il presse de
nouveau. Rien ne l'oublie : ses recours sont repris à chaque minute, à leur rang, et la mémoire du
planificateur ne refait une recherche que si ce qu'il croit a changé. Un recours qu'on n'a pas
essayé (un but plus pressant a abouti, un renoncement récent) ne décide rien. Dans le moteur actuel,
un besoin sans plan ne bloquait aucun autre but (les candidats passent au suivant) : ce qu'il
faussait, c'est la mesure (« sans recours ») et le récit. Le banc distingue désormais
`minutes_urgentes_sans_recours` (un plan possible, qu'il n'entreprend pas : au banc, tous des
renoncements après une occasion guettée en vain) de `minutes_urgentes_en_attente` (aucun plan sur ce
qu'il croit : le devoir de Gorm, d'Odile et de Mireille sans bois ni tâche, la faim sans vivres connus
ou après un refus) ; le stratège est toujours appelé pour un besoin sans plan.

Cas vérifiés après rechargement (`tests/test_dynamique_besoins.py`) :
- Lucien, l'auberge telle qu'écrite, au grenier noir, biens et sécurité pressants : il allait au
  couloir et revenait (19 changements de salle en 4 h sur `main`) ; il va prendre la lanterne de
  l'étable et la rapporte au grenier, où il reste (5 changements, dont le vol du ballot).
- Bram, la mine, la chandelle du bureau à sec, sachant la lampe du filon allumée : sur `main`, abri
  au baraquement deux heures, puis retour au bureau ; il va prendre la lampe et revient garder la paie.
- Sans lumière à emporter : à la peur ordinaire, ses biens l'emportent, il retourne au grenier et
  y endure le noir (la sécurité attend) ; qui craint fort le noir reste dans la lumière (les biens
  attendent).
- L'effet de seuil, le besoin comblé qui retrouve son seuil, l'interruption d'un plan.
- Le devoir de Gorm sans tâche possible attend, puis reprend à la ronde échue ; la faim refusée
  attend, puis redemande quand le refus a vieilli.

**La lumière d'une salle, une seule règle** (`esprits.constater_lumiere`, `deliberation.lumiere_crue`).
Correctif révélé en route, accordé avec la croyance à niveaux de `planif-defauts`. Ce qu'il constate
là où il se tient garde deux choses : `niveau`, la lumière de sa case, lueur d'une salle voisine
comprise (sa chance au crochetage est celle du jet) ; `propre` (et `eclairee`, `propre` > 0), ce que
la salle tient de ses propres sources. Sur place, il juge à `niveau` ; de loin, à `propre` : la lueur
d'une autre salle n'éclaire que les cases où elle entre. Sans cela, au seuil de la cuisine de
l'auberge, Joss, Tilo et Mathurine croyaient la cuisine éclairée, s'y abritaient, s'y trouvaient
dans le noir et repartaient chercher la lumière à chaque minute (alternances lumière ↔ abri par
nuit : 15,75 sur la branche avant ce correctif, 0 après ; `main` d'alors 0,5).

Bancs (8 h, départ tiré ; Relais 8 graines 1985 7 42 2024 3 11 99 500 `--joueur chambre_cloche`, mine,
auberge et crue 4 graines 1985 7 42 2024 ; `main` 87c1ed5 → `besoins`, moyennes par nuit ; `main` et
la branche lancés en même temps). Chaque PNJ oisif et pressé compte dans une seule catégorie : sans
recours, en attente, ou confiée (une pulsion confiée à qui l'on croit fiable, `depart-tire`).

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| sans recours | 116,9 → 53,1 | 368,75 → 56,25 | 665 → 67,5 | 81,25 → 45 |
| en attente (nouvelle mesure) | → 67,5 | → 306,25 | → 622,5 | → 52,5 |
| confiées | 171,9 → 163,1 | 0 → 0 | 0 → 0 | 266,25 → 261,25 |
| urgentes oisives (total) | 289,4 → 284,4 | 681,25 → 680 | 960 → 975 | 351,25 → 362,5 |
| événements | 30 → 31,1 | 45,5 → 44,5 | 43,75 → 46,5 | 34,25 → 34,75 |
| échanges | 11,4 → 11 | 27,75 → 27,75 | 20,25 → 23,75 | 10,75 → 11,75 |
| va-et-vient (A, B, A < 30 min) | 8,25 → 8,1 | 13 → 6 | 19,25 → 2,25 | 4,75 → 5,5 |
| vols vus | 0,9 → 1 | 0,75 → 0,75 | 0,5 → 0,5 | 0,5 → 0,75 |
| usurpations, violations | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

Les minutes urgentes oisives restent les mêmes : ce qui change, c'est qu'on sait pourquoi. La plupart
des « sans recours » étaient des besoins sans aucun plan sur ce qu'il croit (en attente) ; restent
les renoncements après une occasion guettée en vain. Va-et-vient : avec le départ tiré, le cas réel de
Lucien revient au banc de l'auberge sur `main` (70 en quatre nuits, entre le grenier et la lumière),
3 sur la branche ; à la mine, Lucien 8 → 1,25 et Odon 4,25 → 3,25 ; au Relais et à la crue, ce sont
les rondes de Gorm entre deux gardes (marchand 7,5 → 7,25 au Relais, 4,25 → 5,25 à la crue), un
devoir que la branche ne change pas. Crue : un vol vu de plus (graine 7), minutes dans l'eau 492,5 →
476,25. `VERIFIER` sur une nuit (graine 42) de chaque scénario.

Premier banc, départ fixe, contre `main` 789be7a : sans recours 294 → 71, 463 → 84, 690 → 126, 445 →
33 ; va-et-vient 6,6 → 5,5, 8,25 → 3,5, 4,5 → 2,25, 4 → 0,5. Au Relais, Ilse y hésitait deux fois
entre l'abri et le brasero sur trois nuits (froid apaisé sans être comblé, voir les limites) ; le
départ tiré ne le reproduit plus.

Temps de calcul (une nuit par processus, départ tiré, `main` et `besoins` lancés ensemble, moyenne des
4 graines, `--diagnostic`) : Relais 4,8 → 5 s, mine 16,6 → 17,2 s, auberge 18,7 → 21,1 s, crue
6,6 → 6,8 s. À l'auberge, la part du planificateur passe de 9 à 10,9 s : les recherches `garder`
(1,9 s par nuit) et le surcoût de `GARDE`, qui renchérit chaque minute loin de ses biens et élargit
d'autant les autres recherches de qui garde. Le cas le plus lourd (départ fixe, graine 1985) :
Lucien au grenier noir refait chaque minute une recherche `garder` d'environ 450 nœuds (tout ce
qu'il pourrait faire pour moins que les 30 minutes de noir qu'il endurerait), que la mémoire du
planificateur ne reprend pas : le prix d'une faute varie avec la détresse de ses biens à chaque
minute, et la lanterne à rapporter est à autrui. Aucun élagage exact n'a été trouvé : ne retenir le
prix d'une faute que quand un geste fautif s'est présenté ne reprend presque rien (la lanterne est
fautive), et une borne inférieure du retour (A*) changerait l'ordre entre plans de même coût, donc
les nuits.

Limites :
- le cas réel de Lucien est aussi rejoué en placement d'auteur (départ fixe) ; au banc de l'auberge,
  Anselme revient de la lumière quand il entend forcer son coffre (un bruit à aller voir, légitime) ;
- `GARDE` est une constante du moteur, pas encore une valeur du profil ; un méfiant près de ses
  biens ne pèse pas sur la garde : à la mine, Bram revenu avec la lampe part s'abriter quand Odon,
  dont il se méfie, entre au bureau (méfiance et compagnie l'emportent sur `GARDE`) ; depuis que la
  porte du bureau se crochète (`planif-defauts`), Odon y vient pour la paie : le test de Bram le
  rend honnête pour isoler la garde. Levé par `pnj-lumiere-garde` (la menace sur le bien) ;
- seuls le noir et la garde ont un coût par minute ; le froid, la compagnie et la méfiance n'entrent
  que dans le gain de l'abri ; se chauffer compte le séjour sans l'endurer ;
- au Relais, Gorm demande les planches d'Aubin plutôt que d'aller chercher son bois à la crypte
  (s'éloigner du refuge coûte `GARDE`) : cohérent avec la règle, à signaler. Diagnostiqué dans
  `petits-correctifs-pnj` : `GARDE` n'en est qu'une des causes ;
- la lumière d'une salle se constate à la case où il se tient : une salle aux sources inégales se
  juge de loin à ce qu'il en a vu de sa case ;
- la peur du noir ne s'émousse pas avec le temps passé ;
- un besoin apaisé sans avoir été comblé (repassé sous son seuil sans descendre à seuil − `REPRISE`)
  ne presse de nouveau qu'à seuil + `REPRISE` (au départ fixe, Ilse au Relais laissait monter son
  froid jusqu'à 85, puis hésitait deux fois entre l'abri et le brasero) ;
- le planificateur coûte plus à qui garde ses biens (auberge +13 % de temps par nuit, ci-dessus).

## Petits correctifs (branche `petits-correctifs-pnj`)

Quatre écarts entre ce que le planificateur supposait et ce que le PNJ croit, voit ou peut faire.
Règles communes, aucune branche propre à un personnage, un objet ou un lieu.

**La lumière se constate devant la serrure** (`pnj._assez_de_lumiere`, `esprits.constater_lumiere_devant`,
`planification.Vue.lumiere_devant`). L'étape `crocheter` porte la lumière sur laquelle le plan
comptait (`contenu: {"lumiere": n}`). Arrivé devant, avant tout geste (le tour d'horizon compris),
il constate la lumière de sa case (ce qu'il porte compris, celle du jet) et la retient de l'objet
(croyance `lumiere`, sans ce qu'on porte, comme celle d'une salle). Si elle est moindre que prévu ou
rend le geste impossible, il n'essaie pas (chronique « renonce à crocheter … : trop sombre, là »)
et reconsidère à la minute suivante : de loin, la chance devant cet objet se juge sur ce qu'il y a
vu, à défaut sur la salle, et pleine avec la lumière du plan (une source en main ou allumée là).
Une étape sans lumière prévue (stratège) n'est arrêtée que si le geste est impossible.

**Forcer** (`donjon/force.py`, geste `frapper` du planificateur, `pnj._forcer`). La règle de
`frapper` du joueur, sortie du moteur et partagée : outil qui fait choc (percussion, levier) ou qui
coupe la cible ; d20 + FOR modulée + 2 (percussion) contre 10, un 1 abîme l'outil ; un coup réussi
ôte la puissance de l'outil plus la FOR qui aide ; à zéro, la porte reste ouverte et
déverrouillée, le contenant s'ouvre et ce qu'il tenait tombe au sol (`force.briser`, aussi pour le
joueur). Au plan : sur une serrure qu'il croit fermée à clé, avec un outil qu'il porte, coût =
coups nécessaires / chance d'un coup, la serrure devient ouverte. Sur le bien d'autrui, deux prix :
la faute (honnêteté, une fois par personne lésée) et le dégât (douceur, `caractere.prix_faute(…,
"douceur")`, une fois par personne lésée, `Vue.degat`), chacun exclu à 100 ; aucune permission
(prêt, garde) ne couvre ce qui brise (`biens.BRISER`). Chaque coup est bruyant (`ouie`), entre au
registre des gestes illicites (`frapper`, puis `briser` quand elle cède) et se raconte (« a frappé
pour forcer », « a forcé »). Un outil qui force n'est pertinent que s'il croit une serrure fermée
à clé (`Vue.verrous`). Distinct du geste nommé `forcer` du registre, qui reste l'essai de
crochetage manqué. `_entrees` lit le prix du dégât, la FOR modulée et ce qu'il est illicite de
briser ; l'intégrité d'un objet y entrait déjà.

**Gorm et les planches** (diagnostic par `--diagnostic` et une comparaison des coûts : le meilleur
plan, le meilleur sans demander ni acheter, puis sans `GARDE`, puis sans `NOIR` ; Relais graines
1985, 7, 42, 2024, 99 et 500 aux minutes où Gorm demande). Trois causes :
- **la croyance** : les vannes, où est son bois, ne sont baignées que de la lueur diffuse du
  brasero (pénombre partout, `CarteLumiere.ambiance`) ; de loin, il jugeait une salle à ses seules
  sources (`propre`, branche `besoins`), et les croyait noires : deux minutes de noir lui coûtaient
  3 (`NOIR` × 0,5). Désormais `propre` compte aussi la lueur diffuse qui baigne la salle entière
  (`esprits.lumiere_ici`) ; seule la lumière directe d'une source voisine, qui n'atteint que les
  cases qu'elle voit (un seuil), en reste exclue. Sans cases, la lueur d'une voisine baigne la
  salle : elle compte ;
- **le coût** : une part demandée comptait 1 + `DEMANDE` (4), comme si elle était accordée,
  quand un objet demandé coûte 1 + `DEMANDE` / `PRET` (7). Elle coûte désormais comme l'objet ;
  acheter (accepté sans jet) reste à 1 + `DEMANDE` + le prix ;
- **`GARDE`** : quand ses biens le pressent (la réserve forcée par Brune), s'éloigner du refuge lui
  coûte 2 par minute ; acheter une part à Aubin, présent, reste moins cher qu'aller aux vannes
  (5,7 contre 15 à la graine 42). C'est la règle de la garde, gardée.
Graine 1985, minute 106 : avant, demander 4 (puis acheter après un refus) contre son bois 7 ;
après, son bois 4, acheter 4,7, demander 7.

Cas vérifiés après rechargement (`tests/test_petits_correctifs.py`) :
- lumière : Odon (mine, cas réel de `planif-defauts`) entre au bureau qu'il imaginait comme le
  baraquement, renonce devant le coffre en pénombre sans essai, retient la lumière, puis essaie à
  la minute suivante sur un plan qui la porte ; Brune devant la réserve en pénombre au fond du
  refuge éclairé ; Brune aux vannes noires qu'elle croyait éclairées : elle n'essaie rien, et son
  plan ne crochète plus sans lumière en main ;
- forcer : Brune force la porte étanche, qui n'est à personne (même à douceur 100), passe et mange ;
  à douceur 100 elle ne force pas la réserve de Gorm, à 60 elle la force et les vivres tombent au
  sol ; Ilse qui la voit frapper cesse de la croire fiable ; le joueur frappe par la même règle ;
  Gorm sans clé force la porte étanche avec le pied-de-biche pour rapporter la cloche
  (`test_besoins`, qui garde aussi le cas sans outil : la cloche reste là-haut) ;
- Gorm : les vannes baignées de lueur sont crues en pénombre, le cellier fermé reste noir ; Gorm
  va prendre ses fagots, recharge le brasero, les planches d'Aubin restent entières ; une part
  demandée coûte 1 + `DEMANDE` / `PRET`. À l'auberge, Mireille achète désormais la part de fagots
  de Joss au lieu de la demander (`test_entretenir`). À la mine (graine 3, départ fixe, 10 h), le
  blessé, qui appelait à l'aide dans le noir, va allumer une lampe de rechange à la réserve ouverte,
  Odon en prend une autre et éclaire Bram au bureau (`test_mine` accepte désormais l'un ou l'autre) :
  les deux lampes que personne n'allumait (manque relevé par `lumiere-besoin`) servent.

`VERIFIER` passe sur une nuit de 8 h (graine 42) de chaque scénario. Bancs 8 h, `main` 1ee493b et la
branche lancés au même moment (Relais 8 graines, joueur à la galerie ; mine, auberge et crue 4 ;
départ tiré ; moyennes par nuit, `main` → branche) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| sans recours | 53,1 → 53,1 | 56,3 → 58,8 | 67,5 → 15 | 15 → 15 |
| en attente | 67,5 → 62,5 | 303,8 → 288,8 | 622,5 → 540 | 105 → 88,8 |
| événements distincts | 31,1 → 31,6 | 45,3 → 47 | 46,5 → 48,3 | 33,8 → 32,5 |
| échanges | 11 → 11,1 | 28,3 → 30 | 23,8 → 26,5 | 10,8 → 10,3 |
| achats | 1,1 → 2 | 1 → 1,5 | 0,25 → 2,25 | 1,75 → 2,5 |
| crochetages : essais (réussis) | 4 (0,63) → 3,75 (0,5) | 2,75 (0,5) → 3,5 (0,25) | 13,5 (0,25) → 3,75 (0,25) | 6 (1,25) → 4,5 (1,25) |
| renoncements devant une serrure trop sombre | 0 → 0 | 0 → 1,5 | 0 → 1,75 | 0 → 0 |
| forçages : coups (réussis) | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| parts remboursées | 0 → 0,13 | 0 → 0 | 0 → 0 | 0 → 0 |
| vols vus | 1 → 1 | 0,75 → 0,75 | 0,5 → 0,5 | 0,25 → 0,25 |
| nuits distinctes (5/60/120/240/480 min, issues) | 8 partout → 8 partout | 4 → 4 | 4 → 4 | 4 → 4 |
| temps d'une nuit (8 processus ou 4 par côté, 4 cœurs) | 32,7 → 35,2 s | 60,1 → 72,5 s | 76,1 → 83,7 s | 22 → 22,4 s |

Aucune usurpation ni violation (le banc vérifie l'état à chaque pas). Écarts expliqués :
- Gorm : avant, il demandait ou achetait une part des planches d'Aubin vers la minute 110 à 150
  dans 6 nuits sur 8 alors que ses fagots étaient aux vannes ; après, il va les chercher dans les
  nuits où ses biens ne le pressent pas (1985, 3, 11, 99 : premier achat de planches quand son bois
  est épuisé, minute 348 à 361), et achète encore dans les quatre où ses biens le pressent
  (7, 42, 2024 après que Brune a forcé la réserve, 500 : `GARDE`). Le compte des échanges de planches est égal (2,5 par nuit) : il
  se déplace vers la fin de la nuit, quand son bois est épuisé ;
- achats en hausse partout : une part demandée coûte désormais selon sa chance ; payer (sans jet)
  devient souvent moins cher que demander (Mireille, Joss, Mathurine à l'auberge) ; les refus
  suivis d'un achat deviennent un achat, d'où moins de minutes en attente ;
- auberge : Lucien s'acharnait sur le coffre ferré à la lumière de la case d'où il partait (13,5
  essais par nuit) ; il renonce devant la serrure plus sombre (1,75 par nuit), puis n'essaie plus que
  là où sa chance le justifie (3,75). Les minutes sans recours tombent (67,5 → 15) : moins de guet
  vain devant le coffre ;
- mine : Odon renonce devant le coffre de la paie (1,5 par nuit) au lieu d'un premier essai perdu ;
  le temps augmente (+20 %) : un outil qui force (la pioche) devient pertinent pour qui croit une
  serrure fermée à clé, ce qui élargit des recherches, et la lueur diffuse se calcule à chaque
  constat ;
- aucun forçage au banc : dans les quatre scénarios, ceux qui prendraient le bien d'autrui ont la
  douceur à 100, et la seule porte sans propriétaire qu'on trouve fermée sur son chemin s'ouvre à
  la clé que Gorm porte ;
- un remboursement (Relais, graine 99, minute 419) : Gorm rend 2 pièces à Aubin, la part de vivres
  vendue n'ayant pas été servie (`docs/plan-social.md`).

Limites :
- la lumière devant une serrure est celle qu'il y a vue en dernier : une source posée près d'elle
  depuis ne compte qu'avec la lumière du plan ou à son retour ; sa chance au geste se constate,
  celle d'un autre geste (inspecter) non. Levé par `pnj-lumiere-garde` pour une source qu'il sait
  allumée ou posée près d'elle depuis ;
- la chance d'une demande reste une constante (`PRET`), pour un objet comme pour une part ;
- forcer ne connaît que l'intégrité de la cible (vue, comme son aspect) ; abîmer ce qui n'est à
  personne ou ce qui est à soi n'a d'autre prix que le temps et le bruit ; le geste ne sert qu'à
  lever une serrure fermée à clé (pas une porte calée, ni une cloison) ;
- la lueur diffuse est la même dans toute la salle (`ambiance`) ; une salle en L ou un recoin
  qu'elle n'atteindrait pas serait cru en pénombre (c'est le modèle du moteur lui-même, voir
  `pnj-lumiere-garde`) ;
- Gorm achète encore les planches d'Aubin quand ses biens le pressent : c'est `GARDE`. Corrigé par
  `pnj-lumiere-garde` : l'attente de la part, loin de ses biens, n'était pas comptée.

## Lumière et garde (branche `pnj-lumiere-garde`)

**Recours d'un gardien en détresse (lot 43, `codex-gardien-detresse`).** Un besoin
en attente, faute de plan accepté, ouvre les secours qui le laissent auprès d'un
bien dont il a la charge. La recherche commune propose de confier l'allumage d'une
source locale ou la remise d'un moyen utile connu, pour tout but qui l'emploie ;
les demandes ordinaires d'objet, de part et de feu restent disponibles. L'appel à
l'aide couvre aussi les autres besoins bloqués, une fois par épisode du besoin ;
les charges déjà satisfaites ou déléguées ne déclenchent pas cet appel.
Ni le prix de la garde, ni les seuils, ni `REPIT` ne changent.

La demande utilise `echanges.confier` et son devis autonome, ses droits et son jet.
Elle ne réalise aucun effet : le plan s'arrête à la parole, puis attend le geste
réel. Le demandeur garde dans `aides_attendues` ce qu'il a entendu accepter ; il
ne consulte pas l'agenda privé de l'autre. Un refus reçu ou l'échéance commune
ferme cette attente. Une remise se fait en main propre, même dans le noir.
`Vue.detresses`, le poste gardé et les aides connues entrent dans `_entrees` ;
un recours d'aide en cours se conserve après le classement du besoin en « presse ».

Le secours reste une possibilité, pas une ressource créée : l'autre peut refuser,
ne rien avoir ou ne pas venir. Sur mine 42, Bram demande à Gaspard de rallumer sa
lampe (impossible), puis appelle pour la faim ; les biscuits sont déjà connus
épuisés. L'appel de sécurité existant avait bien eu lieu à 462. Les croyances de
lieu restent révisées seulement par les indices perçus, sans effacement automatique
d'une présence dans le noir. Voir le [rapport du lot 43](taches/rapport-codex-43-gardien-detresse.md).

Quatre limites des branches précédentes. Règles communes, aucune branche propre à un personnage, un
objet ou un lieu ; diagnostics faits sur les bancs (`--chronique`, `--diagnostic`) et sur des copies
de leurs états (coûts des plans comparés, gestes écartés un à un).

**Trouver de la lumière dans le noir.** Diagnostic (mine, nuits de 11 h, graines 1985, 7, 42, 2024 ;
le poêle meurt vers la minute 450) : la dernière flamme est le briquet de Gaspard ; ceux qui craignent
le noir connaissent les lampes de rechange de la réserve, pas toujours où est Gaspard. Deux gestes
manquaient. *Chercher qui porte ce qu'il faut* : une part se cherchait chez son propriétaire perdu de
vue, pas un objet ; désormais, quand le but l'emploie lui-même (ce que le but vise, ou une source ou
une flamme pour avoir de la lumière, `Vue.moyen_du_but`), on va chercher son porteur et on l'appelle
là où on ne le voit pas (`_chercher`, `pnj.appeler`) ; la suite se décide sur ce qu'on a trouvé.
*Demander du feu* (`demander_feu`, geste social, `echanges.demander_feu`) : on tend sa source (en main,
chargée, qu'on peut employer sans faute) à qui porte une flamme là où l'on se tient ; il l'y allume
sans rien prêter ni donner, sauf méfiance ou voix inconnue (`accueil`) ; coût 1 + `DEMANDE`, sans
jet ; un refus se retient pour cette source ; la lampe allumée ainsi se ménage ensuite
(`flamme_employee`). Une lampe d'autrui qui l'éclaire ne se prête pas (`echanges.necessaire`) : la
lui demander restait vain ; le feu, lui, se partage. Chercher le porteur n'est offert que pour les
moyens du but : l'offrir aussi pour un feu ou un repas faisait atteindre la borne de nœuds aux
recherches `feu` de l'auberge (Mireille, Odile : nœuds × 2 à 3) sans les servir.
Auberge : Lucien dans le noir (graine 7, minute 390) a des plans de lumière (le couloir éclairé) ;
il les endure : rester au grenier lui coûte 3,5 par minute (noir 1,5, `GARDE` 2), partir 4 (le
grenier et la chambre du ballot qu'il convoite) ; la seule lampe portable qu'il connaît est à Hugues,
qui se méfie de lui. Rien à corriger là, sinon ce qu'il sait.

**La lumière devant une serrure** (`deliberation.apport_cru`, `sources_posees_crues`). Constatée devant
l'objet, la croyance `lumiere` retient aussi les sources qu'il croyait alors allumées et posées dans
la salle (`allumees`). De loin, une source qu'il croit allumée et posée dans cette salle, absente de
cette liste (allumée ou posée depuis), y ajoute ce qu'elle donne à la distance qu'il croit entre elles
(portée, `perception.PORTEES`), sans ce qui ferait ombre : devant, il le constate
(`pnj._assez_de_lumiere`), et la source entre alors dans la liste (pas de boucle). `_entrees` lit cet
apport. La lueur diffuse par case : le moteur lui-même ne la connaît que par salle
(`CarteLumiere.ambiance`, « communs à toutes les cases d'une salle ») ; la croyance l'égale déjà.

**L'échange compte l'éloignement** (Gorm et les planches). Diagnostic (Relais, graine 42, minute 149,
réserve forcée, biens pressants) : sur `main`, acheter une part à Aubin coûtait 5,66 (aller au refuge
1, acheter 1 + `DEMANDE` + 0,66), aller chercher ses fagots 15 (4 minutes loin du refuge, `GARDE` 2 et
noir 1,5 par minute) ; sans `GARDE`, 5,66 contre 7 : `GARDE` n'était pas seul en cause. Le plan
d'échange s'arrêtait à l'achat, au refuge, la part tenue pour servie ; or Gorm retournait ensuite
attendre près du brasero, loin de ses biens (minute 151), et ce temps n'était compté nulle part
(l'attente d'une part promise valait 0 minute). Règle commune : promise ou vendue, une part n'est pas
acquise ; elle s'attend là où elle se sert (le feu qu'elle entretient, les vivres), et ce temps compte
comme tout autre, avec ce qu'il y laisse monter (`Vue.attente_part` : que le donneur aille d'où on le
croit jusqu'à la part, la prenne s'il faut la porter, vienne la servir, moins le chemin qu'on a fait
soi-même depuis la promesse). La demander ou l'acheter ne s'explore que si, servie là, elle atteint le
but (comme `TERMINAUX`). Même minute : acheter 16,16, ses fagots 15 (sans `GARDE` : 10,16 contre 7).
Une minute plus tard, le brasero mort, l'achat (Aubin apporte aussi la flamme) redevient moins cher
que les fagots plus une torche à allumer au fanal (16,16 contre 22) : c'est la règle.

**Un gardien ne laisse pas son bien à qui le menace** (`deliberation.menaces`, `gardes`,
`planification.abri`, `appeler_a_l_aide`). Diagnostic (mine, Bram au bureau, lampe en main, biens
non pressants, sécurité pressante, Josse cru au baraquement éclairé) : sur `main`, quand Odon, dont
il se méfie, est au bureau, l'abri gagne « quitter qui l'inquiète » (méfiance) plus la compagnie, et
rien ne coûte l'éloignement (`GARDE` ne vaut que quand les biens pressent) : Bram part au baraquement
et laisse Odon avec la paie. (Ses biens pressants, l'abri atteignait la borne de nœuds et rendait
None : il restait, mais par accident.) Règles : un bien dont il a la charge (le sien, ou confié : y
toucher n'est pas une faute ; pas ce qu'il convoite) est *menacé* là où il croit quelqu'un dont il se
méfie ; s'éloigner d'un lieu menacé coûte `GARDE` à tout plan, biens pressants ou non ; quitter qui
l'inquiète n'est pas un gain de l'abri quand cette présence menace ce qu'il garde là ; près de son
bien menacé, il appelle à l'aide dès que sa sécurité presse, si sa crainte l'emporte sur son courage
(`voix.prudent`) ; plus courageux, il reste et surveille. Le protecteur accourt (Josse pour Bram), et
le voleur, vu, renonce.

Cas vérifiés après rechargement (`tests/test_lumiere_garde.py`) :
- mine, le camp éteint (cas réel) : Rémy prend une lampe de rechange, appelle Gaspard, le rejoint et
  lui demande du feu ; le briquet reste à Gaspard (sur `main` : il va au baraquement, qu'il croyait
  éclairé, et y reste dans le noir) ; auberge (même nature) : Joss, sa lanterne éteinte, trouve les
  foyers morts, appelle Odile et allume sa lanterne à son briquet ; qui se méfie refuse, et le refus
  se retient ;
- Odon compte la chandelle rallumée à trois pas du coffre (pénombre), et non ce qu'il savait déjà
  allumé ; Brune compte la torche posée près de la réserve (pleine lumière, son plan la porte) ;
- Gorm (Relais 42, cas réel) prend ses fagots et recharge le brasero, les planches d'Aubin restent
  entières ; Brune attend sa part promise près des vivres, ce temps est compté (le refuge noir le
  renchérit), et Gorm la sert ;
- Bram reste au bureau, appelle à l'aide, Josse accourt, la paie reste au coffre ; plus courageux
  (90), il reste sans appeler ; Gorm au refuge ne laisse pas sa réserve à Brune (sur `main`, il allait
  s'abriter près d'Aubin) ; Brune ailleurs, il va s'abriter.
Tests changés et pourquoi : `test_planification` (le plan d'une part demandée mène attendre près des
vivres) ; `test_constater_rumeurs` (le baraquement noir : la lampe de Josse vide, sinon il demande du
feu et rallume le poêle ; la réserve noire : Odon honnête, car demander puis attendre sa part dans le
baraquement noir lui coûte un peu plus que forcer le garde-manger, 10,5 contre 9,95 ; la scène, qui sert
aussi à `tests/test_voix_inconnues.py`, éprouve ainsi le jugement d'une demande venue d'une voix).

`VERIFIER` passe sur une nuit de 8 h (graine 42) de chaque scénario.

Bancs 8 h, `main` 888bbc4 (avec la seule mesure `minutes_dans_le_noir` ajoutée) et la branche lancés au
même moment (Relais 8 graines, joueur à la galerie ; mine, auberge et crue 4 ; départ tiré ; moyennes
par nuit, `main` → branche) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| sans recours | 53,1 → 53,8 | 58,8 → 55 | 15 → 43,8 | 15 → 15 |
| en attente | 63,1 → 66,3 | 290 → 281,3 | 536,3 → 541,3 | 88,8 → 107,5 |
| confiées | 159,4 → 188,8 | 0 → 0 | 0 → 0 | 267,5 → 290 |
| événements distincts | 33 → 30,8 | 48,5 → 50,8 | 50,3 → 52 | 33,8 → 35,8 |
| échanges | 11,1 → 10,3 | 30 → 30,5 | 25,8 → 28,3 | 10,3 → 10 |
| achats | 2 → 2 | 1,5 → 1,5 | 2,3 → 2,5 | 2,5 → 2,5 |
| vols vus | 1 → 0,9 | 0,75 → 1 | 0,5 → 0,5 | 0,25 → 0 |
| minutes dans le noir (qui le craint) | 9,4 → 5 | 282,5 → 270 | 1303,8 → 1276,3 | 8,8 → 8,8 |
| appels (chercher quelqu'un) | 2 → 1,1 | 2,75 → 2,75 | 3,5 → 6,75 | 2,25 → 2,5 |
| appels à l'aide (total des nuits) | 2 → 3 | 11 → 12 | 4 → 9 | 0 → 0 |
| usurpations, violations | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| nuits distinctes (5/60/120/240/480 min, issues) | 8 partout → 8 partout | 4 → 4 | 4 → 4 | 4 → 4 |
| temps d'une nuit | 22,8 → 20,2 s | 89,9 → 96,1 s | 96,1 → 82,7 s | 18,3 → 19,5 s |

Mine prolongée à 11 h (le camp s'éteint vers 450 ; 4 graines, lancées ensemble) : appels à l'aide
192 → 96, minutes dans le noir 812,5 → 696,3 par nuit, 2 feux demandés (Rémy à la minute 489 au lieu
de 581 en 1985 ; à 477 en 7, après un briquet refusé) ; en 2024, Gaspard rallume le poêle à 466 (sur
`main`, à 541).

Écarts expliqués :
- Gorm : dans les trois nuits du Relais où ses biens le pressent quand le brasero baisse (7, 42,
  2024), il achetait une part des planches (minutes 123, 150, 111) ; il va désormais prendre ses
  fagots, et n'achète que son bois épuisé (346 à 356), comme dans les autres nuits. Graine 500
  (minute 239), il essaie encore d'acheter (refusé : Aubin garde ses planches) : l'achat l'éloigne
  2 minutes de ses biens, ses fagots 4 (11,66 contre 12, `GARDE` compté des deux côtés) ;
- le plan d'une part promise mène attendre là où elle se sert : le demandeur y va aussitôt, et non
  plus à la minute suivante ; les nuits se décalent dès la première part (Relais 11 : Brune rejoint
  le refuge avant Gorm). D'où des écarts sans cause propre : les minutes « confiées » (le devoir de
  Gorm, la cloche confiée au joueur) au Relais et à la crue, moins d'événements au Relais ;
- auberge : la menace sur le bien fait appeler à l'aide Lucien (son coffret, Hugues présent) et
  Anselme (son ballot, Lucien présent) quand leur sécurité presse et l'emporte sur leur courage (4 → 9
  appels à l'aide sur quatre nuits) ; ces appels font aller voir (29,8 → 39,8 par nuit) et mettent des
  témoins sous les yeux de Lucien, qui renonce plus souvent à son vol (sans recours 15 → 43,8 :
  l'heure qui suit un renoncement). Anselme, volé, cherche Lucien pour reprendre son ballot (appels
  3,5 → 6,75) ;
- mine : le feu demandé n'apparaît qu'en fin de nuit ; les nuits de 8 h changent peu. Temps : mine
  +7 %, auberge −14 %, Relais −11 % (des nuits différentes) ; sur des états identiques de la mine et
  de l'auberge (minutes 120, 240, 360, graine 7), la délibération de tous coûte 1,17 → 1,73 s, surtout
  Lucien, à la mine, qui trouve un plan de lumière là où il endurait.

Limites :
- chercher le porteur n'est offert que pour la lumière et ce que le but vise : pour un feu, on ne
  cherche que le propriétaire d'une part de bois, pas qui porte une flamme ; Josse, poêle mort, ne
  retrouve pas Gaspard pour le briquet (il le demande s'il le sait là) ;
- demander du feu suppose sa source en main : on ne fait pas allumer une source fixe (un poêle) par
  qui porte une flamme ; rejoindre qui porte une lampe n'est ni un abri ni une lumière (elle suit son
  porteur) ;
- l'apport d'une source devant une serrure ignore ce qui ferait ombre ; il se constate devant ; une
  ancienne croyance `lumiere` sans `allumees` compte une fois toutes les sources crues allumées ;
- l'attente d'une part est une estimation (chemins crus, un geste pour servir) : le donneur peut
  tarder (aller d'abord chercher une flamme) ; l'achat et la marche restent comparés de près
  (Relais 500) ;
- la menace sur le bien se juge sur où il croit les autres, et ne fait appeler qu'en sa présence ; un
  voleur qui garde aussi ses propres biens (Lucien) appelle à l'aide comme un autre ; on ne chasse ni
  n'affronte qui menace ;
- qui ne répond pas à un chercheur qu'il reconnaît et dont il se méfie lui fait parcourir une salle
  par minute (Anselme cherchant Lucien), comme pour une part.

## Coût de calcul (branche `planif-cout`)

Les branches `besoins` et `petits-correctifs-pnj` avaient alourdi les nuits (auberge +13 %, mine
+20 %). Rien n'est changé à ce que décident les PNJ : seulement ce que coûte de le calculer, nuits
strictement identiques à `main`.

**Points chauds** (profil `cProfile` d'une nuit de chaque scénario et `--diagnostic`) :
- des recherches refaites à chaque minute sans reprise par la mémoire, alors que seul le prix d'une
  faute ou celui d'abîmer avait changé avec la détresse : à l'auberge, Lucien au grenier noir
  (`garder`, ~580 nœuds ; `faim`, ~1 000 nœuds, épuisée ; puis `placer:ballot`) ; à la mine, Odon
  (`faim`, la faute) et Rémy (`faim`, le prix d'abîmer). Les seules recherches de Lucien faisaient
  près des deux tiers d'une nuit de l'auberge (graine 1985, départ tiré) ;
- la vue du planificateur (`Vue`) construite ~10 000 fois par nuit à l'auberge, dont 6 000 par
  `enrichir` et `reclamer` qui n'avaient rien à chercher ; les gardes confiées relues pour chaque
  objet (`biens.gardes`) ; un parcours des salles refait pour chaque arrivée (`pnj.chemin`) ;
- la perception de tous (`esprits.percevoir_tous`) recalculait l'empreinte de l'état
  (`spatial.etat_vue`) pour chaque PNJ ; un trajet relisait tous les objets pour chaque case essayée
  (`spatial._bloque`) et levait une exception par pas refusé ; la copie de travail du moteur
  (`Monde.copier`) passait par `copy.deepcopy` ;
- reste : des recherches neuves, sur des entrées qui ont vraiment changé, jusqu'à la borne de 4 000
  nœuds (la mine, graine 7, en fin de nuit : Josse, `faim` et `feu:poele`, à chaque minute où sa
  croyance sur la place d'un autre change), environ 100 µs par état développé.

**Le graphe repris** (`planification._GRAPHES`, `_explorer`, `_suites`). Une recherche garde, pour
chaque état développé, s'il atteint le but, ce qu'il laisse monter (`pression`) et ses gestes avec
chaque terme de leur coût (fautes, minutes, durée, abîme, pression de l'état suivant). Ces termes ne
dépendent que de ce que lit la recherche (`_entrees`, l'adresse et la force modulées, `tenir`, et
s'il envisage d'abîmer) ; le prix d'une faute et celui d'abîmer n'entrent que dans la somme que fait
`_explorer`, la même expression, dans le même ordre, sur les mêmes nombres. Quand seuls ces deux prix
ont changé, la recherche se refait sur le graphe gardé : mêmes additions en virgule flottante, mêmes
comparaisons et mêmes égalités départagées par l'ordre de découverte, donc le même résultat qu'une
recherche complète, sans recalculer un seul geste ; un état que la nouvelle recherche atteint pour la
première fois est développé à la demande. Le graphe n'est gardé qu'à la deuxième recherche de suite
sur les mêmes entrées (les buts dont les entrées changent à chaque fois n'encombrent pas la mémoire).
Un élagage par borne (A*) reste écarté : il changerait l'ordre entre plans de même coût. Pour que le
graphe reste juste, `gestes` ne doit lire ni le prix d'une faute ni celui d'abîmer (le geste qui
abîme rend un indicateur, `_explorer` y met `Vue.degat`) ; `VERIFIER` refait chaque recherche reprise.

**Lectures moins chères**, au même résultat :
- la vue : les gardes confiées lues une fois par propriétaire (`biens.permis(confies=…)`), `autorise`
  tiré de `illicite` déjà jugé ; aucune vue pour `enrichir` sans pièces crues ni pour `reclamer` sans
  créance, ni dans `planifier_pulsion` avant qu'un plan soit trouvé ;
- les gestes : un parcours des salles par départ, clés et portes crochetées (`pnj.parcours`), valable
  pour toutes les arrivées, et les trajets d'une salle relevés une fois (`Vue.allers`) ; les objets
  sans geste possible écartés une fois (`Vue.agissables`) ; un objet qu'il ne porte pas et qu'il croit
  dans une autre salle n'offre qu'une part (`_parts`) ; ce qu'un état laisse monter, une fois par état ;
  le besoin d'une part par objet, ce qu'il porte pour l'apaiser, les refus et promesses lus sans
  fonction construite à chaque lecture ; l'état d'un plan comparé et haché comme le tuple qu'il est
  (`Etat`) ; la clé de la mémoire sans réencoder les entrées ;
- hors du planificateur : la perception de tous sur un état lu une fois (`etat_fige` autour de la
  boucle, ce que `spatial.VERIFICATION` contrôle) ; les obstacles d'une salle relevés une fois par
  trajet (`spatial._bloquantes`) ; le pas sans exception dans la recherche d'un trajet
  (`spatial._pas`) ; la copie de travail par `monde.copie` (même résultat que `copy.deepcopy`,
  partages compris) ; un esprit ne construit un champ par défaut que s'il manque ; des imports de
  fonctions très appelées faits une fois.

**Preuve d'identité.** Pour chaque nuit, `main` (888bbc4) et la branche : empreinte de la chronique,
des mesures, de l'état final complet (`monde.data`), du récit, des empreintes du banc (minutes 5,
60, 120, 240, 480 et issue), nombre de recherches et de nœuds examinés. Tout est identique sur 32 nuits (4 scénarios × graines
1985, 7, 42 et 2024 × départ tiré et fixe), puis de nouveau sur les 16 nuits tirées d'une seconde
passe.
`VERIFIER` (chaque résultat repris de la mémoire, du graphe ou cherché parmi ce qu'il vaut la peine de
porter, refait par une recherche complète) et `spatial.VERIFICATION` (chaque lecture mémorisée de la
perception recomparée, l'état d'un bloc figé contrôlé) passent sur 16 nuits (4 scénarios × graines 42 et 7 × départ tiré et fixe). Cas réels après
rechargement (`tests/test_planif_cout.py`) : Lucien au grenier noir (le graphe gardé à la deuxième
recherche, repris à la troisième, égal à une recherche complète ; 30 minutes de vie, même monde avec
ou sans graphe) et, de même nature, Odon affamé à la mine (même monde avec ou sans graphe).

Temps d'une nuit de 8 h au processeur (`process_time`), moyenne par nuit, `main` → branche, lancés
ensemble, 8 processus à la fois sur une machine que d'autres travaux chargeaient aussi (16 fils) ;
départ tiré : 4 graines, 2 passes ; départ fixe : 1 passe. Entre parenthèses, le planificateur (somme
des durées des recherches, `--diagnostic`) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| départ tiré | 14,5 → 9,2 s (4 → 1,4) | 57,3 → 31,7 s (33,7 → 14,9) | 62 → 26,4 s (36,2 → 9,4) | 15,3 → 10,5 s (3,2 → 1,8) |
| départ fixe | 16,2 → 9,9 s (4,9 → 1,9) | 44,2 → 27,6 s (19 → 10,3) | 54,1 → 25,4 s (29,1 → 9,3) | 15,4 → 10,8 s (2,1 → 1,3) |
| rapport (tiré) | × 1,58 | × 1,81 | × 2,35 | × 1,45 |

Le planificateur passe de 58 % à 36 % d'une nuit à l'auberge, de 59 % à 47 % à la mine. Les valeurs
absolues dépendent de la charge (à 4 processus, graine 42 : auberge 44,1 → 19,6 s, mine 49,5 →
24,5 s) ; les rapports restent. Nuit la plus lourde, la mine graine 7 (départ tiré, 2 passes) :
70 → 43,4 s, dont le planificateur 44,3 → 24,7 s, presque tout en recherches neuves (ci-dessous).

**Après fusion de `main` 5861f71** (`pnj-lumiere-garde` et ses nouvelles lectures : `moyen_du_but`, le
porteur à chercher, `demander_feu`, la part promise attendue, `apport_cru` dans `_entrees`, `GARDE`
sur un bien menacé). La part promise passe dans `_parts` ; un objet cru dans une autre salle n'offre
toujours qu'une part (chercher son porteur suppose de ne pas savoir où il est, demander du feu suppose
de porter la source) ; `gestes` ne lit toujours ni le prix d'une faute ni celui d'abîmer (seulement
s'il envisage d'abîmer, dans la clé du graphe). Preuve refaite contre ce `main` : empreintes
identiques sur 32 nuits (4 scénarios × 4 graines, départ tiré et fixe), `VERIFIER` et
`spatial.VERIFICATION` sur une nuit de chaque scénario (graine 42). Temps au processeur, priorité
réduite, 4 processus au plus (2 graines par côté à la fois), `main` → branche :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| départ tiré | 11,7 → 7,2 s (3 → 1,2) | 70 → 39,5 s (43,2 → 19,6) | 47,3 → 24,2 s (22,4 → 8) | 12,6 → 9 s (2,9 → 1,7) |
| départ fixe | 11,7 → 7,6 s (3,1 → 1,2) | 36,5 → 24,7 s (16,7 → 10) | 42,8 → 22,3 s (22 → 8,6) | 15,2 → 10,6 s (4,4 → 2,4) |
| rapport (tiré) | × 1,63 | × 1,77 | × 1,95 | × 1,40 |

Limites :
- une recherche neuve coûte toujours ~100 µs par état développé : la mine, graine 7, en fin de nuit,
  refait à chaque minute deux recherches de 4 000 nœuds pour Josse (sa croyance sur la place d'un
  autre change) ; aucune reprise partielle n'est sûre, presque chaque geste (une part, une demande)
  lisant la place des autres ;
- le graphe n'est repris que si seuls le prix d'une faute ou celui d'abîmer ont changé ; une croyance
  nouvelle, même sans rapport avec le but, refait tout. Toute lecture nouvelle de la recherche entre
  dans `_entrees` (comme avant) et `gestes` ne lit pas ces deux prix ;
- mémoire : les graphes gardés (un par PNJ et par but, remplacé quand les entrées changent) ;
  à la mine (graine 7) la fin de nuit est égale à `main`, le pic passe de 30 à 59 Mo ;
- la perception reste le plus gros poste hors du planificateur (un tiers d'une nuit) : chaque PNJ
  revoit tout ce qu'il croit après chaque événement.

## Coût de calcul, suite (branche `cout-calcul`)

Les nuits avaient de nouveau ralenti avec la délibération à l'événement et le temps réel. Même règle
que `planif-cout` : rien ne change dans ce que décident les PNJ, seulement ce que coûte de le calculer.
Rapport complet : `docs/taches/rapport-cout-calcul.md`.

**Mesurer.** Un profil `cProfile` grossit cinq à six fois les fonctions à appels très nombreux ; les
parts se lisent sur un échantillonnage (`py-spy`). Sur `main`, une nuit de 8 h passait 19 à 57 % dans
le choix du but (dont 7 à 45 % de recherches neuves), 16 à 27 % dans la perception, 13 à 28 % dans les
gestes et la marche, 6 à 16 % dans l'ouïe, et 5 à 8 % à calculer l'empreinte de l'état (`etat_vue`) :
22 978 fois dans une nuit de la mine pour 1 550 états distincts. PyPy fait les mêmes nuits mais 1,5 à
1,7 fois plus lentement, avec trois fois plus de mémoire : écarté.

**Reprendre le choix entier : non retenu.** Les entrées d'un choix (même abstraites : besoins
pressants, prix d'une faute, caractéristiques modulées, valeurs des croyances) ne sont les mêmes
qu'au choix précédent du même PNJ que dans 1 à 12 % des cas, et ce sont les choix les moins chers
(0,02 à 0,25 s par nuit), alors que la clé coûte autant que le choix. Reprendre une recherche neuve sur
les seules croyances qu'elle a lues ne vaut pas mieux : la plupart les lisent toutes.

**Ce qui est fait** (chaque reprise ou lecture gardée a son contrôle : `spatial.VERIFICATION` recompare
la lecture gardée à un calcul de zéro ; `planification.VERIFIER` reste celui des recherches) :
- *Perception incrémentale* (`esprits._percus_depuis`). Dans un état nouveau, ce que perçoit un PNJ se
  tire de sa perception précédente quand seuls ont changé des objets qui ne bornent pas la vue (ni porte
  ni objet opaque), pas lui, et que son champ est le même : seuls sont revus les objets changés (la
  différence des deux empreintes `etat_vue`, objet par objet), ce qu'ils portent ou contiennent (la
  chaîne de leurs lieux) et les objets installés sur un support, par le même test que le calcul complet
  (`_vu_dans_le_champ`) ; le reste se voit de même, dans l'ordre exact d'un calcul complet. Deux
  perceptions sur trois passent par là. Le mémo d'un état garde son empreinte ; la différence de deux
  empreintes et les chaînes de lieux se calculent une fois par état et se partagent entre PNJ.
- *Signatures de la vue héritées* (`esprits._heriter_signatures`, `memo["signatures"]`) : quand aucun
  objet changé, ni rien de ce qu'il porte ou contient, n'est allumé ni opaque et qu'aucun n'a changé
  d'ouverture, l'état nouveau partage les signatures de chaque salle du précédent.
- *Lectures de l'état figé* : le regard d'un acteur (`spatial._vue`) et la lumière de sa case
  (`esprits.lumiere_ici`) sont gardés dans le mémo de l'état ; percevoir, témoigner, relever ce que voit
  le joueur et noter le temps vécu d'un geste (`pnj._avancer`) se font dans un seul état figé, comme le
  relevé des présences : l'empreinte n'est plus recalculée entre des lectures que rien ne sépare. Une
  lecture seule (`vecu.conditions` hors de ce bloc) reste sans état figé : l'empreinte y coûterait plus
  que ce qu'elle ferait retrouver (mesuré).
- *Pas et passages gardés* : un pas d'une case dans un sens (`spatial._pas_possibles`) ne dépend que de
  la géométrie, des obstacles solides et des portes ouvertes ou fermées ; les passages de l'ouïe
  (`ouie._passages`), de la géométrie, des portes et des appuis verticaux : gardés sous ces clés d'un
  trajet ou d'un bruit à l'autre.
- *Le planificateur* : `enrichir` juge les bourses crues sans construire la vue ; la vue juge prendre,
  consommer et abîmer le bien d'autrui en un seul calcul du propriétaire (`biens.leses`) ; les tests de
  but (`a_mange`, `rechauffe`) ne trient plus les faits ; `Etat.apres` reprend les faits de l'état
  quand un geste n'en ajoute aucun ; `_suites` ne cherche un fait terminal nouveau que si l'état
  suivant a plus de faits ; flammes fixes et flammes d'autrui lues une fois par état ; le lieu cru dans
  un dictionnaire dédié (`Vue._lieu`) ; l'utilité d'une part ne se juge que si son donneur se tient là ;
  la clé de la mémoire encodée sans contrôle de cycles.
- *Ce que le joueur saisit des paroles* : un terme absent du texte n'est pas cherché par son motif, une
  seule passe (`lexique`) ; ce que nomme le contexte du joueur n'est calculé qu'une fois dans un bloc de
  lecture (`paroles.contexte_fige`, `ecoute.lier` et `ecoute.rendre`).
- *Menus* : `esprits.esprit` ne complète ses champs que s'il en manque ; `Monde.objets` et
  `Monde.joueur` sont des attributs remis à jour à chaque affectation de `data` ; des imports faits une
  fois.

**Preuve d'identité.** Pour chaque nuit, `main` 06602a6 et la branche (`tools/empreintes_nuits.py`) :
empreintes de la chronique, des mesures, du récit, des souvenirs, de l'état final complet, des repères
du banc et des recherches neuves (PNJ, but, nœuds, issue). Identiques sur 32 nuits (4 scénarios ×
graines 1985, 7, 42, 2024 × départ tiré et fixe, 8 h), puis dans chaque passe de mesure ; de même avec
`tools/comparer_bancs.py --empreintes` (Codex, `origin/codex-outils`). `VERIFIER` et
`spatial.VERIFICATION` à 0,2 sur une nuit de 8 h de chaque scénario (graine 42) ; `VERIFICATION` à 1 sur
deux heures de chaque scénario après chaque changement de la perception : sans écart.

Temps d'une nuit de 8 h au processeur, `main` → branche, lancés ensemble (2 processus de chaque côté) ;
départ tiré : 4 graines, 2 passes ; départ fixe : 1 passe. Entre parenthèses, le planificateur :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| départ tiré | 8,9 → 6,4 s (2,4 → 2,2) | 23,7 → 18,8 s (13,1 → 10,9) | 16,2 → 12,6 s (4,9 → 4,0) | 7,7 → 5,8 s (1,4 → 1,2) |
| départ fixe | 6,8 → 4,6 s (1,4 → 1,1) | 23,6 → 19,6 s (14,3 → 12,4) | 15,9 → 12,6 s (4,8 → 4,2) | 8,9 → 6,9 s (1,6 → 1,5) |
| rapport (tiré) | × 1,39 | × 1,26 | × 1,29 | × 1,33 |

Pic de mémoire : Relais 43 → 42 Mo, mine 91 → 83 Mo, auberge 85 → 77 Mo, crue 46 → 47 Mo.

Limites :
- un PNJ qui bouge ou se tourne revoit tout (son champ change) : un tiers des perceptions ;
- l'empreinte de l'état se calcule encore à chaque lecture hors d'un état figé : sans suivi des
  écritures (des centaines de points du moteur écrivent dans les objets), rien ne dit à moindre coût
  que l'état n'a pas changé ;
- les recherches neuves coûtent toujours ce qu'elles coûtaient par état développé, à peu près : la mine
  reste dominée par elles (Rémy, Josse et Mathe refont chaque minute des recherches épuisées, Lucien à
  l'auberge des recherches de quelque 380 nœuds) ;
- toute lecture nouvelle de la perception doit rester couverte par `spatial.etat_vue` (comme avant) ;
  une lecture de la perception qui dépendrait d'un autre objet que ceux de la chaîne de ses lieux ou de
  son support devrait entrer dans `_percus_depuis`.

### Suite sur `main` a7ecb50 — branche `codex-cout-suite`, fusionnée

Les absences de plan ne se reprennent pas sur le seul fait que le prix d'une faute change.
La recherche pondérée garde le meilleur coût par état, pas par couple (état, profondeur) : un
chemin moins cher mais plus long peut empêcher de développer un chemin court qui atteindrait le
but. Même un espace annoncé « épuisé » n'est donc pas une preuve indépendante des prix ; une
borne de 4 000 nœuds l'est encore moins. Le contre-exemple est testé dans `test_cout_suite.py`.

`_sans_plan` parcourt en largeur le graphe déjà développé, à profondeur minimale par état,
avec les permissions de gestes inchangées. Il ne conclut à l'impossibilité que si tous les chemins
autorisés jusqu'à `PROFONDEUR` sont couverts et n'atteignent aucun but. Une lacune, un but ou le
plafond du certificat font reprendre le calcul habituel. Il ne développe aucun geste supplémentaire :
une première version qui complétait le graphe coûtait autant qu'elle économisait, avec davantage
de mémoire. Le certificat garde toutes les entrées structurelles, la profondeur et la permission
de faute ; seuls les prix peuvent varier. Chaque reprise est recalculée exactement par `VERIFIER`.
Une seule dernière preuve par PNJ et but ; le graphe volumineux est libéré lorsqu'elle suffit.

Accord avec les deux graphes de la lumière employée (fusion après `codex-lampes-suite`) : le graphe
repris en garde deux, `sombre` et `lumiere` (« Lumière employée », plus bas). Qui emploie la lumière
dès le départ (coût du noir, lumière comme but) cherche sur `lumiere`, et la preuve s'y fait. Sinon la
recherche jouée passe d'abord sur `sombre` ; un état dont l'examen y a lu la lumière (son but, ou ses
gestes quand il les développe : le cinquième terme du nœud) la fait reprendre depuis le départ sur
`lumiere`, et c'est cette reprise qui décide. Le parcours de `sombre` ne suit pas un tel état et le
signale (`_parcours`) : atteignable à sa profondeur minimale, un autre prix d'une faute peut l'y faire
examiner, et l'absence n'est prouvée que si le parcours de `lumiere` la prouve aussi (une lacune s'il
n'a pas été développé). Sans cette règle, le parcours du seul graphe sombre concluait à l'absence
alors qu'à faute bon marché la reprise avec lumière trouve un plan (`VERIFIER` l'arrête :
`test_recherche_epuisee_dans_le_noir_que_la_lumiere_reprendrait_n_est_pas_prouvee`). Le plafond
`PREUVE_MAX` compte les deux parcours ensemble.

Les dates de visites ne servent dans `_chercher` qu'à classer les destinations, avant la longueur
du trajet et le nom de salle. La clé garde donc leur ordre avec toutes les égalités, y compris la
date implicite −1, plutôt que les dates absolues. Croyances, refus et moyens restent dans la clé :
leurs changements sont réels, même si deux explorations successives échouent.

`spatial.etat_vue` partage désormais les signatures des objets inchangés. Des copies de leurs
dictionnaires isolent les valeurs composées lues par la vue et les positions ; les autres données
restent des références. Une comparaison des dictionnaires en C permet de partager la liste entière
des signatures lorsque rien n'a changé. L'ordre des objets et le texte des propriétés composées
restent contrôlés séparément. Les écritures ordinaires, y compris les mutations en place, sont
conservées ; aucune instrumentation des objets sauvegardés. Une empreinte identique reprend
également directement le mémo courant sans rehacher son contenu. `spatial.VERIFICATION` compare
l'empreinte à la construction complète, en plus des contrôles existants de perception.

`tools/empreintes_nuits.py comparer --calcul` compare tous les résultats des recherches logiques
(coût exact, étapes, état final ou absence), dans leur ordre, ainsi que toutes les empreintes de
nuit. Les comptes de recherches effectivement calculées peuvent différer : c'est l'économie visée.
Le mode strict antérieur reste disponible. Un résultat logique, une empreinte ou une nuit manquants
font échouer le contrôle.

Mesures, contrôles et limites : [rapport Codex 10](taches/rapport-codex-10-cout-suite.md).
Après fusion de a7ecb50 : 32 nuits de 8 h et quatre nuits de 12 h de l'auberge identiques,
y compris les résultats de chaque recherche. CPU total des 32 nuits 453,03 → 439,51 s
(−3,0 %), quatre calculs lourds au plus ; auberge 12 h 86,85 → 84,66 s/nuit. La première
mesure sur 9075aea reste documentée dans le rapport. Suite après fusion : 1 431 tests,
quatre sautés, six échecs MiMo préexistants.
Les six échecs sont reproduits à l'identique sur a7ecb50 ; 39 tests ciblés passent.
`VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h de chaque scénario
(graine 42) : sans écart, nuits identiques.

La piste de dominance de dépense (mêmes faits et moyens, coût strictement plus faible,
dépense et profondeur au plus égales) a été contre-vérifiée hors du moteur. Elle change
deux recherches de Lucien à l'auberge : la référence atteint 4 000 nœuds sans plan, le
prototype en trouve un avant la borne. Retirer un état dominé peut conserver l'optimum
illimité tout en changeant cette réponse bornée ; un contre-exemple général et deux
sauvegardes réelles le testent. Cette règle n'est donc pas livrée. `_parts_remises`
n'est ni retiré ni restreint, et l'espace de la recherche jouée n'est pas modifié.
La perception complète de qui bouge n'est pas modifiée : son poids mesuré ne justifie pas de
complexifier ce contrat. La reprise des grosses recherches bornées de la mine reste une limite
explicite ; ce chantier ne change ni les limites ni le choix des plans.

## VERIFIER et l'eau (branche `verifier-eau`)

Deux défauts de l'audit des nuits (`docs/audit-nuits.md`, V1 et A4).

**Une recherche restreinte n'explore qu'une partie de la complète.** `emplois` dit ce qu'il vaut la
peine de porter ; il ne doit que retirer. Or `Vue.moyen_du_but` (chercher qui porte une source ou une
flamme) et le `superflu` des flammes (`lumiere_compte`) lisaient `"lumiere" in emplois` : la recherche
de référence de `VERIFIER`, sans `emplois`, n'offrait pas ces gestes, et la restreinte trouvait des plans
qu'elle ne connaissait pas (70 des 108 écarts de l'audit ; même défaut dans `test_lumiere`, révélé à la
fusion de `ouie-temoins`). Règle : ce que le but demande lui-même se lit du but. `eclairer` passe
`vises={"eclairer": True}` (comme `vises` ouvre déjà les gestes propres à un but), d'où `Vue.eclairer`,
que lisent `moyen_du_but`, `pertinent` et `gestes` ; `emplois` ne garde que « manger » et « feu », qui ne
font que borner `pertinent`. Les nuits n'en changent pas (empreintes identiques sur 8 nuits de chaque
scénario, VERIFIER désactivé).

**La référence de `VERIFIER`** (`_verifier`) : deux contrôles, chacun avec sa référence.
- Un résultat repris de la mémoire ou du graphe doit être exactement (plan et égalités compris) celui
  d'une recherche refaite de zéro avec les mêmes paramètres (même `emplois`, même borne).
- Un résultat cherché avec `emplois` doit avoir le coût de la recherche complète du même but (`emplois`
  à None, même `Vue.eclairer`), bornée à `REFERENCE` (15 × `NOEUDS`, 60 000 nœuds) et non plus à la
  borne de ce qu'elle contrôle : la complète examine plus d'états, elle atteignait 4 000 nœuds avant
  l'optimum (15 faux écarts). Le coût, pas le plan : les deux recherches n'examinent pas les mêmes
  gestes, l'ordre de découverte qui départage deux plans de même coût diffère donc nécessairement
  (21 écarts « même coût, étapes différentes ») ; rendre cet ordre commun demanderait une clé de
  départage sur les étapes, qui changerait toutes les nuits sans rien apprendre au contrôle. Coûts égaux
  à l'arrondi des sommes près (1e-9 relatif). Si la complète atteint sa borne, la restreinte doit
  seulement ne pas coûter plus qu'elle.
- Si la recherche jouée atteint sa borne de nœuds, ce n'est pas un défaut de la restriction mais une
  limite de la recherche : l'écart est noté (`planification.BORNES`, `bornes_verifier` de l'audit), pas
  tenu pour faux. La mémoire garde désormais si la recherche avait atteint sa borne.

Les deux « vrais manques » de l'audit (Lucien, la lumière, auberge 3 et 99) ne se rejouent plus ; le cas
de même nature relevé sur `main` 8589ca2 (auberge 99, minute 374 : restreinte sans plan, complète à 98,
demander sa lanterne à Hugues puis l'allumer au couloir) est une recherche jouée arrêtée à 4 000 nœuds :
à 12 400 nœuds, la restreinte trouve le même optimum. La restriction n'écartait rien.

`VERIFIER` (continu, `tools/audit_nuits.py jouer --verifier-continu`) sur 32 nuits de 12 h (4 scénarios
× graines 1985, 7, 42, 2024, 3, 11, 99, 500), après fusion d'`integration` f5cf65f : **0 écart** (avant :
mine 15/16, auberge 11/16) ; 161 recherches jouées bornées reconnues, toutes sans plan là où la complète
en trouve un : Lucien et la lumière (auberge 7, 88 minutes), Josse et le poêle (mine 7 et 11, 64), Odon
et l'argent (mine 99, 8), un abri (auberge 7). Coût du contrôle : une nuit de mine de 12 h passe à 5 à
12 minutes avec `VERIFIER` (référence à 60 000 nœuds), sans effet hors des tests et de l'audit.

**L'eau dans les plans.** Seul l'abri tenait compte de l'eau attendue ; la chaleur, les rondes, le
devoir menaient là où elle monte et d'où le retour serait coupé. L'eau que le PNJ attend dans chaque
salle est `eau.attendue` (celle qu'il y croit, ou plus à la vitesse où il l'a vue monter, d'ici
`eau.HORIZON`) ; la `Vue` en tire les salles menacées (eau attendue) et celles qu'il attend noyées,
entrées de la mémoire (`_entrees`) avec le fait qu'il la voit monter. Quatre règles communes :
- **Ce que coûte l'eau** (`Vue.pression`) : chaque minute dans une salle où il croit l'eau coûte ce
  qu'elle l'inquiète (`deliberation.ressentir` : 2 × taux `eau` × hauteur / 100 cm, ou taux `menace`
  quand il l'y attend), `NOIR` par point, comme le noir à qui le craint ; pour tout plan, à tout état.
- **On ne se tient pas dans l'eau** : un but qui se tient en restant (chaleur, lumière, garde, abri)
  n'est pas atteint dans une salle menacée (`_explorer`) ; on ne s'y chauffe pas (geste `chauffer`), et
  une part de bois ne va pas à un feu d'une salle menacée (`_parts`, qui généralise `feu_noye`) ; si
  chaque foyer qu'il connaît est menacé, la chaleur n'est pas cherchée (`planifier` : aucun plan ne
  l'atteindrait, et la recherche épuisait l'espace à chaque minute, 66 000 nœuds pour Brune en une nuit).
- **On ne descend pas dans la crue** (`Vue.descente`, filtre des trajets `allers` et de `_chercher`) :
  pas d'aller vers une salle où il attend plus d'eau qu'ici (il l'y attend et pas ici ; ou il la voit
  monter et la salle est plus basse, elle monte par le bas) quand il l'y attend noyée ou que son retour
  serait coupé par une salle qu'il attend noyée ; et, tant qu'elle monte, pas d'un lieu relié au plus
  haut lieu qu'il croit pouvoir gagner (par ses chemins, avec ses clés) vers un lieu que l'eau attendue
  en coupera ou noiera (`Vue.piege`), même en deux trajets. Monter, aller vers moins d'eau ou vers un
  lieu d'où l'on revient reste permis, même en traversant l'eau.
- **Piégé, il sort d'abord** (`deliberation.candidats`, `eau.en_peril`) : là où il attend l'eau noyer la
  salle, l'abri passe avant tout ; sans abri hors de l'eau à sa portée, `_plan_abri` le mène au lieu où il
  attend le moins d'eau, éclairé ou non (sans y « rester à l'abri », `pnj._abriter` refusant un lieu
  menacé). Clé, crochetage et forcer viennent des gestes de l'aller, comme avant.

Cas réels et cas de même nature après rechargement (`tests/test_verifier_eau.py`) : Lucien dans la mine
noire cherche Josse et l'appelle, `VERIFIER` actif ; Rémy cherche Gaspard ; une référence bornée n'est
pas un défaut ; crue 500 (Brune ne se chauffe plus sous 88 cm, Gorm ne fait plus sa ronde aux vannes,
personne n'appelle à l'aide ni ne reste dans 50 cm d'eau jusqu'à 360 minutes) ; le même laps de 240
minutes, d'un bloc ou en six blocs rechargés, donne le même monde ; une autre crue (1 cm par minute) :
pas de ronde aux vannes ni de feu dans la conduite qu'on attend noyées, l'eau coûte par minute, Aubin
attardé aux vannes en sort aussitôt. Test changé : `test_eau` (Ilse, rassurée à la galerie, ne fait plus
sa ronde au refuge, qui la couperait de la galerie : son intention peut être finie).

Limites :
- l'eau coûte par la salle d'arrivée, pas par celles qu'on traverse ; la traversée d'une salle qu'on
  attend noyée n'est jugée que par le retour qu'elle couperait ;
- le lieu « relié au plus haut » ignore les portes (une porte verrouillée sans clé n'est pas un
  obstacle pour ce jugement) et le plus haut est la salle de plus haute altitude du scénario ;
- l'eau ne coûte qu'à qui a le besoin de sécurité (comme `ressentir`) ; un PNJ sans ce besoin ne
  descend toujours pas dans la crue ni ne s'y tient (les règles de lieu valent pour tous) ;
- l'horizon reste `HORIZON` (60 min) : au-delà, l'eau n'est pas attendue ; qui ne l'a pas vue monter
  n'attend que celle qu'il voit ; désœuvré dans une eau qui ne menace pas de noyer sa salle, il y reste
  jusqu'à ce que sa sécurité presse ;
- la crue n'a qu'un foyer, dans la conduite : quand elle est menacée, plus personne ne se chauffe, et
  le froid attend (Brune et Aubin, ci-dessous) ; d'autres remèdes au froid restent une question ouverte
  de `docs/plan-crue.md`.

Audit de la crue (12 h, 8 graines, relevés toutes les 5 minutes, `integration` f5cf65f → branche) :
minutes·PNJ dans l'eau 709 → 588 par nuit, à 50 cm ou plus 262 → 124, à 86 cm ou plus 128 → 14 ;
quelqu'un se chauffe les pieds dans l'eau dans 7 nuits sur 8 → 0 ; PNJ restés une heure de suite à
50 cm ou plus 2 (crue 500) → 0 ; appels à l'aide 94 (crue 500) → 2 sur les 8 nuits ; `VERIFIER` sans écart.

Bancs 8 h (8 graines, départ tiré ; `integration` f5cf65f puis la branche, l'un après l'autre) : Relais,
mine et auberge identiques graine par graine (empreintes) ; crue :

| | `integration` | branche |
|---|---|---|
| minutes dans l'eau | 588,8 | 506,9 |
| appels à l'aide | 7,4 | 0,1 |
| feux noyés | 0,1 | 0 |
| au sec à la fin | 3,1 | 3,4 |
| sans recours | 23,8 | 16,3 |
| en attente | 188,1 | 520 |
| minutes dans le noir | 86,3 | 18,1 |
| échanges | 23,5 | 21,1 |
| usurpations, violations | 0 | 0 |
| temps d'une nuit | 11,7 s | 10,8 s |

Les minutes en attente sont le froid : Brune pressée par le froid 7 → 291 minutes par nuit, Aubin 19 →
151, sans feu hors de l'eau ; la sécurité de Brune ne presse plus que 4 minutes au lieu de 72. Temps
d'une nuit, `integration` et branche lancées ensemble (4 graines) : mine 27 → 27 s, auberge 30,1 →
30,3 s.

## Les boucles de la revérification (branche `boucles-pnj`)

Deux boucles nouvelles de la [revérification](reverification.md) (N1 et N2), nées de la délibération à
l'événement (`docs/plan-temps.md`, « Délibérer à l'événement ») : chacun rechoisissant son but à
l'instant, ce qui se relayait une fois par minute se relaie maintenant à chaque geste ou à chaque pas.
La troisième (N4, prévenir de ce que la victime sait) est dans `docs/plan-ouie.md`, « Ce qu'on a déjà
dit ».

**Un geste défait sous ses yeux** (N1 : à la mine 42, Odon ouvrait le garde-manger de Mathe, elle le
refermait, 689 fois chacun toutes les deux secondes, puis crochetage et reverrouillage, et Mathe
appelait à l'aide toutes les deux minutes). Diagnostic, corrigé de celui de la revérification : la
condition `sans_temoin` porte bien sur chaque geste illicite du plan, ouvrir compris
(`planification.gestes` : `faute`) ; c'est la faim d'Odon passée à `DESESPOIR` (95, à la minute 214)
qui lève la précaution (`pnj.desespere`), comme voulu. La boucle venait de ce que voir son propre
geste défait par un autre ne lui apprenait rien : réveillé, il le refaisait à l'instant. Règle commune
(`deliberation.changer_etat`, `contrarie`) : ce qu'un PNJ vient de faire de sa main à une chose
(l'ouvrir, la fermer, la verrouiller, la crocheter, l'allumer, l'éteindre : `ETATS_DONNES`, retenu
dans l'esprit `donne` pendant `DEFAIT` minutes, 5), un autre — PNJ ou joueur — le défait sous ses yeux :
on s'oppose à lui sur cette chose. Il le retient comme un refus (`retenir_refus`, opération `defaire`,
raison « oppose ») qui tient tant qu'il croit l'opposant là où est la chose, au plus `REDEMANDE`
minutes (`tient`), et le planificateur ne lui offre plus aucun geste sur elle (`Vue.contrarie`) : il
cherche autre chose, ou attend. Une gardienne dont on rouvre sous ses yeux ce qu'elle vient de fermer
ne le referme pas en boucle : sa pulsion reste rompue sans plan, elle reste (garder) et appelle si elle
le craint. Seul « ce qu'il vient de faire » compte : Mathe avait verrouillé le garde-manger 89 minutes
plus tôt ; qu'Odon le crochète ne l'empêche pas de le reverrouiller ; c'est Odon, dont elle referme ce
qu'il vient d'ouvrir, qui cesse. Pour le joueur auteur, le moteur l'applique à ses gestes d'ouverture,
de déverrouillage et d'allumage (`moteur._appliquer`).

**Deux recours d'un même besoin** (N2 : à la crue 3, Ilse et Brune passaient 946 et 747 fois d'une
salle à l'autre, jusqu'à 552 passages dans une heure). Diagnostic, corrigé de celui de la
revérification : la Galerie de ronde est éclairée par le jour (pénombre), pas par une lanterne du
joueur (la sienne était éteinte) ; la lumière y est réelle. La boucle a deux moitiés. (a) Dans la
galerie, à l'abri de la lumière, la sécurité qui presse cherche un abri auprès de quelqu'un de sûr :
Gorm au refuge, par le palier ; dans le palier, où l'eau baisse encore (15 cm), l'abri devient le plus
haut lieu éclairé que l'eau ne menace pas (`_plan_abri`, branche de l'eau) : la galerie ; arrivée, de
nouveau le refuge. (b) Dans le noir du palier, la lumière (recours avant l'abri, `RECOURS`) la renvoie
à la galerie, la plus proche. Chaque pas de l'une, entendu de l'autre, la fait rechoisir. Deux règles :
- **Le recours en cours garde la main** (`choisir`, `_candidats`) : une hystérésis entre recours,
  comme `INERTIE` entre besoins. Quand un autre recours du même besoin et du même rang (la lumière et
  l'abri, une pulsion rompue, se chauffer…) donne un autre but, la méthode du but en cours est essayée
  d'abord ; si elle le rend encore sur ce qu'il croit, il le garde. Ce qui n'est pas un recours (une
  alarme, une parole due, prévenir, attendre l'appelant, sortir de l'eau où l'on se croit en péril, un
  bruit à voir, l'argent) passe devant, comme avant ; la routine n'en a pas besoin (une ronde faite le
  reste pour sa période ; sans cette exception, Gorm allait faire la ronde des vannes avant celle du
  refuge où il se tenait).
- **L'abri vers lequel il est en route garde la main** (`_plan_abri`) tant qu'il en est un à ses yeux
  (éclairé, hors de l'eau, quelqu'un de sûr y est), qu'il ne se tient pas déjà dans un abri, que l'eau
  ne monte pas sous ses yeux et qu'il ne se croit pas en péril : un abri « meilleur » apparu en chemin
  (quelqu'un de sûr passé ailleurs) ne le détourne pas, ni un lieu menacé qu'il traverse — ce passage,
  son plan le prévoyait. Devant l'eau qui monte, le plus haut lieu reste la règle
  (`tests/test_eau.py`, Ilse fuit vers la galerie).
- La lumière se juge comme le planificateur la juge (`_plan_lumiere`) : sa lumière en main, ou celle
  du lieu (`lumiere_crue`) ; plus la lanterne qu'un autre porte et qui partira avec lui (avant :
  `autour`, la lumière de sa case quelle qu'en soit la source).

Cas vérifiés après rechargement (`tests/test_boucles_pnj.py`, 11 tests ; chacun échoue sur `main`) :
- N1, cas réel (mine) : Odon, à 96 de faim, crochets en main, Mathe méfiante devant son garde-manger
  verrouillé : un crochetage, une ouverture, Mathe referme et verrouille, Odon ne revient plus au
  garde-manger tant qu'elle est là (au plus un appel à l'aide) ; même laps découpé, même monde.
- N1, même nature (Relais) : Brune à 96, devant la réserve de Gorm ; il referme et verrouille sous
  ses yeux ; elle n'y touche plus, et l'opposition tombe quand elle le sait à la crypte.
- N1, le joueur auteur : il éteint le brasero que Gorm vient d'allumer ; Gorm ne le rallume pas lui-même
  tant qu'il le croit là ; le sachant monté à la galerie, l'opposition tombe.
- N2, cas réel (crue, l'eau à 15 cm au palier, en baisse) : Brune et Ilse gagnent le refuge par le
  palier et l'eau, sans revenir à la galerie (sur `main` : 16 et 19 passages en quinze minutes) ; même
  laps découpé, même monde.
- N2, même nature (Relais, sans eau) : les deux mêmes, l'abri de chacune suivant l'autre ; elles
  s'abritent ensemble au lieu de se croiser (sur `main` : 23 passages en quinze minutes).
- N2, même nature, seule : Brune part pour le refuge ; le joueur, lanterne éteinte, va et vient dans le
  palier noir ; chaque pas entendu la fait rechoisir ; elle ne rebrousse plus (sur `main` : 22 passages
  en quatre minutes).

Audit (`tools/audit_nuits.py`, qui mesure désormais les boucles : `bascules`, un état qu'un PNJ donne à
une chose et qu'un autre reprend ; `passages_heure_max` ; `avertissements_redits` ; appels à l'aide),
4 scénarios × 8 graines (3 42 123 500 1985 2024 7 11) × 12 h, départ tiré, `main` e07bc20 puis la
branche, l'un après l'autre, 5 processus ; par nuit (pire nuit entre parenthèses) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| bascules | 2,5 → 2,5 | 180,6 (1 436) → 2,1 (8) | 15,5 (62) → 2,5 (4) | 1,75 → 1,75 |
| passages de salle par heure, au plus | 9,25 → 9,25 | 12,75 (16) → 13,4 (16) | 27,25 (44) → 27,4 (35) | 24 (40) → 24 (40) |
| avertissements redits | 0 → 0 | 0 → 0 | 4,4 (21) → 0,75 (2) | 0 → 0 |
| appels à l'aide | 0,4 → 0,4 | 5,6 (13) → 4,1 (8) | 2,9 → 2,6 | 0 → 0 |
| sans recours | 119 → 119 | 47,5 → 46,9 | 191 → 195 | 57,5 → 57,5 |
| en attente | 295 → 295 | 1 369 → 1 404 | 379 → 456 | 537 → 537 |
| vols vus (témoins) | 1,25 (2,75) → idem | 0,5 (1,5) → 0,375 (0,9) | 1,75 (2,9) → 1,25 (2,9) | 0,6 (1,25) → idem |
| minutes dans le noir | 236 → 236 | 1 403 → 1 541 | 961 → 992 | 97,5 → 97,5 |
| gestes | 211 → 211 | 533 → 336 | 642 → 635 | 293 → 293 |
| temps d'une nuit | 19,1 → 22,5 s | 111 → 112 s | 96 → 105 s | 28,8 → 28,2 s |

Relais et crue : les 8 nuits identiques (empreintes) ; mine 6 sur 8, auberge 1 sur 8. Aucun plantage,
aucune violation de `Monde.verifier` (chaque pas), aucune usurpation. `planification.VERIFIER` et `spatial.VERIFICATION`
(0,2) sans écart sur une nuit de 8 h de chaque scénario (graine 42, celle de la mine qui bouclait). Les temps, sur une machine chargée
et à nuits identiques pour le Relais, sont dans le bruit. Sur ce `main`, deux nuits de l'auberge (42 et
1985) montraient la même boucle que N1 : Lucien ouvre le coffre ferré d'Anselme, Anselme le referme, 31
et 25 fois ; corrigée par la même règle. Les données de la crue ayant changé (`ressources`), la boucle de
la crue 3 n'y apparaît plus ; sur `main` ec2352e, avant ces données, la crue 3 passait de 1 705 à 136
passages de salle en 8 h (au plus 552 dans une heure sur `main`). À la mine 42, Mathe appelle à l'aide 3
fois au lieu de 13. En attente monte à l'auberge et à la
mine : qui s'est vu opposer un geste attend que l'opposant s'en aille au lieu de le refaire ; à la mine,
Odon, privé du garde-manger, reste plus longtemps dans le noir.

Limites :
- « Ce qu'il vient de faire » est une fenêtre de `DEFAIT` minutes ; au-delà, défaire son geste n'est
  plus une opposition (Mathe reverrouille ce qu'Odon a crocheté). L'opposition porte sur la chose
  entière, pas sur le seul état défait, et tient tant qu'il croit l'opposant là (une croyance qui peut
  être périmée, bornée par `REDEMANDE`) ; elle ne change pas sa confiance en l'opposant, qui peut agir
  de plein droit (le propriétaire qui referme son bien).
- Seuls les états ouvert, verrouillé et allumé sont des gestes qu'on défait ; prendre ce qu'un autre
  vient de poser ne l'est pas. Les portes ouvertes en chemin (la marche) n'en sont pas non plus.
- L'hystérésis compare les buts, pas leur coût : un recours bien meilleur apparu en chemin ne
  l'emporte qu'à la fin du plan, si celui en cours tient encore. La routine en est exclue.
- L'abri en route ne cède qu'à l'eau qui monte sous ses yeux, au péril, ou s'il cesse d'être un abri
  à ses yeux ; traverser un lieu qu'il attend inondé pour le rejoindre reste possible (la crue 3).

## Des parts pour recharger une source (branche `codex-lampes`)

Une part de combustible est aussi un moyen d'un geste, et ne termine donc pas toujours un but.
`_parts_remises` projette sa réception en main, puis les gestes ordinaires `alimenter` et `allumer`
établissent la lumière. Le choix de la réserve dépend de `perception.recharge` et du contenu déclaré
de la source. Porter un combustible incompatible ne dispense pas d'en chercher un qui convienne.
Ce contrat vaut pour une lampe, une lanterne ou toute source rechargeable, sans nom de substance.

La demande ou l'achat d'une part à son propriétaire s'offre pour un lot posé comme porté. Le
donneur garde le lot et fournit une charge. Une part déjà promise n'est pas acquise : le plan
compte le trajet et l'attente du donneur, sans changer l'état de la source. Le plan exécutable
s'arrête à la demande, ou avant la livraison attendue ; après réception, il se refait sur
l'identifiant de la part réellement reçue. Ces frontières sont conservées dans le cache de
recherche : relire le même plan ne les fait pas disparaître (`_couper`).

L'autre service reste possible : demander une part pour qu'un donneur entretienne une source
identifiée. Le combustible doit la recharger ; la cible nommée n'est jamais remplacée. Une source
promise n'est tenue pour servie qu'après son constat, une part livrée qu'après sa réception. La
mémoire et la recherche lisent ces distinctions ; les refus gardent leur cause, leur prix et leurs
moyens selon le contrat commun. Pour la chaleur, une enquête ne compte que le combustible d'un
foyer connu, pas celui de toute source lumineuse (`part_pour`).

L'audit des lectures distingue la catégorie comptée de son emploi : reconnaître un consommable,
le donner plutôt que le prêter et le découper en parts n'affirment aucun besoin servi. En revanche,
`s_enquerir`, `Vue.sur_soi`, `rechauffe`, la garde urgente et les moyens/réponses d'une enquête
emploient `part_pour` ; une part ne réchauffe qu'auprès d'un foyer compatible allumé. Connaître chez
quelqu'un le combustible d'une autre source ne dispense donc pas de l'interroger sur la chaleur.
Une demande de part n'exige pas que le demandeur ait lui-même un besoin de chaleur ; le but qui
emploie cette part vient des gestes. L'eau se juge au lieu de la source désignée, sans écarter une
recharge parce que tous les autres foyers connus sont noyés.

Cas et mesures : `docs/taches/rapport-codex-3-lampes.md`. Les tests `test_lampes_parts` suivent la
lanterne vide de l'étable et la lampe vide de la mine, le bidon posé, une autre substance déclarée,
les lots portés, la parole typée du joueur, les refus, la provenance d'une part et le cache ; l'état,
la perception et le rendu sont vérifiés après sauvegarde et rechargement.

## Lumière employée (branche `codex-lampes-suite`, fusionnée)

La capacité de crocheter ne décide plus si une source et sa recharge sont des moyens du but.
`Vue.emploie_lumiere` rassemble le coût du noir, le but explicite de lumière (`vises.eclairer`)
et les lectures de `Vue.lumiere` / `lumiere_devant` à un niveau que le plan peut améliorer.
Cela vaut pour tout but ou geste qui lit ce contrat commun. La lecture de chance du crochetage
reste conditionnée à la capacité qui autorise ce geste ; cette capacité n'est plus un substitut
à son emploi de lumière. `pertinent`, `gestes` et `_parts_remises` partagent cette dépendance.

Quand une recherche découvre cette dépendance après avoir écarté des moyens lumineux, `_explorer`
reprend depuis le départ, avec la borne entière et sans les anciennes listes d'objets pertinents.
La passe de découverte s'arrête dès la première dépendance révélée : poursuivre un graphe qui
sera jeté ne sert à rien. Il n'y a qu'une reprise : la dépendance reste acquise pendant cette recherche.

Correctif de la fusion : la découverte dépend de l'ordre d'exploration, donc du prix d'une faute,
que la clé du graphe repris (`_GRAPHES`) ne contient pas. Le marqueur `emploie_lumiere` que la
branche posait sur le graphe valait ensuite pour toute recherche de mêmes entrées : une recherche
au prix d'une faute qui ne mène jamais à la lecture de lumière passait quand même avec les moyens
d'éclairer, autrement qu'une recherche neuve (borne atteinte au lieu du plan : `VERIFIER` l'arrête,
`test_le_graphe_repris_redecouvre_la_lumiere_selon_le_prix_d_une_faute`). Le graphe en garde
désormais deux, sans les moyens d'éclairer (`sombre`) et avec (`lumiere`), chacun ne dépendant que
des entrées ; chaque nœud du premier retient si son but ou ses gestes ont lu la lumière, et, rejoué,
la relit au même point : la découverte se refait comme dans une recherche neuve à ce prix-là.
Le nombre de nœuds diagnostiqué et le statut de borne décrivent la passe finale ; le temps
diagnostiqué comprend aussi la découverte éventuelle. La recherche reste bornée : une dépendance
jamais atteinte avant sa borne ne se découvre pas par magie.

`_entrees` explicite le coût du noir et le but de lumière. Les autres lectures restent déterminées
par les croyances, objets, profils et `vises` déjà décrits dans cette clé ; la description `memo`
doit toujours déterminer le but. Aucun état de découverte ne traverse deux entrées différentes.
L'ajout est regroupé à la fin de la clé, pour l'intégration après les relations 3b.

`test_lampes_buts` suit une demande, la part réellement livrée, la replanification, la recharge,
l'allumage et le rendu après rechargement : crochetage sans peur, but d'inspection éclairée sans
peur ni crochetage (mine et auberge), geste d'inspection visuelle de fixture dont le but ne lit
pas la lumière, moyen écarté pour un but sans lumière, graphe repris et
mémoire contrôlés. L'inspection ordinaire reste possible dans le noir ; le test lui compose
explicitement un but de lumière. Mesures et causalité historique :
`docs/taches/rapport-codex-9-lampes-suite.md`.

## Part remise : étape estimée (branche `codex-part-estimee`, non fusionnée)

Le graphe détaille le trajet jusqu'au donneur, la recherche éventuelle de celui-ci,
la demande (chance de `relations.chance_demande`) ou l'achat et son prix. Il ne
développe plus les combinaisons d'états après réception du combustible. La demande,
l'achat ou l'attente d'une part déjà promise mène à un candidat terminal estimé.
`_couper` conserve les frontières existantes : aucune recharge n'est exécutable
avant la livraison réelle ; après celle-ci, le moteur replanifie avec son identifiant.
Le service où le donneur entretient lui-même le foyer conserve son contrat distinct.

`part_estimee.suites` établit un devis depuis le lieu de remise. La scène et ses
faits sont ceux du début de recherche ; les possessions, droits acquis, fautes
déjà comptées et budget engagé viennent du préfixe. Une source déjà empruntée
n'est pas à emprunter une seconde fois. Les autres préparatifs du préfixe ne
refont pas la scène du devis. Il est gardé pour ce contexte, ce lot et l'emploi
de lumière pendant cette recherche ; aucune donnée d'une autre vue n'est reprise.

Le devis parcourt les sources rechargeables connues, compatibles par `recharge`
et non contrariées. Il compte le trajet connu vers la source,
sa prise, son emprunt ou son achat si elle est mobile, une recharge, puis l'accès à une flamme connue et
l'allumage s'il le faut. La flamme peut être portée, accessible et prise, posée si
la source est portable, ou demandée à son porteur connu, avec le refus de feu et le
prix social usuels. Une prise autorisée mais illicite garde son coût de faute,
compté une fois par victime, comme les autres gestes. Une source fixe demande une flamme en main. Aucune substance,
personne ou salle n'est distinguée.

Le reste du but est estimé par un trajet connu et zéro ou un geste conclusif,
offert par le contrat commun `_suites` : ses permissions, chances, fautes, dégâts,
budget et restriction aux moyens du commanditaire s'appliquent aussi. Il n'y a ni
file d'états de gestes ni développement de ses successeurs. Le prix des trajets
entre salles est calculé séparément sur les routes connues, avec la pression de
chaque étape et la combustion de la source portée ; aucun autre fait n'y change.
Un but déjà satisfait au
lieu candidat s'y arrête. Les préparatifs plus longs restent du ressort de la
recherche réelle après remise ; ils ne sont pas prédits par ce devis.

Chaque segment paie ses minutes plus sa durée multipliée par `Vue.pression` à
l'arrivée, comme les trajets de la recherche : noir avant allumage, eau, éloignement
de chaque bien gardé et présence crainte. Le dernier trajet et geste comptent aussi
la combustion d'une source nouvellement portée ; un but à tenir compte encore
`RESTER * pression(final)`. L'attente du donneur vient de `Vue.attente_part`, au
lieu de remise, sans prendre la promesse pour une source déjà chargée. Le prix
d'une faute et celui d'abîmer restent des termes séparés, appliqués par la file
pondérée, jamais choisis ou comparés par le devis.

Ce prix est une estimation de parcours, **pas une borne admissible de l'optimum
détaillé**. Elle peut surestimer en oubliant une ouverture acquise dans
le préfixe, et écarter une voie dont le but
exige plusieurs gestes après allumage. Elle peut sous-estimer une livraison
retardée, un porteur parti, un chemin devenu impraticable, le temps et la combustion
d'un détour, ou les préparatifs omis ; la replanification sur le monde réel demeure
obligatoire. Elle n'établit aucune faisabilité future garantie.

Les lectures proviennent des mêmes objets, croyances, refus, routes, propriétés et
profils que les gestes ordinaires. `_entrees` explicite en plus l'identité de cette
règle et les pressions d'eau et sociales. Le point de départ est déjà dans la clé
(les recherches avec `depuis` ne sont pas mémorisées). Le devis ne compare aucun
prix de faute : les graphes `sombre` et `lumiere` restent indépendants de ces prix.
Ses lectures de lumière passent par les méthodes communes, donc participent à la
découverte et à sa reprise. Les candidats estimés sont terminaux et ne produisent
aucune arête de continuation. Un certificat qui rencontre leur nœud absent ne
prouve aucune impossibilité ; il conserve sa réponse « lacune ». `VERIFIER` refait
la recherche complète avec cette même règle estimée, et conserve ses contrôles de
mémoire, de graphes et de restriction des objets.

`tools/mesurer_part_estimee.py` utilise le banc et l'audit de `comparer_bancs`. Pour
la justesse, chaque recherche concernée, y compris ses reprises, est rejouée avec
la fonction `_parts_remises` de la référence, dans des mémoires séparées, sans
modifier le monde. Il conserve les coûts, le premier geste, le lieu et les effets
terminaux du but, et les deux plans quand ils diffèrent. Les temps de ce contrôle
sont exclus de la comparaison de vitesse. Résultats et limites du lot :
[rapport Codex 16](taches/rapport-codex-16-part-estimee.md).

## Garde et chance de demande (branche `codex-garde-pret`, fusionnée)

Les constantes `GARDE` et `PRET` des bilans précédents sont retirées. Les lieux gardés restent
ceux des pulsions de biens, hors rondes : quand les biens pressent, ou qu'une présence crue
menace un bien dont il a la charge. Méfiance, rancune ou peur en bande suffisent à cette menace.

`prix_gardes` compte chaque lieu une fois. Son prix de base est `1 + valeur / 50` : ambition
pour ses biens ou ceux qu'il convoite, loyauté pour le bien d'autrui confié par une permission
effective. L'ambition pèse la conservation du patrimoine ; la loyauté, la charge acceptée.
À valeurs 50, le prix est l'ancien 2 ; il va de 1 à 3, sans rendre un détaché indifférent à
toute garde. Plusieurs biens au même lieu prennent le plus fort de ces attachements.
Ce prix est multiplié par `1 + risque`, où le risque est le plus fort, parmi les personnes
qu'il croit à cet endroit, de `max(0, 40 − confiance)/100 + rancune/100 + peur/100`.
Les valeurs viennent du gardien, les relations de son propre esprit, les positions de ses
croyances. La peur renchérit l'abandon du bien ; son coût de sécurité propre peut toujours
le faire fuir. Le coût maximal est 10,2 par minute ; plusieurs suspects ne se cumulent pas.

`relations.chance_demande` est le seul calcul de la chance estimée, bornée à 0,1–0,9 :
`0,5 + (confiance−40)/200 + affection/500 − rancune/250 − peur/500 + dette/1000`.
Ce lien est celui du demandeur envers l'autre, un a priori imparfait nourri par ce qu'il a
vécu, jamais l'attitude réelle de l'autre envers lui. Un refus personnel retenu de moins de
`REDEMANDE` minutes retire 0,15 (0,3 par méfiance), sans cumul ; une incapacité matérielle
ne le fait pas. Les refus précis continuent d'interdire la demande selon leur cause.
Un don ou engagement tenu pour l'autre, retenu dans cette même fenêtre, ajoute 0,1 d'espoir
de réciprocité, sans cumul ; se savoir vu fauter par lui retire 0,3. Les services reçus et
les dettes ressenties entrent déjà par les axes. L'auteur retient les témoins qu'il remarque
pendant le geste (`se_sait_vu`) dans sa mémoire bornée, même s'il les remarque après le début.

Objet porté, part servie, part livrée et tâche payée utilisent tous `DEMANDE / chance`.
L'ancienne pénalité de tâche issue des refus d'autres personnes disparaît : l'estimation
porte sur cet interlocuteur. Vente et demande de feu gardent leur contrat existant.
Les deux cartes calculées de la vue (`prix_gardes`, `chances_demandes`) entrent explicitement
dans `_entrees`, donc dans les caches de résultat et de graphe et dans `VERIFIER`.

Cas après sauvegarde et rechargement : Gorm et Bram restent près du bien menacé, quittent
le lieu sans cette méfiance ; garde à valeur neutre, ambition et charge confiée ; positions
crues indépendantes des positions réelles ; Ilse et Joss choisissent le donneur qui les a
servis, reçoivent réellement son objet et le joueur lit la remise ; témoin remarqué conservé
après le geste. `tests/test_garde_pret.py` ; mesures et limites dans le
[rapport](taches/rapport-codex-13-garde-pret.md).

Limites : cette chance n'est pas une prévision calibrée du jet de persuasion. Les signes lus
(3c), la proposition avec sa contrepartie, la réparation et les intermédiaires (3e) restent
à faire. La fenêtre des expériences récentes et les coefficients sont des réglages du moteur.
Les lieux gardés restent issus des pulsions, pas de tout objet possédé ; l'éloignement se juge
par salle et le risque n'est pas réévalué selon une réaction hypothétique des tiers au plan.

## Signalements des nuits (branche `codex-signalements`, fusionnée)

L'audit de `main` 43fa7ac distingue un besoin haut d'une action restant à accomplir. La lecture
commune `deliberation.inactivite` reprend exactement le classement du banc : sans recours entrepris,
en attente de moyen, charge confiée, ou charge déjà satisfaite. Le banc conserve ses comptes ; le
récit distingue les deux derniers cas au lieu de les appeler « sans rien entreprendre ». L'audit
retient la cause avec chaque relevé. Cette lecture ne cherche aucun plan et ne change aucun choix.

Un appel à l'aide suit **l'épisode d'urgence de la sécurité**, avec son effet de seuil, et non le
seul dépassement de `DESESPOIR`. Quitter le lieu où un bien est menacé ou descendre de 96 à 94 ne
rassure pas quelqu'un que sa sécurité presse toujours. `esprit["secours"]` garde la minute de
l'appel et si l'épisode s'est apaisé, indépendamment des quarante souvenirs. Un autre besoin ou
une réponse qui ne rassure pas ne réarme pas l'appel. Le répit `APPEL_REPIT` reste applicable à un
nouvel épisode ; un abri en cours passe toujours avant l'appel. Le recours est inscrit avant le son.
Pour une ancienne sauvegarde, le dernier souvenir d'appel initialise ce suivi ; son ancien marqueur
`apaise` n'est retenu que si la sécurité ne presse plus au chargement. Un appel déjà sorti de
l'ancienne mémoire ne peut être reconstruit.

**Une recherche retient ce qu'elle a appris, même si quelqu'un a répondu.** Après un tour d'horizon
et l'appel éventuel, ne pas savoir la personne cherchée là est un résultat infructueux de cette
personne dans ce lieu. `esprit["recherches"][personne][salle]` le garde hors mémoire bornée ; les
anciens appels sans réponse l'initialisent. `appels_vains` applique toujours `APPEL_OUBLI` (60 min)
et la date de la dernière croyance de lieu : apprendre une nouvelle position permet de rechercher
de nouveau. La liste des salles ainsi écartées entre dans `_entrees`, donc dans la mémoire et les
graphes contrôlés du planificateur. Aucune réponse anonyme n'apprend une identité ou une position
de corps par ce suivi.

Un plan qui cherche celui à qui il a dit « J'arrive ! » emploie d'abord le lieu du rendez-vous
(`_attendre_qui_vient`, `appel.plan_venir`) ; il ne continue pas sa tournée pour le trouver.
L'inspection infructueuse du lieu convenu termine ce rendez-vous, même dans sa minute de création,
sans relancer l'appel au même endroit. Un plan visant quelqu'un d'autre conserve son rang habituel.

Cas enregistrés et cas de même nature, après rechargement et avec le même laps découpé : Gorm au
Relais 42, minute 160 ; Ilse seule entre désespoir et urgence ; Anselme à l'auberge 3, minute 570,
et une recherche de bien porté au Relais sans voix identifiée. La cause des longues inactivités
est également vérifiée sur l'auberge 11, minute 500 (Mireille : charge payée confiée ; Hugues :
rondes à jour), et le Relais 1985, minute 120 (charge du joueur). Résultats et limites dans
`docs/taches/rapport-codex-14-signalements.md`.

## Le coût du temps (branche `codex-trajets-reels`, non fusionnée)

Le temps d'un aller n'est plus un nombre de salles. `obstacles.cout_route` compte en
minutes fractionnaires les pas du chemin cru (`temps.duree_pas`, diagonales et allure),
les gestes des portes et les rotations. `Route` garde les sorties, les pas, la case
d'arrivée et les durées dans chaque salle ; une approche sans changement de salle a
aussi une durée. Sans mode cases, les anciennes parties gardent leur horloge par minute.

La recherche conserve la case et l'orientation dans `Etat`. Une entrée par un autre
seuil ou un geste au fond d'une salle ne se confond plus avec le départ. Un objet posé
par le plan garde sa case prévue. Les portes ouvertes en passant font partie des effets
du déplacement. La marche ordinaire et la marche feutrée sont deux départs possibles
quand un geste sans témoin est permis ; les gestes qui demandent cette précaution
exigent l'allure feutrée depuis le début. Un plan feutré n'achève pas un but sans avoir
effectivement employé cette précaution. Les deux graphes de lumière et le certificat
d'absence suivent ces mêmes états et départs.

`Vue.allers`, `route`, `trajet`, `_chercher`, l'attente d'une part, la peine de la tâche,
le choix de l'interlocuteur d'une enquête, `part_estimee` et la fuite du joueur lisent
cette mesure. `pnj.parcours` et `chemin` fournissent des routes mesurées en mode cases,
même sans passage spécial. Une salle coupée sans franchissement cru est donc inaccessible.
La marche et la fuite spatiales comptent aussi les gestes des portes dans leur choix de
chemin. La preuve `metrique_necessaire` reste celle qui permet d'écarter les arêtes de
franchissement dominées par la marche ; elle n'écarte plus la distance ordinaire.

`_mesurer` emploie le contact commun `_a_toucher` / `_a_portee_de`, les positions crues,
les durées `pnj.DUREES` et les tentatives attendues d'un jet. L'approche et la rotation
précèdent le geste. La pression se compte dans les salles traversées et pendant le
geste, avant ses effets : allumer ne supprime pas le noir du temps passé à l'allumer.
La combustion en main multiplie le temps réel, pas les préférences sociales ou les prix.
Le devis de part conserve son ordre de préparatifs et sa frontière de replanification.

Le parcours global développe le départ et les seuils d'entrée. Les distances de chaque
origine locale aux cases de sa salle sont gardées dans une mémoire bornée de 2 048 tables,
partagée entre vues. Sa clé porte la salle, les obstacles crus et leurs formes, l'origine,
l'allure et, quand les passages servent, le corps et les dimensions/masse de l'équipement.
Les portes et clés prévues distinguent les parcours globaux. `spatial.VERIFICATION`
recalcule les tables reprises ; `_entrees` inclut les positions crues, le départ réel,
l'orientation et les placements fixes connus du lieu, pour les résultats, graphes et
certificats. Une recharge qui ne change pas une charge suffisante n'ajoute plus un état ;
un combustible sans source à recharger n'ajoute pas un inventaire inutile à la projection.

L'échelle des prix reste volontairement inchangée : `DEMANDE`, `CHERCHER`, `RESTER`,
`TACHE`, `SALAIRE`, les fautes et la valeur des pièces ne sont pas recalibrés en silence.
Quelques secondes de marche coûtent désormais quelques centièmes de minute ; demander
ou payer peut donc peser beaucoup plus. Les mesures et propositions de réglage sont dans
le [rapport du lot](taches/rapport-codex-20-trajets-reels.md).

Limites de la prévision : les positions inconnues demandent une origine conventionnelle
du lieu ; une promesse ne prédit pas les autres préparatifs ni les délais du donneur.
Les personnes peuvent bouger, faire obstacle ou refuser ; cela reste revalidé à l'exécution.
Les gestes durables gardent leur horizon de séjour `RESTER`, sans simuler toute l'évolution
future du corps. Le devis de part reste une estimation, pas une borne admissible. La recherche
reste bornée à 4 000 états, dans un espace devenu plus riche ; les échecs par borne doivent
être distingués des impossibilités prouvées.

La mesure du temps ne garantit pas que la délibération laissera le plan aller au bout :
une urgence d'abri peut interrompre un aller pour la faim ; la fuite actuelle s'achève
dès que la salle diffère de celle du danger cru, sans horizon de sécurité durable.
Les campagnes de ce lot révèlent des oscillations nouvelles dans ces domaines. Le
critère d'absence de boucle nouvelle n'est pas satisfait ; les cas et mesures sont
consignés dans le rapport, sans exception de scénario ni recalibrage masquant le défaut.


## Modèle de trajet de recherche — lot 30 (2026-10-24)

Dans la recherche, le trajet s'estime ; il ne se mesure qu'à l'exécution.
`Etat` identifie salle, possessions et faits. L'allure distingue encore les pas
ordinaires des pas feutrés : les gestes sans témoin exigent ces derniers dès
le début du plan. Case et orientation restent des attributs de compatibilité
vides ; aucun fait de position d'objet posé n'est produit par la recherche.

`trajet_estime.tables` réemploie les tables métriques locales d'`obstacles.distances`,
partagées sous la géométrie et les obstacles crus, l'allure, le gabarit et
l'équipement utile aux franchissements. Les origines sont les seuils intérieurs
triés. Une approche coûte la moyenne des distances au contact depuis ces seuils.
Une sortie coûte la moyenne depuis les autres seuils ; avec une entrée unique,
c'est la moyenne sur le sol accessible. Sans sortie, le premier point du sol
sert d'origine conventionnelle. Un angle moyen de 90° (une seconde) s'ajoute au
déplacement, puis à l'orientation du geste ciblé. Un Dijkstra par salle choisit
les routes ; portes et pas de seuil gardent leur tarif propre. La durée passe
exclusivement par `obstacles.cout_route`, la pression par `Vue.prix_route`,
avec le temps passé dans chaque salle avant l'effet du geste.

`Vue.allers`, `trajet`, les attentes de parts et `part_estimee` consomment tous
ces routes estimées. `_entrees` garde la géométrie, les croyances, l'équipement,
les tarifs et la version du modèle, sans position ni orientation de départ.
`VERIFIER` refait la recherche avec ce même modèle. `pnj.parcours`, `_marcher`
et `defense.chemin_fuite` gardent leurs chemins et durées réels, revérifiés
à l'exécution ; aucun itinéraire estimé n'est exécuté comme un chemin spatial.

Limite de l'abstraction : une salle coupée ne permet plus d'identifier la
composante où l'acteur se trouve. Une sortie sans origine moyenne accessible est
refusée conservativement ; une action locale sans entrée accessible est estimée
sur la composante du contact. Elle peut donc échouer à l'exécution si l'acteur
est dans une autre composante. Ni l'occupation mobile ni les détours par une
autre salle pour toucher un objet local ne sont prévus par cette moyenne.
L'erreur mesurée et les limites du banc figurent dans le rapport du lot 30.


## Borne du séjour final — lot 48 (`codex-borne-rester`, non fusionnée)

Pour `tenir`, `Vue.borne_rester` calcule une fois par départ de la Vue :
`H = RESTER × min_s (somme(prix_gardes[g] pour g != s) + NOIR × eau[s])`.
Les salles `s` sont celles reliées au départ par les sorties, sans restriction
de serrure, d'obstacle, d'équipement ou d'eau. C'est une relaxation : chaque
salle atteignable par un geste ou un devis est dans cet ensemble, même après
une préparation qui ouvre un passage. Une carte inconnue donne zéro. Le noir
et la présence inquiétante sont omis : un plan peut les faire disparaître.
Salles, prix des gardes et eau sont déjà dans `_entrees` ; aucune donnée
nouvelle du monde n'est lue par le tri, le graphe ou le certificat.

**Admissibilité.** Dans toute salle finale, la pression est au moins le terme
gardes + eau de cette salle. Les autres termes, comme tous les coûts de
transition, sont non négatifs. Le séjour réel `RESTER × pression(final)` est
donc au moins H, même sur une suite estimée. H est zéro pour les buts sans
séjour et pendant la découverte de lumière : celle-ci doit s'arrêter à la même
lecture que la recherche historique.

**Cohérence.** H est constant sur les états ordinaires d'une recherche :
`H <= coût(arête) + H`. L'arête d'un état qui atteint le but vers son résultat
paie son séjour, au moins H ; le résultat a h = 0. Un nœud `SuiteDifferee` a
h = H + sa borne B : l'arête entrante coûte zéro (`H <= H+B`), la sortie
terminale coûte au moins B + son séjour, donc au moins B+H. On n'utilise jamais
un devis approximatif comme minorant. Une borne nulle reste valide.

**Rang et reprises.** `_explorer_etats` garde g intact et trie les états par
g+H ; les suites différées par g+B+H ; les résultats par leur coût total. Le
coût de file historique est la deuxième clé, avant le type et le rang réservé
du lot 38 : même quand l'addition de H arrondit deux coûts distincts au même
flottant, l'ordre entre états non terminaux reste historique. Les résultats
de même coût gardent leur ordre de génération et les suites différées leur
rang réservé. La recherche peut s'arrêter avant les états dont aucun résultat
ne peut battre celui déjà trouvé, sans retirer de transition au graphe.
`_sans_plan`/`_parcours` restent indépendants du coût et une suite inconnue
reste une lacune. Aucun prix, coût de jeu, profondeur ni plafond ne change.

**Contrat précisé par l'utilisateur le 2026-10-24.** Décisions identiques
partout où la référence uniforme n'atteint pas son plafond. Si elle l'atteint,
un résultat différent est permis seulement s'il égale celui de la recherche
complète (`REFERENCE`, 60 000 nœuds, sans restriction d'emplois) : même coût,
ou aucun plan si la complète n'en trouve pas. `VERIFIER` recalcule désormais
la référence uniforme sans H et sans report des devis ; toute différence
non bornée échoue. Une différence bornée est comparée à la complète et notée
dans `planification.BORNES` avec `ancienne_borne=True`. La désactivation
interne `borner=False` sert à ce témoin ; elle n'est pas un mode de jeu.

Première divergence réelle : auberge 42, minute 559, Lucien, `garder:grenier`.
Uniforme : aucun plan à 4 000 états ; avec H=72 : plan en 78 états ; complète :
exactement ce plan, coût 78,92250378787878, à 5 759 états. Il recharge et allume
sa lanterne avant de regagner le grenier. La capture est versionnée dans
`tests/data/borne-rester/` ; les conséquences et le rendu après rechargement
sont vérifiés. Cette divergence ne vient ni d'une inadmissibilité ni du rang :
la référence épuisait son budget avant de retirer le résultat de la file.
Autre première divergence : auberge 1985, minute 486, Lucien, `garder:etable` :
aucun plan à 4 000 états dans la référence ; avec H, rester (plan vide, coût 90)
en 102 états ; la complète rend exactement ce résultat à 4 180 états. Les deux
reprises passent `VERIFIER` et portent `ancienne_borne=True` dans `BORNES` ;
`tests/data/borne-rester/contrat.json` garde les résultats et les captures.

Pour chaque nuit divergente, on contrôle sa première recherche différente et
sa complète ; on ne compare plus les décisions pas à pas après ce point.
On relève ensuite les mesures de sûreté, les boucles et le CPU de ces nuits,
dont les trajectoires différentes ne permettent plus d'attribuer tout écart
de temps à l'optimisation seule. Mesures et limites dans le
[rapport du lot 48](taches/rapport-codex-48-borne-rester.md).

## Coût des nuits de 12 h — lot 38 (`codex-cout-12h`, non fusionnée)

L'invariant est de ne calculer une lecture coûteuse qu'une fois pour ses entrées,
et de ne développer une suite terminale que si sa borne peut encore battre ou
égaler le meilleur coût. Aucun tarif, prix, plafond de nœuds ou scénario ne change.

**Borne admissible et cohérente.** La file peut contenir une `SuiteDifferee` :
un nœud intermédiaire sans effet, entre un préfixe et ses suites terminales.
Son g est le coût du préfixe, son h le minimum des prix d'offre possibles,
moins le geste conventionnel d'une minute que `_mesurer` remplacera par une
approche et un geste de durée positive. Pour une attente déjà promise, h est
l'attente ; sans justification, h vaut zéro. Tout le devis, les fautes, la
combustion, les pressions et le séjour final de `tenir` sont non négatifs.
Ainsi h ne dépasse aucune sortie terminale ; h = 0 aux sorties et aux états
ordinaires. Les arêtes préfixe → nœud différé coûtent zéro : la cohérence vaut
sur les deux arêtes. Le devis approximatif de `part_estimee` n'est jamais une
borne. Ce n'est pas une heuristique positive sur tous les états ordinaires :
leurs moyens futurs et un but Python arbitraire ne sont pas bornés ici.

La clé de file réserve le rang historique de chaque groupe avant de différer
son calcul, avec le rang interne de ses sorties. À priorité égale, les nœuds
intermédiaires se révèlent avant toute décision, puis les vrais résultats se
départagent par le rang réservé. Ni l'ordre des états ordinaires, ni leur
compte sous `NOEUDS`, ni les égalités de plans ne changent. Les développements
économisés sont ceux des devis, pas les états ordinaires comptés par le banc.
Tous les résultats passent par `_normaliser_suites` : les restrictions des
devis par leurs seuls moyens, les effets terminaux et les gardes restent communs.
La découverte des moyens d'éclairer force l'évaluation au point historique ;
seule la passe aux moyens déjà définis diffère les calculs.

`_GRAPHES` garde les mêmes transitions, éventuellement encore différées, dont
les termes ne dépendent pas des prix de faute et de dégât. Une suite révélée
se calcule une seule fois ; une suite encore inconnue n'est pas une preuve
vide. `_parcours` retourne « lacune » sans l'évaluer ; `_sans_plan` reste un
parcours indépendant des coûts, sur les deux graphes de lumière. `VERIFIER`
recompare aussi les recherches neuves à l'évaluation immédiate complète des
mêmes gestes, avec la même borne et le même rang ; la référence sans restriction
d'emplois conserve son contrôle de coût antérieur.

**Parts et devis.** Chaque `Vue`, figée pendant la recherche, garde :

- Les résultats de `_parts` par état complet, lot, lieu du lot, emploi de lumière
  et contexte du but/visées. Aucun fait n'est retiré de cet état : le but peut
  lire chacun d'eux. La première lecture reste un générateur, afin de conserver
  l'instant des lectures de lumière.
- Les sources à recharger par possessions, faits `allume`/`charge`, emploi de
  lumière et sources entretenues. La disponibilité et les compatibilités de
  combustible sont des données figées de la vue ; salle, droits et autres effets
  ne sont pas lus par ce test et peuvent différer.
- L'attente d'une part par donneur, lot, salle de service, cible, salle de départ,
  possessions, allure et faits de lieux, portes, positions et départ de promesse.
  Les lieux incluent le porteur et toute chaîne de contenants ; budget et effets
  terminaux ne modifient pas ce trajet. Deux états équivalents partagent ce scalaire.
- Le devis par état normalisé complet déjà employé par `part_estimee`, contexte
  du but et ensemble exact des sources que recharge le lot. Le lot n'est lu que
  pour cette compatibilité : deux lots de même compatibilité réemploient le devis.

Ces mémoires restent locales à la vue ; elles ne passent ni mutation du monde ni
sauvegarde. Toutes les lectures extérieures restent couvertes par `_entrees`.
Les imports des fonctions chaudes sont au module ou utilisent une référence
conservée ; `perception.substance` garde le module matière au premier appel,
pour ne pas introduire le cycle de démarrage matière → monde → perception.

Mesures, preuve d'identité et limites : [rapport du lot 38](taches/rapport-codex-38-cout-12h.md).

## Départ feutré découvert — lot 51 (`codex-depart-feutre`, non fusionnée)

La permission globale de voler ou de frapper ne suffit plus à doubler les
états initiaux. `_normaliser_suites`, commun aux gestes immédiats et aux
suites différées, découvre la discrétion sur leurs gardes `sans_temoin` et
`dans_le_dos`, après les restrictions de tiers et d'effets terminaux utiles.
La première recherche part à l'allure ordinaire. Si elle découvre un tel
geste, `_explorer` reprend depuis le départ avec les deux allures, la même
borne et le même ordre ; la découverte de lumière repart elle aussi de son
état initial. Vérifier les filtres du candidat ne déplace pas les lectures
de lumière : elles se feront dans la reprise, à leur point historique.
Les plans discrets marchent donc feutré dès le début.

`_GRAPHES[(PNJ, but)]` retient la marque `discretion` dès cette première
rencontre des entrées. Il ne garde alors que cette marque ; les nœuds des
graphes `sombre` et `lumiere` restent gardés à la deuxième recherche sur les
mêmes entrées. Un changement des seuls prix reprend directement les deux
départs, sans refaire la découverte. Un changement des entrées remet la
marque à zéro. Une marque fausse ne prouve pas une impossibilité : une
recherche ultérieure peut encore découvrir un geste dans des nœuds que le
prix précédent n'avait pas fait examiner.

Les gardes lisent les permissions, capacités, visées, refus, moyens et
croyances déjà couverts par `_entrees` et sa clé complémentaire ; aucune
nouvelle lecture du monde n'est ajoutée. La marque reste une mémoire de
calcul, sans modification des sauvegardes. `_sans_plan` et `_parcours`
partagent `_departs` avec la recherche jouée ; aucun certificat ne développe
une suite inconnue. `VERIFIER` refait la recherche uniforme avec les départs
historiques et, si elle plafonne, compare à la complète (`REFERENCE`) selon
le contrat du lot 48. `decouvrir_discretion=False` sert à ce témoin interne.
Aucun coût, prix, plafond, scénario ni geste ne change.

Limite : la garde découvre un geste candidat après les filtres communs,
avant la mesure de son approche. Elle peut donc conserver la discrétion pour
un geste dont l'approche échouera ensuite ; cette possibilité supplémentaire
ne retire aucun plan. Les mesures, divergences et contrôles figurent dans le
[rapport du lot 51](taches/rapport-codex-51-depart-feutre.md).

## Devis sans voie d'allumage — lot 49 (`codex-devis-vides`, non fusionnée)

Avant `part_estimee._preparer`, `_allumable` exige une voie possible d'allumage
pour la source atteinte et obtenue. Une source déjà allumée satisfait la condition.
Sinon il faut une autre flamme portable connue, allumée ou outil d'allumage,
déjà portée ou dont le lieu est accessible. Elle doit pouvoir être prise avec
autorisation, demandée ou achetée selon les droits, refus, restriction `seul`
et budget restants ; une source mobile peut aussi demander du feu à son porteur
ou rejoindre une source fixe allumée. Routes et descentes utilisent les méthodes
communes. Le retour vers une source fixe et les approches des gestes ne sont pas
exigés : le filtre reste volontairement optimiste.

**Nécessité.** Toute sortie de `_preparer` passe par sa liste `allumages`. Cette
liste n'a que quatre origines : source déjà allumée, flamme en main, flamme
obtenue ou feu demandé au porteur, source fixe rejointe par une source mobile.
La condition les couvre toutes, en conservant des possibilités supplémentaires
(retour non vérifié, approches non mesurées). La mesure locale d'`alimenter`
ajoute seulement `charge` et ne franchit aucune porte ; elle ne change donc ni
les routes, ni les permissions, ni l'état des autres flammes que lit la condition.
Si celle-ci est fausse, aucun allumage et donc aucune suite ne peut être produit.
Si toutes les sources échouent, le devis rend vide sans développer ses préparatifs.
Ce n'est pas une condition suffisante de conclusion du but, qui reste une fonction
arbitraire ; les devis sans geste conclusif peuvent encore être développés.

La passe de découverte conserve ses lectures au point historique : tant que
`emploie_lumiere` est faux, le filtre laisse passer la préparation, dont la pression
peut découvrir la lumière. Aucun nouvel effet, prix ou plafond n'est introduit.

Le certificat est local à la `Vue`, dans `_crus`, clé par source et **état complet**
atteint après obtention ; le résultat du devis garde sa clé normalisée complète,
compatibilité, contexte et emploi de lumière. Toutes les lectures extérieures sont
déjà dans `_entrees` : objets connus et usages, croyances d'état et de lieu,
propriétaires, permissions et refus, richesse, `seul`, géométrie, routes et eau.
Aucun champ du monde nouveau n'est lu ; aucune lecture de vérité physique ne
remplace une croyance. Sauvegardes et cache des recherches gardent leur contrat.

Mesures et limites : [rapport du lot 49](taches/rapport-codex-49-devis-vides.md).


## Une source de plus — lot 46 (`codex-une-source`, non fusionnée)

L'invariant prolonge « on ne porte que ce qui peut servir le but » : **une source de lumière portable
de plus, qui n'apporte aucune capacité absente des sources déjà portées, n'ouvre aucun geste de la
recherche** — ni prendre, ni demander, ni acheter, ni la saisir sur un porteur (et donc ni chercher
son porteur), ni la faire remettre par une aide sur place — sauf si le but la vise (`prendre`,
`poser`, `fermer`, `servir`, `entretenir`). La règle est dans `gestes` et `_aide_sur_place`, comme
celle des combustibles sans source à recharger et celle des flammes `superflu` : elle ne dépend pas
d'`emplois`, la recherche de référence de `VERIFIER` l'applique aussi.

**Capacité** (`Vue.capacite`), définie une fois sur ce que lisent les gestes de lumière (`feu`,
`flamme`, `brule`, la faute de toucher la source) : un rang, une substance, « sans faute ».
Rang 3, allumée : elle éclaire et donne une flamme ; 2, éteinte et chargée : une flamme l'allume ;
1, éteinte et vide : elle se recharge de sa substance (`perception.brule`) puis s'allume ; 0, rien
(état inconnu, ou vide sans se recharger). « Sans faute » : l'allumer ou la recharger n'est pas une
faute (bien d'autrui sans permission). `Vue.couvre(a, b)` : allumée couvre tout ; sinon un rang au
moins aussi haut, la même substance à rang 1, et sans faute si `b` l'est. La source candidate est
jugée au mieux (« sans faute » : acquise par une demande, elle serait permise). Seules comptent les
sources qui ne servent qu'à y voir (`Vue.sources_seules` : mobiles, ni foyer, ni clé, ni outil de
`USAGES` — l'allumage compris —, ni vivres, ni part) ; une source portée à laquelle il ne touche pas
(`contrarie`) ne couvre rien.

Pourquoi le résultat ne change pas : la lumière d'un état ne dépend que d'une source allumée en main
ou allumée par le plan (`_eclaire_par_le_plan`), pas de laquelle ni de combien ; recharger, allumer,
demander du feu se font sur la source portée qui couvre la candidate, avec un coût égal ou moindre
(pas de détour d'acquisition) ; une seconde source allumée par le plan coûte de plus `FLAMME_EN_MAIN`.
Un objet de plus ne rend aucun passage possible. Aucune lecture nouvelle : croyances d'état des
sources, permissions, refus tenus et données d'objets sont déjà dans `_entrees`.

Ce que la règle ne touche pas : allumer ou recharger sur place une source qu'on ne porte pas (une
lampe posée allumée par le plan éclaire sa salle sans se consumer en main) ; le devis d'une part
remise (`part_estimee`), qui reste une estimation ; les coûts, prix, bornes de nœuds et scénarios.

Mesures, divergences et limites : [rapport du lot 46](taches/rapport-codex-46-une-source.md).

## Étapes chaînées — lot 72 (`codex-etapes-chainees`, fusionnée)

La file de `_explorer_etats` porte un maillon en tuple `(parent, ajout)` par
transition retenue, sans recopier les étapes du préfixe. Les ajouts appartiennent
aux suites du graphe, qui se lisent sans mutation pendant la recherche ; ni le
chemin ni ses maillons ne participent au tri. États, coûts, rangs, égalités,
plafonds, découverte de lumière et de discrétion restent inchangés. Un résultat
de séjour et une `SuiteDifferee` partagent le préfixe jusqu'à leur retrait du tas.

Seul le chemin rendu est parcouru par `_reconstruire_etapes`. Ses dictionnaires,
listes et tuples imbriqués sont gelés dans une séquence immuable, conservée telle
quelle dans `_MEMOIRE` et comparée telle quelle par `VERIFIER`. `chercher` produit
une liste publique indépendante, avec les mêmes types de contenus qu'avant,
pour chaque appel, y compris le premier. Aucune copie profonde n'est nécessaire
à la restitution ou à la mémoire. `_couper` conserve ses marqueurs et frontières
de replanification ; les sauvegardes continuent à contenir les listes ordinaires.

Le contrat d'étape est celui des données de geste : dictionnaires à clés scalaires,
listes, tuples et valeurs scalaires. Le gel ne sert pas à sérialiser des objets
Python arbitraires ou cycliques. Les étapes des suites restent des données de
calcul internes, jamais exposées à l'appelant. Les états finaux et les autres
mémoires ne changent pas de contrat.

Les captures `cout-12h` gardent les empreintes de chaque plan, de l'ordre des
retraits du tas et des diagnostics de `fbcf0ff`, puis du monde complet, du journal
et du rendu après recharge. Un plan avec plusieurs ajouts, une égalité avec
suite différée, l'absence de résultat et les mutations profondes des plans
publics sont testés. Les profils ne justifient pas un changement des signes
dans ce lot. Mesures et limites : [rapport du lot 72](taches/rapport-codex-72-etapes-chainees.md).

## Préparation d'un choix — lot 71 (`codex-cout-fixe`, non fusionnée)

`deliberation.choisir` encadre seulement la boucle des méthodes candidates par
`planification.vues_du_choix`. Ce bloc est en lecture seule : les constatations,
échéances et attentes le précèdent ; intention, classement des urgences et recours
proposés le suivent. `VERIFIER` compare l'état complet à l'entrée et à la sortie.
La préparation de `Vue` est paresseuse, propre au monde et à l'acteur du bloc,
abandonnée à sa sortie même sur exception. Un nouveau choix après déplacement,
perception ou changement de croyance ne reprend rien de cette préparation.

`vue` fournit une copie privée de la préparation à chaque appel : paramètres du
but, découvertes de lumière/discrétion et dictionnaires internes restent locaux à
la recherche. La base vierge n'est jamais explorée. `_entrees_communes` sérialise
une fois le relevé indépendant du candidat ; `_entrees` lui adjoint les visées,
bornes, emplois, but explicite de lumière, admissibilité de violence selon le
motif et entrées de défense. Aucune lecture de l'ancienne clé n'est supprimée.
La vérification de référence construit une `Vue` neuve ; depuis le lot 81,
elle partage les seules tables de géométrie et de tarifs de la vue contrôlée.

`obstacles.cle_carte` conserve une copie témoin des salles et un texte immuable
du contenu et de l'ordre des salles/sorties. L'égalité avec le témoin détecte les
éditions en place ; le texte n'est refait qu'au changement. Les trois clés de
géométrie (`metrique_necessaire`, `distances`, `parcours_cru`) l'utilisent comme
composante de tuple, sans le réencoder. Obstacles, portes crues, équipement,
gabarit et allure restent dans leur partie dynamique historique. Aucune lecture
de vérité ne remplace une croyance, aucun tarif ou ordre de recherche ne change.

Limites : le partage ne franchit pas un choix ; il exige que les méthodes candidates
restent en lecture seule. La carte reste un dictionnaire JSON éditable : le témoin
demande encore une comparaison de contenu, et l'ordre des salles et sorties est
relevé à chaque lecture. Ce lot ne réduit ni l'espace de recherche ni le nombre
de nœuds. Mesures et validation : [rapport du lot 71](taches/rapport-codex-71-cout-fixe.md).

## Géométrie et tarifs par recherche — lot 81 (`codex-cout-par-noeud`, non fusionnée)

Un état lit les mêmes routes quand sa salle, son allure, ses clés (tout son
équipement si les franchissements sont métriques) et les faits de portes sont
identiques. `Vue.contexte_route` projette ces entrées une fois par état ; `route`
garde aussi l'admissibilité et sa cause de refus, `allers` reprend la même liste
triée. Les routes d'approche continuent à distinguer les cibles et leurs contacts,
l'allure et l'équipement métrique (`trajet_estime.approche`). Les durées des
`Route` sont sommées une fois par orientation par `obstacles.cout_route`.

`prix_route` mémorise l'intégration dans l'ordre original des séjours. Sa clé
conserve les possessions et les faits de lumière et de lieu qui déterminent
la pression. Si aucune lumière ni présence ne peut la changer (ni peur du noir
ni peur sociale), la pression dépend seulement des gardes et de l'eau, figées
par salle ; elle se lit directement dans cette table. Ce critère vient des
lectures de `pression`, sans règle de scénario ou de personnage.

`mesure_aller` compose durée, pression et effets de portes, puis `_mesurer`
applique ces seules écritures à l'état suivant du nœud. Un droit ou un effet
terminal ne provient jamais du nœud qui a rempli la table. Les séquences
composées gardent leur calcul pas à pas et emploient les mêmes tarifs de route.
Les tables indexées par identité retiennent la route elle-même : son identité
ne peut pas être réattribuée tant qu'un tarif la désigne.

Ces tables appartiennent à la photographie de `Vue`, y compris dans les passes
de référence de `VERIFIER` ; les emplois, découvertes, graphes et résultats
restent privés. `spatial.VERIFICATION` refait les parcours, leur admissibilité,
les sommes et les effets avant de comparer la table des déplacements entre
salles. Le coût et l'ordre des additions, les nœuds et leurs plafonds, les
choix et le modèle d'estimation restent les mêmes. Aucune table n'entre dans
la sauvegarde ou ne franchit un changement du monde. Mesures et limites :
[rapport du lot 81](taches/rapport-codex-81-cout-par-noeud.md).

Le contrôle garde seulement le parcours témoin du dernier état **complet**,
avec case et orientation, sans employer la projection qu'il contrôle. Les
destinations consécutives de cet état partagent le recalcul indépendant ;
un autre état le remplace. Une dépendance omise d'une clé projetée et une
corruption de la table restent détectables, sans garder les témoins de tout
le graphe ni refaire le même parcours pour chacune de ses destinations.
