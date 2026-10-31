# Tâche Codex 397 : S1f, une seule interface pour la localisation crue et les preuves de possession

Sixième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1f, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384) et S1e (385), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378 et 385, et le rapport 374 (position crue comme hypothèse datée, fusionné), dont tu reprends la méthode.

## Invariant (un seul)
**Les valeurs de localisation crue (lieu d'autrui, hypothèse datée du 374 avec mobilité, confiance initiale et consommation) et les preuves de possession se lisent et s'écrivent par une seule interface de `donjon/memoire.py` (ou d'un module de croyances qu'elle désigne) ; plus aucun accès direct à ces champs de `croyances` hors de l'interface.** Aucune perte du statut daté, de la confiance ni de la consommation ; aucun droit recomposé ; stockage historique inchangé (clés, ordre, sérialisation). Aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST de ces accès décroît. S0 prévient que S1f à S1i touchent des centaines d'accès : si le diff dépasse le créneau, livre une partie cohérente (par exemple localisation d'abord, possession ensuite) et dis ce qui reste.

## Vérification
Les fichiers que S0 indique pour S1f (`contact_position_inconnue`, `contact_sous_but`, `garde_ouidire`, `agendas_transferts`, `position_hypothese`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 381 (A2 passage), 392 (scènes connues), 395 (avis redits crue), 396 (U-T social comptes) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1f-localisation`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-397-s1f-localisation.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1f-397\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
