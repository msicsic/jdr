# Tâche Codex 372 : A6, le soupçon déduit : qui a pris mon bien, d'après mes croyances

Suite d'A6 (`docs/plan-agendas.md`, lot 192 et « Reste A6 » : occasions, soupçon déduit, disparition attribuée sans portage constaté). Aujourd'hui un projet `récupérer {objet, qui}` ne naît que si le propriétaire a constaté qui porte son bien.

Lis `AGENTS.md`, `docs/etat-dev.md` (court) et les documents cités. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Un PNJ qui constate qu'un de ses biens a disparu de là où il le croyait en déduit, à partir de ses seules croyances (qui il a vu ou entendu près du bien depuis son dernier regard, qui le convoitait d'après les signes lus, qui a l'habitude de prendre), un ou plusieurs suspects pondérés ; le soupçon est une croyance faillible, sauvegardée, qui peut ouvrir le projet `récupérer` contre le suspect le plus probable (question, recherche, réclamation selon les moyens existants), jamais une certitude ni une lecture de l'état réel.** Un soupçon démenti (bien retrouvé ailleurs, suspect innocenté par un constat) se retire. Une épreuve sociale (méfiance) ne se crée que par la voie commune, à la mesure de la conviction.

Luna : aucune passe.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/esprits.py`, `donjon/agendas.py`, `donjon/social.py` si le soupçon se dit ; tests ; lis le rapport 192. Lots en cours : 365 (catalogue des choix), 369 (U-T social information), 370, 371, 372 ; signale tout recouvrement. Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna.

## Livraison
Branche `codex-soupcon-deduit`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-372-soupcon-deduit.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\soupcon-deduit-372\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
