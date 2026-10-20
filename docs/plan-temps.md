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

## Hors périmètre

Assommer, tuer, ligoter, l'affrontement (étape « corps et force » de `docs/plan-social.md`) ;
courir et se faufiler (plus tard, sur ces mêmes durées).
