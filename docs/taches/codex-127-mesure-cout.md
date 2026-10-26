# Tâche Codex 127 (outil) : une mesure déterministe du coût des nuits

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`).
Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de
calcul, priorité réduite. **Outil seul** : ce lot ne touche que `tools/` (et ses tests) ; aucun fichier de `donjon/`. Si un
compteur manque dans le jeu, dis-le dans le rapport au lieu de modifier le moteur. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/etat-dev.md` (lots 98, 109, 114, revue Argon et lots 118–119), les rapports
`rapport-codex-98-profil-compare.md`, `rapport-codex-109-recherche-tiree.md`, `rapport-revue-argon-cout.md`, puis
`tools/empreintes_nuits.py` (`--calcul`), `donjon/banc_pnj.py` (`--diagnostic`), `tools/comparer_bancs.py`.

## Pourquoi
Décision de l'utilisateur du 2026-10-26 : avant de toucher aux leviers qui changent le comportement (deux allures, fréquence
des choix), mesurer le coût autrement que par le temps processeur. Sur ce poste partagé, le même code donne ×2,64 à ×3,81
contre `42bb9c0` selon la cohorte : le CPU ne permet pas de juger un gain de 5 à 10 %.

## Ce qu'il faut livrer
Un outil (`tools/mesure_cout.py`, ou une extension documentée d'un outil existant) qui, pour une nuit (scénario, graine,
heures, départ), rend des **compteurs déterministes** : choix de but (appels de `choisir`), recherches lancées / neuves /
reprises, nœuds développés, gestes générés, par heure de jeu et par PNJ × but, plus le temps processeur à titre indicatif.
Mêmes compteurs à chaque exécution du même code, quelle que soit la charge. Comparaison de deux références git sans
toucher au worktree courant (worktrees détachés comme `comparer_bancs`), résultats rangés dans le cache des références.

## Vérification
- Déterminisme : deux exécutions de la même nuit donnent des compteurs identiques ; l'instrumentation ne change ni la
  chronique ni l'état final (empreintes identiques avec et sans).
- Mesure de référence : auberge 1985 12 h fixe et tiré, mine 1985 12 h fixe, `42bb9c0` contre `integration` ; tableau des
  compteurs et rapport compteurs/CPU (montrer quel compteur suit le mieux le CPU mesuré dans les lots 98/109/114).
- Tests de l'outil ; pas de suite complète (aucun code du jeu touché).

## Livraison
Commits signés si une clé est configurée sur ce poste (sinon le dire), branche `codex-mesure-cout` poussée (pas `main`).
Section « Outils de mesure » de `docs/etat-dev.md` et une entrée « Branche `codex-mesure-cout`, non fusionnée ». Rapport
d'une page : `docs/taches/rapport-codex-127-mesure-cout.md`.
