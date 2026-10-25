# Lot 81 — coût par nœud (2026-10-25)

Branche `codex-cout-par-noeud`, **non fusionnée**, base **cf08508**, brief **f7a558a**,
correctif signé **0270367**.
Aucun changement de scénario, modèle, choix, borne ou modèle de trajet ; aucun appel à Luna.

**Invariant.** `Vue` partage ses tables avec ses nœuds et `VERIFIER` : routes selon
salle/allure/clés/portes (équipement entier en métrique), approches selon contacts,
durées par orientation, pressions selon possessions/lieux/lumières, ou gardes/eau
figées par salle. `route`, `cout_route`, `prix_route`, `mesure_aller`, `_mesurer`
conservent additions et effets de portes, composés avec l'état suivant original.
Tables transitoires, graphes privés ; contrat détaillé dans
[`plan-planificateur`](../plan-planificateur.md).

**Profil de la capture auberge 1985 à 480 min, Joss/faim.**
`tools/profiler_cout_noeud.py`, vingt recherches neuves/processus avant les nuits.
CPU sans profileur ; décomposition `cProfile` en horloge haute résolution.

| Version | Nœuds/recherche | CPU total | µs/nœud |
|---|---:|---:|---:|
| `42bb9c0` | 73 | 0,219 s | 149,8 |
| Base | 149 | 1,094 s | 367,0 |
| Branche | 149 | 0,781 s | 262,2 |

Base/branche : même résultat, coût **15,356590909090908**, **−28,6 % CPU**.
Ancien modèle : coût 28,5, autre recherche. Profil, **µs/nœud** base → branche :
`gestes` **465,1 → 461,0**, `_mesurer` **348,7 → 107,5**, `prix_route`
**115,6 → 9,7**, `route` **193,0 → 138,4**, `pression` **53,1 → 0,8** ;
normalisation propre **36,9 → 33,1**, tas **1,8 → 1,9**. Cumuls emboîtés,
non additifs, dans l'horloge du profileur.
Q ajoutait approches, portes, allures et pressions ; le lot 31 gardait déjà les
distances moyennes, mais la composition/tarification restait répétée. Appels
`route` **25 440 → 6 820**, `prix_route` **21 320 → 2 700**, `apres`
**134 700 → 54 140**. Génération et premiers calculs géométriques restent coûteux.

**Nuits de 12 h.** Trois versions démarrées ensemble sur ce poste, un processus
chacune, priorité réduite ; mine/auberge, graine 1985, départs fixe et tiré.

| Nuit | `42bb9c0` CPU | Base CPU | Branche CPU | Gain | Nœuds base = branche |
|---|---:|---:|---:|---:|---:|
| Mine fixe | 345,62 s | 112,33 s | 106,69 s | 5,02 % | 353 096 |
| Auberge fixe | 170,16 s | 497,86 s | 453,42 s | 8,93 % | 1 061 032 |
| Mine tiré | 163,44 s | 220,86 s | 216,22 s | 2,10 % | 476 548 |
| Auberge tiré | 127,17 s | 607,02 s | 567,25 s | 6,55 % | 1 326 957 |

Stricte et `--calcul` : **quatre nuits identiques**, état/chronique/mesures/récit/
souvenirs/repères/résultats/recherches/nœuds. CPU par tranches 0–4 / 4–8 / 8–12 h :

| Nuit | Base | Branche |
|---|---:|---:|
| Mine fixe | 16,59/30,00/65,66 | 16,23/29,00/61,37 |
| Mine tiré | 26,38/64,14/130,23 | 25,83/66,56/123,72 |
| Auberge fixe | 28,39/52,83/416,42 | 26,34/50,22/376,62 |
| Auberge tiré | 18,11/50,94/537,78 | 18,22/46,86/502,06 |

**Validation.** Cinq tests nouveaux : table/direct (portes, clés, obstacle, eau
attendue, allures, approches, lumière), reprise, corruption et clé omise. Captures
mine/auberge vécues par le moteur puis rechargées : mêmes monde, lignes joueur,
`regarder`, `scene_percue`, diagnostics. Empreintes 2 h, quatre scénarios × quatre
graines : **16 nuits identiques**, référence en cache ; deux processus avec le contrôle.
`VERIFIER` + `spatial.VERIFICATION=1`, auberge 42 tiré, 2 h : **sans écart ni
entrée dans `BORNES`**, **413,98 s CPU**, 1 219 nœuds joués. Suite complète unique :
**1 908 tests, 16 ignorés, zéro échec/erreur**, 194 fichiers, trois processus
à priorité réduite, **1 829,4 s écoulées** (`tools/tests.py --processus 3`).

**Limites. Coût ancien par nœud et cible sous ×2 non retrouvés** : auberge fixe
**×2,66**, tiré **×4,46**. Aucun développement supprimé. Pic mémoire
**191,8 → 205,7 Mo** (auberge tiré). Une passe CPU, sans affinité ; autres tests
Python concomitants, petits gains sans portée statistique. Créneau de 45 min dépassé.
Premier contrôle spatial interrompu : recalcul redondant par destination ; son
témoin indépendant du dernier état complet sert désormais ses destinations.
Seul ce contrôle est ajusté après les mesures CPU.
Bruts dans `artifacts/cout-par-noeud/` du worktree de livraison.
