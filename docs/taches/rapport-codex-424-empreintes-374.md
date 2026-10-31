# Lot 424 — empreintes du 374, famille E du 414

31 octobre 2026, **PC fixe** (`MSI-DESKTOP`). Branche `codex-empreintes-374`,
base intégration `a874d646`. **Deux tests adaptés, aucun code du jeu modifié.**
Bruts : `C:/Users/msics/donjon/artifacts/empreintes-374-424/` ;
preuve consolidée : `fin-attribution.json`, détails `a_mange-ecarts.json` et `eclaire-ecarts.json`.

**Invariant.** Chaque écart doit être attribué avant de toucher l'oracle.
Rejeu sur copies de `c3f0c2d5^` (`1fd48fb5`), `c3f0c2d5`, puis de la branche :
le parent restitue exactement les oracles historiques ; le 374 et la branche donnent
les mêmes mondes, plans, coûts, rendus et traces ordonnées de successeurs.

| Écart | Verdict et preuve ; traitement |
|---|---|
| Mondes Joss 622 épuisé, Tilo 566 épuisé, Joss 622 plan, Rémy mine 480 | **Voulu, migration seule** : unique différence structurelle, `/positions_hypotheses = {seuil: .5, demi_vies: {mobile: 15, pose: 60, retenu: 120}}`, ajoutée par `esprits.installer` au 374. Aucun plan ni coût changé. `test_completion_preuves` contrôle exactement cette règle après recharge puis garde les **quatre hashes d'origine** sur le reste du monde. |
| Mine 480, `a_mange` : états/successeurs/nœuds **503/2383/576 → 945/5678/1350** | **Voulu** : Rémy a entendu Gaspard en galerie à 459 ; à 480, confiance `2**(-21/15) = .378929… ≤ .5`. `salle_crue` retire sa présence certaine ; `_chercher` et `_parts*` ajoutent le contact préalable. Hash réancré seul, résultat toujours `None`. |
| Même graphe, 147 états communs modifiés | **Voulu, même preuve Gaspard 459** : retrait de 20 demandes de briquet, 19 demandes de feu, 20 devis différés de remise de `bois_gaspard` ; ajout de 25 questions à Mathe, 102 marches/inspections et 20 inspections en galerie. Les transitions conservées gardent leur sous-ordre et tous les bits de leurs coûts. Les 630 états nouveaux portent `cherche:gaspard`; 188 anciens états disparaissent avec les branches de contact certain. |
| Mine 480, `eclaire` : **1/6/2 → 1/8/2** | **Voulu, même preuve Gaspard 459** : deux occurrences de la question à Mathe, issues de `_parts_remises` et `_parts_calculer` pour `bois_gaspard` (remise/service). Temps `.285`, coût `3.285`, pression par minute `3`. Six déplacements initiaux inchangés. Hash réancré ; plan final et coût inchangés (aller au bureau). |
| Auberge 480 et 600, faim et lumière | **Aucun écart** : quatre graphes, résultats, coûts et hashes historiques conservés. |

**Preuve causale.** Une ablation diagnostique de l'expiration, puis de la seule
position de Gaspard, sur la copie du 374 restitue **chaque appel de `_suites` du parent**,
dans le même ordre, tuples et coûts hexadécimaux compris, pour les six graphes.
Les autres positions périmées (Josse et Lucien, 459) ne causent donc aucun écart
dans ces recherches. Aucune ablation n'entre dans les tests livrés.
Les quatre captures sont sauvegardées/rechargées dans chaque version ; monde
entier égal avant/après, rendu et scène identiques. Les plans sont rejoués trois fois.

**Vérification.** Les trois fichiers ciblés (`test_planification`,
`test_completion_preuves`, `test_gestes_par_noeud`) : **26/26 verts**, **64,4 s**,
deux processus à priorité réduite (`tests-voisins.json`). Les deux méthodes du brief
sont vertes, ainsi que les comparaisons du monde, du rendu et de la scène rechargés.
Deux lancements sous bac à sable n'ont pas pu écrire leurs résultats temporaires ;
ils sont exclus de ce bilan, acquis par le lanceur normal hors bac à sable.
Pas de suite complète, ni Luna, ni banc : seules les assertions de tests changent.

**Limites.** Aucun écart non attribué dans ces captures ; cette attribution ne
certifie ni tous les comportements du 374, ni l'absence générale de boucles.
Les deux occurrences d'un même préfixe restent dans le graphe ; ce lot ne change
pas son énumération. Fusion réservée au superviseur.
