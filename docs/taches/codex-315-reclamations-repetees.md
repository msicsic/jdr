# Tâche Codex 315 : une réclamation refusée ne se répète pas sans entrée nouvelle

Défaut révélé par le lot 306 (`codex-a5-agenda-hameau`, non fusionné : agenda d'évacuation de Gorm dans le hameau).
Lis son rapport `docs/taches/rapport-codex-306-a5-agenda-hameau.md` sur sa branche (section « Sève, 2024 »), et ses
bruts sur le PC fixe : `C:\Users\msics\donjon\artifacts\agenda-hameau-306\reprise-309\` (`diagnostic-2024/`,
`diagnostic-2024-choix.json`, `hameau-2024-*`).

## Le constat
Hameau, graine 2024, avec l'agenda du 306 : Sève fait **sept retours sans entrée nouvelle**, en réclamant à Gorm puis à
Brune entre les minutes 83 et 95. La sonde la classe `repetition_sans_entree_nouvelle`, sans preuve 271 ni différence
perceptive 276. Les passages horaires maximaux de la nuit montent à 95.

## L'invariant
**Une réclamation refusée est retenue selon la cause du refus, comme les autres demandes (refus retenus, lot du
2026-10-22 ; obstacle du lot 225). Elle ne se répète qu'après une entrée nouvelle qui lève cette cause, jamais par le
délai ni par le seul aller-retour entre deux interlocuteurs.** Établis d'abord la cause : réclamation hors de la mémoire
des refus, ou cause mal retenue, ou deux recours qui se relancent l'un l'autre. Corrige le contrat commun (`echanges`,
`deliberation`, biens/dettes), sans cas propre à Sève ni au hameau, ni délai.

## Base et reproduction
Base `integration`. Reproduis sur une capture rechargée du 306 (worktree temporaire avec la branche
`origin/codex-a5-agenda-hameau`, ou rechargement direct de ses captures). **Ne modifie pas les données du hameau.**

## Vérification
- La capture de la graine 2024 avant la minute 83 rechargée : la réclamation est faite, puis retenue. Vérifie aussi
  que monde, rendu et scène sont identiques après recharge, et que le résultat est le même avec un laps d'un bloc ou
  découpé.
- Un autre cas de même nature (réclamation au joueur ou dans un autre scénario).
- Empreintes 2 h, Relais, mine, auberge et crue, 4 graines.
- Banc rapide : le hameau avec les données du 306, 4 h × 4 graines, sur un worktree temporaire. Les retours de Sève
  disparaissent, sans hausse des suspects ailleurs. Calcul détaché.
- Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Le lot 314 traite l'achat promis répété : ne le
chevauche pas. Si vos fichiers se recouvrent, dis-le.

## Livraison
- Branche `codex-reclamations-repetees`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-315-reclamations-repetees.md`.
- Entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\reclamations-315\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
