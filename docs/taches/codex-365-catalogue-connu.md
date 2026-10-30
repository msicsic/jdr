# Tâche Codex 365 : le catalogue des choix ne montre que ce que Corvus connaît

Lot prioritaire, décidé par l'utilisateur le 2026-10-30. Le lot 364 (rapport `docs/taches/rapport-codex-364-e6-libre-vers-formulaire.md`,
section « Alertes du catalogue », bruts `C:\Users\msics\donjon\artifacts\e6-364\`) signale **seize entités affichées dans
les choix**, pour chacun des deux scénarios de ses bancs, alors que sur les copies de départ elles ne sont ni visibles, ni
dans `connus`, ni dans les souvenirs visuels : `paroles._connu_du_joueur` les admet néanmoins. Préexistant (avant E6).

Lis `AGENTS.md` (contrat du MJ : « Le contrôle garantit de façon déterministe l'absence de fuite d'entités non perçues »),
`docs/etat-dev.md` (court), le rapport 364 et, par mot-clé dans `docs/historique-lots.md` (sans le lire en entier), les
lots qui ont fait `_connu_du_joueur`, `personnages_connus`, les noms connus (`codex-noms`, lots 26, 27, 32, 65, 346).

## Invariant (un seul)
**Toute entité proposée au joueur dans un catalogue de choix (menu web, terminal, formulaire, gestes publics, accords) est
connue de Corvus selon la même règle que le reste de la projection publique : perçue, mémorisée par sa vue ou son ouïe,
ou nommée par une source qu'il a entendue ; jamais d'après l'état réel ni d'après un lexique dérivé du monde.**
Diagnostique d'abord : qui sont les seize entités, par quelle voie `_connu_du_joueur` les admet (fondement lexical ?),
si elles atteignent effectivement le joueur ou le MJ (fuite réelle) ou seulement une liste interne. Corrige la règle
commune, sans cas particulier ; si une admission est légitime (nom entendu, savoir de scénario déclaré), garde-la et
documente-la.

## Vérification
Les deux scénarios des bancs du 364 et un autre (Relais, auberge) : catalogue avant/après, aucune entité non connue,
entités connues toujours proposées ; monde, scène et fiche après recharge ; tests des noms, de la projection publique,
des menus U-M/U-T et des accords. Empreintes 2 h, quatre graines, Relais et auberge, si le code du jeu change. Pas de
suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Lot en cours : 360 (PC fixe, régressions du 337) ;
signale tout recouvrement.

## Livraison
- Branche `codex-catalogue-connu`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-365-catalogue-connu.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\catalogue-365\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
