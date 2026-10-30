# Tâche Codex 371 : Évaluation du noyau de l'échéance négociée (E1 à E6) avant E7 à E9

Le noyau de l'échéance négociée est fusionné : E1 (348), E2 (350), E3 (352, correctif 357), E4 (355), E5 (359), E6 partiel (363/364). La conception (`docs/conception-menace-echeance.md`, section 5, « Noyau jouable après E1–E6 ») prévoit une **évaluation avant E7–E9** (offres PNJ, révision, délais proposés par les PNJ).

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Lot de mesure et de jeu, sans changement de code.** Joue le cas de jeu 1.2 de la conception (auberge, huile livrée à temps) et un autre cas (Relais ou mine), en choix direct (menu, terminal) et en texte libre, sur copies : ce que le joueur peut faire, combien de choix/appels jusqu'à l'accord, ce qui casse, ce qui est confus ; réalisation à temps et en retard, remboursement, comptes, paroles, recharge. Mesure aussi, sur un banc rapide 4 h (quatre graines, auberge, Relais, mine), si les PNJ rencontrent des situations où un délai les aiderait (sans E9 ils n'en proposent pas) : cas observés, fréquence. Conclus par une recommandation pour E7, E8, E9 (lesquels, dans quel ordre, ou s'arrêter) et les questions à l'utilisateur.

Luna : une passe ciblée sur les scripts du texte libre (prépare-les ; si la revue automatique bloque, dépose la commande, l'orchestrateur la jouera).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : aucun fichier de code ; scripts de banc et bruts seulement. Lots en cours : 365 (catalogue des choix), 369 (U-T social information), 370, 371, 372 ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-evaluation-echeance`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-371-evaluation-echeance.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\evaluation-echeance-371\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
