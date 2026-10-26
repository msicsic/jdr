# Revue externe : le coût des bancs, qu'avons-nous manqué ?

Demande de l'utilisateur (2026-10-26) : un regard neuf sur le coût de calcul des nuits simulées, après une longue série de lots.
**Revue seule, sans modifier le code du jeu.** Tu écris uniquement ton rapport : `docs/taches/rapport-revue-argon-cout.md`.

## Le projet en deux phrases
« Le Seuil » : jeu de rôle textuel en français ; un moteur Python déterministe simule des PNJ (perception, ouïe, besoins,
relations, échanges) minute par minute et seconde par seconde, et un MJ (modèle de langage) raconte. Les « bancs » jouent des
nuits entières sans joueur pour vérifier le comportement des PNJ ; ce sont eux qui sont trop lents.

À lire : `AGENTS.md`, `docs/plan-planificateur.md`, `docs/plan-decision.md`, `docs/etat-dev.md` (« À revoir », volet coût), et le
code : `donjon/planification.py` (recherche A*/Dijkstra pondérée des plans d'un PNJ : `chercher`, `_explorer_etats`, `gestes`,
`Vue`, `Etat`, `_entrees`, `_MEMOIRE`, graphes repris, certificats `_sans_plan`), `donjon/deliberation.py` (`choisir`,
`_candidats`), `donjon/pnj.py` (`_avancer`), `donjon/trajet_estime.py`, `donjon/obstacles.py`, `donjon/spatial.py`,
`donjon/esprits.py` (perception), `donjon/signes.py`, `donjon/ouie.py`.

## Le but et la mesure
Seuil de l'utilisateur pour avancer la branche principale : nuit de 12 h de l'**auberge**, graine 1985, temps CPU **≤ ×1,5**
contre l'ancienne version `42bb9c0`, au départ « fixe » et au départ « tiré » (état initial tiré de la graine). Aujourd'hui
(vérification `590653e`) : **×1,65 fixe** (118 → 195 s), **×2,64 tiré** (93 → 247 s). Le surcoût croît avec l'heure de la nuit
(8–12 h surtout). Contrainte dure : les optimisations **ne changent aucune décision** des PNJ (empreintes identiques de l'état,
`comparer --calcul` mêmes résultats de recherche ; `planification.VERIFIER` et `spatial.VERIFICATION` recontrôlent toute reprise),
sauf décision explicite de l'utilisateur.

## D'où vient le surcoût (profils des lots 98 et 109)
- **Fréquence** : sur 8–12 h, `choisir` 14,9 → 20,2 appels/minute (fixe), `chercher` 16,8 → 26,5 /min (fixe), 10,5 → 19,5 /min
  (tiré). Décomposition : **≈ 58 % fréquence, 42 % coût moyen** par recherche. Causes probables : délibération à chaque événement
  (pas seulement à la minute), recours « faute de mieux », temps réel.
- **Coût moyen** : surtout le **tiré** (123 → 209 ms par recherche ; 2,67× plus d'états développés par recherche que le fixe).
  **58 % du CPU de recherche tirée** est dans les recherches qui essaient **les deux allures** (pas ordinaire / pas feutré pour agir
  sans être entendu) ; Tilo/faim seul : 105 passes, 155 k nœuds, 59 s.
- **Perception** (esprits, spatial, signes) : **62 → 111 s** (fixe), **52 → 104 s** (tiré) sur 8–12 h — **pas encore attaquée**.
- Hausses propres de fonctions (Δ fixe / tiré, s) : `dict.get` +27/+70, `spatial._bloquantes` +32/+33 (traité, lot 98 b),
  `_normaliser_suites` +17/+42, `Etat.apres` +13/+33, `gestes` −12/+55, `Vue.arrivee` +11/+19, `mesure_aller` +9/+17,
  `_mesurer` +8/+16, `prix_route` +5/+12. « JSON, primitives et autres » 147 → 228 s.
- Le saut principal de l'historique : les **trajets réels** (lot Q : un trajet coûte son temps réel en secondes, cases, portes,
  approches, au lieu d'une minute par salle) : ×4,3 à nœuds presque égaux (bissection, lot 76).
- 68 à 88 % du coût de fin de nuit vient de recherches **sans plan** (épuisées ou bornées à 4 000 nœuds) : une borne A* ne les
  accélère pas.

## Ce qui a été fait (gains exacts, mêmes décisions)
- Lot 38 : borne admissible des suites terminales, caches exacts des parts/devis, imports hors des fonctions chaudes (−15 à −20 %).
- Lot 46 : une source de lumière en plus sans capacité nouvelle n'ouvre aucun geste (mine −34 %).
- Lot 48 : borne admissible du séjour final (contrat : mêmes décisions hors plafond ; si la référence plafonne, résultat = recherche
  complète à 60 000 nœuds).
- Lot 49 : certificat nécessaire d'allumage dans les devis (−1 à −2 %).
- Lot 51 : départ feutré découvert seulement au besoin (−2,7 %).
- Lot 71 : préparation paresseuse de `Vue`, entrées communes partagées pendant un choix (−2 %).
- Lot 72 : étapes chaînées sans recopie des préfixes (−0,6 %).
- Lot 81 : tarifs et routes partagés par les nœuds d'une `Vue` (−2 à −9 %).
- Lot 86 : lieux, portée, droits partagés par salle (−4 à −10 %).
- Lot 87 : une recherche bornée sans plan attend un fait nouveau avant d'être refaite (auberge −21,6 % fixe, −8,5 % tiré).
- Lot 92 c : preuves d'absence de plan complétées à profondeur minimale (nœuds −40 % au tiré, mais CPU −5 % : les reprises
  évitées relisaient déjà un graphe).
