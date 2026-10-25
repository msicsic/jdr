# Lot 71 — le coût fixe d'un choix

Branche `codex-cout-fixe`, non fusionnée ; base **fbcf0ff**, brief **5ea04cf**.
Aucun appel à Luna, aucune modification de `main`.

**Invariant.** La préparation indépendante du but se paie une fois pendant la
sélection en lecture seule d'un même choix. `deliberation.choisir` borne ce partage
à la boucle des candidats. `planification.vue` duplique une préparation paresseuse
sans transmettre les dictionnaires de calcul ni les découvertes d'une recherche.
`_entrees_communes` garde le relevé commun ; les visées, bornes, emplois, lumière
explicite, violence selon le motif et défense restent propres au candidat. Les
lectures, tarifs, plafonds et fonctions d'exploration restent inchangés.

`obstacles.cle_carte` fournit le texte immuable d'une carte comparée à sa copie
témoin ; le contenu et l'ordre des salles/sorties comptent. Les trois clés
géométriques l'utilisent directement dans un tuple, sans sérialiser la carte à
chaque appel. Obstacles et portes crues restent dans la partie dynamique.

**Profil CPU, même fenêtre.** Auberge, graine 1985, départ tiré, 2 h,
`tools/empreintes_nuits.py profil` avant/après : total **35,47 → 35,28 s** ;
constructions de `Vue` **121 → 72**, cumul **0,781 → 0,656 s** ; `_entrees`
**0,219 → 0,109 s**, dont relevé commun après **0,094 s**, 67 appels des deux côtés
(part de `Vue.__init__` : 2,20 → 1,86 % ; entrées : 0,62 → 0,31 %).
Préparation complète après (`vue`) : **0,688 s**. JSON directement appelé par
`obstacles` : **0,141 → 0,109 s**, dont texte de carte **0,016 s**, 188 encodages
pour 1 223 lectures de clé. Le témoin de carte coûte **0,094 s** au total.
Les durées cProfile sont quantifiées et amplifient les petites fonctions : cette
fenêtre ne montre pas de gain global significatif.

**12 h, graine 1985**, trois versions lancées ensemble, un processus chacune,
priorité réduite ; secondes CPU, sans cache de temps :

| Nuit | `42bb9c0` | base `fbcf0ff` | branche | Nœuds base = branche |
|---|---:|---:|---:|---:|
| Mine, tiré | 132,73 | 208,47 | 203,52 | 950 284 |
| Auberge, tiré | 114,56 | 610,42 | 598,77 | 1 355 512 |
| Mine, fixe | 320,81 | 149,33 | 145,55 | 476 193 |
| Auberge, fixe | 124,86 | 605,31 | 593,28 | 1 277 770 |

Gain sur cette passe **1,91 à 2,53 %** contre la base ; pic mémoire au plus **202,0 → 201,4 Mo**
(mine fixe : 77,8 → 81,0 Mo). Les deux comparaisons, `--calcul` et stricte,
trouvent **quatre nuits identiques** : chronique, mesures, récit, souvenirs,
état complet, repères, résultats de chaque appel, recherches et nœuds. `42bb9c0`
est un repère de coût, pas une référence d'identité pour les comportements intégrés.

**Validation.** Six tests nouveaux : captures réelles mine/auberge vécues par le
moteur, recherches et diagnostics identiques, état et rendu après recharge ;
nouveau choix après déplacement ou croyance modifiée ; paramètres privés,
frontière en lecture seule, exceptions ; carte, ordre, sortie et obstacle changés.
Empreintes 2 h, quatre scénarios × quatre graines : **16 nuits identiques** à
`fbcf0ff`, référence relue du cache. `VERIFIER` et `spatial.VERIFICATION=1`, auberge
42 tiré, 2 h : **sans écart**, aucune entrée dans `BORNES`, 260,7 s CPU.
Suite complète unique (`tools/tests.py --processus 3`) : **1 864 tests, 16 ignorés,
aucun échec ni erreur**, 186 fichiers, **1 260,4 s écoulées**, priorité réduite.

**Limites.** Le partage cesse avant toute écriture du choix ; il suppose que les
méthodes candidates restent en lecture seule, frontière contrôlée par `VERIFIER`.
Pas de reprise d'une vue au choix suivant. La carte reste du JSON éditable : sa
comparaison au témoin et le relevé de l'ordre restent linéaires. Les autres clés
spatiales ne sont pas modifiées. Ce lot ne réduit ni l'espace ni les nœuds et ne
résout pas à lui seul le surcoût des longues nuits.

Bruts : `artifacts/cout-fixe/` dans le worktree, non versionnés.
