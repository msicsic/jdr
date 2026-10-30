# Tâche Codex 353 : U-T corps et passage, les gestes de corps et les franchissements au terminal

Lots U-T corps et U-T passage de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md), réunis parce qu'ils
portent le même invariant sur les mêmes fichiers. Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les rapports du web
(lot 344 U-M corps, lot 349 U-M passage) et du terminal (lots 299, 301, 307, 321 : `rapport-codex-299-ut-premier-geste.md`,
`rapport-codex-301-ut-inventaire.md`, `rapport-codex-307-ut-outils.md`, `rapport-codex-321-ut-fabrication.md`).

## L'invariant
**Console et TUI proposent, sur une personne ou un obstacle perçus, les mêmes gestes de corps (méthode, arme, réactions
à une agression) et les mêmes franchissements qualifiés que le menu web, choisis parmi les seules ressources connues de
Corvus ; le choix envoie le même descripteur U-D au moteur, sans analyse de texte ni modèle.** Les gestes et méthodes
viennent du catalogue commun (`gestes_publics`), comme pour le web : aucune liste parallèle. Le moteur seul juge ; un
geste lourd passe par le consentement U-C ; les réactions n'apparaissent que sur danger perçu ; le saut à la perche
n'est proposé qu'avec un arbitrage déjà mémorisé (décision du lot 349) ; aucune dimension ni forme inventée.

## Vérification
- Parité avec le web et la commande : parcours des lots 344 et 349 refaits au terminal (frapper, assommer, ligoter,
  fuir/riposter sur danger perçu ; dessous, dessus, trop bas, encombré, forme inconnue), même descripteur, même plan,
  même effet et même rendu ; monde, scène, fiche et carte après recharge ; consentement et annulation.
- Référence périmée ou cible partie : refus public, aucun substitut. Zéro appel au modèle.
- Mesure des touches jusqu'à l'effet, comme les lots 299 et 301.
- Tests ciblés, dont les tests TUI existants inchangés. Pas de Luna, de banc ni de suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Fichiers attendus : `jeu.py`, `tui.py`, le descripteur
U-D et `gestes_publics.py` seulement si un paramètre public manque. Le lot 354 (U-M social information, laptop) touche
`page.html`/`dialogues.py` : signale tout recouvrement.

## Livraison
- Branche `codex-ut-corps-passage`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-353-ut-corps-passage.md`, entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ut-corps-passage-353\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
