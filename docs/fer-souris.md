# Fer & Flamme — boutons souris indépendants

## Invariant et correction

Chaque commande maintenue suit son bouton, indépendamment des appuis et
relâchements des autres boutons. La visée, le moteur des armes et le rendu
partagent cet état ; aucun appui n'est sauvegardé.

Le jeu écoutait `pointerdown` pour chaque commande alors que, pour une souris,
seul le premier appui produit cet événement. Son `pointerup` annulait toutes
les commandes. L'essai sur le vrai navigateur a reproduit le défaut : après
gauche puis droite, l'orientation du bouclier restait inactive.

`synchroniserBoutonsSouris` lit le masque `buttons` sur `mousedown`, `mousemove`
et `mouseup`. Les deux bits sont indépendants. `mouseup` est reçu sur la fenêtre
pour ne pas perdre un relâchement hors du canvas. Les actions de l'atelier
utilisent également `mousedown`. La position est actualisée dès l'appui, puis
le bouclier est orienté si son bouton est maintenu. La sortie du canvas, la
perte de focus, `pointercancel` et les transitions atelier/piste utilisent la
même remise à zéro des deux commandes.

Références navigateur : [pointerdown](https://developer.mozilla.org/en-US/docs/Web/API/Element/pointerdown_event)
et [buttons](https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent/buttons).

## Vérification

`tools/test-fer-souris.cjs`, même environnement de test isolé et variables que
`test-fer-assistance.cjs` (`FER_PUPPETEER_MODULE`, `FER_BROWSER`, `FER_RAPIER_MODULE`).
Rapier réel, boucle du jeu et vrais appuis/relâchements du navigateur de test ;
aucun accès au navigateur ou à la sauvegarde personnels.

- Canon et laser avec bouclier, avant et après recharge du même build : huit
  combinaisons arme/recharge/ordre d'appui ; les deux ordres de relâchement sont
  contrôlés pour chaque combinaison.
- Les deux commandes restent actives ensemble ; obus consommés ou charge du
  laser dépensée avec faisceau produit et rendu, bouclier réellement orienté.
- Relâcher droite conserve le tir et fige l'orientation ; relâcher gauche
  conserve l'orientation et arrête les nouveaux tirs.
- Sortie réelle du canvas, événement de perte de focus et aller-retour
  atelier/piste : aucune commande bloquée.
- Plan rechargé identique, état et HUD vérifiés, huit captures produites.

Résultats : `artifacts/fer-souris/resultats.json` et captures dans le même
dossier, ignorés par Git. Travail non fusionné ; `main` inchangé.
