# Tâche Codex 4 : outils de mesure (comparer les bancs, tests en parallèle)

Branche `codex-outils`, worktree dans `tmp-worktrees/`. Ne touche que `tools/`, `tests/` (tests des
outils) et les docs. Lis d'abord `AGENTS.md` et `docs/etat-dev.md` (« Outils de mesure »).

## 1. `tools/comparer_bancs.py`
La spécification est dans `docs/taches/outil-comparer-bancs.md` : la suivre telle quelle. Points
d'attention : réutiliser `donjon/banc_pnj.py` (nuits, mesures, empreintes, `divergence`) et
`tools/audit_nuits.py` (boucles, `analyser`) plutôt que de les recopier ; le mode `--empreintes`
compare chronique, mesures et état final complet nuit par nuit, et dit la première nuit et la
première minute qui divergent ; le temps d'une nuit se mesure aussi au processeur
(`time.process_time` dans chaque processus), pour qu'un chantier de coût de calcul puisse comparer
sur une machine chargée. Le chantier « coût de calcul » (session Claude, branche `cout-calcul`)
s'en servira : livre cette partie d'abord, pousse la branche dès qu'elle est utilisable.

## 2. La suite de tests en parallèle : `tools/tests.py`
La suite (`python -m unittest discover -s tests -q`, ~1280 tests) prend 20 minutes sous charge.
- Lance les fichiers `tests/test_*.py` en N processus (défaut : la moitié des cœurs, `--processus`),
  en priorité réduite (même règle que `banc_pnj.ceder`), les plus longs d'abord (durées gardées
  d'une exécution à l'autre dans un fichier non versionné, par exemple `.cache/durees_tests.json`).
- Sortie : comme unittest (nombre de tests, échecs et erreurs avec leur trace, sautés), code de
  retour non nul si un test échoue ; option pour ne lancer qu'une liste de fichiers ou un motif.
- Les tests qui écrivent des fichiers le font déjà dans des dossiers temporaires : vérifier qu'aucun
  ne se gêne en parallèle (tests du terminal, du web, ports) ; sinon, les regrouper dans un même
  processus, et le dire.
- Mesure : durée de la suite complète en série et en parallèle, sur cette machine.
- Docs : `AGENTS.md` (ligne « Tests sans appel au modèle » : ajouter la commande parallèle),
  `docs/etat-dev.md` (« Outils de mesure », entrée de la branche, compte de tests).

## Vérifications
- `tests/test_comparer_bancs.py` (voir la spécification) et un test du lanceur (un fichier qui
  échoue fait échouer l'ensemble ; le compte des tests est celui d'unittest).
- Essais réels : `main` contre `main` (identique, `--empreintes`) ; `main` contre une branche connue ;
  la suite complète par le lanceur, même compte de tests qu'unittest.

## Rapport
Dans `docs/taches/rapport-codex-4-outils.md` : commandes, mesures, limites.
