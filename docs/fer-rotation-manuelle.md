# Fer & Flamme — participation des réacteurs latéraux en manuel

## Défaut et contrat corrigé

Sur le plan joueur sauvegardé, Q actionnait les trois réacteurs verticaux
(`−585,73 / −585,73 / +1 171,46 N`) et laissait les deux latéraux à zéro.
L'allocation ne considérait que leur capacité à produire un couple à force
nette nulle. Les deux latéraux étant à la même hauteur, leur couple vaut
`−ry × Fx` : annuler Fx annule aussi tout leur couple.

En manuel, cette contrainte n'était pas demandée. `repartirManuel` calcule
désormais la capacité de couple de chaque groupe depuis les bornes de chaque
actionneur et son bras de levier. Après partage du couple, il choisit, parmi
les forces réalisables à ce couple, celle qui est la plus proche de la commande.
Un latéral peut donc contribuer même si une dérive accompagne sa poussée.
Quand un couple pur est possible pour le groupe, une force nulle reste choisie
si aucune translation n'est demandée.

Les limites des moteurs, la poussée inversée, le budget électrique et l'inertie
sont conservés. Le plafond de rotation encore présent lors de cette passe a
depuis été supprimé : Q/D demandent tout le couple disponible, voir le
[contrat manuel courant](fer-manuel.md). Une passe ultérieure ajoute le freinage
automatique au relâchement de Q/D, sans recentrage de l'angle. Pendant l'appui,
le couple suit la jauge ; le freinage utilise toute l'autorité opposée disponible.
Le contrôleur assisté est inchangé.

## Validation de la participation latérale avant retrait du plafond

`tools/test-fer-manuel.cjs` : plan exact du joueur, mêmes moteurs déplacés
au-dessus du centre de masse, montage asymétrique, chacun après deux
chargements ; montage supplémentaire à tuyères horizontales décalées.
Appuis ZQSD réels dans un navigateur isolé, Rapier et rendu du jeu.

- Sur le joueur, rotation Q seule : latéraux **−239,41 / +478,82 N**, soit
  **+519,48 N·m** sur les **+878,60 N·m** demandés, avec **+718,23 N** de
  force latérale. Les autres réacteurs complètent le couple.
- Au-dessus du centre de masse, les latéraux poussent dans l'autre sens :
  **−634,73 N**, avec un couple toujours positif (**+401,90 N·m**).
- Q et D, rotation seule et combinée à Z : contribution des latéraux dans
  le bon sens, bornes des moteurs et consommation vérifiées.
- Couple et dérive cohérents avec les bras de levier ; inertie conservée au
  relâchement, contre-braquage, annulation des touches opposées, commandes
  ON/OFF et équivalence des alias vérifiés. Les 80 contrôles mathématiques
  d'enveloppe passent aussi.

Tous ces contrôles passent, aucune erreur JavaScript. Capture du plan joueur
rechargé inspectée ; artefacts dans `artifacts/fer-manuel/`, référence antérieure
`reference-rotation-laterale.json`. Aucune modification de la sauvegarde
personnelle ni de `main`.
