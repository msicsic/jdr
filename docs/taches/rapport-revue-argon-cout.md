# Revue Argon — Coût de calcul des nuits simulées (`auberge` 12 h)

## État des lieux chiffré (lot 114, `590653e` contre `42bb9c0`)

Sur `auberge` 12 h (graine 1985), la cible **≤ ×1,5** correspond à **≤ 177,8 s** en départ fixe (réf. `118,5 s`) et **≤ 140,0 s** en départ tiré (réf. `93,3 s`). Le moteur actuel est à **195,1 s en fixe (×1,65)** et **246,7 s en tiré (×2,64)**, dont plus de 80 % dans la tranche **8–12 h** (~155 s fixe, ~214 s tiré).
- **En fixe**, il ne manque que **−17,3 s (−8,9 %)** : le seuil est à portée immédiate.
- **En tiré**, il faut retrancher **~107 s (−43,3 %)** sur 12 h (soit ~50 % du coût de 8–12 h), où **88,1 % du CPU de `chercher`** passe dans des recherches sans plan (`435` épuisées = 68,5 %, `162` bornées = 19,6 %), dominées par `Tilo/faim` (32,6 %) et `Joss/faim` (26,7 %).

---

## 1. Ce qui a été manqué dans les lots précédents

1. **Le piège « deux recherches avant certificat » (`_GRAPHES` / `_IMPOSSIBLES`) et l'invalidation parasite de `_entrees_communes`**
   Dans `planification.chercher` (l. 2018–2045), au **premier** appel après tout changement de `base = _entrees_communes(v)`, le moteur initialise `graphe = {"garder": False, "discretion": False}`. Cela a trois effets destructeurs :
   - `_explorer` met `sombre = None` et `lumiere = None` (l. 2200) : aucun nœud ni liste `gestes` n'est conservé.
   - Si cette 1re recherche déclenche 2 ou 3 passes internes (découverte de lumière ou de discrétion en cours d'exploration : **109 recherches et 155 702 nœuds en tiré**, dont 105 pour `Tilo/faim`), la passe 2 recalcule `gestes` depuis zéro pour tous les nœuds déjà ouverts en passe 1.
   - Quand cette 1re recherche s'épuise sans plan (`trouve is None and not borne`), **le certificat d'impossibilité du lot 92c (`_sans_plan`) n'est pas construit** car la ligne 2042 exige `and graphe.get("garder", True)`. Il faut attendre une **2e recherche complète** (à la minute suivante, quand le tarif `faute` bouge) avec exactement le même `base` pour que `garder` passe à `True`, que l'arbre soit ré-exploré de zéro et que `_sans_plan` soit enfin appelé.
   - Or `base = _entrees_communes(v)` est invalidé en permanence par des faits que `chercher` **ne lit jamais** :
     - `"cases"` (l. 1921) inclut `[s, salle, case]` pour **toutes** les croyances du PNJ. Chaque fois qu'un tiers (ex. Odile, 36 fois pour Tilo en 4 h) fait un pas d'une case dans une salle vue, `base` change, détruisant `_MEMOIRE` et `_GRAPHES` (`garder` retombe à `False`). Pourtant, `Vue.approche` renvoie `0` dès que `e.salle != v.salle_depart` (l. 859), et dans `v.salle_depart`, `Vue.case_objet` n'est jamais lu pour un PNJ conscient sauf s'il est cible directe (`_a_toucher`) ou donneur d'un lot partageable (`_attente_part`).
     - `"signes": actives(monde, id)` (l. 1899) invalide `base` à chaque expiration de signe social, alors qu'aucune fonction sous `chercher` ne lit `actives`.

2. **Les 12 tables géométriques de `Vue` jetées entre recherches d'un même `choisir()` (`vues_du_choix`)**
   Dans `vue(monde, id)` (l. 203–220), `partage[0]` reste vierge et chaque recherche du même `choisir()` (jusqu'à 8 candidats sur la même photographie du monde) reçoit une copie de dictionnaires vides `{}`. Les 12 tables qui ne dépendent **que** du monde cru (`_contextes_routes`, `_contextes_pressions`, `_parcours`, `_routes`, `_allers`, `_approches`, `_contacts`, `_locaux`, `_moyennes`, `_effets_routes`, `_tarifs_routes`, `_mesures_allers`, plus `_pressions` et `_droits_gestes`) sont donc recalculées à chaque candidat, alors même que `_verifier` (l. 2116) et `_preparer_graphe_preuve` (l. 2557) les partagent déjà explicitement. De plus, `_entrees_communes(v)` (et son lourd `json.dumps` sur tous les objets et croyances) est rappelé à chaque `chercher()` (6 329 fois en 4 h) au lieu d'une fois par `vues_du_choix`.

3. **Duplication du graphe et de `gestes()` entre `allure=15` et `allure=30` (57,6 % du CPU de recherche en tiré)**
   Quand la discrétion est active (`departs = [allure=15, allure=30]`), `Etat` inclut `allure` dans sa clé.
   - D'une part, `gestes(v, e, vises, but)` (220 lignes, ~45 % du coût par nœud) **ne dépend pas de `e.allure`** : le filtre `e.allure != 30` sur `sans_temoin`/`dans_le_dos` est appliqué *après* dans `_normaliser_suites` (l. 2428). Pourtant, `gestes()` est exécuté deux fois pour chaque état `(salle, portes, faits)` visité dans les deux allures.
   - D'autre part, un but en `allure=30` n'est valide que si `e.fait("furtif")` est vrai (l. 2351). À profondeur `n == profondeur - 1`, pour tout état `e.allure == 30` avec `not e.fait("furtif")`, toute transition non furtive produit une feuille à `n == profondeur` qui ne peut **ni** être un but **ni** être développée : mesurer sa route/approche et l'empiler est un travail mort.

4. **Biais de `cProfile` et surcoûts de perception hors `etat_fige`**
   `cProfile` gonfle de ×4,5 à ×6 les petits appels Python (`_case_libre`, `dict.get`, `Etat.fait`), ce qui a surestimé le gain du lot 98b. Côté perception (~104–111 s instrumentées) : 1) dans `pnj._avancer` (l. 1889–1890), `percevoir(monde, id)` est appelé pour chaque PNJ juste avant `percevoir_tous(monde)` ; 2) à chaque pas (l. 1963), `percevoir_signes(monde)` s'exécute **hors** de `with etat_fige(monde):` et `signes._percus_gardes` (l. 280) fait `repr()` + `copy.deepcopy(signature)` pour chaque PNJ ; 3) dans `esprits._percus_depuis` (l. 649), dès que `acteur in changes` (chaque pas du PNJ), `_percus` balaie tous les objets du monde au lieu d'indexer les objets par salle dans `memo`.

