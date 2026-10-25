# Lot 76 — bissection de l’auberge (2026-10-25)

Branche `codex-bissection-auberge`, moteur **1171fc3**, brief **bf4bf71**.
**Diagnostic seul**, moteur et `main` inchangés, aucun appel à Luna.

**Protocole.** Auberge 1985, fixe, dortoir, **12 h**, priorité réduite ; 22 révisions du
premier parent, bissection et sondages des intervalles en baisse. Bornes :
**144,44 → 511,14 s CPU (×3,54)**. Puis dix contre-mesures appariées sur deux cœurs de
classe 1 (**0x11**, logiques 0 et 4), tests terminés, deux versions simultanées au plus.
Référence 12 h de `main` calculée une fois. Lanceur `tools/mesurer_bissection_auberge.py`,
wrapper d’`empreintes_nuits.nuit`, diagnostics CPU et `--affinite 0x11` pour les contrôles.

**Révisions sondées, secondes CPU (affinité libre)** :
`42bb9c0` 144,44 ; `1f21384` 624,03 ; `3792eb7` 869,09 ; `7526ff4` 913,31 ; `121afb1` 1149,03 ; `f4e95fd` 342,28 ;
`750837a` 277,67 ; `cd7195d` 263,45 ; `bafb9b9` 291,19 ; `60da18c` 291,11 ; `3aba83b` 533,86 ; `d60b80a` 601,08 ;
`5125d06` 732,59 ; `f033364` 325,28 ; `c592d68` 536,70 ; `04bca30` 517,44 ; `95936ac` 515,61 ; `de3e986` 467,36 ;
`4c828a3` 486,38 ; `d78cfcc` 683,64 ; `455b042` 674,45 ; `1171fc3` 511,14.

**Marches.** Q (`42bb9c0` → `1f21384`) : **144,44 → 624,03 s (+332 %)**,
936 162 → 947 538 nœuds ; Q reproduit à **624,05 s** sous affinité fixée.
Autres couples contrôlés ci-dessous ; neuves = hors mémoire du résultat.

| Fusion (avec son prédécesseur mesuré) | CPU avant → après | Nœuds | Neuves / bornées |
|---|---:|---:|---:|
| Calibration `3792eb7` | 624,05 → 944,42 (+51,3 %) | 947 538 → 1 133 384 | 1685 → 2128 / 11 → 83 |
| 45, recours `3aba83b` | 340,98 → 516,45 (+51,5 %) | 755 462 → 1 107 908 | 2058 → 2270 / 47 → 169 |
| 55, constats `c592d68` | 372,88 → 621,92 (+66,8 %) | 760 632 → 1 712 879 | 1896 → 2135 / 106 → 289 |
| 60, rendez-vous `4c828a3` | 540,31 → 565,47 (+4,7 %) | 1 021 057 → 1 289 146 | 2189 → 2298 / 64 → 96 |
| 61, orientation `d78cfcc` | 454,27 → 456,75 (+0,5 %) | 1 289 146 → 1 289 146 | 2298 → 2298 / 96 → 96 |

**Ce qui coûte.**

- **Q, trajets réels** : `chercher`, 100,55 → 584,19 s dans le sondage. Joss/faim :
  **462 089 → 442 922 nœuds**, mais **27,09 → 135,77 s**. Coût apparent par nœud élevé
  avec cases, orientations, allures et tarifs réels ; coûts internes et passes non séparés.
- **Calibration** : Joss/faim, **442 922 → 476 089 nœuds**, **136,72 → 222,44 s**,
  185 → 231 neuves, **7 → 80 bornées**. Bifurcation à 80 min, sans preuve d’un point chaud
  dans `signes`. Correctif intercalé `3235227` non exercé : aucun coup contre une chose.
- **45, propositions faute de mieux** : Joss/faim **427 479 → 675 827 nœuds**,
  **101,81 → 234,91 s**, 47 → 141 bornées ;
  Lucien/garder:etable ajoute 56 000 nœuds et 14 bornées. Plus de nœuds par recherche,
  après le premier échange proposé à 189 min.
- **55, constats partagés** : Tilo/faim **41 759 → 616 647 nœuds**,
  **10,33 → 226,31 s**, 163 → 277 neuves,
  **0 → 118 bornées**. Bifurcation dès une nouvelle à 215 min.
  Nœuds du lot 62 reproduits ; la fenêtre du lot 75 n’attribue pas le coût de 12 h.

Le lot 60 change la nuit (+26 % de nœuds), mais reste sous +30 % CPU au contrôle. Le **lot 61 est un faux saut CPU** : mêmes monde, chronique, trace et nœuds,
**+0,55 %** contrôlé contre +40,6 % apparent. Comparer les CPU uniquement dans un couple.

**Contrats recommandés, deux lots.** (1) Génération/tarification par état fixé : mêmes coûts
complets (pression, route admissible, portes, possessions), plans hors plafond et qualité
`REFERENCE` si l’ancienne recherche plafonne.
(2) Absence certifiée sur le graphe admissible : **un échec borné ne prouve pas l’absence** ;
une reprise pondérée couvre aussi les prix hors `_entrees` (lot 63). Captures des nuits
réellement mesurées, autre scénario, monde/rendu rechargés ; conserver les nouveaux comportements.

**Vérification/limites.** Suite unique : **1 874 tests, 16 ignorés, zéro échec/erreur**,
un processus, 3 836,85 s. Harnais instrumenté/affinité contre témoin : empreintes identiques,
auberge ancienne et mine actuelle. Monde, `regarder`, `scene_percue` identiques après recharge ;
monde/rendu/trace/compteurs des contrôles reproduisent leurs sondages. Un scénario/graine/départ ; hausse compensée possible
entre points non testés, aucune garantie générale de temps. **45 min dépassées** : 32 nuits et
contrôles CPU. Tous les **(PNJ, but)**, états/rendus et conditions : `artifacts/bissection-auberge/`
du worktree (`bilan.json`, `controles.json`, `conditions-controle.json`, bruts par commit,
`tests-complets.json`).
