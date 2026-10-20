# Scénario d'étude : la crue du Relais

Document de discussion, pas encore un jalon. Il décrit une situation qui doit mettre à
l'épreuve les PNJ (buts opposés, relations, menace commune) et en tire les mécanismes
généraux qui manquent au moteur. Rien n'y est un script : le scénario déclare des données
(personnages, croyances de départ, rythme de la menace, ressources), et ce qui arrive doit
naître des mécanismes communs.

## Ce que le scénario doit éprouver

- **Des buts opposés sur une même ressource** : ce qui sert à l'un prive l'autre.
- **Des croyances opposées sur l'avenir**, sans qu'aucune soit vraie d'avance : chacun agit
  sur son avis, et c'est la partie qui tranche.
- **Des relations qui pèsent** : qui l'on croit, qui l'on aide, avec qui l'on part.
- **Une menace commune** que personne ne peut ignorer, qui force à choisir, et qu'aucun ne
  peut affronter seul.
- **Des issues variées** d'une graine à l'autre et selon le joueur, à partir d'un petit
  nombre de règles.

Critère principal, repris de la piste de planification : des comportements cohérents, variés
et adaptatifs, sans méthode écrite pour ce scénario.

## Situation

La nuit de la crue. Le Relais est la maison des vannes : la conduite basse et la salle des
vannes sont au plus bas, le refuge au-dessus, le palier des vannes et la galerie de ronde en
haut. Gorm le garde ; Brune, Ilse et Aubin y ont été évacués. La cloche d'alarme, qui prévient
le village en aval, est restée dans la galerie (l'objectif actuel du joueur).

L'eau monte. Personne ne sait jusqu'où ni quand elle cessera.

## La menace

- **Un niveau d'eau**, quantité du monde, comparé à l'altitude de chaque salle (`altitude_cm`
  existe déjà). Au-dessus du sol, une salle est **mouillée** (froid, feu menacé), puis
  **noyée** : impraticable, feu éteint, objets légers perdus ou gâtés.
- **Un rythme déclaré par le scénario** : montée par heure et heure du pic, tirées dans des
  bornes selon la graine. Le pic peut tomber avant le refuge ou après : Gorm peut avoir raison.
- **Ce qu'on en perçoit** : l'eau vue dans une salle, son bruit, et la mesure aux vannes qui
  donne une tendance. Chacun s'en fait une croyance (niveau, vitesse) qui peut être fausse ou
  périmée, comme les autres croyances.
- **Ce qui la change** : barrer les vannes ralentit la montée dans les salles basses tant que
  le barrage tient. Le barrage peut céder si on l'a fait avec trop peu.

## Les recours

Chacun a un coût, et ils se disputent les mêmes moyens.

| Recours | Il faut | Ce que ça coûte |
|---|---|---|
| Barrer les vannes | des planches, un marteau, deux personnes, du temps | les planches ne brûleront pas ; du travail dans l'eau froide |
| Monter en haut | rien | froid, pas de feu sans bois monté, vivres à emporter |
| Partir en barque | la barque de service, quelqu'un qui sait la mener | deux places ; laisser les autres |
| Sonner l'alarme | la cloche, de là-haut | rien pour soi : c'est pour le village |
| Garder le feu | du bois ou des planches | ce qui brûle ne barre plus |

Ressources disputées : les **planches** d'Aubin (barrage, feu, ou passerelle si une salle est
coupée), le **bois** de Gorm, les **4 parts** de vivres, les **2 places** de la barque.

## Les personnages

Chacun a un avis de départ, un but qui en découle, et ce qui pourrait le faire changer.

**Gorm**, gardien. Croit que le Relais tient : il l'a vu tenir à chaque crue. Son devoir : ne
pas partir tant que des évacués sont attendus, garder le feu pour eux. Il tient son bois et ses
vivres. Respecte Aubin de longue date ; se méfie de Brune. *Levier* : l'eau vue dans le
refuge ; la parole d'Aubin, s'il le croit encore ; un service rendu au refuge.

**Aubin**, passeur. Croit que les vannes céderont avant le pic si on ne les barre pas. Veut
ses planches pour le barrage, ce qui le met face à Gorm (le feu) et à quiconque en a besoin
ailleurs. Ne peut pas barrer seul. Taciturne : il dit ce qu'il a vu, sans insister.
*Levier* : quelqu'un qui accepte de l'aider ; la vue d'un barrage qui cède.

**Brune**, batelière. Croit que seule la barque sauve. Elle sait la mener ; personne d'autre
ne le fait sans risque. Affamée, peu scrupuleuse. Deux places : elle peut partir seule,
emmener qui la paie (une part, un objet), ou qui elle préfère. *Levier* : de quoi manger ; une
dette ; l'eau qui baisse.

**Ilse**, meunière. A peur. Suit celui qu'elle croit le plus fiable, et répète ce qu'elle a vu
et entendu : son avis fait pencher le groupe. Si elle prend la seconde place, la barque est
pleine. *Levier* : la confiance ; la peur, que le noir et l'eau aggravent.

Relations de départ (à régler) : Gorm et Aubin se font confiance ; Gorm se méfie de Brune ;
Ilse craint Brune et s'en remet à Gorm ; Aubin doit à Gorm son hébergement.

