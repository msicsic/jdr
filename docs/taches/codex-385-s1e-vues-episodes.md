# Tâche Codex 385 : S1e, tous les autres lecteurs d'épisodes passent par des vues pures

Cinquième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1e, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383) et S1d (384), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 382, 383 et 384, dont tu reprends la méthode.

## Invariant (un seul)
**Tous les lecteurs d'épisodes qui restent (jeu, rendu, récit, rejeu, banc, audit et outils) passent par des vues pures de `donjon/memoire.py` qui renvoient des copies ; plus aucune lecture directe du stock d'épisodes hors de la porte, et l'inventaire AST de lecture atteint zéro hors exceptions nommées.** Stockage historique strictement inchangé (liste, plafond 40, ordre, clés, sérialisation). Aucun changement de choix, de parole, de texte affiché, d'ordre des `paroles_retenues`, de métrique historique, de dernier son ni des trois derniers souvenirs montrés. Si le lot dépasse le créneau, livre une partie cohérente (par exemple jeu et rendu, puis outils) et dis ce qui reste.

## Vérification
Les fichiers que S0 indique pour S1e (annexe A ; rendu, récit, rejeu, banc, audit des nuits) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 374 (position crue, repris :
`deliberation.py`/`echanges.py`/`esprits.py`/`pnj.py`/`planification.py`), 375 (rouges de la suite), 380 (U-M social
comptes, web), 381 (A2 passage, `operations.py`/`comprehension.py`) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1e-vues-episodes`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-385-s1e-vues-episodes.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1e-385\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
