# Scénario d'étude : la crue du Relais

Document de discussion, pas encore un jalon. Il décrit une situation qui doit mettre à
l'épreuve les PNJ (buts opposés, relations, menace commune) et en tire les mécanismes
généraux qui manquent au moteur. Rien n'y est un script : le scénario déclare des données
(personnages, croyances de départ, bornes de la crue, ressources), et ce qui arrive doit
naître des mécanismes communs. Les PNJ seront d'abord étudiés sans joueur, au banc.

## Ce que le scénario doit éprouver

- **Des buts opposés sur une même ressource** : ce qui sert à l'un prive l'autre.
- **Des croyances opposées sur l'avenir**, sans qu'aucune soit vraie d'avance : chacun agit
  sur son avis, et c'est la partie qui tranche.
- **Des relations qui pèsent** : qui l'on croit, qui l'on aide, avec qui l'on part.
- **Une menace commune** que personne ne peut ignorer, qui force à choisir, et qu'aucun ne
  peut affronter seul.
- **Des issues variées** d'une graine à l'autre, à partir d'un petit nombre de règles.

Critère principal : des comportements cohérents, variés et adaptatifs, sans méthode écrite
pour ce scénario.

## Le cadre

Aujourd'hui, le scénario n'établit presque rien autour du Relais : l'introduction (« Après la
rupture du pont, tu as rejoint à pied le Relais des crues par la digue […] Gorm préparait
l'accueil des habitants évacués »), les noms des salles, et la cloche qui « devait servir à
donner le signal depuis le refuge ». Le cadre qui suit est une proposition ; les noms sont
provisoires.

- **La vallée.** Une rivière en crue. D'un côté de la digue, le hameau des bateliers, sur la
  berge. De l'autre, en contrebas, le bourg, protégé par la digue, et le canal qui l'alimente
  et fait tourner le moulin d'Ilse. Derrière le bourg, le coteau, au sec.
