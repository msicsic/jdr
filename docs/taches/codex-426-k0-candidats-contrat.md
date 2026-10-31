# Tâche Codex 426 : K0, candidats de contrat déterministes

Lot K0 de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne K0 ; `docs/conception-valeur-llm.md`, « Pipeline
proposé » et « Lots de valeur à ouvrir après décision »). Ses préalables G12, G13, G17 et U-D sont fusionnés.

Lis `AGENTS.md` (contrat du MJ), `docs/etat-dev.md` (court), les deux documents ci-dessus, et les rapports de G17 et
U-D (cherche-les dans `docs/historique-lots.md`).

## Invariant (un seul)
**Le moteur propose au joueur, sans modèle, des termes de marché publics et admissibles avec un PNJ présent :
un besoin que ce PNJ a exprimé ou accepte de discuter, un bien connu de Corvus qu'il pourrait échanger, une tâche
admissible. Une suggestion n'accepte rien, ne paie rien et n'engage personne. Elle n'expose aucun besoin secret ni
aucune possession inconnue de Corvus.** Elle utilise les termes typés existants (pas de nouvelle clause) ; un choix
du joueur ouvre le formulaire de marché existant prérempli (voie d'E5/U-D), jamais l'accord.

Le générateur est déterministe : mêmes données perçues, même liste dans le même ordre. Il servira de référence pour
mesurer plus tard ce que Luna ajoute (K2). Validation sur copie avant affichage (forme, droits, moyens, ressources,
doublon), comme pour une proposition du joueur. Le verdict reste celui du PNJ, au moment où le joueur propose.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/echanges.py`, `donjon/dialogues.py`, le descripteur U-D, rendu
terminal et web au besoin, tests. Aucun appel à Luna dans le chemin. Lots en cours : 402, 419, 424, 425. Pendant S1,
n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite.

## Vérification
Cas réel : Corvus devant Aubin au Relais (planches, faim ou froid d'Aubin connus) : suggestions affichées, choix d'une
suggestion, formulaire prérempli, puis accord ou refus du PNJ par la voie existante ; état et vue identiques après
recharge. Autre cas : une autre famille (huile à l'auberge, ou une tâche) et un PNJ dont le besoin n'est pas connu de
Corvus (aucune suggestion qui le révèle). Tests voisins verts (marché, U-D, E5). Pas de suite complète, ni Luna.

## Livraison
Branche `codex-k0-candidats-contrat`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
dépôt de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-426-k0-candidats-contrat.md` ;
entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents
graves). Bruts dans `C:\Users\msics\donjon\artifacts\k0-candidats-426\`. Termine par `LOT TERMINÉ`,
`CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
