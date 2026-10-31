# Fer & Flamme — assistance au vol

Branche `fer-et-flamme`, base `origin/main` récupérée : `0bad2272`.
Le fichier HTML, non suivi dans le dépôt principal, a été repris à l'identique
avant correction (SHA-256 `797e70c586caaa3c93e24b4182768878e7a9a4d5ab8e85ed84828ca2e3ce3318`).
Ni la branche `main` locale ni son fichier HTML n'ont été modifiés.

## Pleine poussée latérale et freinage de la translation

La cible d'inclinaison n'est plus atténuée par le cosinus de l'angle courant.
Cette atténuation créait un équilibre artificiel à 51,3° sur le plan colonne,
contre environ 82,06° physiquement soutenables. La division de portance ne
plafonne plus son cosinus à 0,25. L'accélération demandée utilise le vecteur
de poussée disponible, avec une composante verticale compatible avec le
maintien d'altitude ; Z/Q/D et S/Q/D partagent ce vecteur lorsque les deux
axes sont commandés. Aucun plafond de vitesse n'est ajouté.

`portanceSousPuissance` calcule la portance à couple nul sous le budget
électrique disponible, y compris avec des bras asymétriques, des moteurs
retournés et des rendements distincts. Les moteurs latéraux au repos ne
réduisent plus forfaitairement ce budget. La consommation réellement
allouée reste payée par le bus et les stocks du jeu.

Au relâchement, la translation est prioritaire : pleine autorité de freinage,
puis verrouillage après l'arrêt. Le retour à plat est anticipé avec la même
enveloppe force/couple que les tuyères réelles, afin de limiter la poussée
résiduelle pendant la rotation. L'impulsion finale ne doit pas inverser X ;
les résidus float32 inférieurs à 1 µm/s sont traités comme nuls. Le couple
reste disponible pour finir la rotation. La réserve de portance est conservée
lorsqu'elle est réalisable ; le départ et le freinage angulaire peuvent la
libérer lorsqu'un changement d'assiette l'exige.

Le critère n'exige pas l'arrêt simultané de la rotation et de la translation.
Sur le plan colonne lancé à 40 m/s, X passe sous 0,15 m/s à 1,20 s, alors que
la rotation atteint encore environ 3,9 rad/s et Y vaut −0,22 m/s. Le retour
à plat se termine ensuite. La comparaison sans anticipation gagne environ
0,20 s sur ce premier arrêt X, mais provoque ensuite une perte de plus de
8 m d'altitude : elle détériore la stabilisation de la translation Y.

Validation Rapier réelle dans Edge isolé, boucle déterministe sans attente
du temps réel : 24 épisodes de poussée/arrêt, trois montages, deux sens,
deux chargements (`tools/test-fer-frein-max.cjs`), plus 24 commandes combinées
avec `FER_COMBINEES=1`. Sur le plan colonne : 82,06°, poussée affichée 100 %,
arrêt X depuis 40 m/s en 1,20 s et 27,59 m, contre 5,50 s et environ 75 m
avant correction. Dans ces essais, la perte transitoire d'altitude atteint
environ 1,02 m, puis l'altitude est récupérée. Compact : 70,05° et pleine
poussée ; précédent build à latéraux : 74,69° et arrêt depuis 40 m/s en 1,50 s.
Les 24 transitions sol → Z → Q/D et stationnaire → Q/D restent vérifiées
après recharge, avec HUD et état physique concordants. L'arène de transition
est élargie et aplatie dans la copie de test ; combat désactivé pour isoler
l'assistance des impacts et du relief. La piste normale du jeu est inchangée.

Les tests mathématiques comparent 80 enveloppes et 16 budgets électriques
à des oracles indépendants, et vérifient l'allocation prédite/réelle ainsi
que la dernière impulsion près de la verticale. Les cinq plans du test
général passent aussi accélération, freinage, redressement et recharge.
Les captures de poussée et
les traces sont dans `artifacts/fer-frein-max/`. L'anticipation reste une
prévision discrète, pas une preuve d'optimalité globale en temps X/Y/rotation.
Les changements brusques d'assiette peuvent encore consommer de l'altitude.

## Coordination de la poussée et de la direction au décollage

Plan exact de 479 kg conservé dans `tools/fer-build-joueur-colonne.json`.
Reproduction : Z pendant 0,35 s depuis le sol, puis D. La vitesse verticale
initiale dépasse 20 m/s ; le freinage inverse les réacteurs. L'ancienne
consigne inclinait pourtant le corps comme sous une poussée positive et
l'allocation pouvait appliquer une poussée horizontale opposée à la commande.
Recul mesuré à 14,37 m/s sur l'essai D, avec excursion jusqu'à 1,60 rad.
L'estimation du contre-couple supposait également une portance positive.

