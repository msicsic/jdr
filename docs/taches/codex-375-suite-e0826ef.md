# Tâche Codex 375 : Les onze méthodes rouges de la suite e0826ef

La suite complète de l'intégration `e0826efc` (après les lots 360 à 368, E5 et E6) donne **15 échecs sur 11 méthodes**, contre 104 sur `f014c80`. Neuf sont apparues depuis `f014c80` (fusions 360, 361, 362, 359, 363/364, 366, 367, 368) : avis redits (deux), banc sans joueur, bourse redemandée, complétion des preuves, prêt réclamé, attente d'une part, rendez-vous, traîner. Deux restent d'avant : intermédiaires (laps découpé) et `DemanderLePassageTests`. Liste : `C:/Users/msics/donjon/artifacts/suite-e0826ef/rouges.txt`, suite brute `C:/Users/msics/donjon/artifacts/suite-e0826ef/suite.log`. Suspect probable pour plusieurs : la règle du lot 360 (l'inventaire connu dès le départ n'est pas une nouvelle ; décision de l'utilisateur, à garder).

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les rapports des lots cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Chaque méthode rouge est attribuée à la fusion qui l'a fait basculer (bissection `--first-parent` entre `f014c80` et `e0826efc`), puis corrigée dans le contrat commun si la cause est claire et locale, ou adaptée seulement si son attente est devenue fausse par un changement voulu et documenté (preuve citée, assertions de sécurité intactes) ; sinon listée avec la question précise.** La règle du lot 360 est une décision de l'utilisateur : un test qui suppose qu'un PNJ confie son inventaire de départ s'adapte à elle (preuve : rapport 360).

## Contraintes
**Poste : le laptop.** Fichiers attendus : selon la cause ; tests ; signale tout fichier commun avec les lots en cours. Lots en cours : 365 (catalogue), 369 (U-T social), 373 (S0, documentation), 374 (position crue, `esprits.py`/`planification.py`), 375, 376, 377 ; signale tout recouvrement. Pendant S1 à venir, n'ajoute aucun nouveau registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-suite-e0826ef`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-375-suite-e0826ef.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\suite-e0826ef-375\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
