# Lot 385 — S1e, vues pures des épisodes

30 octobre 2026 · `codex-s1e-vues-episodes` · base exacte `integration b2028ede`.
Code `cad2e15e`, mesuré après fusion documentaire d'`origin/integration 51c3d37d`
dans `8b5cabfc` ; aucun changement moteur apporté par cette fusion.

**Invariant et code.** Tous les lecteurs restants du tampon d'épisodes passent
par `memoire.episodes`, vue pure qui renvoie des copies profondes, dans l'ordre
historique, sans créer d'esprit. Le filtre de types conserve les doublons et
ne trie jamais les dates. La fenêtre des trois derniers souvenirs porte sur
le tampon entier avant tout filtre. Les règles métier restent chez leurs lecteurs.
Les quatre dernières paroles admissibles gardent leur ordre et leurs contrôles
de connaissance ; dernier son et rejeu utilisent déjà la porte sonore de S1b.

Jeu, paroles, récit du banc, export des souvenirs et outils de diagnostic sont
portés. Les lectures d'audit utilisent les mêmes vues ; leurs archives exportées
et métriques historiques conservent leur format. La migration des présences
sort du lecteur `esprits.installer` : retrait par identité et copies des résultats
dans la porte. `rafraichir_geste_entendu` reprend l'écriture auparavant cachée
dans `pnj._temoins_a_l_oreille` : dernière occurrence correspondante, borne
inclusive, même identité, ni nouvel épisode ni crochet. La branche joueur de
`defense.souvenirs` garde le registre distinct `violences_joueur`, hors épisodes.
Liste, plafond 40, clés et sérialisation sont inchangés ; aucun registre ajouté.

**Contrôle AST.** L'inventaire passe de 69 à **zéro lecture hors exceptions**.
Les 23 expressions restantes sont nommées : cinq validations de schéma dans
`esprits.verifier`, dix-huit homonymes du cache de recherche. Les créations vides
historiques et la fixture d'outil restent gelées à l'expression exacte.
Les mutations de champs sont désormais contrôlées pour toute famille d'épisodes,
avec alias, champ imbriqué, méthode détachée, sélection par indice ou `next`.
Les retours bruts et copies superficielles de liste sont également éprouvés.
Ce contrôle syntaxique ne prouve pas tous les flux interprocéduraux de Python.

**Vérification.** Première passe : **9/9 verts** (16,1 s), contrôle AST et quatre
nouveaux tests : copies imbriquées/pureté/ordre/fenêtre, ordre des paroles
admissibles, rafraîchissement du geste entendu, chaînes réelles mine et auberge.
Odon au coffre de la paie entendu par Bram, puis Lucien au coffre ferré entendu
par Anselme : même laps entier ou découpé avec recharges, état complet et ordre
JSON, rendu, scène, paroles émises et retenues ; récit observateur sans mutation.
La restriction Windows sur les sauvegardes temporaires a nécessité l'exécution
autorisée hors restriction, comme dans les lots précédents.

**Calcul détaché en cours.** 22 fichiers ciblés, deux processus au plus et
priorité réduite, puis empreintes **2 h × quatre graines × Relais/mine/auberge/crue**
contre la base exacte `b2028ede`, avec cache partagé. Référence puis branche,
sans comparaison de coût ; aucune suite complète ni Luna.
Les résultats ne sont pas encore déclarés acquis. Reprendre à `fin.json`,
attribuer tout échec puis clore le rapport et l'entrée d'état.

**Bruts et recouvrements.** `C:/Users/msics/donjon/artifacts/s1e-385/` :
`tests-initiaux.log`, `tests.json`, `tests.log`, `fin-tests.json`,
`empreintes-base.json`, `empreintes-base.log`, `run.ps1` et `fin.json` écrit
en dernier. Recouvrement potentiel 374 : lectures seules de `deliberation`,
`echanges.affirmer`, migration d'`esprits` et audition/services de `pnj` ;
aucune localisation ni recherche modifiée. Aucun fichier propre à 380/381 touché.
Rétention selon âge/importance et nouveau stockage restent hors lot.
