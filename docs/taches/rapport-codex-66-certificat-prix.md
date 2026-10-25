# Lot 66 — le certificat d'absence complété quand seuls les prix changent

Branche `codex-certificat-prix`, **non fusionnée** ; brief e7bb089 sur l'intégration d78cfcc, puis
fusion de l'intégration locale afd3602 (lots 64 et 65 ; le lot 63 n'y est pas, son rapport et son
outil ont été lus sur `origin/codex-faim-sans-plan`). Base des mesures : **4708c9d** (cette fusion).
Aucun appel à Luna ; `main` et `integration` inchangées. Un seul poste : tous les calculs en priorité
réduite, au plus trois processus.

**Mesure** (`tools/mesurer_certificat.py`, nuits de 12 h, recherches de faim après la minute 480).

| | Rémy, mine 1985 tirée | Joss, auberge 1985 fixe |
|---|---:|---:|
| Recherches neuves (épuisées / bornées / plans) | 326 (325 / 1 / 0) | 193 (62 / 129 / 2) |
| Nœuds de ces recherches | 802 721 | 680 958 |
| Certificats tentés par le moteur → issue | 29 → 29 lacunes | 7 → 7 lacunes |
| Même preuve sur le graphe de chaque recherche épuisée | 325 lacunes | 62 lacunes |
| Cause de la (première) lacune | nœud non développé : 325 | nœud non développé : 62 |
| Graphe complété à part (oracle) | 325 prouvées | 29 prouvées, 33 hors de l'oracle (*) |
| Signatures d'absence distinctes | 43 | 13 |
| Recherches dont la signature était déjà prouvable | 282 (694 747 nœuds) | ≥ 49 (126 175 nœuds) |

Un **nœud non développé** est un état que la recherche pondérée a examiné à la profondeur limite et
que le parcours en largeur atteint plus tôt par un chemin plus cher : la seule cause observée. Les
suites différées n'en sont pas une dans ces nuits (une recherche épuisée développe toutes celles
qu'elle pousse) ; une suite terminale estimée en serait une (son état n'est jamais un nœud). (*) La
recherche avait découvert la lumière : l'oracle ne sait pas y revenir, le moteur si.

**Règle livrée.** Une recherche épuisée sans plan, dont seuls des prix ont changé depuis, ne se
refait pas : le certificat le prouve. `chercher` garde sa règle (graphe gardé à la deuxième
recherche sur les mêmes entrées, certificat tenté sur lui) ; épuisée, la recherche **complète** le
certificat : `_sans_plan(..., completer=True)` et `_parcours(..., completer=…)` développent à part,
dans le mode de chaque graphe (sombre puis lumière, ordinaire puis feutré, comme les passes de
`_explorer`), les états absents ou non développés et le détail des suites différées ; une suite
terminale estimée y compte comme le but. Rien n'est écrit dans le graphe gardé. Preuve de
couverture dans `docs/plan-planificateur.md` (« Certificat complété… ») ; bornée, la recherche ne
complète rien. Après : Rémy **73** recherches neuves (72 épuisées, 177 045 nœuds), **258 reprises
par certificat**, 29 certificats complétés tous prouvés ; Joss 152 neuves (2 / 129 / 21), 41 reprises,
7 certificats prouvés.

**Temps sur 12 h** (`tools/empreintes_nuits.py`, 42bb9c0, base et branche lancés ensemble, un
processus chacun, seulement mine et auberge 1985, tiré et fixe : contrainte de charge du poste).

| Nuit | 42bb9c0 | base | branche | base → branche | neuves | nœuds | reprises cert. | pic Mo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mine tiré | 110,8 s | 177,5 s | 171,9 s | ×1,03 | 1 200 → 929 | 950 k → 298 k | 249 → 525 | 90 → 88 |
| auberge tiré | 95,6 s | 748,6 s | 740,9 s | ×1,01 | 2 179 → 1 926 | 1 356 k → 1 110 k | 326 → 714 | 171 → 173 |
| mine fixe | 336,0 s | 263,5 s | 260,5 s | ×1,01 | 1 333 → 1 111 | 476 k → 333 k | 246 → 470 | 79 → 75 |
| auberge fixe | 167,6 s | 834,4 s | 816,8 s | ×1,02 | 2 063 → 1 976 | 1 278 k → 1 109 k | 9 → 105 | 204 → 200 |