- **Le Relais des crues** est la maison de garde de la digue, bâtie dans la digue : le refuge
  sur la crête, la conduite basse et la salle des vannes dans l'épaisseur du talus, au niveau
  du canal, la galerie de ronde en haut pour guetter l'eau. On y vend aussi aux bateliers qui
  passent (l'échoppe de Gorm).
- **Les vannes** sont des portes de bois dans la digue, entre la rivière et le canal. En crue
  on les ferme, mais elles sont vieilles et fuient. Si elles cèdent, l'eau envahit les salles
  basses, puis le canal, puis le bourg. Barrer les vannes, c'est les renforcer de planches et
  d'étais.
- **Les évacués** viennent du hameau, noyé le premier. Le pont est rompu ; ils ont suivi la
  digue jusqu'au Relais, seul bâtiment en dur.
- **La cloche** prévient le bourg, depuis la galerie, que les vannes vont céder, pour qu'il
  monte au coteau.
- **La barque** du Relais est amarrée à la salle des vannes pour l'entretien. Le Relais est
  une île : pont rompu, digue submergée par endroits. La barque ne descend pas la rivière (le
  courant charrie des troncs) : elle traverse les prés noyés jusqu'au coteau.

```
          coteau (sec)
              ↑   traversée en barque : prés noyés, courant de travers
   bourg ── canal ── moulin
              ║ digue ── RELAIS ── digue (submergée par endroits) ── pont rompu
   ~~~~~~~~~~ rivière en crue ~~~~~~~~~~
```

Données à changer : les altitudes (aujourd'hui toutes les salles sont à 0, sauf la galerie à
240 cm ; les salles basses doivent passer sous le refuge), la barque, l'introduction. Les
altitudes et l'introduction le sont dans le scénario dérivé `crue` (voir « Étape 3 faite ») ; le
Relais reste tel quel pour les tests et son banc.

## La menace

- **Un niveau d'eau**, quantité du monde, comparé à l'altitude de chaque salle. Une salle est
  d'abord **mouillée**, puis **noyée** : impraticable, feu éteint, objets légers perdus ou
  trempés.
- **Bornes déclarées, valeurs tirées.** Le scénario déclare des bornes pour la montée par
  heure, l'heure du pic et sa hauteur ; les valeurs sont tirées au départ de la graine, par un
  tirage séparé (`seed:crue`) que les jets de la partie ne décalent pas. Personne ne les connaît,
  ni l'auteur pour une graine donnée, ni le joueur qui rejoue : selon la partie, Gorm a raison
  de croire que le Relais tient, ou Aubin de craindre les vannes. Aujourd'hui la graine ne sert
  qu'aux jets de dés (`Monde.d20`) ; c'en serait un usage nouveau.
- **Ce qu'on en perçoit** : l'eau vue dans une salle, son bruit, la mesure aux vannes qui donne
  une tendance. Chacun s'en fait une croyance (niveau, vitesse), qui peut être fausse ou
  périmée.
- **Ce qui la change** : barrer les vannes ralentit la montée dans les salles basses tant que le
  barrage tient ; un barrage fait avec trop peu peut céder.
- **Les vannes cèdent, pas la digue** : le Relais est en pierre, il tient. L'eau monte dans les
  salles basses, puis dans le refuge. **La galerie reste toujours sèche** : dernier abri, froid ;
  son seul feu est le poêle du guet (branche `ressources`, ci-dessous). Personne ne meurt de ce seul fait ; le danger passe par les règles du corps (le
  froid, la faim, la fatigue extrêmes coûtent des PV) et par le courant (une traversée ratée).
  L'enjeu est l'état dans lequel on passe la nuit, et qui l'on a laissé derrière soi.
- **Le bourg**, hors scène : si l'alarme a sonné, il est monté au coteau ; sinon il est surpris.
  Le bilan de fin le dit.

## L'eau, le froid et le feu

- **Ce qui existe** (`donjon/corps.py`) : un personnage peut être trempé ; trempé, le froid
  monte de 10 par heure au lieu de 2. On sèche en restant 30 minutes de suite dans la salle d'un
  feu allumé. Aujourd'hui, seul l'état de départ mouille quelqu'un.
- **À ajouter** : entrer dans l'eau mouille ; une salle inondée refroidit selon la hauteur
  d'eau, ralentit, et empêche d'y faire du feu ou d'y poser un objet sans le mouiller.
- **Le feu devient vital**, et dispute le bois au barrage. Le brasero est dans la conduite
  basse, parmi les premières salles noyées.
- **Le brasero est déclaré fixe** (`mobile: false`, 20 kg de fer), un choix fait quand il n'était
  qu'un décor. Proposition : le rendre transportable, avec deux règles du moteur, un feu allumé
  ne se transporte pas, et une charge au-delà de ce qu'on porte demande deux personnes (le
  joueur porte 12 kg). Le monter à la galerie passe par la conduite, la salle des vannes, la
  porte étanche et l'escalier du palier : par les salles les plus menacées, donc avant de savoir
  si les vannes tiendront.
- **Un foyer improvisé** : du combustible sec, un sol hors de l'eau, de quoi allumer. N'importe
  quel lieu peut avoir un feu, la galerie comprise, si l'on y monte du bois resté sec. C'est un
  usage de plus pour la fabrication.
- Le bois sec devient la ressource de la nuit : brûler en bas maintenant, brûler en haut plus
  tard, ou barrer les vannes.

## Les recours

| Recours | Il faut | Ce que ça coûte |
|---|---|---|
| Barrer les vannes | des planches, un marteau, deux personnes, du temps | les planches ne brûleront pas ; on en sort trempé |
| Monter à la galerie | rien | froid, pas de feu sans bois monté ou brasero porté |
| Partir en barque | la clé de la chaîne, une lumière, un équipage de deux | deux places ; laisser les autres |
| Sonner l'alarme | la cloche, de la galerie | rien pour soi : c'est pour le bourg |
| Garder le feu | du bois ou des planches | ce qui brûle ne barre plus |

Ressources disputées : les **planches** d'Aubin, le **bois** de Gorm, les **4 parts** de vivres,
les **2 places** de la barque, la **lumière** (la lanterne du joueur, la torche, le fanal).

## La barque

Rien d'interdit à Brune en particulier : le départ a des conditions générales, et chacune
croise les buts des autres.

1. **Elle ne se mène pas seule dans le courant** : l'une rame, l'autre écarte les débris à la
   gaffe. Il faut convaincre un compagnon, qui prend l'une des deux places.
