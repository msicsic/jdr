# Tâche Codex 20 : le planificateur compte le vrai temps de marche et des gestes

Branche `codex-trajets-reels` (elle porte ce fichier, issue de `main` aff9626, avec force 4c et « passer sous un obstacle » fusionnés), worktree dans `tmp-worktrees/`.
Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `planificateur`, `temps-fin`, `temps-fin-marche`,
`diagonales`, `besoins`, `planif-cout`, `cout-calcul`, `codex-cout-suite`, `codex-lampes-suite`,
`codex-part-estimee`, `codex-force-4c`, `codex-sous-obstacle`, et « À revoir »), `docs/plan-planificateur.md` en entier, `docs/plan-temps.md` (« la marche », « les
diagonales »), puis `donjon/planification.py` (`Vue`, `allers`, `route`, `trajet`, `attente_part`, `pression`,
`_gestes`, `_suites`, `_explorer_etats`, `_entrees`, `_GRAPHES`, `_sans_plan`), `donjon/part_estimee.py`,
`donjon/temps.py`, `donjon/obstacles.py` (`cout_route`, `Parcours`, `transitions`, `metrique_necessaire`),
`donjon/defense.py` (`chemin_fuite`), `pnj.parcours`, `pnj.chemin`, `pnj._marcher`, `spatial.trajet`.

## Le constat (reliquat d'avant le temps fin)
Le planificateur et le temps fin sont nés en parallèle et ont été intégrés le même jour : le planificateur a
gardé le modèle d'avant, une salle à la fois. Le geste « aller » coûte le **nombre de passages entre salles**
(`Vue.allers` : `len(route)`) ; `Vue.trajet` (attente d'une part, chemin d'une tâche payée, `planification`
~2021), le devis de N (`part_estimee` : `len(route) * (1 + pression)`) et d'autres lectures reprennent la même
mesure. Dans une salle, la distance ne compte pas : prendre un objet à l'autre bout d'une grande salle coûte
autant que celui qu'on a sous la main ; les gestes ont un coût forfaitaire. La pression (noir, eau, biens,
présences craintes) se compte par « minute » de ce temps faux. L'exécution, elle, est juste : le PNJ marche case
par case au dixième de seconde (`temps.duree_pas`, diagonales √2). Conséquences : entre deux flammes à une salle,
il ne préfère pas la plus proche ; un grand détour par une porte paraît moins cher qu'un court passage par deux ;
la peur du noir pèse autant pour deux cases que pour vingt.

## L'invariant
Le coût de temps d'un plan est le temps qu'il croit que prendra son exécution, par les mêmes règles que
l'exécution, sur ce qu'il croit du monde :
- **Marche** : le temps de marche estimé de sa position (réelle au départ, puis celle où le plan le laisse : le
  seuil par lequel il entre, ou la case du geste) jusqu'à la case où se fait le geste suivant, sur la géométrie
  des salles et les obstacles **crus** (pas ceux qu'il ignore), avec la durée de pas du jeu (`temps.duree_pas`,
  diagonales, allure du plan) ; les portes au temps de leur geste. Une seule fonction de coût de trajet, employée
  par `allers`, `trajet`, `attente_part`, `_chercher`, le devis de N (`part_estimee.aller`) et toute lecture qui
  en dépend (recense-les toutes ; aucune ne garde la minute par salle). Elle existe déjà sous une forme
  abstraite : `obstacles.cout_route` (une minute par salle plus le supplément réel d'un passage dessous ou
  dessus, lot O) ; c'est elle qui devient le vrai temps, sans seconde fonction de route. Reprends ce que O a
  posé : les routes mesurées de `obstacles.Parcours` (`duree_trajet`, `surcout_passages`), la preuve de
  domination (`metrique_necessaire` et sa mémoire, contrôlée par `spatial.VERIFICATION`), la case de départ
  dans `_entrees`, la clé des routes par équipement, les arêtes de `_marcher` selon l'allure. La force 4c
  compare fuite et riposte par des trajets (`defense`, gestes de défense du planificateur) et la fuite du
  joueur (`defense.chemin_fuite`) passe par `obstacles.transitions` : même fonction pour elles.
- **Gestes** : leur durée réelle (celle que le moteur leur donne à l'exécution), plus l'approche jusqu'à l'objet.
- **Pression** : comptée au prorata de ces durées, salle par salle là où il passe.
- **Unité** : le coût reste exprimé en minutes (fractionnaires) pour rester comparable aux prix des fautes, de
  `RESTER`, `TACHE`, de la chance d'une demande et de la valeur d'une pièce. Ces constantes ont été réglées avec
  « une minute par passage » : si le changement d'échelle rend une constante absurde, **ne la retouche pas en
  silence** ; mesure, explique, et propose le réglage dans le rapport (règle commune, jamais par scénario).
- **Coût de calcul** : distances seuil à seuil (et seuil à case d'objet) calculées une fois par salle et gardées
  sous la clé de ce qu'elles lisent (géométrie, obstacles crus, portes) ; dans `_entrees` tout ce que la recherche
  lit de nouveau ; `VERIFIER` et `spatial.VERIFICATION` contrôlent les reprises, les deux graphes
  `sombre`/`lumiere` et le certificat `_sans_plan` (attention : les arêtes des graphes repris gardent leurs termes
  de coût ; une durée qui dépend de la position d'arrivée change la forme de l'état).

## Vérifications
- Tests après rechargement (`tests/test_trajets_reels.py`) : entre deux flammes connues, il va à la plus proche
  en temps (cas réel du Relais ou de la mine, et un autre de même nature) ; un court passage par deux portes
  préféré à un long détour par une seule ; un objet loin dans une grande salle coûte plus que l'objet proche ; la
  peur du noir pèse selon la durée réelle dans le noir ; un obstacle cru allonge le trajet, un obstacle qu'il ne
  croit pas là ne compte pas ; même laps d'un bloc ou découpé.
- Suite complète verte (`tools/tests.py --processus 4`).
- `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, chaque scénario et
  `rixe`, sans écart.
- Les nuits changent, c'est voulu : banc 8 h, quatre scénarios × 4 graines (`tools/comparer_bancs.py --reference
  aff9626`) et audit 12 h, 4 graines (`tools/audit_nuits.py`) : minutes dans le noir, dans l'eau, sans recours, en
  attente, échanges, vols vus, passages par heure et bascules (aucune boucle nouvelle), usurpations et violations
  (aucune) ; chaque écart notable expliqué par une nuit lue. Temps au processeur et nœuds, `main` et la branche
  lancés ensemble.
- Docs : `docs/plan-planificateur.md` (section nouvelle : le coût du temps, sa fonction, l'échelle des
  constantes, limites), `docs/etat-dev.md` (« Branche `codex-trajets-reels`, non fusionnée », compte de tests).

## Luna
Ce lot ne change ni le MJ ni les consignes : pas de vérification Luna demandée.

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-20-trajets-reels.md` : la règle, la fonction unique et ses lecteurs, le cache et ses
clés, cas vérifiés, mesures avant → après, constantes dont l'échelle pose question et réglages proposés, limites.
Garde les changements localisés et la fonction de coût de trajet unique ; la calibration des signes (3c) pourra
tourner en parallèle sur un autre poste (`signes`, `relations`).
