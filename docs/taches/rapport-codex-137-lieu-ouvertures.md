# Lot 137 — lieu initial des ouvertures

Branche `codex-lieu-ouvertures`, **non fusionnée**, base `97e7198`.
Aucun Luna ; aucun fichier réservé aux lots 135/136 modifié. Deux processus
de calcul au plus, priorité réduite ; aucune comparaison de temps CPU.

**Invariant et carte.** Une ouverture déclarée par `relie` a son `lieu`
dans ces salles. Les dix ouvertures des huit scénarios JSON ont été contrôlées :
seules `porte` dans Relais/crue/rixe/rixe douce violaient ce contrat.
La carte place cette porte entre la sortie est de `crypte`, seuil `[9,3]`,
contact intérieur `[8,3]`, et la sortie ouest de `beffroi`, seuil `[-1,3]`,
contact `[0,3]`. Les axes sont attachés côté crypte. L'antichambre rejoint
l'échoppe, sans sortie sur la porte : aucune visibilité supplémentaire à créer.
Le lieu de référence devient `crypte` ; la présence physique reste des deux côtés.

**Correction commune.** `depuis_scenario` refuse avant construction toute
ouverture dont le lieu est extérieur à `relie`, sans filtrer le type ni le nom.
L'erreur et son `attendu` donnent objet, champ, valeur reçue et salles admises.
Les quatre JSON changent d'un champ chacun. Aucune croyance initiale `porte.lieu`
n'y est déclarée : `_lieu_cru`, puis `planification.Vue`, prennent pour ces objets
fixes le lieu corrigé. Les savoirs textuels décrivent déjà le trajet conduite,
vannes, palier et ne nécessitent aucun changement.

**Preuves.** Trois tests ciblés verts (0,437 s) : chargement de tous les scénarios,
même refus avec trois types et un autre identifiant, capture réelle crue 11
à 210 min importée du lot 133 et scène du Relais. État complet et rendu identiques
après sauvegarde/recharge ; absence physique dans l'antichambre, perception PNJ,
cases des deux côtés, ouverture exécutée par Ilse/Gorm, état perçu et rendu
rechargés. Le parcours de manipulation remet explicitement la porte brisée de
la capture en état et place les acteurs à portée : preuve d'accès, pas rejeu
de la promesse autonome historique. Une attente de texte ciblée a été corrigée
pour accepter les retours à la ligne du rendu.

**Banc 4 h, base contre branche, quatre graines chacun.** Les douze références
manquantes ont été calculées une fois puis cachées. Pour **chacune** des nuits
Relais 1985/7/42/2024, crue 1985/7/42/2024 et rixe 1985/7/42/2024 : chroniques,
récits, souvenirs, relevés PNJ, projection finale, boucles et constats identiques ;
zéro plantage/usurpation. Toutes les mesures métier sont identiques. Seul
compteur différent : crue 7, recherches neuves **629 → 624**, avec les mêmes
actions ; le lieu fixe corrigé modifie les entrées de recherche. Les douze
empreintes d'état complet diffèrent, ce qui est attendu avec `porte.lieu`
modifié ; le banc rapide ne conserve pas ces états complets pour une attribution
exhaustive champ par champ. Aucune nouvelle boucle dans ces nuits.

**Suite complète unique : 2 076 tests, 228 fichiers, deux échecs, zéro erreur,
1 073,32 s**, deux processus réduits. Uniquement les deux échecs MiMo historiques
`6 != 5` (`test_fournisseurs_jeu`, `test_restes_fusions`), déjà reproduits sur
la base intacte `3cdcab3` au lot 133 ; ces deux fichiers de tests sont inchangés
entre cette base et `97e7198`. Aucun autre défaut, aucune seconde suite.

**Limites.** Validation des scénarios initiaux, sans migration implicite des
anciennes sauvegardes ni effacement des croyances acquises historiquement.
Ce lot ne corrige pas les préconditions des gestes sur un objet brisé et
n'étend ni la visibilité ni les règles de promesse du lot 133.
Les premiers lancements du banc et des tests ont rencontré les permissions
Windows des worktrees/fichiers temporaires, puis ont été repris avec accès
approprié ; aucune suite complète rejouée.
Aucune clé Git de signature configurée : commit non signé.
Bruts : `artifacts/ouvertures-137/`.
