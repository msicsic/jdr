# Lot 119 — perception sans calcul redondant

Branche `codex-perception-exacte`, non fusionnée, base `c3568ae`.
Luna, scénarios et planificateur inchangés. Les calculs sont exécutés à priorité
réduite, avec deux processus au plus ; les archives de mesure restent dans ce
worktree. Aucun changement de `main` ni du dépôt principal hors cache autorisé.

L'invariant visé est une même perception physique ordonnée pour un même état,
sans travail répété ni examen des objets dont la salle exclut la présence.
Quatre leviers, quatre commits signés SSH :

- `d158a45`, `pnj._avancer` : une révision commune après les évolutions de la
  minute remplace la révision individuelle juste avant cette passe commune.
- `9c78827`, `pnj._avancer` : la lecture des signes rejoint l'état figé du geste.
  `signes.percevoir_tous` possédait déjà son propre bloc figé ; le gain visé
  porte sur l'empreinte supplémentaire à l'entrée, pas sur ses lectures internes.
- `7d0d274`, `signes._percus_gardes` : émissions scalaires et positions sont
  figées en tuples ; disparition de `repr` et de la copie profonde de cette clé.
- `5397015`, `esprits._percus` : index par pose dans le mémo physique partagé.
  Seule une salle unique prouvée autorise une exclusion. Portes, objets portés,
  installés ou multisalles restent candidats ; l'ordre d'insertion du monde
  est restauré avant la perception. L'oracle sans mémo garde le parcours complet.

Chaque levier : **8/8 empreintes identiques**, Relais/auberge, 2 h,
graines 1985/7/42/2024, départ tiré, contre `c3568ae`. Contrôle final :
**16/16 identiques**, quatre scénarios, mêmes durée et graines. Chronique,
mesures et état complet contrôlés ; références réutilisées depuis le cache.
Ces temps cachés ne servent pas de mesure CPU.

Oracles : auberge 42, 2 h, `VERIFIER` et `spatial.VERIFICATION=1`, aucun
écart (354,09 s CPU). Captures réelles auberge 1985 à 480 et 600 minutes :
perceptions ordonnées, croyances, monde, description et scène après recharge
identiques entre base et branche. Les huit nuits CPU passent aussi la recharge.
Base/branche, 12 h fixe et tiré : `comparer --calcul`, **2/2 identiques**
(résultats de chaque recherche, chronique, mesures, souvenirs, état).
Les deux répétitions de branche sont également identiques, nœuds compris.

CPU nu, auberge 1985, deux versions lancées ensemble par paire, sans cache
ni profileur. Secondes au processeur ; tranche = cumul 12 h moins cumul 8 h :

| Référence / départ | Nuit référence → branche | Tranche 8–12 h référence → branche |
| --- | ---: | ---: |
| `42bb9c0`, fixe | 127,28 → 201,80 (×1,59) | 100,84 → 125,92 |
| `42bb9c0`, tiré | 112,27 → 347,09 (×3,09) | 84,02 → 298,67 |
| `c3568ae`, fixe | 197,08 → 195,16 (−0,97 %) | 120,42 → 120,05 |
| `c3568ae`, tiré | 330,41 → 327,86 (−0,77 %) | 288,30 → 287,50 |

**Seuil ×1,5 manqué dans les deux départs.** Le gain ponctuel contre la base
reste inférieur à la variation entre les répétitions de branche (−3,29 % fixe,
−5,54 % tiré) sur ce poste partagé : aucun gain robuste de vitesse n'est établi.
La réduction du travail redondant et l'identité des trajectoires sont vérifiées,
pas une accélération générale ni une borne pour toute partie future.
Les objets sans pose unique nécessitent toujours le contrôle complet de visibilité.
Le lot 118 n'est pas incorporé ; les résultats concernent uniquement A5.

Suite complète unique : **2 040 tests, 16 ignorés, aucun échec ni erreur**,
220 fichiers, deux processus réduits, **2 120,42 s**. Elle inclut l'équivalence
des actions mine/Relais avec et sans mémoire, état et affichage rechargés.
Bruts et lanceur : `artifacts/perception-119/` (non versionnés).
