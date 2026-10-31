# Tâche Codex 381 : A2, famille passage : un sens unique pour moteur, schéma et plan public

Troisième lot A2 de la forme A du compilateur (`docs/conception-g1.md`, section A, point 3) après séquence/attente (370) et expression/son (379), fusionnés. Reprends la méthode du rapport 379 (`docs/taches/rapport-codex-379-*.md`, module de contrat commun, tests cas réel/autre cas/faux pendant). Ce lot ne traite que la famille **passage** : `passer_obstacle` (dessous, dessus), franchir, demander le passage et pousser pour passer, avec leurs raccourcis.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Une opération de la famille passage et ses raccourcis ont un sens unique, le même pour le moteur, le schéma du compilateur et le plan public montré au joueur (« Compris : … ») ; aucun champ voisin simplement légal ne remplace la charge requise (obstacle, côté, manière, destinataire).** Cas réel, autre cas et faux pendant ; mécanique inchangée (gabarit, jet commun, durées, passage social de `passage.py`). Pas de changement de revue ni de raccord libre (A4, A6).

Luna : aucune passe dans ce lot.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : un module de contrat de la famille (comme `contrats_son.py`), `donjon/operations.py`, `donjon/comprehension.py`, `donjon/commandes.py`, `donjon/obstacles.py` ou `donjon/franchissement.py` seulement pour réemployer leurs tables, tests. Lots en cours : 374 (position crue, `esprits.py`/`planification.py`), 375 (rouges de la suite), 378 (S1a, `esprits.py`), 380 (U-M social comptes, `web/page.html`) ; pendant S1, n'ajoute aucun registre d'esprit ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-a2-passage`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-381-a2-passage.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\a2-passage-381\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
