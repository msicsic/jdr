# Tâche Codex 435 : S1o, aides, rendez-vous et connaissances de contrat sont des vues référencées

Quinzième lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1o, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md) ; [conception S2](../conception-s2.md), tableau des
champs, ligne S1o), après S1a à S1n (lots 378 à 420), fusionnés (porte `donjon/memoire.py`, inventaire AST
`tests/fixtures/acces_memoire_s1a.json`). Le lot 419 (vérification de contact, qui touchait `gardien_detresse` et les
familles aide/appel) est fusionné ; pars de l'intégration qui le contient. Lis `AGENTS.md`, `docs/etat-dev.md` (court),
la conception S0 (§ 2 à 7), les rapports 378, 418 et 420, et le rapport 419 pour l'état actuel des aides et du contact.

## Invariant (un seul)
**Les aides attendues, les rendez-vous (`rejoint`, `rejoindre`), les mandats perçus et les connaissances qu'un PNJ a
des contrats (engagements, promesses du joueur, référence temporelle, séquence et issues d'obligations, accord initial,
et ce qu'il sait des dettes, permissions, services rendus et restitutions) sont lus et écrits seulement par des vues et
opérations nommées de `donjon/memoire.py`, qui référencent l'archive d'`agendas` sans la copier ni en déplacer
l'autorité ; une issue réelle distante n'y devient pas une issue connue.** Stockage historique inchangé ; aucun
changement de choix, de parole, de délai, de tirage ni de classement. L'inventaire AST décroît.

## Vérification
Les fichiers que S0 indique pour S1o (`gardien_detresse` et les familles aide, appel, mandat, date) et ceux des
écrivains touchés, plus `test_memoire_socle` ; cas historique réel et autre cas, état complet, rendu, scène et paroles
après recharge, même laps entier/découpé ; clôture mécanique distante sans connaissance automatique. Le rouge connu de
`test_gardien_detresse.test_demander_un_moyen_pour_un_autre_besoin` (oracle sans `suite_conditionnelle`, rouge sur
l'intégration avant ce lot) n'est pas à masquer : dis s'il reste identique. **Empreintes 2 h, quatre graines, Relais,
mine, auberge et crue, identiques à la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite
complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 402 (vérification
d'intégration, calcul seul), 431 (admission préalable, `portee_narrative.py`, `mj.py`), 434 (K2, `echanges.py`,
`dialogues.py`, `compilation.py`) : touche le moins possible leurs fonctions, signale tout recouvrement ; à la fin,
fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au plus, priorité réduite, calculs longs
détachés.

## Livraison
- Branche `codex-s1o-aides-contrats`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-435-s1o-aides-contrats.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1o-435\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