5. **Idées classiques de planification / multi-agents non essayées**
   - *Pertinence causale par état (Delete-Relaxation / Backward Reachability)* : le lot 92b a constaté que **74,3 % des expansions** en tiré viennent de préparatifs (`prendre burette/pot/fagots`, `ouvrir besace`), mais s'est arrêté à une clôture globale statique (0,01 % d'élagage). Or, dans un état `e`, préparer de la lumière ou du combustible est causalement stérile pour `faim` dès que toutes les salles noires accessibles ont déjà le fait `("inspecte", salle)` (ou que le PNJ porte déjà une flamme allumée) et qu'aucun contenant verrouillé crochetable n'y reste à ouvrir.
   - *Seuils d'événements (Event-Driven Thresholds)* : ne pas invalider une recherche sans plan par une dérive continue de `faute` tant qu'aucun palier discret de `_droits_gestes` n'est franchi.

---

## 2. Pistes détaillées et classement

| Rang | Piste | Exacte ? | Gain attendu (`auberge` 8–12 h) | Effort | Risque |
|---:|---|:---:|---:|---|---|
| **1** | **A3.** Partager les 12 tables géométriques/routes/pressions de `Vue` et cacher `_entrees_communes` dans `vues_du_choix` (+ réutilisation de `Vue` si esprit/monde inchangés) | **Oui** (`--calcul` identique) | **−12 à −20 s fixe** (−8–12 %)<br>**−15 à −25 s tiré** (−7–11 %) | Faible (~25 l.) | Nul |
| **2** | **A1.** Conserver `sombre`/`lumiere` entre passes 1→2→3 dès le 1er appel, persister `discretion` par `(id, signature_but)` et certifier `_sans_plan` dès le 1er épuisement | **Oui** (mêmes plans, coûts et états) | **−5 à −10 s fixe** (−3–6 %)<br>**−25 à −40 s tiré** (−12–18 %) | Faible (~35 l.) | Très faible |
| **3** | **A2.** Retirer `actives` de `_entrees_communes` et restreindre `"cases"` aux cibles pertinentes de `v.salle_depart` | **Oui** (prouvé par `VERIFIER=1`) | **−5 à −10 s fixe** (−3–6 %)<br>**−15 à −25 s tiré** (−7–12 %) | Faible (~20 l.) | Faible |
| **4** | **A4.** Factoriser `gestes()` par `(salle, portes, faits)` entre `allure=15` et `allure=30` (+ couper les feuilles non furtives `allure=30` à `profondeur - 1` hors plafond) | **Oui** (`--calcul` identique pour `gestes`) | **−5 à −8 s fixe** (−3–5 %)<br>**−20 à −35 s tiré** (−10–15 %) | Moyen (~45 l.) | Faible |
| **5** | **A5.** `percevoir_signes` sous `etat_fige`, suppression du double `percevoir` à la minute, indexation des objets par salle dans `esprits._percus`, clé tuple dans `signes._percus_gardes` | **Oui** (`--calcul` identique) | **−8 à −15 s fixe et tiré** (−5–7 %) | Moyen (~50 l.) | Faible |
| **6** | **B3.** Élagage causal des préparatifs de lumière/combustible dans `gestes()` quand aucune cible noire/serrure non résolue ne reste dans `e` | **Hors plafond oui** ; change les recherches bornées (4 000 nœuds) | **−40 à −70 s tiré** (−20–30 %) | Moyen (~60 l.) | Moyen (modifie `examines` sous borne) |
| **7** | **B1.** Seuil discret de réveil sur le tarif `faute` (ne relancer pour les prix seuls que si un palier de `_droits_gestes` ou de coût d'attente est franchi) | **Non** sur recherches bornées | **−45 à −75 s tiré** (−20–35 %) | Moyen (~50 l.) | Moyen |
| **8** | **B2.** Fusionner `allure=15` et `allure=30` avant le premier geste `furtif` (état unique avec surcoût différé du préfixe marché) | **Non** (ordre A* sous plafond et pression de route) | **−35 à −55 s tiré** (−16–25 %) | Élevé (~120 l.) | Moyen à élevé |

### Protocole de vérification par catégorie
- **Pistes exactes (A1 à A5)** : 1) test unitaire direct d'équivalence sur captures (`auberge` 1985 à 480 et 600 min : mêmes plans, coûts hexadécimaux, monde et scène après recharge) ; 2) `comparer_bancs.py --empreintes` 2 h (4 scénarios × 4 graines) ; 3) `VERIFIER=1` + `spatial.VERIFICATION=1` sur `auberge` 2 h (prouve qu'aucun cache élargi par A1/A2/A3 ne diverge de l'oracle complet sans cache) ; 4) paire CPU 12 h `auberge` 1985 fixe/tiré avec `comparer --calcul` (strictement 0 écart pour A3/A4/A5 ; mêmes plans/chroniques/états et réduction du nombre de nœuds pour A1/A2).
- **Pistes B1–B3** : banc rapide 4 h × 4 graines × 4 scénarios, audit des nuits (vols, sans recours, attentes) et vérification qu'aucun plan trouvé auparavant n'est manqué.

