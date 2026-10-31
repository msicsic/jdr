# Tâche Codex 384 : S1d, promesses, prêts et travaux payés lisent leurs épisodes par des requêtes nommées

Quatrième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1d, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382) et S1c (383), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 382 et 383, dont tu reprends la méthode.

## Invariant (un seul)
**Les promesses, les prêts et les travaux payés lisent et marquent leurs épisodes (accord, remise, réalisation datée, réclamation, abandon annoncé) seulement par des requêtes et opérations nommées de `donjon/memoire.py` ; leurs requêtes historiques gardent exactement la même fenêtre de 40 souvenirs et le même ordre.** Stockage historique strictement inchangé (liste, plafond 40, ordre, clés, sérialisation), mêmes crochets et même réentrance. Aucun changement de choix, de parole, de délai, de tirage, de classement, de dette ni de clôture d'engagement. L'autorité d'`agendas` sur les engagements ne se déplace pas. L'inventaire AST décroît : ces accès disparaissent de la fixture.

## Vérification
Les fichiers que S0 indique pour S1d (`promesses`, `taches_payees`, `contrat_engagement`, `echanges_suite`, `reclamations_repetees`, `realisation_datee`) et ceux
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
- Branche `codex-s1d-promesses`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-384-s1d-promesses.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1d-384\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
