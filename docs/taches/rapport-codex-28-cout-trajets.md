# Rapport Codex 28 — coût des trajets

Branche `codex-cout-trajets`, **non fusionnée**, base `0ac6b15` (brief `ff33ef0`).
Invariant : décisions, coûts, ordre d'exploration, recherches et nœuds identiques.
Aucun appel à Luna. Deux leviers, deux commits signés : `6b6a9b5`, `8a734d2`.

**Profil par échantillonnage.** `py-spy` 0.4.2, 100 Hz, 4 h simulées, graine 42,
départ tiré ; 1 308/1 249 échantillons avant, 1 051/1 004 après (mine/auberge).
Parts inclusives, donc non additionnables : parcours **14,1 → 6,5 % / 21,8 → 11,5 %**
(distances locales incluses : 7,4 → 1,8 % / 10,8 → 3,4 %) ; approches
**8,8 → 3,1 % / 6,0 → 4,9 %** ; encodage JSON **7,0 → 6,1 % / 6,4 → 6,5 %**.
Profil : interpréteur Python 3.13.7 du venv avec ses dépendances (`py-spy` ne reconnaît
pas son lanceur Windows). CPU et tests : `.venv/Scripts/python.exe`.

**Leviers exacts.** `obstacles.parcours_cru` partage une LRU de 256 parcours. Sa clé
lit les géométries réelle et crue, obstacles crus (positions et formes), états des
portes de sortie, origine, allure, déverrouillages projetés, clés et serrures qu'elles
ouvrent, salles crues noyées, métrique, formes de franchissement, gabarit et équipement
utile, tarifs d'ouverture/déverrouillage. L'ordre des salles, sorties et obstacles
est conservé ; les rotations restent payées ensuite.
`spatial.VERIFICATION` recalcule le parcours et compare routes, chemins, séjours,
portes et tables locales ordonnées. `Vue.contacts` garde les cases atteignant les
cibles sous `(salle, cibles, centre)`, dans une vue géométrique figée ; elle conserve
l'ordre des tables qui départage les approches et recompute sous le même contrôle.
Pression inchangée, déjà gardée par salle, possessions et faits `allume`/`lieu`
(1,3 % / 2,4 % du profil final).

**CPU, trois versions lancées ensemble**, un travailleur chacune, priorité réduite ;
4 h, graines 42 et 1985, départ tiré, moyenne en secondes :

| Scénario | `42bb9c0` | `0ac6b15` | Branche | Gain contre Q | Branche / ancien |
|---|---:|---:|---:|---:|---:|
| Mine | 6,745 | 14,045 | 11,485 | 18,2 % | ×1,70 |
| Auberge | 4,840 | 13,290 | 11,255 | 15,3 % | ×2,33 |

Pics mémoire Q → branche : mine 63 → 70 Mo, auberge 88 → 92 Mo.
**Cible ×1,5 non atteinte.** Le temps reste dans `_explorer_etats` (39,9 % / 53,1 %,
dont génération des gestes 22,1 % / 35,0 %). Aucun champ d'`Etat` supprimé : case, orientation et
allure influencent respectivement approches, rotations et marche/gestes furtifs.
Une réflexion limitée pourrait gagner davantage mais changer les décisions ; elle
n'est pas implémentée. Estimation par les parts mesurées : atteindre ×1,5 demanderait
encore −12 % / −35 % du CPU total, soit environ −30 % / −67 % de la recherche seule.
Ce sont des seuils nécessaires, pas un gain démontré ni une équivalence exacte.

**Validation.** 50 tests ciblés verts ; Relais et mine exécutés puis rechargés
(source allumée, position, perception et récit), reprise entre vues, invalidation
de porte et détection d'un séjour corrompu. Empreintes strictes sur **16 nuits de
2 h** (quatre scénarios × quatre graines), recherches et nœuds compris : **zéro écart**
contre `0ac6b15` ; les quatre nuits CPU de 4 h sont aussi identiques à Q.
Contrôles `VERIFIER` + `spatial.VERIFICATION=1`, mine et auberge, 2 h, graine 42 :
aucun écart, aucune borne ; mêmes empreintes qu'en mode ordinaire.
Suite complète, lancée une fois à trois processus : **1 603 tests, quatre ignorés,
aucun échec**, 999,7 s ; le test existant de nuit de 10 h à la mine est inclus.
Bruts dans `artifacts/` du worktree ; références également conservées dans
`artifacts/references/{0ac6b15,42bb9c0}/codex-28-*.json` du dépôt principal.
Pas de banc long, d'audit, de fusion ni de modification de `main`.
