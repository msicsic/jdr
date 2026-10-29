# Tâche Codex 321 : U-T fabrication, la recette paramétrée au terminal

Lot U-T fabrication de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md). Lis `AGENTS.md` et les rapports
du formulaire web de fabrication (lot 305, `docs/taches/rapport-codex-305-um-fabrication.md`) et du terminal (lots 299,
301 et 307 : `rapport-codex-299-ut-premier-geste.md`, `rapport-codex-301-ut-inventaire.md`, `rapport-codex-307-ut-outils.md`).

## L'invariant
**Console et TUI permettent d'assembler et de découper avec la même recette paramétrée que le formulaire web : usage,
pièces par rôle, lien, outil et dimensions, choisis parmi les seules ressources connues de Corvus, sous leurs références
publiques. Le choix envoie le même descripteur U-D au moteur, sans analyse de texte ni modèle.** Le moteur seul juge
les pièces et les droits ; une référence périmée est refusée sans substitut ; une forme inconnue est dite sans valeur
inventée. Les usages, rôles et capacités viennent du catalogue commun (`gestes_publics`), comme pour le web et les
outils (307) : aucune liste parallèle de verbes ou de recettes.

## Vérification
- Parité : les quatre parcours du lot 305 (assemblage d'une échelle, découpe) refaits au terminal, même descripteur,
  même plan, même effet et même rendu que la commande et que le web ; monde, scène, fiche et carte après recharge.
- Une pièce périmée ou hors de portée, une forme inconnue, un bien d'autrui (droits du moteur).
- Mesure des touches jusqu'à l'effet, comme les lots 299 et 301.
- Tests ciblés, dont les 28 tests TUI existants inchangés. Pas de Luna, de banc ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Le lot U-P (319, laptop) touche `jeu.py` et `rendu.py` :
signale tout recouvrement.

## Livraison
- Branche `codex-ut-fabrication`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-321-ut-fabrication.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ut-fabrication-321\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