Le contrat commun tient maintenant compte du signe de la force verticale
mondiale pour l'inclinaison et la prédiction du freinage. Une commande Q/D
contraint la force nette de base au demi-espace de la direction demandée.
Cette contrainte passe par `domaineGroupe` et `repartirGroupe` : elle ne coupe
pas les moteurs individuellement et conserve la possibilité d'un couple pur.
L'ajout affine des latéraux conserve cette direction ; leur sens local tient
compte du retournement du corps. Lorsqu'une réorientation empêche de satisfaire
simultanément les commandes verticale et horizontale, la poussée incompatible
est suspendue pendant que le couple tourne le véhicule.

La cible d'assiette est calculée comme l'équilibre couplé entre inclinaison,
anticipation de translation et poussée signée, par résolution numérique.
Elle ne se déplace plus elle-même à chaque correction de l'angle mesuré.
Cela traite aussi le verrouillage après relâchement. Aucun plafond de vitesse,
de rotation ou d'accélération angulaire n'est réintroduit.

`tools/test-fer-transition.cjs` reproduit le sol → Z → Q/D, ainsi que le même
appui depuis le stationnaire, sur le plan exact, le montage compact et le
précédent build à latéraux. Deux chargements pour chaque plan. Il contrôle la
force mondiale produite, l'absence de recul depuis le repos, l'assiette pendant
l'appui, l'arrêt, les sauvegardes et le HUD. Les trajectoires restent à distance
des murs ; les tirs et les autres véhicules sont neutralisés dans la copie de
test pour ne pas confondre impulsion extérieure et assistance. L'absence de
dégât et de perte de bloc est contrôlée. Les tests mathématiques
vérifient aussi que la contrainte de force conserve les couples purs et la
poussée inversée. Artefacts : `artifacts/fer-transition/`.

Validation : 24 épisodes après recharge sur trois montages, sans départ opposé
depuis le repos, puis arrêt stable. Sur le plan colonne, la variation d'assiette
sur les 0,25 dernières secondes de l'appui reste sous 0,06°. Les cinq plans
du test général passent également accélération, freinage, redressement et
recharge en conservant le jeu normal. Le compact dépasse encore 7,21 rad/s et
32,94 rad/s², avec pleine poussée Z/S puis retour stable : les anciens plafonds
restent supprimés. L'équilibre exactement nul est préservé par le solveur
numérique pour ne pas créer une minuscule demande de couple à plat.

## Assistance sans plafonds forfaitaires de vol

À la demande du joueur, retrait des plafonds de consigne de rotation
(2,5–4,5 rad/s), d'accélération angulaire (22–39,6 rad/s²), du facteur de couple
à 90 %, des dosages de montée à 50 % et de descente à 70 %/8 g, ainsi que de la
marge forfaitaire de portance à 15 %. Z/S demandent toute la force disponible
dans le sens du monde ; la répartition conserve la priorité de stabilisation.
Le vol n'a toujours aucun plafond explicite de vitesse de translation.

`domaineGroupe` partage avec `repartirGroupe` les bornes de couple compatibles
avec le poids à soutenir. Si cette portance est irréalisable, l'assiette reste
libre de redresser. L'inclinaison de conception atteint la limite de portance
calculée, sans facteur de réduction. Une simple suppression des plafonds ne
suffisait pas : le couple de freinage diminue à l'approche de cette limite.
Le contrôleur intègre donc le travail du contre-couple sur l'angle restant
(quadrature de Simpson à cinq points), avec l'inertie physique courante et les
capacités électriques disponibles. La consigne de vitesse permet encore le
freinage après le prochain pas physique ; le couple peut saturer dans ses
vraies bornes, sans limite fixe de vitesse ou d'accélération angulaire.

Ce calcul reste une prédiction : il n'établit pas une optimalité globale et
ne garantit pas le redressement après toute collision ou rupture de bloc,
ni lorsque la puissance, le couple opposé ou l'altitude manquent.
Les limites des moteurs (dont les 50 % en inverse), des ressources et les
amortissements physiques communs aux deux modes sont conservés. Les gains de
verrouillage de position et les précautions numériques restent présents.

