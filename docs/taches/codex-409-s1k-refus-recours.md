# Tâche Codex 409 : S1k, refus et recours par leurs seuls prédicats historiques

Onzième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1k, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384), S1e (385), S1f (397), S1g (400), S1h (404), S1i (405) et S1j (406, 408), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 406 et 408, dont tu reprends la méthode.

## Invariant (un seul)
**Les refus retenus et les recours (demande, raison, date, cause, offre et contre-offre, recours de propositions, de services et d'intermédiaires, service en cours) se lisent et s'écrivent seulement par des vues et opérations nommées de `donjon/memoire.py` (ou de l'interface de croyances du 397), et ne se réarment que par leurs prédicats historiques : une baisse de moyens ou le seul passage du temps ne lèvent rien.** Prédicats de réouverture et publication au choix réussi conservés ; stockage historique inchangé ; aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST décroît. Si le diff dépasse le créneau, livre une partie cohérente (par exemple refus retenus, puis recours) et dis ce qui reste.

## Vérification
Les fichiers que S0 indique pour S1k (`refus_retenus`, `proposer_recours`, `rendre_service`, `refus_leve_contrepartie`, `offre_sensee`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 402 (vérification d'intégration, calcul seul), 407 (A2 consultation sociale) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1k-refus-recours`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-409-s1k-refus-recours.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1k-409\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
