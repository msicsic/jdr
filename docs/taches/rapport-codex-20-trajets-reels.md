# Rapport Codex 20 — trajets réels

Branche `codex-trajets-reels`, non fusionnée, base **aff9626**. Commits signés,
signatures vérifiées. Aucun appel à Luna.

## Changement

Le coût prévoit la marche et les gestes sur le monde cru, depuis la case réelle
puis projetée. `obstacles.cout_route` est la conversion
unique en minutes : pas, diagonales, allure, rotations et portes. `Vue.allers`,
`trajet`, `_chercher`, l'attente d'une part, la tâche, l'enquête, `part_estimee`,
`pnj.parcours` / `chemin` et la fuite le partagent. Les gestes lisent `pnj.DUREES` ;
les portes du joueur gardent leur durée existante d'une minute. La pression se paie
par salle, pendant le trajet et avant les effets du geste, dont l'allumage.

`Etat` distingue case, orientation, allure, portes et objets posés ; les mémoires,
graphes de lumière et certificats suivent ces états.
Les distances locales sont mémorisées (LRU de 2 048 tables) par géométrie, obstacles
crus, origine, allure et équipement utile aux franchissements ; les routes globales
ajoutent les portes et clés prévues. Les reprises sont contrôlées par `VERIFIER` et
`spatial.VERIFICATION`. Aucun cas de scénario ajouté.

## Vérification et mesures

- Suite complète : **1 585 tests, quatre ignorés, aucun échec**, trois processus à
  priorité réduite. Le neuvième test de trajets passe séparément : **1 586 tests
  couverts** ; aucune nouvelle suite relancée.
- Neuf tests : deux flammes (Relais et mine), approches, portes, noir, obstacles
  crus/ignorés, allure, clé posée, fuite et temps découpé ; exécution, état, rendu et
  rechargement. Allumer au Relais : **11,5 s près / 21,4 s loin**, contre
  une minute dans les deux cas auparavant ; pression **0,575 / 1,07**, puis zéro.
  Fuite du joueur par une porte fermée : fiche et exécution **61,5 s**.
- Contrôles 2 h, graine 42, quatre scénarios et `rixe` : aucune erreur ni borne.
  Les empreintes jusqu'à 2 h sont conservées sur quatre graines des quatre scénarios,
  sans relancer la référence, rangée dans `artifacts/references/aff9626*/`.

## Limites et intégration

La règle « Rythme des lots » de **main 42bb9c0** est appliquée : campagne CPU 8 h
arrêtée, aucun calcul restant ni banc long relancé. Les bruts déjà produits restent
dans `artifacts/`. Deux réserves : **Bram, mine 42, 463 min**, manque un
plan à la borne de 4 000 états ; **Relais 1985**, nouvelle rafale de **197 passages
par PNJ dans une heure**, et courts allers-retours faim/abri dans la crue 2024.
L'absence de boucle nouvelle n'est **pas acquise**. Le temps physique correct
ne résout ni les interruptions par d'autres besoins ni la sécurité durable d'une
fuite. Les positions inconnues, délais des tiers et séjours durables restent estimés.
Le coût CPU complet et ces défauts de délibération sont à vérifier à l'intégration.

Préférences, fautes et pièces inchangées : demander à chance 0,5 pèse encore six
minutes face à quelques secondes de marche. À mesurer séparément : `DEMANDE` 0,25–0,5,
`CHERCHER` 0,5, `TACHE` 0,5 puis devis des gestes ; conserver d'abord les taux
physiques et `SALAIRE`. Aucun de ces réglages n'est appliqué dans ce lot.
