# Plan : temps fin et orientation

Jalon décidé avant les caractères et valeurs (`docs/plan-social.md`) : c'est la fondation de
tout ce qui touche à la discrétion et à la force (arriver dans le dos, fuir, poursuivre,
assommer). Mesuré au banc sans joueur et à son récit, puis en jeu.

## Point de départ

- Une case fait 1 m. Le joueur fait un pas en 6 s : le moteur compte une minute tous les dix
  pas (`pas_depuis_minute`).
- Les PNJ vivent par minutes entières (`pnj.avancer`) : en une minute, ils rejoignent une case
  au contact de ce qu'ils visent (`_approcher`) ou passent dans la salle voisine (`_pas`).
  Pendant les neuf pas du joueur qui ne comptent pas de minute, ils sont figés ; puis tout le
  monde avance d'une minute d'un coup.
- Personne n'a d'orientation : chacun voit tout autour de lui.

## Décisions

- **L'unité est la seconde**, comptée en dixièmes (entiers, sans erreur d'arrondi) :
  `data["instant"]`. `data["minutes"]` reste, dérivé de l'instant, pour tout ce qui vit à la
  minute (besoins, croyances, rondes, feu, horloges).
- **Durées** (constantes du moteur, à régler au banc) : un pas en avant 1,5 s ; un pas de côté ou
  en arrière 3 s ; en diagonale, √2 fois plus (voir « Correctif : les diagonales ») ; une rotation
  de 45° 0,5 s (un demi-tour 2 s). Les gestes ont leur durée :
  prendre ou poser quelques secondes, ouvrir, verrouiller, alimenter un feu un peu plus ;
  crocheter, manger, se chauffer, attendre gardent leurs minutes.
- **Huit directions.** Chacun fait face à une direction ; il se tourne vers où il va, vers celui à
  qui il parle, vers ce qu'il manipule.
- **Champ de vision** : un cône de 120° devant soi, plus les cases immédiatement voisines sur les
  côtés. Derrière, rien. Joueur et PNJ ont la même règle.
- **L'ouïe ne dépend pas de l'orientation.** Un bruit proche venu d'une case qu'on ne voit pas
  fait se retourner : réflexe commun, qui prend le temps d'une rotation. (Remplacé depuis par une
  règle d'ouïe commune, qui interprète le bruit selon ce qu'on croit : `docs/plan-ouie.md`.)
- **Simulation par événements.** Chaque personnage a l'instant où son geste en cours finit ; le
  moteur traite toujours le prochain geste qui se termine. Quand le joueur agit, le monde avance
  de la durée de son geste, et tout ce qui se termine entre-temps est traité dans l'ordre. Quand
  rien ne bouge, l'horloge saute au prochain événement : le coût suit le nombre de gestes, pas
  le nombre de secondes.