La cible des roues à 9,5 m/s est conservée : son remplacement par une commande
de couple sans vitesse cible a fait basculer le preset rover sur terrain plat.
Débrider la conduite au sol demanderait un contrôle adapté du tangage et de
l'adhérence ; cette passe porte sur une assistance au vol stable.

`tools/test-fer-debridage.cjs` : deux builds joueur et montage compact, chacun
après deux chargements. Pleines poussées Z/S vérifiées moteur par moteur,
redressements depuis ±1,2 rad et π, mesure de chaque pas physique, déplacement
dans les deux sens puis arrêt, état physique et HUD après recharge. Le montage
compact doit effectivement dépasser les anciens plafonds de rotation et
d'accélération ; les mesures ne se contentent pas de contrôler les formules.
Artefacts : `artifacts/fer-debridage/`. Le seuil de 0,9 rad du test d'inversion
est remplacé par la limite de portance du montage, avec la même exigence de
stabilité d'altitude et d'arrêt.

Passe finale verte : les trois plans après deux chargements, soit dix-huit
redressements. Build actuel : pic de 5,78 rad/s ; compact : 7,84 rad/s et
33,49 rad/s², puis retour stable. Pleines poussées Z/S à plat : +20 400 N
en montée et −10 200 N en descente sur les deux builds joueur. Le test assisté général
passe aussi ses 80 enveloppes et cinq plans, avec freinage, retournement et
recharge. Les variantes à latéral unique et verticales retournées passent
après deux chargements ; la voie sans autorité d'assiette reste bornée.
Régressions manuelles vertes : quatre plans et un montage horizontal ; frein
de rotation sur deux builds et un montage asymétrique. Capture après recharge
inspectée. La suite Python et les bancs Luna ne concernent pas ce changement.

## Poussée inversée dans les deux modes

La passe du 31 octobre ouvre la poussée inverse à toute assiette en assisté.
Elle était auparavant réservée au redressement sur le dos pour les verticales,
et absente de la commande latérale. Le test de descente du build actuel échoue
sur le commit précédent `e3f8b8cf` et passe après correction.

`bornesPoussee` définit désormais la même plage physique pour le manuel,
l'assistance et le bilan : 6 800 N en normal, 3 400 N en inverse pour le moteur
actuel, dans son orientation locale. L'assistance utilise cette plage pour S,
le freinage vertical, la sustentation et l'assiette. Les latéraux opposés à la
commande contribuent par inversion, dans la proportion dont la portance et le
couple restent compensables. Sans autorité d'assiette, la poussée reste bornée
par cette même plage. Le bilan de portance, le rapport poussée/poids et
l'inclinaison calculée incluent aussi les capacités inverses.

Lors de cette passe d'inversion, les lois de stabilisation et le budget électrique restent applicables :
l'inversion est une capacité disponible au contrôleur, pas une commande qui
impose tous les moteurs à fond. Les gains et les règles de commande
montée/descente étaient alors conservés ; les capacités dans le sens du monde tiennent
compte de l'orientation du véhicule.

`tools/test-fer-inversion-assistee.cjs` contrôle les deux builds joueur, un seul
latéral et des moteurs verticaux orientés vers le bas, chacun dans les deux sens
après deux chargements : stationnaire, S propulsé, frein d'une montée rapide,
commande latérale puis arrêt, bornes de chaque tuyère et consommation commune.
Le plan à moteurs retournés vérifie aussi la portance inverse dans le bilan
rechargé. Une seule tuyère verticale vérifie la voie sans autorité d'assiette.
Les captures rapprochées servent à contrôler les flammes inverses et le HUD.
Artefacts : `artifacts/fer-inversion-assistee/`.

Passe verte : quatre plans après deux chargements, puis recontrôle du build
actuel et des moteurs retournés avec le bilan final. Sur le build de 549 kg,
S produit −5 524 N et le freinage de la montée atteint −10 200 N ; l'écart
d'altitude pendant les épisodes latéraux testés reste inférieur à 2,5 cm.
Flammes orangées et HUD inspectés sur capture rapprochée. Régressions vertes :
80 enveloppes et cinq configurations de vol assisté (accélération sans plafond,
freinage, redressement et recharge), manuel sur quatre plans et un montage
horizontal, freinage manuel sur les deux builds et un montage asymétrique.

## Contrat corrigé

Les commandes d'assistance sont allouées dans l'ensemble des forces et couples
réalisables par les tuyères restantes. Ce même calcul sert aux limites de
conception et à la simulation, sans supposer deux tuyères ou un centre de masse
centré. La sauvegarde conserve son format et le plan rechargé utilise ce calcul.

