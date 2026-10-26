# Lot 92 c — compléter la preuve à profondeur minimale

Branche `codex-aller-utile`, **non fusionnée**, suite de `7598fc4`, base moteur
**9810f4a**. Aucun coût, prix, plafond, scénario ou choix changé.

**Mesure préalable.** Auberge 1985 tirée, `[480, 720[` : les **31 lacunes de
faim** (18 Tilo, 13 Joss) deviennent certifiables. Seules les relances à une
minute ultérieure, même but, signature et permission, comptent : **234 relances,
395 972 expansions**, dont **191 relances de faim, 358 057 expansions évitables**.
Coût sur toute la nuit et tous les buts : **2 837 états
ajoutés**, **7 728 listes complétées**, union **10 353 états enrichis**, **69 231
visites de preuve**, **5,39 s CPU** instrumentées. Borne nette : **347 704,
33,06 %** des 1 051 797 expansions ; en retranchant aussi toutes les visites,
**26,48 %**. Le seuil ~15 % justifie l'implémentation. Témoin 92 b réutilisé ;
relevé sans changement des résultats ni du monde.

**Invariant.** `_parcours` visite en largeur, à profondeur minimale.
`_preparer_graphe_preuve` complète dans une vue privée les seuls nœuds manquants,
avec le même `_suites` que la recherche jouée ; `_sans_plan` publie les
compléments sûrs dans le graphe gardé. File épuisée sans but : aucun chemin
admissible dans la profondeur autorisée ; changer les prix ne crée aucun arc.
Permissions, départs, profondeur et entrées restent couverts par la signature
existante, sans nouveau cache ni champ sauvé. Une lecture sombre exige aussi
la preuve lumineuse ; nouvelle discrétion, but ou plafond de preuve ne certifient
rien. Une sortie terminale admissible interdit le certificat. Une recherche
bornée conserve l'attente distincte du lot 87. `VERIFIER` refait **toute reprise
par certificat** avec la complète à `REFERENCE`. Preuve détaillée dans
[le contrat du planificateur](../plan-planificateur.md).

**Contrôles.** Captures Joss 622, Tilo 566, mine 480 et plan positif : mêmes
plans/coûts hexadécimaux, monde et rendus après recharge. Joss et mine passent à
zéro nœud au troisième appel, contre 2 071 et 576. **32 tests ciblés existants +
huit nouveaux verts**. Empreintes 2 h : **quatre scénarios × quatre graines,
16 identiques** contre la base, références mises en cache. `VERIFIER` + spatial
1, auberge 42 tirée, 2 h : aucun écart ni borne, **354,34 s CPU**.

Suite complète unique : **1 947 tests, 16 ignorés, 201 fichiers, 1 828,67 s**.
Deux reprises ciblées vertes : erreur Windows TUI de remplacement temporaire
non reproduite ; empreinte de calcul mine adaptée (7 212 → 5 478 visites).
L'oracle historique reste intact ; le supplément n'est produit qu'après contrôle
strict des plans, monde, lignes joueur et rendus. Aucun défaut restant consolidé.

**CPU 12 h, graine 1985.** Protocole autorisé : deux cohortes appariées,
ancien/branche puis base/branche, deux processus à priorité réduite, sans cache
de temps ; premier contrôle base/auberge-tirée effectué avant la suite.
Chaque flèche compare deux versions lancées ensemble. Temps en secondes CPU :

| Nuit | `42bb9c0` → branche | Rapport | Base → branche | Gain | 8–12 h ancien → branche | 8–12 h base → branche |
|---|---:|---:|---:|---:|---:|---:|
| Auberge fixe | 131,03 → 257,05 | ×1,96 | 239,11 → 238,94 | 0,1 % | 104,88 → 195,83 | 183,44 → 183,25 |
| Auberge tirée | 105,98 → 341,17 | ×3,22 | 335,31 → 318,27 | 5,1 % | 77,16 → 287,81 | 288,41 → 271,50 |
| Mine fixe | 282,14 → 93,22 | ×0,33 | 88,59 → 85,94 | 3,0 % | 246,20 → 47,38 | 46,59 → 43,97 |
| Mine tirée | 116,30 → 147,64 | ×1,27 | 152,64 → 148,73 | 2,6 % | 74,02 → 83,42 | 87,16 → 83,16 |

`comparer --calcul` : **quatre nuits, zéro différence** base/branche ; idem
entre les deux répétitions branche. Monde et rendus rechargés identiques partout.
Nœuds base → branche : auberge tirée **1 175 083 → 706 709** ; mine fixe
**353 115 → 187 010**, tirée **472 638 → 283 772** ; auberge fixe inchangée.
Le gain CPU reste modeste : beaucoup de reprises évitées relisaient déjà un
graphe. **Seuil utilisateur ≤ ×1,5 à l'auberge fixe et tirée non atteint ;
ce lot ne permet pas d'avancer `main`.** Une seule mesure par paire, charge
partagée, sans affinité ; ne pas comparer les temps entre cohortes.

Bruts/reproduction : `artifacts/preuves-92c/`, outils `mesurer_completion_preuves`,
`bilan_completion_preuves`, `rejouer_preuves_92c`, `banc_preuves_92c`. Moteur figé
pendant les validations ; aucun Luna ni sauvegarde utilisateur touchée. Écart
préalable de charge : un test ciblé de cinq secondes a chevauché deux contrôles ;
cohortes CPU et suite complète limitées à deux processus. Le lourd expressément
demandé a dépassé la durée habituelle d'un lot.

**P3, sans implémentation :** choisir la route au prix réel, pression comprise,
ne suffit pas à prouver P3 (portes et admissibilité/retour restent à couvrir) ;
cela pourrait changer les routes retenues, leurs coûts et les décisions.
