# Tâche Codex 406 : S1j, paroles, audiences, savoir initial et identité vocale par des vues sourcées

Dixième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1j, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384), S1e (385), S1f (397), S1g (400), S1h (404) et S1i (405), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 404 et 405, dont tu reprends la méthode.

## Invariant (un seul)
**Les paroles retenues, les audiences, le savoir initial (dont la décision du 360 : un inventaire de départ n'est pas une nouvelle) et l'identité vocale (voix connues, prétentions, imposture) se lisent et s'écrivent seulement par des vues sourcées de `donjon/memoire.py` (ou de l'interface de croyances du 397) ; plus aucun accès direct à ces registres hors de l'interface.** Saturation des registres, imposture démasquée, témoin absent et registre de ce qui a été dit (lot 64) conservés ; stockage historique inchangé ; aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST décroît. Si le diff dépasse le créneau, livre une partie cohérente (par exemple paroles et audiences, puis identité vocale) et dis ce qui reste.

## Vérification
Les fichiers que S0 indique pour S1j (`deja_dit`, `parole_commune`, `social`, `voix`, `voix_inconnues`, `noms`, `garde_ouidire`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 381 (A2 passage, en fusion), 403 (rouges de la suite c562aa21) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1j-paroles-voix`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-406-s1j-paroles-voix.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1j-406\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
