# Fer & Flamme — commandes du vol sans assistance

## Commandes et contrat

`R` bascule l'assistance. La saisie est commune en ON et OFF : Z/S pour
haut/bas, Q/D pour gauche/droite, avec les alias W/A et ←/→ acceptés.
↑/↓ règlent désormais le couple et ne commandent aucune propulsion dans les
deux modes. L'aide affiche ZQSD pour le clavier AZERTY. En mode OFF :

- Z demande la poussée positive dans l'axe local du véhicule ; S demande
  la poussée négative. L'axe tourne avec le véhicule, y compris sur le dos.
- Q demande un couple antihoraire ; D demande un couple horaire.
- Les deux axes se combinent. Deux directions opposées s'annulent, même
  entre alias (Q + flèche droite, par exemple). Un alias n'amplifie pas la commande.
- Au relâchement de Q/D, le couple opposé maximal disponible freine la vitesse
  angulaire jusqu'à zéro. La dernière impulsion est réduite pour éviter de
  repartir dans l'autre sens. L'angle atteint est conservé, sans remise à plat.
  Il n'y a toujours aucun maintien automatique d'altitude ou de translation.
- En OFF, Q/D commandent la rotation ; ils ne lancent pas simultanément les
  moteurs des roues. La conduite au sol par Q/D reste dans le mode assisté.

L'aide change avec le mode et le HUD conserve ON/OFF. La touche R maintenue ne
bascule qu'une fois par appui. X répare et remet en piste en conservant le choix
d'assistance. Une nouvelle partie commence avec l'assistance comme auparavant ;
les appuis et l'état dynamique ne sont pas sauvegardés.

## Implémentation commune

La saisie fournit `poussee` et `rotation` dans [-1,1]. `repartirManuel` les
convertit en forces locales et couples avec les mêmes enveloppes bornées que
le reste du moteur. Il regroupe les actionneurs par axe, calcule leur capacité
de couple depuis les bras de levier réels, puis partage la demande entre les
groupes. Pour chaque couple attribué, il choisit la force réalisable la plus
proche de la commande. Une rotation peut ainsi entraîner une dérive latérale
si la géométrie ne permet pas un couple pur ; aucune force n'est annulée
artificiellement. [Correction des latéraux](fer-rotation-manuelle.md).

Q/D demandent la proportion choisie du couple réalisable dans leur sens.
À 100 %, chaque tuyère ayant un bras de levier utile atteint sa limite normale
ou inversée correspondante. Le plafond artificiel d'accélération angulaire a
été supprimé ; la réduction est maintenant un choix explicite du joueur.
Le budget électrique habituel s'applique aux forces demandées.
Au neutre, le freinage utilise toute l'autorité dans le sens opposé, indépendamment
de la jauge. Sa demande vaut au plus `I × |omega| / dt`, avec l'inertie physique
courante de Rapier. La même répartition en tuyères et le même budget électrique
s'appliquent : aucun changement direct de vitesse angulaire. Une nouvelle
commande Q/D reprend immédiatement la priorité. Un véhicule hors service ne
commande pas ce freinage. Deux directions opposées ramènent l'axe au neutre.
En poussée et rotation simultanées, la rotation conserve cette priorité ;
la poussée axiale est la plus grande compatible avec ce couple. Certaines
géométries ne laissent aucune poussée axiale lorsque tous les moteurs sont
mobilisés pour le couple maximal. Aucun retour automatique à plat n'est appliqué.

Le réacteur possède désormais la propriété explicite `reverse: 0.5`, déjà
conforme au taux de poussée inversée utilisé pour le redressement assisté.
Le manuel emploie cette capacité dans chaque orientation. Les demandes restent
converties en consommation puis en impulsions par le budget électrique habituel :
aucune force ni aucun couple directement ajouté au corps. Le calcul de pilotage
assisté reste celui validé précédemment. `avance`, `recule`, `gauche`, `droite`
lisent les mêmes touches dans les deux modes, via `KeyboardEvent.key`, qui
respecte la disposition AZERTY. Le manuel en déduit poussée et rotation.

## Vérification

La jauge « Couple manuel » démarre à 100 % dans les anciennes sauvegardes.
↑ ajoute et ↓ retire dix points, de 0 à 100 %. Le choix est affiché, appliqué
immédiatement à la commande de rotation, conservé par X et enregistré avec le
plan. Il peut être préparé en ON mais ne modifie que le couple manuel en OFF.
La commande Z/S n'est pas multipliée par ce réglage ; à 0 %, elle reste active.

