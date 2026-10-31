# Tâche Codex 420 : S1n, les suivis relationnels ont une preuve stable et une seule projection de décision

Quatorzième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1n, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md)), après S1a (378), S1b (382), S1c (383), S1d (384), S1e (385), S1f (397), S1g (400), S1h (404), S1i (405), S1j (406, 408), S1k (409, 411), S1l (413) et S1m (418), fusionnés (porte
`donjon/memoire.py`, inventaire AST `tests/fixtures/acces_memoire_s1a.json`). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception S0 (§ 2 à 7) et les rapports 378, 413 et 418, et le rapport 372 (soupçon déduit), dont tu reprends la méthode.

## Invariant (un seul)
**Les suivis relationnels (épreuves reçues, ancrages, compagnie partagée, soupçons déduits du 372, liens et bandes) ont une preuve stable lue et écrite seulement par des vues et opérations nommées de `donjon/memoire.py` (ou de l'interface de croyances du 397), et une seule projection vers les décisions ; `relations.py` reste la seule autorité sur les axes.** Mêmes axes, mêmes ancrages, mêmes effets complémentaires, hystérésis et estompement conservés ; stockage historique inchangé ; aucun changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST décroît.

## Vérification
Les fichiers que S0 indique pour S1n (`relations_graduees`, `agendas_evenement`, `constater_soupcon`, `soupcon_deduit`) et ceux
des écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine, auberge et crue, identiques à
la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 402 (vérification d'intégration, calcul seul), 416 (A6, `mj.py`), 419 (vérification de contact, `deliberation.py`/`planification.py`) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1n-suivis-relationnels`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-420-s1n-suivis-relationnels.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1n-420\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
