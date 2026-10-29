# Lot 290 — G0, contrat du MJ

29 octobre 2026. PC fixe. Branche `codex-g0-contrat`, **non fusionnée**.
Base intégration `4d9aad7`. Le brief figure dans ce commit. HEAD vérifié
sur cette base avant rédaction ; arbre de travail initial propre.

**Invariant.** La documentation distingue le contrat cible adopté des contrôles
encore nécessaires. Un contrôle ne disparaît que dans le portage qui livre
sa garantie de remplacement. G0 ne change aucun comportement du jeu.

**Changements.** Le [contrat détaillé](../contrat-mj.md) reprend en tête
le contrat d'`AGENTS.md`. Chaque section existante reçoit un statut.
Les sous-sections et les principaux blocs d'audit précisent leur devenir.
Noms, références publiques, portée, refus avec `attendu`, faits typés et
sauvegarde avant affichage restent valables. Audit du mécanique, révisions,
explications de refus et revues de fidélité sont rattachés à leur portage.
Le contrôle de l'ambiance cible reste en fond. Un doute fait jeter le bloc
entier sans relance. Les répliques à contenu fixé seront formulées par le moteur.

Les [plans prompt](../plan-prompt.md) et [migration](../plan-migration-mj.md)
gardent leur historique. Un encadré indique les reprises et abandons.
L6/170 est absorbé ; L7/166 reste abandonné. L'audit invariant 162 devient
sans objet sur les voies portées. Les phases 3 et 6 reportées ne deviennent
pas des préalables cachés au compilateur ou aux actions directes.

La [feuille de route](../plan-refonte-mj.md) est le suivi unique du superviseur.
Elle reprend l'ordre du 288. Chaque lot porte son invariant, ses dépendances,
ses fichiers probables, ses mesures sur les quatre axes et son état.
U-M et les extensions U-T sont séparés par famille. G3 accompagne le
compilateur si nécessaire ; le local peut attendre. K0/K1/K2 et D0 sont
décidés. Les mécaniques sociales nouvelles restent des chantiers distincts.
L'[état du développement](../etat-dev.md) porte l'entrée non fusionnée
et renvoie les pistes MJ de « À revoir » vers cette feuille.

**Vérification documentaire.** Lecture d'`AGENTS.md`, du brief et des décisions
287/288. Les 14 sections et 39 sous-sections anciennes sont annotées.
Les 46 lots couvrent G0–G21/U/K/D, leurs dépendances et les quatre axes.
Les 23 liens ajoutés sont résolus, ancres comprises ; encodage UTF-8 contrôlé.
Les blocs historiques du contrat restent conservés, sauf l'introduction
remplacée pour distinguer cible et transition. `git diff --check` sans erreur.
Six documents livrés. `AGENTS.md` et les fichiers sous `donjon/`, `tests/`
et `tools/` restent inchangés. Aucun test de jeu, import du jeu, appel à Luna
ou banc. Aucun calcul actif.

**Limites.** Cette lecture ne prouve aucun invariant en exécution et ne mesure
aucun gain de vitesse. G0 reste `en cours` jusqu'à intégration. Les fichiers
du plan sont indicatifs. Chaque portage devra vérifier cas réel, autre cas
de même nature, état et rendu après recharge. Le retrait des revues exige
une observation de ce que le joueur comprend. La prose libre ne garantit
pas toute absence de contradiction implicite. Aucune contradiction bloquante
relevée dans `AGENTS.md` ; aucune modification de ce fichier.

Livraison sur la branche `codex-g0-contrat` vers
`origin` (`https://github.com/msicsic/jdr.git`), sans fusion ni rebase.
Le résultat de poussée et le commit sont donnés à la clôture du lot.
