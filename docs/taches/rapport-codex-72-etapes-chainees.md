# Lot 72 — étapes chaînées (2026-10-25)

Branche `codex-etapes-chainees`, non fusionnée ; base `fbcf0ff`, brief `f5fec82`.
L'intégration n'avait pas avancé au départ. Aucun appel à Luna.

**Contrat.** `_explorer_etats` remplace les listes de préfixes par des maillons
`(parent, ajout)`, empruntant les ajouts du graphe en lecture. Seul le chemin retenu
est reconstruit et gelé. `_MEMOIRE` le garde sans copie ; `chercher` rend une liste
indépendante, contenus imbriqués compris. `_verifier` compare les formes internes,
`_couper` conserve ses frontières. Coûts, états, rangs et ordre restent inchangés.

**Profil.** Captures mine et auberge, graine 1985, même fenêtre 480–505 minutes,
cinq attentes moteur, priorité réduite. `cProfile(process_time)` :

| Part cumulée du profil, base → branche | Mine | Auberge |
|---|---:|---:|
| `_explorer_etats` | 79,1 → 79,3 % | 85,0 → 84,7 % |
| `signes.percevoir_tous` | 0,87 → 0,95 % | 0,60 → 0,54 % |

Petites copies sous la résolution CPU Windows ; complément `perf_counter_ns` :
43 810 / 76 741 ajouts, 229 359 / 327 708 références de préfixe recopiées → zéro ;
176 / 341 copies profondes du plan → zéro. Ajouts : 17,82 → 13,23 ms (mine),
34,93 → 23,15 ms (auberge). Copies profondes : 1,46 / 4,58 ms supprimées ;
reconstruction et gel : 0,22 / 2,02 ms, 30 / 148 chemins. Moins de 0,2 % du temps
écoulé instrumenté, hors restitution publique (incluse dans le temps global).
Le profil ne justifie pas de modifier `signes.py`, laissé inchangé.

**Justesse.** Oracles de la base sur les deux captures 480–485 : mêmes plans,
7 212 / 8 212 retraits du tas, 49 / 25 recherches, diagnostics, monde, journal et
rendu après recharge. Tests : plusieurs ajouts, égalité différée, séjour,
reconstruction unique ou absente, isolation du graphe et mutations profondes des
appelants. 28 tests existants ciblés et trois nouveaux verts avant les mesures.
Empreintes 2 h, quatre scénarios × quatre graines : chronique, mesures et état
complet identiques. Référence calculée une fois et mise en cache ; un processus
pendant les profils pour respecter le plafond de trois calculs.

**Contrôle intégral.** `VERIFIER` + `spatial.VERIFICATION=1`, mine 42 tirée,
2 h : aucun écart, aucune borne signalée, 5 483 nœuds ; 593,02 s CPU,
54,7 Mo.

**Temps 12 h.** Trois versions lancées ensemble, un calcul chacune, priorité
réduite, graine 1985, sans cache de temps. Secondes CPU :

| Nuit | `42bb9c0` | base `fbcf0ff` | branche |
|---|---:|---:|---:|
| Mine tirée | 126,66 | 198,61 | 198,06 |
| Auberge tirée | 109,48 | 628,19 | 622,98 |
| Mine fixe | 323,55 | 159,81 | 157,61 |
| Auberge fixe | 140,03 | 617,97 | 616,47 |
| Total | 699,72 | 1 604,58 | 1 595,12 |

`comparer --calcul` et comparaison stricte : quatre nuits, zéro différence,
y compris chaque résultat logique, les recherches neuves et les nœuds
(950 284 / 1 355 512 / 476 193 / 1 277 770). Gain total **0,59 %**, une passe ;
pics mémoire 89,3 / 170,6 / 77,5 / 202,0 → 89,3 / 170,9 / 78,0 / 202,6 Mo.
L'économie structurelle est acquise, sans accélération importante mesurée.
Le coût total reste ×2,28 contre `42bb9c0`, dont les décisions diffèrent : la
cible générale ×1,3 n'est pas atteinte.

**Suite complète unique** : 1 861 tests, 16 ignorés, aucun échec ni erreur,
186 fichiers, 1 144,39 s, trois processus à priorité réduite.

**Limites.** Le gel couvre les données d'étapes (dictionnaires, listes, tuples,
scalaires), pas des objets arbitraires ou cycliques. Les ajouts du graphe restent
en lecture pendant la recherche. Profil instrumenté et mesure non profilée ne
se confondent pas ; charge concurrente réelle du poste. Aucun changement de `main`
ni fusion.

Traces locales : `artifacts/profil-*.prof`, `profils-resume.json`, `alloc-*.json`,
`empreintes-2h.json`, `12h-*.json`, `comparaison-12h-*.txt`,
`verifier-mine-42.json`, `tests-complets.json`.
