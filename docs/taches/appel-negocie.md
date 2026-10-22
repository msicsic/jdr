# Tâche : l'appel négocié (qui vient à qui)

Branche `appel-negocie`, worktree `.worktrees/appel-negocie`. Lis d'abord `AGENTS.md`,
`docs/etat-dev.md` (« Décisions prises le 2026-10-22 », entrées `voix`, `parole-voix`,
`voix-inconnues`, `voix-suite`, `deliberation-evenements`) et `docs/plan-ouie.md` (« Les voix »,
« Nommer, attendre, héler », « La suite des voix »).

## Aujourd'hui
Héler est un cri (`pnj.heler`, nature `hele`) ; l'appelé qui saisit son nom répond « Ici ! »
(`pnj.repondre`, `voix.repond` : sauf méfiance) et attend d'être rejoint `REJOINT` (5) minutes sur place
(`deliberation.attendre_l_appelant`, esprit `rejoint`), sauf ce qui presse ; le joueur hèle
(`commandes.heler`, `paroles.hele`) et répond (`commandes.repondre`, `pnj.repondre_a`) par la même règle.
Rien ne décide qui se déplace : l'appelant cherche, l'appelé attend, quelle que soit la raison de l'appel.

## Décision de l'utilisateur (2026-10-22)
L'appelé et l'appelant conviennent de qui vient à qui, par un échange de paroles typées, selon qui a
besoin de qui, qui peut bouger (geste en cours, garde, blessure, eau, porte), la distance et l'urgence :
- « J'arrive » : l'appelé vient à l'appelant (il a de quoi répondre au besoin, ou l'appelant ne peut pas
  bouger, ou l'urgence le demande) ; l'appelant l'attend, le temps que la distance demande ;
- « Ici, viens » : l'appelé ne peut ou ne veut pas bouger (sa garde, son geste) ; l'appelant vient ;
- « Qu'est-ce que tu veux ? » : l'appelé ne sait pas pourquoi on l'appelle et n'a pas de raison de
  bouger ; l'appelant dit ce qu'il veut (un contenu typé existant : part, aide, avertissement…) et la
  décision se reprend ;
- le silence : méfiance, ou ne pas vouloir se signaler (le voleur qui guette).
L'attente se règle sur la distance (le temps de venir, plus une marge), pas une constante. Même règle
pour le joueur : il peut répondre ou demander par des paroles typées sans Luna (« j'arrive », « viens »,
« qu'est-ce que tu veux ? »), et les réponses des PNJ lui parviennent par l'ouïe commune.

## À faire
Une règle commune, au même endroit pour PNJ et joueur ; chaque réponse est un contenu de parole typé
que le moteur tranche ; ce qui est convenu entre dans l'esprit des deux (qui attend qui, jusqu'à quand)
et se tient comme une parole donnée (le rompre est visible et pèse comme les autres paroles non tenues).
Pas de cas par personnage ni par scénario.

## Vérifications
- Tests après rechargement (`tests/test_appel_negocie.py`), même laps découpé (le monde ne dépend pas du
  découpage) : un cas de chaque réponse, avec un cas réel tiré d'une nuit de banc (Hugues et Anselme à
  l'auberge, Aubin et Gorm au Relais, Rémy et Gaspard à la mine dans le noir) et un autre de même nature ;
  le joueur qui hèle et reçoit chacune des réponses ; le joueur hélé qui répond « j'arrive » / « viens ».
- Suite complète verte en priorité réduite ; `planification.VERIFIER` et `spatial.VERIFICATION` 0,2 sur
  une nuit de 8 h de chaque scénario.
- Bancs : rapide (4 h, 4 graines, les quatre scénarios), `main` puis la branche, `--processus 4` ;
  appels, réponses par sorte, retrouvailles, attentes vaines, minutes à attendre, sans recours, en attente,
  usurpations et violations (aucune), temps. `tools/comparer_bancs.py` s'il est sur `main`
  (branche Codex `codex-outils`).
- Luna, si la connexion est faite sur cette machine (`python connexion.py connecter`), sur des copies
  seulement, une exécution à la fois : « j'appelle Gorm », puis « j'arrive », « viens ici », « qu'est-ce que
  tu veux ? » ; nombre d'appels au modèle (0 attendu pour les formes typées).
- Docs : `docs/plan-ouie.md` (section « L'appel négocié »), `docs/mecaniques.md` (« Appeler, crier et
  siffler »), `docs/etat-dev.md` (« Branche `appel-negocie`, non fusionnée », compte de tests).

## Livraison
Commits signés comme d'habitude ; pousse la branche `appel-negocie` sur `origin` (pas `main`) ; rapport
dans `docs/taches/rapport-appel-negocie.md` : règle, fonctions, cas vérifiés, mesures, limites.
