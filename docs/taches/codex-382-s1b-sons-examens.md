# Tâche Codex 382 : S1b, sons et examens par requêtes et opérations nommées

Deuxième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1b, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (lot 378, fusionné : porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et le rapport 378, dont tu reprends la méthode.

## Invariant (un seul)
**Les souvenirs de sons et d'examens (bruit retenu, bruit couvert, examen vain, rafraîchissement d'un examen) se lisent
et se modifient seulement par des requêtes et opérations nommées de `donjon/memoire.py` ; plus aucune mutation d'un alias
de la mémoire sonore hors de la porte.** Stockage historique strictement inchangé (liste, plafond 40, ordre, clés,
sérialisation), mêmes crochets et même réentrance. Aucun changement de choix, de parole, de délai, de tirage, de
classement ni de couverture sonore. L'inventaire AST décroît : les accès sonores/examens disparaissent de la fixture.

## Vérification
Les fichiers que S0 indique pour S1b (`ouie`, `ouie_commune`, `ouie_temoins`, `appels_restes`, `demander_cause`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 374 (position crue,
`esprits.py`/`planification.py`), 375 (rouges de la suite), 380 (U-M social comptes, web), 381 (A2 passage,
`operations.py`/`comprehension.py`) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1b-sons-examens`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-382-s1b-sons-examens.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1b-382\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
