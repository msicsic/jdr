# Tâche Codex 404 : S1h, eau, prévisions et statuts par des preuves accessibles et une révision déclarée

Huitième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1h, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384), S1e (385), S1f (397) et S1g (400), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 397 et 400, dont tu reprends la méthode.

## Invariant (un seul)
**Les croyances d'eau (niveau mesuré, prévision, pente), les avis de menace reçus et les statuts sourcés se lisent et s'écrivent seulement par des vues et une politique de révision déclarée de `donjon/memoire.py` (ou de l'interface de croyances du 397) ; plus aucun accès direct à ces champs de `croyances` hors de l'interface.** Poids, conviction, dates, preuves et jets actuels conservés à l'identique ; stockage historique inchangé ; aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST décroît. Si le diff dépasse le créneau, livre une partie cohérente (par exemple eau et prévisions, puis statuts) et dis ce qui reste.

## Vérification
Les fichiers que S0 indique pour S1h (`avis_menace`, `avis_parles`, `disputes`, `relations_statuts`, `eau`, `prevision_bornee`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 381 (A2 passage), 399 (rembourser depuis le menu et le terminal), 403 (rouges de la suite c562aa21) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1h-eau-statuts`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-404-s1h-eau-statuts.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1h-404\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
