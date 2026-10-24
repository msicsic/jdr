# Tâche Codex 37 : chercher quelqu'un en l'appelant, sans courir en rond

Branche `codex-chercher-appeler` (elle porte ce fichier, issue de l'intégration **da13f9d** : lots 27 à 32
fusionnés), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »).
Pas de Luna nécessaire.

Un autre lot tourne sur l'autre poste (36 : coût du geste `proposer`, dans `planification.py` et
`pnj_propositions.py`). **Ne touche pas `planification.py`** ; si l'invariant l'exige vraiment, change le
minimum dans un commit à part et dis-le.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrée « Vérification d'intégration ffcc295 », défaut 1 ; entrées
`codex-signalements`, `appel-negocie`, lots 30 et 31), `docs/plan-ouie.md` (« Chercher quelqu'un », « L'appel
négocié »), puis `donjon/deliberation.py` (`appels_vains`, la recherche d'une personne), `donjon/pnj.py`
(`appeler`, `heler`, `_inspecter`, `parcours`), `donjon/appel.py`.

## Le constat (audit 12 h de l'intégration ffcc295, contre `main` 42bb9c0)
- Crue, graine 3, minutes 121 à 128 : Brune hèle « Gorm ? » dix fois en courant refuge ↔ conduite ↔ vannes ↔
  palier ↔ galerie, va voir deux bruits, puis crochète la réserve.
- Mine, graine 7, minutes 470 à 474 : Odon appelle « Mathe ? » huit fois et repasse quatre fois par le
  baraquement.
- Appels par nuit : mine 5,3 → 10,5, crue 2,4 → 4,8.
Extraits : `C:\Users\msics\donjon\artifacts\verif-integ-ffcc295\extraits.txt` ; nuits dans `audit-12h\`.
Hypothèse à vérifier, pas à présumer : depuis les trajets estimés (lot 30), traverser une salle coûte quelques
secondes, et une salle parcourue sans réponse n'est plus écartée assez longtemps (`appels_vains`, sa durée, son
lien à la minute) ; ou chaque salle traversée relance un appel.

## L'invariant
Chercher quelqu'un, c'est parcourir les lieux où on le croit, chacun une fois, en l'appelant une fois par lieu ;
un appel sans réponse écarte ce lieu pour la recherche tant que rien de nouveau n'indique qu'il y est (un bruit,
une voix, une nouvelle), quelle que soit la durée du trajet. Une règle commune à toute recherche d'une personne,
joueur compris s'il est cherché, sans constante propre à un scénario.

## Vérification (minimale)
- Tests après rechargement (`tests/test_chercher_appeler.py`), le cas réel (scène de la crue 3 vers 120, ou une
  scène reconstruite) et un autre de même nature (la mine 7, ou un autre chercheur) : nombre d'appels et de
  passages bornés, l'appelé trouvé quand il répond, même laps d'un bloc ou découpé.
- Banc rapide (`tools/comparer_bancs.py`, 4 h, 4 graines, quatre scénarios, contre da13f9d), plus l'audit
  12 h de la crue 3 et de la mine 7 (`tools/audit_nuits.py`) : appels par nuit, passages par heure, écarts
  expliqués ; aucune usurpation ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-ouie.md`, `docs/etat-dev.md` (« Branche
`codex-chercher-appeler`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-37-chercher-appeler.md`.
