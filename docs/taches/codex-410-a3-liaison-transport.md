# Tâche Codex 410 : A3, liaison du transport : mode, charge, opération et paramètres corrélés

Lot A3 de la forme A du compilateur (`docs/conception-g1.md`, section A, point 4), après A0, A1 et les quatre lots A2 par famille (370 séquence/attente, 379 expression/son, 381 passage, 407 consultation sociale), tous fusionnés. Les modules de contrat par famille (`contrats_son.py`, `contrats_passage.py`, `contrats_consultation.py`…) donnent le sens de chaque opération ; ce lot les relie au transport vers Luna.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), `docs/conception-g1.md` (section A), les rapports 370, 379, 381 et 407. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Dans le schéma transmis au fournisseur, le mode et la charge, puis l'opération et ses paramètres, sont corrélés par la grammaire commune des contrats : une proposition dont un champ voisin simplement légal remplace la charge requise est impossible à exprimer ou refusée avant préparation avec son `attendu` ; le transport cloud (OpenAI) et le prompt local portent le même sens.** Aucune sélection de schéma par lieu, scénario ou mot-clé. L'ordre exact dépend des limites du fournisseur (taille et forme du schéma) : vérifie-le hors ligne d'abord.

**Luna : une passe ciblée**, sur copies, des bancs qui exercent les quatre familles (`relais`, `atelier`, `echanges`, `noms-dialogue`, `sous-obstacle-relais`). Si la revue automatique la bloque, laisse la commande exacte dans les bruts. Le contrat ne garantit pas le choix sémantique de Luna : mesure-le, sans l'affirmer.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/fournisseurs/contrat.py`, `donjon/fournisseurs/local.py`, `donjon/operations.py`, les modules de contrat par famille, `donjon/sources.py` si nécessaire, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 409 (S1k refus et recours, `memoire.py`) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna hors de la passe demandée ci-dessus.

## Livraison
Branche `codex-a3-liaison-transport`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-410-a3-liaison-transport.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\a3-liaison-transport-410\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