## Le joueur

Il a les mêmes besoins que les PNJ et la même menace. Il peut convaincre, mentir, arbitrer
entre Gorm et Aubin, aider au barrage, négocier une place, sonner l'alarme, ou partir seul.
Il n'a pas de rôle réservé : les PNJ le traitent selon ce qu'ils croient de lui.

## Déroulés possibles

Des exemples de ce qui devrait pouvoir arriver, pas des branches à écrire.

- Le pic tombe bas. Gorm garde le feu avec les planches, Aubin cède à contrecœur ; Brune,
  partie seule à minuit, a eu tort ; Ilse en parle à tout le monde.
- Le pic tombe haut. Aubin convainc le joueur, ils barrent les vannes ; le refuge reste sec
  deux heures de plus ; Gorm, qui a vu l'eau monter, cède son bois pour les étayer.
- Brune propose une place à Ilse contre sa part de vivres ; Gorm le voit, refuse de servir
  Brune ; Ilse hésite entre les deux ; le joueur prend la place à sa façon.
- Personne ne s'entend : chacun pour soi, le feu meurt, tout le monde monte en haut, et la
  cloche est la seule chose qui reste à faire.

## Mécanismes généraux à ajouter

Chacun est commun au moteur ; le scénario n'en fournit que les données.

1. **Niveau d'eau** : quantité du monde, rythme et pic déclarés, salles mouillées puis noyées
   selon leur altitude, effets sur le feu, les objets et le corps (froid). Perception de l'eau
   et de sa tendance, croyances qui en découlent. Les `horloges` existent mais ne portent que
   des événements ponctuels.
2. **Avis sur ce qu'il faut faire** : une croyance sur un recours (« barrer les vannes nous
   sauve », « le Relais tient »), avec sa confiance. On se convainc les uns les autres
   (parole typée, CHA, confiance, ce qu'on a vu soi-même). Deux avis opposés font une dispute
   que le joueur peut voir et entendre.
3. **Relations graduées** : au-delà de « fiable » oui ou non, une affection, une dette (un
   service rendu), une rancune (un refus, un vol, un mensonge découvert). Elles pèsent sur
   qui l'on croit, ce qu'on accepte, ce qu'on donne.
4. **Agir ensemble** : une tâche qui demande plusieurs personnes ; on demande de l'aide pour
   elle, l'autre accepte ou refuse selon ses buts et la relation ; la tâche avance quand tous
   y sont.
5. **Quitter la scène** : un départ (la barque) fait sortir des personnages de la partie, avec
   leurs biens. Places comptées ; une capacité (mener une barque) comme `crochetage`.
6. **Ressource à plusieurs usages** : les planches brûlent, barrent ou font passerelle. C'est
   là que la fabrication (étape 4, passerelle et cale) et la planification se rejoignent.
7. **Fin de partie** : le pic passé, l'eau baisse ; le bilan dit qui est resté, qui est parti,
   qui a eu froid ou faim, si l'alarme a sonné. Pas de fin écrite.

## Ce qui serait un script, à éviter

- Un événement déclenché par la présence du joueur, ou à une minute fixée pour faire avancer
  l'histoire (hors rythme de l'eau, donnée de scénario).
- Une règle propre à un personnage (« si Gorm voit l'eau, il cède »). Gorm change d'avis par le
  mécanisme commun des avis : ce qu'il voit pèse plus que ce qu'on lui dit.
- Des répliques écrites ; un ordre des recours codé par personnage.
- Une méthode de planification par recours (barrer, fuir, monter) : voir plus bas.

## Ordre proposé

1. **Planificateur par recherche** (piste GOAP) : les opérations déclarent conditions et
   effets sur les croyances, le profil donne les coûts. D'abord sur la faim et le froid, au
   banc du Relais actuel : ne rien perdre (événements, 0 violation, minutes sans recours,
   temps de calcul). Sinon chaque recours ci-dessus deviendrait une méthode de plus.
2. **Niveau d'eau** et sa perception, avec un banc sans joueur : les PNJ fuient l'eau, montent,
   perdent le feu, sans autre ajout.
3. **Relations graduées** et **avis** : disputes et persuasion entre PNJ.
4. **Agir ensemble**, puis **quitter la scène**.
5. **Passerelle et cale** (fabrication, étape 4) si une salle coupée le demande.
6. Mesure finale sur la crue complète : issues par graine (qui part, barrage fait ou non, feu,
   alarme), disputes vues, alliances, aucune violation.

Chaque étape reste mesurée au banc et peut s'arrêter là si elle n'apporte rien.

## Questions ouvertes

- Le pic : tiré dans des bornes selon la graine, ou fixé par l'auteur et seulement ignoré des
  personnages ?
- La barque : partir est-il une fin pour ceux qui partent (ils quittent la partie), ou un trajet
  vers une autre scène ?
- Le barrage : effet chiffré (ralentir la montée) ou seuil (tenir jusqu'à un niveau) ?
- Le joueur peut-il partir en barque, ce qui finit sa partie ?
- Un cinquième personnage (un enfant à protéger, quelqu'un d'attendu qui n'arrive pas) pour
  plus de tension, ou rester à quatre ?
