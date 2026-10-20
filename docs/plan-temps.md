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
  fait se retourner : réflexe commun, qui prend le temps d'une rotation.
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
  pour ouvrir une porte attend ;
- les autres façons de placer le joueur (escalade, appui) ne vérifient pas encore la case.
- Mesure : le banc ne recueille pas la chronique de la première minute de chaque pas de cinq
  minutes (`c["minute"] > vue`) ; constaté, non corrigé ici.

## Hors périmètre

Assommer, tuer, ligoter, l'affrontement (étape « corps et force » de `docs/plan-social.md`) ;
courir et se faufiler (plus tard, sur ces mêmes durées).
