# Lot 216 — Vérification Luna de l'intégration d85fb54

27 octobre 2026. L'agent du PC fixe n'a pu obtenir aucune réponse de Luna (« Coffre ChatGPT illisible » dans son contexte ;
blocage documenté au commit `03c4287`). **Campagne jouée par l'orchestrateur sur le laptop**, avec la connexion du dépôt
principal, sur des copies seulement : `tools/banc_multi.py --variante ref=cdaf371 --variante integ=d85fb54 --repetitions 2
--paralleles 3 --connexion chatgpt` sur les 34 scripts du lot 165 (références, signes/ambiance/noms, ressources/comptes,
sous-obstacle, force, poser au sol). Le cache de `227c496` étant sur le PC fixe, la référence est `cdaf371` (lot 153), lue du
cache ; les scripts qui y manquaient ont été joués sur `cdaf371` et rangés. Aucun code du jeu changé.

| Indicateur | `cdaf371` (2 passes) | `d85fb54` (2 passes) |
|---|---:|---:|
| Appels par tour MJ | 3,21 | 2,98 |
| Secondes par tour MJ (médiane) | 11,5 (9,3) | 10,5 (9,0) |
| Tours en repli | 2,0 | 0,5 |
| Obstacles narratifs | 31,0 | 19,5 |
| Relances narratives | 18,0 | 16,5 |
| Refus (moteur, contre-revue) | 25,5 | 22,0 |

Par fonction : audit narratif 3,54 → 2,81 s/tour ; interprétation 4,56 → 4,47 s/tour, entrée cachée 0,88 → 2,47 millions de
jetons. Force (deux passes) : traîner 2 appels/tour sans refus ; enfermer 2,5 appels/tour, un refus sur quatre tours ; ligoter
2,75 avec un refus ; geste improvisé encore refusé (3 refus sur 2 tours) ; achever 2,5. Poser au sol 4 appels/tour sans refus de
destination. Comptes 4,75 appels/tour. Sous-obstacle : refus du moteur attendus (trop bas, trop haut, encombré, forme inconnue).

**Limites.** Pas de lecture saisie par saisie des textes (comptes, réclamation, prise au seuil) : les compteurs ne montrent aucune
régression, mais la justesse sémantique n'est pas certifiée. Secondes de la référence mesurées en partie dans d'autres conditions
de charge. Bruts : `C:/Users/msics/donjon/artifacts/verif-luna-d85fb54/` (journal, détail par partie).
