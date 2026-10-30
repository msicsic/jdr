# Tâche Codex 376 : Les messages affichés ne dépendent pas du découpage du temps

Le lot 371 (`docs/taches/rapport-codex-371-evaluation-echeance.md`, bruts `C:/Users/msics/donjon/artifacts/evaluation-echeance-371/`, `jeu.json`) relève, à l'auberge, que **le même laps passé d'un bloc ou découpé donne le même état final mais des messages différents** (« quitte la pièce » contre « aperçois un instant » pour Odile autour de l'extinction). Le principe commun est : même laps découpé, même monde **et même ce que voit le joueur**.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les rapports des lots cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Ce que le joueur lit pendant un laps (présences, départs, aperçus, sons) ne dépend pas du découpage de ce laps en actions : le bilan des présences (`pnj.bilan_presences` et voisins) se calcule sur ce que Corvus a effectivement perçu pendant le laps entier, quel que soit le nombre de tranches.** Reproduis d'abord sur la capture du 371, trouve la cause, corrige le contrat commun, vérifie un autre cas (Relais ou mine).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/pnj.py` (bilan des présences), `donjon/moteur.py` ou l'attente découpée de `commandes`, tests. Lots en cours : 365 (catalogue), 369 (U-T social), 373 (S0, documentation), 374 (position crue, `esprits.py`/`planification.py`), 375, 376, 377 ; signale tout recouvrement. Pendant S1 à venir, n'ajoute aucun nouveau registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-messages-decoupage`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-376-messages-decoupage.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\messages-decoupage-376\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