---

## 3. Avis franc : peut-on atteindre ≤ ×1,5 sans changer les décisions des PNJ ?

1. **En départ fixe (×1,65 → ≤ ×1,50) : OUI, facilement.**
   Il ne manque que 17 secondes sur 195 s. Les seules pistes **A3 + A5** (100 % exactes, `comparer --calcul` bit-à-bit identique) suffisent à descendre autour de **×1,40–1,45 (~165–172 s)**.

2. **En départ tiré (×2,64 → ≤ ×1,50) : OUI, mais uniquement en groupant les pistes exactes A1 + A2 + A3 + A4 + A5 dans un même lot.**
   - Pourquoi les lots précédents ont-ils échoué à entamer le tiré ? Parce qu'ils ont optimisé le coût unitaire d'un nœud gardé (lots 81, 86, 105) tout en laissant **A2** invalider `_entrees_communes` à chaque pas d'un tiers et **A1** jeter le graphe et le certificat d'impossibilité au premier appel après chaque invalidation, forçant la régénération complète de `gestes` sur deux passes et deux recherches consécutives.
   - En combinant **A1 + A2 + A3 + A4 + A5** (en tenant compte du recouvrement entre A1, A2 et A4), le gain cumulé réaliste en tiré est de **−38 % à −46 %** (soit **~133 à 153 s** sur 12 h, contre 140 s pour le seuil ×1,50).
   - **Recommandation** : réaliser un lot groupé **A1 + A2 + A3 + A4 + A5** (100 % exact, zéro changement des décisions des PNJ) et mesurer la paire 12 h une seule fois au bout. Si le tiré atterrit entre **×1,50 et ×1,60** (~140–150 s) à cause de la variance du poste, ne plus chercher de micro-gains Python : activer alors **B3** (élagage des préparatifs de lumière/combustible quand toutes les cibles noires accessibles sont déjà inspectées), qui est sémantiquement exact hors plafond et tranche à la source les 74 % d'expansions de préparatifs stériles.
