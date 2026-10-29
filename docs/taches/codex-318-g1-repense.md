# Tâche Codex 318 : repenser G1, le compilateur d'intention (conception)

Décision de l'utilisateur du 2026-10-29 : G1 n'est pas fusionné ; il est **repensé** avant tout nouveau code.
Lis `AGENTS.md` (contrat du MJ), `docs/plan-refonte-mj.md` (ligne G1 et ses dépendances), `docs/conception-refonte-mj.md`,
`docs/conception-valeur-llm.md`, puis les quatre rapports de la branche `codex-g1-compilateur` (sur `origin`) :
`rapport-codex-294-*`, `rapport-codex-296-*`, `rapport-codex-304-g1c-familles.md`, `rapport-codex-311-g1d-revue.md`.
Bruts : `C:\Users\msics\donjon\artifacts\g1d-311\` et les dossiers des lots 294, 296, 304 sur le laptop.

## Le constat
Quatre reprises (294, 296, 304, 311) ont toutes manqué leurs critères. Dernière mesure (311, une passe, six scripts) :
- gains : prix de mission fidèle ; entrée divisée par 1,6 (22 572 → 13 858 jetons) ; secondes modèle 9,8 → 7,7 par tour ;
- pertes : appels/tour 3,30 → 3,47 ; admission au premier coup 22 → 21/30 ; intentions fidèles 27 → 23 ; abandons 1 → 3 ;
- défauts : Luna nie une opération disponible (levier, crypte/10) ; passages et coups remplacés par des gestes étrangers ;
  attente omise d'un vol ; famille de refus nouvelle (avis sur lieu inconnu) ; justification technique affichée au joueur.

## Ce qui est demandé : conception seule
1. Établis, saisie par saisie sur les quatre campagnes, **pourquoi** le petit contexte perd ces intentions. Distingue :
   une information retirée du contexte dont la compilation avait besoin (laquelle) ; une consigne ambiguë ; un schéma
   qui pousse vers une opération voisine ; la revue de fidélité trop stricte ou trop permissive ; une variance de Luna.
2. Dis ce que le compilateur doit **garder** de l'ancienne interprétation (contexte, consignes, schéma) et ce qu'il peut
   laisser, avec la preuve tirée des fils.
3. Propose **au plus deux formes** de G1, chacune avec son périmètre (toutes les saisies libres, ou seulement celles
   que les actions directes U-* ne couvriront pas), ses critères mesurables (mêmes axes I/V/F/P que la feuille de
   route) et son découpage en lots d'un invariant. Évalue ce que les lots d'interface déjà fusionnés (U-D, U-T, U-M)
   retirent du texte libre, d'après les bancs existants.
4. Recommande une forme, ou de suspendre G1 jusqu'après d'autres lots, et dis pourquoi.

Aucun code du jeu modifié, aucune passe Luna nouvelle : relis les fils archivés (et rejoue hors ligne les requêtes si
utile, sans appel au modèle). Ni banc ni suite complète.

## Contraintes
**Poste : le laptop.** Un processus Python léger à la fois.

## Livraison
- Branche `codex-g1-repense`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Note de conception `docs/conception-g1.md` et rapport d'une page `docs/taches/rapport-codex-318-g1-repense.md` ;
  entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g1-318\`.
- Termine par `LOT TERMINÉ` ou `QUESTION : …`.
