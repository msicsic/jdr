# Tâche Codex 405 : S1i, signes, détresse et dangers avec une invalidation subjective unique

Neuvième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1i, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384), S1e (385), S1f (397), S1g (400) et S1h (404), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 400 et 404, dont tu reprends la méthode.

## Invariant (un seul)
**Les croyances sur les signes perçus, la détresse d'autrui et les dangers se lisent et s'écrivent seulement par des vues de `donjon/memoire.py` (ou de l'interface de croyances du 397), avec une seule règle d'invalidation subjective par propriété : perdre le regard ne dément rien, seul un constat contraire ou la fin connue invalide.** Lectures de signes, jets, cadence de dix minutes, suivi par observateur et épisodes conservés ; stockage historique inchangé ; aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST décroît. Si le diff dépasse le créneau, livre une partie cohérente (par exemple signes, puis détresse et dangers) et dis ce qui reste.

## Vérification
Les fichiers que S0 indique pour S1i (`signes`, `empathie_peur`, `peur_transmise`, `defense`, `secours_acquitte`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 381 (A2 passage), 399 (rembourser depuis le menu et le terminal), 403 (rouges de la suite c562aa21) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1i-signes-dangers`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-405-s1i-signes-dangers.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1i-405\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