2. **Elle est enchaînée, et c'est Gorm qui garde la clé.** On la demande, on la vole, ou l'on
   crochète le cadenas, au risque d'être vu.
3. **La nuit, sans lumière**, la traversée est presque impossible. Le risque est un jet dont la
   difficulté dépend du courant, de la lumière et de l'équipage.
4. **Affamé ou gelé**, on a un malus (déjà dans le modèle du corps).

Partir, c'est quitter la partie : on est sauf, ses biens partent avec soi, la scène continue
sans soi, et le bilan dit qui est parti, avec qui.

## Les personnages

Chacun a un avis de départ, un but qui en découle, et ce qui pourrait le faire changer.

**Gorm**, gardien. Croit que la digue tient : elle a toujours tenu. Son devoir : ne pas partir
tant que des évacués sont attendus, garder le feu pour eux. Il tient son bois, ses vivres et la
clé de la barque. Respecte Aubin de longue date ; se méfie de Brune. *Levier* : l'eau vue dans
le refuge ; la parole d'Aubin, s'il le croit encore ; un service rendu au refuge.

**Aubin**, passeur. Il surveille les vannes et les voit fuir : il croit qu'elles céderont avant
le pic si on ne les barre pas. Il veut ses planches pour le barrage, ce qui le met face à Gorm
(le feu). Il ne peut pas barrer seul. Taciturne : il dit ce qu'il a vu, sans insister.
*Levier* : quelqu'un qui accepte de l'aider ; la vue d'un barrage qui cède.

**Brune**, batelière. Sa maison est noyée ; elle croit que seule la barque sauve. Elle sait la
mener ; personne d'autre ne le fait sans risque. Affamée, peu scrupuleuse. *Levier* : de quoi
manger ; une dette ; l'eau qui baisse.

**Ilse**, meunière. Pense à son moulin, donc au bourg. A peur ; suit celui qu'elle croit le plus
fiable, et répète ce qu'elle a vu et entendu : son avis fait pencher le groupe. *Levier* : la
confiance ; la peur, que le noir et l'eau aggravent.

Relations de départ (à régler) : Gorm et Aubin se font confiance ; Gorm se méfie de Brune ;
Ilse craint Brune et s'en remet à Gorm ; Aubin doit à Gorm son hébergement.

## S'influencer

**Ce qui existe** (`donjon/echanges.py`, `donjon/social.py`) : affirmer un fait (lieu, verrou,
fiabilité), rapporter ce qu'on a vu (rumeurs, trois bouches au plus), demander un objet ou une
part, confier une tâche (un objet dans une salle, verrouillé, un feu entretenu). Un jet de CHA
tranche, plus facile si l'auditeur croit le locuteur fiable. Une demande est refusée d'office
si l'auditeur se méfie, ou si l'objet lui est nécessaire (il sert son plan, c'est ce qu'il garde
ou sa clé).

**Ce que ça donne** : Brune ne peut pas obtenir la clé de Gorm (nécessaire, et méfiance), ni
demander à Ilse de la demander pour elle : une tâche confiée ne porte que sur l'état d'un objet,
le planificateur d'Ilse ne sait pas obtenir un objet porté par quelqu'un, et le moteur ne fait
jamais demander un objet (seulement des parts ; le reste vient du stratège, désactivé). On
donne des faits, pas des raisons ; l'influence ne fait qu'un pas ; une méfiance ne remonte
jamais.

**À ajouter** :
- **Une demande est une proposition** : ce que je demande, et pourquoi tu y gagnes. L'auditeur
  la juge d'après ses croyances et ses buts : ce qu'il perd, ce qu'il y gagne (un but servi,
  une contrepartie, une dette honorée), sa confiance que la promesse sera tenue. Le jet de CHA
  penche la balance.
- **Des avis** : une croyance sur ce qu'il faut faire (« les vannes céderont », « la digue
  tient »), avec sa confiance. On s'en convainc ; ce qu'on voit soi-même pèse plus que ce qu'on
  entend ; deux avis opposés font une dispute.
- **Obtenir un objet porté par quelqu'un** comme but que le planificateur sait atteindre
  (demander, échanger, prendre sans être vu, selon le caractère), et qu'on peut confier à un
  autre.
- **Des relations graduées** : affection, dette (un service rendu), rancune (un refus, un vol,
  un mensonge découvert) ; la confiance perdue peut se regagner.

