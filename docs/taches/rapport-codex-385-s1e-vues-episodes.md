# Lot 385 — S1e, vues pures des épisodes

30 octobre 2026 · `codex-s1e-vues-episodes` · base exacte `integration b2028ede`.
Code corrigé `a50a3648`, mesuré dans `dba080d1` après fusion documentaire
d'`origin/integration fcb82692` ; aucun changement moteur dans ces fusions.

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

**Résultats de la première passe et corrections.** Les 22 fichiers ont exécuté
325 tests : 78 erreurs avaient une cause commune, le dictionnaire local
`episodes` de `signes.percevoir_tous` masquait la vue importée. L'import est
maintenant nommé `episodes_retenus`. L'assertion du détecteur de services
simulait encore `lire` : son mock porte désormais sur la vue `episodes`.
L'autre échec, `passage.test_cas_reel_acceptee_elle_s_ecarte_vraiment`, se
reproduit à l'identique sur la base exacte isolée : attente d'une ancienne
formulation (« Tu avances d'un pas. »), état/recharge parcourus avant ce texte.
Cette limite héritée est attribuée, sans modifier le comportement du passage.

La campagne d'empreintes initiale s'est arrêtée **avant de jouer une nuit** :
l'observateur courant importait la vue depuis l'ancienne référence qui ne
l'expose pas. Le récit importe maintenant sa vue à l'usage ; le détecteur charge
la porte livrée avec l'observateur, dont les imports relatifs lisent le moteur
comparé, comme le fait déjà l'audit pour son rendu. Aucun accès brut ajouté.
Une contre-épreuve simule une référence sans cette API. Les sept tests ciblés
(AST, compatibilité et service) passent ; comparaison réelle de 1,2 minute au
Relais : chronique, mesures et état final complet identiques à `b2028ede`.

**Calcul corrigé détaché en cours.** 17 fichiers en échec ou concernés par les
corrections, puis empreintes **2 h × quatre graines × Relais/mine/auberge/crue**
contre `b2028ede`, cache partagé. Les autres fichiers déjà verts ne sont pas
relancés. Deux processus au plus, priorité réduite, référence puis branche ;
aucune suite complète ni Luna, aucune comparaison de coût. Reprendre à
`fin-corrige.json`, lire les résultats puis clore le lot. Les empreintes longues
ne sont pas encore déclarées acquises.

**Bruts et recouvrements.** `C:/Users/msics/donjon/artifacts/s1e-385/` :
`tests-initiaux.log`, `tests.json`, `tests.log`, `fin-tests.json`,
`empreintes-base.log`, `fin.json` (première passe),
`attribution-passage-base.log`, `compatibilite-courte.json` et son journal ;
`tests-corriges.json/log`, `empreintes-base-corrigees.json/log`,
`run-corrige.ps1` et `fin-corrige.json` écrit en dernier pour la nouvelle passe. Recouvrement potentiel 374 : lectures seules de `deliberation`,
`echanges.affirmer`, migration d'`esprits` et audition/services de `pnj` ;
aucune localisation ni recherche modifiée. Aucun fichier propre à 380/381 touché.
Rétention selon âge/importance et nouveau stockage restent hors lot.
