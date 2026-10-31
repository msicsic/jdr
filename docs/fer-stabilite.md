# Fer & Flamme — stabilité du build transmis par le joueur

## Reproduction et invariant

Le JSON exact est conservé dans `tools/fer-build-joueur.json` : 12 blocs,
627 kg, trois tuyères verticales et deux latérales placées sous le centre de
masse. La sauvegarde personnelle et le plan du véhicule n'ont pas été modifiés.

L'invariant est un contrat physique commun : position et vitesse contrôlées
désignent le même point ; les forces attribuées à chaque tuyère doivent
réaliser ensemble le couple et la portance commandés.

Deux défauts ont été reproduits dans le vrai moteur Rapier :

- À 6 800 N, une tuyère latérale distante de 0,723 m du centre de masse
  produit environ 4 918 N·m. Les verticales ne peuvent opposer que 3 400 N·m.
  Le moteur conservait les latérales à fond après saturation des verticales :
  couple parasite mesuré **+1 518 N·m**, basculement **130°** après une
  commande droite d'une seconde. En sens inverse, l'appareil n'était toujours
  pas stabilisé huit secondes après relâchement.
- Les boucles de position employaient l'origine de la grille, alors que
  `linvel` décrit la vitesse du centre de masse. Une rotation du build déporté
  changeait fortement les positions contrôlées et la caméra sans translation
  physique équivalente. Le HUD utilisait le même mauvais point.

## Correction commune

`proportionRealisable` intersecte une demande affine de compensation avec
l'enveloppe force/couple existante. `simulerAppareil` choisit d'abord une demande
verticale/d'assiette réalisable, puis ajoute la poussée latérale dans la
proportion dont la compensation verticale **et** le couple sont réalisables.
Les anciens plafonds indépendants, incomplets, ont été retirés. L'accélération
commandée reste maintenue ; aucun plafond de vitesse n'est ajouté.

Les positions des boucles de contrôle, du HUD, de la caméra, des pilotes et des
mesures de test emploient désormais le centre de masse mondial. L'origine
reste celle de la transformation géométrique des blocs et de la détection du
sol. `__fer.etat().x/y` et `__fer.placer(x,y)` désignent le centre de masse.
Les cibles initiales utilisent aussi ce centre. La vitesse d'émission des obus
emploie le bras de levier depuis le centre de masse.

`centreMasseCorps` recalcule les leviers à partir des masses courantes des
colliders (munitions et cargaison comprises), en double précision. Soustraire
directement le `localCom` de Rapier, arrondi en simple précision, introduisait
des différences de saturation lors d'un déplacement de la grille.

## Vérification et limites

`tools/test-fer-stabilite.cjs` exerce le plan exact, sa copie décalée de trois
colonnes et une variante au centre de masse plus haut, chacun après deux
chargements. Commande droite/gauche pendant une seconde, relâchement pendant
huit secondes : états, assiette, vitesse, altitude, HUD et captures. Les traces
du plan et de sa copie doivent coïncider à 2 mm / 0,002 rad près ; un simple
placement différent dans la grille ne doit changer aucune commande.

Résultat ciblé : les trois plans passent dans les deux sens, avant et après
recharge. Sur le plan exact, l'altitude reste entre 16,031 et 16,057 m pour
une consigne de 16 m ; la vitesse résiduelle après freinage reste inférieure
à 0,001 m/s et l'assiette revient à zéro. L'inclinaison de déplacement atteint
48,3° de façon maîtrisée, sans retournement. L'écart maximal de trajectoire
entre le plan et sa copie décalée est d'environ 0,031 mm. Une capture du plan
rechargé a été inspectée : HUD à 16,0 m, assiette à 0°, assistance ON.

`test-fer-assistance.cjs` compare aussi l'intersection de la demande latérale
à un oracle indépendant sur 80 ensembles bornés, avec contrôles de faisabilité
et de maximalité, puis exerce les cinq configurations précédentes.
`test-fer-souris.cjs` contrôle les commandes simultanées après les changements
de repère et de caméra.
Le freinage des cinq montages précédents est mesuré à cinq secondes, avec
contrôle de l'intégrité du véhicule. Une attente prolongée dans la zone de
combat avait détruit une tuyère : la trace confirme que le freinage était
terminé avant cet impact. Ce dommage n'est pas assimilé à un défaut de contrôle.
Passe finale : **tous les contrôles passent**, aucune erreur JavaScript : six
couples plan/chargement et douze épisodes latéraux, invariance de grille,
80 groupes avec oracle, cinq montages de régression et huit combinaisons souris.

Fichiers et captures : `artifacts/fer-stabilite/` ; baseline `avant.json` et
`avant.html`, validation `resultats.json`. Environnement isolé, même variables
`FER_PUPPETEER_MODULE`, `FER_RAPIER_MODULE`, `FER_BROWSER` que les autres tests.
`FER_DIAGNOSTIC=1` conserve les traces sans arrêter sur les assertions.

L'enveloppe décrit la géométrie et les limites des tuyères. Le budget électrique
et les profils de priorité restent appliqués ensuite : une puissance réellement
insuffisante peut compromettre la portance. Le redressement près du sol ne
garantit pas d'éviter un impact. Les mesures décrivent les trajectoires testées,
pas une garantie pour toute destruction ou toute charge électrique.
