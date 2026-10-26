# Lot 118 — reprises exactes du planificateur

Branche `codex-reprises-exactes`, **non fusionnée**, base `c3568ae`.
Aucun Luna, scénario, prix, plafond ou changement de décision voulu.
Moteur limité à `planification.py` ; lot perception 119 indépendant.

**Contrats.** A3 (`2fd4c4a`) partage les tables du monde cru pendant un choix,
avec paramètres, découvertes et parts privés ; le JSON commun était déjà
partagé. A2 (`5827a31`) retire les signes bruts, conserve leurs effets dérivés
et les cases réellement lues, y compris dans les salles atteintes par le plan.
La réduction des positions reste conservatrice : acteur et entrées hors
entités écartés, cibles connues et leurs contenants conservés.
A1 (`96350dc`) garde le premier graphe, certifie le premier épuisement et
libère les nœuds prouvés en gardant la discrétion. Correctif `d782dfc` :
`_entrees_effort` sépare la signature durable des attentes de la clé de calcul.
L'essai A2 initial différait par deux chaînes sauvegardées : ses bruts
`essai-A2-signature` restent invalides pour l'exactitude ; cohorte corrigée
distincte. [Audit des lectures et contrats](../plan-planificateur.md#reprises-dès-la-première-recherche-lot-118).

**A4 (`757fbf3`) non appliqué : prémisse réfutée.** `gestes` lit indirectement
l'allure par les trajets, recherches de tiers, parts et devis. Joss/auberge
600 min, `aller cellier` : **0,16916666666666666 / 0,32166666666666666** minute
à allure 15/30 ; états et suites différées retiennent aussi cette allure.
Test ajouté ; aucun élagage des feuilles qui comptent dans la borne.
Partager les recettes séparément des mesures reste à concevoir : A4 non garanti.

**Exactitude.** Par levier : six recherches mine 480/auberge 480/600, faim et
lumière, mêmes états, successeurs ordonnés, coûts hexadécimaux et plans.
Trois tours moteur : mêmes résultats, monde, lignes joueur et deux rendus
après recharge. Tests ciblés : 14 tables/partage/suites, six nouveaux,
27 de preuves (une attente de compteur actualisée). Une case omise à tort
est refusée par VERIFIER ; le réveil d'effort sauvegardé égale le témoin A3.

**Mesures par levier, auberge tirée 12 h, 1985.** Chaque ligne est une paire
lancée ensemble, sans profileur ; les temps de lignes différentes ne sont
pas comparables sur le poste partagé. A4 n'ajoute aucun code de recherche.

| Levier | CPU avant → après | Variation | Nœuds avant → après | Pic Mo avant → après |
| --- | ---: | ---: | ---: | ---: |
| A3 | 324,73 → 333,09 s | +2,6 % | 708 522 → 708 522 | 113,4 → 134,6 |
| A2 corrigé | 338,69 → 337,97 s | −0,2 % | 708 522 → 692 059 | 132,9 → 138,2 |
| A1 corrigé | 341,06 → 392,50 s | +15,1 % | 692 059 → 638 478 | 136,2 → 266,6 |

**Aucun gain global établi par ces leviers.** A1 réduit les développements de
recherche mais fait **60 → 365** tentatives de preuve ; le pic mémoire double.
Visites de preuve **59 334 → 281 984**, sans plafond atteint, pour seulement
**53 581** développements de recherche évités.
Les trois comparaisons `--calcul` sont exactes, état entier inclus.

**Paires finales de 12 h, graine 1985.** Priorité réduite, deux ouvriers au
plus ; chaque flèche compare des versions lancées ensemble. Une passe par
paire, poste partagé. Base/branche : **trois nuits, zéro différence
`--calcul`**, monde et rendus rechargés identiques. Les deux répétitions de
branche ont les mêmes nombres de nœuds et de preuves.

| Nuit | `42bb9c0` → branche CPU | Rapport | Base → branche CPU | Variation | 8–12 h base → branche | Pic Mo base → branche |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Auberge fixe | 114,73 → 221,91 s | ×1,93 | 190,48 → 220,05 s | +15,5 % | 119,922 → 143,062 s | 131,6 → 175,6 |
| Auberge tirée | 91,98 → 350,23 s | ×3,81 | 288,94 → 339,20 s | +17,4 % | 248,766 → 299,453 s | 112,9 → 264,6 |
| Mine fixe | 270,66 → 97,72 s | ×0,36 | 81,73 → 85,20 s | +4,2 % | 41,109 → 42,703 s | 76,4 → 94,4 |

Tranche 8–12 h ancien → branche, mêmes paires : auberge fixe
91,734 → 146,641 s, tirée 68,734 → 309,687 s, mine
236,469 → 48,609 s. **Seuil ×1,5 manqué aux deux départs de l'auberge ;
lot non recommandé pour intégration comme gain de coût.** Les prédictions
de la revue ne sont pas confirmées : A2 ne peut supprimer les cases
réellement lues, et A1 multiplie les preuves précoces et la mémoire retenue.

Empreintes 2 h : **16/16 chroniques et états finaux identiques**, références
en cache ; seul `recherches_neuves` change sur les quatre mines
(163→156, 153→150, 157→155, 189→187). Toutes les autres mesures concordent ;
rapport strict brut conservé, compteur de travail séparé comme dans `--calcul`.
VERIFIER + spatial **1**, auberge 42 tirée, 2 h : **aucun écart ni BORNES**,
**290,58 s CPU**, monde et deux rendus rechargés identiques.
Suite complète unique : **2 046 tests, 16 ignorés, 221 fichiers, 1 778,82 s**,
deux processus réduits ; six assertions anciennes de calcul dans quatre
fichiers actualisées, **18 reprises vertes en 63,90 s**, zéro échec restant
consolidé. Plans, monde et rendus historiques vérifiés avant d'enregistrer
les seuls nouveaux compteurs (visites mine 5 478 → 4 579). Aucune seconde
suite complète ; vérifications lourdes expressément demandées, créneau
habituel du lot largement dépassé.

Bruts : `artifacts/reprises-118/`. Reproduction :
`tools/verifier_reprises_118.py`, `tools/banc_reprises_118.py --leviers`,
`tools/verifications_reprises_118.py --suite`. Archives locales seulement ;
le dépôt principal ne reçoit que les références du cache autorisé.
