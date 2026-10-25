# Tâche Codex 68 : « observer » rend les impressions que les signes perçus soutiennent

Branche `codex-impressions-observer` (elle porte ce fichier, issue de l'intégration **d78cfcc**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna (le chemin « observer » est
local, sans appel au modèle).

Lot en même temps sur ce poste : 66 (`planification.py`). Ce lot touche `donjon/signes.py` et, s'il le faut,
`deliberation.autour` ; pas `planification.py`.

Lis `AGENTS.md`, `docs/etat-dev.md` (« Vérification Luna de l'intégration f033364 », **défaut (5)** ; entrées
`codex-relations-3c` (signes et impressions, `observer`), `codex-signes-calibration`, `codex-peur-transmise` lot 53,
`codex-soi-meme` lot 35 (personne ne lit ses propres signes)), `docs/plan-relations.md` (3c), puis `donjon/signes.py`
(`lire`, `percevoir_tous`, impressions, leur appui sur un signe présent), le chemin de la commande `observer`
(`commandes`, `moteur`). Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-f033364\relecture.txt` (banc
`signes-ecart`, « observer Ilse » / « observer Brune », les deux passes ; même chose dans `verif-luna-8443458`).

## Le constat
Banc `signes-ecart` : sur `main` et en 8443458, « observer Ilse » donnait ses signes (« se tient à l'écart de Brune »,
« baisse les yeux », « tremble ») **et** les impressions « semble craindre Brune » / « semble avoir peur ». Sur
l'intégration f033364, dans les deux passes et aux deux observations, Ilse ne donne plus ces impressions ; « observer
Brune » les donne encore. Changement probable avec le lot 53 (impressions appuyées par un signe présent) ou la
calibration des signes ; non établi.

## L'invariant
**Observer quelqu'un rend les impressions que les signes que Corvus perçoit de lui soutiennent maintenant**, par la même
règle pour le joueur et les PNJ (lecture faillible, jet de PSY tiré une fois, mémorisé) ; une impression n'est retirée
que si le signe qui la soutenait n'est plus perçu. Trouve la cause (lot 53, calibration, lecture déjà faite qui n'est
plus rendue…), corrige la règle commune, pas Ilse ni ce banc.

## Vérification (minimale)
- Tests après rechargement : le cas réel (scène `tests/data/scenes/signes_ecart_relais` ou le banc) : « observer Ilse »
  rend ses signes et ses impressions, deux fois de suite sans relancer de dé ; un autre cas de même nature (une
  impression soutenue chez un autre personnage) ; une impression dont le signe a disparu n'est plus rendue.
- Empreintes 2 h, Relais et crue, 4 graines (`tools/comparer_bancs.py --empreintes --reference d78cfcc`) : identiques,
  ou chaque écart expliqué.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (3c), `docs/etat-dev.md` (« Branche
`codex-impressions-observer`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-68-impressions-observer.md`.
