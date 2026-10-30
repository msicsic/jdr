# Tâche Codex 379 : A2, famille expression et son : un sens unique pour moteur, schéma et plan public

Deuxième lot A2 de la forme A du compilateur (`docs/conception-g1.md`, section A, points 3 à 7) après la famille séquence et attente (lot 370, fusionné, rapport `docs/taches/rapport-codex-370-*.md`, dont tu reprends la méthode). Ce lot ne traite que la famille **expression et son** (siffler, crier, héler, chuchoter une manière, frapper pour faire du bruit, `emettre_son` et ses méthodes).

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Une opération de la famille expression/son et ses raccourcis ont un sens unique, le même pour le moteur, le schéma du compilateur et le plan public montré au joueur (« Compris : … ») ; aucun champ voisin simplement légal ne remplace la charge requise.** Cas réel, autre cas et faux pendant ; mécanique inchangée (ouïe commune, appels, réponses). Pas de changement de revue ni de raccord libre (A4, A6).

Luna : aucune passe dans ce lot.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/compilateur.py` ou le schéma en vigueur, `donjon/comprehension.py`, `donjon/commandes.py`, tests. Lots en cours : 374 (position crue), 375 (rouges de la suite), 378 (S1a, porte des épisodes, esprits.py) ; pendant S1, n'ajoute aucun registre d'esprit ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-a2-expression-son`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-379-a2-expression-son.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\a2-expression-son-379\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
