# Tâche Codex 66 : quand seuls les prix changent, l'absence de plan déjà prouvée tient

Branche `codex-certificat-prix` (elle porte ce fichier, issue de l'intégration **d78cfcc** : lots 38 à 61 compris),
worktree dans `tmp-worktrees/`. Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop lents »).
Pas de Luna. Les lots 63 (diagnostic, outil), 64 et 65 entrent dans l'intégration pendant ton lot :
`git merge origin/integration` au début si elle a avancé.

Lot en même temps sur ce poste : 68 (`signes.py`). Ce lot touche `planification.py` (`_sans_plan`, `_parcours`,
`_explorer`, la mémoire des recherches) ; pas `signes.py`.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-cout-suite` (certificats d'absence indépendants des prix),
`codex-lampes-suite` (deux graphes `sombre`/`lumiere`), `codex-cout-12h` lot 38 (suites terminales différées,
`SuiteDifferee`), `codex-depart-feutre` lot 51), **le rapport du lot 63** (`origin/codex-faim-sans-plan`,
`docs/taches/rapport-codex-63-faim-sans-plan.md`) et son outil `tools/mesurer_lectures_recherche.py`, puis
`donjon/planification.py` (`_sans_plan`, `_parcours`, `_explorer`, `_GRAPHES`, `_IMPOSSIBLES`, `PREUVE_MAX`, `VERIFIER`).

## Le constat (lot 63, mine 1985 tirée, 12 h)
Après 8 h, Rémy/faim fait **292 recherches neuves épuisées, sans plan, de même résultat** (544 000 nœuds) ; dans
**266 paires successives, seule la valeur `Vue.degat` (prix d'abîmer) change**, et dans 289 le prix de casse lu change ;
`_entrees` est même identique dans 245 paires. Or le certificat d'absence (`_sans_plan`) est conçu pour cela : la
permission de fauter reste une condition, son prix et celui d'abîmer ne créent aucune arête. Il ne conclut pourtant pas :
le lot 63 relève des preuves à issue **« lacune »** à la mine. Dans `_parcours`, une lacune vient d'un nœud absent du
graphe gardé, d'un nœud sans suites (`noeud[3] is None`) ou d'une **suite différée non développée** (`SuiteDifferee`
sans `suites`, introduite par le lot 38) ; le graphe n'est gardé qu'à la deuxième recherche.

## D'abord, mesurer
Pour ces recherches de Rémy (capture `tests/data/cout-12h/mine-1985-480.json.gz`, puis la nuit) : l'issue de `_sans_plan`
à chaque reprise possible (épuisé, lacune et sa cause exacte, borne), et la part des recherches neuves qu'un certificat
réussi aurait évitées. Même chose pour Joss/faim à l'auberge 1985 fixe.

## L'invariant
**Une recherche épuisée sans plan, dont seuls des prix ont changé depuis (pas une permission, pas une arête), ne se refait
pas : le certificat d'absence le prouve.** Ce qui manque au certificat se complète au moment où la recherche épuisée le
connaît : le graphe gardé dès la recherche épuisée, les suites différées développées ou certifiées vides sans effet sur
les décisions de la recherche jouée, ou une preuve dédiée. Prouve que le certificat reste un vrai certificat (couverture
de tous les chemins autorisés jusqu'à la profondeur) ; `VERIFIER` refait la recherche complète pour chaque reprise par
certificat et compare. Mêmes décisions partout : aucun coût, prix, borne, profondeur ni donnée changé.

## Vérification (demandée expressément)
- Tests après rechargement : Rémy (capture) : la seconde recherche, seul le prix d'abîmer changé, est reprise par
  certificat, même résultat ; une permission changée (une faute devenue permise) la fait refaire ; une suite différée
  qui aurait mené au but n'est jamais certifiée vide.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference d78cfcc`), quatre scénarios × 4 graines : identiques.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche **lancés ensemble** (`tools/empreintes_nuits.py jouer --heures
  12 --scenarios mine auberge --graines 42 1985 --processus 2`, tiré et fixe), CPU par nuit et par tranche, nœuds,
  recherches neuves, reprises par certificat ; `comparer --calcul` base contre branche : identiques.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (le certificat complété, sa preuve),
`docs/etat-dev.md` (« Branche `codex-certificat-prix`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-66-certificat-prix.md` (mesure, causes des lacunes, règle, temps, reprises, limites).
