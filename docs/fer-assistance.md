# Fer & Flamme — assistance au vol

Branche `fer-et-flamme`, base `origin/main` récupérée : `0bad2272`.
Le fichier HTML, non suivi dans le dépôt principal, a été repris à l'identique
avant correction (SHA-256 `797e70c586caaa3c93e24b4182768878e7a9a4d5ab8e85ed84828ca2e3ce3318`).
Ni la branche `main` locale ni son fichier HTML n'ont été modifiés.

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
