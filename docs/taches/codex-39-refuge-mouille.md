# Tâche Codex 39 : ne pas rester au refuge mouillé quand un lieu sec et chaud est connu

Branche `codex-refuge-mouille` (elle porte ce fichier, issue de l'intégration **63a717c**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant, vérification
minimale, rapport d'une page. Luna inutile.

Un autre lot tourne en même temps sur l'autre poste (38, coût des recherches). **Ne touche ni `planification.py`,
ni `part_estimee.py`, ni `obstacles.py`.** Si la cause est là, arrête-toi au diagnostic (chiffres, fonctions, cas
réel) et propose le correctif dans le rapport.

Lis `AGENTS.md`, `docs/etat-dev.md` (« Vérification d'intégration ffcc295 », défaut (2) ; entrées `verifier-eau`,
`ressources`, `boucles-pnj`, `temps-reel`, `codex-chercher-appeler`), `docs/plan-crue.md` (« L'eau dans tous les
plans », « Un feu hors de l'eau »), puis `donjon/deliberation.py` (`_candidats`, `choisir`, `_plan_abri`,
`attentes`, `retenir_refus`), `donjon/eau.py` (`attendue`, `en_peril`).

## Le constat
Audit 12 h, crue graine 500 (`tools/audit_nuits.py`, bruts dans `artifacts/verif-integ-ffcc295/` du dépôt
principal) : sur ffcc295, Brune, Ilse et Aubin restent 235 minutes au refuge mouillé (1 à 14 cm d'eau), chaleur 73
à 100 sans recours, la faim renoncée entre eux ; sur `main` 42bb9c0, Brune et Ilse gagnent la galerie (poêle du
guet, au sec) vers la minute 300. Rejoue la nuit sur la base (même placement que l'audit), trouve la minute où
chacun renonce à partir et pourquoi : le recours écarté, son coût, ou le refus retenu qui le bloque.

## L'invariant (à confirmer par le diagnostic)
Un PNJ que le froid ou l'eau presse et qui connaît un lieu sec où il pourrait se chauffer ne reste pas indéfiniment
« sans recours » dans l'eau : soit il y va, soit la raison qui l'en empêche est vraie dans l'état (chemin coupé, eau
attendue là-bas, porte crue fermée, méfiance) et le récit la montre. Corrige la règle commune en cause (le choix du
recours, un refus retenu trop longtemps, la lecture de l'eau attendue…), pas la crue 500 ni ces trois personnes.

## Vérification (minimale)
- Tests après rechargement : le cas réel (scène enregistrée de la crue 500 à la minute du renoncement) et un autre
  de même nature (une autre graine ou une scène d'auteur), même laps découpé.
- Banc rapide (`tools/comparer_bancs.py --reference 63a717c`, 4 h, 4 graines, crue et Relais) : aucune usurpation,
  violation, plantage ni boucle nouvelle ; écarts lus en deux lignes. Puis l'audit 12 h de la seule crue 500 (et
  d'une autre graine touchée), branche seule, contre les nuits ffcc295 conservées.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-crue.md` (la règle), `docs/etat-dev.md` (« Branche
`codex-refuge-mouille`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-39-refuge-mouille.md`
(cause, invariant, fonctions, mesures, limites).
