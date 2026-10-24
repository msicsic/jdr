# Tâche Codex 49 : un devis de part qui ne peut rien donner ne se développe pas

Branche `codex-devis-vides` (elle porte ce fichier, issue de l'intégration **3aba83b** : lots 38 à 45 compris),
worktree dans `tmp-worktrees/`. Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop lents »).
Pas de Luna.

**Lots en même temps** : 48 sur ce même poste (`planification._explorer_etats`, construction de la `Vue`) ; 46 sur
l'autre poste (`planification.py` : `Vue.pertinent`, `emplois`, les gestes de prise de lumière) ; 47 (`paroles.py`,
`mj.py`). Ce lot touche `donjon/part_estimee.py` et, s'il le faut, l'appel du devis dans `_parts_remises` ; ne touche
ni `_explorer_etats`, ni la `Vue`, ni les gestes de lumière. Deux lots font des bancs sur ce poste : priorité réduite,
au plus 4 processus.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-part-estimee`, `codex-cout-12h` lot 38, `codex-cout-exact`
lot 31), `docs/plan-planificateur.md` (le devis de part estimée, la borne terminale du lot 38, les caches exacts),
le rapport `docs/taches/rapport-codex-16-part-estimee.md`, puis `donjon/part_estimee.py` (`suites`, `_preparer`)
et `donjon/planification.py` (`_parts_remises`, les suites terminales différées, `_entrees`, `VERIFIER`).

## Le diagnostic (mesuré sur l'intégration, graine 1985, 12 h, auberge)
Sur 3 963 devis de part développés en 60 minutes de fin de nuit, **2 845 sont vides** (aucune suite) : environ
21 % du temps du planificateur. Dans une recherche sans plan, tout finit par être dépilé : la borne différée du
lot 38 n'y économise rien. Le devis 15 % du profil à la mine, 27 à 37 % à l'auberge.

## L'invariant
**Un devis dont une condition nécessaire, prouvée, manque ne se développe pas : il rend vide sans explorer.**
Trouve ce qui rend ces devis vides (mesure d'abord, sur la capture `tests/data/cout-12h/auberge-1985-480.json.gz` :
source absente ou éteinte sans flamme atteignable, foyer incompatible, rien à recharger, lieu inaccessible…), et
écris une condition nécessaire de toute suite non vide, calculée sur ce que le devis lit déjà, avant `_preparer`.
Démontre qu'elle est nécessaire (un devis non vide la satisfait toujours) ; ce qu'elle lit entre dans les clés
exactes du devis et dans `_entrees`. Mêmes décisions : aucun coût, prix, borne de nœuds ni donnée changé.

## Vérification (demandée expressément)
- Tests après rechargement : la capture de l'auberge à 480 : devis vides évités, mêmes résultats de recherche ; un
  cas où la condition est remplie (devis non vide, même suite qu'avant) ; un cas de même nature à la mine.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference 3aba83b`), quatre scénarios × 4 graines :
  identiques.
- **Temps sur 12 h** : `42bb9c0`, la base `3aba83b` et la branche **lancés ensemble**
  (`tools/empreintes_nuits.py jouer --heures 12 --scenarios mine auberge --graines 42 1985 --processus 2`), CPU par
  nuit et par tranche de 4 h, nœuds ; `comparer --calcul` base contre branche : identiques.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, auberge et mine 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la condition et sa preuve),
`docs/etat-dev.md` (« Branche `codex-devis-vides`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-49-devis-vides.md` (causes des devis vides, condition, fonctions, temps, limites).
