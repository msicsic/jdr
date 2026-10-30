# Lot 349 — U-M passage

Branche `codex-um-passage`, base intégration `a0f0eba`, non fusionnée.

## Invariant et changement

`gestes_publics.passages_publics` propose dessous/dessus sur un obstacle
perçu dont la forme est établie, le parcours d'une échelle installée et
le franchissement avec un appui mobile déjà arbitré. Le menu ne calcule
aucune aptitude : gabarit, charge, encombrement, état du matériel et jets
restent jugés par le moteur. La page reçoit seulement les références et
les choix publics, sans dimensions, préconditions ou difficulté à choisir.
L'échelle se choisit sur son support, sa représentation sur la carte.
Les homonymes matériels portent un rang visible et gardent leur identité.

`commandes.passage_descripteur` revalide l'offre et construit la même
proposition que la commande locale. La nouvelle commande
`franchir <obstacle> avec <appui>` reprend un arbitrage mémorisé et inclut
la prise si l'appui est au sol. Le clic ne passe ni par l'analyseur ni par
le MJ. `moteur.preparer` raccorde cette famille au consentement existant,
au récapitulatif « Compris » et à la revalidation exacte du descripteur
jusqu'à confirmation ; annuler ne publie aucun effet.

Deux raccords nécessaires hors des fichiers principaux : `moteur.py`
pour le consentement ; extraction pure de `franchissement.cle_arbitrage`
pour réutiliser le sceau existant sans tester la faisabilité au menu.
La signature et les règles de franchissement sont conservées ; ni
`obstacles.py`, MJ, `jeu.py` ou `tui.py` ne changent. Aucun fichier de code
commun avec les lots 345/348 ; `etat-dev.md` est commun à la livraison.

## Vérification et mesures

Vérification finale ciblée en cours : passages publics, franchissement,
sous-obstacle, web/Node, descripteur public et consentement.
Les nouveaux tests comparent plans, effets, textes et monde/scène/fiche/carte
après recharge dans la vraie boucle, avec MJ interdit et sauvegarde avant
affichage. Les sept bancs réels `sous-obstacle-*` sont repris sur copies :
Relais, auberge, enjambement, trop bas, trop haut, encombré et forme inconnue.
Échelle dans les deux sens, perche portée ou prise au sol, annulation,
référence/qualification périmée, paramètres injectés et homonymes sont couverts.

Bruts : `C:/Users/msics/donjon/artifacts/um-passage-349/`.
Clôture détachée : `fin-verification.json`, écrit en dernier après le bilan
`tests-final.json` et les mesures des callbacks (`mesures.json`). Les premiers
essais restent dans `premiere.json` et `reprise.json` ; ils ne valent pas validation.
Mesures et bilan final à reporter à la reprise, avant de déclarer le lot terminé.
Deux travailleurs au plus, priorité réduite ; aucune suite complète,
passe Luna ou banc PNJ, l'entrée d'interface seule étant portée.

## Limites et livraison

Décision explicite de l'utilisateur : **le saut à la perche n'est offert
que pour une difficulté déjà mémorisée dans le même contexte physique**.
Un premier arbitrage reste au chemin libre du MJ ; le joueur ne fixe pas
sa difficulté. Une forme inconnue reste à qualifier séparément (G13).
Une offre ne promet jamais la réussite. U-T passage reste à faire.
Branche à pousser vers `origin` avec ce statut de calcul en cours ; fusion
laissée au superviseur. Aucun résultat final vert n'est encore revendiqué.
