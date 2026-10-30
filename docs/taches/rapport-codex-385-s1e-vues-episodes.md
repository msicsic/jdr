# Lot 385 — S1e, vues pures des épisodes

31 octobre 2026 · `codex-s1e-vues-episodes` · base exacte `integration b2028ede`.
Moteur mesuré : `dba080d1` (correctif `a50a3648`) ; observateur : `a848394d`.
`origin/integration fcb82692` fusionnée, dernière lecture distante à la clôture :
aucune nouvelle avance ; ces fusions ne changent que la documentation.

**Invariant livré.** Tous les lecteurs restants du tampon d'épisodes passent par
`memoire.episodes`, vue pure renvoyant des copies profondes sans créer d'esprit.
L'ordre de liste, les doublons et les dates restent inchangés. La fenêtre des
trois derniers souvenirs porte sur le tampon entier avant le filtre de types ;
les quatre dernières paroles admissibles gardent leur ordre et leur contrôle
de connaissance. Les politiques métier restent chez leurs consommateurs.
Jeu, paroles, récit, exports du banc et diagnostics sont portés ; dernier son
et rejeu utilisent déjà la porte sonore de S1b. Le registre distinct
`violences_joueur` de la défense reste hors de ce tampon.

`rafraichir_geste_entendu` reprend l'écriture cachée dans l'audition : dernière
occurrence correspondante, borne inclusive, même identité, aucun ajout/crochet.
`migrer_presences_percues` retire les anciens épisodes par identité et rend des
copies des présences. Liste, plafond 40, clés et sérialisation restent inchangés ;
aucun registre ajouté. Le détecteur charge la porte livrée avec l'observateur,
dont les imports relatifs lisent le moteur comparé, même antérieur à cette API.
Le récit importe sa vue à l'usage ; la clé du cache inclut le code de la vue.

**Contrôle et tests.** Inventaire AST : 69 expressions initiales → **zéro lecture
hors exceptions nommées**. Restent cinq validations de schéma et dix-huit
homonymes de diagnostic. Créations vides et fixture d'outil sont gelées à
l'expression exacte. Mutations de champs de toute famille, alias, champs
imbriqués, méthodes détachées, sélections par indice/`next`, retours bruts et
copies superficielles de liste sont éprouvés. Le contrôle reste syntaxique,
sans preuve exhaustive des flux interprocéduraux de Python.

Bilan consolidé des **22 fichiers : 325/326 verts, aucune erreur ni saut**.
Les 17 fichiers concernés repassent (284 tests, 588,5 s) ; les cinq fichiers
restés verts apportent 42 tests réutilisés. Les erreurs initiales étaient dues
au masquage de la vue par le dictionnaire local des signes ; l'alias est corrigé.
Le mock du détecteur suit désormais la vue pure. Une contre-épreuve charge
l'observateur avec une référence dépourvue de la nouvelle API.

Cas réels : Odon au coffre de la paie entendu par Bram, puis Lucien au coffre
ferré entendu par Anselme. Même laps entier/découpé avec recharges : état complet
et ordre JSON, rendu, scène, paroles émises/retenues, récit sans mutation.
Les tests couvrent aussi copies imbriquées, pureté, ordre et rafraîchissement.
Le seul rouge, `passage.test_cas_reel_acceptee_elle_s_ecarte_vraiment`, attend
l'ancien texte « Tu avances d'un pas. » ; il échoue à l'identique sur une copie
isolée de `b2028ede`. Limite héritée attribuée, aucun comportement de passage
modifié. Les sauvegardes temporaires ont nécessité l'exécution autorisée hors
restriction Windows, sans adaptation du moteur.

**Empreintes : 16/16 identiques.** Deux heures × graines 1985/7/42/2024 ×
Relais/mine/auberge/crue, contre `b2028ede` : chronique, mesures, récit,
souvenirs, empreintes du banc et état final complet, sans exclusion ni plantage.
Les références manquantes et les nuits de branche sont rangées dans le cache.
Avis auxiliaires identiques : neuf « à expliquer », aucun « non justifié » ;
aucune correction revendiquée. Référence puis branche, deux processus au plus,
priorité réduite ; aucun coût comparé, aucune suite complète ni Luna.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1e-385/` :
`tests-corriges.json/log`, `empreintes-base-corrigees.json/log`,
`attribution-passage-base.log`, `conclusion.json`, les premières passes,
`run-corrige.ps1` et `fin-corrige.json`. La première campagne s'était arrêtée
avant toute nuit, sur l'import de la vue absente de la référence.
Recouvrement 374 : lectures de `deliberation`/`echanges`, migration d'`esprits`,
audition et services de `pnj` ; aucune localisation ni recherche modifiée.
Aucun fichier propre à 380/381 touché. Oubli historique et nouveau stockage
restent hors lot. **Lot clos avec le rouge hérité ci-dessus ; aucun calcul requis
ni vérification ciblée en attente.**
