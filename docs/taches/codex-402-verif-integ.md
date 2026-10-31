# Tâche Codex 402 : vérification d'intégration (moteur, sans Luna)

Vérification groupée (`AGENTS.md`, « Vérification à l'intégration ») des lots fusionnés depuis la vérification `0bad227`
(lot 274, `main` actuel). Ils couvrent :
- la refonte du MJ : U-M/U-T, A2 ;
- l'échéance négociée E1 à E6, et A5 ;
- S0 et S1a à S1f (mémoire unifiée, porte `donjon/memoire.py`) ;
- 374 (position crue comme hypothèse datée), 376 (messages selon le découpage) ;
- 377 et 393 (double promesse, réservation) ;
- 380, 388, 396 et 399 (comptes, remboursement) ;
- 390, 391, 392, 394, 395 et 401 (rouges de la suite, parité acoustique, plantage du raccord).

La partie Luna est jouée à part par le superviseur : **pas de Luna ici**.

**Aucun changement de code du jeu.** Un défaut trouvé devient un petit lot, décrit avec son cas réel.
**Bruts dans `C:\Users\msics\donjon\artifacts\verif-integ-<commit>\`**, jamais dans le worktree.

**Poste : le PC fixe**, dans ton propre worktree. Note le commit de départ ; le code du jeu doit y rester identique
(`git diff --stat <commit> -- donjon tools` vide), aucun `pull` pendant le lot. D'autres lots calculent sur ce poste :
**un seul processus de calcul à la fois**, priorité réduite, en fond, détaché ; vérifie qu'il vit et que sa sortie
avance, puis termine par `CALCUL EN COURS : <fichier de fin>` (ne surveille pas en boucle). Termine par `LOT TERMINÉ`
(résumé d'une ligne) ou `QUESTION : …`.

Modèle : le lot 274 (`docs/taches/codex-274-verif-integ.md`, `docs/taches/rapport-codex-274-verif-integ.md`). Ses bruts
sont sur ce poste dans `C:\Users\msics\donjon\artifacts\verif-integ-0bad227\` : **références à relire, jamais à rejouer**.

## Campagnes (une fois, en fond)
Compteurs actifs : classes 219 et causes 227 dans leur version actuelle (compare à la 274).
- Audit 12 h, quatre scénarios × graines 1985, 7, 42, 2024, 3, 11, 99, 500.
- `rixe` et `rixe_douce`, 8 h × quatre graines.
- `VERIFIER` + `spatial.VERIFICATION` 0,2, 8 h, graine 42, cinq scénarios.
- `crue_hameau`, 12 h × quatre graines.

## Ce que le rapport doit dire
- Plantages, violations, usurpations, coups, morts, captifs, écarts `VERIFIER`/`VERIFICATION`, recherches bornées.
- Tableau par scénario `0bad227` → nouveau commit, mêmes mesures qu'au lot 274, compteurs 219/227 et S/F/D (lot 183).
- Suivis :
  - appels et passages après le 374 (Aubin crue 42, appels auberge/mine/crue) ;
  - richesse et attente du hameau ;
  - remboursements et dettes (388), mandats (A5), coups ;
  - S1 sans changement de comportement visible.
- Défauts nouveaux, chacun avec un cas réel et l'invariant en cause ; pour une boucle, dire si elle existait déjà dans la
  même nuit sur `0bad227`.

## Livraison
- Branche `codex-verif-integ-4` : seulement `docs/taches/rapport-codex-402-verif-integ.md` (une page) et une entrée
  « Vérification d'intégration <commit> » dans `docs/etat-dev.md`. Poussée vers origin
  (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ; poussée autorisée), jamais `main`.