`tools/test-fer-reglage-couple.cjs` vérifie tous les niveaux dans les deux sens,
sur les deux plans joueur, ainsi que les bornes, le changement pendant Q maintenu,
la persistance après recharge, le HUD et sa valeur ARIA. Les captures 1440×900
et 1024×640 ont été inspectées ; jauge et aide clavier restent dans la fenêtre.

`tools/test-fer-manuel.cjs`, navigateur isolé, moteur Rapier réel, appuis clavier
réels et même environnement `FER_PUPPETEER_MODULE`, `FER_RAPIER_MODULE`, `FER_BROWSER`
que les autres scripts. Plan exact du joueur et montage asymétrique avec tuyères
opposées, chacun après deux chargements :

- poussée avant/arrière, rotation gauche/droite, combinaison des deux axes ;
- freinage automatique au relâchement et reprise immédiate de la commande ;
- orientation à 90° et 180°, sans interprétation en haut/bas du monde ;
- bornes des tuyères et puissance consommée, absence de propulsion sans appui ;
- aide OFF, réparation conservant OFF, retour ON et commandes assistées ;
- sauvegarde du plan, recharge et répétition des comportements, captures du HUD.
- décollage manuel depuis le sol avec Z ; équivalence Q/D et ←/→ en ON,
  alias W/A en OFF, annulation des directions et absence de double commande.

Un troisième montage, avec seulement deux tuyères horizontales décalées, vérifie
le couple pur et l'absence de poussée fictive sur l'axe vertical absent.
Les trajectoires assistées du plan réel et de ses variantes sont aussi comparées
à la référence conservée de la passe précédente ; les boutons souris sont revérifiés.

Le plan joueur courant est dans `tools/fer-build-joueur-actuel.json` ; le
précédent reste dans `tools/fer-build-joueur.json` pour la régression.
Le test calcule un oracle indépendant du maximum de couple en sommant les
contributions extrêmes des tuyères. Il exige ce maximum dans les deux sens,
avec et sans poussée, et vérifie chaque force à sa borne utile. Les durées
des impulsions de test sont courtes pour observer le couple maximal avant
de nombreux tours ; le jeu conserve toute la poussée tant que la touche tient.
Sur le build courant de 549 kg, le couple demandé passe d'environ 670 à
12 727 N·m. Le contrôleur assisté conserve son propre calcul, inchangé.

Validation du couple maximal : quatre plans chacun après deux chargements,
plus un montage horizontal, tous verts. Sur le build courant, Q et D donnent
respectivement +12 726,776 et −12 726,776 N·m pour 420 kW demandés, facteur
électrique 1. Z+Q garde ce couple avec 480 kW demandés. Les forces utiles
sont à 6 800 N en normal ou −3 400 N en inverse ; chaque borne et le couple
servi sont vérifiés par un oracle indépendant. La capture du build courant
rechargé a été inspectée. Les 80 contrôles mathématiques d'enveloppe passent.

Artefacts : `artifacts/fer-manuel/`. Une capture du plan joueur rechargé a été
inspectée : assistance OFF, poussée et rotation actives. L'aide affiche désormais
les mêmes touches ZQSD en ON et OFF.
La force et le couple dépendent des orientations, bras de levier, pertes de blocs
et ressources : le mode manuel ne crée pas une autorité absente du véhicule.
L'arrêt dépend donc du couple opposé disponible et de l'alimentation ; une
géométrie qui ne produit pas de couple pur peut dériver pendant le freinage.
Travail dans le worktree `fer-et-flamme`, sans modification de `main`.

## Freinage de rotation au neutre

`tools/test-fer-frein-rotation.cjs` contrôle chaque pas physique à 120 Hz avec
Rapier réel : les deux builds joueur et un montage à autorité asymétrique,
chacun dans les deux sens après deux chargements. Pendant l'appui, le couple
atteint le maximum choisi. Au relâchement, l'oracle vérifie le couple opposé
maximal puis l'impulsion d'arrêt, une vitesse décroissante et l'absence de
relance au-delà de la précision numérique de Rapier (tolérance 1e-5 rad/s).
L'angle reste stable, sans remise à plat. Sont aussi vérifiés Z maintenu,
la jauge à 30 et 0 %, une alimentation insuffisante, ±0,0003 rad/s,
la priorité immédiate à Q, l'aide visible après recharge et l'absence d'erreur JS.
Résultats verts, ainsi que le test manuel existant et la régression de jauge.
Artefacts : `artifacts/fer-frein-rotation/`, capture du freinage inspectée.