- `enveloppeGroupe`, `sectionEnveloppe`, `bornesGroupe`, `repartirGroupe` :
  enveloppe convexe exacte, force puis couple atteints par combinaison de deux
  répartitions bornées. Réduction de l'effort maximal avant cette combinaison
  pour éviter les poussées opposées inutiles. Sur les leviers −0,1 / +0,5 / +1 m,
  la poussée à couple nul est bien 8 160 N, au lieu du faux zéro précédent.
- `pousseeNette` et `angleInclinaisonMax` utilisent cette même enveloppe.
  L'atelier affiche la poussée à couple nul et alerte sur la sustentation.
- `simulerAppareil` : allocation commune des tuyères vers le haut, vers le bas
  et inversées. Le redressement conserve son couple ; la prédiction latérale
  utilise la pente de la portance modulo π. La demande d'inclinaison décroît
  lorsque le corps est renversé. La vitesse angulaire visée est bornée par le
  couple de freinage dans le sens opposé. Une sustentation devenue impossible
  ne confisque plus toute l'autorité d'assiette.
- La commande gauche/droite maintenue demande l'accélération disponible, sans
  consigne ni plafond de vitesse. Le freinage et le verrouillage de position
  interviennent au relâchement. Le plafond de 9,5 m/s et la limite proportionnelle
  à l'accélération, introduits lors de la première correction, ont été retirés
  à la demande du joueur.

## Vérification reproductible

`tools/test-fer-assistance.cjs` utilise un navigateur Edge/Chromium de test isolé,
le vrai moteur Rapier 2D 0.21.0 et la boucle du jeu à pas fixe. L'instrumentation
et l'horloge déterministe sont ajoutées seulement à la copie servie par le test.
Aucune modification du profil ou du stockage du navigateur personnel.

Installer `puppeteer-core` dans un environnement de test, puis lancer
`node tools/test-fer-assistance.cjs`. Variables facultatives :
`FER_PUPPETEER_MODULE` (module installé ailleurs), `FER_BROWSER` (exécutable),
`FER_RAPIER_MODULE` (copie locale du module officiel pour éviter le CDN).

Les contrôles couvrent 80 ensembles de bornes comparés à un oracle indépendant,
le contre-exemple asymétrique et le couple inversé, puis cinq plans de véhicules :
symétrique, asymétrique, tuyères opposées, tuyères latérales et preset Foudre.
Pour chaque plan : sauvegarde/recharge, rendu du bilan et de la vitesse, sustentation, accélération maintenue,
freinage, retournement à 38 m, redressement, retour à l'altitude et nouvelle
recharge avec reproduction du vol, de l'accélération et du freinage. Les tuyères opposées sont aussi contrôlées
sur leur consommation au maintien.

Résultats bruts et captures : `artifacts/fer-assistance/` (ignoré par Git).
Les contrôles de déplacement exigent une vitesse qui augmente entre 1,25 et
2,5 secondes de commande maintenue, puis un arrêt au relâchement. Ils n'imposent
aucune vitesse de croisière. La même accélération est vérifiée après recharge,
avec concordance entre état physique et vitesse affichée au HUD.
Passe après retrait du plafond : **80 groupes et cinq configurations validés**,
aucune erreur JavaScript. Entre 1,25 et 2,5 secondes de commande, le montage
symétrique passe de 9,49 à 21,92 m/s, l'asymétrique de 7,69 à 18,47 m/s,
les tuyères opposées de 9,00 à 20,72 m/s, les latérales de 25,72 à 54,20 m/s
et Foudre de 1,90 à 4,60 m/s. Le freinage au relâchement ramène chaque appareil
à moins de 0,25 m/s, avant et après recharge. L'écart d'altitude pendant ces
accélérations reste inférieur à 0,31 m sur les cinq plans.
La suite Python du Seuil et les bancs Luna ne concernent pas ce moteur JavaScript.

## Limites

Le redressement consomme de l'altitude ; aucun contrôleur ne garantit d'éviter
le sol si le véhicule manque de hauteur, de couple ou de puissance. Le budget
électrique partagé et les profils de priorité restent applicables. L'inclinaison
de conception est une estimation sur les capacités installées, pas une promesse
de portance sous toute charge électrique. Le build personnel a depuis été fourni
et a révélé deux défauts supplémentaires, corrigés dans le contrat commun :
[allocation latérale et repères physiques](fer-stabilite.md). Les mesures
numériques ci-dessus décrivent la passe initiale sur les cinq plans ; les
résultats de la passe courante sont dans les artefacts de test.
