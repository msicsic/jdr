# Esquisse : une réflexion humaine, imparfaite, pour les PNJ

**À reprendre après l'étape A4 de `docs/plan-agendas.md`** (décision 7 du 2026-10-23), sur la mesure
du coût de calcul et de la plausibilité des nuits. Ce n'est pas un plan : c'est la trace d'une
discussion de conception du 2026-10-23, pour ne pas la perdre. Rien n'est décidé ni implémenté.

## 1. Le constat

Le planificateur (`docs/plan-planificateur.md`) cherche le plan **le moins cher** vers un but : une
recherche de coût uniforme (Dijkstra, sans heuristique), bornée à `NOEUDS` états et `PROFONDEUR`
gestes, sur ce que le PNJ croit. « Meilleur » veut dire meilleur selon ses croyances, ses valeurs,
ses peurs et ses relations, pas selon la vérité ; mais à l'intérieur de ce qu'il croit, il est
optimal. Un humain ne l'est pas : il ne fait pas une recherche exhaustive, il ne pense pas à tout
ce qu'il sait, il refait ce qui a marché.

Deux motifs de changer cela, qui ne pressent pas de la même façon :
- **la plausibilité** : des erreurs humaines, explicables et racontables, rendent un PNJ crédible ;
- **le coût** : les recherches neuves restent l'essentiel du calcul (mine, auberge ; recherches
  bornées de Josse, Rémy, Lucien).

## 2. Trois étages

1. **L'habitude** : refaire ce qui a marché.
2. **La réflexion limitée** : chercher, mais parmi ce qui vient à l'esprit, et se contenter d'un
   plan assez bon.
3. **La recherche complète** : la recherche actuelle, en dernier recours.

## 3. L'habitude (les recettes)

Une **recette** est un automatisme propre à un PNJ, appris de son expérience : pour tel but, dans tel
genre de situation, telle suite de gestes, avec des **rôles** plutôt que des objets (« le bois pour ce
feu », « la clé de ce contenant »), liés au moment de l'exécution. Elle est gardée tant qu'elle
fonctionne. Ce n'est pas un HTN écrit à la main ; ce n'est pas non plus la mémoire exacte des
recherches (`planification._MEMOIRE`, indexée sur toutes les entrées).

Risques relevés :
- **elle retient les gestes, pas les raisons qui la rendaient bonne** ;
- **une boucle d'interruptions sans échec** (le grenier noir de Lucien et le couloir éclairé, déjà vu
  et corrigé par la branche `besoins` parce que la recherche pesait les deux besoins ensemble) ;
- **l'habitude qui dépasse les valeurs** (Brune vole par habitude alors que le prix d'une faute a
  remonté) ;
- **la rigidité** (Gorm va au brasero alors qu'une lampe allumée est à côté) ;
- **une mauvaise généralisation des rôles** ;
- **l'état** : sauvegarde, même laps découpé, mémoire bornée et déterministe.

Parades envisagées :
- une recette ne retient jamais le coût : elle est **réévaluée aux prix du moment**, un calcul
  linéaire et pas une recherche, et elle cède si elle ne bat plus le niveau d'exigence (§ 4) ; un prix
  de faute qui remonte suffit à la faire céder ;
- elle tombe aussi quand le PNJ croit à un **moyen nouveau** du même but, saillant : la même règle que
  les refus retenus (`deliberation.moyens_crus`) ;
- une interruption compte comme un demi-échec ;
- une **exploration occasionnelle** quand rien ne presse, par un tirage indexé sur l'identifiant,
  l'instant et un compteur de l'esprit, jamais sur l'ordre des appels ;
- l'audit des nuits compte les boucles de recettes.

## 4. La réflexion limitée

- **Contentement.** Avec une recherche de coût uniforme, le premier plan trouvé est déjà le moins
  cher : s'arrêter au premier plan satisfaisant ne fait rien gagner tel quel. Il ne coupe vraiment
  qu'avec un but qui se tient en restant (`tenir`, où la recherche continue après le premier état qui
  atteint le but), ou avec un autre ordre de recherche (A* pondéré, heuristique gloutonne). Le niveau
  d'exigence existe déjà : `_endure` (un plan vaut s'il coûte moins que rester), avec une marge selon
  l'enjeu.
