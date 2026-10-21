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
- **La salle éclairée sans ce qu'on porte** : la croyance `eclairee` d'une salle ne compte plus
  les sources qu'il porte (elles le suivent).
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

Limites :
- le va-et-vient entre deux besoins dont l'urgence dépend du lieu (la garde au grenier noir, la
  lumière du couloir) : rien ne retient dans la lumière celui qui n'emporte pas de lumière ;
  l'abri a la même faiblesse ;
- demander une flamme suppose de croire son porteur là : dans le noir, on ne retrouve personne
  (manque déjà relevé) ; on n'allume pas sa lampe à celle d'un autre sans la lui emprunter ;
- inspecter dans le noir compte encore comme une ronde ; seul crocheter demande d'y voir ;
- une lampe n'a pas de contenance : chaque charge ajoute sa durée ;
- une lampe prêtée reste celle d'autrui : l'allumer est une faute (prêts, manque déjà relevé).
