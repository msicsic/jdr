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
rend pertinent (sources, flammes, ce qui les recharge) ne l'est que s'il croit le noir quelque
part, s'il sait crocheter ou si le but est la lumière ; une lampe ou un briquet de plus ne s'explore
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
  (manque déjà relevé) ; on n'allume pas sa lampe à celle d'un autre sans la lui emprunter ;
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
  moins éclairée ; il le constate au premier essai (au plus un essai perdu par arrivée) ;
- un essai à chance réelle faible mais non nulle (5 % avec DEX + 2 dans le noir) reste envisagé,
  à son coût (1 / chance minutes) : les jets sont indépendants, un échec n'apprend rien de plus ;
- forcer une porte (frapper) n'est pas un geste des PNJ ; seuls la clé et le crochetage lèvent
  une porte verrouillée, et le PNJ n'apprend une porte verrouillée qu'en l'essayant ou par savoir ;
- personne n'apprend le contenu d'une bourse autrement qu'en la tenant ou par un savoir déclaré :
  ni la voir compter, ni l'entendre dire ;
- au banc, Lucien, dans la chambre noire, ne va pas chercher de lumière : sa recherche n'en trouve
  aucun moyen ; il retourne garder ses biens.

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
  rend honnête pour isoler la garde ;
- seuls le noir et la garde ont un coût par minute ; le froid, la compagnie et la méfiance n'entrent
  que dans le gain de l'abri ; se chauffer compte le séjour sans l'endurer ;
- au Relais, Gorm demande les planches d'Aubin plutôt que d'aller chercher son bois à la crypte
  (s'éloigner du refuge coûte `GARDE`) : cohérent avec la règle, à signaler ;
- la lumière d'une salle se constate à la case où il se tient : une salle aux sources inégales se
  juge de loin à ce qu'il en a vu de sa case ;
- la peur du noir ne s'émousse pas avec le temps passé ;
- un besoin apaisé sans avoir été comblé (repassé sous son seuil sans descendre à seuil − `REPRISE`)
  ne presse de nouveau qu'à seuil + `REPRISE` (au départ fixe, Ilse au Relais laissait monter son
  froid jusqu'à 85, puis hésitait deux fois entre l'abri et le brasero) ;
- le planificateur coûte plus à qui garde ses biens (auberge +13 % de temps par nuit, ci-dessus).
