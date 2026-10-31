# Tâche Codex 408 : S1j (suite), l'identité vocale par des vues sourcées

Suite du dixième lot de S1 (le 406 a livré paroles, audiences et savoir initial), le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1j, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384), S1e (385), S1f (397), S1g (400), S1h (404), S1i (405) et S1j partiel (406), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 405 et 406, dont tu reprends la méthode.

## Invariant (un seul)
**L'identité vocale (voix connues, voix entendues et leur signature, prétentions d'un nom, méfiance, imposture démasquée, noms retenus) se lit et s'écrit seulement par des vues sourcées de `donjon/memoire.py` (ou de l'interface de croyances du 397) ; plus aucun accès direct à ces registres hors de l'interface.** Saturation des voix entendues (éviction actuelle), imposture démasquée après coup, voix inconnue au MJ (`voix_<n>`), genre d'une voix et noms appris conservés ; stockage historique inchangé ; aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST décroît.

## Vérification
Les fichiers que S0 indique pour la partie vocale de S1j (`voix`, `voix_inconnues`, `voix_suite`, `noms`, `parole_voix`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 402 (vérification d'intégration, calcul seul), 407 (A2 consultation sociale) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1j-voix`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-408-s1j-voix.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1j-408\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
