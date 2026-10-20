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
  en arrière 3 s ; une rotation de 45° 0,5 s (un demi-tour 2 s). Les gestes ont leur durée :
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
  réaction réaliste.
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
   délibération par événement et à la minute, perception par événement. Les sauvegardes
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

## Hors périmètre

Assommer, tuer, ligoter, l'affrontement (étape « corps et force » de `docs/plan-social.md`) ;
courir et se faufiler (plus tard, sur ces mêmes durées).
