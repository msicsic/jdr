# Rapport Codex 4 — outils

Branche `codex-outils`, worktree `tmp-worktrees/codex-outils`, base `06602a6`.
Livraison en deux temps, sans fusion ni modification de `main`.

## Comparateur livré en premier

Commandes (Python du dépôt principal depuis le worktree) :

```powershell
C:/Users/msics/donjon/.venv/Scripts/python.exe -m unittest tests.test_comparer_bancs -q
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference main --branche main --empreintes --processus 2 --sortie artifacts/outils/main-main.json
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference main --branche codex-profils --empreintes --processus 2 --sortie artifacts/outils/main-profils-identite.json
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference main --branche codex-profils --heures 4 --processus 2 --sortie artifacts/outils/main-profils.json
```

- Six tests passent : nuits réelles identiques, scènes sauvegardées et rechargées avec changement
  du joueur ou d'une donnée interne, première minute et chronique tronquée, mesure absente,
  plantage jamais déclaré identique, nettoyage réel d'un worktree après erreur.
- Relais, départ tiré, 2 h, graines 1985/7/42/2024 : `main` contre `main` identique pour les trois
  composantes, huit nuits achevées. Moyennes écoulées 3,112 → 3,581 s ; processeur 2,820 → 3,184 s.
  Ces temps illustrent le bruit d'une mesure unique sur une machine partagée ; aucun gain revendiqué.
- `main` contre `codex-profils` : différence dès la minute 0 de la première nuit (1985), chronique,
  mesures et état final différents ; code 1 attendu. Les données de profil diffèrent au départ.
- Mode normal, Relais, 4 h, quatre graines : huit nuits achevées sans violation ni usurpation,
  code 0 ; tableaux, écarts notables, boucles et constats d'audit produits. Moyennes écoulées
  5,915 → 4,853 s ; processeur 5,648 → 4,617 s. Les nuits diffèrent : ce n'est pas une preuve
  d'optimisation. Sortie Windows redirigée vérifiée en UTF-8.

Réutilisation : `banc_pnj.nuit`, `ceder`, `divergence`, empreintes physiques existantes ;
`audit_nuits._releve`, `_final`, `boucles`, `analyser_nuit`. Le moteur n'est pas modifié.
Chaque nuit a un processus neuf : les caches d'une graine précédente ne biaisent pas ses compteurs
ni son coût. Les deux lots sont joués successivement. Les références sont résolues une fois en
commits ; les modifications non committées sont incluses seulement si `--branche` est omise.

Limites :

- L'identité porte sur tout `monde.data`, pas sur les caches Python hors sauvegarde ; les mesures
  incluent les compteurs de recherches. Une optimisation qui change ces compteurs n'est donc pas
  déclarée identique sans justification des écarts.
- La datation utilise la première entrée différente de la chronique et, au rejeu, le dernier état
  complet observé après perception de chaque minute, plus création et fin de nuit. Elle donne la
  première minute **observée**, pas la première instruction Python divergente ; un écart transitoire
  résorbé entre ces points peut échapper à cette datation. Un écart de mesures seul sans trace ni
  état différent est annoncé « minute indéterminée ». L'outil ne prétend pas garantir davantage.
- Le mode normal inclut les relevés d'audit dans ses temps ; le mode identité ne les prend pas.
  Comparer les coûts avec le même mode, les mêmes options et plusieurs passes. `process_time`
  exclut l'attente du processeur, sans éliminer tous les effets de la charge sur le matériel.
- Les violations de vérification et les autres exceptions sont comptées comme nuits en échec,
  avec type, message, minute et trace dans le JSON ; aucune nuit échouée ne vaut zéro mesures.
- Le nettoyage est assuré par `finally` après erreur Python ; un arrêt forcé du processus ou de la
  machine peut laisser un worktree à retirer. Git et Python ≥ 3.11 sont nécessaires.

## Lanceur de tests

Réalisation et mesures à suivre dans le deuxième commit de cette branche.
