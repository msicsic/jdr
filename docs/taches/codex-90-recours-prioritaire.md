# Tâche Codex 90 : un plan inférieur ne défait pas aussitôt le recours prioritaire qui vient d'aboutir

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste** : priorité réduite, au plus 3 processus. Ce lot touche `donjon/deliberation.py` et
`donjon/planification.py` : **il ne démarre qu'après la fusion du lot 87** (mêmes fichiers) ; `git merge origin/integration`
au début. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `boucles-pnj` (l'hystérésis entre recours d'un **même** besoin, `_plan_lumiere`,
`_plan_abri`), `besoins` (effet de seuil, inertie), `deliberation-evenements`), **le diagnostic du lot 88** (branche
`origin/codex-avis-reels`, `docs/taches/rapport-codex-88-boucle.md`), puis `donjon/deliberation.py` (`choisir`, `_candidats`,
`_plan_lumiere`, `_plan_abri`, l'inertie), `donjon/planification.py` (`eclairer(tenir=True)`, `_pulsion`), `donjon/pnj.py`
(`_avancer`). Capture et script de reprise : `C:\Users\msics\.paseo\worktrees\3vhx9bfb\codex-avis-reels\artifacts\88\suite-boucle\`
(capture stable de la crue 2024 à 645 min, état SHA-256 `a2279ca9…`).

## Le constat (diagnostic du lot 88, établi)
Crue 2024, à partir de 649 min, Aubin fait **237 passages en une heure** (292 sur 60 min glissantes) en alternant **lumière ↔
inspection** : sa sécurité presse (99,97) dans le noir, le recours de lumière l'envoie à la galerie éclairée ; arrivé, `eclairer
(tenir=True)` n'a exporté que l'« aller » et s'achève, `_plan_lumiere` ne propose plus rien là où il voit clair, `_plan_abri` ne
donne pas de relais stable (seule Ilse est fiable, salle inconnue) ; `_candidats` retrouve alors l'inspection (ronde, pulsion
non satisfaite), dont le trajet repasse par le noir ; au palier, la sécurité encore urgente rétablit la lumière, et ainsi de suite,
plusieurs fois par minute (`pnj._avancer` rechoisit à la fin de chaque plan et à chaque éveil). L'inertie de `choisir` ne protège
que les recours d'un même besoin. **Le défaut est latent dans la base** : depuis la capture à 645, 128 passages en 30 min avec le
code de c9245dd comme avec la branche, monde et rendu identiques d'un bloc ou découpé.

## L'invariant
**Un plan d'un besoin inférieur ne défait pas aussitôt l'état qu'un recours prioritaire vient d'atteindre, sauf s'il porte les
moyens de le maintenir** (ici : aller inspecter en emportant de quoi voir, ou attendre que la sécurité soit apaisée) : le recours
de lumière qui s'achève dans un lieu éclairé laisse le PNJ s'y tenir tant que le besoin qui l'y a mené presse (comme un but qui se
tient en restant), et un plan qui quitterait ce lieu pour le noir compte ce que ce départ rouvre (le coût du noir de la pression, déjà
dans la recherche) et n'est retenu que s'il l'emporte vraiment ; l'hystérésis s'applique entre besoins différents dès qu'un plan en
défait un autre. Corrige la règle commune (choix, état terminal du recours, progression), pas Aubin, la galerie ni la ronde ; pas de
délai fixe. Ce que lit la règle entre dans `_entrees` si la recherche le lit ; `VERIFIER` sans écart.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : la capture réelle à 645 (Aubin ne fait plus la navette ; passages bornés sur 30 min,
  il inspecte une fois apaisé ou en emportant une lumière) ; un autre cas de même nature (un gardien dans le noir avec une ronde, à
  la mine) ; un recours de lumière ordinaire inchangé.
- Banc rapide (`tools/comparer_bancs.py --reference <base> --processus 3`, 4 h, 4 graines, quatre scénarios) : bascules, passages
  par heure (pire), aucune usurpation ni boucle nouvelle ; puis l'audit 12 h de la crue 2024 (avec la branche `codex-avis-reels`
  fusionnée localement dans ton worktree, pour retrouver la nuit qui bouclait) et de la crue 500.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche `codex-recours-prioritaire`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-90-recours-prioritaire.md`.
