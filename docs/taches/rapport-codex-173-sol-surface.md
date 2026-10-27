# Lot 173 — la surface du sol comme destination

Branche `codex-sol-surface`, non fusionnée, base `79594e4`, PC fixe partagé
avec les lots 167 c et 172. Aucun fichier réservé au lot 172 modifié.

**Invariant.** `deplacement_objet.destination_depot`, appelé par
`operations.compiler`, résout un objet de type `surface`, nommé exactement
`sol`, visible et situé dans la salle courante, vers la même destination
physique que `sol`. Le dépôt utilise la case de Corvus, sans déplacement
vers un éventuel ancrage de la surface. La résolution suit l'état de chaque
étape pour `deplacer`, `prelever`, séquences et improvisations. Aucun
identifiant de scénario ni consigne supplémentaire à Luna. Murs, plafonds,
sols distants ou non perçus et objets simplement nommés sol suivent le refus
commun de destination, avec valeur reçue et destinations admises dans `attendu`.

**Vérification ciblée.** Neuf tests verts (1,714 s) dans
`tests/test_poser_sol.py` : console et MJ simulé, `antichambre_sol` et
`cour_sol`, prélèvement direct et improvisation, refus sans mutation, état
complet des refus et scène/carte après sauvegarde et rechargement. Les
contrôles existants des dossiers de contre-revue restent verts.
Les premières tentatives ciblées ont rencontré les permissions temporaires
du bac à sable, puis une normalisation de référence publique du nouveau
repère de test ; reprise finale verte avec scène normalisée.

**Luna non validée.** Première exécution réduite prévue pour les deux dépôts
et `atelier` : coffre illisible dès les appels (13 tentatives locales,
13 tours en erreur, aucune réponse modèle). Vérification directe de lecture
également en échec ; aucune donnée secrète affichée. Deuxième passe non
lancée, faute de coffre lisible. Aucun résultat de cette tentative ne
certifie l'absence de refus de destination ou la fidélité sémantique.
Commandes exactes des deux passes à reprendre dans
`C:/Users/msics/donjon/artifacts/sol-173/luna-a-jouer.txt`.

**Suite unique et banc.** 2 251 tests, 259 fichiers, 1 295,595 s, deux
travailleurs réduits : zéro erreur/ignoré, deux échecs MiMo historiques
`6 != 5` (`test_restes_fusions`, `test_fournisseurs_jeu`), aucun autre échec.
Relais, 4 h × quatre graines : états finaux, relevés, bilans, boucles et
constats identiques 4/4 à `main` `812ebe5` ; seules les secondes diffèrent
dans les données de nuit. Trois `fige_presse` historiques de chaque côté,
aucune alerte nouvelle. Références entièrement relues dans le cache,
branche seule calculée avec un travailleur réduit quand la suite n'en
avait plus qu'un actif. Aucun gain de temps revendiqué (charges distinctes).
L'atelier n'a pas de banc PNJ ; il est couvert par la console simulée.
Aucune clé Git de signature configurée. `main` intacte ; livraison limitée
à la branche du lot. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/sol-173/`.
