# Tâche Codex 400 : S1g, les états matériels et capacités crus par leurs seules vues

Septième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1g, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384), S1e (385) et S1f (397), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 385 et 397, dont tu reprends la méthode.

## Invariant (un seul)
**Les états matériels crus (ouvert, verrouillé, allumé, éteint, charge, fin d'un bien, réservé) et les capacités crues se lisent et s'écrivent seulement par leurs vues de `donjon/memoire.py` (ou de l'interface de croyances du 397) ; plus aucun accès direct à ces champs de `croyances` hors de l'interface, et la vue distingue absence de croyance, fin négative et valeur inconnue.** Stockage historique inchangé (clés, ordre, sérialisation) ; aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST de ces accès décroît. Si le diff dépasse le créneau, livre une partie cohérente (par exemple états des contenants et sources, puis capacités) et dis ce qui reste.

## Vérification
Les fichiers que S0 indique pour S1g (`planification`, `lumiere`, `constater_rumeurs`, `agendas_fins`, `service_non_defait`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 381 (A2 passage), 399 (rembourser depuis le menu et le terminal) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1g-etats-materiels`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-400-s1g-etats-materiels.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1g-400\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
