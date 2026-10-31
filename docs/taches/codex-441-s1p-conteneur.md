# Tâche Codex 441 : S1p, nouveau conteneur versionné de la mémoire

Seizième et dernier lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5, ligne S1p, et son
[annexe d'accès](../conception-memoire-unifiee-annexe-acces.md) ; [conception S2](../conception-s2.md), tableau des
champs, ligne S1p). S1a à S1o (lots 378 à 435) sont fusionnés : toutes les familles de la mémoire subjective passent
par la porte `donjon/memoire.py` (inventaire AST `tests/fixtures/acces_memoire_s1a.json`, 106 expressions après S1o).
Lis `AGENTS.md`, `docs/etat-dev.md` (court), la conception S0 (§ 2 à 7, en particulier les trois couches, le registre,
les index, la version et la migration), les décisions S0 Q1 et Q2 (`docs/etat-dev.md`, « Questions de S0 » : rétention
selon importance et âge ; héritage minimal, aucun passé reconstruit), et les rapports 378, 420 et 435.

## Invariant (un seul)
**La mémoire subjective de chaque esprit est rangée dans un conteneur versionné (trois couches, registre et index
reconstruits), atteint seulement par `donjon/memoire.py` ; une sauvegarde de l'ancien format se charge par une migration
réversible et déterministe, puis se sauvegarde et se recharge sans perte ni changement de l'état historique ; aucun
lecteur nouveau du dossier, aucun stock brut renvoyé par les vues.** Aucun changement de choix, de parole, de délai, de
tirage ni de classement. Les captures réelles de `tests/data` relues à l'identique (décision S0 Q2). L'inventaire AST
final ne garde que les expressions gelées justifiées (archives mécaniques, formats publics).

Si le conteneur complet ne tient pas en un lot de 30 à 45 minutes, découpe-le : livre la première tranche (version,
migration aller-retour et une couche), décris les suivantes dans le rapport, et dis la limite.

## Vérification
`test_memoire_socle` et les fichiers des familles S1a à S1o ; aller-retour complet de sauvegarde (ancien format →
conteneur → sauvegarde → recharge → ancien format reconstitué identique) sur toutes les captures de `tests/data` ; état,
rendu, scène et paroles après recharge, même laps entier/découpé. **Empreintes 2 h, quatre graines, Relais, mine,
auberge et crue, identiques à la base exacte** (`tools/comparer_bancs.py --empreintes`, cache). Pas de suite complète,
ni Luna.

## Contraintes
**Poste : le PC fixe.** **Ne pousse pas vers origin** et n'utilise pas l'API GitHub ou le connecteur GitHub : le PC fixe
n'a plus d'identifiants Git en ce moment ; commite dans ta branche locale et donne le commit final dans ton dernier
message, le superviseur la récupère par SSH. Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours : 431
(admission préalable, `mj.py`, `portee_narrative.py`), 437 (`planification.py`), 438 (`agendas.py`, `deliberation.py`),
439 (diagnostic), 440 (rouges connus) : touche le moins possible leurs fonctions, signale tout recouvrement. Deux
processus au plus, priorité réduite, calculs longs détachés.

## Livraison
- Branche `codex-s1p-conteneur`, base `integration` (locale ; voir contraintes).
- Rapport d'une page `docs/taches/rapport-codex-441-s1p-conteneur.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1p-441\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