- **Saillance : le vrai levier.** Ne voir que ce qui vient à l'esprit : vu récemment, dans sa salle,
  souvent employé, lié au but ; le reste est en mémoire sans venir à l'idée. Une forme existe déjà :
  `emplois` et `Vue.pertinent` (ce qu'il vaut la peine de porter), la découverte de la lumière
  (`emploie_lumiere`, graphes `sombre` et `lumiere`). Aujourd'hui `VERIFIER` exige que ces restrictions
  ne changent pas l'optimum ; ici, elles auraient le droit de le rater. Le critère premier de
  saillance doit être **l'utilité pour le but**, avant la proximité, pour garder les trouvailles
  émergentes du planificateur (Gorm qui demande les planches d'Aubin pour le feu).
- **Budget.** Exprimé en grandeurs du modèle, jamais en nœuds (un budget en nœuds ferait dépendre le
  comportement de l'ordre d'expansion, et ne se raconte pas) : **une profondeur** (combien d'étapes il
  sait enchaîner), selon l'intelligence, rétrécie par la peur, la faim ou la panique ; **un rayon de
  saillance**. Le récit peut alors dire « il n'a pas pensé à la lampe d'Ilse » ou « trop d'étapes pour
  lui ».

## 5. Avec les agendas

Après A4, les erreurs humaines sont de deux sortes : sur **comment** faire (ce qui précède) et sur
**quoi viser** (s'accrocher à un agenda qui ne marche plus, ou en changer trop vite). La seconde
relève de l'hystérésis des agendas (`docs/plan-agendas.md`, § 6.4, ténacité selon la VOL).

Précaution à tenir dès maintenant : le choix du prochain sous-but d'un agenda et le choix d'un
mandataire (étapes A4 et A5) restent des fonctions séparées, appelées à un seul endroit, pour que la
réflexion limitée puisse s'y brancher sans tout reprendre.

## 6. Ce que deviendrait `VERIFIER`

Il se sépare en trois :
- **exactitude de la règle limitée** (assertion) : sur l'ensemble saillant, la recherche trouve bien
  l'optimum de cet ensemble ; mémoire et graphes repris rendent la même chose qu'un recalcul ;
- **déterminisme** (assertion) : le même laps, d'un bloc ou découpé, donne le même monde ;
- **prix de la myopie** (mesure, pas assertion) : l'écart entre le plan joué et celui de la recherche
  complète, noté comme `BORNES` aujourd'hui. C'est la mesure qui dit si les PNJ sont devenus bêtes ou
  seulement humains.

## 7. Mesures et critères envisagés

- plausibilité lue au récit : chaque choix sous-optimal porte sa raison racontable ;
- boucles (audit des nuits) : recettes qui alternent, interruptions répétées ;
- trouvailles émergentes conservées (scènes enregistrées : planches d'Aubin, lumière avant de
  crocheter) ;
- prix de la myopie, par scénario ;
- temps de calcul : le lot « coût de calcul 3 » se réduirait alors à une mesure de référence et aux
  recherches bornées les plus coûteuses.

## 8. Place de A* et des trajets réels

- **Trajets réels** (lot Q) : avant tout le reste. Saillance et contentement comparent des coûts ; des
  trajets comptés en minutes abstraites par salle les faussent.
- **A\*** : avec une heuristique admissible, même plan que Dijkstra en moins d'états ; pondéré, plus
  rapide et sous-optimal de façon bornée. Utile surtout pour l'étage 3 (recherche complète) et les
  recherches qui butent sur la borne. Difficultés : une borne basse avec une pression variable, les
  buts à plusieurs voies, `RESTER`, la compatibilité avec la mémoire, les graphes repris et le
  certificat d'impossibilité.
- **Langage** (revue externe du 2026-10-24) : réduire l'espace (saillance, profondeur bornée) rapporte plus
  qu'une boucle compilée sur une recherche exhaustive. Porter `_explorer_etats` en Rust (bitsets u64/u128) ne
  se conçoit qu'une fois `Etat` et ces règles figés ; voir `docs/etat-dev.md`, « À revoir », volet coût.

## 8 bis. Avis externe (2026-10-24)

Une revue externe recommande la réflexion limitée avant les recettes : filtrer ce que le PNJ remarque
(saillance, selon la PER) et borner la profondeur selon l'INT et la panique est sans état, accélère tout de
suite et donne des oublis crédibles, alors que les recettes sauvegardées compliquent l'invalidation. Cela
rejoint la question 6 ; à trancher avec elle après A4.

## 9. Questions ouvertes, pour l'utilisateur

1. **Accepter des PNJ non optimaux** : recommandé oui ; à confirmer.
2. **Le seuil des habitudes** : la même marge pour tous (celle de `_endure`), ou selon le caractère ?
3. **Les sources des recettes** : l'expérience propre d'abord ; l'observation des autres et le
   savoir-faire du scénario plus tard ?
4. **Le rôle du caractère** : intelligence pour la profondeur, perception pour la saillance, peur et
   faim pour le rétrécissement ?
5. **Quand la recherche complète** : seulement au calme, après deux échecs de la réflexion limitée,
   jamais sous la peur ? Tension entre le désespoir qui pousse à se creuser la tête et la panique qui
   rétrécit l'esprit.
6. **L'ordre interne** : la réflexion limitée avant les recettes (sans état sauvegardé, plus simple à
   vérifier, gain de calcul immédiat, et les recettes ont besoin d'un niveau d'exigence pour céder) ?
