# Tâche Codex 383 : S1c, approches, avertissements et secours lisent et acquittent la même occurrence

Troisième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1c, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378) et S1b (382), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378 et 382, dont tu reprends la méthode.

## Invariant (un seul)
**Une approche observée, un avertissement d'interposition et un secours (cri d'un protégé, appel à l'aide) se lisent et s'acquittent sur la même occurrence de mémoire, par des requêtes et opérations nommées de `donjon/memoire.py` : plus aucun `examine`/`tenu` posé sur une copie perdue ni mutation d'un alias hors de la porte.** Stockage historique strictement inchangé (liste, plafond 40, ordre, clés, sérialisation), mêmes crochets et même réentrance. Aucun changement de choix, de parole, de délai, de tirage, de classement ni d'acquittement observable. L'inventaire AST décroît : ces accès disparaissent de la fixture.

## Vérification
Les fichiers que S0 indique pour S1c (`interposition`, `interposition_lieu`, `protection`, `secours_acquitte`) et ceux
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
- Branche `codex-s1c-approches-secours`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-383-s1c-approches-secours.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1c-383\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