Chemins de Brune vers la clé, avec ces règles : convaincre Gorm que les vannes vont céder (dur :
elle n'est pas fiable à ses yeux ; la parole d'Aubin ou l'eau vue pèseraient plus) ; servir ses
buts (« j'emmène Ilse au coteau »), avec une condition qu'il pose ; passer par Ilse, qu'il croit ;
regagner sa confiance par un service ; voler ou crocheter. Aucun n'est écrit pour elle.

## Déroulés possibles

Des exemples de ce qui devrait pouvoir arriver, pas des branches à écrire.

- Le pic tombe bas. Gorm garde le feu avec les planches, Aubin cède à contrecœur ; Brune, partie
  à minuit avec Ilse, a pris un risque pour rien ; le bilan le dit.
- Le pic tombe haut. Aubin convainc le joueur, ils barrent les vannes ; le refuge reste sec deux
  heures de plus ; Gorm, qui a vu l'eau monter, cède son bois pour les étayer.
- Brune propose une place à Ilse contre sa part de vivres ; Gorm le voit, refuse de servir
  Brune ; Ilse hésite entre les deux.
- Personne ne s'entend : le feu meurt dans la conduite noyée, tout le monde monte trempé à la
  galerie, et la cloche est la seule chose qui reste à faire.

## Mécanismes généraux à ajouter

1. **Planification par recherche** (piste GOAP) : les opérations déclarent conditions et effets
   sur les croyances, le profil donne les coûts. Préalable aux comportements nouveaux, sinon
   chaque recours devient une méthode écrite à la main.
2. **Niveau d'eau** : bornes déclarées, valeurs tirées, salles mouillées puis noyées,
   perception et croyances ; entrer dans l'eau mouille ; effets sur le feu et les objets.
3. **Le feu déplacé ou improvisé** : un feu allumé ne se transporte pas ; charge à deux ; foyer
   improvisé.
4. **Influence** : proposition jugée sur les buts de l'auditeur, avis, obtenir un objet porté
   par autrui, confier ce but.
5. **Relations graduées** : affection, dette, rancune, confiance qui se regagne.
6. **Agir ensemble** : une tâche à plusieurs (barrer, porter le brasero, mener la barque).
7. **Quitter la scène** : un départ fait sortir des personnages avec leurs biens ; places
   comptées ; une capacité (mener une barque).
8. **Fin de partie** : le pic passé, l'eau baisse ; un bilan, pas de fin écrite.

## Ce qui serait un script, à éviter

- Un événement déclenché par la présence du joueur, ou à une minute fixée pour faire avancer
  l'histoire (hors la crue elle-même, donnée du scénario).
- Une règle propre à un personnage (« si Gorm voit l'eau, il cède »). Gorm change d'avis par le
  mécanisme commun des avis.
- Des répliques écrites ; un ordre des recours codé par personnage.
- Une méthode de planification par recours (barrer, fuir, monter).

## Ordre proposé

Le joueur reste passif pendant ce travail ; tout est observé au banc sans joueur.

1. **Un récit du banc lisible** : qui voulait quoi, ce qu'il a tenté, qui l'a aidé ou contrarié,
   ce qui a changé entre eux. La chronique actuelle noie cela dans les déplacements.
2. **Planificateur par recherche**, d'abord sur la faim et le froid, au banc du Relais actuel :
   ne rien perdre (événements, 0 violation, minutes sans recours, temps de calcul), puis voir
   si un affamé sans recours trouve d'autres voies sans qu'on les lui écrive.
3. **Niveau d'eau**, avec un banc : les PNJ fuient l'eau, montent, perdent le feu, sans autre
   ajout. Fait (branche `crue-eau`), voir ci-dessous.
4. **Influence et relations** : disputes et persuasion entre PNJ.
5. **Agir ensemble**, puis **quitter la scène**.
6. **Passerelle et cale** (fabrication, étape 4) si une salle coupée le demande.
7. Mesure sur la crue complète : issues par graine (qui part, barrage fait ou non, feu, alarme),
   disputes vues, alliances, aucune violation.

Chaque étape reste mesurée au banc et peut s'arrêter là si elle n'apporte rien.

## Étape 3 faite : le niveau d'eau

Branche `crue-eau`. Mécanisme décrit dans `docs/mecaniques.md` (« Crue : le niveau d'eau »).

**Le moteur** (`donjon/eau.py`) : un niveau tiré de la graine (`seed:crue`), parti d'un niveau de
départ déclaré, qui monte jusqu'à l'heure du pic sans dépasser sa hauteur, puis baisse. Une
salle mouillée trempe qui s'y tient ; noyée (100 cm), elle ne se traverse plus et un feu posé y
meurt. Mêmes règles pour le joueur (pas, `aller`, échelle, `allumer`) et pour les PNJ (chemins,
trajets, gestes).

**Le scénario `crue`** (`donjon/scenario_crue.json`, `donjon/crue.py`), dérivé du Relais :
refuge 0, conduite basse -120 (le brasero), salle des vannes -100, palier -60, galerie +240 ;
eau au départ à -150 ; montée 20 à 50 cm/h, pic entre la 3e et la 6e heure, plafond -100 à
+80 cm, baisse 5 à 20 cm/h. Sur 2 000 graines : la conduite est noyée (feu perdu, galerie coupée
du refuge) dans 36 % des nuits, le refuge mouillé dans 22 %. Le refuge ne communique qu'avec la
conduite : monter à la galerie, c'est passer par les salles les plus menacées, avant qu'elles ne
soient noyées.

**Règles générales ajoutées**, aucune propre à un lieu ou à un personnage :
- la croyance `eau` d'une salle (sa hauteur, le niveau, un repère) ; revue quinze minutes plus
  tard, l'eau donne sa vitesse, et le PNJ l'attend là où elle arrivera dans l'heure ;
- l'eau où l'on se tient inquiète selon sa hauteur, l'eau attendue aussi, la voir gagner un lieu
  d'un coup ;
- l'abri : un lieu où l'on croit ou attend l'eau n'en est pas un ; tant qu'on voit l'eau
  monter, c'est le plus haut lieu éclairé qu'elle ne menace pas, avec ou sans compagnie ;
- debout dans l'eau, on ne sèche pas, même près du feu ;
- un réflexe d'alerte sans passage cru tombe (révélé ici : Gorm restait des heures à vouloir
  accourir vers la galerie coupée).

**Banc** (16 graines × 8 h, `--scenario crue --joueur chambre_cloche`) : le feu se noie dans 5
nuits ; quelqu'un monte à la galerie dans 14 (Aubin 11 fois, Gorm 6, Ilse 3, Brune jamais). Vers
la 170e minute, le plus souvent : Aubin et Ilse, inquiets, voient l'eau monter dans la conduite,
puis Brune forcer la réserve ; le premier qui prend la clé de la porte étanche monte, l'autre
trouve la porte verrouillée et reste. On redescend quand l'eau cesse de monter, s'il reste un
passage. Graine 8 : Gorm monte à 137 avec la clé, Ilse et Aubin à 172 par la porte qu'il a
ouverte ; Brune, qui crochetait la réserve, reste au refuge, mouillé à partir de 202, et appelle
à l'aide vingt-deux fois ; en haut, sans feu, Aubin finit à 91 de froid. Graine 9 : Aubin monte
avec la clé ; le brasero se noie à 186, le refuge est mouillé à 216 ; Gorm, Brune et Ilse
finissent dans 41 cm d'eau, sans feu, et appellent à l'aide. Le banc du Relais est inchangé
(sortie identique octet pour octet sur 4 graines).

Deux défauts communs révélés en route et corrigés : un PNJ prenait un objet dans la main d'un
autre (la même clé, prise tour à tour par Aubin et Ilse) ; un PNJ demandait du bois pour un feu
qu'il croit sous l'eau.

**Limites** :
- les salles à des altitudes différentes ne se voient plus entre elles (le moteur spatial les
  traite comme des étages) : la lumière du brasero n'éclaire plus la salle des vannes ;
- l'eau ne touche pas aux objets (bois mouillé, objets légers emportés) ; une salle inondée ne
  refroidit pas plus selon la hauteur : être trempé suffit (10 de froid par heure) ;
- un personnage dans une salle noyée sans issue y reste, sans danger propre (pas de nage,
  pas de noyade) ; le bruit de l'eau n'est pas un son du monde ;
- tous jugent la crue de la même façon (même horizon, même règle) : les avis divergents
  viennent seulement de ce que chacun a vu ; les avis vrais relèvent de l'étape 4.

## Le départ tiré de la graine

Branche `depart-tire`. Constat : hors des d20 (≈ 8 jets par nuit au Relais), tout était identique
d'une graine à l'autre : états de départ, rondes, durées. Au Relais, une seule nuit jusqu'à la
minute 5, deux jusqu'à 120 (Gorm promet ou refuse sa part à Brune), puis les branches se
rejoignent ; la faim atteint 70 aux mêmes minutes partout, Brune crochète vers la 123e minute.

**La règle** (`donjon/depart.py`, décrite dans `docs/mecaniques.md`) : le départ déclaré par un
scénario est une valeur centrale dont le moteur tire une variante, à la création du monde, par un
tirage à part (`seed:depart`) comme l'eau : les d20 d'une graine sont inchangés. Le tirage et ses
valeurs vivent dans `data["depart"]` ; un rechargement ne tire plus rien. Rien n'y est propre à un
scénario : chacun déclare ses bornes (`depart.bornes`), le moteur a des défauts.

**Les bornes retenues**, les mêmes dans les quatre scénarios (Relais, crue, mine, auberge) :

| borne | valeur | ce qu'elle dit |
|---|---|---|
| `corps` | 0,2 | dernier repas, veille, temps trempé à 20 % près : une heure ou deux d'écart |
| `besoins` | 10 | devoir, biens, sécurité à 10 points près, sous leurs seuils d'urgence pour la plupart |
| `periodes` | 0,2 | une ronde de 45 min revient toutes les 36 à 54 min |
| `rondes` | 0,5 | la prochaine ronde tombe dans la première moitié de sa période |
| `horloges` | 0,25 | la rafale de l'auberge entre la 150e et la 250e minute |

Plafond : aucun besoin tiré au-delà de 85 (l'extrême du corps et le désespoir sont à 95), sauf
déclaré plus haut. Réglées au banc (Relais, 16 graines, 8 h) : à 0,1 / 5 / 0,1 les nuits
divergent un peu moins (12 nuits distinctes à la minute 5, 12 issues) ; à 0,3 / 15 / 0,3 et
`rondes` 1, pas davantage (12 et 13) et plus de vols précoces (minutes 3, 10, 21, 29). La phase
des rondes fait l'essentiel de la divergence : seule, elle donne déjà 7 nuits sur 8 distinctes à
la minute 5 ; le corps seul, 4. Elle est aussi la cause des vols précoces : au départ déclaré,
toutes les rondes tombent à la minute 0 et Gorm va d'abord au refuge ; tiré, il peut rester à la
conduite, et Brune, refusée et affamée, crochète en son absence (même avec `rondes` à 0,25).

**Le banc** mesure la divergence : l'empreinte de l'état physique (places, regards, objets,
portes, feux, portions, horloges, eau ; sans besoins, corps ni croyances, que le tirage fait
différer dès la minute 0) aux minutes 5, 60, 120, 240 et 480, et l'issue de la nuit (où finit
chaque objet déplaçable et chaque personnage, ce qui reste ouvert, verrouillé, allumé, à manger,
et les vols vus) ; les jets par heure. Une pulsion confiée à quelqu'un que l'on croit fiable n'est
plus « sans recours » (`minutes_urgentes_confiees`, à part) ; `echanges` ne compte plus les appels
de qui cherche quelqu'un ni leurs réponses.

**Bancs** (8 h, au même moment, d'autres bancs tournant en parallèle ; fixe → tiré) :

| | Relais (16) | mine (8) | auberge (8) | crue (8) |
|---|---|---|---|---|
| nuits distinctes 5/60/120/240/480 min | 1/2/2/6/10 → 14/16/16/16/16 | 3/2/2/2/4 → 8 partout | 1/1/3/8/8 → 8 partout | 2/4/6/7/8 → 8 partout |
| issues distinctes | 4 → 13 | 4 → 8 | 8 → 8 | 6 → 8 |
| sans recours, ancienne mesure | 325 → 299 | 486 → 462 | 659 → 692 | 389 → 421 |
| sans recours, nouvelle | 109 → 94 | 486 → 462 | 659 → 692 | 105 → 115 |
| confiées (cloche de Gorm) | 216 → 205 | 0 | 0 | 284 → 306 |
| échanges (sans appels) | 10,5 → 11,2 | 29,6 → 29,0 | 31,4 → 26,6 | 12,6 → 11,0 |
| appels | 2,9 → 1,25 | 2,6 → 2,5 | 4,6 → 11,3 | 3,6 → 1,9 |
| vols vus | 0,75 → 1,0 | 0,6 → 0,9 | 1,4 → 0,9 | 0,1 → 0,1 |
| jets par heure | 0,79 → 1,14 | 4,5 → 2,3 | 4,5 → 10,5 | 0,53 → 0,56 |
| temps par nuit | 17,9 → 16,2 s | 42 → 36 s | 42 → 45 s | 16 → 13 s |

Aucune usurpation ni violation ; `planification.VERIFIER` sur une nuit tirée de chaque scénario.
Premiers crochetages au Relais : fixe, six nuits entre 122 et 129 ; tiré, neuf nuits, aux minutes
3, 30, 36, 96, 97, 97, 363, 366, 450. À l'auberge, la rafale variant, les trois crochetages de
Lucien tombent à 332, 362 et 439 au lieu de 197–201 (et 405, 420). On y appelle davantage : Hugues
cherche Anselme pour le prévenir dans cinq nuits sur huit (deux au départ fixe), Odile cherche
Joss dans trois (aucune), un appel par salle parcourue (règle de `constater-et-rumeurs`, inchangée).

**Limites** :
- les durées des gestes et la vitesse des besoins restent celles du moteur, identiques pour tous ;
  seul le départ varie ;
- un vol dès la troisième minute au Relais (une nuit sur 16) : cohérent avec Brune affamée et
  refusée, mais il abrège le premier acte ; si on le juge trop tôt, c'est la phase des rondes du
  gardien qu'il faudrait régler (une donnée), pas le moteur ;
- les tests de scène partent du départ déclaré (`depart="fixe"`) : ils décrivent un placement
  d'auteur ; le départ tiré a ses propres tests (`tests/test_depart.py`) ;
- le joueur n'est pas tiré (son corps et ses besoins restent déclarés).

## L'eau dans tous les plans (branche `verifier-eau`)

Défaut A4 de l'audit des nuits (`docs/audit-nuits.md`) : seul l'abri tenait compte de l'eau attendue.
Crue 500 : Brune quittait le refuge sec pour se chauffer au brasero sous 88 cm d'eau, Gorm faisait sa
ronde à la salle des vannes ; la conduite noyée et la porte étanche verrouillée les enfermaient 475
minutes (48 appels à l'aide). Dans 31 nuits sur 32, quelqu'un se chauffait les pieds dans l'eau.

Règles communes (détail dans `docs/plan-planificateur.md`, « VERIFIER et l'eau ») : l'eau qu'il attend
(`eau.attendue` : celle qu'il croit, ou plus à la vitesse où il l'a vue monter) coûte à tout plan par
minute, comme le noir ; un but qui se tient en restant (se chauffer, garder, la lumière, l'abri) ne se
tient pas là où il croit ou attend l'eau, et aucune part de bois ne va à un feu menacé ; il ne descend
pas dans une salle qu'il attend noyée, ni ne s'enferme du côté de la crue (retour coupé, ou lieu coupé du
plus haut qu'il puisse gagner) ; là où il attend l'eau noyer sa salle, il en sort avant tout
(`eau.en_peril`), au moins vers le lieu où il attend le moins d'eau.

Audit (12 h, 8 graines) : se chauffer dans l'eau 7 nuits sur 8 → 0 ; minutes·PNJ à 50 cm d'eau ou plus
262 → 124 par nuit, à 86 cm ou plus 128 → 14 ; appels à l'aide 94 → 2 ; personne ne reste une heure à
50 cm ou plus. Prix : le brasero de la conduite est le seul feu ; quand elle est menacée, on a froid
(Brune pressée par le froid 7 → 291 minutes par nuit au banc de 8 h). Traité par la branche `ressources` : un feu à la
galerie (section suivante).

## Un feu hors de l'eau (branche `ressources`)

Décision de l'utilisateur après `verifier-eau` : augmenter les ressources, par des données seules. Le
brasero de la conduite (-120 cm) était le seul feu ; les évacués partent trempés (300 à 390 minutes
déclarées, le froid monte de 10 par heure) et ne sèchent qu'en restant 30 minutes près d'un feu hors de
l'eau. Dès que la conduite est menacée, personne ne s'y chauffe plus : froid pressant (70 ou plus)
491 minutes·PNJ par nuit au banc de 8 h (Brune 281, Aubin 180).

**Ce qui est ajouté** (`donjon/scenario_crue.json`) : à la galerie de ronde (+240 cm, jamais atteinte),
un **poêle du guet** de fonte, fixe, allumé au départ avec 120 minutes de combustible (le gardien le
tient allumé pour qui guette l'eau la nuit), et à côté trois charges de **bûches du guet** (90 minutes
chacune), à Gorm. Les quatre PNJ savent le poêle et le bois là-haut (savoir de départ : Gorm l'a dit en
accueillant les évacués). Rien d'autre ne change : le brasero, les fagots de Gorm aux vannes, les
planches d'Aubin, la porte étanche verrouillée dont seul Gorm sait la clé.

Pourquoi là, et pas au refuge : la galerie est le seul lieu hors d'atteinte de l'eau. Essayé au banc, un
âtre au refuge (150 minutes) supprimait tout froid pressant (0 minute sur 8 nuits) : plus aucune tension.
À la galerie, s'y chauffer coûte de passer par la conduite, la salle des vannes et le palier, les salles
les plus menacées, avant qu'elles ne soient noyées, et de franchir la porte étanche ; le bois du guet est
à Gorm, qui l'emporte aussi pour son brasero ; une fois la conduite noyée, le poêle est coupé du refuge.

**Bancs 8 h** (8 graines, `--joueur chambre_cloche`, `main` ec2352e puis la branche) : froid pressant
491 → 111 minutes·PNJ par nuit (Brune 281 → 71, Aubin 180 → 14, Ilse 30 → 27) ; en attente 541 → 219 ;
sans recours 24 → 16 ; dans l'eau 438 → 373 ; dans le noir 29 → 25 ; échanges 19 → 18 ; achats 1 → 2
(on achète une part des bûches du guet à Gorm) ; demandes « as-tu… ? » 6 → 2,5 ; poêle allumé 163 minutes
par nuit, bûches du guet restantes 0,8 sur 3 ; brasero allumé 416 → 436 minutes ; vols vus 0,1 → 0 ;
aucune usurpation ni violation ; une nuit 21 → 18 s. Graine 500 (eau haute tôt) inchangée : Brune a
encore froid 335 minutes. **Audit 12 h** (8 graines, `tools/audit_nuits.py`) : froid pressant 794 → 199
minutes·PNJ par nuit (Brune 375 → 102, Aubin 328 → 24), en attente 914 → 571, noir 202 → 104, dans
l'eau 491 → 448, constats « eau longue » 7 → 4, aucun plantage. `VERIFIER` sans écart (graine 7, 8 h).
Cas vérifiés après rechargement : `tests/test_ressources.py` (graine 7 : Aubin puis Brune montent se
chauffer au poêle, Brune demande une part des bûches du guet à Gorm, refusée, Aubin l'achète, Gorm
recharge et rallume le poêle) ; `test_eau` et `test_verifier_eau` (Ilse fuit à la galerie et y sèche ;
transie au refuge, elle monte au poêle du guet au lieu du brasero menacé).

**Limites** : la traversée vers la galerie mouille (l'eau ne coûte que par la salle d'arrivée, limite
du moteur relevée par `verifier-eau`) ; le savoir du poêle est donné à tous au départ ; quand l'eau monte
tôt (graine 500), le poêle reste hors d'atteinte et le froid revient.

## Questions ouvertes

- Le barrage : effet chiffré (ralentir la montée) ou seuil (tenir jusqu'à un niveau) ?
- Le joueur peut-il partir en barque, ce qui finit sa partie ?
- Un cinquième personnage (un enfant à protéger, quelqu'un d'attendu qui n'arrive pas) ?
- D'autres moyens de sécher que le feu (se changer, une couverture) avec la crue, ou plus tard ?