- Lot 98 b : obstacles relevés une fois par trajet estimé (−2 à −4 %).
- Lot 105 : effets de portes d'un trajet composés sans recopier l'état (−4,5 % / −7 %).

## Ce qui a été tenté sans gain
- **C1, « une capacité nouvelle ou rien »** (lot 52) : ne prendre/demander un objet que s'il apporte une capacité absente ;
  règle généralisée, **aucun gain** (nœuds −0,1 %).
- **P3, « aller seulement vers une salle d'intérêt »** (lot 92) : 88 % des successeurs sont des `aller` et 34 % des expansions
  sont des salles de passage sans geste ; mais **impossible à prouver exact** car `trajet_estime` minimise la distance alors que le
  prix réel ajoute une pression par salle (noir, garde, eau) : un trajet en deux arrêts peut être moins cher ; filtre conservateur
  = 0,5 % des états.
- **P2, pertinence des préparatifs par chaînage arrière** (lot 92 b) : 74 % des expansions descendent d'un préparatif
  (prendre la burette, le pot d'huile, les fagots…), mais une clôture conservatrice n'en déclare que **0,01 %** sans rapport.
- **Caches** : les lots 52 et 66 (caches ajoutés) n'ont pas été fusionnés faute de gain ; principe retenu « réduire l'espace plutôt
  qu'ajouter un cache ».
- **PyPy** : 1,5 à 1,7 fois plus lent ; écarté. **Rust/PyO3** pour le noyau géométrique : repoussé (pas avant l'étape A5).

## Leviers identifiés mais non tentés
- Exacts : perception (esprits/spatial/signes) ; `gestes`/`_normaliser_suites` au tiré ; `Etat` en bitsets ; ouïe ; « JSON et
  primitives » à décomposer ; retirer les caches qui ne rapportent plus ; relevé automatique des entrées de la mémoire des
  recherches.
- Qui changent le comportement (décision de l'utilisateur) : réduire la fréquence des relances (choix/recherche refaits à chaque
  événement) ; borner l'exploration des deux allures ; le « plan de décision » (habitudes, réflexion limitée, saillance, budget
  selon l'enjeu, A* pondéré — `docs/plan-decision.md`, prévu après A4).

## Ce que nous te demandons
1. Lire le code et ces constats, et dire **ce que nous avons manqué** : une cause de coût mal comprise, une mesure trompeuse, une
   structure de recherche ou de données inadaptée (représentation de l'état, ordre d'exploration, granularité des actions, ce qui
   est recalculé à chaque choix), une idée classique de planification ou de simulation multi-agents non essayée (par exemple
   recherche incrémentale type LPA*/D* Lite, planification hiérarchique par salles, réutilisation de plans, abstraction des
   allures, évaluation paresseuse, invalidation par dépendances au lieu de clés…).
2. Pour chaque piste : pourquoi elle s'appliquerait ici, le gain attendu (ordre de grandeur) sur l'auberge 8–12 h, si elle peut
   garder **exactement** les mêmes décisions ou si elle les change, et comment la vérifier.
3. Classer les pistes par rapport gain / risque / effort ; dire honnêtement si le seuil ×1,5 te paraît atteignable **sans** changer
   les décisions.

Tu peux lancer des mesures légères (profil d'une recherche, `python -m cProfile`) avec `C:\Users\msics\donjon\.venv\Scripts\python.exe`,
priorité réduite, **un processus à la fois** (le poste est partagé) ; ne modifie aucun fichier du jeu ni la branche principale.
Rapport : `docs/taches/rapport-revue-argon-cout.md` (deux pages au plus), commité sur ta branche.
