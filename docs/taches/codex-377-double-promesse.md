# Tâche Codex 377 : Une même part n'est pas promise deux fois

Le lot 371 relève, auberge graine 7, minute 187 : **Mireille promet de remettre `marmite_2` à Tilo, puis vend le service de cette même part à Mathurine pour une pièce** ; remboursement 233 dixièmes après le paiement (`auberge-7.json.gz` dans `C:/Users/msics/donjon/artifacts/evaluation-echeance-371/`).

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les rapports des lots cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Un bien ou une part déjà promis (engagement en cours) n'est pas promis ni vendu une seconde fois tant que le premier engagement tient : le devis d'une offre ou d'une vente compte les engagements en cours du promettant (même voie pour les parts, objets et services), d'après ses seules croyances.** Reproduis sur la capture, corrige le contrat commun (`agendas`, `echanges`), vérifie un autre cas ; aucune promesse légitime ne disparaît (une part encore disponible reste vendable).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/echanges.py`, `donjon/agendas.py`, `donjon/biens.py` si la réservation y vit, tests. Lots en cours : 365 (catalogue), 369 (U-T social), 373 (S0, documentation), 374 (position crue, `esprits.py`/`planification.py`), 375, 376, 377 ; signale tout recouvrement. Pendant S1 à venir, n'ajoute aucun nouveau registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-double-promesse`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-377-double-promesse.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\double-promesse-377\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