Les huit premières heures sont égales ; l'écart vient de la dernière tranche. Le gain de temps est faible : les recherches évitées
étaient surtout des graphes repris, déjà peu chers (reprises de graphe mine tirée 297 → 29). Deux
variantes, plus rapides à la mine tirée (×1,20 et ×1,18), ont été écartées : compléter dès la
première recherche épuisée ralentissait les trois autres nuits (×0,91 à ×0,96, +9 à +52 Mo) ;
garder le graphe de toute première recherche épuisée aussi (×0,92 à ×0,96, +40 à +85 Mo ;
ramasse-miettes de l'auberge tirée 36 → 95 s contre 3,3 s de complétion). Hors lot : sur
l'auberge, **l'intégration est 5 à 8 fois plus lente que `main` 42bb9c0** (96 et 168 s contre 749 et
834 s), à examiner.

**Identité.** `empreintes_nuits comparer --calcul` base contre branche : 4 nuits de 12 h identiques
à chacune des trois mesures, 16 nuits de 2 h (quatre scénarios × 1985, 7, 42, 2024) identiques
(chronique, mesures hors comptes de recherche, récit, souvenirs, état complet, empreintes du banc,
résultat de chaque recherche). `comparer_bancs --empreintes --reference 4708c9d` s'arrête sur
« mesures » à la mine 1985 : la mesure `recherches_neuves` y baisse, par construction. `VERIFIER` +
`spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart (aucune reprise par certificat
dans ces deux heures) ; depuis la capture de la mine (8 h, 1985), 60 minutes : 907 recherches, **116 reprises par
certificat refaites et comparées**, 15 certificats complétés tous prouvés, aucun écart ni borne (la
même épreuve depuis la capture de l'auberge, sans reprise attendue, arrêtée après 1 h 40 de calcul).

**Tests** (`tests/test_certificat_prix.py`, captures rechargées) : Rémy et Odon (mine) : la faim qui
monte change les prix, pas les permissions ; la deuxième recherche complète le certificat, la
troisième est reprise par lui, `VERIFIER` refait chacune ; une faute devenue permise (honnêteté
40) fait refaire la recherche ; cinq minutes de la capture, avec ou sans certificat : même monde,
même rendu et même scène après rechargement. Synthèse : une suite différée qui mène au but n'est
jamais certifiée vide, trou et suite vide prouvés, lumière lue en complétant, discrétion découverte.
Suite complète (`tools/tests.py --processus 2`, le troisième processus pris par `VERIFIER`) :
**1 857 tests, 16 sautés, 2 échecs** (`test_parole_commune` : champ `observe` des souvenirs
`vu_agir`), les mêmes sur la base 4708c9d, absents de l'intégration 1171fc3 ; essai de fusion dans
1171fc3 (lots 67 à 72, sans conflit) : `test_certificat_prix`, `test_cout_suite`,
`test_borne_rester`, `test_depart_feutre`, `test_cout_12h`, `test_parole_commune` verts (59 tests).

**Limites.** La preuve vient à la deuxième recherche sur des entrées : la première et la deuxième
se font toujours ; une seule dernière preuve par PNJ et but (deux signatures qui alternent se
refont) ; une recherche bornée n'est pas complétée (129 des 152 recherches neuves de Joss) ; le
certificat coûte un parcours qui développe ce que la recherche pondérée n'a pas développé (au
plus 3 292 états examinés dans ces nuits, plafond `PREUVE_MAX` inchangé). Bruts non versionnés :
`artifacts/certificat/`.
