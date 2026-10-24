# Tâche Codex 58 : un refus de la marche sur l'eau est retenu, et la recherche ne le repropose pas

Branche `codex-eau-plan-marche` (elle porte ce fichier, issue de l'intégration **c592d68** : lots 38 à 55 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna.

Lots en même temps : 57 sur ce même poste (`pnj_propositions.py`, refus retenus) ; 56 sur l'autre poste (comptes).
Ce lot touche `donjon/route_admissible.py`, `planification.py` (routes, `_entrees`) et `pnj._marcher` ; pas
`pnj_propositions.py`. Deux lots font des bancs sur ce poste : priorité réduite, au plus 4 processus.

Lis `AGENTS.md`, `docs/etat-dev.md` (**« Vérification d'intégration 5c2ce81 », défaut (1)** ; entrées
`codex-route-admissible` lot 41, `codex-refuge-mouille` lot 39, `boucles-pnj`), `docs/plan-crue.md` (la règle de
traversée, séjour, retour), le rapport `docs/taches/rapport-codex-41-route-admissible.md`, puis
`donjon/route_admissible.py` (`refus`), `donjon/planification.py` (`Vue.route`, `Vue.allers`, `Vue.descente`,
`_entrees`), `donjon/trajet_estime.py` (`parcours`), `donjon/pnj.py` (`_marcher`), `donjon/eau.py`. Bruts de l'audit :
`C:\Users\msics\donjon\artifacts\verif-integ-5c2ce81\` (`extraits.txt`, nuits crue 2024 et 1985).

## Le constat (audit 12 h de l'intégration 5c2ce81)
Crue 2024, minutes 368-383 : Gorm monte une dizaine de fois de la galerie aux vannes ; la marche refuse (« reste dans :
Salle des vannes ; Conduite basse : séjour ou retour menacé par l'eau »), il remonte (« reste dans la lumière »),
et recommence toutes les une à deux minutes, entre s'abriter et entretenir le brasero (49 passages par heure, la
pire rafale de la crue). Crue 1985, 258-264 : même boucle pour Ilse (ronde vers la conduite basse ↔ lumière). Le
message de refus de la marche n'existe sur aucune nuit ffcc295. Le lot 41 a mis une seule fonction pour la recherche
et la marche ; il reste un écart entre ce que la recherche admet et ce que la marche refuse, et **le refus de la marche
n'est pas retenu** : le même plan revient à la minute suivante.

## L'invariant
**Une route que la marche refuse, sur les mêmes croyances, la recherche ne la propose plus** : trouve l'écart restant
(une lecture différente : horizon, durée estimée et durée réelle du passage, eau crue contre eau vue en route, retour
compté d'un côté seulement) et supprime-le ; et quand la marche refuse sur un fait appris en route (l'eau vue plus haut
que crue), ce fait est **retenu dans les croyances** (eau constatée, datée) pour que la délibération suivante ne
reprenne pas le même plan sans fait nouveau. Pas de cas de Gorm, des vannes ni de la crue 2024.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : la scène réelle (crue 2024 vers 368, capture enregistrée) : Gorm ne
  remonte plus dix fois ; un autre cas de même nature (crue 1985, Ilse) ; les captures du lot 39 rejoignent toujours le
  sec ; le détour dangereux (`test_signes_calibration.TrajetsRevelesTests`) toujours refusé.
- Banc rapide (`tools/comparer_bancs.py --reference c592d68`, 4 h, 4 graines, crue et Relais) puis l'audit 12 h des
  crues 2024, 1985 et 500, branche seule : passages par heure (pire), eau, sans recours, « eau longue ».
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, crue 42 et 2024 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-crue.md`, `docs/etat-dev.md` (« Branche
`codex-eau-plan-marche`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-58-eau-plan-marche.md`.
