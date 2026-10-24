# Lot 44 — Portée commune des gestes

24 octobre 2026. Branche `codex-geste-hors-portee`, **non fusionnée**, base `cd7195d`,
brief `39db38e`. Correctif **b758341**, signature SSH vérifiée. `main`, scénarios et fichiers
réservés au lot 43 inchangés.

## Cause et invariant

Les quatre fils historiques du Relais ont été relus, contexte et réponses compris.
Hors de vue, la poutre figure dans les souvenirs mais pas dans le dossier des obstacles :
les règles de `passer_obstacle` disparaissent. Le refus de `franchir` suggère alors
`improviser` ; Luna choisit `adresse`, qui échappe au contrôle de contact. La contre-revue
admet ce passage sans effet déplaçant Corvus. Avec une autre approche : « Approche-toi… ».

**La manière d'un geste n'accorde aucune portée physique.** `improvisation.preparer`
contrôle toutes ses cibles par `proximite.exiger`, comme `obstacles.compiler`, avec
`HorsDePortee` et `attendu`. `obstacles.dossier` suit `Monde.designable` et la préparation
ordinaire du moteur, rotation simulée comprise, sans mutation. `consignes` expose l'opération
même sans dossier ; le refus de type d'`artisanat.preparer_usage` l'indique ; la contre-revue
exige l'effet du déplacement demandé. Contrat documenté.

**Issue retenue : refus cohérent, sans rapprochement automatique.** `_a_toucher` et
`_approcher` appartiennent aux PNJ. Le joueur se rapproche par ses pas, puis obtient la
fiche du passage ; aucune fiche abstraite ni tentative n'est créée à distance.

## Vérifications

- Trois nouveaux tests console/MJ simulé/recharge : poutre et table de l'auberge,
  cinq approches, contexte historique exact, refus sans jet/temps/geste, puis pas,
  fiche, ramper et état rechargé. Ciblés : 38 tests historiques verts et trois nouveaux verts.
- Suite complète unique, trois processus à priorité réduite : 1 692 décomptés en 1 833,6 s,
  dont deux erreurs de workers interrompus comptées pour un test chacune. Bilan après reprises :
  **164 fichiers validés, 1 723 tests couverts, 16 ignorés**, sans seconde suite complète. Une ancienne
  attente de fiche à distance corrigée ; ses **19 tests rejoués seuls, verts**. Deux erreurs
  web `WinError 10013` du bac à sable : **huit tests rejoués hors restriction, verts**, sans modification.
  Deux workers TUI bloqués sans calcul dans le bac à sable ont été arrêtés seuls ;
  leurs **33 tests rejoués hors restriction sont verts** (186,2 s), sans modification.
- Banc rapide Relais/auberge, **4 h × quatre graines**, contre `cd7195d` : chroniques,
  mesures, récits, souvenirs et empreintes identiques ; aucun plantage, violation ou usurpation,
  constats d'audit inchangés. Huit références manquantes calculées une fois et cachées.
- Luna `gpt-6-luna`, copies, **une passe**, neuf scripts : **71 appels / 29 tours MJ**,
  aucun repli, obstacle narratif, défaut technique ou de recharge. Obstacles : **19 appels /
  10 tours** ; fiches de ramper/enjamber en deux appels, exécution réelle ; forme inconnue
  en un appel, encombré/trop bas/trop haut en deux, sans déplacement ni forme inventée.

| Appels/tour MJ | `main` en cache → lot 44 |
|---|---:|
| Relais | 3,00 → 2,63 (9 → 8 tours) |
| Atelier | 3,91 → 2,82 (11 tours chacun) |
| Ensemble comparable | 3,50 → 2,74 ; 70 → 52 appels |

Référence `main` **42bb9c0**, clé de son outil historique vérifiée : Relais et atelier
disponibles ; sept `sous-obstacle-*` absents du cache, aucun rejeu de référence.

Relais **n° 20**, `passer_obstacle` du premier coup, **un appel** (main : cinq) :
« Approche-toi de la poutre effondrée : il faut être juste à côté pour agir. »
**N° 21**, **quatre appels** (main : trois), `impossible` puis `frapper` :
« La poutre effondrée n’est pas dans ton champ de vision : tu l’as vue à quelques mètres
derrière toi, vers le sud-est. Pour lui donner un coup de pied, il faut t’en approcher ;
d’ici, tu ne peux pas l’atteindre. Tu peux toutefois chercher à la rejoindre par un autre moyen. »
Position, orientation, instant et jets inchangés aux deux tours.

## Limites et traces

Portée des cibles déclarées déterministe ; choix du geste et de ses cibles encore sémantique.
Aucune mécanique d'improvisation à distance ajoutée ; les sons gardent leur propagation.
Une passe et des temps de cache ne mesurent pas la vitesse propre au correctif.
Bruts du worktree : `artifacts/{cause44.txt,analyser44.py,mesures44.json,relecture44.txt,
suite.log,banc-rapide44.json,tui-hors-sandbox44.json}`, `bancs-multi/20261024-190728-42524/`.
Premier lancement sans accès réseau (`190636-23640`) inexploitable, exclu des mesures.
