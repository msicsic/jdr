# Tâche Codex 19 : passer sous un obstacle, ou par-dessus

Branche `codex-sous-obstacle` (elle porte ce fichier, issue de `main` 276524c), worktree dans `tmp-worktrees/`.
Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `temps-fin-marche`, `diagonales`, `laisser-passer`,
`fabrication-generale`, `repli-et-appel`, `mj-restes`, `relances-luna`), `docs/reverification.md` (N5),
`docs/mecaniques.md` (« Franchissement improvisé avec un appui mobile », le pas, le pas feutré, les obstacles),
`docs/plan-temps.md` (« Correctif : la marche »), `donjon/matiere.py`, `donjon/franchissement.py`,
`donjon/artisanat.py` (`preparer_usage`), `donjon/operations.py`, `spatial.trajet`.

**Pas de Luna sur ce poste.** Fais tout le moteur et les tests ; écris à la fin du rapport une section
« Vérification Luna à faire » (scènes préparées dans `tests/data/bancs`, saisies exactes, ce que le joueur doit
lire), que je ferai depuis l'autre poste à la fusion.

## Le constat
Au Relais, « est-ce que je pourrais passer sous la poutre effondrée ? » répond « Il faut une échelle accessible
et en état de servir. » (2 passes sur 2, revérification N5). La poutre (`poutre_conduite`, échoppe) est un
`meuble` qui `bloque_passage` et `bloque_vue` sa case, sans aucune dimension verticale ; seule l'échelle
(`franchir`, `preparer_usage`) et le saut à la perche (`franchir_obstacle`) savent franchir. Le moteur ne peut
donc ni accepter ni refuser avec sa vraie raison un passage dessous, par-dessus ou en se glissant à côté : Luna
tombe sur le seul refus qui existe.

## L'invariant
Un obstacle physique se franchit selon sa forme, par une règle commune au joueur et aux PNJ, sans cas propre à
un objet, un lieu ou un scénario :
- **Ce qu'on sait de sa forme** : un obstacle qui bloque le passage peut porter une description physique
  (`matiere.py` : dimensions, et ce qui compte ici, le dégagement dessous et la hauteur au-dessus du sol),
  déclarée par le scénario ou établie par le MJ (`etablir_faits`, qualification, vérifiée par le moteur comme
  les autres descriptions). Sans description, le moteur ne suppose rien : il dit ce qui manque (`attendu`),
  jamais « il faut une échelle ».
- **Les manières de passer** : dessous (en rampant, si le dégagement suffit à la carrure de qui passe), par-dessus
  (en l'enjambant ou en l'escaladant, selon sa hauteur et la stature), chacune avec sa durée (sur les durées du
  pas, comme le pas feutré), son bruit (ouïe commune), son effort (corps au temps vécu), ce qu'on ne peut pas
  emporter (longueur, masse portée), et un jet seulement si la manière en demande un (DEX ou FOR, difficulté
  fixée par la règle, pas par Luna, ou arbitrage mémorisé comme le saut). L'échelle et le saut à la perche
  restent ce qu'ils sont ; décide s'ils deviennent des manières de la même règle ou restent à côté, et dis
  pourquoi.
- **Joueur** : une action typée commune (nouvelle ou extension d'une existante : choisis et justifie), avec
  fiche avant tentative, `attendu` en identifiants (champ fautif, valeur reçue, ce qui serait accepté), une cause
  par refus ; « est-ce que je pourrais… ? » passe par la faisabilité (`commandes.faisabilite` : la fiche sans
  rien exécuter) ; une commande locale si une formulation simple le permet (« ramper sous la poutre »), comme
  « monter » et « descendre ».
- **PNJ** : le trajet (`spatial.trajet`, `pnj.chemin`, le chemin par salles) connaît ce passage avec son coût en
  temps ; le planificateur ne le prend que s'il le croit possible (forme crue de l'obstacle) ; ce qu'il porte et
  sa carrure le limitent comme le joueur. Toute lecture nouvelle de la recherche entre dans `_entrees`
  (`VERIFIER`), et une lecture de lumière passe par la découverte de lumière (graphes `sombre`/`lumiere`).
- **Vue** : un obstacle qui bloque la vue la bloque toujours ; passer dessous n'y change rien.

## Données
Étape 1, aucune donnée de scénario changée : prouve que les nuits restent identiques
(`tools/comparer_bancs.py --empreintes`, 2 h puis 8 h, quatre scénarios × 4 graines, contre 276524c).
Étape 2, décris la forme des obstacles des scénarios où c'est plausible (la poutre effondrée de l'échoppe, et
les autres obstacles qui bloquent un passage dans les quatre scénarios ; liste-les), en restant fidèle à leur
nom et à leur texte ; mesure alors l'effet (banc 8 h, 4 graines : trajets, minutes, usurpations, boucles avec
`tools/audit_nuits.py analyser`) et explique chaque écart.

## Vérifications
- Tests après rechargement (`tests/test_sous_obstacle.py`) : le cas réel (la poutre du Relais : la question de
  faisabilité donne la fiche, « tenter » fait passer, ce que lit le joueur, l'état après rechargement) et au
  moins un autre obstacle de même nature dans un autre scénario ; dessous trop bas (refus avec sa raison) ;
  par-dessus trop haut ; un objet porté trop long ; un PNJ qui passe dessous dans son trajet, même laps d'un bloc
  ou découpé ; un PNJ qui ne le croit pas possible ne le planifie pas ; un obstacle sans description (refus qui
  dit ce qui manque).
- Suite complète verte (`tools/tests.py --processus 3`).
- `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, chaque scénario et
  `rixe`, sans écart.
- Docs : `docs/mecaniques.md` (la règle, pour le joueur), `docs/plan-temps.md` ou le plan qui convient (le
  trajet), `docs/etat-dev.md` (« Branche `codex-sous-obstacle`, non fusionnée », compte de tests).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-19-sous-obstacle.md` : règle, fonctions, cas vérifiés, données décrites, mesures
avant → après, limites, et la section « Vérification Luna à faire ». D'autres branches sont en cours (relations
3c et part estimée en fusion, force 4c, lisibilité des noms) : garde les changements localisés, ne touche pas
au code des noms.