- **Les PNJ réfléchissent** à la fin de leur plan, à un geste manqué, à un événement (un bruit,
  quelqu'un qui entre dans leur cône ou en sort, une porte), et au moins une fois par minute.
  Chaque geste est revalidé quand il commence. On finit son geste avant de réagir : un temps de
  réaction réaliste. *État* : jusqu'à la branche `deliberation-evenements`, seule la minute était
  faite (le choix du but n'avait lieu qu'à la frontière de minute) ; les autres déclencheurs le sont
  depuis (voir « Correctif : délibérer à l'événement »).
- **Les PNJ marchent case par case**, sur un chemin en cases qui traverse les salles et les
  portes ; `_approcher` et le passage d'une salle d'un coup disparaissent.
- **La perception se met à jour par événement** : celui qui bouge, et ceux qui pouvaient
  l'apercevoir (la case qu'il quitte, celle où il arrive).
- **Le joueur** : une flèche le tourne vers sa direction puis l'avance d'une case (s'il y fait
  déjà face, il avance) ; Maj + flèche fait un pas chassé, de côté ou en arrière, sans tourner ;
  une commande le fait se retourner ou regarder vers une direction sans bouger. La carte montre
  son orientation et son cône ; derrière lui, seulement ce dont il se souvient.

## Étapes

1. **L'horloge à l'instant et la file d'événements**, à comportement constant : les PNJ gardent
   leurs gestes d'une minute, planifiés comme événements. L'empreinte des quatre nuits du banc
   (chronique, mesures, état final) doit rester identique : la réforme du temps est vérifiée
   seule, avant de changer quoi que ce soit au comportement.
2. **Les PNJ case par case et les durées des gestes** : chemin en cases, un pas par 1,5 s,
   délibération par événement et à la minute (faite à la minute seulement ; par événement depuis
   `deliberation-evenements`), perception par événement. Les sauvegardes
   existantes se rechargent (l'instant se déduit des minutes).
3. **Orientation et cône** pour tous ; rotations et leur durée ; se retourner au bruit.
4. **Le joueur sur la même horloge** : flèches, Maj + flèche, se retourner, carte avec cône ;
   ce que Luna reçoit (ce que le joueur voit) suit le cône.
5. **La surprise** : témoins jugés par les cônes ; vols dans le dos ; une poursuite et une fuite
   au banc.

## Critères

- **Pas de perte** (banc, 4 graines × 8 h, récit) : aucune violation ni usurpation ; pas plus de
  minutes urgentes sans recours ; mêmes sortes d'histoires (demander avant de voler, servir,
  entretenir le feu, prévenir).
- **Vitesse** : une nuit en moins de 10 s ; la suite de tests sans dérive notable.
- **En jeu** : les PNJ bougent entre deux pas du joueur ; on peut arriver dans le dos d'un PNJ
  qui regarde ailleurs ; un PNJ qui entend des pas derrière lui se retourne ; ce qui est affiché
  et raconté reste ce que le joueur voit, après rechargement compris.

## Risques

- **Le coût** : plus de gestes à traiter. La file d'événements, le cône (moins de cases) et le
  cache de vue le compensent ; mesuré à chaque étape.
- **Les tests** écrits à la minute (un PNJ qui atteint sa cible en une minute) : à reprendre sur
  l'état atteint, pas sur l'instant.
- **Les sauvegardes** : migration de l'horloge et de l'orientation (par défaut, face au centre
  de la salle).
- **Le rendu** : la carte, le récit de Luna et le contrôle narratif doivent suivre le cône du
  joueur, sans fuite de ce qu'il ne voit pas.

## Correctif : la marche (branche `temps-fin-marche`)

Une relecture du jalon a montré quatre défauts de la marche des PNJ ; chacun est corrigé par une
règle commune, vérifiée sur le cas réel et un autre cas de même nature (`tests/test_marche.py`,
état du monde après rechargement).

- **Aucun geste ne s'achève sur une case occupée** (joueur ou personnage). Le trajet traverse
  les autres ; le pas qui mène sur la case de quelqu'un se poursuit, dans le même geste et pour
  la durée des deux pas, jusqu'à la case libre suivante. Si une porte fermée suit cette case, il
  contourne, ou attend qu'on lui laisse le passage. Arriver dans une salle, c'est donc s'arrêter
  sur une case libre. Le joueur ne marche pas non plus sur un PNJ (refus avec `attendu`).
  `Monde.verifier` refuse deux personnages sur une case ; une ancienne partie superposée
  s'écarte vers la case libre la plus proche au chargement. Cas réels : Gorm alerté vers
  l'antichambre dont le joueur, puis Aubin, occupe le seuil.
- **Tout contact passe par la marche.** Ce qu'un geste touche se déduit du geste
  (`_a_toucher`) : sa cible, objet ou personne à qui l'on parle, sauf se chauffer qui agit à
  distance ; un outil fixe s'emploie sur place, un outil mobile en main. Le PNJ marche jusqu'à
  avoir tout à portée ; la vérification de portée ne le déplace plus (`_approcher` d'un bond
  est retiré). Cas réels : allumer sa lanterne au brasero, éteindre le brasero (absent de
  l'ancienne liste de contact).
- **Le trajet en cases est le seul juge du passage** quand le PNJ a une position. Sans trajet,
  c'est un geste manqué : il apprend les obstacles qui coupent le chemin (croyance de lieu,
  source « essai ») ; le chemin par salles, qui sert à planifier, évite tout passage dont il
  croit un seuil barré ; le réflexe cesse, la stratégie tombe, un autre but patiente puis
  renonce (`PATIENCE`). Cas réels : obstacle sur le seuil, de chaque côté du passage.
- **On marche vers ce qu'on croit, puis on constate sur place.** La destination est la case
  crue (là où il l'a vu ; une porte ou un objet fixe, à sa place connue du lieu) ; il n'est
  jamais guidé par la position réelle d'une chose qu'il ne perçoit pas. S'il la croit dans la
  salle sans savoir où, il la parcourt des yeux. Il ne se tourne vers la cible que s'il la
  touche ou la voit. Cas réels : le marteau déplacé hors de sa vue ; Ilse partie ailleurs.

Banc (4 graines × 8 h) : aucune violation (le contrôle des cases tourne à chaque pas du banc),
aucune usurpation. Moyennes avant → après : gestes 121 → 129, événements distincts 20 → 22,
échanges 6,5 → 8, vols vus 1,5 → 5,3, confidences 1 → 3,5, minutes urgentes oisives 400 → 420
(graine 7 −60, graine 2024 +110). Marcher jusqu'à la réserve ou jusqu'à quelqu'un prend du
temps : les gestes illicites ont plus de témoins, qui en parlent. Les minutes oisives suivent
des jets différents (graine 2024 : la demande d'Ilse à Gorm est refusée au jet à la minute 250
au lieu d'être promise, elle n'est servie qu'à 371). Même temps de calcul par nuit.

Limites :
- le trajet lui-même contourne les obstacles réels, même ceux que le PNJ n'a pas vus ;
- le chemin par salles ne connaît d'un obstacle que le seuil qu'il barre : un obstacle qui
  coupe une salle en deux donne un geste manqué à chaque minute, jusqu'au renoncement ;
- personne ne s'écarte pour laisser passer : un PNJ qui doit s'arrêter sur la case d'un autre
  pour ouvrir une porte attend. Corrigé ensuite (branche `laisser-passer`, voir « Correctif :
  laisser passer ») ;
- les autres façons de placer le joueur (escalade, appui) ne vérifient pas encore la case.
- Mesure : le banc ne recueille pas la chronique de la première minute de chaque pas de cinq
  minutes (`c["minute"] > vue`) ; constaté, non corrigé ici.
## Correctif : laisser passer (branche `laisser-passer`)

Cas réel (partie de l'utilisateur) : Brune, désœuvrée sur le seuil du refuge, barrait la seule
sortie au joueur. « Je demande à Brune de se pousser » : Luna lui faisait promettre de bouger,
mais rien ne la déplaçait, et Luna répétait ensuite qu'elle l'avait promis ; « je la pousse »
était refusé, faute d'action. Un PNJ ne bougeait que pour ses propres buts ; un PNJ en attendait
un autre qui le bloquait. Trois règles communes, joueur compris (`donjon/passage.py`, détail dans
`docs/mecaniques.md`, « Laisser passer, demander le passage, pousser ») :

- **Laisser passer.** Qui doit s'arrêter sur la case d'un PNJ (le pas du joueur, la case d'où un
  PNJ ouvre une porte ou atteint ce qu'il touche) le voit s'écarter d'une case, hors de son
  chemin, le temps d'un pas de côté, et passer d'abord ; sauf raison de rester (un geste en cours
  là où il se tient, dont la porte qu'il va ouvrir) ou refus d'aider (méfiance, fierté qui
  l'emporte de 30 points sur l'altruisme). Le pas du joueur attend ce pas de côté, ou il est
  refusé avec un `attendu` qui dit pourquoi et ce qui reste possible.
- **Demander le passage** : contenu de parole typé `passage` ; le moteur tranche (méfiance,
  raison de rester, place, puis jet de persuasion pour l'orgueilleux) et le PNJ s'écarte
  vraiment avant que Luna ne fasse répondre le personnage d'après cette issue.
- **Pousser** : action `pousser` (commande `pousser <personnage> [vers <direction>]`), jet de
  FOR opposé, 3 s ; réussi, la victime recule d'une case hors du chemin de l'auteur. Contrainte
  légère : victime et témoins (registre des gestes en cours) cessent de croire l'auteur fiable.
  La douceur 100 l'interdit ; sinon c'est une faute au prix de la douceur. Un PNJ bloqué attend
  qu'on s'écarte, demande, puis pousse si ses valeurs le permettent, sinon patiente et renonce à
  la longue ; il prie le joueur de le laisser passer, et ne le pousse qu'après 30 s sans
  réponse.

Vérifié (`tests/test_passage.py`, état et texte lu après rechargement) : le cas réel reconstruit
(Brune s'écarte du seuil, le joueur sort du refuge) et Ilse au milieu du refuge ; Brune méfiante,
ou occupée à prendre les planches, qui reste ; la demande acceptée, refusée au jet, refusée par
méfiance ; la poussée réussie (Brune écartée du seuil, Ilse témoin, Aubin qui l'apprend d'elle)
et manquée ; deux PNJ à la porte étroite du palier (Aubin s'écarte pour Gorm ; méfiant, il
refuse et Gorm, doux, patiente ; un Gorm brutal le pousse sous les yeux d'Ilse ; deux qui vont à
la même porte passent l'un après l'autre) ; le joueur sur la case de la porte, prié de laisser
passer, puis poussé par un Gorm brutal. Luna, sur la sauvegarde réelle : « je demande à Brune de
se pousser » donne une parole typée `passage`, Brune s'écarte et la sortie est libre ; méfiante,
elle refuse et la réplique le dit ; « je la pousse » donne l'action `pousser`, présentée avec son
jet opposé avant « tenter ».

Bancs : Relais (8 graines), mine et auberge (4 graines) identiques à `main`, aucune violation ni
usurpation : personne n'y reste immobile sur la case d'arrêt d'un autre (les PNJ se traversent en
marchant). Un premier essai faisait s'écarter, à l'auberge, Odile et Hugues l'un pour l'autre
devant la porte de l'étable, sans fin (530 écarts par nuit) : d'où les deux règles « la porte
qu'il va ouvrir le retient » et « celui qu'il laisse passer passe d'abord ». Joueur posté sur une
porte : au Relais (`--joueur crypte`), 1,25 demande de passage par nuit, renoncements 1 → 1,25 ;
à l'auberge (`--joueur cuisine`, la porte du cellier), 6,25 demandes, renoncements 1 → 7 (avant,
ils attendaient sans fin, sans rien entreprendre d'autre), minutes urgentes oisives 778 → 988 ;
aucune poussée, ces PNJ ayant la douceur entière.

Limites :
- les PNJ se traversent toujours en marchant ; seules la case où l'on s'arrête (porte à ouvrir,
  ce qu'on touche) et le pas du joueur appellent ces règles ;
- le choix de pousser se fait sur place, dans la marche, au prix que le planificateur donne aux
  fautes (`caractere.prix_faute`, douceur) ; la recherche du planificateur, qui raisonne par
  salles, ne prévoit ni de pousser ni de contourner quelqu'un qui refuse ;
- on ne s'écarte que d'une case, dans sa salle : dans une impasse large d'une case, personne ne
  peut laisser passer (« place ») ;
- s'écarter de soi-même ne demande pas de percevoir le passant (il est au contact) ;
- garder un lieu ne retient pas sur une case (garder, c'est se tenir dans la salle) ;
- demander à un tiers de faire bouger quelqu'un n'est pas modélisé (un `passage` dont le sujet
  n'est pas l'interlocuteur reste un propos) ; qu'une réplique ne promette pas un déplacement
  non décidé n'est garanti que par la consigne et le contenu typé (Luna a repris une fois « je
  vais me pousser » de la conversation, alors que Brune bougeait) ;
- un essai avec Luna sur trois s'est conclu par la réponse de repli « Je ne peux pas encore
  répondre avec certitude » (contrôle narratif, sans trace : cause non établie), comme deux fois
  dans la partie réelle ;
- le joueur prié de laisser passer n'a pas de réponse typée : rester 30 s vaut refus.

## Après relecture : le temps sans état caché (branche `temps-fin-etat`)

Une relecture du jalon a montré que le monde dépendait du découpage des actions du joueur :
chaque action travaille sur une copie de `data`, et des états rangés hors de `data` étaient
perdus à chaque action. Règle retenue : **tout ce dont dépend la suite est dans `data`**,
sauvegardé et contrôlé par `Monde.verifier` ; le même laps de temps, attendu d'un bloc ou
découpé en petits gestes, rechargé ou non en route, donne le même monde.

- **Tour d'horizon** avant un geste sans témoin : dans l'esprit du PNJ (`balayage` : salle,
  case, instant). Avant, Brune refaisait un tour à chaque rotation du joueur et ne crochetait
  jamais.
- **Pas feutré** : il se lit dans l'intention (une étape `sans_temoin`), sans autre état.
- **Gestes en cours** : un seul registre, joueur compris (`data["gestes_en_cours"]` : auteur,
  geste, objet, instant de fin, témoins), gardé jusqu'à l'instant de fin, d'une action du joueur
  à l'autre. Un témoin est quiconque voit l'auteur pendant la durée du geste. Pour le joueur, ceux
  qui le regardent quand il commence sont départagés par son jet (comme avant) ; qui se tourne
  vers lui ensuite est témoin comme d'un geste de PNJ, et le joueur le sait s'il le voit
  (« X t'a vu faire »). Le message de vol ne promet plus « sans être remarqué ».
- **Bruits datés à l'instant** (dixièmes de seconde) et filtrés depuis le début du geste du
  joueur : une voix pendant une rotation de 2 s s'entend, même sans minute franchie. Les bruits
  des anciennes sauvegardes sont migrés (minute × 600).
- **Interlocuteur** : un personnage que le joueur perçoit, vu, ou entendu pendant son dernier
  geste (`data["entendus"]`) et assez près pour l'entendre. Qui se tait dans son dos ou dans le
  noir n'est plus livré au MJ (contexte, locuteurs autorisés, conversations).
- **Perception par événement** : après chaque geste d'un PNJ, tous les PNJ revoient ce qu'ils
  voient (la vue est en cache), au lieu d'attendre leur propre geste ou la minute. Sans cela,
  les actions du joueur, qui font percevoir tout le monde, rafraîchissaient les croyances plus
  souvent quand elles étaient courtes.

Vérifié (`tests/test_temps_etat.py`, après rechargement) : Brune et la réserve, puis le Relais
livré à lui-même (5 min d'un bloc contre 150 rotations rechargées en route, état des PNJ, objets,
chronique, registre et jets identiques ; 30 min vérifiées hors suite) ; voix pendant une rotation
et pendant un pas ; PNJ muet dans le dos, PNJ devant lui dans le noir, PNJ entendu ; témoin
tardif d'un vol du joueur ; geste de PNJ à cheval sur deux actions. Banc (4 graines × 8 h) :
identique à `main` avant la perception par événement ; après, aucune usurpation, minutes
urgentes sans recours 370 (400), échanges 10 (6,5), confidences 4,5 (1), rumeurs crues 3,25
(0,75), vols vus 4 (1,5).

Limites :
- L'humeur affichée d'un PNJ (calme, inquiet, méfiant) est recalculée à chaque action du joueur
  pour ceux qui sont à portée de voix : c'est un rendu, sans effet sur les PNJ, mais il dépend
  du découpage.
- Le joueur garde un jet de DEX contre ceux qui le regardent quand il commence ; un PNJ n'en a
  pas. Le seul geste illicite du joueur au registre est le vol (prendre le bien d'autrui).
- Un PNJ dont le geste n'a jamais été daté (partie neuve, ancienne sauvegarde) agit à l'instant
  même où commence la première action : ce bruit-là n'est pas entendu.
- « Entendu » vaut pour le dernier geste du joueur : un tour de dialogue sans action garde ce
  qu'il a entendu ; l'action suivante le remplace.

## Correctif : les diagonales (branche `diagonales`)

Constat de l'utilisateur : un pas durait 1,5 s quelle que soit sa direction et les chemins prenaient
le moins de pas, si bien qu'un trajet en diagonale allait ~41 % trop vite ; les portées (lumière,
ouïe, parole « de près ») se mesuraient en Tchebychev : une diagonale portait 41 % plus loin et les
halos de lumière étaient carrés. Trois règles communes, joueur et PNJ :

- **Durée d'un pas selon son vecteur** (`temps.duree_pas`) : l'allure pour un pas droit (pas 1,5 s,
  chassé ou feutré 3 s, `pnj.PAS`), √2 fois l'allure en diagonale, arrondie au dixième de seconde le
  plus proche, en entiers (`geometrie.racine` : 15 → 21, 30 → 42). Employée par le pas du joueur
  à toute allure, chaque pas d'un geste de PNJ (pas enchaînés compris) et le pas de côté de qui
  laisse passer (`passage.duree_ecart`).
- **Chemins au plus court en temps** : `spatial.trajet` est une recherche au moindre coût (le coût
  d'un pas est sa durée ; à coût égal, l'ordre de découverte, sens dans l'ordre trié de
  `VECTEURS`) ; le chemin du clic de la page (`chemin`) suit la même règle et le même ordre. On ne
  coupe toujours pas l'angle d'un mur en diagonale. Le planificateur raisonne par salles (coût
  d'aller : nombre de salles) : il n'estime pas de durée en cases, rien n'y change.
- **Portées en distance réelle** (`geometrie.distance` : euclidienne arrondie à la case la plus
  proche, en entiers) : lumière directe (`PORTEES` pleine/pénombre), portée de vue (`PORTEE_VUE`),
  murs vus, ouïe (`ouie.distance` : paliers, `PROCHE`, `PRES_DE`), parole « de près »
  (`pnj.de_pres`), rejoindre un proche, la case libre la plus proche ; dans la page, le rayon des
  cônes des autres. Les seuils restent en cases ; une case voisine en diagonale est à 1, donc au
  contact (prendre, toucher, `proche`, inchangés). Deux cases en diagonale sont à 3, quatre à 6.
  Le cône de vision est inchangé.

Vérifié (`tests/test_diagonales.py`, état après rechargement) : quatre pas droits 6 s, quatre en
diagonale 8,4 s, pour le joueur au pas, au pas chassé et au pas feutré ; pour un PNJ au pas et au
pas feutré, et un geste de deux pas enchaînés à travers la case d'Ilse (4,2 s en biais, 3 s droit) ;
le chemin le plus rapide plutôt que le moins de pas (deux buts : trois diagonales, 6,3 s, ou quatre
pas droits, 6 s ; un plan où le moins de pas, 12,3 s, passe au sud et le plus rapide, 12 s, au nord),
par le moteur et par la page ; le halo de la lanterne est rond ; des pas qui s'achèvent à cinq cases
dans le dos d'Aubin le font se retourner, à cinq cases en diagonale (7 en distance réelle) non ; la
voix « de près » en disque. Les caches (`spatial.VERIFICATION = 1`, `planification.VERIFIER`) ont
tenu une nuit du Relais (graine 1985) et une de l'auberge (graine 42) sans écart. Un test d'avant
(Brune marche vers le marteau qu'elle croit là) suivait le zigzag du moins de pas : en allant droit,
elle voit dès son premier pas qu'il n'y est pas ; le test suit désormais sa croyance.

Bancs (8 h ; Relais 8 graines, mine, auberge, crue 4), avant → après : aucune usurpation, aucune
violation (l'état est vérifié à chaque pas), même temps de calcul (Relais 12 → 10 s, mine 17 → 17,
auberge 38 → 36, crue 14 → 13).

| | Relais (8) | Mine (4) | Auberge (4) | Crue (4) |
|---|---|---|---|---|
| gestes | 148 → 145 | 193 → 190 | 494 → 467 | 255 → 207 |
| minutes urgentes sans recours | 432 → 428 | 604 → 668 | 584 → 589 | 275 → 335 |
| échanges | 7,8 → 7,6 | 38,5 → 33,5 | 22 → 28,8 | 8 → 9,5 |
| vols vus | 2,9 → 8,1 | 1,8 → 0,5 | 2,3 → 3 | 2,5 → 7,3 |
| retournements au bruit | 125 → 150 | 239 → 230 | 227 → 167 | 151 → 120 |
| bruits inconnus retenus | 48 → 54 | 82 → 71 | 169 → 163 | 111 → 93 |
| allés voir | 7,6 → 10 | 29,5 → 27,5 | 85 → 76 | 32 → 20 |
| jets | 7,6 → 8,1 | 11,5 → 9 | 161 → 127 | 11 → 9,8 |

Écarts :
- **Vols vus (Relais, crue)** : avant, Brune gagnait la réserve par le zigzag du moins de pas et
  crochetait à la minute 7 tournée vers le mur, sous les yeux d'Aubin et d'Ilse qu'elle ne voyait
  pas. Par le chemin direct, elle arrive face à eux, les voit et attend (`sans_temoin`) ; elle
  s'y remet vers la minute 122, quand elle se croit seule, mais Gorm et Ilse la voient depuis
  l'ombre ; cette fois elle réussit : crocheter, ouvrir et manger font trois gestes vus par deux
  témoins (graine 500 : 9 → 30). Moins de méfiances précoces, plus de vols aboutis.
- **Ouïe** : un bruit en diagonale vient de plus loin ; à l'auberge et à la crue, moins de
  retournements, de bruits retenus et d'allers voir (d'où, à la crue, moins de gestes et plus de
  minutes urgentes sans recours, et à l'auberge moins de jets : Lucien s'acharne moins souvent sur
  le coffre). Au Relais, davantage, par la scène de Brune ci-dessus.
- **Mine** : minutes sans recours 604 → 668 en moyenne, mais d'une graine à l'autre de −405 à +430 :
  des jets à d'autres instants ; pas de tendance propre à la géométrie.

Limites :
- Le coût d'un chemin ne compte que les pas : le temps de se tourner (0,5 s par 45°) n'y entre
  pas ; deux chemins de même durée de pas sont départagés par l'ordre de découverte, pas par le
  nombre de rotations.
- L'ouïe perd un cran par distance doublée (paliers 1, 3, 6, 12, 24) : à quatre cases, droit
  (4) ou en diagonale (6), le palier est le même ; la différence se voit à trois cases (3 contre
  4) et à cinq (5 contre 7).
- La distance est arrondie à la case : un disque de rayon r contient les cases à moins de r + ½ ;
  la lumière porte à 6 cases en diagonale pour une portée de 8 (8,5 réel), pas 5,66.
- Le pas de côté de qui laisse passer prend sa durée ; le passant attend toujours un `PAS` droit
  après lui (`passage.s_ecarter`), et la poussée garde sa durée fixe (`POUSSEE`).

## Correctif : délibérer à l'événement (branche `deliberation-evenements`)

Constat : la décision « les PNJ réfléchissent à la fin de leur plan, à un geste manqué, à un
événement, et au moins une fois par minute » n'était faite que pour la minute. `pnj._avancer`
n'appelait `deliberer` qu'à la frontière de minute, pour tous à la fois dans l'ordre des
identifiants ; un PNJ au plan fini, au geste manqué ou désœuvré attendait la minute suivante
(jusqu'à 59,9 s d'inaction), et un voleur vu, un appel ou une porte ouverte sous ses yeux ne
changeaient son but qu'à la minute suivante.

**Ce qui est fait** (décision de l'utilisateur, la version simple) :
- **Deux temps de la délibération** (`deliberation.py`) : `deliberer` fait vivre la minute (dérive des
  besoins, corps, sécurité ressentie, effet de seuil) puis appelle `choisir`, le choix du but et du
  plan, qui ne fait passer aucun temps. `choisir` relit aussi, à l'instant, ce qu'il croit de ses
  charges et de ses paroles (`constater_pulsions` : une pulsion rompue sous ses yeux ;
  `echanges.engagements_echus` : une parole tenue, échue, impossible) et l'attente d'être rejoint.
- **Fin du plan, geste manqué** (`pnj.agir` rend désormais `(durée, issue, étape manquée)` : `GESTE`,
  `ATTENTE`, `FIN`, `MANQUE`) : il choisit aussitôt la suite et commence le geste suivant au même
  instant. Un geste manqué ne se retente pas avant la minute suivante, même réveillé entre-temps
  (`esprit["manque"]`, comparé sans ce que le plan ajoute à l'étape).
- **Événements** (`esprits.reconsiderer`, qui date l'éveil dans l'esprit) : un bruit interprété
  (`ouie._bruit_inconnu`, `_se_tourner`, le bruit de qui l'on se méfie), quelqu'un qui entre dans
  son regard ou en sort, l'état visible d'une chose vue qui change (porte, contenant, feu), une
  absence constatée, son bien aux mains d'un autre (`esprits._percevoir`, `_vu_porter`), un geste
  illicite sous ses yeux (`pnj._temoins`), une parole qui lui est adressée (`ouie.retentir`) ou
  surprise et qui lui apprend quelque chose (`social.retenir_parole`). Il choisit de nouveau à la fin
  de son geste en cours, ou aussitôt s'il ne fait qu'attendre (`esprit["veille"]` : désœuvré,
  guettant une occasion, assis, au feu, à l'abri) ; une rotation vers un bruit, un pas de côté
  restent des gestes. Ce qu'il voit changer par son propre geste (ses pas, se tourner, son tour
  d'horizon, une porte qu'il ouvre) ne l'éveille pas : son plan le prévoyait.
- **Le filet de la minute** reste : `deliberer` pour chacun à chaque frontière, pour ce qui monte peu
  à peu. Aucun franchissement de seuil n'est programmé comme événement.
- **Gestes qui durent** : se reposer, se chauffer, s'abriter rendent « en cours » (None), achevé
  (True) ou impossible (False) ; achevé ou impossible, il choisit aussitôt la suite ; en cours, son
  attente cède à un événement (un abri devenu noir se quitte à l'instant).
- **L'ordre** : à des instants distincts, dans l'ordre du temps ; au même instant, dans l'ordre des
  identifiants (déterministe). Une garde arrête la boucle si un même instant se retraitait sans fin.
- **Même laps découpé, même monde** : `veille`, `eveil`, `manque`, `en_vue` (ce qu'il voit, établi
  par sa première perception sans l'éveiller) et `patience` sont dans l'esprit, contrôlés par
  `esprits.verifier`. Deux défauts de découpage révélés et corrigés : la perception du résultat
  d'une action du joueur se faisait après le passage du temps (datée de la fin de l'action, selon
  son découpage) ; elle se fait au début, comme le monde des PNJ à cet instant (`moteur`), et ce
  qu'ils en voient, ils y réagissent pendant l'action (l'instant même de son début appartient à
  l'action précédente, `ecoute.entendus`).
- **Ce qui en dépendait** : guetter son occasion se compte une fois par minute (`esprit["patience"]`)
  et, réveillé par un événement, on regarde de nouveau autour de soi (un témoin a pu arriver ou
  partir) ; un bruit du lieu où l'on est se va voir quand on y est venu pour lui (`_voir_en_cours` :
  avant, le but tombait à l'arrivée, avant d'avoir regardé) ; une parole n'est tenue que sur ce qu'on
  a constaté une minute après l'avoir donnée (`echanges.tenu` : les croyances sont datées à la
  minute) ; la chronique porte l'instant (`instant`), dont le récit se sert pour attribuer les
  gestes d'un but choisi et quitté dans la même minute ; `recit_pnj` et `rejeu` observent `choisir`.

**Deux boucles de l'audit des nuits** (`docs/audit-nuits.md`), dans la délibération :
- B1 : un appel à l'aide attend sa réponse ; tant que dure le désarroi qui l'a fait lancer, il ne se
  répète pas, que quelqu'un soit venu sans l'apaiser ou que personne ne vienne ; rassuré depuis
  (sous `DESESPOIR`, sans menace), un nouveau désarroi rappelle (`appeler_a_l_aide`, l'appel retenu
  porte `apaise`).
- B3 : on prévient d'un fait que la victime ignore : qu'un auteur n'est pas fiable, s'il ne le lui a
  jamais dit ; où sont ses biens, s'il ne le lui a pas dit depuis qu'il le croit (`_a_dire`,
  `_deja_dit`). Chaque minute d'un même crochetage vu ne relance plus l'avertissement.

**Vérifié** après rechargement (`tests/test_deliberation_evenements.py`, 18 tests) : plan fini à
2,5 s (Gorm prend la clé, part à sa ronde ; Aubin pose ses planches) ; geste manqué (marteau
absent ; porte crue ouverte, verrouillée) et le même geste manqué non retenté avant la minute ;
voleur entrant dans le regard (Brune, les vivres de Gorm en main) et crochetage sous ses yeux ;
bruit à voir et appel du joueur (Gorm part dès le bruit) ; réserve ouverte sous les yeux de Brune,
brasero éteint sous ceux de Gorm (il le rallume) ; abri devenu noir quitté aussitôt ; filet de la
minute pour une faim qui franchit son seuil en marchant ; se chauffer cesse au seuil (déjà vrai à la
minute sur `main`) ; même laps découpé ; les deux boucles. `VERIFIER` et `spatial.VERIFICATION`
sur une nuit de 8 h de chaque scénario (graine 1985), après fusion de `main` 4261bf5 (`verifier-eau`) :
aucun écart.

**Bancs** (8 h, départ tiré, `main` 4261bf5 puis la branche, l'un après l'autre, 4 processus ; Relais
8 graines `--joueur chambre_cloche`, mine `--joueur galerie`, auberge `--joueur dortoir`, crue `--joueur
chambre_cloche` 4 graines ; `main` → branche, par nuit) :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| événements distincts | 38,1 → 37,25 | 65,75 → 65,5 | 113,75 → 101,5 | 40,5 → 42,5 |
| échanges | 16,6 → 15,4 | 45,75 → 43,75 | 76 → 81,25 | 20,5 → 21,5 |
| vols vus (témoins) | 1 (2,6) → 1 (2,75) | 0,75 (2,25) → 0,75 (3,25) | 1,25 (3,75) → 1 (1,5) | 0 (0) → 0,25 (0,5) |
| allés voir | 10,1 → 10,25 | 12 → 15,5 | 28,75 → 38,5 | 12,5 → 14,5 |
| minutes sans recours | 58,75 → 60,6 | 43,75 → 56,25 | 40 → 75 | 16,25 → 32,5 |
| minutes en attente | 59,4 → 52,5 | 285 → 240 | 311 → 309 | 474 → 472,5 |
| appels à l'aide | 0,375 → 0,375 | 2,5 → 3,75 | 2 → 1,25 | 0,25 → 0,25 |
| choix : minute + événement | 1 920 → 1 920 + 917 | 3 360 → 3 360 + 3 016 | 3 840 → 3 840 + 2 153 | 1 920 → 1 920 + 821 |
| recherches (neuves) | 687 (259) → 1 145 (312) | 1 359 (539) → 4 073 (2 229) | 1 506 (722) → 3 647 (1 070) | 473 (247) → 837 (349) |
| part du planificateur | 16 % → 20 % | 42 % → 42 % | 33 % → 41 % | 14 % → 18 % |
| temps d'une nuit | 10,5 → 9,7 s | 25 → 34 s | 26,8 → 31,9 s | 10,3 → 12 s |

Aucune usurpation ni violation (le banc vérifie le monde à chaque pas). Les PNJ réagissent dans
l'instant : on va voir plus souvent (+1 à +34 %), les témoins de vols augmentent sauf à l'auberge (on y
accourt au bruit et le voleur, qui se sait entendu, attend : moins de vols vus), les minutes en attente
baissent ou restent égales. Les choix entre deux minutes sont un tiers à la moitié de tous les choix ;
la mémoire du planificateur en reprend la plupart. À la mine, les recherches neuves quadruplent, mais
ce sont surtout des recherches d'une étape (`aller`, le chemin vers un abri, ~1 nœud) : la nuit coûte
+36 % (le choix lui-même, à chaque fois, construit une vue du planificateur pour l'argent et l'abri) ;
ailleurs le temps reste dans la dispersion (−8 % à +19 %). Une première version, où ce qu'il voyait
changer de son propre geste l'éveillait aussi, coûtait +70 % à l'auberge : d'où cette règle. Écarts
expliqués : « sans recours » monte surtout par Lucien (auberge) qui guette son occasion pour le ballot,
plus souvent vu ou entendu, renonce au bout de `PATIENCE` puis attend son répit (`REPIT`, 60 min) ; à la
crue et au Relais, quelques minutes de plans possibles non entrepris pendant un répit.

**Limites et suite** :
- Restent à la minute : besoins et corps (faim, froid, fatigue, sécurité ressentie), combustion,
  crue, effet de seuil des besoins, échéance des paroles et des prêts, dettes soldées, flamme ménagée,
  appel à l'aide, horloges du scénario (déclenchées par le moteur à la fin d'une action), dates des
  croyances et souvenirs (la minute), répit après renoncement et patience (en minutes). Hors
  périmètre, à faire ensuite : corps, besoins, combustion et crue au temps réel ; horloges à leur
  instant ; croyances et souvenirs datés au dixième ; patience en temps.
- Un franchissement de seuil n'éveille personne (refusé pour l'instant) : un besoin qui presse entre
  deux minutes attend la minute.
- Ce qui change de son propre fait ne l'éveille pas : un PNJ qui découvre en marchant quelqu'un ou
  quelque chose qui changerait son but poursuit son plan jusqu'à sa fin, un geste manqué ou la
  minute (un geste illicite vu, son bien aux mains d'un autre l'éveillent quand même).
- Un geste manqué ne coûte que le temps déjà passé (une rotation, rien de plus) ; l'essai lui-même
  n'a pas de durée propre.
- La perception du résultat d'une action du joueur est datée de son début ; les croyances restant
  datées à la minute, un ordre fin d'une même minute peut encore dépendre du découpage hors des PNJ
  (horloges).
- Coût : chaque choix entre deux minutes refait les lectures du choix (une vue du planificateur
  pour l'argent, l'abri, des chemins d'une étape) même quand rien de ce qu'il lit n'a changé ; la
  mémoire n'épargne que les recherches. Une reprise du choix entier sur les mêmes entrées serait la
  suite à faire si le coût gênait (mine +36 %).
- Plus vifs, les PNJ font d'autres histoires : des tests de scène ont dû être retouchés (intention
  imposée sans motif, que le premier événement remplace ; scènes qui supposaient une minute d'inertie) ;
  chacun dit pourquoi.

## Correctif : le temps réel (branche `temps-reel`)

Constat (inventaire de « Délibérer à l'événement ») : les PNJ délibéraient à l'événement, mais le
reste tournait à l'instant pile de chaque minute. Les horloges du scénario n'étaient déclenchées
qu'à la fin d'une action du joueur : une attente de cinq minutes retardait la rafale de l'auberge, et
les PNJ vivaient comme si elle n'avait pas eu lieu. Le corps, la dérive des besoins et la sécurité
ressentie étaient échantillonnés à la frontière de minute : un PNJ qui traversait un couloir noir
entre deux minutes n'avait pas peur, un autre qui s'y tenait une seconde à la frontière en subissait
une minute entière ; l'effort ou le repos se lisaient du premier geste de son plan, pas des gestes
faits ; le corps du joueur ne changeait qu'au franchissement d'une minute, selon l'action qui la
franchissait. La patience comptait des appels (`passage`) ou des minutes où l'on y avait repensé
(`pnj._patienter`), pas le temps passé à attendre.

**Ce qui est fait** (le filet de délibération à la minute reste ; aucun franchissement de seuil n'est
programmé comme événement, décision de l'utilisateur) :
- **Les horloges à leur instant** (`horloges.declencher`, appelé par `pnj._avancer`) : à chaque
  frontière de minute franchie, avant la combustion et la délibération, et au début de la vie des
  PNJ pour une échéance déjà passée (la minute 0). Les PNJ qui voient l'effet le perçoivent à cet
  instant (un feu qui s'éteint sous leurs yeux les éveille) ; l'annonce va au joueur s'il est dans un
  des lieux, comme avant. Le moteur ne les déclenche plus à la fin de l'action.
- **Le temps vécu** (`donjon/vecu.py`, `corps["vecu"]` de chaque personnage qui a un corps, joueur
  compris) : l'état où il se trouve depuis un instant, son activité (`effort` d'un geste qui creuse,
  dont la marche ; `repos` ; rien), le chaud d'un foyer allumé dans sa salle, l'eau où il se tient, et,
  pour un PNJ qui ressent sa sécurité, ce qu'elle gagne ou perd par minute là où il est
  (`deliberation.ecart_securite` : le noir, la compagnie, la méfiance, l'eau, la menace). `solder`
  fait vivre le temps passé dans cet état : faim, fatigue, froid, séchage et trempe (`corps.vivre`,
  au prorata), dérive des besoins du profil, sécurité. Un PNJ solde à chacun de ses gestes (avant de
  choisir : il décide sur ses besoins à l'instant), note l'état où son geste le met (`noter` :
  l'activité du geste fait, `pnj.agir` la dit par `monde._activite`), et chaque frontière de minute
  solde puis relit les conditions (`vecu.minute`, appelé par `deliberer`). Le joueur note l'état de
  chaque action à son début (`moteur._terminer_etape`) ; un état inchangé continue sans rien solder,
  et chaque minute franchie le solde (`pnj._avancer`) avec ses messages (« Tu as faim. », la peine
  d'une heure à l'extrême, comptée en dixièmes). Ces instants ne dépendent pas du découpage des
  actions du joueur : le même laps, découpé autrement, donne le même monde. Se tourner sur place
  (`tourner`) ne creuse plus (`corps.CALMES`).
- **Le froid sec à 4 par heure** (`corps.CORPS`, décision du 2026-10-22 ; 2 avant).
- **La patience en temps** (`pnj.commencer_attente`, `compter_attente`) : guetter son occasion ou
  attendre qu'on lui fasse place ouvre une attente, datée dans l'esprit (`patience`) ; le temps
  passé s'ajoute à `intention["attente"]`, en dixièmes, à son geste suivant et à chaque frontière ; il
  renonce au-delà de `PATIENCE` minutes d'attente, quel que soit le nombre de fois qu'un événement
  l'a fait reconsidérer. Un autre but remet l'attente à zéro. **Le répit** se compte de l'instant du
  renoncement (`renoncements` en dixièmes, `REPIT` minutes).

**Vérifié** après rechargement (`tests/test_temps_reel.py`) : la rafale de l'auberge avancée à la
minute 2 pendant une attente de cinq minutes (Hugues voit l'âtre éteint à la minute 2) ; une horloge
qui éteint le brasero sous les yeux de Gorm, qui choisit de le rallumer à cet instant et le rallume
avant la fin de l'action ; la même horloge d'un bloc ou en rotations rechargées ; Ilse qui traverse
le noir pour gagner la lumière et Gorm dont la ronde passe au chaud, chacun à quatre phases de la
minute (0, 15, 30, 45 s) : même chemin, mêmes besoins à 0,005 près (avant, la phase décidait si la
traversée comptait) ; le corps du joueur qui marche puis se tourne, ou l'inverse, dans la même
minute : mêmes besoins, et la faim compte la marche à l'effort au dixième près ; le froid sec du
joueur et de Gorm ; Brune qui renonce après 30 minutes de guet comptées au temps, puis son répit ;
Gorm bloqué par le joueur, dont l'attente compte le temps et qui renonce au-delà ; la patience d'un
bloc ou découpée.

## Hors périmètre

Assommer, tuer, ligoter, l'affrontement (étape « corps et force » de `docs/plan-social.md`) ;
courir et se faufiler (plus tard, sur ces mêmes durées).
